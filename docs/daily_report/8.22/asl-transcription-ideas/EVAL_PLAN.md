# Evaluation Plan

> **Update 2026-08-23:** Per boss-provided ground truth, ASL translation
> already has real, SEO-driven user demand and a live baseline (frame
> sampling + generic VLM, "**Baseline 0**" in `SOLUTION_OPTIONS.md`) whose
> quality is currently poor. This changes the eval plan's priority: the
> first job is no longer "does any automated ASL path exist to evaluate" —
> it's "characterize exactly why the live baseline underperforms, using the
> error taxonomy in `CURRENT_VLM_BASELINE_DIAGNOSIS.md`, and compare it
> against the cheapest possible improvements (Baselines 1–2)." The
> historical-data guidance below is unchanged, but the eval priority order
> at the bottom of this doc now leads with the Baseline 0 vs. 1 vs. 2
> comparison (see `EXPERIMENT_PRIORITY.md`) rather than treating any
> automated result as a novelty. Baseline 3 joins the same round only if a
> real, loadable open checkpoint is found.

## On accessing historical Supabase ASL projects

Per the task constraint, I did **not** query production Supabase directly —
I found no existing tool in `curify-studio` that is clearly built for safe,
scoped extraction of user projects by content-type/keyword (there is generic
DB access in `curify_background/app/database.py` and
`curify_background/app/crud/admin.py`, and an `admin_portal/` app, but nothing
purpose-built for "pull ASL-tagged jobs anonymized for eval use"). Building
that extraction tool is itself a small, well-scoped first task — not
something to improvise against a production database during an ideation
pass.

**What's already known without any new query**, from committed docs/code:
- At least one real, named user request (user 1252) with two uploaded ASL
  videos and a failed automated job — documented in `gtm_tools/send_1252_asl.py`.
- Real demand signal via blog traffic to `/blog/asl-video-translator`
  (per `docs/asl-translation-mvp-spec.md`, `docs/workstream-tooling-and-engineering.md`).
- A `project_asl_captioning_demand` memory record referenced (but not itself
  read here) as the source of the "docked" decision history.

**Recommended safe extraction process** (for whoever runs Stage 1/2 of the
intern spec, not something to do ad hoc):
1. Query Supabase for jobs/projects filtered on a non-PII signal that's
   already a first-class field if one exists (e.g., `content_type`, source
   registry tool = `asl-video-translator`, or `has_speech()`-rejected job
   status) — not by scanning free-text user data.
2. Pull only the fields needed for eval (video reference/duration, job
   status/failure reason, any existing translation output) — exclude
   account email/PII from the working eval dataset entirely.
3. Get explicit sign-off (from whoever owns user-data policy) before using
   any real user video as a training or public benchmark asset; internal
   eval-only use of a small, access-controlled sample is a much lower bar
   than that, but still needs an owner's approval since these are real user
   uploads, not licensed research data.
