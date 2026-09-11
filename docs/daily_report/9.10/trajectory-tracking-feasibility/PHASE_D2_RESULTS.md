# Phase D2 — Trajectory-Augmented Inference Experiment: Results

**Date:** 2026-09-10. Inference-side only. No training. No model change. 7 Gemini calls
total across the same 5 Phase-D1 clips — condition A made 0 new calls (reused frozen
predictions). Stopped after 5 clips as instructed. No commit/push. `curify-studio`
untouched.

**Gate language correction, restated:** the ≥3/5 semantic-flip reading below uses a
**proposed internal POC heuristic** (same shape as the native-video §7 P0-4 gate, for
methodological consistency only) — it is **not manager-prescribed** for this direction.
See `PHASE_D1_D2_POC_AND_EXPERIMENT_PLAN.md` §D2.3 for the full correction.

## Status: closed as a negative result — narrow scope, stated precisely

**"Explicit RTMPose-derived trajectory information supplied as structured context to the
existing generic Gemini frame pipeline produced 0/5 genuine semantic recoveries."**

No further trajectory-augmented Gemini calls, no prompt tuning, and no expansion to the
diagnostic-12 or 128-clip corpus follow from this result — this experiment is closed.

**What this does and does not reject**, split into three explicit parts:

1. **D1 — trajectory extraction feasibility: PASS.** RTMPose (via `rtmlib`) reliably
   recovers continuous hand/body trajectories from this video corpus — 0% missing
   tracking, high confidence, visually-confirmed-correct on all 5 probed clips. This
   finding stands independent of D2 and is not affected by D2's outcome.
2. **D2 — trajectory-as-structured-text-context to generic Gemini: NEGATIVE.** Appending
   an RTMPose-derived observation-level text block to the existing frame-based Gemini
   pipeline's prompt did not produce semantic recovery on any of the 5 tested clips (see
   per-clip results below). This is a negative result for *this one specific
   implementation* — a generic pretrained VLM given a short auxiliary text summary of
   tracked positions/velocities.
3. **Remaining untested, still-plausible hypothesis: a learned, sign-specific temporal
   representation.** D2 only tested handing raw kinematic text to a generic model that
   was never trained to use it. It does NOT test — and therefore does not rule out — a
   model architecture that *learns* to consume hand/body/face/handshape trajectory
   features directly (e.g., a trained temporal/graph encoder purpose-built for this
   signal, closer to what Uni-Sign's own architecture attempts, or a fine-tuned/adapted
   Gemini path). Trajectory/pose representations for ASL translation in general remain an
   open question — only the "hand it to an off-the-shelf VLM as prompt text" path is
   closed by this result.

## Pre-flight checks (all passed before any Gemini call)

1. **Exact trajectory representation** shown for `92V3oH63zbQ_5-1-rgb_front` batch 1 —
   printed via `--show-example`, reproduced in the chat transcript. Pure geometric
   observations (position samples, confidence, speed, body-relative bands, two-hand
   distance) — grepped for interpretive phrasing (`this means`, `the sign for`, etc.):
   none found.
2. **Exact prompt diff** shown: control = `[PRODUCTION_PROMPT] + [frame parts...]`;
   treatment = `[PRODUCTION_PROMPT] + [ONE trajectory text Part] + [frame parts...]` —
   same frames, same order, same count, same model/decoding config, for every batch.
3. **Reference inaccessibility** confirmed by grep: no `reference`, `local_reference_path`,
   `.srt`, `parse_srt`, or `build_transcript` identifier appears anywhere in
   `run_trajectory_augmented_experiment.py` or `render_trajectory_text.py` above the
   (separate, post-call) scoring pass.
4. **Single-variable isolation** confirmed: sampling re-derived via the same unmodified
   `probe_motion`/`segment_runs`/`allocate_timestamps` functions with each clip's own
   frozen `frame_budget` (not re-resolved) — `--plan-only` verified re-derived frame
   counts and batch counts match the frozen baseline's recorded values on all 5 clips.
5. **Planned scope:** 7 total Gemini calls (1+1+1+1+3 across the 5 clips), confirmed via
   `--plan-only` before any real call, then confirmed again by the actual run log
   (exactly 7 calls made, matching the plan exactly).

