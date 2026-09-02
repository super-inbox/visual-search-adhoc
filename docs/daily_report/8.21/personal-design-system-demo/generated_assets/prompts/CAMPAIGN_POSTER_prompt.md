# CAMPAIGN_POSTER — generation record

## Method actually used
`.dc.html` Design Component. Source: `canvas_src/Poster.dc.html`, importing one large-scale
`SproutBubbleSymbol.dc.html` instance (background device, ~78% of frame width at 16% opacity) and
one `Can.dc.html` instance (Lychee Rose props, foreground, normal scale).

## Photoreal generation prompt (for future use with an actual image-gen tool)

From `ASSET_PLAN.md` §Asset 4:

> large soft white-gold bubble-sprout silhouette as a background graphic on a bright pale ground,
> one 330ml can (any SKU) placed in front at moderate scale with condensation, bold but clean
> Chinese headline typography, small English subhead, generous whitespace around the composition,
> poster/out-of-home aspect ratio.

## What was actually generated instead

A portrait-format poster: the Sprout-Bubble symbol enlarged as a faint background watermark
(same exact shape as the on-can mark, per Rule 2 — reused via `<dc-import>`, not redrawn), the
Lychee Rose can in front at moderate scale, a bold Chinese headline ("轻盈气泡 / 源头养分") with a
small English subhead ("LICHUAN SPARKLING"), and a small footer line naming all three flavors
("荔枝玫瑰 · 黄瓜薄荷 · 柚子姜片 — 即刻开启"). Generous whitespace throughout. No condensation
droplets were added to the can in this specific asset (present in Asset 1 and 3) — noted as a
minor omission in `ASSET_GENERATION_NOTES.md`.
