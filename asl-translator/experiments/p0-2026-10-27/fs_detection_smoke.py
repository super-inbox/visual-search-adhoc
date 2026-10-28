"""Task 3 C: FS-Detection (chevalierNoir/FS-Detection, CVPR 2021) technical setup check on CPU. Not a port.

Stages, each recorded with its exact error if it fails:
  A  as-is construction on CPU: convnet.ConvNet(char_list, rd_iou_thr, num_concat) with upstream defaults
     (ctc_type='warp', RPN device=cuda); expected to fail on this machine
  B  construction with minimal shims (no weight change): ctc_type='builtin' (upstream's own option; CTC is a training
     loss, unused at inference) and RPN device=cpu. VGG19 ImageNet init download is skipped because the checkpoint
     overwrites those weights
  C  torch.load(best-dev.pth, map_location=cpu) + strict load_state_dict
  D  stage-1 forward (evaluate.py eval_pred path, training=False) on real clips, preprocessing reimplemented in memory
     from upstream preproc/process.py + roiloader.py: ffmpeg fps=29.97 + scale/pad 640x360; Farneback magnitude flow at
     0.5 scale resized back; center crop 360x360; x image_scale 0.3; ImageNet normalize (RGB only). Deviation: the flow
     is not round-tripped through an H.264 file. Output = top-k (start, end, score) proposals in 29.97-fps frames.
Proposals are unvalidated technical output: no labels, fs_present unknown, no detection-accuracy claim.

usage: python -I fs_detection_smoke.py --src FS-Detection/src --ckpt-dir fswild-plus/pwd --clips R02=path,R05=path
       --spans R02=1.4583,R05=0.7917 --out results/fs_detection_feasibility.json
"""
import argparse, hashlib, json, os, platform, subprocess, sys, tempfile, time, traceback
import numpy as np


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stage(rec, name, fn):
    t0 = time.time()
    try:
        out = fn()
        rec[name] = {"status": "PASS", "seconds": round(time.time() - t0, 2), **(out or {})}
        return True
    except BaseException as e:  # noqa: BLE001 - every failure is the deliverable
        rec[name] = {"status": "FAIL", "seconds": round(time.time() - t0, 2), "error_type": type(e).__name__,
                     "error": str(e)[:500], "traceback_tail": traceback.format_exc().strip().splitlines()[-6:]}
        return False


