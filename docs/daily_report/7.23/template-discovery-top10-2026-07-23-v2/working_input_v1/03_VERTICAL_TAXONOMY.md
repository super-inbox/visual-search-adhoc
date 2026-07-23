# Vertical Taxonomy — Template Discovery

This taxonomy groups the 10 Top-10 template candidates (and the queries feeding them) into primary verticals,
derived from the `category_or_vertical` field of `02_UNIFIED_QUERY_INVENTORY.csv` and cross-checked against the
Task A `10_VERTICAL_SUMMARY.csv` per-category pass-rate table (which uses a related but coarser category naming
scheme -- e.g. Task A's `certificate`, `classroom_material`, `flyer`, `label`, `package`, `bottle`, `collectible`,
`coupon`, `merch_item` roughly correspond to the verticals below).

## Verticals represented in the Top-10 pool

### Education & Classroom Materials
- Candidates: T03, T02

### Posters & Information Design
- Candidates: T04

### Certificates & Academic Documents
- Candidates: T01

### Sticker & Product-Label Design
- Candidates: T05

### Packaging Design
- Candidates: T07, T06

### Commercial & Graphic Design
- Candidates: T09

### Toy, Plush, Character & Collectible Design
- Candidates: T08

### Product & Merchandise Design
- Candidates: T10

## Notes on Task A vertical alignment (10_VERTICAL_SUMMARY.csv)
- `certificate` (Task A vertical): 8 queries, 0% PASS rate, 3 zero-result queries -- directly supports T01.
- `classroom_material` (Task A vertical): 10 queries, 0% PASS rate, 2 zero-result -- directly supports T02.
- `flyer` (Task A vertical): 10 queries, 10% PASS rate, 2 zero-result -- directly supports T04.
- `label` (Task A vertical): 16 queries, 12.5% PASS rate, 2 zero-result -- weak overall, supports T05 (price tag)
  narrowly; broader label category also includes unrelated wine-label content that already performs adequately.
- `package` / `product_box` (Task A vertical): supports T06 (chocolate gift box) and T07 (perfume/cosmetic bottle
  packaging) -- these Task A verticals actually show some improvements vs production, consistent with T06/T07
  being PARTIAL rather than CONFIRMED gaps (general packaging exists; specific sub-types do not).
- `collectible` (Task A vertical): 20 queries, 5% PASS rate -- supports T08 (puzzle/jigsaw).
- `coupon` (Task A vertical): 2 queries, 0% PASS rate, both zero-result -- supports T09, but only 1 of the 2
  underlying queries (`discount coupon`, EN) is used as primary evidence; the ZH sibling (`优惠券`) is excluded as
  a search regression.
- `merch_item` (Task A vertical): 30 queries, 10% PASS rate -- supports T10 (fridge magnet), the narrowest and
  weakest-evidence candidate in the pool.
- `map` (Task A vertical, 4 queries, 0% PASS, 2 zero-result) and `flashcard` (Task A vertical, 12 queries, 8.3%
  PASS, 2 zero-result) are **excluded** from the Top-10 pool entirely -- see `07_SEARCH_VS_CONTENT_GAP_CLASSIFICATION.csv`
  and Section 18 discussion in the Chinese report for why these are search regressions, not content gaps.
