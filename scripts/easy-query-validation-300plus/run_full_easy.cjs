#!/usr/bin/env node
/**
 * Prompt 8 -- 300+ Easy Query Validation orchestrator.
 *
 * D-mode only (dEnabled=true, gEnabled=true -- production defaults), against
 * the SAME frozen candidate bundle already used and hash-verified in Stage 7R
 * Prompt 4 V2 (scripts/curify-search-stage7-full-rerun-v2/engine.cjs +
 * _bundle_current.cjs). This script does not modify or rebuild that bundle;
 * it requires it read-only from its existing location.
 *
 * Checkpoint/resume: each completed query is written immediately to TMP_DIR
 * as JSON. Reruns of this script skip any query whose JSON already exists
 * AND is a non-error, non-timeout result. Errored/timed-out queries are
 * always genuinely re-executed (up to one retry).
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { parseCsv } = require("../curify-search-stage7-full-rerun-v2/csv_utils.cjs");

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const STAGE7_DIR = path.join(__dirname, "..", "curify-search-stage7-full-rerun-v2");
const QUERY_CSV = process.argv[2];
const TMP_DIR = process.argv[3] || "/tmp/curify-easy328-prompt8/runs";

if (!QUERY_CSV) {
  console.error("[run_full_easy] usage: node run_full_easy.cjs <cleaned_csv_path> [tmp_dir]");
  process.exit(1);
}

function main() {
  fs.mkdirSync(TMP_DIR, { recursive: true });

  const rows = parseCsv(fs.readFileSync(QUERY_CSV, "utf-8"));
  console.log(`[run_full_easy] ${rows.length} easy queries loaded from ${QUERY_CSV}`);

  let idx = 0;
  for (const row of rows) {
    idx++;
    const runId = row.easy_id;
    const outJson = path.join(TMP_DIR, `${runId}.json`);

    let payload = null;

    if (fs.existsSync(outJson)) {
      try {
        const prior = JSON.parse(fs.readFileSync(outJson, "utf-8"));
        if (prior.result && !prior.error && !prior.timeout) {
          payload = prior;
          console.log(`[run_full_easy] ${idx}/${rows.length} REUSING prior successful result for ${runId} (final=${prior.result.finalResultCount})`);
        }
      } catch {
        // fall through, re-execute
      }
    }

    if (!payload) {
      const MAX_ATTEMPTS = 2;
      for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        console.log(`[run_full_easy] ${idx}/${rows.length} launching ${runId} query=${JSON.stringify(row.query)} (attempt ${attempt}/${MAX_ATTEMPTS})`);
        try {
          execFileSync(
            process.execPath,
            [
              "--env-file=" + path.join(CURIFY_ROOT, ".env.local"),
              path.join(STAGE7_DIR, "run_one_mode.cjs"),
              "--query-id", runId,
              "--query", row.query,
              "--mode", "D",
              "--d-enabled", "true",
              "--g-enabled", "true",
              "--out", outJson,
            ],
            { cwd: STAGE7_DIR, stdio: "inherit", timeout: 45_000 }
          );
        } catch (e) {
          console.error(`[run_full_easy] child process error for ${runId}:`, e.message);
        }
        try {
          payload = JSON.parse(fs.readFileSync(outJson, "utf-8"));
        } catch (e) {
          payload = null;
        }
        if (payload && payload.result && !payload.error && !payload.timeout) break;
        if (attempt < MAX_ATTEMPTS) {
          console.log(`[run_full_easy] ${runId} attempt ${attempt} failed, retrying...`);
        }
      }
    }

    const final = payload && payload.result ? payload.result.finalResultCount : "ERROR";
    console.log(`[run_full_easy] ${idx}/${rows.length} DONE ${runId} final=${final} error=${payload && payload.error ? "YES" : "no"}`);
  }

  console.log(`[run_full_easy] all ${rows.length} runs complete. JSON checkpoints in ${TMP_DIR}`);
}

main();
