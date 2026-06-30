# Prompt 7 — External Signal Research Plan: Bing Images & Pinterest Sub-Intent Discovery

**Date:** 2026-06-19  
**Branch:** baobao/multi-intent-topic-cooccurrence  
**Phase:** Research & data-collection design only — no production code modified.

---

## Section 1 — Existing Repository Decisions & Constraints

### What has already been decided (confirmed from repository documentation)

#### Pinterest

| Decision | Source |
|---|---|
| Do NOT build a Pinterest API integration or scraper | `docs/eval-framework-visual-search-benchmark-2026-06-14.md` — "Out of scope (deliberately)" |
| Pinterest's Search API is essentially closed to the public | Same doc — "Search API — essentially closed to the public; Content Discovery API — heavily rate-limited, narrow scope" |
| Manual screenshot is the preferred data-collection method for Pinterest | Same doc — "For a few dozen queries, **manual screenshot** of Pinterest's own search page is more honest and cheaper" |
| Pinterest is an upstream demand signal, NOT a competitor to replicate | Same doc — "Pinterest = human-curated visual demand; Curify = AI-generated visual supply" |
| Pinterest data has already been used as an eval source (manual) | `scripts/configs/search_eval_set.json` — 8 queries with `source: "pinterest-discovery-2026-05-29"` |
| Playwright/browser automation against pinterest.com is explicitly rejected | Benchmark doc — "Pinterest has aggressive bot-detection — captcha, rate-limit, IP block" |

#### Bing Images

| Decision | Source |
|---|---|
| Bing Images is one of 5 comparison surfaces in the planned eval | `docs/eval-framework-visual-search-benchmark-2026-06-14.md` — table includes "Bing Images — Manual screenshot — top 20 results" |
| Collection method defined as manual screenshot (not API) | Same doc |
| Eval execution deferred to post-WC strategic window (post 2026-07-19) | Both eval framework docs |
| Bing Image API integration research was explicitly queued as next step | `docs/daily_report/2026-06-18.md` — item 5: "Bing Image API and Pinterest results acquisition research" |
| No Bing Search API key is currently configured | `.env.local` — only Azure Blob Storage key; `package.json` — only `@azure/storage-blob` (no Bing Search SDK) |

#### External demand signals generally

| Decision | Source |
|---|---|
| External demand signals currently come from: SEARCH_NORESULT logs, GSC Pages.csv, Reddit hot_topics.json snapshot | `docs/search-and-content.md` Thread d |
| Reddit adapter has no live crawler — it re-runs LLM against a static snapshot | Thread d open item 5 |
| GSC adapter not yet implemented | Thread d open item 2 |
| Bing/Pinterest are positioned as *benchmark surfaces* for eval, NOT as content-production signal sources | `eval-framework-visual-search-benchmark-2026-06-14.md` |

#### What has NOT yet been implemented

1. No Bing Images API integration exists anywhere in the repo.
2. No Pinterest integration (API or scraper) exists or is planned.
3. The 100-query, 5-surface visual search benchmark has NOT been executed (filed 2026-06-14, deferred to post-WC).
4. The VIRB (Visual Intent Routing Benchmark) has NOT been executed (filed 2026-06-15, deferred to post-WC).
5. Sub-intent refinement signal comparison (Bing suggestions / Pinterest refinement bubbles mapped to Curify clusters) has not been studied.
6. No external demand-signal schema exists for recording Bing or Pinterest observations.

#### How this prompt differs from existing work

The existing benchmark doc (`eval-framework-visual-search-benchmark-2026-06-14.md`) focuses on **visual search quality** — comparing Curify, Pinterest, Bing, Google Images, Canva on Relevance / Diversity / Actionability of top-20 image results.

This prompt's scope is narrower and complementary: focus specifically on **sub-intent refinement signals** — the related searches, refinement chips, suggested queries, and visual exploration paths that Bing Images and Pinterest expose *alongside* their results. These signals reveal latent user goals that Curify's current intent taxonomy can be validated against.

---

## Section 2 — Proposed External Signal Schema

### Record-level schema

