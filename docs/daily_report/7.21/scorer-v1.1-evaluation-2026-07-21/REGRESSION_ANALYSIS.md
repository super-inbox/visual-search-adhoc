# Regression Analysis — scorer v1.1 vs current production main

Full paired data: `FULL326_COMPARISON.csv`. A "regression" = candidate label strictly worse than baseline
(rank FAIL<UNJUDGABLE<PARTIAL<PASS). 41 raw regressions; **2 are pure LLM-judge noise** (byte-identical top-5,
label flipped by `gpt-4o-mini` variance) → **39 real regressions** vs **51 real improvements** (1 improvement was
also identical-top5 judge noise). Net real transitions remain positive (+12), but the regressions are not random —
they cluster into two mechanism-specific failure modes plus a preserved-win break.

## Judge-noise regressions (NOT real — flagged, excluded from counts below)
- `coffee cup` PARTIAL→FAIL and `anime merch` PASS→PARTIAL: candidate top-5 titles **identical** to baseline; label
  difference is judge nondeterminism only. (Caveat: this same noise floor of ~1-2/side applies to every count in the
  report; label deltas of this magnitude are within judge variance.)

## Cluster A — multi-term "head-noun + modifier" product queries lose the head noun — HIGH severity, SYSTEMATIC

The correct results match the **head noun** strongly but rarely carry the **modifier** token in their tags, so v1.1's
multi-term machinery (`REQUIRED_TERM_COVERAGE_MIN_RATIO=0.5` coverage gate + `ISOLATED_HIT_MAX_COVERAGE_RATIO=0.5` /
`ISOLATED_HIT_SCORE_CAP=8` isolated-hit cap) treats them as isolated single-term hits and caps their whole-token
score at 8. Wrong-sense content that happens to carry the *modifier* token (or a decomposition slot) then out-ranks
the correct head-noun results. Root-cause tie: `scoreRecord` L166–174 + L232–240; disclosed inference from top-5 shape.

| query | base→cand | candidate top now surfaces (wrong sense) |
|---|---|---|
| wine label / 酒标 | PARTIAL→FAIL | `label printer`, food labels (cheese, olive oil, honey) — **all actual wines dropped** (base had White/Red Wine, Champagne) |
| coffee package / coffee bean package | PARTIAL→FAIL | `ISTJ vs ENFP package` (MBTI "package"), spring-festival MBTI |
| cosmetic package / 护肤品包装 | PARTIAL→FAIL | `blessing dragon`, `bronze rabbit`, `ink fox scholar` (merch) |
| 巧克力礼盒 (chocolate gift box) | PARTIAL→FAIL | `van gogh mystery box`, `waltz box step`, `lifting box` (matched on 盒/"box") |
| 咖啡包装 | PASS→PARTIAL | drift toward generic packaging |
| 零食包装 / bakery package | PARTIAL→FAIL | generic packaging/merch |
| 字母海报 (alphabet poster) | PARTIAL→FAIL | `Analysts/Diplomats/Explorers/Sentinels Group` (MBTI, matched "海报/poster" slot); base had `bl/ch/gr/sh/th` phonics |
| online store banner / 清仓促销横幅 / trade show banner / 直播预告横幅 / black friday banner / 橱窗展示 / product display | PARTIAL/UNJUDGABLE→FAIL | Marvel/comic characters (`Valkyrie`, `thena`, `ikaris`, `marvel blackwidow`) — the "banner"→"Bruce **Banner**" collision; correct promo/retail banners displaced |

**Severity: HIGH.** This is ~18 of the 39 real regressions, hits both zh and en, and is a *new* failure mode
(current main returns the correct head-noun results at the top for these). It is the mirror image of the very cases
v1.1's coverage gate improved (促销海报, sale poster, product launch poster all improved) — the same mechanism helps
some multi-term promo queries and hurts adjacent ones, i.e. high-variance rather than uniformly positive.

## Cluster B — thin single-token CJK queries: relaxed/never-empty expansion buries the exact match — MED/HIGH

For sparse single-token CJK queries the never-empty guarantee + relaxed retrieval + the single-token
`subjectPresent = titleHit || tagsHit` bigram shortcut pull off-subject non-original content **above** the few exact
matches. Because the query is not "result-rich" (< `RESULT_RICH_MIN_ONSUBJECT=8` on-subject candidates), the v1.1
rich-gate is off *by design*, so nothing prunes the junk.

| query | base→cand | note |
|---|---|---|
| 笔袋 / pencil case | PARTIAL→FAIL | western-food sticker templates ranked #1–2 over `Stationery` (see TARGETED_CASE_ANALYSIS Case 1) |
| 挂件 (pendant) | PASS→FAIL | base #1 = exact `pendant`; candidate buries it under `sun wukong`, `zhu bajie`, demographic infographics |
| 娃娃 (doll) | PARTIAL→FAIL | candidate adds `alphabet phonics`, `sun wukong`, `aging society` above/around a thin toy set |
| 泰迪熊 / teddy bear | PARTIAL→FAIL | candidate 4 results (`teddy`, `poodle teddy`, `panda`, `bear`) — borderline; near judge-noise but `panda` off-subject |
| 公仔盒 / mystery box / cultural relic figure | PARTIAL→FAIL | figure/box queries pull wrong-sense box/character content |
| 单词卡 (word card) | PARTIAL→FAIL | candidate surfaces cartoon IP (`black cat detective`, `bluey`, `peppa pig`) over vocabulary cards |
| 练习册 / 课程表 / 书签 / 图解 / diagram / 科学图解 / 广告 / drink bottle | mixed →FAIL/PARTIAL | same shape: relaxed expansion admits off-subject non-original content |

**Severity: MEDIUM-HIGH.** This is the exact class v1.1 was commissioned to fix (笔袋), and for the flagship member
it is *worse* than main. The `subjectPresent` single-token-CJK bigram shortcut (Step-6 residual risk) is the enabling
mechanism and is not addressed by v1.1.

## New zero-result cases (candidate returns 0 where main returned results) — 4
`bobblehead`, `场景模型` (scene model), `会员卡` (membership card), `积分卡` (points card). **`积分卡` was already flagged
as a new-zero case in the 7/19 V2-R3 report and is still not fixed.** Net zero-result is nonetheless *down*
(23→20) because 7 baseline zeros recovered (`扭蛋`, `puzzle`, `diorama`, `advertisement`, `折扣传单`, `优惠券`,
`数学练习册`) — so the zero-result axis is a net win, but with 4 specific fresh holes.

## Preserved-win break — 人体图解 PASS→FAIL
Architecture "anatomy/infographic" templates promoted above human-body content (detailed in TARGETED_CASE_ANALYSIS).
1 of the 6 preserved-win cases; the other 5 improved.

## Net read
The candidate's aggregate is positive, but the regressions are **systematic and mechanism-attributable**, not a
random long tail: the multi-term coverage/isolated-hit cap (Cluster A) and the single-token-CJK relaxed-expansion +
subjectPresent shortcut (Cluster B) each help one set of queries and hurt an adjacent set. Both clusters include the
specific cases this fix was built to repair.
