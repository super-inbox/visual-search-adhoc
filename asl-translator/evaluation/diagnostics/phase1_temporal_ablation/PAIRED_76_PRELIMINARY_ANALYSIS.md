# Paired 76-clip PRELIMINARY comparison — baseline A (2 fps) vs. Experiment B (8 fps)

**PRELIMINARY. This is NOT a clean causal fps experiment.** See "Confounds"
below before drawing any conclusion from these numbers. No model call was
made to produce this analysis — it reads only the already-saved
`per_clip_results.json` from both existing runs and reuses
`run_curify_how2sign_v2_benchmark.py`'s own `_corpus_wer_cer()` aggregation.

## Pairing

- Experiment B (`curify_gemini_3_6_2026_09_06_8fps`) has completed exactly
  **76** of 128 frozen clips (the rest failed on `429
  RESOURCE_EXHAUSTED` — Gemini project monthly spend cap, an external billing
  block, not a code issue; see `docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md`).
- Baseline A (`curify_gemini_3_6_2026_09_04`) is scored on the **identical**
  76 clip IDs only — not its full 128 — so every number below
  compares the same clips under both configs.

## Headline numbers (paired 76-clip subset)

| metric | baseline A (2 fps) | Experiment B (8 fps) |
|---|---|---|
| corpus WER (pooled substitutions+deletions+insertions / reference words) | 0.973 | 0.9715 |
| mean per-clip WER | 0.9836 | 0.9785 |
| corpus CER | 0.8084 | 0.7763 |

- **Absolute corpus WER delta (8fps − baseline):** -0.0015
- **Relative corpus WER delta:** -0.15% of baseline corpus WER
- **Median per-clip WER delta:** +0.0000
- **Clips improved** (8fps WER < baseline WER): 15 / 76
- **Clips worsened** (8fps WER > baseline WER): 20 / 76
- **Clips unchanged** (exact WER tie): 41 / 76

## Largest improvements (most negative delta)

- `fZM3IcM2Xs4_14_15_16-10-rgb_front` — baseline WER 1.913, 8fps WER 1.0435, delta -0.8695 (baseline 2 batch(es) @ 2.0 fps -> 8fps 7 batch(es) @ 8.0 fps)
- `G3di9jJTqDs_0-10-rgb_front` — baseline WER 1.0, 8fps WER 0.8, delta -0.2000 (baseline 1 batch(es) @ 16.0 fps -> 8fps 1 batch(es) @ 16.0 fps)
- `g1HXoDkax5A_15-3-rgb_front` — baseline WER 1.0, 8fps WER 0.875, delta -0.1250 (baseline 1 batch(es) @ 16.0 fps -> 8fps 1 batch(es) @ 16.0 fps)
- `FZbyRzy4huk_3-8-rgb_front` — baseline WER 1.0, 8fps WER 0.9286, delta -0.0714 (baseline 2 batch(es) @ 2.0 fps -> 8fps 7 batch(es) @ 7.949 fps)
- `-fZc293MpJk_5-1-rgb_front` — baseline WER 1.0, 8fps WER 0.95, delta -0.0500 (baseline 1 batch(es) @ 4.174 fps -> 8fps 2 batch(es) @ 7.826 fps)

## Largest regressions (most positive delta)

- `g2NA_eBUcH8_0-3-rgb_front` — baseline WER 0.75, 8fps WER 0.9167, delta +0.1667 (baseline 1 batch(es) @ 8.727 fps -> 8fps 1 batch(es) @ 8.727 fps)
- `G0PNAsonBGk_11-2-rgb_front` — baseline WER 1.0, 8fps WER 1.1538, delta +0.1538 (baseline 1 batch(es) @ 4.0 fps -> 8fps 2 batch(es) @ 8.0 fps)
- `fzcsY2gm7t0_8-8-rgb_front` — baseline WER 0.9167, 8fps WER 1.0, delta +0.0833 (baseline 1 batch(es) @ 6.4 fps -> 8fps 2 batch(es) @ 8.0 fps)
- `fZgbCwSG3Hc_4-8-rgb_front` — baseline WER 0.9167, 8fps WER 1.0, delta +0.0833 (baseline 1 batch(es) @ 6.4 fps -> 8fps 2 batch(es) @ 8.0 fps)
- `G0peUY2cfeE_2-2-rgb_front` — baseline WER 0.875, 8fps WER 0.9583, delta +0.0833 (baseline 1 batch(es) @ 2.133 fps -> 8fps 4 batch(es) @ 8.0 fps)

