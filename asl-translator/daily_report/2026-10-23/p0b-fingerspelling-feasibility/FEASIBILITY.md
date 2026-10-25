# P0-B — fingerspelling / proper-name local fusion: feasibility (2026-10-23)

**Status (updated 2026-10-24): recognizer survey done (desk research only, see below). Still blocked on an ASL-fluent
reviewer.** No spans have been inferred, no hand video extracted, no recognizer installed or run, nothing downloaded.
`interval_labels.csv` is still blank. Source: [boss report §8](../../2026-10-21/UNISIGN_CASE_REVIEW_AND_P0_PLAN.md).
Protocol: [P0_PROTOCOL_FREEZE.md §2](../P0_PROTOCOL_FREEZE.md).

## Question

Does the continuous hand RGB video contain letter information that the current pose path does not keep, and can it
be recovered with few false positives?

## Cases and matched inputs

Windows come from `../p0a-candidate-rerank/provenance/case_provenance.csv`, in source-video seconds. The page video
in the inspection sheet is the **original** window only.

| ID | clip_id | Reference name (scoring only, never a lexicon) | Original window (D-B, page video) | Realigned window (D-A, official input) | IoU | Source raw video (test) |
|---|---|---|---|---|---|---|
| R02 | G3OMdQo1zjY_0-10-rgb_front | Mike Camelin (+ school / place names) | 3.31–7.50 | 1.43–11.69 | 0.41 | `raw_videos/G3OMdQo1zjY-10-rgb_front.mp4` |
| R05 | G3VM7etNABI_0-10-rgb_front | Les Whitley | 1.22–6.47 | 0.76–8.33 | 0.69 | `raw_videos/G3VM7etNABI-10-rgb_front.mp4` |
| R35 | G2kVb4gINSI_1-10-rgb_front | CarolAnn | 6.50–12.48 | 13.11–16.90 | **0.00** | `raw_videos/G2kVb4gINSI-10-rgb_front.mp4` |

The raw videos are present locally in `~/Desktop/curify/p018-work/downloads/test_raw_videos.zip` (test split; listed,
not extracted).

**R35:** the two windows do not overlap. If a fingerspelled name exists, it can be in either window or in neither.
The reviewer must see both.

## Feasibility steps (in order; each gated by the previous)

1. **Reviewer spans (blocking).** Send `asl_reviewer_request.md`. The reviewer fills `interval_labels.csv` blind
   first (letters seen), then unblinded (does it match the reference name?). Claude does not fill this file.
2. **Matched clip export (after reviewer agreement on the format).** Cut both windows from the raw source at native
   resolution with `ffmpeg`, with no re-scaling and no contact sheets. Kept local, not committed.
3. **Recognizer survey (can run in parallel with step 1).** List existing fingerspelling recognizers: input type
   (RGB vs landmarks), licence, whether weights are available, CPU runnability, and expected input format. Nothing
   is assumed to exist until verified.
4. **Dev comparison (only on confirmed spans).** Character error rate and exact name match, recognizer vs the
   current Uni-Sign output, on confirmed spans only.
5. **Local replacement test.** Replace a name only above a fixed confidence. Low confidence means no change. Log
   every replacement, wrong replacements, uncovered cases, and any whole-sentence damage.

## Exit conditions (frozen)

Pause P0-B if any of these hold:
- the name is not in the matched window;
- it is not fingerspelled;
- the frames are insufficient;
- no recognizer gives a reliable gain.

Never feed reference names as a candidate list, and never guess-complete a name. Needing a specialist trained from
scratch is not a low-cost fix and goes back to the boss.

## Blockers

| Blocker | Owner | Notes |
|---|---|---|
| ASL-fluent reviewer for 3 cases × 2 windows | Baobao / boss | The 45-clip ASL review is still pending. This request is small (about 6 short windows). |
| Recognizer availability and licence | Claude (survey) | **Surveyed 2026-10-24** (below). Two have public weights for a research-only diagnostic. None is cleared for commercial use. Running one needs a MediaPipe re-extraction of the matched windows (our P0-12 poses are RTMPose-133, not MediaPipe). |
| Official crop RGB is not stored locally | — | D-A windows can be cut full-frame from raw. The official crop box is not available as video. |

## Recognizer survey (2026-10-24, desk research only)

Scope: existing, public systems that take ASL fingerspelling video (or poses from it) and output letters. Done from
public repos and papers only. **Nothing was installed, downloaded or run**, and no target clip was touched. "Weights
available" means the README links a checkpoint. It has not been checked that the files download or load. Facts marked
*unverified* come from secondary summaries and must be confirmed before use.

### Constraints any candidate must meet (from protocol §2 and §0)

- It already exists. No training or fine-tuning.
- Its licence permits research-diagnostic use. Shipping would need a separate commercial licence.
- It runs on local CPU (no GPU).
- It decodes **open-vocabulary letters** (CTC greedy or beam search, no lexicon). If a repo adds a word-level or
  name-list LM, it must be switched off, and **no reference name is ever given as a vocabulary**.
