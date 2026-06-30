# Prompt 6 Paris Metadata — Semantic Review

**Date:** 2026-06-19  
**Branch:** baobao/multi-intent-topic-cooccurrence  
**Scope:** Single record with `topics: ["france", "travel", "itinerary"]`

---

## 1. Exact Paris Record Inspected

```json
{
  "id": "template-tourist-spot-watercolor-map-infographic-historic-landmarks-of-paris",
  "template_id": "template-tourist-spot-watercolor-map-infographic",
  "params": { "topic": "Historic Landmarks of Paris" },
  "locales": { "en": { "title": "Historic Landmarks of Paris" } },
  "topics": ["france", "travel", "itinerary"],
  "tags": ["infographic", "map", "paris", "travel", "watercolor"]
}
```

---

## 2. Evidence from Content

### Parent template base prompt (the content structure this record renders into):

> "Create a charming illustrated map infographic titled 'Historic Landmarks of Paris'. Layout: **A winding path representing a guided tour or route**, with hand-drawn watercolor illustrations of key locations/scenes along the way, each paired with a title and short description. Add theme-appropriate decorative elements (like bikes, leaves, boats, or city skyline silhouettes). Style: Whimsical watercolor illustration style, soft pastel colors, vintage travel poster aesthetic, clean typography, direct high-quality image generation."

### Parent template topics:
```json
["travel", "itinerary", "design", "posters", "watercolor", "map",
 "infographic", "illustration", "art-prints", "wall-art"]
```
The parent template itself carries `"itinerary"` in its own `topics` list — the classification was intentional at the template level.

### Record aliases (route-related terms added in Prompt 6):
`"itinerary plan"`, `"journey plan"`, `"road book"`, `"roadbook"`, `"route plan"`, `"travel route"`, `"trip plan"`, `"Paris tourist map"`, `"Paris travel guide"`

### Tags: `["infographic", "map", "paris", "travel", "watercolor"]`

### Valid existing topic pool check:
- `"map"` — 0 records (not a valid existing topic)
- `"landmarks"` — 0 records (not a valid existing topic)
- `"infographic"` — 0 records (not a valid existing topic)
- `"france"` — 19 records ✓
- `"travel"` — 41 records ✓
- `"itinerary"` — appears in multiple records ✓

---

## 3. Whether `itinerary` Was Semantically Accurate

**Verdict: YES — `itinerary` is semantically accurate. No change made.**

### Reasoning:

The decision hinges on the template's content structure. The base prompt explicitly produces **"a winding path representing a guided tour or route"** with locations/scenes ordered along that path. This is:

- An **ordered travel route** ✓  
- A **sequence of stops intended as a travel plan** ✓  

Decision Rule 2 says: *"If it is **only** a Paris landmark map, tourist guide, or attraction infographic, remove `itinerary`."* The operative word is **only**. This record is **not only** a static landmark map — the template structure generates an **ordered winding path through stops**, making it a visual tour route, not merely a flat attraction index.

Decision Rule 1 says: *"Keep `itinerary` only if the content genuinely represents an itinerary or ordered route plan."* The winding path structure is an ordered route plan. ✓

Additionally, the **parent template itself** declares `"itinerary"` in its topics, establishing that the template category is intentionally itinerary-adjacent. Removing `itinerary` from the child record while the parent template retains it would create an inconsistency.

The aliases also include legitimately route-related terms (`"route plan"`, `"travel route"`, `"road book"`) that reflect genuine content characteristics, not SEO inflation.

---

## 4. Final Topics

```json
["france", "travel", "itinerary"]
```

No change from current state.

---

## 5. Files Changed

**None.** The review concluded `itinerary` is semantically accurate. No edits were made to `nano_inspiration.json` or any other file.

---

## 6. Test Result

```
 ✓ lib/__tests__/query_normalize.test.ts          (22 tests)
 ✓ lib/__tests__/topic_resolver.test.ts           (20 tests)
 ✓ lib/__tests__/topic_cooccurrence.test.ts       (10 tests)
 ✓ lib/__tests__/search_business_override.test.ts (34 tests)
 ✓ lib/__tests__/intent_clusters.test.ts          (44 tests)
 ✓ lib/__tests__/search_metadata_scenarios.test.ts (30 tests)

Test Files  6 passed (6)
     Tests  160 passed (160)
```

**PASS — all 160 tests green.**

---

## 7. TypeScript Result

```
(no output)
```

**PASS — zero type errors.**

---

## 8. Eval Result

```
paris travel itinerary  │ prefill-pool-2026-06-14 │ rich │ thin │ 2 │ WARN
```

Overall: `PASS=106  WARN=19  FAIL=0  (of 125)`

The `paris travel itinerary` WARN is pre-existing and reflects genuinely sparse content in this niche (only 2 matching records exist), not a metadata quality issue. The record's `itinerary` topic is accurate; the WARN is a corpus coverage gap, not a tagging error.

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
?? claude_prompt6_safe_warn_fixes_result.md
?? docs/daily_report/
?? lib/__tests__/query_normalize.test.ts
?? lib/__tests__/search_business_override.test.ts
?? lib/__tests__/search_metadata_scenarios.test.ts
?? lib/intent_taxonomy.ts
?? lib/query_normalize.ts
?? lib/search_business_override.ts
```

No new modifications. This review session introduced zero file changes.
