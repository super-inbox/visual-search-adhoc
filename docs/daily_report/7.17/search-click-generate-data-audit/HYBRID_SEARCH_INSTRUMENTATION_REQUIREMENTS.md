# Minimum Instrumentation Required Before a Hybrid Search A/B Test

Repository: `curify-studio` @ `7b3fa5b40b03da3056536257ead2200dab031247`. No Hybrid Search / external-provider search code exists in this repository today — all fields below are prospective and evaluated against the current schema baseline (`user_interactions`, `project`).

## Search event

| Field | Current status | Why needed | Event where emitted (proposed) | Priority | Effect if missing |
|---|---|---|---|---|---|
| search_id | MISSING | Sole reliable join key across the whole funnel | search event | P0 | No experiment can attribute downstream clicks/generations to a specific search variant with confidence |
| session_id | PRESENT (on user_interactions only) | Anonymous-user grouping | search event | P0 (extend to generation record too) | Anonymous funnel breaks at generation step |
| query | PRESENT (as content_id) | Core dimension for query-level analysis | search event | P0 | N/A - already present |
| normalized_query | MISSING as column (ad hoc at read time only) | Stable grouping across encoding variants | search event | P1 | Query-level rollups fragment |
| language | MISSING | Segment by locale for hybrid rollout | search event | P1 | Cannot evaluate hybrid effect per-locale |
| search_mode | MISSING | Distinguish internal-only vs. hybrid-variant search | search event | P0 | Cannot run or measure an A/B test at all |
| initial_internal_result_count | MISSING (only string-encoded for low-result case) | Baseline to detect internal-result cannibalization | search event | P0 | Cannot measure "internal-result preservation rate" |
| rewrite_triggered | MISSING as column (string-encoded per secondary evidence) | Understand which searches are query-rewritten before hitting hybrid providers | search event | P1 | Confounds hybrid-effect analysis with rewrite effects |
| rewritten_query | MISSING | Same as above, needed for query-level debugging | search event | P1 | Same as above |
| external_triggered | MISSING | Know whether external provider was actually called for this search | search event | P0 | Cannot separate "hybrid enabled" from "hybrid actually returned external results" |
| external_provider | MISSING | Attribute effects to a specific provider if multiple are tested | search event | P1 | Cannot compare providers |
| total_latency_ms | MISSING | Guardrail metric - hybrid search must not regress latency | search event | P0 | Latency regressions go undetected |
| error_type | MISSING | Guardrail metric - external API failures | search event | P0 | Provider outages/errors invisible to reporting |

## Result impression

