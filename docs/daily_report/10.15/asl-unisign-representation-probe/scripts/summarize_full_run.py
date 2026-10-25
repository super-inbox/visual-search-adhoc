"""P0-14: report tables from the full run (descriptive; reads run_probe.py / analyze_*.py outputs, decides nothing).

Writes <out>/macro_by_fraction.csv, <out>/per_concept_p100.csv, <out>/recovery_per_concept_p100.csv and prints
markdown versions. Usage: python -I summarize_full_run.py --results RESULTS_DIR --out OUT_DIR
"""
import argparse, csv, json, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--results", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
L = os.path.join(a.results, "lr")
os.makedirs(a.out, exist_ok=True)
REPS = ["raw", "fsign", "mt5", "length", "shuffle"]
FRACS = {"p10": 5, "p25": 5, "p50": 3, "p100": 1, "testcv": 3}

def ld(rep, draw):
    return json.load(open(os.path.join(L, f"{rep}_ms_{draw}.json")))

rows = []
for frac, n in FRACS.items():
    draws = [f"testcv_r{i}" for i in range(n)] if frac == "testcv" else [f"{frac}_d{i}" for i in range(n)]
    for rep in REPS:
        rs = [ld(rep, d) for d in draws]
        for tier in ("L", "S"):
            row = {"fraction": frac, "design": "B" if frac == "testcv" else "A", "rep": rep, "tier": tier,
                   "n_draws": n, "n_train": int(np.mean([r["n_train"] for r in rs]))}
            for m in ("precision", "recall", "f1", "auroc", "auprc", "f1_prev_matched"):
                v = [r["macro"][tier][m] for r in rs]
                row[m] = float(np.mean(v)); row[m + "_sd"] = float(np.std(v)) if n > 1 else 0.0
            rows.append(row)
with open(os.path.join(a.out, "macro_by_fraction.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

fr = json.load(open(os.path.join(a.results, "fusion_readiness.json")))
Dper = fr["D_translation"]["per_concept"]
pc = []
for c, d in Dper.items():
    row = {"concept": c, "tier": d["tier"], "n_pos_test": d["n_pos"]}
    for rep in ("raw", "fsign", "mt5"):
        v = ld(rep, "p100_d0")["per_concept"][c]
        for m in ("precision", "recall", "f1", "auroc"):
            row[f"{rep}_{m}"] = v[m]
    for m in ("precision", "recall", "f1"):
        row[f"D_{m}"] = d[m]
    row["D_n_missed"] = d["n_missed"]
    pc.append(row)
with open(os.path.join(a.out, "per_concept_p100.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(pc[0])); w.writeheader(); w.writerows(pc)

rc = []
for frac in ("p10", "p25", "p50", "p100"):
    for rep in ("raw", "fsign", "mt5", "length"):
        r = fr["readiness"][frac]["L"][rep]
        for c, v in r["per_concept"].items():
            rc.append({"fraction": frac, "rep": rep, "concept": c, "n_missed": Dper[c]["n_missed"], **v})
with open(os.path.join(a.out, "recovery_per_concept.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rc[0])); w.writeheader(); w.writerows(rc)

print("| frac | rep | n_train | P | R | F1 | AUROC | AUPRC |\n|---|---|---|---|---|---|---|---|")
for r in rows:
    if r["tier"] == "L":
        sd = f" ±{r['f1_sd']:.3f}" if r["n_draws"] > 1 else ""
        print(f"| {r['fraction']} | {r['rep']} | {r['n_train']} | {r['precision']:.3f} | {r['recall']:.3f} | "
              f"{r['f1']:.3f}{sd} | {r['auroc']:.3f} | {r['auprc']:.3f} |")
print("\n| concept | n_pos | missed by D | D F1 | raw F1/AUROC | fsign F1/AUROC | mt5 F1/AUROC | rec raw | rec fsign | rec mt5 |")
print("|---|---|---|---|---|---|---|---|---|---|")
rec = {(x["rep"], x["concept"]): x for x in rc if x["fraction"] == "p100"}
for r in pc:
    if r["tier"] != "L":
        continue
    c = r["concept"]
    print(f"| {c} | {r['n_pos_test']} | {r['D_n_missed']} | {r['D_f1']:.2f} | {r['raw_f1']:.2f}/{r['raw_auroc']:.2f} | "
          f"{r['fsign_f1']:.2f}/{r['fsign_auroc']:.2f} | {r['mt5_f1']:.2f}/{r['mt5_auroc']:.2f} | "
          f"{rec[('raw', c)]['recovery']:.2f} | {rec[('fsign', c)]['recovery']:.2f} | {rec[('mt5', c)]['recovery']:.2f} |")
