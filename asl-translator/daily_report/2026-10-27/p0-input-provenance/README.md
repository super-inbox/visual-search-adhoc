# Task 2 Steps 1–2 — resolve input provenance before same-domain sampling-quality evaluation (2026-10-27)

This is Step 1 of 任务二 in [THREE_P0_EXECUTION_REPORT.md](../THREE_P0_EXECUTION_REPORT.md): "首先解决 R10 的
23.38–42.38 与 31.03–56.34 时间来源冲突；追溯实际文件与切片命令，不凭时长猜测", and the "同域视频 PTS→pose 帧映射"
that the sampling-quality comparison needs. It was started under the working name "P0-1 input provenance". Script
comments still use that name and "P0-2" for the later sampling step.

- **Step 1** (commit `3d495562`): manifest, R10 resolved, 14 cases left UNRESOLVED.
- **Step 2** (this update): the UNRESOLVED rows re-attacked under **Amendment 2**, frozen before any download or
  measurement. 9 of 14 cases resolved; 5 remain UNRESOLVED. R10/R14 were not re-measured and stay MISMATCH.
- **Step 3** (not run): same-domain sampling-quality evaluation.

**Status:**
- Manifest built and independently re-verified (`scripts/verify_input_manifest.py`: OK).
- **R10 resolved** (see [R10_PROVENANCE.md](R10_PROVENANCE.md)): 23.38–42.38 s never entered Uni-Sign. Both domains
  received the re-aligned interval.
- Cross-checked against the boss's sampling results (see [below](#cross-check-with-the-boss-sampling-results)).
- No model decode. CPU only. No H18/H19 (holdout guard on all 45 IDs; only How2Sign **test** files read).
- Nothing in earlier reports or artifacts was changed.
- Step 2: 14 official crop clips range-fetched from the same HF release P0-12 used (7.1 MB, CRC32 and P0-12 ffprobe
  checked; scratch only, not committed). No Uni-Sign generation, no translation comparison, no GPU, no reference text
  used for localization.

**Question:** for R01–R45 (the 10.18 inspection-sheet set), which source-video interval actually entered Uni-Sign,
per preprocessing domain? Rules and method: [INPUT_PROVENANCE_PLAN.md](INPUT_PROVENANCE_PLAN.md), frozen before
measuring. Amendment 1 (matching method) was made after a 2-case pilot and before the other 43 were measured.
Amendment 2 (direct official-crop match for A; signer-region match for B) was written before Step 2 fetched or measured
anything, and its pre-specified positive control (R01–R05) passed before it was applied.

## Result

90 rows = 45 cases × {`A_official`, `B_ours_5p39`}. Status per the frozen rules:

| | VERIFIED | MISMATCH | UNRESOLVED |
|---|---|---|---|
| `A_official` rows | 41 | 0 | 4 |
| `B_ours_5p39` rows | 42 | 2 | 1 |
| **Cases** (worse of the two rows) | **38** | **2** (R10, R14) | **5** (R26, R28, R32, R35, R42) |

Step 1 → Step 2: A 31/0/14 → 41/0/4; B 38/2/5 → 42/2/1; cases 29/2/14 → 38/2/5. Only the 19 rows that were
UNRESOLVED changed; the other 71 rows are byte-identical in the manifest.

**True of all 90 rows:**
- the pose sha256 matches P0-12 `CHECKSUMS.sha256` and P0-A;
- the pose frame count equals its input video's frame count;
- Uni-Sign's frame selection and the **model-input keypoint hash reproduce exactly** (27 rows had more than 256
  frames and were subsampled).

So *what* Uni-Sign received is reproducible everywhere. The open question is only *where in the source video* some
of it came from.

**Where it matches:**
- **VERIFIED `A_official`** rows match the re-aligned annotation: Step 1 rows |Δstart| ≤ 0.040 s, median 0.017 s;
  Step 2 rows |Δstart| ≤ 0.037 s, |Δend| ≤ 0.098 s.
