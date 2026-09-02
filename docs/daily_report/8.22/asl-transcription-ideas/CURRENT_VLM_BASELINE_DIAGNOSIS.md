# Diagnosis: Why the Current Sampled-Frame + Generic VLM Baseline Underperforms

Per boss-provided ground truth (2026-08-23), the current/recent live ASL
approach is: **video → frame extraction/sampling → generic VLM → inferred
sign meaning/transcription.** This is referred to throughout the research set
as **Baseline 0**. This doc is the technical diagnosis of why that baseline
is structurally weak, independent of which specific VLM is used.

Note on repo evidence (see `CURRENT_APPROACH_GAPS.md` for full reconciliation):
this frame+VLM implementation was **not found** anywhere in `curify-studio`
after checking all local/remote branches and all Python sources — it most
plausibly lives in the separate `curify-frontend` repo (registry routes live
there per `docs/tool-inventory.md`), which is outside this research pass's
access. The diagnosis below is a general technical analysis of the *approach
class* (sampled frames → generic VLM), not a code review of the specific
implementation, since that code was not available to inspect.

---

## 1. Why sampled-frame VLM is structurally weak for continuous ASL

**Loss of temporal motion information.** A sign is not a pose, it's a
trajectory. Handshape at a single instant is frequently ambiguous or even
identical between two different signs that differ only in how the hand moves
between two configurations. Sampling discrete frames and asking a VLM to
reason over a handful of static images throws away exactly the motion
information that disambiguates them.

**Sign transitions.** Continuous signing has no pause between signs the way
speech has (weak) pauses between words. The transition motion between sign A
and sign B is often co-articulated — it blends into both — so a frame grabbed
mid-transition can look like a plausible third sign that was never actually
made. A VLM reasoning frame-by-frame has no principled way to know which
frames are "real" sign content vs. transition blur.

**Movement direction.** Many ASL verbs are directional and change meaning
based on movement path alone (e.g., verbs that inflect for subject/object by
moving toward or away from a location in signing space — the same handshape
moving in opposite directions can mean "I ask you" vs. "you ask me"). Static
frames cannot encode direction; you need at least two temporally-ordered
points and their sequence, which sparse independent-frame reasoning discards.

**Fingerspelling sequences.** Fingerspelling is a rapid sequence of
handshapes (letters) produced at a much higher rate than lexical signing.
It is the single case most sensitive to frame rate: missing frames between
letters doesn't blur the meaning slightly, it drops entire letters, which
generic VLMs then tend to "fill in" with a plausible-looking but wrong word
(see error taxonomy below).

**Hand/body/face coordination.** ASL meaning is frequently carried by the
*relationship* between simultaneous channels — handshape + location + palm
orientation + torso lean + eye gaze, all at once. A VLM prompted on isolated
frames has to infer this joint state from pixels with no explicit structure
telling it "these are the channels that matter and here's how they combine,"
unlike a model built around a structured representation of exactly those
channels.

**Facial and non-manual markers.** ASL grammar (negation, yes/no vs.
wh-questions, conditionals, topicalization, adverbial intensity) is encoded
substantially through eyebrow position, head tilt, and mouth morphemes — not
hand movement at all. A generic VLM has no inductive bias telling it these
are grammatically load-bearing signals rather than incidental facial
expression, so it is likely to drop or misweight them relative to the (more
visually salient) hand motion.

**Long-context discourse.** ASL uses signing space itself to track
referents across an entire discourse — a referent gets "placed" at a point in
space early on and is referred back to by pointing at that same point
minutes later. Per-clip or per-window VLM prompting, with no persistent
memory of where referents were placed, cannot track this; each window is
translated in isolation.

**Sparse-frame aliasing.** This is the umbrella technical failure mode: when
the sampling rate is below the rate of the signal's true temporal frequency,
you don't get a slightly-degraded version of the true motion, you get
*aliasing* — a different, confidently-wrong apparent motion (the visual
equivalent of a spinning wheel looking like it's turning backward in a
strobe-lit video). Below a sign-specific Nyquist-like threshold, more
sampling doesn't gracefully degrade quality, it can produce entirely
different, still-plausible-looking sign interpretations.

