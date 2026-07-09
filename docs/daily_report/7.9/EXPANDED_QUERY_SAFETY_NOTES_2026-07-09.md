# Expanded Query Safety Notes — 2026-07-09

## Overview

This document reviews the 68 executed gold-set queries and the 1,118-row expanded candidate pool (`docs/daily_report/7.7/02-05`) for safety-sensitive content categories, ahead of any future round where these queries — or their auto-generated expansions — might be used as prompts for image generation rather than just search pressure-testing.

**Expanded queries should not be sent directly into an auto-generation workflow without a filtering pass.** A query that is perfectly reasonable to run against Curify's *search* index (to test recall/relevance, as this whole audit has done) is not automatically safe or appropriate to use as a prompt for *generating new images* — search surfaces existing, already-moderated content, while generation creates new content that carries the platform's own liability and brand risk if it depicts something unsafe, exploitative, or infringing. This document exists to separate those two uses and flag which queries need a closer look before crossing from one to the other.

## Safety Scope

Per the manager-specified risk categories, plus the search-time trigger-keyword list already used earlier in this audit (`CURIFY_SEARCH_RELEVANCE_SUMMARY_2026-07-07.md`, "Safety-Risk Observations"):

| Category | Why it matters for auto-generation |
|---|---|
| Funeral / 殡葬 | Generating imagery for grief/memorial contexts risks producing tasteless or exploitative content if not handled with care, even in a commercial-branding framing. |
| Sexual / 色情 | Auto-generation of sexual content is a hard platform-policy line in essentially every commercial image-generation product. |
| Medical disease / 医疗疾病 | Generated depictions of disease/illness risk medical misinformation, stigmatizing imagery, or content that reads as diagnostic/clinical without any actual medical oversight. |
| Skin disease / 皮肤病 | Same concern as medical disease, specifically for visible/dermatological conditions, which also intersects with beauty-industry "before/after" claims that can mislead. |
| Violence / 暴力 | Generated violent imagery is a standard platform-policy exclusion and a brand-safety risk regardless of stated intent. |
| Body abnormality / 身体异常 | Risk of generating content that stigmatizes disability or physical difference, or that reads as exploitative rather than respectful/functional (e.g., assistive-device marketing is fine; mocking or sensationalizing a body difference is not). |
| Sensitive cultural or religious content / 敏感文化或宗教内容 | Risk of generating content that misrepresents, appropriates, or trivializes a religious or cultural practice/symbol. |

## Findings From the 68 Executed Queries

A keyword scan of all 68 executed query strings against the seven categories above found:

- **`宠物殡葬服务品牌视觉设计`** (pet funeral/memorial service brand visual design) — matches the funeral/殡葬 category. As previously noted in `CURIFY_SEARCH_RELEVANCE_SUMMARY_2026-07-07.md`, the context is a commercial pet-industry service, not a human-funeral, sexual, medical-disease, or violent context — lower severity than the trigger term implies at face value, but still recommended for a standard content-moderation pass before any generation use. Label: **`needs_review`**.
- **`家用医疗器械品牌设计`** (home medical device brand design) — this is medical-device **branding**, not medical-disease or diagnostic content. Consistent with the prior pass in the relevance summary doc, this is **not flagged** as medical_disease/医疗疾病 risk; it sits in the adjacent "medical device branding" commercial-design category instead (see below). Label: **`safe`** for search eval; **`needs_review`** only if a future generation prompt would depict device-on-body usage in a way that reads as clinical/diagnostic rather than product marketing.
- **`first then board autism`** and **`visual schedule strips autism classroom`** — these are special-education support-tool queries (a "first/then" visual schedule board is a standard, benign autism-support classroom tool). Consistent with the prior pass, **autism-support classroom material is not a body-abnormality or medical-disease risk** — flagging it as such would overclaim. Label: **`safe`**.
- **`IEP accommodations checklist visual`** — an administrative special-education document (Individualized Education Program). No safety-category match; this is a benign educational/accessibility query. Label: **`safe`**.
- **Fandom/IP queries** (`NCT Dream photocard template`, `genshin impact Furina fanart wallpaper 4k`, `光与夜之恋 卡面设计参考图`, `Love and Deepspace card pack design`) — none of these match any of the seven core safety categories. They are flagged here under a *different* concern: **copyright/IP risk**, not safety risk. Generating new "fan art" style images depicting specific copyrighted game/idol-group characters carries IP/licensing risk distinct from the manager's seven listed categories, and is called out separately in Safety Scope's adjacent-edge-case list. Label: **`needs_review`** (IP/copyright basis, not a content-safety basis).
- **No other rows matched any of the seven core categories** under a literal keyword read — consistent with, and now re-confirmed alongside, the original finding in `CURIFY_SEARCH_RELEVANCE_SUMMARY_2026-07-07.md`.

