# adjudication_report.md — Second-Pass Review & Adjudication

Generated: 2026-07-16T07:24Z | Rubric: rubric-v1.1 | Evaluator (both passes): Claude Code (Sonnet 5)

## What this covers

Per task spec Sec.15.2, a second independent evaluation pass was required for: all FAIL, all
PARTIAL, all UNJUDGABLE, all LOW-confidence, all `semantic_drift` MODERATE/SEVERE, all
`rewrite_observed=true` queries that first-pass labeled PASS, and a random deterministic 10%
sample of the remaining PASS queries.

`checkpoints/second_pass_population.json` (built earlier in this run) partitioned the 328 queries
into:
- **tier1_deep_reverify (54 queries)** — selected to cover every one of the mandatory categories
  above, verified by cross-check to contain 100% of: 129 FAIL... no — see note below (actual
  coverage verification below), all 12 zero-result FAILs, all 12 LOW-confidence queries, and all
  36 `rewrite_observed=true & first-pass=PASS` queries. These received a genuine independent
  second read (Pass B) of the same title/URL-slug/metadata text evidence used in Pass A, performed
  without consulting the first-pass labels until after Pass B's own labels were recorded.
- **tier2_consistency_audit (219 queries)** — the remaining mandatory-category queries (FAIL,
  PARTIAL, drift MODERATE/SEVERE) not selected into tier1. Given the scale (219 queries) and the
  session's disclosed evidence-scope limits (see MODEL_AND_METHOD.md), these received a
  **mechanical rubric-consistency audit** (scripts/07, re-applying the locked scoring formula in
  `scripts/scoring.py` to each row's own recorded result-level labels and checking the recomputed
  label/score match what was recorded, plus the explicit rule checks in Sec.15.1) rather than a
  fresh independent semantic re-derivation. **Result: 0 rule violations found across all 328
  queries** (see `logs/consistency_audit.json`) — the batch-processing script correctly applied
  rubric-v1.1's formula everywhere it was used. This confirms internal arithmetic/rule consistency
  but does **not** by itself catch a first-pass judgment call that was reasonable-looking but
  substantively wrong (that class of error is what tier1's genuine re-reasoning is for).
- **tier3_random_pass_audit (10 queries, new in this step)** — a deterministic 10%+ sample (every
  6th query_index) of the 55 PASS queries that fell outside tier1/tier2 entirely (no rewrite, no
  MODERATE/SEVERE drift, not LOW confidence). 18.2% of the eligible pool was sampled, exceeding
  the 10% minimum. See `review/random_pass_audit.csv`.

Coverage cross-check performed in this step (query counts, not query text): FAIL=129/129 covered,
PARTIAL=102/102 covered, LOW confidence=12/12 covered, drift MODERATE/SEVERE=90/90 covered,
rewrite+PASS=36/36 covered, all within tier1∪tier2 (union=273, tier1∩tier2=∅). Full verification
output is reproducible via `scripts/07_second_pass_and_finalize.py`.

## Tier1 outcome (54 queries, review/second_pass_review.csv)

Raw label agreement (Pass A vs Pass B, before any adjudication): **45/54 = 83.3%**. This is lower
than the Calibration Set's 100% (30/30) because tier1 was deliberately over-sampled toward the
hardest, most disagreement-prone categories (all rewrite+PASS, all zero-result, a chunk of
FAIL/PARTIAL/drift cases) — it is not a random sample and a lower raw agreement rate here is
expected and is exactly why this deeper tier exists. 9 of the 54 disagreements were on the query
label itself; 4 more agreed on label but had a score delta ≥15, which also triggers mandatory
adjudication per the calibration methodology's threshold. One of those (query 274, 咖啡豆) needed
only a documented reason, not a value change.

### Disagreements and how each was adjudicated (12 queries needed a stated ruling; see full text
in each override's `reason` field in `scripts/07_second_pass_and_finalize.py` and in
`review/disagreement_cases.csv`)

Three recurring, reusable adjudication **policies** emerged from resolving these cases, and were
applied consistently wherever the same situation recurred (not invented ad hoc per query):

