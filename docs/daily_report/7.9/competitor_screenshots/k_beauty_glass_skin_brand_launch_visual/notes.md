# K-beauty glass skin brand launch visual

## Query

`K-beauty glass skin brand launch visual`

## Query Intent

Find a brand-launch visual template for a Korean-beauty ('glass skin') skincare product line.

## Claude Metadata Label (first pass, text-only, from Task 3)

- **claude_relevance_label:** FAIL
- **claude_issue_type:** `bad_relevance;wrong_decomposition;competitor_gap`
- **claude_confidence:** high
- **claude_relevance_reason:** Results are unrelated consumer product categories (eyemask, speaker, coffee maker); no K-beauty brand-launch visual content.
- **primary_scene / secondary_scene:** 品牌 / 营销电商
- **visible_result_count:** 10
- **search_url:** https://www.curify-ai.com/search?q=K-beauty%20glass%20skin%20brand%20launch%20visual

## Screenshot Paths

- **Curify screenshot:** `curify.png` — **resolved 2026-07-09.** The user's manual re-capture had been saved as `curify1.png` (top-of-page view) and `curify2.png` (scrolled view) instead of `curify.png`. `curify1.png` — which shows the actual search-results grid used in the Visual Review below — was copied to `curify.png`; both `curify1.png` and `curify2.png` remain in the folder as backups.
- **Pinterest screenshot:** `pinterest.png` — **manually added 2026-07-09** (captured by a human in a logged-in Pinterest session; not automated — see note below)
- **Canva screenshot:** `canva.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)
- **Bing Images screenshot:** `bing.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)
- **Google Images screenshot:** `google.png` — **captured 2026-07-09** (see Competitor Screenshot Results below; superseded the earlier `screenshot_pending` note)

**2026-07-09 update:** Bing, Google, and Canva screenshots were captured in a follow-up session using a purpose-built Playwright collector (`scripts/external-screenshot-p0-12/`). Pinterest was **not automated** — the repo's documented ToS/bot-detection concern for Pinterest automation was not resolved — but the user manually captured and added `pinterest.png` afterward using a real, logged-in Pinterest session. The user also manually re-captured the Curify screenshot; it was initially saved under `curify1.png`/`curify2.png` rather than `curify.png`, which has since been resolved — see the note above. See the "Competitor Screenshot Results — 2026-07-09" section below for findings.

## Visual Review (Claude, direct inspection of curify.png)

**visual_curify_label: FAIL**

Screenshot confirms results are baby-care brand cards, an eyemask, a musical instrument, a pendant, an aroma diffuser, a bluetooth speaker, a coffee maker, and generic packaged-food product shots (oats, cookies, pasta sauce) — a completely unrelated consumer-product grab-bag with no K-beauty, skincare, or glass-skin visual content.

## Preliminary Conclusion

Visual inspection of the Curify screenshot **confirms** the Task 3 text-metadata label (FAIL / `bad_relevance;wrong_decomposition;competitor_gap`) — the mismatch is visible directly in the rendered result grid, not just inferable from titles. Competitor comparison (Pinterest / Canva / Bing / Google) is needed to determine whether this is a **retrieval gap** (competitors surface real matches Curify misses) or a **content gap** (no platform has this niche/IP-specific content) — that determination is marked **pending** until competitor screenshots can be captured, ideally by a human using a real browser session or by wiring up a browser-automation tool (Playwright/computer-use) in a future session. Recommend a quick human spot-check to confirm this reading before using as a report/PR example.


---

## Competitor Screenshot Results — 2026-07-09 (Bing / Google / Canva run)

Bing, Google, and Canva were collected via `scripts/external-screenshot-p0-12/collect.mjs` (headful Playwright, conservative 7-13s delay between queries, no CAPTCHA/login-wall bypass attempted). Pinterest was **manually captured by a human** in a logged-in session — not automated, consistent with the repo's documented ToS/bot-detection concern for Pinterest automation specifically (see `EXTERNAL_SCREENSHOT_AUTOMATION_PLAN_2026-07-09.md`).

| Platform | Status | Query used | File |
|---|---|---|---|
| Bing Images | Captured | primary | `bing.png` |
| Google Images | Captured | primary | `google.png` |
| Canva | Captured | K-beauty glass skin brand launch visual | `canva.png` |
| Pinterest | Manually added (human, logged-in session) | primary | `pinterest.png` |

**Bing observation:** Real K-beauty/glass-skin brand marketing imagery ("The Glass Skin Gateway", "K-Beauty Glass Skin Serum").

**Google observation:** K-beauty glass-skin editorial and brand imagery (Vogue, Popsugar, LA Times) — strong topical match.

**Canva observation:** Genuinely on-topic brand-launch templates ("Glowing Skin Is Always In", "Skin Glow Beauty Care", "Launching Soon").

**Pinterest observation:** Abundant, precisely on-topic K-beauty "glass skin" brand imagery ("Korean Glass Skin: Glow Like You Mean It", "The Secret to Korean Glass Skin", multiple branded product-launch visuals) — as strong a match as Bing/Google/Canva.

**Best competitor platform for this query:** Four-way tie — all strong

**Updated conclusion:** Strong retrieval gap on Curify, confirmed by all four competitor platforms. This was determined by direct visual inspection of all four screenshots (not inferred from search-result counts), so the retrieval-gap vs. content-gap distinction left open in the prior visual-review pass is fully resolved for this case.
