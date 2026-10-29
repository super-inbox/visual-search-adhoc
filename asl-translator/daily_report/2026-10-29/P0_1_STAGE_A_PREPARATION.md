# P0-1 Stage A preparation: keypoint vs hand-RGB fingerspelling recognition on confirmed spans

**Status:** preparation only, 2026-10-29.
- No recognizer was run and no prediction exists.
- No external API was called. No production change.
- No fingerspelling accuracy is claimed.

**Update (later 2026-10-29):** the blind reviewer package is built and HandReader_RGB passed a technical feasibility
check. See [`P0_1_STAGE_A_REVIEWER_PACKAGE_AND_RGB_FEASIBILITY.md`](P0_1_STAGE_A_REVIEWER_PACKAGE_AND_RGB_FEASIBILITY.md).
The HandReader facts and the decoding choice are now frozen in the pre-registration.

Source of truth:
- `NEXT_P0_PLAN.md` (2026-10-28, branch `origin/codex/asl-next-p0-20261028`), P0-1;
- the 2026-10-28 `PROGRESS_REVIEW.md`.

Files:
- script [`p0_1_stage_a_prepare.py`](../../experiments/p0-2026-10-29/p0_1_stage_a_prepare.py);
- scorer [`p0_1_stage_a_score.py`](../../experiments/p0-2026-10-29/p0_1_stage_a_score.py);
- [`results/`](../../experiments/p0-2026-10-29/results/): inventory, pre-registration, candidate set, blank label
  template.

## Bottom line

- **Keypoint baseline:** OpenFS recognizer @ `0d6fa3fa`, checkpoint `c8e4c227…2925`, on MediaPipe Holistic 2D hand
  keypoints with greedy decoding.
  - It is runnable and deterministic here, but platform/encode-sensitive: the boss's strings reproduce on 10 of 18
    windows.
  - It is frozen as the Stage A keypoint baseline. It is not hand-RGB fusion.
- **No hand-RGB recognizer exists locally.**
  - Primary candidate: **HandReader_RGB**. Code licence Apache-2.0; released checkpoint trained on ChicagoFSWild+
    (subject to its own terms); hand-crop input, CTC.
  - Fallback: **MiCT-RANet**. Full-frame RGB plus optical flow, released weights, but its licence is not stated.
  - Neither is installed.
- **Expanded blind label set:** 36 items from the frozen How2Sign v2 clips, chosen by a letter-free, input-side
  hand-motion screen. Tiers: 16 candidate-positive, 12 easy-to-confuse candidate-negative, 8 random.
  - Final positive / negative categories come only from blind Step 1 labels.
  - Uni-Sign already-correct controls are derived after labelling.
- **Frozen:** the label schema, the shared span/frame/crop pipeline, the metrics and the acceptance gates.
- **The scorer** passes its synthetic self-test.

## 1. Requirements carried over from the plan and review

- **Diagnostic scope:** Stage A is a diagnostic on independently human-confirmed spans. It is reported separately
  from automatic localization (Stage B) and fusion (Stage C), and is never presented as an end-to-end score.
- **No extra information:** the recognizers receive no reference text, target name, audio, captions or translation
  output.
- **Item types:** fingerspelling positives, easy-to-confuse ordinary-signing negatives, and Uni-Sign already-correct
  controls. The set must not be limited to names that look like successes.
- **Logged per item:**
  - source video ID and hash;
  - span times and crop box;
  - frame timestamps;
  - detection flags;
  - raw letters, candidates and abstain reason.
- **Timing:**
  - Source time, clip time and frame index are kept separate.
  - Per-letter timing stays blank: only span-level timing exists.
- **Metrics:** CER, whole-word accuracy, abstain rate, and false positives on negatives.
- **Model self-confidence** is never used as evidence.
- **Thresholds** are frozen here, before any confirmation-set result exists.

## 2. Inventory of existing fingerspelling artifacts

