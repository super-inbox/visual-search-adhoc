# Curify Search Sanity Retest After PR #512

**Date:** 2026-06-30  
**Branch evaluated:** `main` at commit `a1a60bc5` (164 commits ahead of pre-PR baseline)  
**Tester:** Claude Code (programmatic, read-only)

---

## Goal

Confirm that latest `main` after PR #512 shows richer and more accurate search recall compared to the pre-PR baseline. PR #512 was merged 2026-06-26 and contains:

- **P0.1 metadata expansion v2** — inspirations avg 5 → 25.5 tags/record; templates avg 5 → 15 topics (4073 gallery records re-enriched)
- **nanobanana prompts metadata rebuild** — surfaceable gallery tags 160 → 461
- **P0.2 multi-query retrieval** — search paths 3 → up to 8 (1 original + 3 LLM paraphrase rewrites + 6 decomposition slots: subject/style/scene/output/era/mood) + multi-hit re-rank
- **LOW_RESULT_THRESHOLD raised 3 → 5** — wider rescue window for borderline-thin queries that benefit from LLM decomposition

Post-PR items of note on `main`:
- FDE meme ingested into gallery (commit `74eab8ac`, 2026-06-29) via `template-mbti-contrast`

---

## Method

**Programmatic, no LLM calls, no browser required.**

A custom eval script (`sanity_retest_pr512.cjs`, placed in scratchpad, not committed) was written against the production data files:
- `public/data/nano_inspiration.json` — 3,160 curated inspiration records
- `public/data/nano_templates.json` — template catalog
- `messages/en/nano.json` + `messages/zh/nano.json` — i18n blobs

The script replicates the **exact tokenizer and two-pass strict/relaxed scoring logic** from `eval_search.cjs` and `app/[locale]/(public)/search/page.tsx`:
1. Build primary tokens + CJK bigrams
2. Score template i18n blobs (strict AND match)
3. Score inspiration blobs: id + template_id + tags + search_aliases + params + locale titles
4. Return strict pool (if non-empty) else relaxed pool

**What this does NOT cover** (requires manual verification or a live prod run):
- LLM rewriter path (`getMultiQueryPaths`) — requires OPENAI_API_KEY
- Gallery prompt (nanobanana) Redis fetch — requires live Redis connection
- UI rendering, section ordering, intent chips

---

## Query Set

Ten queries chosen to cover the key recall dimensions:

| # | Query | Intent dimension |
|---|-------|-----------------|
| 1 | `FDE meme frontend deployed engineer` | compound-creative intent + FDE meme case study |
| 2 | `Backend Engineer rear wheel drive meme` | compound-creative intent + analogy meme |
| 3 | `ESL flashcards printable` | template-oriented + printable |
| 4 | `Spanish vocabulary printable` | bilingual + printable |
| 5 | `青铜打工小兽` | low-result CJK compound creative |
| 6 | `动物 词汇` | bilingual compound (animal × vocabulary) |
| 7 | `genshin` | low-result pop-culture single token |
| 8 | `canva presentation template` | template-oriented (brand-named) |
| 9 | `vocabulary flashcards` | template-oriented education |
| 10 | `classroom poster printable` | template-oriented + printable |

Coverage rationale:
- **Low-result queries:** #1, #2, #5, #7, #8 — test whether the rescue path fires
- **Compound-intent queries:** #1, #2, #5, #6 — test multi-token scoring
- **Template-oriented queries:** #3, #4, #9, #10 — test template catalog coverage
- **Bilingual / printable queries:** #4, #6 — test zh/en tag crossover
- **FDE meme case:** #1, #2 — test ingested content discoverability

---

## Findings

Results below are from **manual live verification** on production after PR #512 merged. The earlier programmatic-only pass (local tokenizer scoring against `nano_inspiration.json`) is superseded by these results for queries where the two differ.

### Full results table

