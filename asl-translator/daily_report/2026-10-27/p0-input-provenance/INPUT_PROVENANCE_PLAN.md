# P0-1 input provenance: plan and frozen rules (2026-10-27)

**Written before any measurement in this folder.** The rules below are not changed after results are seen. Any
amendment is a dated section appended *before* the step it affects.

## Question

For the exact 45-case inspection-sheet set (R01–R45, `docs/daily_report/10.18/asl-review-inspection-sheet/`), which
source-video interval actually entered Uni-Sign in each preprocessing domain, and in which order of frames?

The domains are not collapsed. There is one row per `review_id × domain`, giving 90 rows:

| Domain | Pose input (P0-12 `prepared_inputs/<domain>/test-pose-rtmpose-192/<clip>.pkl`) | Declared timing (P0-12 `MANIFEST.csv`) |
|---|---|---|
| `A_official` | Official Uni-Sign How2Sign test poses (HF `how2sign_pose_format.zip`), extracted from the official crop clip | re-aligned |
| `B_ours_5p39` | rtmlib-lite on every frame of our frozen `how2sign_v2/videos/<clip>.mp4` (full frame) | How2Sign original |

## Constraints

- No model decode.
- CPU only.
- No H18/H19 or val material. The holdout guard runs on all IDs, and only `test_raw_videos.zip` and the test CSVs
  are read.
- Nothing is fixed or overwritten. Historical artifacts are read only.
- Raw videos are extracted to a temporary scratch folder, one at a time, and deleted after use. They are never
  committed.

## Evidence chain per row

1. **Pose integrity.**
   - PKL sha256 equals P0-12 `CHECKSUMS.sha256`, and the `pose_sha256` stored in P0-A `candidates.jsonl` for the
     domain.
   - Pose frame count equals the frame count of the video the poses were extracted from:
     - B: `ffprobe -count_frames` on the clip.
     - A: the official crop-clip frame count in P0-12 `data/official_crop_ffprobe.csv`.
2. **Actual slice in the source video.**
   - **B (direct measurement).** Locate the clip inside the raw source video (`test_raw_videos.zip`) by pixel
     matching:
     - grayscale 64×36 thumbnails of every raw frame and every clip frame;
     - best frame offset by mean absolute difference over 32 evenly spaced clip frames;
     - uniqueness check: the best offset outside ±5 frames of the winner.
     - Slice = `[offset/fps_raw, (offset + n_clip_frames)/fps_raw]`.
   - **A (derived).**
     - The official crop clip is not stored locally.
     - A's poses are frame-identical to P0-12 condition C (rtmlib on the same official crop clip; P0-12 V3: equal
       frame counts and `w_h`).
     - P0-12 `crossframe_alignment_B_vs_C.json` gives the frame offset between B and C (C index = B index + shift
       + off, with shift = round((ours_start − realigned_start)·fps) as in that script).
     - A slice start = B measured start − (shift + off)/fps; end = start + n_A/fps.
     - Available only where B and A overlap in time. Otherwise the A row is UNRESOLVED, and no fetch or extraction is
       done here.
3. **Annotation provenance.** Original and realigned start/end from the How2Sign test CSVs (both hashed). Also
   recorded: the repo `how2sign_v2` subset TSV each clip's timing was taken from, and the P0-A
   `case_provenance.csv` values.
4. **Sampling.**
   - Reproduce upstream Uni-Sign `S2T_Dataset.load_pose` (commit `eed438bc`, `max_length=256`) on CPU in
     `unisign-cpu-arm64`.
   - The seed is `random.seed(int(sha256(clip_id)[:8], 16))`, exactly as the P0-A decoder.
   - Recompute `frame_idx_sha256` and `kps_sha256` (model-input keypoint tensor hash) and compare with P0-A
     `candidates.jsonl`.
   - Selected timestamps = slice start + index / fps.

## Frozen status rules

