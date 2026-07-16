# automated_relevance_run_log.md

Run ID: `curify-easy-query-automated-relevance-eval-2026-07-15-16`
Task: AUTOMATED_RELEVANCE_EVALUATION_FOR_ALL_328_EASY_QUERIES
Baseline root: `docs/daily_report/7.15/easy-query-production-baseline-v1`
Output directory: `automated_relevance_evaluation-v1` (first available slot; created fresh, not overwriting anything)

## Timeline (as recorded in checkpoints/ timestamps and this session)

1. **Phase 1 — Input audit.** Verified 328/328 query-level records, 328 raw files, 328
   screenshots, unique/contiguous query_index, 0 order/text mismatches, 0 corrupt files, 0
   unexplained gaps. Result: `INPUT_AUDIT.md`, `input_integrity.json`. No blocking condition.
2. **Phase 2 — Rubric.** `RELEVANCE_RUBRIC.md` drafted and locked as rubric-v1, with one
   clarifying revision (rubric-v1.1) made *before* the scored calibration runs, documented in
   `CALIBRATION_REPORT.md`. Scoring formula implemented once, in `scripts/scoring.py`, and reused
   unchanged by every subsequent phase (calibration, first pass, second pass).
3. **Phase 3 — Evidence packets.** `evidence/query_packets.json` built (328 structured packets:
   original query, rewrite/broaden fields, zero/low-result flags, all visible Top Results with
   title/URL-slug/metadata).
4. **Phase 4 — Calibration (30 queries).** Two independent passes (A/B) with full TEXT_PLUS_VISUAL
   evidence (screenshots actually opened). Query-level label agreement: 30/30 = 100%. Result:
   `CALIBRATION_REPORT.md`, `calibration_results.csv`.
5. **Phase 5 — First pass (328 queries, 17 batches of ~20).** Every query evaluated against
   rubric-v1.1; TEXT_PLUS_VISUAL for the calibration set + all zero-result queries + spot audits,
   TEXT_EVIDENCE_ONLY for the rest (disclosed in MODEL_AND_METHOD.md). Aggregated into
   `checkpoints/master_query_level_first_pass.csv` (328 rows) and
   `checkpoints/master_result_level_first_pass.jsonl` (1,511 rows). First-pass label distribution:
   PASS 97 / PARTIAL 102 / FAIL 129 / UNJUDGABLE 0.
6. **Phase 6 — Second-pass population selection.** `checkpoints/second_pass_population.json` built:
   tier1_deep_reverify (54, covers every mandatory category from task spec Sec.15.2 items 1-6),
   tier2_consistency_audit (219, remaining mandatory-category queries).
7. **Phase 7 — Second-pass execution (this continuation).**
   - Tier1 (54): independent Pass-B re-derivation from the same text evidence, without consulting
     first-pass labels first. Raw label agreement 45/54 = 83.3%. 12 queries needed adjudication
     (9 label disagreements + 3 same-label-large-score-delta cases); 3 flipped PASS→PARTIAL.
   - Tier3 (10, added in this continuation): deterministic random 10%+ audit of the 55 PASS
     queries untouched by tier1/tier2 — found 1 additional label flip (query 233, 旅行者)
     via the same audience-vs-subject conflation pattern discovered in tier1.
   - Tier2 (219) + full-corpus sanity pass: mechanical rubric-consistency audit
     (`scripts/07_second_pass_and_finalize.py`) re-applying the locked scoring formula to every
     row's own recorded result-level labels. **0 rule violations found across all 328 queries.**
   - Adjudication reasoning and 3 reusable policy decisions recorded in
     `review/adjudication_report.md`.
8. **Phase 8 — Final dataset.** `checkpoints/master_query_level_final.csv` /
   `master_result_level_final.jsonl` built by applying the 13 second-pass overrides on top of the
   first-pass master. Final label distribution: **PASS 93 / PARTIAL 106 / FAIL 129 / UNJUDGABLE 0**
   (328 total, sum verified).
9. **Phase 9 — Deliverables.** All `final/` CSV/JSONL exports, per-label subsets, manual review
   queue (P0 72 / P1 78 / P2 51), rewrite analysis, zero/low-result analysis, summary statistics,
   integrity report, file manifest — built by `scripts/08_build_deliverables.py` and
   `scripts/09_integrity_and_manifest.py`, all read-only against the checkpoints/ final dataset.
10. **Phase 10 — Reports and safety.** This log, the Chinese report, `WORKTREE_SAFETY_REPORT.md`,
    and the baseline-root pointer file `AUTOMATED_RELEVANCE_EVALUATION_ADDED.md`.

## Actions explicitly NOT taken

- No HTTP request was made to `https://www.curify-ai.com` or any other production endpoint during
  this run (verified: no network-calling code exists anywhere in `scripts/`; all scripts operate
  only on local files under `raw/`, `screenshots/`, `final/`, `checkpoints/`, `evidence/`).
- No file under `raw/`, `screenshots/`, `query_input/`, or any `final/easy_query_production_baseline_*`
  path (the original baseline deliverables) was opened in write mode by any script in this run.
- No git commit, no git push, performed by this run.
- No production code (this repo contains no Curify application source; it is a docs/evaluation
  workspace) was touched.
