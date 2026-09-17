# Manual SignCaption Pilot — Batch 2 (10 new clips, n=5 → n=15)

Results directory/schema for **Batch 2** of the manually-run SignCaption pilot. Same
convention as the original 5-clip pilot
(`asl-translator/evaluation/manual_signcaption/how2sign_v2_5clip/`) — nothing in this
directory is produced by any script; every result file under `clips/*/` is placed here by
a human using the SignCaption website, per
`docs/daily_report/9.13/signcaption-batch2-manual-pilot/MANUAL_UPLOAD_CHECKLIST.md`.

**No SignCaption API was called. No result in this directory is fabricated or assumed.**
An empty/missing `clips/<clip_id>/` result file means SignCaption has not been tried on
that clip yet — never inferred or filled in. **The original 5-clip pilot's results
(`how2sign_v2_5clip/`) are read-only from here and are not modified by this batch.**

## Scope: 10 new clips, selected to diversify the original 5-clip pilot

Selected via stratified sampling over the 123 clips eligible after excluding the original
5 (frozen reference + local `.mp4` + successful Curify + successful Uni-Sign required for
eligibility): duration tercile × Curify-WER tercile × Uni-Sign-WER tercile, 3 drawn from
the (at selection time) still-partly-unresolved diagnostic-12 subset and 7 from outside
it. Full selection rationale, the eligibility audit, and the bias assessment:
`docs/daily_report/9.13/signcaption-batch2-manual-pilot/pilot_manifest_batch2.csv` and
`README.md` in that same directory.

- `g2NA_eBUcH8_0-3-rgb_front` (diagnostic-12)
- `G19uBylwQww_1-2-rgb_front` (diagnostic-12)
- `fZM3IcM2Xs4_14_15_16-10-rgb_front` (diagnostic-12)
- `g2nvBjp0loQ_4-3-rgb_front`
- `g05yGRoZE10_1-8-rgb_front`
- `FzQPg4aqNYc_13-1-rgb_front`
- `G3RvsnzQrXQ_3-10-rgb_front`
- `g0UUmEkoT1w_2-10-rgb_front`
- `FZCEymcpq7I_14-1-rgb_front`
- `G1jsDl1mVvk_1-1-rgb_front`

**A note on the manifest's `number_token` / `fingerspelling_candidate` / `question` /
`fast_signing` tags, referenced in the per-batch selection docs:** these are
**reference-text-derived heuristic labels** (e.g. "does the English reference text contain
a digit or number word," "does it end in a question mark") computed by the benchmark's own
selection scripts from the frozen English reference — **not** human-verified ASL visual
content categories, and not a claim that any of these clips were confirmed by an
ASL-fluent reviewer to contain fingerspelling, fast signing, or a signed question. Several
are explicitly marked `[HEURISTIC, manual review needed]` in the manifest itself. Treat
them as weak, text-side priors for stratification only.

## Native-video coverage note (combined n=15)

All 5 original pilot clips already have valid Gemini native-video predictions (they were,
in fact, the exact 5 clips chosen for the original pilot specifically because they had
native-video results). 3 of these 10 Batch-2 clips are diagnostic-12 members that gained a
valid native-video prediction in the 2026-09-13 diagnostic-12 retry. **Combined native-video
coverage across all 15 SignCaption-pilot clips (original 5 + Batch 2) is 8/15** — the
other 7 Batch-2 clips have no native-video prediction and none will be fabricated; the
4-way (Curify / Uni-Sign / native-video / SignCaption) comparison stays a matched 8/15
subset, reported separately from the full matched-15 3-way (Curify / Uni-Sign /
SignCaption) comparison.

## Layout

```
how2sign_v2_batch2_10clip/
├── README.md                          this file
├── clips/
│   ├── <clip_id>/
│   │   ├── README.md                  per-clip instructions + reference text (already written)
│   │   ├── signcaption_result.srt     <- YOU place this (preferred, if SignCaption exports SRT)
│   │   └── signcaption_result.txt     <- YOU place this (fallback, plain returned text)
│   └── ... (one directory per clip, listed above)
├── results/                            scorer output lands here (created by score_batch2_and_combined.py, not yet run)
└── score_batch2_and_combined.py        prepared scoring script — NOT executed yet
```

## What goes in `clips/<clip_id>/`

Exactly one of:
- `signcaption_result.srt` — SignCaption's own exported caption/subtitle file, unmodified.
- `signcaption_result.txt` — if no file export exists, the exact English caption text
  SignCaption returned, pasted verbatim (empty file if SignCaption returned nothing).

Do not edit either file after saving. Do not create synthetic/placeholder content in
either file — a missing file means "not attempted," not "assumed empty."

## Scoring

`score_batch2_and_combined.py` is prepared but **has not been run** (no Batch-2 results
exist yet). Once some or all of the 10 slots are filled, it will report, without
fabricating any missing prediction:
- Batch-2-only aggregate (n up to 10, whatever is actually filled)
- Combined aggregate across all 15 pilot clips (original 5 + Batch 2), official
  corpus-level WER/CER/BLEU/chrF (same convention as the original pilot's audited §3b
  table — edit counts summed then divided once; BLEU/chrF via one `sacrebleu.corpus_score()`
  call over all available hypothesis/reference pairs)
- SignCaption vs. Uni-Sign vs. Curify frame-baseline on all 15
- SignCaption vs. Uni-Sign vs. Curify vs. native-video on the matched 8/15 subset only
  (never silently extrapolated to the other 7)
- Placeholders for semantic-adequacy / topic-mismatch / genuine-recovery review — these
  are a text-based English-reference-vs-English-prediction judgment call, not computed by
  this script, and are left blank until filled in by the same review process used for the
  original 5 (never auto-filled or inferred from WER).
