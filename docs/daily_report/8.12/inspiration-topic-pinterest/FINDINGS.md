# 8.12 Inspiration Topic + Pinterest Pilot — Findings

Scope: read-only research + data-preparation task in `visual-search-adhoc-inspiration-2026-08-11`.
No production code was changed. No commit/push/PR was created (see `git status` in the task's
final validation step).

---

## Google pilot

### 1. What are the original 47 records?

The 47-record dataset is the historical inspiration pilot at
`docs/daily_report/8.8/inspiration-source-pilot/`, in two equivalent forms:
- `inspirations.jsonl` — 47 JSON lines
- `SOURCE_CANDIDATES.csv` — 47 data rows (48 lines incl. header)

Every record's `discovered_via` field says **`WebSearch`** (in most cases paired with "Behance
project-search results"), not literally "Google Search." The latest product meeting identifies
this pilot as the "Google Search 47-record dataset" — we use that label for the pilot as a whole
(discovery channel), while keeping the **source URL/domain** distinct: 45 of 47 records resolve
to `behance.net`, 1 to `designkit.cn`, 1 to `andreaspedersen.se`. In short: **47 inspiration
records discovered through the Google/WebSearch pilot, with the resulting records pointing to
their underlying source pages** (mostly Behance case studies, not "google.com" pages themselves).

### 2. How many unique queries were actually used?

**10 unique queries** (10 unique `query_id`s), each backed by 4–5 records.

### 3. What are the 10 queries?

`figure` (V004, 5), `product photo` (V174, 5), `sticker` (V014, 5), `influencer post` (V216, 4),
`flashcard` (V248, 4), `logo` (V084, 5), `certificate` (V260, 4), `business card` (V094, 5),
`coffee package` (V098, 5), `gift box` (V120, 5). Sum = 47.

### 4. Are there duplicate source URLs?

**No.** All 47 `source_url` values are unique, and all 47 `canonical_url` values are unique.
Re-verified in this session with an exact-match and a normalized (protocol/`www.`/trailing-slash
insensitive) URL comparison across every field in both `inspirations.jsonl` and
`SOURCE_CANDIDATES.csv` — zero unexplained duplicate/repeated links found anywhere in the 47
records.

### 5. The `pack_v098_003` two-URL case

`pack_v098_003` ("Swerl Coffee Roasters", query `coffee package`) has:
- `source_url`: `https://www.behance.net/gallery/151709757/Swerl-Coffee-Roasters-Brand-identity-packaging`
- `canonical_url`: `https://andreaspedersen.se/work/swerlcoffeeroasters`

These are **legitimately two different URLs** — the Behance page is where it was discovered, the
designer's own portfolio site is a richer canonical source. This is documented in the original
pilot's `INSPIRATION_INTEGRATION_FINDINGS.md` as the proof case that `source_url`/`canonical_url`
are "a real, non-redundant distinction," not a data error. The record is **preserved as-is** in
`google_pilot_clean.csv`, with an explicit note in its `mapping_notes` field explaining the
distinction, and is **not** flagged as a duplicate anywhere in this task's outputs.

### 6. What manually annotated tags/domains/subdomains exist?

Every record carries: `domain` (5 values: `merch`, `ecommerce`, `education`, `brand_logo`,
`packaging`), `subdomain` (one per query, e.g. `figure_generic`, `product_photography`,
`sticker`, `social_commerce_content`, `flashcard_generic`, `logo`, `certificate_generic`,
`print_collateral`, `food_beverage_packaging`, `gift_packaging`), a free-form `tags` array
(3–6 tags per record), plus `source_type`, `source_quality_recommendation` (A/B/C),
`source_quality_reason`, `human_review_status`, `access_status`, `source_expansion_status`,
`creator_or_author`, `content_understanding`. Full detail already reported in the prior turn of
this task; summarized here for completeness.

---

## Topic mapping

### 7. Mapped / needs_product_confirmation / unmapped counts

| Status | Queries | Records |
|---|---|---|
| mapped | 3 | 13 |
| needs_product_confirmation | 4 | 20 |
| unmapped | 3 | 14 |
| **Total** | **10** | **47** |

Source of truth for every topic id: `lib/taxonomy.json` and `messages/en/topics.json` in the
read-only `curify-frontend-workflow-inspiration-2026-08-09` reference directory.

### 8. Clear mappings (`mapped`)

- **sticker** → `stickers` (exact match; declared topic, stub-only i18n entry)
- **flashcard** → `flashcards` (exact match; declared topic, stub-only i18n entry)
- **influencer post** → `social-media-posts` (conceptual match, only real candidate; declared topic, stub-only)

### 9. Ambiguous/broad mappings (`needs_product_confirmation`)

