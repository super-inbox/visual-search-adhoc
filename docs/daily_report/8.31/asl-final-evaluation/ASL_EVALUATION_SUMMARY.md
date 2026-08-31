# ASL translator evaluation — combined summary, 2026-08-31

**Audience:** decision-maker skim. **Scope:** evaluation/diagnostics
only, spanning two completed milestones — ground-truth/data work plus two
open-source baseline checkpoints. No production code changed, nothing
trained, nothing committed or pushed as part of this evaluation work.

---

## 1. Current Curify frame-based approach — diagnosis confirmed weak

Curify's production ASL translator reasons over sparse, static frames. It
has no explicit representation of continuous motion — the exact signal
ASL depends on for both ordinary signing (movement path, speed, repeated
strokes) and fingerspelling (rapid, discrete hand-shape sequences).

The clearest evidence is the `1252` case, the only fully verified-gold
production comparison available:

| Config | WER |
|---|---|
| Curify baseline0 | **0.9231** |
| Curify temperature0 | **0.9231** |

Both configurations **fail to recover the fingerspelled names "Greg" and
"Sara"** present in the reference. Pinning `temperature=0` improved
run-to-run *repeatability* on unrelated content (documented separately)
but did not change this outcome — the failure is structural (sparse
frame sampling loses continuous motion, not the decoding temperature.

---

## 2. Ground truth / data work

- The 2026-08-30 label-leakage contamination cleanup (two videos had the
  answer burned directly into the model's input) is incorporated; guard
  rails (`check_leakage.py`, `corpus_guard.py`) are in place.
- **SignCaption (external commercial tool) annotations: 6 total.**
- **155 and 1252 are the corpus's two verified-gold, human-translated
  anchors.** Both now have a SignCaption reading checkable directly
  against real gold:

  | Clip | WER | CER |
  |---|---|---|
  | 155 | **0.4815** | **0.3712** |
  | 1252 | **0.5192** | **0.3347** |

- **On 1252, SignCaption correctly recovered both fingerspelled names
  ("Greg" and "Sara"); neither Curify configuration recovered either
  name.** This is the clearest concrete evidence in this project that
  motion/continuous-video-aware processing (which SignCaption, an
  external tool, uses) captures information Curify's frame-based pipeline
  structurally loses.
- **SignCaption is still not ground truth.** It makes real factual errors
  (e.g. a wrong age on 155) and at least one clear fabricated clause on
  1252 ("It's nice to volunteer" — absent from the gold entirely).
  **Conclusion: SignCaption is a useful external reference point, not a
  source of truth**, and it is a commercial/external system, not
  something evaluated for licensing or integration here.

---

## 3. Public benchmark — frozen How2Sign mini-benchmark

- Fixed 19-clip subset of the official How2Sign **test** split.
- **351.6 seconds total (~5.86 minutes)** across the 19 clips.
- **19/19** English references matched against the official test-split
  TSV.
- **19/19** clips visually checked for obvious burned-in answer text —
  clean.
- Selection was frozen **before** any model was evaluated against it, and
  has not been touched since — including throughout both baseline runs
  below.

---

## 4. OpenSLT — first open-source baseline

- The official How2Sign paper's own released pretrained
  continuous-ASL→English checkpoint (`imatge-upc/slt_how2sign_wicv2023`).
- Successfully reproduced locally: checksum-verified checkpoint, CPU-only
  Apple Silicon environment, no training or fine-tuning.
- **18/19 scored.** The 19th clip was **skipped, not worked around**: its
  1034 I3D feature frames exceed the official checkpoint's own
  `max_source_positions=1024` config limit; the official
  `--skip-invalid-size-inputs-valid-test` flag dropped it exactly as
  documented.

| Metric | Value |
|---|---|
| Corpus WER | **1.1637** |
| Corpus CER | **0.8675** |
| SacreBLEU | **~0.93–0.96** |
| chrF | **~17.11–19.59** |

**Main failures:** semantic mismatch with the reference topic, fluent-
sounding but unsupported English, repetition loops in longer clips, one
severe hallucination outlier. **Reproducible, but not usable as a
drop-in production baseline.**

---

## 5. Uni-Sign — second open-source baseline

- A motion/pose-aware continuous ASL model (ICLR 2025), architecturally
  distinct from both Curify (no temporal model) and OpenSLT (single I3D
  feature extractor): raw video → RTMPose 2D keypoints → skeleton/graph
  temporal encoder → mT5-base English decoder.
- Its How2Sign-specific pose-only checkpoint was released 2025-12-20 —
  the first genuinely runnable, ASL-native second checkpoint found in
  this project's search.
- Reproduced locally under the same constraints as OpenSLT: CPU-only
  Apple Silicon, no training/fine-tuning, decoding parameters
  (`num_beams=4`, `max_new_tokens=100`) left exactly as documented,
  never tuned against any reference.
- **19/19 inference success** — notably including the one clip OpenSLT's
  pipeline could not score at all (Uni-Sign's frame-subsampling approach
  has no equivalent hard length limit).

| Metric | Value |
|---|---|
| Corpus WER | **0.9480** |
| Corpus CER | **0.7606** |
| SacreBLEU | **3.13** |
| chrF | **20.34** |
| Runtime | **~20.6 minutes, CPU only, all 19 clips** |

**Materially better than OpenSLT on every aggregate metric computed.**
But: **topic fabrication occurs on 19/19 clips** — no prediction tracks
its reference's actual content, regardless of the metric improvement.
Repetition loops occur on 8/19 clips (42%). No reliable number or
fingerspelling recovery was observed anywhere in this public subset (one
prediction fabricates a specific but unrelated proper noun). Every clip
15.81 seconds or longer was truncated mid-sentence by the
`max_new_tokens=100` decoding cap — a completion-budget effect, separate
from and not the explanation for the semantic failure. **Not usable
quality in absolute terms**, despite the relative improvement.

---

## 6. Same-benchmark comparison — OpenSLT vs. Uni-Sign

Matched exactly to OpenSLT's own 18 scored clips (excluding the one clip
only Uni-Sign could score, for a strict apples-to-apples set):

| Metric | OpenSLT (18/19) | Uni-Sign (18/18, same clips) |
|---|---|---|
| WER | 1.1637 | **0.9477** |
| CER | 0.8675 | **0.7613** |
| SacreBLEU | ~0.93–0.96 | **3.35** (higher) |
| chrF | ~17.11–19.59 | **20.88** (higher) |

**Uni-Sign is relatively better than OpenSLT on every metric on the
identical clip set — but neither system is production-quality.** A
corpus WER near or above 1.0 for both means the total edit distance
required to correct either system's output is comparable to or exceeds
the total length of the reference text.

---

## 7. Licensing

- **Uni-Sign checkpoint:** CC BY-NC-4.0 (non-commercial only).
- **Uni-Sign code repository:** no explicit LICENSE file found (confirmed
  at the pinned evaluation commit).
- **Therefore: research/evaluation only.** Not approved for commercial
  Curify production integration, independent of and regardless of any
  accuracy result documented above.
- (For completeness: OpenSLT's code is MIT; its data/checkpoints are CC
  BY-NC-ND 4.0 — also non-commercial, also not production-eligible as-is.)

---

## 8. Overall conclusion

- **The current Curify frame-by-frame approach is confirmed weak.** Its
  sparse, static-frame representation structurally loses continuous
  motion, and this has a concrete, verified consequence: it fails
  fingerspelling recovery (Greg/Sara on 1252) that an external
  motion-aware system (SignCaption) succeeds at on the same content.
- **Motion-aware modeling helps relative benchmark performance**, as
  shown directly by Uni-Sign outperforming OpenSLT on every metric on the
  same 18-clip matched benchmark.
- **But neither released academic checkpoint (OpenSLT, Uni-Sign) is
  sufficiently accurate for product use.** Topic fabrication is universal
  or near-universal in both; neither recovers numbers or names reliably
  in this public benchmark.
- **SignCaption performs substantially better on the two internal
  human-gold cases** (WER 0.48–0.52 vs. both academic checkpoints' WER
  ≥0.95) and is the only system in this project confirmed to recover
  fingerspelled names — but it is a **commercial, external reference
  system**, not something this evaluation vetted for licensing,
  integration, or cost, and it still makes real factual errors.
- **The next phase should NOT be more tuning of these academic
  checkpoints.** Their absolute quality ceiling, decoding budget
  behavior, and non-commercial licensing are all now well characterized;
  further tuning on the frozen benchmark would also risk contaminating
  the evaluation set this project has deliberately kept untouched.
- **The next phase should target a product-usable continuous-video
  approach with commercially compatible licensing.** See
  `NEXT_PRODUCT_DIRECTION.md` for the proposed goal and hard
  requirements — no specific next experiment has been executed yet.