**Explicitly not overflagged, per the task's instruction:** `家用医疗器械品牌设计` (medical device branding), `first then board autism`, `visual schedule strips autism classroom`, `IEP accommodations checklist visual`, `zones of regulation poster classroom`, and other special-education/accessibility queries are **not** treated as unsafe. These are legitimate, benign commercial/educational design categories that happen to share vocabulary with sensitive-sounding trigger words (medical, autism) without actually depicting disease, disability-as-spectacle, or clinical content.

## Findings From the 1,118 Candidate Pool

A first-pass keyword scan (documented dictionary match, not a trained classifier — see Limitations) was run across all 1,118 candidate-pool rows plus the 68 executed queries (1,186 total query strings scanned, with some overlap since several of the 68 also appear verbatim in the pool):

**Core safety categories:**

| Category | Hits | Detail |
|---|---|---|
| Funeral / 殡葬 | **2 distinct queries** (3 raw hits, one duplicated across the 68-set and the pool) | `宠物殡葬服务品牌视觉设计` (pet funeral, already reviewed above) and, newly surfaced in the pool, **`殡葬服务行业品牌视觉设计`** (funeral-services-industry brand visual design, general — not pet-specific). This second query is closer to human-funeral-industry branding and warrants its own review pass rather than being assumed identical in severity to the pet-focused case. Label: **`needs_review`**. |
| Sexual / 色情 | 0 hits | No matches under the keyword dictionary used (English + Chinese terms), including after an extended second-pass sweep with additional terms (underwear, lingerie, swimsuit, nsfw, etc.). |
| Medical disease / 医疗疾病 | 0 hits for actual disease/illness/diagnosis terms | The only medically-adjacent hits found were commercial branding queries: `家用医疗器械品牌设计` (medical device branding), `宠物医院品牌视觉手册` (pet hospital brand manual), and `医美机构品牌视觉设计` / `医美术后修复品牌视觉` (medical-aesthetics/cosmetic-clinic branding) — none depict disease or diagnostic content; all are commercial branding requests. |
| Skin disease / 皮肤病 | 0 hits | No matches. |
| Violence / 暴力 | 0 hits | No matches, including after the extended sweep (war, injury, blood, accident, etc. — the 2 "war" substring hits were false positives on "reward(s)," see Limitations). |
| Body abnormality / 身体异常 | 0 hits | No matches, including after the extended sweep (disability, amputee, disabled, etc.). |
| Sensitive culture/religion | 0 real hits; 6 false-positive substring matches | All 6 initial "hits" were the substring "cult" matching inside "**cult**ural" (e.g., `cultural creative product packaging design`, `intangible cultural heritage pattern design`) — not actual cult/extremism content. A follow-up sweep for explicit religion terms (佛教, 基督, 伊斯兰, 清真, religion) found no real hits either. |

**Adjacent commercial-design edge cases** (not core safety risks, but flagged for a lighter review pass before generation use):

