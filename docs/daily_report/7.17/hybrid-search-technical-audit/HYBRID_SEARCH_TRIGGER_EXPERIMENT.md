# Hybrid Search — Trigger Experiment Design

## Existing precedent

Today, exactly one threshold gates the only existing "thin result" behavior (the LLM rewrite): `LOW_RESULT_THRESHOLD = 5`, duplicated independently in `app/[locale]/(public)/search/page.tsx:47` (server) and `app/[locale]/(public)/search/SearchResultsClient.tsx:204` (client). It gates on `initialThinCount` server-side (strict-matched inspirations + i18n-matched templates, computed **before** any rewrite) and on `totalResults` client-side (grid + templates + gallery, computed **after** rewrite). These are two different counts measuring related but not identical things — worth being precise about which one a hybrid trigger reuses.

**This audit does not assume `5` is correct for the new feature.** It is reused as the *existing* threshold for the LLM path; the hybrid trigger threshold must be independently tested (per manager's Session-3 brief: "treat it as an experiment variable, not a lock").

## Required policies (as specified)

| Policy | Definition | Rationale for testing |
|---|---|---|
| **T0** | `initial_internal_result_count == 0` | Most conservative — only fires on true content gaps. Lowest external-result volume, lowest cost, lowest risk of cannibalizing internal clicks. |
| **T3** | `initial_internal_result_count < 3` | Matches the *pre-2026-06-26* LOW_RESULT_THRESHOLD value (the code comment at page.tsx:44 states it was "raised from 3 → 5" for the rewrite gate on that date) — worth testing whether the original, tighter threshold was actually right for an external-fallback decision even if 5 is right for the LLM-rewrite decision. |
| **T5** | `initial_internal_result_count < 5` | Matches today's `LOW_RESULT_THRESHOLD` exactly — reuses the existing gate value, simplest to reason about alongside the LLM rewrite trigger, but not proven optimal for THIS decision. |

## Discussed but not required for MVP

- **Top-result relevance/confidence trigger** — would require the relevance-labeling work that `docs/eval-framework-visual-search-benchmark-2026-06-14.md` Extension B explicitly says does not exist yet ("Curify has zero pairwise relevance labels," line 190). Not buildable today without that prerequisite.
- **Poor ranking despite high count** — same blocker; requires NDCG or a graded relevance signal, which the doc confirms doesn't exist.
- **Repeated reformulation trigger** (user re-searches similar queries in one session) — technically buildable from `session_id` + query history, but no session-level query history is currently tracked beyond individual search events; would be new instrumentation, not a repurposing of existing state.
- **Query category-specific trigger** (e.g., only trigger for "creative reference" categories, not "brand/business" categories) — plausible and possibly valuable (an ecommerce/brand query might not want inspiration from a random blog), but requires the intent-cluster taxonomy (`lib/intent_taxonomy.ts`) to be extended with an "external-appropriate" flag that doesn't exist today.

**Recommendation:** defer all four to a post-MVP iteration once count-based triggers (T0/T3/T5) have offline + online data. Count-based triggers are cheap to implement (pure arithmetic on an already-computed number) and directly testable with the Core-80 offline plan (Deliverable 11); the discussed-but-deferred triggers all require new infrastructure this audit did not find evidence of.

## First-MVP candidate (as specified by the brief)

```
0 results:    always trigger
1-4 results:  trigger
5+ results:   do not trigger
```
This is mathematically identical to **T5** (`< 5`). Treating it as the first candidate to test does not mean adopting `5` permanently — see below.

## Known risks with any count-based trigger (documented per brief, not resolved here)

1. **Count can be high while results are irrelevant.** The current internal scorer's precision-first design (`hasStrict` gate, page.tsx:704 — if ANY strict match exists, ALL relaxed matches are dropped) means a query returning "5 strict matches" could still be a poor experience if those 5 are marginally relevant. A count-only trigger cannot see this; it would suppress the external fallback exactly when it might most help. This is a structural limitation of every count-based policy, not just the specific threshold chosen.
2. **Count can be low while results are highly relevant.** A tightly-scoped query (e.g., "cat breed chart") might return exactly 2 *excellent* matches. Triggering external fallback here adds noise/dilution risk for no real benefit — the trigger would fire on a query that didn't need rescuing.
3. **Broad queries may create too many external results.** A one-word query like "flowers" that happens to score below threshold (e.g., due to strict/relaxed gating quirks) could pull in an enormous, largely-redundant external image set — needs the merge policy's external-result cap (Deliverable 9) to bound this, not the trigger alone.
4. **LLM rewrite may drift from user intent** — if the hybrid design sends the *rewritten* query to the external provider (per Extension C's stated intent) rather than the original, a bad rewrite compounds into a bad external result set. This argues for testing both "external search on original query" (Mode C) and "external search on rewritten query" (folded into Mode D/E) independently — see Mode Matrix.
5. **Google results may be visually relevant but commercially unusable** — e.g., copyrighted stock photography, or content styles Curify's generation engine can't actually reproduce, making the "Make with Curify" CTA a dead end even when the visual match is good.
6. **External results may increase exit rate** — the core CTR-vs-Generate tension the manager explicitly flagged; see Online Metrics doc.

## Explicit non-lock statement

Per the brief: none of T0/T3/T5/the-brief's-candidate is being locked as a final production value in this document. The Core-80 offline experiment (Deliverable 11) is designed to produce comparative data across these thresholds (and the five modes) before any threshold is chosen for a staged online test.