```json
{
  "query": "cat",
  "source": "bing_images",
  "captured_at": "2026-06-20T10:30:00Z",
  "locale": "en-US",
  "surface": "bing_images_related_searches",
  "suggestions": [
    {
      "label": "cat breeds",
      "search_query": "cat breeds",
      "position": 1,
      "signal_type": "related_search",
      "normalized_intent": "visual reference for cat breeds",
      "curify_cluster": "learning-materials",
      "evidence": "cat breeds returns 47 results; template-dog-breed-retro-infographic family has direct cat equivalent",
      "notes": "strong Curify match; likely maps to species-profile infographic shape"
    }
  ]
}
```

### `source` values

| Value | Meaning |
|---|---|
| `bing_images` | Bing Images search result page |
| `pinterest` | Pinterest search result page |

### `surface` values (where on the page the signal was observed)

| Value | Meaning |
|---|---|
| `bing_images_related_searches` | "Related searches" row below Bing Images results |
| `bing_images_pivot_suggestions` | Pivot/filter row at top of Bing Images results |
| `bing_images_entity_panel` | Knowledge panel entity labels |
| `bing_images_collection_tags` | Image collection/category labels in results |
| `bing_api_relatedsearches` | From `relatedSearches[]` field in Bing Image Search API response |
| `bing_api_pivotsuggestions` | From `pivotSuggestions[]` field in Bing Image Search API response |
| `bing_api_imagetags` | From `imageInsightToken` / tag data in Bing Image Search API response |
| `pinterest_refinement_bubbles` | Horizontal refinement chips/bubbles below the Pinterest search bar |
| `pinterest_autocomplete` | Pinterest search autocomplete dropdown suggestions |
| `pinterest_board_labels` | Board names that appear as context around top pins |
| `pinterest_topic_labels` | Topic/category labels on result clusters |

### `signal_type` vocabulary (controlled)

| Value | Definition | Example |
|---|---|---|
| `related_search` | A fully-formed alternative query suggested by the platform | "cat breeds" when searching "cat" |
| `refinement_chip` | A filter chip that narrows the current query (additive modifier) | "cute" · "outdoor" · "black" chips on Bing for "cat" |
| `autocomplete` | A query completion suggestion shown before search is submitted | "cat breeds chart" from Pinterest autocomplete |
| `visual_category` | A visual cluster label grouping a set of results by theme | "Siamese" · "Maine Coon" image clusters on Bing |
| `entity_refinement` | A named entity (person/place/thing) Bing identifies in the query domain | "Ragdoll" · "Persian" breed panel on Bing |
| `style_refinement` | A visual style modifier (aesthetic, art style, color, rendering style) | "watercolor" · "cartoon" · "realistic" |
| `format_refinement` | A content format or layout modifier | "infographic" · "poster" · "chart" · "printable" |
| `audience_refinement` | A target audience modifier | "kids" · "classroom" · "beginner" |
| `occasion_refinement` | A time, event, or occasion modifier | "birthday" · "Christmas" · "wedding" |
| `task_refinement` | A task or action modifier | "printable" · "template" · "DIY" · "how to" |
| `unknown` | Signal type cannot be reliably classified | Ambiguous Pinterest bubble |

### `curify_cluster` values (Curify's 8 existing clusters only)

| Value | Label |
|---|---|
| `learning-materials` | Learning Materials |
| `visual-art` | Visual & Art |
| `merch-commerce` | Merch & Commerce |
| `social-personal` | Social & Personal |
| `storytelling-identity` | Storytelling & Identity |
| `travel-place` | Travel & Place |
| `events-hot-now` | Events & Hot Now |
| `diy-guides` | DIY & Guides |
| `unmapped` | Does not fit any existing cluster |

**Rule:** A suggestion maps to `unmapped` when no existing cluster's topic set clearly covers it. `unmapped` suggestions are documented but do not trigger any taxonomy change in this phase.

### Full schema (TypeScript type definition for reference)

```typescript
type SignalType =
  | "related_search" | "refinement_chip" | "autocomplete"
  | "visual_category" | "entity_refinement" | "style_refinement"
  | "format_refinement" | "audience_refinement" | "occasion_refinement"
  | "task_refinement" | "unknown";

type CurifyCluster =
  | "learning-materials" | "visual-art" | "merch-commerce"
  | "social-personal" | "storytelling-identity" | "travel-place"
  | "events-hot-now" | "diy-guides" | "unmapped";

type Suggestion = {
  label: string;
  search_query: string;
  position: number;
  signal_type: SignalType;
  normalized_intent: string;       // brief plain-english intent statement
  curify_cluster: CurifyCluster;
  evidence: string;                // Curify data supporting or contradicting this cluster
  notes: string;                   // observer's comment; gaps, risks, opportunities
};

type ExternalSignalRecord = {
  query: string;
  source: "bing_images" | "pinterest";
  captured_at: string;             // ISO 8601
  locale: string;                  // e.g. "en-US"
  surface: string;                 // from surface vocabulary above
  suggestions: Suggestion[];
};
```

