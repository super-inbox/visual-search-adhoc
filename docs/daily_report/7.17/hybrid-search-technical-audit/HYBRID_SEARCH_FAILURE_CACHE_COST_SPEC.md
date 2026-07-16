# Hybrid Search — Failure, Timeout, Cache, Cost, and Feature Flag Design

Design only — no timeout/cache implementation exists for an external provider today (none exists to reference). Where the existing LLM-rewrite implementation (`lib/searchRewrite.ts`) provides a directly analogous, already-production-validated pattern, it is cited and reused as precedent; where no precedent exists, only *ranges* are proposed per the task's instruction not to assign precise values without code evidence.

## Timeouts

| Component | Existing precedent | Proposed range (NOT finalized) |
|---|---|---|
| LLM rewrite call | `TIMEOUT_MS = 8_000` (`lib/searchRewrite.ts:20`), explicitly "bumped from 5s — gives cold-start OpenAI clients more headroom" | Keep as-is; already tuned from one real incident class (cold starts). No change proposed. |
| External provider call | No precedent in this repo | Recommend evaluating in the **3,000-6,000ms** range, informed by real latency measurements gathered in Rollout Stage 3 (mocked/sample validation) — not assumed from this document. Should likely be tighter than the LLM timeout since image-search APIs are typically lower-latency than an LLM completion call, but this must be measured, not guessed. |
| Total latency budget (page render) | No explicit page-level timeout found in `page.tsx` — the RSC simply awaits whatever it awaits | Recommend defining an explicit **total hybrid-path budget** (e.g., internal retrieval + max(LLM timeout, external timeout) run in parallel, so total added latency ≈ the slower of the two legs, not their sum) — this is the direct benefit of parallel execution (`Promise.allSettled`) over sequential, and should be measured/validated, not assumed. |

## Parallel execution & partial success

- **Must use `Promise.allSettled`, not `Promise.all`** — a rejected external-provider promise must not throw and abort the LLM-rewrite leg, and vice versa. This is a direct, mandatory consequence of the "failure must never prevent returning internal results" guarantee.
- Partial success behavior: if the LLM rewrite succeeds but the external call fails (or vice versa), render whatever succeeded — Mode B-equivalent behavior on external failure, Mode C-equivalent (internal + external, no rewrite) on LLM failure. Never block the internal-only result set on either.
- Internal retrieval (`scoreQueryTokens`) is synchronous and always completes before either async leg is even started (per the call graph) — so "the original internal results" are never at risk from either external system's behavior, by construction. This is the strongest form of the required guarantee: not a try/catch safety net, but a structural ordering guarantee.

## Retry policy

- No retry precedent exists in `lib/searchRewrite.ts` — it fails fast, once, per request. **Recommend the same fail-fast posture for the external call at MVP**: no in-request retries. A retry would extend tail latency for a signal (thin results) that is already latency-sensitive, and would consume additional provider quota for a call that's already being made only because internal results were thin. Retries, if wanted, belong at the caching layer (retry the underlying miss on a *future* request, not within the same request).

## Provider quota handling & circuit breaker

