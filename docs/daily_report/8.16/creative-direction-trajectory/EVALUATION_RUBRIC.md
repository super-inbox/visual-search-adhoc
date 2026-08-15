# EVALUATION_RUBRIC.md — Creative Direction quality rubric

Used to score every trajectory in `trajectory_cases.jsonl` and to fill `paired_evaluation.csv`.
There is deliberately no single aggregate score: Creative Direction quality is multi-dimensional,
and collapsing it to one number hides exactly the tradeoffs (diversity vs. specificity,
preference fit vs. brief integrity) this experiment exists to surface. Individual dimension
scores are the primary evidence; `winner`/`confidence` in `paired_evaluation.csv` is a holistic
call made *from* those scores, not a replacement for them.

## Scale

All eight dimensions use the same 1–5 scale:

| Score | Anchor |
|---|---|
| 1 | Poor — actively unusable; a designer would discard the direction set and start over. |
| 2 | Weak — usable only after significant rework; the dimension's core requirement is largely unmet. |
| 3 | Usable — meets the bar for the dimension; a designer could work from it as-is, with minor gaps. |
| 4 | Strong — clearly good on this dimension, with only small room for improvement. |
| 5 | Excellent — a designer would point to this as a model example for the dimension. |

## Dimensions

### 1. Relevance
Does the direction set answer the user's actual task (product, audience, format, constraints — not
a generic version of the brief)?
- 1: ignores the brief's product/audience/format entirely.
- 3: addresses the brief's core ask but misses secondary details (e.g. forgets one named constraint).
- 5: every direction is clearly built from this specific brief; no detail in the brief is ignored.

### 2. Direction diversity
Are the returned directions genuinely different visual territories, or wording variants of the same
idea?
- 1: all directions are the same idea restated (same composition/palette/type logic, different adjectives).
- 3: directions differ on at least one real axis (e.g. palette) but share others (e.g. same layout logic).
- 5: directions differ on multiple independent axes (composition, palette, typography, material,
  imagery source) such that a viewer could not mistake one direction's visual output for another's.

### 3. Specificity
Does each direction give concrete visual guidance, not adjectives alone? Look for checkable detail in:
composition, typography, color, materials, imagery, layout, mood, references.
- 1: only mood adjectives ("modern," "premium," "clean") with no concrete visual instruction.
- 3: at least 3 of the 7 concrete categories above are specified per direction.
- 5: most/all categories specified with enough precision that two different designers executing the
  same direction would converge on visually similar output.

### 4. Actionability
Could a designer or downstream generation workflow actually execute this direction today?
- 1: direction is abstract/conceptual only, no executable instruction.
- 3: a competent designer could start from it, filling in some gaps themselves.
- 5: direction is close to prompt/brief-ready with minimal interpretation required.

### 5. Preference fit *(personalized trajectories only; baseline scored N/A)*
Does the result observably reflect the supplied preference profile's evidence and structured
preference fields — not merely name-check them?
- 1: preference profile is not reflected in the output at all (or contradicted).
- 3: preference is reflected in surface language (styleTags, mood words) but not in concrete
  composition/material/color choices.
- 5: preference's structured fields (color, typography, density, etc.) are traceable in the actual
  `promptModifier` content of most/all directions.

### 6. Visual distinctiveness
Would each direction plausibly render as a visibly different image? (Related to diversity, but scored
on the *output*, not the *labels* — a set can have diverse-sounding titles yet converge visually.)
- 1: all 3 directions would plausibly render near-identically.
- 3: at least 2 of 3 directions would plausibly render distinguishably.
- 5: all 3 directions would plausibly render as clearly separate images to a viewer with no labels.

### 7. Redundancy / genericness *(inverse-scored: higher = less generic)*
Penalize outputs that collapse into vague, repeated language ("modern," "minimal," "premium,"
"clean") without concrete differentiation.
- 1: direction set is dominated by generic adjectives with no differentiating detail.
- 3: some generic language present but paired with concrete differentiating detail per direction.
- 5: no reliance on generic mood adjectives to do differentiating work; all differentiation is concrete.

### 8. Brief integrity
Does personalization remain compatible with the user's actual design task? Preference should sharpen
the brief, not override it.
- 1: personalized output actively contradicts a stated brief requirement (audience, format, hard
  constraint) to satisfy the preference profile instead.
- 3: personalized output is compatible with the brief but doesn't actively reinforce it.
- 5: personalized output satisfies both the preference profile and every stated brief requirement,
  and the two reinforce rather than compete.

## How dimensions map to failure modes (see `FINDINGS.md` §Preference)

| Failure mode | Diagnostic dimension pattern |
|---|---|
| Preference helps | preference_fit high, brief_integrity stays high, diversity/distinctiveness not much lower than baseline |
| Preference does almost nothing | preference_fit moderate, but personalized directions nearly identical in content to baseline's closest direction |
| Over-constrains | preference_fit high, but diversity/distinctiveness drop sharply vs. baseline (directions converge on one territory) |
| Conflicts with the brief | preference_fit high, brief_integrity low (personalization wins at the brief's expense) |
| Reference copying | preference_fit very high, specificity/actionability drop because the output only restates the reference rather than adapting it to the brief |
| Fake personalization | preference_fit scored high on surface language alone but the underlying `promptModifier` content is unchanged from baseline — a scoring-process risk, not a rubric gap: always check the raw `creative_directions` content, not the `notes` summary, before assigning this score |

## Scoring process notes

- Score from `creative_directions[].promptModifier` content plus `final_answer`, not from
  `notes` (which is evaluator commentary, written after scoring, and must not be treated as
  ground truth when assigning the numeric scores themselves).
- Baseline trajectories are scored on all dimensions except preference_fit (marked N/A / left out
  of `paired_evaluation.csv`'s `preference_fit_baseline` column only in the sense that there is no
  preference input to fit — the column is still populated for comparability, scored against "does
  this direction set happen to already resemble a plausible future preference," which is why some
  baseline preference_fit scores in `paired_evaluation.csv` are non-trivial, e.g. cdq-002's baseline
  scoring 3 because its own "earthy-elegance" direction already partially overlaps the paired
  profile's territory).
- `winner` in `paired_evaluation.csv` is `personalized`, `baseline`, or `tie`, chosen holistically
  from the eight dimension scores with brief_integrity and diversity weighted most heavily against
  preference_fit gains (a preference_fit win that costs brief_integrity or collapses diversity does
  not, by itself, make personalized the winner — see `FINDINGS.md` for worked examples).
- `confidence` (`low`/`medium`/`high`) reflects how clearly the dimension scores separate the two
  arms, not how "good" either arm is — a close, low-margin result should be marked `low`/`medium`
  even if one side nominally scores higher on more dimensions.
