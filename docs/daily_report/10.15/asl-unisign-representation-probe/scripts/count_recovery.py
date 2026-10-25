"""P0-14: absolute counts behind the fusion-readiness analysis (descriptive; no new thresholds, nothing fitted).

Tier L, test_clean, frozen OOF-F1 thresholds from run_probe.py, frozen matcher from build_concepts.py (as in
analyze_fusion_readiness.py). For each probe: of the (clip, concept) positives Uni-Sign's translation misses, how many
the probe fires on (recovered); how many probe fires land on negatives the translation also left out (false adds);
the precision of what the probe would add; and overlap between probes.
Usage: python -I count_recovery.py --probe-dir . --predictions predictions.jsonl --results results/lr --csvs T V T --out x.json
"""
import argparse, csv, json, os, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--probe-dir", required=True)
ap.add_argument("--predictions", required=True)
ap.add_argument("--results", required=True)
ap.add_argument("--csvs", nargs=3, required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_concepts.py")).read()
src = src.split("# ---------------------------------------------------------------- per-clip annotations")[0]
g = {"__name__": "bc"}; argv = sys.argv; sys.argv = ["bc", *a.csvs, a.probe_dir]
exec(compile(src, "build_concepts.py", "exec"), g); sys.argv = argv
con = list(csv.DictReader(open(os.path.join(a.probe_dir, "concepts", "concept_list_v1.csv"))))
L = [k for k, c in enumerate(con) if c["tier"] == "L"]

def present(s):
    lem, tok = g["lemmas"](s), set(g["tokens"](s))
    return [int((c["concept"].lower() in lem) if c["match"] == "lemma" else bool(tok & set(c["forms"].split()))) for c in con]

man = [r for r in csv.DictReader(open(os.path.join(a.probe_dir, "splits", "manifest.csv"))) if r["role"] == "test_clean"]
pred = {json.loads(l)["clip_id"]: json.loads(l)["pred"] for l in open(a.predictions)}
Y = np.array([[int(r[c["concept"]]) for c in con] for r in man])[:, L]
Dm = np.array([present(pred[r["clip_id"]]) for r in man])[:, L]
missed, neg0 = (Y == 1) & (Dm == 0), (Y == 0) & (Dm == 0)
out = {"tier": "L", "n_clips": len(man), "n_concepts": len(L), "n_positive_cells": int(Y.sum()),
       "translation": {"hit": int(((Y == 1) & (Dm == 1)).sum()), "missed": int(missed.sum()),
                       "false_mentions": int(((Y == 0) & (Dm == 1)).sum())}, "probes": {}}
FR = {"p10": [f"p10_d{i}" for i in range(5)], "p25": [f"p25_d{i}" for i in range(5)],
      "p50": [f"p50_d{i}" for i in range(3)], "p100": ["p100_d0"]}
P100 = {}
for frac, draws in FR.items():
    out["probes"][frac] = {}
    for rep in ("raw", "fsign", "mt5", "length"):
        vals = []
        for d in draws:
            P = np.asarray(json.load(open(os.path.join(a.results, f"{rep}_ms_{d}.json")))["test_pred"])[:, L]
            rec, fa = int((P * missed).sum()), int((P * neg0).sum())
            vals.append((rec, fa))
            if frac == "p100":
                P100[rep] = P
        rec, fa = np.mean([v[0] for v in vals]), np.mean([v[1] for v in vals])
        out["probes"][frac][rep] = {"recovered": float(rec), "recovered_frac_of_missed": float(rec / missed.sum()),
                                    "false_adds": float(fa), "precision_of_adds": float(rec / max(rec + fa, 1)),
                                    "n_draws": len(draws)}
any3 = np.maximum.reduce([P100[r] for r in ("raw", "fsign", "mt5")])
out["p100_overlap"] = {"recovered_by_any_of_raw_fsign_mt5": int((any3 * missed).sum()),
                       "mt5_only": int((P100["mt5"] * (1 - P100["fsign"]) * (1 - P100["raw"]) * missed).sum()),
                       "fsign_only": int((P100["fsign"] * (1 - P100["mt5"]) * (1 - P100["raw"]) * missed).sum()),
                       "raw_only": int((P100["raw"] * (1 - P100["mt5"]) * (1 - P100["fsign"]) * missed).sum()),
                       "mt5_and_fsign": int((P100["mt5"] * P100["fsign"] * missed).sum())}
json.dump(out, open(a.out, "w"), indent=1)
print(json.dumps(out, indent=1))
