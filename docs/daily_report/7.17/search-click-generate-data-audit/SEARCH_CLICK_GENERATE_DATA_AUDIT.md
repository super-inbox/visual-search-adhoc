# Search → Click → Generate Data Pipeline Audit

**Audited repository:** `/Users/baobaoli/Desktop/curify-studio`
**Remote:** `https://github.com/super-inbox/curify-studio.git`
**Branch:** `main` (up to date with `origin/main`)
**Commit:** `7b3fa5b40b03da3056536257ead2200dab031247` ("Merge origin/jwang/rong-doc-sync into main", 2026-07-16 16:30:52 +0800)
**Shallow clone:** yes (`git rev-parse --is-shallow-repository` → `true`)
**Working tree status:** clean, no modifications made during this audit
**Audit date:** 2026-07-17
**Method:** strict read-only static inspection (grep/find/read only); no code executed, no server started, no SQL executed, no database connected to, no files modified

---

## 0. Scope correction (important, read first)

The manager's brief assumes `curify-studio` is the application whose search UI and click handlers live in this repo. **That is not the case.** `curify-studio` is a **backend/ops monorepo**, containing:

- `curify_background/` — the FastAPI + SQLAlchemy/asyncpg backend (event ingestion API, analytics/admin API, generation pipelines, database models)
- `admin_portal/` — a static HTML/JS/Chart.js admin dashboard (no framework, calls the FastAPI backend)
- `dev/jayw/admin_analysis/` — one-off analyst Python scripts that reuse/extend the admin SQL
- `docs/` — internal planning/design docs
- Several unrelated microservices (`chatterbox_server`, `fastapi_whisper`, `musetalk`, `paddle_ocr_service`, `xtts_server`, `twiiterbanana`)

The actual product frontend that renders `/search`, fires click/generate tracking calls, and calls the search-matching API lives in a **separate sibling repository, `curify-frontend`**, which is **not part of this checkout** and is **out of scope** for this audit. A small number of findings below are cited from that sibling repo, clearly marked **[SECONDARY — curify-frontend, out of scope]**, because they are necessary to correctly interpret what the curify-studio backend/database can and cannot measure (e.g., under what conditions a `SEARCH` event is even sent to the backend). Everything else is drawn directly from `curify-studio`.

No interaction occurred with the other two sessions/working trees mentioned in the task (`curify-frontend-hybrid-audit`, or the 326-query benchmark session). This audit was conducted independently.

---

## 1. Where search-query data is stored/queried (Q1)

There is **no dedicated `search_logs` / `search_history` / `search_events` / `queries` table**. All search activity is stored as rows in one generic event table:

**`user_interactions`** — `curify_background/app/models/interactions.py`

```python
class ActionType(str, Enum):
    VIEW, CLICK, COPY, FAVORITE, SHARE, GENERATE, REMIX, DOWNLOAD,
    SEARCH, SEARCH_NORESULT, SEARCH_LOWRESULT, VIDEO_CLICK, VIDEO_PLAY

class UserInteraction(SQLModel, table=True):
    __tablename__ = "user_interactions"
    id: uuid.UUID                      # PK
    user_id: Optional[int]             # nullable → anonymous
    user_ip: Optional[str]
    user_agent: Optional[str]
    content_id: str                    # for SEARCH* rows: THE QUERY TEXT (+ encoded suffixes)
    content_type: ContentType           # "topic_capsule" for search rows
    action_type: ActionType
    session_id: Optional[str]
    view_mode: Optional[str]
    referrer: Optional[str]
    current_page_url: Optional[str]
    current_page_route: Optional[str]
    created_at: datetime
```

A search is "a row where `action_type` is `SEARCH`, `SEARCH_NORESULT`, or `SEARCH_LOWRESULT`." The query text itself is packed into the generic `content_id` string column, sometimes with encoded suffixes (`|within=`, `|n=<count>`, `|rw=1`, `|paths=N`) rather than dedicated columns.

