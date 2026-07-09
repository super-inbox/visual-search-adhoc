# External Screenshot Automation Plan — 2026-07-09

**Status: planning only. No browser collection has been run. No production code, existing scripts, or historical eval data have been modified.**

## Overview

This plan covers how to actually capture the 4 competitor screenshots (Pinterest / Canva / Bing / Google) per case that were left `screenshot_pending` in `docs/daily_report/7.9/competitor_screenshots/` for the 12 selected P0 cases. It inspects the repo's existing Playwright-based collectors (`scripts/bing-image-eval/`, `scripts/google-image-eval/`, `scripts/canva-search-eval/`, `scripts/pinterest-search-eval/`) and proposes the smallest way to point them at these 12 queries instead of their original fixed 58-query eval set — **without editing those scripts or overwriting their historical data.**

## Input

`docs/daily_report/7.9/manual_review/external_screenshot_queries_12_2026-07-09.csv` — the 12 P0 cases, with `safe_query_slug` matching the existing `competitor_screenshots/<slug>/` folder names exactly, `issue_type` carried over from the visual review CSV for traceability, and a `canva_fallback_query` for the simplified retry variant.

## Which Scripts Can Be Reused

All four target-platform folders share an identical, well-built structure — nothing here needs to be written from scratch:

| Module | Reusable as-is? | What it does |
|---|---|---|
| `browser.ts` | ✅ Yes, unchanged | Persistent browser context (tries system Chrome, falls back to Playwright Chromium), viewport, and the platform's search-URL builder |
| `*Consent.ts` / `captcha.ts` | ✅ Yes, unchanged | Cookie-consent auto-accept, login-wall detection, CAPTCHA pause-and-resume (never auto-bypasses) |
| `extractLabels.ts` / `extractResults.ts` | ✅ Yes, unchanged | Label/chip and top-10 result DOM extraction |
| `screenshots.ts` | ⚠️ Reusable logic, not reusable output path | The page1/page2 viewport-screenshot capture function is fine to import as-is; only its hardcoded `SCREENSHOTS_BASE` path (pointed at the old 58-query eval folder) needs to be overridden |
| `queries.ts` | ❌ Do not reuse directly | Hardcoded to the exact 58-query set with an `assertQueries()` sanity check pinned to specific indices/text (e.g. must be exactly 58 items, item 0 must be "单词", item 57 must be "maps"). Editing this in place would corrupt a real historical benchmark file |
| `storage.ts` | ❌ Do not reuse directly | Hardcoded `OUT_DIR = docs/external-signal-pilot/<platform>-58/` and seeds `observations.json` 1:1 from `queries.ts`'s 58 items — there is no way to point it at a different query list without editing it |
| `collect.ts` | ❌ Do not reuse directly | CLI only supports `--query-id` (single item from the 58) or `--start/--end` (a sub-range of the 58) — there is no `--queries-file` flag, so it cannot take an arbitrary custom list today |

**Bottom line: the parts that talk to the browser and the target site are fully reusable. The parts that define *which* queries to run and *where* to save results are hardcoded to the 58-query eval set and must not be edited in place** — that file is real historical data (58/58 Bing, 58/58 Google, 36 ok / 21 login_required / 1 partial Canva, and the corresponding Pinterest run), and `assertQueries()` would throw immediately if the 12-query set were substituted in.

## Smallest Code Change Needed

Do **not** modify `queries.ts`, `storage.ts`, or `collect.ts` in the existing eval folders. Instead, add one small sibling folder per platform (or one shared folder covering all three ready platforms) that imports the reusable modules unchanged and supplies only the two things that differ:

```
scripts/external-screenshot-p0-12/          (new, does not touch existing eval folders)
  queries.ts        — 12 items, loaded from external_screenshot_queries_12_2026-07-09.csv
                      (or hardcoded inline — no assertQueries() constraint needed since
                      this isn't the fixed benchmark set)
  storage.ts         — same shape as the existing storage.ts, but:
                        OUT_DIR = docs/daily_report/7.9/manual_review/external_screenshot_runs/
                        (keeps output out of docs/external-signal-pilot/ entirely, so the
                        historical 58-query datasets are never at risk of being overwritten)
  collect-bing.ts    — imports { createBrowserContext, buildBingImagesUrl, randomDelay }
                        from ../bing-image-eval/browser.js, { detectBlockOrConsent,
                        waitForUserToUnblock } from ../bing-image-eval/bingConsent.js,
                        extractLabels/extractResults from the same folder — copies only
                        collect.ts's per-query loop, driven by the new 12-item queries.ts
  collect-google.ts  — same pattern, importing from ../google-image-eval/*
  collect-canva.ts   — same pattern, importing from ../canva-search-eval/*, plus: after
                        the primary query, if extractResults returns 0 (or a "couldn't
                        find anything" empty state), automatically retry once with
                        canva_fallback_query from the CSV before marking ok_empty
  collect-pinterest.ts — same pattern, written but **not wired to run** until the ToS
                        question below is resolved
```

