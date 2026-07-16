# Hybrid Search — Search → Click → Generate Instrumentation Design

Design only. No tracking code was modified. All "current" statements below are verified against `services/useTracking.ts` and its call sites; all "proposed" statements are net-new and explicitly marked.

## The central gap: no `search_id` exists anywhere

Full-repo grep for `search_id`/`searchId` across all `.ts`/`.tsx` returns **zero hits**. The current tracking system (`services/useTracking.ts`) has:
- `session_id` — one per browser tab/session (`sessionStorage`, `services/useTracking.ts:92-101`), persists across MULTIPLE searches in that session.
- `user_id` — from `localStorage.curifyUser` (`useTracking.ts:103-110`), optional.
- `content_id` — currently overloaded to carry the query text itself, plus ad-hoc suffixes (`|within=`, `|rw=1`, `|paths=N`) for search events (`SearchResultsClient.tsx:243-263`).

**There is no field that uniquely identifies one specific search request.** This means: if a user searches "cat," gets results, clicks one, and generates — there is today no direct database key joining the `search` event, the `click` event, and the `generate` event. The only possible join is a heuristic one: `(session_id, normalized query text, timestamp proximity)` — which breaks the moment a user searches the same query twice in one session (repeat searches, back-button, refinement), or when a click happens well after the search (long browse session).

**This is the single most important fix required before the manager's "did users click and generate" question can be answered with a real join, not an approximation.** It is also a prerequisite fix independent of Hybrid Search — it would improve attribution for the *already-shipped* LLM-rewrite feature and all internal search results today, not just future external results.

## Proposed event schema (net-new fields marked, existing fields marked)

### Search event
| Field | Status | Source |
|---|---|---|
| search_id | **NEW — critical** | Should be generated once per search request, server-side, at the top of `SearchPage` (page.tsx:237) and threaded through to the client via a serialized prop, so both server-side computation context and client-side click/generate events can carry it |
| session_id | Existing | `useTracking.ts:92-101` |
| user_id / anonymous_id | Existing (user_id only; no explicit anonymous_id, but session_id serves that role today) | `useTracking.ts:103-110` |
| query | Existing | passed via `content_id` today, would become its own field with `search_id` in place |
| normalized_query | **NEW** (trivial — `normalizeSearchQuery`/`normalizeForSearch` already compute this server-side, just not currently emitted as a tracked field) | `lib/query_normalize.ts:51`, `page.tsx:133` |
| language | Existing (`locale` is already known server-side, just not attached to the search event) | `page.tsx:244` |
| scenario/category | Not currently available as a structured field — would require either the intent-cluster taxonomy (`lib/intent_taxonomy.ts`) or a new lightweight classifier; **not assumed available**, mark UNKNOWN/optional | n/a |
| search_mode | **NEW** — A/B/C/D/E per Mode Matrix, or simply "internal"/"internal+rewrite"/"internal+rewrite+external" for production (not all 5 experimental modes need to exist as a runtime concept in prod, only the shipped ones) | n/a |
| initial_internal_result_count | **NEW** (the underlying number already exists as `initialThinCount`, just not emitted) | `page.tsx:611-613` |
| rewrite_triggered | Existing in spirit (`usedRewrites.length > 0` drives the `|rw=1` suffix today) — recommend promoting from a suffix to a real boolean field | `SearchResultsClient.tsx:243` |
| external_triggered | **NEW** — analogous new boolean for the external leg | n/a |
| latency_ms | **NEW** — not currently measured/emitted for search requests at all | n/a |
| error_type | **NEW** | n/a |

### Result impression event
| Field | Status |
|---|---|
| search_id | **NEW** |
| result_id | Existing concept (`InspRecord.id`/`template_id`), not currently tracked as an impression (only clicks and views via `useViewTracking`'s `IntersectionObserver`, `useTracking.ts:188-225`, are tracked — and that hook is not currently wired into the search-result grid components per the Explore-agent's UI inventory; UNKNOWN/likely-absent for search cards specifically, would need direct verification of `ExampleImagesGrid.tsx` usage of `useViewTracking`) |
| result_source | **NEW** — internal / external_google / external_other |
| rank | Not currently tracked for search results |
| destination_type | **NEW** |
| provider | **NEW** (external only) |

### Result click event
| Field | Status |
|---|---|
| search_id | **NEW** |
| result_id | Partially exists — `useClickTracking(contentId, contentType, viewMode)` fires today (`useTracking.ts:227-237`), but `contentId` is a free-text string (e.g. `search_generable_template:<template_id>`, `GenerableTemplatesSection.tsx:29-56`), not a structured `result_id` + `result_source` pair |
| result_source | **NEW** |
| rank | **NEW** — not currently attached to any click event |
| internal_click / external_click | **NEW** — would be derivable from `result_source` rather than a separate boolean, but the brief asks for it explicitly; recommend deriving at query time from `result_source` rather than storing redundantly |
| destination_url domain | **NEW** for external; N/A for internal (internal destinations are always Curify routes) |