- It runs on the **reviewer-confirmed span**. Every candidate below assumes a pre-trimmed fingerspelling segment. None of
  them localizes fingerspelling inside a full sentence, so none of them can confirm a span by itself.

### Our input vs what they expect

How2Sign test is studio green-screen, frontal, one signer, 1280×720, 24–30 fps. That is easier for hand/pose extraction
than ChicagoFSWild (YouTube in-the-wild) or FSboard (phone selfie). But our sentences mix fingerspelling with lexical
signing, and all candidates were trained on fingerspelling-only segments. Our stored P0-12 poses are **RTMPose
COCO-WholeBody-133**. Every pose-based candidate expects **MediaPipe Holistic/Hands landmarks**, so the matched windows
would be re-extracted with MediaPipe on CPU (a few seconds of video, which is cheap). The RGB candidates expect a signing-hand
crop. The license (How2Sign CC BY-NC 4.0) allows research use. No derived video is committed.

### Candidates

| # | System | Official source | Task | Input | Continuous FS | Pretrained weights | Licence | CPU/GPU | Expected preprocessing | Can take our How2Sign hand video? | Known limitations | Setup | Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **OpenFS** (Cha, Kim, Park; CVPR 2026, arXiv 2602.22949) | github.com/AIRC-KETI/OpenFS | FS recognition (+ signing-hand detection, pose synthesis) | Pose sequence: MediaPipe Holistic hand landmarks (+ arm points for raised-hand detection); YOLO11s person detector for multi-person video | Yes (sequence → letters) | **Yes**: `download_ckpts.sh` / Google Drive. `recognizer` (ChicagoFSWild), `recognizer_plus` (+ synthetic data), `recognizer_fsboard` (FSboard) | **Non-commercial research only.** Commercial use needs the authors' permission | Tested on an A40 / CUDA 12.4. CPU inference is plausible for a pose model on a few seconds of video, but *unverified* | Image frames on disk → YOLO11s → MediaPipe Holistic (`model_complexity=2`) → `.npy` hand poses. No FPS resampling (sorted frame index) | **Yes, after MediaPipe re-extraction** of the confirmed span. Single signer, so the simple branch applies | No FPS handling (our 24 vs 30 fps clips go in as is). `preprocessing.py` has file-skip bugs. FSboard schema caveats in its README. Does the decoder use an LM or lexicon? Check and disable. New repo (2026), little outside use | Medium: conda + requirements; test scripts expect their npz layout | **Viable** (first choice) |
| 2 | **HandReader** (ai-forever, arXiv 2505.10267) | github.com/ai-forever/handreader | FS recognition | Three variants: **KP** (MediaPipe on raw frames, 54 hand + pose points × xyz), **RGB** (signing-hand crops, ~224 px), **RGB+KP** | Yes (CTC + 2-layer BiGRU) | **Yes**: `HandReader_ChicagoFSWild`, `HandReader_ChicagoFSWild+`, `HandReader_Znaki` (Russian; not usable for ASL) zips on Sber Cloud | Code Apache-2.0. **Weights licence not stated.** ChicagoFSWild itself has no stated licence | Trained on an H100. The paper reports timings on a MacBook M1 Pro single CPU core: KP 3.9 ms, RGB 51.4 ms, RGB+KP 55.2 ms per sample (Znaki; hardware for the table *unverified*) | KP: MediaPipe on raw frames, NaN → 0. RGB: hand crops from the iterative-attention hand detector of Shi et al. 2019 (not packaged); the paper suggests a centre crop if the signer is centred | **KP: yes, after MediaPipe re-extraction.** RGB: yes only with a hand-crop step we would have to supply | README gives only the Znaki test command; the Chicago config and data layout are undocumented; "TBA" sections; PyTorch 2.0.1 / 2.3.1 with CUDA wheel URLs (need CPU wheels). Letter accuracy on ChicagoFSWild+ 72.4 (KP) / 75.6 (RGB+KP) | Medium–high (undocumented data format) | **Viable** (KP variant), second choice |
| 3 | **Fingerspelling PoseNet** (Fayyazsanavi et al., arXiv 2311.12128) | github.com/pooyafayyaz/Fingerspelling-PoseNet | FS recognition | MediaPipe pose (`extract_pose_mediapipe.py`) + signing-hand detection | Yes (CTC-style decoder; `train_with_lm.py`) | Yes (Google Drive, per README) | **No licence file** (all rights reserved by default) | GPU not stated; small pose model | MediaPipe extraction → their CSV/feature format | Technically yes, after MediaPipe re-extraction | No inference instructions; LM-assisted decoding must be disabled. Letter accuracy ChicagoFSWild 66.3 / + 71.1 (secondary source) | Medium–high | **Maybe**: blocked on licence (ask the authors) |
| 4 | **Kaggle "Google – ASL Fingerspelling" 1st place** (Henkel & Hanley, 2023) | github.com/ChristofHenkel/kaggle-asl-fingerspelling-1st-place-solution | FS recognition (phrase level) | 130 MediaPipe landmarks (hands, arms, face) | Yes (Squeezeformer encoder + transformer decoder, with a confidence output) | **No**: the README only gives the training recipe (GPU Docker) → TFLite export | Code Apache-2.0; competition data CC BY 4.0 | Training on GPU. The final TFLite runs on CPU | MediaPipe Holistic → their parquet/npy format | Only if trained, which protocol forbids | Phone-selfie phrase domain (addresses, URLs, phone numbers) | Low to read, high to reproduce | **Not suitable** (needs training). Re-check only if someone publishes the trained TFLite under a clear licence |
| 5 | **FSboard ByT5-Small baseline** (Georg, Tanzer et al., CVPR 2025) | arXiv 2407.15806 (dataset CC BY 4.0) | FS recognition | 30 Hz MediaPipe Holistic landmarks → ByT5 | Yes | **No public weights found** | Data CC BY 4.0 | — | — | — | — | — | **Not suitable** (no weights). Note OpenFS ships an FSboard-trained recognizer |
| 6 | **Iterative visual attention** (Shi et al., ICCV 2019) | github.com/chevalierNoir/asl-iter-attn | FS recognition on ChicagoFSWild | RGB frame sequences, face-ROI or whole frame | Yes (CTC + LM beam search) | **No** | No licence file | PyTorch 0.4, warp-ctc (old CUDA stack) | ChicagoFSWild-style frames | Only after training | Obsolete stack | High | **Not suitable** |
| 7 | Static alphabet / single-letter classifiers (e.g. HF `ColdSlim/ASL-TFLite-Edge`, Apache-2.0; the MediaPipe gesture-model tutorial built on a Kaggle model) | Hugging Face / blog posts | Single handshape → letter | One image, or a 64×64 render of hand landmarks | **No** (no segmentation; J/Z unsupported in at least one) | Yes | Mixed or unstated | CPU fine | Per-frame hand landmarks | Per frame only | Trained on posed isolated letters; no temporal model; would need our own letter-segmentation heuristic | Low | **Not suitable** as the recognizer. At most an ablation after a viable run |
| 8 | Fingerspelling **detection** (Shi et al. CVPR 2021; JSL point-supervised localization ICCVW 2025; BSL weakly-supervised Prajwal et al. 2022) | papers | Temporal localization of FS spans (BSL: + recognition) | RGB | — | Not verified / not found | — | — | — | — | Would only automate what the reviewer does; BSL and JSL are the wrong language | — | **Not suitable now**. Spans come from the reviewer |