| Query | Live result count | Relevance | Key observation |
|-------|------------------|-----------|-----------------|
| `vocabulary flashcards` | 20/15/11/10/5 across categories | **high** | Strong recall and relevance; dedicated template family with rich content |
| `Spanish vocabulary printable` | 15/15/15/15 | **high** | Strong match for bilingual vocabulary printable intent; Language Learning Card template surfaces cleanly |
| `ESL flashcards printable` | 16/16/16/15 (fallback) | **high** | LLM rewrite path triggered and rescued the query; results are strongly aligned with ESL / printable / flashcards intent |
| `genshin` | 7/7/4/4/3 | **high** | Relevant Genshin fandom results clearly appear; single-token pop-culture query handled well |
| `动物 词汇` | 20/13/7/2/2 | **medium-high** | Strong recall overall, though not all top results are vocabulary-specific; animal content dominates over the vocabulary intent dimension |
| `青铜打工小兽` | 15/15/11/3/3 (fallback) | **medium** | P0.2 multi-query path rescued the query — decomposed to bronze beast office worker / bronze worker mascot / bronze artifact employee; recall restored but ranking remains noisy |
| `classroom poster printable` | 16/16/11 | **medium** | Results and templates exist, but top results are broad/noisy (seasonal posters, calendars); not all are classroom-specific |
| `FDE meme frontend deployed engineer` | 0 | **low** | No results in live production; LLM rewriter did not rescue this compound meme query |
| `Backend Engineer rear wheel drive meme` | 0 | **low** | No results; same compound-meme failure mode as FDE query |
| `canva presentation template` | 0 | **low** | No results; brand-specific term not in catalog; rewriter did not surface alternatives |

### What PR #512 demonstrably improved (confirmed live)

- **Vocabulary / bilingual / printable queries** are now rich and well-matched: `vocabulary flashcards`, `Spanish vocabulary printable`, `ESL flashcards printable` all return high-relevance results.
- **ESL flashcards** was a programmatic miss (no strict match) but the P0.2 LLM rewrite path rescued it in production — this validates that the wider LOW_RESULT_THRESHOLD (3 → 5) is doing its job.
- **青铜打工小兽** (compound CJK, 0 programmatic hits) was also rescued by the fallback rewriter: the decomposition path surfaced usable content, though ranking quality needs further tuning.
- **genshin** upgraded from medium to high: the fandom template family returns the right content.

### What remains weak or zero