---

## Section 3 — Selected 20-Query Research Set

Each query is grounded in repository content (eval set, templates, inspirations, or known gaps).

| # | Query | Category | Why included | Curify status |
|---|---|---|---|---|
| 1 | `cat` | Broad entity | Classic single-noun entity; broad enough to surface many sub-intents; present as a real Curify test case | Rich — 40+ results |
| 2 | `cat breeds` | Entity refinement | Step from entity → typed sub-entity; in eval set implicitly via "cat"; tests breed-level visual demand | Moderate — breed infographic templates exist |
| 3 | `paris` | Place | Ambiguous place: poster / map / itinerary / scrapbook; the Paris record was reviewed in Prompt 6.5 | Rich — watercolor map, travel poster, landmark records exist |
| 4 | `paris travel itinerary` | Travel / Sparse | Known sparse (WARN: thin, 2 results in eval); tests if Bing/Pinterest show demand signals Curify can't yet satisfy | **Sparse** — explicit WARN in eval |
| 5 | `science poster` | Learning/Reference | Explicit in daily report browser validation (2026-06-18); learning-materials cluster; common query type | Rich |
| 6 | `cat breeds chart` | Learning / Format explicit | Format-explicit query; tests what sub-intents platforms surface when format is stated | Moderate |
| 7 | `vintage stamp collection garden birds` | Visual style / Niche | Explicit in eval set (`prefill-pool-2026-06-14`); known sparse-content query (WARN: thin, 1 result) | **Sparse** — WARN in eval |
| 8 | `childhood snacks then vs now` | Nostalgia / Before-After | Explicit in eval set; known sparse-content query (WARN: thin, 1 result); tests nostalgia sub-intents | **Sparse** — WARN in eval |
| 9 | `warmup routine running checklist` | DIY / Guide | Explicit in eval set; known sparse-content query (WARN: thin, 1 result); tests fitness/guide sub-intents | **Sparse** — WARN in eval |
| 10 | `mbti infj` | Personality / Identity | Eval set query; heavy storytelling-identity cluster; tests personality visual sub-intents | Rich |
| 11 | `world cup 2026` | Events / Trending | Eval set (`world cup 2026 schedule`); heavy events-hot-now cluster; tests sports sub-intents | Rich |
| 12 | `kids english animals vocabulary` | Learning / Audience | Eval set (`kids english animals vocabulary cards`); rich result; tests how platforms refine audience signals | Rich |
| 13 | `watercolor map europe travel` | Visual style / Travel | Eval set (`watercolor travel journal collage`, `watercolor map of europe travel destinations`); tests style × place sub-intents | Moderate |
| 14 | `product packaging mockup` | Commerce / Design | Eval set (`product packaging mockup display`); merch-commerce cluster; tests design/format sub-intents | Rich |
| 15 | `evolution snacks infographic` | Learning / Before-After | Eval set — explicitly validated rich result; then-vs-now shape; tests if platforms surface broader nostalgia or food sub-intents | Rich |
| 16 | `diy home decor ideas` | DIY / Lifestyle | Eval set (`diy home decor ideas`); diy-guides + social-personal overlap; tests domestic content sub-intents | Moderate |
| 17 | `retro 90s aesthetic poster` | Visual style | Eval set (`retro 90s aesthetic poster`); visual-art cluster; tests how style sub-intents are labeled | Moderate (WARN: dropped-quality pool) |
| 18 | `mbti marvel` | Multi-intent / Ambiguous | Eval set (`popular` source); storytelling-identity × learning-materials × events; tests multi-cluster signals | Rich |
| 19 | `brand logo design board` | Commerce / Design | Eval set — rich result; merch-commerce + visual-art overlap; tests commercial design sub-intents | Rich (WARN: dropped-quality pool) |
| 20 | `dubai map travel guide` | Travel / Place | Eval set (`dubai map travel guide`); rich result; tests how place-specific travel sub-intents split (map vs guide vs itinerary) | Rich (WARN: dropped-quality pool) |

