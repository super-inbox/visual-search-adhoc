"""Per-window hand-keypoint edge statistics from a P0-18 whole-video pose npz (GPU env poses, full frame px).
usage: edge_stats.py NPZ name:start:end [...]"""
import sys, numpy as np
d = np.load(sys.argv[1]); K, S, fps = d["K"], d["S"], float(d["fps"]); W, H = d["frame_wh"]
def signer(i):  # person with the highest mean body score
    return int(np.argmax(S[i, :, :11].mean(1)))
for spec in sys.argv[2:]:
    name, a, b = spec.split(":"); a, b = float(a), float(b)
    fr = range(int(round(a * fps)), int(round(b * fps)))
    n = len(fr); top = low = maxhigh = 0; ymins = []
    for i in fr:
        p = signer(i); hk, hs = K[i, p, 91:133], S[i, p, 91:133]
        ok = hs > 0.3
        ymin = hk[ok, 1].min() if ok.any() else np.nan; ymins.append(ymin)
        top += bool(ok.any() and ymin < 15)
        low += bool((hs[:21] <= 0.3).mean() > 0.5 or (hs[21:] <= 0.3).mean() > 0.5)
    ymins = np.array(ymins)
    print(f"{name} {a:.2f}-{b:.2f}s frames={n} hand_kp_within_15px_of_top={top} "
          f"frames_with_a_hand_mostly_lowconf={low} min_hand_y_px={np.nanmin(ymins):.0f} "
          f"median_min_hand_y_px={np.nanmedian(ymins):.0f}")
