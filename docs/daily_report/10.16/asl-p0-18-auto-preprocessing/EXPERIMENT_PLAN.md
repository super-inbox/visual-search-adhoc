# P0-18: Automatic preprocessing (signing interval + signer crop) for Uni-Sign — Experiment Plan

**Date:** 2026-10-19 · **Status: PLAN, frozen in `FREEZE.json` before H18 is opened.** Not committed.

**Revision 2 (2026-10-19, before H18):** the primary candidate is **B_crop_only (original timing + automatic signer
crop)**, set in `config/p018_config.json → primary_arm`. The full-TEST development result showed that the automatic
timing (window widening) raises WER beyond the P5 do-no-harm bound, so the automatic-timing strategy is not supported
and is kept only as a descriptive arm. Thresholds P1–P5, the verdict table, the gates, the environments and all
tuned parameters are unchanged; no new search was run (`DEVELOPMENT_RESULTS.md` §5–§6).
Protocol: P0-16 (`../asl-p0-16-experimental-credibility/`: `HOLDOUT_PLAN.md`, `SANITY_GATE_POLICY.md`,
`EXPERIMENT_PROTOCOL.md`). Development evidence: `DEVELOPMENT_RESULTS.md`.

## 1. Question

> Without any oracle information (no re-aligned timestamps, no official crops), can an automatic, pose-only
> preprocessing step make Uni-Sign translate raw How2Sign videos better than the current pipeline (original
> timestamps, full frame), and how much of the gap to the official preprocessing does it close?

P0-12 showed that most of Uni-Sign's gap on our inputs comes from preprocessing: clips cut at the original (speech)
timestamps instead of the re-aligned (signing) ones, and full frames instead of signer crops.

## 2. Data

| Role | Data | Use |
|---|---|---|
| Development (tuning + comparison) | How2Sign **test**: 2,357 clips, 184 videos (raw videos from `test_raw_videos.zip`, sha256 `3755f06d…`) | everything in `DEVELOPMENT_RESULTS.md` |
| Dev oracle arm | 128 test clips (one per video, the P0-12 benchmark) with official crop videos (Uni-Sign HF archive, revision `eab251b7…`) | C_official reference, crop-box oracle |
| **Confirmatory (one shot)** | **H18** (P0-16): 814 val clips, 57 videos (57 single-video units) | this plan, §6–§9 |
| Sealed | H19 (829 val clips, 58 videos) | not touched by P0-18 |

Every development script calls the P0-16 `holdout_guard.assert_not_holdout` on its clip ids. No val frame, reference,
timing row or model output is read before `RUN_LOCK.json` exists.

## 3. The automatic pipelines (frozen: `config/p018_config.json` → `interval`, `crop`; code `p018_lib.py`, `pipeline.py`)

**Primary candidate (B_crop_only):** steps 1, 2, 4 and 5 below over the ORIGINAL window (no automatic timing).
Step 3 (automatic interval) is used only by the descriptive automatic-timing arms (B_auto, B_time_only, B_lag_only).

Input: the raw video and the ORIGINAL timing of the video's sentences (VIDEO_ID, VIDEO_NAME, SENTENCE_NAME, START, END;
no text column is read).

1. **Pose:** full-frame RTMPose (rtmlib 0.0.13 Wholebody lightweight: YOLOX-tiny `ceb11c07…` + RTMW-dw-l-m 256×192
   `68db326c…`) on every frame of the video, in the canonical pose environment (§5).
2. **Signer track:** per frame, the person with the largest confident upper-body box (continuity tie-break).
3. **Signing interval:** per-frame activity score (hand height + wrist speed, normalised by shoulder width,
   smoothed 0.2 s, valid-hand gate 0.3), hysteresis 0.55 / 0.25, gaps ≤ 0.6 s filled, runs < 0.3 s dropped.
   Expected window = [orig.start + 0.5 s, orig.end + 2.0 s] (min 1 s); each bound snapped to the nearest activity
   onset / offset within ±2.0 s. The per-video lag / linear-warp estimator is part of the code but disabled by the
   tuned margins (identity warp; dev CV showed it hurts).
4. **Signer crop:** static clip-level box from the 1st / 99th percentiles of confident body + hand keypoints over the
   clip's window (original window for the primary candidate), ± 0.25 shoulder widths horizontally, 0.5 shoulder widths above, down to the frame bottom.
5. **Uni-Sign input:** the signer track over the window, keypoints relative to the crop, divided by its W, H.

Tuning used **alignment-level targets only**: interval IoU vs the re-aligned window (`tune_interval.py`, 5-fold CV
grouped by VIDEO_ID, all 2,357 test clips) and box IoU vs the official crop box (`tune_crop.py`, 128 clips).
No translation metric was used to choose any parameter.

**Failure** (P3, for the primary arm; `pipeline.clip_failed(rec, m, primary_arm)`): the arm's condition cannot be built
(< 2 frames) or its crop falls back to the full frame; for an arm with automatic timing, also an interval-detector
failure (no shoulders / no activity in the interval / degenerate after snapping).

## 4. Arms

| Arm | Timing | Crop | Role |
|---|---|---|---|
| **A_old** | original | full frame | the current pipeline (baseline) |
| **B_crop_only** | original | automatic | **the P0-18 candidate (primary arm)** |
| **C_official** | re-aligned (official clip video) | official crop, posed with our extractor (P0-12 condition C) | oracle reference arm (P0-16 HOLDOUT_PLAN §6) |
| B_time_only | automatic (widened) | full frame | descriptive: timing contribution |
| B_auto | automatic (widened) | automatic | descriptive: the revision-1 candidate (automatic timing + crop) |
| B_lag_only | automatic, no activity snapping | automatic | descriptive |