### Coverage check

| Category | Queries |
|---|---|
| Broad entities | 1 (cat), 11 (world cup) |
| Places | 3 (paris), 13 (watercolor map europe), 20 (dubai) |
| Learning/Reference | 5 (science poster), 6 (cat breeds chart), 12 (kids english), 15 (evolution snacks) |
| Visual style | 13 (watercolor), 17 (retro 90s), 2 (cat breeds chart) |
| Before/After | 8 (childhood snacks), 15 (evolution snacks) |
| Travel | 3 (paris), 4 (paris itinerary), 13 (watercolor europe), 20 (dubai) |
| Product/Commerce | 14 (product packaging), 19 (brand logo) |
| Personal/Social | 10 (mbti infj), 16 (diy home decor) |
| Events/Trends | 11 (world cup) |
| Multi-intent ambiguous | 18 (mbti marvel), 3 (paris), 2 (cat breeds) |
| Known sparse | 4 (paris itinerary), 7 (vintage stamp birds), 8 (childhood snacks), 9 (warmup routine) |
| Known rich | 1 (cat), 5 (science poster), 10 (mbti infj), 12 (kids english), 14 (product packaging), 15 (evolution snacks), 18 (mbti marvel) |

---

## Section 4 — Bing Images Access Assessment

### Current repository state

**No Bing Images API integration exists anywhere in the repository.**

Confirmed by:
- `package.json`: only `@azure/storage-blob ^12.31.0` — Azure Blob Storage for video processing, not search.
- `.env.local`: only `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_STORAGE_CONTAINER_NAME` — video translate blob storage. No `BING_SUBSCRIPTION_KEY`, `BING_SEARCH_V7_ENDPOINT`, or any Cognitive Services credential.
- Exhaustive grep across `scripts/`, `lib/`, `.env*`: no references to Bing Search API, Cognitive Services, or `@azure/cognitiveservices-imagesearch`.

### Bing Image Search API — what it offers

The **Bing Image Search API v7** (part of Azure Cognitive Services / Microsoft Azure AI Search) exposes:

| Response field | What it contains | Relevant to this task |
|---|---|---|
| `value[]` | Top N image results (URL, thumbnail, dimensions, source domain) | Partial — not the focus |
| `relatedSearches[]` | Array of `{text, displayText, webSearchUrl}` — related query suggestions | **Yes — primary signal** |
| `pivotSuggestions[]` | Per-token pivot alternatives (e.g. for "cat breeds", pivot on "breeds" → dogs, rabbits) | **Yes — refinement signal** |
| `queryExpansions[]` | Expanded / broadened query suggestions | Yes |
| `nextOffsetAddCount` | Pagination metadata | No |
| `totalEstimatedMatches` | Result count estimate | Partial |

**Image-level tags** require a separate call: the **Bing Visual Search API** (not Image Search) returns entity/concept tags on a given image. This is distinct and would require per-image API calls.

**Autocomplete** is a separate Bing Autosuggest API endpoint.

### API cost and rate limits

- Bing Image Search API: Free tier S1 = 1,000 calls/month; paid tiers up to $21/1,000 transactions.
- For 20 queries × ~2 API calls each (one for related searches, one for pivot suggestions) = 40 calls — easily within free tier.
- Bing Autosuggest API: Free tier F0 = 3,000 transactions/month.

### What requires API vs browser observation

| Signal | API available? | Browser observation fallback |
|---|---|---|
| Related searches | Yes (`relatedSearches[]`) | Visual row labeled "Related searches" below results |
| Pivot suggestions | Yes (`pivotSuggestions[]`) | Filter chips at top of results page |
| Autocomplete suggestions | Yes (Autosuggest API, separate endpoint) | Type query in Bing search bar, observe dropdown |
| Image tags/entities | Partial (Visual Search API, per-image) | Entity labels in Bing Knowledge panel |
| Visual category clusters | No direct API field | Observe image groupings on results page |
| "People also search for" entities | Not in Image Search API | Observe sidebar entity cards |

### Assessment

**Without an API key:** Manual browser observation covers the most important signals (related searches, refinement chips, autocomplete). For 20 queries this is 1-2 hours of manual work — fully practical.

**With a Bing Search API key (free tier S1):** The `relatedSearches[]` and `pivotSuggestions[]` fields provide machine-readable, reproducible data. This enables structured extraction into the JSON schema without manual transcription errors. Cost: $0 for ≤1,000 calls/month.

