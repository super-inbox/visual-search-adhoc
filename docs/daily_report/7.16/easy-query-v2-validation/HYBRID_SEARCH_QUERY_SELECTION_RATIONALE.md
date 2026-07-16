# Hybrid Search Core-80 Candidate Set — Selection Rationale

Date: 2026-07-17
Source: `easy_query_v2_relevance_evaluation.csv` (326 rows, 2026-07-16 collection, rubric-v1.1)
Companion files: `HYBRID_SEARCH_CORE80_CANDIDATE_SET.csv`, `EASY_QUERY_V2_ROOT_CAUSE_ANALYSIS_ZH.md`

This document is analysis-only. No new collection was run, the query bank
(`easy_query_bank_v2_2026-07-16.csv`) was not touched, and no search code was modified. It explains how
the 80-query Hybrid Search candidate set was selected from the completed 326-query evaluation, and the
decision framework used to judge whether a Google Image fallback or an improved LLM rewrite step would
plausibly fix each candidate.

## 1. Goal

Hybrid Search planning needs a small, high-signal query set that (a) stress-tests every failure mode
observed in the full 326-query run, (b) is balanced enough across scenarios and query difficulty that a
before/after comparison is meaningful, and (c) includes a regression guard so a Hybrid Search rollout
can be checked for "did it also break what already worked" and not just "did it fix what was broken."

## 2. Composition

**80 queries, 20 per scenario** (Education uses 6/5/6/3 instead of 5/5/7/3 because zero-result queries
are heavily concentrated there — 16 of the benchmark's 34 zero-result queries are Education queries,
so Education's zero-result quota was raised by one and its FAIL/PARTIAL quota lowered by one to keep
the scenario total at 20):

| Scenario | ZERO_RESULT | LOW_RESULT | FAIL_PARTIAL (representative) | PASS_GUARD | Total |
|---|---:|---:|---:|---:|---:|
| Creative / Cultural / Merch | 5 | 5 | 7 | 3 | 20 |
| Brand / Business Visual Assets | 5 | 5 | 7 | 3 | 20 |
| Marketing / Ecommerce | 5 | 5 | 7 | 3 | 20 |
| Education / Learning Material | 6 | 5 | 6 | 3 | 20 |
| **Total** | **21** | **20** | **27** | **12** | **80** |

Each selection group answers a different question for Hybrid Search planning:

- **ZERO_RESULT (21)** — the current sparse/token pipeline returns literally nothing. Tests whether
  dense retrieval or an external fallback can produce *any* usable candidate. All 21 come from the
  benchmark's 34 zero-result queries, chosen to spread across the four special-focus clusters (design,
  teaching material, drawing/illustration, toy/merch) rather than clustering in one category.
- **LOW_RESULT (20)** — final `result_count` between 1 and 4 (inclusive), a distinct signal from
  zero-result. Tests whether hybrid retrieval increases recall depth/confidence, including a few cases
  that already PASS on a single thin hit (e.g. V272 `timetable`, V309 `人体图解`) — worth checking
  whether Hybrid Search adds *supporting* evidence rather than just fixing failures.
  Note: because `low_result` in the evaluation CSV is defined pre-rewrite (`first_pass_count < 5`, which
  correlates 1:1 with `rewrite_triggered`), this group instead uses **final result_count 1–4** as the
  operative "low-result" signal, since that is what a Hybrid Search reviewer actually sees in the UI.
- **FAIL_PARTIAL representative (27)** — queries with results, but bad ones. Selected to cover all four
  root-cause buckets (catalog gap, ambiguous intent, query-understanding/rewrite drift, retrieval
  ranking) documented in the root-cause analysis, and to include several of the most dramatic
  "flooding" cases (`globe` at 3,205 results, `drink bottle` at 3,134, `statue` at 2,748, `unboxing
  photo` at 1,284) as stress tests of how much headroom Hybrid Search + reranking actually has.
- **PASS_GUARD (12)** — currently-PASS queries, one per scenario cluster of clean, unambiguous
  templates (e.g. `movie poster`, `world map`, `flashcard`, `product label`). Their only job is to
  confirm Hybrid Search does not regress them.

## 3. Root-cause tagging and the fallback/rewrite decision framework

Every non-PASS candidate is tagged with a primary root cause (rule-based classification over the
`reason` field + `result_count` + `rewrite_triggered`, detailed in the companion Chinese report,
section 2). The tag then drives a consistent recommendation for the two remediation levers this task
asked about:

