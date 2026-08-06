# outputs/

## creative_explore_agent_route_queries.jsonl (populated, Phase 3)

**6 local candidate records**, IDs `AR-ZCE-001`..`AR-ZCE-006`. Each is a valid `agent_route`-layer record with exactly the 7 authoritative fields (`id`, `query`, `language`, `has_reference`, `expected_route`, `note`, `layer`) — no extra fields. `expected_route` is `creative_explore` on every record — see `../query_schema/SCHEMA_MAPPING.md` §2. `has_reference` is `false` on every record (no real reference image exists for any source case).

`AR-ZCE-xxx` is a **provisional, adhoc-repo-local ID prefix**, deliberately distinct from the authoritative file's `AR-xxx` sequence (currently `AR-001`..`AR-018`). It is not a reservation of, or a proposal for, any specific official ID — merging any of these candidates upstream would require the schema owner to review content and assign real IDs. See `../CREATIVE_EXPLORATION_FINDINGS.md` and `../QUERY_DERIVATION_FINDINGS.md` for how each query was derived, and `../provenance/query_to_case_mapping.jsonl` for full per-query traceability back to the source case.

## creative_exploration_workflows.jsonl (still empty, 0 lines)

Intended shape when populated: workflow-provenance records in the `baseline_pilot`/`design_workflow_schema_v0.1.json` structure (case → step → asset), for any *newly* processed creative-exploration cases. This file is entirely separate from `queries.jsonl`'s schema — see `SCHEMA_MAPPING.md` §4 — and is never merged into the authoritative query file. Not populated this phase because no new case-extraction work was performed — this phase only re-derived queries from the already-migrated `baseline_pilot` cases.
