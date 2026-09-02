# How2Sign v2 benchmark — selection methodology and validation record

This file is part of the frozen benchmark's checksum coverage (see
`FREEZE_CHECKSUMS.sha256` / `FREEZE.sha256`). It documents exactly how the
128 clips were chosen and validated, so the selection is auditable and
reproducible from the official TSV alone — no model was run at any point.

## 0. Relationship to `pilot_v1`

`../how2sign/` (19 clips) is kept untouched as the historical pilot. This is
a separate, disjoint benchmark, not a replacement. Clip-ID disjointness from
`pilot_v1`'s 19 clips is asserted programmatically at build time (0 overlap).
19 of this benchmark's 128 clips do come from a source `VIDEO_ID` that
`pilot_v1` also drew a (different) sentence from — disclosed per-row in
`manifest.csv`'s `overlaps_pilot_v1_source_video` column, not hidden.

## 1. Universe

Official How2Sign **TEST split only**. Freshly downloaded "English
Translation (original)" TSV (2,357 rows, 149 unique source `VIDEO_ID`s) from
https://how2sign.github.io/, cross-checked against `pilot_v1`'s own 19 rows
(all 19 found, text byte-identical) to confirm authenticity before use.

## 2. Candidate pool

- Row-level exclusion of `pilot_v1`'s 19 exact `SENTENCE_NAME`s (clip-level
  disjointness).
- 1.0s minimum-duration floor (sub-1s clips are not meaningfully gradeable).
- Result: 2,219 eligible rows across all 149 unique videos (the floor drops
  zero videos entirely).

## 3. One clip per source video

Same diversity rule `pilot_v1` used, applied to the full 149-video universe
(not just videos `pilot_v1` never touched) — since How2Sign's entire TEST
split has only 149 unique source videos total, this is also the hard ceiling
on any one-clip-per-video design.

## 4. Deterministic per-video row choice (before any video was viewed)

For each video, the single representative row is chosen by the first rule
that matches, evaluated in this fixed priority order (protects the scarcest
strata first), with capped supply per category to prevent any one heuristic
from dominating, and alphabetical `SENTENCE_NAME` tie-break throughout — no
manual cherry-picking, no randomness:

1. duration in [15, 31]s (cap 30) — rarest stratum (only 43/149 videos have
   one at all)
2. ends with "?" (cap 19, i.e. uncapped — this is the entire available
   supply) — **official text feature**, not a heuristic
3. contains a number token (cap 20) — **[HEURISTIC]**: digit or spelled-out
   number word
4. proper-noun/acronym proxy (cap 20) — **[HEURISTIC]**: capitalized
   non-sentence-initial word or 2+ letter acronym; a fingerspelling/name
   *candidate*, not a fingerspelling annotation — How2Sign has no official
   fingerspelling field
5. fast-signing proxy, words ÷ official duration ≥ pool p90 (cap 10) —
   **[HEURISTIC]**: text-derived rate only, never measured from video
6. fallback: the video's row whose duration is closest to the pool median
   ("general_fill_plain_or_typical") — this is the "simple sentence" /
   no-special-flag pool

This rule is fully reproducible from the official TSV alone, the same way
`pilot_v1`'s own selection rule is documented in prose rather than as a
committed script.

## 5. Pre-freeze physical validation (this is what actually determined N)

Every one of the 149 metadata-selected candidates was downloaded from the
official `test_rgb_front_clips.zip` archive (2.41GB, `zipfile.testzip()`
integrity-checked) and validated **before** being accepted:

- **Archive presence**: is `raw_videos/<SENTENCE_NAME>.mp4` actually a member?
- **Identity**: does the extracted file's own name match the intended
  `SENTENCE_NAME` exactly?
- **Alignment**: does `ffprobe`'s measured duration match the official TSV's
  `END − START` within 0.05s (same tolerance `pilot_v1` validated with)?
- **Checksum**: SHA-256 of the extracted video bytes.
- **Leakage/burned-answer check**: `asl-eval/check_leakage.py`'s own
  `ocr_video` / `reference_words` / `overlap_fraction` functions, imported
  unmodified (ffmpeg 2-pass frame sampling at 0.5fps + tesseract OCR),
  checked per clip against its own reference text.
