# Task (b) manager summary — segment long ASL video before Uni-Sign?

**Classification: B — NO CLEAR BENEFIT YET.** (n = 1 long clip; do not generalise.)
Full detail: `RESULTS.md`. Local R&D only: no ACR / Azure / production changes, checkpoint not copied or committed, no generated videos committed, Uni-Sign preprocessing untouched.

## Short answer
Segmenting fixes a real *mechanical* problem (Uni-Sign randomly throws away frames on long clips), but on the one long clip I tested it did **not** show better translations. It costs about 2× the runtime.

## What I did
- **Audited the existing uncommitted POC first.** It is real and was executed (13 segments, real checkpoint), but on a *different* video (76.8 s, non-independent reference) with different parameters (6–7.5 s segments). It does not answer the frozen-clip question, so I left it untouched and ran a fresh experiment.
- **Clip:** How2Sign `FzmL8SL6Bow_1-8-rgb_front`, 25.75 s, 618 frames. Direct baseline reused from task (a) (not re-run).
- **Motion detector reused, not rewritten** (`probe_motion` / `segment_runs`, verified identical to production code). Deterministic segmentation using motion only: target 6 s, 4–8 s allowed, ~1 s overlap (0.5–1.5). Parameters fixed before inference, not tuned.
- Result: **5 segments** — 0–6.75, 5.75–10.75, 10.0–14.25, 13.25–19.5, 18.5–25.75 s. Each sent once to the real Uni-Sign service (checkpoint SHA verified; `/healthz` and `/readyz` both 200; 5/5 HTTP 200).

## Findings
| | Direct (whole video) | Segmented (5 clips) |
|---|---|---|
| Frames reaching model | **256 of 618** (362 dropped at random) | **708 of 708** (90 = overlap) |
| Segments hitting the 256 cap | 1 (the whole clip) | **0** (max 174 frames) |
| Same input twice | **different outputs** | identical (checked on segment 2) |
| WER / CER | 0.872 / 0.702 (repeat: 0.859 / 0.702) | 1.180 / 0.815 |
| BLEU / chrF | 2.48 / 20.5 (repeat: 1.86 / 22.0) | 3.17 / 35.3 |
| Output length (ref = 78 words) | 38 words | 110 words |
| Runtime, model calls | 101 s, 1 call | 249 s (≈221 s warm), 5 calls |

- **Good:** the 618→256 random frame drop is completely gone; per-segment output is deterministic.
- **Not shown:** better translation. Segmented text covers the whole timeline but is mostly generic/hallucinated (glass, wheel, rubber stamps, pot vs. a reference about a hole and the signer's hands). WER/CER got worse (over-long output), chrF/BLEU got higher — mixed, and the direct baseline itself varies run to run.
- **Overlap:** produced no duplicated text (0-word repeats at all 4 junctions), so the dedup merge changed nothing and "naive" = "dedup". We can't tell whether the overlap helped.
- **Motion-aware boundaries:** calmer than a fixed grid (mean motion rank 0.37 vs 0.52) and two land on the clip's only real rest pose, but one start boundary (18.5 s) is mid-sign. This signer barely pauses.
- **4–8 s / 1 s overlap is technically reasonable** (median clip in our benchmark is 5.2 s). But the 256 cap is in *frames*: 8 s is fine at 24 fps and borderline at 30 fps, so a production rule should be `min(8 s, 256/fps)`.

## Recommendation
Keep segmentation as an **experimental candidate** preprocessing step for clips over the 256-frame cap — not a production recommendation; don't claim quality gains and don't ship the merge step. The next useful experiment needs **segment-level gold**: build long test videos by concatenating consecutive How2Sign sentence clips (known per-sentence references and boundaries). I did not run a second long clip — with n = 2 the classification could not change, and the missing gold is the real blocker.

## Caveats
n = 1; single un-aligned 78-word reference and no segment-level references; overlap benefit could not be established; sentence-level BLEU is noisy; segments were re-encoded before pose extraction; amd64-emulated timing with an approximate cold-start correction.
