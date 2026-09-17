# ASL Temporal-Sampling Ablation — Blocker Status

**Date:** 2026-09-06
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Status:** BLOCKED (external billing), not a code/logic failure

## Summary

Experiment B (8 fps temporal-sampling ablation vs. the 2 fps Baseline A) is
implemented, committed, and validated on a real smoke test. The full 128-clip
run is **76/128 complete**; the remaining 52 clips are blocked by the Gemini
project's monthly spending cap, not by any defect in the harness.

## Baseline A (2 fps) — complete

- Status: 128/128 clips succeeded.
- Commit: `b6774164a64fb3383a07623046bd98b8a200c6ba`
- Results directory: `curify_gemini_3_6_2026_09_04/` — untouched by Experiment B.

## Experiment B (8 fps) — implementation complete, run in progress

- Implementation commit: `e32e2ed62509620f75b4af2b4cfdf06a1cc61320`
- Design: controlled ablation — only `target_frames_per_sec` changes (2.0 → 8.0);
  model, prompt, dedup, thinking level, and all other config are identical to
  Baseline A.
- Plan-only (dry run, no network calls): 128 clips, 7,988 sampled frames,
  383 expected Gemini calls.
- Two-clip real smoke test: passed (`FZbyRzy4huk_3-8-rgb_front`,
  `FzmL8SL6Bow_1-8-rgb_front`), config metadata verified on disk.
- Full run: reached **76/128 successful clips** before hitting the blocker
  below. All 76 succeeded on the first attempt (no retries needed) —
  no flakiness observed prior to the cap being hit.

## Blocker

- Error on all 52 remaining clips: `429 RESOURCE_EXHAUSTED` — the Gemini
  project has exceeded its **monthly spending cap**.
- A resume attempt was made after being told the cap should be
  cleared/reset: all 52 clips failed again with the identical error,
  confirming the cap is still exhausted (this is not a transient
  rate-limit that resolves with a short wait or a retry).
- This is an **external billing condition** on the Gemini project, not a
  bug in the evaluation harness, the sampling/prompt logic, or the scoring
  pipeline.

## What is preserved / verified

- The 76 successful Experiment-B predictions are preserved on disk,
  untouched, under their own config metadata.
- Resume behavior is verified end-to-end: re-running the harness against
  the same `--results-dir` skips all 76 completed clips and attempts only
  the 52 that are missing — no re-work and no risk of overwriting valid
  predictions.
- Baseline A's results directory, the frozen benchmark manifest/references,
  and their checksum fingerprint were not touched at any point.

## What is blocked

- Final ALL-128 / MATCHED-126 aggregation and the Baseline-A vs.
  Experiment-B comparison report cannot be produced until all 128 clips
  succeed — a partial-corpus comparison would not be a valid ablation
  result.

## Next step (external, not code)

Raise or reset the Gemini project's monthly spending cap
(https://ai.google.dev/gemini-api/docs/billing#project-spend-caps). Once
confirmed cleared, resume with:

```
python3 asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py \
    --config evaluation_2026_09_06_gemini_3_6_8fps \
    --results-dir asl-translator/evaluation/results/how2sign_v2/curify_gemini_3_6_2026_09_06_8fps
```

This will run only the 52 missing clips, after which full aggregation and
the A/B comparison can proceed.
