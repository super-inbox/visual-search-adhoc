# FINDINGS.md — 8.14 Inspiration Scale-Up

66 new inspiration records collected across all 36 selected queries, spanning
merch, packaging, ecommerce, edtech, and brand_design. This is exploratory —
see [QUERY_GAPS.md](QUERY_GAPS.md) for the query/topic-gap analysis this batch
was built to close, and [DAILY_REPORT.md](DAILY_REPORT.md) for exact counts.

## Query-source findings

**A1 (`exploration.jsonl`, 30 raw benchmark lines) contributed narrowly but
usably.** The file is a visual-intent-routing *template benchmark* (10 themes
× 3 language variants), not organic search queries — each line reads like
"explore three visual directions for X." Only 4 of the 10 themes had any real
overlap with the five target domains (12/30 lines), and 3 languages of the
same theme collapse to one usable query concept, so A1 ultimately yielded
just 4 distinct queries: a home-fragrance ecommerce launch, two fandom-merch
themes (Marvel, Chiikawa), and one edtech homophones theme (the last was
reserved, not collected — near-duplicate of the old pilot's `flashcard`
query). A1 contributed **zero** usable queries for `packaging` or
`brand_design`.

**A2 (curify-frontend topic registry) did the heavy lifting.** 37 of the 41
pool queries — and 33 of 36 selected — were derived from `messages/en/topics.json`
(185 declared topics) and `lib/taxonomy.json` (tier1-4 vocabulary). This is
where the batch's most useful discovery came from: 9 of the merch queries
target topics that are **declared in navigation but have zero authored
content** (`mascots`, `fan-art`, `original-ip`, `dunhuang`, `mogao-caves`,
`silk-road`, `modernized-artifact`, `cultural-fusion`, plus edtech's
`study-sheets`/`mind-maps`) — see `lib/topicRegistry_pure.ts`'s own comment
describing these as hitting a "noindex-fallback." This batch is disproportionately
useful for exactly those stub topics.

**A3 (real user query data) was unavailable.** Confirmed via
`docs/daily_report/7.17/search-click-generate-data-audit/`: real per-query
click/CTR/zero-result data lives only in production Postgres and requires
DB credentials this task explicitly may not access. Every priority judgment
in this batch is taxonomy/benchmark-derived, not demand-validated — the
single largest blind spot going into the next batch (see DAILY_REPORT.md).

## Domain findings

