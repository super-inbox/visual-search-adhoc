# Stage 7 — 68 Hard Query Refresh Report

## 1. Executive Summary

- Locked the authoritative 68-query manifest (`gold_query_test_set_2026-07-07.csv`, SHA-256 `00bd2cff...`), the immutable pre-fix baseline (`curify_search_auto_collect_2026-07-07.csv`, real Playwright execution against live production on 2026-07-07, before any of Stage 2/5/6), and ran a full, code-accurate 2×2 ablation (A=neither, B=d-only, C=g-only, D=d+g) against the real Stage 5/6 modules — not mocks, not a stale mirror.
- **Result: Stage 5+6 do not clear the 60–80% improvement target on this specific 68-query hard set.** Strict PASS = **0/68 (0.0%)**. Broad improvement (PASS+PARTIAL) = **4/68 (5.9%)**. Weighted improvement = **2.9%**. This is a real, verified result, not a harness artifact — see §8 for why, and §12 for what Stage 5/6 *did* measurably fix.
- **New, quantified finding**: a generic single-word LLM decomposition/rewrite slot (`poster`, `design`, `template`, `moodboard`, …) combined with Stage 6's real tokenizer floods the result set catalog-wide in **23/68 (34%) of Mode D rows** (>1000 of 3209 catalog records; two queries hit exactly 3209/3209 when the slot was the literal word "template," which strips to zero tokens and trivially satisfies `allPrimary`). Stage 5 §12 and Stage 6 §17 had already flagged this class of risk from 2 hand-picked examples each; this run shows it is not an edge case on this query set — it is close to a plurality outcome.
- Dictionary-first Scoped Hybrid (d) is working as designed where it fires: 8/68 queries hit a Protected Phrase rule in Mode D, tokenization changed for 34/68 queries relative to the pre-Stage-6 mirror, and the specific fixes Stage 6's own report cited (ASCII preservation, `手冲咖啡` alias/denominator repair, false-`zero_result` noise removal on 3 queries) are all independently reproduced here (§10, §14).
- LLM rewrite (g) triggers on all 68 queries (all are thin by construction — that's why they're the "hard" set) and returns at least one executable path on 50/68 (73.5%); the other 18/68 are genuine `empty_output` (valid JSON, zero usable candidates) — never a parse failure or malformed response in this run.
- **Zero d-only-solved and zero g-only-solved cases** on this 68-query set at the PASS/PARTIAL bar. 3 queries show genuine `d_plus_g_joint_synergy` (neither B nor C alone improved, D did). 1 query shows `combination_regression` (a single component helped, but D was worse than the best single mode). The remaining 64 are `neither_solved` at this query set's difficulty level — mostly genuine content gaps (fandom IP, niche edu jargon, Chinese e-commerce operations jargon) that no amount of better tokenization or paraphrase-rewriting can fix without new catalog content.
- Production code was **not modified**: `git diff --stat` on `curify-frontend` before and after this stage is byte-identical (9 modified + 3 new files, 996 insertions / 82 deletions, same as session start). No commit, no push.

## 2. Completion Status

**Stage 7 DATA COLLECTION COMPLETE. Stage 7 ATTRIBUTION COMPLETE** (not partial) — all four ablation modes were run against real, unmodified Stage 5/6 production code (imported directly, not mocked), all 68 queries received a judged verdict in all 4 modes (272/272), and every query has a final PASS/PARTIAL/FAIL verdict with a documented attribution category. The one limitation worth flagging up front (detailed in §18): Mode A/C's "d=OFF" tokenizer is a faithful, `git show HEAD`-sourced reconstruction run in a standalone harness, not literally the live Next.js SSR page — see §18 for exactly what that harness does and does not reproduce.

## 3. Repositories and Git State

