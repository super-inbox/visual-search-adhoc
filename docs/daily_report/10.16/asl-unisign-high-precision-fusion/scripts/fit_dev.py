"""P0-15 §5–§8: fit and calibrate C and D on DEV ONLY, decide the primary arm, freeze everything.

Reads only WORK/cells_dev.csv.gz (asserts no final clip is present). Writes dev/DEV_RESULTS.json and FREEZE.json.

Usage: python -I fit_dev.py
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (EXP, WORK, D_FEATURES, D_ABLATION_FEATURES, N2_FEATURES, LAMBDAS, MIN_ADDS, LB_TARGET, Z90,  # noqa
                    sha256, read_cells, feat, select_tau, d_procedure, score_model, model_to_json, unit_counts,
                    summarize, bootstrap_weights, ci95, jdump)

B, DEV_SEED, FINAL_SEED, N_PERM = 2000, 20261016, 20261017, 20

cells = read_cells(os.path.join(WORK, "cells_dev.csv.gz"))
final_clips = set(open(os.path.join(EXP, "split", "final_clips.txt")).read().split())
dev_clips = set(open(os.path.join(EXP, "split", "dev_clips.txt")).read().split())
assert set(cells["clip_id"]) == dev_clips and not set(cells["clip_id"]) & final_clips
fold_of_unit = json.load(open(os.path.join(EXP, "split", "dev_folds.json")))["folds"]
fold = np.array([fold_of_unit[u] for u in cells["unit"]])
Y, D = cells["Y"], cells["D"]
cand = D == 0
CONCEPTS = sorted(set(cells["concept"]), key=list(cells["concept"]).index)
assert len(CONCEPTS) == 24
unit_list = sorted(set(cells["unit"])); n_clips = len(dev_clips)
Xd, Xa, Xn = feat(cells, D_FEATURES), feat(cells, D_ABLATION_FEATURES), feat(cells, N2_FEATURES)
m = cells["mt5_margin"]


# ---------------------------------------------------------------- nested OOF on dev (§8)
def oof_C():
    A = np.zeros_like(Y); taus = []
    for f in range(5):
        tr, te = cand & (fold != f), cand & (fold == f)
        tau = select_tau(m[tr], Y[tr]); taus.append(tau)
        A[te & (m >= tau)] = 1
    return A, taus


def oof_D(X):
    A = np.zeros_like(Y); info = []
    for f in range(5):
        tr, te = cand & (fold != f), cand & (fold == f)
        r = d_procedure(X[tr], Y[tr], fold[tr])
        s = score_model(r["model"], X[te])
        idx = np.where(te)[0]
        A[idx[s >= r["tau"]]] = 1
        info.append({"lam": r["lam"], "tau": r["tau"], "cv_ap": r["cv_ap"]})
    return A, info


oof = {}
oof["C"], c_taus = oof_C()
oof["D"], d_info = oof_D(Xd)
oof["D_ablation"], abl_info = oof_D(Xa)
oof["N2"], n2_info = oof_D(Xn)
oof["B"] = (cand & (cells["mt5_p100_pred"] == 1)).astype(float)
oof["A"] = np.zeros_like(Y)
counts = {k: unit_counts(cells["unit"], cells["concept"], Y, D, v, unit_list, CONCEPTS) for k, v in oof.items()}
oof_summary = {k: summarize(c.sum(0), counts["A"].sum(0), n_clips) for k, c in counts.items()}

# ---------------------------------------------------------------- D-vs-C primary-arm rule (§8)
net_u = {k: counts[k][:, :, 3].sum(1) - counts[k][:, :, 4].sum(1) for k in ("C", "D")}     # per unit
Wb = bootstrap_weights(len(unit_list), B, DEV_SEED)
delta_boot = Wb @ (net_u["D"] - net_u["C"])
net_C, net_D = float(net_u["C"].sum()), float(net_u["D"].sum())
delta = net_D - net_C
delta_ci = ci95(delta_boot)
d_primary = bool(delta >= 0.25 * max(net_C, 0.0) and delta_ci[0] > 0)
primary = "D" if d_primary else "C"

# ---------------------------------------------------------------- frozen configurations on all dev
tau_C = select_tau(m[cand], Y[cand])
fD = d_procedure(Xd[cand], Y[cand], fold[cand])
fA = d_procedure(Xa[cand], Y[cand], fold[cand])
fN2 = d_procedure(Xn[cand], Y[cand], fold[cand])
fz_model = lambda r: {"model": model_to_json(r["model"]), "tau": r["tau"], "lam": r["lam"], "cv_ap": r["cv_ap"]}

# frozen-config in-sample additions on dev (descriptive; how many cells each frozen rule adds on dev)
def insample(Aarr):
    return summarize(unit_counts(cells["unit"], cells["concept"], Y, D, Aarr, unit_list, CONCEPTS).sum(0),
                     counts["A"].sum(0), n_clips)
ins = {"C": insample((cand & (m >= tau_C)).astype(float))}
for k, r, X in (("D", fD, Xd), ("D_ablation", fA, Xa), ("N2", fN2, Xn)):
    s = score_model(r["model"], X); ins[k] = insample((cand & (s >= r["tau"])).astype(float))

# ---------------------------------------------------------------- N1: 20 within-concept label permutations of dev
n1 = {"C": [], "D": []}
for p in range(1, N_PERM + 1):
    rng = np.random.default_rng(p)
    Yp = Y.copy()
    for c in CONCEPTS:
        idx = np.where(cells["concept"] == c)[0]
        Yp[idx] = Y[idx][rng.permutation(len(idx))]
    n1["C"].append({"perm_seed": p, "tau": select_tau(m[cand], Yp[cand])})
    r = d_procedure(Xd[cand], Yp[cand], fold[cand])
    n1["D"].append({"perm_seed": p, **fz_model(r)})

dev_results = {
    "n_dev_clips": n_clips, "n_dev_units": len(unit_list), "n_cells": int(len(Y)), "n_candidates": int(cand.sum()),
    "candidate_positives": int(Y[cand].sum()), "translation_hits": int((D * Y).sum()),
    "translation_false_mentions": int((D * (1 - Y)).sum()),
    "oof": oof_summary, "oof_fold_taus_C": c_taus, "oof_fold_D": d_info, "oof_fold_D_ablation": abl_info,
    "oof_fold_N2": n2_info,
    "decision": {"net_C": net_C, "net_D": net_D, "delta": delta, "delta_ci95": delta_ci,
                 "required_delta": 0.25 * max(net_C, 0.0), "D_primary": d_primary, "primary_arm": primary,
                 "B": B, "seed": DEV_SEED},
    "frozen_insample_on_dev": ins,
    "N1_abstentions": {"C": sum(np.isinf(x["tau"]) for x in n1["C"]), "D": sum(np.isinf(x["tau"]) for x in n1["D"])},
}
jdump(dev_results, os.path.join(EXP, "dev", "DEV_RESULTS.json"))

# ---------------------------------------------------------------- FREEZE.json
hash_paths = ["EXPERIMENT_PLAN.md", "dev/DEV_RESULTS.json", "dev/CELLS_META.json"] + \
             [f"scripts/{n}" for n in ("common.py", "build_split.py", "build_cells.py", "fit_dev.py",
                                       "evaluate_final.py")] + \
             [f"split/{n}" for n in ("dev_units.txt", "final_units.txt", "dev_clips.txt", "final_clips.txt",
                                     "dev_folds.json", "units.json", "SPLIT_LOG.json", "SPLIT.sha256")] + \
             [os.path.join(WORK, "cells_dev.csv.gz"), os.path.join(WORK, "cells_final_nolabel.csv.gz")]
cm = json.load(open(os.path.join(EXP, "dev", "CELLS_META.json")))
freeze = {
    "experiment": "P0-15", "concepts": CONCEPTS, "primary_arm": primary,
    "rule": {"min_adds": MIN_ADDS, "wilson_lb_target": LB_TARGET, "z": Z90, "lambdas": LAMBDAS},
    "features": {"D": D_FEATURES, "D_ablation": D_ABLATION_FEATURES, "N2": N2_FEATURES, "C_score": "mt5_margin"},
    "C": {"tau": tau_C},
    "D": fz_model(fD), "D_ablation": fz_model(fA), "N2": fz_model(fN2),
    "N1": n1,
    "bootstrap": {"B": B, "dev_seed": DEV_SEED, "final_seed": FINAL_SEED, "unit": "final split unit (video)"},
    "criteria": {"P1": "net_correct CI95 lower > 0", "P2": "d_micro_p CI95 lower >= -0.020 and d_macro_p point >= -0.020",
                 "P3": "tp_add >= 0.05 * final missed positives and d_micro_f1 CI95 lower > 0",
                 "N1": "median final net_correct of the primary arm's 20 permutation configs <= 0",
                 "N2": "N2 does not pass P1"},
    "p014_inputs": cm["inputs"],
    "hashes": {p: sha256(p if os.path.isabs(p) else os.path.join(EXP, p)) for p in hash_paths},
}
jdump(freeze, os.path.join(EXP, "FREEZE.json"))
print(json.dumps({"primary_arm": primary, "tau_C": tau_C, "D_lam": fD["lam"], "tau_D": fD["tau"],
                  "net_C_oof": net_C, "net_D_oof": net_D, "delta": delta, "delta_ci95": delta_ci}, default=str))
