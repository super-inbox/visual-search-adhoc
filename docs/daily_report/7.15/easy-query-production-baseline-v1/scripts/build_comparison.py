#!/usr/bin/env python3
"""
Phase 16: attempt to build a join-ready baseline-vs-optimized comparison file.
Reads this run's own final/*.jsonl (never modifies it) plus the READ-ONLY
prior optimized-code run's results CSV at:
  docs/daily_report/7.14/search-relevance-stage7-rerun/easy-query-validation-300-plus/easy_query_validation_results_2026-07-14.csv
Writes ONLY into this run's summaries/ directory. Never touches the 07-14
directory or any file in it.
"""
import csv
import json
import os

RUN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_JSONL = os.path.join(RUN_ROOT, "final", "easy_query_production_baseline_full_results.jsonl")
QUERY_CSV = os.path.join(RUN_ROOT, "query_input", "easy_queries_cleaned_300_plus_2026-07-14.csv")
OPTIMIZED_CSV = os.path.join(
    os.path.dirname(os.path.dirname(RUN_ROOT)),
    "7.14", "search-relevance-stage7-rerun", "easy-query-validation-300-plus",
    "easy_query_validation_results_2026-07-14.csv",
)
OUT_CSV = os.path.join(RUN_ROOT, "summaries", "baseline_vs_optimized_join_ready.csv")


def load_baseline():
    recs = {}
    with open(FINAL_JSONL, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            recs[r["query_id"]] = r
    return recs


def load_optimized():
    if not os.path.exists(OPTIMIZED_CSV):
        return None
    with open(OPTIMIZED_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["easy_id"]: r for r in rows}


def load_input_order():
    with open(QUERY_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_bool(s):
    return str(s).strip().lower() in ("true", "1", "yes")


def main():
    baseline = load_baseline()
    optimized = load_optimized()
    input_rows = load_input_order()

    if optimized is None:
        with open(OUT_CSV, "w", encoding="utf-8") as f:
            f.write("OPTIMIZED_COMPARISON_NOT_CONFIRMED\n")
        print("OPTIMIZED_COMPARISON_NOT_CONFIRMED — source file not found")
        return

    fields = [
        "query_index", "query_id", "original_query",
        "baseline_status", "baseline_result_count", "baseline_zero_result", "baseline_low_result", "baseline_broadened",
        "optimized_status", "optimized_result_count", "optimized_zero_result", "optimized_low_result", "optimized_broadened",
        "comparison_available", "comparison_warning",
    ]
    rows_out = []
    for i, row in enumerate(input_rows, start=1):
        eid = row["easy_id"]
        b = baseline.get(eid)
        o = optimized.get(eid)
        warning = []
        if b is None:
            warning.append("baseline record missing")
        if o is None:
            warning.append("no matching optimized-run record for this easy_id")
        elif o.get("query") != row["query"]:
            warning.append("query text mismatch between input file and optimized-run row — do not trust this join")

        comparison_available = b is not None and o is not None and not warning

        rows_out.append({
            "query_index": i,
            "query_id": eid,
            "original_query": row["query"],
            "baseline_status": b.get("final_status") if b else None,
            "baseline_result_count": b.get("result_count_observed") if b else None,
            "baseline_zero_result": b.get("zero_result") if b else None,
            "baseline_low_result": b.get("low_result") if b else None,
            "baseline_broadened": b.get("query_broadened") if b else None,
            "optimized_status": ("ERROR" if o and to_bool(o.get("error")) else ("TIMEOUT" if o and to_bool(o.get("timeout")) else "SUCCESS")) if o else None,
            "optimized_result_count": o.get("final_result_count") if o else None,
            "optimized_zero_result": to_bool(o.get("zero_result_final")) if o else None,
            "optimized_low_result": to_bool(o.get("low_result_final")) if o else None,
            "optimized_broadened": to_bool(o.get("rewrite_triggered")) if o else None,
            "comparison_available": comparison_available,
            "comparison_warning": "; ".join(warning) if warning else (
                "NOTE: optimized run used the LOCAL, uncommitted, unpushed search-optimization branch — not production. "
                "This is a code-path comparison (production baseline vs. local optimization candidate), not a temporal before/after on the same deployed code."
            ),
        })

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)

    available = sum(1 for r in rows_out if r["comparison_available"])
    print(f"wrote {len(rows_out)} rows, comparison_available={available}")


if __name__ == "__main__":
    main()
