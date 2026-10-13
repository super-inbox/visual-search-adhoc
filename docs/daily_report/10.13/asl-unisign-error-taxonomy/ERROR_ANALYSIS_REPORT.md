# Uni-Sign error taxonomy on the frozen 128-clip How2Sign subset

> **Status: automated first-pass / weak-label analysis; manual ASL review pending.**
>
> This taxonomy is **not final**. Every category label in this report is an automatic weak label.
> `fingerspelling_candidate` and `named_entity_candidate` come from heuristics on the English reference text. They are
> **not** verified fingerspelling and **not** verified ASL linguistic behaviour. Visual categories are proxies computed
> from pose files; they are not observed video quality. A 45-clip manual review queue is prepared
> (`manual_review_queue.csv`, all rows `PENDING`). None of the findings below has been checked against the videos.
> No broad category of A_official shows a penalty that survives multiple-comparison correction (§3.2).

> **Follow-up hypothesis (high priority): the apparent >256-frame penalty may be a decoding-length cap effect.**
>
> - `long_clip_gt_256_frames` clips score −12.6 chrF below their length-matched controls, but the match is poor and
>   frame count is confounded with reference length (r = 0.86).
> - **No A_official prediction exceeds 50 words.**
> - **71 % of A_official predictions for references with ≥35 words are truncated** (no terminal punctuation; 15 / 21),
>   against 6.5 % for shorter references.
> - The eval decodes with `max_new_tokens=100`, so the long-clip penalty may come from the output length cap, not
>   from visual frame subsampling. This has not been tested yet. Follow-up A in §6 tests it.

Inputs: the restored P0-12 T4 / fp16 predictions (`../asl-p0-12-full128-fp16/predictions/`). The run setup is
described in `../asl-p0-12-full128-fp16/P0_12_RESULTS.md`.

## 0. Systems and roles

| System | Role in this analysis | Corpus BLEU-4 |
|---|---|---|
| **A_official** (official poses, official timing + crop) | **primary system** for the taxonomy | 9.13 |
| **C_ours_on_official_crop** (our extractor, same frames / crop / timing as A) | **paired diagnostic**: A vs C isolates the pose source | 8.61 |
| B_ours_5p39 (our extractor, original timing, full frame) | preprocessing control only | 5.47 |
| B_aspect (B + aspect / coordinate fix) | preprocessing control only | 5.80 |

## 1. Input verification (passed)

`scripts/verify_predictions.py` → `verification.json`:

| Check | Result |
|---|---|
| Exactly 128 lines / 128 parseable predictions per file | 4/4 files |
| Blank, unparseable, empty, duplicate, unknown or missing IDs | 0 in every file |
| Line order == `labels.test_p012_128` order == `manifest.csv` order | yes, all 4 files, line by line |
| Same clip at every line position across the 4 files (no shifted rows) | yes |
| Recomputed corpus BLEU-1..4 vs committed `p0_12_full128_fp16_results.csv` | identical (\|Δ\| < 0.0001) for all 4 systems |
| Recomputed ROUGE vs committed | within ±0.004 (the committed values are rounded to 2 decimals) |
| BLEURT | not recomputed (no BLEURT-20 checkpoint on this machine); committed values carried over |

Notes on the reproduction:

- BLEU uses sacrebleu 2.6 (13a tokenizer, cumulative BLEU-n). It matches the vendored sacrebleu 1.4.2 that Uni-Sign uses.
- ROUGE uses pltrdy `rouge==1.0.1` (ROUGE-L F, case-sensitive), the package Uni-Sign's How2Sign eval installs. The
  SLRT sentence-level ROUGE-L variant does **not** reproduce the committed values (it is about 2–3 points lower).
- **References.** The canonical reference is the encoding-fixed `manifest.csv` `reference_text`. This is the same
  text the committed scorer used. `labels.test_p012_128` differs on 3 clips, only by mojibake apostrophes (UTF-8
  bytes read as latin-1). Corpus BLEU and ROUGE are identical under both versions. Both strings are kept
  (`reference`, `reference_labels_test`).

## 2. Method (fixed before looking at scores)

**Per-sample metrics** (`inputs_128.jsonl`, all 4 systems):

