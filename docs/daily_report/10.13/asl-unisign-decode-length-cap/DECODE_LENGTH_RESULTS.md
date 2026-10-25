# Uni-Sign decode-length-cap: results (R100 / R150 / R256)

> **Negative-result diagnostic.** This experiment tested one hypothesis, that the inference-time `max_new_tokens=100`
> cap causes the long-sequence failure, and **rejects it**. It does not identify the actual cause, and it does not test
> any training-side explanation.

**Status: COMPLETE (negative result).** The three GPU runs finished on 2026-10-14 (Tesla T4, fp16). The analysis is CPU-only and
byte-reproducible (`scripts/analyze_decode_length.py`, run twice with identical outputs). Design and decision rules:
`EXPERIMENT_PLAN.md`.

## Bottom line

**Raising `max_new_tokens` from 100 to 150 or 256 does not materially change translation quality.**

- 126 of 128 outputs are byte-identical across R100, R150 and R256.
- Only the 2 clips that hit the 100-token cap change. Both are degenerate repetition loops (`"a typical typical typical …"`
  and `"a D, a D, a D, …"`), and a bigger budget only makes the loops longer. Their scores get slightly worse.
- Full-set deltas vs R100 (R256): BLEU-4 +0.01, chrF −0.05, WER +0.97 (the WER change comes from one looping clip).
  On the long-reference subset BLEU-4 moves by +0.03 and chrF by −0.07, and WER does not change.
- The original hypothesis, that **the 100-token inference cap explains the long-sequence failure, is rejected.** This is
  outcome **C** in plan §6: few cap hits, and R150/R256 are nearly identical to R100.
- The long-reference outputs stop **on their own, by emitting EOS**. They stop short (≈33 words for references of ≥35
  words), and 71% lack terminal punctuation. This is **observed learned early stopping**: the model predicts EOS, and no
  decoding limit cuts it off. 12 of the 21 end at 48–52 generated mT5 tokens. That clustering is *consistent with* a
  length prior learned from the 50-token training-target truncation, but training was not changed here, so **that
  explanation is an untested hypothesis, not a finding** (see "Interpretation").

## 1. Verification (all passed: `metrics/verification.json`, 41/41 checks)

| Check | Result |
|---|---|
| 128 predictions, 128 refs, 128 diagnostics lines per run, all parse | pass ×3 |
| Clip order identical to `labels.test_p012_128` in predictions, refs and diagnostics | pass ×3 |
| `test_tmp_refs.txt` byte-identical across runs (sha256 `383bd315…`); equal to the raw `labels.test` text; equal to the manifest `reference_text` after the known mojibake fix (3 lines with `â€™`) | pass |
| `SHA256SUMS` (VM absolute paths, checked by basename) for pres / refs / diag | pass ×3 |
| `RUNTIME_INPUTS_A_official.sha256` lists 128 A_official PKLs and is identical in all three runs and in the pinned `results/out/` copy (sha256 `b835a2ae…`) | pass |
| Diagnostics: `max_new_tokens` = 100/150/256, decoder start id 0, `n_new_tokens` ≤ cap, `hit_cap` ⇔ (no EOS and n_gen = cap), `n_gen_tokens` = len(`gen_ids`), `pred_words` matches the text | pass ×3 |
| Launch flags identical across runs except `--output_dir` (batch 8, `--dtype fp16`, `--eval`, same checkpoint) | pass |
| `R100_GATE.json`: verdict **REPRODUCED_EXACT**, 128/128 lines identical, no hard failures. The R100 prediction file sha256 equals the committed `A_official.txt` (`d865008b…`) | pass |
| Gate re-run locally (`scripts/r100_gate.py`, sacrebleu 2.6.0): REPRODUCED_EXACT, ΔBLEU-4 0.0000, ΔchrF 0.0000 | pass |
| Analysis re-run into a separate directory: all 5 outputs byte-identical | pass |

Not re-run locally: `scripts/test_patch_cpu.py`. It needs the pristine Uni-Sign `fine_tuning.py` and the mT5 tokenizer via
`transformers`, and neither is installed on this laptop. It was run on the VM before R100 (README, step 0).

## 2. Full 128 clips

Quality is from `scripts/analyze_decode_length.py`: corpus BLEU-4 (sacrebleu 13a; it matches the official
`SLRT_metrics.sableu` value in `run.log` to 4 decimals for all three runs), corpus chrF, and corpus WER (`score_conditions.py` definition). The `log_*` columns are copied from each
run's `run.log` (official Uni-Sign scorer).

