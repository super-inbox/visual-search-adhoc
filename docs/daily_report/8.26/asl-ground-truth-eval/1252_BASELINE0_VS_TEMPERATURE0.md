# 1252 ASL Eval — Baseline0 vs Temperature=0

## Reference

- human-translated by Curify
- verified
- 11 segments
- fingerspelled names (Greg, Sara)
- numbered items ("Number two", "Number three", "Number four" ×2, "number three" embedded in a sentence)
- real user-submitted ASL video (`1252_1000016397_76.8s.mp4`)

Note: the filename says `76.8s`; ffprobe reports actual duration `77.496s`. This
discrepancy existed before this experiment and is not corrected here — both
runs used the actual ffprobe-observed duration for frame sampling.

## Controlled experiment

Same:
- `gemini-2.5-flash`
- same prompt (`prompt_sha256` identical across both runs)
- same motion sampler
- same `FRAME_BUDGET=96`
- same `KEYFRAME_WIDTH=512`
- same `BATCH_SIZE=24`
- same selected-frame logic (96/96 frames used, 22 active / 22 idle runs)

Only intentional variable:
- **baseline0** — temperature omitted (provider default)
- **temperature0** — temperature explicitly set to `0.0`

This is "production-configuration-equivalent," not "identical deterministic
reproduction." Gemini decoding is non-deterministic in practice even at
temperature 0.

## Results

| Metric | baseline0 | temperature0 |
|---|---|---|
| Reference words | 52 | 52 |
| Prediction words | 50 | 41 |
| Substitutions | 46 | 37 |
| Deletions | 2 | 11 |
| Insertions | 0 | 0 |
| WER | 0.9231 | 0.9231 |
| CER | 0.7211 | 0.6693 |
| Temporal precision | 0.6877 | 0.7810 |
| Temporal recall | 0.6046 | 0.7318 |
| Temporal IoU | 0.4743 | 0.6072 |
| Prediction segments | 14 | 15 |
| Frames sampled | 96 | 96 |
| Model calls | 4 | 4 |

Note: WER is numerically identical (0.9231) in both configs — this is a
coincidence of total error count (46+2=48 vs 37+11=48, both over 52 reference
words), not equal quality. The error *composition* differs: baseline0 makes
mostly substitutions, temperature0 has more deletions (more reference content
dropped entirely) but a somewhat closer CER.

## Diagnostic content

| Reference concept | baseline0 | temperature0 | observation |
|---|---|---|---|
| "Greg" (fingerspelled name, ref#1: "The boy's name is Greg.") | "Do you know H.G.Q.?" | "Do you remember HPG?" | Neither run recognized the name. Both attempted a fingerspelling readout but produced different, wrong letter sequences (H.G.Q. vs HPG) — no match to "Greg" in either. |
| "Sara" (fingerspelled name, ref#7: "The woman named Sara has a name sign.") | "sign, yes." | "Name, name, sign, yes." | Neither run outputs "Sara" or any name. temperature0 recovers more of the segment content (iou 0.66 vs 0.18, closer timing) but the fingerspelled name itself is absent from both. |
| "Number two" (ref#2) | "Two more." | "Add two." | Numeral "two" present in both; neither reproduces the reference's "Number two" phrasing. Both are substitutions. |
| "Number three" (ref#4) | "And three more." | "Add three." | Same pattern — numeral present, "Number" wording lost in both. |
| "Number four" (ref#6, first occurrence) | "numbers: four, three." | "Family, four, three." | Both mention "four" but bundle extra content ("three" / "Family") not present in this specific reference segment. |
| "Number four" (ref#8, second occurrence) | *(no aligned prediction — segment dropped, 0 overlap)* | "How many?" | baseline0 fully drops this reference segment (a deletion); temperature0 has weak overlap and doesn't reproduce "four" either. |
| "The book is number three." (ref#10) | "you show number three." | "How many do you have?" | baseline0 retains the literal "number three" wording (partial semantic match); temperature0 loses it entirely, substituting an unrelated question. |

## Interpretation

Scoped to this one verified 1252 case only:

1. **Did temperature0 improve WER?** No — WER is numerically identical
   (0.9231 in both), and the tie is coincidental (same total error count,
   different error composition). Not an improvement.
2. **Did temperature0 improve CER?** Yes, modestly — 0.6693 vs 0.7211, about
   0.05 absolute lower.
3. **Did it improve fingerspelling?** No. Both configurations completely
   failed on both fingerspelled names ("Greg" and "Sara" never appear in
   either prediction transcript). This is a shared failure mode, not
   temperature-sensitive on this video.
4. **Did it improve numbered-item recognition?** No clear improvement, and
   arguably slightly worse: baseline0 retained literal "number three" wording
   once (ref#10) where temperature0 lost it; neither reliably reproduces the
   reference's "Number N." phrasing across the other numbered segments.
5. **Did timing materially change?** Yes, and this is the largest effect
   observed on this video: temporal IoU rose from 0.4743 to 0.6072 (+0.13
   absolute), precision from 0.6877 to 0.7810, recall from 0.6046 to 0.7318.
   temperature0 segments align noticeably better with when signing actually
   occurred, even though *what* was transcribed did not reliably improve.
6. **Did hallucination/fragmentation change?** Both configurations produce
   fluent, grammatical English sentences that are largely unsupported by the
   literal reference content (neither ever reproduces the specific
   fingerspelled names or consistent "Number N" phrasing) — this pattern is
   present in both configs. Segment count is similar (14 vs 15 from 11
   reference segments); temperature0 is not more or less fragmented in any
   meaningful way.

## 1252 conclusion

On this video, temperature=0 modestly improved CER and **substantially
improved temporal alignment** (IoU +0.13), but did **not** improve WER (tied)
and did **not** fix the dominant failure mode on this case: neither
configuration recognized either fingerspelled name ("Greg", "Sara"), and
neither reliably reproduced the reference's numbered-item phrasing. This
contrasts with 155, where temperature0's advantage was primarily a small
WER/CER edge with timing nearly unchanged — here it's the reverse: timing
moved more than text quality. No generalization beyond this one video is
claimed.
