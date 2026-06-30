#!/usr/bin/env node
/**
 * Debug selector discovery for Google Images.
 * Runs ONE query, waits 8s after load, then dumps available selectors.
 *
 * Usage:
 *   npx tsx scripts/google-image-eval/debug-selectors.ts
 */

import { createBrowserContext, getOrCreatePage, buildSearchUrl } from "./browser.js";

const QUERY = "单词";

const context = await createBrowserContext(false);
const page = await getOrCreatePage(context);

console.log(`\nNavigating to Google Images for: "${QUERY}"`);
const url = buildSearchUrl(QUERY);
console.log(`URL: ${url}\n`);

await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
await page.waitForTimeout(5000);

console.log("=== Page title:", await page.title());
console.log("=== URL:", page.url());

// Dump body text preview (first 500 chars)
const bodyText = await page.evaluate(() => (document.body?.innerText ?? "").slice(0, 500));
console.log("\n=== Body text preview:\n", bodyText);

// Check candidate selectors for labels
const CHIP_CANDIDATES = [
  'a[href*="tbm=isch"]',
  'g-scrolling-carousel a',
  '[role="list"] a',
  '[role="tab"]',
  '[role="listitem"] a',
  '.Cl9Tod a',       // 2025 chips
  '.GKS7s a',        // another variant
  '.RntSmf a',
  '.arPgPb a',
  '.ellipsis a',
  'div[jsname] a[href*="tbm"]',
  'a.UcdLK',
  'a.ovfLK',
];

console.log("\n=== Chip selector probe:");
for (const sel of CHIP_CANDIDATES) {
  try {
    const els = await page.$$(sel);
    if (els.length > 0) {
      const texts = await Promise.all(els.slice(0, 5).map((e) => e.textContent()));
      console.log(`  ✓ ${sel} → ${els.length} elements, texts: ${texts.map((t) => t?.trim()).join(" | ")}`);
    }
  } catch {
    // skip
  }
}

// Check candidate selectors for image grid
const GRID_CANDIDATES = [
  "div[data-ri]",
  "div[data-id]",
  "#islrg",
  ".islrc",
  "#rg_s",
  "g-img",
  "img[jsname]",
  'div[role="listitem"]',
  ".fR600b img",
  ".wH6SXe",
  ".ivg-i",
  ".H8Rx8c",
  ".YQ4gaf",
  "[data-ved] img",
];

console.log("\n=== Grid selector probe:");
for (const sel of GRID_CANDIDATES) {
  try {
    const els = await page.$$(sel);
    if (els.length > 0) {
      console.log(`  ✓ ${sel} → ${els.length} elements`);
    }
  } catch {
    // skip
  }
}

// Dump all img src (first 5 non-data)
console.log("\n=== Img srcs (first 5 non-data):");
const imgSrcs = await page.evaluate(() => {
  const imgs = Array.from(document.querySelectorAll("img"));
  return imgs
    .map((i) => i.src)
    .filter((s) => s && !s.startsWith("data:") && !s.startsWith("//"))
    .slice(0, 5);
});
imgSrcs.forEach((s) => console.log(" ", s.slice(0, 120)));

// Find all links containing tbm=isch
console.log("\n=== Links with tbm=isch (first 10):");
const links = await page.evaluate(() =>
  Array.from(document.querySelectorAll('a[href*="tbm=isch"]'))
    .slice(0, 10)
    .map((a) => ({ text: (a.textContent ?? "").trim().slice(0, 40), href: (a as HTMLAnchorElement).href.slice(0, 80) })),
);
links.forEach((l) => console.log(`  "${l.text}" → ${l.href}`));

// Dump all distinct class names from img parents (depth 3)
console.log("\n=== Class names near image elements:");
const classNames = await page.evaluate(() => {
  const classes = new Set<string>();
  document.querySelectorAll("img").forEach((img) => {
    let el: Element | null = img;
    for (let d = 0; d < 4; d++) {
      if (!el) break;
      if (el.className && typeof el.className === "string") {
        el.className.split(/\s+/).filter(Boolean).forEach((c) => classes.add(c));
      }
      el = el.parentElement;
    }
  });
  return [...classes].slice(0, 40);
});
console.log("  ", classNames.join(", "));

await context.close();
console.log("\nDone.");
