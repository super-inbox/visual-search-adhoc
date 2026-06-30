#!/usr/bin/env node
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import { PINTEREST_SEARCH_EVAL_QUERIES, assertQueries } from "./queries.js";
import type { PinterestObservationsFile } from "./types.js";
import {
  OBSERVATIONS_PATH,
  PROGRESS_CSV_PATH,
  DATA_DIR,
  PER_QUERY_DIR,
  SCREENSHOTS_BASE,
} from "./storage.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VALIDATION_REPORT_PATH = path.join(DATA_DIR, "validation-report.json");

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

// ── Query constant checks ─────────────────────────────────────────────────────

try {
  assertQueries();
  pass("Query constant assertions");
} catch (e) {
  fail("Query constant assertions", (e as Error).message);
}

PINTEREST_SEARCH_EVAL_QUERIES.length === 58
  ? pass("Expected queries", "58")
  : fail("Expected queries", `Got ${PINTEREST_SEARCH_EVAL_QUERIES.length} (need 58)`);

const ids = PINTEREST_SEARCH_EVAL_QUERIES.map((q) => q.query_id);
ids.every((id, i) => id === i + 1)
  ? pass("Query IDs consecutive 1–58")
  : fail("Query IDs consecutive", `IDs: ${ids.join(",")}`);

const dupIds = ids.filter((id, i) => ids.indexOf(id) !== i);
dupIds.length === 0 ? pass("No duplicate query IDs") : fail("No duplicate query IDs", `${dupIds}`);

const queryTexts = PINTEREST_SEARCH_EVAL_QUERIES.map((q) => q.query);
const dupQueries = queryTexts.filter((q, i) => queryTexts.indexOf(q) !== i);
dupQueries.length === 0
  ? pass("No duplicate query texts")
  : fail("No duplicate query texts", `${dupQueries.join(", ")}`);

PINTEREST_SEARCH_EVAL_QUERIES[0].query === "单词"
  ? pass("First query", "单词")
  : fail("First query", `Got: ${PINTEREST_SEARCH_EVAL_QUERIES[0].query}`);

PINTEREST_SEARCH_EVAL_QUERIES[57].query === "maps"
  ? pass("Last query", "maps")
  : fail("Last query", `Got: ${PINTEREST_SEARCH_EVAL_QUERIES[57].query}`);

PINTEREST_SEARCH_EVAL_QUERIES.some((q) => q.query === "maps")
  ? pass("maps query included")
  : fail("maps query included", "maps not found");

!PINTEREST_SEARCH_EVAL_QUERIES.some((q) => q.query.toLowerCase() === "cat")
  ? pass("cat excluded")
  : fail("cat excluded", "cat was found in queries");

PINTEREST_SEARCH_EVAL_QUERIES[34].query === "动物 词汇"
  ? pass("Query 35", "动物 词汇")
  : fail("Query 35", `Got: "${PINTEREST_SEARCH_EVAL_QUERIES[34].query}"`);

PINTEREST_SEARCH_EVAL_QUERIES[47].query === "Spanish vocabulary printable"
  ? pass("Query 48", "Spanish vocabulary printable")
  : fail("Query 48", `Got: "${PINTEREST_SEARCH_EVAL_QUERIES[47].query}"`);

PINTEREST_SEARCH_EVAL_QUERIES[48].query === "ESL flashcards printable"
  ? pass("Query 49", "ESL flashcards printable")
  : fail("Query 49", `Got: "${PINTEREST_SEARCH_EVAL_QUERIES[48].query}"`);

// ── Load observations ─────────────────────────────────────────────────────────

let obs: PinterestObservationsFile | null = null;
const obsExists = fs.existsSync(OBSERVATIONS_PATH);

if (!obsExists) {
  warn("observations.json", "File does not exist yet — run collect:pinterest-search first");
} else {
  try {
    obs = JSON.parse(fs.readFileSync(OBSERVATIONS_PATH, "utf8")) as PinterestObservationsFile;
    pass("observations.json parse");
  } catch (e) {
    fail("observations.json parse", (e as Error).message);
  }
}

