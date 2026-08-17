# Reddit — FINAL

Based on `../REDDIT_DRAFTS.md` and `../REDDIT_COMMUNITY_RESEARCH.md`, re-verified against the
repository this session. All figures (318/1/7, 326/326, 12/68, human-review boundary) already matched
the corrected repo state in the source drafts — no factual correction was needed for Reddit copy this
pass, only repackaging into the `final/` structure with explicit posting-day banners.

---

## INTERNAL REVIEW NOTE — REMOVE BEFORE POSTING

Same caveat as the other two platforms: `main` on
`https://github.com/super-inbox/visual-search-benchmark` does not yet include the working branch's two
documentation-fix commits (`0cb6f07`, `cd2f5e4`). All three bodies below cite the corrected 318/1/7
breakdown, which currently only matches the working branch, not `main`. Sync `main` before posting, or
be ready for a reader to notice the repo still says "319" in three docs. See
`PUBLIC_RELEASE_FACT_SHEET_FINAL.md` §10–11. This note is informational only — no Reddit posting
action was taken this session, and this environment could not verify current subreddit rules (see
below).

**This session could not fetch live subreddit rules.** `WebFetch` to `reddit.com`/`old.reddit.com`
and a direct API `curl` were both blocked in the environment used to prepare `REDDIT_COMMUNITY_RESEARCH.md`.
Every "rules," "flair," and "karma" note below is drawn from each subreddit's long-standing public
conventions, not a rules page fetched today. Nothing in this file should be read as "current rules
already verified" — see the mandatory banner before each destination.

---

## Summary table

| Community | Recommended format | Standalone post? | Required manual check |
|---|---|---|---|
| r/datasets | Title + link post | Yes | Current flair options, minimum account age/karma, link-post frequency cap |
| r/computervision | Title + link post (or top-level comment with link, if the sub currently prefers that for dataset shares) | Yes | Current flair options, current stance on link-posts vs. comment-with-link format |
| r/MachineLearning | Comment inside the current self-promotion thread | **No** — comment only, not a standalone submission | Whether the self-promotion thread still exists in its current form, and whether this content is currently permitted there at all |

---

## 1. r/datasets (standalone post)

### POSTING-DAY ACTION REQUIRED:
Manually verify the current subreddit rules, flair requirements, account/karma restrictions, and
link-post policy before posting.

**Recommended flair:** whatever this subreddit's current flair options offer for a dataset release
(e.g. "Dataset" / "Resource") — verify the current flair list before posting; do not guess a flair
name that doesn't exist.

#### COPY-READY TITLE

```
[Dataset] Visual/design search eval data — 68-query + 326-query, with real search-page screenshots and documented limitations
```

#### COPY-READY BODY

> Sharing two internal search-evaluation datasets from work on a visual/design search product
> (Curify), converted for public release.
>
> - **68-query benchmark:** 68 hand-curated queries, LLM-judged relevance labels (Claude, single
>   pass). For 12 of the 68, real screenshots across 5 platforms (Curify/Bing/Google
>   Images/Canva/Pinterest) — same query, different platforms, actual result pages, with an offline
>   filterable gallery.
> - **326-query benchmark:** 326 queries (163 zh / 163 en), used to regression-test two states of the
>   same search pipeline (production baseline vs. a candidate branch). All 326 queries also have real
>   screenshot evidence from Google Images and from the product's own search — 652 screenshots, two
>   more offline galleries.
>
> Schema docs, source-file SHA-256 hashes, and a validator script (`scripts/validate_data.py`,
> `scripts/validate_benchmark.py`) are included, and both currently pass. We documented what's *not*
> here rather than smoothing it over: neither dataset includes completed human review (both use an
> LLM judge only), the 68-query image coverage is 12 of 68 queries (not all 68), the screenshot
> evidence added to the 326-query set is unscored — no relevance judgment was generated from it — and
> the 326-query candidate branch was explicitly not approved for production at capture time.
>
> Licensing is split: query/label/schema data and the product's own screenshots are CC BY 4.0; the
> third-party platform screenshots (Bing/Google/Canva/Pinterest, and the 326-query Google Images set)
> are included as evidence only, not relicensed for reuse or training.
>
> Repo: https://github.com/super-inbox/visual-search-benchmark

#### COPY-READY DISCLOSURE

```
Disclosure: I worked on assembling and validating this benchmark.
```

#### Discussion question

Is a per-record provenance field (source-file hash, capture method, an explicit confidence rating like
`confirmed`/`probable`/`unknown` on image-to-query mappings) useful in datasets you've used, or is it
more overhead than most consumers actually check? Interested in what a "good provenance" bar looks
like from people who reuse third-party eval data regularly.

#### Link placement

Repo link once, at the end of the body. Not repeated in the title, not posted separately as a comment.

---

## 2. r/computervision (standalone post)

