# Second ASL baseline candidate search — Phase 2

**Scope:** Research and verification only. Nothing was downloaded (beyond
HTTP HEAD requests to confirm file existence/size), no environment was
created, no model was run, no production code was touched, nothing was
committed. This document records what was checked and why each candidate
was accepted or rejected.

**Goal restated:** find a motion-aware / continuous-video ASL→English
system that (1) is ASL-specific (not only DGS/CSL), (2) has public code
**and** a pretrained checkpoint usable **today without training**, (3)
accepts raw video or a reproducible feature-extraction path from raw
video, (4) can be evaluated on at least a subset of our frozen 19-clip
How2Sign benchmark, and (5) has a research/evaluation-usable license.

---

## Result up front

**Uni-Sign (Li et al., ICLR 2025 / `ZechengLi19/Uni-Sign`) is the winning
candidate — classification `RUNNABLE_NOW`.** It is the only system found
in this search, across both the candidates re-checked from the 8/30
search and every newly investigated 2025–2026 system, that ships a
pretrained checkpoint **trained and evaluated specifically on How2Sign
(ASL)**, releases it under a license that permits research/evaluation
use, and provides a documented, code-complete, training-free inference
path from a raw `.mp4` file to an English sentence.

This is a materially different situation from the 8/30 search, where the
only runnable ASL-native checkpoint found was the official How2Sign
baseline itself (OpenSLT) — i.e. Phase 1's own subject. Uni-Sign is an
independent, more recent, architecturally different system (skeleton/pose
temporal modeling + multilingual T5 decoder, optionally fused with RGB),
so it is a genuine second data point, not a restatement of Phase 1.

---

## Candidates re-checked from the 8/30 search (per instructions: only
if necessary)

The 8/30 search (`docs/daily_report/8.30/asl-open-source-baseline/OSS_BASELINE_FEASIBILITY.csv`)
already directly verified repo contents, checkpoints, and licenses for
these. Only one day has elapsed; nothing indicated a re-check was
warranted, so these classifications are carried forward as-is:

- **SpaMo** — `WRONG_TASK` / no usable ASL checkpoint. Its one real
  checkpoint (5.52GB) is Phoenix14T (German Sign Language) only; the
  released code has no How2Sign dataset loader at all despite the paper's
  claims.
- **SSVP-SLT (Meta)** — `NO_PUBLIC_WEIGHTS`. Best native How2Sign code
  support of any repo checked (worked examples literally use
  `/path/to/how2sign`), but zero model checkpoints of any kind (backbone
  or SLT) are released. Linux+CUDA-only install (dlib built with CUDA,
  custom fairseq fork). Would require self-supervised pretraining from
  scratch.
- **VTaMo** — `REQUIRES_TRAINING`, and worse: the maintainers' own README
  states inference code and weights are **both** unreleased future work.
  Cannot be run at all today, with or without training.
- **SignLLM (Gong et al., CVPR 2024)** — `UNVERIFIED`. No discoverable
  code repository at all, on arXiv's own linked-resources or elsewhere.
  (Not to be confused with the unrelated `SignLLM/Prompt2Sign` GitHub org,
  which does sign PRODUCTION — text-to-video — a different task by
  different authors; re-confirmed this distinction still holds in this
  search.)
- **SignVLM (Luqman, 2025)** — `WRONG_TASK`. Confirmed again this search:
  it is isolated sign RECOGNITION (word/sign classification: KArSL,
  WLASL, LSA64, AUSTL), not continuous English-sentence translation, and
  not ASL-specific (KArSL=Arabic SL, LSA64=Argentine SL, AUSTL=Australian
  SL; only WLASL is ASL, and only for isolated-word classification).
- **GFSLT-VLP (Zhou et al., ICCV 2023)** — `WRONG_TASK` for our purposes,
  re-confirmed directly this search by fetching the live README: the
  repo's own paper badges and installation/eval instructions only ever
  reference Phoenix14T (German) and CSL-Daily (Chinese) — no How2Sign
  config, checkpoint, or benchmark reference exists anywhere in the repo.
  Code license is MIT (real and permissive), but there is no ASL artifact
  to run under it.
- **OpenASL official repo** — `UNVERIFIED` / not a real candidate. Ships
  data-preparation scripts only; no model code of any kind exists in the
  repo.

