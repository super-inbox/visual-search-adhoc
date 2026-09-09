# Task 0 — Why baseline A shows both "128" and "matched 126"

No inference was rerun to answer this; it is entirely explained by reading
existing files.

## The two numbers are answering two different questions

| File | Question it answers | n | 
|---|---|---|
| `curify_gemini_3_6_2026_09_04/corpus_summary.json` | "Of the 128 frozen How2Sign v2 clips, how many did **Curify/Gemini 3.6** itself successfully produce and score a prediction for?" | `n_total=128`, `n_success=128`, `n_failure=0` |
| `curify_gemini_3_6_2026_09_04/corpus_summary_matched_126.json` | "Restricting to only the clips where **every model being compared** (Curify, OpenSLT, Uni-Sign) has a usable prediction, what is Curify's corpus WER on that common subset?" | `matched_count=126`, `n_of_matched_set_actually_scored_here=126` |

Curify/Gemini 3.6 has **128/128** predictions on disk — nothing is missing on
the Curify side. The matched-126 file is not reporting a Curify shortfall; it
is reporting a **cross-model comparability restriction** caused by a different
model (OpenSLT) failing on 2 of the 128 clips.

## The exact mechanism (`run_curify_how2sign_v2_benchmark.py`)

`compute_matched_subset()` (lines 219–233) builds the matched set by
excluding, from all 128 manifest IDs, any clip ID present in:

- `load_openslt_missing_ids()` (lines 203–208) — reads
  `evaluation/results/how2sign_v2/openslt/run_metadata.json`'s
  `how2sign_v2_clips_missing` list.
- `load_unisign_missing_ids()` (lines 211–216) — reads
  `evaluation/results/how2sign_v2/unisign/per_clip_results.json` for any row
  with `status != "success"`.

`aggregate()` (lines 475–509) then writes **both** files every run:
`corpus_summary.json` (all 128 Curify predictions, Curify's own denominator)
and `corpus_summary_matched_126.json` (the 126-clip intersection, for
apples-to-apples Curify-vs-OpenSLT/Uni-Sign comparison only).

## The 2 excluded clips, and why

```json
"excluded_ids": ["G3EfBFwsOpE_3-10-rgb_front", "fZK9hW81XCU_9-10-rgb_front"],
"excluded_from_openslt": ["G3EfBFwsOpE_3-10-rgb_front", "fZK9hW81XCU_9-10-rgb_front"],
"excluded_from_unisign": []
```

Both exclusions come from `openslt/run_metadata.json`'s
`how2sign_v2_clips_missing` — i.e. OpenSLT failed/could not run on these 2
clips. Uni-Sign has **0** missing clips (`unisign/per_clip_results.json`, all
128 rows `status == "success"`). Curify/Gemini 3.6 also has 0 missing clips.
So the "126" ceiling in this benchmark round is entirely attributable to
OpenSLT, not to Curify or to Uni-Sign.

## Practical takeaway for Phase 1 / the ablation

- **Use `corpus_summary.json` (n=128)** for anything Curify-only: baseline vs.
  ablation-arm comparisons, the 12-clip diagnostic set, the 40-clip taxonomy.
  All 128 clips have a valid Curify prediction; there is no reason to drop
  the 2 OpenSLT-missing clips from a Curify-internal analysis.
- **Use `corpus_summary_matched_126.json`** only if a claim is being made that
  also cites OpenSLT or Uni-Sign numbers side-by-side with Curify's.
- The 8 fps ablation run (`curify_gemini_3_6_2026_09_06_8fps`) has its own,
  separate shortfall (76/128, blocked on Gemini billing — see
  `docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md`) that is
  unrelated to this 126/128 distinction and must not be conflated with it.
