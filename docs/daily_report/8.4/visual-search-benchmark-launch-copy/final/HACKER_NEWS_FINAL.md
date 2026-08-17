# Hacker News — FINAL

Based on `../HACKER_NEWS_DRAFT.md`, re-verified against the repository this session and corrected
where the draft's wording was no longer accurate. One substantive fix: Q2 ("are the relevance labels
human-reviewed?") previously answered "An internal human-review pass exists for both [benchmarks],"
which is imprecise for the 68-query set (no pass was ever completed there, not merely withheld) — see
the corrected answer below.

---

## INTERNAL REVIEW NOTE — REMOVE BEFORE POSTING

`main` on `https://github.com/super-inbox/visual-search-benchmark` does **not** yet contain the two
documentation-fix commits (`0cb6f07`, `cd2f5e4`) that corrected the 326-query Curify page-type count
from a buggy "319 standard search-results pages" to the correct "318 standard / 1 zero-result / 7
topic-redirect." Those fixes exist only on the working branch
(`baobao/publish-visual-search-benchmarks-2026-07-30`) right now. The copy-ready sections below
already use the correct 318/1/7 figures. **If this post goes out before `main` is synced, a reader
who clicks through will land on a repo page that still says "319" in three places — sync `main` first,
or expect this discrepancy to be visible and be ready to explain it in a reply.** This is a
boss/repo-maintainer decision, not something resolved by this drafting pass. See
`PUBLIC_RELEASE_FACT_SHEET_FINAL.md` §10–11.

---

## 1. Title options (5)

1. `Show HN: Visual search benchmark with screenshot evidence for all 326 queries`
2. `Show HN: We published search-eval data with real screenshots, not just scores`
3. `Show HN: A search-relevance benchmark that shows the actual result page, not a summary`
4. `Show HN: 394 queries, real search screenshots, and a documented LLM-judge rubric`
5. `Show HN: Two visual-search eval datasets, published with source hashes and known limitations`

## 2. Recommended title

**#1 — `Show HN: Visual search benchmark with screenshot evidence for all 326 queries`**

Re-confirmed this session: 326/326 Google Images and 326/326 Curify screenshot coverage for the
326-query set is accurate and current. This title names the single most concrete, verifiable fact
instead of an adjective, and doesn't require the reader to already know what "search-relevance
benchmark" means before clicking.

## 3. Show HN vs. regular submission

**Use Show HN.** This is something the team built and is presenting for feedback (a dataset, a
gallery UI, a validator script, a provenance/hash methodology) — exactly what Show HN is for, per HN's
own guidelines. It is not news and not commentary on someone else's work.

---

## COPY-READY TITLE

```
Show HN: Visual search benchmark with screenshot evidence for all 326 queries
```

## COPY-READY BODY

> We publish internal search-quality data as two datasets, not a summary post.
>
> **68-query benchmark:** 68 hand-curated queries testing our own visual/design search
> (`curify-ai.com/search`), LLM-judged (Claude, single pass). For 12 of those 68 queries we also have
> real screenshots from Curify, Bing Images, Google Images, Canva, and Pinterest — same query, five
> platforms, actual pages. Offline gallery included, opens locally with no server.
>
> **326-query benchmark:** 326 queries (163 Chinese / 163 English) used to regression-test two code
> states of our search pipeline — a production baseline and a candidate branch. Every one of the 326
> queries also has a real, unedited screenshot from Google Images and from Curify's own search — 652
> screenshots total, two offline galleries.
>
> The screenshots are evidence, not a new evaluation. No relevance judgment, ranking, or score was
> generated from either screenshot set — the only scored data in this release is the 326-query
> `evaluations.csv` (production baseline vs. candidate, Curify only), and it wasn't touched or re-run
> for the screenshot addition. If you're looking for a cross-platform score, it isn't here on
> purpose — we didn't want to publish a number we can't stand behind.
>
> We also tried to be specific about what's incomplete rather than rounding it off: the 68-query image
> evidence covers 12 of 68 queries, not all 68 (a real limit of the source data). Neither benchmark has
> completed human review in this release — both use an LLM judge, and we say so directly rather than
> implying otherwise. The 326-query candidate branch was explicitly not approved for production at the
> time it was captured; treat it as a regression snapshot, not a claim about current production
> quality. Full rubric, source hashes, and known-limitations list are in the repo (`METHODOLOGY.md`,
> `SOURCE_AUDIT.md`, `VALIDATION_REPORT.md`).
>
> Question for HN: for people who've published eval/benchmark data before — is per-record source
> provenance (hash of the originating internal file, capture method, confidence field) worth the
> overhead we put into it, or is that more rigor than most consumers of a dataset actually use? Also
> genuinely curious whether anyone has a cleaner way to license third-party screenshot evidence (ours
> are evidence-only, not CC BY, since we don't own the underlying platforms' content) than what we
> landed on.
>
> Repo: https://github.com/super-inbox/visual-search-benchmark