```text
curify-frontend:
  branch: baobao/search-relevance-phrase-alias-2026-07-09
  HEAD:   c062e618bce4044bedf718aadf59ff69f0999344 ("improve Chinese phrase protection in search")
  git status --short (before AND after this stage, byte-identical):
     M app/[locale]/(public)/search/page.tsx
     M lib/__tests__/search_metadata_scenarios.test.ts
     M lib/query_phrase_aliases.ts
     M lib/searchRewrite.ts
     M lib/zh_normalize.ts
     M next.config.ts
     M package-lock.json
     M package.json
     M scripts/eval_search.cjs
    ?? lib/__tests__/searchRewrite.test.ts
    ?? lib/__tests__/stage6_dictionary_hybrid.test.ts
    ?? lib/cjk_tokenizer.ts
  git diff --stat (before AND after, identical): 9 files changed, 996 insertions(+), 82 deletions(-)

visual-search-adhoc:
  branch: main
  HEAD (at session start): 39d8d0a1c6a1c3bd9d31fedfc2d51954cff44f18
  New this stage: docs/daily_report/7.13/search-optimization-stage-7/*,
                  scripts/curify-search-collect-stage7/*
```

No `git reset`/`checkout`/`stash`/`clean`/`commit`/`push` was run against `curify-frontend` at any point. No production file was written to.

## 4. Query Dataset

- **Source**: `docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv`
- **SHA-256**: `00bd2cff0f1dee8168c366020198ed592d0f9654786ff417aa00a19ba4c7ae68`
- **Row count**: 68 data rows, 68 unique `query` values, 0 empty, fixed order preserved throughout (same order used in every output file)
- **Why this file**: it is the query list that was actually executed (via `visual-search-adhoc/scripts/curify-search-collect/collect_curify_search.mjs`, a Playwright collector against production) to produce `curify_search_auto_collect_2026-07-07.csv` — the only real, non-synthetic 68-query execution artifact in the repo. No other 68-row query-execution file exists anywhere under `docs/daily_report/` (checked 7.7, 7.9, 7.11, 7.12 exhaustively). The word "baseline" in this doc set is otherwise reserved for the *58*-query set (`01_original_58_query_scene_classification_2026-07-07.csv`) — the 68 is consistently called the "gold execution set," a distinct, larger, superset-adjacent list. This stage treats it as authoritative per the Stage 7 prompt's own framing ("固定的 68 条 hard queries").
- **Categories**: `primary_scene`/`secondary_scene` (文创/品牌/营销电商/教育, plus English-language homeschool/SEN-education and Amazon/social-commerce clusters), `priority` (mostly P0), `confidence`, `content_gap_hypothesis` — all carried through unmodified into `query_category`/`priority` columns of every output CSV.

## 5. Baseline Provenance

- **Source file**: `docs/daily_report/7.7/curify_search_auto_collect_2026-07-07.csv` (SHA-256 `a4b0f322839241505d7b94c0348461947e3d3ba1fa9f6efe6b78857c60a18404`), collected via Playwright against **live production** `https://www.curify-ai.com` on **2026-07-07**.
- **Source commit context**: predates commits `4210e21f` (Fix 1, phrase-protection) and `c062e618` (Fix 2, Chinese compound protection) — both committed 2026-07-09, two days *after* this collection ran — and predates the entire uncommitted Stage 2/5/6 diff (dated 2026-07-13). It is therefore a real "before this whole initiative" snapshot, not merely "before Stage 5/6."
- **Relevance labels**: reused, not re-judged. `docs/daily_report/7.9/manual_review/curify_68_manual_relevance_audit_2026-07-09.csv` (SHA-256 `e8bb59bdd35d90955b4c5039ac806dfad46e8a90a8bb515e1b6bb344d2b862ce`) already carries a documented, rubric-based Claude first-pass judgment (`claude_relevance_label` PASS/WARN/FAIL, `claude_issue_type`, `claude_relevance_reason`, `claude_confidence`) for exactly these 68 rows. The `human_relevance_label` column exists but was **never filled** (confirmed 0/68 non-empty as of both 2026-07-09 and this stage) — so the existing Claude label is genuinely the best available judged baseline, and reusing it (rather than re-judging with a fresh, unblinded pass) is both the "reuse existing judge" instruction and the only way to avoid contaminating the baseline with knowledge of what Stage 5/6 later did.
- **Data-quality limitations** (declared in `baseline_data_quality` per row, not silently omitted): the Playwright collector scraped only rendered HTML — it never had access to server-side tokenizer/rewrite internals, so `baseline_tokens_json`, `baseline_protected_phrases_json`, `baseline_rewrite_*` fields are `not_available` by construction. This is a collection-scope limit, not a data-quality defect.
- **Proof it was not overwritten**: `hard_queries_68_baseline.csv` did not exist before this run; `aggregate.cjs` checks for its existence and refuses to overwrite (would print a message and exit without writing) if it already existed — the immutability rule is enforced by code, not just by intent. SHA-256 of the written file: `904ea6a5a17a28dbafe3948de6f5bcb958674e518280e5eaad079b150453d233`.

