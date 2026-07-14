#!/usr/bin/env node
/**
 * Stage 7R Prompt 3 guard-smoke bundler.
 *
 * READ-ONLY against curify-frontend: uses esbuild (resolved from curify-
 * frontend's own node_modules) to bundle the REAL, unmodified, CURRENT
 * (post-Prompt-2) production modules —
 *   lib/searchRewrite.ts
 *   lib/query_phrase_aliases.ts
 *   lib/cjk_tokenizer.ts
 *   lib/zh_normalize.ts
 *   lib/topic_resolver.ts
 * — into one CJS file this harness can require(). No file in curify-frontend
 * is written to or modified.
 *
 * This is a SEPARATE bundle from scripts/curify-search-collect-stage7/
 * _bundle_stage56.cjs (that one was built 2026-07-13, BEFORE Prompt 2's
 * Guard changes, and is therefore stale for this purpose — reusing it would
 * silently test pre-Guard code). This bundler additionally exports
 * `flattenPathsWithDiagnostics`, the real Guard 2 (subject-binding) function
 * that did not exist at the time the old bundle was built.
 *
 * Usage: node build_bundle.cjs
 */
"use strict";
const path = require("path");
const fs = require("fs");
const crypto = require("crypto");

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const esbuildPath = path.join(CURIFY_ROOT, "node_modules/esbuild");
const esbuild = require(esbuildPath);

const OUT_DIR = __dirname;
const OUT_FILE = path.join(OUT_DIR, "_bundle_current.cjs");

const ENTRY_SRC = `
export { tsToSc } from "${CURIFY_ROOT}/lib/zh_normalize";
export {
  applyPhraseAliasRules,
  applyPhraseAliasRulesExcluding,
  segmentCJKToken,
  CJK_ATOMIC_PHRASES,
  PHRASE_ALIAS_RULES,
} from "${CURIFY_ROOT}/lib/query_phrase_aliases";
export { segmentText } from "${CURIFY_ROOT}/lib/cjk_tokenizer";
export {
  getMultiQueryPaths,
  flattenPaths,
  flattenPathsWithDiagnostics,
} from "${CURIFY_ROOT}/lib/searchRewrite";
export { buildTemplateTopicsMap, resolveTopics } from "${CURIFY_ROOT}/lib/topic_resolver";
`;

const entryFile = path.join(OUT_DIR, "_entry.ts");
fs.writeFileSync(entryFile, ENTRY_SRC, "utf-8");

esbuild.buildSync({
  entryPoints: [entryFile],
  bundle: true,
  platform: "node",
  format: "cjs",
  target: "node18",
  outfile: OUT_FILE,
  external: ["@node-rs/jieba", "@node-rs/jieba/dict", "openai"],
  logLevel: "warning",
});

fs.unlinkSync(entryFile);
console.log(`Bundled current (post-Prompt-2) production modules -> ${OUT_FILE}`);

const sourceFiles = [
  "lib/zh_normalize.ts",
  "lib/query_phrase_aliases.ts",
  "lib/cjk_tokenizer.ts",
  "lib/searchRewrite.ts",
  "lib/topic_resolver.ts",
];
const hashes = {};
for (const f of sourceFiles) {
  const full = path.join(CURIFY_ROOT, f);
  hashes[f] = crypto.createHash("sha256").update(fs.readFileSync(full)).digest("hex");
}
fs.writeFileSync(
  path.join(OUT_DIR, "_bundle_source_hashes.json"),
  JSON.stringify({ builtAt: new Date().toISOString(), sourceFiles: hashes }, null, 2)
);
console.log("Source hashes written -> _bundle_source_hashes.json");
