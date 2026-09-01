# OpenSLT reproduction plan — bounded checkpoint milestone, 2026-08-31

> **UPDATE, same day — environment built, checkpoint loaded, ONE clip run
> successfully.** The milestone below (assets/repo/feasibility, nothing
> installed) was completed first; a follow-up authorization then asked for
> an isolated macOS/arm64 CPU environment and exactly one inference. Both
> succeeded. Full account: **§11 below**. Result detail:
> `results/OPENSLT_ONE_CLIP_RESULT.md`. Per instructions, this stopped after
> one clip — the remaining 18 were **not** run.
>
> **UPDATE 2, same day — all 19 clips run.** A further authorization asked
> for the full frozen benchmark. **18/19 produced predictions**; 1 clip
> (`G33aqW3DLpc_1-10-rgb_front`, 30.67s, longest in the set) was excluded by
> the official checkpoint's own `max_source_positions=1024` limit — not
> worked around, per instructions. Corpus WER 1.16, corpus sacreBLEU 0.96
> (cross-checked against the paper's own `analyze_fairseq_generate.py`:
> 0.93) — translation quality is very poor on this benchmark, a real,
> reproducible baseline number. Full account:
> `results/OPENSLT_19CLIP_RESULTS.md` + `.csv` + `raw_generation_19.txt`.

**Status (original milestone): assets obtained and verified, environment inspected, nothing installed,
no inference run.** This session executed the six bounded steps authorized by
the manager: download+checksum the checkpoint, obtain small vocab/config/test
metadata, clone+pin the official repo, read the generation code path, assess
CPU/Apple-Silicon feasibility, and write this plan. **Stopped exactly where
instructed** — before creating any Python environment and before running
`fairseq-generate`.

Builds directly on `docs/daily_report/8.30/asl-open-source-baseline/ASL_PRETRAINED_BASELINE_SEARCH.md`
and `OPENSLT_HOW2SIGN_COMPATIBILITY.md`, which established OpenSLT as the P0
candidate and confirmed our 19 How2Sign clips are covered by the released test
I3D features. This document picks up from there.

---

## 1. Checkpoint verification

| Field | Value |
|---|---|
| File | `final_models/baseline_6_3_dp03_wd/ckpts/checkpoint.best_reduced_sacrebleu_3.5401.pt` |
| Source | CORA/Dataverse, DOI `10.34810/DATA693`, Dataverse file ID `51903` |
| Direct access URL | `https://dataverse.csuc.cat/api/access/datafile/51903` |
| Reported size (API) | 126,827,063 bytes |
| Actual downloaded size | 126,827,063 bytes — **exact match** |
| Reported MD5 (API) | `52f2f55dca970d82c7ffe534fbfdec43` |
| Actual MD5 (computed locally) | `52f2f55dca970d82c7ffe534fbfdec43` — **exact match** |
| Local path | `asl-translator/data/public_benchmarks/how2sign/openslt_checkpoint/checkpoint.best_reduced_sacrebleu_3.5401.pt` |

**Verdict: checkpoint verification PASSED.** Obtained via the Dataverse REST
API (`/api/datasets/:persistentId/versions/:latest/files`), which lists all 32
files in the dataset with per-file MD5s — not trusted from the README. This is
the same checkpoint file `OPENSLT_HOW2SIGN_COMPATIBILITY.md` and
`ASL_PRETRAINED_BASELINE_SEARCH.md` already identified as the paper's
best-performing How2Sign model.

---

## 2. Small metadata assets — obtained and verified

