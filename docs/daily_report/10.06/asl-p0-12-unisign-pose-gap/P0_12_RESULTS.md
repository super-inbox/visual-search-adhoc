# P0-12 — Results

**Status: PARTIAL.** Controlled translation inference was **not run**: no CUDA GPU (Step 4), and per instructions the
official path was not rewritten into a CPU approximation. The hypotheses were tested with preprocessing-only
evidence (full 128-clip pose diagnostics) and with the predictions that already exist. The controlled GPU
experiment is fully designed, prepared, and validated up to the model boundary.

## 1. Run facts

| Item | Value |
|---|---|
| Did controlled inference run? | **No** |
| Hardware | Apple M3 Pro, 18 GiB, macOS 14.1. `nvidia-smi` absent; `torch.cuda.is_available()=False`; MPS only |
| Clip count | 128 (frozen `how2sign_v2`, freeze `16c41282…411a`, re-verified 260/260) |
| Checkpoint | `how2sign_pose_only_slt.pth`, sha256 `1bfd5f33…683fb00d` (= HF LFS oid) |
| Pose sources prepared | A official · C rtmlib on official crop · B_aspect · B our 5.39 input (+ V4 runtime arms) |
| Decoding (prepared, every arm) | official `fine_tuning.py --eval`, `num_beams=4`, `max_new_tokens=100`, bf16, seed 42; batch 8 (V4 arms: batch 1) |
| Scorer | official `SLRT_metrics.sableu` (vendored sacrebleu 1.4.2, 13a), validated: reproduces 9.59 / 5.39 / 14.50 |
| Authors' released predictions, same 128 | **9.59** BLEU-4 |
| Our previous baseline, same 128 | **5.39** BLEU-4 (gap 4.20, paired-bootstrap 95 % CI 2.42–6.15) |
| New inference results | **none** |

## 2. Revised hypothesis

The received hypothesis, *"the pose extractor is the leading suspect"*, is **not supported by the full 128-clip
diagnostics** and is no longer used. "Pose extraction" breaks into separable parts. The pose network is the part
that differs least:

| Variable | Input-level evidence (all 128 clips) | Size | Translation-level evidence | Current standing |
|---|---|---|---|---|
| **V1 Timestamp alignment** | Official clips = How2Sign re-aligned timestamps (128/128 within 0.25 s); ours = original. IoU median 0.555; **28/128 zero overlap**, 61/128 < 0.5. Frame correspondence confirmed: on overlapping clips the timestamp-predicted frame is the best match within ±1 frame for 95/100 | **Large** | **Observational support** (§3) | **Leading hypothesis** |
| **V2 Crop / coordinate normalization** | Full 1280×720 (H/W 0.5625) vs signer crop (H/W 1.23); `kp/(W,H)` per axis → model-input shoulder-w/neck-h **0.90 vs 2.06** (~0.44×); body scale 0.55 vs 0.86 | **Large, systematic** | **None yet** | **Strong candidate, untested** |
| **V3 Pose extractor model** | Same frames, same crop: keypoint difference **0.85 %** (body), **1.5–1.7 %** (hands) of shoulder width; worst clip 2.6 %; no visibility disagreements; same confidence scale, missingness, jitter | **Small** | None | **Minor at keypoint level; not the leading suspect** |
| **V4 dtype / device / batch / inference** | dtype bf16 on both (held equal). CPU vs CUDA, batch 1 vs 8, single-process vs 8-worker RNG (affects the 34–36 clips > 256 frames), `S2T_Dataset_online` vs `S2T_Dataset` (logically identical) | Unknown | None | **Expected small; untested** |

Also measured: running the same extractor on the official crop instead of the full frame changes keypoints by only
0.7 % (body) / 1.05 % (hands) of shoulder width after a pure translation. Cropping matters through the
**normalization** (V2), not through detection quality.

## 3. Observational evidence for V1 (existing predictions, no new inference)

The authors' predictions all come from re-aligned clips, so their per-bucket score controls for sentence difficulty.

| IoU(our clip, re-aligned window) | n | Authors B4 | Ours B4 | Ours/Authors B4 | Authors chrF | Ours chrF |
|---|---|---|---|---|---|---|
| = 0 (no overlap) | 28 | 8.84 | **0.71** | **0.08** | 27.80 | 14.08 |
| (0, 0.5) | 33 | 13.06 | 6.90 | 0.53 | 31.83 | 22.43 |
| [0.5, 0.9) | 51 | 8.29 | 5.76 | 0.70 | 27.94 | 25.10 |
| ≥ 0.9 | 16 | 8.45 | 7.01 | **0.83** | 30.08 | 27.57 |
| **All** | 128 | **9.59** | **5.39** | 0.56 | 29.07 | 22.75 |

- Bootstrap: ours − authors = **−7.09** for IoU < 0.5 (95 % CI −10.6 to −3.9) vs **−2.25** for IoU ≥ 0.5 (CI −4.4 to
  −0.3). Difference of the two gaps: CI 1.0 to 9.0, excludes 0 (`data/bootstrap_iou_contrast.json`).
- Sentence-level Spearman ρ(IoU, ours − authors chrF) = **0.42** (permutation p < 1e-4). Control: ρ(IoU, authors'
  chrF) = 0.04 (p = 0.67), so IoU is not a stand-in for difficulty.

