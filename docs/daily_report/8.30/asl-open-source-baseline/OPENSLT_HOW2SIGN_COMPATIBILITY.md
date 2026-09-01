# OpenSLT / How2Sign test-feature compatibility check — 2026-08-30

**Scope: bounded compatibility check only.** No checkpoint downloaded, no
model dependencies installed, no environment created, no inference run, no
training, no private Curify data used, no production code touched. Nothing
committed or pushed.

## Why OpenSLT is now the primary runnable ASL baseline candidate

Per `ASL_PRETRAINED_BASELINE_SEARCH.md` (2026-08-30), every LLM-decoder
candidate researched (SpaMo, SSVP-SLT, VTaMo) turned out to have no
downloadable ASL-trained checkpoint at all — SpaMo's one real checkpoint is
Phoenix14T (German Sign Language, not ASL); SSVP-SLT and VTaMo release no
checkpoint of any kind. The official How2Sign baseline — "Sign Language
Translation from Instructional Videos" (Tarrés et al., CVPR WiCV 2023,
`imatge-upc/slt_how2sign_wicv2023`) — is the one candidate that ships a real,
non-restricted, How2Sign-native checkpoint plus the official test-split
features, confirmed directly via the hosting platform's own API rather than
trusted from a README. This document verifies the second half of that
claim: that the released features actually cover our own fixed 19-clip
subset.

## 1. Download record

| Field | Value |
|---|---|
| Source | CORA/Dataverse, DOI `10.34810/DATA693` (CC BY-NC-ND 4.0) |
| Dataverse file ID | `51538` |
| Direct access URL | `https://dataverse.csuc.cat/api/access/datafile/51538` |
| Reported size (API) | 572,646,623 bytes |
| Reported MD5 (API) | `ce7d020f0b84cab96100e2071ea7b693` |
| Actual downloaded size | 572,646,623 bytes — **exact match** |
| Actual MD5 (computed locally) | `ce7d020f0b84cab96100e2071ea7b693` — **exact match** |
| Local temporary path (transient, deleted after use) | `<scratchpad>/openslt/test.zip` |

Download took considerably longer than the transfer size alone would
suggest — the Dataverse host's bandwidth to this connection was slow and
uneven (roughly 0.1–2 MB/s, varying) rather than failing; it was resumed
once (`curl -C -`) after appearing to stall, and completed with a
byte-for-byte, checksum-verified match to the officially reported file. No
partial or corrupted data was used for anything below.

## 2. Archive contents (listed, not fully extracted)

```
unzip -l test.zip
```
- **2,330 total entries**: `test/` (directory marker), `__MACOSX/._test`
  (macOS zip metadata artifact, harmless), and **2,328 real `.npy` feature
  files** under `test/`.
