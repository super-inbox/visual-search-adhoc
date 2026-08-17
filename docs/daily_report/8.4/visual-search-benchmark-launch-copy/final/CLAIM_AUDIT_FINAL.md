# Claim Audit — FINAL (Visual Search Benchmark Launch Copy)

Every claim below is checked against `PUBLIC_RELEASE_FACT_SHEET_FINAL.md` and, through it, the
repository itself (working branch `baobao/publish-visual-search-benchmarks-2026-07-30` @
`cd2f5e4ad5db49fc1a0f47a125e5a760073d19be`). "Allowed in public copy" is a hard gate — a "No" means
that claim does not appear in any HN/Reddit/LinkedIn draft in `final/`, in any form.

## Allowed claims

| Claim | Allowed | Required qualification |
|---|---|---|
| "326-query benchmark, 326 unique queries (163 zh / 163 en), 0 duplicates" | Yes | None — verified directly |
| "68 + 326 = 394 combined unique queries across both benchmarks" | Yes | Must state "two separate benchmarks published together, not merged" every time |
| "Google Images screenshot evidence: 326/326 for the 326-query set" | Yes | Must say "unscored visual evidence," never "relevance judgment" or "ranking" |
| "Curify screenshot evidence: 326/326 for the 326-query set" | Yes | Must use the 318/1/7 breakdown if any sub-number is cited (see next row) |
| "318 standard search-results pages / 1 zero-result page / 7 topic-redirect pages" (Curify, 326-query) | Yes | Use **318**, not 319. This is now the number stated consistently across the repo's own prose docs on the working branch (fixed in `0cb6f07`) — not just the manifest-only truth it was when the original audit was written |
| "319 automated + 7 automated_retry captures" | Yes, if the topic is *capture method*, not *page type* | Must not be presented as if it were the page-type count; 319 = 318 search_results + 1 search_zero_results rows, both captured via `capture_method=automated` |
| "68-query image evidence: 12 of 68 queries, 62 images" | Yes | Never state as if it applies to the 326-query set |
| "7 topic-redirect queries, real Curify product behavior" | Yes | Must state these are explicitly tagged `page_type=topic_redirect` and never presented as standard search-results pages |
| "1 genuine zero-result query (V078, 'bobblehead')" | Yes | Must call it a real product response, not a technical failure |
| "No CAPTCHA or consent wall in the published Google Images evidence" | Yes | Supported directly: `consent_detected=false` and `captcha_detected=false` on all 326 manifest rows |
| "Capture issues encountered: network timeouts, page-loading races, and 7 client-side product redirects" | Yes | Supported by `METHODOLOGY.md`'s stated 45,000ms navigation timeout, the result-card/zero-result-text detection race, and the 7 topic-redirect retries — do not upgrade this to "CAPTCHAs, consent walls" |
| "Production vs. candidate branch comparison" (326-query `evaluations.csv`) | Yes — the one legitimate scored comparison in the release | Must state the candidate was not approved for production at capture time |
| "LLM-judged relevance labels" | Yes | Must not be written or implied as human-reviewed |
| "Reproducible / validators pass" | Yes | Note both benchmarks are point-in-time snapshots; only the *data as published* is reproducible |

## Forbidden claims

| Claim | Why forbidden |
|---|---|
| "This is a relevance judgment / evaluation of Google vs. Curify" | No such scored comparison exists anywhere in the source data |
| "Human-review annotations are included" / "human-reviewed ground truth" / "human/LLM-audited" (implying completed human review) | 68-query: 0/68 completed. 326-query: internal pass exists but withheld. Correct phrasing: "LLM-judged, with human-review status documented explicitly" or "not included in this public release" |
| "An internal human-review pass exists for both [benchmarks]" as a direct answer to "are labels human-reviewed" | Misleading by omission — true only for 326-query (withheld, not published), and **not true** for 68-query (no pass was ever completed, not merely withheld). Must give the two cases separately, per HN Q2 in `HACKER_NEWS_FINAL.md` |
| "Browser-automation captures hit CAPTCHAs, consent walls[, ...]" | Not supported: `consent_detected`/`captcha_detected` are `false` on all 326 Google Images manifest rows; no CAPTCHA/consent-wall event is documented anywhere in the repo for either dataset's evidence collection |
| "Curify beats Google" / any comparative performance claim between platforms | No scored cross-platform comparison exists in this release |
| "Open source" (unqualified) | CC BY 4.0 covers data/schema/docs/code/Curify's own screenshots; explicitly excludes the third-party 68-query images (50 files) and the 326 Google Images screenshots |
| "First [of its kind]" | No document makes or supports this claim |
| "Largest [benchmark of its kind]" | No comparative sizing against other benchmarks exists anywhere |
| "Best" | Contradicted by the data itself (68-query: 43 FAIL/25 WARN/0 PASS; 326-query candidate: still 195 FAIL) |
| "State of the art" / "SOTA" | Contradicted by `provenance.json` (candidate branch = "NEEDS_MORE_FIXES", not approved) |
| Any exclamation point in HN title/body/comment | House-style requirement carried from the original HN draft, unchanged |
| "319 standard search-results pages" | Superseded — this was the repo's own bug (arithmetic error, 319+1+7=327), already fixed on the working branch. Do not resurrect it in launch copy even though it is, as of this session, still what `main` displays until synced (§10 of the fact sheet) |
| Citing the working-branch-only fix commits (`0cb6f07`, `cd2f5e4`) or their SHAs in public copy | Internal Git history, not reader-relevant; belongs in the fact sheet / boss summary only |
| "328-query" anything | No such dataset exists in this release |

## Notes on enforcement

- Every row above was checked against `PUBLIC_RELEASE_FACT_SHEET_FINAL.md` in full, re-derived this
  session from the repository, not carried forward from the original (pre-fix) audit without
  re-verification.
- The single substantive change from the original `CLAIM_AUDIT.md`: the 318/1/7 vs. 319 conflict is
  **no longer an open documentation bug to flag** — it is fixed on the working branch. What remains
  open is a **Git-sync** issue (branch vs. `main`), not a **data/claim** issue — tracked in the fact
  sheet §10–11 and the boss summary, not as a forbidden-claim row here.
- The CAPTCHA/consent-wall correction is new in this pass — the original LinkedIn draft's personal
  version made this claim without a supporting citation; it has been rewritten in
  `LINKEDIN_FINAL.md` using only what the manifest data and `METHODOLOGY.md` actually document.
