# LinkedIn — FINAL

Based on `../LINKEDIN_DRAFTS.md`, re-verified against the repository this session. One substantive
correction: the personal version's original claim that "Browser-automation captures hit CAPTCHAs,
consent walls, network drops" is **not supported** by the published data —
`data/326-query/google-images/manifest.csv` records `consent_detected=false` and
`captcha_detected=false` on all 326 rows, and no CAPTCHA/consent-wall event is documented anywhere in
the repo for either dataset's collection. `METHODOLOGY.md` documents what actually happened: a
45,000ms navigation timeout, a race between "results loaded" and "zero-results text appeared"
detection, and the 7 topic-redirect product-routing cases. The personal version below uses that
language instead. Character counts were recomputed this session on the exact final text (blockquote
markers stripped), not carried over from the original draft.

---

## INTERNAL REVIEW NOTE — REMOVE BEFORE POSTING

Same caveat as the other two platforms: `main` on
`https://github.com/super-inbox/visual-search-benchmark` does not yet include the working branch's two
documentation-fix commits (`0cb6f07`, `cd2f5e4`), so the repo page a LinkedIn reader lands on today
still shows the old "319 standard search-results pages" wording in three docs. None of the three
copy-ready versions below states the 318/1/7 sub-breakdown at that level of detail (LinkedIn copy
stays at the "326/326 screenshot coverage" level, not the page-type breakdown), so this is a lower-risk
inconsistency than for HN/Reddit, but sync `main` before posting if possible. See
`PUBLIC_RELEASE_FACT_SHEET_FINAL.md` §10–11.

Also unresolved, not something this pass can fill in: no LinkedIn handle for any teammate or for a
Curify company page is known with confidence in this session. Do not guess or insert one — see §7
below.

---

## 1. Personal profile version

### COPY-READY PERSONAL VERSION

> Over the past few weeks I worked on turning two of our internal search-quality evaluations into a
> public dataset release, and wanted to share what actually went into it.
>
> We had two datasets sitting inside our internal search-quality work: a 68-query "gold set" testing
> our own visual/design search, and a 326-query bilingual (Chinese/English) set used to
> regression-test our search-relevance pipeline against a candidate code change. Both had real value
> beyond our own team, so we converted them for public release — with source-file hashes, schema
> docs, and an explicit accounting of what is and isn't included, rather than just a summary post.
>
> The part I'm most glad we shipped: for a 12-query subset of the 68-query set, real screenshots
> across five platforms (our product, Bing Images, Google Images, Canva, Pinterest) so you can see
> what each one actually returned for the same query, not just a label. And every one of the 326
> queries in the larger set now has a real Google Images screenshot and a real product-search
> screenshot too — 652 more screenshots, two more offline galleries.
>
> None of that was trivial to get right. Browser-automation captures ran into network timeouts,
> page-loading races, and — on 7 queries — our own product's client-side redirect to a category page
> instead of a normal results page. Every retry is logged, the 7 redirect pages are explicitly tagged
> as redirects rather than silently counted as normal results, and one query's genuine zero-result
> page is published as exactly that — a real product response, not a failure we hid. We also caught
> and fixed a mid-run mislabeling bug before anything went out the door.
>
> What I'd want anyone using this to know up front: neither dataset includes completed human review in
> this release — both use an LLM judge, and we say so directly. The new screenshot evidence is
> unscored — real visual evidence, not a new relevance judgment. Our own candidate search-pipeline
> branch was explicitly not approved for production at the time we captured it — this is a regression
> snapshot, not a claim about current quality.
>
> If you work on search relevance, retrieval evaluation, or multimodal ranking and want data where you
> can see the actual result page behind a label instead of just trusting a score, take a look. Thanks
> to the team members who ran the original internal evaluations this was built from.
>
> Full data, methodology, and offline galleries: https://github.com/super-inbox/visual-search-benchmark

**Character count (body text, blockquote markers stripped): 2,478** — within the ~2,300–2,600 target.

## 2. Company page version

### COPY-READY COMPANY VERSION

> We've published two internal search-evaluation datasets from our work on visual/design search:
>
> - A 68-query curated benchmark, including real cross-platform screenshot evidence — Curify vs. Bing
>   Images, Google Images, Canva, and Pinterest, for the same queries — for 12 of the 68.
> - A 326-query bilingual (Chinese/English) regression benchmark comparing two states of our
>   search-relevance pipeline, including a real Google Images screenshot and a real Curify-search
>   screenshot for all 326 queries.
>
> Every dataset includes a schema, source-file hashes, a validator script, and a written account of
> what's included and what isn't — cross-platform image evidence, not a cross-platform score;
> LLM-judged relevance labels, not completed human review; a candidate pipeline branch that was
> explicitly not approved for production at capture time. We'd rather publish that clearly than round
> it off.
>
> This is meant to be useful beyond our own product: for visual/creative search and multimodal
> retrieval research, for ranking and recommendation-system evaluation, and as a reference for
> regression-testing a search-relevance pipeline against a fixed, documented query bank. Query text,
> schemas, evaluation labels, and our own product's screenshots are released under CC BY 4.0; the
> third-party platform screenshots are included as evidence only, not relicensed for reuse or
> training.
>
> If you work in search engineering, IR research, or product on a search/discovery surface, we think
> this is worth a look — every claim in it is backed by a real screenshot, a source hash, or an
> explicit "we don't have that" note.
>
> Data, methodology, and offline galleries: https://github.com/super-inbox/visual-search-benchmark

