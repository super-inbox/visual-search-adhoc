# Old-328 Easy Query: V0 vs V2-R1 (frozen) Statistical Comparison

Date: 2026-07-19. Supplementary run only — backfills the old 328-query Easy Query seed library (`docs/daily_report/7.15/easy-query-production-baseline-v1/query_input/easy_queries_cleaned_300_plus_2026-07-14.csv`, SHA-256 `682ed08a...b32f3e`) that the prior 326-query session explicitly reported as `NOT_ATTEMPTED` due to time constraints. All numbers below are computed directly from real, live-collected data (`scripts/collector.mjs` against real running `next start` V0/V2 servers, ports 4501/4502) and real LLM judgments (`scripts/judge.mjs`, gpt-4o-mini, rubric-v1.1). Same, byte-identical scripts as the prior 326-query run — see `00_V2_R1_FREEZE_MANIFEST.json` for the full config-reuse record. No numbers here are estimated, extrapolated, or fabricated.

## Completion status

| Dataset | Queries | Status |
|---|---:|---|
| Old 328 Easy Query seed library | 328 | **COMPLETE** (328/328, 0 technical collection failures, 0 error rows, 11 legitimate UNJUDGABLE on each side) |

## Aggregate results

All rates/percentages below use the true denominator **n=328** (all queries, including UNJUDGABLE). PASS+PARTIAL+FAIL alone sums to 317 on each side because 11 queries per side are UNJUDGABLE (a legitimate judge outcome — see §Label completeness audit below); the rate calculations were never computed on 317, only the raw PASS+PARTIAL+FAIL count naturally omits the UNJUDGABLE bucket if read without that context.

| Metric | V0 | V2-R1 | Δ |
|---|---:|---:|---:|
| PASS | 56 (17.07%) | 60 (18.29%) | +1.22pp (better) |
| PARTIAL | 79 (24.09%) | 79 (24.09%) | 0 |
| FAIL | 182 (55.49%) | 178 (54.27%) | −1.22pp (better) |
| UNJUDGABLE | 11 (3.35%) | 11 (3.35%) | 0 (count equal, underlying queries differ — see §Label completeness audit) |
| **Sum (PASS+PARTIAL+FAIL+UNJUDGABLE)** | **328 (100.00%)** | **328 (100.00%)** | accounts for all 328 rows |
| Zero-result | 27 (8.23%) | 29 (8.84%) | **+0.61pp (worse)** |
| Low-result (1–4) | 18 (5.49%) | 23 (7.01%) | **+1.52pp (worse)** |
| Mean relevance score (judgeable, n=317) | 22.64 | 24.17 | +1.53 |
| Median relevance score | 0 | 0 | 0 |
| Improved queries | — | — | 24 |
| Regressed queries | — | — | 16 |
| McNemar (PASS transitions, b/c) | b=5, c=9 | | χ²=0.643, p=0.423 (not significant) |
| Paired bootstrap mean score Δ (n=311) | | | **+1.46 [95% CI: +0.36, +2.56] (excludes zero — statistically significant)** |
| Wilcoxon signed-rank (n=58 non-tied pairs) | | | z=−2.694, **p=0.007 (statistically significant)** |

## Reading

On the old-328 seed library taken in isolation, V2-R1 shows a **small, statistically detectable positive shift** in judge score (paired bootstrap CI excludes zero; Wilcoxon p=0.007) and more improved queries (24) than regressed (16). PASS rate is up 1.2pp and FAIL rate down 1.2pp, though neither reaches significance via McNemar (p=0.42, n too small for this specific transition count).

At the same time, **zero-result rate and low-result rate both moved in the unfavorable direction** (zero +0.61pp, low-result +1.52pp) — the same category of regression the 326-set analysis flagged as the core failure mode (simple literal-noun queries losing their previously-clean strict-only result set to weaker relaxed candidates). The regressed-query list below shows this pattern concretely: several PASS→PARTIAL/FAIL and PARTIAL→FAIL transitions are exactly the literal-object/demographic queries (马克杯/mug, 咖啡/coffee, 香水/perfume, 口红/lipstick, 家纺/home textiles, 保健品/health supplements, 大学生/college student, 素食者/vegetarian) already diagnosed in `docs/daily_report/7.19/search-relevance-prod-main-v2/31_STATISTICAL_COMPARISON.md` as the root cause of the 326-set regression.

### Improved queries (n=24)

