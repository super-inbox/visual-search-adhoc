# P0-11: supervised-data scaling, results (with same-init control)

Date: 2026-10-11. Plan and decision rules: `P0_11_PLAN.md` (written before any result). Splits: `DATASET_SPLITS.md`.
This file adds the **same-initialization 2,751-clip control** (`ref_sameinit`) to the p25 / p50 / p100 runs
completed on 2026-10-08/09. The p25 / p50 / p100 and P0.2 reference results are unchanged: the regenerated
`metrics.csv` rows, bootstrap entries and diagnostics files for them are byte-identical to the committed versions.

## Status: COMPLETE

The question P0-11 asks ("does more supervised How2Sign data improve the current baseline?") is now answered with
initialization controlled. The caveats in §7 (single seed per condition, compute-matched budget) qualify the
answer; they do not leave it open.

## 1. Initialization

| Run | Train clips | Launcher threads | Init `state_dict` sha256 |
|---|---|---|---|
| P0.2 reference (`p02_ref`, existing run) | 2,751 | default (6 intra-op on this Mac) | `e651b0232eeb…` |
| p25 / p50 / p100 | 6,605 / 13,210 / 26,419 | `OMP_NUM_THREADS=4` (`scripts/run_p011.sh`) | `c328ad26f450…` |
| **`ref_sameinit` (this control)** | **2,751** | **`OMP_NUM_THREADS=4`** | **`c328ad26f450…`** |

All runs call `set_seed(42)` before model construction. PyTorch's CPU initialization depends on the intra-op thread
count, so the P0.2 reference and the P0-11 runs started from different weights. This was re-verified on
2026-10-11 by hashing a fresh model under both settings (`e651b023…` default threads, `c328ad26…` with
`OMP_NUM_THREADS=4`).

## 2. The control run

| Item | Value |
|---|---|
| Train IDs | `splits/train_p02_ref.txt`: the exact 2,751 P0.2 clips, 1,208 videos, sha256 `900929628d3e…` |
| Val / frozen | 366 / 147, the same files as every other condition |
| Code and arguments | `scripts/train_p011.py`, same arguments as `run_p011.sh` except `--train-ids` and `--output-dir`. `run_config.json` differs from p25's only in train IDs, train count, steps/epoch, data passes and paths |
| Recipe | Conformer + MLP bridge + t5-small decoder, Adafactor lr 1e-4 (T5 0.1×), wd 0.01, linear schedule, warmup 0.1 of 10,320 steps, batch 8, grad-accum 1, max_grad_norm 1.0, gradient checkpointing, 1 dataloader worker, train augmentation on, t5-small tokenizer (max target 30), greedy max_length 30 |
| Budget / selection | max 10,320 steps, eval + checkpoint every 344 steps, best val loss, early-stopping patience 10 evals |
| Device | Apple M3 Pro, **CPU** (`use_cpu=True`; MPS available but not used, as in all P0-11 runs). torch 2.10.0, transformers 4.57.6, Python 3.12.4. `OMP_NUM_THREADS=4` → 4 intra-op / 12 inter-op threads |
| Execution | run alone, under `caffeinate -ims`, 2026-10-11 15:56 → 18:03 (the p25/p50/p100 runs had run three-concurrently) |
| Previous attempt | `ref_omp4` (2026-10-09) died at step 1,032. It was **not resumed**: an HF-Trainer resume does not replay the augmentation / dataloader-worker RNG stream exactly. Restarted from scratch instead. The restart reproduces `ref_omp4` **bit-for-bit** on all 1,032 overlapping steps (loss and grad-norm), on evals 1–2 (val 5.5670 / 4.9533, frozen 5.6445 / 4.9845) and on the epoch-2 frozen predictions. `ref_omp4` was left untouched |

**Outcome.** Early stopping fired at eval 27 (step 9,288 of 10,320). The best val loss was at eval 17 (step 5,848,
about 17 passes over the data), then val and frozen loss drifted up while train loss kept falling (3.66 → 3.46).
This is the planned protocol, not a failure. The P0.2 reference ran all 30 evals with its best at eval 20. Wall time
was 7,584 s (2.1 h).

