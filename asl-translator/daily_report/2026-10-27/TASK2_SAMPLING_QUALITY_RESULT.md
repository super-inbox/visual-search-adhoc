# Task 2 Step 3 — same-domain sampling translation-quality evaluation (2026-10-27)

**Scope:** a Uni-Sign 256-frame sampling diagnostic. **It is not a production-model result.** The production Gemini
path does not use this sampling scheme.

**Bottom line:** none of the three arms consistently changes translation quality.
- The direction flips between domains: slightly up in A, slightly down in B.
- No paired sign test comes near significance (p ≥ 0.23).
- One case, R10, drives most of the A gain.
- Automatic metrics only. Human semantic labels are pending for every case.

Inputs:
- provenance: [p0-input-provenance](p0-input-provenance/README.md) at commit `59b13d48`, not modified;
- sampler: the boss's frozen `sampling.py` / `run_sampling.probe` in
  [`experiments/p0-2026-10-27`](../../experiments/p0-2026-10-27/), imported unchanged;
- protocol: [PROTOCOL.md](../../experiments/p0-2026-10-27/PROTOCOL.md) §A.

## What was run

| Item | Value |
|---|---|
| Model | Uni-Sign `eed438bc`, checkpoint sha256 `1bfd5f33…fb00d`, mT5 snapshot `2eb15465…` |
| Decode | `generate(num_beams=4, max_new_tokens=100, do_sample=False)`, `U.set_seed(42)`, batch 1, 4 threads: the P0-A "T" path, identical to the Task 1 control |
| Inputs | P0-12 `prepared_inputs/{A_official,B_ours_5p39}` pose PKLs. Sha256 equals P0-A for all 90 rows |
| References | 10.13 `inputs_128.jsonl` (sha256 `1c7336c4…`), used for scoring only |
| Metrics | P0-A frozen definitions, copied from `score_repetition.py`: corpus BLEU-4 / chrF (sacrebleu defaults), WER (lowercase whitespace, ×100), mean output/reference word ratio; sentence chrF / WER |
| Device | CPU only. CUDA hidden and MPS disabled; each `generate` call asserts every parameter and input is on CPU. 283 calls, all `cpu`, one kwargs set, 808 s of generation |
| Holdout | P0-16 guard on all 45 IDs. No H18/H19 |

**Arms.** Budget 256. Clips with ≤ 256 pose frames keep every frame, so all arms are identical there.
- `random`: Uni-Sign's own draw, `sorted(random.Random(sha256(clip_id)[:8]).sample(range(n), 256))`.
- `uniform`: `sampling.uniform(n, 256)`.
- `coverage_motion`: `sampling.coverage_motion(energy, 256)`, with energy from `run_sampling.probe` on the video the
  pose was extracted from:
  - B: `how2sign_v2/videos/<clip>.mp4`;
  - A: the official crop clip `crop_test/<clip>.mp4`.
- `coverage_motion_boss` (B long clips only, sensitivity check): the boss's `sampling_45.json` indices. Those were
  computed on compressed display re-encodes of the same B clips.

**How the arm indices reach the model.** Uni-Sign's `load_pose` draws `sorted(random.sample(range(n), 256))`. For
the non-random arms, that single call is replaced by one that returns the arm's indices. The random arm always runs
the real upstream draw.

**Scripts and fixed definitions.**
- `decode_sampling.py` holds the preflight and the decode.
- `score_sampling.py` holds the scoring. Its bins and definitions were written before the full decode ran:
  - improve / regress candidate: Δ sentence chrF ≥ +5 / ≤ −5 (same bin as Task 1);
  - geometry improves: max gap ≤ random − 2 frames;
  - similar geometry: |Δ max gap| ≤ 1 frame and overlap ≥ 90 % of 256.

## Preflight: PASS

