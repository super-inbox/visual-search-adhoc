"""P0-14 step 4 (PROPOSED): paired cluster bootstrap + the pre-registered decision rules (EXPERIMENT_PLAN.md §9).

Reads results/lr/*.json from run_probe.py. Resamples TEST VIDEOS with replacement (B = 2000), applying the same
resample to every representation (paired). Thresholds are fixed (they were chosen on probe-train), so F1 under a
resample is recomputed from the stored binary predictions and AUROC from the stored scores.

Writes results/DECISION.json and prints a verdict per comparison (fsign vs raw, mt5 vs raw) plus the descriptive
mt5 vs fsign layer comparison.
Usage: python -I analyze_probe.py --probe-dir . [--primary-draw p100_d0] [--B 2000]
"""
import argparse, csv, glob, json, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--probe-dir", required=True)
ap.add_argument("--results", default=None)
ap.add_argument("--primary-draw", default="p100_d0")
ap.add_argument("--pool", default="ms")
ap.add_argument("--B", type=int, default=2000)
a = ap.parse_args()
D = a.probe_dir
RES = a.results or os.path.join(D, "results", "lr")

# ---- pre-registered thresholds (copy of EXPERIMENT_PLAN.md §9; do not edit after features exist)
RULES = {"C1_min_delta_macro_f1": 0.05, "C2_min_delta_macro_auroc": 0.03, "C3_min_concepts_auroc_up": 17,
         "C4_low_data_draws": ["p10", "p25"], "C4_min_delta_macro_f1": 0.05, "C5_min_auroc_over_length": 0.05,
         "S1_shuffle_auroc_band": [0.47, 0.53], "layer_pref_min_delta_f1": 0.02}

man = [r for r in csv.DictReader(open(os.path.join(D, "splits", "manifest.csv"))) if r["role"] in ("probe_train", "test_clean")]
test = [r for r in man if r["role"] == "test_clean"]
vid = np.array([r["group"] for r in test])
signer = np.array([r["signer_proxy"] for r in test])
uv, vinv = np.unique(vid, return_inverse=True)
rng = np.random.default_rng(20261015)
BOOT = [rng.integers(0, len(uv), len(uv)) for _ in range(a.B)]
BOOT_IDX = []
members = [np.where(vinv == i)[0] for i in range(len(uv))]
for b in BOOT:
    BOOT_IDX.append(np.concatenate([members[i] for i in b]))

def load(rep, draw, pool=None):
    f = os.path.join(RES, f"{rep}_{pool or a.pool}_{draw}.json")
    return json.load(open(f)) if os.path.exists(f) else None

def auroc(y, s):
    n1 = y.sum(); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return np.nan
    r = np.argsort(np.argsort(s, kind="mergesort"), kind="mergesort") + 1.0  # ties are measure-zero for float scores
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

def f1(y, p):
    tp = (y * p).sum(); d = y.sum() + p.sum()
    return 2 * tp / d if d else 0.0

def macro(res, idx, tier="L", metric="f1", Y=None):
    cs = [c for c, v in res["per_concept"].items() if v["tier"] == tier]
    allc = list(res["per_concept"])
    S = np.asarray(res["test_scores"])[idx]
    P = np.asarray(res["test_pred"])[idx] if res.get("test_pred") is not None else None
    vals = []
    for c in cs:
        k = allc.index(c)
        y = Y[idx, k]
        vals.append(f1(y, P[:, k]) if metric == "f1" else auroc(y, S[:, k]))
    return float(np.nanmean(vals))

concepts = list(json.load(open(glob.glob(os.path.join(RES, "*.json"))[0]))["per_concept"])
Y = np.array([[int(r[c]) for c in concepts] for r in test], dtype=float)