**Recommendation for V0:** Obtain a free-tier Bing Search API key from Azure portal (requires Azure account, no cost for the volume needed). This enables a reproducible, scriptable data-collection path. If key acquisition is blocked, fall back to browser observation.

### Required API endpoint

```
GET https://api.bing.microsoft.com/v7.0/images/search?q={query}&mkt=en-US&count=10&responseFilter=RelatedSearches
Headers: Ocp-Apim-Subscription-Key: {BING_SEARCH_KEY}
```

For pivot suggestions, the same endpoint returns `pivotSuggestions[]` by default.

### Environment variable to add (when key is available)

```
BING_SEARCH_API_KEY=<key-from-azure-portal>
```

Do NOT commit this to version control. Add to `.env.local` only.

---

## Section 5 — Pinterest Access Assessment

### Official Pinterest API

The **Pinterest API v5** (current) supports:
- Reading a user's own boards and pins (OAuth required)
- Creating/updating pins and boards
- Ads management

**It does NOT support:**
- General search: `query → top pins` — not exposed in v5
- Trending topic feeds
- Refinement bubble data
- Related search suggestions

The v3 internal API (which Pinterest's own web app uses) is not publicly documented and is not available for third-party use.

**Verdict: The official Pinterest API cannot serve this research purpose.**

### Repository Pinterest integration

No Pinterest API integration exists anywhere in the repository. The 8 eval queries marked `source: "pinterest-discovery-2026-05-29"` were generated from **manual observation** on 2026-05-29 — they represent queries that a human observer noted as high-performing on Pinterest, not data extracted via API or scraper.

### Automated scraping assessment

| Method | Assessment |
|---|---|
| Playwright/Puppeteer against pinterest.com | Explicitly rejected in `eval-framework-visual-search-benchmark-2026-06-14.md`: "aggressive bot-detection — captcha, rate-limit, IP block. Doesn't scale, gets fragile fast." Do not build. |
| Commercial SERP scraping tools (Bright Data, SerpAPI, etc.) | Not approved or budgeted in this project. Would tell us which Pinterest pages rank on Google Images, not what Pinterest's internal search surfaces. |
| `site:pinterest.com <query>` via Google | Sparse, SERP-biased. Not representative of Pinterest search. |

### What can be collected safely

| Signal | Safe? | Method |
|---|---|---|
| Autocomplete suggestions | Yes | Type query in Pinterest search bar, observe dropdown — manual record |
| Refinement bubbles | Yes | After searching, record the horizontal chip row below the search bar — manual screenshot |
| Visible board/topic labels | Yes | Observe board names that appear around top pins — manual record |
| Result visual themes | Yes | Describe what the top 20 pins look like by content type — manual observation |
| Screenshots | Yes | Personal, non-commercial research use; no login required for most queries |
| Related search phrases | Yes | Observe the related searches row (appears for some queries) — manual record |

### Research method for Pinterest

**Manual observation only.** For each of 20 queries:
1. Open `pinterest.com/search/pins/?q={query}` in a browser (no login required for most queries).
2. Record the refinement bubble row (chips below search bar) — typically 5-12 chips.
3. Record autocomplete suggestions (type the query in search bar, observe before submitting).
4. Note visible board labels and content themes from top 20 pins (visual summary only, no pin data).
5. Take screenshots for reference. Do not download images.

This is consistent with project precedent (the 2026-05-29 pinterest-discovery eval set was generated this way).

---

## Section 6 — Comparison Methodology & Scoring Rubric

### Per-query comparison dimensions

For each of the 20 queries, compare across three sources:
1. **Curify** — intent chips shown by current implementation (`?intent=` clusters + `?within=` output-type chips)
2. **Bing Images** — `relatedSearches[]`, `pivotSuggestions[]`, visible refinement chips, autocomplete
3. **Pinterest** — refinement bubbles, autocomplete, board/topic labels

### Dimensions

| Dimension | Definition | How to score |
|---|---|---|
| **Suggestion count** | How many distinct sub-intent suggestions does each source expose? | Count unique suggestions per source |
| **Distinct user goals** | How many genuinely different user goals are represented? | Cluster suggestions by goal (not by surface form) |
| **Style diversity** | How many different visual styles are suggested? | Count distinct style modifiers |
| **Format diversity** | How many different output formats are suggested? | Count distinct format modifiers (infographic, poster, printable, etc.) |
| **Entity coverage** | How many named entities (breeds, places, brands, characters) are suggested? | Count |
| **Task/Actionability** | Do suggestions represent actionable creation tasks (make X, design Y)? | Binary per suggestion |
| **Relevance** | Is the suggestion relevant to the original query? | 0/1 per suggestion |
| **Redundancy** | Are suggestions mostly paraphrases of each other? | % of suggestions that map to same intent |
| **Commercial bias** | Do suggestions skew toward buying/selling vs. creation/learning? | Binary per suggestion |
| **Visual specificity** | Does the suggestion imply a specific visual output vs. general content? | 0/1 per suggestion |
| **Curify content available** | Does Curify have results for this suggestion? | Run `node scripts/score_user_queries.cjs "{suggestion}"` → hits ≥ 3 = Yes |
| **Curify cluster mappable** | Does the suggestion fit one of the 8 Curify clusters? | Assign cluster or `unmapped` |
| **Actionable Curify result** | Would following this suggestion lead to a usable Curify creation? | Yes / Partial / No |

### Compact manual scoring rubric (per suggestion)

Score each suggestion from Bing or Pinterest on these 5 fields:

```
Suggestion: {label}
Signal type: {signal_type}
Curify cluster: {cluster or "unmapped"}
Curify content available: Y / N / Partial  (run score_user_queries.cjs)
Actionable: Y / N
Notes: {why this is or isn't a gap}
```

### Distinguishing the four categories

| Category | Definition | How to identify |
|---|---|---|
| **External demand signal** | A sub-intent that external platforms surface — evidence of real user demand | Appears in Bing relatedSearches OR Pinterest refinement bubbles |
| **Curify content availability** | Whether Curify's current catalog can satisfy the sub-intent | `score_user_queries.cjs "{suggestion}"` returns ≥ 3 hits |
| **Curify search capability** | Whether Curify's search can find the content if it exists | Check if hits would rank in top 20 for the parent query |
| **Suggestions Curify should NOT adopt** | Commercial signals (buy/sell), login-gated content, out-of-scope formats (video, audio), competitor ads | Mark `exclude: true` with reason |

### Scoring output table format (per query)

```markdown
## Query: {query}

### Curify chips (current)
| Chip | Cluster |
|---|---|
| {chip label} | {cluster} |

### Bing signals
| # | Label | Signal type | Curify cluster | Content available | Actionable |
|---|---|---|---|---|---|
| 1 | cat breeds | related_search | learning-materials | Y (47 hits) | Y |
...

### Pinterest signals
| # | Label | Signal type | Curify cluster | Content available | Actionable |
|---|---|---|---|---|---|
...

### Gap analysis
- Curify covers: {list}
- Curify misses: {list}
- External demand not yet in Curify: {list}
- Suggestions to ignore: {list}
```

---

## Section 7 — V0 Execution Plan

### Files to create

```
scripts/
  collect_bing_signals.cjs          # Bing Image Search API collector (if API key available)
  score_suggestion.cjs              # Check if a suggestion has Curify content (wraps score_user_queries.cjs)

data/external_signals/
  bing_raw/                         # Raw Bing API JSON responses (gitignored if large)
  pinterest_manual/                 # Manual observation notes per query
  v0_observations.json             # Normalized schema records (the main artifact)
  v0_comparison_report.md          # Final per-query comparison table + summary
```

### Step-by-step plan

#### Step 1 — Gather Curify baseline (automated, ~30 min)

For each of the 20 queries, record the current Curify intent chips and top result counts.

```bash
for QUERY in "cat" "cat breeds" "paris" "paris travel itinerary" ...; do
  node scripts/score_user_queries.cjs "$QUERY" >> data/external_signals/curify_baseline.jsonl
done
```

Then manually record which intent chips appear for each query by loading `/search?q={query}` in the browser. Note which of the 8 clusters are shown and their order.

#### Step 2 — Bing Images API collection (automated if key available, ~2 hours)

**If `BING_SEARCH_API_KEY` is configured in `.env.local`:**

Create `scripts/collect_bing_signals.cjs`:
- Reads the 20 query list
- Calls `https://api.bing.microsoft.com/v7.0/images/search?q={query}&mkt=en-US&count=10`
- Extracts `relatedSearches[]` and `pivotSuggestions[]`
- Writes raw JSON to `data/external_signals/bing_raw/{query_slug}.json`
- Calls Bing Autosuggest for autocomplete: `https://api.bing.microsoft.com/v7.0/suggestions?q={query}`
- Total: ~40 API calls, well within free tier

**If no API key:** Open Bing Images in browser for each query. Record:
- The "Related searches" row (below results) — typically 8-12 suggestions
- The refinement chip row at the top — typically 5-10 chips
- Note any autocomplete completions when typing

#### Step 3 — Pinterest manual observation (~2 hours)

For each of the 20 queries:
1. Open `https://www.pinterest.com/search/pins/?q={url-encoded-query}` (no login required for most queries)
2. Record the refinement bubble row (horizontal chips below search bar)
3. Note autocomplete suggestions for the query
4. Briefly describe what the top ~20 pins show (visual themes, not individual pin data)
5. Take a screenshot of the refinement chip row for reference

Save observations as plain-text notes in `data/external_signals/pinterest_manual/{query_slug}.txt`.

**Do not:** log in to Pinterest to see additional content, scrape pin data, download images, or collect more than the visible refinement signals and chip labels.

#### Step 4 — Normalize into schema (~1 hour)

For each query and source, convert raw observations into the `ExternalSignalRecord` schema:
- Assign `signal_type` from the vocabulary
- Classify `curify_cluster` (or `unmapped`)
- Write `evidence` field by running `scripts/score_user_queries.cjs "{suggestion}"`
- Write to `data/external_signals/v0_observations.json`

#### Step 5 — Map to Curify clusters (~1 hour, manual review)

For each suggestion record:
1. Assign `curify_cluster` — consult `lib/intent_taxonomy.ts` topic slug lists
2. For ambiguous cases: note the conflict; do NOT create a new cluster
3. Flag `unmapped` suggestions that appear frequently across multiple queries — these are candidates for future taxonomy expansion (separate decision)
4. Use `scripts/score_user_queries.cjs "{suggestion_query}"` to check Curify content availability

#### Step 6 — Run comparison and generate report (~1 hour)

Create `data/external_signals/v0_comparison_report.md` with:
- Per-query table (Curify chips vs Bing signals vs Pinterest signals)
- Coverage summary:
  - Suggestions Curify already covers (cluster mapped + content available)
  - Suggestions Curify covers by cluster but has thin content
  - Suggestions that are `unmapped` (outside existing taxonomy)
  - Suggestions to exclude (commercial, login-gated, out-of-scope)
- Top-5 gaps: sub-intents with highest external demand signal (appear across multiple queries) that Curify has thin or no content for
- Top-5 validations: sub-intents Curify already handles well that external platforms also prominently surface

#### Step 7 — Manual review of ambiguous cluster mappings (~30 min)

Go through all `unmapped` records. For each:
- Confirm it genuinely doesn't fit any of the 8 clusters (by checking `lib/intent_taxonomy.ts` topic slug lists)
- Document WHY it is unmapped (new audience signal? new format signal? out-of-scope?)
- Record frequency across 20 queries
- Note as future taxonomy input (separate decision from this phase)

---

## Section 8 — Files to Create in the Next Implementation Prompt

```
scripts/collect_bing_signals.cjs
  — Bing Image Search API caller
  — Inputs: query list, BING_SEARCH_API_KEY from .env.local
  — Outputs: bing_raw/{slug}.json per query
  — Gracefully degrades if no key (prints manual-capture instructions)

scripts/score_suggestion.cjs
  — Thin wrapper around score_user_queries.cjs
  — Input: suggestion string
  — Output: hit count + top 3 template matches
  — Used in Step 5 to populate "evidence" field in schema records

data/external_signals/v0_observations.json
  — Populated during collection; follows ExternalSignalRecord schema

data/external_signals/v0_comparison_report.md
  — Final output artifact

data/external_signals/bing_raw/
  — Raw Bing API responses (add to .gitignore if needed)

data/external_signals/pinterest_manual/
  — Plain-text manual observation notes per query
```

**Not to create in the next prompt:**
- Do not modify `lib/intent_taxonomy.ts`
- Do not modify `lib/intent_clusters.ts`
- Do not modify `nano_inspiration.json` or `nano_templates.json`
- Do not add Business Overrides

---

## Section 9 — Risks and Limitations

### Bing Images

| Risk | Mitigation |
|---|---|
| No API key available | Fall back to browser observation; still produces valid schema records |
| Bing results are locale/personalization-dependent | Lock to `mkt=en-US`, use private browsing for manual observations |
| `relatedSearches[]` field may be absent for some queries | Record as empty; do not treat absence as "no demand" |
| Bing's suggestions reflect Bing's commercial priorities (ads, Microsoft products) | Flag suggestions where commercial bias is suspected; use `commercial bias` column |
| API responses change over time | Record `captured_at` on every record; this is a point-in-time snapshot |

### Pinterest

| Risk | Mitigation |
|---|---|
| Login wall on some queries | Note which queries require login; use only non-gated observations |
| Refinement chips change based on session/personalization | Use private browsing; note variability in `notes` field |
| Bot detection triggering | Open pages manually; do not automate; rate-limit to ~1 page per minute |
| Pinterest content skews toward specific demographics (home decor, fashion, parenting) | Weight Pinterest signals accordingly; do not over-index on categories where Curify doesn't compete |
| Manual transcription errors | Take screenshots as reference; double-check against screenshot before filing schema record |

### General

| Risk | Mitigation |
|---|---|
| Point-in-time snapshot aging quickly | `captured_at` field enables future re-observation; plan quarterly re-runs |
| 20 queries is a small sample | Explicitly frame as V0 pilot; full 100-query benchmark is the next phase |
| Observer bias in cluster assignment | Use topic slug lists from `lib/intent_taxonomy.ts` as the objective reference; mark truly ambiguous cases `unmapped` |
| Confusing external demand with Curify opportunity | Explicitly track `exclude: true` for suggestions that are out-of-scope for Curify |

---

## Section 10 — Recommended First Executable Step

**Obtain a free-tier Bing Image Search API key, then run the 20-query collection.**

Concrete steps:
1. Go to Azure Portal → Create Resource → "Bing Search v7" → Free tier (S0, 1,000 calls/month)
2. Copy the key into `.env.local` as `BING_SEARCH_API_KEY=<key>` (do not commit)
3. Create `scripts/collect_bing_signals.cjs` — a simple Node.js script calling the Bing Image Search endpoint for each of the 20 queries, extracting `relatedSearches[]` and `pivotSuggestions[]`, writing to `data/external_signals/bing_raw/`
4. Run collection: `node scripts/collect_bing_signals.cjs`
5. Manually observe Pinterest for the same 20 queries in a private browser window (~2 hours)
6. Normalize both into `v0_observations.json`
7. Run `scripts/score_suggestion.cjs` for each suggestion to populate the `evidence` field
8. Generate `v0_comparison_report.md`

**If the Azure key cannot be obtained immediately:** Start with the Pinterest manual observation for the 5 known-sparse queries (queries #4, #7, #8, #9 from the query set) — these are the highest-value targets since Curify already knows it has thin content there. Pinterest signal on those queries reveals whether the sparse content is a catalog gap or a query-matching gap.

---

## Section 11 — `git status --short`

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
?? claude_prompt7_external_signal_research_plan.md
?? docs/daily_report/
?? lib/__tests__/query_normalize.test.ts
?? lib/__tests__/search_business_override.test.ts
?? lib/__tests__/search_metadata_scenarios.test.ts
?? lib/intent_taxonomy.ts
?? lib/query_normalize.ts
?? lib/search_business_override.ts
```

No production code was modified. This file (`claude_prompt7_external_signal_research_plan.md`) is the only new artifact from this prompt.

---

## Appendix — Cross-reference map

| This plan references | Repository location |
|---|---|
| 8-cluster intent taxonomy | `lib/intent_taxonomy.ts` (untracked, in working tree) |
| Existing eval queries | `scripts/configs/search_eval_set.json` |
| `score_user_queries.cjs` | `scripts/score_user_queries.cjs` |
| Existing visual search benchmark framing | `docs/eval-framework-visual-search-benchmark-2026-06-14.md` |
| Existing visual intent routing framing | `docs/eval-framework-visual-intent-routing-2026-06-15.md` |
| Demand signal pipeline | `docs/search-and-content.md` Thread d |
| Pinterest taxonomy gap analysis | `docs/taxonomy-gap-canva-pinterest-2026-06-14.md` |
| Known sparse queries (WARN) | `scripts/eval_search.cjs` output / `node scripts/eval_search.cjs --verbose` |
