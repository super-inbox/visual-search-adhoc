#!/usr/bin/env node
/**
 * Curify Search batch collector — fixed 58-query eval set.
 *
 * Usage:
 *   CURIFY_BASE_URL=http://localhost:3000/en npx tsx scripts/curify-search-eval/collect.ts [options]
 *
 * Options:
 *   --dry-run         Print queries only, do not start browser
 *   --start N         First query_id to process (default: 1)
 *   --end N           Last query_id to process inclusive (default: 58)
 *   --query-id N      Process a single query by ID
 *   --force           Re-run already-collected queries
 *   --headless        Use headless Chromium (default: headful)
 *   --delay-min N     Min delay between queries in ms (default: 1500)
 *   --delay-max N     Max delay between queries in ms (default: 3000)
 */

import { CURIFY_SEARCH_EVAL_QUERIES, assertQueries } from "./queries.js";
import {
  createBrowserContext,
  getOrCreatePage,
  buildSearchUrl,
  randomDelay,
  getCurifyBaseUrl,
  isLocaleRedirect,
} from "./browser.js";
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
  saveObservationsCsv,
  savePerQueryJson,
} from "./storage.js";
import type { CurifyQueryObservation } from "./types.js";

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

const START_ID = getArgNum("start", 1);
const END_ID = getArgNum("end", 58);
const QUERY_ID_ARG = getArg("query-id");

const DELAY_MIN = getArgNum("delay-min", 1500);
const DELAY_MAX = getArgNum("delay-max", 3000);

// ── Dry run ───────────────────────────────────────────────────────────────────

if (DRY_RUN) {
  console.log("\nDry run — 58 Curify search queries:\n");
  for (const q of CURIFY_SEARCH_EVAL_QUERIES) {
    console.log(`${q.query_id}. ${q.query}`);
  }
  console.log(`\nTotal: ${CURIFY_SEARCH_EVAL_QUERIES.length} queries`);
  console.log(`First: ${CURIFY_SEARCH_EVAL_QUERIES[0].query}`);
  console.log(`Last: ${CURIFY_SEARCH_EVAL_QUERIES[57].query}`);
  const hasMaps = CURIFY_SEARCH_EVAL_QUERIES.some((q) => q.query === "maps");
  const hasCat = CURIFY_SEARCH_EVAL_QUERIES.some((q) => q.query.toLowerCase() === "cat");
  console.log(`Contains maps: ${hasMaps}`);
  console.log(`Contains cat: ${hasCat} (must be false)`);
  console.log(`Query 35: "${CURIFY_SEARCH_EVAL_QUERIES[34].query}"`);
  console.log(`Query 48: "${CURIFY_SEARCH_EVAL_QUERIES[47].query}"`);
  console.log(`Query 49: "${CURIFY_SEARCH_EVAL_QUERIES[48].query}"`);
  console.log(`\nCurify base URL: ${getCurifyBaseUrl()}`);
  console.log(`Sample URL: ${buildSearchUrl(CURIFY_SEARCH_EVAL_QUERIES[0].query)}`);
  process.exit(0);
}

// ── Select queries ────────────────────────────────────────────────────────────

let queriesToRun = [...CURIFY_SEARCH_EVAL_QUERIES];

if (QUERY_ID_ARG && QUERY_ID_ARG !== true) {
  const id = parseInt(QUERY_ID_ARG as string, 10);
  queriesToRun = queriesToRun.filter((q) => q.query_id === id);
  if (queriesToRun.length === 0) {
    console.error(`No query found with ID ${id}`);
    process.exit(1);
  }
} else {
  queriesToRun = queriesToRun.filter(
    (q) => q.query_id >= START_ID && q.query_id <= END_ID,
  );
}

// ── Init storage ──────────────────────────────────────────────────────────────

initLog();
log("INFO", `Curify Search collector (58-query set) — ${queriesToRun.length} queries`);
log("INFO", `Base URL: ${getCurifyBaseUrl()}`);

const obs = initObservations();
initProgressCsv(obs);

// ── Browser ───────────────────────────────────────────────────────────────────

