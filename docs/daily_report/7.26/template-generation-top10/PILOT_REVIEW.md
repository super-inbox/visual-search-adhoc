# Pilot Review — 10 Templates, Example 01 Each

Generated via `scripts/generate_examples.mjs --pilot`, model `gemini-3-pro-image-preview`, single attempt each,
0 failures, 0 retries needed. All 10 pilots visually inspected directly (not just automated checks) before
proceeding to the full batch.

| # | Template | Example | Output | Gen. Status | Structural Consistency | Text Readability | Subject Accuracy | Unexpected Text | Watermark | Clipping | Result | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | T03 Workbook | example-01 | 896x1200, 425KB | success | matches spec (title band / center illustration / footer) | clear, correctly spelled | numbers + abacus motif, on-topic | none | none | none | **PASS** | Grade badge rendered as ribbon in top-right as specified |
| 2 | T04 Flyer | example-01 | 928x1152, 993KB | success | matches spec (headline / hero / offer / footer) | clear, correctly spelled | noodle bowl hero image on-topic for restaurant flyer | none | none | none | **PASS** | Denser info-packed layout correctly distinct from a poster |
| 3 | T02 STEM | example-01 | 1024x1024, 448KB | success | matches spec (title / center equipment / callouts / caption) | clear, correctly spelled | whiteboard illustration accurate, 4 labeled parts | none | none | none | **PASS** | Callout lines correctly point to labeled parts |
| 4 | T05 Price Tag | example-01 | 848x1264, 872KB | success | matches spec (hole+string / brand band / price / product / barcode) | clear, correctly spelled | tag silhouette with string correct | none | none | none | **PASS** | Price is visually dominant as specified |
| 5 | T01 Certificate | example-01 | 1200x896, 640KB | success | matches spec (border / seal / title / name / reason / sig+date) | clear, correctly spelled | certificate framing accurate | none | none | none | **PASS** | Seal, ribbon, and border all present |
| 6 | T07 Perfume | example-01 | 896x1200, 532KB | success | matches spec (center bottle / label / bottom wordmark) | clear, correctly spelled | perfume bottle shape correct (not a sport/water bottle) | none | none | none | **PASS** | Studio lighting and soft shadow present as specified |
| 7 | T06 Chocolate Box | example-01 | 1024x1024, 804KB | success | matches spec (open lid / compartments / ribbon / seasonal badge / label) | clear, correctly spelled | genuinely open box with visible chocolate compartments | none | none | none | **PASS** | Clearly distinct from a generic closed "mystery box" |
| 8 | T08 Puzzle | example-01 | 1200x896, 797KB | success | matches spec (logo band / cover art / piece cutout / count badge) | clear, correctly spelled | landscape cover art on-topic, puzzle-piece cutout present | none | none | none | **PASS** | Piece-count badge legible ("1000 pieces") |
| 9 | T09 Coupon | example-01 | 1632x656, 754KB | success | matches spec (tear line / stub callout / business name / details / barcode) | clear, correctly spelled | ticket/tear-tab shape accurate | none | none | none | **PASS** | Perforated tear line clearly visible |
| 10 | T10 Magnet | example-01 | 1024x1024, 432KB | success | matches spec (die-cut shape / face illustration / bottom wordmark) | clear, correctly spelled | family-photo illustration on-topic for "custom photo" theme | none | none | none | **PASS** | Drop shadow present, single product mockup as specified |

## Summary
- 10/10 pilots: **PASS**, 0 FAIL, 0 NEEDS_REVIEW.
- No systematic issues found (no missing text, no watermarks, no cropped subjects, no structural drift from
  the fixed-layout spec). Automated file/dimension checks (see `QUALITY_REVIEW.md`) corroborate: all files
  non-trivial size, valid PNG, aspect ratio consistent with each template's requested ratio.
- Decision: proceed directly to the full batch (examples 02-04 for all 10 templates, 30 additional generations)
  with the same script/parameters, no prompt changes needed.
