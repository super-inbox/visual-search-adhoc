# TEMPLATE SPEC — Price Tag & Product Label Templates (T05)

## Identity
- **template_id**: T05
- **template_name**: Price Tag & Product Label Templates
- **zh_name**: 价格标签/商品吊牌合集
- **category**: Sticker & Product-Label Design
- **rank in discovery package**: #4

## Purpose & audience
- **purpose**: Small die-cut-style retail price tags and product labels for boutique, sale, and gift-shop merchandising.
- **target_user**: Small retailers, boutique/handmade sellers, e-commerce merchandisers

## Discovery grounding
- **content_gap**: '价格标签' and 'price tag' return 0 results at every timepoint, confirmed by an independent 7/17 'No results' screenshot.
- **discovery_reason**: CONFIRMED content gap, HIGH confidence, rank #4 (P1), evidence-adjusted score 62.2 -- now correctly outranks T01 (Certificates) after the v2 ranking-rule correction.
- **discovery_source**: docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/10_TOP10_TEMPLATE_RECOMMENDATIONS.csv (row rank=4, candidate_id=T05)
- **benchmark_queries**: 价格标签 (price tag); price tag
- **competitor_references**: No local competitor screenshot found for 'price tag' specifically (NOT_FOUND).

## Format
- **aspect_ratio**: 2:3
- **output_size**: 1000x1500

## Fixed structure (must not vary across examples)
- Die-cut tag silhouette (rounded rectangle or scalloped-edge shape) with a punched string hole at top-center
- Brand/shop name band directly below the hole (~top 20%)
- Large center price display (~middle 45%), price as the dominant text element
- Product/item name line directly below price (~15%)
- Bottom barcode-placeholder strip (~15%) with a generic barcode-pattern graphic

## Variable content (must vary across examples)
- **editable_fields**: brand_name, price, product_name, tag_shape_variant, seasonal_motif, color_scheme
- **image_slots**: barcode_placeholder_graphic, seasonal_motif_icon
- **text_slots**: brand_name, price, product_name

## Information hierarchy
1) price (largest, dominant) 2) brand name 3) product name 4) barcode placeholder (smallest)

## Visual system
- **visual_style**: Small die-cut-style tag layout with string/hole punch mark, clean retail-merchandising aesthetic
- **typography_direction**: Bold display numerals for price; clean sans-serif for brand and product name
- **color_direction**: Seasonal/sale color variants (standard = neutral kraft/white, sale = red, boutique = pastel, holiday = green/gold)

## Prompt template
```
Design a die-cut-style retail PRICE TAG, {aspect_ratio} portrait aspect ratio, output size {output_size}. FIXED LAYOUT (must match across every variant of this template): a die-cut tag silhouette (rounded rectangle or scalloped edge) with a small punched string hole at the top-center; a brand/shop name band directly below the hole; a large center price display as the dominant text element; a product/item name line directly below the price; a bottom strip with a generic barcode-pattern graphic. VARIABLE CONTENT for this specific example: brand/shop name = "{brand_name}", price = "{price}", product/item name = "{product_name}", tag shape = {tag_shape_variant}, seasonal motif = {seasonal_motif}, color scheme = {color_scheme}. Render the brand name, price, and product name as real, legible, correctly spelled text exactly as given. The barcode graphic should look like a generic scannable barcode pattern, not a real functional code. Do not add a watermark.
```

## Negative constraints
- no watermark of any kind
- no stock-photo watermark text or agency logos
- no extra/duplicate text blocks beyond the specified text_slots
- no misspelled or garbled text -- render all specified text exactly as given, legible at output resolution
- no meta-references (no 'template', 'placeholder', 'lorem ipsum', or design-tool UI chrome in the image)
- no cropped or clipped subject at the edges of the frame
- no low-contrast text over busy backgrounds -- keep all text slots on a readable, sufficiently contrasted zone
- barcode graphic must be a generic decorative pattern, not a real functional barcode
- price text must be the single largest text element on the tag

## Quality criteria
- die-cut tag silhouette with a visible string hole is present
- price is the visually dominant text element and is legible
- brand name and product name are both present and correctly spelled

## Planned examples
- Example 01: Typical case: standard boutique clothing price tag
- Example 02: Different business: handmade candle shop sale tag
- Example 03: Different visual content, same layout: gift-shop souvenir hang tag
- Example 04: Edge case: holiday seasonal gift tag with longer product name
