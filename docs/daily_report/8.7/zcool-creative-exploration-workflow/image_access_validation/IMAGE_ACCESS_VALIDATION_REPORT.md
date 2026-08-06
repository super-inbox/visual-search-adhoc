# Image Access Validation Report

Scope: small-scale technical validation only, on the 3 already-migrated baseline-pilot cases (`case_001`, `case_002`, `case_003`). No new zcool cases were searched, discovered, or scraped. No login, no captcha bypass, no access-control evasion. No commit/push/PR.

---

## 1. Test environment

- Working directory: `/Users/baobaoli/Desktop/visual-search-adhoc-zcool-creative-exploration-2026-08-07`
- HTML fetch: `curl` with a standard desktop Chrome User-Agent, no cookies, no auth.
- Browser: Playwright 1.61.1 (Chromium, headless), driven from a Node.js script.
  - The repo already declares Playwright as a dependency in `scripts/external-screenshot-p0-12/package.json` and `scripts/curify-search-collect/package.json`, but neither has `node_modules` installed locally.
  - Chromium browser binaries were **already present** in the shared local cache (`~/Library/Caches/ms-playwright/chromium-1228`), so no browser download was needed.
  - `playwright` (JS package only, no browser download) was installed into this session's **scratchpad** directory (`/private/tmp/claude-501/.../scratchpad/pw_env/`), **not** into any repo directory — this respects "don't install large node_modules into the repo" while still reusing existing browser binaries. No `package-lock.json` or `node_modules` were added anywhere under `visual-search-adhoc-zcool-creative-exploration-2026-08-07/`.
  - No global environment or system config was modified.
- No account login, no captcha solving, no anti-bot bypass was used at any point.

## 2. Test cases

| case_id | source_url | design_category |
|---|---|---|
| case_001 | https://www.zcool.com.cn/work/ZNzAxNjAwMTY=.html | brand_full_case (冯老二散养牛) |
| case_002 | https://www.zcool.com.cn/work/ZNjkwOTUzMTY=.html | brand_full_case_packaging (NOMNOMBOX) |
| case_003 | https://www.zcool.com.cn/work/ZNjQ0MTA3MDg=.html | brand_full_case (MELLOWCO好醇恰巧) |

Source URLs were read from `baseline_pilot/structured_cases/raw_cases/case_00{1,2,3}/source_metadata.json` — not re-derived, not guessed. Full per-case results in `test_cases.csv`.

## 3. HTML fetch results (Method A)

Plain `curl` fetch, no JS execution. All 3 pages returned `HTTP 200`.

| case_id | `<img>` tags | `src=` attrs | `data-src=` attrs | `bg-placeholder` occurrences | `lazyload photoImage` (data-src) count |
|---|---|---|---|---|---|
| case_001 | 121 | 179 | 17 | 17 | 17 |
| case_002 | 140 | 204 | 27 | 23 | 27 (incl. 4 `isGifImage`) |
| case_003 | 144 | 221 | 40 | 36 | 40 (incl. 4 `isGifImage`) |

No `srcset`, no `<picture>`/`<source>` elements found on any of the 3 pages. `background-image` CSS occurred 13 times per page but only in shared site chrome (header/footer), not case content.

**Key finding:** every content image on the page uses this pattern:
```html
<img data-src="https://img.zcool.cn/community/<id>.jpg?x-oss-process=...&k=...&t=..."
     src="https://public-static.zcool.com.cn/git_z/z/images/new/bg-placeholder.jpg"
     class="lazyload photoImage" ... />
```
`src` (the placeholder) is what the 8.5 pilot's `asset_manifest.csv` recorded for all assets in all 3 cases (`source_url: .../bg-placeholder.jpg` on every row, `quality_flags: image_bytes_unavailable;placeholder_only`). `data-src` — never read by the prior pilot — holds the real, directly-fetchable image URL. This is the most likely root cause of the prior `source_quality: text_ok_images_blocked` conclusion.

## 4. Browser rendering results (Method B)

All 3 pages: real Chromium render succeeded, page scrolled slowly (600px steps, 350ms pauses) to trigger lazyload, full-page screenshot succeeded. No ads clicked, no login, no CAPTCHA encountered.

| case_id | render_success | screenshot | screenshot size (px) | screenshot file size |
|---|---|---|---|---|
| case_001 | true | true | 1440×13916 | 7.2 MB |
| case_002 | true | true | 1440×37216 | 24.2 MB |
| case_003 | true | true | 1440×28801 | 14.3 MB |

