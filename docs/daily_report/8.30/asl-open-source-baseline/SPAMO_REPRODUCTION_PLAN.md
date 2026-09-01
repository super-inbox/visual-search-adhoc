# SpaMo reproduction plan — milestones M0–M6

**Status: plan only.** Nothing below has been executed. No downloads beyond
what Phase 1 research already fetched (small text: README, requirements.txt,
config, paper PDF — no checkpoints, no feature archives, no model weights).

**Read this before M0:** SpaMo's released code and public checkpoint only
cover **Phoenix14T** (German Sign Language, weather-forecast domain), not
How2Sign — see `OSS_BASELINE_CANDIDATES.md`'s headline finding. This plan is
sequenced so that **M4 reproduces what SpaMo actually ships** (a Phoenix14T
number, using the model's own out-of-the-box config) before attempting
anything How2Sign-shaped, and splits the How2Sign milestone (M5) into a
pipeline-plumbing check (achievable without training) and a real-quality
result (which needs fine-tuning, out of scope now, called out explicitly).

---

## M0 — Environment compatibility check

**Goal:** confirm, on this Mac, without installing anything heavy, whether
SpaMo's stated dependency versions are even resolvable here.

**Exact commands:**
```bash
python3 --version
uname -m               # confirm arm64 (Apple Silicon)
python3 -c "import torch" 2>&1 || echo "torch not yet installed - expected"
pip3 index versions torch 2>&1 | head -5     # check torch==2.0.1 availability for this platform
```
**Required machine/environment:** this Mac, no changes. Read-only checks.
**Download/storage:** ~0 (a version index query only, no wheel download).
**Expected result:** confirms whether `torch==2.0.1` (pinned in
`requirements.txt`) has an official macOS arm64 wheel, and what Python
versions this machine has available (3.8–3.11 required in practice).
**Success criterion:** a compatible Python + torch combination is identified,
OR a clear incompatibility is documented (e.g., only newer torch available
on this Python).
**Likely blocker:** torch 2.0.1 does ship official macOS arm64 wheels, so
this step should succeed; the real blockers appear later (bf16/GPU
accelerator assumptions in M2–M5, not raw installability).
**Modifies this machine:** no.

---

## M1 — Clone and pin the official repository

**Exact commands:**
```bash
git clone https://github.com/eddie-euijun-hwang/SpaMo.git /path/to/scratch/SpaMo
cd /path/to/scratch/SpaMo
git checkout aee7f8b6ea8201b710690adcce6f46260dd11bba   # pin exact commit; no tags/releases exist
```
**Required machine/environment:** any machine with git + internet. Not
Curify's production repo — clone into a separate scratch location, never
inside `visual-search-adhoc`.
**Download/storage:** <5MB (repo is source-only, no large files tracked).
**Expected result:** a working tree at the exact commit this plan was
researched against, so future drift in the upstream repo doesn't silently
change what "M2 onward" means.
**Success criterion:** `git log -1` shows `aee7f8b6...`.
**Likely blocker:** none expected — small public repo, no auth needed.
**Modifies this machine:** adds one new directory outside this repo; no
system-level change.

---

## M2 — Minimal environment setup

**Exact commands:**
```bash
python3 -m venv /path/to/scratch/spamo-venv
source /path/to/scratch/spamo-venv/bin/activate
pip install -r requirements.txt
```
**Required machine/environment:** this Mac is sufficient for the *install*
step itself (no GPU needed to `pip install`). A dedicated virtualenv, not the
system Python.
**Download/storage:** requirements.txt pulls ~15 packages; the two heaviest
are `torch==2.0.1` (~200MB wheel) and `transformers==4.32.0` (~5MB, but pulls
`tokenizers`/`huggingface_hub` too). Total: roughly 500MB–1GB of pip
packages, no model weights yet.
**Expected result:** a clean install with no dependency-resolution errors.
**Success criterion:** `python -c "import torch, transformers, pytorch_lightning, peft"`
succeeds with no import errors.
**Likely blocker:** `pytorch_lightning==1.9.5` **and** `lightning==1.9.5` are
both pinned (redundant/legacy pairing observed in the repo, §
`OSS_BASELINE_CANDIDATES.md`) — possible but not certain version-resolution
friction; `torch==2.0.1` may also want a matching-generation `torchvision`
that isn't pinned in `requirements.txt` at all (not needed by this repo's own
code as far as reviewed, so likely a non-issue, but worth watching for at
install time).
**Modifies this machine:** yes, but reversibly — one new virtualenv
directory, deletable at any time; no system-wide or global Python changes.

