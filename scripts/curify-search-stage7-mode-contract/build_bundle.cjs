#!/usr/bin/env node
/**
 * Stage 7R Prompt 4A Mode Contract bundler.
 *
 * READ-ONLY against curify-frontend: uses esbuild (resolved from curify-
 * frontend's own node_modules) to bundle the REAL, unmodified, CURRENT
 * production modules —
 *   lib/searchTokens.ts       (Stage 7R Prompt 4A — the new `d` runtime
 *                               toggle; the whole point of this harness)
 *   lib/searchRewrite.ts      (Guard 2/R/N/S/Piggyback, real "g" pipeline)
 *   lib/query_phrase_aliases.ts
 *   lib/cjk_tokenizer.ts
 *   lib/zh_normalize.ts
 *   lib/topic_resolver.ts
 * — into one CJS file this harness can require(). No file in curify-frontend
 * is written to or modified. `buildSearchTokens`/`normalizeForSearch` are
 * imported directly from lib/searchTokens.ts — NOT transcribed — satisfying
 * Prompt 4A's "Search Page and Eval Harness must import the same helper"
 * requirement. Only Merge/Ranking/scoreBlob (page.tsx-local, not exported,
 * not modified this stage) remain a verbatim transcription in scoring.cjs,
 * same as the pre-existing curify-search-stage7-guard-smoke harness.
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
  buildSearchTokens,
  normalizeForSearch,
  DEFAULT_SEARCH_TOKENIZATION_OPTIONS,
  STOPWORDS,
} from "${CURIFY_ROOT}/lib/searchTokens";
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
console.log(`Bundled current production modules (incl. lib/searchTokens.ts) -> ${OUT_FILE}`);

const sourceFiles = [
  "lib/zh_normalize.ts",
  "lib/query_phrase_aliases.ts",
  "lib/cjk_tokenizer.ts",
  "lib/searchTokens.ts",
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