Run files: `data/runs/ref_sameinit/` (`run_config.json`, `summary.json`, `epoch_log.jsonl`, `epoch_table.csv`,
best-epoch val/frozen predictions). Diagnostics: `data/diagnostics/ref_sameinit_best.json`.

## 3. Controlled learning curve (frozen-147, val-selected checkpoint)

Same initialization, recipe and budget in every row; only the number of distinct training clips changes.

| Condition | Train clips | Best eval / step | Best val loss | Frozen loss | BLEU | chrF | WER | Distinct /147 | Top-1 share | Shuffled Δloss (frozen) |
|---|---|---|---|---|---|---|---|---|---|---|
| **ref_sameinit** | 2,751 | 17 / 5,848 (early-stopped at 27) | 3.6418 | 3.7146 | **0.80** | **10.60** | **1.056** | **63** | 30.6 % | **0.048** |
| p25 | 6,605 | 29 / 9,976 | 3.5908 | 3.6676 | 1.15 | 12.37 | 1.005 | 73 | 8.8 % | 0.073 |
| p50 | 13,210 | 30 / 10,320 | 3.5866 | 3.6650 | 0.54 | 12.25 | 1.047 | 35 | 36.7 % | 0.066 |
| p100 | 26,419 | 30 / 10,320 | 3.5760 | 3.6534 | 0.52 | 9.51 | 1.056 | 29 | 20.4 % | 0.061 |
| *P0.2 reference (other init)* | *2,751* | *20 / 6,880* | *3.6415* | *3.7224* | *1.02* | *11.12* | *1.025* | *102* | *6.8 %* | *0.067* |

Paired bootstrap vs the same-init control (10k resamples, frozen-147; `data/bootstrap_frozen147.json`):

| Comparison | ΔBLEU [95 % CI] | ΔchrF [95 % CI] | ΔWER |
|---|---|---|---|
| p25 − ref_sameinit | +0.36 [−0.28, +1.01] | **+1.78 [+0.96, +2.61]** | −0.051 |
| p50 − ref_sameinit | −0.26 [−0.71, +0.28] | **+1.66 [+1.07, +2.29]** | −0.009 |
| p100 − ref_sameinit | −0.28 [−0.71, +0.21] | **−1.08 [−1.74, −0.45]** | 0.000 |
| p50 − p25 | −0.61 [−1.24, +0.09] | −0.12 [−0.85, +0.61] | +0.042 |
| p100 − p50 | −0.02 [−0.44, +0.36] | **−2.74 [−3.35, −2.16]** | +0.009 |
| *Init effect: ref_sameinit − p02_ref (same data)* | *−0.22 [−0.86, +0.42]* | *−0.53 [−1.45, +0.39]* | *+0.031* |

Representation diagnostics at the best checkpoint (`data/diagnostics_summary.csv`, frozen-147):

| Condition | Encoder participation ratio (effective dims) | Encoder PC1 share | Shuffled Δloss frozen / val |
|---|---|---|---|
| ref_sameinit | 3.84 | 0.48 | 0.048 / 0.077 |
| p25 | 3.86 | 0.46 | 0.073 / 0.100 |
| p50 | 2.38 | 0.62 | 0.066 / 0.090 |
| p100 | 2.34 | 0.63 | 0.061 / 0.084 |
| *p02_ref (other init)* | *7.72* | *0.28* | *0.067 / 0.095* |

Figures: `figures/learning_curve.png` (same-init line plus the P0.2 point and P0-13 marker) and
`figures/training_curves.png` (all five runs).

## 4. Pre-registered decision rules, applied with the same-init control as reference

| Rule | Check | Met? |
|---|---|---|
| A: flat | p100 − ref: \|ΔBLEU\| = 0.28 < 0.5 ✓; ΔchrF CI includes 0 ✗ (it is significantly **negative**) | no, narrowly |
| B: steady material rise | p100 − ref ΔBLEU ≥ +1.0 | no |
| C: rise then plateau | p25 − ref ΔchrF CI excludes 0 ✓; p100 − p50 ΔBLEU < 0.3 ✓ | literally yes |
| D: fits more, generalizes no better | val loss 3.642 → 3.591 → 3.587 → 3.576 and frozen loss fall monotonically; frozen BLEU never moves significantly; chrF rises then falls below the start | in spirit yes |

