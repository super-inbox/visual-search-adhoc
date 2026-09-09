# Phase 1 — Temporal Architecture Diagnosis: Summary

**Scope of this phase:** representative-case inspection + qualitative
taxonomy preparation only. No Gemini API calls were made, the blocked 8 fps
run was not resumed, no new ablation arm (5/10 fps, sliding windows, direct
video) was implemented, and nothing was committed.

---

## 1. What the current "2 fps" sampler actually does

It is **not** uniform 0.5s-interval sampling. `asl-eval/run_current_model.py`:

1. `TARGET_FRAMES_PER_SEC = 2.0` sets a **total frame budget** for the clip:
   `budget_for_duration()` = `round(duration_s * 2.0)`, clamped to
   `[MIN_FRAME_BUDGET=24, MAX_FRAME_BUDGET=240]`.
2. That budget is then **spent non-uniformly** by `allocate_timestamps()`:
   a motion probe (`probe_motion`, 4 fps grayscale frame-diff) is segmented
   into active/idle runs (`segment_runs`), and each active run gets a share
   of the budget proportional to its motion energy. High-motion stretches
   get many frames; static stretches get few or none.

**Consequence confirmed by the 12-clip inspector:** frames cluster where the
signer is moving fastest — which is frequently the *worst* place for a still
image to carry legible handshape (fast transitions blur). This reproduces,
on the frozen How2Sign v2 corpus, the same "fingerspelling dies because the
sampler works" pattern the private-corpus 1252 inspector documented.

## 2. What independent 24-frame batching actually does

`BATCH_SIZE = 24`. `run_real()` splits the sampled frames into chunks of 24
and issues one `generate_content` call per chunk, each with a fresh
single-turn prompt (frames + static instructions only). Confirmed by direct
code reading: **no conversation history, no prior segments, no prior frames
are passed between batches.** The only cross-batch step is a client-side,
text-only `merge_adjacent_duplicates()` applied *after* every batch has
already returned independently.

The 12-clip inspector operationalizes this: for every model output segment,
it flags whether that segment's nearest sampled frame sits within 1 frame of
a batch boundary ("near_batch_seam"). Multi-batch clips in the diagnostic set
(`FzmL8SL6Bow_1-8-rgb_front`, 3 batches, 1 flagged segment;
`fzNnTgHa1lM_2-5-rgb_front`, 3 batches, 2 flagged;
`fZM3IcM2Xs4_14_15_16-10-rgb_front`, 2 batches, 2 flagged;
`G05uFub3YFc_9-2-rgb_front`, 2 batches, 2 flagged) show real candidate
seam-crossing cases to review frame-by-frame.

## 3. Why this matters for the manager's temporal hypothesis

The manager's controlled-ablation request explicitly says: preserve temporal
order, do **not** optimize around motion peaks. But the **current
production/baseline path already does the opposite** — it is a motion-peak
adaptive sampler, not a naive fixed-rate one. That means:

- Baseline A (2 fps) and the partial Experiment B (8 fps) both inherit
  motion-weighted allocation; only the *budget* changes between them, not the
  allocation *strategy*. A future "uniform 5/10 fps" arm would change **two**
  things vs. baseline at once (density AND strategy) unless it deliberately
  keeps motion-weighting and only changes the target density, or explicitly
  adds a separate uniform-sampling arm to isolate strategy from density.
- Batching is confirmed independent, so any coverage/deletion problem that
  correlates with batch-seam-adjacent segments is a batching artifact, not a
  sampling-density artifact — the two need separate ablation arms (see §7).

## 4. Which 12 clips were selected, and why

Selected deterministically by `select_12_diagnostic_clips.py` from the full,
already-scored 128-clip baseline A results (no reference to WER-only
extremes as the sole criterion) — six categories, 2 clips each, overlap
allowed:

