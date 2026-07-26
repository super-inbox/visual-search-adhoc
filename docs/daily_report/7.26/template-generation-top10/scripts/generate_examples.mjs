#!/usr/bin/env node
/*
 * generate_examples.mjs
 *
 * Standalone batch image generator for the Curify Top-10 Template Generation task.
 *
 * Reuses the @google/genai SDK already installed in curify-frontend/node_modules and the
 * GEMINI_API_KEY already present in curify-frontend/.env.local (read-only borrow — this
 * script never modifies any file inside curify-frontend or curify-studio, never writes to
 * any database, and never calls any CDN/production sync command).
 *
 * All output is written exclusively under this package's own templates/ directory.
 *
 * Usage:
 *   node scripts/generate_examples.mjs --dry-run
 *   node scripts/generate_examples.mjs --pilot                # example-01 only, all 10 templates
 *   node scripts/generate_examples.mjs                        # all templates, all examples
 *   node scripts/generate_examples.mjs --template=T03
 *   node scripts/generate_examples.mjs --example=template-01-workbook-practice-book-covers-example-02
 *   node scripts/generate_examples.mjs --concurrency=2 --interval-ms=1500 --timeout-ms=90000 --max-retries=2
 *
 * Resume behavior: an example whose metadata.json already has status "success" is skipped
 * (never overwritten) unless --force is passed.
 */

"use strict";

import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const OUT_ROOT = path.resolve(__dirname, "..");
const FRONTEND_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const GENERATION_LOG = path.join(OUT_ROOT, "generation_log.jsonl");
const EXAMPLE_MANIFEST = path.join(OUT_ROOT, "example_manifest.json");
const TEMPLATE_MANIFEST = path.join(OUT_ROOT, "template_manifest.json");

const DEFAULT_MODEL = "gemini-3-pro-image-preview";

// ── env (read-only borrow from curify-frontend/.env.local) ─────────────────
function loadEnvLocal(envPath) {
  const out = {};
  if (!fs.existsSync(envPath)) return out;
  const text = fs.readFileSync(envPath, "utf-8");
  for (const line of text.split("\n")) {
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (!m) continue;
    let val = m[2];
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    out[m[1]] = val;
  }
  return out;
}

const envVars = loadEnvLocal(path.join(FRONTEND_ROOT, ".env.local"));
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || envVars.GEMINI_API_KEY;

// ── SDK (resolved from curify-frontend/node_modules, not copied/installed here) ──
let GoogleGenAI, Modality;
try {
  const sdkPath = path.join(FRONTEND_ROOT, "node_modules", "@google", "genai");
  ({ GoogleGenAI, Modality } = require(sdkPath));
} catch (e) {
  console.error("Failed to load @google/genai from curify-frontend/node_modules:", e.message);
  process.exit(1);
}

// ── CLI args ─────────────────────────────────────────────────────────────
function parseArgs() {
  const args = process.argv.slice(2);
  const out = {
    dryRun: false,
    pilot: false,
    template: null,
    example: null,
    concurrency: 2,
    intervalMs: 1200,
    timeoutMs: 120000,
    maxRetries: 2,
    force: false,
    model: DEFAULT_MODEL,
  };
  for (const a of args) {
    if (a === "--dry-run") out.dryRun = true;
    else if (a === "--pilot") out.pilot = true;
    else if (a === "--force") out.force = true;
    else if (a.startsWith("--template=")) out.template = a.split("=")[1];
    else if (a.startsWith("--example=")) out.example = a.split("=")[1];
    else if (a.startsWith("--concurrency=")) out.concurrency = parseInt(a.split("=")[1], 10);
    else if (a.startsWith("--interval-ms=")) out.intervalMs = parseInt(a.split("=")[1], 10);
    else if (a.startsWith("--timeout-ms=")) out.timeoutMs = parseInt(a.split("=")[1], 10);
    else if (a.startsWith("--max-retries=")) out.maxRetries = parseInt(a.split("=")[1], 10);
    else if (a.startsWith("--model=")) out.model = a.split("=")[1];
  }
  return out;
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf-8"));
}
function writeJson(p, obj) {
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + "\n", "utf-8");
}
function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}
function appendLog(entry) {
  fs.appendFileSync(
    GENERATION_LOG,
    JSON.stringify({ ts: new Date().toISOString(), ...entry }) + "\n",
    "utf-8"
  );
}

async function withTimeout(promise, ms, label) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`timeout after ${ms}ms: ${label}`)), ms);
  });
  try {
    return await Promise.race([promise, timeout]);
  } finally {
    clearTimeout(timer);
  }
}

async function generateOne(gemini, model, prompt, outPath, timeoutMs) {
  const response = await withTimeout(
    gemini.models.generateContent({
      model,
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: { responseModalities: [Modality.IMAGE, Modality.TEXT] },
    }),
    timeoutMs,
    outPath
  );
  const parts = response?.candidates?.[0]?.content?.parts || [];
  const imagePart = parts.find((p) => p?.inlineData?.data);
  if (!imagePart?.inlineData?.data) {
    const text = parts.map((p) => p?.text || "").join("\n");
    const err = new Error(`no image returned. text=${text.slice(0, 300) || "[none]"}`);
    err.responseSummary = {
      finishReason: response?.candidates?.[0]?.finishReason || null,
      textOnly: text.slice(0, 500),
    };
    throw err;
  }
  const buf = Buffer.from(imagePart.inlineData.data, "base64");
  await fsp.writeFile(outPath, buf);
  return {
    bytes: buf.length,
    finishReason: response?.candidates?.[0]?.finishReason || null,
    mimeType: imagePart.inlineData.mimeType || "image/png",
  };
}