| | R100 | R150 | R256 |
|---|---|---|---|
| BLEU-4 | 9.1319 | 9.1385 | 9.1389 |
| BLEU-4 (`run.log`, SLRT sableu) | 9.1319 | 9.1385 | 9.1389 |
| chrF | 28.9939 | 28.9453 | 28.9437 |
| WER (%) | 90.96 | 91.87 | 91.94 |
| ROUGE (`run.log`) | 29.00 | 28.98 | 28.98 |
| BLEURT (`run.log`) | 0.44068 | 0.44073 | 0.44078 |
| Cap hits | **2 / 128 (1.56%)** | 1 / 128 (0.78%) | **0 / 128** |
| EOS rate | 98.44% | 99.22% | 100% |
| Generated tokens min / median / p90 / max | 2 / 28 / 51 / 100 | 2 / 28 / 51 / 150 | 2 / 28 / 51 / 154 |
| Output words min / median / p90 / max (mean) | 1 / 18 / 33.3 / 50 (19.83) | 1 / 18 / 33.3 / 76 (20.09) | 1 / 18 / 33.3 / 78 (20.11) |
| Output/reference length ratio, corpus (median clip) | 0.882 (0.917) | 0.894 (0.917) | 0.895 (0.917) |
| Repetition rate (repeated 3-gram not in ref) | 26.56% | 26.56% | 26.56% |
| Repetition-loop rate (rep3 ratio ≥ 0.15) | 14.06% | 14.06% | 14.06% |
| Truncation rate (no terminal punctuation) | 17.19% | 17.19% | 17.19% |
| Outputs identical to R100 | — | 126 / 128 | 126 / 128 |

Paired bootstrap vs R100 (clip-level, 2000 resamples, seed 0), Δ [95% CI]:

| Subset | Contrast | ΔBLEU-4 | ΔchrF | ΔWER |
|---|---|---|---|---|
| full 128 | R150 − R100 | +0.01 [−0.01, +0.02] | −0.05 [−0.12, 0.00] | +0.90 [0.00, +2.87] |
| full 128 | R256 − R100 | +0.01 [−0.02, +0.02] | −0.05 [−0.12, 0.00] | +0.97 [0.00, +3.12] |

The WER increase comes entirely from clip `g2ur4BIuN0Q_8-3` (18-word reference): its looping output grows from 50 to
76/78 words, which adds insertions. Because only 1–2 clips differ, many resamples give a delta of exactly 0, and most CIs
have one end at exactly 0. The CIs show how small the effect is. They are not evidence of a systematic effect in either
direction.

## 3. Subsets

`metrics/subset_comparison.csv` has every metric for every run × subset, with paired-bootstrap columns. Key rows:

| Subset | n | Run | BLEU-4 | chrF | WER | Cap hits | EOS | Gen tokens med / max | Words med / max | Len ratio | Rep. | Trunc. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ref ≥ 35 words** | 21 | R100 | 5.5669 | 24.1644 | 86.29 | 1 | 95.2% | 50 / 100 | 33 / 48 | 0.638 | 47.6% | 71.4% |
|  |  | R150 | 5.5967 | 24.0965 | 86.29 | 0 | 100% | 50 / 124 | 33 / 48 | 0.646 | 47.6% | 71.4% |
|  |  | R256 | 5.5967 | 24.0965 | 86.29 | 0 | 100% | 50 / 124 | 33 / 48 | 0.646 | 47.6% | 71.4% |
| ref ≥ 45 words | 14 | R100 | 2.3953 | 20.9461 | 89.01 | 1 | 92.9% | 50 / 100 | 33.5 / 48 | 0.576 | 50.0% | 85.7% |
|  |  | R256 | 2.4223 | 20.8644 | 89.01 | 0 | 100% | 50 / 124 | 33.5 / 48 | 0.586 | 50.0% | 85.7% |
| est. ref > 50 mT5 tokens ¹ | 25 | R100 | 6.4462 | 25.7338 | 84.92 | 1 | 96.0% | 50 / 100 | 33 / 48 | 0.661 | 48.0% | 64.0% |
|  |  | R256 | 6.4730 | 25.6700 | 84.92 | 0 | 100% | 50 / 124 | 33 / 48 | 0.668 | 48.0% | 64.0% |
| **> 256 frames** | 36 | R100 | 6.5535 | 26.3743 | 87.38 | 1 | 97.2% | 49.5 / 100 | 32 / 48 | 0.737 | 44.4% | 55.6% |
|  |  | R150 | 6.5669 | 26.3221 | 87.38 | 0 | 100% | 49.5 / 124 | 32 / 48 | 0.742 | 44.4% | 55.6% |
|  |  | R256 | 6.5669 | 26.3221 | 87.38 | 0 | 100% | 49.5 / 124 | 32 / 48 | 0.742 | 44.4% | 55.6% |
| > 256 frames, ref < 35 words | 15 | all three | 8.5520 | 31.6587 | 90.27 | 0 | 100% | 44 / 51 | 26 / 35 | 0.998 | 40.0% | 33.3% |
| **≤ 256 frames** | 92 | R100 | 11.1069 | 31.6850 | 94.85 | 1 | 98.9% | 22 / 100 | 15 / 50 | 1.040 | 19.6% | 2.2% |
|  |  | R150 | 10.8277 | 31.6416 | 96.74 | 1 | 98.9% | 22 / 150 | 15 / 76 | 1.059 | 19.6% | 2.2% |
|  |  | R256 | 10.8062 | 31.6382 | 96.88 | 0 | 100% | 22 / 154 | 15 / 78 | 1.060 | 19.6% | 2.2% |
| ref ≥ 35 words and ≤ 256 frames | **0** | — | not estimable: every reference of ≥ 35 words comes from a clip of > 256 frames | | | | | | | | | |

