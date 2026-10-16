"""P0-14: decoder baseline D + fusion-readiness analysis (descriptive; NOT part of the pre-registered C1-C6 decision).

D (Uni-Sign translation concept presence): a concept is "present" for a clip if Uni-Sign's own beam-4 translation
contains it, using EXACTLY the frozen matcher that produced the reference labels (build_concepts.py tokens/lemmas,
concept_list_v1.csv forms; nothing re-tuned). D is binary, so its AUROC is the single-point (TPR + TNR) / 2.

Fusion readiness, on test_clean, per (clip, concept) with a positive reference label:
  missed      = Uni-Sign's translation does NOT contain the concept (D = 0)
  recovered   = the specialist probe fires on it (score >= its frozen OOF-F1 threshold from probe-train)
  recovery    = recovered / missed                        (how much of what Uni-Sign misses the probe gets)
  false alarm = probe fires on a (clip, concept) whose reference is negative AND D = 0 (the cost of adding the head)
  AUROC | D=0 = probe AUROC restricted to clips where the translation omits the concept (threshold-free: does the
                probe rank the missed positives above the true negatives that Uni-Sign also left out?)
  OR-fusion   = predict present if D = 1 OR probe fires; macro P/R/F1 vs D alone (the simplest possible late fusion)
Uncertainty: the same paired video-cluster bootstrap over the 149 test videos as analyze_probe.py (seed 20261015).

Usage: python -I analyze_fusion_readiness.py --probe-dir . --predictions decode/predictions.jsonl --results results/lr \
           --csvs TRAIN VAL TEST --out results/fusion_readiness.json [--B 2000]
"""
import argparse, csv, json, os, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--probe-dir", required=True)
ap.add_argument("--predictions", required=True)
ap.add_argument("--results", required=True)
ap.add_argument("--csvs", nargs=3, required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--pool", default="ms")
ap.add_argument("--B", type=int, default=2000)
a = ap.parse_args()
D_ = a.probe_dir

# ---- the frozen matcher (top half of build_concepts.py, executed as-is, like validate_features.py does)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_concepts.py")).read()
src = src.split("# ---------------------------------------------------------------- per-clip annotations")[0]
g = {"__name__": "bc"}; argv = sys.argv; sys.argv = ["bc", *a.csvs, D_]
exec(compile(src, "build_concepts.py", "exec"), g); sys.argv = argv
concept_rows = list(csv.DictReader(open(os.path.join(D_, "concepts", "concept_list_v1.csv"))))
CON = [c["concept"] for c in concept_rows]
TIER = {c["concept"]: c["tier"] for c in concept_rows}

def present(sent):
    lem, tok = g["lemmas"](sent), set(g["tokens"](sent))
    return [int((c["concept"].lower() in lem) if c["match"] == "lemma" else bool(tok & set(c["forms"].split())))
            for c in concept_rows]

man = [r for r in csv.DictReader(open(os.path.join(D_, "splits", "manifest.csv"))) if r["role"] == "test_clean"]
ids = [r["clip_id"] for r in man]
Y = np.array([[int(r[c]) for c in CON] for r in man])
preds = {}
for l in open(a.predictions):
    p = json.loads(l)
    assert p["clip_id"] not in preds, "duplicate prediction " + p["clip_id"]
    preds[p["clip_id"]] = p["pred"]
assert set(preds) == set(ids), (len(preds), len(ids))
Dm = np.array([present(preds[c]) for c in ids])

# sanity: the matcher applied to the REFERENCES reproduces the frozen manifest labels exactly
ref = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in g["splits"]["test"]}
Yre = np.array([present(ref[c]) for c in ids])
assert (Yre == Y).all(), "matcher does not reproduce manifest labels"

vid = np.array([r["group"] for r in man]); uv, vinv = np.unique(vid, return_inverse=True)
members = [np.where(vinv == i)[0] for i in range(len(uv))]
rng = np.random.default_rng(20261015)
BOOT = [np.concatenate([members[i] for i in rng.integers(0, len(uv), len(uv))]) for _ in range(a.B)]
LIDX = [k for k, c in enumerate(CON) if TIER[c] == "L"]
SIDX = [k for k, c in enumerate(CON) if TIER[c] == "S"]