def load_clip(path):
    import cv2
    tmp = tempfile.mkdtemp()
    res = os.path.join(tmp, "r.mp4")
    vf = ("fps=29.97,scale=iw*min(640/iw\\,360/ih):ih*min(640/iw\\,360/ih),"
          "pad=640:360:(640-iw*min(640/iw\\,360/ih))/2:(360-ih*min(640/iw\\,360/ih))/2,setsar=1:1")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", vf, "-c:v", "libx264", "-crf", "20", res], check=True)
    cap = cv2.VideoCapture(res); rgb, opt, prv = [], [], None
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        H, W = fr.shape[:2]
        g = cv2.cvtColor(cv2.resize(fr, (W // 2, H // 2)), cv2.COLOR_BGR2GRAY)
        if prv is None:
            mag = np.zeros((H, W), np.uint8)
        else:
            fl = cv2.calcOpticalFlowFarneback(prv, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            m, _ = cv2.cartToPolar(fl[..., 0], fl[..., 1])
            mag = cv2.resize((255.0 * (m - m.min()) / max(float(m.max() - m.min()), 1)).astype(np.uint8), (W, H))
        prv = g

        def crop_scale(x):
            x = x[:, W // 2 - H // 2: W // 2 + H // 2]
            return cv2.resize(x, (int(x.shape[1] * 0.3), int(x.shape[0] * 0.3)))
        rgb.append(crop_scale(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))); opt.append(crop_scale(mag))
    cap.release(); os.remove(res); os.rmdir(tmp)
    return np.stack(rgb).astype(np.float32), np.stack(opt).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--ckpt-dir", required=True)
    ap.add_argument("--clips", required=True); ap.add_argument("--spans", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--top-k", type=int, default=5)
    a = ap.parse_args()
    sys.path.insert(0, os.path.abspath(a.src))
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import torch, yaml
    torch.set_num_threads(4)
    conf = yaml.safe_load(open(os.path.join(a.ckpt_dir, "train_conf.yaml")))
    ckpt = os.path.join(a.ckpt_dir, "best-dev.pth")
    upstream = subprocess.check_output(["git", "-C", a.src, "rev-parse", "HEAD"], text=True).strip()
    rec = {"repo": "https://github.com/chevalierNoir/FS-Detection", "upstream_commit": upstream,
           "checkpoint": {"source": "README 'Pretrained models' Google Drive 1zl1Pq54E55mrYQHE4qwZzVz-mBr3U0w5 "
                                    "(fswild-plus.zip: pwd/best-dev.pth, pwd/train_conf.yaml), ChicagoFSWild+ detector, "
                                    "README AP@0.5 0.448",
                          "best_dev_pth_sha256": sha256(ckpt), "train_conf": conf},
           "environment": {"python": platform.python_version(), "machine": platform.machine(), "torch": torch.__version__,
                           "cuda_available": torch.cuda.is_available()},
           "is_fs_detector": True, "labels_supplied": False, "fs_present": "unknown", "stages": {}}
    S = rec["stages"]
    import convnet, rpn

    def as_is():
        convnet.ConvNet(char_list=conf["char_list"], rd_iou_thr=conf["reward_iou_thr"], num_concat=conf["stage"])
    stage(S, "A_as_is_cpu_construction", as_is)

    model = {}

    def shimmed():
        init = rpn.RPN.__init__
        def cpu_init(self, *args, **kw):
            kw["device"] = torch.device("cpu"); init(self, *args, **kw)
        rpn.RPN.__init__ = cpu_init
        model["m"] = convnet.ConvNet(char_list=conf["char_list"], ctc_type="builtin", rd_iou_thr=conf["reward_iou_thr"],
                                     num_concat=conf["stage"]).eval()
        return {"shims": ["ctc_type='builtin' (upstream option; CTC unused at inference)", "RPN device=cpu",
                          "VGG19 ImageNet init skipped (overwritten by checkpoint)"]}
    stage(S, "B_shimmed_cpu_construction", shimmed)

    def load():
        sd = torch.load(ckpt, map_location="cpu")
        r = model["m"].load_state_dict(sd, strict=True)
        return {"n_tensors": len(sd), "missing": list(r.missing_keys), "unexpected": list(r.unexpected_keys)}
    if "m" in model:
        stage(S, "C_checkpoint_load_strict", load)

    spans = {k: float(v) for k, v in (x.split("=") for x in a.spans.split(","))}
    runs = []
    for item in a.clips.split(","):
        rid, path = item.split("=", 1)
        run = {"review_id": rid, "input_sha256": sha256(path), "source_span_start_s": spans[rid]}

        def fwd():
            rgb, opt = load_clip(path)
            mean = torch.tensor(conf["immean"]).view(1, -1, 1, 1); std = torch.tensor(conf["imstd"]).view(1, -1, 1, 1)
            img = ((torch.from_numpy(rgb).permute(0, 3, 1, 2) / 255.0) - mean) / std
            L = img.shape[0]
            sample = {"img_global": img[None], "img_local": img[None], "opt_global": torch.from_numpy(opt)[None],
                      "opt_local": torch.from_numpy(opt)[None], "det_label": torch.zeros(1, 30, 3, dtype=torch.int32),
                      "fs_label": [[]], "fs_mask": -torch.ones(1, 30)}
            t0 = time.time()
            with torch.no_grad():
                prob, pred = model["m"](sample, training=False, fsr_on=False, pose_on=False, stage=1)
            prob, pred = prob[:, :, 0].numpy(), np.floor(pred.numpy())
            mask = (pred[:, :, 0] <= pred[:, :, 1]) & (pred[:, :, 0] >= 0) & (pred[:, :, 1] < L)
            p, c = prob[0][mask[0]], pred[0][mask[0]]
            idx = np.argsort(p)[-a.top_k:][::-1]
            fps = 29.97
            props = [{"start_frame_29p97": int(c[i, 0]), "end_frame_29p97": int(c[i, 1]),
                      "clip_start_s": round(c[i, 0] / fps, 3), "clip_end_s": round((c[i, 1] + 1) / fps, 3),
                      "source_start_s": round(spans[rid] + c[i, 0] / fps, 3),
                      "source_end_s": round(spans[rid] + (c[i, 1] + 1) / fps, 3),
                      "score_uncalibrated": round(float(p[i]), 4), "interval_source": "detector",
                      "status": "unverified_proposal", "fs_present": "unknown", "letters": None,
                      "character_timestamps": None} for i in idx]
            return {"frames_29p97": L, "input_hw": list(img.shape[-2:]), "forward_seconds": round(time.time() - t0, 2),
                    "n_valid_proposals": int(mask.sum()), "top_proposals": props}
        if "m" in model and S.get("C_checkpoint_load_strict", {}).get("status") == "PASS":
            stage(run, "D_forward", fwd)
        runs.append(run)
    rec["runs"] = runs
    import re
    txt = re.sub(r"/(private/)?(var|tmp)/[^\s\"']*?/scratchpad", "<scratch>", json.dumps(rec, indent=1))
    open(a.out, "w").write(txt.replace(os.path.expanduser("~"), "~"))
    print(json.dumps({k: v["status"] for k, v in S.items()}), [(r["review_id"], r.get("D_forward", {}).get("status")) for r in runs])


if __name__ == "__main__":
    main()
