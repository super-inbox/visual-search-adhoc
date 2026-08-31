# Open-source ASL/SLT baseline candidates — feasibility research, 2026-08-30

**Scope:** research only. Nothing installed, nothing downloaded beyond small
README/config/paper text, nothing trained, no GPU stack touched, no Curify
code modified, no private data used. Full column-by-column comparison:
`OSS_BASELINE_FEASIBILITY.csv`. Step-by-step reproduction plan for the primary
candidate: `SPAMO_REPRODUCTION_PLAN.md`.

> **2026-08-30 update — a genuinely runnable ASL baseline was found, and it
> is none of the candidates below.** A follow-up targeted search
> (`ASL_PRETRAINED_BASELINE_SEARCH.md`) found that the official **How2Sign**
> baseline itself — "Sign Language Translation from Instructional Videos"
> (Tarrés et al., CVPR WiCV 2023; `imatge-upc/slt_how2sign_wicv2023`) —
> ships a real, non-restricted, ~127MB How2Sign-trained checkpoint plus the
> official test-split I3D features, with a documented no-training evaluation
> path. This is a materially better candidate than SpaMo/SSVP-SLT/VTaMo for
> answering "does open-source ASL translation work at all" specifically
> because it is a lighter, older (2023), fully-released Fairseq system, not
> an LLM-decoder one. **Read `ASL_PRETRAINED_BASELINE_SEARCH.md` first** —
> the SpaMo-centric analysis below is still accurate but is no longer the
> best next step.

## The headline finding, before the per-candidate detail

**Neither P0 (SpaMo) nor P1 (SSVP-SLT) can produce a How2Sign number today
without training/fine-tuning from scratch.** This is the single most
important thing this research surfaced, and it changes the shape of "Phase 1"
from what was assumed going in:

- **SpaMo** ships exactly one public checkpoint, and it is **Phoenix14T-only**
  (verified by opening its pre-extracted-features Dropbox folder directly:
  the folder is titled `PHOENIX14T` and contains only Phoenix14T motion/
  spatial feature archives plus the checkpoint — no How2Sign or CSL-Daily
  entry exists there at all). The released code's dataset loader
  (`dataset/p14t.py`) and only config (`configs/finetune.yaml`) are likewise
  hardcoded to Phoenix14T, despite the paper and README both claiming
  How2Sign was validated.
- **SSVP-SLT** ships **zero public checkpoints of any kind** — its README
  and every sub-module README were checked directly; only the DailyMoth-70h
  *dataset* has download links, no model weights. It has the better native
  How2Sign code path of the two (its example commands literally target
  `/path/to/how2sign`), but there is nothing to run on it without first
  self-supervised-pretraining a video backbone from scratch — a
  materially heavier lift than SpaMo's LoRA fine-tune.

Both papers' claimed How2Sign numbers are real and citable (§ per-candidate
detail below), but reproducing either one requires training, which is
explicitly out of scope right now. This does not mean stop — it means the
smallest *honest* first milestone is a **pipeline-validation reproduction on
the one dataset each project actually ships a checkpoint for** (Phoenix14T,
for SpaMo), not an immediate How2Sign inference run. See
`SPAMO_REPRODUCTION_PLAN.md` M0–M6 for how this is sequenced.

---

## P0 — SpaMo (primary candidate)

- **Repo:** https://github.com/eddie-euijun-hwang/SpaMo — commit `aee7f8b6`
  (2025-07-09, message "ckpt_link"), no tags or releases exist; pin this
  exact commit SHA if/when cloned.
- **Paper:** Hwang, Cho, Lee, Park, *"An Efficient Sign Language Translation
  Using Spatial Configuration and Motion Dynamics with LLMs,"* NAACL 2025.
  https://aclanthology.org/2025.naacl-long.197.pdf
- **License: none.** No `LICENSE` file exists in the repo; none is stated in
  the README. Default copyright (all rights reserved) applies. This should
  be flagged to whoever eventually signs off on using this code, even for
  internal research/evaluation.
