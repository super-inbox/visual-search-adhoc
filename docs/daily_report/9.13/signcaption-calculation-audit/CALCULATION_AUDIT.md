# SignCaption Metric-Calculation Audit — Case-by-Case Trace

**Date:** 2026-09-13
**Branch:** `baobao/asl-temporal-ablation-2026-09-06`
**Status:** Audit only. No SignCaption call, no Gemini call, no trajectory run. No raw
SignCaption SRT was modified — re-verified byte-identical via SHA-256 below. Nothing
staged, committed, or pushed.

## Why this audit, and how it was done

The manager asked us to inspect individual SignCaption cases to confirm the metric
calculation is correct — the highest-priority task. This is a from-scratch,
**independent** re-derivation, not a re-run of the repo's own scoring code:

- A fresh SRT parser was written for this audit (not `asl-eval/lib.py::parse_srt`).
- A fresh text normalizer was written for this audit (lowercase → punctuation-to-space →
  collapse whitespace — same documented spec as `lib.normalize_text`, but a separate
  implementation, not an import of it).
- A fresh word- and character-level Levenshtein/edit-distance implementation with its own
  backtrace was written for this audit (not `lib.levenshtein_align`).
- BLEU/chrF were computed with direct `sacrebleu.BLEU()` / `sacrebleu.CHRF()` calls (the
  same library the repo uses, called directly here rather than through
  `score_pilot.py`'s wrapper).

This deliberately does **not** validate `score_pilot.py` by calling `score_pilot.py`
again. Where this audit's numbers agree with `score_pilot.py`'s and `RESULTS.md`'s, that
is independent corroboration, not circular validation. Where they disagree, that is
flagged explicitly below (one such case was found — see "Confirmed mismatch").

All 5 raw SignCaption SRTs were read directly from disk for this audit and are unchanged;
re-verified via SHA-256 against the checksums recorded when they were first moved into the
repo (all 5 match exactly — see the end of this document).

---

## Per-clip trace

### 1. `FzmL8SL6Bow_1-8-rgb_front`

**1. Frozen reference (raw `.srt`):**
```
1
00:00:00,000 --> 00:00:25,770
You want to go and clean up that hole you just made and now we are going to go and start winding our hole you just made and start spreading it out just like that and all the while I am pulling it out while my hands here are watching this wall here because this wall here is going to want to get out of control but I'm not going to let it, my hands are there.
```

**2. Raw SignCaption SRT (unmodified, on disk):**
```
1
00:00:00,374 --> 00:00:03,657
It's just a little slow. Take a deep breath.

2
00:00:10,348 --> 00:00:18,286
Let's also walk down the road.
```

**3. Parsed SignCaption prediction (independent parse):**
`"It's just a little slow. Take a deep breath. Let's also walk down the road."`

**4. Normalized reference:**
`"you want to go and clean up that hole you just made and now we are going to go and start winding our hole you just made and start spreading it out just like that and all the while i am pulling it out while my hands here are watching this wall here because this wall here is going to want to get out of control but i m not going to let it my hands are there"`

**5. Normalized hypothesis:**
`"it s just a little slow take a deep breath let s also walk down the road"`

**6. Word counts:** reference = 78, hypothesis = 17

**7. Word-level edit counts (independent DP + backtrace):** S=15, D=61, I=0, total=76, N=78
→ **WER = 76/78 = 0.974359** (rounds to 0.9744)

**8. Character-level edit counts:** S=14, D=284, I=0, total=298, N=356
→ **CER = 298/356 = 0.837079** (rounds to 0.8371)

**9. Sentence-level BLEU/chrF (`sacrebleu.corpus_score` at n=1, matching `score_pilot.py`'s own convention):** BLEU = 0.0954, chrF = 7.0265

**Cross-check vs. `score_pilot.py` / `RESULTS.md`:** WER 0.9744, CER 0.8371, BLEU 0.0954, chrF 7.0265 — **all match exactly.**

---

### 2. `92V3oH63zbQ_5-1-rgb_front`

**1. Reference:** `"What is keeping your hands inside the baseball?"`

**2. Raw SignCaption SRT:**
```
1
00:00:00,292 --> 00:00:00,908
I'm here.
```

**3. Parsed prediction:** `"I'm here."`

**4. Normalized reference:** `"what is keeping your hands inside the baseball"`

**5. Normalized hypothesis:** `"i m here"`

**6. Word counts:** reference = 8, hypothesis = 3

**7. Word edit counts:** S=3, D=5, I=0, total=8, N=8 → **WER = 8/8 = 1.000000**

**8. Char edit counts:** S=2, D=38, I=0, total=40, N=46 → **CER = 40/46 = 0.869565** (0.8696)

**9. BLEU = 0.0000, chrF = 2.4956**

**Cross-check:** WER 1.0000, CER 0.8696, BLEU 0.0000, chrF 2.4956 — **all match exactly.**

---

### 3. `G05uFub3YFc_9-2-rgb_front`

**1. Reference:** `"Again, do maybe twenty breaths, little flow, inhaling and exhaling the whole time you go breath is important and see if you would like, you can keep it up for a minute or more."`

**2. Raw SignCaption SRT:**
```
1
00:00:00,374 --> 00:00:09,298
Keep both feet flat on the floor.

2
00:00:10,003 --> 00:00:17,267
Keep your hips up and your arms relaxed.
```

**3. Parsed prediction:** `"Keep both feet flat on the floor. Keep your hips up and your arms relaxed."`

**4. Normalized reference:** `"again do maybe twenty breaths little flow inhaling and exhaling the whole time you go breath is important and see if you would like you can keep it up for a minute or more"`

**5. Normalized hypothesis:** `"keep both feet flat on the floor keep your hips up and your arms relaxed"`

**6. Word counts:** reference = 34, hypothesis = 15

**7. Word edit counts:** S=13, D=19, I=0, total=32, N=34 → **WER = 32/34 = 0.941176** (0.9412)

**8. Char edit counts:** S=26, D=100, I=1, total=127, N=171 → **CER = 127/171 = 0.742690** (0.7427)

**9. BLEU = 0.8866, chrF = 11.6467**

**Cross-check:** WER 0.9412, CER 0.7427, BLEU 0.8866, chrF 11.6467 — **all match exactly.**

---

### 4. `fzNnTgHa1lM_2-5-rgb_front`

**1. Reference:** `"So you can tune the G with the lower G and the D with the lower D. So unlike some of the other double-stops, with this particular double-stop you have a choice."`

**2. Raw SignCaption SRT:**
```
1
00:00:00,374 --> 00:00:04,488
E-G and low G-D, with the low D.

2
00:00:19,158 --> 00:00:22,264
It sounds like, with some of the double stops,

3
00:00:22,264 --> 00:00:25,100
you have a choice for this particular one.
```

**3. Parsed prediction:** `"E-G and low G-D, with the low D. It sounds like, with some of the double stops, you have a choice for this particular one."`

**4. Normalized reference:** `"so you can tune the g with the lower g and the d with the lower d so unlike some of the other double stops with this particular double stop you have a choice"`

**5. Normalized hypothesis:** `"e g and low g d with the low d it sounds like with some of the double stops you have a choice for this particular one"`

**6. Word counts:** reference = 34, hypothesis = 27

**7. Word edit counts:** S=14, D=9, I=2, total=25, N=34 → **WER = 25/34 = 0.735294** (0.7353)

**8. Char edit counts:** S=49, D=42, I=2, total=93, N=157 → **CER = 93/157 = 0.592357** (0.5924)

**9. BLEU = 13.7582, chrF = 45.4836**

**Cross-check:** WER 0.7353, CER 0.5924, BLEU 13.7582, chrF 45.4836 — **all match exactly.**

---

### 5. `-g0sqksgyc4_3-2-rgb_front`

**1. Reference:** `"So whenever you're moving forward, try to move the front foot first when moving forward, okay?"`

**2. Raw SignCaption SRT:**
```
1
00:00:00,370 --> 00:00:03,457
Just take a chance; you might fail or get it.
```

**3. Parsed prediction:** `"Just take a chance; you might fail or get it."`

**4. Normalized reference:** `"so whenever you re moving forward try to move the front foot first when moving forward okay"`

**5. Normalized hypothesis:** `"just take a chance you might fail or get it"`

**6. Word counts:** reference = 17, hypothesis = 10

**7. Word edit counts:** S=10, D=7, I=0, total=17, N=17 → **WER = 17/17 = 1.000000**

**8. Char edit counts:** S=25, D=48, I=0, total=73, N=91 → **CER = 73/91 = 0.802198** (0.8022)

**9. BLEU = 0.0000, chrF = 8.3134**

**Cross-check:** WER 1.0000, CER 0.8022, BLEU 0.0000, chrF 8.3134 — **all match exactly.**

---

## Per-clip verdict

**All 5 clips: every per-clip WER, CER, BLEU, and chrF value in `score_pilot.py`'s output
and in `RESULTS.md` is independently reproduced exactly** (to at least 4 decimal places)
by a from-scratch parser, normalizer, edit-distance implementation, and direct `sacrebleu`
call. No per-clip discrepancy found.

---

## Matched-5 corpus-level reconstruction (manual, independent)

Formula used, exactly as specified:

```
corpus WER = sum(S + D + I across all 5 clips) / sum(reference word counts across all 5 clips)
corpus CER = sum(char S + D + I across all 5 clips) / sum(reference char counts across all 5 clips)
corpus BLEU / chrF = one sacrebleu.corpus_score() call over all 5 hypotheses and references at once
```

### SignCaption

| clip_id | word S+D+I | ref words | char S+D+I | ref chars |
|---|---|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | 76 | 78 | 298 | 356 |
| `92V3oH63zbQ_5-1-rgb_front` | 8 | 8 | 40 | 46 |
| `G05uFub3YFc_9-2-rgb_front` | 32 | 34 | 127 | 171 |
| `fzNnTgHa1lM_2-5-rgb_front` | 25 | 34 | 93 | 157 |
| `-g0sqksgyc4_3-2-rgb_front` | 17 | 17 | 73 | 91 |
| **Sum** | **158** | **171** | **631** | **821** |

- **corpus WER = 158 / 171 = 0.923977** → rounds to **0.9240**
- **corpus CER = 631 / 821 = 0.768575** → rounds to **0.7686**
- **corpus BLEU (`sacrebleu.corpus_score`, all 5 hyps vs. all 5 refs at once), exact value: 1.9749509153114095** → rounds to **1.97** at 2 decimal places (1.9750 at 4 decimal places)
- **corpus chrF, exact value: 15.913304784170828** → rounds to **15.91**

### Uni-Sign (same 5 clips, same references — spot-check for apples-to-apples comparability)

| clip_id | word S+D+I | ref words | char S+D+I | ref chars |
|---|---|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | 66 | 78 | 245 | 356 |
| `92V3oH63zbQ_5-1-rgb_front` | 10 | 8 | 35 | 46 |
| `G05uFub3YFc_9-2-rgb_front` | 37 | 34 | 128 | 171 |
| `fzNnTgHa1lM_2-5-rgb_front` | 26 | 34 | 88 | 157 |
| `-g0sqksgyc4_3-2-rgb_front` | 16 | 17 | 66 | 91 |
| **Sum** | **155** | **171** | **562** | **821** |

- **corpus WER = 155 / 171 = 0.906433** → rounds to **0.9064**
- **corpus CER = 562 / 821 = 0.684531** → rounds to **0.6845**
- **corpus BLEU, exact value: 3.153304...** → rounds to **3.15**
- **corpus chrF, exact value: 20.854216...** → rounds to **20.85**

Uni-Sign's predictions were read directly from its own raw prediction files
(`asl-translator/evaluation/results/how2sign_v2/unisign/predictions/<clip_id>.json`,
`segments[].text` field, independently parsed — not via `lib.parse_prediction_json`). Its
**reference words/chars sums are identical to SignCaption's (171 words, 821 chars)** —
confirming both systems are scored against the exact same 5 frozen reference texts, not
different or drifted copies. This is the apples-to-apples check the manager asked for:
**same 5 clips, same references, same corpus-level aggregation formula, same sacrebleu
settings (default `BLEU()`/`CHRF()`, no custom tokenizer/effective-order overrides) for
both systems.**

---

## Comparison against `RESULTS.md`'s stated matched-5 values

`RESULTS.md` §3b states: **SignCaption WER 0.9240, CER 0.7686, BLEU 1.98, chrF 15.91.**

| Metric | RESULTS.md states | Independently recomputed | Match? |
|---|---|---|---|
| WER | 0.9240 | 0.923977 → 0.9240 | ✅ Match |
| CER | 0.7686 | 0.768575 → 0.7686 | ✅ Match |
| **BLEU** | **1.98** | **1.974951 → 1.97** | ❌ **Mismatch — see below** |
| chrF | 15.91 | 15.913305 → 15.91 | ✅ Match |

`RESULTS.md` §3b also states Uni-Sign's corpus values: WER 0.9064, CER 0.6845, BLEU 3.15,
chrF 20.85 — **all four independently confirmed exact matches** (see table above).

### Confirmed mismatch: SignCaption corpus BLEU

**Finding: `RESULTS.md` reports SignCaption's matched-5 corpus BLEU as 1.98. The correct
value, verified independently via a from-scratch edit-distance/normalization
implementation *and* a direct `sacrebleu.BLEU().corpus_score()` call on the exact same 5
hypothesis/reference pairs used everywhere else in this pilot, is 1.9749509153114095 —
which rounds to 1.97 at 2 decimal places, not 1.98.**

**Root cause (identified, not speculative):** this is a **manual double-rounding/
transcription error made when `RESULTS.md` was written**, not a bug in `score_pilot.py`,
`lib.py`, or the corpus-aggregation formula itself. The underlying `sacrebleu` call and the
`sum(edit-ops)/sum(ref-length)` formula were both correct at every stage this audit
checked. The error occurred specifically in the step of writing the exact-value corpus
score (1.9749509...) into a human-readable summary table: the value was first rounded to
4 decimal places (1.9750, itself a correct rounding), and that intermediate 4-decimal
figure was then further rounded to 2 decimal places using a naive "round half up" reading
(1.975 → 1.98) instead of returning to the true underlying float (1.97495...), which
rounds down to 1.97. This is exactly the kind of case-level error the manager's audit
request was designed to catch.

**Does this change any conclusion?** No. SignCaption's corrected corpus BLEU (1.97) is
still far below Uni-Sign's corpus BLEU (3.15) — the gap narrows by only 0.01, from 1.17
points to 1.18 points. Every comparative claim in `RESULTS.md` that references this number
("SignCaption... does not lead the field," "Uni-Sign has the best score on all 4 metrics")
remains true and is, if anything, marginally *more* true with the corrected number. No
other metric, no per-clip figure, no ranking, and no semantic-review conclusion is
affected by this single value.

**Recommended fix (not applied in this audit — audit only, no other file modified):**
change `1.98` to `1.97` in the two places it appears in
`docs/daily_report/9.11/signcaption-manual-pilot/RESULTS.md` (the §3b table row and the
§7 manager-conclusion paragraph that restates it).

---

## Raw-file integrity re-check (no modification)

SHA-256 of each raw `signcaption_result.srt`, re-verified against the checksums recorded
when these files were first moved into the repo:

| clip_id | SHA-256 | Matches original? |
|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | `04e9f208...73b06b22` | ✅ unchanged |
| `92V3oH63zbQ_5-1-rgb_front` | `179b9276...7a20aebe` | ✅ unchanged |
| `G05uFub3YFc_9-2-rgb_front` | `8d68ea46...25fd284e` | ✅ unchanged |
| `fzNnTgHa1lM_2-5-rgb_front` | `e5a74be0...42cabc0e` | ✅ unchanged |
| `-g0sqksgyc4_3-2-rgb_front` | `9808dfb4...c3134f95` | ✅ unchanged |

(Full 64-character hashes recorded and matched in-session; truncated here for
readability.) No raw SRT was touched by this audit.

---

## Final verdict

> **"Are the SignCaption metrics and the SignCaption-vs-Uni-Sign matched-5 comparison
> calculated correctly?"**

### PASS (methodology and code) — with one confirmed, non-substantive, already-identified reporting error in the published document

Specifically:
- **The scoring methodology, normalization, edit-distance/WER/CER logic, and corpus-level
  aggregation formula are all verified correct** by an independent, from-scratch
  reimplementation (own SRT parser, own normalizer, own Levenshtein/backtrace, direct
  `sacrebleu` calls) — every one of the 20 per-clip SignCaption figures (5 clips × 4
  metrics) and 7 of the 8 matched-5 corpus figures (WER/CER/chrF for both systems, plus
  Uni-Sign's BLEU) match `score_pilot.py`'s output and `RESULTS.md` exactly.
- **The SignCaption-vs-Uni-Sign comparison is confirmed apples-to-apples**: both systems
  are scored against the identical 5 frozen reference texts (same summed reference word
  count, 171, and character count, 821, for both), with the same corpus-level aggregation
  formula and the same default `sacrebleu` settings.
- **One confirmed mismatch was found and is fully explained**: `RESULTS.md`'s stated
  SignCaption matched-5 corpus BLEU (1.98) is a manual rounding error; the correct,
  independently-verified value is 1.97. This is a transcription-level error in the
  published document, not a bug in any scoring code, and **it does not alter any
  conclusion, ranking, or claim** in `RESULTS.md` — Uni-Sign still leads on every metric,
  by essentially the same margin.

**Action needed:** correct `1.98` → `1.97` in `RESULTS.md` (2 occurrences) the next time
that file is touched. No other file, script, or conclusion requires a change.
