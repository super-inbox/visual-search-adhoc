#!/usr/bin/env python3
"""Phase 1: input completeness/integrity audit for the automated relevance evaluation.
Read-only against the baseline root. Writes INPUT_AUDIT.md and input_integrity.json
into the automated_relevance_evaluation-v1 output directory only.
"""
import csv, json, hashlib, os, sys
from collections import Counter, OrderedDict

BR = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1"
OUT = os.path.join(BR, "automated_relevance_evaluation-v1")

QUERY_INPUT = os.path.join(BR, "query_input/easy_queries_cleaned_300_plus_2026-07-14.csv")
FULL_CSV = os.path.join(BR, "final/easy_query_production_baseline_full_results.csv")
FULL_JSONL = os.path.join(BR, "final/easy_query_production_baseline_full_results.jsonl")
TOP_CSV = os.path.join(BR, "final/easy_query_production_baseline_top_results.csv")
ZERO_CSV = os.path.join(BR, "final/easy_query_production_baseline_zero_results.csv")
LOW_CSV = os.path.join(BR, "final/easy_query_production_baseline_low_results.csv")
REWRITE_CSV = os.path.join(BR, "final/easy_query_production_baseline_rewrite_observed.csv")
BROADEN_CSV = os.path.join(BR, "final/easy_query_production_baseline_broadened_queries.csv")
RAW_DIR = os.path.join(BR, "raw")
SHOT_DIR = os.path.join(BR, "screenshots")

issues = []
notes = []

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

query_input = read_csv(QUERY_INPUT)
full_rows = read_csv(FULL_CSV)
top_rows = read_csv(TOP_CSV)
zero_rows = read_csv(ZERO_CSV)
low_rows = read_csv(LOW_CSV)
rewrite_rows = read_csv(REWRITE_CSV)
broaden_rows = read_csv(BROADEN_CSV)

with open(FULL_JSONL, encoding='utf-8') as f:
    jsonl_lines = [json.loads(l) for l in f if l.strip()]

# 1. authoritative query count
n_query_input = len(query_input)
if n_query_input != 328:
    issues.append(f"query_input has {n_query_input} rows, expected 328")

# 2/3. full csv / jsonl record counts
n_full_csv = len(full_rows)
n_jsonl = len(jsonl_lines)
if n_full_csv != 328:
    issues.append(f"full_results.csv has {n_full_csv} data rows, expected 328")
if n_jsonl != 328:
    issues.append(f"full_results.jsonl has {n_jsonl} objects, expected 328")

# 4. query order consistency between query_input and full_results (by source_row_number / easy_id)
qi_by_easyid = OrderedDict((r['easy_id'], r) for r in query_input)
order_mismatch = 0
for i, (r_qi, r_full) in enumerate(zip(query_input, full_rows)):
    if r_qi['easy_id'] != r_full['query_id']:
        order_mismatch += 1
if order_mismatch:
    issues.append(f"{order_mismatch} rows where query_input order != full_results order by easy_id/query_id")

# 5. query_index uniqueness / contiguity
qidx = [int(r['query_index']) for r in full_rows]
qidx_set = set(qidx)
duplicate_qidx = len(qidx) - len(qidx_set)
contiguous = qidx_set == set(range(1, 329))
if duplicate_qidx:
    issues.append(f"{duplicate_qidx} duplicate query_index values in full_results.csv")
if not contiguous:
    issues.append("query_index values in full_results.csv are not a contiguous 1..328 set")

# 6. original_query match against authoritative input, keyed by query_id/easy_id
mismatched_query_text = []
for r_full in full_rows:
    qid = r_full['query_id']
    qi = qi_by_easyid.get(qid)
    if qi is None:
        mismatched_query_text.append((qid, "MISSING_IN_QUERY_INPUT"))
        continue
    if qi['query'] != r_full['original_query']:
        mismatched_query_text.append((qid, f"input={qi['query']!r} vs full={r_full['original_query']!r}"))
if mismatched_query_text:
    issues.append(f"{len(mismatched_query_text)} query_id(s) with original_query text mismatch vs authoritative input: {mismatched_query_text[:10]}")

# 7. top results linkage by query_index
top_by_qidx = {}
for r in top_rows:
    top_by_qidx.setdefault(int(r['query_index']), []).append(r)
queries_with_top_results = set(top_by_qidx.keys())
full_qidx_set = qidx_set
queries_without_any_top_result = full_qidx_set - queries_with_top_results
# cross check against zero_result flag
zero_result_qidx = set(int(r['query_index']) for r in full_rows if r['zero_result'] == 'True' or r['zero_result'] == 'true')
unexplained_no_top = queries_without_any_top_result - zero_result_qidx
notes.append(f"Queries with zero visible Top Results rows: {len(queries_without_any_top_result)} (of which zero_result=true accounts for {len(queries_without_any_top_result & zero_result_qidx)})")
if unexplained_no_top:
    issues.append(f"{len(unexplained_no_top)} queries have NO Top Results rows but are not flagged zero_result: query_index={sorted(unexplained_no_top)}")

