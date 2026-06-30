#!/usr/bin/env node
/**
 * Google Images batch collector — fixed 58 query eval set.
 *
 * Usage:
 *   npx tsx scripts/google-image-eval/collect.ts [options]
 *
 * Options:
 *   --dry-run               Print queries only, do not start browser
 *   --start N               First query_id to process
 *   --end N                 Last query_id to process (inclusive)
 *   --query-id N            Process a single query by ID
 *   --query "text"          Process a single query by text
 *   --force                 Re-run complete queries
 *   --headless              Use headless Chromium (default: headful)
 *   --validate-only         Run validate.ts and exit
 *   --delay-min N           Min delay between queries in ms (default: 4000)
 *   --delay-max N           Max delay between queries in ms (default: 8000)
 *   --max-scrolls N         Max scrolls to find more images (default: 8)
 *   --pause-every N         Pause every N queries for 15–30s (default: 5)
 */

import type { Page } from "playwright";
import { GOOGLE_IMAGE_EVAL_QUERIES, assertQueries } from "./queries.js";
import { createBrowserContext, getOrCreatePage, buildSearchUrl, randomDelay } from "./browser.js";
import { extractLabels } from "./extractLabels.js";
import { extractTop10 } from "./extractResults.js";
import { takeScreenshots, takeDebugScreenshot } from "./screenshots.js";
import {
  initLog,
  log,
  initObservations,
  updateQueryObservation,
  initProgressCsv,
  updateProgressCsv,
  appendError,
  savePerQueryJson,
} from "./storage.js";
import { detectCaptchaOrBlock, waitForUserToClearCaptcha } from "./captcha.js";
import type { QueryObservation, ErrorStage } from "./types.js";

// ── Validate query constants immediately ──────────────────────────────────────
assertQueries();

// ── CLI args ──────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);

function getArg(name: string): string | true | null {
  for (let i = 0; i < args.length; i++) {
    if (args[i] === `--${name}`) {
      const next = args[i + 1];
      if (next && !next.startsWith("--")) return next;
      return true;
    }
    if (args[i].startsWith(`--${name}=`)) {
      return args[i].slice(`--${name}=`.length);
    }
  }
  return null;
}

function getArgNum(name: string, defaultVal: number): number {
  const v = getArg(name);
  if (v && v !== true) return parseInt(v as string, 10);
  return defaultVal;
}

const DRY_RUN = args.includes("--dry-run");
const FORCE = args.includes("--force");
const HEADLESS = args.includes("--headless");
const VALIDATE_ONLY = args.includes("--validate-only");

const START_ID = getArgNum("start", 1);
const END_ID = getArgNum("end", 58);
const QUERY_ID_ARG = getArg("query-id");
const QUERY_TEXT_ARG = getArg("query");

const DELAY_MIN = getArgNum("delay-min", 4000);
const DELAY_MAX = getArgNum("delay-max", 8000);
const PAUSE_EVERY = getArgNum("pause-every", 5);

// ── Dry run ───────────────────────────────────────────────────────────────────

if (DRY_RUN) {
  console.log("\nDry run — 58 queries:\n");
  for (const q of GOOGLE_IMAGE_EVAL_QUERIES) {
    console.log(`${q.query_id}. ${q.query}`);
  }
  console.log(`\nTotal: ${GOOGLE_IMAGE_EVAL_QUERIES.length} queries`);
  console.log(`First: ${GOOGLE_IMAGE_EVAL_QUERIES[0].query}`);
  console.log(`Last: ${GOOGLE_IMAGE_EVAL_QUERIES[57].query}`);
  const hasMaps = GOOGLE_IMAGE_EVAL_QUERIES.some((q) => q.query.toLowerCase() === "maps");
  const hasCat = GOOGLE_IMAGE_EVAL_QUERIES.some((q) => q.query.toLowerCase() === "cat");
  console.log(`Contains maps: ${hasMaps}`);
  console.log(`Contains cat: ${hasCat} (must be false)`);
  console.log(`Query 35: "${GOOGLE_IMAGE_EVAL_QUERIES[34].query}"`);
  console.log(`Query 48: "${GOOGLE_IMAGE_EVAL_QUERIES[47].query}"`);
  console.log(`Query 49: "${GOOGLE_IMAGE_EVAL_QUERIES[48].query}"`);
  process.exit(0);
}

// ── Validate-only mode ────────────────────────────────────────────────────────

if (VALIDATE_ONLY) {
  console.log("Run: npm run validate:google-images");
  process.exit(0);
}