| Check | Result |
|---|---|
| Assets: checkpoint sha256, Uni-Sign commit, mT5 snapshot | pass |
| Rows R01–R45 × {A, B}; holdout guard; pose sha256 = P0-A | 90/90 |
| Video frame count = pose frame count (subsampled rows) | 27/27 (A 14, B 13) |
| Random-arm indices = P0-A `frame_idx_sha256` | 90/90 |
| Random-arm model-input `kps_sha256` = P0-A, via the real upstream draw **and** via injection | 90/90 |
| Boss geometry, B long clips: `random` / `uniform` indices identical | 13/13 / 13/13 |
| Boss geometry, B long clips: `coverage_motion` indices | 0/13 identical, overlap 176–250 of 256; max gap in seconds identical in 13/13 |
| CPU only | pass |

The `coverage_motion` difference is expected. Its energy comes from pixels, and the boss read a compressed
display re-encode where this run reads the actual B input clip. Both versions were decoded; see the B tables.

**Random-control reproduction:** for each domain, the random-arm output equals the saved P0-A T in text and token
ids on **45/45** rows. Non-subsampled rows give identical outputs across all arms (A 27/27, B 31/31).

## Scopes

- **Primary (source-time-sensitive):** provenance VERIFIED rows only, domains kept separate.
  - A: 41 rows (excludes R26, R28, R35, R42).
  - B: 42 rows (excludes R10, R14 MISMATCH and R32 UNRESOLVED).
- **Long:** primary rows with more than 256 frames, the only rows where the arms differ.
  - A: 14 (R03 R04 R10 R11 R12 R14 R19 R20 R21 R23 R36 R38 R39 R44).
  - B: 11 (R03 R11 R12 R19 R20 R21 R23 R36 R38 R39 R44).
- **Control:** primary rows with ≤ 256 frames. A 27, B 31.
- **All 45:** model-input-relative only.
  - R10/R14 B are labelled **timing-label MISMATCH (measured interval, not original timing)**.
  - UNRESOLVED rows are labelled.

## A_official

| Scope | Arm | n | BLEU-4 | chrF | WER | len ratio |
|---|---|---|---|---|---|---|
| primary | random | 41 | 5.21 | 23.73 | 95.80 | 1.006 |
| primary | uniform | 41 | 5.39 | 24.61 | 95.49 | 1.021 |
| primary | coverage_motion | 41 | 6.05 | 24.70 | 94.57 | 1.012 |
| long | random | 14 | 2.09 | 20.71 | 92.18 | 0.822 |
| long | uniform | 14 | 2.28 | 22.21 | 91.68 | 0.866 |
| long | coverage_motion | 14 | 3.91 | 22.36 | 90.18 | 0.839 |
| control | all three (identical) | 27 | 8.34 | 28.15 | 101.60 | 1.101 |

The all-45 random corpus (chrF 23.7634 / BLEU 5.7246 / WER 95.4369) equals the saved P0-A T corpus to the last
digit.

## B_ours_5p39

| Scope | Arm | n | BLEU-4 | chrF | WER | len ratio |
|---|---|---|---|---|---|---|
| primary | random | 42 | 1.78 | 18.26 | 100.31 | 1.045 |
| primary | uniform | 42 | 1.65 | 17.65 | 101.46 | 1.046 |
| primary | coverage_motion | 42 | 1.76 | 17.73 | 100.63 | 1.039 |
| long | random | 11 | 0.97 | 18.57 | 92.78 | 0.709 |
| long | uniform | 11 | 0.55 | 17.39 | 94.87 | 0.713 |
| long | coverage_motion | 11 | 0.93 | 17.55 | 93.35 | 0.687 |
| long | coverage_motion_boss (sensitivity) | 11 | 0.90 | 16.88 | 94.49 | 0.688 |
| control | all three (identical) | 31 | 2.79 | 17.94 | 109.47 | 1.163 |

