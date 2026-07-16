#!/usr/bin/env node
/**
 * EASY QUERY V2 PRODUCTION BASELINE collector.
 *
 * Adapted from ../../7.15/easy-query-production-baseline-v1/scripts/collect_easy_query_baseline.mjs
 * (the 2026-07-15 production baseline collector for the original 328-query bank),
 * which already proved out safe, working, read-only, production-page collection.
 * This copy changes ONLY the input file path and run-id prefix:
 *   - reads the 326-row Easy Query Benchmark v2 CSV (query_input/easy_query_v2_input_with_ids.csv)
 *     instead of the original 328-row easy_queries_cleaned_300_plus_2026-07-14.csv
 *   - RUN_ID prefix changed to "easyqv2-prod-baseline-" to distinguish from the
 *     original 7/15 run
 * All collection/extraction/checkpoint/retry/screenshot logic is UNCHANGED from
 * the original script (byte-identical except for the two constants above and
 * this header comment), so results are directly comparable to the 7/15 baseline
 * methodology.
 *
 * It does NOT touch curify-frontend production code, does NOT call any local
 * search engine code, and does NOT modify the search algorithm in any way.
 * It only drives a real browser against the live https://www.curify-ai.com
 * production website via GET page navigation, exactly as a human user would.
 *
 * Usage:
 *   node collect_easy_query_v2_baseline.mjs --smoke <idx1,idx2,idx3,idx4,idx5>
 *   node collect_easy_query_v2_baseline.mjs --full
 *   node collect_easy_query_v2_baseline.mjs --full --headed
 */

import { chromium } from "playwright";
import { parse } from "csv-parse/sync";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RUN_ROOT = path.resolve(__dirname, "..");

const QUERY_CSV = path.join(RUN_ROOT, "query_input", "easy_query_v2_input_with_ids.csv");
const RAW_DIR = path.join(RUN_ROOT, "raw");
const SCREENSHOT_DIR = path.join(RUN_ROOT, "screenshots");
const CHECKPOINT_DIR = path.join(RUN_ROOT, "checkpoints");
const LOG_DIR = path.join(RUN_ROOT, "logs");
const SMOKE_DIR = path.join(RUN_ROOT, "raw", "smoke_test");
const SMOKE_SCREENSHOT_DIR = path.join(RUN_ROOT, "screenshots", "smoke_test");

const BASE_URL = "https://www.curify-ai.com";
const NAV_TIMEOUT_MS = 45000; // 30-60s range per spec
const RESULT_WAIT_TIMEOUT_MS = 20000;
const DELAY_MIN_MS = 1200;
const DELAY_MAX_MS = 2200;
const MAX_TOP_RESULTS = 5;
const MAX_CARDS_COUNTED = 200; // generous cap so result_count_observed isn't truncated by our own extraction
const LOW_RESULT_THRESHOLD = 5; // matches production app/[locale]/(public)/search/page.tsx:47 LOW_RESULT_THRESHOLD
const MAX_ATTEMPTS = 2; // retries only for network/timeout errors
const CHECKPOINT_EVERY = 10;

const RUN_ID = `easyqv2-prod-baseline-${new Date().toISOString().replace(/[:.]/g, "-")}`;

const args = process.argv.slice(2);
const MODE = args.includes("--smoke") ? "smoke" : "full";
const HEADLESS = !args.includes("--headed");
const smokeArgIdx = args.indexOf("--smoke");
const smokeIndices =
  smokeArgIdx !== -1 && args[smokeArgIdx + 1] && /^[0-9,]+$/.test(args[smokeArgIdx + 1])
    ? args[smokeArgIdx + 1].split(",").map(Number)
    : null;

