# Targeted Case Analysis — scorer v1.1 (candidate) vs current production main (baseline)

All top-5 lists below are the real server-computed `inspirations` order from the RSC flight payload
(`collector.mjs`), collected live 2026-07-21. Labels/scores are actual `gpt-4o-mini` rubric-v1.1 judgments
from the full-326 run (all 9 queries are in the bank). Rewrites shown are the `usedRewrites` the server reported;
they are cached per-server and were verified deterministic across repeat samples.

## Case 1 — 笔袋 (pencil case) — THE FLAGSHIP FIX TARGET — **NOT FIXED (regressed)**

| | baseline (main) | candidate (v1.1) |
|---|---|---|
| label / score | PARTIAL / 0 | **FAIL / 0** |
| total results | 17 | 8 |
| rewrites | pencil case, stationery pouch, writing utensil holder | pencil case, stationery pouch, writing tools bag |

Baseline top-5: `microsoft ai dilemma…gemini`, `microsoft ai dilemma…gemini`, **`Stationery`**, `label printer`, **`en-zh`** (stationery flashcards)
Candidate top-5: **`western1`**, **`western2`**, `microsoft ai dilemma…gemini`, `microsoft ai dilemma…gemini`, **`Stationery`**

v1.1 did prune the tail (17→8), but the top of the result is **worse**: two western-food sticker templates
(`western1`, `western2`, template `template-food-photo-doodle-sticker-overlay`) were promoted to **#1–#2**, pushing
the one genuinely on-subject item (`Stationery`) from #3 down to #5. The judge scored 4 of 5 irrelevant → FAIL,
a drop from baseline PARTIAL. The en twin `pencil case` regressed identically (PARTIAL/27 → FAIL/0, 21→3 results).

**Why the food template matches at all (catalog-verified):** `template-food-photo-doodle-sticker-overlay-western1`
contains **no `笔` character anywhere**; its only 袋-related content is `search_aliases[47] = "帆布袋设计"`
(*canvas tote-bag design*). The query 笔袋's single bigram is the whole string `笔袋`, which does **not** substring-match
`帆布袋设计` — so this item **cannot** have come from the original-query path. It is a **non-original (rewrite/decomposition)
candidate**. For it to rank #1 it must have a large positive `final_score`, which is only possible if `subjectPresent`
evaluated **true** (otherwise `missing_subject_penalty −15` + `NON_ORIGINAL_OFFSUBJECT_EXTRA_PENALTY −10` would drive it
below the −5 inclusion floor and it would be excluded). So the exact mechanism v1.1 added — the −10 off-subject demotion
and the result-rich gate — **did not fire** on this off-subject non-original candidate, because it was treated as
subject-present. This is the Step-6 residual risk manifesting live (see §Residual Risk below).
*(The specific token that flipped `subjectPresent` true could not be confirmed without instrumenting the frozen
worktree; the above chain — non-original, subject-present-by-inference — rests on the ranking arithmetic and catalog
cross-reference, and is disclosed as inference.)*

**Verdict: the 笔袋-class regression is NOT fixed. It is worse than current main.**

## Case 2 — 促销海报 (promotional poster) — result-count gate benign, **OK**

| | baseline | candidate |
|---|---|---|
| label / score | PARTIAL / 42 | **PASS / 65** |
| total / paths | 10 / 1 | 10 / 1 |

Both return the same 10 promotional-poster items (all tagged `promotional-poster`; all on-subject) — the candidate
merely re-orders (`tech gadget sale`, two `Chinese` promo posters, `baby care brand`, `spring beauty festival`…).
There are **no non-original candidates** here (paths=1, no rewrite), so `RESULT_RICH_MIN_ONSUBJECT=8` has nothing
off-subject to prune; it does **not** over-filter — count stays 10 and every item remains valid. Label improved
PARTIAL→PASS. The result-count-aware gate behaves as intended (does not shrink a valid result set).

## Case 3 — 拼读卡 (phonics/spelling cards) — no over-filtering, **OK**

| | baseline | candidate |
|---|---|---|
| label | UNJUDGABLE | UNJUDGABLE |
| total / paths | 19 / 6 | **29 / 6** |