**All 45 B (model-input-relative, includes R10/R14 MISMATCH):** chrF random 18.22, uniform 18.96, coverage_motion
19.12. The sign flips against the primary scope. That is R10 alone: Δ chrF +38.9 uniform, +41.8 coverage_motion.

## Long clips: paired comparison vs random (primary scope)

| Domain | Arm | n | chrF > / < random | WER better / worse | mean / median Δ chrF | mean / median Δ WER | sign test p | ≥ +5 / ≤ −5 |
|---|---|---|---|---|---|---|---|---|
| A | uniform | 14 | 9 / 5 | 8 / 5 | +1.57 / +1.14 | +0.69 / −2.22 | 0.42 | R03, R10 / R04 |
| A | coverage_motion | 14 | 7 / 7 | 7 / 5 | +1.41 / +0.67 | −2.19 / −2.17 | 1.00 | R03, R10 / R04, R20 |
| B | uniform | 11 | 3 / 8 | 2 / 7 | −1.71 / −1.89 | +3.61 / +1.89 | 0.23 | — / R39 |
| B | coverage_motion | 11 | 5 / 6 | 3 / 6 | −1.21 / −0.93 | +1.03 / +1.30 | 1.00 | — / R19 |
| B | coverage_motion_boss | 11 | 3 / 8 | 4 / 7 | −1.89 / −1.82 | +2.37 / +2.27 | 0.23 | — / R19 |

- Every long clip changed its output text in every arm.
- Without R10, the A mean Δ chrF drops to +0.92 (uniform) and +0.16 (coverage_motion, median −0.03, 6 up / 7 down).
- In B, energy from the real clip vs. the display re-encode moves coverage_motion's mean by about 0.7 chrF (−1.21 vs
  −1.89). That is about the same size as the arm effects themselves.

## Strongest apparent improvements (Δ sentence chrF vs random, long, primary)

| Domain | Case | Arm | Δ chrF | Δ WER | overlap / 256 | Δ max gap (fr) |
|---|---|---|---|---|---|---|
| A | R10 | coverage_motion | +17.68 | −21.9 | 100 | −7 |
| A | R10 | uniform | +10.04 | −9.4 | 113 | −9 |
| A | R03 | uniform | +6.27 | −7.3 | 118 | −7 |
| A | R03 | coverage_motion | +5.79 | +4.9 | 105 | −5 |
| B | R12 | coverage_motion_boss | +3.08 | +1.9 | 107 | −5 |
| B | R12 | coverage_motion | +2.18 | +1.9 | 113 | −5 |

