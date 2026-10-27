# Task 2 Step 1 — resolve R10 provenance before same-domain sampling-quality evaluation (2026-10-27)

This is Step 1 of 任务二 in [THREE_P0_EXECUTION_REPORT.md](../THREE_P0_EXECUTION_REPORT.md): "首先解决 R10 的
23.38–42.38 与 31.03–56.34 时间来源冲突；追溯实际文件与切片命令，不凭时长猜测", and the "同域视频 PTS→pose 帧映射"
that the sampling-quality comparison needs. It was started under the working name "P0-1 input provenance". Script
comments still use that name and "P0-2" for the later sampling step.

**Status:**
- Manifest built and independently re-verified (`scripts/verify_input_manifest.py`: OK).
- **R10 resolved** (see [R10_PROVENANCE.md](R10_PROVENANCE.md)): 23.38–42.38 s never entered Uni-Sign. Both domains
  received the re-aligned interval.
- Cross-checked against the boss's sampling results (see [below](#cross-check-with-the-boss-sampling-results)).
- No model decode. CPU only. No H18/H19 (holdout guard on all 45 IDs; only How2Sign **test** files read).
- Nothing in earlier reports or artifacts was changed.
- Not done in this step: the 14 UNRESOLVED cases, official crop-clip downloads, same-domain sampling decodes.

**Question:** for R01–R45 (the 10.18 inspection-sheet set), which source-video interval actually entered Uni-Sign,
per preprocessing domain? Rules and method: [INPUT_PROVENANCE_PLAN.md](INPUT_PROVENANCE_PLAN.md), frozen before
measuring. Amendment 1 (matching method) was made after a 2-case pilot and before the other 43 were measured.

## Result

90 rows = 45 cases × {`A_official`, `B_ours_5p39`}. Status per the frozen rules:

| | VERIFIED | MISMATCH | UNRESOLVED |
|---|---|---|---|
| `A_official` rows | 31 | 0 | 14 |
| `B_ours_5p39` rows | 38 | 2 | 5 |
| **Cases** (worse of the two rows) | **29** | **2** (R10, R14) | **14** |

**True of all 90 rows:**
- the pose sha256 matches P0-12 `CHECKSUMS.sha256` and P0-A;
- the pose frame count equals its input video's frame count;
- Uni-Sign's frame selection and the **model-input keypoint hash reproduce exactly** (27 rows had more than 256
  frames and were subsampled).

So *what* Uni-Sign received is reproducible everywhere. The open question is only *where in the source video* some
of it came from.

**Where it matches:**
- **VERIFIED `A_official`** rows match the re-aligned annotation: |Δstart| ≤ 0.040 s, median 0.017 s.
- **VERIFIED `B_ours_5p39`** rows match the original annotation: |Δstart| ≤ 0.038 s, median 0.022 s.

## Cases with provenance problems

| Case | Rows | Finding |
|---|---|---|
| **R10** | B MISMATCH, A VERIFIED | B input is the **re-aligned** interval +4 frames (31.21–56.54 s), not the declared original (23.38–42.38). See R10_PROVENANCE.md |
| **R14** | B MISMATCH, A VERIFIED | Same mechanism (`how2sign_v2` "rescued via re-aligned-file timing"): B input is 34.93–48.17 s = re-aligned 35.25–48.53 shifted −10 frames (−0.32 / −0.36 s). Original 26.19–36.11 never entered |
| R15, R21, R26, R28, R35, R36, R40 | A UNRESOLVED | A and B windows do not overlap, so there is no B↔C alignment to anchor A, and the official crop clip is not stored locally. B VERIFIED |
| R42, R45 | A UNRESOLVED | P0-12 B↔C alignment residual 0.137 / 0.146 shoulder widths (> 0.02), so A is not anchored. B VERIFIED |
| R09, R22, R29, R39 | B and A UNRESOLVED | B clip match below the frozen margin (repetitive motion). The best offset coincides with the original annotation start (R09 r 0.945, R22 0.962, R29 0.998, R39 0.996), but the runner-up outside ±5 frames is within 0.20 of the winner. A cannot be derived without B |
| R32 | B and A UNRESOLVED | The two matching methods disagree (motion best 159.33 s, r 0.855, vs normalized-MAE best 34.83 s ≈ original start 34.81). Windows also do not overlap |

UNRESOLVED means not anchored by the frozen evidence rules. It does not mean the input is wrong: the model-input
hashes reproduce for all 14 cases.

**Cheapest ways to resolve the 14** (not done here; each needs approval):
- range-fetch the official crop clips for the 11 A rows from the same HF zip (~1 MB each) and pixel-match them;
- for the 5 B rows, a finer match on a hand-region crop.

## Other provenance facts found

- **`B_ours_5p39` is not purely "original timestamps".** Every B input is the How2Sign archive's own pre-cut clip;
  no repo code cut it. 38 are verified to follow the original CSV and 2 (R10, R14) follow the re-aligned CSV. The
  other 5 are unresolved, although their best match sits at the original start.
- **Mislabeled columns for R10/R14.** P0-A `case_provenance.csv` (`orig_*`) and P0-12 `segment_alignment_128.json`
  (`ours_*`) hold re-aligned times for those two clips.
