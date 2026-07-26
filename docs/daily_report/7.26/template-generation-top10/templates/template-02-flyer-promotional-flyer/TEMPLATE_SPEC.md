# TEMPLATE SPEC — Flyer & Promotional-Flyer Templates (T04)

## Identity
- **template_id**: T04
- **template_name**: Flyer & Promotional-Flyer Templates
- **zh_name**: 传单/促销单页合集
- **category**: Posters & Information Design
- **rank in discovery package**: #2

## Purpose & audience
- **purpose**: Compact, info-dense single-page promotional flyers (restaurant/retail/event/school-notice), distinct from Curify's existing wall-poster format.
- **target_user**: Restaurants, retail/small business owners, event organizers, schools

## Discovery grounding
- **content_gap**: '传单' and 'flyer' return 0 results at every timepoint; 'discount flyer' returns only 3 irrelevant results. Curify has poster-style content but no dedicated compact flyer layout.
- **discovery_reason**: CONFIRMED content gap, HIGH confidence, rank #2 (P0), evidence-adjusted score 85.0 -- zero/near-zero at every benchmark timepoint including an independent 7/17 screenshot baseline predating the recent search-fix cycle.
- **discovery_source**: docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/10_TOP10_TEMPLATE_RECOMMENDATIONS.csv (row rank=2, candidate_id=T04)
- **benchmark_queries**: 传单 (flyer); flyer; discount flyer (weak, partial signal)
- **competitor_references**: Text-only (not image) category evidence: CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md documents Canva's filter-chip taxonomy explicitly includes 'Flyer' as a template-type facet.

## Format
- **aspect_ratio**: 4:5
- **output_size**: 1600x2000

## Fixed structure (must not vary across examples)
- Top headline band (top ~20%): business/event name + short headline
- Hero image/graphic block (upper-middle ~35%): one dominant photo-style or illustrated visual matching the promotion
- Offer/detail text block (lower-middle ~30%): the specific offer, date/time, and 2-3 supporting detail lines
- Bottom contact/QR footer bar (~15%): address/phone/QR-code placeholder + CTA line

## Variable content (must vary across examples)
- **editable_fields**: business_name, headline, offer_details, date_time, contact_info, cta_text, hero_image_subject, color_scheme
- **image_slots**: hero_image_block, qr_code_placeholder
- **text_slots**: headline, offer_details, date_time, contact_footer, cta_text

## Information hierarchy
1) headline/offer (largest) 2) hero image (dominant visual weight) 3) date/time + details 4) contact/QR footer (smallest)

## Visual system
- **visual_style**: Compact, info-dense commercial flyer layout -- clearly distinct from a wall-poster: more text zones, smaller margins, denser information packing
- **typography_direction**: Bold condensed sans-serif headline; clean sans-serif body for offer details; small mono/sans for contact footer
- **color_direction**: High-contrast promotional palette keyed to business type (warm red/orange for food, cool blue for retail/events, navy/gold for school notices)

## Prompt template
```
Design a single-page promotional FLYER (not a wall poster), {aspect_ratio} portrait aspect ratio, output size {output_size}. FIXED LAYOUT (must match across every variant of this template): a top headline band (top ~20% of frame) with the business/event name and headline; a hero image/graphic block (upper-middle ~35%) with one dominant visual; an offer/detail text block (lower-middle ~30%) containing the offer, date/time, and 2-3 supporting detail lines; a bottom contact/QR footer bar (~15%) with a QR-code-shaped placeholder graphic, address/phone line, and a short call-to-action line. Keep the layout compact and info-dense like a real commercial flyer, NOT a sparse wall-poster. VARIABLE CONTENT for this specific example: business/event name and headline = "{headline}", hero image = {hero_image_subject}, offer details = "{offer_details}", date/time = "{date_time}", contact footer text = "{contact_info}", call-to-action text = "{cta_text}", color scheme = {color_scheme}. Render all specified text exactly as given, legible and correctly spelled. The QR-code placeholder should look like a generic scannable QR pattern graphic, not a real functional code. Do not add a watermark.
```

## Negative constraints
- no watermark of any kind
- no stock-photo watermark text or agency logos
- no extra/duplicate text blocks beyond the specified text_slots
- no misspelled or garbled text -- render all specified text exactly as given, legible at output resolution
- no meta-references (no 'template', 'placeholder', 'lorem ipsum', or design-tool UI chrome in the image)
- no cropped or clipped subject at the edges of the frame
- no low-contrast text over busy backgrounds -- keep all text slots on a readable, sufficiently contrasted zone
- must read as a compact flyer, not a sparse decorative poster
- QR placeholder must not be presented as a real scannable code

## Quality criteria
- all four fixed zones (headline / hero image / offer details / contact footer) are present and in the correct vertical order
- offer details and date/time text are legible and correctly spelled
- layout reads as flyer-dense, not poster-sparse

## Planned examples
- Example 01: Typical case: restaurant discount flyer
- Example 02: Different business: retail seasonal sale flyer
- Example 03: Different visual content, same layout: community event flyer
- Example 04: Edge case: school-notice flyer with denser text requirements
