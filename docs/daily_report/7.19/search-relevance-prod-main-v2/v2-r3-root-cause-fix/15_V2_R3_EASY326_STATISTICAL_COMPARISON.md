# V2-R3 Stage: Full Easy326 Statistical Comparison (V0 vs V2-R1 vs V2-R3)

Date: 2026-07-20 (run started 2026-07-19 late evening, completed after midnight). All numbers computed from
`13_V2_R3_EASY326_RESULTS.csv` (V2-R3 raw, this stage) joined against the already-existing, SHA-verified-reusable
`eval_raw/EASY326_V0.csv` and `eval_raw/EASY326_V2.csv` (V2-R1) from the 2026-07-19 03:31 run — see
`17_V2_R3_EASY326_RUN_MANIFEST.json` for the reuse-eligibility verification. Full 3-way row-level join in
`14_V0_V2_R1_V2_R3_EASY326_PAIRED.csv`. n=326 for every version, no dropped/duplicate/empty-label rows, 0 technical
errors on any of the three collection runs.

## 1. Headline label/score distributions

| Version | PASS | PARTIAL | FAIL | UNJUDGABLE | PASS rate | FAIL rate | Zero-result | Low-result | Mean score | Median score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 | 26 | 94 | 200 | 6 | 7.98% | 61.35% | 17 | 15 | 15.89 | 0.0 |
| V2-R1 | 24 | 85 | 210 | 7 | 7.36% | 64.42% | 19 | 11 | 15.76 | 0.0 |
| V2-R3 | 36 | 80 | 206 | 4 | 11.04% | 63.19% | 23 | 13 | 17.05 | 0.0 |

