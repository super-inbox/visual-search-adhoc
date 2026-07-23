# Run Context — Cluster A/B Latest-Fix Full-326 Evaluation (2026-07-22)

## What this run is
This is the **post-Cluster-A-and-B latest-fix** evaluation of the Curify search-relevance pipeline. The manager has
already pushed both fixes to the remote branch
`baobao/search-relevance-prod-main-v2-r3-root-cause-fix-2026-07-19`, and this run tests the resulting HEAD commit
**`0e794cd9`** (`fix(search): format-word-aware query subject (Fix A / Cluster A)`), which sits on top of
`6efdd904` (`Fix B — single-token subject-presence bypass, 笔袋 flagship`) and `b4116648` (catalog alias strip).

## What already happened before this run
- The user manually spot-checked several former FAIL cases directly in the local website and found no obvious
  blocking issue — so this run does **not** repeat extensive UI/browser testing. It runs the full authoritative
  326-query benchmark through the same production-compatible collector/judge pipeline used on 2026-07-19 and
  2026-07-21, to get a systematic, judged (not eyeballed) answer.
- The engineering gate (unit tests, `tsc`, production build) was re-verified fresh against `0e794cd9` before any
  benchmark query was run — see `16_ENGINEERING_VALIDATION.md`.

## What this run will NOT do
- It will **not** overwrite or modify anything in `docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/` — the
  production-baseline (`c550856e`, current-main-as-of-7/21) and previous-candidate (`1e56e3f0`, pre-Cluster-A/B)
  result CSVs from that directory are read-only inputs to this run's comparison, reused verbatim (not re-collected).
- It will **not** modify any production source file in the frontend repository. If any execution blocker had made
  the benchmark impossible, this run would stop and report rather than edit search logic.
- It will **not** commit, push, create a PR, reset, rebase, merge, or switch branches in either repository.

## Directory
All new artifacts for this run live under this directory only:
`/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22/`

## Three-way comparison being produced
| role | commit | source |
|---|---|---|
| production baseline | `c550856e` (main, as of 2026-07-21) | reused CSV from 7/21 dir |
| previous candidate | `1e56e3f0` (pre-Cluster-A/B) | reused CSV from 7/21 dir |
| **latest candidate** | **`0e794cd9`** (Cluster A + B fixed) | **freshly collected this run** |