- WER, with the same definition as the P0-12 scorer: lowercase whitespace tokens, punctuation kept.
- chrF and sentence BLEU (sacrebleu, exp smoothing).
- S / D / I edit counts on normalized tokens.
- chrF is the **primary per-sample metric**. Sentence BLEU is very skewed at this quality level (A median 5.6).
  Corpus BLEU-4 on 13–18 clips is unstable, so it is reported but not used to rank categories.

**Linguistic weak labels.** All come from the reference text, all are tagged `label_source=automatic,
status=candidate_unverified`, and each lists its evidence tokens:

- `fingerspelling_candidate` fires on any of: acronyms / all-caps words, single capital letters,
  letter-hyphen spellings, CamelCase names, capitalised non-initial words found in `/usr/share/dict/propernames`, or
  capitalised words not in the lowercase dictionary. Days, months, languages and holidays are excluded as
  *likely lexical signs*.
- `named_entity_candidate`: any capitalised non-sentence-initial word (except I / I'm / OK), plus acronyms.
- `number_candidate`: digits, cardinal number words, and ordinals third to twentieth. "one", "first" and "second" are
  excluded as too ambiguous. This explains most of the gap to the manifest heuristic (32 clips vs 15 here; the 15 are a
  subset of the manifest's 32). **This strict definition is the primary number analysis.** A broad definition that
  adds one / first / second (`number_candidate_broad_sensitivity`, n = 32) is reported only as a **secondary
  sensitivity analysis** (§3.7). It is excluded from the Bonferroni family and from the ranking.
- `negation_candidate`: not / no / never / none / … / *n't.
- `question_candidate`: "?" in the reference.

**Visual weak labels.** Proxies from the A_official pose PKLs plus `pose_diagnostics.csv`. The same flags computed on
the C poses are stored too.

- Absolute keypoint-missing rates are about 0 for every source (see the 10.06 report), so confidence flags are
  **relative** (quartiles).
- The flags are: `long_clip_gt_256_frames` (Uni-Sign randomly subsamples to 256 frames), `hand_out_of_frame` (≥50 %
  of a hand's keypoints outside the crop in ≥5 % of frames), `low_hand_conf` (bottom quartile of hand confidence),
  `hand_near_face` (wrist within 0.5 shoulder-widths of the nose in ≥5 % of frames; a self-occlusion proxy),
  `fast_hand_motion` (top quartile of wrist speed), `high_hand_jitter` (top quartile), `fast_signing_text_proxy`
  (manifest, words/sec ≥ p90), and `high_pose_disagreement_A_vs_C` (top quartile of A vs C hand keypoint error).
- **Motion blur and true occlusion cannot be observed from poses and are not labelled.**

**Error types per system and clip** (multi-label flags plus one primary type):

- omission: length ratio < 0.6.
- over-generation: length ratio > 1.6.
- hallucination candidate: < 20 % of predicted content words appear in the reference.
- repetition: the prediction repeats a word 3-gram that the reference does not.
- truncation candidate: no terminal punctuation.
- substitution-dominant: S ≥ D and S ≥ I.
- The primary type is assigned in priority order: repetition_loop (rep-3gram ratio ≥ 0.15) > omission > hallucination
  > over_generation > substitution. "Substitution" therefore means a fluent output with partial overlap but the wrong
  words.

**Category-specific checks:** number recall (numeric values found in the prediction), negation dropped / inserted,
question mark lost / inserted, and exact-token recall of named-entity / fingerspelling candidate tokens.

**Statistics:**

- **Length-matched control:** each category clip is paired with the nearest non-category clip by reference word count
  (ties broken by duration), with replacement. A match is flagged `poor_match` if the mean word gap is > 2 or fewer
  than 50 % of controls are unique.
- **Pose sensitivity:** the interaction (A − C chrF in the category) − (A − C chrF outside it).
- 95 % bootstrap CIs (10 000 resamples, seed 12345), plus Bonferroni CIs for the 16 tested categories
  (α = 0.05 / 16).
- **n < 10 is marked exploratory.** Every category has n ≥ 13. The sub-analyses with smaller cells (length bins,
  evidence types, per-category check counts) are marked inline.

## 3. Main findings

### 3.1 A_official error profile: mostly fluent, partly on-topic, wrong content

| A_official, n = 128 | count | | flag (multi-label) | rate |
|---|---|---|---|---|
| substitution (fluent, partial overlap, wrong words) | **67** | | hallucination candidate (< 20 % content supported) | 30.5 % |
| hallucination | 26 | | repetition (3-gram loop) | 26.6 % |
| repetition_loop | 18 | | truncation candidate | 17.2 % |
| omission | 13 | | omission (length < 0.6×) | 11.7 % |
| over_generation | 4 | | over-generation (length > 1.6×) | 8.6 % |

C_ours_on_official_crop has nearly the same profile (substitution 74, hallucination 20, repetition 16, omission 15,
over-generation 3). It assigns the same primary type as A on 99/128 clips. The B controls have far more
hallucinations (42 / 41 clips; 55 % / 53 % flag rate vs 30.5 % for A). This is consistent with P0-12: wrong timing / crop
produces content that is unrelated to the reference, not just worse wording.

### 3.2 No category shows a sentence-level penalty that survives length matching

A_official (chrF; `failure_matrix.csv` has every metric for all 4 systems):

| Category | group | n | BLEU-4 (corpus) | mean chrF [95% CI] | WER (pooled) | Δ chrF vs length-matched non-category [95% CI] | match quality |
|---|---|---|---|---|---|---|---|
| `ALL` | all | 128 | 9.13 | 30.1 [27.71, 32.47] | 0.910 | — | — |
| `fingerspelling_candidate` | linguistic | 15 | 10.29 | 30.6 [24.72, 36.74] | 0.971 | +3.19 [-5.07, 12.58] | ok |
| `named_entity_candidate` | linguistic | 17 | 8.06 | 28.9 [23.62, 34.62] | 0.907 | +2.70 [-6.04, 11.72] | ok |
| `number_candidate` | linguistic | 15 | 11.52 | 33.5 [26.39, 41.29] | 0.879 | -5.84 [-14.58, 5.17] | ok |
| `negation_candidate` | linguistic | 13 | 5.77 | 29.5 [24.21, 35.55] | 0.839 | -0.54 [-6.34, 5.28] | ok |
| `question_candidate` | linguistic | 13 | 11.73 | 30.4 [21.01, 40.26] | 0.965 | +8.21 [-2.84, 19.4] | ok |
| `long_clip_gt_256_frames` | visual | 36 | 6.55 | 27.7 [24.44, 31.11] | 0.874 | -12.55 [-16.99, -7.83] | **poor_match** (see 3.4) |
| `hand_out_of_frame_candidate` | visual | 18 | 7.25 | 29.1 [23.12, 35.72] | 0.939 | +2.23 [-4.27, 9.34] | ok |
| `low_hand_conf_candidate` | visual | 32 | 8.19 | 28.3 [23.85, 33.03] | 0.901 | -0.88 [-6.81, 5.18] | ok |
| `hand_near_face_candidate` | visual | 14 | 5.74 | 28.4 [22.13, 35.38] | 0.880 | -0.90 [-6.31, 5.81] | ok |
| `fast_hand_motion_candidate` | visual | 32 | 9.70 | 30.0 [25.79, 34.31] | 0.893 | -0.77 [-7.39, 5.68] | ok |
| `high_hand_jitter_candidate` | visual | 32 | 13.02 | 34.8 [29.87, 39.7] | 0.832 | +7.22 [0.14, 14.35] | ok |
| `fast_signing_text_proxy` | visual | 13 | 17.33 | 30.1 [20.03, 40.23] | 0.799 | +3.11 [-11.21, 16.75] | ok |
| `high_pose_disagreement_A_vs_C` | visual | 34 | 5.11 | 29.1 [24.98, 33.61] | 0.909 | +2.09 [-4.53, 8.78] | ok |
| `ref_length_short` (≤ tercile 1) | length | 45 | 10.15 | 30.0 [25.29, 34.8] | 1.068 | — | n/a (matching variable) |
| `ref_length_long` (> tercile 2) | length | 39 | 7.43 | 29.5 [26.13, 33.06] | 0.845 | — | n/a (matching variable) |
| `no_linguistic_candidate` | linguistic | 73 | 8.28 | 29.2 [26.27, 32.3] | 0.925 | -2.84 [-7.57, 1.79] | poor_match (pool < n) |

- **For A_official and C, no category's matched-control contrast excludes 0 after Bonferroni correction.** No broad
  category has a statistically significant penalty in this first pass. The only nominal 95 % hit for A is
  `high_hand_jitter` (+7.2), and it goes in the *unexpected* direction (jittery clips score better). Read it as noise or
  confounding, not a finding.
- **Disclosed exception, control system only:** for the B_aspect preprocessing control, strict `number_candidate`
  clips score −10.96 chrF below matched controls (Bonferroni CI [−19.3, −3.5]). The correction covers 16 categories
  per system, not the 16 × 4 system-category tests, and B_aspect is not a taxonomy baseline. This is not a finding
  about Uni-Sign under correct inputs.
- With n = 13–18 per linguistic category, the CIs are ±8–11 chrF wide. The design can only detect large
  sentence-level effects. "No detectable penalty" does **not** mean "no failure" (see 3.3).

### 3.3 Entity- and token-level failures that sentence metrics hide (rare-name / entity recovery failure)

A proper name is usually 1–2 tokens in a 20–40-word reference. Sentence chrF and BLEU barely move when the name is
wrong, so the category checks look at the tokens directly. The counts in the evidence-type and per-category checks
are small (n < 10 per evidence type), so this section is **exploratory**.

| Check (A_official) | Result | C_ours_on_official_crop |
|---|---|---|
| Rare-name / entity recovery: `fingerspelling_candidate` tokens that are **multi-letter rare names / acronyms / CamelCase** (Larew, Dias, Camelin, SunState, Kissimmee, Tadasana, Albondigas, Segundo, Whitley, ALVIN, DEDEUX, CV, Yu-Gi-Oh, …) | **2 / 21 recalled** ("Barbie", "Robert"); every rare out-of-dictionary name or acronym missed | 2 / 21 (same two) |
| `fingerspelling_candidate` tokens that are **single capital letters** (G, D, V, C) | 6 / 8 recalled. Caveat: one "D" hit is inside a degenerate "a D, a D, a D…" loop (`g2ur4BIuN0Q_8-3`) | 5 / 8 |
| Named-entity candidate tokens, mean per-clip recall (n = 17) | 0.18 | 0.18 |
| Number values recalled, mean per clip (n = 15) | 0.57 (8 clips full, 6 clips zero) | 0.53 (8 full, 7 zero) |
| Number inserted where the reference has none (n = 113) | 0 / 113 | 1 / 113 |
| Negation dropped, reference has a negation (n = 13) | **7 / 13** | 7 / 13 |
| Negation inserted, reference has none (n = 115) | 7 / 115 | 5 / 115 |
| Question mark lost, reference is a question (n = 13) | **10 / 13** | 11 / 13 |

Interpretation (hypotheses for the manual review, not conclusions):

- **Rare-name / entity recovery failure.** Rare proper names and acronyms are essentially never produced, and the
  result is the same for both pose sources. This is **not a verified fingerspelling failure**. Whether the signer
  fingerspelled these names has **not been checked**; they may have used a name sign, mouthing, or omitted the name.
  It becomes a fingerspelling result only if the video review confirms fingerspelling. Single capital letters are
  recovered more often.
- **Polarity is unreliable.** About half of the negated references come out affirmative. Insertions are rarer (6 %).
- **Question form is mostly lost.** In ASL the question is often marked by non-manual signals (brow, head). The
  pose-only input keeps face keypoints but not appearance. Whether the signer actually used a question NMM is
  unverified.
- Numbers (strict definition, primary) are recovered about half the time. When a number appears in the prediction it
  is never invented (0 / 113). See §3.7 for the broad-definition sensitivity check.

### 3.4 The largest sentence-level failure is long references, and it cannot be attributed to the >256-frame subsampling

- `long_clip_gt_256_frames` clips score −12.6 chrF below their matched controls. **The match is poor**, though: only 8
  unique controls, mean gap 11 reference words.
- Frame count and reference length correlate at r = 0.86. **No ≤256-frame clip has more than 33 reference words**,
  and every clip with ≥35 words has >256 frames. In this sample the two factors cannot be separated.
- Within the overlapping length bins (`taxonomy_summary.json → long_clip_vs_reference_length`) there is no consistent
  long-clip penalty:

  | Ref words | >256 n | >256 mean chrF | ≤256 n | ≤256 mean chrF |
  |---|---|---|---|---|
  | 15–24 | 4 ⚠ | 24.7 | 44 | 31.9 |
  | 25–34 | 10 | 34.8 | 4 ⚠ | 30.6 |

- **Follow-up hypothesis, not yet tested: a decoding-length cap effect.** No A_official prediction is longer than 50 words.
  71 % of predictions for references with ≥35 words (n = 21) end without terminal punctuation, against 6.5 % for
  shorter references. The mean length ratio for these long references is 0.67. This is consistent with the eval's
  `max_new_tokens=100` cutting the output off. For references of 50+ words (n = 10), A's mean chrF is 19.5.
  Follow-up A (§6) tests this directly.
- Primary error types also shift with length. For ≥35-word references (n = 21): substitution 6, omission 6,
  repetition_loop 6, hallucination 3. For shorter references, substitution dominates.

### 3.5 Pose-source sensitivity (A vs C): small and uniform, no category-specific effect survives

| Category | n | A BLEU-4 | C BLEU-4 | ΔBLEU-4 (C−A) | Δ chrF (C−A) [95% CI] | A−C chrF in cat / outside | interaction [95% CI] | Bonferroni CI |
|---|---|---|---|---|---|---|---|---|
| `ALL` | 128 | 9.13 | 8.61 | -0.52 | -1.46 [-2.27, -0.67] | — | — | — |
| `fingerspelling_candidate` | 15 | 10.29 | 10.22 | -0.07 | -0.50 [-2.48, 1.32] | +0.50 / +1.58 | -1.08 [-3.11, 1.13] | [-4.27, 2.31] |
| `named_entity_candidate` | 17 | 8.06 | 8.62 | +0.56 | -1.41 [-3.94, 0.82] | +1.41 / +1.47 | -0.06 [-2.46, 2.72] | [-3.55, 4.07] |
| `number_candidate` | 15 | 11.52 | 8.05 | -3.47 | -3.58 [-5.51, -1.47] | +3.58 / +1.18 | +2.40 [0.13, 4.54] | [-1.09, 5.57] |
| `negation_candidate` | 13 | 5.77 | 4.62 | -1.15 | -1.06 [-2.71, 0.58] | +1.06 / +1.50 | -0.45 [-2.3, 1.43] | [-3.32, 2.36] |
| `question_candidate` | 13 | 11.73 | 9.99 | -1.74 | -1.98 [-5.19, 0.73] | +1.98 / +1.40 | +0.58 [-2.31, 3.89] | [-3.44, 5.82] |
| `long_clip_gt_256_frames` | 36 | 6.55 | 5.97 | -0.58 | -0.64 [-1.99, 0.67] | +0.64 / +1.78 | -1.13 [-2.81, 0.55] | [-3.68, 1.42] |
| `hand_out_of_frame_candidate` | 18 | 7.25 | 7.04 | -0.21 | -0.00 [-1.12, 1.29] | +0.00 / +1.70 | -1.69 [-3.21, -0.27] | [-4.02, 0.36] |
| `low_hand_conf_candidate` | 32 | 8.19 | 8.37 | +0.18 | -0.83 [-2.27, 0.55] | +0.83 / +1.67 | -0.83 [-2.51, 0.85] | [-3.36, 1.98] |
| `hand_near_face_candidate` | 14 | 5.74 | 5.81 | +0.07 | -0.20 [-3.11, 2.45] | +0.20 / +1.61 | -1.42 [-4.18, 1.62] | [-5.4, 3.14] |
| `fast_hand_motion_candidate` | 32 | 9.70 | 9.72 | +0.02 | -0.88 [-2.6, 0.84] | +0.88 / +1.65 | -0.77 [-2.65, 1.12] | [-3.69, 2.21] |
| `high_hand_jitter_candidate` | 32 | 13.02 | 12.71 | -0.31 | -2.69 [-4.88, -0.57] | +2.69 / +1.05 | +1.64 [-0.63, 4.0] | [-1.74, 5.27] |
| `fast_signing_text_proxy` | 13 | 17.33 | 15.02 | -2.31 | -2.96 [-5.11, -1.11] | +2.96 / +1.29 | +1.68 [-0.4, 4.02] | [-1.33, 5.37] |
| `high_pose_disagreement_A_vs_C` | 34 | 5.11 | 4.47 | -0.64 | -2.44 [-4.42, -0.58] | +2.44 / +1.10 | +1.34 [-0.67, 3.53] | [-1.7, 4.59] |
| `ref_length_short` | 45 | 10.15 | 9.63 | -0.52 | -2.42 [-3.95, -1.0] | +2.42 / +0.94 | +1.48 [-0.21, 3.3] | [-1.06, 4.1] |
| `ref_length_long` | 39 | 7.43 | 6.85 | -0.58 | -0.44 [-1.76, 0.85] | +0.44 / +1.90 | -1.47 [-3.1, 0.13] | [-3.9, 0.99] |
| `no_linguistic_candidate` | 73 | 8.28 | 8.82 | +0.54 | -1.09 [-2.23, -0.0] | +1.09 / +1.95 | -0.85 [-2.42, 0.73] | [-3.24, 1.57] |

- **Overall:** official poses beat ours by +1.46 chrF [0.67, 2.28] on the same frames. This agrees with the
  +0.52 BLEU-4 measured in P0-12.
- **No category interaction excludes 0 after Bonferroni correction.** There is no evidence that any linguistic or
  visual category depends specifically on the pose extractor.
- Two nominal 95 % signals, to be treated as hypotheses only:
  - **Numbers (strict):** the A advantage grows to +3.6 chrF and +3.5 BLEU-4 (interaction +2.4 [0.13, 4.54]). This is
    plausible because number handshapes need fine finger detail, but the per-clip recall difference is small (0.57 vs
    0.53), and the signal **does not hold under the broad definition** (§3.7: interaction +0.86 [−0.77, 2.51]).
  - **Hand out of frame:** the A−C gap disappears (interaction −1.7 [−3.21, −0.27]). One possible reading: when the
    hand leaves the crop, both extractors lose the same information.
- Per-clip swings are much larger than the mean. 25 clips favour A by >5 chrF and 6 favour C by >5. Because the
  >256-frame clips are randomly subsampled and each system was run once, part of this swing is probably sampling noise.
  P0-12 did not measure seed-to-seed variance.

### 3.6 Preprocessing controls (B): short and question clips suffer most from wrong timing / crop

| Category | n | Δ chrF B_ours_5p39 − A [95% CI] | Δ chrF B_aspect − A [95% CI] |
|---|---|---|---|
| `ALL` | 128 | -8.01 [-10.26, -5.89] | -7.37 [-9.62, -5.25] |
| `ref_length_short` | 45 | -11.51 [-16.38, -6.95] | -10.85 [-15.83, -6.16] |
| `ref_length_long` | 39 | -4.68 [-7.2, -2.32] | -3.37 [-5.84, -1.06] |
| `question_candidate` | 13 | -16.48 [-26.42, -7.33] | -16.77 [-26.57, -7.62] |
| `named_entity_candidate` | 17 | -11.51 [-16.7, -6.99] | -9.08 [-13.91, -4.48] |
| `fingerspelling_candidate` | 15 | -10.04 [-16.4, -4.32] | -7.25 [-13.14, -1.58] |
| `number_candidate` | 15 | -8.85 [-16.12, -3.11] | -9.58 [-17.03, -3.95] |
| `long_clip_gt_256_frames` | 36 | -4.63 [-7.39, -2.09] | -3.46 [-6.01, -1.02] |

- The B penalty is about 2.5× larger on short references than on long ones. This fits the 10.06 segment-IoU
  finding: a fixed timing offset removes a larger share of a short clip.
- Question clips (mostly short) show the largest drop. These are preprocessing effects. They are kept as context and
  are not used as the taxonomy baseline.

### 3.7 Secondary sensitivity analysis: broad number definition (not part of the primary result)

The broad definition is the strict one plus the ambiguous forms one / first / second. It covers 32 clips and matches
the manifest heuristic's count. It is shown only to check how much the strict-number conclusions depend on the
definition. It is outside the Bonferroni family and the ranking.

| System | strict `number_candidate` (primary, n = 15): mean chrF / matched Δ chrF [95% CI] | broad sensitivity (n = 32): mean chrF / matched Δ chrF [95% CI] |
|---|---|---|
| A_official | 33.5 / −5.84 [−14.58, 5.17] | 34.8 / +0.42 [−6.14, 7.29] |
| C_ours_on_official_crop | 29.9 / −8.11 [−15.81, 2.15] | 32.7 / −2.45 [−8.46, 4.00] |

| Check | strict (primary) | broad (sensitivity) |
|---|---|---|
| A_official number recall (mean per clip) | 0.57 | 0.54 (counts one / first / second as values) |
| C − A chrF | −3.58 [−5.51, −1.47] | −2.10 [−3.47, −0.76] |
| A−C pose-sensitivity interaction | +2.40 [0.13, 4.54] | +0.86 [−0.77, 2.51] |

Neither definition shows a significant number penalty for A_official. The nominal number-specific pose-source signal
under the strict definition shrinks and loses nominal significance under the broad definition, which further supports
treating it as a hypothesis only.

## 4. Provisional ranking: where Uni-Sign (A_official) fails

The ranking is based on the automated first-pass / weak-label analysis only. It is **not final** and should be
revisited after the manual review.

1. **Rare-name / entity recovery failure** (fingerspelling / NE *candidates*): 2 / 21 rare names recovered, identical
   with both pose sources. This is the cleanest token-level signal. It is **not a verified fingerspelling failure**:
   whether fingerspelling occurred is unverified until the video review (Follow-up B).
2. **Long references / possible decoding-cap effect** (hypothesis): truncation for ≥35-word references, and the lowest
   chrF for 50+ word references. This is possibly an **inference-configuration** issue (`max_new_tokens=100`) that
   can be tested without retraining (Follow-up A). The frame-subsampling effect cannot be separated from length in
   this sample.
3. **Polarity and question form**: negation dropped 7/13 and question marks lost 10/13. Small n; needs review of
   whether the signer marked negation or the question manually or non-manually.
4. **General content substitution / hallucination** on ordinary clips (substitution 67, hallucination 26,
   repetition 18 of 128). This is the bulk of the error mass, and it is not concentrated in any category tested here.
5. **Numbers** (strict definition): about 50 % recall. The only nominal hint of pose-source sensitivity does not
   survive Bonferroni correction and does not hold under the broad definition (§3.7).

Visual proxies (out-of-frame, near-face, low confidence, fast motion, jitter) show **no** detectable effect on
A_official at this n. The pose-level confidence measures carry little signal, because missing rates are about 0
everywhere.

## 5. Limitations

1. **Automatic weak labels only. No manual review has been done.** Every category label can be wrong in either
   direction. Some NE candidates are title-case words ("Ready", "Studio", "Glider"). Some "names" may have been signed
   with a name sign rather than fingerspelled.
2. **Small categories (n = 13–18).** The CIs are wide, and 16 categories × several contrasts raise the risk of false
   positives. Bonferroni-adjusted CIs are reported. No A_official or C matched-control or pose-interaction contrast
   survives them. The single exception is in the B_aspect control (§3.2).
3. **Confounding.** Frame count, reference length and the decoding cap are confounded (r = 0.86). Visual proxies come
   from poses, not from video quality. Blur and occlusion are not measured.
4. **Single run per system** at T4 / fp16. The 36 clips over 256 frames are randomly subsampled, so per-clip
   differences include run-to-run noise that has not been quantified.
5. Error-type rules are simple token heuristics. The primary-type thresholds (0.6 / 1.6 length ratio, 20 % content
   precision, 0.15 repeated-3gram ratio) were chosen a priori and not tuned. `substitution_dominant` is true for about
   80 % of clips and is not discriminative on its own.
6. BLEURT is not recomputed. Category-level ROUGE is not reported, because the corpus ROUGE path needs the pltrdy
   package.

## 6. Next steps (two immediate follow-ups)

**A. Re-decode A_official with a higher `max_new_tokens` and evaluate the long-reference subset.**

- Keep everything else identical: A_official poses, checkpoint, T4 / fp16, beams = 4, batch 8, seed 42. Change only
  `max_new_tokens`, for example 100 → 200 (and 300 if it is still capped).
- Evaluate (i) the 21 clips with ≥35 reference words, (ii) the 36 >256-frame clips, and (iii) all 128 clips. Report
  truncation rate, maximum prediction length, length ratio, chrF and BLEU-4, and the matched-control contrast for
  `long_clip_gt_256_frames`.
- If truncation drops and the long-reference gap closes, the >256-frame "penalty" is mostly a decoding-cap effect.
  If it persists with uncapped output, frame subsampling or long-context modelling remain candidates.
- Because the >256-frame clips are randomly subsampled, also re-run the current cap with 2 extra seeds to bound
  run-to-run noise.

**B. Manually review the 45 queued clips** (`manual_review_queue.csv`) against the videos and record:

- verified fingerspelling (yes / no / partial; which tokens),
- number signing (how each number was signed; number error type),
- named entities (fingerspelled, name sign, or omitted),
- negation and question non-manual markers (headshake, brow raise / furrow, head tilt),
- spatial relations (classifier / location use that the translation should express),
- occlusion and other visual issues (hands out of frame, hand-over-face, blur),
- the true error type for A_official (and C where they differ).

Only after B can the fingerspelling and entity results be stated as fingerspelling results, and the weak labels be
replaced or calibrated.

## 7. Manual review queue (prepared, not started)

`manual_review_queue.csv` holds 45 clips, all `review_status = PENDING`, with empty reviewer fields. They are
stratified as follows (some clips meet more than one reason):

| Stratum | Clips |
|---|---|
| fingerspelling candidates (lowest A chrF first) | 10 |
| named-entity candidates without a fingerspelling flag | 5 |
| number candidates | 7 |
| negation flips | 9 |
| question candidates | 6 |
| largest \|A − C\| per-clip disagreement | 8 |
| visual proxies | 18 |
| A_official best clips | 2 |
| random no-candidate controls | 4 |

Each row has the exact reference, the A and C predictions, auto labels with evidence, metrics, the local video path, and
blank fields for: `verified_fingerspelling`, `verified_named_entity`, `verified_number_signing`,
`verified_negation_nmm`, `verified_question_nmm`, `spatial_relations_notes`, `occlusion_observed`,
`visual_issue_observed`, `manual_primary_error_type` and `manual_notes`. Every row also carries
`analysis_status` = "automated first-pass / weak-label analysis; manual ASL review pending".

## 8. Files

| File | Content |
|---|---|
| `verification.json` | Prediction-file verification (structure, ordering, metric reproduction) |
| `inputs_128.jsonl` | 128 rows: exact references (canonical + labels.test), exact predictions for the 4 systems, per-sample WER / chrF / sentence BLEU / S-D-I, manifest heuristics, pose features (A / B / C diagnostics + PKL-derived A / C features), A-vs-C keypoint agreement, segment alignment |
| `error_taxonomy_annotations.jsonl` | Per clip: weak labels with evidence (`automatic`, `candidate_unverified`), visual flags from C poses, and per-system error analysis (primary type, flags, length ratio, content precision / recall, category checks) |
| `failure_matrix.csv` | 17 primary categories + 1 secondary sensitivity category (`number_candidate_broad_sensitivity`, group `sensitivity_secondary`) × 4 systems: corpus BLEU-4 / chrF, pooled WER, mean chrF with CI, mean sentence BLEU, error-type rates, primary-type counts, category checks, matched-control Δ with 95 % / Bonferroni CI and match quality, paired Δ vs A, A−C pose-sensitivity interaction |
| `manual_review_queue.csv` | 45-clip review queue (PENDING) |
| `representative_failures.md` | Auto-selected examples per A_official error type, per linguistic category, and largest A / C disagreements (verbatim text) |
| `taxonomy_summary.json` | Label counts, thresholds, error-type distributions, long-clip stratification, decoding-cap check, entity-token recall by evidence type |
| `scripts/` | `common.py`, `verify_predictions.py`, `build_inputs.py`, `taxonomy.py`, `validate_outputs.py`, `run_all.sh` (CPU only, about 15 s) |

Reproduce: `pip install --target <dir> rouge==1.0.1 && ROUGE_PYLIB=<dir> bash scripts/run_all.sh`.
