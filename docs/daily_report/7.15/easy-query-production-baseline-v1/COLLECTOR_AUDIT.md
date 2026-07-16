# COLLECTOR_AUDIT.md — Collector Audit & Isolated Adaptation

## Result: `EXISTING_COLLECTOR_REQUIRES_ISOLATED_ADAPTATION`

Two categories of existing "300+ Easy Query" collection tooling were found. They are fundamentally different in what they call, and only one is usable as a starting point.

## Collector A (rejected as unsafe for this task): `scripts/easy-query-validation-300plus/run_full_easy.cjs`

This is the orchestrator that produced the 2026-07-14 result set referenced in `QUERY_FILE_AUDIT.md`. Audit against the checklist:

| Check | Finding |
|---|---|
| Calls production | **No.** It shells out to `scripts/curify-search-stage7-full-rerun-v2/run_one_mode.cjs` with `CURIFY_ROOT = /Users/baobaoli/Desktop/curify-frontend` (the local dev clone), loading `.env.local` from that clone and running `--mode D --d-enabled true --g-enabled true`. |
| Calls localhost/preview | No HTTP server involved at all — it's an in-process/local simulation of the search engine, not a browser or HTTP call to any deployed site. |
| Depends on local product code | **Yes**, entirely — and specifically the **uncommitted, unpushed local optimization branch** (`baobao/search-relevance-phrase-alias-2026-07-09`). |
| Includes post-optimization features (d/g toggle, etc.) | **Yes**, explicitly (`--d-enabled true --g-enabled true`, its own doc-comment calls these "production defaults" — which this task's investigation in `CODE_VERSION_AUDIT.md` shows is **incorrect**; they are not deployed to production at all). |
| Overwrites old results | No (checkpoint-skip logic present), but moot given the above. |

**Conclusion**: Collector A cannot be used, adapted, or reused in any form for this task — it structurally cannot reach the live production website; it only exercises local optimized code. Using it, even with input-file changes, would violate task rules #12/#13/#15 (no local optimized code as a stand-in for production).

## Collector B (adapted as the basis for this baseline): `scripts/curify-search-collect/collect_curify_search.mjs`

A Playwright-based collector, previously run successfully in `--full` mode against the 68 gold hard queries (evidence: `docs/daily_report/7.7/curify_search_auto_collect_2026-07-07.csv`, 68 rows, and `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/`, 68 screenshots, ~51 MB total — a working precedent of safe, successful production collection). SHA-256 of original: `62ac14abacb2166e55a0a5de26f5760bb5e46111f9d11310f83fd70bd4e5f189` (472 lines).

Audit against the checklist:

| # | Check | Finding |
|---|---|---|
| 1 | Input file path | Hardcoded to the 68-row gold CSV (`docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv`) — must be changed |
| 2 | Query field reading | `csv-parse/sync` with `columns: true`; reads `row.query` verbatim |
| 3 | Preserves original order | Yes — iterates `records` in file order |
| 4 | Dedup | No |
| 5 | Filters empty queries | No explicit filter (would attempt to navigate with an empty `q=`) |
| 6 | Modifies query text | No — passed through `encodeURIComponent` only (transport encoding, not content modification) |
| 7 | Trims | No |
| 8 | Changes case | No |
| 9 | Appends extra keywords | No |
| 10 | Calls production | **Yes** — `BASE_URL = "https://www.curify-ai.com"`, navigates to `/search?q=<query>` |
| 11 | Calls localhost | No |
| 12 | Calls preview | No |
| 13 | Calls internal API | No — page navigation only, same as a real browser user |
| 14 | Depends on local product code | No — pure HTTP/browser client, zero dependency on any local repo checkout |
| 15 | Includes d/g optimization | No |
| 16 | Enables LLM rewrite | N/A — LLM rewrite is server-side production behavior (see `CODE_VERSION_AUDIT.md`); the collector itself never calls an LLM |
| 17 | Collector calls LLM | **No** — confirmed no OpenAI/LLM SDK import anywhere in the script |
| 18 | Records raw rewrite | Partial — detects the "Few results for X / Also showing results for Y" banner text as a rewrite/broaden signal, but doesn't have a distinct raw-response capture channel |
| 19 | Records broadened query | Partial — same banner-text mechanism |
| 20 | Records result count | Yes — `visible_result_count` (count of extracted cards, capped at `MAX_RESULTS = 10`) |
| 21 | Records Top Results | Yes — top 10 titles/links/tags/types |
| 22 | Saves raw response | Partial — writes one combined JSON array at the **end** of the whole run (`OUT_JSON`), not per-query immediately |
| 23 | Saves screenshots | Yes, full-page, but only guaranteed on error paths in the original; success paths also screenshot in practice |
| 24 | Supports resume | **No** — no per-query checkpoint file, no skip-if-already-done logic |
| 25 | Supports checkpoint | **No** |
| 26 | Retry | **No** — single attempt per query, no retry logic at all |
| 27 | Concurrency limit | Implicitly 1 (single sequential loop, single page) |
| 28 | Handles rate limit | No explicit 429/backoff handling |
| 29 | Handles timeout | Yes — `NAV_TIMEOUT_MS = 30000`, `RESULT_WAIT_TIMEOUT_MS = 20000`, caught and flagged `page_error`/`extract_failed` |
| 30 | Handles captcha | No explicit captcha detection |
| 31 | Overwrites old results | Would overwrite `OUT_CSV`/`OUT_JSON` on every full run (same fixed output path) — **unsafe to run as-is against this task's directory** |
| 32 | Skips queries on exception | Records an error result rather than skipping — good |
| 33 | Auto-writes failures as 0 | **No** — `visible_result_count = 0` is only set when 0 cards are actually extracted; a `page_error`/`extract_failed` flag is set separately, distinguishing failure from a genuine zero-result. This distinction is preserved and made more explicit (`final_status` enum) in the adapted version. |
| 34 | Reuses cache incorrectly | No shared cache between queries observed |
| 35 | Depends on cookies/API key/login | No login required; `NEXT_LOCALE` cookie is set automatically by the site and not manipulated by the script |
| 36 | Modifies production data | No — GET navigation only, no forms submitted, no mutating requests |
| 37 | Excessive load on production | No — sequential, 1–2s delay between queries, single browser context |

**Conclusion**: `EXISTING_COLLECTOR_REQUIRES_ISOLATED_ADAPTATION`. Collector B's production-targeting core (URL construction, login-wall detection, DOM extraction logic, screenshot capture) is safe and correct and was reused verbatim in the adapted script. What needed changing was purely collection/checkpoint/output plumbing — never the search algorithm, never anything that talks to the product repo.

## Adaptation performed

- **Copied unmodified** to `scripts/original_reference/collect_curify_search.mjs` (SHA-256 `62ac14abacb2166e55a0a5de26f5760bb5e46111f9d11310f83fd70bd4e5f189`, verified identical to the source in `visual-search-adhoc/scripts/curify-search-collect/`). The original script was **not edited in place**.
- **New file** written at `scripts/collect_easy_query_baseline.mjs` (SHA-256 `bec305912927f5c8ff3f786e15449b6ac0ccbdc2b8b6375462a7b121ebdf02bf`, 568 lines) in this isolated run directory.

### What changed and why

| Change | Reason |
|---|---|
| Input CSV → `query_input/easy_queries_cleaned_300_plus_2026-07-14.csv`, read via `easy_id`/`query` columns | Task requires the confirmed authoritative 328-row Easy Query file, not the 68-row gold set |
| One JSON file written **immediately** per query (`raw/<idx>_<easy_id>.json`) instead of one combined array at end-of-run | Required for checkpoint/resume safety — a crash mid-run must not lose completed work |
| `isCompletedSuccessfully()` resume check: skip a query only if its prior record has `final_status` ∈ {SUCCESS, ZERO_RESULT, LOW_RESULT, INPUT_INVALID} | Errors/timeouts must always be genuinely retried on resume, never silently treated as done |
| Retry loop, max 2 attempts, only on navigation exceptions (network/timeout) | Task requires bounded retry, and retries must never apply to a legitimately-executed zero-result search |
| `final_status` enum (SUCCESS / ZERO_RESULT / LOW_RESULT / NETWORK_ERROR / TIMEOUT / PARSE_ERROR / INPUT_INVALID / UNKNOWN_ERROR) | Required so failures can never be silently recorded as "0 results" |
| Checkpoint file every 10 completed queries (`checkpoints/checkpoint_after_N.json`) | Explicit task requirement |
| Top results reduced from 10 → 5, with `image_url` extracted as its own field separate from `title` | Matches the per-query record schema (`top_result_1..5_*`) requested for this task |
| `--smoke <idx1,idx2,...>` mode writes to a separate `raw/smoke_test/` + `screenshots/smoke_test/` subtree, never touching the full-run `raw/`/`screenshots/` paths | Smoke Test must not overwrite or interleave with the formal 328-query run, and the 5 sampled queries stay in the full run too (nothing is removed from the input file) |
| Full-page screenshot taken on **every** query (not just failures) | Task's evidence bar for this baseline explicitly asks for broader screenshot coverage than the original ad-hoc script guaranteed |
| Empty-query row handling: recorded as `final_status: "INPUT_INVALID"`, never silently dropped | Task rule #4/#28 |
| No mutation of `OUT_CSV`/single shared output path — every output path is per-query and per-run-mode | Prevents any possibility of overwriting existing results from a different run |

### What was explicitly NOT changed

- URL construction (`${BASE_URL}/search?q=${encodeURIComponent(query)}`) — identical.
- Login-wall detection logic — identical, copied verbatim.
- DOM card-extraction selectors and "few results / also showing results for" banner detection — identical logic, only the output shape changed (added `image_url`, capped differently).
- No search-ranking, rewrite, or matching logic of any kind exists in either script — both are pure browser drivers.
- `BASE_URL` remains the real production domain confirmed in `CODE_VERSION_AUDIT.md`.

## Safety checklist for the adapted collector

- Concurrency: 1 (single `page`, sequential `for` loop) ✅
- Delay between queries: 1200–2200ms random ✅
- Navigation timeout: 45s (within the 30–60s band) ✅
- Max retries: 2, network/timeout only ✅
- No infinite retry loops ✅
- No write/mutating requests to production ✅
- No credentials, cookies, or login state manipulated ✅
- Checkpoint every 10 queries + per-query immediate write ✅
- Resume-safe (skips only genuinely completed queries) ✅
