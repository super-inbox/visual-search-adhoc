import type { Page } from "playwright";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";
import { VIEWPORT } from "./browser.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
const SCREENSHOTS_BASE = path.join(
  ROOT,
  "docs/external-signal-pilot/curify-search-eval-58/screenshots",
);

export function makeSlug(query: string, queryId: number): string {
  const ascii = query
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);
  return ascii.length >= 2 ? ascii : `q${String(queryId).padStart(3, "0")}`;
}

export function makeScreenshotDir(queryId: number, slug: string): string {
  const dirName = `${String(queryId).padStart(3, "0")}-${slug}`;
  const dirPath = path.join(SCREENSHOTS_BASE, dirName);
  fs.mkdirSync(dirPath, { recursive: true });
  return dirPath;
}

export function makeScreenshotPaths(queryId: number, slug: string): { page1: string; page2: string } {
  const dir = makeScreenshotDir(queryId, slug);
  return {
    page1: path.join(dir, "curify-search-page1.png"),
    page2: path.join(dir, "curify-search-page2.png"),
  };
}

export async function takeViewportScreenshot(page: Page, filePath: string): Promise<void> {
  await page.setViewportSize(VIEWPORT);
  await page.screenshot({
    path: filePath,
    clip: { x: 0, y: 0, width: VIEWPORT.width, height: VIEWPORT.height },
  });
}

export async function takeScreenshots(
  page: Page,
  queryId: number,
  query: string,
): Promise<{ page1: string; page2: string }> {
  const slug = makeSlug(query, queryId);
  const paths = makeScreenshotPaths(queryId, slug);

  // Ensure top of page
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(500);

  // page1: first viewport after load
  await takeViewportScreenshot(page, paths.page1);

  // Scroll down ~900px and wait for images to settle
  await page.evaluate(() => window.scrollBy(0, 900));
  await page.waitForTimeout(1000);

  // page2: second viewport
  await takeViewportScreenshot(page, paths.page2);

  // Scroll back to top
  await page.evaluate(() => window.scrollTo(0, 0));

  return paths;
}

export async function takeDebugScreenshot(
  page: Page,
  queryId: number,
  label: string,
): Promise<string> {
  const id = String(queryId).padStart(3, "0");
  fs.mkdirSync(SCREENSHOTS_BASE, { recursive: true });
  const filePath = path.join(SCREENSHOTS_BASE, `${id}-debug-${label}.png`);
  await takeViewportScreenshot(page, filePath);
  return filePath;
}
