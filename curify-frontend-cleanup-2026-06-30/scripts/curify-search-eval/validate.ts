#!/usr/bin/env node
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import { CURIFY_SEARCH_EVAL_QUERIES, assertQueries } from "./queries.js";
import type { CurifyObservationsFile, CurifyQueryObservation } from "./types.js";
import {
  OBSERVATIONS_PATH,
  PROGRESS_CSV_PATH,
  DATA_DIR,
  PER_QUERY_DIR,
  OUT_DIR,
} from "./storage.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VALIDATION_REPORT_PATH = path.join(DATA_DIR, "validation-report.json");
const SCREENSHOTS_DIR = path.join(OUT_DIR, "screenshots");

interface ValidationResult {
  check: string;
  status: "PASS" | "FAIL" | "WARN";
  detail?: string;
}

const results: ValidationResult[] = [];
const warns: string[] = [];

function pass(check: string, detail?: string): void {
  results.push({ check, status: "PASS", detail });
}
function fail(check: string, detail: string): void {
  results.push({ check, status: "FAIL", detail });
}
function warn(check: string, detail: string): void {
  results.push({ check, status: "WARN", detail });
  warns.push(`${check}: ${detail}`);
}

// ── 1. Query constant assertions ──────────────────────────────────────────────

try {
  assertQueries();
  pass("Query constant assertions");
} catch (e) {
  fail("Query constant assertions", (e as Error).message);
}

CURIFY_SEARCH_EVAL_QUERIES.length === 58
  ? pass("Query count", "58")
  : fail("Query count", `Got ${CURIFY_SEARCH_EVAL_QUERIES.length} (need 58)`);

const hasCat = CURIFY_SEARCH_EVAL_QUERIES.some((q) => q.query.toLowerCase() === "cat");
!hasCat ? pass("cat excluded") : fail("cat excluded", "cat found in query set");

CURIFY_SEARCH_EVAL_QUERIES[57].query === "maps"
  ? pass("Last query", "maps")
  : fail("Last query", `Got: ${CURIFY_SEARCH_EVAL_QUERIES[57].query}`);

CURIFY_SEARCH_EVAL_QUERIES[0].query === "单词"
  ? pass("First query", "单词")
  : fail("First query", `Got: ${CURIFY_SEARCH_EVAL_QUERIES[0].query}`);

CURIFY_SEARCH_EVAL_QUERIES[34].query === "动物 词汇"
  ? pass("Query 35", "动物 词汇")
  : fail("Query 35", `Got: "${CURIFY_SEARCH_EVAL_QUERIES[34].query}"`);

CURIFY_SEARCH_EVAL_QUERIES[47].query === "Spanish vocabulary printable"
  ? pass("Query 48", "Spanish vocabulary printable")
  : fail("Query 48", `Got: "${CURIFY_SEARCH_EVAL_QUERIES[47].query}"`);

CURIFY_SEARCH_EVAL_QUERIES[48].query === "ESL flashcards printable"
  ? pass("Query 49", "ESL flashcards printable")
  : fail("Query 49", `Got: "${CURIFY_SEARCH_EVAL_QUERIES[48].query}"`);

// ── 2. Load observations.json ─────────────────────────────────────────────────

let obs: CurifyObservationsFile | null = null;

if (!fs.existsSync(OBSERVATIONS_PATH)) {
  warn("observations.json", "File does not exist yet — run collect first");
} else {
  try {
    obs = JSON.parse(fs.readFileSync(OBSERVATIONS_PATH, "utf8")) as CurifyObservationsFile;
    pass("observations.json parse");
  } catch (e) {
    fail("observations.json parse", (e as Error).message);
  }
}

const summary = {
  ok: 0,
  ok_empty: 0,
  error: 0,
  pending: 0,
  partial: 0,
  redirected: 0,
  labelsEmpty: 0,
  topResultsEmpty: 0,
  missingScreenshots: 0,
  totalScreenshotBytes: 0,
};

