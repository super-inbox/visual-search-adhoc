# Cross-Asset Check

Compares all 5 generated assets against each other and against `BRAND_VISUAL_SYSTEM.md` /
`ASSET_PLAN.md`. Where a check can be verified structurally (from shared source, not just visual
inspection) that is called out explicitly.

**Update, 2026-08-21**: this document originally flagged one inconsistency — condensation droplets
present on 1 of 5 assets, absent on the other 4 (and incorrectly noted as present on a 2nd asset
that, on re-check of source, never actually had them). That has been fixed: condensation is now
authored once, inside the shared `Can.dc.html` component, so it appears identically on every can in
every asset with no per-asset authoring. §4 below reflects the corrected, now-consistent state; the
prior finding is kept visible (struck through in spirit, not deleted) so the fix is auditable rather
than silently smoothed over.

## 1. Super-symbol consistency

**Structurally verified, not just visually similar**: HERO_KEY_VISUAL, SKU_FAMILY_SHOT (x3),
SOCIAL_POST, CAMPAIGN_POSTER (enlarged), and WEBSITE_HERO all `<dc-import>` the same
`SproutBubbleSymbol.dc.html` file — the circle + teardrop-bubble + two sprout tendrils, same SVG
path data, same stroke color, in every instance. CAMPAIGN_POSTER's background version is the
identical component scaled up and set to 16% opacity, not a redrawn or reinterpreted symbol.

**Result: PASS — full consistency**, and verifiable from source rather than eyeballed.

## 2. Typography hierarchy consistency

Every asset that shows a can face (all 5) carries the same three-tier stack from the shared `Can`
component: large Chinese "荔泉气泡" → small-caps English "LICHUAN SPARKLING" → smallest
flavor-name pill. HERO_KEY_VISUAL, SOCIAL_POST, CAMPAIGN_POSTER, and WEBSITE_HERO additionally
repeat the same large-Chinese/small-English relationship in their standalone headlines ("轻盈气泡
/ 源头养分" over "LICHUAN SPARKLING" / "LIGHT BUBBLES. REAL NOURISHMENT."). SKU_FAMILY_SHOT's
corner brand mark follows the same relationship at reduced scale.

**Result: PASS — consistent across all 5.**

## 3. SKU color logic

Lychee Rose = blush/coral, Cucumber Mint = mid-green, Yuzu Ginger = pale gold, in every asset that
shows more than one SKU (SKU_FAMILY_SHOT, WEBSITE_HERO) — same three `dominant` prop values passed
to the same shared component in both files (verified from source). Single-SKU assets
(HERO_KEY_VISUAL, SOCIAL_POST, CAMPAIGN_POSTER) all use Lychee Rose consistently, matching
`BRAND_BRIEF.md`'s designation of it as the primary SKU.

**Result: PASS — no color drift between assets.**

## 4. Composition family resemblance

All 5 sit on the same light, bright, near-white-to-pale-warm background family (no asset uses a
dark/heritage backdrop), consistent with Rule 6's light branch being the correct choice for this
brand's category. Whitespace is generous across HERO_KEY_VISUAL, CAMPAIGN_POSTER, and WEBSITE_HERO;
SKU_FAMILY_SHOT and SOCIAL_POST are slightly denser (props/scene elements), which is appropriate to
their respective purposes (family lineup; lifestyle scene) rather than a departure from the
system.

**Result: PASS — fully consistent.** Condensation droplets now appear on every can in all 5 assets
(HERO_KEY_VISUAL, all 3 cans in SKU_FAMILY_SHOT, SOCIAL_POST, CAMPAIGN_POSTER, all 3 cans in
WEBSITE_HERO), same subtle treatment everywhere, **structurally guaranteed** rather than
per-asset-authored: the droplets live in the shared `Can.dc.html` component (fixed 2026-08-21), so
every `<dc-import name="Can" ...>` call picks them up automatically. Previously this section
flagged condensation as present on only 1 of 5 assets — that inconsistency is now resolved at the
component level, the same way symbol and color consistency already were.

## 5. CGI vs. lifestyle usage

Per `BRAND_VISUAL_SYSTEM.md`, 4 of 5 assets (HERO_KEY_VISUAL, SKU_FAMILY_SHOT, CAMPAIGN_POSTER,
WEBSITE_HERO) should be CGI-rendered product shots, and SOCIAL_POST should be the deliberate
lifestyle exception. That structural split is preserved: SOCIAL_POST is the only asset with a
staged scene (desk, laptop, plant) rather than a plain product-focused background.

**Caveat already logged in `ASSET_GENERATION_NOTES.md`**: none of the 5 are actually photoreal CGI
or actual photography — all are flat/vector renders, so the *medium* distinction (CGI vs.
photography) that Rule 5 is really about could not be tested at its intended fidelity. The
*compositional* distinction (clean product shot vs. staged lifestyle scene) was preserved instead,
as the closest achievable proxy.

**Result: PASS at the compositional level; the underlying medium distinction is untestable with
available tools** (both branches ended up in the same rendering medium).

## 6. Overall brand coherence

Viewed side by side (all 5 PNGs in `generated_assets/`), the set reads unmistakably as one brand:
same symbol, same wordmark treatment, same three SKU colors, same light staging register. Nothing
in any asset drifts toward the source portfolio's heritage/ornamental register (no dragon motifs,
no calligraphic type, no dark maroon staging) — the anti-drift check from
`BRAND_SYSTEM_CONSISTENCY_CHECK.md` holds across the actual generated outputs, not just the written
spec.

**Result: PASS.**

## Summary

| Check | Result |
|---|---|
| Super-symbol consistency | ✅ PASS (structurally verified via shared component) |
| Typography hierarchy consistency | ✅ PASS |
| SKU color logic | ✅ PASS |
| Composition family resemblance | ✅ PASS — condensation inconsistency fixed, now structurally verified via shared component |
| CGI vs. lifestyle usage | ✅ PASS at composition level; medium distinction untestable this session |
| Overall brand coherence | ✅ PASS |

**Overall: the 5 assets pass as one coherent brand system, with no open cross-asset
inconsistencies.** The one concrete issue found in the prior round (condensation droplets present
on some assets, absent on others) has been fixed by moving the treatment into the shared `Can`
component, so it's now structurally guaranteed everywhere a can appears — the same mechanism
already relied on for symbol and color consistency. One disclosed capability ceiling remains
(flat/vector medium standing in for photoreal CGI and real photography throughout); that is a tool
availability gap, not a Personal-Design-System-rule violation, and does not block proceeding.