---

## M3 — Obtain/load official pretrained assets

**Exact commands (Phoenix14T track — the only track with real assets):**
```bash
# checkpoint (5.52GB) and Phoenix14T features (390MB + 6.7GB) — Dropbox, no auth needed
curl -L -o spamo.ckpt "https://www.dropbox.com/scl/fi/c9khflgxgl96lx919p6oq/spamo.ckpt?rlkey=gp3zmk6jwg9cnf3e2hpw268ih&dl=1"
# (the mo_feat_p14t.zip / spa_feat_p14t.zip archives are in the same shared
#  folder; only fetch these if attempting M4's full Phoenix14T eval, not needed for M5)
```
**Required machine/environment:** any machine with ~13GB free disk and a
decent connection (checkpoint + both Phoenix14T feature archives together).
**Download/storage:** 5.52GB (checkpoint) + 390MB + 6.7GB (Phoenix14T
features, only if doing the full M4 Phoenix14T eval) ≈ **12.6GB total** if
all three are fetched; 5.52GB if only the checkpoint is needed (e.g. to
inspect its state-dict shape without running a full eval).
**Expected result:** a local `spamo.ckpt` file loadable by `torch.load`.
**Success criterion:** `torch.load('spamo.ckpt', map_location='cpu')` returns
a state dict without error.
**Likely blocker:** this is explicitly the kind of "multi-GB checkpoint
download" your instructions say not to do **yet** — flagging this milestone
as **paused pending your go-ahead**, not executed. No How2Sign-specific asset
exists to fetch here regardless (§ headline finding).
**Modifies this machine:** adds large files to disk; fully reversible
(delete after use), no system modification.

---

## M4 — Reproduce the official evaluation (Phoenix14T, the only dataset SpaMo actually ships)

**Exact command (from the README, verbatim):**
```bash
python main.py -c configs/finetune.yaml -e bleu --train False --test True --ckpt /path/to/spamo.ckpt
```
**Required machine/environment:** **NVIDIA GPU with CUDA required in
practice** — `configs/finetune.yaml` sets `accelerator: gpu` and
`precision: bf16` (Ampere+ GPU needed for native bf16); this Mac cannot run
this milestone as configured (see Q. B/C below). Requires a Linux+NVIDIA
machine.
**Download/storage:** needs M3's Phoenix14T features (7.1GB) in place at the
paths `configs/finetune.yaml` expects (`/data2/sl_datasets/vit_feat_Phoenix14T`,
`/data2/sl_datasets/mae_feat_Phoenix14T` — these hardcoded absolute paths
will need editing to point at wherever the features actually land).
**Expected result:** BLEU-1/2/3/4 and ROUGE numbers close to the paper's
Table 1 Phoenix14T row for SpaMo (B1 49.80, B2 37.32, B3 29.50, B4 24.32,
ROUGE 46.57) — this is the number to sanity-check reproduction against, not
How2Sign's numbers.
**Success criterion:** reproduced BLEU-4 within a small tolerance (a couple
points) of the paper's reported 24.32 on Phoenix14T.
**Likely blocker:** GPU/CUDA/bf16 requirement (see M0/environment); the
hardcoded absolute feature paths in `finetune.yaml` will need local editing
regardless of platform.
**Modifies this machine:** N/A — this milestone cannot run on this Mac at
all; it needs a different machine (see Q. C below).

---

## M5 — Run on our fixed 19-clip How2Sign mini subset

**Split into two sub-milestones because no How2Sign checkpoint exists:**

### M5a — Pipeline-plumbing check only (no training, achievable in principle)

Extract SpaMo-shaped spatial+motion features for our 19 clips and run a
forward pass through the **Phoenix14T-trained** checkpoint, purely to
confirm the mechanical pipeline (video → features → model → text) executes
without errors on our data shape.

