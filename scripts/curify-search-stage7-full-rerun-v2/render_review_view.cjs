#!/usr/bin/env node
/**
 * Renders a condensed, human-readable Markdown view of all 68
 * baseline-vs-D-mode comparisons (query, baseline top titles, D top10
 * titles, counts, guard triggers) for the structured Top-10 review pass.
 * Read-only against the compiled before/after CSV -- writes to a scratch
 * file, NOT one of the 7 required deliverables.
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { parseCsv } = require("./csv_utils.cjs");

const ADHOC_ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc";
const OUT_DIR = path.join(ADHOC_ROOT, "docs/daily_report/7.14/search-relevance-stage7-rerun/full-68-rerun-v2");
const BEFORE_AFTER_CSV = path.join(OUT_DIR, "hard_queries_before_after_68_2026-07-14.csv");

function safeParse(s, fallback) {
  try { return JSON.parse(s); } catch { return fallback; }
}

function main() {
  const rows = parseCsv(fs.readFileSync(BEFORE_AFTER_CSV, "utf-8"));
  const lines = [];
  for (const r of rows) {
    const baselineTop = safeParse(r.baseline_top_results, []);
    const afterTop = safeParse(r.after_top_10, []);
    const baselineTitles = baselineTop.map((t) => t.title).join(" | ");
    const afterTitles = afterTop.map((t) => `${t.title}[${t.strict_or_relaxed}]`).join(" | ");
    lines.push(`### ${r.query_id}: ${r.query}`);
    lines.push(`- baseline: count=${r.baseline_result_count} verdict=${r.baseline_relevance} top=${baselineTitles || "(none)"}`);
    lines.push(`- after(D): count=${r.after_result_count} rewrite_triggered=${r.after_rewrite_triggered} full_catalog=${r.full_catalog_after} 1000+=${r.thousand_plus_after} zero=${r.zero_result_after}`);
    lines.push(`  top10: ${afterTitles || "(none)"}`);
    const guards = safeParse(r.after_guard_triggers, {});
    const guardsFired = Object.entries(guards).filter(([, v]) => v === "true" || v === true).map(([k]) => k);
    lines.push(`  guards_fired: ${guardsFired.length ? guardsFired.join(",") : "none"}`);
    const rejRewrites = safeParse(r.after_rejected_rewrites, []);
    const rejReasons = safeParse(r.after_rejection_reasons, []);
    if (rejRewrites.length) lines.push(`  rejected_rewrites: ${JSON.stringify(rejRewrites)} reasons=${JSON.stringify(rejReasons)}`);
    lines.push("");
  }
  const outPath = "/tmp/curify-stage7r-prompt4-v2/review_view.md";
  fs.writeFileSync(outPath, lines.join("\n"));
  console.log(`wrote ${rows.length} query blocks -> ${outPath}`);
}

main();
