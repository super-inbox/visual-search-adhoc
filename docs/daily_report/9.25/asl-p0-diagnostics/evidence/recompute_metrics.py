"""Recompute the report's text metrics from the published per-sample predictions.

Needs only Python 3 + sacrebleu (the original runs used sacrebleu 2.6.0). No model,
checkpoint, landmark or dataset is required. Run from this directory:

    python recompute_metrics.py

Each check compares a value recomputed from published predictions with the value the
original run wrote (summary.json / epoch_table.csv / metrics.json). Prints PASS/FAIL per check
and exits non-zero if any check fails.
"""
import csv
import json
import statistics
import sys
from pathlib import Path

import sacrebleu

R = Path(__file__).resolve().parent / "results"
fails = 0
n_checks = 0


def load(p):
    with open(R / p) as f:
        return json.load(f)


def bleu_chrf(refs, hyps, blank_safe=True):
    safe = [h if h.strip() else " " for h in hyps] if blank_safe else hyps
    return sacrebleu.corpus_bleu(safe, [refs]).score, sacrebleu.corpus_chrf(safe, [refs]).score


def check(name, got, want, tol):
    global fails, n_checks
    n_checks += 1
    ok = abs(got - want) <= tol
    fails += not ok
    if not ok or "-v" in sys.argv:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: recomputed={got:.4f} recorded={want:.4f}")
    return ok


# ---- P0.1: 32 training clips, final greedy predictions vs summary.json
for run in ["tiny32_e200_lr1e-4", "tiny32_e200_lr1e-4_constant", "tiny32_e200_lr1e-4_t5drop0"]:
    rows = load(f"{run}/final_predictions.json")
    refs, hyps = [r["reference"] for r in rows], [r["prediction"] for r in rows]
    b, c = bleu_chrf(refs, hyps, blank_safe=False)
    fg = load(f"{run}/summary.json")["final_generate"]
    check(f"{run} BLEU", b, fg["bleu"], 1e-6)
    check(f"{run} chrF", c, fg["chrf"], 1e-6)
    check(f"{run} exact", sum(r.strip() == h.strip() for r, h in zip(refs, hyps)), fg["exact_match"], 0)
    print(f"P0.1 {run}: BLEU {b:.2f}  chrF {c:.2f}  exact {sum(r.strip() == h.strip() for r, h in zip(refs, hyps))}/{len(rows)}")

# ---- P0.2: every epoch's val/frozen predictions vs epoch_table.csv (table is rounded to 2 dp)
for run in ["p02_10pct_e30", "p02_padfix_10pct_e30"]:
    with open(R / run / "epoch_table.csv") as f:
        table = {int(r["epoch"]): r for r in csv.DictReader(f)}
    for ep, row in sorted(table.items()):
        for split, d in (("val", "val_predictions"), ("frozen", "frozen_predictions")):
            rows = load(f"{run}/{d}/epoch_{ep:02d}.json")
            b, c = bleu_chrf([r["reference"] for r in rows], [r["prediction"] for r in rows])
            check(f"{run} ep{ep} {split} BLEU", b, float(row[f"{split}_bleu"]), 0.006)
            check(f"{run} ep{ep} {split} chrF", c, float(row[f"{split}_chrf"]), 0.006)
    best = next(r for r in table.values() if r["is_best"] == "True")
    print(f"P0.2 {run}: {len(table)} epochs checked; best epoch {best['epoch']} val_loss {best['val_loss']} "
          f"val BLEU {best['val_bleu']} frozen BLEU {best['frozen_bleu']}")

# ---- best retrained checkpoint (bs1 / bs8) and before/after-fix evaluation vs metrics.json
for d in ["p02_padfix_10pct_e30_best_eval/bs1", "p02_padfix_10pct_e30_best_eval/bs8",
          "p02_padfix_eval/before_bs1", "p02_padfix_eval/before_bs8",
          "p02_padfix_eval/after_bs1", "p02_padfix_eval/after_bs8"]:
    m = load(f"{d}/metrics.json")["sets"]
    for s in ("val366", "frozen147"):
        rows = load(f"{d}/{s}_predictions.json")
        b, c = bleu_chrf([r["reference"] for r in rows], [r["prediction"] for r in rows])
        check(f"{d} {s} BLEU", b, m[s]["bleu"], 1e-6)
        check(f"{d} {s} chrF", c, m[s]["chrf"], 1e-6)


def diff_count(a, b):
    pa = {r["sample_id"]: r["prediction"] for r in load(a)}
    pb = {r["sample_id"]: r["prediction"] for r in load(b)}
    assert pa.keys() == pb.keys()
    return sum(pa[k] != pb[k] for k in pa)


for s in ("val366", "frozen147"):
    before = diff_count(f"p02_padfix_eval/before_bs1/{s}_predictions.json", f"p02_padfix_eval/before_bs8/{s}_predictions.json")
    after = diff_count(f"p02_padfix_eval/after_bs1/{s}_predictions.json", f"p02_padfix_eval/after_bs8/{s}_predictions.json")
    best = diff_count(f"p02_padfix_10pct_e30_best_eval/bs1/{s}_predictions.json", f"p02_padfix_10pct_e30_best_eval/bs8/{s}_predictions.json")
    print(f"padding fix {s}: bs1-vs-bs8 differing predictions  old ckpt before fix {before}, after fix {after}; retrained best {best}")

# ---- input-mismatch: per-seed BLEU/chrF and per-sample loss comparisons vs summary.json
summ = load("p02_input_dependence/summary.json")["sets"]
for s in ("val366", "frozen147", "train_sample"):
    runs = {r["seed"]: r for r in summ[s]["runs"]}
    deltas = []
    for seed, rec in sorted(runs.items()):
        rows = load(f"p02_input_dependence/{s}/perm_seed{seed}.json")["rows"]
        b, c = bleu_chrf([r["reference"] for r in rows], [r["prediction_mismatched_input"] for r in rows])
        check(f"mismatch {s} seed{seed} BLEU", b, rec["bleu"], 1e-6)
        check(f"mismatch {s} seed{seed} chrF", c, rec["chrf"], 1e-6)
        lower = sum(r["tf_loss_original"] < r["tf_loss_mismatched"] for r in rows)
        check(f"mismatch {s} seed{seed} correct-video-lower-loss", lower, rec["n_correct_video_lower_loss"], 0)
        d = statistics.fmean(r["tf_loss_mismatched"] - r["tf_loss_original"] for r in rows)
        check(f"mismatch {s} seed{seed} per-sample loss delta", d, rec["per_sample_delta_mean"], 1e-6)
        deltas.append(d)
    print(f"mismatch {s}: per-sample loss increase with wrong video {min(deltas):+.3f}..{max(deltas):+.3f} over {len(runs)} shuffles")

print(f"\n{n_checks} checks, {fails} failed")
sys.exit(1 if fails else 0)
