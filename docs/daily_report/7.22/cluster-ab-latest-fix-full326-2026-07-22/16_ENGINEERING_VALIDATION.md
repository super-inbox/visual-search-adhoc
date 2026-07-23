# Engineering Validation — commit 0e794cd9

All commands run in `/Users/baobaoli/Desktop/curify-frontend-search-v2-r3-2026-07-19` at HEAD `0e794cd9` before any
benchmark query was executed. Package manager: npm 11.16.0 (package-lock.json present, no pnpm/yarn lockfile). Node
v26.3.0.

## 1. Unit tests — subject detection + relevance scorer
**Command:**
```
npx vitest run --config vitest.unit.config.ts lib/__tests__/relevanceScorer.test.ts lib/__tests__/searchSubject.test.ts
```
- Start: 2026-07-22 15:17:50 CST
- End: 2026-07-22 15:17:52 CST
- Exit code: **0**
- Result: **53/53 passed** (16 in `searchSubject.test.ts` — the new Fix-A tests; 37 in `relevanceScorer.test.ts`)
- No failures, no skipped tests.

## 2. TypeScript validation
**Command:**
```
npx tsc --noEmit
```
- Start: 2026-07-22 15:17:54 CST
- End: 2026-07-22 15:17:57 CST
- Exit code: **0**
- Result: clean, 0 errors.

## 3. Production build
**Command:**
```
npm run build
```
- Start: 2026-07-22 15:18:06 CST
- End: 2026-07-22 15:19:07 CST (~61s wall clock; "Compiled successfully in 8.0s" reported within that window, remaining
  time is static-page generation/prerendering across the site, not related to search code)
- Exit code: **0**
- Result: build succeeded. `.next/BUILD_ID` = `f-pp5Q3gQdRK6AuBomZkF-`, reused unmodified for the candidate server
  started later in this run (port 4522).
- **Known, pre-existing, non-blocking warning** (unrelated to search): repeated `Error: MISSING_MESSAGE:
  blog.qaBotToTask (en)` lines during static generation of blog pages — an i18n content gap on an unrelated blog
  post, not a search-relevance or build-breaking issue. Exit code remained 0; documented here per the charter's
  "warnings may be documented but not hidden" instruction, not silently discarded.

## Post-build worktree check
`git status --short` immediately after the build: **empty** (clean) — the build writes only to the gitignored
`.next/` directory, no source files were touched.

## Gate result
**ENGINEERING_GATE_PASS** — all three checks (tests, typecheck, build) passed with exit code 0 before the 326-query
benchmark was started.
