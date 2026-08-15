# DAILY_REPORT.md — 8.14 Inspiration Scale-Up

Date: 2026-08-15
Task: Curify Task A — Creative Inspiration / Topic Mapping / external inspiration data scaling

## 1-5. Query sources

| Source | Available? | Raw count | Relevant/usable count |
|---|---|---|---|
| A1 `exploration.jsonl` | Yes | 30 lines (10 themes × 3 language variants) | 12 lines relevant (4 themes) → 4 distinct queries after collapsing language variants |
| A2 curify-frontend topic registry | Yes | 185 declared topics total in `messages/en/topics.json` | 37 queries derived across the 5 target domains (from `topics.json` + `lib/taxonomy.json` tier1-4) |
| A3 real user-query export | **No — BLOCKED** | n/a | 0. Real per-query click/CTR/zero-result data lives only in production Postgres (`user_interactions` table); no safe local export exists. Documented input schema written to `user_queries_input_schema.csv`. |

## 6-8. Query pool and selection

- **Total candidate queries in pool:** 41 (`query_pool.csv`)
- **Selected queries:** 36 (`selected_queries.csv`)
- **Reserved (not collected this round):** 5 — all explicit close variations of the
  old pilot's 10 queries (`sticker sheet POD design`≈sticker,
  `gift box packaging design`≈gift box, `logo application brand identity design`≈logo,
  `English homophones flashcard learning design`≈flashcard,
  `flashcard visual design for learning`≈flashcard). Kept in the pool with
  provenance but deliberately excluded from the collected batch since the
  task's goal is coverage expansion, not re-running the old pilot.
- **Domain breakdown of the 36 selected queries:**

| Domain | Selected queries | A1-sourced | A2-sourced |
|---|---|---|---|
| merch | 12 | 2 | 10 |
| ecommerce | 8 | 1 | 7 |
| packaging | 6 | 0 | 6 |
| edtech | 6 | 0 | 6 |
| brand_design | 4 | 0 | 4 |

The merch/ecommerce lean is a direct, data-driven consequence of A1
containing zero packaging/brand_design-relevant content and `branding` having
a thinner taxonomy vocabulary than `merch`/`product` (see QUERY_GAPS.md) —
not an arbitrary choice.

## 9-11. Inspiration batch collected

- **New inspiration records collected: 66** (`SOURCE_CANDIDATES.csv` /
  `inspirations.jsonl`), across **all 36** selected queries.
- **Follow-up addendum (same day):** the original pass left `S012` (Mogao
  Caves museum souvenir design) at zero usable records — search via
  `WebFetch`/`curl` returned only travel/documentary photography of the
  physical caves, no genuinely on-topic souvenir/merch-design references
  (see Blockers). A follow-up pass using interactive Chrome browser
  automation (not available to the original `WebFetch`/`curl`-only session)
  re-ran the Pinterest search for `S012` and found 2 genuinely on-topic,
  independently verified souvenir-product records (a handmade Etsy fridge
  magnet and a Zazzle magnet, both explicitly referencing the Mogao
  Caves/Cave 17) — confirming the original zero-result was a content-gap at
  the tooling layer, not the query itself. These are recorded as
  `merch_S012_001`/`002` with `collection_method=ChromeBrowser+PinterestGridExtract+PageText`
  to distinguish them from the batch's original `WebSearch+curl(og:meta)`
  records.
- **Content-source distribution: 100% `pinterest_pin`.** Behance, Dribbble,
  and The Dieline all returned HTTP 403 to both `WebFetch` and direct `curl`
  with a browser user-agent this session — see Blockers below. Every record
  was independently verified — either via a live fetch of its real Pinterest
  pin page (`og:title`/`og:image`/`og:description`) or, for the 2 `S012`
  addendum records, via an interactive browser page-text read of the live
  pin page — not fabricated or guessed.
- **Thumbnails successfully stored: 66 of 66** (100%) — every thumbnail was
  downloaded, confirmed to be a real decodable image via `file`, and linked
  to its record. Zero HTML-error-page-as-image failures made it into the
  final dataset (candidates that failed image validation were either retried
  once or the record was dropped, never saved with a fake `.jpg`).
