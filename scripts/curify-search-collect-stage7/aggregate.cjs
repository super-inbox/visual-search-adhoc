#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const ADHOC_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const OUT_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.13/search-optimization-stage-7");
const HARNESS_DIR = __dirname;

function sha256(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}
function readJSON(p) {
  return JSON.parse(fs.readFileSync(p, "utf-8"));
}

// ---- minimal RFC4180 CSV (parse + stringify) ----
function parseCsv(text) {
  const rows = [];
  let row = [], field = "", inQuotes = false, i = 0;
  const n = text.length;
  while (i < n) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') { if (text[i + 1] === '"') { field += '"'; i += 2; continue; } inQuotes = false; i++; continue; }
      field += c; i++; continue;
    }
    if (c === '"') { inQuotes = true; i++; continue; }
    if (c === ",") { row.push(field); field = ""; i++; continue; }
    if (c === "\r") { i++; continue; }
    if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; i++; continue; }
    field += c; i++;
  }
  if (field.length > 0 || row.length > 0) { row.push(field); rows.push(row); }
  const header = rows[0];
  return rows.slice(1).filter((r) => r.length > 1 || (r.length === 1 && r[0] !== "")).map((r) => Object.fromEntries(header.map((h, idx) => [h, r[idx] ?? ""])));
}
function csvField(v) {
  if (v === null || v === undefined) return "";
  const s = typeof v === "string" ? v : JSON.stringify(v);
  if (/[",\n\r]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}
function toCsv(rows, columns) {
  const lines = [columns.join(",")];
  for (const r of rows) lines.push(columns.map((c) => csvField(r[c])).join(","));
  return lines.join("\r\n") + "\r\n";
}

// ---- Load sources ----
const GOLD_CSV_PATH = path.join(ADHOC_ROOT, "docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv");
const BASELINE_RAW_CSV_PATH = path.join(ADHOC_ROOT, "docs/daily_report/7.7/curify_search_auto_collect_2026-07-07.csv");
const BASELINE_CLAUDE_CSV_PATH = path.join(ADHOC_ROOT, "docs/daily_report/7.9/manual_review/curify_68_manual_relevance_audit_2026-07-09.csv");

const goldRows = parseCsv(fs.readFileSync(GOLD_CSV_PATH, "utf-8"));
const baselineRawRows = parseCsv(fs.readFileSync(BASELINE_RAW_CSV_PATH, "utf-8"));
const baselineClaudeRows = parseCsv(fs.readFileSync(BASELINE_CLAUDE_CSV_PATH, "utf-8"));

if (goldRows.length !== 68) throw new Error("gold manifest != 68 rows: " + goldRows.length);
if (baselineRawRows.length !== 68) throw new Error("baseline raw != 68 rows");
if (baselineClaudeRows.length !== 68) throw new Error("baseline claude != 68 rows");

const baselineRawByQuery = new Map(baselineRawRows.map((r) => [r.query, r]));
const baselineClaudeByQuery = new Map(baselineClaudeRows.map((r) => [r.query, r]));

const modeData = {};
for (const m of ["A", "B", "C", "D"]) modeData[m] = readJSON(path.join(HARNESS_DIR, `mode_${m}_results.json`));
const judgeData = readJSON(path.join(HARNESS_DIR, "judge_results.json"));
const judgeByMode = {};
for (const m of ["A", "B", "C", "D"]) {
  judgeByMode[m] = new Map(judgeData.byMode[m].map((j) => [j.query, j]));
}
const rowsByModeQuery = {};
for (const m of ["A", "B", "C", "D"]) {
  rowsByModeQuery[m] = new Map(modeData[m].results.map((r) => [r.query, r]));
}

// ---- SHA-256 of key sources ----
const queryManifestSha256 = sha256(fs.readFileSync(GOLD_CSV_PATH));
const baselineRawSha256 = sha256(fs.readFileSync(BASELINE_RAW_CSV_PATH));
const baselineClaudeSha256 = sha256(fs.readFileSync(BASELINE_CLAUDE_CSV_PATH));

// ============================================================
// 1) hard_queries_68_baseline.csv (immutable, historical, Priority A)
// ============================================================
const baselineCols = [
  "query_id", "query", "query_category", "priority",
  "baseline_source_file", "baseline_source_type", "baseline_commit", "baseline_timestamp", "baseline_environment",
  "baseline_result_count", "baseline_zero_result", "baseline_low_result",
  "baseline_top_results_json", "baseline_relevance_score", "baseline_relevance_verdict", "baseline_relevance_notes",
  "baseline_tokens_json", "baseline_protected_phrases_json",
  "baseline_rewrite_triggered", "baseline_rewrite_raw_output", "baseline_rewrite_parsed_output_json", "baseline_final_search_queries_json",
  "baseline_error", "baseline_timeout", "baseline_empty_page", "baseline_data_quality",
];
const CLAUDE_TO_VERDICT = { PASS: "PASS", WARN: "PARTIAL", FAIL: "FAIL", UNCLEAR: "PARTIAL" };
const baselineRows68 = [];
goldRows.forEach((g, idx) => {
  const q = g.query;
  const raw = baselineRawByQuery.get(q);
  const cl = baselineClaudeByQuery.get(q);
  if (!raw || !cl) throw new Error("baseline query mismatch: " + q);
  const topTitles = (raw.top_10_result_titles || "").split(" | ").filter(Boolean);
  const topTypes = (raw.top_10_result_types || "").split(" | ").filter(Boolean);
  const topTags = (raw.top_10_result_tags_or_labels || "").split(" | ").filter(Boolean);
  const topResultsJson = topTitles.map((t, i) => ({ rank: i + 1, title: t, type: topTypes[i] || "not_available", tags: topTags[i] || "" }));
  const zero = Number(raw.visible_result_count) === 0;
  const low = Number(raw.visible_result_count) < 5;
  baselineRows68.push({
    query_id: `Q${String(idx + 1).padStart(2, "0")}`,
    query: q,
    query_category: `${g.primary_scene || ""}/${g.secondary_scene || ""}`,
    priority: g.priority || "",
    baseline_source_file: "docs/daily_report/7.7/curify_search_auto_collect_2026-07-07.csv",
    baseline_source_type: "historical_production_snapshot",
    baseline_commit: "pre-Fix1/Fix2 production (collected 2026-07-07, before commits 4210e21f/c062e618 and before the uncommitted Stage 2/5/6 diff)",
    baseline_timestamp: "2026-07-07",
    baseline_environment: "Playwright headless Chromium vs live https://www.curify-ai.com (production)",
    baseline_result_count: raw.visible_result_count,
    baseline_zero_result: zero,
    baseline_low_result: low,
    baseline_top_results_json: JSON.stringify(topResultsJson),
    baseline_relevance_score: cl.claude_confidence || "not_available",
    baseline_relevance_verdict: CLAUDE_TO_VERDICT[cl.claude_relevance_label] || "not_available",
    baseline_relevance_notes: `claude_relevance_label=${cl.claude_relevance_label}; claude_issue_type=${cl.claude_issue_type}; reason=${cl.claude_relevance_reason}`,
    baseline_tokens_json: "not_available",
    baseline_protected_phrases_json: "not_available",
    baseline_rewrite_triggered: "not_available",
    baseline_rewrite_raw_output: "not_available",
    baseline_rewrite_parsed_output_json: "not_available",
    baseline_final_search_queries_json: JSON.stringify([q]),
    baseline_error: raw.page_loaded === "yes" ? "" : "page_load_issue",
    baseline_timeout: "not_available",
    baseline_empty_page: raw.auto_flags && raw.auto_flags.includes("zero_result") ? true : false,
    baseline_data_quality: "Collected via live-browser scrape of rendered HTML only; tokenizer/rewrite internals were never observed (no server-log access), so tokens/protected-phrases/rewrite fields are not_available by construction, not a collection failure. Relevance verdict reused from the existing Claude first-pass judge (claude_relevance_label), not re-judged in Stage 7, per baseline-immutability rule.",
  });
});

// ============================================================
// Helper: apply the Stage 7 judge mapping + build a per-mode row
// ============================================================
function judgeVerdict(judgeEntry) {
  if (!judgeEntry || !judgeEntry.ok) return { verdict: "manual_review_required", label: "JUDGE_ERROR", raw: judgeEntry };
  const label = judgeEntry.verdict.relevance_label;
  const mapped = label === "PASS" ? "PASS" : label === "FAIL" ? "FAIL" : "PARTIAL"; // WARN, UNCLEAR -> PARTIAL (flagged)
  return { verdict: mapped, label, v: judgeEntry.verdict };
}

// ============================================================
// 2) hard_queries_68_refreshed.csv (Mode D)
// ============================================================
const refreshedCols = [
  "query_id", "query", "query_category", "mode",
  "primary_tokens_json", "alias_groups_json",
  "initial_result_count", "initial_zero_result", "initial_low_result", "low_result_threshold",
  "rewrite_triggered", "rewrite_output_json", "final_search_queries_json", "number_of_search_passes",
  "final_result_count", "final_zero_result", "final_low_result", "strict_result_count", "relaxed_result_count", "has_strict",
  "top_results_json",
  "judge_relevance_label", "judge_verdict", "judge_reason", "judge_confidence",
  "judge_core_intent_preserved", "judge_noise_level", "judge_over_broadening", "judge_under_recall",
  "judge_tokenization_error", "judge_rewrite_intent_drift",
];
const refreshedRows = [];
goldRows.forEach((g, idx) => {
  const q = g.query;
  const r = rowsByModeQuery.D.get(q);
  const j = judgeByMode.D.get(q);
  const jv = judgeVerdict(j);
  refreshedRows.push({
    query_id: `Q${String(idx + 1).padStart(2, "0")}`,
    query: q,
    query_category: `${g.primary_scene || ""}/${g.secondary_scene || ""}`,
    mode: "D",
    primary_tokens_json: JSON.stringify(r.primary_tokens),
    alias_groups_json: JSON.stringify(r.alias_groups),
    initial_result_count: r.initial_result_count,
    initial_zero_result: r.initial_zero_result,
    initial_low_result: r.initial_low_result,
    low_result_threshold: r.low_result_threshold,
    rewrite_triggered: r.rewrite_triggered,
    rewrite_output_json: JSON.stringify(r.rewrite_output),
    final_search_queries_json: JSON.stringify(r.final_search_queries),
    number_of_search_passes: r.number_of_search_passes,
    final_result_count: r.final_result_count,
    final_zero_result: r.final_zero_result,
    final_low_result: r.final_low_result,
    strict_result_count: r.strict_result_count,
    relaxed_result_count: r.relaxed_result_count,
    has_strict: r.has_strict,
    top_results_json: JSON.stringify(r.top_results),
    judge_relevance_label: jv.label,
    judge_verdict: jv.verdict,
    judge_reason: jv.v ? jv.v.reason : "not_available",
    judge_confidence: jv.v ? jv.v.confidence : "not_available",
    judge_core_intent_preserved: jv.v ? jv.v.core_intent_preserved : "not_available",
    judge_noise_level: jv.v ? jv.v.noise_level : "not_available",
    judge_over_broadening: jv.v ? jv.v.over_broadening : "not_available",
    judge_under_recall: jv.v ? jv.v.under_recall : "not_available",
    judge_tokenization_error: jv.v ? jv.v.tokenization_error : "not_available",
    judge_rewrite_intent_drift: jv.v ? jv.v.rewrite_intent_drift : "not_available",
  });
});

// ============================================================
// 5) hard_queries_68_ablation.csv (long format, 272 rows)
// ============================================================
const ablationCols = [
  "query_id", "query", "mode", "d_enabled", "g_enabled", "historical_baseline",
  "result_count", "zero_result", "low_result", "protected_phrase_hit",
  "tokens_json", "rewrite_triggered", "rewrite_output_json", "final_search_queries_json",
  "relevance_score", "relevance_verdict", "top_results_json", "runtime_ms", "error",
];
const ablationRows = [];
goldRows.forEach((g, idx) => {
  const q = g.query;
  const qid = `Q${String(idx + 1).padStart(2, "0")}`;
  for (const m of ["A", "B", "C", "D"]) {
    const r = rowsByModeQuery[m].get(q);
    const j = judgeByMode[m].get(q);
    const jv = judgeVerdict(j);
    ablationRows.push({
      query_id: qid,
      query: q,
      mode: m,
      d_enabled: r.d_enabled,
      g_enabled: r.g_enabled,
      historical_baseline: false,
      result_count: r.final_result_count,
      zero_result: r.final_zero_result,
      low_result: r.final_low_result,
      protected_phrase_hit: (r.alias_groups && r.alias_groups.length > 0) || false,
      tokens_json: JSON.stringify(r.primary_tokens),
      rewrite_triggered: r.rewrite_triggered,
      rewrite_output_json: JSON.stringify(r.rewrite_output),
      final_search_queries_json: JSON.stringify(r.final_search_queries),
      relevance_score: jv.v ? jv.v.confidence : "not_available",
      relevance_verdict: jv.verdict,
      top_results_json: JSON.stringify(r.top_results),
      runtime_ms: "not_measured",
      error: r.error || r.rewrite_error || "",
    });
  }
});
if (ablationRows.length !== 272) throw new Error("ablation rows != 272: " + ablationRows.length);

// ============================================================
// Attribution logic (section 11)
// ============================================================
function verdictRank(v) { return v === "FAIL" ? 0 : v === "PARTIAL" ? 1 : v === "PASS" ? 2 : -1; }
function improved(vBase, vNew) { return verdictRank(vNew) > verdictRank(vBase); }
function notWorse(vRef, vNew) { return verdictRank(vNew) >= verdictRank(vRef); }

function attribute(q) {
  const a = judgeVerdict(judgeByMode.A.get(q)).verdict;
  const b = judgeVerdict(judgeByMode.B.get(q)).verdict;
  const c = judgeVerdict(judgeByMode.C.get(q)).verdict;
  const d = judgeVerdict(judgeByMode.D.get(q)).verdict;
  const bImproved = improved(a, b);
  const cImproved = improved(a, c);
  if (bImproved && !cImproved && notWorse(b, d)) return "d_only_solved";
  if (cImproved && !bImproved && notWorse(c, d)) return "g_only_solved";
  if (bImproved && cImproved && notWorse(b, d) && notWorse(c, d)) return "both_independently_solved";
  if (!bImproved && !cImproved && improved(a, d)) return "d_plus_g_joint_synergy";
  const bestSingle = verdictRank(b) > verdictRank(c) ? b : c;
  if ((bImproved || cImproved) && verdictRank(d) < verdictRank(bestSingle)) return "combination_regression";
  if (!bImproved && !cImproved && !improved(a, d)) return "neither_solved";
  return "ambiguous";
}

// ============================================================
// 3) hard_queries_68_before_after.csv
// ============================================================
const beforeAfterCols = [
  "query_id", "query", "category",
  "baseline_result_count", "d_only_result_count", "g_only_result_count", "d_plus_g_result_count",
  "baseline_zero_result", "d_plus_g_zero_result",
  "baseline_low_result", "d_plus_g_low_result",
  "baseline_relevance_score", "d_only_relevance_score", "g_only_relevance_score", "d_plus_g_relevance_score",
  "baseline_top_results_json", "d_plus_g_top_results_json",
  "baseline_tokens_json", "d_plus_g_tokens_json",
  "protected_phrase_hit", "tokenization_changed", "rewrite_triggered", "rewrite_empty_output",
  "core_intent_preserved", "noise_increased", "count_increased_but_relevance_decreased",
  "d_only_verdict", "g_only_verdict", "d_plus_g_verdict",
  "final_verdict", "verdict_reason", "attribution", "manual_review_required",
];
const beforeAfterRows = [];
const manualOverrides = new Map(); // filled after manual spot-check pass, query -> {verdict, reason}

goldRows.forEach((g, idx) => {
  const q = g.query;
  const qid = `Q${String(idx + 1).padStart(2, "0")}`;
  const baseRaw = baselineRawByQuery.get(q);
  const baseClaude = baselineClaudeByQuery.get(q);
  const baseVerdict = CLAUDE_TO_VERDICT[baseClaude.claude_relevance_label] || "FAIL";
  const rA = rowsByModeQuery.A.get(q), rB = rowsByModeQuery.B.get(q), rC = rowsByModeQuery.C.get(q), rD = rowsByModeQuery.D.get(q);
  const jB = judgeVerdict(judgeByMode.B.get(q));
  const jC = judgeVerdict(judgeByMode.C.get(q));
  const jD = judgeVerdict(judgeByMode.D.get(q));

  const baselineCount = Number(baseRaw.visible_result_count);
  const countIncreasedButWorse = rD.final_result_count > baselineCount && verdictRank(jD.verdict) < verdictRank(baseVerdict);

  let autoVerdict = jD.verdict;
  let verdictReason = jD.v ? jD.v.reason : "judge_error";
  const manualReviewRequired =
    jD.label === "UNCLEAR" ||
    !jD.v ||
    countIncreasedButWorse ||
    rD.final_result_count > 1000 ||
    ["二手奢侈品", "蔚来ES6", "蔚来 ES6", "比亚迪海豹", "白箱", "五菱宏光", "蜜雪冰城"].some((k) => q.includes(k));

  const override = manualOverrides.get(q);
  const finalVerdict = override ? override.verdict : autoVerdict;
  const finalReason = override ? override.reason : verdictReason;

  const attribution = attribute(q);

  beforeAfterRows.push({
    query_id: qid,
    query: q,
    category: `${g.primary_scene || ""}/${g.secondary_scene || ""}`,
    baseline_result_count: baselineCount,
    d_only_result_count: rB.final_result_count,
    g_only_result_count: rC.final_result_count,
    d_plus_g_result_count: rD.final_result_count,
    baseline_zero_result: baselineCount === 0,
    d_plus_g_zero_result: rD.final_zero_result,
    baseline_low_result: baselineCount < 5,
    d_plus_g_low_result: rD.final_low_result,
    baseline_relevance_score: baseClaude.claude_confidence,
    d_only_relevance_score: jB.v ? jB.v.confidence : "not_available",
    g_only_relevance_score: jC.v ? jC.v.confidence : "not_available",
    d_plus_g_relevance_score: jD.v ? jD.v.confidence : "not_available",
    baseline_top_results_json: JSON.stringify((baseRaw.top_10_result_titles || "").split(" | ").filter(Boolean)),
    d_plus_g_top_results_json: JSON.stringify(rD.top_results),
    baseline_tokens_json: "not_available",
    d_plus_g_tokens_json: JSON.stringify(rD.primary_tokens),
    protected_phrase_hit: (rD.alias_groups && rD.alias_groups.length > 0) || false,
    tokenization_changed: JSON.stringify(rB.primary_tokens) !== JSON.stringify(rA.primary_tokens),
    rewrite_triggered: rD.rewrite_triggered,
    rewrite_empty_output: rD.rewrite_triggered && rD.number_of_search_passes === 1,
    core_intent_preserved: jD.v ? jD.v.core_intent_preserved : "not_available",
    noise_increased: jD.v ? jD.v.noise_level === "high" || jD.v.noise_level === "medium" : "not_available",
    count_increased_but_relevance_decreased: countIncreasedButWorse,
    d_only_verdict: jB.verdict,
    g_only_verdict: jC.verdict,
    d_plus_g_verdict: autoVerdict,
    final_verdict: finalVerdict,
    verdict_reason: finalReason,
    attribution,
    manual_review_required: manualReviewRequired,
  });
});

// ---- write everything (baseline is immutable-checked separately by caller) ----
fs.writeFileSync(path.join(OUT_DIR, "hard_queries_68_refreshed.csv"), toCsv(refreshedRows, refreshedCols));
fs.writeFileSync(path.join(OUT_DIR, "hard_queries_68_before_after.csv"), toCsv(beforeAfterRows, beforeAfterCols));
fs.writeFileSync(path.join(OUT_DIR, "hard_queries_68_ablation.csv"), toCsv(ablationRows, ablationCols));

module.exports = { baselineRows68, baselineCols, toCsv, OUT_DIR, beforeAfterRows, ablationRows, refreshedRows, queryManifestSha256, baselineRawSha256, baselineClaudeSha256 };

if (require.main === module) {
  // Baseline immutability check (section 3.3 / 5)
  const baselinePath = path.join(OUT_DIR, "hard_queries_68_baseline.csv");
  if (fs.existsSync(baselinePath)) {
    console.log("hard_queries_68_baseline.csv already exists — NOT overwriting (immutability rule).");
  } else {
    fs.writeFileSync(baselinePath, toCsv(baselineRows68, baselineCols));
    console.log("Wrote hard_queries_68_baseline.csv (first write).");
  }
  console.log("Wrote refreshed/before_after/ablation CSVs to", OUT_DIR);
  console.log("query_manifest_sha256:", queryManifestSha256);
  console.log("baseline_raw_sha256:", baselineRawSha256);
  console.log("baseline_claude_sha256:", baselineClaudeSha256);
}
