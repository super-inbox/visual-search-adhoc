# Cluster A / Cluster B Outcome Analysis — 0e794cd9 vs. Full-326 Live Results

Source of cluster definitions: `docs/search-relevance-v2r3-r1-2026-07-21.md` (commit `0e794cd9`) and the 2026-07-21
`scorer-v1.1-evaluation-2026-07-21/REGRESSION_ANALYSIS.md`. Both are the frontend team's own authoritative,
evidence-supported cluster mapping — no cluster membership is invented in this report. Row-level evidence:
`11_CLUSTER_AB_REPRESENTATIVE_CASES.csv`.

## What Cluster A is
Multi-term **"head-noun + format/output word"** queries (e.g. `wine label`, `字母海报`, `巧克力礼盒`, `人体图解`) where the
scorer's old subject heuristic ("longest original token = subject") picked the **format word** (label, 海报, 礼盒, 图解)
instead of the theme/head-noun (wine, 字母, 巧克力, 人体). Wrong-sense content carrying only the format word then read
as subject-present and outranked genuine head-noun matches, which took a missing-subject penalty. Code path:
`lib/searchSubject.ts` (new file, `subjectUnits()` + `FORMAT_TOKENS` lexicon), wired into
`app/[locale]/(public)/search/page.tsx`'s `deriveFieldHits`. Landed in `0e794cd9` (Fix A).

## What Cluster B is
Sparse **single-token CJK queries** (e.g. `笔袋`, `挂件`, `娃娃`, `泰迪熊`, `单词卡`) where relaxed/never-empty expansion
plus a `subjectPresent = titleHit || tagsHit` bigram/substring shortcut let off-subject non-original content rank
above the few genuine exact matches. Code path: the single-token branch of `deriveFieldHits` in `page.tsx`. Landed in
`6efdd904` (Fix B), predates this diff range but is included here because `0e794cd9` also touches the single-token
branch (folding it into the same `subjectUnits()` call).

## Did the fixes work? — evidence from the live full-326 run

### Cluster A (format-word subject fix)
| query | production | prev candidate (pre-fix) | **latest (0e794cd9)** | verdict |
|---|---|---|---|---|
| wine label (EN) | PARTIAL | FAIL | **PASS** | **Fixed** — correct wines (White/Red Wine, Champagne, tequila) back at top. |
| 酒标 (ZH, same concept) | PARTIAL | FAIL | **FAIL (unchanged)** | **Not fixed** — top5 still `label printer`, `en-zh` mismatches. |
| 字母海报 | PARTIAL | FAIL | **FAIL (unchanged)** | **Not fixed** — MBTI group photos still dominate; identical top5 to pre-fix. |
| 巧克力礼盒 | PARTIAL | FAIL | **FAIL (unchanged)** | **Not fixed** — `van gogh mystery box`, box-merch content still on top. |
| 人体图解 (preserved-win break) | PASS | FAIL | **PARTIAL (partial recovery)** | **Partially fixed** — genuine `human body` results return to rank 1, but architecture landmarks (`empire state building` etc.) still intrude at rank 4-5; does not fully restore the original PASS. |

**Read:** the doc (`search-relevance-v2r3-r1-2026-07-21.md`) states the fix was *"confirmed live on all four via
scorer instrumentation"* for wine label, 字母海报, 巧克力礼盒, 人体图解. The **full-326 live pipeline result does not
match that claim for 3 of the 4** — only `wine label` (English) is fully fixed, and `人体图解` is only partially
fixed. The most likely explanation (inference, not instrumented) is that the format-word subject fix removes ONE
demotion trigger, but the Cluster-A root cause the 7/21 report identified was **two mechanisms together**
(`REQUIRED_TERM_COVERAGE_MIN_RATIO` coverage gate + `ISOLATED_HIT_SCORE_CAP` isolated-hit cap) — Fix A only touches
subject derivation upstream of those gates, so a query can now be correctly subject-present and still get capped by
the OTHER mechanism. This is disclosed as inference from result shape, consistent with the charter's own
"per-candidate attribution is inference" methodology used in the 7/21 report.

### Cluster-A-adjacent (same "head-noun + format" shape, English "X package")
| query | production | prev candidate | latest | verdict |
|---|---|---|---|---|
| coffee package | PARTIAL | FAIL | **PASS** | **Fixed** — MBTI "package" content displaced, genuine coffee-brewing/packaging content restored. |
| coffee bean package | PARTIAL | FAIL | **FAIL (unchanged)** | Not fixed — top5 now just `coffee bean anatomy` (1 item), low-result. |
| cosmetic package | PARTIAL | FAIL | **PARTIAL (partial recovery)** | Improved from FAIL but does not reach production's PARTIAL-quality result mix fully; `blessing dragon`/`bronze rabbit` merch pushed out, `beauty products`/`skincare routine` restored to top ranks. |

