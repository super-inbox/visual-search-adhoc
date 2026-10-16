# P0-15 result: high-precision specialist verification and fusion

**Date:** 2026-10-16 · **Verdict: NOT SUPPORTED, closed at the dev stage.** CPU only, no new Uni-Sign forward pass.
Plan: `EXPERIMENT_PLAN.md` (frozen; its sha256 is in `FREEZE.json`).

## 1. Status of the held-out final set

- **Final labels were never read.** `cells_final_nolabel.csv.gz` has no label column, and the only code that joins
  final labels (`evaluate_final.py --target final`) was never run.
- **No final metrics exist.** No final add-precision, curve, per-concept count or AUROC was computed.
- **`final/` was never created**, and neither was `final/RUN_LOCK`.
- **The verdict rests entirely on dev and the pre-registered rule.**
- **The final split is untouched and sealed for a future P0:** 73 video units, 1,157 clips, 510 Tier L positives.
  `split/final_units.txt` and `split/final_clips.txt` define it, with hashes in `split/SPLIT.sha256`.

  It is not pristine at the design level. As disclosed in plan §10, P0-14's aggregate full-test numbers already
  included these clips, and the split balance check read their reference-positive counts.

## 2. Why the verdict is already fixed on dev

Under the frozen operating-point rule (plan §6), a threshold is valid only when it adds at least 10 cells and the
Wilson 90 % lower bound of their precision is at least 0.50. **No such threshold exists on dev for C or D.**
- Both abstain in every nested out-of-fold fold and in the final fit on all dev.
- The primary arm is C (D did not beat it: net correct additions 0 vs 0), and C adds nothing.
- So it would add nothing on final whatever the final labels are.

| Criterion | Result on dev |
|---|---|
| P1: net correct additions CI lower bound > 0 | **fails** (0 additions) |
| P2: do no harm | passes trivially (nothing added) |
| P3: large enough to matter | **fails** |
| N1: 20 label permutations | all 20 abstain, for C and for D (control behaves) |
| N2: length-only verifier | abstains (control behaves) |

The dry run of the frozen evaluation code on dev (`dev/dryrun/`, in-sample, a code-path test only) returns the
same: NOT SUPPORTED.

## 3. Key dev results

Dev split:
- 75 units and 1,052 clips;
- 24,782 candidate cells (the translation omits the concept), 234 of them positive;
- the translation itself has 288 hits and 178 false mentions, so micro precision is 0.618.

| Arm (dev) | What it shows |
|---|---|
| **B**: naive union, frozen P0-14 thresholds | 331 additions, **50 correct (15 %), net −231**. Fused micro-precision −19.4 pts, micro-F1 −7.0 pts |
| **C**: mT5 margin | top 20: **7/20** correct. AP **0.094**. Best Wilson 90 % lower bound over all thresholds: **0.244** (9/23) |
| **D**: learned verifier (11 features), out-of-fold, λ = 1e-3 | top 20: **11/20** correct. AP **0.110**. Best Wilson 90 % lower bound: **0.393** (10/17) |
| D without Fsign/raw-pose features; N2 length-only | both abstain |

The best lower bound is **below 0.50 for every arm and every threshold**. C and D add 0 cells under the frozen rule,
and so do all N1 permutation configurations and N2.

Sources:
- `dev/DEV_RESULTS.json` (out-of-fold summaries, per-fold λ and τ, decision bootstrap B = 2,000);
- `FREEZE.json` (τ_C = τ_D = ∞, D at λ = 1e-3 with CV AP 0.110);
- the top-20 counts, AP and best lower bounds were recomputed from `cells_dev.csv.gz` with the frozen code in
  `scripts/common.py`.

## 4. Interpretation

- **The P0-14 finding stands:** mT5 encoder states carry concept signal that complements Uni-Sign's translation.
- **The verifier helps the ranking.** Combining the mT5 margin with probe agreement, pose margins, length and the
  concept prior ranks candidates better than the raw margin: AP 0.110 vs 0.094, and 11/20 vs 7/20 at the top.
- **The signal is not strong enough for safe high-precision fusion.** Even the verifier's best slice is about
  50–60 % correct on 17–20 cells, and its 90 % lower bound (0.39) stays below the 0.50 needed for additions to be
  more often right than wrong.
- **So P0-14's complementary signal does not yet give a usable fusion mechanism.** With these frozen signals,
  the safest system is Uni-Sign's translation alone.
- **No claim about sentence translation quality is made.** P0-15 evaluates concept-set reliability only. No sentence
  was changed, and no BLEU or chrF was computed.

## 5. What a future P0 would need

- **A stronger verification signal.** Options are decoder-side evidence (sequence or token scores, which need a new
  decode pass and a reproducibility gate) or a probe stronger than linear. It must be specified in a new frozen plan
  **before** the sealed final split is opened.
- **The sealed final split can be reused once,** under that new plan's one-shot rule. Dev (this report's 75 units)
  can be refit freely.

## 6. Reproduce (dev only, about 10 s CPU)

```bash
PY=~/Desktop/curify/gloss-free-asl-translation/.venv/bin/python   # numpy + scipy
E=docs/daily_report/10.16/asl-unisign-high-precision-fusion
$PY -I $E/scripts/build_split.py      # split/ (seed 15 passes first)
$PY -I $E/scripts/build_cells.py      # ~/Desktop/curify/p015-work/cells_{dev,final_nolabel}.csv.gz
$PY -I $E/scripts/fit_dev.py          # dev/DEV_RESULTS.json, FREEZE.json
$PY -I $E/scripts/evaluate_final.py --target dev   # dry run only. Do NOT run --target final under this plan.
```
