# automated_relevance_integrity_report.md

Generated: 2026-07-16T07:29:40Z

## Row-count checks
- Query-level CSV rows: 328 (expected 328) -- PASS
- Query-level JSONL objects: 328 (expected 328)
- Result-level CSV rows: 1511
- Baseline Top Results source rows (for cross-reference): 1511
- Duplicate query_index found: 0

## Label distribution and sum check
- PASS: 93
- PARTIAL: 106
- FAIL: 129
- UNJUDGABLE: 0
- Sum: 328 (expected 328) -- PASS

## Score range / label-score contradiction checks
- Out-of-range scores: 0
- Label/score contradictions: 0

## Path existence checks
- Missing screenshot files (of 328 referenced): 0
- Missing raw record files (of 328 referenced): 0

## Mechanical rubric-consistency audit (scripts/07, all 328 queries)
- Queries audited: 328
- Rule violations found: 0

## Second-pass review coverage
- Tier1 deep-reverify queries reviewed: 54 (covers 100% of: all FAIL/PARTIAL/UNJUDGABLE, all LOW confidence, all semantic_drift MODERATE/SEVERE, all rewrite_observed+first-pass-PASS -- see checkpoints/second_pass_population.json)
- Tier3 deterministic random 10% audit of remaining untouched PASS queries: 10 of 55 eligible (18.2%, exceeds the 10% minimum)
- Tier2 (219 queries): mechanical rubric-consistency audit only (no fresh independent semantic re-judgment); see MODEL_AND_METHOD.md and review/adjudication_report.md for the disclosed scope of this tier.

## Overall verdict
- **ALL CHECKS PASS**
