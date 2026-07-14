#!/usr/bin/env node
/**
 * Stage 7R Prompt 2B — Deterministic Replay re-run against the current
 * (Guard R) working tree.
 *
 * Companion to replay.cjs (Prompt 3), NOT a modification of it — Prompt 3's
 * output file (stage7_guard_replay_results_2026-07-14.csv) is untouched and
 * remains the Prompt-2-era baseline. This script re-runs the EXACT SAME
 * frozen smoke_test_query_set_2026-07-14.csv Phase-A rows through the SAME
 * ./engine.cjs (which now requires the freshly-rebuilt ./_bundle_current.cjs
 * containing Guard R's evaluateRewriteCandidate + the updated
 * flattenPathsWithDiagnostics — see build_bundle.cjs, re-run before this
 * script), using the SAME 7.13-recorded raw rewrite/decomposition JSON —
 * NO LLM call is made here either.
 *
 * The "old" baseline for this run is Prompt 3's own new_result_count (i.e.
 * "after Guard 1+2, before Guard R") rather than the original Stage 7
 * historical count, so the delta this script reports isolates Guard R's
 * incremental effect. The original Stage 7 historical count is carried
 * forward as `stage7_historical_result_count` for full context.
 *
 * Usage: node replay_prompt2b.cjs
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { parseCsv, writeCsv } = require("./csv_utils.cjs");
const { runOne, catalogInfo, verifyAgainstLiveSource } = require("./engine.cjs");

const ADHOC_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const STAGE7_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.13/search-optimization-stage-7");
const SMOKE_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/smoke-test");
const PROMPT2B_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/prompt2b");
const QUERY_SET_CSV = path.join(SMOKE_DIR, "smoke_test_query_set_2026-07-14.csv");
const PROMPT3_REPLAY_CSV = path.join(SMOKE_DIR, "stage7_guard_replay_results_2026-07-14.csv");
const OUT_CSV = path.join(PROMPT2B_DIR, "stage7_guard_replay_results_prompt2b_2026-07-14.csv");

const CATALOG_SIZE = catalogInfo().catalogSize; // read dynamically — never hardcoded

function safeJsonParse(s, fallback) {
  if (s === undefined || s === null || s === "") return fallback;
  try {
    return JSON.parse(s);
  } catch {
    return fallback;
  }
}

function loadAblationByQidMode() {
  const text = fs.readFileSync(path.join(STAGE7_DIR, "hard_queries_68_ablation.csv"), "utf-8");
  const rows = parseCsv(text);
  const byKey = new Map();
  for (const r of rows) byKey.set(`${r.query_id}|${r.mode}`, r);
  return byKey;
}

function loadPrompt3ByQidMode() {
  const text = fs.readFileSync(PROMPT3_REPLAY_CSV, "utf-8");
  const rows = parseCsv(text);
  const byKey = new Map();
  for (const r of rows) byKey.set(`${r.query_id}|${r.source_mode}`, r);
  return byKey;
}

function classifyVerdict({ oldCount, newCount, oldFullCatalog, newFullCatalog, rewriteAnchorGuardTriggered, newTop10, query, error }) {
  if (error) return "BLOCKED";
  const eliminatedFullCatalog = oldFullCatalog && !newFullCatalog;
  const droppedBelow1000 = oldCount >= 1000 && newCount < 1000;
  const substantialDrop = oldCount > 0 && newCount / oldCount <= 0.7 && newCount < oldCount;

  const queryLower = query.toLowerCase();
  const queryTokens = queryLower.split(/[\s,，、。]+/).filter((t) => t.length >= 2);
  const top10Blob = newTop10
    .map((t) => `${t.title ?? ""} ${t.category ?? ""} ${(t.tags ?? []).join(" ")}`)
    .join(" ")
    .toLowerCase();
  const anyKeywordHit = queryTokens.some((t) => top10Blob.includes(t));

  if (newFullCatalog) return "FAIL";
  if (newCount >= 1000 && !eliminatedFullCatalog) {
    return rewriteAnchorGuardTriggered ? "PARTIAL" : "FAIL";
  }
  if (eliminatedFullCatalog || droppedBelow1000 || substantialDrop) {
    return anyKeywordHit || newCount <= 20 ? "PASS" : "PARTIAL";
  }
  if (newCount === oldCount) return "PARTIAL"; // unchanged — Guard R had no effect either way
  return "PARTIAL";
}

async function main() {
  console.log("[replay2b] drift check:", JSON.stringify(verifyAgainstLiveSource()));
  console.log("[replay2b] catalog size:", CATALOG_SIZE);

  if (fs.existsSync(OUT_CSV)) {
    console.error(`[replay2b] refusing to overwrite existing output: ${OUT_CSV}`);
    process.exit(1);
  }
  if (!fs.existsSync(PROMPT2B_DIR)) fs.mkdirSync(PROMPT2B_DIR, { recursive: true });

  const queryRows = parseCsv(fs.readFileSync(QUERY_SET_CSV, "utf-8")).filter((r) => r.required_phase === "A");
  const ablation = loadAblationByQidMode();
  const prompt3 = loadPrompt3ByQidMode();

  const results = [];
  let replayId = 0;

  const priorityIds = ["Q39", "Q40", "Q42"];
  const ordered = [
    ...queryRows.filter((r) => priorityIds.includes(r.query_id)),
    ...queryRows.filter((r) => !priorityIds.includes(r.query_id)),
  ];

  let gateFailure = null;

  for (const row of ordered) {
    replayId++;
    const qid = row.query_id;
    const mode = row.old_mode;
    const key = `${qid}|${mode}`;
    const src = ablation.get(key);
    const p3 = prompt3.get(key);

    let status = "OK";
    let error = "";
    let rewriteRaw = null;
    let decomposition = {};
    let result = null;

    if (!src) {
      status = "REPLAY_BLOCKED_MISSING_INPUT";
      error = `no ablation row found for ${key}`;
    } else if (!p3) {
      status = "REPLAY_BLOCKED_MISSING_INPUT";
      error = `no Prompt 3 baseline row found for ${key} in stage7_guard_replay_results_2026-07-14.csv`;
    } else {
      const rewriteOutput = safeJsonParse(src.rewrite_output_json, null);
      if (rewriteOutput === null && src.rewrite_triggered === "true") {
        status = "REPLAY_BLOCKED_MISSING_INPUT";
        error = "rewrite_output_json missing/unparseable but rewrite_triggered=true";
      } else {
        rewriteRaw = rewriteOutput;
        decomposition = rewriteOutput?.decomposition ?? {};
        try {
          result = await runOne(row.query, {
            multiPathsOverride: rewriteOutput ?? { rewrites: [], decomposition: {} },
          });
        } catch (e) {
          status = "ERROR";
          error = String(e && e.stack ? e.stack : e);
        }
      }
    }

    const oldPrompt3Count = p3 ? Number(p3.new_result_count) : NaN;
    const stage7HistoricalCount = p3 ? Number(p3.old_result_count) : NaN;
    const oldFullCatalog = Number.isFinite(oldPrompt3Count) && oldPrompt3Count === CATALOG_SIZE;
    const oldThousandPlus = Number.isFinite(oldPrompt3Count) && oldPrompt3Count >= 1000;
    const newCount = result ? result.finalResultCount : null;
    const newFullCatalog = newCount === CATALOG_SIZE;
    const newThousandPlus = Number.isFinite(newCount) && newCount >= 1000;

    const rewriteRejected = result ? result.diagnostics.rejectedSlots.filter((r) => r.slotKey === "rewrite") : [];
    const decompRejected = result ? result.diagnostics.rejectedSlots.filter((r) => r.slotKey !== "rewrite") : [];
    const rewritePaths = result ? result.candidatePaths.filter((p) => p.slotKey === "rewrite") : [];
    const acceptedUnboundRewrites = rewritePaths.filter((p) => !p.subjectBound).map((p) => p.text);
    const boundRewrites = rewritePaths.filter((p) => p.subjectBound).map((p) => p.text);
    const originalRewriteCandidates = rewriteRaw?.rewrites ?? [];
    const rewriteAnchorGuardTriggered =
      rewriteRejected.length > 0 || boundRewrites.length > 0;
    const emptyTokenGuardTriggered =
      (result ? result.diagnostics.emptyTokenPaths.length > 0 : false) ||
      rewriteRejected.some((r) => r.reason === "EMPTY_EXECUTABLE_TOKENS") ||
      decompRejected.some((r) => r.reason === "EMPTY_EXECUTABLE_TOKENS");
    const subjectBindingTriggered = result ? result.candidatePaths.some((p) => p.subjectBound) : false;

    let verdict = "BLOCKED";
    if (result) {
      verdict = classifyVerdict({
        oldCount: oldPrompt3Count,
        newCount,
        oldFullCatalog,
        newFullCatalog,
        rewriteAnchorGuardTriggered,
        newTop10: result.top10,
        query: row.query,
        error: status !== "OK" ? error : null,
      });
    }

    const countDelta = Number.isFinite(oldPrompt3Count) && Number.isFinite(newCount) ? newCount - oldPrompt3Count : "NOT_APPLICABLE";
    const countRatio = Number.isFinite(oldPrompt3Count) && oldPrompt3Count > 0 && Number.isFinite(newCount) ? +(newCount / oldPrompt3Count).toFixed(4) : "NOT_APPLICABLE";

    results.push({
      replay_id: `R${String(replayId).padStart(3, "0")}`,
      query_id: qid,
      query: row.query,
      source_mode: mode,
      old_prompt3_result_count: Number.isFinite(oldPrompt3Count) ? oldPrompt3Count : "NOT_RECORDED",
      stage7_historical_result_count: Number.isFinite(stage7HistoricalCount) ? stage7HistoricalCount : "NOT_RECORDED",
      new_prompt2b_result_count: Number.isFinite(newCount) ? newCount : "NOT_RECORDED",
      count_delta: countDelta,
      count_ratio: countRatio,
      raw_rewrite: rewriteRaw ? JSON.stringify(rewriteRaw) : "NOT_RECORDED",
      parsed_rewrites: JSON.stringify(originalRewriteCandidates),
      decomposition: JSON.stringify(decomposition),
      original_rewrite_candidates: JSON.stringify(originalRewriteCandidates),
      accepted_rewrite_candidates: JSON.stringify(acceptedUnboundRewrites),
      bound_rewrite_candidates: JSON.stringify(boundRewrites),
      rejected_rewrite_candidates: JSON.stringify(rewriteRejected.map((r) => r.slotValue)),
      rewrite_rejection_reasons: JSON.stringify(rewriteRejected.map((r) => r.reason)),
      original_decomposition_paths: JSON.stringify(Object.keys(decomposition)),
      new_decomposition_paths: result ? JSON.stringify(result.candidatePaths.filter((p) => p.slotKey !== "rewrite").map((p) => p.text)) : "NOT_APPLICABLE",
      empty_token_guard_triggered: emptyTokenGuardTriggered,
      subject_binding_triggered: subjectBindingTriggered,
      rewrite_anchor_guard_triggered: rewriteAnchorGuardTriggered,
      no_valid_rewrite_path: result ? result.diagnostics.noValidRewritePath : "NOT_APPLICABLE",
      actual_executed_queries: result ? JSON.stringify(result.candidatePaths.map((p) => p.text)) : "NOT_APPLICABLE",
      per_path_result_counts: "NOT_RECORDED_PER_PATH_ONLY_AGGREGATE_TRACKED",
      pre_merge_count: result ? result.preMergeCount : "NOT_APPLICABLE",
      post_merge_count: result ? result.postMergeCount : "NOT_APPLICABLE",
      dedup_count: result ? result.dedupCount : "NOT_APPLICABLE",
      full_catalog: newFullCatalog,
      thousand_plus: newThousandPlus,
      original_entity_preserved: "SEE_HUMAN_REVIEW_CSV",
      top_results: result ? JSON.stringify(result.top10) : "NOT_APPLICABLE",
      human_label: "NOT_REVIEWED",
      replay_verdict: verdict,
      error: error || "",
      notes: `old_full_catalog=${oldFullCatalog} old_thousand_plus=${oldThousandPlus} source=hard_queries_68_ablation.csv+prompt3_baseline key=${key}`,
    });

    console.log(`[replay2b] ${replayId}/${ordered.length} ${qid} (${mode}) old(p3)=${oldPrompt3Count} new(2b)=${newCount} verdict=${verdict}`);
  }

  const gateRows = results.filter((r) => ["Q39", "Q40"].includes(r.query_id) && r.source_mode === "D" || (r.query_id === "Q42" && (r.source_mode === "D" || r.source_mode === "C")));
  const stillFullCatalog = gateRows.filter((r) => r.full_catalog === true);
  if (stillFullCatalog.length > 0) {
    gateFailure = stillFullCatalog.map((r) => `${r.query_id}(${r.source_mode})`).join(", ");
    console.error(`[replay2b] GATE FAILURE: still full-catalog after replay: ${gateFailure}`);
  }

  writeCsv(
    OUT_CSV,
    [
      "replay_id", "query_id", "query", "source_mode",
      "old_prompt3_result_count", "stage7_historical_result_count", "new_prompt2b_result_count",
      "count_delta", "count_ratio", "raw_rewrite", "parsed_rewrites", "decomposition",
      "original_rewrite_candidates", "accepted_rewrite_candidates", "bound_rewrite_candidates",
      "rejected_rewrite_candidates", "rewrite_rejection_reasons",
      "original_decomposition_paths", "new_decomposition_paths",
      "empty_token_guard_triggered", "subject_binding_triggered", "rewrite_anchor_guard_triggered",
      "no_valid_rewrite_path", "actual_executed_queries", "per_path_result_counts",
      "pre_merge_count", "post_merge_count", "dedup_count",
      "full_catalog", "thousand_plus", "original_entity_preserved", "top_results",
      "human_label", "replay_verdict", "error", "notes",
    ],
    results
  );
  console.log(`[replay2b] wrote ${results.length} rows -> ${OUT_CSV}`);

  const d23 = results.filter((r) => queryRows.find((q) => q.query_id === r.query_id && q.category === "d_plus_g_flood_23"));
  const summary = {
    total: results.length,
    blocked: results.filter((r) => r.error).length,
    pass: results.filter((r) => r.replay_verdict === "PASS").length,
    partial: results.filter((r) => r.replay_verdict === "PARTIAL").length,
    fail: results.filter((r) => r.replay_verdict === "FAIL").length,
    old_prompt3_ge1000: results.filter((r) => Number(r.old_prompt3_result_count) >= 1000).length,
    new_prompt2b_ge1000: results.filter((r) => r.thousand_plus === true).length,
    old_prompt3_full_catalog: results.filter((r) => Number(r.old_prompt3_result_count) === CATALOG_SIZE).length,
    new_prompt2b_full_catalog: results.filter((r) => r.full_catalog === true).length,
    d23_old_ge1000: d23.filter((r) => Number(r.old_prompt3_result_count) >= 1000).length,
    d23_new_ge1000: d23.filter((r) => r.thousand_plus === true).length,
    rewrite_anchor_guard_triggered_count: results.filter((r) => r.rewrite_anchor_guard_triggered === true).length,
    gate_failure: gateFailure,
  };
  console.log("[replay2b] summary:", JSON.stringify(summary, null, 2));
  fs.writeFileSync(path.join(PROMPT2B_DIR, "_replay_prompt2b_summary.json"), JSON.stringify(summary, null, 2));

  if (gateFailure) {
    console.error("[replay2b] STOP: gate failure.");
    process.exit(2);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