## COPY-READY FIRST COMMENT

Post immediately after submission.

> A few things worth stating up front since they'd come up anyway:
>
> - The Curify screenshots for the 326-query set aren't all literal search-results pages: 318 are
>   standard `/search?q=...` results, 1 is a genuine zero-result page, and 7 are Curify's own
>   deterministic redirect to a `/topics/...` category page for certain single generic words (e.g.
>   "logo," "map"). Each of the 7 is explicitly tagged as a redirect in the manifest, not folded into
>   the "normal" count.
> - The Google Images screenshots are a single first-viewport capture per query (not scrolled, not
>   cropped to one result), so there's no per-result rank recorded — we didn't invent one. No CAPTCHA
>   or unresolved consent wall shows up in any of the 326 published Google Images captures.
> - The 12-query image subset in the 68-query benchmark happens to be all cases where our own search
>   already failed. That's because that pilot was scoped to already-flagged problem queries, not
>   because we only published failures — the full 68-query label distribution (43 FAIL / 25 WARN / 0
>   PASS) is in the CSV, unfiltered.
> - License: query/label/schema data and Curify's own screenshots are CC BY 4.0. The third-party
>   screenshots (Bing/Google/Canva/Pinterest in the 68-query set, Google Images in the 326-query set)
>   are included as evidence only — not relicensed, not free to redistribute or train on.

---

## 4. Frequently asked questions and answers

**Q1: Is this a benchmark showing Curify beats Google/Bing/Pinterest/Canva?**
No. No platform other than Curify has a scored, ranked result anywhere in this release. The
non-Curify screenshots are visual evidence (what that platform's page actually looked like for that
query) with no numeric label attached. The only scored comparison in this release is Curify's own
production baseline vs. a candidate branch on the 326-query set — a regression test of our own
pipeline, not a cross-platform ranking.

**Q2: Are the relevance labels human-reviewed?** *(corrected this pass — see note above)*
No. For the 68-query benchmark, a human-review rubric and spreadsheet were prepared, but no human
reviewer completed the pass — the label column you see is entirely LLM output. For the 326-query
benchmark, an internal human-verification pass exists but is not included in this public release. In
neither case should the published labels be read as human-reviewed ground truth.

**Q3: Why isn't the 326-query set fully cross-platform if you already collected Google Images
screenshots for it?**
The Google Images and Curify screenshots are real, but they're unscored — we didn't generate a
relevance judgment for Google Images, so publishing them as a "cross-platform comparison" would
overstate what we actually did. We'd rather ship the screenshots honestly labeled as evidence than
delay the release until we could score them properly (or not ship them at all).

**Q4: What happened with the 7 "topic redirect" queries — did you force those results?**
No. Those 7 single-word queries (e.g. "logo," "map") trigger Curify's own client-side redirect away
from the search-results page to a topic-category page — that's real product behavior, not something
our collector caused or worked around. We captured the actual page the redirect lands on and tagged
it distinctly (`page_type=topic_redirect`) rather than either dropping those 7 queries or presenting
the redirect page as if it were a normal search-results page.

**Q5: Did the automated collection run into problems — CAPTCHAs, blocks, anything like that?**
Not in what's published. The Google Images manifest records `consent_detected=false` and
`captcha_detected=false` on all 326 rows — no CAPTCHA or consent wall appears anywhere in the
published evidence. What we did hit: a 45-second navigation timeout per attempt, and a detection race
between "results loaded" and "zero-results text appeared" that occasionally needed a retry — both
resolved by retrying, never by bypassing or faking a result.

**Q6: Is any of this data going to be kept up to date, or is it a one-time snapshot?**
One-time, point-in-time snapshots — the 68-query set from 2026-07-07, the 326-query evaluations from
2026-07-21/22, and the screenshot evidence from 2026-08-01/03. Live Curify (or Google) search will
have changed since. We're not committing to a refresh cadence with this release; if we do a follow-up
capture later we'll publish it as a new dated snapshot rather than overwriting this one.

## 5. Marketing language that must not appear

Do not use, in the title, body, or any comment: revolutionary, groundbreaking, game-changing,
best-in-class, best, state of the art / SOTA, first (of its kind), largest, industry-leading,
world-class, cutting-edge, disruptive, next-generation, unparalleled, unmatched. No exclamation points
anywhere. Do not describe Curify as beating, outperforming, or being superior to any other platform
named in this dataset (Google, Bing, Pinterest, Canva) — no scored comparison against any of them
exists in this release.

## 6. Pre-publish checklist for this post specifically

- [ ] Confirm `main` has been synced with `0cb6f07`/`cd2f5e4` (or accept and be ready to explain the
      "319 vs. 318" discrepancy a reader would see if not) — see the internal review note above.
- [ ] Boss sign-off on this exact title + body + first comment.
- [ ] Post the first comment immediately after submission, not hours later.
- [ ] Re-read Q1–Q6 once more right before submitting in case anything in the repo changed since this
      draft was finalized.