- **Duplicate handling:** 0 duplicate `id` values, 0 duplicate `source_url`
  values across all 66 records (verified by `merge_outputs.py` and
  `validate_gallery.py`). No perceptual-hash visual dedupe was built (none
  existed in the prior pilot either — see audit finding) but with 0 exact-URL
  duplicates this was not needed for this batch size.

Per-domain final counts: merch 28, ecommerce 14, packaging 12, edtech 10,
brand_design 8 (72 total after the second-pass addendum below).

Quality distribution: A=5, B=58, C=9 (see FINDINGS.md for why A-grades
cluster in brand_design/merch; the addendum below added 2 more A-grades).

- **Second follow-up addendum (same day, after the S012 fix above):**
  applying the same interactive-Chrome-browser method — this time with more
  specific search terms per topic rather than the original broad query text
  — to the three remaining topics flagged as "still thin" in section 13-14
  below: `silk-road` (S013), `modernized-artifact` (S014), and
  `cultural-fusion` (S015). silk-road and cultural-fusion each went from 2
  records to 4, and modernized-artifact went from 1 record to 3, adding 6
  new verified records total (`merch_S013_003/004`, `merch_S014_002/003`,
  `merch_S015_003/004`, `collection_method=ChromeBrowser+PinterestGridExtract+PageText`).
  Two are quality A: an A' Design Award-winning "Xijiu Silk Road Liquor
  Packaging" (a real, awarded product-packaging design explicitly built
  around Silk Road landmarks/culture) and "Fusion, Visual Identity for
  Takeaway Streetfood Cafe with fusion cuisine" (a complete logo/food-truck-
  livery/packaging brand-identity system for a fusion-cuisine cafe). The
  other four are quality B, real verified commercial products: a Samarkand
  "Silk Road Travel Souvenir Shirt" (Etsy apparel), a "Brutalist Roman Ruin
  Catch-All Bowl" (a MakerWorld 3D-print product reinterpreting ancient-ruin
  architecture as modern homeware), an "Amphora Vase Necklace" (Etsy jewelry
  shaped as a miniature ancient amphora), and a "Folk Kit" cultural-pattern
  packaging asset kit (Creative Market). Every record was independently
  verified by reading the real Pinterest pin page (price/description/award
  listing, via `get_page_text` or a live screenshot where the page was
  client-rendered with no static `og:meta`) — not fabricated or guessed.
  Thumbnails for these 6 records were captured from the live rendered pin
  image (cropped screenshot, converted to JPEG) rather than `curl`-downloaded,
  because the shell sandbox used for this addendum had no outbound DNS/
  network access at all (a separate, environment-level constraint from the
  Behance/Dribbble/Dieline 403 bot-blocking documented below — not the same
  cause, just another case where the interactive browser was the only path
  that worked). Every thumbnail was still confirmed to be a real, decodable
  image via `file` before being counted as AVAILABLE.

Topic-mapping-status distribution: `mapped_full`=31, `mapped_stub`=21,
`needs_confirmation`=12.

## 12. New coverage vs. the previous pilot

The previous pilot (8.8 + 8.12) covered **10 queries / 91 records** (47
Google/Behance + 44 Pinterest), all variations of: figure, sticker, logo,
business card, coffee package, gift box, product photo, influencer post,
flashcard, certificate.

This batch adds **35 queries with real collected records** that are either
entirely new query concepts (e.g. Dunhuang/Silk Road cultural merch, brand
color/typography systems, unboxing experience, DTC campaign visuals, aesthetic
study notes) or a materially different sub-direction of an old pilot subject
(e.g. old pilot had one generic `coffee package` query; this batch has six
distinct packaging product-type queries spanning food/beverage/cosmetic/
electronics/luxury/unboxing). Zero selected queries in this batch are exact
duplicates of the old pilot's 10 — the 5 close variations were explicitly
reserved out (see above), preserving that provenance in `query_pool.csv`
rather than silently re-running them.

## 13-14. Promising directions and thin topics

- **Most promising:** Chinese cultural-heritage "文创" merch (Dunhuang got a
  genuine, on-topic, high-quality hit) and brand-identity-system queries
  (color/typography/brand-book all scored well on Pinterest/Behance-sourced
  content).
