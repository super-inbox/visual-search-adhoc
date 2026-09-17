# Manual SignCaption Pilot — How2Sign v2, 5 clips

Results directory/schema for a **manually run** SignCaption pilot. Nothing in this
directory is produced by any script — every result file under `clips/*/` is placed here
by a human using the SignCaption website, per
`docs/daily_report/9.11/signcaption-manual-pilot/MANUAL_UPLOAD_CHECKLIST.md`.

**No SignCaption API was called. No result in this directory is fabricated or assumed.**
An empty/missing `clips/<clip_id>/` result file means SignCaption has not been tried on
that clip yet — never inferred or filled in.

## Scope

5 clips — chosen because they are exactly the 5 clips with a valid Gemini native-video
result (see `docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md`), so
SignCaption can be compared against Reference, Curify frame baseline, Uni-Sign, Gemini
native-video, and (for 2 of the 5) trajectory-augmented Gemini, all at once:

- `FzmL8SL6Bow_1-8-rgb_front`
- `92V3oH63zbQ_5-1-rgb_front`
- `G05uFub3YFc_9-2-rgb_front`
- `fzNnTgHa1lM_2-5-rgb_front`
- `-g0sqksgyc4_3-2-rgb_front`

## Layout

```
how2sign_v2_5clip/
├── README.md                          this file
├── clips/
│   ├── <clip_id>/
│   │   ├── README.md                  per-clip instructions + reference text (already written)
│   │   ├── signcaption_result.srt     <- YOU place this (preferred, if SignCaption exports SRT)
│   │   └── signcaption_result.txt     <- YOU place this (fallback, plain returned text)
│   └── ... (one directory per clip, listed above)
├── results/                            scorer output lands here (created by score_pilot.py, not yet run)
└── score_pilot.py                      prepared scoring script — NOT executed yet
```

## What goes in `clips/<clip_id>/`

Exactly one of:
- `signcaption_result.srt` — SignCaption's own exported caption/subtitle file, unmodified.
- `signcaption_result.txt` — if no file export exists, the exact English caption text
  SignCaption returned, pasted verbatim (empty file if SignCaption returned nothing).

Do not edit either file after saving. Do not create synthetic/placeholder content in
either file — a missing file means "not attempted," not "assumed empty."

## Scoring

`score_pilot.py` is prepared but **has not been run**. It will not run until the 5 result
slots above are manually filled in. See that script's own docstring for exact usage. It
distinguishes three non-equivalent states, never collapsing them:
1. **missing** — no `signcaption_result.{srt,txt}` file exists for a clip.
2. **empty_prediction** — a result file exists but contains no text (a real SignCaption
   output of "nothing," not an error).
3. **parse_failure** — a result file exists and is non-empty but could not be parsed
   (malformed SRT, unreadable encoding, etc.).

SignCaption's output is scored as a **prediction being benchmarked against the frozen
reference** — never treated as ground truth, and never used to correct or re-score any
other system's existing result.
