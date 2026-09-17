# Curify ASL Translation — Work Report

**Date:** 2026-09-11
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Head commit at time of writing:** `01cfd054faa67bd4980ea606e100bcfdf5f1b96e`
**Scope of this document:** consolidation only. No benchmark, no Gemini call, no external
API call, and no experiment was re-run to produce it; every number below is read from an
artifact already committed on this branch. `curify-studio` untouched. No PR created.

---

## 1. Executive Summary

- The work stream is **evaluation, diagnosis and architecture exploration** for ASL video →
  English text. It did **not** yet produce a major ASL translation-quality breakthrough.
- It did materially **narrow the technical search space**: five distinct input-side
  interventions (frame density, sampling strategy, batch/context grouping, native video
  input, trajectory-as-text context) have now been tested against a frozen benchmark, and
  none produced demonstrated semantic recovery on the diagnostic cases.
- It also produced **reusable infrastructure**: a frozen, checksum-validated 128-clip
  How2Sign v2 benchmark, four scored systems on it, a per-clip frame inspector now showing
  reference / Curify frame baseline / Uni-Sign / Gemini native video side by side, a
  native-video benchmark harness, and a pose/trajectory extraction probe.
- **Task A (Uni-Sign in the inspector) is complete.** **Task B (Gemini native video) is
  partial and blocked on the Gemini Files API** — 5 of 12 diagnostic clips scored, 7 still
  unscored. **Task C (SignCaption / Sign-Speak) is research-complete but access-pending.**
  **Task D (trajectory tracking) has a completed POC with a negative D2 result.**
- The dominant observed failure is **topic-level semantic mismatch** — fluent English about
  the wrong subject — not mis-wording of a correct read (0/40 clips in the qualitative
  review showed "correct meaning, different English").
- Recurring methodological finding: **metric movement ≠ semantic recovery.** WER, BLEU and
  chrF all moved on individual interventions without a single clip becoming correct.
- The strongest remaining hypothesis is that the bottleneck needs a **sign-specific learned
  temporal/linguistic representation**, not more or differently-formatted visual input fed
  to a generic multimodal model. This is a hypothesis supported by the current evidence,
  not a proof.

---

## 2. Project Goal

**Product/research goal:** reliable ASL video → accurate English caption/text, good enough
to ship as a Curify captioning capability.

**What this work stream actually is:** benchmark construction, evaluation, failure
diagnosis and architecture exploration. It is explicitly **not** training a new
SignGemma-class sign-language model. Every experiment on this branch is an
inference-time/input-formulation intervention against a frozen benchmark, scored with an
unmodified scorer. Nothing here trains or fine-tunes a model, and no repository evidence
yet justifies committing to that.

---

## 3. Benchmark and Evaluation Foundation

**How2Sign v2 frozen benchmark** (`asl-translator/data/public_benchmarks/how2sign_v2/`):
128 clips drawn from How2Sign's official, human-translated **test split**, selected by a
deterministic metadata-only rule *before any video was viewed and before any model was
run*, then validated (alignment, leakage, duplicate-content) and frozen under
`FREEZE.sha256` / `FREEZE_CHECKSUMS.sha256`. Public CC BY-NC 4.0 research data, held
separately from the private Curify corpus.

**Verified aggregate results on the frozen 128-clip set** (each system's own
`corpus_summary.json`):

| System | n scored | corpus WER | corpus CER | corpus BLEU | corpus chrF |
|---|---|---|---|---|---|
| Curify / Gemini frame baseline (`curify_gemini_3_6_2026_09_04`) | 128/128 | **0.9762** | 0.8071 | 0.1341 | 11.2835 |
| Uni-Sign | 128/128 | **0.9819** | 0.7608 | 5.3876 | 22.7498 |
| OpenSLT | 126/128 | **1.0246** | 0.7689 | 0.962 (independent) | 18.5904 |
| Curify / Gemini 8 fps ablation (`..._2026_09_06_8fps`) | 76/128 (billing-capped) | 0.9715 | 0.7763 | 0.1412 | 13.3686 |

Cross-model comparison is only valid on the **matched-126** intersection (OpenSLT failed 2
clips, Uni-Sign 0): Curify frame baseline WER **0.9761**, Uni-Sign WER **0.9801** there.
Curify's own WER is essentially unchanged between denominators (0.9762 vs 0.9761), so the
126-clip restriction is a comparability device, not a missing-prediction problem.
`asl-translator/evaluation/compare_how2sign_v2_systems.py` builds the 4-system scorecard
and the pairwise comparisons from these already-written summaries, without model calls.

