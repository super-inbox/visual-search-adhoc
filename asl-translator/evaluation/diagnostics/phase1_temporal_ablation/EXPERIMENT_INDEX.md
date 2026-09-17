# Experiment Index — Phase 1–3B Temporal/Architecture Diagnosis

All paths below are relative to `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/`
unless otherwise noted. Chronological order. No new inference was run to
produce this index — it only links and describes already-completed artifacts.

## 0. Baseline denominator note

**`TASK0_baseline_denominator.md`**
Explains why the frozen baseline shows both "128" and "matched 126": Curify/
Gemini 3.6 has 128/128 successful predictions; the matched-126 file is a
cross-model comparability restriction caused by OpenSLT failing on 2 clips,
not a Curify shortfall. Source data:
`../../results/how2sign_v2/curify_gemini_3_6_2026_09_04/corpus_summary.json`
and `corpus_summary_matched_126.json`.

## 1. 12-clip diagnostic set

**`diagnostic_12_clips.json`** / `.csv`, built by **`select_12_diagnostic_clips.py`**
Six fixed, deterministic selection categories (long/multi-batch-boundary risk,
fingerspelling candidate, number-token, fast-signing, question, worst/best-WER
contrast) — no model calls used for selection. This fixed 12-clip set is
reused, unchanged, across every ablation below (3A, 3B) and has its own
frame-level inspector (`inspector/`).

## 2. 40-clip taxonomy + LLM-assisted text-semantic review

- **`taxonomy_40_clips.csv`** / `.json`, built by **`select_40_taxonomy_clips.py`**
  — the 40-clip taxonomy sample (superset including the 12 diagnostic clips).
- **`taxonomy_40_human_review.csv`** / `.json`, served by **`review_app/server.py`**
  — the human-annotation schema and app, later revised to separate TEXT-BASED
  fields (reviewable without ASL fluency) from ASL/VISUAL fields (requiring an
  ASL-fluent reviewer). See **`HUMAN_REVIEW_GUIDE.md`**. Two clips have
  migrated legacy annotations (`hallucination: yes` downgraded to
  `requires_asl_review` once the schema distinguished text-based from
  visually-grounded claims); the rest are unannotated (by design — the human
  reviewer is not ASL-fluent).
- **`taxonomy_40_text_semantic_review.csv`** / `.json`, built inline by the
  assistant in that session (LLM-assisted, not human/ASL-expert) — automatic
  TEXT-BASED semantic comparison (English reference vs. English prediction
  only) for all 40 clips, with every ASL-specific judgment field left blank.
  See **`TEXT_SEMANTIC_REVIEW_SUMMARY.md`** for the full breakdown.

## 3. Paired-76 frame-density probe (2fps vs. 8fps)

**`PAIRED_76_PRELIMINARY_ANALYSIS.md`**, built by **`paired_76_analysis.py`**
from `paired_76_2fps_vs_8fps.csv`. Compares baseline A (2 fps,
`curify_gemini_3_6_2026_09_04`, full 128/128) against Experiment B (8 fps,
`curify_gemini_3_6_2026_09_06_8fps`, **76/128 only** — the remaining 52 are
blocked on a Gemini project billing/spend cap, see
`docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md`) on the
identical 76-clip intersection. **Preliminary and confounded** (not a clean
single-variable ablation — see that file's own "Confounds" section) but the
headline numbers are cited throughout the final reports.

## 4. Phase 3A — adaptive vs. uniform sampling (12 diagnostic clips)

`controlled_ablation/adaptive_vs_uniform_2fps/`:
- `config_or_metadata.json`, `design_check.json` — design/pre-flight (no model calls)
- `predictions/` — 12 new real predictions (config `evaluation_2026_09_07_gemini_3_6_uniform_2fps`)
- `paired_results.csv` / `.json`, `ADAPTIVE_VS_UNIFORM_2FPS.md` — scoring + report
- `inspectors/` — per-clip adaptive-vs-uniform timeline/thumbnail comparison

Built by `controlled_ablation/design_check.py`, `run_uniform_arm.py`,
`score_and_report.py`, `build_comparison_inspector.py`. Adds the new,
additive `allocate_timestamps_uniform()` sampler and one new CONFIGS entry to
`asl-eval/run_current_model.py` (production adaptive sampler and every
pre-existing config unchanged — verified by test suite and diff).

## 5. Phase 3B — independent batches vs. overlapping sliding windows (12 diagnostic clips)

`controlled_ablation/independent_vs_sliding/`:
- `design_check.json` — design/pre-flight (no model calls), including the
  deterministic reference-free ownership-partition merge strategy
- `predictions/` — 12 new real predictions (config `phase3b_independent_vs_sliding_window24_stride12_2026_09_07`)
- `paired_results.csv` / `.json`, `INDEPENDENT_VS_SLIDING.md` — scoring + report
- `inspectors/` — per-clip independent-batch-vs-sliding-window timeline comparison

Built by `controlled_ablation/design_check_sliding.py`, `run_sliding_arm.py`,
`score_and_report_sliding.py`, `build_comparison_inspector_sliding.py`. Makes
**no changes at all** to `asl-eval/run_current_model.py` — reuses it strictly
read-only for the sampler/prompt functions.

## 6. Frame inspectors

- **`inspector/`** — the original Phase-1 frame inspector for the 12
  diagnostic clips (baseline-only: sampled frames, batch boundaries, motion
  trace, word diff vs. reference). Built by `inspector/build_inspector.py`.
- **`controlled_ablation/adaptive_vs_uniform_2fps/inspectors/`** — extends it
  with an adaptive-vs-uniform comparison (Phase 3A).
- **`controlled_ablation/independent_vs_sliding/inspectors/`** — extends it
  with an independent-batch-vs-sliding-window comparison (Phase 3B).

None of the three inspector sets modify or overwrite one another.

## 7. Consolidated final reports (this task)

- **`FINAL_TEMPORAL_DIAGNOSIS.md`** — full auditable consolidation of 0–6
  above, manager's original questions answered, final conclusion, recommended
  next options.
- **`MANAGER_SUMMARY.md`** — short version of the same for a quick read.
- **`EXPERIMENT_INDEX.md`** — this file.