## Per-clip evaluation

### `92V3oH63zbQ_5-1-rgb_front`
- **Reference:** "What is keeping your hands inside the baseball?"
- **A (control):** "" (empty)
- **B (treatment):** "" (empty)
- WER: A 1.0000 / B 1.0000 · CER: A 1.0000 / B 1.0000 · BLEU: A 0.0000 / B 0.0000 · chrF: A 0.0000 / B 0.0000
- Pred/ref word ratio: A 0/8 · B 0/8
- Semantic adequacy: completely wrong (empty) → completely wrong (empty), **no change**
- Topic mismatch: yes → yes, **no change**
- Genuine semantic recovery: **No — identical output, byte-for-byte.**

### `Fz-N1S0swh8_2-8-rgb_front`
- **Reference:** "I'm not going to use a lot, I'm going to use very very little."
- **A (control):** "Angry"
- **B (treatment):** "Problem"
- WER: A 1.0000 / B 1.0000 · CER: A 0.9167 / B 0.9500 · BLEU: A 0.0000 / B 0.0000 · chrF: A 3.0111 / B 2.4736
- Pred/ref word ratio: A 1/16 · B 1/16
- Semantic adequacy: completely wrong → completely wrong, **no change**
- Topic mismatch: yes → yes, **no change**
- Genuine semantic recovery: **No.** Different single wrong word; CER/chrF moved slightly worse.

### `-g0iPSnQt6w_0-1-rgb_front`
- **Reference:** "Buenos Dias, I'm Bobby Larew, you didn't know I spoke Spanish, did you?"
- **A (control):** "Back in Barcelona"
- **B (treatment):** "bronze"
- WER: A 1.0000 / B 1.0000 · CER: A 0.8507 / B 0.9254 · BLEU: A 0.0000 / B 0.0000 · chrF: A 4.3229 / B 1.7218
- Pred/ref word ratio: A 3/15 · B 1/15
- Semantic adequacy: completely wrong → completely wrong, **no change**
- Topic mismatch: yes → yes, **no change**
- Genuine semantic recovery: **No.** Worth flagging: control's "Barcelona" has a coincidental
  thematic proximity to the reference's own "I spoke Spanish" (Spain/Spanish-language
  association — not real comprehension, a lexical accident); treatment's "bronze" has none.
  If anything this is a *worse* coincidental overlap, not better — n=1, could be pure
  decoding noise, not read as a systematic negative effect.

### `G19uBylwQww_1-2-rgb_front`
- **Reference:** "Hi, my name is Robert Segundo and today I'm going to teach you how to make one of my favorite paper airplanes, the simple one."
- **A (control):** "My name is Robert. I was born in California."
- **B (treatment):** "My name is Robert. Nice to meet you."
- WER: A 0.8077 / B 0.7692 · CER: A 0.7398 / B 0.7480 · BLEU: A 3.1963 / B 3.0704 · chrF: A 16.0795 / B 15.9750
- Pred/ref word ratio: A 9/26 · B 8/26
- Semantic adequacy: partially correct (name "Robert" recovered) → partially correct (same), **no change in category**
- Topic mismatch: yes (paper-airplane instructional content never appears in either) → yes, **no change**
- Genuine semantic recovery: **No.** The one correct element (the name) was already correct
  in control, before any trajectory information was added — not something treatment
  introduced. Treatment replaced a fabricated biographical detail ("born in California")
  with a generic greeting phrase ("Nice to meet you") that is arguably more
  register-appropriate to an introduction, but recovers no additional reference content.
  WER's small improvement (−0.0385) is inside the previously-established decoding-noise
  range for this corpus (§12.2: mean |Δ| 0.029–0.107).

