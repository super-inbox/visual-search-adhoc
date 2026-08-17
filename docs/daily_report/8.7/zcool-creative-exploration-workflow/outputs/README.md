# outputs/

## creative_explore_agent_route_queries.jsonl (populated, Phase 3)

**6 local candidate records**, IDs `AR-ZCE-001`..`AR-ZCE-006`. Each is a valid `agent_route`-layer record with exactly the 7 authoritative fields (`id`, `query`, `language`, `has_reference`, `expected_route`, `note`, `layer`) — no extra fields. `expected_route` is `creative_explore` on every record — see `../query_schema/SCHEMA_MAPPING.md` §2. `has_reference` is `false` on every record (no real reference image exists for any source case).

`AR-ZCE-xxx` is a **provisional, adhoc-repo-local ID prefix**, deliberately distinct from the authoritative file's `AR-xxx` sequence (currently `AR-001`..`AR-018`). It is not a reservation of, or a proposal for, any specific official ID — merging any of these candidates upstream would require the schema owner to review content and assign real IDs. See `../CREATIVE_EXPLORATION_FINDINGS.md` and `../QUERY_DERIVATION_FINDINGS.md` for how each query was derived, and `../provenance/query_to_case_mapping.jsonl` for full per-query traceability back to the source case.

## creative_exploration_workflows.jsonl (populated, Phase 6 — 1 line)

**1 case record**, `zcool_ce_001` (source: `ZCE-CAND-001`, the sole Phase 5 `SELECT`). Structure follows `baseline_pilot/schema/design_workflow_schema_v0.1.json` exactly (`case` / `steps[]` / `missing_stages[]` / `assets[]`), same shape as `baseline_pilot/structured_cases/pilot_cases.jsonl`. 9 steps (`ZCE-WF-001`..`ZCE-WF-009`), 1 shared full-page-screenshot asset (individual evidence sections are logged in `../cases/zcool_ce_001/evidence_manifest.csv`, not split into separate `asset_id`s, since only one screenshot file exists), 26 `missing_stages`.

Two documented, non-silent deviations from the baseline schema constants (`case.language="zh-CN"` instead of `"zh"`, `case.source_platform="ZCOOL"` instead of `"zcool"`) and one enum-mapping decision (`keyword_extraction` stage mapped to `creative_direction`, the closest existing `stage_type` value) — see `../cases/zcool_ce_001/QUALITY_REVIEW.md` "Schema compatibility notes" for the full list, which this file's own `case.schema_note` field also points back to.

`usable_for_workflow_training=true` — a first in this task's case lineage (every `baseline_pilot` case is `false`) because this is the only case with real sketch-exploration *and* side-by-side final-comparison visual evidence. This must **not** be read as also supporting selection-decision training: `selected_output`/`selection_reason` are `null` on every step, since no page evidence states why any sketch or final version was chosen. See `../cases/zcool_ce_001/FORMAL_WORKFLOW_CLEANING_FINDINGS.md` for the full Phase 6 writeup.

This file is entirely separate from `queries.jsonl`'s schema — see `SCHEMA_MAPPING.md` §4 — and is never merged into the authoritative query file. No `creative_explore` query was generated from this case this phase (see open items in `../PROGRESS_STATUS.md`).
