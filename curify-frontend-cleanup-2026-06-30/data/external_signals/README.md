# External Signal Research — V0 Manual Pilot

**Created:** 2026-06-19  
**Branch:** baobao/multi-intent-topic-cooccurrence  
**Phase:** V0 — 5-query manual pilot (schema validation + workflow dry-run)

---

## Purpose

This directory stores observations of how Bing Images and Pinterest expose sub-intent signals
alongside their search results — specifically:
- related searches
- refinement chips / bubbles
- autocomplete suggestions
- entity/category labels

These observations are used to validate and calibrate Curify's 8-cluster intent taxonomy
against external demand signals. They are research artifacts only. No production code is
modified based on this data without a separate implementation prompt.

---

## Why the Bing Image Search API is NOT used

Microsoft officially **retired Bing Search APIs** (including Bing Image Search API v7,
Bing Autosuggest, and Bing Web Search API) on **August 11, 2025**. All endpoints under
`https://api.bing.microsoft.com/v7.0/` are no longer available.

Therefore:
- No `BING_SEARCH_API_KEY` environment variable is used or should be created.
- No script calls the retired Bing API endpoints.
- `relatedSearches[]`, `pivotSuggestions[]`, and Autosuggest API responses referenced in
  the old plan (Prompt 7) are no longer available.
- Bing Images signals are collected by **manual browser observation only**.

---

## Why Pinterest uses manual observation only

Pinterest's official API v5 does not expose general search (query → pins), refinement
bubbles, autocomplete suggestions, or related-search signals to third parties. A beta
partner keyword search endpoint exists but requires partner program access, which this
project does not have.

Automated scraping (Playwright, Puppeteer, headless browsers) against pinterest.com is
rejected because:
- Pinterest has aggressive bot-detection (captcha, rate-limit, IP block).
- It violates Pinterest's ToS under web crawling restrictions.
- The repository's benchmark doc explicitly ruled it out.

Pinterest signals are collected by **manual browser observation only**.

---

## V0 pilot scope — 5 queries

| # | Query | Rationale |
|---|---|---|
| 1 | `cat` | Broad entity; validates schema for rich multi-intent queries |
| 2 | `paris` | Place query; ambiguous between poster/map/itinerary/scrapbook |
| 3 | `science poster` | Learning/Reference; rich Curify content (221 hits) |
| 4 | `paris travel itinerary` | Known sparse — WARN in eval (thin, 2 results); high external demand expected |
| 5 | `warmup routine running checklist` | Known sparse — WARN in eval (thin, 1 result); diy-guides cluster |

The goal of the 5-query pilot is to:
1. Validate the `ExternalSignalRecord` schema handles real observations.
2. Identify any schema gaps before scaling to 20 queries.
3. Establish the manual workflow for one observer.
4. Produce the first real gap analysis on the two sparse queries.

---

## Directory layout

```
data/external_signals/
  README.md                         ← this file
  v0_query_set.json                 ← 5 pilot queries with metadata
  v0_observations.json              ← normalized schema records (fill after manual capture)
  v0_manual_collection_template.md  ← step-by-step instructions for one observer
  bing_manual/                      ← screenshots and raw notes from Bing Images
    <query_slug>_<date>.png         ← screenshot naming convention
    <query_slug>_notes.txt          ← freeform capture notes (input to schema)
  pinterest_manual/                 ← screenshots and raw notes from Pinterest
    <query_slug>_<date>.png
    <query_slug>_notes.txt
```

---

## File roles

| File | Role | Filled by |
|---|---|---|
| `v0_query_set.json` | Stable query metadata | Human / Claude (already populated) |
| `v0_observations.json` | Normalized schema records | Human fills from `bing_manual/` + `pinterest_manual/` notes |
| `v0_manual_collection_template.md` | Step-by-step observer instructions | Claude (already written) |
| `bing_manual/*.png` | Bing screenshots | Human captures during manual session |
| `bing_manual/*_notes.txt` | Raw Bing capture notes | Human writes during/after session |
| `pinterest_manual/*.png` | Pinterest screenshots | Human captures during manual session |
| `pinterest_manual/*_notes.txt` | Raw Pinterest capture notes | Human writes during/after session |

---

## How to expand to 20 queries after V0

1. Review `v0_observations.json` — confirm the schema accommodates all signal types encountered.
2. Review `v0_manual_collection_template.md` — update any steps that were unclear.
3. Extend `v0_query_set.json` with the remaining 15 queries from the full 20-query set in
   `claude_prompt7_external_signal_research_plan.md`.
4. Repeat the manual capture workflow for the additional 15 queries.
5. Merge into a `v1_observations.json` covering all 20 queries.
6. Run `node scripts/score_suggestion.cjs "<suggestion>"` for each captured suggestion to
   populate the `evidence` field programmatically.
