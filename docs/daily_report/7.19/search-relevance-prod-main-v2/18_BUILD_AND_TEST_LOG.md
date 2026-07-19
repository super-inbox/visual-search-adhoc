# Stage 11: Build and Test Log

Date: 2026-07-19. All commands run directly (no `npm test`/`npm run typecheck` scripts exist in `package.json` — confirmed in Stage 2 audit).

## TypeScript

```
cd /Users/baobaoli/Desktop/curify-frontend-search-v2-2026-07-19 && npx tsc --noEmit
```
Result: **0 errors** (empty output), re-run after every implementation change this session (7+ times), always clean.

## Vitest unit suite

```
cd /Users/baobaoli/Desktop/curify-frontend-search-v2-2026-07-19 && npx vitest run --config vitest.unit.config.ts
```
Result: **128/128 tests passed** (7 pre-existing files, 111 tests, unmodified and all still passing; 1 new file `lib/__tests__/relevanceScorer.test.ts`, 17 new tests covering the scorer/phrase-protection modules).

V0 baseline for comparison: same 7 pre-existing files, 111/111 passing (V0 has no scorer module, so no equivalent new-test count).

## Production build

```
cd /Users/baobaoli/Desktop/curify-frontend-search-v2-2026-07-19 && PUPPETEER_SKIP_DOWNLOAD=true npm run build
```
Result: **succeeds**, `next build` completes with no errors. (`PUPPETEER_SKIP_DOWNLOAD=true` works around a broken local Puppeteer browser-cache download unrelated to this app's own code — Puppeteer is a transitive devDependency of something else in the repo, not used by the search path; V0 build required the same workaround and also succeeds.)

V0 baseline: also builds cleanly with the same flag.

## Live server behavioral verification (this session, both V0 port 4501 and V2 port 4502, real `next start` production builds, real OpenAI calls)

| Behavior | How verified | Result |
|---|---|---|
| LLM rewriter actually triggers | Real thin queries (烘焙包装, coffee cup, black friday banner, etc.) hit against running servers; `usedRewrites` non-empty, `pathsUsed > 1` observed in real RSC response payloads | PASS on both V0 and V2 |
| Rewrite Guard (Path A/B decision, garbage/bot pre-filter) | Code-audit confirmed present and unmodified in V2 (`looksLikeGarbageQuery`, `BOT_UA_REGEX` untouched); V2 diff only touches the merge/scoring section, not these functions | PASS (unmodified, still present) |
| multi-path retrieval actually runs and merges | Confirmed via `pathsUsed` values of 4-7 on real thin queries on both V0 and V2, and via source-path tracking added in V2 (`sourcePathsById`, observed via temporary debug trace during implementation, e.g. `["original","rewrite:Black Friday sale poster","decomposition:banner"]`) | PASS on both V0 and V2 |
| decomposition slots contribute | Same trace showed `decomposition:<slot>` labeled paths independently contributing merged candidates | PASS on both V0 and V2 |
| L2 hierarchical content | UNKNOWN per Stage 2 audit (no code artifact identified; the source design doc itself flags this as unresolved). V2 does not touch any code that could plausibly be "L2" (no changes outside `page.tsx`'s merge/scoring section and new `lib/relevanceScorer*`/`lib/searchPhraseProtection.ts` files) | UNKNOWN (honestly reported, not guessed; scope discipline minimizes regression risk even though it cannot be positively verified) |
| Multi-paragraph display | Same as above | UNKNOWN |
| Search result cards render | `ExampleImagesGrid` component untouched; verified via live page fetch showing populated `inspirations` arrays rendering correctly in RSC payload | PASS |
| Click / Generate / Remix | `GenerableTemplatesSection.tsx`, `NanoTemplateDetailClient.tsx`, `services/searchGenerationBatch.ts` — all untouched by any V2 commit (`git diff` shows only `page.tsx` + 3 new `lib/` files changed) | PASS (unmodified) |
| Empty state | Confirmed live: queries with genuinely no catalog content (e.g. 课程表 pre-fix) render the empty-state path; V2's never-zero safety net (`selectFinalCandidates`) is specifically designed to avoid INCREASING the zero-result rate relative to V0, not to eliminate the empty state entirely | PASS (behavior preserved, not regressed) |
| Loading state | Component-internal to `GenerableTemplatesSection.tsx`, untouched | PASS (unmodified) |
| Error / timeout fallback | `lib/searchRewrite.ts` catch blocks (return safe empty on any failure) untouched in V2 | PASS (unmodified) |

## Git diff scope confirmation

```
cd /Users/baobaoli/Desktop/curify-frontend-search-v2-2026-07-19 && git diff 05e5f2d3 HEAD --stat
```
Only 5 files touched across both commits: `app/[locale]/(public)/search/page.tsx` (modified), `lib/relevanceScorer.ts` (new), `lib/relevanceScorerConfig.ts` (new), `lib/searchPhraseProtection.ts` (new), `lib/__tests__/relevanceScorer.test.ts` (new). No other file in the repository was touched — this is the strongest evidence that LLM rewriter, Rewrite Guard, multi-path, decomposition, and all UI/interaction components (cards, click, Generate, Remix, empty/loading/error states) were not deleted, disabled, or short-circuited, since their source files are byte-identical to V0.