- **product photo** → `product` / `ecommerce` / `showcase` (3 plausible declared candidates, no single canonical slug)
- **logo** → `branding` (closest declared topic; taxonomy has `logo-application` as a tier3 vocabulary entry under `product`, but it is **not** declared in `topics.json` — no page exists for it)
- **coffee package** → `packaging` (only the generic topic is declared; taxonomy's finer `food-packaging`/`beverage-packaging` tier3 entries are undeclared)
- **gift box** → `packaging` (same pattern; taxonomy's `gift-packaging` tier3 entry — whose name nearly matches the pilot's own subdomain `gift_packaging` — is undeclared)

### 10. Currently missing topics (`unmapped`)

- **figure** — zero hits for `figure`/`toy`/`collectible` anywhere in `taxonomy.json` or `topics.json` (verified via direct grep). Adjacent declared topics (`merch`, `character`, `mascots`, `character-ip`) exist but do not cover 3D collectible figures.
- **business card** — zero hits for `business-card`/`stationery`/`print-collateral` anywhere in either file.
- **certificate** — zero hits for `certificate` anywhere in either file. `information-card` is the only remotely adjacent declared topic, but it is a stretch, not a real match.

These three are genuine **product/taxonomy gaps**, not something this task's data preparation can resolve.

### 11. No invented topic IDs

Every `proposed_internal_topic` / `candidate_curify_topic_ids` value in
`google_pilot_clean.csv`, `topic_mapping.csv`, and `authoritative_queries.csv` is a slug quoted
directly from `messages/en/topics.json` (i.e., a topic that is actually declared/navigable today).
No new slug was invented; where no real candidate existed, the field is left blank and the query
is marked `unmapped` rather than assigned a plausible-sounding but nonexistent id.

---

## Pinterest

### 12. How many of the same 10 queries were attempted?

**All 10** of the queries from `authoritative_queries.csv` were attempted, exactly as written —
no query text was altered, added, or expanded. Method: Chrome browser automation
(`claude-in-chrome`), navigating to `https://www.pinterest.com/search/pins/?q=<query>` for each
query and extracting pin data (title text, thumbnail URL, pin URL, visible retailer/source name)
directly from the rendered search-results grid via a read-only DOM query. No forms were
submitted, no account actions were taken (no pins saved, no boards created, no follows).

**Caveat on session state:** the shared Chrome session used for this pilot happened to already be
signed in to a Pinterest account (ambient state of the user's existing browser profile — not
something initiated for this task; no login action, saved-cookie injection, or credential entry
was performed to reach that state). Only public pin-search-grid results were viewed; no
private boards, saved pins, or account-only content were accessed. A logged-out or different
session could plausibly see different/less-personalized results — this is a reproducibility
caveat, not a bypass.

### 13. How many returned useful candidates?

- **9 of 10** queries returned pins at all (44 candidates captured total).
- **8 of 10** queries returned at least one candidate judged relevant/usable on inspection
  (title + image + domain consistent with the query's design intent).
- **1 of 10** (`gift box`) returned **zero** results for the literal query string.

Note on `pinterest_candidates.csv` row count: the file has **45 data rows**, not 44 — 44 rows for
the real captured candidates plus **1 additional row that records the `gift box` zero-result
status itself** (`retrieval_status = zero_results_exact_phrase`, all Pinterest-specific fields
empty). That 45th row is a status record, not a candidate — **the correct candidate count is 44,
not 45**.

Per-query candidate/usable counts (full detail in `pinterest_candidates.csv` and
`google_vs_pinterest_comparison.csv`):

| query_id | query | candidates captured | usable |
|---|---|---|---|
| V004 | figure | 4 | 4 |
| V174 | product photo | 5 | 3 |
| V014 | sticker | 5 | 5 |
| V084 | logo | 5 | 3 |
| V094 | business card | 5 | 5 |
| V098 | coffee package | 5 | 5 |
| V120 | gift box | 0 | 0 |
| V216 | influencer post | 5 | 0 |
| V248 | flashcard | 5 | 5 |
| V260 | certificate | 5 | 1 |
| **Total** | | **44** | **31** |

(figure has 4 rather than 5 candidates because the 5th grid item's data was cut off by a tool
output-size limit mid-response; rather than guess its title/URL, that row was dropped instead of
fabricated.)

### 14. Access limitations observed

- **`gift box` returned zero results** for the exact literal phrase (`"Sorry, we couldn't find any
  Pins for this search"`, with suggested alternates: "Gift boxes for women," "Present boxes,"
  "Gift box template," "Christmas gift ideas," "Bday box"). Retested twice (space- and
  `+`-encoded URLs), same result both times. As a same-session diagnostic **only** (not used to
  substitute or expand the query set), the plural "gift boxes" was tried immediately after and
  returned 18 normal results — confirming this is a **literal-phrase search-index quirk specific
  to "gift box"**, not a login gate, rate limit, or general outage.
- **Outbound/original source URL is not extractable** for any of the 44 captured candidates. This
  was tested directly: opened one individual pin page and inspected (a) all rendered `<a>` tags,
  (b) the page's embedded initial-state JSON (`__PWS_DATA__`) recursively for any non-Pinterest
  `http` URL. Neither exposed the outbound "visit site" link — Pinterest resolves it only via a
  click-triggered action, not present in static markup or embedded JSON. This is recorded
  precisely as a field-level limitation in `pinterest_candidates.csv`
  (`outbound_source_url` = "not_available_from_search_grid...") rather than fabricated.
- **Per-pin tags/hashtags are not exposed** in the search-results grid; would require opening each
  of the 44 pins individually. Not attempted at this scale — recorded as `not_collected` rather
  than fabricated.
- **Title/source metadata is frequently missing** directly in the grid for some queries — most
  severely `certificate` (4 of 5 pins had no title text at all) and `influencer post` (5 of 5 had
  no title text AND no visible retailer/source badge). This lowered the "usable" count for those
  queries independent of any access block.
- No CAPTCHA, no explicit login wall, and no rate-limit message was encountered on any of the 9
  successful queries.

### 15. What kinds of inspiration/results did Pinterest return?

Overwhelmingly **retail/marketplace product photography** (Etsy, eBay, Zazzle, Depop, Poshmark,
Target listings) and **free-printable/blog-aggregator content**, plus a smaller number of
genuine **design-editorial roundups** (`My Modern Met` business-card article, two "coffee
packaging design trends" pins) and **native Pinterest lifestyle/UGC content** with no outbound
link at all (most of `influencer post`).

### 16. Relevance/diversity vs. the Google/WebSearch pilot

The Google/WebSearch pilot is uniformly **designer-portfolio case studies** (mostly Behance),
each with a named creator, a quality grade (A/B/C), and — for several records — visible
design-process documentation (sketches, prototypes, multiple stages). Pinterest results for the
same queries are, on the whole, **less diverse and more commerce-oriented**: single finished
product photos rather than process documentation, frequently missing even basic title metadata
(worst on `certificate` and `influencer post`), and for none of the 44 candidates could an
outbound source URL be resolved (vs. 100% of the 47 Google records having a working
`source_url`/`canonical_url` pair). The two queries where Pinterest performed best relative to
Google were `sticker`, `business card`, `coffee package` and `flashcard` (5/5 usable, some real
editorial/design-roundup content); the weakest were `certificate` (1/5, mostly untitled) and
`influencer post` (0/5 usable, no source metadata at all). Full per-query evidence in
`google_vs_pinterest_comparison.csv`.

---

## Recommendation

### 17. Should Pinterest be used as replacement / supplement / not useful yet?

**Supplemental at most, not a replacement, and not yet ready to use as-is.** Evidence:
- Pinterest never matched Google/Behance's 100% outbound-URL-resolution rate — every one of the
  44 candidates lacks a resolvable outbound source URL with the tested method, which is a hard
  requirement the current Google pilot schema (`source_url`, `canonical_url`) satisfies for all
  47 records.
- Pinterest's usable-candidate rate varied hugely by query (0/5 to 5/5), and title/source
  metadata was frequently missing outright — this is inconsistent enough that per-query manual
  review would be required before any candidate is trusted at the same quality bar as the Google
  set.
- One query (`gift box`) produced zero results outright, for reasons unrelated to a general
  Pinterest access problem (a literal-phrase quirk), which is itself evidence that any
  broader Pinterest pass needs per-query verification, not blind automation.
- On the queries where it performed well (`sticker`, `business card`, `coffee package`,
  `flashcard`), Pinterest did surface a genuinely different visual style (retail product photos,
  free-printable aesthetics, editorial roundups) not present in the Behance-heavy Google set —
  real supplemental value, not redundant noise. This is evidence-based, not "Pinterest is a
  design platform so it must be better."

### 18. Smallest sensible next step

Do **not** run a full Pinterest re-collection or automate outbound-URL resolution yet. The
smallest sensible next step is: **have product confirm the 4 `needs_product_confirmation` topic
mappings and decide on the 3 `unmapped` topic gaps** (this is blocking regardless of source), then
**only if/when a business-card or similar new topic is created**, revisit Pinterest specifically
for that query since it had the strongest showing (5/5 usable, incl. a real editorial roundup) —
rather than re-running all 10 queries again.

---

## Product boundary

**The production step of making mapped records appear in Search Results, Creative Exploration,
Inspiration Hub, or Topic Pages is a separate future `curify-frontend` implementation task and
was NOT performed here.** This task only produced read-only research and CSV/thumbnail data
artifacts inside `visual-search-adhoc-inspiration-2026-08-11`; no frontend repository was read
for anything beyond taxonomy verification (read-only), and none was modified.

---

## Workflow direction

Recorded per the meeting clarification only (no further workflow research performed in this
task): workflow data has two product destinations — **(1) `/resources` case studies** and
**(2) vertical-specific workflows**. The five-domain workflow study itself was not redone here.

---

## Lovart

Recorded per the meeting mention only: **Lovart** was named as another possible
design-inspiration source for future evaluation. **No Lovart crawl or research was performed in
this task.**
