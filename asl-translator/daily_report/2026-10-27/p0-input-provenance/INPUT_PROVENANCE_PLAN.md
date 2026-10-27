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
