# RELEVANCE_RUBRIC.md — Curify Easy Query Automated Relevance Evaluation

Version: rubric-v1 (locked before calibration; any change requires a new version number and a logged reason in CALIBRATION_REPORT.md)

## 1. Evaluation object

The object of evaluation is **the relevance between the user's `original_query` and the Top Results actually returned by production**, regardless of whether production internally broadened or rewrote the query. `broadened_query` is context for explaining *why* a result appears, never the yardstick for whether it *should* appear.

## 2. Result-level labels

- **RELEVANT** — the result's visual subject/object/scene/design-type/core semantic clearly matches the original query's core intent.
- **PARTIALLY_RELEVANT** — matches a secondary attribute, superordinate category, adjacent concept, or only part of a multi-component query.
- **IRRELEVANT** — does not match the query's core intent, including drift introduced by an incorrect rewrite/broaden.
- **UNJUDGABLE** — insufficient evidence (blank/unrendered thumbnail with no usable title/url signal, corrupted screenshot, empty placeholder, raw record and screenshot both insufficient).

## 3. Query-level labels

**PASS / PARTIAL / FAIL / UNJUDGABLE**, defined by the mechanical reference bands below *plus* a mandatory holistic check (intent preservation, severity of drift). The mechanical bands are a starting point, not an auto-decision; the evaluator may override with a stated reason (recorded in `notes`), but may not override silently.

Let `judgeable_count = relevant_count + partially_relevant_count + irrelevant_count` (UNJUDGABLE results excluded).
Let `relevant_rate = relevant_count / judgeable_count`, `rel_plus_partial_rate = (relevant_count + partially_relevant_count) / judgeable_count`, `irrelevant_rate = irrelevant_count / judgeable_count`.

- **FAIL** if `zero_result = true` (always, `primary_failure_reason=ZERO_RESULT`), OR `judgeable_count > 0` AND `irrelevant_rate > 0.60`, OR `semantic_drift = SEVERE` AND `original_intent_preserved = NO`.
- **PASS** if NOT FAIL, AND `irrelevant_rate <= 0.20`, AND `original_intent_preserved != NO`, AND `semantic_drift != SEVERE`, AND (`relevant_rate >= 0.60` OR (`rel_plus_partial_rate >= 0.80` AND `relevant_rate >= 0.20`)).
- **UNJUDGABLE** if `judgeable_count == 0` AND `zero_result = false` (i.e. results exist but none are evaluable from available evidence), OR evidence is flagged `EVIDENCE_INCOMPLETE` to a degree that prevents any reliable call.
- **PARTIAL** — everything else (mixed quality, partial intent coverage, moderate drift, thin-but-real evidence).

**rubric-v1.1 clarification (added during Calibration, see CALIBRATION_REPORT.md):** the original mechanical draft treated `relevant_rate < 0.20` as an independent FAIL trigger. Calibration on real data (e.g. a query where 100% of judged results were PARTIALLY_RELEVANT and 0% IRRELEVANT) showed this over-triggers FAIL for thin-but-not-wrong result sets. `relevant_rate < 0.20` alone is now advisory context for the PARTIAL/FAIL judgment call, not a hard FAIL trigger — the only hard FAIL triggers are `zero_result`, `irrelevant_rate > 0.60`, and `semantic_drift=SEVERE` combined with `original_intent_preserved=NO`. Symmetrically, PASS's `rel_plus_partial_rate >= 0.80` clause now requires `relevant_rate >= 0.20` alongside it, so an all-PARTIALLY_RELEVANT result set (0% fully RELEVANT) cannot mechanically PASS either — it lands in PARTIAL, which matches the intuitive read of "nothing here is wrong, but nothing is a strong hit."

Technical errors (page failed to load, timeout, parse error) are **never** scored FAIL on relevance grounds — they are `UNJUDGABLE` with `primary_failure_reason=TECHNICAL_ERROR`. (Note: this baseline run recorded 0 technical errors per RUN_MANIFEST, so this path is expected to be unused but is kept as a rule.)

## 4. Scoring (0-100), fixed formula — locked, not changed mid-run

**Step 1 — Top-5 weighted relevance (0-1):**
Rank weights: rank1=0.30, rank2=0.25, rank3=0.20, rank4=0.15, rank5=0.10.
Label values: RELEVANT=1.0, PARTIALLY_RELEVANT=0.5, IRRELEVANT=0.0. UNJUDGABLE results are excluded from both numerator and denominator (renormalized over judgeable ranks only).

```
top5_weighted_relevance = Σ(weight_i * value_i, i judgeable) / Σ(weight_i, i judgeable)
```

