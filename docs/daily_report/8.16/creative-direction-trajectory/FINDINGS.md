# FINDINGS.md

**Corrected 2026-08-16 (same day).** Evidence is drawn from `creative_direction_questions.jsonl` (26
questions), `preference_profiles.jsonl` (8 profiles), `trajectory_cases.jsonl` (20 trajectories / 10
pairs), and `paired_evaluation.csv` (10 scored pairs). **Read `README.md` §"Audit correction" first**:
a same-day-earlier version of this pass wrongly concluded no Brand Direction Explorer tool was
shipped. It is shipped — in a worktree that earlier audit didn't check
(`curify-frontend-brand-direction-explorer`, branch `baobao/brand-direction-explorer-tool-demo-2026-08-04`).
3 of 20 trajectories are real, verbatim output from that tool (`execution_source:
"real_current_agent"`); the other 17, and all 8 preference profiles, remain synthetic. Sample size is
10 pairs (3 with a real baseline arm); percentages below are descriptive of this sample, not
statistically powered claims.

## Four evidence layers (do not blur these — Phase 9)

Findings below draw on four distinct kinds of evidence. Each has a different reliability and a
different claim it can support:

1. **Prior Task C research** (`docs/daily_report/8.12/visual-direction-trajectory-sft/`, commits
   `3af4b57`/`2eac69d`): a trajectory vocabulary and an external-repo concept analysis. Reused
   unchanged; supports schema-design claims, not behavior claims.
2. **Current implementation audit** (this pass, corrected 2026-08-16): direct inspection of
   `curify-frontend-brand-direction-explorer`'s actual code. Supports factual claims about what the
   real tool does and does not do today (architecture, request/response schema, preference support —
   see below). Does not by itself support claims about output *quality* at scale.
3. **Synthetic controlled preference experiment** (this pass): 8 preference profiles, 10 paired
   baseline/personalized cases, all `execution_source: "synthetic_experiment"` except the 3 baselines
   promoted to real (see layer 4). Supports hypotheses about *what kinds of preference evidence and
   failure modes a rubric can distinguish* — not proof of what the real model would actually do when
   given a preference input, because the real tool has no preference input to test this against.
4. **Real current-agent executions** (this pass, corrected 2026-08-16): 3 real, verbatim
   `gpt-4o-mini` responses from the actual tool (`traj-001/002/003-baseline`), captured 2026-08-06/07
   and archived in the tool's own worktree, reused here rather than re-run. Supports narrow, small-n
   claims about actual current baseline (no-preference) output quality for 3 specific scenarios. Does
   not support any preference/personalization claim — no real personalized counterpart exists.