- **VERIFIED `B_ours_5p39`** rows match the original annotation: Step 1 rows |Δstart| ≤ 0.038 s, median 0.022 s;
  Step 2 rows |Δstart| ≤ 0.018 s, |Δend| ≤ 0.033 s.

## Cases with provenance problems

| Case | Rows | Finding |
|---|---|---|
| **R10** | B MISMATCH, A VERIFIED | B input is the **re-aligned** interval +4 frames (31.21–56.54 s), not the declared original (23.38–42.38). See R10_PROVENANCE.md |
| **R14** | B MISMATCH, A VERIFIED | Same mechanism (`how2sign_v2` "rescued via re-aligned-file timing"): B input is 34.93–48.17 s = re-aligned 35.25–48.53 shifted −10 frames (−0.32 / −0.36 s). Original 26.19–36.11 never entered |
| R26, R28, R35, R42 | A UNRESOLVED, B VERIFIED | Official crop clip fetched and intact, but its **position in the raw frame is not unique** under A2.2: NCC best / next >16 px = R26 0.894 / 0.871, R28 0.865 / 0.845, R35 0.950 / 0.916, R42 0.907 / 0.886 (margins 0.020–0.034 < 0.05). Without an accepted box, A2.3 is not run. R42 also had the Step 1 B↔C residual 0.137 > 0.02 |
| R32 | B UNRESOLVED, A VERIFIED | A2.4 signer-region match: grid motion r 0.896 (< 0.90), next outside ±5 frames 0.643. Both cues agree on offset 1045 (34.83 s, ≈ original start 34.81), but r misses the frozen 0.90, so the row stays UNRESOLVED. Step 1: full-frame methods disagreed (159.33 s vs 34.83 s) |

UNRESOLVED means not anchored by the frozen evidence rules. It does not mean the input is wrong: the model-input
hashes reproduce for all 5 cases.

## Step 2: resolved rows (Amendment 2)

**Positive control (A2.4 on R01–R05 B, pre-specified):** 5/5 unique, each at exactly the Amendment 1 offset (grid r
0.966–0.9998, next 0.26–0.46). So A2.4 was applied.

| Row | Step 1 → Step 2 | Method | Evidence (offset; grid motion r / next outside ±5; NCC box) | Slice (s) | Δ vs declared (start/end, s) |
|---|---|---|---|---|---|
| R09 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 20 fr; 0.968 / 0.500; NCC 0.952 / 0.857 | 0.833–3.208 | realigned +0.023 / +0.048 |
| R09 B | UNRESOLVED → VERIFIED | A2.4 | 17 fr (= Step 1 best); 0.984 / 0.595 | 0.708–1.958 | original +0.018 / +0.028 |
| R15 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 358 fr; 0.940 / 0.651; NCC 0.896 / 0.812 | 14.917–15.708 | realigned +0.037 / +0.098 |
| R21 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 3155 fr; 0.998 / 0.337; NCC 0.945 / 0.795 | 105.167–119.367 | realigned +0.007 / +0.027 |
| R22 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 1501 fr; 0.972 / 0.685; NCC 0.894 / 0.790 | 62.542–64.375 | realigned +0.012 / +0.075 |
| R22 B | UNRESOLVED → VERIFIED | A2.4 | 1501 fr (= Step 1 best); 0.972 / 0.713 | 62.542–64.333 | original +0.012 / +0.033 |
| R29 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 301 fr; 0.999 / 0.545; NCC 0.748 / 0.631 | 10.033–11.867 | realigned +0.003 / +0.007 |
| R29 B | UNRESOLVED → VERIFIED | A2.4 | 301 fr (= Step 1 best); 0.999 / 0.545 | 10.033–11.867 | original +0.003 / +0.007 |
| R32 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 1301 fr; 0.998 / 0.577; NCC 0.932 / 0.769 | 43.367–45.700 | realigned +0.017 / +0.020 |
| R36 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 2651 fr; 0.993 / 0.245; NCC 0.985 / 0.913 | 88.367–120.967 | realigned +0.027 / +0.087 |
| R39 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 2334 fr; 0.997 / 0.422; NCC 0.957 / 0.869 | 46.680–52.440 | realigned 0.000 / 0.000 |
| R39 B | UNRESOLVED → VERIFIED | A2.4 | 1815 fr (= Step 1 best); 0.998 / 0.653 | 36.300–42.180 | original 0.000 / 0.000 |
| R40 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 2124 fr; 0.996 / 0.396; NCC 0.922 / 0.727 | 70.800–76.200 | realigned +0.010 / +0.010 |
| R45 A | UNRESOLVED → VERIFIED | A2.2+A2.3 | 764 fr; 0.984 / 0.424; NCC 0.946 / 0.847 | 31.833–35.583 | realigned +0.033 / +0.023 |