- **Different clip archives.** The B archive clip and the official crop clip are not frame-identical cuts even when
  both follow re-aligned timing: offsets of +4 frames (R10) and −10 frames (R14).

## Cross-check with the boss sampling results

Source: `asl-translator/experiments/p0-2026-10-27/results/sampling_45.json` (commit `2a84dd0`). That run used 45
compressed OLD-window display videos, which are not stored on this machine. R10's display file has sha256
`c0b43d9a…`. The B input clip is `f1887acb…`, which is also the 10.18 inspection-sheet video here. Recorded as a
cross-check only: it does not change any status, and it is not a quality result.

| Check (45 cases) | Result |
|---|---|
| `clip_id` per `review_id` | 45/45 equal |
| Decoded frame count = our B pose frame count | 45/45 |
| Boss frame PTS = index / our B clip fps (24, 30 or 50) | 45/45 |
| Cases over 256 frames | Boss 13 = our B 13: R03, R10, R11, R12, R14, R19, R20, R21, R23, R36, R38, R39, R44 |
| Boss `random` arm indices = our reproduced Uni-Sign B indices | 45/45 identical, R10 included |

- The A domain has **14** subsampled rows: the same 13 plus R04. R04's A pose has 278 frames; its B clip has 175
  frames at 50 fps. The boss's run covers only B-length videos, so it has no A counterpart.
- The display files match the B clips in frame count, fps and seeded indices. **Their pixel identity to the B clip
  was not checked**, because the files are absent here.
- Mapping display time to source time below assumes a frame-for-frame re-encode of the B clip.

**R10 diagnostic region.** The boss's 5–16 s (clip-relative, display video) maps to:
- B frames 120–384;
- source frames 869–1133 (B start = source frame 749);
- **≈ 36.2–47.2 s source time**.

Precision: the B start is measured to one source frame (±1 frame ≈ ±0.04 s). Under the re-encode assumption, the
mapped bounds are good to about ±0.05 s. In A-clip time the same span is about 5.17–16.17 s (A frame 0 = B frame
−4). The region is the boss's pre-existing diagnostic slice. It is not a signing label.

## Can same-domain sampling-quality evaluation (Task 2 Step 2) proceed?

Not on all 45. Use only rows whose interval is anchored:

- **Both domains:** the **29 VERIFIED cases**.
- **Per domain:**
  - B (38 rows) adds R15, R21, R26, R28, R35, R36, R40, R42, R45;
  - A (31 rows) adds R10, R14.
- **R10/R14 B rows** are fully determined (measured slice, hashes reproduce). They may be used **only with their
  measured intervals**, never labeled as original timing.
- **Exclude the 14 UNRESOLVED cases** from any timing-dependent P0-2 claim until they are anchored.

## Files

| File | Content |
|---|---|
| `INPUT_PROVENANCE_PLAN.md` | Question, evidence chain, frozen status rules, Amendment 1 |
| `input_manifest_45.csv` | 90 rows. Columns for source video, annotations (both CSVs + v2 TSV + P0-A values, with file sha256), actual slice and how it was established, pose file/sha/frames, timestamp mapping, sampling (seed, count, first/last index and timestamp, hashes), stored vs reproduced model-input hash, status, reasons, notes |
| `selected_frames.jsonl` | Full selected index and source-timestamp lists per row (timestamps blank where the slice is unresolved) |
| `provenance_summary.json` | Counts, case lists by status, annotation file hashes, R10 rows |
| `R10_PROVENANCE.md` | Answers to the eight R10 questions |
| `scripts/locate_clips.py` | Pixel-match each B input clip inside its raw source (raw videos extracted one at a time to scratch and deleted) |
| `scripts/reproduce_sampling.py` | Re-runs upstream `load_pose` (unisign-cpu-arm64, no model) and recomputes index / model-input hashes |
| `scripts/build_input_manifest.py` | Assembles the manifest and applies the frozen rules |
| `scripts/verify_input_manifest.py` | Independent re-check of hashes, timestamps and status rules |
| `work/located_clips.json`, `work/sampling.jsonl`, `work/locate_all.log` | Raw evidence produced by the two measurement scripts |

## Reproduce

```bash
D=asl-translator/daily_report/2026-10-27/p0-input-provenance
python -I $D/scripts/locate_clips.py --scratch <scratch dir> --out $D/work/located_clips.json    # ~10 min CPU
/opt/anaconda3/envs/unisign-cpu-arm64/bin/python -I $D/scripts/reproduce_sampling.py \
    --unisign-repo ~/Desktop/curify/p014-work/Uni-Sign --out $D/work/sampling.jsonl          # ~1 min CPU
python -I $D/scripts/build_input_manifest.py && python -I $D/scripts/verify_input_manifest.py
```

The external inputs are local and not committed:
- `p018-work/downloads/test_raw_videos.zip` and `how2sign_test.csv` (sha256 `ecc73526…`);
- the re-aligned test CSV (sha256 `d1799dcb…`);
- the Uni-Sign checkout at `eed438bc`.
