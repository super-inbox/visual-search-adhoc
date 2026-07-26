# TEMPLATE SPEC — Chocolate & Specialty Gift-Box Packaging (T06)

## Identity
- **template_id**: T06
- **template_name**: Chocolate & Specialty Gift-Box Packaging
- **zh_name**: 巧克力/节日礼盒包装合集
- **category**: Packaging Design
- **rank in discovery package**: #7

## Purpose & audience
- **purpose**: Layered gift-box mockups (open lid, visible compartments, ribbon) for chocolate and holiday/gift merchandising, distinct from Curify's existing generic 'mystery box' style.
- **target_user**: Confectionery/gift retailers, holiday-season sellers, corporate gifting

## Discovery grounding
- **content_gap**: '巧克力礼盒' returns only generic mystery-box templates (none chocolate-specific); '礼品盒' returns 1 irrelevant hit. General chocolate product photography exists but no dedicated gift-box presentation layout.
- **discovery_reason**: PARTIAL content gap, MEDIUM confidence, rank #7 (P1, PROVISIONAL) -- textbook partial-coverage pattern: general chocolate product photography exists in the catalog, but the multi-compartment gift-box ribbon-presentation format does not.
- **discovery_source**: docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/10_TOP10_TEMPLATE_RECOMMENDATIONS.csv (row rank=7, candidate_id=T06)
- **benchmark_queries**: 巧克力礼盒 (chocolate gift box); 礼品盒 (gift box, weak/partial signal)
- **competitor_references**: Adjacent (not exact): 7.9 Pinterest tea gift-box/tin packaging product photography, re-verified in v2 as genuinely on-topic for the low-saturation gift-box packaging aesthetic.

## Format
- **aspect_ratio**: 1:1
- **output_size**: 1600x1600

## Fixed structure (must not vary across examples)
- Open gift-box mockup shown at a 3/4 angle with the lid tilted open, revealing internal compartments
- Compartmentalized interior showing individual items nestled in each compartment
- Ribbon wrapped around the closed portion of the box, tied in a bow at the front-left
- Seasonal motif badge in the top-right corner
- Brand label centered on the box front/lid exterior

## Variable content (must vary across examples)
- **editable_fields**: occasion, brand_name, ribbon_color, box_pattern, compartment_contents
- **image_slots**: open_box_mockup, seasonal_motif_badge
- **text_slots**: brand_label

## Information hierarchy
1) open box mockup with visible compartments (dominant) 2) ribbon/bow accent 3) brand label 4) seasonal motif badge (smallest)

## Visual system
- **visual_style**: Layered gift-box mockup (open lid showing compartments), ribbon and seasonal motif overlays, distinct from the existing generic 'mystery box' art style
- **typography_direction**: Elegant serif or script for the brand label on the box lid
- **color_direction**: Occasion-coded palette (holiday=red/green/gold, Valentine=pink/red/gold, corporate=navy/gold, mooncake-adjacent=burgundy/gold)

## Prompt template
```
Design an open GIFT-BOX packaging mockup, {aspect_ratio} square aspect ratio, output size {output_size}. FIXED LAYOUT (must match across every variant of this template): the gift box shown at a 3/4 angle with the lid tilted open, revealing a compartmentalized interior with individual items nestled in each compartment; a ribbon wrapped around the closed portion of the box tied in a bow at the front-left; a small seasonal motif badge in the top-right corner; a brand label centered on the box lid exterior. VARIABLE CONTENT for this specific example: occasion = {occasion}, box contents = {compartment_contents}, brand label text = "{brand_name}", ribbon color = {ribbon_color}, box pattern = {box_pattern}. Render the brand label as real, legible, correctly spelled text. Do not add a watermark.
```

## Negative constraints
- no watermark of any kind
- no stock-photo watermark text or agency logos
- no extra/duplicate text blocks beyond the specified text_slots
- no misspelled or garbled text -- render all specified text exactly as given, legible at output resolution
- no meta-references (no 'template', 'placeholder', 'lorem ipsum', or design-tool UI chrome in the image)
- no cropped or clipped subject at the edges of the frame
- no low-contrast text over busy backgrounds -- keep all text slots on a readable, sufficiently contrasted zone
- must show a genuinely open box with visible compartments, not a closed 'mystery box'
- compartment contents must match the specified occasion (e.g. chocolates, not unrelated items)

## Quality criteria
- box is shown open with visible, distinct compartments
- ribbon/bow accent is present
- brand label text is legible and correctly spelled

## Planned examples
- Example 01: Typical case: holiday chocolate gift box
- Example 02: Different occasion: Valentine's Day chocolate box
- Example 03: Different visual content, same layout: corporate holiday gift set
- Example 04: Edge case: mooncake-adjacent festival gift box
