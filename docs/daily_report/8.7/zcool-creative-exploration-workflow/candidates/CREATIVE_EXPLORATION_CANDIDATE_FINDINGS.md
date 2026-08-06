# Creative Exploration Candidate Findings — Phase 5 (Small-Scale Targeted Candidate Screening)

Scope: small-scale, targeted discovery and screening of *new* zcool candidate cases for future creative-exploration workflow cleaning. No new `creative_explore` queries were generated, no `query_to_case_mapping.jsonl` changes, no official `queries.jsonl` changes, no large-scale scraping, no author/profile data collected, no login/captcha bypass, no bulk image downloads, no commit/push/PR.

---

## 1. Phase goal

Following Phase 4's `IMAGE_ACCESS_VALIDATION: PASSED` / `SCALE_UP_SCRAPING: CONTINUE_TARGETED_ONLY` recommendation, this phase performed a small, targeted search for 8–10 new zcool work pages, opened each page in a real Chromium browser (Playwright), scrolled to trigger lazyload, saved one internal-research full-page screenshot per candidate, extracted the real `data-src` image URLs (never the `bg-placeholder.jpg` `src`), and scored each candidate against the 9 creative-exploration criteria defined for this phase. This is a candidate-screening pass only — no case was promoted to a formal `case_00N`/`zcool_ce_NNN` structured record.

## 2. Search keywords used

品牌视觉 多方案 设计推导 · logo 多方案 提案 · 包装设计 多方案 茶饮品牌 视觉推导 · IP形象 吉祥物 多方案 设计过程 · logo 草图 方案对比 · 咖啡品牌 设计全案 方向探索 · KV视觉方向 2D 3D 活动海报 · 吉祥物设计 多方案 提案

All searches were scoped to `zcool.com.cn` / `www.zcool.com.cn`. Only individual `/work/*.html` case pages were followed as candidates; `/collection/*`, `/tag/*`, and author-homepage links returned by search were excluded at triage (not opened as candidates).

## 3. Candidate total

**10** candidates (`ZCE-CAND-001`–`ZCE-CAND-010`), within the 8–10 cap. Full detail: `creative_exploration_candidates.csv`.

## 4. Decision counts

| Decision | Count |
|---|---|
| SELECT | 1 |
| BACKUP | 0 |
| REJECT | 8 |
| NEGATIVE_SAMPLE | 1 |

No candidate was scored a BACKUP (5–6) this round — the sample split cleanly into one strong SELECT and a cluster of REJECT-range cases (score 0–3), with no candidate landing in the middle band. Per task rule, the bar was not loosened to manufacture additional SELECT/BACKUP results.

## 5. SELECT case(s)

### ZCE-CAND-001 — 「韩娱嘉年华」品牌视觉升级全流程分享 (brand_upgrade_full_process) — score 8/9

**Why selected:** This is the only candidate in the sample documenting a full, single-project creative-exploration arc with real visual evidence, not just final renders. The page walks through: 项目背景 (project background) → 用户画像 (user persona) → 情绪板分析 (moodboard collage of ~15 reference images) → 关键词提取 (keyword extraction: 活力/狂热/甜酷) → an 8-sketch LOGO草图 grid (hand-drawn-style logo sketches) → a logo-concept breakdown explaining the V+ring+heart+bubble symbolism → two distinct finished logo lockups shown side by side (版本一/版本二) → KV concept and execution → IP exploration reasoning → real on-site event photography as the final application. It satisfies `has_multiple_directions=true` (two compared final logo versions plus the 8-sketch set) and 2 of the 3 extra-strength criteria (`has_sketches`, `has_comparison`), meeting the SELECT gate.

**Strongest evidence:** The 8-sketch LOGO草图 grid (`ZCE-CAND-001-E003`) combined with the side-by-side 版本一/版本二 final-logo comparison (`ZCE-CAND-001-E004`) — this is the only instance in the whole sample of an actual sketch-to-comparison-to-final progression visible in the images themselves, not just asserted in text.

