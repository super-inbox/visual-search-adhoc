# V2-R3 Stage: Full Easy326 Gate Result

Date: 2026-07-20. Full data: `13_V2_R3_EASY326_RESULTS.csv` (326/326 V2-R3), `14_V0_V2_R1_V2_R3_EASY326_PAIRED.csv`
(3-way join), `15_V2_R3_EASY326_STATISTICAL_COMPARISON.md` (full statistical detail). This report applies the 15
gate conditions of charter §六 mechanically to that data.

## Headline numbers

| Version | PASS | PARTIAL | FAIL | UNJUDGABLE | Zero-result | Mean score |
|---|---:|---:|---:|---:|---:|---:|
| V0 | 26 | 94 | 200 | 6 | 17 | 15.89 |
| V2-R1 | 24 | 85 | 210 | 7 | 19 | 15.76 |
| V2-R3 | 36 | 80 | 206 | 4 | 23 | 17.05 |

V0→V2-R3: improved=44, regressed=47, unchanged=235.
V2-R1→V2-R3: improved=39, regressed=26, unchanged=261.

## Gate checklist (charter §六, all 15 conditions)

| # | Condition | Result | Basis |
|---:|---|---|---|
| 1 | V2-R3 PASS ≥ V0 PASS | **PASS** | 36 ≥ 26 |
| 2 | V2-R3 FAIL ≤ V0 FAIL | **FAIL** | 206 > 200 |
| 3 | V2-R3 zero-result ≤ V0 zero-result | **FAIL** | 23 > 17 (+6 net new zero-result vs V0) |
| 4 | V2-R3 improved ≥ regressed (vs V0) | **FAIL** | 44 < 47 |
| 5 | V2-R3 clearly better than V2-R1 | **MIXED** | R1→R3: PASS 24→36, FAIL 210→206, improved(39) > regressed(26), McNemar p≈0.006 (significant) — clearly better on relevance labels; but zero-result also rose 19→23 vs V2-R1 (5 net-new zero-result cases introduced this stage, §7 of statistical comparison) — not unambiguously better once zero-result is included |
| 6 | Original V2-R1 main regressions net-fixed | **PASS** | 50-query regression set: 17 fixed / 1 newly regressed / 32 unchanged (R1→R3) |
| 7 | Most of V2-R1's existing improvements preserved | **PASS** | 贴纸/咖啡馆菜单/吉祥物/coffee cup all label-unchanged-or-better R1→R3 (§5 of statistical comparison); flooding and broad-noise improvements both preserved (condition 8/9 below) |
| 8 | Broad-noise improvement preserved | **PASS** | 151→140→124, monotonically improving |
| 9 | Flooding improvement preserved | **PASS** | Flooding (≥200 results): 23→0→0. Preserved exactly. |
| 10 | No new full-catalog flooding | **PASS** | Full-catalog flooding (≥300): 9→0→0. None introduced. |
| 11 | Rewrite net-negative not expanded | **PASS** | Among 171 rewrite-triggered V2-R3 rows, R1→R3 improved=18 > regressed=14; net positive, not expanding negative |
| 12 | coffee cup / 贴纸 / 咖啡馆菜单 no severe label regression | **PASS** | All three label-unchanged R1→R3 in the full-326 live run (coffee cup FAIL→FAIL, 贴纸 PASS→PASS, 咖啡馆菜单 PARTIAL→PARTIAL) |
| 13 | No systemic Chinese/English regression | **PASS** | Both zh and en slices show PASS-rate improvement V0→R3 with no material FAIL-rate increase (§8 of statistical comparison) |
| 14 | No systemic single-word/multi-word regression | **PASS** | Both slices show PASS-rate improvement V0→R3 with no material FAIL-rate increase (§8 of statistical comparison) |
| 15 | Clear overall net improvement (not just a few cases) | **FAIL** | V0→R3 regressed(47) exceeds improved(44); none of the three statistical tests (McNemar, bootstrap, Wilcoxon) reach significance for V0→R3; zero-result count increased net vs V0 |

**Result: 4 of 15 conditions fail (#2, #3, #4, #15); #5 is mixed/not clearly satisfied.**

## Why this differs from the targeted-stage result

The targeted 63-case stage (`08_V2_R3_TARGETED_GATE_RESULT.md`, `FINAL_STATUS: V2_R3_TARGETED_FIX_COMPLETE`) passed
all 20 of its conditions. That stage's sample was a curated mix of calibration/holdout/protection cases selected
specifically to probe the two known root-cause mechanisms (A: original-template overpromotion, B: relaxed-score
sense-collision) and to protect known-good V2-R1 improvements. It was explicitly *not* a representative random
sample of the full 326-query bank, and its own §7 disclosed exactly this limitation ("Full-326 is authorized as
the next stage's task"). This full-326 run is the first time V2-R3's code runs against the **unrestricted** query
distribution, and it surfaces two effects the targeted sample structurally could not see:

1. **New zero-result cases outside the tested holdout/calibration/protection sets** (`online store banner`,
   `积分卡`, `证书`, `microscope` — §7 of the statistical comparison) — none of these 4 queries were in any of the
   63 targeted-stage rows, so the targeted stage had no way to detect them.
2. **A broader base rate of both new fixes and new regressions** that roughly cancel out at the FAIL/regressed
   level (V0→R3: 44 improved vs 47 regressed) even though the *targeted* mechanism-A/B cases the design was built
   around do clearly improve (§3, §4 of the statistical comparison: original 50-regression set nets +16;
   4/5 of the targeted-stage's own flagged new-regressions flip back to improved at full scale).

This is exactly the scenario charter §六 condition 15 exists to catch: real, measurable, mechanism-level fixes in
a subset of the query space, without a clear net improvement once evaluated against the full unrestricted
distribution — including a new failure mode (new zero-result cases) that the smaller stage's sample never had a
chance to exercise.

## Verdict

**FINAL_STATUS: NOT_READY_TO_REPLACE_PRODUCTION**

Per charter §六: this stage stops here. No Hard68, no old-328, no P0-12, no further parameter tuning, no code
changes, no push. The specific, reproducible new zero-result cases in §7 of the statistical comparison
(`online store banner`, `积分卡`, `证书`, `microscope`, plus the already-documented `算盘`) are the most concrete,
actionable finding for whoever picks this up next — they are not part of any previously-documented catalog-gap
exception list and directly contradict the stage's own stated "original non-empty results never cleared"
invariant when exercised outside the 63-case targeted sample.