def prf(y, p):
    tp = (y * p).sum(); fp = ((1 - y) * p).sum(); fn = (y * (1 - p)).sum()
    P = tp / (tp + fp) if tp + fp else 0.0; R = tp / (tp + fn) if tp + fn else 0.0
    return P, R, (2 * P * R / (P + R) if P + R else 0.0)

def auroc(y, s):
    n1 = y.sum(); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return np.nan
    from scipy.stats import rankdata  # noqa: E402 (average ranks for ties: D is binary)
    r = rankdata(s)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def macro_prf(Yy, P, idx, ks):
    v = np.array([prf(Yy[idx, k], P[idx, k]) for k in ks])
    return v.mean(0)

def load(rep, draw):
    f = os.path.join(a.results, f"{rep}_{a.pool}_{draw}.json")
    if not os.path.exists(f):
        return None
    r = json.load(open(f))
    return np.asarray(r["test_scores"], np.float32), np.asarray(r["test_pred"], np.uint8)

ALL = np.arange(len(ids))
out = {"n_test": len(ids), "n_videos": len(uv), "B": a.B, "pool": a.pool,
       "decoder": {"source": os.path.abspath(a.predictions)}}

# ---- D on its own
dper = {}
for k, c in enumerate(CON):
    P, R, F = prf(Y[:, k], Dm[:, k])
    dper[c] = {"tier": TIER[c], "n_pos": int(Y[:, k].sum()), "n_pred": int(Dm[:, k].sum()), "precision": P, "recall": R,
               "f1": F, "auroc_binary": auroc(Y[:, k], Dm[:, k].astype(float)),
               "n_missed": int(((Y[:, k] == 1) & (Dm[:, k] == 0)).sum())}
def mac(per, key, tier):
    return float(np.nanmean([v[key] for v in per.values() if v["tier"] == tier]))
out["D_translation"] = {"per_concept": dper,
                        "macro": {t: {k: mac(dper, k, t) for k in ("precision", "recall", "f1", "auroc_binary")}
                                  for t in ("L", "S")},
                        "n_missed_L": int(sum(dper[c]["n_missed"] for c in CON if TIER[c] == "L")),
                        "n_pos_L": int(sum(dper[c]["n_pos"] for c in CON if TIER[c] == "L"))}

def readiness(S, Pp, ks, idx=ALL):
    """Pooled over (clip, concept) cells of the given concepts, plus macro over concepts."""
    y, d, p = Y[idx][:, ks], Dm[idx][:, ks], Pp[idx][:, ks]
    missed = (y == 1) & (d == 0)
    neg_d0 = (y == 0) & (d == 0)
    rec_c = [p[missed[:, j], j].mean() if missed[:, j].any() else np.nan for j in range(len(ks))]
    fa_c = [p[neg_d0[:, j], j].mean() for j in range(len(ks))]
    au_c = [auroc(y[d[:, j] == 0, j], S[idx][:, ks][d[:, j] == 0, j]) for j in range(len(ks))]
    orf = np.maximum(d, p)
    f_or = np.mean([prf(y[:, j], orf[:, j])[2] for j in range(len(ks))])
    f_d = np.mean([prf(y[:, j], d[:, j])[2] for j in range(len(ks))])
    return {"n_missed": int(missed.sum()), "n_recovered": int((p * missed).sum()),
            "recovery_pooled": float((p * missed).sum() / max(missed.sum(), 1)),
            "recovery_macro": float(np.nanmean(rec_c)),
            "false_alarm_rate_on_D0_negatives_pooled": float((p * neg_d0).sum() / max(neg_d0.sum(), 1)),
            "false_alarm_macro": float(np.mean(fa_c)),
            "excess_recovery_over_false_alarm_macro": float(np.nanmean(np.array(rec_c) - np.array(fa_c))),
            "auroc_given_D0_macro": float(np.nanmean(au_c)),
            "or_fusion_macro_f1": float(f_or), "D_alone_macro_f1": float(f_d), "or_fusion_delta_f1": float(f_or - f_d),
            "_per_concept": {"recovery": rec_c, "false_alarm": fa_c, "auroc_given_D0": au_c}}

