# Stage 1 (CPU post-hoc repetition cleanup): stopped at the pre-metric guards

**Status: CLOSED as a negative result (decision 2026-10-14).** The GPU repetition constraint is not implemented in this
iteration. The stricter tandem rule (option 2 below) is **not** a research quality result; at most it is a possible
future product guardrail against runaway loops. The frozen rule, `metrics/rule_freeze.json` and `metrics/changed_clips.csv`
are kept as evidence.

**Stopped before metrics.** Rule v1 (`CLEANUP_RULE.md`, frozen; sha256 in `metrics/rule_freeze.json`) failed
both pre-registered guards in the dry run (`python3 -I scripts/run_cleanup.py --dry-run`). No metric was computed on
cleaned output. `run_cleanup.py` refuses the metric run while G1 fails. The original predictions are unchanged
(sha256 `d865008b…` checked before and after).

## G1 failed: the rule deletes a legitimate repetition in a reference

`G1hb5HugzVk_2-8`: "… covered with sauce and **mixed and mixed and mixed**." This is a 2-token unit repeated 3 times
in a row, in a human reference. Rule v1 would collapse it to "mixed". So "≥ 3 consecutive copies" is not a safe
definition of a loop.

## G2 failed: two changed clips are outside the 18 taxonomy loop clips

| Clip | In loop-18? | Before → after (words) | Why it is outside the 18 |
|---|---|---|---|
| `g2ur4BIuN0Q_8-3` | no | 50 → 6 ("I'm going to use a D, a D, … " → "I'm going to use a D,") | its reference repeats a 3-gram ("we're going to"), and the taxonomy rule only counts a loop when the reference has no repeated 3-gram |
| `Fzj3jz2Imf0_1-1` | no | 35 → 29 ("the brew, the brew, the brew, the brew," → "the brew,") | same reason |

Both are obvious degenerate loops. They count as "non-loop" only because of how the taxonomy defines a loop: it reads
the reference. A reference-free rule cannot respect that boundary. So "non-loop outputs byte-identical" cannot be
satisfied as stated by any rule that catches these two loops.

## Coverage: v1 touches only 3 of the 18 loop clips

Changed loop clips:
- `G095RWKQ39g_10-1` ("typical" × 30)
- `_FzvMVnR_aU_3-10` ("bounce back and forth," × 3)
- `fZM3IcM2Xs4_14_15_16-10` ("you're ready to go," × 6)

The other 15 loop clips are **clause-level near-repeats**, mostly two copies joined by "and" / "or". Examples:
"We're going to put black spots on top of it and then we're going to put black spots on top of it.", "You're going
to feel it in your face, or you're going to feel it in your face, or …". A tandem rule deliberately leaves these alone.

The pre-registered usefulness criterion needs the loop rate on the 18 to fall by half. With at most 3/18 clips
changed, the loop rate can fall by at most 17 %. **v1 therefore cannot meet the "useful" criterion, whatever its
metrics.**

## Why a broader rule is not an easy fix (counts from text only, no metrics)

| Repeated n-gram (anywhere in the text) | references (of 128) | loop-18 predictions | other 110 predictions |
|---|---|---|---|
| 4-gram | 7 | 18 | 16 |
| 5-gram | 3 | 18 | 8 |
| 6-gram | 1 | 16 | 3 |
| 8-gram | 0 | 11 | 2 |

Removing repeated clauses at any length that reaches most loop clips also touches human references or non-loop
predictions. Any threshold picked from this table would be fitted to these 128 clips.

## Options considered (decision: option 1, negative result accepted)

1. **Accept the negative result**: post-hoc cleanup is not a useful lightweight fix for the loop clips in this sample.
   Most "loops" are clause duplications, not runaway tandem repeats. Do not build the GPU decode-time constraint on
   the strength of Stage 1.
2. **v2 tandem rule, narrow by design.** Collapse only runs with ≥ 4 copies, or ≥ 3 copies with a unit of ≥ 3 tokens.
   This passes G1 by construction, but the threshold was chosen after seeing G1. Report it as a product guardrail
   against runaway loops (it would change ≈ 5 clips), not as a quality intervention, and redefine the evaluation strata
   as loop-18 / the 2 reference-excluded loops / the other 108.
3. **Go straight to the decode-time constraint** (`no_repeat_ngram_size`, GPU). It acts during beam search and can
   prevent clause duplication, which post-hoc text rules cannot fix safely. This contradicts the instruction to stop
   if Stage 1 is not useful, so it needs explicit approval.
