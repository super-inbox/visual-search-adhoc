# Zero / Low-Result Analysis — Full-326 Latest Candidate (0e794cd9)

Row-level data: `09_ZERO_LOW_RESULT_ANALYSIS.csv`. Definitions: zero-result = `total_results == 0`; low-result =
`0 < total_results < 5` (established methodology, unchanged from 7/19/7/21 runs).

## Headline counts
| | production baseline (c550856e) | previous candidate (1e56e3f0) | latest candidate (0e794cd9) |
|---|---:|---:|---:|
| zero-result | 23 | 20 | **20** |
| low-result | 19 | 13 | **18** |
| mean result count | 74.4 | 61.7 | **46.6** |
| median result count | 46.5 | 46.0 | **28.5** |
| max result count | 375 | 188 | 190 |

Zero-result count is unchanged in aggregate vs. previous candidate (20→20) but the **underlying set of queries is
different** (see transitions below) — aggregate parity hides real churn. Low-result count rose 13→18 (+5) vs.
previous candidate, and result-pool size (mean/median) continued shrinking, consistent with progressively tighter
filtering across the R1 → Fix B → Fix A lineage.

## Zero-result transitions vs. production baseline (c550856e)
- **New zero-result (2):** `会员卡` (membership card), `diploma` — both went from a large non-zero pool in production
  (368 and 101 results respectively) to **zero** in the latest candidate. `会员卡` was already zero in the previous
  candidate (not new relative to that run); `diploma` progressively shrank across all three runs (101 → 6 → 0) —
  see below.
- **Recovered zero-result (5):** `扭蛋`, `diorama`, `advertisement`, `折扣传单`, `数学练习册` — these were zero under
  production main and now return results under the latest candidate.
- Net zero-result vs. production: **-3** (23→20), a real improvement, but with 2 fresh holes underneath the net number.

## Zero-result transitions vs. previous candidate (1e56e3f0, pre-Cluster-A/B)
- **New zero-result (3):** `puzzle`, `优惠券`, `diploma`.
- **Recovered zero-result (3):** `bobblehead`, `场景模型`, `积分卡` — all three were flagged as "new zero-result"
  problems in the 2026-07-21 `scorer-v1.1` report (`REGRESSION_ANALYSIS.md`: *"New zero-result cases... `bobblehead`,
  `场景模型`, `会员卡`, `积分卡`"*). **`积分卡` in particular was explicitly called out as still-broken and a target of
  this fix cycle — it is now confirmed recovered** (production baseline also had it at FAIL/368-results, i.e. never a
  real production win either; the latest candidate returns 87 results and a PARTIAL judgment, a genuine improvement
  over both prior states).
- `会员卡` (the other flagged 7/21 new-zero case) is **still zero** in the latest candidate — not fixed.
- Net zero-result vs. previous candidate: flat (20→20), but 3 fixed / 3 broken — a wash in count, not in identity.

## `diploma` — flagged regression, needs attention
| run | total_results | label |
|---|---:|---|
| production baseline | 101 | FAIL |
| previous candidate | 6 | FAIL |
| **latest candidate** | **0** | **FAIL** |
Result count collapsed monotonically across all three versions and is now zero. It was FAIL in all three runs (never
a production win to protect), but the trend line (101→6→0) suggests progressively more aggressive filtering is
starving this query of any candidates at all, independent of the Cluster A/B mechanisms specifically. Likely
**candidate-loss regression** (see `12_REMAINING_FAILURE_ROOT_CAUSES.csv`), not a catalog gap — production main
did return 101 items for it, so matching content exists in the catalog.

## Low-result transitions vs. production baseline
- **Newly low-result (8):** `statue`, `coffee bean package`, `礼品盒`, `购物袋`, `咖啡杯`, `饮料瓶`, `advertisement`, `pencil case`.
- **Resolved low-result (9):** `娃娃`, `capsule toy`, `潮流公仔`, `潮流手办`, `mystery box`, `bobblehead`, `soap package`,
  `drink bottle`, `荣誉证书`.
- `pencil case` appearing in the newly-low-result list is consistent with the Cluster-B flagship regression (see
  `11_CLUSTER_AB_OUTCOME_ANALYSIS.md`) — its result pool shrank from 21 (production) to 3 (latest), now both
  low-result AND still FAIL.

## Likely reasons for new zero/low cases (inference from row-level fields only)
- `diploma`, `会员卡`: large production pools collapsing to zero across successive candidate iterations — pattern
  matches progressively stricter multi-path/coverage filtering (candidate loss), not a query-ambiguity or genuine
  content-gap signature (production DID find matching content).
- `puzzle`, `优惠券`: newly zero only vs. the previous candidate, not vs. production main — narrower regression window,
  same candidate-loss shape.
- No new zero/low case in this run shows evidence of a rewrite-suppression signature (`rewrite_triggered=false` on
  all four new-zero queries in `eval_raw/CANDIDATE_LATEST_EASY326.csv`), so rewrite suppression is not the likely
  mechanism here; execution error is ruled out (`ok=true`, `collect_error` empty on all four).
