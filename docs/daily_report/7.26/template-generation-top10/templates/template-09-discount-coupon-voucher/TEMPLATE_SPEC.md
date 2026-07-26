# TEMPLATE SPEC — Discount Coupon & Promotional Voucher Templates (T09)

## Identity
- **template_id**: T09
- **template_name**: Discount Coupon & Promotional Voucher Templates
- **zh_name**: 折扣优惠券/代金券合集
- **category**: Commercial & Graphic Design
- **rank in discovery package**: #9

## Purpose & audience
- **purpose**: Tear-tab ticket-style discount coupons and vouchers for retail, restaurant, and loyalty-program promotions.
- **target_user**: Retailers, restaurants, membership/loyalty programs

## Discovery grounding
- **content_gap**: English 'discount coupon' returns 0 results at every timepoint including production, confirmed by an independent 7/17 'No results' screenshot.
- **discovery_reason**: CONFIRMED content gap (single-language basis), MEDIUM confidence, rank #9 (P2, PROVISIONAL) -- now correctly outranks T10 within P2 after the v2 ranking-rule correction; thinnest evidence-completeness (33%) of the ten candidates.
- **discovery_source**: docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/10_TOP10_TEMPLATE_RECOMMENDATIONS.csv (row rank=9, candidate_id=T09)
- **benchmark_queries**: discount coupon (EN) -- sole basis; 优惠券 (ZH) explicitly excluded from justification
- **competitor_references**: No local competitor screenshot found for 'discount coupon' specifically (NOT_FOUND).

## Format
- **aspect_ratio**: 5:2
- **output_size**: 2000x800

## Fixed structure (must not vary across examples)
- Horizontal ticket-style coupon shape with a vertical perforated/dashed tear line about 25% in from the left edge
- Left tear-tab stub section: percentage/amount-off callout in large display numerals
- Right main section: business name (top), discount description (middle), expiry date and barcode-placeholder (bottom)

## Variable content (must vary across examples)
- **editable_fields**: business_name, discount_amount, discount_type, expiry_date, terms_text, color_scheme
- **image_slots**: barcode_placeholder_graphic
- **text_slots**: business_name, discount_callout, expiry_date, terms_text

## Information hierarchy
1) discount callout (largest, on the tear-tab) 2) business name 3) expiry date 4) terms/fine print (smallest)

## Visual system
- **visual_style**: Tear-tab / ticket-style coupon layout with a percentage-off callout, barcode/QR placeholder, expiry-date field
- **typography_direction**: Extra-bold display numerals for the discount callout; clean sans-serif for business name and terms
- **color_direction**: High-contrast promotional palette (red/yellow for urgency, brand-neutral navy/white for loyalty-program vouchers)

## Prompt template
```
Design a tear-tab ticket-style DISCOUNT COUPON, {aspect_ratio} wide horizontal aspect ratio, output size {output_size}. FIXED LAYOUT (must match across every variant of this template): a horizontal ticket shape with a vertical perforated/dashed tear line about a quarter of the way in from the left edge; a left tear-tab stub section containing a large percentage/amount-off callout in bold display numerals; a right main section containing the business name at the top, a short discount description in the middle, and an expiry date plus a barcode-placeholder graphic at the bottom. VARIABLE CONTENT for this specific example: business name = "{business_name}", discount callout = "{discount_amount}", discount description = "{discount_type}", expiry date = "{expiry_date}", terms text = "{terms_text}", color scheme = {color_scheme}. Render all specified text exactly as given, legible and correctly spelled. The barcode graphic should look like a generic scannable pattern, not a real functional code. Do not add a watermark.
```

## Negative constraints
- no watermark of any kind
- no stock-photo watermark text or agency logos
- no extra/duplicate text blocks beyond the specified text_slots
- no misspelled or garbled text -- render all specified text exactly as given, legible at output resolution
- no meta-references (no 'template', 'placeholder', 'lorem ipsum', or design-tool UI chrome in the image)
- no cropped or clipped subject at the edges of the frame
- no low-contrast text over busy backgrounds -- keep all text slots on a readable, sufficiently contrasted zone
- perforated tear line must be clearly visible and vertical
- discount callout must be the single largest text element

## Quality criteria
- perforated tear line dividing stub from main section is visible
- discount callout is legible and matches the specified amount
- business name and expiry date are both present and legible

## Planned examples
- Example 01: Typical case: retail percentage-off coupon
- Example 02: Different business: restaurant fixed-amount voucher
- Example 03: Different visual content, same layout: buy-one-get-one coffee shop coupon
- Example 04: Edge case: loyalty-program punch-card style insert with denser terms text
