# Uni-Sign decode-length-cap follow-up: experiment plan

**Status: COMPLETE (2026-10-14), negative-result diagnostic.** R100 passed the gate as REPRODUCED_EXACT (128/128 lines identical to the committed
A_official). R150 and R256 then ran. Results: `DECODE_LENGTH_RESULTS.md`. Outcome **C**: the 100-token cap is not the main cause
(2/128 cap hits; 126/128 outputs unchanged at 150/256). The design below is unchanged from the pre-run version.
Paths differ from §3 step 5: the run folders are in `results/out/`, and the analysis writes to `metrics/`.

## 1. Question

The first-pass error taxonomy (`../asl-unisign-error-taxonomy/ERROR_ANALYSIS_REPORT.md`) found three things:
- No A_official prediction is longer than about 50 words.
- 15 / 21 predictions for references of 35 words or more have no terminal punctuation.
- Clips over 256 frames score much worse, but frame count and reference length are confounded (r = 0.86).

Is the long-reference failure caused by the **inference decoding cap** (`max_new_tokens=100`)? Or is it caused by
**model behaviour learned in training**? Uni-Sign fine-tuning truncates target sentences to `max_length=50` mT5 tokens
(`models.py:282-286` at `eed438bc`), so the model never saw a full-length target for long references.

## 2. Design

One variable, three levels. The only system is A_official.

| Run | `max_new_tokens` | Purpose |
|---|---|---|
| **R100** | 100 (upstream) | Reproducibility gate. It must reproduce the committed P0-12 A_official predictions (§4) before anything else runs |
| **R150** | 150 | Moderate extension |
| **R256** | 256 | Effectively no cap. The longest reference is 100 mT5 tokens |

**Held fixed** (same as P0-12 T4/fp16):
- Code: Uni-Sign `eed438bcb49e30405cd6ccdfcccca330c134e830`
- Checkpoint: `how2sign_pose_only_slt.pth`, sha256 `1bfd5f33…`
- Inputs: the exact `/tmp/p012_fp16` tree the P0-12 T4/fp16 run read. That is the 128 A_official PKLs after the one-off float16 conversion of the pose arrays, plus `labels.test_p012_128`. The PKLs are byte-checked before every run against the runtime manifest `A_official_fp16_runtime.sha256`, which is pinned at the first preflight. The labels are byte-checked against `runner/source_prepared_inputs_A_official.sha256`, which is copied from the committed `CHECKSUMS.sha256`. Those source checksums describe the pre-conversion PKLs and serve only as provenance (README, Input lineage). The pose files are not reconverted
- Hardware and precision: Tesla T4, `--dtype fp16`
- Loop settings: batch 8, seed 42, `max_length` 256 (frame cap), `num_workers` 8, deepspeed on a single GPU
- Decoding: `num_beams=4` and all other generation defaults
- Scoring: the same scorer

**Allowed changes** (`patch/fine_tuning_decode_length.patch`, `fine_tuning.py` only):
1. `max_new_tokens` is read from `UNISIGN_MAX_NEW_TOKENS`. The default is 100, so with the variable unset the code behaves exactly like upstream.
2. Padding safeguard: `torch.ones(150-len(tgt_pres[0]))` becomes `torch.ones(max(150, max(len(t) for t in tgt_pres))-len(tgt_pres[0]))`.
   - When every output is 150 ids or shorter this builds the same tensor as upstream, which covers every R100 output (at most 101 ids).
   - For longer outputs upstream raises `RuntimeError`.
   - The padding value is EOS, which `skip_special_tokens=True` drops, so the decoded text is unchanged. `test_patch_cpu.py` checks this with the real mT5 tokenizer.
3. Diagnostics (only when `UNISIGN_DECODE_DIAG=1`): `test_decode_diag.jsonl` records, per clip, the raw generated ids before padding.
   - It also records generated-token count, EOS produced, cap hit (no EOS within `max_new_tokens`) and output word count.
   - Computing these does not touch any RNG or tensor that `generate` uses.

Not changed: model weights, training target length, beam size, any other decoding parameter, `models.py`, `datasets.py`.
The VM's existing P0-12 clone is not modified. The patch is applied in a separate git worktree.

## 3. Order and stop rule

1. Run the CPU self-test (any machine).
2. **R100 only.** `scripts/r100_gate.py` runs automatically.
3. If the verdict is `NOT_REPRODUCED`, **stop.** Diagnose the cause (flags vs the old runner, environment, inputs) before R150/R256.
   The runner refuses to start R150/R256 without a passing gate file.
