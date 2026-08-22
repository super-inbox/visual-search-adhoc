# SKU_FAMILY_SHOT — generation record

## Method actually used
`.dc.html` Design Component. Source: `canvas_src/SkuFamily.dc.html`, importing `Can.dc.html` three
times (Lychee Rose / Cucumber Mint / Yuzu Ginger props) plus one `SproutBubbleSymbol.dc.html`
instance for the small corner brand mark.

## Photoreal generation prompt (for future use with an actual image-gen tool)

From `ASSET_PLAN.md` §Asset 2:

> three 330ml cans side by side (blush/coral, mid-green, pale gold), identical white-gold
> bubble-sprout circular mark at identical scale/position on each, identical typographic stack on
> each, bright even studio lighting, near-white background, photoreal CGI render, condensation on
> all three, evenly spaced flat composition.

Consistency requirement carried from `BRAND_VISUAL_SYSTEM.md`/`ASSET_PLAN.md`: identical can
silhouette, identical symbol scale/position/fill across all three; only the dominant background hue
and one small quaternary flavor icon differ.

## What was actually generated instead

Three flat/vector can renders (via the shared `Can.dc.html` component, so their markup — and
therefore their symbol geometry, type layout, and rim/gloss treatment — is byte-identical across
all three, differing only in the `dominant` color prop and the flavor name/icon prop), arranged in
an evenly-spaced row on a shared light background, with a small brand mark (symbol + wordmark) at
top-left. No condensation droplets were added to this asset (present on Asset 1 and 3 instead) —
noted as a minor omission in `ASSET_GENERATION_NOTES.md`.