| Root cause | Google Image fallback | LLM rewrite improvement |
|---|---|---|
| **CATALOG_GAP** — object/template family genuinely absent from the 3,209-item catalog (all 34 zero-result queries, plus near-miss cases where only thematically-adjacent content surfaces) | **YES** — common real-world objects/documents (certificates, coupons, whiteboards, plush toys) have strong external image-search coverage; the catalog cannot be rewritten into having content it never had | **NO** — no phrasing change manufactures a template family that does not exist |
| **AMBIGUOUS_INTENT** — query term maps to 2+ catalog senses and the wrong one dominates (咖啡杯→World Cup, 标志→landmark, charm→"charming character") | **PARTIAL** — an external image call could return the right object, but only if intent is disambiguated *before* the fallback fires, otherwise it inherits the same ambiguity | **YES** — needs a disambiguation-aware rewrite/intent-classification step, not a generic paraphrase |
| **QUERY_UNDERSTANDING_REWRITE** — the rewrite step itself drifted off-topic or over-broadened (e.g. `globe`→3,205 irrelevant "leader" MBTI cards) | **NO** — internal rewrite malfunction; an external source doesn't fix a broken internal step, and raw (if wrong) results already exist | **YES** — this is a rewrite-guardrail problem by construction; tightening subject-fidelity constraints on generated rewrite candidates is the direct fix |
| **RETRIEVAL_RANKING** — relevant content plausibly exists but recurring high-frequency noise templates (food-doodle stickers, IP merch mockups, MBTI character series) outrank it | **NO** — the gap isn't content, it's ranking; an external image doesn't help re-sort the internal candidate pool | **NO** — most of these queries never triggered rewrite, or rewrite didn't change the outcome; the fix is dense/hybrid retrieval + reranking |

This framework is applied per-query in `HYBRID_SEARCH_CORE80_CANDIDATE_SET.csv` (columns
`google_image_fallback_may_help` / `llm_rewrite_may_help`, each with a query-specific rationale in the
adjacent `*_rationale` column). Aggregate distribution across the 80 candidates:

- Google Image fallback: **30 YES / 14 PARTIAL / 36 NO**
- LLM rewrite improvement: **25 YES / 55 NO**

The asymmetry is intentional and reflects the underlying data: CATALOG_GAP (30/80 candidates) is the
single largest bucket among non-PASS candidates and is the one root cause an external fallback directly
addresses, while QUERY_UNDERSTANDING_REWRITE + AMBIGUOUS_INTENT together (25/80) are the buckets an
improved rewrite/intent step addresses. RETRIEVAL_RANKING (9/80 in this sample; 77/244 in the full
non-PASS population) is neither fixed by fallback nor rewrite — it is the strongest argument in this
whole analysis for actual hybrid (dense + sparse) retrieval and reranking, as opposed to just adding a
fallback or improving prompts.

## 4. CSV column reference (`HYBRID_SEARCH_CORE80_CANDIDATE_SET.csv`)

| Column | Meaning |
|---|---|
| `easy_id` | Stable ID from the 326-query evaluation (traceable back to `easy_query_v2_relevance_evaluation.csv`) |
| `query`, `language`, `scenario`, `category` | From the original benchmark |
| `special_bucket` | This task's four cross-cutting analysis clusters: `design`, `teaching_material`, `drawing_illustration`, `toy_merch` (mapped from `category`; see root-cause report section 3 for the mapping) |
| `selection_group` | `ZERO_RESULT` / `LOW_RESULT` / `FAIL_PARTIAL` / `PASS_GUARD` |
| `current_label`, `current_score`, `result_count`, `rewrite_triggered` | Carried over from the 7/16 evaluation, unchanged |
| `root_cause` | `CATALOG_GAP` / `AMBIGUOUS_INTENT` / `QUERY_UNDERSTANDING_REWRITE` / `RETRIEVAL_RANKING` / `HEALTHY_BASELINE` |
| `why_selected` | Why this specific query earned a slot in the 80 |
| `expected_failure_mode` | What is actually going wrong, grounded in the original independent judgment |
| `google_image_fallback_may_help` / `_rationale` | Per the decision framework above |
| `llm_rewrite_may_help` / `_rationale` | Per the decision framework above |

## 5. Notable individual candidates worth flagging to the Hybrid Search team

- **`globe` (V268)**: rewrite_triggered inflated the result set to 3,205 items, all irrelevant (drifted
  to unrelated "leader" MBTI character cards). Its Chinese pair `地球仪` (V267) is zero-result. Together
  they show the two extremes of the same catalog gap — total silence vs. confident-but-wrong flooding —
  and make a good acceptance-test pair for Hybrid Search + reranking.
- **`mascot` / `吉祥物` (V010 PASS vs V009 FAIL)**: same concept, opposite outcomes by language. The
  Chinese query hits an entirely unrelated "organ health infographic" series while the English query
  scores 100. Included as a bilingual-asymmetry regression check, not purely a difficulty check.
- **`membership card` / `会员卡` / `loyalty card` / `gift card` (V223, V224, V228)**: an entire category
  (membership_card) fails 100% (6/6), all for different sub-reasons (rewrite drift on two, generic
  "education-card"/"flashcard" template-naming collision on the others) — a good cluster to validate
  whether Hybrid Search fixes the category as a whole or just individual queries within it.
- **PASS_GUARD set intentionally skews toward unambiguous, single-template-family hits** (`movie
  poster`, `flashcard`, `world map`, `product label`, `envelope`, `before/after comparison`) rather than
  borderline PASS scores, so a regression in this group is unambiguous signal, not noise.

## 6. Explicit non-goals / constraints honored

- No benchmark re-run: all data reused from the existing 326-row evaluation and its checkpoint JSONs.
- No modification to `easy_query_bank_v2_2026-07-16.csv` or any prior evaluation output.
- No search code changes — this is a planning artifact for the next phase, not an implementation.
- Root-cause tags are a rule-based heuristic over evaluator-written text, not a ground-truth label;
  borderline cases exist and are called out rather than hidden (see root-cause report section 2 and 5).