// ── Select queries to process ─────────────────────────────────────────────────

let queriesToRun = [...GOOGLE_IMAGE_EVAL_QUERIES];

if (QUERY_ID_ARG && QUERY_ID_ARG !== true) {
  const id = parseInt(QUERY_ID_ARG as string, 10);
  queriesToRun = queriesToRun.filter((q) => q.query_id === id);
  if (queriesToRun.length === 0) {
    console.error(`No query found with ID ${id}`);
    process.exit(1);
  }
} else if (QUERY_TEXT_ARG && QUERY_TEXT_ARG !== true) {
  const text = QUERY_TEXT_ARG as string;
  queriesToRun = queriesToRun.filter((q) => q.query === text);
  if (queriesToRun.length === 0) {
    console.error(`No query found with text "${text}"`);
    process.exit(1);
  }
} else {
  queriesToRun = queriesToRun.filter(
    (q) => q.query_id >= START_ID && q.query_id <= END_ID,
  );
}

// ── Init storage ──────────────────────────────────────────────────────────────

initLog();
log("INFO", `Starting collector (58-query set) — ${queriesToRun.length} queries to process`);
log("INFO", `Delay: ${DELAY_MIN}–${DELAY_MAX}ms, Pause every: ${PAUSE_EVERY}`);

const obs = initObservations();
initProgressCsv(obs);

// ── Browser ───────────────────────────────────────────────────────────────────

const context = await createBrowserContext(HEADLESS);
const page = await getOrCreatePage(context);

// Handle new tabs opened by clicks (close them, log URL)
context.on("page", async (newPage: Page) => {
  await newPage.waitForLoadState("domcontentloaded");
  log("INFO", `New tab opened: ${newPage.url()}`);
  await newPage.close();
});

// Graceful shutdown
process.on("SIGINT", async () => {
  log("INFO", "Interrupted — saving progress and closing browser");
  await context.close();
  process.exit(0);
});

// ── Per-query processing ──────────────────────────────────────────────────────

let completedCount = 0;

