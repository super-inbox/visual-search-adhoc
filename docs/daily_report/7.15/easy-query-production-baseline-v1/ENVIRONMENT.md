# ENVIRONMENT.md — Phase 0 Environment Snapshot

Read-only environment check performed before any collection activity. No code, branches, or files were modified as part of this phase.

| Field | Value |
|---|---|
| Timestamp of check | 2026-07-15 16:27:37 CST (see `date` output below) |
| Current working directory (at task start) | `/Users/baobaoli/Desktop/visual-search-adhoc` |
| Shell | `/bin/zsh` |
| User | `baobaoli` |
| macOS version | macOS 14.1 (Build 23B2073) |
| CPU architecture | `arm64` |
| Node.js version | `v26.3.0` |
| npm version | `11.16.0` |
| pnpm version | not installed (`command not found: pnpm`) |
| yarn version | not installed (`command not found: yarn`) |
| Python version | `Python 3.11.7` |
| Git version | `git version 2.44.0` |
| Timezone | `CST +0800` |
| Current time | `Wed Jul 15 16:27:37 CST 2026` |

## Git state — `/Users/baobaoli/Desktop/visual-search-adhoc` (evaluation repo)

- Is a Git repository: `true`
- Repository root: `/Users/baobaoli/Desktop/visual-search-adhoc`
- Branch: `main`
- HEAD commit: `de1cda483a499e4cc3cf00230cc503cb2969fc7b`
- Remote: `origin https://github.com/super-inbox/visual-search-adhoc.git`
- Staged/modified/untracked files at task start: yes — pre-existing, unrelated to this task (mostly `.DS_Store` churn and prior daily-report work-in-progress under `docs/daily_report/7.11`, `7.12`, `7.5`, plus `node_modules/` directories left over from earlier ad-hoc script runs, and `scripts/curify-search-collect-stage7/*.log`). None of these were created, modified, or deleted by this task. Full pre-existing `git status` snapshot is in the top-level task transcript; this task only **adds** new files under `docs/daily_report/7.15/easy-query-production-baseline-v1/`.

## Output directory versioning

Target output directory `docs/daily_report/7.15/easy-query-production-baseline-v1` did not exist and `docs/daily_report/7.15/` did not exist at all before this task. No collision with `v2`, `v3`, etc. was necessary.

**Final actual output directory: `/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1`**

## Product repository clone directories present on Desktop (read-only inspection, not created by this task)

These pre-existing clones were inspected read-only to establish which code is "local optimized" vs. authoritative production, per task rules. They were **not** modified.

- `/Users/baobaoli/Desktop/curify-frontend` — existing dev clone, remote `https://github.com/super-inbox/curify-frontend.git`, branch `baobao/search-relevance-phrase-alias-2026-07-09`, HEAD `c062e618bce4044bedf718aadf59ff69f0999344`, with extensive **uncommitted local modifications** to search-relevant files (`lib/searchRewrite.ts`, `lib/query_phrase_aliases.ts`, `lib/zh_normalize.ts`, `app/[locale]/(public)/search/page.tsx`, etc.). This is the local search-optimization development branch and was excluded from use as the Baseline test target per task instructions.
- `/Users/baobaoli/Desktop/curify-blog-fix` — unrelated dev clone, branch `baobao/multi-intent-topic-cooccurrence`, not used.

## New isolated clone for this task

Per task instructions, a fresh, independent clone was made rather than reusing the above:

- Path: `/Users/baobaoli/Desktop/curify-production-baseline-2026-07-15`
- Source: `https://github.com/super-inbox/curify-frontend.git` (full clone, default branch `main`)
- Purpose: code audit / version confirmation only — **not** used to run search queries locally as a substitute for the live production website.

## Rules honored in this phase

- No `git pull`, `checkout`, or history-modifying command was run in `/Users/baobaoli/Desktop/visual-search-adhoc`.
- No `git pull`, `checkout`, or history-modifying command was run in `/Users/baobaoli/Desktop/curify-frontend` (the existing dev clone) — it was only inspected with `git remote -v`, `git branch --show-current`, `git rev-parse HEAD`, `git status --porcelain`.
- The new clone at `/Users/baobaoli/Desktop/curify-production-baseline-2026-07-15` is additive (new directory) and does not touch either existing clone.
