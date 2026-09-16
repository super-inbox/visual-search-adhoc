# Curify ASL — Manager Summary
Date: 2026-09-15

## Goal

ASL video → reliable sign-language understanding → accurate English caption/text. This
is currently benchmark/evaluation/diagnosis work, not training a new model.

## What We Built

- A frozen, 128-clip How2Sign v2 benchmark with byte-verified inputs and fixed
  references — the shared measuring stick for every system compared below.
- A 12-clip diagnostic inspector showing reference, Curify frame baseline, Uni-Sign, and
  Gemini native-video side by side (COMPLETE).
- A native-video benchmark harness (Files API, resumable, one call per clip) — found and
  fixed a real parser bug along the way (Gemini can return a top-level JSON array, not
  just an object).
- A pose/trajectory extraction pipeline, shown feasible on a 5-clip probe (5/5 success,
  0% missing tracking).
- An expanded SignCaption manual pilot: 5 clips → 15 clips (Batch-2 +10, manually
  uploaded, no API automation), plus a corrected BLEU-rounding fix.
- A Uni-Sign inference-parameter audit (today), answering the open question of whether
  Uni-Sign's predictions can be tuned.

## Key Results

**Matched-126 (full frozen benchmark):**

| System | WER | CER | BLEU | chrF |
|---|---|---|---|---|
| Curify / Gemini 3.6 | 0.9761 | 0.8070 | 0.13 | 11.30 |
| Uni-Sign | 0.9801 | 0.7601 | 5.40 | 22.83 |
| OpenSLT | 1.0246 | 0.7689 | ~0.96 | 18.59 |

**Matched-15 (SignCaption combined pilot):**

| System | WER | CER | BLEU | chrF |
|---|---|---|---|---|
| Curify (frame) | 0.9978 | 0.8637 | 0.548 | 12.62 |
| Uni-Sign | 0.9332 | 0.7217 | 5.0763 | 20.66 |
| SignCaption | 0.9109 | 0.7631 | 1.4654 | 16.55 |

**Matched-8 (native-video overlap subset):**

| System | WER | CER | BLEU | chrF |
|---|---|---|---|---|
| Curify (frame) | 1.0388 | 0.9003 | 0.9038 | 14.09 |
| Uni-Sign | 0.9181 | 0.6812 | 2.5923 | 19.55 |
| Gemini native-video | 0.9784 | 0.8486 | 0.1868 | 7.47 |
| SignCaption | 0.8922 | 0.7596 | 1.9084 | 16.39 |

**Reading these tables:** SignCaption beats the Curify frame baseline (matched-15) and
Gemini native-video (matched-8) on every metric. SignCaption does **not** beat Uni-Sign
overall — Uni-Sign wins CER/BLEU/chrF in both pilots; SignCaption only wins WER. All
matched-15/8 numbers are a small, stratified manual pilot, not the full 128-clip
benchmark.

## Latest Uni-Sign Parameter Answer

Direct answer to: *"Uni-Sign prediction 这个模型在调用时 有参数 可以控制吗?"*

- **Yes** — Uni-Sign's decoding is controllable, in principle.
- Only `num_beams` and `max_new_tokens` are currently wired through to the model at all.
- Our existing frozen benchmark used `num_beams=4`, `max_new_tokens=100` — the official
  upstream defaults.
- **No tuning was ever done** — these values were never changed after seeing any
  benchmark output, on any clip.
- The underlying mT5 model supports more decoding knobs (repetition penalty, n-gram
  blocking, sampling, temperature, top-p/top-k), but Uni-Sign's own wrapper code does not
  forward any of them — using them would require a source-code change, not a flag.
- Proposed next step (not yet run): a 3-arm beam-width ablation (`num_beams` = 1, 4, 8;
  `max_new_tokens` fixed at 100) on the existing frozen 12-clip diagnostic subset.

## Main Technical Conclusion

Generic Gemini approaches (frame sampling, denser frames, native full-video, trajectory
text-context) all remain semantically weak — none produced a genuine topic/semantic
recovery in the setups tested. Specialized sign-language systems (Uni-Sign, SignCaption)
show clearly stronger signal on lexical metrics. The evidence increasingly favors a
learned, sign-specific temporal/linguistic representation over further generic
prompt/frame engineering — but Uni-Sign's own results are still well below its published
literature, so decoding config, checkpoint, and preprocessing need to be ruled out with
controlled experiments (starting with the beam-width ablation) before treating that gap
as an architecture conclusion.

## Current Blockers

- Gemini native-video: 7/12 diagnostic clips still blocked at the Files API stage.
- SignCaption: no written vendor/ToS clearance for benchmark use — raw Batch-2 `.srt`
  exports stay local/untracked, not committed deliverables.
- No fluent-ASL expert has reviewed semantic adequacy anywhere in this project yet; all
  scoring so far is text-only or single-reviewer.
- The Uni-Sign inference environment (conda env, checkpoint, pinned repo) no longer
  exists on this machine and would need to be rebuilt to run any new ablation.
- Local Uni-Sign metrics are far below published literature — cause not yet isolated.

## Recommended Next Steps

1. Stop tuning generic Gemini prompts/frame sampling — consistently unproductive so far.
2. Run the Uni-Sign beam-width ablation (1/4/8) on the diagnostic-12 subset.
3. If beam width shows no effect, investigate Uni-Sign's input side (256-frame cap,
   pose-only vs. RGB+pose, checkpoint/protocol fidelity).
4. Resolve SignCaption vendor permission before expanding that pilot further.
5. Keep the frozen benchmark and inspector as the standing decision framework.
6. If continuing trajectory work, move toward a learned sign-specific model, not more
   trajectory-to-text prompting.

## Deliverables

- `docs/daily_report/9.15/ASL_COMPLETE_WORK_REPORT.md` (full report)
- `docs/daily_report/9.15/ASL_MANAGER_SUMMARY.md` (this file)
- `docs/daily_report/9.15/unisign-inference-parameter-audit/README.md` (not yet
  committed — local only as of this report)
- Branch: `baobao/asl-temporal-ablation-2026-09-06`, HEAD `fdc2872`, no PR open.
