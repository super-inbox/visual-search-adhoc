# P0-1 Stage A: blind reviewer package and HandReader_RGB feasibility

**Status:** preparation only, 2026-10-29.
- No Stage A evaluation, no CER or word accuracy.
- No OpenFS or HandReader run on any Stage A item.
- No external model API, no production change.

Follows [`P0_1_STAGE_A_PREPARATION.md`](P0_1_STAGE_A_PREPARATION.md).

## Bottom line

- **A. Blind reviewer package: built and verified.**
  - 36 blind items, `FSA-001` to `FSA-036`.
  - The reviewer gets 4 text files plus 36 clips.
  - An automated leakage scan found 0 hits.
  - The review page was browser-tested: dummy labels, export, re-import, byte-identical round trip, then cleared.
  - Every clip fully decodes.
- **B. HandReader_RGB: technically viable for Stage A.** Upstream @ `77d390d0` (code licence Apache-2.0), checkpoint
  `chicago+/rgb/best.pt` sha256 `fa92e90d…` (trained on ChicagoFSWild+; its own terms apply).
  - Weights load strictly: 241 tensors, 0 missing, 0 unexpected.
  - A CPU forward pass on a synthetic input works and is deterministic. Both upstream decoders run.
  - Two runtime-only portability patches were needed; no upstream file and no model logic changed.
  - **Main caveat:** upstream ships no hand-crop code, so Stage A crops (MediaPipe) differ from the training crops.
- **Decoder frozen:** CTC beam search (beam 5, no language model) is primary; greedy is a secondary diagnostic only.
- **No Stage A accuracy claim exists.** No recognizer (OpenFS or HandReader) was run on any of the 36 blind items.
- **Final positive / negative / uncertain labels** come only from the blind human review.

## A. Blind reviewer package (Step 1)

**Builder:**
[`p0-1-stage-a-reviewer-package/build_stage_a_package.py`](p0-1-stage-a-reviewer-package/build_stage_a_package.py).
It reads the frozen candidate set only for the blind-ID → clip mapping.

| Folder | Contents | In git? |
|---|---|---|
| `package_local/send_step1_blind/` (**send this**, or `send_step1_blind.zip`) | `reviewer_instructions.md`, `blind_review.csv`, `review_blind.html`, `clips/FSA-001.mp4` … `FSA-036.mp4`, `SHA256SUMS` (42 MB) | no (local exclude, as for the 10-23 package) |
| `package_local/internal/` (team only) | `blind_mapping.csv` (blind ID → clip, source video, hashes, selection tier), `build_log.json`, `leakage_check.json` | no |
| report folder | builder plus copies of the three reviewer-facing text files | yes (no clips) |

No Step 2 (reference-conditioned) material was created.

**Clips:**
- Stream-copied from the frozen How2Sign v2 videos, each sha256-checked against `FREEZE_CHECKSUMS`.
- The video stream only. Audio (`-an`) and all container metadata are removed, and the files are renamed to the blind
  ID.
- `+faststart` is applied, so the index is at the front and the clip opens immediately.
- Every clip was fully decoded: 6,661 frames in total, equal to the source packet count per clip. All are H.264 High,
  yuv420p.

**Reviewer task and fields** (frozen schema, one row per span):
- `fingerspelling_present`: yes / no / uncertain.
- If yes, per span:
  - start and end (clip seconds);
  - letters (a–z as signed, `?` for an unreadable letter);
  - confidence;
  - signing hand;
  - visibility and occlusion issues.
- **More spans:** a second span is added with "+ span".
- **If no:** letters stay blank.
- **If uncertain:** the reason goes in `notes`.

**What the reviewer sees:** blind ID, clip and duration, neutral instructions, annotation fields.

**Leakage check** (`internal/leakage_check.json`, automated over every file in the send folder, including the MP4
tags):

| Check | Scope | Hits |
|---|---|---|
| Clip and source-video IDs | 260 How2Sign v2 identifiers | 0 |
| Reference text | 659 four-word sequences from the 36 references (read for this check only) | 0 |
| Tier and model words | positive / negative / random / tier / likely / screen / candidate / OpenFS / HandReader / Uni-Sign / Gemini / OpenAI / reference / How2Sign | 0 |

The page and CSV contain no reference sentence, name, expected letters, model output, selection tier or screen
window.