### `FzmL8SL6Bow_1-8-rgb_front`
- **Reference:** "You want to go and clean up that hole you just made and now we are going to go and start winding our hole you just made and start spreading it out just like that and all the while I am pulling it out while my hands here are watching this wall here because this wall here is going to want to get out of control but I'm not going to let it, my hands are there."
- **A (control):** "I looked and saw a dog approaching. It just stood there, completely frozen. A large, fierce bear walked slowly forward."
- **B (treatment):** "I looked and reached into my pocket. Then I just froze in shock. A heavy creature slowly shuffled and walked forward, emerging into a wide open area, struggling with great difficulty."
- WER: A 0.9615 / B 0.9615 (**exactly identical**) · CER: A 0.7865 / B 0.7500 · BLEU: A 0.2719 / B 0.5051 · chrF: A 11.1616 / B 14.3380
- Pred/ref word ratio: A 20/78 · B 31/78
- Semantic adequacy: completely wrong → completely wrong, **no change**
- Topic mismatch: yes → yes, **no change**
- Genuine semantic recovery: **No — this is the clearest case of the exact confound this
  project's own §12.5 finding warns about.** Treatment restates the *same* fabricated
  narrative structure (look at something → freeze/shock → a creature/heavy thing slowly
  approaches into an open area) in more words. WER is byte-for-byte identical; BLEU and
  chrF moved up purely because the output got longer and used more varied phrasing of the
  same wrong idea — not because it got closer to the actual (wall-repair) reference topic.

## Aggregate

| | A (control) | B (treatment) |
|---|---|---|
| Semantic-adequacy flips (0→≥1) | — | **0 / 5** |
| Topic-mismatch flips (yes→no) | — | **0 / 5** |
| WER identical or worse | — | 3/5 identical, 1/5 slightly worse (CER only), 1/5 slightly better (−0.0385, within noise floor) |
| Clips where the wrong word/phrase changed | — | 3/5 (`Fz-N1S0swh8`, `-g0iPSnQt6w`, `G19uBylwQww` swapped which specific wrong text was produced) |
| Clips where BLEU/chrF moved but WER/semantics did not | — | 1/5 (`FzmL8SL6Bow`, driven by output length, not content) |

**Reading against the proposed (non-manager) internal POC heuristic (§D2.3):** 0/5 flips
clears the *rejection* reading (0 flips, WER movement within/below the established noise
floor on every clip) rather than the promotion reading (≥3/5 flips). This is a 5-clip
probe, not a claim about the full diagnostic-12 or the corpus — stated as a heuristic
reading only, not a decision, pending whatever the manager wants to do with it.

## Failure-mode analysis (explicitly requested)

- **Did trajectory information help?** No clip shows semantic-adequacy improvement or a
  topic-mismatch flip. The one clip with a small WER improvement (`G19uBylwQww`) improved
  via a more plausible-sounding fabrication (a greeting phrase), not via recovering any
  actual reference content.
- **Was it ignored?** Partially evidenced, not proven: `92V3oH63zbQ` produced a
  byte-identical empty output in both conditions — a real "ignored" signal on at least
  that one clip. On the other 4 clips the output *did* change (different wrong words),
  which is inconsistent with the block being wholly ignored — the model appears to read
  it, but not in a way that changes the underlying (wrong) high-level interpretation.
- **Did it cause new hallucinations?** The specific wrong content changed on 3/5 clips
  without becoming more correct — different, not better, hallucinations. No case produced
  a *new* fabricated claim more elaborate or more confidently wrong than control already
  was; the character stayed the same (short wrong word/phrase or a restated wrong
  narrative).
- **Did it only improve lexical metrics without recovering meaning?** Yes, cleanly, on
  `FzmL8SL6Bow`: BLEU/chrF both rose while WER stayed exactly the same and the underlying
  wrong narrative was unchanged — a textbook instance of the length-driven metric
  confound this project's own methodology already flags. This reinforces: **WER and the
  conservative semantic-adequacy/topic-mismatch judgment are the metrics that matter
  here; BLEU/chrF movement alone should not be read as evidence of improvement.**

## Files changed
New: `asl-translator/asl-eval/trajectory_probe/render_trajectory_text.py`,
`asl-translator/evaluation/run_trajectory_augmented_experiment.py`,
`asl-translator/evaluation/results/how2sign_v2/curify_gemini_trajectory_augmented_2026_09_10/predictions/*.json`
(5 files, gitignored like every other `results/` output), this document. No existing
prediction, score, or benchmark file touched. `condition A` made 0 new Gemini calls.