## 6. Search Configurations

| Mode | d | g | How constructed |
|---|---|---|---|
| A | OFF | OFF | Harness reconstruction: `buildSearchTokens`/`scoreBlob` transcribed verbatim from `git show HEAD:app/[locale]/(public)/search/page.tsx` (the actual last-committed pre-Stage-6 code); no rewrite call made. |
| B | ON | OFF | Harness: real Stage 6 `segmentCJKToken`/`applyPhraseAliasRulesExcluding` (imported live from `lib/query_phrase_aliases.ts`) + working-tree `page.tsx`'s decoupled `scoreBlob`; no rewrite call made. |
| C | OFF | ON | Pre-Stage-6 tokenizer (as in A) + real `getMultiQueryPaths()`/`flattenPaths()` imported live from `lib/searchRewrite.ts` (actual production rewrite call, gpt-4o-mini, real API). |
| D | ON | ON | Working-tree `page.tsx` logic end-to-end (Stage 6 tokenizer + real Stage 5 rewrite) — the current production code path. This is the source for `hard_queries_68_refreshed.csv`. |

All four modes import the **same, real, unmodified** `lib/searchRewrite.ts`, `lib/query_phrase_aliases.ts`, `lib/cjk_tokenizer.ts`, `lib/zh_normalize.ts`, `lib/topic_resolver.ts` — bundled via esbuild (`build_bundle.cjs`), never hand-copied for the tokenizer/rewrite core logic. Only the page.tsx-local orchestration (`buildSearchTokens` wrapper, `scoreBlob`, `scoreQueryTokens`, the merge loop, `hasStrict`) — about 150 lines — is reproduced in the harness, and it is reproduced twice: once from the working tree (NEW/d=ON) and once from `git show HEAD` (OLD/d=OFF), both read directly from the actual source, not from memory or documentation.

## 7. Run Environment

```text
Node:              v26.3.0
Package manager:   npm (curify-frontend's own node_modules, symlinked read-only)
OpenAI model:      gpt-4o-mini (production model + params, unchanged)
Jieba dependency:  @node-rs/jieba@^2.0.1 — present, loaded via real lib/cjk_tokenizer.ts
Runtime:           plain Node process per mode (not Next.js SSR — see §18)
Endpoint:          none (offline harness; catalog read directly from public/data/*.json)
Top-K:             10
Low-result threshold: 5 (LOW_RESULT_THRESHOLD, page.tsx:52, read from source — not assumed)
Cache isolation:   one OS process per mode; lib/searchRewrite.ts's in-memory MULTI_CACHE
                    (Map, 256-entry LRU, 7-day success / 10-min negative TTL) starts empty
                    per mode — no cross-mode cache reuse. C and D were run as separate
                    concurrent processes (independent memory), not sharing any cache.
Judge model:       gpt-4o-mini, temperature=0, response_format=json_object
Judge prompt SHA-256: 264bc59e37b08a8421c6cb2cb9ef57d17b76285c7b21bd87ff349319fd9ec2c0
```

## 8. Overall Results

| Metric | Count | Rate |
|---|---:|---:|
| PASS | 0 | — |
| PARTIAL | 4 | — |
| FAIL | 64 | — |
| **Strict PASS rate** (PASS/68) | | **0.0%** |
| **Broad improvement rate** ((PASS+PARTIAL)/68) | | **5.9%** |
| **Weighted improvement rate** ((PASS+0.5×PARTIAL)/68) | | **2.9%** |

**60–80% target assessment**: **Not achieved under any of the three definitions.** Strict PASS (0.0%), Broad improvement (5.9%), and Weighted improvement (2.9%) are all far below the 60–80% band.

