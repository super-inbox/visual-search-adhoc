"""P0-A provenance (no decoding): which pose / window / input each 45-case review clip maps to.

Reads only committed repo files plus the git-ignored P0-12 prepared pose inputs (sha256-checked against the committed
CHECKSUMS.sha256). Every clip id passes the P0-16 holdout guard; no H18/H19 or How2Sign val material is opened.

Usage (repo root):
  /opt/anaconda3/envs/unisign-cpu-arm64/bin/python -I \
      asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/scripts/build_provenance.py

Writes, next to this script's parent folder:
  provenance/case_provenance.csv   one row per review case (45)
  provenance/provenance_summary.json
  case_list.csv                    P0-A roles (focus / named control / hash-selected ordinary control / decode-only)
"""
import csv, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(EXP, "..", "..", "..", ".."))
DR = os.path.join(REPO, "docs", "daily_report")
P012 = os.path.join(DR, "10.06", "asl-p0-12-unisign-pose-gap")
PREP = os.path.join(P012, "artifacts", "prepared_inputs")
SHEET = os.path.join(DR, "10.18", "asl-review-inspection-sheet")
TAX = os.path.join(DR, "10.13", "asl-unisign-error-taxonomy")
P016 = os.path.join(DR, "10.16", "asl-p0-16-experimental-credibility")
BENCH = os.path.join(REPO, "asl-translator", "data", "public_benchmarks", "how2sign_v2")

sys.path.insert(0, os.path.join(P012, "scripts"))
sys.path.insert(0, os.path.join(P016, "scripts"))
import safe_pickle  # noqa: E402
from holdout_guard import assert_not_holdout  # noqa: E402

CONDS = ["A_official", "B_ours_5p39", "C_ours_on_official_crop"]
FOCUS = ["R01", "R18", "R42", "R15", "R24", "R40"]           # boss report 2026-10-21 §7
NAMED_CONTROL = ["R41"]                                        # boss report §7: "不应被修坏" control
OTHER_P0 = {"R02": "P0-B", "R05": "P0-B", "R35": "P0-B/P0-C", "R10": "P0-C", "R26": "P0-C", "R29": "P0-C"}
N_ORDINARY = 6
MAX_FRAMES = 256                                               # Uni-Sign random-subsamples above this


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


sheet = list(csv.DictReader(open(os.path.join(SHEET, "inspection_sheet.csv"))))
vman = {r["review_id"]: r for r in csv.DictReader(open(os.path.join(SHEET, "videos_manifest.csv")))}
inputs = {}
for line in open(os.path.join(TAX, "inputs_128.jsonl")):
    r = json.loads(line)
    inputs[r["clip_id"]] = r
seg = json.load(open(os.path.join(P012, "data", "segment_alignment_128.json")))
checks = {}
for line in open(os.path.join(PREP, "CHECKSUMS.sha256")):
    h, p = line.split(None, 1)
    checks[p.strip()] = h
status = {r["clip_id"]: r for r in csv.DictReader(open(os.path.join(P016, "CLIP_STATUS.csv")))}
bman = {r["how2sign_id"]: r for r in csv.DictReader(open(os.path.join(BENCH, "manifest.csv")))}

ids = [r["clip_id"] for r in sheet]
assert_not_holdout(ids)                                        # raises on any val / H18 / H19 clip or video

