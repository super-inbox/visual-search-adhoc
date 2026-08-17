# Public Release Fact Sheet — FINAL (Visual Search Benchmark)

Regenerated 2026-08-04, same day as the original `PUBLIC_RELEASE_FACT_SHEET.md`, but after a fresh
re-read of the repository. **Every number and Git fact below was re-verified in this session directly
against `/Users/baobaoli/Desktop/visual-search-benchmark`, not carried over from the earlier draft.**
The single most important change from the original fact sheet: the earlier draft's §12 ("`main`
already contains everything, byte-identical to the working branch") is **no longer true**. Two new
documentation-fix commits landed on the working branch after that draft was written, and neither is
on `main` yet. See §12 below — this supersedes the original fact sheet's §12 in full.

## 1. Release scope (unchanged from the original fact sheet)

Two Curify-internal search-evaluation datasets, converted for public release:

- **68-query benchmark** — Curify's own search relevance, 68 hand-curated queries, plus real
  cross-platform screenshots (Curify/Bing/Google Images/Canva/Pinterest) for **12 of the 68**.
- **326-query benchmark** — a production-vs-candidate regression test of Curify's search-relevance
  pipeline over 326 queries, plus real, unscored Google Images + Curify screenshot evidence for
  **all 326** queries.

Published together but **not one merged benchmark** — different query sets, different systems under
test, different label vocabularies (`README.md` §4–5; `METHODOLOGY.md` "Why the two benchmarks are
not merged").

## 2. 68-query benchmark — exact figures (re-verified, unchanged)

| Metric | Value |
|---|---|
| Rows / unique queries | 68 / 68, 0 duplicates, 0 empty |
| Cross-platform image evidence | **12 of 68 queries**, 62 image files |
| Images per platform (12-query subset) | curify 14, bing 12, google 12, canva 12, pinterest 12 |
| Human review | **0 of 68** rows ever completed by a human reviewer; rubric/spreadsheet prepared, never executed |

## 3. 326-query benchmark — exact figures (re-verified this session)

| Metric | Value | Re-verified against |
|---|---|---|
| Rows / unique queries | 326 / 326, 0 duplicates | `data/326-query/queries.csv` |
| Language split | 163 Chinese / 163 English | `data/326-query/queries.csv` |
| `evaluations.csv` rows | 652 (326 × 2 `run_variant`) | direct row count |
| Candidate branch production status | explicitly **not approved** at capture time | `provenance.json` `known_limitations` |
| Google Images screenshot evidence | **326/326**, `status=success`, 1440×1000 JPEG | `data/326-query/google-images/manifest.csv` |
| Curify screenshot evidence | **326/326**, `status=success`, 1440×900 JPEG | `data/326-query/curify/manifest.csv` |
| Curify `page_type` breakdown | `search_results` **318**, `search_zero_results` **1** (`V078`, "bobblehead"), `topic_redirect` **7** — sums to 326 | recomputed directly, this session: `awk -F',' '{print $20}' manifest.csv \| sort \| uniq -c` |
| Curify `capture_method` breakdown | `automated` **319** (= 318 + 1), `automated_retry` **7** (= the 7 redirects) — sums to 326 | recomputed directly, this session |
| Curify decode/exception status | `consent_detected`/`captcha_detected` not applicable to Curify manifest; `error_type` empty on all 326 rows; `exception_type` = `stale_search_box_text` on the 7 `topic_redirect` rows only, empty elsewhere | recomputed directly, this session |
| Google Images capture conditions | `consent_detected=false` and `captcha_detected=false` on **all 326 rows** — no CAPTCHA or consent wall was encountered in the published evidence | recomputed directly, this session: `set(row['consent_detected'] ...)` / `set(row['captcha_detected'] ...)` both `{'false'}` |
| Human review | Internal human-verification pass **exists but is withheld** from this release | `SOURCE_AUDIT.md`; `provenance.json` |

**318/1/7 is now the number everywhere in the repo, including prose docs.** The original fact sheet's
"Conflict #1" (root `README.md`, `METHODOLOGY.md`, and `data/326-query/README.md` mislabeling the
319-automated-capture total as "319 standard search-results pages") **has already been fixed** on the
working branch, in two commits made after the original fact sheet was written:

- `0cb6f07` ("docs: correct Curify 326 evidence breakdown") — fixed `README.md`, `METHODOLOGY.md`,
  `SOURCE_AUDIT.md`, `data/326-query/README.md` to state 318/1/7 and distinguish `page_type` from
  `capture_method`.
- `cd2f5e4` ("docs: align benchmark release documentation") — fixed a second, related ambiguity in
  `data/326-query/provenance.json`'s `captured` field and `data/326-query/curify/gallery.html`'s
  summary banner (both previously read as "319 standard + 1 zero-result," which is arithmetically
  confusable with 320); also fixed a `VALIDATION_REPORT.md` file-size claim that contradicted
  `SIZE_REPORT.md`, removed a "human/LLM" phrasing that implied completed human review, and removed a
  README claim that the 326-query set had "no cross-platform data at all" (no longer true since the
  screenshot evidence was added).

**Re-verified directly, this session:** `README.md`, `METHODOLOGY.md`, `SOURCE_AUDIT.md`,
`data/326-query/README.md`, `data/326-query/curify/README.md`, `data/326-query/curify/gallery.html`,
and `data/326-query/provenance.json` **all now state 318/1/7 consistently, with no remaining
"319 standard" or arithmetic-error phrasing.** This is a working-branch fact, not yet a `main` fact —
see §12.

## 4. Combined 68 + 326

**0 query overlap**, **394 combined unique queries**. Not stated in any repo document; computed by
comparing `data/68-query/queries.csv` and `data/326-query/queries.csv` as sets. Must always be
qualified as "two separate benchmarks published together, not one merged set."

## 5. Screenshot evidence vs. relevance judgment (must never be conflated)

- The 326-query Google Images and Curify screenshots are **unscored visual evidence** — no relevance
  judgment, ranking, or score was generated for either surface, and `evaluations.csv` (the only scored
  data in this release, Curify-only) was not re-run or altered.
- The 68-query 12-subset screenshots: only the Curify screenshot in each of the 12 carries a formal
  label (`FAIL`, all 12); the four competitor-platform screenshots carry free-text observations, not a
  numeric score.
- No platform other than Curify has scored, per-query relevance data anywhere in this release.

## 6. Data collection conditions (for LinkedIn/HN copy accuracy — re-verified this session)

Per `METHODOLOGY.md`'s 326-query capture section and the manifest fields themselves:

- **Google Images:** 326/326 succeeded. **Zero CAPTCHA and zero unresolved consent walls** in the
  published evidence (`consent_detected=false`, `captcha_detected=false` on all 326 rows). A small
  number of transient network/timeout errors during collection were resolved by retry, never
  bypassed.
- **Curify:** 45,000ms navigation timeout per attempt; results-loaded detection is a race between a
  result-card selector and an explicit zero-result-text selector; the 7 topic-redirect queries needed
  up to 3 attempts each in a fresh browser context. `error_type` is empty on all 326 published rows —
  no unresolved errors in what was published.
- **Do not write that captures "hit CAPTCHAs" or "hit consent walls"** — that is not supported by the
  published manifest data (both flags are `false` on every row). The supported, evidenced framing is
  network timeouts, page-loading races, and the 7 topic-redirect product-routing cases.

## 7. Human-review publication boundary

- **68-query:** a human-review rubric/spreadsheet was prepared but **0 of 68** rows were ever
  completed by a human reviewer.
- **326-query:** an internal human-verification pass exists over this query set but is **withheld**
  from this release — no counts, verdicts, or file hash from it are published.
- Neither benchmark may be described as human-reviewed ground truth. `human_spot_check.csv` is
  confirmed absent repo-wide.

## 8. License

- Query lists, schemas, provenance, evaluation labels/reasons, documentation, code, and **Curify's
  own screenshots** (both benchmarks): **CC BY 4.0**, attribution to Curify.
- **Not CC BY 4.0:** the 50 third-party platform screenshots in `data/68-query/images/`
  (Bing/Google/Canva/Pinterest) and the 326 Google Images screenshots in
  `data/326-query/google-images/` — evidence-only inclusion; copyright remains with the original
  rights holders. `CITATION.cff` now carries an `abstract:` field stating this carve-out explicitly
  (added in `cd2f5e4`).

## 9. Validation status (re-run this session, on the current working-branch `HEAD`)

```
python3 scripts/validate_data.py       -> OVERALL: PASS (exit 0)
python3 scripts/validate_benchmark.py  -> OVERALL: PASS (exit 0)
```

Both scripts were actually re-executed in this session against the current tree — not copied from
`VALIDATION_REPORT.md`.

## 10. Current Git status — re-verified this session (supersedes original fact sheet §12)

```
git remote -v                → origin: https://github.com/super-inbox/visual-search-benchmark.git
git branch --show-current    → baobao/publish-visual-search-benchmarks-2026-07-30
git rev-parse HEAD           → cd2f5e4ad5db49fc1a0f47a125e5a760073d19be
git rev-parse origin/main    → 22414abf6e6f7a4d4453a647c46bc4765119d6c8
git rev-parse origin/<branch> → cd2f5e4ad5db49fc1a0f47a125e5a760073d19be (matches local HEAD — branch is pushed)
git status --short           → (clean)
git diff --stat origin/main...HEAD → 8 files changed (see below)
```

- **Working branch `HEAD`:** `cd2f5e4ad5db49fc1a0f47a125e5a760073d19be` — 2 commits ahead of
  `origin/main`:
  - `0cb6f07` — docs: correct Curify 326 evidence breakdown (318/1/7 fix, 4 files)
  - `cd2f5e4` — docs: align benchmark release documentation (human-review wording, file-size
    contradiction, provenance/gallery ambiguity, CITATION.cff license note — 5 files)
- **`origin/main` HEAD:** `22414abf6e6f7a4d4453a647c46bc4765119d6c8` — this is the merge commit of PR
  #2 (`gh pr list` confirms PR #1 and PR #2 both `MERGED`, `headRefOid` of PR #2 =
  `e537cc641e4e0103ac59fd17da0f7792c1d4f31f`, i.e. the commit **before** both fix commits above).
