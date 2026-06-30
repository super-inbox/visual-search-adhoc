# Prompt 4.6 — Redirect Fix Result

**Date:** 2026-06-19  
**Branch:** `baobao/multi-intent-topic-cooccurrence`  
**Verdict:** ✅ FIXED — `cat` and `cats` now follow identical routing; all other topic redirects intact.

---

## 1. Root Cause

`lib/searchIndex.ts` registers `"cat"` as an alias for the `animal` topic:

```ts
{ slug: "animal", label: "Animals & Pets", aliases: ["pet", "pets", "wildlife", "creature", "dog", "cat"] }
```

`page.tsx` runs its topic-redirect check on `query = q.trim().toLowerCase()`. For `q=cat`, this yields `"cat"`, which matches the `animal` alias with only one candidate (`containsQuery.length === 1`) → redirect fires.

`normalizeSearchQuery("cats") → "cat"` is computed in Prompt 4 **only** for the Business Override lookup, not for the topic-redirect check. So:
- `q=cat` → `query = "cat"` → matches animal alias → **redirected**
- `q=cats` → `query = "cats"` → no alias match → **stays on search page**

---

## 2. Exact Redirect Source

**File:** `app/[locale]/(public)/search/page.tsx`  
**Condition (before fix):** line ~400
```ts
if (target && !target.searchFallback) {
  redirect(target.href ? `/${locale}${target.href}` : `/${locale}/topics/${target.slug}`);
}
```
`target` is set when a unique topic alias match is found in `ALL_SUGGESTIONS`.  
For `q=cat`, `target = { slug: "animal", ... }`, `searchFallback = undefined` → redirect to `/en/topics/animal`.

---

## 3. Was the Redirect Intentional?

**Outdated conflict.** The `cat → animal` alias predates the Multi-Intent search work (Prompt 2–4). The intent was to route a bare "cat" query to the topic page because no richer search experience existed. Now that:
- A Business Override explicitly maps "cat" to the `visual-art` cluster
- Multi-intent chips, cluster filtering, and co-occurrence evidence all run on the search page
- `normalizeSearchQuery("cats") → "cat"` makes the two queries semantically equivalent

…the topic redirect actively contradicts the curated multi-intent experience. No repository documentation or test file asserts that `cat` must redirect to `/topics/animal`. `docs/gallery-tag-taxonomy.md` mentions `cat → animal` as a gallery-tag classification rule (separate concern), not a search-redirect requirement.

---

## 4. Final Behavior for `cat` and `cats`

Both stay on the search results page and receive identical treatment:

| Query | normalizeSearchQuery | Business Override | Routing |
|-------|---------------------|-------------------|---------|
| `cat` | `cat` | `visual-art` | stays on `/search` |
| `cats` | `cat` | `visual-art` | stays on `/search` |
| `Cat` | `cat` | `visual-art` | stays on `/search` |
| `CATS` | `cat` | `visual-art` | stays on `/search` |
| ` cat ` | `cat` | `visual-art` | stays on `/search` |

Both render: `Visual & Art` chip first (count=12), then `Social & Personal (9)`, `Learning Materials (7)`.

---

## 5. Files Changed (this prompt)

### `lib/search_business_override.ts`
- Added `import { normalizeSearchQuery } from "./query_normalize"`
- Added exported function `shouldSkipTopicRedirect(rawQuery: string): boolean` — returns `true` when a Business Override exists for the normalized query, indicating the search page is the richer destination.

### `app/[locale]/(public)/search/page.tsx`
- Added `shouldSkipTopicRedirect` to the import from `@/lib/search_business_override`
- Changed the redirect condition from:
  ```ts
  if (target && !target.searchFallback) {
  ```
  to:
  ```ts
  if (target && !target.searchFallback && !shouldSkipTopicRedirect(q)) {
  ```

### `lib/__tests__/search_business_override.test.ts`
- Added `shouldSkipTopicRedirect` to the import
- Added a new `describe('shouldSkipTopicRedirect', ...)` suite with 15 tests covering all required input variants

---

## 6. Tests Added or Updated

**File:** `lib/__tests__/search_business_override.test.ts`

New `shouldSkipTopicRedirect` describe block (15 tests):

| Input | Expected | Rationale |
|-------|----------|-----------|
| `"cat"` | `true` | canonical form, has BO |
| `"cats"` | `true` | plural, normalises to "cat" |
| `"Cat"` | `true` | leading capital |
| `"CATS"` | `true` | all-caps |
| `"  cat  "` | `true` | surrounding whitespace |
| `"  cats  "` | `true` | plural with whitespace |
| `"kitten"` | `true` | own BO entry |
| `"kittens"` | `true` | normalises to "kitten" |
| `"cat breeds"` | `true` | multi-token BO entry |
| `"dog"` | `false` | animal alias — redirect must still fire |
| `"travel"` | `false` | topic slug — redirect must still fire |
| `"stickers"` | `false` | no BO, no redirect bypass |
| `"science poster"` | `false` | content query, no BO |
| `"birthday card"` | `false` | content query, no BO |
| `""` | `false` | empty string |

