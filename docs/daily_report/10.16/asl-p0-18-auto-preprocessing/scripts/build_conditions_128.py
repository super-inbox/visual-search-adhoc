"""P0-18 DEV: timing-vs-crop decomposition on the 128 benchmark from the existing P0-12 poses (no new extraction).

  A_old           original timing, full frame                 (= P0-12 B_ours_5p39)
  A_oraclecrop    original timing, official crop aspect       (~ P0-12 B_aspect)
  A_autocrop      original timing, automatic crop
  C_oracle        re-aligned timing, official crop            (= P0-12 C_ours_on_official_crop)
  C_fullframe     re-aligned timing, full-frame aspect
  C_autocrop      re-aligned timing, automatic crop

Uni-Sign is invariant to translation, so only crop W/H matters. For C poses the full-frame position needs the
oracle origin; where it is unknown (28 clips, no overlap) the median origin is used, which can only affect clamping.

Usage: python -I build_conditions_128.py ORACLE_BOXES_JSON CROP_PARAMS_JSON OUT_ROOT
"""
import json, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p018_lib as L  # noqa: E402

P012 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                    "10.06", "asl-p0-12-unisign-pose-gap")
sys.path.insert(0, os.path.join(P012, "scripts"))
import safe_pickle  # noqa: E402

OB = json.load(open(sys.argv[1])); CP = json.load(open(sys.argv[2]))["selected_params"]; OUT = sys.argv[3]
PI = os.path.join(P012, "artifacts", "prepared_inputs")
med_x0 = float(np.median([v["x0"] for v in OB.values() if v["x0"] is not None]))
med_y0 = float(np.median([v["y0"] for v in OB.values() if v["y0"] is not None]))
FW, FH = 1280, 720


def load(cond, cid):
    d = safe_pickle.load(os.path.join(PI, cond, "test-pose-rtmpose-192", cid + ".pkl"))
    wh = np.array(d["w_h"], float)
    return (np.stack([np.asarray(x, float)[0] for x in d["keypoints"]]) * wh,
            np.stack([np.asarray(x, float)[0] for x in d["scores"]]), d)


names = ["A_old", "A_oraclecrop", "A_autocrop", "C_oracle", "C_fullframe", "C_autocrop"]
for n in names:
    os.makedirs(os.path.join(OUT, n), exist_ok=True)
meta, maxdiff = {}, {"A_old_vs_B": 0.0, "C_oracle_vs_C": 0.0}
for cid, o in sorted(OB.items()):
    KB, SB, dB = load("B_ours_5p39", cid)
    KC, SC, dC = load("C_ours_on_official_crop", cid)
    x0 = o["x0"] if o["x0"] is not None else med_x0; y0 = o["y0"] if o["y0"] is not None else med_y0
    KCf = KC + np.array([x0, y0])                                     # C in full-frame pixels
    boxA, failA = L.signer_box(KB, SB, (FW, FH), CP)
    boxC, failC = L.signer_box(KCf, SC, (FW, FH), CP)
    out = {
        "A_old": L.to_unisign(KB, SB, (0, 0, FW, FH)),
        "A_oraclecrop": L.to_unisign(KB, SB, (x0, y0, o["W"], o["H"])),
        "A_autocrop": L.to_unisign(KB, SB, boxA),
        "C_oracle": L.to_unisign(KC, SC, (0, 0, o["W"], o["H"])),
        "C_fullframe": L.to_unisign(KCf, SC, (0, 0, FW, FH)),
        "C_autocrop": L.to_unisign(KCf, SC, boxC),
    }
    for n, d in out.items():
        pickle.dump(d, open(os.path.join(OUT, n, cid + ".pkl"), "wb"))
    maxdiff["A_old_vs_B"] = max(maxdiff["A_old_vs_B"], float(np.max(np.abs(
        np.stack([k[0] for k in out["A_old"]["keypoints"]]) - np.stack([np.asarray(k, float)[0] for k in dB["keypoints"]])))))
    maxdiff["C_oracle_vs_C"] = max(maxdiff["C_oracle_vs_C"], float(np.max(np.abs(
        np.stack([k[0] for k in out["C_oracle"]["keypoints"]]) - np.stack([np.asarray(k, float)[0] for k in dC["keypoints"]])))))
    meta[cid] = {"boxA": boxA, "failA": failA, "boxC": boxC, "failC": failC, "oracle_aspect": o["aspect"],
                 "origin_known": o["x0"] is not None}
json.dump({"crop_params": CP, "max_abs_diff": maxdiff, "clips": meta}, open(os.path.join(OUT, "conditions_meta.json"), "w"),
          indent=1)
print({"max_abs_diff": maxdiff, "n": len(meta), "failsA": sum(m["failA"] is not None for m in meta.values()),
       "failsC": sum(m["failC"] is not None for m in meta.values())})
assert maxdiff["A_old_vs_B"] < 1e-5 and maxdiff["C_oracle_vs_C"] < 1e-5, "reproduction gate failed"
