#!/usr/bin/env node
import * as fs from "fs";
import * as path from "path";
import { GOOGLE_IMAGE_EVAL_QUERIES, assertQueries } from "./queries.js";
import type { ObservationsFile, QueryObservation } from "./types.js";
import {
  OBSERVATIONS_PATH,
  PROGRESS_CSV_PATH,
  OUT_DIR,
  DATA_DIR,
  PER_QUERY_DIR,
} from "./storage.js";

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

// ── Run all checks ────────────────────────────────────────────────────────────

// 1. Assert query constants
try {
  assertQueries();
  pass("Query constant assertions");
} catch (e) {
  fail("Query constant assertions", (e as Error).message);
}

// 2. Query count
if (GOOGLE_IMAGE_EVAL_QUERIES.length === 58) {
  pass("Expected queries", "58");
} else {
  fail("Expected queries", `Got ${GOOGLE_IMAGE_EVAL_QUERIES.length} (need 58)`);
}

// 3. Query IDs 1–58 consecutive
const ids = GOOGLE_IMAGE_EVAL_QUERIES.map((q) => q.query_id);
const consecutive = ids.every((id, i) => id === i + 1);
if (consecutive) {
  pass("Query IDs consecutive 1–58");
} else {
  fail("Query IDs consecutive", `IDs: ${ids.join(",")}`);
}

// 4. No duplicate IDs
const dupIds = ids.filter((id, i) => ids.indexOf(id) !== i);
if (dupIds.length === 0) {
  pass("No duplicate query IDs");
} else {
  fail("No duplicate query IDs", `Duplicates: ${dupIds.join(",")}`);
}

// 5. No duplicate queries
const queryTexts = GOOGLE_IMAGE_EVAL_QUERIES.map((q) => q.query);
const dupQueries = queryTexts.filter((q, i) => queryTexts.indexOf(q) !== i);
if (dupQueries.length === 0) {
  pass("No duplicate query texts");
} else {
  fail("No duplicate query texts", `Duplicates: ${dupQueries.join(", ")}`);
}

// 6. First/last query; key checks
const firstQuery = GOOGLE_IMAGE_EVAL_QUERIES[0].query;
const lastQuery = GOOGLE_IMAGE_EVAL_QUERIES[57].query;
firstQuery === "单词"
  ? pass("First query", "单词")
  : fail("First query", `Got: ${firstQuery}`);
lastQuery === "maps"
  ? pass("Last query", "maps")
  : fail("Last query", `Got: ${lastQuery}`);

// 7. maps included, cat excluded
const hasMaps = GOOGLE_IMAGE_EVAL_QUERIES.some((q) => q.query === "maps");
const hasCat = GOOGLE_IMAGE_EVAL_QUERIES.some((q) => q.query.toLowerCase() === "cat");
hasMaps ? pass("maps query included") : fail("maps query included", "maps not found");
!hasCat ? pass("cat excluded") : fail("cat excluded", "cat was found in queries");

// 7b. Required specific query checks
GOOGLE_IMAGE_EVAL_QUERIES[34].query === "动物 词汇"
  ? pass("Query 35", "动物 词汇")
  : fail("Query 35", `Got: "${GOOGLE_IMAGE_EVAL_QUERIES[34].query}"`);
GOOGLE_IMAGE_EVAL_QUERIES[47].query === "Spanish vocabulary printable"
  ? pass("Query 48", "Spanish vocabulary printable")
  : fail("Query 48", `Got: "${GOOGLE_IMAGE_EVAL_QUERIES[47].query}"`);
GOOGLE_IMAGE_EVAL_QUERIES[48].query === "ESL flashcards printable"
  ? pass("Query 49", "ESL flashcards printable")
  : fail("Query 49", `Got: "${GOOGLE_IMAGE_EVAL_QUERIES[48].query}"`);

// ── Load observations ─────────────────────────────────────────────────────────

let obs: ObservationsFile | null = null;
const obsExists = fs.existsSync(OBSERVATIONS_PATH);

if (!obsExists) {
  warn("observations.json", "File does not exist yet");
} else {
  try {
    obs = JSON.parse(fs.readFileSync(OBSERVATIONS_PATH, "utf8")) as ObservationsFile;
  } catch (e) {
    fail("observations.json parse", (e as Error).message);
  }
}

