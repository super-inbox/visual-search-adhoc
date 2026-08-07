# cases/

## zcool_ce_001/ (new, Phase 6 — first formal case record)

The first and only formally cleaned, structured workflow case in this task's lineage, produced from Phase 5's sole `SELECT` candidate (`ZCE-CAND-001`, 8/9, 「韩娱嘉年华」品牌视觉升级全流程分享). Contains `CASE_SUMMARY.md`, `QUALITY_REVIEW.md`, `FORMAL_WORKFLOW_CLEANING_FINDINGS.md`, `source_metadata.json`, `workflow_extraction.json` (9 steps, `ZCE-WF-001`..`ZCE-WF-009`), and `evidence_manifest.csv` (11 evidence rows, all cross-referenced with zero orphans). `workflow_completeness=substantial`; `usable_for_workflow_training=true` — the first `true` in this task's lineage, since it is the only case with both real sketch-exploration and side-by-side final-comparison visual evidence, but **not** usable as a selection-decision training example (`has_selection_reason=false`, unchanged from Phase 5). No new zcool page was fetched, no new screenshot taken, no images downloaded this phase — cleaning was done entirely from Phase 5's already-captured screenshot and findings narrative. See `FORMAL_WORKFLOW_CLEANING_FINDINGS.md` for the full phase writeup and open items.

A schema-conformant copy of this case (matching `baseline_pilot/structured_cases/pilot_cases.jsonl`'s `{case, steps[], missing_stages[], assets[]}` shape) is written to `../outputs/creative_exploration_workflows.jsonl`.

## CASE_QUERY_ELIGIBILITY.csv (Phase 3)

Query-derivation eligibility analysis of the 5 cases already migrated into `../baseline_pilot/structured_cases/raw_cases/` (`case_001`..`case_005`). Judged strictly from existing structured-case evidence (`workflow_extraction.json`, `source_metadata.json`, `REVIEW.md`, `asset_manifest.csv`, plus the cross-case `pilot_cases.jsonl`, `case_quality_review.csv`, and `PILOT_FINDINGS.md`) — `raw_text.md` was never read, per task instruction. Result: 4/5 cases (`case_001`–`case_004`) eligible for brief-derived queries; 0/5 eligible for workflow-derived queries (no case has any documented multi-direction/candidate-comparison evidence); `case_005` excluded (deliberate negative sample). See `../QUERY_DERIVATION_FINDINGS.md` for the full reasoning.

This eligibility analysis predates, and is unrelated to, the Phase 6 `zcool_ce_001/` case above — it covers only the 5 `baseline_pilot` cases, none of which were promoted to a formal `cases/` record (all case-derived query work for them lives in `../outputs/creative_explore_agent_route_queries.jsonl` instead). `SCALE_UP_SCRAPING` is `CONTINUE_TARGETED_ONLY` as of Phase 4 (see top-level `README.md`).
