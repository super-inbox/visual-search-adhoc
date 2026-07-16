# Hybrid Search — Merge and Ranking Specification (Design Only)

No cross-source merge/rank logic exists in the codebase today (confirmed, Current Architecture doc §2.4). This document specifies a deterministic MVP policy for future implementation — nothing here has been coded.

## Governing principles (as specified in the brief, restated with rationale)

- **Preserve relevant internal results** — the internal catalog is Curify's actual product; external content must never crowd it out.
- **Internal results rank first by default** — matches the existing precision-first posture of the internal scorer (`hasStrict` gate, page.tsx:704) and Extension C's own framing ("Curify results ... native, copy/remix" listed first, "Inspiration from elsewhere" listed below).
- **External results fill gaps, not replace inventory** — external is a supplement triggered only by thinness, never a parallel competing ranked list merged token-for-token with internal.
- **Cap external results in the first screen** — bounds both cost (fewer displayed = smaller acceptable fetch, though the provider call itself may return more than shown) and exit-rate risk.
- **Explicitly label external sources** — required both for user trust and (per Provider Options doc) likely attribution compliance requirements.
- **Preserve original external destination links** — never rewrite/proxy/redirect through Curify; matches Extension C's hotlink-only stance and copyright mitigation.
- **Never present external results as Curify templates** — enforced structurally via the separate-card recommendation (Deliverable 4/5).
- **No edit/use/generate actions on external results** unless a separate, explicitly-designed "Make with Curify" workflow exists (not the same as the internal generate action).
- **External provider failure must never remove internal results** — internal results are computed independently and render regardless of the external leg's outcome; this is a hard invariant, not a best-effort behavior (see Failure/Cache/Cost spec).

## Case-based policy

### Case A — 0 internal results
- Internal section renders empty (or is omitted entirely) — current UI already handles this (`SearchResultsClient.tsx:319-329` zero-result branch).
- External section: allow up to **8-12** external results (per the brief's example design).
- The entire external section is **clearly labeled** as external inspiration/reference — not blended visually with what would have been an internal grid. Recommend the exact framing already drafted in Extension C: "Inspiration from elsewhere," with each result carrying a per-card source-domain badge in addition to the section-level label (redundant labeling reduces misattribution risk more than a single label placement).

### Case B — 1-4 internal results
- Keep **all** internal results, ranked first, in their existing order (internal ranking logic unchanged).
- Fill remaining first-screen slots with external results up to the cap.
- Example for a 12-position first screen (as given in the brief): if internal count is, say, 3, show all 3 internal + up to 9 external (bounded by the section cap below, not necessarily using all 9 remaining slots if fewer external results are relevant/available).

### Case C — 5+ internal results
- Internal-only by default under the T5 trigger candidate — the external leg would not have fired at all in Mode E under a T5 threshold, so this case is largely moot for T5. It matters only if a looser trigger (a discussed-but-deferred relevance-based trigger) is later adopted, in which case: primarily internal, **at most 4** external results appended after all internal results — never interleaved above an internal result.

## Proposed first-screen policy (12 positions) — evaluated per brief

```
If internal count >= 8:
  - primarily internal
  - at most 4 external
If internal count is 1-7:
  - keep all internal first
  - fill remaining slots with external results
If internal count is 0:
  - allow up to 8-12 external results
  - clearly label the entire section as external inspiration/reference
```

**Assessment:** structurally sound and consistent with the "internal-first, external-fills-gaps" principle. Two refinements recommended for the next design pass (not implemented here):
1. The `>= 8` branch is inconsistent with a T5 trigger (which wouldn't fire external search at all once internal count reaches 5) — this branch only becomes reachable if the trigger threshold is later loosened beyond T5, or if the external call was already in flight when the internal count crossed 5 mid-request (a race that the "parallel" execution model in Mode D/E makes structurally possible: the external call starts before the internal count is fully known in the >=5 sense... actually the internal count IS known synchronously before the parallel calls start, per the call graph, so this race does not exist in this design — noted here for completeness. External calls should therefore only ever be initiated when the trigger condition is met, making the `>=8` branch unreachable under any single-threshold policy. Recommend removing this branch from the MVP policy and revisiting it only if/when a non-count-based trigger is added.)
2. "At most 4 external" for the 5+ case should be treated as a documented exception path (per point 1), not a mainline MVP case.

**Revised MVP recommendation:** collapse to two mainline cases (0, and 1-4) matching whatever trigger threshold is chosen, and treat the "5+" case as simply "no external call ever made" — internal-only — for MVP simplicity and cost minimization, until online results justify complicating the trigger.

## Deterministic fields (data contract link)

Reuses the proposed `HybridSearchResult` fields from Deliverable 4/5: `source_type`, `source_domain`, `external_provider`, `original_query`, `retrieval_query`, `rewrite_used`, `rank_before_merge`, `rank_after_merge`, `image_url`, `destination_url`, `internal_result_id`, `external_result_key` (= `result_key` for external rows). No new fields introduced here beyond what those two deliverables already define.

## Deduplication

### MVP dedup keys (cheap, deterministic, no ML)
- **Canonical destination URL** — normalize scheme/trailing-slash/query-param-order, compare exact match. Catches the same external page returned twice (e.g., by two different query paths in Mode D/E's parallel-path design). **Limitation:** does not catch the same image hosted at two different URLs (mirrors, CDNs, re-posts) — a real and common case for viral/Pinterest-sourced images.
- **Normalized image URL** — same normalization applied to `image_url` rather than `destination_url`. Catches cases where the same image is embedded on two different pages. **Limitation:** breaks the moment a provider serves a resized/cropped/re-encoded variant of the same underlying image (different URL, visually identical or near-identical content) — very common for image search results.
- **Title + domain composite key** — fallback when URLs don't match but the pairing (exact title string, same domain) suggests a duplicate. **Limitation:** high false-negative rate (titles are often absent or generic — "Image result" — making this key useless in exactly the cases it's meant to help with) and non-trivial false-positive rate (two different images on the same domain can share a generic title).

None of the three MVP keys can dedup internal-vs-external overlap (an external result that happens to visually resemble an internal template) — that is out of scope for MVP dedup and listed as a later-phase item below.

### Later (explicitly not MVP, requires new infrastructure not present in the repo)
- **Perceptual hash (pHash/dHash)** of images — would catch resized/re-encoded/cropped duplicates that URL-based keys miss. Requires an image-fetch-and-hash pipeline (fetching external images server-side introduces its own latency/cost/legal considerations around temporarily processing third-party image bytes) — not something to add casually; needs its own design review.
- **Visual similarity (embedding-based)** — would also help internal-vs-external overlap detection (e.g., suppressing an external result nearly identical to an internal template Curify already has) but requires an embedding model and vector comparison infrastructure not present anywhere in this repository today.
- **Semantic similarity** (title/description embedding match) — lowest priority; text-based semantic dedup is weaker signal than visual for an image-search feature, and the "we have zero relevance labels" gap (Extension B) would also block calibrating any such threshold.

## Explicit non-goals for MVP merge/ranking

- No learned reranker — this document specifies a deterministic, rule-based policy only, consistent with the absence of any relevance-labeling infrastructure (Extension B gap, confirmed unbuilt).
- No cross-source (internal template vs. external image) visual similarity suppression — listed under "Later" above.
- No personalization/user-history-based ranking adjustment — no evidence this exists for internal search either; out of scope.
