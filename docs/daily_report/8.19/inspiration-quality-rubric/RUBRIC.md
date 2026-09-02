# Inspiration Candidate Quality Rubric — v1.0

Status: **v1.0, human evaluation rubric.** This formalizes the A/B/C grading heuristic that
has been applied informally (and inconsistently) across prior inspiration-sourcing pilots. It
is **not** an automatic/model-computed score — it is a reproducible procedure for a human
reviewer to apply by hand. A future version may turn some or all of this into an automated or
model-assisted score (see Versioning).

## 1. Purpose and scope

**Purpose:** give every human reviewer grading inspiration candidates the same three questions,
the same scoring anchors, and the same deterministic rule for turning those answers into an
A/B/C grade — so that two reviewers looking at the same candidate produce the same grade, and
the same reviewer produces the same grade on two different days.

**In scope:** grading a single already-discovered inspiration candidate (an image/case-study
page surfaced for a specific query) for whether it is fit to store, show, or scale as
inspiration content.

**Out of scope:**
- Discovery/search strategy (how candidates are found) — not graded here.
- Deduplication against other candidates — handled separately (`duplicate_status` /
  `UNIQUE`/`DUPLICATE` fields in existing pilots), not part of this rubric.
- Topic/taxonomy mapping (whether the candidate maps to a declared Curify topic) — a separate,
  already-documented workflow (see `docs/daily_report/8.12/inspiration-topic-pinterest/FINDINGS.md`).
- Legal/licensing review — grading here is about evaluation quality, not usage rights.

## 2. Unit of evaluation

**One inspiration candidate, for one query/brief.** A candidate is one row: one source URL (or
canonical URL, if it differs from the discovery URL — see §7 on the `source_url` vs.
`canonical_url` distinction, grounded in `pack_v098_003` /
`docs/daily_report/8.8/inspiration-source-pilot/INSPIRATION_INTEGRATION_FINDINGS.md` point 7)
paired with the single query it was retrieved for. The same source graded against a different
query is a different unit of evaluation, because Query Relevance (§4a) is query-dependent.

## 3. The three core dimensions

Every candidate is scored on exactly three dimensions, each on a **0–2 scale**:

| Score | Meaning |
|---|---|
| **2** | Strong — clearly satisfies the dimension |
| **1** | Partial / adequate — satisfies the dimension but with a real, nameable gap |
| **0** | Fails the dimension |

### 3a. Query Relevance

Does this candidate visually and conceptually match the query's subject, format, and design
intent?

- **2 — Direct match.** The candidate's subject, format, and domain line up with the query
  without qualification. *Example: a business-card case study returned for the query
  "business card."*
- **1 — Partial/adjacent match.** The candidate matches the query's general category or format
  but not the full intent, or matches on format while the underlying content is thin relative
  to what the query implies. *Example: a static ad mockup returned for an "influencer post"
  query — right general content type, but a mocked-up static image rather than native
  influencer content.*
- **0 — No real match.** The candidate is only superficially related (keyword overlap without
  visual/conceptual relevance) or is a different subject entirely. In practice, a candidate
  scoring 0 here should usually never have been retained past discovery — if you are grading a
  0 here, double check the candidate wasn't mis-attached to the wrong query.

### 3b. Design / Source Evidence

How much genuine design/production detail does the candidate actually show — process,
system-level thinking, stated rationale — versus a single bare finished image?

- **2 — High depth.** Multiple stages or a full system are shown or described: sketches,
  prototypes, before/after, multi-touchpoint collateral, or an explicitly stated design
  rationale. *Examples: RACCOON FACTORY (`merch_v004_003`) — sketch/prototype/product-photo
  stages shown; Nook Coffee (`brand_v094_005`) — full identity system (typeface, palette, style
  guide) applied across cards and stationery.*
- **1 — Medium depth.** A coherent, finished single-stage output with no process documentation.
  *Example: MIKO® ART-TOY (`merch_v004_001`) — final renders across multiple angles, credited
  tools, but no sketch/process stage.*
