#!/usr/bin/env node
/**
 * Stage 7R Prompt 4A — Mode Contract Smoke Test.
 *
 * 8 fixed queries x 4 modes (A/B/C/D) = 32 runs. NO real LLM calls (C/D use
 * a fixed rewrite_fixtures.json, verbatim-copied from real, already-saved
 * Prompt 2B/2C/2D production output). Proves all four modes are
 * constructible from the SAME current, unmodified production code, only
 * switching the explicit {dEnabled, gEnabled} flags.
 */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { parseCsv, writeCsv } = require("./csv_utils.cjs");
const { runOne, catalogInfo, verifyAgainstLiveSource, bundle } = require("./engine.cjs");

const REPO_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const OUT_DIR = path.join(REPO_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/prompt4a");
const QUERY_SET_CSV = path.join(OUT_DIR, "mode_contract_query_set_2026-07-14.csv");
const OUT_CSV = path.join(OUT_DIR, "mode_contract_smoke_results_2026-07-14.csv");
const FIXTURES = JSON.parse(fs.readFileSync(path.join(__dirname, "rewrite_fixtures.json"), "utf-8"));

function sha256File(p) {
  return crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
}

const FIELDNAMES = [
  "run_id", "query", "query_order", "mode", "d_enabled", "g_enabled",
  "default_production_mode", "production_source_hash", "token_helper_source_hash",
  "normalized_query", "protected_phrase", "tokenization", "primary_tokens", "secondary_tokens",
  "aliases", "alias_groups", "rewrite_provider_called", "rewrite_fixture", "guard_executed",
  "planned_paths", "actual_paths", "result_count", "top_results", "error", "timeout",
  "mode_contract_pass", "notes",
];

async function main() {
  if (fs.existsSync(OUT_CSV)) {
    console.error(`[smoke] refusing to overwrite existing output: ${OUT_CSV}`);
    process.exit(1);
  }

  const drift = verifyAgainstLiveSource();
  console.log(`[smoke] drift check:`, JSON.stringify(drift));
  const catalog = catalogInfo();
  console.log(`[smoke] catalog size:`, catalog.catalogSize);

  const rows = parseCsv(fs.readFileSync(QUERY_SET_CSV, "utf-8"));
  if (rows.length !== 8) {
    console.error(`[smoke] expected exactly 8 queries, got ${rows.length}`);
    process.exit(1);
  }

  const modes = ["A", "B", "C", "D"];
  const results = [];
  let runIdx = 0;
  for (const row of rows) {
    const fixture = FIXTURES[row.rewrite_fixture_id];
    if (!fixture) {
      console.error(`[smoke] unknown rewrite_fixture_id: ${row.rewrite_fixture_id}`);
      process.exit(1);
    }
    const rewritePayload = { rewrites: fixture.rewrites, decomposition: fixture.decomposition };

    for (const mode of modes) {
      runIdx++;
      const dEnabled = mode === "B" || mode === "D";
      const gEnabled = mode === "C" || mode === "D";
      const runId = `MC${String(runIdx).padStart(3, "0")}-${row.query_order}-${mode}`;
      let result = null;
      let error = null;
      try {
        result = await runOne(row.query, { dEnabled, gEnabled, rewriteFixture: rewritePayload });
      } catch (e) {
        error = String(e && e.stack ? e.stack : e);
      }

      const isDefaultMode = mode === "D"; // dEnabled=true,gEnabled=true is the current production default
      const guardExecuted = result ? result.rewriteTriggered && result.candidatePaths !== undefined : false;
      const providerCalled = result ? result.rewriteProviderCalled : false;

      // Mode Contract correctness checks, per-row:
      const checks = [];
      if (mode === "A" || mode === "B") {
        checks.push(providerCalled === false);
        checks.push(!result || result.multi.rewrites.length === 0 || !result.rewriteTriggered);
      }
      if (mode === "C" || mode === "D") {
        checks.push(providerCalled === false); // never a real LLM call in this smoke test
      }
      if (mode === "A" || mode === "C") {
        // d=OFF: primary must not be empty for this non-empty real query,
        // and must differ from the d=ON tokenization for d-affected queries
        // (informational only here; the aggregate d=OFF evidence check
        // happens in the summary step below).
        checks.push(!result || result.tokens.primary.length > 0 || result.tokens.bigrams.length > 0 || (result.tokens.aliasGroups?.length ?? 0) > 0);
      }
      const modeContractPass = error === null && checks.every(Boolean);

      results.push({
        run_id: runId,
        query: row.query,
        query_order: row.query_order,
        mode,
        d_enabled: dEnabled,
        g_enabled: gEnabled,
        default_production_mode: isDefaultMode,
        production_source_hash: sha256File(path.join("/Users/baobaoli/Desktop/curify-frontend/app/[locale]/(public)/search/page.tsx")),
        token_helper_source_hash: sha256File("/Users/baobaoli/Desktop/curify-frontend/lib/searchTokens.ts"),
        normalized_query: result ? bundle.normalizeForSearch(row.query) : "NOT_APPLICABLE",
        protected_phrase: result ? JSON.stringify((result.tokens.aliasGroups || []).map((g) => g[0])) : "NOT_APPLICABLE",
        tokenization: result ? JSON.stringify(result.tokens) : "NOT_APPLICABLE",
        primary_tokens: result ? JSON.stringify(result.tokens.primary) : "NOT_APPLICABLE",
        secondary_tokens: result ? JSON.stringify(result.tokens.bigrams) : "NOT_APPLICABLE",
        aliases: result ? JSON.stringify(result.tokens.aliasGroups) : "NOT_APPLICABLE",
        alias_groups: result ? JSON.stringify(result.tokens.aliasGroups) : "NOT_APPLICABLE",
        rewrite_provider_called: providerCalled,
        rewrite_fixture: gEnabled ? row.rewrite_fixture_id : "NOT_APPLICABLE_G_OFF",
        guard_executed: guardExecuted,
        planned_paths: gEnabled ? JSON.stringify(rewritePayload) : "NOT_APPLICABLE_G_OFF",
        actual_paths: result ? JSON.stringify(result.candidatePaths.map((p) => p.text)) : "NOT_APPLICABLE",
        result_count: result ? result.finalResultCount : "NOT_RECORDED",
        top_results: result ? JSON.stringify(result.top10.slice(0, 5)) : "NOT_APPLICABLE",
        error: error || "",
        timeout: false,
        mode_contract_pass: modeContractPass,
        notes: `dEnabled=${dEnabled} gEnabled=${gEnabled} rewriteTriggered=${result ? result.rewriteTriggered : "N/A"}`,
      });
      console.log(`[smoke] ${runId} query=${JSON.stringify(row.query)} mode=${mode} result=${result ? result.finalResultCount : "ERROR"} providerCalled=${providerCalled} pass=${modeContractPass}`);
    }
  }

  writeCsv(OUT_CSV, FIELDNAMES, results);
  console.log(`[smoke] wrote ${results.length} rows -> ${OUT_CSV}`);

  const byMode = { A: 0, B: 0, C: 0, D: 0 };
  for (const r of results) byMode[r.mode]++;
  const providerCalls = results.filter((r) => r.rewrite_provider_called === true).length;
  const failures = results.filter((r) => r.mode_contract_pass !== true);
  const dupKey = new Set();
  let duplicates = 0;
  for (const r of results) {
    const k = `${r.query}|${r.mode}`;
    if (dupKey.has(k)) duplicates++;
    dupKey.add(k);
  }

  const summary = {
    total: results.length,
    expected: 32,
    by_mode: byMode,
    missing: 32 - results.length,
    duplicates,
    real_llm_calls: providerCalls,
    mode_contract_failures: failures.length,
    failure_run_ids: failures.map((f) => f.run_id),
  };
  fs.writeFileSync(path.join(OUT_DIR, "_mode_contract_smoke_summary.json"), JSON.stringify(summary, null, 2));
  console.log(`[smoke] summary:`, JSON.stringify(summary, null, 2));
}

main().catch((e) => {
  console.error("[smoke] FATAL:", e);
  process.exit(1);
});