### Generation event
| Field | Status |
|---|---|
| search_id | **NEW — this is the actual missing link.** `generate` action already fires (`ActionType` includes `"generate"`, `useTracking.ts:31`), at real call sites: `app/[locale]/_components/ReproduceWorkbench.tsx:233`, `ExampleGeneratePanel.tsx:86,108`, `ExampleRightColumn.tsx:137,323`, `UnifiedActionBar.tsx:125`. None of these currently receive or forward a `search_id`. |
| source_result_id | **NEW** — would need to be threaded from the search-result click, through the navigation to `/nano-template/[slug]#reproduce`, into the generate event. Today the navigation is a plain `<Link>` — carrying `search_id`/`source_result_id` would require either a query param on the destination URL or a client-side handoff (e.g., sessionStorage, matching the existing `WITHIN_INTENT_KEY` pattern already used for a different handoff in `SearchResultsClient.tsx:71`). |
| generate_click | Existing (`actionType: "generate"`) |
| generation_started / generation_success / generation_failure | Existing `actionType="generate"` fires once, at click time — it is NOT currently split into started/success/failure phases (confirmed: all four cited call sites fire a single `trackAction(tracking, "generate")` on click, not on completion). **This is a second, independent gap**: even without Hybrid Search, Curify cannot currently tell whether a "generate" click led to a *successful* generation, only that the button was clicked. Flagging this because the manager's business question ("do users click AND generate") implicitly assumes generation *success* is observable — today only the click is. |

## Minimum P0 fields required before ANY online experiment

Per the brief, the minimum viable set is:
```
search_id, search_mode, result_source, result_rank, result_click, generate_click, generation_success
```

Assessment against current state:
- `search_id` — **does not exist, must be built first.** This blocks everything else in the list from being joinable.
- `search_mode` — new field, cheap to add (a string constant known at request time).
- `result_source` — new field, cheap to add (known at merge time — internal vs external).
- `result_rank` — new field, not currently tracked for any result type, cheap to add at render/click time.
- `result_click` — exists as the `"click"` ActionType, needs `search_id`+`result_source`+`result_rank` attached to become useful for this analysis.
- `generate_click` — exists as the `"generate"` ActionType, needs `search_id` attached (the harder integration point, per above).
- `generation_success` — **does not exist at all** — today's "generate" event is click-time only, not outcome-time. Building this requires instrumenting the actual generation completion (success/failure) at whatever async job/API call performs the generation — not evaluated in this audit (out of scope: this audit covers search-side code, not the generation pipeline internals).

**Bottom line: 3 of 7 P0 fields require net-new work beyond "just add a field" — `search_id` (needs a request-scoped ID generated and threaded across a server→client→next-page-navigation boundary), the click→generate linkage (needs a handoff mechanism across a full page navigation), and `generation_success` (needs instrumenting the actual generation pipeline's completion, not just its trigger click).**

## How missing `search_id` weakens attribution (explicit explanation, as required)

Without `search_id`, any Search→Click→Generate analysis must fall back to joining on `(session_id, query text, coarse time window)`. This fails in at least four concrete, common scenarios:
1. **Repeat search** — user searches "cat" twice in one session (e.g., refines, goes back, re-searches). Two `search` events share the same `session_id` and `query` — a click/generate event in between cannot be unambiguously attributed to the first or second search.
2. **Long browse gap** — user searches, browses for 20+ minutes (reading other pages, coming back), then clicks/generates. A time-window join either misses this (window too short) or over-attributes unrelated activity (window too long) — there's no principled window size that's correct for all users.
3. **Multi-tab/session ambiguity** — `session_id` is `sessionStorage`-scoped (per-tab in most browsers); a user with two tabs open on different searches has two `session_id`s already, so this specific failure mode is actually already mitigated by the existing session model — but ONLY within a tab; the query-text collision (case 1) still applies within that single tab/session.
4. **Hybrid-specific**: when both an internal AND an external result are shown for the same query, and the user clicks one of them, a text/time-based join cannot distinguish "clicked the internal result" from "clicked the external result" after the fact if both events only record the query text — `result_source`+`search_id` on the click event is the only reliable way to know which.

## Frontend files/components where events could be added later (no code changed in this audit)

| Event | Where to add (file:function) |
|---|---|
| search_id generation | `app/[locale]/(public)/search/page.tsx:237` `SearchPage()` — generate once, pass as a new prop to `SearchResultsClient` |
| search event with new fields | `app/[locale]/(public)/search/SearchResultsClient.tsx:207-276` (existing tracking `useEffect`) — extend the `track()` call payload |
| result impression | Would need a new `useViewTracking`-based hook wired into `ExampleImagesGrid.tsx` / `NanoTemplateDetailClient.tsx` / `PromptCard.tsx` / a new external-result card — `useViewTracking` (`useTracking.ts:188-225`) already exists as a reusable primitive |
| result click (internal) | Existing `useClickTracking` call sites within `ExampleImagesGrid.tsx`, `GenerableTemplatesSection.tsx:29-56` — extend payload with `search_id`/`result_source`/`rank` |
| result click (external) | New card component (per Deliverable 5) — new `useClickTracking`-style call, needs a new `"external_click"` (or reuse `"click"` with `result_source: "external"`) ActionType |
| search_id handoff to destination page | Recommend a URL query param (e.g. `?from_search=<search_id>`) on the Remix/generate-CTA destination links, read by `ReproduceWorkbench.tsx`/`ExampleGeneratePanel.tsx`/`ExampleRightColumn.tsx`/`UnifiedActionBar.tsx` at their existing `trackAction(tracking, "generate")` call sites (lines cited above) |
| generation_started/success/failure | Out of scope for this audit — requires locating the actual generation-job invocation code, not covered by the search-flow exploration this audit performed |

## Explicit caveat

No backend field/table was verified to exist for any of the "NEW" fields above — this document only confirms what the **frontend** currently does and could plausibly emit. Whether `/interactions/track`'s backend schema can accept new arbitrary fields, and whether admin SQL tooling can query them, is **UNKNOWN** and out of scope for a frontend-repo read-only audit — flag for the backend team before implementation.