- **Medical device branding:** 2 hits (`家用医疗器械品牌设计`, appearing in both the 68-set and the pool) — commercial branding only, `safe` for search, light review recommended before generation if the prompt would depict device-on-body use.
- **Autism / special education:** 8 hits (`IEP accommodations checklist visual`, `first then board autism`, `visual schedule strips autism classroom`, `IEP goal tracking data sheet template`, `IEP present levels data visual`, and siblings) — all benign administrative/support-tool content; `safe`.
- **Funeral / memorial branding:** same 2 queries as the core funeral category above.
- **Body / skin / beauty claims:** 4 hits (`K-beauty glass skin brand launch visual`, `医美机构品牌视觉设计`, `医美术后修复品牌视觉`, plus the search-eval-only duplicate of the K-beauty query in the pool) — cosmetic/aesthetic-clinic branding queries carry a mild "medical claims" adjacency (a clinic-branding image implying a treatment outcome) worth a light review before generation, even though none depict disease.
- **Fandom / IP / copyrighted characters:** **18 hits** — the largest adjacent-risk cluster, concentrated in two fandoms: NCT Dream, Genshin Impact/Furina, Love and Deepspace, and 光与夜之恋 (already reviewed above), plus a cluster of **Chiikawa (吉伊卡哇)** queries in the pool not present in the 68-executed set (`吉伊卡哇高清电脑壁纸`, `吉伊卡哇头像图片`, `吉伊卡哇钥匙圈周边设计`, `吉伊卡哇生日快乐贺图`, `chiikawa透明背景贴纸素材`, `chiikawa钥匙圈周边设计`, `chiikawa玩偶产品图`, `吉伊卡哇 x 麦当劳联名 折气球教程`, `Chiikawa 奇美拉 同人壁纸`, `Sanrio x Chiikawa crossover keychain design`, and others). This entire cluster is a copyright/IP-risk category, not a content-safety category — flagged for legal/licensing review before any generation use, separate from the seven core safety categories.
- **Minors / classroom / children-related educational materials:** **58 hits** — by far the largest raw count, but this is expected and appropriate given how much of the query pool is legitimately educational (classroom posters, children's flashcards, kindergarten worksheets). **None of these 58 are flagged as unsafe** — they are the kind of benign query this audit has repeatedly confirmed elsewhere (e.g., `zones of regulation poster classroom`, `IEP accommodations checklist visual`). They are listed here only because "content involving minors" is a category that generally warrants baseline platform-policy awareness (e.g., ensuring generated imagery of children stays strictly in an illustrated/cartoon educational-material register, not photorealistic), not because anything in this specific set shows a problem.

## Recommended Safety Labels

| Label | Meaning |
|---|---|
| `safe` | No match against the seven core safety categories or the adjacent edge-case list; suitable for both search eval and generation use without special review. |
| `needs_review` | Matches an adjacent edge case (medical device branding, autism/special-ed, funeral/memorial branding, body/skin/beauty claims, fandom/IP, minors-related) or a core category in a mitigated/commercial context (e.g., pet funeral branding) — safe enough to keep in the search-eval pipeline, but should get a human look before any generation use. |
| `exclude_from_generation` | Matches a core safety category in an unmitigated way (none found in this scan) — should not be used to generate new images at all, regardless of search-eval status. |
| `allowed_for_search_eval_only` | Valid and useful for testing Curify's *search* recall/relevance (per this whole audit's methodology), but should not be forwarded into any auto-generation workflow without a separate, dedicated review — this applies to the fandom/IP cluster specifically, where testing search recall is fine but generating new "fan art" of copyrighted characters is a distinct decision with its own risk profile. |

Based on this scan: **0 queries across the full 1,186 scanned (68 executed + 1,118 pool, with overlap) warrant `exclude_from_generation`.** The funeral cluster (2 queries), the fandom/IP cluster (18 queries), and the body/skin/beauty-claims cluster (4 queries) warrant `needs_review` or `allowed_for_search_eval_only`, depending on which specific future generation use is being considered. Everything else scanned is `safe`.

## Suggested Filtering Rules Before Auto-Generation

