# P0-12 — Pose-level diagnostics (no translation inference)

Three pose sources for the same 128 clip IDs:

| Source | What it is | Segment | Frame | Extractor |
|---|---|---|---|---|
| **A** `A_official_pkl` | official Uni-Sign pkl (`test-pose-rtmpose-192/`, range-fetched from HF, CRC-verified) | re-aligned | official crop | official ("RTMPose", MMPose) |
| **B** `B_rtmlib_lightweight_fullframe` | **our 5.39 pose input**, re-extracted (rtmlib 0.0.13 lightweight, same ONNX files) | original | 1280×720 | rtmlib YOLOX-tiny + RTMW-dw-l-m 256×192 |
| **C** `C_rtmlib_lightweight_officialcrop` | same extractor as B, run on the official crop videos (`crop_test/*.mp4`, range-fetched, CRC-verified) | re-aligned | official crop | rtmlib (as B) |

Model-input statistics use Uni-Sign's own `load_part_kp`/`crop_scale` (copied verbatim from `datasets.py:18-104`),
with a 0.3 confidence threshold. Per-clip values are in `pose_diagnostics.csv` (384 rows = 128 × 3) and aggregates in
`data/pose_diagnostics_aggregate.json`. Script: `scripts/pose_diagnostics.py`.

## 1. B reproduces our 5.39 input

All **128/128** re-extracted B sequences have exactly the frame count logged for that clip in the historical
5.39 run (`per_clip_results.csv` `n_frames`). Same rtmlib version, same ONNX files, same `kp/(W,H)` code. B is
therefore taken as the 5.39 pose input. This is a frame-count check plus code identity, not a byte-level check:
the historical in-memory poses were never saved.

## 2. Extractor model: A vs C on identical frames (clean V3 test)

A and C come from the **same official crop videos**: frame counts equal on 128/128 clips, and stored `w_h` equal on
128/128. The only difference is the pose model/detector.

| Part | Median keypoint distance / shoulder width (per-clip median, then median over clips) | p90 clip | worst clip | Visibility disagreement (one source > 0.3, the other ≤ 0.3) |
|---|---|---|---|---|
| Body (9) | **0.85 %** | 0.97 % | 1.14 % | 0.0 % |
| Left hand (21) | **1.53 %** | 1.99 % | 2.57 % | 0.0 % |
| Right hand (21) | **1.68 %** | 2.10 % | 2.51 % | 0.0 % |
| Face (18) | **0.63 %** | — | — | 0.0 % |

At a typical crop scale this is a few pixels. All other statistics also match (table §4). **At keypoint level,
the official How2Sign poses and rtmlib-lightweight output are close to interchangeable.** That fits the official
directory name `rtmpose-192` (a 256×192 model like ours) better than the paper's RTMPose-x. The exact official model
identity is still not established, and keypoint closeness does not prove equal translation quality. That needs the
A vs C inference run.

## 3. Geometry: what the model actually sees (V2)

Uni-Sign divides x by W and y by H **separately** before an isotropic body-bbox rescale. So the frame aspect changes
the shape of the normalized skeleton.

