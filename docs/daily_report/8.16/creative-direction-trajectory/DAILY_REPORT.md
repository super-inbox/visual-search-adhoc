# DAILY_REPORT.md — Task C, 2026-08-16 (corrected, same day)

## What this covers

Creative Direction dataset expansion, preference representation, paired baseline/personalized
experiments, observable trajectory capture, evaluation rubric, trajectory-SFT candidate
classification, and product recommendations for Curify's Creative Exploration / Brand Direction
Explorer. No model trained. No production code changed. Nothing committed or pushed.

**This version corrects a same-day error:** an earlier pass on this same task concluded the Brand
Direction Explorer tool did not exist in shipped code. It does — the earlier pass audited the wrong
git checkout (`curify-frontend`, branch `baobao/search-relevance-phrase-alias-2026-07-09`) instead of
the correct one (`curify-frontend-brand-direction-explorer`, a separate worktree on branch
`baobao/brand-direction-explorer-tool-demo-2026-08-04`, commit `322cd51f`). See
`README.md` "Audit correction" for the full account.

## Prior Task C artifacts reused

- `docs/daily_report/8.12/visual-direction-trajectory-sft/` (commits `3af4b57`, `2eac69d`): 10-stage
  trajectory vocabulary, no-hidden-CoT constraint, and workflow/trajectory/preference data-type
  distinction — reused unchanged. Not modified.
- `docs/daily_report/8.8/workflow-research-5-domains/candidates/` (this repo, prior pass): 18 real
  case-study files; **15 used** this pass as question source material.
- `docs/daily_report/8.7/brand-direction-explorer-real-effect-validation/` (in
  `curify-frontend-brand-direction-explorer`, a separate read-only worktree, not this repo): 3
  archived real end-to-end runs of the actual tool, dated 2026-08-06/07 — reused (not re-executed) as
  the source for this pass's 3 `real_current_agent` trajectories. Not modified (read-only worktree).

## FOUR EVIDENCE LAYERS (read this before the counts below — see `FINDINGS.md` for full detail)

1. **Real project-derived case studies:** 15 of 26 Creative Direction questions (`source_type:
   "project_derived_case_study"`) — briefs normalized from real published case studies already
   researched in this repo. Briefs real; directions responding to them are synthetic (no matching
   real scenario exists in the actual tool for these domains).
2. **Real current-agent briefs + real current-agent baseline trajectories:** 3 of 26 questions
   (`source_type: "real_current_agent_brief"`, `cdq-001`–`cdq-003`) and 3 of 20 trajectories
   (`execution_source: "real_current_agent"`, `traj-001/002/003-baseline`) — real field values and
   real, verbatim `gpt-4o-mini` output from the actual shipped tool, archived 2026-08-06/07.
3. **Synthetic, never to be read as real:** 8 of 26 questions, all 8 preference profiles (every
   record carries `data_type: "synthetic_experiment"`), and 17 of 20 trajectories (all 10
   personalized, plus the other 7 baselines) — hand-authored, not observed from the real system. The
   10 personalized trajectories are synthetic specifically because the real tool has no preference
   input field to send them through, a confirmed code finding as of this correction.
4. **Prior Task C research:** schema/vocabulary reused unchanged from `docs/daily_report/8.12/`.

## Exact counts

