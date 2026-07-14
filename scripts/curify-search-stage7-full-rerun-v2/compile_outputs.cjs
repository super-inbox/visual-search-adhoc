#!/usr/bin/env node
/**
 * Stage 7R Prompt 4 V2 -- compiles the 272 per-run JSON checkpoints (written
 * by run_full_68.cjs / run_one_mode.cjs) into:
 *   hard_queries_ablation_abcd_68_2026-07-14.csv       (272 rows, A/B/C/D)
 *   hard_queries_refreshed_dg_guarded_68_2026-07-14.csv (68 rows, D only)
 *   hard_queries_before_after_68_2026-07-14.csv         (68 rows, baseline vs D)
 * Also writes _compile_summary.json (raw counters consumed by the manifest
 * and the Markdown summary -- NOT one of the seven required deliverables
 * itself).
 *
 * Read-only against: gold query CSV, locked baseline copy. Never invents or
 * drops a row -- if a (query, mode) JSON checkpoint is missing, the CSV row
 * is still written with error="MISSING_RUN_CHECKPOINT".
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { parseCsv, writeCsv } = require("./csv_utils.cjs");
const { catalogInfo } = require("./engine.cjs");

const ADHOC_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const OUT_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/full-68-rerun-v2");
const QUERY_CSV = path.join(ADHOC_ROOT, "docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv");
const BASELINE_LOCKED_CSV = path.join(OUT_DIR, "hard_queries_baseline_locked_68_2026-07-14.csv");
const TMP_DIR = "/tmp/curify-stage7r-prompt4-v2/runs";

const MODE_CONTRACT = {
  A: { dEnabled: false, gEnabled: false, guardEnabled: false },
  B: { dEnabled: true, gEnabled: false, guardEnabled: false },
  C: { dEnabled: false, gEnabled: true, guardEnabled: true },
  D: { dEnabled: true, gEnabled: true, guardEnabled: true },
};
const MODES = ["A", "B", "C", "D"];

const PRODUCTION_BRANCH = "baobao/search-relevance-phrase-alias-2026-07-09";
const PRODUCTION_HEAD = "c062e618bce4044bedf718aadf59ff69f0999344";
const MODEL_PROVIDER = "openai";
const MODEL_NAME = "gpt-4o-mini";
const TEMPERATURE = 0.4;

function j(v) {
  return JSON.stringify(v === undefined ? null : v);
}

function deriveGuardFields(result) {
  if (!result) {
    return {
      subjectRejected: [], rewriteRejected: [], decompRejected: [],
      acceptedUnboundRewrites: [], boundRewrites: [], subjectPath: undefined,
      weakNumericGuardTriggered: "NOT_APPLICABLE", subjectGuardTriggered: "NOT_APPLICABLE",
      crossLanguageGuardTriggered: "NOT_APPLICABLE", rewriteAnchorGuardTriggered: "NOT_APPLICABLE",
      emptyTokenGuardTriggered: "NOT_APPLICABLE", subjectBindingTriggered: "NOT_APPLICABLE",
      piggybackGuardTriggered: "NOT_APPLICABLE",
    };
  }
  const rejectedSlots = result.diagnostics?.rejectedSlots ?? [];
  const subjectRejected = rejectedSlots.filter((r) => r.slotKey === "subject");
  const rewriteRejected = rejectedSlots.filter((r) => r.slotKey === "rewrite");
  const decompRejected = rejectedSlots.filter((r) => r.slotKey !== "rewrite" && r.slotKey !== "subject");
  const rewritePaths = (result.candidatePaths ?? []).filter((p) => p.slotKey === "rewrite");
  const subjectPath = (result.candidatePaths ?? []).find((p) => p.slotKey === "subject");
  const acceptedUnboundRewrites = rewritePaths.filter((p) => !p.subjectBound).map((p) => p.text);
  const boundRewrites = rewritePaths.filter((p) => p.subjectBound).map((p) => p.text);

  const weakNumericGuardTriggered = rewriteRejected.some((r) => r.reason === "WEAK_NUMERIC_ONLY_ANCHOR") || subjectRejected.some((r) => r.reason === "WEAK_NUMERIC_ONLY_ANCHOR");
  const subjectGuardTriggered = subjectRejected.length > 0 || subjectPath !== undefined;
  const crossLanguageGuardTriggered = rewriteRejected.some((r) => r.reason === "CROSS_LANGUAGE_WITHOUT_ANCHOR");
  const rewriteAnchorGuardTriggered = rewriteRejected.length > 0 || boundRewrites.length > 0;
  const emptyTokenGuardTriggered =
    (result.diagnostics?.emptyTokenPaths?.length ?? 0) > 0 ||
    rewriteRejected.some((r) => r.reason === "EMPTY_EXECUTABLE_TOKENS") ||
    subjectRejected.some((r) => r.reason === "EMPTY_EXECUTABLE_TOKENS");
  const subjectBindingTriggered = (result.candidatePaths ?? []).some((p) => p.subjectBound);
  const piggybackGuardTriggered = subjectBindingTriggered && boundRewrites.length > 0;

  return {
    subjectRejected, rewriteRejected, decompRejected, acceptedUnboundRewrites, boundRewrites, subjectPath,
    weakNumericGuardTriggered, subjectGuardTriggered, crossLanguageGuardTriggered,
    rewriteAnchorGuardTriggered, emptyTokenGuardTriggered, subjectBindingTriggered, piggybackGuardTriggered,
  };
}

function buildRow(queryId, query, queryOrder, mode, payload, catalog) {
  const contract = MODE_CONTRACT[mode];
  const result = payload && payload.result ? payload.result : null;
  const meta = (payload && payload._attempt_meta) || {};
  const g = deriveGuardFields(result);

  const decomposition = result ? result.multi?.decomposition || {} : {};
  const rewriteRaw = result ? result.multi?.rewrites || [] : [];
  const finalCount = result ? result.finalResultCount : null;
  const fullCatalog = Number.isFinite(finalCount) && finalCount === catalog.catalogSize;
  const thousandPlus = Number.isFinite(finalCount) && finalCount >= 1000;
  const zeroResult = Number.isFinite(finalCount) && finalCount === 0;
  const lowResult = result ? result.initialThinCount < 5 : "NOT_APPLICABLE";

  const notApplicableAB = !contract.gEnabled;

  return {
    run_id: `${queryId}-${mode}`,
    query_id: queryId,
    query,
    query_order: queryOrder,
    mode,
    d_enabled: contract.dEnabled,
    g_enabled: contract.gEnabled,
    guard_enabled: contract.guardEnabled,
    production_branch: PRODUCTION_BRANCH,
    production_head: PRODUCTION_HEAD,
    token_helper_sha256: "SEE_MANIFEST_SOURCE_HASHES",
    rewrite_helper_sha256: "SEE_MANIFEST_SOURCE_HASHES",
    catalog_sha256: "SEE_MANIFEST_SOURCE_HASHES",
    query_set_sha256: "SEE_MANIFEST_SOURCE_HASHES",
    model_provider: notApplicableAB ? "NOT_APPLICABLE" : MODEL_PROVIDER,
    model_name: notApplicableAB ? "NOT_APPLICABLE" : MODEL_NAME,
    temperature: notApplicableAB ? "NOT_APPLICABLE" : TEMPERATURE,
    started_at: payload ? payload.started_at : "NOT_RECORDED",
    completed_at: payload ? payload.completed_at : "NOT_RECORDED",
    duration_ms: payload ? payload.duration_ms : "NOT_RECORDED",
    cache_hit: "FALSE_FRESH_PROCESS_PER_RUN",
    cache_status: "PROCESS_ISOLATED_FRESH_CACHE_PER_RUN",
    attempt_count: meta.attemptCount ?? "NOT_RECORDED",
    first_attempt_error: meta.firstAttemptError ?? "NONE",
    retry_reason: meta.retryReason ?? "NONE",
    normalized_query: result ? j(result.tokens?.primary ? result.tokens : null) !== "null" ? "SEE_tokenization" : "NOT_RECORDED" : "NOT_APPLICABLE",
    protected_phrase: "NOT_RECORDED_HARNESS_LIMITATION",
    protected_phrase_matches: "NOT_RECORDED_HARNESS_LIMITATION",
    tokenization: result ? j(result.tokens) : "NOT_APPLICABLE",
    primary_tokens: result ? j(result.tokens?.primary ?? []) : "NOT_APPLICABLE",
    secondary_tokens: result ? j(result.tokens?.bigrams ?? []) : "NOT_APPLICABLE",
    aliases: result ? j((result.tokens?.aliasGroups ?? []).flat()) : "NOT_APPLICABLE",
    alias_groups: result ? j(result.tokens?.aliasGroups ?? []) : "NOT_APPLICABLE",
    first_pass_count: result ? result.initialThinCount : "NOT_APPLICABLE",
    first_pass_top_results: "NOT_RECORDED_SEE_final_top_10",
    low_result: lowResult,
    low_result_reason: result ? (lowResult === true ? "initialThinCount<LOW_RESULT_THRESHOLD" : "NOT_LOW") : "NOT_APPLICABLE",
    rewrite_triggered: result ? result.rewriteTriggered : "NOT_APPLICABLE",
    llm_called: result ? (notApplicableAB ? false : !!result.rewriteProviderCalled) : "NOT_APPLICABLE",
    raw_rewrite: notApplicableAB ? "NOT_APPLICABLE" : (result ? j(rewriteRaw) : "NOT_RECORDED"),
    raw_llm_response: notApplicableAB ? "NOT_APPLICABLE" : (result ? j(result.multi) : "NOT_RECORDED"),
    parsed_rewrites: notApplicableAB ? "NOT_APPLICABLE" : (result ? j(rewriteRaw) : "NOT_RECORDED"),
    accepted_rewrites: notApplicableAB ? "NOT_APPLICABLE" : j(g.acceptedUnboundRewrites),
    bound_rewrites: notApplicableAB ? "NOT_APPLICABLE" : j(g.boundRewrites),
    rejected_rewrites: notApplicableAB ? "NOT_APPLICABLE" : j(g.rewriteRejected.map((r) => r.slotValue)),
    rewrite_rejection_reasons: notApplicableAB ? "NOT_APPLICABLE" : j(g.rewriteRejected.map((r) => r.reason)),
    decomposition: notApplicableAB ? "NOT_APPLICABLE" : j(decomposition),
    raw_subject: notApplicableAB ? "NOT_APPLICABLE" : j(decomposition.subject ?? null),
    accepted_subject: notApplicableAB ? "NOT_APPLICABLE" : (g.subjectPath ? j(g.subjectPath.text) : "NOT_APPLICABLE_OR_REJECTED"),
    bound_subject: notApplicableAB ? "NOT_APPLICABLE" : (g.subjectPath && g.subjectPath.subjectBound ? j(g.subjectPath.text) : "NONE"),
    rejected_subject: notApplicableAB ? "NOT_APPLICABLE" : j(g.subjectRejected.map((r) => r.slotValue)),
    subject_rejection_reason: notApplicableAB ? "NOT_APPLICABLE" : j(g.subjectRejected.map((r) => r.reason)),
    generic_guard_triggered: notApplicableAB ? "NOT_APPLICABLE" : g.emptyTokenGuardTriggered,
    empty_token_guard_triggered: notApplicableAB ? "NOT_APPLICABLE" : g.emptyTokenGuardTriggered,
    subject_binding_triggered: notApplicableAB ? "NOT_APPLICABLE" : g.subjectBindingTriggered,
    rewrite_anchor_guard_triggered: notApplicableAB ? "NOT_APPLICABLE" : g.rewriteAnchorGuardTriggered,
    weak_numeric_guard_triggered: notApplicableAB ? "NOT_APPLICABLE" : g.weakNumericGuardTriggered,
    cross_language_guard_triggered: notApplicableAB ? "NOT_APPLICABLE" : g.crossLanguageGuardTriggered,
    piggyback_guard_triggered: notApplicableAB ? "NOT_APPLICABLE" : g.piggybackGuardTriggered,
    no_valid_rewrite_path: notApplicableAB ? "NOT_APPLICABLE" : (result ? result.diagnostics?.noValidRewritePath : "NOT_RECORDED"),
    final_query_paths: result ? j((result.candidatePaths ?? []).map((p) => p.text)) : "NOT_APPLICABLE",
    actual_executed_queries: result ? j([query, ...(result.candidatePaths ?? []).map((p) => p.text)]) : "NOT_APPLICABLE",
    per_path_result_counts: "NOT_RECORDED_HARNESS_LIMITATION",
    pre_merge_count: result ? result.preMergeCount : "NOT_APPLICABLE",
    merged_count: result ? result.postMergeCount : "NOT_APPLICABLE",
    dedup_count: result ? result.dedupCount : "NOT_APPLICABLE",
    final_result_count: Number.isFinite(finalCount) ? finalCount : "NOT_RECORDED",
    final_top_10: result ? j(result.top10) : "NOT_APPLICABLE",
    full_catalog: fullCatalog,
    thousand_plus: thousandPlus,
    zero_result: zeroResult,
    original_query_results_preserved: "TRUE_BY_CONSTRUCTION",
    original_entity_preserved: "SEE_MANUAL_REVIEW",
    auto_judge_label: "NOT_APPLICABLE_NO_LLM_JUDGE_THIS_STAGE",
    auto_judge_reason: "NOT_APPLICABLE_NO_LLM_JUDGE_THIS_STAGE",
    error: payload ? (payload.error || "") : "MISSING_RUN_CHECKPOINT",
    timeout: payload ? !!payload.timeout : false,
    notes: `openai_key_present=${payload ? payload.openai_api_key_present : "NOT_RECORDED"}`,
  };
}

function main() {
  const goldRows = parseCsv(fs.readFileSync(QUERY_CSV, "utf-8"));
  const baseRows = parseCsv(fs.readFileSync(BASELINE_LOCKED_CSV, "utf-8"));
  const queries = [];
  for (let i = 0; i < 68; i++) {
    queries.push({ queryId: baseRows[i].query_id, query: goldRows[i].query, queryOrder: i + 1, baseline: baseRows[i] });
  }
  const catalog = catalogInfo();

  const ablationRows = [];
  const seen = new Set();
  let missing = 0;

  for (const q of queries) {
    for (const mode of MODES) {
      const key = `${q.queryId}-${mode}`;
      if (seen.has(key)) throw new Error(`DUPLICATE ${key}`);
      seen.add(key);
      const jsonPath = path.join(TMP_DIR, `${key}.json`);
      let payload = null;
      if (fs.existsSync(jsonPath)) {
        payload = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
      } else {
        missing++;
      }
      ablationRows.push(buildRow(q.queryId, q.query, q.queryOrder, mode, payload, catalog));
    }
  }

  const ABLATION_FIELDS = [
    "run_id", "query_id", "query", "query_order", "mode", "d_enabled", "g_enabled", "guard_enabled",
    "production_branch", "production_head", "token_helper_sha256", "rewrite_helper_sha256",
    "catalog_sha256", "query_set_sha256", "model_provider", "model_name", "temperature",
    "started_at", "completed_at", "duration_ms", "cache_hit", "cache_status",
    "attempt_count", "first_attempt_error", "retry_reason",
    "normalized_query", "protected_phrase", "protected_phrase_matches",
    "tokenization", "primary_tokens", "secondary_tokens", "aliases", "alias_groups",
    "first_pass_count", "first_pass_top_results", "low_result", "low_result_reason",
    "rewrite_triggered", "llm_called", "raw_rewrite", "raw_llm_response", "parsed_rewrites",
    "accepted_rewrites", "bound_rewrites", "rejected_rewrites", "rewrite_rejection_reasons",
    "decomposition", "raw_subject", "accepted_subject", "bound_subject", "rejected_subject", "subject_rejection_reason",
    "generic_guard_triggered", "empty_token_guard_triggered", "subject_binding_triggered",
    "rewrite_anchor_guard_triggered", "weak_numeric_guard_triggered", "cross_language_guard_triggered",
    "piggyback_guard_triggered", "no_valid_rewrite_path",
    "final_query_paths", "actual_executed_queries", "per_path_result_counts",
    "pre_merge_count", "merged_count", "dedup_count", "final_result_count", "final_top_10",
    "full_catalog", "thousand_plus", "zero_result",
    "original_query_results_preserved", "original_entity_preserved",
    "auto_judge_label", "auto_judge_reason", "error", "timeout", "notes",
  ];

  const ablationOut = path.join(OUT_DIR, "hard_queries_ablation_abcd_68_2026-07-14.csv");
  writeCsv(ablationOut, ABLATION_FIELDS, ablationRows);
  console.log(`[compile] wrote ${ablationRows.length} rows -> ${ablationOut}`);

  // ---- D Guarded (68 rows, derived, no re-run) -----------------------------
  const dRows = ablationRows.filter((r) => r.mode === "D");
  const dOut = path.join(OUT_DIR, "hard_queries_refreshed_dg_guarded_68_2026-07-14.csv");
  writeCsv(dOut, ABLATION_FIELDS, dRows);
  console.log(`[compile] wrote ${dRows.length} D rows -> ${dOut}`);

  // ---- Before/After ---------------------------------------------------------
  const BEFORE_AFTER_FIELDS = [
    "query_id", "query", "baseline_source", "baseline_result_count", "baseline_top_results", "baseline_relevance",
    "baseline_tokens", "baseline_rewrite_signal",
    "after_result_count", "after_top_10", "after_first_pass_count", "after_low_result", "after_rewrite_triggered",
    "after_raw_rewrite", "after_accepted_rewrites", "after_bound_rewrites", "after_rejected_rewrites",
    "after_rejection_reasons", "after_decomposition", "after_guard_triggers", "after_final_paths",
    "after_original_entity_preserved",
    "result_count_delta", "result_count_ratio", "zero_result_before", "zero_result_after",
    "low_result_before", "low_result_after", "thousand_plus_before", "thousand_plus_after",
    "full_catalog_before", "full_catalog_after", "top10_intent_before", "top10_intent_after",
    "auto_judge_before", "auto_judge_after",
    "human_relevance_label", "human_review_reason", "improvement_verdict", "regression",
    "comparability_status", "notes",
  ];
  const beforeAfterRows = [];
  for (const q of queries) {
    const b = q.baseline;
    const dRow = dRows.find((r) => r.query_id === q.queryId);
    const baselineCount = Number(b.baseline_result_count);
    const afterCount = Number.isFinite(Number(dRow.final_result_count)) ? Number(dRow.final_result_count) : null;
    const guardTriggers = {
      empty_token: dRow.empty_token_guard_triggered, subject_binding: dRow.subject_binding_triggered,
      rewrite_anchor: dRow.rewrite_anchor_guard_triggered, weak_numeric: dRow.weak_numeric_guard_triggered,
      cross_language: dRow.cross_language_guard_triggered, piggyback: dRow.piggyback_guard_triggered,
    };
    beforeAfterRows.push({
      query_id: q.queryId,
      query: q.query,
      baseline_source: b.baseline_source_file,
      baseline_result_count: b.baseline_result_count,
      baseline_top_results: b.baseline_top_results_json,
      baseline_relevance: b.baseline_relevance_verdict,
      baseline_tokens: b.baseline_tokens_json,
      baseline_rewrite_signal: b.baseline_rewrite_triggered,
      after_result_count: dRow.final_result_count,
      after_top_10: dRow.final_top_10,
      after_first_pass_count: dRow.first_pass_count,
      after_low_result: dRow.low_result,
      after_rewrite_triggered: dRow.rewrite_triggered,
      after_raw_rewrite: dRow.raw_rewrite,
      after_accepted_rewrites: dRow.accepted_rewrites,
      after_bound_rewrites: dRow.bound_rewrites,
      after_rejected_rewrites: dRow.rejected_rewrites,
      after_rejection_reasons: dRow.rewrite_rejection_reasons,
      after_decomposition: dRow.decomposition,
      after_guard_triggers: j(guardTriggers),
      after_final_paths: dRow.final_query_paths,
      after_original_entity_preserved: "SEE_MANUAL_REVIEW",
      result_count_delta: afterCount !== null && Number.isFinite(baselineCount) ? afterCount - baselineCount : "NOT_RECORDED",
      result_count_ratio: afterCount !== null && Number.isFinite(baselineCount) && baselineCount > 0 ? (afterCount / baselineCount).toFixed(3) : "NOT_APPLICABLE",
      zero_result_before: b.baseline_zero_result,
      zero_result_after: dRow.zero_result,
      low_result_before: b.baseline_low_result,
      low_result_after: dRow.low_result,
      thousand_plus_before: Number.isFinite(baselineCount) && baselineCount >= 1000,
      thousand_plus_after: dRow.thousand_plus,
      full_catalog_before: Number.isFinite(baselineCount) && baselineCount === catalog.catalogSize,
      full_catalog_after: dRow.full_catalog,
      top10_intent_before: "SEE_MANUAL_REVIEW",
      top10_intent_after: "SEE_MANUAL_REVIEW",
      auto_judge_before: "NOT_APPLICABLE_NO_LLM_JUDGE_THIS_STAGE",
      auto_judge_after: "NOT_APPLICABLE_NO_LLM_JUDGE_THIS_STAGE",
      human_relevance_label: "PENDING_MANUAL_REVIEW",
      human_review_reason: "PENDING_MANUAL_REVIEW",
      improvement_verdict: "PENDING_MANUAL_REVIEW",
      regression: "PENDING_MANUAL_REVIEW",
      comparability_status: "D_OFF_IMPLEMENTATION_REEXPRESSED; MODEL_NONDETERMINISM_APPLIES",
      notes: "",
    });
  }
  const beforeAfterOut = path.join(OUT_DIR, "hard_queries_before_after_68_2026-07-14.csv");
  writeCsv(beforeAfterOut, BEFORE_AFTER_FIELDS, beforeAfterRows);
  console.log(`[compile] wrote ${beforeAfterRows.length} before/after rows -> ${beforeAfterOut}`);

  const summary = {
    total_runs: ablationRows.length,
    missing_runs: missing,
    duplicate_runs: 0,
    modes: MODES.map((m) => ({
      mode: m,
      rows: ablationRows.filter((r) => r.mode === m).length,
      errors: ablationRows.filter((r) => r.mode === m && r.error).length,
      timeouts: ablationRows.filter((r) => r.mode === m && r.timeout === true).length,
      zero_result: ablationRows.filter((r) => r.mode === m && r.zero_result === true).length,
      thousand_plus: ablationRows.filter((r) => r.mode === m && r.thousand_plus === true).length,
      full_catalog: ablationRows.filter((r) => r.mode === m && r.full_catalog === true).length,
      rewrite_triggered: ablationRows.filter((r) => r.mode === m && r.rewrite_triggered === true).length,
      llm_called: ablationRows.filter((r) => r.mode === m && r.llm_called === true).length,
    })),
    catalog_size: catalog.catalogSize,
  };
  fs.writeFileSync(path.join(__dirname, "_compile_summary.json"), JSON.stringify(summary, null, 2));
  console.log("[compile] summary:", JSON.stringify(summary, null, 2));
}

main();
