import type { Page } from "playwright";
import type { ImageResult } from "./types.js";

const SCROLL_STEP = 900;
const SCROLL_WAIT_MS = 1200;
const MAX_SCROLLS = 6;

function extractDomain(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

/**
 * Extract top-10 results from Google Images (2026 udm=2 layout).
 * Data is read directly from DOM attributes — no clicking required.
 */
export async function extractTop10(
  page: Page,
  onNote?: (rank: number, note: string) => void,
): Promise<ImageResult[]> {
  // Scroll to collect at least 10 tiles
  const tiles = await scrollAndCollect(page, 10);

  const results: ImageResult[] = [];
  let rank = 1;

  for (const tile of tiles.slice(0, 10)) {
    const result: ImageResult = {
      rank,
      title: tile.title,
      source: tile.source,
      page_url: tile.pageUrl,
      image_url: "", // base64 thumbnails are too large; skip
      thumbnail_url: "",
      result_type: "organic",
      notes: tile.notes,
    };

    if (!result.page_url) {
      onNote?.(rank, "page_url empty");
      result.notes = result.notes || "page_url not found";
    }

    results.push(result);
    rank++;
  }

  return results;
}

interface TileData {
  title: string;
  source: string;
  pageUrl: string;
  notes: string;
}

async function scrollAndCollect(page: Page, needed: number): Promise<TileData[]> {
  let scrolls = 0;

  while (scrolls <= MAX_SCROLLS) {
    const tiles = await extractTiles(page);
    if (tiles.length >= needed) return tiles;

    const prevCount = tiles.length;
    await page.evaluate((step) => window.scrollBy(0, step), SCROLL_STEP);
    await page.waitForTimeout(SCROLL_WAIT_MS);

    // Check if new tiles loaded
    const newTiles = await extractTiles(page);
    if (newTiles.length <= prevCount) break; // no new content
    scrolls++;
  }

  return await extractTiles(page);
}

async function extractTiles(page: Page): Promise<TileData[]> {
  return page.evaluate(() => {
    const results: Array<{ title: string; source: string; pageUrl: string; notes: string }> = [];
    const seen = new Set<string>();

    // 2026 layout: .ivg-i tiles with data-lpage attribute
    const ivgTiles = document.querySelectorAll(".ivg-i[data-lpage]");
    if (ivgTiles.length > 0) {
      ivgTiles.forEach((el) => {
        const pageUrl = el.getAttribute("data-lpage") ?? "";
        if (!pageUrl || seen.has(pageUrl)) return;

        // Skip items without organic attrid
        const attrid = el.getAttribute("data-attrid") ?? "";
        if (attrid && attrid !== "images universal") return;

        const img = el.querySelector("img");
        const title = img?.alt?.trim() ?? "";

        let source = "";
        try {
          source = new URL(pageUrl).hostname.replace(/^www\./, "");
        } catch {
          source = "";
        }

        seen.add(pageUrl);
        results.push({ title, source, pageUrl, notes: "" });
      });
    }

    // Fallback: older div[data-ri] layout
    if (results.length === 0) {
      document.querySelectorAll("div[data-ri]").forEach((el) => {
        const img = el.querySelector('img[src]:not([src^="data:"])');
        if (!img) return;
        const src = (img as HTMLImageElement).src;
        if (seen.has(src)) return;
        seen.add(src);
        results.push({ title: (img as HTMLImageElement).alt ?? "", source: "", pageUrl: "", notes: "fallback:data-ri" });
      });
    }

    return results;
  });
}

// Re-export for tests that import it
export { extractTiles as testableExtractTiles };