In every resolved row the normalized-MAE offset equals the motion offset. Per-row details are in
`work/located_amendment2.json` and in the manifest `slice_evidence` column.

**Official crop clips fetched (A2.1).**
- Source: HF `ZechengLi19/Uni-Sign` @ `eab251b7fe7e8521afc0e67be98add670ea40a0d`, `how2sign_rgb_format.zip.*`, entries
  `crop_test/<clip>.mp4`.
- 14 files, 7,142,719 bytes in total, each CRC32-checked against the zip central directory. Per-clip size, CRC32,
  sha256 and byte ranges are in `work/official_crops.json`; the A rows' `input_video_sha256` holds the sha256.
- Each clip's w_h, fps and frame count equal P0-12 `official_crop_ffprobe.csv` and the A pose frame count.
- Not committed (scratch only).

## Other provenance facts found

- **`B_ours_5p39` is not purely "original timestamps".** Every B input is the How2Sign archive's own pre-cut clip;
  no repo code cut it. 42 are verified to follow the original CSV and 2 (R10, R14) follow the re-aligned CSV. R32 is
  unresolved, although both cues' best match sits at the original start.
- **`A_official` follows the re-aligned CSV in every row that could be measured (41/41).**
- **Mislabeled columns for R10/R14.** P0-A `case_provenance.csv` (`orig_*`) and P0-12 `segment_alignment_128.json`
  (`ours_*`) hold re-aligned times for those two clips.
- **Different clip archives.** The B archive clip and the official crop clip are not frame-identical cuts even when
  both follow re-aligned timing: offsets of +4 frames (R10) and −10 frames (R14).

## Cross-check with the boss sampling results

Source: `asl-translator/experiments/p0-2026-10-27/results/sampling_45.json` (commit `2a84dd0`). That run used 45
compressed OLD-window display videos, which are not stored on this machine. R10's display file has sha256
`c0b43d9a…`. The B input clip is `f1887acb…`, which is also the 10.18 inspection-sheet video here. Recorded as a
cross-check only: it does not change any status, and it is not a quality result.

Re-run after Step 2 against the updated manifest and `selected_frames.jsonl`: every line below is unchanged (45/45 on
each check, same 13 subsampled cases).

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

## Can same-domain sampling-quality evaluation (Task 2 Step 3) proceed?

Not on all 45 for any timing-dependent claim. Run it **separately by domain**, on rows whose interval is anchored:

- **Both domains (paired A-vs-B claims):** the **38 VERIFIED cases**.
- **A only:** 41 rows = the 38 + R10, R14, R32.
- **B only:** 42 VERIFIED rows = the 38 + R26, R28, R35, R42.
  - The R10/R14 B rows are fully determined (measured slice, hashes reproduce). They may be added (44 rows) **only
    with their measured intervals**, never labeled as original timing.
- **Exclude:** A rows of R26, R28, R35, R42 and the B row of R32 from any timing-dependent claim.
- Claims that do not depend on source time (model input as given) can use all 90 rows, since every model-input hash
  reproduces.

