# rewrite_relevance_summary.md

Generated: 2026-07-16T07:23:55Z

## Scope

138 of 328 queries had `rewrite_observed=True` (production's own broaden/rewrite mechanism fired).
Per RUN_MANIFEST/INPUT_AUDIT this was recorded as 138 in the baseline collection; the automated-relevance
pass finds 138 rows still flagged `rewrite_observed=True` in the final adjudicated dataset
(no discrepancy expected -- rewrite_observed is a collection-time production-behavior flag untouched by
relevance judging, so this equals the original collection's count unless noted otherwise below).

## 1-4. Label distribution among rewrite queries

- PASS: 34 (24.64%)
- PARTIAL: 42 (30.43%)
- FAIL: 62 (44.93%)
- UNJUDGABLE: 0 (0.0%)

## 5. Semantic drift among rewrite queries

{"MINOR": 25, "MODERATE": 25, "SEVERE": 68, "NONE": 20}
MODERATE+SEVERE: 93 of 138 (67.39%)

## 6. Intent preservation

original_intent_preserved=YES: 36 of 138 (26.09%)

## 7. Rewrite queries introducing clear off-topic drift

See `automated_relevance_semantic_drift_cases.csv` intersected with rewrite_observed=True, and the FAIL-label
rewrite rows in this file. Representative confirmed-drift cases from this run's second-pass review: E017 地球仪
(desk-globe -> generic country maps), E019 镜子 (mirror -> unrelated heritage/solar-term posters, SEVERE drift,
confirmed via screenshot during calibration), E245 宝妈 (mom-life -> noise-template + unrelated gardening/park
content, MODERATE drift, label flipped PASS->PARTIAL on adjudication), E269 冬至 (winter solstice -> a different
holiday (Christmas) and a wrong-season solar term, MODERATE drift, label flipped PASS->PARTIAL).

## 8. Most common failure modes in rewrite queries

{"PARTIAL_INTENT_ONLY": 102, "MOST_RESULTS_IRRELEVANT": 104, "ZERO_RESULT": 12, "REWRITE_SEMANTIC_DRIFT": 15, "CORE_INTENT_LOST": 1, "WRONG_ENTITY": 1}
(counted across FAIL+PARTIAL queries corpus-wide; see automated_relevance_fail_queries.csv /
automated_relevance_partial_queries.csv filtered to rewrite_observed=True for the rewrite-only subset)

## 9. Queries best illustrating the case for a Rewrite Guard

E019 镜子 (SEVERE drift, 0 relevant results despite a mirror-specific rewrite), E245 宝妈 and E269 冬至
(MODERATE drift pulling in off-topic noise-template/wrong-holiday content that downgraded an
otherwise-workable query from PASS to PARTIAL), and the recurring 'dual-character-comparison-infographic'
noise-template pattern documented in CALIBRATION_REPORT.md finding #5, which surfaces via the
*non-rewrite* retrieval path across multiple unrelated object queries (cat/dog/book) as well as inside
rewritten queries like E245 -- indicating the noise is a retrieval-ranking issue, not purely a rewrite
issue, and a Rewrite Guard alone would not fully fix it.

## 10. Cases where rewrite improved results

Several object queries with literal near-zero direct catalog matches were meaningfully rescued by broadening,
e.g. E020 花瓶 (vase; rewrite surfaced a directly on-topic 'Ming vase' result, low_result=True but final PASS),
E297 香薰机 (diffuser; rewrite matched the exact product template, PASS), E304 婴儿用品 (baby products; rewrite
matched an exact-title template, PASS) -- all originally low_result queries where the broadened terms produced
a small but genuinely relevant result set rather than expanding into noise. This is disclosed evidence-based,
not an assumption that rewrite is uniformly helpful or harmful: mean relevance_score for rewrite queries is
29.3 vs 38.3 for
non-rewrite queries in this run -- rewrite queries score somewhat lower on average, consistent with rewrite
generally firing on harder/sparser queries to begin with (selection effect), not proof that rewriting itself
causes harm on a per-query basis.