Findings that mix layers 3 and 4 (e.g. `cdq-001`/`cdq-002`/`cdq-003`'s pairs) are explicitly flagged
below and in `paired_evaluation.csv` as mixed-arm: a real baseline compared against a synthetic
personalized hypothesis, not a real-vs-real comparison.

## Dataset

### 1. Can the current niche-topic + Creative Direction question dataset be meaningfully expanded?

Yes, and cheaply, before any new authoring: **3 real case-study files
(`MERCH-04-darin-michau-mascot.md`, `PACK-04-danjiaoshi-process-overview.md`,
`ECOM-04-zimu-aipl-report.md`) already exist in this repo's `workflow-research-5-domains/candidates/`
and were not used** in this 26-question pass. Converting those into `cdq-027`–`cdq-029` following the
same normalization pattern used for `cdq-004`–`cdq-018` is close to zero-research-cost expansion.
Beyond that, this pass's `synthetic_experiment` questions (11 of 26) show a repeatable pattern for
*designed* expansion: each targets one specific evaluation failure mode (ambiguity, over-constraint,
negative preference, brief-conflict, whose-preference-is-this) rather than generic brief variety —
that pattern is more valuable to keep expanding than volume alone.

### 2. Which domains/topics remain under-covered?

- **In the question dataset itself:** coverage is reasonably even (`brand_design` 8, `merch` 5,
  `ecommerce` 5, `packaging` 4, `edtech` 4) but shallow within `edtech` and `packaging` — `edtech`
  has no course/curriculum topic beyond `cdq-013`/`cdq-014`/`cdq-015`/`cdq-022` (all app/curriculum
  visual systems; no print/physical edtech product, no adult-professional-education case).
  `packaging` has no subscription/unboxing-experience case and no sustainability/regulatory-label
  case (despite `pf-007` sustainability preference profile existing with nothing paired to it).
- **In the *paired* experiment specifically:** `edtech` and `ecommerce` each got only 1 of 10 paired
  cases, versus 4 for `brand_design`. This is a real gap — the personalization findings below lean
  disproportionately on brand/merch/packaging evidence and should not yet be generalized to edtech
  or ecommerce with confidence.
- **Not covered anywhere in this dataset:** multi-application systems requiring *consistency across
  many assets* (the brief asks for one moodboard/poster per question, never "produce directions for
  a 12-piece campaign that must read as one family") — this is a real Creative Exploration use case
  (see `cdq-009`, `cdq-015`, `cdq-018` which *mention* multi-SKU/cross-subject scale as a constraint
  but the trajectory schema has no field for scoring cross-direction-set consistency at that scale).

### 3. What kinds of Creative Direction questions provide useful training/evaluation signal?

The most diagnostically useful questions in this dataset were not the "clean" briefs but the ones
built to create tension:
- **Brief-vs-preference conflict** (`cdq-019` illustrator/pf-001, `cdq-008` pet-grooming/pf-004): these
  produced this experiment's clearest `preference_misaligned` results (§Preference below) — a
  well-fit-sounding preference profile actively worked against the brief's hard requirement.
- **Feedback-derived (not stated-taste) preference** (`cdq-020`/pf-008): this produced the *strongest*
  positive personalization result in the sample — see §Preference.
- **Explicit negative preference** (`cdq-023`, "I'm done with minimalism"): cleanly separated a
  baseline that violated the stated negative constraint from a personalized arm that respected it,
  while also surfacing a distinct over-constraint side effect.
- **The one deliberately generic prompt** (`cdq-025`, "Make it look premium and modern," not run as a
  paired case) is retained specifically as a floor case for future rubric calibration — a system that
  can't ask a clarifying question or can't produce a broad initial direction spread from a genuinely
  underspecified brief is a real failure mode worth a dedicated test, not one this pass scored.

## Preference

### 4. Which types of preference evidence are useful?

Ranked by what this sample's evidence suggests, most to least reliable:
1. **`previous_client_feedback` + `rejected_concept`** (`pf-008`, used in `cdq-020`): produced this
   sample's cleanest win (`paired_evaluation.csv` cdq-020: winner=personalized, confidence=high).
   This evidence type states a *fact about what already failed*, which a generation process can act
   on unambiguously — it doesn't require interpreting taste, just avoiding a known-rejected concept.
2. **`explicit_statement` + `previous_work`/`saved_inspiration`** (most other profiles): useful for
   sharpening territory *when the brief doesn't already specify a strong aesthetic direction*
   (`cdq-011` beauty PDP + pf-006 luxury-minimal: winner=personalized, high confidence — the brief's
   own ask, "differentiate from clinical shots, stay premium," and the profile's restraint pointed
   the same way).
3. **A stated taste profile applied without checking whose preference it is** (`cdq-019`: pf-001 is a
   brand *designer's* own taste, applied to an *illustrator-client's* brief) — this was this sample's
   clearest negative case (§Preference below), not because the evidence type is bad, but because the
   preference-injection step in this dataset's schema has no field distinguishing "whose preference"
   a profile represents before applying it. This is a concrete schema/product gap, not just a data
   observation — see Product recommendations, P0.

### 5–8. Did preference improve outputs? Where did it help, do little, or hurt?

Across the 10 paired cases: **5 personalized wins, 4 baseline wins, 1 tie**
(`paired_evaluation.csv`). Preference did not uniformly help — the split is close to even, and the
*mechanism* of the win or loss is the useful signal, not the count:

**Helped (5 cases: cdq-003, cdq-011, cdq-013, cdq-020, cdq-023):**
- `cdq-020` (skincare, feedback-derived preference): personalized arm correctly avoided re-proposing
  a concept type the client had already rejected, which the baseline — lacking that evidence —
  included as one of its 3 directions. This is the sample's strongest, cleanest positive case
  precisely because the preference evidence was a fact, not a taste judgment.
- `cdq-011` (beauty PDP, luxury-minimal preference): preference and brief pointed the same direction;
  restraint satisfied both the profile and the brief's own explicit "differentiate from clinical,
  stay premium" requirement.
- `cdq-003` (event poster, maximalist-streetwear preference): the brief already asked for
  "energetic, youthful, experimental" — the profile added concrete, checkable material/typography
  specificity (halftone, sticker-sheet edges, stencil type) without narrowing diversity or
  conflicting with the brief.
- `cdq-023` (explicit "no more minimalism"): personalized arm correctly satisfied the stated negative
  constraint the baseline violated — but flagged `medium` not `high` confidence, because see
  "over-constrains" below.
- `cdq-013` (kids edtech, feedback-derived warmth preference): real improvement, but *not uniform*
  across all 3 personalized directions — only 1 of 3 preserved the baseline's parent-facing
  scannability requirement equally well. Recorded as a moderate, not unqualified, win.

**Did almost nothing / redundant (1 case: cdq-002, tie):**
- `cdq-002` (tea brand, heritage-craft preference): the baseline's own "earthy-elegance" direction
  already sat in nearly the same territory (terracotta/kraft/botanical) that all 3 personalized
  directions converged on. Preference reinforced an already-present baseline option rather than
  producing new value, while reducing the personalized set's internal diversity relative to the
  baseline's 3-way spread. This is the concrete shape of "preference does almost nothing": not zero
  effect, but effect fully redundant with what a good baseline already offered as one option among
  several.

**Over-constrained (2 cases: cdq-001, cdq-023 secondary effect):**
- `cdq-001` (coffee shop poster, luxury-minimal preference): personalized set matched the preference
  profile strongly but all 3 directions collapsed into one narrow monochrome-plus-bronze-accent
  territory — and that territory itself drifted from the brief's own "warm, memorable" requirement
  for a mass-market coffee-shop opening. Baseline won on brief_integrity and diversity despite losing
  on preference_fit.
- `cdq-023`: even in its "win," none of the 3 personalized directions offered a non-minimal-yet-still-
  credible middle ground the brief's audience (prospective creative-industry clients) plausibly needs
  — satisfying the negative preference correctly still narrowed the option space more than ideal.

**Conflicted with the brief / whose-preference-is-this (2 cases: cdq-008, cdq-019, both baseline wins):**
- `cdq-008` (pet grooming packaging, tech-startup-clean preference): all 3 personalized directions
  dropped the explanatory-illustration device the baseline used to solve the brief's actual hard
  constraint ("product is unfamiliar — packaging must carry explanatory weight"). A SaaS-brand
  preference profile is a poor fit for a shelf product that must explain an unfamiliar mechanism to a
  browsing shopper — preference actively worked against a brief requirement, not just a style clash.
- `cdq-019` (illustrator merch, restrained-editorial preference): the preference profile was a brand
  *designer's own* taste, applied to an *illustrator-client's* brief — it suppressed the illustrator's
  actual established medium (illustration) in favor of the profile's typographic restraint. This is
  the sample's clearest "whose preference is this" failure: the mechanism didn't fail because the
  preference was badly specified, but because nothing checked whether this preference source was
  even the right one to apply to this brief.

**No reference-copying case occurred in this sample** — every personalized trajectory adapted the
preference profile's structured fields to the specific brief rather than reproducing a positive
reference verbatim. This is a gap in this sample (not evidence the failure mode doesn't matter): none
of the 8 preference profiles' `positive_references` are concrete enough (they're named categories —
"Kinfolk magazine cover layouts" — not source assets) for a real system to literally copy from. A
real reference-copying test needs actual reference *images*, which this dataset doesn't include
(see Blockers).

### 9. How should saved inspiration potentially feed preference memory?

Treated as a hypothesis only (see `README.md` §Preference representation), tested indirectly through
`pf-008`'s evidence shape. The useful finding: **the most reliable preference evidence in this sample
was fact-shaped (what was previously rejected/approved), not taste-shaped (what someone says they
like)**. A saved-inspiration pipeline should therefore prioritize capturing *decisions* (what a user
saved vs. discarded, what a client approved vs. rejected) over free-text taste statements, and should
summarize that evidence into the same `structured_preference` shape used here (color, typography,
layout_density, etc.) rather than passing raw saved images as an unstructured blob — the
`preference_injection` trajectory stage in `TRAJECTORY_SCHEMA.md` only works as an observable,
checkable step because the input it logs is already structured. It should also carry a "whose
preference / for what role" tag (client vs. designer vs. brand-system-owner) — the `cdq-019` failure
above is exactly the case a saved-inspiration pipeline would hit if it didn't track that.

## Preference status (Phase 4/7/9 — corrected 2026-08-16)

### What we know (from the synthetic controlled experiment — layer 3)

Ranked by which preference-evidence types produced the cleanest wins/losses in the synthetic sample:
feedback/rejection-derived evidence (`pf-008`) outperformed stated-taste evidence; "whose preference
is this" and over-constraint were this sample's two clearest failure modes (see items 4–8 above).
**This is a hypothesis about what a preference mechanism would need to get right, not evidence about
how the real tool behaves with preference input** — the real tool has none.

### What the current implementation supports

**Absent.** Confirmed by direct code inspection of `app/api/brand-direction-explorer/`,
`lib/brand_direction_explorer.ts`, and `lib/brandDirectionOpenAI.ts` (see `README.md` "Audit
correction" → "Preference support"): the request schema is `{caseId, fieldValues}` only, the OpenAI
system prompt has no preference/persona instruction, and a case-insensitive search for `preference`,
`persona`, `saved.?inspiration`, `liked/disliked.?reference`, `reference.?image`, `prior.?selection`,
`user.?profile` across every file in the feature returns zero matches. This is option **C** of
Phase 4's A/B/C choice, not A or B.

### What real-agent evidence shows

Nothing — there is no real personalized execution to show anything from. The 3 real trajectories
(`traj-001/002/003-baseline`) are all baseline (no-preference) calls, because that is the only kind of
call the real tool's schema permits.

### What is still missing

1. A real preference/reference input field in the request schema and prompt (currently absent
   entirely — see Product recommendations P0 below for the smallest version of this).
2. A real preference-evidence pipeline (saved-inspiration capture, like/dislike storage, client-
   feedback ingestion) — none exists; `preference_profiles.jsonl` is entirely synthetic.
3. Real human/target-user judgments of any kind — even the 3 real baseline trajectories are only
   evaluator-scored against the rubric (this pass's own process), not designer/client-scored.
4. A real paired baseline-vs-personalized comparison — cannot exist until (1) exists.

## Evaluation

### 10. What does a "good Creative Direction" look like?

Not a single property. The best-performing trajectories in this sample (`sft_candidate_status:
strong_positive`, 7 of 20) share a pattern: each of the 3 returned directions solves the brief's
actual hard requirement through a *structurally different mechanism* (e.g. `cdq-006`'s blind-box
directions: one line-work family, one material-variation family, one expression-driven family — not
three color palettes on the same idea), and every direction carries checkable, non-generic detail
across composition/palette/material/typography rather than mood adjectives alone. See
`EVALUATION_RUBRIC.md` dimensions 2, 3, 6, 7 for the checkable version of this.

### 11. Can richness/diversity be evaluated without one single metric?

Yes — and collapsing to one score would have hidden this sample's most useful findings. `cdq-001` and
`cdq-011` both show `preference_fit` = 4–5, but `cdq-001` loses on `diversity`/`brief_integrity` while
`cdq-011` wins on both. A single aggregate score would likely have rated these similarly high; the
8-dimension breakdown is what makes the over-constraining failure mode visible at all. This is the
core justification for `EVALUATION_RUBRIC.md`'s no-single-score design.

### 12. Which dimensions were most discriminative?

Across the 10 pairs, `diversity`, `preference_fit`, and `brief_integrity` showed the widest
baseline-vs-personalized spread and did the most work distinguishing winners; `relevance` and
`specificity` were consistently high on both arms in this sample (both baseline and personalized
trajectories were authored to a similar specificity floor) and therefore discriminated less between
arms — though they would likely discriminate more once real (non-hand-authored) outputs of varying
quality are being compared, since specificity variance in this sample is artificially compressed by
the authoring process itself (see Blockers).

## Real current-agent execution (Phase 6/9 — layer 4)

3 of the real tool's 3 total scenarios were captured as real trajectories — all of them, since the
real tool has only `coffee-opening`, `tea-brand-exploration`, and `event-poster` and no other real
scenario existed to sample from. All 3 succeeded (`execution_status: "success"`, HTTP 200,
latency 8.6–10.6s, exactly 3 unique directions each). One concrete quality gap was already documented
in the source validation report and is preserved here: the `coffee-opening` run's 3 directions all
share `title.en` "Morrow Coffee" (subtitle/description/tags differ) — the schema requires non-empty
bilingual titles but not that they differ, a real, observed content-quality gap worth a prompt-tuning
pass. No execution failures occurred in this small sample; this does not mean failures don't occur at
scale, only that none appeared in these 3 real calls.

## Trajectory

### 13. What observable agent trajectory should be retained?

Per `TRAJECTORY_SCHEMA.md`: `user_input`, `preference_input` (verbatim profile, for personalized
cases), `tool_calls`/`tool_results` (or their honest absence, as here), `creative_directions` (the
actual structured output), `final_answer`, `execution_status`, `evaluator_results`,
`sft_candidate_status`, and `notes` explaining *why* a case was classified as it was. Explicitly not
retained: any unrestricted internal reasoning trace — every trajectory in this dataset's `notes` field
is a short, structured, observable justification, never a claimed chain-of-thought.

### 14. What makes a strong trajectory-SFT candidate?

From this sample's 7 `strong_positive` cases: (1) the output solves the brief's actual constraint,
not a generic version of it, (2) directions are structurally diverse, not wording variants, (3) for
personalized cases, the preference input is traceable in concrete `promptModifier` content, not just
`styleTags`, and (4) `brief_integrity` stays high even when preference is applied. Notably, **the
"whose preference is this" and "over-constraining" failures were not obviously bad on first read** —
`cdq-001`'s personalized output is polished and internally coherent; it fails only against the brief
comparison. This means SFT candidate selection cannot be done by reading a single trajectory in
isolation — the *paired* comparison is what surfaces the failure, which has a direct implication for
future data collection (see Blockers below).

### 15. What recurring failure trajectories should be excluded or retained as negative examples?

Retain, don't exclude, the 4 `preference_misaligned` and 1 `generic_redundant` cases in this dataset
— they are exactly the shape of negative example a preference-aware SFT pass would need to avoid
regressing on (brief-override, whose-preference-is-this, redundant-with-baseline). Exclude only
`execution_status: failure` cases (none occurred in this sample).

**Corrected 2026-08-16:** `traj-001-baseline`, `traj-002-baseline`, `traj-003-baseline` were
previously flagged `needs_human_review` on the (wrong) theory that they were corrected-from-fabricated
synthetic content needing a real execution to validate against. They now *are* verified real
executions (`execution_source: "real_current_agent"`, see `README.md` "Audit correction") and have
been reclassified to `usable_positive` — real, successful, structurally-3-distinct-directions output,
with one documented quality caveat each (see "Real current-agent execution" above). They are not
`strong_positive`: no human/target-user judgment has scored them, and the `coffee-opening` case has
the repeated-title gap. This reclassification is evidence-based (rubric-adjacent read of a verified
real response), not a return to the earlier (also wrong) unconditional `real_agent_replay` label.

### 16. What remains missing before actual trajectory SFT?

See Blockers in `README.md`, "SFT status" below, and Product recommendations below — summarized:
(1) more real scenarios (the real tool covers only 3 fixed cases across 1 of this dataset's 5
domains), (2) a real preference input to execute against (none exists in the real tool's schema —
this is now a confirmed code finding, not a hypothesis), (3) real human/target-user judgments (this
pass's scores, including for the 3 real trajectories, are evaluator-assigned against a rubric, not
designer/client-assigned), (4) a larger, better-balanced sample across domains, and (5)
reference-image input, which the real tool does not accept (see "no reference-copying case occurred,"
§Preference above, now confirmed by code inspection rather than only inferred from the dataset).

## SFT status (Phase 10 — corrected 2026-08-16)

Three distinct sources, not to be conflated:

**Synthetic trajectory fixtures** — 17 of 20 trajectories (all 10 personalized, plus 7 of 10
baselines). Useful for: format/schema development (this is what shaped `TRAJECTORY_SCHEMA.md`'s
fields), evaluator development (`EVALUATION_RUBRIC.md` was tuned against these), and a
positive/negative taxonomy (`strong_positive`/`usable_positive`/`preference_misaligned`/
`generic_redundant`, 7/5/4/1 of the synthetic set respectively). **Not production training-ready** —
none of it was observed from the real system.

**Real current-agent trajectories** — 3 of 20 (`traj-001/002/003-baseline`), all `usable_positive`.
Useful for: actual current-behavior analysis (e.g. the repeated-title gap is a real, not hypothesized,
finding) and as the first 3 candidates for a future trajectory-SFT dataset once more exist. Not yet
enough to train anything: n=3, one domain-adjacent scenario set, no preference axis, no human labels.

**Strong real SFT candidates today: 0.** All 3 real trajectories are `usable_positive`, not
`strong_positive` — none has a human/target-user judgment, and one has a known quality gap. 0 real
personalized trajectories exist at all (blocked by preference not being implemented).

**Human preference labels** — 0 real ones exist anywhere in this dataset. `paired_evaluation.csv`'s
`winner`/`confidence` columns are this pass's own evaluator judgment against `EVALUATION_RUBRIC.md`,
for both the synthetic and the 3 mixed-arm real-baseline pairs. Needed for: personalized alignment
claims, reliable winner labels, and any preference-grounded SFT target — none of which can be claimed
from evaluator-assigned scores alone, real trajectory or not.

**Minimum additional dataset before actual trajectory SFT training:** (a) a real preference input
implemented in the tool (see Product recommendations P0 below) so real personalized trajectories can
exist at all; (b) real trajectories across more than 3 scenarios/1 domain — ideally one real scenario
per domain this dataset covers; (c) real human or target-user (designer/client) preference judgments
on at least a subset of real paired trajectories, not evaluator-assigned rubric scores; (d) enough
real paired volume (rule of thumb: at least the 10-pair scale already reached synthetically, but
real) to make a directional claim about personalization's real effect, mirroring what this pass did
synthetically but with real data. None of (a)–(d) exist yet.

---

## Product iteration recommendations (Phase 11 — corrected 2026-08-16)

**Corrected framing:** the prior version of this section reasoned "production iteration is not
justified because the tool does not exist." That premise is false — the tool exists, ships on a
pushed branch, and has a real, passing validation report. Recommendations below are corrected to
reason from the actual current implementation instead. Every recommendation below cites the specific
evidence it's drawn from.

### P0 — Highest priority

**P0-0. Add a minimal preference/reference input to the real request and prompt — this is the
prerequisite for every other preference finding in this document to become testable in reality.**
- *Problem:* the real tool (`app/api/brand-direction-explorer/directions/route.ts` →
  `lib/brandDirectionOpenAI.ts`) has no preference/persona/reference field anywhere in its request
  schema or system prompt (confirmed by code inspection — see "Preference status" above). Every
  preference finding in this document (P0-1/P0-2/P1-2 below, and the entire synthetic experiment) is
  currently untestable against the real system.
- *Evidence:* direct inspection of `lib/brand_direction_explorer.ts` (`buildProjectBrief`,
  `buildBrandDirectionPrompt`), `lib/brandDirectionOpenAI.ts` (`SYSTEM_PROMPT`, `buildUserMessage`),
  and `app/api/brand-direction-explorer/directions/route.ts` (`validateFieldValues`) — none accept or
  reference a preference input.
- *Proposed change (smallest useful version):* one optional `preferenceProfile` object in the POST
  body (`{caseId, fieldValues, preferenceProfile?}`), validated in `route.ts` alongside
  `validateFieldValues`, summarized into a short instruction block appended to `buildUserMessage()` in
  `lib/brandDirectionOpenAI.ts` (mirroring how `preference_injection` is already modeled in
  `TRAJECTORY_SCHEMA.md` §1/§6) — reusing the `structured_preference` shape already designed in
  `preference_profiles.jsonl` rather than inventing a new one. No UI change is required for a first,
  API-only version; `BrandDirectionExplorerClient.tsx` can gain a UI affordance in a later iteration.
- *Expected impact:* unblocks a real paired A/B test (Phase 7), turning every preference finding above
  from a synthetic hypothesis into a testable claim.
- *Implementation area:* `app/api/brand-direction-explorer/directions/route.ts` (request schema),
  `lib/brandDirectionOpenAI.ts` (prompt construction), `lib/brand_direction_explorer.ts` (types).

**P0-1. Track "whose preference this is" as a first-class field before applying any preference
profile to a brief.**
- *Problem:* Applying a preference source to the wrong role in the brief silently produces
  polished-looking but brief-violating output.
- *Evidence:* `cdq-019` (traj-005-personalized) — a brand designer's own taste profile (`pf-001`)
  overrode an illustrator-client's established medium; `paired_evaluation.csv` scored this a clean
  `baseline` win, `high` confidence.
- *Proposed change:* preference profiles need a `role` / `applies_to` field (e.g. `client`,
  `end_designer`, `brand_system_owner`) checked against the brief's own stated author/decision-maker
  before injection.
- *Expected impact:* removes this sample's clearest, highest-confidence failure mode.
- *Implementation area:* data schema (preference profile) + prompt/agent (a gating check before
  `preference_injection`, per `TRAJECTORY_SCHEMA.md` §5–6).

**P0-2. Add a diversity/over-constraint check as a generation-time gate, not just a post-hoc eval
dimension.**
- *Problem:* personalized generations can be internally polished yet collapse all 3 directions into
  one territory.
- *Evidence:* `cdq-001` (bronze-monochrome collapse), `cdq-023` (correct on preference, still no
  non-minimal-yet-credible middle option) — 2 of 10 paired cases show this pattern even in a small
  sample.
- *Proposed change:* an explicit instruction/check requiring returned directions to vary on at least
  2 independent axes (composition, palette, material, imagery source) even under a strong preference
  input — directly reusable from `agentic-adhoc`'s `variation-engine.md` anti-mode-collapse rule
  (see prior Task C research, `REPO_ANALYSIS.md` item B.3).
- *Expected impact:* addresses 2 of this sample's 10 cases directly; likely proportionally larger at
  scale given how natural over-constraint is once a strong preference profile is present.
- *Implementation area:* prompt/agent.

### P1 — Quality improvements

**P1-0. Fix repeated-title generation for single-entity cases (a real, observed bug).**
- *Problem:* the `coffee-opening` case's real captured run returned all 3 directions sharing the
  identical `title.en` ("Morrow Coffee") — differing only in subtitle/description/tags. Already
  documented as a known limitation in the source validation report.
- *Evidence:* `traj-001-baseline` (real, `execution_source: "real_current_agent"`) — this is not a
  synthetic hypothesis, it is an observed real output.
- *Proposed change:* add an explicit rule to `SYSTEM_PROMPT` in `lib/brandDirectionOpenAI.ts`
  requiring the 3 `title` values to be non-identical (the schema currently only requires non-empty
  bilingual strings via `parseAndValidateDirections`'s `isBilingual` check, not distinctness).
- *Expected impact:* directly fixes a confirmed real quality gap; cheap (prompt-only) change.
- *Implementation area:* `lib/brandDirectionOpenAI.ts` (`SYSTEM_PROMPT` rules list).

**P1-1. Score/gate against brief hard-constraints explicitly, separate from general "relevance."**
- *Problem:* preference can satisfy taste while dropping a load-bearing brief requirement.
- *Evidence:* `cdq-008` — personalized directions dropped the explanatory-illustration device needed
  to solve the brief's stated hard constraint ("product is unfamiliar — packaging must carry
  explanatory weight").
- *Proposed change:* extract explicit hard constraints from `constraints[]` (already present in the
  question schema) as a checklist scored independently of style/preference fit.
- *Expected impact:* would have caught this case before it reached evaluation.
- *Implementation area:* evaluation (rubric), prompt/agent.

**P1-2. Prefer feedback/rejection-derived preference evidence over stated-taste evidence when both
are available.**
- *Evidence:* `cdq-020` (feedback-derived) was this sample's cleanest, highest-confidence win;
  taste-derived profiles produced 2 of this sample's 4 baseline-win (preference-hurt) cases.
- *Proposed change:* when both evidence types exist for a user, weight feedback/rejection history
  higher in preference summarization.
- *Expected impact:* directional improvement in preference reliability, based on this sample's
  evidence-type comparison (§Preference, item 4).
- *Implementation area:* data / prompt.

### P2 — Product/data opportunities

**P2-1. Persistent preference memory + saved-inspiration ingestion**, structured per
`preference_profiles.jsonl`'s schema (evidence[] + structured_preference), not as raw unstructured
reference dumps. *Evidence:* this schema is what made `preference_injection` an observable, checkable
trajectory step at all (see Finding 9). *Implementation area:* data, backend.

**P2-2. Explicit like/dislike + rejected-concept capture as a first-class feedback UI**, since
rejection-derived evidence outperformed stated-taste evidence in this sample. *Implementation area:*
frontend, data.

**P2-3. Direction-selection feedback loop** (which of N directions a user actually picked) as future
real trajectory data — the real tool ships today with no telemetry linking "which of the 3 directions
did the user pick" to the Stage-2 generation call (confirmed by inspecting
`BrandDirectionExplorerClient.tsx`'s `handleGenerateClick`/`generate()` call, which threads
`selectedDirection` through `meta` for its own UI state but does not appear to log this server-side).
This is the single highest-value real data source for actual trajectory-SFT training once it exists,
since it's a real human preference judgment collected for free during normal product use.
*Implementation area:* frontend (already has the selection in state), backend/telemetry (needs a log
sink).

### P2-4. Saved-inspiration → preference-memory data contract, fitted to the real architecture (Phase 12)

The product hypothesis (saved inspiration → persistent preference evidence → preference profile →
personalized Creative Direction) is retained as a hypothesis only — **not built, not shipped, no
desktop companion** — but can now be scoped against the real request flow instead of an abstract one:

- **Minimum data contract:** a `preferenceProfile` object shaped like this dataset's
  `preference_profiles.jsonl` records (`structured_preference` + a small `evidence[]` list,
  prioritizing `previous_client_feedback`/`rejected_concept`-type evidence per Finding 9 above) — the
  same shape P0-0 proposes adding to the real POST body.
- **Where it would enter the real flow:** `route.ts`'s request body (alongside `caseId`/`fieldValues`)
  → summarized in `buildUserMessage()` (`lib/brandDirectionOpenAI.ts`) as an added instruction block,
  the same point `TRAJECTORY_SCHEMA.md`'s `preference_injection` stage already models.
  `BrandDirectionExplorerClient.tsx` would need a UI affordance to attach a saved profile (none exists
  today) but the *server-side* plumbing point is exactly P0-0's.
  `services/useFreeformGenerate.ts` (Stage 2) already accepts an optional `referenceImageUrl`
  generically — unused by this feature today — which is the more natural entry point for a saved
  *reference image* specifically, as opposed to a structured taste profile for Stage 1.
- **Not yet defined:** where "saved inspirations" would actually be stored/retrieved from (no such
  store exists anywhere in the inspected code), and how a raw saved item becomes the structured
  `evidence[]` shape above — this pass's synthetic `pf-008` models the *output* shape, not the
  ingestion pipeline that would produce it.

### Corrected: does the evidence justify a concrete next production-code iteration of Brand Direction Explorer?

**Corrected 2026-08-16.** The premise of the earlier answer ("no — the tool doesn't exist") is false.
Reasoning from the real, current implementation instead:

1. **What currently exists:** a shipped (pushed, tested, validated) Stage-1 OpenAI-backed direction
   generator for 3 fixed scenarios, feeding an unchanged, pre-existing Gemini-backed Stage-2 image
   generator.
2. **What it does well:** real, live generation (not static/hand-curated); strict output validation
   with retry (`parseAndValidateDirections`); clean Stage 1/Stage 2 separation; sanitized
   error-handling with no fallback content to mask failures; 54/54 tests passing.
3. **What it does not support yet:** preference/persona/reference input of any kind (P0-0); more than
   3 scenarios/1 domain; distinct titles across directions in every case (P1-0, confirmed real bug);
   direction-selection telemetry (P2-3).
4. **Is preference implemented:** No (confirmed by code inspection, not inference).
5. **Smallest next production-code iteration:** **P0-0** (the minimal preference input contract) —
   not "build the tool," since it is already built. This single, small, API-schema-level change is
   what would let every other finding in this document (the synthetic preference experiment, the
   evaluation rubric, the SFT-candidate taxonomy) become testable against real output instead of
   hypothesis.
6. **Data/telemetry to collect before trajectory SFT:** direction-selection logging (P2-3) is the
   cheapest real signal available today, even before P0-0 ships — it requires no new input schema,
   only logging what the client already knows client-side.
7. **Before actual SFT training:** see "SFT status" above — (a) P0-0 shipped, (b) real trajectories
   across more scenarios/domains, (c) real human/target-user preference judgments, (d) real paired
   volume at roughly this pass's synthetic scale (10 pairs) or more. None of these exist yet; 0 is the
   correct current count for real personalized trajectories and real human preference labels.
