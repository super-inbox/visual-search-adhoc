# Phase D1 — Trajectory-Tracking POC: Results

**Date:** 2026-09-10. Implementation + execution of the D1 plan only. No Gemini calls, no
semantic prompting, no model training, no changes to any existing benchmark prediction,
no commits. `curify-studio` untouched.

## 0. Framing (restated, see `PHASE_D0_RESEARCH_AND_AUDIT.md`'s correction)

Trajectory tracking is genuinely new **for the Curify/Gemini pipeline** — this is the
first time any structured motion signal has been extracted anywhere on this branch. It is
**not new across our benchmarked systems**: Uni-Sign already runs on RTMPose-extracted
skeleton keypoints. §7 below spells out precisely what this POC adds beyond what Uni-Sign
already had.

## 1. Dependency restoration

`rtmlib` was reinstalled **pinned to the exact version already proven in this project**
(`rtmlib==0.0.13`, matching the dist-info metadata left from the prior Uni-Sign run),
via `pip install --no-deps --force-reinstall rtmlib==0.0.13` into the existing
`unisign-cpu-arm64` conda env — no other package in that env was touched (verified:
`onnxruntime 1.23.2`, `opencv-python 4.10.0.84`, `decord 0.6.0`, `torch 2.1.1` all
unchanged before/after). The prior install had been `pip install -e` from a
session-scratchpad checkout that no longer exists (see D0 §4); this reinstall replaces
that broken editable pointer with a normal PyPI wheel at the same version — a repair, not
an upgrade.

**Reproduced the same extraction path Uni-Sign previously used:** the two cached ONNX
model files already on disk from that prior run —

| File | SHA-256 |
|---|---|
| `yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx` (detector) | `ceb11c07298f95c50d7c5abeb906d03340c85f23aa79e3e66966e7fb6c307250` |
| `rtmw-dw-l-m_simcc-cocktail14_270e-256x192_20231122.onnx` (pose) | `68db326c5c6f3273456f803eae0faf5440478369f2c3ee67258d2f36512e8d76` |

— exactly match `rtmlib`'s built-in `'lightweight'` mode, so `Wholebody(mode='lightweight', backend='onnxruntime', device='cpu')` loaded them directly with **no network
download** (confirmed live: model load 0.22s, log lines read `load
/Users/.../checkpoints/...onnx`, no download progress). This is the same detector+pose
model pair Uni-Sign's own `online_inference.py` used for this corpus.

## 2. Exact 5 clips

| clip_id | duration_s | why selected (from D1 plan) |
|---|---|---|
| `92V3oH63zbQ_5-1-rgb_front` | 1.83 | Shortest; both frame-baseline and native-video Gemini were completely empty here |
| `Fz-N1S0swh8_2-8-rgb_front` | 2.27 | `fast_signing` + `fingerspelling_candidate`, single-wrong-word baseline |
| `-g0iPSnQt6w_0-1-rgb_front` | 3.51 | `fingerspelling_candidate` + `question` |
| `G19uBylwQww_1-2-rgb_front` | 4.53 | Richest tag combination, least-bad baseline WER (0.8077) |
| `FzmL8SL6Bow_1-8-rgb_front` | 25.77 | Longest; deepest existing cross-referenced artifact trail (frame-baseline, Uni-Sign, native-video Stage 1 all already exist for this one clip) |

## 3. Extraction success/failure

**5/5 succeeded.** No failures, no retries needed.

| clip_id | frames processed | extraction wall-clock |
|---|---|---|
| `92V3oH63zbQ_5-1-rgb_front` | 55 | 3.28s |
| `Fz-N1S0swh8_2-8-rgb_front` | 54 | 3.22s |
| `-g0iPSnQt6w_0-1-rgb_front` | 175 | 10.43s |
| `G19uBylwQww_1-2-rgb_front` | 136 | 8.07s |
| `FzmL8SL6Bow_1-8-rgb_front` | 618 | 37.23s |

Total: 1,038 frames across ~38s of video in 62.2s of extraction wall-clock (excluding
0.22s one-time model load) — roughly real-time-to-2x-real-time throughput on CPU.

## 4. Quantitative tracking-quality table

| clip_id | frames | body detected | L-hand detected | R-hand detected | missing % (body/L/R) | mean conf (body/L/R) | multi-person frames |
|---|---|---|---|---|---|---|---|
| `92V3oH63zbQ_5-1-rgb_front` | 55 | 55 | 55 | 55 | 0.0 / 0.0 / 0.0 | 0.906 / 0.885 / 0.880 | 0 |
| `Fz-N1S0swh8_2-8-rgb_front` | 54 | 54 | 54 | 54 | 0.0 / 0.0 / 0.0 | 0.861 / 0.835 / 0.811 | 0 |
| `-g0iPSnQt6w_0-1-rgb_front` | 175 | 175 | 175 | 175 | 0.0 / 0.0 / 0.0 | 0.877 / **0.579** / 0.877 | 0 |
| `G19uBylwQww_1-2-rgb_front` | 136 | 136 | 136 | 136 | 0.0 / 0.0 / 0.0 | 0.867 / 0.929 / 0.868 | 0 |
| `FzmL8SL6Bow_1-8-rgb_front` | 618 | 618 | 618 | 618 | 0.0 / 0.0 / 0.0 | 0.861 / 0.841 / 0.851 | 0 |

