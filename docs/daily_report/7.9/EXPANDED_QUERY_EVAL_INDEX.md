# Expanded Query Eval Index — 2026-07-07

## Overview

This index links the newly expanded query eval set back to the original 58-query baseline. It records how the baseline was expanded into a broader candidate pool, how a first-round gold set was curated from that pool, and how that gold set was executed against Curify search. Use this file as the single pointer into `docs/daily_report/7.7/` for anyone picking up the eval work.

The expanded candidate pool contains **1,118 query candidates** in total. This number refers to the full candidate pool generated during expansion — it is **not** the number of queries that have been executed. Only the 68 queries in the first-round curated gold eval set have been executed against Curify search so far.

Head terms in `05_simple_head_term_seed_bank_2026-07-07.csv` (328 entries) are counted as query candidates here, consistent with the original 58-query baseline, which itself includes short/head-term queries such as "bicycle" and "wine."

## File Index

| File | Role | Row / query count | Include in final eval index? | Notes |
|---|---|---|---|---|
| `01_original_58_query_scene_classification_2026-07-07.csv` | Original baseline | 58 | Yes | The original 58-query baseline with scene classification. Reference point for everything downstream. |
| `02_expanded_from_58_query_candidates_2026-07-07.csv` | Expanded candidate pool | 188 | No (candidate pool) | Query candidates derived directly from the original 58 queries via competitor/autocomplete signals. |
| `03_net_new_scenario_seed_queries_2026-07-07.csv` | Expanded candidate pool | 98 | No (candidate pool) | Net-new scenario seed queries covering gaps the original 58 did not address (e.g. brand identity). |
| `04_high_signal_niche_query_candidates_500_2026-07-07.csv` | Expanded candidate pool | 504 | No (candidate pool) | High-signal niche / pressure-test query candidates; carries its own `keep_or_review` filter column. |
| `05_simple_head_term_seed_bank_2026-07-07.csv` | Expanded candidate pool | 328 | No (candidate pool) | Simple head-term query candidates (bilingual zh/en), consistent with head-term style queries already present in the original 58. |
| `gold_query_test_set_2026-07-07.csv` | First-round curated gold eval set | 68 | Yes | High-priority queries selected from the expanded candidate pool for the first Curify search pressure test. |
| `curify_search_auto_collect_2026-07-07.csv` | First Curify search execution result | 68 | Yes | Execution results for the 68 gold queries: visible result count, top-10 result metadata, screenshot paths, auto flags, `needs_human_review`, and manual review columns (currently empty). |

## Eval Pipeline

```
Original 58 baseline
        │
        ▼
1,118 expanded query candidates
  (188 + 98 + 504 + 328)
        │
        ▼
68 curated gold queries
        │
        ▼
Curify search execution results
```

## How to Use This Eval Set

- Use the original 58 (`01_original_58_query_scene_classification_2026-07-07.csv`) as the baseline reference.
- Use the 1,118 query candidates (files 02–05) as the broader pressure-test pool for future rounds.
- Use the 68 gold queries (`gold_query_test_set_2026-07-07.csv`) for immediate manual relevance review — these are already executed.
- Use `curify_search_auto_collect_2026-07-07.csv` as the first execution result to review and grade.
- Use the remaining candidates (everything not in the 68 gold queries) for future broader pressure tests and for taxonomy/ontology expansion work.

## Known Limitations

- Only the 68 gold queries have been executed so far — the full 1,118 candidate pool has not all been executed yet.
- Manual relevance columns in `curify_search_auto_collect_2026-07-07.csv` (`manual_relevant_count`, `manual_irrelevant_count`, `manual_recall_status`, `manual_filtering_status`, `manual_content_gap`, `manual_issue_type`, `manual_notes`) are still empty.
- Gallery image recall needs separate analysis and is not covered by this index.
- Safety filtering is required before any auto-generation workflow is applied to the remaining candidate pool.

## Next Steps

- Manually review the 68 collected Curify results.
- Fill in relevance labels and issue types for each of the 68 executed queries.
- Identify and tag: zero-result cases, low-result cases, bad relevance, missing content type, available-but-not-retrieved, competitor gap, and gallery image under-recall cases.
- Prepare PR candidates for: NER generalization, Chinese segmentation, alias expansion, semantic synonym replacement, multi-path retrieval, and gallery image recall.
- Extract taxonomy / 3-tier ontology candidates from the expanded query pool (files 02–05).
