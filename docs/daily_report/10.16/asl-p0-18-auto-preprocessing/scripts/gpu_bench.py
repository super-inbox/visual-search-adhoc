"""P0-18 GPU extractor throughput benchmark (How2Sign TEST frames only; dev tooling, not part of the pipeline).

The RTMPose stack is unchanged in every config: same two ONNX models, rtmlib's own YOLOX / RTMPose preprocess and
postprocess, same output (keypoints (P,133,2) float64 pixels, scores (P,133) float32 per frame). What varies:
  workers     threads calling the per-frame pipeline concurrently on one GPU
  det         ORT SessionOptions.use_deterministic_compute
  algo        CUDA EP cudnn_conv_algo_search (EXHAUSTIVE | HEURISTIC | DEFAULT)
  batch       0 = rtmlib per-crop pose inference (reference); B > 0 = detection per frame as before, then the pose crops
              of a chunk of frames go through RTMPose.preprocess -> ONE session.run per B crops -> RTMPose.postprocess
  procs       independent processes (each its own sessions) running the same frames concurrently (video-level
              parallelism; throughput = procs * frames / wall)
Each config runs in its own subprocess: GPU utilisation and memory are sampled every 0.25 s, ORT "Fallback mode"
warnings are counted, the inference is run twice (determinism) and its outputs are compared with the reference config.

Usage: python -I gpu_bench.py VIDEO.mp4 OUT_DIR [--frames 150]          (driver)
       python -I gpu_bench.py --worker CFG_JSON                         (internal)
"""
import argparse, hashlib, json, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def worker(cfg):
    import cv2
    import numpy as np
    import onnxruntime as ort
    import pose_extract as PE
    cap = cv2.VideoCapture(cfg["video"]); frames = []
    while len(frames) < cfg["frames"]:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    wb = PE.make_wholebody("cuda")
    for kind, tool in (("det", wb.det_model), ("pose", wb.pose_model)):
        so = ort.SessionOptions(); so.use_deterministic_compute = cfg["det"]
        tool.session = ort.InferenceSession(PE.model_path(kind), sess_options=so, providers=[
            ("CUDAExecutionProvider", {"device_id": 0, "cudnn_conv_algo_search": cfg["algo"]})])
        assert tool.session.get_providers()[0] == "CUDAExecutionProvider"
    pm, dm = wb.pose_model, wb.det_model
    pin, pout = pm.session.get_inputs()[0].name, [o.name for o in pm.session.get_outputs()]

    def batched(chunk):
        with ThreadPoolExecutor(max_workers=cfg["workers"]) as ex:
            boxes = list(ex.map(lambda f: dm(np.uint8(f)), chunk))
        crops, meta = [], []
        for fi, (f, bb) in enumerate(zip(chunk, boxes)):
            img = np.uint8(f)
            if len(bb) == 0:                                   # rtmlib RTMPose.__call__: no box -> whole image
                bb = [[0, 0, img.shape[1], img.shape[0]]]
            for b in bb:
                x, c, s = pm.preprocess(img, b)
                crops.append(np.ascontiguousarray(x.transpose(2, 0, 1), dtype=np.float32)); meta.append((fi, c, s))
        outs = []
        for i in range(0, len(crops), cfg["batch"]):
            o = pm.session.run(pout, {pin: np.stack(crops[i:i + cfg["batch"]])})
            outs += [[o[0][j:j + 1], o[1][j:j + 1]] for j in range(len(o[0]))]
        per = [([], []) for _ in chunk]
        for (fi, c, s), o in zip(meta, outs):
            k, sc = pm.postprocess(o, c, s); per[fi][0].append(k); per[fi][1].append(sc)
        return [(np.concatenate(k, 0), np.concatenate(s, 0)) for k, s in per]

    def run():
        if cfg["batch"]:
            res = []
            for i in range(0, len(frames), 64):
                res += batched(frames[i:i + 64])
            return res
        if cfg["workers"] == 1:
            return [wb(np.uint8(f)) for f in frames]
        with ThreadPoolExecutor(max_workers=cfg["workers"]) as ex:
            return list(ex.map(lambda f: wb(np.uint8(f)), frames))

    wb(np.uint8(frames[0]))                                    # warm-up: lazy init / cuDNN algo search
    out = {}
    for r in (1, 2):
        c0, t = os.times(), time.time(); res = run(); dt = time.time() - t; c1 = os.times()
        h = hashlib.sha256()
        for k, s in res:
            h.update(np.asarray(k, np.float64).tobytes()); h.update(np.asarray(s, np.float32).tobytes())
        out[f"run{r}"] = {"seconds": round(dt, 2), "fps": round(len(frames) / dt, 2), "sha": h.hexdigest()[:16],
                          "cpu_pct": round(100 * ((c1.user - c0.user) + (c1.system - c0.system)) / dt)}
        if r == 1:
            np.savez(cfg["npz"], n=np.array([len(k) for k, _ in res]),
                     K=np.concatenate([np.asarray(k, np.float64).reshape(-1, 133, 2) for k, _ in res]),
                     S=np.concatenate([np.asarray(s, np.float32).reshape(-1, 133) for _, s in res]))
    json.dump(out, open(cfg["result"], "w"))


