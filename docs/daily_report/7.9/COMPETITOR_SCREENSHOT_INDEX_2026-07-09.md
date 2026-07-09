# Competitor Screenshot Index — 2026-07-09

Index of `docs/daily_report/7.9/competitor_screenshots/` — one folder per selected P0 case, each containing the Curify screenshot, a `notes.md` writeup, and competitor screenshots.

**Updated 2026-07-09 (third pass — final verification):** Bing, Google, and Canva screenshots were captured for all 12 cases using a purpose-built Playwright collector (`scripts/external-screenshot-p0-12/`). The user has since **manually added Pinterest screenshots for all 12 cases** (captured in a real, logged-in Pinterest session — not automated) and **manually re-captured several Bing/Google/Canva/Curify screenshots** that had been taken before the page fully finished loading. This pass verifies the final folder contents, corrects two findings that changed after the manual re-capture, and flags one genuinely missing file. See [Final Check](#final-check) below and the companion `COMPETITOR_SCREENSHOT_FINAL_CHECK_2026-07-09.md` for full detail.

## Status Legend

- ✅ available = captured, present in the folder, and visually reviewed.
- ⚠️ = present but flagged (see notes for the one case with a naming issue).
- Canva's `Query used` column shows the query actually captured — 9 of 12 cases used the primary query; 3 Chinese-language cases originally fell back to `canva_fallback_query` in the automated run, but 2 of those 3 no longer need the fallback after the manual re-capture (see Corrections below).

## Index

| # | Folder | Query | Curify | Bing | Google | Canva | Pinterest |
|---|---|---|---|---|---|---|---|
| 1 | `nct_dream_photocard_template/` | NCT Dream photocard template | ✅ | ✅ | ✅ | ✅ | ✅ manually added |
| 2 | `maker_space_label_set_printable/` | maker space label set printable | ✅ | ✅ | ✅ | ✅ | ✅ manually added |
| 3 | `y2k_chrome_skincare_launch_poster/` | Y2K chrome skincare launch poster | ✅ (manually re-captured) | ✅ | ✅ | ✅ | ✅ manually added |
| 4 | `k_beauty_glass_skin_brand_launch_visual/` | K-beauty glass skin brand launch visual | ✅ (resolved — see below) | ✅ | ✅ | ✅ | ✅ manually added |
| 5 | `xiaohongshu_aromatherapy_product_teaser_image/` | 小红书香薰产品种草图 | ✅ (manually re-captured) | ✅ | ✅ | ✅ (manually re-captured — **corrected**, see below) | ✅ manually added |
| 6 | `low_saturation_chinese_style_tea_packaging_design/` | 低饱和国风茶包装设计 | ✅ (manually re-captured) | ✅ | ✅ | ✅ (manually re-captured — **corrected**, see below) | ✅ manually added |
| 7 | `zones_of_regulation_poster_classroom/` | zones of regulation poster classroom | ✅ (manually re-captured) | ✅ | ✅ | ✅ (manually re-captured) | ✅ manually added |
| 8 | `coding_unplugged_activity_cards/` | coding unplugged activity cards | ✅ | ✅ | ✅ | ✅ | ✅ manually added |
| 9 | `genshin_impact_furina_fanart_wallpaper_4k/` | genshin impact Furina fanart wallpaper 4k | ✅ (manually re-captured) | ✅ | ✅ | ✅ (manually re-captured) | ✅ manually added |
| 10 | `amazon_ebc_enhanced_brand_content_layout/` | Amazon EBC enhanced brand content layout | ✅ | ✅ | ✅ | ✅ (manually re-captured) | ✅ manually added |
| 11 | `iep_accommodations_checklist_visual/` | IEP accommodations checklist visual | ✅ | ✅ | ✅ | ✅ | ✅ manually added |
| 12 | `guangyu_yezhilian_card_design_reference/` | 光与夜之恋 卡面设计参考图 | ✅ (manually re-captured) | ✅ | ✅ | ✅ (manually re-captured — **corrected**, see below) | ✅ manually added |

**Curify coverage: 12 / 12 (100%). Bing/Google/Pinterest coverage: 12 / 12 each (100%). Canva coverage: 12 / 12 (100%).** All screenshots have been visually reviewed by Claude (direct pixel inspection, not metadata inference).

## Missing File (Resolved)

`k_beauty_glass_skin_brand_launch_visual/` was missing `curify.png` — the user's manual re-capture had been saved as `curify1.png` (top-of-page) and `curify2.png` (scrolled) instead. **Resolved 2026-07-09:** `curify1.png` (the one showing the actual search-results grid) was copied to `curify.png`; both originals remain as backups. See `COMPETITOR_SCREENSHOT_FINAL_CHECK_2026-07-09.md` for the full check.

## Corrections From the Manual Re-Capture

Three of the manually re-captured Canva screenshots showed materially different content than the original automated (logged-out) captures, requiring a factual correction — not just a status-label update:

- **小红书香薰产品种草图 (xiaohongshu) and 低饱和国风茶包装设计 (low_saturation):** Originally reported as a genuine Canva **content gap** ("We couldn't find any results," even on the fallback query). The manually re-captured, logged-in screenshots instead show Canva returning generic, broad results (oats/cookies/pasta-sauce product photography; eyemask/musical-instrument/pendant items) — **the same generic categories Curify itself returns for these queries.** Revised finding: this is a mild version of the same retrieval/decomposition weakness Curify shows, not a hard content gap.
- **光与夜之恋 卡面设计参考图 (guangyu):** Originally reported as a genuine Canva content gap. The manually re-captured, logged-in screenshot shows Canva's filter chips correctly naming the game's actual playable characters (萧逸, 陆沉, 齐司礼, 查理苏, 夏鸣星) — but the visible template cards themselves have no connection to the game. Revised finding: **partial recognition, no matching inventory** — a nuanced case, not a clean content gap.

Two other cases (`amazon_ebc_enhanced_brand_content_layout`, `zones_of_regulation_poster_classroom`) and one `genshin_impact_furina_fanart_wallpaper_4k` also had Canva/Curify screenshots manually re-captured, but the content was consistent with (or, for Amazon EBC, marginally stronger than) the original findings — no correction needed there. Full detail for every case is in each `notes.md`.

## Category Coverage (per Task 7 requirement)

| Category | Cases covering it |
|---|---|
| `zero_result` | Amazon EBC enhanced brand content layout |
| `low_result` | IEP accommodations checklist visual |
| `wrong_decomposition` | NCT Dream photocard template, maker space label set printable, Y2K chrome skincare launch poster, K-beauty glass skin brand launch visual, 小红书香薰产品种草图, 低饱和国风茶包装设计, zones of regulation poster classroom, coding unplugged activity cards, genshin impact Furina fanart wallpaper 4k, 光与夜之恋 卡面设计参考图 |
| `bad_relevance` | all 12 |
| `missing_content_type` | maker space label set printable, 低饱和国风茶包装设计, zones of regulation poster classroom, IEP accommodations checklist visual |
| `competitor_gap` | NCT Dream photocard template, Y2K chrome skincare launch poster, K-beauty glass skin brand launch visual, zones of regulation poster classroom, coding unplugged activity cards, genshin impact Furina fanart wallpaper 4k, IEP accommodations checklist visual, 光与夜之恋 卡面设计参考图 — **all 8 confirmed as real retrieval gaps by Bing/Google/Pinterest screenshots**, not just inferred from text metadata. |
| Chinese queries | 小红书香薰产品种草图, 低饱和国风茶包装设计, 光与夜之恋 卡面设计参考图 |
| English queries | remaining 9 |
| brand (品牌) | Y2K chrome skincare launch poster, K-beauty glass skin brand launch visual |
| education (教育) | maker space label set printable, zones of regulation poster classroom, coding unplugged activity cards, IEP accommodations checklist visual |
| cultural/creative (文创) | NCT Dream photocard template, 低饱和国风茶包装设计, genshin impact Furina fanart wallpaper 4k, 光与夜之恋 卡面设计参考图 |
| marketing/e-commerce (营销电商) | 小红书香薰产品种草图, Amazon EBC enhanced brand content layout |

All 10 prioritized queries from the task instructions were included; `IEP accommodations checklist visual` and `光与夜之恋 卡面设计参考图` were added to close the `low_result` gap and add a second Chinese IP-card comparison point, bringing the set to 12.

## What the Screenshots Actually Show

**Bing, Google, and Pinterest: near-uniformly strong, on-topic results for all 12 queries.** Every one of the 36 Bing/Google/Pinterest screenshots shows abundant, closely-matching real content — from exact-title matches ("Unplugged Coding Activity Deck of Cards," "Zones of Regulation" posters with the correct Blue/Green/Yellow/Red framework, official "光与夜之恋" character-card art, an explicit "EBC / A+ Content" branded Amazon-listing template on Pinterest) to strongly on-topic categories (K-beauty glass-skin editorial imagery, Y2K-chrome beauty branding). This is the strongest, most consistent evidence in the whole project that most of Curify's P0 failures are **retrieval gaps**, not content gaps — the content clearly exists and is well-served elsewhere; Curify's query-decomposition/matching logic is what's failing to surface it.

**Canva: mixed, with two of its three apparent "content gaps" now revised.** 9 of 12 primary Canva queries returned genuinely relevant results (some strong: zones of regulation, K-beauty, IEP; some partial/generic: maker space matched literal "space" much like Curify does). Of the remaining 3 (all Chinese-language, all IP/niche-specific), the automated run had reported all three as genuine "We couldn't find any results" zero-result pages — **2 of those 3 (小红书香薰产品种草图, 低饱和国风茶包装设计) are now known to be generic-but-non-empty results after the manual, logged-in re-capture**, not hard content gaps. The third (光与夜之恋 卡面设计参考图) is now understood as partial recognition (correct character-name filter chips, non-matching template cards). Only `genshin impact Furina fanart wallpaper 4k` remains a clean, confirmed Canva content gap (re-verified on the manually re-captured screenshot) — consistent with Canva's template marketplace simply not carrying licensed anime/game character art.

**Pinterest: manually added, uniformly strong.** All 12 Pinterest screenshots were captured by the user in a real, logged-in session and show abundant, precisely on-topic results — as strong as or stronger than Bing/Google in several cases (e.g., an exact "EBC / A+ Content" branded template for Amazon EBC; exact NCT Dream-branded photocard templates). No blocks, CAPTCHAs, or empty results were observed on any of the 12.

## Final Check

See `docs/daily_report/7.9/COMPETITOR_SCREENSHOT_FINAL_CHECK_2026-07-09.md` for the full completeness table, missing/suspicious-file check, and manual-replacement log.
