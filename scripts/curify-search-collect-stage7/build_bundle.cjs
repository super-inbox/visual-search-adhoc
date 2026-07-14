#!/usr/bin/env node
/**
 * Stage 7 evaluation-harness bundler.
 *
 * READ-ONLY against curify-frontend: uses esbuild (already a transitive
 * dependency there, resolved from its own node_modules) to bundle the real,
 * unmodified Stage 5/6 production modules —
 *   lib/searchRewrite.ts
 *   lib/query_phrase_aliases.ts
 *   lib/cjk_tokenizer.ts
 *   lib/zh_normalize.ts
 * — into one CJS file this harness can require(). No file in curify-frontend
 * is written to. @node-rs/jieba and openai are marked external so they
 * resolve from curify-frontend's real node_modules at require-time (this
 * script's own required() call sets `cwd` via NODE_PATH so that works).
 */
"use strict";
const path = require("path");
const fs = require("fs");

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const esbuildPath = path.join(CURIFY_ROOT, "node_modules/esbuild");
const esbuild = require(esbuildPath);

const OUT_DIR = __dirname;
const OUT_FILE = path.join(OUT_DIR, "_bundle_stage56.cjs");

// Entry shim: re-export everything the harness needs from the real modules.
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
console.log(`Bundled real Stage 5/6 modules -> ${OUT_FILE}`);

// Verify the SHA-256 of each source file that went into the bundle, for the
// run manifest / audit trail (proves which exact source lines were used).
const crypto = require("crypto");
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
