# Chunked-decoding pilot: results

**Status: COMPLETE.** This is a partial positive mechanism result and a **failed intervention** under the fixed
success criteria.

> **Chunking can bypass Uni-Sign's short-output behavior, but frame-count-based chunking is not a robust intervention
> because it over-generates when long clips contain short linguistic content.**

- **What passed.** On the 21 long-reference targets, chunking mitigates the observed short-output / early-stopping
  behaviour. All three arms pass T1 (length), T2 (chrF) and T3 (BLEU-4) there, and T5 (loops) overall.
- **Why every arm fails.** **No arm passes T4.** On the 15 controls (long clip, short reference), every arm
  over-generates: length ratio 1.46–1.58 against the ≤ 1.3 limit, and WER worsens by 32–42 points. All arms therefore
  fail the pre-registered criteria: S2 and S3 (primary) and S1 (exploratory).
- **What is unresolved.** Chunk selection at inference time, i.e. estimating how much linguistic content an input
  holds. Each chunk yields about one sentence of output whatever it contains, and the number of chunks follows frame
  count.
- **What this does not show.** It neither proves nor disproves that the 50-token training-target truncation causes the
  early stopping.
- **No re-tuning on these clips.** No new chunk-selection rule is tuned on these 36 clips. Any such rule needs data
  that was not used here.

Setup: Tesla T4, fp16, the P0-12 checkpoint and runtime inputs, Uni-Sign `eed438bc` plus the decode-length patch at
`max_new_tokens=100`, no training. The analysis was frozen before any GPU run (`FREEZE.sha256`, frozen at
2026-10-15T00:07:52Z; the runner re-verified it on the VM). It was run unchanged: `python3 -I scripts/analyze_pilot.py`.

## Deviations from the approved design (both decided before any GPU run, both documented in the frozen plan)

1. **U36 decodes all 128 clips, not 36.** The loader randomly subsamples clips over 256 frames, with 8 workers and
   batch 8. A 36-entry run would consume that RNG differently and could not reproduce R100 byte for byte. U36 therefore
   decodes all 128 clips unchanged, from byte copies of the runtime inputs, and the gate is evaluated on the 36 pilot
   clips. Result: 36/36 identical, and 128/128 overall.
2. **The frame-slice check is done on raw frames, not model-input tensors.** Uni-Sign normalises each loaded sequence
   with one body bounding box (`datasets.crop_scale`), so chunk tensors cannot equal a slice of the full clip's tensors.
   The check verifies:
   - that each chunk PKL is exactly the runtime frames `[start, end)`;
   - that, for S2 and S3, the loader output equals `load_part_kp` on those frames, i.e. nothing beyond the
     per-sequence normalisation is applied.

## 1. Gates (all passed)

| Gate | Result |
|---|---|
| Freeze checksums (laptop, then VM before any step) | OK |
| Loader / frame-slice validation (`results/out/loader_check.json`) | **pass**: every chunk PKL = runtime frames `[start, end)`; S2 / S3 have 0 chunks > 256 frames and loading them never calls `random.sample`; S1 subsamples exactly its 32 planned chunks > 256 frames; S2 / S3 loader output = `load_part_kp(frames)` exactly; U36 inputs are byte copies |
| SMOKE (4 entries) | OK |
| **U36 gate** (`U36_GATE.json`) | **pass: 36/36 pilot predictions byte-identical to R100** (also 128/128 overall); U36 metrics = R100 metrics on every subset |
| Run folders: entry counts, `SHA256SUMS` | 23/23 checks passed (`metrics/pilot_summary.json → verification`) |

**Disclosed confound (found in preflight):** Uni-Sign normalises each loaded sequence with a single body bounding
box (`datasets.crop_scale`). A chunk therefore gets its own box. The chunk/full-clip body-scale ratio has a median of
0.96–0.98, and 8 of S2's 91 chunks (9 of S3's) are below 0.8. This is part of "translate each chunk as its own clip"
and cannot be separated from it here.

## 2. Results: arm vs U36 (= R100), paired bootstrap 95 % CI (2000 resamples, seed 0)

### 21 long-reference target clips (reference ≥ 35 words)

