# 8.12 Daily Report

Two independent adhoc research tasks completed today. Full detail in each task's own directory;
this is a manager-readable summary only.

---

## Task 1 — Creative Inspiration / Topic Mapping / Pinterest

Full report: [`inspiration-topic-pinterest/DAILY_REPORT.md`](inspiration-topic-pinterest/DAILY_REPORT.md)
· Visual review: [`inspiration-topic-pinterest/gallery.html`](inspiration-topic-pinterest/gallery.html)

- **Google/WebSearch pilot**: 47 records across 10 unique queries, cleaned into
  `google_pilot_clean.csv`; 47/47 Google-side thumbnails present, no duplicate source URLs.
- **Tag → Curify topic mapping**: of the 10 queries (47 records) — **3 queries / 13 records
  mapped** to existing topics, **4 queries / 20 records need product confirmation** (near-matches
  or only a broader topic exists), **3 queries / 14 records unmapped** (no matching topic exists
  today: `figure`, `business card`, `certificate`).
- **Pinterest same-query pilot**: all 10 authoritative queries attempted, **44 actual candidates**
  returned (9/10 queries returned results), of which **31 were usable** on inspection, across 8 of
  10 queries. Outbound source URLs could not be extracted for any Pinterest candidate — a confirmed
  platform limitation, not a scraping gap.
- **Conclusion**: Pinterest is **supplemental, not a replacement** for the Google/Behance pilot — it
  never matched Google's 100% outbound-URL/attribution completeness, but it did surface genuinely
  different visual styles on a few queries (sticker, business card, coffee package, flashcard).
- **Next step** (unchanged from Task 1's own report): get product confirmation on the 4
  needs-confirmation mappings and a decision on the 3 missing topics before any production
  surfacing.

---

## Task 2 — Visual Direction / Creative Exploration Trajectory SFT

Full reports: [`visual-direction-trajectory-sft/`](visual-direction-trajectory-sft/) —
`REPO_ANALYSIS.md`, `TRAJECTORY_SCHEMA.md`, `CURIFY_TRAJECTORY_EXAMPLES.jsonl`,
`BENCHMARK_PROPOSAL.md`, `MANAGER_SUMMARY.md`, `overview.html`.

Research only, per manager direction to look at how trajectory SFT methods could apply to Visual
Direction / Creative Exploration. No training, pipeline, backend, or frontend code was built.

- **gc-minimal-zine-poster** (public GitHub repo, verified real — not the typo'd "-posterr"
  variant) is a Codex Skill (markdown instructions, no code, no logged trajectory data). Useful
  patterns extracted: a fixed/variable/sample-residue reference-analysis split, numeric checkable
  fixed-system fields, a named variation-axis set with an anti-repetition rule, and a capped
  single-retry revision loop that discloses residual limitations instead of overclaiming. The
  poster-specific numbers and its eval set (rubric prompts, not a real benchmark) are explicitly
  flagged as not transferable as-is.
- **The manager-shared ChatGPT discussion link was not accessible.** WebFetch returned only the
  page title ("ChatGPT - Agentic AI Architecture State"); the share page is a JS-rendered SPA that
  serves no body content to a non-interactive fetch, and interactive browser access wasn't available
  in this environment (Chrome extension not connected). No content from that discussion was used or
  invented.
- **Workflow data vs. trajectory data**: Curify's existing 8.8 five-domain workflow research
  captured finished-project pipelines (`brief → concepts → design → final result`) with no rejected
  paths, by construction — a published case study can't show what didn't ship. Trajectory data is
  a different object: a logged decision process (`state → decision → action/tool → observation →
  evaluation → revision → final output`) that must include rejected/revised paths to be useful for
  SFT.
- **Proposed 10-stage trajectory structure**: brief understanding → reference retrieval → reference
  analysis → direction generation → direction evaluation → selection → critique (conditional) →
  revision (conditional) → generation → final output.
- **Proposed data schema** (`TRAJECTORY_SCHEMA.md`): trajectory-level fields (id, task, domain,
  user_input, references, steps, final_output, outcome, quality_labels, human_preference,
  failure_mode, provenance) and step-level fields (stage, state_summary, decision, action, tool,
  tool_input, observation, evaluation, critique, selected/rejected candidates, revision_reason).
  Every field is a short, observable, structured statement — **no hidden chain-of-thought** is
  required or stored.
- **4 proposed trajectory examples** (`CURIFY_TRAJECTORY_EXAMPLES.jsonl`, all lines independently
  valid JSON): coffee shop, brand/logo, poster, packaging. The coffee-shop example demonstrates the
  required weak-direction path — a candidate generated, evaluated as a brief mismatch, rejected with
  a stated reason, and a separate defect on the winner caught and fixed in one capped revision. All
  are labeled **proposed examples for schema illustration, not production logs**.
- **Benchmark proposal** (`BENCHMARK_PROPOSAL.md`): three separate layers — step-level,
  trajectory-level, final-output — across 11 evaluation dimensions, each split into rule-based
  checks, LLM-judge checks, and human-only review. No single scalar "visual quality" score is
  proposed.
- **Smallest recommended next pilot**: 10–20 Creative Exploration tasks across 2–3 domains, manually
  reviewed as full trajectories (not just final images), including both clean successes and
  failed/revised examples — benchmark the dimensions for gradability first; do not start
  trajectory-SFT data collection or training until that pilot shows the dimensions are usable.

---

## Notes

- Both tasks are research/data-prep only — no production frontend or backend code was changed
  today.
- Task 1's evidence (CSVs, gallery, screenshots) was completed and pushed previously; it was not
  redone or modified in this session.
- Task 2's outputs, including screenshots, were generated fresh in this session.
