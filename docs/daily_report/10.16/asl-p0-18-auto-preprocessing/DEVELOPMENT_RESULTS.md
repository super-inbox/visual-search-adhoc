# P0-18 development results (How2Sign TEST only)

**Date:** 2026-10-19 · Plan: `EXPERIMENT_PLAN.md` · Config: `config/p018_config.json` · Not committed.
Everything here is **development** evidence on How2Sign test, which is exploratory / validation-used under P0-16.
It is not the P0-18 result; that is the one-shot H18 run. H18 and H19 were not opened.

**Final candidate (revision 2): B_crop_only = original timing + automatic signer crop** (§5a). The revision-1
candidate B_auto (automatic widened timing + crop) is kept as a descriptive arm.

All poses come from the canonical T4 pose environment and all predictions from the canonical T4 decoder environment.
No Mac-CPU pose or Mac-decoded prediction is part of any number below (Mac outputs: cross-checks only, §6).

## 1. Pose extraction (T4, canonical)

| | Full TEST videos | Oracle arm (official crop clips) |
|---|---|---|
| Completed / failed | **184 / 0** | **128 / 0** |
| Frames | 521,219 | 29,113 |
| Throughput | 31.26 fps (pose 16,675 s; wall 16,795 s = 4 h 40 min) | 34.6 fps (wall 1,558 s) |
| Output | 727 MB npz; per-file SHA-256 in `SUMMARY.json` (sha256 `9aa8a4d4…`), re-verified locally 184/184 | 128 pkls, SHA-256 verified locally 128/128 |

- Settings: per-frame RTMPose, CUDAExecutionProvider, `cudnn_conv_algo_search = HEURISTIC`, deterministic compute,
  4 workers. The CPU-fallback-must-fail check stayed on; it never triggered.
- Videos were range-fetched from the pinned mirror and had to reproduce the SHA-256 of the member in the locally
  verified archive (`3755f06d…`). At most ~4 temporary videos were on the VM at once; each was deleted only after its
  npz passed validation (frame count, layout, finite values) and was checksummed.
- Determinism: `_fZbAxSSbX4-5-rgb_front` gave arrays sha256 `b796a84f…` in two preflight runs and in the production run.
- ORT warnings: one "Non-deterministic TopKImpl kernel" (detector), 4 "nodes not assigned to preferred EP", 6
  "unused initializer"; **0 cuDNN "Fallback mode"**. One transient curl HTTP/2 error, retried and verified.

## 2. Automatic timing detector (timing agreement only; details `p018-work/dev/tune_gpu/TIMING_DETECTOR_NOTE.md`)

5-fold CV grouped by VIDEO_ID, 2,357 clips, interval IoU vs the re-aligned window:

| Detector | mean IoU | median IoU | IoU = 0 |
|---|---|---|---|
| Original timing (old) | 0.335 | 0.195 | 42.3% |
| **Selected: original + [+0.5 s, +2.0 s], snapped to activity edges ±2 s** | **0.350** | **0.317** | **35.3%** |
| Pose-estimated per-video constant lag | 0.275 | 0.064 | 47.2% |
| Pose-estimated per-video linear warp | 0.292 | 0.107 | 44.6% |

The pose-only drift estimators do not work (signing is near-continuous, so activity does not identify the drift) and
were disabled by the tuning. In-sample 0.354 vs CV 0.350; in-sample failure rate 0.64% (15 / 2,357).

## 3. Automatic signer crop (box agreement only)

128 clips, oracle box recovered from GPU poses (affine fit full frame → official crop, median residual 1.96 px, all 128
positioned). Auto crop vs official crop: **CV mean IoU 0.868** (full frame 0.301), median |log aspect error| 0.098 (full
frame 0.78). Selected: pct 1, margin_x 0.25, margin_top 0.5, to bottom.

## 4. Old vs Automatic vs Oracle (Uni-Sign translation, T4 decoder)

Paired bootstrap over source videos (B = 2,000, seed 20261016). Δ are vs A_old unless stated.

### 4.1 Full TEST: 2,347 evaluable clips (149 VIDEO_IDs)