| Arm | role | chrF | ΔchrF | BLEU-4 | ΔBLEU-4 | WER | ΔWER | length ratio | BLEURT (Δ) | loops | trunc. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U36 | baseline | 24.16 | — | 5.57 | — | 86.3 | — | 0.638 | 0.342 | 6 | 71 % |
| **S2** | primary | 34.61 | **+10.44 [+7.71, +13.03]** | 7.38 | +1.81 [+0.04, +3.62] | 103.3 | +17.0 [+9.2, +24.6] | 1.163 | 0.410 (+0.068 [+0.041, +0.093]) | 5 | 19 % |
| **S3** | primary | 33.54 | +9.38 [+6.15, +12.23] | 7.27 | +1.70 [−0.44, +3.87] | 103.7 | +17.4 [+9.9, +24.4] | 1.150 | 0.398 (+0.056 [+0.016, +0.091]) | 5 | 19 % |
| S1 | exploratory | 33.55 | +9.39 [+6.15, +12.31] | 9.81 | +4.24 [+2.23, +6.08] | 91.8 | +5.5 [+1.0, +11.2] | 0.993 | 0.404 (+0.062 [+0.033, +0.089]) | 2 | 19 % |

Per-clip sentence chrF improves on 19/21 clips (S2) and 18/21 (S3).

### 15 control clips (> 256 frames, reference < 35 words)

| Arm | chrF | ΔchrF | BLEU-4 | ΔBLEU-4 | WER | ΔWER | length ratio | BLEURT (Δ) | loops |
|---|---|---|---|---|---|---|---|---|---|
| U36 | 31.66 | — | 8.55 | — | 90.3 | — | 0.998 | 0.428 | 4 |
| **S2** | 36.85 | +5.19 [+0.42, +10.63] | 9.34 | +0.79 [−2.92, +5.38] | 132.6 | **+42.3 [+21.9, +68.6]** | **1.577** | 0.454 (+0.026 [−0.001, +0.054]) | 4 |
| **S3** | 34.54 | +2.88 [−1.69, +7.80] | 8.32 | −0.23 [−3.52, +3.39] | 129.7 | **+39.4 [+21.7, +59.1]** | **1.521** | 0.447 (+0.019 [−0.007, +0.046]) | 5 |
| S1 | 35.43 | +3.78 [−1.05, +8.93] | 9.43 | +0.87 [−2.64, +5.10] | 122.6 | +32.4 [+10.4, +60.1] | **1.460** | 0.450 (+0.022 [−0.004, +0.054]) | 4 |

Per-clip sentence chrF: 8 better and 7 worse, for both S2 and S3.

### All 36 clips

| Arm | ΔchrF | ΔBLEU-4 | ΔWER | length ratio | ΔBLEURT | loops (U36: 10) |
|---|---|---|---|---|---|---|
| S2 | +8.89 [+6.22, +11.13] | +1.56 [−0.34, +3.65] | +24.0 [+15.7, +33.1] | 1.276 | +0.050 [+0.030, +0.070] | 9 |
| S3 | +7.46 [+4.52, +10.00] | +1.10 [−0.79, +2.93] | +23.4 [+16.2, +31.5] | 1.252 | +0.041 [+0.015, +0.064] | 10 |
| S1 | +7.74 [+5.05, +10.39] | +3.13 [+1.17, +5.12] | +12.9 [+5.4, +22.5] | 1.121 | +0.045 [+0.024, +0.067] | 6 |

### Pre-registered criteria

| | T1 target len ≥ 0.85 | T2 target ΔchrF ≥ 2, CI > 0 | T3 target ΔBLEU-4 ≥ 0 | T4 control ΔchrF ≥ −2 **and** len ≤ 1.3 | T5 loops ≤ U36 + 2 | **pass** |
|---|---|---|---|---|---|---|
| S2 (primary) | ✓ 1.163 | ✓ | ✓ | ✗ (ΔchrF ✓, length 1.577 ✗) | ✓ 9 ≤ 12 | **no** |
| S3 (primary) | ✓ 1.150 | ✓ | ✓ | ✗ (ΔchrF ✓, length 1.521 ✗) | ✓ 10 ≤ 12 | **no** |
| S1 (exploratory) | ✓ 0.993 | ✓ | ✓ | ✗ (ΔchrF ✓, length 1.460 ✗) | ✓ 6 ≤ 12 | **no** |

## 3. Observed vs hypothesized / unresolved

### Observed (this run, these 36 clips)

- **Long-reference outputs become substantially longer.**
  - Length ratio on the targets: 0.64 → 1.16 (S2) and 1.15 (S3).
  - Outputs without final punctuation: 71 % → 19 %.
  - Every chunk ends by EOS, with no cap hits. Chunk outputs are sentence-sized: median 30–31 generated tokens
    (S2 / S3), and 9–11 chunks end at 48–52 tokens.
