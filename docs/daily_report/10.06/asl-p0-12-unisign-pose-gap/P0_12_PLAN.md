# P0-12 — Plan: Uni-Sign same-128 inference gap (9.59 vs 5.39)

## Research question

On the same 128 frozen How2Sign clip IDs, with the same references and the same official BLEU code, the authors'
released predictions score **9.59** and our Uni-Sign pipeline scores **5.39** (E0, re-verified; paired-bootstrap
95 % CI for the 4.20 gap: 2.42–6.15). Which part of our inference/preprocessing path causes the gap, and can it be
closed without training?

## Hypothesis: as received, and as revised by the evidence

**As received (H0):** the gap is caused by the *pose extractor*: rtmlib `lightweight` (RTMW-dw-l-m 256×192) vs the
paper's RTMPose-x.

**Revised after the full 128-clip pose diagnostics:** H0 is **not supported as the leading explanation.** On
identical frames, our extractor reproduces the official keypoints to 0.85 % (body) / ~1.6 % (hands) of shoulder width,
with identical confidence and missingness statistics (`POSE_DIAGNOSTICS.md` §2). The input differences that *are*
large sit upstream and downstream of the pose model:

- **H1 (leading): timestamp alignment.** Our clips are cut at How2Sign *original* timestamps; the authors' at
  *re-aligned* timestamps. 28/128 of our clips contain none of the signed sentence. This has observational support
  in existing predictions (`P0_12_RESULTS.md` §3).
- **H2 (strong candidate): signer crop / coordinate normalization.** Full 1280×720 frame vs signer crop. Uni-Sign
  divides x by W and y by H separately, so our model input is ~0.44× as wide, relative to height, as in training.
  This is a large systematic input change with no translation-level evidence yet.
- **H3 (minor, keypoint level): pose extractor model.** Small measured difference; translation effect untested.
- **H4 (expected small, untested): dtype / device / batch / inference runtime.**

These are hypotheses for the GPU run to test, not conclusions.

## The four variables, kept separate

| ID | Variable | Ours (5.39) | Official / authors | Input difference measured | Isolating contrast |
|---|---|---|---|---|---|
| **V1** | Timestamp alignment (which frames) | original timestamps | re-aligned (128/128 within 0.25 s) | IoU median 0.555; 28/128 zero overlap | **C − B_aspect** |
| **V2** | Crop / coordinate normalization | `kp/(1280,720)`, H/W 0.5625 | `kp/(crop W,H)`, median H/W 1.23 | shoulder-w/neck-h 0.90 vs 2.06 | **B_aspect − B** |
| **V3** | Pose extractor model | rtmlib YOLOX-tiny + RTMW-dw-l-m 256×192 | official `rtmpose-192` (MMPose) | 0.85 % / 1.6 % of shoulder width on identical frames | **A − C** |
| **V4** | dtype / device / batch / inference | bf16, CPU, batch 1, single-process RNG, `S2T_Dataset_online` | bf16, CUDA (deepspeed), batch 8, 8 DataLoader workers, `S2T_Dataset` | not measurable without GPU | **B − B_bs1_nw0** (batch + worker RNG); **B_bs1_nw0(GPU) − 5.39(CPU)** (device/kernels + loader class) |

dtype cannot be varied in the official path (`--dtype` ∈ {fp16, bf16}). Both pipelines use bf16, so dtype is held
equal, not tested.

## Why each contrast isolates one variable

- **A vs C (V3):** same official crop videos, same frames (128/128 frame counts and `w_h` equal), same normalizer.
  Only the pose network and detector differ.
