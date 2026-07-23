# Repository Image Search Summary

Scope: recursive filename/directory keyword search across `docs/daily_report/` (~1,600 image files: png/jpg/jpeg/webp)
for all 10 candidate keyword groups (EN + ZH), followed by direct visual inspection of every filename/keyword match
that was not already accounted for in the v1 package. A background research-agent run for this step failed
mid-stream (API connection error, no output files produced); the search below was performed directly instead of
retried, using targeted `find`/`grep` filename+directory matching plus manual visual inspection (not filename trust
alone), consistent with the task instructions.

An initial attempt via a background agent failed with a connection error before producing any output; this index
reflects a from-scratch manual search, not a partial/unverified agent result.

## Coverage
- Filename/directory keyword matches found and reviewed: ~35 candidate files across T01-T10 (see full list in
  `02_REPOSITORY_IMAGE_SEARCH_INDEX.csv`; most were already known from the v1 package).
- Newly opened and visually inspected in this pass: 9 images (diploma, worksheet, phonics_card, event_flyer,
  product_label, 7/15 perfume baseline, plus the 5-platform `047-phonics-worksheets-kindergarten` screenshot set).
- Newly selected for the V2 package: 6 images (see below).

## Per-candidate result
- **T01 Certificates**: no new EXACT or ADJACENT competitor reference found. New CURIFY_GAP_EVIDENCE: `318_V318_diploma.png` (irrelevant fallback, extends the gap pattern to a third query). Still REFERENCE IMAGE NEEDED for competitor evidence.
- **T02 STEM**: no new images found beyond the 3 already in the v1 package. Still REFERENCE IMAGE NEEDED.
- **T03 Workbook**: **ADJACENT_REFERENCE found** — a real Canva "Phonics Worksheets Kindergarten templates" screenshot (`docs/daily_report/6.19-20/external-signal-pilot/canva-search-eval-58/screenshots/047-phonics-worksheets-kindergarten/canva-search-page1.png`), paired with Curify's own zero-result screenshot for the identical query from the same benchmark run. This upgrades T03 from "text-only competitor mention" to a real side-by-side image pair. Important caveat also found: `worksheet` (bare query) and `phonics card` both return real, relevant Curify content — the gap is specifically the workbook-COVER/booklet format and 练习册, not worksheets/practice pages in general.
- **T04 Flyer**: no new competitor image found (still text-only Canva category evidence). Important caveat found: `event flyer` (a compound query outside the original 2-query benchmark set) surfaces an actual saved "Event Flyer" template in Curify. This does not overturn the STILL_ZERO finding for the literal benchmarked queries (`flyer`, 传单), but suggests the gap may partly be a retrieval/alias issue for the generic term rather than a pure content vacuum — flagged as a pre-production caveat, not a status change.
- **T05 Price Tag**: no new EXACT/ADJACENT competitor reference found. Context found: `product label` (adjacent term) returns real Curify content (cheese/olive-oil/coffee labels), sharpening the gap definition to the price/hang-tag sub-format specifically. Still REFERENCE IMAGE NEEDED for competitor evidence.
- **T06 Chocolate Gift-Box**: no new images beyond the already-known adjacent tea-packaging set (still not copied in, subject mismatch).
- **T07 Perfume**: no new EXACT/ADJACENT competitor reference beyond the 3 already-known aromatherapy images. New CURIFY_GAP_EVIDENCE: an earlier (7/15) baseline screenshot for bare "perfume", extending the confirmed-gap timeline one timepoint earlier.
- **T08 Puzzle**: no new images found.
- **T09 Coupon**: no new images found.
- **T10 Magnet**: no new images found.

## Conclusion
Six candidates remain without any exact or adjacent competitor reference image on file (T01, T02, T05, T08, T09,
T10) even after this expanded search — this is reported honestly as REFERENCE IMAGE NEEDED rather than filled with
an unrelated placeholder. One candidate (T03) gained a genuine adjacent-reference image. No exact-match competitor
image was found for any of the 10 candidates in this pass.
