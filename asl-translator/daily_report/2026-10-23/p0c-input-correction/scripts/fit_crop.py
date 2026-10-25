"""Estimate where an official crop clip sits in the full frame: per-axis affine fit of official-crop keypoints (P0-12
A_official pkl, normalized) onto P0-18 whole-video full-frame keypoints over the realigned window; searches a frame
offset. usage: fit_crop.py PKL NPZ START_S"""
import sys, pickle, numpy as np
d = pickle.load(open(sys.argv[1], "rb")); W, H = d["w_h"]
kc = np.asarray(d["keypoints"])[:, 0] * [W, H]; sc = np.asarray(d["scores"])[:, 0]
v = np.load(sys.argv[2]); fps = float(v["fps"]); s0 = int(round(float(sys.argv[3]) * fps))
best = None
for off in range(-12, 13):
    xs, ys, ms = [], [], []
    for i in range(len(kc)):
        j = s0 + off + i
        if not 0 <= j < len(v["K"]): continue
        p = int(np.argmax(v["S"][j, :, :11].mean(1)))
        m = (sc[i] > 0.5) & (v["S"][j, p] > 0.5)
        xs.append(np.c_[v["K"][j, p][m], kc[i][m]])
    if not xs: continue
    X = np.concatenate(xs)
    if len(X) < 50: continue
    res, co = [], []
    for ax in (0, 1):
        A = np.c_[X[:, ax], np.ones(len(X))]; c = np.linalg.lstsq(A, X[:, 2 + ax], rcond=None)[0]
        co.append(c); res.append(A @ c - X[:, 2 + ax])
    r = float(np.median(np.hypot(*res)))
    if best is None or r < best[0]: best = (r, off, co, len(X))
r, off, (cx, cy), n = best
x0, y0 = -cx[1] / cx[0], -cy[1] / cy[0]
print(f"crop {W}x{H}: offset_frames={off} scale=({cx[0]:.4f},{cy[0]:.4f}) x0={x0:.1f} y0={y0:.1f} "
      f"x1={x0 + W / cx[0]:.1f} y1={y0 + H / cy[0]:.1f} median_resid_px={r:.2f} points={n}")
