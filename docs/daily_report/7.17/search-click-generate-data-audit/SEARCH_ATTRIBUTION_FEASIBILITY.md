# Search → Click → Generate Attribution Feasibility

Repository: `curify-studio` @ `7b3fa5b40b03da3056536257ead2200dab031247` (branch `main`)

## Segment-by-segment classification

Rather than force one single global level onto the whole funnel, each link is classified separately because the evidence shows they are not uniform.

### Search → Click: **LEVEL 3 — Approximate attribution**

Evidence: `curify_background/app/crud/admin.py`, `_section_search_queries()`. A search row and a click row are joined via:
```
who = COALESCE(user_id::text, session_id)
clicked_at BETWEEN searched_at AND searched_at + INTERVAL '5 minutes'
AND current_page_route = '/search'
```
This is a bounded time-window join on a user/session key — the definition of Level 3. It is not Level 2 because there is no `result_id` shared between the two events to prove *which* result was clicked as a consequence of *which* result set, and it is not Level 1 because there is no `search_id`.

Known failure modes (documented in the code/comments themselves):
- **Multiple searches in one session create ambiguity.** If a user searches twice within 5 minutes, a click could be attributed to the wrong search.
- **Server-side redirects break attribution entirely.** `/search` → `/topics/<slug>` redirects for certain queries drop the user onto a topic page without ever firing a click event on `/search` — `dev/jayw/admin_analysis/search_cycle5_pull.py` had to invent a synthetic `content_id='search-redirect'` marker as a workaround, direct evidence the join misses real clicks.
- **Missing `session_id` rows** — several queries filter `WHERE session_id IS NOT NULL`, meaning some anonymous activity is silently excluded rather than joined.
- **[SECONDARY — curify-frontend]** Only a subset of searches even fire a `SEARCH`-family event (zero-result, low-result, or chip-narrowed searches) — a healthy plain search with ≥5 results never generates a row at all, so the "searches" side of the join systematically excludes most successful top-of-funnel searches.

### Click → Generate: **LEVEL 4 — Not reliably attributable**

Evidence: the `GENERATE` click-log event (`user_interactions.action_type='GENERATE'`, written via `POST /interactions/track`) and the actual generation record (`Project` row, written via `POST /nano-templates/generate` or `POST /nano-freeform/generate`) are produced by **two code paths that never call each other**. `curify_background/app/routers/nano_templates.py` and `curify_background/app/pipelines/nano_freeform_pipeline.py` never call `crud_interactions.create_interaction()`. There is no shared key, and — unlike Search→Click — **no time-window heuristic is implemented in code either**; any such join would have to be built from scratch, and even then would be limited to logged-in users only (see below).

### Search → Generate (direct): **LEVEL 4 — Not reliably attributable**, with one **population-level Level 3-ish proxy**

The only place Search and Generate co-occur in any query is `surface_cohorts` (`crud/admin.py`): a `'searcher'` cohort (`BOOL_OR(action_type='SEARCH')` in a 7-day window) is cross-tabbed against a `did_replicate` flag (`BOOL_OR(action_type IN ('COPY','GENERATE','REMIX'))` in the same window). This proves **co-occurrence within a cohort and a week**, not that any individual user's specific search caused their specific generation. It cannot answer "did search X lead to generation Y" for any single instance — only "what fraction of people who searched at all also generated at all this week."

## Exact join keys available

- `COALESCE(user_id::text, session_id)` — the only identity join key in the system, used for every attribution query found.
- Timestamp proximity (`created_at` column, compared via `BETWEEN ... AND ... + INTERVAL`) — the only temporal join mechanism, and it is only actually implemented for Search→Click (5 minutes), not for Click→Generate or Search→Generate.
- `current_page_route = '/search'` — a route filter used to scope which clicks count as "on the search page," itself a proxy for "resulting from a search," not a guarantee.

## Which links are missing

| Link | Status |
|---|---|
| Search → Result Impression | Missing entirely — no impression event exists |
| Result Impression → Click | Missing (no impression event to join against) |
| Search → Click | Present, heuristic (5-min window + user/session key) |
| Click → Generate (specific item) | Missing — no shared key, no time-window join implemented |
| Search → Generate (specific instance) | Missing — only a population-level weekly cohort correlation exists |
| Generation → source Result | Missing — `Project` has no `source_result_id`/`search_id` column; only `source_prompt_id` for gallery-remix (unrelated to search) |

## Ambiguity and attribution risk

- **Multiple searches per session:** yes, creates ambiguity in the 5-minute Search→Click join (a click could get attributed to the wrong one of several recent searches).
- **Multiple clicks per session:** yes — the join uses `BOOL_OR(...)` across all clicks in the window, so a session with several clicks on different content types all get folded into the same search row's `had_result_click`/`had_chip_click`/`had_escape_click` flags; it cannot say which specific click, if any, led anywhere further.
- **Anonymous users included?** Yes, for the `user_interactions` event log (via `session_id`). **No**, for the generation side — `Project` has no `session_id` column, so an anonymous user's generation cannot be tied to their anonymous search/click history at all, only a logged-in user's `user_id` could theoretically bridge that gap (and even then, no code currently does so).
- **Logged-in vs. anonymous identifiers:** logged-in users get a stable `user_id` (custom int auth, not Supabase Auth); anonymous users get only a client-generated `session_id` string with no documented persistence guarantee (session storage-based per secondary evidence — cleared on tab close in many browsers).
- **Cross-device attribution:** none exists. There is no device fingerprint, email-based matching, or persistent anonymous ID that would survive a device change; a `user_id` only bridges devices once a user logs in on both.

## False-positive / false-negative risk

**False positives (attributing a click/generation to a search that didn't actually cause it):**
- The 5-minute window can attribute an unrelated click (e.g., a menu click that happens to land within 5 minutes of an unrelated search) to that search.
- The weekly cohort correlation (`surface_cohorts`) can count a user as "searched → replicated" even if their generation was driven entirely by an unrelated gallery remix.

**False negatives (missing a real search→click→generation link):**
- Any healthy, plain, un-chipped search with ≥5 results never fires a `SEARCH` event at all **[SECONDARY — curify-frontend evidence]**, so its downstream clicks/generations are invisible to the Search Queries table entirely.
- Redirected `/search → /topics` flows lose their click event unless the synthetic `search-redirect` marker was applied.
- Any click that happens more than 5 minutes after a search is dropped from attribution even if it was the direct result of that search (e.g., a user who takes time deciding).
- All Click→Generate and Search→Generate links for any individual instance are false negatives by construction today — there is no mechanism to detect them at all.

## Bottom line

**Best currently available attribution level for the full funnel: LEVEL 4 (Not reliably attributable end-to-end)**, downgraded from the Search→Click segment's Level 3 because the chain breaks completely at Click→Generate. Any dashboard number that appears to show "Search leads to Generate" today is, at best, the `surface_cohorts` weekly correlation — which should be labeled as a correlation, not a funnel conversion rate, in any reporting that uses it.
