# Chunked-decoding pilot: plan (approved 2026-10-14; analysis frozen before any GPU output)

**Research question.** Can deterministic chunking of long pose sequences overcome Uni-Sign's learned
early-stopping / short-output behaviour without materially degrading translation quality on long clips whose
references are already short?

A positive result does **not** show that the 50-token training-target truncation caused the failure. It only shows
that chunking can mitigate the observed long-input / long-reference failure mode.

**Frozen before any GPU run** (`FREEZE.sha256`, checked by the runner before it does anything):
- `scripts/analyze_pilot.py`: all definitions, gates and T1–T5.
- `scripts/pilot_join.py`: the join rule.
- `scripts/u36_gate.py`, `scripts/bleurt_score.py`, `scripts/check_loader_chunks.py`, `scripts/make_chunks.py`.
- The runner, `chunk_plan.csv`, `pilot_clips.csv` and this plan.

**Question.** The decode-length experiment showed that on long references Uni-Sign ends its output on its own (EOS)
after about 33 words / ~50 mT5 tokens. Does translating a long input in temporal chunks, and joining the chunk
translations, recover the missing content? No training; inference only.

What the pilot can show: whether chunking raises output length and reference-based quality on long-reference clips,
and whether it hurts long clips whose references are short.

What it cannot show: *why* the model stops early. Every ≥35-word reference is also a >256-frame clip (r = 0.86).
S1 versus S2 separates "shorter output per call" from "no random frame subsampling" only partially (see below).

## 1. Fixed setup (identical to P0-12 / decode-length R100)

| Item | Value |
|---|---|
| Checkpoint | `how2sign_pose_only_slt.pth`, sha256 `1bfd5f33…683fb00d` |
| Code | Uni-Sign `eed438bc` in the existing decode-length worktree (`fine_tuning.py` = decode-length patch, sha256 `f13e1689…`); `max_new_tokens` = 100 (upstream default, env var unset); diagnostics on |
| Inputs | fp16 runtime PKLs in `/tmp/p012_fp16`, verified against the pinned `RUNTIME_INPUTS_A_official.sha256` before every run |
| Runtime | Tesla T4, `--dtype fp16`, batch 8, `num_beams=4`, seed 42, `max_length` 256, 8 workers, deepspeed single GPU |
| Benchmark | frozen 128-clip How2Sign subset; references = manifest `reference_text` |

## 2. Clips (`pilot_clips.csv`)

All 36 A_official clips with more than 256 frames:

| Group | n | Frames | Role |
|---|---|---|---|
| `long_ref_ge35` | **21** | 280–978 | target: every reference of ≥ 35 words |
| `control_gt256_ref_lt35` | **15** | 260–624 | control: long clip, short reference (length ratio ≈ 1.0 today) |

The 92 clips of ≤ 256 frames are **not chunked and not run**. Their outputs are, by construction, the committed R100
outputs.

## 3. Arms (`chunk_plan.csv`: frozen integer frame boundaries, computed locally by `scripts/make_chunks.py plan`)

| Arm | Rule | Chunks | Chunk length | Chunks > 256 frames (loader subsamples them) |
|---|---|---|---|---|
| **U36** (control) | unchunked; the run decodes **all 128** clips from byte copies of the runtime inputs, and the 36 pilot clips are used | 128 (36 used) | 260–978 | 36 |
| **S1** halves | K = 2 equal contiguous halves | 72 | 130–489 | 32 |
| **S2** ≤256 windows | K = ⌈T / 256⌉ equal contiguous windows (K = 2: 20 clips, 3: 13, 4: 3) | 91 | 130–246 | **0** |
| **S3** ≤256 pause-snapped | S2's K, each internal boundary moved to the lowest two-hand wrist-speed frame within ±24 frames of the equal split | 91 | 109–256 | **0** |

Rules common to all arms:

- **Splits.** Equal splits give sizes that differ by at most one frame; the earlier chunks get the extra frame.
- **Overlap: none.** Chunks are contiguous and every frame is used exactly once. Overlapping windows would make the
  model translate the overlap twice. Joining would then need a fuzzy text de-duplication step, which is itself a
  heuristic and would interact with the repetition problem. So it is left out of the pilot.
- **S3 boundaries.**
  - Wrist speed is the sum of the left and right wrist displacements per frame, in units of the clip's median shoulder
    width, smoothed with a 5-frame moving average. The pose PKLs are the committed source; the boundaries are frozen
    as integers, so the VM's fp16 PKLs never recompute them.
  - Boundaries move only within ±24 frames of the equal split, and every chunk stays in [64, 256] frames. Ties go to
    the frame closest to the equal split, then the earlier one.
  - Over 55 internal boundaries the median |shift| is 12 frames, and 6 of them sit at the ±24 limit.
  - The point of S3 is to test whether cutting mid-sign hurts. It is a proxy: low wrist speed is not verified as a sign
    boundary.
- **Chunk input.** A chunk PKL is the source dict with `keypoints` and `scores` sliced to `[start, end)` and `w_h`
  unchanged.
- **Normalisation is per sequence (found in preflight, before any run).**
  - `datasets.crop_scale` (Uni-Sign `datasets.py:80`) computes **one body bounding box per loaded sequence**. The
    hand and face parts are scaled by it too.
  - So a chunk is normalised with its own box, exactly as any short clip would be. That is not the box of the full
    clip, and the same was already true of the >256-frame baseline, whose box comes from its 256 sampled frames.
  - Chunk tensors therefore cannot equal a slice of the full clip's tensors. Per-sequence re-normalisation is part of
    the intervention "translate each chunk as its own clip". It is not a pipeline error.
  - The ratio of chunk body scale to full-clip body scale is reported per chunk.
