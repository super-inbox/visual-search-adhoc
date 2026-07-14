#!/usr/bin/env node
/**
 * Stage 7R Prompt 4 V2 -- Full 68 x A/B/C/D orchestrator.
 *
 * Fixed order: Q01:A,B,C,D -> Q02:A,B,C,D -> ... -> Q68:A,B,C,D (272 runs).
 * Each run is spawned as its own child process (run_one_mode.cjs) for cache
 * isolation. Each completed run is written immediately to TMP_DIR as JSON
 * (resumable: reruns of this script skip any run whose JSON already exists
 * AND is a non-error, non-timeout result). Any run that errored/timed out is
 * always genuinely re-executed (up to one retry, per Section 13).
 */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execFileSync } = require("child_process");
const { parseCsv } = require("./csv_utils.cjs");

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const ADHOC_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const QUERY_CSV = path.join(ADHOC_ROOT, "docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv");
const BASELINE_CSV = path.join(
  ADHOC_ROOT,
  "docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_baseline.csv"
);
const TMP_DIR = "/tmp/curify-stage7r-prompt4-v2/runs";

const MODE_CONTRACT = {
  A: { dEnabled: false, gEnabled: false },
  B: { dEnabled: true, gEnabled: false },
  C: { dEnabled: false, gEnabled: true },
  D: { dEnabled: true, gEnabled: true },
};
const MODES = ["A", "B", "C", "D"];

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function main() {
  fs.mkdirSync(TMP_DIR, { recursive: true });

  const goldRows = parseCsv(fs.readFileSync(QUERY_CSV, "utf-8"));
  const baseRows = parseCsv(fs.readFileSync(BASELINE_CSV, "utf-8"));
  if (goldRows.length !== 68 || baseRows.length !== 68) {
    console.error(`[full68] FATAL: expected 68/68 rows, got gold=${goldRows.length} base=${baseRows.length}`);
    process.exit(1);
  }
  const queries = [];
  for (let i = 0; i < 68; i++) {
    if (goldRows[i].query !== baseRows[i].query) {
      console.error(`[full68] FATAL: order mismatch at index ${i}: gold=${JSON.stringify(goldRows[i].query)} base=${JSON.stringify(baseRows[i].query)}`);
      process.exit(1);
    }
    queries.push({ queryId: baseRows[i].query_id, query: goldRows[i].query, queryOrder: i + 1 });
  }
  console.log(`[full68] ${queries.length} queries loaded and order-verified against baseline`);

  const runs = [];
  for (const q of queries) {
    for (const mode of MODES) {
      runs.push({ ...q, mode });
    }
  }
  console.log(`[full68] ${runs.length} total mode runs planned (expected 272)`);

  let idx = 0;
  for (const run of runs) {
    idx++;
    const runId = `${run.queryId}-${run.mode}`;
    const outJson = path.join(TMP_DIR, `${runId}.json`);
    const contract = MODE_CONTRACT[run.mode];

    let payload = null;
    let attemptCount = 0;
    let firstAttemptStatus = null;
    let firstAttemptError = null;
    let retryReason = null;

    if (fs.existsSync(outJson)) {
      try {
        const prior = JSON.parse(fs.readFileSync(outJson, "utf-8"));
        if (prior.result && !prior.error && !prior.timeout) {
          payload = prior;
          console.log(`[full68] ${idx}/${runs.length} REUSING prior successful result for ${runId} (final=${prior.result.finalResultCount})`);
        }
      } catch {
        // fall through, re-execute
      }
    }

    if (!payload) {
      const MAX_ATTEMPTS = 2; // one evaluation-layer retry max, per Section 13
      for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        attemptCount = attempt;
        console.log(`[full68] ${idx}/${runs.length} launching ${runId} mode=${run.mode} query=${JSON.stringify(run.query)} (attempt ${attempt}/${MAX_ATTEMPTS})`);
        try {
          execFileSync(
            process.execPath,
            [
              "--env-file=" + path.join(CURIFY_ROOT, ".env.local"),
              "run_one_mode.cjs",
              "--query-id", run.queryId,
              "--query", run.query,
              "--mode", run.mode,
              "--d-enabled", String(contract.dEnabled),
              "--g-enabled", String(contract.gEnabled),
              "--out", outJson,
            ],
            { cwd: __dirname, stdio: "inherit", timeout: 45_000 }
          );
        } catch (e) {
          console.error(`[full68] child process error for ${runId}:`, e.message);
        }
        try {
          payload = JSON.parse(fs.readFileSync(outJson, "utf-8"));
        } catch (e) {
          console.error(`[full68] failed to read output for ${runId}:`, e.message);
          payload = null;
        }
        if (attempt === 1) {
          firstAttemptStatus = payload && payload.result && !payload.error && !payload.timeout ? "SUCCESS" : "FAILED";
          firstAttemptError = payload ? payload.error : "CHILD_PROCESS_FAILED";
        }
        if (payload && payload.result && !payload.error && !payload.timeout) break;
        if (attempt < MAX_ATTEMPTS) {
          retryReason = payload && payload.timeout ? "TIMEOUT" : "TRANSIENT_ERROR_OR_NETWORK";
          console.log(`[full68] ${runId} attempt ${attempt} failed (error=${payload ? payload.error : "no payload"}), retrying (reason=${retryReason})...`);
        }
      }
    } else {
      attemptCount = 0; // reused from a prior invocation of this script
      firstAttemptStatus = "REUSED";
    }

    // Persist attempt metadata alongside the run payload for the compiler step.
    if (payload) {
      payload._attempt_meta = { attemptCount, firstAttemptStatus, firstAttemptError, retryReason };
      fs.writeFileSync(outJson, JSON.stringify(payload, null, 2));
    }

    const final = payload && payload.result ? payload.result.finalResultCount : "ERROR";
    console.log(`[full68] ${idx}/${runs.length} DONE ${runId} final=${final} error=${payload && payload.error ? "YES" : "no"}`);
  }

  console.log(`[full68] all ${runs.length} runs complete. JSON checkpoints in ${TMP_DIR}`);
}

main();
