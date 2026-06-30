import { chromium, type BrowserContext, type Page } from "playwright";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
const PROFILE_DIR = path.join(ROOT, ".cache/curify-search-eval-profile");

export const VIEWPORT = { width: 1440, height: 900 };

const DEFAULT_BASE_URL = "http://localhost:3000/en";

export function getCurifyBaseUrl(): string {
  return (process.env.CURIFY_BASE_URL ?? DEFAULT_BASE_URL).replace(/\/$/, "");
}

export function buildSearchUrl(query: string): string {
  const base = getCurifyBaseUrl();
  return `${base}/search?q=${encodeURIComponent(query)}`;
}

export async function createBrowserContext(headless = false): Promise<BrowserContext> {
  fs.mkdirSync(PROFILE_DIR, { recursive: true });

  const opts = {
    viewport: VIEWPORT,
    locale: "en-US",
    args: ["--lang=en-US", "--no-first-run", "--no-default-browser-check"],
    headless,
  };

  // Try system Chrome first
  try {
    const ctx = await chromium.launchPersistentContext(PROFILE_DIR, {
      ...opts,
      channel: "chrome",
    });
    console.log("[browser] Using system Chrome");
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

export async function randomDelay(minMs: number, maxMs: number): Promise<void> {
  const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  await new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Returns true if finalUrl is the same page as searchUrl after stripping the
 * Next.js default-locale prefix (e.g. /en → /).
 * Used to distinguish real redirects from locale-prefix stripping.
 */
export function isLocaleRedirect(searchUrl: string, finalUrl: string): boolean {
  if (searchUrl === finalUrl) return true;
  try {
    const a = new URL(searchUrl);
    const b = new URL(finalUrl);
    if (a.origin !== b.origin) return false;
    if (a.search !== b.search) return false;
    // Strip leading /xx (2-char locale) from path
    const normA = a.pathname.replace(/^\/[a-z]{2}(?=\/|$)/, "");
    const normB = b.pathname.replace(/^\/[a-z]{2}(?=\/|$)/, "");
    return normA === normB;
  } catch {
    return false;
  }
}
