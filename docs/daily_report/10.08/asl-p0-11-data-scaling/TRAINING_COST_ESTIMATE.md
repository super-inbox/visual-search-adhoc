# P0-11: training cost estimate (made before the runs)

## Device

| Item | Value |
|---|---|
| Machine | Apple M3 Pro (12 cores), 18 GiB RAM, macOS 14.1 |
| CUDA | none |
| Device used | CPU, as in P0.2 (`use_cpu=True`). MPS exists but is not used, to keep numerics and the recipe identical to the P0.2 reference |
| Env | `gloss-free-asl-translation/.venv`: Python 3.12.4, torch 2.10.0, transformers 4.57.6, the same as P0.2 |

## Measured anchors

- **P0.2:** 10,320 steps plus 30 evaluations took 8,465 s training (8,508 s wall).
- **P0-11 smoke run** (344 steps + 1 evaluation, P0.2 IDs): 288 s.
  - Peak RSS **1.73 GB**.
  - CPU use about 1.6 cores (user+sys 477 s over 294 s wall).
  - Init hash equals P0.2's.

## Per-condition estimate (compute-matched: 10,320 steps, eval every 344)

| Condition | Clips | Steps | Data passes | Training + evals | Peak RAM | Disk (ckpts, limit 2) |
|---|---|---|---|---|---|---|
| p25 | 6,605 | 10,320 | 12.5 | about 2.4 h | about 1.8 GB | about 0.85 GB |
| p50 | 13,210 | 10,320 | 6.2 | about 2.4 h | about 1.8 GB | about 0.85 GB |
| p100 | 26,419 | 10,320 | 3.1 | about 2.4 h | about 1.8 GB | about 0.85 GB |

- Per-step cost does not depend on subset size; clip-length distributions match.
- Each run uses about 1.6 cores, so **all three run concurrently**. Expected wall time is about 2.5–3.5 h, allowing
  some contention.
- Early stopping can end runs sooner.
- **Diagnostics** (correct vs shuffled video, 5 seeds, best checkpoint): about 25 min each, so about 30–40 min
  concurrently.

## Data preparation

| Item | Size | Time |
|---|---|---|
| `frontal.rar` (re-download; the copy from 2026-09-22 was deleted) | 21.8 GB | about 10 min at the previous 40 MB/s, **about 3.5 h at today's about 1.6 MB/s** (link-limited: 16 parallel range requests give the same total) |
| Extraction (`unar`, all 31,047 files) | about 31 GB (3,117 files = 3.1 GB) | about 10–20 min |

All of this is in the session scratchpad, outside the repo.

## Feasibility

**All three conditions are feasible locally.** Total is about 3.5 h download + about 0.3 h extraction + about 3 h
training + about 0.6 h diagnostics, so **about 7.5 h**.

- A GPU is not needed for this protocol.
- The alternative fixed-epoch protocol (30 epochs at each size) would be about 31 h of CPU sequentially (p100 alone
  about 17 h). It is not run, by design (see `P0_11_PLAN.md`).