- **merch (22 records / 12 queries):** The richest domain in this batch —
  covers both fandom/character merch (Marvel, Chiikawa, mascots, fan-art,
  original-IP, sprite sheets) and Chinese cultural-heritage "文创" merch
  (Dunhuang, Silk Road, Mogao Caves, modernized-artifact, cultural-fusion).
  Dunhuang yielded a strong, on-topic hit (a real Jingdezhen ceramic
  co-branded cultural-creative product — quality A). Mogao Caves (S012)
  initially yielded no genuinely on-topic souvenir-design results under
  `WebSearch`/`curl` — only travel photography of the caves themselves — but
  a same-session follow-up using interactive browser automation found 2 real,
  verified souvenir-product records (a handmade Etsy fridge magnet and a
  Zazzle magnet, both explicitly Mogao-Caves-themed), confirming the gap was
  a tooling-access limit rather than a genuine absence of on-topic content.
  A second, later addendum this session applied the same
  interactive-browser-with-more-specific-search-terms treatment to the three
  remaining thin culture-tier3 topics flagged for a follow-up pass —
  `silk-road`, `modernized-artifact`, `cultural-fusion` — adding 2 new
  verified records to each (6 total: `merch_S013_003/004`,
  `merch_S014_002/003`, `merch_S015_003/004`). Every addendum record was
  found via a live Pinterest search grid and independently verified by
  reading the actual pin page (product price/description/award listing where
  present); the Xijiu Silk Road liquor packaging (A' Design Award winner) and
  the Fusion streetfood-cafe brand identity (a complete logo/livery/packaging
  system) are both quality-A, materially stronger than anything the original
  `WebSearch`/`curl` pass found for these three topics.
- **packaging (12 records / 6 queries):** Solid coverage of product-type
  variety (food, beverage, cosmetic, electronics, luxury, unboxing) that the
  old pilot never touched (which only had `coffee package` and `gift box`).
  All sources are quality B — mostly Pinterest lifestyle/inspiration pins
  rather than deep designer case studies, since Behance/Dribbble/The Dieline
  all blocked automated fetches this session (see External-source findings).
- **ecommerce (14 records / 8 queries):** Good spread across hero banners,
  lifestyle shots, flat-lays, detail images, mood boards, and DTC campaign
  visuals — genuinely different visual treatments of "product photography,"
  not restatements of the old pilot's single `product photo` query.
- **brand_design (8 records / 4 queries):** Smallest domain by query count
  (matches the QUERY_GAPS.md finding that `branding`'s taxonomy vocabulary is
  thinner than the other four domains) but yielded the **highest quality
  scores of the batch** — 2 of 8 records graded A (a real named-designer
  typography suite and a real Behance visual-identity case study), reflecting
  that "brand identity system" is a well-established Pinterest/Behance search
  category with strong existing content.
- **edtech (10 records / 6 queries):** Even spread across vocabulary,
  dialogue, study-sheets, mind-maps, information-cards, and classroom
  worksheets. Notably, the `study sheet infographic design` query surfaced an
  "aesthetic study notes" visual trend (handwritten, decorated, Instagram/
  Pinterest-native study content) that is a genuinely different visual
  direction from the flashcard/infographic aesthetic the old pilot's
  `flashcard` and `certificate` queries produced.

## Topic richness

- **Richest:** `merch`, `ecommerce`, `branding` — all fully-authored parent
  topics with real keyword sets in `topics.json`, and this batch adds several
  genuinely distinct sub-directions to each (character-merch vs cultural-merch
  vs flatlay-merch; hero-banner vs flatlay vs mood-board ecommerce; color-system
  vs typography vs brand-book branding).
- **Thin but now seeded:** the culture-tier3 stub topics (`dunhuang`,
  `silk-road`, `modernized-artifact`, `cultural-fusion`) and the
  character-tier3 stub topics (`mascots`, `fan-art`, `original-ip`) had zero
  prior inspiration content in this repo's pilots; this batch gives each 1-2
  real candidate records, which is a start but not yet "rich" — 1-2 records
  per topic is not enough to represent real style diversity within that topic.
  A same-session second-pass addendum brought `silk-road`,
  `modernized-artifact`, and `cultural-fusion` up to 4/3/4 records
  respectively (from 2/1/2 originally)
  — still not "rich" by the same standard, but no longer at the single- or
  double-record floor. `dunhuang`, `mascots`, `fan-art`, and `original-ip`
  were not re-touched and remain at their original batch counts.
- **Repetitive risk:** `packaging`'s six product-type queries (food/beverage/
  cosmetic/electronics/luxury/unboxing) all route to the single generic
  `packaging` topic page today (per QUERY_GAPS.md, none of these product-type
  sub-vocabulary terms have their own topic page) — if this topic page is the
  actual integration target, it risks becoming a large undifferentiated bucket
  rather than reflecting the real sub-category diversity this batch collected.
- **Missing style diversity confirmed:** as predicted in QUERY_GAPS.md, no
  record in this batch shows an illustrated, handcrafted, or maximalist
  packaging/branding treatment — every packaging and branding record collected
  is photographic/clean-minimal. The one exception is edtech's "aesthetic
  study notes" pins, which lean handcrafted/illustrative.

## External-source findings

**Pinterest was the only reliably automatable source this session.**
Behance, Dribbble, and The Dieline all returned HTTP 403 to both WebFetch and
direct `curl` with a browser user-agent — these sites now actively block
non-interactive fetches. This is a **hard technical constraint**, not a
quality choice: it means this batch is 100% `pinterest_pin` sourced, versus
the old pilot's Google/Behance-heavy mix. Practical effect: quality skews
toward Pinterest's own distribution (B-grade lifestyle/inspiration pins are
common; A-grade individually-authored designer case studies are rarer, since
many strong Behance/Dribbble case studies surface in Pinterest search only as
a re-pinned thumbnail, not a direct link to the original case-study page).

A same-session follow-up confirmed part of the fix: switching from
`WebFetch`/`curl` to **interactive Chrome browser automation** (available
later in this session) immediately unblocked the one documented zero-result
query (`S012`, Mogao Caves) via a live Pinterest search-grid extraction and
page-text read, without any login or account interaction. This validates the
report's original hypothesis that the prior 8.8/8.12 pilots' apparent edge
came from interactive browser tooling, not a different source mix. A second
addendum later this session extended the same fix to `S013`/`S014`/`S015`
(silk-road, modernized-artifact, cultural-fusion), each re-run with more
specific Pinterest search terms than the original query text, per
DAILY_REPORT.md's recommended next action — 6 new verified records total, 2
per topic. Behance/Dribbble/Dieline were still not re-tested with the browser
tool this session and remain unconfirmed as unblockable this way. See
DAILY_REPORT.md for the exact blocker detail and remaining recommended next
steps.