4. Prefer public academic datasets (How2Sign, YouTube-ASL, Phoenix-2014T,
   CSL-Daily) for *quantitative benchmark* comparisons across model options —
   reserve the real Curify user sample for *qualitative, product-realism*
   validation (real user videos are more likely to have the messy properties
   described in `ASL_PROBLEM_FRAMING.md` — camera cuts, mixed audio, casual
   framing — that clean academic benchmarks don't capture).

## What to measure

| Dimension | Why it matters | How to measure |
|---|---|---|
| **Semantic translation quality** | Core correctness — did the output convey what was signed? | chrF / COMET-style semantic-similarity scoring against a reference English translation; BLEU as a secondary/legacy metric (weak for this task — see caveat below) |
| **Fingerspelling accuracy** | Named as the single most common ASL-model failure mode; also the case that matters most for product usefulness (names, places, brands) | Dedicated sub-metric: exact-match rate on fingerspelled tokens only, scored separately from running-text BLEU/chrF |
| **Omission / hallucination** | An LLM refinement stage (Baseline 5) can produce fluent English that simply wasn't signed — this is worse than a visibly garbled output because it looks trustworthy | Human review flags per-segment: [correct] / [omitted content] / [hallucinated content not in source] |
| **Long-context coherence** | Referent tracking and topic maintenance across a multi-minute video | Human review on full-length videos specifically (not just short clips) — check pronoun/referent consistency across segments |
| **Subtitle timing** | Downstream utils are reused unchanged, but the sign-recognition step still needs to emit correct segment boundaries for alignment to work | Compare emitted segment start/end timestamps against human-marked sign-boundary ground truth; measure offset in ms |
| **Robustness across video quality** | Real user uploads vary wildly (resolution, lighting, camera cuts) vs. clean academic benchmarks | Stratify the eval set explicitly by quality tier (e.g., studio/tutorial vs. casual phone-recorded) and report metrics per tier, not just pooled |
| **User-usable end result** | The metric that actually matters for the "docked → un-docked" decision | Small human panel (2–3 reviewers) rating each output pass/fail on "would a real user find this usable as a first-draft caption," independent of exact-match scores |

## Suggested metrics summary

- **Automatic:** chrF or COMET-style embedding similarity (preferred over
  BLEU — sign language translation research explicitly flags BLEU as an
  unreliable/gameable metric for this task; see "A Critical Study of
  Automatic Evaluation in Sign Language Translation," arXiv:2510.25434).
  Report BLEU too only for comparability with published model numbers
  (e.g., Sign-Speak's advertised BLEU 55.1, or academic Phoenix-2014T
  scores), not as the primary internal decision metric.
- **Human review:** structured rubric per segment — correct / partial /
  omission / hallucination / wrong-but-plausible — plus the end-to-end
  usability pass/fail above.
- **Timestamp alignment quality:** mean/median offset (ms) between predicted
  and ground-truth segment boundaries.
- **Task-specific error taxonomy** — use the concrete error classes in
  `CURRENT_VLM_BASELINE_DIAGNOSIS.md` §2 (wrong-sign substitution,
  fingerspelling garbling/hallucination, direction/argument-structure
  errors, grammar/polarity errors, discourse incoherence, confident
  hallucination, transition-frame artifacts, occlusion dropouts) in addition
  to the intern spec's original buckets (missed signs, signer variation,
  low-resolution, fast-signing). Tag every human-reviewed error into exactly
  one bucket so the recommendation is backed by *which* failure mode
  dominates, not just an aggregate score — this is what actually
  distinguishes "needs denser sampling" from "needs a specialized model."

## Priority 0 — Baseline comparison (run before anything else)

Per `EXPERIMENT_PRIORITY.md` §7: take the same 5–10 real ASL videos and run
them through **Baseline 0** (current live approach, as control),
**Baseline 1** (denser/motion-aware sampling, same VLM), and **Baseline 2**
(video-native VLM input, preserving temporal continuity). Add **Baseline 3**
(pose landmarks → open sign-translation model) to the same round only if a
real, loadable checkpoint is found without significant implementation work
— otherwise run it as a fast-follow once the landscape search resolves, not
a blocker on this round. Score all runs with the same error-taxonomy rubric
above. This comparison is the fastest way to learn whether the current poor
quality is a sampling problem, a temporal-continuity problem, or a
genuinely structural gap requiring ASL specialization — see
`EXPERIMENT_PRIORITY.md` §7 for the full reasoning.

## Minimal eval set proposal (matches the intern spec's Stage 4 scale)

20–50 videos total, deliberately stratified:
- A handful of clean single-signer tutorial-style clips (upper bound on
  quality — "can it work at all")
- A handful of real/realistic phone-recorded clips (lower bound — "does it
  survive real input")
- The known real user case(s) if access is approved per the process above
- A few videos with audio+signing both present (exercises the audiovisual
  fusion quick win)
- A few with heavy fingerspelling (names/places) as a dedicated stress test
