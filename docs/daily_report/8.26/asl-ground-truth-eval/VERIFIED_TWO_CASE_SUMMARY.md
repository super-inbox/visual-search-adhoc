> # ⛔ RETRACTED — 2026-08-30
>
> **Every 155 number below is withdrawn.** The video scored as `155` was
> `videos/155_demo_asl-demo-translation_26.7s.mp4`, which was byte-identical to
> `curify-frontend/public/video/asl-demo-translation.mp4` — the **published demo output, with
> the English captions burned into the frame**. The reference answer was visible in the model's
> input, so these scores measure OCR of on-screen text, not ASL recognition.
>
> The tell is in the numbers themselves: the prediction reproduces the gold SRT verbatim
> including punctuation, with **0 substitutions and 0 deletions**, and the two "duplicate"
> segments are two batches reading the same caption while it was still on screen.
>
> Withdrawn: baseline0 WER 0.3704, temperature0 WER 0.3333, the post-dedup WER 0.0000
> "exact match", and any pooled figure combining 155 with 1252.
>
> **What still stands: everything about 1252** — clean input, verified human reference,
> WER 0.9231 under both configs. It is now the only accuracy measurement the corpus supports.
>
> Full account: `asl-translator/data/asl_corpus/CONTAMINATION.md`.

# Verified ASL A/B Summary — 155 + 1252

## Cases

**155** (`155_demo_asl-demo-translation_26.7s.mp4`)
- Curify public demo
- verified human GT
- 6 segments
- content: family member count and relations, four ages/numbers

**1252** (`1252_1000016397_76.8s.mp4`)
- real user-submitted video
- verified human GT
- 11 segments
- content: fingerspelled names (Greg, Sara) + numbered items

1320 is **not** included in this verified aggregate — it remains
`candidate_reference` / pending production-direction confirmation, per prior
scoping decisions.

## Per-case results

| Case | Config | WER | CER | Temporal IoU | Notes |
|---|---|---|---|---|---|
| 155 | baseline0 | 0.3704 | 0.3485 | 0.7095 | 2 sub / 1 del / 7 ins; ages/numbers all correct |
| 155 | temperature0 | 0.3333 | 0.3409 | 0.7049 | 0 sub / 0 del / 9 ins; ages/numbers all correct |
| 1252 | baseline0 | 0.9231 | 0.7211 | 0.4743 | 46 sub / 2 del / 0 ins; both fingerspelled names missed |
| 1252 | temperature0 | 0.9231 | 0.6693 | 0.6072 | 37 sub / 11 del / 0 ins; both fingerspelled names missed |

## Aggregate

Two methods, reported separately so the reader can judge which is more
appropriate:

**1. Simple macro average across the 2 verified videos** (unweighted mean of
each video's own metric — treats 155 and 1252 as equally important
regardless of length):

| Metric | baseline0 | temperature0 |
|---|---|---|
| Mean WER | 0.6468 | 0.6282 |
| Mean CER | 0.5348 | 0.5051 |
| Mean Temporal IoU | 0.5919 | 0.6561 |

**2. Pooled/micro word error rate** (total substitutions+deletions+insertions
across both videos, divided by total reference words across both videos —
weights each video by its own length, so 1252's 52 reference words count
more than 155's 27):

- baseline0: (10 + 48) errors / (27 + 52) words = 58 / 79 = **0.7342**
- temperature0: (9 + 48) errors / (27 + 52) words = 57 / 79 = **0.7215**

Methodology note: macro-average treats both videos as equally weighted data
points; pooled/micro weights by reference length, so it is dominated by
1252 (52 of 79 total reference words, ~66%). The two methods agree on
direction (temperature0 slightly lower error either way) but the pooled
number is much closer to 1252's own WER (0.9231) than to 155's, because of
that length weighting. Neither method should be read as more than a
2-video estimate.

1320 was not combined into either aggregate.

## Temperature conclusion

Across the two currently verified cases, the effect of temperature0 is
**mixed, not consistently positive**:

- **CER improved in both cases** (155: 0.3485→0.3409; 1252: 0.7211→0.6693) —
  the one metric where the direction is consistent.
- **WER improved in 155 but was exactly tied in 1252** (0.9231 = 0.9231,
  coincidentally identical total error count under different error
  composition) — not a conflict, but not a consistent improvement either.
- **Temporal IoU was essentially flat in 155** (0.7095→0.7049, a small
  decrease) **but rose substantially in 1252** (0.4743→0.6072) — the timing
  effect is not consistent in direction/magnitude across the two videos.

Do not read this as "temperature=0 is globally better" — it is not
confirmed across even these two verified cases in a consistent way, and both
videos still show serious errors under both configurations.

## Diagnostic observations

- **Numbers**: 155's four ages/numbers were recognized correctly by both
  configs. 1252's numbered items ("Number two/three/four") were mostly
  garbled into other numeral-bearing phrases by both configs (e.g. "Two
  more.", "Add two."), rarely reproducing the reference's literal "Number N."
  phrasing. Number handling on 1252 did not clearly improve with
  temperature0.
- **Fingerspelling**: 1252 is the only case that tests this, and both
  configs **completely failed** to recognize either fingerspelled name
  ("Greg" → "H.G.Q." / "HPG"; "Sara" → name omitted entirely in both). This
  is a shared, temperature-independent failure mode.
- **Duplicate segments**: present in 155 under both configs (repeated "My
  mother is twenty-nine." / "My brother is seven." lines) — the dominant
  error source there, not temperature-linked.
- **Hallucinations**: neither video shows content entirely unrelated to the
  reference topic; instead both configs on 1252 produce fluent, plausible
  English sentences that substitute for — rather than transcribe — the
  actual signed content (especially names and number phrasing). This looks
  like a "confident paraphrase" failure mode rather than random hallucination.
- **Timing vs. content**: the two cases diverge here. On 155, *when* signing
  occurred and *what* was signed were both already close to reference under
  both configs (timing nearly unchanged, content already near-correct). On
  1252, temperature0 markedly improved alignment on *when* signing occurred
  (IoU +0.13) without meaningfully improving *what* was recognized (WER
  tied, fingerspelling still 0/2). The two error dimensions do not move
  together.

## Recommendation

**(C) Temperature alone is not the core fix.** Both verified cases still
show major, temperature-independent failure modes: 155's duplicate-segment
problem persists under both configs, and 1252's catastrophic fingerspelling
failure (0/2 names recognized) and near-ceiling WER (0.9231) are identical
regardless of temperature. Where temperature0 helps, it helps only
partially and inconsistently (CER modestly, in both; timing substantially
in 1252 only; WER not at all in 1252). This does not look like a case where
switching production temperature would resolve the dominant error sources.
The more useful next step is expanding verified ground truth (particularly
more fingerspelling-heavy and number-heavy cases like 1252) to characterize
these failure modes before considering any prompt- or sampler-level fix —
not a production temperature change.