def paired(resA, resB, metric, tier="L", subset=None):
    base = np.arange(len(test)) if subset is None else np.where(subset)[0]
    point = macro(resA, base, tier, metric, Y) - macro(resB, base, tier, metric, Y)
    if subset is None:
        boots = [macro(resA, i, tier, metric, Y) - macro(resB, i, tier, metric, Y) for i in BOOT_IDX]
    else:
        sel = set(base.tolist())
        boots = []
        for i in BOOT_IDX[: a.B // 4]:
            j = np.array([x for x in i if x in sel])
            if len(j):
                boots.append(macro(resA, j, tier, metric, Y) - macro(resB, j, tier, metric, Y))
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    return {"delta": point, "ci95": [float(lo), float(hi)]}

def avg_draws(rep, prefix):
    return [r for r in (load(rep, f"{prefix}_d{d}") for d in range(5)) if r is not None]

def paired_avg(repA, repB, prefix, metric):
    As, Bs = avg_draws(repA, prefix), avg_draws(repB, prefix)
    if not As or len(As) != len(Bs):
        return None
    full = np.arange(len(test))
    point = np.mean([macro(x, full, "L", metric, Y) - macro(y, full, "L", metric, Y) for x, y in zip(As, Bs)])
    boots = [np.mean([macro(x, i, "L", metric, Y) - macro(y, i, "L", metric, Y) for x, y in zip(As, Bs)])
             for i in BOOT_IDX[: a.B // 4]]
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    return {"delta": float(point), "ci95": [float(lo), float(hi)], "n_draws": len(As)}

out = {"rules": RULES, "primary_draw": a.primary_draw, "pool": a.pool, "B": a.B, "comparisons": {}}
raw, length, shuf = load("raw", a.primary_draw), load("length", a.primary_draw), load("shuffle", a.primary_draw)
full = np.arange(len(test))
sh_auc = macro(shuf, full, "L", "auroc", Y) if shuf else np.nan
out["sanity"] = {"S1_shuffle_macro_auroc": sh_auc,
                 "S1_pass": bool(RULES["S1_shuffle_auroc_band"][0] <= sh_auc <= RULES["S1_shuffle_auroc_band"][1]),
                 "length_macro_auroc": macro(length, full, "L", "auroc", Y) if length else None,
                 "raw_macro_auroc": macro(raw, full, "L", "auroc", Y), "raw_macro_f1": macro(raw, full, "L", "f1", Y)}

for rep in ("fsign", "mt5"):
    X = load(rep, a.primary_draw)
    if X is None:
        continue
    c = {}
    c["C1_macro_f1"] = paired(X, raw, "f1")
    c["C1_pass"] = c["C1_macro_f1"]["delta"] >= RULES["C1_min_delta_macro_f1"] and c["C1_macro_f1"]["ci95"][0] > 0
    c["C2_macro_auroc"] = paired(X, raw, "auroc")
    c["C2_pass"] = c["C2_macro_auroc"]["delta"] >= RULES["C2_min_delta_macro_auroc"] and c["C2_macro_auroc"]["ci95"][0] > 0
    up = [k for k, v in X["per_concept"].items() if v["tier"] == "L" and v["auroc"] > raw["per_concept"][k]["auroc"]]
    nL = sum(1 for v in X["per_concept"].values() if v["tier"] == "L")
    c["C3_concepts_auroc_up"] = f"{len(up)}/{nL}"
    c["C3_pass"] = len(up) >= RULES["C3_min_concepts_auroc_up"]
    c4 = {p: paired_avg(rep, "raw", p, "f1") for p in RULES["C4_low_data_draws"]}
    c["C4_low_data_macro_f1"] = c4
    c["C4_pass"] = all(v is not None and v["delta"] >= RULES["C4_min_delta_macro_f1"] and v["ci95"][0] > 0 for v in c4.values())
    c["C5_auroc_over_length"] = macro(X, full, "L", "auroc", Y) - (out["sanity"]["length_macro_auroc"] or 0.5)
    c["C5_pass"] = c["C5_auroc_over_length"] >= RULES["C5_min_auroc_over_length"]
    b = [(load(rep, f"testcv_r{r}"), load("raw", f"testcv_r{r}")) for r in range(3)]
    b = [(x, y) for x, y in b if x and y]
    if b:
        point = np.mean([macro(x, full, "L", "auroc", Y) - macro(y, full, "L", "auroc", Y) for x, y in b])
        boots = [np.mean([macro(x, i, "L", "auroc", Y) - macro(y, i, "L", "auroc", Y) for x, y in b]) for i in BOOT_IDX[: a.B // 4]]
        c["C6_designB_macro_auroc"] = {"delta": float(point), "ci95": [float(v) for v in np.nanpercentile(boots, [2.5, 97.5])]}
        c["C6_pass"] = bool(point > 0 and c["C6_designB_macro_auroc"]["ci95"][0] > 0)
    else:
        c["C6_pass"] = False
    c["secondary_unseen_signer_proxy10_auroc"] = paired(X, raw, "auroc", subset=(signer == "10"))
    c["secondary_tierS_macro_f1"] = paired(X, raw, "f1", tier="S")
    core = c["C1_pass"] and c["C2_pass"]
    rest = all(c[k] for k in ("C3_pass", "C4_pass", "C5_pass", "C6_pass"))
    c["verdict"] = ("STRONG SUPPORT" if core and rest and out["sanity"]["S1_pass"]
                    else "PARTIAL SUPPORT" if core else "NOT SUPPORTED")
    out["comparisons"][f"{rep}_vs_raw"] = c

fs, m5 = load("fsign", a.primary_draw), load("mt5", a.primary_draw)
if fs and m5:
    d = paired(m5, fs, "f1")
    out["layer_choice_mt5_vs_fsign"] = {"macro_f1": d, "macro_auroc": paired(m5, fs, "auroc"),
                                        "prefer": "mt5" if d["delta"] >= RULES["layer_pref_min_delta_f1"] and d["ci95"][0] > 0
                                        else "fsign (cheaper, not significantly worse)" if d["delta"] > -RULES["layer_pref_min_delta_f1"]
                                        else "fsign"}
json.dump(out, open(os.path.join(os.path.dirname(RES), "DECISION.json"), "w"), indent=1, default=float)
print(json.dumps({k: v.get("verdict") for k, v in out["comparisons"].items()}, indent=1))
print(json.dumps(out["sanity"], indent=1, default=float))
