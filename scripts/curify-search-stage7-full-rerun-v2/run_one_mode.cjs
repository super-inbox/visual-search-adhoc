#!/usr/bin/env node
/**
 * Stage 7R Prompt 4 V2 -- single (query, mode) entry point. Run as ONE
 * PROCESS PER MODE RUN (see run_full_68.cjs) so each run gets a fresh, empty
 * in-memory MULTI_CACHE -- same isolation pattern as the Prompt 2D/3B live
 * harness. This means C/D calls to the real Rewrite Provider are always
 * genuine, independent LLM calls, never silently served from a same-process
 * cache.
 *
 * Usage:
 *   node --env-file=<curify-frontend>/.env.local run_one_mode.cjs \
 *     --query-id Q01 --query "..." --mode A --d-enabled false --g-enabled false --out /tmp/xxx.json
 */
"use strict";
const fs = require("fs");
const { runOne, catalogInfo, verifyAgainstLiveSource } = require("./engine.cjs");

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith("--")) {
      const key = argv[i].slice(2);
      out[key] = argv[i + 1];
      i++;
    }
  }
  return out;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const { "query-id": queryId, query, mode, "d-enabled": dEnabledRaw, "g-enabled": gEnabledRaw, out } = args;
  if (!queryId || query === undefined || !mode || dEnabledRaw === undefined || gEnabledRaw === undefined || !out) {
    console.error("[run_one_mode] missing required args");
    process.exit(1);
  }
  const dEnabled = dEnabledRaw === "true";
  const gEnabled = gEnabledRaw === "true";

  const drift = verifyAgainstLiveSource();
  const catalog = catalogInfo();

  const startedAt = new Date().toISOString();
  const t0 = Date.now();
  let result = null;
  let error = null;
  let timeout = false;

  const TIMEOUT_MS = 30_000;
  try {
    result = await Promise.race([
      runOne(query, { dEnabled, gEnabled }),
      new Promise((_, reject) => setTimeout(() => reject(new Error("FULL68_HARNESS_TIMEOUT_30000MS")), TIMEOUT_MS)),
    ]);
  } catch (e) {
    error = String(e && e.stack ? e.stack : e);
    timeout = /FULL68_HARNESS_TIMEOUT/.test(String(e && e.message));
  }
  const completedAt = new Date().toISOString();
  const durationMs = Date.now() - t0;

  const payload = {
    query_id: queryId,
    query,
    mode,
    d_enabled: dEnabled,
    g_enabled: gEnabled,
    started_at: startedAt,
    completed_at: completedAt,
    duration_ms: durationMs,
    drift_check: drift,
    catalog_size: catalog.catalogSize,
    openai_api_key_present: !!process.env.OPENAI_API_KEY,
    error,
    timeout,
    result: result
      ? {
          tokens: result.tokens,
          initialThinCount: result.initialThinCount,
          rewriteTriggered: result.rewriteTriggered,
          rewriteProviderCalled: result.rewriteProviderCalled,
          rewriteError: result.rewriteError,
          multi: result.multi,
          candidatePaths: result.candidatePaths,
          diagnostics: result.diagnostics,
          executedPathCount: result.executedPathCount,
          usedPathsCount: result.usedPathsCount,
          preMergeCount: result.preMergeCount,
          postMergeCount: result.postMergeCount,
          dedupCount: result.dedupCount,
          finalResultCount: result.finalResultCount,
          strictCount: result.strictCount,
          relaxedCount: result.relaxedCount,
          hasStrict: result.hasStrict,
          top10: result.top10,
        }
      : null,
  };

  fs.writeFileSync(out, JSON.stringify(payload, null, 2));
  console.log(
    `[run_one_mode] ${queryId} mode=${mode} query=${JSON.stringify(query)} ` +
      `rewriteTriggered=${result ? result.rewriteTriggered : "N/A"} ` +
      `final=${result ? result.finalResultCount : "ERROR"} ` +
      `durationMs=${durationMs} error=${error ? "YES" : "no"}`
  );
}

main().catch((e) => {
  console.error("[run_one_mode] FATAL:", e);
  process.exit(1);
});