**Why WER alone is insufficient.** Every system sits near WER ≈ 1.0, where the metric can
no longer discriminate: an edit-distance score near 1 is compatible with an empty output, a
short wrong output, and a long fluent hallucination. Worse, WER can *improve* when one
fabrication is replaced by another that happens to match the reference's word count, and
BLEU/chrF can rise purely because an output got longer. Both effects were observed directly
on this branch. A **semantic adequacy / reference-topic-mismatch review** was therefore
added as the judgment that actually decides whether an intervention helped.

**40-clip LLM-assisted text-semantic review** (labeled explicitly as *text-only*, English
reference vs. English prediction — **not** ASL-fluent visual annotation):

| metric | value |
|---|---|
| clips reviewed | 40 / 40 |
| semantic adequacy = 2 (core meaning correct) | 0 / 40 (0%) |
| semantic adequacy = 1 (partial) | 3 / 40 (7.5%) |
| semantic adequacy = 0 (wrong/unrelated) | 37 / 40 (92.5%) |
| reference topic mismatch = yes | 36 / 40 (90%) |
| correct meaning, different English | 0 / 40 (0%) |
| obvious text-level repetition | 0 / 40 (0%) |

The 0/40 "correct meaning, different English" figure is the important one: there is no
evidence that a good translation is being unfairly penalized by raw WER. The failure is
real and semantic.

---

## 4. Earlier Temporal Diagnostics

Three controlled ablations were run against the frozen adaptive-2 fps / independent-24-frame-batch
baseline, all documented in
`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/FINAL_TEMPORAL_DIAGNOSIS.md`.

| Intervention | Scope | Result |
|---|---|---|
| Frame density: adaptive ~2 fps → adaptive ~8 fps | paired 76 clips (Experiment B stopped early at an external Gemini billing cap) | corpus WER 0.9730 → 0.9715 (Δ −0.0015); median per-clip Δ 0.0000; 15 improved / 20 worsened / 41 unchanged. **Flat.** |
| Sampling strategy: motion-weighted/adaptive → uniform, same 2 fps | 12 diagnostic clips | corpus WER 1.0524 → 1.0594; median per-clip Δ 0.0000; 2 improved / 5 worsened / 5 unchanged. **No semantic recovery.** |
| Batch/context: independent 24-frame batches → overlapping sliding windows (stride 12) | 12 diagnostic clips, same sampled frames | corpus WER 1.0524 → 0.9545; 4 improved / 2 worsened / 6 unchanged — **but 12/12 clips remain topic-mismatched under both arms.** |

The sliding-window result is the one most likely to be over-read. Its own architecturally
inert control — the 8 single-batch clips, where 1 window = 1 batch = the same frames in the
same single call — moved by a mean WER delta of **−0.0673** from decoding variance alone.
That is the empirical noise floor for small-n ablations on this corpus, and it is not small
relative to several of the "improvements" attributed to the multi-batch subset (n=4, itself
dominated by one clip).

**Key conclusion:** simple frame-density and sampling changes did **not** materially solve
the semantic/topic failure. This is a statement about the three interventions actually
tested, at the sample sizes tested. It is **not** a claim that temporal information is
useless for ASL, nor that no frame-based intervention could ever help.

These diagnostics are what motivated the 2026-09-10 manager tasks: having exhausted *when*
the model looks, the next axes to test were *what representation it is given* (native video,
trajectory), *what a commercial ASL-specific system can do* (SignCaption/Sign-Speak), and
*how to inspect all of it side by side* (the inspector).

---

## 5. Manager Task A — Uni-Sign Inspector

**Status: COMPLETE.**

The per-clip diagnostic frame inspector
(`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/`) was extended
in `build_inspector.py` so that each of the 12 diagnostic clip pages now shows, with the
same word-level Levenshtein diff treatment against the reference:

1. **Reference** (official How2Sign English translation, from the frozen `.srt`),
2. **Curify / Gemini frame-baseline prediction** (with WER/CER),
3. **Uni-Sign prediction** (with WER/CER),
4. **Gemini native-video prediction** (with WER/CER) where one exists.

`index.html` gained per-system WER columns (frame-baseline / Uni-Sign / native-video) plus
a trajectory-probe column and explicit coverage banners.

Important properties:

- **Read-only.** The inspector re-runs only the production *sampler* to redraw which frames
  the model saw; it makes **no model call**. Uni-Sign and native-video predictions are read
  from each system's own frozen `per_clip_results.json`, and their WER/CER are read, not
  recomputed — so the page always agrees with the scored corpora.
- **Real empty predictions are distinguished from unavailable results.** A system that
  genuinely returned nothing renders as `(empty prediction)` inside a normal prediction
  block; a system with no valid result renders as `Unavailable — <reason>`. For native
  video the reason is specific: Files-API failures render as "Unavailable — Gemini Files API
  processing failed before inference", while a failure that happened *after* a real model
  call shows its own actual reason rather than being collapsed into the Files-API message.