- R10 is the R10_PROVENANCE case. The random output is already close to the reference ("So the G, the L, the G, the D
  with the low D…"). Coverage_motion's output is closer still ("So the G, the low G and the D with the lower D,
  unlike some of the double portions…").
- In the model-input-relative B scope, R10 B goes from a loop ("This is a sling which is a sling with a low D…", chrF
  12.6) to chrF 51.5 (uniform) and 54.4 (coverage_motion). That row is timing-label MISMATCH: its interval is the
  measured re-aligned slice, not the original timing.
- No B primary case reaches +5.

## Strongest regressions

| Domain | Case | Arm | Δ chrF | Δ WER | overlap / 256 | Δ max gap (fr) |
|---|---|---|---|---|---|---|
| A | R04 | coverage_motion | −7.42 | +53.8 | 235 | −1 |
| A | R04 | uniform | −6.96 | +53.8 | 236 | −1 |
| A | R20 | coverage_motion | −6.78 | +5.5 | 169 | −3 |
| B | R19 | coverage_motion | −7.27 | 0.0 | 171 | −3 |
| B | R19 | coverage_motion_boss | −6.81 | +2.3 | 178 | −3 |
| B | R39 | uniform | −6.39 | +5.3 | 224 | −2 |

- R04 A has 278 frames, so the arms share 235–236 of 256 indices. Even so, the output switches from "Hi, I'm Bobby
  Silver…" to "Hi, my name is Brandon Daniels, and I'm a biography expert…". Swapping about 20 frames is enough to
  change the hallucinated name. This shows how sensitive the decoder is to small input changes.
- R20 A coverage_motion falls into a loop ("if you don't want to, if you don't want to…").

## Geometry vs translation (long, primary)

**Geometry improves but translation does not** (max gap ≤ random − 2 frames, Δ chrF < +5):
- A: 22 of 26 geometry-improving arm-rows;
- B: 28 of 28 (including the sensitivity arm).
- Uniform shortens the longest gap in every long clip (mean −7.1 frames A, −5.7 B). The translation change does not
  follow it.

**Translation improves despite similar geometry** (|Δ max gap| ≤ 1, overlap ≥ 90 %, Δ chrF ≥ +5): **none**. Only 2 A
arm-rows (R04) have similar geometry, and both regress.

## Is there enough signal to justify further sampling work?

**No, not on this evidence.**
- The arms change every long-clip output, but neither the direction nor the size is consistent:
  - A long is mildly positive and driven mostly by R10;
  - B long is mildly negative;
  - none of the five paired comparisons reaches p < 0.2;
  - the B energy-source sensitivity is as large as the arm effect.
- R04 shows outputs flip on a ~20-frame swap. Without an estimate of how much outputs vary across random seeds, the
  differences above cannot be separated from that seed-to-seed variation. Measuring it would be the minimum next step
  before any sampler work. It was not run here.
- Only 14 (A) and 11 (B) clips are long enough to be subsampled at all.
- If anything is pursued, the candidates are R10 (both domains) and R03 (A), for **human** review of whether the
  outputs are semantically better. Automatic metrics alone do not establish that.

## Downloads

To compute coverage_motion energy for the 14 long A clips, the official crop clips were range-fetched with the P0-12
`fetch_entries.py` (`rgb` mode, CRC32-checked). The source is HF `ZechengLi19/Uni-Sign` `how2sign_rgb_format.zip.*`,
the same release as Step 2.
- 3 clips were already in scratch from Step 2 (R21, R36, R39). 11 were fetched now.
- The 14 clips total 22,133,288 bytes. Per-clip sha256 is in `sampling_quality_decode.json` (`energy_video_sha256`).
- Scratch only; not committed.

## Files

`asl-translator/experiments/p0-2026-10-27/`:
- `decode_sampling.py`: preflight + CPU decode. Imports `sampling.py` and `run_sampling.probe` unchanged.
- `score_sampling.py`: scoring with the frozen definitions.
- `results/sampling_quality_decode.json`: preflight record, per row × arm indices, index and kps hashes, geometry,
  output text and token ids.
- `results/sampling_quality_calls.json`: device, kwargs and seconds for each `generate` call.
- `results/sampling_quality_scores.json`: summary (all scopes) plus per-case rows.
- `results/sampling_quality_cases.csv`: 283 case × arm rows (human_status pending).

Not modified: `sampling_45.json`, `sampling_summary.json`, the provenance folder, Task 1 outputs, `sampling.py`,
`run_sampling.py`, `PROTOCOL.md`.

## Reproduce

```bash
# repo root; crop clips fetched to <scratch>/a_long_crops with P0-12 fetch_entries.py (rgb)
/opt/anaconda3/envs/unisign-cpu-arm64/bin/python -I asl-translator/experiments/p0-2026-10-27/decode_sampling.py \
  --unisign ~/Desktop/curify/p014-work/Uni-Sign \
  --checkpoint ~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth \
  --mt5 ~/.cache/huggingface/hub/models--google--mt5-base/snapshots/2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f \
  --crop-dir <scratch>/a_long_crops \
  --out asl-translator/experiments/p0-2026-10-27/results/sampling_quality_decode.json   # add --preflight-only first
/opt/anaconda3/bin/python3 -I asl-translator/experiments/p0-2026-10-27/score_sampling.py
```
