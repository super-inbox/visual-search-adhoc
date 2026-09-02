# Current Internal ASL Approach — What Exists vs. What's Documented

> **Update 2026-08-23:** This doc was originally written from repo-only
> evidence, before the boss supplied ground-truth context that (1) ASL
> translation has real, meaningful user demand driven by SEO traffic, many
> users are actively trying it, and (2) the current/recent approach is
> **frame extraction/sampling → generic VLM → inferred sign meaning**, and
> quality is currently poor / not commercially satisfactory. That
> boss-provided information takes priority over repo-only inference where
> the two seem to conflict. This doc now separates evidence into three
> explicit tiers so nothing is erased, only reconciled.

## Tier A — Code/repo-observed paths (curify-studio only)

This is what I could directly verify by reading `curify-studio` (backend,
tools, docs, all local + remote branches). **I found no frame-sampling +
VLM implementation anywhere in this repo** — no vision-capable model call,
no multi-frame extraction utility, no ASL-specific util file. What exists:

| Doc | What it is |
|---|---|
| `docs/asl-translation-mvp-spec.md` | Intern spec (2026-06-14), framed as a time-boxed OSS-landscape evaluation, not a production build. Stage 1's comparison table is empty — no OSS model has been benchmarked from this backend's side. |
| `docs/tool-inventory.md` (line 166) | Registry entry: `ASL video translator` — status **DEMO**, monetization **Docked (tech challenge)**. |
| `docs/workstream-tooling-and-engineering.md` | States ASL captioning is docked: *"real demand from blog traffic, but a genuine tech challenge (no viable path: Sign-Speak API silent, OSS poor/costly)."* |
| `gtm_tools/send_signspeak_inquiry.py` | Outbound pricing inquiry to Sign-Speak (vendor ASL API, BLEU 55.1 reported) — a path that went dark. |
| `gtm_tools/send_1252_asl.py` | Real user (1252) uploaded 2 ASL videos; automated job(s) failed; a human hand-translated one as a goodwill gesture. |
| `curify_background/app/utils/transcription_utils.py` | ElevenLabs Scribe (audio ASR) is the engine behind Curify's *speech*-based subtitle/dubbing pipeline. Its `has_speech()` pre-flight explicitly exists to catch *"silent video, sign-language footage, audio track stripped"* before paying for a Scribe call. |
| `curify_background/app/utils/video_preprocess_utils.py` | The only frame extraction in this backend is a single-frame thumbnail grab (`-vframes 1`) for UI thumbnails — not multi-frame sampling for model input. |
| `curify_background/app/utils/openai_client_utils.py` | No vision/image_url/multi-frame VLM call exists in this backend's OpenAI client wrapper. |

**What this backend genuinely does not have:** any ASL recognition
capability, any VLM-based video understanding call, or a committed
`asl_utils.py`/`asl_pipeline.py` (both are named in the spec only as the
*target* shape if the project graduates).

**What this backend does have, reusable unchanged regardless of which
future ASL approach is chosen:** the full downstream pipeline —
`translation_utils.py`, `subtitle_utils.py`, `alignment_utils.py`,
`voiceover_utils.py`, orchestrated via `transcribe_burn_pipeline.py`.

## Tier B — Boss-described current/recent production or experimental approach

Per the boss's higher-authority context (2026-08-23): the live/recent ASL
path is **video → frame extraction/sampling → generic VLM → inferred sign
meaning/transcription**, it has real, meaningful SEO-driven user demand
(many users actively trying it), and quality is currently poor / not
commercially satisfactory. This is treated as ground truth for what the
product currently does, even though its code was not locatable in this
research pass.

**Where this most plausibly lives, and why it wasn't found here:** the
`asl-video-translator` registry route is defined in `curify-frontend`
(`docs/tool-inventory.md`: *"Shipped routes live in
`curify-frontend/lib/tools-registry.ts`"*), a **separate repository** not
in this session's accessible directories (only `curify-studio` and this
worktree were searchable). A frame-sampling + generic VLM call is exactly
the kind of lightweight implementation that would ship fast as a frontend
API route or serverless function calling a hosted VLM directly — without
ever touching `curify_background`'s dubbing pipeline, Scribe, or
`has_speech()`. That would explain why it's live enough to draw real SEO
traffic and "many users trying it," while remaining invisible to a
backend-only search.