**Exact commands (illustrative — requires the custom How2Sign dataset glue
described in `OSS_BASELINE_CANDIDATES.md`, not yet written):**
```bash
python scripts/vit_extract_feature.py \
  --anno_root /path/to/how2sign_mini_anno \
  --model_name openai/clip-vit-large-patch14 \
  --video_root asl-translator/data/public_benchmarks/how2sign/videos \
  --save_dir /path/to/scratch/how2sign_mini_feats/spatial \
  --s2_mode s2wrapping --scales 1 2 --batch_size 4 --device <cuda:0|mps|cpu>

python scripts/mae_extract_feature.py \
  --anno_root /path/to/how2sign_mini_anno \
  --model_name MCG-NJU/videomae-large \
  --video_root asl-translator/data/public_benchmarks/how2sign/videos \
  --save_dir /path/to/scratch/how2sign_mini_feats/motion \
  --overlap_size 8 --batch_size 4 --device <cuda:0|mps|cpu>
```
**Required machine/environment:** CLIP ViT-L/14 + VideoMAE-L are standard
HuggingFace models; extraction *might* run on this Mac via `--device cpu` or
`--device mps` (both scripts expose a `--device` flag, no hardcoded
`.cuda()`) — **untested, not documented as supported**, and VideoMAE-large
over 19 short clips would likely be slow but is a bounded, one-time cost if
it works at all.
**Download/storage:** CLIP ViT-L/14 (~1.7GB) + VideoMAE-L (~1.2GB) weights
from HF Hub; extracted features for 19 short clips would be small (tens of
MB, not GB).
**Expected result:** the model produces *some* text output per clip — almost
certainly **irrelevant/wrong** (fluent-sounding German-weather-forecast-style
output, or unrelated fragments), because a Phoenix14T-trained checkpoint has
never seen ASL, English, or How2Sign's domain. **This is expected and does
not indicate a bug** — it only proves the plumbing runs.
**Success criterion:** no crashes; one text string per clip is produced;
confirms feature shapes/dtypes match what the frozen checkpoint expects.
**Likely blocker:** requires writing the custom How2Sign annotation/dataset
glue first (not yet built — a real, scoped coding task); still needs a GPU
for the actual SpaMo `main.py` forward pass even if feature extraction itself
runs on CPU/MPS, because `configs/finetune.yaml`'s `accelerator: gpu`/`bf16`
assumptions apply to inference too, not just training.
**Modifies this machine:** downloads two moderate model checkpoints (~3GB)
if run here; otherwise none.

### M5b — A real How2Sign-quality result (out of scope right now)

Requires fine-tuning SpaMo on How2Sign's official training split (or at
minimum a domain-adaptation run) using the LoRA setup the paper describes,
on a real GPU, for real wall-clock time. **This is training and is
explicitly excluded from this workstream today.** Flagging it here only so
it isn't confused with M5a's much smaller pipeline check.

---

## M6 — Compare against Curify's current frame-based baseline

**Exact commands:** reuse the existing, unmodified
`asl-translator/asl-eval/evaluate.py` against SpaMo's output (once M5
produces a real, domain-appropriate text file) and Curify's own prediction
for the same 19 clips (once Curify's model has been run on them — a separate,
already-gated model-call decision, not part of this plan):
```bash
python3 asl-translator/asl-eval/evaluate.py \
    --reference asl-translator/data/public_benchmarks/how2sign/references/<clip_id>.srt \
    --prediction /path/to/spamo_output/<clip_id>.json
```
**Required machine/environment:** this Mac (scoring itself is local,
stdlib-only, no GPU needed) — only *producing* the two predictions being
compared needs a GPU/model call.
**Download/storage:** none beyond what M5/Curify's own run already produced.
**Expected result:** side-by-side WER/CER/BLEU-shaped metrics for Curify vs.
SpaMo (or any OSS baseline) on identical clips — the actual apples-to-apples
comparison this whole workstream exists to enable.
**Success criterion:** a comparison table exists and both predictions were
scored with the same unmodified tool against the same reference.
**Likely blocker:** depends entirely on M5b's real fine-tuned SpaMo output
existing — until then, M6 has nothing meaningful to compare (M5a's
domain-mismatched output would only prove the pipeline runs, not translation
quality).
**Modifies this machine:** no, scoring only.

