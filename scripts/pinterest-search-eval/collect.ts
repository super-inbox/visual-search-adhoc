#!/usr/bin/env node
/**
 * Pinterest Search batch collector — fixed 58 query eval set.
 *
 * Usage:
 *   npx tsx scripts/pinterest-search-eval/collect.ts [options]
 *
 * Options:
 *   --dry-run               Print queries only, do not start browser
 *   --start N               First query_id to process
 *   --end N                 Last query_id to process (inclusive)
 *   --query-id N            Process a single query by ID
 *   --force                 Re-run already-collected queries
 *   --headless              Use headless Chromium (default: headful)
 *   --delay-min N           Min delay between queries in ms (default: 3000)
 *   --delay-max N           Max delay between queries in ms (default: 6000)
 *   --pause-every N         Pause every N queries for 20–35s (default: 8)
 */

import type { Page } from "playwright";
import { PINTEREST_SEARCH_EVAL_QUERIES, assertQueries } from "./queries.js";
import {
  createBrowserContext,
  getOrCreatePage,
  buildPinterestSearchUrl,
  randomDelay,
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
  appendError,
  savePerQueryJson,
  saveObservationsCsv,
} from "./storage.js";
import {
  detectPageState,
  handleCookieConsent,
  tryDismissLoginModal,
  waitForUserToHandleBlock,
} from "./pinterestConsent.js";
import type { PinterestQueryObservation } from "./types.js";

// Validate query constants immediately
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
    if (args[i].startsWith(`--${name}=`)) return args[i].slice(`--${name}=`.length);
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

const DELAY_MIN = getArgNum("delay-min", 3000);
const DELAY_MAX = getArgNum("delay-max", 6000);
const PAUSE_EVERY = getArgNum("pause-every", 8);

// ── Dry run ───────────────────────────────────────────────────────────────────

if (DRY_RUN) {
  console.log("\nDry run — 58 queries:\n");
  for (const q of PINTEREST_SEARCH_EVAL_QUERIES) {
    console.log(`${q.query_id}. ${q.query}`);
  }
  console.log(`\nTotal: ${PINTEREST_SEARCH_EVAL_QUERIES.length} queries`);
  console.log(`First: ${PINTEREST_SEARCH_EVAL_QUERIES[0].query}`);
  console.log(`Last: ${PINTEREST_SEARCH_EVAL_QUERIES[57].query}`);
  const hasMaps = PINTEREST_SEARCH_EVAL_QUERIES.some((q) => q.query === "maps");
  const hasCat = PINTEREST_SEARCH_EVAL_QUERIES.some((q) => q.query.toLowerCase() === "cat");
  console.log(`Contains maps: ${hasMaps}`);
  console.log(`Contains cat: ${hasCat} (must be false)`);
  console.log(`Query 35: "${PINTEREST_SEARCH_EVAL_QUERIES[34].query}"`);
  console.log(`Query 48: "${PINTEREST_SEARCH_EVAL_QUERIES[47].query}"`);
  console.log(`Query 49: "${PINTEREST_SEARCH_EVAL_QUERIES[48].query}"`);
  process.exit(0);
}

// ── Select queries to process ─────────────────────────────────────────────────

let queriesToRun = [...PINTEREST_SEARCH_EVAL_QUERIES];

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
log(
  "INFO",
  `Starting Pinterest Search collector (58-query set) — ${queriesToRun.length} queries to process`,
);
log("INFO", `Delay: ${DELAY_MIN}–${DELAY_MAX}ms, Pause every: ${PAUSE_EVERY}`);

const obs = initObservations();
initProgressCsv(obs);

// ── Browser ───────────────────────────────────────────────────────────────────

const context = await createBrowserContext(HEADLESS);
const page = await getOrCreatePage(context);

context.on("page", async (newPage: Page) => {
  await newPage.waitForLoadState("domcontentloaded").catch(() => {});
  log("INFO", `New tab opened: ${newPage.url()} — closing`);
  await newPage.close().catch(() => {});
});