rows = []
for r in sheet:
    rid, cid = r["review_id"], r["clip_id"]
    inp, s, st, bm = inputs.get(cid), seg.get(cid, {}), status.get(cid, {}), bman.get(cid, {})
    o = {
        "review_id": rid, "clip_id": cid, "video_id": r["video_id"],
        "in_frozen128": int(inp is not None), "frozen128_idx": inp["idx"] if inp else "",
        "p016_status": st.get("status", "NOT_LISTED"), "p014_role": st.get("p014_role", ""),
        "in_p15_dev": st.get("in_p15_dev", ""), "in_p15_final": st.get("in_p15_final", ""),
        "holdout_guard": "PASS",
        "display_video_sha256": vman.get(rid, {}).get("sha256", ""),
        "display_video_sha_eq_benchmark": int(vman.get(rid, {}).get("sha256", "x") == bm.get("video_sha256", "y")),
        "display_video_s": r["duration_s"],
        "orig_start": s.get("ours_start", ""), "orig_end": s.get("ours_end", ""),
        "realigned_start": s.get("realigned_start", ""), "realigned_end": s.get("realigned_end", ""),
        "iou_orig_vs_realigned": s.get("iou", ""),
    }
    for c in CONDS:
        rel = f"{c}/test-pose-rtmpose-192/{cid}.pkl"
        p = os.path.join(PREP, rel)
        if os.path.exists(p):
            d = safe_pickle.load(p)
            n = len(d["keypoints"])
            o[f"{c}_pkl"] = os.path.relpath(p, REPO)
            o[f"{c}_sha_ok"] = int(sha256(p) == checks.get(rel))
            o[f"{c}_frames"] = n
            o[f"{c}_w_h"] = "x".join(str(int(v)) for v in d["w_h"])
            o[f"{c}_gt256"] = int(n > MAX_FRAMES)
        else:
            o[f"{c}_pkl"], o[f"{c}_sha_ok"], o[f"{c}_frames"], o[f"{c}_w_h"], o[f"{c}_gt256"] = "MISSING", 0, "", "", ""
    pred = (inp or {}).get("predictions", {})
    o["sheet_prod_eq_B_ours_5p39"] = int(bool(pred) and r["prod_output"].strip() == pred.get("B_ours_5p39", "").strip())
    o["sheet_unisign_eq_A_official"] = int(bool(pred) and r["unisign_output"].strip() == pred.get("A_official", "").strip())
    o["other_p0"] = OTHER_P0.get(rid, "")
    rows.append(o)

# ordinary controls: frozen, reference-free rule = lowest sha256(clip_id) among cases not focus / named / other-P0
pool = [o for o in rows if o["review_id"] not in FOCUS + NAMED_CONTROL and o["review_id"] not in OTHER_P0]
ordinary = sorted(pool, key=lambda o: hashlib.sha256(o["clip_id"].encode()).hexdigest())[:N_ORDINARY]
ord_ids = {o["review_id"] for o in ordinary}
for o in rows:
    rid = o["review_id"]
    o["p0a_role"] = ("focus" if rid in FOCUS else "named_control" if rid in NAMED_CONTROL
                     else "ordinary_control" if rid in ord_ids else "decode_only")

out = os.path.join(EXP, "provenance")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "case_provenance.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
order = {"focus": 0, "named_control": 1, "ordinary_control": 2, "decode_only": 3}
with open(os.path.join(EXP, "case_list.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["review_id", "clip_id", "p0a_role", "human_review", "other_p0"])
    for o in sorted(rows, key=lambda o: (order[o["p0a_role"]], o["review_id"])):
        w.writerow([o["review_id"], o["clip_id"], o["p0a_role"], int(o["p0a_role"] != "decode_only"), o["other_p0"]])

summ = {
    "n_cases": len(rows),
    "in_frozen128": sum(o["in_frozen128"] for o in rows),
    "holdout_guard": "PASS (all ids)",
    "pkl_present_and_sha_ok": {c: sum(o[f"{c}_sha_ok"] for o in rows) for c in CONDS},
    "gt256_frames": {c: [o["review_id"] for o in rows if o[f"{c}_gt256"] == 1] for c in CONDS},
    "sheet_prod_eq_B_ours_5p39": sum(o["sheet_prod_eq_B_ours_5p39"] for o in rows),
    "sheet_unisign_eq_A_official": sum(o["sheet_unisign_eq_A_official"] for o in rows),
    "display_video_sha_eq_benchmark": sum(o["display_video_sha_eq_benchmark"] for o in rows),
    "iou0_orig_vs_realigned": [o["review_id"] for o in rows if o["iou_orig_vs_realigned"] == 0.0],
    "iou_lt_0_5": [o["review_id"] for o in rows if o["iou_orig_vs_realigned"] != "" and o["iou_orig_vs_realigned"] < 0.5],
    "p016_status_counts": {k: sum(o["p016_status"] == k for o in rows) for k in sorted({o["p016_status"] for o in rows})},
    "p014_role_counts": {k: sum(o["p014_role"] == k for o in rows) for k in sorted({o["p014_role"] for o in rows})},
    "in_p15_final": [o["review_id"] for o in rows if o["in_p15_final"] == "1"],
    "ordinary_controls": sorted(ord_ids),
}
json.dump(summ, open(os.path.join(out, "provenance_summary.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))