¹ Reference mT5 token counts are **estimated** as words × 1.534. That ratio is mT5 tokens per word, measured on R100's
EOS-terminated outputs. No tokenizer was available locally. This subset flags references that probably exceed the
50-token training cap. It is not exact.

The "ref ≥ 35 words ∩ > 256 frames" subset is identical to "ref ≥ 35 words" (same 21 clips). Pearson r(frames,
reference words) = 0.864.

Paired bootstrap vs R100 on the long and long-clip subsets (R256 shown). R150 deltas are within 0.01 of these, except
≤ 256 frames, where R150 gives ΔBLEU-4 −0.28 [−0.81, 0.00] and ΔWER +1.89 [0.00, +6.15]. All R150 CIs are in
`metrics/subset_comparison.csv`:

| Subset | ΔBLEU-4 | ΔchrF | ΔWER |
|---|---|---|---|
| ref ≥ 35 words (n=21) | +0.03 [0.00, +0.09] | −0.07 [−0.19, 0.00] | 0.00 [0.00, 0.00] |
| ref ≥ 45 words (n=14) | +0.03 [0.00, +0.08] | −0.08 [−0.21, 0.00] | 0.00 [0.00, 0.00] |
| est. ref > 50 tokens (n=25) | +0.03 [0.00, +0.09] | −0.06 [−0.18, 0.00] | 0.00 [0.00, 0.00] |
| > 256 frames (n=36) | +0.01 [0.00, +0.05] | −0.05 [−0.155, 0.00] | 0.00 [0.00, 0.00] |
| ≤ 256 frames (n=92) | −0.30 [−0.87, 0.00] | −0.05 [−0.15, 0.00] | +2.03 [0.00, +6.72] |

## 4. What happened to the 2 R100 cap-hit clips

| Clip | Frames | Ref words | R100 | R150 | R256 | Sentence chrF R100 → R150 → R256 |
|---|---|---|---|---|---|---|
| `G095RWKQ39g_10-1` | 978 | 69 | cap hit, 100 tok, 35 words | **EOS** at 124 tok, 43 words | EOS at 124 tok, 43 words | 7.98 → 7.67 → 7.67 |
| `g2ur4BIuN0Q_8-3` | 179 | 18 | cap hit, 100 tok, 50 words | cap hit, 150 tok, 76 words | **EOS** at 154 tok, 78 words | 11.35 → 10.27 → 10.19 |

- Both R100 outputs are already degenerate loops (rep3 ratio 0.82 and 0.88): `"We're going to use a typical typical
  typical …"` and `"I'm going to use a D, a D, a D, …"`.
- With a larger budget each loop continues with the same R100 prefix and then stops. The rep3 ratio rises to 0.85 and
  0.91, and sentence chrF falls by 0.3 and 1.2.
- Neither clip improves. Only one of the two is a long-reference clip. The other is a short (18-word, 179-frame) clip,
  so cap hits are not specific to long sequences.
- All 126 clips that ended with EOS in R100 are byte-identical in R150 and R256. In these runs, a larger length budget
  did not change any output that already terminated naturally.

## 5. Answers

**Does increasing `max_new_tokens` materially improve translation quality?** No. Full-set BLEU-4 +0.007, chrF −0.05 (R150 −0.049, R256 −0.050),
WER +0.90 / +0.97 (one looping clip), BLEURT +0.0001, ROUGE −0.02. 126/128 outputs are unchanged.

**Do the 2 R100 cap-hit clips improve?** No. Both reach EOS by R256, but only after extending a repetition loop.
Sentence chrF falls slightly for both, so by chrF neither is closer to its reference.

**Do long-reference clips become longer or better?** No. For references of ≥ 35 words, the output median stays at 33
words and the maximum at 48 words. The corpus length ratio moves 0.6385 → 0.6458, entirely from the one looping clip. chrF
changes by −0.07, BLEU-4 by +0.03 and WER by 0.00. 20 of the 21 clips are unchanged. At R256 all 21 end with EOS, and
15/21 still lack terminal punctuation.