if (obs) {
  // 8. 58 records
  obs.queries.length === 58
    ? pass("observations 58 records", `${obs.queries.length}`)
    : fail("observations 58 records", `Got ${obs.queries.length} (need 58)`);

  // 9. Order matches
  const orderMatch = obs.queries.every(
    (q, i) => q.query_id === GOOGLE_IMAGE_EVAL_QUERIES[i].query_id,
  );
  orderMatch
    ? pass("Query order")
    : fail("Query order", "Mismatch between observations and fixed array");

  // 10. Group and query text match
  let groupMismatch = "";
  let textMismatch = "";
  for (let i = 0; i < obs.queries.length; i++) {
    const expected = GOOGLE_IMAGE_EVAL_QUERIES[i];
    const actual = obs.queries[i];
    if (actual.group !== expected.group) {
      groupMismatch += `id=${actual.query_id} expected=${expected.group} got=${actual.group}; `;
    }
    if (actual.query !== expected.query) {
      textMismatch += `id=${actual.query_id} expected="${expected.query}" got="${actual.query}"; `;
    }
  }
  groupMismatch ? fail("Group consistency", groupMismatch) : pass("Group consistency");
  textMismatch ? fail("Query text consistency", textMismatch) : pass("Query text consistency");

  // Per-query checks for complete items
  const statusCounts = {
    complete: 0,
    partial: 0,
    captcha: 0,
    failed: 0,
    pending: 0,
    running: 0,
  };

  const incompleteList: string[] = [];
  const missingScreenshots: string[] = [];
  const rankIssues: string[] = [];
  const duplicateUrls: string[] = [];

  for (const q of obs.queries) {
    const s = q.status as keyof typeof statusCounts;
    if (s in statusCounts) statusCounts[s]++;

    if (q.status === "complete") {
      // Labels must be array
      if (!Array.isArray(q.labels)) {
        fail(`Query ${q.query_id} labels`, "Not an array");
      }
      if (q.labels.length === 0) {
        warn(`Query ${q.query_id} labels empty`, q.query);
      }

      // Must have 10 top10
      if (q.top10.length !== 10) {
        fail(
          `Query ${q.query_id} top10 count`,
          `Expected 10, got ${q.top10.length}`,
        );
        incompleteList.push(`${q.query_id}:${q.query}`);
      }

      // Ranks 1–10
      const ranks = q.top10.map((r) => r.rank);
      const ranksOk =
        ranks.length === 10 && ranks.every((r, i) => r === i + 1);
      if (!ranksOk) {
        rankIssues.push(`${q.query_id}: ranks=${ranks.join(",")}`);
      }

      // result_type must be organic
      const badType = q.top10.filter((r) => r.result_type !== "organic");
      if (badType.length > 0) {
        fail(`Query ${q.query_id} result_type`, `Non-organic: ${badType.map((r) => r.rank).join(",")}`);
      }

      // At least 2 screenshots
      if (q.screenshots.length < 2) {
        fail(`Query ${q.query_id} screenshots`, `Only ${q.screenshots.length}`);
        missingScreenshots.push(`${q.query_id}:${q.query}`);
      }

      // Screenshot paths exist
      for (const screenshotPath of q.screenshots) {
        if (!fs.existsSync(screenshotPath)) {
          fail(`Query ${q.query_id} screenshot path`, `Missing: ${screenshotPath}`);
        }
      }

      // Duplicate URLs
      const pageUrls = q.top10.map((r) => r.page_url).filter(Boolean);
      const dupUrlSet = pageUrls.filter((u, i) => pageUrls.indexOf(u) !== i);
      if (dupUrlSet.length > 0) {
        duplicateUrls.push(`${q.query_id}: ${dupUrlSet.join(",")}`);
      }

      // WARN for missing fields
      for (const r of q.top10) {
        if (!r.page_url) warn(`Query ${q.query_id} rank ${r.rank}`, "page_url missing");
        if (!r.image_url) warn(`Query ${q.query_id} rank ${r.rank}`, "image_url missing");
        if (!r.title) warn(`Query ${q.query_id} rank ${r.rank}`, "title missing");
      }
    }
  }

  rankIssues.length === 0
    ? pass("Top 10 rankings")
    : fail("Top 10 rankings", rankIssues.join("; "));

  duplicateUrls.length === 0
    ? pass("No duplicate page URLs in top10")
    : warn("Duplicate page URLs in top10", duplicateUrls.join("; "));

  // 11. Screenshot paths check
  const allScreenshotPaths = obs.queries.flatMap((q) => q.screenshots);
  const missingPaths = allScreenshotPaths.filter((p) => !fs.existsSync(p));
  missingPaths.length === 0
    ? pass("Screenshot paths")
    : fail("Screenshot paths", `Missing: ${missingPaths.slice(0, 5).join(", ")}`);

  // 12. per-query JSON files
  let missingPerQuery = 0;
  if (fs.existsSync(PER_QUERY_DIR)) {
    for (const q of obs.queries) {
      if (q.status === "complete" || q.status === "partial") {
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

  // Summary
  console.log("\nGoogle Images Evaluation — 58-query set\n");
  console.log(`Expected queries: 58`);
  console.log(`Observed queries: ${obs.queries.length}\n`);
  console.log(`Complete: ${statusCounts.complete}`);
  console.log(`Partial: ${statusCounts.partial}`);
  console.log(`Captcha: ${statusCounts.captcha}`);
  console.log(`Failed: ${statusCounts.failed}`);
  console.log(`Pending: ${statusCounts.pending}`);

  if (incompleteList.length > 0) {
    console.log(`\nIncomplete queries: ${incompleteList.join(", ")}`);
  }
  if (statusCounts.partial > 0 || statusCounts.captcha > 0 || statusCounts.failed > 0) {
    console.log(
      `\nNon-complete: partial=${statusCounts.partial} captcha=${statusCounts.captcha} failed=${statusCounts.failed}`,
    );
  }
}

// ── Progress CSV ──────────────────────────────────────────────────────────────

if (fs.existsSync(PROGRESS_CSV_PATH)) {
  const csv = fs.readFileSync(PROGRESS_CSV_PATH, "utf8");
  const lines = csv.trim().split("\n").slice(1); // skip header
  lines.length === 58
    ? pass("Progress CSV row count", `${lines.length}`)
    : fail("Progress CSV row count", `Got ${lines.length} (need 58)`);
} else {
  warn("Progress CSV", "File does not exist yet");
}

// ── Print check results ───────────────────────────────────────────────────────

console.log("\n--- Check Results ---");
for (const r of results) {
  const icon = r.status === "PASS" ? "✓" : r.status === "WARN" ? "⚠" : "✗";
  const detail = r.detail ? ` — ${r.detail}` : "";
  console.log(`${icon} ${r.check}${detail}`);
}

// ── Overall verdict ───────────────────────────────────────────────────────────

const hasFail = results.some((r) => r.status === "FAIL");
const hasWarn = results.some((r) => r.status === "WARN");

let overall: "PASS" | "INCOMPLETE" | "FAIL";
if (hasFail) {
  overall = "FAIL";
} else if (!obs || obs.queries.some((q) => q.status !== "complete")) {
  overall = "INCOMPLETE";
} else {
  overall = "PASS";
}

console.log(`\nOverall: ${overall}\n`);

// ── Write validation report ───────────────────────────────────────────────────

const report = {
  generated_at: new Date().toISOString(),
  overall,
  checks: results,
  warnings: warns,
  status_counts: obs
    ? {
        complete: obs.queries.filter((q) => q.status === "complete").length,
        partial: obs.queries.filter((q) => q.status === "partial").length,
        captcha: obs.queries.filter((q) => q.status === "captcha").length,
        failed: obs.queries.filter((q) => q.status === "failed").length,
        pending: obs.queries.filter((q) => q.status === "pending").length,
      }
    : null,
};

fs.mkdirSync(DATA_DIR, { recursive: true });
fs.writeFileSync(VALIDATION_REPORT_PATH, JSON.stringify(report, null, 2), "utf8");
console.log(`Report saved to: ${VALIDATION_REPORT_PATH}`);
