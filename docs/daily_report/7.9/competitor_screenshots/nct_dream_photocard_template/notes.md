# NCT Dream photocard template

## Query

`NCT Dream photocard template`

## Query Intent

Find a design template for making K-pop photocards themed around the NCT Dream group (a specific idol-group IP).

## Claude Metadata Label (first pass, text-only, from Task 3)

- **claude_relevance_label:** FAIL
- **claude_issue_type:** `wrong_decomposition;bad_relevance;competitor_gap`
- **claude_confidence:** high
- **claude_relevance_reason:** Results matched on the generic word 'dream' (Dream of the Red Chamber, dream career) instead of the NCT Dream K-pop IP; no photocard template content returned.
- **primary_scene / secondary_scene:** 文创 / 营销电商
- **visible_result_count:** 10
- **search_url:** https://www.curify-ai.com/search?q=NCT%20Dream%20photocard%20template

## Screenshot Paths

- **Curify screenshot:** `curify.png` (copied from `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/002_cultural_nct_dream_photocard_template.png`)
- **Pinterest screenshot:** `pinterest.png` — **manually added 2026-07-09** (captured by a human in a logged-in Pinterest session; not automated — see note below)
- **Canva screenshot:** `canva.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)
- **Bing Images screenshot:** `bing.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)
- **Google Images screenshot:** `google.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)

**2026-07-09 update:** Bing, Google, and Canva screenshots were captured in a follow-up session using a purpose-built Playwright collector (`scripts/external-screenshot-p0-12/`). Pinterest was **not automated** — the repo's documented ToS/bot-detection concern for Pinterest automation was not resolved — but the user manually captured and added `pinterest.png` afterward using a real, logged-in Pinterest session. See the "Competitor Screenshot Results — 2026-07-09" section below for findings.

## Visual Review (Claude, direct inspection of curify.png)

**visual_curify_label: FAIL**

Screenshot confirms: an orange banner reads "Few results... also showing results for: NCT Dream photocard design, NCT Dream member template, K-pop photocard layout," then the grid shows 'academic dream of the red chamber' scroll illustrations, mythological figures (Sha Wujing, Sun Wukong, Tang Seng), a DNA helix diagram, and plate tectonics — the query was decomposed down to the bare word 'dream' and matched to an unrelated Chinese classic-literature IP ('Dream of the Red Chamber'). Zero K-pop or photocard content visible.

## Preliminary Conclusion

Visual inspection of the Curify screenshot **confirms** the Task 3 text-metadata label (FAIL / `wrong_decomposition;bad_relevance;competitor_gap`) — the mismatch is visible directly in the rendered result grid, not just inferable from titles. Competitor comparison (Pinterest / Canva / Bing / Google) is needed to determine whether this is a **retrieval gap** (competitors surface real matches Curify misses) or a **content gap** (no platform has this niche/IP-specific content) — that determination is marked **pending** until competitor screenshots can be captured, ideally by a human using a real browser session or by wiring up a browser-automation tool (Playwright/computer-use) in a future session. Recommend a quick human spot-check to confirm this reading before using as a report/PR example.


---

## Competitor Screenshot Results — 2026-07-09 (Bing / Google / Canva run)

Bing, Google, and Canva were collected via `scripts/external-screenshot-p0-12/collect.mjs` (headful Playwright, conservative 7-13s delay between queries, no CAPTCHA/login-wall bypass attempted). Pinterest was **manually captured by a human** in a logged-in session — not automated, consistent with the repo's documented ToS/bot-detection concern for Pinterest automation specifically (see `EXTERNAL_SCREENSHOT_AUTOMATION_PLAN_2026-07-09.md`).

| Platform | Status | Query used | File |
|---|---|---|---|
| Bing Images | Captured | primary | `bing.png` |
| Google Images | Captured | primary | `google.png` |
| Canva | Captured | NCT Dream photocard template | `canva.png` |
| Pinterest | Manually added (human, logged-in session) | primary | `pinterest.png` |

**Bing observation:** Abundant, highly relevant real NCT Dream photocard templates; the related-products panel explicitly lists "NCT Dream Photocards" and "Mark Lee NCT Photocard".

**Google observation:** Real NCT Dream photocard templates sourced from Instagram/Pinterest/Reddit/X ("Dreamscape", "Candy", "Beatbox" photocard templates).

**Canva observation:** Real K-pop photocard "wishlist"-style templates in the correct genre/format, though not NCT Dream-branded specifically.

**Pinterest observation:** Abundant, precisely NCT Dream-branded photocard templates ("Dreamscape Album Photocard Template", "Candy", "Both Sides Jeno Jaemin Photocard Album Template") — the strongest, most exactly-branded match of the four platforms.

**Best competitor platform for this query:** Pinterest (most precisely branded), with Bing/Google close behind

**Updated conclusion:** Strong retrieval gap on Curify, now confirmed by all four competitor platforms. This was determined by direct visual inspection of all four screenshots (not inferred from search-result counts), so the retrieval-gap vs. content-gap distinction left open in the prior visual-review pass is fully resolved for this case.
