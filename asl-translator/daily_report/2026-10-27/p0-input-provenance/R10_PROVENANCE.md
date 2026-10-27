# R10 input provenance — `fzNnTgHa1lM_2-5-rgb_front`

Task 2 Step 1 ([THREE_P0_EXECUTION_REPORT.md](../THREE_P0_EXECUTION_REPORT.md) 任务二): resolve R10 provenance before
same-domain sampling-quality evaluation.

## Evidence chain

| # | Link | Finding | Evidence |
|---|---|---|---|
| 1 | Source of 23.38–42.38 s | How2Sign test **original, speech-aligned** CSV `how2sign_test.csv` (sha256 `ecc73526…`), row `fzNnTgHa1lM_2` | §1 |
| 2 | Source of 31.03–56.34 s | How2Sign test **manually re-aligned** CSV (sha256 `d1799dcb…`). It reached the repo through `how2sign_v2` ("rescued via re-aligned-file timing") and from there P0-12/P0-A | §2 |
| 3 | Actual A interval | **31.04–56.38 s** (derived: B measurement + P0-12 B↔C offset of 4 frames, residual 0.0066 shoulder widths) | §3–4 |
| 4 | Actual B interval | **31.21–56.54 s** (measured: pixel match at source frame 749, motion r 0.994, next best outside ±5 frames 0.617) = re-aligned +4 frames | §4 |
| 5 | Pose frame count | 608 in both PKLs = 608 frames in each input video = 25.33 s at 24 fps (the original span would be ~456 frames) | §5 |
| 6 | Frames given to the model | 256 of 608, the same seeded indices in both domains (`frame_idx_sha256` `686f25cb…`) | §6 |
| 7 | Model-input hashes | Reproduced exactly in both domains: A `14aade5b…`, B `7ad6aa36…` = stored P0-A values | §7 |
| 8 | Conclusion | **23.38–42.38 s never entered Uni-Sign. Both domains received the re-aligned interval.** | §8 |

Status: `A_official` VERIFIED, `B_ours_5p39` MISMATCH.
- The MISMATCH is a **timing-label** mismatch: B is declared "How2Sign original timestamps" but is the re-aligned
  interval.
- It is **not** a reproducibility failure: the pose hashes, frame counts, selected indices and model-input hashes all
  reproduce.
- R14 has the same class of mismatch: its B input is 34.93–48.17 s, the re-aligned 35.25–48.53 shifted by −10 frames,
  not the original 26.19–36.11.
- Therefore R10's (and R14's) old/B input must not be described as "original timing".

**Conclusion.** Neither Uni-Sign input for R10 came from 23.38–42.38 s. Both are the **re-aligned interval
(31.03–56.34 s)**, measured in the source video:

| Domain | Interval Uni-Sign saw | Status |
|---|---|---|
| Official preprocessing (`A_official`) | **31.04–56.38 s** (within 0.04 s of the annotation) | **VERIFIED** (declared realigned, matches realigned) |
| Old preprocessing (`B_ours_5p39`) | **31.21–56.54 s**, the same interval delayed by 4 frames | **MISMATCH** (declared "How2Sign original timestamps"; actually the realigned interval +4 frames) |

Uni-Sign received 256 of the 608 frames in each domain. The indices are the same in both domains, and the
model-input hash reproduces exactly.

Source video: `raw_videos/fzNnTgHa1lM-5-rgb_front.mp4` (How2Sign test), 1280×720, 24 fps, 2,107 frames, sha256
`df24c8fb…5b232f`. All times are source-video seconds. Evidence: `input_manifest_45.csv` (rows R10),
`selected_frames.jsonl`, `work/located_clips.json`, `work/sampling.jsonl`.

## 1. Where does 23.38–42.38 come from?

The **How2Sign test "English Translation (original)" CSV**: `how2sign_test.csv`, sha256 `ecc73526…`, row
`fzNnTgHa1lM_2`, START 23.38, END 42.38.

- These are the original **speech-aligned** sentence times. P0-18 downloaded this file, which is how it entered the
  P0-C case sheet.
