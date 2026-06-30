# V0 Manual Collection Instructions — One Query at a Time

**Audience:** Any observer doing the manual browser collection session.  
**Time per query:** ~10–15 minutes.  
**Tools needed:** A web browser (Chrome or Firefox recommended), a text editor, a screenshot tool.

---

## Before you start

### Rules (read first)
- Collection is **manual**. Do not use automation, browser extensions that inject scripts, or any tool that makes automated requests.
- Use **private/incognito browsing** for every page. This minimizes personalization effects from your search history.
- Do **not** scrape, auto-click, or programmatically interact with Bing or Pinterest.
- Do **not** download images or Pin data. Only record visible text labels (chip text, suggestion text, board names).
- If a signal is **absent**, record it as absent — do **not** guess or fill in what you think should be there.
- If you cannot see a signal (login wall, region block, empty result), record the barrier, not the signal.
- Take a **screenshot** of the full visible area after loading the page and after the chips appear. Name screenshots consistently (see naming convention below).

### Screenshot naming convention
```
bing_<query_slug>_<YYYY-MM-DD>.png
pinterest_<query_slug>_<YYYY-MM-DD>.png
```

Query slug: replace spaces with underscores, remove special characters.

Examples:
```
bing_cat_2026-06-19.png
pinterest_cat_2026-06-19.png
bing_paris_travel_itinerary_2026-06-19.png
pinterest_paris_travel_itinerary_2026-06-19.png
bing_warmup_routine_running_checklist_2026-06-19.png
```

Save screenshots in:
- `data/external_signals/bing_manual/`
- `data/external_signals/pinterest_manual/`

---

## Step 1 — Curify baseline (local, ~3 min per query)

You only need to do this if the `intent_chips_visible` field in `v0_observations.json` is still `"pending_manual_capture"`.

1. Start the local dev server: `npm run dev`
2. Open the URL listed in `localhost_url` for the query (e.g. `http://localhost:3000/en/search?q=cat`)
3. Record:
   - **Total result count shown** (the number displayed in the results header)
   - **Visible intent chips** (the cluster pill row, if present) — record the label text and their left-to-right order
   - **Output-type chips** (the `?within=` row, if present) — record labels and order
   - **Rewrite banner** — if a "We also searched for…" banner appears, record it
4. Open `data/external_signals/v0_observations.json` in a text editor.
5. Under the matching query → `curify_baseline`:
   - Set `intent_chips_visible` to a list of chip labels in order, or `"not_visible"` if no chips appear.
   - Set `rewrite_banner_visible` to the banner text, or `"not_visible"`.
   - Update `result_count_strict` if the page shows a different count than the file says.

---

## Step 2 — Bing Images (manual, ~5 min per query)

Bing Image Search API v7 was retired on 2025-08-11. **Do not attempt to use any Bing API.**  
All data collection is from the browser UI only.

### 2a — Autocomplete
1. Open a **new private/incognito** browser window.
2. Go to `https://www.bing.com/images`
3. Click the search bar. Type the query **slowly** (so autocomplete appears) but **do not press Enter yet**.
4. Record all visible autocomplete suggestions in the dropdown. Stop typing once you see the full dropdown.
5. Take a screenshot of the autocomplete dropdown: `bing_<slug>_autocomplete_<date>.png`

### 2b — Refinement chips (filters at top)
6. Press Enter to submit the search.
7. Wait for the page to fully load. Scroll slowly to see the full chip row.
8. Record **all visible filter/refinement chips** that appear at the top or just below the search bar.
   - These look like pill-shaped buttons: e.g. "Cute" · "Breeds" · "Memes" · "Wallpaper"
   - Record their text and left-to-right order (position 1, 2, 3…).
9. Take a screenshot of the chip row: `bing_<slug>_<date>.png`

### 2c — Related searches (bottom of page)
10. Scroll to the bottom of the Bing Images results page.
11. Look for a **"Related searches"** or **"Explore more"** section. It may appear as a row of text links or image tiles.
12. Record all visible related search labels/queries.
13. Note: if no related searches section is visible, record `"not_visible"`.

### 2d — Entity/category labels
14. Look for any Knowledge Panel, entity card, or category grouping that appears alongside or above results.
    - Example: "Cat Breeds" panel, animal category labels on image tiles.
15. Record the panel title and any sub-categories listed.

### 2e — Visual categories
16. Some Bing Images pages show labeled image clusters (e.g. "Cute cats", "Black cats", "Cat memes").
17. Record the category label text for any such groupings visible on the first screen.

### 2f — Record in notes file
18. Open (or create) `data/external_signals/bing_manual/<query_slug>_notes.txt`
19. Write freeform notes covering:
    - Date and time of capture
    - Browser used (Chrome/Firefox) and version
    - Private/incognito mode: yes/no
    - Autocomplete suggestions (numbered list)
    - Refinement chips (numbered list with position)
    - Related searches (numbered list)
    - Entity/category labels (if any)
    - Visual categories (if any)
    - Any barriers (e.g. "page showed a CAPTCHA", "region redirect")
    - Any other observations

---

## Step 3 — Pinterest (manual, ~5 min per query)

Pinterest API does not expose general search or refinement signals. Do not use any Pinterest API or automated browser.  
All data is from the visible browser UI only.

### 3a — Autocomplete
1. Open a **new private/incognito** browser window.
2. Go to `https://www.pinterest.com`
3. Click the search bar. Type the query **slowly** — observe the autocomplete dropdown.
4. Record all visible autocomplete suggestions.
5. Take a screenshot: `pinterest_<slug>_autocomplete_<date>.png`

