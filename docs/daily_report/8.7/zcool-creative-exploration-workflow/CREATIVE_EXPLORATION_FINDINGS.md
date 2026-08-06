# Creative Exploration Findings — Phase 3 (Local Candidate Query Generation)

This document summarizes what this phase established about turning the 8.5 pilot's structured zcool cases into `creative_explore` routing queries. For the detailed per-case reasoning and per-query provenance, see `cases/CASE_QUERY_ELIGIBILITY.csv`, `provenance/query_to_case_mapping.jsonl`, and `QUERY_DERIVATION_FINDINGS.md` (all new this phase).

## What this phase did

1. Re-confirmed the authoritative `agent_route` schema directly from `super-inbox/curify-studio@origin/main:dev/jayw/design-agent-v0/eval/queries.jsonl` via `git show` (read-only, no checkout, no branch switch). Result: unchanged since Phase 2 — 118 lines, SHA-256 `5384474f8334f352f6ce157331b7d96c68721179f5da2049fcdc8c8e0ffe2e3d`. The `agent_route` layer's field set is exactly `{id, query, language, has_reference, expected_route, note, layer}` — 7 fields, confirmed by direct inspection of all 18 `agent_route` records, not assumed from the task prompt (the prompt's guess omitted `language`, which is in fact present on every record).
2. Evaluated all 5 migrated `baseline_pilot/structured_cases/raw_cases/*` cases for query-derivation eligibility, writing `cases/CASE_QUERY_ELIGIBILITY.csv`. Result: 4/5 eligible for brief-derived queries (`case_001`–`case_004`), 0/5 eligible for workflow-derived queries, `case_005` excluded entirely (deliberate negative sample).
3. Generated **6** local candidate `agent_route` records in `outputs/creative_explore_agent_route_queries.jsonl`, IDs `AR-ZCE-001`..`AR-ZCE-006`. All have `expected_route: "creative_explore"`, `layer: "agent_route"`, `has_reference: false`, and exactly the 7 authoritative fields — no extra fields (no `source_refs`, `case_id`, `source_url`, `theme`, `tool_intent`, `candidate_templates`, etc.).
4. Wrote full query→case provenance for all 6 queries in `provenance/query_to_case_mapping.jsonl`, keyed by `query_id`/`case_id`, referencing only real `step_id`s that exist in `baseline_pilot/structured_cases/pilot_cases.jsonl`. `supporting_evidence_ids` is `[]` on every record — no case in this dataset has any usable visual evidence (asset-level `usable_for_analysis: false` on every asset row, across all 5 cases), so citing an asset ID as "supporting evidence" would misrepresent an unresolved placeholder image as evidence.
5. Wrote `QUERY_DERIVATION_FINDINGS.md` with the full 8-point analysis (eligibility counts, common available/missing information, why brief-derived ≠ workflow evidence, what the new queries can/cannot test, and next-round screening priorities).

## Key finding carried forward from the 8.5 pilot, now independently reconfirmed

`candidate_outputs` is empty on every step in every one of the 5 cases — there is still no case in this lineage with a documented multi-direction exploration, candidate comparison, or refinement pass. This was already flagged as a blind spot in `baseline_pilot/reviews/PILOT_FINDINGS.md` §2; this phase's fresh, field-by-field re-check of the same 5 cases confirms it holds with zero exceptions. Consequently, **all 6 generated queries are `brief_derived`, none are `workflow_derived`** — see `QUERY_DERIVATION_FINDINGS.md` §2 for the full reasoning and §5 for why this distinction matters.

## Schema-governance items, unchanged from Phase 2

- Whether a new `ZCOOL_CREATIVE_EXPLORATION` value may be added to `source_refs` is still undecided and still requires the schema owner (Jay) — see `query_schema/SCHEMA_MAPPING.md` §6. This phase's query generation does **not** depend on that decision: `agent_route` records have no `source_refs` field at all, so the local candidate queries in this phase carry no `source_refs` tag of any kind.
- Whether/how the `AR-ZCE-xxx` provisional candidate IDs generated this phase would ever be merged into the authoritative `queries.jsonl` (and under what ID allocation scheme) is still undecided and still requires the schema owner. **`AR-ZCE-xxx` are adhoc-repo-local provisional IDs, not curify-studio official numbering** — see `README.md` and `PROGRESS_STATUS.md`.

## Status carried forward, unchanged

```text
SCALE_UP_SCRAPING:        PAUSED     — unchanged; still blocked on zcool image access
IMAGE_ACCESS_VALIDATION:  CONTINUE   — unchanged; still the recommended next technical investigation, not started this phase
```

No new zcool pages were fetched, no images were downloaded, and the authoritative `curify-studio` `queries.jsonl` was not modified — verified in `VALIDATION_REPORT.md`.
