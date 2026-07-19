// Batch evaluation runner: reads a query CSV, collects real results from
// V0 (port 4501) and V2 (port 4502) via the SAME collector.mjs method
// for both, judges each with the rubric-v1.1 LLM judge, and writes
// separate V0/V2/paired result CSVs. Progress logged to stderr so a
// long run can be monitored; writes incrementally so partial progress
// is never lost if interrupted. Processes rows with a bounded
// concurrency pool (default 6) -- both local dev servers and the OpenAI
// API handle a handful of concurrent requests fine, and this cuts a
// ~300-700 query run from over an hour to a manageable window.
import fs from "fs";
import { collectQuery } from "./collector.mjs";
import { judgeResultSet, loadEnv } from "./judge.mjs";

loadEnv("/Users/baobaoli/Desktop/curify-frontend-search-v2-2026-07-19/.env.local");

const args = process.argv.slice(2);
const csvPath = args[0];
const queryCol = args[1] || "query";
const langCol = args[2] || "language";
const outPrefix = args[3];
const limit = args[4] ? parseInt(args[4], 10) : Infinity;
const concurrency = args[5] ? parseInt(args[5], 10) : 6;

function parseCSV(text) {
  const rows = [];
  let row = [], field = "", inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else inQuotes = false; }
      else field += c;
    } else {
      if (c === '"') inQuotes = true;
      else if (c === ',') { row.push(field); field = ""; }
      else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ""; }
      else if (c === '\r') { }
      else field += c;
    }
  }
  if (field.length > 0 || row.length > 0) { row.push(field); rows.push(row); }
  return rows;
}