Write path: `POST /interactions/track` (`curify_background/app/routers/interactions.py`) → `crud_interactions.create_interaction()` (`curify_background/app/crud/interactions.py`) — a single, public, unauthenticated, best-effort endpoint used for **every** tracked action type (view/click/copy/search/generate/etc.), not just search.

Read/aggregation path: `GET /admin/interaction-analytics` (`curify_background/app/routers/admin.py`) → `curify_background/app/crud/admin.py` (the ~1,381-line analytics engine).

There is no `.sql` schema file anywhere; the only `*.sql` file in the repo is an unrelated local dev dump (`dev/jayw/video-translation/local_dump.sql`). Schema changes are hand-rolled Python scripts in `curify_background/scripts/` (`ALTER TYPE ... ADD VALUE` for the two enums).

---

## 2. Admin dashboard pages displaying search data (Q2)

`admin_portal/` (static Vite/Tailwind/Chart.js site, tabs switched client-side via `admin_portal/js/tabs.js`):

| Tab | Relevant to Search→Click→Generate? | Evidence |
|---|---|---|
| **Business Metrics** | **Yes** — embeds the "interaction analytics" block: Search Queries table, Engagement Funnel, Surface Cohorts | `admin_portal/index.html` (`#analyticsSearchQueries`, `#analyticsEngagementFunnel`, `#analyticsSurfaceCohorts`), `admin_portal/js/fetchData.js` (`fetchInteractionAnalytics()`, `renderInteractionAnalytics()`) |
| **Project History** | No — raw generation-job rows (status/language/duration), not search-linked | `crud/admin.py: get_recent_projects()` |
| **Daily Inspiration** | Indirect only — editorial content-review queue, not user search behavior | `curify_background/app/routers/inspiration.py` |
| **RSS Ingestion** | No | `curify_background/app/routers/rss_ingestion.py` |
| **Proposals** | **Yes**, indirectly — `search_no_result` is one proposal source, turning failed search queries into content/template proposals | `curify_background/app/utils/search_no_result_utils.py`, `admin_portal/js/proposals.js` |
| **Agentic Eval** | Related to search-quality evaluation, but disconnected from real click/generate telemetry — client-side-only labeling tool using `localStorage`, reading static JSON candidate files | `admin_portal/js/agentic.js` |

The **Search Queries** table (columns: `query, searches, no_results, users, noresult_pct, result_clicks, chip_clicks, escape_clicks, result_ctr_pct`) is the only admin UI element that directly reports search→click behavior at query grain. The **Engagement Funnel** and **Surface Cohorts** tables are the only places Generate-adjacent behavior (`GENERATE`/`COPY`/`REMIX`) appears alongside Search, but only as population-level/cohort flags, not a per-search trace (see §8).

A second admin portal prototype (`dev/jayw/Curify-Admin-Portal/`) exists but runs on **mock data** (`backend/app/mock_data/jobs.py`) — not a real data source, excluded from this audit.

---

## 3. SQL / query functions powering those pages (Q3)

All backed by `curify_background/app/crud/admin.py`, querying `user_interactions` (and `project`/`user`/`transaction`/`subscription` for the non-search Business Metrics). Central function: `_compute_interaction_analytics()`, producing 9 sections: `replication_analysis`, `daily_activity`, `entry_bar_clicks`, `actions_per_page`, `session_engagement`, `engagement_funnel`, `surface_cohorts`, `search_queries`, `dau_by_landing`/`dau_by_referrer`. A duplicated "lite" fast-path (`_section_daily_activity`, `_section_search_queries`) exists for first-paint and is explicitly commented as needing to be kept in sync with the full version — a maintenance risk. Full detail in `SEARCH_SQL_QUERY_INVENTORY.csv`.

---

## 4. Is search result count stored? (Q4)

