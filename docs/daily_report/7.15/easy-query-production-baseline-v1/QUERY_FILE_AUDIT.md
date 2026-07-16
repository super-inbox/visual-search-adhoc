# QUERY_FILE_AUDIT.md — Authoritative 300+ Easy Query File Identification

## Result: `AUTHORITATIVE_EASY_QUERY_FILE_CONFIRMED`

## Selected file

- **Path (original)**: `docs/daily_report/7.14/search-relevance-stage7-rerun/easy-query-validation-300-plus/easy_queries_cleaned_300_plus_2026-07-14.csv`
- **Path (copied into this run, byte-identical)**: `query_input/easy_queries_cleaned_300_plus_2026-07-14.csv`
- **Format**: CSV, UTF-8
- **Size**: 64,125 bytes
- **Last modified**: 2026-07-15 04:24:28 (local checkout time; content-committed 2026-07-15T04:31:54+08:00 in commit `de1cda4` "Add Jul 13-14 search relevance evaluation artifacts")
- **Git status**: tracked, clean (no uncommitted changes)
- **SHA-256**: `682ed08a97f69ff39317c923ac859fe2f085ab8e8d7b9dc7b1a0f31fa0b32f3e` — verified identical between original and copy
- **Header / fields**: `easy_id, query, source_file, source_row, language, query_type, contains_proper_noun, contains_number_or_model, contains_mixed_language, duplicate_status, overlaps_hard_68, overlaps_p0_12, easy_confidence, notes`
- **`query_column`**: `query`
- **`id_column`**: `easy_id`
- **`category_column`**: `query_type` (also `language`, `primary_scene`-equivalent not present; scene data lives only in the upstream seed-bank source file, not carried into this cleaned file)
- **Row count (incl. header)**: 329
- **Query count (data rows)**: 328
- **Empty query count**: 0
- **Duplicate query count**: 0 distinct duplicated strings (0 extra rows) — verified via Python `csv.DictReader` + `collections.Counter`
- **Original order**: preserved, `easy_id` runs `E001` → `E328` sequentially, matching original row order

## Selection chain / provenance (why this file, not another)

1. **Root candidate pool**: `docs/daily_report/7.7/05_simple_head_term_seed_bank_2026-07-07.csv` — 328 rows, columns `term,language,term_type,primary_scene,secondary_scene,...`. SHA-256 `393da01404746614a81ef5e2096cbf632cc2c851a711f132bec224947bfcf5b0`. Committed 2026-07-08 in `32cb4c3`.
2. Explicitly recommended as the correct 300+ easy-query starting pool by the project's own `docs/daily_report/7.11/search-optimization-stage-1/TEST_DATA_INVENTORY_2026-07-11.md` (Section 5+15): *"从未被执行测试"* (never previously executed), *"风格上最接近'easy/head-term'定义"* (closest in style to the "easy/head-term" definition). Four other 2026-07-07 candidate CSVs (04_high_signal_niche..., 02_expanded_from_58..., 03_net_new_scenario..., plus the 1,118-row taxonomy candidate table) were considered and explicitly **rejected** in `docs/daily_report/7.14/.../easy_query_input_inventory_2026-07-14.csv` for wrong difficulty tier, insufficient row count, wrong code path, or wrong purpose — see that inventory file for the full rejection rationale (copied evidence, not re-derived here).
3. The seed bank was carried through a documented cleaning step (`easy_id` assignment, language/type tagging, duplicate/overlap-with-Hard-68/overlap-with-P0-12 tagging) producing `easy_queries_cleaned_300_plus_2026-07-14.csv` — the **exact same file** consumed as `input_source` by the prior (optimized-code) 300+ Easy Query validation run, per that run's own manifest: `docs/daily_report/7.14/.../easy_query_validation_manifest_2026-07-14.json` → `"raw_count": 328, "clean_count": 328, "input_hash": "393da...b32f3e0"` — wait, manifest's `input_hash` field actually records the **seed-bank** file's hash (root pool), while `output_hashes.easy_queries_cleaned_300_plus_2026-07-14.csv` records the cleaned file's hash `682ed08a97f69ff39317c923ac859fe2f085ab8e8d7b9dc7b1a0f31fa0b32f3e` — **exactly matching** the SHA-256 recomputed independently on this file. This is a direct, verifiable manifest-hash match, satisfying the highest-priority selection criterion in the task instructions ("被之前正式 Easy Query 测试 Manifest 明确引用" + "SHA-256 与之前运行记录一致").
4. Row/query count (328) matches the prior run's reported `successful_runs: 328` and the meeting's "300+" framing.
5. That prior run explicitly used the **local, uncommitted, unpushed optimization branch** (`candidate_branch: baobao/search-relevance-phrase-alias-2026-07-09`, `candidate_head: c062e618b...`, `d_enabled: true, g_enabled: true, guard_enabled: true`) to execute these exact queries — meaning this file has query text established and frozen, but **no valid pre-optimization execution has ever been recorded against it**. That is precisely the gap this task's baseline run fills.

## Rejected candidates (for completeness — not re-analyzed independently, provenance taken from the existing inventory)

| File | Rows | Why rejected |
|---|---|---|
| `docs/daily_report/7.7/04_high_signal_niche_query_candidates_500_2026-07-07.csv` | 504 | Niche/hard-difficulty tier — feeds the 68 Hard Query set, not Easy |
| `docs/daily_report/7.7/02_expanded_from_58_query_candidates_2026-07-07.csv` | 188 | Below 300+ threshold |
| `docs/daily_report/7.7/03_net_new_scenario_seed_queries_2026-07-07.csv` | 98 | Below 300+ threshold, scenario-seed style |
| `curify-frontend/scripts/configs/search_eval_set.json` | 137 | Exercises a different code path (template-match, not the search-results pipeline) |
| `docs/daily_report/7.9/taxonomy_candidates_from_expanded_queries_2026-07-09.csv` | 1,118 | Explicitly forbidden as an Easy Query substitute per the Prompt 8 rules that produced the 07-14 run; flat taxonomy table, not a query test set |

## Compliance with task prohibitions

No merging, regeneration, dedup, reordering, or filtering was performed. The file was copied byte-for-byte (`cp` + SHA-256 verification, not re-typed or re-exported) into `query_input/`.
