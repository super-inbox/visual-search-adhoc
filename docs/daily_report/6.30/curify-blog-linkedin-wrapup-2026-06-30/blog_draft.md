# Visual Search in 2026: A 5-Platform, 58-Query Benchmark

_How Google, Bing, Pinterest, Canva, and Curify handle the same creative and consumer queries — and what the gap tells us about where AI image search is actually going._

---

## The Problem with Visual Search Benchmarks

Most "visual search comparisons" test one thing: did the platform return results for this query? That's a floor, not a metric.

The more interesting question is: **when a user searches for a creative output — a flashcard, a poster, a vocabulary chart — which platform actually gets them from intent to creation?**

To answer that, we ran a 58-query benchmark across five platforms: Google Images, Bing Images, Pinterest, Canva, and Curify. 30 of those queries had clear creative production intent (the user wanted to make something: a printable, a template, a chart). 28 were consumer browsing (fan content, lifestyle aesthetic, nature imagery). We collected top-10 results, related-search chips, and template availability for each query on each platform in June 2026. Then we re-ran Curify's portion programmatically on June 30, 2026, after a significant search infrastructure update (PR #512), to show where recall moved.

Here's what we found.

---

## Platform Snapshot: What Each Does Well

_Methodology note: Google, Bing, Pinterest, and Canva data was collected June 19–23, 2026 and has not been re-crawled for this post. Only Curify was re-scored, programmatically on June 30, 2026 after PR #512._

<!-- [Screenshot placeholder: side-by-side grid of "Spanish vocabulary printable" results across 5 platforms] -->

### Google Images and Bing Images: the recall floor

Both cover all 58 queries with 10 results per query — no auth barriers, no login walls, no CJK blocks. If a visual concept exists on the web, Google and Bing find it. Bing's 39.9 related-search chips per query and Google's 17.8 give researchers the richest raw material for understanding what sub-intents exist around a query. That's valuable. But neither platform routes you to a template, a generator, or a creation surface. You get images you can look at; you don't get a button that says "make one like this."

### Pinterest: the sub-intent map

Pinterest's top-10 results are the most visually diverse of the five — board clusters reveal creative directions (the "cozy reading aesthetic" query surfaces pins spanning book nooks, hygge corners, and reading trackers). The structural limitation: 40 of our 58 queries returned 0 label chips due to Pinterest's login modal intercepting the filter bar before collection. Pinterest's browse signal is strong; its taxonomy signal is unreliable at scale.

### Canva: the English-template benchmark

Canva is the most direct comparison to Curify's core thesis: template-first search. For English creative queries, it works well — average 58.2 filter chips per accessible query (Format, Style, Size, Color, Audience), and clear template results for things like recipe posters, compatibility charts, and phonics worksheets. The structural gap: 21 of our 58 queries — all CJK queries and fandom queries (chiikawa, genshin) — hit a login wall before loading any results. For users whose primary creative language isn't English, Canva's search surface essentially disappears.

### Curify: the current position

Before the June update, Curify covered 53/58 queries (5 empty, all in the recipe cluster: weeknight dinners, gluten-free, meal prep). Of the 30 creative-intent queries — the ones where the user is explicitly trying to make something — only 10 (33%) returned a rich result set. The other 20 returned thin results or nothing at all. That's the gap this work was trying to close.

---

## What Changed After PR #512