**Character count (body text, blockquote markers stripped): 1,703** — under the 3,000-character limit.

## 3. Short version

### COPY-READY SHORT VERSION

> We published two internal search-eval datasets: a 68-query benchmark with real cross-platform
> screenshots (Curify vs. Bing/Google/Canva/Pinterest) for 12 of those queries, and a 326-query
> bilingual regression set that now has a real Google Images screenshot and a real Curify-search
> screenshot for all 326 queries. This is evidence, not a new score: the screenshots are unscored, and
> the only relevance labels in the release come from an LLM judge, not completed human review. Full
> data, schema, source hashes, and known limitations are in the repo.
>
> https://github.com/super-inbox/visual-search-benchmark

**Character count (body text, blockquote markers stripped): 605** — under the 1,000-character target.

## 4. Recommended choice

**Personal profile version (#1).** It's the only one of the three that can honestly carry the "real
challenges in collection and validation" material (network timeouts/retries, the mid-run mislabeling
catch, the zero-result page published as-is) — that's the most differentiated, least generic part of
this release, and it reads naturally as first-person work, not as company messaging. Use the company
page version instead if the boss wants the announcement to come from Curify's account rather than an
individual, and the short version as a same-week technical-audience follow-up or as document-carousel
caption text, not as a replacement for #1 or #2.

## 5. Character counts (summary)

| Version | Characters (posted text, blockquote markers stripped) | Limit | Status |
|---|---|---|---|
| 1. Personal profile version | 2,478 | ~2,300–2,600 target | Within target |
| 2. Company page version | 1,703 | < 3,000 | Well under |
| 3. Short version | 605 | < 1,000 | Well under |

All three are comfortably clear of truncation risk, including after LinkedIn's own UI adds the
link-preview card.

## 6. Recommended image / carousel structure

A document carousel (LinkedIn's native PDF-slide format) outperforms a single image for this kind of
release because the differentiator is "you can see the actual evidence," which needs more than one
frame to land. Suggested slide order:

1. **Title slide** — "Visual Search Benchmark: 68-query + 326-query search-relevance eval data," repo
   name, CC BY 4.0 badge.
2. **The idea** — one sentence: query + platform + actual result page + (where scored) a relevance
   label, joined explicitly, not implied.
3. **68-query, 12-query subset** — a side-by-side crop of 2–3 platforms' screenshots for one query
   from `data/68-query/gallery/index.html`, to show the "real screenshot, not a description" point
   concretely.
4. **326-query, screenshot evidence** — one Google Images screenshot + one Curify screenshot side by
   side for a single query, from `data/326-query/google-images/gallery.html` /
   `data/326-query/curify/gallery.html`, labeled "unscored evidence, not a new score."
5. **The redirect / zero-result honesty slide** — a screenshot of the `topics/...` redirect page and a
   one-line caption explaining it's tagged, not hidden; this is the single most credible-signal slide
   in the set precisely because it shows an edge case instead of a highlight.
6. **Known limitations slide** — bulleted, plain text: no human review in this release, no
   cross-platform score, candidate branch not production-approved, point-in-time snapshot.
7. **Closing slide** — repo link, license note, "issues/PRs for data-quality problems welcome."

Do not use any image that isn't already published in the repo's `gallery/` or `screenshots/`
directories — every image used publicly should be traceable to a `published_sha256` entry already in
the release, not a new export or crop generated just for this post.

## 7. Recommended mention placement

Do not guess or insert anyone's LinkedIn handle — none is known with confidence in this session.
Recommended placements, to be filled in by the poster with confirmed handles before publishing:

- Personal version: an optional closing line thanking named teammates who ran the original internal
  evaluations, using a placeholder like `@[teammate name — confirm handle before posting]` — do not
  publish with a guessed or unconfirmed @-mention.
- Company version: an optional `@[Curify company page — confirm handle/URL before posting]` if posted
  from a personal account and cross-linked to the company page, rather than posted directly from the
  company page itself.
- Do not @-mention any individual without their prior confirmation that they're comfortable being
  tagged on an external post — this is a boss-review item, not a drafting decision.

## 8. Pre-publish checklist for this post specifically

- [ ] Confirm which account posts: personal or company (boss decision, §5 of the boss summary).
- [ ] Fill in any @-mentions only after each named person confirms their handle and consent.
- [ ] Confirm no carousel image is a new crop/export — every image must already exist in the repo with
      a `published_sha256` entry.
- [ ] Re-confirm `main` sync status per the internal review note above.
