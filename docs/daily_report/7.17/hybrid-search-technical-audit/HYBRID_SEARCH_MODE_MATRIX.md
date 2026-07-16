# Hybrid Search — Five Experimental Mode Matrix

All five modes reuse the **existing** internal retrieval engine (`scoreQueryTokens` in `page.tsx`) and the **existing** LLM rewriter (`getMultiQueryPaths` in `lib/searchRewrite.ts`) where applicable. None require modifying either — only orchestrating them differently and, for C/D/E, adding a net-new external-search call (not yet built; see Provider Options doc).

---

## Mode A — Internal Only (baseline)

| Field | Value |
|---|---|
| Input | Original query |
| Trigger | None — always runs, this is the current production baseline behavior *minus* the LLM rewrite |
| Retrieval sources | Internal only (`scoreQueryTokens`, single pass) |
| Output structure | `InspRecord[]` / `NanoInspirationCardType[]` — existing shape, unchanged |
| Merge behavior | None (single source) |
| Expected benefit | Clean floor — measures what internal retrieval alone achieves without any rescue mechanism. Establishes the counterfactual against which B/C/D/E's *incremental* lift is measured. |
| Primary risk | None — this is strictly a measurement mode, not a candidate for shipping (production already has the LLM rewrite live). |
| Required instrumentation | Result count, latency, top-K relevance labels (offline) |
| Rollback behavior | N/A — read-only baseline, no user-facing change |
| Suitable for | Offline test only. Never staging/production (would be a regression vs. current prod, which already has LLM rewrite live). |

## Mode B — Rewrite Only (current production behavior)

