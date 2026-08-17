# Schema Mapping: zcool creative exploration data → queries.jsonl

This document defines how (if at all) zcool creative-exploration workflow data may relate to the AUTHORITATIVE query schema at `super-inbox/curify-studio@origin/main:dev/jayw/design-agent-v0/eval/queries.jsonl` (see `QUERY_SCHEMA_PROFILE.md` for the full profile). It is a mapping *analysis*, not a set of edits — no query has been written or modified as part of this document.

## 1. Two shapes exist; do not conflate them

The file holds two independent record shapes selected by `layer`:

- `routing_benchmark` (100 records, `TIQ-xxx`) — routing/coverage benchmark queries with template-matching metadata (`theme`, `tool_intent`, `specificity`, `coverage`, `candidate_templates`, `source_refs`, `expected_route_intents`).
- `agent_route` (18 records, `AR-xxx`) — short, high-level "which agent route should handle this query" examples (`expected_route`, `note`).

Any zcool-inspired query work must pick **one** of these two shapes and conform to it exactly. There is no third shape and no shared superset schema to extend.

## 2. Creative-exploration routing queries belong in `agent_route`, using the existing `creative_explore` value

`expected_route` already has a `creative_explore` enum value (see profile: `image_edit_variants`, `design_vote`, `virtual_tryon`, `factory_export`, `creative_explore`, `ask` — 3 examples each). A query whose purpose is "help me explore creative/brand directions" is a routing decision that belongs in the `agent_route` layer under `expected_route: "creative_explore"`, **not** a new field and **not** the `routing_benchmark` layer (which is about template-coverage benchmarking, a different concern).

## 3. No new query schema fields

Neither layer's field set may be extended. Specifically:
- No `derived_from_case_id`, `zcool_case_ref`, `workflow_stage`, or similar field may be added to any `queries.jsonl` record, in either layer.
- If a future query's wording is inspired by a specific zcool case (e.g. case_001's "冯老二散养牛"), that lineage is **not** recorded in `queries.jsonl` itself — see §4.

## 4. Case-level detail (case_id, source_url, evidence_id) goes in provenance files, never in queries.jsonl

The `pilot_cases.jsonl` structure (case → step → asset, with `evidence_text`, `confidence`, `order_confidence`, `copyright_or_reuse_notes`, etc.) has no counterpart field in either `routing_benchmark` or `agent_route`. This is expected — `queries.jsonl` is a flat benchmark-query list, not a workflow-provenance store. Any traceability between a future query and the zcool case that inspired it must live in `provenance/query_to_case_mapping.jsonl` (this task directory), keyed by `query_id` and `case_id`, and must never be written into the authoritative `queries.jsonl` file.

## 5. `source_refs` is an abstract corpus-classification tag, not a per-case reference

Observed `source_refs` values already include a `ZCOOL_*` family: `ZCOOL_BRAND_UPGRADE`, `ZCOOL_ECOM_BRANDING`, `ZCOOL_PACKAGING`, `ZCOOL_NEW_CULTURAL`, `ZCOOL_MODERN_BRAND`, `ZCOOL_GLOBAL_BRAND`, `ZCOOL_COCREATE_ECOM`. Every one of these is a **dataset-level classification label** (roughly: "this query's inspiration corpus is zcool brand-upgrade style cases"), not a pointer to an individual case page or case_id. Concrete case_ids (`case_001`...) must **not** be placed in `source_refs` — doing so would silently change the field's granularity from "corpus classification" to "individual citation," which is a schema semantics change, not a data-entry choice.

## 6. Whether a new `ZCOOL_CREATIVE_EXPLORATION` tag should exist is undecided

If a future round of `agent_route`/`routing_benchmark` queries is specifically about creative-exploration workflows sourced from this pilot's cases, the natural extension — by analogy with the existing `ZCOOL_*` naming pattern — would be a new tag such as `ZCOOL_CREATIVE_EXPLORATION`. **This has not been added anywhere.** Whether it should be added, and to which record's `source_refs`, is a decision for the schema owner (Jay), because:
- it is unclear whether `source_refs` values are governed by an enum/allowlist elsewhere in `design-agent-v0` that this audit did not have visibility into;
- adding an unreviewed value to a benchmark eval file used downstream could silently break consumers that validate against a closed list.

This task's `outputs/` and `provenance/` files remain empty placeholders until that confirmation is obtained (see `outputs/creative_explore_agent_route_queries.jsonl`).

## 7. Summary table

| Old pilot concept | Where it can live |
|---|---|
| `case_id`, `source_url`, `source_title`, `source_author` | `provenance/query_to_case_mapping.jsonl` (new, this task) — never in `queries.jsonl` |
| `evidence_text`, `confidence`, `order_confidence`, `stage_type` | Stays in `baseline_pilot/structured_cases/` (migrated as-is), not mapped into query schema at all |
| Query wording (`query` field) | May be *inspired by* a case's `case_summary`/`brand_or_project_name`, written fresh, placed in `outputs/creative_explore_agent_route_queries.jsonl` using the existing `agent_route` shape — not yet done in this phase |
| Corpus classification | `source_refs`, using existing `ZCOOL_*` values only, unless/until schema owner approves a new tag |
| Routing decision | `expected_route: "creative_explore"` (already exists, `agent_route` layer) |