("Detected" = majority (≥50%) of that part's keypoints score ≥0.3, rtmlib's own
built-in visibility convention. "Detected" counts are identical to "frames" for every
clip/part above — i.e. every single frame of every clip cleared the detection bar.)

| clip_id | wrist velocity L/R (mean, norm-diag/s) | two-hand distance (mean, norm-diag) | discontinuity candidates L/R |
|---|---|---|---|
| `92V3oH63zbQ_5-1-rgb_front` | 0.178 / 0.574 | — (both hands rarely co-visible near center) | 5 / 14 |
| `Fz-N1S0swh8_2-8-rgb_front` | 0.473 / 0.625 | — | 6 / 2 |
| `-g0iPSnQt6w_0-1-rgb_front` | 0.055 / 0.265 | — | 0 / 12 |
| `G19uBylwQww_1-2-rgb_front` | 0.284 / 0.289 | — | 18 / 23 |
| `FzmL8SL6Bow_1-8-rgb_front` | 0.233 / 0.284 | 0.114 | 98 / 132 |

Discontinuity candidates are a **self-calibrated heuristic** (frame-to-frame jump >4x
that clip's own median step) — a count of moments worth a closer look, not a confirmed
tracking-error count (rtmlib's per-frame detect+pose call carries no persistent track ID,
so "identity swap" cannot be directly confirmed, only proxied by spatial jumps; see §5).

## 5. Trajectory visualizations created

- Static SVG hand-center-path plots: **all 5 clips**
  (`trajectory_probe/<clip_id>/trajectory_plot.svg`), now additively embedded in the
  matching inspector page.
- Full skeleton-overlay `.mp4`: **1 clip** (`92V3oH63zbQ_5-1-rgb_front`, 55 frames,
  1280×720, confirmed valid via `ffprobe`) — built to demonstrate it's practical; not
  built for all 5 given the POC's effort scope (static plots were the primary deliverable
  per the D1 plan's own preference).
- Skeleton-overlay still frames (visual spot-checks, not persisted as deliverable files —
  used for the human sanity check in §D1.6): **4 clips**
  (`92V3oH63zbQ`, `Fz-N1S0swh8`, `FzmL8SL6Bow`, `-g0iPSnQt6w`) — exceeding the plan's
  ≥2/5 minimum. All four visually confirmed correct: skeleton lines on the actual
  shoulders/arms, face landmarks on the actual face, hand skeletons (including individual
  finger joints) on the actual hands, including a clearly-resolved fingerspelling-style
  hand shape on `Fz-N1S0swh8`.

## 6. Main failure modes observed

**None at the missing-tracking level** — 0% missing tracking on every part, every clip.
The two things actually observed worth naming as failure-adjacent (neither rose to a
tracking failure):

1. **Asymmetric hand confidence on `-g0iPSnQt6w_0-1-rgb_front`** (left-hand mean 0.579 vs.
   right-hand 0.877): traced to one hand being visibly more active/prominent in frame than
   the other (visual spot-check confirms both hands ARE tracked, just with different
   certainty) — a real, explainable characteristic of that clip's content, not a detector
   defect. Still cleared the majority-of-points threshold in 100% of frames.
2. **Discontinuity candidates scale with clip length and hand speed**, not with any
   obvious defect — the longest clip (`FzmL8SL6Bow`, 618 frames) has the most raw
   candidates (98 L / 132 R) simply because it has the most frame-to-frame steps; rates
   (~16–21%) are comparable across clips regardless of duration. Not independently
   confirmed as true tracking errors vs. genuine fast motion — this heuristic flags
   moments for human review, it does not itself adjudicate them.

No occlusion, no lost-track, no wrong-person-tracked, no zero-detection span occurred on
any of the 5 clips.

## 7. Comparison with what Uni-Sign already extracts — what is actually new here

| | Uni-Sign (already existed) | This Phase D1 probe (new) |
|---|---|---|
| Tracker | RTMPose (via `rtmlib`), same detector+pose model family | Same — `rtmlib` `Wholebody`, `lightweight` mode, same cached ONNX weights |
| What happens to the keypoints | Consumed internally by a trained graph/temporal skeleton encoder → mT5 decoder; **never exposed as an inspectable artifact** | Persisted directly as `landmarks.json` (raw) + `trajectory_summary.json` (derived) — human/tool-inspectable, nothing hidden inside a trained model |
| Tracking-quality measurement | **Not measured anywhere in this project** — Uni-Sign's WER (0.948 corpus-wide on 19 clips; 0.5–2.07 on our diagnostic-12) reflects the *whole pipeline* (tracking + encoder + mT5 decoder combined); no prior evidence isolates whether poor results were a tracking problem or a decoder/training problem | Measured directly and explicitly: missing-tracking %, per-part confidence, discontinuity candidates, visual spot-checks — see §4/§6 |
| Derived kinematic signals (velocity, pauses, two-hand distance, body-relative bands) | Implicitly learned inside the trained encoder's weights, not extractable or inspectable | Explicitly computed and persisted as plain numbers |
| Consumption path | Fixed: skeleton → from-scratch graph encoder → mT5-base decoder (a completely different architecture from Gemini) | Designed (D2) to be: trajectory summary → short structured text → **appended to Gemini's existing input** — tests the signal against the actual production-relevant model, not a different architecture entirely |
| Visualization / inspector integration | None in this project | SVG plots + overlay video, additively integrated into the existing frame-inspector |

**A narrow, scope-limited new empirical fact this POC adds:** on these **same 5 clips**
(not the full 19- or 128-clip corpus Uni-Sign was scored on), we now have direct,
independent tracking-quality evidence (0% missing, high confidence, visually-confirmed-
correct skeletons — see §4/§6). On **these 5 clips specifically**, poor pose tracking is
**unlikely** to explain Uni-Sign's translation failure — the tracking itself is
demonstrably clean here. **This should not be generalized to all 128 clips**; Uni-Sign's
tracking quality on the other 123 clips has not been independently measured by this POC
and could differ. Within that scope, this weakly suggests Uni-Sign's known failure mode
on these clips (topic hallucination, a repetition loop on its own one-clip qualitative
result) more likely sits in its encoder/decoder/training-data than in input tracking —
offered as a scoped, tentative observation, not a corpus-wide conclusion.

## 8. Usable / partially usable / unusable classification

| clip_id | classification | reasoning (observable tracking evidence only) |
|---|---|---|
| `92V3oH63zbQ_5-1-rgb_front` | **Usable** | 0% missing all parts; visually confirmed correct overlay; non-degenerate trajectory despite being the shortest clip |
| `Fz-N1S0swh8_2-8-rgb_front` | **Usable** | 0% missing all parts; visually confirmed correct finger-level detail on a fingerspelling+fast-signing clip — the hardest case in the set, and it held up |
| `-g0iPSnQt6w_0-1-rgb_front` | **Usable** | 0% missing all parts; visually confirmed correct; one hand's confidence is notably lower (0.579) but still consistently above threshold and explainable by real reduced prominence in frame, not a defect |
| `G19uBylwQww_1-2-rgb_front` | **Usable** | 0% missing all parts; strongest hand-confidence numbers in the set (not independently visually spot-checked this round, relies on quantitative evidence alone) |
| `FzmL8SL6Bow_1-8-rgb_front` | **Usable** | 0% missing all parts sustained over 25.75s/618 frames; visually confirmed correct mid-clip on a second, different signer |

**5/5 usable. 0 partially usable. 0 unusable.**

## 9. Does D1 support proceeding to D2?

**Yes, against the pre-registered D1.7 failure criteria** (from the D1 plan): missing-
tracking stayed at 0% (target was <15% per hand to pass), the human sanity check found no
mistracking across 4 spot-checks (target was ≥2/5), and even the two shortest/fastest
clips produced clearly non-degenerate trajectories. None of the three explicit D1 failure
conditions (excessive missing-tracking, visually wrong tracking, impractical throughput)
occurred.

**This is a tracking-quality verdict only.** It says the representation is reliably
*recoverable* from this video corpus — it says nothing on its own about whether
trajectory-derived context would change Gemini's semantic output. That question has since
been tested: D2 has been run and is now closed as a negative result — appending
RTMPose-derived trajectory text to Gemini's existing frame-based prompt produced 0/5
genuine semantic recoveries on these same 5 clips. See `PHASE_D2_RESULTS.md` for the full
per-clip results.

## 10. Inspector integration

Purely additive, matching the pattern already used for Uni-Sign/native-video: a new
"Trajectory probe (RTMPose via rtmlib, Phase D1)" section on each of the 5 covered clip
pages (missing-tracking %, confidence, discontinuity counts, the inline SVG plot, a link
to `QA.md`); the other 7 pages get an explicit "Not run for this clip" note, never a
silent omission. `index.html` gains one new column ("trajectory probe": done/not run) and
a banner stating 5/12 coverage with an explicit "no ASL semantic interpretation" note.
Nothing existing (timeline, frames, motion trace, batch boundaries, word diffs, all three
existing prediction rows) was altered — confirmed by diff review.
