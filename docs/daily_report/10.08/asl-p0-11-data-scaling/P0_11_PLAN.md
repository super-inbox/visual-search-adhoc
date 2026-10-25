# P0-11: supervised-data scaling, plan

Date: 2026-10-08 · Written before any P0-11 training result. Scope: P0-11 only. P0-12 and P0-13 are not modified,
no Uni-Sign features or decoders are used, and nothing is committed.

## Research question

The manager asked: *"Do we mainly lack labeled data, or do we lack a representation that maps ASL motion to
semantics?"* P0-13 varied the representation at fixed data. **P0-11 varies only the amount of supervised How2Sign
training data, with the current baseline representation and model held fixed.**

1. Does the P0.2 baseline improve as the supervised How2Sign data grows?
2. Is the learning curve still rising strongly at the largest size?
3. Does more labeled How2Sign data fix the poor generalization on the frozen test set?
4. How does the effect compare with P0-13's representation swap (frozen BLEU 1.02 → 3.25)?

## Hypothesis

H0 (prior, from external literature and the P0-13 result): within this model and recipe, roughly 10× more How2Sign
supervision moves frozen-test quality only slightly. That is a flat or plateauing curve, with an effect much smaller
than the representation swap. **This experiment can reject H0.**

## Conditions (exact counts: `DATASET_SPLITS.md`)

| Condition | Train clips | Videos | % of eligible pool (26,419) | % of official train (31,165) |
|---|---|---|---|---|
| P0.2 reference (existing run, **not** retrained) | 2,751 | 1,208 | 10.41 % | 8.83 % |
| p25 | 6,605 | 1,667 | 25.00 % | 21.19 % |
| p50 | 13,210 | 1,804 | 50.00 % | 42.39 % |
| p100 | 26,419 | 1,826 | 100.00 % | 84.77 % |

- The subsets are nested: 2,751 ⊂ p25 ⊂ p50 ⊂ p100. They are prefixes of one deterministic order (the P0.2 train
  clips first, then the rest of the pool shuffled with seed 20261008).
- **The pool is not all of How2Sign train.** It excludes 118 clips without landmark files, 2 clips whose text equals
  a frozen-test sentence (P0.2's rule), the 366 val clips, and **4,260 other clips from the 366 val videos**. The
  last group keeps validation video-disjoint, as in P0.2.
- Val (366) and frozen test (147) are unchanged.

## Controls (identical across conditions)

Data pipeline, model, optimizer, schedule, generation and metrics are all P0.2's, via
`scripts/train_p011.py`, a copy of `train_p02.py` with a 63-line diff:

- **Input:** MediaPipe Holistic landmarks (Kaggle "How2Sign Holistic", same archive as P0.2), 501-d, `max_len` 150
  with stride subsampling, face included, normalization and train-time augmentation unchanged.
- **Model:** 4-block Conformer (d 512, 4 heads, kernel 31, stride-2) + MLP bridge + HF `t5-small` decoder (encoder
  deleted), T5 dropout 0.1. Fresh init with `set_seed(42)`. The init hash equals P0.2's (`e651b023…`).
- **Optimizer:** Adafactor with 4 parameter groups (T5 at 0.1× lr), lr 1e-4, wd 0.01, linear schedule, warmup 0.1,
  batch 8, grad-accum 1, max_grad_norm 1.0, CPU.
- **Tokenizer:** t5-small, max target 30.
- **Generation:** greedy, max_length 30.
- **Metrics:** sacrebleu BLEU and chrF, jiwer WER on full references (`score()` from P0.2), unique predictions, top-1
  share.
- **Selection:** best val loss, early-stopping patience 10 evaluations.

## Training-budget choice: compute-matched (fixed optimizer steps)

| Option | What grows with data | Cost here | Verdict |
|---|---|---|---|
| Fixed epochs (P0.2's 30) | steps grow 2.4× / 4.8× / 9.6× | about 5 h / 9 h / 17 h (about 31 h) | confounds data with compute; not run |
| **Fixed optimizer steps = 10,320** (P0.2's total) | only the **number of distinct examples** | about 2.4 h each, concurrent | **chosen** |
| Fixed examples seen | same as fixed steps at a fixed batch size | — | identical to the above |

- Every condition gets exactly P0.2's budget: 10,320 steps × batch 8 = 82,560 examples seen, the same warmup (1,032
  steps) and linear decay, evaluation and checkpointing every 344 steps (one P0.2 epoch), and early-stopping patience
  of 10 evaluations.
- **The existing P0.2 run is therefore the 2,751-clip condition of this design,** with no adjustment needed.
- What changes is only how often each example repeats: about 30 passes at 2,751, 12.5 at p25, 6.2 at p50 and 3.1 at
  p100. This isolates "more distinct supervised examples" from "more compute".
- **Known risk:** at p100 the model sees each clip only about 3 times and might be under-trained. Pre-registered rule:
  if a run's best val loss is at one of its last two evaluations, its point is reported as a **lower bound**
  (still improving), and a longer run would be the follow-up. Fixed-epoch view A is not run (about 31 h).

## Measurements

- **Per evaluation:** train loss, val loss, val BLEU/chrF/WER/unique/top-1, frozen-147 loss/BLEU/chrF/WER/unique/top-1
  (the P0.2 callback).
- **Per run:** best evaluation, early-stop point, optimizer steps, wall time.
- **Best checkpoint per run:** correct vs shuffled video (5 derangements, same definition as P0-13), and collapse
  statistics, using a copy of P0-13's `diagnose_p013.py`. The P0.2 reference already has these from P0-13.
- **Paired bootstrap:** 10k resamples of frozen-147 corpus BLEU/chrF, for each condition minus the P0.2 reference
  and p100 minus p50.

## Decision rules (fixed in advance; frozen-147 at the val-selected checkpoint)

| Outcome | Rule |
|---|---|
| **A: flat** | p100 − ref: \|ΔBLEU\| < 0.5 **and** the ΔchrF 95 % CI includes 0 |
| **B: steady, material rise** | p100 − ref: ΔBLEU ≥ +1.0 with the ΔchrF CI excluding 0, **and** p100 − p50 still positive with the ΔchrF CI excluding 0 |
| **C: rise then plateau** | some step up from ref has the ΔchrF CI excluding 0, but p100 − p50 has a ΔchrF CI including 0 (or ΔBLEU < 0.3) |
| **D: fits more, generalizes no better** | val/train loss improve with data, but frozen metrics meet A |
| Inconclusive | none of the above (for example, non-monotone noise within the CIs) |

- **Comparison with P0-13** (frozen-147, verified from P0-13 files): representation swap ΔBLEU +2.23 [1.28, 3.39],
  ΔchrF +5.93 [4.66, 7.34], WER 1.025 → 0.939.
- "Data scaling matters as much" requires p100 − ref ΔBLEU to be within the P0-13 CI or larger.
- **Interpretation guardrail.** Whatever the outcome, this tests *supervised How2Sign scaling for this model and
  recipe*. It does not test broad sign-language pretraining data, and it cannot show that "data does not matter".