Candidate returns **more** results (29 vs 19) with an identical relevant top-6 (`apple`, `book`, `dog`,
`high speed rail`, `school timetable`, `animal learning card…` — bilingual kids-learning vocabulary cards). The
stricter v1.1 gate did **not** over-prune this thin-ish query. (Both sides judged UNJUDGABLE: the vocabulary-card
titles/tags give the text-only judge no signal to separate "phonics card" from generic bilingual learning cards —
a judging-signal limitation, not a retrieval regression.)

---

## Preserved-wins validation (candidate vs current main)

| query | baseline | candidate | outcome |
|---|---|---|---|
| 电影海报 (movie poster) | FAIL / 0 | **PASS / 100** | improved — candidate returns 5/5 film posters (forrest gump, la la land, titanic, casablanca, gone with the wind); baseline top was 4/5 Chinese-**food** items |
| sticker pack | PARTIAL / 24 | **PASS / 95** | improved — candidate 5/5 literal meme/character sticker packs |
| product photo | FAIL / 0 | **PASS / 100** | improved — candidate 5/5 product-**packaging** photos (oats, cookies, pasta sauce, coffee beans); baseline top was raw produce guides |
| logo | FAIL / 0 | **PASS / 57** | improved — candidate 4/5 brand-identity/logo mockups; baseline top was anime-studio "X vs Y" infographics |
| 日历 (calendar) | FAIL / 0 | **PASS / 32** | improved — candidate skews to event schedules + a `chiikawa 2026` calendar; baseline top was sports-event posters |
| **人体图解 (human-body diagram)** | **PASS / 67** | **FAIL / 0** | **REGRESSED** — see below |

**5 of 6 preserved-wins are retained/improved.** Note the current-main baseline had *lost* most of these wins
(they read FAIL on main because main is pre-scorer); the candidate restores them — direct evidence the unified
scorer's merch/promo/product-poster improvements are real and re-added on top of current production.

### 人体图解 — preserved-win **REGRESSED PASS→FAIL**

Baseline top-5: `human brain usage`, `human body bilingual science mindmap`, `human body`, `body parts`, `sleep disorder guide` — 5/5 human-body anatomy (but 303 results = flooded).
Candidate top-5: `human body`, **`empire state building`**, **`giant wild goose pagoda`**, **`national stadium (bird nest)`**, **`oriental pearl tower`** — #1 correct, #2–#5 are **architecture** infographics.

v1.1 cut the flooding (303→164) but its re-ranking promoted building "anatomy/infographic" templates (they carry an
`anatomy` tag) above genuine human-body content, giving 4/5 irrelevant → FAIL. A concrete case where the new scoring
trades flooding reduction for a top-of-list precision loss on a query current main gets right.

---

## Step 6 — `subjectPresent` residual risk (single-token CJK) — CONFIRMED MANIFESTING

Code under review: `app/[locale]/(public)/search/page.tsx` L594–605 (`deriveFieldHits`). For a single-token query
(`originalPrimaryTokens.length <= 1`, true for standalone CJK terms like 笔袋 / 日历 / logo), the code sets
`subjectPresent = titleHit || tagsHit`, where `tagsHit = tagsScore.allPrimary || tagsScore.bigramHits > 0`
(L568). So a CJK **bigram/substring-only** hit in the tags blob — with no true whole-token hit — is sufficient to
satisfy `subjectPresent`, which is exactly the signal `NON_ORIGINAL_OFFSUBJECT_EXTRA_PENALTY` and
`selectFinalCandidates`'s rich-gate rely on to drop off-subject non-original candidates.

**Live manifestation (笔袋, disclosed inference):** the western-food template that ranks #1 for 笔袋 carries no whole
`笔袋` token and no `笔` character; its only 袋-content is the alias `帆布袋设计` (canvas tote bag). It is a
non-original candidate (cannot come from the original path — the `笔袋` bigram does not substring-match the alias),
yet its large positive final score proves `subjectPresent` was satisfied and the −10 off-subject demotion never
applied — the off-subject non-original candidate a whole-token subject gate would have dropped. This is the residual
risk in practice: for single-token CJK queries, tag-substring evidence alone is treated as subject presence, so v1.1's
off-subject penalty and rich-gate can be bypassed. **Not fixed here (per charter, no fix implemented) — documented as a
required follow-up.** The precise triggering token was not directly instrumented (frozen worktree); the conclusion is
inferred from the ranking arithmetic + catalog record and is disclosed as such.