**Reading.** This **supports** V1 as a major contributor. It is observational and does not establish how much BLEU
re-aligned input would recover. The ~2.3-BLEU residual on the better-aligned half (CI excludes 0) is where V2, V3 and
V4 would show up. The pose diagnostics put V2 ahead of V3 by input size, but **that ordering is untested at
translation level.**

## 4. Does pose extraction explain the gap?

- **Pose extractor model (V3): not supported as the main cause.** Keypoint-level differences are ~1–2 % of shoulder
  width. This pass cannot rule out a small translation-level effect.
- **Pose input preparation: the leading explanation.** Timestamp alignment (V1) has observational support. Crop /
  coordinate normalization (V2) is a large, systematic input distortion with no translation evidence yet.
- **Runtime (V4):** open; expected small.
- **Overall: unresolved experimentally.** No share of the 4.20 gap is attributed to any variable until the GPU
  contrasts run.

## 5. Controlled-condition design (complete; ready to run)

| Contrast | Arms | Isolates | Why it is single-variable |
|---|---|---|---|
| Path check | A_official vs authors' released (9.59) | does the official path reproduce on the subset | — |
| **V3** | A_official − C_ours_on_official_crop | pose model + detector | identical crop videos/frames (128/128 frame counts and `w_h` equal) |
| **V1** | C_ours_on_official_crop − B_aspect | which frames (timestamps) | same extractor, same normalizer; crop-vs-full-frame detection differs ≤ 1 % of shoulder width, and translation is normalized away |
| **V2** | B_aspect − B_ours_5p39 | `kp/(W,H)` aspect | byte-identical detections and frames; only the normalizer's H/W changes |
| **V4a** | B_ours_5p39 − B_ours_5p39·bs1_nw0 (and the same on A) | batch 8 + worker RNG | pose input fixed |
| **V4b** | B_ours_5p39·bs1_nw0 (GPU) − 5.39 (historical CPU) | CUDA vs CPU kernels (+ loader class) | same input, batch 1, single process |
| Noise | A·seed43, A·seed44 − A | run-to-run (random >256-frame subsample) | sets the "no detectable effect" band |
| Interaction | V2 split by IoU < 0.5 / ≥ 0.5 | does geometry matter more once frames are right | — |

A − B = V3 + V1 + V2 (telescoping, same runtime). B(GPU) − 5.39 = V4. Decision rules are in `P0_12_PLAN.md`; every
contrast gets a paired-bootstrap CI (`scripts/contrasts.py`).

**Preparation status**

- All 4 pose conditions are built in the official pkl layout, together with the 128-clip and 3-clip
  `labels.test` subsets.
- Each condition passes the **unmodified official `S2T_Dataset` loader** on CPU with no model: 128/128 clips, part
  shapes (9/21/21/18, 3), sequence length ≤ 256 (`data/official_loader_validation.json`).
- `scripts/run_p012_gpu.sh` covers the full sequence: preconditions (checkpoint hash, CUDA), pinned clone, BLEURT
  and rouge install, a 3-clip smoke test per condition, 4 main arms and 4 V4/noise arms at 128 clips,
  `score_conditions.py`, then `contrasts.py`.
- Estimated 1–2 GPU-hours (estimate, not measured).
- The scoring scripts are validated on the existing predictions (9.59 / 5.39; reference contrast 4.20, CI
  2.42–6.15).
- Condition inputs (284 MB) are in the session scratchpad, which is temporary. Copy them out, or regenerate with
  `scripts/`.

## 6. Secondary Uni-Sign issues (documented, not separate experiments)

| Observation | Authors (128) | Ours (128) | Reading |
|---|---|---|---|
| Predictions with a repeated 3-gram | 33.6 % | 37.5 % | repetitive decoding is a **model/decoder property**, present in the authors' own outputs |
| … on the 34 clips where *our* sequence > 256 frames | 68 % | 74 % | concentrates in long clips for both |
| No terminal punctuation (truncation proxy) | 19.5 % | 15.6 % | `max_new_tokens=100` truncation hits both, the authors slightly more |
| … on the same 34 clips | 65 % | 47 % | long-sequence truncation is a shared Uni-Sign limitation |
| Unique predictions / distinct-1 | 1.00 / 0.254 | 1.00 / 0.255 | no diversity collapse |
| Exact matches | 0 | 0 | — |

Repetition and truncation occur at similar or higher rates in the authors' outputs. They look **separate from**
the 9.59 vs 5.39 accuracy gap.

## 7. Unresolved variables

1. Translation-level size of V1, V2, V3 (each separately).
2. V4: batch / worker RNG, and CUDA vs CPU.
3. Whether the released checkpoint reproduces the released predictions (E0 C3): the path check on the 128 clips,
   and optionally the full-test 14.5 run (needs the 8.47 GB pose archive).

## 8. Next step

Run `scripts/run_p012_gpu.sh` on one CUDA GPU with the prepared condition directories. Read the results against the
pre-fixed rules in `P0_12_PLAN.md`. If V1 and V2 are confirmed, the product-side fix is input preparation: segment to
the signing and crop to the signer (normalize by the crop). No model change is needed.

## 9. Not done (by instruction)

- No training, no P0-11/P0-13, and no CPU approximation of the official eval.
- No edits to the frozen benchmark, labels, E0 or historical results.
- No product or frontend changes.
- No commit or push.
- The upstream clone was only read.
- From the official archives, only the 128 relevant entries (137 MB) and the two zip directories (8.5 MB) were
  range-fetched.