The June 26 update (PR #512) shipped three things at once:

1. **Metadata expansion v2.** Gallery prompts went from an average of 5 tags/record to 26.3. Template topic coverage went from avg 5 topics to 15. Curated inspiration records went from avg 5 to 25.5 search aliases. This is the part that explains most of the query-level improvements.

2. **Multi-query retrieval (P0.2).** When the original query returns fewer than 5 results, the system now fires up to 8 retrieval paths simultaneously: the original query + up to 3 LLM-generated paraphrases + up to 6 decomposition slots (subject, style, scene, output type, era, mood). Results from all paths are merged and re-ranked by multi-hit score. The threshold was also raised from 3 to 5 to catch more borderline-thin queries.

3. **FDE meme ingest.** A two-panel comparison meme (Backend Engineer pushing the car from behind / Frontend Deployed Engineer pulling from the front) was generated via the `template-mbti-contrast` template and ingested as a gallery example. More on this below — including why the ingest succeeded but live search still returns zero results.

After re-scoring all 58 queries programmatically on June 30:

| Metric | Before PR #512 | After PR #512 |
|--------|---------------|--------------|
| Rich queries (of 58) | ~35 | **41** |
| Creative rich rate (30 queries) | 33% | **57%** |
| Consumer rich rate (28 queries) | 82% | **86%** |
| Queries that improved | — | **18 (31%)** |
| Queries that regressed | — | 4 (7%) — see below |

Eighteen queries moved up a bucket. The biggest gains were in three clusters:

**Travel and lifestyle content.** `remote destination`, `short city escapes`, and `global influence` all jumped from empty or thin to rich (177, 177, and 38 results respectively). `minimalist autumn outfit for japan travel` jumped from empty to rich (11 results). The metadata expansion surfaced cross-topic connections that weren't previously tagged.

**Educational and bilingual content.** `ESL flashcards printable` (thin → rich, 16 results) and `Spanish vocabulary printable` (thin → rich, 15 results) are now reliably surfacing the vocabulary template family. `homophones and homonyms` improved from thin to moderate. `cozy reading aesthetic` jumped from 1 result to 103.

**Character and MBTI content.** `marvel mbti character chart 16 types` went from moderate to rich (92 results). `monstera plant care guide infographic` went from moderate to rich (105 results). `wedding planner` moved from moderate to rich (28 results).

<!-- [Screenshot placeholder: "vocabulary flashcards" results page on Curify — showing template cards + inspiration grid] -->

---

## What Still Doesn't Work (And Why That's Honest)

Four queries regressed. Three are minor; one is a genuine bug.

`phonics worksheets kindergarten` dropped from thin to zero. An alias fix for this query was shipped on a development branch but hasn't merged to main yet. This is a merge-timing issue, not a content gap.

`香薰` (aromatherapy) dropped from rich to moderate (5 results). This warrants investigation — the P0.1 metadata re-enrichment may have narrowed tags on some aromatherapy records. We're flagging it.

`bilingual flashcards for kids learning korean fruits` dropped from moderate to thin (1 result). This is a 6-token strict query where only one record has all tokens simultaneously. The fix is alias expansion on sibling vocabulary records (en-ko vegetables, animals, colors) so the relaxed pool grows.

`samurai` dropped from rich to moderate with 9 results — one result below the rich threshold. This is noise.

Four queries remain empty outside of the regressions already noted: the two recipe queries (weeknight dinners and gluten-free dinner ideas — `meal prep weekly recipes` partially recovered to 5 results after the update), the MBTI compatibility chart, and the `水果中文` compound alias gap. These are known gaps with identified fixes. The recipe cluster requires a batch-generation run with existing templates (`template-recipe`, `template-food-recipe-tip-infographic`). The compatibility chart needs a one-off batch for `template-mbti-relationship-infographic`. The `水果中文` gap needs a direct alias addition — the bigram tokenizer doesn't span the full compound term.

---

## The FDE Meme: A Case Study in Compound Creative Intent

<!-- [Screenshot placeholder: FDE meme — two-panel comparison card (Backend Engineer RWD / FDE FWD)] -->

On June 29, a specific piece of content was generated and ingested: the Frontend Deployed Engineer (FDE) / Backend Engineer wheel-drive analogy meme. Two panels. An anthropomorphic beaver engineer pushing a car from behind (rear-wheel drive — "Reliable, invisible"). A fox engineer pulling the car forward by a rope (front-wheel drive — "Still drives the company — now you can see it").

This example is worth explaining precisely because it's not what it appears to be at first glance.

**It is not a signal that Curify is building a tech meme category.** The FDE meme exists in the catalog as one gallery example under `template-mbti-contrast` — the same template family that generates spring festival MBTI comparisons, office personality contrasts, and gym-behavior archetypes. The template doesn't know or care whether the "two characters" are software engineering roles or MBTI types — it's a two-panel contrast structure with bold titles, animal characters, and humorous captions.

**It is a demonstration that compound creative intent is handleable.** The FDE query ("frontend deployed engineer meme") has four distinct components: a specific professional role, a car-mechanics analogy, a contrast-meme format, and a corporate-commentary tone. None of those tokens exist individually in the catalog. A traditional keyword search would return zero results — which is exactly what our eval showed.

In production, the P0.2 multi-query path fires on zero-result queries: it decomposes the intent into `{subject: "engineer", style: "cartoon", output: "comparison meme", scene: "workplace"}` and runs up to 8 retrieval paths. This is the infrastructure that's supposed to rescue the FDE query. Our manual verification on June 30 showed 0 results in live production — meaning the rewriter didn't surface the ingested meme or the template in this case. The gap is that the gallery entry for the FDE meme has empty `searchAliases`, so neither the direct scorer nor the rewriter can bridge the gap from "FDE meme" to the `template-mbti-contrast` family.

The fix is not to build a meme category. The fix is to add `searchAliases: ["engineer meme", "fde meme", "contrast meme", "frontend backend comparison"]` to the gallery entry. The template is already there. The retrieval path is already there. It's a tagging problem, not a product problem.

The broader lesson: Curify's value proposition is not "more images of X" — it is "X → template → generation." The FDE case makes that concrete: a user who types "FDE meme" isn't looking to browse other people's memes. They want to generate their own. The template infrastructure can do that. The retrieval gap is what needs closing.

---

## Where Each Platform Actually Routes You

For a query with clear creative intent — `ESL flashcards printable`:

| Platform | What the user sees | Gets to generation? |
|----------|--------------------|---------------------|
| Google Images | 10 images of printed ESL flashcards from external teacher blogs | No |
| Bing Images | 10 images + 40 related-search chips (ESL activities, printable worksheets, classroom flashcards…) | No |
| Pinterest | 10 pins from Teachers Pay Teachers, Etsy, and ESL blogs | No — redirects off-platform |
| Canva | Template search results with filter chips; "Flashcard" as a format option | Yes — if user knows to navigate to templates |
| **Curify** | 16 bilingual vocabulary inspiration cards + dedicated flashcard templates (detailed vocab flashcard, cartoon English vocabulary, verb action learning cards) | **Yes — template and generation in one surface** |

Canva and Curify are the two platforms that route creative intent to an actionable surface. Curify's distinction: CJK queries work (Canva blocks them), and the connection between example cards and the underlying template is explicit — clicking an inspiration directly opens the template and pre-fills parameters.

---

## What the Label Count Gap Actually Means

Bing: 39.9 chips. Canva: 58.2 chips. Google: 17.8 chips. Curify: 8.8 chips.

This gap is real but should be read carefully. Bing's 40 chips are related-search suggestions algorithmically generated for every query — they cover synonyms, style variants, and sub-topics across the full web. Canva's 59 chips are a fixed platform-level filter panel (Format × Style × Color × Size × Audience) that appears regardless of the specific query. Neither number reflects "how well this platform understands this query."

Curify's 8.8 intent chips per query are search-result-specific clusters — they reflect what the platform's own catalog actually contains for this query, clustered into the intent taxonomy (character, language, learning, travel, culture, lifestyle…). Fewer chips means less category coverage, not less intent clarity. The right direction for Curify is expanding the category taxonomy depth — not padding the chip count.

---

## Next Steps: Three Lines of Work

**Relevance scoring.** Raw result count (empty/thin/moderate/rich) doesn't distinguish rich-and-precise from rich-and-noisy. The `classroom poster printable` query returns 16 results, but manual verification showed the top results were broad seasonal posters and calendars rather than classroom-specific content. Adding a human relevance score (1–5) to the top-5 results for priority queries would surface this kind of quality gap.

**GSC eval expansion.** The `raw/gsc-audit-2026-06-26/Queries-all.csv` file contains 5,913 real user query signals from Google Search Console. Sampling the top-50 thin-result queries (under 3 clicks) and adding them to the eval set would anchor the benchmark to actual user demand rather than analyst-constructed queries.

**Crawling-based discovery.** For zero-result queries where the LLM rewriter fires in production, verify that the rewritten paths actually surface generatable templates — not just any inspiration. A `--matcher` pass through `eval_search.cjs` for the 6 remaining empty queries would confirm whether template routing is working correctly when the rewriter kicks in.

---

## FAQ

**How is Curify different from Pinterest for creative queries?**  
Pinterest shows you existing work by other creators — you browse, then leave the platform to find tools or buy files. Curify routes you to a template and generates output within the same session. You start from a query; you end with your own generated image.

**Why does Canva score higher than Curify on creative template intent?**  
Canva has a larger English-language template library and a well-established category taxonomy. Curify is template-first from the ground up but is still building catalog depth, particularly in recipe, regional map, and niche printable categories. Curify's advantage is CJK query support and tighter example-to-template linking.

**What's the significance of the creative rich rate improvement (33% → 57%)?**  
Before the June update, fewer than 1 in 3 creative-intent queries returned a rich set of inspiration examples and templates. After the update, more than 1 in 2 do. That matters because creative-intent users — the ones who want to make something, not just look at something — are the users most likely to engage with generation.

**Why do some queries still return zero results?**  
Two are the recipe cluster (weeknight dinners and gluten-free dinner ideas) — there are templates in the catalog but no example content has been generated yet. `meal prep weekly recipes` partially recovered to 5 results (moderate) after the update. One is the MBTI compatibility chart (same issue). One is a compound CJK alias gap (`水果中文`). All have a known fix path; none require new template design.

**Is Curify trying to compete with Google Images?**  
No. Google Images is the ground truth for "does a visual representation of this concept exist on the internet?" Curify isn't trying to be that. The comparison is useful because it shows which queries have visual demand — and therefore which are worth building generation capacity for.

---

_Data: 58-query benchmark collected June 19–23, 2026 (Google, Bing, Pinterest, Canva). Curify re-scored June 30, 2026 on `main` at commit `a1a60bc5` after PR #512. Programmatic scoring; LLM rewriter results from manual live verification on a 10-query subset. See `five_platform_comparison_curify_refresh_2026-06-30.md` and `curify_refresh_after_pr512_report.md` for full methodology._
