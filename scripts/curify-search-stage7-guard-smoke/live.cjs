#!/usr/bin/env node
/**
 * Stage 7R Prompt 3B — Phase B: Limited Live Smoke, single-query entry
 * point.
 *
 * Genuinely calls the real, current (post-Prompt-2B) production pipeline:
 *   bundle.getMultiQueryPaths(query)   — a REAL OpenAI API call (gpt-4o-mini,
 *                                        per lib/searchRewrite.ts's MODEL
 *                                        constant), when the query's
 *                                        first-pass result count is thin
 *                                        (LOW_RESULT_THRESHOLD, same gate as
 *                                        production)
 *   bundle.flattenPathsWithDiagnostics — Guard 2 (subject-binding) + Guard R
 *                                        (rewrite anchor validation), the
 *                                        real, current lib/searchRewrite.ts
 *                                        function
 *   the transcribed scoreBlob/buildSearchTokens/hasExecutableConstraint
 *                                        (Guard 1), drift-checked against
 *                                        the live page.tsx before running
 *
 * Deliberately run as ONE PROCESS PER LIVE RUN (see run_live_smoke.sh) so
 * each invocation gets a fresh, empty in-memory MULTI_CACHE — the exact
 * same isolation a real Vercel serverless invocation gets in production
 * (lib/searchRewrite.ts's own CACHE/MULTI_CACHE comment: "Vercel serverless
 * invocations don't share memory so this saves nothing across requests in
 * prod"). This means Q39/Q40/Q42's two runs are guaranteed genuine,
 * independent LLM calls, never silently served from a same-process cache —
 * no Query text mangling, no cache namespace hacks, no global cache
 * clearing.
 *
 * Usage:
 *   node --env-file=<curify-frontend>/.env.local live.cjs \
 *     --live-run-id L01-1 --query "..." --run-number 1 --out /tmp/xxx.json
 *
 * Writes one JSON result object to --out. Never logs the OPENAI_API_KEY
 * value itself (only whether it was present, via engine.cjs/production
 * code's own env check).
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
  const { "live-run-id": liveRunId, query, "run-number": runNumber, out } = args;
  if (!liveRunId || query === undefined || !runNumber || !out) {
    console.error("[live] missing required args: --live-run-id --query --run-number --out");
    process.exit(1);
  }

  const drift = verifyAgainstLiveSource();
  const catalog = catalogInfo();

  const startedAt = new Date().toISOString();
  const t0 = Date.now();
  let result = null;
  let error = null;
  let timeout = false;

  const TIMEOUT_MS = 25_000;
  try {
    result = await Promise.race([
      runOne(query, {}), // no override -> real getMultiQueryPaths call if low-result gate passes
      new Promise((_, reject) => setTimeout(() => reject(new Error("LIVE_HARNESS_TIMEOUT_25000MS")), TIMEOUT_MS)),
    ]);
  } catch (e) {
    error = String(e && e.stack ? e.stack : e);
    timeout = /LIVE_HARNESS_TIMEOUT/.test(String(e && e.message));
  }
  const completedAt = new Date().toISOString();
  const durationMs = Date.now() - t0;

  const payload = {
    live_run_id: liveRunId,
    query,
    run_number: Number(runNumber),
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
    `[live] ${liveRunId} run#${runNumber} query=${JSON.stringify(query)} ` +
      `rewriteTriggered=${result ? result.rewriteTriggered : "N/A"} ` +
      `final=${result ? result.finalResultCount : "ERROR"} ` +
      `durationMs=${durationMs} error=${error ? "YES" : "no"}`
  );
}

main().catch((e) => {
  console.error("[live] FATAL:", e);
  process.exit(1);
});
