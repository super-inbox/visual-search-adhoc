# Stage 1: Worktree and Branch Setup

Date: 2026-07-19

## Worktrees

| Role | Path | Branch / HEAD state | SHA |
|---|---|---|---|
| V0 baseline | `/Users/baobaoli/Desktop/curify-frontend-v0-baseline-2026-07-19` | detached HEAD (read-only) | `05e5f2d332778ac52c712dd2429f4a8f4e7c3673` |
| V2 development | `/Users/baobaoli/Desktop/curify-frontend-search-v2-2026-07-19` | `baobao/search-relevance-prod-main-v2-2026-07-19` | `05e5f2d332778ac52c712dd2429f4a8f4e7c3673` (initial) |

Both confirmed live via `git rev-parse HEAD` at the start of this session (2026-07-19). V2 initial SHA equals V0 SHA (same fork point, `origin/main` / verified live-deploy SHA).

## Initial diff verification (re-run this session)

Command: `diff -rq --exclude=.git --exclude=node_modules <V0 worktree> <V2 worktree>`

Output: **empty** (no differences reported) — confirms V0 and V2 worktrees are byte-identical at session start, before any V2 code changes.

Note: `.env.local` was copied into both worktrees *after* this diff was run (both worktrees received an identical copy from the same source file, so this does not break the byte-identical guarantee — both sides now hold the same `.env.local` content, and `.env.local` is git-ignored in both, so it does not appear in either worktree's git status).

## Original repository state (NOT touched)

`/Users/baobaoli/Desktop/curify-frontend`, branch `baobao/search-relevance-phrase-alias-2026-07-09` (old Candidate / V1, frozen per design doc), HEAD SHA `c062e618bce4044bedf718aadf59ff69f0999344`.

`git status --short` shows **26 entries** (re-verified this session), matching the count recorded in the pre-existing authoritative docs:

Modified (21):
```
app/[locale]/(public)/blog/[slug]/components/GenericBlogContent.tsx
app/[locale]/(public)/blog/[slug]/page.tsx
app/[locale]/(public)/search/page.tsx
lib/__tests__/search_metadata_scenarios.test.ts
lib/query_phrase_aliases.ts
lib/searchRewrite.ts
lib/zh_normalize.ts
messages/de/blog.json
messages/en/blog.json
messages/es/blog.json
messages/fr/blog.json
messages/hi/blog.json
messages/ja/blog.json
messages/ko/blog.json
messages/ru/blog.json
messages/tr/blog.json
messages/zh/blog.json
next.config.ts
package-lock.json
package.json
scripts/eval_search.cjs
```

Untracked (5):
```
lib/__tests__/searchRewrite.test.ts
lib/__tests__/searchTokens.test.ts
lib/__tests__/stage6_dictionary_hybrid.test.ts
lib/cjk_tokenizer.ts
lib/searchTokens.ts
```

21 + 5 = 26. Confirmed.

**Was the original repository touched during this task: NO.** No `git` write commands, no `checkout`, no `stash`, no `reset`, no `clean`, no file edits were run against `/Users/baobaoli/Desktop/curify-frontend`. It was only read via `git status`/`git rev-parse` for verification.

## Environment

- Node: `v26.3.0` (verified via `node -v` in both worktrees' shell context)
- npm: `11.16.0`
- `.env.local` copied (content copy, not moved, not modified) from `/Users/baobaoli/Desktop/curify-frontend/.env.local` into both worktrees, `chmod 600`. Actual values were never printed to any log, report, or terminal output — only variable names and existence/liveness were recorded (see `00_PRODUCTION_BASELINE_MANIFEST.json`).
- Live LLM sanity check (this session, values never printed): `OPENAI_API_KEY` → live 200 response from `gpt-4o-mini` via `/v1/chat/completions`. `GEMINI_API_KEY` → live 200 response from `/v1beta/models` (key authenticates; model list retrieved). No `BLOCKED_LLM_EVALUATION_ENVIRONMENT`.
