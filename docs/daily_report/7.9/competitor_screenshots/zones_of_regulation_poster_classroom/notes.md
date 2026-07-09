# zones of regulation poster classroom

## Query

`zones of regulation poster classroom`

## Query Intent

Find a classroom poster for the 'Zones of Regulation' social-emotional-learning (SEL) framework used in special education.

## Claude Metadata Label (first pass, text-only, from Task 3)

- **claude_relevance_label:** FAIL
- **claude_issue_type:** `bad_relevance;wrong_decomposition;missing_content_type;competitor_gap`
- **claude_confidence:** high
- **claude_relevance_reason:** Generic vocabulary flashcards and unrelated items; nothing addresses the Zones of Regulation SEL framework.
- **primary_scene / secondary_scene:** 教育 / 文创
- **visible_result_count:** 10
- **search_url:** https://www.curify-ai.com/search?q=zones%20of%20regulation%20poster%20classroom

## Screenshot Paths

- **Curify screenshot:** `curify.png` (copied from `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/068_education_zones_of_regulation_poster_classroom.png`)
- **Pinterest screenshot:** `pinterest.png` — **manually added 2026-07-09** (captured by a human in a logged-in Pinterest session; not automated — see note below)
- **Canva screenshot:** `canva.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)
- **Bing Images screenshot:** `bing.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)
- **Google Images screenshot:** `google.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)

**2026-07-09 update:** Bing, Google, and Canva screenshots were captured in a follow-up session using a purpose-built Playwright collector (`scripts/external-screenshot-p0-12/`). Pinterest was **not automated** — the repo's documented ToS/bot-detection concern for Pinterest automation was not resolved — but the user manually captured and added `pinterest.png` afterward using a real, logged-in Pinterest session. The user also manually re-captured `canva.png` and `curify.png` after noticing the automated versions had been captured before the page fully finished loading; both replacements show content consistent with (Canva: equally strong; Curify: unchanged) the original findings below, so no correction was needed for this case. See the "Competitor Screenshot Results — 2026-07-09" section below for findings.

## Visual Review (Claude, direct inspection of curify.png)

**visual_curify_label: FAIL**

Screenshot confirms results are an Islamic Golden Age knowledge card, musical-instrument/shape/food vocabulary charts, a classroom-vocabulary poster, a library scene, and phonics cards ('ar', 'er', 'ow') — generic K-12 classroom decor and vocabulary content, with no reference to the Zones of Regulation color-zone SEL framework anywhere.

## Preliminary Conclusion

Visual inspection of the Curify screenshot **confirms** the Task 3 text-metadata label (FAIL / `bad_relevance;wrong_decomposition;missing_content_type;competitor_gap`) — the mismatch is visible directly in the rendered result grid, not just inferable from titles. Competitor comparison (Pinterest / Canva / Bing / Google) is needed to determine whether this is a **retrieval gap** (competitors surface real matches Curify misses) or a **content gap** (no platform has this niche/IP-specific content) — that determination is marked **pending** until competitor screenshots can be captured, ideally by a human using a real browser session or by wiring up a browser-automation tool (Playwright/computer-use) in a future session. Recommend a quick human spot-check to confirm this reading before using as a report/PR example.


---

## Competitor Screenshot Results — 2026-07-09 (Bing / Google / Canva run)

Bing, Google, and Canva were collected via `scripts/external-screenshot-p0-12/collect.mjs` (headful Playwright, conservative 7-13s delay between queries, no CAPTCHA/login-wall bypass attempted); `canva.png` and `curify.png` were later manually re-captured by the user (see 2026-07-09 update above) — both replacements are consistent with the original findings below. Pinterest was **manually captured by a human** in a logged-in session — not automated, consistent with the repo's documented ToS/bot-detection concern for Pinterest automation specifically (see `EXTERNAL_SCREENSHOT_AUTOMATION_PLAN_2026-07-09.md`).

| Platform | Status | Query used | File |
|---|---|---|---|
| Bing Images | Captured | primary | `bing.png` |
| Google Images | Captured | primary | `google.png` |
| Canva | Captured (manually re-captured 2026-07-09) | zones of regulation poster classroom | `canva.png` |
| Pinterest | Manually added (human, logged-in session) | primary | `pinterest.png` |

**Bing observation:** Abundant exact "Zones of Regulation" posters with the Blue/Green/Yellow/Red zone framework — precise match.

**Google observation:** Same, extremely abundant exact matches (Amazon, Etsy, TPT listings).

**Canva observation:** Exact "Zones of Regulation" worksheet/poster templates with the same color-zone framework. (Confirmed unchanged on the manually re-captured screenshot.)

**Pinterest observation:** Exact "Zones of Regulation" posters, check-in stations, and "What Zone Are You In?" classroom displays with the correct Blue/Green/Yellow/Red framework — as strong a match as Bing/Google/Canva, making this a four-way unanimous case.

**Best competitor platform for this query:** Four-way tie — the single strongest, most unanimous case in the batch

**Updated conclusion:** Severe retrieval gap on Curify (which returned 100% unrelated vocabulary flashcards), now confirmed unanimously by all four competitor platforms. This was determined by direct visual inspection of all four screenshots (not inferred from search-result counts), so the retrieval-gap vs. content-gap distinction left open in the prior visual-review pass is fully resolved for this case.
