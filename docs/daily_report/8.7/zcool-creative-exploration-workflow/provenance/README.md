# provenance/

## query_to_case_mapping.jsonl (populated, Phase 3)

**6 rows**, one per query in `../outputs/creative_explore_agent_route_queries.jsonl` (`AR-ZCE-001`..`AR-ZCE-006`). Actual schema per record:

```json
{"query_id": "...", "case_id": "...", "source_url": "...", "derivation_type": "brief_derived", "derived_from_fields": ["..."], "supporting_step_ids": ["..."], "supporting_evidence_ids": [], "unsupported_workflow_elements": ["..."], "confidence": "...", "limitations": "..."}
```

All 6 records have `derivation_type: "brief_derived"` — none are `workflow_derived`, because no case in `baseline_pilot/structured_cases/` has any step with a non-empty `candidate_outputs` list (i.e. no documented multi-direction exploration or candidate comparison exists anywhere in this dataset). `supporting_evidence_ids` is `[]` on every record: no case has any usable visual evidence (every image asset in every case resolves to an unresolved zcool placeholder), so no asset ID is cited as supporting evidence. `supporting_step_ids` references only real `step_id`s from `baseline_pilot/structured_cases/pilot_cases.jsonl` — verified in `../VALIDATION_REPORT.md`.

This is where case_id / source_url / evidence-level detail lives — see `../query_schema/SCHEMA_MAPPING.md` §4. This file must never be merged into or confused with the authoritative `queries.jsonl` (`super-inbox/curify-studio@origin/main:dev/jayw/design-agent-v0/eval/queries.jsonl`); it is a local traceability record only.
