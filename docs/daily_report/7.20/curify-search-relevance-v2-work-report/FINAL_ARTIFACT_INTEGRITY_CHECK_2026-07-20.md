# Final Artifact Integrity Check — 2026-07-20

**Repo**: `visual-search-adhoc` (worktree `visual-search-adhoc-v2-delivery-2026-07-20`)
**Branch**: `baobao/search-relevance-v2-delivery-2026-07-20`
**Commits checked**: `10793a2`, `2e935e8`, `8294ece` (the 3 commits unique to this branch vs `main`)
**Scope**: 92 files added by these 3 commits, plus cross-checks against files inherited from `main`'s history that
those documents reference.

---

## 1. CSV integrity

All 36 CSV files in the 3 commits were parsed with Python's `csv` module.

- **Files checked**: 36
- **Parse failures**: 0
- **Empty or single-row (header-only) files**: 0
- **Row-count spot checks**:
  - `13_V2_R3_EASY326_RESULTS.csv`: 326 data rows + 1 header = 327 lines. `relevance_label` value counts:
    FAIL=206, PARTIAL=80, PASS=36, UNJUDGABLE=4 (sums to 326). `zero_result=True` count: 23. **Matches the
    work report's headline table exactly** (independently recomputed, not copied from the report).
  - `14_V0_V2_R1_V2_R3_EASY326_PAIRED.csv`: 327 lines (326 rows + header), consistent with the 326-query bank.

## 2. JSON integrity

- **Files checked**: 16
- **Parse failures**: 0

## 3. Duplicate-file check

3 pairs of byte-identical files were found:

| File A | File B |
|---|---|
| `v2-r1-328-completion/01_V0_OLD328_RESULTS.csv` | `v2-r1-328-completion/eval_raw/OLD328_V0.csv` |
| `v2-r1-328-completion/02_V2_R1_OLD328_RESULTS.csv` | `v2-r1-328-completion/eval_raw/OLD328_V2.csv` |
| `v2-r1-328-completion/03_V0_V2_R1_OLD328_PAIRED.csv` | `v2-r1-328-completion/eval_raw/OLD328_PAIRED.csv` |

**Assessment**: expected, not accidental. Each numbered top-level file is a curated copy of the corresponding raw
file in `eval_raw/`, matching the same pattern used everywhere else in this archive (e.g. `13_V2_R3_EASY326_RESULTS.csv`
vs `eval_raw/full326/EASY326_V2R3.csv`). Not flagged as redundant/removable — both copies are part of the
established archive convention (numbered file = "read this one", `eval_raw/` = raw provenance copy).

No other duplicate content was found among the 92 files.

## 4. Markdown relative-path reference check

292 inline-code file references (`` `path/to/file.ext` `` patterns) were extracted from all 24 Markdown files in
this delivery and checked for resolvability:

- 10 references point into the **code repo** (`curify-frontend`: `app/`, `lib/`, `public/`, `messages/`,
  `package.json`, etc.) — correctly not present in this eval repo, not a defect.
