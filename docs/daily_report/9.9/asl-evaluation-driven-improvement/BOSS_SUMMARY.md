# ASL Diagnosis — 2-Minute Summary

**Full detail:** `WORK_REPORT.md` (this folder). **No Gemini call, no code
change, no result modification** was made to produce either document —
everything below is read from already-committed artifacts on
`baobao/asl-temporal-ablation-2026-09-06` @ `22bb867`.

## What you asked for

1. Look at concrete examples, not just aggregate WER.
2. P0-2: controlled ablations on the "2fps / independent 24-frame batch"
   architecture before training anything — does better temporal evidence
   move WER/semantic accuracy?
3. P0-3: a 30–50 clip qualitative error taxonomy, tracking semantic adequacy
   and hallucination rate (since WER alone is misleading — it cannot
   distinguish a correct answer that's merely worded differently from a
   fluent but semantically wrong output).
4. Later: does the ASL pipeline in a shared "evaluation-driven
   self-improvement" ChatGPT conversation help?

## What we did

- Built a deterministic **12-clip** frame-inspectable diagnostic set and a
  **40-clip** qualitative taxonomy sample, both reused across every
  experiment below.
- Ran a **text-only, explicitly-labeled** semantic review (not ASL-expert
  annotation — we don't have that capability yet).
- Ran three controlled ablations against the frozen 128-clip How2Sign v2
  baseline (WER 0.9762, 128/128 predictions).
- Compared the resulting gap analysis against the shared conversation's ASL
  pipeline.

## Key numbers

| Experiment | Result |
|---|---|
| 40-clip semantic review | 92.5% wrong/unrelated meaning, 90% topic mismatch, **0%** "correct meaning, different English" |
| Density: 2fps → 8fps (76 clips) | WER 0.9730 → 0.9715 — **flat** |
| Sampling: adaptive → uniform (12 clips) | WER 1.0524 → 1.0594 — **flat/slightly worse**, no semantic recovery |
| Batching: independent → sliding windows (12 clips) | WER 1.0524 → 0.9545 — **moves numerically, but 12/12 clips stay topic-mismatched under both arms**; part of the movement matches measured decoding noise (-0.0673 on architecturally-identical clips) |

## Main conclusion

The benchmark's dominant failure is the model describing **the wrong topic
entirely**, not mis-wording a correct read. None of the three frame-based
interventions tested (more frames, differently-sampled frames, differently-batched
frames) produced a case where a wrong prediction became a correct one. This
does **not** mean temporal information never matters — it means these three
tested interventions didn't fix it.

## What the newly-shared GPT conversation adds

Its evaluation-driven-improvement framing is **consistent with, not new
relative to**, what we already did — the three ablations above are three
manually-executed, human-gated iterations of exactly that loop, and its own
recommended P0 (build a diagnostic set before automating) is already done.
Two of its ASL-specific ideas are genuinely new and untested here: (1)
full-body + high-resolution hand-crop input, (2) native/direct video input.
Its multi-channel recognition and fingerspelling-recognizer+reranking ideas
are also new, but high-effort and blocked on ASL-fluent review to validate.

## What we should NOT repeat

- More frame-rate tuning (5fps/10fps) — would likely repeat the flat
  2fps-vs-8fps result.
- Whole-frame motion-weighted sampling vs. uniform sampling — tested, no
  effect. Higher frame density under the same coarse whole-frame motion
  signal — also tested, no effect. **Hand-specific motion tracking itself
  (as opposed to our whole-frame pixel-diff proxy) remains untested** — it's
  a different, finer-grained signal, just lower priority given the coarse
  version of the same idea didn't move the dominant failure at two
  densities.
- Generic sliding-window/overlapping-context re-batching — already tested,
  WER moved but zero semantic recovery.

## Proposed next experiment

**Full-body + high-resolution hand-crop dual-stream** on the existing 12
diagnostic clips — reuse existing timestamps/batching/model exactly, only
add a cropped hand-region image alongside each existing frame. This is a
**spatial**, not temporal, axis — untested and orthogonal to everything
above. Cheap (same call count, modestly larger payload).

- **Promote if:** ≥3/12 clips move semantic_adequacy 0→≥1, OR ≥25% flip
  `reference_topic_mismatch` yes→no.
- **Reject if:** no clip changes category, or movement stays within the
  known noise floor.

Second-priority, larger option: a small native-video Gemini probe (also
new, but bigger cost/unknown token profile).

## Current blocker / limitation

- No ASL-fluent reviewer yet — we cannot confirm whether failures are
  handshape/motion/fingerspelling/facial-marker-specific or genuine
  hallucination. This blocks validating any of the "genuinely new"
  multi-channel ideas.
- Gemini monthly billing cap was hit once already during the 8fps
  experiment (`docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md`)
  — any further Gemini spend should be sized and confirmed before running.
- **Recommendation: ask you before building/running the hand-crop
  experiment** — it needs a new local dependency and a small amount of
  additional Gemini quota.

## References

- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/FINAL_TEMPORAL_DIAGNOSIS.md` — full consolidated diagnosis
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/MANAGER_SUMMARY.md` — prior short summary (temporal ablations only)
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/EXPERIMENT_INDEX.md` — full file map
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/TEXT_SEMANTIC_REVIEW_SUMMARY.md` — 40-clip semantic review detail
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/controlled_ablation/adaptive_vs_uniform_2fps/ADAPTIVE_VS_UNIFORM_2FPS.md`
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/controlled_ablation/independent_vs_sliding/INDEPENDENT_VS_SLIDING.md`
- `docs/daily_report/9.6/asl-temporal-ablation/BLOCKER_STATUS.md` — Gemini billing cap record
