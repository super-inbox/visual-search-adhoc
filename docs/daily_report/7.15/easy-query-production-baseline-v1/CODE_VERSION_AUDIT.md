# CODE_VERSION_AUDIT.md — Production vs. Local-Optimization Code Audit

## 1. Version identification (cross-validated)

| Field | Value | Confidence |
|---|---|---|
| `origin_main_commit` | `72b55b667bb5173cab87fcec377198064dc3ac28` | HIGH |
| `production_commit` | `72b55b667bb5173cab87fcec377198064dc3ac28` | HIGH (see evidence below) |
| `pre_optimization_commit` | same as `production_commit` — the entire search-relevance optimization branch (see below) was never pushed to `origin`, so **every commit reachable from `origin/main` is, by definition, pre-optimization** | HIGH |
| `first_optimization_commit` | N/A — no optimization commit exists in `origin/super-inbox/curify-frontend` history at all (see evidence item 5) | HIGH |

### Evidence

1. **GitHub Deployments API** (`gh api repos/super-inbox/curify-frontend/deployments`): the most recent deployment tagged `"environment":"Production"` has `"sha":"72b55b667bb5173cab87fcec377198064dc3ac28"`, `"state":"success"`, `created_at: 2026-07-15T05:39:23Z`, deployed by `vercel[bot]`.
2. **origin/main HEAD match**: `gh api repos/super-inbox/curify-frontend/branches/main` returns the identical commit `72b55b667bb5173cab87fcec377198064dc3ac28`, authored `2026-07-15T05:37:02Z` (2 minutes before the Vercel deployment fired) — "Merge pull request #528 from super-inbox/jwang/vercel".
3. **vercel.json** (`git.deploymentEnabled`): explicitly `"main": true` while all feature-branch patterns (`jwang/*`, `hongjie28-*`, `RS-RSSJobs`, `super-inbox/**`, `dependabot/**`, `renovate/**`, `*`) are `false`. Only `main` auto-deploys to Vercel — corroborates that `origin/main` HEAD is the production source.
4. **Fresh isolated clone**: `/Users/baobaoli/Desktop/curify-production-baseline-2026-07-15` cloned directly from `https://github.com/super-inbox/curify-frontend.git`, `git checkout --detach 72b55b667bb5173cab87fcec377198064dc3ac28` performed. Working tree is clean (`git status --porcelain` empty).
5. **The local optimization branch never reached origin**: the existing dev clone at `/Users/baobaoli/Desktop/curify-frontend` is on local branch `baobao/search-relevance-phrase-alias-2026-07-09`, HEAD `c062e618bce4044bedf718aadf59ff69f0999344`, with a large set of **uncommitted working-tree modifications** to search files. `git ls-remote`/`gh api repos/.../commits/c062e618...` returns **404 Not Found** — this commit does not exist anywhere in the `super-inbox/curify-frontend` remote. `gh api repos/super-inbox/curify-frontend/branches` (full branch list) does not contain `baobao/search-relevance-phrase-alias-2026-07-09` either. The optimization work is 100% local, unpushed, and un-merged.

Per task rule, `origin/main` is not automatically assumed to equal production — it was independently corroborated via the GitHub Deployments API and `vercel.json`, not commit-message inference.

## 2. Feature-by-feature audit at `production_commit` (72b55b6)

Audit method: (a) file-existence check for files that are new in the local optimization branch, (b) full-repo `grep -rniE` for feature-specific identifier strings, run both via GitHub Contents API (pre-clone) and again locally in the checked-out clone (post-clone) — both gave identical results.

