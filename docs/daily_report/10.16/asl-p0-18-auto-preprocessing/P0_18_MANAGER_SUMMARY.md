# P0-18 — Can automatic preprocessing close Uni-Sign's input gap? (development result)

**Date:** 2026-10-19 · **Status: FINAL — development completed, NOT SUPPORTED. P0-18 stopped here; H18 remains sealed
for a stronger candidate.** The confirmatory H18 run was not opened.

## Bottom line

- **Automatic signer cropping gives a small, clean gain; automatic timing does not work.** On the full How2Sign test set
  (2,347 clips), cropping to the signer raises BLEU-4 from 4.85 to 5.24 (**+0.39**, 95% CI +0.17 to +0.62) with no
  change in WER or output length.
- **The real gap is timing, and we cannot recover it from pose alone.** Using the correct (re-aligned) clip timing
  would be worth **+7.4 BLEU-4**. Our automatic timing detector only widened the window, which raised BLEU-4 a little
  but made translations longer and **worse on WER by ~9 points**, so we dropped it.
- **Development verdict for the final candidate (crop only): NOT SUPPORTED.** It is safe but below the bar we set
  before seeing the data (+0.5 BLEU-4 and ≥ 33% of the gap to the official preprocessing). The thresholds were not
  changed. **Decision (2026-10-19): P0-18 stops at the development result; H18 is not opened** and stays sealed for a
  stronger candidate.

## Results (How2Sign test, 2,347 clips; every arm decoded on the same T4 GPU)

| Arm | Timing | Crop | BLEU-4 | chrF | WER | Output length vs reference |
|---|---|---|---|---|---|---|
| Old pipeline | speech timestamps | full frame | 4.85 | 22.1 | 101.1 | 0.90 |
| **Final candidate: crop only** | speech timestamps | **automatic** | **5.24** | **22.6** | **100.9** | **0.90** |
| First candidate (dropped) | automatic, widened | automatic | 5.77 | 24.7 | 109.7 | 1.08 |
| Correct timing + automatic crop (oracle) | official signing timestamps | automatic | 13.15 | 33.0 | 87.2 | 0.95 |

- Crop only vs old: BLEU-4 +0.39 [+0.17, +0.62], chrF +0.48 [+0.24, +0.73], WER −0.1 [−1.3, +1.0].
- The automatic crop is about as good as the official one (+0.47 BLEU-4 for the official crop at correct timing, not
  significant).
- Share of the Old → oracle gap recovered: crop only ≈ 5% (27% on the 128-clip subset with official crops);
  first candidate ≈ 11% (42% on that subset).

## Pre-registered criteria (development)

| Criterion | Requirement | Crop only (final) | First candidate |
|---|---|---|---|
| P1 improvement | ≥ +0.5 BLEU-4, CI above 0 | **fail** (+0.39, CI above 0) | pass (+0.92) |
| P2 gap recovery | ≥ 33% of the gap to the official preprocessing | **fail** (27%) | pass on the subset (42%) |
| P3 reliability | ≤ 5% failures | pass (0.3%) | pass (0.6%) |
| P4 cost | ≤ 15 s preprocessing per clip | pass (7.1 s on one T4) | pass |
| P5 do no harm | WER increase ≤ +5 (upper CI), length 0.8–1.2× | **pass** (+1.0) | **fail** (+10.5) |
| **Verdict** | | **NOT SUPPORTED** | **NOT SUPPORTED** |

## Engineering status

- Pose extraction and decoding run in one frozen GPU environment (T4). It reproduces the CPU decoder exactly (128/128
  identical) and is deterministic run to run.
- Design, thresholds, verdict logic, environment and code are frozen (`FREEZE.json`). The H18 runner has been dry-run
  end to end on test data with the final candidate (see below). H18 and H19 remain sealed. Nothing is committed.

**H18 dry run (final candidate, test data, 3 videos / 30 clips, 31 min):** the runner used crop-only as the primary
arm; all three sanity gates passed (environment reproduction, decoding determinism, data integrity); verdict NOT
SUPPORTED. On these 3 videos crop-only happened to score below the old pipeline (−1.8 BLEU-4): a 30-clip pipeline test
is not evidence about the effect, but it is a reminder that the crop gain is small and varies by video. An earlier dry
run found and fixed a bug that would have stopped the H18 run.

## Decision and next direction

- **P0-18 is closed at development: NOT SUPPORTED** (final candidate: original timing + automatic signer crop).
  The automatic crop gives a clean but small gain; the automatic-timing candidate was not supported (WER harm).
- **H18 and H19 remain sealed.** H18 is kept for a stronger candidate; the frozen runner, environment and dry run can be
  reused.
- **Next:** pose-only timing is the main unresolved bottleneck (correct timing is worth +7.4 BLEU-4). A future candidate
  needs a stronger timing/alignment method, such as a learned sign/no-sign segmenter or transcript-to-sign alignment.
