# zcool Creative Exploration Workflow — Phase 3 (Local Candidate Query Generation + Provenance)

**Phase 3 update (2026-08-07):** this phase re-verified the authoritative `agent_route` schema (unchanged), evaluated the 5 migrated baseline-pilot cases for query-derivation eligibility, and generated **6 local, provisional `creative_explore` candidate queries** with full query→case provenance. See `CREATIVE_EXPLORATION_FINDINGS.md` and `QUERY_DERIVATION_FINDINGS.md` for the phase summary and detailed analysis, and `VALIDATION_REPORT.md` for the verification checklist. The rest of this README (below) describes Phase 2 (schema verification, worktree isolation, baseline migration) and is kept as-is since it remains accurate background.

**Key facts about Phase 3, stated explicitly per task requirement:**
- The AUTHORITATIVE `agent_route` query schema has been (re-)confirmed directly from `super-inbox/curify-studio@origin/main:dev/jayw/design-agent-v0/eval/queries.jsonl` — still 118 lines, still SHA-256 `5384474f8334f352f6ce157331b7d96c68721179f5da2049fcdc8c8e0ffe2e3d`, unchanged since Phase 2.
- This phase only generates **local candidate queries** (`outputs/creative_explore_agent_route_queries.jsonl`, IDs `AR-ZCE-001`..`AR-ZCE-006`). They live only in this adhoc repo directory.
- The official `super-inbox/curify-studio` `queries.jsonl` was **not modified** — read-only access only (`git show`, no checkout, no branch switch, no write).
- `source_refs` is not part of the `agent_route` schema, so this phase's query generation **does not depend on, and does not add, any new ZCOOL `source_refs` tags** — that open governance question from Phase 2 (`query_schema/SCHEMA_MAPPING.md` §6) remains untouched and unresolved.
- Any future merge of `AR-ZCE-xxx` candidates into the official `queries.jsonl` still requires the schema owner (Jay) to review and re-confirm or re-number them — `AR-ZCE-xxx` are **provisional, adhoc-repo-local candidate IDs**, not curify-studio official numbering, and must not be treated as pre-reserved.
- `SCALE_UP_SCRAPING` remains `PAUSED`.
- `IMAGE_ACCESS_VALIDATION` remains `CONTINUE` (recommended next technical investigation, not started).

---

## Phase 2 background (unchanged)

## Location

This directory lives inside **`visual-search-adhoc`**, specifically in an isolated git worktree/branch created for this task:
- Worktree path: `/Users/baobaoli/Desktop/visual-search-adhoc-zcool-creative-exploration-2026-08-07`
- Branch: `baobao/zcool-creative-exploration-2026-08-07`
- Base: `origin/main` of `super-inbox/visual-search-adhoc`

The task's primary `visual-search-adhoc` checkout (`/Users/baobaoli/Desktop/visual-search-adhoc`) currently has an unrelated dirty working tree (uncommitted changes and untracked files from other in-flight work). **This worktree was created specifically to avoid touching that dirty state** — nothing in the main checkout was cleaned, stashed, reset, or modified to produce this directory.

## Baseline

`baseline_pilot/` contains the cleaning-rules, schema, and structured-case outputs from the **8.5 zcool design-workflow pilot** (`curify-frontend/docs/daily_report/8.5/zcool-design-workflow-pilot/`), migrated read-only into this task directory. See `baseline_pilot/MIGRATION_MANIFEST.csv` for the complete file-by-file mapping (43 rows: 31 migrated, 12 explicitly excluded).

**Not migrated**, and never will be under this task's scope: the raw zcool article text (`raw_text.md` for all 5 cases) and any image/long-image content. Only 5 lightweight zcool images ever existed as *references* in the pilot, and all 5 resolved to the same zcool placeholder URL — no real image bytes were ever retrieved by the 8.5 pilot, so there is nothing beyond a URL string to exclude on the image side. The full original-text exclusion is deliberate: republishing another platform's article text would exceed "internal data-structure verification" and is excluded regardless.

