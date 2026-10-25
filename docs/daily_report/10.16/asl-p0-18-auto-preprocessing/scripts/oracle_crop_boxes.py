"""P0-18 DEV ONLY: recover the official (oracle) signer-crop box of each dev oracle-arm clip in full-frame pixels, from
poses of the canonical GPU pose environment only (full-video npz from vm_worker.py, C_official pkls from
vm_official.py); no Mac CPU / P0-12 pose is read.

Same affine model as P0-12 crossframe_alignment.py: x_C = sx * x_B + tx per axis, B = our full-frame signer track over
the clip's re-aligned window, C = the official crop clip (which covers that window). The frame offset between the two
(container rounding) is searched in [-MAX_OFF, MAX_OFF] by the smallest median residual. The crop origin is -t/s;
W, H are the official crop's frame size. Used to SCORE crops; never an input to the automatic pipeline.

Usage: python -I oracle_crop_boxes.py --vid-dir DIR --official-dir DIR --refs TEST_REFS.json --ids IDS.txt --out OUT.json
"""
import argparse, json, os, pickle, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "asl-p0-16-experimental-credibility", "scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402
import p018_lib as L  # noqa: E402
import pose_extract as PE  # noqa: E402

IDX = [0] + list(range(3, 11)) + list(range(91, 133))
MAX_OFF = 6


def official_track(pkl):
    d = pickle.load(open(pkl, "rb")); wh = np.array(d["frame_wh"], float)
    K, S, _ = L.select_signer([np.asarray(k) * wh for k in d["keypoints"]], d["scores"])
    return K, S, d["frame_wh"]


def fit(kb, sb, kc, sc, off):
    """Affine fit of C frame i+off on B frame i over confident shared keypoints: (sx, tx, sy, ty, median residual px,
    frames used), or None if too few points."""
    ib = np.arange(len(kb)); ic = ib + off; ok = (ic >= 0) & (ic < len(kc))
    b, c = kb[ib[ok]][:, IDX], kc[ic[ok]][:, IDX]
    m = (sb[ib[ok]][:, IDX] > L.THR) & (sc[ic[ok]][:, IDX] > L.THR)
    if m.sum() < 50:
        return None
    coef, res = [], []
    for ax in (0, 1):
        X = np.stack([b[..., ax][m], np.ones(m.sum())], 1)
        co = np.linalg.lstsq(X, c[..., ax][m], rcond=None)[0]
        coef.append(co); res.append(X @ co - c[..., ax][m])
    return (*coef[0], *coef[1], float(np.median(np.hypot(*res))), int(ok.sum()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vid-dir", required=True); ap.add_argument("--official-dir", required=True)
    ap.add_argument("--refs", required=True); ap.add_argument("--ids", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ids = open(a.ids).read().split()
    assert_not_holdout(ids)
    R = json.load(open(a.refs)); out = {}; videos = {}
    for cid in ids:
        pkl = os.path.join(a.official_dir, cid + ".pkl")
        if not os.path.exists(pkl):
            continue
        kc, sc, (W, H) = official_track(pkl)
        vn = R[cid]["video_name"]
        if vn not in videos:
            videos = {vn: PE.VideoPose(os.path.join(a.vid_dir, vn + ".npz"))}
        kb, sb, _, _ = videos[vn].clip_pose(R[cid]["rs"], R[cid]["re"])
        rec = {"W": W, "H": H, "aspect": W / H, "x0": None, "y0": None}
        fits = {o: f for o in range(-MAX_OFF, MAX_OFF + 1) if (f := fit(kb, sb, kc, sc, o)) is not None}
        if fits:
            o = min(fits, key=lambda k: fits[k][4]); sx, tx, sy, ty, r, n = fits[o]
            rec.update(x0=float(-tx / sx), y0=float(-ty / sy), sx=float(sx), sy=float(sy), offset_frames=o,
                       median_resid_px=r, n_frames=n)
        out[cid] = rec
    json.dump(out, open(a.out, "w"), indent=1)
    pos = [v for v in out.values() if v["x0"] is not None]
    print({"clips": len(out), "with_position": len(pos),
           "x0_median": round(float(np.median([v["x0"] for v in pos])), 1),
           "y0_median": round(float(np.median([v["y0"] for v in pos])), 1),
           "scale_median": round(float(np.median([v["sx"] for v in pos])), 4),
           "resid_px_median": round(float(np.median([v["median_resid_px"] for v in pos])), 2),
           "aspect_median": round(float(np.median([v["aspect"] for v in out.values()])), 3)})
