# Prompt 4 Implementation Result

## Summary

Prompt 4 added three deterministic layers to the Multi-Intent search chip system:
- **Query normalization** (`lib/query_normalize.ts`) -- canonical form for override lookup
- **Business Override** (`lib/search_business_override.ts`) -- high-confidence cluster promotion
- **Integration** (`app/[locale]/(public)/search/page.tsx`) -- wired into chip generation

All 115 unit tests pass. TypeScript check returns zero errors.

---

## Files Changed or Created

| File | Status | Description |
|---|---|---|
| `lib/query_normalize.ts` | New | Deterministic query normalizer |
| `lib/search_business_override.ts` | New | Business Override map + apply logic |
| `lib/__tests__/query_normalize.test.ts` | New | 22 normalization tests |
| `lib/__tests__/search_business_override.test.ts` | New | 19 override tests |
| `app/[locale]/(public)/search/page.tsx` | Modified | Imports + normalizedQuery + override apply |

Previously modified in Prompt 3 (unchanged this session):
- `lib/intent_taxonomy.ts` (new)
- `lib/intent_clusters.ts` (modified)
- `app/[locale]/(public)/search/SearchResultsClient.tsx` (modified)
- `lib/__tests__/intent_clusters.test.ts` (modified)

---

## Business Override Precedence

```
User query
  → normalizeSearchQuery(q)          # canonical form: cats → cat
  → getBusinessOverride(normalized)   # lookup in OVERRIDE_MAP
  → applyBusinessOverride(chips, overrideSlug, locale)
      if overrideSlug found in ranked chips → move to index 0
      if overrideSlug NOT found → return chips unchanged (no injection)
  → intentChips (passed to SearchResultsClient)
```

Full precedence chain for the chip row:
1. Business Override (reorders existing evidence chips only)
2. Content-grounded co-occurrence (rankIntentClusters, minCount=2, topN=5)
3. Raw output-type topic chips (topIntentChipsFromTopicCounts, fallback)
4. Empty chip row (no evidence, no override)

---

## Normalization Rules

`normalizeSearchQuery(raw: string): string`

Steps applied in order:
1. Trim leading/trailing whitespace
2. Lowercase
3. Collapse repeated internal whitespace to single space
4. Normalize punctuation:
   - Curly/smart single quotes + backtick → straight apostrophe `'`
   - Curly/smart double quotes → straight double quote `"`
   - En-dash / em-dash → hyphen-minus `-`
5. Alias table lookup (exact match on full string)

Alias table:
```
cats     → cat
kittens  → kitten
```

Conservative design -- words that change meaning when changed (glass, business, dress, analysis) are NOT in the alias table and pass through unchanged.

---

## Current Override Map

```typescript
const OVERRIDE_MAP = {
  cat:        "visual-art",       // 10 results, top topics: art-prints(8), wall-art(8), posters(7)
  kitten:     "visual-art",       // cat-content family; 0 direct results but same design domain
  "cat breeds": "learning-materials",  // comparison/infographic content family
};
```

---

## Test Results

```
Test Files  5 passed (5)
     Tests  115 passed (115)
  Duration  523ms
```

Breakdown:
- `topic_resolver.test.ts`              20 tests
- `topic_cooccurrence.test.ts`          10 tests
- `intent_clusters.test.ts`             44 tests
- `query_normalize.test.ts`             22 tests
- `search_business_override.test.ts`    19 tests

---

## Commands to Reproduce

```bash
# Run all unit tests
npx vitest run --config vitest.unit.config.ts

# TypeScript check
npx tsc --noEmit

# Git status
git status --short
```

---

## Local Demo Steps

1. Start dev server: `npm run dev`
2. Navigate to `/en/search?q=cats`
   - Expected: intent chip row shows Visual & Art promoted to position 0
3. Navigate to `/en/search?q=science+poster`
   - Expected: no Business Override; chip order is purely evidence-based
4. Navigate to `/en/search?q=cats&intent=visual-art`
   - Expected: active intent pill "Visual & Art" shown; chip row hidden
5. Navigate to `/en/search?q=cats&intent=invalid-slug`
   - Expected: invalid intent silently ignored; chip row shown normally

---

## Remaining Limitations

- **Browser visual verification pending**: The intent cluster chip row (`intent=` parameter, active pill, chip styles) has not been verified live in a browser. Automated tests cover logic but not rendering.
- **Override map is minimal by design**: Only 3 entries. Adding new entries requires data analysis (inspect merged topics for the query in nano_inspiration.json) before committing.
- **`kitten` has 0 current results**: The override is forward-looking (same content family as `cat`). If no results exist for the query, the chip row is empty regardless of override.
- **No topic-level override**: Business Override only promotes existing cluster chips. If a cluster chip is absent from the evidence (count below minCount), override does not inject it.
- **`cats breeds` not aliased**: Only single-token aliases exist. `cats breeds` after normalization remains `cats breeds` (no alias entry). This is intentional -- multi-token alias pairs would need separate OVERRIDE_MAP entries.

---

## Git Status

Branch: `baobao/multi-intent-topic-cooccurrence`
Last commit: `ca338b48 feat(search): add topic co-occurrence intent evidence`

All changes uncommitted (working tree only):
- Modified: `page.tsx`, `SearchResultsClient.tsx`, `intent_clusters.ts`, `intent_clusters.test.ts`
- Untracked: `intent_taxonomy.ts`, `query_normalize.ts`, `search_business_override.ts`, all new test files, `docs/daily_report/`
