# Manager Summary — ASL Temporal-Architecture Diagnosis

*Full detail: `FINAL_TEMPORAL_DIAGNOSIS.md`. No new inference was run for this summary.*

## What we tested

Baseline: Curify/Gemini 3.6, motion-weighted adaptive frame sampling (~2fps),
independent 24-frame batches. 128/128 predictions on the frozen How2Sign v2
benchmark. Against that baseline, three frame-based interventions:

| # | Intervention | Scope |
|---|---|---|
| 1 | ~4x higher frame density (2fps → ~8fps) | 76 paired clips (preliminary, billing-capped) |
| 2 | Uniform sampling instead of motion-weighted | 12 diagnostic clips |
| 3 | Overlapping sliding windows instead of independent batches | 12 diagnostic clips |

Plus: a 40-clip **LLM-assisted text-semantic review** (English reference vs.
English prediction only — not ASL-fluent visual annotation) to characterize
what's failing.

## Strongest numbers

- **Baseline corpus WER: 0.9762** (128/128 clips).
- **40-clip semantic review:** 92.5% of clips score "wrong/unrelated meaning";
  90% show a clear topic mismatch between reference and prediction; 0% show a
  "correct meaning, different wording" pattern.
- **Density (2→8fps):** corpus WER 0.9730 → 0.9715 — flat.
- **Sampling strategy (adaptive→uniform):** corpus WER 1.0524 → 1.0594 —
  flat/slightly worse.
- **Batching (independent→sliding windows):** corpus WER 1.0524 → 0.9545 —
  moves numerically, but **all 12 clips remain topic-mismatched under both
  arms**, and the architecturally-identical single-batch clips alone move by
  a mean of -0.0673 from decoding noise — a meaningful share of this
  "improvement" is not attributable to the architecture change.

## What we learned

The benchmark's dominant failure is the model describing the **wrong topic
entirely**, not mis-wording a correct read. None of the three frame-based
interventions tested — more frames, differently-sampled frames, or
differently-batched frames — produced a case where a wrong prediction became
a correct one.

## What we did NOT establish

- Whether the true cause is a handshape/motion/fingerspelling/facial-marker
  reading failure specifically — that requires an **ASL-fluent** reviewer, which
  this diagnosis explicitly does not have.
- Whether feeding Gemini the **raw video directly** (instead of extracted
  frames) would behave differently — untested.
- Whether a **different or stronger model** would do better — every test used
  the same model.

## Recommended next step

**Not** more frame-rate tuning (5fps/10fps would likely repeat the same flat
result already seen at 2→8fps). Instead, in either order:

1. A small **direct-video** Gemini probe on a few clips — tests a more
   fundamental input-formulation change than any frame-sampling variant.
2. A small **ASL-fluent expert review** of a representative clip subset — the
   only way to learn whether these are handshape/motion/fingerspelling
   failures, facial/non-manual misses, or genuine hallucination.

Neither has been implemented; both are recommendations only.