- **Task:** gloss-free continuous sign language translation, video → English
  (or → German/Chinese depending on dataset). Confirmed via paper abstract
  and architecture description.
- **Architecture (confirmed from paper §3 and repo source):** Spatial
  Encoder = CLIP ViT-L/14 (`openai/clip-vit-large-patch14`), applied with
  S²-multiscale wrapping; Motion Encoder = VideoMAE-L
  (`MCG-NJU/videomae-large`), applied with a sliding window (stride 8); Sign
  Adaptor = linear projection + 1D TCN + cross-modal MLP; LLM = **Flan-T5-XL**
  (~3B params), fine-tuned via **LoRA** (r=16, alpha=32) — confirmed for
  **both Phoenix14T and How2Sign** in the paper's implementation-details
  section (CSL-Daily instead uses mT0-XL).
- **Officially reported How2Sign numbers** (paper Table 2, read directly from
  the PDF, not summarized): BLEU-1 33.41, BLEU-2 20.28, BLEU-3 13.96,
  **BLEU-4 10.11**, ROUGE-L 30.56, BLEURT 42.23 — reported ahead of FLa-LLM
  (BLEU-4 9.66) and SSVP-SLT (BLEU-4 7.00) **under a controlled,
  non-dataset-scaled comparison protocol** (the paper's own footnote). SSVP-SLT's
  own paper claims a materially better number at full pretraining scale (>3
  BLEU points over prior SOTA) — so "SpaMo beats SSVP-SLT" is protocol-
  dependent, not an absolute, source-agreed ranking.
- **Training hardware, documented (paper Appendix A.3):** *"We train our
  model for 40 epochs, using a single NVIDIA A100 GPU, completing the entire
  process within 24 hours."* No VRAM figure is given; A100 exists in 40GB and
  80GB variants, unspecified which. No inference-only VRAM figure is
  documented anywhere.
- **Public checkpoint:** exactly one, `spamo.ckpt` (5.52GB, Dropbox) — and it
  lives inside a Dropbox folder titled **`PHOENIX14T`**, alongside
  `spa_feat_p14t.zip` (6.7GB) and `mo_feat_p14t.zip` (390MB) — no How2Sign or
  CSL-Daily counterpart exists in that folder. This was confirmed by directly
  opening the folder in a browser, not inferred from the README.
- **How2Sign in the released code: not present.** `preprocess/` contains only
  a `Phoenix14T/` subfolder (six `.npy` annotation files); `dataset/` contains
  only `datamodule.py` and `p14t.py` (the latter hardcodes `'lang': 'German'`
  and reads Phoenix-specific `{mode}_info_ml.npy` annotation files);
  `configs/` contains only `finetune.yaml`, itself hardcoded to
  `dataset.p14t.Phoenix14T` and Phoenix-specific paths. Using SpaMo on How2Sign
  requires **writing a new dataset class + annotation builder + config**
  mirroring `p14t.py`'s structure — real, scoped engineering work, not a flag
  flip.
- **Raw MP4 vs. features:** the *model* only ever consumes pre-extracted
  `.npy` features (spatial + motion), never raw video. Raw video is consumed
  only by the two standalone extraction scripts
  (`scripts/vit_extract_feature.py`, `scripts/mae_extract_feature.py`), which
  are generically written (HuggingFace `transformers` models + a `--device`
  CLI arg) and not hardcoded to Phoenix14T internally — only the example
  invocation in the README targets Phoenix paths.
- **Dependencies (from `requirements.txt`):** `torch==2.0.1`,
  `transformers==4.32.0`, `pytorch_lightning==1.9.5` (and, oddly, also
  `lightning==1.9.5` pinned separately — redundant/legacy, a minor
  cleanliness flag), `peft==0.7.1` (LoRA), `accelerate==1.4.0`, `einops`,
  `sacrebleu==2.2.0`, `rouge-score`, `omegaconf`, `wandb`. **No Python version
  is pinned anywhere**; `torch==2.0.1` in practice constrains this to Python
  3.8–3.11. **No CUDA version is pinned**; the training config's
  `precision: bf16` needs an Ampere-class (or newer) NVIDIA GPU for native
  support.
- **macOS / Apple Silicon:** **training/fine-tuning is effectively
  unsupported** — `configs/finetune.yaml` sets PyTorch-Lightning
  `accelerator: gpu` (CUDA-only terminology in Lightning 1.9.5) and
  `precision: bf16`, neither mapped to Apple's MPS backend anywhere in the
  code. **Feature extraction alone is plausible but untested** — both
  extraction scripts expose a `--device` argument and use plain HuggingFace
  `.to(device)` calls (no hardcoded `.cuda()`), so `--device mps` or
  `--device cpu` might work for CLIP ViT-L/VideoMAE-L inference, but this has
  not been tried and VideoMAE-large is likely to be very slow on CPU/MPS.
- **Storage, approximate:** repo clone <5MB; `spamo.ckpt` 5.52GB; Phoenix14T
  features 6.7GB + 390MB (not needed if we skip Phoenix14T entirely, but
  needed for the pipeline-validation milestone in the reproduction plan);
  CLIP ViT-L/14 weights via HF Hub ≈1.7GB; VideoMAE-L weights via HF Hub
  ≈1.2GB; Flan-T5-XL base weights via HF Hub ≈11GB (fp32) / ≈5.7GB (bf16).
- **Official evaluation command (from README, verbatim):**
  ```
  python main.py -c configs/finetune.yaml -e bleu --train False --test True --ckpt /PATH/TO/CHECKPOINT
  ```
  This is Phoenix14T-only as currently configured (the config file it points
  at hardcodes Phoenix14T paths); there is no separate "How2Sign" flag.

## P1 — SSVP-SLT (secondary candidate)

- **Repo:** https://github.com/facebookresearch/ssvp_slt (actively
  maintained, last push 2026-05-19).
