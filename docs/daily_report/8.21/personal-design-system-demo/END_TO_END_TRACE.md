# End-to-End Trace

Eight concrete chains: **portfolio observation → Personal Design System rule → new brand decision
→ asset manifestation.** Each one names the actual work ID, rule, decision, and asset file involved
— no step is asserted without pointing at the document/file that carries it.

---

## 1. Super-symbol

- **Portfolio observation**: work_05's circular "©CA" logomark repeats identically across three
  differently-colored SKU boxes; work_06's floral roundel repeats across ≥2 tags in one gift set;
  work_09's circular mark + mascot ties together four package formats.
  (`PORTFOLIO_EVIDENCE.jsonl`, `symbol_or_motif_observation` fields for work_05/06/09)
- **Personal Design System rule**: Rule 2 — "design one fixed, simplified graphic mark per brand
  and reuse it verbatim across every SKU/format." HIGH confidence, 4 supporting works
  (work_01/05/06/09). (`PERSONAL_DESIGN_SYSTEM.md` §9)
- **New brand decision**: an original bubble-plus-sprout mark, inside a circle (the circle borrowed
  as a *container convention* from the same 4 works, per §6's recurring-geometry note — the shape
  inside it is new). (`BRAND_VISUAL_SYSTEM.md` §Super-Symbol; `BRAND_SYSTEM_TRACEABILITY.md` row 3)
- **Asset manifestation**: `SproutBubbleSymbol.dc.html`, imported identically into all 5 assets —
  visible at full scale in `HERO_KEY_VISUAL.png`, at three-times-repeated scale in
  `SKU_FAMILY_SHOT.png`, enlarged as a background device in `CAMPAIGN_POSTER.png`.

---

## 2. Dominant hue + small accent

- **Portfolio observation**: gold/maroon+red (work_01), mint+coral/blue (work_02), black/grey+blue
  (work_03), burgundy+gold (work_06), periwinkle+pink/green (work_07) — one dominant field, one
  small saturated accent, in 5 independent works.
  (`PORTFOLIO_EVIDENCE.jsonl`, `observed_color_behavior` fields)
- **Personal Design System rule**: Rule 1 — "one dominant hue family, then exactly one small
  saturated accent, never a flat multicolor palette." HIGH, 5 works. (`PERSONAL_DESIGN_SYSTEM.md` §9)
- **New brand decision**: each SKU gets one new dominant hue (blush-coral / mid-green / pale-gold)
  plus one shared "spark-white" accent held constant across the whole line — no exact hex claimed.
  (`BRAND_VISUAL_SYSTEM.md` §Color Behavior)
- **Asset manifestation**: `Can.dc.html`'s `dominant` prop, passed as three different values across
  `SKU_FAMILY_SHOT.png` and `WEBSITE_HERO.png`; the accent (spark-white symbol fill) stays fixed in
  every asset — verifiable directly in `canvas_src/Can.dc.html`'s `data-props`.

---

## 3. Bilingual Chinese/Latin hierarchy

- **Portfolio observation**: large Chinese "摘要" + small Latin "ZHAI YAO" (work_01); oversized
  "artevive" + smaller Chinese "文创芝" (work_03) — large-native-leads pattern in 2 of the 4 works
  supporting this rule; work_09 shows a closer-to-parity alternative.
  (`PORTFOLIO_EVIDENCE.jsonl`, `typography_observation` fields for work_01/03/09)
- **Personal Design System rule**: Rule 3 — "pair Chinese and Latin systematically; hierarchy
  decided per brief, not fixed." HIGH, 4 works (work_01/03/04/09). (`PERSONAL_DESIGN_SYSTEM.md` §9)
- **New brand decision**: deliberately chose the large-Chinese/small-Latin branch (work_01/03's
  pattern) over the near-parity branch (work_09's), reasoned in `BRAND_VISUAL_SYSTEM.md`
  §Typography Direction as the better fit for this brand's China-market-first identity.
- **Asset manifestation**: `Can.dc.html`'s `.cn` (large, weight 900) vs. `.en` (small, letter-spaced
  caps) CSS classes — visible identically on every can in all 5 PNGs.

---

## 4. SKU family consistency

- **Portfolio observation**: work_05 shows one fixed graphic mark reused across 3 SKU colors within
  one product line; work_09 shows one color system spanning 4 physical formats of one line.
  (`PORTFOLIO_EVIDENCE.jsonl`, work_05/work_09 `recurring_trait_candidates`)
- **Personal Design System rule**: Rule 7 — "present multi-SKU lines as one ensemble/family
  composition." HIGH, 3 works (work_05/06/09). (`PERSONAL_DESIGN_SYSTEM.md` §9)
- **New brand decision**: 3 SKUs (Lychee Rose / Cucumber Mint / Yuzu Ginger) defined as one family
  table in `BRAND_VISUAL_SYSTEM.md` §SKU/Family System — mark, accent, hierarchy, and can silhouette
  held constant; only dominant hue and one small flavor icon vary.
- **Asset manifestation**: `SkuFamily.dc.html` imports `Can.dc.html` three times with only
  `dominant`/`flavorCN`/`flavorEN`/`flavorIcon` props changed — `SKU_FAMILY_SHOT.png` and
  `WEBSITE_HERO.png` both show the same 3-color family, verified pixel-consistent in
  `ASSET_MANIFEST.csv`'s notes column for both assets.

