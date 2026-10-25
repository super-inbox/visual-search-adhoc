# ASL P0-11 / P0-12 / P0-13: Boss Summary

2026-10-09, updated 2026-10-11 (P0-11 same-init control completed) · Full detail: `WORK_REPORT.md`

| Experiment | Question | Status |
|---|---|---|
| P0-11 | Does more labeled How2Sign data help? | **COMPLETE**: same-init control done 2026-10-11 |
| P0-12 | Why is our Uni-Sign at 5.39 vs the authors' 9.59 on the same clips? | **PARTIAL**: causes identified; GPU confirmation blocked |
| P0-13 | Does a better representation help at the same data? | **COMPLETE** |

## The one comparison that matters (frozen 147-clip test)

| What we changed | Supervised clips | BLEU | chrF |
|---|---|---|---|
| Nothing (current baseline, P0.2 run) | 2,751 | 1.02 | 11.1 |
| Nothing (re-run with the same starting weights as the rows below) | 2,751 | 0.80 | 10.6 |
| More labeled How2Sign data | 6,605 | 1.15 | 12.4 |
| More labeled How2Sign data | 13,210 | 0.54 | 12.3 |
| More labeled How2Sign data | 26,419 | 0.52 | 9.5 |
| **Better pretrained representation (Uni-Sign), same data** | **2,751** | **3.25** | **17.0** |

The two baseline rows differ only in random starting weights. That ~0.2 BLEU gap is about the size of the noise,
so BLEU differences below ~0.5 here are not meaningful.

## Answers

1. **Data or representation?** Representation, in our current setup. Swapping in Uni-Sign's pretrained
   representation tripled BLEU at the same data, with a 95 % CI of +1.3 to +3.4. Nearly 10× more labeled
   How2Sign data did not improve BLEU. The same-starting-weights control (done 2026-10-11) confirms this. It is
   strong evidence, not final proof: each condition is still a single training seed.
2. **Does more How2Sign data help?** Not for translation quality with our current model.
   - Loss improves, but BLEU stays flat within noise (best +0.36, not significant). chrF gains ~1.7 at 2.4–4.8×
     data, then drops below the start at 9.6×.
   - Outputs become more generic at the larger sizes: 63 → 29 distinct sentences out of 147 (same starting
     weights).
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
   - Seed variance.
   - Generalization to real users.
6. **Important nuance.** Uni-Sign's representation was itself learned from much more sign-language data (about
   984 h of YouTube-ASL plus all of How2Sign). The lesson is not "data doesn't matter". It is: **broad
   sign-language pretraining beats adding more of the same labeled How2Sign sentences.**

## Next

1. **One CUDA GPU session (about 1–2 h) for the P0-12 controlled run.** Test timestamp, crop, extractor and
   runtime one at a time. Already scripted.
2. **Fix the canonical Uni-Sign preprocessing** (segment to the signing, crop to the signer) based on step 1.

(The P0-11 same-init control is done; it confirmed the result.)

Later:
- multi-seed checks
- decoder fine-tuning
- a random-init architecture control
- real Curify-user video
- ASL-fluent human evaluation
