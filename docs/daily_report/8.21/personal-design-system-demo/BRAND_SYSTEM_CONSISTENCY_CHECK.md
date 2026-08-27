# Brand System Consistency Check — 荔泉气泡

Validates `BRAND_VISUAL_SYSTEM.md` against the Personal Design System, the new brief, and the
task's explicit anti-copying and anti-fabrication requirements.

## 1. Every major design choice maps to the Personal Design System or the brand brief

Checked against `BRAND_SYSTEM_TRACEABILITY.md`'s full table: every row resolves to either a numbered
Signature Rule (1, 2, 3, 5, 6, 7, or the optional 4), a named §-level narrative observation (the
whitespace/density note in §4, explicitly flagged there as medium-confidence rather than a numbered
rule), or an explicit brief-level/task-instruction decision (the standard-can baseline, the specific
flavor names, the brand name). No row is unaccounted for.

**Result: PASS.**

## 2. No direct copying of a source work

- The super-symbol (bubble-sprout inside a circle) does not match any sampled work's mark: it is
  not work_05's eye/comb-swoosh, not work_06's floral roundel, not work_09's leaf/arrow mark, and
  not work_01's dragon linework. Only the *container convention* (a circle) is shared, which is a
  recurring geometric habit across 4 works, not a single work's specific logo.
- The typography hierarchy (large Chinese, small Latin) follows the *same relationship* as work_01,
  but uses a plain modern sans/rounded display style rather than work_01's calligraphic seal-script
  rendering, and a wholly different brand name/wordform — this is explicitly called out in
  `BRAND_VISUAL_SYSTEM.md` §Typography as "not copying that specific art style."
  Chosen deliberately: work_01's calligraphic register belongs to that
  brand's premium-spirits/heritage positioning, which this brief explicitly does not share.
- The 3-SKU family system is modeled on work_05's *mechanism* (one mark, varying dominant hues) but
  applied to a beverage-can format work_05 never shows (work_05 is a hairbrush/comb line) — a new
  application of a transferable mechanic, not a reproduction of work_05's actual product, color
  values, or SKU count.
- No packaging photograph, prop arrangement, or scene composition described in
  `BRAND_VISUAL_SYSTEM.md` reproduces any sampled work's specific staging (e.g. no dark maroon
  velvet surface with brush and cups as in work_01; no burgundy flat-lay table setting as in
  work_06).

**Result: PASS.**

## 3. No unsupported exact source colors/fonts

`BRAND_VISUAL_SYSTEM.md` §Color Behavior explicitly states the three SKU hues and the shared accent
are "newly designed brand values... not extracted, sampled, or estimated from any source-portfolio
image," and no hex value is given anywhere in the document. §Typography Direction explicitly
disclaims any named source-portfolio typeface. Grepped both `BRAND_VISUAL_SYSTEM.md` and this
checklist for hex-style strings and named font families — none present.

**Result: PASS.**

## 4. The system is coherent across all 3 SKUs

The SKU table in `BRAND_VISUAL_SYSTEM.md` §SKU/Family System holds four elements constant across
Lychee Rose, Cucumber Mint, and Yuzu Ginger (the super-symbol shape/scale/position/fill, the full
typographic hierarchy, the can silhouette, and the shared accent color) while varying exactly two
elements (dominant background hue, one small quaternary-tier botanical icon). This is a closed,
specific rule — not a vague "keep them similar" instruction — and matches the same
constant-vs-varying split directly observed in work_05 (mark/logo constant, box color varies).

**Result: PASS.**

## 5. The brand still fits plant-protein sparkling water, not wine/tea/food packaging carried over from the portfolio

Checked for register drift toward the source portfolio's heritage/CPG-food categories:

- **Color/lighting register**: `BRAND_VISUAL_SYSTEM.md` explicitly places this brand in Rule 6's
  *light-backdrop* branch (bright, cool, soft studio lighting, near-white ground), the same branch
  work_02/04/08/10 occupy — explicitly **not** the dark/maroon dramatic branch used for work_01's
  spirits or work_06's festival gift box. This is the single most important anti-drift check, since
  a dark, ornamental, gold-accented treatment would have made this read as premium liquor/tea
  packaging rather than a youthful sparkling water.
- **Illustration style**: no ornamental linework, no folk-art mascot character, no traditional
  motif (dragon, floral roundel, calligraphy) appears anywhere in the system — the super-symbol is
  a simplified modern geometric mark, consistent with work_03's abstract-geometric register rather
  than work_01/09's illustrative-heritage register.
- **Format/staging**: baseline packaging is an aluminum beverage can with condensation-droplet
  staging — a beverage-specific visual cue with no equivalent in the sampled portfolio (none of the
  10 works is a beverage), so this detail is a new-brief addition, not something that could have
  been carried over incorrectly from a wine/tea/food work.
- **Tone/copy**: the core message ("轻盈气泡，源头养分" / "Light bubbles, real nourishment") and the
  brief's occasion (desk-break, post-workout, commute) are unambiguously beverage/wellness-register,
  with no gifting, ceremonial, or festival framing carried over from work_01/06.

**Result: PASS.** The system reads as a contemporary plant-protein sparkling water brand, not as a
relabeled wine, tea, or heritage food package.

## Summary

| Check | Result |
|---|---|
| Every choice maps to system or brief | ✅ PASS |
| No direct copying of a source work | ✅ PASS |
| No unsupported exact colors/fonts | ✅ PASS |
| Coherent across 3 SKUs | ✅ PASS |
| Fits plant-protein sparkling water, not portfolio's other categories | ✅ PASS |

**Overall: the system passes all five consistency checks.** The one area worth a second look before
Phase 4 asset generation is the optional pull-tab embossing detail (Rule 4, form-as-symbol) —
already labeled non-baseline in `BRAND_VISUAL_SYSTEM.md`, and the traceability doc already flags it
as resting on the Personal Design System's softest HIGH rule. No change is needed; it's flagged so
Phase 4 doesn't accidentally treat it as a hard requirement.