function toCSVField(v) {
  const s = String(v ?? "");
  if (/[",\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}
function toCSVRow(fields) { return fields.map(toCSVField).join(","); }

const rawText = fs.readFileSync(csvPath, "utf8");
const rows = parseCSV(rawText);
const header = rows[0];
const qIdx = header.indexOf(queryCol);
const langIdx = header.indexOf(langCol);
if (qIdx === -1) throw new Error(`query column "${queryCol}" not found in ${csvPath}, header=${header.join(",")}`);
const dataRows = rows.slice(1).filter((r) => r.length > 1 && r[qIdx]).slice(0, limit);

console.error(`[run_eval] ${dataRows.length} queries from ${csvPath}, concurrency=${concurrency}`);

const V0 = "http://localhost:4501";
const V2 = "http://localhost:4502";

const resultHeader = [
  "row_index", "query", "language", "ok", "collect_error", "http_status", "elapsed_ms",
  "inspiration_count", "matched_template_count", "gallery_prompt_count", "total_results",
  "zero_result", "low_result", "rewrite_triggered", "used_rewrites", "paths_used",
  "top5_titles",
  "relevance_label", "relevance_score", "primary_failure_reason",
  "semantic_drift", "original_intent_preserved", "judgeable_count",
  "relevant_count", "partial_count", "irrelevant_count",
];
const pairedHeader = [
  "row_index", "query", "language",
  "v0_total", "v2_total", "v0_zero", "v2_zero",
  "v0_label", "v2_label", "v0_score", "v2_score",
  "improved", "regressed",
];

const v0Out = new Array(dataRows.length);
const v2Out = new Array(dataRows.length);
const pairedOut = new Array(dataRows.length);

async function processRow(i) {
  const r = dataRows[i];
  const query = r[qIdx];
  const language = langIdx >= 0 ? r[langIdx] : "";
  const locale = language === "zh" ? "zh" : "en";
  const t0 = Date.now();
  try {
    // Retry once on collection failure -- a single transient timeout
    // (e.g. brief server contention under concurrent load) should not
    // be recorded as a permanent technical error if a retry succeeds.
    async function collectWithRetry(base) {
      let r = await collectQuery(base, query, { locale });
      if (!r.ok) {
        await new Promise((res) => setTimeout(res, 500));
        r = await collectQuery(base, query, { locale });
      }
      return r;
    }
    const [v0, v2] = await Promise.all([collectWithRetry(V0), collectWithRetry(V2)]);
    const v0Top5 = v0.ok ? v0.inspirations.slice(0, 5) : [];
    const v2Top5 = v2.ok ? v2.inspirations.slice(0, 5) : [];
    const v0Zero = v0.ok && v0.totalResults === 0;
    const v2Zero = v2.ok && v2.totalResults === 0;
    // Technical collection failures (per rubric section 3: "Technical
    // errors... are never scored FAIL on relevance grounds -- they are
    // UNJUDGABLE with primary_failure_reason=TECHNICAL_ERROR") are
    // short-circuited without an LLM judge call -- there is nothing to
    // judge if the page never rendered.
    const v0JudgePromise = v0.ok
      ? judgeResultSet(query, v0Top5, v0Zero)
      : Promise.resolve({ query_relevance_label: "UNJUDGABLE", score: null, primary_failure_reason: "TECHNICAL_ERROR:" + (v0.error ?? "unknown"), semantic_drift: "NONE", original_intent_preserved: "YES", judgeable_count: 0 });
    const v2JudgePromise = v2.ok
      ? judgeResultSet(query, v2Top5, v2Zero)
      : Promise.resolve({ query_relevance_label: "UNJUDGABLE", score: null, primary_failure_reason: "TECHNICAL_ERROR:" + (v2.error ?? "unknown"), semantic_drift: "NONE", original_intent_preserved: "YES", judgeable_count: 0 });
    const [v0Judge, v2Judge] = await Promise.all([v0JudgePromise, v2JudgePromise]);
    v0Out[i] = [
      i, query, language, v0.ok, v0.error ?? "", v0.httpStatus ?? "", v0.elapsedMs ?? "",
      v0.inspirationCount ?? "", v0.matchedTemplateCount ?? "", v0.galleryPromptCount ?? "", v0.totalResults ?? "",
      v0Zero, v0.ok && v0.totalResults > 0 && v0.totalResults < 5, v0.rewriteTriggered ?? "",
      JSON.stringify(v0.usedRewrites ?? []), v0.pathsUsed ?? "",
      JSON.stringify(v0Top5.map((x) => x.title)),
      v0Judge.query_relevance_label, v0Judge.score ?? "", v0Judge.primary_failure_reason ?? "",
      v0Judge.semantic_drift, v0Judge.original_intent_preserved, v0Judge.judgeable_count,
      v0Judge.relevant_count ?? "", v0Judge.partial_count ?? "", v0Judge.irrelevant_count ?? "",
    ];
    v2Out[i] = [
      i, query, language, v2.ok, v2.error ?? "", v2.httpStatus ?? "", v2.elapsedMs ?? "",
      v2.inspirationCount ?? "", v2.matchedTemplateCount ?? "", v2.galleryPromptCount ?? "", v2.totalResults ?? "",
      v2Zero, v2.ok && v2.totalResults > 0 && v2.totalResults < 5, v2.rewriteTriggered ?? "",
      JSON.stringify(v2.usedRewrites ?? []), v2.pathsUsed ?? "",
      JSON.stringify(v2Top5.map((x) => x.title)),
      v2Judge.query_relevance_label, v2Judge.score ?? "", v2Judge.primary_failure_reason ?? "",
      v2Judge.semantic_drift, v2Judge.original_intent_preserved, v2Judge.judgeable_count,
      v2Judge.relevant_count ?? "", v2Judge.partial_count ?? "", v2Judge.irrelevant_count ?? "",
    ];
    const labelRank = { FAIL: 0, UNJUDGABLE: 1, PARTIAL: 2, PASS: 3 };
    const improved = (labelRank[v2Judge.query_relevance_label] ?? -1) > (labelRank[v0Judge.query_relevance_label] ?? -1);
    const regressed = (labelRank[v2Judge.query_relevance_label] ?? -1) < (labelRank[v0Judge.query_relevance_label] ?? -1);
    pairedOut[i] = [
      i, query, language,
      v0.totalResults ?? "", v2.totalResults ?? "", v0Zero, v2Zero,
      v0Judge.query_relevance_label, v2Judge.query_relevance_label,
      v0Judge.score ?? "", v2Judge.score ?? "",
      improved, regressed,
    ];
  } catch (e) {
    console.error(`[run_eval] ERROR row ${i} query="${query}": ${(e && e.message) || e}`);
    const errRow = [i, query, language, false, String((e && e.message) || e), "", "", "", "", "", "", "", "", "", "", "", "ERROR", "", String((e && e.message) || e), "", "", 0, "", "", ""];
    v0Out[i] = errRow;
    v2Out[i] = errRow;
    pairedOut[i] = [i, query, language, "", "", "", "", "ERROR", "ERROR", "", "", false, false];
  }
  return Date.now() - t0;
}

function writeOutputs() {
  fs.writeFileSync(`${outPrefix}_V0.csv`, [toCSVRow(resultHeader), ...v0Out.filter(Boolean).map(toCSVRow)].join("\n") + "\n");
  fs.writeFileSync(`${outPrefix}_V2.csv`, [toCSVRow(resultHeader), ...v2Out.filter(Boolean).map(toCSVRow)].join("\n") + "\n");
  fs.writeFileSync(`${outPrefix}_PAIRED.csv`, [toCSVRow(pairedHeader), ...pairedOut.filter(Boolean).map(toCSVRow)].join("\n") + "\n");
}

let nextIndex = 0;
let completed = 0;
async function worker() {
  while (nextIndex < dataRows.length) {
    const i = nextIndex++;
    console.error(`[run_eval] row ${i} start "${dataRows[i][qIdx].slice(0, 40)}"`);
    const ms = await processRow(i);
    completed++;
    console.error(`[run_eval] row ${i} done in ${ms}ms (${completed}/${dataRows.length})`);
    if (completed % 5 === 0 || completed === dataRows.length) {
      writeOutputs();
    }
  }
}

const workers = Array.from({ length: Math.min(concurrency, dataRows.length) }, () => worker());
await Promise.all(workers);
writeOutputs();
console.error(`[run_eval] DONE ${completed}/${dataRows.length}`);