| Arm | Timing | Crop | BLEU-4 | chrF | WER | Length ratio |
|---|---|---|---|---|---|---|
| **A_old** | original | full | 4.85 | 22.08 | 101.1 | 0.90 |
| B_crop_only | original | auto | 5.24 | 22.56 | 100.9 | 0.90 |
| B_time_only | auto | full | 5.40 | 24.19 | 110.8 | 1.08 |
| **B_auto** | auto | auto | **5.77** | **24.71** | 109.7 | 1.08 |
| O_time | re-aligned | full | 12.28 | 32.04 | 88.7 | 0.95 |
| O_time_crop | re-aligned | auto | 13.15 | 32.97 | 87.2 | 0.95 |

| Contrast | Δ BLEU-4 [95% CI] | Δ chrF | Δ WER |
|---|---|---|---|
| **B_auto − A_old** | **+0.92 [0.49, 1.37]** | +2.62 [2.18, 3.04] | **+8.62 [6.77, 10.49]** |
| Timing only: B_time_only − A_old | +0.55 [0.17, 0.96] | +2.11 [1.64, 2.54] | +9.72 [7.89, 11.63] |
| Crop only: B_crop_only − A_old | +0.39 [0.17, 0.62] | +0.48 [0.24, 0.73] | −0.14 [−1.30, 1.01] |
| Crop given auto timing: B_auto − B_time_only | +0.37 [0.11, 0.62] | +0.52 [0.22, 0.78] | −1.10 [−2.27, 0.18] |
| Timing given auto crop: B_auto − B_crop_only | +0.53 [0.09, 0.99] | +2.14 [1.73, 2.54] | +8.76 [6.95, 10.59] |
| Oracle timing: O_time − A_old | +7.43 [6.18, 8.68] | +9.96 | −12.31 |
| Oracle timing + auto crop: O_time_crop − A_old | +8.30 [7.01, 9.62] | +10.89 | −13.89 |

**Gap recovery (full TEST, oracle = re-aligned timing + auto crop):** B_auto recovers **11.1%** of the BLEU-4 gap
(0.92 of 8.30) and 24.1% of the chrF gap.

### 4.2 Oracle-arm set: 128 clips (one per video), adds the official-crop oracle

| Arm | BLEU-4 | chrF | WER | Length ratio |
|---|---|---|---|---|
| **A_old** | 5.12 | 21.99 | 97.7 | 0.83 |
| B_crop_only | 6.10 | 23.53 | 95.6 | 0.83 |
| B_time_only | 6.50 | 25.08 | 102.3 | 0.96 |
| **B_auto** | **6.65** | **25.13** | 103.1 | 0.98 |
| B_lag_only | 6.75 | 25.16 | 103.5 | 0.97 |
| O_time | 7.56 | 27.07 | 94.7 | 0.91 |
| O_time_crop | 8.32 | 27.25 | 92.7 | 0.90 |
| **C_official** | **8.79** | **27.76** | 93.1 | 0.89 |

| Contrast | Δ BLEU-4 [95% CI] | Δ chrF | Δ WER |
|---|---|---|---|
| **B_auto − A_old** | **+1.53 [0.18, 2.80]** | +3.14 [1.70, 4.70] | +5.39 [1.74, 9.22] |
| C_official − A_old | +3.67 [2.18, 5.34] | +5.77 | −4.62 |
| C_official − B_auto | +2.14 [0.68, 3.89] | +2.64 | −10.01 |
| Timing only | +1.38 [0.12, 2.45] | +3.09 | +4.52 |
| Crop only | +0.98 [−0.18, 2.21] | +1.54 | −2.12 |
| C_official − O_time_crop (official vs auto crop at oracle timing) | +0.47 [−0.25, 1.21] | +0.51 | +0.42 |

**Gap recovery (128, oracle = C_official):** **41.7%** of the BLEU-4 gap (1.53 of 3.67), 54.3% of chrF.

### 4.3 Reading

1. **Automatic preprocessing helps, modestly.** On the full TEST set, B_auto beats the old pipeline by +0.92 BLEU-4
   (CI excludes 0) and +2.6 chrF.
