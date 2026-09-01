# How2Sign mini benchmark — pilot execution, 2026-08-30

**Scope of this pilot:** stage a small, reproducible public-benchmark subset only.
No model/API calls were made, nothing was trained, and no private `asl_corpus`
data was touched or modified. Not committed or pushed.

---

## 1. Re-verified official download/access instructions and TEST split structure

Re-checked directly against https://how2sign.github.io/ (same page cited in
`PUBLIC_ASL_DATASET_RESEARCH.md`). The **test split**, specifically, offers
these official downloads:

| Modality | Size | Notes |
|---|---|---|
| Green Screen RGB videos (frontal view) — full, unsegmented | 23G | not needed |
| Green Screen RGB videos (side view) — full, unsegmented | 23G | not needed |
| **Green Screen RGB clips (frontal view)** — pre-segmented, sentence-level | **2.2G** | used — smallest official path to segmented clips |
| Green Screen RGB clips (side view) | 1.6G | not needed |
| B-F-H 2D Keypoints clips (frontal view) | 1.6G | not needed |
| English Translation (original) | 423K | used — matches the physical clip boundaries (see §4) |
| English Translation (manually re-aligned) | 424K | downloaded, compared, **not used as the timing source** (see §4) |

No separate small "test-only clip list" exists — the smallest official archive
that contains pre-segmented (not full-length) test-split video is the 2.2GB
`test_rgb_front_clips.zip`. This was the smallest available *official* path to
real segmented test clips (the alternative, 23GB per view, is the full
unsegmented split and was never considered).

## 2. Minimum files needed for evaluation

- **Source ASL video clips**: pre-segmented per-sentence `.mp4` files from
  `test_rgb_front_clips.zip` (`raw_videos/<SENTENCE_NAME>.mp4` inside the
  archive — the folder is named `raw_videos/` in the archive but these are
  the sentence-level clips, not the full unsegmented recordings).
- **English reference/translation**: the "English Translation (original)"
  TSV (423KB) — columns `VIDEO_ID, VIDEO_NAME, SENTENCE_ID, SENTENCE_NAME,
  START, END, SENTENCE`.
- **IDs/timestamps/split metadata**: entirely contained in that same TSV;
  `SENTENCE_NAME` is the exact clip filename (minus `.mp4`) and doubles as the
  join key between video and text. No separate ID-mapping file exists or is
  needed.
- **Alignment metadata actually required**: none beyond the TSV's own
  `START`/`END` columns — no external forced-aligner output, no keypoints, no
  gloss annotation were downloaded or are needed for this pilot (those exist
  officially but are out of scope for a text-vs-video WER/CER comparison).

## 3. Avoided downloading unnecessarily — with one honest exception

The **video** side has no smaller official granular option than the 2.2GB
clips archive (no per-clip download endpoint exists). To avoid keeping that
2.2GB locally: the archive was downloaded once, the needed clips were
extracted via Python's `zipfile` (selective per-member extraction, not a full
unzip), and **the archive was deleted immediately afterward**. It was
downloaded a **second** time only because an error in the first selection
pass (see §4) required different clips than were first extracted — both
downloads were transient and deleted right after use; nothing multi-GB is
retained on disk or in the repo. Final retained footprint: **19 clips, 56MB**
(see §9).

The two small **text** files (423KB and 424KB) were fully downloaded, as
intended — they are tiny and both were needed to catch the timing
discrepancy in §4.

## 4. A correction found during this pilot (recorded here per your instruction)

The initial clip selection was computed from the **"manually re-aligned"**
translation file's `START_REALIGNED`/`END_REALIGNED` timestamps. After
extracting those clips, `ffprobe`-measured durations did not match the
selection metadata at all (e.g. one clip's re-aligned duration said 6.25s;
`ffprobe` measured 3.21s — a near-2x discrepancy, not rounding noise).

Cross-checking against the **"original"** translation file resolved it: the
physical clips inside `test_rgb_front_clips.zip` were segmented according to
the **original** (non-realigned) timestamps, not the manually re-aligned
ones — `ffprobe` durations matched the *original* file's `END − START` to
within ~0.03s for every clip checked. The **SENTENCE text itself is
byte-identical between both files for all 2,357 test rows** (verified
directly) — only the timing columns differ. This was **not** a model-related
issue; it was caught entirely through metadata verification before any
frame was viewed or any model was run, and the selection was redone using
the original-alignment file as the correct source of truth for both duration
filtering and the reference `.srt` end-times.

This is the exact same category of mistake as the corpus contamination
lesson from `CONTAMINATION.md` (2026-08-30): *trust, but verify, that a
dataset's stated metadata actually matches the physical artifact it
describes* — here it cost a re-selection, not a bad accuracy claim, only
because it was caught before any scoring happened.

## 5. Selection rule (recorded before any video frame was viewed)

Decided purely from the official-test-split TSV, before opening a single
video file:

1. **Universe:** official test split only (`how2sign_test_original.tsv`, all
   2,357 rows).
2. **Duration filter:** `5.0 ≤ (END − START) ≤ 60.0` seconds → 1,105
   candidates.
3. **One clip per unique source `VIDEO_ID`** — avoids multiple clips from the
   same recording session, maximizing signer/content diversity across the
   subset.
4. **Stratified by duration bucket** to force genuine duration diversity
   rather than defaulting to whatever sorts first: bucket A (5–15s, 997
   available), bucket B (15–30s, 99 available), bucket C (30–60s, only 9
   available). Target composition: take **all** available unique-video
   candidates from the rare long bucket C (6 obtained), a fixed 7 from
   bucket B, and 7 from bucket A to reach 19 total.