def driver(video, out_dir, n):
    import numpy as np
    os.makedirs(out_dir, exist_ok=True)
    base = {"video": video, "frames": n}
    C = []
    for w in (1, 2, 4, 8, 16):
        C.append(dict(base, name=f"ref-settings det=on DEFAULT w{w}", det=True, algo="DEFAULT", workers=w, batch=0, procs=1))
    for det in (True, False):
        for algo in ("EXHAUSTIVE", "HEURISTIC", "DEFAULT"):
            C.append(dict(base, name=f"det={'on' if det else 'off'} {algo} w4", det=det, algo=algo, workers=4, batch=0,
                          procs=1))
    for det in (True, False):
        for algo in ("EXHAUSTIVE", "HEURISTIC"):
            for w in (1, 8):
                C.append(dict(base, name=f"det={'on' if det else 'off'} {algo} w{w}", det=det, algo=algo, workers=w,
                              batch=0, procs=1))
    for det in (True, False):
        for b in (16, 64):
            C.append(dict(base, name=f"det={'on' if det else 'off'} EXHAUSTIVE batched B{b} w4", det=det,
                          algo="EXHAUSTIVE", workers=4, batch=b, procs=1))
    for det in (True, False):
        for p in (2, 4):
            C.append(dict(base, name=f"det={'on' if det else 'off'} EXHAUSTIVE w4 x{p} procs", det=det,
                          algo="EXHAUSTIVE", workers=4, batch=0, procs=p))
    report, ref = [], None
    for i, cfg in enumerate(C):
        samples, stop = [], threading.Event()

        def sample():
            while not stop.is_set():
                v = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
                                   capture_output=True, text=True).stdout.strip().split(",")
                if len(v) == 2:
                    samples.append((int(v[0]), int(v[1])))
                time.sleep(0.25)
        th = threading.Thread(target=sample, daemon=True); th.start()
        procs, t = [], time.time()
        for p in range(cfg["procs"]):
            wc = dict(cfg, npz=os.path.join(out_dir, f"c{i}_p{p}.npz"), result=os.path.join(out_dir, f"c{i}_p{p}.json"))
            json.dump(wc, open(wc["result"] + ".cfg", "w"))
            procs.append(subprocess.Popen([sys.executable, "-I", __file__, "--worker", wc["result"] + ".cfg"],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True))
        errs = [p.communicate()[1] for p in procs]; wall_total = time.time() - t
        stop.set(); th.join()
        rec = {"name": cfg["name"], "ok": all(p.returncode == 0 for p in procs),
               "fallback_warnings": sum(e.count("Fallback mode") for e in errs)}
        if not rec["ok"]:
            rec["error"] = [e.strip().splitlines()[-1:] for e in errs]
            report.append(rec); print(json.dumps(rec), flush=True); continue
        R = [json.load(open(os.path.join(out_dir, f"c{i}_p{p}.json"))) for p in range(cfg["procs"])]
        r2 = [r["run2"] for r in R]
        rec.update({"procs": cfg["procs"], "frames_per_proc": n,
                    "wall_s_run2": max(r["seconds"] for r in r2),
                    "fps": round(cfg["procs"] * n / max(r["seconds"] for r in r2), 2),
                    "cpu_pct": sum(r["cpu_pct"] for r in r2),
                    "gpu_util_mean": round(float(np.mean([s[0] for s in samples])), 1) if samples else None,
                    "gpu_util_max": max(s[0] for s in samples) if samples else None,
                    "peak_vram_mib": max(s[1] for s in samples) if samples else None,
                    "deterministic": all(r["run1"]["sha"] == r["run2"]["sha"] for r in R)
                    and len({r["run1"]["sha"] for r in R}) == 1})
        z = np.load(os.path.join(out_dir, f"c{i}_p0.npz"))
        if ref is None:
            ref = z; rec["reference"] = True
        same_n = np.array_equal(z["n"], ref["n"])
        rec["person_count_mismatch_frames"] = int((z["n"] != ref["n"]).sum()) if len(z["n"]) == len(ref["n"]) else None
        if same_n:
            d = np.abs(z["K"] - ref["K"])
            rec.update(identical_to_ref=bool((d == 0).all() and np.array_equal(z["S"], ref["S"])),
                       max_abs_kp_diff_px=float(d.max()), median_abs_kp_diff_px=float(np.median(d)),
                       max_abs_score_diff=float(np.abs(z["S"] - ref["S"]).max()))
        report.append(rec); print(json.dumps(rec), flush=True)
        json.dump(report, open(os.path.join(out_dir, "gpu_bench.json"), "w"), indent=1)
    return report


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--worker":
        worker(json.load(open(sys.argv[2])))
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("video"); ap.add_argument("out_dir")
        ap.add_argument("--frames", type=int, default=150)
        a = ap.parse_args()
        driver(a.video, a.out_dir, a.frames)
