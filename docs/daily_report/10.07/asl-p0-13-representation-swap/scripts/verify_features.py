"""P0-13: verify cached Uni-Sign features (shapes, coverage, alignment with the P0.2 IDs and references).
Usage: python verify_features.py FEAT_ROOT POSE_ROOT P02_RUN_DIR OUT_JSON"""
import csv, json, pickle, sys
from pathlib import Path
import numpy as np

feat_root, pose_root, run, out = map(Path, sys.argv[1:5])
res = {}
for split in ("train", "val", "frozen"):
    ids = [x.strip() for x in open(run / "ids" / f"{split}_ids.txt") if x.strip()]
    rows, bad = [], []
    for cid in ids:
        f = feat_root / split / f"{cid}.npz"
        if not f.exists():
            bad.append((cid, "missing"))
            continue
        z = np.load(f)
        enc, pe = z["enc"], z["pose_emb"]
        pose = pickle.load(open(pose_root / split / f"{cid}.pkl", "rb"))
        raw = int(pose["end"] - pose["start"]) if "start" in pose else len(pose["scores"])
        T = enc.shape[0]
        ok = (enc.shape == (min(raw, 256), 768) and pe.shape == enc.shape and int(z["T"]) == T
              and int(z["n_frames_raw"]) == raw and np.isfinite(enc.astype(np.float32)).all())
        if not ok:
            bad.append((cid, f"shape {enc.shape} raw {raw}"))
        rows.append((raw, T, float(np.linalg.norm(enc.astype(np.float32), axis=1).mean())))
    raw, T, nrm = (np.array(c) for c in zip(*rows))
    res[split] = {"n_ids": len(ids), "n_features": len(rows), "n_bad": len(bad), "bad_examples": bad[:5],
                  "raw_frames_min_median_max": [int(raw.min()), float(np.median(raw)), int(raw.max())],
                  "T_min_median_max": [int(T.min()), float(np.median(T)), int(T.max())],
                  "n_subsampled_to_256": int((raw > 256).sum()),
                  "T_after_p02_stride_rule_max": int(max(len(range(0, t, int(np.ceil(t / 150)))) if t > 150 else t for t in T)),
                  "mean_frame_l2_norm": float(nrm.mean()), "dim": 768, "dtype_on_disk": "float16"}
# reference alignment: the treatment reads texts from the same metadata files P0.2 used; check they equal the
# references P0.2 itself scored against (epoch 20 = val-selected epoch)
for split, f in (("val", "val_predictions/epoch_20.json"), ("frozen", "frozen_predictions/epoch_20.json")):
    p = json.load(open(run / f))
    ids = [x.strip() for x in open(run / "ids" / f"{split}_ids.txt") if x.strip()]
    res[split]["p02_prediction_file_ids_equal_ids_txt_in_order"] = [r["sample_id"] for r in p] == ids
print(json.dumps(res, indent=1))
json.dump(res, open(out, "w"), indent=1)
