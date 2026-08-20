# Evidence — Search + Creative Exploration Demo

Every path/URL below was checked to exist or was directly observed during this task's own
preparation session (2026-08-19). Nothing here is invented. Two kinds of evidence are used:
**(A) live production observations made today**, by this task's own browser session, and
**(B) pre-existing archived files** in this repo or in a separate, read-only repo checkout.

---

## A. Live production evidence (observed today, 2026-08-19)

All of the following were checked live against `https://www.curify-ai.com` via direct browser
navigation during this task's preparation. These are the primary source for `DEMO_PLAN.md`'s
click sequence and expected results.

| # | URL | What was observed |
|---|---|---|
| 1 | `https://www.curify-ai.com/` | Homepage: "Don't just make an image. Finish the job." headline; tagline "Curify helps you search inspiration, generate visuals, localize for the world, and scale across every channel"; topic-tab row (Merch & Stickers, Product & E-commerce, Education, Brand Design, Packaging, Social Media, World Cup, MBTI & Characters, Travel, Food…). No nav entry for Brand Direction Explorer anywhere on this page. |
| 2 | `https://www.curify-ai.com/search?q=modern%20tea%20brand%20identity` | "Few results for 'modern tea brand identity'..." banner; top-row Examples results: "Tea Brand — Contemporary Vibrant," "Tea Brand — Earthy Elegance," "Tea Brand — Heritage 国风," then "PAW PARADISE IP Material Design Specification," "bubble tea shop," "Panda tea master." |
| 3 | Click-through from the "Tea Brand — Earthy Elegance" result card | Landed on `https://www.curify-ai.com/nano-template/food-product-packaging-design/example/template-food-product-packaging-design-tea-earthy-elegance` — a **Food Product Packaging Design Generator** template page (a single-parameter "Make It Yours" generation tool), unrelated to Brand Direction Explorer. Direct, live proof that Search result clicks do not lead to Creative Exploration. |
| 4 | `https://www.curify-ai.com/topics/branding` (via the homepage "Brand Design" tab) | Clean grid, no results-warning banner. Includes a full "BREW & CO" coffee-shop brand board (logo, cup mockup, tote bag, "GOOD COFFEE. GOOD MOOD." tagline), "CATTÉ COFFEE 喵咖" branding, and a "北岳茶事"-style tea-brand font/logo exploration card. Used as the documented fallback search step in `DEMO_PLAN.md` §3. |
| 5 | `https://www.curify-ai.com/tools/brand-direction-explorer` | Brand Direction Explorer, live on production. "Explore three creative directions from one brief." 4 scenario tabs: **Coffee shop opening poster**, **Chinese tea brand style exploration**, **Market / community event poster**, **From your brief** (this 4th tab was not exercised/tested and is not referenced further in this demo plan). Includes a live "VISUAL PREFERENCE (OPTIONAL)" Prefer/Avoid section — this is the feature `docs/daily_report/8.16/creative-direction-product-iteration/` describes as uncommitted local-only work; it has since shipped to production. |
| 6 | Live test run: "Chinese tea brand style exploration" tab, filled with the exact 山岚茶事 brief from `DEMO_PLAN.md` §3 | Debounced auto-fetch fired after field entry; ~8s later, three direction cards rendered: **Modern Minimalism / 现代极简主义**, **Cultural Contemporary / 文化当代**, **Serene Zen / 宁静禅意** — each with a distinct tagline, description, and 4 style tags. Clicking a card shows a "SELECTED" badge and enables the "Generate visual" button ("1 image per generation · 5 credits"). Stage-2 image generation itself was **not** executed (requires login/credit spend — left for the actual presenter to do live; see `DEMO_PLAN.md` §6). |
| 7 | Live test run: "Coffee shop opening poster" tab, filled with a "Brew & Co" brief | Returned three real but repetitive titles: "Brew & Co Coffee Shop," "Welcome to Brew & Co," "Discover Brew & Co." This live observation is the basis for `DEMO_PLAN.md` §1's recommendation to prefer the tea scenario over coffee for the recording. |

---

## B. Archived files — this repo (`visual-search-adhoc`)

| Path | Relevance |
|---|---|
| `docs/daily_report/8.16/creative-direction-product-iteration/README.md`, `FINDINGS.md`, `real_paired_evaluation.csv`, `real_paired_runs.jsonl`, `gallery.html` | Documents the "Visual preference" feature build (now live in production per §A.5), the duplicate-title fix, and the 3 real scenarios' names/behavior as of 2026-08-17. Background context; superseded where it conflicts with §A above (see `DEMO_PLAN.md` §2). |
| `docs/daily_report/8.16/creative-direction-trajectory/README.md`, `FINDINGS.md`, `TRAJECTORY_SCHEMA.md` | Contains the "Audit correction" section explaining the two-worktree history of Brand Direction Explorer, and the original discovery that the tool is real (2026-08-16). Also documents that the coffee-opening case had an exact-duplicate-title bug ("Morrow Coffee" ×3) in an earlier real run — relevant background for why `coffee-opening` is not the primary demo scenario. |
| `docs/daily_report/8.16/creative-direction-trajectory/gallery.html` | Internal gallery viewer for the above trajectory dataset — not used directly in the demo, background reference only. |

## C. Archived files — separate repo checkout (`curify-frontend-brand-direction-explorer`, read-only)

This is a separate local git worktree of the `curify-frontend` repository
(`/Users/baobaoli/Desktop/curify-frontend-brand-direction-explorer`, branch
`baobao/brand-direction-explorer-tool-demo-2026-08-04`). **It was only read for this task, never
modified**, consistent with the "do not modify curify-frontend" constraint.

| Path (relative to that repo root) | Relevance |
|---|---|
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/FINAL_REPORT.md` | Full real end-to-end validation report (2026-08-07): implementation scope, test results (54/54 unit tests, `npm run build` passing), and a 3-case results table confirming `coffee-opening` had the duplicate-title issue while `tea-brand-exploration` and `event-poster` did not. |
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/input.txt` | The exact brief text used for the primary demo scenario (§ above, also in `DEMO_PLAN.md` §3). |
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/notes.txt` | Real run notes: HTTP 200, ~8.63s round-trip, 3 unique direction ids, UI-confirmed rendering. |
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/stage1-directions.json` | Raw real Stage-1 API response for this scenario (2026-08-07 run) — an earlier real generation of the same brief; today's live re-run (§A.6) returned different but comparably distinct direction titles, since generation is non-deterministic. |
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/stage1-directions-full-page-corrected.png` | Archived Stage-1 UI screenshot — Stage-1 fallback image per `DEMO_PLAN.md` §6. |
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/generated-output-primary.jpg` | Archived real Stage-2 output (sage-green ceramic tea jar moodboard) — Stage-2 fallback image per `DEMO_PLAN.md` §6. |
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/02-shanlan-tea/generated-output-alternative.jpg` | Archived real Stage-2 output (red-and-gold lacquered tea tin poster) — Stage-2 fallback image per `DEMO_PLAN.md` §6. |
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/03-afterglow-market/input.txt` | Exact brief for the backup scenario (`DEMO_PLAN.md` §7). |
| `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/01-morrow-coffee/` | Archived real run showing the original coffee-opening duplicate-title bug ("Morrow Coffee" ×3) — background evidence for why coffee is not the primary scenario. |

**Note on repo boundaries:** none of these `curify-frontend-brand-direction-explorer` files were
copied into `visual-search-adhoc`. This document only records their existing, real paths for
reference during recording — consistent with "work only inside visual-search-adhoc" for new
deliverables while still pointing at genuine supporting evidence where it actually lives.