**Why this is useful:** at WER ≈ 1.0 across all systems, aggregate metrics cannot tell the
team anything. The inspector is the mechanism for qualitative cross-model comparison —
seeing, on the same clip and the same frames, that Curify hallucinates one narrative,
Uni-Sign another, and native-video Gemini a third, all unrelated to the reference. That
observation is what drives every conclusion in §11, and it is not visible in any scorecard.

Inspector (commit-pinned):
https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/index.html

---

## 6. Manager Task B — Gemini Native Video

**Status: PARTIAL / INFRASTRUCTURE-BLOCKED.**

### What was implemented

A native-video runner (`asl-translator/asl-eval/run_native_video.py`) and its benchmark
driver (`asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py`), built as a
sibling of the frame-based runner rather than a modification of it, so the frozen
frame-baseline configs stay byte-for-byte unaffected:

- **Full `.mp4` upload** to the Gemini Files API (upload → poll for ACTIVE → `Part.from_uri`
  → `generate_content` → delete), **one model call per clip**, instead of N batched
  JPEG-frame calls.
- **Production prompt adapted for video**: `PRODUCTION_PROMPT` imported byte-identically
  from the frame runner, with exactly the two documented edits — the "frames are sparse"
  rule bullet removed, and "the frame timestamps you used" → "the video timeline". This is
  the one unavoidable prompt confound, documented in the module docstring rather than
  hidden. Model, thinking level and decoding knobs are held at the frame-baseline control's
  values (`gemini-3.6-flash`, `thinking_level=medium`, no explicit temperature).
- **Evaluation/scoring** through the existing, unmodified `asl-eval/evaluate.py` + `lib.py`,
  same manifest, same matched-126 comparability logic as the frame driver.
- **Safety guard for private-data upload**: default mode is dry-run (local `ffprobe` +
  `corpus_guard` leakage check only, never imports `google.genai`, never needs an API key).
  A real run requires **both** `--run` and `--acknowledge-private-data-upload`.
- **Resumability**: re-running against the same results directory skips already-completed
  clips and attempts only the missing ones — verified end-to-end across three invocations.
- **Cleanup**: uploaded files are deleted in a `finally` block, including on the
  FAILED-state path; stray uploads recoverable from logs were individually verified and
  deleted.
- **Parser robustness** (see below).

### The real parser bug

One clip, `G05uFub3YFc_9-2-rgb_front`, failed with `AttributeError: 'list' object has no
attribute 'get'`. Diagnosis, not assumption: its recorded `inference_wall_clock_s` was
16.622 s — consistent with a real `generate_content` call (the valid clips took 8.5–18.5 s),
not the ~3 s immediate `FAILED` response the Files-API-blocked clips return. **Gemini had
returned a top-level JSON array instead of the requested `{"segments": [...]}` object**, and
the parser assumed the object shape. This was a **local parsing bug, not a Files API or
backend problem**. `parse_segments_response` now accepts either shape. The fix was then
**validated end-to-end**: a single-clip retry of `G05uFub3YFc_9-2-rgb_front` made a real
model call (`model_calls=1`, `inference_wall_clock_s=17.459`, `status=success`), received
the same bare-array shape, and parsed it correctly.

### Current status — exactly

- **5 / 12** diagnostic clips valid and scored: `FzmL8SL6Bow_1-8-rgb_front` (WER 1.0000),
  `-g0sqksgyc4_3-2-rgb_front` (1.0000), `92V3oH63zbQ_5-1-rgb_front` (1.0000),
  `fzNnTgHa1lM_2-5-rgb_front` (0.9118), `G05uFub3YFc_9-2-rgb_front` (0.9412).
- **7 / 12** still blocked at the Gemini Files API **before model inference** — the same 7
  clip IDs failed identically on two independent attempts with no config change. A local
  `ffprobe` inspection found no distinguishing pattern (all 12 are h264 / 1280×720 /
  yuv420p, overlapping duration/framerate/size ranges). Root cause is **unresolved**: either
  transient/account-side Files API degradation or a clip-specific processing
  incompatibility. Neither is confirmed.
- **0 / 5 genuine semantic recoveries** among the scored clips — semantic adequacy remains
  0 and reference-topic mismatch remains "yes" on all five, the same failure class as the
  frame baseline.
- **The manager's §7 P0-4 decision gate remains inconclusive.** The gate is defined over all
  12 clips (promotion: ≥3/12 flip semantic adequacy 0→≥1 or topic mismatch yes→no;
  rejection: 0/12 flip *and* WER movement inside the noise floor). With 5/12 scored and 0/5
  flips, promotion is still arithmetically reachable and rejection cannot be asserted. **Do
  not extrapolate 5/12 to 12/12.**

