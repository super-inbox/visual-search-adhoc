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
`REPO_ANALYSIS.md`, `DISCUSSION_ANALYSIS.md`, `TRAJECTORY_SCHEMA.md`,
`CURIFY_TRAJECTORY_EXAMPLES.jsonl`, `BENCHMARK_PROPOSAL.md`, `MANAGER_SUMMARY.md`, `overview.html`.

Research only, per manager direction to look at how trajectory SFT methods could apply to Visual
Direction / Creative Exploration. No training, pipeline, backend, or frontend code was built. This
entry reflects an **incremental correction-and-completion pass**: the manager-shared discussion,
previously inaccessible, has now been incorporated.

- **gc-minimal-zine-poster** (public GitHub repo, verified real — not the typo'd "-posterr"
  variant) is a Codex Skill (markdown instructions, no code, no logged trajectory data). Useful
  patterns extracted: a fixed/variable/sample-residue reference-analysis split, numeric checkable
  fixed-system fields, a named variation-axis set with an anti-repetition rule, and a capped
  single-retry revision loop that discloses residual limitations instead of overclaiming. The
  poster-specific numbers and its eval set (rubric prompts, not a real benchmark) are explicitly
  flagged as not transferable as-is.
- **The public ChatGPT share was not directly machine-readable during the initial pass** — WebFetch
  returned only the page title, and interactive browser access wasn't available in that environment
  — **but the discussion transcript was subsequently provided directly by the user/manager and has
  now been incorporated** (`DISCUSSION_ANALYSIS.md`). No content from it was invented.
- **Workflow data vs. trajectory data vs. preference data**: Curify's existing 8.8 five-domain
  workflow research captured finished-project pipelines (`brief → concepts → design → final
  result`) with no rejected paths, by construction. Trajectory data is a different object: a logged
  decision process (`state → decision → action/tool → observation → evaluation → revision → final
  output`) including rejected/revised paths. The incorporated discussion adds a third object,
  **preference/taste data** — pairwise comparisons between candidates ("A > C"), used for judge/
  reward models or DPO-style training, not a record of process.
- **Distill observable behavior/action policy, not hidden CoT**: the discussion's central claim.
  Trajectory SFT should train `state + tools + history → next action/tool/arguments/concise
  decision`, never an unrestricted reasoning trace — consistent with, and reinforcing, this
  research's existing no-hidden-CoT schema constraint.
- **Harness → Trajectory → Preference**: a three-layer framing from the discussion — the harness
  (workflow/tools) is designed first, trajectory data trains the next-action policy, preference data
  trains taste. The insight that the valuable asset may be "100k decisions about what changes next,"
  not "100k design images," reframes what counts as a data asset.
- **11-stage trajectory structure** (10 core + 1 new conditional stage): brief understanding →
  reference retrieval → reference analysis → direction generation → direction evaluation →
  selection → critique (conditional) → revision (conditional) → generation → **client feedback
  (conditional, new)** → final output. The new `client_feedback` stage captures the discussion's
  `BEFORE → HUMAN/CLIENT FEEDBACK → AFTER` pattern (e.g. "this feels too cheap" → concrete design
  changes → "this is right"), added to `TRAJECTORY_SCHEMA.md` and demonstrated end-to-end in the
  packaging example below.
- **Recovery trajectories**: the discussion names `wrong result → detect → diagnose → change →
  verify` as a meaningful distinction between a strong agent and a demo, and recommends a dedicated
  Recovery benchmark dimension. The existing coffee-shop example already demonstrated this pattern
  and needed no change; Recovery is now a named benchmark dimension.
- **Semantic robustness / interface-perturbation caveat (new)**: trajectory SFT on one fixed tool
  schema risks teaching interface memorization (token/schema matching) instead of tool-use
  semantics. `BENCHMARK_PROPOSAL.md` now has a dedicated section recommending tool-rename, schema-
  perturbation, tool-ordering, and alternate-generator/source tests for any future evaluation.
- **4 proposed trajectory examples** (`CURIFY_TRAJECTORY_EXAMPLES.jsonl`, all lines independently
  valid JSON): coffee shop, brand/logo, poster, packaging. The coffee-shop example demonstrates the
  required weak-direction/recovery path. The packaging example was extended (steps 8–10) to
  demonstrate the before → client-feedback → after pattern, closing with an explicit
  `final_acceptance: true`. All remain labeled **proposed examples for schema illustration, not
  production logs**.
- **Benchmark proposal** (`BENCHMARK_PROPOSAL.md`): three separate layers — step-level,
  trajectory-level, final-output — now across **18 evaluation dimensions** (11 original + 7 added:
  recovery rate/quality, tool-call correctness, turns to completion, cost/efficiency, human
  preference, cross-asset consistency, production readiness). No single scalar "visual quality"
  score is proposed. This small internal pilot benchmark is explicitly distinguished from a much
  larger, not-yet-built future Curify Design Agent Benchmark the discussion describes as a possible
  strategic asset.
- **Curify's possible moat** (strategic framing from the discussion, not a product decision made
  here): **Workflow × Trajectory Data × Evaluation**, with the underlying model kept replaceable.
  Points toward a narrower product niche hypothesis — **Brief → Design System → Product Family →
  Production** — recorded for reference, not scoped or implemented.
- **Two-phase pilot roadmap**: **Phase 0** (unchanged from the original recommendation) — 10–20
  Creative Exploration tasks across 2–3 domains, manually reviewed as full trajectories, including
  clean successes and failed/revised examples, testing whether the dimensions are gradable before
  any training. **Phase 1** (only if Phase 0 succeeds; the source discussion's proposed next-stage
  MVP shape, not a committed plan) — roughly 300–500 design briefs, a teacher agent running 4–8
  trajectories per brief, training a permitted/open-weight student on the same harness, blind
  teacher-vs-student evaluation. Any real Phase 1 run requires a data-provenance/compliance check on
  the teacher model/provider's terms first.

---

## Notes

- Both tasks are research/data-prep only — no production frontend or backend code was changed
  today.
- Task 1's evidence (CSVs, gallery, screenshots) was completed and pushed previously; it was not
  redone or modified in this session, and its numbers above are unchanged.
- Task 2's outputs were originally generated in an earlier session; this entry reflects a later
  incremental pass that incorporated the manager-provided discussion transcript (`DISCUSSION_ANALYSIS.md`,
  new) and updated the schema, examples, benchmark, manager summary, and `overview.html` accordingly.
  Screenshots were regenerated to match.
