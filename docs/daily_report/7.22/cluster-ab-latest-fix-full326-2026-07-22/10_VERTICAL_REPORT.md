# Vertical / Category Performance — Full-326 Latest Candidate (0e794cd9)

Row data: `10_VERTICAL_SUMMARY.csv`. Categories are the benchmark's own `category` column (37 distinct labels) — not
invented for this report.

## Strongest verticals (latest candidate)
| category | n | PASS rate | notes |
|---|---:|---:|---|
| sticker | 4 | 100% | 4/4 PASS, 0 regressions either direction — clean win, untouched by Cluster A/B mechanisms. |
| mascot | 2 | 100% | 2/2 PASS. |
| poster_specific | 16 | 31.2% | Best-performing sizeable vertical; **+8 improvements vs. production**, only 1 regression — the strongest vertical-level evidence of net positive change. |
| package | 18 | 22.2% | **+6 improvements vs. previous candidate, 0 regressions vs. previous candidate** — this is the vertical where the Cluster-A format-word fix shows its clearest payoff (`coffee package`, `cosmetic package` moved out of FAIL). |
| promotion / logo / calendar / product_display / cup | 2-4 each | 25-50% | Small n, but positive or flat. |

## Weakest verticals (latest candidate)
| category | n | PASS rate | notes |
|---|---:|---:|---|
| banner | 28 | 0% | 19/28 FAIL, **+4 regressions vs. production** — the single worst vertical by regression count. Includes the disclosed-unfixed `black friday banner` (Marvel "Bruce Banner" collision) and related promo-banner queries. |
| stationery | 6 | 0% | **4/6 regressed vs. production** — contains the Cluster-B flagship `笔袋`/`pencil case` regression (both still FAIL, worse than production's PARTIAL), plus `信封` (envelope, PASS→PARTIAL) and `书签` (bookmark, UNJUDGABLE→FAIL). The vertical most directly tied to the fix that was supposed to help it, and it is net negative. |
| certificate | 8 | 0% | 3/8 zero-result, 2 regressions vs. production, 0 improvements. |
| classroom_material / worksheet / flyer | 10 each | 0-10% | Persistently weak; flyer has 2 zero-result queries. |
| chart | 14 | 21.4% | 9/14 FAIL, +3 regressions vs. production (worst regression count after banner/product_photo/figure). |
| figure / product_photo | 12 / 8 | 8-25% | Both show more regressions-vs-previous-candidate (4 each) than improvements — a **local regression pocket** worth a closer look outside this report's scope. |
| doll / globe / keychain / textbook / coupon | 2 each | 0% | Small-n categories with no wins; `coupon` has both queries zero-result. |

## Reading across the two "core areas" the charter calls out
- **Education/classroom** (classroom_material, worksheet, flashcard, chart, textbook, flyer): mixed-to-weak. Only
  flashcard shows a clean local win (+4 improvements, 1 regression vs. production); worksheet/classroom_material/chart
  remain largely FAIL-dominated. Largely **catalog-content-gap and insufficient-evidence** territory per
  `12_REMAINING_FAILURE_ROOT_CAUSES.csv`, not a single fixable scorer mechanism.
- **Commercial/graphic design, poster/info design** (banner, poster_specific, flyer, advertisement, signage): a split
  picture — poster_specific is the strongest vertical in the whole benchmark, while banner is the weakest. This
  mirrors the Cluster-A doc's own disclosure that the coverage-gate/isolated-hit-cap mechanism "helps some multi-term
  promo queries and hurts adjacent ones."
- **Sticker/label/product-label design**: sticker is a clean 100% win; label is middling (12.5% pass, 2 zero-result,
  net +3 improvements vs. previous candidate) — 酒标 (wine label, ZH) sits in this category and remains unresolved
  (see Cluster A analysis).
- **Merchandise/toy/plush/character/collectible**: merch_item and collectible show small net improvements; plush,
  doll, character, keychain, textbook are all-FAIL small-n categories with no evidence of movement either direction —
  likely catalog-content-gap-dominated, not a search-logic problem this fix cycle could address.
- **Menu, certificate, membership-card, cup, packaging**: membership_card (6 queries, incl. `会员卡`/`积分卡`) is a
  genuine mixed bag — one flagship zero-result case recovered (`积分卡`), the sibling case did not (`会员卡`); package
  is a strong-improvement vertical; certificate remains uniformly weak with 3 zero-result queries and no improvements
  in either comparison.

## Separating relevance failures from catalog/content gaps/ambiguity (vertical-level read)
- **Likely genuine search-relevance issues** (movement seen between runs, same catalog): banner, stationery, chart,
  figure, product_photo — these verticals show real regressions/improvements as the scorer changed, meaning the
  catalog has relevant content but ranking/filtering logic determines whether it surfaces.
- **Likely catalog/content gaps** (flat FAIL/zero across all three runs regardless of scorer version): doll, globe,
  keychain, textbook, coupon, and most of certificate — no version of the scorer tested here (main, R1-pre-fix,
  latest) produces a PASS, suggesting the relevant template content may not exist or is too sparse, independent of
  ranking logic. These are the categories to hand to the separate template-discovery task.