| # | Feature | Status | Evidence | Affects Easy-Query Baseline? |
|---|---|---|---|---|
| 1 | 中文复合短语保护 (Chinese compound-phrase protection) | NOT_FOUND | No match for `compound.?phrase`/`短语保护` outside comment text unrelated to this feature; `lib/query_phrase_aliases.ts` absent | Yes — affects zh compound-word queries |
| 2 | protected phrase dictionary | NOT_FOUND | `lib/query_phrase_aliases.ts` does not exist at this commit (`git show 72b55b6:lib/query_phrase_aliases.ts` → not found / GitHub Contents API 404) | Yes |
| 3 | 小红书 (Xiaohongshu) specific rules | NOT_FOUND | No match for `小红书`/`xiaohongshu` anywhere in repo | Only if such queries present |
| 4 | 手冲咖啡 (hand-pour coffee) specific rules | NOT_FOUND | No match for `手冲`/`hand.?pour` | Only if such queries present |
| 5 | 二手奢侈品 (secondhand luxury) specific rules | NOT_FOUND | No match for `奢侈`/`luxury`/`secondhand` | Only if such queries present |
| 6 | protected aliases | NOT_FOUND | Same as #2 | Yes |
| 7 | CJK tokenization 新逻辑 | NOT_FOUND | `lib/cjk_tokenizer.ts` absent. Production's existing CJK handling is an older, simpler **bigram substring match** inline in `search_page.tsx` (comment: "Any CJK character → substring (covers bigrams and full CJK tokens)"), not the new dedicated tokenizer module | Yes — zh queries use the older substring/bigram method |
| 8 | sliding-window 调整 | NOT_FOUND | No match for `sliding.?window` | Unknown magnitude |
| 9 | low-result detection 新逻辑 | PARTIAL / pre-existing baseline version | `LOW_RESULT_THRESHOLD = 5` **already exists** in production `search_page.tsx:47`, with broadening to "up to 8 retrieval paths" when thin (`search_page.tsx:591-621`). This is the **pre-optimization version** of low-result handling (git history shows `P0.2 multi-query retrieval — 3 → up-to-8 paths` landed 2026-06-26, well before the unpushed branch). The branch's "新逻辑" is additional refinement on top of this, not present here | Yes — governs `low_result`/`query_broadened` fields in this baseline |
| 10 | LLM rewrite 新逻辑 | PRESENT (baseline, not "new") | `lib/searchRewrite.ts` (515 lines) calls OpenAI `gpt-4o-mini` for thin-result queries; feature has existed in production since commit `5f442728` (2026-05-18, "LLM query rewrite for thin-result queries") through `c8504f27` (2026-06-26). This is **existing production behavior**, not a later optimization | Yes — production search *does* call an LLM rewriter; this baseline will observe real rewrite behavior |
| 11 | Rewrite Guard | NOT_FOUND | No match for `rewrite.?guard` anywhere in repo | Yes — no guard filtering exists on rewrites in this baseline |
| 12 | accepted rewrites | NOT_FOUND | No match for `acceptedRewrite` | Yes |
| 13 | rejected rewrites | NOT_FOUND | No match for `rejectedRewrite` | Yes |
| 14 | rejection reasons | NOT_FOUND | No match for `rejection.?reason` | Yes |
| 15 | decomposition 新逻辑 | PRESENT (baseline, not "new") | `lib/searchRewrite.ts` already implements query decomposition into orthogonal facets (subject/style/scene/output/era/mood) as part of the "multi-query JSON" rewrite path — present in this same production commit, part of the long-standing rewrite feature, not the unpushed branch's addition | Yes — decomposition is active in this baseline |
| 16 | `d` runtime toggle (`dEnabled`) | NOT_FOUND | No match for `dEnabled` / `d_enabled` anywhere in repo | Yes — no toggle exists; production runs a single fixed code path |
| 17 | `g` runtime toggle (`gEnabled`) | NOT_FOUND | No match for `gEnabled` / `g_enabled` | Yes |
| 18 | A/B/C/D mode support | NOT_FOUND | No match for `mode\s*===?\s*['"]?[ABCD]` | Yes |
| 19 | negative cache TTL fix | NOT_FOUND | No match for `negative.?cache` | Unknown magnitude |
| 20 | model-refusal negative cache | NOT_FOUND | Same as #19 | Unknown magnitude |
| 21 | same-query-only negative cache | NOT_FOUND | Same as #19 | Unknown magnitude |
| 22 | anchor piggyback fix | NOT_FOUND | No match for `anchor.?piggyback` / `piggyback` | Unknown magnitude |
| 23 | Stage 7 相关运行逻辑 | NOT_FOUND | No match for `stage.?7`/`Stage7` in product repo (Stage 7 tooling lives only in the `visual-search-adhoc` eval repo, `scripts/curify-search-stage7-*`, and is local simulation tooling — never part of the product repo) | N/A to production code |
| 24 | Prompt 2D 相关修改 | NOT_FOUND | No relevant match; "Prompt N" is `visual-search-adhoc` project-management terminology, not present in product repo | N/A |
| 25 | Prompt 4A typed runtime toggle | NOT_FOUND | Same reasoning as #16-18 | N/A |
| 26 | full 68 A/B/C/D rerun support | NOT_FOUND | Confirmed absent; that tooling (`scripts/curify-search-stage7-full-rerun-v2/`) lives only in `visual-search-adhoc` and calls the **local uncommitted** branch code, not production | N/A to production code |

## 3. What production search actually does (baseline behavior, for interpreting results)

Confirmed from `app/[locale]/(public)/search/page.tsx` (897 lines) and `lib/searchRewrite.ts` (515 lines) at commit `72b55b6`:

- Search is a **server-rendered page** at `/search?q=<query>` (Next.js App Router, no separate client-side search API call for the initial render).
- `LOW_RESULT_THRESHOLD = 5`. If the initial thin-count is below this, the page expands to up to 8 retrieval paths (1 original + up to 3 LLM paraphrases + up to 6 decomposition facets from `lib/searchRewrite.ts`).
- LLM rewriting **is live in production**, model `gpt-4o-mini`, called server-side (needs `OPENAI_API_KEY` on Vercel — assumed configured since this is the live site).
- CJK queries are matched via inline bigram/substring logic (no dedicated tokenizer module).
- No compound-phrase protection, no protected-alias dictionary, no Rewrite Guard, no accept/reject rewrite tracking are present — so any mis-segmentation or over-eager rewrite behavior for zh compound terms, niche-vertical terms (小红书/手冲咖啡/二手奢侈品), etc. will show up **unmitigated** in this baseline, which is the correct and expected behavior for a pre-optimization baseline.

## 4. Conclusion

`origin/main` and the live production site are the same code version for the purposes of this task, confirmed through independent Vercel/GitHub deployment metadata rather than assumption. This version contains **none** of the 26 listed post-optimization features. It does already contain pre-existing LLM-rewrite and decomposition behavior that predates the unpushed optimization branch by ~2 months — this is expected, baseline production behavior, not contamination.
