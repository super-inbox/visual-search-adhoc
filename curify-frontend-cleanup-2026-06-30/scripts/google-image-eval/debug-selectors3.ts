#!/usr/bin/env node
/**
 * Debug: check if .GKS7s is inside .ivg-i, and find thumbnail URL from ivg-i.
 */
import { createBrowserContext, getOrCreatePage, buildSearchUrl } from "./browser.js";

const context = await createBrowserContext(false);
const page = await getOrCreatePage(context);
await page.goto(buildSearchUrl("chiikawa"), { waitUntil: "domcontentloaded", timeout: 30000 });
await page.waitForTimeout(5000);

const result = await page.evaluate(() => {
  const ivgItems = Array.from(document.querySelectorAll(".ivg-i")).slice(0, 3);
  return ivgItems.map((el, i) => {
    const allImgs = [...el.querySelectorAll("img")].map((img) => ({
      src: img.src.slice(0, 80),
      alt: img.alt.slice(0, 50),
      classes: img.className?.toString().slice(0, 60),
    }));
    const gks = el.querySelector(".GKS7s");
    const encImg = el.querySelector('img[src*="encrypted-tbn"]');
    const lpage = el.getAttribute("data-lpage") ?? "";
    const mainImg = el.querySelector("img");
    return {
      i,
      lpage: lpage.slice(0, 80),
      mainImgAlt: mainImg?.alt?.slice(0, 60) ?? "",
      hasGKS7s: !!gks,
      encryptedTbnInside: !!encImg,
      encTbnSrc: (encImg?.getAttribute("src") ?? "").slice(0, 80),
      allImgCount: allImgs.length,
      allImgs: allImgs.slice(0, 3),
    };
  });
});

console.log(JSON.stringify(result, null, 2));

// Also check if there's a separate GKS7s-to-ivg-i mapping
const topLevelGks = await page.evaluate(() => {
  return Array.from(document.querySelectorAll(".GKS7s")).length;
});
console.log("\nTop-level .GKS7s count:", topLevelGks);

// Find what contains GKS7s
const gksParent = await page.evaluate(() => {
  const gks = document.querySelector(".GKS7s");
  if (!gks) return null;
  let el: Element | null = gks;
  const chain: string[] = [];
  for (let i = 0; i < 8; i++) {
    if (!el) break;
    const classes = el.className?.toString().split(" ").slice(0, 4).join(".");
    const hasIvg = el.classList?.contains("ivg-i");
    chain.push(`${el.tagName}${classes ? "." + classes : ""}${hasIvg ? " [ivg-i]" : ""}`);
    el = el.parentElement;
  }
  return chain;
});
console.log("\n.GKS7s ancestor chain:", gksParent?.join(" > "));

// Data-lpage check — get first 5
const lpages = await page.evaluate(() => {
  return Array.from(document.querySelectorAll(".ivg-i")).slice(0, 5).map((el) => ({
    lpage: el.getAttribute("data-lpage") ?? "",
    docid: el.getAttribute("data-docid") ?? "",
    alt: el.querySelector("img")?.alt?.slice(0, 50) ?? "",
  }));
});
console.log("\nFirst 5 .ivg-i lpage+alt:");
lpages.forEach((l) => console.log(`  lpage=${l.lpage} | alt=${l.alt}`));

await context.close();
