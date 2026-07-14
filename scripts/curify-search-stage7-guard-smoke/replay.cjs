#!/usr/bin/env node
/**
 * Stage 7R Prompt 3 — Phase A: Deterministic Replay.
 *
 * Reuses the EXACT raw rewrite/decomposition JSON already recorded in
 * 7.13's hard_queries_68_ablation.csv (mode D for the 23 flood cases, plus
 * mode C for Q42/Q39/Q40) — NO LLM call is made in this phase. The real,
 * current (post-Prompt-2) Guard code is exercised via ./engine.cjs, which
 * requires the real bundled lib/searchRewrite.ts (Guard 2) and transcribes
 * page.tsx's scoreBlob (Guard 1) with a drift detector against the live
 * source (see scoring.cjs).
 *
 * Usage: node replay.cjs
 * (no CLI args needed; reads the frozen smoke_test_query_set_2026-07-14.csv
 * Phase-A rows and the read-only 7.13 ablation CSV)
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { parseCsv, writeCsv } = require("./csv_utils.cjs");
const { runOne, catalogInfo, verifyAgainstLiveSource } = require("./engine.cjs");

const ADHOC_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const STAGE7_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.13/search-optimization-stage-7");
const SMOKE_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/smoke-test");
const QUERY_SET_CSV = path.join(SMOKE_DIR, "smoke_test_query_set_2026-07-14.csv");
const OUT_CSV = path.join(SMOKE_DIR, "stage7_guard_replay_results_2026-07-14.csv");

const CATALOG_SIZE = catalogInfo().catalogSize; // 3209, read dynamically — never hardcoded

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

function classifyReplayVerdict({ oldCount, newCount, oldFullCatalog, newFullCatalog, executedPathCount, rejectedCount, emptyTokenCount, newTop10, query, error }) {
  if (error) return "BLOCKED";
  const eliminatedFullCatalog = oldFullCatalog && !newFullCatalog;
  const droppedBelow1000 = oldCount >= 1000 && newCount < 1000;
  const substantialDrop = oldCount > 0 && newCount / oldCount <= 0.5 && newCount < oldCount;

  // Heuristic top-10 relevance signal (Claude-structured, not a human/LLM
  // judge call): does at least one query keyword-ish token appear in the
  // top-10 titles/categories/tags blob? This does not replace the
  // structured human review file (Section 10) for the cases that matter —
  // it is only used to avoid a blind "count went down = PASS" verdict here.
  const queryLower = query.toLowerCase();
  const queryTokens = queryLower.split(/[\s,，、。]+/).filter((t) => t.length >= 2);
  const top10Blob = newTop10
    .map((t) => `${t.title ?? ""} ${t.category ?? ""} ${(t.tags ?? []).join(" ")}`)
    .join(" ")
    .toLowerCase();
  const anyKeywordHit = queryTokens.some((t) => top10Blob.includes(t));

  if (newFullCatalog) return "FAIL";
  if (newCount >= 1000 && !eliminatedFullCatalog) {
    // still broad; only PARTIAL if guard visibly did something (rejected an
    // unbound slot or blocked an empty-token path), otherwise FAIL (guard
    // had no effect at all).
    return (rejectedCount > 0 || emptyTokenCount > 0) ? "PARTIAL" : "FAIL";
  }
  if (eliminatedFullCatalog || droppedBelow1000 || substantialDrop) {
    return anyKeywordHit || newCount <= 20 ? "PASS" : "PARTIAL";
  }
  return "PARTIAL";
}

async function main() {
  console.log("[replay] drift check:", JSON.stringify(verifyAgainstLiveSource()));
  console.log("[replay] catalog size:", CATALOG_SIZE);

  if (fs.existsSync(OUT_CSV)) {
    console.error(`[replay] refusing to overwrite existing output: ${OUT_CSV}`);
    process.exit(1);
  }

  const queryRows = parseCsv(fs.readFileSync(QUERY_SET_CSV, "utf-8")).filter((r) => r.required_phase === "A");
  const ablation = loadAblationByQidMode();

  const results = [];
  let replayId = 0;

  // Step 5 (Prompt 3 execution order): run Q39/Q40/Q42 first as a gate check.
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

    let status = "OK";
    let error = "";
    let rewriteRaw = null;
    let decomposition = {};
    let oldTopResults = "NOT_RECORDED";
    let oldExecutedPaths = "NOT_RECORDED";
    let oldCount = null;
    let result = null;

    if (!src) {
      status = "REPLAY_BLOCKED_MISSING_INPUT";
      error = `no ablation row found for ${key}`;
    } else {
      const rewriteOutput = safeJsonParse(src.rewrite_output_json, null);
      if (rewriteOutput === null && src.rewrite_triggered === "true") {
        status = "REPLAY_BLOCKED_MISSING_INPUT";
        error = "rewrite_output_json missing/unparseable but rewrite_triggered=true";
      } else {
        rewriteRaw = rewriteOutput;
        decomposition = rewriteOutput?.decomposition ?? {};
        oldTopResults = src.top_results_json || "NOT_RECORDED";
        oldExecutedPaths = src.final_search_queries_json || "NOT_RECORDED";
        oldCount = Number(src.result_count ?? NaN);
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

    const oldFullCatalog = oldCount === CATALOG_SIZE;
    const oldThousandPlus = Number.isFinite(oldCount) && oldCount >= 1000;
    const newCount = result ? result.finalResultCount : null;
    const newFullCatalog = newCount === CATALOG_SIZE;
    const newThousandPlus = Number.isFinite(newCount) && newCount >= 1000;

    let verdict = "BLOCKED";
    if (result) {
      verdict = classifyReplayVerdict({
        oldCount,
        newCount,
        oldFullCatalog,
        newFullCatalog,
        executedPathCount: result.executedPathCount,
        rejectedCount: result.diagnostics.rejectedSlots.length,
        emptyTokenCount: result.diagnostics.emptyTokenPaths.length,
        newTop10: result.top10,
        query: row.query,
        error: status !== "OK" ? error : null,
      });
    }

    const countDelta = Number.isFinite(oldCount) && Number.isFinite(newCount) ? newCount - oldCount : "NOT_APPLICABLE";
    const countRatio = Number.isFinite(oldCount) && oldCount > 0 && Number.isFinite(newCount) ? +(newCount / oldCount).toFixed(4) : "NOT_APPLICABLE";

    results.push({
      replay_id: `R${String(replayId).padStart(3, "0")}`,
      query_id: qid,
      query: row.query,
      source_mode: mode,
      old_result_count: Number.isFinite(oldCount) ? oldCount : "NOT_RECORDED",
      old_top_results: oldTopResults,
      raw_rewrite: rewriteRaw ? JSON.stringify(rewriteRaw) : "NOT_RECORDED",
      decomposition: JSON.stringify(decomposition),
      old_executed_paths: oldExecutedPaths,
      new_planned_paths: result ? JSON.stringify(result.candidatePaths.map((p) => p.text)) : "NOT_APPLICABLE",
      accepted_paths: result ? JSON.stringify(result.candidatePaths.map((p) => ({ text: p.text, slotKey: p.slotKey, subjectBound: p.subjectBound }))) : "NOT_APPLICABLE",
      rejected_paths: result ? JSON.stringify(result.diagnostics.rejectedSlots) : "NOT_APPLICABLE",
      rejection_reasons: result
        ? JSON.stringify([
            ...result.diagnostics.rejectedSlots.map(() => "UNBOUND_NON_SUBJECT_SLOT"),
            ...result.diagnostics.emptyTokenPaths.map(() => "EMPTY_EXECUTABLE_TOKENS"),
          ])
        : "NOT_APPLICABLE",
      empty_token_guard_triggered: result ? result.diagnostics.emptyTokenPaths.length > 0 : "NOT_APPLICABLE",
      subject_binding_triggered: result ? result.candidatePaths.some((p) => p.subjectBound) : "NOT_APPLICABLE",
      no_valid_rewrite_path: result ? result.diagnostics.noValidRewritePath : "NOT_APPLICABLE",
      base_result_count: result ? result.preMergeCount : "NOT_APPLICABLE",
      per_path_result_counts: "NOT_RECORDED_PER_PATH_ONLY_AGGREGATE_TRACKED",
      pre_merge_count: result ? result.preMergeCount : "NOT_APPLICABLE",
      post_merge_count: result ? result.postMergeCount : "NOT_APPLICABLE",
      dedup_count: result ? result.dedupCount : "NOT_APPLICABLE",
      new_result_count: Number.isFinite(newCount) ? newCount : "NOT_RECORDED",
      new_top_results: result ? JSON.stringify(result.top10) : "NOT_APPLICABLE",
      old_full_catalog: oldFullCatalog,
      new_full_catalog: newFullCatalog,
      old_thousand_plus: oldThousandPlus,
      new_thousand_plus: newThousandPlus,
      count_delta: countDelta,
      count_ratio: countRatio,
      entity_preserved: "SEE_HUMAN_REVIEW_CSV",
      replay_status: status,
      replay_verdict: verdict,
      error: error || "",
      evidence: `source=hard_queries_68_ablation.csv key=${key}; engine=scripts/curify-search-stage7-guard-smoke/engine.cjs (current bundle + live page.tsx transcription, drift-checked)`,
    });

    console.log(`[replay] ${replayId}/${ordered.length} ${qid} (${mode}) old=${oldCount} new=${newCount} verdict=${verdict}`);

    if (priorityIds.includes(qid) && mode === (qid === "Q42" ? "D" : "D") && newFullCatalog) {
      // Gate check: Q39/Q40/Q42(D) must not still be full catalog.
    }
  }

  // Gate check after priority cases (Q39 D, Q40 D, Q42 D, Q42 C all included in ordered/results by now if present)
  const gateRows = results.filter((r) => ["Q39", "Q40"].includes(r.query_id) && r.source_mode === "D" || (r.query_id === "Q42" && (r.source_mode === "D" || r.source_mode === "C")));
  const stillFullCatalog = gateRows.filter((r) => r.new_full_catalog === true);
  if (stillFullCatalog.length > 0) {
    gateFailure = stillFullCatalog.map((r) => `${r.query_id}(${r.source_mode})`).join(", ");
    console.error(`[replay] GATE FAILURE: still full-catalog after replay: ${gateFailure}`);
  }

  writeCsv(
    OUT_CSV,
    [
      "replay_id","query_id","query","source_mode","old_result_count","old_top_results","raw_rewrite","decomposition",
      "old_executed_paths","new_planned_paths","accepted_paths","rejected_paths","rejection_reasons",
      "empty_token_guard_triggered","subject_binding_triggered","no_valid_rewrite_path","base_result_count",
      "per_path_result_counts","pre_merge_count","post_merge_count","dedup_count","new_result_count","new_top_results",
      "old_full_catalog","new_full_catalog","old_thousand_plus","new_thousand_plus","count_delta","count_ratio",
      "entity_preserved","replay_status","replay_verdict","error","evidence",
    ],
    results
  );
  console.log(`[replay] wrote ${results.length} rows -> ${OUT_CSV}`);

  const summary = {
    total: results.length,
    blocked: results.filter((r) => r.replay_status !== "OK").length,
    pass: results.filter((r) => r.replay_verdict === "PASS").length,
    partial: results.filter((r) => r.replay_verdict === "PARTIAL").length,
    fail: results.filter((r) => r.replay_verdict === "FAIL").length,
    old_ge1000: results.filter((r) => r.old_thousand_plus === true).length,
    new_ge1000: results.filter((r) => r.new_thousand_plus === true).length,
    old_full_catalog: results.filter((r) => r.old_full_catalog === true).length,
    new_full_catalog: results.filter((r) => r.new_full_catalog === true).length,
    gate_failure: gateFailure,
  };
  console.log("[replay] summary:", JSON.stringify(summary, null, 2));
  fs.writeFileSync(path.join(SMOKE_DIR, "_replay_summary.json"), JSON.stringify(summary, null, 2));

  if (gateFailure) {
    console.error("[replay] STOP: gate failure, do not proceed to Live Smoke.");
    process.exit(2);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