### The G05 example — metric movement is not semantic recovery

| | text |
|---|---|
| **Reference** | breathing-exercise instructions ("Again, do maybe twenty breaths, little flow, inhaling and exhal…") |
| **Frame baseline** | "She smooths out the cloth and places it flat on the table. She sets the container down on the surface. She puts on her gear and fastens it securely around her back. The tree caught on fire." — unrelated cloth/gear/fire hallucination |
| **Native video** | "I was terrified and my heart was pounding. Then I looked closely and saw what was actually there." — unrelated fear / heart-pounding hallucination |

WER improved numerically (1.0294 → 0.9412) and CER improved (0.8012 → 0.7251), but
**semantic adequacy stayed 0 and reference-topic mismatch stayed "yes."** One unrelated
hallucination was exchanged for a different unrelated hallucination. This is the single
clearest illustration of the methodological point running through the whole work stream:
**a better number is not a better translation.**

Blocker status (commit-pinned):
https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md

---

## 7. Manager Task C — SignCaption / Sign-Speak

**Status: RESEARCH COMPLETE / ACCESS PENDING.**

Method: pure local research — this repo and the read-only sibling `curify-studio` checkout
were grepped for existing documentation, outreach history, provenance files and `.env*`
files. **No network calls, no vendor contact, no production code changed.** Every "known"
item cites a source file; every unknown is stated as unknown rather than guessed.

**Verified publicly / locally:**

- Sign-Speak is the vendor; **SignCaption** is its ASL captioning product. An "API & SDK
  Integration" offering exists per its public Enterprise page.
- This is **not a cold start**: a pricing-inquiry email was previously sent to
  `management@sign-speak.com` via a one-shot script in `curify-studio`. **No reply was ever
  recorded**, and the project was previously docked for exactly that reason.
- Its public Enterprise page documents a base64-encoded video parameter (`b64video`).
- SignCaption accuracy has been measured internally — but **only from manually downloaded
  SRT exports already on disk, never via a live API call**. Best recorded results: WER
  0.4815 / CER 0.3712 (clip 155) and WER 0.5192 / CER 0.3347 (clip 1252), with fingerspelled
  names "Greg"/"Sara" correctly recovered. Those numbers are on private-corpus clips, not on
  the frozen How2Sign v2 benchmark, and every use of them in this repo is tagged
  `usable_for_official_metrics: false`.
- Sign-Speak's public Customer ToS **explicitly bars using the service "to create a
  competitive product"** — Curify's own ASL translator is arguably exactly that — and also
  prohibits sublicensing/resale, licenses uploaded video back to Sign-Speak for model
  training, and caps liability at trailing-6-months fees. **No written clearance on the
  competitive-product clause has been obtained.**

**Still unknown / requires vendor confirmation:**

- **API credentials** — none exist in either repo (both `.env.example` files checked; no
  `SIGN_SPEAK`/`SIGNCAPTION`/`SIGNSPEAK` variable; no non-example `.env` found).
- **Endpoint URL, request/response schema, SDK sample** — not documented anywhere.
- **Auth scheme** — no key format, header, or session scheme documented.
- **Pricing** — not public; gated behind Enterprise contact.
- **Rate limits** — not documented; was an explicit question in the unanswered outreach.
- **Benchmark permission** — no permission obtained to use SignCaption outputs as a
  benchmark comparator.
- **Commercial / ToS clearance** on the competitive-product clause — a standing open legal
  risk, flagged in a prior plan as a required gating Step 0, still not done.
- The vendor's marketed "BLEU score of 60" claim is **unverified vendor marketing**.

There is no technical work that can advance this direction from inside the repository. The
next steps are outreach and legal clearance, in that order — clearance before any further
technical evaluation.

Checklist (commit-pinned):
https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/signcaption-signspeak-research/CHECKLIST.md

---

## 8. Manager Task D — Trajectory Tracking

**Status: POC COMPLETE / NEGATIVE D2 RESULT.**

Origin: a CV tennis example where raw video is converted into structured spatiotemporal
trajectories, and the question of whether an analogous representation — explicit,
continuous hand/body/face tracking over time — could help ASL recognition, as an
*additional* signal rather than a replacement for handshape, fingerspelling, non-manual
markers or language context.

### D0 — Feasibility Research

This was **not a cold start**. Two claims must be kept separate:

- **New to the Curify/Gemini pipeline:** true. No pose/keypoint/trajectory code existed
  anywhere in `run_current_model.py` or `run_native_video.py`; Gemini had never been given a
  structured motion signal in any experiment on this branch.
