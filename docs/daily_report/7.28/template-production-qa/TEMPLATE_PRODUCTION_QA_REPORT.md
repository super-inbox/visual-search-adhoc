# Template Production QA Report — 2026-07-28

**Task type:** Read-only QA / audit (no source, config, or Production writes)
**Tested repository:** curify-frontend-prod-template-qa
**Tested commit:** `2d4a89f81946414095c122ca6422aa0ec41b09d3` (`2d4a89f8`)
**Production URL (confirmed from `README.md`, not a fallback assumption):** https://www.curify-ai.com

## Overall status: **PASS_WITH_ISSUES**

10/10 templates were accurately identified from real git diff evidence, 10/10 pass static
integrity checks, and 10/10 are live and reachable on Production with correct titles, categories,
descriptions, and all 80 associated images (10 covers + 40 full-size + 40 preview) loading with
HTTP 200. No blocking defects were found.

**Update 1 — 2026-07-28, automated screenshot review:** Claude directly reviewed all 10 desktop and
all 10 mobile screenshots captured by this QA pass and stored in `screenshots/` (a different thing
from the user's own local browser screenshots referenced in Update 2 below). This confirmed Desktop
rendering is clean 10/10, and flagged a mobile responsive-layout concern plus wide-image
card-thumbnail cropping on 3 templates, and a search-bar query mismatch — all recorded at the time
as `NEEDS_MANUAL_REVIEW` pending confirmation in a real browser.

**Update 2 — 2026-07-28, User manual visual review (authoritative, supersedes Update 1's mobile
conclusion):** the user independently opened and manually inspected all 10 Production template
pages in Chrome DevTools responsive mode, at real mobile viewports (~400×943 and ~430×932). Claude
did not view the user's local screenshots for this round — every finding attributed below to
**"User manual visual review"** is transcribed from the user's reported observations, not from
images Claude examined directly. Full detail is in `MANUAL_VISUAL_REVIEW.md`.

This manual review **corrects** the earlier automated-screenshot conclusion on mobile: the mobile
two-column example grid is usable on all 10 templates — there is **no** severe horizontal page
overflow and **no** unusable/cut-off second column, contrary to what the automated screenshot pass
had suggested. The confirmed mobile issue is narrower: the shared floating mobile header (search
icon + language toggle) overlaps the page H1, affecting title readability only — **MEDIUM**
severity, non-blocking, a shared template-page responsive-layout issue not specific to the 10 newly
added templates.

The User manual visual review also refines the wide-image card-thumbnail-cropping finding to
**4/10** templates (not 3): Discount Coupon and Certificates are significantly cropped, Puzzle and
STEM are minor-to-medium, and the remaining 6 templates show no meaningful crop. The desktop
search-bar query mismatch remains `NEEDS_MANUAL_REVIEW` — the user's independently-observed query
strings differ entirely from the ones seen in the automated screenshot pass, which is itself
evidence pointing toward session/client-side state rather than a fixed per-template data bug (see
§4.4). None of these findings are blocking. Full detail in §4, final classification in §7.

---

## 1. How the 10 templates were identified

The task brief's theme hints ("mascot, periodic table, movie poster, sticker pack, calendar, logo,
...") were treated as unreliable search leads only, per instructions. The actual introducing
commit was found via `git log --grep`, not assumed to be HEAD:

**Source commit:** `19d9e978e215b0a008f5178e015d11eeaed64227` —
`content-drop(2026-07-28): top10 discovered templates + 40 examples`, an ancestor of tested HEAD
`2d4a89f8`. Only 2 of the 10 brief-provided hints ("puzzle", "coupon") actually matched; the other
8 templates are different from what the hints implied. Full derivation is in
`TEMPLATE_SOURCE_COMMITS.md`.

### The 10 confirmed templates

| # | template_id | Category | Production URL |
|---|---|---|---|
| 1 | `template-workbook-practice-book-cover` | Workbook & Practice-Book Cover | `/nano-template/workbook-practice-book-cover` |
| 2 | `template-promotional-flyer` | Flyer & Promotional-Flyer | `/nano-template/promotional-flyer` |
| 3 | `template-stem-classroom-teaching-aid` | STEM Classroom Teaching-Aid Illustrations | `/nano-template/stem-classroom-teaching-aid` |
| 4 | `template-price-tag-product-label` | Price Tag & Product Label | `/nano-template/price-tag-product-label` |
| 5 | `template-achievement-certificate-award` | Certificates & Achievement Awards | `/nano-template/achievement-certificate-award` |
| 6 | `template-perfume-cosmetic-bottle-mockup` | Perfume & Cosmetic Bottle Packaging | `/nano-template/perfume-cosmetic-bottle-mockup` |
| 7 | `template-chocolate-giftbox-packaging` | Chocolate & Specialty Gift-Box Packaging | `/nano-template/chocolate-giftbox-packaging` |
| 8 | `template-jigsaw-puzzle-box` | Puzzle & Jigsaw Collectible | `/nano-template/jigsaw-puzzle-box` |
| 9 | `template-discount-coupon-voucher` | Discount Coupon & Promotional Voucher | `/nano-template/discount-coupon-voucher` |
| 10 | `template-fridge-magnet-merch` | Fridge Magnet & Small Merch-Item | `/nano-template/fridge-magnet-merch` |

All URLs are on `https://www.curify-ai.com` (English, default locale, no path prefix per
`i18n/routing.ts` `localePrefix: "as-needed"`). Full field-level detail (title, description,
og_image, topics, rank_score, parameters, all 40 example IDs, declared aspect ratios) is in
`TEMPLATE_PRODUCTION_MANIFEST.json`.

---

## 2. Static integrity checks — 10/10 PASS

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Template registration exists | PASS 10/10 | `public/data/nano_templates.json`, commit `19d9e978` diff |
| 2 | JSON/config parses cleanly | PASS | `python3 -c "import json; json.load(...)"` on both data files + all 10 `messages/{locale}/nano.json` |
| 3 | template ID unique | PASS | 346/346 unique IDs catalog-wide, 0 duplicates |
| 4 | slug unique | PASS | slug = `id` minus `template-` prefix; IDs unique ⇒ slugs unique |
| 5 | Required fields complete | PASS | `id`, `locales.en.base_prompt`, `locales.en.parameters`, `og_image`, `topics`, `rank_score`, `allow_generation` all present on all 10 |
| 6 | title / description non-empty | PASS 10/10 | `messages/en/nano.json` title+category+description non-empty for all 10 |
| 7 | category/tags match schema | PASS | consistent with other 336 catalog templates' shape |
| 8 | Cover asset reference correct | PASS | `og_image` on each of the 10 points to one of that template's own 4 examples (no cross-wiring) |
| 9 | Example references correct | PASS | 40/40 examples, `template_id` back-reference correct on all |
| 10 | Local repo assets exist | **NOT_APPLICABLE** | `public/images/` is `.gitignore`d project-wide (verified against an older, live template — same pattern); images are CDN-served at runtime, verified in §3 instead |
| 11 | Images decode cleanly | PASS (10/10 sampled) | Downloaded 1 full-size PNG per template from CDN, decoded with Pillow 10.2.0 — no corruption |
| 12 | Image format/size/ratio sane | PASS (10/10 sampled) | Actual aspect ratio within 0.7% of each template's declared ratio (3:4, 4:5, 1:1, 2:3, 4:3, 5:2 as applicable) |
| 13 | No local absolute paths (`/Users/...`) | PASS | `git show 19d9e978 \| grep "/Users/\|/home/"` → no matches |
| 14 | No dead relative paths | PASS | all `og_image`/`image_url`/`preview_image_url` resolved 200 on CDN (§3) |
| 15 | No cross-template image mixing | PASS | every example's image filename verified to start with its own `template_id` |
| 16 | No duplicate IDs/slugs/asset bindings | PASS | 0 duplicate template IDs (346 total), 0 duplicate example IDs (3550 total), 0 duplicate `image_url`/`preview_image_url` |
| 17 | style/layout params match schema | PASS | each template's `parameters` array uses the same `{name,label,type,placeholder}` shape as the rest of the catalog |
| 18 | params have a consumer in code | PASS (8/10 fields) — see note | `lib/nano_utils.ts`, `nano-template/[slug]/page.tsx`, `example/[exampleId]/page.tsx` all read these fields (traced file:line by a dedicated research pass); `base_rank_score` and `creation_date` are written by build-time generator scripts only, not read by runtime app code — informational, not a defect |
| 19 | Locale completeness per project's actual requirement | PASS 10/10 × 10/10 | UI-string layer (`messages/{locale}/nano.json` title/category/description) is 100% complete for all 10 locales × 10 templates. Per-template *generation-prompt* localization (`nano_templates.json` `locales.{other}`) is **not** a project-wide requirement — 282/346 (81.5%) of all catalog templates only have an `en` prompt locale, so these 10 matching that majority pattern is normal, not a gap. |
| 20 | No secret/token/local-path leakage | PASS | `git show 19d9e978 \| grep -iE "api[_-]?key\|secret\|token\|password\|AKIA\|sk-\|bearer"` → no matches |

---

## 3. Production launch checks — 10/10 live

| # | Check | Result |
|---|---|---|
| 1 | Findable via public entry point | PASS — direct detail-page route `nano-template/{slug}`, confirmed from `app/[locale]/(public)/nano-template/[slug]/page.tsx` + `lib/nano_pure.ts:toSlug()` |
| 2 | HTTP status | PASS 10/10 → `200` (see `logs/page_status.csv`) |
| 3 | No 404 / bad redirect | PASS — all 10 `curl -L` final URLs matched the requested URL exactly, single hop |
| 4 | Page `<title>` matches template | PASS 10/10 — exact match to `messages/en/nano.json[id].title` |
| 5 | On-page title matches config | PASS 10/10 — H1 + category chip + description visible and correct in screenshots |
| 6 | Cover image loads | PASS 10/10 — `og:image` meta tag → `cdn.curify-ai.com`, HTTP 200, `image/jpeg` |
| 7 | Example images load | PASS 40/40 (`image_url`) + 40/40 (`preview_image_url`) → HTTP 200, correct `image/*` content-type (see `logs/image_status.csv`) |
| 8 | Public CTA visible | PASS — "Make your own" buttons visible per example card, "Copy / Save / Share" visible in the reproduce-template panel (not clicked — read-only) |
| 9 | No write/points-consuming action taken | Confirmed — no button clicks, no generation requests, no login |
| 10 | No JS console errors | **BLOCKED** — see §5 |
| 11 | No broken key image/script loads | PASS (per screenshots, all visible images rendered — see §4) |
| 12 | Desktop viewport renders correctly | PASS 10/10 — see `screenshots/desktop/` |
| 13 | Mobile viewport renders | PASS_WITH_ISSUES 10/10 — two-column example grid confirmed **usable** by User manual visual review; MEDIUM, header/H1 overlap only, see §4.2 |

Images were served from `https://cdn.curify-ai.com` (confirmed via downloaded HTML `og:image` meta
tags), not from the app's own domain — this is the project's standard CDN pattern (`next.config.ts`
`remotePatterns` allow-lists `cdn.curify-ai.com`), consistent across the whole catalog.

---

## 4. Visual checks

Two independent review passes are documented in this section:

- **Automated screenshot review** (2026-07-28): screenshots captured for all 10 templates × 2
  viewports (desktop 1440×1000, mobile 390×844) via headless Chrome (a pre-existing system
  application — no install performed), saved to `screenshots/desktop/` and `screenshots/mobile/`,
  and reviewed directly by Claude.
- **User manual visual review** (2026-07-28, authoritative for mobile and per-template crop
  detail): the user manually opened and inspected all 10 live Production template pages in Chrome
  DevTools responsive mode at real mobile viewports (~400×943 and ~430×932). **Claude did not view
  the user's local screenshots for this pass** — every finding below labeled "User manual visual
  review" is transcribed from the user's reported observations. Full method and per-template
  results are in `MANUAL_VISUAL_REVIEW.md`.

Where the two passes disagree (mobile layout severity), the User manual visual review is treated
as authoritative, since it reflects true browser rendering rather than a headless-CLI screenshot.

### 4.0 Per-template result summary (User manual visual review)

| # | Template | Content/registration | Desktop page | Mobile example grid | Crop severity |
|---|---|---|---|---|---|
| 1 | Workbook & Practice-Book Cover | PASS | PASS | PASS | None |
| 2 | Flyer & Promotional-Flyer | PASS | PASS | PASS | None |
| 3 | STEM Classroom Teaching-Aid Illustrations | PASS | PASS_WITH_ISSUES | PASS_WITH_ISSUES | Minor to Medium |
| 4 | Price Tag & Product Label | PASS | PASS | PASS | None |
| 5 | Certificates & Achievement Awards | PASS | PASS_WITH_ISSUES | PASS_WITH_ISSUES | Medium (significant) |
| 6 | Perfume & Cosmetic Bottle Packaging | PASS | PASS | PASS | None |
| 7 | Chocolate & Specialty Gift-Box Packaging | PASS | PASS | PASS | None |
| 8 | Puzzle & Jigsaw Collectible | PASS | PASS_WITH_ISSUES | PASS_WITH_ISSUES | Minor to Medium |
| 9 | Discount Coupon & Promotional Voucher | PASS | PASS_WITH_ISSUES | PASS_WITH_ISSUES | Medium to High (most severe) |
| 10 | Fridge Magnet & Small Merch-Item | PASS | PASS | PASS | None |

Across all 10, User manual visual review confirmed: Production page opens, title and description
are present, all 4 examples are present, all images load, images match the template's theme, "Make
your own" CTAs are present, the "Reproduce this template" panel is present, and no 404s, broken
images, missing assets, or cross-template image mixing were found. Per-template narrative detail
(what exactly was cropped, why each status was assigned) is in `MANUAL_VISUAL_REVIEW.md`.

### 4.1 Desktop — 10/10 PASS on core structure, 4/10 also show the card-crop issue

All 10 templates are live with core content rendering correctly: H1 title, category chip,
description, images, CTAs, and the "Reproduce this template" parameter panel populated with real
placeholder values and a working prompt preview. No blocking defects on any template. Of the 10,
4 templates (Certificates, Puzzle, Discount Coupon, STEM) additionally show the card-thumbnail
cropping issue described in §4.3 on the desktop example grid as well as mobile — see that section
for detail. This does not change the PASS classification for template availability or core content;
it is tracked separately as a presentation-layer issue.

### 4.2 Mobile — PASS_WITH_ISSUES (MEDIUM, shared header/H1 overlap only, 10/10 affected)

**Correction (User manual visual review supersedes the automated screenshot pass on this point):**
the automated headless-Chrome screenshot review had described the mobile issue as including severe
horizontal page overflow and an unusable/cut-off second card column. The user's manual check, done
in Chrome DevTools responsive mode across all 10 templates at ~400×943 and ~430×932, **does not
confirm that description** and it is retracted:

- The mobile two-column example grid **is usable** on all 10 templates — no severe horizontal
  overflow of the page, and the second column is not cut off or unusable.
- The confirmed issue is narrower: **the shared floating mobile header (search icon + language
  toggle) overlaps the page H1**, affecting title readability only.

| | |
|---|---|
| Issue | Shared mobile header overlaps page H1 |
| Severity | Medium |
| Scope | Shared template-page responsive-layout issue, not specific to the newly added template data |
| Blocking | No |

This matches the earlier control check (the same header-overlap pattern was also seen on an older,
unrelated, already-live template, `character-analysis-zh`) — it remains a sitewide, pre-existing
issue inherited by these 10 templates, not a regression caused by this content drop. Overall status
remains `PASS_WITH_ISSUES`.

### 4.3 Card-thumbnail cropping on non-square source images — MEDIUM (4/10 templates, per User manual visual review)

The template files and image assets are valid. **The crop issue is caused by the shared
example-card preview layout, not by corrupted or incorrectly generated template assets.** Per-
template severity (User manual visual review):

- **Discount Coupon & Promotional Voucher** (5:2 wide source) — **most severe of the 10**. The
  uniform, taller-than-wide preview area crops the wide coupon heavily left/right; business name,
  offer details, expiry date, or terms are often not fully visible. Not blocking, but the preview
  does not adequately represent the full design. Crop severity: **Medium to High**.
- **Certificates & Achievement Awards** (4:3 landscape source) — landscape certificates in the
  same uniform, taller-than-wide preview area; left/right portions and some certificate text are
  visibly cropped. Crop severity: **Medium**.
- **Puzzle & Jigsaw Collectible** (4:3 landscape source) — light-to-moderate left/right cropping;
  the template theme is still understandable. Crop severity: **Minor to Medium**.
- **STEM Classroom Teaching-Aid Illustrations** (1:1 square per the declared prompt) — the main
  equipment subject displays, but teaching labels/captions near the left/right edges show light-to-
  moderate cropping. Crop severity: **Minor to Medium**.
- **Chocolate & Specialty Gift-Box Packaging** (1:1) — asset ratio matches the card; no meaningful
  crop.
- **Fridge Magnet & Small Merch-Item** (1:1) — displays fully; no crop.
- **Perfume & Cosmetic Bottle Packaging** (3:4 vertical) — matches the card; bottle body fully
  visible; no crop.
- **Price Tag & Product Label** (2:3 vertical) — matches the card; price, product name, and barcode
  are essentially intact; no crop.
- **Flyer & Promotional-Flyer** (4:5 vertical) — displays normally; small text in the mobile
  thumbnail is a function of the source asset's information density, not abnormal cropping.
- **Workbook & Practice-Book Cover** (3:4 vertical) — matches the card; no crop. (One mobile card
  title shows an ellipsis on a long title — a text-space constraint, not an asset or template
  error.)

The full, uncropped image still loads correctly on the detail page and via direct CDN access
(confirmed in §3) — this is a card-thumbnail display issue, not a broken, missing, or wrong image.
Recorded as `MEDIUM` overall (not blocking); **no code change was made in this QA pass.**

**Pattern observed** (root cause is the shared card aspect ratio, not the assets):

- Generally displays well: 1:1, 2:3, 3:4, 4:5
- More likely to be cropped: 4:3 landscape, 5:2 wide landscape, and square educational diagrams
  that contain important edge labels (e.g. STEM)

**Suggested follow-up directions (recorded for future consideration only — not implemented in this
QA pass, no code was changed):**
- aspect-ratio-aware card preview
- `object-fit: contain` for information-dense or wide assets
- a horizontal preview variant
- per-template preview-fit metadata
- dynamic card aspect ratio

### 4.4 Search-bar query vs. page content mismatch — NEEDS_MANUAL_REVIEW (majority of 10/10, two independent observations)

Two independent passes, on two different days/sessions, each observed a search-bar query string
that does not match the template page it's shown on — but the **specific strings differ entirely**
between the two passes, which is itself useful evidence (see analysis below).

**Automated screenshot review** (Claude reviewing headless-Chrome screenshots):

| Template page | Search-bar text shown |
|---|---|
| `workbook-practice-book-cover` | "english spanish word comparison" |
| `promotional-flyer` | "world history timeline poster" |
| `stem-classroom-teaching-aid` | "east asian culture comparison" |
| `price-tag-product-label` | "world history timeline poster" |
| `achievement-certificate-award` | "quick recipe meal prep guide" |
| `perfume-cosmetic-bottle-mockup` | "vintage nostalgia infographic poster" |
| `chocolate-giftbox-packaging` | "east asian culture comparison" |
| `jigsaw-puzzle-box` | "generation comparison nostalgia infographic" |
| `discount-coupon-voucher` | "evolution snacks infographic" |
| `fridge-magnet-merch` | "world history timeline poster" |

**User manual visual review** (independent browser session, same day):

| Template page | Search-bar text shown |
|---|---|
| `workbook-practice-book-cover` | "beauty step by step guide" |
| `promotional-flyer` | "diy home decor ideas" |
| `stem-classroom-teaching-aid` | "interior design home guide" |
| `price-tag-product-label` | "quick recipe meal prep guide" |
| `achievement-certificate-award` | "english spanish word comparison" |
| `perfume-cosmetic-bottle-mockup` | "english spanish word comparison" |
| `chocolate-giftbox-packaging` | "world cuisine food poster" |
| `jigsaw-puzzle-box` | "weird science facts infographic" |
| `discount-coupon-voucher` | "interior design home guide" |
| `fridge-magnet-merch` | "kids english animals vocabulary cards" |

In neither pass does the shown string relate to the template category it's displayed under. Within
each pass, some templates share an identical string (e.g. three templates showed "world history
timeline poster" in the automated pass; `stem-classroom-teaching-aid` and `discount-coupon-voucher`
both showed "interior design home guide" in the User manual visual review; `achievement-
certificate-award` and `perfume-cosmetic-bottle-mockup` both showed "english spanish word
comparison"). Between the two passes, **no template shows the same string in both** — the values
changed entirely between sessions.

**Status: `NEEDS_MANUAL_REVIEW`.** This is not classified as a template-registration or template-
content bug without further evidence. The fact that the observed strings differ completely between
two independent sessions on the same day is consistent with — though does not prove — the search
input preserving whatever query was used before navigating to the template page, via client- or
session-side state, rather than the template page itself carrying or generating that string.

**Possible explanation:** the search input may preserve the query used before navigating to the
template page through client/session state.

**Suggested follow-up:** verify whether the search field is intentionally persistent, URL-state
driven, or stale client state.

No stretched images, no fallback-image states observed, no cross-template image bleed.

---

## 5. BLOCKED items (environment constraints — not skipped, not faked)

| Item | Reason BLOCKED |
|---|---|
| Browser console / network-tab error capture | `playwright` is declared in `package.json` but **not installed** (`node_modules` does not exist in this checkout). Per the task's hard constraint, no `npm install` / `playwright install` was run. No alternative CDP-capable tool was available. Screenshot capture was still possible via the pre-existing system Chrome.app in plain headless-CLI mode, but that mode does not expose `console.*` output in a scriptable way. |
| Login-gated / generation-gated flows | Out of scope per task brief (no login, no points consumption, no POST). Not attempted. |
| Real image-generation test of the 10 templates | Out of scope per task brief. Not attempted — only pre-existing example images were checked. |

These are the only BLOCKED items. They do not, in combination, rise to the level of
`INCOMPLETE_DUE_TO_BLOCKERS`: the critical Production checks (page reachability, title/content
match, image load, visual render) were all completed with real evidence.

---

## 6. Issue severity summary

| Severity | Count | Detail |
|---|---|---|
| Blocking (would require FAIL) | 0 | none found |
| MEDIUM, confirmed via User manual visual review | 2 categories | (1) shared mobile header overlaps page H1 — confirmed on 10/10 templates; mobile two-column example grid itself is usable; sitewide pre-existing pattern, not exclusive to this drop, non-blocking (§4.2); (2) card-thumbnail cropping of non-square source images on 4/10 templates — Discount Coupon (Medium–High, most severe) and Certificates (Medium/significant) most affected, Puzzle and STEM Minor-to-Medium, remaining 6 templates show no meaningful crop (§4.3) |
| NEEDS_MANUAL_REVIEW, cause not yet determined | 1 category | desktop search-bar query text not matching the template page shown, observed independently in two review passes with two entirely different sets of strings — consistent with client/session state rather than a per-template data bug, but not confirmed; see §4.4 |
| Blocked checks (tooling) | 1 category | browser console/network error capture |
| Informational only (not a defect) | 2 | `base_rank_score`/`creation_date` have no runtime consumer (build-tooling only); `nano_templates.json` locale coverage matches the 81.5%-en-only catalog norm |

---

## 7. Final QA classification (post-User-manual-visual-review, 2026-07-28)

- Templates identified: **10/10**
- Templates available in Production: **10/10 PASS**
- Static configuration and assets: **10/10 PASS**
- Desktop page availability and core structure: **10/10 PASS**
- Mobile example grid usability: **10/10 PASS** (confirmed by User manual visual review — two-column grid is usable, not "unusable"/"cut off")
- Shared mobile header/H1 overlap: **10/10 affected, Medium, non-blocking**
- Thumbnail crop:
  - Significant: Discount Coupon, Certificates
  - Minor to Medium: Puzzle, STEM
  - No meaningful crop: Chocolate, Fridge Magnet, Perfume, Price Tag, Flyer, Workbook
- Search field/template-page consistency: **NEEDS_MANUAL_REVIEW**
- Real generation flow: **NOT_TESTED**
- Credit deduction: **NOT_TESTED**
- Browser console error diagnosis: **NOT_VERIFIED** (no CDP-capable tool was available in this
  checkout; not claimed as PASS or FAIL — see §5)

**Overall status: PASS_WITH_ISSUES.**

The 10 newly merged templates are live and usable. The identified issues are shared presentation-
layer concerns rather than missing templates, invalid registrations, broken assets, or incorrect
example bindings.

---

## 8. What was NOT tested (explicitly out of scope per task brief)

Search-algorithm quality, query comparisons, the 326-query search eval, vertical-page development,
SEO refactors, login flows, real template generation/output-image testing, points/credit
deduction, any Production data modification, and fixing any of the findings above — none of these
were performed, per the task brief's explicit exclusions.

---

## 9. Output files in this directory

```
docs/daily_report/7.28/template-production-qa/
├── TEMPLATE_PRODUCTION_QA_REPORT.md   (this file)
├── TEMPLATE_PRODUCTION_QA_RESULTS.csv
├── TEMPLATE_PRODUCTION_MANIFEST.json
├── TEMPLATE_SOURCE_COMMITS.md
├── COMMANDS_AND_EVIDENCE.md
├── MANUAL_VISUAL_REVIEW.md          (user-reported manual browser check, 2026-07-28)
├── screenshots/
│   ├── desktop/  (10 PNGs, one per template)
│   └── mobile/   (10 PNGs, one per template)
└── logs/
    ├── page_status.csv    (10 template-page HTTP checks)
    └── image_status.csv   (80 image HTTP checks)
```

---

## 10. End-of-run integrity check

```
$ git status --short
$ git diff --name-only
$ git diff --stat
```

Confirmed: all files created during this audit are located under
`docs/daily_report/7.28/template-production-qa/`. No existing application source, config, test, or
documentation file was modified. No commit, push, branch, or PR was created. No dependency was
installed or upgraded. No `.env`/credential/secret file was read.