if (obs) {
  obs.queries.length === 58
    ? pass("observations 58 records", `${obs.queries.length}`)
    : fail("observations 58 records", `Got ${obs.queries.length} (need 58)`);

  // Check no cat in observations
  const hasCatObs = obs.queries.some((q) => q.query.toLowerCase() === "cat");
  !hasCatObs ? pass("cat excluded in observations") : fail("cat excluded in observations", "cat found");

  // Check last query is maps
  const lastObs = obs.queries[obs.queries.length - 1];
  lastObs?.query === "maps"
    ? pass("Last observation query", "maps")
    : fail("Last observation query", `Got: ${lastObs?.query}`);

  // Per-query checks
  const missingPerQuery: string[] = [];
  const missingScreenshotList: string[] = [];

  for (const q of obs.queries) {
    const s = q.status;
    if (s === "ok") summary.ok++;
    else if (s === "ok_empty") summary.ok_empty++;
    else if (s === "error") summary.error++;
    else if (s === "pending") summary.pending++;
    else if (s === "partial") summary.partial++;

    if (q.redirected) summary.redirected++;
    if (q.labels.length === 0 && s !== "error" && s !== "pending") summary.labelsEmpty++;
    if (q.topResults.length === 0 && s !== "ok_empty" && s !== "error" && s !== "pending") summary.topResultsEmpty++;

    // Screenshot checks
    if (s === "ok" || s === "ok_empty") {
      const p1 = q.screenshots.page1;
      const p2 = q.screenshots.page2;
      if (!p1 || !fs.existsSync(p1)) {
        summary.missingScreenshots++;
        missingScreenshotList.push(`${q.index}:${q.query} page1`);
      } else {
        summary.totalScreenshotBytes += fs.statSync(p1).size;
      }
      if (!p2 || !fs.existsSync(p2)) {
        summary.missingScreenshots++;
        missingScreenshotList.push(`${q.index}:${q.query} page2`);
      } else {
        summary.totalScreenshotBytes += fs.statSync(p2).size;
      }
    }

    // Per-query JSON
    if (s !== "pending") {
      const files = fs.existsSync(PER_QUERY_DIR) ? fs.readdirSync(PER_QUERY_DIR) : [];
      const prefix = String(q.index).padStart(3, "0") + "-";
      const found = files.some((f) => f.startsWith(prefix) && f.endsWith(".json"));
      if (!found) missingPerQuery.push(`${q.index}:${q.query}`);
    }

    // topResults count check
    if ((s === "ok") && q.topResults.length > 10) {
      fail(`Query ${q.index} topResults count`, `${q.topResults.length} > 10 (must be <= 10)`);
    }

    // finalUrl check
    if ((s === "ok" || s === "ok_empty") && !q.finalUrl) {
      warn(`Query ${q.index} finalUrl`, "missing");
    }
  }

  missingPerQuery.length === 0
    ? pass("Per-query JSON files")
    : warn("Per-query JSON files", `Missing ${missingPerQuery.length}: ${missingPerQuery.slice(0, 5).join(", ")}`);

  missingScreenshotList.length === 0
    ? pass("Screenshot files")
    : warn("Screenshot files", `Missing ${missingScreenshotList.length}: ${missingScreenshotList.slice(0, 5).join(", ")}`);

  summary.labelsEmpty > 0
    ? warn("Labels empty count", `${summary.labelsEmpty} queries have labels=[]`)
    : pass("Labels non-empty for collected queries");

  summary.topResultsEmpty > 0
    ? warn("topResults empty (non-empty-status)", `${summary.topResultsEmpty} ok queries have no results`)
    : pass("topResults populated for ok queries");
}

// ── 3. Progress CSV ───────────────────────────────────────────────────────────

if (fs.existsSync(PROGRESS_CSV_PATH)) {
  const csv = fs.readFileSync(PROGRESS_CSV_PATH, "utf8");
  const lines = csv.trim().split("\n").slice(1);
  lines.length === 58
    ? pass("Progress CSV rows", "58")
    : fail("Progress CSV rows", `Got ${lines.length} (need 58)`);
} else {
  warn("Progress CSV", "Not found yet");
}

// ── Print results ─────────────────────────────────────────────────────────────

console.log("\nCurify Search — 58-query collection validation\n");
if (obs) {
  console.log(`Queries collected: ${obs.queries.length}`);
  console.log(`ok: ${summary.ok}`);
  console.log(`ok_empty: ${summary.ok_empty}`);
  console.log(`error: ${summary.error}`);
  console.log(`pending: ${summary.pending}`);
  console.log(`redirected: ${summary.redirected}`);
  console.log(`labels=[] count: ${summary.labelsEmpty}`);
  console.log(`topResults=[] (ok status) count: ${summary.topResultsEmpty}`);
  console.log(`missing screenshots: ${summary.missingScreenshots}`);
  console.log(`total screenshot size: ${(summary.totalScreenshotBytes / 1024 / 1024).toFixed(1)} MB`);
}

console.log("\n--- Check Results ---");
for (const r of results) {
  const icon = r.status === "PASS" ? "✓" : r.status === "WARN" ? "⚠" : "✗";
  const detail = r.detail ? ` — ${r.detail}` : "";
  console.log(`${icon} ${r.check}${detail}`);
}

// ── Overall verdict ───────────────────────────────────────────────────────────

const hasFail = results.some((r) => r.status === "FAIL");
const hasWarn = results.some((r) => r.status === "WARN");
const isComplete = obs && obs.queries.every((q) => q.status === "ok" || q.status === "ok_empty");

let overall: "PASS" | "WARN" | "FAIL";
if (hasFail) overall = "FAIL";
else if (hasWarn || !isComplete) overall = "WARN";
else overall = "PASS";

console.log(`\nOverall: ${overall}\n`);

// ── Write validation report ───────────────────────────────────────────────────

fs.mkdirSync(DATA_DIR, { recursive: true });
const report = {
  generated_at: new Date().toISOString(),
  overall,
  checks: results,
  warnings: warns,
  summary: {
    ...summary,
    totalScreenshotSizeMB: parseFloat((summary.totalScreenshotBytes / 1024 / 1024).toFixed(2)),
  },
};
fs.writeFileSync(VALIDATION_REPORT_PATH, JSON.stringify(report, null, 2), "utf8");
console.log(`Validation report: ${VALIDATION_REPORT_PATH}`);