**Not as a first-class numeric column.** Result count only appears **encoded as a string suffix inside `content_id`** for low-result searches (e.g. `"cats|n=3"`), and only when `SEARCH_LOWRESULT` fires. For `SEARCH` (healthy) and `SEARCH_NORESULT` events, no count is recorded (zero is implied by the event type; for healthy searches no count is recorded at all). Classification: **DERIVABLE** for low-result searches only (requires string parsing), **MISSING** as a general-purpose numeric field.

## 5. Can zero-result and low-result searches be measured? (Q5)

Yes, directly — these are first-class `action_type` enum values (`SEARCH_NORESULT`, `SEARCH_LOWRESULT`), added via `curify_background/scripts/migrate_action_type_add_search_noresult.py` and `migrate_action_type_add_search_lowresult.py`. **However**, per **[SECONDARY — curify-frontend, out of scope]** evidence (`SearchResultsClient.tsx`), the low-result threshold is 5 results, and — critically — **a healthy, un-narrowed search with ≥5 results fires no event at all** ("the URL change is the implicit signal"). This means the denominator used for zero-/low-result rate in `_section_search_queries` (`COUNT(*) FILTER (WHERE atype='SEARCH')`) systematically **undercounts total search volume**, and any zero-/low-result *rate* computed against that denominator will be **inflated** relative to true search volume, because most healthy plain searches never enter the table at all. This is one of the most important findings of this audit (see §14, Q22).

## 6–9. Click tracking (Q6–Q9)

- **Is click behavior tracked?** Yes, generically — `action_type IN ('CLICK','VIDEO_CLICK','VIDEO_PLAY')` rows in `user_interactions`, same table as search.
- **Is clicked result rank tracked?** **No.** No `result_rank`/`position` column exists anywhere in the schema.
- **Is clicked result ID tracked?** **Partially/indirectly.** There is no dedicated `result_id` column. The clicked item's identity is only available as `content_id` (a string, e.g. a template id) combined with `content_type` (e.g. `NANO_INSPIRATION_TEMPLATE_CARD`) on the *click row itself* — but this click row is **not linked by any key to the specific search row** that produced the impression. Attribution from a search to a subsequent click is done purely by a same-user/session, 5-minute time-window heuristic SQL join (`crud/admin.py`, `_section_search_queries`), not a stored identifier.
- **Can internal vs. external result clicks be distinguished now or later?** **Not now** — there is no `result_source`/`destination_domain` column, and today all results are internal (no Hybrid Search external provider is live yet). It **could** be added later (see `HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md`), but requires new schema.

## 10–13. Generation tracking and linkage (Q10–Q13)

- **Is generate intent tracked?** Yes, as a click-log event: `action_type='GENERATE'` row in `user_interactions`, fired via the same generic `/interactions/track` endpoint.
- **Is generation success tracked?** Yes, but in a **completely different table**: `Project.status` (`curify_background/app/models/project.py`), enum including `QUEUED/STARTED/PREPROCESSING/.../COMPLETED/FAILED/APPROVED`), written by `/nano-templates/generate` and `/nano-freeform/generate` (`curify_background/app/routers/nano_templates.py`, `nano_freeform.py`).
- **Can a generation be linked back to a specific search?** **No.** Neither `/nano-templates/generate` nor `/nano-freeform/generate` accept or store a `search_id`/`result_id`. The `GENERATE` click-log event in `user_interactions` and the `Project` row created by the real generation pipeline are **written by entirely separate code paths that never call each other** — `nano_templates.py`/`nano_freeform_pipeline.py` never call `crud_interactions.create_interaction()`. There is no shared key between them at all; not even a time-window heuristic is implemented in code (unlike search→click, which has one).
- **Can a generation be linked back to a specific clicked result?** **No**, for the same reason. The one partial exception: `/nano-freeform/generate` accepts an optional `source_prompt_id` (gallery-remix origin), persisted into `Project.runtime_config`/`description` (an untyped JSON/string field, not a first-class column) — but this covers only the **gallery remix** surface, never the **search** surface, and is not a `search_id` or `result_id`.
- **Critical structural gap:** `Project` has a `user_id` column but **no `session_id` column**. This means even if a search_id/result_id linkage existed, **anonymous (not-logged-in) generations could not be tied back to an anonymous search/click at all**, because the only anonymous identity key (`session_id`) doesn't exist on the generation-record side of the join.

