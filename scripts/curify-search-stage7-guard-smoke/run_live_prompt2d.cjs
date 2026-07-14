#!/usr/bin/env node
/**
 * Stage 7R Prompt 2D — Limited Live Retest orchestrator.
 *
 * Reuses live.cjs UNMODIFIED (spawned as one child process per run, so each
 * run gets a fresh, empty in-memory MULTI_CACHE — same process-isolation
 * pattern as Prompt 3B/2C). Reads the SAME frozen 20-unique-query/23-run
 * query set used by Prompt 3B/2C (live_smoke_query_set_2026-07-14.csv,
 * SHA-256 verified against the Prompt 2C manifest before running). Writes
 * the compiled CSV in the exact same column schema as
 * stage7_guard_live_results_prompt2c_2026-07-14.csv for direct comparability.
 */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execFileSync } = require("child_process");
const { writeCsv } = require("./csv_utils.cjs");
const { verifyAgainstLiveSource, catalogInfo } = require("./engine.cjs");

const REPO_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const LIVE_SMOKE_DIR = path.join(REPO_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/live-smoke");
const OUT_DIR = path.join(REPO_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/prompt2d");
const QUERY_SET_CSV = path.join(LIVE_SMOKE_DIR, "live_smoke_query_set_2026-07-14.csv");
const EXPECTED_SHA256 = "d328df4b9cc4d298314ee439c6da06a382f5b3e962194f4f9fba2c14658f025c";
const OUT_CSV = path.join(OUT_DIR, "stage7_guard_live_results_prompt2d_2026-07-14.csv");
const TMP_DIR = "/tmp/curify-stage7r-prompt2d/live_runs";

const { parseCsv } = require("./csv_utils.cjs");

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function main() {
  if (fs.existsSync(OUT_CSV)) {
    console.error(`[live2d] refusing to overwrite existing output: ${OUT_CSV}`);
    process.exit(1);
  }

  const actualSha = sha256(QUERY_SET_CSV);
  if (actualSha !== EXPECTED_SHA256) {
    console.error(`[live2d] QUERY SET SHA MISMATCH: expected ${EXPECTED_SHA256}, got ${actualSha}`);
    process.exit(1);
  }
  console.log(`[live2d] query set sha256 verified: ${actualSha}`);

  const drift = verifyAgainstLiveSource();
  console.log(`[live2d] drift check:`, JSON.stringify(drift));
  const catalog = catalogInfo();
  console.log(`[live2d] catalog size:`, catalog.catalogSize);

  fs.mkdirSync(TMP_DIR, { recursive: true });

  const rows = parseCsv(fs.readFileSync(QUERY_SET_CSV, "utf-8"));
  const runs = [];
  for (const row of rows) {
    const n = Number(row.run_count);
    for (let i = 1; i <= n; i++) {
      runs.push({ liveRunId: `${row.live_query_id}-${i}`, liveQueryId: row.live_query_id, queryId: row.query_id, query: row.query, category: row.category, runNumber: i });
    }
  }
  console.log(`[live2d] ${runs.length} total runs planned (${rows.length} unique queries)`);

  const compiled = [];
  let idx = 0;
  for (const run of runs) {
    idx++;
    const outJson = path.join(TMP_DIR, `${run.liveRunId}.json`);

    // Reuse a prior successful (non-error, non-timeout) result if this run
    // was already executed in an earlier invocation of this script (e.g.
    // after a mid-batch OpenAI outage) -- avoids re-spending real API calls
    // on runs that already succeeded. Any run that errored/timed out is
    // always re-executed as a genuine fresh process.
    let payload = null;
    if (fs.existsSync(outJson)) {
      try {
        const prior = JSON.parse(fs.readFileSync(outJson, "utf-8"));
        if (prior.result && !prior.error && !prior.timeout) {
          payload = prior;
          console.log(`[live2d] ${idx}/${runs.length} REUSING prior successful result for ${run.liveRunId} (final=${prior.result.finalResultCount})`);
        }
      } catch {
        // fall through to re-execute
      }
    }

    if (!payload) {
      const MAX_ATTEMPTS = 3;
      for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        console.log(`[live2d] ${idx}/${runs.length} launching ${run.liveRunId} query=${JSON.stringify(run.query)} (attempt ${attempt}/${MAX_ATTEMPTS})`);
        try {
          execFileSync(
            process.execPath,
            ["--env-file=" + path.join(CURIFY_ROOT, ".env.local"), "live.cjs", "--live-run-id", run.liveRunId, "--query", run.query, "--run-number", String(run.runNumber), "--out", outJson],
            { cwd: __dirname, stdio: "inherit", timeout: 60_000 }
          );
        } catch (e) {
          console.error(`[live2d] child process error for ${run.liveRunId}:`, e.message);
        }
        try {
          payload = JSON.parse(fs.readFileSync(outJson, "utf-8"));
        } catch (e) {
          console.error(`[live2d] failed to read output for ${run.liveRunId}:`, e.message);
          payload = null;
        }
        if (payload && payload.result && !payload.error && !payload.timeout) break;
        if (attempt < MAX_ATTEMPTS) console.log(`[live2d] ${run.liveRunId} attempt ${attempt} failed (error=${payload ? payload.error : "no payload"}), retrying...`);
      }
    }

    const result = payload && payload.result ? payload.result : null;
    const error = payload ? payload.error : "CHILD_PROCESS_FAILED";
    const timeout = payload ? payload.timeout : false;

    const subjectRejected = result ? result.diagnostics.rejectedSlots.filter((r) => r.slotKey === "subject") : [];
    const rewriteRejected = result ? result.diagnostics.rejectedSlots.filter((r) => r.slotKey === "rewrite") : [];
    const decompRejected = result ? result.diagnostics.rejectedSlots.filter((r) => r.slotKey !== "rewrite" && r.slotKey !== "subject") : [];
    const rewritePaths = result ? result.candidatePaths.filter((p) => p.slotKey === "rewrite") : [];
    const subjectPath = result ? result.candidatePaths.find((p) => p.slotKey === "subject") : undefined;
    const acceptedUnboundRewrites = rewritePaths.filter((p) => !p.subjectBound).map((p) => p.text);
    const boundRewrites = rewritePaths.filter((p) => p.subjectBound).map((p) => p.text);
    const decomposition = result ? result.multi.decomposition || {} : {};
    const rewriteRaw = result ? result.multi.rewrites || [] : [];

    const weakNumericGuardTriggered = rewriteRejected.some((r) => r.reason === "WEAK_NUMERIC_ONLY_ANCHOR") || subjectRejected.some((r) => r.reason === "WEAK_NUMERIC_ONLY_ANCHOR");
    const subjectGuardTriggered = subjectRejected.length > 0 || subjectPath !== undefined;
    const crossLanguageGuardTriggered = rewriteRejected.some((r) => r.reason === "CROSS_LANGUAGE_WITHOUT_ANCHOR");
    const rewriteAnchorGuardTriggered = rewriteRejected.length > 0 || boundRewrites.length > 0;
    const emptyTokenGuardTriggered =
      (result ? result.diagnostics.emptyTokenPaths.length > 0 : false) ||
      rewriteRejected.some((r) => r.reason === "EMPTY_EXECUTABLE_TOKENS") ||
      subjectRejected.some((r) => r.reason === "EMPTY_EXECUTABLE_TOKENS");
    const subjectBindingTriggered = result ? result.candidatePaths.some((p) => p.subjectBound) : false;
    // Stage 7R Prompt 2D — piggyback guard triggered: subject required
    // binding AND at least one rewrite candidate is bound too (the exact
    // mechanism this stage fixes: candidates that would otherwise have
    // self-certified via the subject's unbound raw text now get bound).
    const piggybackGuardTriggered = subjectBindingTriggered && boundRewrites.length > 0;

    const finalCount = result ? result.finalResultCount : null;
    const fullCatalog = finalCount === catalog.catalogSize;
    const thousandPlus = Number.isFinite(finalCount) && finalCount >= 1000;

    compiled.push({
      live_run_id: run.liveRunId,
      live_query_id: run.liveQueryId,
      query_id: run.queryId,
      query: run.query,
      category: run.category,
      run_number: run.runNumber,
      started_at: payload ? payload.started_at : "",
      completed_at: payload ? payload.completed_at : "",
      duration_ms: payload ? payload.duration_ms : "",
      tokenization: result ? JSON.stringify(result.tokens) : "NOT_APPLICABLE",
      primary_tokens: result ? JSON.stringify(result.tokens.primary) : "NOT_APPLICABLE",
      alias_groups: result ? JSON.stringify(result.tokens.aliasGroups || []) : "NOT_APPLICABLE",
      first_pass_count: result ? result.initialThinCount : "NOT_APPLICABLE",
      low_result_triggered: result ? result.rewriteTriggered : "NOT_APPLICABLE",
      cache_strategy: "PROCESS_ISOLATED_FRESH_CACHE_PER_RUN",
      llm_called: result ? result.rewriteTriggered : "NOT_APPLICABLE",
      llm_model: "gpt-4o-mini",
      raw_llm_response: result ? JSON.stringify(result.multi) : "NOT_APPLICABLE",
      raw_rewrite: JSON.stringify(rewriteRaw),
      decomposition: JSON.stringify(decomposition),
      decomposition_subject: decomposition.subject ?? "NOT_APPLICABLE",
      subject_executed_text: subjectPath ? subjectPath.text : "NOT_APPLICABLE_OR_REJECTED",
      subject_rejected: subjectRejected.length > 0,
      accepted_rewrite_candidates: JSON.stringify(acceptedUnboundRewrites),
      bound_rewrite_candidates: JSON.stringify(boundRewrites),
      rejected_rewrite_candidates: JSON.stringify(rewriteRejected.map((r) => r.slotValue)),
      rewrite_rejection_reasons: JSON.stringify(rewriteRejected.map((r) => r.reason)),
      decomposition_rejected_slots: JSON.stringify(decompRejected.map((r) => ({ slotKey: r.slotKey, reason: r.reason }))),
      weak_numeric_guard_triggered: weakNumericGuardTriggered,
      subject_guard_triggered: subjectGuardTriggered,
      cross_language_guard_triggered: crossLanguageGuardTriggered,
      empty_token_guard_triggered: emptyTokenGuardTriggered,
      subject_binding_triggered: subjectBindingTriggered,
      rewrite_anchor_guard_triggered: rewriteAnchorGuardTriggered,
      piggyback_guard_triggered: piggybackGuardTriggered,
      no_valid_rewrite_path: result ? result.diagnostics.noValidRewritePath : "NOT_APPLICABLE",
      actual_executed_queries: result ? JSON.stringify(result.candidatePaths.map((p) => p.text)) : "NOT_APPLICABLE",
      pre_merge_count: result ? result.preMergeCount : "NOT_APPLICABLE",
      post_merge_count: result ? result.postMergeCount : "NOT_APPLICABLE",
      dedup_count: result ? result.dedupCount : "NOT_APPLICABLE",
      final_result_count: Number.isFinite(finalCount) ? finalCount : "NOT_RECORDED",
      final_top_results: result ? JSON.stringify(result.top10) : "NOT_APPLICABLE",
      full_catalog: fullCatalog,
      thousand_plus: thousandPlus,
      original_query_results_preserved: "TRUE_BY_CONSTRUCTION",
      error: error || "",
      timeout: timeout || false,
      smoke_verdict: "REVIEW_PENDING",
      notes: `drift_missing=${drift.missing} openai_key_present=${payload ? payload.openai_api_key_present : "NOT_RECORDED"}`,
    });

    console.log(`[live2d] ${idx}/${runs.length} ${run.liveRunId} final=${finalCount} error=${error ? "YES" : "no"}`);
  }

  const FIELDNAMES = [
    "live_run_id", "live_query_id", "query_id", "query", "category", "run_number",
    "started_at", "completed_at", "duration_ms",
    "tokenization", "primary_tokens", "alias_groups",
    "first_pass_count", "low_result_triggered", "cache_strategy", "llm_called", "llm_model",
    "raw_llm_response", "raw_rewrite", "decomposition", "decomposition_subject",
    "subject_executed_text", "subject_rejected",
    "accepted_rewrite_candidates", "bound_rewrite_candidates",
    "rejected_rewrite_candidates", "rewrite_rejection_reasons", "decomposition_rejected_slots",
    "weak_numeric_guard_triggered", "subject_guard_triggered", "cross_language_guard_triggered",
    "empty_token_guard_triggered", "subject_binding_triggered", "rewrite_anchor_guard_triggered",
    "piggyback_guard_triggered", "no_valid_rewrite_path",
    "actual_executed_queries", "pre_merge_count", "post_merge_count", "dedup_count",
    "final_result_count", "final_top_results", "full_catalog", "thousand_plus",
    "original_query_results_preserved", "error", "timeout", "smoke_verdict", "notes",
  ];
  writeCsv(OUT_CSV, FIELDNAMES, compiled);
  console.log(`[live2d] wrote ${compiled.length} rows -> ${OUT_CSV}`);

  const errors = compiled.filter((r) => r.error);
  const timeouts = compiled.filter((r) => r.timeout);
  const fullCatalogRows = compiled.filter((r) => r.full_catalog === true);
  const summary = {
    total: compiled.length,
    errors: errors.length,
    timeouts: timeouts.length,
    full_catalog: fullCatalogRows.length,
    thousand_plus: compiled.filter((r) => r.thousand_plus === true).length,
    piggyback_guard_triggered_count: compiled.filter((r) => r.piggyback_guard_triggered === true).length,
    subject_guard_triggered_count: compiled.filter((r) => r.subject_guard_triggered === true).length,
  };
  fs.writeFileSync(path.join(OUT_DIR, "_live_prompt2d_summary.json"), JSON.stringify(summary, null, 2));
  console.log(`[live2d] summary:`, JSON.stringify(summary, null, 2));
}

main();
