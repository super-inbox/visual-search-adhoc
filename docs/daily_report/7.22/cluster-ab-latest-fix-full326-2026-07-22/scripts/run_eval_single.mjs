// Single-target variant of run_eval.mjs: collects+judges against ONE
// base URL (V2-R3, default port 4503) using the SAME collector.mjs /
// judge.mjs (byte-identical, imported not copied) as the V0/V2-R1 runs,
// so methodology is held fixed. Emits the identical per-row schema used
// by run_eval.mjs's V0/V2 CSVs, so the output can be joined with the
// already-existing, SHA-verified-reusable EASY326_V0.csv / EASY326_V2.csv
// (V2-R1) from this morning's run without any format drift.
import fs from "fs";
import { collectQuery } from "./collector.mjs";
import { judgeResultSet, loadEnv } from "./judge.mjs";

loadEnv("/Users/baobaoli/Desktop/curify-frontend-search-v2-r3-2026-07-19/.env.local");

const args = process.argv.slice(2);
const csvPath = args[0];
const queryCol = args[1] || "query";
const langCol = args[2] || "language";
const outPath = args[3];
const baseUrl = args[4] || "http://localhost:4503";
const limit = args[5] ? parseInt(args[5], 10) : Infinity;
const concurrency = args[6] ? parseInt(args[6], 10) : 6;

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

console.error(`[run_eval_single] ${dataRows.length} queries from ${csvPath} against ${baseUrl}, concurrency=${concurrency}`);

const resultHeader = [
  "row_index", "query", "language", "ok", "collect_error", "http_status", "elapsed_ms",
  "inspiration_count", "matched_template_count", "gallery_prompt_count", "total_results",
  "zero_result", "low_result", "rewrite_triggered", "used_rewrites", "paths_used",
  "top5_titles",
  "relevance_label", "relevance_score", "primary_failure_reason",
  "semantic_drift", "original_intent_preserved", "judgeable_count",
  "relevant_count", "partial_count", "irrelevant_count",
];

const out = new Array(dataRows.length);

async function processRow(i) {
  const r = dataRows[i];
  const query = r[qIdx];
  const language = langIdx >= 0 ? r[langIdx] : "";
  const locale = language === "zh" ? "zh" : "en";
  const t0 = Date.now();
  try {
    async function collectWithRetry(base) {
      let r = await collectQuery(base, query, { locale });
      if (!r.ok) {
        await new Promise((res) => setTimeout(res, 500));
        r = await collectQuery(base, query, { locale });
      }
      return r;
    }
    const v = await collectWithRetry(baseUrl);
    const top5 = v.ok ? v.inspirations.slice(0, 5) : [];
    const zero = v.ok && v.totalResults === 0;
    const judgePromise = v.ok
      ? judgeResultSet(query, top5, zero)
      : Promise.resolve({ query_relevance_label: "UNJUDGABLE", score: null, primary_failure_reason: "TECHNICAL_ERROR:" + (v.error ?? "unknown"), semantic_drift: "NONE", original_intent_preserved: "YES", judgeable_count: 0 });
    const judge = await judgePromise;
    out[i] = [
      i, query, language, v.ok, v.error ?? "", v.httpStatus ?? "", v.elapsedMs ?? "",
      v.inspirationCount ?? "", v.matchedTemplateCount ?? "", v.galleryPromptCount ?? "", v.totalResults ?? "",
      zero, v.ok && v.totalResults > 0 && v.totalResults < 5, v.rewriteTriggered ?? "",
      JSON.stringify(v.usedRewrites ?? []), v.pathsUsed ?? "",
      JSON.stringify(top5.map((x) => x.title)),
      judge.query_relevance_label, judge.score ?? "", judge.primary_failure_reason ?? "",
      judge.semantic_drift, judge.original_intent_preserved, judge.judgeable_count,
      judge.relevant_count ?? "", judge.partial_count ?? "", judge.irrelevant_count ?? "",
    ];
  } catch (e) {
    console.error(`[run_eval_single] ERROR row ${i} query="${query}": ${(e && e.message) || e}`);
    out[i] = [i, query, language, false, String((e && e.message) || e), "", "", "", "", "", "", "", "", "", "", "", "", "ERROR", "", String((e && e.message) || e), "", "", 0, "", "", ""];
  }
  return Date.now() - t0;
}

function writeOutputs() {
  fs.writeFileSync(outPath, [toCSVRow(resultHeader), ...out.filter(Boolean).map(toCSVRow)].join("\n") + "\n");
}

let nextIndex = 0;
let completed = 0;
async function worker() {
  while (nextIndex < dataRows.length) {
    const i = nextIndex++;
    console.error(`[run_eval_single] row ${i} start "${dataRows[i][qIdx].slice(0, 40)}"`);
    const ms = await processRow(i);
    completed++;
    console.error(`[run_eval_single] row ${i} done in ${ms}ms (${completed}/${dataRows.length})`);
    if (completed % 5 === 0 || completed === dataRows.length) {
      writeOutputs();
    }
  }
}

const workers = Array.from({ length: Math.min(concurrency, dataRows.length) }, () => worker());
await Promise.all(workers);
writeOutputs();
console.error(`[run_eval_single] DONE ${completed}/${dataRows.length}`);