- **Duplicate-content check**: SHA-256 collision check across all accepted
  videos, exact-reference-text collision check, and a video-per-clip
  uniqueness assertion (structurally guaranteed here since every clip is
  `-rgb_front` only — no side-camera variant ever entered the pool, so the
  "differs only by camera/take suffix" duplicate case cannot arise).

**Result: 115/149 passed all checks outright. 1/149 was missing from the
archive. 33/149 failed the alignment check** — not rounding noise: most
cluster at a striking ~1.33× physical/official duration ratio, and a
minority are unrelated large discrepancies (one physical clip is only 38%
of its declared length). Testing the 34 failures against the official
**"manually re-aligned"** TSV (a second official timing source,
`pilot_v1`'s own §4 finding established that a minority of videos can use a
different official file than most) recovered 2 more within the same 0.05s
tolerance. Of the 21 remaining physically-unresolvable videos, 19 have
`VIDEO_ID`s starting `G2`/`G3` — a specific, disproportionate concentration
(19 of 34 total `G2`/`G3`-prefixed candidates, ~56%) suggesting a real
packaging inconsistency in a segment of the official archive, not a defect
introduced by this pipeline.

## 6. Deterministic replacement rule (applied before any of it was known to
matter — pre-documented, not improvised per-failure)

A hard-invalidated clip (missing from archive, or alignment/leakage/
duplicate-content failure) is replaced **only** by a different sentence from
the **same source video** — every one of the 149 available videos was
already assigned to a slot, so no other video exists to substitute from
without deviating further from the one-clip-per-video rule (a deviation not
authorized for this pass). The replacement is chosen by re-applying the
exact §4 priority cascade to that video's remaining rows only, and is itself
physically re-validated (archive presence + `ffprobe` alignment) before
acceptance; a failed replacement attempt cascades to the next candidate row
from the same video. If a video has no row that ever passes, it is dropped
— never silently substituted with an unrelated video.

Full attempt-by-attempt audit trail (rejected clip, every row tried, and
why): `validation/replacement_audit.json`.

| Outcome | Count |
|---|---|
| Replaced — alternate sentence, same video, original-file timing | 11 |
| Rescued — same clip, re-aligned-file timing instead | 2 |
| Dropped — no row from that video validates under either official file | 21 |

## 7. Final N: 128

Below the original ~149 metadata-only target *because of the archive
validation finding in §5, not a selection change*. Every one of the 128
clips is hard-validated: archive-present, `ffprobe`-aligned to an official
timing source within 0.05s, OCR-clean (0 leaks; 1 clip has a single stray
2-character misread, 0.00 reference overlap — noise, not a caption), and
free of duplicate content.

## 8. Text-encoding correction (official text, not a content change)

3 of the 128 clips' official reference text contained a **double-UTF-8-encoded**
artifact baked into the source TSV itself (verified in the raw downloaded
file's bytes — e.g. `Thereâ\x80\x99s` for `There's`; 23/2357 rows in the
whole TSV are affected). A standard latin1→utf8 re-decode was applied when
writing `references/*.srt` and `manifest.csv`'s `reference_text` column —
this corrects *decoding*, not wording or meaning. Flagged per-row via
`manifest.csv`'s `text_encoding_fixed` column.

## 9. Heuristic strata — tagged, not verified

`heuristic_contains_number_token`, `heuristic_proper_noun_or_acronym_fingerspelling_candidate`,
and `heuristic_fast_signing_wps_ge_p90` in `manifest.csv` are **heuristics**,
explicitly labeled as such, never "ground truth." Review artifacts listing
every flagged clip are in `validation/review_*.csv`, each row marked
`manual_review_status: pending` — no clip's inclusion was changed based on a
heuristic turning out to be a false positive; only a qualified human review
may promote or demote a tag, per this repo's existing convention for
`asl_corpus/` candidate references.

## 10. Freeze integrity

`FREEZE_CHECKSUMS.sha256` covers `manifest.csv`, every `references/*.srt`,
`source_metadata/*.tsv`, this methodology document, and every local
`videos/*.mp4` (SHA-256 per file, individually listed — the checksums are
committed to git even though the video bytes themselves stay gitignored).
`FREEZE.sha256` is a single SHA-256 fingerprint of `FREEZE_CHECKSUMS.sha256`'s
own contents. Both were computed **after** every step above, before any
model inference against this benchmark.