process.on("SIGINT", async () => {
  log("INFO", "Interrupted — saving progress and closing browser");
  saveObservationsCsv(obs);
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

  if ((existing.status === "ok" || existing.status === "ok_empty") && !FORCE) {
    log("INFO", `Query ${queryItem.query_id} already ${existing.status} — skipping (--force to rerun)`);
    continue;
  }

  log("INFO", `Processing query ${queryItem.query_id}: "${queryItem.query}"`);

  const observation: PinterestQueryObservation = {
    ...existing,
    status: "running",
    attempts: existing.attempts + 1,
  };
  updateQueryObservation(obs, observation);

  const searchUrl = buildPinterestSearchUrl(queryItem.query);
  observation.pinterestUrl = searchUrl;

  try {
    // Navigate to Pinterest search
    await page.goto(searchUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(2500);

    observation.finalUrl = page.url();

    // ── Handle page state ─────────────────────────────────────────────────────
    let pageState = await detectPageState(page);

    if (pageState === "cookie_consent") {
      log("INFO", `Query ${queryItem.query_id}: cookie consent — auto-accepting`);
      await handleCookieConsent(page);
      await page.waitForTimeout(1500);
      observation.finalUrl = page.url();
      pageState = await detectPageState(page);
    }

    if (pageState === "login_wall") {
      log("INFO", `Query ${queryItem.query_id}: login wall detected — attempting to dismiss`);
      const dismissed = await tryDismissLoginModal(page);
      if (dismissed) {
        log("INFO", `Query ${queryItem.query_id}: modal dismissed`);
        await page.waitForTimeout(1000);
        pageState = await detectPageState(page);
      }
    }

    if (pageState === "login_wall") {
      // Check if pin results are visible behind the modal — Pinterest often shows
      // results in the background even when the login modal is present.
      const pinsVisible = await page.evaluate(() => {
        const pins = document.querySelectorAll('a[href*="/pin/"]');
        // Count only actual pin-ID links (not profile/board links)
        let count = 0;
        pins.forEach((el) => {
          if (/\/pin\/\d+/.test((el as HTMLAnchorElement).href)) count++;
        });
        return count;
      });

      if (pinsVisible >= 5) {
        // Results are visible behind the modal — collect them and note the modal
        log(
          "INFO",
          `Query ${queryItem.query_id}: login modal present but ${pinsVisible} pins visible — collecting with note`,
        );
        observation.notes = "login modal present but results visible behind it";
        pageState = "ok" as typeof pageState;
      } else {
        // Results truly blocked — ask user
        const debugPath = await takeDebugScreenshot(page, queryItem.query_id, "login-wall").catch(() => "");
        appendError({
          query_id: queryItem.query_id,
          query: queryItem.query,
          stage: "login_wall",
          message: "Pinterest login wall — results not visible",
          stack: "",
          timestamp: new Date().toISOString(),
          screenshot: debugPath,
        });

        const screenshots = await takeScreenshots(page, queryItem.query_id, queryItem.query).catch(
          () => ({ page1: debugPath, page2: "" }),
        );
        observation.screenshots = screenshots;

        const cleared = await waitForUserToHandleBlock(
          page,
          queryItem.query_id,
          "login wall — dismiss manually or log in",
        );
        if (!cleared) {
          observation.status = "login_required";
          observation.error = "Pinterest login wall not cleared";
          observation.capturedAt = new Date().toISOString();
          observation.notes = "login wall blocked results";
          updateQueryObservation(obs, observation);
          updateProgressCsv(obs);
          savePerQueryJson(observation);
          completedCount++;
          log("WARN", `Query ${queryItem.query_id} login_required — skipping`);
          continue;
        }

        // User cleared — re-check state
        await page.waitForTimeout(1000);
        observation.finalUrl = page.url();
        pageState = await detectPageState(page);
      }
    }

    if (pageState === "captcha") {
      const debugPath = await takeDebugScreenshot(page, queryItem.query_id, "captcha").catch(() => "");
      appendError({
        query_id: queryItem.query_id,
        query: queryItem.query,
        stage: "captcha",
        message: "CAPTCHA / bot block detected",
        stack: "",
        timestamp: new Date().toISOString(),
        screenshot: debugPath,
      });

      const cleared = await waitForUserToHandleBlock(
        page,
        queryItem.query_id,
        "CAPTCHA detected",
      );
      if (!cleared) {
        observation.status = "captcha";
        observation.error = "CAPTCHA not cleared";
        observation.capturedAt = new Date().toISOString();
        updateQueryObservation(obs, observation);
        updateProgressCsv(obs);
        savePerQueryJson(observation);
        completedCount++;
        log("WARN", `Query ${queryItem.query_id} captcha — skipping`);
        continue;
      }

      await page.waitForTimeout(1000);
      observation.finalUrl = page.url();
    }

    // ── Wait for pin grid to load ─────────────────────────────────────────────
    let hasResults = false;
    try {
      await page.waitForSelector(
        '[data-test-id="pin"], a[href*="/pin/"], [data-test-id="pinWrapper"]',
        { timeout: 12000 },
      );
      hasResults = true;
    } catch {
      log("WARN", `Query ${queryItem.query_id}: no pin grid appeared after 12s`);
    }

    // Extra wait for lazy images
    await page.waitForTimeout(2000);

    // ── Extract labels/chips ──────────────────────────────────────────────────
    let labels: PinterestQueryObservation["labels"] = [];
    try {
      labels = await extractLabels(page);
      if (labels.length === 0) {
        log("WARN", `Query ${queryItem.query_id}: no labels found`);
      }
    } catch (err) {
      log("WARN", `Query ${queryItem.query_id} label extraction error: ${(err as Error).message}`);
      appendError({
        query_id: queryItem.query_id,
        query: queryItem.query,
        stage: "extract_labels",
        message: (err as Error).message,
        stack: (err as Error).stack ?? "",
        timestamp: new Date().toISOString(),
        screenshot: "",
      });
    }

    // ── Extract top-10 pins ───────────────────────────────────────────────────
    let topResults: PinterestQueryObservation["topResults"] = [];
    try {
      topResults = await extractTop10(page, (rank, note) => {
        log("WARN", `Query ${queryItem.query_id} rank ${rank}: ${note}`);
      });
      if (topResults.length === 0 && hasResults) {
        log("WARN", `Query ${queryItem.query_id}: extractTop10 returned 0 despite hasResults=true`);
      }
    } catch (err) {
      log("ERROR", `Query ${queryItem.query_id} top10 extraction failed: ${(err as Error).message}`);
      appendError({
        query_id: queryItem.query_id,
        query: queryItem.query,
        stage: "extract_top10",
        message: (err as Error).message,
        stack: (err as Error).stack ?? "",
        timestamp: new Date().toISOString(),
        screenshot: "",
      });
    }

    // ── Screenshots ───────────────────────────────────────────────────────────
    let screenshots: PinterestQueryObservation["screenshots"] = { page1: "", page2: "" };
    try {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(400);
      screenshots = await takeScreenshots(page, queryItem.query_id, queryItem.query);
    } catch (err) {
      log("ERROR", `Query ${queryItem.query_id} screenshot failed: ${(err as Error).message}`);
      appendError({
        query_id: queryItem.query_id,
        query: queryItem.query,
        stage: "take_screenshot",
        message: (err as Error).message,
        stack: (err as Error).stack ?? "",
        timestamp: new Date().toISOString(),
        screenshot: "",
      });
    }

    // ── Determine status ──────────────────────────────────────────────────────
    let status: PinterestQueryObservation["status"];
    // Preserve any notes set during earlier stages (e.g. login modal note)
    const priorNotes = observation.notes || "";
    let statusNotes = "";

    if (!hasResults && topResults.length === 0) {
      status = "ok_empty";
      statusNotes = "no pin results found on page";
    } else if (topResults.length >= 5 && screenshots.page1) {
      status = "ok";
    } else if (topResults.length > 0 || screenshots.page1) {
      status = "partial";
      statusNotes = `only ${topResults.length} results extracted`;
    } else {
      status = "ok_empty";
      statusNotes = "empty result set";
    }

    const combinedNotes = [priorNotes, statusNotes].filter(Boolean).join("; ");

    observation.labels = labels;
    observation.topResults = topResults;
    observation.screenshots = screenshots;
    observation.status = status;
    observation.capturedAt = new Date().toISOString();
    observation.error = null;
    observation.notes = combinedNotes;

    log(
      "INFO",
      `Query ${queryItem.query_id} ${status}: labels=${labels.length} topResults=${topResults.length} screenshots=${screenshots.page1 ? 2 : 0}`,
    );
  } catch (err) {
    const debugPath = await takeDebugScreenshot(page, queryItem.query_id, "error").catch(() => "");
    log("ERROR", `Query ${queryItem.query_id} failed: ${(err as Error).message}`);
    appendError({
      query_id: queryItem.query_id,
      query: queryItem.query,
      stage: "open_page",
      message: (err as Error).message,
      stack: (err as Error).stack ?? "",
      timestamp: new Date().toISOString(),
      screenshot: debugPath,
    });
    observation.status = "error";
    observation.error = (err as Error).message;
    observation.capturedAt = new Date().toISOString();
  }

  updateQueryObservation(obs, observation);
  updateProgressCsv(obs);
  savePerQueryJson(observation);
  completedCount++;

  // Pause every N queries
  if (completedCount % PAUSE_EVERY === 0 && completedCount < queriesToRun.length) {
    const pauseMs = Math.floor(Math.random() * 15000) + 20000; // 20–35s
    log("INFO", `Pausing ${(pauseMs / 1000).toFixed(0)}s after ${completedCount} queries`);
    await new Promise((resolve) => setTimeout(resolve, pauseMs));
  } else if (completedCount < queriesToRun.length) {
    await randomDelay(DELAY_MIN, DELAY_MAX);
  }
}

// ── Finish ────────────────────────────────────────────────────────────────────

await context.close();
saveObservationsCsv(obs);

const okCount = obs.queries.filter((q) => q.status === "ok").length;
const emptyCount = obs.queries.filter((q) => q.status === "ok_empty").length;
const blockedCount = obs.queries.filter((q) => q.status === "blocked").length;
const loginCount = obs.queries.filter((q) => q.status === "login_required").length;
const captchaCount = obs.queries.filter((q) => q.status === "captcha").length;
const errorCount = obs.queries.filter((q) => q.status === "error").length;
const partialCount = obs.queries.filter((q) => q.status === "partial").length;
const pendingCount = obs.queries.filter((q) => q.status === "pending").length;

log(
  "INFO",
  `Run complete — ok=${okCount} ok_empty=${emptyCount} blocked=${blockedCount} login_required=${loginCount} captcha=${captchaCount} error=${errorCount} partial=${partialCount} pending=${pendingCount}`,
);
log("INFO", "Run validation with: npm run validate:pinterest-search");
