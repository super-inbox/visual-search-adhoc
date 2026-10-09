# ASL P0-11 / P0-12 / P0-13: Boss Summary

2026-10-09 · Full detail: `WORK_REPORT.md`

| Experiment | Question | Status |
|---|---|---|
| P0-11 | Does more labeled How2Sign data help? | **PARTIAL**: main runs done; same-init control unfinished |
| P0-12 | Why is our Uni-Sign at 5.39 vs the authors' 9.59 on the same clips? | **PARTIAL**: causes identified; GPU confirmation blocked |
| P0-13 | Does a better representation help at the same data? | **COMPLETE** |

## The one comparison that matters (frozen 147-clip test)

| What we changed | Supervised clips | BLEU | chrF |
|---|---|---|---|
| Nothing (current baseline) | 2,751 | 1.02 | 11.1 |
| More labeled How2Sign data | 6,605 | 1.15 | 12.4 |
| More labeled How2Sign data | 13,210 | 0.54 | 12.3 |
| More labeled How2Sign data | 26,419 | 0.52 | 9.5 |
| **Better pretrained representation (Uni-Sign), same data** | **2,751** | **3.25** | **17.0** |

## Answers

1. **Data or representation?** Representation, in our current setup. Swapping in Uni-Sign's pretrained
   representation tripled BLEU at the same data, with a 95 % CI of +1.3 to +3.4. Nearly 10× more labeled
   How2Sign data did not improve BLEU. This is strong current evidence, not final proof: one control run and
   multi-seed checks are still open.
2. **Does more How2Sign data help?** Not for translation quality with our current model.
   - Loss improves, but BLEU peaks at 2.4× data and then falls.
   - Outputs become more generic: 102 → 29 distinct sentences out of 147.
   - The model never learns to rely on the video more.
3. **What's wrong with our Uni-Sign pipeline?** Most likely how we prepare the input video, not the model.
   - We cut clips at the original How2Sign timestamps, while the authors use corrected ones. In 28 of 128 clips our
     video contains none of the signed sentence.
   - We also feed the full frame instead of a crop around the signer, which distorts the skeleton scale.
   - Our pose extractor matches the official one closely.
   - How much each cause explains is **not yet measured**. That needs one CUDA GPU session.
4. **Is Uni-Sign a good research base?** **Yes.** It is our strongest baseline, and its representation clearly
   helps. **It is not product-ready.**
   - Our inference path is still behind the authors' (5.39 vs 9.59).
   - Real-user video is untested, and outputs repeat themselves.
   - Long videos are handled poorly.
   - No ASL-fluent human evaluation has been done.
5. **Still open:**
   - The size of each P0-12 cause.
   - The P0-11 same-init control.
   - Seed variance.
   - Generalization to real users.
6. **Important nuance.** Uni-Sign's representation was itself learned from much more sign-language data (about
   984 h of YouTube-ASL plus all of How2Sign). The lesson is not "data doesn't matter". It is: **broad
   sign-language pretraining beats adding more of the same labeled How2Sign sentences.**

## Next

1. **One CUDA GPU session (about 1–2 h) for the P0-12 controlled run.** Test timestamp, crop, extractor and
   runtime one at a time. Already scripted.
2. **Finish the P0-11 same-init control** (about 2.4 h CPU). It was cut short when the machine slept and the
   launching session ended; partial outputs are kept.
3. **Fix the canonical Uni-Sign preprocessing** (segment to the signing, crop to the signer) based on step 1.

Later:
- multi-seed checks
- decoder fine-tuning
- a random-init architecture control
- real Curify-user video
- ASL-fluent human evaluation