## Reconciling the two: do both paths coexist, and does has_speech() apply here?

**Most likely: yes, both paths coexist, and they solve different problems.**

- `has_speech()` gates the **general-purpose dubbing/captioning pipeline**
  (`transcribe_burn_pipeline.py` → Scribe), which is speech-first by design.
  If an ASL video is ever routed through *that* pipeline, it would correctly
  get treated as a no-speech input and skipped — but that pipeline was never
  meant to handle ASL in the first place.
- The **dedicated `asl-video-translator` tool** (boss's Tier B path) is a
  separate, purpose-built (if minimal) route that does not go through Scribe
  or `has_speech()` at all — it goes straight from frames to a VLM. This is
  consistent with it being live for real users right now, and with its
  quality being poor for the structural reasons in
  `CURRENT_VLM_BASELINE_DIAGNOSIS.md` (sparse-frame aliasing, no temporal
  motion modeling, no ASL specialization) rather than for the reason
  originally assumed here (silent-input rejection).
- The user 1252 case (`send_1252_asl.py`, docstring: *"the automated jobs
  failed (ASL is still R&D)"*) is genuinely ambiguous between these two
  explanations — it could be a `has_speech()` rejection if routed through the
  general pipeline, or a quality/error failure in the dedicated VLM path.
  Both are plausible; nothing in the available evidence rules either out,
  and it isn't necessary to resolve which one occurred to move forward.

**Correction to this doc's original framing:** the original version of this
document said *"the current system is explicitly designed to reject ASL
video as a no-speech input"* as if that were the whole story. That is true
only of the general Scribe-based dubbing pipeline. It is **not** accurate to
say Curify's current ASL handling is "audio-only" or that there is no
automated attempt at ASL translation at all — per the boss, a dedicated
frame+VLM path exists, is live, and is what real users are actually hitting.
Both pieces of evidence are kept in this doc rather than one overwriting the
other.

## Tier C — Proposed future architecture

Everything in `SOLUTION_OPTIONS.md`, `CURIFY_RECOMMENDED_ARCHITECTURE.md`,
and `CURRENT_VLM_BASELINE_DIAGNOSIS.md` is forward-looking proposal, not
anything observed to exist today. The current live approach (Tier B) is
now explicitly labeled **Baseline 0** and used as the reference point for
comparison in those docs.

## Major technical gaps (updated)

1. **No verified ASL-specialized recognition capability anywhere.** The live
   path (Tier B) is a generic-VLM baseline, not a sign-language-specialized
   model — see `CURRENT_VLM_BASELINE_DIAGNOSIS.md` for why that structurally
   caps quality regardless of prompt tuning.
2. **No vetted OSS specialized-model alternative.** The one credible vendor
   path (Sign-Speak) went dark; no OSS alternative has been benchmarked.
3. **No visibility from this backend into the actual live implementation.**
   Because the live tool lives in `curify-frontend`, this research pass
   could not inspect its exact frame-sampling rate, prompt, or VLM provider
   — those specifics should be pulled directly from that repo/team before
   finalizing next steps (see `BOSS_SUMMARY.md` remaining unknowns).
4. **No eval harness for sign-to-text quality.** `evaluation_utils.py`
   exists for the speech pipeline; nothing analogous exists for
   translation/fingerspelling/discourse-quality on the ASL path.
5. **No labeled Curify ASL data.** Aside from the 1252 videos and one demo
   asset (`dev/jayw/raw/asl-demo-translation.mp4`), no known internal corpus
   exists to fine-tune or benchmark against.
6. **Two ASL code paths risk drifting further apart** if the backend
   (`curify_background`) and frontend (`curify-frontend`) evolve
   independently — worth explicitly deciding whether future ASL work should
   consolidate into one owned pipeline (per the intern spec's own
   `asl_utils.py`/`asl_pipeline.py` target shape) rather than leaving a
   frontend-only VLM call as the permanent production path.
