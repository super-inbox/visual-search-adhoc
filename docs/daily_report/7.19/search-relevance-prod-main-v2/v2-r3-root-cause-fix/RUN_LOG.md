# V2-R3 Run Log

Date: 2026-07-19.

1. **Pre-flight state check**: verified V2-R3 worktree on branch `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19` at SHA `32f6282a240edfa87edae5a0ba5308aecf462466`, clean. Verified V0/V2-R1/V2-R2 worktrees clean at their expected frozen SHAs. Verified original `curify-frontend` workspace has its own pre-existing uncommitted changes (26 files, untouched by this stage). Verified artifact backup zip unchanged (SHA-256 identical before/after).
2. **Read design files**: `01_V2_R3_ROOT_CAUSE_REVALIDATION.md`, `02_V2_R3_REGRESSION_TRACE.csv`, `03_V2_R3_CASE_SPLIT.csv`, `04_CATALOG_GAP_POLICY_PROPOSAL.md`, `05_V2_R3_MINIMAL_FIX_DESIGN.md`, `06_V2_R3_DESIGN_MANIFEST.json` in full.
3. **Read current code**: `lib/relevanceScorer.ts`, `lib/relevanceScorerConfig.ts`, `lib/searchPhraseProtection.ts`, `lib/__tests__/relevanceScorer.test.ts`, and the relevant sections of `app/[locale]/(public)/search/page.tsx` (tokenizer, `deriveFieldHits`, `scoreQueryTokens`'s template-promotion branch, the final candidate-selection pipeline).
4. **Environment setup**: `cp .env.local` from the V2-R1 worktree into V2-R3 (read-only copy, does not modify V2-R1). `PUPPETEER_SKIP_DOWNLOAD=true npm ci` (plain `npm ci` failed on an unrelated Chrome-headless-shell download step; skipping it is safe since no browser automation is used by this stage's checks).
5. **Implemented mechanism A** (per-inspiration re-scoring for template-promoted siblings) in `page.tsx`.
6. **Implemented mechanism B** (required multi-term coverage + isolated-hit score cap) in `lib/relevanceScorer.ts` / `lib/relevanceScorerConfig.ts`, wired from `page.tsx`.
7. **Updated tests**: extended `lib/__tests__/relevanceScorer.test.ts` fixtures for the new type fields; added 18 new tests (4 mechanism A, 14 mechanism B).
8. **Engineering checks** (see `11_V2_R3_ENGINEERING_CHECKS.md` for full detail): TypeScript (`npx tsc --noEmit`) — PASS after fixing the test-fixture types; unit tests (`npx vitest run --config vitest.unit.config.ts`) — 143/143 PASS; production build (`npm run build`) — PASS.
9. **Started 3 live servers** (`next start`, pre-existing production builds for V0/V2-R1, fresh build for V2-R3) on ports 4501/4502/4503.
10. **Ran the targeted evaluation**: 63 queries (calibration + holdout + previous_improvement_protection + rewrite_invariant, `functional_protection` covered by the unit suite instead) × 3 servers, using `scripts/collector.mjs` + `scripts/judge.mjs` (rubric-v1.1, gpt-4o-mini). First pass hit 49 transient `fetch failed` errors (documented environment flakiness); a retry pass with backoff resolved 46 of them, leaving 3 legitimate `NO_JUDGEABLE_RESULTS` outcomes (confirmed not call failures by inspecting raw content). Corrected 4 CJK protection queries whose case-split CSV text accidentally included an English parenthetical gloss.
11. **Aggregated results** into `07_V0_R1_R3_TARGETED_COMPARISON.csv` and analyzed against all 20 gate conditions (see `08_V2_R3_TARGETED_GATE_RESULT.md`).
12. **Gate result: all 20 conditions pass.** Zero parameter-adjustment rounds beyond the initial design-derived defaults were needed (calibration showed net improvement on the first attempt).
13. **Stopped the 3 local `next start` servers.**
14. **Created one local commit** (see below) containing exactly the 4 changed files. Report directory, raw eval output, `.env.local`, caches, and logs are excluded (report lives in `visual-search-adhoc`, a separate repo from `curify-frontend`, so no explicit exclusion was even needed).

## Commit

SHA `a811f06f8838e330e08caa4d3c4952d6ab10554d` (parent `32f6282a240edfa87edae5a0ba5308aecf462466`), branch `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`. Exactly 4 files changed (533 insertions, 72 deletions): `app/[locale]/(public)/search/page.tsx`, `lib/relevanceScorer.ts`, `lib/relevanceScorerConfig.ts`, `lib/__tests__/relevanceScorer.test.ts`. Not pushed.

## Final status

`FINAL_STATUS: V2_R3_TARGETED_FIX_COMPLETE`