**Browser test** (Chrome, page served on localhost):
1. The page opened and rendered 36 cards.
2. Dummy labels went in through the real UI: typed reviewer ID, typed letters, and the "+ span" button. The other
   fields were set through DOM input/change events. Cases covered: a 2-span item, `no`, `uncertain`, and notes
   containing a comma, quotes and a newline.
3. **Export:** the real button produced `blind_review.csv`.
4. **Round trip:** export → clear → import → export was **byte-identical**.
5. **Parsing:** Python's `csv` module and the Stage A scorer (`load_labels`) read the exported rows correctly. The
   header equals the frozen `label_fields`.
6. **Cleanup:** all dummy labels were removed, local storage was cleared, and after reload 0 fields were filled.

**Not verified in the browser:** in-browser video playback. The automation tab was hidden and Chrome defers media
loading there. Decodability was verified with a full ffmpeg decode instead.

**Uni-Sign control subgroup rule (frozen in the pre-registration):**
- The 36-item selection does not use Uni-Sign output.
- After blind labels return, an "already-correct Uni-Sign control" subgroup may be defined by comparing the human
  letters with the saved Uni-Sign A_official output.
- It is analysis-only, after labelling, and cannot affect which 36 items were selected.

## B. HandReader_RGB feasibility (technical only)

**Record:** [`results/p0_1_handreader_rgb_feasibility.json`](../../experiments/p0-2026-10-29/results/p0_1_handreader_rgb_feasibility.json).
**Runner:** [`p0_1_handreader_feasibility.py`](../../experiments/p0-2026-10-29/p0_1_handreader_feasibility.py).

| Item | Frozen value |
|---|---|
| Repo | `https://github.com/ai-forever/HandReader` @ `77d390d0650a63b917087b78ab36e1eeb4e0ae3b` (2 commits; last 2026-10-18) |
| Paper | arXiv 2505.10267 |
| Licence | **Code:** Apache-2.0 (LICENSE sha256 `c71d239d…`). **Checkpoint:** trained on ChicagoFSWild+. Using the checkpoint and its training data remains subject to the relevant dataset and checkpoint terms; it is not necessarily covered by the code's Apache-2.0 licence |
| Checkpoint | `HandReader_ChicagoFSWild+.zip` (README link; sha256 `f66a5c77…`, 451.6 MB) → `chicago+/rgb/best.pt`, sha256 `fa92e90db23a467c59d47e718f07233b94d73c1bff8dfdf3a2248ed4f3c9ad0a` (217.8 MB). Not committed |
| Variant | RGB only: `TSM_Resnet` (ResNet-34, unidirectional temporal shift) + 2-layer BiGRU head (1024). `configs/rgb_chicago.yaml` (sha256 `3ccc1c1b…`). 54.4 M parameters |
| Alphabet | `_ &'.@abcdefghijklmnopqrstuvwxyz`: CTC blank `_` at index 0, 32 classes |
| Input | per-frame RGB **hand crops**. Eval transform: Normalize (ImageNet mean/std) **then** Resize 224×224, ToTensorV2. Frames are concatenated over clips, with per-clip lengths (TSAM). No temporal resampling |
| Crop source | **not in the repo.** Per the paper, training crops came from the Shi et al. 2019 hand localizer. Stage A must use the frozen MediaPipe crop pipeline: a crop-source shift |
| Decoding | **frozen** (see below): upstream CTC `beam_decode`, beam 5, no language model = **primary**. Upstream `greedy_decode` = secondary diagnostic only |

**Decoder freeze (Stage A):**
- **Primary:** CTC beam search, beam size 5, no language model and no lexicon. Upstream `beam_decode` with
  `scorer=None`, so `lm_beta` and `ins_gamma` have no effect.
- **Secondary:** upstream `greedy_decode`, recorded as a diagnostic only. It never feeds a metric or gate.
- **Why:** the upstream greedy decoder can collapse a legitimate repeated letter. Once 2 or more characters have
  been emitted, it skips any letter equal to the previous emitted letter, even across a CTC blank, so a real double
  letter such as "ll" can be lost. Beam decoding has no such rule.
- **Not claimed:** that beam decoding is more accurate on our data. That is untested.
- This decoder choice was frozen before any Stage A evaluation output was produced and therefore was not selected based on benchmark accuracy.