- **New to the project:** false. **Uni-Sign — already one of the four scored systems on the
  frozen benchmark — is itself built on RTMPose-extracted skeleton keypoints.** Pose/
  skeleton-style representations were therefore already demonstrated inside our own
  benchmark ecosystem.

D0 also established why trajectory is genuinely distinct from the sampler already tested:
the existing motion signal (`probe_motion`) is **one scalar per timestep** — mean absolute
whole-frame grayscale pixel difference. It has no concept of a hand, a wrist, or a spatial
coordinate; it can say *when* something moved, never *where* or *what*. Trajectory tracking
produces a named, per-landmark `(x, y, confidence)` time series instead.

### D1 — Tracking POC

RTMPose via `rtmlib` (`Wholebody`, `lightweight` mode, ONNX/CPU), run on **5 probe clips**
chosen to stress the hardest cases: shortest clip, fastest signing, fingerspelling-heavy,
richest content, longest clip.

- **5/5 extraction success**, no failures, no retries.
- **1,038 total frames** processed across ~38 s of video in 62.2 s of wall-clock (excluding
  a 0.22 s one-time model load) — roughly real-time to 2× real-time on a laptop CPU.
- **Missing-tracking rate = 0.0%** for body, left hand and right hand on **every frame of
  every one of the 5 clips**.
- **Good confidence overall**, with one weaker case: `-g0iPSnQt6w_0-1-rgb_front`'s left hand
  averaged 0.579 vs. its right hand's 0.877 — traced to that hand being visibly less
  prominent in frame, still above threshold in 100% of frames. All other per-part means fall
  in roughly 0.81–0.93.
- **0 multi-person frames** on any clip.
- **Visual skeleton/finger QA passed**: skeleton overlays were spot-checked against the
  actual video on 4 of the 5 clips (the plan required ≥2) and confirmed correct — limbs on
  the actual shoulders and arms, face landmarks on the actual face, hand skeletons including
  individual finger joints on the actual hands, including a clearly resolved
  fingerspelling-style handshape on `Fz-N1S0swh8_2-8-rgb_front`. A full skeleton-overlay
  `.mp4` was rendered for one clip; static SVG path plots for all 5, embedded into the
  matching inspector pages.
- Classification: **5/5 usable, 0 partially usable, 0 unusable.**

**Conclusion: tracking itself is feasible on this probe set.** The signal is reliably
recoverable from this video corpus.

**Do not generalize this to the full 128-clip benchmark.** Tracking quality on the other 123
clips has not been measured and could differ. For the same reason, the scoped observation
that poor pose tracking is *unlikely* to explain Uni-Sign's failure applies **only to these
5 clips**, not corpus-wide.

### D2 — Trajectory-Augmented Gemini

