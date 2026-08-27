# 155 ASL Eval — Baseline0 vs Temperature=0

## Experiment

Same video (`155_demo_asl-demo-translation_26.7s.mp4`), evaluated with the same
production-configuration-equivalent sampler, prompt, and model
(`gemini-2.5-flash`), same 96-frame budget, same 4-batch structure
(`batch_size=24`). The only intentional variable is temperature:

- **baseline0** — temperature omitted (provider default)
- **temperature0** — temperature explicitly set to `0.0`

This is "production-configuration-equivalent," not a literal reproduction of
any past production run. Gemini decoding is non-deterministic in practice
even at temperature 0, so this comparison does not claim deterministic
reproduction of old baseline output — it's two fresh calls under two
configurations.

## Reference

Verified human-translated SRT, 6 reference segments, Curify public demo
asset. Diagnostic content: family member count and relations ("my family has
five, including my father," mother/father/brother/sister), and four
ages/numbers (thirty, twenty-nine, nine, seven).

## Results

| Metric | baseline0 | temperature0 |
|---|---|---|
| Reference words | 27 | 27 |
| Prediction words | 33 | 36 |
| Substitutions | 2 | 0 |
| Deletions | 1 | 0 |
| Insertions | 7 | 9 |
| WER | 0.3704 | 0.3333 |
| CER | 0.3485 | 0.3409 |
| Temporal precision | 0.9125 | 0.8847 |
| Temporal recall | 0.7613 | 0.7762 |
| Temporal IoU | 0.7095 | 0.7049 |
| Prediction segments | 8 | 8 |
| Frames sampled | 96 | 96 |
| Model calls | 4 | 4 |

## Qualitative errors

- **Age/number handling**: identical and fully correct in both runs — five,
  thirty, twenty-nine, nine, seven, seven all matched the reference exactly
  in both configurations.
- **Family relationship wording**: baseline0 dropped the clause "including my
  father" from segment 1 (a deletion); temperature0 kept it verbatim,
  matching the reference exactly for that segment.
- **Duplication**: both runs independently emit the "My mother is
  twenty-nine." line twice (once ~8.9–9.9s, again ~10.3–12.6s) and the "My
  brother is seven." line twice (once ~18.2–18.8s or ~18.5–18.8s, again
  ~19.1–20.4s). This is the dominant error in both configurations — it drives
  most of the insertion count in both, not a temperature-specific failure
  mode.
- No hallucinated content unrelated to the reference was observed in either
  run; all extra words are exact repeats of already-correct lines.

## Interpretation

Answer scoped to this one verified demo case only:

1. **Did temperature=0 improve WER?** Yes, marginally — 0.3333 vs 0.3704 on
   this single case, driven by temperature0 correctly retaining "including
   my father" (0 substitutions/deletions vs baseline0's 2 substitutions/1
   deletion), offset by one extra insertion.
2. **Did temperature=0 improve CER?** Marginally — 0.3409 vs 0.3485, a small
   difference in the same direction as WER.
3. **Did timing coverage materially change?** No — temporal precision,
   recall, and IoU are within ~0.03 of each other across configurations; not
   a material difference on this one video.
4. **Did number/age recognition improve?** No — both configurations got every
   age/number correct already; there was no room for temperature to change
   this.
5. **Did output become obviously less/more fragmented?** No — both produced
   8 segments from 6 reference segments, with the same duplication pattern
   (mother-is-twenty-nine and brother-is-seven each split into two segments)
   in both runs.

Temperature0 was **better on this single verified demo case** by a small
margin (WER and CER both slightly lower), primarily because it retained a
clause baseline0 dropped. This does **not** establish that temperature=0
solves ASL recognition, generalizes to other videos, or represents a
corpus-wide quality difference — it is one data point from one video with
one call each. The duplication pattern present in both runs suggests the
sampler/prompt's segment-merging behavior, not temperature, is the larger
source of error on this clip.

## Next step

Given that both configurations share the same duplication artifact and the
WER/CER gap is small, the more informative next step is likely a repeat run
on 155 to check whether the duplication and the baseline0/temperature0 gap
are stable across repeated calls (testing determinism/variance) before
drawing any conclusion about temperature. Proceeding to a different verified
corpus item would trade determinism information for breadth, which isn't yet
established here. Recommend testing repeat-run variance on 155 next, not
executed as part of this phase.