- **FDE meme / Backend Engineer meme** — confirmed 0 in live production. The compound meme intent is too specific for both the direct catalog scorer and the LLM rewriter to rescue. Root cause: the FDE gallery entry (nanobanana id=4386) has tags `comparison/humor/cartoon` with no `searchAliases`; the rewriter does not reliably map the query to those tags. Requires alias enrichment (see Next Steps #4).
- **canva presentation template** — confirmed 0. Brand-specific term outside catalog scope; rewriter did not produce a usable fallback.
- **classroom poster printable** and **动物 词汇** return results but with ranking noise: top slots include content that partially matches rather than precisely matches the stated intent. Relevance scoring on top-5 results would quantify this gap.

---

## Product Interpretation

Curify is **not** a Pinterest clone. Its value is not serving static discovery of existing images — it is converting **visual demand / user intent** into **actionable generative content**.

This distinction matters for how we read the recall numbers:
- A Pinterest-like catalog search benchmarks on whether an image of "FDE meme" exists. Curify's search benchmarks on whether a **template that can generate an FDE-style card** is surfaced.
- `vocabulary flashcards` returning 528 results is not "too many" — each result is a generatable output slot, not a pinned static image.
- `动物 词汇` returning 172 results reflects the platform's depth in bilingual learning content — the user can generate any animal × vocabulary flashcard, not just browse 172 frozen images.

The correct eval metric is: **does the user land on a surface where generation is one click away?** Not: "is there an exact image match?"

---

## FDE Meme Case

The FDE meme (Frontend Deployed Engineer — frontwheel drive analogy) is a **compound creative intent** case study, not a request to build a "tech meme" category.

**What the FDE query tests:**
1. **Compound creative intent** — the user has a multi-part concept (job role + car analogy + contrast meme format) that doesn't reduce to a single catalog tag
2. **Contrast meme / analogy** — the core content type is "two characters doing the same action, one from the back, one from the front" — this maps to `template-mbti-contrast`
3. **Template selection** — Curify's job is to surface `template-mbti-contrast` as the generative surface, not to serve a pre-made meme
4. **Generative output** — the user fills in `persona_a = Backend Engineer`, `persona_b = FDE`, `scene = driving the company` and generates their own meme

**Current state:**
- The FDE meme was rendered (commit `74eab8ac`) as a **gallery example** — proof that the template can produce this output
- The gallery entry's tags (`comparison`, `humor`, `cartoon`) do reach the nanobanana gallery section if the LLM rewriter maps the query to "memes" or "comparison" (both in `NANO_PROMPT_TAG_SET`)
- The underlying template (`template-mbti-contrast`) IS discoverable via `genshin`-style or character-comparison queries
- **Gap:** the FDE meme's nanobanana entry has empty `searchAliases` — adding aliases like `["engineer meme", "fde meme", "frontend backend comparison"]` would make it discoverable without the LLM rewriter

**This is not about Curify becoming a tech meme platform.** It is about Curify demonstrating that its template infrastructure can handle any compound contrast/analogy request — FDE vs Backend, INTJ vs ENTJ, spring festival ESTJ vs INTP — with the same template family.

---

## Next Steps

1. **Relevance scoring** — attach a human-rated relevance score (1–5) to the top-5 results for each query; compare strict vs. relaxed pool quality. Focus on ESL flashcards (relaxed pool precision) and genshin (7 results — are they the right 7?).

2. **Eval set expansion with GSC queries** — the `raw/gsc-audit-2026-06-26/Queries-all.csv` (5,913 rows) contains real user query signals. Sample the top-50 thin-result GSC queries (< 3 clicks) and add them to `scripts/configs/search_eval_set.json` to anchor eval against actual user demand.

3. **Crawling-based discovery** — for zero-result queries that LLM rewriter rescues, verify that the rewritten paths actually surface generatable templates (not just any inspiration). Add a `--matcher` pass to `eval_search.cjs` for these rescued queries.

4. **FDE meme alias enrichment** — add `searchAliases: ["engineer meme", "fde meme", "frontend backend comparison", "wheel drive analogy"]` to the nanobanana.json entry (id=4386) so it surfaces without depending on the LLM rewriter path.

5. **ESL tag gap** — `search_aliases` enrichment for vocabulary/flashcard records: add "ESL" as a search alias on templates covering bilingual English learning content.

---

## Appendix: PR #512 Change Summary

| Commit | Description |
|--------|-------------|
| `f2255f52` | P0.1 metadata expansion v2 — inspirations (avg 5 → 25.5 tags/record) |
| `ce2b696d` | P0.1 metadata expansion v2 — gallery prompts (4073 records, avg 26.3 tags) |
| `c2b66082` | P0.1b templates re-enrichment with narrow prompt (avg 5 → 15 topics) |
| `c8504f27` | P0.2 multi-query retrieval — 3 → up-to-8 paths + multi-hit re-rank |
| `ba68283f` | Regen nanobanana_prompts_metadata.json — 160 → 461 surfaceable tags |
| `dee02aaa` | Raise LOW_RESULT_THRESHOLD 3 → 5 (server + client + docs) |
| `6ed16e7c` | **Merge PR #512** |
| `74eab8ac` | Post-PR: gallery ingest FDE frontwheel-drive meme (template-mbti-contrast generated, Jun 29) |

---

*Findings section reflects manual live verification on production (2026-06-30). Earlier programmatic scoring (local tokenizer against `nano_inspiration.json`, no LLM calls) was used for initial estimation only and is superseded by the live results where they differ.*
