# Content Revision Note — Blog & LinkedIn Public v2
**Date:** 2026-07-02
**Purpose:** Record what was preserved, moved to internal-only, or removed when rewriting the original blog_draft.md and linkedin_post.md into public-facing v2 versions.

---

## Files Created

| File | Purpose |
|---|---|
| `blog_public_v2.md` | Rewritten public-facing blog post |
| `linkedin_public_v2.md` | Rewritten LinkedIn post |
| `content_revision_note.md` | This file — internal revision record |

Original files **blog_draft.md** and **linkedin_post.md** are preserved untouched as internal reference material.

---

## What Was Preserved in v2

| Content | Source | Destination in v2 |
|---|---|---|
| 58-query pilot scope and framing | EXTERNAL_SIGNAL_INSIGHTS_2026-06-23_zh.md §0, §2 | blog §1, §2 |
| Topic category distribution table (8 categories, counts, share %) | EXTERNAL_SIGNAL_INSIGHTS_zh.md §3.1 | blog §2 |
| Consumption / creation / mixed split (25/26/7 queries) | EXTERNAL_SIGNAL_INSIGHTS_zh.md §3.2 | blog §2 |
| Visual search spectrum diagram | EXTERNAL_SIGNAL_INSIGHTS_zh.md §7.2 | blog §3, LinkedIn |
| Platform star rating table (5 platforms × 5 dimensions) | EXTERNAL_SIGNAL_INSIGHTS_zh.md §5 | blog §4, LinkedIn |
| Bing avg 39.9 label chips, Google avg 17.8 label chips | label-count-statistics-report-2026-06-23.md; blog_draft.md | blog §5, LinkedIn |
| Pinterest One Bar sub-intent chip examples (monstera, weeknight dinners, samurai, chiikawa, 香薰) | EXTERNAL_SIGNAL_INSIGHTS_zh.md §6.4 | blog §5 |
| Pinterest: 36/58 queries with chips, avg 19.9 chips (non-zero), 12.4 overall | EXTERNAL_SIGNAL_INSIGHTS_zh.md §5, §6.4 | blog §5 |
| Canva: 21/58 CJK login block, avg 43 chips for accessible queries | blog_draft.md; EXTERNAL_SIGNAL_INSIGHTS_zh.md §6.5 | blog §5, LinkedIn |
| Curify: 54/58 results, strong on vocabulary/IP queries, 8-cluster chip system | EXTERNAL_SIGNAL_INSIGHTS_zh.md §6.1; blog_draft.md | blog §5 |
| Case study — "ESL flashcards printable" routing comparison table | blog_draft.md (§ "Where Each Platform Actually Routes You") | blog §6, LinkedIn |
| Case study — "monstera plant care guide infographic" Pinterest chip discovery | EXTERNAL_SIGNAL_INSIGHTS_zh.md §6.4 | blog §7 |
| Label count gap explanation (what Bing/Canva/Google chips actually mean vs Curify) | blog_draft.md (§ "What the Label Count Gap Actually Means") | blog §5 (condensed, reframed as external signal insight) |
| Pilot limitations | EXTERNAL_SIGNAL_INSIGHTS_zh.md §10.3 | blog §9 |
| Platform signal recommendation table (best platform by signal need) | EXTERNAL_SIGNAL_INSIGHTS_zh.md §7.1 | blog §8 |

---

## What Was Moved to Internal Only (not in v2)

These sections exist in the original drafts and should remain available as internal reference material, but are not appropriate for a public-facing post.

| Content | Reason | Where it lives now |
|---|---|---|
| "What Changed After PR #512" — full section with before/after metrics table | References a specific internal code PR; not meaningful to public readers | blog_draft.md (internal) |
| "What Still Doesn't Work (And Why That's Honest)" | Internal gap/deficiency framing; signals unresolved production issues | blog_draft.md (internal) |
| FDE meme case study ("Frontend Deployed Engineer" / "Backend Engineer" comparison) | Internal engineering example; too niche and jargon-heavy for public post | blog_draft.md (internal) |
| Regression analysis (4 queries that regressed, root causes, fix plans) | Internal QA content; not public-facing | blog_draft.md (internal) |
| P0/P1/P2/P3 gap severity breakdown table | Internal gap classification system; not meaningful without context | EXTERNAL_SIGNAL_INSIGHTS_zh.md §8.3 (internal) |
| Curify internal alias fixes, alias expansion plans, tokenizer details | Engineering implementation details | blog_draft.md (internal) |
| "GSC eval expansion" and "crawling-based discovery" next steps | Internal roadmap; references internal file paths and systems | blog_draft.md (internal) |
| Programmatic scoring methodology, eval_search.cjs references | Too technical for public blog | blog_source_inventory.md (internal) |
| LinkedIn references to PR #512, FDE meme, alias tagging | Not appropriate for public LinkedIn | linkedin_post.md (internal draft preserved) |

---

## What Was Removed (not preserved anywhere in public content)

These items were removed even from internal notes because they are too version-specific or too low-level to carry forward.

| Content | Reason |
|---|---|
| Specific commit hash references (e.g., `a1a60bc5`) | Too internal / version-specific; no public meaning |
| "Curify re-scored on main at commit …" phrasing | Internal CI artifact reference |
| `水果中文` bigram tokenizer gap detail | Internal tokenizer implementation detail |
| `searchAliases: []` fix instruction (FDE meme tagging task) | Internal task item, not an insight |
| References to internal file paths (`eval_search.cjs`, `nano_inspiration.json`, `search_eval_set.json`) | Internal engineering artifacts |

---

## What Was Added or Reframed in v2

| Content | What changed |
|---|---|
| Pilot scope framing ("not a rigorous full benchmark") | Added explicitly per boss feedback; mirrors EXTERNAL_SIGNAL_INSIGHTS_zh.md §0 disclaimer |
| "What This Is (and Isn't)" opening section | New; replaces the "Problem with Visual Search Benchmarks" framing which leaned too internal |
| "What This Means for Visual Search Strategy" closing section | Synthesized from EXTERNAL_SIGNAL_INSIGHTS_zh.md §7 and §8.2; reframed as external insight rather than Curify-specific recommendations |
| Platform signal recommendation table (§8 in blog) | Adapted from EXTERNAL_SIGNAL_INSIGHTS_zh.md §7.1 into English and external-facing framing |
| Case Study 2 — "monstera plant care guide infographic" | New case study; added to show Pinterest sub-intent chips in action (was in internal report but not in blog_draft.md) |
| Image TODO table | New; minimal placeholder section to track what images are needed for next step |
| LinkedIn star rating table | New addition to LinkedIn post — summarizes the key comparative data concisely |

---

## Image Needs for Next Step

All image collection deferred. Placeholders are in place in blog_public_v2.md. No CDN work, no uploads.

| Image | Query | Platform(s) | Priority |
|---|---|---|---|
| Label chip bar + top image results | ESL flashcards printable | Google Images | High |
| Label chip bar + top image results | ESL flashcards printable | Bing Images | High |
| One Bar sub-intent chip row + pin grid | monstera plant care guide infographic | Pinterest | High |
| Template grid with filter label chips | phonics worksheets kindergarten | Canva | Medium |
| Result grid with intent label chips | ESL flashcards printable | Curify | High |
| Full Case Study 1 set | ESL flashcards printable | Google / Pinterest / Canva / Curify | High |
| Pinterest chip bar for Case Study 2 | monstera plant care guide infographic | Pinterest | Medium |

Recommendation for collection: take fresh screenshots — the June 2026 pilot screenshots may not match current platform UIs, and Canva/Pinterest UIs change frequently.
