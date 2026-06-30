import { chromium, type BrowserContext, type Page } from "playwright";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
const PROFILE_DIR = path.join(ROOT, ".cache/pinterest-search-eval-profile");

export const VIEWPORT = { width: 1536, height: 960 };

const BASE_LAUNCH_OPTIONS = {
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
};

export async function createBrowserContext(headless = false): Promise<BrowserContext> {
  fs.mkdirSync(PROFILE_DIR, { recursive: true });
  const opts = { ...BASE_LAUNCH_OPTIONS, headless };

  try {
    const ctx = await chromium.launchPersistentContext(PROFILE_DIR, {
      ...opts,
      channel: "chrome",
    });
    console.log("[browser] Using system Chrome (channel: chrome)");
    return ctx;
  } catch {
    console.log("[browser] System Chrome unavailable, falling back to Playwright Chromium");
  }

  const ctx = await chromium.launchPersistentContext(PROFILE_DIR, opts);
  console.log("[browser] Using Playwright Chromium");
  return ctx;
}

export async function getOrCreatePage(context: BrowserContext): Promise<Page> {
  const pages = context.pages();
  if (pages.length > 0) {
    const page = pages[0];
    await page.setViewportSize(VIEWPORT);
    return page;
  }
  const page = await context.newPage();
  await page.setViewportSize(VIEWPORT);
  return page;
}

export function buildPinterestSearchUrl(query: string): string {
  return `https://www.pinterest.com/search/pins/?q=${encodeURIComponent(query)}`;
}

export async function randomDelay(minMs: number, maxMs: number): Promise<void> {
  const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  await new Promise((resolve) => setTimeout(resolve, ms));
}