| Metric | Count |
|---|---|
| Prior Task C artifact directories reused (read-only) | 1 (`docs/daily_report/8.12/visual-direction-trajectory-sft/`) |
| Real case-study source files available (this repo) | 18 |
| Real case-study source files used this pass | 15 |
| Real case-study source files still unused (expansion-ready) | 3 |
| Creative Direction questions created | 26 |
| — real/project-derived-case-study | 15 |
| — real/current-agent-brief (corrected 2026-08-16) | 3 |
| — synthetic experimental | 8 |
| Domain breakdown | brand_design 8, merch 5, ecommerce 5, packaging 4, edtech 4 |
| Preference profiles created (all synthetic) | 8 |
| Questions flagged `personalization_candidate: true` | 12 |
| Paired cases planned | 10 |
| Paired cases attempted | 10 |
| Paired cases with at least one real arm (corrected 2026-08-16) | 3 (mixed-arm: real baseline, synthetic personalized) |
| Paired cases fully synthetic (both arms) | 7 |
| Baseline trajectories | 10 (3 real, 7 synthetic) |
| Personalized trajectories | 10 (0 real, 10 synthetic) |
| Total trajectories | 20 |
| Trajectories with `execution_source: real_current_agent` (corrected 2026-08-16; enum renamed from `real_agent_replay`) | 3 |
| Trajectories with `execution_source: synthetic_experiment` | 17 |
| Real scenarios covered by real trajectories (of 3 total in the real tool) | 3 of 3 |
| Domains with a real scenario in the current tool (of this dataset's 5) | 1 of 5 (`brand_design`-adjacent only) |
| Strong-positive SFT candidates (`strong_positive`) | 7 (all synthetic) |
| Usable-positive SFT candidates (`usable_positive`) | 8 (5 synthetic + 3 real, corrected 2026-08-16) |
| Preference-misaligned (negative examples, retained) | 4 |
| Generic/redundant (negative examples, retained) | 1 |
| Needs human review | 0 (corrected 2026-08-16 — was 3, see below) |
| Execution failures | 0 |
| Personalized wins | 5 |
| Baseline wins | 4 |
| Ties / inconclusive | 1 |
| Real human preference labels | 0 |
| Real paired (baseline-vs-personalized) A/B cases | 0 (blocked — preference not implemented, see below) |

## Correction made during this pass (second correction, same day)

An earlier same-day pass on this exact task audited only `curify-frontend` and `curify-studio`,
found no Brand Direction Explorer implementation, and concluded (a) no such tool is shipped anywhere,
and (b) an even-earlier background process's `real_agent_replay` label on 3 trajectories was
therefore fabricated — relabeling them `synthetic_experiment` with paraphrased content and
downgrading them to `sft_candidate_status: needs_human_review`.

**Both (a) and (b) were wrong.** The tool is shipped, on a separate git worktree
(`curify-frontend-brand-direction-explorer`) and branch
(`baobao/brand-direction-explorer-tool-demo-2026-08-04`, commit `322cd51f`, pushed to origin) that the
audit never checked. That worktree also contains a real, dated validation report with archived raw
API responses. This pass verified the 3 disputed trajectories field-for-field against those archived
responses (exact ID/title/subtitle/description/styleTags match; `promptModifier` had been
paraphrased and has been restored to the byte-exact original) and corrected `execution_source` to
`"real_current_agent"`, added `capture_method`/`implementation_version`/`source_reference` fields,
and reclassified `sft_candidate_status` to `usable_positive`. Reported here in full, alongside the
original (also-preserved) error, rather than silently fixed — the task's anti-fabrication requirement
applies symmetrically to false "doesn't exist" claims and false "is real" claims alike.

## Blockers

1. **The real tool covers only 3 fixed scenarios in 1 of this dataset's 5 domains** — confirmed by
   code inspection, not absence. Real trajectory-SFT data at scale needs more real scenarios/domains.
2. **No preference input exists in the real tool's request schema or prompt** — confirmed by direct
   code inspection of `app/api/brand-direction-explorer/`, `lib/brand_direction_explorer.ts`, and
   `lib/brandDirectionOpenAI.ts` (zero matches for preference/persona/reference-related terms). This
   is the primary blocker for real personalization evidence specifically.
3. No human/target-user judgments exist yet — `paired_evaluation.csv` scores, including for the 3
   real-baseline pairs, are evaluator-assigned against `EVALUATION_RUBRIC.md`, not designer/client-
   assigned.
4. Small sample (10 paired cases, only 3 with a real arm; uneven domain spread: `edtech`/`ecommerce`
   at 1 paired case each vs. 4 for `brand_design`) — findings are directional, not statistically
   powered.

## Highest-priority next action

**P0-0 (see `FINDINGS.md` §Product recommendations):** add a minimal `preferenceProfile` field to the
real tool's request schema and prompt construction (`route.ts` + `lib/brandDirectionOpenAI.ts`) —
this is the single change that would let the entire synthetic preference experiment in this dataset
become a testable claim against real output instead of a hypothesis. **P1-0:** fix the real, observed
repeated-title bug in the `coffee-opening` case (prompt-only change to `SYSTEM_PROMPT`). Both are
scoped against actual files in the real implementation, not a hypothetical future build.