A row is **VERIFIED** only if all of these hold:
- (a) the pose sha256 matches both stored hashes;
- (b) the pose frame count equals its source video's frame count;
- (c) the actual slice is measured (B: unique match with best MAE ≤ 6.0 and second-best MAE ≥ 2 × best; A: B row
  measured and the P0-12 alignment `resid_body` ≤ 0.02 shoulder widths);
- (d) the reproduced `frame_idx_sha256` and `kps_sha256` equal the stored P0-A values;
- (e) the slice matches the domain's **declared** timing source within **0.20 s** at both start and end.

The row is **MISMATCH** if (a)–(d) hold and the slice is determined, but (e) fails:
- the slice disagrees with the declared timing source;
- the note records which annotation, if any, it does match within 0.20 s.

The row is **MISMATCH** if any stored hash disagrees with a reproduced one (a or d).

The row is **UNRESOLVED** if the slice cannot be determined:
- no unique pixel match;
- no B↔C alignment;
- frame counts that cannot be reconciled.

A case's overall status is the worse of its two rows, ordered UNRESOLVED > MISMATCH > VERIFIED.

## Outputs

- `input_manifest_45.csv`: 90 rows.
- `selected_frames.jsonl`: full selected index and timestamp lists per row. The CSV carries counts, first/last and
  hashes.
- `provenance_summary.json`
- `R10_PROVENANCE.md`
- `README.md`
- `scripts/`:
  - `locate_clips.py` (B pixel match);
  - `reproduce_sampling.py` (upstream `load_pose`, unisign env);
  - `build_input_manifest.py`;
  - `verify_input_manifest.py`.

## Amendment 1 (2026-10-27, after the R10/R14 pilot, before the other 43 cases were measured)

**Pilot result.** On R10 and R14 the frozen raw-intensity match did not meet the uniqueness rule:
- R10: best MAE 7.19 vs 9.09 outside ±5 frames;
- R14: 7.11 vs 10.56.

**Cause.** A global brightness difference between the How2Sign clip-archive encode and the raw video (R10 mean
146.0 vs 138.4). It puts a ~7-unit floor under every offset. The rule as written could never pass on these files.
This is a method defect, not a data finding.

**Replacement match (applies to all 45 cases, R10/R14 re-run with it):**

1. **Normalized MAE.**
   - Each 64×36 thumbnail is z-normalized per frame (subtract the mean, divide by the std).
   - The MAE is taken over 64 evenly spaced clip frames.
2. **Motion signature.**
   - Pearson correlation between the per-frame mean |Δ| motion energy of the clip and of the raw window, over all
     clip frames.
3. **Unique match.** All three must hold:
   - the two methods agree on the best offset within ±1 frame;
   - motion r_best ≥ 0.90;
   - r_best − (best r outside ±5 frames) ≥ 0.20.
   - Otherwise the B slice is UNRESOLVED.
4. **Unchanged:** the raw-intensity MAE is still recorded for transparency, and rules (a), (b), (d) and (e) and the
   0.20 s tolerance are unchanged.

## Amendment 2 (2026-10-27, Task 2 Step 2, written before any Step 2 download or measurement)

**Scope.** Only the 19 rows that are UNRESOLVED after Amendment 1:
- 14 `A_official` rows: R09, R15, R21, R22, R26, R28, R29, R32, R35, R36, R39, R40, R42, R45;
- 5 `B_ours_5p39` rows: R09, R22, R29, R32, R39.

Rows already VERIFIED or MISMATCH keep their Amendment 1 evidence and status. R10/R14 are not re-measured.

**Why it is needed.**
- A: the derived path (B start + P0-12 B↔C offset) cannot reach 14 rows. In 9 of them the A and B windows do not
  overlap. In 2 the B↔C residual is too high. In the remaining 5 the B row is itself UNRESOLVED (R32 also lacks overlap).
  The only direct evidence is the official crop clip, which is not stored locally.
- B: the 5 rows fail only the motion-margin test. Scalar full-frame motion energy says *how much* moves, not *where*,
  so a repeated gesture produces near-duplicate signatures. A signature that separates left/right and high/low motion
  in the signer region addresses exactly this failure without touching any threshold.