- **B vs B_aspect (V2):** byte-identical detections and frames (B_aspect is B's pixel keypoints divided by the
  clip's official crop (W,H) instead of (1280,720)). Uni-Sign's `crop_scale` is invariant to translation and
  isotropic scale, so only the normalizer's H/W ratio changes. B_aspect restores shoulder-w/neck-h to 2.01 (A: 2.06).
- **B_aspect vs C (V1):** both use the official crop's (W,H). They differ in which frames are included. They also
  differ in whether the keypoints came from detection on the full frame or on the crop. The second difference was
  measured and is negligible. On the 100 clips where our window and the re-aligned window overlap, B keypoints map
  onto C keypoints by a pure translation: fitted scale 1.001, x/y ratio 1.003, residual 0.7 % (body) / 1.05 %
  (hands) of shoulder width, smaller than V3 itself. The best frame offset is within ±1 frame of the timestamp
  prediction for 95/100 clips (`data/crossframe_alignment_B_vs_C.json`). So C − B_aspect is effectively a
  timestamp-only contrast.
- **V4:** B (batch 8, 8 workers) vs B_bs1_nw0 (batch 1, no workers), with the pose input fixed. Then B_bs1_nw0 on
  GPU vs the historical CPU 5.39: device/kernels plus `S2T_Dataset` vs `S2T_Dataset_online` (logically identical for
  pose-only; E0). The same batch contrast on the official input (A vs A_bs1_nw0) checks consistency.
- **Noise band:** A with seeds 43 and 44 vs 42. The seed only changes the random subsample of the 36 clips over 256
  frames. This bounds run-to-run variation.

The chain telescopes: **A − B = V3 (A−C) + V1 (C−B_aspect) + V2 (B_aspect−B)**, all on GPU with identical runtime,
and **B(GPU) − 5.39(CPU) = V4**. Contributions are order-dependent if variables interact (e.g. geometry may matter
more on well-aligned clips). The order above is fixed in advance, and an IoU-stratified V2 contrast is reported as
an interaction check.

## Conditions (all prepared, all pass the unmodified official loader, 128/128)

| Condition | V1 frames | V2 normalizer | V3 extractor | V4 runtime |
|---|---|---|---|---|
| **A_official** | re-aligned | crop (W,H) | official | GPU, bs 8, 8 workers, seed 42 |
| **C_ours_on_official_crop** | re-aligned | crop (W,H) | rtmlib-lite | same |
| **B_aspect** | original | crop (W,H) | rtmlib-lite | same |
| **B_ours_5p39** | original | (1280,720) | rtmlib-lite | same |
| B_ours_5p39 · bs1_nw0 | original | (1280,720) | rtmlib-lite | GPU, bs 1, 0 workers |
| A_official · bs1_nw0 | re-aligned | crop | official | GPU, bs 1, 0 workers |
| A_official · seed43 / seed44 | re-aligned | crop | official | seed 43 / 44 |

## Controls (held fixed everywhere)

Same 128 clip IDs and references (freeze `16c41282…`); same checkpoint (sha256 `1bfd5f33…`); same mT5-base; same
unmodified `fine_tuning.py --eval` (only README-sanctioned `config.py` paths change); `num_beams=4`,
`max_new_tokens=100`, HF defaults otherwise, bf16, `max_length=256`; same scorer (`score_conditions.py` → official
`SLRT_metrics.sableu`, validated 9.59 / 5.39) and same contrast script (`contrasts.py`, paired bootstrap, 2,000
resamples).

## Decision rules (fixed before inference)

| Check | Criterion (BLEU-4 on the 128, paired 95 % CI) | Interpretation |
|---|---|---|
| Path reproduces | A_official within 1 BLEU of 9.59 and CI of (A − authors) contains 0 | the official path reproduces on the subset; attribution is meaningful. If not, report the miss first (V4 or checkpoint, E0 C3) |
| Noise floor | \|seed43 − A\|, \|seed44 − A\| | contrasts smaller than this band are reported as "no detectable effect" |
| Per variable | CI excludes 0 **and** \|Δ\| exceeds the noise band | variable has a detectable effect; report Δ and share of (A − B) |
| V1 leading | C − B_aspect is the largest share of A − B | H1 supported |
| V2 matters | B_aspect − B CI excludes 0 | geometry fix alone recovers BLEU (cheap product fix) |
| V3 minor | \|A − C\| ≤ noise band | H0 (extractor) not supported at translation level |
| V4 small | \|B_bs1_nw0 − 5.39\| ≤ 1 and B − B_bs1_nw0 CI contains 0 | runtime not a material part of the gap |

Words to use: "supports" / "does not yet establish". A share is reported only with its CI. "Explains 100 %" is not
used unless the A − B decomposition plus V4 accounts for the full 4.20 within CIs.

## Status criteria for P0-12

- **COMPLETE:** all 8 runs scored and contrasts reported against the rules above.
- **PARTIAL:** no controlled inference, but the hypotheses tested with preprocessing-only and observational evidence,
  and the GPU run fully prepared and validated. **← this pass** (no CUDA GPU; no CPU approximation run, by instruction).
- **BLOCKED:** neither.