- **`main` does NOT yet contain `0cb6f07` or `cd2f5e4`.** Concretely, right now, the default-branch
  copy of `README.md`, `METHODOLOGY.md`, `SOURCE_AUDIT.md`, and `data/326-query/README.md` on GitHub
  still say **"319 standard search-results pages"** (the arithmetic/labeling bug), and
  `VALIDATION_REPORT.md` on `main` still has the file-size contradiction and the human-review-implying
  phrasing that were fixed on the branch.
- **This reverses the original fact sheet's finding.** The original `PUBLIC_RELEASE_FACT_SHEET.md`
  (written earlier the same day) correctly found `main` and the branch were byte-identical **at that
  time** — that was true before `0cb6f07`/`cd2f5e4` were made. It is not true anymore.
- **No PR was created and no merge was performed in this session** (only read-only `git`/`gh` commands
  were run) — per this task's explicit instructions not to touch `main` or open a PR.

## 11. Canonical URL status

- **URL itself:** `https://github.com/super-inbox/visual-search-benchmark` remains the correct,
  stable, public repo URL — this does not change based on branch state, and does not need a
  branch-specific query string or ref.
- **Content-freshness caveat (new, this session):** publishing external copy that links to this URL
  **today** sends readers to `main`, which still has the "319 standard search-results pages"
  documentation bug and the other issues fixed in `0cb6f07`/`cd2f5e4`. If any of this launch copy
  states "318 standard / 1 zero-result / 7 topic-redirect" (which it does, per §3), a reader who
  clicks through to `main` right now would see a page that still says "319" in three places — an
  avoidable, easily-noticed inconsistency between the announcement and the linked repo.
- **Recommendation:** sync `main` (fast-forward or a new PR, boss-approved) to include `0cb6f07` and
  `cd2f5e4` **before** any external post goes out. This is a merge decision for the boss/repo
  maintainer — not performed in this session.

## 12. Known limitations (for disclosure in every platform's copy — unchanged)

- 326-query and 68-query screenshot evidence is unscored; no cross-platform ranking exists anywhere in
  this release.
- Relevance labels (both benchmarks) are LLM-judge output, not completed human review.
- 326-query candidate branch was not approved for production at capture time.
- Both benchmarks are point-in-time snapshots; live results will differ on a re-run.
- 68-query image evidence covers 12 of 68 queries, not all 68.
- No "328-query" dataset exists in this release; never write "328" in public copy.
