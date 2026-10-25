"""P0-15 §9: apply the FROZEN configurations in FREEZE.json and evaluate.

  --target dev    dry run of this exact code on dev cells (in-sample, code-path test only) -> dev/dryrun/
  --target final  ONE-SHOT final evaluation -> final/. Refuses to run if any FREEZE hash differs or final/RUN_LOCK
                  exists. Writes RUN_LOCK before final labels are loaded. Primary metrics are written before any
                  descriptive curve is computed.

Usage: python -I evaluate_final.py --target {dev,final}
"""
import argparse, csv, datetime, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (EXP, P014, WORK, D_FEATURES, D_ABLATION_FEATURES, N2_FEATURES, sha256, read_cells, feat,  # noqa
                    model_from_json, score_model, unit_counts, summarize, bootstrap_weights, ci95, jdump,
                    tau_from_json, average_precision)

ap = argparse.ArgumentParser()
ap.add_argument("--target", choices=["dev", "final"], required=True)
a = ap.parse_args()

FZ_PATH = os.path.join(EXP, "FREEZE.json")
FZ = json.load(open(FZ_PATH))
bad = [p for p, h in FZ["hashes"].items() if sha256(p if os.path.isabs(p) else os.path.join(EXP, p)) != h]
assert not bad, f"FREEZE hash mismatch: {bad}"
fz_sha = sha256(FZ_PATH)

