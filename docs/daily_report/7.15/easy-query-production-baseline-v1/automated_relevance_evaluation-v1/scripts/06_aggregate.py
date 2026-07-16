#!/usr/bin/env python3
"""Aggregate all batch_NNN.csv / batch_NNN_results.jsonl into master first-pass datasets.
Read-only w.r.t. batches/; writes into checkpoints/ (intermediate, not a final/ deliverable)."""
import csv, json, os, glob

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1/automated_relevance_evaluation-v1"
BATCHES = os.path.join(OUT, "batches")

def main():
    query_rows = []
    result_rows = []
    for i in range(1, 18):
        bid = f"batch_{i:03d}"
        csv_path = os.path.join(BATCHES, f"{bid}.csv")
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                query_rows.append(row)
        jl_path = os.path.join(BATCHES, f"{bid}_results.jsonl")
        with open(jl_path, encoding="utf-8") as f:
            for line in f:
                result_rows.append(json.loads(line))

    query_rows.sort(key=lambda r: int(r["query_index"]))
    result_rows.sort(key=lambda r: (int(r["query_index"]), int(r["result_rank"])))

    # integrity checks
    indices = [int(r["query_index"]) for r in query_rows]
    assert len(indices) == 328, f"expected 328 query rows, got {len(indices)}"
    assert len(set(indices)) == 328, "duplicate query_index detected"
    assert set(indices) == set(range(1, 329)), "query_index does not cover 1..328 exactly"

    label_counts = {}
    for r in query_rows:
        label_counts[r["query_relevance_label"]] = label_counts.get(r["query_relevance_label"], 0) + 1
    assert sum(label_counts.values()) == 328

    os.makedirs(os.path.join(OUT, "checkpoints"), exist_ok=True)
    master_csv = os.path.join(OUT, "checkpoints", "master_query_level_first_pass.csv")
    with open(master_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(query_rows[0].keys()))
        w.writeheader(); w.writerows(query_rows)

    master_results_jsonl = os.path.join(OUT, "checkpoints", "master_result_level_first_pass.jsonl")
    with open(master_results_jsonl, "w", encoding="utf-8") as f:
        for r in result_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("query rows:", len(query_rows))
    print("result rows:", len(result_rows))
    print("label distribution:", label_counts)

    conf_counts = {}
    for r in query_rows:
        conf_counts[r["relevance_confidence"]] = conf_counts.get(r["relevance_confidence"], 0) + 1
    print("confidence distribution:", conf_counts)

    drift_counts = {}
    for r in query_rows:
        drift_counts[r["semantic_drift"]] = drift_counts.get(r["semantic_drift"], 0) + 1
    print("drift distribution:", drift_counts)

    rewrite_pass = sum(1 for r in query_rows if r["rewrite_observed"] == "True" and r["query_relevance_label"] == "PASS")
    print("rewrite_observed AND first-pass PASS:", rewrite_pass)

    needs_review = sum(1 for r in query_rows if r["needs_manual_review"] == "True")
    print("needs_manual_review (raw first-pass flag):", needs_review)

if __name__ == "__main__":
    main()