- **Join.** For each clip, the chunk predictions are stripped and joined in temporal order with a single space. No
  de-duplication, re-casing or punctuation edits. Sentence-internal capitals and periods are kept.
- **Determinism.**
  - S2 and S3 have no chunk over 256 frames, so the loader never subsamples them. They are seed-independent and are
    the **primary** arms.
  - S1 still subsamples 32 chunks randomly. It is **exploratory**: not a clean chunk-only intervention.
  - U36 subsamples like R100. It decodes all 128 clips because a 36-entry run would consume the loader's RNG stream
    differently (8 workers, batch 8) and could not reproduce R100.
- **S1 vs S2.** In S1, 16 of the clips still have both halves subsampled. Within those clips, S2 − S1 is "no
  subsampling, plus more chunks". This is suggestive at best, because K differs too.

Every chunk entry carries its full clip reference in its labels file (the loader needs a text). Its `run.log`
BLEU/ROUGE/BLEURT values are chunk-vs-whole-reference numbers and **are ignored**. All scoring is done on the joined
output.

## 4. Runner changes (`runner/run_chunk_pilot.sh`)

- **No code change.** Same worktree, same patched `fine_tuning.py` (sha256-checked), same flags, same checkpoint and
  runtime-PKL verification as the decode-length runs.
- **Per-arm `config.py` edits only.** These are the same three README-sanctioned `sed` lines as P0-12. Labels point to
  `$PILOT/<ARM>/labels.test_pilot` and poses to `$PILOT/<ARM>/{}-pose-rtmpose-192`. `config.py` is restored after each
  run.
- **Sequence, with hard stops:**
  1. `FREEZE.sha256` check.
  2. `make_chunks.py build`: arm inputs from the runtime PKLs and the frozen plan, plus `PILOT_INPUTS.sha256`,
     re-verified before every run.
  3. **Loader / frame-slice validation** (`check_loader_chunks.py`, CPU). It checks:
     - every chunk PKL equals the runtime frames `[start, end)`;
     - S2 and S3 have no chunk over 256 frames, and loading them never calls `random.sample`;
     - S1's 32 chunks over 256 frames are exactly the ones subsampled;
     - for S2 and S3, the loader output equals `load_part_kp(frames [start, end))`, so nothing is added beyond the
       per-sequence normalisation;
     - U36 inputs are byte copies of the runtime inputs.
  4. **SMOKE**: 3 S2 chunks plus 1 unchunked clip.
  5. **U36** and the **U36 gate** (`u36_gate.py`). All 36 pilot predictions must be byte-identical to the committed
     R100 predictions, or **STOP** before S1/S2/S3. The analysis re-checks this and also requires the U36 metrics on
     the 36 to equal R100's.
  6. **S1, S2, S3.**
  7. **BLEURT-20** on the joined outputs (`bleurt_score.py`, the eval's own BLEURT-20 checkpoint).
- **Diagnostics.** `UNISIGN_DECODE_DIAG=1` records EOS / cap hit / generated tokens **per chunk**.

## 5. Success thresholds (fixed now, before any GPU output)

Unchanged from the plan shown before approval. Every definition is implemented in the frozen `analyze_pilot.py`.

Primary contrast: **arm − U36** on the same clips, with paired clip-level bootstrap (2000 resamples, seed 0). Metrics
are corpus chrF, BLEU-4 (sacrebleu 13a), WER (P0-12 definition), the length ratio (predicted words / reference
words), the truncation rate, and the taxonomy repetition-loop rate.

| # | Criterion | Subset |
|---|---|---|
| T1 | corpus length ratio ≥ 0.85 (decode-length R100: 0.64) | long_ref_ge35 (21) |
| T2 | ΔchrF ≥ +2.0 **and** 95 % CI lower bound > 0 | long_ref_ge35 |
| T3 | ΔBLEU-4 ≥ 0 (point estimate) | long_ref_ge35 |
| T4 | ΔchrF ≥ −2.0 **and** corpus length ratio ≤ 1.3 | control_gt256_ref_lt35 (15) |
| T5 | repetition-loop clips (taxonomy rule) ≤ U36 count + 2 | all 36 |

- **Pass.** An arm **passes** only if T1–T5 all hold.
- **Noise check.** The U36 gate makes U36 = R100 exactly, so the subset-rerun noise check is zero by construction.
  Seed-to-seed noise is **not measured**, because there are no extra seeds. S2 and S3 involve no randomness; S1 and the
  baseline do.
- **Next step.** If at least one arm passes, propose the next stage: extra seeds, and the 2×2 with repetition control.
  If no arm passes, report a negative result.
- **Secondary, no decision weight:**
  - Full-128 metrics, splicing the arm's 36 joined outputs into the committed R100 for the 92 ≤256-frame clips.
  - Per-chunk EOS and length.
  - BLEURT-20 on the joined outputs, scored on the VM with the same BLEURT-20 checkpoint by the analysis script.
    That script is to be written before any results are copied back.

## 6. GPU runs

5 inference invocations, no training:

| Run | Entries decoded |
|---|---|
| SMOKE | 4 |
| U36 | 128 (36 used) |
| S1 | 72 |
| S2 | 91 |
| S3 | 91 |
| **Total** | **386** (≈ 3 × one 128-clip decode) |

Estimated time on the T4 is roughly 15–25 min. Most of it is per-run start-up (deepspeed, model load, BLEURT import).
The 128-clip R100 decode itself took 43 s. **This is an estimate, not measured.**

## 7. Not in this pilot

- Extra seeds.
- The 2×2 with repetition control.
- Overlapping windows.
- Chunking ≤256-frame clips.
- Any change to `max_new_tokens`, beams or training.
