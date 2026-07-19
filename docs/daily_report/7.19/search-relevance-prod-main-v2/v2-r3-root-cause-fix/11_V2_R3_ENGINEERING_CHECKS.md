# V2-R3 Stage: Engineering Checks

Date: 2026-07-19. Worktree: `/Users/baobaoli/Desktop/curify-frontend-search-v2-r3-2026-07-19`, branch `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`.

All checks below were run AFTER implementing mechanisms A and B (see `10_V2_R3_IMPLEMENTATION_SUMMARY.md`) and BEFORE the targeted evaluation in `08_V2_R3_TARGETED_GATE_RESULT.md`.

## 1. TypeScript

Command: `npx tsc --noEmit -p tsconfig.json`
Exit code: `0`
Duration: ~7.8s
Result: **PASS** — zero errors. (One intermediate run surfaced 7 errors in `lib/__tests__/relevanceScorer.test.ts` from the new `FieldHitInfo`/`ScoreContext` fields before the test file was updated; fixed by adding `coverageRatio`/`isMultiTermQuery`/`hasProtectedPhraseQuery` to the test fixtures, see below.)

## 2. Relevance scorer unit tests / search-related tests / rewrite-related tests / Rewrite Guard / multi-path / decomposition / phrase protection / subject binding

All of these are covered by the single existing `lib/__tests__/*.test.ts` suite (this repo does not split them into separate files/scripts) plus the new mechanism A/B tests added this stage.

Command: `npx vitest run --config vitest.unit.config.ts`
Exit code: `0`
Duration: 2.76s
Result: **PASS** — 143/143 tests across 8 files:

| File | Tests | Result |
|---|---:|---|
| `lib/__tests__/topic_cooccurrence.test.ts` | 10 | PASS |
| `lib/__tests__/topic_resolver.test.ts` | 20 | PASS |
| `lib/__tests__/intent_clusters.test.ts` | 12 | PASS |
| `lib/__tests__/relevanceScorer.test.ts` | 32 (was 14; +18 new mechanism A/B tests) | PASS |
| `lib/__tests__/search_generation_batch.test.ts` | 3 | PASS |
| `lib/__tests__/search_generation_plan.test.ts` | 8 | PASS |
| `lib/__tests__/search_metadata_scenarios.test.ts` | 30 | PASS |
| `lib/__tests__/thin_recall_queries.test.ts` | 28 | PASS |

`relevanceScorer.test.ts` breakdown relevant to the charter's specific check list:
- **Phrase protection** (`describe("searchPhraseProtection")`): 5 tests, unchanged, all pass.
- **Rewrite guard / subject binding** (`"cross-path agreement is NOT credited when the subject is missing"` / `"IS credited when the subject is present"`): unchanged, pass — confirms mechanism B's coverage gate composes correctly (these tests use `ctx({isMultiTermQuery:false})`, i.e. explicitly exercise the pre-existing single-term-shaped behavior untouched by mechanism B).
- **Multi-path** (`path_agreement` tests): unchanged, pass.
- **Mechanism A** (new `describe` block, 4 tests): sibling-own-evidence-scores-higher, unrelated-sibling-does-not-inherit, safe-fallback-non-catastrophic, `isOriginal` not read by `scoreRecord` (existence vs. rank decoupling).
- **Mechanism B** (new `describe` block, 11 tests): isolated-hit cap fires/doesn't fire, exact-phrase exemption, coverage-vs-isolated-hit comparison, subject-token-present-but-low-coverage loses credit, single-term queries fully bypass the gate, protected-phrase queries fully bypass the gate, CJK bigram-coverage shape (well-covered vs. poorly-covered), whole-token-outweighs-substring preserved.
- **Direction 1 floor invariant** (`describe("relevanceScorer.selectFinalCandidates")`, 5 tests, unchanged): never-drops-original, drops-low-scoring-non-original, keeps-good-non-original, never-zero guarantee, real-floor-when-enough-candidates. All untouched by this stage's design (confirmed by design doc §4.4) and all still pass.
- **Family saturation** (`describe("relevanceScorer.applyFamilySaturation")`, 3 tests, unchanged): all pass.

No test was deleted, skipped, or had its assertions weakened to pass.

## 3. Production build

Command: `npm run build` (`next build`)
Exit code: `0` (confirmed via presence of `.next/BUILD_ID` and full route table printed with no error banner)
Duration: ~61.6s wall clock (255.65s user CPU across build workers)
Result: **PASS** — `/[locale]/search` route built successfully (11.4 kB page bundle, 216 kB First Load JS), all 8660 static pages generated, no type or build errors.

## 4. No engineering-check failures required a design-scope fix this stage

The only failure encountered during implementation was the expected pre-existing-test-fixture TypeScript error (item 1), which was resolved by updating test fixtures to the new (additive) `FieldHitInfo`/`ScoreContext` shape — not a design or logic bug, and not a skip/weaken of any assertion.

**Engineering gate: PASS.**