---

## New candidates investigated this search

### Uni-Sign — `RUNNABLE_NOW` (primary recommendation)

- **Repo:** [`ZechengLi19/Uni-Sign`](https://github.com/ZechengLi19/Uni-Sign)
  (ICLR 2025, arXiv:2501.15187), actively maintained (pushed 2026-02-11,
  174 stars).
- **What changed since 8/30:** on **2025-12-20** the authors released
  "pose-only checkpoints and inference code for How2Sign and OpenASL,"
  explicitly "for researchers interested in ASL." This did not exist at
  the time of the 8/30 search and is the direct reason this candidate is
  now viable where it would not have been a month ago.
- **Architecture:** RTMPose-extracted 2D skeleton keypoints (body, hands,
  face) → a graph/temporal skeleton encoder (implementation derived from
  CoSign, a skeleton-based continuous-SLR method) → an mT5-base
  (multilingual T5) decoder producing English text. An optional
  RGB-pose fusion mode also exists (`--rgb_support`) that additionally
  conditions on raw RGB frames; we would use pose-only first since that's
  the officially released How2Sign checkpoint.
  This is a **genuinely different mechanism from both of Phase 1's
  systems**: Curify is frame-by-frame still-image reasoning with no
  explicit temporal model; OpenSLT is a single 3D-CNN (I3D) feature
  extractor feeding a from-scratch Fairseq transformer. Uni-Sign is
  explicit continuous **skeletal motion** over time (the literal thing
  Phase 1 flagged as Curify's structural weakness), decoded by a
  pretrained multilingual language model rather than a from-scratch
  vocabulary.
- **Checkpoint:** `how2sign_pose_only_slt.pth`, confirmed present and
  downloadable at
  `https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_pose_only_slt.pth`,
  **1,186,925,007 bytes (≈1.19GB)**, confirmed via `curl -sIL`
  (HEAD-follow, no body downloaded). An `openasl_pose_only_slt.pth`
  (≈1.19GB) also exists but is out of scope (OpenASL isn't our benchmark).
- **License:** the Hugging Face model card explicitly declares
  **`cc-by-nc-4.0`** for the checkpoint (non-commercial — acceptable for
  our research/evaluation use, not for production deployment). The GitHub
  **code** repo itself has **no LICENSE file** (`license: None` via the
  GitHub API) — this is a real gap, not a technicality to wave away: it
  means there is no explicit grant covering redistribution/modification
  of the code, only the conventional academic norm that published
  research code is usable for research. Flagging this explicitly as a
  blocker to resolve (at minimum, confirm acceptable use with the repo
  owner or legal) before any result derived from it is used beyond
  internal evaluation.
- **Raw video support:** **yes, directly.** `demo/online_inference.py
  --online_video {video_path} --finetune {ckpt_path}` runs pose
  extraction (via `rtmlib`, a lightweight ONNX-runtime-based RTMPose
  wrapper — not the heavier `mmpose` full framework) and inference in one
  step from a raw `.mp4`. This means it can run on **both** our own
  internal clean corpus clips **and** the 19 How2Sign benchmark clips
  without needing How2Sign's separately-hosted pre-extracted pose `.zip`
  files at all (those exist too, as an alternative/faster path, but raw
  video is the more direct route for our own footage).
- **Hardware / Mac feasibility:** no CUDA-only claim in the docs (unlike
  SSVP-SLT's explicit "Linux, CUDA >= 11.7" requirement). `rtmlib` uses
  ONNX Runtime, which has working CPU (and Apple-Silicon-native, via
  `onnxruntime` universal2/arm64 wheels) support — the same class of
  CPU-only path we already validated works for OpenSLT on this machine.
  **Two real risk items** in `requirements.txt`, both Linux/CUDA-leaning
  and not obviously Apple-Silicon-safe: `decord==0.6.0` (video decoding
  library with historically inconsistent macOS ARM wheels) and
  `deepspeed==0.16.3` (distributed-training library, almost certainly
  only needed for the training scripts, not `demo/online_inference.py`).
  Neither has been tested on this Mac yet — this is the main open
  technical risk, not a confirmed blocker.
- **Estimated download for a first single-clip test:** `mt5-base` text
  backbone weights (**2,329,735,129 bytes ≈ 2.33GB**, confirmed via HEAD
  request to `huggingface.co/google/mt5-base`) + the How2Sign checkpoint
  (**≈1.19GB**) + small `rtmlib`/RTMPose ONNX pose models (tens–low
  hundreds of MB, not yet individually measured) ≈ **~3.5GB total**.
  Materially smaller than SpaMo's ~18GB (checkpoint + features + decoder
  weights) from the 8/30 search, but still a real download, correctly
  **not** performed in this phase per instructions.
- **Can test on our internal clean clips:** yes, in principle, via
  `online_inference.py` directly on any local `.mp4` — no dataset-specific
  packaging required.
- **Can test on our 19 How2Sign clips:** yes — same mechanism, or via the
  officially pre-extracted `how2sign_pose_format.zip.*` pose files keyed
  by the same How2Sign `SENTENCE_NAME` IDs our benchmark already uses.
- **Major blocker:** none fatal, but three concrete open items before
  execution: (1) code-repo license gap (no LICENSE file — checkpoint
  itself is CC BY-NC-4.0), (2) `decord`/`deepspeed` Apple-Silicon
  installability unverified, (3) exact behavior/output format of
  `online_inference.py` on a single clip not yet observed (only the
  documented command signature has been confirmed, not a live run).

### RVLF (Rao et al., Dec 2025 / CVPR 2026) — `NO_PUBLIC_WEIGHTS`

Reports the newest and strongest published How2Sign numbers found in this
search (+1.4 BLEU-4 over its own baseline on How2Sign, +1.61 on OpenASL),
using skeleton motion fused with DINOv2 visual features plus a GRPO-based
RL fine-tuning stage — architecturally close to what we'd want. However,
**no GitHub repository, code, or checkpoint could be located** — only the
arXiv paper (2512.07273) and its CVPR 2026 camera-ready PDF. Worth
revisiting if the authors release code later; not actionable today.

### AttnSign / "Attention-Steered Vision-Language Models for SLT" (Hu et
al., Jul 2026) — `NO_PUBLIC_WEIGHTS`

Directly targets How2Sign and OpenASL with a VLM-based spatial-temporal
attention-steering approach — exactly the "native-video VLM" category
this search was asked to prioritize. No public GitHub repository, code,
or weights were found in any search result, only the arXiv abstract
(2608.00235). Too new (published within the last month) to have code
released yet in most cases. Not actionable today; worth a follow-up
search in a few weeks.

---

## On the "native-video VLM" priority specifically

The task asked to prioritize native-video VLM approaches. Two purpose-built
ASL-targeting VLM systems (AttnSign, RVLF) were found in the current
literature, but neither has released code/weights yet — both are
`NO_PUBLIC_WEIGHTS`. The remaining option in this category is a
**general-purpose, non-ASL-specific** video-language model (e.g. an
open-weight video-capable VLM) run **zero-shot** on our ASL clips with a
prompt asking for an English translation of the signing. This was not
deep-dived in this pass because Uni-Sign already clears every hard
requirement including ASL-specific training — a zero-shot general VLM
would be a weaker, un-ASL-trained fallback, appropriate only if Uni-Sign's
open risk items (§ above) turn out to be blocking. See
`NEXT_EXPERIMENT_PLAN.md` for how this fallback is sequenced.

---

## Classification summary

| Candidate | Classification |
|---|---|
| **Uni-Sign** | **RUNNABLE_NOW** |
| SpaMo | WRONG_TASK (checkpoint is Phoenix14T/German only) |
| SSVP-SLT | NO_PUBLIC_WEIGHTS |
| VTaMo | REQUIRES_TRAINING (no inference code released either) |
| SignLLM (Gong et al.) | UNVERIFIED (no repo found) |
| SignVLM (Luqman) | WRONG_TASK (isolated recognition, not ASL-specific) |
| GFSLT-VLP | WRONG_TASK (Phoenix14T/CSL-Daily only, no How2Sign) |
| OpenASL official repo | UNVERIFIED (data-only repo, no model code) |
| RVLF (Rao et al., CVPR 2026) | NO_PUBLIC_WEIGHTS |
| AttnSign (Hu et al., 2026) | NO_PUBLIC_WEIGHTS |
| General-purpose native-video VLM, zero-shot | RUNNABLE_WITH_SMALL_ADAPTER (fallback only — see above) |
