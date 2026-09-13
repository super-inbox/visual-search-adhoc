# SignCaption Manual Pilot — How2Sign v2, 5 Clips

**Date:** 2026-09-11
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Status:** preparation only. No SignCaption API was called, no Gemini call was made, no
trajectory experiment was run, nothing was committed or pushed. This document and its
companions only verify eligibility, lay out where to place manually collected results, and
prepare (but do not run) a scorer.

## Why this pilot, why these 5 clips

The manager's highest current priority is a manual SignCaption comparison — using the
SignCaption website by hand, not its API (see
`docs/daily_report/9.10/signcaption-signspeak-research/CHECKLIST.md` for why API access
isn't available yet). The 5 clips below are exactly the 5 clips that already have a valid
Gemini native-video prediction (see
`docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md`), so SignCaption can
be slotted into an existing 4-way comparison (Reference / Curify frame baseline / Uni-Sign
/ Gemini native-video) immediately, plus a 5th (trajectory-augmented Gemini) on the 2 of
these 5 clips that also have a Phase-D2 trajectory result.

## Standing legal note (carried over, not resolved here)

`docs/daily_report/9.10/signcaption-signspeak-research/CHECKLIST.md` already flagged that
Sign-Speak's public Customer ToS bars using the service "to create a competitive product"
and licenses uploaded video back to Sign-Speak for training, with no written clearance
obtained. This pilot does not resolve that — it is unchanged by manually using the public
website instead of an API. Recorded here for visibility; not blocking this preparation
step, which makes no upload and no vendor contact itself.

## Verified eligibility (all 5 clips)

Checked directly against the repo — no assumptions:

| clip_id | in frozen manifest | reference `.srt` | source `.mp4` | frame baseline | Uni-Sign | native-video | trajectory (D1/D2) |
|---|---|---|---|---|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | yes | yes | yes | yes (success) | yes (success) | yes (success) | yes |
| `92V3oH63zbQ_5-1-rgb_front` | yes | yes | yes | yes (success) | yes (success) | yes (success) | yes |
| `G05uFub3YFc_9-2-rgb_front` | yes | yes | yes | yes (success) | yes (success) | yes (success) | no |
| `fzNnTgHa1lM_2-5-rgb_front` | yes | yes | yes | yes (success) | yes (success) | yes (success) | no |
| `-g0sqksgyc4_3-2-rgb_front` | yes | yes | yes | yes (success) | yes (success) | yes (success) | no |

"Frame baseline / Uni-Sign / native-video" verified from each system's own
`per_clip_results.json` under `asl-translator/evaluation/results/how2sign_v2/`, read-only —
none of these three systems was rerun to build this pilot. "Trajectory (D1/D2)" verified
from the existence of `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/trajectory_probe/<clip_id>/`
(D1 tracking) and `asl-translator/evaluation/results/how2sign_v2/curify_gemini_trajectory_augmented_2026_09_10/predictions/<clip_id>.json`
(D2 treatment condition) — only `FzmL8SL6Bow_1-8-rgb_front` and `92V3oH63zbQ_5-1-rgb_front`
have both; the other 3 diagnostic clips were never part of the 5-clip D1/D2 probe set, so
"no" here is a real, verified absence, not an omission.

Full per-clip detail (video path, duration, reference text, availability flags, and where
each SignCaption export goes): `pilot_manifest.csv` in this directory.

## What was NOT done

- No SignCaption API call, no SignCaption website automation.
- No Gemini call of any kind.
- No trajectory experiment (D0/D1/D2) was run or re-run.
- No source video or reference file was modified.
- No score was computed — the scorer (`asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/score_pilot.py`)
  is prepared and syntax-checked only; it was dry-run once to confirm it correctly reports
  all 5 clips as `missing` (no fabricated result), and nothing else.
- Nothing staged, committed, or pushed.

## What you do next

Follow `MANUAL_UPLOAD_CHECKLIST.md` in this directory, one clip at a time. Do not run
`score_pilot.py --write-results` until you've placed real SignCaption output for however
many of the 5 clips you complete — it can be run against a partial set (it explicitly
supports and reports `missing` per clip) but every "missing" entry stays unscored, never
approximated.

## Files in this pilot

- `docs/daily_report/9.11/signcaption-manual-pilot/README.md` — this file
- `docs/daily_report/9.11/signcaption-manual-pilot/MANUAL_UPLOAD_CHECKLIST.md` — step-by-step workflow
- `docs/daily_report/9.11/signcaption-manual-pilot/pilot_manifest.csv` — per-clip eligibility/paths/reference text
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/README.md` — results-directory schema
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/clips/<clip_id>/README.md` — per-clip result-slot instructions
- `asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/score_pilot.py` — prepared scorer, **not yet run to completion**