| File | Dataverse ID | Reported size/MD5 | Actual | Local path |
|---|---|---|---|---|
| `cvpr23.train.how2sign.unigram7000_lowercased.model` (SentencePiece model) | 53219 | 359,877 B / `760fc506...` | exact match | `openslt_checkpoint/vocab/` |
| `cvpr23.train.how2sign.unigram7000_lowercased.txt` (dict) | 53220 | 80,103 B / `f8c52732...` | exact match | `openslt_checkpoint/vocab/` |
| `cvpr23.train.how2sign.unigram7000_lowercased.vocab` | 53221 | 128,497 B / `f0d9efb3...` | exact match | `openslt_checkpoint/vocab/` |
| `cvpr23.fairseq.i3d.test.how2sign.tab` (official test manifest) | 53222 | see §2a below — **required a re-download** | resolved, exact match | `openslt_checkpoint/cvpr23.fairseq.i3d.test.how2sign.tab` |
| `Readme.txt` (dataset's own README) | 53890 | 11,823 B / `cc96e92f...` | exact match | `openslt_checkpoint/upstream_Readme.txt` |

**Deliberately not fetched:** `train.zip` (7.78GB), `val.zip` (435MB),
`cvpr23.fairseq.i3d.train.how2sign.tab`, `cvpr23.fairseq.i3d.val.how2sign.tab`,
every `hydra_train.log`, and every checkpoint variant other than the one above
— all are training/validation assets or unneeded artifacts, out of scope per
"no train/val data."

### 2a. A checksum mismatch, found and resolved — not glossed over

The first download of the test manifest **did not match its reported
checksum**: API said 577,471 bytes / MD5 `18a84b0ab5df1e71418ecb491fa10edf`;
the plain `/api/access/datafile/53222` download came back as 577,586 bytes /
MD5 `df4ddba138c5d6b9d7c71291de611640`. This was not waved through — the
mismatched file was renamed (`...tab.INGESTED_MISMATCH`, kept in scratchpad
as evidence, not copied into the repo) and investigated before use.

**Cause: Dataverse's own tabular-ingestion re-formatting.** Dataverse
auto-"ingests" uploaded `.tab`/`.tsv`/`.csv`-shaped files into its own
normalized internal representation for browsing, and serves *that* version by
default from the plain access URL — not the byte-identical original the
checksum was computed against. Re-downloading with `?format=original`
(`https://dataverse.csuc.cat/api/access/datafile/53222?format=original`)
returned a file whose MD5 matched the API's reported checksum **exactly**.
(The API's own `filesize` field is still off by ~28KB from either actual
download in either format — a metadata inconsistency on Dataverse's side, not
ours; the MD5 match is what actually verifies content, and it is exact.)

**Why this mattered, not just as a formality:** the un-ingested and
Dataverse-ingested versions of a `.tab` file are not guaranteed to be
byte-for-byte semantically identical (re-quoting, whitespace, or delimiter
normalization can differ) — this project has already been burned once by
treating "the file that loaded without error" as equivalent to "the correct
file" (`CONTAMINATION.md`). The corrected, checksum-verified file was
content-checked directly (§3 below), not just re-hashed.

---

## 3. Manifest content-verification (beyond the compatibility doc's frame-count check)

The checksum-verified `cvpr23.fairseq.i3d.test.how2sign.tab` was parsed
directly (stdlib `csv`, tab-delimited): **2,328 data rows**, 11 columns —
`id, signs_file, signs_offset, signs_length, signs_type, signs_lang,
translation, translation_lang, glosses, topic, signer_id`.

- **All 19 of our clip IDs are present** (exact string match on `id`),
  confirming and *strengthening* `OPENSLT_HOW2SIGN_COMPATIBILITY.md`'s
  "strongly consistent, not yet fully proven" finding from frame-count
  scaling alone.
- **Direct text match, not just presence:** row `-fZc293MpJk_2-1-rgb_front`'s
  `translation` field reads *"The aileron is the control surface in the wing
  that is controlled by lateral movement right and left of the stick."* —
  **word-for-word identical** to our own `manifest.csv`'s reference text for
  that clip. This settles OPENSLT_HOW2SIGN_COMPATIBILITY.md's open question:
  the released manifest's segmentation/alignment **is** the same one our
  19-clip benchmark was drawn from, confirmed at the text level, not inferred.
- **`signs_file` values are absolute paths from the original authors'
  cluster** (e.g. `/home/usuaris/imatge/ltarres/wicv2023/how2sign/i3d_features/test/-fZc293MpJk_2-1-rgb_front.npy`)
  — exactly the caveat the repo's own README states ("you might need to
  manually change the path of the `signs_file` column"). This is a real,
  concrete, still-open blocker, sized precisely in §6 below.
- **`signs_offset`/`signs_length` carry real per-clip cropping values** (e.g.
  offset 181, length 327 for `-fZc293MpJk_2-1-rgb_front`) — the loader does
  not simply consume a whole `.npy` file; it slices it. This means the fix in
  §6 is a **path rewrite of 19 existing official rows**, not a
  re-derivation of offsets/lengths — lower risk than it first appeared.

**19-clip benchmark selection: read only, not touched.** No row was added,
removed, or reordered in `asl-translator/data/public_benchmarks/how2sign/manifest.csv`.

---

## 4. Repository: cloned and pinned

| Field | Value |
|---|---|
| Repo | `https://github.com/imatge-upc/slt_how2sign_wicv2023` |
| License | MIT (Facebook, Inc. — this repo is a fork of the full `fairseq` codebase) |
| Pinned commit | `3260d05f4804d3611a911adf3fab8cc50d8204cd` (latest on default branch as of this session) |
| Clone location | scratch, outside this repo (`<scratchpad>/openslt_repo`) — **not** inside `visual-search-adhoc` |
| Clone size | 56MB working tree + 34MB `.git` |

The actual How2Sign-specific code is not at the repo root — it lives under
`examples/sign_language/` (config, `Taskfile.yml`, `datasets/how2sign.py`,
`scripts/`), with the model/task/data classes registered into the vendored
`fairseq/` tree (`fairseq/tasks/sign_to_text.py`,
`fairseq/data/sign_language/`).

---

## 5. Exact runtime dependencies

From `examples/sign_language/environment.yml` (conda), read directly, not
summarized from the README:

```
python=3.8            pandas=1.4.3          fairscale=0.4.3
pip=22.2               pandarallel=1.6.1     sentencepiece=0.1.96
numpy=1.22.4           cudatoolkit=11.5.1    curl / axel / tar / pigz / pv / parallel
pytorch=1.11.0          torchvision=0.12.0    conda-forge::imageio(-ffmpeg)
torchaudio=0.11.0       opencv=4.6.0          conda-forge::sacremoses=0.0.53
pysoundfile=0.10.2      h5py=3.7.0            wandb / tensorboardx / jupyterlab
sacrebleu=2.3.1         srt=3.5.2

pip: mediapipe==0.8.10.1, pose-format==0.1.0, vidgear==0.2.6, truecase==0.0.14
```

**Per-package Apple Silicon (osx-arm64) check, done today, not assumed:**

| Package | Finding |
|---|---|
| `python=3.8` | conda-forge and Anaconda's `pkgs/main` both ship osx-arm64 builds — confirmed via `conda search`. |
| `pytorch=1.11.0` | PyPI ships an official `macosx_11_0_arm64` wheel for cp38/cp39/cp310 — confirmed by inspecting the PyPI file listing directly. **No cp311 arm64 wheel exists for this exact version** — this machine's default `python3` is 3.11.7, so a **3.8/3.9/3.10 interpreter is mandatory**, not optional. This is a CPU-only wheel on macOS regardless (Apple never ships CUDA wheels), so no CUDA substitution is even needed here — it's moot on this platform. |
| `cudatoolkit=11.5.1` | Confirmed **zero** osx-arm64 (or any macOS) build on conda-forge — matches prior research. Must be **omitted entirely** from the env, not substituted; nothing on macOS needs it since PyTorch's own macOS wheels never link CUDA. |
| `sentencepiece=0.1.96` | **No arm64 wheel on PyPI** (only `macosx_10_6_x86_64` for cp35–cp39) — but **conda-forge does ship osx-arm64 builds** (py38/py39/py310). This is exactly why the upstream authors used conda for this dependency rather than pip; the documented conda path is not optional here, it is load-bearing. |
| `fairscale=0.4.3` | **No wheel of any kind on PyPI — sdist only** (`fairscale-0.4.3.tar.gz`), and **not present on conda-forge at all** for this exact pin. This is a genuine, disclosed, untested gap: installing it on this Mac means building from source via pip (`pip install fairscale==0.4.3`), which is plausible (fairscale's core ops are pure PyTorch; CUDA kernels are optional extensions that should degrade gracefully on a CPU-only build) but **not verified in this session** — flagged as a real risk item, not glossed over. |
| `mediapipe==0.8.10.1` | Not required for our path — see §7 below; the module that would need it lazily imports it only when `feats_type == mediapipe`, which our i3d-only path never hits. |
| `pose-format==0.1.0` | **Is** required — `fairseq/data/sign_language/sign_features_dataset.py` does `from pose_format import Pose` as a hard, unconditional top-level import. Even though our path never constructs a `Pose` object, the import must succeed at module load time. Not checked for arm64 wheel availability this session — flagged as an open item for the next pass. |
| `vidgear` | Not imported anywhere in `fairseq/` or `fairseq_cli/` — confirmed by grep. Extraction-script-only; not required for our generate-only path. |

**Net assessment:** the documented recipe is `conda env create -f
environment.yml` (not pip alone) specifically *because* several pins
(sentencepiece, fairscale) don't have arm64 PyPI wheels — conda is the right
tool here, not a workaround. One real, disclosed, unresolved risk remains:
`fairscale==0.4.3` has no prebuilt binary anywhere and would need to build
from source on this Mac, untested.

---

## 6. The generation code path — exact command and CPU support

`task generate` (`examples/sign_language/Taskfile.yml`, `generate:` target)
resolves to:

```bash
fairseq-generate {{.I3D_DIR}} \
  --path {{.CKPT_FILE}} \
  --task sign_to_text \
  --gen-subset {{.SUBSET}} \
  --seed 48151623 \
  --batch-size 32 \
  --scoring sacrebleu \
  --max-source-positions {{.MAX_SOURCE_POSITIONS}} \
  --max-target-positions {{.MAX_TARGET_POSITIONS}} \
  --max-tokens 16000 \
  --beam 5 \
  --sacrebleu --sacrebleu-tokenizer 13a \
  --bpe sentencepiece --sentencepiece-model {{.SPM_MODEL}} \
  --skip-invalid-size-inputs-valid-test > {{.OUT_FILE}}
```

**CPU path, verified by reading code, not assumed from the README's
silence:**
- `fairseq-generate`'s own CLI exposes a standard `--cpu` flag
  (`fairseq/dataclass/configs.py:146` — `cpu: bool = field(default=False,
  help="use CPU instead of CUDA")`) — this is fairseq's generic,
  well-exercised CPU path, not something OpenSLT would need to special-case.
- **Zero hardcoded `.cuda()` / `torch.cuda` calls** anywhere in
  `fairseq/data/sign_language/` or `fairseq/tasks/sign_to_text.py` — grepped
  directly, not inferred. The How2Sign-specific code does not fight the
  `--cpu` flag.
- The task's own registered model is a Fairseq `TransformerModel` variant
  (seq2seq over I3D features, not a custom architecture with GPU-only ops) —
  consistent with `ASL_PRETRAINED_BASELINE_SEARCH.md`'s framing of this as "a
  classic Fairseq transformer... not a 3B-parameter LLM decoder."
- The README's own **Evaluation** section, unlike **Training**, never says a
  GPU is required — consistent with everything above, now corroborated by
  reading the actual generate command and task code, not just the README's
  silence.

**How `SignToTextTask.load_dataset` resolves data** (read directly,
`fairseq/tasks/sign_to_text.py:211-224`):
```python
root_dir = Path(self.cfg.data)
manifest_file = root_dir / f"{split}.tsv"
```
— i.e. `I3D_DIR/<SUBSET>.tsv` must exist, where `SUBSET` is the
`--gen-subset` value (`cvpr23.fairseq.i3d.test.how2sign` per the README).
**Concrete filename mismatch, not yet fixed:** our verified manifest is named
`cvpr23.fairseq.i3d.test.how2sign.tab` (Dataverse's own extension), but the
loader requires exactly `<subset>.tsv`. This is a same-content rename, zero
semantic risk, not yet performed (would count as environment/data setup,
which this session was told to stop before).

---

## 7. Can this Apple Silicon Mac realistically run ONE inference?

**Yes, with a real, mostly-scoped, partially-untested environment
substitution — not a clean "just works," and not a hard blocker either.**

| Requirement | This Mac | Verdict |
|---|---|---|
| Architecture | `arm64` (confirmed: `uname -m`) | — |
| Python | System default is 3.11.7; **3.8/3.9/3.10 required** for pytorch 1.11.0's arm64 wheel | Not installed yet, but `conda` (Anaconda3, already present at `/opt/anaconda3`) can create one — confirmed via `conda search python=3.8 -c conda-forge --subdir osx-arm64` |
| PyTorch | `pytorch=1.11.0` has an official arm64 macOS wheel for the required Python range | Available, no substitution needed on this axis |
| CUDA | Pinned `cudatoolkit=11.5.1` has no macOS build at all | **Moot, not a blocker** — macOS PyTorch wheels are CPU-only by construction, so there is nothing to substitute; simply omit the line |
| `sentencepiece==0.1.96` | No arm64 PyPI wheel, but conda-forge has one | Solvable via conda, not pip |
| `fairscale==0.4.3` | No wheel anywhere (PyPI sdist-only, absent from conda-forge) | **Real, disclosed, untested risk** — plausible via source build, not verified this session |
| `pose-format==0.1.0` | Hard unconditional import in the data path | Required; arm64 availability not checked this session |
| Disk | 575GB free | No constraint |
| The model itself | Fairseq transformer, `--cpu` flag exists, no hardcoded CUDA in the sign-language-specific code | Should run on CPU; **speed unknown/untested** — this session did not attempt to estimate wall-clock inference time for 19 short clips |

**Bottom line:** nothing found today rules this out. Two real, disclosed gaps
remain before a clean install: `fairscale`'s from-source build is untested on
this platform, and `pose-format`'s arm64 wheel availability wasn't checked.
Neither is a documented hard blocker (unlike SpaMo's `accelerator: gpu` +
`bf16` Lightning config, which **is** a hard blocker on this Mac per
`SPAMO_REPRODUCTION_PLAN.md`) — both are "try it and see" risks, not "known
impossible" ones.

---

## 8. What was explicitly NOT done (per instructions)

- No training, no train/val feature archives downloaded (`train.zip` 7.78GB,
  `val.zip` 435MB — left alone).
- No CUDA installed (moot on this platform anyway — see §7).
- No production code touched (`curify-*` untouched).
- No private Curify video used — everything here is How2Sign public research
  data, kept under `public_benchmarks/`, never touching `../asl_corpus/`.
- **No new Python environment created** — `conda search` (read-only query)
  was used to check package availability; no `conda env create`, no `pip
  install`, no venv.
- **No inference run** — `fairseq-generate` was read as code, never executed.
- Nothing staged with `git add`, nothing committed, nothing pushed — matches
  the existing untracked-by-design convention for `public_benchmarks/how2sign/`.

---

## 9. Answers

**A. Checkpoint verification: PASSED.** Exact byte-size and MD5 match against
the Dataverse API's own reported values (§1).

**B. Complete assets: mostly yes, with one gap disclosed.** Checkpoint ✅,
vocab (model/txt/vocab) ✅, official test manifest ✅ (after resolving the
Dataverse-ingestion checksum trap, §2a), repo pinned ✅. **Not yet done:**
renaming `.tab`→`<subset>.tsv` and rewriting the 19 relevant `signs_file`
paths to point at `asl-translator/data/public_benchmarks/how2sign/openslt_features/`
— a scoped, disclosed, zero-training data-wiring step, deliberately not
performed this session (counts as "setup," which the instructions said to
stop before).

**C. Exact dependency versions:** §5 table above — `python=3.8`,
`pytorch=1.11.0`, `sentencepiece=0.1.96` (conda-forge, not pip),
`fairscale=0.4.3` (untested source build, real risk), plus the full pinned
list from `environment.yml`, each individually checked for arm64
availability today, not assumed.

**D. CPU inference feasibility: plausible, not yet proven.** `--cpu` flag
exists natively in fairseq; zero hardcoded CUDA calls found in the
How2Sign-specific code (§6); README's Evaluation section never claims a GPU
requirement. No wall-clock estimate exists yet — that requires actually
running it, which was out of scope today.

**E. Exact next setup command** (not executed, for your review before
authorizing the next milestone):
```bash
conda env create -f <scratch>/openslt_repo/examples/sign_language/environment.yml
```
— expected to mostly succeed per §5/§7, with `fairscale==0.4.3`'s
from-source build as the one step likely to need hand-holding or a pinned
alternative if it fails.

**F. Estimated path to first English prediction, from here:**
1. `conda env create` (§9E) — new risk surface: `fairscale` build.
2. `pip install --editable .` from the pinned repo root (installs
   `fairseq-generate` and registers `sign_to_text`).
3. Copy `cvpr23.fairseq.i3d.test.how2sign.tab` → `<I3D_DIR>/cvpr23.fairseq.i3d.test.how2sign.tsv`
   (rename only, confirmed safe — §6).
4. Filter that TSV to our 19 rows and rewrite `signs_file` to point at
   `asl-translator/data/public_benchmarks/how2sign/openslt_features/<id>.npy`
   (the files already extracted and verified in
   `OPENSLT_HOW2SIGN_COMPATIBILITY.md`) — `signs_offset`/`signs_length` are
   already correct in the official rows and need no changes (§3).
5. Set `.env` (`EXPERIMENT`, `CKPT=checkpoint.best_reduced_sacrebleu_3.5401.pt`,
   `SUBSET=cvpr23.fairseq.i3d.test.how2sign`,
   `SPM_MODEL=.../cvpr23.train.how2sign.unigram7000_lowercased.model`) and run
   `task generate` with `--cpu` (needs confirming the Taskfile's `generate`
   target accepts a CPU override, or invoking `fairseq-generate` directly
   with the same flags plus `--cpu`).
6. Score with `scripts/analyze_fairseq_generate.py` (BLEU/rBLEU, the paper's
   own metric) and separately with this repo's own
   `asl-eval/evaluate.py` against `public_benchmarks/how2sign/references/*.srt`
   for WER/CER/IoU consistency with every other comparison in this project.

No wall-clock estimate for step 5 is given — untested, and 19 short clips (5.9
minutes of source video total) on CPU-only beam-5 decoding could plausibly
range from a few minutes to significantly longer depending on how the
Fairscale build and CPU thread count land; this should be measured directly
once attempted, not guessed here.

---

## 10. Files added this session (all untracked, none staged)

```
asl-translator/data/public_benchmarks/how2sign/openslt_checkpoint/
├── checkpoint.best_reduced_sacrebleu_3.5401.pt   (126.8MB, MD5-verified)
├── cvpr23.fairseq.i3d.test.how2sign.tab           (549.7KB, MD5-verified, original format)
├── upstream_Readme.txt                            (11.8KB, MD5-verified)
└── vocab/
    ├── cvpr23.train.how2sign.unigram7000_lowercased.model  (359.9KB, MD5-verified)
    ├── cvpr23.train.how2sign.unigram7000_lowercased.txt    (80.1KB, MD5-verified)
    └── cvpr23.train.how2sign.unigram7000_lowercased.vocab  (128.5KB, MD5-verified)
```
Total: 122MB, mirrors the existing untracked-by-design convention already
used for `openslt_features/` (37.79MB) and `videos/` in the same directory.
The pinned repo clone itself (`imatge-upc/slt_how2sign_wicv2023` @
`3260d05f4804d3611a911adf3fab8cc50d8204cd`) lives outside this repository, in
scratch space, per the same convention used for SpaMo in
`SPAMO_REPRODUCTION_PLAN.md` M1.

---

## 11. UPDATE 2026-08-31 (same day) — environment build, checkpoint load, one-clip CPU inference

Authorized as a follow-up to the milestone above. Full success on all four
phases. Nothing committed/pushed/staged; no training; no other 18 clips run;
no private Curify data touched; no Curify production code modified.

### 11.1 Phase 1 — isolated conda environment

**A platform bug was found and fixed before any package installed.** This
machine's base Anaconda install is itself an **x86_64 build running under
Rosetta** (`conda info` reports `platform: osx-64` despite `uname -m` =
`arm64`). The first environment-creation attempt silently solved and
installed **Intel** packages (`pytorch/osx-64::pytorch-1.11.0-py3.8_0`, etc.)
— not what "build an Apple-Silicon environment" means. Caught before
anything beyond the env itself was installed; the env was removed and
recreated with `CONDA_SUBDIR=osx-arm64` / `--platform osx-arm64` forced
explicitly, which produced genuinely native arm64 packages
(`conda-forge/osx-arm64::pytorch-1.11.0-cpu_py38h17550ec_2`, etc.). Every
version claim below is from this corrected, verified-native env.

**Environment name:** `openslt-cpu-arm64`
**Path:** `/opt/anaconda3/envs/openslt-cpu-arm64` (new, isolated conda env — base/system Python untouched, nothing installed globally)

**Classification of `environment.yml`, applied:**

| Class | Packages | Action |
|---|---|---|
| Required runtime | `python`, `numpy`, `pandas`, `sentencepiece`, `sacrebleu`, `h5py`, `pytorch`, `torchvision`, `torchaudio`, `sacremoses` (+ pip: `fairscale`, `pose-format`, `truecase`) | Installed, exact pins where resolvable |
| CUDA/Linux-only | `cudatoolkit=11.5.1` | **Omitted entirely** — no macOS build exists, and moot anyway since macOS PyTorch wheels are CPU-only by construction (§7 of the original milestone) |
| Training-only, not needed for generate | `wandb`, `tensorboardx`, `jupyterlab` | Omitted |
| Extraction-only, not needed (we already have I3D features) | `ffmpeg`, `opencv`, `imageio(-ffmpeg)`, `pysoundfile`, `mediapipe`, `vidgear` | Omitted — confirmed by grep that none are hard-imported in the `sign_to_text`/generate code path (mediapipe is lazily imported only when `feats_type==mediapipe`; vidgear isn't imported anywhere in `fairseq/`) |
| Shell tools (dataset download/extraction), not needed | `curl`/`axel`/`tar`/`pigz`/`pv`/`parallel`/`pandarallel` | Omitted |

### 11.2 Exact dependency deviations from the official environment

**No package was installed at a version other than the one officially
pinned.** Every deviation below is a *tooling/method* deviation, not a
version compromise — each was individually verified before being accepted,
not assumed:

| Package | Official pin | What actually happened | Deviation type |
|---|---|---|---|
| `python` | 3.8 | `3.8.19`, native osx-arm64 (conda-forge) | none (patch version only, upstream never pinned one) |
| `pytorch` | 1.11.0 | `1.11.0.post2` (conda-forge osx-arm64 build; `pytorch` channel had no arm64 build for this exact version) | **channel**, not version — `.post2` is a rebuild suffix, base version identical |
| `torchvision` | 0.12.0 | `0.12.0a0` via conda-forge | **channel**, not version |
| `torchaudio` | 0.11.0 | **not on conda for osx-arm64 at all** — installed via `pip install torchaudio==0.11.0`, which has an official arm64 wheel | **install method** (pip vs. conda), exact version |
| `sacremoses` | 0.0.53 | **not on conda-forge for osx-arm64** — installed via `pip install sacremoses==0.0.53` (sdist, pure-Python, builds cleanly anywhere) | **install method**, exact version |
| `sentencepiece` | 0.1.96 | conda-forge osx-arm64 build (no PyPI arm64 wheel exists — conda was the correct call here, exactly as the original environment.yml already assumed) | none |
| `fairscale` | 0.4.3 | **no wheel anywhere (PyPI sdist-only, absent from conda-forge)** — `pip install fairscale==0.4.3` built from source successfully, no errors | **install method** (source build), exact version |
| `pose-format` | 0.1.0 | pip, exact version, arm64 wheel available | none |
| `truecase` | 0.0.14 | pip, exact version | none |
| `fairseq` itself | pinned commit `3260d05f` | `pip install --editable .` — succeeded, but required two mechanical, non-version fixes (§11.3) | build tooling, not version |
| `pip` (the tool itself, not a project dependency) | n/a | Downgraded from 24.3.1 → 24.0 **inside this env only** | pip 24.1+ rejects `omegaconf==2.0.6`'s old-style metadata (`PyYAML (>=5.1.*)`) as invalid syntax; pip's own error message recommended `pip<24.1`. This unblocked installing `omegaconf`/`hydra-core` at fairseq's own exact required versions — it did not change which package versions were requested. |

**No exact version was unavailable and silently swapped for a newer one.**
The two closest calls (`fairscale`, `torchaudio`) both resolved to the exact
official pin via a different install channel — nothing was upgraded to make
installation succeed.

### 11.3 Two build-tooling gaps found and fixed (disclosed, not version changes)

1. **Missing Cython transpilation step.** `pip install --editable .` failed:
   `ninja: error: '.../fairseq/data/data_utils_fast.cpp' ... missing and no
   known rule to make it`. Root cause: fairseq's `setup.py` lists `.pyx`
   sources directly and relies on the long-deprecated `setup_requires`
   mechanism to auto-cythonize them — modern `setuptools`/pip ignore
   `setup_requires` entirely (a security/reliability change, unrelated to
   macOS or arm64; this would fail identically on Linux with a modern
   toolchain). Fixed by manually running
   `cython --cplus -3 fairseq/data/data_utils_fast.pyx` (and the
   `token_block_utils_fast.pyx` sibling) to produce the missing `.cpp` files
   before retrying the install — no source code was edited, only a build
   artifact that should have been auto-generated was generated by hand.
2. **pip metadata strictness vs. old package metadata** — see the `pip`
   row in §11.2's table above.

After both fixes: `pip install --editable . --no-build-isolation` completed
with **exit code 0**, building all three native extensions
(`fairseq.libbleu`, `fairseq.data.data_utils_fast`,
`fairseq.data.token_block_utils_fast`) successfully on arm64.

### 11.4 Phase 2 — imports and checkpoint load

**Environment:** `openslt-cpu-arm64` · **Python:** 3.8.19 (arm64) · **Torch backend:** CPU only (`torch.cuda.is_available()` → `False`; this specific conda-forge build also has `torch.distributed.is_available()` → `False`, i.e. compiled without distributed support — expected and irrelevant for single-process inference)

| Import | Result |
|---|---|
| `torch` | OK — `1.11.0.post2` |
| `sentencepiece` | OK |
| `fairseq` | OK — `0.12.2` |
| `fairseq.tasks.sign_to_text.SignToTextTask` | OK |
| `fairseq.data.sign_language.sign_features_dataset.SignFeatsDataset` | OK |
| `fairseq.libbleu` (C++ ext) | OK |
| `fairseq.data.data_utils_fast` (Cython ext) | OK |
| `fairseq.data.token_block_utils_fast` (Cython ext) | OK |
| **`import fairscale`** (bare, top-level) | **FAILS**: `ImportError: cannot import name 'ProcessGroup' from 'torch.distributed'` — fairscale's FSDP submodule unconditionally imports a symbol this distributed-less torch build doesn't have |

**This one warning does not block anything we need.** Confirmed by reading
`fairseq/distributed/fully_sharded_data_parallel.py`: every internal fairseq
usage of fairscale is wrapped in `try/except ImportError`, correctly
degrading to `has_FSDP = False`. FSDP is a training-time sharding technique
never invoked by `fairseq-generate` on a single checkpoint. Verified
directly: `from fairseq.distributed.fully_sharded_data_parallel import
has_FSDP` → `False`, and `import fairseq` (the real thing we need) succeeds
cleanly regardless.

**Checkpoint load:** `torch.load(CKPT, map_location='cpu')` —

| Field | Value |
|---|---|
| Result | **Success**, zero warnings |
| Wall time | 0.45s |
| Peak RSS (`/usr/bin/time -l`) | 246,628,352 bytes reported max RSS / **196,642,816 bytes peak memory footprint** — well under 200MB |
| Top-level keys | `args, cfg, model, criterion, optimizer_history, task_state, extra_state, last_optimizer_state` (standard fairseq shape) |
| Model size | 187 tensors, **11,746,819 parameters** total |
| First layer | `encoder.feat_proj.weight`, shape `(256, 1024)` — **the 1024-dim input exactly matches our extracted I3D features' shape**, an independent consistency check that the right checkpoint/feature pairing was used |
| Embedded `task.bpe_sentencepiece_model` | An absolute path from the original author's cluster (`/mnt/gpid08/users/ltarres/...`) — not present here; overridden via `--sentencepiece-model` at generate time (same pattern as `signs_file`, §6/§3) |
| Embedded `generation.beam` | `5` — matches the Taskfile's documented `--beam 5`; used as-is |

### 11.5 Phase 3 — one-clip scratch manifest

**CLIP_ID:** `-g0iPSnQt6w_11-1-rgb_front` — the **first row** of the frozen
`asl-translator/data/public_benchmarks/how2sign/manifest.csv` (row order,
not cherry-picked, per instructions).

Built by filtering the checksum-verified official
`cvpr23.fairseq.i3d.test.how2sign.tab` (§2/§3 above) to this one `id`,
changing **only** the `signs_file` column (from the original author's
cluster path to our local, already-extracted
`openslt_features/-g0iPSnQt6w_11-1-rgb_front.npy`), and renamed to the
loader-required `cvpr23.fairseq.i3d.test.how2sign.tsv`. `signs_offset`
(2005), `signs_length` (100), and `translation` (the reference text) were
carried over **unmodified** from the official row.

**Kept fully outside authoritative benchmark data**, at
`<session scratchpad>/openslt_one_clip_run/i3d_data/` — not in
`manifest.csv`, not in `openslt_checkpoint/`, not committed anywhere.

**One loose end investigated, not a bug:** the official `signs_offset=2005`
looks out-of-bounds against our 100-frame extracted `.npy`. Read
`sign_features_dataset.py.__getitem__`/`postprocess()` directly: for
`feats_type=i3d`, offset/length are stored for dataset-length bookkeeping
only and are **never used to slice the loaded array** (only the
`mediapipe` branch slices by offset/length). Confirmed harmless before
running anything.

### 11.6 Phase 4 — one CPU inference

**Result: SUCCESS.** Full detail, exact command, raw output, and metrics in
`results/OPENSLT_ONE_CLIP_RESULT.md` and `results/raw_generation.txt`.
Summary:

| | |
|---|---|
| CLIP_ID | `-g0iPSnQt6w_11-1-rgb_front` |
| REFERENCE | "what you're going to do is you're going to take both your arms and they're going to come underneath your legs." |
| PREDICTION | "so, what i' be/ to do is i' be/ to from all together pressure the kick." |
| WER | 0.8333 |
| CER | 0.6789 |
| sacreBLEU | 7.67 (fairseq's own `--scoring sacrebleu`, independently cross-checked via the `sacrebleu` package directly — exact match) |
| chrF | 15.97 |
| Temporal IoU | not computed — sentence-level output only, no timestamps, not applicable |
| Runtime | 4 seconds wall-clock (full process) |

**One real code-path bug found and fixed, disclosed:** the exact official
command initially crashed 3 seconds in with
`_pickle.PicklingError: Can't pickle <enum 'Choices'>` inside PyTorch's
DataLoader. Cause: macOS defaults to `spawn`-based multiprocessing (Linux
defaults to `fork`); `spawn` requires pickling the full dataset/config to
hand to worker subprocesses, and one of fairseq's Hydra-generated config
Enums isn't picklable that way. Fixed with `--num-workers 0` (disables
DataLoader subprocess workers entirely) — a data-loading plumbing flag with
**no effect on beam search, sampling, temperature, or any decoding
parameter**. Every other flag matches the Taskfile's documented `generate:`
target verbatim; nothing was tuned against the reference.

### 11.7 Answer to the standing feasibility question

§7/§9 of the original milestone called Apple Silicon feasibility "plausible,
not yet proven," with two disclosed open risks (`fairscale` source build,
`pose-format` arm64 availability) and no wall-clock estimate. Both risks are
now resolved (fairscale built clean; pose-format has an arm64 wheel), and
the wall-clock estimate is now measured, not guessed: **~4 seconds per short
clip (5.27s of video) end-to-end on CPU**, plus a fixed ~0.5s/~200MB
one-time model-load cost. This does not by itself predict the 19-clip
batch's total time (network effects like batching, and longer clips'
sequence lengths, both change per-clip cost) — that measurement is deferred
to the next authorized run.