- No repo code used this interval to cut or select R10's input.

## 2. Where does 31.03–56.34 come from?

The **How2Sign test "English Translation (manually re-aligned)" CSV**: `how2sign_realigned_test.csv`, sha256
`d1799dcb…`, START_REALIGNED 31.03, END_REALIGNED 56.34. It reached the repo in two places:

- **`how2sign_v2`.** Its builder checked each clip's physical duration against the original CSV.
  - R10's clip is 25.33 s long, against 19.00 s in the original CSV, so it failed that check.
  - It matched the re-aligned CSV within 0.05 s (`validation/replacement_audit.json`: "RESCUED via re-aligned-file
    timing").
  - So `source_metadata/how2sign_test_realigned_subset_v2.tsv` (sha256 `7a76d34e…`) carries 31.03–56.34.
- **P0-12 `segment_alignment_128.json`.** It took its `ours_start/ours_end` from that v2 TSV.
  - P0-A `case_provenance.csv` copied those values into its `orig_start/orig_end` columns.
  - **So for R10 (and R14) the "orig" columns hold re-aligned times.** That is why P0-A recorded IoU 1.00.

## 3. Which code path generated the pose PKLs Uni-Sign used?

No repo code chose R10's interval in either domain. Both inputs are pre-cut clips made by the dataset or model
authors:

- **`A_official`.** The official Uni-Sign How2Sign pose release: HF `ZechengLi19/Uni-Sign`
  `how2sign_pose_format.zip`, entry `test-pose-rtmpose-192/fzNnTgHa1lM_2-5-rgb_front.pkl`.
  - Fetched by P0-12 `fetch_entries.py` (CRC-verified) and re-pickled content-identically by `make_condition_dirs.py`.
  - The Uni-Sign authors extracted it from the official crop clip `crop_test/fzNnTgHa1lM_2-5-rgb_front.mp4`
    (480×562, 24 fps, 608 frames per P0-12 `official_crop_ffprobe.csv`).
  - PKL sha256 `9ff6ba1b…0f8c`.
- **`B_ours_5p39`.** P0-12 `extract_rtmlib_lightweight.py` (rtmlib 0.0.13, YOLOX-tiny + RTMW, CPU), run on every frame
  of `how2sign_v2/videos/fzNnTgHa1lM_2-5-rgb_front.mp4`.
  - That file is the How2Sign "Green Screen RGB clips (frontal view)" archive clip
    (`test_rgb_front_clips.zip:raw_videos/fzNnTgHa1lM_2-5-rgb_front.mp4`), copied unchanged: sha256 `f1887acb…`,
    equal to the `how2sign_v2` manifest and the 10.18 inspection-sheet video.
  - PKL sha256 `1ae8a43b…49df`.

## 4. Which exact interval does each PKL correspond to?

**B (measured directly).** The archive clip was located inside the raw source by pixel matching (method:
`INPUT_PROVENANCE_PLAN.md`, Amendment 1):

| Candidate start | Source frame | Motion-signature r | Normalized MAE |
|---|---|---|---|
| **Best match** | **749 (31.208 s)** | **0.994** | **0.031** |
| Re-aligned annotation, 31.03 s | 745 | 0.697 | 0.058 |
| Original annotation, 23.38 s | 561 | 0.090 | 0.180 |
| Best offset outside ±5 frames of the winner | — | 0.617 | — |
| Median over all offsets | — | — | 0.204 |

B slice = frames 749–1356 = **31.208–56.542 s**.

**A (derived).** The P0-12 cross-frame alignment of B against C (rtmlib on the same official crop clip as A) gives
C index = B index + 4:
- residual 0.0066 body and 0.0082 hands, in shoulder widths, over 604 frames;
- so A frame 0 = B frame −4;
- A slice = **31.042–56.375 s**: Δ vs re-aligned +0.012 / +0.035 s; Δ vs original +7.66 / +14.00 s.

## 5. Is the pose frame count consistent with that interval?

Yes.
- Both PKLs have **608 frames**: 25.33 s at 24 fps.
- They equal their input videos: the B clip has 608 decoded frames, and the A official crop has 608 frames.
- The re-aligned span is 25.31 s, about 607 frames. The original span would be 19.00 s, about 456 frames.
- The PKLs have no `start`/`end` keys, so frame *i* is at slice start + *i*/24 s.

## 6. With more than 256 frames, which 256 were selected?

Upstream `S2T_Dataset.load_pose` (Uni-Sign `eed438bc`, `max_length=256`) draws
`sorted(random.sample(range(608), 256))` after `random.seed(1358842863)` = `int(sha256(clip_id)[:8], 16)`.

- The same 256 indices are used in both domains: 352 frames dropped, largest gap 12 frames (0.5 s).
- They start `0, 2, 4, 6, 10, 12, 16, 17, 20, 22, 28, 29, …` and end at 607.
- `frame_idx_sha256` = `686f25cb…97e3`. The full list is in `selected_frames.jsonl`.
- Selected timestamps:
  - A: 31.042 → 56.333 s (sha256 `b99e8402…`);
  - B: 31.208 → 56.500 s (sha256 `57dd2189…`).

## 7. Can the stored model-input hash be reproduced?

Yes, in both domains. `reproduce_sampling.py` re-ran upstream `load_pose` on CPU, with no model. It recomputed the
hash of the exact keypoint tensor Uni-Sign received:

- `A_official`: `14aade5b…837f` = stored P0-A value;
- `B_ours_5p39`: `7ad6aa36…0fc1` = stored P0-A value.

The `frame_idx_sha256` values also match.

## 8. Which timestamp range actually entered Uni-Sign?

| Domain | Interval Uni-Sign saw | Matches |
|---|---|---|
| A_official | 31.04–56.38 s (256 of 608 frames) | Re-aligned 31.03–56.34 |
| B_ours_5p39 | 31.21–56.54 s (256 of 608 frames) | Re-aligned +4 frames (Δ +0.18 / +0.20 s). **Not** the original 23.38–42.38 |

The 23.38–42.38 interval never entered Uni-Sign. The "timing conflict" in the P0-C case sheet is between annotation
files, not between model inputs.

## 9. The boss's R10 diagnostic region (5–16 s) in source time

The boss's sampling report counts frames in R10's "5–16 秒诊断区间" (random 111, uniform 111, coverage_motion 69 of
256). These times are clip-relative on the compressed OLD display video.

| Frame of reference | Span | Basis |
|---|---|---|
| Display / B clip | 5.00–16.00 s = frames 120–384 | Display PTS = index / 24 for all 608 frames. The boss's three counts reproduce exactly with indices 120–384 |
| Source video | frames 869–1133 = **≈ 36.2–47.2 s** | B start = source frame 749 (§4) |
| A clip | ≈ 5.17–16.17 s | A frame 0 = B frame −4 |

**Precision.** The B start is measured to ±1 source frame (≈ ±0.04 s), so the source bounds are good to about
±0.05 s. That holds only if the display video is a frame-for-frame re-encode of the B clip (sha256 `c0b43d9a…` vs
`f1887acb…`).
- That is supported: same 608 frames, same 24 fps, and the boss's random-arm indices equal ours.
- It is **not pixel-verified**: the display file is not on this machine.

The region is a diagnostic slice, not a signing or information label.

## Consequences (recorded, nothing changed)

- `B_ours_5p39` is documented everywhere as "How2Sign original timestamps". For R10 (and R14), that is false: its
  clip is the re-aligned interval, shifted by a few frames.
- P0-A `case_provenance.csv` and P0-12 `segment_alignment_128.json` label re-aligned times as "orig/ours" for these
  two clips. That is a labeling issue only: the stored values describe the real input to within a few frames.
- The P0-C R10 blocker "resolve the timing-source conflict" is answered.
  - The model saw 31.04–56.54 s; 23.38 s is never part of the input.
  - The rest-span labelling still needs a human.
  - `CASE_SHEET.md` and `case_inputs.csv` are not edited here.