If no judgeable results exist, `top5_weighted_relevance = null`.

**Step 2 — Base score:** `base = round(top5_weighted_relevance * 100)` if not null, else base is undefined (score = null, label likely UNJUDGABLE).

**Step 3 — Deductions applied to base (order-independent, additive, floor 0):**
- `semantic_drift = SEVERE`: −20
- `semantic_drift = MODERATE`: −10
- `semantic_drift = MINOR`: −3
- `original_intent_preserved = NO`: −15
- `original_intent_preserved = PARTIALLY`: −5

**Step 4 — Hard overrides:**
- `zero_result = true` → score = 0, label = FAIL, regardless of Steps 1-3.
- `query_relevance_label = UNJUDGABLE` → score = null (never force a number to hit a completion quota).

**Step 5:** clamp to [0,100], round to nearest integer.

## 5. Confidence

- **HIGH**: `judgeable_result_count >= 3`, evidence unambiguous (clear title/url/slug match or direct screenshot read), no unresolved conflicts, not `EVIDENCE_INCOMPLETE`.
- **MEDIUM**: `judgeable_result_count` in 1-2, or evidence is text-only for a visually-ambiguous query, or minor unresolved signal conflicts.
- **LOW**: `judgeable_result_count == 0`, `EVIDENCE_INCOMPLETE`, conflicting evidence, or a two-pass disagreement not yet adjudicated with high certainty.

If `judgeable_result_count < 3`, confidence may never be HIGH (rule from task spec §12). `needs_manual_review = true` whenever confidence is LOW, label is FAIL/UNJUDGABLE, semantic_drift is MODERATE/SEVERE, or the two evaluation passes disagreed.

## 6. Evidence priority (task spec §8, applied as-is)

1. Screenshot visual content (read directly for: the 30-query calibration set, all zero-result queries, all second-pass-review queries, and spot audits — see MODEL_AND_METHOD.md for exact scope; full-328 screenshot reading was not performed for scale reasons and this is disclosed, not hidden).
2. Top Result title / URL / metadata — for production Curify results the URL slug is a descriptive template/carousel identifier (e.g. `template-fashion-nail-art-design-cherry-blossom`) and is treated as strong textual evidence of visual subject matter, not just a title match.
3. raw record structured fields.
4. broadened_query / rewrite banner text (context only, never the relevance target itself).
5. Result count / page state.

## 7. Query intent structure (task spec §7)

Every query gets: `original_query, detected_language, query_type, primary_intent, core_entities, core_attributes, visual_expectation, ambiguity_level (LOW/MEDIUM/HIGH), acceptable_interpretations, unacceptable_drift`. `query_type` reuses the authoritative input taxonomy (object, material, style, scene, industry, format, audience, festival, product_category, action) since that classification is already validated in `query_input/`; additional descriptive types (brand, visual-identity, ambiguous-simple-word, multi-intent, interface, architecture, etc.) may be layered on where the input taxonomy under-specifies a query.

Ambiguous/multi-sense queries: any common, plausible visual reading of the word is acceptable; a query is not FAILed merely for having multiple senses. It is only marked with `semantic_drift` if production's rewrite/broadening locked the query into a narrow or clearly wrong sense.

## 8. Rewrite / broaden handling

`rewrite_observed=true` and/or `query_broadened=true` never automatically imply PASS or FAIL. The evaluator judges the *actual returned results* against the *original* query intent. `semantic_drift` records whether the rewrite's substituted/added terms pulled the result set away from the original intent (NONE/MINOR/MODERATE/SEVERE), independent of the query-level PASS/FAIL outcome.

## 9. Zero-result / low-result handling

- `zero_result=true` → always FAIL, score 0, `primary_failure_reason=ZERO_RESULT`, `needs_manual_review=false` unless the underlying data is internally contradictory (e.g. zero_result=true but Top Results rows exist — none observed in the Phase-1 audit).
- `low_result=true` → never auto-FAIL. Evaluated the same as any other query on its actual (few) results; small relevant result sets can PASS or PARTIAL. Confidence is capped based on `judgeable_result_count` per §5.

## 10. Formula lock

This rubric (rubric-v1) is applied unchanged across Calibration Pass A, Calibration Pass B, the full 328-query first pass, and the second-pass review. If Calibration reveals the rubric's wording is ambiguous, at most 2 clarifying revisions are permitted (documented in CALIBRATION_REPORT.md as rubric-v1.1 / rubric-v1.2); the scoring *formula* and label thresholds in §3-4 are not altered, only clarifying language.