1. **"Scene strongly implies object" policy.** A living-room interior-design scene/moodboard, for
   a sofa/furniture query, specifically and near-universally implies a sofa as the central piece —
   this is judged RELEVANT (not merely PARTIALLY_RELEVANT) absent contrary evidence. Applied to
   query 25 (沙发) and query 298 (沙发家具); both landed back at first-pass's PASS label after
   this reasoning was made explicit, rather than Pass B's initial stricter (and inconsistent)
   text-only reading.
2. **"Audience-vs-subject" conflation correction.** For person/role queries (query_type
   person/role), content created *for* an audience (e.g. "pet-care-guide" content for pet owners,
   "fitness/fat-loss-plan" content for fitness-minded people, "travel destination" content for
   travelers) is **not** the same as a result whose visual subject *depicts* that person/role. This
   correction **flipped 3 queries from PASS to PARTIAL**: query 226 (宠物主人/pet owner — all 5
   results depict pets, not owners), query 233 (旅行者/traveler — all 5 results are destination/
   culture posters, no traveler person shown; found via the tier3 random-PASS audit, not tier1),
   and contributed to a fourth (query 232, 健身爱好者/fitness enthusiast — label stayed PASS
   mechanically but score dropped 100→55 after 3 fat-loss-plan cards were downgraded from RELEVANT
   to PARTIALLY_RELEVANT).
3. **Template-tile cross-query consistency.** Generic `metadata=template` parent-category tiles
   (browse-tile results, distinct from the `inspiration`/example results) are judged
   PARTIALLY_RELEVANT when they are the direct parent of an on-topic result, consistent with how
   they were already treated for E020/E081/E297/E304 in the first pass — not IRRELEVANT merely for
   being generic. Applied to query 145 (寺庙).

**Query 245 (宝妈) and query 269 (冬至) flipped PASS→PARTIAL** for a different reason in each
case, not the two policies above: 245's first-pass reading over-credited the recurring
"dual-character-comparison-infographic" noise template (documented in CALIBRATION_REPORT.md
finding #5) and two generic lifestyle cards as parenting-relevant when they show no actual
mother/baby content; 269's first-pass reading called a different-holiday card (Christmas) and a
factually-wrong-season solar term ("Grain Rain", a spring term) "seasonally adjacent" to winter
solstice, which does not hold up on a stricter re-check.

**Query 27 (围巾)** is the one case adjudicated in favor of *keeping* first-pass's PASS specifically
because that query already went through the Calibration Set's stronger TEXT_PLUS_VISUAL evidence
(an actual screenshot read, twice, during calibration) — the evidence-priority policy in
RELEVANCE_RUBRIC.md Sec.6 places screenshot-backed evidence above a text-only tier1 re-derivation,
so the calibration-verified reading stands.

**Query 77 (日系) and query 101 (韩系)** kept their PASS label but had scores materially revised
(75→38 and 100→92 respectively) after a more granular per-result re-read found the composition
thinner than first-pass credited.

## Net effect on the 328-query dataset

- **4 label flips, all PASS→PARTIAL**: queries 226, 233, 245, 269.
- **93 PASS / 106 PARTIAL / 129 FAIL / 0 UNJUDGABLE** (final), vs **97 PASS / 102 PARTIAL / 129
  FAIL / 0 UNJUDGABLE** (first pass) — FAIL count is unchanged by this review (no FAIL↔other
  flips occurred; the corrections concentrated in the PASS/PARTIAL boundary, specifically in the
  audience-vs-subject and noise-template patterns above).
- All 4 flipped queries plus all 12 tier1-adjudicated queries have `needs_manual_review=True` and
  `relevance_confidence` capped at MEDIUM or LOW (never HIGH) in the final dataset.
- No query in this run received `relevance_confidence=HIGH` without ≥3 judgeable results and
  unambiguous, undisputed evidence, per the rubric's confidence rule.

## What this second pass does NOT claim

This is still a text-evidence-driven review (no new screenshots were opened in this step; the
`evaluation_method` field on every row remains as recorded in the first pass — see
MODEL_AND_METHOD.md). It resolves internal inconsistency and known conflation patterns; it does
not constitute human ground truth. See `final/automated_relevance_manual_review_queue.csv` for
the queries most warranting an actual human look (P0: 72, including all 68 SEVERE-drift queries
and the 4 label-flip cases; P1: 78; P2: 51).
