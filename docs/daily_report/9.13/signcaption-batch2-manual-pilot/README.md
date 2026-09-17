# SignCaption Manual Pilot — Batch 2 (10 New Clips, n=5 → n=15)

**Date:** 2026-09-13
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Status:** preparation only. No SignCaption API was called, no Gemini call was made, no
trajectory experiment was run, nothing was committed or pushed. This document and its
companions verify eligibility, lay out where to place manually collected results, and
prepare (but do not run to completion) a scorer.

## Why Batch 2, why these 10 clips

The original 5-clip SignCaption pilot showed one genuine result (a guitar/double-stops
clip) but was too small and, on inspection, skewed toward near-total-failure cases for the
Curify frame baseline. Batch 2 expands the pilot to n=15 with 10 new clips chosen by
stratified sampling — **not** cherry-picked to make any system look better or worse — to
give the eventual combined comparison more range in duration and difficulty.

## Selection method

- **Eligibility filter (123 candidate clips):** every one of the 128 frozen benchmark
  clips *except* the original 5, that has a frozen reference, a local `.mp4`, a
  successful Curify frame-baseline result, and a successful Uni-Sign result. All 123
  passed (Curify and Uni-Sign are both 128/128 complete).
- **Stratification:** duration tercile × Curify-WER tercile × Uni-Sign-WER tercile,
  computed over that 123-clip pool.
- **Diagnostic-12 mix:** 3 of the 10 drawn from the (at selection time) diagnostic-12
  clips that still lacked SignCaption coverage; 7 drawn from outside the diagnostic-12.
- **Explicitly avoided:** selecting only clips where both Curify and Uni-Sign already
  fail badly. Several relatively easy cases for both systems are included specifically to
  counterbalance the original 5, which were almost entirely near-ceiling-failure cases for
  Curify.

## The 10 selected clips

| clip_id | duration (s) | ref words | Curify WER | Uni-Sign WER | native-video | diagnostic-12 | category (manifest) |
|---|---|---|---|---|---|---|---|
| `g2NA_eBUcH8_0-3-rgb_front` | 2.87 | 12 | 0.750 | 0.667 | yes | yes | question |
| `G19uBylwQww_1-2-rgb_front` | 4.53 | 25 | 0.808 | 0.808 | yes | yes | number/fingerspelling/fast-signing heuristic |
| `fZM3IcM2Xs4_14_15_16-10-rgb_front` | 18.67 | 22 | 1.913 | 1.261 | yes | yes | long-duration (15–31s) |
| `g2nvBjp0loQ_4-3-rgb_front` | 4.89 | 11 | 0.833 | 0.167 | no | no | plain/typical |
| `g05yGRoZE10_1-8-rgb_front` | 4.42 | 16 | 0.882 | 0.471 | no | no | plain/typical |
| `FzQPg4aqNYc_13-1-rgb_front` | 6.35 | 16 | 1.000 | 2.000 | no | no | fingerspelling heuristic |
| `G3RvsnzQrXQ_3-10-rgb_front` | 12.93 | 47 | 0.980 | 0.860 | no | no | fingerspelling heuristic |
| `g0UUmEkoT1w_2-10-rgb_front` | 5.13 | 8 | 1.000 | 1.875 | no | no | plain/typical |
| `FZCEymcpq7I_14-1-rgb_front` | 9.81 | 39 | 1.000 | 0.854 | no | no | number heuristic |
| `G1jsDl1mVvk_1-1-rgb_front` | 17.01 | 68 | 0.931 | 0.958 | no | no | long-duration (15–31s) |

