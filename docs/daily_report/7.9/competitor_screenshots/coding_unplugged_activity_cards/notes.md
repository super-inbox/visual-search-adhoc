# coding unplugged activity cards

## Query

`coding unplugged activity cards`

## Query Intent

Find printable activity cards for 'unplugged coding' (computer-science concepts taught without a computer) for classroom use.

## Claude Metadata Label (first pass, text-only, from Task 3)

- **claude_relevance_label:** FAIL
- **claude_issue_type:** `bad_relevance;wrong_decomposition;competitor_gap`
- **claude_confidence:** high
- **claude_relevance_reason:** Results are unrelated lifestyle/food/wellness content; nothing related to coding or unplugged CS activities.
- **primary_scene / secondary_scene:** 教育 / 文创
- **visible_result_count:** 10
- **search_url:** https://www.curify-ai.com/search?q=coding%20unplugged%20activity%20cards

## Screenshot Paths

- **Curify screenshot:** `curify.png` (copied from `docs/daily_report/7.7/curify_search_screenshots_2026-07-07/060_education_coding_unplugged_activity_cards.png`)
- **Pinterest screenshot:** `pinterest.png` — **manually added 2026-07-09** (captured by a human in a logged-in Pinterest session; not automated — see note below)
- **Canva screenshot:** `canva.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)
- **Bing Images screenshot:** `bing.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)
- **Google Images screenshot:** `google.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)

**2026-07-09 update:** Bing, Google, and Canva screenshots were captured in a follow-up session using a purpose-built Playwright collector (`scripts/external-screenshot-p0-12/`). Pinterest was **not automated** — the repo's documented ToS/bot-detection concern for Pinterest automation was not resolved — but the user manually captured and added `pinterest.png` afterward using a real, logged-in Pinterest session. See the "Competitor Screenshot Results — 2026-07-09" section below for findings.

## Visual Review (Claude, direct inspection of curify.png)

**visual_curify_label: FAIL**

Screenshot confirms results are beach/vocabulary cards (surfboard, sunglasses), self-care/depression posters, fruit and kitchen-utensil vocabulary cards, and body-expression/hobby-action illustration sets — general ESL/lifestyle content with zero connection to coding, computer science, or 'unplugged' CS pedagogy.

## Preliminary Conclusion

Visual inspection of the Curify screenshot **confirms** the Task 3 text-metadata label (FAIL / `bad_relevance;wrong_decomposition;competitor_gap`) — the mismatch is visible directly in the rendered result grid, not just inferable from titles. Competitor comparison (Pinterest / Canva / Bing / Google) is needed to determine whether this is a **retrieval gap** (competitors surface real matches Curify misses) or a **content gap** (no platform has this niche/IP-specific content) — that determination is marked **pending** until competitor screenshots can be captured, ideally by a human using a real browser session or by wiring up a browser-automation tool (Playwright/computer-use) in a future session. Recommend a quick human spot-check to confirm this reading before using as a report/PR example.


---

## Competitor Screenshot Results — 2026-07-09 (Bing / Google / Canva run)

Bing, Google, and Canva were collected via `scripts/external-screenshot-p0-12/collect.mjs` (headful Playwright, conservative 7-13s delay between queries, no CAPTCHA/login-wall bypass attempted). Pinterest was **manually captured by a human** in a logged-in session — not automated, consistent with the repo's documented ToS/bot-detection concern for Pinterest automation specifically (see `EXTERNAL_SCREENSHOT_AUTOMATION_PLAN_2026-07-09.md`).

| Platform | Status | Query used | File |
|---|---|---|---|
| Bing Images | Captured | primary | `bing.png` |
| Google Images | Captured | primary | `google.png` |
| Canva | Captured | coding unplugged activity cards | `canva.png` |
| Pinterest | Manually added (human, logged-in session) | primary | `pinterest.png` |

**Bing observation:** Abundant exact "Unplugged Coding" activity-card products (Twinkl, Etsy, teacher marketplaces).

**Google observation:** Same — "Unplugged Coding Activity Deck of Cards", multiple exact matches.

**Canva observation:** Real coding-themed activity cards ("Let's Code!", "Coding Exercise" grid) — good match once the lazy-loaded image grid was given enough time to render (see Limitations).

**Pinterest observation:** Abundant exact "Coding Unplugged Activity" cards ("Bee-Bot Job Cards", "Coding Direction Cards for Kids", "Zoo Path unplugged coding activity") — as strong a match as Bing/Google.

**Best competitor platform for this query:** Bing / Google / Pinterest (three-way tie)

**Updated conclusion:** Strong retrieval gap on Curify, confirmed by all four competitor platforms. This was determined by direct visual inspection of all four screenshots (not inferred from search-result counts), so the retrieval-gap vs. content-gap distinction left open in the prior visual-review pass is fully resolved for this case.