**Still missing:** An explicit selection statement — the page explains what each final logo *version* is used for (版本一 default, 版本二 for a dated campaign placement) rather than stating why one sketch/direction was chosen over the others during the 8-sketch stage. `has_selection_reason` is therefore `false`. A future workflow-cleaning pass on this case would need to either accept the version-usage note as a soft proxy for selection reasoning, or flag `candidate_outputs`/selection as still partially undocumented.

## 6. BACKUP cases

None this round. The next-closest candidates by raw score (`ZCE-CAND-004`, `ZCE-CAND-005`, `ZCE-CAND-008`, `ZCE-CAND-009`, each scoring 3/9) fall well short of the 5–6 BACKUP band — see §7.

## 7. REJECT cases — main strengths and gaps

| candidate_id | title (short) | score | main strength | main gap |
|---|---|---|---|---|
| ZCE-CAND-002 | 智能感知与计算研究中心logo | 1 | Brief symbolism explanation for the one logo shown | No brief, no sketches, no alternative directions — only light/dark color-mode variants of one mark |
| ZCE-CAND-003 | 一起"稿"设计——标志篇 | 0 | Large image count (74 images) | Not one project: a ~40-logo student roundup across unrelated clients, so `has_multiple_directions` does not apply; finished vector marks only, no sketches |
| ZCE-CAND-004 | Study Tea 研茶包装设计 | 3 | Real brand-background + design-concept paragraphs | Only one packaging direction shown across 6 flavor colorways — per task rule, colorway variety alone is not `has_multiple_directions` |
| ZCE-CAND-005 | 壹茶 新中式茶饮品牌全案 | 3 | Real project-background paragraph, logo construction/grid refinement, very extensive applications | No design-rationale text, no sketches, no alternative directions, no comparison, no selection reasoning |
| ZCE-CAND-006 | 快手 KV海报动态作品合集 | 1 | Large finished-poster volume, consistent 3D template | A multi-year client-recap of separate campaigns, not one project's directions; no brief, no rationale |
| ZCE-CAND-007 | 海报，活动主视觉，主KV，字体设计 | 1 | — | Freelance poster portfolio with a one-line hire-me caption; no brief or process content of any kind |
| ZCE-CAND-008 | 小熊咖啡 VI设计作品集 | 3 | 4-point design-rationale paragraph, logo grid + IP orthographic-view refinement, rich applications | No brief (generic company description only), no sketches, no alternative logo/IP directions, no comparison |
| ZCE-CAND-009 | 固体饮料包装（大括号包装设计） | 3 | Strong project-motive brief + numbered design-logic/differentiation rationale | One packaging system across ~11 flavor variants — no sketches, no alternative directions, no comparison |

## 8. Negative sample

### ZCE-CAND-010 — 奈杉咖啡×反转创意 | 品牌全案/IP吉祥物/包装设计 — score 2/9

Flagged `NEGATIVE_SAMPLE` rather than plain `REJECT` because it is the cleanest illustration in this batch of the task's core warning: **a beautiful, extremely polished final result is not evidence of a documented exploration process.** The page's only text is a project/service/team-credits block (no business background, no goals, no design rationale of any kind). What follows is a very large gallery of finished output — one wordmark, one IP character (shown in front/side/back views, counted as `has_refinement`), a full color system, and dozens of social-media, packaging, and environmental application mockups (`has_applications=true`). Despite the volume and production value, there is no brief, moodboard, sketch, alternative direction, comparison, or selection statement anywhere on the page. This is a useful negative-training example precisely because its visual richness could tempt an automated or careless reviewer into over-crediting it as a rich creative-exploration case.

(`ZCE-CAND-005` and `ZCE-CAND-007` share the same "final-result-only" pattern and were considered as the negative-sample slot; `ZCE-CAND-010` was chosen because it has literally zero process/rationale text — the purest case of the pattern — while `ZCE-CAND-005` at least has a genuine brief paragraph and `ZCE-CAND-007` has no real text at all rather than misleadingly thorough-looking credits.)

## 9. Common creative-exploration patterns observed

- Where a real multi-stage process exists (`ZCE-CAND-001`), it follows a consistent template: background → persona/moodboard → keyword extraction → sketches → concept rationale → final comparison/versions → application. This matches the 9-criterion schema well and suggests the schema is a reasonable fit for zcool's own "全流程分享" (full-process share) post format when that format is actually used.
- Pages explicitly labeled 全流程/流程/设计推导 in the title were the only ones that delivered on process documentation; pages labeled 全案/作品集/合集 (full case / portfolio / compilation) consistently turned out to be finished-result showcases or multi-project roundups, regardless of visual polish.