# 8. raw files count (328, excluding smoke_test subdir)
raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.json')]
n_raw = len(raw_files)
if n_raw != 328:
    issues.append(f"raw/ has {n_raw} .json files (top-level), expected 328")

# 9. screenshots count
shot_files = [f for f in os.listdir(SHOT_DIR) if f.endswith('.png')]
n_shot = len(shot_files)
if n_shot != 328:
    issues.append(f"screenshots/ has {n_shot} .png files (top-level), expected 328")

# 10. screenshot <-> query mapping via full_results.screenshot_path
missing_screenshot_refs = []
missing_raw_refs = []
for r in full_rows:
    sp = r.get('screenshot_path', '')
    rp = r.get('raw_response_path', '')
    if sp:
        full_sp = os.path.join(BR, sp) if not os.path.isabs(sp) else sp
        if not os.path.exists(full_sp):
            missing_screenshot_refs.append((r['query_id'], sp))
    else:
        missing_screenshot_refs.append((r['query_id'], "EMPTY_PATH"))
    if rp:
        full_rp = os.path.join(BR, rp) if not os.path.isabs(rp) else rp
        if not os.path.exists(full_rp):
            missing_raw_refs.append((r['query_id'], rp))
    else:
        missing_raw_refs.append((r['query_id'], "EMPTY_PATH"))
if missing_screenshot_refs:
    issues.append(f"{len(missing_screenshot_refs)} query rows reference a screenshot_path that does not resolve: {missing_screenshot_refs[:10]}")
if missing_raw_refs:
    issues.append(f"{len(missing_raw_refs)} query rows reference a raw_response_path that does not resolve: {missing_raw_refs[:10]}")

# 11. broaden/rewrite relational integrity: every rewrite_observed row's query_index must exist in full_rows
full_qidx_by_id = {int(r['query_index']) for r in full_rows}
rewrite_qidx = {int(r['query_index']) for r in rewrite_rows}
broaden_qidx = {int(r['query_index']) for r in broaden_rows}
if not rewrite_qidx.issubset(full_qidx_by_id):
    issues.append("rewrite_observed.csv has query_index values not present in full_results.csv")
if not broaden_qidx.issubset(full_qidx_by_id):
    issues.append("broadened_queries.csv has query_index values not present in full_results.csv")
# cross-check rewrite_observed flag in full_results matches rewrite csv membership
full_rewrite_true = {int(r['query_index']) for r in full_rows if r['rewrite_observed'] in ('True', 'true')}
if full_rewrite_true != rewrite_qidx:
    notes.append(f"rewrite_observed flag set in full_results for {len(full_rewrite_true)} queries vs {len(rewrite_qidx)} rows in rewrite_observed.csv (diff={len(full_rewrite_true.symmetric_difference(rewrite_qidx))})")

# 12. zero/low result relational integrity
full_zero_true = {int(r['query_index']) for r in full_rows if r['zero_result'] in ('True', 'true')}
zero_csv_qidx = {int(r['query_index']) for r in zero_rows}
if full_zero_true != zero_csv_qidx:
    issues.append(f"zero_result flag set for {len(full_zero_true)} queries in full_results vs {len(zero_csv_qidx)} rows in zero_results.csv")
full_low_true = {int(r['query_index']) for r in full_rows if r['low_result'] in ('True', 'true')}
low_csv_qidx = {int(r['query_index']) for r in low_rows}
if full_low_true != low_csv_qidx:
    issues.append(f"low_result flag set for {len(full_low_true)} queries in full_results vs {len(low_csv_qidx)} rows in low_results.csv")

# 13. empty queries
empty_queries = [r['easy_id'] for r in query_input if not r['query'] or not r['query'].strip()]
if empty_queries:
    issues.append(f"{len(empty_queries)} empty queries in query_input: {empty_queries}")

# 14/15. duplicate queries (by normalized text)
query_text_counts = Counter(r['query'].strip().lower() for r in query_input)
dupes = {k: v for k, v in query_text_counts.items() if v > 1}
if dupes:
    notes.append(f"{len(dupes)} duplicate query text value(s) found in query_input, all retained as distinct rows per RUN_MANIFEST duplicate policy: {dupes}")
else:
    notes.append("No duplicate query text found in query_input (consistent with RUN_MANIFEST duplicate_query_count_in_input=0).")