4. R150 and R256.
5. Copy the three run folders back to `runs/` here and run `scripts/analyze_decode_length.py`.

## 4. R100 gate: what counts as "reproduced"

R100 is compared with the committed `../asl-p0-12-full128-fp16/predictions/A_official.txt` (sha256 `d865008b…`,
checked before and after). The checks are:

- **Structure (hard):**
  - 128 lines.
  - The same clip order in the predictions, references and diagnostics.
  - The diagnostics confirm R100 settings: `max_new_tokens` = 100, decoder start id = 0, at most 100 new tokens, a cap hit means no EOS, and word counts match the text.
  - The longest sequence is 150 ids or fewer, so the padding safeguard did nothing.
- **REPRODUCED_EXACT** if all 128 prediction lines are byte-identical. This is expected: same code path, GPU, batch, seed and workers, deterministic beam search.
- **REPRODUCED_CLOSE** if all of the following hold. These thresholds were fixed before any run.
  - At most 4 of 128 lines differ.
  - |ΔBLEU-4| ≤ 0.10, using the official `SLRT_metrics.sableu` on the VM.
  - |ΔchrF| ≤ 0.20.
  - If so, proceed. The differing clips are listed, and R100 (not the committed file) is the baseline for every R150/R256 comparison.
- **NOT_REPRODUCED** in any other case, so stop.

## 5. Analysis (`scripts/analyze_decode_length.py`)

**Subsets:**

| Subset | n |
|---|---|
| Full set | 128 |
| References ≥ 35 words | 21 |
| Clips > 256 frames | 36 |
| References ≥ 35 words and > 256 frames | 21 |
| References ≥ 35 words and ≤ 256 frames | **0** |

**Design limitation:** every reference of 35+ words comes from a clip over 256 frames, so the requested within-≥35-words
"> 256 vs ≤ 256 frames" comparison is **not estimable** on these 128 clips. The script reports it as empty.
Two supplementary subsets are added: > 256 frames with references under 35 words (n = 15), and ≤ 256 frames (n = 92).
Splitting the 36 long clips by reference length (21 vs 15) is the only within-sample handle on the confound.

**Metrics** per run and subset:

| Group | Metrics |
|---|---|
| Quality | corpus WER (`score_conditions.py` definition), corpus chrF, corpus BLEU-4 (sacrebleu 13a, the same as committed within 1e-4) |
| Termination | exact cap-hit rate, EOS termination rate |
| Length | predicted words and generated tokens (min / median / p90 / max), output/reference length ratio (corpus and median clip) |
| Repetition | repetition rate (repeated word 3-gram in the prediction but not in the reference, as in the taxonomy), repetition-loop rate (rep3 ratio ≥ 0.15) |
| Truncation | no-terminal-punctuation rate |

**Contrasts:** R150 − R100 and R256 − R100 for WER, chrF and BLEU-4, with paired clip-level bootstrap 95% CIs
(2000 resamples, seed 0, as in P0-12 `contrasts.py`).

**Change diagnostics:**
- Clips identical to R100.
- R100 EOS-terminated clips that are unchanged at a larger budget. All of them should be unchanged; any difference means beam search depends on the length budget and will be reported.
- For R100 cap-hit clips:
  - how many now end with EOS
  - how many still hit the cap
  - whether the R100 prefix is preserved
  - words added
  - repetition loops
  - change in sentence chrF

## 6. Interpretation (decided before the runs)

- **A, decoding cap:** cap hits fall, and long-reference chrF/WER improve with a bootstrap CI that excludes 0. Raising
  `max_new_tokens` is then a real low-cost intervention, and much of the "> 256 frames" penalty is decoding, not perception.
- **B, training-time truncation / learned short output:** outputs get longer, but the added text is mostly repetition or
  run-on (the repetition-loop rate rises), and chrF/WER on long references do not improve (CI includes 0 or is negative).
  The fix then needs training-side work, such as a longer target `max_length`, which is out of scope here.
- **C, natural stopping:** few or no R100 cap hits, or R150/R256 nearly identical to R100. The 100-token cap is not the
  main cause. Remaining candidates are frame subsampling above 256 frames and long-context modelling.

Mixed outcomes are reported as mixed. n = 21 for the long-reference subset, so CIs will be wide.

## 7. Known limitations

- A single run per level. Seed noise from the random subsampling of clips over 256 frames is not measured here.
- T4 / fp16, not the official bf16.
- `n_gen_tokens` counts mT5 ids up to the first EOS. It assumes that `generate()` output starts with the decoder start
  token (id 0); the gate checks this.
