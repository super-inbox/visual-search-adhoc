#!/usr/bin/env python3
import csv
import hashlib
import json
import os

RUN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_DIR = os.path.join(RUN_ROOT, "final")

FILES = [
    ("README.md", "top-level run README explaining scope, target, and results"),
    ("RUN_MANIFEST.json", "machine-readable full run manifest"),
    ("ENVIRONMENT.md", "Phase 0 environment snapshot"),
    ("CODE_VERSION_AUDIT.md", "production commit confirmation + 26-feature optimization audit"),
    ("QUERY_FILE_AUDIT.md", "authoritative 328-query file identification & provenance"),
    ("COLLECTOR_AUDIT.md", "existing collector audit + isolated adaptation rationale"),
    ("COLLECTION_METHOD.md", "collection method selection & verification"),
    ("smoke_test_report.md", "5-query smoke test report"),
    ("smoke_test_results.csv", "smoke test results, flattened CSV"),
    ("smoke_test_results.jsonl", "smoke test results, full JSON records"),
    ("WORKTREE_SAFETY_REPORT.md", "post-run worktree safety audit"),
    ("logs/resume_history.md", "log of any run interruptions and resumes"),
    ("final/easy_query_production_baseline_full_results.csv", "one row per input query, flattened key fields"),
    ("final/easy_query_production_baseline_full_results.jsonl", "one JSON object per input query, full record"),
    ("final/easy_query_production_baseline_summary.json", "aggregate statistics, machine-readable"),
    ("final/easy_query_production_baseline_summary.md", "aggregate statistics, human-readable"),
    ("final/easy_query_production_baseline_zero_results.csv", "subset: zero-result queries"),
    ("final/easy_query_production_baseline_low_results.csv", "subset: low-result queries"),
    ("final/easy_query_production_baseline_errors.csv", "subset: technical errors (empty — none occurred)"),
    ("final/easy_query_production_baseline_timeouts.csv", "subset: timeouts (empty — none occurred)"),
    ("final/easy_query_production_baseline_broadened_queries.csv", "subset: queries where production broadened/rewrote"),
    ("final/easy_query_production_baseline_rewrite_observed.csv", "subset: queries with an observed rewrite signal"),
    ("final/easy_query_production_baseline_top_results.csv", "long-format top-5-results table, all queries"),
    ("final/easy_query_production_baseline_integrity_report.md", "post-run completeness/integrity checks"),
    ("final/easy_query_production_baseline_run_log.md", "full chronological collector run log"),
    ("final/CURIFY_EASY_QUERY_PRODUCTION_BASELINE_WORK_REPORT_2026-07-15_zh.md", "formal Chinese-language work report"),
    ("summaries/manual_review_queue.csv", "P0/P1/P2 human-review priority queue"),
    ("summaries/baseline_vs_optimized_join_ready.csv", "join-ready comparison vs. prior optimized-code run"),
    ("query_input/easy_queries_cleaned_300_plus_2026-07-14.csv", "authoritative input query file, byte-identical copy"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path):
    if path.endswith(".csv"):
        with open(path, newline="", encoding="utf-8") as f:
            return sum(1 for _ in csv.reader(f)) - 1
    if path.endswith(".jsonl"):
        with open(path, encoding="utf-8") as f:
            return sum(1 for _ in f)
    return None


def main():
    entries = []
    for rel, purpose in FILES:
        abs_path = os.path.join(RUN_ROOT, rel)
        if not os.path.exists(abs_path):
            entries.append({"relative_path": rel, "absolute_path": abs_path, "exists": False, "purpose": purpose})
            continue
        entries.append({
            "relative_path": rel,
            "absolute_path": abs_path,
            "exists": True,
            "file_type": os.path.splitext(rel)[1].lstrip("."),
            "byte_size": os.path.getsize(abs_path),
            "row_count": row_count(abs_path),
            "sha256": sha256(abs_path),
            "purpose": purpose,
            "generated_at": "2026-07-15",
        })

    out_path = os.path.join(FINAL_DIR, "easy_query_production_baseline_file_manifest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"run_root": RUN_ROOT, "files": entries}, f, ensure_ascii=False, indent=2)

    missing = [e["relative_path"] for e in entries if not e["exists"]]
    print(f"wrote manifest with {len(entries)} entries; missing at manifest-build time: {missing}")


if __name__ == "__main__":
    main()
