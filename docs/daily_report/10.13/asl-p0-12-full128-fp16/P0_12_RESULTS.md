# P0-12: controlled results (full 128 clips, T4 / fp16)

**Status: COMPLETE (T4 / fp16).** All four controlled P0-12 conditions ran through the same Uni-Sign inference and
evaluation path. Each produced 128/128 predictions. These are **T4 / fp16 controlled results**. They are **not**
an exact reproduction of the official bf16 configuration. Design, hypotheses and contrast definitions:
`../../10.06/asl-p0-12-unisign-pose-gap/P0_12_PLAN.md` and `P0_12_RESULTS.md` (the earlier preprocessing-only
pass). Machine-readable table: `p0_12_full128_fp16_results.csv`.

## 1. Objective

Find out why our earlier Uni-Sign result on the frozen 128-clip How2Sign subset (5.39 BLEU-4) was much lower than
the official-style pipeline (authors' released predictions: 9.59 BLEU-4). The question is whether the gap comes
from **our pose extractor** or from **input preparation** (timing / crop / coordinate normalization).

## 2. Setup

| Item | Value |
|---|---|
| Clips | same frozen 128 How2Sign clips in every condition |
| References | same 128 references in every condition |
| Checkpoint | same official Uni-Sign checkpoint (`how2sign_pose_only_slt.pth`) |
| Inference / evaluation | same Uni-Sign inference and evaluation path in every condition |
| Hardware | NVIDIA Tesla T4 |
| Precision | **fp16** (the T4 does not support bf16; the official configuration is bf16) |
| Predictions | 128/128 in every condition |

| Condition | Pose source | Timing / crop / normalization |
|---|---|---|
| **A_official** | official Uni-Sign poses | official re-aligned timing + signer crop |
| **B_ours_5p39** | our pose extractor (original pipeline) | original timestamps, full-frame preprocessing |
| **B_aspect** | our pose extractor (same detections as B) | original timestamps, full frame, aspect / coordinate normalization corrected |
| **C_ours_on_official_crop** | our pose extractor | official re-aligned timing + signer crop |

## 3. Measured results

| Condition | n | BLEU-1 | BLEU-2 | BLEU-3 | **BLEU-4** | ROUGE | BLEURT |
|---|---|---|---|---|---|---|---|
| A_official | 128 | 32.39 | 19.52 | 12.88 | **9.13** | 29.00 | 0.4407 |
| B_ours_5p39 | 128 | 24.24 | 12.80 | 8.08 | **5.47** | 18.69 | 0.3767 |
| B_aspect | 128 | 24.99 | 13.77 | 8.72 | **5.80** | 20.59 | 0.3849 |
| C_ours_on_official_crop | 128 | 31.50 | 18.99 | 12.38 | **8.61** | 27.67 | 0.4247 |

Full-precision values are in `p0_12_full128_fp16_results.csv`.

The ordering is the same on every metric: **B_ours_5p39 < B_aspect < C_ours_on_official_crop < A_official**.

## 4. Measured deltas

| Contrast | What changes | ΔBLEU-1 | ΔBLEU-4 | ΔROUGE | ΔBLEURT |
|---|---|---|---|---|---|
| B_ours_5p39 → B_aspect | aspect / coordinate normalization only | +0.75 | **+0.3238** | +1.90 | +0.0082 |
| B_aspect → C_ours_on_official_crop | official timing + crop (same extractor) | +6.51 | **+2.8109** | +7.08 | +0.0398 |
| B_ours_5p39 → C_ours_on_official_crop | official timing / crop / normalization (same extractor) | +7.27 | **+3.1347** | +8.98 | +0.0481 |
| C_ours_on_official_crop → A_official | pose source only (ours → official), timing / crop matched | +0.89 | **+0.5238** | +1.33 | +0.0159 |
| B_ours_5p39 → A_official | total gap | +8.15 | **+3.6584** | +10.31 | +0.0640 |

Share of the total B_ours_5p39 → A_official gap:

| Step | BLEU-4 | ROUGE | BLEURT |
|---|---|---|---|
| B_ours_5p39 → B_aspect | 8.9 % | 18.4 % | 12.9 % |
| B_ours_5p39 → C_ours_on_official_crop | **85.7 %** | 87.1 % | 75.1 % |
| C_ours_on_official_crop → A_official (remaining) | 14.3 % | 12.9 % | 24.9 % |

BLEU-4 recovery = (8.60817 − 5.47351) / (9.13194 − 5.47351) = 3.1347 / 3.6584 = **85.7 %**.

**Not measured in this run:** paired-bootstrap confidence intervals, seed-to-seed noise, and per-clip breakdowns.
The deltas above are point estimates on n = 128.

## 5. Interpretation

- **Input preparation, not the pose extractor, is the dominant source of the gap.** Our own extractor, run under
  the official timing / crop, raises BLEU-4 from 5.47 to 8.61. That recovers about 86 % of the gap to A_official.
  ROUGE (87 %) and BLEURT (75 %) agree.
- **The pose extractor accounts for a small remainder.** Once timing and crop are matched, swapping our poses for the
  official ones adds only +0.52 BLEU-4, +1.33 ROUGE and +0.016 BLEURT. This matches the earlier keypoint-level
  diagnostic (our keypoints differ from the official ones by about 1–2 % of shoulder width).
- **Aspect / coordinate normalization alone gives only a modest gain** (+0.32 BLEU-4). Even when corrected, the
  normalization does not explain most of the gap while the original timestamps and full frame are still used.
- **Most of the gain arrives together with the official timing / crop** (B_aspect → C: +2.81 BLEU-4). This
  condition changes several things at once: the frame window (re-aligned timestamps), the signer crop, and the
  normalization frame that comes with the crop. The design cannot split this gain between timing and cropping.
  The earlier observational IoU analysis (see 10.06 report) suggests that timestamp misalignment is a large part of
  it, but this run does not test that directly.

## 6. Limitations

1. **T4 / fp16, not bf16.** The available T4 does not support bf16. Absolute scores are **not** an exact
   reproduction of the official bf16 configuration. For reference only: A_official here is 9.13 BLEU-4 vs 9.59 for
   the authors' released predictions, and B_ours_5p39 is 5.47 vs our historical 5.39. These cross-runtime differences
   are not attributed to any single cause.
2. **Internally controlled.** All four conditions share the same runtime (T4, fp16), clips, references, checkpoint
   and inference / evaluation path. Therefore the **contrasts between conditions** are the main result, more than
   the absolute values.
3. **Bundled preprocessing factor.** "Official timing / crop" changes the timestamps, the crop and the related
   normalization together. Do not credit the whole gain to timing alone or crop alone.
4. **No uncertainty estimates.** Single run per condition and no bootstrap CIs. The small deltas
   (B → B_aspect +0.32; C → A +0.52 BLEU-4) may fall inside run-to-run or sampling noise. Their sign and size should
   be read as indicative.
5. **Scope.** The run covers 128 clips with one checkpoint. Do not extend the causal claims beyond these controlled
   conditions.

## 7. Conclusion

Under a controlled T4 / fp16 runtime, most of our earlier Uni-Sign shortfall on the frozen 128-clip subset comes
from **timing / cropping / preprocessing**, not from our pose extractor. Running our extractor on the official timing
and crop recovers about **86 % of the BLEU-4 gap** (5.47 → 8.61 vs 9.13). Replacing our poses with the official
ones adds only another ~0.52 BLEU-4. The practical fix is input preparation: segment the clip to the signing and
crop to the signer. Changing the pose extractor or the model is not the priority.

## 8. Next step: Uni-Sign error taxonomy

The input-preparation gap is now mostly explained. The next question is **where Uni-Sign itself fails** when inputs
are correct. Use the A_official and C_ours_on_official_crop predictions on the same 128 clips (and extend to more
clips if possible). Tag each reference / prediction pair with these categories:

- **Fingerspelling** (spelled words, acronyms)
- **Numbers** (quantities, dates, times)
- **Named entities** (people, places, brands)
- **Negation and questions** (polarity flips, wh- / yes-no forms)
- **Visual-quality conditions** (motion blur, occlusion, hands out of frame, low-confidence keypoints, long clips
  over 256 frames)

For each category, report the per-category score and the main error types (omission, substitution, hallucination,
repetition). Compare A against C to check whether any category is sensitive to the pose source. The goal is to rank
the categories where Uni-Sign does worst, and use that ranking to choose the next data or modelling work.