## 14–15. Stable IDs (Q14–Q15)

- **Is there a stable `search_id`?** **No.** One analyst script (`dev/jayw/admin_analysis/search_cycle5_pull.py`) aliases a search row's own UUID as `search_id` *inside a single SQL query's `GROUP BY`* — this is a query-local alias, not a persisted, passed-through identifier that ever reaches a click or generation event.
- **Is there a `session_id`?** **Yes** — `user_interactions.session_id` (nullable string), client-generated (per **[SECONDARY]** evidence: `sessionStorage`-based, key `_curify_session_id`). Several analytics queries filter `WHERE session_id IS NOT NULL` because it is not always present.

## 16. Are anonymous users covered? (Q16)

Yes, for the `user_interactions` event log — `user_id` is nullable and `session_id` is the fallback identity. The universal join key used throughout the analytics code is:
```sql
COALESCE(user_id::text, session_id)
```
But anonymous coverage **breaks at the generation step**: `Project` has no `session_id`, so anonymous generations cannot be attributed to anything upstream (see §10–13).

## 17. Current attribution quality (Q17) — see `SEARCH_ATTRIBUTION_FEASIBILITY.md` for full detail

**Search → Click:** LEVEL 3, Approximate attribution (session/user key + 5-minute bounded window), with known, documented edge cases that break it (see below).
**Click → Generate / Search → Generate:** LEVEL 4, Not reliably attributable per-instance. Only a population-level, non-sequential cohort correlation exists (`surface_cohorts`: users who searched at all vs. users who replicated at all in the same 7-day window) — this proves co-occurrence in a cohort, not causation or order for any individual search.

## 18–20. Metric reliability summary (Q18–Q20) — full detail in `SEARCH_FUNNEL_METRIC_DEFINITIONS.md` and `SEARCH_DASHBOARD_CAPABILITY_MATRIX.csv`

- **Reliable now:** zero-result / low-result event classification (as tracked, subject to the undercounting caveat in §5); per-query search→click CTR via the 5-minute heuristic (subject to the same caveat plus documented redirect gaps); generation start/success rate (independent of search, computed straight from `Project.status`).
- **Approximate only:** total search volume, unique search users/sessions, unique queries (content_id string is not normalized for suffix encodings), search abandonment, search refinement/requery rate (derivable but not built).
- **Not computable without new instrumentation:** search-to-generate rate, click-to-generate rate, query-level conversion rate, result-rank CTR, internal vs. external CTR (no external results exist yet), search result impression rate (no impression event at all).

## 21. Minimum tracking before a Hybrid Search A/B test (Q21) — full detail in `HYBRID_SEARCH_INSTRUMENTATION_REQUIREMENTS.md`

Minimum P0 set: `search_id` (persisted, generated at search time, passed through to every downstream impression/click/generate event), `search_mode`, `result_source`, `result_rank`, `result_click` (linked by `search_id`, not time window), `generate_click` (linked by `search_id`), `generation_success` (linked by `search_id`). Without a persisted `search_id` threaded through impression → click → generate, **no A/B test can attribute outcome differences to a specific search variant with confidence** — everything currently falls back to the same fragile time-window heuristic that already has documented failure modes (see §5, §22).

## 22. Could current reporting show higher CTR while generation decreases? (Q22)

**Yes — this is a live, structural risk, not a hypothetical.** Two independent mechanisms already present in the current codebase would each, on their own, produce this false signal:

1. **Denominator undercounting (§5):** because healthy plain searches fire no event, adding a Hybrid Search surface that generates *more clicks on external-looking cards* would increase the numerator (`result_clicks`) in `_section_search_queries` while the "searches" denominator remains an undercounted, failure-biased sample — inflating the *reported* CTR beyond its real-world value, independent of whether generation improved.
2. **No Search→Generate or Click→Generate linkage exists at all (§10–13, §17).** If Hybrid Search increases clicks on external results that don't support in-product "generate," the admin dashboard's `search_queries` table (CTR) would show an improvement, while `surface_cohorts`/`replication_analysis` (the only generation-adjacent signals) would not be able to prove *which* clicks did or didn't lead to generation — they'd only show, at best, a same-week cohort-level dip in the overall `did_replicate` rate, several steps removed from causal attribution to the search change. A dashboard viewer watching CTR alone would have no visibility into this at all.

This is why Search-to-Generate Rate and Generation Success Rate, not CTR, must be the primary decision metrics for any Hybrid Search rollout (see `SAFE_READ_ONLY_SQL_TEMPLATES.sql` and the executive summary).

---

## Key supporting evidence details

### The `user_interactions` → `search_queries` SQL (search→click attribution, `crud/admin.py`, `_section_search_queries`, duplicated ~L511-584 and ~L1139-1235)

```sql
WITH search_events AS (
    SELECT id, LOWER(TRIM(content_id)) AS query,
           COALESCE(user_id::text, session_id) AS who,
           created_at AS searched_at, action_type::text AS atype
    FROM user_interactions
    WHERE action_type::text IN ('SEARCH', 'SEARCH_NORESULT', 'SEARCH_LOWRESULT')
      AND content_id IS NOT NULL
      AND created_at >= NOW() - INTERVAL '7 days'
      AND (user_id IS NULL OR user_id NOT IN (155, 1117, 1267))   -- hardcoded test-user exclusion
),
clicks_on_search AS (
    SELECT COALESCE(user_id::text, session_id) AS who,
           created_at AS clicked_at, content_type::text AS ctype
    FROM user_interactions
    WHERE action_type::text IN ('CLICK', 'VIDEO_CLICK', 'VIDEO_PLAY')
      AND current_page_route = '/search'
      AND created_at >= NOW() - INTERVAL '7 days'
      AND (user_id IS NULL OR user_id NOT IN (155, 1117, 1267))
),
attributed AS (
    SELECT s.id, s.query, s.atype, s.who,
           BOOL_OR(c.ctype IN ('NANO_INSPIRATION_EXAMPLE_GRID','NANO_INSPIRATION_TEMPLATE_CARD')) AS had_result_click,
           BOOL_OR(c.ctype = 'TOPIC_CAPSULE') AS had_chip_click,
           BOOL_OR(c.ctype = 'MENU_LINK')     AS had_escape_click
    FROM search_events s
    LEFT JOIN clicks_on_search c
      ON c.who = s.who
     AND c.clicked_at BETWEEN s.searched_at AND s.searched_at + INTERVAL '5 minutes'
    GROUP BY s.id, s.query, s.atype, s.who
)
SELECT query,
       COUNT(*) FILTER (WHERE atype='SEARCH')                                  AS searches,
       COUNT(*) FILTER (WHERE atype IN ('SEARCH_NORESULT','SEARCH_LOWRESULT')) AS no_results,
       COUNT(DISTINCT who)                                                     AS users,
       ROUND(100.0 * <no_results_calc>, 1)  AS noresult_pct,
       COUNT(*) FILTER (WHERE had_result_click) AS result_clicks,
       COUNT(*) FILTER (WHERE had_chip_click)   AS chip_clicks,
       COUNT(*) FILTER (WHERE had_escape_click) AS escape_clicks,
       ROUND(100.0 * result_clicks / NULLIF(searches,0), 1) AS result_ctr_pct
FROM attributed
GROUP BY query
HAVING COUNT(*) FILTER (WHERE atype='SEARCH') > 0
ORDER BY no_results DESC, searches DESC
LIMIT 50
```