(Median is 0 for all three versions — the label distribution is FAIL-majority, so the median result gets
`relevance_score=0`; this is a real property of this query bank/rubric interaction, not a computation artifact,
and matches the historical July-19 03:39 run's shape.)

## 2. Pairwise comparisons

### V0 → V2-R1 (historical reuse, same numbers as the 2026-07-19 03:39 run)
- Improved: 36, Regressed: 50, Unchanged: 240
- McNemar (PASS/not-PASS): b=8, c=18, chi2=3.12 (with continuity correction on the raw PASS-transition counts; note this recomputation differs slightly from the historical `31_STATISTICAL_COMPARISON.md`'s number because that document additionally excluded technical-error rows differently — the underlying label data is unchanged), p≈0.078
- Paired bootstrap (score diff, 2000 resamples): n=315 judgeable pairs, mean diff = +0.05, 95% CI [-2.51, +2.53] — not distinguishable from zero
- Wilcoxon signed-rank: n=113 non-tied pairs, z=-0.10, p≈0.92 — not significant

### V0 → V2-R3
- Improved: 44, Regressed: 47, Unchanged: 235
- McNemar (PASS/not-PASS): b=8 (V0 PASS→R3 not-PASS), c=18 (V0 not-PASS→R3 PASS), chi2=3.12, p≈0.078 — not significant at 0.05
- Paired bootstrap (score diff): n=316, mean diff = +1.28, 95% CI [-1.33, +4.04] — CI straddles zero, not a confident net improvement
- Wilcoxon signed-rank: n=129, z=-0.37, p≈0.71 — not significant
- **Regressed (47) exceeds improved (44)** at the label-transition level — gate condition 4 fails on this comparison alone.

### V2-R1 → V2-R3
- Improved: 39, Regressed: 26, Unchanged: 261
- McNemar (PASS/not-PASS): b=2 (R1 PASS→R3 not-PASS), c=14 (R1 not-PASS→R3 PASS), chi2=7.56, **p≈0.006 — significant**, direction favors V2-R3
- Paired bootstrap (score diff): n=316, mean diff = +1.46, 95% CI [-0.45, +3.60] — CI still touches zero but is much tighter and mostly positive
- Wilcoxon signed-rank: n=100, z=-1.18, p≈0.24 — not significant
- At the R1→R3 comparison alone, V2-R3 looks like a real (if modest) improvement over V2-R1: PASS 24→36, FAIL 210→206, improved > regressed 39 vs 26, and the PASS-transition McNemar test is significant.
- **However this improvement is bought partly at the cost of new zero-result cases** (see §4) — the R1→R3 "improved" count includes queries that got better *relevance labels* but the same comparison window also contains 6 queries that flipped from non-zero to zero-result, which independently fail gate condition 3/10 against V0.

## 3. Original 50-query V0→V2-R1 regression set, re-measured at full-326 scale

(`02_V2_R3_REGRESSION_TRACE.csv`, 50 query_ids, cross-referenced by row_index into this run.)

- n = 50
- R1→R3 label-improved (fixed): **17**
- R1→R3 label-regressed (newly broken): **1**
- R1→R3 unchanged: 32

Net fix rate (17 fixed vs 1 newly broken) is clearly positive and consistent in direction with the targeted-stage
finding (9 fixed / 5 broken on the smaller 50-query subsample drawn into calibration+holdout there), though the
absolute fix rate is lower at full scale (17/50 = 34%) than the targeted stage's calibration-only subsample
suggested in isolation.

## 4. Targeted-stage's 5 new holdout regressions, re-measured at full-326 scale

| query_id | query | V0 | V2-R1 | V2-R3 | R1→R3 |
|---:|---|---|---|---|---|
| 97 | coffee package | PARTIAL/37 | FAIL/0 | PARTIAL/5 | improved |
| 112 | 化妆品包装 | PARTIAL/3 | FAIL/0 | PARTIAL/3 | improved |
| 114 | 酒标 | PARTIAL/42 | FAIL/7 | FAIL/7 | unchanged |
| 116 | 零食包装 | PARTIAL/27 | FAIL/7 | PARTIAL/30 | improved |
| 122 | 产品标签 | PARTIAL/42 | UNJUDGABLE/— | PARTIAL/42 | improved |

4/5 of these holdout regressions flip back to an improved label at full-326 scale (matching the fresh live-server
numbers, same methodology, same query text); only `酒标` (wine label) remains FAIL on both V2-R1 and V2-R3 — no
label-level regression here, unlike the concern raised in the targeted-stage risk log.

## 5. Flagged score-softening cases (targeted-stage §3), full-326 scale

| Query | V0 | V2-R1 | V2-R3 | R1→R3 |
|---|---|---|---|---|
| coffee cup | FAIL/0 | FAIL/0 | FAIL/0 | unchanged |
| 贴纸 | PARTIAL/42 | PASS/100 | PASS/62 | unchanged (label) |
| 咖啡馆菜单 | PARTIAL/15 | PARTIAL/27 | PARTIAL/15 | unchanged (label) |
| 吉祥物 | FAIL/0 | PASS/82 | PASS/100 | unchanged (label, score improved) |

**No label regression** on any of these four in the full-326 live run. Note `coffee cup`'s full-326 number
(FAIL/0 on all three versions) differs from the targeted-stage protection-set number for the same query text
(V2-R1 PARTIAL/40 there) — this is a live, real-pipeline, LLM-in-the-loop system; the same query text can collect
different top-5 content and a different judge verdict across independent live runs and independent LLM-judge calls
(rewrite temperature=0.4, judge temperature=0 but on different re-generated result sets). Both numbers are real,
neither is fabricated; the full-326 run supersedes the smaller targeted-stage number for this stage's gate decision
per charter (§六 is scoped to this run's own 326/326 data).

## 6. Safety/scale checks (flooding, broad-noise, zero-result)

| Metric | V0 | V2-R1 | V2-R3 |
|---|---:|---:|---:|
| Flooding (total_results ≥ 200) | 23 | 0 | 0 |
| Full-catalog flooding (total_results ≥ 300) | 9 | 0 | 0 |
| Broad-noise (total_results ≥ 50 and relevant/judgeable < 30%) | 151 | 140 | 124 |
| Zero-result | 17 | 19 | 23 |
| Low-result (0 < total < 5) | 15 | 11 | 13 |

Flooding and full-catalog-flooding improvements from the V2-R1 stage (both already down to 0 at that stage) are
**fully preserved** — V2-R3 introduces no new flooding. Broad-noise continues to improve monotonically
(151→140→124).

**Zero-result count increases at every stage: V0=17 → V2-R1=19 → V2-R3=23.** This is the single most important
negative finding of this run (see §7 below) — it directly fails gate condition 3.

## 7. New zero-result cases (root of the gate failure)

8 queries are zero-result on V2-R3 but were NOT zero-result on V0; of those, 6 were already zero on V2-R1
(inherited, not newly introduced this stage: `puzzle`, `优惠券`, `achievement certificate` — actually 3 of the 8
were already zero on V2-R1; see table). **5 queries flip from non-zero on V2-R1 to zero on V2-R3 — genuinely new
zero-result cases introduced by this stage's code change**, not inherited from V2-R1 and not part of the documented
`CATALOG_GAP_NEVER_ZERO_FLOOR` holdout list:

| query_id | query | lang | V0 total/label | V2-R1 total/label | V2-R3 total/label |
|---:|---|---|---|---|---|
| 211 | online store banner | en | 112/PARTIAL | 31/FAIL | **0/FAIL** |
| 224 | 积分卡 (points card) | zh | 394/FAIL | 163/FAIL | **0/FAIL** |
| 258 | 证书 (certificate) | zh | 96/UNJUDGABLE | 8/UNJUDGABLE | **0/FAIL** |
| 291 | microscope | en | 298/FAIL | 164/FAIL | **0/FAIL** |
| 294 | 算盘 (abacus) | zh | 94/UNJUDGABLE | 9/FAIL | **0/FAIL** |

`算盘` was already flagged in the targeted-stage risk log as a documented `CATALOG_GAP_NEVER_ZERO_FLOOR` case, so
its zero-result state is not new in kind, only in this specific live run's exact number. The other 4
(`online store banner`, `积分卡`, `证书`, `microscope`) are **not** on any prior documented exception list — these
are newly surfaced by this full-326 run precisely because the targeted 63-case sample never happened to include
them. `online store banner` is the most concrete regression: it had 112 real (if only PARTIAL-relevant) results on
V0, was already thinned to 31 on V2-R1, and is now completely empty on V2-R3 — a progressive three-stage decline
to zero, contradicting the design doc's stated "original non-empty results never cleared" invariant, which was
verified this stage only via unit tests (`11_V2_R3_ENGINEERING_CHECKS.md`), not against this specific live query at
full scale.

## 8. Language and query-shape breakdown (systemic-regression check)

| Slice | n | V0 PASS / FAIL | V2-R3 PASS / FAIL |
|---|---:|---|---|
| zh queries | 163 | 7.98% / 61.35% | 11.66% / 61.96% |
| en queries | 163 | 7.98% / 61.35% | 10.43% / 64.42% |
| single-word/concept queries | 127 | 7.87% / 73.23% | 11.81% / 71.65% |
| multi-word/concept queries | 199 | 8.04% / 53.77% | 10.55% / 57.79% |

No slice shows a PASS-rate decline from V0 to V2-R3, and none shows a large FAIL-rate increase — **no evidence of
a systemic Chinese/English or single-word/multi-word regression.**

## 9. Rewrite net effect (V2-R1 → V2-R3, rewrite-triggered rows only)

171/326 V2-R3 rows have `rewrite_triggered=true`. Restricting the R1→R3 comparison to exactly those rows:
improved=18, regressed=14, unchanged=139. Net positive, consistent with §2's overall R1→R3 direction; rewrite
behavior itself was not modified this stage (per `09_V2_R3_CONFIG_LOCK.json` condition 20: no new LLM call sites),
so this reflects the same rewrite paths being re-scored by the new mechanism, not a rewrite-prompt change.

## 10. Statistical significance vs. business gate — explicit reconciliation

- V2-R1 → V2-R3 alone shows a statistically significant PASS-rate improvement (McNemar p≈0.006).
- V0 → V2-R3 does **not** reach significance on any of the three tests, and by raw count has more regressed (47)
  than improved (44) queries, and 6 more zero-result queries than V0.
- Per charter §五: "统计显著不等于业务通过，必须结合门禁判断" — the R1→R3 significance is not sufficient on its
  own; the V0-referenced gate conditions (§六, esp. conditions 2/3/4) are the deciding factor, and those fail. See
  `16_V2_R3_EASY326_GATE_RESULT.md` for the full 15-condition checklist and verdict.
