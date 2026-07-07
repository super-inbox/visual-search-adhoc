#!/usr/bin/env node
/**
 * Ad-hoc Playwright collector for the gold_query_test_set (68 queries).
 *
 * NOT part of curify-frontend production code. This is a throwaway script
 * used to auto-collect raw search-result evidence (titles/links/tags/screenshots)
 * from the live Curify search page, for later human review. It does not
 * modify any production code, does not run ranking, and does not decide
 * final PASS/FAIL — those fields (manual_*) are left blank for a human.
 *
 * Usage:
 *   node collect_curify_search.mjs --smoke        # first 3 queries only
 *   node collect_curify_search.mjs --full          # all 68 queries
 *   node collect_curify_search.mjs --full --headed # visible browser window
 */

import { chromium } from "playwright";
import { parse } from "csv-parse/sync";
import { stringify } from "csv-stringify/sync";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");

const GOLD_CSV = path.join(REPO_ROOT, "docs/daily_report/7.7/gold_query_test_set_2026-07-07.csv");
const OUT_CSV = path.join(REPO_ROOT, "docs/daily_report/7.7/curify_search_auto_collect_2026-07-07.csv");
const OUT_JSON = path.join(REPO_ROOT, "docs/daily_report/7.7/curify_search_auto_collect_raw_2026-07-07.json");
const SCREENSHOT_DIR = path.join(REPO_ROOT, "docs/daily_report/7.7/curify_search_screenshots_2026-07-07");

const BASE_URL = "https://www.curify-ai.com";
const RESULT_WAIT_TIMEOUT_MS = 20000; // 20s per spec
const NAV_TIMEOUT_MS = 30000;
const DELAY_MIN_MS = 1000;
const DELAY_MAX_MS = 2000;
const MAX_RESULTS = 10;

const SCENE_SLUG = {
  "文创": "cultural",
  "品牌": "brand",
  "营销电商": "marketing",
  "教育": "education",
};

// ── CLI args ─────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const MODE = args.includes("--full") ? "full" : "smoke"; // default smoke
const HEADLESS = !args.includes("--headed");

