# P0-13: representation swap (frozen Uni-Sign features), plan

Date: 2026-10-07 · Scope: P0-13 only. P0-11 is not started and P0-12 is not modified. No commit or push.

## Question

With the downstream supervised data held fixed at P0.2's 2,751 clips, does a better input representation
materially improve translation? This is experiment **E1** from
`docs/daily_report/10.05/asl-research-followup/ASL_DATA_REPRESENTATION_UNISIGN_ANALYSIS.md` §6.

## Arms (one variable)

| | Baseline (A) | Treatment (B) |
|---|---|---|
| Per-frame input | 501-d MediaPipe landmarks (Kaggle train/val, local frozen extraction) | **768-d frozen Uni-Sign features**: mT5-Base encoder output of `how2sign_pose_only_slt.pth` on the official RTMPose poses |
| Conformer input projection | Linear(501→512) | Linear(768→512), the only shape change |
| Conformer (4 layers, d 512, stride-2), MLP bridge, t5-small decoder (encoder deleted) | trained from scratch / HF t5-small | **same** |
| Tokenizer, max target 30 | t5-small | **same** |
| Optimizer | Adafactor, 4 param groups, T5 lr ×0.1, wd 0.01 | **same** |
| Schedule | lr 1e-4, linear, warmup 0.1, 30 epochs, early stop patience 10 on val loss | **same** |
| Batch / seed / device | 8 / 42 / CPU | **same** |
| Generation | greedy, max_length 30 | **same** |
| Metrics | sacrebleu BLEU, chrF, jiwer WER on full references | **same** (same `score()` code) |
| Data | 2,751 train / 366 val / 147 frozen (P0.2 `ids/*.txt`) | **same IDs, same order, same reference strings** |

- **Baseline:** the existing P0.2 padfix run (`gloss-free-asl-translation/results/p02_padfix_10pct_e30`, best
  epoch 20 by val loss). It is reused, not retrained.
- **Treatment:** `scripts/train_p013_unisign.py`, a copy of `scripts/train_p02.py` with a 65-line diff
  (feature dataset + `input_dim`).

## Forced deviations (cannot be held fixed; reported, not hidden)

1. **Augmentation.** P0.2's landmark augmentations (flip, temporal drop, hand dropout, 3D jitter) cannot act on
   cached frozen features, so the treatment trains without augmentation.
2. **Frame source.** Uni-Sign needs COCO-WholeBody RTMPose keypoints. These exist only in the official archive,
   which uses the re-aligned clip timings and the official signer crop. Baseline landmarks come from Kaggle
   (train/val) and our own original-timing videos (frozen). P0-12 showed that 28/128 of our frozen clips have zero
   overlap with the re-aligned window. **On the frozen set, the treatment therefore also sees better-aligned
   video.** This confound is reported, not removed.
3. **Precision.** Uni-Sign runs in fp32 instead of the official bf16, because bf16 is about 50× slower on this
   CPU. Measured drift: mean per-frame cosine 0.9994.

## Leakage audit (decides which numbers count)

Uni-Sign's own `data/How2Sign/labels.train` contains **all 2,751 train and all 366 val clips**. The frozen
147 are all in its `labels.test`.

- **Frozen 147 is the only clean comparison.** It is the primary endpoint.
- **Val 366 is contaminated for the treatment.** The frozen encoder was fine-tuned on these exact clip–sentence
  pairs. Treatment val metrics are reported but not used to judge the hypothesis. Checkpoint selection by val
  loss (unchanged recipe) is also affected, so frozen results are reported both at the val-selected epoch and at
  the fixed final epoch 30.
- "Identical supervised data" holds **only for the downstream component**. The frozen representation itself was
  built from about 31k How2Sign train pairs plus 984 h of YouTube-ASL. That is what is being tested ("our
  representation" vs "a pretrained one"), but it must not be described as "same data, better architecture".

## Outputs and diagnostics

- val and frozen BLEU, chrF and WER at the selected and final epochs, for both arms
- prediction diversity: unique predictions, top-1 share, distinct-1/2
- **correct-vs-shuffled video:** teacher-forced loss and generation with deranged inputs (5 seeds), same
  definition as `diagnose_input_dependence.py`
- **collapse statistics:** mean pairwise cosine of mean-pooled representations across clips, raw and
  mean-centred, plus PC1 energy share. Measured at three points: the input features, the encoder output after
  the bridge (what the decoder sees), and the raw Uni-Sign features
- **feature interface check:** decode cached features with Uni-Sign's own frozen decoder and compare with the
  authors' released predictions

## Decision rule (fixed before treatment results)

The primary metric is frozen-147 BLEU and chrF at the val-selected checkpoint, with a paired bootstrap 95% CI for
B − A (10k resamples).

| Outcome | Reading |
|---|---|
| CI of ΔchrF excludes 0 **and** ΔBLEU ≥ +2 (about 3× baseline), with shuffled-video Δloss clearly larger than baseline | **Material improvement**: supports a representation bottleneck at fixed downstream data |
| Δ within noise (CI includes 0, or ΔBLEU < +1) | **Not established**: representation swap did not help in this setup |
| B < A | Report it; the swap made translation worse here |

Because of confound 2, a material improvement is then checked on the frozen clips where our original-timing
clip overlaps the re-aligned window (IoU ≥ 0.5, from P0-12) to see whether it survives.