def ci(vals):
    lo, hi = np.nanpercentile(vals, [2.5, 97.5]); return [float(lo), float(hi)]

KEYS = ("recovery_macro", "excess_recovery_over_false_alarm_macro", "auroc_given_D0_macro", "or_fusion_delta_f1")
draw_sets = {"p10": [f"p10_d{i}" for i in range(5)], "p25": [f"p25_d{i}" for i in range(5)],
             "p50": [f"p50_d{i}" for i in range(3)], "p100": ["p100_d0"]}
out["readiness"] = {}
for frac, dlist in draw_sets.items():
    out["readiness"][frac] = {}
    loaded = {rep: [x for x in (load(rep, d) for d in dlist) if x is not None] for rep in ("raw", "fsign", "mt5", "length")}
    for tier, ks in (("L", LIDX), ("S", SIDX)):
        res_t = {}
        for rep, lst in loaded.items():
            if not lst:
                continue
            per_draw = [readiness(S, P, ks) for S, P in lst]
            r = {k: float(np.mean([x[k] for x in per_draw])) for k in per_draw[0] if not k.startswith("_")}
            r["n_draws"] = len(lst)
            if tier == "L":
                r["per_concept"] = {CON[ks[j]]: {m: float(np.nanmean([x["_per_concept"][m][j] for x in per_draw]))
                                                 for m in ("recovery", "false_alarm", "auroc_given_D0")}
                                    for j in range(len(ks))}
            nb = a.B if frac == "p100" else a.B // 4  # as analyze_probe.py: fewer resamples for multi-draw averages
            boots = {k: [] for k in KEYS}
            for b in BOOT[:nb]:
                rb = [readiness(S, P, ks, b) for S, P in lst]
                for k in KEYS:
                    boots[k].append(np.mean([x[k] for x in rb]))
            r["ci95"] = {k: ci(v) for k, v in boots.items()}
            r["_boot"] = boots
            res_t[rep] = r
        for rep in ("fsign", "mt5"):  # paired specialist-vs-raw differences, same resamples
            if rep in res_t and "raw" in res_t:
                res_t[rep]["vs_raw"] = {k: {"delta": res_t[rep][k] - res_t["raw"][k],
                                            "ci95": ci(np.array(res_t[rep]["_boot"][k]) - np.array(res_t["raw"]["_boot"][k]))}
                                        for k in KEYS}
        if "fsign" in res_t and "mt5" in res_t:
            res_t["mt5"]["vs_fsign"] = {k: {"delta": res_t["mt5"][k] - res_t["fsign"][k],
                                            "ci95": ci(np.array(res_t["mt5"]["_boot"][k]) - np.array(res_t["fsign"]["_boot"][k]))}
                                        for k in KEYS}
        for r in res_t.values():
            r.pop("_boot", None)
        out["readiness"][frac][tier] = res_t

# D bootstrap CI on its macro F1 (Tier L)
dfb = [macro_prf(Y, Dm, b, LIDX)[2] for b in BOOT]
out["D_translation"]["macro_L_f1_ci95"] = ci(dfb)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
json.dump(out, open(a.out, "w"), indent=1, default=float)
m = out["D_translation"]["macro"]["L"]
print(f"D translation Tier L: P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} AUROC(bin)={m['auroc_binary']:.3f}"
      f"  missed {out['D_translation']['n_missed_L']}/{out['D_translation']['n_pos_L']}")
for frac in draw_sets:
    for rep, r in out["readiness"][frac].get("L", {}).items():
        print(f"{frac:4s} {rep:6s} recovery={r['recovery_macro']:.3f} FA={r['false_alarm_macro']:.3f} "
              f"AUROC|D0={r['auroc_given_D0_macro']:.3f} OR-fusion dF1={r['or_fusion_delta_f1']:+.3f} "
              f"CI{[round(x, 3) for x in r['ci95']['or_fusion_delta_f1']]}")