for (const queryItem of queriesToRun) {
  const existing = obs.queries.find((q) => q.query_id === queryItem.query_id);
  if (!existing) {
    log("WARN", `Query ${queryItem.query_id} not found in observations — skipping`);
    continue;
  }

  // Skip completed unless --force
  if (existing.status === "complete" && !FORCE) {
    log("INFO", `Query ${queryItem.query_id} already complete — skipping`);
    continue;
  }

  log("INFO", `Processing query ${queryItem.query_id}: "${queryItem.query}"`);

  const observation: QueryObservation = {
    ...existing,
    status: "running",
    attempts: existing.attempts + 1,
  };
  updateQueryObservation(obs, observation);

  const searchUrl = buildSearchUrl(queryItem.query);
  observation.search_url = searchUrl;

  let captchaEncountered = false;
  let captchaCleared = false;

  try {
    // Navigate
    await page.goto(searchUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(2000);

    // Check for consent/CAPTCHA
    const blocked = await detectCaptchaOrBlock(page);
    if (blocked) {
      captchaEncountered = true;
      const debugPath = await takeDebugScreenshot(page, queryItem.query_id, "captcha");
      appendError({
        query_id: queryItem.query_id,
        query: queryItem.query,
        stage: "captcha",
        message: "Google verification detected",
        stack: "",
        timestamp: new Date().toISOString(),
        screenshot: debugPath,
      });

      captchaCleared = await waitForUserToClearCaptcha(page, queryItem.query_id);

      if (!captchaCleared) {
        observation.status = "captcha";
        observation.error = "Google verification not completed";
        observation.captured_at = new Date().toISOString();
        updateQueryObservation(obs, observation);
        updateProgressCsv(obs);
        log("WARN", `Query ${queryItem.query_id} blocked by captcha — skipping`);
        continue;
      }

      // Re-navigate after captcha clearance
      await page.goto(searchUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
      await page.waitForTimeout(2000);
    }

    // Wait for images to load (2026 layout: .ivg-i tiles; fallback: div[data-ri])
    try {
      await page.waitForSelector(".ivg-i, div[data-ri]", { timeout: 8000 });
    } catch {
      log("WARN", `Query ${queryItem.query_id}: No image grid found after load`);
    }

    // Extract labels
    let labels: string[] = [];
    try {
      labels = await extractLabels(page);
      if (labels.length === 0) {
        log("WARN", `Query ${queryItem.query_id}: No labels found`);
      }
    } catch (err) {
      log("WARN", `Query ${queryItem.query_id} label extraction failed: ${(err as Error).message}`);
      appendError({
        query_id: queryItem.query_id,
        query: queryItem.query,
        stage: "extract_labels" as ErrorStage,
        message: (err as Error).message,
        stack: (err as Error).stack ?? "",
        timestamp: new Date().toISOString(),
        screenshot: "",
      });
    }

    // Extract top 10
    let top10: QueryObservation["top10"] = [];
    try {
      top10 = await extractTop10(page, (rank, note) => {
        log("WARN", `Query ${queryItem.query_id} rank ${rank}: ${note}`);
      });
    } catch (err) {
      log("ERROR", `Query ${queryItem.query_id} top10 extraction failed: ${(err as Error).message}`);
      appendError({
        query_id: queryItem.query_id,
        query: queryItem.query,
        stage: "extract_top10" as ErrorStage,
        message: (err as Error).message,
        stack: (err as Error).stack ?? "",
        timestamp: new Date().toISOString(),
        screenshot: "",
      });
    }

    // Take screenshots
    let screenshots: string[] = [];
    try {
      // Scroll back to top before screenshots
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(500);
      screenshots = await takeScreenshots(page, queryItem.query_id, queryItem.query);
    } catch (err) {
      log("ERROR", `Query ${queryItem.query_id} screenshot failed: ${(err as Error).message}`);
      appendError({
        query_id: queryItem.query_id,
        query: queryItem.query,
        stage: "take_screenshot" as ErrorStage,
        message: (err as Error).message,
        stack: (err as Error).stack ?? "",
        timestamp: new Date().toISOString(),
        screenshot: "",
      });
    }

    // Determine status
    const isComplete = top10.length === 10 && screenshots.length >= 2;
    const status = isComplete ? "complete" : "partial";

    // Check if Google auto-corrected query
    let queryNotes = "";
    try {
      const correctedEl = await page.$('[data-term]');
      if (correctedEl) {
        const correctedText = await correctedEl.getAttribute("data-term");
        if (correctedText && correctedText !== queryItem.query) {
          queryNotes = `Google corrected to: "${correctedText}"`;
          log("WARN", `Query ${queryItem.query_id}: ${queryNotes}`);
        }
      }
    } catch {
      // ignore
    }

    observation.labels = labels;
    observation.top10 = top10;
    observation.screenshots = screenshots;
    observation.status = status;
    observation.captured_at = new Date().toISOString();
    observation.query_notes = queryNotes;
    observation.error = null;

    log(
      "INFO",
      `Query ${queryItem.query_id} ${status}: labels=${labels.length} top10=${top10.length} screenshots=${screenshots.length}`,
    );
  } catch (err) {
    const debugPath = await takeDebugScreenshot(
      page,
      queryItem.query_id,
      "error",
    ).catch(() => "");

    log("ERROR", `Query ${queryItem.query_id} failed: ${(err as Error).message}`);
    appendError({
      query_id: queryItem.query_id,
      query: queryItem.query,
      stage: "open_page" as ErrorStage,
      message: (err as Error).message,
      stack: (err as Error).stack ?? "",
      timestamp: new Date().toISOString(),
      screenshot: debugPath,
    });

    observation.status = "failed";
    observation.error = (err as Error).message;
    observation.captured_at = new Date().toISOString();
  }

  updateQueryObservation(obs, observation);
  updateProgressCsv(obs);
  savePerQueryJson(observation);

  completedCount++;

  // Pause every N queries
  if (completedCount % PAUSE_EVERY === 0 && completedCount < queriesToRun.length) {
    const pauseMs = Math.floor(Math.random() * 15000) + 15000; // 15–30s
    log("INFO", `Pausing ${(pauseMs / 1000).toFixed(0)}s after ${completedCount} queries`);
    await new Promise((resolve) => setTimeout(resolve, pauseMs));
  } else if (completedCount < queriesToRun.length) {
    await randomDelay(DELAY_MIN, DELAY_MAX);
  }
}

// ── Finish ────────────────────────────────────────────────────────────────────

await context.close();

const completeCount = obs.queries.filter((q) => q.status === "complete").length;
const partialCount = obs.queries.filter((q) => q.status === "partial").length;
const failedCount = obs.queries.filter((q) => q.status === "failed").length;
const pendingCount = obs.queries.filter((q) => q.status === "pending").length;

log("INFO", `Run complete — complete=${completeCount} partial=${partialCount} failed=${failedCount} pending=${pendingCount}`);
log("INFO", "Run validation with: npm run validate:google-images");