### POSTING-DAY ACTION REQUIRED:
Manually verify the current subreddit rules, flair requirements, account/karma restrictions, and
link-post policy before posting.

**Recommended flair:** whatever this subreddit's current flair set offers for a
dataset/resource/project share — verify before posting.

#### COPY-READY TITLE

```
Visual search benchmark with real cross-platform screenshots (Curify/Bing/Google/Canva/Pinterest) and full 326-query Google Images + product screenshot coverage
```

#### COPY-READY BODY

> Not a model release — an evaluation-data release, might be useful if you do multimodal/visual
> retrieval work.
>
> The core idea: most public search-quality data is either a query list with no visible output, or an
> aggregate score with no way to see what actually happened. Here we tied together, wherever the
> source data allowed: the query text, which platform, what that platform's page actually looked like
> (a real screenshot, not a description), and — where one exists — a relevance label with a written
> reason.
>
> - 68 curated queries, with real screenshots from 5 platforms (Curify/Bing/Google
>   Images/Canva/Pinterest) for 12 of the 68 — full-page captures, so there's no per-result rank field
>   (we don't invent one where the source data doesn't have it). Offline gallery, filter by
>   query/platform/label/mapping-confidence.
> - A separate 326-query set (bilingual, zh/en) regression-testing two code states of the same search
>   pipeline, now with a real Google Images screenshot *and* a real product-search screenshot for
>   every one of the 326 queries — 652 screenshots total. This half is unscored: real evidence of what
>   each surface returned, no relevance judgment generated from it, no cross-platform ranking implied.
>
> Explicitly out of scope: this is not a scored cross-platform comparison anywhere in the release —
> only one product's own search has per-query relevance labels, and those come from an LLM judge, not
> completed human review.
>
> Repo: https://github.com/super-inbox/visual-search-benchmark

#### COPY-READY DISCLOSURE

```
Disclosure: I worked on assembling and validating this benchmark.
```

#### Discussion question

For people doing cross-platform visual retrieval eval — is unscored, side-by-side screenshot evidence
(query → platform → actual result page, no score) useful on its own as a qualitative check, or does it
only become useful once someone adds a scoring pass on top? Curious whether the gallery/manifest
format here would be reusable for that.

#### Link placement

Repo link once, at the end of the body.

---

## 3. r/MachineLearning (self-promotion-thread comment — not a standalone post)

### POSTING-DAY ACTION REQUIRED:
Manually verify that r/MachineLearning's current self-promotion thread still exists in its current
form, and that a comment of this kind is currently permitted there, before posting.

Per `REDDIT_COMMUNITY_RESEARCH.md`, r/MachineLearning's norms are stricter about standalone
announcement-shaped posts; this is written as a **comment**, sized for posting inside that subreddit's
current self-promotion thread, not as a submission of its own. If no compliant destination exists on
posting day, skip r/MachineLearning this round rather than force a fit.

#### COPY-READY COMMENT

> Disclosure: I worked on assembling and validating this benchmark.
>
> Published two internal search-relevance eval datasets (68-query + 326-query, visual/design search
> product) with real search-page screenshots alongside the query/label data, not just aggregate
> scores. Newest part: the 326-query set now has a real Google Images screenshot and a real
> product-search screenshot for all 326 queries (previously had none) — unscored evidence, not a new
> evaluation; the only scored data in the release is a production-vs-candidate regression comparison
> on the product's own search, LLM-judged (`gpt-4o-mini`, deterministic rubric), not human-reviewed.
> Source hashes, schema docs, and a validator script included; known limitations (partial image
> coverage on the 68-query set, no human review either way, candidate branch not production-approved)
> are documented rather than glossed over.
>
> Curious whether people building/consuming eval datasets find LLM-judge-only labels (no human review
> layer) usable as-is, or consider that disqualifying without a human pass on top — genuinely
> unresolved question for us. Repo: https://github.com/super-inbox/visual-search-benchmark

**Recommended flair:** N/A — posted as a comment inside an existing thread, not a new submission.

#### Discussion question

(embedded above) LLM-judge-only labels — usable as-is, or not, without a human-review layer.

#### Link placement

Repo link once, at the end of the comment.

---

## Cross-community rules

- All three bodies are written separately for their community — none of the three are the same text
  reused; each leads with a different framing (provenance/documentation rigor for r/datasets,
  multimodal/retrieval-research fit for r/computervision, methodology-question framing for the
  r/MachineLearning comment).
- Do not post the three on the same day as a batch — space them out (see
  `SUMMARY_FINAL_ZH.md` §6 for the recommended sequencing) to avoid reading as coordinated
  spam across subreddits.
- Do not claim, in any of the three, that current subreddit rules have been checked in this session —
  they have not. Each destination's "POSTING-DAY ACTION REQUIRED" banner above is mandatory, not
  boilerplate.