- **0 — Low depth.** Minimal extractable visual or compositional detail — e.g., only production
  software is listed with no describable composition, palette, or layout; or a generic
  template with no distinguishing craft/provenance detail. *Example:
  `ecom_v216_004` — "only production software listed, no static frame composition/palette/
  layout description extractable."*

### 3c. Attribution / Context Completeness

Is there a real, named creator or organization behind this candidate, and can that attribution
be trusted and (ideally) independently verified?

- **2 — Verified attribution.** A named individual or studio is credited, **and** that
  attribution is independently verifiable through a second channel beyond the discovery page
  itself — a personal site, a real client/business, social presence, or press coverage — with
  the source directly and currently accessible. *Example: Nook Coffee — "independently verified
  as a real, currently-operating business at a specific real-world location... named designer
  with verified LinkedIn/Instagram."*
- **1 — Named but unverified.** A named individual or studio is credited on the discovery
  platform itself and the page is directly accessible, but no independent second channel was
  found or checked. *Example: MIKO® ART-TOY — "named individual designer's own Behance
  publication; credited tools; no verified external site."*
- **0 — No trustworthy attribution.** No named creator; the credited party is a re-poster and
  not the actual designer (e.g., a recipient sharing someone else's design work); or the source
  is currently inaccessible with no working alternative. *Example: `edu_v260_004` — a student's
  repost of their own certificate, credited to "Dhruv Desai... recipient, not the certificate's
  designer."*

## 4. Overall A / B / C assignment

Compute `sum = relevance + evidence + attribution` (range 0–6). Then apply, **in order**:

1. **If any hard-fail condition applies (§5): grade = C**, regardless of `sum`.
2. **If any single dimension scored 0: grade = C**, regardless of `sum`. (A candidate cannot be
   A or B if it completely fails even one dimension — a 0 is a real disqualifier, not something
   the other two dimensions can average away.)
3. **Else, grade by sum:**
   - `sum` 5–6 → **A**
   - `sum` 3–4 → **B**
   - `sum` 0–2 → **C**

This is fully deterministic from the three 0–2 scores plus the hard-fail check — no reviewer
judgment is needed once the three dimension scores are assigned. Reviewer judgment is
concentrated where it belongs: in assigning the 0/1/2 score per dimension.

### Worked check against real prior data

| Candidate | Relevance | Evidence | Attribution | Sum | Hard-fail? | Grade (this rubric) | Grade (prior pilot) |
|---|---|---|---|---|---|---|---|
| `brand_v094_005` Nook Coffee | 2 | 2 | 2 | 6 | No | **A** | A |
| `merch_v004_001` MIKO® ART-TOY | 2 | 1 | 1 | 4 | No | **B** | B |
| `ecom_v216_004` UGC-Style Ad | 2 | 0 | 1 | 3 | No (but Evidence=0) | **C** (0-dimension rule) | C |
| `ecom_v174_005` Amazon A+ Content | 1 | 0 | 1 | 2 | Yes (unverified performance claim) | **C** | C |

The rubric reproduces all four prior grades. See `CALIBRATION_EXAMPLES.csv` for the full set,
including cases where this rubric is intentionally **stricter** than the prior informal
grading.

## 5. Hard-fail / downgrade conditions

Any of the following forces the overall grade to **C**, regardless of the dimension sum:

1. **Access is blocked with no working alternative.** The primary source page returns an error
   (e.g., HTTP 402/403/404) and no other accessible page carries the same content.
   (`traceability` = `ACCESS_BLOCKED` with no `AVAILABLE` fallback.)
2. **No thumbnail/preview image is available.** (`thumbnail_reliability` = `UNAVAILABLE`.)
3. **An unverified performance/marketing claim is presented uncritically as fact** in the
   candidate's own description (e.g., an unsubstantiated "300% better conversion" claim), and
   grading does not flag it as unverified.
4. **The credited party is not the original designer** — a recipient, re-poster, or third party
   sharing someone else's design work, presented without that distinction being made explicit.
5. **The candidate is a duplicate** of an already-retained candidate for the same query
   (`duplicate_status` = `DUPLICATE`). Grade as C (or exclude outright) rather than scoring it
   independently — duplicates should not accumulate separate A/B grades.

A hard-fail is a **grading outcome**, not a reason to skip scoring the three dimensions — always
record the 0–2 scores first, then apply the hard-fail as an override. This keeps the record
useful for calibration even when the final grade is capped.

## 6. Handling ambiguous cases

- **Partial verification (some but not all attribution channels blocked).** If the discovery
  page itself is directly accessible but a *secondary* verification channel (e.g., the
  creator's personal site) is blocked, this is **not** a hard-fail under condition 1 (which
  applies to the *primary* source) — score Attribution as 1, not 0, and note the blocked
  secondary channel in `reviewer_notes`. *Example: `edu_v260_002` — Behance page accessible,
  creator's personal site returned HTTP 402; graded B under this rubric (see calibration
  examples), reflecting the incomplete independent verification, even though the earlier
  informal pass called it A.*
