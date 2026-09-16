# Uni-Sign inference/decoding parameter audit — 2026-09-15

**Status: audit only.** No Uni-Sign inference was run, no prediction was modified, no
128-clip benchmark was run, nothing was committed or pushed. This answers manager
question (c): *"这个模型在调用时 有参数 可以控制吗?"* ("does this model have parameters
that can be controlled at call time?") for Uni-Sign specifically.

**Sources used (all read-only):**
- Our own run provenance: `docs/daily_report/9.2/asl-baselines/results/run_metadata.json`,
  `docs/daily_report/8.31/asl-next-baseline/results/UNISIGN_ONE_CLIP_RESULT.md`,
  `docs/daily_report/8.31/asl-next-baseline/results/raw_output.txt` (full argparse
  `Namespace(...)` dump from our actual one-clip run).
- Upstream Uni-Sign source, fetched read-only at our pinned commit
  `eed438bcb49e30405cd6ccdfcccca330c134e830`
  (https://github.com/ZechengLi19/Uni-Sign): `models.py`, `demo/online_inference.py`,
  `fine_tuning.py`, `utils.py`, `config.py`, `datasets.py`.
- `google/mt5-base`'s own `generation_config.json` / `config.json` on Hugging Face (to
  determine which decoding fields the checkpoint itself overrides vs. leaves at library
  defaults).
- **No local Uni-Sign checkout, conda env, or checkpoint exists on this machine right
  now** — the `unisign-cpu-arm64` env and `<scratchpad>/unisign_run/` directory referenced
  in our own docs were built in a prior session/machine and are gone. This audit is based
  entirely on committed documentation plus a fresh read-only fetch of the pinned upstream
  commit, not on a live local install.

---

## 1. Can Uni-Sign prediction parameters be controlled? (plain language)

**Yes, but only two of them, and "controlled" means editing a hardcoded number in the
Uni-Sign source file, not passing a CLI flag or config option.** Uni-Sign's own scripts
do not expose `--num_beams` or `--max_new_tokens` as command-line arguments anywhere.
Both values are literal integers baked into the `.generate(...)` call inside the script
you run. Every other common decoding knob (repetition penalty, length penalty, sampling,
temperature, top-p/top-k, no-repeat-ngram blocking, early stopping) is not wired through
Uni-Sign's wrapper at all — even the underlying mT5 model supports them, Uni-Sign's own
`generate()` method physically does not forward them, so they silently fall back to the
`transformers` library's global defaults (effectively "off").

## 2. Which parameters are actually exposed today?

Only `num_beams` and `max_new_tokens`, and "exposed" overstates it — they are hardcoded
literals at the two call sites, not flags:

```python
# models.py:313-321 (Uni_Sign.generate — the ONLY two kwargs this method accepts/forwards)
@torch.no_grad()
def generate(self, pre_compute_item, max_new_tokens, num_beams):
    ...
    out = self.mt5_model.generate(inputs_embeds=inputs_embeds,
                                   attention_mask=attention_mask,
                                   max_new_tokens=max_new_tokens,
                                   num_beams=num_beams)
    return out
```
```python
# demo/online_inference.py:125-127 (call site — literal values, not CLI-derived)
output = model.generate(stack_out, max_new_tokens=100, num_beams=4)

# fine_tuning.py:263-265 — identical literals
output = model_without_ddp.generate(stack_out, max_new_tokens=100, num_beams=4)
```

`utils.get_args_parser()` (utils.py:442-535) is the complete, exhaustive list of every
CLI flag Uni-Sign accepts. It contains **no** `--num_beams`, `--max_new_tokens`,
`--length_penalty`, `--repetition_penalty`, `--do_sample`, `--temperature`, `--top_p`,
`--top_k`, `--no_repeat_ngram_size`, or `--early_stopping` flag. Confirmed by fetching
and grepping the actual file at the pinned commit — this is not inferred from a README.

## 3. What values did our current benchmark use?

The frozen 128-clip Uni-Sign benchmark (and both smaller pilots before it) used:

| Field | Value | Provenance |
|---|---|---|
| Checkpoint | `how2sign_pose_only_slt.pth` | `run_metadata.json` §unisign |
| Mode | **pose-only** (`rgb_support=False`) | confirmed in argparse dump, `raw_output.txt:3` |
| `num_beams` | 4 | hardcoded literal, matches upstream default |
| `max_new_tokens` | 100 | hardcoded literal, matches upstream default |
| Everything else HF `generate()` accepts (`length_penalty`, `repetition_penalty`, `do_sample`, `temperature`, `top_p`, `top_k`, `no_repeat_ngram_size`, `early_stopping`) | **library defaults** (`do_sample=False`, `repetition_penalty=1.0`, `length_penalty=1.0`, `no_repeat_ngram_size=0`, `early_stopping=False`) | not passed by Uni-Sign's wrapper at all; `mt5-base`'s own `generation_config.json` sets only `decoder_start_token_id`/`eos_token_id`/`pad_token_id`, no decoding-field overrides — confirmed via fresh HF fetch |
| `seed` | 42 | argparse **default** (`--seed`, default=42, `utils.py:486`), never explicitly overridden by us — confirmed via literal `Namespace(..., seed=42, ...)` in our own `raw_output.txt:3` |
| Pinned repo commit | `eed438bcb49e30405cd6ccdfcccca330c134e830` | `run_metadata.json` |
| Pose extractor | `rtmlib` `Wholebody`, `mode="lightweight"`, RTMPose, 133 keypoints (body+hands+face), **every video frame processed, no stride/subsampling** | `demo/online_inference.py:70-96` (`pose_extraction()` reads every frame via `cap.read()` in a loop, no skip logic); confirmed 263/263 frames processed in our own run, `raw_output.txt:10-12` |
| Input pose-sequence cap | `max_length=256` frames (argparse default) — if a clip's pose sequence exceeds 256 frames, **`random.sample()` subsamples down to 256, seeded by the global `seed=42`** | `datasets.py:606-641` (`S2T_Dataset_online`, the class `online_inference.py` actually uses) |
| Not tuned | Confirmed explicitly in our own docs: *"num_beams=4 and max_new_tokens=100 are the documented defaults and were not changed after seeing any benchmark output, on any clip."* | `run_metadata.json:83` |
| Matches official upstream defaults? | **Yes** — `fine_tuning.py`'s own evaluation call uses the identical `max_new_tokens=100, num_beams=4` literals | `fine_tuning.py:263-265` |

Nothing here is inferred — every row traces to either our own committed run artifact or a
grep hit against the pinned upstream file.

## 4. Which parameters are worth testing?

**Worth testing (a real code edit, small, mechanically simple, addresses an observed
failure mode):**
- **`num_beams`** — cheap to vary (1 vs. 4 vs. 8), directly implicated by the repetition-
  loop failure mode already observed on our one-clip pilot ("mascara brush" repeated 4x
  near-verbatim — see `UNISIGN_ONE_CLIP_RESULT.md`), a textbook beam-search degeneration
  symptom.
- **`max_new_tokens`** — already diagnosed as a real, quantified problem: truncation
  (no terminal punctuation) rises from 3.3% of clips <5s to 65.0% of clips 15–31s, tied
  directly to hitting this cap (`run_metadata.json:11`). Worth a follow-on experiment,
  but per the conservative decision rule below, only *after* beam width is settled.

**Worth testing but requires adding new code, not just changing a number** (Uni-Sign's
`generate()` wrapper does not forward these at all — you'd add parameters to the method
signature and the `mt5_model.generate(...)` call):
- `no_repeat_ngram_size` — directly targets the observed repetition-loop pattern; would
  need to be added to `models.py`'s `generate()`.
- `repetition_penalty` — same category, same motivation.

**Lower priority / defer:** `length_penalty`, `do_sample`/`temperature`/`top_p`/`top_k`
(sampling would trade determinism for diversity — not clearly motivated by anything
observed yet), `early_stopping` (only affects beam search's stopping heuristic, weak
expected effect at `num_beams` this small).

## 5. What cannot be fixed by decoding parameters?

Two failure modes already documented on our existing predictions are **not** decoding
issues and won't move with any `generate()` kwarg:

- **Topic fabrication** — the one-clip pilot's prediction confidently describes an
  unrelated topic ("mascara brush") absent from the reference entirely. This is a
  content/grounding failure (checkpoint or input-representation), not a search failure —
  changing how the beam searches among the model's own token probabilities cannot fix the
  model being confident about the wrong topic.
- **Input frame subsampling for longer clips** — any clip whose pose sequence exceeds
  `max_length=256` frames gets randomly subsampled before it ever reaches the decoder
  (`datasets.py:640-641`). At typical How2Sign frame rates this affects most clips longer
  than roughly 8–10 seconds — plausibly compounding with (not explaining away) the
  `max_new_tokens=100` truncation pattern on the same long-clip population. This is a
  preprocessing/input-representation issue, invisible to any decoding-parameter change.
- **Checkpoint/domain fit** — whether `how2sign_pose_only_slt.pth` itself has learned the
  right content mapping for our specific 128-clip pool is a training/fit question, not a
  decoding-time question.

**Distinguishing the three categories, per the manager's ask — no causality claimed yet:**

| Category | Candidate evidence already on hand | Decoding-fixable? |
|---|---|---|
| Prediction search/decoding | Repetition-loop pattern (4x "mascara brush"); `no_repeat_ngram_size=0`, `repetition_penalty=1.0` (both off) | Plausibly yes |
| Checkpoint/model | Confident fabrication of an unrelated topic on a clip with no numbers/fingerspelling | No |
| Preprocessing/input-representation | `max_new_tokens=100` truncation scaling with duration; `max_length=256`-frame random subsampling for long clips | No |

This table separates *where the evidence points*, not a conclusion about which one
dominates. All three could be contributing simultaneously.

## 6. Proposed minimal experiment (NOT run)

**Feasibility check first:** re-running Uni-Sign requires rebuilding an environment that
no longer exists on this machine (conda env `unisign-cpu-arm64`, the pinned repo clone,
`mt5-base` weights ~2.33GB, and the `how2sign_pose_only_slt.pth` checkpoint ~1.19GB,
CC BY-NC-4.0 research/eval-only). This is a real setup cost before any of U1/U2 can run;
Arm U0 alone requires no new inference.

**Diagnostic-12 subset compatibility:** confirmed. All 12 clips in
`asl-translator/evaluation/diagnostics/phase1_temporal_ablation/diagnostic_12_clips.csv`
already have a frozen, exact-provenance Uni-Sign prediction in
`docs/daily_report/9.2/asl-baselines/results/unisign_predictions.jsonl` (checked
programmatically: 12/12 present). This subset was originally selected from Curify's WER
distribution, not Uni-Sign's, but it is the same frozen 12 clips already reused for the
native-video / SignCaption diagnostics, so reusing it here keeps the clip set consistent
across every system this project has already ablated.

### Ablation matrix

| Arm | `num_beams` | `max_new_tokens` | Checkpoint | Pose/RGB | Preprocessing | Clip set | Source |
|---|---|---|---|---|---|---|---|
| **U0** (baseline) | 4 | 100 | `how2sign_pose_only_slt.pth` | pose-only | rtmlib, all frames, `max_length=256` cap, `seed=42` | diagnostic-12 | **Reuse verbatim** from `unisign_predictions.jsonl` — exact provenance match, no new inference needed |
| **U1** | 1 | 100 | same | same | same | same | New inference required |
| **U2** | 8 | 100 | same | same | same | same | New inference required |

Everything held fixed across arms per the manager's instruction: checkpoint, pose/RGB
mode, preprocessing (rtmlib extractor, frame cap, seed), references, scorer, and clip
set. Only `num_beams` changes.

### Metrics to compare, if/when run

WER, CER, sacreBLEU, chrF, output length (token/word count), empty-prediction rate,
a repetition/degeneration check (e.g., repeated-clause detection, as already flagged
qualitatively on the one-clip pilot), and semantic adequacy / topic-mismatch where the
existing manual-review process already supports it (per the SignCaption pilots' review
convention).

### Conservative decision rule (per instructions)

Only proceed into `max_new_tokens` / `length_penalty` follow-on experiments if `num_beams`
shows a meaningful signal on this 12-clip diagnostic set first. If beam width alone
resolves the repetition pattern with no WER/CER/BLEU/chrF regression, that is the
stronger, cheaper first fix to report before touching the truncation-cap question
separately.

**Not proposed here and not in scope:** editing `models.py` to add
`no_repeat_ngram_size`/`repetition_penalty` support — that requires a real code change to
the wrapper's `generate()` signature, not just varying an existing kwarg, and should only
be considered after this simpler ablation returns a result.

---

## Exact source/code locations supporting each finding

| Finding | File | Location |
|---|---|---|
| `generate()` wrapper only accepts/forwards `max_new_tokens`, `num_beams` | upstream `models.py` @ `eed438bc` | lines 313–321 |
| Hardcoded call-site literals (online inference) | upstream `demo/online_inference.py` @ `eed438bc` | lines 125–127 |
| Hardcoded call-site literals (fine-tuning eval) | upstream `fine_tuning.py` @ `eed438bc` | lines 263–265 |
| Complete CLI flag list (no decoding flags beyond none) | upstream `utils.py` @ `eed438bc` | `get_args_parser()`, lines 442–535 |
| `--seed` default = 42 | upstream `utils.py` @ `eed438bc` | line 486 |
| `--rgb_support` flag (store_true, default False) | upstream `utils.py` @ `eed438bc` | line 520 |
| `--max_length` default = 256 (input pose-frame cap, not decoding) | upstream `utils.py` @ `eed438bc` | line 523 |
| Pose extraction processes every frame, no stride | upstream `demo/online_inference.py` @ `eed438bc` | `pose_extraction()`, lines 70–96 |
| `max_length`-based random frame subsampling, seeded globally | upstream `datasets.py` @ `eed438bc` | `S2T_Dataset_online`, lines 606–641 |
| `mt5-base` generation config has no decoding overrides | `huggingface.co/google/mt5-base/resolve/main/generation_config.json` | fetched read-only 2026-09-15 |
| Our actual run's full argparse `Namespace` (seed=42, rgb_support=False, dataset=How2Sign) | `docs/daily_report/8.31/asl-next-baseline/results/raw_output.txt` | line 3 |
| Our 128-clip run's exact decoding config + "not tuned" statement | `docs/daily_report/9.2/asl-baselines/results/run_metadata.json` | `unisign` object, lines 53–94 |
| `max_new_tokens=100` truncation-vs-duration finding | `docs/daily_report/9.2/asl-baselines/results/run_metadata.json` | line 11 |
| One-clip repetition-loop qualitative finding | `docs/daily_report/8.31/asl-next-baseline/results/UNISIGN_ONE_CLIP_RESULT.md` | lines 69–73, 84–88 |
| Diagnostic-12 clip list | `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/diagnostic_12_clips.csv` | full file |
| Diagnostic-12 × Uni-Sign frozen-prediction coverage (12/12 confirmed) | `docs/daily_report/9.2/asl-baselines/results/unisign_predictions.jsonl` | checked programmatically against the CSV above |

## Files created

- `docs/daily_report/9.15/unisign-inference-parameter-audit/README.md` (this file)

## git status --short (at time of writing, before this file was staged)

```
?? asl-translator/evaluation/diagnostics/phase1_temporal_ablation/MANAGER_FINDINGS_DRAFT.md
?? asl-translator/evaluation/diagnostics/phase1_temporal_ablation/trajectory_probe/92V3oH63zbQ_5-1-rgb_front/trajectory_overlay.mp4
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/FZCEymcpq7I_14-1-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/FzQPg4aqNYc_13-1-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/G19uBylwQww_1-2-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/G1jsDl1mVvk_1-1-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/G3RvsnzQrXQ_3-10-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/fZM3IcM2Xs4_14_15_16-10-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/g05yGRoZE10_1-8-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/g0UUmEkoT1w_2-10-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/g2NA_eBUcH8_0-3-rgb_front/signcaption_result.srt
?? asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/clips/g2nvBjp0loQ_4-3-rgb_front/signcaption_result.srt
?? docs/daily_report/9.13/asl-full-benchmark-comparison/
?? docs/daily_report/9.15/unisign-inference-parameter-audit/
```

Nothing staged, committed, or pushed. No Uni-Sign inference, no 128-clip benchmark, no
prediction modification, no official Uni-Sign checkout touched (none exists locally to
touch — every upstream fact above came from a fresh, read-only fetch of the pinned
commit's raw files).
