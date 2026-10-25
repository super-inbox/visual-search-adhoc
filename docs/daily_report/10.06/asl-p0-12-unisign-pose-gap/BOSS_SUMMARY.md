# P0-12 — Boss summary: why is our Uni-Sign at 5.39 when the authors get 9.59 on the same 128 clips?

**Status: PARTIAL.** No CUDA GPU on this machine, so the controlled translation runs were **not** executed. The
experiment is fully designed and its inputs pass the official data loader. The findings below come from pose
measurements on all 128 clips and from the predictions we already had.

**A. Why 5.39 vs 9.59?**
"Same 128 clips" turned out to mean the same clip IDs and sentences, **not the same video input**. We separated
four possible causes:

| Cause | What we found | Size |
|---|---|---|
| 1. **Timestamp alignment** | Authors cut clips at How2Sign's *re-aligned* timestamps, we used the *original* ones. In **28/128** clips our video contains none of the signed sentence | **large**, with evidence in BLEU (see B) |
| 2. **Crop / coordinate normalization** | We fed the full 1280×720 frame; the authors used a signer crop. Uni-Sign's scaling then makes our skeleton ~0.44× as wide as what it was trained on | **large** input distortion; BLEU effect not yet tested |
| 3. **Pose extractor model** | On identical frames our lightweight model matches the official keypoints within ~1–2 % of shoulder width | **small**, no longer the leading suspect |
| 4. **dtype / device / batch** | Same bf16; CPU vs CUDA, batch 1 vs 8 | not measurable here; expected small |

**B. Did pose extraction explain the gap?**
**Not the pose model.** The evidence points to *how the input is prepared* (which seconds of video, and how the
frame is cropped and normalized). Timestamp alignment has real support from existing predictions:

| Our clips that… | Clips | Authors' BLEU | Our BLEU |
|---|---|---|---|
| miss the signed part completely | 28 | 8.84 | 0.71 |
| cover ≥ 90 % of it | 16 | 8.45 | 7.01 |

The gap is significantly larger on misaligned clips (bootstrap CI of the difference excludes 0). That is still a
correlation, not a controlled test.

**C. How much did it recover?**
**Nothing measured yet. We do not claim a number.** On the better-aligned half of clips our deficit is about
2.3 BLEU, vs 7.1 on the misaligned half. The recoverable amount has to come from the GPU run.

**D. What to test next**
One GPU session (estimated 1–2 GPU-hours): `scripts/run_p012_gpu.sh`. Each comparison changes exactly one cause:

| Comparison | Measures |
|---|---|
| our crop-correct input vs official-timing input | timestamp alignment |
| our input vs same input with corrected crop normalization | crop / normalization |
| our extractor vs official extractor on identical frames | pose model |
| batch 1 vs 8, and GPU vs our old CPU run | runtime |

Plus a seed-noise check. Every result comes with a confidence interval, and decision rules were fixed in advance.

**E. Can Uni-Sign remain our research base?**
**Yes, provisionally.** Nothing points to a defect in the checkpoint or decoder. Our pose model looks
equivalent to the official one, and repetition and truncation appear in the authors' own outputs too. Confirm with the
GPU run. Product implication if confirmed: live input must be **segmented to the actual signing** and **cropped to
the signer before normalization**. That is a preprocessing fix, not a model change.
