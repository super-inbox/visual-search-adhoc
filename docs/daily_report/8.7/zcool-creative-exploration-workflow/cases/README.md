# cases/

## CASE_QUERY_ELIGIBILITY.csv (new, Phase 3)

Query-derivation eligibility analysis of the 5 cases already migrated into `../baseline_pilot/structured_cases/raw_cases/` (`case_001`..`case_005`). Judged strictly from existing structured-case evidence (`workflow_extraction.json`, `source_metadata.json`, `REVIEW.md`, `asset_manifest.csv`, plus the cross-case `pilot_cases.jsonl`, `case_quality_review.csv`, and `PILOT_FINDINGS.md`) — `raw_text.md` was never read, per task instruction. Result: 4/5 cases (`case_001`–`case_004`) eligible for brief-derived queries; 0/5 eligible for workflow-derived queries (no case has any documented multi-direction/candidate-comparison evidence); `case_005` excluded (deliberate negative sample). See `../QUERY_DERIVATION_FINDINGS.md` for the full reasoning.

This directory remains otherwise empty — no *new* zcool cases have been scraped or extracted this phase (or any prior phase). `SCALE_UP_SCRAPING` remains `PAUSED` (see top-level `README.md`).