All 3 PNGs verified to decode correctly (Pillow `Image.verify()`), non-blank (pixel-stddev check across 5 sampled crops per case, all >15, well above a blank/solid-color page). Manual visual spot-check of sampled crops confirms real design content:
- `case_001`: brand mascot (cow character) applied to vehicle wrap, keychains, storefront signage — final/application shots.
- `case_002`: a moodboard-style brand-positioning slide (ingredient icons + tagline "以中式轻食成就健康平衡") and egg-shaped packaging renders.
- `case_003`: a 4-colorway wordmark comparison grid (cyan/green/orange/yellow "MELLOWCO") plus multi-angle packaging box renders — the closest thing to an explicit multi-direction/comparison visual found in this 3-case sample.

Note: only 5 crops per case (~4,500px of each 13,916–37,216px page) were manually reviewed, not the full screenshot pixel-by-pixel. This is a sampling check for "is there real content," not an exhaustive content audit.

After scroll-triggered lazyload, DOM-level placeholder `src` count dropped to 0 (case_001, case_003) or 5 (case_002, likely images below the final scroll position or a secondary lazy-load pass) — confirming the scroll step is functionally necessary and effective for this pattern.

## 5. Network request results (Method C)

Captured via Playwright's `response` event, filtered to `image` and `document` resource types only (other resource types — scripts, XHR, fonts, CSS — were not logged, to keep the log focused and avoid capturing analytics/tracking noise).

| case_id | image responses observed | candidate real (network-level, broad*) | placeholder responses |
|---|---|---|---|
| case_001 | 179 | 128 | 1 |
| case_002 | 204 | 143 | 1 |
| case_003 | 236 | 177 | 1 |

\* "broad" network-level candidate count includes recommendation-widget thumbnails and avatar images elsewhere on the page, not only the case's own content images — see §3's `lazyload photoImage` count for the precise content-image figure used in `test_cases.csv`.

Full logs: `browser_logs/case_00{1,2,3}_network.jsonl` (622 lines total, all validated as legal JSON). No cookies, `Authorization` headers, or session tokens were recorded in any log line — only response URL, resource type, status, content-type, content-length, and placeholder/candidate flags.

## 6. Direct image access results