藤编, denim, 北欧, 厨房, 演唱会, 医疗健康, 美发美甲, 标签, 折页, children, 青少年, teacher, 健身爱好者, 手工艺人, 宝妈, 情人节, 双十一, 光棍节, 首饰, 包包, 童装, 灯具, 护发产品, 学习

### Regressed queries (n=16)

月亮 (PASS→PARTIAL), metal (UNJUDGABLE→FAIL), 温室 (PARTIAL→FAIL), 咖啡 (PARTIAL→FAIL), 马克杯 (UNJUDGABLE→FAIL), 大学生 (PASS→UNJUDGABLE), 素食者 (PARTIAL→FAIL), 留学生 (PASS→PARTIAL), 冬至 (PASS→PARTIAL), 香水 (PARTIAL→FAIL), 口红 (PARTIAL→FAIL), 家纺 (PARTIAL→FAIL), toys (UNJUDGABLE→FAIL), 保健品 (PARTIAL→FAIL), 乳制品 (PASS→PARTIAL), 送礼 (UNJUDGABLE→FAIL)

Full per-query detail: `03_V0_V2_R1_OLD328_PAIRED.csv`.

## Label completeness audit (added 2026-07-19, post-hoc read-only verification)

A read-only integrity pass confirmed the following against `01_V0_OLD328_RESULTS.csv`, `02_V2_R1_OLD328_RESULTS.csv`, `03_V0_V2_R1_OLD328_PAIRED.csv`:

- **Row counts**: exactly 328 data rows (+1 header) in each of the three CSVs. No file is short or long.
- **Duplicate `row_index`**: none, in any of the three files (328 distinct values each).
- **Duplicate `query`**: none.
- **Empty `relevance_label`**: none, in either V0 or V2 file.
- **Distinct label values observed**: exactly `{PASS, PARTIAL, FAIL, UNJUDGABLE}` on both sides — no stray/unexpected label strings, no `ERROR` rows (0 error rows, consistent with 0 technical collection failures already reported).
- **Full label distribution**: V0 = PASS 56 + PARTIAL 79 + FAIL 182 + UNJUDGABLE 11 = **328**. V2-R1 = PASS 60 + PARTIAL 79 + FAIL 178 + UNJUDGABLE 11 = **328**. Both sides account for all 328 rows exactly.
- **`ok` column**: `true` for all 328 rows on both sides (no silent collection failures hiding inside the UNJUDGABLE bucket).
- **UNJUDGABLE reason**: all 22 UNJUDGABLE rows (11 V0 + 11 V2) carry `primary_failure_reason=NO_JUDGEABLE_RESULTS` — i.e. the query returned nonzero results (`total_results` > 0, `zero_result=false` in every case), but the LLM judge's per-result labels for the top-5 items were all `UNJUDGABLE` (titles/tags/topics gave no usable relevance signal), so `judgeable_count=0` and the rubric assigns the query-level label `UNJUDGABLE` per `scripts/judge.mjs`'s documented logic. This is an intended, disclosed outcome category of the rubric (see prior run's `31_STATISTICAL_COMPARISON.md` and the original rubric's UNJUDGABLE definition), not a script defect.

**Important nuance**: V0's 11 UNJUDGABLE queries and V2-R1's 11 UNJUDGABLE queries are **not the same 11 queries** — the judge runs independently per version per query, so a query can be UNJUDGABLE on one side and have a real label (PASS/PARTIAL/FAIL) on the other. The union of "UNJUDGABLE on at least one side" is **17 unique queries** (5 UNJUDGABLE on both sides + 6 UNJUDGABLE only on V0 + 6 UNJUDGABLE only on V2-R1 = 17), not 11.

