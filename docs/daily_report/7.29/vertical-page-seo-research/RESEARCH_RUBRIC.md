# Research Rubric — Vertical Page SEO Competitor Analysis

**Date:** 2026-07-29
**Purpose:** a single, consistent checklist for analyzing each competitor/reference page selected
via `SEARCH_QUERY_PLAN.md`, so findings across MBTI / Education / Creative Merch / Ecommerce Content
are directly comparable and map cleanly onto `VerticalPageSchema` (Pillars 1–4, see
`docs/vertical-page-schema-v1.md`) and the gaps identified in `CURRENT_CURIFY_PAGE_AUDIT.md`.

**How to use:** for every page recorded in `TOP_PAGE_INPUT_TEMPLATE.csv`, fill out one copy of this
rubric (as a row in a spreadsheet, a per-page markdown block, or however the research is compiled).
Every "rank observed" value must come from a real, manually-run search — this rubric does not
authorize inferring or assuming ranking.

---

## A. Identification

| Field | What to record |
|---|---|
| Google query | The exact query string used (must match one row in `SEARCH_QUERY_PLAN.md`) |
| Rank observed | Organic position (1, 2, 3…) at the time of the manual search. Record the date/time of the search alongside it if possible — rankings move. **User-confirmed only.** |
| Page type | One of: template library / single template detail / generator tool / blog guide / gallery-of-examples / hub-landing / product-category page / other (specify) |

## B. On-page SEO structure

| Field | What to record |
|---|---|
| SEO title | The literal `<title>` tag text (view source or SERP snippet) |
| Meta description | The literal meta description (view source or SERP snippet) |
| H1/H2 structure | List the H1 and each H2 in order, verbatim or close paraphrase — this reveals the page's information architecture |
| Hero section | What sits above the fold: headline + subhead pattern, hero image/video, primary CTA, any trust badges |

## C. Core content modules

| Field | What to record |
|---|---|
| Template/example gallery | Is there a grid of templates/examples? Card count, whether cards show a title/tag/preview, whether clicking opens a detail page or a lightbox |
| Educational or professional content | Depth and format of authoritative prose: is it a paragraph, a structured explainer, a multi-section article? Who is it written for (beginner/practitioner)? |
| Use cases | Are specific use cases/audiences called out (e.g. "for teachers", "for gift shops")? How are they presented — list, chips, separate sections? |
| How-to section | Is there a step-by-step "how to use this" or "how to make one" block? Numbered steps, video, or prose? |
| FAQ | Presence/absence, number of questions, whether it appears to target long-tail queries (compare question phrasing to the query list) |
| CTA | What is the primary conversion action (generate / download / buy / sign up / add to cart)? How many CTAs, and where placed? |

## D. Site architecture signals

| Field | What to record |
|---|---|
| Internal links | Roughly how many contextual internal links on the page, and where they point (related templates? category hub? blog?) |
| Related content | Is there a "related"/"you might also like"/"similar" module? How is relatedness determined (visually obvious pattern — same category, same author, same tag)? |
| Structured data / JSON-LD | View source and look for `<script type="application/ld+json">`; record the `@type`(s) present (e.g. `Product`, `Article`, `LearningResource`, `FAQPage`, `BreadcrumbList`, `HowTo`, `AggregateRating`) |
| Trust signals | Ratings/reviews, usage counts ("10,000+ downloads"), author/expert bylines, verification badges, testimonials, "as seen in" logos |

## E. Category-specific differentiators

| Field | What to record |
|---|---|
| Unique category-specific modules | Anything that doesn't fit the generic modules above and appears specific to this vertical — e.g. a compatibility matrix (MBTI), a grade-level filter (Education), a material/DPI spec sheet (Merch), a platform size-chart (Ecommerce). This is often the most valuable field — it's what a generic template site (including Curify today) is missing. |

## F. Assessment

| Field | What to record |
|---|---|
| Strengths | What this page does well that likely helps it rank/convert — be specific (e.g. "FAQ answers 8 long-tail questions matching PAA box", not "good content") |
| Weaknesses | What's thin, outdated, cluttered, or a poor user experience |
| Ideas applicable to Curify | Concrete, scoped suggestions — phrase each as "add X to [template page / example page]" so it can be checked against `CURRENT_CURIFY_PAGE_AUDIT.md`'s gap list and the relevant `VerticalPageSchema` attribute/knowledge-slot definitions in `lib/vertical_schema.ts`. Flag whether the idea maps to Pillar 1 (Knowledge), Pillar 2 (Attributes/ontology), or is a page-layout/UX idea outside the 4-pillar model. |

---

## Column-to-CSV mapping

`TOP_PAGE_INPUT_TEMPLATE.csv` captures only the page-selection metadata (query, rank, URL, why this
page was picked). The full A–F rubric above is the next step, applied to each page recorded in that
CSV — record the detailed rubric findings in a separate per-page notes file or an extended
spreadsheet, referencing the CSV row (category + search_query + url) as the join key.

## Rules carried over from the task brief

- Do not classify a page as "Google's top result" unless a human has actually run the search and
  observed the rank. This rubric's `rank_observed` field exists specifically to keep that fact
  explicit and separately tracked from `selected_reason`.
- No login, no form submission, no bypassing anti-bot/paywall measures to view a page. If a page
  requires that, note it under `manual_notes` in the CSV and select the next organic result instead.
