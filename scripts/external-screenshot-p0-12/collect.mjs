#!/usr/bin/env node
/**
 * Ad-hoc Playwright collector for the 12 P0 visual-review cases
 * (docs/daily_report/7.9). NOT part of curify-frontend production code.
 *
 * Reuses the same URL-building / consent-handling approach as
 * scripts/bing-image-eval, scripts/google-image-eval, scripts/canva-search-eval,
 * but targets the small custom 12-query CSV instead of the fixed 58-query
 * eval set, and writes screenshots straight into
 * docs/daily_report/7.9/competitor_screenshots/<slug>/<platform>.png
 * instead of docs/external-signal-pilot/.
 *
 * Never bypasses CAPTCHA, login walls, or bot-protection — if one appears,
 * the query is marked screenshot_pending with a reason and left for a human.
 *
 * Usage:
 *   node collect.mjs --platform=bing
 *   node collect.mjs --platform=google
 *   node collect.mjs --platform=canva
 */

import { chromium } from "playwright";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");

const CSV_PATH = path.join(
  REPO_ROOT,
  "docs/daily_report/7.9/manual_review/external_screenshot_queries_12_2026-07-09.csv",
);
const SCREENSHOTS_ROOT = path.join(REPO_ROOT, "docs/daily_report/7.9/competitor_screenshots");

const args = process.argv.slice(2);
function getArg(name, fallback = null) {
  const pre = `--${name}=`;
  const hit = args.find((a) => a.startsWith(pre));
  return hit ? hit.slice(pre.length) : fallback;
}

const PLATFORM = getArg("platform");
if (!["bing", "google", "canva"].includes(PLATFORM)) {
  console.error('Usage: node collect.mjs --platform=bing|google|canva');
  process.exit(1);
}
const HEADLESS = args.includes("--headless");
const DELAY_MIN_MS = parseInt(getArg("delay-min", "7000"), 10);
const DELAY_MAX_MS = parseInt(getArg("delay-max", "13000"), 10);

// ── tiny quote-aware CSV reader ──────────────────────────────────────────────
// (platforms_to_capture contains embedded commas inside quotes, e.g.
// "bing,google,canva,pinterest" — a naive split(",") misaligns every
// column after it, so this must respect quotes.)
function splitCsvLine(line) {
  const cells = [];
  let cur = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (inQuotes) {
      if (c === '"' && line[i + 1] === '"') {
        cur += '"';
        i++;
      } else if (c === '"') {
        inQuotes = false;
      } else {
        cur += c;
      }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ",") {
      cells.push(cur);
      cur = "";
    } else {
      cur += c;
    }
  }
  cells.push(cur);
  return cells;
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const header = splitCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const cells = splitCsvLine(line);
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
}

let rows = parseCsv(fs.readFileSync(CSV_PATH, "utf8"));
console.log(`Loaded ${rows.length} queries from ${CSV_PATH}`);

const LIMIT = getArg("limit", null);
if (LIMIT) {
  rows = rows.slice(0, parseInt(LIMIT, 10));
  console.log(`--limit set: only processing first ${rows.length} queries`);
}

const ONLY = getArg("only", null);
if (ONLY) {
  const slugs = ONLY.split(",");
  rows = rows.filter((r) => slugs.includes(r.safe_query_slug));
  console.log(`--only set: processing ${rows.length} queries (${slugs.join(", ")})`);
}

// ── URL builders (mirrors scripts/{bing,google,canva}-*/browser.ts) ─────────
function buildUrl(platform, query) {
  const q = encodeURIComponent(query);
  if (platform === "bing") {
    return `https://www.bing.com/images/search?q=${q}&mkt=en-US&setlang=en-US&safeSearch=Moderate`;
  }
  if (platform === "google") {
    return `https://www.google.com/search?tbm=isch&q=${q}&hl=en`;
  }
  return `https://www.canva.com/templates/?query=${q}`;
}

const VIEWPORT = { width: 1440, height: 1000 };

async function detectBlock(page, platform) {
  const bodyText = await page.evaluate(() => document.body.innerText || "").catch(() => "");
  const lower = bodyText.toLowerCase();

  if (platform === "bing") {
    if (/unusual traffic|automated (queries|access)/.test(lower)) return "captcha";
    const hasConsent = await page
      .locator("#bnp_btn_accept, #bnp_container")
      .first()
      .isVisible()
      .catch(() => false);
    if (hasConsent) return "consent";
  }

  if (platform === "google") {
    if (/unusual traffic|not a robot|recaptcha/.test(lower)) return "captcha";
    if (page.url().includes("/sorry/")) return "captcha";
  }

  if (platform === "canva") {
    const loginModal = await page
      .locator('text=/log in to canva/i, [data-testid="login-modal"], text=/sign up.{0,20}free/i')
      .first()
      .isVisible()
      .catch(() => false);
    // Only treat as a hard wall if it also seems to hide the results grid.
    const hasResultsGrid = await page
      .locator('[data-testid="search-results"], a[href*="/templates/"]')
      .count()
      .catch(() => 0);
    if (loginModal && hasResultsGrid === 0) return "login_required";
  }

  return "ok";
}

async function isCanvaEmpty(page) {
  const bodyText = await page.evaluate(() => document.body.innerText || "").catch(() => "");
  return /couldn.?t find|no results|didn.?t match/i.test(bodyText);
}