| row_index (query_id) | query | V0 total_results | V2-R1 total_results | V0 label | V2-R1 label | judge status | reason |
|---:|---|---:|---:|---|---|---|---|
| 23 | 相框 | 93 | 91 | UNJUDGABLE | UNJUDGABLE | UNJUDGABLE both sides | NO_JUDGEABLE_RESULTS |
| 42 | metal | 25 | 25 | UNJUDGABLE | FAIL | UNJUDGABLE on V0 only | V0: NO_JUDGEABLE_RESULTS; V2: judged normally |
| 61 | 藤编 | 49 | 49 | FAIL | UNJUDGABLE | UNJUDGABLE on V2-R1 only | V2: NO_JUDGEABLE_RESULTS; V0: judged normally |
| 63 | 亚克力 | 11 | 11 | UNJUDGABLE | UNJUDGABLE | UNJUDGABLE both sides | NO_JUDGEABLE_RESULTS |
| 119 | 厨房 | 56 | 56 | FAIL | UNJUDGABLE | UNJUDGABLE on V2-R1 only | V2: NO_JUDGEABLE_RESULTS |
| 128 | 展览 | 89 | 89 | UNJUDGABLE | UNJUDGABLE | UNJUDGABLE both sides | NO_JUDGEABLE_RESULTS |
| 169 | gaming | 37 | 37 | UNJUDGABLE | UNJUDGABLE | UNJUDGABLE both sides | NO_JUDGEABLE_RESULTS |
| 194 | 标签 | 119 | 119 | FAIL | UNJUDGABLE | UNJUDGABLE on V2-R1 only | V2: NO_JUDGEABLE_RESULTS |
| 202 | 折页 | 96 | 96 | FAIL | UNJUDGABLE | UNJUDGABLE on V2-R1 only | V2: NO_JUDGEABLE_RESULTS |
| 215 | 马克杯 | 40 | 40 | UNJUDGABLE | FAIL | UNJUDGABLE on V0 only | V0: NO_JUDGEABLE_RESULTS |
| 218 | 青少年 | 24 | 24 | FAIL | UNJUDGABLE | UNJUDGABLE on V2-R1 only | V2: NO_JUDGEABLE_RESULTS |
| 226 | 大学生 | 294 | 309 | PASS | UNJUDGABLE | UNJUDGABLE on V2-R1 only | V2: NO_JUDGEABLE_RESULTS |
| 231 | 健身爱好者 | 12 | 289 | UNJUDGABLE | PARTIAL | UNJUDGABLE on V0 only | V0: NO_JUDGEABLE_RESULTS |
| 278 | 首饰 | 12 | 12 | UNJUDGABLE | PASS | UNJUDGABLE on V0 only | V0: NO_JUDGEABLE_RESULTS |
| 287 | toys | 14 | 14 | UNJUDGABLE | FAIL | UNJUDGABLE on V0 only | V0: NO_JUDGEABLE_RESULTS |
| 306 | 送礼 | 11 | 11 | UNJUDGABLE | FAIL | UNJUDGABLE on V0 only | V0: NO_JUDGEABLE_RESULTS |
| 320 | 拍照 | 97 | 97 | UNJUDGABLE | UNJUDGABLE | UNJUDGABLE both sides | NO_JUDGEABLE_RESULTS |

None of these 17 rows are "untagged", "empty-label", "other label", or "summary-script omissions" — every one carries a fully valid, explained rubric outcome. No original evaluation CSV was modified to produce this audit; this section only adds an explicit accounting that was previously stated in prose (`"11 legitimate UNJUDGABLE on each side"` in the Completion Status line above) but not broken out as a table row, which is what created the apparent 317-vs-328 discrepancy.

## Why this does not overturn the 326-set conclusion

The task brief for this stage is explicit that a favorable-looking 328 result must not be used to wave away the already-observed 326-set regression. Three reasons the 326 finding stands as the governing result:

1. **Sample size and representativeness**: the 326-query Easy Query Benchmark v2 is the larger, purpose-built, more recently curated dataset (326 vs 328, but 326 was explicitly the "primary, most statistically meaningful dataset" per the prior session's own analysis). Old-328 is an older seed library with partial content overlap but was not the dataset the scorer was calibrated or evaluated against during development.
2. **Same failure mode is present in both datasets**, just at different net magnitudes. Zero-result and low-result rates worsen on old-328 too — the direction of the core regression (simple literal-noun/demographic queries losing precision) reproduces here, even though the net PASS/FAIL movement happens to come out positive on this particular 328-query mix.
3. **No individual metric on old-328 clears the bar the task's own gates require** ("V2 must be unambiguously better with no serious functional regression, not obtained by trading zero-result/FAIL for a small mean-score gain") — zero-result rate is explicitly named as a metric that must not worsen, and it worsens here too.

**Combined reading (326 + 328, 654 total queries)**: mixed-to-negative. 326 alone is net negative on every headline metric. 328 alone is net positive on score/PASS/FAIL but net negative on zero-result/low-result — the exact failure signature already diagnosed. No combined-dataset number changes the qualitative conclusion: V2-R1's scorer configuration has not achieved an unambiguous net improvement over V0 and still exhibits the same regression pattern on precision-sensitive simple queries.
