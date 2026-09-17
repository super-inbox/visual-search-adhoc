# SpaMo + SSVP-SLT — fresh runnable-feasibility re-check, 2026-09-02

**Scope: feasibility re-check only, not a literature review.** Verified
live against each project's current official GitHub state (API + raw file
fetches, today). No download beyond HTTP HEAD/GET on small text files
(READMEs, LICENSE, configs — no checkpoints, no feature archives). No
training. No environment created. No inference attempted. No PR. Does not
touch `how2sign_v2/`, `pilot_v1`, or `asl_corpus`.

**Bottom line: nothing has changed since 8.30/8.31.** Both repos are at
the exact same commit this project already pinned; neither has released
new code, a new checkpoint, or a new tag/release since then.

---

## 1. SpaMo

| Field | Value | Verified how |
|---|---|---|
| Repo | `https://github.com/eddie-euijun-hwang/SpaMo` | GitHub API |
| Latest commit | `aee7f8b6ea8201b710690adcce6f46260dd11bba` — **identical to the commit already pinned in `SPAMO_REPRODUCTION_PLAN.md` (8.30)** | `GET /repos/.../commits?per_page=1` |
| Last pushed | 2025-07-09 (over a year before this check) | GitHub API `pushed_at` |
| Releases / tags | 0 / 0 | GitHub API |
| Code license | **None** — `license: null` via API, no LICENSE file in the repo | GitHub API `license` field |
| Inference code | Yes — `main.py -c configs/finetune.yaml -e bleu --train False --test True --ckpt ...` | `README.md` fetched live |
| Pretrained checkpoint | **One** checkpoint exists: `spamo.ckpt` (Dropbox link, confirmed alive — HTTP 302 to a real download URL, checked today) | `curl -sIL` on the README's Dropbox link |
| Is that checkpoint usable for ASL→English? | **No.** The repo's `configs/` directory contains exactly one config (`finetune.yaml`); `preprocess/` contains exactly one dataset directory (`Phoenix14T`). The single released checkpoint is trained on **Phoenix-2014T (German Sign Language)**. | `GET /repos/.../contents/configs` and `/contents/preprocess` — both list only Phoenix14T-related entries |
| Does the released checkpoint/path support How2Sign? | **No, despite the README listing How2Sign.** `README.md`'s "Data Preparation" section lists How2Sign as one of three datasets the *paper* validates on, but no How2Sign config, no How2Sign preprocessing annotation files, and no How2Sign checkpoint exist anywhere in the repo — confirmed by directly listing both directories live, not inferring from the README's prose. |
| Required input | Pre-extracted CLIP ViT-L/14 spatial features + VideoMAE-L motion features (`.npy`) — **not raw video** | `scripts/vit_extract_feature.py` / `scripts/mae_extract_feature.py`, README |
| Hardware/runtime | `configs/finetune.yaml`: `accelerator: gpu`, `precision: bf16`, decoder is `google/flan-t5-xl` (3B params) — confirmed live by fetching the raw config file today | `finetune.yaml` fetched live |
| Checkpoint/weight license | Undocumented (no LICENSE file covers the Dropbox-hosted checkpoint either) | same as code license finding |

### Classification: **NOT_RUNNABLE_WRONG_LANGUAGE_OR_TASK**

The only released checkpoint is Phoenix14T (German Sign Language). Per
explicit instruction, a German Sign Language checkpoint is not used as an
ASL benchmark. There is no released How2Sign checkpoint, and none of the
repo's actual code assets (configs, preprocessing) support How2Sign today
— only the README's prose claims it as a validated dataset. Getting a
real ASL number from SpaMo would require fine-tuning from scratch on
How2Sign, which is training and explicitly out of scope.

---

## 2. SSVP-SLT (Meta)

