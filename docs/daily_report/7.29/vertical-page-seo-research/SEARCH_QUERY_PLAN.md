# Search Query Plan — Vertical Page SEO Research

**Date:** 2026-07-29
**Purpose:** query set for manually researching top-ranking competitor/reference pages across the 4
vertical categories, to inform `VerticalPageSchema` design (see `docs/vertical-page-schema-v1.md`
and `CURRENT_CURIFY_PAGE_AUDIT.md` in this folder).

**How to use this plan:** run each query in Google (incognito/logged-out, to avoid personalization
skew), record the top-ranking organic results (not ads, not the "People also ask" box) in
`TOP_PAGE_INPUT_TEMPLATE.csv`, and analyze the selected pages using `RESEARCH_RUBRIC.md`. Rank
numbers must be recorded from an actual manual search — nothing in this plan or the CSV template
should be read as an existing ranking claim.

Each category has 6 queries chosen to span distinct user intents: **template**, **generator**,
**guide**, **examples**, **printable / platform-specific**, and **commercial use**. This mix matters
because Curify's own pages currently serve template + generator + example intent only (see
`CURRENT_CURIFY_PAGE_AUDIT.md` §2–3) — the guide/printable/commercial-use intents are where the
Knowledge (Pillar 1) and licensing-trust gaps are most likely to surface.

---

## 1. MBTI

Reference sites named in the design doc: 16Personalities, Truity (+ Personality Junkie for depth).

| # | Query | Intent |
|---|---|---|
| 1 | `INFJ personality type poster template` | template |
| 2 | `MBTI character card generator` | generator |
| 3 | `16 personalities types guide` | guide |
| 4 | `MBTI personality poster examples` | examples |
| 5 | `printable MBTI type chart` | printable |
| 6 | `MBTI compatibility chart Pinterest` | platform-specific |

---

## 2. Education

Reference sites named in the design doc: Teachers Pay Teachers, Twinkl (+ K5 Learning).

| # | Query | Intent |
|---|---|---|
| 1 | `HSK reading worksheet template` | template |
| 2 | `vocabulary flashcard generator` | generator |
| 3 | `phonics worksheet guide for teachers` | guide |
| 4 | `classroom worksheet examples elementary` | examples |
| 5 | `printable phonics worksheet` | printable |
| 6 | `Teachers Pay Teachers commercial use license worksheet` | commercial use |

---

## 3. Creative Merch (文创)

Reference sites named in the design doc: Printify knowledge hub, PrintKK / Prodigi.

| # | Query | Intent |
|---|---|---|
| 1 | `fridge magnet design template` | template |
| 2 | `sticker mockup generator` | generator |
| 3 | `print on demand file prep guide` | guide |
| 4 | `Etsy sticker pack mockup examples` | examples / platform-specific |
| 5 | `printable gift box template` | printable |
| 6 | `print on demand commercial use license` | commercial use |

---

## 4. Ecommerce Content

Reference sites named in the design doc: TheGood, BrandJump (Amazon A+ patterns). **No schema exists
in code for this vertical yet** (see `CURRENT_CURIFY_PAGE_AUDIT.md` §4) — treat this category's
research as informing a from-scratch schema, not validating an existing one.

| # | Query | Intent |
|---|---|---|
| 1 | `Amazon product photo template` | template |
| 2 | `product mockup generator ecommerce` | generator |
| 3 | `Amazon A+ content image guide` | guide |
| 4 | `product listing photo examples` | examples |
| 5 | `Shopify product image size guide` | platform-specific |
| 6 | `product photography commercial use license` | commercial use |

---

## Notes on running the searches

- Use an incognito/private window and a fresh/no-history browser profile where possible, to reduce
  personalized-ranking skew.
- Record the **organic** result position only — skip paid ads, shopping carousels, and the "People
  also ask" / "People also search for" boxes when assigning `rank_observed`.
- If a query returns near-identical top results to another query in the same category (e.g. two
  queries both surfacing the same 16Personalities hub page), that's a useful signal on its own —
  note it in `manual_notes` in the CSV rather than forcing a different pick.
- No login, no form submission, no bypassing of paywalls/anti-bot measures — if a top result is
  gated, note that in `manual_notes` and move to the next organic result instead.