function log(msg) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}`;
  console.log(line);
  try {
    fs.appendFileSync(
      path.join(LOG_DIR, MODE === "smoke" ? "smoke_test_run_log.md" : "run_log.md"),
      line + "\n",
      "utf-8",
    );
  } catch {
    /* logging must never crash the collector */
  }
}

function randomDelay(minMs, maxMs) {
  const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function slugify(str, maxLen = 60) {
  return str
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, maxLen)
    .replace(/_+$/g, "") || "query";
}

// buildSearchUrl uses the ORIGINAL, UNMODIFIED query string exactly as read
// from the CSV. encodeURIComponent is a transport-encoding step only (does
// not change case, spacing, punctuation, or language of the query itself).
function buildSearchUrl(query) {
  return `${BASE_URL}/search?q=${encodeURIComponent(query)}`;
}

function loadQueries() {
  const raw = fs.readFileSync(QUERY_CSV, "utf-8");
  const records = parse(raw, { columns: true, skip_empty_lines: false });
  return records;
}

// ── Login wall detection (unchanged from original) ─────────────────────────

const LOGIN_URL_SIGNALS = ["/login", "/signup", "/sign-up", "/sign-in", "/auth/"];
const LOGIN_TEXT_SIGNALS = [
  "sign in to continue",
  "log in to continue",
  "create an account",
  "sign up to continue",
  "please log in",
  "please sign in",
];

async function detectLoginWall(page) {
  const url = page.url();
  if (LOGIN_URL_SIGNALS.some((s) => url.includes(s))) return true;
  try {
    const bodyText = await page.evaluate(() => document.body?.innerText?.toLowerCase().slice(0, 3000) ?? "");
    if (LOGIN_TEXT_SIGNALS.some((s) => bodyText.includes(s))) return true;
    const hasAuthModal = await page.evaluate(() => {
      const modalSelectors = ['[role="dialog"]', "div[class*='modal']", "div[class*='Modal']"];
      for (const sel of modalSelectors) {
        const els = document.querySelectorAll(sel);
        for (const el of els) {
          const t = el.textContent?.toLowerCase() ?? "";
          if (
            (t.includes("sign in") || t.includes("log in") || t.includes("sign up")) &&
            el.querySelector('input[type="email"], input[type="password"]')
          ) {
            return true;
          }
        }
      }
      return false;
    });
    if (hasAuthModal) return true;
  } catch {
    // ignore
  }
  return false;
}

// ── Result + broaden/rewrite-signal extraction (unchanged from original) ───

async function extractResults(page) {
  return page.evaluate(
    ({ MAX, MAX_COUNT }) => {
      function textOf(el) {
        return el?.textContent?.trim() ?? "";
      }
      function findSectionByHeading(names) {
        const sections = document.querySelectorAll("section");
        for (const section of sections) {
          const h2 = section.querySelector("h2");
          const heading = textOf(h2).toLowerCase();
          if (names.includes(heading)) return section;
        }
        return null;
      }

      const cards = [];
      const seen = new Set();
      function pushCard(href, title, tag, sourceType, imageUrl) {
        const key = href || title;
        if (!key || seen.has(key)) return;
        if (cards.length >= MAX_COUNT) return;
        seen.add(key);
        cards.push({ title, href, tag, sourceType, imageUrl });
      }

      const examplesSection = findSectionByHeading(["examples"]);
      if (examplesSection) {
        const cardEls = examplesSection.querySelectorAll("div.group, div[class*='rounded-3xl']");
        for (const card of cardEls) {
          const link =
            card.querySelector('a[href*="/nano-template/"][href*="/example/"]') ??
            card.querySelector('a[href*="/carousel/template-example/"]');
          if (!link) continue;
          const img = card.querySelector("img");
          const title = img?.alt?.trim() || textOf(link);
          const captionEl = card.querySelector("div.px-3.pt-2, p.text-xs, div.text-xs");
          const tag = textOf(captionEl);
          pushCard(link.href, title, tag, "inspiration", img?.src || img?.currentSrc || "");
        }
      }

      const templatesSection = findSectionByHeading(["templates"]);
      if (templatesSection) {
        const links = templatesSection.querySelectorAll('a[href*="/nano-template/"]');
        for (const link of links) {
          if (link.href.includes("/example/") || link.href.includes("/carousel/")) continue;
          const cardEl = link.closest("div.group") ?? link.closest("article") ?? link.closest("div");
          const img = cardEl?.querySelector("img");
          const nameEl = cardEl?.querySelector("h3, h4, p.font-semibold, div.font-semibold");
          const title = img?.alt?.trim() || textOf(nameEl) || textOf(link);
          pushCard(link.href.split("#")[0], title, textOf(nameEl), "template", img?.src || img?.currentSrc || "");
        }
      }

      if (cards.length === 0) {
        const genericLinks = document.querySelectorAll('a[href*="/nano-template/"], a[href*="/template/"]');
        for (const link of genericLinks) {
          const img = link.querySelector("img") ?? link.closest("div")?.querySelector("img");
          const title = img?.alt?.trim() || textOf(link);
          pushCard(link.href, title, "", "unknown", img?.src || img?.currentSrc || "");
        }
      }

      let noResultOrBroadenText = "";
      const candidates = Array.from(document.querySelectorAll("p, h2, h3, div, span")).filter((el) => {
        const t = textOf(el).toLowerCase();
        return (
          t.length > 0 &&
          t.length < 400 &&
          (t.includes("no results") ||
            t.includes("nothing found") ||
            t.includes("couldn't find") ||
            t.includes("no matches") ||
            t.includes("few results for") ||
            t.includes("also showing results for"))
        );
      });
      if (candidates.length > 0) {
        const texts = candidates.map(textOf);
        const withBroadenClause = texts.filter((t) => /also showing results for/i.test(t));
        if (withBroadenClause.length > 0) {
          noResultOrBroadenText = withBroadenClause.sort((a, b) => a.length - b.length)[0];
        } else {
          noResultOrBroadenText = texts.sort((a, b) => a.length - b.length)[0];
        }
      }

      const resultsForHeading = document.querySelector("p.mb-5, p.text-neutral-500");
      const headingText = textOf(resultsForHeading);

      return {
        cards: cards.slice(0, MAX),
        totalCardsCounted: cards.length,
        noResultOrBroadenText,
        headingText,
      };
    },
    { MAX: MAX_TOP_RESULTS, MAX_COUNT: MAX_CARDS_COUNTED },
  );
}

function emptyRecord(runId, index, row) {
  return {
    run_id: runId,
    query_index: index,
    source_row_number: row.source_row ?? null,
    query_id: row.easy_id ?? null,
    original_query: row.query,
    original_query_exact_bytes_or_normalized_reference: Buffer.from(row.query ?? "", "utf-8").toString("hex"),
    category: row.category ?? row.query_type ?? null,
    scenario: row.scenario ?? null,
    language: row.language ?? null,
    test_target: "production",
    production_url: BASE_URL,
    request_url: null,
    request_method: "GET",
    request_timestamp: null,
    response_timestamp: null,
    duration_ms: null,
    HTTP_status: null,
    page_loaded: false,
    search_completed: false,
    result_count_reported: null,
    result_count_observed: null,
    zero_result: false,
    low_result: false,
    low_result_threshold: LOW_RESULT_THRESHOLD,
    query_broadened: false,
    broadened_query: null,
    rewrite_observed: null,
    raw_rewrite_visible: null,
    rewrite_source: null,
    final_search_query_visible: null,
    spelling_correction_visible: null,
    filter_state: null,
    pagination_state: null,
    top_results: [],
    raw_response_path: null,
    screenshot_path: null,
    console_error: null,
    network_error: null,
    timeout: false,
    rate_limited: false,
    captcha: false,
    login_required: false,
    parse_error: false,
    retry_count: 0,
    final_status: "UNKNOWN_ERROR",
    error_code: null,
    error_message: null,
    checkpoint_written: false,
    notes: null,
  };
}

async function collectOne(page, runId, index, row, outDir, screenshotDir) {
  const rec = emptyRecord(runId, index, row);
  const query = row.query ?? "";
  const idxStr = String(index).padStart(3, "0");
  const easyId = row.easy_id || `IDX${idxStr}`;
  const screenshotPath = path.join(screenshotDir, `${idxStr}_${easyId}_${slugify(query)}.png`);

  if (query.trim() === "") {
    rec.final_status = "INPUT_INVALID";
    rec.notes = "Empty query string in authoritative input file at this row — recorded verbatim, not skipped.";
    return rec;
  }

  const searchUrl = buildSearchUrl(query);
  rec.request_url = searchUrl;

  let attempt = 0;
  let lastErr = null;
  while (attempt < MAX_ATTEMPTS) {
    attempt++;
    rec.retry_count = attempt - 1;
    rec.request_timestamp = new Date().toISOString();
    const t0 = Date.now();
    try {
      const response = await page.goto(searchUrl, { waitUntil: "domcontentloaded", timeout: NAV_TIMEOUT_MS });
      rec.HTTP_status = response ? response.status() : null;
      rec.page_loaded = true;
    } catch (err) {
      rec.response_timestamp = new Date().toISOString();
      rec.duration_ms = Date.now() - t0;
      lastErr = err;
      const msg = err && err.message ? err.message : String(err);
      if (/timeout/i.test(msg)) {
        rec.timeout = true;
        rec.error_code = "NAV_TIMEOUT";
      } else {
        rec.network_error = msg;
        rec.error_code = "NAV_ERROR";
      }
      rec.error_message = msg;
      log(`  [${idxStr}] (${easyId}) navigation failed (attempt ${attempt}/${MAX_ATTEMPTS}): ${msg}`);
      if (attempt < MAX_ATTEMPTS) {
        await randomDelay(1500, 3000);
        continue;
      }
      try {
        await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
        rec.screenshot_path = path.relative(RUN_ROOT, screenshotPath);
      } catch {
        /* ignore */
      }
      rec.final_status = rec.timeout ? "TIMEOUT" : "NETWORK_ERROR";
      return rec;
    }

    let timedOutWaiting = false;
    try {
      await Promise.race([
        page.waitForSelector('section h2, div[class*="rounded-3xl"], a[href*="/nano-template/"]', {
          timeout: RESULT_WAIT_TIMEOUT_MS,
        }),
        page.waitForSelector("text=/no results/i", { timeout: RESULT_WAIT_TIMEOUT_MS }),
      ]);
    } catch {
      timedOutWaiting = true;
    }
    await page.waitForTimeout(1500);

    const loginWall = await detectLoginWall(page);
    rec.login_required = loginWall;

    if (timedOutWaiting && !loginWall) {
      const stillLoading = await page
        .evaluate(() => {
          const bodyText = document.body?.innerText ?? "";
          return bodyText.trim().length < 50 || /loading/i.test(bodyText.slice(0, 200));
        })
        .catch(() => true);
      if (stillLoading) {
        rec.response_timestamp = new Date().toISOString();
        rec.duration_ms = Date.now() - t0;
        rec.parse_error = true;
        rec.error_code = "EXTRACT_TIMEOUT";
        rec.error_message = "Result container never appeared and body text stayed effectively empty.";
        try {
          await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
          rec.screenshot_path = path.relative(RUN_ROOT, screenshotPath);
        } catch {
          /* ignore */
        }
        rec.final_status = "PARSE_ERROR";
        return rec;
      }
    }

    try {
      const { cards, totalCardsCounted, noResultOrBroadenText, headingText } = await extractResults(page);
      rec.search_completed = true;
      rec.result_count_observed = totalCardsCounted;
      rec.final_search_query_visible = headingText || null;
      rec.top_results = cards.map((c, i) => ({
        rank: i + 1,
        title: c.title || null,
        url: c.href || null,
        image_url: c.imageUrl || null,
        metadata: c.tag || c.sourceType || null,
      }));

      const broadenMatch = /few results for|also showing results for/i.test(noResultOrBroadenText);
      rec.query_broadened = broadenMatch;
      if (broadenMatch) {
        rec.rewrite_observed = true;
        rec.raw_rewrite_visible = noResultOrBroadenText;
        rec.rewrite_source = "ui_banner";
        const m = noResultOrBroadenText.match(/also showing results for:?\s*(.+)$/i);
        rec.broadened_query = m ? m[1].trim() : noResultOrBroadenText;
      } else {
        rec.rewrite_observed = false;
      }

      if (totalCardsCounted === 0) {
        rec.zero_result = !loginWall;
        rec.low_result = false;
      } else if (totalCardsCounted < LOW_RESULT_THRESHOLD) {
        rec.low_result = true;
        rec.zero_result = false;
      }

      rec.response_timestamp = new Date().toISOString();
      rec.duration_ms = Date.now() - t0;

      if (loginWall) {
        rec.final_status = "SUCCESS";
        rec.notes = "login_wall detected during collection; result extraction attempted regardless.";
      } else if (rec.zero_result) {
        rec.final_status = "ZERO_RESULT";
      } else if (rec.low_result) {
        rec.final_status = "LOW_RESULT";
      } else {
        rec.final_status = "SUCCESS";
      }
    } catch (err) {
      rec.response_timestamp = new Date().toISOString();
      rec.duration_ms = Date.now() - t0;
      rec.parse_error = true;
      rec.error_message = err && err.message ? err.message : String(err);
      rec.error_code = "EXTRACT_EXCEPTION";
      rec.final_status = "PARSE_ERROR";
    }

    try {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(300);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      rec.screenshot_path = path.relative(RUN_ROOT, screenshotPath);
    } catch (err) {
      log(`  [${idxStr}] (${easyId}) screenshot failed: ${err.message}`);
    }

    return rec;
  }

  rec.final_status = "UNKNOWN_ERROR";
  rec.error_message = lastErr ? String(lastErr) : "exhausted retries with no captured error";
  return rec;
}

function isCompletedSuccessfully(rec) {
  return rec && ["SUCCESS", "ZERO_RESULT", "LOW_RESULT", "INPUT_INVALID"].includes(rec.final_status);
}

async function main() {
  fs.mkdirSync(RAW_DIR, { recursive: true });
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  fs.mkdirSync(CHECKPOINT_DIR, { recursive: true });
  fs.mkdirSync(LOG_DIR, { recursive: true });
  fs.mkdirSync(SMOKE_DIR, { recursive: true });
  fs.mkdirSync(SMOKE_SCREENSHOT_DIR, { recursive: true });

  const allQueries = loadQueries();
  log(`Loaded ${allQueries.length} rows from ${path.relative(RUN_ROOT, QUERY_CSV)}`);

  let indices;
  let outDir;
  let screenshotDir;
  if (MODE === "smoke") {
    indices = smokeIndices && smokeIndices.length > 0 ? smokeIndices : [1, 2, 3, 4, 5];
    outDir = SMOKE_DIR;
    screenshotDir = SMOKE_SCREENSHOT_DIR;
    log(`Mode: smoke — query_index list = [${indices.join(",")}]`);
  } else {
    indices = allQueries.map((_, i) => i + 1);
    outDir = RAW_DIR;
    screenshotDir = SCREENSHOT_DIR;
    log(`Mode: full — will process ${indices.length} queries (headless=${HEADLESS})`);
  }

  const browser = await chromium.launch({ headless: HEADLESS });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: "en-US",
  });
  const page = await context.newPage();

  let doneCount = 0;
  let resumedCount = 0;
  for (const idx of indices) {
    const row = allQueries[idx - 1];
    if (!row) {
      log(`  index ${idx} out of range of input file — skipping (should not happen)`);
      continue;
    }
    const easyId = row.easy_id || `IDX${String(idx).padStart(3, "0")}`;
    const outJson = path.join(outDir, `${String(idx).padStart(3, "0")}_${easyId}.json`);

    if (fs.existsSync(outJson)) {
      try {
        const prior = JSON.parse(fs.readFileSync(outJson, "utf-8"));
        if (isCompletedSuccessfully(prior)) {
          log(`[${idx}/${indices.length}] RESUME: reusing prior completed record for ${easyId} (final_status=${prior.final_status})`);
          resumedCount++;
          doneCount++;
          continue;
        }
      } catch {
        // fall through and re-run
      }
    }

    log(`[${idx}/${indices.length}] "${row.query}" (${easyId})`);
    const rec = await collectOne(page, RUN_ID, idx, row, outDir, screenshotDir);
    rec.checkpoint_written = true;
    fs.writeFileSync(outJson, JSON.stringify(rec, null, 2), "utf-8");
    log(
      `  -> final_status=${rec.final_status} results=${rec.result_count_observed} broadened=${rec.query_broadened} login=${rec.login_required} duration_ms=${rec.duration_ms}`,
    );
    doneCount++;

    if (MODE === "full" && doneCount % CHECKPOINT_EVERY === 0) {
      const checkpointPath = path.join(CHECKPOINT_DIR, `checkpoint_after_${doneCount}.json`);
      fs.writeFileSync(
        checkpointPath,
        JSON.stringify({ run_id: RUN_ID, done_count: doneCount, resumed_count: resumedCount, last_index: idx, timestamp: new Date().toISOString() }, null, 2),
        "utf-8",
      );
      log(`  checkpoint written: ${path.relative(RUN_ROOT, checkpointPath)}`);
    }

    if (idx !== indices[indices.length - 1]) {
      await randomDelay(DELAY_MIN_MS, DELAY_MAX_MS);
    }
  }

  await browser.close();
  log(`Done. processed=${doneCount} resumed_from_checkpoint=${resumedCount} run_id=${RUN_ID}`);
}

main().catch((err) => {
  console.error("FATAL:", err);
  process.exit(1);
});
