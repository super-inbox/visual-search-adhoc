# Curify Search Relevance Summary — 2026-07-07

## Overview

This report covers the first-round Curify search execution against the 68-query gold eval set (`gold_query_test_set_2026-07-07.csv`), captured in `curify_search_auto_collect_2026-07-07.csv`. All 68 executed rows were read, summarized, and given a first-pass relevance label based on available metadata (title, tag, and type text for the top 10 results, plus Curify's own `auto_flags`). No screenshots were visually inspected for this pass — labels are inferred from result text only, so this is a **first-pass, metadata-only** relevance audit, not a final human-verified grading.

Outputs from this pass:
- `curify_search_auto_collect_with_claude_relevance_2026-07-07.csv` — the original 68 rows plus 5 new columns (`claude_relevance_label`, `claude_issue_type`, `claude_relevance_reason`, `claude_confidence`, `recommended_manual_review_priority`).
- This file.

## Search Execution Metrics

| Metric | Value |
|---|---|
| Total executed queries | 68 |
| Average `visible_result_count` | 7.26 |
| Median `visible_result_count` | 10 |
| Min / Max `visible_result_count` | 0 / 10 |
| Zero-result queries (`count == 0`) | 11 (16.2%) |
| Low-result queries (`count <= 3`, includes the 11 zero-result rows) | 14 (20.6%) |
| `needs_human_review == yes` | 68 (100%) |

**Distribution by `primary_scene`**

| Scene | Count |
|---|---|
| 品牌 (brand) | 19 |
| 营销电商 (marketing/e-commerce) | 18 |
| 教育 (education) | 17 |
| 文创 (cultural/creative) | 14 |

**Distribution by `secondary_scene`**

| Scene | Count |
|---|---|
| 文创 (cultural/creative) | 26 |
| 营销电商 (marketing/e-commerce) | 19 |
| 品牌 (brand) | 18 |
| (empty) | 5 |

**Distribution by `planned_test_type`**

| Type | Count |
|---|---|
| content_gap | 24 |
| recall | 18 |
| both | 16 |
| filtering | 10 |

**Distribution of Curify's own `auto_flags`** (source data, multi-label — a row can carry more than one flag, so counts exceed 68)

| Flag | Count |
|---|---|
| possible_filtering_issue | 42 |
| query_broadened_by_curify | 36 |
| zero_result | 11 |
| low_result | 2 |
| (no flag) | 2 |

Curify itself flagged a relevance or filtering concern (`possible_filtering_issue` and/or `query_broadened_by_curify`) on the large majority of rows — only 2 of 68 rows came back with no auto-flag at all. That is consistent with the FAIL/WARN-heavy distribution below.

## Claude Relevance Label Distribution

| Label | Count | % |
|---|---|---|
| FAIL | 43 | 63.2% |
| WARN | 25 | 36.8% |
| PASS | 0 | 0% |
| UNKNOWN | 0 | 0% |

No row was labeled PASS. Every row had at least a partial mismatch, a content-type gap, or (for 11 rows) zero results — this first-pass metadata read did not find a single query where the top-10 titles cleanly and fully matched query intent with no caveats. This is a genuine finding, not an artifact of harsh grading: it lines up with Curify's own `possible_filtering_issue`/`query_broadened_by_curify` flags being present on 66 of 68 rows.

**Confidence distribution:** high = 37, medium = 30, low = 1. Most FAIL labels (zero-result and totally-unrelated-titles cases) carry high confidence, since these are easy to judge from title text alone without seeing the actual images. WARN labels are mostly medium confidence, since they depend on judging partial/structural relevance from titles rather than a visual check.

**Recommended manual review priority:** P0 = 42, P1 = 26, P2 = 0.

## Issue Type Distribution

(multi-label — a row can carry more than one issue tag)

| Issue type | Count |
|---|---|
| bad_relevance | 48 |
| wrong_decomposition | 29 |
| missing_content_type | 22 |
| competitor_gap | 18 |
| zero_result | 11 |
| content_gap | 4 |
| low_result | 3 |
| safety_risk | 1 |
| available_but_not_retrieved | 0 |
| gallery_under_recall | 0 (see [Gallery Image Recall Observations](#gallery-image-recall-observations)) |

Note: `zero_result` (11) and `low_result` (3) here are the specific issue-type *tags* used per-row (zero-result rows are tagged `zero_result` only, not double-tagged `low_result`). This is different from the "low-result queries" execution metric above, which mechanically counts all rows with `visible_result_count <= 3` (14 rows, including the 11 zero-result ones).

`wrong_decomposition` (29 rows) is the single most actionable pattern: Curify's query understanding repeatedly locks onto one generic word inside a longer/qualified query (e.g. "dream" out of "NCT Dream", "space" out of "maker space", "moodboard" out of "dreamcore aesthetic moodboard") and drops the qualifying context, returning generic or wildly unrelated content.

## Zero-Result Queries (11)

| Query | Scene | planned_test_type | Source priority |
|---|---|---|---|
| Amazon EBC enhanced brand content layout | 营销电商 | recall | P0 |
| Amazon Vine review request insert card | 营销电商 | recall | P0 |
| TikTok GRWM product placement mockup | 营销电商 | filtering | P0 |
| 亚马逊A+页面模块设计 | 营销电商 | both | P0 |
| 社群接龙团购价目表 | 营销电商 | content_gap | P0 |
| 私域用户运营SOP流程图 | 营销电商 | content_gap | P0 |
| 私域裂变任务宝海报 | 营销电商 | content_gap | P0 |
| RTI intervention tracker template | 教育 | recall | P0 |
| WIDA can-do descriptors chart | 教育 | recall | P0 |
| first then board autism | 教育 | content_gap | P0 |
| sub tub emergency lesson plan folder cover | 教育 | content_gap | P1 |

Notably, **7 of 11 zero-result queries are marketing/e-commerce operational assets** (Amazon EBC/A+/Vine, private-domain/community group-buy operations content). This looks like a genuine content-category gap rather than a query-parsing failure — these are operational/e-commerce-workflow asset types (compliance inserts, SOP flowcharts, page-module layouts) that may simply not exist in Curify's template library yet, as opposed to a recognition failure on a well-covered subject.

## Low-Result Queries (1–3 results)

| Query | Scene | visible_result_count |
|---|---|---|
| Amazon brand story module design | 营销电商 | 2 |
| 亚马逊评论截图水印素材 | 营销电商 | 2 |
| IEP accommodations checklist visual | 教育 | 3 |

All three are also FAIL-labeled — low count and weak title relevance co-occur here.

## P0 Manual Review Cases (42)

Sorted zero-result first, then ascending by `visible_result_count`.

| # | Query | Scene | Vis. Count | Label | Issue Type(s) | Confidence |
|---|---|---|---|---|---|---|
| 1 | Amazon EBC enhanced brand content layout | 营销电商 | 0 | FAIL | zero_result | high |
| 2 | Amazon Vine review request insert card | 营销电商 | 0 | FAIL | zero_result | high |
| 3 | TikTok GRWM product placement mockup | 营销电商 | 0 | FAIL | zero_result | high |
| 4 | 亚马逊A+页面模块设计 | 营销电商 | 0 | FAIL | zero_result | high |
| 5 | 社群接龙团购价目表 | 营销电商 | 0 | FAIL | zero_result | high |
| 6 | 私域用户运营SOP流程图 | 营销电商 | 0 | FAIL | zero_result | high |
| 7 | 私域裂变任务宝海报 | 营销电商 | 0 | FAIL | zero_result | high |
| 8 | RTI intervention tracker template | 教育 | 0 | FAIL | zero_result | high |
| 9 | WIDA can-do descriptors chart | 教育 | 0 | FAIL | zero_result | high |
| 10 | first then board autism | 教育 | 0 | FAIL | zero_result | high |
| 11 | sub tub emergency lesson plan folder cover | 教育 | 0 | FAIL | zero_result | high |
| 12 | Amazon brand story module design | 营销电商 | 2 | FAIL | low_result;bad_relevance | medium |
| 13 | IEP accommodations checklist visual | 教育 | 3 | FAIL | low_result;bad_relevance;missing_content_type;competitor_gap | medium |
| 14 | Love and Deepspace card pack design | 文创 | 4 | FAIL | bad_relevance;wrong_decomposition | high |
| 15 | dreamcore aesthetic moodboard | 文创 | 4 | FAIL | wrong_decomposition;bad_relevance | high |
| 16 | 二手奢侈品鉴定品牌视觉 | 品牌 | 4 | FAIL | bad_relevance;wrong_decomposition | medium |
| 17 | 小红书香薰产品种草图 | 营销电商 | 4 | FAIL | bad_relevance;wrong_decomposition | high |
| 18 | 国货美妆联名限定包装 | 品牌 | 5 | FAIL | bad_relevance;missing_content_type | medium |
| 19 | genshin impact Furina fanart wallpaper 4k | 文创 | 6 | FAIL | wrong_decomposition;bad_relevance;competitor_gap | high |
| 20 | 手冲咖啡工作室视觉手册 | 品牌 | 8 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 21 | NCT Dream photocard template | 文创 | 10 | FAIL | wrong_decomposition;bad_relevance;competitor_gap | high |
| 22 | weirdcore aesthetic sticker design | 文创 | 10 | FAIL | wrong_decomposition;bad_relevance | high |
| 23 | 低饱和国风茶包装设计 | 文创 | 10 | FAIL | wrong_decomposition;bad_relevance;missing_content_type | high |
| 24 | 光与夜之恋 卡面设计参考图 | 文创 | 10 | FAIL | wrong_decomposition;bad_relevance;competitor_gap | high |
| 25 | 故障艺术风格海报 | 文创 | 10 | FAIL | bad_relevance;wrong_decomposition | high |
| 26 | K-beauty glass skin brand launch visual | 品牌 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 27 | Y2K chrome skincare launch poster | 品牌 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 28 | clean girl aesthetic skincare packaging mockup | 品牌 | 10 | FAIL | bad_relevance;missing_content_type;wrong_decomposition | high |
| 29 | 儿童安全座椅品牌视觉 | 品牌 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 30 | 宠物摄影工作室品牌设计 | 品牌 | 10 | FAIL | bad_relevance;wrong_decomposition;missing_content_type | high |
| 31 | 家用医疗器械品牌设计 | 品牌 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 32 | 手工皂工作室品牌视觉 | 品牌 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 33 | 美妆博主个人IP视觉设计 | 品牌 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 34 | 小红书图文笔记模板 数字标题 | 营销电商 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 35 | 小红书探店打卡九宫格 | 营销电商 | 10 | FAIL | bad_relevance;missing_content_type;wrong_decomposition | medium |
| 36 | Gen Alpha slang classroom poster | 教育 | 10 | FAIL | bad_relevance;wrong_decomposition;missing_content_type | medium |
| 37 | charlotte mason copywork printable | 教育 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 38 | coding unplugged activity cards | 教育 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 39 | loop schedule homeschool printable | 教育 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 40 | maker space label set printable | 教育 | 10 | FAIL | wrong_decomposition;bad_relevance;missing_content_type | high |
| 41 | newcomer welcome kit printable | 教育 | 10 | FAIL | bad_relevance;wrong_decomposition;competitor_gap | high |
| 42 | zones of regulation poster classroom | 教育 | 10 | FAIL | bad_relevance;wrong_decomposition;missing_content_type;competitor_gap | high |

All 42 P0 rows are FAIL-labeled. No WARN row was elevated to P0 in this pass — WARN rows (partial/structural relevance) were left at P1.

## Representative Bad Relevance Cases

- **NCT Dream photocard template** (文创, 10 results, high confidence) — every title matched on the generic word "dream" ("Dream of the Red Chamber" ×3, "dream career") instead of the K-pop group NCT Dream. Classic keyword-collision decomposition failure.
- **maker space label set printable** (教育, 10 results, high confidence) — matched generic "space" (outer space/astronomy: "astronaut space," "Indian Manned Space") instead of "maker space" (STEM workshop). Same failure pattern, different domain.
- **genshin impact Furina fanart wallpaper 4k** (文创, 6 results, high confidence) — returned Studio Ghibli film stills and generic "media-themed wallpaper" templates; no Genshin Impact content at all.
- **低饱和国风茶包装设计** (文创, tea packaging, 10 results, high confidence) — returned generic food products (oats, cookies, pasta sauce); nothing related to tea or Chinese-style packaging.
- **手冲咖啡工作室视觉手册** (品牌, pour-over coffee studio manual, 8 results, high confidence) — returned ethnic-costume boards and anime-studio comparison content; nothing related to coffee or brand manuals.
- **小红书图文笔记模板 数字标题** (营销电商, Xiaohongshu note template, 10 results, high confidence) — returned post-office imagery, Journey to the West characters, and MBTI train comparisons; no Xiaohongshu template format.

## Gallery Image Recall Observations

The labeling rule for `gallery_under_recall` (flag when a moodboard/aesthetic/wallpaper/visual-reference query returns no gallery-type result) could not be applied as literally specified: `top_10_result_types` in this dataset only ever contains the values `inspiration` and `template` — there is no distinct `gallery` type value to check against. Under a literal reading, this issue tag never fires (0 rows), because almost every non-zero-result row includes at least one `inspiration`-typed entry.

This is a **measurement limitation, not a clean bill of health**. Several moodboard/aesthetic/wallpaper queries returned `inspiration`-typed results that were topically unrelated (e.g. `dreamcore aesthetic moodboard` returned brand-identity moodboards for a coffee shop, bakery, and grocery store — technically "inspiration" type, but not remotely dreamcore-themed). The `inspiration` type tag guarantees a *format* (a gallery-style image result), not topical relevance. Queries worth a manual visual/gallery-recall check specifically:
- dreamcore aesthetic moodboard
- weirdcore aesthetic sticker design
- genshin impact Furina fanart wallpaper 4k
- 松弛感生活方式插画 (relaxed lifestyle illustration)
- heritage brand rebrand moodboard
- dress to impress historical royalty outfit inspo

**Recommendation:** treat gallery/image recall as a separate analysis pass that requires opening the screenshots (or the live result grid), not something derivable from the `top_10_result_types` column as currently populated.

## Safety-Risk Observations

One query matched a safety-risk trigger term from the given list:

- **宠物殡葬服务品牌视觉设计** (pet funeral service brand visual design) — matches the "funeral" trigger keyword. Context is a commercial pet-industry service (pet funeral/memorial branding), not human funeral, sexual, medical-disease, or violent content — lower severity than the trigger list implies at face value, but still recommend a standard content-moderation pass before this query (or its expansion siblings) is used in any auto-generation workflow. Results also showed no funeral/memorial-specific content (content gap), independent of the safety flag.

No other rows matched the listed trigger topics (sexual content, medical disease, skin disease, violence, body abnormality, sensitive culture/religion) under a literal keyword read. Note "医疗器械" (medical device, row 29) and "autism" (row 62) were deliberately **not** flagged — device branding and autism-support classroom tools are not "medical disease" or "body abnormality" per the given trigger list, and flagging them would overclaim.

## Recommended PR Candidate Directions

Mapping the issue-type distribution to fix categories:

- **NER / entity generalization** (drives most of the 29 `wrong_decomposition` cases) — proper nouns and IP/brand/franchise names (NCT Dream, Genshin Impact Furina, Love and Deepspace, 光与夜之恋) are getting decomposed into generic dictionary words instead of being recognized as named entities.
- **Chinese segmentation** — several Chinese compound queries (低饱和国风茶包装设计, 光与夜之恋 卡面设计参考图, 汉服马面裙叠穿灵感图) show signs of losing key qualifying phrases during tokenization.
- **Alias / synonym expansion** — fandom and platform-specific vocabulary (photocard, 应援色, GRWM, 小红书探店九宫格, EBC/A+ page) likely isn't mapped to Curify's internal taxonomy terms.
- **Multi-path retrieval** — the 22 `missing_content_type` cases (e.g. brand-identity queries returning only generic moodboards, never a packaging-mockup or logo-specific template) suggest a single retrieval path is being used regardless of the requested asset format; consider routing by `expected_content_type`.
- **Gallery image recall** — see dedicated section above; needs a distinct analysis pass with actual image inspection, not just type-tag presence.
- **Content ingestion / competitor gap** (18 `competitor_gap` cases, concentrated in Amazon-seller operational assets, K-pop/game-fandom IP, and homeschool/special-ed education content) — these look like genuine library gaps rather than retrieval bugs; may warrant content sourcing rather than a retrieval fix.

## Next Steps for Human Spot-Check and Competitor Screenshot Comparison

- Manually review the 68 collected Curify results (screenshots under `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/`), starting with the 42 P0 rows above.
- Fill in the existing `manual_relevant_count`, `manual_irrelevant_count`, `manual_recall_status`, `manual_filtering_status`, `manual_content_gap`, `manual_issue_type`, and `manual_notes` columns in the source CSV (still empty) to convert this metadata-only pass into a human-verified grading.
- Confirm or correct each `claude_relevance_label` / `claude_issue_type` against the actual screenshots, especially the WARN rows (25 rows, medium/low confidence) where the call depended on partial title-text signal.
- Specifically re-check: zero-result vs. low-result cases, bad-relevance cases, missing-content-type cases, available-but-not-retrieved cases (none detected this pass — worth confirming that's real and not a labeling gap), competitor-gap cases, and gallery/image under-recall cases (see dedicated section above).
- Prepare PR candidates for the six directions listed above (NER generalization, Chinese segmentation, alias expansion, semantic synonym replacement, multi-path retrieval, gallery image recall).
- Extract taxonomy / 3-tier ontology candidates from the expanded 1,118-query candidate pool (`docs/daily_report/7.7/EXPANDED_QUERY_EVAL_INDEX.md`), informed by which content types and niches this first round showed as under-covered (e-commerce operational assets, fandom/IP content, special-education/homeschool content, wellness/functional branding).
- Once the 68-query gold set is fully human-verified, use the results to decide which of the remaining ~1,050 candidate queries (files 02–05) should be executed in the next pressure-test round.