const context = await createBrowserContext(HEADLESS);
const page = await getOrCreatePage(context);

// Close unexpected new tabs
context.on("page", async (newPage) => {
  await newPage.waitForLoadState("domcontentloaded").catch(() => null);
  log("INFO", `New tab: ${newPage.url()} — closing`);
  await newPage.close();
});

process.on("SIGINT", async () => {
  log("INFO", "Interrupted — saving progress");
  saveObservationsCsv(obs);
  await context.close();
  process.exit(0);
});

// ── Per-query processing ──────────────────────────────────────────────────────

let completedCount = 0;

for (const queryItem of queriesToRun) {
  const existing = obs.queries.find((q) => q.index === queryItem.query_id);
  if (!existing) {
    log("WARN", `Query ${queryItem.query_id} not found in observations — skipping`);
    continue;
  }

  if ((existing.status === "ok" || existing.status === "ok_empty") && !FORCE) {
    log("INFO", `Query ${queryItem.query_id} already collected — skipping (use --force to re-run)`);
    completedCount++;
    continue;
  }

  log("INFO", `Processing query ${queryItem.query_id}: "${queryItem.query}"`);

  const observation: CurifyQueryObservation = {
    ...existing,
    status: "running",
  };
  updateQueryObservation(obs, observation);

  const searchUrl = buildSearchUrl(queryItem.query);
  observation.curifyUrl = searchUrl;

  try {
    // Navigate
    await page.goto(searchUrl, { waitUntil: "domcontentloaded", timeout: 30000 });

    // Wait for either results or error state
    try {
      await Promise.race([
        page.waitForSelector('section h2, div[class*="rounded-3xl"], a[href*="intent="], a[href*="within="]', { timeout: 10000 }),
        page.waitForSelector('p:has-text("No results"), p:has-text("no results")', { timeout: 10000 }),
      ]);
    } catch {
      // continue anyway — page might still have content
    }

    // Extra wait for images to load
    await page.waitForTimeout(2000);

    // Record final URL (detect meaningful redirects)
    // Next.js strips the default locale prefix (/en → /) — that's a locale redirect, not meaningful.
    // Only flag "redirected" when the page landed on a genuinely different path (e.g. /topics/).
    const finalUrl = page.url();
    observation.finalUrl = finalUrl;

    const isTopicRedirect = finalUrl.includes("/topics/");
    const isLocaleStrip = isLocaleRedirect(searchUrl, finalUrl);
    const isMeaningfulRedirect = finalUrl !== searchUrl && !isLocaleStrip;
    observation.redirected = isMeaningfulRedirect;

    if (isMeaningfulRedirect) {
      if (isTopicRedirect) {
        observation.redirectType = "topic";
        log("INFO", `Query ${queryItem.query_id} → topic redirect: ${finalUrl}`);
      } else {
        observation.redirectType = "other";
        log("INFO", `Query ${queryItem.query_id} → redirect: ${finalUrl}`);
      }
      await page.waitForTimeout(1500);
    }

    // Check for server error
    let pageTitle = "";
    try {
      pageTitle = await page.title();
    } catch {
      // Page may have navigated away; re-read after settling
      await page.waitForLoadState("domcontentloaded").catch(() => null);
      await page.waitForTimeout(1000);
      pageTitle = await page.title().catch(() => "");
      // Update final URL after any post-load navigation
      const newFinalUrl = page.url();
      if (newFinalUrl !== finalUrl) {
        observation.finalUrl = newFinalUrl;
        observation.redirected = isTopicRedirect || !isLocaleRedirect(searchUrl, newFinalUrl);
        if (newFinalUrl.includes("/topics/")) observation.redirectType = "topic";
      }
    }
    const bodyText = await page.evaluate(() => (document.body?.innerText ?? "").slice(0, 500)).catch(() => "");
    if (
      pageTitle.toLowerCase().includes("internal server error") ||
      bodyText.toLowerCase().includes("internal server error")
    ) {
      const debugPath = await takeDebugScreenshot(page, queryItem.query_id, "error").catch(() => "");
      log("ERROR", `Query ${queryItem.query_id}: Server error detected`);
      observation.status = "error";
      observation.error = `Server error: ${pageTitle} — ${bodyText.slice(0, 200)}`;
      observation.capturedAt = new Date().toISOString();
      observation.screenshots = { page1: debugPath, page2: "" };
      updateQueryObservation(obs, observation);
      updateProgressCsv(obs);
      savePerQueryJson(observation);
      completedCount++;
      await randomDelay(DELAY_MIN, DELAY_MAX);
      continue;
    }

    // Extract labels / chips
    let labels: CurifyQueryObservation["labels"] = [];
    try {
      labels = await extractLabels(page);
      if (labels.length === 0) {
        log("WARN", `Query ${queryItem.query_id}: No labels found`);
      }
    } catch (err) {
      log("WARN", `Query ${queryItem.query_id} label extraction failed: ${(err as Error).message}`);
    }

    // Extract top 10 results
    let topResults: CurifyQueryObservation["topResults"] = [];
    try {
      topResults = await extractTop10(page, (rank, note) => {
        log("WARN", `Query ${queryItem.query_id} rank ${rank}: ${note}`);
      });
    } catch (err) {
      log("ERROR", `Query ${queryItem.query_id} top10 extraction failed: ${(err as Error).message}`);
    }

    // Take screenshots
    let screenshots: CurifyQueryObservation["screenshots"] = { page1: "", page2: "" };
    try {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(500);
      screenshots = await takeScreenshots(page, queryItem.query_id, queryItem.query);
    } catch (err) {
      log("ERROR", `Query ${queryItem.query_id} screenshot failed: ${(err as Error).message}`);
    }

    // Determine empty state
    let notes = "";
    if (topResults.length === 0) {
      try {
        const emptyText = await page.evaluate(() => {
          const noResults = document.querySelector('p, h3, div');
          // Look for known empty state text patterns
          const allText = Array.from(document.querySelectorAll("p, h2, h3"))
            .map((el) => el.textContent?.trim() ?? "")
            .filter((t) => t.length > 5 && t.length < 200)
            .join(" | ");
          return allText.slice(0, 300);
        });
        notes = `Empty results. Page text: ${emptyText}`;
      } catch {
        notes = "Empty results (no extraction context)";
      }
    }

    observation.labels = labels;
    observation.topResults = topResults;
    observation.screenshots = screenshots;
    observation.counts = { labels: labels.length, topResults: topResults.length };
    observation.capturedAt = new Date().toISOString();
    observation.notes = notes;
    observation.error = null;
    observation.status = topResults.length === 0 ? "ok_empty" : "ok";

    log(
      "INFO",
      `Query ${queryItem.query_id} ${observation.status}: labels=${labels.length} results=${topResults.length} redirected=${observation.redirected}`,
    );
  } catch (err) {
    const debugPath = await takeDebugScreenshot(page, queryItem.query_id, "error").catch(() => "");
    log("ERROR", `Query ${queryItem.query_id} failed: ${(err as Error).message}`);
    observation.status = "error";
    observation.error = (err as Error).message;
    observation.capturedAt = new Date().toISOString();
    observation.screenshots = { page1: debugPath, page2: "" };
  }

  updateQueryObservation(obs, observation);
  updateProgressCsv(obs);
  savePerQueryJson(observation);
  completedCount++;

  if (completedCount < queriesToRun.length) {
    await randomDelay(DELAY_MIN, DELAY_MAX);
  }
}

// ── Finish ────────────────────────────────────────────────────────────────────

await context.close();
saveObservationsCsv(obs);

const okCount = obs.queries.filter((q) => q.status === "ok").length;
const emptyCount = obs.queries.filter((q) => q.status === "ok_empty").length;
const errorCount = obs.queries.filter((q) => q.status === "error").length;
const pendingCount = obs.queries.filter((q) => q.status === "pending").length;
const redirectCount = obs.queries.filter((q) => q.redirected).length;

log("INFO", `Run complete — ok=${okCount} ok_empty=${emptyCount} error=${errorCount} pending=${pendingCount} redirected=${redirectCount}`);
log("INFO", "Run validation with: npm run validate:curify-search");
