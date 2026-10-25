"""P0-11: aggregate runs -> metrics.csv, learning_curve.csv, data/*.json, figures/*.png.
Usage (gloss-free-asl-translation .venv): python analyze_p011.py REPORT_DIR RUNS_DIR P02_RUN_DIR DIAG_DIR P013_DIR"""
import csv, json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from compare_arms import compare  # noqa: E402

rep, runs, p02, diag, p013 = map(Path, sys.argv[1:6])
(rep / "data").mkdir(exist_ok=True)
(rep / "figures").mkdir(exist_ok=True)
splits = json.load(open(rep / "splits" / "splits_summary.json"))
POOL, OFFICIAL = splits["pool_size"], splits["n_official_train"]
# p02_ref = existing P0.2 run (init e651b023, default threads); ref_sameinit = same 2,751 clips re-run with the P0-11
# launcher (OMP_NUM_THREADS=4 -> init c328ad26, identical to p25/p50/p100). See P0_11_RESULTS.md, section "Initialization".
conds = [("p02_ref", p02), ("ref_sameinit", runs / "ref_sameinit"), ("p25", runs / "p25"), ("p50", runs / "p50"), ("p100", runs / "p100")]
SUB = lambda n: splits["subsets"]["p02_ref" if n == "ref_sameinit" else n]


def table(d):
    return [dict(r) for r in csv.DictReader(open(d / "epoch_table.csv"))]


def preds(d, kind, ep):
    rows = json.load(open(d / f"{kind}_predictions" / f"epoch_{int(ep):02d}.json"))
    return {r["sample_id"]: r for r in rows}


def distinct(rows):
    toks = [r["prediction"].split() for r in rows.values()]
    return len({t for x in toks for t in x}) / max(1, sum(map(len, toks)))


out, curves, P = [], {}, {}
for name, d in conds:
    s = json.load(open(d / "summary.json"))
    t = table(d)
    curves[name] = t
    best = next(r for r in t if r["is_best"] == "True")
    ep = int(best["epoch"])
    fr, va = preds(d, "frozen", ep), preds(d, "val", ep)
    P[name] = fr
    sub = SUB(name)
    dg = diag / f"{name}_best.json"
    sh = json.load(open(dg))["sets"]["frozen147"]["shuffled_summary"]["delta_loss_mean"] if dg.exists() else None
    shv = json.load(open(dg))["sets"]["val366"]["shuffled_summary"]["delta_loss_mean"] if dg.exists() else None
    em = sum(r["prediction"].strip().lower() == r["reference"].strip().lower() for r in fr.values())
    out.append({
        "condition": name, "fraction_of_pool_pct": sub["pct_of_pool"], "fraction_of_official_train_pct": sub["pct_of_official_train"],
        "train_examples": sub["n_clips"], "train_videos": sub["n_videos"],
        "best_eval_index": ep, "evals_completed": s["epochs_completed"], "early_stopped": s["early_stopped"],
        "optimizer_steps": s["global_step"], "best_step": ep * 344,
        "data_passes_at_best": round(ep * 344 * 8 / sub["n_clips"], 2),
        "wall_time_s": s["wall_clock_total_s"],
        "train_loss_at_best": float(best["train_loss"]), "val_loss": float(best["val_loss"]),
        "val_bleu": float(best["val_bleu"]), "val_chrf": float(best["val_chrf"]), "val_wer": float(best["val_wer"]),
        "val_distinct_predictions": int(best["val_unique"].split("/")[0]),
        "frozen_loss": float(best["frozen_loss"]), "frozen_bleu": float(best["frozen_bleu"]),
        "frozen_chrf": float(best["frozen_chrf"]), "frozen_wer": float(best["frozen_wer"]),
        "distinct_predictions": int(best["frozen_unique"].split("/")[0]),
        "top_prediction_fraction": round(float(best["frozen_top1_pct"]) / 100, 4),
        "frozen_distinct1": round(distinct(fr), 4), "frozen_exact_match": em,
        "shuffle_loss_delta": None if sh is None else round(sh, 4),
        "shuffle_loss_delta_val": None if shv is None else round(shv, 4),
        "best_is_in_last_two_evals": ep >= s["epochs_completed"] - 1,
    })

