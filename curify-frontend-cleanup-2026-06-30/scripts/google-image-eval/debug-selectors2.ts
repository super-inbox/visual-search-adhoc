#!/usr/bin/env node
/**
 * Debug: identify chips and image tile structure for 2026 Google Images layout.
 */

import { createBrowserContext, getOrCreatePage, buildSearchUrl } from "./browser.js";

const QUERY = "单词";
const context = await createBrowserContext(false);
const page = await getOrCreatePage(context);

await page.goto(buildSearchUrl(QUERY), { waitUntil: "domcontentloaded", timeout: 30000 });
await page.waitForTimeout(5000);

// ── Find chips ────────────────────────────────────────────────────────────────

console.log("=== All role=list or role=listitem links with their classes:");
const listLinks = await page.evaluate(() => {
  const NAV = new Set(["AI Mode","All","Images","Videos","Shopping","Forums","Short videos","More","Tools","News"]);
  const results: Array<{text: string; href: string; parentClasses: string}> = [];
  document.querySelectorAll('[role="listitem"] a, [role="list"] a').forEach((a) => {
    const text = (a.textContent ?? "").trim();
    if (NAV.has(text)) return;
    if (!text || text.length < 1) return;
    const parent = a.parentElement;
    results.push({
      text: text.slice(0, 40),
      href: (a as HTMLAnchorElement).href.slice(0, 100),
      parentClasses: parent?.className?.toString().slice(0, 60) ?? "",
    });
  });
  return results.slice(0, 20);
});
listLinks.forEach((l) => console.log(`  "${l.text}" parent="${l.parentClasses}"`));

// ── Find .ivg-i elements ─────────────────────────────────────────────────────

console.log("\n=== .ivg-i element details (first 3):");
const ivgI = await page.evaluate(() => {
  return Array.from(document.querySelectorAll(".ivg-i")).slice(0, 3).map((el) => {
    const img = el.querySelector("img");
    const a = el.querySelector("a");
    return {
      tagName: el.tagName,
      classes: el.className?.toString().slice(0, 80),
      imgSrc: (img?.src ?? "").slice(0, 80),
      imgAlt: img?.alt?.slice(0, 40) ?? "",
      aHref: ((a as HTMLAnchorElement)?.href ?? "").slice(0, 80),
      dataAttribs: [...el.attributes].filter(a => a.name.startsWith("data-")).map(a => `${a.name}=${a.value.slice(0,30)}`).join(", "),
    };
  });
});
ivgI.forEach((e, i) => console.log(`  [${i}] tag=${e.tagName} classes=${e.classes}\n      img=${e.imgSrc}\n      alt=${e.imgAlt}\n      data=${e.dataAttribs}`));

// ── Find .H8Rx8c elements ─────────────────────────────────────────────────────

console.log("\n=== .H8Rx8c element details (first 3):");
const h8 = await page.evaluate(() => {
  return Array.from(document.querySelectorAll(".H8Rx8c")).slice(0, 3).map((el) => {
    const img = el.querySelector("img");
    return {
      tagName: el.tagName,
      classes: el.className?.toString().slice(0, 80),
      imgSrc: (img?.src ?? "").slice(0, 80),
      dataAttribs: [...el.attributes].filter(a => a.name.startsWith("data-")).map(a => `${a.name}=${a.value.slice(0,30)}`).join(", "),
    };
  });
});
h8.forEach((e, i) => console.log(`  [${i}] tag=${e.tagName} classes=${e.classes}\n      img=${e.imgSrc}\n      data=${e.dataAttribs}`));

// ── Find encrypted-tbn images  ───────────────────────────────────────────────

console.log("\n=== encrypted-tbn img parents (first 5):");
const tbnParents = await page.evaluate(() => {
  return Array.from(document.querySelectorAll("img")).filter((img) =>
    img.src.includes("encrypted-tbn")
  ).slice(0, 5).map((img) => {
    let el: Element | null = img;
    const chain: string[] = [];
    for (let i = 0; i < 5; i++) {
      if (!el) break;
      chain.push(`${el.tagName}.${(el.className?.toString() ?? "").split(" ").slice(0,3).join(".")}`);
      el = el.parentElement;
    }
    return { src: img.src.slice(0, 60), chain: chain.join(" > ") };
  });
});
tbnParents.forEach((e, i) => console.log(`  [${i}] ${e.src}\n      ${e.chain}`));

// ── Check for chip container ─────────────────────────────────────────────────

console.log("\n=== Possible chip container classes:");
const chipContainer = await page.evaluate(() => {
  // Look for a scrollable element or g-scrolling-carousel equivalent
  const candidates = [
    "g-scrolling-carousel",
    ".VDgVie",   // chips bar 2025
    ".lJ9FBc",   // chips item
    ".OkX2Lc",   // chips wrapper
    ".bVBTFe",
    ".Z1JsRb",
    ".aCF1je",
    ".qEVEsc",
    '[aria-label="Search filters"]',
  ];
  return candidates.map((sel) => {
    const els = document.querySelectorAll(sel);
    if (els.length === 0) return null;
    const el = els[0];
    const texts = [...el.querySelectorAll("a")].slice(0, 5).map((a) => a.textContent?.trim() ?? "");
    return { sel, count: els.length, texts };
  }).filter(Boolean);
});
chipContainer.forEach((c) => console.log(`  ${c?.sel} → ${c?.count} els, texts: ${c?.texts.join(" | ")}`));

// ── Check actual URL after redirect ─────────────────────────────────────────

console.log("\n=== Final URL:", page.url());
console.log("=== udm=2 in URL:", page.url().includes("udm=2"));

await context.close();
console.log("\nDone.");
