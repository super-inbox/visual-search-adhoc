# How2Sign v2 benchmark — Phase 1 execution, 2026-09-01

**Scope of Phase 1:** build and freeze a new, larger How2Sign test-split
benchmark, disjoint from the existing 19-clip pilot (kept untouched as
`pilot_v1`). Metadata-only selection, then physical validation against the
real archive. **No model/API call was made at any point.** Not pushed; not
a PR.

Full detail (selection rule, per-step validation results, freeze method)
lives with the benchmark itself:
`asl-translator/data/public_benchmarks/how2sign_v2/SELECTION_METHODOLOGY.md`.
This doc is the daily-report-style summary, matching the convention set by
`8.30/asl-data/HOW2SIGN_MINI_BENCHMARK.md` for `pilot_v1`.

## Why 128, not ~150

The metadata-only selection (deterministic, one clip per source video,
category-priority strata) produced 149 candidates — the hard ceiling, since
How2Sign's entire TEST split has only 149 unique source videos total.
Physically validating all 149 against the real archive found that **34 of
them (23%) didn't hold up**: 1 was missing from the archive, and 33 had a
physical/official duration mismatch beyond the 0.05s tolerance `pilot_v1`
established — not rounding noise, a real archive/metadata integrity issue
concentrated in a specific batch of source videos (`G2`/`G3`-prefixed IDs,
56% failure rate for that batch vs. near-zero elsewhere). 13 were
recoverable (11 via a different sentence from the same source video, 2 via
the official "manually re-aligned" timing file instead of "original").
**21 were not recoverable under any deterministic, no-video-inspection
rule** and were dropped rather than silently backfilled from an unrelated
video. Final N=128, approved after presenting this finding.

## What else Phase 1 caught

Independently of clip selection: 23/2,357 rows in the official TSV (3 of
the 128 selected) have a double-UTF-8-encoding artifact baked into the
source file's own bytes (verified directly — not introduced by this
pipeline). Left alone, it would have quietly penalized WER on any correct
model output for those clips. Corrected via a documented, mechanical
latin1→utf8 re-decode, flagged per-row in `manifest.csv`.

## Validation summary

| Check | Result |
|---|---|
| Archive download/integrity | 2.41GB `test_rgb_front_clips.zip`, `zipfile.testzip()` passed |
| Archive presence | 148/149 candidates found; 1 missing |
| ffprobe alignment (0.05s tolerance) | 115/149 matched "original" TSV; 2 more matched "re-aligned" TSV; 33 unresolved (1 already counted as missing → 32 additional) |
| Replacement resolution | 11 replaced (same video, alt sentence), 2 rescued (re-aligned timing), 21 dropped |
| Leakage/burned-answer OCR | 128/128 clean, 0 leaks (reused `check_leakage.py`'s functions unmodified) |
| Duplicate content | 0 duplicate clip IDs, 0 videos with >1 clip, 0 duplicate sentence texts, 0 SHA-256 collisions |
| Clip-ID overlap with `pilot_v1` | 0 (hard-checked) |
| Smoke test (`run_smoke_test.py`, unmodified `evaluate.py`/`lib.py`) | 128/128 PASSED, WER=0/CER=0/IoU=1.0 |

## Freeze

`FREEZE_CHECKSUMS.sha256` (260 entries: manifest, 128 references, 2
source_metadata TSVs, the methodology doc, 128 local videos) and
`FREEZE.sha256` (single fingerprint of that file) were computed after every
validation step above, before any model inference.

## Next step (not part of Phase 1)

Running any model (Curify's own, OpenSLT, Uni-Sign, or otherwise) against
this benchmark is a separate, later step requiring its own explicit
authorization — same discipline as `pilot_v1` and the rest of this
project's model-call gating.