function log(msg) {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${msg}`);
}

function randomDelay(minMs, maxMs) {
  const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function slugify(str, maxLen = 50) {
  return str
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, maxLen)
    .replace(/_+$/g, "");
}

function buildSearchUrl(query) {
  return `${BASE_URL}/search?q=${encodeURIComponent(query)}`;
}

// ── Load gold query set ─────────────────────────────────────────────────

function loadGoldQueries() {
  const raw = fs.readFileSync(GOLD_CSV, "utf-8");
  const records = parse(raw, { columns: true, skip_empty_lines: true });
  return records;
}

// ── Login wall detection (adapted from scripts/canva-search-eval/canvaConsent.ts) ──

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
    // Modal-specific heuristic: a dialog/modal element containing "sign in"/"log in" plus a password or email field
    const hasAuthModal = await page.evaluate(() => {
      const modalSelectors = ['[role="dialog"]', "div[class*='modal']", "div[class*='Modal']"];
      for (const sel of modalSelectors) {
        const els = document.querySelectorAll(sel);
        for (const el of els) {
          const t = el.textContent?.toLowerCase() ?? "";
          if ((t.includes("sign in") || t.includes("log in") || t.includes("sign up")) && el.querySelector('input[type="email"], input[type="password"]')) {
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

// ── Result extraction (adapted from scripts/curify-search-eval/extractResults.ts) ──

async function extractResults(page) {
  return page.evaluate((MAX) => {
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

    function pushCard(href, title, tag, sourceType) {
      const key = href || title;
      if (!key || seen.has(key)) return;
      seen.add(key);
      cards.push({ title, href, tag, sourceType });
    }

    // Examples / inspiration section
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
        pushCard(link.href, title, tag, "inspiration");
      }
    }

    // Templates section
    const templatesSection = findSectionByHeading(["templates"]);
    if (templatesSection) {
      const links = templatesSection.querySelectorAll('a[href*="/nano-template/"]');
      for (const link of links) {
        if (link.href.includes("/example/") || link.href.includes("/carousel/")) continue;
        const cardEl = link.closest("div.group") ?? link.closest("article") ?? link.closest("div");
        const img = cardEl?.querySelector("img");
        const nameEl = cardEl?.querySelector("h3, h4, p.font-semibold, div.font-semibold");
        const title = img?.alt?.trim() || textOf(nameEl) || textOf(link);
        pushCard(link.href.split("#")[0], title, textOf(nameEl), "template");
      }
    }

    // Generic fallback: any card-like element with an image + link, if nothing found above
    if (cards.length === 0) {
      const genericLinks = document.querySelectorAll('a[href*="/nano-template/"], a[href*="/template/"]');
      for (const link of genericLinks) {
        const img = link.querySelector("img") ?? link.closest("div")?.querySelector("img");
        const title = img?.alt?.trim() || textOf(link);
        pushCard(link.href, title, "", "unknown");
      }
    }

    // "No results" / "few results" banner text detection.
    // Curify shows a banner like: 'Few results for "X". Also showing results for: Y, Z.'
    // when it broadens the query — this is an important system-provided signal, capture it verbatim.
    let noResultText = "";
    const candidates = Array.from(document.querySelectorAll("p, h2, h3, div")).filter((el) => {
      const t = textOf(el).toLowerCase();
      return (
        t.length > 0 &&
        t.length < 300 &&
        (t.includes("no results") ||
          t.includes("nothing found") ||
          t.includes("couldn't find") ||
          t.includes("no matches") ||
          t.includes("few results for") ||
          t.includes("also showing results for"))
      );
    });
    if (candidates.length > 0) {
      // Prefer the most specific (shortest non-trivial) match, since parent divs often duplicate child text
      const sorted = candidates.map(textOf).sort((a, b) => a.length - b.length);
      noResultText = sorted[0];
    }

    return {
      cards: cards.slice(0, MAX),
      noResultText,
    };
  }, MAX_RESULTS);
}

// ── Weak filtering heuristic (NOT a final judgement — see spec) ─────────

function possibleFilteringIssue(query, titles) {
  if (titles.length === 0) return false;
  const stop = new Set(["a", "an", "the", "for", "and", "or", "of", "in", "on", "with", "to"]);
  const qTokens = query
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .split(/\s+/)
    .filter((t) => t.length > 1 && !stop.has(t));
  if (qTokens.length === 0) return false;
  let anyOverlap = false;
  for (const title of titles) {
    const tLower = title.toLowerCase();
    if (qTokens.some((tok) => tLower.includes(tok))) {
      anyOverlap = true;
      break;
    }
  }
  return !anyOverlap;
}

// ── Per-query collection ─────────────────────────────────────────────────

async function collectOne(page, index, row) {
  const query = row.query;
  const scene = row.primary_scene;
  const sceneSlug = SCENE_SLUG[scene] ?? "unknown";
  const idxStr = String(index + 1).padStart(3, "0");
  const filename = `${idxStr}_${sceneSlug}_${slugify(query)}.png`;
  const screenshotPath = path.join(SCREENSHOT_DIR, filename);
  const searchUrl = buildSearchUrl(query);

  const result = {
    query,
    primary_scene: scene,
    secondary_scene: row.secondary_scene || "",
    planned_test_type: row.planned_test_type,
    priority: row.priority,
    confidence: row.confidence,
    search_url: searchUrl,
    page_loaded: "no",
    login_wall: "no",
    visible_result_count: 0,
    top_10_result_titles: [],
    top_10_result_links: [],
    top_10_result_tags_or_labels: [],
    top_10_result_types: [],
    no_result_text: "",
    screenshot_path: "",
    auto_flags: [],
    needs_human_review: "yes",
  };

  try {
    await page.goto(searchUrl, { waitUntil: "domcontentloaded", timeout: NAV_TIMEOUT_MS });
    result.page_loaded = "yes";
  } catch (err) {
    log(`  [${idxStr}] Navigation failed: ${err.message}`);
    result.auto_flags.push("page_error");
    try {
      await page.screenshot({ path: screenshotPath, fullPage: true });
      result.screenshot_path = path.relative(REPO_ROOT, screenshotPath);
    } catch {
      /* ignore */
    }
    return result;
  }

  // Wait for either a results container, "no results" text, or timeout.
  let timedOut = false;
  try {
    await Promise.race([
      page.waitForSelector('section h2, div[class*="rounded-3xl"], a[href*="/nano-template/"]', {
        timeout: RESULT_WAIT_TIMEOUT_MS,
      }),
      page.waitForSelector('text=/no results/i', { timeout: RESULT_WAIT_TIMEOUT_MS }),
    ]);
  } catch {
    timedOut = true;
  }

  // Extra settle time for images / late hydration
  await page.waitForTimeout(1500);

  const loginWall = await detectLoginWall(page);
  result.login_wall = loginWall ? "yes" : "no";
  if (loginWall) {
    result.auto_flags.push("login_wall");
  }

  if (timedOut && !loginWall) {
    // Re-check once more in case content arrived just after the race resolved false
    const stillLoading = await page.evaluate(() => {
      const bodyText = document.body?.innerText ?? "";
      return bodyText.trim().length < 50 || /loading/i.test(bodyText.slice(0, 200));
    }).catch(() => true);
    if (stillLoading) {
      result.auto_flags.push("extract_failed");
      try {
        await page.screenshot({ path: screenshotPath, fullPage: true });
        result.screenshot_path = path.relative(REPO_ROOT, screenshotPath);
      } catch {
        /* ignore */
      }
      return result;
    }
  }

  // Extract results (even if login wall present — some results may be visible behind it)
  try {
    const { cards, noResultText } = await extractResults(page);
    result.visible_result_count = cards.length;
    result.top_10_result_titles = cards.map((c) => c.title || "");
    result.top_10_result_links = cards.map((c) => c.href || "");
    result.top_10_result_tags_or_labels = cards.map((c) => c.tag || "");
    result.top_10_result_types = cards.map((c) => c.sourceType || "unknown");
    result.no_result_text = noResultText || "";

    if (cards.length === 0) {
      result.auto_flags.push(noResultText ? "zero_result" : loginWall ? "zero_result" : "extract_failed");
    } else if (cards.length < 3) {
      result.auto_flags.push("low_result");
    }

    // Curify's own "Few results for X. Also showing results for: Y, Z" banner means the
    // engine itself broadened the query — even if 10 cards are shown, they may be padding
    // from the broadened query rather than genuine matches. Flag distinctly so a human
    // reviewer doesn't miss it just because visible_result_count looks healthy.
    if (/few results for|also showing results for/i.test(noResultText)) {
      result.auto_flags.push("query_broadened_by_curify");
    }

    if (cards.length > 0 && possibleFilteringIssue(query, result.top_10_result_titles)) {
      result.auto_flags.push("possible_filtering_issue");
    }
  } catch (err) {
    log(`  [${idxStr}] Extraction failed: ${err.message}`);
    result.auto_flags.push("extract_failed");
  }

  // Full-page screenshot
  try {
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(300);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    result.screenshot_path = path.relative(REPO_ROOT, screenshotPath);
  } catch (err) {
    log(`  [${idxStr}] Screenshot failed: ${err.message}`);
  }

  return result;
}

// ── Main ──────────────────────────────────────────────────────────────────

async function main() {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  fs.mkdirSync(path.dirname(OUT_CSV), { recursive: true });

  const allQueries = loadGoldQueries();
  log(`Loaded ${allQueries.length} gold queries from ${path.relative(REPO_ROOT, GOLD_CSV)}`);

  const queriesToRun = MODE === "smoke" ? allQueries.slice(0, 3) : allQueries;
  log(`Mode: ${MODE} — will process ${queriesToRun.length} queries (headless=${HEADLESS})`);

  const browser = await chromium.launch({ headless: HEADLESS });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: "en-US",
  });
  const page = await context.newPage();

  const results = [];
  for (let i = 0; i < queriesToRun.length; i++) {
    const row = queriesToRun[i];
    log(`[${i + 1}/${queriesToRun.length}] "${row.query}" (${row.primary_scene})`);
    const r = await collectOne(page, i, row);
    log(
      `  -> page_loaded=${r.page_loaded} login_wall=${r.login_wall} results=${r.visible_result_count} flags=[${r.auto_flags.join(",")}]`,
    );
    results.push(r);
    if (i < queriesToRun.length - 1) {
      await randomDelay(DELAY_MIN_MS, DELAY_MAX_MS);
    }
  }

  await browser.close();

  // Write raw JSON (always, even for smoke test — useful for debugging)
  const jsonPath = MODE === "smoke" ? OUT_JSON.replace(".json", "_smoke.json") : OUT_JSON;
  fs.writeFileSync(jsonPath, JSON.stringify(results, null, 2), "utf-8");
  log(`Raw JSON written: ${path.relative(REPO_ROOT, jsonPath)}`);

  // Write CSV only in --full mode (smoke test is for verification only)
  if (MODE === "full") {
    const csvRows = results.map((r) => ({
      query: r.query,
      primary_scene: r.primary_scene,
      secondary_scene: r.secondary_scene,
      planned_test_type: r.planned_test_type,
      priority: r.priority,
      confidence: r.confidence,
      search_url: r.search_url,
      page_loaded: r.page_loaded,
      login_wall: r.login_wall,
      visible_result_count: r.visible_result_count,
      top_10_result_titles: r.top_10_result_titles.join(" | "),
      top_10_result_links: r.top_10_result_links.join(" | "),
      top_10_result_tags_or_labels: r.top_10_result_tags_or_labels.join(" | "),
      top_10_result_types: r.top_10_result_types.join(" | "),
      no_result_text: r.no_result_text,
      screenshot_path: r.screenshot_path,
      auto_flags: r.auto_flags.join(";"),
      needs_human_review: r.needs_human_review,
      manual_relevant_count: "",
      manual_irrelevant_count: "",
      manual_recall_status: "",
      manual_filtering_status: "",
      manual_content_gap: "",
      manual_issue_type: "",
      manual_notes: "",
    }));
    const csvOut = stringify(csvRows, { header: true });
    fs.writeFileSync(OUT_CSV, csvOut, "utf-8");
    log(`CSV written: ${path.relative(REPO_ROOT, OUT_CSV)}`);
  }

  // Summary counts
  const loaded = results.filter((r) => r.page_loaded === "yes").length;
  const loginWall = results.filter((r) => r.login_wall === "yes").length;
  const zeroResult = results.filter((r) => r.auto_flags.includes("zero_result")).length;
  const lowResult = results.filter((r) => r.auto_flags.includes("low_result")).length;
  const extractFailed = results.filter((r) => r.auto_flags.includes("extract_failed")).length;
  const pageError = results.filter((r) => r.auto_flags.includes("page_error")).length;

  log("── Summary ──────────────────────────────────");
  log(`Total processed: ${results.length}`);
  log(`page_loaded=yes: ${loaded}`);
  log(`login_wall=yes: ${loginWall}`);
  log(`zero_result: ${zeroResult}`);
  log(`low_result: ${lowResult}`);
  log(`extract_failed: ${extractFailed}`);
  log(`page_error: ${pageError}`);
}

main().catch((err) => {
  console.error("FATAL:", err);
  process.exit(1);
});
