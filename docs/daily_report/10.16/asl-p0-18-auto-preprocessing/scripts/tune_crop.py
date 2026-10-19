"""P0-18 DEV: tune the automatic signer-crop parameters against the oracle boxes (oracle_crop_boxes.py) of the dev
oracle-arm clips: crop agreement only, no translation metric. Poses: the canonical GPU full-video npz, signer track over
each clip's re-aligned window (the frames the official crop covers). Grid search, 5-fold CV grouped by source VIDEO_ID
(deterministic sorted order) for an honest estimate.

Usage: python -I tune_crop.py --vid-dir DIR --refs TEST_REFS.json --boxes ORACLE_BOXES.json --out OUT.json
"""
import argparse, itertools, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "asl-p0-16-experimental-credibility", "scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402
import p018_lib as L  # noqa: E402
import pose_extract as PE  # noqa: E402

GRID = {"pct": [0, 1, 2, 5], "margin_x": [0.0, 0.25, 0.5, 0.75, 1.0, 1.25], "margin_top": [0.0, 0.25, 0.5, 0.75, 1.0],
        "margin_bottom": [0.0], "to_bottom": [True, False]}
combos = [dict(zip(GRID, v)) for v in itertools.product(*GRID.values())]
VIDEO_ID = lambda c: re.sub(r"_\d+(?:_\d+)*-\d+-rgb_front$", "", c)


def evaluate(p, sel):
    ious, aerr, fails = [], [], 0
    for c in sel:
        K, S, wh = poses[c]
        box, fail = L.signer_box(K, S, wh, p)
        fails += fail is not None
        o = OB[c]
        aerr.append(abs(np.log((box[2] / box[3]) / o["aspect"])))
        if o["x0"] is not None:
            ious.append(L.box_iou(box, (o["x0"], o["y0"], o["W"], o["H"])))
    return {"mean_iou": float(np.mean(ious)), "median_iou": float(np.median(ious)),
            "median_abs_log_aspect_err": float(np.median(aerr)), "mean_abs_log_aspect_err": float(np.mean(aerr)),
            "fails": fails, "n_iou": len(ious), "n": len(sel)}


def best_of(sel):
    return max(combos, key=lambda p: (evaluate(p, sel)["mean_iou"], -p["margin_x"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vid-dir", required=True); ap.add_argument("--refs", required=True)
    ap.add_argument("--boxes", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    OB = json.load(open(a.boxes)); R = json.load(open(a.refs))
    ids = sorted(OB)
    assert_not_holdout(ids)
    poses = {}
    for c in ids:
        V = PE.VideoPose(os.path.join(a.vid_dir, R[c]["video_name"] + ".npz"))
        K, S, _, _ = V.clip_pose(R[c]["rs"], R[c]["re"])
        poses[c] = (K, S, V.frame_wh)
    vids = sorted({VIDEO_ID(c) for c in ids}); vfold = {v: i % 5 for i, v in enumerate(vids)}
    fold = {c: vfold[VIDEO_ID(c)] for c in ids}
    cv = []
    for f in range(5):
        tr = [c for c in ids if fold[c] != f]; te = [c for c in ids if fold[c] == f]
        best = best_of(tr)
        cv.append({"fold": f, "params": best, "test": evaluate(best, te)})
    best_all = best_of(ids)
    full = {"mean_iou": float(np.mean([L.box_iou((0, 0, *poses[c][2]), (OB[c]["x0"], OB[c]["y0"], OB[c]["W"], OB[c]["H"]))
                                       for c in ids if OB[c]["x0"] is not None])),
            "median_abs_log_aspect_err": float(np.median([abs(np.log((poses[c][2][0] / poses[c][2][1]) / OB[c]["aspect"]))
                                                          for c in ids]))}
    res = {"grid": GRID, "objective": "mean box IoU vs oracle box (clips with a recovered position)",
           "poses": "canonical GPU full-video npz, re-aligned window", "n_clips": len(ids), "n_videos": len(vids),
           "cv": cv, "cv_mean_test_iou": float(np.mean([x["test"]["mean_iou"] for x in cv])),
           "cv_median_test_aspect_err": float(np.median([x["test"]["median_abs_log_aspect_err"] for x in cv])),
           "selected_params": best_all, "selected_insample": evaluate(best_all, ids), "full_frame_baseline": full}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("cv_mean_test_iou", "cv_median_test_aspect_err", "selected_params",
                                           "selected_insample", "full_frame_baseline")}, indent=1))