async function run() {
  const profileDir = path.join(REPO_ROOT, ".cache", `external-screenshot-p0-12-${PLATFORM}-profile`);
  fs.mkdirSync(profileDir, { recursive: true });

  const context = await chromium.launchPersistentContext(profileDir, {
    headless: HEADLESS,
    viewport: VIEWPORT,
    locale: "en-US",
    timezoneId: "America/Los_Angeles",
    args: [
      "--lang=en-US",
      "--disable-blink-features=AutomationControlled",
      "--no-first-run",
      "--no-default-browser-check",
    ],
    ignoreDefaultArgs: ["--enable-automation"],
  });

  const page = context.pages()[0] ?? (await context.newPage());
  await page.setViewportSize(VIEWPORT);

  context.on("page", async (p) => {
    await p.waitForLoadState("domcontentloaded").catch(() => {});
    if (p !== page) await p.close().catch(() => {});
  });

  const results = [];

  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const slug = row.safe_query_slug;
    const outDir = path.join(SCREENSHOTS_ROOT, slug);
    fs.mkdirSync(outDir, { recursive: true });
    const outFile = path.join(outDir, `${PLATFORM}.png`);

    let queryUsed = row.query;
    let attempt = "primary";
    let status = "error";
    let reason = "";

    for (let pass = 0; pass < (PLATFORM === "canva" ? 2 : 1); pass++) {
      if (pass === 1) {
        queryUsed = row.canva_fallback_query;
        attempt = "fallback";
      }

      const url = buildUrl(PLATFORM, queryUsed);
      try {
        await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
        await page.waitForTimeout(2500);
        if (PLATFORM === "canva") {
          // Canva's template grid lazy-loads thumbnails; nudge-scroll to
          // trigger loading, then wait longer for images to actually render
          // before the screenshot (fixes blank/skeleton-card captures).
          await page.evaluate(() => window.scrollBy(0, 400));
          await page.waitForTimeout(1500);
          await page.evaluate(() => window.scrollTo(0, 0));
          await page.waitForTimeout(3000);
        }
      } catch (err) {
        status = "error";
        reason = `Navigation failed: ${err.message}`;
        console.log(`[${slug}] ${PLATFORM} (${attempt}: "${queryUsed}") -> error: ${reason}`);
        break;
      }

      const block = await detectBlock(page, PLATFORM);
      if (block === "consent") {
        // Try the one documented auto-accept selector; never click anything else.
        try {
          await page.locator("#bnp_btn_accept").click({ timeout: 3000 });
          await page.waitForTimeout(1500);
        } catch {
          /* fall through to re-check below */
        }
        const recheck = await detectBlock(page, PLATFORM);
        if (recheck !== "ok") {
          status = "consent_wall";
          reason = "Cookie consent page shown and not auto-acceptable via the known selector.";
          console.log(`[${slug}] ${PLATFORM} (${attempt}: "${queryUsed}") -> ${status}`);
          break;
        }
      } else if (block === "captcha") {
        status = "captcha";
        reason = `${PLATFORM} showed a CAPTCHA / bot-verification page for this query. Not bypassed.`;
        console.log(`[${slug}] ${PLATFORM} (${attempt}: "${queryUsed}") -> captcha`);
        break;
      } else if (block === "login_required") {
        if (PLATFORM === "canva" && pass === 0) {
          console.log(`[${slug}] canva (primary: "${queryUsed}") -> login_required, will try fallback query`);
          continue; // try fallback query
        }
        status = "login_required";
        reason = "Canva showed a login wall covering the results grid. Not bypassed.";
        console.log(`[${slug}] ${PLATFORM} (${attempt}: "${queryUsed}") -> login_required`);
        break;
      }

      // Canva zero-result check -> try fallback once
      if (PLATFORM === "canva" && pass === 0) {
        const empty = await isCanvaEmpty(page);
        if (empty) {
          console.log(`[${slug}] canva (primary: "${queryUsed}") -> empty, will try fallback query`);
          continue;
        }
      }

      // Success path: take the screenshot
      try {
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForTimeout(500);
        await page.screenshot({
          path: outFile,
          clip: { x: 0, y: 0, width: VIEWPORT.width, height: VIEWPORT.height },
        });
        status = "ok";
        reason =
          PLATFORM === "canva" && attempt === "fallback"
            ? `Captured using canva_fallback_query ("${queryUsed}") after the primary query ("${row.query}") showed login_required/empty.`
            : "Captured successfully.";
        console.log(`[${slug}] ${PLATFORM} (${attempt}: "${queryUsed}") -> ok -> ${outFile}`);
      } catch (err) {
        status = "error";
        reason = `Screenshot capture failed: ${err.message}`;
        console.log(`[${slug}] ${PLATFORM} (${attempt}: "${queryUsed}") -> error: ${reason}`);
      }
      break;
    }

    results.push({
      query: row.query,
      slug,
      platform: PLATFORM,
      status,
      queryUsed,
      attempt,
      reason,
      screenshotPath: status === "ok" ? path.relative(REPO_ROOT, outFile) : "",
    });

    if (i < rows.length - 1) {
      const delay = Math.floor(Math.random() * (DELAY_MAX_MS - DELAY_MIN_MS + 1)) + DELAY_MIN_MS;
      console.log(`  ...waiting ${(delay / 1000).toFixed(1)}s before next query`);
      await new Promise((r) => setTimeout(r, delay));
    }
  }

  await context.close();

  console.log("\n=== RESULT_JSON_START ===");
  console.log(JSON.stringify(results, null, 2));
  console.log("=== RESULT_JSON_END ===");

  const okCount = results.filter((r) => r.status === "ok").length;
  console.log(`\n${PLATFORM}: ${okCount}/${results.length} ok`);
}

run();