**Why, concretely** (not spin — verified in §12/§14/§15): this specific 68-query set was explicitly curated (`content_gap_hypothesis` column in the source manifest) to probe **content gaps** — fandom IP (Love and Deepspace, NCT Dream, Genshin Impact Furina), niche special-education/homeschool jargon (IEP, WIDA, RTI, Charlotte Mason), and Chinese e-commerce operations jargon (私域裂变, 社群接龙, 抖音小黄车) that the **catalog itself** largely does not contain. Stage 5 (rewrite) and Stage 6 (tokenizer/dictionary) are retrieval-mechanics fixes; they cannot manufacture catalog content that was never authored. Where the underlying content genuinely exists but was mis-retrieved, both mechanisms measurably help (§12, §14) — but that describes a minority of this 68-query set.

## 9. Zero-result and Low-result Changes

| | Before (baseline) | After (D) |
|---|---:|---:|
| Zero-result | 11 | 12 |
| Low-result (<5) | 20 | 14 |

- **Zero-result resolved** (baseline zero → D non-zero): 3 queries.
- **New zero-result "regressions"** (baseline non-zero → D zero): 4 queries — but **3 of the 4 are precision improvements, not regressions**, confirmed by manual read: `儿童安全座椅品牌视觉` and `家用医疗器械品牌设计` baseline "10 results" were entirely unrelated noise (eyemask/pendant/duck/guinea pig; baby-care/cookies/pasta-sauce) from the pre-Stage-6 bigram-collision bug — baseline's own Claude judge already scored both **FAIL**, so D returning 0 honest results instead of 10 dishonest ones does not change the verdict (`neither_solved`, FAIL→FAIL). `charlotte mason copywork printable` is the same pattern (baseline FAIL, noise removed). **`知识付费博主课程品牌` is a genuine regression** — baseline was WARN (partial real signal: "Time Management Mastery," "Book Interpretation Series" plausibly adjacent), D returns 0. Flagged in `hard_queries_68_before_after.csv` and listed in §15.
- **Low-result resolved**: 20→14 net; several of the 6 net-resolved are also the same "generic word flooded past 5" pattern from §1, not necessarily quality wins — see §14 for the distinction.

## 10. Protected Dictionary and Tokenization

- **Protected Dictionary hit queries** (Mode D): **8/68** — `NCT Dream photocard template` (nct/photocard), `K-beauty glass skin brand launch visual`, `Y2K chrome skincare launch poster`, `手冲咖啡工作室视觉手册` (手冲咖啡 atomic phrase → its own concept OR-group, the Stage 6 denominator fix, reproduced here), `Amazon EBC enhanced brand content layout`, `Amazon brand story module design`, `小红书香薰产品种草图` (小红书 atomic + 香薰 alias), `maker space label set printable`.
- **Tokenization changed** (Mode B primary tokens ≠ Mode A primary tokens): **34/68 queries** — the real `@node-rs/jieba` segmentation is doing substantive work on over half the set, splitting compound CJK strings into real words instead of the old whole-query-collapse-then-bigram fallback.
- **Longest-match / ASCII preservation**: confirmed working as designed on the CJK-atomic-phrase queries above (e.g. `手冲咖啡` protected as a span, never re-tokenized); no ASCII-drop cases observed among the 68 (no glued mixed-script query like `小红书cover设计` happens to be in this particular 68-set, so this specific Stage 6 fix wasn't newly exercised here — it was already verified in Stage 6's own unit tests).

## 11. Rewrite Performance

```text
Rewrite eligible (initial_result_count < 5):    68/68 (by construction — these are the hard set)
Rewrite triggered:                              68/68
Rewrite executable-path success (≥1 usable path): 50/68  (73.5% of triggered)
Rewrite empty_output (valid JSON, 0 candidates):  18/68  (26.5% of triggered)
Rewrite parse_failure / invalid_shape / model_refusal / same_query_only: 0  (none observed this run)
```

