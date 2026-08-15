# 8.14 Inspiration Scale-Up — Task A

**Task:** Curify Task A — Creative Inspiration / Topic Mapping / external inspiration data scaling.
**Goal:** expand the query pool and external inspiration dataset beyond the previous pilot
(`docs/daily_report/8.8/inspiration-source-pilot/`, `docs/daily_report/8.12/inspiration-topic-pinterest/`
— 10 queries / 91 Google+Pinterest records), not repeat it. See `DAILY_REPORT.md` for exact counts
and `FINDINGS.md` / `QUERY_GAPS.md` for the analysis behind the numbers.

## Query-source definitions (do not confuse with content sources below)

| `query_source` value | Meaning |
|---|---|
| `exploration_jsonl` (**A1**) | Derived from `agentic-adhoc/visual-intent-routing/benchmarks/vir_v2/data/candidates/exploration.jsonl` (read-only reference repo). A visual-intent-routing benchmark, not organic search — 30 raw lines = 10 themes × 3 language variants. |
| `niche_topic` (**A2**) | Derived from the current Curify topic registry in the read-only `curify-frontend` repo (`messages/en/topics.json`, `lib/taxonomy.json`). |
| `user_query` (**A3**) | Would be derived from a real production user-query export (result count / clicks / CTR). **Blocked this round** — no safe local export exists; production DB access is out of scope. See `user_queries_input_schema.csv` for the documented schema a future export should match. |

## Content-source definitions (separate concept from query source)

Each collected inspiration record's `source_type` / `source_domain` (e.g. `pinterest_pin`, `pinterest.com`)
describes *where the inspiration image/page was found* — Pinterest, Behance, Google-discovered portfolio
pages, etc. A query sourced from `niche_topic` can and does produce inspiration records sourced from
Pinterest, Behance, or elsewhere. This batch's collected records are 100% `pinterest_pin` — Behance,
Dribbble, and The Dieline returned HTTP 403 to both `WebFetch` and `curl` this session (see Blockers in
`DAILY_REPORT.md`).

## Directory structure

```
query_pool.csv              full candidate query pool (A1 + A2), pre-selection, with provenance
selected_queries.csv        the queries actually selected for this batch's collection run
query_coverage.csv          per-domain rollup: pool/selected/reserved/mapped counts
QUERY_GAPS.md                topic/style/intent gap analysis that motivated query selection
SOURCE_CANDIDATES.csv        consolidated collected inspiration records (CSV form)
SOURCE_CANDIDATES_<domain>.csv   per-domain intermediate checkpoint (same records, split by domain)
inspirations.jsonl          consolidated collected inspiration records (JSONL form, canonical)
inspirations_<domain>.jsonl per-domain intermediate checkpoint
thumbnails/<domain>/        downloaded, validated thumbnail images, one subfolder per target domain
gallery.html                offline human-review gallery (open directly in a browser, no server needed)
validate_gallery.py         validation script — checks JSONL/CSV parse, id/URL/thumbnail integrity,
                             gallery-to-CSV consistency, no HTML-as-image failures, no dead links
FINDINGS.md                  narrative findings: what each query source contributed, per-domain
                             coverage findings, topic richness, external-source findings
DAILY_REPORT.md               exact counts for every question the task requires answering
user_queries_input_schema.csv documented schema for a future A3 (real user query) export
run_<domain>.py, run_<domain>_retry.py, collect_pins.py, merge_outputs.py, build_query_pool.py
                              collection/build scripts used to produce the above (kept for
                              reproducibility / re-running a future batch)
append_second_pass_silkroad_artifact_fusion.py
                              the second-pass interactive-browser addendum for silk-road/
                              modernized-artifact/cultural-fusion (see Known blockers below);
                              already applied — do not re-run without first removing the 6 rows
                              it appends, or it will duplicate them
```

The per-domain `SOURCE_CANDIDATES_<domain>.csv` / `inspirations_<domain>.jsonl` files are the
intermediate checkpoints each `run_<domain>.py` script wrote before `merge_outputs.py` combined
them into the canonical `SOURCE_CANDIDATES.csv` / `inspirations.jsonl`. They're kept for
traceability; the consolidated files are the ones to treat as authoritative.

## How to inspect the gallery

Open `gallery.html` directly in any browser (double-click, or `open gallery.html` on macOS) — it's a
fully self-contained static file with the record data embedded, no server or build step required.
Use the filters (domain, query, query source, source domain/type, topic-mapping status, review
status, free-text search) to answer: *are these actually useful inspirations for this query?*

## How to rerun / extend this batch

1. `build_query_pool.py` — rebuilds `query_pool.csv` from A1 (`exploration.jsonl`, read directly
   from the `agentic-adhoc` path) and A2 (`curify-frontend` topic registry, read directly from that
   repo path). Both source repos are read-only inputs; nothing in them is written.
2. Hand-curate `selected_queries.csv` from the pool (selection principles are documented in the
   task brief / `QUERY_GAPS.md`).
3. `run_<domain>.py` (one per target domain) collects candidates for that domain's selected queries
   and writes the per-domain checkpoint files + downloads thumbnails into `thumbnails/<domain>/`.
   `run_ecommerce_retry.py` / `run_packaging_retry.py` are retry passes for candidates that failed
   the first time (e.g. a dead thumbnail URL).
4. `merge_outputs.py` consolidates the per-domain checkpoints into `SOURCE_CANDIDATES.csv` /
   `inspirations.jsonl` and rebuilds `gallery.html`.
5. `python3 validate_gallery.py` — must print `ALL CHECKS PASSED` before treating the batch as done.

## Known blockers (see DAILY_REPORT.md / FINDINGS.md for full detail)

- **A3 (real user-query data): blocked.** No safe local export exists; would require production DB
  access this task must not use. Schema for a future export is documented in
  `user_queries_input_schema.csv`.
- **Behance / Dribbble / The Dieline: blocked for non-interactive fetch.** Both `WebFetch` and
  `curl` with a realistic browser user-agent got HTTP 403 from all three this session, forcing
  100% reliance on Pinterest for this batch's collected content. The prior pilot's Playwright-based
  browser-automation scripts (`scripts/pinterest-search-eval`, `scripts/google-image-eval`) were not
  invoked this run; a future batch run with that tooling (or interactive browser automation) would
  likely reopen these sources.
- `mogao-caves` (query S012) initially returned zero genuinely on-topic souvenir-design results
  under `WebFetch`/`curl`; a same-session follow-up using interactive Chrome browser automation
  found 2 real, verified records, confirming it was a tooling-access gap, not a genuine content
  gap. A second addendum later this session applied the same fix to the three other thin
  culture-tier3 topics (`silk-road`, `cultural-fusion`, `modernized-artifact`), each re-searched
  with more specific terms, adding 2 new verified records per topic (6 total, 2 quality-A). See
  `DAILY_REPORT.md` for detail — the same fix was not applied to the Behance/Dribbble/Dieline
  blockers, or to `mogao-caves` a second time (it remains the thinnest of the five at 2 records),
  this session.

## What this is not

This directory is data + query expansion + collection/mapping + review artifacts for internal
review. It is not frontend integration, production database integration, or Creative Exploration
product code. Integrating this data into Curify's product surfaces is handled separately.
