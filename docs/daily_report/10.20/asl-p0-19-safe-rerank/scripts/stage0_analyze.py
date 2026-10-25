"""P0-19 Stage 0 analysis (Mac CPU): gates G1-G5, criteria C1-C3 for k=4 and k=8, GO / NO-GO / VOID.

Every definition comes from config/stage0_config.json (frozen; its hash and this script's hash are checked against
STAGE0_FREEZE.json before anything is computed). References are How2Sign TEST; the val CSV is never opened.

Usage: python -I stage0_analyze.py --main WORK/stage0/main --repeat WORK/stage0/repeat --out WORK/stage0/result
       [--allow-partial]   (smoke only: analyse whatever clips are present; no decision is written)
Writes <out>/STAGE0_RESULT.json and <out>/STAGE0_RESULT.md.
"""
import argparse, json, os, sys

import numpy as np
import sacrebleu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p019_common import CONFIG, EXP, P014, guard_and_trip, load_config, load_matcher, sha256  # noqa: E402
from stage0_verdict import stage0_decision  # noqa: E402

REF_DIR = os.path.expanduser("~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/"
                             "landmark_t5_1pct/local_run_10pct/raw_download")
ap = argparse.ArgumentParser()
ap.add_argument("--main", required=True)
ap.add_argument("--repeat", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--train-csv", default=os.path.join(REF_DIR, "how2sign_realigned_train.csv"))
ap.add_argument("--test-csv", default=os.path.join(REF_DIR, "how2sign_realigned_test.csv"))
ap.add_argument("--allow-partial", action="store_true")
a = ap.parse_args()

# ------------------------------------------------------------------ freeze check
freeze = json.load(open(os.path.join(EXP, "STAGE0_FREEZE.json")))
for rel, h in freeze["files"].items():
    if sha256(os.path.join(EXP, rel)) != h:
        raise SystemExit(f"STAGE0_FREEZE mismatch: {rel} changed after the freeze")
cfg = load_config()["stage0"]
TH = cfg["go_thresholds"]

import csv  # noqa: E402
man = [r for r in csv.DictReader(open(os.path.join(P014, "splits", "manifest.csv"))) if r["role"] == cfg["role"]]
ids = [r["clip_id"] for r in man]
trip = guard_and_trip(ids)

pred_path = os.path.join(P014, "full_run", "vm_decode", "predictions.jsonl")
stored = {p["clip_id"]: p for p in map(json.loads, open(pred_path))}
main = [json.loads(l) for l in open(os.path.join(a.main, "candidates.jsonl"))]
rep = [json.loads(l) for l in open(os.path.join(a.repeat, "candidates.jsonl"))]
meta = [json.load(open(os.path.join(d, "run_meta.json"))) for d in (a.main, a.repeat)]
byid = {r["clip_id"]: r for r in main}
use = [c for c in ids if c in byid] if a.allow_partial else ids
gates, info = {}, {"n_clips": len(use)}

# ------------------------------------------------------------------ G4 input integrity
g4 = sha256(pred_path).startswith("0116a41a") and len(stored) == len(ids)
g4 &= [r["clip_id"] for r in main] == (use if a.allow_partial else ids)
pose_bad = [c for c in use if byid[c]["pose_sha256"] != stored[c]["pose_sha256"]]
gates["G4_input_integrity"] = bool(g4 and not pose_bad)
info["G4"] = {"pose_sha_mismatch": len(pose_bad), "order_and_coverage_ok": bool(g4)}

# ------------------------------------------------------------------ G1 reproduction (num_beams=4 rank 0 == stored)
g1_bad = [c for c in use if byid[c]["k4"]["cands"][0]["text"] != stored[c]["pred"]
          or byid[c]["k4"]["cands"][0]["n_tokens"] != stored[c]["n_tokens"]]
gates["G1_reproduction"] = not g1_bad and len(use) > 0
info["G1"] = {"identical": len(use) - len(g1_bad), "of": len(use), "examples": g1_bad[:5]}

# ------------------------------------------------------------------ G2 determinism (independent repeat run)
want_rep = use[: len(rep)] if a.allow_partial else ids[:40]
g2_ok, max_ds, g2_bad = [r["clip_id"] for r in rep] == want_rep, 0.0, []
for r in rep:
    m = byid.get(r["clip_id"])
    for k in cfg["ks"]:
        x, y = (m or {}).get(f"k{k}", {}).get("cands"), r[f"k{k}"]["cands"]
        if x is None or [(c["rank"], c["ids"], c["text"]) for c in x] != [(c["rank"], c["ids"], c["text"]) for c in y]:
            g2_bad.append((r["clip_id"], k)); continue
        max_ds = max(max_ds, max(abs(c["seq_score"] - d["seq_score"]) for c, d in zip(x, y)))
gates["G2_determinism"] = bool(g2_ok and not g2_bad and max_ds <= 1e-5)
info["G2"] = {"repeat_ids_ok": g2_ok, "mismatches": g2_bad[:5], "max_abs_seq_score_diff": max_ds}

# ------------------------------------------------------------------ G3 no holdout access
g3 = trip["tripwire_installed"] and all(m.get("tripwire_installed") for m in meta)
g3 &= all(m.get("archive_dir_allowed") == "test-pose-rtmpose-192/" for m in meta)
g3 &= all(m.get("guard_checked_ids") == m.get("n_rows") for m in meta)
gates["G3_no_holdout"] = bool(g3)
info["G3"] = {"runs_with_tripwire": sum(bool(m.get("tripwire_installed")) for m in meta), "analysis_tripwire": True}

# ------------------------------------------------------------------ G5 label reproduction
present, crow, LIDX, refs = load_matcher(a.train_csv, a.test_csv)
CON = [r["concept"] for r in crow]
Y = np.array([[int(r[c]) for c in CON] for r in man])
Yhat = np.array([present(refs[c]) for c in ids])
Dtop = np.array([present(stored[c]["pred"]) for c in ids])
missed = (Y[:, LIDX] == 1) & (Dtop[:, LIDX] == 0)
gates["G5_label_reproduction"] = bool((Y == Yhat).all() and int(Dtop[:, LIDX].sum()) == 888 and int(missed.sum()) == 498)
info["G5"] = {"label_mismatch": int((Y != Yhat).sum()), "tierL_mentions_top1": int(Dtop[:, LIDX].sum()),
              "missed_cells": int(missed.sum())}

# ------------------------------------------------------------------ pools and criteria
row = {c: i for i, c in enumerate(ids)}


def pool(c, k):
    texts = [stored[c]["pred"]] if k == 8 else []
    texts += [x["text"] for x in byid[c][f"k{k}"]["cands"]]
    seen, out = set(), []
    for t in texts:
        if t not in seen:
            seen.add(t); out.append(t)
    return out


def lset(t):
    v = present(t)
    return frozenset(CON[j] for j in LIDX if v[j])


res = {}
refs_use = [refs[c] for c in use]
top1 = [stored[c]["pred"] for c in use]
_chrf = sacrebleu.CHRF()
chrf_top1 = _chrf.corpus_score(top1, [refs_use]).score
assert chrf_top1 == sacrebleu.corpus_chrf(top1, [refs_use]).score
chrf_sig = str(_chrf.get_signature())
bleu_top1 = sacrebleu.corpus_bleu(top1, [refs_use]).score
for k in cfg["ks"]:
    n_div, recovered, oracle, sizes, big = 0, 0, [], [], 0
    for c in use:
        P = pool(c, k); sizes.append(len(P))
        sets = [lset(t) for t in P]
        n_div += any(s != sets[0] for s in sets[1:])
        i = row[c]
        for j in LIDX:
            if missed[i, j] and any(CON[j] in s for s in sets):
                recovered += 1
        sc = [sacrebleu.sentence_chrf(t, [refs[c]]).score for t in P]
        b = int(np.argmax(sc)); oracle.append(P[b]); big += sc[b] >= sc[0] + 5
    chrf_or = sacrebleu.corpus_chrf(oracle, [refs_use]).score
    res[f"k{k}"] = {"C1_diversity_fraction": n_div / len(use), "C1_clips": n_div,
                    "C2_recovered_missed_cells": recovered, "C2_of": int(missed[[row[c] for c in use]].sum()),
                    "C3_oracle_chrf": chrf_or, "top1_chrf": chrf_top1, "C3_delta_chrf": chrf_or - chrf_top1,
                    "desc_mean_unique_candidates": float(np.mean(sizes)),
                    "desc_oracle_bleu4": sacrebleu.corpus_bleu(oracle, [refs_use]).score, "desc_top1_bleu4": bleu_top1,
                    "desc_clips_oracle_ge_top1_plus5_chrf": int(big),
                    "desc_decode_sec_mean": float(np.mean([byid[c][f"k{k}"]["sec"] for c in use]))}
criteria = {}
for k in cfg["ks"]:
    r = res[f"k{k}"]
    criteria[f"C1_k{k}"] = r["C1_diversity_fraction"] >= TH["C1_diversity_min_fraction"]
    criteria[f"C2_k{k}"] = r["C2_recovered_missed_cells"] >= TH["C2_recovery_min_cells"]
    criteria[f"C3_k{k}"] = r["C3_delta_chrf"] >= TH["C3_oracle_min_delta_chrf"]

out = {"gates": gates, "criteria": criteria, "metrics": res, "gate_details": info,
       "sacrebleu": sacrebleu.__version__, "chrf_signature": chrf_sig,
       "freeze_sha256": sha256(os.path.join(EXP, "STAGE0_FREEZE.json")), "partial_smoke": a.allow_partial}
if a.allow_partial:
    out["decision"] = "NONE (smoke run on a partial clip set; not a Stage 0 result)"
else:
    out["decision"] = stage0_decision(gates, criteria)
os.makedirs(a.out, exist_ok=True)
json.dump(out, open(os.path.join(a.out, "STAGE0_RESULT.json"), "w"), indent=1, default=str)

L = [f"# P0-19 Stage 0 result{' (SMOKE, partial)' if a.allow_partial else ''}", "",
     f"Decision: **{out['decision'] if a.allow_partial else out['decision']['stage0']}**", "", "| Gate | Pass |", "|---|---|"]
L += [f"| {g} | {'PASS' if v else 'FAIL'} |" for g, v in gates.items()]
L += ["", "| Metric | k=4 | k=8 | Threshold |", "|---|---|---|---|"]
for key, th in [("C1_diversity_fraction", f">= {TH['C1_diversity_min_fraction']}"),
                ("C2_recovered_missed_cells", f">= {TH['C2_recovery_min_cells']} of 498"),
                ("C3_delta_chrf", f">= {TH['C3_oracle_min_delta_chrf']}")]:
    L.append(f"| {key} | {res['k4'][key]:.4f} | {res['k8'][key]:.4f} | {th} |")
open(os.path.join(a.out, "STAGE0_RESULT.md"), "w").write("\n".join(L) + "\n")
print(json.dumps({"decision": out["decision"], "gates": gates, "criteria": criteria}, indent=1, default=str))
