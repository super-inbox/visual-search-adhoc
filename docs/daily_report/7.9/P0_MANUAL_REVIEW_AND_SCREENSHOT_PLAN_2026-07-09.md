# P0 Manual Review and Screenshot Plan — 2026-07-09

## Overview

This document turns the Claude first-pass relevance labeling (Task 3, done on 2026-07-08) into an actionable manual-review plan. Of the 68 executed Curify search queries, **42 are flagged `recommended_manual_review_priority = P0`** — all of them are `claude_relevance_label = FAIL` cases carrying at least one of the issue types called out in the task: `zero_result`, `low_result`, `bad_relevance`, `wrong_decomposition`, `missing_content_type`, or `competitor_gap`. (`gallery_under_recall` did not occur in any of the 68 rows — see [Gallery image recall](#screenshot-availability-check) note below.)

This plan:
- Prioritizes the 42 P0 cases into a review order (zero-result → low-result → high-confidence `wrong_decomposition` → high-confidence `bad_relevance` → `missing_content_type`/`competitor_gap`).
- Confirms which of the 68 Curify screenshots already captured on 2026-07-07 exist on disk, so no re-capture is needed for that side of the comparison.
- Flags which P0 cases most need a competitor screenshot (Pinterest / Canva / Bing / Google) to confirm whether Curify is missing content that competitors surface.
- Checks the 68-query set for the 8 queries mentioned in the product meeting, and reports what related coverage exists today.

No production code was touched. No files were staged or committed. This document does not replace or duplicate the earlier `CURIFY_SEARCH_RELEVANCE_SUMMARY_2026-07-07.md` — it is the human-review action layer on top of it.

## Input Files

| File | Role |
|---|---|
| `docs/daily_report/7.9/curify_search_auto_collect_with_claude_relevance_2026-07-07.csv` | Enriched 68-row execution + Claude relevance dataset (source of truth for this plan). |
| `docs/daily_report/7.9/CURIFY_SEARCH_RELEVANCE_SUMMARY_2026-07-07.md` | Prior relevance summary (label/issue distributions, zero/low-result lists) — cross-checked against, not duplicated here. |
| `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/` | 68 Curify screenshots captured during the original 2026-07-07 execution run; checked for existence per row. |

## P0 Manual Review Summary

- **Total executed queries:** 68
- **P0 (FAIL, high-priority) cases:** 42 (62%)
- **P1 (WARN, lower-priority) cases:** 26 (38%) — out of scope for this plan; see the relevance summary doc.
- **P0 confidence split:** high = 36, medium = 6 (no low-confidence P0 cases — Claude only escalated to P0 when reasonably sure of the mismatch).
- **P0 review-order bucket breakdown:**

| Bucket (review order) | Count |
|---|---|
| 1. Zero-result | 11 |
| 2. Low-result (≤3 visible results) | 2 |
| 3. High-confidence `wrong_decomposition` | 28 |
| 4. High-confidence `bad_relevance` (not already in 1–3) | 1 |
| 5. `missing_content_type` / `competitor_gap` (not already in 1–4) | 0 |

Bucket 5 is 0 because every P0 case carrying `missing_content_type` or `competitor_gap` also carries `wrong_decomposition` or `bad_relevance`, so it was already captured upstream in the review order — no case is *only* a content-type/competitor-gap issue at P0.

- **P0 issue-type frequency** (a case can carry multiple tags): `bad_relevance` 31, `wrong_decomposition` 28, `competitor_gap` 17, `missing_content_type` 9, `zero_result` 11, `low_result` 2.
- **Safety note:** the one `safety_risk`-tagged row in the full 68 (`宠物殡葬服务品牌视觉设计` — pet funeral/memorial service branding) is `WARN`/P1, not P0, so it does not appear in the tables below. It is still worth a light manual glance given the sensitive-topic rule, but it is not a search-relevance emergency.

## Top P0 Cases

Full detail (all 10 required columns) for the **top 20** highest-priority P0 cases, in review order:

| # | query | primary_scene | secondary_scene | visible_result_count | claude_relevance_label | claude_issue_type | claude_relevance_reason | claude_confidence | screenshot_path | screenshot_exists | suggested_human_check | suggested_competitor_screenshots |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Amazon EBC enhanced brand content layout | 营销电商 | 品牌 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/034_marketing_amazon_ebc_enhanced_brand_content_layout.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 2 | Amazon Vine review request insert card | 营销电商 | 品牌 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/035_marketing_amazon_vine_review_request_insert_card.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 3 | RTI intervention tracker template | 教育 | 文创 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/055_education_rti_intervention_tracker_template.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 4 | TikTok GRWM product placement mockup | 营销电商 | 品牌 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/037_marketing_tiktok_grwm_product_placement_mockup.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 5 | WIDA can-do descriptors chart | 教育 | — | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/057_education_wida_can_do_descriptors_chart.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 6 | first then board autism | 教育 | 文创 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/062_education_first_then_board_autism.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 7 | sub tub emergency lesson plan folder cover | 教育 | 品牌 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/066_education_sub_tub_emergency_lesson_plan_folder_cover.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 8 | 亚马逊A+页面模块设计 | 营销电商 | 品牌 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/038_marketing_a.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 9 | 社群接龙团购价目表 | 营销电商 | 品牌 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/049_marketing_.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 10 | 私域用户运营SOP流程图 | 营销电商 | 品牌 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/050_marketing_sop.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 11 | 私域裂变任务宝海报 | 营销电商 | 品牌 | 0 | FAIL | zero_result | Zero results returned for this query. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/051_marketing_.png` | Yes | Confirm true zero-result in live UI; check for typo/segmentation issue or missing alias/synonym. | Pinterest, Bing, Google |
| 12 | Amazon brand story module design | 营销电商 | 品牌 | 2 | FAIL | low_result;bad_relevance | Only 2 results; 'Brand IP Full Design Display Board' is loosely on-topic but 'capybara jiangyuan' is an unrelated character IP. | medium | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/036_marketing_amazon_brand_story_module_design.png` | Yes | Confirm low result count live; assess whether backend under-retrieves vs. inventory is genuinely sparse. Manually inspect top-10 results against query intent; confirm mismatch is systemic vs. an isolated ranking issue. | Pinterest, Canva, Bing, Google |
| 13 | IEP accommodations checklist visual | 教育 | 文创 | 3 | FAIL | low_result;bad_relevance;missing_content_type;competitor_gap | Only 3 results; 'Men's Lifestyle Step Guide' templates loosely match the checklist format but the subject is unrelated to IEP/special-education accommodations. | medium | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/053_education_iep_accommodations_checklist_visual.png` | Yes | Confirm low result count live; assess whether backend under-retrieves vs. inventory is genuinely sparse. Manually inspect top-10 results against query intent; confirm mismatch is systemic vs. an isolated ranking issue. Verify expected content type is present in top results. | Pinterest, Canva, Bing, Google |
| 14 | Love and Deepspace card pack design | 文创 | 营销电商 | 4 | FAIL | bad_relevance;wrong_decomposition | Top results (Velociraptor, generic sports equipment cards) do not match 'Love and Deepspace' card pack design intent; query appears mis-decomposed to a generic 'card' concept. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/001_cultural_love_and_deepspace_card_pack_design.png` | Yes | Inspect query segmentation/NER decomposition; verify key tokens (IP name, style qualifier) were not dropped. Manually inspect top-10 results against query intent. | Pinterest, Canva, Google |
| 15 | dreamcore aesthetic moodboard | 文创 | 品牌 | 4 | FAIL | wrong_decomposition;bad_relevance | Results are generic F&B brand-identity moodboards, not 'dreamcore aesthetic' mood content; only 4 results returned. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/004_cultural_dreamcore_aesthetic_moodboard.png` | Yes | Inspect query segmentation/NER decomposition; verify key tokens (style qualifier) were not dropped. Manually inspect top-10 results against query intent. | Pinterest, Canva, Google |
| 16 | 小红书香薰产品种草图 | 营销电商 | 文创 | 4 | FAIL | bad_relevance;wrong_decomposition | Only 4 results, none related to aromatherapy/香薰 products. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/046_marketing_.png` | Yes | Inspect query segmentation/NER decomposition; verify "香薰" token was not dropped. Manually inspect top-10 results against query intent. | Pinterest, Canva, Google |
| 17 | genshin impact Furina fanart wallpaper 4k | 文创 | — | 6 | FAIL | wrong_decomposition;bad_relevance;competitor_gap | Returned Studio Ghibli film stills and generic 'media-themed wallpaper' templates instead of any Genshin Impact/Furina content; likely IP content gap. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/006_cultural_genshin_impact_furina_fanart_wallpaper_4k.png` | Yes | Inspect query segmentation/NER decomposition; verify IP name was not dropped. Capture on Pinterest/Canva/Bing/Google to confirm competitor coverage. | Pinterest, Canva, Google |
| 18 | 手冲咖啡工作室视觉手册 | 品牌 | 营销电商 | 8 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | Results are ethnic-group and anime-studio-comparison content; nothing related to coffee or brand visual manuals. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/030_brand_.png` | Yes | Inspect query segmentation/NER decomposition. Capture on Pinterest/Canva/Bing/Google to confirm competitor coverage. | Pinterest, Canva, Google |
| 19 | K-beauty glass skin brand launch visual | 品牌 | 营销电商 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | Results are unrelated consumer product categories (eyemask, speaker, coffee maker); no K-beauty brand-launch visual content. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/015_brand_k_beauty_glass_skin_brand_launch_visual.png` | Yes | Inspect query segmentation/NER decomposition. Capture on Pinterest/Canva/Bing/Google to confirm competitor coverage. | Pinterest, Canva, Google |
| 20 | NCT Dream photocard template | 文创 | 营销电商 | 10 | FAIL | wrong_decomposition;bad_relevance;competitor_gap | Results matched on the generic word 'dream' (Dream of the Red Chamber, dream career) instead of the NCT Dream K-pop IP; no photocard template content returned. | high | `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/002_cultural_nct_dream_photocard_template.png` | Yes | Inspect query segmentation/NER decomposition; verify IP name was not dropped. Capture on Pinterest/Canva/Bing/Google to confirm competitor coverage. | Pinterest, Canva, Google |

Remaining P0 cases (21–42), compact form — full reason/human-check text for these is in the enriched CSV:

| # | query | primary_scene | secondary_scene | visible_result_count | claude_issue_type | claude_confidence | screenshot_exists |
|---|---|---|---|---|---|---|---|
| 21 | Y2K chrome skincare launch poster | 品牌 | 营销电商 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 22 | charlotte mason copywork printable | 教育 | 文创 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 23 | clean girl aesthetic skincare packaging mockup | 品牌 | 营销电商 | 10 | bad_relevance;missing_content_type;wrong_decomposition | high | Yes |
| 24 | coding unplugged activity cards | 教育 | 文创 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 25 | loop schedule homeschool printable | 教育 | 文创 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 26 | maker space label set printable | 教育 | 文创 | 10 | wrong_decomposition;bad_relevance;missing_content_type | high | Yes |
| 27 | newcomer welcome kit printable | 教育 | — | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 28 | weirdcore aesthetic sticker design | 文创 | 品牌 | 10 | wrong_decomposition;bad_relevance | high | Yes |
| 29 | zones of regulation poster classroom | 教育 | 文创 | 10 | bad_relevance;wrong_decomposition;missing_content_type;competitor_gap | high | Yes |
| 30 | 低饱和国风茶包装设计 | 文创 | 品牌 | 10 | wrong_decomposition;bad_relevance;missing_content_type | high | Yes |
| 31 | 儿童安全座椅品牌视觉 | 品牌 | 营销电商 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 32 | 光与夜之恋 卡面设计参考图 | 文创 | 营销电商 | 10 | wrong_decomposition;bad_relevance;competitor_gap | high | Yes |
| 33 | 宠物摄影工作室品牌设计 | 品牌 | 营销电商 | 10 | bad_relevance;wrong_decomposition;missing_content_type | high | Yes |
| 34 | 家用医疗器械品牌设计 | 品牌 | 营销电商 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 35 | 小红书图文笔记模板 数字标题 | 营销电商 | 文创 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 36 | 手工皂工作室品牌视觉 | 品牌 | 营销电商 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 37 | 故障艺术风格海报 | 文创 | 品牌 | 10 | bad_relevance;wrong_decomposition | high | Yes |
| 38 | 美妆博主个人IP视觉设计 | 品牌 | 文创 | 10 | bad_relevance;wrong_decomposition;competitor_gap | high | Yes |
| 39 | 二手奢侈品鉴定品牌视觉 | 品牌 | 营销电商 | 4 | bad_relevance;wrong_decomposition | medium | Yes |
| 40 | Gen Alpha slang classroom poster | 教育 | 文创 | 10 | bad_relevance;wrong_decomposition;missing_content_type | medium | Yes |
| 41 | 小红书探店打卡九宫格 | 营销电商 | 文创 | 10 | bad_relevance;missing_content_type;wrong_decomposition | medium | Yes |
| 42 | 国货美妆联名限定包装 | 品牌 | 文创 | 5 | bad_relevance;missing_content_type | medium | Yes |

## Screenshot Availability Check

Checked `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/` (68 files, named `<row_index>_<primary_scene_slug>_<query_slug>.png`) against the `screenshot_path` column of every row in the enriched CSV.

- **68 / 68 rows** (100%) have a matching screenshot file on disk — including all 42 P0 rows.
- No re-capture of Curify's own results is needed before manual review; every P0 case can be reviewed directly from the existing screenshot plus the `search_url` in the CSV if a live re-check is wanted.
- A handful of filenames rendered with an empty query slug (e.g. `009_cultural_.png`, `028_brand_.png`, `049_marketing_.png`) because the slugifier dropped non-ASCII (Chinese) query text — this is a cosmetic naming artifact only; the files exist and are correctly indexed to their row via the CSV's `screenshot_path` column, so it does not block review.
- **Gallery-image recall:** the `gallery_under_recall` issue type did not fire on any of the 68 rows (0 occurrences), including on inspiration/moodboard-style queries like `dreamcore aesthetic moodboard`. Those cases were tagged `wrong_decomposition`/`bad_relevance` instead — the query was mis-matched to the wrong subject entirely, not merely missing the gallery image type within an otherwise on-topic result set. Gallery recall specifically is not a driver of P0 volume in this round.

## Cases Needing Competitor Screenshots

17 of the 42 P0 cases (40%) carry `competitor_gap`, meaning Claude's first-pass read suspects the content likely exists elsewhere but Curify isn't surfacing it — these are the highest-value targets for competitor screenshots, because a competitor hit would confirm a real retrieval gap rather than a genuine content gap:

- Amazon brand story module design
- IEP accommodations checklist visual
- genshin impact Furina fanart wallpaper 4k
- 手冲咖啡工作室视觉手册
- K-beauty glass skin brand launch visual
- NCT Dream photocard template
- Y2K chrome skincare launch poster
- charlotte mason copywork printable
- coding unplugged activity cards
- loop schedule homeschool printable
- newcomer welcome kit printable
- zones of regulation poster classroom
- 儿童安全座椅品牌视觉
- 光与夜之恋 卡面设计参考图
- 家用医疗器械品牌设计
- 小红书图文笔记模板 数字标题
- 手工皂工作室品牌视觉
- 美妆博主个人IP视觉设计

For the 11 zero-result and 2 low-result cases (buckets 1–2), competitor screenshots also matter but for a different reason: they test whether the query concept exists at all in the broader market (Pinterest/Google) versus being a genuinely novel/niche request no platform serves well.

Suggested competitor screenshot targets, applied per the `suggested_competitor_screenshots` column:
- **Pinterest** — always capture; primary visual-inspiration competitor benchmark.
- **Canva** — capture when the issue involves `bad_relevance`, `wrong_decomposition`, or `competitor_gap` (i.e., most of bucket 3+); Canva's template search is the closest functional analog to Curify.
- **Bing** — capture for `zero_result`, `low_result`, or `gallery_under_recall` cases, as Bing Images is a fast way to confirm whether the underlying visual concept exists anywhere online.
- **Google** — always capture as a general baseline (Google Images / Google Search) for whether the query concept has any real-world visual presence.

## Meeting-Mentioned Case Coverage

None of the 8 queries mentioned in the meeting exist verbatim in this 68-query gold set:

| Meeting-mentioned query | Exact match in 68-query set? | Closest related query tested | Related query's label / issue type |
|---|---|---|---|
| 早八穿搭插画 (early-morning outfit illustration) | No | `松弛感生活方式插画` (relaxed-lifestyle illustration) | WARN — bad_relevance;missing_content_type (P1) |
| 马建群 | No | — no related query in the set | — |
| 苏州平台 | No | — no related query in the set | — |
| skin care launch booster | No | `K-beauty glass skin brand launch visual`, `Y2K chrome skincare launch poster` | Both FAIL — bad_relevance;wrong_decomposition;competitor_gap (P0) |
| 香薰海报 (aromatherapy poster) | No | `小红书香薰产品种草图` (Xiaohongshu aromatherapy product image) | FAIL — bad_relevance;wrong_decomposition (P0) |
| classroom procedure poster set | No | `Gen Alpha slang classroom poster`, `zones of regulation poster classroom`, `behavior clip chart classroom`, `visual schedule strips autism classroom` | Mixed: 2 FAIL/P0 (`Gen Alpha slang classroom poster`, `zones of regulation poster classroom`), 2 WARN/P1 |
| parent communication with kids | No | — no related query in the set | — |
| challenge card | Partial (substring) | `STEM challenge card printable` | WARN — bad_relevance (P1) |

**Takeaway:** this gold set was built from a different query-expansion pipeline (see `docs/daily_report/7.9/EXPANDED_QUERY_EVAL_INDEX.md`) and does not directly cover the meeting's specific examples. Where a topically-adjacent query was tested, the pattern already visible in this data (skincare-launch and aromatherapy-poster analogs both FAIL/P0 on `bad_relevance;wrong_decomposition`) suggests the exact meeting queries would likely surface the same decomposition problems, but this is an inference, not a tested result — `马建群`, `苏州平台`, and `parent communication with kids` have no tested analog at all and should not be assumed to fail or pass. Recommend adding all 8 exact queries to the next test round rather than relying on the proxies above.

## Suggested Manual Review Workflow

1. **Work strictly in review-order buckets** (zero-result → low-result → high-confidence `wrong_decomposition` → high-confidence `bad_relevance` → `missing_content_type`/`competitor_gap`) using the Top P0 Cases table above; don't jump around.
2. **Per case:** open the screenshot at `screenshot_path` (all 42 confirmed present) side by side with the `search_url` from the enriched CSV (re-run live if the case is more than a few days old, to catch any index changes).
3. **For `competitor_gap`-flagged cases**, capture the same query on the suggested competitor targets (Pinterest / Canva / Bing / Google) and save alongside the Curify screenshot for a direct comparison — this is what confirms retrieval-gap vs. content-gap.
4. **Log the verdict back into the manual columns** of `docs/daily_report/7.9/curify_search_auto_collect_with_claude_relevance_2026-07-07.csv` (`manual_relevant_count`, `manual_irrelevant_count`, `manual_recall_status`, `manual_filtering_status`, `manual_content_gap`, `manual_issue_type`, `manual_notes`) — these are still empty and are the ground-truth signal that will confirm or correct Claude's first-pass label.
5. **Escalate immediately, out of normal order, if** a case's manual review surfaces anything matching the `safety_risk` rule (funeral, sexual content, medical/disease, violence, sensitive culture/religion) even if it wasn't auto-tagged that way — the auto-tagging is first-pass and may under-flag.
6. **After all 42 P0 cases are reviewed**, spot-check a sample of the 26 P1 cases to validate Claude's WARN calls before treating the P0/P1 split as final.

## Next Steps

- Complete human spot-check of the top 20 P0 cases first (bucket 1–2 zero/low-result, highest confidence bucket-3 items) before moving to the remaining 22.
- Capture competitor screenshots (Pinterest, Canva, Bing, Google) for the 17 `competitor_gap` cases and for all 13 zero/low-result cases; store alongside existing Curify screenshots for direct visual comparison.
- Add the 8 meeting-mentioned queries verbatim to the next gold-query test round — this set currently has no exact coverage for `马建群`, `苏州平台`, or `parent communication with kids`, and only proxy coverage for the others.
- Once manual columns are filled in for all 42 P0 cases, re-diff Claude's `claude_relevance_label`/`claude_issue_type` against the manual verdict to measure first-pass labeling precision before relying on Claude auto-labeling at larger scale.
- Do not write the consolidated work report until the manual spot-check pass above is complete — this plan is preparatory, not a final result.