The verdict is the same as with the P0.2 reference: **loss improves with data, translation does not show a
sustained gain.** On BLEU the curve is flat within noise (no BLEU difference between any pair is significant). On
chrF it rises by about 1.7 points at 2.4–4.8× data and then falls below the start at 9.6×.

**Learning-curve shape: plateau / non-monotonic.** There is no rising trend at the largest size.

## 5. Did the initialization mismatch matter?

**It did not change the conclusion, but it changed some of the magnitudes previously reported.**

- **Unchanged.** More supervised How2Sign data gives no material, sustained translation gain with this model and
  recipe, and the best gain is far below P0-13's. This now holds at matched initialization.
- **Revised: BLEU decline.** Against the same-init control, p50/p100 BLEU is −0.26 / −0.28 with CIs including 0.
  The earlier "BLEU roughly halves" (−0.48 / −0.51 vs `p02_ref`) was partly the reference run's favorable
  initialization. The same-init BLEU curve is flat, not falling.
- **Revised: chrF gain.** The chrF gain at p25/p50 is slightly larger against the same-init control (+1.7 to +1.8,
  vs +1.1 to +1.3). The p100 chrF drop is smaller (−1.1 vs −1.6) but still significant.
- **Revised: collapse with data.** It is smaller than reported:
  - Distinct predictions go 63 → 73 → 35 → 29, not 102 → 29.
  - Encoder effective dimensions go 3.8 → 3.9 → 2.4 → 2.3, not 7.7 → 2.3.
  - Collapse still grows from p25 to p50/p100, but the first step (2,751 → 6,605) shows none.
- **Revised: video reliance.** The shuffled-video gap is 0.048 at 2,751 same-init and 0.061–0.073 at larger sizes.
  That is a small increase, still about 20× below P0-13's 1.28.
- **Initialization alone is a sizeable source of variance.** Same data, different init gave BLEU 1.02 vs 0.80,
  chrF 11.12 vs 10.60, and distinct predictions 102 vs 63. That is comparable to the BLEU differences between
  data sizes, so the exact shape of the BLEU curve (for example, the p25 peak) should not be read as real.

Of the user-specified outcomes, this is **A: same-init 2,751 is close to p25/p50/p100.** It is within ±0.36 BLEU
everywhere, and p25/p50 are better only on chrF. That **strengthens** the P0-11 conclusion, with the noise caveat
above.

## 6. Comparison with P0-13 (representation swap at the same 2,751 clips)

| Lever | Train clips | Frozen BLEU | chrF | WER | ΔBLEU vs its 2,751 baseline [CI] | ΔchrF [CI] |
|---|---|---|---|---|---|---|
| Best supervised scaling (p25 vs same-init) | 6,605 (2.4×) | 1.15 | 12.37 | 1.005 | +0.36 [−0.28, +1.01] | +1.78 [+0.96, +2.61] |
| Largest supervised scaling (p100 vs same-init) | 26,419 (9.6×) | 0.52 | 9.51 | 1.056 | −0.28 [−0.71, +0.21] | −1.08 [−1.74, −0.45] |
| **Pretrained representation (P0-13 vs P0.2)** | **2,751 (1×)** | **3.25** | **17.05** | **0.939** | **+2.23 [+1.28, +3.39]** | **+5.93 [+4.66, +7.34]** |

- **The benefit from supervised-data scaling is much smaller than from the pretrained representation.**
  - The best data-scaling BLEU CI lies entirely below the P0-13 BLEU CI (upper bound 1.01 < 1.28).
  - The best chrF gain is about 30 % of P0-13's.
  - At 9.6× data, both BLEU and chrF are at or below the start.
- The P0-13 delta is measured against `p02_ref`, which has a different init from the P0-11 runs. Here the
  measured init effect is −0.22 BLEU / −0.53 chrF, an order of magnitude below the P0-13 effect, so this does not
  change the comparison.
- **This is not "data does not matter."**
  - Adding more *same-domain supervised How2Sign sentence pairs* to the current landmark model does not buy
    translation quality.
  - The representation that does help was itself learned from *broad sign-language pretraining*: YouTube-ASL plus
    How2Sign, through Uni-Sign's stages.
  - The data lever that works is **pretraining data that shapes the representation**, not more labels for the
    current one.