| Model-input statistic (median over 128 clips) | A official | **B ours (5.39)** | C | B_aspect (B re-normalized with each clip's official (W,H)) |
|---|---|---|---|---|
| Frame H/W fed to `kp/(W,H)` | 1.230 | **0.5625** | 1.230 | 1.230 (by construction) |
| Shoulder width / neck height | 2.055 | **0.902** | 2.056 | 2.014 |
| Body scale (`crop_scale`, normalized units) | 0.857 | **0.548** | 0.858 | 0.853 |

In our 5.39 input, horizontal body extents are ~0.44× what the checkpoint saw in training (0.902 / 2.055). Hands and
face are divided by the body scale, so their relative shape is distorted in the same way. B_aspect undoes this
**without changing a single frame or keypoint detection** (same 25,031 frames as B). That makes it a clean
single-variable condition for the GPU run.

## 4. Other pose statistics (means over clips unless noted)

| Metric | A | B | C |
|---|---|---|---|
| Clips | 128 | 128 | 128 |
| Total frames | 29,113 | 25,031 | 29,113 |
| Median frames / clip | 161 | 127 | 161 |
| Clips > 256 frames (random-subsampled) | 36 | 34 | 36 |
| Frames with 0 persons | 0 | 0 | 0 |
| Frames with >1 person (person 0 used) | 0 (always 1 stored) | 0.008 / clip (1 clip, 1 frame) | 0.055 / clip (6 clips, ≤2 frames each) |
| Body / L-hand / R-hand / face missing rate (score ≤ 0.3) | 0.0 / 0.0 / 0.0001 / 0.0 | 0.0 / 0.0 / 0.0 / 0.0 | 0.0 / 0.0002 / 0.0 / 0.0 |
| Frames with a whole hand absent | 0.0 | 0.0 | 0.0 |
| Mean confidence body / L / R / face | 1.028 / 0.874 / 0.868 / 1.032 | 1.070 / 0.879 / 0.863 / 1.042 | 1.049 / 0.875 / 0.862 / 1.035 |
| Confidence p50 / p95 / max (median over clips) | 1.021 / 1.077 / 1.125 | 1.027 / 1.083 / 1.199 | 1.021 / 1.077 / 1.188 |
| Hand jitter, L / R (median 2nd difference, model units) | 0.0093 / 0.0135 | 0.0093 / 0.0139 | 0.0111 / 0.0161 |
| Fraction of model-input entries zeroed by threshold | 0.0 | 0.0 | 0.0001 |
| Keypoint ordering / tensor shape | COCO-WholeBody 133; parts (T,9/21/21/18,3) | same | same |

Confidence scales are the same family (SimCC, ~1.0), so the 0.3 threshold behaves identically. **Missing joints,
confidence handling and temporal smoothness do not distinguish our pose input from the official one.** C is
slightly jitterier than A (+~20%), but B is not jitterier than A.

## 5. Frame alignment / sequence length (V1)

B covers different time windows than A/C. Our clips use How2Sign *original* timestamps, and the official ones use
*re-aligned* timestamps (`OFFICIAL_VS_CURRENT_PIPELINE.md`). Official/ours frame-count ratio: 0.17–2.46, median 1.09,
only 5/128 equal. Temporal IoU with the re-aligned window: median 0.555; **28/128 = 0**. So frames cannot be
matched one-to-one between B and A, and B vs A pose differences mix all three variables. That is why C and B_aspect
exist.

## 5b. Same moments, different cut: B vs C where the windows overlap

On the **100 clips** where our window and the re-aligned window overlap, each B frame was matched to the C frame
showing the same absolute timestamp. A per-clip affine map from B (full-frame pixels) to C (crop pixels) was then
fitted, searching ±12 frames around the timestamp prediction (`scripts/crossframe_alignment.py`,
`data/crossframe_alignment_B_vs_C.json`).

| Result | Value | Meaning |
|---|---|---|
| Best frame offset within ±1 frame of the timestamp prediction | **95 / 100** clips (±3: 96; median 0) | the official crop clips are the same footage, cut at the re-aligned timestamps. The timing difference is fully explained by the two timestamp files |
| Fitted scale / x:y ratio | 1.001 / 1.003 | the official crop is a pure crop (no resize) of the same 1280×720 video |
| Residual after the fit / shoulder width | body **0.70 %** (p90 0.94 %), hands **1.05 %** (p90 1.33 %) | running the same extractor on the crop instead of the full frame barely changes keypoints, even less than the extractor swap (§2) |

Consequence for the design: Uni-Sign's normalization ignores translation, so B_aspect and C give
practically the same model input on shared moments. They differ in **which moments are included**. That makes
C − B_aspect a clean timestamp-alignment (V1) contrast.

## 6. What these diagnostics do and do not show

- They **do** show the four variables are separable and of very different size at the input level:
  - **V1 timestamp alignment:** large. 28/128 clips share no frames with the signed window.
  - **V2 crop / normalization:** large and systematic. Model-input width ~0.44×.
  - **V3 extractor model:** small. ~1–2 % of shoulder width on identical frames.
  - **Crop pixels vs full frame for the same extractor:** smaller still (0.7–1 %).
  - **V4 runtime:** not observable at pose level.
- They **do not** show how any of these differences changes BLEU. Pose statistics alone say nothing about
  semantic impact. That requires the GPU run in `scripts/run_p012_gpu.sh`.
