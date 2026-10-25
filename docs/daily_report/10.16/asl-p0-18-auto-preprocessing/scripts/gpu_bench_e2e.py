"""P0-18 GPU extractor end-to-end benchmark on ONE full How2Sign TEST video (dev tooling, not part of the pipeline).

Times the whole extract_video path (sequential cv2 decode -> pose -> npz) for candidate configs and compares every
output with a reference npz (the preflight run, ref settings det=on DEFAULT). Model, preprocessing, postprocessing and
output format are rtmlib's / pose_extract's, unchanged; only the ORT session options and the pose batching vary.

Usage: python -I gpu_bench_e2e.py VIDEO.mp4 REF.npz OUT_DIR
"""
import argparse, hashlib, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cv2  # noqa: E402
import numpy as np  # noqa: E402
import onnxruntime as ort  # noqa: E402
import pose_extract as PE  # noqa: E402


def session_wb(det, algo):
    wb = PE.make_wholebody("cuda")
    for kind, tool in (("det", wb.det_model), ("pose", wb.pose_model)):
        so = ort.SessionOptions(); so.use_deterministic_compute = det
        tool.session = ort.InferenceSession(PE.model_path(kind), sess_options=so, providers=[
            ("CUDAExecutionProvider", {"device_id": 0, "cudnn_conv_algo_search": algo})])
        assert tool.session.get_providers()[0] == "CUDAExecutionProvider"
    return wb


def per_frame(wb, workers):
    def f(batch):
        with ThreadPoolExecutor(max_workers=workers) as ex:
            return list(ex.map(lambda fr: wb(np.uint8(fr)), batch))
    return f


def batched(wb, workers, B):
    pm, dm = wb.pose_model, wb.det_model
    pin, pout = pm.session.get_inputs()[0].name, [o.name for o in pm.session.get_outputs()]

    def f(chunk):
        with ThreadPoolExecutor(max_workers=workers) as ex:
            boxes = list(ex.map(lambda fr: dm(np.uint8(fr)), chunk))
        crops, meta = [], []
        for fi, (fr, bb) in enumerate(zip(chunk, boxes)):
            img = np.uint8(fr)
            if len(bb) == 0:
                bb = [[0, 0, img.shape[1], img.shape[0]]]
            for b in bb:
                x, c, s = pm.preprocess(img, b)
                crops.append(np.ascontiguousarray(x.transpose(2, 0, 1), dtype=np.float32)); meta.append((fi, c, s))
        outs = []
        for i in range(0, len(crops), B):
            o = pm.session.run(pout, {pin: np.stack(crops[i:i + B])})
            outs += [[o[0][j:j + 1], o[1][j:j + 1]] for j in range(len(o[0]))]
        per = [([], []) for _ in chunk]
        for (fi, c, s), o in zip(meta, outs):
            k, sc = pm.postprocess(o, c, s); per[fi][0].append(k); per[fi][1].append(sc)
        return [(np.concatenate(k, 0), np.concatenate(s, 0)) for k, s in per]
    return f


def extract(video, out_npz, chunk_fn):
    """pose_extract.extract_video with the per-chunk inference swapped in (same decode, CHUNK and npz layout)."""
    t0 = time.time(); c0 = os.times()
    cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS)
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ks, ss, batch, t_dec = [], [], [], 0.0

    def flush():
        for k, s in chunk_fn(batch):
            ks.append(np.asarray(k, np.float64).reshape(-1, 133, 2)); ss.append(np.asarray(s, np.float32).reshape(-1, 133))
        batch.clear()
    while True:
        td = time.time(); ok, fr = cap.read(); t_dec += time.time() - td
        if not ok:
            break
        batch.append(fr)
        if len(batch) == PE.CHUNK:
            flush()
    if batch:
        flush()
    N = len(ks); P = max([len(k) for k in ks] + [1])
    K = np.zeros((N, P, 133, 2), np.float64); S = np.zeros((N, P, 133), np.float32)
    npers = np.array([len(k) for k in ks], np.int16)
    for t in range(N):
        K[t, :npers[t]], S[t, :npers[t]] = ks[t], ss[t]
    tw = time.time(); np.savez_compressed(out_npz, K=K, S=S, n_persons=npers, fps=fps, frame_wh=np.array([W, H]))
    t_write = time.time() - tw; dt = time.time() - t0; c1 = os.times()
    return {"frames": N, "seconds": round(dt, 1), "fps": round(N / dt, 2), "decode_s": round(t_dec, 1),
            "write_s": round(t_write, 1), "cpu_pct": round(100 * ((c1.user - c0.user) + (c1.system - c0.system)) / dt)}


def compare(a, ref):
    z, r = np.load(a), np.load(ref)
    h = hashlib.sha256()
    for k in ("K", "S", "n_persons"):
        h.update(np.ascontiguousarray(z[k]).tobytes())
    out = {"arrays_sha256": h.hexdigest()[:16], "person_count_mismatch_frames": int((z["n_persons"] != r["n_persons"]).sum())}
    if z["K"].shape == r["K"].shape:
        valid = np.arange(z["K"].shape[1])[None, :] < r["n_persons"][:, None]          # real persons only
        d = np.linalg.norm(z["K"] - r["K"], axis=-1)[valid]; sd = np.abs(z["S"] - r["S"])[valid]
        sc = r["S"][valid]
        out.update(identical=bool((d == 0).all() and (sd == 0).all()), max_kp_px=round(float(d.max()), 4),
                   median_kp_px=float(np.median(d)), p999_kp_px=round(float(np.quantile(d, 0.999)), 4),
                   frac_kp_gt_0p1px=float((d > 0.1).mean()), frac_kp_gt_1px=float((d > 1).mean()),
                   max_kp_px_where_score_ge_0p3=round(float(d[sc >= 0.3].max()), 4) if (sc >= 0.3).any() else None,
                   max_score_diff=float(sd.max()))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("ref"); ap.add_argument("out")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    plan = [("perframe det=on HEURISTIC w4 run1", True, "HEURISTIC", 0),
            ("perframe det=on HEURISTIC w4 run2", True, "HEURISTIC", 0),
            ("perframe det=on EXHAUSTIVE w4", True, "EXHAUSTIVE", 0),
            ("batched B16 det=on HEURISTIC w4 run1", True, "HEURISTIC", 16),
            ("batched B16 det=on HEURISTIC w4 run2", True, "HEURISTIC", 16)]
    rep = []
    for i, (name, det, algo, B) in enumerate(plan):
        wb = session_wb(det, algo)
        fn = batched(wb, 4, B) if B else per_frame(wb, 4)
        fn([cv2.VideoCapture(a.video).read()[1]])                                    # warm-up
        o = os.path.join(a.out, f"e{i}.npz")
        rec = dict(name=name, **extract(a.video, o, fn)); rec.update(compare(o, a.ref))
        rep.append(rec); print(json.dumps(rec), flush=True)
        json.dump(rep, open(os.path.join(a.out, "gpu_bench_e2e.json"), "w"), indent=1)