Documented gaps in the analyst extensions of this query (`dev/jayw/admin_analysis/search_cycle5_pull.py`): server-side redirects from `/search` → `/topics/<slug>` for certain queries never fire a click event on `/search` at all (a special `content_id='search-redirect'` marker was invented as a workaround — direct evidence that attribution is patched around, not designed in).

### Generation pipeline entry points (no search linkage)

- `POST /nano-templates/generate` (`curify_background/app/routers/nano_templates.py`) — request body: `{template_id, params, example_id?, reference_image_url?}`. No `search_id`/`result_id`.
- `POST /nano-freeform/generate` (`curify_background/app/routers/nano_freeform.py`, pipeline in `curify_background/app/pipelines/nano_freeform_pipeline.py`) — request body: `{prompt, reference_image_url?, source_prompt_id?}`. `source_prompt_id` covers gallery-remix only.
- Both create/update a `Project` row (`curify_background/app/models/project.py`) — `project_id, user_id, status, job_settings_raw (JSON), runtime_config (JSON), cost_credits, created_at/updated_at`. No `template_id`, `search_id`, or `result_id` first-class columns.

### Bot filtering and data-quality caveats

- `_bot_free_cte()` (`crud/admin.py`) — a 3-stage filter (known-bot user-agent strings, single-event "sessions," carousel-scraper patterns), backing most analytics sections. Comments acknowledge it cannot distinguish true direct traffic from empty-referrer bots.
- A materialized view `bot_free_30d` (`curify_background/scripts/migrate_bot_free_matview_and_indexes.py`) was built to speed this up, but per code comments is **currently dead code** — Supabase's `pg_cron` is not enabled, so nothing refreshes it; analytics reverted to the inline CTE on 2026-06-08. An admin endpoint `POST /admin/refresh-bot-free-matview` exists but nothing calls it on a schedule.
- Hardcoded test-user exclusion list is **inconsistent** across scripts: `(155, 1117, 1267)` in some places, `(155, 1117)` in others — a data-quality issue worth resolving before trusting absolute counts.
- No cron/scheduled job computes or precomputes funnel metrics; the dashboard runs live queries with a 30-minute in-process TTL cache.
- No external analytics/warehouse tool (PostHog, Mixpanel, Amplitude, Segment, ClickHouse, BigQuery) is used anywhere in this repo — all analytics is first-party SQL directly against Supabase-hosted Postgres.

### Security note (flagged, not exploited)

`curify_background/scripts/migrate_content_type_enum.py` contains a **hardcoded fallback production Supabase Postgres connection string with an embedded password** in a `DATABASE_URL` default value. The value itself is **not reproduced anywhere in this audit's outputs**. This should be rotated and removed from source control as a follow-up, independent of the search/click/generate analytics question.

---

## Limitations of this audit

1. This audit is strictly static/read-only; no query above was executed, so exact row counts, current CTR values, or current generation-success percentages are **not** reported — only whether they are structurally computable.
2. Several findings (search-event-firing conditions, click handler code, the actual `/search` page and tracking-wrapper implementation) live in the sibling `curify-frontend` repository, outside the nominal audit scope. They are clearly marked `[SECONDARY]` above and in the supporting files. If the manager wants this audit strictly confined to `curify-studio`'s own files, those specific claims should be treated as unverified-by-this-repo (though they were independently confirmed by a read-only inspection of the sibling repo on this same machine).
3. It is possible that additional analytics code exists in branches other than `main`, or in commits not reachable from this shallow clone; this audit only covers the current `main` HEAD as checked out.
4. No live database was queried, so it is not verified whether the columns/tables described in the SQLModel classes exactly match the live production schema (e.g., whether all enum migrations have actually been applied in production).

---

**FINAL_STATUS: COMPLETE_WITH_LIMITATIONS** (see `FINAL_AUDIT_LOG.md` for the full validation checklist)