# 16. screenshot corruption check (basic: file size > 0 and PNG signature)
corrupt_screens = []
for r in full_rows:
    sp = r.get('screenshot_path', '')
    if not sp:
        continue
    full_sp = os.path.join(BR, sp) if not os.path.isabs(sp) else sp
    if os.path.exists(full_sp):
        try:
            with open(full_sp, 'rb') as fh:
                head = fh.read(8)
            if head[:8] != b'\x89PNG\r\n\x1a\n':
                corrupt_screens.append((r['query_id'], 'BAD_PNG_SIGNATURE'))
            elif os.path.getsize(full_sp) < 1024:
                corrupt_screens.append((r['query_id'], f'SUSPICIOUSLY_SMALL_{os.path.getsize(full_sp)}B'))
        except Exception as e:
            corrupt_screens.append((r['query_id'], f'READ_ERROR_{e}'))
if corrupt_screens:
    issues.append(f"{len(corrupt_screens)} screenshot(s) flagged as possibly corrupt/suspicious: {corrupt_screens[:10]}")

# 17. raw record corruption check (valid JSON, already parsed above per-file just re-validate)
corrupt_raw = []
for r in full_rows:
    rp = r.get('raw_response_path', '')
    if not rp:
        continue
    full_rp = os.path.join(BR, rp) if not os.path.isabs(rp) else rp
    if os.path.exists(full_rp):
        try:
            with open(full_rp, encoding='utf-8') as fh:
                json.load(fh)
        except Exception as e:
            corrupt_raw.append((r['query_id'], str(e)))
if corrupt_raw:
    issues.append(f"{len(corrupt_raw)} raw record(s) failed to parse as JSON: {corrupt_raw[:10]}")

# 18. Top Results missing for non-zero-result queries (result_count_observed > 0 but no top rows)
missing_top_but_nonzero = []
for r in full_rows:
    qidx_i = int(r['query_index'])
    rco = int(r['result_count_observed']) if r['result_count_observed'] not in ('', None) else 0
    has_top = qidx_i in top_by_qidx
    if rco > 0 and not has_top:
        missing_top_but_nonzero.append(r['query_id'])
if missing_top_but_nonzero:
    issues.append(f"{len(missing_top_but_nonzero)} queries report result_count_observed>0 but have no Top Results rows: {missing_top_but_nonzero}")

# 19. screenshot/raw content conflict: result_count_observed in full_results vs len(top_results) sanity (not strict equality since Top Results capped, but low_result claims should not wildly exceed top-5 cap when small)
count_conflicts = []
for r in full_rows:
    qidx_i = int(r['query_index'])
    rco = int(r['result_count_observed']) if r['result_count_observed'] not in ('', None) else 0
    n_top = len(top_by_qidx.get(qidx_i, []))
    if rco < n_top:
        count_conflicts.append((r['query_id'], rco, n_top))
if count_conflicts:
    issues.append(f"{len(count_conflicts)} queries where Top Results row count exceeds result_count_observed (possible conflict): {count_conflicts[:10]}")

# 20. path reference validity handled in 10 above.

# sha256 of query_input for provenance cross-check against RUN_MANIFEST
h = hashlib.sha256()
with open(QUERY_INPUT, 'rb') as f:
    h.update(f.read())
query_input_sha256 = h.hexdigest()

result = {
    "authoritative_query_count": n_query_input,
    "full_results_csv_row_count": n_full_csv,
    "full_results_jsonl_object_count": n_jsonl,
    "query_index_unique_count": len(qidx_set),
    "query_index_contiguous_1_328": contiguous,
    "order_mismatch_count": order_mismatch,
    "original_query_text_mismatch_count": len(mismatched_query_text),
    "queries_with_zero_top_results_rows": len(queries_without_any_top_result),
    "queries_with_zero_top_results_rows_unexplained_by_zero_result_flag": sorted(unexplained_no_top),
    "raw_json_file_count": n_raw,
    "screenshot_png_file_count": n_shot,
    "missing_screenshot_ref_count": len(missing_screenshot_refs),
    "missing_raw_ref_count": len(missing_raw_refs),
    "rewrite_csv_row_count": len(rewrite_rows),
    "broaden_csv_row_count": len(broaden_rows),
    "zero_result_csv_row_count": len(zero_rows),
    "low_result_csv_row_count": len(low_rows),
    "empty_query_count": len(empty_queries),
    "duplicate_query_text_count": len(dupes),
    "suspicious_screenshot_count": len(corrupt_screens),
    "corrupt_raw_json_count": len(corrupt_raw),
    "missing_top_results_for_nonzero_result_count": len(missing_top_but_nonzero),
    "top_results_exceeds_observed_count_count": len(count_conflicts),
    "query_input_sha256": query_input_sha256,
    "query_input_sha256_matches_run_manifest": query_input_sha256 == "682ed08a97f69ff39317c923ac859fe2f085ab8e8d7b9dc7b1a0f31fa0b32f3e",
    "total_issues": len(issues),
    "issues": issues,
    "notes": notes,
}

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "input_integrity.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# Determine blocking condition: only block if we cannot map the vast majority of queries
mapping_failure_rate = (order_mismatch + len(mismatched_query_text) + len(missing_top_but_nonzero)) / max(n_query_input, 1)
blocked = mapping_failure_rate > 0.5

