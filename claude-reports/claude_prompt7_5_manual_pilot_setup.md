# Prompt 7.5 — Manual Pilot Setup: Bing Images & Pinterest External Signals

**Date:** 2026-06-19  
**Branch:** baobao/multi-intent-topic-cooccurrence  
**Phase:** V0 5-query manual pilot — research artifacts only, no production code modified.

---

## 1. Corrected Bing Access Conclusion

**Bing Image Search API v7 is retired and unavailable.**

Microsoft retired all Bing Search APIs (Image Search v7, Web Search v7, Autosuggest v7) on **August 11, 2025**. All endpoints under `https://api.bing.microsoft.com/v7.0/` return errors. This invalidates the entire API-based collection path described in Prompt 7:

| Prompt 7 plan item | Corrected status |
|---|---|
| Obtain free-tier Bing Search API key | **Do not do this — key has no valid endpoint** |
| Create `BING_SEARCH_API_KEY` env variable | **Do not create** |
| Create `scripts/collect_bing_signals.cjs` | **Do not create** |
| `relatedSearches[]` from API | **Not available** |
| `pivotSuggestions[]` from API | **Not available** |
| Free-tier 1,000 calls/month | **No longer applicable** |

**Replacement for V0:** Manual browser observation of the Bing Images UI, which still exposes:
- Autocomplete dropdown (type query in search bar, observe before submitting)
- Refinement chips at the top of the image results page
- "Related searches" row at the bottom of the page
- Entity/category panels alongside results

The signals are the same; only the collection path changes from API to manual.

**Microsoft Search alternative:** Microsoft Grounding with Bing Search (part of Azure AI Foundry) is a distinct product from the retired Bing Search API — it powers LLM grounding, not image refinement-chip collection. It is not a replacement for the retired Image Search API's `relatedSearches[]` or `pivotSuggestions[]` fields.

---

## 2. Corrected Pinterest Access Conclusion

**Pinterest observation remains manual only. No change to the method, only to the API description.**

The Prompt 7 plan correctly ruled out a Pinterest API and chose manual observation. However, the wording was slightly imprecise. Corrected state:

| Access method | Status |
|---|---|
| Pinterest API v5 (public) | Does not support general query → pins search or refinement signals |
| Pinterest beta partner keyword search | Exists in beta; requires partner program admission; project does not have access |
| Playwright/Puppeteer automation | Explicitly rejected (bot-detection, ToS, fragility) |
| Commercial SERP tools (Bright Data, etc.) | Not approved or budgeted |
| Manual browser observation | **Approved method** — consistent with how `pinterest-discovery-2026-05-29` eval queries were collected |

Manual observation in private/incognito browsing collects: autocomplete suggestions, refinement bubbles, board labels, dominant visual themes. No login is required for most queries.

---

## 3. Files Created

```
data/external_signals/
  README.md                         ← why Bing API is not used; why Pinterest is manual; pilot scope; expansion path
  v0_query_set.json                 ← 5 pilot queries with metadata, Curify baseline, repository evidence
  v0_observations.json              ← normalized schema records (pending_manual_capture; no fabricated data)
  v0_manual_collection_template.md  ← step-by-step beginner-friendly observer instructions
  bing_manual/
    .gitkeep                        ← placeholder; screenshots and notes go here after capture
  pinterest_manual/
    .gitkeep                        ← placeholder; screenshots and notes go here after capture
```

**No existing files modified.** All Prompt 2–6.5 work is intact.

---

## 4. Five-Query Pilot Design

### Selected queries and rationale

| # | Query | Category | Curify status | Why included |
|---|---|---|---|---|
| 1 | `cat` | Broad entity | 33 hits — rich | Validates schema handles high-suggestion-volume queries; many sub-intents expected |
| 2 | `paris` | Place | 35 hits — rich | Canonical multi-intent place query; the parent of the sparse itinerary query |
| 3 | `science poster` | Learning / Reference | 221 hits — rich | Highest-hit query in the set; tests schema with ultra-rich Curify content |
| 4 | `paris travel itinerary` | Travel / Sparse | 2 hits — thin — WARN | Primary gap target; external demand likely high; Curify content confirmed sparse |
| 5 | `warmup routine running checklist` | DIY / Guide / Sparse | 1 hit — thin — WARN | Second gap target; single template match; diy-guides cluster nearly empty for this query |

### What the pilot validates

