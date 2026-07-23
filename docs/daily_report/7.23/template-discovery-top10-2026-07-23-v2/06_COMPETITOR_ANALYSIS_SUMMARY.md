# Competitor Analysis Summary (V2, revised 2026-07-23)

**V2 changes from v1:** an expanded repository image search (see `02_REPOSITORY_IMAGE_SEARCH_INDEX.csv` and
`02_IMAGE_SEARCH_SUMMARY.md`) found one new real competitor image (T03) and confirmed one previously-excluded
adjacent image as genuinely on-topic and worth including (T06). No exact-match competitor image was found for any
of the 10 candidates. Six candidates remain with no competitor evidence at all.

Three candidates now have direct image-based competitor evidence on file, all adjacent-category (not exact):

- **T07 (Perfume & Cosmetic Bottle Packaging)**: xiaohongshu-aromatherapy competitor case
  (`docs/daily_report/7.9/competitor_screenshots/xiaohongshu_aromatherapy_product_teaser_image/`), real Pinterest,
  Canva, Bing, Google, and Curify screenshots. Adjacent (aromatherapy/scent product, not perfume-bottle-exact),
  scored MEDIUM confidence.
- **T03 (Workbook & Practice-Book Covers) — NEW in V2**: a real Canva screenshot
  (`docs/daily_report/6.19-20/external-signal-pilot/canva-search-eval-58/screenshots/047-phonics-worksheets-kindergarten/canva-search-page1.png`)
  showing a dedicated "Phonics Worksheets Kindergarten templates" category page, paired with Curify's own
  zero-result screenshot for the identical query from the same benchmark run. Adjacent (phonics worksheets, not
  workbook-cover-exact), scored MEDIUM confidence. This upgrades T03 from text-only to real image evidence.
- **T06 (Chocolate & Specialty Gift-Box Packaging) — re-verified and included in V2**: the 7.9
  `low_saturation_chinese_style_tea_packaging_design` Pinterest capture (tea, not chocolate, but same
  low-saturation gift-packaging aesthetic family) was visually re-checked in V2, confirmed genuinely on-topic
  (real tea gift-box/tin product photography), and is now copied into the images/ directory and shown on the card
  — v1 had documented this evidence but chose not to copy it in. The paired Canva capture for the same query was
  checked and found off-topic (general Chinese-aesthetic templates, not packaging) and was excluded.

One candidate (T04 flyer) has **text-only** (not image) competitor evidence: the
`CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md` document records that Canva's own filter-chip taxonomy
explicitly includes "Flyer" / "Travel Flyer" as merchandised template categories. No screenshot of the exact
category-filter view was found even after the expanded V2 search.

The remaining six candidates (T01, T02, T05, T08, T09, T10) still have **no local competitor screenshot or
document** found in any reviewed competitor-analysis artifact, even after the expanded V2 search. This is recorded
honestly as `NOT_FOUND` rather than fabricated — these candidates rely on internal benchmark/screenshot evidence
only, reflected in their lower competitor-evidence sub-score (see `09_TEMPLATE_CANDIDATE_SCORING.csv`,
`competitor_15` column) and their card's "REFERENCE IMAGE NEEDED" placeholder.

No competitor screenshot in this report was captured, generated, or altered for this run — all competitor images
are unmodified copies of pre-existing files from 7/9, 6/19-20, and other prior sessions.