- **Keyword-based prefilter** — run the same seven-category + adjacent-edge-case dictionary scan used in this document against any new query batch before it enters a generation workflow, as a fast, cheap first pass (with the explicit caveat that it will have false positives like the "cult"/"cultural" and "war"/"reward" collisions found here, and possible false negatives for phrasing not in the dictionary).
- **Manual review for `needs_review` queries** — the funeral cluster, body/skin/beauty-claims cluster, and medical-device-branding queries identified above should get a human look (not necessarily a rejection) before being used as generation prompts.
- **Exclude or block high-risk generation prompts** — establish a hard block for the three zero-tolerance categories (sexual, violence, body-abnormality-as-spectacle) even though this scan found no current matches, since future query-pool expansions could introduce them.
- **Keep some sensitive-but-valid queries for search eval only** — the fandom/IP cluster (NCT Dream, Genshin/Furina, 光与夜之恋, Love and Deepspace, Chiikawa) is legitimate and valuable for search pressure-testing (as this entire audit has used it) but should be explicitly routed to `allowed_for_search_eval_only` rather than silently flowing into a generation pipeline.
- **Separate search evaluation from generation evaluation** — as a structural rule, not just a per-query label: the pipeline that runs queries against Curify's search index should not be the same pipeline (or at least not the same unreviewed gate) that would feed prompts into an image-generation step, precisely because a query can be safe/valuable for the former and risky for the latter (see next section).

## Safety vs. Search Evaluation

**A query can be entirely valid for search pressure-testing while being unsuitable — or at least requiring extra review — for automatic generation.** This audit's entire methodology has depended on this distinction: testing whether Curify's *search* surfaces relevant results for `NCT Dream photocard template` or `genshin impact Furina fanart wallpaper 4k` is a legitimate, low-risk way to measure retrieval quality, because search only surfaces pre-existing, already-published content (fan art, official assets, etc.) that already exists on the web — it doesn't create anything new. Using the same query text as a prompt to *generate* a new image of Furina or an NCT Dream member is a categorically different action with its own copyright and platform-policy considerations, independent of whether the search-relevance finding was positive or negative. The `allowed_for_search_eval_only` label exists specifically to keep this distinction explicit rather than letting a query's "already tested and found useful" status quietly imply it's also generation-safe.

The same logic applies, more mildly, to the funeral and body/skin/beauty-claims clusters: `殡葬服务行业品牌视觉设计` is a fine query to run against a search index to see what branding content exists for that industry, while generating new memorial/funeral-branding imagery from scratch is a more sensitive act that deserves its own review regardless of the search-side finding.

## Limitations

- **This is a first-pass, keyword-based review**, not a trained safety classifier. The dictionaries used (English + Chinese terms per category) were constructed for this task and will have both false positives (demonstrated here: "cult" inside "cultural," "war" inside "reward(s)") and false negatives (phrasings, slang, or euphemisms not in the dictionary that a human reviewer or a real classifier might catch).
- **Not a final policy classifier.** The labels proposed here (`safe`/`needs_review`/`exclude_from_generation`/`allowed_for_search_eval_only`) are a first-pass triage framework, not a substitute for whatever formal content-policy review process governs actual production generation workflows.
- **Needs human review before production generation.** Every `needs_review` and `allowed_for_search_eval_only` query listed in this document should get an actual human look before being used to generate images, regardless of how benign this keyword-level analysis judged it to be.
- **Scope limited to query text only.** This scan evaluated the query strings themselves, not any downstream generated output, actual search results, or screenshots — a query with safe-sounding text could still theoretically surface or generate unsafe content depending on what a model does with it, which this document cannot detect.

## Next Steps

- **Add a safety label column to the expanded query candidates.** Extend files 02-05 (or a companion index) with a `safety_label` column populated from this first pass, so future rounds don't have to re-derive it from scratch.
- **Review `needs_review` queries manually** — starting with the 2 funeral-cluster queries, the 4 body/skin/beauty-claims queries, and a sample of the 18 fandom/IP queries — before any of them are used in a generation context.
- **Exclude high-risk categories from auto-generation** — even though 0 queries currently warrant `exclude_from_generation`, keep the hard-block rule active for sexual, violence, and body-abnormality-as-spectacle content so future query-pool expansions are caught automatically rather than requiring a fresh manual scan every time.
- **Keep search-eval-only queries separated from the generation workflow** — specifically, ensure the fandom/IP cluster's `allowed_for_search_eval_only` status is enforced structurally (e.g., a pipeline flag or separate query list), not just documented here, so it can't be accidentally forwarded into a generation step later.

No production code was touched in producing this document. No files were staged or committed. The final consolidated work report has not been written.