1. **Schema fitness** — does the `ExternalSignalRecord` schema accommodate all signal types actually observed (vs. hypothetically)?
2. **Signal type vocabulary completeness** — does `signal_type` cover what Bing and Pinterest actually show, or are new values needed?
3. **Cluster mapping friction** — how often is `unmapped` necessary vs. how easily do suggestions map to the 8 clusters?
4. **Observer time** — is 10–15 minutes per query accurate, or does it need adjustment?
5. **Gap signal quality** — for the two WARN queries (`paris travel itinerary`, `warmup routine running checklist`), do external platforms confirm strong demand that Curify cannot currently satisfy?

---

## 5. Curify Baseline Results

Collected automatically using `node scripts/score_user_queries.cjs` on 2026-06-19.

| Query | Strict hits | Eval bucket | Eval status | Top templates |
|---|---|---|---|---|
| `cat` | 33 | rich | not in eval set | lunar-new-year-red-envelope-set ×8, pet-life-journey-infographic ×6, disney-character-color-grid-art ×5, pet-care-guide ×4 |
| `paris` | 35 | rich | not in eval set | city-miniature ×15, tourist-spot-watercolor-map-infographic ×6, global-city-walkability-infographic-card ×6, city-mbti ×5 |
| `science poster` | 221 | rich | not in eval set | herbal ×77, food ×40, weird-cold-knowledge-popular-science-card ×15, figure-principles-infographic ×11 |
| `paris travel itinerary` | 2* | thin | **WARN** (expected: rich) | tourist-spot-watercolor-map-infographic ×1, city-miniature ×1 |
| `warmup routine running checklist` | 1 | thin | **WARN** (expected: rich) | warmup-routine ×1 |

*Note on `paris travel itinerary` discrepancy: `score_user_queries.cjs` returns 7 hits (moderate bucket) while the eval pipeline records 2 hits (thin). The discrepancy reflects the full strict-AND + relaxed + deduplication in the eval pipeline vs. the raw alias scorer.

### Curify intent chips — status

Intent chip output requires browser verification (the cluster co-occurrence implementation in `lib/intent_clusters.ts` is not yet browser-verified after the 2026-06-18 daily-report update). Expected behavior based on the implementation:

| Query | Expected cluster chips | Fallback risk |
|---|---|---|
| `cat` | storytelling-identity, social-personal, diy-guides | Unlikely — 33 results, many topics |
| `paris` | travel-place, visual-art, storytelling-identity | Unlikely — 35 results |
| `science poster` | learning-materials, visual-art | Unlikely — 221 results |
| `paris travel itinerary` | travel-place only OR fallback | **Likely fallback** — 2 results insufficient for minCount threshold |
| `warmup routine running checklist` | none OR fallback | **Certain fallback** — 1 result; no co-occurrence possible |

Record actual chips during browser verification in Step 1 of the collection template.

---

## 6. Exact Manual Capture Workflow

The complete step-by-step instructions are in `data/external_signals/v0_manual_collection_template.md`. Summary:

### For each query:

**Step 1 — Curify baseline (~3 min)**
- `npm run dev` → open `http://localhost:3000/en/search?q={query}`
- Record: result count, visible cluster chips and their order, rewrite banner text
- Update `curify_baseline` fields in `v0_observations.json`

**Step 2 — Bing Images (~5 min)**
- Open new private/incognito window
- Go to `https://www.bing.com/images`
- Type query slowly → record autocomplete dropdown → screenshot `bing_<slug>_autocomplete_<date>.png`
- Submit → record refinement chips at top (label, position) → screenshot `bing_<slug>_<date>.png`
- Scroll to bottom → record related searches row
- Record entity/category panels and visual category clusters if visible
- Write freeform notes to `data/external_signals/bing_manual/<query_slug>_notes.txt`

**Step 3 — Pinterest (~5 min)**
- Open new private/incognito window
- Go to `https://www.pinterest.com`
- Type query slowly → record autocomplete suggestions
- Submit → check for login wall (record if present) → record refinement bubbles (label, position) → screenshot `pinterest_<slug>_<date>.png`
- Record visible board labels
- Write 1–3 sentences describing dominant visual themes of top ~20 pins
- Write freeform notes to `data/external_signals/pinterest_manual/<query_slug>_notes.txt`

**Step 4 — Fill schema (~3 min)**
- Open `v0_observations.json`
- Update `status`, `captured_at`, arrays, and `suggestions[]` from notes
- Use controlled vocabulary for `signal_type` and `curify_cluster`
- Mark absent signals as `"not_visible"`, not empty arrays

