# ASL evaluation & open-source baseline — summary, 2026-08-31

**Audience:** decision-maker skim. **Scope:** evaluation/data work only — no
production code changed, nothing trained, nothing committed.

---

## 1. Manager goal

Curify's current production ASL translator uses a frame-by-frame approach
that is structurally weak for two things motion sign language depends on:
continuous motion and fingerspelling. The assigned goal was threefold:
clean up the evaluation data, expand trustworthy test data, and try whether
a runnable open-source ASL baseline exists as a reference point.

---

## 2. Data / ground-truth progress

- The 2026-08-30 label-leakage contamination cleanup (155 and 1320 had the
  answer burned into the model's input) is incorporated; the corpus's
  guard rails (`check_leakage.py`, `corpus_guard.py`) are in place.
- **SignCaption (external tool) annotations: 6 total** —
  `1467_nohead-half1`, `1474_1000004432`, `1477_recording`,
  `1320_1000022357`, `155_demo`, `1252_1000016397`.
- **155 and 1252 are the corpus's two verified-gold human-translated
  anchors.** Both now have a SignCaption reading checkable directly against
  that real gold — the first time in this project SignCaption's own error
  rate is measurable, not just "how much it disagrees with another
  unverified system."
  - **155:** WER 0.4815, CER 0.3712
  - **1252:** WER 0.5192, CER 0.3347
- **On 1252, SignCaption correctly recovered both fingerspelled names
  ("Greg" and "Sara"); neither Curify baseline0 nor temperature0 recovered
  either name.**
- **SignCaption is still not ground truth.** It makes real factual errors
  (e.g. a wrong age on 155) and at least one clear fabricated clause on
  1252 ("It's nice to volunteer" — not in the gold at all). Treat it as an
  external-tool reference point, not a source of truth.

---

## 3. Public benchmark (How2Sign)

- Fixed 19-clip subset of the official How2Sign **test** split.
- **351.6 seconds total (~5.86 minutes)** across the 19 clips.
- 19/19 English references matched against the official test-split TSV.
- 19/19 clips visually checked for obvious burned-in answer text — clean.
- Selection was frozen **before** any model was evaluated against it, and
  has not been touched since.
- The evaluator smoke test (feeding each reference back as its own
  "prediction," expecting WER=0/CER=0/IoU=1.0) passed for all 19.

---

## 4. Open-source baseline search

- **SpaMo** — its one released checkpoint is trained on Phoenix14T (German
  Sign Language), not ASL. Not usable without training.
- **SSVP-SLT** — best native How2Sign code support of the candidates
  checked, but **no checkpoint of any kind is released.**
- **VTaMo** — has How2Sign configs, but the maintainers' own README states
  pretrained weights and inference/eval scripts are **not released yet.**
- **OpenSLT** (`imatge-upc/slt_how2sign_wicv2023`, the official How2Sign
  paper's own baseline) was the **first genuinely runnable, non-restricted,
  How2Sign-native pretrained continuous ASL→English checkpoint found.**

---

## 5. OpenSLT reproduction

- Official checkpoint downloaded and **checksum-verified** against the
  Dataverse host's own reported MD5 (exact match).
- Official released How2Sign I3D test features matched our 19-clip
  benchmark **19/19** by clip ID, including a direct text-level match on
  one clip's reference sentence (not just a frame-count consistency check).
- A CPU-only, isolated conda environment was built and verified to be
  **genuinely native Apple Silicon (arm64)** — an earlier attempt silently
  resolved Intel/Rosetta packages and was caught and rebuilt correctly
  before anything else was installed.
- Checkpoint **loaded successfully** on CPU (11.7M parameters, ~200MB RAM,
  under half a second).
- **No retraining, no fine-tuning** — inference only, throughout.
- CPU inference **works**, end to end, on real benchmark data.

---

## 6. OpenSLT result

- 19 selected benchmark clips → **18/19 scored.**
- **1 clip skipped, not a crash and not a workaround failure**: the
  official checkpoint's own config caps input length at
  `max_source_positions=1024`; our longest clip
  (`G33aqW3DLpc_1-10-rgb_front`, 30.67s) has 1034 I3D feature frames. The
  official pipeline's own `--skip-invalid-size-inputs-valid-test` flag
  dropped it, exactly as documented. This was not worked around — doing so
  would mean tuning the official config.

**18 scored clips:**

| Metric | Value |
|---|---|
| Corpus WER | **1.1637** |
| Corpus CER | **0.8675** |
| SacreBLEU | **0.96** (fairseq's own scorer) / **0.93** (official `analyze_fairseq_generate.py`, truecased) |
| chrF | **19.59** (independent) / **17.11** (official script, word_order=2) |
| Full batch runtime | **~25 seconds, CPU only** |

**Main observed failures:**
- Weak semantic correspondence — predictions rarely track the reference's actual topic.
- Fluent, grammatical-sounding English that is unsupported by the reference content.
- Repetition loops, concentrated in longer clips.
- One severe hallucination outlier (a 3-word reference produced a 122-word repetitive fabrication).
- No fingerspelling/name examples exist in this particular public subset, so it can't speak to that failure mode one way or the other.

---

## 7. Conclusion

- **OpenSLT is reproducible and runnable** on this hardware, with no
  training required.
- **This released checkpoint performs poorly on our fixed mini benchmark** —
  corpus WER above 1.0, sacreBLEU under 1.0.
- It is therefore useful **as an open-source baseline / reference point**
  for what a lightweight, fully-released, non-LLM ASL translation system
  achieves — **not as a drop-in replacement for production.**
- This does **not** mean the OpenSLT architecture is fundamentally bad —
  the paper's own reported numbers are modest too, and this is one of
  several checkpoint variants the authors released.
- This does **not** establish OpenSLT as better or worse than Curify on
  How2Sign — Curify has not yet been run on these exact 19 clips, so no
  apples-to-apples comparison exists yet.
- Separately, existing internal evidence (the 1252 case) already shows
  Curify's current frame-by-frame approach performs poorly and specifically
  loses fingerspelling information — that finding stands on its own and
  doesn't depend on the OpenSLT comparison above.

---

## 8. Recommended next step

1. **Report these results first** before further investment.
2. **Do not spend more effort optimizing the current frame-based production
   approach** on the strength of this data alone — the fingerspelling
   weakness is already independently established (1252).
3. **If a second open-source attempt is wanted**, the next step is
   investigating whether any *other* genuinely runnable pretrained ASL
   checkpoint exists (same strict bar used here: real weights, not just a
   paper).
4. **If no second runnable model exists**, the next reasonable experiment
   is a **native-video VLM baseline** (e.g. dense-frame-sampling video
   understanding, sidestepping the sparse-still-frame failure mode already
   diagnosed in Curify's own pipeline) — flagged as a separate, later
   experiment, not started here.

---

## What is complete / what is not complete

| Item | Status |
|---|---|
| Contamination cleanup incorporated | ✅ Complete |
| SignCaption annotations (6 total, incl. both verified-gold anchors) | ✅ Complete |
| 19-clip How2Sign benchmark frozen + verified | ✅ Complete |
| Open-source candidate search (SpaMo/SSVP-SLT/VTaMo/OpenSLT) | ✅ Complete |
| OpenSLT checkpoint + features verification | ✅ Complete |
| OpenSLT CPU environment + inference (18/19 clips) | ✅ Complete |
| OpenSLT vs. Curify on the same 19 clips | ❌ Not started (explicitly deferred) |
| The 19th (longest) clip scored under any config | ❌ Not attempted (would require tuning the official config) |
| A second open-source ASL baseline candidate | ❌ Not started |
| Native-video VLM baseline experiment | ❌ Not started (flagged as a future option only) |
| Any change to production code | ❌ Not applicable — none made |

---

## Scope note

No model was run beyond what's reported above. No OpenSLT parameter was
tuned. Curify was not run on the 19 How2Sign clips. Nothing was staged,
committed, or pushed.