### Known, disclosed non-fix
`black friday banner` remains FAIL, unchanged top5 (`marvel blackwidow.jp`) across prev→latest. The `search-relevance-v2r3-r1-2026-07-21.md` doc **explicitly discloses this is out of scope** for Fix A — it is a protected-phrase case where the isolated-hit cap is disabled, requiring a separate lever "filed as follow-up, not in this commit." Confirmed consistent with live results: **no regression, but also no fix, exactly as documented.**

## Cluster B (single-token CJK subject-presence fix)
| query | production | prev candidate | **latest (0e794cd9)** | verdict |
|---|---|---|---|---|
| **笔袋 (flagship)** | PARTIAL | FAIL | **FAIL (unchanged)** | **Not fixed** — top5 still led by two unrelated "microsoft ai dilemma 07 case google gemini" tech-news templates, `Stationery` sits at rank 3. Worse than production's PARTIAL. |
| pencil case (EN pair) | PARTIAL | FAIL | **FAIL (unchanged)** | Same shape — same 2 tech-news templates now the ONLY 2 results (total dropped to 3, now also low-result). |
| 挂件 (pendant) | PASS | FAIL | **PASS (recovered)** | **Fixed** — genuine pendant results restored to top ranks, `sun wukong`/`zhu bajie` pushed out. |
| 娃娃 (doll) | PARTIAL | FAIL | **FAIL (unchanged)** | Not fixed — alphabet-phonics content still dominates. |
| 泰迪熊 (teddy bear) | PARTIAL | FAIL | **FAIL (unchanged)** | Not fixed — same top5 as pre-fix. |
| 单词卡 (word card) | PARTIAL | FAIL | **FAIL (unchanged)** | Not fixed — cartoon IP (`black cat detective`, `bluey`, `peppa pig`) still dominates. |
| 积分卡 (points card, 7/21-flagged new-zero) | FAIL (368 results, wrong-sense) | FAIL (**zero**) | **PARTIAL (recovered from zero, 87 results)** | **Fixed** — the zero-result hole from 7/21 is resolved; genuine-adjacent content now returns. |
| 会员卡 (membership card, 7/21-flagged new-zero, 积分卡's sibling) | FAIL (368 results, wrong-sense) | FAIL (**zero**) | **FAIL (still zero)** | **Not fixed.** |

**Read: Cluster B's flagship case (`笔袋`) — the case the fix was explicitly named after (`Fix B — single-token
subject-presence bypass (笔袋 flagship)`) — remains unresolved and still worse than production main.** Of the 6
Cluster-B-shaped queries tested, only 1 (`挂件`) is genuinely fixed; the two zero-result-recovery bonus cases split
1-for-1 (`积分卡` fixed, `会员卡` not). This is a materially weaker outcome than the commit message's framing implies.

One further observation (not part of the original Cluster B taxonomy, flagged during automated sanity checking,
`01_AUTOMATED_SANITY_NOTES.md`): the two "microsoft ai dilemma 07 case google gemini" templates that block `笔袋`/
`pencil case` look like a **specific mis-tagged/mis-aliased catalog record** (a tech-news template with no plausible
stationery content), not a generic off-subject-relaxation artifact. This may be a narrower, more directly fixable
catalog-hygiene issue than the general Cluster-B mechanism — worth a targeted look independent of further scorer
tuning.

## Net assessment
- Cluster A: **1 of 4** representative cases fully fixed, 1 partially recovered, 2 unchanged. The adjacent English
  "X package" shape fares better (1 fixed, 1 partial, 1 unchanged of 3). Aggregate vertical-level evidence (`package`,
  `poster_specific` in `10_VERTICAL_SUMMARY.csv`) is genuinely positive, but the four cases the fix was named for are
  only partially resolved.
- Cluster B: **1 of 6** representative cases fully fixed (recovered to production's PASS); the flagship case is
  unresolved and still a regression vs. production. The `stationery` vertical (which contains 笔袋/pencil case) shows
  a **net 4 regressions vs. production, 0 improvements** — the vertical most directly targeted by this fix is,
  in aggregate, worse than before the fix.
- No NEW regression was introduced by testing these specific representative cases beyond what the 7/21 report already
  disclosed (`酒标`, `字母海报`, `巧克力礼盒`, `笔袋`, `pencil case`, `娃娃`, `泰迪熊`, `单词卡`, `会员卡` were already FAIL in
  the previous candidate; none of them got worse in the latest candidate). The fix's real, confirmable wins are:
  `wine label` (EN), `coffee package`, `挂件`, `积分卡`, and a partial recovery on `人体图解` and `cosmetic package`.