### Shortlist (to try only after the reviewer confirms spans)

1. **OpenFS `recognizer_fsboard` and `recognizer`/`recognizer_plus`**: published ASL weights trained on two different domains;
   MediaPipe pose input; research licence explicit. Use both Chicago and FSboard checkpoints and report them separately (no
   picking the better one per case).
2. **HandReader KP (ChicagoFSWild+ weights)**: cheap CPU pose model; confirm the weights licence with the authors
   first, and reconstruct the Chicago data format from `configs/`/`src/`.
3. *(conditional)* **Fingerspelling PoseNet**: only if the authors grant a licence.

None of them is a commercial path today: OpenFS is non-commercial and the others lack weight licences. A positive
P0-B result would justify a licensing or own-training decision for the boss, not a ship.

### Pre-registered usage rules (added 2026-10-24, before any recognizer output exists)

- Input = the reviewer-confirmed span only (from `interval_labels.csv`, both windows if marked), cut from the raw test
  video at native resolution. MediaPipe Holistic is run on CPU over exactly that span.
- Decoding is open-vocabulary letters with the repo's LM or lexicon off; if a repo cannot run without an LM, that LM must
  be trained on data independent of How2Sign test and of the reference names, and its source logged.
- Character metrics are computed against the reviewer's **blind** letters (`letters_seen_blind`) and, separately,
  against the reference name. Reference names are never given to the recognizer.
- A tiny environment check (install, load weights, run on the repo's own bundled test sample) is allowed before the
  reviewer returns. It must not touch R02/R05/R35 or any How2Sign clip.

### What only the ASL-fluent reviewer can provide

- Whether each of R02, R05 and R35 contains fingerspelling at all (`fs_present`). It is not assumed.
- Exact span start and end in each matched window (O and R). For R35 the two windows do not overlap.
- Blind letter readings with `?` for unreadable letters. These are the primary character ground truth.
- Handshape visibility quality (good / partial / poor), which triggers the "frames insufficient" stop.
- Name sign vs fingerspelling vs lexicalized fingerspelling (e.g. `#`-loan signs), which changes what a recognizer can
  be expected to output.
- After unblinding: whether the letters match the reference name.