## Stratified by existing manifest/run metadata (paired subset only)

| stratum | n | baseline corpus WER | 8fps corpus WER | corpus WER delta | mean per-clip delta |
|---|---|---|---|---|---|
| fingerspelling candidate | 24 | 0.9967 | 0.9734 | -0.0233 | -0.0294 |
| number token | 28 | 0.9634 | 0.9657 | 0.0023 | 0.0091 |
| fast signing | 12 | 0.9595 | 0.9711 | 0.0116 | 0.0064 |
| question | 11 | 0.9597 | 0.9758 | 0.0161 | 0.0068 |
| plain / no heuristic flag | 16 | 0.951 | 0.9673 | 0.0163 | 0.0084 |
| single-batch at baseline (2 fps) | 58 | 0.97 | 0.9797 | 0.0097 | 0.007 |
| multi-batch at baseline (2 fps) | 18 | 0.9763 | 0.9623 | -0.014 | -0.044 |
| shorter clips (< median 5.79s) | 38 | 0.9676 | 0.979 | 0.0114 | 0.0052 |
| longer clips (>= median 5.79s) | 38 | 0.975 | 0.9687 | -0.0063 | -0.0154 |

"single-batch vs multi-batch" is stratified on **baseline's own** batch count
(2 fps): a clip's batch count can differ between configs since 8 fps samples
more frames from the same duration (see Confound 3 below) — per-clip
`baseline_model_calls` / `eightfps_model_calls` are both in
`paired_76_2fps_vs_8fps.csv` so this shift is visible per clip.

"shorter vs longer" splits the paired 76 at the median duration
(5.79s) within this subset, not the full 128-clip corpus.

## Confounds — why this is NOT a clean fps-only comparison

1. **Both configs use motion-weighted/adaptive timestamp allocation.**
   Neither baseline A nor Experiment B samples frames at a uniform rate —
   both spend their frame budget proportional to motion energy
   (`allocate_timestamps()` in `run_current_model.py`, unchanged between the
   two configs). Any change observed here reflects "more frames allocated by
   the same motion-weighted rule," not "denser uniform temporal sampling."
2. **Target frame density changes (2.0 -> 8.0 target_frames_per_sec)** is
   the one deliberate variable — but see confound 3, it does not act alone.
3. **A fixed 24-frame batch spans different amounts of video time at
   different target fps.** At 2 fps a 24-frame batch covers roughly 12s of
   video; at 8 fps the same 24 frames cover roughly 3s. So any WER delta
   conflates "denser motion-weighted sampling" with "shorter, more
   self-contained time span per independent model call" — these are not
   separated by this data.
4. **Independent batching is unchanged.** Both configs still send batches of
   24 frames to the model with zero shared context between batches
   (confirmed in `run_current_model.run_real()` — see `PHASE1_SUMMARY.md`
   §2). Any seam-crossing failure mode is present, unchanged in mechanism,
   in both arms; only how much time a given seam represents changes.
5. **Partial-corpus subset.** 76/128 is not a random sample of the
   benchmark — it is manifest-order prefix up to where the spend cap hit
   (see `run_curify_how2sign_v2_benchmark.py`'s frozen-manifest-order
   iteration). No claim here generalizes to the full 128 without the
   remaining 52 clips.

**Do not report any WER delta in this file as caused by fps.** It is
reported as an observed, confounded, paired difference on a partial corpus,
to be revisited once a controlled ablation (isolating sampling strategy,
frame density, and batch/context effects — see `PHASE1_SUMMARY.md` §7) is
actually run.

## Files

- `paired_76_2fps_vs_8fps.csv` — one row per paired clip, both configs' WER,
  frame/batch/density metadata, and manifest heuristic hints.
- This file (`PAIRED_76_PRELIMINARY_ANALYSIS.md`).

## No inference performed

This script imports only `run_curify_how2sign_v2_benchmark.py` for its
`_corpus_wer_cer()` aggregation helper (pure arithmetic, no I/O to Gemini)
and reads only already-saved `per_clip_results.json` / `manifest.csv` files.
`google.genai` is not imported anywhere in this script; `GEMINI_API_KEY` is
never read.
