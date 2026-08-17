# QUERY_GAPS.md — 8.14 Inspiration Scale-Up

Exploratory findings from building `query_pool.csv` (41 candidates) against the
five target domains (merch, packaging, ecommerce, edtech, brand_design), the
declared Curify topic registry (`curify-frontend/messages/en/topics.json`,
185 topics), and its underlying taxonomy (`curify-frontend/lib/taxonomy.json`).
Not a single clean metric — see [FINDINGS.md](FINDINGS.md) for the collected-inspiration
side of this analysis.

## Coverage

**Reasonably covered:** `merch` (12 selected) and `ecommerce` (8 selected) — both
have a fully-authored parent topic page (`merch`, `ecommerce`) plus multiple
sub-vocabulary terms in `taxonomy.json` (tier3 under `product`/`character`/`culture`)
to derive distinct queries from.

**Under-covered:** `brand_design` (4 selected) and `edtech` (6 selected).
`brand_design`'s only declared parent is `branding`, whose keyword list
(`logo, brand-identity, visual-identity, brand-book, color-system, typography`)
is a flat set of 6 terms with no tier3 sub-branch of its own in `taxonomy.json`
— there is simply less real source vocabulary to derive queries from than
`packaging` or `product`, which each have 6-8 tier3 children. This is a genuine
data-driven imbalance, not an oversight — see "Next scaling batch" below.

## Topic gaps

**Rich (fully-authored, keyword-backed):** `merch`, `ecommerce`, `showcase`,
`branding`, `packaging`, `vocabulary`, `dialogue`, `information-card`, `insight`,
`learning`, `language` all have real `title`/`description`/`intro`/`keywords` in
`topics.json`.

**Declared but thin ("stub" topics — chip exists, page has no content):**
`mascots`, `character-ip`, `fan-art`, `original-ip`, `dunhuang`, `mogao-caves`,
`silk-road`, `modernized-artifact`, `cultural-fusion` (all under `merch`/`character`/
`culture`), and `flashcards`, `study-sheets`, `mind-maps`, `infographic` (under
`edtech`-adjacent `learning`/`design`). Per `lib/topicRegistry_pure.ts`'s own
comment, these render as a clickable chip but hit a "noindex-fallback" when the
topic page tries to resolve `title|description|keywords|intro` — i.e. they are
live in navigation with **zero backing content today**. 9 of our 36 selected
queries (all the cultural-merch and character-merch ones) target exactly these
stub topics, which is the single highest-leverage place for this batch to land:
filling them moves a topic from "chip with a 404-flavored page" to "chip with
real inspiration."

**Taxonomy vocabulary with no topic page at all (not even a stub):**
`food-packaging`, `beverage-packaging`, `cosmetic-packaging`, `electronics-packaging`,
`luxury-packaging`, `gift-packaging` (all fold into the single generic `packaging`
topic today), and `hero-banner`, `lifestyle-shot`, `flat-lay`, `detail-image`,
`mood-board`, `product-lineup`, `promotional-poster`, `logo-application` (fold
into `ecommerce`/`showcase`/`branding`). These are real, product-typed vocabulary
the taxonomy already tracks internally but has never turned into a page — a
plausible next tier of topic pages once there's inspiration evidence to justify one.

**Overlap warning:** `product` ("Commerce & Branding") and `ecommerce` topics
have near-identical keyword sets (`shopping`/`ecommerce` vs
`product-photography`/`hero-banner`/etc.) — worth a product-side review of
whether `product` should be merged into `ecommerce`+`branding` rather than kept
as a third overlapping parent.

## Style gaps

The selected batch itself is style-neutral at the query level (style comes out
during collection via `style_tags`, not query wording) — but the *source*
taxonomy's style vocabulary (`taxonomy.json#tier3.design`: `cartoon`, `kawaii`,
`ink`, `isometric`, `photorealistic`, `monochrome`, `watercolor`, `vintage`,
`illustration`, `hyperrealistic`, `y2k`, `metallic`, `neon`, `cinematic`, …) is
large and mostly untested against `packaging`/`ecommerce`/`brand_design` queries
specifically. Two concrete gaps worth flagging for the next batch:

- **Packaging + brand_design skew toward clean/minimal/photographic** in this
  batch (`luxury packaging`, `cosmetic packaging`, `brand color system`) — no
  query yet deliberately pairs packaging/branding with `illustration`,
  `handcrafted`, `maximalist`, or `retro` treatments, all of which are real,
  common packaging-design directions in practice.
- **Merch is the opposite** — heavily character/IP-driven (`kawaii`, `cartoon`,
  `illustration` implied) with no `editorial` or `typographic` merch direction
  tested (e.g. a type-driven or photo-editorial museum-merch treatment vs. the
  illustrated-character default).

## Intent gaps

- **Audience:** most `brand_design` and `packaging` queries assume a B2B/brand-owner
  audience; only `classroom worksheet design for kids` (edtech) and the
  cultural-merch cluster (museum-visitor audience) explicitly target a
  consumer/end-user audience. No packaging query targets an individual
  gifting/personal-use occasion (e.g. wedding, birthday) as opposed to a
  generic retail SKU.
- **Industry vertical:** `brand_design` queries (`logo`, `color system`,
  `typography`, `brand book`) are entirely industry-agnostic. The task brief's
  own framing ("niche brand design") implies vertical-specific queries
  (e.g. a food brand vs. a tech startup vs. a fashion label) would surface more
  distinctive visual directions than generic identity-system queries — this is
  the clearest single opportunity for the next batch.
- **Platform:** `ecommerce` queries name `shopify`/`dtc` generically but don't
  differentiate marketplace-specific creative constraints (Amazon listing image
  rules vs. a DTC Shopify hero vs. a social-commerce card) even though the
  `topics.json` keywords already gesture at this distinction.
- **A3 (real user demand) is entirely absent this round** — every priority/gap
  judgment above is taxonomy- and benchmark-derived, not validated against
  actual search volume, zero-result queries, or low-CTR queries. This is the
  single biggest blind spot in this batch; see `DAILY_REPORT.md` for the exact
  export needed to close it.
