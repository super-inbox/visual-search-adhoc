# LinkedIn Post — Curify Visual Search Benchmark

---

We benchmarked 5 visual search platforms across 58 queries. Here's the honest result.

**Platforms tested:** Google Images, Bing Images, Pinterest, Canva, Curify  
**Query set:** 30 creative intent + 28 consumer browsing — spanning English, CJK, and bilingual educational content

---

**The gap that matters isn't recall. It's routing.**

Google and Bing returned results for all 58 queries. Pinterest too. But none of them answer the question a creative user actually has: *can I make one of these?*

Canva and Curify are the two platforms that route search to a generative surface. The difference:

- Canva blocked 21/58 queries (all CJK queries, all fandom queries) behind a login wall
- Curify imposes no auth barrier on any query — though 6 queries still return zero results due to catalog gaps (recipe content not yet generated, one alias gap), not access restrictions. Where results exist, they link directly to the template that generated them.

---

**What changed after our latest search infrastructure update (PR #512):**

Before: creative-intent queries returning rich results = **33%** (10/30)  
After: **57%** (17/30) — a 24-point jump

18 of 58 queries improved. The biggest gains: ESL flashcards (thin → rich), Spanish vocabulary (thin → rich), travel lifestyle content (empty → rich across multiple clusters).

4 queries regressed — we listed them publicly, with root causes and fix plans.

---

**The counter-intuitive finding on label counts:**

Bing: 39.9 chips/query. Canva: 58.2. Curify: 8.8.

Curify's lower number isn't a gap in intent understanding — it's a reflection of what's actually in the catalog. Bing's 40 chips are web-wide suggestions; Canva's 59 are a static filter panel. Curify's 8.8 are specific to what exists in the platform. The right response isn't to pad the chip count — it's to expand catalog depth.

---

**One case study that crystallized the whole thesis:**

The "FDE meme" query — Frontend Deployed Engineer / Backend Engineer wheel-drive comparison — still returns zero results in production as of June 30. This is a live failure, not a hypothetical. The content was generated and ingested (via our contrast-meme template). The multi-query rewriter fires on zero-result queries. None of that helped. The gap: the gallery entry has no search aliases, so neither the direct scorer nor the rewriter can bridge "FDE meme" to the `template-mbti-contrast` family. The template infrastructure is there. The retrieval path is there. It's a tagging problem.

That's the simplest possible statement of where this kind of search breaks down: not architecture, not content, not infrastructure. Metadata.

---

**Next: relevance scoring (not just recall), GSC query expansion (5,913 real user signals), template routing verification for zero-result queries.**

Full benchmark data and methodology in the comments.

---

*External platform data (Google, Bing, Pinterest, Canva) collected June 19–23, 2026 — not re-crawled. Curify re-scored programmatically June 30, 2026 on main after PR #512.*

#VisualSearch #CreativeAI #SearchEngineering #ProductInsights #Curify