- No existing precedent for quota/circuit-breaker logic anywhere in this codebase (the LLM rewriter has no explicit quota-tracking — it fails safe on any OpenAI error, which implicitly covers quota-exceeded errors too, but doesn't distinguish them for backoff purposes).
- **Recommend**: a simple circuit breaker keyed on consecutive external-provider error count within a rolling window (e.g., N failures in M minutes → stop calling the provider entirely for a cool-down period, serve Mode-B-equivalent behavior). Exact N/M values are **unresolved** — should be tuned from real error-rate data gathered during staging QA (Rollout Stage 7), not guessed here.
- This is functionally the automated, systemic version of the `EXTERNAL_SEARCH_KILL_SWITCH` flag below (manual override) — both should exist; the circuit breaker is the automatic first line of defense, the kill switch is the manual escape hatch.

## Success cache / negative cache

| Aspect | LLM rewrite precedent (`lib/searchRewrite.ts:245-274`) | Proposed for external provider |
|---|---|---|
| Cache key | `trimmed.toLowerCase()` (query only) | Recommend `(retrieval_query, locale)` — per Extension C's explicit design intent ("7-day key by (query, locale)," line 251) — locale matters for external search because image relevance is locale-dependent in a way the LLM rewrite's catalog-matching is not. |
| Storage | **Process-local `Map`, in-memory** — explicitly documented as NOT shared across Vercel serverless invocations ("Vercel serverless invocations don't share memory so this saves nothing across requests in prod," `searchRewrite.ts:248-249`) | **Must NOT repeat this limitation for the external leg** — because external calls are billed per-query (unlike the LLM leg, which is also billed but the comment doesn't flag cost as the reason for wanting a shared cache), an in-memory-only cache provides near-zero hit rate in a serverless deployment and would not meaningfully bound cost. Recommend a **shared, persistent cache** (Vercel KV or Redis — the `redis` npm package is already a project dependency per `package.json`, so this is a small, low-risk addition to evaluate, not a new vendor) from day one for the external leg specifically. |
| TTL | 7 days (`CACHE_TTL_MS`) | Reuse 7 days as the starting point (matches Extension C's stated intent exactly) — but treat as a tunable, not fixed, pending compliance review of what caching duration Google's ToS actually permits (Provider Options doc flags this as unresolved). |
| Negative cache | Not cached on parse failure or transient error ("do NOT cache empty on transient errors — failed cache eats 7 days of retries," `searchRewrite.ts:359-360`); IS cached on a confirmed zero-result response | Recommend the same distinction: cache a confirmed "provider returned 0 relevant images for this query" result (short-to-medium TTL, avoids re-paying for a query with no better answer), but never cache a transient error/timeout (so a temporary outage self-heals on the next real request). |
| Stale-result policy | N/A (rewrites don't go stale in the same way images do) | External images CAN go stale (page moved, image deleted) — cache staleness is a listed risk (Risk Register). MVP mitigation: client-side broken-image handling (hide/skip a card whose image fails to load) rather than server-side freshness verification, which would require an extra fetch per cached entry and defeat the purpose of caching. |

## Cost tracking

- No cost-tracking instrumentation exists for the LLM rewrite calls today (confirmed — `lib/searchRewrite.ts` logs errors via `console.error` but does not emit a cost/usage metric). **This is itself a gap worth flagging**, independent of the hybrid feature: neither the shipped LLM-rewrite feature nor any future external-search feature currently has cost observability.
- Recommend the hybrid feature ship with `rewrite_cost_estimate` and `external_cost_estimate` fields from day one (already specified in the Core-80 CSV schema, Deliverable 11) — both for the offline experiment AND as a pattern to carry into production observability, rather than repeating the existing gap.

## Provider error tracking / observability fields

Recommend logging (structured, not necessarily a new dashboard at MVP) at minimum: `external_provider`, `http_status_or_error_code`, `latency_ms`, `cache_hit: boolean`, `circuit_breaker_state`, `query_hash` (not raw query, for log-volume/privacy reasons — see Risk Register "query privacy risk"). This mirrors the level of detail `lib/searchRewrite.ts` already logs for the LLM leg (query, finish reason, elapsed ms, error message) — same rigor, applied to the new leg.

## Required guarantee (restated as the single hardest constraint)

**Failure of the LLM rewrite OR the external search must never prevent returning the original internal results.** This is structurally satisfied by the call-graph ordering (internal retrieval is synchronous and complete before either async leg starts) plus `Promise.allSettled` for the two async legs. No implementation of Mode D or E should deviate from this ordering — it is the single non-negotiable safety property of the whole feature.

## Independent feature flags

| Flag | Purpose | Why independent |
|---|---|---|
| `ENABLE_LLM_REWRITE` | Master on/off for the (already-shipped) LLM rewrite leg | Must be independently toggleable from the external leg so a bad LLM-rewrite regression can be killed without also killing external fallback, and vice versa — bundling them would make incident response slower and less precise. |
| `ENABLE_EXTERNAL_IMAGE_FALLBACK` | Master on/off for whether the external call is made at all | Separate from UI rendering (below) so the call can be disabled (stops cost/quota consumption) independent of whether any already-cached results are still shown. |
| `ENABLE_HYBRID_RESULT_MERGE` | Whether merge logic combines internal+external into one ordered structure, vs. rendering them as fully separate sections | Lets the team ship "external results exist as a separate labeled rail" (Mode C/D-like) before committing to the more complex unified-ranking merge policy (Mode E) — an intentionally staged rollout lever, not just an incident switch. |
| `ENABLE_EXTERNAL_RESULT_UI` | Whether the external rail renders in the client at all | Separate from whether the call is made — allows "dark launch" data collection (call the provider, log results, don't show them to users yet) as an offline-adjacent validation step before any user-visible change ships. |
| `EXTERNAL_SEARCH_KILL_SWITCH` | Single, fast, highest-priority override — when true, the entire external leg is disabled regardless of the other four flags | This is the manual escape hatch for the exact failure mode Extension C names explicitly: "if `external_click → curify_create` conversion < 8%, kill the rail" (line 257). Must be checkable/settable without a deploy (an env var or remote config, not a hardcoded constant) so it can respond in minutes, not a release cycle. |

**Why independence matters**: each flag answers a different question (Is the LLM leg healthy? Is the external leg healthy? Is the merge logic ready? Is the UI ready? Should we panic-disable everything?) and bundling any two into one flag removes the ability to answer one "yes" and one "no" simultaneously — which is exactly the situation an incident (e.g., external provider outage while LLM rewrite is fine) will produce.
