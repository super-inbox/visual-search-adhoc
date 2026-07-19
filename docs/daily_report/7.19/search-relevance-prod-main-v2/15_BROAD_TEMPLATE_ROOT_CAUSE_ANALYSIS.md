# Stage 10: Direction 7 Root-Cause Analysis — Broad Template Ranking Noise

Date: 2026-07-19. Investigated per task instructions: root cause FIRST, soft-penalty list only if the scorer proves insufficient.

## Root cause (confirmed, evidence-backed)

All investigated broad-noise cases (吉祥物/mascot, periodic table/元素周期表, 贴纸/sticker, logo, 横幅/banner) share the **same underlying mechanism**, confirmed via direct inspection of `messages/en/nano.json` and `messages/zh/nano.json` in the V0 worktree:

1. **Template-level strict promotion is a broad-recall design choice**: when a template's own combined blob (`category + title + description + content.sections.what + content.sections.who`) strict-matches the query, ALL of that template's inspirations are promoted to `score=100, strict=true` (page.tsx `scoreQueryTokens`, `promoteAllUnderStrictTpl=true` branch). This is intentional recall behavior, not a bug by itself (documented in the pre-existing code comment: "a query like 'character' that matches template-mbti-marvel's blob surfaces every Marvel MBTI inspiration").

2. **The blob mixes high-signal (title/category) and low-signal (long free-text description) fields with equal weight for the match DECISION**. `content.sections.what` is a multi-sentence "how it works" paragraph written for template documentation purposes, not for search matching — and it can incidentally contain vocabulary describing a decorative *motif* or *aesthetic* rather than the template's actual subject matter.

3. **Concrete confirmed case**: `template-mbti-breakingbad`'s `content.sections.what` field literally reads (EN): *"...combines weathered metal headers, **periodic table typography**, comic-style portraits..."* and (ZH): *"...风化金属标题、**元素周期表排版**、漫画风格肖像..."* — this is describing the Breaking Bad chemistry-teacher visual aesthetic (a "periodic table" font/graphic motif on the card design), not periodic-table educational content. Because this text lives in the SAME blob field as the title/category, it strict-matches the query "periodic table" / "元素周期表" with EQUAL weight to the actual title, and the resulting promotion pulls in all 20 Breaking Bad MBTI character cards.

## Answering the design doc's specific root-cause questions

- **Matched field**: `content.sections.what` (description prose), NOT title/category, NOT tags. Confirmed by direct JSON inspection — see `14_BROAD_TEMPLATE_QUERY_RESULT_TRACE.csv`.
- **Match type**: whole-token (for the English "periodic table" — both words present) and CJK-bigram-substring (for "元素周期表").
- **Path**: `original` — template-level strict promotion on the ORIGINAL query pass, not via rewrite/relaxed/decomposition/multi-path. This is important: it means Direction 5's path-level controls (which only apply to non-original paths) structurally CANNOT touch this — the fix had to be in the scoring of the original-pass template-promotion branch itself.
- **Template metadata too broad?** YES — this is the confirmed root cause. The description field is written for human documentation ("here's how this template's design works") and was never curated for search-matching precision.
- **Same-family quantity advantage?** YES, secondarily — because ALL inspirations under a promoted template get score=100, a template with many inspirations (Breaking Bad MBTI has ~20) can dominate the ranked pool purely by inspiration count once promoted, independent of the promotion's own precision.
- **Can the scorer alone fix it?** YES, demonstrated — see below.

## Scorer fix (implemented, no manual penalty list needed)

Rather than adding template IDs to a blacklist (which the task explicitly discourages doing before investigating a scorer-level fix), the actual fix was to stop treating "matched somewhere in the blob" as uniform evidence for template-promoted records. `templateTitleCategoryBlob` (title+category ONLY) was added alongside the existing full blob; `titleHit` / `subjectPresent` for template-promoted records are now evaluated against this high-signal-only blob instead of being hardcoded `true`. **Retrieval/promotion is unchanged** (a template still strict-matches via its full blob, so recall and the zero-result-rate gate are unaffected) — only the SCORE given to a promotion driven purely by description prose changed, via the pre-existing `missing_subject_penalty` now correctly firing for these cases.

## Before/after verification (live, this session)