- **Target chrF and BLEURT improve.**
  - S2: chrF +10.44 [+7.71, +13.03], BLEURT +0.068 [+0.041, +0.093]. Sentence chrF improves on 19 of the 21 clips.
  - S3: chrF +9.38, BLEURT +0.056, both with CIs above 0.
  - BLEU-4 improves less: S2's CI is just above 0, S3's includes 0.
  - Target WER also **worsens** by about 17 points, from added words.
- **Control length ratio and WER worsen.**
  - Length ratio 1.00 → 1.58 (S2) and 1.52 (S3).
  - WER +42.3 [+21.9, +68.6] (S2) and +39.4 [+21.7, +59.1] (S3).
  - BLEU-4 change is about 0, with wide CIs. BLEURT change is about 0: its CIs include 0.
  - Sentence chrF: 8 clips better and 7 worse.
- **S3 pause snapping does not outperform S2.** Its chrF, BLEU-4 and BLEURT are lower than S2's on every subset.
- **chrF has a recall bias.** sacrebleu chrF uses β = 2 and weights recall twice as much as precision, so extra text
  raises it. The control chrF gains (+5.2 S2, +2.9 S3), which come with large WER losses, are best read as that recall
  effect, not as better translation. BLEURT and BLEU-4 are less length-favouring and show smaller gains: real on the
  targets, about 0 on the controls.
- **Per-chunk normalisation (confound).** Each chunk is normalised with its own body bounding box. The chunk / full-clip
  body-scale ratio has a median of 0.96–0.98, and 8 of S2's 91 chunks (9 of S3's) are below 0.8. This is inherent to
  "translate each chunk as its own clip" and cannot be separated from chunking here.

### Hypothesized / unresolved

- **The 50-token training target.** Whether the learned early stopping comes from it. The per-chunk clustering at
  48–52 tokens is *consistent with* a learned length prior, but training was not varied, so this is untested.
- **Content-aware chunk selection.** Whether choosing the number of chunks from the input's linguistic content can fix
  the control failure. Frame count cannot tell the two groups apart: both are > 256 frames. Nothing here tests a
  content-aware rule, and none may be tuned on these 36 clips.
- **Generalisation.** Whether the results hold beyond these 36 selected clips:
  - n = 21 / 15, one checkpoint, no extra seeds;
  - S2 and S3 are deterministic, but the U36 baseline subsamples randomly and was run once;
  - the clips are not a random sample of How2Sign.

**S1 (exploratory)** has the best-calibrated length on the target clips (0.99) and the largest BLEU-4 gain (+4.2).
It still fails T4 (1.46). It mixes chunking with random subsampling of 32 chunks, so it is not a clean intervention
and is not a basis for a claim.

## 4. Implications (no further experiment run)

- **What failed.** The failure is "one sentence-length output per chunk". The number of chunks is set by frame count,
  and frame count does not tell a 69-word reference apart from a 20-word one: both groups are > 256 frames.
- **What a deployable variant needs.** A deployable variant would have to choose K from something available at
  inference time, not from the reference.
- **Overfitting risk.** Any K rule tuned on these 36 clips would be fitted to them. Per the decision of 2026-10-15,
  none is tuned here; a content-aware rule needs held-out data.
- **Secondary, no decision weight.** Full-128 metrics with the 92 short clips left at R100: BLEU-4 9.13 → 9.39
  (S2) / 9.13 (S3) / 10.34 (S1); chrF 28.99 → 33.57 / 32.81 / 32.94; WER 91.0 → 103.4 / 103.2 / 97.7.

## 5. Files

| Path | Content |
|---|---|
| `PILOT_PLAN.md`, `FREEZE.sha256`, `FREEZE_TIME.txt` | plan and the pre-run freeze |
| `chunk_plan.csv`, `pilot_clips.csv` | frozen chunk boundaries and clip groups |
| `scripts/` | `make_chunks.py`, `check_loader_chunks.py`, `pilot_join.py`, `u36_gate.py`, `bleurt_score.py`, `analyze_pilot.py` |
| `runner/run_chunk_pilot.sh` | VM runner (gated sequence) |
| `results/out/` | VM outputs copied back verbatim: `SMOKE/ U36/ S1/ S2/ S3/` (predictions, decode diagnostics, `run.log`, `SHA256SUMS`), `U36_GATE.json`, `loader_check.json`, `bleurt.jsonl`, `PILOT_INPUTS.sha256`, `PLAN.sha256`, `environment.json`, `pilot_run.log` |
| `metrics/` | `pilot_summary.json` (verification, metrics, contrasts, decision, chunk diagnostics), `pilot_comparison.csv`, `per_clip.csv`, `per_chunk.csv` |

The `run.log` BLEU / ROUGE / BLEURT lines for S1 / S2 / S3 compare chunks against whole references and are not used.