| Field | Current status | Why needed | Priority | Effect if missing |
|---|---|---|---|---|
| search_id | MISSING (event doesn't exist) | Join impressions to the originating search | P0 | No true CTR denominator |
| result_id | MISSING | Identify which specific result was shown | P0 | Cannot compute per-result metrics |
| result_source | MISSING | internal vs. external tagging | P0 | Cannot separate internal/external CTR |
| provider | MISSING | Which external provider served this result | P1 | Cannot compare providers at result grain |
| result_rank | MISSING | Position-based analysis | P0 | No rank CTR, no ranking-quality evaluation |
| destination_type | MISSING | e.g. template/gallery/external-page | P1 | Cannot distinguish generate-capable vs. dead-end results |
| visible_on_first_screen | MISSING | Above/below-fold analysis | P2 | Minor - nice-to-have for UX tuning |

*(No impression event of any kind currently exists — this entire entity is net-new.)*

## Result click

| Field | Current status | Why needed | Priority | Effect if missing |
|---|---|---|---|---|
| search_id | MISSING | Join click to originating search | P0 | Falls back to the lossy 5-min heuristic already documented as broken by redirects/multi-search sessions |
| result_id | PARTIAL (generic content_id present, not scoped to a specific impression) | Identify which item was clicked | P0 | Cannot join click back to a specific impression |
| result_source | MISSING | internal vs. external | P0 | Cannot compute the internal/external CTR split central to the manager's Q22 risk scenario |
| provider | MISSING | Provider-level comparison | P1 | Cannot compare providers |
| result_rank | MISSING | Position-based CTR | P0 | No rank CTR |
| internal_click | MISSING (derivable once result_source exists) | Guardrail: is internal engagement being cannibalized | P0 | Cannot detect internal-content cannibalization risk |
| external_click | MISSING (derivable once result_source exists) | Guardrail: external exit rate | P0 | Cannot measure external exit rate |
| destination_domain | MISSING | Guardrail: which external destinations are drawing users away | P1 | Cannot diagnose specific problem domains |

## Generation

| Field | Current status | Why needed | Priority | Effect if missing |
|---|---|---|---|---|
| search_id | MISSING | The single most important missing field - ties generation back to the search that started the journey | P0 | Cannot compute Search-to-Generate Rate at all, for any experiment |
| source_result_id | MISSING (only source_prompt_id for unrelated gallery-remix flow) | Ties generation to the specific clicked result | P0 | Cannot compute Click-to-Generate Rate |
| result_source | MISSING | Was this generation seeded from an internal or external result | P0 | Cannot test the core hypothesis that external results reduce generation |
| generate_click | PRESENT (as action_type='GENERATE' click-log event, but disconnected from below) | Intent signal | P0 (needs to be linked, not just logged) | Currently cannot be reconciled with actual Project rows |
| generation_started | PRESENT (Project.status transitions) | Funnel stage | P0 (needs search_id added) | Present in isolation, unusable for the funnel without search_id |
| generation_success | PRESENT (Project.status='COMPLETED') | The single most important outcome metric per the manager's business framing | P0 (needs search_id added) | Present in isolation, unusable for the funnel without search_id |
| generation_failure | PRESENT (Project.status='FAILED', partial structured detail in nano-freeform pipeline only) | Guardrail/error-rate | P1 | Partial coverage today (video-dubbing pipeline has less structured failure detail than nano-freeform) |
| generation_id | PRESENT (as project_id, doubles as generation record) | Primary key for joins | P0 | Already usable as-is once search_id exists on Project |

---

## Minimum P0 fields before online A/B testing

Per the manager brief's own framing, confirmed correct against the evidence gathered:

- **search_id**
- **search_mode**
- **result_source**
- **result_rank**
- **result_click** (linked via search_id, not a time-window guess)
- **generate_click** (linked via search_id)
- **generation_success** (linked via search_id, sourced from `Project.status`)

## Why `search_id` is especially important

Every other P0 field in this list is meaningless for experimentation without it. The audit found that **the current system's only cross-event join mechanism is `COALESCE(user_id, session_id)` plus a bounded time window**, and that mechanism is already demonstrably lossy even for the one link it's used for today (Search→Click — see `SEARCH_ATTRIBUTION_FEASIBILITY.md`: multiple searches per session, server-redirect gaps, and undercounted search-event volume all break it). Extending that same fragile heuristic to a three-hop chain (Search→Click→Generate) for an A/B test would compound each of those error sources, and — critically — an A/B test needs to attribute outcomes to *the specific search variant a user was assigned to*, not just "a search happened sometime near this click." A persisted `search_id`, generated once per search and threaded through impression, click, and generation events, is the only way to:
1. Guarantee correct attribution even when a user issues multiple searches in quick succession (a near-certainty at any real traffic volume).
2. Directly join to `search_mode` to know which experiment arm produced the outcome.
3. Eliminate the systematic bias windows introduce (a slow-deciding user's legitimate 6-minute-later click is currently invisible; a `search_id` has no such time limit).
4. Close the current, confirmed gap where anonymous generations cannot be linked to anything upstream at all (once `search_id` — not just `session_id` — is added to the `Project`/generation record, anonymous coverage is restored without needing session persistence to survive across page loads).

Without `search_id`, any Hybrid Search A/B test result is at serious risk of exactly the false-signal scenario described in the manager's Q22: CTR could appear to rise (more attention-grabbing external cards get clicked) while the true Search-to-Generate rate falls, and the current instrumentation would not be able to prove or disprove that connection at all — only observe the two trends moving independently, with no way to link them causally to the experiment.
