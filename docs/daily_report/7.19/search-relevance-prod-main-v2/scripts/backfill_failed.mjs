// Re-processes only rows whose relevance_label is UNJUDGABLE due to a
// technical failure (JUDGE_CALL_FAILED / TECHNICAL_ERROR / ERROR),
// using the improved retry logic in judge.mjs / collector.mjs. Reads
// and rewrites the same *_V0.csv / *_V2.csv / *_PAIRED.csv triple in
// place. This exists because this evaluation session hit intermittent
// network flakiness to api.openai.com (confirmed via isolated testing,
// not a script bug) -- rather than re-running an entire batch (wasting
// the successful rows' real results and cost), only the failed subset
// is retried.
import fs from "fs";
import { collectQuery } from "./collector.mjs";
import { judgeResultSet, loadEnv } from "./judge.mjs";

loadEnv("/Users/baobaoli/Desktop/curify-frontend-search-v2-2026-07-19/.env.local");

const outPrefix = process.argv[2];
const V0 = "http://localhost:4501";
const V2 = "http://localhost:4502";

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

const v0Text = fs.readFileSync(`${outPrefix}_V0.csv`, "utf8");
const v2Text = fs.readFileSync(`${outPrefix}_V2.csv`, "utf8");
const pairedText = fs.readFileSync(`${outPrefix}_PAIRED.csv`, "utf8");
const v0Rows = parseCSV(v0Text);
const v2Rows = parseCSV(v2Text);
const pairedRows = parseCSV(pairedText);
const v0Header = v0Rows[0], pairedHeader = pairedRows[0];
const idx = Object.fromEntries(v0Header.map((h, i) => [h, i]));
const pidx = Object.fromEntries(pairedHeader.map((h, i) => [h, i]));

const FAIL_MARKERS = ["JUDGE_CALL_FAILED", "TECHNICAL_ERROR", "ERROR"];
function isFailed(row) {
  const reason = row[idx.primary_failure_reason] || "";
  return FAIL_MARKERS.some((m) => reason.includes(m));
}

const toRetry = [];
for (let i = 1; i < v0Rows.length; i++) {
  const v0row = v0Rows[i];
  const v2row = v2Rows[i];
  if (!v0row || v0row.length < 3) continue;
  if (isFailed(v0row) || isFailed(v2row)) toRetry.push(i);
}
console.error(`[backfill] ${toRetry.length} rows to retry out of ${v0Rows.length - 1}`);

let done = 0;
for (const i of toRetry) {
  const query = v0Rows[i][idx.query];
  const language = v0Rows[i][idx.language];
  const locale = language === "zh" ? "zh" : "en";
  console.error(`[backfill] retrying row ${i} "${query.slice(0, 40)}"`);
  try {
    const [v0, v2] = await Promise.all([
      collectQuery(V0, query, { locale }),
      collectQuery(V2, query, { locale }),
    ]);
    const v0Top5 = v0.ok ? v0.inspirations.slice(0, 5) : [];
    const v2Top5 = v2.ok ? v2.inspirations.slice(0, 5) : [];
    const v0Zero = v0.ok && v0.totalResults === 0;
    const v2Zero = v2.ok && v2.totalResults === 0;
    const v0Judge = v0.ok
      ? await judgeResultSet(query, v0Top5, v0Zero)
      : { query_relevance_label: "UNJUDGABLE", score: null, primary_failure_reason: "TECHNICAL_ERROR:" + (v0.error ?? "unknown"), semantic_drift: "NONE", original_intent_preserved: "YES", judgeable_count: 0 };
    const v2Judge = v2.ok
      ? await judgeResultSet(query, v2Top5, v2Zero)
      : { query_relevance_label: "UNJUDGABLE", score: null, primary_failure_reason: "TECHNICAL_ERROR:" + (v2.error ?? "unknown"), semantic_drift: "NONE", original_intent_preserved: "YES", judgeable_count: 0 };

    v0Rows[i] = [
      i - 1, query, language, v0.ok, v0.error ?? "", v0.httpStatus ?? "", v0.elapsedMs ?? "",
      v0.inspirationCount ?? "", v0.matchedTemplateCount ?? "", v0.galleryPromptCount ?? "", v0.totalResults ?? "",
      v0Zero, v0.ok && v0.totalResults > 0 && v0.totalResults < 5, v0.rewriteTriggered ?? "",
      JSON.stringify(v0.usedRewrites ?? []), v0.pathsUsed ?? "",
      JSON.stringify(v0Top5.map((x) => x.title)),
      v0Judge.query_relevance_label, v0Judge.score ?? "", v0Judge.primary_failure_reason ?? "",
      v0Judge.semantic_drift, v0Judge.original_intent_preserved, v0Judge.judgeable_count,
      v0Judge.relevant_count ?? "", v0Judge.partial_count ?? "", v0Judge.irrelevant_count ?? "",
    ];
    v2Rows[i] = [
      i - 1, query, language, v2.ok, v2.error ?? "", v2.httpStatus ?? "", v2.elapsedMs ?? "",
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
    pairedRows[i] = [
      i - 1, query, language,
      v0.totalResults ?? "", v2.totalResults ?? "", v0Zero, v2Zero,
      v0Judge.query_relevance_label, v2Judge.query_relevance_label,
      v0Judge.score ?? "", v2Judge.score ?? "",
      improved, regressed,
    ];
    done++;
  } catch (e) {
    console.error(`[backfill] STILL FAILED row ${i}: ${(e && e.message) || e}`);
  }
}

fs.writeFileSync(`${outPrefix}_V0.csv`, v0Rows.map(toCSVRow).join("\n") + "\n");
fs.writeFileSync(`${outPrefix}_V2.csv`, v2Rows.map(toCSVRow).join("\n") + "\n");
fs.writeFileSync(`${outPrefix}_PAIRED.csv`, pairedRows.map(toCSVRow).join("\n") + "\n");
console.error(`[backfill] DONE, recovered ${done}/${toRetry.length}`);