---

## 7. Unit Test Result

```
 ✓ lib/__tests__/query_normalize.test.ts            (22 tests)
 ✓ lib/__tests__/topic_resolver.test.ts             (20 tests)
 ✓ lib/__tests__/search_business_override.test.ts   (34 tests)  ← was 19, now 34
 ✓ lib/__tests__/topic_cooccurrence.test.ts         (10 tests)
 ✓ lib/__tests__/intent_clusters.test.ts            (44 tests)

 Test Files  5 passed (5)
      Tests  130 passed (130)
   Duration  521ms
```

---

## 8. TypeScript Result

```
npx tsc --noEmit → (no output, exit 0)
```

Zero type errors.

---

## 9. Live Verification

**Dev server: port 3001**

All responses fetched via `curl -sL` (following the locale-prefix middleware redirect). The `NEXT_REDIRECT` field was checked in the SSR HTML (Next.js App Router dev mode encodes server redirects as `data-dgst="NEXT_REDIRECT;..."`).

| URL | HTTP | Redirect? | Chip row | First chip | Input value |
|-----|------|-----------|----------|------------|-------------|
| `/search?q=cat` | 200 | ❌ no animal redirect ✅ | ✅ yes | Visual & Art (12) | `cat` |
| `/search?q=cats` | 200 | ❌ no redirect ✅ | ✅ yes | Visual & Art (12) | `cats` |
| `/en/search?q=Cat` | 307→200 | ❌ no redirect ✅ | ✅ yes | Visual & Art (12) | `Cat` (header) / `cat` (mobile) |
| `/en/search?q=%20cat%20` | 307→200 | ❌ no redirect ✅ | ✅ yes | Visual & Art (12) | ` cat ` (header) / `cat` (mobile) |
| `/search?q=kitten` | 200 | ❌ no redirect ✅ | ✅ yes | Visual & Art (18)* | `kitten` |
| `/search?q=cat+breeds` | 200 | ❌ no redirect ✅ | ✅ yes | Learning Materials (19)* | `cat breeds` |
| `/search?q=cats&intent=visual-art` | 200 | ❌ no redirect ✅ | ❌ (active pill) | "Visual & Art ×" pill | `cats` |
| `/search?q=dog` | 200 | ✅ → `/en/topics/animal` | — | — | — |
| `/search?q=travel` | 200 | ✅ → `/en/topics/travel` | — | — | — |

\* Business Override promotes visual-art over learning-materials for kitten; learning-materials is promoted for cat breeds.

**Key confirmations:**
- `cat` no longer redirects to `/en/topics/animal` ✅
- `cats` behavior unchanged ✅  
- `dog` still redirects to animal topic ✅
- `travel` still redirects to travel topic ✅
- `cats&intent=visual-art` active filter pill still works ✅
- No redirect loop observed ✅

---

## 10. `git status --short`

```
 M app/[locale]/(public)/search/SearchResultsClient.tsx
 M app/[locale]/(public)/search/page.tsx
 M lib/__tests__/intent_clusters.test.ts
 M lib/intent_clusters.ts
?? claude_prompt4_5_result.md
?? claude_prompt4_6_redirect_fix_result.md
?? docs/daily_report/
?? lib/__tests__/query_normalize.test.ts
?? lib/__tests__/search_business_override.test.ts
?? lib/intent_taxonomy.ts
?? lib/query_normalize.ts
?? lib/search_business_override.ts
```

Note: `search_business_override.ts` and its test file are untracked (added in Prompt 4, not yet committed). The changes from this prompt (`shouldSkipTopicRedirect` + new tests) are included in those untracked files.

---

## 11. `git diff --stat`

```
 app/[locale]/(public)/search/SearchResultsClient.tsx |  133 ++++---
 app/[locale]/(public)/search/page.tsx               |  125 +++++--
 lib/__tests__/intent_clusters.test.ts               |  399 +++++++++++++++++++++
 lib/intent_clusters.ts                              |  149 +++++++-
 4 files changed, 720 insertions(+), 86 deletions(-)
```

The `search_business_override.ts` modifications and new test cases are in untracked files so they appear in `git status` but not `git diff --stat`. The full Prompt 4.6 delta within those files:

- `lib/search_business_override.ts`: +1 import line + 18-line `shouldSkipTopicRedirect` function
- `lib/__tests__/search_business_override.test.ts`: +1 import update + 68-line test suite (15 new tests)
- `app/[locale]/(public)/search/page.tsx`: +1 import update + 4-line comment + guard condition (tracked file, included in diff above)
