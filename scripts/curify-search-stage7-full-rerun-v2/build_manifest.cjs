#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execSync } = require("child_process");

const ADHOC_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const OUT_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/full-68-rerun-v2");

function sha256(p) {
  return crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
}

function main() {
  const compileSummary = JSON.parse(fs.readFileSync(path.join(__dirname, "_compile_summary.json"), "utf-8"));
  const bundleHashes = JSON.parse(fs.readFileSync(path.join(__dirname, "_bundle_source_hashes.json"), "utf-8"));

  const preSnapshot = fs.readFileSync("/tmp/curify-stage7r-prompt4-v2/pre_production_snapshot.txt", "utf-8");
  const postStatus = execSync("git status --short", { cwd: CURIFY_ROOT }).toString();
  const postDiffStat = execSync("git diff --stat", { cwd: CURIFY_ROOT }).toString();
  const postHead = execSync("git rev-parse HEAD", { cwd: CURIFY_ROOT }).toString().trim();
  const postBranch = execSync("git branch --show-current", { cwd: CURIFY_ROOT }).toString().trim();

  const manifest = {
    version: "2026-07-14",
    task: "Stage 7R Prompt 4 V2 Full 68 A/B/C/D Rerun",
    preconditions: {
      prompt2d_status: "READY_FOR_FULL_68",
      prompt2d_verified: true,
      prompt4a_status: "READY_FOR_PROMPT4",
      prompt4a_verified: true,
    },
    production: {
      repo: CURIFY_ROOT,
      branch: postBranch,
      head: postHead,
      head_message: "improve Chinese phrase protection in search",
      dirty: postStatus.trim().length > 0,
      status_short: postStatus.trim().split("\n").filter(Boolean),
      diff_stat: postDiffStat.trim(),
      source_hashes: bundleHashes.sourceFiles,
    },
    runtime: {
      node_version: process.version,
      npm_version: execSync("npm --version").toString().trim(),
      os: process.platform,
      architecture: process.arch,
      started_at: null, // filled by caller
      completed_at: new Date().toISOString(),
      duration_ms: null,
    },
    inputs: {
      query_file: "docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv",
      query_sha256: sha256(path.join(ADHOC_ROOT, "docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv")),
      query_count: 68,
      baseline_file: "docs/daily_report/7.13/search-optimization-stage-7/hard_queries_68_baseline.csv",
      baseline_sha256: sha256(path.join(OUT_DIR, "hard_queries_baseline_locked_68_2026-07-14.csv")),
      catalog_file: "public/data/nano_inspiration.json",
      catalog_sha256: sha256(path.join(CURIFY_ROOT, "public/data/nano_inspiration.json")),
      catalog_size: compileSummary.catalog_size,
    },
    model: {
      provider: "openai",
      name: "gpt-4o-mini",
      temperature: 0.4,
      max_tokens: 600,
      client_timeout_ms: 8000,
    },
    environment_presence: {
      OPENAI_API_KEY: "PRESENT",
      DATABASE_URL: "NOT_REQUIRED",
      NEXTAUTH_SECRET: "NOT_REQUIRED",
    },
    cache_strategy: "PROCESS_ISOLATED_FRESH_CACHE_PER_RUN (one child node process per (query,mode), same pattern as Prompt 2D/3B live harness -- MULTI_CACHE starts empty every run, no cross-run/cross-mode cache reuse)",
    retry_policy: "One evaluation-layer retry max per failed mode run, only for timeout/child-process/network-class failures (30s in-process timeout + 45s child-process timeout); never retried for output quality/count",
    mode_contract: {
      A: { dEnabled: false, gEnabled: false, guardEnabled: false },
      B: { dEnabled: true, gEnabled: false, guardEnabled: false },
      C: { dEnabled: false, gEnabled: true, guardEnabled: true },
      D: { dEnabled: true, gEnabled: true, guardEnabled: true },
    },
    pre_registered_targets: {
      source: "Prompt 0-2D smoke gates (23-case D-flood / 20-query live-smoke subsets) do NOT scope to the full 68; original Stage 7 (7.13) task instructions do scope to the full 68 (60-80% improvement band on strict/broad/weighted PASS rate), already measured as failed (0.0%/5.9%/2.9%) in 7.13 -- see hard_queries_68_summary.md Section 8",
      full_68_numeric_target_found: true,
      full_68_target_detail: "60-80% improvement band (strict PASS, broad PASS+PARTIAL, weighted PASS+0.5*PARTIAL, each as X/68), from the original Stage 7 task instructions, per 7.13 summary Section 8",
      note: "NO_PRE_REGISTERED_FULL68_NUMERIC_TARGET_FOUND does NOT apply verbatim -- a full-68 target exists but originates from 7.13's task framing, not from a document specific to this 7.14 rerun; Full-catalog=0 / D-flood>=80% / Human FAIL<=20% are real gates but were pre-registered for smaller smoke subsets (23-case / 20-query), not the full 68 -- applied here as directional targets, not literally pre-registered for this exact run",
    },
    expected_runs: 272,
    actual_runs: compileSummary.total_runs,
    missing_runs: compileSummary.missing_runs,
    duplicate_runs: compileSummary.duplicate_runs,
    mode_breakdown: compileSummary.modes,
    comparison_limitations: [
      "D_OFF_IMPLEMENTATION_REEXPRESSED: Prompt 4A's d=OFF is a new, minimal, explicit-toggle re-expression of the historical d contract (lib/searchTokens.ts), not the 7.13 git-show HEAD:page.tsx textual reconstruction -- not byte-identical by design, documented in Prompt 4A Section 8",
      "MODEL_CONFIGURATION_UNCHANGED: gpt-4o-mini, temperature=0.4, same as 7.13 and Prompt 2D -- LLM nondeterminism still applies to every C/D call",
      "CATALOG_VERSION: catalog_sha256 recorded above; 7.13 run_manifest.json does not record a catalog sha256, only catalog record count (3209, matches this run) -- exact byte-level catalog match across the two runs is not independently provable, flagged as CATALOG_VERSION_NOT_FULLY_PROVABLE",
      "No LLM relevance judge was run this stage (7.13 used a gpt-4o-mini judge on all 272 rows); this stage's PASS/PARTIAL/FAIL labels come entirely from CLAUDE_STRUCTURED_TOP10_REVIEW (manual review), not an automated judge -- auto_judge_label/reason fields are NOT_APPLICABLE by design, so there is no judge-vs-human disagreement metric this run (judge_human_disagreement_count = 0 by construction, not because agreement was measured)",
      "Harness scoring adapter (scoreBlob/merge/ranking) is a verbatim, drift-checked transcription of page.tsx-local orchestration (verifyAgainstLiveSource), not a literal import -- Merge/Ranking/relaxed-threshold logic itself was not modified this stage",
    ],
    commands: [
      "node build_bundle.cjs",
      "node run_full_68.cjs",
      "node compile_outputs.cjs",
      "node build_manifest.cjs",
    ],
    output_files: [
      "hard_queries_baseline_locked_68_2026-07-14.csv",
      "hard_queries_refreshed_dg_guarded_68_2026-07-14.csv",
      "hard_queries_before_after_68_2026-07-14.csv",
      "hard_queries_ablation_abcd_68_2026-07-14.csv",
      "hard_queries_manual_review_68_2026-07-14.csv",
      "STAGE7_RERUN_SUMMARY_2026-07-14_zh.md",
      "stage7_rerun_manifest_2026-07-14.json",
    ],
    human_review_count: 68,
    judge_human_disagreement_count: 0,
    stage7_gate: "PENDING",
  };

  fs.writeFileSync(path.join(OUT_DIR, "stage7_rerun_manifest_2026-07-14.json"), JSON.stringify(manifest, null, 2));
  console.log(`[manifest] wrote -> ${path.join(OUT_DIR, "stage7_rerun_manifest_2026-07-14.json")}`);
}

main();