This reuses 100% of the browser/consent/extraction logic (by import, zero duplication of that logic) and writes perhaps 60–80 lines of new glue code per platform (a query loader + a thin copy of `collect.ts`'s loop with the CSV-driven list and the new output path). It does not touch any file inside `scripts/bing-image-eval/`, `scripts/google-image-eval/`, `scripts/canva-search-eval/`, or `scripts/pinterest-search-eval/`, and it cannot corrupt the existing 58-query `observations.json`/`observations.csv` files because it writes to a different `OUT_DIR` entirely.

**This is a proposal, not yet implemented** — per this task's instructions, no new script files have been created and no browser collection has been run.

## Required npm install / package.json Setup

None of the four platform folders currently have their own `package.json`; only `scripts/curify-search-collect/` does (and its `playwright@^1.61.1` install already has a Chromium binary cached at `~/Library/Caches/ms-playwright/`). Every file across `bing-image-eval/`, `google-image-eval/`, `canva-search-eval/`, and `pinterest-search-eval/` imports only Node built-ins (`fs`, `path`, `url`, `readline`) plus the bare `playwright` package — no `csv-parse`/`csv-stringify` or other dependency is needed for these four.

To make the new `scripts/external-screenshot-p0-12/` folder (or the existing four, if reusing them turns out to be preferred later) actually runnable:

```jsonc
// scripts/external-screenshot-p0-12/package.json (new file, not yet created)
{
  "name": "external-screenshot-p0-12",
  "private": true,
  "type": "module",
  "dependencies": {
    "playwright": "^1.61.1"
  }
}
```

Then, once created:

```bash
cd scripts/external-screenshot-p0-12
npm install
npx playwright install chromium   # already cached from curify-search-collect — likely a fast no-op
```

Running the TypeScript entrypoints follows the same convention already documented in every existing README: `npx tsx path/to/collect-*.ts [options]` (the READMEs assume `tsx`; it is not currently installed anywhere in this repo and would need to be added, either as a `devDependency` here or resolved via `npx tsx` which downloads it on first use).

## How to Pass the 12-Query Input

The new `queries.ts` for this folder would load directly from `docs/daily_report/7.9/manual_review/external_screenshot_queries_12_2026-07-09.csv` (12 rows: `query`, `safe_query_slug`, `primary_scene`, `secondary_scene`, `issue_type`, `platforms_to_capture`, `canva_fallback_query`) instead of a hardcoded array — this is the one piece of real "new" logic (a ~15-line CSV reader), everything else downstream (the collect loop, browser, consent, screenshots) stays a straight import from the existing eval folders. `safe_query_slug` in the CSV already matches the `competitor_screenshots/<slug>/` folder names 1:1, so the collector can write each platform's screenshot straight into the existing folder (e.g. `competitor_screenshots/nct_dream_photocard_template/bing.png`) instead of inventing a new numbering scheme — no renaming or re-mapping step needed after the run.

## Recommended Run Order: Bing → Google → Canva → (Pinterest deferred)

1. **Bing first.** Lowest friction historically (58/58 `ok` in the 2026-06-19/20 run, no login/CAPTCHA hits), and it's the fastest sanity check that the new glue code and CSV loader work end-to-end before spending time on the trickier platforms.
2. **Google second.** Also 58/58 clean historically, but has a documented (manual, non-bypassing) CAPTCHA pause-and-resume flow — worth confirming that flow still triggers correctly (or doesn't need to) before moving to Canva.
3. **Canva third.** This is the platform with **real, confirmed login-wall friction** — 21/58 `login_required` + 1 `partial` in the historical run, concentrated on CJK-language queries. Since 3 of our 12 queries are Chinese (`小红书香薰产品种草图`, `低饱和国风茶包装设计`, `光与夜之恋 卡面设计参考图`), expect this to be the platform most likely to need a manual login-wall resolution or a fallback-query retry. Run this **headful**, not headless, so a login wall can be handled by hand if it appears — same recommendation every existing Canva README already gives.
4. **Pinterest: deferred, not run.** See below.

## Pinterest Status: Technically Possible but Blocked Pending Manager Confirmation

`scripts/pinterest-search-eval/` is a fully-built, working Playwright collector (58/58 `ok` in the historical run — no blocks hit that time) — technically, it is the *easiest* of the four to run based on that history. It is **not being run in this plan** because two other files in this repo explicitly document a prior decision against Playwright automation on Pinterest specifically:

- `data/external_signals/README.md`: *"Automated scraping (Playwright, Puppeteer, headless browsers) against pinterest.com is rejected because: Pinterest has aggressive bot-detection (captcha, rate-limit, IP block); it violates Pinterest's ToS under web crawling restrictions; the repository's benchmark doc explicitly ruled it out."*
- `claude-reports/claude_prompt7_5_manual_pilot_setup.md` (2026-06-19): lists "Playwright/Puppeteer automation" for Pinterest as *"Explicitly rejected (bot-detection, ToS, fragility)"* and names manual browser observation as the approved method instead.

Both documents coexist in the repo alongside the working `pinterest-search-eval` script and its successful historical run — so it's unclear whether that rejection was formally reversed before the script was built and run, or whether the script was built and run without that decision being revisited. Rather than assume either way, **Pinterest automation stays off the table until a manager/owner explicitly confirms whether the ToS objection still applies.** If approved later, `collect-pinterest.ts` can be written and run using the exact same pattern as the other three — no additional technical work beyond what's already described above.

## Failure Handling

Following the exact conventions already built into the existing consent/CAPTCHA modules (reused unchanged, not reinvented):

| Condition | Existing handling (reused as-is) | Recorded as |
|---|---|---|
| `login_required` (Canva, primarily) | Script pauses, prompts for manual login in the open (headful) browser window, then resumes on Enter. Never auto-bypassed. | `status = "login_required"` if unresolved after the pause |
| `captcha` / bot-block (Bing "unusual traffic", Google verification page) | Script pauses, prompts for manual resolution in-browser, resumes on Enter. Never auto-bypassed. | `status = "blocked"` / `"captcha"` if unresolved |
| Cookie `consent` interstitial | Auto-accepted via known selectors (all four platforms have this) | Transparent — proceeds automatically; only surfaces if auto-accept fails |
| Canva zero/poor results on primary query | New behavior for this batch only (not in the original 58-query collectors): automatically retry once with `canva_fallback_query` from the CSV before giving up | `status = "ok"` on fallback with a note recording that the fallback query was used, or `ok_empty` if the fallback also returns nothing |
| Any platform screenshot still not captured (not attempted, or attempted and unresolved) | Matches the convention already established in this batch's `notes.md` files | `screenshot_pending`, with the specific reason (not yet run / login wall / CAPTCHA / error) recorded in that case's `notes.md`, same as the current Pinterest/Canva/Bing/Google-wide `screenshot_pending` state |

No platform is ever auto-bypassed past a login wall or CAPTCHA — that rule is inherited unchanged from every existing script's documented behavior and is not being relaxed for this batch.

## Next Steps

1. Get explicit confirmation on the Pinterest ToS question before writing or running any Pinterest collector for this batch.
2. Create `scripts/external-screenshot-p0-12/` (queries loader + storage override + three collect-*.ts files for Bing/Google/Canva) as described above — this has not been done yet.
3. `npm install` in that new folder, confirm `npx playwright install chromium` is a no-op against the already-cached binary.
4. Dry-run each collector against the 12-query CSV (print-only, no browser) before the first real headful run, matching every existing README's own recommended first step.
5. Run Bing → Google → Canva in that order, headful, watching for the Canva login wall on the 3 Chinese queries in particular.
6. Copy/rename the resulting screenshots into the matching `competitor_screenshots/<safe_query_slug>/{bing,google,canva}.png` slots and update each case's `notes.md` and the `P0_visual_review_with_claude_2026-07-09.csv` (`competitor_screenshots_available`, `best_competitor_platform`, `visual_competitor_observation`) — this closes the loop opened in the prior visual-review pass.