**Step 5 — Evidence check (optional, run after session)**
```bash
node scripts/score_user_queries.cjs "{suggestion_query}"
```
Paste output into the `evidence` field of each suggestion.

---

## 7. Empty/Pending Fields Requiring Human Browser Observation

All of the following fields in `v0_observations.json` are currently `"pending_manual_capture"` or empty arrays. They require the human observer to complete the browser session:

### Bing Images (all 5 queries)
- `captured_at` — set after capture
- `autocomplete` — manual type-and-observe
- `refinement_chips` — visible after search submission
- `related_searches` — visible at bottom of results page
- `entity_labels` — visible if Bing shows a knowledge panel
- `visual_categories` — visible if Bing groups results into labeled clusters
- `suggestions[]` — populated from all of the above

### Pinterest (all 5 queries)
- `captured_at` — set after capture
- `login_required` — check on first load
- `autocomplete` — manual type-and-observe
- `refinement_bubbles` — horizontal chip row below search bar
- `board_labels_visible` — scan top 20 pins
- `dominant_visual_themes` — 1–3 sentence description
- `suggestions[]` — populated from bubbles and autocomplete

### Curify baseline (all 5 queries)
- `intent_chips_visible` — verify at `http://localhost:3000/en/search?q={query}`
- `rewrite_banner_visible` — check if "We also searched for…" banner appears

---

## 8. Recommended Collection Order

Collect in this order to maximize learning from the pilot:

| Order | Query | Why this order |
|---|---|---|
| **1st** | `cat` | Warmup — rich Curify content, broad external signals expected. Use this query to calibrate the manual workflow and screenshot conventions before tackling harder queries. |
| **2nd** | `science poster` | Second warmup — another rich query with clear subject framing. Validates how the schema handles format-explicit queries and audience refinements. |
| **3rd** | `paris` | First ambiguous multi-intent place query. At this point the workflow is calibrated; this query's rich external signal will reveal how well the schema captures intent diversity. |
| **4th** | `paris travel itinerary` | First sparse gap query. Immediately follow `paris` so the context is fresh. The contrast between `paris` (rich signals) and `paris travel itinerary` (sparse Curify, expected rich external demand) is the key finding. |
| **5th** | `warmup routine running checklist` | Second sparse gap query. The most extreme case (1 result, zero template match). Collect last so you're experienced with the workflow and can give full attention to the signals. |

**Target time budget:** ~70 minutes total (14 min × 5 queries). A single browser session, no breaks needed.

---

## 9. `git status --short`

```
 M app/[locale]/(public)/search/SearchResultsClient.tsx
 M app/[locale]/(public)/search/page.tsx
 M lib/__tests__/intent_clusters.test.ts
 M lib/intent_clusters.ts
 M messages/en/nano.json
 M public/data/nano_inspiration.json
?? claude_prompt4_5_result.md
?? claude_prompt4_6_redirect_fix_result.md
?? claude_prompt5_warn_audit_result.md
?? claude_prompt6_5_paris_topic_review.md
?? claude_prompt6_safe_warn_fixes_result.md
?? claude_prompt7_5_manual_pilot_setup.md
?? claude_prompt7_external_signal_research_plan.md
?? data/
?? docs/daily_report/
?? lib/__tests__/query_normalize.test.ts
?? lib/__tests__/search_business_override.test.ts
?? lib/__tests__/search_metadata_scenarios.test.ts
?? lib/intent_taxonomy.ts
?? lib/query_normalize.ts
?? lib/search_business_override.ts
```

---

## 10. `git diff --stat`

```
 app/[locale]/(public)/search/SearchResultsClient.tsx | 133 ++++---
 app/[locale]/(public)/search/page.tsx               | 125 +++++--
 lib/__tests__/intent_clusters.test.ts               | 399 +++++++++++++++++++++
 lib/intent_clusters.ts                              | 149 +++++++-
 messages/en/nano.json                               |   4 +-
 public/data/nano_inspiration.json                   | 197 +++++++---
 6 files changed, 878 insertions(+), 129 deletions(-)
```

All changes in the diff are from Prompts 2–6.5 (multi-intent search implementation and metadata fixes). This prompt added only untracked files (`data/external_signals/`, `claude_prompt7_5_manual_pilot_setup.md`). No tracked files were modified.
