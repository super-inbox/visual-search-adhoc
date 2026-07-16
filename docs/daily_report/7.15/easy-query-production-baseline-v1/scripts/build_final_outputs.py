#!/usr/bin/env python3
"""
Builds all Phase 13/14/15 deliverables from raw/*.json + query_input CSV.
Read-only with respect to raw/, query_input/, checkpoints/, logs/ — only writes
into final/ and summaries/. Safe to re-run; final/*.csv|jsonl|json|md are the
only files it writes, and it always writes to the SAME run's final/ (never a
path outside this run directory), so it never touches any other prior run's
output.
"""
import csv
import glob
import hashlib
import json
import os
import statistics
import sys

RUN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUERY_CSV = os.path.join(RUN_ROOT, "query_input", "easy_queries_cleaned_300_plus_2026-07-14.csv")
RAW_DIR = os.path.join(RUN_ROOT, "raw")
FINAL_DIR = os.path.join(RUN_ROOT, "final")
SUMMARIES_DIR = os.path.join(RUN_ROOT, "summaries")

os.makedirs(FINAL_DIR, exist_ok=True)
os.makedirs(SUMMARIES_DIR, exist_ok=True)


def load_input_rows():
    with open(QUERY_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_raw_record(idx, easy_id):
    path = os.path.join(RAW_DIR, f"{idx:03d}_{easy_id}.json")
    if not os.path.exists(path):
        return None, path
    with open(path, encoding="utf-8") as f:
        return json.load(f), path


def main():
    input_rows = load_input_rows()
    n = len(input_rows)
    records = []
    missing = []
    for i, row in enumerate(input_rows, start=1):
        easy_id = row["easy_id"]
        rec, path = load_raw_record(i, easy_id)
        if rec is None:
            missing.append({"query_index": i, "query_id": easy_id, "original_query": row["query"]})
            rec = {
                "run_id": None,
                "query_index": i,
                "source_row_number": row.get("source_row"),
                "query_id": easy_id,
                "original_query": row["query"],
                "category": row.get("query_type"),
                "final_status": "MISSING_RECORD",
                "result_count_observed": None,
                "zero_result": False,
                "low_result": False,
                "query_broadened": False,
                "rewrite_observed": False,
                "duration_ms": None,
                "login_required": None,
                "HTTP_status": None,
                "top_results": [],
                "screenshot_path": None,
                "raw_response_path": None,
                "error_code": None,
                "error_message": "no raw record file found at expected path",
                "timeout": False,
                "network_error": None,
                "captcha": False,
                "rate_limited": False,
                "parse_error": False,
            }
        rec["_raw_path_expected"] = os.path.relpath(path, RUN_ROOT)
        rec["_raw_path_exists"] = os.path.exists(path)
        records.append(rec)

    # ---------- full_results.csv / .jsonl ----------
    full_csv_fields = [
        "run_id", "query_index", "source_row_number", "query_id", "original_query", "category",
        "test_target", "production_url", "request_url", "request_method", "request_timestamp",
        "response_timestamp", "duration_ms", "HTTP_status", "page_loaded", "search_completed",
        "result_count_reported", "result_count_observed", "zero_result", "low_result",
        "low_result_threshold", "query_broadened", "broadened_query", "rewrite_observed",
        "raw_rewrite_visible", "rewrite_source", "final_search_query_visible",
        "spelling_correction_visible", "login_required", "timeout", "rate_limited", "captcha",
        "parse_error", "network_error", "retry_count", "final_status", "error_code", "error_message",
        "screenshot_path", "raw_response_path",
    ]
    with open(os.path.join(FINAL_DIR, "easy_query_production_baseline_full_results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=full_csv_fields, extrasaction="ignore")
        w.writeheader()
        for r in records:
            row = {k: r.get(k) for k in full_csv_fields}
            row["raw_response_path"] = r.get("_raw_path_expected") if r.get("_raw_path_exists") else None
            w.writerow(row)

    with open(os.path.join(FINAL_DIR, "easy_query_production_baseline_full_results.jsonl"), "w", encoding="utf-8") as f:
        for r in records:
            out = {k: v for k, v in r.items() if not k.startswith("_")}
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    # ---------- category-specific CSVs ----------
    def write_subset_csv(name, predicate, extra_fields=None):
        fields = full_csv_fields + (extra_fields or [])
        path = os.path.join(FINAL_DIR, name)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            count = 0
            for r in records:
                if predicate(r):
                    row = {k: r.get(k) for k in fields}
                    row["raw_response_path"] = r.get("_raw_path_expected") if r.get("_raw_path_exists") else None
                    w.writerow(row)
                    count += 1
        return count

    zero_count = write_subset_csv("easy_query_production_baseline_zero_results.csv", lambda r: bool(r.get("zero_result")))
    low_count = write_subset_csv("easy_query_production_baseline_low_results.csv", lambda r: bool(r.get("low_result")))
    error_count = write_subset_csv(
        "easy_query_production_baseline_errors.csv",
        lambda r: r.get("final_status") in ("NETWORK_ERROR", "PARSE_ERROR", "UNKNOWN_ERROR", "MISSING_RECORD", "SITE_UNAVAILABLE"),
    )
    timeout_count = write_subset_csv("easy_query_production_baseline_timeouts.csv", lambda r: bool(r.get("timeout")) or r.get("final_status") == "TIMEOUT")
    broadened_count = write_subset_csv("easy_query_production_baseline_broadened_queries.csv", lambda r: bool(r.get("query_broadened")), extra_fields=["broadened_query", "raw_rewrite_visible"])
    rewrite_count = write_subset_csv("easy_query_production_baseline_rewrite_observed.csv", lambda r: bool(r.get("rewrite_observed")), extra_fields=["broadened_query", "raw_rewrite_visible", "rewrite_source"])

    # ---------- top_results.csv (long format) ----------
    with open(os.path.join(FINAL_DIR, "easy_query_production_baseline_top_results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["query_index", "query_id", "original_query", "result_rank", "result_title", "result_url", "image_url", "metadata"])
        for r in records:
            for tr in r.get("top_results") or []:
                w.writerow([r["query_index"], r.get("query_id"), r.get("original_query"), tr.get("rank"), tr.get("title"), tr.get("url"), tr.get("image_url"), tr.get("metadata")])

    # ---------- summary stats ----------
    def bucket_for(count):
        if count is None:
            return "unavailable"
        if count == 0:
            return "0"
        if count == 1:
            return "1"
        if 2 <= count <= 5:
            return "2-5"
        if 6 <= count <= 10:
            return "6-10"
        if 11 <= count <= 20:
            return "11-20"
        return "20+"

    buckets = {"0": 0, "1": 0, "2-5": 0, "6-10": 0, "11-20": 0, "20+": 0, "unavailable": 0}
    durations = []
    by_category = {}
    status_counts = {}
    dup_query_result_consistency = {}

    for r in records:
        rc = r.get("result_count_observed")
        buckets[bucket_for(rc)] += 1
        if isinstance(r.get("duration_ms"), (int, float)):
            durations.append(r["duration_ms"])
        cat = r.get("category") or "UNKNOWN"
        by_category.setdefault(cat, {"count": 0, "zero": 0, "low": 0, "error": 0, "broadened": 0})
        by_category[cat]["count"] += 1
        if r.get("zero_result"):
            by_category[cat]["zero"] += 1
        if r.get("low_result"):
            by_category[cat]["low"] += 1
        if r.get("final_status") in ("NETWORK_ERROR", "PARSE_ERROR", "UNKNOWN_ERROR", "MISSING_RECORD", "TIMEOUT"):
            by_category[cat]["error"] += 1
        if r.get("query_broadened"):
            by_category[cat]["broadened"] += 1

        st = r.get("final_status") or "UNKNOWN"
        status_counts[st] = status_counts.get(st, 0) + 1

        q = r.get("original_query")
        dup_query_result_consistency.setdefault(q, []).append(r.get("result_count_observed"))

    durations_sorted = sorted(durations)

    def pct(p):
        if not durations_sorted:
            return None
        k = (len(durations_sorted) - 1) * p
        f = int(k)
        c = min(f + 1, len(durations_sorted) - 1)
        if f == c:
            return durations_sorted[f]
        return durations_sorted[f] + (durations_sorted[c] - durations_sorted[f]) * (k - f)

    slowest_20 = sorted(
        [r for r in records if isinstance(r.get("duration_ms"), (int, float))],
        key=lambda r: r["duration_ms"],
        reverse=True,
    )[:20]

    duplicate_queries_with_inconsistent_counts = {
        q: counts for q, counts in dup_query_result_consistency.items() if len(counts) > 1 and len(set(counts)) > 1
    }

    summary = {
        "authoritative_query_count": n,
        "actual_completed_count": sum(1 for r in records if r.get("final_status") != "MISSING_RECORD"),
        "successful_search_count": sum(1 for r in records if r.get("final_status") in ("SUCCESS", "ZERO_RESULT", "LOW_RESULT")),
        "zero_result_count": zero_count,
        "zero_result_pct": round(100 * zero_count / n, 2) if n else None,
        "low_result_count": low_count,
        "low_result_pct": round(100 * low_count / n, 2) if n else None,
        "result_count_buckets": buckets,
        "missing_record_count": len(missing),
        "query_broadened_count": broadened_count,
        "rewrite_observed_count": rewrite_count,
        "spelling_correction_observed_count": sum(1 for r in records if r.get("spelling_correction_visible")),
        "network_error_count": sum(1 for r in records if r.get("final_status") == "NETWORK_ERROR"),
        "timeout_count": timeout_count,
        "rate_limited_count": sum(1 for r in records if r.get("rate_limited")),
        "captcha_count": sum(1 for r in records if r.get("captcha")),
        "parse_error_count": sum(1 for r in records if r.get("final_status") == "PARSE_ERROR"),
        "login_required_count": sum(1 for r in records if r.get("login_required")),
        "avg_duration_ms": round(statistics.fmean(durations), 1) if durations else None,
        "median_duration_ms": round(statistics.median(durations), 1) if durations else None,
        "p90_duration_ms": round(pct(0.90), 1) if durations else None,
        "p95_duration_ms": round(pct(0.95), 1) if durations else None,
        "slowest_20_queries": [
            {"query_index": r["query_index"], "query_id": r.get("query_id"), "original_query": r.get("original_query"), "duration_ms": r["duration_ms"]}
            for r in slowest_20
        ],
        "status_counts": status_counts,
        "by_category": by_category,
        "duplicate_query_result_consistency": {
            "distinct_queries_appearing_more_than_once": sum(1 for counts in dup_query_result_consistency.values() if len(counts) > 1),
            "inconsistent_result_count_across_duplicates": len(duplicate_queries_with_inconsistent_counts),
            "detail": duplicate_queries_with_inconsistent_counts,
        },
        "missing_records": missing,
    }

    with open(os.path.join(FINAL_DIR, "easy_query_production_baseline_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # ---------- summary.md ----------
    md = []
    md.append("# Easy Query Production Baseline — Summary\n")
    md.append(f"- Authoritative query count: **{summary['authoritative_query_count']}**")
    md.append(f"- Actual completed records: **{summary['actual_completed_count']}**")
    md.append(f"- Successful searches (SUCCESS/ZERO_RESULT/LOW_RESULT): **{summary['successful_search_count']}**")
    md.append(f"- Zero-result: **{summary['zero_result_count']}** ({summary['zero_result_pct']}%)")
    md.append(f"- Low-result (<{records[0].get('low_result_threshold', 5) if records else 5}): **{summary['low_result_count']}** ({summary['low_result_pct']}%)")
    md.append(f"- Missing records: **{summary['missing_record_count']}**")
    md.append(f"- Query broadened (server-side rewrite/broaden banner observed): **{summary['query_broadened_count']}**")
    md.append(f"- Rewrite observed: **{summary['rewrite_observed_count']}**")
    md.append(f"- Network errors: **{summary['network_error_count']}**, Timeouts: **{summary['timeout_count']}**, Rate-limited: **{summary['rate_limited_count']}**, Captcha: **{summary['captcha_count']}**, Parse errors: **{summary['parse_error_count']}**")
    md.append(f"- Login required encountered: **{summary['login_required_count']}**")
    md.append("\n## Result-count distribution\n")
    for k in ["0", "1", "2-5", "6-10", "11-20", "20+", "unavailable"]:
        md.append(f"- {k}: {summary['result_count_buckets'][k]}")
    md.append("\n## Response time\n")
    md.append(f"- Average: {summary['avg_duration_ms']} ms")
    md.append(f"- Median: {summary['median_duration_ms']} ms")
    md.append(f"- P90: {summary['p90_duration_ms']} ms")
    md.append(f"- P95: {summary['p95_duration_ms']} ms")
    md.append("\n## final_status breakdown\n")
    for k, v in sorted(summary["status_counts"].items(), key=lambda kv: -kv[1]):
        md.append(f"- {k}: {v}")
    md.append("\n## By category\n")
    md.append("| category | count | zero | low | error | broadened |")
    md.append("|---|---|---|---|---|---|")
    for cat, d in sorted(by_category.items()):
        md.append(f"| {cat} | {d['count']} | {d['zero']} | {d['low']} | {d['error']} | {d['broadened']} |")
    md.append("\n## Duplicate-query consistency\n")
    md.append(f"- Distinct queries appearing more than once in the input: {summary['duplicate_query_result_consistency']['distinct_queries_appearing_more_than_once']}")
    md.append(f"- Of those, with inconsistent result counts across occurrences: {summary['duplicate_query_result_consistency']['inconsistent_result_count_across_duplicates']}")
    md.append("\nThis is a **factual baseline summary only** — no relevance pass/fail judgement is made here. See `summaries/manual_review_queue.csv` for the human-review priority list.\n")

    with open(os.path.join(FINAL_DIR, "easy_query_production_baseline_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    # ---------- integrity report ----------
    integrity = []
    integrity.append("# Integrity Report\n")
    integrity.append(f"- Input query count: {n}")
    integrity.append(f"- Output record count (JSONL lines): {len(records)}")
    integrity.append(f"- final_record_count == authoritative_query_count: {len(records) == n}")
    integrity.append(f"- Missing record count: {len(missing)}")
    query_indices = [r["query_index"] for r in records]
    integrity.append(f"- Unique query_index count: {len(set(query_indices))} (expected {n})")
    integrity.append(f"- query_index values are a contiguous 1..{n} sequence: {sorted(query_indices) == list(range(1, n + 1))}")
    neg_counts = [r for r in records if isinstance(r.get("result_count_observed"), (int, float)) and r["result_count_observed"] < 0]
    integrity.append(f"- Records with negative result_count_observed (illegal): {len(neg_counts)}")
    zero_but_error = [r for r in records if r.get("zero_result") and r.get("final_status") not in ("ZERO_RESULT",)]
    integrity.append(f"- Records flagged zero_result=true but final_status != ZERO_RESULT (should be 0): {len(zero_but_error)}")
    error_as_zero = [
        r for r in records
        if r.get("final_status") in ("NETWORK_ERROR", "TIMEOUT", "PARSE_ERROR", "UNKNOWN_ERROR")
        and r.get("result_count_observed") == 0
        and not r.get("zero_result")
    ]
    integrity.append(f"- Sanity: failed queries with result_count_observed=0 but correctly NOT marked zero_result: {len(error_as_zero)} (this is the expected/correct pattern, not a defect)")
    screenshot_missing = [r for r in records if r.get("screenshot_path") and not os.path.exists(os.path.join(RUN_ROOT, r["screenshot_path"]))]
    integrity.append(f"- Records with a screenshot_path reference that does NOT exist on disk: {len(screenshot_missing)}")
    raw_missing = [r for r in records if not r.get("_raw_path_exists")]
    integrity.append(f"- Records with missing raw JSON file: {len(raw_missing)}")
    order_ok = [r["original_query"] for r in records] == [row["query"] for row in input_rows]
    integrity.append(f"- Output order matches input order exactly: {order_ok}")

    with open(os.path.join(FINAL_DIR, "easy_query_production_baseline_integrity_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(integrity) + "\n")

    # ---------- manual review queue ----------
    review_rows = []
    for r in records:
        if r.get("zero_result") or r.get("final_status") in ("NETWORK_ERROR", "PARSE_ERROR", "UNKNOWN_ERROR", "MISSING_RECORD", "SITE_UNAVAILABLE"):
            pr = "P0"
        elif r.get("low_result") or r.get("query_broadened") or r.get("spelling_correction_visible"):
            pr = "P1"
        else:
            continue
        review_rows.append({
            "priority": pr,
            "query_index": r["query_index"],
            "query_id": r.get("query_id"),
            "original_query": r.get("original_query"),
            "category": r.get("category"),
            "final_status": r.get("final_status"),
            "result_count_observed": r.get("result_count_observed"),
            "query_broadened": r.get("query_broadened"),
            "broadened_query": r.get("broadened_query"),
            "reason": (
                "zero_result" if r.get("zero_result") else
                "search_failed" if r.get("final_status") in ("NETWORK_ERROR", "PARSE_ERROR", "UNKNOWN_ERROR", "MISSING_RECORD", "SITE_UNAVAILABLE") else
                "low_result" if r.get("low_result") else
                "query_broadened_by_production" if r.get("query_broadened") else
                "spelling_correction_visible"
            ),
        })
    review_rows.sort(key=lambda x: (x["priority"], x["query_index"]))
    with open(os.path.join(SUMMARIES_DIR, "manual_review_queue.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["priority", "query_index", "query_id", "original_query", "category", "final_status", "result_count_observed", "query_broadened", "broadened_query", "reason"])
        w.writeheader()
        w.writerows(review_rows)

    print(json.dumps({
        "n": n,
        "records": len(records),
        "missing": len(missing),
        "zero": zero_count,
        "low": low_count,
        "error": error_count,
        "timeout": timeout_count,
        "broadened": broadened_count,
        "rewrite": rewrite_count,
    }, indent=2))


if __name__ == "__main__":
    main()
