#!/usr/bin/env python3
"""Shared, locked scoring engine implementing RELEVANCE_RUBRIC.md (rubric-v1.1).
Input: per-query result-level labels (assigned by the evaluator/LLM) + drift/intent
calls. Output: judgeable counts, top5_weighted_relevance, query_relevance_label,
relevance_score, relevance_confidence. This module is the single source of truth
for the arithmetic so it cannot drift between calibration, batches, and second pass.
"""

RANK_WEIGHTS = {1: 0.30, 2: 0.25, 3: 0.20, 4: 0.15, 5: 0.10}
LABEL_VALUES = {"RELEVANT": 1.0, "PARTIALLY_RELEVANT": 0.5, "IRRELEVANT": 0.0}
DRIFT_DEDUCTION = {"NONE": 0, "MINOR": 3, "MODERATE": 10, "SEVERE": 20, "UNKNOWN": 5}
INTENT_DEDUCTION = {"YES": 0, "PARTIALLY": 5, "NO": 15, "UNKNOWN": 5}


def score_query(result_labels, semantic_drift, intent_preserved, zero_result):
    """result_labels: list of dicts [{'rank':1,'label':'RELEVANT'}, ...] for visible top results (<=5).
    Returns dict with counts, weighted relevance, label, score, and the mechanical band used.
    """
    relevant_count = sum(1 for r in result_labels if r['label'] == 'RELEVANT')
    partial_count = sum(1 for r in result_labels if r['label'] == 'PARTIALLY_RELEVANT')
    irrelevant_count = sum(1 for r in result_labels if r['label'] == 'IRRELEVANT')
    unjudgable_count = sum(1 for r in result_labels if r['label'] == 'UNJUDGABLE')
    judgeable_count = relevant_count + partial_count + irrelevant_count

    if zero_result:
        return {
            "relevant_count": relevant_count, "partially_relevant_count": partial_count,
            "irrelevant_count": irrelevant_count, "unjudgable_result_count": unjudgable_count,
            "judgeable_result_count": judgeable_count,
            "top5_weighted_relevance": 0.0,
            "relevant_rate": None, "rel_plus_partial_rate": None, "irrelevant_rate": None,
            "query_relevance_label": "FAIL",
            "relevance_score": 0,
            "primary_failure_reason": "ZERO_RESULT",
        }

    num, den = 0.0, 0.0
    for r in result_labels:
        if r['label'] == 'UNJUDGABLE':
            continue
        w = RANK_WEIGHTS.get(r['rank'], 0)
        num += w * LABEL_VALUES[r['label']]
        den += w

    if judgeable_count == 0:
        return {
            "relevant_count": 0, "partially_relevant_count": 0, "irrelevant_count": 0,
            "unjudgable_result_count": unjudgable_count, "judgeable_result_count": 0,
            "top5_weighted_relevance": None,
            "relevant_rate": None, "rel_plus_partial_rate": None, "irrelevant_rate": None,
            "query_relevance_label": "UNJUDGABLE",
            "relevance_score": None,
            "primary_failure_reason": "EVIDENCE_INCOMPLETE",
        }

    weighted = num / den if den > 0 else 0.0
    relevant_rate = relevant_count / judgeable_count
    rel_plus_partial_rate = (relevant_count + partial_count) / judgeable_count
    irrelevant_rate = irrelevant_count / judgeable_count

    base = round(weighted * 100)
    score = base - DRIFT_DEDUCTION.get(semantic_drift, 0) - INTENT_DEDUCTION.get(intent_preserved, 0)
    score = max(0, min(100, score))

    is_fail = (irrelevant_rate > 0.60) or (semantic_drift == "SEVERE" and intent_preserved == "NO")
    is_pass = (not is_fail and irrelevant_rate <= 0.20 and intent_preserved != "NO" and
               semantic_drift != "SEVERE" and
               (relevant_rate >= 0.60 or (rel_plus_partial_rate >= 0.80 and relevant_rate >= 0.20)))

    if is_fail:
        label = "FAIL"
    elif is_pass:
        label = "PASS"
    else:
        label = "PARTIAL"

    return {
        "relevant_count": relevant_count, "partially_relevant_count": partial_count,
        "irrelevant_count": irrelevant_count, "unjudgable_result_count": unjudgable_count,
        "judgeable_result_count": judgeable_count,
        "top5_weighted_relevance": round(weighted, 4),
        "relevant_rate": round(relevant_rate, 4), "rel_plus_partial_rate": round(rel_plus_partial_rate, 4),
        "irrelevant_rate": round(irrelevant_rate, 4),
        "query_relevance_label": label,
        "relevance_score": score,
    }


def confidence_for(judgeable_result_count, evidence_incomplete, disagreement, evaluation_method):
    if judgeable_result_count == 0 or evidence_incomplete or disagreement:
        return "LOW"
    if judgeable_result_count < 3:
        return "MEDIUM"
    if evaluation_method == "TEXT_EVIDENCE_ONLY":
        return "MEDIUM"
    return "HIGH"