## What this phase is

1. **Phase A** — verified that the authoritative `queries.jsonl` schema is `super-inbox/curify-studio@origin/main:dev/jayw/design-agent-v0/eval/queries.jsonl`, read via `git show` without switching branches or modifying the local `curify-studio` checkout. Compared it (read-only) against the previously-flagged local copy at `curify-studio-brand-direction-explorer` — confirmed byte-identical (same SHA-256), because that directory turns out to be a `git worktree` of the same repository, pinned in detached HEAD at exactly `origin/main`. Full detail in `query_schema/QUERY_SCHEMA_PROFILE.md`.
2. **Phase B** — created the isolated worktree/branch listed above, off `origin/main`, without touching the dirty primary checkout.
3. **Phase C** — migrated the *cleaned, structured* outputs of the 8.5 pilot into this directory (this phase), and defined how (and how *not*) any future zcool-derived query would map onto the authoritative query schema (`query_schema/SCHEMA_MAPPING.md`).

## What this phase is explicitly NOT

- **No new zcool cases were scraped, searched, or fetched.** `candidates/`, `cases/`, `provenance/query_to_case_mapping.jsonl`, and both files in `outputs/` are empty placeholders.
- **No new benchmark queries were written.** Nothing was added to, or derived as a draft for, the authoritative `queries.jsonl`.
- **No commit, push, or PR was created.** All work exists only as uncommitted files in the isolated worktree.

## Status carried forward from the 8.5 pilot (unchanged)

```text
SCALE_UP_SCRAPING:        PAUSED     — unchanged; still blocked on zcool image access (see baseline_pilot/reviews/PILOT_FINDINGS.md §4)
IMAGE_ACCESS_VALIDATION:  CONTINUE   — unchanged; still the recommended next technical investigation, not yet started
```

## Query schema sourcing rule for this task

Any reference to "the query schema" in this directory's documents means, specifically and only, `super-inbox/curify-studio@origin/main:dev/jayw/design-agent-v0/eval/queries.jsonl` as it existed at commit `c74d990903d193a4c78814759bd117bfa98f4817` at the time of this audit. See `query_schema/QUERY_SCHEMA_PROFILE.md` for the full verification record. Any local copy found elsewhere (including the `curify-studio-brand-direction-explorer` worktree) is a comparison artifact only and must not be treated as authoritative on its own.

## Directory contents

```text
zcool-creative-exploration-workflow/
├── README.md                          this file
├── PROGRESS_STATUS.md                 phase-by-phase status
├── CREATIVE_EXPLORATION_FINDINGS.md   Phase 3 summary (new)
├── QUERY_DERIVATION_FINDINGS.md       Phase 3 detailed 8-point analysis (new)
├── VALIDATION_REPORT.md               Phase 3 verification checklist (new)
├── baseline_pilot/                    migrated 8.5 pilot outputs (see MIGRATION_MANIFEST.csv)
│   ├── cleaning_rules/
│   ├── schema/
│   ├── structured_cases/
│   ├── reviews/
│   └── MIGRATION_MANIFEST.csv
├── query_schema/                      authoritative schema profile + mapping analysis
│   ├── QUERY_SCHEMA_PROFILE.md
│   └── SCHEMA_MAPPING.md
├── candidates/                        still empty — next-round *new* zcool case discovery (not started, SCALE_UP_SCRAPING remains PAUSED)
├── cases/                             CASE_QUERY_ELIGIBILITY.csv (new, Phase 3) — eligibility analysis of the 5 existing baseline_pilot cases
├── provenance/                        query_to_case_mapping.jsonl (new, Phase 3) — 6 rows, one per generated candidate query
└── outputs/
    ├── creative_explore_agent_route_queries.jsonl   6 local candidate agent_route records (new, Phase 3): AR-ZCE-001..AR-ZCE-006
    └── creative_exploration_workflows.jsonl          still empty — no new case→step→asset workflow records produced this phase
```
