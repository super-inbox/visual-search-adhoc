# Framing the ASL Product Problem

> **Update 2026-08-23:** Per boss-provided ground truth, the current/recent
> live approach is frame-sampling → generic VLM (**Baseline 0** in
> `SOLUTION_OPTIONS.md`), it has real SEO-driven user demand, and quality is
> currently poor. The framing below (why A+D infrastructure can't just be
> extended to ASL) still explains why the *general dubbing pipeline*
> (Scribe/`has_speech()`) can't handle ASL — but it is **not** the reason the
> live frame+VLM tool underperforms. That tool already attempts continuous
> translation (task C below); it's just structurally weak at it. See
> `CURRENT_VLM_BASELINE_DIAGNOSIS.md` for the technical reasons why, and
> `CURRENT_APPROACH_GAPS.md` for the full reconciliation of both code paths.

## Four different problems that get conflated as "ASL transcription"

| | Task | Input → Output | Example system |
|---|---|---|---|
| A | **Audio speech transcription** | audio waveform → text | ElevenLabs Scribe / Whisper — this is what Curify already runs for every non-ASL video |
| B | **Isolated sign recognition** | single sign / short clip → one gloss/word | classroom ASL-alphabet or single-word classifiers (MNIST-style ASL datasets); 80–95% accuracy on isolated signs, but not what users actually sign |
| C | **Continuous ASL translation** | minutes of natural, connected signing → fluent English sentences | Sign Language Transformers, YouTube-ASL/How2Sign-trained models, Google DeepMind's SL2T |
| D | **Subtitle generation / alignment** | any text stream + timing → SRT/VTT with correct time boundaries | Curify's existing `subtitle_utils.py` / `alignment_utils.py` — already solved, model-agnostic |

**Why the conflation is dangerous — two different failure modes coexist:**
Curify's general dubbing pipeline is built entirely for **A + D** and has no
component for **B or C**; if ASL video is ever routed through that pipeline,
it fails closed at the `has_speech()` gate because there's no speech to
transcribe. Separately, per boss-provided context, Curify's **dedicated**
ASL tool already attempts **C** directly (frame-sampling → generic VLM →
inferred meaning) — it doesn't fail closed, it produces output, but that
output is poor quality because a generic VLM reasoning over sparse
independent frames is a structurally weak way to do continuous sign
translation (see `CURRENT_VLM_BASELINE_DIAGNOSIS.md`). The product problem
is therefore not "make Scribe work on quiet videos" (that's a dead end
regardless), it's "make the C-task itself — continuous ASL → English —
good enough to be commercially usable," which is a harder, separate
technical problem from anything the existing A+D infrastructure can help
with directly.

## The actual product problem, stated precisely

> **ASL video → English text → time-aligned subtitles**

This decomposes as: continuous sign recognition (a video/pose understanding problem, closer to action recognition + language generation than to ASR) → machine translation into fluent English (ASL is not just "English with different words," it has its own grammar, word order, and non-manual grammar — see below) → segmentation and timestamping of that English text against the source video for subtitle rendering.

Only the first two steps are new for Curify. The third step (D) is already solved by existing utils per `CURRENT_APPROACH_GAPS.md`.

## Hard cases that any solution must handle

- **Pure silent ASL** — no audio track at all, or audio present but irrelevant (e.g., background music). `has_speech()`-style gating must route to the ASL path instead of failing closed.
- **ASL + spoken audio simultaneously** ("sign-supported speech," interpreters signing while a speaker talks, or a signer who also voices) — the two channels may agree, conflict, or only partially overlap; naively picking one loses information.
- **Fingerspelling** — proper nouns, technical terms, and spelled-out words use a distinct, fast, high-frequency finger-shape sequence that generic sign-translation models handle poorly (this is the single most commonly cited ASL-model failure mode in the literature).
- **Facial and non-manual markers** — ASL grammar encodes negation, questions, topicalization, and conditionals through eyebrow position, head tilt, and mouth shape, not hand shape. A hands-only pipeline will systematically mistranslate grammar, not just miss vocabulary.
- **Fast / co-articulated signing** — natural signing blends adjacent signs the way connected speech blends phonemes; frame-sampling rate and temporal modeling must be tuned for this, not for slow tutorial-speed signing.
- **Occlusion** — one hand blocking the other, hands leaving frame, or signing while holding an object.
- **Multiple signers / interpreter + speaker in frame** — requires signer detection and cropping before any recognition step, plus turn-taking logic.
- **Camera cuts / edited video** — user-uploaded video (Curify's actual input distribution) is not lab-recorded single-take footage; cuts break temporal continuity assumptions that most SLT models are trained under (most academic datasets are single continuous shots).
- **Long-context discourse** — pronoun reference, spatial referencing (ASL uses signing space to track referents across a whole discourse, not just a sentence), and topic maintenance over minutes-long videos exceed the context window of per-clip translation models.

Each of these hard cases maps onto a concrete structural weakness of the
current live approach — see `CURRENT_VLM_BASELINE_DIAGNOSIS.md` for the
detailed mechanism (e.g., "fast/co-articulated signing" is largely the
sparse-frame-aliasing and transition-frame problem; "facial and non-manual
markers" is the generic-VLM-lacks-ASL-grammar-priors problem).

## Implication for architecture

Any viable Curify solution needs, at minimum: (1) a video-native front end that can isolate the signer and extract hand/body/face signal at a frame rate suited to fast signing, (2) a sequence model that can hold context across more than a few seconds, and (3) an explicit answer for what happens when audio and signing co-occur. These constraints are the basis for the options in `SOLUTION_OPTIONS.md`.