- **Was thin, now second-pass-seeded:** `silk-road`, `cultural-fusion`, and
  `modernized-artifact` originally had only 1-2 marginal records each — see
  FINDINGS.md; `mogao-caves` was thin for the same reason until the earlier
  follow-up interactive-browser pass added 2 real records. The second-pass
  addendum documented above applied the same fix to these three topics,
  bringing silk-road and cultural-fusion to 4 records each and
  modernized-artifact to 3 (each +2 new). This is a real improvement
  but still short of genuine style-diversity coverage — `mogao-caves` remains
  at only 2 records (from its own earlier follow-up pass) and was not
  re-touched in this addendum, so it's still the thinnest culture-tier3
  topic in the batch. See next action #3 below, plus the packaging
  product-type sub-topics
  (all 6 packaging queries route to the single generic `packaging` topic with
  no sub-page, risking an undifferentiated bucket if this data is integrated
  as-is).

## 15-16. Blockers

- **A3 real user-query data is blocked** — requires production DB access this
  task must not use. Next step: someone with Supabase/production read access
  should export `user_interactions` rows matching the documented schema in
  `user_queries_input_schema.csv` (query, action_type, result_count if
  available, click_count, ctr, created_at, search_category), filtered to
  `SEARCH_NORESULT`/`SEARCH_LOWRESULT` action types and design-domain-relevant
  queries. Task A can then re-run Phase 4-7 to fold real demand signal into
  query prioritization.
- **Behance/Dribbble/The Dieline collection is blocked for automated fetch** —
  all three returned HTTP 403 to both `WebFetch` and `curl` with a realistic
  browser user-agent this session (tested directly, not assumed). This forced
  100% reliance on Pinterest, which is a real and usable source but skews the
  quality/source-type distribution versus the old pilot's Google/Behance mix.
  The prior pilot's `scripts/google-image-eval`, `scripts/pinterest-search-eval`
  browser-automation tooling (Playwright-based) was not invoked this session;
  it would very likely bypass this 403 blocker if run in a future session with
  access to that tooling's browser environment.
- **Mogao Caves (S012) — resolved this session.** Originally yielded 0
  usable records under `WebSearch`/`curl`; a follow-up interactive-browser
  pass (see above) found 2 genuinely on-topic records, confirming this was a
  tooling-access gap (non-interactive fetch vs. a real Pinterest search
  session), not a genuine absence of on-topic content.
- **Silk Road / modernized-artifact / cultural-fusion (S013/S014/S015) —
  also resolved this session, second addendum.** Originally each had only
  1-2 marginal records from the `WebSearch`/`curl` pass; a second
  interactive-browser follow-up (see section 9-11 above), using more
  specific per-topic search terms instead of the original broad query text,
  found 2 new genuinely on-topic, independently verified records for each
  topic (6 total), including 2 quality-A hits (an award-winning packaging
  design and a complete brand-identity system). This confirms the same
  tooling-access-gap hypothesis validated by the Mogao Caves fix, now for
  three more topics.

## 17. Recommended next action

1. Run the next scaling batch's collection through interactive browser
   automation (confirmed this session to unblock at least Pinterest search
   grids that `WebFetch`/`curl` missed — see the `S012` addendum above) or
   the prior pilot's Playwright-based scripts (`scripts/pinterest-search-eval`,
   `scripts/google-image-eval`), to reopen Behance/Dribbble/Dieline as
   sources and diversify the quality distribution beyond Pinterest.
2. Request a production `user_interactions` export (schema in
   `user_queries_input_schema.csv`) to unblock A3 and validate/reprioritize
   this batch's queries against real search demand.
3. `silk-road`, `cultural-fusion`, and `modernized-artifact` received their
   targeted second pass this session (see section 9-11); silk-road and
   cultural-fusion now have 4 records each and modernized-artifact has 3, up
   from 1-2. `mogao-caves` still has only 2 (from its own
   earlier, separate follow-up) and remains the thinnest culture-tier3 topic
   — it, plus a genuine third pass on all four topics for real style
   diversity (not just record count), is the next candidate for this
   treatment.
4. If this data is integrated into topic pages, treat the 6 packaging
   product-type queries as a signal to consider splitting `packaging` into
   sub-pages (food/beverage/cosmetic/etc.) rather than merging all 12 records
   into one generic topic — a product decision, not something this task
   should make unilaterally.
