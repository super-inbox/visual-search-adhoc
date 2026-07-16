# Integrity Report

- Input query count: 328
- Output record count (JSONL lines): 328
- final_record_count == authoritative_query_count: True
- Missing record count: 0
- Unique query_index count: 328 (expected 328)
- query_index values are a contiguous 1..328 sequence: True
- Records with negative result_count_observed (illegal): 0
- Records flagged zero_result=true but final_status != ZERO_RESULT (should be 0): 0
- Sanity: failed queries with result_count_observed=0 but correctly NOT marked zero_result: 0 (this is the expected/correct pattern, not a defect)
- Records with a screenshot_path reference that does NOT exist on disk: 0
- Records with missing raw JSON file: 0
- Output order matches input order exactly: True
