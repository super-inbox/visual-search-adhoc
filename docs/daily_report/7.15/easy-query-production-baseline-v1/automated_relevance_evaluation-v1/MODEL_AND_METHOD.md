# MODEL_AND_METHOD.md

## Evaluator

The evaluator is Claude (Claude Code environment, Sonnet 5), acting as a rubric-driven human-analogue judge — not a separate LLM API call, not a heuristic keyword-matching script. All query-intent interpretation, result-level labeling, semantic-drift calls, and evidence summaries in this run were authored by direct reasoning against RELEVANCE_RUBRIC.md, applied by a human operator (Claude Code) reading the actual data. Deterministic scripts (Python, in `scripts/`) are used only for: data extraction/joining, the fixed scoring-formula arithmetic (§4 of the rubric), aggregation, CSV/JSONL generation, and integrity checks — never for producing the relevance judgment itself.

## Evidence actually used, and its real scope (important — read before trusting confidence labels)

**Text evidence (used for all 328 queries, no exceptions):** `original_query`, `category`, `query_type` from the authoritative input file; `result_count_observed`, `zero_result`, `low_result`, `query_broadened`, `broadened_query`, `rewrite_observed`, `raw_rewrite_visible` (the literal on-page banner text) from the full-results record; and for every visible Top Result, `result_title`, `result_url` (including the descriptive slug segment, e.g. `template-fashion-nail-art-design-cherry-blossom`), `image_url`, and `metadata` (`inspiration` / `template` / etc.) from the Top Results long table.

**Direct screenshot visual reading (used for a bounded subset, not all 328):** the Read tool can open the saved PNGs and they were spot-checked early in this run (see below) — most render real thumbnail content, though at least one query (E001, "鲜花") showed blank/unloaded example-card thumbnails alongside otherwise-normal page chrome, which is a genuine capture-time limitation (likely lazy-loaded images that hadn't painted yet when the headless screenshot fired), not a systemic failure. Reading all 328 full-page screenshots individually was not performed — each is a large, densely detailed multi-section image, and doing so for all 328 (and again for every second-pass query) would consume a disproportionate share of the evaluation session relative to what the URL-slug text evidence already provides for a strongly template/slug-driven catalog. Screenshots were actually opened and read (via the Read tool, real pixel content, not inferred) for a bounded, disclosed set:
- All 30 Calibration Set queries (both Pass A and Pass B) — used to establish whether text-only evidence tracks visual ground truth closely enough to trust for the bulk pass.
- All 12 zero-result queries (to visually confirm a true empty state vs. a rendering glitch).
- A deterministically chosen spot-audit sample from the second-pass review population (§15.2 categories: FAIL, PARTIAL, UNJUDGABLE, LOW confidence, semantic_drift MODERATE/SEVERE, rewrite+first-pass-PASS, random 10% PASS audit) — sized to what the session can actually cover with real image reads (target: ~25-35 additional screenshots, see CALIBRATION_REPORT.md / review/adjudication_report.md for the exact list and count actually read).
- Additional ad-hoc spot-audits noted inline in batch reports where text evidence alone left a genuine ambiguity.

For the remainder of the 328 (and the remainder of the second-pass review population beyond the spot-audit sample), the evaluation is **text-evidence-only** (`evaluation_method=TEXT_EVIDENCE_ONLY`): title, URL/slug, metadata, rewrite banner text, and result counts, without opening the corresponding PNG. This is a real scope limit of this run, not a claim of full visual coverage — see §17 (limitations) of the final Chinese report.

This is disclosed explicitly so the report cannot be read as claiming full-328 pixel-level visual verification. Where a query's label rests on text evidence only, `evaluation_method` is recorded as `TEXT_EVIDENCE_ONLY`; where a screenshot was actually opened and read, it is recorded as `TEXT_PLUS_VISUAL`.

## What was not done

- No re-querying of https://www.curify-ai.com. All evaluation is against the already-saved `raw/`, `screenshots/`, and `final/*` files from the 2026-07-15 collection run.
- No external LLM API call (no OpenAI, no third-party vision API). No screenshot was uploaded anywhere.
- No modification of `raw/`, `screenshots/`, `query_input/`, or any `final/easy_query_production_baseline_*` file.
- No git commit, no push.

## Why URL slugs are treated as strong evidence

Curify's search results are backed by a fixed catalog of templates/carousels/examples with descriptive, human-authored slugs (confirmed by inspecting `raw/001_E001.json` and others — e.g. a "cherry blossom" nail-art template has `template-fashion-nail-art-design-cherry-blossom` in its URL, matching its display title exactly). Because slugs and titles are consistently descriptive rather than opaque IDs, they are a reliable proxy for the depicted subject even without opening every thumbnail — this was verified, not assumed, by cross-reading several `raw/*.json` records against their corresponding screenshots during setup.
