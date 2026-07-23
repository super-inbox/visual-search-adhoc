# Automated Sanity Check — Notes

**Purpose (per charter):** verify the runner points at the latest frontend worktree (commit `0e794cd9`), results are
generated, output fields are populated, no environment/configuration mismatch exists, and the full run will not
immediately fail. This is NOT a new manual adjudication phase — no PASS/PARTIAL/FAIL labels are assigned here.

## Setup
- Candidate build: `npm run build` at commit `0e794cd9` (same build used for the engineering gate — not rebuilt a
  second time; `.next/BUILD_ID` = `f-pp5Q3gQdRK6AuBomZkF-` unchanged between build and server start).
- Server: `npm run start -- -p 4522` (port 4522 — free at the time, chosen to avoid the historical 7/21 ports
  4520/4521 which this new run does not reuse or overwrite).
- Collector: byte-identical copy of `docs/daily_report/7.19/.../scripts/collector.mjs` (SHA-256
  `ded59e39818501fae4de726102d7317f323cedc7151937f2c478ce4e7f6d25e1`), imported directly, no re-implementation.
- Confirmed `/en/search?q=coffee%20cup` → HTTP 307 (redirect to `/search`), same as documented in the 7/21 RUN_LOG —
  the collector follows redirects, consistent with prior runs.

## Queries run (7)
笔袋, 人体图解, 促销海报, 日历 (all zh) + logo, movie poster, product photo (all en) — the charter-specified set
(笔袋/人体图解/促销海报 required; 日历/logo/movie poster/product photo as holdouts).

Raw output: `01_AUTOMATED_SANITY_RESULTS.csv`.

## Result
All 7 queries returned `ok=true`, HTTP 200, non-empty `top5_titles`, and a populated `total_results` count. No
collector/network/HTTP errors, no empty schema fields, no zero-result. This confirms:
- runner reaches the correct (0e794cd9) frontend worktree,
- results are generated end-to-end (fetch → RSC flight decode → field extraction),
- the output schema fields used by `run_eval_single.mjs` are populated,
- no port/branch/catalog/API-endpoint mismatch is present.

**Gate: AUTOMATED_SANITY_PASS.**

## Observation flagged for the full-326 root-cause analysis (not a sanity failure)
`笔袋`'s top-2 results are unrelated tech-news templates ("microsoft ai dilemma 07 case google gemini" x2) ahead of
`Stationery` (rank 3). This is a *different* off-subject-content shape than the specific canvas-tote-bag/西式食品
alias case Fix B (`6efdd904`) targeted, and than the format-word case Fix A (`0e794cd9`) targets — worth root-causing
in the full run's Cluster-B representative-case analysis (`11_CLUSTER_AB_REPRESENTATIVE_CASES.csv`) rather than
dismissed as sanity noise. Not corrected here — no production code was modified in response to this observation, per
the charter's no-edit constraint.