**Terminology note — important, carried over from the frozen benchmark's own manifest:**
the `question` / `number` / `fingerspelling` / `fast-signing` tags above are
**reference-text-derived heuristic labels** — computed automatically from properties of
the frozen *English reference text* (e.g. "does it end in a `?`", "does it contain a digit
or number word"), by the benchmark's own selection scripts. **They are not human-verified
ASL visual-content categories.** Several are explicitly marked
`[HEURISTIC, manual review needed]` in the manifest itself, meaning no ASL-fluent reviewer
has confirmed the signed content actually contains fingerspelling, fast signing, or a
signed question. Treat them as weak, text-side priors used only to diversify the sample —
never as a claim about what was actually signed.

## Native-video coverage across the combined n=15 — corrected

**All 5 original pilot clips already have valid Gemini native-video predictions** — they
were, in fact, chosen for the original pilot specifically because they were 5 of the 12
diagnostic clips with a valid native-video result. 3 of these 10 Batch-2 clips
(`g2NA_eBUcH8_0-3-rgb_front`, `G19uBylwQww_1-2-rgb_front`,
`fZM3IcM2Xs4_14_15_16-10-rgb_front`) are diagnostic-12 members that gained a valid
native-video prediction in the 2026-09-13 diagnostic-12 retry (see
`docs/daily_report/9.13/asl-full-benchmark-comparison/READINESS.md`).

**Combined native-video coverage across all 15 SignCaption-pilot clips is therefore
8/15 (5 original + 3 Batch 2), not 5/15.** (An earlier verbal estimate of this batch's
proposal stated 5/15 in error — that undercounted the original 5, which already had
native-video coverage. Corrected here before any Batch-2 artifact was created.) The
4-way (Curify / Uni-Sign / native-video / SignCaption) comparison will be reported on
this matched 8/15 subset only; the other 7 Batch-2 clips have no native-video prediction
and none will be fabricated for them.

## Bias assessment (unchanged conclusion, now with the corrected coverage figure)

The combined n=15 does not look obviously biased:
- **Duration:** spans 2.87s–18.67s, roughly even across short (~3–5s), medium (~5–10s),
  and long (~13–19s) buckets.
- **Difficulty:** includes clips relatively easy for both systems (e.g. `g2nvBjp0loQ`
  Uni-Sign WER 0.167), clips hard for both (e.g. `fZM3IcM2Xs4` Curify WER 1.913), and a
  divergent case (`FZCEymcpq7I`: Curify fails, Uni-Sign relatively strong) — not
  uniformly stacked toward failure the way the original 5 were.
- **Topic diversity:** poker, paper airplanes, a music/celebration remark, fitness,
  a technical term, cooking, sewing/craft, fatigue symptoms, golf, refereeing — no
  repeated domain among the 10.
- **Diagnostic mix:** 3/10 diagnostic-12, 7/10 outside, as requested.
- **Real (non-bias) limitation:** native-video coverage stays partial (8/15) by
  construction — native-video was never run on any clip outside the original
  diagnostic-12, so this is a coverage gap inherent to which experiments have been run so
  far, not a property of how these 10 clips were chosen.

## What was NOT done

- No SignCaption API call, no SignCaption website automation.
- No Gemini call of any kind.
- No trajectory experiment was run or re-run.
- No source video or reference file was modified.
- The original 5-clip pilot's results were not touched, re-scored, or overwritten.
- No score was computed for Batch 2 — the scorer
  (`asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/score_batch2_and_combined.py`)
  is prepared and dry-run-verified only; it correctly reports all 10 Batch-2 clips as
  `missing` (no fabricated result) and correctly restricts the native-video 4-way
  comparison to the true 8-clip matched subset.
- Nothing staged, committed, or pushed.

## What you do next

Follow `MANUAL_UPLOAD_CHECKLIST.md` in this directory, one clip at a time. Do not run
`score_batch2_and_combined.py --write-results` until you've placed real SignCaption output
for however many of the 10 clips you complete.

## Files in this batch

- `docs/daily_report/9.13/signcaption-batch2-manual-pilot/README.md` — this file
- `docs/daily_report/9.13/signcaption-batch2-manual-pilot/MANUAL_UPLOAD_CHECKLIST.md` — step-by-step workflow
- `docs/daily_report/9.13/signcaption-batch2-manual-pilot/pilot_manifest_batch2.csv` — per-clip eligibility/paths/reference text
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/README.md` — results-directory schema
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/<clip_id>/README.md` — per-clip result-slot instructions
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/score_batch2_and_combined.py` — prepared scorer, **dry-run verified, not yet run with real data**
