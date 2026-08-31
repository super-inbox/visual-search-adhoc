# Targeted search: is there an actually-runnable pretrained ASL→English baseline?

**Scope:** research only. No installs, no large downloads, no model/API calls,
no training, no GPU provisioning. Every candidate below was checked against
its **primary source** (official repo file listing, license file, and — for
the one candidate that matters — the actual host serving its checkpoint
files, queried directly via API, not just read from a README's claim).

**The strict rule applied throughout, per your instruction:** a paper
reporting How2Sign/OpenASL numbers is not enough, and a GitHub repo existing
is not enough. `RUNNABLE_ASL_BASELINE` is reserved for candidates where (a)
compatible **ASL** pretrained weights actually exist and are accessible, and
(b) there is a plausible inference/evaluation path **without retraining**.

---

## Headline result

**Yes — one genuinely runnable candidate exists, and it is not SpaMo or
SSVP-SLT.** It is the **official How2Sign baseline model**, "Sign Language
Translation from Instructional Videos" (Tarrés et al., CVPR WiCV 2023 —
cited elsewhere in this research as "OpenSLT"):

- Code: https://github.com/imatge-upc/slt_how2sign_wicv2023 (MIT license)
- Data + weights: https://dataverse.csuc.cat/dataset.xhtml?persistentId=doi:10.34810/DATA693
  (CC BY-NC 4.0... **correction, verified directly: CC BY-NC-ND 4.0** — no
  derivatives, matching OpenASL's license class)
- **A real, non-restricted, ~127MB checkpoint** trained natively on How2Sign
  — confirmed by querying the Dataverse API directly (not by trusting the
  README), which returned the file with `restricted: false`:
  `final_models/baseline_6_3_dp03_wd/ckpts/checkpoint.best_reduced_sacrebleu_3.5401.pt`
  (126,827,063 bytes) — several other checkpoint variants exist alongside it,
  all similarly sized and similarly unrestricted.
- **The official test-split I3D features are also released**, pre-extracted,
  as `data/how2sign/i3d_features/test.zip` (572,646,623 bytes ≈ 546MB,
  `restricted: false`).
- A documented, code-backed, no-training evaluation command exists
  (`task generate` → `analyze_fairseq_generate.py`).

This is a materially different, much lighter-weight system than SpaMo/
SSVP-SLT/VTaMo: a classic Fairseq transformer over I3D features with a
from-scratch SentencePiece tokenizer, not a 3B-parameter LLM decoder — the
checkpoint is ~127MB, not 5.5GB+.

**Two real, unresolved items remain** before calling this "ready to run
today" (see §5) — neither requires training, both are disclosed rather than
glossed over.

---

## 1. Direct answer

**Does a genuinely runnable pretrained continuous ASL→English open-source
baseline exist? YES.**

- **Which one:** the official How2Sign baseline, OpenSLT (Tarrés et al.,
  CVPR WiCV 2023).
- **Exact checkpoint:** `checkpoint.best_reduced_sacrebleu_3.5401.pt` (or
  `checkpoint_best.pt` from the same run) — 126.8MB, hosted at CORA/Dataverse
  DOI 10.34810/DATA693, confirmed downloadable (non-restricted) via direct
  API query today.
- **Exact dataset:** How2Sign — the same dataset our own 19-clip mini
  benchmark was drawn from. This is not a different ASL corpus; it is
  literally the paper that ships alongside the How2Sign dataset itself.
- **Shortest path to first inference:** download the checkpoint (127MB) +
  the released test-split I3D features (`test.zip`, 546MB) + the vocab files
  (~570KB combined) → run `task generate` per the repo's documented
  `.env`/config → run `analyze_fairseq_generate.py` for BLEU/rBLEU. No
  feature-extraction step needed if our clip IDs are already inside
  `test.zip` (see §5).
- **Can we run our 19 How2Sign clips?** Very likely yes, not yet 100%
  confirmed — see §5.

---

## 2. Every candidate, strictly classified

Full detail in `OSS_BASELINE_FEASIBILITY.csv`. Summary:

| Candidate | Classification | One-line reason |
|---|---|---|
| **How2Sign official baseline (OpenSLT)** | **`RUNNABLE_ASL_BASELINE`** | Real, non-restricted, How2Sign-native ~127MB checkpoint + released test features; documented no-training eval path |
| SpaMo | `PIPELINE_REPRODUCTION_ONLY` | Its one real checkpoint is Phoenix14T (German SL) — not ASL at all; How2Sign has no checkpoint or released dataset loader |
| SSVP-SLT | `REQUIRES_TRAINING` | Best native How2Sign *code* fit of the LLM-based candidates, but literally zero checkpoints of any kind released (backbone or SLT) |
| VTaMo | `REQUIRES_TRAINING` (and worse) | Repo's own README states outright: *"Inference/evaluation scripts and pre-trained VTaMo weights are not included yet"* — training code only, no eval path exists on any platform today |
| GFSLT-VLP | `REQUIRES_TRAINING` | Only a generic MBart text-model backbone is released, not a finished SLT checkpoint; needs a 3-stage, 4-GPU pretrain+finetune pipeline; likely never validated on How2Sign at all (absent from SpaMo's own How2Sign leaderboard table) |
| SignLLM (Gong et al., CVPR 2024) | `UNVERIFIED` | No official code repository discoverable anywhere, despite being a published paper |
| SignVLM (Luqman, 2025) | `WRONG_TASK` | Isolated sign *recognition* across 4 sign languages, not continuous translation, no English sentence output |
| OpenASL official baseline | `UNVERIFIED` (effectively N/A) | The dataset's own official repo contains zero model code — `{LICENSE.md, README.md, assets, data, prep}` only, confirmed by direct listing |

---

## 3. Why the strict rule eliminated every LLM-based candidate

Every LLM-decoder candidate in this search (SpaMo, SSVP-SLT, VTaMo) shares
the same pattern: a paper claiming How2Sign results, a public repo, and
**no actual downloadable ASL-trained weights** behind either claim once you
open the real file listing (not just the README). This is worth stating
plainly because it's a real, repeated finding, not a one-off: the field's
current LLM-based SLT work is much better at publishing numbers than at
publishing the weights that produced them. The one candidate that clears the
bar (OpenSLT) predates the LLM-decoder wave — it's a 2023 Fairseq transformer
over I3D features — and clears it precisely because it's simpler and was
released more completely.

---

## 4. Task-fit verification detail for the runnable candidate

- **Continuous SLT, not isolated recognition:** confirmed — the whole repo
  is built around sentence-level How2Sign clips and Fairseq's
  sequence-to-sequence translation task.
- **ASL specifically:** confirmed — How2Sign is the sole dataset this repo
  targets; no other language.
- **English sentence output:** confirmed — the released vocab
  (`cvpr23.train.how2sign.unigram7000_lowercased.*`) is an English
  SentencePiece model; the paper reports BLEU/rBLEU against English
  references.
- **Official repository:** https://github.com/imatge-upc/slt_how2sign_wicv2023
  (MIT), data/weights at the Dataverse DOI above.
- **License:** code MIT; data+weights **CC BY-NC-ND 4.0** — non-commercial,
  no derivatives, same restrictive class already flagged for OpenASL. Any
  future redistribution of a fine-tuned/derived checkpoint would need this
  checked with whoever owns that decision, same as already flagged for
  How2Sign's own video license.
- **Pretrained checkpoint publicly available today:** confirmed via direct
  Dataverse API query — `restricted: false` on every file, including all
  checkpoint variants.
- **Checkpoint actually opened/verified:** the checkpoint's *existence,
  size, and non-restricted status* were confirmed via the Dataverse REST
  API (`/api/datasets/:persistentId/versions/:latest/files`); the file's
  *contents* (state-dict structure) were **not** downloaded or opened in
  this pass, per "do not download large model assets yet."
- **Checkpoint trained on:** How2Sign (confirmed — this is the paper's only
  dataset).
- **Inference without training:** yes — `task generate` runs the trained
  model in eval mode; the README's "Evaluation" section, unlike its
  "Training" section, does not state a GPU is required.
- **Official inference/evaluation command:**
  ```
  task generate   # after setting EXPERIMENT, CKPT, SUBSET, SPM_MODEL in .env
  python scripts/analyze_fairseq_generate.py --generates-dir ... --vocab-dir ... \
      --experiment baseline_6_3_dp03_wd --partition test --checkpoint checkpoint_best
  ```
- **Raw MP4 accepted:** no — the model consumes pre-extracted I3D features
  (`.npy` per clip), same two-stage pattern as every other candidate in this
  research.
- **Feature extractor publicly available:** the I3D extraction pipeline is
  credited to prior work (https://imatge-upc.github.io/sl_retrieval/); not
  independently re-verified as downloadable/runnable in this pass (not
  needed if `test.zip` already covers our 19 clips — see §5).
- **Can arbitrary/new MP4s be processed:** only after independently
  reproducing that I3D extraction pipeline — not attempted here.
- **Can our fixed 19 How2Sign TEST clips be used:** see §5 — very likely,
  not yet confirmed at the individual-clip-ID level.
- **Linux/NVIDIA requirement:** the *documented* conda `environment.yml`
  pins `cudatoolkit=11.5.1` — a package with **no macOS build** — so the
  environment cannot be created exactly as specified on this Mac. The
  **Evaluation** step itself (unlike Training) is not documented as
  GPU-only, so a disclosed, untested deviation (skip `cudatoolkit`, install
  a CPU-only `torch==1.11.0` or a compatible CPU build) is the realistic
  path to trying this on the current machine.
- **Approximate setup complexity:** lower than every other candidate in this
  search — one conda env, standard Fairseq, a `Taskfile`-driven CLI, no
  from-source CUDA builds, no forked libraries, no multi-billion-parameter
  LLM download.
- **Blocking issue:** none that requires training; two disclosed,
  addressable items remain (macOS/CUDA environment substitution; per-clip-ID
  confirmation in `test.zip`) — both are the natural next steps if you want
  to proceed (§6).

---

## 5. Does the released checkpoint depend on features that block using our own 19 clips?

**Not in the way that would block us — but not yet 100% confirmed either.**
The released `test.zip` is explicitly the **official How2Sign test split's**
I3D features (matching the README's own directory example, which shows
per-clip `.npy` files named exactly like `-fZc293MpJk_0-1-rgb_front.npy` —
**the same `VIDEO_ID` prefix, `-fZc293MpJk`, as one of our own 19 selected
clips**, `-fZc293MpJk_2-1-rgb_front`). Since this archive exists specifically
so the paper's own reported test-set BLEU/rBLEU could be computed, it almost
certainly contains features for the *entire* official test split — which
would include all 19 of our clips, since they were themselves drawn from
that same official test split (`HOW2SIGN_MINI_BENCHMARK.md`).

**What is not yet confirmed:** the exact list of `SENTENCE_NAME` IDs inside
`test.zip` has not been enumerated, because doing so means downloading the
546MB archive and listing it (`unzip -l`) — a real download, which this
task's instructions say not to do yet. This is the one concrete fact-check
standing between "very likely" and "confirmed."

---

## 6. Fallback options compared (per your framing)

**A. SpaMo Phoenix14T reproduction** — proves the OSS SLT pipeline is
reproducible (real value: builds confidence in *our* ability to stand up
one of these systems at all), but does **not** measure ASL performance,
since Phoenix14T is German Sign Language. Cheapest to attempt of the
LLM-based candidates, but answers a different question than "how good is
open-source ASL translation."

**B. Train/fine-tune SpaMo (or another model) on How2Sign** — real work,
not executed here. Rough shape: write a custom How2Sign dataset loader
(mirroring `dataset/p14t.py`), extract CLIP-ViT-L + VideoMAE-L features over
How2Sign's ~35K train+val+test clips (a real compute cost, unlike our
19-clip subset), then run the LoRA fine-tune the paper describes ("40
epochs... single NVIDIA A100 GPU... 24 hours" for Phoenix14T's much smaller
8,257-sample corpus — How2Sign's ~35K samples would scale that materially,
plausibly multiple A100-days). This is the only path to a *real* SpaMo
How2Sign number, and it is training, out of scope right now.

**C. General video-VLM ASL baseline** (native video input rather than
sparse still frames) — genuinely worth flagging as a **cheaper, different
experiment**, not evaluated in depth in this pass: modern video-native VLMs
(e.g. Gemini's own video understanding, or open video-LLMs like
Qwen2-VL/InternVideo2 with dense frame sampling) sidestep the still-frame
sparse-sampling failure mode this project's own frame-inspector already
diagnosed on Curify's model (fingerspelling smear, 1-frame-cue fabrication,
`CONTAMINATION.md`/`asl-1252-frame-inspector.html`). This is a **promising
direction to scope as its own follow-up research pass**, not something this
session verified against primary sources — flagging it rather than
recommending it outright.

**D. Commercial ASL recognition API** — research only, no calls made or
suggested here. You already have a real, confirmed comparison point for this
class of tool: SignCaption/Sign-Speak, already used in this project's own
internal corpus work (`ground_truth_candidates/signcaption/`). Any
additional commercial API would need the same treatment: verify it's
ASL-specific and continuous (not isolated-sign), and treat its output the
same way SignCaption's is already treated — external-tool candidate
reference, never gold.

---

## 7. Recommendation — smallest experiment that directly answers "open-source baseline approach"

**Fetch the OpenSLT checkpoint (127MB) + released test I3D features
(546MB), confirm our 19 clip IDs are present in `test.zip`, and run the
documented `task generate` + `analyze_fairseq_generate.py` evaluation on
just those 19 — using a disclosed CPU-only environment substitution for the
non-macOS-buildable `cudatoolkit` pin.** This is the only path in this
entire search that produces a real, ASL-native, non-training BLEU/rBLEU
number on our own fixed clips, at ~673MB total download (checkpoint + test
features + vocab) — two to three orders of magnitude smaller than any
LLM-decoder candidate's footprint, and with no training step anywhere in the
path.

---

## 8. Explicit next-action recommendation

**Do not** provision a GPU for SpaMo yet, and **do not** pursue SpaMo/SSVP-SLT/
VTaMo further as the "first pretrained ASL baseline" — none of them can
produce one without training.

**The next action should be: run the OpenSLT/How2Sign-official pretrained
model** — specifically, as the very first, smallest, still-paused-for-your-
approval step: download only `test.zip` (546MB) and `unzip -l` it (list
contents, don't extract) to settle §5's one open question — whether our 19
clip IDs are actually inside it — **before** committing to the checkpoint
download or any environment setup. That single check is the cheapest
possible next fact-check and determines whether "run the released model on
our 19 clips with zero feature extraction" is really as immediate as this
research suggests.

Testing a native-video VLM baseline (option C) is a reasonable **second**
track to scope later, but shouldn't happen before this session's own
finding — a real runnable ASL baseline that already exists — is followed
through.