Full list with sha256s: `results/p0_1_stage_a_inventory.json`.

| Artifact | Role | Type | Reusable for Stage A? | Limitation |
|---|---|---|---|---|
| `experiments/p0-2026-10-27/specialist.py` | OpenFS CPU runner (boss's adapter) | keypoint | **yes**: baseline runner, span taken from the human label | abstains only when there are fewer than 8 hand frames; greedy decoding |
| `results/specialist_openfs_official.json` | OpenFS on R02/R05 official windows (R35 kept separate) | keypoint | legacy stratum only | `unverified_proposal`; R35 official span UNRESOLVED |
| `results/specialist_openfs_reproduction.json`, `specialist.json` | reproduction of the boss's old-window run | keypoint | platform-sensitivity evidence only | the boss's input videos are not local |
| `fs_detection_smoke.py`, `results/fs_detection_feasibility.json` | FS-Detection stage-1 on CPU, top-50 proposals | detector only (RGB + flow) | **no**; reserved for Stage B | no LICENSE file; stage 2 and NMS not ported; CPU equivalence not verified |
| `2026-10-23/asl-reviewer-followup/blind_review.csv` | existing Step 1 package (R02/R05/R35 fingerspelling checks) | label template | schema basis; its 3 fingerspelling cases stay a separate legacy stratum | labels still empty |
| `2026-10-23/p0b-fingerspelling-feasibility/interval_labels.csv` | earlier interval sheet | label template | superseded | unfilled |
| `how2sign_v2/validation/review_proper_noun_fingerspelling.csv` | proper-noun review | **reference-derived** | **no** (not allowed for selection) | derived from the reference |
| P0-12 `B_ours_5p39` RTMPose keypoints (local, git-ignored) | per-frame wholebody keypoints of the frozen v2 videos | keypoint (input side) | yes, for the letter-free selection screen only | rtmlib lightweight; not the OpenFS keypoint path |
| OpenFS repo and checkpoint (local scratch, not committed) | recognizer | keypoint | yes | non-commercial research licence |
| FS-Detection repo and checkpoint (local scratch) | detector | detector only | Stage B only | no licence |

Crop/time metadata from earlier work is window-level only: reviewer-package slices and P0-input-provenance spans. No
per-frame hand crop exists anywhere.

## 3. Keypoint baseline (frozen)

| Item | Value |
|---|---|
| Model | OpenFS recognizer (CVPR 2026, AIRC-KETI), `github.com/AIRC-KETI/OpenFS` @ `0d6fa3fa9b5aeaf99171e8c77e89531a22a6fd27` |
| Checkpoint | `recognizer/best_model.pth`, sha256 `c8e4c227…2925` (the boss's checkpoint) |
| Architecture | EncoderDecoderTransformer: `input_dim` 42 (21 hand points × 2D), d_model 256, 8 heads, 3 layers |
| Preprocessing | MediaPipe Holistic 0.10.9, complexity 1, full frame, no YOLO crop. A hand is kept on a frame only if its wrist is above its elbow. Per-hand upstream `normalize` |
| Decoding | greedy, max 32 tokens, open vocabulary, no lexicon or language model |
| Abstain | fewer than 8 hand observations, or an empty decoded string |
| Platform | M3 Pro, Python 3.11.7 x86_64 under Rosetta, torch 2.2.2 CPU |
| Reproducibility | same commit and checkpoint as the boss; deterministic run-to-run. The boss's strings reproduce on 10 of 18 windows because input encode and platform differ. Official-window inference is reproducible locally (Task 3) |
| Licence | non-commercial research only |

For Stage A, the only change is the span: `specialist.py`'s model call is fed the human-confirmed span instead of
fixed 2 s windows. It is never described as RGB or fusion.

## 4. Hand-RGB recognizer candidates (none installed or run)

| Candidate | Input | Checkpoint | Vocabulary / decoding | Dependencies / hardware | Continuous? | Fit for Stage A |
|---|---|---|---|---|---|---|
| **HandReader_RGB** (ai-forever, arXiv 2505.10267) | per-frame RGB **hand crops** (the paper uses the Shi et al. 2019 localizer, ~224 px) | **released** for ChicagoFSWild and ChicagoFSWild+ | letter sequence, CTC; no language model reported | torch 2.0.1, cu118 pins; the paper times CPU inference on an M1 (51 ms per clip) | letter-sequence clips (names, 1–4 words) | **Primary.** It actually consumes hand RGB, its code licence is Apache-2.0 (the checkpoint's ChicagoFSWild+ terms apply separately), and it is recent. Risks: our crops come from MediaPipe, not its localizer; only 2 public commits; ChicagoFSWild+ domain vs How2Sign studio video |
| **MiCT-RANet** (fmahoudeau) | **full RGB frames** (224/256p) plus Farneback flow; attention finds the hand | **released** (Proton Drive): MiCT-RANet34 V1, MiCT-RANet18 ChicagoFS V2 | CTC, beam 5, no language model | PyTorch 2.2, Python 3.10; README says it runs on a quad-core CPU | yes | **Fallback.** RGB-only and maintained, but there is **no stated licence** (research use must be confirmed), training code is not released, and it takes full frames, not hand crops |
| asl-iter-attn (Shi et al., ICCV 2019) | RGB plus flow, iterative attention | **none released** | CTC | PyTorch 0.4, Warp-CTC, Python 2.7 era | yes | rejected: no checkpoint, old stack |
| FS-Detection recognizer head | RGB plus flow | inside the detector checkpoint | attention-LSTM, training-only head | CUDA hard-coded | — | rejected: auxiliary training head, no licence |
| Static ASL-alphabet image classifiers (e.g., HF ViT/CNN) | single RGB images | many | 26 isolated letters | light | **no** | rejected: they need per-letter segmentation, which Stage A does not have, and are trained on studio stills |
| Landmark models (Kaggle 2023 winners, OpenFS) | keypoints | various | CTC | light | yes | not RGB |

Recommendation: install HandReader_RGB (ChicagoFSWild+ checkpoint) in an isolated CPU venv. Switch to MiCT-RANet only
if HandReader can't be verified or run, and only after its licence is confirmed for research use. Paper accuracies
were not a selection criterion.

## 5. Expanded blind label set (`results/p0_1_stage_a_candidate_set.json`)

**Pool:** How2Sign v2, 128 frozen test clips, one per source video. These clips are chosen because Uni-Sign A_official
predictions exist for all of them, which the control subgroup and Stage C need, and because their videos, hashes and
per-frame keypoints are local.
- **Excluded:**
  - 66 clips in the P0-15 fusion **sealed final** split (seal respected, including 30 dev clips);
  - 1 legacy Step 1 clip (R02, R05 and R35 stay a separate legacy stratum; the other two are sealed).
- **Eligible:** 61 clips. H18/H19 holdout guard passed.
- **Exposure:** every clip has prior Uni-Sign and Gemini exposure, so this is **not a clean holdout**. None of the 36
  has been run through OpenFS, FS-Detection or any RGB fingerspelling recognizer. 27 of the 36 were P0-2 pilot or
  reserve clips (Gemini/OpenAI only).

**Selection (input side only):** a frozen, letter-free hand-motion screen over the existing RTMPose keypoints.
- Score for a 1 s window: (fraction of frames with the hand raised) × (median handshape-change rate) / (1 + median
  wrist speed).
- The screen reads **no** reference text, name, model letter output, detector proposal, Uni-Sign or Gemini output, or
  past success.

| Tier | n | Rule | Screen score median |
|---|---|---|---|
| candidate-positive | 16 | top screen scores (signer cap 12 overall) | 10.9 |
| candidate easy-to-confuse negative | 12 | raised-hand fraction ≥ eligible median **and** screen score in the bottom half: ordinary signing with raised hands; first 12 by salted hash | 6.9 |
| random | 8 | first 8 of the remainder by salted hash | 8.7 |

- **Balance:** signer proxies 1 / 2 / 3 / 8 / 10 have 6 / 6 / 9 / 8 / 7 items; 9 items are dev-45 clips.
- **Blind IDs:** `FSA-001` to `FSA-036`, assigned by a salted hash, so the ID reveals nothing about the tier.
- **What the reviewer sees:** the blind-named clip only. No reference, tier, screen window or clip ID.

**Categories are decided by humans, not by the screen:**
- **Positive:** `fingerspelling_present = yes`, with letters at high or medium confidence.
- **Negative:** `fingerspelling_present = no`.
- **Uncertain:** excluded from primary metrics and reported.
- **Uni-Sign already-correct control:** a positive span whose human letters appear as a token in the Uni-Sign
  A_official output. This is derived after labelling, so selection never uses Uni-Sign correctness.

The screen's real fingerspelling recall is unknown. If labels leave too few positives (gate G0), more items are
labelled in a pre-declared order: remaining clips by screen score, in batches of 8 (6 by score, 2 by hash). Beyond the
61-clip pool, a raw How2Sign test pool would need new keypoints and a separate approval.

## 6. Blind Step 1 label schema (frozen)

Template: `results/p0_1_stage_a_blind_labels_TEMPLATE.csv`, one row per span.

Fields:
- `blind_id`, `video_file`, `span_no`;
- `fingerspelling_present` (yes / no / uncertain);
- `span_start_s`, `span_end_s` (clip seconds, span level only; **no per-letter times**);
- `letters` (a–z as signed, `?` for an unreadable letter);
- `letters_confidence` (high / medium / low);
- `signing_hand` (left / right / both / unclear);
- `visibility_issue`, `occlusion_issue`, `multiple_spans_in_clip`;
- `notes`, `reviewer_id`, `asl_background`, `labelled_at`.

**Not shown in Step 1:** the reference sentence, any expected name, OpenFS / RGB / Uni-Sign / Gemini output, the
selection tier or screen window, and the clip/source ID.

## 7. Shared span / frame / crop pipeline (implemented, self-tested)

1. **Timing:** ffprobe PTS for every decoded frame of the frozen clip. `frame_index`, `clip_time_s` and
   `source_time_s` (How2Sign START + PTS) are logged separately, with no resampling. Clip frame rates vary (24, 50
   fps), so PTS is always used.
2. **Span:** frames with start ≤ PTS < end.
   - **Positives:** the human span.
   - **Negatives:** the frozen 2 s probe window from the screen.
   - No detector is ever used for the temporal span. Stage A isolates recognition.
3. **Landmarks:** one MediaPipe Holistic 0.10.9 pass over the span frames, shared by both recognizers.
4. **Hand side:** the human-labelled signing hand. Otherwise, the hand with more raised valid frames (tie: right).
   Both recognizers use the same hand.
5. **Keypoint input:** the OpenFS path unchanged.
6. **RGB crop:**
   - **Box:** square, centred on the landmark bbox; side 1.6 × max(w, h), minimum 64 px.
   - **Smoothing:** centred 5-frame median over detected frames.
   - **Missing hands:** gaps of 4 frames or fewer are linearly interpolated (status `interpolated`); longer gaps are
     marked `hand_missing` and dropped.
   - **Frame edges:** the box is shifted inside the frame, never shrunk.
   - **Size:** resized to the recognizer's input size.
   - **Fallback recognizer:** MiCT-RANet takes full frames instead.
7. **Abstain:** fewer than 8 usable frames.
8. **Naming and metadata:** blind ID only. No reference text or name anywhere.

The functions `frame_table`, `span_frames`, `choose_hand` and `crop_boxes` live in `p0_1_stage_a_prepare.py`. The
self-test covers determinism, short-gap interpolation, long-gap `hand_missing`, edge clamping and hand choice.

## 8. Frozen metrics and acceptance gates

**Normalisation:** lowercase, a–z only. A human `?` matches any one letter.

**Primary metrics:**
- **CER:** Levenshtein edits over positive spans ÷ human letters. An abstain is scored as the empty string.
- **Whole-word exact accuracy.**

**Secondary metrics:**
- abstain rate on positives and on negatives;
- **false-positive rate on negatives** (2 or more letters emitted on the probe window);
- coverage;
- per-letter confusion;
- runtime per span.

**Paired comparison:** per-span ΔCER (RGB − keypoint).
- Wins / losses / ties, with a tie if |Δ| < 0.05.
- 95 % bootstrap CI clustered by source video: 10,000 resamples, seed 20261029.

**Subgroups:** Uni-Sign already-correct controls, dev-45 vs non-dev, and selection tier.

Model confidence is never read.

| Gate | Condition |
|---|---|
| **G0 validity** | at least 12 positive spans with letters (high or medium confidence) and at least 8 negatives; otherwise INSUFFICIENT_LABELS |
| **G1 CER** | RGB CER ≤ keypoint CER − 0.10 **and** the upper bound of the cluster-bootstrap CI of mean per-span ΔCER < 0 |
| **G2 word** | RGB whole-word accuracy ≥ keypoint whole-word accuracy |
| **G3 false positives** | RGB false-positive rate ≤ keypoint false-positive rate + 0.10 |
| **G4 breadth** | without the 2 largest-gain spans, RGB CER is still below keypoint CER, **and** RGB wins ≥ 1.5 × its losses |
| **Readable at known spans** | the better recognizer has CER ≤ 0.35 **and** whole-word accuracy ≥ 0.30. If not, the plan's rule applies: improve the recognizer first and postpone Stage B and fusion |

Outcomes:
- **RGB_ADDS_VALUE:** G0 and G1–G4 all pass.
- **NO_RGB_GAIN:** G0 passes and any of G1–G4 fails.
- **INSUFFICIENT_LABELS:** G0 fails.

These thresholds are fixed now and are hard-coded in the scorer, not passed as arguments.

## 9. Scoring code

`p0_1_stage_a_score.py` takes the blind label CSV, the candidate set, two prediction JSONL files and an optional
Uni-Sign output map. It computes all of the metrics, gates and subgroups above.

Its self-test uses only invented strings and checks:
- a broad RGB gain → `RGB_ADDS_VALUE`;
- a gain from only 2 spans → `NO_RGB_GAIN` (G4);
- RGB false positives → `NO_RGB_GAIN` (G3);
- too few labels → `INSUFFICIENT_LABELS`;
- abstain scored as all deletions (CER 1.0);
- confidence ignored.

No real labels or predictions exist.

## 10. Before labels vs blocked on labels

**Done or possible now, before labels:**
- inventory, baseline freeze, candidate set, schema, pipeline, metrics, gates, scorer (all done);
- building the blind reviewer package of 36 blind-named clips (not built yet: it copies videos);
- with approval, installing HandReader in an isolated venv and verifying its checkpoint hash and alphabet on a
  synthetic input.

**Blocked on blind Step 1 labels:**
- final positive / negative / uncertain categories, and the Uni-Sign control subgroup;
- the spans to feed both recognizers;
- running both recognizers;
- every metric, gate and verdict.

## Limitations

- **The screen is a heuristic for enrichment, not a detector.** Its recall and precision are unknown until labels
  arrive. The random tier provides an unbiased check.
- **Small pool:** 61 eligible clips after respecting the P0-15 seal. Every clip has prior Uni-Sign and Gemini
  exposure.
- **Crop domain shift:** HandReader was trained on crops from a different hand localizer. A Stage A failure could
  reflect that shift, not RGB as such. The report will say so.
- **Licences:** OpenFS is non-commercial research only. MiCT-RANet's licence is unknown. FS-Detection has none.