**Environment:**
- An isolated venv in the session scratch directory: Python 3.11.7 x86_64 under Rosetta, the same platform as the
  OpenFS runs.
- torch 2.0.1 and torchvision 0.15.2 (CPU wheels), numpy 1.26.3, albumentations 1.4.8, Hydra 1.3.2. `pip check` is
  clean.

Install deviations from the repo pins:
- **opencv 4.9.0.80 instead of 4.10.0.82:** there is no x86_64 wheel.
- **CPU torch wheel** instead of the cu118 index.
- **Only the inference-path packages** were installed.
- **antlr4 4.9.3** came from its pure-Python source package.

The production and curify-studio dependencies are untouched.

**Feasibility checks:**

| # | Check | Result |
|---|---|---|
| 1 | clone / read the repo | PASS; clone unmodified (`git status` clean) |
| 2 | checkpoint obtained and hashed | PASS |
| 3 | weights load | PASS: `load_state_dict(strict=True)`, 241 tensors, 0 missing, 0 unexpected |
| 4 | exact RGB variant | PASS: built from the upstream `rgb_chicago.yaml` via Hydra |
| 5 | alphabet / blank / CTC | PASS: as above |
| 6 | preprocessing documented | PASS, apart from the missing crop code |
| 7 | CPU inference | PASS after runtime patch P2 |
| 8 | synthetic input accepted | PASS: 24 synthetic 224×224 frames (white canvas, moving rectangle, disc). No benchmark, reviewer or real-world content |
| 9 | output shape and decoding | input `[24, 3, 224, 224]`, lengths `[24]` → logits `[1, 24, 32]`, all finite. Two runs identical. Greedy and beam both decode. CPU forward about 3.6–3.7 s for 24 frames |

The decoded strings are not recorded: the input is synthetic and meaningless.

**Portability patches** (runtime only, no upstream file edited, no change to model logic or weights):
- **P1:** `make_resnet` calls `resnet34(pretrained=True)`, which would download ImageNet weights at construction. The
  model is constructed without them, since the strict checkpoint load overwrites every tensor anyway.
- **P2:** `src/models/modules/tsm_resnet.py:452` hard-codes `.cuda()` on a zero padding buffer. This is the only CUDA
  call on the RGB path. `Tensor.cuda()` is made a no-op when CUDA is absent.

**Verdict:** technically viable for Stage A. The released checkpoint loads and runs on CPU deterministically with
documented, logic-free patches. Accuracy on How2Sign is unknown and was not measured.

**Not done (by instruction):** no comparison with OpenFS, no run on any Stage A or benchmark clip, no MiCT-RANet
(the fallback stays untested).

## Remaining blockers before the real Stage A

1. **Send** `send_step1_blind/` (or the zip) to the ASL-fluent reviewer, and get the blind Step 1 labels back.
2. **Gate G0** on the returned labels: at least 12 positive spans and at least 8 negatives. Otherwise use the
   pre-declared expansion order.
3. **Approval to run** both recognizers (OpenFS keypoint, HandReader_RGB) on the confirmed spans and negative probe
   windows, through the frozen span/crop pipeline. The MediaPipe crop pass has not been run on any item yet.
4. The decoder is already frozen (beam 5, no language model; greedy secondary). Any change has to happen before the
   first Stage A output exists.

## Files

- `asl-translator/daily_report/2026-10-29/P0_1_STAGE_A_REVIEWER_PACKAGE_AND_RGB_FEASIBILITY.md` (this report)
- `asl-translator/daily_report/2026-10-29/p0-1-stage-a-reviewer-package/`:
  - `build_stage_a_package.py`
  - `reviewer_instructions.md`, `blind_review.csv`, `review_blind.html` (copies of the reviewer-facing files)
  - `package_local/` (local only, git-excluded): clips, send folder, zip, internal mapping
- `asl-translator/experiments/p0-2026-10-29/p0_1_handreader_feasibility.py`
- `asl-translator/experiments/p0-2026-10-29/results/p0_1_handreader_rgb_feasibility.json`
- Updated:
  - `p0_1_stage_a_prepare.py` and the regenerated `p0_1_stage_a_preregistration.json`: the HandReader repo, commit,
    checkpoint, alphabet, preprocessing and decoding are frozen, and the control-subgroup rule is stated.
  - The candidate set and label template regenerated byte-identically.
