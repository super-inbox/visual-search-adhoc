import type { Page } from "playwright";
import type { BingImageResult } from "./types.js";

const MAX_SCROLLS = 4;
const SCROLL_STEP = 900;
const SCROLL_WAIT_MS = 1200;

/**
 * Extract top-10 image results from Bing Images page.
 * Reads directly from DOM attributes — no clicking into the detail panel.
 * NOTE: No inner const-arrow-function assignments inside page.evaluate callbacks —
 *       esbuild injects __name helpers for them, which are undefined in the browser context.
 */
export async function extractTop10(
  page: Page,
  onNote?: (rank: number, note: string) => void,
): Promise<BingImageResult[]> {
  const tiles = await scrollAndCollect(page, 10);
  const results: BingImageResult[] = [];
  for (const tile of tiles.slice(0, 10)) {
    const rank = results.length + 1;
    const result: BingImageResult = {
      rank,
      title: tile.title,
      source: tile.source,
      pageUrl: tile.pageUrl,
      imageUrl: tile.imageUrl,
      thumbnailUrl: tile.thumbnailUrl,
      visibleText: tile.visibleText,
    };
    if (!result.pageUrl) onNote?.(rank, "pageUrl empty");
    if (!result.title) onNote?.(rank, "title empty");
    results.push(result);
  }
  return results;
}

interface TileData {
  title: string;
  source: string;
  pageUrl: string;
  imageUrl: string;
  thumbnailUrl: string;
  visibleText: string;
}

async function scrollAndCollect(page: Page, needed: number): Promise<TileData[]> {
  let scrolls = 0;
  while (scrolls <= MAX_SCROLLS) {
    const tiles = await extractTiles(page);
    if (tiles.length >= needed) return tiles;
    const prevCount = tiles.length;
    await page.evaluate((step) => window.scrollBy(0, step), SCROLL_STEP);
    await page.waitForTimeout(SCROLL_WAIT_MS);
    const newTiles = await extractTiles(page);
    if (newTiles.length <= prevCount) break;
    scrolls++;
  }
  return await extractTiles(page);
}

async function extractTiles(page: Page): Promise<TileData[]> {
  // All logic inlined — no inner function declarations — avoids esbuild __name injection
  return page.evaluate(() => {
    const results: Array<{
      title: string; source: string; pageUrl: string;
      imageUrl: string; thumbnailUrl: string; visibleText: string;
    }> = [];
    const seenKeys = new Set<string>();

    // Primary: .iusc tiles (standard Bing Images result containers)
    const iuscTiles = document.querySelectorAll(".iusc");
    iuscTiles.forEach((el) => {
      if (results.length >= 15) return;

      // Parse the 'm' attribute JSON: {murl, turl, purl, t, ...}
      const mAttr = el.getAttribute("m") || el.getAttribute("data-m") || "";
      let parsedMurl = "";
      let parsedTurl = "";
      let parsedPurl = "";
      let parsedTitle = "";
      if (mAttr) {
        try {
          const obj = JSON.parse(mAttr) as Record<string, string>;
          parsedMurl = obj["murl"] ?? "";
          parsedTurl = obj["turl"] ?? "";
          parsedPurl = obj["purl"] ?? "";
          parsedTitle = obj["t"] ?? "";
        } catch {
          // ignore parse errors
        }
      }

      let pageUrl = parsedPurl;
      const imageUrl = parsedMurl;
      const thumbnailUrl = parsedTurl;
      let title = parsedTitle;

      // Try anchor href as fallback for pageUrl
      const anchor = el.querySelector("a[href]") as HTMLAnchorElement | null;
      const img = el.querySelector("img") as HTMLImageElement | null;

      if (!pageUrl && anchor) {
        const href = anchor.href || anchor.getAttribute("href") || "";
        if (href.includes("purl=")) {
          try {
            pageUrl = decodeURIComponent(new URL(href).searchParams.get("purl") ?? "");
          } catch {
            // ignore
          }
        } else if (href.startsWith("http") && !href.includes("bing.com")) {
          pageUrl = href;
        }
      }

      // Title fallbacks
      if (!title && img) title = (img.alt || "").trim();
      if (!title && anchor) title = (anchor.getAttribute("aria-label") || "").trim();

      // Thumbnail fallback
      let thumb = thumbnailUrl;
      if (!thumb && img) {
        const src = img.src || img.getAttribute("data-src") || "";
        if (src && !src.startsWith("data:")) thumb = src;
      }

      // Deduplicate
      const dedupeKey = pageUrl || imageUrl || title;
      if (!dedupeKey || seenKeys.has(dedupeKey)) return;
      seenKeys.add(dedupeKey);

      // Skip ad tiles
      if (el.getAttribute("data-adblk") || el.getAttribute("data-ad")) return;

      // Domain
      let source = "";
      try {
        source = new URL(pageUrl || imageUrl).hostname.replace(/^www\./, "");
      } catch {
        // ignore
      }

      const visText = (el.querySelector(".b_imageTitleText") as HTMLElement | null)?.innerText?.trim()
        || (el.querySelector(".inflnk") as HTMLElement | null)?.innerText?.trim()
        || "";

      results.push({
        title,
        source,
        pageUrl,
        imageUrl: imageUrl.startsWith("data:") ? "" : imageUrl,
        thumbnailUrl: thumb.startsWith("data:") ? "" : thumb,
        visibleText: visText,
      });
    });

    if (results.length > 0) return results;

    // Fallback: .inflnk anchors (older Bing layout)
    const inflnkAnchors = document.querySelectorAll("a.inflnk[href]");
    inflnkAnchors.forEach((el) => {
      if (results.length >= 15) return;
      const anchor = el as HTMLAnchorElement;
      const href = anchor.href || "";
      if (!href || href.includes("bing.com")) return;
      if (seenKeys.has(href)) return;
      seenKeys.add(href);
      const img = anchor.querySelector("img") as HTMLImageElement | null;
      const title = (img?.alt || anchor.textContent || "").trim();
      const src = img?.src ?? "";
      let source = "";
      try { source = new URL(href).hostname.replace(/^www\./, ""); } catch { }
      results.push({
        title,
        source,
        pageUrl: href,
        imageUrl: "",
        thumbnailUrl: src.startsWith("data:") ? "" : src,
        visibleText: "",
      });
    });

    return results;
  });
}