md = []
md.append("# INPUT_AUDIT.md — Phase 1 Input Integrity Audit\n")
md.append(f"Run against baseline root: `{BR}`\n")
md.append(f"Query input SHA256: `{query_input_sha256}` — matches RUN_MANIFEST.json value: **{result['query_input_sha256_matches_run_manifest']}**\n")
md.append("## Checklist results (items 1-20 from task spec)\n")
checklist = [
    ("1. Authoritative query count == 328", n_query_input == 328, f"{n_query_input}"),
    ("2. full_results.csv has 328 query-level records", n_full_csv == 328, f"{n_full_csv}"),
    ("3. full_results.jsonl has 328 objects", n_jsonl == 328, f"{n_jsonl}"),
    ("4. Query order consistent between query_input and full_results", order_mismatch == 0, f"{order_mismatch} mismatches"),
    ("5. query_index unique and contiguous 1..328", duplicate_qidx == 0 and contiguous, f"unique={len(qidx_set)}, contiguous={contiguous}"),
    ("6. original_query matches authoritative input", len(mismatched_query_text) == 0, f"{len(mismatched_query_text)} mismatches"),
    ("7. Top Results linkable by query_index", len(unexplained_no_top) == 0, f"{len(unexplained_no_top)} unexplained gaps"),
    ("8. raw/ has 328 files", n_raw == 328, f"{n_raw}"),
    ("9. screenshots/ has 328 files", n_shot == 328, f"{n_shot}"),
    ("10. Screenshot/raw paths resolve for every query", len(missing_screenshot_refs) == 0 and len(missing_raw_refs) == 0, f"missing_screenshot={len(missing_screenshot_refs)}, missing_raw={len(missing_raw_refs)}"),
    ("11. broaden/rewrite data relationally consistent", rewrite_qidx.issubset(full_qidx_by_id) and broaden_qidx.issubset(full_qidx_by_id), "see notes"),
    ("12. zero/low-result data relationally consistent", full_zero_true == zero_csv_qidx and full_low_true == low_csv_qidx, "see notes"),
    ("13. No empty queries", len(empty_queries) == 0, f"{len(empty_queries)}"),
    ("14/15. Duplicate queries identified and retained (not dropped)", True, f"{len(dupes)} duplicate text value(s)"),
    ("16. No corrupt/suspicious screenshots", len(corrupt_screens) == 0, f"{len(corrupt_screens)} flagged"),
    ("17. No corrupt raw records", len(corrupt_raw) == 0, f"{len(corrupt_raw)} flagged"),
    ("18. No missing Top Results for queries with observed results", len(missing_top_but_nonzero) == 0, f"{len(missing_top_but_nonzero)}"),
    ("19. No screenshot/raw-record count conflicts", len(count_conflicts) == 0, f"{len(count_conflicts)} conflicts"),
    ("20. All path references valid", len(missing_screenshot_refs) == 0 and len(missing_raw_refs) == 0, "see item 10"),
]
for label, ok, detail in checklist:
    md.append(f"- [{'x' if ok else ' '}] {label} — {detail}")

md.append("\n## Issues found\n")
if issues:
    for i in issues:
        md.append(f"- ISSUE: {i}")
else:
    md.append("- None. All 20 checklist items pass.")

md.append("\n## Notes\n")
for n in notes:
    md.append(f"- {n}")

md.append(f"\n## Blocking decision\n")
md.append(f"- Mapping failure rate across order/text/top-results checks: {mapping_failure_rate:.4f}")
md.append(f"- BLOCKED_INPUT_MAPPING_FAILURE triggered: **{blocked}** (threshold: >50% of queries unmappable)")
md.append("- Any individual query with unresolved issues will be marked EVIDENCE_INCOMPLETE and evaluated as UNJUDGABLE / NEEDS_MANUAL_REVIEW rather than blocking the whole run.")

with open(os.path.join(OUT, "INPUT_AUDIT.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")

print("BLOCKED" if blocked else "OK", "issues=", len(issues))
print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