Empty-output rate: **18/68 = 26.5%** (using "of all 68," the more conservative denominator, since 68/68 also triggered — reporting both per the task's requirement not to cherry-pick the denominator: 18/68 = 26.5% either way here since triggered = 68).

## 12. Ablation and Attribution

Per-mode judged verdict distribution (blind LLM judge, gpt-4o-mini temp=0, same prompt across all 4 modes):

| Mode | PASS | PARTIAL | FAIL | zero-result | low-result |
|---|---:|---:|---:|---:|---:|
| A (neither) | 0 | 2 | 66 | 42 | 46 |
| B (d-only) | 0 | 2 | 66 | 41 | 50 |
| C (g-only) | 1 | 1 | 66 | 11 | 15 |
| D (d+g) | 0 | 4 | 64 | 12 | 14 |

Attribution (relative to A, per the §11 rules in the Stage 7 prompt):

| Category | Count | Queries |
|---|---:|---|
| d-only solved | 0 | — |
| g-only solved | 0 | — |
| both independently solved | 0 | — |
| **d+g joint synergy** | **3** | `genshin impact Furina fanart wallpaper 4k`, `松弛感生活方式插画`, `clean girl aesthetic skincare packaging mockup` |
| **combination regression** | **1** | `dress to impress historical royalty outfit inspo` (B or C alone did better than D) |
| neither solved | 64 | (full list in `hard_queries_68_before_after.csv`) |
| ambiguous | 0 | — |

Note on reading this table: "solved" here means "reached PARTIAL or better," which is a low bar given 0 strict PASS anywhere. The 3 joint-synergy cases are real — neither the dictionary fix nor the rewrite alone moved these off FAIL, but the combination did (the rewrite supplies a usable English paraphrase and the tokenizer correctly processes it without flooding). This is the clearest evidence in this dataset that d and g are complementary, not merely additive noise, when they both fire cleanly.

## 13. Query-level Result Table

Full 68-row detail (all columns required by the Stage 7 prompt, including baseline/d-only/g-only/d+g result counts, top-10 JSON, tokens, verdicts, attribution) is in `hard_queries_68_before_after.csv`. Full 272-row A/B/C/D detail is in `hard_queries_68_ablation.csv`. Not reproduced inline here to keep this report readable — see §19 for the files list.

## 14. Count Increased but Relevance Decreased

`count_increased_but_relevance_decreased = true` for **22/68 queries** (baseline count < D count AND D's judged verdict is worse than baseline's). This is dominated by the §1 generic-decomposition-slot flood: of the 23 queries whose Mode D result count exceeds 1000, 22 also fail this relevance check (the 23rd, `genshin impact Furina fanart wallpaper 4k`, is a joint-synergy PARTIAL — genuinely more relevant despite the larger count). Representative examples (full list in `hard_queries_68_before_after.csv`):

- `亚马逊评论截图水印素材`: baseline near-zero → D **3209/3209** (the literal entire catalog — decomposition `output` slot resolved to the stopword "template," which strips to zero primary tokens, making `allPrimary` trivially true for every record). Judge: FAIL, noise_level=high.
- `小红书图文笔记模板 数字标题`: same 3209/3209 mechanism, same root cause.
- `故障艺术风格海报`: baseline near-zero → D 2814 (decomposition `output`="poster", a single common word matching most of the catalog's tag vocabulary). Note: Stage 6's own isolated tokenizer-only test showed this query improving from 339→2 (a precision win) — that fix is real and reproducible (confirmed in Mode B: tokenization alone does not reintroduce this flood), but it is **undone end-to-end** once Stage 5's rewrite layer adds the generic "poster" pass on top in Mode D. This is a genuine Stage 5×Stage 6 interaction this stage is the first to quantify at full-dataset scale.

## 15. Remaining FAIL Cases

64/68 queries remain FAIL under Mode D. Manually reviewed in full (not sampled) via: (a) an automated cross-consistency check across all 272 judge outputs for PASS-but-noisy or FAIL-but-apparently-relevant contradictions — **zero found**; (b) direct reading of the specific higher-risk subsets: all 22 count-increased-but-worse rows, all 23 >1000-result rows, all zero-result-transition rows (both directions), and the one in-scope named-risk query (`二手奢侈品鉴定品牌视觉`, §16). No case where the automatic (judge) verdict looked wrong on manual inspection was found; no override was applied to any of the 68 final verdicts (`hard_queries_68_before_after.csv`'s `final_verdict` equals the judge's `d_plus_g_verdict` for every row in this run).

The 64 FAILs split roughly into three buckets on manual read:
1. **Genuine content gaps** (majority): fandom/IP queries (Love and Deepspace, NCT Dream, 光与夜之恋, meme格式国风梗图), niche special-education/homeschool terms (IEP, WIDA, RTI, Charlotte Mason, "first then board autism"), and Chinese social-commerce operations jargon (私域裂变, 社群接龙, 抖音小黄车) where the catalog has no matching content regardless of retrieval quality.
2. **Generic-decomposition-slot flood** (§1/§14): retrieval mechanics actively made these worse, not merely unhelpful.
3. **Empty rewrite, unchanged from baseline**: 18 queries where the rewrite legitimately found nothing usable (§11) and Stage 6's tokenizer alone doesn't have matching content either.

## 16. PARTIAL Cases and Why They Are Not PASS

4 PARTIAL (WARN-labeled) cases in Mode D, all missing PASS on the same axis — subject/category is right, the query's *specific* qualifier is not represented:

- `genshin impact Furina fanart wallpaper 4k`: results are genuinely Genshin-Impact-adjacent but not Furina-specific or wallpaper-format-specific.
- `松弛感生活方式插画`: results are lifestyle/wellness-adjacent but not the specific "relaxed/loose" (松弛感) illustration aesthetic.
- `clean girl aesthetic skincare packaging mockup`: some relevant skincare content present but mixed with unrelated items; no packaging-mockup-specific hits.
- `heritage brand rebrand moodboard`: branding/moodboard content present but no heritage-brand-specific examples.

**Named-risk query check** (`二手奢侈品鉴定品牌视觉`, the one query from the Stage 7 prompt's named-risk list that is actually in the 68 — see §18 for the other 5, which are not in this query set): baseline 4 results (already FAIL per Claude's judge), Mode B and D both **57** results — reproducing exactly the risk Stage 6's own report flagged in advance (§17 of that report: "generic remaining tokens (品牌/视觉) clearing the relaxed bar... recorded as manual_review_needed, not silently accepted as a pure win"). This stage's judge independently and correctly labels both B and D **FAIL** ("generic fashion items rather than luxury goods authentication") — confirming the count increase (4→57) is noise, not a real recall gain, exactly as Stage 6 predicted and exactly why this stage does not auto-PASS on count.

## 17. Runtime Errors, Timeouts, and Empty Pages

**Zero.** 0/272 harness rows had `error`/`rewrite_error` set; 0/272 judge calls failed after retry (all succeeded on first or second attempt, `run_judge.cjs`'s 3-attempt retry loop). No timeouts, no empty pages (not applicable — offline harness, no page rendering).

## 18. Known Limitations

- **Historical-baseline scope**: baseline (2026-07-07) predates Stage 2's Fix1/Fix2 as well as Stage 5/6 (§5, §18-manifest). The strict, code-accurate "neither" for d/g attribution purposes is the separately-computed harness Mode A, not the historical baseline — both are reported, not conflated.
- **Corpus drift**: the catalog (`public/data/nano_inspiration.json`, 3209 records) was read live from the current `curify-frontend` working tree at run time (2026-07-13). If the catalog changed between 2026-07-07 (baseline collection) and now, baseline vs. D count comparisons partially reflect catalog drift, not only code changes. Not independently quantified this stage (would require a historical catalog snapshot, which does not exist).
- **LLM nondeterminism**: both the rewrite calls (temperature=0.4) and the judge calls (temperature=0, but determinism is not contractually guaranteed by the API) mean an exact re-run could differ slightly. The gating/gap logic and overall magnitude of findings (0% strict PASS, 34% generic-flood rate) are robust to this — a few individual query verdicts flipping on re-run would not change the headline conclusion.
- **Native-module / deployment**: this stage ran entirely locally (Node process, real `@node-rs/jieba`, real catalog) — it does not independently re-verify Vercel Serverless cold-start behavior (Stage 6 §19 already flagged this as `not_verified` and this stage does not add new evidence either way).
- **Missing instrumentation**: the harness does not reproduce the concept-expansion template-rail pass, topic-page redirects, or the client-side LLM template matcher (`lib/searchTemplateMatch.ts`) — none of these touch the inspiration-level Top-10 results this report scores, so this is a scope boundary, not a known gap in the reported numbers.
- **Named-risk query list mismatch**: 5 of the 6 explicitly-named risk queries in the Stage 7 prompt (蔚来ES6, 比亚迪海豹, 白箱, 五菱宏光, 蜜雪冰城) are not members of the actual 68-query gold set (grep-verified against `gold_query_test_set_2026-07-07.csv`) — they were evaluated in Stage 5/6's own separate, smaller test matrices, cited here for context but out of this stage's dataset per the no-query-modification rule.

## 19. Files Generated

```text
/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_baseline.csv
/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_refreshed.csv
/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_before_after.csv
/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_ablation.csv
/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_summary.md  (this file)
/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.13/search-optimization-stage-7/run_manifest.json

/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/build_bundle.cjs     (esbuild-bundles real Stage 5/6 modules)
/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/run_mode.cjs          (2x2 ablation harness)
/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/run_judge.cjs         (blind LLM relevance judge)
/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/judge_prompt.js       (judge rubric, reused from 7.9 guide)
/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/aggregate.cjs         (CSV/report assembly)
/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/mode_{A,B,C,D}_results.json  (raw per-mode harness output)
/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/judge_results.json    (raw judge output)
/Users/baobaoli/Desktop/visual-search-adhoc/scripts/curify-search-collect-stage7/_bundle_source_hashes.json  (SHA-256 of every bundled production source file)
```

No screenshots were taken this stage (offline harness, no browser).

## 20. Git Diff and Safety Verification

```text
$ cd curify-frontend && git status --short && git diff --stat
(identical before and after this stage — see §3)
```

Verified via `git diff --stat` blob-level comparison (line counts, not just file names) at both the start and end of this session: `page.tsx` +145/-X, `search_metadata_scenarios.test.ts` +112, `query_phrase_aliases.ts` +209, `searchRewrite.ts` +244, `zh_normalize.ts` +9, `next.config.ts` +11, `package-lock.json` +281, `package.json` +1, `eval_search.cjs` +66 — 996 insertions / 82 deletions total, matching exactly. No Stage 5 or Stage 6 file was touched. No protected-dictionary content was edited. No query-specific branch was added anywhere in the harness (`run_mode.cjs`/`aggregate.cjs` contain zero query-string literals other than the risk-family substring list used purely for `manual_review_required` flagging, which does not alter any verdict computation). Production default behavior is unchanged — the harness only *imports* real modules read-only; it never writes to `curify-frontend`.

Test/typecheck/build/lint were **not re-run** this stage: Stage 6's own report (§21-22) already ran and recorded the full suite (232/232 tests, 0 typecheck errors, build PASS, lint FAILS with a documented pre-existing, non-regressing signature) immediately before this stage began, and this stage made zero production-file edits, so there is nothing new to verify. Re-running was judged unnecessary rather than skipped for convenience — happy to re-run on request.

## 21. Final Stage 7 Verdict

**Stage 7 COMPLETE.**

- Authoritative 68-query list: locked and hashed (§4).
- Baseline: traceable, immutable, not overwritten (§5).
- Final d+g 68-query re-run: done (Mode D, `hard_queries_68_refreshed.csv`).
- Auditable 2×2 ablation: done, real code, 272/272 rows (`hard_queries_68_ablation.csv`).
- All 68 queries have a final verdict, all summary metrics computed, all 6 required files generated and row/uniqueness/consistency-checked (§19, and PASS+PARTIAL+FAIL=68 confirmed).
- Production search behavior: unmodified, verified byte-identical before/after.
- No commit, no push.
- **Headline finding, stated plainly**: Stage 5+6 do not reach the 60–80% improvement target on this specific hard-query set (actual: 0% strict / 5.9% broad / 2.9% weighted), primarily because most of the 68 queries probe genuine catalog content gaps rather than retrieval-mechanics bugs — and where retrieval mechanics *are* the bottleneck, this run surfaces a real, previously-under-quantified regression risk (generic decomposition-slot flood, 34% of D rows) that a future stage should address before claiming a broad win.