if a.target == "final":
    OUT = os.path.join(EXP, "final")
    lock = os.path.join(OUT, "RUN_LOCK")
    assert not os.path.exists(lock), "final evaluation already run (final/RUN_LOCK exists)"
    os.makedirs(OUT, exist_ok=True)
    with open(lock, "x") as f:
        f.write(json.dumps({"started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            "freeze_sha256": fz_sha}) + "\n")
    cells = read_cells(os.path.join(WORK, "cells_final_nolabel.csv.gz"))
    assert "Y" not in cells
    clips = set(open(os.path.join(EXP, "split", "final_clips.txt")).read().split())
    man = {r["clip_id"]: r for r in csv.DictReader(open(os.path.join(P014, "splits", "manifest.csv")))
           if r["clip_id"] in clips}
    cells["Y"] = np.array([int(man[c][k]) for c, k in zip(cells["clip_id"], cells["concept"])], dtype=float)
    B, SEED = FZ["bootstrap"]["B"], FZ["bootstrap"]["final_seed"]
else:
    OUT = os.path.join(EXP, "dev", "dryrun")
    cells = read_cells(os.path.join(WORK, "cells_dev.csv.gz"))
    clips = set(open(os.path.join(EXP, "split", "dev_clips.txt")).read().split())
    man = {r["clip_id"]: r for r in csv.DictReader(open(os.path.join(P014, "splits", "manifest.csv")))
           if r["clip_id"] in clips}
    B, SEED = 200, FZ["bootstrap"]["final_seed"]
assert set(cells["clip_id"]) == clips

Y, D = cells["Y"], cells["D"]
cand = D == 0
n_clips = len(clips)
unit_list = sorted(set(cells["unit"])); concept_list = FZ["concepts"]


def adds_threshold(score, tau):
    return (cand & (score >= tau)).astype(float)


def adds_model(cfg, names):
    s = score_model(model_from_json(cfg["model"]), feat(cells, names))
    return adds_threshold(s, tau_from_json(cfg["tau"])), s


arms, scores = {}, {}
arms["A"] = np.zeros_like(Y)
arms["B"] = (cand & (cells["mt5_p100_pred"] == 1)).astype(float)
arms["C"] = adds_threshold(cells["mt5_margin"], tau_from_json(FZ["C"]["tau"])); scores["C"] = cells["mt5_margin"]
arms["D"], scores["D"] = adds_model(FZ["D"], D_FEATURES)
arms["D_ablation"], _ = adds_model(FZ["D_ablation"], D_ABLATION_FEATURES)
arms["N2"], _ = adds_model(FZ["N2"], N2_FEATURES)
n1 = {"C": [adds_threshold(cells["mt5_margin"], tau_from_json(c["tau"])) for c in FZ["N1"]["C"]],
      "D": [adds_model(c, D_FEATURES)[0] for c in FZ["N1"]["D"]]}

counts = {k: unit_counts(cells["unit"], cells["concept"], Y, D, v, unit_list, concept_list) for k, v in arms.items()}
point = {k: summarize(c.sum(0), counts["A"].sum(0), n_clips) for k, c in counts.items()}
Wb = bootstrap_weights(len(unit_list), B, SEED)
clip_unit = dict(zip(cells["clip_id"], cells["unit"]))
nclip_u = np.array([sum(1 for u in clip_unit.values() if u == uu) for uu in unit_list])
KEYS = ["net_correct", "add_precision", "missed_recall", "d_micro_p", "d_micro_f1", "d_macro_p", "d_macro_f1",
        "micro_p", "micro_f1", "false_adds_per_clip"]
boot = {}
for k, c in counts.items():
    vals = {m: [] for m in KEYS}
    for w in Wb:
        cw = np.tensordot(w, c, axes=(0, 0)); bw = np.tensordot(w, counts["A"], axes=(0, 0))
        s = summarize(cw, bw, int(w @ nclip_u))
        for m in KEYS:
            vals[m].append(s[m])
    boot[k] = {m: ci95(v) for m, v in vals.items()}

n1_net = {arm: [float(summarize(unit_counts(cells["unit"], cells["concept"], Y, D, A_, unit_list,
                                             concept_list).sum(0), counts["A"].sum(0), n_clips)["net_correct"])
                for A_ in lst] for arm, lst in n1.items()}

prim = FZ["primary_arm"]
pp, pb = point[prim], boot[prim]
P1 = pb["net_correct"][0] > 0
P2 = pb["d_micro_p"][0] >= -0.020 and pp["d_macro_p"] >= -0.020
P3 = pp["tp_add"] >= 0.05 * pp["missed_positives"] and pb["d_micro_f1"][0] > 0
N1 = float(np.median(n1_net[prim])) <= 0
N2 = not (boot["N2"]["net_correct"][0] > 0)
verdict = ("VOID" if not (N1 and N2) else "SUPPORTED" if P1 and P2 and P3 else "PARTIAL" if P1 and P2
           else "NOT SUPPORTED")
primary = {
    "target": a.target, "freeze_sha256": fz_sha, "n_clips": n_clips, "n_units": len(unit_list),
    "n_cells": int(len(Y)), "n_candidates": int(cand.sum()), "B": B, "seed": SEED, "primary_arm": prim,
    "point": point, "ci95": boot, "N1_net_correct": n1_net,
    "criteria": {"P1": bool(P1), "P2": bool(P2), "P3": bool(P3), "N1": bool(N1), "N2": bool(N2)},
    "verdict": verdict,
}
jdump(primary, os.path.join(OUT, "RESULTS_PRIMARY.json"))

# ---------------------------------------------------------------- descriptive only (after primary is written)
from scipy.stats import rankdata  # noqa: E402

def auroc(y, s):
    n1_, n0 = y.sum(), len(y) - y.sum()
    r = rankdata(s)
    return float((r[y == 1].sum() - n1_ * (n1_ + 1) / 2) / (n1_ * n0)) if n1_ and n0 else float("nan")

desc = {"candidate_auroc": {}, "candidate_auprc": {}, "per_concept": {}, "by_signer": {}, "curves": {}}
for k, s in scores.items():
    desc["candidate_auroc"][k] = auroc(Y[cand], s[cand])
    desc["candidate_auprc"][k] = average_precision(Y[cand], s[cand])
ci = {c: i for i, c in enumerate(concept_list)}
for k in ("B", "C", "D"):
    desc["per_concept"][k] = {c: {"n_add": int(arms[k][cells["concept"] == c].sum()),
                                  "tp_add": int((arms[k] * Y)[cells["concept"] == c].sum()),
                                  "missed_pos": int(((1 - D) * Y)[cells["concept"] == c].sum())} for c in concept_list}
sig = np.array([man[c]["signer_proxy"] for c in cells["clip_id"]])
for k in ("C", "D"):
    desc["by_signer"][k] = {s_: {"n_add": int(arms[k][sig == s_].sum()), "tp_add": int((arms[k] * Y)[sig == s_].sum())}
                            for s_ in sorted(set(sig), key=int)}
for k, s in scores.items():
    sc, yc = s[cand], Y[cand]
    o = np.argsort(-sc, kind="mergesort"); tp = np.cumsum(yc[o]); n = np.arange(1, len(o) + 1)
    pts = [j for j in range(len(o)) if (j + 1) <= 50 or (j + 1) % 25 == 0][:400]
    desc["curves"][k] = [{"n_add": int(n[j]), "tp_add": int(tp[j]), "precision": float(tp[j] / n[j]),
                          "missed_recall": float(tp[j] / yc.sum()), "threshold": float(sc[o][j])} for j in pts]
jdump(desc, os.path.join(OUT, "RESULTS_DESCRIPTIVE.json"))
print(json.dumps({"target": a.target, "primary_arm": prim, "verdict": verdict, **primary["criteria"]}))