All arms are decoded by the frozen Uni-Sign (`how2sign_pose_only_slt.pth` `1bfd5f33…`, beam 4, max_new_tokens 100,
fp32, batch 1, per-clip frame-sampling seed) in the canonical decoder environment (§5).

## 5. Frozen environments (P0-18 canonical: T4 VM `baobao-training-t4`)

- **Pose:** conda `p018-pose`: onnxruntime-gpu 1.23.2 (CUDA 12.9 / cuDNN 9.27 pip wheels), CUDAExecutionProvider
  with `cudnn_conv_algo_search = HEURISTIC`, `use_deterministic_compute = True`, per-frame inference, 4 worker threads,
  chunk 256; opencv 4.10.0 with FFmpeg avcodec 59.37; numpy 1.22.4; driver 580.178.04. The run fails if ONNX Runtime
  is not on CUDA (no silent CPU fallback). Videos are range-fetched from the pinned mirror revision and must reproduce
  the SHA-256 of the member in the locally verified archive. Record: `config/p018_config.json → pose_env`.
- **Decoder:** conda `unisign`: Python 3.9.25, torch 2.1.1+cu121 (CUDA 12.1, cuDNN 8902), transformers 4.40.0,
  numpy 1.22.4, Uni-Sign `eed438bc` (tracked-file content sha256 `890edc73…`), checkpoint `1bfd5f33…`, mT5-base file
  hashes recorded, 2 processes × 2 threads, cuda. Record: `config/p018_config.json → decode_env`.
- Condition building and scoring run on the Mac (numpy 2.2.6; sacrebleu 2.2.0; Uni-Sign SLRT_metrics).

The Mac-CPU pose and decode outputs from earlier development are cross-checks only and are not part of any P0-18 result.

## 6. One-shot H18 run (`scripts/run_h18_oneshot.py --mode h18 --confirm OPEN-H18`)

Order (nothing from val is read before step 2): verify FREEZE + P0-16 holdout hashes + every input's SHA-256 → write
`RUN_LOCK.json` → H18 target list (asserted disjoint from H19 / EXCLUDED, 814 clips / 57 videos) → original timing of
the target videos → poses on the T4 → arms A_old, B_auto, B_time_only, B_crop_only, B_lag_only (Mac) → C_official
(official val crops, T4) → decoding of the 6 arms (T4) → gates → references (re-aligned val CSV, SENTENCE) → scoring →
criteria → verdict → `RESULT.json`. A run is never repeated; `--resume` only continues an interrupted run under the same
lock and FREEZE (infrastructure failures only).

Evaluable clips: target clips for which every arm was built. Missing clips are reported with a reason.

## 7. Sanity gates (any FAIL → VOID)

| Gate | PASS condition |
|---|---|
| **G1 environment reproduction** | (a) the frozen 24 development pkls (`ref/g1/`) decoded now on the T4 give **identical** strings to the frozen predictions; (b) re-extracting the frozen dev video `_fZbAxSSbX4-5-rgb_front` on the T4 gives pose arrays sha256 `b796a84f…`; (c) every pose-extractor environment record of the run equals the frozen `pose_env`; (d) the decoder environment record equals the frozen `decode_env` |
| **G2 decode determinism** | 16 primary-arm clips (sha256 order) decoded a second time give identical strings |
| **G3 integrity** | FREEZE and input hashes verified; only target clips processed; input-missing rate ≤ 5%; all arms complete; sampled pkl sha256 = the decoded `pose_sha256` |

## 8. Criteria and verdict (`p018_verdict.py`; thresholds in `config/p018_config.json → thresholds`)

Primary endpoint: corpus BLEU-4 (Uni-Sign `sableu`, 13a). CIs: paired bootstrap over H18 units (= source videos),
B = 2,000, seed 20261016.

| Criterion | Definition | Threshold |
|---|---|---|
| **P1 improvement** | Δ BLEU-4 (primary − A_old) ≥ min **and** 95% CI lower bound > 0 | min = **+0.5** |
| **P2 gap recovery** | gap = BLEU-4(C_official) − BLEU-4(A_old) ≥ 1.0 **and** (primary − A_old) / gap ≥ min | min = **0.33** |
| **P3 reliability** | automatic-pipeline failure rate | ≤ **5%** |
| **P4 cost** | preprocessing seconds per clip (pose extraction of the needed videos on the T4 + condition building) | ≤ **15 s** |
| **P5 do no harm** | primary length ratio in [0.8, 1.2] **and** 95% CI upper bound of Δ WER (primary − A_old) | ≤ **+5.0** WER points |

**Verdict table** (complete; implemented as a lookup in `p018_verdict.RULES`, checked by `test_p018_verdict.py` over
all 2³ × 2⁵ = 256 combinations):

| Gates | Criteria | Verdict |
|---|---|---|
| any gate FAIL | any | **VOID** |
| all PASS | P1, P2, P3, P4, P5 all true | **SUPPORTED** |
| all PASS | P1, P3, P4, P5 true, P2 false | **PARTIAL** (improves on the old pipeline, recovers less of the oracle gap than pre-registered) |
| all PASS | any other combination | **NOT SUPPORTED** |

Descriptive arms (B_auto, B_time_only, B_lag_only), chrF and per-clip analyses are **descriptive** and do not enter
the verdict.

## 9. Reporting

`RESULT.json` (verdict, gates with details, criteria, every point estimate and paired delta), then a written H18 report.
VOID results report numbers only in an appendix headed "descriptive, uninterpretable: sanity gate failed".
After H18 is opened it becomes validation-used (P0-16 §6); H19 stays sealed for P0-19.