## 10. Common missing content

- **`has_selection_reason` was false on every candidate**, including the one SELECT case. No page in this sample states "we chose direction/sketch X over Y because Z." This is the single most consistently absent criterion.
- **`has_multiple_directions` was true on only 1 of 10 candidates.** The next most common failure mode was a single finished direction shown across color, flavor, or format *variants* (Study Tea, 壹茶, 固体饮料包装) — explicitly excluded from counting as multiple directions per this phase's scoring rules.
- **No candidate showed a moodboard/keyword stage except `ZCE-CAND-001`.**

## 11. Image access

Consistent with Phase 4: all 10 candidate pages returned HTTP 200 on both a plain fetch and a real Chromium render; all real content images live in each `<img>`'s `data-src` attribute (never the `src` placeholder `bg-placeholder.jpg`). A 3-URL-per-candidate `data-src` sample (30 URLs total, not a bulk download) was checked with HTTP `HEAD` requests — **30/30 returned HTTP 200**, `image/jpeg`-or-`image/png`/`image/gif` content-type, no login or cookies required. All 10 full-page screenshots were captured successfully, decode correctly, and are non-blank (verified by `PIL.Image.verify()` plus per-crop pixel-stddev sampling). Full per-file results in §13 of the validation section below and in `creative_exploration_candidates.csv`'s `page_accessible`/`real_images_accessible`/`full_page_screenshot` columns (all `true`).

## 12. Candidates suitable for next-phase detailed workflow cleaning

**`ZCE-CAND-001`** is the only candidate in this batch that justifies moving into a formal, structured `case_00N`-style workflow-cleaning pass — it has the sketch-to-final progression, the moodboard/keyword stage, and application evidence needed to populate a `creative_exploration_workflows.jsonl` record with `candidate_outputs` actually filled in (unlike every one of the 5 baseline-pilot cases from Phase 3, where `candidate_outputs` was empty on every step).

## 13. Candidates that can only support a brief-derived query, not workflow evidence

`ZCE-CAND-004`, `ZCE-CAND-005`, `ZCE-CAND-008`, `ZCE-CAND-009` all have a real, quotable project-background and/or design-rationale paragraph, so each could support a *brief_derived* `agent_route` query (in the same style as the 6 `AR-ZCE-xxx` queries from Phase 3) — but none has multi-direction visual evidence, so none should be cited as `workflow_derived` or given a non-empty `supporting_evidence_ids` for a comparison/selection step. `ZCE-CAND-002`, `ZCE-CAND-003`, `ZCE-CAND-006`, `ZCE-CAND-007` lack even a usable brief and are not recommended for query derivation of either kind. `ZCE-CAND-010` (the negative sample) should only ever be cited as a negative/counter-example, never as brief or workflow evidence.

## 14. Copyright and internal-research limits

All 10 screenshots and all recorded evidence descriptions are internal research artifacts only. No original zcool artwork was downloaded in bulk, no author/profile information was collected beyond the byline already visible on each public work page (needed only to identify the case, per the existing `baseline_pilot` convention), and nothing from this phase is intended for publication or redistribution. See `CANDIDATE_EVIDENCE_INDEX.csv`'s `copyright_reuse_note` column (uniform on every row: "Internal research evidence only; do not republish original ZCOOL artwork.").

## 15. Next-phase recommendation

Recommend cleaning **1 candidate** (`ZCE-CAND-001`) into a formal structured workflow case next phase. This is a deliberately conservative recommendation: the task's own scoring rules produced only one qualifying SELECT case from a targeted 10-candidate sample, and the instructions are explicit that standards must not be loosened to manufacture more. A larger next-phase cleaning batch would require either a fresh, larger targeted search specifically for pages using the "全流程分享/设计推导" post pattern (the only pattern that produced usable evidence in this sample), or accepting brief-derived-only queries (§13) for the 4 candidates that have a real brief but no workflow evidence.
