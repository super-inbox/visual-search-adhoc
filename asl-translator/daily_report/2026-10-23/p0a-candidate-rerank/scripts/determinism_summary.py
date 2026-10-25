"""P0-A gate G3 evidence: compare the two independent full45 decode processes per domain (run1 canonical, run2 repeat)
and write a compact summary, so run2 itself does not need to be committed.

Compared per clip (everything except wall-clock timing fields): clip order, pool / beam5 counts, order, sources,
ranks, token ids, texts, sequence scores and log-prob sums (|diff| <= 1e-5), pose sha256, clip seed, frame-index and
model-input hashes. Writes runs/full45/DETERMINISM.json.

Usage (repo root): python3 -I asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/scripts/determinism_summary.py
"""
import csv, hashlib, json, os

EXP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(EXP, "runs", "full45")
TOL = 1e-5
TIMING = {"sec_forward", "sec_T", "sec_beam5", "sec_clip"}
SCORES = {"seq_score", "sum_logprob", "source_seq_score", "source_sum_logprob", "beam5_seq_score"}
order = [r["clip_id"] for r in csv.DictReader(open(os.path.join(EXP, "case_list.csv")))]


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def compare(a, b, path=""):
    """-> (list of mismatching paths, max |score diff|); timing fields skipped, score fields within TOL."""
    if isinstance(a, dict):
        if set(a) - TIMING != set(b) - TIMING:
            return [path + ":keys"], 0.0
        bad, md = [], 0.0
        for k in sorted(set(a) - TIMING):
            if k in SCORES and a[k] is not None and b[k] is not None:
                d = abs(a[k] - b[k]); md = max(md, d)
                if d > TOL:
                    bad.append(f"{path}.{k}")
            else:
                x, y = compare(a[k], b[k], f"{path}.{k}"); bad += x; md = max(md, y)
        return bad, md
    if isinstance(a, list):
        if len(a) != len(b):
            return [path + ":len"], 0.0
        bad, md = [], 0.0
        for i, (x, y) in enumerate(zip(a, b)):
            p, d = compare(x, y, f"{path}[{i}]"); bad += p; md = max(md, d)
        return bad, md
    return ([] if a == b else [path]), 0.0


out = {"gate": "G3 determinism (P0_PROTOCOL_FREEZE.md §1.5), run on all 45 cases (protocol minimum: first 5)",
       "tolerance_abs_score": TOL, "ignored_fields": sorted(TIMING), "domains": {}}
for dom in ("A_official", "B_ours_5p39"):
    f1, f2 = (os.path.join(RUNS, dom, r, "candidates.jsonl") for r in ("run1", "run2"))
    r1, r2 = ([json.loads(l) for l in open(f)] for f in (f1, f2))
    m1, m2 = (json.load(open(os.path.join(RUNS, dom, r, "run_meta.json"))) for r in ("run1", "run2"))
    bad, md = compare(r1, r2)
    out["domains"][dom] = {
        "run1_candidates_sha256": sha256(f1), "run2_candidates_sha256": sha256(f2),
        "n_run1": len(r1), "n_run2": len(r2),
        "order_equals_case_list": [x["clip_id"] for x in r1] == order == [x["clip_id"] for x in r2],
        "n_clips_identical": sum(not compare(x, y)[0] for x, y in zip(r1, r2)),
        "mismatches": bad, "max_abs_score_diff": md,
        "subsampled_gt256": [x["review_id"] for x in r1 if x["subsampled"]],
        "frame_idx_and_model_input_hashes_identical": all(x["frame_idx_sha256"] == y["frame_idx_sha256"] and
                                                           x["kps_sha256"] == y["kps_sha256"] for x, y in zip(r1, r2)),
        "same_script_sha256": m1["script_sha256"] == m2["script_sha256"], "script_sha256": m1["script_sha256"],
        "device_precision": [m1["device"], m1["precision"], m2["device"], m2["precision"]],
        "holdout_guard_ids": [m1["guard_checked_ids"], m2["guard_checked_ids"]],
        "tripwires_installed": all(m["tripwire_installed"] and m["reference_tripwire_installed"] for m in (m1, m2)),
        "decode_loop_seconds": [sum(r["seconds"] for r in m1["runs"]), sum(r["seconds"] for r in m2["runs"])],
        "PASS": not bad and len(r1) == len(r2) == len(order) and md <= TOL,
    }
json.dump(out, open(os.path.join(RUNS, "DETERMINISM.json"), "w"), indent=1)
print(json.dumps({d: {k: v[k] for k in ("n_clips_identical", "max_abs_score_diff", "PASS")} for d, v in out["domains"].items()}))
