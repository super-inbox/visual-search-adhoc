# Query Derivation Findings

Scope: derive a small batch of local `creative_explore` `agent_route` candidate queries from the 5 already-migrated 8.5 zcool pilot cases (`baseline_pilot/structured_cases/`), with strict query→case provenance. No new zcool pages were fetched. Full eligibility reasoning is in `cases/CASE_QUERY_ELIGIBILITY.csv`; full per-query traceability is in `provenance/query_to_case_mapping.jsonl`.

## 1. How many of the 5 old pilot cases support a brief-derived query?

**4 of 5** (`case_001`, `case_002`, `case_003`, `case_004`). All four have at least one reliable, explicit `business_context`/`project_brief` step or a populated `stage_goal`, which satisfies the brief-derived bar (reliable background, design goal, or deliverables — see `CASE_QUERY_ELIGIBILITY.csv` decision column).

`case_005` is excluded. It is the pilot's deliberately-selected negative sample: `workflow_completeness=showcase_only`, 0 extracted steps, no project background, no single named brand, and `missing_stages` lists all 25 schema stage types as absent. Deriving a query from it would require fabricating a brief the source does not contain, which the task instructions explicitly prohibit.

## 2. How many genuinely support a workflow-derived query?

**0 of 5.** `candidate_outputs` is an empty list on **every single step across all 5 cases** — this is confirmed both by the raw JSONL and independently by the migrated `baseline_pilot/reviews/PILOT_FINDINGS.md` §2, which already flagged "包含多个候选方案的案例——本 Pilot 同样未遇到" (cases with multiple documented candidate options — this pilot did not encounter any) as a known blind spot of the 8.5 sample. No case shows a documented moodboard, sketch set, direction comparison, or refinement pass. Per task rule 3, the existence of a finished, published design must not be read backward as evidence that a multi-direction exploration process happened — so all 6 generated queries are `brief_derived`, never `workflow_derived`.

Three individual steps (`case_001_step_04`, `case_001_step_08`, `case_002_step_03`) do have a populated `selection_reason` field. These were treated carefully: each documents *why a single, already-decided outcome makes sense* (e.g. "keeping the old name is less alienating to existing customers"), not a comparison among multiple named/sketched candidates that were weighed against each other. They are recorded in `provenance/query_to_case_mapping.jsonl` with that caveat rather than being used to justify `workflow_derived` status.

## 3. Most common available information across the 5 cases

- Case-level metadata (title, author, URL, industry, `case_summary`) — 5/5, stable and unambiguous (confirmed by `PILOT_FINDINGS.md` §1).
- An explicit, high-confidence `business_context` or `project_brief` step — 4/5 (`case_001`–`case_004`).
- At least one populated `stage_goal` (an explicit design objective) — 3/5 (`case_001`, `case_002`; `case_003` and `case_004` have none).
- Deliverable *categories* named, even without process narrative (e.g. "服务范围：标志/VIS识别/产品包装") — 4/5, but for `case_003`/`case_004` this is a service-line listing, not evidence of a design process (`quality_flags: service_category_label_only_no_process_narrative`).

## 4. Most common missing information across the 5 cases

- Multiple documented candidate directions (`candidate_outputs` populated) — 0/5.
- Explicit candidate comparison or a selection rationale that references more than one option — 0/5.
- `audience_definition` (an explicitly named target audience) — 1/5 (`case_003` only).
- Any usable visual evidence — 0/5. All image assets across all 5 cases resolve to the same zcool placeholder URL; `evidence_type=visual_explicit` was never used anywhere in the source pilot.
- Sketches, moodboards, or a refinement/iteration record — 0/5.
- A reliable, non-inferred logo design process — 0/5 (`case_004`'s only logo-related evidence is `evidence_type=inferred`, sourced from a team-credit line, and its own `review_notes` say it must not be treated as process evidence).

## 5. Why a brief-derived query is not the same as real creative-exploration workflow evidence

A brief-derived query only proves that *a plausible starting brief* (background, goal, or deliverable list) can be phrased as a natural user request. It says nothing about whether the *response* to that query — multiple directions, a comparison, a chosen direction with a stated reason — is something the source case actually demonstrated. All 6 queries below are brief-derived: they establish that a `creative_explore` routing decision is a reasonable *entry point* for this kind of request, but none of them carry forward, or are validated against, an actual multi-direction exploration process, because no such process is documented in any of the 5 source cases. Treating a brief-derived query as equivalent to workflow evidence would silently launder the pilot's known blind spot (no multi-candidate cases) into an implied claim that such data exists.

## 6. What the 6 generated queries can test

- Whether an `agent_route` classifier correctly routes an open-ended, multi-direction creative brief (naming, color, positioning, packaging-structure, visual-concept, brand-identity) to `creative_explore` rather than to a single-output route (e.g. `image_edit_variants`, `factory_export`).
- Whether the routing behaves consistently across a range of brief specificity (from a fairly bounded packaging brief in `AR-ZCE-004` to the loosely-scoped identity brief in `AR-ZCE-006`), mirroring the "vague brief → offer directions" pattern already established by the authoritative file's existing `creative_explore` examples (`AR-013`–`AR-015`).
- Whether zh-CN natural-language briefs across several industries (food/beverage, packaging, confectionery, B2B campus branding) all resolve to the same expected route.

## 7. What the 6 generated queries cannot test

- Whether the downstream `creative_explore` response correctly reproduces a *real* multi-direction exploration, comparison, or selection process — no source case demonstrates this, so there is nothing to validate against.
- Any visual/reference-image-conditioned behavior — `has_reference` is `false` on all 6 by construction, since no real reference image exists for any of the 5 cases.
- Whether a generated response's final direction would match what the original zcool designer actually chose — deliberately out of scope; the queries never encode the case's final selected visual answer.
- Coverage of `logo_sketch`/`logo_exploration`/`logo_refinement`/`moodboard`-specific creative-exploration phrasing — none of the 5 cases contain usable evidence for these stage types.

## 8. What the next round of new zcool case screening should prioritize

Per `PILOT_FINDINGS.md` §2 and confirmed by this derivation pass, future candidate screening should specifically look for cases that show:

1. **Multiple distinct creative directions** — cases where `candidate_outputs`-equivalent content (2+ named/described options) is actually present in the source text or images.
2. **Candidate comparison** — explicit "we considered A and B" language, not just a stated final choice.
3. **Selection rationale tied to a comparison** — a `selection_reason` that references what was *not* chosen, not just why the chosen option works.
4. **Sketches or moodboards** — any process-stage visual content, which requires solving the image-access blocker first (`IMAGE_ACCESS_VALIDATION: CONTINUE`, unchanged from the 8.5 pilot).
5. **Direction refinement** — an iteration/revision record (`revision_instruction` populated), which is empty in all 5 current cases.
6. **Reliable visual evidence** — at minimum, real image bytes for logo/color/packaging stages, since `evidence_type=visual_explicit` has never been used in this dataset lineage.

Until the image-access blocker is resolved, any future case pool is likely to keep reproducing this round's core limitation: strong case-level and brief-level metadata, near-total absence of documented multi-direction exploration.