## 7. Caveats

- **One seed per condition.** Bootstrap CIs cover test-sample noise only. §5 shows init alone moves BLEU by about
  0.2 and distinct predictions by about 40. A multi-seed matrix (≥ 3 seeds per size) would be needed to pin down
  the curve's shape. It is not needed for the main conclusion: the gap to P0-13 is about 10× the observed init
  effect.
- **Checkpoint-to-checkpoint noise.** From eval 15 onward, frozen BLEU fluctuates between evaluations by about
  0.6–0.9 within every run (ref_sameinit 0.43–1.34, p25 0.43–1.15, p50 0.38–0.98, p100 0.31–1.05, p02_ref 0.74–1.21;
  `data/runs/*/epoch_table.csv`). The selected point is chosen by val loss, not frozen BLEU, so it is unbiased, but
  BLEU differences under about 0.5 between conditions are not meaningful.
- **Compute-matched budget.** p25/p50/p100 selected their best checkpoint at their last evaluations, so their
  points are lower bounds. The 2,751 control early-stopped at about 27 passes. A longer p100 run remains optional.
- **Val text overlap** grows with subset size (6 → 90 clips). Frozen-147 is the primary endpoint for that reason.
- **Scope.** This is *supervised How2Sign scaling for this landmark model and recipe*. It does not test broad
  sign-language pretraining data.

## 8. Reproduction

Paths: `$WORK` = the P0-11 working directory (temporary Claude session scratchpad holding `landmarks/frontal`,
`full_train_metadata.csv`, `runs/`, `diag/`); `$N` = `~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/landmark_t5_1pct`;
`$D` = this directory. Run from `~/Desktop/curify/gloss-free-asl-translation` with its `.venv`.

```bash
# training (same arguments as run_p011.sh, 2,751 P0.2 IDs)
caffeinate -ims env OMP_NUM_THREADS=4 PYTHONPATH=. .venv/bin/python $D/scripts/train_p011.py \
  --stage-dir $WORK/landmarks/frontal --metadata $WORK/full_train_metadata.csv \
  --split-json $N/local_run_10pct/work/holdout_split.json --raw-dir $N/local_run_10pct/raw_download \
  --frozen-landmarks $N/frozen_benchmark_mediapipe_eval/landmarks \
  --frozen-metadata $N/frozen_benchmark_mediapipe_eval/frozen_benchmark_metadata.csv \
  --frozen-denylist $N/frozen_denylist.json \
  --how2sign-v2-manifest ~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv \
  --train-ids $D/splits/train_p02_ref.txt --max-steps 10320 --patience 10 --output-dir $WORK/runs/ref_sameinit

# diagnostics on the best checkpoint (5 shuffled-video derangements + collapse statistics)
OMP_NUM_THREADS=4 PYTHONPATH=. .venv/bin/python $D/scripts/diagnose_p011.py --arm baseline \
  --checkpoint $WORK/runs/ref_sameinit/checkpoints/checkpoint-5848 --ids-dir $WORK/runs/ref_sameinit/ids \
  --metadata $WORK/full_train_metadata.csv --frozen-metadata $N/frozen_benchmark_mediapipe_eval/frozen_benchmark_metadata.csv \
  --stage-dir $WORK/landmarks/frontal --frozen-landmarks $N/frozen_benchmark_mediapipe_eval/landmarks \
  --seeds 5 --out $WORK/diag/ref_sameinit_best.json

# aggregation (metrics.csv, learning_curve.csv, bootstrap, figures)
.venv/bin/python $D/scripts/analyze_p011.py $D $WORK/runs results/p02_padfix_10pct_e30 $WORK/diag \
  ~/Desktop/visual-search-adhoc/docs/daily_report/10.07/asl-p0-13-representation-swap
```

`analyze_p011.py` was changed only to label the control `ref_sameinit` (it previously expected `ref_omp4`).
`diagnostics_summary.csv` rows are computed from `data/diagnostics/*_best.json`. The formula was checked against
the committed p02_ref/p25/p50/p100 rows.
