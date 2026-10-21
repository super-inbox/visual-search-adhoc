# ASL translation — the one doc

> **Moved 2026-10-21** from `curify-studio/docs/asl-translation-mvp-spec.md`. This is now the canonical ASL index. Historical `git show` commands and production-code paths below refer to **curify-studio** unless another repository is named. [Pre-move source and history](https://github.com/super-inbox/curify-studio/blob/d9406add0/docs/asl-translation-mvp-spec.md).
>
> [Research summary — 2026-10-20 (PDF)](asl-research-retrospective-2026-10-20.pdf). The PDF is a dated snapshot; maintain this Markdown index for future updates.

> **Entry point for everything ASL.** Read this before opening any other ASL file,
> quoting a result, or touching `asl_utils.py` / `asl_pipeline.py`.
> **Revised 2026-10-16 — current research entry point: §18.** Reviewed Baobao's branch
> at `c38497b2e3f90d0bdaaa3554c32705435eea956f` against its reports, scripts and compact
> metrics. **P0-12 is complete on T4/fp16:** matched timing/crop raises BLEU-4
> **5.47 → 8.61**, versus **9.13** with official poses (85.7% gap recovery).
> **No new Uni-Sign translation model was trained.** P0-14 trained frozen-feature
> concept probes; P0-15 trained a lightweight verifier. Representation evidence is
> qualified; naive fusion hurts, and the guarded verifier adds nothing. **No fused
> sentence translation improvement has been demonstrated.**
> ASL category labels remain unverified; all 45 manual-review clips are PENDING.
> §18 answers the model/fusion/category questions and records the sanity-gate and
> holdout-provenance qualifications. §17 preserves the earlier training and local
> backend-switch record. This documentation update does not deploy or switch models.
> Older dated priorities and “P0-12 pending CUDA” statements are superseded below.
> **Revised 2026-09-21** — **P0-8 has cleared.** Uni-Sign's first author granted commercial
> use *and* redistribution of the weights in writing, so the licence no longer blocks PR #448,
> the ACR push, or any hosting option (**§16**). Three things travel with the grant: a **credit
> line** linking to the Uni-Sign GitHub is required wherever it ships; **How2Sign is explicitly
> not covered** — the dataset stays CC BY-NC 4.0 and redistributing it needs a separate ask;
> and the grant currently exists **only in an email** — the HF model card still reads
> `cc-by-nc-4.0` and the code repo still ships no LICENSE (MIT stated as intent), both verified
> 2026-09-21 (**LHF-12**). ⚠️ **Nothing about the evidence changed.** §15.2's complete
> degeneration on real Curify user video and §15.4's no-gain segmentation result both stand, so
> this removes the *permission* barrier and supplies no *reason* to deploy. The queue still
> leads with **P0-6**, not with deployment. **The migration question was asked the same day and
> is answered in §16.5: no.** A ~40× BLEU advantage on How2Sign, WER unmoved at 0.98, no
> timestamps, and complete degeneration on the only real user video it has been shown.
> **Revised 2026-09-19** — **§15: Uni-Sign was built as a real service and run on the real
> checkpoint, and the deployment question now has an answer — no, on four counts, the first
> of which is a licence and not code (§15.5).** The checkpoint is CC BY-NC-4.0
> (non-commercial) and upstream ships no LICENSE at all, so **`curify-studio` PR #448 must
> not be merged or pushed to ACR** until that is cleared (**P0-8**). Two findings outrank the
> deployment mechanics: on **real Curify user video** Uni-Sign **degenerated completely**
> ("One, two, three…" on repeat, both clips), so its How2Sign advantage over our own pipeline
> has never been shown to hold on the distribution our users actually send (§15.2); and above
> **256 frames (~10.7 s at 24 fps) Uni-Sign discards the excess at random, unseeded per
> request**, so identical long clips return different translations and every long-clip
> Uni-Sign number is one draw rather than a measurement (§15.3). Segmentation removes that
> mechanism but **did not improve translations** (§15.4). Nothing shipped; production is
> unchanged.
> **Revised 2026-09-12** — **§14: P0-4 was executed against the frozen benchmark and
> §13's result did not reproduce.** Native video is now a real, resumable config (P0-4
> step 1 ✅); on the 12 diagnostic clips it has scored 5, and **0 of 5 recovered meaning**
> — the remaining 7 died in the Gemini Files API before inference, so the gate is
> **inconclusive, not failed**. Two further axes closed alongside it: trajectory tracking
> extracts cleanly (0% missing on 5/5 clips) but **0/5** when handed to Gemini as prompt
> text, and SignCaption is blocked by a ToS clause, not by engineering. **Five input-side
> axes have now recovered meaning on zero clips (§14.6).**
> **Revised 2026-09-10 (b)** — **§13: native video input beat the frame pipeline on a
> controlled same-model comparison** — the first time this workstream has recovered
> meaning on anything. One clip, circular reference, so it is a signal and not a
> measurement; **§7 P0-4** is how it becomes one. §13.6 also surfaces a reproducibility
> bug affecting every §11/§12 provenance claim (**§7 P0-5**).
> **Revised 2026-09-10** — **§12**: three controlled temporal
> ablations, a 40-clip semantic review, and a re-check of SpaMo/SSVP-SLT. Its headline is
> that *none* of the frame-based fixes moved the failure, and that **0 of 40 clips are a
> case of "right meaning, wrong words"** — the last comfortable reading of §11's WER is
> now closed off.
> **Revised 2026-09-07** — Curify's model has finally been scored on an independent
> benchmark; **§11 is the current state of the evidence and supersedes §1 on accuracy.**
> The 2026-08-30 label-leakage finding that retracted the demo-clip results is §1.0 (record
> in §10); start there for why the older numbers cannot be quoted.
> **Consolidated 2026-08-29** from three separate docs: this index, plus
> `asl-recognition-evaluation-2026-08-18.md` (now Appendix B) and
> `asl-mvp-stage2-results-2026-08-18.md` (now Appendix C). Both are preserved
> verbatim below; nothing was dropped. The original 2026-06-14 MVP spec is
> Appendix A. Owner: jay.
>
> ---
>
> 📐 **Current eval scorecard (2026-09-04) — read this before quoting any accuracy number
> in this document:** <https://claude.ai/code/artifact/9cd7d59e-dd5c-479d-b389-eed170011363>
>
> One page: every metric on the board across all three datasets, what each is still worth,
> whether the newly-benchmarked open models can be deployed, and the P0 chain.
> **It supersedes §0 and §1 on accuracy.**
>
> ✅ **Scorecard P0-4 is now done in this file.** 1252's WER 0.9231 is no longer called
> "the only defensible accuracy number we have": as of the 2026-09-02 corpus
> reclassification (`visual-search-adhoc:asl-translator/data/asl_corpus/inventory.json`,
> and the *Data status — 2026-09-01* README section already on `origin/main`) 1252 is
> `non_independent` / `usable_for_official_metrics: false`, and **0 of 13 private-corpus
> videos are usable for an official metric.** §0, §1.0 and §4 now say so.
>
> ⚠️ **The scorecard itself is now partly stale — read §11 alongside it.** Its headline
> "0 Curify runs on the frozen 128-clip benchmark" and its ⛔ empty cell were closed on
> 2026-09-06: Curify's model has been scored on all 128 clips (WER 0.9762, BLEU 0.1341),
> and scorecard P0-1 and P0-3 are done. **P0-2 — the text-memorisation control that was
> supposed to gate P0-3 — was never run** (§11.5), and P0-5, the on-screen-text prompt
> bug, is still live (§7 P0-2).

---

## 0. Answer in one screen

**Current decision (2026-10-16):** retain the production-default decision; no new
production-quality evidence justifies switching. Uni-Sign remains the strongest
research base. The controlled preprocessing diagnosis is complete, but automatic
input preparation on customer videos and safe fusion remain unvalidated. Read
**§18** for current results and next steps; **§17** for earlier custom-model training
and the local backend adapter. Frozen-128 translation, frozen-147 training comparisons,
and 2,209-clip concept detection are different endpoints; do not compare their scores
as if they were one benchmark. The September scorecards below are historical.

**Is it accurate?** No. As of 2026-09-06 that is no longer an inference from one
video — it is measured on 128 clips against references we did not write:

| What we can score | WER | Read as |
|---|---|---|
| **Frozen How2Sign-128, independent references, Curify's own pipeline** (§11) | **0.976** | BLEU **0.134** against a field SOTA of 12.39. 0 of 128 clips scored WER < 0.5; the *best* clip in the corpus is a truncated fragment |
| ~~The one real user video with a human reference~~ (1252, 76.8s) | ~~0.92~~ | **DIAGNOSTIC ONLY — the reference is a Curify outreach translation with no annotator or method on record.** `inventory.json` marks it `non_independent` / `usable_for_official_metrics: false` (§1.0) |
| ~~The demo clip on our own tool page (155, 26.7s)~~ | ~~0.33~~ | **RETRACTED — the model was reading captions burned into the frame** (§1.0) |
| **Two production runs of the same video against each other** (jobs 1466/1467, both charged 32 credits) | **0.97** | the tool disagreed with itself more than 1252 disagreed with its ground truth |

**The private corpus supports no accuracy claim at all** — 0 of its 13 videos are
usable for an official metric. The September How2Sign-128 number was the first independent metric for the
production pipeline. Later Uni-Sign and custom-model research results are in §§17–18;
they do not retroactively validate the private corpus or current production.

⚠️ **One caveat that must travel with it.** The 128-clip run used `gemini-3.6-flash`,
because `gemini-2.5-flash` — what production actually runs — is entitlement-blocked for
the evaluation credential (§2, §11.2). Prompt, sampling, batching, dedup and schema are
production's, byte for byte; the model is not. **Production as shipped remains
unmeasured on any independent benchmark.**

**The shape of the failure matters more than the number.** It is not visibly
broken output. It is fluent, confident, correctly-timed English that substitutes
for the signing instead of transcribing it — "The boy's name is Greg" comes back
as "Do you know H.G.Q.?" at almost the right timestamp. A hearing reviewer cannot
tell which lines are real, and the deaf viewer the captions are made for has
nothing to check them against.

**Shipped 2026-08-29** (see §7 for each item, and the ✅ markers there):
the tool is **now free** (`JOB_CREDIT_COST["ASL_TRANSLATION"] = 0`) and stays live;
segment dedup and `temperature=0` are in; the frame budget scales with duration and
flags low-density jobs; `runtime_config` finally survives to the API; and the result
page renders an unverified/low-confidence notice. Marketing copy in all 10 locales
that still claimed the tool was an unreleased demo has been corrected. **Full record
in §9**, including the four follow-ups it left open.

⚠️ **Every number in §1 predates that batch**, and the 155 numbers are now retracted
outright (§1.0). The 08-29 work re-scored existing predictions; it did not generate new
ones. **The first genuinely new model run since is the 09-06 How2Sign-128 baseline in
§11** — read that, not §1, for how a production-shaped configuration actually performs.

**Where the wins are.** §7 lists them in order. Note that the first item's
headline number was retracted on 2026-08-30 (§1.0):

1. ~~**Deduplicate consecutive repeated segments** — the difference between WER 0.33 and
   an exact match~~ — **that measurement was the model reading burned-in captions.** The
   fix is still correct (batch boundaries really do duplicate) and stays shipped, but it
   is now **unmeasured**.
2. **Pin `temperature=0`** — repeat-run disagreement drops from WER 0.97 to 0.18.
   One line. It buys reproducibility and supportability, **not** accuracy: on the one
   clean verified case it moves WER 0.923→0.923.

Neither touches the real ceiling. Field SOTA for open-domain ASL→English is
**12.39 BLEU**; production MT is 40–50. Nothing in §7 changes that (§8). The 09-06
benchmark puts our own figure on that scale for the first time: **0.134 BLEU** — two
orders of magnitude below SOTA, and below both open baselines we can run (§11.3).

**The failure now has a measured shape, not just a described one.** Across 128 clips,
Curify predicts 41% of the reference word count, 61% of all edit operations are
deletions, and temporal recall is 0.58 against a temporal precision of 0.99. It is not
mostly *misreading* the signing — it is *silent across most of the video*, and fluent
where it does speak (§11.4). That is what the 8 fps temporal ablation was built to
test, and that run is 76/128 done and blocked on billing (§11.6).

**Three temporal fixes have now been tried, and none of them worked (§12).** More frames,
uniformly-spaced frames, and overlapping batches with shared context all left the failure
where it was — **0 clips out of 12 recovered correct meaning under any of them.** The one
arm whose WER moved (batching, 1.0524 → 0.9545) moved it by getting *shorter*, not better:
chrF2 went 14.30 → 13.54 and output length fell to 46% of reference. And a 40-clip
semantic review found **0/40 cases of "correct meaning, different English"** — so the
comfortable reading of §11, that WER is punishing decent translations for wording, is
dead. The failure is topical.

**One of those untested axes was probed on 09-10 and looked like the first thing that
worked (§13)** — sending Gemini the whole `.mp4` instead of extracted frames moved WER
**0.9615 → 0.8269** on one clip and recovered the numbered-list structure of the exercise,
**2 of 7 items semantically right**, at 1 call instead of 7. ⚠️ **That was one private clip
against a circular reference.** It has now been run against independent ones, and **it did
not reproduce: 0 of 5 scored benchmark clips recovered meaning (§14.1).** Where WER moved
there, it moved by swapping one hallucination for another. 7 of the 12 clips are still
unscored — blocked in the Gemini Files API before inference — so P0-4's gate is
**inconclusive rather than failed**, but nothing independent yet supports §13's reading.
What survives is narrower and still worth having: native video is **cheaper**, and so far
**no more accurate**.

**Five input-side axes have now been tested, and they have recovered meaning on zero
clips** (§14.6): more frames, evenly-spaced frames, overlapping frame batches, the raw
video itself, and explicit hand/body trajectory handed over as prompt text. Trajectory
*extraction* works well — 0% missing tracking on 5/5 probe clips, down to individual finger
joints — but a generic model told about the motion in words does nothing with it (§14.2).
The class of fix that keeps failing is "give a general-purpose multimodal model better
visual input"; the hypothesis left standing is that ASL needs a **sign-specific learned
representation**. ⚠️ Our own nearest data point cuts against rushing there: **Uni-Sign is
that kind of model, consumes exactly that pose signal, and still sits at WER 0.9819 / BLEU
5.39** on the same 128 clips. So the cheapest next move is not a new experiment — it is
finding out why Uni-Sign fails, from artifacts already on disk (§7 P0-6).

---

## 1.0 ⛔ The contamination finding — 2026-08-30

**The demo clip we scored had the answer burned into it.**
`asl_corpus/videos/155_demo_asl-demo-translation_26.7s.mp4` was byte-identical
(md5 `d714db71…`) to `curify-frontend/public/video/asl-demo-translation.mp4` — the
**published marketing demo, which is the tool's own output with English captions burned
in**. The corpus took the output video as the input, so every 155 score measured the
model's ability to read on-screen text.

Three things make this unambiguous:

1. **The prediction is the reference, verbatim.** Under `temperature=0` the output
   reproduces the gold SRT word for word including punctuation ("My family has five,
   including my father."), with **0 substitutions and 0 deletions**. A model translating
   ASL does not land on a human translator's comma placement.
2. **PSNR against the clean twin**: 28.1 dB full-frame, **47.1 dB excluding the bottom
   third**. Same footage; the entire difference is the caption band.
3. **The "duplicate segments" were two batches reading the same caption.** Segments 3+4
   span 8.88–12.65 against a caption window of 8.867–12.833; segments 6+7 span
   18.48–20.42 against 18.2–20.3. Each pair's union *is* the caption's display window.

**What this retracts** — see the ~~struck~~ rows throughout:

| Withdrawn | Was |
|---|---|
| 155 baseline0 / temperature0 | WER 0.3704 / 0.3333 |
| 155 temperature0 **after dedup** | WER 0.0000 — the "exact match against the human reference" |
| Pooled/micro WER over 79 reference words | 0.7342 / 0.7215 — pooled a clean case with an OCR case |
| "On well-framed slow content the recogniser is essentially correct" | rested entirely on 155 |

**Deduplication is not retracted.** Batch-boundary duplication is a real artifact of
stateless `frames[i:i+BATCH_SIZE]` batching and the fix stays shipped. Only its *measured*
benefit is withdrawn — it is now an unmeasured fix.

**`1320` was contaminated the same way** (captions across ~85% of the clip), which matters
because **LHF-5 — this document's top-priority next action — would have scored the model
against captions transcribed from the video it was reading.**

**Only those two.** All 13 corpus videos were re-checked frame by frame. That matches
`VIDEO_TYPE_AUDIT.csv`'s own `burned_in_captions` column, which had recorded the burn-in on
both — and still marked them `suitable_for_asl_translator_evaluation = yes`, citing the
captions as corroboration that the signing matched. **The fact was captured; the
consequence was never drawn.** The manifest likewise recorded 155 as *"Curify's own demo
asset, already public at /video/asl-demo-translation.mp4"* and read that as low risk rather
than as the answer key.

**What still stands:** 1252 (input clean, WER 0.9231 — ~~the only defensible accuracy
number we have~~ **downgraded to diagnostic-only on 2026-09-02**: its reference is a
Curify outreach translation with no annotator or method on record, and `inventory.json`
now marks it `non_independent` / `usable_for_official_metrics: false`. The only
defensible accuracy number is now How2Sign-128, §11), the repeatability results (§1.2 — 1466/1467 are clean), the SignCaption
comparison (§1.3 — 1474/1477 are clean), and the corpus authenticity audit.

**What was fixed** (`visual-search-adhoc`, branch `jwang/asl-decontaminate-corpus-2026-08-30`):
the contaminated files moved out of `videos/` into the ground-truth folders where the other
burned reference renders live; the raw demo source swapped in for 155; a masked render built
for 1320; `label_in_input` added to the manifest and both CSVs; and a guard added so this
cannot recur silently (§3).

Full account: `visual-search-adhoc:asl-translator/data/asl_corpus/CONTAMINATION.md`.

---

## 1. Accuracy — what we can actually claim (2026-08-26 evidence)

Source: `super-inbox/visual-search-adhoc` @ `baobao/asl-ground-truth-tool-2026-08-26`,
`asl-translator/` + `docs/daily_report/8.26/asl-ground-truth-eval/`. Scored with a
stdlib-only WER/CER/timing scorer (`asl-eval/evaluate.py`) against an offline runner
that reproduces the production config exactly (`asl-eval/run_current_model.py`, which
records `source_commit` and `prompt_sha256` per run).

### 1.1 Against verified human ground truth — the only accuracy-capable evidence

| Case | Config | WER | CER | Temporal IoU | Error composition |
|---|---|---|---|---|---|
| ~~**155** demo, 26.7s~~ | ~~baseline0~~ | ~~0.3704~~ | ~~0.3485~~ | ~~0.7095~~ | **RETRACTED — captions burned into the input (§1.0)** |
| ~~**155**~~ | ~~temperature0~~ | ~~0.3333~~ | ~~0.3409~~ | ~~0.7049~~ | **RETRACTED** — the "0 sub / 0 del" was the tell |
| **1252** real user, 76.8s | baseline0 | 0.9231 | 0.7211 | 0.4743 | 46 sub / 2 del / 0 ins |
| **1252** | temperature0 | **0.9231** | 0.6693 | 0.6072 | 37 sub / 11 del / 0 ins |

~~Pooled/micro WER over both videos (79 reference words): baseline0 0.7342,
temperature0 0.7215.~~ **Withdrawn** — it pooled a clean case with an OCR case.
**The corpus supports one accuracy number: 1252 at WER 0.9231.**

**The 155 analysis that used to sit here has been removed.** It read the row's
"0 substitutions, 0 deletions, 9 insertions from two duplicated caption lines" as evidence
that the recogniser was essentially correct on well-framed slow content, and concluded that
dropping the duplicates made the demo clip an exact match against its human reference.

Both readings were artifacts. The model was reading English captions burned into the frame,
and the two "duplicates" were two batches reading the same caption while it was still on
screen. A perfect score with zero substitutions was the signal that something was wrong, not
that something was right — see §1.0.

### 1.2 Against itself — repeatability

| Comparison | WER | CER | IoU | Segments |
|---|---|---|---|---|
| **baseline0**: jobs 1466 vs 1467, real production, content-identical input | 0.9706 | 0.7088 | 0.4631 | 24 vs 29 |
| **temperature0**: two offline repeat runs, same video, all else held | **0.1786** | 0.1335 | **0.9085** | 18 vs 15 |

12 of 18 segments (~76% of the clip's duration) returned **byte-for-byte identical**
under `temperature=0`. All residual disagreement is confined to a single ~42-second
window near the start of the clip; nothing outside it differs at all.

**This is repeatability, not correctness.** Two runs agreeing says nothing about
whether either is a correct translation — and §1.1 shows the accuracy effect on
verified gold is small and inconsistent in direction.

**Caveat on this pair:** 1466/1467 is genuine sustained signing (re-confirmed by
frame audit), but the framing **crops the signer's head out of shot**, removing
ASL's facial-grammar channel by construction. Valid for the repeatability and
segmentation-timing diagnostics it was used for; **not** representative of
well-framed ASL for accuracy. Do not generalize the 0.97→0.18 magnitude.

### 1.3 Against an external commercial tool (SignCaption / Sign-Speak)

Disagreement with SignCaption stays at ~0.95 WER **and does not improve at all**
under `temperature=0`, even though self-disagreement collapsed. So decode noise was
not what separated the two systems. On `1477_recording_6.7s` the two outputs share
**no words at all** while agreeing on timing (IoU 0.82) — SignCaption reads one short
question, we emit four unrelated first-person statements.

**Neither side is ground truth here.** These files are marked
`usable_for_official_metrics: false` throughout and must never be quoted as a
benchmark. The comparison establishes only that two independent systems disagree
completely on the same signing; it cannot say which is closer to the truth.

### 1.4 Failure modes, named

- **Fingerspelling: 0 for 2, temperature-independent.** "Greg" → `"H.G.Q."` /
  `"HPG"`; "Sara" → omitted entirely under both configs. 1252 is our only
  fingerspelling case and both configs failed it completely.
- **Numbers: not split after all.** This used to read "155's four ages were recognised
  correctly, 1252's were garbled" and reach for an explanation about slow, well-framed
  sentence frames. 155's ages were *read off the screen* (§1.0). What is left is 1252
  alone: "Number two / three / four" garbled into other numeral-bearing phrases
  ("Two more.", "Add two."). **Numbers fail on the only clean case we have.**
- ~~**Duplicate segments** — the dominant and *entire* error source on 155.~~
  **Retracted (§1.0):** both duplicates were the same burned-in caption read by two
  consecutive batches. Batch-boundary duplication is still real, but 155 is no longer
  evidence for its rate or its cost.
- **Confident paraphrase, not random hallucination.** Neither video produced
  off-topic content; both produced fluent plausible English that stands in for the
  signed content. That is the harder failure to catch.
- **Timing and content move independently.** On 1252, `temperature=0` improved
  *when* (IoU +0.13) without improving *what* (WER tied, fingerspelling still 0/2).

### 1.5 Corpus authenticity, and one correction to the record

A frame/audio audit of all 13 curated videos found **12 showing sustained
ASL-consistent signing, 1 uncertain (`1457`, poorly-lit screen recording), 0
confirmed non-ASL**. This covers the curated corpus only and says nothing about the
broader production video pool, which has not been audited (that would need
authorized, metadata-only, read-only production DB access — no video bytes).

**Correction:** §4 of the previous index said the corpus was on hold because
`super-inbox/visual-search-adhoc` is public. **It is not** — an unauthenticated
GitHub API probe returns 404 while an authenticated fetch succeeds, i.e. the repo is
private. The videos are committed on `main` (`c3d8ff7`) and the hold is resolved for
that repo. The constraint that remains real: this is unconsented personal data,
faces cannot be blurred without destroying the very signal the corpus measures, and
it must not be pushed anywhere public or pointed at any third-party service.

---

## 2. Live configuration — current, and the baseline that produced §1

**Two configurations, and confusing them will mislead you.** *Current* is what a
user gets today. *Baseline 0* is what produced every saved prediction and every
number in §1, so it is the one you need in order to read those results. The offline
runner keeps both as named configs and refuses to conflate them (§3).

**Recognition** — `curify_background/app/utils/asl_utils.py`

**Backend selection, added locally 2026-10-12:** `ASL_RECOGNIZER=current_prod` (default)
calls the existing `transcribe_asl(video_path)` unchanged. `ASL_RECOGNIZER=unisign`
calls `app/utils/asl_backend.py` and requires `UNISIGN_API_URL` pointing to the
real-checkpoint service. This is an operator environment flag, not a public job
parameter. Activation and rollback instructions: **§17.5**. The table below still
describes the default recognizer; no production setting was changed in this update.

| Knob | Current (from 2026-08-29) | Baseline 0 (08-16 → 08-29) |
|---|---|---|
| Model | `gemini-2.5-flash` (`OPENAI_ASL_MODEL = "gpt-4o"` available, unused) | same |
| Temperature | `ASL_TEMPERATURE = 0.0`, passed explicitly | **unset → provider default 1.0** |
| Frame budget | **derived from duration** — `TARGET_FRAMES_PER_SEC = 2.0`, clamped to `MIN_FRAME_BUDGET = 24` … `MAX_FRAME_BUDGET = 240` | `FRAME_BUDGET = 96`, **absolute** |
| Density floor | `DENSITY_FLOOR_FPS = 1.0` → sets `low_density` | none |
| Caption dedup | adjacent duplicates merged, `DEDUP_MAX_GAP_S = 1.0` | none |
| Degeneracy signal | `DEGENERATE_REPEAT_COUNT = 3` → sets `degenerate_repetition` | none |
| Frame width | `KEYFRAME_WIDTH = 512` | same |
| Batch size | `BATCH_SIZE = 24` frames/call, **non-overlapping, stateless** | same |
| Motion probe | `PROBE_FPS = 4.0`, `PROBE_WIDTH = 160` | same |
| Idle threshold | `IDLE_QUANTILE = 0.35`, `ABS_MOTION_FLOOR = 2.0` | same |

⚠️ **`gemini-2.5-flash` — the model in *both* columns — can no longer be called with
the credential the evaluation environment holds.** `generate_content` returns
`404 NOT_FOUND` ("no longer available to new users") while `models.list()` /
`models.get()` still advertise it as generation-capable: a provider-side entitlement on
the project, not a defect in our code, prompt or sampling. **Production is unaffected —
it holds a separate key from the evaluation project**, and `ASL_MODEL =
"gemini-2.5-flash"` (`asl_utils.py:137`) still runs there normally. The consequence is
purely evaluative, and it is not small: the 09-06 benchmark had to be run on
`gemini-3.6-flash` (§11.2), so **no independent number describes production as
shipped**, and the offline runner can no longer reproduce `production_2026_08_29` at
all.

What the budget curve actually does, on real corpus durations:

| Duration | Baseline 0 | Current | batches |
|---|---|---|---|
| 6.7s | 14.33 f/s | 3.58 (floor, 24 frames) | 4 → **1** |
| 26.7s | 3.60 | 1.99 (53) | 4 → 3 |
| 76.8s | 1.25 | 2.01 (154) | 4 → 7 |
| 137.2s | **0.70** | 1.75 (cap, 240) | 4 → 10 |
| 189.5s | **0.51** | 1.27 (cap) | 4 → 10 |
| 300.0s | **0.32** | 0.80 (cap) — still under the floor, so flagged | 4 → 10 |

Short jobs got *cheaper*, not more expensive: a 6.7s clip used to burn all 96
frames across four calls, and now takes one — which also removes every batch
boundary, and with it the duplicate mechanism, on short input.

Pipeline: motion-energy probe → active/idle run segmentation → budget allocated
**100% inside active runs** → ffmpeg stills at 512px → N batched VLM calls → JSON
segments → sort → **dedup**. Response format is forced JSON; the prompt (`_PROMPT`)
instructs "translate meaning, not gloss", "omit stretches with no signing", "say so
in `notes` rather than guessing". Batches still have **no cross-batch context** —
see §7 LHF-8, which is the fix at source rather than after the fact.

**Orchestration** — `app/pipelines/asl_pipeline.py`, thin wrapper per the
architecture standard: `transcribe_asl()` → `translation_utils` → `subtitle_utils` →
`alignment_utils` mux. Dispatched from `orchestrators/dispatch_pipeline.py`. Persists
`asl_unverified`, `review_required`, `asl_frames_sampled`, `asl_segments`,
`asl_frame_budget`, `asl_sampling_density_fps`, `asl_low_confidence`.

**Pricing** — `JOB_CREDIT_COST["ASL_TRANSLATION"] = 0`
(`app/constants/subscription_constants.py`), mirrored as `ratePerMinute: 0` in
`curify-frontend/lib/create-job-ui.ts` and tripwired in
`curify-frontend/lib/__tests__/pricing.test.ts`. Was 8/min from 2026-08-16 to
2026-08-29 (§7 P0-1). For comparison: video dubbing 5, plain captioning 1.

**Frontend** — `curify-frontend/lib/tools-registry.ts`, slug `asl-video-translator`,
`status: "create"`, upload + YouTube input, target language selectable, no
voice-over. The result page renders `AslUnverifiedNotice` above everything else.

---

## 3. Where everything lives

**In this repo**

| Path | What |
|---|---|
| **this file** | everything. §9 = the 08-29 change record, §10 = the 08-30 decontamination, **§11 = the 09-06 How2Sign-128 baseline and the 8 fps ablation**. Appendix A = original spec, B = 08-18 recognition eval, C = 08-18 stage 1+2 |
| `curify_background/app/utils/asl_backend.py` | §17.5. Operator switch, unchanged production default, Uni-Sign HTTP adapter with bounded deterministic windows and explicit coarse timestamps; no weights in the worker |
| `curify_background/tests/test_asl_backend_unit.py` | Routing, failure/no-fallback, response identity, timestamp/window and cleanup tests; mocked service is not checkpoint inference validation |
| `workstream-tooling-and-engineering.md` §ASL | where ASL sits in the workstream; `AslSuspectedError` detect-and-offer routing |
| `tool-inventory.md` | portfolio-level row |
| `app/utils/asl_utils.py` | sampler + VLM recogniser + dedup/degeneracy/budget helpers + `detect_probable_asl()` |
| `app/pipelines/asl_pipeline.py` | thin pipeline wrapper; writes the runtime_config flags |
| `app/pipelines/base.py` | `_finalize_pipeline_run` — merges `runtime_config` (§6) |
| ⛔ `uni_sign_server/` — **PR #448, DRAFT, NOT MERGED** | §15. The Uni-Sign FastAPI service: `app/main.py` (`/healthz`, `/readyz`, `POST /translate`), `app/unisign_bridge.py` (lazy singleton, licence gate, sha256 check), `Dockerfile` (vendors upstream at `eed438bc…`), `patches/unisign_cpu_and_mt5path.patch`. ~~**Do not merge and do not push to ACR** — the checkpoint is CC BY-NC-4.0 and upstream ships no LICENSE (**P0-8**).~~ **Licence cleared 2026-09-21 (§16)** — merging is now an engineering and evidence call, not a permission one, and §15.2 still answers it "no". Any merge carries the required Uni-Sign credit line (LHF-10 item 7). The 1.19 GB checkpoint is never committed, never baked in, and mounted at run time only |
| `curify_background/tests/test_asl_dedup_unit.py` | 28 tests, fixtures from the real corpus. **Register new test files in `tests/layers.py` or they never run.** |
| `curify-frontend/app/[locale]/_components/AslUnverifiedNotice.tsx` | the user-facing warning; reads `runtime_config` off `GET /projects/{id}` |
| `curify-frontend/lib/__tests__/pricing.test.ts` | tripwire — the UI's `ratePerMinute` vs the backend's `JOB_CREDIT_COST` |
| `curify-frontend/scripts/{add_asl_job_warning,fix_asl_tool_copy}_i18n.py` | the 10-locale copy patches |
| `dev/asl_mvp/code/{pose55,run_tgcn,bench}.py` | MediaPipe→WLASL-55 extractor, TGCN loader, bench harness |
| `dev/asl_mvp/bench/` | `ground_truth_1434.json`, verified 2000-gloss index map |
| `dev/jayw/raw/asl-demo-translation.mp4` | the demo asset on the tool page (= case 155). ⚠️ **This is the captioned OUTPUT** (md5 `d714db71…`), identical to `curify-frontend/public/video/`. The caption-free source is `curify-frontend/raw/asl-groundtruth-08-25/asl-demo-translation_raw.mp4` (md5 `d71313d0…`) and is what the corpus now holds. Confusing the two is what caused §1.0 |
| ~~`curify-frontend/raw/asl-groundtruth-08-25/`~~ | **Not the canonical location — do not push it.** A 29 MB local staging copy: untracked, *not* gitignored, and containing user 1252's identifiable video. The gold lives in the side repo at `asl-translator/data/asl_corpus/ground_truth/` (both SRTs verified byte-identical to the local copies), which is private and carries the sensitivity notice. Committing it into a deployed frontend tree would put unconsented personal data somewhere it has no reason to be. |

**External research — `super-inbox/visual-search-adhoc` (private)**

| Ref | What |
|---|---|
| `@8746ab1:docs/daily_report/8.22/asl-transcription-ideas/` | baseline ladder B0→B4, decision tree, 12-item no-training quick-win list, note that DeepMind shipped **SL2T (Aug 2026)** validating pose→text as an approach class (weights unavailable to us) |
| `main:asl-translator/` **(merged 2026-08-29, `49bdab0`)** | corpus + ground truth + predictions, `asl-eval/` scorer and offline production-equivalent runner, `asl-ground-truth-annotator/` browser tool, `BOSS_SUMMARY.md`, `DETERMINISM_EXPERIMENT_V1.md`, `SIGNCAPTION_COMPARISON_V1.md`, `ANNOTATION_PLAN.md`, `annotation_queue.csv` |
| `jwang/asl-decontaminate-corpus-2026-08-30` | **the leakage fix.** `data/asl_corpus/CONTAMINATION.md` is the full account. `asl-eval/check_leakage.py` (OCR detector, validated against both known positives), `asl-eval/corpus_guard.py` (refuses leaky inputs and retracted predictions), `label_in_input` in `manifest.json` + both CSVs, `input_md5` in the runner's `run_metadata` |
| same, `docs/daily_report/8.26/asl-ground-truth-eval/` | the verified two-case A/B and its per-case result JSONs |
| `baobao/asl-temporal-ablation-2026-09-06` **(not merged to `main` as of 09-07)** | **everything in §11.** `data/public_benchmarks/how2sign_v2/` — the frozen 128-clip benchmark, `FREEZE.sha256` + `FREEZE_CHECKSUMS.sha256` (260 files), `SELECTION_METHODOLOGY.md`, `validation/leakage_check_results.json`. `evaluation/run_curify_how2sign_v2_benchmark.py` — the benchmark driver (resumable; skips clips already on disk). Two new configs in `asl-eval/run_current_model.py` + `TestExperimentB8fpsAblation` in its test file |
| same, `docs/daily_report/9.5/asl-evaluation-v2/` | the frozen Curify baseline: `BOSS_SUMMARY.md`, `BASELINE_METRICS.json` (machine-readable, every figure re-derived from the saved outputs), `BASELINE_SCORECARD.csv` (the three-way table), `QUALITATIVE_REVIEW_CANDIDATES.csv` (7 hand-picked clips — read this before forming an opinion about the failure mode) |
| same, `docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md` | the 8 fps arm: what ran, what is blocked, and the exact resume command |
| same, `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/` | **everything in §12.** `inspector/` — 12 frame-inspector pages + index; `controlled_ablation/{adaptive_vs_uniform_2fps,independent_vs_sliding}/` — each with its own write-up, `design_check.json`, `paired_results.csv`, per-clip predictions and 12 side-by-side comparison pages; `taxonomy_40_text_semantic_review.csv`; `review_app/` (built, never used); `FINAL_TEMPORAL_DIAGNOSIS.md`, `EXPERIMENT_INDEX.md`. ⚠️ `taxonomy_40_human_review.csv` is **not** a taxonomy result — see §12.5 |
| same, `docs/daily_report/9.9/asl-evaluation-driven-improvement/` | `WORK_REPORT.md` + `BOSS_SUMMARY.md` — the manager-facing consolidation, including the gap analysis against the shared "evaluation-driven self-improvement" pipeline (verdict: largely what we already did; two genuinely new ideas, both untested) |
| same, `docs/daily_report/9.2/asl-baselines/SPAMO_SSVP_SLT_FEASIBILITY_RECHECK.md` | why SpaMo and SSVP-SLT cannot be run at all — re-verified live 09-10, unchanged (§12.6) |
| same, `docs/daily_report/9.10/` + `docs/daily_report/9.11/` | **everything in §14.** `9.11/ASL_WORK_REPORT.md` + `ASL_MANAGER_SUMMARY.md` — the consolidation (no model re-run to produce them); `9.10/asl-native-video-evaluation/BLOCKER_STATUS.md` — the 5/12 split, the 7 Files-API clips, the ruled-out local explanations and the exact resume command; `9.10/trajectory-tracking-feasibility/` — `PHASE_D0_RESEARCH_AND_AUDIT.md`, the D1/D2 plan, `PHASE_D1_RESULTS.md`, `PHASE_D2_RESULTS.md`, `MANAGER_SUMMARY.md`; `9.10/signcaption-signspeak-research/CHECKLIST.md` — per-item known/unknown with a source for every "known" |
| same, `docs/daily_report/9.15/` | the matched-126 / matched-15 / matched-8 scorecards quoted in §15.2, and the Uni-Sign decoding-parameter audit (`num_beams`/`max_new_tokens` are the only knobs wired through; **never tuned**) |
| same, `docs/daily_report/9.17/unisign-deployment-work-report/` | §15.1's PARTIAL grade — container, endpoints and pose extraction all verified against a **22-byte dummy** checkpoint. Also answers two standing questions: Uni-Sign emits **no timestamps**, and the 128-clip benchmark was always run on pre-segmented clips |
| same, `docs/daily_report/9.18/asl-manager-followup-a-c/` | Phase A — the first real-checkpoint run, and **the two degenerate real-user-video outputs in §15.2**. Phase C — the first `gloss-free-asl-translation` bring-up |
| same, `docs/daily_report/9.19/unisign-real-e2e/` | **§15.1–15.3.** `RESULTS.md`, `score_e2e.py`, `scores.json`, both clips' raw responses and repeat runs, container logs, `long_docker_stats.log` (the 6.6 GiB peak). Scoring reuses `asl-eval/lib.py::text_metrics` unmodified; BLEU/chrF via `sacrebleu` 2.6.0 |
| same, `docs/daily_report/9.19/unisign-overlapping-segmentation/` | **§15.4.** `scripts/{segment_video,run_segments,merge_and_score}.py`, `segmentation_manifest.json`, `segment_predictions.json`, `comparison_metrics.json`, `boundary_frames.jpg`, `motion_strip.txt`. ⚠️ Its §0 audits an **untracked local POC on a different video** (1252, 13 segments) that is not on this branch and not on GitHub — do not go looking for it |
| same, `docs/daily_report/9.19/gloss-free-asl-translation-audit/` | **§15.6.** `checkpoint_search.json` (the exhaustive negative result), `mediapipe_vs_rtmpose_comparison.json`, `run_mediapipe_extraction.py`, `compare_mediapipe_vs_rtmpose.py` |
| same, `asl-translator/asl-eval/run_native_video.py` + `evaluation/run_native_video_how2sign_v2_benchmark.py` | the native-video path P0-4 asked for: Files API, **1 call/clip**, dry-run default (a real run needs `--run` **and** `--acknowledge-private-data-upload`), resumable, upload cleanup in a `finally`, provenance on every prediction. Built as a **sibling** of `run_current_model.py`, so every frozen frame config stays byte-for-byte unchanged. Config `native_video_2026_09_10_gemini_3_6` — ⚠️ carries the P0-5 `thinking_level: medium` defect |
| same, `asl-translator/asl-eval/trajectory_probe/` + `evaluation/run_trajectory_augmented_experiment.py` | §14.2. RTMPose extraction via `rtmlib`, summarisation, overlay/SVG rendering, keypoint schema, and the D2 controlled-experiment driver |
| same, `asl-translator/evaluation/compare_how2sign_v2_systems.py` | the 4-system scorecard and pairwise comparisons, built from the already-written `corpus_summary.json` files — read-only, makes no model calls |
| ⚠️ **not in git** | `asl-translator/evaluation/results/` is gitignored *by design*, so the 128 baseline predictions and the 76 completed 8 fps predictions exist **only on the machine that ran them**. Every §11 number is reproducible from that directory and from nothing else. |

**The offline runner is the only way to evaluate a change without touching
production**, and it **vendors a copy** of our constants rather than importing them
(importing `app.config` would demand production env vars). **Six** named configs, and
they are not interchangeable — reporting one as another is the single easiest way to
publish a wrong number here:

| `--config` | what it is |
|---|---|
| `baseline0` *(default)* | production 08-16 → 08-29. **Historical — do not edit.** Every saved prediction and every §1 number came from it. |
| `temperature0` | the 8.26 A/B arm: baseline0 with temperature pinned, nothing else. |
| `production_2026_08_29` | what production runs now — `gemini-2.5-flash`, temperature 0, duration-scaled budget, dedup. **Currently unrunnable offline** — entitlement-blocked (§2). |
| `evaluation_2026_09_04_gemini_3_6` | **Baseline A of §11.** `gemini-3.6-flash`, `thinking_level: medium`; production's exact prompt (`sha256 ea8c5cb1…`), sampling, batching, dedup and schema. The only config any How2Sign-128 Curify number comes from. **Not `production_2026_08_29` and must never be reported as it.** |
| `evaluation_2026_09_06_gemini_3_6_8fps` | **Experiment B of §11.6.** Baseline A with exactly one knob moved: `target_frames_per_sec` 2.0 → 8.0, declared per-config so the module constant stays 2.0 for everyone else. Run is 76/128 complete. |
| `evaluation_2026_09_07_gemini_3_6_uniform_2fps` | **Arm B of §12.2.** Baseline A with the timestamp-allocation formula swapped for `allocate_timestamps_uniform()` (evenly spaced), density held at 2.0. Added **additively** — `allocate_timestamps()` and every pre-existing config are byte-for-byte unchanged. 12 diagnostic clips only, never run on the full 128. |

⚠️ **Two more configs exist outside that table** and are not `run_current_model.py`
entries: `native_video_2026_09_10_gemini_3_6` (§14.1, in `run_native_video.py`) and the D2
trajectory-augmented arm (§14.2, in `run_trajectory_augmented_experiment.py`). Both are
siblings by design, so the six frozen configs above are unaffected — but neither is covered
by `TestProductionParity`, and their results directories are gitignored like everything else
under `evaluation/results/`.

**Two guards now sit in front of any number the harness can produce.**
`corpus_guard.assert_input_usable` refuses a video the manifest marks as showing its own
answer, and `assert_prediction_usable` refuses a prediction that was retracted or generated
from one; `evaluate.py` and `run_current_model.py` both call them, and `status.py` reports
`blocked_label_leakage`. `check_leakage.py` OCRs the corpus and fails on any video whose
on-screen text overlaps its own reference — it runs two passes per frame (whole frame
upscaled, and bottom third upscaled) because **tesseract reads nothing from 155's captions
at native 640×360 and reads them perfectly from an upscaled crop**, so a full-frame-only
checker would have cleared the very file that caused this.

`TestProductionParity` in `asl-eval/test_run_current_model.py` loads
`asl_utils.py` **directly by path** and diffs constants, prompt, budget curve,
normalizer and dedup behaviour against it, so the next drift fails a test instead of
going unnoticed. It works because `asl_utils` keeps every heavy import
function-local; it skips cleanly when curify-studio is not checked out alongside.
Confirmed to fail on drift, not merely to pass in sync.

*What the 8.22 pass got wrong, for lack of repo access:* it could not find the live
tool and inferred our ASL handling was audio-only via `has_speech()`; it proposes
motion-aware sampling as the cheap next win — **we already ship it**, and 08-18 ruled
out sampling density as the cause of the instability. Its blocked dependencies (live
config, real cases, reference transcripts) are answered by §2, §5 and §6 here.

---

## 4. Evidence ledger

| Claim | Evidence | Confidence |
|---|---|---|
| General VLM over sampled frames confabulates | 5 configs × repeat runs, all different; **reversed frames still fluent at same stated confidence** | settled |
| Not fixable by sampling density | 95 frames / 16.6s = 1 per 0.175s, near budget max, denser than uniform — still unstable | settled |
| Not fixable by resolution, model tier, batch size, or native-video input | each tested independently 08-18 | settled |
| TGCN-WLASL (ISR) unusable on our pose front-end | **0/12 top-5 on in-domain WLASL clips**; 6 representation variants ruled out; checkpoint verified genuinely trained | settled |
| The ceiling is the field, not our engineering | YouTube-ASL finetuned SOTA **12.39 BLEU** on studio-quality How2Sign (production MT is 40–50) | settled |
| Motion-adaptive sampler works | 100% of budget inside active signing where active is 65% of timeline | settled, **reusable** |
| Non-determinism reproduces in production on identical input | jobs 1466 / 1467 — same file, 11s apart, disjoint transcripts (§5.1) | settled |
| Sampling density collapses ~44× across real job durations | `FRAME_BUDGET` absolute; degenerate output on both ~190s jobs (§5.2) | settled — **fixed 08-29** |
| The unverified flag never reaches the user | wiped by `_finalize_pipeline_run`; no frontend reader (§6) | settled — **fixed 08-29** |
| **`temperature=0` largely fixes repeatability** | WER 0.97 → 0.18, IoU 0.46 → 0.91 on one video; 12/18 segments byte-identical | **new 08-26, one video** |
| **`temperature=0` does NOT fix accuracy** | verified gold: 0.370→0.333 and 0.923→**0.923**; SignCaption gap unchanged at ~0.95 | **new 08-26, settled** |
| ~~**On well-framed slow content the recogniser is essentially correct**~~ | ~~155 @ temp0: 0 sub, 0 del, 9 ins~~ | **RETRACTED 08-30 — the input had the answer burned in (§1.0)** |
| **Fingerspelling fails completely and temperature-independently** | 1252: "Greg"→"H.G.Q."/"HPG", "Sara" omitted, both configs | **new 08-26** |
| The curated 13-video corpus is genuine signing | frame/audio audit: 12 confirmed, 1 uncertain, 0 non-ASL | **new 08-26** |
| The broader production video pool's ASL-vs-ordinary mix | **not measured**; needs authorized metadata-only DB access | open |
| `visual-search-adhoc` is private, so the corpus hold is resolved | unauthenticated GitHub API 404 vs. authenticated fetch success | **new 08-29** |
| **Two corpus videos had their reference answer burned into the frame** | 155 byte-identical to the published captioned demo; prediction = gold verbatim, 0 sub / 0 del; PSNR 28.1 dB full-frame vs 47.1 dB excluding the caption band; 1320 captioned throughout | **new 08-30, settled** |
| **Only those two** | all 13 re-checked frame by frame; matches `VIDEO_TYPE_AUDIT.csv`'s own `burned_in_captions` column | **new 08-30, settled** |
| **1320's captions are an answer key, not a paraphrase** | OCR of its title cards: "Certificate Program for Sign Language Interpreters / RECEPTIVE SKILLS EVALUATION / SIGN TO VOICE / Record yourself voicing the video" | **new 08-30, settles §9.5** |
| ~~**Dedup alone makes the demo clip an exact match**~~ | ~~155 @ temp0 WER 0.3333 → 0.0000~~ | **RETRACTED 08-30.** The fix is still correct; its measured benefit is withdrawn (§1.0) |
| **The two duplicate populations are 13× apart** | batch-boundary repeats at 0.32s / 0.37s; degenerate repeats at 5.0–13.6s. Any threshold in 0.4–4.9 behaves identically. *Caveat 08-30: the short-gap examples came from 155, so the separation is real but its measured spacing is not evidence about signing* | **08-29, weakened 08-30** |
| **Repetition cannot detect fluent fabrication** | job 1442 (300s, sparsest sampling, most-suspected output) is 100% unique captions and does not trip the detector. Only `low_density` catches it | **new 08-29, settled** |
| The frontend described a sign-trained encoder/decoder we do not have | `aslVideoTranslator.deep.how.p2/p3` in all 10 locales; no such component exists | **new 08-29, partly open (§9)** |
| **1252 cannot carry an accuracy claim either** | its reference is a Curify outreach translation with no annotator or method on record; `inventory.json` marks it `non_independent` / `usable_for_official_metrics: false` — **0 of 13 private-corpus videos qualify** | **new 09-02, settled** |
| **A production-shaped configuration scores WER 0.9762 / BLEU 0.1341 on 128 independently-referenced clips** | frozen How2Sign-128, 128/128 succeeded, 260 checksums re-verified, OCR leakage check clean on every clip (§11) | **new 09-06, settled — the only defensible accuracy number we have** |
| **No clip is a clean pass** | 0/128 below WER 0.5; median 1.0; the best clip (0.75) is a truncated fragment; 1 empty prediction | **new 09-06, settled** |
| **The failure is deletion/coverage, not mis-reading** | predictions are 41% of reference length; 61% of 2,906 edit ops are deletions vs 1% insertions; temporal recall 0.58 against precision 0.99 | **new 09-06, settled** |
| **Curify is the weakest of the three systems on content correctness** | matched-126: Uni-Sign BLEU 5.40 and chrF 22.83 vs Curify's 0.1346 / 11.30. Curify's *WER* sits mid-pack only because deletion-heavy output has fewer chances to substitute | **new 09-06, settled** |
| **No validated production replacement; Uni-Sign is the strongest tested research base** | §17 supersedes the blanket “no open model to switch to”: its representation helps, with 85.7% of the controlled preprocessing gap recovered; user-video quality is unvalidated. Written weights permission cleared 09-21 (§16). Production remains selected; Uni-Sign integration is opt-in and unhosted | **updated 10-16**, P0-12 controlled inference complete; production hosting/quality still open |
| **No frame-based temporal fix moves the failure** | three controlled ablations — density 2→8 f/s (76 clips, WER 0.9730→0.9715), motion-weighted→uniform sampling (12 clips, 1.0524→1.0594), independent→overlapping batches (12 clips, 1.0524→0.9545). **0 of 12 clips recovered correct meaning under any arm**; median per-clip delta 0.0000 in all three (§12.2) | **new 09-09, settled at these sample sizes** |
| **The batching arm's WER gain is a length artifact, not quality** | chrF2 14.30→**13.54** (worse) while WER "improved"; prediction/reference length 0.566→0.458. The 8 architecturally-inert clips move by −0.0673 from decoding noise alone (§12.2) | **new 09-09, settled** |
| **It is not "right meaning, wrong words"** | 40-clip text semantic review: **0/40** correct-meaning-different-English, 0/40 fully adequate, 37/40 wrong or unrelated, 36/40 clear topic mismatch (§12.3) | **new 09-09, settled — closes the last benign reading of §11** |
| **SpaMo and SSVP-SLT cannot be run at all** | SpaMo's only checkpoint is Phoenix14T (German) and no How2Sign config/checkpoint exists; SSVP-SLT has **zero checkpoints of any kind**. Both commits byte-identical to the 09-02 check, re-verified live 09-10 (§12.6) | **09-02, re-confirmed 09-10, settled** |
| **Native video input beats extracted frames** | same clip, same model (`gemini-3.6-flash`), same scorer, modality the only variable: WER 0.9615 → **0.8269**, CER 0.7131 → 0.6454, 1 call vs 7. Numbered-list structure recovered; **2 of 7 items semantically correct** where every §12 arm scored 0/12 (§13) | **new 09-10 — n=1, circular reference. A signal, not a measurement (P0-4)** |
| **Fingerspelling fails under native video too** | Greg → *"E"*; Sara absent. Fails identically across `baseline0`, `temperature0`, 3.6-frames and 3.6-native (§13.4) | **new 09-10 — extends §4's "temperature-independent" to modality-independent** |
| **`thinking_level: "medium"` is silently ignored** | not in the SDK's `ThinkingLevel` enum (`UNSPECIFIED` / `LOW` / `HIGH`); warns and drops, confirmed firing on `evaluation_2026_09_04_gemini_3_6` itself (§13.6) | **new 09-10 — every §11/§12 reproducibility claim needs re-checking (P0-5)** |
| The ASL failure taxonomy — handshape / motion / fingerspelling / facial-non-manual | **not established.** Requires an ASL-fluent reviewer. ⚠️ `taxonomy_40_human_review.csv` *looks* like it holds this and does not — unreviewed tags are serialised as `False` (§12.5) | open — **blocked on ASL expertise** |
| Native/direct video input, and hand-crop dual-stream input | **not tested** — no video-upload path and no crop/hand-detection code exists anywhere in the runner (§12.4) | open — **the two remaining untested axes** |
| Whether the model is simply under-generating rather than mis-reading | **not tested.** §11.4's shape (41% of reference length, 61% deletions, 1% insertions) is consistent with a prompt/token-cap/dedup cause that no experiment has probed (§12.4) | open — **cheapest untested hypothesis on the board** |
| Curify's *shipped* configuration (`gemini-2.5-flash`) on any independent benchmark | **not measured** — entitlement-blocked; §11 measures the 3.6 migration arm instead | open |
| How2Sign's public English references may be memorised by the model | **not tested** — the `SENTENCE_NAME`-without-video control (scorecard P0-2) was never run, and no such control exists in the harness (§11.5) | open — does not threaten §11's numbers, gates any future good one |

---

## 5. The real-user corpus (this is an asset)

**13 distinct videos, 9 submitters, 2 verified-gold + 2 candidate references.**
Committed to `visual-search-adhoc` (private) at
`asl-translator/data/asl_corpus/`. Production copies live in blob storage at
`videos/<user_id>/<video_id>/<video_id>.mp4`.

All 9 `asl_translation` jobs to date:

| Job | User | Duration | Resolution | Status | Credits | Output |
|---|---|---|---|---|---|---|
| `155_…40388ea9` | 155 *(internal)* | 26.7s | 640×360 | FAILED | – | `GOOGLE_API_KEY` missing |
| `1434_…f0aeac0e` | 1434 | 16.6s | 2732×2048 | COMPLETED | not charged | ground truth held; operator rerun, sent as experimental |
| `1442_…213c7671` | 1442 | **300.0s** | 1280×720 | COMPLETED | **40** | 15 segs, fluent narrative |
| `1457_…8a1469a8` | 1457 | 28.3s | 2340×1080 | FAILED | – | Gemini capacity cap |
| `1466_…78caaeaa` | 1466 | 190.0s | 1920×1080 | FAILED | – | upload still PROCESSING after 900s |
| `1466_…934a8b60` | 1466 | 189.5s | 1920×1080 | COMPLETED | **32** | 24 segs, degenerate tail |
| `1467_…2c67f749` | 1467 | 189.5s | 1920×1080 | COMPLETED | **32** | 29 segs, degenerate tail |
| `1474_…fb0a9864` | 1474 | 11.5s | 1920×1080 | COMPLETED | **8** | 5 segs |
| `1477_…8ab4cd12` | 1477 | 6.7s | 640×480 | COMPLETED | **8** | 4 segs |

**Total charged: 120 credits across 5 jobs.** 7 real users, 8 jobs, 2026-08-17 →
08-23. **Repeat usage: 0.** All 7 signed up minutes before submitting (SEO landing →
single job → gone). Two failures were ours (quota cap, upload timeout), not the
signer's.

### 5.0 Misfiled ASL jobs — 4 more videos, filed as speech jobs

These predate the `asl_translation` job type or went to the wrong tool. All failed,
none were charged, and they are **the best-labelled videos we own**.

| Job | User | Duration | Filed as | Failure | Why it matters |
|---|---|---|---|---|---|
| `1252_…8bf77966` / `…9614c46d` | 1252 | 76.8s | `subtitle_only` + `full_translation` | "Translation failed or returned empty" | **Human-verified SRT.** Fingerspelled names (Greg, Sara) + numbered items — our only fingerspelling case. Hand-translated and emailed (`gtm_tools/send_1252_asl.py`). |
| `1252_…527bf833` | 1252 | 250.8s | `video_transcript` | `NO_SPEECH` | Same submitter's second video. |
| `1415_…754da22a` / `…cff48289` | 1415 | 200.6s | `full_translation` ×2 | WhisperX unreachable | The clip the motion sampler was validated on. |
| `1320_…025d7477` | 1320 | 137.2s | `video_transcript` | `NO_SPEECH` | **Confirmed ASL 2026-08-25.** Studio-quality, single signer, face fully visible — **and English captions burned into the frame, which made it a leakage risk, not a bonus.** Now evaluated only through a masked input; see §1.0 and LHF-5. |

Checked and **excluded**: `1328_…cb7702b1` (123.7s, `NO_SPEECH_DETECTED`) — the
failure reason describes background music plus on-screen text, not signing.

The `NO_SPEECH` copy these users saw — *"We can't transcribe sign language or silent
footage"* — is correct and was doing its job. Nothing routed them to the ASL tool.

### 5.1 The free production determinism experiment — jobs 1466 vs 1467

`No head half 1.mp4`, submitted by **two different accounts 11 seconds apart** and
processed independently. Not byte-identical (each upload re-encoded) but identical in
content: same duration to the millisecond, same codec/resolution/framerate, same
frame counts, sizes differ 0.02%, frames at 30s/90s/150s visually identical.

- **Segment boundaries: 29 of 45 timestamps shared** → the motion sampler is deterministic.
- **Text: effectively disjoint** → the recogniser is not.

| t | job 1466 | job 1467 |
|---|---|---|
| 1.1–14.3 / 4.9–14.3 | "What are you doing? Tell me." | "You, / next, you / will expand." |
| 20.2–25.3 | "Repeat that. Think and explain." | "Work together / to grow" |
| 27.6–37.4 | "Begin three tasks together." | "and give / a meeting for three / to further grow," |
| 89.7–94.8 | "Apply hand cream." | "Wash your hands." |
| 186.5–188.2 | "With." | "Explain to the group." |

*Where* signing happens is stable; *what* was signed is not. Both users were charged
32 credits. **As of 08-26 the decode-temperature share of this variance is measured
(§1.2): pinning `temperature=0` takes repeat-run WER from 0.97 to 0.18.** The
head-framing caveat in §1.2 still applies to any accuracy reading of this pair.

### 5.2 Density collapse on long input ✅ *fixed 2026-08-29 — see §2 for the new curve*

`FRAME_BUDGET = 96` was absolute, so mean sampling density was `96 ÷ duration`:

| Duration | Budget-implied density | Observed output quality |
|---|---|---|
| 6.7s | 1 frame / 0.07s | 4 short sentences |
| 16.6s | 1 frame / 0.175s *(measured 95 frames)* | greeting-shaped, ~65% "right" by prior |
| 189.5s | 1 frame / 1.97s | **`Many / Many / All / Many`**, `Not / Not / Not over / Not` |
| 300.0s | 1 frame / 3.13s | fluent narrative about coffee, growth, community |

A **~44× spread with no warning to the user and no price difference.** The two
failure shapes are both bad and differently bad: the ~190s jobs degenerate into
single words (visibly broken), while the 300s job produces *the most confident, most
fluent, most fabricated* output in the corpus — the "priors dominate when perception
is weak" mechanism of Appendix B §5.3.

*Per-job frame counts are unknown because `asl_frames_sampled` is destroyed by the
bug in §6 — the two problems compound.*

---

## 6. The unverified flag — why it never reached the user, and what fixed it ✅

**Fixed 2026-08-29.** Kept here because the failure is instructive and the bug was
general, not ASL-specific.

`asl_pipeline.py` was careful — its docstring said every job carries
`asl_unverified` and `review_required` "so the frontend can surface it". Two things
made that false for eleven days of paid traffic:

1. `_finalize_pipeline_run` (`app/pipelines/base.py`) **replaced `runtime_config`
   wholesale** with the dubbing-settings dict, seconds after the ASL pipeline wrote
   the flags. Verified in the DB: all 5 real completions carried only
   `{tts, alignment, translation, transcription}`; the only row with
   `asl_unverified` was 1434, where an operator had written it by hand.
2. `grep` across `curify-frontend` found **no reader** for either flag — only
   comments in `tools-registry.ts` asserting they existed.

The single surviving warning was the `[AI-generated ASL translation — unverified]`
prefix on caption line 1.

**The fix, and one thing it nearly broke.** `_finalize_pipeline_run` now merges,
mirroring `dispatch_pipeline.py`, with two corrections to that pattern: `or {}`
rather than a truthiness check, because the column is nullable at the DB level and
`**None` raises `TypeError`; and **failure keys are dropped on the COMPLETED path**.
That second one is the regression a naive merge introduces — a job that failed, was
reprocessed and then succeeded would keep `failure_code`, and
`GET /projects/{id}/status` reads it straight out of `runtime_config`, so the API
would report a failure next to `status=COMPLETED`.

**No backend schema change was needed to surface the flags.** `GET /projects/{id}`
has always returned the whole dict via `ProjectDetailsResponse.runtime_config`; the
frontend's `ProjectDetails` type simply never declared the field, so the payload was
discarded on arrival. One line of TypeScript, not an endpoint change.

This was a **general** bug: any pipeline writing `runtime_config` mid-run lost it.
Every video job type went through that path.

---

## 7. Low-hanging fruit and P0 items

**October priority update (2026-10-16, §18):** P0-11/13 complete; P0-12 controlled
T4/fp16 diagnosis complete. P0-14's frozen-feature probes give qualified representation
evidence; P0-15 is NOT SUPPORTED at dev stage and has no final evaluation. Stop tuning
failed rules on these same clips. Prioritize ASL video review, reference-free input
preparation, and a newly frozen confidence/verifier experiment only if research resumes.
Keep production unchanged; the earlier dated queue below is history.

Ordered by (live damage) then (measured gain ÷ effort). Nothing here changes the
field ceiling in §8 — these make the tool honest, reproducible, and correct on the
content it *can* read.

> **2026-08-29 — P0-1 and LHF-1 through LHF-4 shipped.** ~~Measured after the fact by
> re-scoring the saved predictions: the demo clip goes to WER 0.0000, an exact match.~~
> **That measurement was retracted on 2026-08-30 (§1.0)** — it was the model reading
> captions burned into the input. The code changes stand; their headline number does not.
> The degeneracy detector fires on all three ~190s jobs and on nothing else (unaffected —
> those videos are clean). New constants live in `asl_utils.py`; 28 unit tests in
> `tests/test_asl_dedup_unit.py`, registered in `tests/layers.py`.
> **LHF-5 through LHF-8 remain open.**
>
> **The offline runner is in sync** (`visual-search-adhoc` @
> `jwang/asl-eval-mirror-2026-08-29`). It vendors a copy of production's constants
> rather than importing them, so the 08-29 change put it behind; it now carries a
> third config, `production_2026_08_29`, alongside the untouched `baseline0` and
> `temperature0` — those two still reproduce every saved prediction and the 8.26
> report, and must not be edited. A `TestProductionParity` case loads
> `asl_utils.py` directly by path and diffs constants, prompt, budget curve and
> dedup behaviour against it, so the next drift fails a test instead of going
> unnoticed. It skips when curify-studio is not checked out alongside.

> **2026-09-07 — §7 is no longer the whole action list.** The 09-04 scorecard and §11
> carry items this section predates, and two of them now sit at the top of the queue:
> **P0-2** (the on-screen-text prompt bug, still user-facing) and **P0-3** (the
> memorisation control that should have preceded §11). **LHF-9** is the ablation §11.6
> left 76/128 finished.
>
> ~~**2026-09-10 — the queue has a new head: P0-4.**~~ §13's native-video result was the
> only positive signal this project had produced, and scaling it to the frozen benchmark was
> *cheaper* than the frame pipeline it replaces (1 call/clip vs 4–7). **P0-5** is the
> reproducibility bug §13.6 surfaced.
>
> **2026-09-12 — P0-4 ran, and the queue reorders again (§14).** Native video is built and
> resumable, but **0 of 5 scored benchmark clips recovered meaning** and 7 are stuck in the
> Files API, so the gate is inconclusive and P0-4 is no longer something to push harder on —
> it is something to finish *if the API cooperates*. Two new items come out of §14:
> **P0-6** (why does Uni-Sign fail? — cheapest item on the board, needs no new run) and
> **P0-7** (Sign-Speak ToS clearance — email and legal, not code). Order of work now:
> **P0-6, P0-2, P0-3, P0-5, P0-7, then P0-4's remaining 7 and LHF-9 as billing allows.**
>
> **2026-09-19 — a licence now sits above the whole queue (§15).** Uni-Sign was built as a
> service and run on the real checkpoint; it works, and it cannot be deployed. **P0-8**
> (CC BY-NC-4.0 clearance) gates PR #448, every ACR push and every hosting option, and no
> engineering moves it. **P0-9** (segment-level gold) is what would turn §15.4's "no clear
> benefit" into a measurement, and **LHF-10** is the time-segmentation shim that *is* the
> backend integration, not a detail after it. **P0-6 is now half-answered** — the mechanical
> half — and the analysis it actually asks for is still free and still unrun. Order of work
> now: **P0-8, P0-6, P0-2, P0-3, P0-9, LHF-10 (only if P0-8 clears), then P0-5, P0-7, P0-4's
> remaining 7 and LHF-9 as billing allows.**

> **2026-09-21 — P0-8 cleared, and the queue deliberately does *not* reorder around
> deployment (§16).** Written permission arrived from Uni-Sign's first author: commercial use
> and redistribution of the weights, MIT intended on the code, a credit link required,
> How2Sign explicitly excluded. **LHF-10 is unblocked** and PR #448 is mergeable in principle.
> It is still not worth shipping — a licence does not touch §15.2's user-video degeneration —
> so the head of the queue is unchanged. Order of work now: **P0-6, P0-2, P0-3, P0-9,
> LHF-11** (owed to Uni-Sign, cheap) **, LHF-12, LHF-10 only if a deployment is actually
> decided, then P0-5, P0-7, P0-4's remaining 7 and LHF-9 as billing allows.**

### P0-1 — Stop charging for output we've documented as untrustworthy ✅ **DONE 2026-08-29**
Open from 2026-08-18 to 2026-08-29; 5 users paid 120 credits in that window, and §1.1
puts a number on what they bought: WER 0.92 on the one real user video we can score.
**Resolved as rate → 0, tool stays live**: `JOB_CREDIT_COST["ASL_TRANSLATION"] = 0`
plus `ratePerMinute: 0` in `create-job-ui.ts`, now tripwired in
`lib/__tests__/pricing.test.ts`. A zero guard was added to `charge_user_if_needed`
so a free job stops writing a 0-credit `USAGE_DEDUCTION` row.
Demoting to `status: "demo"` was rejected on inspection: **there is no waitlist
anywhere in the frontend** — a demo tool falls through to an italic "Coming Soon"
paragraph — so demoting would have forfeited the corpus and offered users nothing.

### LHF-1 — Deduplicate consecutive repeated segments ✅ **DONE 2026-08-29** ⚠️ *measurement retracted 08-30*
~~**Measured:** on the demo clip this is the difference between WER 0.3333 and 0.0000.~~
**The demo clip had the reference burned into it (§1.0), and both "duplicates" were two
batches reading the same on-screen caption.** The fix is still right — stateless
non-overlapping batching genuinely does emit a sign spanning a boundary twice — but it is
now **unmeasured**, and 1252 (the one clean case) has no adjacent duplicates to fix.
**Cause:** `transcribe_asl` slices `frames[i:i + BATCH_SIZE]` into **non-overlapping,
stateless** batches, each sent with the same prompt and no knowledge of the others. A
sign spanning a batch boundary gets emitted by both batches. 155 is 96 frames = 4
batches = 3 boundaries, and shows 2 duplicates.
**Fix:** after `segs.sort(key=lambda s: s.start)` (`asl_utils.py:419`), collapse
adjacent segments whose normalized text is identical and whose gap is under ~0.5s,
keeping the union span.
**Guard:** ASL uses reduplication for emphasis, so gate on *adjacency + small gap +
exact normalized match*, not on text alone.
**Why it matters beyond the metric:** a user reading "My mother is twenty-nine" twice
sees a defect. This is the one error class that is both visible to the user and
completely fixable.

### LHF-2 — Pin `temperature=0` ✅ **DONE 2026-08-29**
**Measured:** repeat-run WER 0.9706 → 0.1786, IoU 0.4631 → 0.9085, 12/18 segments
byte-identical. One line in `_call_vlm`'s `GenerateContentConfig`.
**Sell it as stability, not accuracy.** On the one clean verified case (1252) it moves
WER not at all, and the SignCaption gap is unchanged. (The 155 improvement previously cited
here is retracted — §1.0.) What it actually
buys: the same video stops producing two different bills' worth of different answers,
support can reproduce a complaint, and every future experiment gets a stable baseline
to measure against. That last one is why it should land *before* LHF-3 and LHF-6.
**Caveat:** measured on one video (and a head-cropped one). An earlier spot-check
showed the effect size is content-dependent. Confirm on a well-framed clip.

### LHF-3 — Scale the frame budget to duration ✅ **DONE 2026-08-29**
`FRAME_BUDGET` absolute ⇒ 44× density spread at one price (§5.2). Make it per-minute
with a hard cap, and when achievable density falls below a floor, say so instead of
returning `Many / Many / All`. The 300s job at 40 credits is the worst case we have
actually shipped. *Shipped as:* `TARGET_FRAMES_PER_SEC = 2.0` clamped to 24…240
frames, with `low_density` flagged rather than the job refused (§2 has the curve).
The trade is purely API spend now that the tool is free — worst case ten model calls
per job instead of four, and *fewer* on short input.

### LHF-4 — Un-wipe `runtime_config` ✅ **DONE 2026-08-29**
Make `_finalize_pipeline_run` (`base.py:130-166`) merge instead of replace (mirror
`dispatch_pipeline.py:199`), and have the frontend render `asl_unverified` /
`review_required`. Three lines, fixes every pipeline, and **restores
`asl_frames_sampled`** — without which LHF-3 cannot be measured in production.

### LHF-5 — Run the offline runner on 1320 ⚠️ **REWRITTEN 2026-08-30 — the original would have produced a fake number**

**As originally written, this item was a trap.** It proposed running the model on
`1320_1000022357_137.2s.mp4` and scoring it against
`ground_truth_candidates/1320_….srt` — a transcript **derived from the English captions
burned into that same video**. The model would have read the captions, matched them
closely, and produced the best score in the corpus. It was the highest-priority item on
this list.

**What changed.** `videos/1320_1000022357_137.2s.mp4` is now a *masked* render: the caption
band is blacked out on every frame, and the title/instruction cards are blacked out
entirely (they leak both the topic — `CATEGORY: RELIGIOUS` — and the exercise
instructions). The unmasked source moved to `ground_truth_candidates/…_burned.mp4`, beside
the reference it produced. `asl-eval/run_current_model.py` now refuses a contaminated input
unless explicitly overridden, and records `input_md5` so a prediction can always be traced
to the file it actually read.

Masking *only* the captioned frames was tried first, to preserve signing in caption-free
stretches, and rejected: it left 14 holes totalling ~22 seconds where captions were still
visible, and a sampled OCR sweep of the result reported it clean. Unconditional masking has
no intervals to get wrong. Its measured cost is **8 frames — 0.3 seconds out of 137** —
where the signer's hands are in the band during active signing.

**§9.5 is settled.** The production-direction question ("ASL rendition later captioned, or
English source interpreted?") is answered by the title cards themselves: *"Certificate
Program for Sign Language Interpreters — RECEPTIVE SKILLS EVALUATION"*, *"SIGN TO VOICE"*,
*"Record yourself voicing the video"*. It is an interpreter certification exercise, so the
**ASL is the source and the captions are the answer key** — which is the direction that
makes them usable as gold. What remains is an annotator confirming the caption text against
the actual signing before the candidate is promoted.

**The run is still worth doing**, and it is still the only well-framed, face-visible,
long-form clip we hold. It is just no longer free of judgement: it needs the masked input,
and the reference needs verifying first.

```
python3 asl-translator/asl-eval/run_current_model.py \
  --video asl-translator/data/asl_corpus/videos/1320_1000022357_137.2s.mp4 \
  --config production_2026_08_29 --run --acknowledge-private-data-upload \
  --output asl-translator/data/asl_corpus/predictions_eval/1320_..._production.json
```

### P0-2 — Tell the prompt to ignore on-screen text ⚠️ **OPEN — live user-facing**
Scorecard P0-5, and §10.5's last bullet promoted to an item because it is the only
thing on this list that is actively producing wrong output for real users. `_PROMPT`
says nothing about burned-in text, so a user who uploads an already-captioned video
gets those captions OCR'd back as a "translation" — fluent, correctly timed, and
labelled as ASL recognition. **This is exactly the §1.0 failure mode, still shipping in
the free live tool**, and it silently inflates any quality statistic gathered from real
traffic. Cost: a prompt edit and a test. There is no argument for leaving it.

### P0-3 — Run the text-memorisation control ⚠️ **OPEN — should have preceded §11**
Scorecard P0-2, which was written to *gate* the benchmark run and was then skipped.
How2Sign's English translations are public and widely mirrored, so the model may have
memorised them; prompt it with a `SENTENCE_NAME` and **no video** and see whether it
completes the reference. **This does not threaten §11's numbers** — memorisation
inflates scores, and §11 is a floor-level failure, so a contaminated model would have
scored *better*, not worse. It gates the next number, not this one: the first time an
ablation or a new model produces a *good* result on How2Sign, this control is the only
thing standing between that result and a second §1.0. Run it before, not after.

### P0-4 — Run native video input on the frozen benchmark 🟡 **PARTIALLY DONE 2026-09-11 — gate inconclusive**

> **Status after §14.1.** **Step 1 ✅** — native video is a real config with a resumable,
> dry-run-default harness, no longer §13.5's scratch script. **Step 2 is 5/12** — and the 5
> scored clips show **0 semantic-adequacy flips and 0 topic-mismatch flips**, the same
> failure class as the frame baseline. The other 7 failed in the Gemini Files API *before
> inference*, twice, on the same IDs. **Neither the promotion nor the rejection criterion
> below can be asserted from 5/12**, so **step 3 (all 128) must not start.** ⚠️ The
> length-insensitive-metric warning at the bottom of this item earned itself: both clips
> whose WER improved did so by exchanging one hallucination for another. Everything below is
> the original 09-10 write-up, kept for the pre-registration record.

**Why this is now the highest-value item on the board.** §13 is the first result in
this workstream where the model recovered *meaning* — 2 of 7 items semantically
correct, and the numbered-list structure of the exercise recovered intact, against a
same-model frame control that produced incoherent output. Every temporal intervention
in §12 returned 0/12 clips with correct meaning; the 40-clip review returned 0/40
adequate. **One clip is not evidence, but it is the only positive signal this project
has ever produced, and it is cheap to convert into a real one.**

**Why it is cheap.** Native video is **one call per clip** against the frame
pipeline's 4–7. The full 128 is roughly **128 calls against Baseline A's 383** — *less*
than the 8 fps arm that exhausted the monthly cap (LHF-9). This is the rare item where
the better experiment is also the cheaper one.

**Why it produces a quotable number and §13 does not.** §13's reference is Curify's own
circular outreach translation (`usable_for_official_metrics: false`). The frozen
How2Sign-128 references are independent and checksummed. Running there converts a
diagnostic into a measurement.

**Do it in this order:**

1. **Land it as a real config**, not a scratch script — `run_current_model.py` gains a
   native-video path and a `evaluation_2026_09_10_gemini_3_6_native_video` entry, so it
   is resumable, covered by the test suite, and reportable like every other arm. §13.5
   records that the current script is none of these.
2. **The 12 diagnostic clips first** (§12.1) — 12 calls, minutes, and directly
   comparable to all three §12 arms on the same clips.
3. **Then all 128**, only if step 2 clears the bar below.

**Pre-registered promotion criterion** (set above the §12.2 noise floor, and above what
every prior arm achieved — which was zero):

> On the 12 diagnostic clips: **≥ 3 of 12 move from `semantic_adequacy = 0` to ≥ 1**,
> **or** `reference_topic_mismatch` flips yes → no on **≥ 3 of 12**. Zero clips flipped
> either in any §12 arm, so any flip at all is new information.

**Pre-registered rejection criterion:** 0/12 flip category and the WER movement sits
inside the pooled noise floor → native video is not the answer either; record it and
stop, do not scale to 128.

⚠️ **Report CER, chrF and prediction/reference length ratio alongside WER** — §12.5's
finding. Native video's §13 output was *shorter* than the frame arm's (42 vs 47 words),
and on this corpus shorter output lowers WER on its own. Without a length-insensitive
metric this experiment can repeat exactly the mistake §12.2 arm C made.

⚠️ **Fingerspelling is not expected to improve** (§13.4) — Greg/Sara failed under native
video too. Do not let a structural win be reported as a fingerspelling fix.

### P0-5 — `thinking_level: "medium"` is rejected by the SDK and silently ignored ⛔ **NEW 2026-09-10**

`ThinkingLevel` in google-genai 1.55.0 is `THINKING_LEVEL_UNSPECIFIED | LOW | HIGH`.
`"medium"` triggers `UserWarning: medium is not a valid ThinkingLevel` and is dropped —
confirmed live, firing on the `evaluation_2026_09_04_gemini_3_6` config itself (§13.6).
That config's comment claims the level is *"pinned explicitly for reproducibility."*

**Every §11 and §12 number therefore carries a provenance claim that may be false.** The
numbers themselves are unaffected in relative terms (all arms share the config), but
"we pinned the thinking level" is not something this repo can currently assert.

Fix: verify against the SDK version the benchmark machine ran, then either pin a valid
level or delete the claim — and **make an unrecognised config value fail the run instead
of warning**. A reproducibility knob that no-ops silently is worse than no knob.

⚠️ **2026-09-11 — a third change record now depends on this.** The native-video config
`native_video_2026_09_10_gemini_3_6` sets `thinking_level=medium` too (§14.1), so §14's
provenance claim is as unverified as §11's and §12's. Still unfixed.

### P0-6 — Find out why Uni-Sign fails on this benchmark 🟡 **HALF-ANSWERED 2026-09-19 — still the cheapest item on the board**

> **Updated diagnosis, 2026-10-16:** P0-12 controlled CUDA inference is complete
> (T4/fp16). Timing/crop/normalization jointly recover 85.7% of the matched-runtime
> gap; swapping the pose extractor adds only 0.52 BLEU-4. Failure taxonomy and three
> inference-time interventions have also been run; none validates a general fix.
> See §18. Do not treat the historical “unrun” queue below as current.

> **2026-09-19 (§15.3):** one mechanism is now known and it is not the one this item is
> after. Above 256 frames Uni-Sign discards the excess **at random**, with a global RNG
> seeded once at model load — 59 % of a 25.8 s clip, 89 % of a 77.5 s one — and
> `max_new_tokens=100` is the same for every input length. That explains the long-clip
> collapse and makes any long-clip Uni-Sign number one draw rather than a measurement.
> **It does not explain the matched-126 result**, where the median clip is 5.15 s and 77 %
> sit under the cap and are processed whole and deterministically. The failure-shape
> analysis below is unchanged, unrun, and still needs no new inference.

§14.6 leaves one hypothesis standing: ASL needs a sign-specific learned temporal
representation rather than better-formatted input to a generic model. **Uni-Sign is the
closest thing we have to a test of it, and it argues the other way** — it is a learned model
built on RTMPose keypoints, it consumes exactly the pose signal §14.2 says a generic model
cannot use, and it still scores **WER 0.9819 / BLEU 5.39** on the frozen 128.

**Why it is first.** It needs **no Gemini spend, no new dependency and no new run** — the
128 Uni-Sign predictions, the frozen references and the inspector are all on disk. It is the
one analysis that can either strengthen the §14.6 hypothesis or kill it *before* anyone
prices a training commitment against it.

**What to look for:** whether Uni-Sign's failure has the same shape as ours (deletion-heavy,
topic-mismatched) or a different one; whether its BLEU 5.39 concentrates in a minority of
clips that are actually translated, or spreads thinly as partial credit across all 128;
whether the clips it does best on are the clips we do best on. Its higher BLEU and chrF
(§11.3) mean it is doing *something* we are not — name it.

⚠️ Not a licence to conclude "pose tracking is fine" from D1's 5 clips (§14.2).

### P0-7 — Get written ToS clearance from Sign-Speak ⛔ **NEW 2026-09-11 — gates C entirely**

SignCaption is the only available read on what a purpose-built commercial ASL system does on
our benchmark, and §14.3 establishes that **nothing technical can advance it**: no
credentials, endpoint, schema, auth, pricing or rate limits exist anywhere, prior outreach
was never answered, and the public Customer ToS bars using the service "to create a
competitive product" — which ours arguably is.

**Order, and it is not negotiable:** written clearance on the competitive-product clause →
benchmark-use permission → any technical evaluation. ⚠️ And when it does happen, it runs on
**public benchmark clips only**: the same ToS licenses uploaded video back to Sign-Speak
perpetually for model training, and §5's corpus is real users' identifiable video.

### P0-8 — Clear the Uni-Sign checkpoint licence ✅ **CLEARED 2026-09-21 — one obligation, one exclusion, two loose ends**

**Reply received 2026-09-21** from Zecheng Li (`lizecheng19@gmail.com`), first author, answering
the 09-20 request recorded below. Read by hand out of Jay's inbox ([[imap-gate-lifted]]); there
is **no path on disk for it**, which is itself a problem — archive the raw message, it is
currently the only artifact the grant exists on (**LHF-12**). The operative sentences, verbatim:

> "On the checkpoint, I don't have extra authorization requirements on our side: you're welcome
> to use and redistribute the Uni-Sign weights, including commercially."
>
> "How2Sign itself is a third-party dataset under CC BY-NC 4.0, so I can't re-license that; if
> you later want to redistribute the dataset, please check with us first."
>
> "If you deploy this, a short credit linking back to the Uni-Sign GitHub would be appreciated —
> something like 'inspired by' or 'powered by' is more than enough."
>
> "The missing LICENSE on the code repo was an oversight; I intend it to be MIT and will add a
> LICENSE file to make that explicit."

**Against the three layers this item was tracking:**

| Layer | Was | Now |
|---|---|---|
| Checkpoint `how2sign_pose_only_slt.pth` | CC BY-NC-4.0 — blocking | ✅ **Granted** for commercial use *and* redistribution, direct from the author |
| Uni-Sign **code** repo | No LICENSE at all — blocking | 🟡 **MIT intended**, stated in writing; the file does not exist yet — GitHub API, 2026-09-21: no LICENSE in the repo root, last push 2026-02-11 |
| How2Sign training data | CC BY-NC 4.0 | ⛔ **Unchanged, and explicitly out of scope** — they cannot re-license it and say so plainly |

**One obligation, and it is cheap:** a visible credit linking to
`https://github.com/ZechengLi19/Uni-Sign` wherever Uni-Sign output reaches a user. Folded into
**LHF-10** as a build item so it cannot be discovered at ship time.

**One exclusion that touches live work:** How2Sign redistribution still needs a separate ask.
It does **not** block **P0-9** — concatenating How2Sign clips into segment-level gold for our
own evaluation is *use*, not redistribution — but the frozen 128-clip benchmark and anything
derived from it stay in the private repo. ⚠️ Do not publish them, and do not attach clips to
the LHF-11 reply.

**Two loose ends → LHF-12.** The published artifacts still say the opposite of the email: the
HF model card reads `license: cc-by-nc-4.0` (`lastModified` 2026-05-22) and the code repo ships
no LICENSE. A deployment resting on a private email while the artifact reads **NC** is a weaker
position than it needs to be, and the author has already volunteered half the fix.

⚠️ **This clears permission, not the case for deploying.** §15.2 — complete degeneration on
both real Curify user videos — is untouched by anything above, and §15.4 found no quality gain
from the segmentation that would make long clips tractable. **P0-8 moves Uni-Sign from "cannot"
to "may". Nothing yet moves it to "should".**

**What was blocking, kept as the record:**

`how2sign_pose_only_slt.pth` is **CC BY-NC-4.0**: non-commercial only. Curify's products are
commercial. Separately, the upstream Uni-Sign **code** repository ships **no LICENSE file at
all** at the pinned commit `eed438bc…`, so there is no explicit grant even to redistribute the
vendored source, let alone bake it into an image in `curifyregistry.azurecr.io`.

**Nothing technical is pending.** §15.1 established that the service works: strict checkpoint
load, `/readyz` 200, real translations. What is pending is permission, and it blocks the ACR
push, any Azure or GCP hosting, and the merge of PR #448 — whose own test plan already says
*do not merge*. The runtime gate (`UNISIGN_NC_CHECKPOINT_LICENSE_ACK=1`, mirroring
`xtts_server`'s `COQUI_TTS_LICENSE_ACCEPTED`) is correct design and **is not permission**.

**Order, and it is not negotiable:** written clearance on both the checkpoint licence and the
missing code licence → then, and only then, a hosting decision. ⚠️ And when that decision
comes, note §15.5's fourth blocker: `curify-xtts-v2` and `curify-whisperX` are both **Stopped**
and production points at GCP VMs, so "deploy it like xtts" means the VM, not App Service.

Until it clears, Uni-Sign stays what it is today: a **local R&D service** for offline
evaluation, which is a legitimate use and needs no sign-off.


#### The "make it free" question — asked and answered 2026-09-20 *(moot 2026-09-21 — the grant is unconditional on pricing; kept because the three-layer table is how to read the next model licence)*

**Going free does not clear this, and the tool has been free the whole time.** P0-1 set
`JOB_CREDIT_COST["ASL_TRANSLATION"] = 0` on 2026-08-29 and the frontend `ratePerMinute`
with it, tripwired in `pricing.test.ts`. So "make it free" is not a change available to us
— it is the status quo, and it has never been what unblocks this.

On the terms themselves (not legal advice; the call is counsel's): **CC's NonCommercial
clause turns on purpose, not price** — "not primarily intended for or directed towards
commercial advantage or monetary compensation." A free tool on a commercial platform,
alongside the paid tools, feeding the paid translate → subtitle → mux machinery, and
serving acquisition and retention, is a hard thing to argue is non-commercial. Free is
evidence, not a safe harbour. And pricing only touches one of three layers:

| Layer | Terms | Does going free help? |
|---|---|---|
| Checkpoint `how2sign_pose_only_slt.pth` | CC BY-NC-4.0 | Narrows it; does not settle it |
| Uni-Sign **code** repo | **No LICENSE at all** | **No.** No licence = no grant. We clone, patch and redistribute it regardless of what users pay |
| How2Sign training data | CC BY-NC 4.0 (`9.30/asl-data/HOW2SIGN_MINI_BENCHMARK.md:212`) | **No** — and it closes the "just retrain it ourselves" escape |

The middle row survives every pricing argument, and the third means a permissive
re-training path needs permissive *data*, which How2Sign is not.

#### ⚠️ Pushing a checkpoint-baked image to ACR is the blocked act, not a way round it

> **2026-09-21 — the licence half of this is gone.** Redistribution is granted, so baking the
> checkpoint into an image is no longer a permission breach. **The four build-path reasons below
> stand entirely on their own** and still point at the same shape: image built by CI, weights out
> of the image, mounted on the VM (§16.4).

Proposed 2026-09-20: have the engineer who holds the checkpoint locally bake it into the
image, push to ACR, and let the deploy pull without rebuilding. **Mechanically it works and
it does dissolve the volume-mount problem — which is exactly what makes it the wrong
trade.** Baking the weights in and pushing **is** the redistribution step: it converts "one
engineer mounted an NC file locally for research" into "a copy of an NC-licensed artifact
lives in the company's production registry, pulled by production infra." The Dockerfile
declines to bake it in *on purpose*, in a comment. A locally-built image reverses that
decision silently.

Four further reasons it is the wrong build path **even after clearance**:
1. **Provenance.** CI builds from a pinned Dockerfile at a known SHA; a laptop image is
   unreproducible from its tag. §15.1's audit had to compare the image's build timestamp
   against the Dockerfile's last edit to convince itself they matched — that is the failure
   mode, already observed once.
2. **Architecture.** Apple Silicon needs `--platform linux/amd64`, emulated and slow; an
   accidental arm64 push will not start on x86 at all.
3. **Size.** Already multi-GB (torch CPU, deepspeed, onnxruntime, opencv, vendored repo);
   +1.19 GB checkpoint, +~2.2 GB more if mT5 is baked. App Service cold-pulls the whole
   image on every recycle.
4. **Credentials.** ACR push credentials end up on a personal laptop.

**The shape to use if P0-8 clears:** image built by CI like every other service, **weights
out of the image**. On the GCP VM — which is what xtts actually uses (§15.5) — the
checkpoint is copied to the VM once and mounted read-only with `docker run -v`, so the
weights never enter the registry at all. If App Service is genuinely required instead, it
is Azure Files BYO-storage plus the P1v3 / 230 s constraints in §15.5.

#### Action taken — licence request sent 2026-09-20

Sent to **`lizecheng19@gmail.com`**, the contact address in Uni-Sign's own README (first
author, Zecheng Li, USTC). Bilingual EN/中文, from `Jay @ Curify`, as a plain one-shot —
deliberately **not** through `send_annotated_emails.send_email`, which appends an
unsubscribe footer and `List-Unsubscribe` headers to everything and would have framed a
licensing request as bulk marketing. Not recorded in the outreach ledger; this is not
outreach. Script: `curify-gtm/gtm_tools/send_unisign_license_request_2026_09_20.py`
(dry-run by default, `--send` to deliver). Delivered 2026-09-20, Message-ID
`<178986621303.87952.3059592973119869558@curify-ai.com>`, from `team@curify-ai.com`.

It asks three things, in this order:

1. **Permission for the checkpoint** under CC BY-NC-4.0, stating plainly that Curify is a
   commercial company even though the ASL tool is free to users — and volunteering the
   How2Sign layer, because a grant they cannot actually give is worse to us than a no.
2. **A LICENSE file on the code repo** (MIT or Apache-2.0 both work), or a statement of the
   terms they intend for use, modification and redistribution.
3. Nothing else. It states that we have only run it locally for offline evaluation, have
   deployed nothing, and **will not deploy until they reply** — which is true and is the
   only commitment in the message.

It offers our frozen-128 How2Sign results and the §15.3 256-frame finding back to them,
unconditionally. Reply goes to Jay's inbox and is read by hand ([[imap-gate-lifted]]);
**no automated follow-up is scheduled and none should be.**

⚠️ **If they decline, or do not reply, the answer is no by default** — silence is not a
grant. In that case Uni-Sign stays what it is today: a local R&D service for offline
evaluation, which is legitimate, needs no sign-off, and is where it sits right now.

### P0-9 — Build segment-level gold from concatenated How2Sign clips ⛔ **NEW 2026-09-19 — unblocks the whole long-video question**

Both long-clip results in §15 are unscoreable for the same reason: a single 78-word reference
for a 25.8 s clip, with no temporal alignment and no per-segment references. WER against it
mostly measures output length — which is exactly how §15.4 produced "WER worse, chrF better,
conclusion neither".

**The fix is cheap and needs no annotation.** How2Sign IDs (`FzmL8SL6Bow_1-8`) are already
sentence-level clips cut from longer videos. Concatenating consecutive clips from one source
video manufactures long test videos with **known per-sentence references and known true
boundaries** — which makes three things measurable at once that are currently not: whether
segmentation beats whole-video input, whether the motion detector's boundaries land where the
real sentence boundaries are, and whether Uni-Sign's per-segment output is right when scored
against the right sentence.

⚠️ **Use clips outside the frozen 128.** Building these out of benchmark clips would
contaminate the benchmark. Also carry §15.3 forward: at 24 fps, keep concatenated segments
under `min(8 s, 256/fps)` or the random-subsample path fires and the comparison is against a
moving target.

### LHF-10 — The time-segmentation shim, if Uni-Sign is ever wired in ⏸ **NEW 2026-09-19 — ~~blocked behind P0-8~~ unblocked 2026-09-21; now gated on evidence, not permission**

**Not a detail after the integration — it *is* the integration.** Production consumes
`AslSegment(start, end, text)` and builds an SRT from it. Uni-Sign returns **one untimed
string**; its `segments[0]` is wrapper metadata (`start` 0.0, `end` = clip duration,
`source: "wrapper_derived"`), and the service says so in its own response. Everything else —
provider switch, HTTP call, retries — already exists.

Cheapest first, and each is independently useful:

1. **Short clips need no segmentation at all.** Under 256 frames (**~10.7 s at 24 fps**)
   Uni-Sign does not subsample and is bit-identical across runs (§15.3). A v1 restricted to
   short clips is honest, deterministic and needs zero new logic — one wrapper-derived segment
   spanning the clip, which is what the service already returns.
2. **Seed the RNG per request.** One line in the service before inference. It does not stop
   frames being dropped, but it makes long-clip output reproducible, which is the difference
   between a bug and a known limitation — and every §11/§15 long-clip number depends on it.
3. **Reuse our own motion detector for boundaries.** `_probe_motion` / `_segment_runs` in
   `asl_utils.py` are already in production and were verified **identical in executable code**
   to the research copy (§15.4). Segment boundaries then *become* the timestamps — which is no
   worse a provenance story than today's, where the timestamps are whatever Gemini claims in
   its JSON.
4. **Cap by frames, not seconds:** `min(8 s, 256/fps)`. 8 s is 192 frames at 24 fps and 480 at
   60 — a duration-only rule silently re-enters the subsampling path on high-fps phone video,
   which is exactly what users upload.
5. **Drop or merge idle-only segments** instead of translating them. A ~3.5 s idle tail was
   turned into a confident sentence (§15.4).
6. **Send the upload as `video/mp4`.** The service's allowlist is strict; an unlabeled part
   arrives as `application/octet-stream` and gets a 415.
7. **Ship the credit line.** ⚠️ **NEW 2026-09-21 — this one is a licence condition, not a
   nicety.** The grant in P0-8 asks for a short credit linking to
   `https://github.com/ZechengLi19/Uni-Sign` ("powered by" is explicitly enough) wherever the
   output reaches a user. That means the ASL result surface, not just a source comment —
   `AslUnverifiedNotice.tsx` is already the one component rendering ASL-specific chrome and is
   the obvious home. Free to build, awkward to retrofit after launch.

⚠️ **What this does and does not buy.** Items 1–7 fix *mechanics* and one licence obligation — determinism, frame
coverage, a valid SRT. **None of them is evidence that the translation gets better**: §15.4
tested exactly this shape and found no quality gain, and §15.2's user-video degeneration is
untouched by any of it. Do not let a working shim become the argument for shipping.

### LHF-11 — Send Uni-Sign the measurements we promised ⛔ **NEW 2026-09-21 — owed, not optional**

The 09-20 request offered our frozen-128 results and the §15.3 256-frame finding
unconditionally, and the reply asks for them by name: *"I'd also be glad to see the measurements
you mentioned, especially the 256-frame sampling behavior."* The grant arrived **before** we
paid that, which makes it a debt rather than a bargaining chip. Do it promptly.

**What to send — all of it already written:**
- **§15.3 in full.** Above 256 frames the excess is discarded at random by a global RNG that is
  never seeded per request, so identical long clips return different translations. This is a
  **bug report they can act on**, and the one-line fix is LHF-10 item 2. Cite the code path,
  not our prose about it.
- **The matched-126 scorecard** (Uni-Sign BLEU 5.40 / chrF 22.83, §15.2 / 9.15 reports) and the
  real-user-video degeneration — carrying its caveat, that it is n=2 with no scoreable
  reference, exactly as this document carries it.
- **The §15.1 load result** — strict load, zero missing and zero unexpected keys, sha256 an
  exact match on 1,186,925,007 bytes. That is a clean third-party reproduction of their release
  and worth them having.

⚠️ **Send findings and numbers, never data.** No How2Sign clips (P0-8's exclusion), no user
video (§5 is unconsented personal data), no private-repo links. Plain prose, from Jay, same
one-shot path as the request — **not** `send_annotated_emails.send_email`, which would append an
unsubscribe footer to a research reply. [[outreach-copy-in-jays-voice]]: Jay writes the final
text.

### LHF-12 — Get the grant onto the artifacts, not just into an inbox ⛔ **NEW 2026-09-21 — one email closes the last gap in P0-8**

As of 2026-09-21 the published artifacts still say the opposite of the email:

| Artifact | What it still says | How checked |
|---|---|---|
| `huggingface.co/ZechengLi19/Uni-Sign` | `license: cc-by-nc-4.0` | HF API, `lastModified` 2026-05-22 |
| `github.com/ZechengLi19/Uni-Sign` | no LICENSE file in the repo root | GitHub API, last push 2026-02-11 |

Neither is a surprise or bad faith — they volunteered the LICENSE fix themselves. But an internal
deployment resting on a private message while the public artifact reads **NC** is a weaker
position than it needs to be, and closing it costs one email. Two asks: the MIT LICENSE file they
already intend, and a line on the model card that the weights may be used commercially.

**Three things to do on our side regardless of their reply:**
1. **Archive the raw email** (`.eml`, headers intact) somewhere durable and findable. It is
   presently the sole artifact the grant exists on, and it lives in exactly one inbox.
2. **Re-pin when the LICENSE lands.** The Dockerfile vendors upstream at `eed438bc…`; a LICENSE
   added later does **not** retroactively appear at that commit. Either re-pin to a commit that
   contains it, or record the licensed commit explicitly next to the pin.
3. **Leave the runtime gate in place.** `UNISIGN_NC_CHECKPOINT_LICENSE_ACK=1` should stay, with
   its comment updated to point at §16 — it now documents a *granted* licence rather than
   guarding an ungranted one, which is the same thing `xtts_server` does with
   `COQUI_TTS_LICENSE_ACCEPTED`.

### LHF-6 — Annotate 1477 and 1474 (≈18 seconds of video, total)
Items 1 and 2 of `annotation_queue.csv`. Both already have baseline0 predictions, so
each annotation immediately produces a scored case. 1477 is 6.7s at 640×480 and is the
only item that isolates **low resolution** from sampling density. The
`asl-ground-truth-annotator/` browser tool exists and is offline-only. This takes n=2
verified cases to n=4 in about an hour.
Then item 4: annotating **1466 once scores both 1466 and 1467** against the same
reference — and finally answers whether either of those two charged jobs was closer to
the truth.

### LHF-7 — Make fingerspelling fail loudly instead of silently
0/2 on our only test, temperature-independent, and it produced a *plausible wrong
name* ("H.G.Q." for Greg) rather than an admission. Actually recognising fingerspelling
is not low-hanging (it wants a hand-ROI crop at much higher fps). Making it *visible*
is: instruct the prompt to emit `[fingerspelled: ?]` for letter-by-letter stretches it
cannot resolve, rather than a guessed proper noun. Converts a silent error into a
flagged one for roughly the cost of a prompt edit.

### LHF-8 — Give each batch the previous batch's tail as context ⬇️ **PROBED 09-09, negative on semantics — downgraded, not closed**
Fixes LHF-1's duplicates at source rather than after the fact, and adds narrative
continuity across the 4+ independent calls that currently never see each other. More
work than LHF-1 and it should not replace it — do the dedup first, this second.

**Why it moved up.** §11.4 measured the failure as deletion/coverage: 41% of the
reference word count emitted, 61% of edit operations deletions, temporal recall 0.58
against precision 0.99. Stateless batches that never see each other are a plausible
mechanism for exactly that — a batch with no narrative context has no reason to
continue a sentence it did not start, and "omit stretches with no signing" is a cheap
out. ~~**If LHF-9 comes back negative** (density is not the cause), this becomes the
leading hypothesis and the next thing to build.~~

⚠️ **Probed on 09-07 and it did not work (§12.2, arm C).** Overlapping 24-frame windows
at stride 12 — i.e. every window sees the previous window's second half — moved corpus
WER 1.0524 → 0.9545 on the 12 diagnostic clips, and **that movement is not quality**:
chrF2 went *down* (14.30 → 13.54), output length fell to 46% of reference, all 12 clips
stayed topic-mismatched, and the architecturally-inert clips in the same run move by
−0.0673 on decoding noise alone.

**Downgraded from "leading hypothesis," not closed.** The probe is *overlapping windows
with a deterministic frame-ownership merge*, which is not identical to LHF-8 as written
(carrying the previous batch's **decoded text tail** into the next prompt). That variant
is still untested and remains cheap. But it is no longer the obvious next build — after
three negative temporal arms, §12.7's untested axes (native video, hand-crop
dual-stream, under-generation) rank above it.

### LHF-9 — Finish the 8 fps temporal ablation — 52 clips ⛔ **BLOCKED on billing, not code**
Experiment B is implemented, unit-tested, smoke-tested and 76/128 run (§11.6). The
remaining 52 clips return `429 RESOURCE_EXHAUSTED` — the Gemini project's **monthly
spending cap**, re-confirmed by a resume attempt, not a transient rate limit. The 76
completed predictions are on disk and the runner skips them, so **the remaining cost is
52 clips, not 128.** Raise or reset the cap
(<https://ai.google.dev/gemini-api/docs/billing#project-spend-caps>), then:

```
python3 asl-translator/evaluation/run_curify_how2sign_v2_benchmark.py \
    --config evaluation_2026_09_06_gemini_3_6_8fps \
    --results-dir asl-translator/evaluation/results/how2sign_v2/curify_gemini_3_6_2026_09_06_8fps
```

Then aggregate ALL-128 / MATCHED-126 and produce the A/B report. **Do not report a
partial-corpus comparison** — 76 clips against Baseline A's 128 is not an ablation
result, it is a subset with an unknown selection bias.

📌 **Two things learned from the 76 that change how to read the finish (§12.2).**
(1) The `MIN_FRAME_BUDGET=24` floor means realised density rose only **1.85× median**
(6.36 → 9.69 f/s), not 4× — this is a weaker density test than its write-up claims, which
makes finishing it *more* worthwhile, not less. (2) **17 of the 76 clips got byte-identical
frame counts**, so they are a free decoding-noise control (mean delta −0.0093, mean
|delta| 0.0289, 14/17 unchanged) — pool them with the arm-C control before setting any
promotion bar on the remaining 52.

### Deliberately NOT low-hanging
- **The OpenPose re-test of TGCN-WLASL.** Appendix C rules it out by name: it settles
  *isolated sign recognition*, which is not the product. Even at a generous 60%
  per-sign accuracy, an 8-sign sentence is ~1.7% fully correct.
- **Chasing the SignCaption gap.** Neither side is ground truth (§1.3); the comparison
  cannot say who is right, so there is nothing to optimize against.
- **Auditing the broader production video pool.** Worth doing before expanding the
  corpus with more "ASL-labeled" production videos, but it needs authorized,
  metadata-only, read-only production DB access that does not exist today.

---

## 8. What would reopen the model question

* A released SLT checkpoint materially above **~25 BLEU** on open-domain ASL, **or**
  ⚠️ *this bar is what the migration question is scored against: the best open checkpoint we
  have actually run, Uni-Sign, sits at **5.40 BLEU** on matched-126 — ~5× short of it, and it
  degenerates on real user video (§16.5).*
* A demand signal with budget — school, NGO, or publisher with batch volume. The
  honest offer there is **human-verified transcription with AI assist**: a services
  motion, not a model.

### 8.1 DeepMind SL2T and SignGemma — checked 2026-08-30

**SL2T is not available to us, and is not a checkpoint.** DeepMind's
[*Putting sign language AI into users' hands*](https://deepmind.google/blog/putting-sign-language-ai-into-users-hands/)
describes a massively multilingual sign-language-to-text model trained on **100,000+ hours
across 50+ sign languages** (~25% ASL), shipping **inside Gboard and Live Transcribe on
Pixel 11**. No weights, no API, no SDK, no dataset. Its input is **MediaPipe Holistic pose
landmarks** — the same approach class Appendix C ruled out for us at 0/12. The difference is
the training data, not the idea, so this is not a gap we can close.

**SignGemma is the thing to watch, and it has not shipped.** Announced May 2025 as an *open*
Gemma-family sign-language model, "coming later this year". As of the most recent post on
Google's own developer forum (**2026-08-17**): no weights, no API, no preview, no timeline.
Trade-press reports of a TF Lite package and hosted API are not corroborated there or by any
Hugging Face release. **The reopening criterion above is not met** — but it now has a
concrete name to watch rather than a generic one.

⚠️ **Do not compare SL2T's 70 BLEURT to the 12.39 BLEU ceiling.** Different metrics,
different scales; the two numbers sitting near each other invite exactly that error. SL2T's
figures (70 BLEURT zero-shot on FLEURS-ASL, 74 one-handed, 85 on PRESTO-ASL) are
vendor-reported with no independent evaluation.

**What is worth copying is their product posture.** With a vastly better model, DeepMind
shipped a *failure map on day one*: the AISLAC joint impact report bars SL2T from **medical
consultations, legal proceedings, police interactions, classroom instruction, job
interviews, and benefits determinations**, and names its error modes — rapid fingerspelling
("prey" read as "grey"), passive constructions, dropped classifier detail, tense without
context. It also notes MediaPipe Holistic does not track the tongue, a real ASL articulator.

Two things follow for us. **The state of the art, productized, still ships with abstention
by scope** — which is external validation for the reframe below rather than a reason to
wait. And **fingerspelling fails even at 100,000 hours**, so LHF-7 is right to make ours
fail *loudly* rather than try to fix it.

**The reframe if it is ever revisited: verifiability, not accuracy.**

| Use case | Who checks the output | Error cost | Viable today |
|---|---|---|---|
| Translation for deaf viewers | nobody — errors are invisible | high, borne by the person it was made for | **no** |
| Learning / practice ("is my sign right?") | the learner, who knows the target | low — mismatch is obvious | **yes** |
| Fingerspelling | narrow closed alphabet | low | **no today** — 0/2, see LHF-7 |

Same model, opposite verdict, purely because the user can verify. The current corpus
is consistent with the learner shape: short self-recorded clips (6.7s webcam, 11.5s
phone) from users who know what they signed.

---

## 9. Change record — 2026-08-29

Everything that shipped, where it lives, how it was verified, and what it left open.
Three repos moved together; the pricing and the recogniser changes are independent
of each other and were committed separately because their blast radii differ.

### 9.1 What changed

| # | Change | Where |
|---|---|---|
| 1 | `runtime_config` merges on finalize instead of replacing | `app/pipelines/base.py` — **affects every video job type**, not just ASL |
| 2 | Adjacent duplicate captions merged | `asl_utils._merge_adjacent_duplicates`, called after the sort in `transcribe_asl` |
| 3 | `temperature=0` pinned | `asl_utils.ASL_TEMPERATURE`, both the Gemini and OpenAI call paths |
| 4 | Frame budget derived from duration; density floor; degeneracy signal | `asl_utils` constants + `AslResult` fields, persisted by `asl_pipeline` |
| 5 | Price → 0, plus a zero guard on the charge path | `subscription_constants.py`, `crud/credits.py`, `pipelines/errors.py` |
| 6 | Rate → 0 in the UI, with a tripwire test | `create-job-ui.ts`, `lib/__tests__/pricing.test.ts` |
| 7 | The unverified notice reaches the user | `AslUnverifiedNotice.tsx`, `CalloutBox` lifted to `_components`, `types/segments.ts` |
| 8 | Tool copy corrected in all 10 locales | `messages/*/home.json`, `messages/*/common.json`, two `scripts/*_i18n.py` |
| 9 | Offline runner mirrored + parity test | `visual-search-adhoc:asl-translator/asl-eval/` |

**Commits.** curify-studio `jwang/asl-free-and-honest`: `95b40f10` (runtime_config),
`f42a3a44` (recogniser), `d75715c1` (pricing), `705c8ae2` + `e23b2b94` (docs).
curify-frontend `jwang/asl-free-and-honest`: `482ae3d3` (free + notice), `8db1c8f0`
(copy). visual-search-adhoc: `6131783`, merged to `main` as `49bdab0`.

### 9.2 How it was verified

- ~~**The dedup claim was measured, not asserted.**~~ **RETRACTED 2026-08-30 (§1.0).**
  It *was* measured — carefully, with zero API calls, against a saved prediction and a
  human-verified SRT. The measurement was still worthless, because the video the
  prediction came from had the SRT burned into its frames. **Rigour downstream of a
  contaminated input produces a confident wrong answer**, which is the lesson worth
  keeping from this bullet. 1252 remains unchanged by dedup, as predicted, because it has
  no adjacent duplicates.
- **The degeneracy detector** fires on all three ~190s predictions and on nothing
  else in the corpus.
- **The budget curve** was checked end-to-end with a dry run on 1320 (no network):
  96 frames / 0.700 f/s / 4 calls → 240 / 1.749 / 10.
- **The parity test fails on drift**, confirmed by deliberately altering a constant,
  not just by observing it pass.
- Backend 116 unit tests, frontend 402, eval harness 71. `tsc --noEmit` clean. No
  i18n key drift in the touched files.

### 9.3 What this did NOT do

It did not make the recogniser better at reading ASL. Fingerspelling is still 0/2
and temperature-independent; 1252 is still WER 0.92; the field ceiling is still
12.39 BLEU against 40–50 for production MT. What shipped makes the tool honest,
reproducible, free, and correct on the narrow content it *can* read.

**No new model run has been made.** Every number in this document still comes from
predictions generated before 2026-08-29 — the 08-29 work re-scored them, it did not
regenerate them. Nothing here reports how the current config actually performs,
because that requires LHF-5.

### 9.4 Open follow-ups this created or uncovered

| Item | Where | Why it was not done |
|---|---|---|
| **`deep.how.p2/p3` describes a model we do not have** — "a vision encoder … sign-aware embeddings", "a translation head … trained on parallel ASL-English video corpora". No such component exists; it is a general VLM over sampled JPEG stills. `why.point2` ("Built for content, not lab demos") is likewise unsupported. | `messages/*/home.json`, all 10 locales | Long-form SEO body copy in ten languages — rewriting it is a content and ranking decision, not a bugfix. The new `faq.a1` contradicts it directly in the place users actually read, which is a stopgap, not the fix. |
| ~~`AslSuspectedError.to_runtime_config()` has **zero callers** — the handler pulls only `failure_code` via `getattr`, so `asl_suggestion` is never persisted and the reroute offer never reaches the frontend~~ | `dispatch_pipeline.py`, `pipelines/errors.py` | ✅ **FIXED 2026-09-09.** Two layers were dropping it, not one: `ProjectStatusResponse` had no field for the payload either. dispatch now merges any error's `to_runtime_config()` generically, the status endpoint serves it gated on FAILED, and `/projects/{id}/retry` re-runs on the stored `video_id` so the switch needs no re-upload. The offer is attached to every no-speech verdict rather than only to a positive detection — `ASL_SUSPECTED` had fired **once** in 90 days, while plain `NO_SPEECH` covered all eleven failures including both users who switched by hand and succeeded (1627 after 59s, 1585 after 10min). |
| The `subtitle_only` free-quota branch is **dead code** — `subtitle_only=True` is never passed anywhere, so "ASL is excluded from the 60 free subtitle minutes" was vacuously true | `crud/credits.py` | Separate bug, found in passing |
| ~~`NO_SPEECH` copy still says "We can't transcribe sign language or silent footage"~~ | `messages/*/common.json` → `magic.errors` | ✅ **FIXED 2026-09-09.** Rewritten in all 10 locales, and it now sits directly above a button offering the ASL tool. Five failure codes the UI had never heard of were added at the same time — the renderer used to fall through to `failure_reason`, the backend's own English log sentence, and show it verbatim to every user whose code it did not recognise. |
| `project_details/[id]` is hard-coded English apart from the new banner | `curify-frontend` | Out of scope; the banner is the page's first `useTranslations` consumer |

### 9.5 Before running LHF-5, settle this ✅ **SETTLED 2026-08-30 — and it was not the real problem**

The question here was the production direction of 1320's captions. **Answered:** OCR of the
video's own title cards reads *"Certificate Program for Sign Language Interpreters —
RECEPTIVE SKILLS EVALUATION"*, *"SIGN TO VOICE"*, *"Record yourself voicing the video"*. It
is an interpreter certification exercise, so the ASL is the source and the captions are the
answer key — the direction that makes them usable as gold.

**But this section was worrying about the wrong risk.** It treated the burned-in captions
purely as a question about *reference quality*, and never asked what they do to the *input*.
They are visible to the model. Scoring 1320 as this document proposed would have measured
OCR and returned the best number in the corpus. See §1.0 and the rewritten LHF-5.

---

## 10. Change record — 2026-08-30 (corpus decontamination)

### 10.1 What was wrong

Two of the thirteen corpus videos had the reference answer burned into the frame the model
was reading, and one of them was the corpus's primary accuracy anchor. Detail in §1.0.

The uncomfortable part is not that it happened but *how long it survived*. The burn-in was
recorded in `VIDEO_TYPE_AUDIT.csv`, the provenance was recorded in `manifest.json`
("Curify's own demo asset, already public at /video/asl-demo-translation.mp4"), and the
prediction's own shape — 0 substitutions, 0 deletions, exact punctuation — was quoted in
three documents as evidence of quality. Every fact needed to catch it was written down.
None of them were connected.

### 10.2 What changed

In `visual-search-adhoc`, branch `jwang/asl-decontaminate-corpus-2026-08-30`:

| # | Change | Where |
|---|---|---|
| 1 | Contaminated files moved out of `videos/` into the ground-truth folders, beside the references they produced | `ground_truth/155_…_burned_marketing.mp4`, `ground_truth_candidates/1320_…_burned.mp4` |
| 2 | Clean raw demo source swapped in for 155 | `videos/155_…mp4`, md5 `d71313d0…` |
| 3 | Masked render built for 1320 — band blacked on every frame, title cards blacked entirely | `videos/1320_…mp4` |
| 4 | `label_in_input` as a first-class field | `manifest.json`, `corpus_inventory.csv`, `VIDEO_TYPE_AUDIT.csv` |
| 5 | 155 moved to `excluded`; 1320 repointed at the masked input | `evaluation_set.json` |
| 6 | Retraction blocks on the 155 predictions and every report quoting them; "unaffected" markers on the ones that still stand | `predictions_eval/`, `docs/daily_report/8.26/`, `BOSS_SUMMARY.md` |
| 7 | `check_leakage.py` — OCR detector, two passes per frame, validated against both known positives | `asl-eval/` |
| 8 | `corpus_guard.py` — refuses leaky inputs and retracted predictions; wired into `evaluate.py`, `status.py`, `run_current_model.py` | `asl-eval/` |
| 9 | `input_md5` recorded in `run_metadata` | `asl-eval/run_current_model.py` |
| 10 | Pre-existing CSV quoting bug fixed (an unquoted comma in 1457's row made it ragged) | `VIDEO_TYPE_AUDIT.csv` |

### 10.3 How it was verified

- **The mask is exhaustive, not sampled.** The band is fully black in **4112 of 4112
  frames**. This matters: masking only the captioned frames was tried first and left
  **14 holes totalling ~22 seconds** with captions still visible, and a sampled OCR sweep
  of that render reported it clean. Sampled OCR is not sufficient to verify a mask.
- **The cost of masking was measured before choosing it**: 8 frames — 0.3s of 137 — where
  the signer's hands are in the band during active signing.
- **The guard refuses the right things and only those**: the retracted 155 prediction is
  refused, the clean 1252 prediction still scores WER 0.9231, and the runner refuses the
  burned files while accepting the clean and masked ones.
- **`check_leakage.py` is validated against known positives on every run** — it must flag
  155-burned and 1320-burned, so a detector that has quietly stopped working fails loudly.
  Measured separation across the corpus: the two contaminated files score **0.97 and 0.85**
  reference-overlap, every clean video scores **0.00**, and the threshold is 0.30. Note
  five clean videos *do* have text on screen (a watermark, chat-app UI, player chrome) and
  are correctly not flagged — **detecting text is not the same as detecting leakage**, and
  a checker that conflated them would have been noise someone eventually switched off.
- Eval-harness suite: **79 tests pass**, up from 71. The one pre-existing test that
  asserted 155 was `verified_gold` was replaced with tripwires for the new invariant:
  155 stays excluded, exactly one item is official, and no official item may have
  `label_in_input`.

### 10.4 What this did NOT do

No model run was made and no number was regenerated. The 155 results are **withdrawn, not
replaced** — there is no clean prediction for it, and the corpus is down from two verified
accuracy cases to **one**. Nothing here makes the recogniser better; it makes the
measurements honest and hard to fake by accident.

### 10.5 What this opens

- **155 needs a prediction from the clean input** before it can re-enter the evaluation set.
- **1320's candidate reference needs human verification** against the actual signing. Its
  production direction is now settled (§9.5), so this is confirmation, not transcription.
- **LHF-6 is worth more than it was.** At n=1, annotating 1477 and 1474 (~18 seconds of
  video) is the cheapest route back to a defensible number.
- **`_PROMPT` says nothing about on-screen text**, and that is a *production* problem, not
  just an eval one: a user uploading an already-captioned video today gets those captions
  OCR'd back as a "translation". Good output, wrong claim — and it silently inflates any
  quality statistic gathered from real traffic. **Still open as of 09-07 — promoted to
  §7 P0-2.**

---

## 11. Change record — 2026-09-04 → 09-06 (the first measurement on a public benchmark)

Source: `super-inbox/visual-search-adhoc` @ `baobao/asl-temporal-ablation-2026-09-06`
— **not merged to `main` as of 2026-09-07.** Reports:
`docs/daily_report/9.5/asl-evaluation-v2/` (baseline) and
`docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md` (ablation).

**This closes the empty cell on the 09-04 scorecard.** Curify's own pipeline has now
been scored on a frozen, checksummed, 128-clip benchmark whose references we did not
write. It is the first accuracy number in this workstream's history that depends
neither on a reference of our own making nor on an input that showed the model its own
answer — and it is **worse than every number it replaces**, which is the point: the
retracted figures were flattering because they were contaminated.

### 11.1 The benchmark

`asl-translator/data/public_benchmarks/how2sign_v2/` — 128 How2Sign clips, frozen and
checksummed. All 260 files under `FREEZE_CHECKSUMS.sha256` re-verified with **zero
mismatches**, and the stored `FREEZE.sha256` fingerprint (`16c41282…`) independently
recomputed and matched. References are How2Sign's own English translations.

**The §1.0 failure mode cannot be present here.** `validation/leakage_check_results.json`
reports `frames_with_text: 0` and `reference_overlap: 0.0` on every clip.

Two properties to carry with any citation:

- **The strata are deliberately skewed** — 20 long clips are 15.6% of clips but 34.5%
  of reference words — so **this corpus WER is not comparable to published full-split
  How2Sign numbers.** It is an internal yardstick, not a leaderboard entry.
- **The harness has never been validated against either open model's published figure.**
  The ranking and the "none of these is usable" verdict are robust; the absolute values
  carry an asterisk until someone reproduces a paper number in this environment.

### 11.2 What was run — and what it is not

| | |
|---|---|
| Config | `evaluation_2026_09_04_gemini_3_6` — `gemini-3.6-flash`, `thinking_level: medium`, duration-scaled budget at 2.0 f/s, dedup on |
| Inherited verbatim from production | prompt (`sha256 ea8c5cb1…`), sampling, batching, dedup, output schema |
| Changed | the model, and its decoding knobs, for the Gemini 3.x migration |
| Provenance | `curify-studio` `origin/main` @ `f42a3a44`; run 2026-09-06T03:17Z → 03:53Z |
| Result | **128/128 clips succeeded, 0 failed** |

⚠️ **It is not `production_2026_08_29`.** That config — `gemini-2.5-flash`, what the live
tool runs — returns `404 NOT_FOUND` for the evaluation credential, which is a separate
key from production's (§2), so it could not be reproduced here. Everything below therefore describes **the migration arm, not production
as shipped**, and reporting it as production would be the same class of error as §1.0.
`production_2026_08_29`'s own config entry was diffed and confirmed untouched.

### 11.3 Headline metrics, and the three-way comparison

**ALL-128** — WER **0.9762** · CER 0.8071 · BLEU **0.1341** · chrF 11.2835 ·
1,095 substitutions / 1,779 deletions / 32 insertions · temporal precision 0.9922 ·
temporal recall 0.5814.

**MATCHED-126** is the only scope valid for cross-system comparison — it drops
`G3EfBFwsOpE_3-10-rgb_front` and `fZK9hW81XCU_9-10-rgb_front`, the two clips OpenSLT
could not predict:

| System | WER | BLEU | chrF |
|---|---:|---:|---:|
| Curify (`evaluation_2026_09_04_gemini_3_6`) | **0.9761** | 0.1346 | 11.30 |
| OpenSLT | 1.0246 | 0.962 | 18.59 |
| Uni-Sign | 0.9801 | **5.40** | **22.83** |

⛔ **Curify's WER must not be read as "we beat Uni-Sign."** WER is a weak signal against
a deletion-dominated system: a model that emits few words has few chances to substitute
a wrong one, which buys a competitive WER without saying anything correct. BLEU and chrF
are the ones sensitive to whether the content is right, and there **Uni-Sign's BLEU is
~40× ours and its chrF roughly double**. On content correctness Curify is the weakest of
the three, not the strongest. Neither open model has temporal metrics (both are
text-only), so the temporal figures are Curify-only and not part of this comparison.

Note the *shape* difference too: OpenSLT is insertion-heavy (2,053 sub / 552 del / 434
ins) — the exact opposite profile to ours. Same bad score, different failure.

### 11.4 The failure has a measured shape: deletion and coverage

- Reference totals **2,977 words**; Curify predicts **1,230** — **41% of reference
  length.**
- Of 2,906 edit operations: **61% deletions**, 38% substitutions, **1% insertions**.
- Temporal **precision 0.99** vs **recall 0.58** — when it emits a timed segment it is
  almost always genuinely aligned; it simply says nothing across ~42% of the signing.
- Distribution: mean WER 0.987, **median 1.0**, **0 clips below 0.5**, 47 in
  [0.5, 1.0), 81 at ≥ 1.0, and one empty prediction (`92V3oH63zbQ_5-1-rgb_front`, an
  8-word reference).
- Even the corpus's best clip (`g2NA_eBUcH8_0-3-rgb_front`, WER 0.75) is a truncated
  fragment: *"If you want to learn"* against *"Hi, have you ever wanted to learn a new
  game of poker?"*

**Read together: the model is not mostly misreading the signing, it is omitting it** —
stopping early, skipping stretches, returning a fragment. That is a different bug from
the one §0 describes qualitatively (fluent confident substitution), and both are real:
`QUALITATIVE_REVIEW_CANDIDATES.csv` holds the seven clips that show it, including two
low-WER-but-topically-unrelated readings (soldering flux → *"Taking a train to
Florida"*), the 78-word reference collapsed to a fabricated 20-word dog-and-bear scene,
and the one over-generating outlier (`fZM3IcM2Xs4_14_15_16-10-rgb_front`, WER 1.913,
21 of the corpus's 32 total insertions).

📌 **One citation correction.** For `FZbyRzy4huk_3-8-rgb_front` the frozen prediction is
**"Tablecloth" / "Coffee"**. An earlier ad-hoc *"Tuberculosis / Drive / Nice"* output is
floating around in prior scratch work; it is not from this baseline and must not be
quoted.

### 11.5 What this did NOT do

- **No text-memorisation control was run.** Scorecard P0-2 — prompt with a
  `SENTENCE_NAME` and no video, see whether the model completes the public reference —
  was written to gate the benchmark run, and the run happened without it. No such
  control exists in `run_curify_how2sign_v2_benchmark.py`. It does not threaten these
  numbers (memorisation would have inflated them, and they are floor-level), but it is
  now §7 P0-3 and must precede any *good* result. This is the same "fact captured,
  consequence never drawn" shape that produced §1.0.
- **It did not measure production.** See §11.2.
- **It did not make the recogniser better.** Nothing shipped to production in this work;
  no production code was changed.
- **The freeze is still verified by hand.** The runner *records*
  `freeze_sha256_fingerprint` in run metadata but does not *check* it, and
  `corpus_guard.py` remains hard-scoped to `data/asl_corpus` — it does not cover
  `how2sign_v2`.

### 11.6 Experiment B — the 8 fps temporal ablation, 76/128 and blocked

The hypothesis from §11.4: if the model is silent across 42% of the signing, perhaps it
is not *seeing* it — 2.0 f/s may simply be too sparse.

**Design.** `evaluation_2026_09_06_gemini_3_6_8fps` moves exactly one knob,
`target_frames_per_sec` 2.0 → 8.0. Model, prompt, dedup, thinking level and every other
setting are copied verbatim from Baseline A, so any delta is attributable to sampling
density alone. The override is declared per-config and threaded through
`resolve_target_fps()` / `budget_for_duration()`, so the module constant stays 2.0 for
baseline A and production — with unit tests (`TestExperimentB8fpsAblation`) asserting
exactly that. Plan-only dry run: 128 clips, 7,988 sampled frames, 383 expected calls.
Two-clip real smoke test passed with config metadata verified on disk.

**Status: 76/128 succeeded, all on first attempt, no flakiness. The remaining 52 return
`429 RESOURCE_EXHAUSTED` — the Gemini project's monthly spending cap.** A resume attempt
after the cap was believed cleared failed identically on all 52, which is what
distinguishes a billing cap from a transient rate limit. **This is an external billing
condition, not a defect in the harness, the sampling logic, or the scorer.**

Preserved and verified: the 76 predictions sit on disk under their own config metadata,
and resume behaviour was tested end-to-end — re-running against the same `--results-dir`
skips all 76 and attempts only the 52 missing. **Nothing needs re-running.** Baseline
A's results directory, the frozen manifest and the checksum fingerprint were never
touched.

**Blocked until the cap clears:** the ALL-128 / MATCHED-126 aggregation and the A/B
report. A 76-clip comparison against a 128-clip baseline is not an ablation result.
Resume command and the reasoning are in §7 LHF-9.

### 11.7 Security note

A Gemini API key was printed into local Claude session history during verification of
the baseline. The local transcript was removed and local secret scans of this
repository's changed and untracked files are clean; no credential material appears in
any committed file. **No claim is made about provider-side revocation** — only the local
remediation. If that key has not been rotated at the provider, rotating it is the
remaining action.

### 11.8 What this opens

- **Finish LHF-9** (52 clips) and get the A/B answer on frame density. It is the
  cheapest open question on the board and it is 60% paid for.
- **If density is not the cause, LHF-8** (cross-batch context) becomes the leading
  hypothesis for the deletion/coverage failure.
- **§7 P0-2** — the on-screen-text prompt bug is still shipping.
- **§7 P0-3** — run the memorisation control before the next number, not after.
- **The GTM story is now evidenced, not asserted.** "Neither we nor any runnable open
  model produces output a deaf viewer could rely on" has three systems and 128 clips
  behind it (§11.3 and the scorecard's open-model verdict). That closes off "adopt
  instead of build" and supports free-and-honest positioning — it does not offer an
  alternative to it (§8 is unchanged: nothing here approaches the ~25 BLEU bar).

## 12. Change record — 2026-09-07 → 09-09 (three temporal ablations, and what they rule out)

**Source:** `visual-search-adhoc:baobao/asl-temporal-ablation-2026-09-06` @ `4d23017`
(11 commits, **no PR, not merged to `main` as of 09-10**). Artifacts under
`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/`; write-ups in
`docs/daily_report/9.9/asl-evaluation-driven-improvement/`. **Every figure below was
independently recomputed from the committed CSVs, not copied from the summaries** —
all aggregates reproduce exactly.

**Nothing shipped to production. No production code was changed.**

### 12.1 What was built

- **A 12-clip diagnostic subset**, selected deterministically from the 128 baseline
  results across six categories (long/multi-batch, fingerspelling candidate, number
  token, fast-signing/question, very-high-WER, low-WER contrast) and **reused unchanged
  across all three ablations**, so the arms are comparable to each other and not just to
  the baseline.
- **A frame inspector** — one self-contained HTML page per clip plus an index: motion
  timeline, every sampled frame as a thumbnail grouped by batch, batch-seam markers,
  reference-vs-prediction word diff. This is the "看几个例子" deliverable §7 has wanted
  since 08-26. **Validated:** re-deriving the sampler reproduced each clip's recorded
  `frames_sampled` exactly, 0 mismatches across 12 — the pages show the frames the real
  run used, not an approximation. Browsable copy of all 12:
  <https://claude.ai/code/artifact/06a90e81-84a5-40f5-88f7-d161522117b4>
- **A 40-clip taxonomy set** (the 12 above + 28 by category quota) and a localhost
  review app for ASL-fluent annotation. **The app has never been used** — see 12.5.

### 12.2 The three ablations

Each moves exactly one variable against the frozen Baseline A, reusing its saved
predictions as the control arm and making fresh calls only for the new arm.

| # | Variable moved | Scope | corpus WER | per-clip |
|---|---|---|---|---|
| A | frame density, `target_frames_per_sec` 2.0 → 8.0 | 76 paired clips (§11.6, still billing-capped) | 0.9730 → **0.9715** (−0.0015) | 15 better / 20 worse / 41 same, median **0.0000** |
| B | sampling strategy, motion-weighted → uniform, density held | 12 clips | 1.0524 → **1.0594** | 2 / 5 / 5, median **0.0000** |
| C | batching, independent 24-frame → overlapping windows (size 24, stride 12) | 12 clips | 1.0524 → **0.9545** | 4 / 2 / 6, median **0.0000** |

**A and B are flat.** B's only large mover (`fZM3IcM2Xs4`, 1.913 → 1.000) swapped one
hallucination for another — "different perspectives and situations" became "crawling
around for two hours," against a reference about a festive musical performance.

**C's 0.098 WER movement is not a quality gain, and this needs to be said plainly
because the number is tempting.** Three independent reasons:

1. **All 12 clips remain topic-mismatched under both arms.** Zero clips recovered
   correct meaning.
2. **It is largely a length artifact.** Recomputing a length-insensitive metric over the
   same CSVs: **chrF2 14.30 → 13.54 — slightly worse** — while the sliding arm's
   prediction/reference word ratio fell **0.566 → 0.458**. Shorter output cuts
   insertions, and on a corpus already at WER ≈ 1.0 that lowers WER without improving
   anything. This is the §11.4 deletion failure being *rewarded* by the metric.
3. **Part of it is decoding noise.** The 8 single-batch clips are architecturally
   identical between arms (1 window = 1 batch = same frames, same call), so their spread
   is pure generation variance: mean WER delta **−0.0673**. The multi-batch subset's
   mean of −0.2503 rests on **n=4**, one of which dominates, and two of which show
   *exactly zero* WER change while producing completely different fabricated text.

📌 **A second, larger noise control exists in arm A and was not used.** 17 of its 76
clips got **byte-identical frame counts** at 8 fps — the `MIN_FRAME_BUDGET=24` floor
binds on short clips — making them a free 17-clip decoding-noise sample: mean delta
**−0.0093**, mean |delta| **0.0289**, 14/17 unchanged. That is ~3.7× tighter than the
n=8 estimate above. Any future small-n ablation should pool both before setting a
promotion bar.

⚠️ **Arm A's "~4× density" is overstated in its own write-up.** Because of the same
floor, median realised density rose **1.85×** (mean 2.27×; 6.36 → 9.69 f/s), not 4×.
The conclusion survives — the 59 clips that *did* get more frames are still flat, mean
delta −0.0039 — but the headline should not be quoted as a 4× test.

### 12.3 The 40-clip semantic review — the most decision-relevant result here

An explicitly-labelled **LLM-assisted, text-only** review (English reference vs. English
prediction, no video watched, no ASL expertise applied), covering all 40 clips:

| metric | value |
|---|---|
| core meaning correct (`semantic_adequacy=2`) | **0 / 40** |
| partial (`=1`) | 3 / 40 |
| wrong / unrelated (`=0`) | **37 / 40 (92.5%)** |
| clear topic mismatch | **36 / 40 (90%)** |
| **correct meaning, different English** | **0 / 40** |
| text-level repetition | 0 / 40 |

**The 0/40 on "correct meaning, different English" is the load-bearing number.** It
retires the most comfortable remaining explanation for §11's WER — that a decent
translation is being punished by edit-distance scoring. It is not. The dominant failure
is topic-level: the model describes different content, fluently.

### 12.4 What this rules out — and what it does not

**Ruled out, at these sample sizes:** more frames under the existing motion-weighted
rule; replacing motion-weighted allocation with uniform; and generic cross-batch context
via overlapping windows. None produced a single clip where a wrong prediction became a
right one.

⚠️ **Stated as the diagnosis states it:** this is *not* "temporal information is
useless." It is "these three frame-based interventions, at these sample sizes, on these
clips, did not move the dominant semantic failure."

**Not established by any of it:**

- The real ASL failure taxonomy — handshape / motion / fingerspelling / numbers /
  facial-non-manual / genuinely visually-grounded hallucination. **Blocked on an
  ASL-fluent reviewer, which this workstream still does not have.**
- **Native/direct video input to Gemini** — completely untested; no video-upload code
  path exists, only `Part.from_bytes(image/jpeg)` per extracted frame.
- **Model choice** — every arm used `gemini-3.6-flash`.
- **Whether the model is simply under-generating** (prompt, token cap, or the dedup
  merge) rather than mis-reading. Given §11.4 (41% of reference length, 61% deletions,
  1% insertions, temporal recall 0.58) this is cheap to probe and orthogonal to every
  temporal axis now exhausted. **Nobody has tested it.**

### 12.5 Two defects in the diagnostic artifacts — fix before quoting them

1. ⛔ **The unreviewed ASL taxonomy is stored as confirmed negatives.**
   `review_app/server.py:145` `blank_annotation()` initialises all 17 `content__*` /
   `failure__*` tags to `False`, not `None`. So `taxonomy_40_human_review.json/.csv`
   assert `failure__handshape = False` for all 40 clips **when nobody has looked**, and
   two rows (`FzmL8SL6Bow_1-8`, `fzNnTgHa1lM_2-5`) still carry
   `failure.hallucinated_topic = true` while the same row's own note records that the
   judgment was downgraded to `requires_asl_review` on 09-07. The 09-09 work report
   states these tags "were left **entirely blank**" — that is not what is on disk.
   Anyone aggregating that CSV reads "0/40 handshape failures, 2/40 confirmed
   hallucinations" as fact. **This is the same "unknown silently serialised as a
   finding" shape as §1.0 and §11.5.**
2. ⚠️ **All three ablations report WER only** — the metric §11.3 and §4 already record
   as the one that *cannot* separate these systems. `lib.text_metrics()` returns CER and
   sub/del/ins counts for free and neither was reported; chrF and BLEU — which do
   separate them (Uni-Sign chrF 22.83 vs Curify 11.30) — were computed for none of the
   three arms. Add CER, chrF and a prediction/reference length ratio to every future arm.

### 12.6 SpaMo and SSVP-SLT — re-checked, still not runnable

Re-verified **live on 2026-09-10**, and against the 09-02 record
(`docs/daily_report/9.2/asl-baselines/SPAMO_SSVP_SLT_FEASIBILITY_RECHECK.md`):

| | SpaMo | SSVP-SLT (Meta) |
|---|---|---|
| Latest commit | `aee7f8b6` — **identical to 09-02** | `7ed332b0` — **identical to 09-02** |
| Last pushed | **2025-07-09** (14 months) | 2026-05-19 |
| Releases / tags | 0 / 0 | 0 / 0 |
| Licence | **none at all** | **CC BY-NC 4.0** — non-commercial |
| Released ASL checkpoint | **No** — the one checkpoint is Phoenix-2014T (**German** Sign Language); repo holds one config and one preprocessing dir, both Phoenix14T | **No checkpoint of any kind exists** — `translation/README.md` reads *"Once you have obtained a pretrained model…"* |
| How2Sign support | README prose only; **no How2Sign config, preprocessing or checkpoint in the repo** | **Yes, in code** — literal `data_dir=/path/to/how2sign`, `slt_t5` config. Best native How2Sign path of anything checked. Nothing to run through it |
| Input | pre-extracted CLIP ViT-L/14 + VideoMAE-L `.npy` | pre-extracted `.pt` + manifest `.tsv` |
| Verdict | `NOT_RUNNABLE_WRONG_LANGUAGE_OR_TASK` | `NOT_RUNNABLE_NO_WEIGHTS` |

Identical commit SHAs mean the contents are provably unchanged — no re-listing needed.
**Neither can be run on the eval set, and neither is deployable in production even if
weights appeared:** both consume pre-extracted feature files rather than raw video (the
same wall OpenSLT hit), SSVP-SLT requires Linux + CUDA ≥ 11.7 with no macOS/CPU path,
and its licence forbids commercial use — as does Uni-Sign's. Getting a number from
either means training, which is out of scope.

📌 **One item not in the 09-02 record.** A third-party HuggingFace repo,
`croco-corp/spamo-pjm-checkpoints` (uploaded 2026-05-03), hosts
`spamo_pjm_ms_dual_bleu5.36.ckpt` — a SpaMo checkpoint for **PJM, Polish Sign
Language**, no model card, no licence. It does not change the verdict (Polish is as
disqualifying as German for an ASL baseline) and is recorded only because it confirms
the pattern: SpaMo checkpoints are trained per sign language, and **nobody has published
an ASL/How2Sign one.**

### 12.7 What this opens

- **§7 LHF-9 is still the cheapest open question** and is now *more* worth finishing,
  not less: arm A's realised density gain was 1.85×, not 4×, so the flat result is a
  weaker test of density than it was reported to be.
- **§7 LHF-8 has been probed and came back negative on semantics** — see its updated
  entry. The probe is not identical to LHF-8 as specified, so LHF-8 is downgraded from
  "leading hypothesis," not closed.
- ~~**Two genuinely untested axes remain**~~ — ~~**native/direct video input was run on
  2026-09-10 and is the first thing that moved the failure: see §13 and P0-4.**~~ **On
  independent references it recovered meaning on 0 of 5 clips (§14.1)**, and a third axis
  — trajectory as prompt context — was tested on 09-10 and returned **0 of 5** (§14.2).
  Still untested: **full-body + high-resolution hand-crop dual-stream input** (spatial rather
  than temporal; same call count, modestly larger payload) — now the last member of a class
  with five zeros behind it (§14.6), and it should not be funded ahead of P0-6.
  A pre-registered promote/reject criterion for the hand-crop probe is written up in
  `WORK_REPORT.md` §12 — **it has not been run, and it needs Gemini spend the project
  does not currently have.**
- **The under-generation probe in 12.4** — cheapest of the lot, needs no new dependency
  and no benchmark run.
- **Fix 12.5's defect 1 before anyone reads that CSV as a taxonomy result.**
- **§8 is unchanged.** Nothing here approaches the ~25 BLEU bar, and 12.6 confirms there
  is still no fourth system to adopt.

---
## 13. Change record — 2026-09-10 (native video input — the first intervention that moved anything)

> ⚠️ **Read §14.1 before quoting anything in this section.** P0-4 ran this on the frozen
> benchmark's 12 diagnostic clips, against independent references instead of this section's
> circular one. **0 of the 5 clips scored so far recovered meaning**, and where WER improved
> it improved by exchanging one hallucination for another. The section title is the 09-10
> reading and is kept as written; on current evidence it holds for **one private clip**, not
> for native video as a technique. What survives: native video is **cheaper** (1 call vs
> 4–7) and, so far, **no more accurate**.

**What was run.** The whole `.mp4` sent to Gemini via the Files API, instead of
extracted JPEG frames. This is §12.4's top-ranked untested axis and §11.8's own
first recommendation, finally executed. **One clip only** — the private-corpus
video `1252_1000016397_76.8s`. Nothing shipped to production; no production code
was changed. The runner is a standalone script, not a `run_current_model.py`
config: `scratchpad/nativevid/run_native_video.py` (see 13.5 for why that matters).

### 13.1 Design, and the control that makes it readable

The first attempt was **confounded** and is recorded here rather than quietly
fixed: the corpus's saved predictions for this clip are `gemini-2.5-flash`, and
the native-video call was `gemini-3.6-flash`. Comparing those two moves *model*
and *modality* together. **A control was therefore run** — the frame pipeline on
the same clip at `evaluation_2026_09_04_gemini_3_6`, i.e. the same model as the
native-video arm — so exactly one variable separates test from control.

| held fixed | varied |
|---|---|
| clip, reference, scorer (`asl-eval/lib.py`), model (`gemini-3.6-flash`), JSON output schema | **input modality only:** 7 batches of extracted frames vs. one whole `.mp4` |

⚠️ **One confound cannot be removed.** The prompt *must* change: the production
prompt tells the model the images are sparse, non-uniformly sampled, and
timestamp-labelled — all false for video input, and actively misleading. Only the
modality-forced sentences were changed (the "frames are sparse / you are seeing key
moments" paragraph removed, "frame timestamps you used" → "the video timeline");
task, rules and output schema are byte-identical. The exact diff is recorded in
`native_video_result.json` under `prompt_diff_vs_PRODUCTION_PROMPT`.

### 13.2 Measured result

| arm | model | input | WER | CER | pred words | model calls |
|---|---|---|---|---|---|---|
| frames · `baseline0` | gemini-2.5-flash | frames | 0.9231 | 0.7211 | 50 | 4 |
| frames · `temperature0` | gemini-2.5-flash | frames | 0.9231 | 0.6693 | 41 | 4 |
| **frames · `evaluation_2026_09_04_gemini_3_6`** ← control | gemini-3.6-flash | frames | **0.9615** | 0.7131 | 47 | 7 |
| **native video** ← test | gemini-3.6-flash | **whole .mp4** | **0.8269** | **0.6454** | 42 | **1** |

**Against its own control: −0.135 WER, −0.068 CER.** That is outside the
decoding-noise floor §12.2 measured (mean |delta| 0.029–0.107 on architecturally
inert clips). It also used **1 call instead of 7**, 9,676 total tokens, 15.9s
wall-clock — cheaper *and* faster, not a quality-for-cost trade.

📌 Note in passing: the 3.6 control (0.9615) is **worse** than the 2.5 `baseline0`
(0.9231) on this clip. The Gemini 3.6 migration did not help here either — consistent
with §11's overall picture, and a reminder that the model axis is not the win.

### 13.3 The qualitative difference is larger than the number

The reference is an ASL class exercise made of **numbered items**.

> **frames (3.6, control):** *"Do you know Mrs. you read Stand Number 3 Glasses Number
> four. What is your name? That girl has the same name. Five Parents Red Room Brown
> Before, now I will tell you about movie three…"*
>
> **native video (3.6, test):** *"Number one: E. Number two: Dancing. Number three:
> Looking out the window. Number four: A crooked smile. Number five: A man walking by,
> looking at me, and scolding me about dirty hands. Number six: Comparing two people.
> Number seven: Reading a book."*

**Native video recovered the numbered-list structure; the frame pipeline never did.**
Item by item, *"Number two: Dancing"* against *"Number two. You're going to dance?"*,
and *"Number seven: Reading a book"* against *"The book is number three. You read it"*,
are **semantically correct** — roughly **2 of 7 items right**.

**This is the first time anything in this workstream has recovered actual meaning on
any item.** Every arm in §12 produced 0/12 clips with correct meaning; the 40-clip
review produced 0/40 adequate. That is the significance here — not the WER delta.

### 13.4 What did NOT improve: fingerspelling

Greg → *"E"* (native), *"H.G.Q."* (`baseline0`), *"HPG"* (`temperature0`),
*"Mrs."* (3.6 frames). **Sara → absent from every arm.** §4's finding that
fingerspelling "fails completely and temperature-independently" now extends to
**modality-independently.** The one independently-corroborated pass/fail this clip
offers (§ the SignCaption agreement on both names) comes back **negative**.

### 13.5 Limitations — read before quoting any of this

- **n = 1 clip.** A diagnostic, not a measurement. **Do not quote 0.8269 as an
  accuracy number.**
- **The reference is circular** (`non_independent`, `usable_for_official_metrics:
  false`, §4). The *delta* is more defensible than either absolute figure, because
  both arms are scored against the same string neither authored — but it is still
  one clip against a reference Curify wrote.
- **Prompt confound**, unavoidable — see 13.1.
- **No repeat runs.** §12.2 showed this model changes its output substantially on
  identical input; a single draw per arm carries that variance.
- **Not a config.** The native path exists only as a scratch script and is **not**
  in `run_current_model.py`, so it is not reproducible through the normal harness,
  not covered by `TestProductionParity`, and not resumable. P0-4 fixes this.

### 13.6 ⛔ A reproducibility bug this surfaced, affecting §11 and §12

`thinking_level: "medium"` **is not a valid value.** In google-genai 1.55.0 the
`ThinkingLevel` enum is `THINKING_LEVEL_UNSPECIFIED | LOW | HIGH`, and the SDK emits
`UserWarning: medium is not a valid ThinkingLevel`. **The same warning fired on the
`evaluation_2026_09_04_gemini_3_6` control run**, whose config comment in
`run_current_model.py` reads *"Gemini 3.6's documented default; pinned explicitly for
reproducibility."*

On this SDK that pin is **silently inert** — the run falls back to the model default,
and nothing in the harness notices. It affects both 13.2 arms equally so the comparison
above stands, but **every §11 and §12 number carries a provenance claim that may not be
true.** Verify against the SDK version the benchmark machine used, then either pin a
valid level or delete the claim. A config value the SDK rejects should fail the run,
not warn.

---
---
## 14. Change record — 2026-09-11 (P0-4 executed on the frozen benchmark; §13 did not reproduce)

**Source:** `visual-search-adhoc @ 01cfd054`, branch `baobao/asl-temporal-ablation-2026-09-06` —
`docs/daily_report/9.11/{ASL_WORK_REPORT,ASL_MANAGER_SUMMARY}.md` plus the three 9.10 task
folders. Those documents are consolidations: **no model was re-run to produce them.**
Nothing in this record shipped to production, and `curify-studio` was not modified by that
work. No PR was opened.

Four tasks were set on 09-10, off §13 and §12.7. All four came back:

| Task | Status | Result in one line |
|---|---|---|
| **A** — Uni-Sign into the frame inspector | ✅ **complete** | 4 systems side by side per clip, read-only, empty ≠ unavailable (§14.4) |
| **B** — native video on the frozen benchmark (**P0-4**) | 🟡 **partial / infra-blocked** | real config built; **5/12 clips scored, 0/5 recovered meaning**, 7 blocked at the Files API (§14.1) |
| **C** — SignCaption / Sign-Speak | ⛔ **research complete / access pending** | the blocker is a ToS clause and an unanswered email, not engineering (§14.3) |
| **D** — trajectory tracking | ✅ **POC complete, D2 negative** | tracking works (0% missing); handing it to Gemini as prompt text recovered **0/5** (§14.2) |

### 14.1 Native video on independent references — P0-4, and what it costs §13

**P0-4 step 1 is done.** Native video is no longer §13.5's scratch script: it is
`asl-eval/run_native_video.py` plus a benchmark driver, built as a **sibling** of
`run_current_model.py` so every frozen frame config stays byte-for-byte unchanged. It is
resumable (verified across three invocations), scores through the unmodified
`asl-eval/evaluate.py`, cleans up Files-API uploads in a `finally` block, records provenance
on every prediction, and **defaults to dry-run** — a real run needs both `--run` and
`--acknowledge-private-data-upload`. The §13.1 prompt confound is unchanged and is
documented in the module's own docstring rather than buried.

**P0-4 step 2 is 5/12 done, and the answer so far is no.**

| clip | native WER | native CER | semantic adequacy | topic mismatch |
|---|---:|---:|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | 1.0000 | 0.9298 | 0 | yes |
| `-g0sqksgyc4_3-2-rgb_front` | 1.0000 | 0.8022 | 0 | yes |
| `92V3oH63zbQ_5-1-rgb_front` | 1.0000 | 1.0000 | 0 | yes |
| `fzNnTgHa1lM_2-5-rgb_front` | 0.9118 | 0.7962 | 0 | yes |
| `G05uFub3YFc_9-2-rgb_front` | 0.9412 | 0.7251 | 0 | yes |

**0 of 5 semantic-adequacy flips. 0 of 5 topic-mismatch flips.** The same failure class as
the frame baseline, against references we did not write.

**The clearest case is G05**, where the *number* improved and nothing else did — WER
1.0294 → 0.9412, CER 0.8012 → 0.7251:

> **Reference:** breathing-exercise instructions — *"Again, do maybe twenty breaths, little
> flow, inhaling and exhal…"*
>
> **Frame baseline:** *"She smooths out the cloth and places it flat on the table… She puts
> on her gear and fastens it securely around her back. The tree caught on fire."*
>
> **Native video:** *"I was terrified and my heart was pounding. Then I looked closely and
> saw what was actually there."*

One unrelated hallucination exchanged for a different unrelated hallucination, at a better
WER. This is §12.5's warning firing again, and it is the thing to quote when anyone reports
a metric delta from this workstream as an improvement.

⚠️ **The P0-4 gate is inconclusive, not failed.** Its pre-registered thresholds were carried
verbatim into every run's `run_metadata.json`: promotion at ≥3/12 flips, rejection at 0/12
flips *and* WER movement inside the noise floor. With 5/12 scored, promotion is still
arithmetically reachable and rejection cannot be asserted. **Do not extrapolate 5/12 to
12/12 in either direction.**

**The 7 unscored clips failed before the model ever ran.** They died in the Gemini Files API
upload/poll step — the same 7 IDs, identically, on two independent attempts with no config
change. A local `ffprobe` pass found nothing that separates them from the 5 that worked (all
12 are h264 / 1280×720 / yuv420p, with overlapping duration, framerate and size ranges). Two
readings remain live and **neither is confirmed**: transient/account-side Files API
degradation (an independent `client.files.list()` failed twice with `ServerError 500`), or a
clip-specific processing incompatibility (pure transience would be expected to hit a random
subset, not the same 7 twice). The resume command is recorded in `BLOCKER_STATUS.md`; a
third identical failure on the same 7 should go to Gemini API support, not into another
retry.

**One real bug was found and fixed properly.** `G05uFub3YFc` had originally been pooled with
the Files-API group. It did not belong there: its recorded `inference_wall_clock_s` was
16.622 s — the range a real `generate_content` call takes on this corpus (8.5–18.5 s), not
the ~3 s an immediate `FAILED` returns. **Gemini had returned a bare JSON array where the
schema asked for `{"segments": [...]}`,** and the parser assumed the object shape. Local bug,
not a backend one. The parser now accepts either shape, and the fix was **validated
end-to-end** rather than assumed: a single-clip retry made a real call (`model_calls=1`,
17.459 s, `status=success`), got the same bare-array response, and parsed it. Diagnosing that
from call timing instead of pooling it with the other failures is the methodological win in
this task.

⚠️ **These runs carry the P0-5 defect.** The verified config is
`native_video_2026_09_10_gemini_3_6` — `gemini-3.6-flash`, **`thinking_level=medium`**, no
explicit temperature. That is exactly the value §13.6 found the SDK rejects and silently
drops. The comparison is unaffected (all arms share it), but **§14.1's provenance claim is
as unverified as §11's and §12's**. P0-5 now has a third change record depending on it.

**What this does to §13.** §13 stands as written — nobody re-ran 1252, and its numbered-list
recovery is still on the record. What changes is what may be claimed from it. §13's result
is one private clip against a **circular** reference (`usable_for_official_metrics: false`);
§14.1 is five clips against independent, checksummed ones, and the meaning-recovery it was
supposed to reproduce did not appear. **Do not quote "2 of 7 items right" as a property of
native video.** The defensible statement today is narrower and worth keeping anyway: native
video is **cheaper** — 1 call per clip against the frame pipeline's 4–7 — and, on everything
independently scored so far, **no more accurate**.

### 14.2 Trajectory tracking — the signal is there, and Gemini can't use it as text

Origin: the CV tennis example — video converted into structured spatiotemporal trajectories
— and whether explicit, continuous hand/body/face tracking could help as an *additional*
signal alongside handshape, fingerspelling, non-manual markers and language context.

**First, a distinction the experiment earns.** This is genuinely different from the sampler
we already ship. Our existing motion signal, `probe_motion`, is **one scalar per timestep**:
mean absolute whole-frame grayscale pixel difference. It can say *when* something moved,
never *where* or *what*. Trajectory tracking produces a named per-landmark `(x, y,
confidence)` time series. But it is **not new to the project** — Uni-Sign, already one of
the four systems on the frozen benchmark, is built on RTMPose keypoints. Pose was new to our
Gemini pipeline only.

**D1 — extraction works.** RTMPose via `rtmlib` (`Wholebody`, lightweight, ONNX/CPU) on 5
probe clips chosen to stress the hardest cases (shortest, fastest signing,
fingerspelling-heavy, richest content, longest):

- **5/5 success**, 1,038 frames across ~38 s of video in 62.2 s of laptop-CPU wall-clock —
  roughly real-time to 2× real-time.
- **Missing-tracking 0.0%** for body, left hand and right hand, **on every frame of every
  clip**. 0 multi-person frames.
- Mean per-part confidence ~0.81–0.93, with one weak case: `-g0iPSnQt6w`'s left hand at
  0.579 (visibly less prominent in frame; still above threshold in 100% of frames).
- Visual QA on 4 of 5 clips: skeletons on the actual limbs, face landmarks on the actual
  face, hand skeletons resolving **individual finger joints**, including a legible
  fingerspelling-style handshape on `Fz-N1S0swh8`.

⚠️ **5 clips, not 128.** Tracking quality on the other 123 is unmeasured. The tempting
corollary — "so pose quality isn't why Uni-Sign fails" — holds for these 5 clips and nowhere
else yet.

**D2 — feeding it to Gemini as text does not work.** Single-variable design on the same 5
clips: same frames, same model, same sampling, same decoding config. The only change was
appending **one** block of purely geometric observations (position samples, confidence,
speed, body-relative bands, two-hand distance) to the existing prompt. Pre-flight verified
before any call: no interpretive or ASL-semantic phrasing in the block, frame
count/order/batching re-derived identically from each clip's own frozen budget, and the
reference text inaccessible to the model. 7 Gemini calls total; the control arm made 0,
reusing frozen predictions.

- **0/5 semantic-adequacy flips. 0/5 topic-mismatch flips.**
- 3/5 changed *which* wrong text they produced. 1/5 (`92V3oH63zbQ`) returned byte-identical
  empty output in both arms. The single WER improvement (`G19uBylwQww`, −0.0385) sits inside
  §12.2's noise floor and came from swapping a fabricated biographical detail for a generic
  greeting.
- The textbook confound, in the opposite direction from §12.2 arm C: `FzmL8SL6Bow` went
  **BLEU 0.2719 → 0.5051 and chrF 11.1616 → 14.3380 while WER stayed byte-identical at
  0.9615.** The model restated the same fabrication in more words. Arm C bought WER by
  getting shorter; this buys BLEU/chrF by getting longer. Neither is a translation.

**Closed:** trajectory-as-structured-text to a generic Gemini. No further calls, no prompt
tuning, no expansion to the diagnostic-12 or the 128. Ruling it out cost 7 calls, and ruling
something out cheaply is a result.

**Not closed:** pose/trajectory as a signal. D2 tested one implementation — raw kinematics
handed as text to a model never trained to read them. A model *trained* to consume the
signal directly is untested here. ⚠️ But Uni-Sign is the caution as much as the hope: it is
that kind of model, consumes that signal, and sits at **WER 0.9819 / BLEU 5.39** on the same
128 clips.

### 14.3 SignCaption / Sign-Speak — the blocker is a contract clause, not engineering

Method: local research only — both repos grepped for documentation, outreach history,
provenance files and `.env*`. No network calls, no vendor contact. Every known item cites a
source; every unknown is recorded as unknown.

**Known.** Sign-Speak is the vendor and SignCaption its ASL captioning product; an "API &
SDK Integration" offering exists on its public Enterprise page, which documents a base64
video parameter (`b64video`). **This is not a cold start** — a pricing inquiry went to
`management@sign-speak.com` from `gtm_tools/send_signspeak_inquiry.py` and **was never
answered**, which is why the project was docked once already. Our internal SignCaption
accuracy figures — **WER 0.4815 / CER 0.3712 on 155, WER 0.5192 / CER 0.3347 on 1252, with
"Greg" and "Sara" both recovered** — come from **manually downloaded SRT exports on disk,
never a live API call**, on private-corpus clips tagged `usable_for_official_metrics:
false`. The vendor's marketed "BLEU 60" is unverified marketing.

**Unknown, and not resolvable from any repo:** credentials (no `SIGN_SPEAK` / `SIGNCAPTION` /
`SIGNSPEAK` variable in any `.env*` in either repo), endpoint URL, request/response schema,
auth scheme, pricing, rate limits, and permission to use its outputs as a benchmark
comparator.

⛔ **The gate is the ToS.** Sign-Speak's public Customer ToS bars using the service **"to
create a competitive product"** — our own ASL translator arguably is one — prohibits
sublicensing and resale, **licenses uploaded video back to Sign-Speak worldwide, perpetual
and royalty-free for model training**, and caps liability at trailing-6-months fees. **No
written clearance on the competitive-product clause exists**, and it was already flagged as a
gating Step 0 in an earlier plan.

⚠️ **Consequence worth stating plainly, because it is easy to walk into:** that training
licence applies to whatever we upload. Running our private user corpus through SignCaption
would hand Sign-Speak a perpetual training licence to real users' identifiable video. §5's
consent posture does not survive that. Any live evaluation uses public benchmark clips, or
it does not happen.

Order of work: **written ToS clearance → benchmark-use permission → technical evaluation.**
All three are email and legal, not code.

### 14.4 The inspector is now the comparison instrument (Task A)

Each of the 12 diagnostic clip pages now shows, with the same word-level Levenshtein diff
against the reference: **reference · Curify frame baseline · Uni-Sign · Gemini native
video**, each with its own WER/CER. `index.html` gained per-system WER columns, a
trajectory-probe column and explicit coverage banners.

Two properties that make it trustworthy:

- **Read-only.** It re-runs only the production *sampler*, to redraw which frames the model
  actually saw. It makes **no model call**. Predictions and their WER/CER are read from each
  system's frozen `per_clip_results.json`, never recomputed — so the page cannot drift from
  the scored corpora.
- **A real empty prediction is not an unavailable one.** A system that genuinely returned
  nothing renders as `(empty prediction)`; a system with no valid result renders as
  `Unavailable — <reason>`, with Files-API failures named as such and post-inference
  failures showing their own reason. That distinction is exactly what stopped the G05 parser
  bug from being buried in the Files-API group (§14.1).

**Why this matters more than it sounds.** All four systems sit near WER ≈ 1.0, where the
metric cannot discriminate — an edit distance near 1 is equally compatible with an empty
output, a short wrong one, and a long fluent fabrication. Seeing three systems hallucinate
three unrelated narratives from the same frames is not visible in any scorecard, and it is
what every conclusion above is actually built on.

### 14.5 What this did NOT do

- **Nothing shipped.** `asl_utils.py` and `asl_pipeline.py` are untouched; production still
  runs `gemini-2.5-flash` on frames, free, with the unverified notice.
- **No §11 or §12 number changed.** Nothing was re-scored.
- **P0-2** (the on-screen-text prompt bug, still live and user-facing) and **P0-3** (the
  memorisation control that should have preceded §11) were not touched. Both still open.
- **LHF-9** — the 52 missing 8 fps clips — still blocked on billing.
- ⛔ **Still no ASL-fluent human review.** Every semantic judgment in §12, §14.1 and §14.2 is
  text-only: English reference against English prediction. It cannot separate a visually
  grounded misread from an ungrounded hallucination, and it cannot test a single
  ASL-specific hypothesis — handshape, motion, fingerspelling, numbers, non-manual markers.
  **This is the fourth consecutive change record to flag it.** Every architectural conclusion
  below is downstream of a judgment no one on this project is qualified to make.

### 14.6 Where this leaves the workstream

Five input-side axes have now been tested against the same frozen benchmark with the same
unmodified scorer:

| axis | where | clips that recovered meaning |
|---|---|---|
| frame density, ~2 → ~8 fps | §11.6, §12.2 | 0 (paired-76; corpus WER Δ −0.0015) |
| sampling, adaptive → uniform | §12.2 | **0 / 12** |
| grouping, independent → sliding windows | §12.2 | **0 / 12** |
| modality, frames → native video | §14.1 | **0 / 5** (7 unscored) |
| representation, + trajectory as prompt text | §14.2 | **0 / 5** |

Zero — not "small", zero. Across every one of them, no wrong prediction became a right one,
and the 40-clip review still stands at **0/40** cases of "correct meaning, different
English" (§12.3). What these five share is the intervention class: *changing what visual
information a generic multimodal model is handed at inference time.* That class now carries
more negative evidence than anything else on this board, and further variants of it — 5 fps,
10 fps, another trajectory phrasing, another prompt rewrite — are the least defensible use of
the next Gemini dollar.

**The surviving hypothesis** is that ASL needs a **sign-specific learned temporal/linguistic
representation**, not better-formatted input to a general model. It is a hypothesis, and our
own nearest data point argues against treating it as a plan: **Uni-Sign is that kind of
model, consumes exactly that signal, and still sits at WER 0.9819 / BLEU 5.39 on these 128
clips.** So the next move is not to train anything. It is to find out *why Uni-Sign fails
here* — an analysis against artifacts already on disk, which either strengthens the
hypothesis or kills it before anyone commits a training budget to it.

**§8 is unchanged.** Nothing in this record approaches the 12.39 BLEU field SOTA, let alone
the ~25 BLEU bar §8 sets for reopening the model question.

### 14.7 What this opens

- **P0-4 needs a decision, not a retry loop.** Finish the 7 only if the Files API becomes
  reliable; resumability skips the 5. If a third identical attempt fails on the same 7 IDs,
  that is evidence for clip-specific incompatibility and belongs with Gemini support.
- **P0-6 is new and is the cheapest item on the board:** diagnose Uni-Sign's failure from
  artifacts already on disk (§14.6).
- **P0-7 is new:** ToS clearance from Sign-Speak. An email and a legal read; it gates the
  only read we can get on what a purpose-built commercial ASL system does on our benchmark.
- **P0-5 grew a third dependant** (§14.1) and is still unfixed.
- **§12.7's last untested input-side axis** — full-body + high-resolution hand-crop
  dual-stream — should now be read as the last member of a losing class, not the next hope.
  It should not be funded ahead of P0-6.
- **P0-3 is now overdue twice over.** Five axes have been scored against a benchmark whose
  memorisation control was never run.

---

## 15. Change record — 2026-09-15 → 09-19 (Uni-Sign runs for real; the deployment question, answered)

**Source:** `visual-search-adhoc @ c0bfcc3`, branch `baobao/asl-temporal-ablation-2026-09-06` —
`docs/daily_report/9.15/ASL_MANAGER_SUMMARY.md`, `9.17/unisign-deployment-work-report/`,
`9.18/asl-manager-followup-a-c/`, `9.19/unisign-real-e2e/`,
`9.19/unisign-overlapping-segmentation/`, `9.19/gloss-free-asl-translation-audit/`.
Plus **`curify-studio` PR #448 (DRAFT, `baobao/asl-unisign-fastapi-service`, +819/−0)**, the
first ASL code ever proposed against the backend repo. **Nothing here shipped.** Production
still runs the Gemini frame pipeline described in §2; no image was pushed to ACR, no Azure or
GCP resource was touched, and `curify_background/` is unmodified.

This record exists because the workstream changed kind. §11–§14 were about *measuring* a
model. §15 is the first time one of the measured models was **built as a deployable
service**, run against the real checkpoint, and asked the question production actually cares
about: can this be shipped, and what does it do to a real user's video?

The short version: **it runs, it is reproducible on short clips, it is still not accurate,
and it cannot be deployed** — the last for a reason that is not an engineering one.

| Task | Status | Result in one line |
|---|---|---|
| **a** — real-checkpoint local E2E | ✅ **complete 09-18/09-19** | `/readyz` 200 with a strict-loaded real checkpoint; real translations for a short and a long clip (§15.1) |
| **b** — overlapping segmentation before Uni-Sign | 🟡 **tested, no clear benefit** | mechanically fixes the 256-frame drop; **no evidence translations got better**, ≈2.2× cost (§15.4) |
| **c** — `gloss-free-asl-translation` bring-up | ⛔ **pipeline works, no trained checkpoint exists** | an upstream-artifact blocker, not a local failure (§15.6) |
| **Deployment** (PR #448 → ACR → Azure App Service) | ⛔ **blocked** | four blockers, the first of which is a licence, not code (§15.5) |

### 15.1 Uni-Sign now runs end to end on the real checkpoint — locally

PR #448 adds `uni_sign_server/`, modelled on this repo's `xtts_server/`: lazy singleton model
load, `/healthz` + `/readyz` + `POST /translate`, single uvicorn worker, tempfile-and-cleanup
uploads, and a runtime licence gate (`UNISIGN_NC_CHECKPOINT_LICENSE_ACK=1`) mirroring
`xtts_server`'s `COQUI_TTS_LICENSE_ACCEPTED`. Upstream Uni-Sign is vendored at the pinned
commit `eed438bc…`, with a 5-line patch replacing four hardcoded `.cuda()` calls with an
env-driven device. **Decoding is the benchmark's, unchanged:** `num_beams=4`,
`max_new_tokens=100`, pose-only, `seed=42`.

The 09-17 report graded local deployment **PARTIAL** — everything was verified except the one
thing that matters, because the real checkpoint was not on the machine and a 22-byte dummy
file was standing in for it. That closed on 09-18 and was re-run cleanly on 09-19:

- Checkpoint fetched from the official HF repo (`ZechengLi19/Uni-Sign`), **1,186,925,007 bytes
  and sha256 `1bfd5f33…fb00d`, both exact matches**. Never committed, never baked into the
  image, mounted read-only at run time.
- `/readyz` **200**, `model_loaded: true`. `load_state_dict(strict=True)` with **zero missing
  and zero unexpected keys** — the architecture matches the checkpoint exactly. 19 s to load
  with a warm HF cache (55 s including the mT5-base download).
- `/translate` **200** on both a short and a long frozen-benchmark clip, inside the
  `linux/amd64` container.

**This is a real E2E pass, and it is the strongest engineering result the workstream has
produced.** It is also the point at which the non-engineering blockers become the whole story.

### 15.2 What it actually said

Two frozen How2Sign v2 clips, real checkpoint, container run (`9.19/unisign-real-e2e/`):

| | short `g0uGWjwdOIw_1-8` (5.9 s) | long `FzmL8SL6Bow_1-8` (25.8 s) |
|---|---|---|
| Reference | *It got a lot to do with math and geometry, geometric designs.* | *You want to go and clean up that hole you just made… my hands are there.* (78 words) |
| Uni-Sign | *So, the main thing is that mathematics are involved in the design.* | *We're going to go ahead and put this on the bottom and we're going to go ahead and put this on the bottom and we're going to go ahead and take our rubber band and* (38 words) |
| WER / CER | 1.000 / 0.746 | 0.872 / 0.702 |
| BLEU / chrF | 0.00 / 21.80 | 2.48 / 20.51 |
| Same request, twice | **bit-identical** | **two different translations** (§15.3) |

**The short clip is the interesting one, and not for its score.** WER 1.000 with BLEU 0.00 is
the worst number on this page, and it is attached to the *only output in this entire document
that a human would call a correct reading* — "math and geometry, geometric designs" ↔
"mathematics are involved in the design". ⚠️ **This is a direct warning about every WER in
§11–§14:** at n=1, WER punishes a right answer in different words exactly as hard as a wrong
one. It does not retract any of those numbers — they are averages over 126–128 clips, where
this effect washes out — but it is the concrete counter-example to reading a single clip's WER
as a semantic verdict. The 09-15 matched-126 table remains the number to quote:

| System (matched-126, frozen benchmark) | WER | CER | BLEU | chrF |
|---|---|---|---|---|
| Curify / Gemini 3.6 | 0.9761 | 0.8070 | 0.13 | 11.30 |
| **Uni-Sign** | **0.9801** | **0.7601** | **5.40** | **22.83** |
| OpenSLT | 1.0246 | 0.7689 | ~0.96 | 18.59 |

**Now the part that matters for the product.** On 09-18 the same service was run against two
**real Curify user videos** — the first time any specialised ASL model has been pointed at our
own corpus rather than at How2Sign:

- `1477_recording_6.7s.mp4` (6.68 s) → *"One, two, three; one, two, three; …"* repeated ~16×,
  truncated at the 100-token cap.
- `1252_1000016397_76.8s.mp4` (77.5 s, the video that already failed in Curify's production
  pipeline) → *"One, two, three, four. One, two, three, four. …"* repeated ~12.5×, truncated.
  It covered **none** of the reference's six sentences and neither fingerspelled name.

⛔ **Read this as the headline of §15, not a footnote.** Uni-Sign's benchmark advantage over
our own pipeline (§11.3, and the table above) was measured entirely on How2Sign — studio-lit,
frontal, sentence-segmented, the distribution its checkpoint was trained on. Handed
phone-recorded user video, it **degenerated completely** on both clips. We have n=2 and no
references worth scoring against, so this is not a measurement; but it means **the 09-15 table
cannot be read as "Uni-Sign would be better than what we ship."** It has never been shown to
be better on the only distribution our users actually send. That comparison does not exist yet
and is the thing most worth building.

### 15.3 The mechanical cause: 256 frames, chosen at random, per request

Read directly out of the vendored code inside the running container
(`unisign_repo/datasets.py:640-641`), not inferred:

```python
if duration > max_length:            # max_length = 256
    idx = sorted(random.sample(range(duration), k=max_length))
```

- **Pose extraction processes every frame** — 618/618 on the long clip, 2283/2283 on the 77.5 s
  user video, no stride. It is the stage *after* it that throws frames away.
- Above 256 frames (**≈10.7 s at 24 fps**), only 256 survive, **sampled at random rather than
  at a uniform stride** — so the gaps are uneven. 41.4 % of the long benchmark clip reached the
  model; **11.2 % of the 77.5 s user video did.**
- `random` is Python's **global** RNG, seeded once at model load (`set_seed(42)`) and **never
  re-seeded per request**. Consequence, observed and not theorised: **the identical long clip
  posted twice to the same live process returned two different translations.** Below the cap
  there is no sampling, and output is bit-identical across runs.
- `max_new_tokens=100` is the same for a 6 s clip and a 77 s one. Neither long-clip output was
  cut off by it — both stopped early on their own, one on a dangling "and" — so the failure
  shape is **early EOS plus degenerate repetition**, not hard truncation.

⚠️ **This retroactively qualifies every Uni-Sign number in §11 and §15.2 for clips over ~10.7 s,
and it is a reproducibility bug of the same class as P0-5.** It does not affect the matched-126
table much — the frozen benchmark's median clip is 5.15 s and 77 % of it sits under the cap —
but any Uni-Sign result on a long clip is one draw from a distribution, not a measurement.

### 15.4 Segmentation fixes the mechanism and not the output

Task (b) tested the obvious response: cut the long clip up first. Boundaries came from **our
own production motion detector** — `_probe_motion` / `_segment_runs`, diffed against
`asl_utils.py` and found **identical in executable code** — targeting 6 s segments (4–8 s) with
~1 s overlap, all parameters fixed before any inference.

| | direct (whole video) | segmented (5 clips) |
|---|---|---|
| frames reaching the model | **256 of 618** (362 dropped at random) | **708 of 708** (90 = overlap) |
| segments hitting the 256 cap | 1 | **0** (max 174 frames) |
| same input twice | **different outputs** | identical |
| WER / CER | 0.872 / 0.702 | **1.180 / 0.815** |
| BLEU / chrF | 2.48 / 20.51 | 3.17 / **35.33** |
| output length (ref 78 words) | 38 words | 110 words |
| runtime | 101 s, 1 call | ≈221–249 s, 5 calls |

**What it fixed is real and mechanical:** the random frame drop is gone entirely, and
per-segment output became deterministic. **What it did not do is translate better.** The
segmented text covers the whole timeline and is mostly generic or hallucinated — a glass, a
wheel, rubber stamps, a pot, against a reference about a hole and the signer's hands. WER and
CER got *worse* (insertions from 1.41× the reference length); chrF rose 13–15 points, which is
what chrF does when output gets longer. Two further nulls worth recording: the ~1 s overlap
produced **zero duplicated text at all four junctions**, so the dedup merge was a no-op and
"naive concatenation" and "dedup" are the same string; and repeated 3-grams went *up*, 7–18 →
33. Classification: **B — no clear benefit yet**, n=1, not generalisable.

Two engineering facts survive regardless of the quality question:
- **The cap is in frames, not seconds.** 8 s is 192 frames at 24 fps, 240 at 30, 480 at 60. Any
  production rule must be `min(8 s, 256/fps)`.
- **Idle segments get translated anyway.** A ~3.5 s idle tail inside the last segment was turned
  into a confident sentence. Drop or merge idle-only spans instead of sending them.

### 15.5 Deployment readiness — the answer is no, and only one of the four reasons is code

PR #448's own test plan says *"do not merge"*. Concretely, between here and an Azure App
Service:

**1. ⛔ Licence — not an engineering blocker, and it gates everything.** The checkpoint
`how2sign_pose_only_slt.pth` is **CC BY-NC-4.0, non-commercial**. Curify is commercial. Worse,
the upstream Uni-Sign *code* repo **ships no LICENSE file at all** at the pinned commit, so
there is no explicit grant even to redistribute the vendored source. The service already
refuses to load the checkpoint without an explicit operator acknowledgement, which is the right
design and is not a substitute for permission. **No ACR push, no deployment, and no merge until
this is cleared.** Everything below is moot until it is. → **P0-8**.

**2. The checkpoint cannot get onto an App Service the way our other models do.** Every other
service in this repo either bakes weights into the image or pulls them from HF at boot.
Neither is available here: baking in is precisely what the licence forbids, and the checkpoint
is deliberately not auto-downloaded. That leaves a 1.19 GB volume mount, and **no service in
this repo uses Azure Files BYO-storage** — there is no pattern to copy. Two secondary mounts
come with it: the HF cache for mT5-base, and **~132 MB of rtmlib ONNX pose weights that
download from `download.openmmlab.com` on the first `/translate`** (≈13 s of cold start, an
outbound-network dependency, and lost on every container recycle — which App Service does
routinely).

**3. Sizing, against the plans we actually have.** Peak resident memory was **6.6 GiB of a
7.65 GiB limit** on a 25.8 s clip — about 1 GiB of headroom, on a clip a third the length of
the 77 s user video already in the corpus. The current estate:

| Plan | SKU | Apps |
|---|---|---|
| `curify-master-plan` | P0v3 — 1 vCPU / 4 GiB | `curify-video-translate` (running), `curify-whisperX` (**stopped**), `curify-xtts-v2` (**stopped**) |
| `curify-linux-plan` | P1v3 — 2 vCPU / 8 GiB | `curify-paddleocr` (**stopped**), `curify-worker` (running) |

P0v3's 4 GiB **cannot hold this model**. P1v3's 8 GiB fits with ~1 GiB spare and is the plan
already carrying the production worker. Latency is the other half: 101 s for a 25.8 s clip and
~25 minutes for the 77 s user video, both under amd64 **emulation** on Apple Silicon, so
neither number transfers to a native x86 server — but nothing has been timed natively, and
**Azure App Service caps an HTTP request at 230 s.** A synchronous `/translate` on a long clip
plausibly exceeds it. Size and time this on native x86 before choosing a plan.

**4. ⚠️ The `xtts` precedent does not point at Azure App Service.** `deploy-xtts.yaml` has three
jobs — build/push to ACR, deploy to App Service, **and deploy to a GCP VM** — and in production
it is the third one that is load-bearing: `curify-xtts-v2` and `curify-whisperX` are both
**Stopped**, and `curify_background/.env` points `XTTS_V2_API_URL` and `WHISPERX_API_URL` at
GCP VM addresses. Copying the yaml would produce a deployment target that xtts itself does not
use. The GCP VM path also happens to dissolve blocker 2 — `docker run -v` mounts a 1.19 GB
checkpoint from local disk without ceremony. **If a hosted Uni-Sign endpoint is wanted after
the licence clears, the VM is the shorter and better-precedented path; App Service is the
longer one and buys nothing here.**

**What is genuinely easy, for the record.** The backend side is small and is *not* the blocker.
`transcribe_asl(video_path, frame_budget, provider="gemini"|"openai")` already has a provider
switch, and the sidecar call pattern (a `settings.*_API_URL`, `requests.post` with an explicit
`(connect, read)` timeout and bounded retries) is sitting in `voiceover_utils.py`. Two real
details: the service's content-type allowlist is strict, so the upload must be sent as
`video/mp4` (a bare `curl -F` labels it `application/octet-stream` and gets a 415); and

⚠️ **the output contracts do not match.** Production consumes
`AslSegment(start, end, text)` and builds an SRT from it. Uni-Sign returns **one untimed
string**; the API's `segments[0]` is wrapper metadata — `start` is always 0.0, `end` is always
the clip duration, `source: "wrapper_derived"` — and the service says so in its own response.
**The time-segmentation shim is not a detail after the integration; it is the integration.**
→ **LHF-10**.

### 15.6 `gloss-free-asl-translation` — the pipeline runs, the model does not exist

`yyouretoast/gloss-free-asl-translation` @ `5b7eb92f`, **MIT** (so no licence problem here).
Brought up cleanly: dependencies install, **11/11 tests pass**, the Conformer + T5 model
constructs and `generate()` runs, and MediaPipe Holistic extraction works on the same two
How2Sign clips used above (141/141 and 618/618 frames, 3.7 s and 15.2 s on CPU, 0 NaNs).

**There is no trained ASL checkpoint, anywhere.** The code tree, 94 commits of history, Git
LFS, GitHub Releases (0), tags (0), the author's Hugging Face, the Kaggle notebook and every
link in the repo were all searched. README Results and Demo are "to be filled in after
training" placeholders. The only real weights are stock T5, which has never seen a sign. No
inference was run and **no evaluation numbers were fabricated** — the correct call.

Two findings worth keeping even so:
- **We are not MediaPipe.** We use `rtmlib.Wholebody()` (COCO-WholeBody, 133 points, 2D pixels,
  with scores). That repo uses MediaPipe Holistic (33 pose + 21 + 21 + 92-of-468 face, 3D
  normalised, 501 dims/frame). The formats are **not interchangeable**; an adapter is possible
  (shoulders and wrists agree to 1–2 % of frame size) but would lose z-depth and cannot map 68
  face points onto 92. None was built, and with no weights there is nothing to feed it.
- **Hand detection differs sharply on the same video.** On the long clip MediaPipe lost the left
  hand on 34.0 % of frames and the right on 40.6 %; RTMPose reported hands on all 618. ⚠️ That
  is not evidence RTMPose is more accurate — it always emits 133 points whether or not it can
  see them, and there is no ground truth here.

This does **not** contradict §14.2's D2 negative, and cannot be used to overturn it either: D2
scored *trajectory-text handed to a frozen generic Gemini* and returned 0/5. A trained temporal
encoder consuming landmarks directly is the path D2 explicitly said it had neither tested nor
ruled out. It remains untested, because the checkpoint does not exist.

**Status: parked with baobao**, who will source a checkpoint or reproduce the training at small
scale as a proof of concept. No action on this side; nothing in this section is a commitment to
train anything.

### 15.7 What this changes

- **P0-6 is now half-answered, and the half it answered was mechanical.** We know *a* reason
  Uni-Sign underperforms on long input — 59–89 % of frames discarded at random, plus a fixed
  100-token output cap. That does not explain the matched-126 result, where most clips are
  under the cap. The failure-shape analysis P0-6 actually asks for is still unrun, and is still
  the cheapest item on the board.
- **A new blocker outranks everything: P0-8**, licence clearance. Every deployment path, and PR
  #448's own merge, sits behind it, and no amount of engineering moves it.
- **A new experiment is worth more than another ablation: P0-9.** Both n=1 long-clip results
  above are unscoreable for the same reason — there is no segment-level gold. Concatenating
  consecutive How2Sign sentence clips (which are already sentence-segmented, with per-sentence
  references) manufactures long videos with known boundaries *and* known per-segment
  references, which would turn "segmentation: no clear benefit" into an actual measurement.
- **The most valuable unbuilt comparison is not on How2Sign at all.** §15.2's user-video
  degeneration is the single most decision-relevant observation in this record, and it rests on
  two clips with no scoreable references. §5's corpus plus LHF-6's annotations is the way to
  make it a measurement.
- **Order of work, revised:** **P0-8** (licence — unblocks or kills the whole branch) → **P0-6**
  (free, no new runs) → **P0-2**, **P0-3** (both still overdue from §11) → **P0-9** →
  **LHF-10** (only if P0-8 clears) → P0-5, P0-7, P0-4's remaining 7, LHF-9 as billing allows.
- **Unchanged:** production still runs the §2 Gemini configuration, still flags every job
  `asl_unverified`, and none of §15 alters any accuracy claim this document makes. **No open
  model has yet been shown to be better than what we ship on the video our users send.**

## 16. Change record — 2026-09-21 (the licence clears; the evidence does not)

**Source:** reply from **Zecheng Li**, first author of Uni-Sign (USTC), received 2026-09-21 in
Jay's inbox, answering the request sent 2026-09-20 (Message-ID
`<178986621303.87952.3059592973119869558@curify-ai.com>`, script
`curify-gtm/gtm_tools/send_unisign_license_request_2026_09_20.py`). The operative sentences are
quoted verbatim in **§7 P0-8**, with the layer-by-layer reading. Artifact state independently
checked against the HuggingFace and GitHub APIs on 2026-09-21. ⚠️ The email has **no path on
disk** — it is the only artifact the grant exists on (LHF-12). **Nothing shipped, no code
changed, production is unchanged.**

**P0-8 sat above the entire queue since 09-19, and it is now closed.** It was answered in the
way this kind of item usually is not: by asking the person, and getting more than was asked for.

### 16.1 What was granted, and what was not

| | Before 09-21 | After |
|---|---|---|
| Use the checkpoint commercially | ⛔ CC BY-NC-4.0 | ✅ granted in writing |
| **Redistribute** the checkpoint (ACR, baked image, VM copy) | ⛔ the specific blocked act | ✅ granted in writing |
| Redistribute / patch the vendored **code** | ⛔ no LICENSE = no grant | 🟡 MIT stated as intent; **file still absent** at the pinned commit |
| Redistribute **How2Sign** clips or derivatives | ⛔ CC BY-NC 4.0 | ⛔ **unchanged** — third-party, they cannot re-license it, separate ask required |
| Credit | not required | ✅ **required** — a link to the Uni-Sign GitHub wherever it ships |

The middle row is the one to watch. The email is an unambiguous statement of intent from the
person with standing to give it, but the artifact a future auditor opens still reads **NC**, and
a LICENSE added to `main` next month does not appear at `eed438bc…`. **LHF-12** closes both.

### 16.2 What this mechanically unblocks

PR #448 becomes mergeable in principle; the ACR push stops being a redistribution question;
**LHF-10** stops being blocked; and the P0-8 build-path analysis stops being about permission
and becomes ordinary engineering guidance (which it should have been all along — its four
reasons never depended on the licence).

What it does **not** unblock: **P0-9 was never blocked by this** — building segment-level gold
from concatenated How2Sign clips is internal use and always was. It stays where it is in the
queue on its own merits.

### 16.3 Why the order of work does not change

The temptation here is to treat a cleared blocker as a green light, and the evidence does not
support that. Three results in §15 are wholly untouched by a licence:

- **§15.2 — on real Curify user video, Uni-Sign degenerated completely**, repeating "One, two,
  three…" on both clips. Its entire advantage over our own pipeline has only ever been shown on
  How2Sign, which is not the distribution our users send.
- **§15.4 — segmentation, the fix that makes long clips tractable, produced no quality gain**
  at ≈2.2× cost.
- **§15.3 — long-clip Uni-Sign output is not reproducible** at all until someone seeds the RNG.

So the head of the queue stays **P0-6** — still free, still unrun, still the cheapest item on
the board — followed by P0-2, P0-3 and P0-9. The two new items (**LHF-11**, the measurements we
owe; **LHF-12**, the paperwork) are cheap and should be done promptly because they are debts,
not because they advance deployment. **LHF-10 is worth building only once someone decides a
deployment is actually happening.**

### 16.4 If a deployment is decided, the target is a GCP VM — not another App Service

> **Historical recommendation.** §17.4 rechecks the actual Azure plans and rules
> out current co-hosting on measured capacity. A separate runtime remains required;
> the old statement below that a GPU “buys nothing” does not apply to the official
> CUDA P0-12 experiment. No hosting target was provisioned on 10-12.

Asked directly on 09-21: *does this need another service app?* **No — and specifically, not an
Azure App Service.** That half of this repo's deployment story is not what production runs
([[ml-sidecar-services-run-on-gcp]]). Every `deploy-<service>.yaml` has three jobs — ACR
build/push, App Service deploy, and GCP VM deploy over SSH — and it is the **third** that is
load-bearing: `curify-xtts-v2`, `curify-whisperX` and `curify-paddleocr` App Services are all
**Stopped**, while `curify_background/.env` points `XTTS_V2_API_URL` and `WHISPERX_API_URL` at
**two different GCP VMs** (`secrets.GCP_VM_HOST`, CPU, xtts; `secrets.GCP_VM_GPUHOST`, GPU,
whisperx), each running its container on `-p 8000:8000`.

For Uni-Sign specifically, App Service is not merely unprecedented — it is a bad fit on four
independent counts already established in §15.5: `curify-master-plan` is P0v3 / 4 GiB and
**cannot hold a 6.6 GiB peak**; `curify-linux-plan` is the P1v3 / 8 GiB plan **already carrying
the production worker**, leaving ~1 GiB spare on a clip a third the length of a real user video;
the **230 s request cap** sits against 101 s for 25.8 s of video and ~25 minutes for the 77 s
user clip (both emulated, neither timed natively); and there is **no volume-mount pattern
anywhere in this repo**, so weights that should not live in an image have no App Service story
without new Azure Files BYO-storage plumbing.

**What it actually takes, if and when it is decided:**

1. **A `deploy-unisign.yaml` with two jobs, not three** — `build-and-push` to ACR and
   `deploy-to-gcp`. Copy `deploy-xtts.yaml` and **delete the `deploy-to-azure` job** rather than
   carrying it dormant; a dormant job is exactly how the xtts precedent became misleading in the
   first place.
2. **A VM decision that needs a measurement first.** Uni-Sign is CPU-only (pose-only, torch CPU),
   so the GPU VM buys nothing. Co-tenanting on the xtts CPU VM means a **different host port** —
   8000 is taken — and enough free RAM for a 6.6 GiB peak measured on a 25.8 s clip. ⚠️ **Check
   free memory on that VM before assuming it fits**; nothing in this document establishes that it
   does, and the one real user video in §5 is 77 s.
3. ⚠️ **Co-tenancy hazard.** `deploy-xtts.yaml`'s VM script runs `sudo docker system prune -af`
   on every deploy. A *running* Uni-Sign container keeps its image alive; a **stopped** one loses
   it and fails to restart on a missing image. Either give Uni-Sign its own VM or narrow that
   prune before sharing.
4. **The checkpoint still stays out of the image** — now as build hygiene rather than permission.
   `scp` it to the VM once, `docker run -v /opt/unisign/ckpt:/models:ro`. P0-8's four reasons
   (provenance, `linux/amd64`, image size, ACR credentials on a laptop) are unaffected by the
   grant, and the VM path dissolves the mount problem that made baking it in tempting.
5. **`UNISIGN_API_URL` in `.env`**, alongside `XTTS_V2_API_URL` and `WHISPERX_API_URL`, called
   with the `voiceover_utils.py` pattern — explicit `(connect, read)` timeout, bounded retries —
   through `transcribe_asl`'s existing `provider=` switch. This is the small part, and §15.5
   already says so.
6. **Do not make it a synchronous request.** A VM has no 230 s cap, but ~25 minutes for a 77 s
   clip is not an HTTP request under any timeout — it is the worker queue's job, and a silent
   stall there has bitten this estate before ([[worker-queue-stall-2026-09-08]]).
7. **The credit line ships with it** (P0-8's obligation, LHF-10 item 7), and the upload must be
   labelled `video/mp4` or the service's strict allowlist returns 415.

⚠️ **None of this is a recommendation to do it.** The honest reading of §15 is that a hosted
Uni-Sign endpoint is justified today only as an **internal evaluation endpoint** — which removes
the local-laptop bottleneck for P0-6 and P0-9, needs no user-facing decision, and is the one
version of this that the evidence supports. Putting it in front of users is §15.2's call, and
§15.2 says no.

### 16.5 "Should we migrate to Uni-Sign?" — asked and answered 2026-09-21

Asked directly on the day the licence cleared, which is the right day to ask it. **No — and
the licence was never what was holding it back.** Recording the reasoning here so it is not
re-derived from five scattered sections next time.

**The honest case for, which is one column of one table** (matched-126, §15.2): BLEU **5.40**
against our **0.13**, chrF **22.83** against **11.30**, CER **0.7601** against **0.8070**.
That is ~40× on BLEU and 2× on chrF, it is real, and it is why the service in PR #448 was
worth building at all. It is also the *entire* case.

**Five things against it, each already measured:**

1. **It has never been shown better on the distribution our users actually send.** Handed two
   real Curify user videos (§15.2), it degenerated completely — `1477` (6.7 s) into
   *"One, two, three; one, two, three…"* ×16, and `1252` (77.5 s) into
   *"One, two, three, four…"* ×12.5, covering **none** of the reference's six sentences and
   neither fingerspelled name, both truncated at the 100-token cap. The matched-126 advantage
   was measured entirely on How2Sign: studio-lit, frontal, sentence-segmented, the
   distribution its own checkpoint was trained on. ⚠️ n=2 with no scoreable reference, so this
   is **not** a measurement — but it is the only evidence that exists on our data, and it
   points the wrong way.
2. **Migration swaps one unusable system for another.** WER 0.9761 → 0.9801: it does not move,
   and it does not move because both systems are far below usable. Field SOTA on How2Sign is
   **12.39 BLEU** (§1 / §8), production MT is 40–50, and **§8's bar for reopening the model
   question is ~25 BLEU**. Uni-Sign's 5.40 is ~2.3× short of the field and ~5× short of the
   bar. Nothing about switching gets a user a transcript they can trust.
3. **It cannot produce what production consumes.** Production builds an SRT from
   `AslSegment(start, end, text)`; Uni-Sign returns **one untimed string**, and its
   `segments[0]` is wrapper metadata that says so in its own response. The time-segmentation
   shim *is* the integration (**LHF-10**) — and §15.4 built exactly that shape and found **no
   quality gain at ≈2.2× cost**.
4. **Long-clip output is not reproducible.** Above 256 frames (~10.7 s at 24 fps) the excess is
   discarded at random by an unseeded global RNG (§15.3), so identical clips return different
   translations. One line fixes it (LHF-10 item 2), but until someone writes that line every
   long-clip Uni-Sign number is a single draw.
5. **Operationally it is a step down** from a hosted API call: 6.6 GiB peak resident, ~101 s
   for a 25.8 s clip and ~25 minutes for the 77 s user video (both emulated, neither timed
   natively, §15.5), and a hard 100-token output cap that truncates long output regardless of
   quality.

⚠️ **One caveat that cuts in Uni-Sign's favour, and does not rescue it.** The single output in
this entire document that a human would call a correct reading — *"mathematics are involved in
the design"* against *"math and geometry, geometric designs"* — scored **WER 1.000 / BLEU
0.00** (§15.2). At n=1 these metrics punish a right answer in different words exactly as hard
as a wrong one. That is a real warning about every per-clip number here. It does not touch the
126-clip averages, where the effect washes out, which is why those are what this verdict rests
on.

**What would change the answer, in cost order:**

- **P0-6 — free, artifacts on disk, still unrun.** Does Uni-Sign's BLEU 5.40 concentrate in a
  minority of clips it genuinely gets right, or is it spread thinly across clips it gets
  wrong? If it concentrates, a routing or hybrid story exists and this verdict is provisional.
  If it is spread, the 40× is a formatting artifact and the verdict hardens.
- **The comparison that does not exist yet** — Uni-Sign against Curify on **our** corpus with
  real references, which needs **LHF-6**'s annotations plus §5. §15.2 already calls this "the
  thing most worth building" and it is what would make point 1 a measurement instead of an
  observation.
- **P0-9** — segment-level gold, which turns §15.4's "no clear benefit" into a number.

**Where to look, if re-checking this by hand.** The per-clip comparison instrument is the frame
inspector (§14.4) — reference · Curify frame baseline · Uni-Sign · Gemini native video, side by
side, word-level diffs and per-system WER/CER, read-only from each system's frozen
`per_clip_results.json`:
`visual-search-adhoc @ baobao/asl-temporal-ablation-2026-09-06`,
`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/index.html`
(last updated `01cfd05`, 2026-09-10). ⚠️ **It covers the 12 diagnostic clips, not the 128**,
and it **predates the real-checkpoint work** — no user-video degeneration, no E2E, no
segmentation. Those are markdown only: `docs/daily_report/9.15/ASL_COMPLETE_WORK_REPORT.md`
(the matched-126 scorecard, the number to quote) and `docs/daily_report/9.19/unisign-real-e2e/`
+ `9.19/unisign-overlapping-segmentation/`. **No artifact consolidates the 09-15 and 09-19
results into one per-clip sheet**, and the 09-04 scorecard linked at the top of this file is
stale for this question — it predates every real-checkpoint Uni-Sign number.

### 16.6 What this changes

- **P0-8 ✅ closed.** The first blocker in this workstream resolved by asking rather than by
  measuring, and the answer was more generous than the request.
- **Two new debts, both cheap: LHF-11** (send the 256-frame finding and the scorecards we
  promised — they asked for them by name) and **LHF-12** (get the grant onto the HF card and a
  LICENSE file; archive the email).
- **One new hard constraint: attribution.** A credit link is now a condition of use, folded into
  LHF-10 so it is not rediscovered at ship time.
- **One constraint explicitly *not* lifted: How2Sign.** The benchmark and anything derived from
  it stay private. This is the same rule §5 already applies to user video, for a different
  reason.
- **Unchanged:** production still runs the §2 Gemini configuration, still flags every job
  `asl_unverified`, and nothing in §16 alters a single accuracy claim in this document. **The
  licence was never what made Uni-Sign unshippable — §15.2 was.**

---
---

## 17. Change record — 2026-10-12 (Baobao's October evidence; production-default backend switch)

**Source:** [Baobao's consolidated work report, updated 2026-10-11](https://github.com/super-inbox/visual-search-adhoc/blob/0c90285e7dc6713dc32ebbb5391f181a5cbd10ea/docs/daily_report/10.09/asl-p0-11-12-13-work-report/WORK_REPORT.md),
branch `baobao/visual-production-research-2026-10-05`, pinned at
`0c90285e7dc6713dc32ebbb5391f181a5cbd10ea`. This update reads existing results; it
does not rerun training or checkpoint inference.

### 17.1 P0-11 complete: more supervised data did not solve the landmark baseline

Same initialization, 10,320-step compute budget, fixed validation/frozen splits:

| Training clips | Frozen-147 BLEU | chrF | Distinct predictions /147 |
|---|---:|---:|---:|
| 2,751, same-init control | 0.80 | 10.60 | 63 |
| 6,605 | 1.15 | 12.37 | 73 |
| 13,210 | 0.54 | 12.25 | 35 |
| 26,419 | 0.52 | 9.51 | 29 |

The control finished on **10-11**, removing the initialization confound. No BLEU
gain is significant: the best size gains +0.36, 95% CI [−0.28, 1.01]. Loss falls
but dependence on video stays near zero (shuffled-video loss gap 0.05–0.07).
The older “BLEU halves” and “102 → 29 distinct predictions” comparisons partly
measured initialization; use the controlled numbers above instead.

Scope: one seed per condition, fixed compute (larger sets see fewer epochs),
and supervised How2Sign scaling for this model/recipe. This does **not** establish
that broad sign-language pretraining data is unhelpful.

### 17.2 P0-12 complete on T4/fp16 — updated 2026-10-16

The 10-12 diagnostic separated subset difficulty (authors' released predictions:
14.50 BLEU-4 on 2,349 clips versus 9.59 on the hard 128) from our path's historical
5.39. Those cross-runtime numbers motivated the experiment, not its final contrast.

All four conditions have now run on the same 128 clips, checkpoint and T4/fp16
inference path: official poses **9.13**, our original path **5.47**, aspect correction
**5.80**, our extractor with official timing/crop **8.61** BLEU-4. The joint
preprocessing fix recovers **85.7%** of the matched-runtime gap. Timing and crop are
not isolated, no seed/CI analysis was run, and this is not official bf16 reproduction.
The old “CUDA inference still pending” priority is closed. Full interpretation and
pinned evidence: **§18.2**. Production input preparation is not thereby implemented.

### 17.3 P0-13 complete: representation helps at fixed downstream supervision

Same 2,751 supervised clips, frozen-147 at validation-selected checkpoint:

| Input representation | BLEU | chrF | WER | Distinct predictions |
|---|---:|---:|---:|---:|
| MediaPipe landmarks | 1.023 | 11.121 | 1.025 | 102/147 |
| Frozen Uni-Sign features | 3.249 | 17.049 | 0.939 | 147/147 |

ΔBLEU **+2.23 [1.28, 3.39]**, ΔchrF **+5.93 [4.66, 7.34]**. Video-shuffle
Δloss grows from 0.067 to 1.280. A timing-matched 128-clip check retains
+2.18 BLEU [1.03, 3.44], though timing/crop explains part of the raw gain.

This supports representation as a bottleneck, not a claim of usable translation.
The Uni-Sign encoder had far more pretraining and saw the downstream validation
pairs during How2Sign fine-tuning; frozen-147 is the uncontaminated endpoint.
Architecture versus pretraining is not isolated, seeds are not replicated, and
How2Sign test shares signers with train. Do not compare these frozen-147 figures
directly with the historical matched-126 scorecard.

**Model decision:** Uni-Sign is the strongest tested research base in this workstream.
It is not proven better on customer uploads. The October experiments include no
new real-user evaluation; that does not erase §15.2's earlier qualitative
real-user degeneration. Repetition and long-input truncation remain unresolved.

### 17.4 Hosting check — current App Service capacity does not meet the condition

Read-only Azure inventory and metrics checked **2026-10-12**:

| Plan | SKU / capacity | Running workload | Finding |
|---|---|---|---|
| `curify-master-plan` | P0v3, 1 instance, 1 vCPU / 4 GB | `curify-video-translate` | Below the previously measured 6.6 GiB inference peak |
| `curify-linux-plan` | P1v3, 1 instance, 2 vCPU / 8 GB | `curify-worker` | Insufficient measured spare memory for co-hosting |

Azure Monitor `MemoryPercentage` / `CpuPercentage`, hourly Average+Maximum,
**2026-10-11 00:00 → 2026-10-12 05:00 UTC**: worker-plan hourly average memory
**61.18–79.05%**, peak **92%**; CPU peak **98%**. Latest complete hour's memory
average is 61.18% (~3.1 GB nominal spare), while peak usage leaves ~0.64 GB.
These are plan-level measurements, not a new Uni-Sign load test. Either is
inadequate against the historical **6.6 GiB** container peak on a 25.8-second
clip (§15.5). Short-window memory and native x86 latency still need measuring.

SKU sizes: [Azure App Service pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/windows/).
Correction to the earlier blanket “230 s” statement: Microsoft's current
[request-timeout documentation](https://learn.microsoft.com/en-us/troubleshoot/azure/app-service/web-request-times-out-app-service)
distinguishes about **230 s on Windows / 240 s on Linux**. A worker calling a
remote synchronous endpoint is still subject to that endpoint's HTTP timeout.

**Decision:** no checkpoint download/load into these production apps, no resize,
no service deployment, and no switch. A separately sized runtime is required.
A CUDA runtime could also unblock P0-12; the fact that the older bridge can run
on CPU does not mean a GPU has no value. Size and benchmark the chosen runtime
before committing to it; no new paid infrastructure was provisioned.

### 17.5 Implemented locally: explicit switch, unchanged production default

`curify_background/app/config.py`:

| Setting | Default | Meaning |
|---|---|---|
| `ASL_RECOGNIZER` | `current_prod` | Existing Gemini recognizer; alternative `unisign` |
| `UNISIGN_API_URL` | unset | Private service base URL; required only for Uni-Sign |
| `UNISIGN_API_TOKEN` | unset | Optional bearer token for an authenticated gateway |
| `UNISIGN_CONNECT_TIMEOUT_SEC` | 10 | Connection timeout |
| `UNISIGN_READ_TIMEOUT_SEC` | 180 | Per-window service read timeout |
| `UNISIGN_MAX_VIDEO_DURATION_SEC` | 120 | Experimental-path limit only |

The pipeline's recognition step dispatches through `app/utils/asl_backend.py`;
translation, subtitle generation, muxing and the current production recognizer
are reused. There is **no automatic fallback** between models.

The opt-in adapter sends sequential 8-second, 24-fps MP4 windows (at most 192
frames each) to the real-checkpoint service's `POST /translate`. It validates
the response's model/checkpoint/upstream identity, rejects empty/malformed output,
and fails the whole job if any window fails. Queue retry policy owns transport
retries; config errors are terminal operator errors, never “no signing detected.”

Window timestamps are **wrapper-derived coarse intervals**, not word or sentence
alignment. Fixed windows avoid the upstream >256-frame random subsampling path,
but **do not fix signer cropping, sentence boundaries or establish a quality gain**.
The October canonical preprocessing decision remains open.

All outputs retain `asl_unverified` and `review_required`. Uni-Sign also sets
`asl_experimental` / `asl_low_confidence`, records model and timestamp provenance,
and includes **“Powered by Uni-Sign: https://github.com/ZechengLi19/Uni-Sign”**
in the first translated caption and runtime metadata. Sampled-frame counters
belong to the production sampler; on Uni-Sign they remain zero, not a measurement
of pose frames. The recognizer/timestamp fields distinguish the two.

**Checkpoint/inference prerequisite — concrete existing implementation, not hosted yet:**
[PR #448](https://github.com/super-inbox/curify-studio/pull/448) is still **open, draft,
unmerged**, head `54259128e8f10b21cd640cc848b0c470064a5235` as checked today.
Its `uni_sign_server/app/unisign_bridge.py` loads and executes the released checkpoint,
rather than calling a VLM or returning canned text. The adapter targets that contract;
the service code is not merged by this change.

- Upstream code pin: `eed438bcb49e30405cd6ccdfcccca330c134e830`.
- [Official checkpoint repository](https://huggingface.co/ZechengLi19/Uni-Sign):
  `how2sign_pose_only_slt.pth`, **1,186,925,007 bytes**;
  SHA-256 `1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`.
- Runtime-mounted checkpoint plus mT5-base assets and RTMPose/rtmlib ONNX weights;
  no checkpoint in git or the backend image. §16's written permission/attribution
  applies; the How2Sign dataset is not covered by that permission.
- Before hosting, harden the draft bridge: checksum mismatch must fail (currently
  only warns), serialize inference/model concurrency, retain model.eval(),
  verify readiness with real weights, and apply the validated preprocessing path.
  Response metadata alone is **not** cryptographic proof of loaded weights.
- Historical real-checkpoint E2E evidence is §15.1, **not a new validation of this adapter**.

**Later activation:** provision and validate the private checkpoint runtime first;
confirm capacity under concurrent production load and P0-12/canonical preprocessing,
then run a real-checkpoint adapter smoke test and held-out/human evaluation. Set
`UNISIGN_API_URL` (and gateway token if required), then explicitly set
`ASL_RECOGNIZER=unisign` on the worker and restart it. Do not expose the draft
unauthenticated service publicly. Roll back by setting `ASL_RECOGNIZER=current_prod`
and restarting; in-flight jobs may finish with the backend they already selected.
Old terminal-failure dedup records are not automatically cleared by the flag;
use a new evaluation upload rather than treating a cached verdict as a new run.

Validation for this change covers routing, window bounds, cleanup, error/no-fallback
behavior and metadata contracts with a mocked HTTP service, plus real ffmpeg
segmentation of an 8.5-second, 60-fps synthetic video into 192/12-frame windows.
Pipeline tests preserve the unverified notice, attribution and backend provenance.
No new checkpoint
inference, accuracy measurement or production deployment is claimed.

---

## 18. Research review — 2026-10-16 (Uni-Sign diagnosis, probes and fusion)

**Reviewed branch:** `baobao/visual-production-research-2026-10-05`; its current head
matches the supplied commit **`c38497b2e3f90d0bdaaa3554c32705435eea956f`**.
This is a source/report/compact-metric review, not a training or GPU-inference rerun.
No research code is merged into the product by this documentation update. Existing
local changes to §17 and the backend adapter are preserved.

Pinned sources (all in `super-inbox/visual-search-adhoc`):

- [Manager summary](https://github.com/super-inbox/visual-search-adhoc/blob/c38497b2e3f90d0bdaaa3554c32705435eea956f/docs/daily_report/10.16/UNISIGN_P0_MANAGER_SUMMARY.md).
- [P0-11/13 training report](https://github.com/super-inbox/visual-search-adhoc/blob/c38497b2e3f90d0bdaaa3554c32705435eea956f/docs/daily_report/10.09/asl-p0-11-12-13-work-report/WORK_REPORT.md).
- [P0-12 controlled results](https://github.com/super-inbox/visual-search-adhoc/blob/c38497b2e3f90d0bdaaa3554c32705435eea956f/docs/daily_report/10.13/asl-p0-12-full128-fp16/P0_12_RESULTS.md).
- [Failure/intervention summary](https://github.com/super-inbox/visual-search-adhoc/blob/c38497b2e3f90d0bdaaa3554c32705435eea956f/docs/daily_report/10.15/UNISIGN_FAILURE_ANALYSIS_SUMMARY.md).
- [Taxonomy and manual-review status](https://github.com/super-inbox/visual-search-adhoc/blob/c38497b2e3f90d0bdaaa3554c32705435eea956f/docs/daily_report/10.13/asl-unisign-error-taxonomy/ERROR_ANALYSIS_REPORT.md).
- [P0-14 full report](https://github.com/super-inbox/visual-search-adhoc/blob/c38497b2e3f90d0bdaaa3554c32705435eea956f/docs/daily_report/10.15/asl-unisign-representation-probe/FULL_RUN_REPORT.md).
- [P0-15 results](https://github.com/super-inbox/visual-search-adhoc/blob/c38497b2e3f90d0bdaaa3554c32705435eea956f/docs/daily_report/10.16/asl-unisign-high-precision-fusion/P0_15_RESULTS.md).

### 18.1 What was trained, and how it differs from Uni-Sign

| System / experiment | What changes or learns | What the evidence establishes |
|---|---|---|
| Released Uni-Sign | Pretrained pose-only sign representation + its How2Sign-fine-tuned mT5-Base decoder | Research baseline; not newly trained by this work |
| Earlier custom translator, P0-11/13 | MediaPipe landmarks → 4-block Conformer → MLP bridge → t5-small; P0-13 replaces the input with frozen 768-d Uni-Sign features, still trains our downstream model | Frozen-147 BLEU 1.023 → 3.249; an improvement over our weak baseline, not over Uni-Sign |
| P0-12 and inference interventions | Same released checkpoint; change input preparation, decode cap, cleanup or chunking | Diagnosis/inference changes, no model training |
| P0-14 | Freeze Uni-Sign; train linear concept probes on pooled raw pose, Fsign, or mT5 encoder states | Tests lexical information, not sentence translation |
| P0-15 | Freeze those probes and translation; train an 11-feature logistic verifier on dev | Tests whether concept additions can be trusted; no end-to-end fusion training |

P0-13's report gives Uni-Sign's own decoder as context: 6.38 BLEU with greedy decoding
and 9.04 with beam 4, versus our 3.249 on frozen-147. This is not a controlled decoder
ablation: pretraining, decoder capacity and supervision differ. P0-13 also changes
augmentation; its representation gain is not an isolated architecture effect.
**“We trained a better Uni-Sign” is not supported.** The later P0-12/14/15 work did
not retrain its translation checkpoint. The T4 VM did execute extraction/inference
(P0-14: 33,295 feature records; 2,209 decoded clips); probes/verifier ran on CPU.

### 18.2 P0-12: close the preprocessing diagnosis, not the production-quality gate

| Same frozen-128, T4/fp16 | BLEU-4 |
|---|---:|
| Official poses, official timing/crop | 9.13 |
| Our extractor, old timestamps/full frame | 5.47 |
| Same, aspect/coordinate correction | 5.80 |
| Our extractor, official timing/crop | 8.61 |

Joint timing/crop/normalization recovery is **85.7%**, using full-precision values
(8.60817 − 5.47351) / (9.13194 − 5.47351). The residual pose-source contrast is +0.52.
Single run, no CIs; small deltas may be noise. Official bf16 and these fp16 values
must not be conflated. Timing and crop effects cannot be separated.

**Practical implication:** prioritize reliable signing boundaries and signer crops
before replacing the pose extractor. Official realigned boundaries are benchmark
inputs: a customer-upload pipeline must produce them without reference text or
manual benchmark annotations. This experiment does not demonstrate that capability.

### 18.3 Fusion: complementary signal exists, usable improvement does not

P0-14 uses 2,209 clean test clips, 24 lexical concepts and English-reference-derived
labels. Macro-F1: raw pose **0.125**, Fsign **0.256**, mT5 states **0.416**, Uni-Sign's
translation **0.548**. mT5 at 10% probe labels reaches **0.338**. These are concept
metrics, not BLEU or sentence accuracy. Its formal code verdict is **PARTIAL SUPPORT**,
subject to the sanity-gate qualification in §18.5.

- Translation misses 498/1,032 positive concept cells. mT5 recovers **90**, but adds
  **581 false positives**: addition precision **13.4%**. Naive OR fusion loses **6.2
  macro-F1 points** versus translation alone. AUROC 0.780 among translation-absent
  cells demonstrates ranking signal, not a sufficiently precise operating point.
- P0-15 dev: **1,052 clips / 75 video units**, 24,782 candidates, only **234 positives
  (0.94%)**. Naive union adds 331 concepts: **50 right, 281 wrong, net −231**;
  micro-F1 falls **7.0 points**, micro-precision **19.4 points**.
- The verifier improves dev ranking (AP **0.110** vs raw margin **0.094**; top 20
  **11 correct** vs **7**). But its best Wilson-90% lower bound is **0.393**, below
  the frozen 0.50 requirement with at least 10 additions. Both guarded arms abstain.
- **P0-15: NOT SUPPORTED at dev stage.** No final metrics and no fused sentence
  output; no sentence BLEU/chrF gain. Dev dry-run metrics are not held-out results.

**Why “Uni-Sign + fusion should improve” is a hypothesis, not a consequence:** the
new branch must correct errors the baseline actually makes, with sufficiently few
new errors. These branches reuse the same pose information; difficult concepts often
fail in both. Pooling also discards temporal alignment, and lexical labels do not
encode negation, argument roles or fluent sentence construction. Better features or
AUROC alone cannot guarantee better translations. The current experiment tests a
narrow *concept-addition* form of late fusion, not every possible multimodal or
jointly trained fusion architecture. Decoder confidence and stronger temporal or
visual evidence are candidates for a new experiment, not demonstrated remedies.

### 18.4 Category analysis: what exists and what can guide iteration

**Two distinct analyses exist:** (1) 128-clip heuristic linguistic/visual taxonomy;
(2) 24 lexical concept scores on 2,209 clips. Neither is an ASL-fluent video review.
The committed 45-clip manual queue has **45 PENDING**, with no completed review.
No broad A_official category penalty survives length matching and Bonferroni
correction. That is insufficient evidence to rank true ASL failure categories, not
proof that categories have equal quality.

| Observation | Evidence | Implication / limit |
|---|---|---|
| Main error mass is content substitution | 67/128 heuristic primary labels; hallucination candidates 26, repetition 18, omission 13, over-generation 4 | Add semantic adequacy/hallucination review, not merely length metrics; these counts are automated proxies |
| Weak rare-entity recovery | 2/21 rare names/acronyms reproduced | Prioritize video review; English names do not establish fingerspelling |
| Polarity/question concerns | Negation absent in 7/13; question mark absent in 10/13 | Verify signed polarity and non-manual markers; punctuation is not question comprehension |
| Shared hard concepts | Translation F1: TURN .21, PULL .28, PLACE .31, PIECE .35, CUT .38; mT5 probe .11–.20 on these | Current specialist does not selectively repair the weakest baseline classes; prioritize temporal/context/error review before another pooled head |
| Small concept-level exceptions | TYPE probe F1 .48 vs translation .44; SHOW .64 vs .62 | Exploratory candidates only; no validated concept-specific fusion gain, and small counts/multiple comparisons apply |
| Long outputs end early | Cap 100→150→256 leaves 126/128 strings unchanged | Stop treating the inference cap as the cause. A training-target 50-token prior is plausible but untested |
| Chunking increases recall but adds content | 21 long-reference clips: chrF +10.4; 15 controls: output length ≈1.58×, WER +42.3 points | Frame count is not linguistic content; reference-length-defined groups are diagnostic, not a deployable router |

Simple repetition cleanup failed both pre-metric guards and covered only 3/18 loops;
all chunking arms failed the control safety criterion. Do not keep tuning these same
128 clips or claim the old taxonomy's decode-cap hypothesis remains untested.

### 18.5 Review findings and next decision

1. **Sanity-gate interpretation must remain qualified.** P0-14 shuffled-label AUROC
   is **0.53017**, outside [0.47, 0.53]. The plan's S1 row says no interpretation on
   failure, whereas `analyze_probe.py` lines 140–141 allows PARTIAL from C1/C2 alone.
   The full report discloses this ambiguity; the manager summary compresses it.
   Preserve the failed gate and reported verdict. Reconcile the specification before
   another run; a separately labeled multi-seed diagnostic must not retroactively
   turn the original result into a pass.
2. **“Final labels were never read” is too strong.** P0-15 `build_cells.py` reads
   all test-clean labels and references and asserts matcher equality before splitting
   output rows; `build_split.py` uses reference-positive counts for balancing. P0-14
   already analyzed these same clips in aggregate. `fit_dev.py` does exclude final
   clips, and the committed artifacts/report show no final evaluation. Accurate
   wording: **no P0-15 final scoring or verifier fitting on final labels; not a
   pristine, never-accessed holdout**. This is a provenance/documentation finding,
   not evidence of a positive-result leak. Keep final evaluation unused; use a fresh
   untouched set for a strong confirmatory claim after further design iteration.
3. **Reproduction remains bounded.** Key scripts depend on the author's absolute
   `~/Desktop/curify/...` paths; bulk features/scores are external with checksums.
   The review verified compact JSON counts and scripts, not those external artifacts
   or full numerical reproduction. No GPU rerun or final-label evaluation was made.

**Recommended sequence (review judgment, not completed work):**

- Complete the existing 45-clip ASL-fluent video review: verified sign category,
  critical meaning error, and whether A/C agree. Keep ordinary/control clips so a
  targeted fix is also tested for harm. Use this to choose one specialist target.
- Implement/validate reference-free input preparation on fresh customer-like clips;
  report semantic adequacy, concept precision/recall and sentence metrics together.
- Pause this version of fusion. If continuing, freeze a new dev-only experiment
  using Uni-Sign output plus mT5 evidence and a stronger reliability feature, e.g.
  decoder scores. Require precision/coverage and abstention gains before attempting
  sentence correction; then compare actual fused sentences against unchanged
  Uni-Sign on held-out video-disjoint data. Do not presume confidence is calibrated.
- If early EOS remains a priority, separately test target-length fine-tuning with
  matched compute/data and long/short controls. No such fine-tuning has run yet.

**Decision:** useful research progress, no new winning translation model, no proven
fusion gain and no production switch. The meaningful next investment is better
error labels and genuinely complementary evidence, not more threshold search on
already-inspected benchmarks.

---

# Appendix A — original project spec (2026-06-14) + the 08-16 evaluation note

*Preserved verbatim for history. The stage plan below was written before any of the
evidence in §3 existed; Stages 1–2 were answered on 2026-08-18 and Stage 5's product
question is answered by §8. Do not plan from this appendix — plan from the index above.*

> Created 2026-06-14. Owner: DS/AI intern. Workstream: **Tooling & Engineering**
> (exploration/evaluation, not a committed product build). This is the concrete
> spec for the ASL effort that has been **DOCKED** in the tool inventory — the
> intern project IS the open-source-landscape evaluation that was the blocker.
> Success = decide whether OSS ASL is now good enough to un-dock, not SOTA accuracy.

## ⛔ 2026-08-16 — evaluated with a general VLM. NEGATIVE. Stays docked.

> **Superseded on 2026-08-18 by Appendix B below**,
> which re-tested this conclusion against an actual ground-truth transcript and
> five separate configurations (sampling density, resolution, model tier, batch
> size, native-video vs stills). The verdict below holds and is now better
> evidenced; read that document for the why and for the open pricing decision.

A working prototype was built (`curify_background/app/utils/asl_utils.py`):
motion-adaptive frame sampling → batched vision-LLM recognition, evaluated on a
real user's ASL video (user 1415, "Unit 7 discussion forum", 200 s — the user
submitted it for translation twice and both jobs failed).

**The sampler works.** Motion-energy probing split the clip into 58 active / 59
idle runs and put **100% of a 96-frame budget inside active signing** (active is
only 65% of the timeline, so uniform sampling wastes ~35% of the budget on the
signer at rest). That component is sound and reusable by any future recogniser.

**The recogniser does not work — it confabulates.** Same 20 frames, three runs:
identical input produced entirely different stories, and **reversing the frame
order produced equally fluent output at the same stated confidence**. ASL is
temporally directional; a model genuinely reading signs cannot be indifferent to
reversal. Output was generic filler ("three important lessons", "patience",
"perseverance") with per-batch greetings and endings — the signature of a model
inventing a plausible narrative per call.

**Why:** ASL's signal is the motion trajectory between postures plus non-manual
markers (brow, mouth, gaze). Sparse stills discard the trajectory, and a general
VLM has no ASL grounding to recover it.

**Decision:** the Stage-1 question ("are available models good enough to
un-dock?") is answered — **no**, not via general VLMs on sampled frames. Keep
`project_asl_captioning_demand` docked. Un-docking requires a purpose-built
sign-language model over continuous video (YouTube-ASL / OpenASL lineage). The
danger here is specific: a fluent hallucinated transcript burned into captions is
invisible to the deaf viewer it is made for.

---

## Why now / context

- **Real demand signal:** the `/blog/asl-video-translator` post draws traffic, and
  we've had at least one real user ask (user 1252 — we hand-delivered a translated
  video via `gtm_tools/send_1252_asl.py`; demo asset `dev/jayw/raw/asl-demo-translation.mp4`).
- **Why it was docked** (`project_asl_captioning_demand` memory): Sign-Speak's API
  went silent and we hadn't found a viable OSS ASL model. This project re-opens
  exactly that question with a time-boxed eval instead of a speculative build.

## ⭐ Scope insight — the intern only owns *ASL → English*

Curify already has the **entire downstream pipeline** built for video dubbing.
Once we have an English transcript, everything else is solved by existing code:

| Pipeline step | Already exists — reuse, don't rebuild |
|---|---|
| English → Chinese (+ post-edit) | `app/utils/translation_utils.py` |
| Subtitle file (SRT/ASS) generation | `app/utils/subtitle_utils.py` |
| TTS voice-over + mux to video | `app/utils/voiceover_utils.py` (+ alignment_utils) |
| Orchestration pattern (thin wrapper over utils) | `app/pipelines/transcribe_burn_pipeline.py` |

So the **only new capability** is the front-end: **ASL video → English text/gloss**.
The MVP's "Translation / Chinese subtitle / voice-over" steps (Stage 3) should
**call or mirror the utils above**, not reimplement them. If this graduates, the
ASL recognizer becomes `app/utils/asl_utils.py` + an `asl_pipeline.py` wrapper
(per our pipelines-are-wrappers architecture standard).

---

## Project Goal

Build an end-to-end prototype that converts ASL (American Sign Language) videos into:
- English subtitles
- Chinese subtitles
- Optional voice-over

The goal is **NOT** to develop a new ASL model. The goal is to evaluate:
1. Current open-source ASL recognition quality
2. Engineering complexity
3. Potential product opportunities

---

## Stage 1: Landscape Research (3–5 days)

**Objective:** understand the current state of open-source ASL recognition/translation.

Research: OpenASL · YouTube-ASL · Sign Language Transformers · Hugging Face ASL
models · MediaPipe-based approaches.

For each, document: GitHub link · dataset used · model architecture · checkpoint
availability · inference requirements · reported performance · ease of deployment.

**Deliverable:** a comparison report + recommendation of the top 2–3 candidates.

| Model | Open Source | Dataset | Ease of Use | Notes |
|---|---|---|---|---|

---

## Stage 2: Reproduce Existing Models (1 week)

**Objective:** run at least one existing ASL model locally.

Tasks: download checkpoint · run inference on sample videos · evaluate latency ·
evaluate output quality. Collect demo videos, screenshots, output text.

**Deliverable:** a simple benchmark.

| Video | Ground Truth | Prediction | Notes |
|---|---|---|---|

---

## Stage 3: Build End-to-End Pipeline (1 week)

**Objective:** create a complete workflow.

```
ASL Video → ASL Recognition → English Subtitle → Translation → Chinese Subtitle
                                                          ↓ (optional)
                                                    TTS → Chinese Voice-over
```

Tasks: simple web demo or notebook. Input: upload video. Output: English
transcript + Chinese translation + subtitle file.

**Reuse note:** everything from "English Subtitle" rightward already exists (see
the table above) — wire to `translation_utils` / `subtitle_utils` /
`voiceover_utils`. Only "ASL Recognition" is new.

**Deliverable:** working demo.

---

## Stage 4: Quality Evaluation

**Objective:** measure practical usefulness.

Collect 20–50 ASL videos. Evaluate: recognition accuracy · keyword coverage ·
translation quality · failure cases.

Error taxonomy: missed words · wrong words · signer variation · occlusion · low
resolution · fast signing.

**Deliverable:** evaluation report.

---

## Stage 5: Product Exploration

**Objective:** identify viable product directions.

- **Option A — ASL → Multilingual Subtitles** · target: YouTube creators, educational content
- **Option B — ASL → Voice-over** · target: accessibility, localization
- **Option C — ASL Learning Assistant** · target: students, schools
- **Option D — ASL Content Localization** (ASL → EN → ZH/JA/ES → voice-over) · target: NGOs, governments, educational publishers

**Deliverable:** recommendation memo — most promising use case · technical gaps ·
estimated effort for production.

---

## Success Criteria

The project is successful if:
1. We can run at least one open-source ASL model.
2. We can build an end-to-end demo.
3. We understand the major quality limitations.
4. We identify at least one potential product opportunity.

It is **NOT** judged by achieving state-of-the-art ASL accuracy.


---
---

# Appendix B — recognition evaluation, 2026-08-18

*Was `docs/asl-recognition-evaluation-2026-08-18.md`, absorbed here verbatim on
2026-08-29. Superseded on the temperature question by §1.2 (which measures the
decode-noise share this document could only hypothesise about), on the accuracy
question by §1.1 (two verified-gold cases, scored), and **on pricing by §9 — where
this document says "still live at 8 credits/min", read "free since 2026-08-29"**.
Everything else below stands — in particular §2 on why a "simple" clip is the worst
acceptance test, §5 on why it fails, and §8's outreach template.*

## ASL recognition — evaluation against ground truth (2026-08-18)


**Status: the recogniser does not read ASL reliably. Five configurations tested,
all non-deterministic. Do not present its output as a translation.**

This is the follow-up to Appendix A, which recorded the
reversal-control failure on 2026-08-16. That result was correct but the reasoning
was thin — it showed the output was unreliable without showing *why*, and it had
no ground truth to score against. This document has both.

---

### 1. The case

User 1434 (new, signed up 20:00:24) uploaded a 16.6s iPad screen recording at
20:02 on 2026-08-17 and the job failed. The recorded reason was:

    ASL recognition failed: batch 0: ClientError; batch 1: ClientError;
    batch 2: ClientError; batch 3: ClientError

Every batch had died on a Gemini 429 — *"Your project has exceeded its monthly
spending cap"* — the same cap that killed five of user 1433's image generations
19 minutes earlier. The batch handler recorded `type(e).__name__` and discarded
the message, so one incident read as two unrelated bugs and the user was told, in
effect, that we could not read their signing. Fixed in `08d12fb3` (message
preserved; quota classified via the shared `is_quota_exhausted`).

**The uploaded video.** A screen recording of
[Basic ASL Conversation by Jay Harris](https://www.youtube.com/watch?v=f_nVhrOgpYw)
(37s), two signers on a plain dark background. The player timecode reads
`0:17 / 0:37` at clip time 14.2s, so the clip covers roughly **video 0:03–0:19 —
the first half only**.

**Ground truth** comes from a comment on that video (crowd-sourced, not
authoritative, but consistent with the visible signing):

| # | | Line | In our clip? |
|---|---|---|---|
| 1 | Blue | Hello | ✅ |
| 2 | Red | Hello | ✅ |
| 3 | Blue | How are you? | ✅ |
| 4 | Red | I'm fine, how are you? | ✅ |
| 5 | Blue | Great | ✅ |
| 6 | Red | Good | ~ boundary |
| 7–11 | | Are you deaf or hearing? / Hearing, are you? / I'm deaf / Nice to meet you / Same here | ❌ not in clip |

**This matters more than anything else in the document.** Lines 1–6 are the
highest-prior exchange in ASL. Lines 7–11 are the only content-bearing part — and
they are the part we did not have.

---

### 2. Why "it's a simple video" makes it *harder* to judge, not easier

The natural reaction to this failure is that a simple greeting exchange should be
easy. The opposite is true, and it is the central lesson here.

A general VLM shown two people on a dark background in lesson framing can produce
"Hello / How are you? / I'm fine" **without decoding a single sign**, because that
is the most likely content of any such video. When the video's actual content *is*
the greeting exchange, the model's prior and the truth coincide, and the output
looks ~65% correct while carrying no evidence that anything was read.

A simple video is therefore the *worst* possible acceptance test: it is the one
case where guessing scores well. The reversal control makes this concrete —
reversed frames still produced fluent greeting-flavoured English.

The diagnostic content was lines 7–11 (deaf vs hearing), which cannot be guessed
from setting. That test remains **unrun** — the source could not be downloaded
(HTTP 403 on every `yt-dlp` player client: `web`, `ios`, `tv`, `android_vr`,
`mweb`).

---

### 3. What was measured

Scored against lines 1–6. `≈` = right in gist, `✗` = not signed at all.

| Config | Output | vs truth |
|---|---|---|
| **Production** (512px stills, flash, batch 24) run 1 | Hello / Hello / I understand / What about you? / Everything is good / **And this is my colleague** / **Thank you** | 4 ≈, 3 ✗ |
| **Production** run 2 (identical input) | Hello / Hello / **Together** / Us and you? / **It's important** / That's good / I'm good | 4 ≈, 2 ✗ |
| **Production** run 3 (shipped to user) | Hello / Hello / **Excuse me, you** / **Explain it** / Good! / I'm fine | 4 ≈, 2 ✗ |
| Chrome-cropped (title hidden) | Hello / Hello / **Together** / **Me?** / **Are you practicing?** / That's great | 2 ≈, 4 ✗ |
| **Frames reversed** (control) | Okay. Thank you / You / **You and I, together?** / Hello / Hello | still fluent |
| 768px signer crop, **2.5-pro**, batch 8 | run 1: Looking around for someone / How are you? / Which one? — run 2: Hello / How did they? / Which one? | unstable |
| 768px signer crop, flash, batch 8 | run 1: searching / Over there / It is good — run 2: Look for / That / It's good | unstable |
| **Native video**, 2.5-pro | run 1: **I like to sit.** What about you? / Great! / Thank you — run 2: Hello / How are you? I'm fine, and you? / I'm good | best single run, still unstable |
| **Native video**, flash | run 1: Hello! How are you? / I'm good, how about you? / Nice to meet you — run 2: Hello / **You know who I am? / Everyone knows!** | unstable |

**Every configuration produced a different transcript on repeat runs of identical
input.** `gemini-2.5-pro` on native video produced the single best output seen
("Hello / How are you? I'm fine, and you? / I'm good") — and on the very next run
of the same file produced "I like to sit."

---

### 4. What was ruled out

Each of these was a plausible cause. None fixed the instability.

| Hypothesis | Test | Result |
|---|---|---|
| Under-sampling — too few frames | measured: **95 frames over 16.6s = one every 0.175s**, against `FRAME_BUDGET=96`; uniform-equivalent was 65 | ✗ ruled out. Sampling was near max and denser than uniform. |
| Resolution — hands too small | `KEYFRAME_WIDTH=512` on a 2732px source puts the hand at ~40px, fingers ~8px. Re-ran cropped to one signer at 768px (≈4× detail) | ✗ still unstable |
| Weak model | re-ran on `gemini-2.5-pro` (production uses `gemini-2.5-flash`) | ✗ still unstable |
| Attention diluted by batch size | 24 images/call → 8 | ✗ still unstable |
| **Stills destroy motion** — the strongest hypothesis | sent the clip as **native video** instead of sampled JPEGs | ✗ still unstable (but best single run) |

Cost of the whole evaluation: ~$0.50.

---

### 5. Why it fails — assessment

Ordered by confidence. The first three are structural, not tuning problems.

1. **A sign is a trajectory, not a pose.** We send still JPEGs with timestamp
   labels. ASL encodes meaning in movement — path, direction, repetition, speed.
   Many sign pairs share a handshape and differ only in movement. The reversal
   result is best read not as "it hallucinates" but as evidence the model was
   **not using temporal order at all** — reversing frames changed nothing because
   nothing depended on sequence. Native video input should have fixed this and
   did not fully, which suggests the deficit is in the model's ASL competence,
   not only in our framing.

2. **No ASL grammar.** ASL is not English-with-hands: topic-comment order, spatial
   referencing, classifiers, and grammar carried on the face (brow raise = yes/no
   question, furrow = wh-question). Even perfect sign recognition needs a second
   ASL→English translation step. General VLMs have seen little aligned ASL.

3. **Priors dominate when perception is weak.** Starve the model of detail and it
   falls back on "what does an ASL lesson video say" — which is why the *shipped*
   config (512px, flash, 24/call) produced the most fluent, most confident and
   most fabricated output, while higher-detail configs produced shorter, hedged
   output. Better inputs did not raise accuracy so much as **make uncertainty
   visible**.

4. **No signer separation.** Ground truth alternates Blue/Red every line. Nothing
   in the pipeline does signer attribution; `AslSegment.speaker` is populated with
   a constant.

5. **Source ceiling.** The underlying upload is an old, soft, low-bitrate video.
   Even a native-resolution crop is blurry.

---

### 6. Product consequences

- **The failure mode is the dangerous one.** Not obviously-broken output —
  *mostly-right output with 2–3 confident fabrications interleaved*, differing
  every run. A reader who cannot verify has no way to spot which lines are real.
- **The audience makes it worse.** Burned-in captions are invisible to the deaf
  viewer they are made for, in the sense that they cannot be checked against the
  audio there isn't any.
- **⚠️ Still live at 8 credits/min** (`create` in `tools-registry.ts`,
  `JOB_CREDIT_COST["ASL_TRANSLATION"]=8`, explicitly excluded from the free
  subtitle quota). We are charging for output we have told a user we do not
  trust. **Open decision: demote to `demo`/waitlist, or make free until the
  recogniser is replaced.**
- If it stays live, raise `KEYFRAME_WIDTH` and use a pro-tier model — not because
  it becomes correct, but because it stops sounding certain.

---

### 7. Next tests, in order of value

1. **Run lines 7–11** (deaf/hearing exchange). The only test that separates
   reading from guessing. Blocked on obtaining the source — ask user 1434, or
   record an equivalent clip with known distinctive content.
2. **Build a real eval set.** ~20 clips with verified glosses, scored per-sign,
   with a repeat-run determinism metric. Impressions do not survive contact with
   a prior; this document exists because there was ground truth.
3. **Purpose-built models** — How2Sign / OpenASL trained recognisers, or a
   pose-estimation front end (MediaPipe Holistic) feeding a sign classifier,
   rather than a general VLM.
4. **Human-in-the-loop** — if the wedge is deaf-accessibility, verified output is
   the product. Unverified output is a liability.

---

### 8. Outreach precedent

User 1434 was sent the captioned video framed explicitly as experimental: the
email named which lines we believed correct ("Hello", "I'm fine") and which we
believed fabricated ("Excuse me, you", "Explain it"), stated that repeat runs
differ, and asked them to tell us what was actually signed. Not charged.

Naming the specific suspect lines is what makes a feedback request answerable —
"tell us if it's wrong" invites nothing; "we think these two are invented, are we
right?" is a one-line reply. Reuse this pattern when shipping any unreliable
output to a user who can verify it.

---
---

# Appendix C — Stage 1 + Stage 2 results, 2026-08-18

*Was `docs/asl-mvp-stage2-results-2026-08-18.md`, absorbed here verbatim on
2026-08-29. This is the open-source-model evaluation (TGCN-WLASL at chance on
in-domain clips) and the 12.39 BLEU field-ceiling close. Nothing since has changed
it; §7 "Deliberately NOT low-hanging" carries its verdict forward. **Its pricing
references are historical — see §9.***

## ASL MVP — Stage 1 + Stage 2 results (2026-08-18)


Follows Appendix A. Continues from
Appendix B, which established that the
general-VLM approach confabulates and that the required next step is a
purpose-built sign model.

**Headline: Success Criterion #1 is now technically met and practically unmet.**
We downloaded, loaded and ran a real open-source ASL model locally. It produces
**chance-level output** on clips whose answer we know, because the pose
front-end it was trained on is not interchangeable with the one we can run.

---

### Why this was the right next step

The spec's success criteria are:

1. run at least one open-source ASL model ← **never attempted before today**
2. build an end-to-end demo ← done (but around a *general* VLM, not an ASL model)
3. understand major quality limitations
4. identify a product opportunity

Stages 1 and 2 had been skipped; the shipped tool went straight to Stage 3 with
`gemini-2.5-flash`. That is precisely the thing the spec says is *not* the
subject of evaluation.

---

### Stage 1 — landscape (condensed)

The important distinction, which the earlier work blurred:

| Task | What it does | Checkpoints? | Fits our need? |
|---|---|---|---|
| **ISR** — isolated sign recognition | one sign per trimmed clip → gloss (WLASL-100/300/1k/2k) | **yes, downloadable** | partially — needs segmentation |
| **CSLR** — continuous recognition | continuous video → gloss sequence | scarce for ASL | closer |
| **SLT** — sign language translation | continuous video → English sentences | mostly **weights not released** (YouTube-ASL lineage) | this is what we actually need |

Our product need is SLT. The only tier with runnable weights is ISR — hence the
plan: pose → motion segmentation → per-segment ISR → gloss sequence → English.

Candidate selected: **TGCN-WLASL** ([`sharonn18/tgcn-wlasl`](https://huggingface.co/sharonn18/tgcn-wlasl)),
a Temporal GCN over 55 pose keypoints, from the WLASL lineage (Li et al.).
Variants for 100 / 300 / 1000 / 2000 classes, all weights public.

**Vocabulary coverage is good.** 11 of 15 ground-truth words from our test video
exist in WLASL, and critically **`deaf` (idx 10) and `hearing` (idx 41) are both
inside the 100-class set** — those are the diagnostic signs that would separate
reading from guessing.

---

### Stage 2 — running it

Reproduced the input contract from the original source rather than the model
card, which matters because the card is vague and partly wrong:

* **55 keypoints** = OpenPose BODY_25 minus `{9,10,11,12,13,14,19,20,21,22,23,24}`
  (legs/feet) → 13 body, then 21 left-hand, then 21 right-hand.
  The model card's claim "MediaPipe pose format" is **incorrect** — MediaPipe
  Pose has 33 keypoints; this is an OpenPose layout.
* **Normalization** `x = 2*((x/256)-0.5)` — WLASL frames are 256×256 signer crops.
* **Tensor layout** `torch.cat(poses, dim=1)` → `(55, 2T)`, x/y **interleaved**
  per frame, not blocked.
* The card also claims **">85% top-1"**; published WLASL-2000 TGCN top-1 is
  ~30%. Treat that number as unreliable.

Code: `dev/asl_mvp/code/{pose55,run_tgcn,bench}.py`. Checkpoint loads with
`missing_keys=0, unexpected_keys=0`.

#### Result on the real user video (u1434, both signers cropped to 256×256)

Ground truth for the clip window is greetings only. Output was unrelated:
`minute 0.96`, `benefit 0.87`, `breakdown 0.79`, `candle 0.65`, `slave 0.59` …

#### Result on IN-DOMAIN WLASL clips — the decisive test

12 clips downloaded from the dataset's own URLs, each a single trimmed sign:

| Model | top-1 | top-5 | random baseline |
|---|---|---|---|
| asl2000 | **0/12** | **0/12** | 0.05% / 0.25% |
| asl100 | **0/12** | **0/12** | 1% / 5% |

Chance level on data where the answer is known. So the failure is **ours or the
checkpoint's — not out-of-domain video**.

#### What was ruled out

| Hypothesis | Test | Result |
|---|---|---|
| Wrong hand assignment | swap L/R hand blocks | 0/12 |
| Mirrored video | negate x | 0/12 |
| Wrong normalization | raw [0,1]; raw pixels ×256 | 0/12 |
| Scale/offset (signer doesn't fill frame) | re-center on neck, scale by shoulder width | 0/12 |
| Model is degenerate / untrained | random + zero + all-−1 inputs | **input-sensitive**; weight std/max exceed uniform init → genuinely trained |
| Class list permuted | a permuted-label model still maps distinct signs to distinct classes; here `forget` appears 3× and `deaf` 2× across 12 different signs | **not a permutation** |

Label ordering was separately verified self-consistent: `wlasl_class_list.txt`
index ranges match `nslt_100.json` (0–99) and `nslt_2000.json` (0–1999) exactly.
Caveat: that validates *WLASL's* ordering, not that this community re-upload
trained with it.

---

### Conclusion

**The blocker is the pose representation, not the model.** TGCN-WLASL consumes
OpenPose-derived features; substituting MediaPipe keypoints — with the documented
layout, normalization and tensor order, across six representation variants —
lands at chance on in-domain clips. The two pose estimators are not drop-in
compatible for a GCN trained on one of them.

This is the concrete, falsifiable answer the spec asked for, and it is stronger
than the 08-16 conclusion because it was measured against known labels.

### Next, in order

1. **Run actual OpenPose** on the 12-clip benchmark and re-test. This is now a
   ~1-day question with a clear pass/fail: if TGCN scores above chance on
   OpenPose features, the whole ISR path re-opens. If it still fails, the
   checkpoint is unusable and we drop this lineage.
2. If (1) passes, wire pose → segmentation → ISR → gloss → English and re-run the
   `deaf`/`hearing` test on video 0:19–0:37, which is the diagnostic half.
3. Keep the motion-adaptive sampler — it was independently validated and is
   reusable by any recogniser.
4. **Do not ship any of this to users.** The live tool remains a general VLM at
   8 credits/min; the open pricing decision in
   Appendix B §6 is unchanged.

### Reusable assets produced

* `dev/asl_mvp/code/pose55.py` — MediaPipe → WLASL-55 extractor (documented layout)
* `dev/asl_mvp/code/run_tgcn.py` — TGCN loader, motion segmentation, inference
* `dev/asl_mvp/code/bench.py` — in-domain benchmark harness
* `dev/asl_mvp/bench/ground_truth_1434.json` — the 11-line reference transcript
* `dev/asl_mvp/bench/wlasl_class_list.txt` — verified 2000-gloss index mapping

---

### ⛔ CLOSED — 2026-08-18

**Decision: stop work on ASL translation as a product. The ceiling is the field,
not our engineering.**

The number that closes it: the finetuned state of the art for ASL→English
translation is **12.39 BLEU** ([YouTube-ASL, NeurIPS 2023](https://arxiv.org/abs/2306.15162)
— 1000 h, 2500+ signers, trained on YouTube-ASL then finetuned on How2Sign;
zero-shot is 3.95). Calibration: production MT runs 40–50 BLEU, ≥30 is "good and
understandable", 20–30 is "gist clear, wrong in places". **12 is below the level
at which you put the output in front of a user as a transcript** — and How2Sign
is studio-lit, front-facing, single-signer. A screen-recorded clip with two
signers is materially harder.

Our two negative results are therefore *what the field predicts*, not anomalies:

| Attempt | Result | Consistent with SOTA? |
|---|---|---|
| General VLM over sampled frames | confabulates; 5 configs, all non-deterministic | yes — no ASL grounding |
| TGCN-WLASL (ISR) over MediaPipe poses | 0/12 top-5 in-domain | yes — and ISR ≠ translation anyway |

Even a *working* ISR model would not compose into a transcript: at a generous 60%
per-sign accuracy, an 8-sign sentence is ~1.7% fully correct, before segmentation
error, and before ASL→English grammar (topic-comment order, classifiers, spatial
reference, non-manual markers).

#### The reframe, if ASL is ever revisited: verifiability, not accuracy

| Use case | Who checks the output | Error cost | Viable today |
|---|---|---|---|
| Translation for deaf viewers | nobody — errors are invisible | high, borne by the person it was made for | **no** |
| Learning / practice ("is my sign right?") | the learner, who knows the target | low — mismatch is obvious | **yes** |
| Fingerspelling | narrow closed alphabet | low | probably |

Isolated-sign recognition at ~60% top-5 is useless as a transcript and genuinely
useful as "here are 5 candidates, which did you mean". Same model, opposite
verdict, purely because the user can verify.

#### What would reopen this

* A released SLT checkpoint materially above ~25 BLEU on open-domain ASL, **or**
* A demand signal with budget — a school, NGO or publisher with batch volume. The
  honest offer there is **human-verified transcription with AI assist**, i.e. a
  services motion, not a model.

#### Explicitly NOT done, and deliberately so

The OpenPose pass/fail on the 12-clip benchmark (§Next step 1 above) is still
~1 day and still cheap — but it only settles *isolated sign recognition*, which
is not the product. Do not run it to close a loop; run it only if the
learner-facing product is being pursued.

#### Retained assets

`dev/asl_mvp/` — pose extractor with the verified WLASL-55 input contract, TGCN
loader + motion segmentation, in-domain benchmark harness, verified 2000-gloss
index map, and the ground-truth transcript. The motion-adaptive sampler in
`app/utils/asl_utils.py` was independently validated and is reusable by any
future recogniser.

#### ⚠️ One open item, requires a product decision

The tool is still live as `create` at **8 credits/min**
(`JOB_CREDIT_COST["ASL_TRANSLATION"]=8`, `tools-registry.ts`), explicitly
excluded from the free subtitle quota. We are charging for output we have told a
user in writing we do not trust. Options: demote to `demo`/waitlist, or set the
rate to 0. This is the only item in this workstream with live downside.
