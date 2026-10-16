# P0-14 local gates (Mac only): Stage 0, smoke, pilot

**Date:** 2026-10-15 · **Machine:** Apple M3 Pro, CPU, fp32 · **Result: ALL GATES PASS.** No T4, no full archive.
Nothing committed. Features are stored outside the repo in `~/Desktop/curify/p014-work/` (durable, not a session
scratchpad). This folder holds only the small evidence files.

## Stage 0: pinned environment (no upgrades)

| Item | Value |
|---|---|
| Uni-Sign | fresh clone of github.com/ZechengLi19/Uni-Sign at **`eed438bcb49e30405cd6ccdfcccca330c134e830`** (same as P0-12/P0-13), unmodified (only `__pycache__` untracked) |
| Checkpoint | `~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth`, sha256 **`1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d`** (matches P0-13) |
| mT5 | HF cache `google/mt5-base` snapshot **`2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f`**; `pytorch_model.bin` sha256 `180573b534144580f04af026da62bf71bc976ee1b7eb311b8945e2fefde8d614`, `spiece.model` `ef78f86560d809067d12bac6c09f19a462cb3af3f54d2b8acbba26e1433125d6`. The mT5 weights are overwritten by the checkpoint's strict load; only the tokenizer and config matter |
| Env | conda `unisign-cpu-arm64`: Python 3.10.13, torch 2.1.1, transformers 4.40.0, numpy 2.2.6, einops 0.6.1 (identical to P0-13) |
| Code fix | `Tensor.numpy()` is broken in this env (torch 2.1 + numpy 2.x; first smoke attempt died with `RecursionError`). Tensors are converted via `.tolist()`, the same workaround P0-13 used |

## Stage 1: 128-clip smoke (committed P0-12 `A_official` test PKLs)

| Check | Result |
|---|---|
| Shapes per clip | raw `[T,207]`, Fsign `[T,1024]`, mT5 `[T,768]`; pooled mean/std/mad `D`, seg4 `4×D` — **PASS** |
| NaN / Inf | 0 — **PASS** |
| One record per clip, no duplicates or extras | 128 / 128 — **PASS** |
| Clip order = manifest order | **PASS** |
| Provenance (split, role, video, pose sha256, dims) | **PASS** |
| T = min(raw frames, 256) | **PASS** (T 6–256; 36 clips subsampled) |
| Primary probe vector [mean ; std] | 414 / 2048 / 1536 — **PASS** |
| Concept labels re-derived from the English reference = manifest | **PASS** (120 positive labels) |
| Determinism (16 clips re-extracted) | max \|diff\| **0.0** on every array — **PASS** |
| Faithfulness: 8 own-decoder decodes vs committed P0-12 predictions | mean chrF **71.6**, 2/8 identical, all on-topic. Differences come from the >256-frame random sampling (4/8 clips) and fp32 CPU vs fp16 T4 under beam search. Same kind of gate as P0-13 (chrF 63.3 vs the authors' predictions) — **PASS** |
| Time | 66 s for 128 clips including 8 beam decodes |

## Stage 2: real pilot (430 clips, range-fetched from the official archive)

- **Selection:** `scripts/fetch_pilot_poses.py`, seed 20261015+14, whole videos from the frozen manifest. 322
  probe_train clips (21 videos, all 5 CV folds present) and 108 test_clean clips (5 videos).
- **Fetch:** 430 PKLs, 186 MB, CRC-32 verified per entry, 81 s. No full download.
- **Validation:** every check above passes again (`VALIDATION_pilot.json`). In addition:
  - **train/test video overlap 0**;
  - split / video / role agree with the CSVs;
  - every pose came from its own split's archive directory;
  - **316 positive concept labels** match labels re-derived from the English references;
  - dimensions are consistent across all 430 clips.
- **Zip-streaming path** (the one the full run uses), tested on a 20-clip zip with the real archive layout: output
  identical to the directory path (max \|diff\| 0.0), all checks pass (`VALIDATION_ziptest.json`).
- **LR probe pipeline test:** runs end to end on real features for all 5 arms, Design A and Design B.
  **Not interpreted.** n_test = 108 from 5 videos, and Design B with 5 videos is degenerate.

## Measured speed (Mac CPU, fp32)

| Step | Speed |
|---|---|
| Frozen forward pass, all three representations, no decoding | **0.25 s/clip** (430 clips in 107 s) |
| Own-decoder beam-4 decode (decoder baseline) | **≈ 5.5 s/clip** (20 clips: 115 s vs 4 s without decoding) |
| Range-fetch from HF | ~5 clips/s with 6 threads |

## Projections for the full run

| | Value |
|---|---|
| Clips | 31,086 probe_train + 2,209 test_clean = **33,295** |
| Full extraction, Mac CPU | 33,295 × 0.25 s ≈ **2.3 h** (+ 8.46 GB download) |
| Decoder baseline, Mac CPU | 2,209 × 5.5 s ≈ **3.4 h** |
| Pooled features (primary artifact) | 53.5 KB/clip measured → **≈ 1.8 GB** |
| Per-frame sequences, test_clean only (fp16) | 0.50 MB/clip measured → **≈ 1.1 GB** |
| Per-frame sequences for train too (not planned) | would be ≈ 15.5 GB more; not needed for mean+std probes |
| Archive | 8.47 GB parts; + 8.47 GB if concatenated (delete parts after `cat`) → peak ≈ 17 GB; Mac has 431 GB free |