A controlled, single-variable experiment on the same 5 clips: **same frames, same frame
baseline, same model, same sampling, same decoding config**. The only change was appending
**one** block of purely geometric trajectory-derived observations (position samples,
confidence, speed, body-relative bands, two-hand distance) to the existing prompt. Verified
before any call: no interpretive or ASL-semantic phrasing in the block (grepped), identical
frame count/order/batching (re-derived from each clip's own frozen frame budget), and the
reference text inaccessible to the model at any point (grepped). 7 Gemini calls total;
condition A made 0 new calls, reusing frozen predictions.

**Results:**

- **5 clips tested.**
- **0/5 semantic-adequacy recoveries** (0→≥1).
- **0/5 topic-mismatch recoveries** (yes→no).
- **No genuine semantic recovery on any clip.**
- Where output changed at all, it changed to a *different* wrong answer: 3/5 clips swapped
  which wrong word or phrase was produced; 1/5 (`92V3oH63zbQ`) returned byte-identical empty
  output in both conditions; the single small WER improvement (`G19uBylwQww`, −0.0385) sits
  inside the established decoding-noise range and came from replacing a fabricated
  biographical detail with a generic greeting, not from recovering reference content.
- `FzmL8SL6Bow` is the textbook confound: **BLEU 0.2719 → 0.5051 and chrF 11.1616 → 14.3380
  while WER stayed byte-for-byte identical at 0.9615** — the model restated the *same*
  fabricated narrative in more words. Counted as no improvement.

**Conclusion: trajectory-as-structured-text-context to a generic Gemini model should be
deprioritized.** That specific, cheap-to-test approach is closed — no further calls, no
prompt tuning, no expansion to the diagnostic-12 or the 128-clip corpus.

**This does NOT conclude that pose/trajectory is useless for ASL.** D2 tested exactly one
implementation: handing raw kinematic text to a generic pretrained model that was never
trained to consume it. The remaining plausible direction is a **learned, sign-specific
temporal representation/model** that consumes the signal directly — hands, fingers, body,
face, orientation, handshape, motion, and non-manual markers — architecturally closer to
what Uni-Sign attempts. That is untested here and therefore not ruled out. It is also a
materially bigger commitment (training, not an inference-time prompt change).

Manager summary (commit-pinned):
https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/trajectory-tracking-feasibility/MANAGER_SUMMARY.md

Full D2 per-clip detail (commit-pinned):
https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/trajectory-tracking-feasibility/PHASE_D2_RESULTS.md

---

## 9. What Worked

Real positive outcomes, including ones that are not translation-quality gains:

1. **A reproducible frozen benchmark.** 128 official-test-split clips, selected by a
   deterministic pre-registered rule before any video was viewed, leakage-checked and
   checksum-frozen. Every experiment on this branch is comparable because of it.
2. **Cross-model comparison on that benchmark.** Four systems scored with one unmodified
   scorer (Curify frame baseline, Uni-Sign, OpenSLT, Gemini native video), with an explicit
   matched-126 comparability scope that is never silently collapsed into the all-scope
   number.
3. **Qualitative semantic review as a first-class metric.** The 40-clip semantic-adequacy /
   topic-mismatch review is what caught, repeatedly, that WER/BLEU/chrF movement did not
   mean improvement — and it is honestly labeled as text-only rather than ASL-expert
   annotation.
4. **Uni-Sign integrated into the frame inspector** (Task A), giving a per-clip,
   four-way qualitative view that no scorecard provides.
5. **A reusable native-video benchmark harness**: dry-run default, explicit private-data
   upload acknowledgement, resumability verified across three invocations, Files-API cleanup
   in a `finally` block, and full provenance recorded on every prediction.
6. **A real parser failure found and fixed** (§6) — a bare-JSON-array Gemini response,
   diagnosed from call-timing evidence and correctly distinguished from the Files-API
   failures it was initially pooled with, then validated end-to-end with a live retry.
7. **Trajectory extraction shown technically viable** — 5/5 clips, 1,038 frames, 0% missing
   tracking, visually confirmed down to individual finger joints.
8. **A controlled experiment cleanly ruled out a cheap approach.** D2 closed
   trajectory-as-prompt-text with a single-variable design and pre-flight verification, at a
   cost of 7 model calls. Ruling something out cheaply is a result.
9. **A clearer separation between infrastructure failure and model-quality failure.** The
   7 Files-API clips, the parser bug, and the semantic failures are now three distinct,
   separately tracked categories — surfaced as such in the inspector itself rather than
   blurred into one "unavailable".

---

## 10. What Did Not Work

- **Higher frame density did not materially fix semantics.** ~2 fps → ~8 fps moved corpus
  WER by −0.0015 on the paired-76 set, with a median per-clip delta of exactly 0.
- **Sampling and batching changes did not materially fix semantics.** Adaptive → uniform was
  flat/slightly worse with no semantic recovery. Independent → sliding windows moved WER
  1.0524 → 0.9545, but 12/12 clips stayed topic-mismatched under both arms and part of the
  movement is indistinguishable from the measured −0.0673 decoding-noise floor.
- **Native video showed no semantic recovery in the 5 scored cases so far** — 0/5 semantic
  adequacy flips, 0/5 topic-mismatch flips, despite WER improving numerically on 2 of them.
- **Trajectory structured context to generic Gemini produced 0/5 semantic recovery** — and
  in the one case where BLEU/chrF rose, WER was byte-for-byte identical.

**None of these is a universal negative conclusion.** Each is a statement about a specific
intervention, at a specific sample size, in a specific tested setup. In particular: 5/12 and
5/5 are small, the native-video result is incomplete by construction, and "no signal
observed here" is not "no signal exists."

---

## 11. Key Technical Conclusion

The five interventions summarized in §4, §6 and §8 (frame density, sampling strategy, frame
grouping/context, native video input, and trajectory context) share one property: **none
produced a case where a wrong prediction became a correct one.** Across all of them, the
failure shape stayed the same: fluent English about the wrong topic, with 0/40 clips in the
qualitative review ever showing the "correct-meaning-different-wording" pattern that would
indicate comprehension.

**The repeated failure pattern suggests that the bottleneck is unlikely to be solved only by
feeding more frames, changing sampling, or textualizing trajectory information. The stronger
remaining hypothesis is that ASL needs a sign-specific learned temporal/linguistic
representation rather than generic multimodal prompting alone.**

This is a **hypothesis supported by the current evidence, not a final proof.** What would
strengthen or break it, and what is genuinely still unknown:

- The **true ASL-specific failure taxonomy** — whether errors originate in handshape,
  motion, fingerspelling, numbers, non-manual markers, or unanchored hallucination — has
  never been established. It requires an ASL-fluent reviewer watching the signing; no
  text-only review can settle it.
- **Native video is only 5/12 tested.** The 7 missing clips could in principle change the
  native-video verdict.
- **Model choice is untested.** Every Gemini experiment on this branch used
  `gemini-3.6-flash`. Nothing here establishes how a different or stronger vision-language
  model would perform.
- **The learned-representation hypothesis itself is untested here.** Uni-Sign is the closest
  architectural data point we have, and it also sits near WER 1.0 on this benchmark — which
  is a caution against assuming a learned pose encoder automatically solves this, not a
  refutation of the hypothesis.

---

## 12. Current Blockers

1. **7 of 12 native-video diagnostic clips blocked at the Gemini Files API**, before model
   inference. Same 7 clip IDs failed identically on two independent attempts; local
   `ffprobe` inspection found no distinguishing property. Root cause unresolved — transient/
   account-side degradation vs. clip-specific processing incompatibility, neither confirmed.
   **This keeps the manager's §7 P0-4 12-case decision gate unanswerable.**
2. **Commercial SignCaption / Sign-Speak API access and permission unresolved.** No
   credentials, endpoint, schema, auth, pricing or rate limits; prior outreach unanswered;
   and a standing, uncleared ToS "competitive product" clause that gates any further
   technical evaluation. All external, none resolvable from the repository.
3. **No human ASL-fluent gold review.** All semantic judgment to date is text-only English
   reference vs. English prediction, explicitly labeled as such. It cannot distinguish a
   visually grounded misread from an ungrounded hallucination, and it cannot validate any
   ASL-specific hypothesis (handshape, fingerspelling, non-manual markers). This blocker has
   been flagged repeatedly and remains open.
4. **Gemini spend is a live constraint.** The 8 fps ablation already hit an external billing
   cap at 76/128 clips; any further Gemini work should be sized and approved first.

---

## 13. Recommended Next Steps

1. **Do not spend more time on simple Gemini prompt / trajectory-text tuning.** Five axes
   have been tested without semantic recovery; further variations of the same class are the
   least likely use of effort. This explicitly includes 5 fps/10 fps density variants and
   further trajectory-prompt phrasing.
2. **If the native-video Files API becomes reliable, finish the remaining 7 diagnostic
   clips** before deciding the manager's 12-case gate. The command is unchanged and
   resumability will skip the 5 valid clips automatically. If a third identical attempt
   fails on the same 7 IDs, treat that as evidence for a clip-specific incompatibility worth
   raising with Gemini API support rather than retrying indefinitely.
3. **If SignCaption / Sign-Speak vendor access is granted, benchmark it as a commercial
   ceiling/reference** on the frozen 128-clip set — it is the only available read on what a
   purpose-built commercial ASL system achieves on our benchmark. Order matters: written ToS
   clearance on the competitive-product clause first, benchmark-use permission second,
   technical evaluation third.
4. **Investigate a learned sign-specific temporal representation** — pose + handshape + face
   modeling, i.e. a model trained to consume the motion signal directly — *before* scaling
   any further trajectory experiments. Start by understanding why Uni-Sign, which already
   consumes exactly this signal, still fails on this benchmark: that analysis is cheap,
   uses assets already on disk, and would tell us whether the hypothesis in §11 survives
   contact with our own closest data point.
5. **Preserve the frozen benchmark and the diagnostic inspector as the decision framework.**
   Every conclusion in this report depends on the benchmark staying frozen and on
   interventions being judged by semantic adequacy rather than WER movement. Keep both.

**Not recommended:** immediately training a large new model. The repository evidence does
not yet support that commitment — the failure mode has not been ASL-diagnostically
characterized, the native-video evidence is incomplete, and our one learned-pose data point
(Uni-Sign) also fails on this benchmark. Item 4 above is the cheap investigation that would
either justify or defuse that step.

---

## 14. Deliverables

**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Commit:** `01cfd054faa67bd4980ea606e100bcfdf5f1b96e` — *eval(asl): add native-video and trajectory diagnostics*
**No PR created.** No push of this report. `curify-studio` not modified at any point.

**Code**

- `asl-translator/asl-eval/run_native_video.py` — native-video runner (Files API, 1 call/clip, dry-run default, parser fix)
- `asl-translator/evaluation/run_native_video_how2sign_v2_benchmark.py` — native-video benchmark driver (resume, scoring, matched-126)
- `asl-translator/evaluation/compare_how2sign_v2_systems.py` — 4-system scorecard + pairwise comparisons, read-only
- `asl-translator/evaluation/run_trajectory_augmented_experiment.py` — D2 controlled experiment driver
- `asl-translator/asl-eval/trajectory_probe/{extract_trajectory,summarize_trajectory,render_overlay,render_trajectory_text,keypoint_schema}.py` — D1 tracking/QA/rendering
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/build_inspector.py` — inspector builder (Task A)

**Artifacts**

- `asl-translator/data/public_benchmarks/how2sign_v2/` — the frozen 128-clip benchmark
- `asl-translator/evaluation/results/how2sign_v2/{curify_gemini_3_6_2026_09_04,curify_gemini_3_6_2026_09_06_8fps,unisign,openslt,curify_gemini_native_video_2026_09_10,curify_gemini_trajectory_augmented_2026_09_10}/`
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/` — inspector, diagnostic-12 and taxonomy-40 sets, controlled ablations, trajectory probe artifacts
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/FINAL_TEMPORAL_DIAGNOSIS.md` — consolidated temporal diagnosis
- `docs/daily_report/9.9/asl-evaluation-driven-improvement/` — prior work report and 2-minute summary

**Commit-pinned GitHub links**

- Inspector:
  https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/index.html
- Native-video blocker/status:
  https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md
- SignCaption / Sign-Speak checklist:
  https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/signcaption-signspeak-research/CHECKLIST.md
- Trajectory manager summary:
  https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/trajectory-tracking-feasibility/MANAGER_SUMMARY.md
- Trajectory D2 details:
  https://github.com/super-inbox/visual-search-adhoc/blob/01cfd054faa67bd4980ea606e100bcfdf5f1b96e/docs/daily_report/9.10/trajectory-tracking-feasibility/PHASE_D2_RESULTS.md

---

## 15. Final Status Table

| Task | Status | Main Result |
|---|---|---|
| A — Uni-Sign inspector | **COMPLETE** | Each diagnostic clip page now shows reference, Curify frame baseline, Uni-Sign and Gemini native video side by side with word-level diffs and per-system WER/CER; real empty predictions are visually distinguished from unavailable results, with Files-API failures named specifically. Read-only — no model is rerun. |
| B — Gemini native-video | **PARTIAL / INFRASTRUCTURE-BLOCKED** | Full harness implemented (Files API, 1 call/clip, adapted production prompt, scoring, private-data guard, resume, cleanup). A real bare-JSON-array parser bug was found, fixed and validated end-to-end. 5/12 clips scored, 7/12 blocked at the Files API before inference (root cause unresolved); 0/5 semantic recoveries; the §7 P0-4 12-case gate is still inconclusive. |
| C — SignCaption / Sign-Speak | **RESEARCH COMPLETE / ACCESS PENDING** | Full local paper trail established: product/API exist, prior outreach unanswered, prior accuracy measured only from offline SRT exports. Credentials, endpoint/schema, auth, pricing, rate limits, benchmark permission and competitive-product ToS clearance all still require vendor confirmation. |
| D — Trajectory tracking | **POC COMPLETE** | D1: RTMPose extraction 5/5 clips, 1,038 frames, 0% missing tracking on body/left hand/right hand, visual QA passed — tracking is feasible on this probe set. D2 (negative): trajectory-as-structured-text to generic Gemini gave 0/5 semantic-adequacy and 0/5 topic-mismatch recoveries; that specific approach is deprioritized, while a learned sign-specific temporal representation remains untested and plausible. |

---

## 16. One-Paragraph Manager Takeaway

Over this work stream we built a frozen, leakage-checked 128-clip How2Sign v2 benchmark,
scored four systems on it, and used it to test five distinct ways of giving a model better
visual input: more frames, differently-chosen frames, differently-grouped frames, the raw
video itself, and explicit hand/body trajectory data. None of them turned a wrong
translation into a correct one, and the qualitative review shows why that matters — the
failure is the model confidently describing the wrong topic, not phrasing a correct read
badly, so the WER and BLEU movements we did see were not improvements. Of the four
2026-09-10 manager tasks, the Uni-Sign inspector integration is complete and is now the
main tool for comparing systems case by case; the Gemini native-video benchmark is built
and working but only 5 of 12 diagnostic clips are scored, with 7 blocked before inference by
an unresolved Gemini Files API problem, so that decision gate genuinely cannot be called
yet; SignCaption/Sign-Speak is fully researched locally but needs vendor credentials and
written ToS clearance before any benchmark is possible; and trajectory tracking works
technically (0% missing tracking on all 5 probe clips) while the cheap way of using it —
handing the numbers to a generic Gemini as prompt text — was cleanly ruled out on 5 clips.
None of this is a failed project: the search space is materially narrower, the infrastructure
is reusable, and the evidence now points, as a hypothesis rather than a proof, toward ASL
needing a sign-specific learned temporal representation rather than more or better-formatted
input to a general-purpose multimodal model. The cheapest next step is not a new experiment
but an analysis we can run against assets already on disk: understand why Uni-Sign, which
already consumes exactly that pose signal, still fails here.
