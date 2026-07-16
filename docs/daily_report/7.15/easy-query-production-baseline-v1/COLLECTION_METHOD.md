# COLLECTION_METHOD.md — Phase 6: Collection Method Selection

## Decision

| Field | Value |
|---|---|
| `collection_mode` | Browser automation (Playwright, Chromium, headless) — **first choice** per task priority order |
| `collection_target` | Live production website |
| `collection_url` | `https://www.curify-ai.com/search?q={query}` (query passed via `encodeURIComponent`, no other transformation) |
| `browser_or_api` | Browser — full page navigation (`page.goto`), not a raw HTTP/fetch call |

## Why browser navigation, not a separate API call

`app/[locale]/(public)/search/page.tsx` (confirmed at `production_commit` `72b55b6`, see `CODE_VERSION_AUDIT.md`) is a Next.js App Router **server component**. The search results (including any server-side LLM rewrite/decomposition/broadening decisions) are computed server-side and delivered as part of the initial HTML response to `GET /search?q=...` — there is no separate client-side XHR/fetch/GraphQL call that fetches results after page load. This was verified two ways:

1. **Source audit**: no `fetch("/api/search...")`-style client call exists in `SearchResultsClient.tsx`; all result data arrives as server-rendered props.
2. **Live HTTP check** (read-only, single request): `curl -s -D - "https://www.curify-ai.com/search?q=flower"` returns `HTTP/2 200`, `x-matched-path: /[locale]/search`, and the full HTML body already contains rendered `nano-template/...` result links — confirming results are present in the very first response, not fetched afterward.

Given this, "navigate a real browser to the search URL and read the rendered DOM" **is** the production search transport — it is not an approximation of it. This also means calling any lower-level API directly would risk missing exactly the server-side rewrite/decomposition/broadening logic this baseline exists to observe, so Choice 1 (browser automation against the real page) was used rather than Choice 2 (a lower-level API call).

## Rejected alternatives

- **Local production-commit checkout run** (Choice 3): not used. The live site is fully accessible and functioning (verified below), so the task's ordering ("仅限于线上无法稳定采集且 production commit 已明确确认") does not license falling back to a local re-run even though the production commit *is* confirmed. A local Next.js dev/prod build would also require live `OPENAI_API_KEY` and production catalog data neither of which are safely reproducible outside Vercel's actual environment, and would reintroduce exactly the "local code standing in for the live site" risk this task forbids by default.
- **Local optimized code** (`/Users/baobaoli/Desktop/curify-frontend`, uncommitted branch): explicitly forbidden per task rules and `CODE_VERSION_AUDIT.md`.
- **Preview/staging deployments**: none used; only the confirmed Production-environment domain `curify-ai.com` was targeted.
- **Mocked/fake responses**: none — every record in `raw/` reflects an actual Playwright-observed DOM state from a real network round-trip to `curify-ai.com`.

## Verification that this matches what a human/browser user would see

- Search page requires no login (`login_wall` detection built into the collector; confirmed manually not triggered on `q=flower`).
- No captcha, region lock, or Cloudflare interstitial encountered on manual checks.
- No admin-only behavior is invoked — GET navigation with a public, unauthenticated `page.newContext()` (no stored cookies/credentials, no auth headers).
- No write operation is ever issued (`page.goto` only; no form submission, no POST).
- Client-side tokenization/rendering is included automatically, since Playwright executes real JS in a real Chromium instance (not a bare HTML fetch) — this is why browser automation was chosen over `curl`.
- Server-side rewrite/broadening is included automatically, since it happens before the HTML response is even sent (see above) — nothing is "skipped" between server and what the collector reads.

## Parameters (match production defaults / task's recommended safety envelope)

- `concurrency`: 1
- `request_delay`: 1200–2200 ms randomized between queries
- `timeout`: 45,000 ms navigation timeout (within the 30–60s recommended band), 20,000 ms result-wait timeout
- `retry_policy`: max 2 attempts, only for navigation-level network/timeout errors; zero-result and low-result outcomes are never retried (they are valid, successfully-executed search outcomes)
- `checkpoint_policy`: one JSON file written immediately per completed query, plus a rollup checkpoint file every 10 queries
- `resume_supported`: yes — a query is only skipped on restart if its existing record has `final_status` ∈ {SUCCESS, ZERO_RESULT, LOW_RESULT, INPUT_INVALID}
- Browser: Chromium (Playwright `playwright@^1.61.1`), headless by default, viewport 1440×900, locale `en-US`, fresh `BrowserContext` for the whole run (not per-query, but every query is a full `page.goto` to a fresh URL — no client-side search state carries over between queries)
