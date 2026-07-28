# Manual Visual Review — 2026-07-28

**Source of this document:** the user performed this review directly in their own browser and
reported the results in chat. **Claude did not view the user's local screenshots.** This file is a
structured transcription of the user's reported observations, not an independent Claude
observation. Every conclusion in this file should be read as "User manual visual review," and is
cited that way in `TEMPLATE_PRODUCTION_QA_REPORT.md`.

This review supersedes the mobile-layout conclusion of the earlier automated screenshot review
(headless-Chrome CLI screenshots, reviewed directly by Claude, documented in
`COMMANDS_AND_EVIDENCE.md` §13 and `TEMPLATE_PRODUCTION_QA_REPORT.md` §4.1/4.2 "automated
screenshot review"). It does not replace the desktop findings from that pass, which remain
Claude-observed and are consistent with this review's per-template crop findings.

## Method

| | |
|---|---|
| Test date | 2026-07-28 |
| Test method | Chrome DevTools responsive mode (real browser rendering, not headless CLI) |
| Viewports | ~400×943 and ~430×932 |
| Coverage | 10/10 templates, manually opened and refreshed |
| Checked per template | Title, description, all 4 examples, image loading, image cropping, mobile layout, CTA, "Reproduce this template" section |

## 1. Shared mobile header / H1 overlap

All 10 Production template pages were manually opened and refreshed at ~400×943 and ~430×932.

Confirmed:
1. The mobile layout uses a two-column example card grid, and **all 10 pages are browsable** in
   this layout.
2. **No** severe horizontal page overflow was found, and the second card column is **not**
   unusable or cut off — this corrects the earlier automated screenshot review's description.
3. The one confirmed issue: the shared floating mobile header (search icon + language toggle)
   overlaps the page H1 title.

| | |
|---|---|
| Issue | Shared mobile header overlaps page H1 |
| Severity | Medium |
| Scope | Shared template-page responsive-layout issue, not specific to the newly added template data |
| Blocking | No |

More precisely:
- Mobile two-column example grid is usable.
- The shared floating mobile header controls overlap portions of the page H1.
- The issue affects title readability but does not block access to the template examples.

## 2. Per-template manual visual results

All 10 templates confirmed: Production page opens; title and description present; all 4 examples
present; images load; images match the template theme; "Make your own" button present;
"Reproduce this template" section present; no 404, broken image, missing asset, or obvious
cross-template image mixing found.

### 1. Certificates & Achievement Awards (`achievement-certificate-award`)
- Template/content: PASS
- Desktop page: PASS_WITH_ISSUES
- Mobile example grid: PASS_WITH_ISSUES
- Notes: source images are 4:3 landscape certificates, displayed in a shared, taller-than-wide
  preview area. Left/right portions and some certificate text are visibly cropped.
- Crop severity: **Medium**

### 2. Chocolate & Specialty Gift-Box Packaging (`chocolate-giftbox-packaging`)
- Template/content: PASS
- Desktop page: PASS
- Mobile example grid: PASS
- Notes: 1:1 source images match the card ratio; no meaningful crop observed.
- Crop severity: **None**

### 3. Discount Coupon & Promotional Voucher (`discount-coupon-voucher`)
- Template/content: PASS
- Desktop page: PASS_WITH_ISSUES
- Mobile example grid: PASS_WITH_ISSUES
- Notes: source images are 5:2 wide coupons. The shared, taller-than-wide preview area causes
  severe left/right cropping — business name, discount details, expiry date, or terms are often
  not fully visible. This is the most visible thumbnail-crop issue among the 10 templates.
- Crop severity: **Medium to High**
- Blocking: No, but the preview does not adequately represent the full design.

### 4. Fridge Magnet & Small Merch-Item (`fridge-magnet-merch`)
- Template/content: PASS
- Desktop page: PASS
- Mobile example grid: PASS
- Notes: 1:1 source images display in full.
- Crop severity: **None**

### 5. Puzzle & Jigsaw Collectible (`jigsaw-puzzle-box`)
- Template/content: PASS
- Desktop page: PASS_WITH_ISSUES
- Mobile example grid: PASS_WITH_ISSUES
- Notes: source images are 4:3 landscape puzzle-box covers. Light-to-moderate left/right cropping
  in the card; the template theme remains understandable.
- Crop severity: **Minor to Medium**

### 6. Perfume & Cosmetic Bottle Packaging (`perfume-cosmetic-bottle-mockup`)
- Template/content: PASS
- Desktop page: PASS
- Mobile example grid: PASS
- Notes: 3:4 vertical source images match the card; bottle body displays in full.
- Crop severity: **None**

### 7. Price Tag & Product Label (`price-tag-product-label`)
- Template/content: PASS
- Desktop page: PASS
- Mobile example grid: PASS
- Notes: 2:3 vertical source images match the card; price, product name, and barcode are
  essentially intact.
- Crop severity: **None**

### 8. Flyer & Promotional-Flyer (`promotional-flyer`)
- Template/content: PASS
- Desktop page: PASS
- Mobile example grid: PASS
- Notes: 4:5 vertical source images display normally. Small text in the mobile thumbnail is a
  function of the source asset's information density, not abnormal cropping.
- Crop severity: **None**

### 9. STEM Classroom Teaching-Aid Illustrations (`stem-classroom-teaching-aid`)
- Template/content: PASS
- Desktop page: PASS_WITH_ISSUES
- Mobile example grid: PASS_WITH_ISSUES
- Notes: the prompt declares a 1:1 square output. The main equipment subject displays, but teaching
  labels/captions near the left/right edges show light-to-moderate cropping.
- Crop severity: **Minor to Medium**

### 10. Workbook & Practice-Book Cover (`workbook-practice-book-cover`)
- Template/content: PASS
- Desktop page: PASS
- Mobile example grid: PASS
- Notes: 3:4 vertical source images match the card. The first mobile card shows an ellipsis on a
  long title — a text-space constraint from the title length, not an asset or template error.
- Crop severity: **None**

## 3. Unified card-preview-ratio conclusion

The template files and image assets are valid. The crop issue is caused by the shared
example-card preview layout rather than corrupted or incorrectly generated template assets.

Pattern observed:

**Generally displays well:**
- 1:1
- 2:3
- 3:4
- 4:5

**More likely to be cropped:**
- 4:3 landscape
- 5:2 wide landscape
- Square educational diagrams containing important edge labels

**Suggested follow-up directions (recorded only — no code was changed as part of this review):**
- aspect-ratio-aware card preview
- `object-contain` for information-dense or wide assets
- horizontal preview variant
- per-template preview-fit metadata
- dynamic card aspect ratio

## 4. Search-bar query vs. page content, observed during this manual review

Multiple pages retained a top search-bar query unrelated to the current template, for example:

| Template page | Search-bar text shown |
|---|---|
| `achievement-certificate-award` | "english spanish word comparison" |
| `chocolate-giftbox-packaging` | "world cuisine food poster" |
| `discount-coupon-voucher` | "interior design home guide" |
| `fridge-magnet-merch` | "kids english animals vocabulary cards" |
| `jigsaw-puzzle-box` | "weird science facts infographic" |
| `perfume-cosmetic-bottle-mockup` | "english spanish word comparison" |
| `price-tag-product-label` | "quick recipe meal prep guide" |
| `promotional-flyer` | "diy home decor ideas" |
| `stem-classroom-teaching-aid` | "interior design home guide" |
| `workbook-practice-book-cover` | "beauty step by step guide" |

Status: **NEEDS_MANUAL_REVIEW**

Possible explanation: the search input may preserve the query used before navigating to the
template page through client/session state.

Do not classify this as a template-registration or template-content bug without further evidence.

Suggested follow-up: verify whether the search field is intentionally persistent, URL-state
driven, or stale client state.

## 5. Overall

- Templates identified: 10/10
- Templates available in Production: 10/10 PASS
- Static configuration and assets: 10/10 PASS
- Desktop page availability and core structure: 10/10 PASS
- Mobile example grid usability: 10/10 PASS
- Shared mobile header/H1 overlap: 10/10 affected, Medium, non-blocking
- Thumbnail crop: significant on Discount Coupon and Certificates; minor-to-medium on Puzzle and
  STEM; no meaningful crop on Chocolate, Fridge Magnet, Perfume, Price Tag, Flyer, Workbook
- Search field/template-page consistency: NEEDS_MANUAL_REVIEW
- Real generation flow: NOT_TESTED
- Credit deduction: NOT_TESTED

The 10 newly merged templates are live and usable. The identified issues are shared
presentation-layer concerns rather than missing templates, invalid registrations, broken assets, or
incorrect example bindings.
