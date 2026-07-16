# Hybrid Search — Final Audit Log

Audit date: 2026-07-17
Auditor: Claude Code (Session 3 — read-only architecture audit and experiment design)
Repository audited: `/Users/baobaoli/Desktop/curify-frontend-hybrid-audit`
Remote: `https://github.com/super-inbox/curify-frontend.git`
Branch: `main`
Commit at start and end of audit: `5a59c4beba7856136396d8d0d249d5355c85322f` (unchanged — see validation below)
Shallow clone: yes (`git rev-parse --is-shallow-repository` → `true`)
Output location: `/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.17/hybrid-search-technical-audit/` (new, empty directory at start — no prior report overwritten, so no `-v2` suffix was needed)

---

## Methodology

1. Confirmed repository identity, branch, commit, shallow-clone status, and clean working tree via `git status`/`git rev-parse` before any exploration.
2. Dispatched one read-only `Explore` subagent to build a first-pass evidence inventory across 11 required investigation areas (entry points, normalization, retrieval, result counting, LLM rewrite, merge/dedup/rank, data contracts, UI cards, tracking, external references, directory structure).
3. Independently re-verified the subagent's highest-leverage claims by directly reading the cited source files in full: `app/[locale]/(public)/search/page.tsx` (key line ranges), `app/[locale]/(public)/search/SearchResultsClient.tsx`, `lib/searchRewrite.ts` (full file), `services/useTracking.ts` (full file), and `docs/eval-framework-visual-search-benchmark-2026-06-14.md` (full file, discovered to contain "Extension C," an existing unshipped design proposal for this exact feature).
4. Ran targeted `rg`/`grep` sweeps to confirm negative findings (absence of `search_id`, absence of any Google Custom Search / SERP API integration, absence of `.env.example`) rather than inferring absence from silence in the subagent report alone.
5. Wrote all 18 required deliverables to the specified output directory, outside the audited repository.
6. Re-confirmed repository state (git status, git diff, HEAD) after all writes.

## Validation checklist (per task §18)

| Check | Result |
|---|---|
| Repository working tree remains unchanged | **Confirmed** — `git status` clean, `git diff --stat` empty, both checked after all report writes |
| No source file was modified | **Confirmed** — all writes went to `/Users/baobaoli/Desktop/visual-search-adhoc/...`, none to the audited repo |
| No dependency was installed | **Confirmed** — no `npm`/`pnpm`/`yarn`/`bun install` command was run at any point |
| No server was started | **Confirmed** — no `npm run dev`/`next dev`/`next start` was run; all inspection was static (Read/Grep/Bash read-only commands) |
| No external API was called | **Confirmed** — no network call to Google, Bing, or any SERP/image-search provider was made |
| No OpenAI request was made | **Confirmed** — `lib/searchRewrite.ts` and `lib/searchTemplateMatch.ts` were read as static files, never executed or invoked |
| No Google request was made | **Confirmed** — same as above; the `@google/genai` dependency was identified via `package.json`/grep only, never invoked |
| No API key or `.env` value was read or copied | **Confirmed** — `.env`/`.env.local` files were never opened; confirmed no `.env.example` even exists in this repo (`find` returned no matches) |
| No commit, push, or deployment occurred | **Confirmed** — only `git status`/`git rev-parse`/`git log`/`git diff --stat` (all read-only) were run; no `git add`/`commit`/`push` |
| All required output files exist | **Confirmed** — see manifest (`AUDIT_MANIFEST.json`) for the full list with hashes |
| All CSV and JSON files parse | **Confirmed** — `HYBRID_SEARCH_CODE_ENTRYPOINTS.csv` (33 rows × 8 cols) and `HYBRID_SEARCH_RISK_REGISTER.csv` (23 rows × 9 cols) validated with Python's `csv` module; `AUDIT_MANIFEST.json` validated as parseable JSON at write time |
| Repository commit recorded | **Confirmed** — `5a59c4beba7856136396d8d0d249d5355c85322f`, see also `AUDIT_MANIFEST.json` |
| Output file hashes recorded | **Confirmed** — SHA-256 for all files, see `AUDIT_MANIFEST.json` |
| Missing architecture evidence recorded | See "Explicit UNKNOWNs" below |
| Verified facts separated from recommendations/assumptions | Done throughout — every deliverable explicitly marks recommendations, proposed (unimplemented) designs, and UNKNOWN items distinctly from verified file:line citations |
| No interaction with the concurrent 326-query benchmark session | **Confirmed** — that process runs in a different working tree and was never referenced, inspected, or touched by any command in this audit |

## Explicit UNKNOWNs / missing evidence (consolidated from all deliverables)

- `lib/nano_page_data.ts` `buildNanoFeedCards` and `lib/nano_utils.ts` `nanoRegistry` internals — used/imported but not read line-by-line.
- `NanoTemplateDetailClient.tsx` full action set beyond default-export confirmation — not read in full.
- `scripts/eval_search.cjs` / `scripts/configs/search_eval_set.json` — referenced via documentation, not opened directly; their exact bucket definitions and compatibility with the proposed Core-80 schema need confirmation before reuse.
- `packs/` directory's relationship (if any) to search taxonomy generation — flagged UNKNOWN by the exploration subagent, not independently resolved.
- Whether `OPENAI_API_KEY` or any future Google Search key is actually set in the deployed Vercel environment — cannot be verified from a local shallow clone, and no `.env*` file exists locally to check even if it were permitted.
- Real external-provider latency, response-field completeness (title/domain/safe-search granularity), current pricing, and quota — all explicitly marked "unresolved" per the task's instruction not to assume availability without evidence; require Rollout Plan Stage 2/3 to resolve.
- Backend (`/interactions/track`) schema flexibility for new instrumentation fields — this is a frontend-only repository; whether the backend can accept/store the proposed new tracking fields is unverified and explicitly flagged as needing backend-team confirmation.
- Whether any client-side view-impression tracking (`useViewTracking`) is currently wired into the search-result grid components specifically — the hook exists (`services/useTracking.ts:188-225`) but its usage inside `ExampleImagesGrid.tsx` was not directly confirmed line-by-line.
- P50/P95 production search latency baseline — not available from a static frontend-only audit; required as a pre-experiment measurement before the online A/B test's latency guardrail can be set.

## Key findings worth re-surfacing at the top level

1. The manager's requested feature has a **pre-existing, detailed design proposal** already in the repository (`docs/eval-framework-visual-search-benchmark-2026-06-14.md`, "Extension C"), filed 2026-06-27, explicitly scoped as post-WC / weeks 7-8 of an 8-week plan — **not yet implemented**. This audit treats it as valuable prior art, cross-checks its assumptions, and does not treat it as authoritative for what to build without independent verification (per the task's explicit instruction that prior conclusions are not automatically valid).
2. **`search_id` does not exist anywhere in the codebase** (confirmed by exhaustive grep) — this is the single most consequential instrumentation gap for the manager's stated business question and should be treated as a P0 prerequisite independent of whether the external-search leg ships at all.
3. Generation IS already tracked today (`actionType: "generate"`, multiple real call sites), but only as a click-time event with no linkage back to the search that produced it, and with no success/failure outcome tracking — a second, related gap.
4. No cross-source merge/rank/dedup logic exists anywhere — this is a genuine from-scratch build, not a refactor of existing code.
5. No external-image-search provider is integrated, provisioned, or evidenced anywhere in this repository — all provider-related figures (cost, quota, latency) are explicitly unresolved pending a real provisioning step.