## Files

| File | Content |
|---|---|
| `INPUT_PROVENANCE_PLAN.md` | Question, evidence chain, frozen status rules, Amendments 1 and 2 |
| `input_manifest_45.csv` | 90 rows. Columns for source video, annotations (both CSVs + v2 TSV + P0-A values, with file sha256), actual slice and how it was established, pose file/sha/frames, timestamp mapping, sampling (seed, count, first/last index and timestamp, hashes), stored vs reproduced model-input hash, status, reasons, notes |
| `selected_frames.jsonl` | Full selected index and source-timestamp lists per row (timestamps blank where the slice is unresolved) |
| `provenance_summary.json` | Counts, case lists by status, annotation file hashes, R10 rows |
| `R10_PROVENANCE.md` | Answers to the eight R10 questions |
| `scripts/locate_clips.py` | Pixel-match each B input clip inside its raw source (raw videos extracted one at a time to scratch and deleted) |
| `scripts/reproduce_sampling.py` | Re-runs upstream `load_pose` (unisign-cpu-arm64, no model) and recomputes index / model-input hashes |
| `scripts/fetch_official_crops.py` | Step 2 (A2.1): range-fetch the 14 official crop clips, CRC32 + sha256 + ffprobe checks |
| `scripts/locate_amendment2.py` | Step 2 (A2.2–A2.4): crop-box NCC, crop-clip and signer-region temporal match, positive control |
| `scripts/build_input_manifest.py` | Assembles the manifest and applies the frozen rules (Amendment 2 evidence only for rows Amendment 1 left without a slice) |
| `scripts/verify_input_manifest.py` | Independent re-check of hashes, timestamps and status rules |
| `work/located_clips.json`, `work/sampling.jsonl`, `work/locate_all.log` | Step 1 raw evidence produced by the two measurement scripts |
| `work/official_crops.json`, `work/located_amendment2.json` | Step 2 raw evidence: fetch records (source, byte ranges, CRC32, sha256, probe), Amendment 2 matches (control + 19 target rows). The console log of the run is not committed; it holds only a subset of `located_amendment2.json` |

## Reproduce

```bash
D=asl-translator/daily_report/2026-10-27/p0-input-provenance
python -I $D/scripts/locate_clips.py --scratch <scratch dir> --out $D/work/located_clips.json    # ~10 min CPU
/opt/anaconda3/envs/unisign-cpu-arm64/bin/python -I $D/scripts/reproduce_sampling.py \
    --unisign-repo ~/Desktop/curify/p014-work/Uni-Sign --out $D/work/sampling.jsonl          # ~1 min CPU
python -I $D/scripts/fetch_official_crops.py --scratch <scratch>/crops --out $D/work/official_crops.json   # 14 clips, 7.1 MB
python -I $D/scripts/locate_amendment2.py --scratch <scratch>/raw --crop-dir <scratch>/crops --crops $D/work/official_crops.json \
    --out $D/work/located_amendment2.json --rows R01:B,R02:B,R03:B,R04:B,R05:B                    # control first
python -I $D/scripts/locate_amendment2.py --scratch <scratch>/raw --crop-dir <scratch>/crops --crops $D/work/official_crops.json \
    --out $D/work/located_amendment2.json --rows R09:A,R09:B,R15:A,R21:A,R22:A,R22:B,R26:A,R28:A,R29:A,R29:B,R32:A,R32:B,R35:A,R36:A,R39:A,R39:B,R40:A,R42:A,R45:A
python -I $D/scripts/build_input_manifest.py && python -I $D/scripts/verify_input_manifest.py
```

The external inputs are local and not committed:
- `p018-work/downloads/test_raw_videos.zip` and `how2sign_test.csv` (sha256 `ecc73526…`);
- the re-aligned test CSV (sha256 `d1799dcb…`);
- the Uni-Sign checkout at `eed438bc`.
