# Scorer v1.1 — Evaluation Summary

**Date:** 2026-07-21 · **Verdict:** `SCORER_V1_1_NEEDS_MORE_FIXES`

## Objective
Determine, with fresh live data against **current production `main`**, whether scorer **v1.1** (candidate) fixes the
two findings that failed the 7/19 full-326 gate for scorer v1.0 — the **笔袋-class regression** (rewrite/decomposition
content displacing the real subject) and the **new zero-result cases** — without introducing new regressions or losing
the R3 wins.

## What was compared
| role | worktree | branch / SHA | scorer |
|---|---|---|---|
| **candidate** | `curify-frontend-search-v2-r3-2026-07-19` | `…v2-r3-root-cause-fix…` / `1e56e3f0` | v1.1 (`NON_ORIGINAL_BASE_FACTOR=0.5`, `NON_ORIGINAL_OFFSUBJECT_EXTRA_PENALTY=-10`, `RESULT_RICH_MIN_ONSUBJECT=8`) |
| **baseline** | `curify-frontend-main-baseline-2026-07-21` | detached / `c550856e` | current production `main` (pre-scorer) |

Benchmark: 326-query easy bank (`easy_query_bank_v2_2026-07-16.csv`). Collection: `collector.mjs` against live
`next start` servers (baseline :4520, candidate :4521) — real server-computed RSC flight results, identical method
both sides. Judging: `gpt-4o-mini` rubric-v1.1, full 326 on both sides, 0 technical/judge errors, no fabricated numbers.

> Note: this baseline (current main) is **weaker than the old "V0"** (main regressed since 7/19: PASS 26→24, FAIL
> 200→207, zero 17→23). So "candidate beats baseline" is measured against a lower bar than the 7/19 report used.

## Headline numbers (candidate vs baseline)
| metric | baseline (main) | candidate (v1.1) | Δ |
|---|---:|---:|---:|
| PASS | 24 | **37** | +13 |
| PARTIAL | 83 | 76 | −7 |
| FAIL | 207 | **203** | −4 |
| UNJUDGABLE | 12 | 10 | −2 |
| zero-result | 23 | **20** | −3 |
| low-result (1–2) | 19 | **13** | −6 |
| mean score | 14.51 | **16.97** | +2.46 |
| flooding ≥200 results | 18 | **0** | −18 |
| full-catalog flooding ≥300 | 8 | **0** | −8 |

Transitions: **improved 52 / regressed 41 / unchanged 233** (after removing byte-identical-top-5 judge noise:
**51 real improved / 39 real regressed**). On raw aggregate metrics the candidate is a **clear net improvement** and
eliminates all catalog flooding.

## 15-condition gate (adapted: candidate vs baseline-main)
| # | Condition | Result | Basis |
|---:|---|---|---|
| 1 | cand PASS ≥ base PASS | **PASS** | 37 ≥ 24 |
| 2 | cand FAIL ≤ base FAIL | **PASS** | 203 ≤ 207 |
| 3 | cand zero-result ≤ base | **PASS** | 20 ≤ 23 (7 recovered, 4 new) |
| 4 | improved ≥ regressed | **PASS** | 52 ≥ 41 (real 51 ≥ 39) |
| 5 | cand clearly better than baseline overall | **PASS** | mean 14.51→16.97; PASS +13 |
| 6 | **the targeted regressions net-fixed (笔袋-class + new-zero)** | **FAIL** | 笔袋 & pencil case PARTIAL→**FAIL** (worse than main); 积分卡 still zero-result; 人体图解 PASS→**FAIL** |
| 7 | most existing/R3 wins preserved | **PASS** | 5/6 preserved-win cases retained/improved (电影海报, sticker pack, product photo, logo, 日历); 人体图解 lost |
| 8 | broad-noise improvement preserved | **PASS** | ≥100-result queries 101→83 |
| 9 | flooding improvement preserved | **PASS** | ≥200 results 18→0 |
| 10 | no new full-catalog flooding | **PASS** | ≥300 results 8→0 |
| 11 | rewrite path not net-negative | **FAIL** | 175 rewrite-triggered rows: improved 26 < regressed 33 |
| 12 | coffee cup / 贴纸 / 咖啡馆菜单 no severe regression | **PASS** | 贴纸 PARTIAL→PASS, 咖啡馆菜单 FAIL→PARTIAL, coffee cup flip is judge-noise (identical top-5) |
| 13 | no systemic zh/en regression | **PASS** | zh PASS 12→19 FAIL 99→98; en PASS 12→18 FAIL 108→105 |
| 14 | no systemic single/multi-word regression | **MIXED** | single-word PASS 16→26 FAIL 134→129 (better); multi-word PASS 8→11 but FAIL 73→74 (Cluster A drag) |
| 15 | clear overall net improvement | **PASS** | improved>regressed, FAIL/zero/low/flooding all down, mean up |

**Result: 11 PASS, 2 FAIL (#6, #11), 1 MIXED (#14).** The failing conditions are exactly the ones that measure
whether v1.1 did the specific job it was built for.

## Two systematic regression mechanisms (detail in `REGRESSION_ANALYSIS.md`)
- **Cluster A — multi-term "head-noun + modifier" product queries** (wine label, coffee/cosmetic package, 巧克力礼盒,
  字母海报, online-store/black-friday banner…): the coverage gate (`REQUIRED_TERM_COVERAGE_MIN_RATIO=0.5`) + isolated-hit
  cap (`ISOLATED_HIT_SCORE_CAP=8`) cap the correct head-noun results as "isolated single-term hits," letting wrong-sense
  matches on the modifier token (MBTI "package", "label printer", Marvel "Banner") win. ~18 of 39 real regressions. HIGH.
- **Cluster B — thin single-token CJK queries** (笔袋, 挂件, 娃娃, 单词卡…): relaxed/never-empty expansion + the
  single-token `subjectPresent = titleHit || tagsHit` **bigram shortcut** admit off-subject non-original content above
  the sparse exact matches; the rich-gate is off (query not result-rich) so nothing prunes it. Includes the flagship 笔袋.

## Step-6 residual risk — CONFIRMED live
For single-token CJK queries, tag-blob **bigram/substring evidence alone** satisfies `subjectPresent`
(`page.tsx` L600–601, L568). Manifests on 笔袋: a canvas-tote-bag food template (`帆布袋设计` alias, no `笔` char) is a
non-original candidate whose subject-present status let it bypass the −10 off-subject penalty and rank **#1** over
genuine stationery. Documented, not fixed (per charter). Disclosed as inference (frozen worktree, no instrumentation).

## Recommendation
**Do not open the PR to replace production yet — `SCORER_V1_1_NEEDS_MORE_FIXES`.**

The aggregate picture is genuinely positive: v1.1 beats current main on every headline axis, eliminates all catalog
flooding, and restores 5 of 6 R3 wins that current main had lost. **But the evaluation's core acceptance criteria are
not met:** the flagship 笔袋 case is *not* fixed (it regressed to FAIL, worse than main), one of the target new-zero
cases (积分卡) is still zero, a preserved-win (人体图解) newly broke, the rewrite path is net-negative, and two
mechanism-specific regression clusters (multi-term packaging/banner; thin CJK relaxed-expansion) were introduced —
the same mechanisms v1.1 tuned. Suggested next iteration (analysis only, not implemented here): tighten
single-token-CJK `subjectPresent` to require a whole-token (not bigram/substring) hit; and revisit the coverage/
isolated-hit cap so head-noun product queries whose modifier rarely appears in tags are not capped below wrong-sense
modifier matches. Re-run this same gate afterward.
