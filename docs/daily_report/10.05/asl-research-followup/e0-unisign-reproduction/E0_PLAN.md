# E0 — Uni-Sign official How2Sign reproduction: plan

Date: 2026-10-05. Scope: E0 only. No training, no product/frontend changes, no commit.

## Goal

Before any new training, find out whether Uni-Sign's published How2Sign result
(pose-only BLEU-4 **14.5**) can be reproduced, and which part of the gap to our
**5.39** (frozen 128-clip `how2sign_v2` benchmark) comes from:

1. benchmark difficulty (our clip selection),
2. our inference pipeline (pose extraction, numerics, batching), or
3. the release itself not reproducing the paper.

## Steps

| # | Step | Needs | Status |
|---|---|---|---|
| 1 | Pin the official repo (`ZechengLi19/Uni-Sign` @ `eed438bc`) and read the paper (arXiv 2501.15187) | network | Done |
| 2 | Extract the exact How2Sign eval protocol (checkpoint, poses, split, preprocessing, decoding, script, BLEU) | step 1 | Done (`E0_PROTOCOL_COMPARISON.md`) |
| 3 | Audit our environment and assets against that protocol | local disk | Done (`E0_ENVIRONMENT_AUDIT.md`) |
| 4a | **Scoring-path reproduction:** re-score the officially released How2Sign predictions (`out/eval_how2sign_pose_only/`) with the official BLEU code | step 1 only | Done → **14.50** |
| 4b | **Benchmark-difficulty isolation:** score the official released predictions on exactly our 128 clips | step 4a + our tracked predictions | Done → **9.59** |
| 5 | **Inference-path reproduction:** run official `fine_tuning.py --eval` on official poses, full test set | official pose files, CUDA GPU, deepspeed, BLEURT | **Blocked**, not run (see below) |
| 6 | Arms from the 10.05 analysis: (2) our 128 × official poses, (4) our 128 × higher-accuracy rtmlib | step 5 assets | Not run (depends on step 5 / would be approximations) |

## Why step 5 was not run (stop rule)

The brief says to stop and report rather than substitute approximations. The
official eval path cannot run unmodified on this machine:

- **No CUDA GPU** (Apple M3 Pro, `torch.cuda.is_available() == False`).
  `fine_tuning.py` hardcodes `model.cuda()` (L69), `.cuda()` on inputs (L254)
  and on the pad tensor (L276), and always wraps the model in a
  `deepspeed.initialize` engine (`utils.py:404-429`). Running it on CPU/MPS
  means editing the official eval script, which is an approximation.
- **Official How2Sign pose files are not on disk.** They are public
  (`how2sign_pose_format.zip.00–.03`, 8,465,474,575 bytes total on HF), so this
  part is a download, not an access blocker. I did not download them, because
  without a GPU they don't unblock the official path.
- **BLEURT is not installed** (`bleurt` package + `BLEURT-20` checkpoint).
  For `--dataset How2Sign --eval`, `fine_tuning.py:292-300` imports BLEURT
  *after* BLEU is printed but *before* the prediction files are written
  (L316-322), so a run without it crashes before saving outputs.
- **`config.py` bug:** `pose_dirs["How2Sign"] = "./dataset/WLASL/pose_format"`.
  Needs a local path edit, which the README explicitly sanctions ("modify the
  `config.py` file to specify the new paths"). This is not a blocker.

Rough cost if the hardware were available: about 2,349 clips × bf16 mT5-base
beam-4 generation is about 1 GPU-hour. On this CPU, our measured ~32 s/clip
(generation only ~20–45 s for long clips) puts it at roughly 15–30 hours, *and*
it would still need the patches above.

## Decision after 4a/4b

Scoring and test labels are confirmed. Benchmark difficulty explains about half
the gap (14.5 → 9.6). The other half (9.6 → 5.4) is inside our inference
pipeline. Next step: see `E0_RESULTS.md` §5.