| clip_id | WER | duration_s | model_calls | reason(s) |
|---|---|---|---|---|
| FzmL8SL6Bow_1-8-rgb_front | 0.9615 | 25.77 | 3 | long/multi-batch |
| fzNnTgHa1lM_2-5-rgb_front | 0.9412 | 25.31 | 3 | long/multi-batch |
| fZM3IcM2Xs4_14_15_16-10-rgb_front | 1.913 | 18.67 | 2 | fingerspelling candidate, very-high-WER |
| -g0iPSnQt6w_0-1-rgb_front | 1.0 | 3.51 | 1 | fingerspelling candidate, fast-signing/question |
| G05uFub3YFc_9-2-rgb_front | 1.0294 | 17.49 | 2 | number-token |
| -g0sqksgyc4_3-2-rgb_front | 1.0 | 5.35 | 1 | number-token, fast-signing/question |
| 92V3oH63zbQ_5-1-rgb_front | 1.0 | 1.83 | 1 | fast-signing/question |
| Fz-N1S0swh8_2-8-rgb_front | 1.0 | 2.27 | 1 | fast-signing/question |
| g0TkUiO7t4I_6-8-rgb_front | 1.4444 | 5.56 | 1 | very-high-WER |
| g2ELiaFjKfs_3-10-rgb_front | 1.1429 | 4.87 | 1 | very-high-WER |
| g2NA_eBUcH8_0-3-rgb_front | 0.75 | 2.87 | 1 | low-WER contrast |
| G19uBylwQww_1-2-rgb_front | 0.8077 | 4.53 | 1 | low-WER contrast |

Full record (reference text, baseline prediction text, frames_sampled,
sampling_density_fps, manifest heuristic tags) is in
`diagnostic_12_clips.json` / `.csv`.

## 5. How the 40-clip taxonomy sample was constructed

`select_40_taxonomy_clips.py`: the same 12 clips above, unconditionally
included, plus 28 more chosen by **manifest heuristic category quotas**
(modeled on `openslt/category_breakdown.json`'s bucket names for
cross-reference), ranked **alphabetically by clip_id within each category**
— deliberately not WER-ranked, so this expansion adds *coverage*, not more
worst-case bias:

| category | quota |
|---|---|
| number_token_HEURISTIC | 6 |
| proper_noun_fingerspelling_HEURISTIC | 6 |
| fast_signing_HEURISTIC | 4 |
| question_official | 4 |
| duration_15-31s (extra long/multi-batch coverage) | 3 |
| duration_lt_2s (near the 24-frame budget floor) | 2 |
| plain_no_flag (control group, no heuristic tag at all) | 3 |

All 7 quotas filled exactly (28/28); 12 + 28 = 40.

## 6. What remains human annotation vs. automatically derived

**Automatically derived / prefilled** in `taxonomy_40_clips.csv`: `clip_id`,
`duration_s`, `duration_bucket`, `reference`, `baseline_prediction`,
`baseline_wer`, `frames_sampled`, `model_calls_baseline`,
`n_batches_baseline`, `sampling_density_fps_baseline`, `hint_number_token`,
`hint_fingerspelling_candidate`, `hint_fast_signing`, `hint_question`,
`in_phase1_12clip_inspector`, `reason_selected`.

The `hint_*` columns are manifest text/WPS heuristics on the **English
reference translation**, not confirmed visual content of the sign video —
they are hints for the reviewer, not answers.

**Left entirely blank for human review**, per instruction not to auto-invent
labels: all `content__*` tags (handshape_sensitive, motion, fingerspelling,
numbers, facial_non_manual, fast_signing, other), all `failure__*` tags
(handshape, motion, fingerspelling, numbers, facial_non_manual,
segmentation, hallucinated_topic, repetition,
correct_meaning_different_english, other), and all semantic columns
(`semantic_adequacy`, `hallucination`, `fps_might_help`,
`batch_boundary_might_help`, `notes`). The 12-clip inspector's per-segment
`near_batch_seam` flag is visible in the inspector pages (not copied into
the 40-clip CSV as an answer) to inform, not pre-answer,
`batch_boundary_might_help`.

## 7. Recommended next controlled-ablation design (NOT implemented)

The core problem to solve first, per §3: baseline sampling is
**motion-weighted**, but the manager wants a **temporal-density** experiment
that does not optimize around motion peaks. Recommend separating three
effects that are currently confounded together:

- **A. Sampling-strategy effect** (motion-weighted vs. uniform-in-time
  allocation at the *same* frame budget). Needs a new, explicit "uniform"
  allocator as an alternative to `allocate_timestamps()` — not a config
  override, an actual second code path — so a run can hold budget fixed and
  swap only the allocation rule.
- **B. Frame-density effect** (2 vs. 5 vs. 8 vs. 10 fps target budget,
  allocation strategy held fixed — this is the one axis the existing
  `target_frames_per_sec` config override already isolates cleanly, as
  Experiment B does).