- This count is consistent with the official How2Sign test split (~2,322
  sentences per the dataset's own documentation) — a handful more files than
  sentences is expected zip-packaging overhead, not a discrepancy worth
  chasing for this check.

## 3. Manifest → archive mapping

Read `asl-translator/data/public_benchmarks/how2sign/manifest.csv` directly
(19 rows, unmodified — **the benchmark selection was not touched** by this
check, per your instruction) and matched each `how2sign_id` against the
archive's `test/<id>.npy` entries by exact string match.

| clip_id | in_our_manifest | feature_found | exact_feature_filename | duplicate_or_ambiguous_match | notes |
|---|---|---|---|---|---|
| `-g0iPSnQt6w_11-1-rgb_front` | yes | yes | `test/-g0iPSnQt6w_11-1-rgb_front.npy` | no | exact match |
| `92V3oH63zbQ_12-1-rgb_front` | yes | yes | `test/92V3oH63zbQ_12-1-rgb_front.npy` | no | exact match |
| `-g45vqccdzI_5-1-rgb_front` | yes | yes | `test/-g45vqccdzI_5-1-rgb_front.npy` | no | exact match |
| `3ddzkmFPEBU_1-1-rgb_front` | yes | yes | `test/3ddzkmFPEBU_1-1-rgb_front.npy` | no | exact match |
| `-fZc293MpJk_2-1-rgb_front` | yes | yes | `test/-fZc293MpJk_2-1-rgb_front.npy` | no | exact match |
| `FZCEymcpq7I_0_1-1-rgb_front` | yes | yes | `test/FZCEymcpq7I_0_1-1-rgb_front.npy` | no | exact match |
| `37ZtKNf6Yd8_0-1-rgb_front` | yes | yes | `test/37ZtKNf6Yd8_0-1-rgb_front.npy` | no | exact match |
| `FZd8Iv9ACVw_3_4-8-rgb_front` | yes | yes | `test/FZd8Iv9ACVw_3_4-8-rgb_front.npy` | no | exact match |
| `Fzj3jz2Imf0_5_6-1-rgb_front` | yes | yes | `test/Fzj3jz2Imf0_5_6-1-rgb_front.npy` | no | exact match |
| `FzAIlhumvMA_3-2-rgb_front` | yes | yes | `test/FzAIlhumvMA_3-2-rgb_front.npy` | no | exact match |
| `FzOQMA-CVPc_9-2-rgb_front` | yes | yes | `test/FzOQMA-CVPc_9-2-rgb_front.npy` | no | exact match |
| `-g0sqksgyc4_2-2-rgb_front` | yes | yes | `test/-g0sqksgyc4_2-2-rgb_front.npy` | no | exact match |
| `8kAWy2YodzQ_16_17_18-1-rgb_front` | yes | yes | `test/8kAWy2YodzQ_16_17_18-1-rgb_front.npy` | no | exact match |
| `FZbyRzy4huk_1-8-rgb_front` | yes | yes | `test/FZbyRzy4huk_1-8-rgb_front.npy` | no | exact match |
| `G33aqW3DLpc_1-10-rgb_front` | yes | yes | `test/G33aqW3DLpc_1-10-rgb_front.npy` | no | exact match |
| `G3VM7etNABI_2_3-10-rgb_front` | yes | yes | `test/G3VM7etNABI_2_3-10-rgb_front.npy` | no | exact match |
| `G1lNlhjWC1I_16_17-8-rgb_front` | yes | yes | `test/G1lNlhjWC1I_16_17-8-rgb_front.npy` | no | exact match |
| `g3ZluRtRXVc_5-3-rgb_front` | yes | yes | `test/g3ZluRtRXVc_5-3-rgb_front.npy` | no | exact match |
| `FzmL8SL6Bow_0-8-rgb_front` | yes | yes | `test/FzmL8SL6Bow_0-8-rgb_front.npy` | no | exact match |

**19/19 found. 0 missing. 0 duplicates. Naming required zero normalization**
— OpenSLT's I3D feature filenames use exactly the same `SENTENCE_NAME`
convention as How2Sign's own official TSVs and our benchmark manifest
(`<video_id>_<sentence_idx>-<view>-rgb_front`), because both are keyed
directly off How2Sign's own official IDs.

## 4. Extraction

Only the 19 matching files were extracted (not the other ~2,309 test-split
entries), into:
```
asl-translator/data/public_benchmarks/how2sign/openslt_features/
```
— a sibling of `videos/` and `references/`, still clearly separated from
`../asl_corpus/` (private Curify data). **Not staged with `git add`** — this
directory is untracked, matching the existing convention for
`public_benchmarks/how2sign/videos/` (see that folder's own README on
licensing/redistribution).

## 5. Feature file inspection

All 19 load cleanly with `numpy.load`, no errors, no corruption.

| Property | Result |
|---|---|
| File type | NumPy `.npy` (binary, valid header on all 19) |
| Shape pattern | `(N_frames, 1024)` for every file — **1024-d feature vector per I3D-encoded segment**, consistent across all 19 |
| dtype | `float32`, consistent across all 19 |
| N_frames range | 100 (`-g0iPSnQt6w_11-1`, 5.27s clip) to 1034 (`G33aqW3DLpc_1-10`, 30.67s clip) — scales with clip duration, as expected |
| Effective feature rate (N_frames / duration_s) | 15.46 to 41.21 features/sec across the 19 clips — **not a single fixed rate** |
| Total disk usage (19 files) | 37.79 MB |

**On the varying feature rate — a caveat, not a red flag.** I3D feature
extraction runs at a fixed *stride over raw video frames*, not a fixed
output rate in features/second; How2Sign's source clips were recorded at
different native frame rates (this project's own earlier frame-rate checks
on these same 19 clips found 24fps, 30fps, and 50fps videos in the set).
A 50fps clip naturally yields more raw frames — and thus more I3D feature
vectors at a fixed stride — per second of video than a 24fps clip. The
observed range is consistent with that explanation and with frame counts
that scale sensibly with each clip's own duration; it is not evidence of
corrupted or mismatched data, but it does mean **feature-frame index does
not correspond to a fixed wall-clock timestamp** across clips — relevant
context if a future step ever needs frame-level (not sentence-level)
alignment.

**Do the released feature IDs correspond to the same How2Sign
segmentation/alignment our benchmark used?** Consistent with yes: frame
counts scale plausibly with the `duration_s` values in our manifest (which
were themselves taken from How2Sign's official **original-alignment** TSV,
not the "manually re-aligned" one — the correction already recorded in
`HOW2SIGN_MINI_BENCHMARK.md`). This is a **consistency check, not an
independent confirmation** — the official small per-split manifest
(`cvpr23.fairseq.i3d.test.how2sign.tab`, ~577KB) that OpenSLT ships
alongside these features would give an exact per-clip length/reference
cross-check, but that file was not part of this turn's approved download
and was not fetched.

## 6. Benchmark integrity

The 19-clip selection in `manifest.csv` was **read only, never modified**.
No clip was added, removed, or re-selected based on this compatibility
result — consistent with the instruction that the benchmark was fixed
before model evaluation and must stay fixed regardless of what any given
model/feature source turns out to support.

## 7. Next requirements if a full evaluation is pursued later

Not executed in this turn; recorded for reference only:
1. Download the ~127MB checkpoint (`checkpoint.best_reduced_sacrebleu_3.5401.pt`,
   Dataverse file listing already confirmed via API in the prior research
   pass) — still pending your explicit go-ahead.
2. Install Fairseq + the repo's conda environment, with a disclosed
   substitution for the `cudatoolkit=11.5.1` pin (no macOS build exists) —
   a CPU-only `torch` build in its place, untested by us so far.
3. Point the repo's `task generate` flow at a manifest containing only our
   19 `openslt_features/*.npy` files (not the full test split) and the
   matching reference text already in `references/*.srt`.
4. Score with `scripts/analyze_fairseq_generate.py` for BLEU/rBLEU, and
   separately with this repo's own `asl-eval/evaluate.py` for WER/CER/IoU
   consistency with every other comparison already done in this project.

---

## Answers

**A. How many of our 19 clips exist in the released OpenSLT test features?**
**19 / 19.**

**B. Is the mapping one-to-one?**
Yes — exactly one feature file per clip ID, zero duplicates, zero ambiguous
matches, zero naming normalization required.

**C. Do the released feature IDs correspond to the same How2Sign
segmentation/alignment used by our benchmark?**
Consistent with yes, based on frame-count-vs-duration scaling using our
manifest's own (original-alignment-derived) durations — but not
independently confirmed against OpenSLT's own official per-clip length
manifest (`cvpr23.fairseq.i3d.test.how2sign.tab`), which was not downloaded
this turn. Call this "strongly consistent, not yet fully proven."

**D. Can we now proceed to checkpoint inference without changing the
19-clip subset?**
Yes, feature-compatibility-wise — every clip we already fixed has a
matching, loadable, correctly-shaped I3D feature file ready to go. The
19-clip subset itself required and received zero changes.

**E. What is the exact next download/setup step?**
Not yet executed, per your instructions to stop here. If/when you approve
continuing: download the ~127MB checkpoint
(`checkpoint.best_reduced_sacrebleu_3.5401.pt`) from the same Dataverse
release, file ID confirmed in the prior research pass.

**F. How much disk space is now used?**
`asl-translator/data/public_benchmarks/how2sign/openslt_features/`: **37.79
MB** (19 files). Full `public_benchmarks/how2sign/` directory (videos +
references + source_metadata + openslt_features): **94 MB** total. The
transient 546MB `test.zip` was deleted immediately after the 19 needed files
were extracted — nothing multi-hundred-MB remains on disk.

**G. git status --short:** see below.