---

## Answers

**A. Is SpaMo still the best first open-source baseline?**
Yes, but with the scope corrected: it's the best *pipeline-validation and
architecture-reference* candidate (single clean checkpoint, simplest
dependency list, only-somewhat-messy license situation), not a
"download-and-immediately-score-How2Sign" candidate — that path doesn't
exist for either SpaMo or SSVP-SLT today.

**B. Can THIS Mac realistically run it?**
Partially. Feature extraction (CLIP ViT-L/14, VideoMAE-L) is plausibly
runnable via `--device cpu`/`--device mps` but untested and undocumented.
The actual SpaMo model forward pass/training (`main.py`, PyTorch-Lightning
`accelerator: gpu`, `precision: bf16`) is **not realistically runnable
here** — no CUDA, no bf16-capable accelerator mapping in this Lightning
version.

**C. If not, what exact Linux/NVIDIA environment should be used?**
A single NVIDIA Ampere-class-or-newer GPU (A100 matches the paper's own
training hardware; anything bf16-capable with ≥24GB VRAM is a reasonable
starting guess for fine-tuning-scale work, though **no official inference-
only VRAM figure exists** to size a smaller card confidently) on Linux with
a CUDA toolkit matching `torch==2.0.1` (cu117/cu118-class).

**D. Can we use the 19 local raw MP4 clips directly?**
No. SpaMo's model never consumes raw video — only pre-extracted `.npy`
spatial+motion features (§ `OSS_BASELINE_CANDIDATES.md`).

**E. If not, what conversion/feature extraction is required?**
Run `scripts/vit_extract_feature.py` (CLIP ViT-L/14, S²-multiscale) and
`scripts/mae_extract_feature.py` (VideoMAE-L, stride 8) over the 19 clips,
after writing a small custom annotation file listing their IDs/paths/text
(mirroring the shape `dataset/p14t.py` expects) — see M5a.

**F. Do official pretrained assets exist and are they accessible?**
Yes for Phoenix14T only (checkpoint + both feature archives, all on Dropbox,
no auth needed, confirmed by direct inspection). **No pretrained asset of any
kind exists for How2Sign**, from either SpaMo or SSVP-SLT.

**G. What is the SMALLEST meaningful reproduction milestone?**
**M4** — reproducing SpaMo's own published Phoenix14T BLEU-4 (≈24.32) using
its shipped checkpoint and shipped config, unmodified. It requires a GPU we
don't yet have provisioned, but it needs zero new code (no custom dataset
glue) and directly validates whether the released checkpoint/config actually
reproduce the paper's own claim — the cheapest real trust-building step
before investing in the How2Sign custom-loader work of M5a.

**H. What is the exact next command I should run after reviewing your plan?**
None yet, by design — every milestone from M1 onward needs either a
download (M1/M3, paused pending your go-ahead per "no multi-GB checkpoints
yet") or a GPU machine we haven't provisioned (M4/M5b). If you want to take
the very first, essentially free, reversible step, it's **M0**:
```bash
python3 --version && uname -m
```
— confirms this machine's baseline before anything else is decided.

**I. Should we proceed with SpaMo, switch to SSVP-SLT, or stop due to
reproducibility blockers?**
**Proceed with SpaMo, but re-scope the near-term goal.** Don't switch to
SSVP-SLT — it has zero released checkpoints of any kind and a strictly
heavier Linux/CUDA/from-source install, despite better native How2Sign code
support. Don't stop either — reproducibility isn't broken, the initial
assumption ("inference-only How2Sign evaluation, no training") was just
wrong for both candidates, discovered here before any GPU spend happened.
The realistic near-term goal is: (1) M4 Phoenix14T reproduction on a
provisioned GPU machine, as a trust check on the released checkpoint; (2)
the custom How2Sign dataset glue + M5a pipeline check, useful immediately
even with domain-mismatched output; (3) a real How2Sign number (M5b) is a
**training** milestone and needs its own explicit go-ahead later, separate
from this data/feasibility workstream.