**Frame selection strategy.** If frames are sampled at fixed intervals
(e.g., 1/sec) rather than motion-aware (e.g., keyframes at peak velocity or
handshape-change events), the sampling is uncorrelated with where the
signing information actually is. Fixed-interval sampling can systematically
land on transition frames (see above) rather than the meaningful "hold"
frames of each sign, compounding the aliasing problem.

**Generic VLM lack of ASL specialization.** The base model was not trained
on enough ASL data (if any) to have learned ASL's grammar, vocabulary
distribution, or visual conventions (e.g., that a raised eyebrow means
"yes/no question," not "surprise"). It is applying general video/image
captioning priors to a domain where those priors are actively misleading —
e.g., it may narrate what a hand gesture *looks like it means* in ordinary
gesture/body-language terms rather than what it means as ASL lexical content.

---

## 2. Errors we should expect from this baseline

| Error class | Mechanism | Example symptom |
|---|---|---|
| **Wrong-sign substitution** | Static handshape at a sampled instant matches a different sign than the one actually produced (motion disambiguates, frames don't) | Output uses a plausible but incorrect word with no indication of low confidence |
| **Fingerspelling garbling/hallucination** | Missed letters at high fingerspelling rate | A spelled name becomes a different, fluent-sounding but wrong name |
| **Direction/argument-structure errors** | Directional verb inflection lost | Subject/object reversed ("I asked you" vs. "you asked me") |
| **Grammar/polarity errors** | Non-manual markers (negation, question type) dropped | A negated statement translated as affirmative, or a question mistranslated as a statement |
| **Discourse incoherence** | No persistent referent tracking across windows | Pronouns/referents shift or contradict across a multi-minute video |
| **Confident hallucination** | VLM fills gaps with fluent, plausible English not grounded in any frame | Output reads well but doesn't match what was actually signed — the most dangerous failure mode because it's the hardest for a non-signing reviewer to catch |
| **Transition-frame artifacts** | Sampling lands mid-transition | Spurious extra "signs" appear in the output that were never actually made |
| **Occlusion dropouts** | A hand leaves frame or is blocked | Missing content with no flag that something was skipped |

---

## 3. Improvements testable WITHOUT training a new model

These are all reordering/engineering changes to Baseline 0 itself, or
orchestration around it — no new model weights required:

- **Denser or adaptive frame sampling** (Baseline 1): raise fixed sampling
  rate, or better, select frames at motion-velocity peaks/handshape-change
  points instead of fixed intervals — directly targets sparse-frame
  aliasing and transition-frame artifacts.
- **Overlapping sliding-window clips** instead of independent frame grabs,
  so consecutive windows share context and the VLM sees short motion
  sequences rather than isolated stills.
- **Video-native VLM input** (Baseline 2) where the model accepts a short
  video clip directly (when the provider supports it) rather than a
  discrete frame set — preserves motion within the window even without any
  fine-tuning.
- **Prompt engineering**: explicitly instruct the model that this is
  continuous ASL (not general gesture), ask it to flag low-confidence spans,
  and ask it to attend to facial expression/eyebrow/mouth as grammatically
  meaningful rather than incidental.
- **Ensembling / self-consistency**: sample the VLM multiple times (or at
  multiple sampling rates/windows) and flag disagreement as low-confidence
  rather than silently picking one answer.
- **Auxiliary pose overlay**: run MediaPipe Holistic and draw the skeleton
  on top of the sampled frames before sending to the VLM, giving it an
  explicit structured cue for hand/body position without changing the
  model itself.
- **Post-hoc LLM refinement + glossary injection** (Baseline 5's second
  half, testable independently): a context-aware pass that can catch
  fingerspelling-shaped garbling and correct against known names/terms, and
  can flag internally-inconsistent discourse.
- **Confidence-based fallback**: route low-confidence output to the existing
  manual-review path rather than presenting it as a finished caption.

None of these fix the fundamental issue (a generic model reasoning over
disconnected stills has no real access to motion, direction, or non-manual
grammar) — they reduce the *frequency* of the failure modes above, not their
*existence*.

## 4. Improvements that require an ASL-specialized model

- **True temporal/motion modeling** — a model architected around a
  continuous input (pose sequence or video-native encoder trained on sign
  data) rather than independent frames, needed to fix direction-dependent
  and transition-related errors at the source rather than just reducing
  their odds (Baselines 3 and 4).
- **Fingerspelling-specific recognition** — dedicated handling of the much
  higher information rate of fingerspelling, which general sampling-rate
  increases alone cannot fully solve given how fast letter transitions are.
- **Non-manual grammar modeling** — requires training signal that explicitly
  associates facial/head cues with grammatical meaning; a generic VLM has no
  such supervision no matter how it's prompted.
- **Long-context discourse/referent tracking** — requires either an
  architecture with persistent state across the whole video or an explicit
  spatial-referent memory mechanism; prompting alone caps out quickly as
  video length grows.
- **Closing the gap to commercial-grade quality** — per the boss's framing,
  this is the real bar: incremental Baseline 0/1/2 improvements can reduce
  obviously-broken output, but reaching quality good enough to ship without
  a "beta/best-effort" caveat plausibly requires a specialized model
  (Baseline 3/4/5), and even then current open-source options are unproven
  at that bar (see `SOLUTION_OPTIONS.md` for the open-checkpoint-availability
  caveat).

## 5. The fastest experiment to tell us which direction is promising

Run the **same 5–10 real ASL videos** (ideally ones resembling actual user
uploads — casual framing, phone camera, natural signing speed, not
studio-clean tutorial footage) through, at minimum:

1. **Baseline 0 (control)** — current sampled-frame + generic VLM approach,
   exactly as currently deployed, to establish the reference failure rate
   and error-type distribution using the taxonomy in Section 2.
2. **Baseline 1** — same VLM, denser/motion-aware frame sampling — isolates
   whether the dominant failures are sampling-rate/aliasing artifacts
   (fixable without a new model) vs. something deeper.
3. **Baseline 2** — a video-native VLM input (native clip/video, not
   discrete frames), where supported — isolates whether motion continuity
   *itself*, independent of sampling density, is the bottleneck.
4. **Baseline 3, added to the same round only if a real, loadable open
   checkpoint is found without significant implementation work** —
   MediaPipe Holistic pose extraction feeding whatever open
   sign-translation checkpoint the landscape search turns up — isolates
   whether a structurally-different, motion-native approach meaningfully
   changes the error profile even at small scale. If no such checkpoint
   exists yet, this step is skipped for this round, not simulated or
   assumed.

**Why this specific comparison is the fastest signal:** if Baseline 1 closes
most of the gap versus Baseline 0, the fix is cheap (no new model, ship
soon). If Baseline 1 barely moves the needle but Baseline 2 does, that
points at motion continuity (not sampling density) as the real bottleneck,
and toward Baseline 3-class investment rather than further sampling tuning.
If Baseline 3 is available in the same round and changes the *kind* of
errors observed (fewer direction/transition errors, even if overall quality
is still not commercial-grade) beyond what Baseline 2 achieves, that's
strong evidence the long-term investment belongs in a pose/temporal-native
model specifically. If none of Baselines 1–2 (and 3, where available)
improve meaningfully, that's evidence the problem is more about verb
argument structure / non-manual grammar / open-checkpoint quality than
about temporal representation at all, and points toward Baseline 5
(specialized model + heavy LLM semantic refinement) or further landscape
research before committing engineering effort. Full ordering and decision
tree in `EXPERIMENT_PRIORITY.md`.

Score every run with the same human-reviewed error-taxonomy rubric (Section
2 here, cross-referenced in `EVAL_PLAN.md`) so the comparison is about error
*type*, not just an aggregate pass/fail — that's what actually tells you
which baseline to invest in next.