### 3b — Refinement bubbles
6. Press Enter to submit the search.
7. Wait for the page to fully load.
8. **Check if a login wall appears.** If you must log in to see results, record `"login_required": true` and stop collecting for this query (or log in if you have a personal account — do not create a fake account).
9. If results are visible without login: look for the **horizontal row of chip/bubble refinements** that appears just below the search bar. These look like rounded pill buttons: e.g. "Cute" · "Ideas" · "Drawing" · "Aesthetic"
10. Record ALL visible refinement bubbles in order (position 1, 2, 3…).
11. Take a screenshot of the refinement bubble row: `pinterest_<slug>_<date>.png`

### 3c — Board labels
12. Scan the top 20 visible pins. Note any board name labels that appear below or beside pin images.
13. Record distinct board names you can see (not individual pin descriptions — just board-level labels).
14. Board names reveal how users categorize this content.

### 3d — Dominant visual themes
15. Look at the top ~20 pins visually (do not click into them).
16. Write a brief 1-3 sentence description of dominant visual themes:
    - Are they mostly photographs? Illustrations? Text-heavy? Infographic-style?
    - Is there a dominant color palette?
    - Do most pins show the same subject, or is there variety?
    - Example: "Top 20 pins are mostly illustrated day-by-day itinerary text plans in pastel colors. Two are watercolor maps. One is a packing list."

### 3e — Record in notes file
17. Open (or create) `data/external_signals/pinterest_manual/<query_slug>_notes.txt`
18. Write freeform notes covering:
    - Date and time of capture
    - Browser used and version
    - Private/incognito mode: yes/no
    - Login required: yes/no (and if yes, stop here for this source)
    - Autocomplete suggestions (numbered list)
    - Refinement bubbles (numbered list with position)
    - Board labels observed (list)
    - Dominant visual themes (1-3 sentences)
    - Any barriers or anomalies

---

## Step 4 — Fill `v0_observations.json`

After completing manual capture for one query:

1. Open `data/external_signals/v0_observations.json`
2. Find the record for your query.
3. For each platform section, update:
   - `status`: change from `"pending_manual_capture"` to `"captured"`, `"not_visible"`, `"login_blocked"`, or `"empty_result"` as appropriate.
   - `captured_at`: set to the ISO 8601 datetime of your capture (e.g. `"2026-06-19T14:30:00Z"`).
   - Fill in the arrays (`autocomplete`, `refinement_chips`, `related_searches`, etc.) from your notes.
4. For each observed suggestion, add an entry to the `suggestions` array using this format:

```json
{
  "label": "cat breeds",
  "search_query": "cat breeds",
  "position": 1,
  "signal_type": "related_search",
  "normalized_intent": "visual reference for different cat breeds",
  "curify_cluster": "learning-materials",
  "evidence": "pending — run: node scripts/score_user_queries.cjs 'cat breeds'",
  "notes": "Strong Curify candidate; breed-infographic template family exists"
}
```

### Signal type reference (use only these values)
| Value | When to use |
|---|---|
| `related_search` | A fully formed alternative query shown as a suggestion |
| `refinement_chip` | A chip/bubble that narrows the current query |
| `autocomplete` | A completion shown before the search is submitted |
| `visual_category` | A labeled visual cluster of results |
| `entity_refinement` | A named entity (breed, place, character, brand) |
| `style_refinement` | A visual style modifier (watercolor, vintage, cartoon) |
| `format_refinement` | A format or layout modifier (printable, poster, infographic) |
| `audience_refinement` | An audience modifier (kids, classroom, beginner) |
| `occasion_refinement` | A time or event modifier (Christmas, birthday, morning) |
| `task_refinement` | An action modifier (DIY, template, how to make) |
| `unknown` | Cannot classify reliably |

### Curify cluster reference (use only these values)
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

Use `"unmapped"` when you genuinely cannot fit the suggestion into any cluster. Do not force a fit.

---

## Step 5 — Evidence check (optional, run after capture)

For each suggestion in `v0_observations.json`, you can check Curify content availability:

```bash
node scripts/score_user_queries.cjs "cat breeds"
```

Replace the `evidence` field value with the actual output:
```
"evidence": "7 hits, moderate bucket. Top templates: species-science × 3, dog-breed-retro-infographic × 2"
```

This step is optional during V0 but required before the final comparison report.

---

## Quick reference — query URLs

| Query | Curify (local) | Bing Images | Pinterest |
|---|---|---|---|
| `cat` | `http://localhost:3000/en/search?q=cat` | `https://www.bing.com/images/search?q=cat` | `https://www.pinterest.com/search/pins/?q=cat` |
| `paris` | `http://localhost:3000/en/search?q=paris` | `https://www.bing.com/images/search?q=paris` | `https://www.pinterest.com/search/pins/?q=paris` |
| `science poster` | `http://localhost:3000/en/search?q=science+poster` | `https://www.bing.com/images/search?q=science+poster` | `https://www.pinterest.com/search/pins/?q=science+poster` |
| `paris travel itinerary` | `http://localhost:3000/en/search?q=paris+travel+itinerary` | `https://www.bing.com/images/search?q=paris+travel+itinerary` | `https://www.pinterest.com/search/pins/?q=paris+travel+itinerary` |
| `warmup routine running checklist` | `http://localhost:3000/en/search?q=warmup+routine+running+checklist` | `https://www.bing.com/images/search?q=warmup+routine+running+checklist` | `https://www.pinterest.com/search/pins/?q=warmup+routine+running+checklist` |