**Unchanged:** Amendment 1, rules (a), (b), (d), (e), the 0.20 s tolerance, and the "worse of two rows" case rule.
Reference text is never used to locate an interval.

### A2.1 Official crop retrieval (A rows)

- Source: the same release P0-12 already used: HF `ZechengLi19/Uni-Sign`, `how2sign_rgb_format.zip.*` (split zip),
  entry `crop_test/<clip>.mp4`, addressed by P0-12 `data/official_rgb_index_128.json`.
- Range-fetch with the P0-12 `fetch_entries.py` logic (local-header parse, inflate, CRC32 against the zip central
  directory). Only the 14 entries above are fetched.
- Record the HF repo commit (`X-Repo-Commit` header), part URL, byte range, size, CRC32 and sha256.
- The fetched clip must match P0-12 `official_crop_ffprobe.csv` (w_h, fps, frame count) and the A pose frame count.
  Otherwise the row stays UNRESOLVED.
- Clips live in scratch only and are never committed.

### A2.2 Crop-box localization (spatial, A rows only)

- Gray frames at half resolution (raw 640×360; crop clip scaled ×0.5).
- Template: mean of all crop-clip frames. Search image: mean of raw frames sampled at 2 fps over the whole raw video.
- Zero-mean normalized cross-correlation (NCC) at every integer position with the template fully inside. Scale is
  fixed at 1.0 (the crop is assumed to be an unscaled pixel crop).
- **Box accepted** if NCC_best ≥ 0.70 **and** the best NCC more than 8 half-res px (16 px full-res) from the winner is
  ≤ NCC_best − 0.05. Otherwise the A row stays UNRESOLVED.
- The box is a nuisance parameter. The decisive test is A2.3, which fails if the box is wrong.

### A2.3 Temporal match of the crop clip (A rows)

- Raw frames are cropped to the A2.2 box (full-res coordinates). Raw and crop-clip frames are both scaled to 64×64 gray.
- Same two cues as Amendment 1, on this region:
  1. per-frame z-normalized MAE over 64 evenly spaced clip frames;
  2. **region motion signature:** mean |Δ| per cell of a 4×4 grid (16 values per frame). Each cell's series is
     centered over the window, and the Pearson r is taken over the flattened frames × 16 array.
- **Unique match: the same frozen Amendment 1 thresholds.**
  - the two cues agree on the best offset within ±1 frame;
  - r_best ≥ 0.90;
  - r_best − (best r more than 5 frames away) ≥ 0.20.
- Scalar (Amendment 1) motion r is recorded alongside for transparency. It is not used for status.
- Rule (c) for A is satisfied by this direct measurement:
  - A slice = [off/fps_raw, (off + n_crop)/fps_raw];
  - rule (e) is checked against the declared realigned timing.

### A2.4 Signer-region match (B rows R09, R22, R29, R32, R39)

- **Region:** the bounding box of the B pose keypoints for that clip (`B_ours_5p39` PKL, keypoints × (1280, 720)).
  - Points: body 0–10, face 23–90, hands 91–132; score ≥ 0.3; union over all clip frames.
  - Padded by 15 % of the box size on each side and clamped to the frame.
  - The B pose is extracted from the B clip itself, so no download is involved.
- The same box is cropped from the B clip and the raw video (same 1280×720 geometry). The cues and the **unique-match
  thresholds are identical to A2.3**.
- **Positive control (pre-specified, run first):** A2.4 on R01–R05, which Amendment 1 VERIFIED.
  - Each must give a unique match at exactly the Amendment 1 offset.
  - If any control fails, A2.4 is declared invalid, is not applied, and the 5 B rows stay UNRESOLVED.

### A2.5 What does not change status

- No threshold above is changed after results are seen.
- A row that fails A2.2, A2.3 or A2.4 stays UNRESOLVED with the measured values recorded.
- A row that passes uniqueness but misses its declared timing is MISMATCH, never VERIFIED.
