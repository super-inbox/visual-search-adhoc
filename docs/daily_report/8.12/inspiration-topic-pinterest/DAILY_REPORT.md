# 8.12 Creative Inspiration Update

## 1. Google pilot cleanup

- 47 records, 10 unique queries (4–5 records each), all preserved and cleaned into
  `google_pilot_clean.csv`.
- **No duplicate source URLs** — all 47 `source_url` and 47 `canonical_url` values are unique
  (re-verified this session with exact + normalized matching).
- Thumbnails: 47/47 present locally (from the original 8.8 pilot).
- Important distinction: the meeting labels this the "Google Search" pilot (discovery channel),
  but the records themselves list `discovered_via = WebSearch` and point to **their underlying
  source pages** — 45/47 to `behance.net`, 1 to `designkit.cn`, 1 to `andreaspedersen.se`. We are
  not claiming every source domain is "google.com."
- `pack_v098_003` legitimately has two different URLs (`source_url` = Behance discovery page,
  `canonical_url` = the designer's own site) — preserved as-is, not treated as a duplicate.

## 2. Tag → Curify topic mapping

| Status | Queries | Records |
|---|---|---|
| mapped | 3 | 13 |
| needs_product_confirmation | 4 | 20 |
| unmapped | 3 | 14 |

- **Mapped:** `sticker`→`stickers`, `flashcard`→`flashcards`, `influencer post`→`social-media-posts`.
- **Needs confirmation:** `product photo` (3 candidates: `product`/`ecommerce`/`showcase`), `logo`→`branding` (broader than "logo" specifically), `coffee package`→`packaging`, `gift box`→`packaging` (both only match the *broad* packaging topic — finer taxonomy vocabulary exists but has no page yet).
- **Product gaps — do not exist as internal topics today:** `figure`, `business card`, `certificate`. Verified via direct search of `taxonomy.json` / `topics.json` — zero matches, not an oversight in this task's mapping logic.
- No new topic slugs were invented anywhere in this output.

## 3. Pinterest same-query pilot

- **Attempted:** all 10 authoritative queries, unchanged.
- **Returned results:** 9 of 10 (44 candidates total).
- **Usable (relevant on inspection):** 31 of 44 candidates, across 8 of 10 queries.
- **Zero-result query:** `gift box` — reproducible literal-phrase quirk (the plural "gift boxes" worked normally in the same session), not a login/rate-limit block.
- **Key technical limitation:** outbound/original source URL could not be extracted for **any** of the 44 candidates (Pinterest only resolves it via a click action, not present in static page data) — confirmed by direct inspection of one pin's DOM and embedded JSON. Per-pin tags were similarly not exposed in the search grid. Both gaps are recorded as explicit limitations, not guessed.
- Thumbnails: 44 real Pinterest CDN images (`i.pinimg.com`, public, no auth) downloaded to `thumbnails/pinterest/`.

## 4. Google vs. Pinterest

Pinterest is **not a drop-in replacement** for the Google/Behance pilot: it never matched the
100% outbound-URL and source-attribution completeness of the Google set, and its usable-candidate
rate swung from 0/5 to 5/5 depending on query, with several queries (`certificate`,
`influencer post`) returning mostly untitled, unattributable results. It **does** add real
supplemental value on a few queries (`sticker`, `business card`, `coffee package`, `flashcard`)
where it surfaced a genuinely different visual style — retail product photos and free-printable
aesthetics — not present in the Behance-heavy Google set. Conclusion is evidence-based per query;
full breakdown in `google_vs_pinterest_comparison.csv` and `FINDINGS.md`.

## 5. Product implication

The mapping/data preparation in this task is now ready to inform the later production
integration where approved inspiration records could be surfaced through Search, Creative
Exploration, Inspiration Hub, and Topic Pages. **No frontend code was changed in this task** —
this is data prep only.

## 6. Workflow direction

Per meeting clarification only: workflow data has two product destinations —
`/resources` → case studies, and vertical-specific workflows → reusable workflow patterns. (The
five-domain workflow study itself was not redone here.) Lovart was also mentioned as a possible
future design-inspiration source to evaluate later — no crawl was performed.

## 7. Next step

Get product confirmation on the 4 `needs_product_confirmation` mappings and a decision on the 3
missing topics (`figure`, `business card`, `certificate`) — this blocks any production surfacing
regardless of source. Hold off on a broader Pinterest re-collection; if a `business card` topic
is created, that's the one query worth revisiting on Pinterest specifically, since it had the
strongest showing (5/5 usable, incl. a real editorial design roundup).
