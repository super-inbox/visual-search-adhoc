# Recommended Curify Architecture (Staged)

> **Update 2026-08-23:** Revised in light of boss-provided ground truth: ASL
> translation already has real, SEO-driven user demand and a live
> frame-sampling + generic VLM approach (**Baseline 0** in
> `SOLUTION_OPTIONS.md`) whose quality is currently poor. This is no longer
> a "should we build anything at all" decision — it's "how do we move off a
> live, underperforming baseline toward something commercially viable,"
> which changes the shape of the recommendation below. It still stays
> consistent with the intern spec's core insight
> (`docs/asl-translation-mvp-spec.md`): the downstream
> translation/subtitle/voiceover pipeline already exists and should be
> reused unchanged — the open work is entirely on the recognition front end.

## Staged pipeline

```
video ingest
  → signer detection/cropping
  → frame/clip sampling strategy (tuned per baseline — see below)
  → recognition step: current generic-VLM baseline OR pose/landmark model OR hybrid (per landscape research + experiment results)
  → context-aware LLM refinement (terminology, fingerspelled names, fluency, discourse coherence)
  → [merge point] subtitle segmentation (existing subtitle_utils.py)
  → timestamp alignment (existing alignment_utils.py)
  → SRT/VTT (existing subtitle_utils.py)
  → optional: translate EN→ZH/other (existing translation_utils.py) + burned-in subs / voice-over (existing voiceover_utils.py)
```

Unlike the first pass of this research, this pipeline is explicitly framed
as **evolving the live Baseline 0 path**, not replacing a nonexistent one.
The `has_speech()`-based general dubbing pipeline stays exactly as-is and
out of scope here — it correctly serves speech content and should not be
where ASL work gets bolted on (see `CURRENT_APPROACH_GAPS.md` for why these
are two separate code paths).

## MVP (near-term, no new model — improve Baseline 0 in place)

- Run the two cheapest, zero-training experiments from
  `CURRENT_VLM_BASELINE_DIAGNOSIS.md` against the live approach: **Baseline
  1** (denser/motion-aware frame sampling, same VLM) and, if feasible,
  **Baseline 2** (video-native VLM input). Both are prompting/sampling
  changes to the *existing* live tool, not new infrastructure.
- Add **Baseline 5**'s refinement layer regardless of outcome: an LLM pass
  with per-account/domain glossary injection and whole-video context (not
  per-clip) for fluency, name/terminology correction, and discourse
  consistency — cheap, low-risk, and independently valuable.
- Add confidence-based flagging (low-confidence spans labeled as
  best-effort rather than presented as finished captions) — directly
  mitigates the "confident hallucination" failure mode identified as the
  most product-damaging error class in the diagnosis doc.
- Everything from "English text" onward continues to reuse
  `translation_utils.py` / `subtitle_utils.py` / `alignment_utils.py` /
  `voiceover_utils.py` unchanged.
- Goal: measurably reduce the specific error types in
  `CURRENT_VLM_BASELINE_DIAGNOSIS.md` §2 without committing to any new
  model — find out how much of the current poor-quality complaint is
  solvable this way before spending on Baseline 3/4.

## Medium-term (1–2 quarters, light training/fine-tuning)

- Finally complete the intern's Stage 1 landscape review with a specific
  target question: **is there a usable open pose-to-text or hybrid
  RGB+pose ASL checkpoint (Baseline 3/4)?** This is the single largest
  unresolved unknown in the whole research set.
- If yes: integrate as `app/utils/asl_utils.py` + `asl_pipeline.py` (per the
  spec's own architecture standard — pipelines are thin wrappers over
  utils), and run it head-to-head against the improved Baseline 0/1 from
  the MVP phase using the rubric in `EVAL_PLAN.md`.
- If no usable checkpoint exists: fine-tune a modest pose-sequence decoder
  on open datasets (YouTube-ASL, How2Sign) as a bridge, rather than
  attempting to build a general-purpose sign model from scratch.
- This is also the point to decide whether the two current ASL code paths
  (a frontend-only Baseline 0 implementation vs. a backend
  `curify_background` pipeline) should consolidate into one owned service,
  rather than letting them diverge further — a product/eng decision, not
  purely technical.
- Track whether Google opens SL2T/SignGemma access or weights during this
  window; if it becomes available, evaluate it as a potential build-vs-buy
  pivot — but do not plan around it being available on any particular
  timeline, since it is not currently accessible to Curify.

## Research-heavy / SOTA (open-ended, explicitly optional)

- **Baseline 4** (RGB + pose hybrid, reproducing Sign2GPT/SpaMo/SSVP-SLT-style
  gloss-free translation) only if Baseline 3's quality ceiling proves
  insufficient for a real commercial tier — not a beta/best-effort label,
  but genuinely satisfactory quality per the boss's stated bar.
- Justified only if ASL demand (already confirmed real and meaningful per
  the boss) grows into a committed, monetized product line — a business
  decision built on top of the technical findings here, not a purely
  engineering call.
- This tier is where the "technical/product moat" upside (per the boss's
  framing) would actually materialize, since current SOTA/open models are
  not known to clear a commercial-grade bar either — but that upside is an
  opportunity to validate through the experiments in `EXPERIMENT_PRIORITY.md`,
  not something this research demonstrates Curify has already achieved.

## What this recommendation deliberately does NOT include

- No claim that pose/landmark modeling (Baseline 3) is definitely the final
  answer — it is the most promising *candidate to test*, contingent on
  open-checkpoint availability that hasn't been verified yet.
- No claim that Curify's current ASL handling is audio-only or that
  `has_speech()` is the reason the live tool underperforms — that gate
  applies to a separate, unrelated pipeline (see `CURRENT_APPROACH_GAPS.md`).
- No gloss-intermediate-representation step — current SOTA trend and lack
  of ASL gloss data both argue against it (unchanged from the prior pass).
- No commitment to a specific vendor or checkpoint yet — that depends on
  the landscape research this recommendation explicitly calls for.
