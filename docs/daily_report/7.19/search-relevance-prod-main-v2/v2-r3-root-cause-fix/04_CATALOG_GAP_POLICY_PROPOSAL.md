# V2-R3 Stage: Catalog-Gap Policy Proposal (offline / advisory only)

Date: 2026-07-19. This document is **advisory** — per charter §7.C, this stage makes **no production zero-result policy change**. It exists to draw a clear line between what V2-R3's ranking/scoring fix can and cannot address, so the fix design (`05_V2_R3_MINIMAL_FIX_DESIGN.md`) doesn't overreach into content-supply territory.

## 1. The 5 confirmed catalog-gap cases

`盲盒` (blind box), `泰迪熊` (teddy bear), `练习册` (workbook), `笔袋` (pencil case), `算盘` (abacus) — all 5 have `relaxed_above_floor=0` in the live V2-R2 trace: **every single candidate the catalog can produce for that query scores below the quality floor.** `泰迪熊` is the clearest instance: V0's top-5 and V2-R1's top-5 are the literal same 4 records, only reordered.

## 2. What ranking CAN fix

- **Reordering among already-available candidates** when at least one is genuinely relevant (not the case here, but true for e.g. `figure`, where the relevant `chinese figure fengshenbang` content exists in the pool but loses on score to over-promoted siblings — see `05_V2_R3_MINIMAL_FIX_DESIGN.md` mechanism A).
- **Demoting genuinely irrelevant candidates below genuinely relevant ones** when both exist in the pool (mechanisms A and B).
- **Preventing one template family from crowding out a smaller but more relevant family** (`applyFamilySaturation`, already implemented, unchanged this round).

## 3. What ranking CANNOT fix

- **A catalog with zero relevant content for the query, period.** No scoring formula, threshold, or coverage rule can promote a candidate that does not exist. This is true by construction for all 5 gap cases: 100% of the pool is below floor, so ranking is choosing among "least bad" options, not "most relevant" ones.
- Tightening the floor (`MIN_SCORE_WHEN_ORIGINAL_EMPTY` or `MIN_KEPT_WHEN_ORIGINAL_EMPTY`) does not create better candidates — it can only choose to show fewer (or zero) results instead of the current low-quality padding, trading one failure mode (irrelevant results) for another (empty page), which the charter's zero-result gate explicitly forbids trading into.

## 4. Options considered (offline comparison only — none implemented this round)

| Option | Effect | Ranking-solvable? | V2-R3 in-scope? |
|---|---|---|---|
| 1. Keep never-zero fill (current behavior) | Always shows 5 (or the full pool if smaller) even when all below floor | N/A — this IS the current policy | Kept unchanged |
| 2. Lower the never-zero count (e.g. `MIN_KEPT_WHEN_ORIGINAL_EMPTY` from 5 to 2-3) | Fewer low-confidence results shown instead of padding to 5 | No — doesn't improve relevance, only changes how much irrelevant content is shown | **Out of scope** — this is exactly the kind of "trade zero/low-result rate for a cosmetic change" the charter's Go/No-Go gates (#8-9) prohibit doing without full-326 evidence, which this round is barred from collecting |
| 3. Show a low-confidence UI hint ("results may not closely match your search") | No ranking change; sets user expectation | No — UX/product decision | **Out of scope** — no production UI code changes permitted this round |
| 4. Return fewer results instead of forcing exactly 5 | Same relevance, smaller page | No — doesn't improve relevance, only display count | **Out of scope** — is itself a "zero/low-result rate" tradeoff the charter says not to make speculatively |
| 5. Add internal content for these 5 specific query concepts | Genuinely fixes the gap | N/A — content/catalog work, not code | **Out of scope for V2-R3** (not a code task at all) — flagged for content team as a candidate backlog item |
| 6. Future V3 Hybrid Search (embeddings/semantic retrieval) | Could surface semantically-related content the current literal-token matcher misses entirely | N/A — architecturally different retrieval, large scope | **Out of scope for V2-R3** — explicitly a future-round consideration, not a minimal fix |

## 5. Recommendation for V2-R3

**No catalog-gap code change in V2-R3.** The 5 `CATALOG_GAP_NEVER_ZERO_FLOOR` cases are correctly left as `NOT_FIXABLE_BY_A_RANKING_CHANGE_THIS_ROUND` in `02_V2_R3_REGRESSION_TRACE.csv`. They are included in the holdout set (3 of them: `练习册`, `笔袋`, `算盘`) and calibration set (2: `盲盒`, `泰迪熊`) purely as a **regression check** — the Go/No-Go gate requires confirming the mechanism-A/B fix does not accidentally worsen these (e.g., does not somehow reduce the never-zero floor's effective pool below 5, or turn a 4-candidate near-zero case into an actual zero-result case) — not as cases the fix is expected to improve.

## 6. Explicit boundary statement (for the Go/No-Go reviewer)

- Ranking problem (in scope, addressed by mechanisms A/B in `05_V2_R3_MINIMAL_FIX_DESIGN.md`): a relevant candidate exists in the pool but is outranked by an irrelevant one.
- Catalog/content problem (out of scope, this document only): no relevant candidate exists in the pool at all.
- The 50-query regression set contains **zero** ambiguous cases between these two categories — all 5 catalog-gap rows have `relaxed_above_floor=0`, an unambiguous, code-derived signal (not a judgment call) that no candidate cleared even the lowest quality bar.