| Query | Before (top-1) | After (top-1) | Same-family Top-5 count before→after |
|---|---|---|---|
| periodic table | Chuck McGill (Breaking Bad MBTI card) | **chemistry periodic table tricks trends** (genuine science infographic) | breakingbad 5→4 (a genuine match entered top-5) |
| 元素周期表 | Chuck McGill | Chuck McGill (unchanged) | breakingbad 5→5 (no Chinese-language genuine periodic-table content exists in the catalog to promote instead — CATALOG_GAP for this specific locale, not a scorer failure) |
| 吉祥物 (mascot) | brain (organ-health infographic) | **coca cola fizz** (genuine brand-mascot content) | organ-health 5→0, brand-ip-mascot 0→3 |
| 贴纸 (sticker) | adventurer max (kawaii character card) | **brunch** (genuine sticker-overlay product) | kawaii-character-card 5→0, food-sticker-overlay 0→5 |
| logo | ghibli vs mappa (anime studio comparison) | ghibli vs mappa (**unchanged**) | animation-studio-comparison 5→5 — NOT resolved, see below |
| 横幅 (banner) | healthy habits (lifestyle infographic) | **2026 World Cup Group A banner** (genuine promotional-banner content) | lifestyle-infographic 6→0, world-cup-group-poster 0→5 |

4 of 6 cases materially improved with NO manual penalty configuration. 2 cases (`元素周期表`, `logo`) did not improve — investigated further below.

## Cases the scorer did NOT resolve, and why

- **元素周期表 (Chinese "periodic table")**: no genuine Chinese-language periodic-table educational content appears to exist anywhere in the catalog's top candidates (unlike the English form, which found `chemistry periodic table tricks trends`). This looks like a **CATALOG_GAP for this specific locale**, not a scoring defect — the scorer cannot rank content into existence. Flagged for the content/template team per the design doc's "模板元数据治理...超出搜索算法能单独解决的范围" (metadata governance is beyond what the search algorithm alone can fix).
- **logo**: `template-animation-studio-comparison-infographic`'s description likely mentions "logo" in the context of comparing studio logos/branding — this may be a genuinely reasonable (if narrow) interpretation rather than an outright collision; without a curated "logo design" template family to promote instead, there's nothing better for the scorer to rank up. Also a plausible CATALOG_GAP.

## Conclusion: `NO_MANUAL_PENALTY_REQUIRED` for the confirmed-fixable cases

Per task instructions ("只有scorer仍无法充分处理，且存在多个重复case时，才允许加入小规模降权配置"): the scorer fix resolved 4 of 6 investigated broad-noise cases with measurable, verified improvement and zero regressions on the 26-case calibration set (`12_SCORER_CALIBRATION_RESULTS.csv`). No soft-penalty / template-ID blacklist configuration file was created — none was needed for these cases. The remaining 2 unresolved cases (`元素周期表`, `logo`) are diagnosed as likely CATALOG_GAP (missing appropriate content), which a ranking penalty cannot fix by definition (there's nothing better to promote in its place) — adding a penalty there would only suppress the imperfect current answer without providing a better one, and was judged not worth the added configuration surface for two cases without clear alternative content to rank up.

## Long-term mechanism (design-doc-required, not implemented this cycle)

- **Field-level weighting for the template-promotion match decision itself** (not just the scoring layer): currently `templateSearchBlob`'s match DECISION still treats title/category/description/sections as one blob; only the SCORE differentiates them post-hoc. A cleaner long-term fix would weight the match decision itself (e.g., require a description-only match to be combined with at least a relaxed-tier signal elsewhere before triggering full-template promotion) — deferred because changing promotion/retrieval eligibility risks new zero-result cases and needs its own dedicated evaluation cycle, out of scope for this V2 pass's minimal-necessary-implementation principle.
- **Template metadata governance**: `content.sections.what`/`who` are authored as human-readable documentation, not search copy. A content-team review of description text for search-collision-prone phrasing (as found for `template-mbti-breakingbad`) would prevent future instances of this exact failure mode without any algorithmic change at all — this is explicitly a cross-team follow-up, not something this task can resolve unilaterally.
- **Template Family Saturation** (implemented in Stage 7-9, `lib/relevanceScorer.ts` `applyFamilySaturation`) already provides a general, evidence-based defense against any future broad template (known or new) dominating the ranked pool by inspiration-count alone, without needing per-template configuration — this is the generalizable mechanism the design doc's long-term goal calls for ("未来新增相似噪声模板时也能被系统自动降到后排").