| Field | Value | Verified how |
|---|---|---|
| Repo | `https://github.com/facebookresearch/ssvp_slt` | GitHub API |
| Latest commit | `7ed332b0db35884a36b73019ca29bf0755537def` ("OSS Checkup fixes: add Meta copyright") — **same commit era already noted in `SECOND_BASELINE_CANDIDATES.md`/`OSS_BASELINE_FEASIBILITY.csv` (8.30), still the tip of `main`** | `GET /repos/.../commits?per_page=1` |
| Last pushed | 2026-05-19 | GitHub API `pushed_at` |
| Releases / tags | 0 / 0 | GitHub API |
| Code license | **CC BY-NC 4.0** — LICENSE file fetched and read directly today, confirms prior finding | `raw.githubusercontent.com/.../LICENSE` |
| Inference code availability | Yes, and the **best native How2Sign fit of anything checked in this whole search** — `translation/README.md`'s worked examples use literal `data_dir=/path/to/how2sign` paths and a `slt_t5` config | `translation/README.md` fetched live |
| Pretrained checkpoint | **None, of any kind.** `translation/README.md` line 5 reads *"Once you have obtained a pretrained model..."* (an unfulfilled precondition, not a download link); `/path/to/pretrained/model/checkpoint.pth` is a placeholder path, not a real asset; `pretraining/README.md` contains **zero** checkpoint/download mentions; the main `README.md`'s only download links are the DailyMoth-70h **dataset** (raw/blurred/unblurred video + manifests) — no model weights anywhere in the repo. | Grepped all three READMEs (`main`, `pretraining/`, `translation/`) live for "checkpoint/pretrained/.pt/download" |
| Is any checkpoint usable for ASL→English? | N/A — none exists | as above |
| Does it support How2Sign? | **Yes, in code** (data loading, config, worked CLI examples) — but there is nothing pretrained to run through that code path | as above |
| Required input | Pre-extracted `.pt` feature files + manifest `.tsv` (via a documented feature-extraction stage) — not raw video | `translation/README.md` |
| Hardware/runtime | `INSTALL.md`'s literal first requirement line: **"Linux, CUDA >= 11.7"** — fetched live today, unchanged from prior finding. Documented training hardware: "fp32 training on 32GB V100 GPUs." No inference-only VRAM figure exists. | `INSTALL.md` fetched live |
| Checkpoint/weight license | N/A — no checkpoint released | — |

### Classification: **NOT_RUNNABLE_NO_WEIGHTS**

Zero model checkpoints (backbone or SLT) exist anywhere in the project,
confirmed by direct inspection of every README today, not just the prior
search. The code path is real and How2Sign-native, but every path to a
number requires self-supervised video pretraining from scratch plus
supervised SLT fine-tuning — training, explicitly out of scope. Also not
realistically runnable on this machine even if weights existed (hard
Linux+CUDA requirement, no macOS/CPU path documented or implied anywhere).

---

## 3. What changed since 8.31

**Nothing.** Both repos are at the identical commit already on record:

| Repo | 8.30/8.31 finding | Today |
|---|---|---|
| SpaMo | pinned commit `aee7f8b6` | same commit, last pushed 2025-07-09, no new commits in over a year |
| SSVP-SLT | "pushed 2026-05-19, actively maintained, no version tag pinned" | still `pushed_at: 2026-05-19`, same latest commit, still 0 releases/tags |

No new checkpoint release, no new How2Sign support, no license change, no
new commit for either project. The 8.30/8.31 classifications
(`WRONG_TASK` / `NO_PUBLIC_WEIGHTS` in that day's informal taxonomy) map
directly onto today's formal categories with no revision needed.

## 4. Does either deserve an actual benchmark run?

**No, for both.**

- **SpaMo**: would require fine-tuning on How2Sign first (training,
  out of scope) or running its Phoenix14T checkpoint against ASL video
  and calling that a comparison (explicitly disallowed — a German Sign
  Language checkpoint is not a valid ASL baseline).
- **SSVP-SLT**: would require self-supervised pretraining from scratch
  (training, out of scope) before any inference is even possible. There
  is no released asset to run at all, on any hardware.

Neither meets the bar OpenSLT and Uni-Sign already cleared: a real,
released, ASL/How2Sign-trained (or How2Sign-evaluated) checkpoint,
runnable today without training.

## 5. Exact files created

```
docs/daily_report/9.2/asl-baselines/SPAMO_SSVP_SLT_FEASIBILITY_RECHECK.md   (this file)
```

Nothing else was written — no code, no environment, no downloads beyond
the small text files listed in the "Verified how" columns above.

## 6. git status

See conversation — this doc is the only new untracked file; not yet
staged or committed, per instructions.