async function processExample(gemini, args, exampleEntry) {
  const edir = path.join(OUT_ROOT, exampleEntry.example_dir);
  const promptPath = path.join(edir, "prompt.txt");
  const metaPath = path.join(edir, "metadata.json");
  const outPath = path.join(edir, "output.png");

  const meta = readJson(metaPath);

  if (meta.status === "success" && !args.force) {
    console.log(`  ↩  skip (already success): ${exampleEntry.example_id}`);
    appendLog({ example_id: exampleEntry.example_id, event: "skip_existing_success" });
    return "skipped";
  }

  const prompt = fs.readFileSync(promptPath, "utf-8");

  if (args.dryRun) {
    console.log(`  (dry-run) would generate: ${exampleEntry.example_id} [${prompt.length} char prompt]`);
    appendLog({ example_id: exampleEntry.example_id, event: "dry_run", prompt_chars: prompt.length });
    return "dry_run";
  }

  let attempt = meta.attempt_count || 0;
  let lastError = null;

  while (attempt < 1 + args.maxRetries) {
    attempt += 1;
    process.stdout.write(`  → [attempt ${attempt}] ${exampleEntry.example_id} ... `);
    try {
      const result = await generateOne(gemini, args.model, prompt, outPath, args.timeoutMs);
      const newMeta = {
        status: "success",
        generation_model: args.model,
        parameters: { responseModalities: ["IMAGE", "TEXT"] },
        attempt_count: attempt,
        generated_at: new Date().toISOString(),
        output_path: path.relative(OUT_ROOT, outPath),
        bytes: result.bytes,
        mime_type: result.mimeType,
        finish_reason: result.finishReason,
        error: null,
        qa_result: null,
      };
      writeJson(metaPath, newMeta);
      console.log(`✓ (${result.bytes} bytes)`);
      appendLog({
        example_id: exampleEntry.example_id,
        event: "success",
        attempt,
        bytes: result.bytes,
        finish_reason: result.finishReason,
      });
      return "success";
    } catch (e) {
      lastError = e.message;
      console.log(`✗ ${e.message}`);
      appendLog({
        example_id: exampleEntry.example_id,
        event: "attempt_failed",
        attempt,
        error: e.message,
        response_summary: e.responseSummary || null,
      });
      if (attempt < 1 + args.maxRetries) {
        await sleep(args.intervalMs * 2);
      }
    }
  }

  const failMeta = {
    status: "failed",
    generation_model: args.model,
    parameters: { responseModalities: ["IMAGE", "TEXT"] },
    attempt_count: attempt,
    generated_at: new Date().toISOString(),
    output_path: null,
    error: lastError,
    qa_result: null,
  };
  writeJson(metaPath, failMeta);
  appendLog({ example_id: exampleEntry.example_id, event: "final_failure", attempts: attempt, error: lastError });
  return "failed";
}

async function runPool(items, worker, concurrency, intervalMs) {
  const results = [];
  let idx = 0;
  async function next() {
    while (idx < items.length) {
      const my = idx++;
      const item = items[my];
      const r = await worker(item);
      results[my] = r;
      if (intervalMs > 0) await sleep(intervalMs);
    }
  }
  const workers = Array.from({ length: Math.max(1, concurrency) }, () => next());
  await Promise.all(workers);
  return results;
}

async function main() {
  const args = parseArgs();

  if (!GEMINI_API_KEY && !args.dryRun) {
    console.error("❌ GEMINI_API_KEY not found (checked process.env and curify-frontend/.env.local)");
    process.exit(1);
  }

  const exampleManifest = readJson(EXAMPLE_MANIFEST);
  let examples = exampleManifest.examples;

  if (args.template) examples = examples.filter((e) => e.template_id === args.template);
  if (args.example) examples = examples.filter((e) => e.example_id === args.example);
  if (args.pilot) examples = examples.filter((e) => e.example_index === 1);

  console.log("=== generate_examples.mjs ===");
  console.log("mode:        ", args.dryRun ? "DRY-RUN" : "LIVE");
  console.log("pilot:       ", args.pilot);
  console.log("template:    ", args.template || "(all)");
  console.log("example:     ", args.example || "(all)");
  console.log("concurrency: ", args.concurrency);
  console.log("interval_ms: ", args.intervalMs);
  console.log("timeout_ms:  ", args.timeoutMs);
  console.log("max_retries: ", args.maxRetries);
  console.log("model:       ", args.model);
  console.log("count:       ", examples.length);
  console.log("");

  const gemini = args.dryRun ? null : new GoogleGenAI({ apiKey: GEMINI_API_KEY });

  appendLog({
    event: "run_start",
    mode: args.dryRun ? "dry_run" : "live",
    pilot: args.pilot,
    template_filter: args.template,
    example_filter: args.example,
    count: examples.length,
  });

  const results = await runPool(
    examples,
    (ex) => processExample(gemini, args, ex),
    args.dryRun ? examples.length : args.concurrency,
    args.dryRun ? 0 : args.intervalMs
  );

  const tally = { success: 0, failed: 0, skipped: 0, dry_run: 0 };
  for (const r of results) tally[r] = (tally[r] || 0) + 1;

  console.log("\n" + "─".repeat(40));
  console.log("Success:", tally.success);
  console.log("Failed: ", tally.failed);
  console.log("Skipped:", tally.skipped);
  console.log("DryRun: ", tally.dry_run);

  appendLog({ event: "run_end", tally });
}

main().catch((e) => {
  console.error("❌ Fatal:", e);
  appendLog({ event: "fatal_error", error: e.message });
  process.exit(1);
});
