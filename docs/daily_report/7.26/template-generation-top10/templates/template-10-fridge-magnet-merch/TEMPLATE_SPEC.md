# TEMPLATE SPEC — Fridge Magnet & Small Merch-Item Templates (T10)

## Identity
- **template_id**: T10
- **template_name**: Fridge Magnet & Small Merch-Item Templates
- **zh_name**: 冰箱贴/小型周边商品合集
- **category**: Product & Merchandise Design
- **rank in discovery package**: #10

## Purpose & audience
- **purpose**: Small die-cut fridge-magnet product mockups beyond Curify's existing single travel-landmark theme.
- **target_user**: Souvenir/gift shops, small brands doing promotional merch, print-on-demand sellers

## Discovery grounding
- **content_gap**: 'magnet' returns only 3 results, all the same single travel-landmark theme (Nanjing/Yangzhou landmark magnets) -- confirms magnet content exists but only in one narrow theme, not as a general-purpose product line.
- **discovery_reason**: PARTIAL content gap, LOW-MEDIUM confidence, rank #10 (P2, PROVISIONAL) -- lowest-priority candidate in the pool; general adjacent content exists, ruling out total search failure, but the requested general-purpose sub-type is absent.
- **discovery_source**: docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/10_TOP10_TEMPLATE_RECOMMENDATIONS.csv (row rank=10, candidate_id=T10)
- **benchmark_queries**: magnet
- **competitor_references**: No local competitor screenshot found for 'magnet' specifically (NOT_FOUND).

## Format
- **aspect_ratio**: 1:1
- **output_size**: 1200x1200

## Fixed structure (must not vary across examples)
- Small die-cut magnet shape (rounded rectangle or circle) centered in the frame, shown as a product mockup with a subtle drop shadow
- Photo/logo/illustration area filling the magnet face (~80% of the die-cut shape)
- Small brand wordmark band along the bottom edge of the magnet face (~15% of the shape height), understated

## Variable content (must vary across examples)
- **editable_fields**: theme, shape_variant, palette, face_subject, brand_wordmark
- **image_slots**: magnet_face_illustration
- **text_slots**: brand_wordmark

## Information hierarchy
1) magnet face illustration (dominant) 2) brand wordmark (smallest, bottom edge)

## Visual system
- **visual_style**: Small die-cut magnet mockup, photo/logo placeholder area, seasonal and quote-based variants beyond the existing travel-landmark style
- **typography_direction**: Compact, friendly sans-serif for the bottom brand wordmark; playful hand-lettered style if the face subject is a quote
- **color_direction**: Theme-coded palette (photo magnet=neutral frame, brand magnet=brand colors, holiday=red/green/gold, quote=pastel)

## Prompt template
```
Design a small die-cut FRIDGE MAGNET product mockup, {aspect_ratio} square aspect ratio, output size {output_size}, shown against a plain neutral background with a subtle drop shadow beneath the magnet. FIXED LAYOUT (must match across every variant of this template): one centered die-cut magnet shape ({shape_variant}) filling most of the frame; a photo/logo/illustration area filling about 80% of the magnet face; a small, understated brand wordmark band along the bottom edge of the magnet face. VARIABLE CONTENT for this specific example: theme = {theme}, magnet face illustration = {face_subject}, brand wordmark text = "{brand_wordmark}", palette = {palette}. Render the brand wordmark as real, legible, correctly spelled text. Do not add a watermark. Do not crop the magnet shape at the frame edges.
```

## Negative constraints
- no watermark of any kind
- no stock-photo watermark text or agency logos
- no extra/duplicate text blocks beyond the specified text_slots
- no misspelled or garbled text -- render all specified text exactly as given, legible at output resolution
- no meta-references (no 'template', 'placeholder', 'lorem ipsum', or design-tool UI chrome in the image)
- no cropped or clipped subject at the edges of the frame
- no low-contrast text over busy backgrounds -- keep all text slots on a readable, sufficiently contrasted zone
- must be shown as a single product mockup (not a sheet/grid of many magnets)
- magnet die-cut shape must not be cropped at the frame edges

## Quality criteria
- a single, clearly die-cut magnet shape is shown as a product mockup with a drop shadow
- face illustration matches the specified theme
- brand wordmark is legible and correctly spelled

## Planned examples
- Example 01: Typical case: custom photo fridge magnet
- Example 02: Different theme: brand/promotional magnet
- Example 03: Different visual content, same layout: holiday seasonal magnet
- Example 04: Edge case: quote/decorative magnet with longer text on the face