**Do longer limits mainly create repetition or run-on output?** Yes, for the little that changes. The only added text is
repetition-loop continuation on the 2 cap-hit clips (+8 and +28 words). The repetition and loop rates do not change at
the corpus level, because both clips were already loops at R100. `G095RWKQ39g_10-1` is counted. `g2ur4BIuN0Q_8-3` is
excluded by the taxonomy rule, because its reference repeats "we're going to".

**Is the hypothesis that the 100-token inference cap explains long-sequence failure supported?** **Rejected.** The cap
binds on only 2/128 clips (1/21 long-reference clips). Removing it changes nothing material for long references.

## 6. Interpretation: four candidate mechanisms

| Mechanism | What this experiment shows |
|---|---|
| **Inference-time `max_new_tokens` cap (100)** | **Not the primary cause.** It binds on 2/128 clips, both degenerate loops. Removing it (R256: 0 cap hits, 100% EOS) changes no non-looping output |
| **Learned early stopping / EOS behaviour** | **Observed.** Long-reference outputs end by EOS, not by the cap: 20/21 at R100 and 21/21 at R256. They stop at ~33 words against references of ≥ 35 words (median clip length ratio 0.62), and 71% lack terminal punctuation (a proxy for ending mid-sentence) even though EOS was produced. Stopping is the model's own EOS prediction, not a decoding cut-off. *Why* it predicts EOS early is not established here |
| **Training-time target truncation at 50 mT5 tokens** (`models.py:282-286`, `max_length=50`) | **Plausible hypothesis, not tested and not proven.** Generated lengths cluster at 48–52 tokens: 21/128 clips overall, 12/21 long-reference clips and 6/15 long-clip short-reference clips. Outside the 2 loops, only 3 outputs exceed 52 tokens (53, 55, 62). This is *consistent with* a length prior learned from 50-token-truncated targets. But the training target length was not varied, and other explanations would produce a similar pattern, so this experiment cannot attribute the stopping to truncation. A test would need re-training or fine-tuning with a longer target `max_length` |
| **Long-context / frame-length effects** (> 256 frames, frame subsampling) | **Not separable here.** Every ≥ 35-word reference is a > 256-frame clip (r = 0.86). The 15 long clips with shorter references score close to the ≤ 256-frame clips on chrF (31.66 vs 31.69) and reach length ratio ≈ 1.0. That is weakly suggestive that reference length matters more than frame count, but n = 15 and the comparison is observational, not a test. Decoding length cannot address this axis |

What we can and cannot conclude:
- We can conclude that the inference cap is not why long references fail.
- We can say that the model stops early by predicting EOS (observed learned early stopping).
- We cannot conclude *why* it stops early. EOS behaviour shaped by the 50-token training-target truncation is a
  plausible hypothesis, and the 48–52-token clustering is consistent with it, but it is unproven. Other explanations are
  not ruled out: the training-data length distribution, and frame-length or long-context effects.

## 7. Limitations

- One run per level. All three runs used seed 42, and R100 reproduced the committed P0-12 output exactly, so the
  pipeline is deterministic at a fixed seed. Variance across seeds (random frame subsampling of > 256-frame clips) is not
  measured.
- T4 / fp16, not the official bf16.
- n = 21 long-reference clips. The bootstrap CIs are degenerate (one end at 0) because only 1–2 clips differ between
  runs.
- The "> 50 tokens" subset uses an estimated tokens-per-word ratio, not the mT5 tokenizer.
- `n_gen_tokens` counts ids before the first EOS (EOS not included).

## 8. Files

| File | Content |
|---|---|
| `results/out/A_official_mnt{100,150,256}/` | VM outputs, copied back verbatim |
| `results/out/RUNTIME_INPUTS_A_official.sha256` | Pinned runtime manifest (128 fp16 A_official PKLs) |
| `metrics/decode_length_comparison.csv` | One row per run (full 128): all metrics, `run.log` BLEU/ROUGE/BLEURT, deltas and CIs vs R100, prediction sha256 |
| `metrics/subset_comparison.csv` | Run × subset (10 subsets): all metrics, length distributions, deltas and CIs vs R100 |
| `metrics/per_clip.csv` | Per clip × run: EOS, cap hit, tokens, words, sentence chrF, rep3 ratio, prediction |
| `metrics/decode_length_summary.json` | All of the above plus change diagnostics |
| `metrics/verification.json` | The 41 verification checks and the launch flags |

Reproduce: `python3 -I scripts/analyze_decode_length.py` (defaults: `--runs-root results/out --out metrics`).