5. **Deterministic tie-break:** within each bucket, candidates are sorted by
   `SENTENCE_NAME` (alphabetical) and taken in that order — no manual
   cherry-picking, no randomness, fully reproducible from the TSV alone.
6. **Visual criteria applied only after this metadata-only list was fixed**
   (§7) — single signer, face/hands visible, no title cards/burned text.
   Rejection at this stage would trigger backfill from the next
   alphabetically-sorted, not-yet-used candidate in the same bucket — this
   did not end up being needed (§7).

No model was run at any point before or during this selection. Nothing here
was chosen because of, or checked against, any model's output.

## 6. Staged location

```
asl-translator/data/public_benchmarks/how2sign/
├── README.md
├── manifest.csv
├── videos/            19 .mp4
├── references/         19 .srt
├── source_metadata/     how2sign_test_original_subset.tsv (our 19 rows only)
└── run_smoke_test.py
```

This mirrors How2Sign's own official distribution shape (clips + a
sentence-level TSV) and this repo's existing `asl_corpus/` convention
(`videos/` + per-item reference text) closely enough that the existing
`asl-eval` tooling needed **zero code changes** to read it (§10). No better
structure was suggested by the official data format, so the proposed layout
was kept as-is, per your instruction not to change it without reason.

## 7. Contamination/leakage visual check

For each of the 19 clips, 3 frames were sampled (near start, middle, near
end) via local `ffmpeg` and manually inspected (no OCR, no tesseract, per
your instruction — this is visual review by the assistant, the same
no-tooling method used for the original 1320 burned-caption read).

**Result: clean, all 19/19.** Every sampled frame shows: a single signer,
green-screen studio background, face and hands clearly in frame, no burned-in
text, captions, subtitles, or title cards anywhere. This matches expectation
— How2Sign's raw studio recordings (unlike Curify's own contaminated
155/1320 cases) were never designed to carry on-screen text at all.

**One disclosed limitation, not a leakage issue:** How2Sign's entire test
split uses only **11 unique signers** total. With 19 clips drawn from 19
different source `VIDEO_ID`s (by design, for content diversity), several
clips still show the **same physical signer** across different source
videos — e.g. one recurring bearded male signer appears in 7 of the 19
selected clips. Source-video diversity does not guarantee signer diversity
in this dataset; this is a known, disclosed property of How2Sign itself
(11 signers total, per the paper), not a selection bias introduced here.

## 8. Evaluator smoke test (data-pipeline check, not a model evaluation)

Ran twice: once via a standalone script exercising `lib.py`'s functions
directly across all 19 clips, and once via the real, unmodified
`asl-eval/evaluate.py` CLI end-to-end for one clip, both using each clip's
own reference text fed back in as a trivial "prediction."

```
python3 asl-translator/data/public_benchmarks/how2sign/run_smoke_test.py
...
SMOKE TEST PASSED: all 19 clips - IDs matched, reference parsed,
reference-as-prediction scored WER=0/CER=0/IoU=1.0.
```

CLI-level spot check (`asl-eval/evaluate.py --reference ... --prediction ...`)
on one clip confirmed the same: WER 0.0, CER 0.0, temporal IoU 1.0, and
`corpus_guard.assert_prediction_usable()` (added in the 2026-08-30
decontamination commit) passed without modification — it only blocks
predictions carrying a `"contamination"` block or pointing at a known-leaky
Curify corpus video by basename, neither of which applies to this public
benchmark's files.

**No changes were made to `evaluate.py`, `lib.py`, or `corpus_guard.py`.**
The only new code is `run_smoke_test.py`, which lives entirely inside the new
`public_benchmarks/how2sign/` directory and only orchestrates calls to the
existing, untouched scoring functions — it does not alter scoring semantics.

## 9. Disk usage

| Item | Size |
|---|---|
| Transient full clips archive (`test_rgb_front_clips.zip`) | 2.2GB downloaded twice, **deleted both times**, 0 bytes retained |
| Transient full-video-source download (accidental, during initial range-request test) | 2.4GB, deleted immediately |
| **Retained: `asl-translator/data/public_benchmarks/how2sign/`** | **56MB** (19 videos + 19 tiny SRTs + one TSV subset) |

## 10. Adapter necessity assessment

**No adapter was needed.** How2Sign's sentence-level clips map 1:1 to this
repo's existing single-segment-SRT convention (start=0, end=clip duration,
one English sentence). `asl-eval/evaluate.py`'s `--reference`/`--prediction`
CLI already reads this shape with zero modification — confirmed by both the
direct-function smoke test and the real CLI run in §8. The only new file,
`run_smoke_test.py`, is a batch-loop convenience wrapper (iterate
`manifest.csv`, call the existing scoring functions per clip) — it is
isolated inside the benchmark's own directory and does not touch, import
privately from, or alter core metric logic in `asl-eval/`.

## Licensing / redistribution note — read before ever committing the videos

**How2Sign is CC BY-NC 4.0** (non-commercial research use, attribution
required). The 19 video files staged in
`asl-translator/data/public_benchmarks/how2sign/videos/` are a direct extract
of the official dataset's own copyrighted video content. Whether this
repository's git history should carry redistributed third-party video bytes
at all — even under a research license, even for 19 short clips — is a
policy question for you/legal, not a technical one this pilot can resolve.
**Per your explicit instruction, nothing has been committed or pushed.**
Recommendation: keep the videos out of git entirely (add
`asl-translator/data/public_benchmarks/how2sign/videos/` to `.gitignore`, or
document a fetch-on-demand script instead of committing bytes) and only
version the small, clearly-licensed text/metadata (`manifest.csv`,
`references/*.srt`, `source_metadata/*.tsv`, `README.md`) if this is ever
committed — decide this explicitly before any future commit of this folder.