if (obs) {
  obs.queries.length === 58
    ? pass("observations 58 records", `${obs.queries.length}`)
    : fail("observations 58 records", `Got ${obs.queries.length} (need 58)`);

  const orderMatch = obs.queries.every(
    (q, i) => q.query_id === PINTEREST_SEARCH_EVAL_QUERIES[i].query_id,
  );
  orderMatch ? pass("Query order") : fail("Query order", "Mismatch between observations and fixed array");

  let textMismatch = "";
  for (let i = 0; i < obs.queries.length; i++) {
    const expected = PINTEREST_SEARCH_EVAL_QUERIES[i];
    const actual = obs.queries[i];
    if (actual.query !== expected.query) {
      textMismatch += `id=${actual.query_id} expected="${expected.query}" got="${actual.query}"; `;
    }
  }
  textMismatch ? fail("Query text consistency", textMismatch) : pass("Query text consistency");

  const TERMINAL_STATUSES = ["ok", "ok_empty", "blocked", "login_required", "captcha", "error"];

  const statusCounts: Record<string, number> = {
    ok: 0, ok_empty: 0, blocked: 0, login_required: 0,
    captcha: 0, error: 0, partial: 0, pending: 0, running: 0,
  };

  const labelsEmptyQueries: string[] = [];
  const topResultsEmptyQueries: string[] = [];
  const topResultsLt10: string[] = [];
  const missingScreenshots: string[] = [];
  const missingFinalUrl: string[] = [];

  for (const q of obs.queries) {
    const s = q.status;
    if (s in statusCounts) statusCounts[s]++;

    if (q.status === "ok" || q.status === "partial") {
      if (!Array.isArray(q.labels)) {
        fail(`Query ${q.query_id} labels`, "Not an array");
      } else if (q.labels.length === 0) {
        warn(`Query ${q.query_id} labels empty`, q.query);
        labelsEmptyQueries.push(`${q.query_id}:${q.query}`);
      }

      if (!Array.isArray(q.topResults)) {
        fail(`Query ${q.query_id} topResults`, "Not an array");
      } else {
        if (q.topResults.length === 0) {
          warn(`Query ${q.query_id} topResults empty`, q.query);
          topResultsEmptyQueries.push(`${q.query_id}:${q.query}`);
        } else if (q.topResults.length < 10) {
          warn(`Query ${q.query_id} topResults < 10`, `got ${q.topResults.length}`);
          topResultsLt10.push(`${q.query_id}:${q.query}(${q.topResults.length})`);
        }
        if (q.topResults.length > 10) {
          fail(`Query ${q.query_id} topResults > 10`, `got ${q.topResults.length}`);
        }
      }

      if (!q.finalUrl) missingFinalUrl.push(`${q.query_id}:${q.query}`);

      if (!q.screenshots.page1 || !q.screenshots.page2) {
        missingScreenshots.push(`${q.query_id}:${q.query}`);
      } else {
        if (!fs.existsSync(q.screenshots.page1)) {
          fail(`Query ${q.query_id} screenshot page1`, `Missing: ${q.screenshots.page1}`);
        }
        if (!fs.existsSync(q.screenshots.page2)) {
          fail(`Query ${q.query_id} screenshot page2`, `Missing: ${q.screenshots.page2}`);
        }
        if (!q.screenshots.page1.endsWith("pinterest-search-page1.png")) {
          fail(`Query ${q.query_id} screenshot filename`, "page1 must end with pinterest-search-page1.png");
        }
        if (!q.screenshots.page2.endsWith("pinterest-search-page2.png")) {
          fail(`Query ${q.query_id} screenshot filename`, "page2 must end with pinterest-search-page2.png");
        }
      }
    }
  }

  missingFinalUrl.length === 0
    ? pass("finalUrl present for ok/partial queries")
    : warn("finalUrl missing", `${missingFinalUrl.length} queries: ${missingFinalUrl.slice(0, 5).join(", ")}`);

  missingScreenshots.length === 0
    ? pass("Screenshots present for ok/partial queries")
    : warn("Missing screenshots", `${missingScreenshots.length}: ${missingScreenshots.slice(0, 5).join(", ")}`);

  // per-query JSON files
  let missingPerQuery = 0;
  if (fs.existsSync(PER_QUERY_DIR)) {
    for (const q of obs.queries) {
      if (TERMINAL_STATUSES.includes(q.status) || q.status === "partial") {
        const files = fs.readdirSync(PER_QUERY_DIR);
        const prefix = String(q.query_id).padStart(3, "0") + "-";
        const found = files.some((f) => f.startsWith(prefix) && f.endsWith(".json"));
        if (!found) missingPerQuery++;
      }
    }
    missingPerQuery === 0
      ? pass("Per-query JSON files")
      : warn("Per-query JSON files", `Missing ${missingPerQuery} per-query JSONs`);
  } else {
    warn("Per-query JSON dir", "data/per-query/ does not exist yet");
  }

  // Screenshot total size
  let totalScreenshotSize = 0;
  if (fs.existsSync(SCREENSHOTS_BASE)) {
    const walkDir = (dir: string): void => {
      for (const f of fs.readdirSync(dir)) {
        const p = path.join(dir, f);
        const stat = fs.statSync(p);
        if (stat.isDirectory()) walkDir(p);
        else if (f.endsWith(".png")) totalScreenshotSize += stat.size;
      }
    };
    walkDir(SCREENSHOTS_BASE);
  }

  // Summary
  console.log("\nPinterest Search Evaluation — 58-query set\n");
  console.log(`Expected queries: 58`);
  console.log(`Observed queries: ${obs.queries.length}\n`);
  console.log(`ok:              ${statusCounts.ok}`);
  console.log(`ok_empty:        ${statusCounts.ok_empty}`);
  console.log(`blocked:         ${statusCounts.blocked}`);
  console.log(`login_required:  ${statusCounts.login_required}`);
  console.log(`captcha:         ${statusCounts.captcha}`);
  console.log(`error:           ${statusCounts.error}`);
  console.log(`partial:         ${statusCounts.partial}`);
  console.log(`pending:         ${statusCounts.pending}`);
  console.log(`\nlabels=0 queries:      ${labelsEmptyQueries.length}`);
  console.log(`topResults=0 queries:  ${topResultsEmptyQueries.length}`);
  console.log(`topResults<10 queries: ${topResultsLt10.length}`);
  console.log(`missing screenshots:   ${missingScreenshots.length}`);
  console.log(`total screenshot size: ${(totalScreenshotSize / 1024 / 1024).toFixed(1)} MB`);

  const report = {
    generated_at: new Date().toISOString(),
    overall: "" as "PASS" | "WARN" | "FAIL",
    checks: results,
    warnings: warns,
    summary: {
      ok: statusCounts.ok,
      ok_empty: statusCounts.ok_empty,
      blocked: statusCounts.blocked,
      login_required: statusCounts.login_required,
      captcha: statusCounts.captcha,
      error: statusCounts.error,
      partial: statusCounts.partial,
      pending: statusCounts.pending,
      labels_empty_count: labelsEmptyQueries.length,
      top_results_empty_count: topResultsEmptyQueries.length,
      top_results_lt10_count: topResultsLt10.length,
      missing_screenshots_count: missingScreenshots.length,
      total_screenshot_size_bytes: totalScreenshotSize,
    },
  };

  console.log("\n--- Check Results ---");
  for (const r of results) {
    const icon = r.status === "PASS" ? "✓" : r.status === "WARN" ? "⚠" : "✗";
    console.log(`${icon} ${r.check}${r.detail ? ` — ${r.detail}` : ""}`);
  }

  const hasFail = results.some((r) => r.status === "FAIL");
  const hasWarn = results.some((r) => r.status === "WARN");
  const allDone = obs.queries.every((q) =>
    [...TERMINAL_STATUSES, "partial"].includes(q.status),
  );

  report.overall = hasFail ? "FAIL" : hasWarn || !allDone ? "WARN" : "PASS";
  console.log(`\nOverall: ${report.overall}\n`);

  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(VALIDATION_REPORT_PATH, JSON.stringify(report, null, 2), "utf8");
  console.log(`Report saved to: ${VALIDATION_REPORT_PATH}`);
} else {
  console.log("\n--- Check Results ---");
  for (const r of results) {
    const icon = r.status === "PASS" ? "✓" : r.status === "WARN" ? "⚠" : "✗";
    console.log(`${icon} ${r.check}${r.detail ? ` — ${r.detail}` : ""}`);
  }
  const hasFail = results.some((r) => r.status === "FAIL");
  const overall = hasFail ? "FAIL" : "WARN";
  console.log(`\nOverall: ${overall}`);
  console.log("Run collect:pinterest-search first to generate observation data.\n");

  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(
    VALIDATION_REPORT_PATH,
    JSON.stringify({
      generated_at: new Date().toISOString(),
      overall,
      checks: results,
      warnings: warns,
      summary: null,
    }, null, 2),
    "utf8",
  );
  console.log(`Report saved to: ${VALIDATION_REPORT_PATH}`);
}