---

## 5. CGI/product-render staging default

- **Portfolio observation**: 7 of 10 sampled works (work_01/03/04/05/06/07/09) are staged CGI
  renders with deliberate studio lighting; work_02 and work_08 are the only real-photography
  exceptions. (`PORTFOLIO_EVIDENCE.jsonl`, `imagery_style` fields across all 10 records)
- **Personal Design System rule**: Rule 5 — "default to a photoreal CGI-rendered mockup; real
  photography is a valid but occasional secondary mode." HIGH, 7 works.
  (`PERSONAL_DESIGN_SYSTEM.md` §9)
- **New brand decision**: `BRAND_VISUAL_SYSTEM.md` §Imagery/Rendering assigns 4 of 5 planned assets
  to the CGI-render default and reserves exactly 1 (`SOCIAL_POST`) for the photography-exception
  role.
- **Asset manifestation**: `HERO_KEY_VISUAL.png`, `SKU_FAMILY_SHOT.png`, `CAMPAIGN_POSTER.png`,
  `WEBSITE_HERO.png` are all clean product-only stagings; `SOCIAL_POST.png` alone shows a staged
  scene (desk, laptop, plant) — the compositional split is preserved even though (per `H. Visual
  Fidelity` in `EVALUATION.md`) neither branch achieved true photoreal/photographic medium in this
  session.

---

## 6. Category-conditioned staging (light vs. dark backdrop)

- **Portfolio observation**: dark/black/maroon backdrops for work_01/03/05/06 (heritage, symbol,
  hairbrush-brand, festival-gift); light/pastel backdrops for work_02/04/08/10 (sunscreen, apparel,
  maternal-health, children's). An even 4-vs-4 split aligned to category register.
  (`PORTFOLIO_EVIDENCE.jsonl`, `composition_observation` fields)
- **Personal Design System rule**: Rule 6 — a two-branch conditional: dark for heritage/premium,
  light for soft-goods/wellness/children's. HIGH, 8 works total.
  (`PERSONAL_DESIGN_SYSTEM.md` §9)
- **New brand decision**: `BRAND_VISUAL_SYSTEM.md` §Imagery/Rendering explicitly places 荔泉气泡 in
  the light-backdrop branch (a wellness/refreshment beverage), *not* the dark/heritage branch — the
  single most important anti-drift decision in the whole brief, called out again in
  `BRAND_SYSTEM_CONSISTENCY_CHECK.md` §5.
- **Asset manifestation**: every one of the 5 PNGs uses a bright, near-white-to-pale background —
  none uses a dark/maroon ground, confirmed in `CROSS_ASSET_CHECK.md` §4.

---

## 7. Shared Can component / condensation consistency

- **Portfolio observation**: not a direct portfolio observation — this trace step is about
  *execution mechanism*, not source content. It exists because `BRAND_VISUAL_SYSTEM.md`
  §Imagery/Rendering (itself grounded in Rule 5) calls for "visible condensation droplets… without
  needing additional props" on product-render shots.
- **Personal Design System rule**: Rule 5's staging convention (condensation is the concrete
  execution of "reinforcing cold, sparkling, refreshing").
- **New brand decision**: rather than authoring condensation per-asset, it was built once into the
  shared `Can.dc.html` component (`generated_assets/canvas_src/Can.dc.html`, `.condensation` layer,
  6 droplet spans) — a 2026-08-21 fix after the first generation round left it on only 1 of 5
  assets. (`ASSET_GENERATION_NOTES.md` fix note; `CROSS_ASSET_CHECK.md` §4)
- **Asset manifestation**: identical subtle droplets now visible on every can in all 5 PNGs —
  `HERO_KEY_VISUAL.png`, all 3 cans in `SKU_FAMILY_SHOT.png`, `SOCIAL_POST.png`,
  `CAMPAIGN_POSTER.png`, all 3 cans in `WEBSITE_HERO.png` — structurally guaranteed rather than
  visually re-checked per asset.

---

## 8. Ensemble/family composition (multi-piece staging)

- **Portfolio observation**: work_05 stages a hero comb in front of its SKU-color lineup; work_06
  stages a full multi-piece gift-set flat-lay (box + envelope + card + ribbon); work_09 stages 4
  package formats side by side. (`PORTFOLIO_EVIDENCE.jsonl`, `composition_observation` fields)
- **Personal Design System rule**: Rule 7 (same rule as trace #4, applied here to *composition*
  rather than *color logic*) — ensemble shots for multi-SKU/multi-piece lines.
- **New brand decision**: `ASSET_PLAN.md` Asset 2 and Asset 5 both specify an ensemble arrangement
  (evenly spaced row, same camera height/angle for every can, no single SKU staged as more "hero"
  than the others) rather than 3 isolated single-item shots.
- **Asset manifestation**: `SKU_FAMILY_SHOT.png` shows all 3 cans in one evenly-lit row;
  `WEBSITE_HERO.png` repeats the same 3-can arrangement beside the copy/CTA column — both verified
  against the "ensemble, not isolated" requirement in `CROSS_ASSET_CHECK.md` §4.
