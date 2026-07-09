# Visual Relevance and Competitor Comparison — 2026-07-09

## Overview

This document is the automated visual-review layer requested on top of the Task 3 text-only relevance labeling and the Task 7/8 P0 manual-review plan. Task 3's `claude_relevance_label`/`claude_issue_type` columns were assigned from **text metadata alone** (titles, tags, types, result counts) — no one, human or Claude, had actually looked at a rendered screenshot yet. This pass closes that gap for a representative sample of 12 P0 cases: each Curify screenshot was directly inspected (not just its metadata), each finding was written to a per-case `notes.md`, and the results were rolled up into a new CSV and this summary.

**Automation achieved:** query selection, folder/file scaffolding, screenshot copying, and the entire visual relevance review (label + reason) were done without human involvement. Competitor screenshot capture for **Bing, Google, and Canva** (36 of 48 possible platform×case combinations) was completed in a follow-up pass using a purpose-built Playwright collector (`scripts/external-screenshot-p0-12/`) — see [Competitor Comparison Results](#competitor-comparison-results) below. **Pinterest automation was not run**, consistent with a documented ToS/bot-detection concern for Pinterest automation specifically — but the user subsequently **manually captured and added all 12 Pinterest screenshots** using a real, logged-in browser session, bringing screenshot coverage for the sample to effectively 4 of 4 platforms. The user also **manually re-captured several Bing/Google/Canva/Curify screenshots** that had been taken before the page fully finished loading, and this pass verifies those replacements and corrects two findings that changed as a result — see [Screenshot Availability](#screenshot-availability) and [Limitations](#limitations) below.

No production code was touched. No files were staged or committed. The final consolidated work report has not been written.

## Why This Visual Pass Was Needed

The P0 manual-review plan (`P0_MANUAL_REVIEW_AND_SCREENSHOT_PLAN_2026-07-09.md`) flagged 42 cases based on text metadata and noted that screenshots existed but had not yet been inspected. Text metadata can mislead in both directions — a title like "brand IP display board" can *sound* on-topic while the rendered image is not, and conversely a terse title can undersell an actually-relevant image. Actually opening the screenshot and reading what's on the page is a stronger relevance signal than titles/tags alone, and it's exactly the kind of check that doesn't require a live browser session — the screenshots already exist on disk from the 2026-07-07 execution run. Doing this pass first, before asking a human to look at anything, maximizes how much of the review loop can be automated.

## Selected Cases

12 P0 cases were selected (10 from the task's prioritized list, plus 2 added to close a category gap — see below), covering every category the task required:

| # | Query | Scenes | Language | Issue types covered |
|---|---|---|---|---|
| 1 | NCT Dream photocard template | 文创/营销电商 | English | wrong_decomposition, bad_relevance, competitor_gap |
| 2 | maker space label set printable | 教育/文创 | English | wrong_decomposition, bad_relevance, missing_content_type |
| 3 | Y2K chrome skincare launch poster | 品牌/营销电商 | English | bad_relevance, wrong_decomposition, competitor_gap |
| 4 | K-beauty glass skin brand launch visual | 品牌/营销电商 | English | bad_relevance, wrong_decomposition, competitor_gap |
| 5 | 小红书香薰产品种草图 | 营销电商/文创 | Chinese | bad_relevance, wrong_decomposition |
| 6 | 低饱和国风茶包装设计 | 文创/品牌 | Chinese | wrong_decomposition, bad_relevance, missing_content_type |
| 7 | zones of regulation poster classroom | 教育/文创 | English | bad_relevance, wrong_decomposition, missing_content_type, competitor_gap |
| 8 | coding unplugged activity cards | 教育/文创 | English | bad_relevance, wrong_decomposition, competitor_gap |
| 9 | genshin impact Furina fanart wallpaper 4k | 文创 | English | wrong_decomposition, bad_relevance, competitor_gap |
| 10 | Amazon EBC enhanced brand content layout | 营销电商/品牌 | English | zero_result |
| 11 | IEP accommodations checklist visual | 教育/文创 | English | low_result, bad_relevance, missing_content_type, competitor_gap |
| 12 | 光与夜之恋 卡面设计参考图 | 文创/营销电商 | Chinese | wrong_decomposition, bad_relevance, competitor_gap |

**Why 12, not 10:** the task's 10 prioritized queries covered every required category except `low_result` (all 10 had either 0 results or ≥4 results). `IEP accommodations checklist visual` (3 results) was added to cover `low_result`. `光与夜之恋 卡面设计参考图` was added as a second Chinese cultural/IP-card case — it's structurally the same failure pattern as `NCT Dream photocard template` (an IP-specific card-design request decomposed down to a generic word) but in Chinese, which strengthens the "this is a systemic decomposition issue, not a one-off" evidence.

Each case's folder, files, and full writeup live at `docs/daily_report/7.9/competitor_screenshots/<slug>/` — see `COMPETITOR_SCREENSHOT_INDEX_2026-07-09.md` for the folder index.

## Curify Visual Review Results

**All 12 of 12 selected cases visually confirmed as FAIL.** Every screenshot was opened and read directly (not inferred from titles) — full per-case reasoning is in `docs/daily_report/7.9/manual_review/P0_visual_review_with_claude_2026-07-09.csv` (`visual_curify_reason` column) and each case's `notes.md`. Highlights:

- **Amazon EBC enhanced brand content layout** — the screenshot is a literal **"No results for..."** page with only generic topic-browse fallback tiles. This is the single most unambiguous result in the batch.
- **genshin impact Furina fanart wallpaper 4k** — only 3 cards render, captioned "friends," "howls moving castle," and "neighbor totoro" (Studio Ghibli references) — zero Genshin Impact content despite Curify's own broadened-query banner explicitly naming "Furina Genshin Impact character art."
- **NCT Dream photocard template** and **光与夜之恋 卡面设计参考图** — both IP-specific card-design requests (English K-pop IP, Chinese mobile-game IP respectively) were decomposed to a bare generic word ("dream," implicitly "night/light") and matched to unrelated content (Dream of the Red Chamber scrolls; La La Land / constellation / AI-infrastructure cards). The same failure shape in two languages is the strongest single piece of evidence that this is a systemic query-decomposition issue, not noise.
- **maker space label set printable** — matched literally on "space" (outer space/astronomy), not the compound term "maker space."
- **Y2K chrome skincare launch poster** and **K-beauty glass skin brand launch visual** — both returned a grab-bag of unrelated consumer products (socks, headphones, eyemasks, coffee makers) with no skincare or Y2K/K-beauty visual style whatsoever.
- **小红书香薰产品种草图** and **低饱和国风茶包装设计** — both Chinese queries returned generic product photography (eyemask/pendant; oats/cookies/pasta sauce) with zero connection to aromatherapy or Chinese-style tea packaging respectively. Notably, 小红书香薰产品种草图 didn't even trigger Curify's own broadened-query fallback banner — it silently returned near-empty, irrelevant results.
- **zones of regulation poster classroom**, **coding unplugged activity cards**, **IEP accommodations checklist visual** — all three education-domain queries returned generic K-12/ESL classroom decor (vocabulary cards, self-care posters, phonics cards) with no trace of the specific special-education/CS-pedagogy concept requested.

For 11 of the 12 cases, visual inspection **confirmed and, where the original label carried only medium confidence (IEP accommodations checklist visual), strengthened it to high** — actually seeing the mismatch on-screen removes the residual uncertainty that comes from judging relevance off titles alone.

## Competitor Comparison Results

**All four competitor platforms are now captured and visually reviewed for all 12 cases (48/48).** Bing, Google, and Canva were captured via `scripts/external-screenshot-p0-12/collect.mjs`, a headful Playwright collector built for this batch (7–13s randomized delay between queries, no CAPTCHA/login-wall bypass attempted at any point). **Pinterest was not automated** — consistent with the repo's documented ToS/bot-detection concern — but the user manually captured all 12 Pinterest screenshots in a real, logged-in session, and also manually re-captured several Bing/Google/Canva/Curify screenshots that had been taken before the page finished loading. Full per-case detail is in each `notes.md`'s "Competitor Screenshot Results" section and in `docs/daily_report/7.9/manual_review/P0_visual_review_with_claude_2026-07-09.csv`.

**Headline finding: this is overwhelmingly a retrieval-gap problem, not a content-gap problem.** Across all 12 cases, Bing, Google, and Pinterest returned abundant, closely-matching, on-topic results — including several exact-title matches ("Unplugged Coding Activity Deck of Cards," "Zones of Regulation" posters with the correct Blue/Green/Yellow/Red framework, official "光与夜之恋" game character-card art, and — on Pinterest — a pin literally titled "EBC / A+ Content" for the Amazon EBC case). The content Curify failed to surface demonstrably exists and is well-served elsewhere. This resolves the open question from the prior pass: text-metadata reasoning had inferred `competitor_gap` for 8 of the 12 cases based on plausibility alone; visual inspection of real competitor screenshots now **confirms** a retrieval gap for all 12, not just those 8 — and the addition of Pinterest as a fourth independent, uniformly strong data point makes this conclusion more robust than it was in the prior pass.

**Canva tells a more nuanced story — and two of its three apparent "content gaps" have since been corrected.** 9 of 12 primary Canva queries returned genuinely relevant results (strongest: zones of regulation, K-beauty glass skin, IEP accommodations; partial/generic: maker space labels matched literal "space" much like Curify itself does, Y2K and Amazon EBC got thematically-adjacent-but-imprecise matches). The automated run had reported the remaining 3 — all Chinese-language, all IP/niche-specific (`小红书香薰产品种草图`, `低饱和国风茶包装设计`, `光与夜之恋 卡面设计参考图`) — as genuine **"We couldn't find any results"** zero-result pages, even after retrying with the simplified `canva_fallback_query`. **After the user manually re-captured these three screenshots from a logged-in Canva session, 2 of the 3 no longer show a hard zero-result:**

- `小红书香薰产品种草图` and `低饱和国风茶包装设计` now show Canva returning **generic, broad results** (eyemask/pendant/musical-instrument items; oats/cookies/pasta-sauce product photography) — the same kind of imprecise, category-level mismatch Curify itself produces, not an empty state. **Revised: mild retrieval/decomposition weakness, not a content gap.**
- `光与夜之恋 卡面设计参考图` now shows Canva's filter chips correctly naming the game's actual playable characters (萧逸, 陆沉, 齐司礼, 查理苏, 夏鸣星), but the visible template cards have no connection to the game. **Revised: partial recognition with no matching inventory** — a nuanced case, not a clean content gap.

Only `genshin impact Furina fanart wallpaper 4k` remains a confirmed, clean Canva content gap (re-verified on the manually re-captured screenshot — still zero relevant content) — consistent with Canva's template marketplace simply not carrying licensed anime/game character art.

Per-case `best_competitor_platform` and `visual_competitor_observation` (abbreviated; full text in each `notes.md`):

| Case | Best platform | One-line finding |
|---|---|---|
| NCT Dream photocard template | Pinterest, then Bing/Google | Pinterest has precisely NCT Dream-branded photocard templates; Bing/Google close behind; Canva generic (not NCT Dream-branded). |
| maker space label set printable | Bing / Google / Pinterest (3-way) | Real "Makerspace/STEM Labels" products on all three; Canva matched literal "space" (astronaut labels), echoing Curify's own weakness. |
| Y2K chrome skincare launch poster | Pinterest / Google | Pinterest has a literal "Y2K Chrome Aesthetics for Beauty" brand kit; Google has BrandCrowd's exact-title poster; Bing/Canva partial. |
| K-beauty glass skin brand launch visual | 4-way tie | All four platforms returned genuinely on-topic K-beauty brand-launch imagery/templates. |
| 小红书香薰产品种草图 | Bing / Pinterest | Real 香薰 product/marketing imagery on both; Canva **(corrected)** returns generic results, not a zero-result — same weakness as Curify, milder. |
| 低饱和国风茶包装设计 | Bing / Google / Pinterest | Abundant real Chinese-style tea packaging designs on all three; Canva **(corrected)** returns generic results, not a zero-result. |
| zones of regulation poster classroom | 4-way tie | The strongest, most unanimous case in the batch — all four platforms show exact "Zones of Regulation" framework matches. |
| coding unplugged activity cards | Bing / Google / Pinterest (3-way) | Exact "Unplugged Coding" activity-card products on all three; Canva has real (if less precisely-branded) coding activity cards. |
| genshin impact Furina fanart wallpaper 4k | Bing / Google / Pinterest (3-way) | Gorgeous, abundant, exact Furina 4K fanart on all three; Canva remains the one confirmed content gap for licensed anime art. |
| Amazon EBC enhanced brand content layout | Pinterest (exact "EBC/A+ Content" template), Bing/Google (abundance) | Likely the single strongest retrieval-gap example in the batch, now confirmed by three of four platforms: Curify returned a literal zero-result for a mature, heavily-served design-service niche. |
| IEP accommodations checklist visual | Bing / Google / Pinterest (3-way) | Exact "IEP Accommodations Checklist" products on all three; Canva has real IEP-specific content once fully loaded. |
| 光与夜之恋 卡面设计参考图 | Bing / Google / Pinterest (3-way) | Exact official game character-card art on all three; Canva **(corrected)** shows partial recognition (correct character-name filter chips) but no matching template cards — nuanced, not a clean content gap. |

## Screenshot Availability

All 12 cases now have all 5 screenshot files (`curify.png`, `bing.png`, `google.png`, `canva.png`, `pinterest.png`) plus `notes.md` — 72 of 72 (100%). `k_beauty_glass_skin_brand_launch_visual/` initially had no `curify.png` (the user's manual re-capture had been saved as `curify1.png`/`curify2.png` instead); this has been **resolved** by copying `curify1.png` (the one showing the actual search-results grid) to `curify.png`, with both originals kept as backups. See `COMPETITOR_SCREENSHOT_FINAL_CHECK_2026-07-09.md` for the full per-file completeness table, a suspicious/empty-file check (none found — every screenshot is well above a trivial size threshold), and a log of exactly which files were manually replaced and when (by file-modification timestamp).

Bing, Google, and Canva screenshots are fresh as of 2026-07-09 (automated capture, with several manually re-captured afterward to fix incomplete page loads). Pinterest screenshots are fresh as of 2026-07-09 (fully manual, human-captured). Curify screenshots are copies of the original 2026-07-07 execution run for 9 of 12 cases, and manually re-captured fresh on 2026-07-09 for the other 3 (`y2k_chrome_skincare_launch_poster`, `genshin_impact_furina_fanart_wallpaper_4k`, `guangyu_yezhilian_card_design_reference`, plus the two misnamed files for `k_beauty`) — in every re-captured case the content matched the original 2026-07-07 capture, so no Curify-side finding needed revision.

## Strongest Examples

Now backed by real competitor screenshots, not just Curify-side reasoning. In order of report-readiness:

1. **Amazon EBC enhanced brand content layout** — a true zero-result on Curify with a literal "No results" screen, **and** now confirmed as the strongest retrieval-gap case in the batch by three independent competitor platforms: Bing and Google are both flooded with real "Amazon EBC/A+ Content" design-service listings, and Pinterest has a pin literally titled "EBC / A+ Content." This pairing (unambiguous Curify failure + unambiguous, multi-platform competitor abundance) is the single best example to lead with in any PR or report.
2. **zones of regulation poster classroom** — the most unanimous case in the batch: Curify returned 100% unrelated vocabulary flashcards, while Bing, Google, Canva, *and* Pinterest all returned exact "Zones of Regulation" framework matches. Four-way competitor agreement makes this nearly impossible to dispute.
3. **NCT Dream photocard template + 光与夜之恋 卡面设计参考图 (paired)** — the same "IP-specific card request → decomposed to a bare generic word → matched to an unrelated IP" Curify failure occurring in both English and Chinese, and now both confirmed as retrieval gaps by Bing/Google (abundant real photocard/game-card content exists). Strongest evidence that this is a systemic decomposition bug, not a one-off ranking miss.
4. **genshin impact Furina fanart wallpaper 4k** — Curify's own UI names the correct broadened query yet returns zero matching content; Bing and Google both return gorgeous, abundant, exact Furina fanart. Canva, notably, *also* has zero relevant content here — useful as the contrast case showing that not every gap is the same shape (Canva's is a genuine, platform-appropriate content gap; Curify's is a retrieval failure despite having identified the right intent).
5. **maker space label set printable** — a clean, simple illustration of literal keyword matching overriding compound-term intent ("maker space" → "space"). Notably, Canva shows a *milder version of the same weakness* (matched literal "space" too, though with visually coherent results) while Bing/Google nail it precisely — useful for showing the failure mode isn't unique to Curify's architecture, just more severe there.

## Cases Still Needing Human Spot Check

11 of 12 cases are marked `needs_human_spot_check = yes` in the CSV — visual confirmation is strong but domain/IP knowledge (K-pop groups, a specific mobile game, SEL frameworks, IEP terminology, Y2K aesthetics) benefits from a fast human glance before being cited in a report or PR. Only **Amazon EBC enhanced brand content layout** is marked `needs_human_spot_check = no`, because a literal "No results" screen requires no domain judgment to confirm.

None of these 11 need a full re-investigation — the recommended check is: open `curify.png`, read the one-paragraph `visual_curify_reason`, confirm agreement, done. This should take a few minutes total for all 11, not a few minutes each.

## Limitations

- **Pinterest automation was still not run — deliberately, not for lack of capability.** Playwright is fully able to run the same collector against Pinterest (a working reference script, `scripts/pinterest-search-eval/`, already exists), but two files in this repo (`data/external_signals/README.md`, `claude-reports/claude_prompt7_5_manual_pilot_setup.md`) explicitly document a prior rejection of Playwright/Puppeteer automation against pinterest.com on ToS/bot-detection grounds. That decision has not been reconfirmed as current, so **the automation path remains unresolved.** However, the user manually captured and added all 12 Pinterest screenshots using a real, logged-in browser session — a human-operated action, not automation — so screenshot coverage for this sample is now complete despite the automation question remaining open. See `EXTERNAL_SCREENSHOT_AUTOMATION_PLAN_2026-07-09.md`.
- **Several screenshots were manually re-captured after incomplete page loading.** Beyond the Canva lazy-load issue below, the user separately identified and replaced a number of Bing/Google/Canva/Curify screenshots that had been captured before the page fully finished rendering, and replaced them with fresh, fully-loaded captures. Two of those replacements (`小红书香薰产品种草图`, `低饱和国风茶包装设计`) changed the Canva finding from a hard content gap to a milder retrieval/decomposition weakness, and one (`光与夜之恋 卡面设计参考图`) changed it to a nuanced partial-recognition finding — see Competitor Comparison Results above. The remaining replacements (Curify screenshots for 3 cases, plus Canva/Curify for `zones_of_regulation_poster_classroom` and `genshin_impact_furina_fanart_wallpaper_4k`) were consistent with the original findings and required no correction. Full replacement log in `COMPETITOR_SCREENSHOT_FINAL_CHECK_2026-07-09.md`.
- **One screenshot had a naming issue, now resolved.** `k_beauty_glass_skin_brand_launch_visual/` initially had no `curify.png` — the manual re-capture had been saved as `curify1.png`/`curify2.png` instead. `curify1.png` was copied to `curify.png`; both originals remain as backups.
- **Canva required a longer render wait for 3 of 12 cases in the original automated run.** `nct_dream_photocard_template`, `coding_unplugged_activity_cards`, and (partially) `iep_accommodations_checklist_visual` were initially captured before Canva's lazy-loaded template grid finished rendering (blank/skeleton cards). The collector was adjusted to scroll-and-wait longer before screenshotting, and all three were re-captured successfully within the same automated pass.
- **Curify's own screenshots are copies of the 2026-07-07 run for 9 of 12 cases; the other 3 (plus the 2 misnamed k-beauty files) were manually re-captured fresh on 2026-07-09.** In every re-captured case, the content matched the original 2026-07-07 capture exactly, so this did not change any Curify-side finding. If Curify's index changes again in the future, the `search_url` recorded in each `notes.md` allows anyone to re-run it live.
- **IEP accommodations checklist visual has a metadata/screenshot count mismatch on the Curify side.** The CSV recorded `visible_result_count = 3`, but only 1 card rendered a visible thumbnail in the original Curify screenshot. This is a Curify-capture artifact from the 2026-07-07 run, unrelated to the competitor screenshots captured in this pass.
- **Confidence is about label correctness, now substantially strengthened by real competitor evidence across four platforms.** `final_confidence = high` in the CSV reflected certainty about Curify-side irrelevance from the first visual pass; the competitor screenshots captured in this pass now also resolve the `competitor_gap` vs. `content_gap` distinction for all 12 cases (see Competitor Comparison Results above) — this is no longer an open question for this sample.
- **Sample of 12, not all 42.** This pass covers a representative slice of the 42 P0 cases, chosen to hit every required category at least once. It is not a substitute for reviewing the remaining 30 P0 cases in the full plan.

## Next Steps

- **Get Pinterest ToS confirmation from a manager/owner if automated Pinterest collection is wanted going forward.** Screenshot coverage for this sample is already complete via manual capture, so this is no longer blocking this batch, but it would still need resolving before extending automated collection (Bing/Google/Canva) to include Pinterest for future batches.
- **Run the human spot-check** described above on the 11 `needs_human_spot_check = yes` cases (a few minutes total) before citing any of these as confirmed findings in a PR or the work report — this is now a lighter check than originally scoped, since the competitor evidence (now spanning four platforms) has already resolved most of the interpretive uncertainty.
- **Extend this same automated visual-review + competitor-capture method to the remaining 30 P0 cases** (and eventually the 26 P1 cases), now that the Bing/Google/Canva pipeline is proven end-to-end on this 12-case sample.
- **Draft the retrieval-gap PR candidates** using the evidence gathered here — `Amazon EBC enhanced brand content layout`, `zones of regulation poster classroom`, and the `NCT Dream photocard template` / `光与夜之恋 卡面设计参考图` pair are the strongest, most competitor-verified examples to lead with.
- **Do not write the consolidated work report yet** — the human spot-check above should land first.