with open(rep / "metrics.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)

# bootstrap: each condition vs P0.2 reference, and adjacent steps (frozen 147)
boot = {}
for a, b in [("p02_ref", "ref_sameinit"), ("ref_sameinit", "p25"), ("ref_sameinit", "p50"), ("ref_sameinit", "p100"),
             ("p02_ref", "p25"), ("p02_ref", "p50"), ("p02_ref", "p100"), ("p25", "p50"), ("p50", "p100")]:
    ids = sorted(set(P[a]) & set(P[b]))
    boot[f"{b}_minus_{a}"] = compare(ids, P[a], P[b], 10000)
json.dump(boot, open(rep / "data" / "bootstrap_frozen147.json", "w"), indent=1)

# P0-13 reference (verified from its committed files)
c13 = json.load(open(p013 / "data" / "compare_frozen_selected.json"))["all"]
p013_pt = {"train_examples": 2751, "frozen_bleu": c13["treatment"]["bleu"], "frozen_chrf": c13["treatment"]["chrf"],
           "frozen_wer": c13["treatment"]["wer"], "delta_bleu": c13["delta"]["bleu"],
           "delta_bleu_ci": c13["bootstrap95_delta"]["bleu"], "delta_chrf": c13["delta"]["chrf"],
           "delta_chrf_ci": c13["bootstrap95_delta"]["chrf"], "baseline_bleu": c13["baseline"]["bleu"]}
json.dump(p013_pt, open(rep / "data" / "p013_reference_point.json", "w"), indent=1)

with open(rep / "learning_curve.csv", "w", newline="") as f:
    cols = ["series", "condition", "train_examples", "pct_of_pool", "pct_of_official_train", "frozen_bleu", "frozen_chrf",
            "frozen_wer", "val_bleu", "best_val_loss", "shuffle_loss_delta", "note"]
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in out:
        w.writerow({"series": "supervised scaling (baseline landmarks)", "condition": r["condition"],
                    "train_examples": r["train_examples"], "pct_of_pool": r["fraction_of_pool_pct"],
                    "pct_of_official_train": r["fraction_of_official_train_pct"], "frozen_bleu": r["frozen_bleu"],
                    "frozen_chrf": r["frozen_chrf"], "frozen_wer": r["frozen_wer"], "val_bleu": r["val_bleu"],
                    "best_val_loss": r["val_loss"], "shuffle_loss_delta": r["shuffle_loss_delta"],
                    "note": {"p02_ref": "existing P0.2 run (different init)", "ref_sameinit": "2,751 re-run, same init as P0-11 runs"}.get(r["condition"], "P0-11 run")})
    w.writerow({"series": "P0-13 representation swap (reference)", "condition": "p013_unisign", "train_examples": 2751,
                "pct_of_pool": splits["subsets"]["p02_ref"]["pct_of_pool"],
                "pct_of_official_train": splits["subsets"]["p02_ref"]["pct_of_official_train"],
                "frozen_bleu": round(p013_pt["frozen_bleu"], 2), "frozen_chrf": round(p013_pt["frozen_chrf"], 2),
                "frozen_wer": round(p013_pt["frozen_wer"], 4), "val_bleu": "", "best_val_loss": "",
                "shuffle_loss_delta": 1.28, "note": "frozen only; P0-13 val is contaminated"})

# ---------------- figures
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.titlecolor": INK, "figure.facecolor": SURF, "axes.facecolor": SURF})
line = [r for r in out if r["condition"] != "p02_ref"]  # same-init series: ref_sameinit, p25, p50, p100
p02r = next(r for r in out if r["condition"] == "p02_ref")
x = [r["train_examples"] for r in line]
panels = [("frozen_bleu", "Frozen-147 BLEU", "frozen_bleu"), ("frozen_chrf", "Frozen-147 chrF", "frozen_chrf"),
          ("frozen_wer", "Frozen-147 WER (lower is better)", "frozen_wer"), ("val_bleu", "Val-366 BLEU", None),
          ("val_loss", "Best val loss", None), ("shuffle_loss_delta", "Shuffled \u2212 correct video loss (frozen)", "shuffle")]
fig, axes = plt.subplots(2, 3, figsize=(13, 7.2))
for ax, (k, title, p13k) in zip(axes.flat, panels):
    pts = [(r["train_examples"], r[k]) for r in line if r[k] is not None]
    ax.plot([a for a, _ in pts], [b for _, b in pts], color=BLUE, lw=2, marker="o", ms=8, mec=SURF, mew=2,
            label="Supervised How2Sign scaling (same init)", zorder=3)
    for xi, y in pts:
        ax.annotate(f"{y:.3f}" if k in ("shuffle_loss_delta", "val_loss") else f"{y:.2f}", (xi, y),
                    textcoords="offset points", xytext=(0, 9), ha="center", color=INK2, fontsize=8.5)
    if p02r[k] is not None:
        ax.plot([2751], [p02r[k]], ls="none", marker="o", ms=10, mfc=SURF, mec=INK2, mew=1.5, zorder=4,
                label="Existing P0.2 run (2,751, other init)")
        ax.annotate(f"{p02r[k]:.3f}" if k in ("shuffle_loss_delta", "val_loss") else f"{p02r[k]:.2f}", (2751, p02r[k]),
                    textcoords="offset points", xytext=(0, -15), ha="center", color=INK2, fontsize=8.5)
    if p13k:
        v = {"frozen_bleu": p013_pt["frozen_bleu"], "frozen_chrf": p013_pt["frozen_chrf"],
             "frozen_wer": p013_pt["frozen_wer"], "shuffle": 1.28}[p13k]
        ax.plot([2751], [v], ls="none", marker="D", ms=8, color=ORANGE, mec=SURF, mew=2, zorder=4,
                label="P0-13 Uni-Sign features (2,751)")
        ax.annotate(f"{v:.2f}", (2751, v), textcoords="offset points", xytext=(10, -3), color=INK2, fontsize=8.5)
    ax.set_xscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['train_examples']:,}\n{r['fraction_of_pool_pct']:.1f}%" for r in line], fontsize=8)
    ax.minorticks_off()
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_title(title, fontsize=10.5, loc="left")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
h, l = axes.flat[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", ncol=3, frameon=False, fontsize=9.5)
fig.supxlabel("Supervised training clips (log scale) and % of the 26,419-clip eligible pool", color=INK2, fontsize=9.5)
fig.tight_layout(rect=(0, 0.02, 1, 0.93))
fig.savefig(rep / "figures" / "learning_curve.png", dpi=150)

# training curves
CAT = ["#8a8984", "#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
for (name, _), col in zip(conds, CAT):
    t = curves[name]
    st = [int(r["epoch"]) * 344 for r in t]
    lab = f"{name} ({SUB(name)['n_clips']:,})"
    axes[0].plot(st, [float(r["train_loss"]) for r in t], color=col, lw=2, label=lab)
    axes[1].plot(st, [float(r["val_loss"]) for r in t], color=col, lw=2, label=lab)
    axes[2].plot(st, [float(r["frozen_bleu"]) for r in t], color=col, lw=2, label=lab)
    b = next(r for r in t if r["is_best"] == "True")
    axes[1].plot([int(b["epoch"]) * 344], [float(b["val_loss"])], marker="o", ms=8, color=col, mec=SURF, mew=2)
for ax, ttl in zip(axes, ["Train loss (mean per eval interval)", "Val loss (dot = selected)", "Frozen-147 BLEU (greedy)"]):
    ax.set_title(ttl, loc="left", fontsize=10.5)
    ax.set_xlabel("Optimizer step (all conditions: 10,320 max)", fontsize=9)
    ax.grid(axis="y", color=GRID, lw=0.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
axes[0].legend(frameon=False, fontsize=9)
fig.tight_layout()
fig.savefig(rep / "figures" / "training_curves.png", dpi=150)
print(json.dumps(out, indent=1))
print(json.dumps({k: {"delta": v["delta"], "ci": v["bootstrap95_delta"]} for k, v in boot.items()}, indent=1))
