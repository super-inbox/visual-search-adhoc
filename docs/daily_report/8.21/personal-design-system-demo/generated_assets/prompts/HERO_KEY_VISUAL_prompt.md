# HERO_KEY_VISUAL — generation record

## Method actually used
Rendered as a `.dc.html` Design Component (Claude Design canvas skill), not a photoreal
text-to-image model — no such tool was available in this session (see
`ASSET_GENERATION_NOTES.md` for the full capability accounting). Source:
`canvas_src/Main.dc.html`, importing the shared `Can.dc.html` (Lychee Rose props) and
`SproutBubbleSymbol.dc.html` components.

## Photoreal generation prompt (for future use with an actual image-gen tool)

Exact ingredients as specified in `ASSET_PLAN.md` §Asset 1, preserved verbatim so this can be
handed to a real photoreal renderer later without re-deriving the spec:

> 330ml matte aluminum can, soft blush/coral dominant field, white-gold bubble-sprout mark in a
> thin circle outline centered upper-third of can face, condensation droplets, bright near-white
> studio background, soft single-source cool lighting, photoreal CGI product render, three-quarter
> hero angle, generous negative space.

Additional constraints carried from `BRAND_VISUAL_SYSTEM.md`: Chinese "荔泉气泡" leads, English
"LICHUAN SPARKLING" smaller beneath it, flavor name "荔枝玫瑰 · Lychee Rose" smallest tier; no
second dominant color; no heritage/ornamental cues (no dragon motif, no calligraphic type, no dark
maroon staging).

## What was actually generated instead

A flat/vector CSS+SVG rendering of the same can: rounded-rectangle can silhouette with metallic
rim gradients, a horizontal dominant-hue gradient body (blush/coral), a gloss highlight strip, the
Sprout-Bubble symbol (circle + teardrop + two sprout tendrils) centered upper-third, Chinese
wordmark large/bold, English wordmark small/letter-spaced beneath, flavor pill beneath that.
Staged on a near-white radial-gradient background with hand-placed condensation-droplet dots and a
soft ground-shadow ellipse. This is a graphic-design mockup, not a photoreal render — it correctly
carries the system's color/symbol/type logic but not photographic material realism (can specularity,
true condensation physics, camera depth of field).