For each case, every `data-src` URL belonging to a `lazyload photoImage` element (the case's own content images — 17 + 27 + 40 = 84 URLs total) was checked with an HTTP `HEAD` request (headers only, no body download):

| case_id | URLs checked | HTTP 200 | other |
|---|---|---|---|
| case_001 | 17 | 17 | 0 |
| case_002 | 27 | 27 | 0 |
| case_003 | 40 | 40 | 0 |
| **Total** | **84** | **84** | **0** |

100% of candidate real-image URLs were directly, publicly accessible — `content-type: image/jpeg` (or `image/png`), real `content-length` values (observed range: ~150 KB to ~1.6 MB per image), no authentication, no cookies, no session state. Full per-URL results: `extracted_image_urls/case_00{1,2,3}.csv`.

## 7. Can we observe the creative-exploration process?

Partial, based on the sampled crops (§4) and the pre-existing text-level `workflow_extraction.json` for these 3 cases:

| Evidence type | case_001 | case_002 | case_003 |
|---|---|---|---|
| Sketches | not observed in sampled crops | not observed | not observed |
| Moodboard | not observed | **observed** — ingredient-icon + tagline slide | not observed in sampled crops |
| Multiple creative directions | not observed | not observed | **observed** — 4-colorway comparison grid |
| Direction comparison | not observed | not observed | **observed** (same grid) |
| Design derivation / reasoning shown visually | not observed | not observed | not observed |
| Selection process shown visually | not observed | not observed | not observed |
| Refinement steps shown visually | not observed | not observed | not observed |

This is consistent with the 8.5 pilot's independent *text*-level finding (`workflow_extraction.json`, `missing_stages`) that none of these cases document `candidate_outputs` at the text level either. The access blocker is now resolved (§6), but content richness for `workflow_derived` evidence remains limited in this specific 3-case sample — that is a case-selection question, separate from the access question this validation targeted. Given only 5 of ~13–37 screenshot-heights' worth of crops were reviewed per case, absence of sketches/comparisons in the sampled crops is not proof of absence across the full page — it is reported as "not observed in this sample," not as a confirmed negative.

## 8. Can page screenshots serve as internal evidence?

Yes, on two independent grounds:
1. All 3 full-page screenshots decode correctly, are non-blank, and were manually spot-checked to contain real, legible design content (§4).
2. Separately, the underlying image URLs are directly fetchable (§6) — so screenshots are not the *only* evidence path; they are a redundant, easy-to-review supplement to direct image access, not a fallback compensating for a failure to access images directly.

Both screenshots and extracted URLs are for internal research use only — not published, not added to any dataset or query schema, not redistributed.

## 9. Which method is most reliable?

**Method A (plain HTML fetch, reading `data-src` instead of `src`) is the most reliable and cheapest method for this specific access pattern.** It required no browser, no scrolling, and correctly identified all 84 real image URLs across all 3 cases in a single request per page. Method B (real browser render + scroll) independently confirmed the same URLs via the network log and additionally provides full-page visual screenshots, which Method A alone cannot produce — so it remains valuable for the visual-evidence question (§7–8), but is not required merely to *locate* real image URLs on this platform, given the `data-src` pattern is consistent site-wide across all 3 sampled cases.

## 10. Continue searching for new high-signal cases?

Out of scope for this task and not evaluated here — this validation was explicitly restricted to the 3 existing cases. Separately, on the narrow access question: since the access blocker is resolved (§6, §9) and cheap to check via Method A alone, any future case screening (if and when authorized) would not be blocked by image access, only by the same content-richness question already flagged in §7.

## 11. `IMAGE_ACCESS_VALIDATION` status recommendation

**PASSED.**

Rationale: 3/3 sampled cases succeeded on every access dimension tested — page fetch (HTTP 200), browser render, full-page screenshot, and direct image URL access (84/84 `HEAD` requests returned `200`) — all via a single, consistent, sitewide mechanism (`data-src` lazyload attribute) requiring no login, no cookies, and no anti-bot bypass. This directly overturns the prior `text_ok_images_blocked` / `IMAGE_ACCESS_VALIDATION: CONTINUE` status, which appears to have been an artifact of only reading the `src` attribute. The sample is small (3 cases, one platform template), so this should be read as "the access method is validated and cheap to reproduce," not as "every zcool work page is guaranteed accessible" — but no case in this sample showed any access friction.

## 12. `SCALE_UP_SCRAPING` status recommendation

**CONTINUE_TARGETED_ONLY** (recommendation only — no scraping was performed or initiated in this task, per scope).

Rationale: the previous blocking assumption (images inaccessible) is now shown to be incorrect, so blanket-pausing purely on access grounds is no longer justified. However, this task's own scope explicitly excludes searching for or scraping any new cases, and §7 shows the *remaining* open question is content richness (sketches/multi-direction comparison), not access — that calls for deliberate, targeted case selection by a human reviewer, not mass scraping. Any future targeted pull should also get explicit sign-off on copyright/reuse handling before retaining image bytes beyond internal validation, since all images remain the original designers' copyrighted work (per `source_metadata.json`'s `copyright_or_reuse_notes` for all 3 cases).

---

## Summary tables

**TEST_CASES**: 3 (`case_001`, `case_002`, `case_003`) — all `source_url` read from existing `source_metadata.json`, none guessed.

**HTML_ACCESS_RESULTS**: 3/3 pages HTTP 200; all 3 expose real image URLs via `data-src` (17 / 27 / 40), previously undetected because the prior pilot only read `src` (which is a site-wide placeholder).

**BROWSER_RENDER_RESULTS**: 3/3 render + scroll + full-page screenshot succeeded; all 3 PNGs decode, non-blank, manually spot-checked to show real design content.

**NETWORK_IMAGE_RESULTS**: 622 total logged image/document responses across 3 cases (179 / 204 / 236 image responses); placeholder responses ≤1 per case after scroll.

**DIRECT_IMAGE_ACCESS_RESULTS**: 84/84 (100%) `data-src` URLs returned HTTP 200 via direct `HEAD` request, no auth.

**VISUAL_WORKFLOW_EVIDENCE_RESULTS**: Partial — final/application designs clearly visible in all 3; case_002 has a moodboard-style slide; case_003 has a 4-colorway comparison grid; no raw sketches or explicit selection/derivation visuals observed in the crops sampled (5 per case, not exhaustive).

**IMAGE_ACCESS_VALIDATION_STATUS**: `PASSED`

**SCALE_UP_SCRAPING_STATUS**: `CONTINUE_TARGETED_ONLY` (recommendation; not acted on this task)