- **Structurally different source type (e.g., an editorial/guidance article instead of a
  single-project case study).** Score the three dimensions as written — an editorial article
  can still score 2 on Evidence if it shows concrete, checkable specs, and 1–2 on Attribution if
  the publishing organization is real and named. If the candidate's *format* itself doesn't fit
  how inspiration content is currently structured (e.g., one article vs. one image), grade it
  normally but flag `reviewer_notes` with `NEEDS_PRODUCT_REVIEW` — that is a product-fit
  question, not a quality question, and should not silently distort the grade.
  (`ecom_v216_002`, `docs/daily_report/8.8/inspiration-source-pilot/SOURCE_QUALITY_REVIEW.csv`,
  is the source example for this pattern.)
- **A real institution/brand is involved but the work shown is a one-off promotional tie-in
  rather than the brand's core product.** Score Design/Source Evidence and Attribution on what
  is actually shown, not on the institution's general reputation. A well-known brand name does
  not by itself earn a 2 on any dimension — every A grade in prior pilots required a specific,
  checkable piece of evidence, not just platform or brand prestige (see
  `INSPIRATION_INTEGRATION_FINDINGS.md` point 4: "No candidate was graded A purely because its
  host platform is well-known").
- **Reviewer disagreement.** If two reviewers score the same candidate differently on the same
  dimension, treat it as a signal the anchor language needs sharpening — record the
  disagreement and the two scores in `reviewer_notes` rather than silently averaging, and raise
  it for the next rubric version (§8).

## 7. Notes carried over from prior practice

- **`source_url` vs. `canonical_url`:** when a candidate is discovered on one page (e.g., a
  Behance listing) but a richer, more detailed version exists on the creator's own site, grade
  against the canonical (richer) page's content — the discovery surface does not cap the
  grade. This is a real, intentional distinction, not a data error (see `pack_v098_003`).
- **A well-known host platform does not substitute for evidence.** Being on Behance, Pinterest,
  or any other reputable platform is not itself a point toward any dimension — every score
  requires specific, describable evidence from the candidate's own content.

## 8. Versioning

- **v1.0 (2026-08-19):** Initial formalization of the previously ad-hoc A/B/C heuristic used
  across the 8.8 (`SOURCE_QUALITY_REVIEW.csv`), 8.12, and 8.14 inspiration pilots, into the
  three fixed dimensions, 0–2 scoring anchors, deterministic A/B/C assignment rule, and
  hard-fail conditions documented above. This is a **human evaluation rubric**; no automatic or
  model-based scoring is implied or attached at this version.
- **Future versions** should be recorded as new `## vX.Y` entries appended below this line
  (never edit a shipped version's history in place). Each new version should state: what
  changed, why (usually: an ambiguous case from §6 that came up often enough to need a named
  rule, or a calibration mismatch found by re-grading existing data), and whether it changes
  any grade on the existing `CALIBRATION_EXAMPLES.csv` set — if it does, regenerate that file
  in the same change so the calibration set and the rubric never drift apart.