| Field | Value |
|---|---|
| Input | Original query |
| Trigger | `initialThinCount < LOW_RESULT_THRESHOLD` (existing gate, `page.tsx:620-625`) |
| Retrieval sources | Internal only, across original + LLM-rewritten paths (`getMultiQueryPaths` → `flattenPaths` → re-run `scoreQueryTokens` per path) |
| Output structure | Existing shape, unchanged — this IS current production behavior, described for completeness of the matrix |
| Merge behavior | Existing same-source merge by record id, max-score-wins, multi-hit boost (`page.tsx:587-665`) |
| Expected benefit | Measures query-understanding improvement in isolation — this is the number to beat/match before adding external content, so any CTR/generate lift from Mode D/E can be attributed to the *external* leg specifically rather than re-crediting the already-shipped rewrite. |
| Primary risk | None new — already in production; the risk here is analytical (failing to isolate this mode's contribution before layering external results on top). |
| Required instrumentation | Same as A, plus `rewrite_triggered`, `rewrites_used`, `second_internal_count` |
| Rollback behavior | N/A — current production behavior |
| Suitable for | Offline test (as the comparison baseline) and already live in production. |

## Mode C — External Fallback Only

| Field | Value |
|---|---|
| Input | Original query |
| Trigger | `initial_internal_result_count` below the tested threshold (T0/T3/T5, per Trigger Experiment doc) |
| Retrieval sources | Internal (single pass, no rewrite) + external image search using the **original** (non-rewritten) query |
| Output structure | Internal `InspRecord[]` + new `ExternalSearchResult[]` (Deliverable 5), NOT yet merged into one ordered list — kept as two arrays for this mode's purpose |
| Merge behavior | Simple append: internal results first, external results appended below/after, per the Merge & Ranking Spec's Case-based policy |
| Expected benefit | Isolates content-gap recovery via external content WITHOUT the LLM rewrite's influence — answers "does raw content-gap-filling help, independent of query understanding?" |
| Primary risk | Original (unrewritten) query may be a poor search term for an external image engine if the internal matcher's failure was itself a *phrasing* problem — this mode cannot rescue phrasing issues, only content gaps. |
| Required instrumentation | `external_triggered`, `external_provider`, `external_count`, `merged_count`, latency, cost estimate, safety flags (see Instrumentation Plan) |
| Rollback behavior | Feature-flag off (`ENABLE_EXTERNAL_IMAGE_FALLBACK=false`) reverts to Mode A/B behavior instantly |
| Suitable for | Offline test only at MVP. Staging only after Core-80 shows positive signal. NOT production without a staged online test first. |

## Mode D — Parallel Hybrid (the manager's literal requirement)

| Field | Value |
|---|---|
| Input | Original query |
| Trigger | Same threshold-based gate as C |
| Retrieval sources | Internal (single pass) + in **parallel**: (a) LLM rewrite → second internal retrieval, AND (b) external image search using the **original** query, run concurrently (`Promise.allSettled`, not sequential) |
| Output structure | Internal `InspRecord[]` (original + rewrite-expanded, merged per existing Mode-B logic) + `ExternalSearchResult[]`, not yet subject to the full MVP safety wrapper (that's Mode E) |
| Merge behavior | Internal-first union (existing logic) + external append, WITHOUT the additional guardrails (caps, kill-switch, observability) that Mode E adds — this is the "raw" version of the manager's requirement, useful for isolating whether parallelism itself (vs. sequencing) matters for latency/relevance |
| Expected benefit | Directly tests the manager's literal proposal: "run LLM Rewriter and Google Image Search at the same time." Measures total latency savings from parallel execution vs. a hypothetical sequential version, and measures relevance when the external query is the ORIGINAL text (not rewritten) run alongside (not gated behind) the LLM path. |
| Primary risk | No safety wrapper yet in this mode — a slow or failing external call must still not block the internal-first render (needs `Promise.allSettled`, not `Promise.all`, to guarantee this even at this experimental stage). Without caps, a broad query could produce a large, unbounded external result set. |
| Required instrumentation | Everything from B + C, plus parallel-execution latency breakdown (internal-only latency vs. total wall-clock vs. slowest-leg latency) |
| Rollback behavior | Feature-flag off reverts to Mode B (current production) |
| Suitable for | Offline test (Core-80) only. Not staging/production as-is — Mode E is the production-safe version of this same idea. |

## Mode E — Controlled Hybrid MVP (production candidate)

| Field | Value |
|---|---|
| Input | Original query |
| Trigger | Same threshold-based gate, value TBD from Core-80 results |
| Retrieval sources | Same as Mode D (parallel internal-rewrite + external) |
| Output structure | Full normalized `HybridSearchResult` union (Deliverable 4/5 proposed contract) with `source_type`, `rank_before_merge`, `rank_after_merge`, `can_open`/`can_edit`/`can_generate` populated |
| Merge behavior | Full deterministic policy from Deliverable 9: internal-first ranking, external-result cap (position-dependent on internal count), explicit source labels, preserved external destination URLs, no internal-only actions on external results, dedup (canonical URL / normalized image URL / title+domain) |
| Expected benefit | This is the actual MVP candidate — the mode with production-grade safety behavior (timeout handling, failure fallback, caching, feature flags, observability, kill switch) layered on top of D's core logic. |
| Primary risk | Highest implementation complexity of the five; must not regress Mode B's already-shipped behavior when the external leg is flag-disabled. |
| Required instrumentation | Everything from D, plus: cache hit/miss, circuit-breaker state, per-provider error codes, `nano_external_inspiration_click`-style event (Instrumentation Plan), kill-switch trigger events |
| Rollback behavior | `EXTERNAL_SEARCH_KILL_SWITCH=true` disables the external leg only, instantly, independent of the other flags — internal + LLM-rewrite behavior (Mode B) continues unaffected. This is the production rollback mechanism. |
| Suitable for | Offline test → staging QA → small-traffic A/B → gradual rollout, per the Safe Rollout Plan (Deliverable 14). This is the ONLY mode this audit recommends progressing toward production, and only after all prior stages pass. |

---

## Cross-mode comparison summary

| Mode | LLM rewrite? | External search? | Parallel? | Safety wrapper? | Ships to prod? |
|---|---|---|---|---|---|
| A | No | No | — | — | No (measurement only) |
| B | Yes | No | — | N/A | **Already in production** |
| C | No | Yes | N/A (single external leg) | Minimal | No (offline/staging only) |
| D | Yes | Yes | Yes | No | No (offline only — proves the concept) |
| E | Yes | Yes | Yes | **Yes — full** | **Yes, candidate**, after staged validation |

Modes A and B are not "new" work — A is a diagnostic control and B is what already ships. C and D exist purely to decompose *why* E works (or doesn't) before committing engineering effort to E's full safety wrapper. This structure directly follows the brief's instruction to isolate the LLM-rewrite contribution from the external-search contribution before evaluating the combined (manager's requested) approach.
