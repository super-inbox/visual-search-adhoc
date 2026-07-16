#!/usr/bin/env python3
"""Generic batch processor. Takes a JUDGMENTS dict (imported from a per-batch module)
mapping query_id -> (result_labels, semantic_drift, intent_preserved, evidence_summary,
evaluation_method, primary_failure_reason_override) and the batch's input packets,
computes the full rubric-v1.1 output per query, writes batch CSV/JSONL/report, appends
result-level rows, and updates the resumable checkpoint.
"""
import csv, json, os, sys, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
from scoring import score_query, confidence_for

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1/automated_relevance_evaluation-v1"
EVALUATOR_VERSION = "claude-code-sonnet-5-rubric-v1.1"
RUBRIC_VERSION = "rubric-v1.1"
RUN_ID = "easyq-prod-baseline-2026-07-15-automated-relevance-v1"

FAILURE_REASON_MAP = {
    "FAIL": "MOST_RESULTS_IRRELEVANT",
    "PARTIAL": "PARTIAL_INTENT_ONLY",
    "PASS": "NONE",
    "UNJUDGABLE": "EVIDENCE_INCOMPLETE",
}


def load_batch_module(path):
    spec = importlib.util.spec_from_file_location("batch_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def process(batch_id, judgments_path, packets_by_id):
    mod = load_batch_module(judgments_path)
    J = mod.JUDGMENTS
    query_rows, result_rows = [], []

    for qid, spec in J.items():
        labels, drift, intent, evidence_summary, eval_method, failure_override = spec
        pk = packets_by_id[qid]
        result_labels = [{"rank": r, "label": l} for r, l in labels]
        scored = score_query(result_labels, drift, intent, pk["zero_result"])
        evidence_incomplete = eval_method == "EVIDENCE_INCOMPLETE"
        conf = confidence_for(scored["judgeable_result_count"], evidence_incomplete, False, eval_method)
        label = scored["query_relevance_label"]
        primary_reason = failure_override or (FAILURE_REASON_MAP.get(label, "NONE") if label != "PASS" else "NONE")
        if pk["zero_result"]:
            primary_reason = "ZERO_RESULT"

        needs_review = (conf == "LOW" or label in ("FAIL", "UNJUDGABLE") or drift in ("MODERATE", "SEVERE"))

        row = {
            "run_id": RUN_ID, "query_index": pk["query_index"], "source_row_number": pk["source_row_number"],
            "query_id": qid, "original_query": pk["original_query"], "detected_language": pk["detected_language"],
            "category": pk["category"], "query_type": pk["category"],
            "result_count_observed": pk["result_count_observed"], "zero_result": pk["zero_result"],
            "low_result": pk["low_result"], "rewrite_observed": pk["rewrite_observed"],
            "broadened_query": pk["broadened_query"], "semantic_drift": drift,
            "semantic_drift_severity": drift, "original_intent_preserved": intent,
            "visible_result_count": pk["visible_result_count"],
            "judgeable_result_count": scored["judgeable_result_count"],
            "relevant_count": scored["relevant_count"], "partially_relevant_count": scored["partially_relevant_count"],
            "irrelevant_count": scored["irrelevant_count"], "unjudgable_result_count": scored["unjudgable_result_count"],
            "top5_weighted_relevance": scored["top5_weighted_relevance"],
            "query_relevance_label": label, "relevance_score": scored["relevance_score"],
            "relevance_confidence": conf, "primary_failure_reason": primary_reason,
            "evidence_summary": evidence_summary, "screenshot_path": pk["screenshot_path"],
            "raw_record_path": pk["raw_response_path"], "evaluation_method": eval_method,
            "needs_manual_review": needs_review, "evaluator_version": EVALUATOR_VERSION,
            "evaluated_at": "2026-07-16", "notes": "",
        }
        for i in range(1, 6):
            match = [l for r, l in labels if r == i]
            row[f"top{i}_label"] = match[0] if match else ""
        query_rows.append(row)

        for r, l in labels:
            top = next((t for t in pk["top_results"] if t["rank"] == r), None)
            result_rows.append({
                "query_index": pk["query_index"], "original_query": pk["original_query"],
                "result_rank": r, "result_title": top["title"] if top else "",
                "result_url": top["url"] if top else "", "image_url": top["image_url"] if top else "",
                "metadata": top["metadata"] if top else "",
                "screenshot_path": pk["screenshot_path"], "relevance_label": l,
                "relevance_score": {"RELEVANT": 90, "PARTIALLY_RELEVANT": 55, "IRRELEVANT": 15}.get(l, None),
                "confidence": conf, "evidence_used": eval_method, "notes": "",
            })

    os.makedirs(os.path.join(OUT, "batches"), exist_ok=True)
    csv_path = os.path.join(OUT, "batches", f"{batch_id}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(query_rows[0].keys()))
        w.writeheader(); w.writerows(query_rows)
    with open(os.path.join(OUT, "batches", f"{batch_id}.jsonl"), "w", encoding="utf-8") as f:
        for r in query_rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    with open(os.path.join(OUT, "batches", f"{batch_id}_results.jsonl"), "w", encoding="utf-8") as f:
        for r in result_rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")

    label_counts = {}
    for r in query_rows:
        label_counts[r["query_relevance_label"]] = label_counts.get(r["query_relevance_label"], 0) + 1
    with open(os.path.join(OUT, "batches", f"{batch_id}_report.md"), "w", encoding="utf-8") as f:
        f.write(f"# {batch_id} report\n\n")
        f.write(f"Queries: {len(query_rows)}\n\nLabel distribution: {label_counts}\n\n")
        for r in query_rows:
            f.write(f"- **{r['query_id']}** `{r['original_query']}` -> {r['query_relevance_label']} "
                    f"(score={r['relevance_score']}, conf={r['relevance_confidence']}, drift={r['semantic_drift']}) "
                    f"— {r['evidence_summary']}\n")

    return query_rows, result_rows
