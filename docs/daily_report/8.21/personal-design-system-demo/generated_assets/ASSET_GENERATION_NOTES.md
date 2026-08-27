# Asset Generation Notes

## 2026-08-21 fix: condensation consistency

The first generation round left condensation droplets on only 1 of 5 assets (HERO_KEY_VISUAL —
`SOCIAL_POST` was incorrectly believed to have them too; re-checked against source and it did not).
This has been fixed by **moving condensation into the shared `Can.dc.html` component** rather than
authoring it per-artboard: a small `.condensation` layer with 6 subtle droplet spans is now part of
the can's own markup, positioned on the can body itself (not floating in the surrounding scene).
Because every asset imports this same component via `<dc-import name="Can" ...>`, condensation now
appears identically, automatically, on every can in every asset — HERO_KEY_VISUAL, all 3 cans in
SKU_FAMILY_SHOT, the can in SOCIAL_POST, the can in CAMPAIGN_POSTER, and all 3 cans in WEBSITE_HERO
— with no per-asset authoring required. The old ad hoc scene-level droplets in `Main.dc.html` were
removed since they're now redundant (and were arguably wrong anyway — condensation belongs on the
can surface, not floating as ambient dust in the background). This is the "apply consistently to
all product-render assets" option, chosen because condensation directly reinforces this brand's
core attribute (cold/sparkling/refreshing per `BRAND_VISUAL_SYSTEM.md` §Imagery/Rendering) without
adding a new color, a new element type, or any visual clutter — it's a single subtle detail applied
uniformly, which best fits a system whose whole discipline is "one fixed device, reused everywhere"
(Rule 2's logic, extended here to a staging detail rather than the symbol itself). All 5 PNGs were
regenerated from the same republished canvas and are up to date as of this fix. (Canvas.json was
also reordered — WebsiteHero moved to x=0 — purely so its full frame could be captured without
clipping; this changed no visual content, only the artboards' spatial arrangement on the canvas.)

## Capability accounting (read this first)

This session has no photoreal text-to-image or photography-generation tool — no Curify image-gen
API, no diffusion model, no camera-photography capability. The only genuine visual-rendering
capability available was the `design` skill (Claude Design's canvas editor, published as an
Artifact), which renders `.dc.html` components via real HTML/CSS/SVG in a browser — a legitimate
generation path, just a **flat/vector graphic-design medium**, not photoreal CGI product
photography or real lifestyle photography.

Per instruction ("prefer real generation if available; if an image cannot be generated, do not
fake it — create the exact prompt/spec and mark status as blocked"), the approach taken was:
generate real, on-system visuals using the one available rendering path, while explicitly marking
the *photoreal/photography* quality bar specifically as blocked, and preserving the exact prompts
that requirement would need for a future photoreal/photography-capable tool (saved under
`prompts/`). Nothing below is a faked or invented image — every PNG in `generated_assets/` is a
real browser screenshot of a real, published, rendered `.dc.html` canvas
(`https://claude.ai/code/artifact/93d72ad9-c85c-4c45-ada7-875c8a3a1a4a`).

**Mechanical consistency, not eyeballed:** all 5 assets import two shared components —
`canvas_src/SproutBubbleSymbol.dc.html` (the symbol) and `canvas_src/Can.dc.html` (a parameterized
can, props: dominant color, flavor name CN/EN, flavor icon) — via `<dc-import>`. This means the
symbol's geometry and every can's structure/typography are **byte-identical markup** everywhere
they appear, differing only in the color/text props explicitly passed in. Cross-asset consistency
in `CROSS_ASSET_CHECK.md` is therefore a structural fact, not a subjective visual read.

---

## HERO_KEY_VISUAL

- **Intent**: establish the super-symbol, typographic hierarchy, and staging register in one
  clean shot (`ASSET_PLAN.md` Asset 1).
- **Applied rules**: Rule 1 (blush-coral dominant + spark-white accent), Rule 2 (symbol centered,
  upper-third, large), Rule 3 (Chinese leads, English small beneath), Rule 5 (CGI-render
  convention — realized here as a clean flat-render, see capability note above), Rule 6 (light/
  bright backdrop branch, not the heritage dark branch).
- **Generated correctly**: symbol placement and scale, bilingual type hierarchy, single dominant
  hue + single accent (no second dominant color introduced), condensation-droplet staging, generous
  whitespace, soft ground shadow.
- **Deviations**: rendered as a flat/vector can illustration, not a photoreal CGI render — the
  single largest deviation from the literal brief for this asset, driven entirely by tool
  availability, not a design choice.
- **Consistency issues**: none found — this asset is the canonical reference the other 4 were
  checked against.

## SKU_FAMILY_SHOT

- **Intent**: prove the family/ensemble mechanism — one brand, three flavors (`ASSET_PLAN.md`
  Asset 2).
- **Applied rules**: Rule 1 (per-SKU dominant hue, shared accent), Rule 2 (identical mark across
  all three), Rule 7 (ensemble composition, no can staged as more "hero" than the others).
- **Generated correctly**: all three cans use the identical shared component (verified by shared
  source, not visual inspection alone); only `dominant`, `flavorCN`, `flavorEN`, `flavorIcon` props
  differ; small brand mark placed once at top-left rather than repeated per can, matching
  `ASSET_PLAN.md`'s explicit instruction.
- **Deviations**: none remaining — condensation is now present via the shared `Can` component fix
  (see the 2026-08-21 fix note above).
- **Consistency issues**: none — symbol/type/hue-logic and condensation are all fully consistent.

## SOCIAL_POST

- **Intent**: the one deliberate "photography/lifestyle exception" touchpoint (`ASSET_PLAN.md`
  Asset 3, Rule 5's secondary mode).
- **Applied rules**: Rule 5 (secondary mode — see deviation below), Rule 2 (symbol reused as a
  small corner mark rather than redrawn), Rule 1/3 (color and type carried through unchanged).
- **Generated correctly**: the can shown is the same shared component (Lychee Rose props), the
  symbol corner-mark is the same shared component at small scale, the campaign headline matches
  `BRAND_BRIEF.md`'s core message exactly.
- **Deviations — the most significant in this asset plan**: the brief specifically calls for real
  lifestyle photography as the deliberate departure from the brand's CGI-render default. No
  photography-generation capability exists in this session, so an **illustrated flat-design desk
  scene** (laptop silhouette, potted-sprout illustration, kraft desk surface) was substituted. This
  preserves the asset's *structural role* (the one non-product-render touchpoint) but not its
  *literal medium* (photography). This is the single clearest instance in this phase of "cannot
  fully satisfy the brief with available tools" — recorded here rather than glossed over.
- **Consistency issues**: none beyond the medium substitution itself.

## CAMPAIGN_POSTER

- **Intent**: graphic-led, symbol-forward brand poster (`ASSET_PLAN.md` Asset 4).
- **Applied rules**: Rule 2 (the enlarged background device is the *same* `<dc-import>` component
  as the on-can mark, just scaled up and set to low opacity — not a redesigned or reinterpreted
  version, per the rule's requirement that the mark never be redrawn per touchpoint), Rule 5
  (can rendering kept consistent with the other assets), Rule 6 (light backdrop retained).
- **Generated correctly**: background symbol shape is verified identical to the on-can version
  (same component); bold Chinese headline with smaller English subhead; generous whitespace;
  single strong dominant hue (blush-coral, matching the featured Lychee Rose SKU).
- **Deviations**: none remaining — condensation is now present on the featured can via the shared
  `Can` component fix (see the 2026-08-21 fix note above).
- **Consistency issues**: none — fully consistent with the system.

## WEBSITE_HERO

- **Intent**: wide-format commercial touchpoint — family or hero SKU, concise bilingual copy, CTA
  (`ASSET_PLAN.md` Asset 5).
- **Applied rules**: Rule 7 (ensemble composition), Rule 1/2 (per-can consistency, unchanged from
  SKU_FAMILY_SHOT — verified via shared component), Rule 6 (light backdrop retained even in this
  more commercial/CTA-driven context, per the instruction not to introduce dark/dramatic staging
  for this touchpoint).
- **Generated correctly**: brand mark + bilingual headline + CTA pill on the left; all three SKU
  cans (identical shared component, reduced scale) on the right; consistent light background.
- **Deviations**: `ASSET_PLAN.md` named a shelf/retail-display fixture as one option for this
  asset; that was simplified to a clean web-banner layout (no illustrated fixture/shelf geometry),
  since building a convincing fixture illustration was judged lower-value than a clean, usable web
  banner given the medium constraint already in effect across all 5 assets.
- **Consistency issues**: none found — cans are pixel-consistent with SKU_FAMILY_SHOT (same
  component, same props, smaller `hint-size` only).

## Cross-cutting deviations, summarized

1. **Medium**: all 5 assets are flat/vector `.dc.html` renders, not photoreal CGI or real
   photography — a capability gap, not a design decision, disclosed on every relevant file.
2. **Condensation droplets**: now consistent across all 5 assets, fixed 2026-08-21 by moving the
   droplet treatment into the shared `Can.dc.html` component (see the fix note at the top of this
   file). No longer an open issue.
3. **WEBSITE_HERO's fixture simplification** — scope reduction, not a rule violation.

None of the above are copied from, or fabricate facts about, the source portfolio — every
deviation is a *medium/capability* limitation disclosed against this session's own generation
constraints, not a claim about `PORTFOLIO_EVIDENCE.jsonl`.
