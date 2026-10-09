# Next Steps (ASL P0-11 / P0-12 / P0-13)

2026-10-09 · Context: `WORK_REPORT.md` §9–10.

## A. Required to answer the current manager questions

| # | Action | Answers | Needs | Est. cost | Done when |
|---|---|---|---|---|---|
| 0 | **Copy scratchpad artifacts to durable storage.** These are the P0-12 condition inputs (284 MB), the P0-11 runs including partial `ref_omp4`, and the P0-13 features and checkpoints. All currently exist only in temporary Claude session scratchpads. | protects everything below | disk | minutes | artifacts in durable storage, outside any temporary session scratchpad |
| 1 | **P0-12 controlled inference on one CUDA GPU.** Run `10.06/asl-p0-12-unisign-pose-gap/scripts/run_p012_gpu.sh`: path check, then V3 extractor, V1 timestamps, V2 crop/normalization and V4 runtime/batch, one variable at a time, plus seed-noise arms. | Q3 "what is wrong with our Uni-Sign pipeline", and part of Q4 | 1 CUDA GPU, BLEURT/rouge install | about 1–2 GPU-h (estimate) | every contrast scored with a paired CI against the pre-fixed rules in `P0_12_PLAN.md` |
| 2 | **P0-11 same-init 2,751 control.** Finish `ref_omp4` from scratch with the original command, or resume from `checkpoint-688`. Keep the machine awake (caffeinate, lid open, on power). Alternatively, rerun the full P0-11 matrix later with identical init and seeds. | firms up Q1/Q2 (removes the init confound) | CPU only | about 2.4 h CPU (single run); about 8–10 h for the full matrix | frozen-147 metrics and shuffled-video diagnostics for the same-init 2,751 point |
| 3 | **Decide the canonical Uni-Sign preprocessing path** from the step-1 results. Expected: segment to re-aligned or actual signing, and crop to the signer before normalization. | Q4/Q6 | step 1 | about 0.5 day | written spec plus one re-scored 128-clip run with that path |

Order: 0 → 1 and 2 in parallel (GPU vs CPU) → 3.

## B. Future research (lower priority)

| Action | Why |
|---|---|
| Multi-seed P0-13 (≥ 3 seeds per arm) | current CIs cover test-sample noise only |
| Uni-Sign decoder fine-tuning on our data | the same features with Uni-Sign's own decoder reach 6.4–9.0 BLEU vs 3.25 through t5-small |
| Random-initialized Uni-Sign architecture control | separates pretraining from architecture in the P0-13 gain |
| Real Curify-user video adaptation and evaluation | How2Sign test shares signers with train; domain generalization is untested |
| ASL-fluent human evaluation | BLEU/chrF at this level say little about usefulness |
| (Optional) longer or fixed-epoch P0-11 p100 | p25/p50/p100 best checkpoints were at their last evals (lower bounds) |

## C. Explicitly not recommended now

- Collecting or labelling more How2Sign-style sentence pairs for the current landmark baseline. P0-11 shows no
  translation gain from up to 9.6× more.
- Presenting Uni-Sign as deployable before step 3 and a real-user evaluation.