- **Paper:** Rust, Shi, Wang, Camgoz, Maillard, *"Towards Privacy-Aware Sign
  Language Translation at Scale,"* ACL 2024. https://arxiv.org/abs/2402.09611
- **License: CC BY-NC 4.0**, confirmed by reading the actual `LICENSE` file
  (portions of the codebase separately under Apache-2.0/OpenCLIP licenses per
  the README's own disclosure) — clearer and more standard than SpaMo's
  no-license state.
- **Task:** gloss-free continuous SLT via self-supervised video masked-
  autoencoding (MAE) pretraining, transferred to supervised SLT fine-tuning.
- **How2Sign support in the code: the best of the three candidates.** The
  `translation/README.md`'s worked examples literally use
  `data_dir=/path/to/how2sign` and `--config-name slt_t5` with
  `data.train_data_dirs=".../how2sign,.../youtube-asl"` — this is a real,
  intended, documented How2Sign path, not a paper-only claim.
- **Public checkpoint: none, of any kind.** Checked the main README,
  `pretraining/README.md`, and `pretraining_clip/README.md` directly — the
  only downloadable artifacts anywhere in this repo are the **DailyMoth-70h
  dataset** files (raw/blurred/unblurred video + manifests). No MAE backbone
  checkpoint and no fine-tuned SLT checkpoint are released. Getting any
  number at all requires self-supervised-pretraining a video backbone from
  scratch (large-scale, unspecified compute budget) and then supervised
  fine-tuning — a strictly heavier lift than SpaMo's "download one 5.5GB
  checkpoint and fine-tune via LoRA."
- **Architecture:** Hiera (Meta's hierarchical video transformer) or a
  CLIP-based vision tower (`from_clip=true`) as the single video backbone
  (no separate spatial/motion split the way SpaMo has); T5 or a
  fairseq/Tarrés-et-al.-2023 decoder for translation.
- **Dependencies / environment — explicitly Linux + CUDA, no ambiguity:**
  `INSTALL.md`'s first line reads *"Linux, CUDA >= 11.7, Python >= 3.8,
  PyTorch >= 2.0.0"* (tested config: CUDA 11.8, Python 3.10, PyTorch 2.2.0).
  Setup additionally requires building **dlib from source with CUDA**, a
  custom **fairseq fork** (`fairseq-sl`), the **stopes** library, and
  **BLEURT built from source** — meaningfully more moving parts than SpaMo's
  plain `pip install -r requirements.txt`.
- **GPU/VRAM, documented:** feature extraction and translation training/eval
  are both described as based on *"fp32 training on 32GB V100 GPUs"*
  (`max_batch_size=2` for extraction); `INSTALL.md`'s own test-script sample
  output shows an `NVIDIA A100-SXM4-40GB` as the example device.
- **macOS / Apple Silicon: unsupported, explicitly** — "Linux" is stated as a
  hard requirement, not inferred; no CPU/MPS path is documented anywhere.
- **Setup complexity, relative to SpaMo:** meaningfully higher (from-source
  CUDA builds, a forked fairseq dependency, a separate BLEURT install) —
  confirmed directly from `INSTALL.md`, not assumed.

## P2 — VTaMo (now directly verified — no longer just research-only)

- **Repo:** https://github.com/junyi2005/vtamo (pushed 2026-07-19).
- **Paper:** *"VTaMo: Video-Text Alignment Model for Sign Language
  Translation,"* arXiv:2607.09126 (2026-07) — reports results on Phoenix-2014T,
  CSL-Daily, **How2Sign, and OpenASL**.
- **License: CC BY-NC 4.0** (confirmed by reading the actual `LICENSE` file
  content directly, same text as SSVP-SLT's).
- **Architecture:** frozen CLIP-ViT-Large (S²-Wrapper) encoder, an
  attention-based temporal encoder, and a LoRA-adapted Flan-T5-XL decoder —
  explicit multi-granularity alignment (Sinkhorn optimal transport + a
  learnable orthogonal transform + position-aligned contrastive learning)
  between visual segments and a pseudo-gloss.
- **Configs exist for How2Sign** (`configs/vtamo_how2sign.yaml`) and the
  data-prep scripts target How2Sign/OpenASL/Phoenix-2014T directly — real,
  not just paper-only claims this time.
- **But: no checkpoint, and no inference/evaluation code at all.** The
  repo's own README states this outright: *"Scope of this release. This drop
  contains the data-preparation and training code only. Inference/evaluation
  scripts and pre-trained VTaMo weights are not included yet — see the
  release plan below."* The TODO list confirms: training code released,
  inference & eval code unreleased, checkpoints unreleased.
- **This makes VTaMo the one candidate that cannot be run at all today, on
  any platform, with or without training** — distinct from (and worse than)
  "requires training": even a from-scratch training run would have no
  released way to produce translations afterward, since evaluation code
  doesn't exist yet either.
- Acknowledges its training codebase builds directly on SpaMo's.

## Auxiliary — not primary continuous-translation baselines (per your framing)

- **PhonSSM** — confirmed via its own abstract to be an **isolated sign
  recognition** model (skeleton/graph-attention-based phonological
  decomposition), evaluated on **WLASL2000** and zero-shot on **ASL
  Citizen** — no continuous video, no sentence-level translation output at
  all. Correctly excluded from primary-baseline consideration.
- **WLASL recognition models / ASL Citizen models / isolated-sign &
  fingerspelling systems** — all isolated single-sign or character-level
  tasks (see `PUBLIC_ASL_DATASET_RESEARCH.md`'s existing classification of
  WLASL and ASL Citizen as `AUXILIARY_SIGN_RECOGNITION`, not translation
  benchmarks). Same reasoning applies to any model trained on them: useful
  only as a component/pretraining signal for a hand-built pipeline, never as
  a stand-in for evaluating Curify's ASL→English sentence-translation
  product.
