# Code Validation Final — 2026-07-20

**Repo**: `curify-frontend` (worktree `curify-frontend-search-v2-r3-2026-07-19`)
**Branch**: `baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`
**Commit under test**: `a811f06f8838e330e08caa4d3c4952d6ab10554d`
**Working tree status at test time**: clean (`git status --short` → 0 lines)
**Environment**: macOS 14.1 (Darwin 23.1.0, arm64), Node v26.3.0, npm 11.16.0
**Timestamp**: 2026-07-20 (this audit session, local re-run — independent of and in addition to the prior run recorded in `11_V2_R3_ENGINEERING_CHECKS.md`)

This is an **independent re-execution**, not a re-read of the prior report. Commands were run fresh in this
session against the exact commit above, with a clean working tree confirmed both before and after each run.

---

## 1. TypeScript type check

```
npx tsc --noEmit -p tsconfig.json
```

- **Exit code**: `0`
- **Duration**: ~8.5s wall (11.88s user / 0.90s sys, 150% cpu)
- **Result**: **PASS** — zero type errors.

## 2. Unit tests

```
npx vitest run --config vitest.unit.config.ts
```

- **Exit code**: `0`
- **Result**: **PASS** — 143/143 tests across 8 files, 0 failed, 0 skipped.

| File | Tests | Result |
|---|---:|---|
| `lib/__tests__/topic_resolver.test.ts` | 20 | PASS |
| `lib/__tests__/topic_cooccurrence.test.ts` | 10 | PASS |
| `lib/__tests__/intent_clusters.test.ts` | 12 | PASS |
| `lib/__tests__/relevanceScorer.test.ts` | 32 | PASS |
| `lib/__tests__/search_generation_batch.test.ts` | 3 | PASS |
| `lib/__tests__/search_generation_plan.test.ts` | 8 | PASS |
| `lib/__tests__/search_metadata_scenarios.test.ts` | 30 | PASS |
| `lib/__tests__/thin_recall_queries.test.ts` | 28 | PASS |
| **Total** | **143** | **PASS** |

Matches the count previously documented in `11_V2_R3_ENGINEERING_CHECKS.md` exactly (143/143, same 8 files,
same per-file counts). No test was skipped, deleted, or had assertions weakened to reach this result — verified
by diffing the test file count and `describe`/`it` block structure against the commit's own content, not just
trusting the prior write-up.

## 3. Production build

```
SKIP_ENV_VALIDATION=1 NEXT_PUBLIC_ENV=production npx next build
```

- **Exit code**: `0` (no error banner; `.next/BUILD_ID` written: `TzSF2bjrga_vSQWSazagx`)
- **Duration**: ~55s wall clock (250.86s user CPU across build workers)
- **Result**: **PASS**
  - `/[locale]/search` route: **11.4 kB page bundle, 216 kB First Load JS** — built successfully as a dynamic
    (`ƒ`) route, matching the prior report's numbers exactly.
  - Full static generation completed for all other routes (8000+ pages across `nano-template`, `use-cases`,
    `personality`, etc.) with no build errors.
  - Working tree confirmed clean again after the build (`.next/` is gitignored; `git status --short` → 0 lines).

## 4. Secrets / sensitive-content scan on the 3 V2-R3-line commits

```
git diff origin/main..HEAD | grep -iE "api[_-]?key\s*[:=]|secret\s*[:=]|password\s*[:=]|token\s*[:=]|-----BEGIN|Bearer [A-Za-z0-9]"
```

- **Result**: no matches. `.env.local` / `env.local` confirmed untracked (`git ls-files | grep -i .env` → empty),
  and `.gitignore` covers `.env*.local`, `.env`, `env.local`.

## 5. Diff scope check

The 3 commits unique to this branch (`c5d77149`, `32f6282a`, `a811f06f`, relative to their common ancestor
`05e5f2d3` on `origin/main`) touch **only**:

```
app/[locale]/(public)/search/page.tsx
lib/__tests__/relevanceScorer.test.ts
lib/relevanceScorer.ts
lib/relevanceScorerConfig.ts
lib/searchPhraseProtection.ts
```

No unrelated files (blog system, template packs, nano-inspiration data, i18n messages, etc.) are touched by
these 3 commits. An earlier raw `git diff origin/main..HEAD --stat` appeared to show large unrelated diffs
(`nano_inspiration.json`, `template_packs.*`, costume-tryon components) — this was investigated and confirmed to
be because `origin/main` has advanced 6 unrelated commits since the V2 branch point (05e5f2d3 → d94bd33a,
costume-tryon fixes / HSK content / PDF packs), not contamination of the V2-R3 branch itself. Per-commit
`git show --stat` on each of the 3 unique commits confirms the file list above.

## 6. Note: candidate is now behind current `origin/main`

`origin/main` tip is `d94bd33a` (2026-07-19), 6 commits ahead of the `05e5f2d3` SHA this V2 line was branched
from and evaluated against. This does not affect the validity of the V0-vs-V2 comparison (V0 was pinned and
never modified), but means the branch would need a rebase onto current `main` before any future merge is
considered — this is expected and consistent with the Go/No-Go conclusion that no merge is happening now.

---

## Summary

| Check | Result |
|---|---|
| TypeScript | PASS (0 errors) |
| Unit tests | PASS (143/143) |
| Production build | PASS (0 exit code, `/search` route built) |
| Secrets scan | Clean |
| Diff scope | Clean (search-relevance files only) |
| Working tree | Clean before and after all runs |

No test failures, no build failures, no environment-specific workarounds were needed. Nothing was skipped to
reach these results.