2. **Timing vs crop.** Both contribute and roughly add up: timing alone +0.55, crop alone +0.39, both +0.92 BLEU-4.
   The **crop** is a clean gain (BLEU and chrF up, WER neutral) and is nearly as good as the official crop (+0.47 BLEU,
   CI includes 0, at oracle timing). The **timing** gain comes with a cost: windows extended by ~2 s make outputs
   ~20% longer (length ratio 0.90 → 1.08) and **raise WER by ~9 points**.
3. **Most of the gap is timing, and automatic timing closes little of it.** Re-aligned timing alone is worth +7.4
   BLEU-4 on full TEST; pose-only automatic timing recovers 11% of the total oracle gap.
4. **The 128-clip oracle benchmark is not representative of the full test set.** Its oracle gap is 3.2–3.7 BLEU-4
   versus 8.3 on full TEST, so its 42% recovery overstates what the pipeline achieves. The pre-registered P2 uses
   C_official, which exists on dev only for these 128 clips; on H18 it is computed on all H18 clips, where a full-TEST
   -like gap would put recovery near 11% (P2 fail).

## 5. Pre-registered criteria applied to development data (descriptive)

Frozen thresholds (`config/p018_config.json`, unchanged since revision 1); P1 / P5 on full TEST, P2 on the 128 set
(C_official exists on dev only there), P3 / P4 from the full-TEST build and pose logs. Computed by `dev_compare.py`.

| Criterion | Threshold | Revision 1: B_auto (widened timing + crop) | **Revision 2 (final): B_crop_only** |
|---|---|---|---|
| P1 Δ BLEU-4, CI lower > 0 | ≥ +0.5 | +0.92 [0.49, 1.37] — pass | +0.39 [0.17, 0.62] — **fail** (CI > 0, below +0.5) |
| P2 gap recovery (C_official, 128) | gap ≥ 1.0, ≥ 0.33 | 0.417 — pass (full-TEST analogue 0.111) | 0.266 — **fail** (full-TEST analogue 0.047) |
| P3 failure rate | ≤ 5% | 0.64% (15 / 2,357) — pass | 0.34% (8 / 2,357; all < 2-frame windows, 0 crop fallbacks) — pass |
| P4 preprocessing s/clip | ≤ 15 s | 7.1 s — pass | 7.1 s — pass |
| P5 do no harm | length in [0.8, 1.2]; Δ WER CI upper ≤ +5.0 | 1.079; **+10.49 — fail** | 0.903; +1.01 — pass |
| **Development verdict (if all gates pass)** | | **NOT SUPPORTED** (P5) | **NOT SUPPORTED** (P1, P2) |

## 5a. Revision 2: conservative crop-only candidate (requested before opening H18)

The full-TEST result is evidence that the automatic timing / window-widening strategy is **not supported**: its BLEU-4
gain comes with longer outputs (length ratio 0.90 → 1.08) and a WER increase (+8.6, CI upper +10.5) that fails P5.
The candidate was therefore revised to the validated automatic signer crop with the ORIGINAL timing (B_crop_only),
with P1–P5 unchanged. No new arm was built and no search was run: all numbers come from the arms already decoded on the
T4 (§4). No conservative automatic-timing variant exists among the built arms (B_time_only and B_lag_only both use the
widened window), so no secondary timing candidate was evaluated.

Full TEST, 2,347 clips (paired 95% CIs vs A_old; gap = Old → oracle timing + auto crop):

| Arm | BLEU-4 | chrF | WER | Length ratio | Δ BLEU-4 | Δ chrF | Δ WER | Δ length | Gap recovery (BLEU-4) |
|---|---|---|---|---|---|---|---|---|---|
| A_old | 4.85 | 22.08 | 101.1 | 0.900 | | | | | |
| **B_crop_only (final)** | **5.24** | **22.56** | **100.9** | **0.903** | **+0.39 [0.17, 0.62]** | +0.48 [0.24, 0.73] | **−0.14 [−1.30, +1.01]** | +0.003 [−0.011, 0.018] | 4.7% |
| B_auto (revision 1) | 5.77 | 24.71 | 109.7 | 1.079 | +0.92 [0.49, 1.37] | +2.62 [2.18, 3.04] | +8.62 [6.77, 10.49] | +0.179 [0.156, 0.203] | 11.1% |
| O_time_crop (oracle timing + auto crop) | 13.15 | 32.97 | 87.2 | 0.951 | +8.30 [7.01, 9.62] | +10.89 [9.35, 12.46] | −13.89 [−16.21, −11.57] | +0.051 [0.033, 0.070] | 100% |