- **C. Batch/context effect** (independent 24-frame batches vs. overlapping
  sliding windows vs. a larger single batch/native video, density and
  strategy both held fixed).

Minimal recommended matrix once Phase 1 review is complete:

| Arm | Allocation | Density | Batching |
|---|---|---|---|
| A0 (frozen baseline) | motion-weighted | 2 fps | independent 24-frame |
| A1 | **uniform** | 2 fps | independent 24-frame |
| B1 (built, partial) | motion-weighted | 8 fps | independent 24-frame |
| B2 | **uniform** | 8 fps | independent 24-frame |
| C1 | motion-weighted | 2 fps | **sliding/overlapping window** |

A0 vs. A1 isolates strategy (A) at fixed density. A0 vs. B1 isolates density
(B) at fixed (motion-weighted) strategy — already available from existing
partial data once B1 finishes. A0 vs. C1 isolates batching (C) at fixed
density and strategy. B1 vs. B2 cross-checks whether the strategy effect
holds at higher density too. This is a proposal for review, not a build
order.

### The 24-frame-batch-spans-different-time confound (explicit)

At 2 fps a 24-frame batch spans ≈12s; at 8 fps the same 24-frame batch spans
≈3s. So "batch size in frames" is not "batch size in time" once density
changes — any WER delta between a 2 fps and an 8 fps arm mixes (i) denser
sampling of the same time span with (ii) a shorter, more self-contained time
window per independent model call (less chance a sign/sentence straddles a
seam). Two ways to handle this, for the manager to choose, not yet built:

1. **Scale `BATCH_SIZE` with fps** so batch *time-span* stays constant
   (≈12s) across density arms — cleanly isolates B (density) from C
   (batching), at the cost of changing C's frame-count between arms.
2. **Keep `BATCH_SIZE` fixed at 24** (current design) and report the
   shrinking batch time-span explicitly as a known, uncontrolled covariate
   of the density arms, rather than eliminating it.

Recommend (1) for any arm meant to isolate density alone, and reserving
fixed-`BATCH_SIZE`-24 comparisons for arms explicitly about batching (C).

---

## Files created

```
asl-translator/evaluation/diagnostics/phase1_temporal_ablation/
├── TASK0_baseline_denominator.md
├── PHASE1_SUMMARY.md                      (this file)
├── select_12_diagnostic_clips.py
├── diagnostic_12_clips.json
├── diagnostic_12_clips.csv
├── select_40_taxonomy_clips.py
├── taxonomy_40_clips.json
├── taxonomy_40_clips.csv
└── inspector/
    ├── build_inspector.py
    ├── index.html
    └── <12 clip_id>.html
```

No files outside this new directory were created or modified.

## Validation performed

- `select_12_diagnostic_clips.py` run to completion: asserts exactly 12
  unique clips, all six category quotas satisfied; printed selection
  matches the table in §4.
- `select_40_taxonomy_clips.py` run to completion: asserts exactly 40
  unique clips (12 fixed + 28), all seven category quotas filled exactly
  (6/6/4/4/3/2/3); CSV spot-checked (38 columns, correct header order,
  human-judgment columns empty, `hint_*`/machine columns populated).
- `build_inspector.py` run to completion for all 12 clips: for every clip,
  the re-derived sampling (`probe_motion → segment_runs → allocate_timestamps`
  with that clip's own recorded `frame_budget`) reproduced the exact
  `frames_sampled` count recorded in its saved baseline prediction
  (`frame_count_mismatch: False` for all 12 clips) — confirms the inspector
  is showing the actual frames the real run used, not an approximation.
  Frame extraction, batch/seam computation, and word-diff rendering
  completed for all 12 pages (file sizes 81 KB–192 KB; `index.html` links
  to all 12).

## No inference calls made

No `GEMINI_API_KEY`-gated code path (`run_real()`, `google.genai`) was
imported or invoked anywhere in this phase. All scripts call only
`probe_motion` / `segment_runs` / `allocate_timestamps` (local ffmpeg/numpy)
and read already-saved prediction/reference files. `run_curify_how2sign_v2_benchmark.py`
was not invoked. The blocked 8 fps run (`curify_gemini_3_6_2026_09_06_8fps`,
76/128) was not resumed or touched.

## Git status

New, untracked files only, under
`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/`. Nothing
staged or committed — see the actual `git status` output reported alongside
this summary in the conversation.