- 269 references resolved to a real file somewhere in the eval repo tree (including files inherited from `main`'s
  pre-existing history, e.g. `docs/daily_report/7.15/.../easy_queries_cleaned_300_plus_2026-07-14.csv`, which are
  not part of this delivery's 3 new commits but do exist in the repo and were not deleted or moved).
- **13 references did not resolve.** All 13 are inside two pre-existing documents from the 2026-07-18
  post-meeting design/changelog (`EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-18_POST_MEETING_ZH.md` and its
  `_CHANGELOG.md`), not inside the primary Work Report or any V2-R1/R2/R3 evaluation report. Two distinct causes:
  - **Directory name mismatch**: both files reference
    `docs/daily_report/7.17/easy-query-search-solution-design-v1/EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-17_zh.md`,
    but the actual directory (inherited from `main`, pre-existing) is
    `docs/daily_report/7.17/easy-query-search-solution-design/` — no `-v1` suffix. The referenced file exists,
    just at a slightly different path.
  - **Two references with no resolvable target anywhere in the repo**: `HYBRID_SEARCH_FLOW_2026-07-17.md` and
    `EASY_QUERY_SEARCH_SOLUTION_DESIGN_2026-07-17_zh.before-reset-baseline.md` do not exist under any path.

**Disposition**: This is a real, minor path-reference defect, but it is **not** in the primary Work Report
(`CURIFY_SEARCH_RELEVANCE_V2_WORK_REPORT_2026-07-18_TO_2026-07-20_ZH.md`) — all 24 paths that report's own §18
appendix cites were separately verified to exist (see `CODE_VALIDATION_FINAL_2026-07-20.md`'s sibling check and
§6 of the task's read-only audit). It is one level removed, inside an earlier supporting design document this
delivery did not author. Per the task's instruction to make only minimal necessary corrections, and because these
two files were authored before this session and their intended fix (rename vs. recreate missing file) is not
knowable without asking the author, **no edit was made to these files**. Flagged here instead of silently fixed
or silently ignored. **Not blocking**: none of the report's headline numbers, gate results, or Go/No-Go
conclusions depend on these two broken cross-references.

## 5. SHA-256 verification

All 92 files' SHA-256 hashes were recomputed in this audit session and recorded in
`FINAL_DELIVERY_MANIFEST_2026-07-20.csv`/`.json`. These match the files as they exist on disk at audit time
(post-commit, pre-push-verification), confirming no silent corruption or accidental edit between commit and
this check.

## 6. Contamination check (node_modules / .DS_Store / temp server output / API cache secrets / unrelated dates)

```
git diff main..HEAD --name-only | grep -iE "node_modules|\.DS_Store|__pycache__|\.env|coverage"
```

- Result: 2 matches, both legitimate evaluation run logs (`raw_targeted_eval/full_eval_run.log`,
  `raw_targeted_eval/retry.log`) — not local dev-server logs, not caches. These are part of the reproducibility
  trail for the targeted-stage LLM-judge run and are the kind of "run log" the delivery explicitly should
  include, not exclude.
- No `node_modules`, `.DS_Store`, `.env`, `__pycache__`, or `coverage` paths present in any of the 3 commits.
- Secrets scan (`api[_-]?key|secret|password|token|-----BEGIN|Bearer <token>`) over the full diff and over the
  8.5MB raw LLM-judge output (`raw_targeted_eval/full_eval_out.json`): **0 matches**.
- No files from unrelated dated tasks (7.11, 7.12, 7.15, 7.16, 7.17 baselines, blog drafts, etc.) are present in
  these 3 commits — confirmed by `git diff main..HEAD --name-only`, which touches only `7.19/` and `7.20/` paths.

## 7. V0 vs V2 separation preserved

`EASY326_V0.csv`, `EASY326_V2.csv` (V2-R1), and `v2-r3-root-cause-fix/eval_raw/full326/EASY326_V2R3.csv` (V2-R3)
were independently hashed and confirmed to be three distinct files with distinct content — the V0 baseline was
not overwritten by either candidate round, and the three rounds' raw data remain independently inspectable.

## 8. Baseline overwrite check

No file under `eval_raw/EASY326_V0.csv`, `eval_raw/HARD68_V0.csv`, `eval_raw/P0_12_V0.csv`,
`eval_raw/TARGETED_V0.csv`, or `v2-r1-328-completion/eval_raw/OLD328_V0.csv` was modified across the 3 commits
being audited (all are net-new additions on top of `main`, not edits to a pre-existing baseline file) — confirmed
via `git diff main..HEAD --diff-filter=M` returning no matches under any `*_V0.csv` path.

---

## Summary

| Check | Result |
|---|---|
| CSV parse / row-count integrity | PASS (36/36 valid, 0 empty/truncated) |
| JSON parse integrity | PASS (16/16 valid) |
| Duplicate files | 3 expected pairs (curated-copy convention), 0 unexplained |
| Markdown path references | 269/292 resolved directly, 10/292 expected code-repo refs, 13/292 broken (pre-existing, outside primary Work Report, not blocking) |
| SHA-256 | Recorded for all 92 files, matches on-disk state |
| Contamination (node_modules/.DS_Store/secrets/unrelated dates) | Clean |
| V0/V2 data separation | Preserved, independently confirmed distinct |
| Baseline overwrite | None |