128-clip set (official oracle): B_crop_only +0.98 BLEU-4 [−0.18, 2.21], WER −2.12 [−6.07, +1.13]; C_official +3.67;
recovery 26.6% (B_auto 41.7%).

**Answer to the key question:** yes, the automatic crop gives a **clean** translation gain without the WER harm of the
automatic timing (BLEU-4 and chrF up with CIs above 0; WER and output length unchanged). But the gain is **small**
(+0.39 BLEU-4, below the pre-registered +0.5 minimum) and recovers only a few percent of the Old → Oracle gap, because
the gap is almost entirely timing. Under the unchanged criteria the final candidate's development verdict is
**NOT SUPPORTED** (P1, P2 fail; P3, P4, P5 pass).

## 6. Environment checks and cross-checks

- **Decoder equivalence Mac CPU vs T4 GPU (A_old, 128 clips):** 128/128 identical strings, identical metrics; T4
  0.88 s/clip (1 × 4) / 108 s wall for 128 clips (2 × 2, identical output). Across all 8 arms on the 128 set,
  1,021 / 1,024 Mac and T4 strings are identical (3 beam flips from CPU-vs-GPU float differences).
- **Mac numpy 2.2.6 pickles on T4 numpy 1.22.4:** `decode_dir.py` remaps the `numpy._core` module path; pkl content
  hashes identical 128/128 (`pkl_content_hash.py`).
- **G1 (development):** the 24 frozen G1 pkls decoded again on the T4 in a separate run: **24/24 identical**.
- **G2 (development):** 16 B_auto clips decoded a second time: **16/16 identical**.
- **T4 determinism:** the full-run A_old subset equals the earlier T4 equivalence run (128/128).
- **Mac CPU vs T4 GPU poses (15 videos, 41,818 frames):** person counts identical; keypoints median 0.22 px, 22% > 1 px.
  The cause is the FFmpeg build (decoded frames differ), so CPU and GPU poses are never mixed.

## 7. Caveats

- Thresholds P1–P5 were set during development, after the 128-set results and the first full-TEST B_auto vs A_old
  numbers were known; they were not tuned to pass, and they were **not changed** for revision 2 (both candidates are
  NOT SUPPORTED on dev).
- The switch to crop-only (revision 2) was made after seeing full-TEST translation results of all arms; the crop
  parameters themselves were tuned on box agreement only.
- Test translation results were already seen in P0-12 (128 benchmark). Tuning of timing and crop used only alignment
  targets, never translation metrics.
- 8 test clips have original windows too short to build (< 2 frames); excluded from the evaluable set.
- To confirm that every H18 unit is a single video (so the per-video bootstrap equals the P0-16 per-unit bootstrap),
  `H18_units.txt` was read once directly (outside `holdout_guard`). It contains VIDEO_IDs only; no frame, reference,
  timing row or output of H18 was read, and no id was printed.

## 8. Artifacts (outside the repo: `~/Desktop/curify/p018-work/dev/`)

`gpu_run/poses/` (184 npz + SUMMARY.json + logs), `gpu_run/C_official/` (128 pkls), `tune_gpu/` (interval + crop
tuning), `cond_gpu/` (all arm pkls, build_meta.json), `dec_t4/` (T4 predictions, decoder_env.json, G1/G2 checks),
`score_t4/final/` (DEV_COMPARISON.json, score_full.json, score_128.json; primary B_auto, revision 1),
`score_t4/final_crop/` (same scores, criteria for primary B_crop_only, revision 2). Mac-only cross-checks: `vid_all/`,
`dec_gpu/`, `score_gpu/`.
