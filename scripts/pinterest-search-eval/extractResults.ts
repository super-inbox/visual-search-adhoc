import type { Page } from "playwright";
import type { PinterestPinResult } from "./types.js";

const MAX_SCROLLS = 3;
const SCROLL_STEP = 900;
const SCROLL_WAIT_MS = 1500;

/**
 * Extract top-10 pin results from Pinterest search page.
 * Reads from DOM attributes — no clicking into pin detail pages.
 * NOTE: All logic inlined inside page.evaluate — no inner const-arrow-function
 *       assignments — avoids esbuild __name injection in serialized browser context.
 */
export async function extractTop10(
  page: Page,
  onNote?: (rank: number, note: string) => void,
): Promise<PinterestPinResult[]> {
  const tiles = await scrollAndCollect(page, 10);
  const results: PinterestPinResult[] = [];

  for (const tile of tiles.slice(0, 10)) {
    const rank = results.length + 1;
    const result: PinterestPinResult = {
      rank,
      title: tile.title,
      description: tile.description,
      source: tile.source,
      pinUrl: tile.pinUrl,
      pageUrl: tile.pageUrl,
      imageUrl: tile.imageUrl,
      thumbnailUrl: tile.thumbnailUrl,
      visibleText: tile.visibleText,
    };
    if (!result.pinUrl) onNote?.(rank, "pinUrl empty");
    if (!result.title) onNote?.(rank, "title empty");
    results.push(result);
  }

  return results;
}

interface PinTileData {
  title: string;
  description: string;
  source: string;
  pinUrl: string;
  pageUrl: string;
  imageUrl: string;
  thumbnailUrl: string;
  visibleText: string;
}

async function scrollAndCollect(page: Page, needed: number): Promise<PinTileData[]> {
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

async function extractTiles(page: Page): Promise<PinTileData[]> {
  return page.evaluate(() => {
    const results: Array<{
      title: string; description: string; source: string;
      pinUrl: string; pageUrl: string; imageUrl: string;
      thumbnailUrl: string; visibleText: string;
    }> = [];
    const seenPinUrls = new Set<string>();

    // Pinterest pin cards: anchors pointing to /pin/<id>/
    const pinAnchors = document.querySelectorAll('a[href*="/pin/"]');
    pinAnchors.forEach((el) => {
      if (results.length >= 20) return;
      const anchor = el as HTMLAnchorElement;
      const href = anchor.href || anchor.getAttribute("href") || "";
      if (!href || !href.includes("/pin/")) return;

      // Normalize to absolute URL
      let pinUrl = href;
      try {
        pinUrl = new URL(href, location.origin).href;
      } catch { }

      // Skip non-pin pages (boards, user profiles)
      if (!/\/pin\/\d+/.test(pinUrl)) return;

      // Deduplicate
      const pinId = pinUrl.match(/\/pin\/(\d+)/)?.[1] ?? pinUrl;
      if (seenPinUrls.has(pinId)) return;
      seenPinUrls.add(pinId);

      // Skip ad tiles
      const container = anchor.closest('[data-test-id]') as HTMLElement | null;
      if (container?.getAttribute("data-test-id") === "ad-pin") return;

      // Image extraction
      const img = anchor.querySelector("img") as HTMLImageElement | null;
      let imageUrl = "";
      let thumbnailUrl = "";
      if (img) {
        const src = img.src || img.getAttribute("data-src") || img.getAttribute("src") || "";
        if (src && !src.startsWith("data:")) {
          if (src.includes("236x") || src.includes("_b.") || src.length < 200) {
            thumbnailUrl = src;
          } else {
            imageUrl = src;
          }
        }
        // srcset: pick highest quality
        const srcset = img.srcset || img.getAttribute("srcset") || "";
        if (srcset) {
          const parts = srcset.split(",").map((s) => s.trim().split(/\s+/));
          const best = parts.sort((a, b) => {
            const wa = parseFloat((a[1] || "0").replace(/[^\d.]/g, "")) || 0;
            const wb = parseFloat((b[1] || "0").replace(/[^\d.]/g, "")) || 0;
            return wb - wa;
          })[0];
          if (best?.[0] && !best[0].startsWith("data:")) {
            imageUrl = imageUrl || best[0];
            thumbnailUrl = thumbnailUrl || best[0];
          }
        }
        if (!thumbnailUrl) thumbnailUrl = imageUrl;
        if (!imageUrl) imageUrl = thumbnailUrl;
      }

      // Title: aria-label on the anchor, or img alt, or heading inside card
      let title = (anchor.getAttribute("aria-label") || "").trim();
      if (!title && img) title = (img.alt || "").trim();
      if (!title) {
        const heading = anchor.querySelector("h2, h3, h4, [data-test-id='pin-title']") as HTMLElement | null;
        if (heading) title = (heading.innerText || heading.textContent || "").trim();
      }

      // Description: text content inside the card (excluding title)
      let description = "";
      const descEl = anchor.querySelector(
        "[data-test-id='pin-description'], .richPinDescription, .richPinInformation",
      ) as HTMLElement | null;
      if (descEl) description = (descEl.innerText || descEl.textContent || "").trim();

      // Source domain from nearby elements
      let source = "";
      const sourceEl = anchor.querySelector(
        "[data-test-id='pin-source-domain'], .pinDomain, a[href*='//']:not([href*='pinterest.com'])",
      ) as HTMLElement | null;
      if (sourceEl) {
        const sourceText = (sourceEl.innerText || sourceEl.textContent || "").trim();
        source = sourceText || "";
      }

      // Visible text of card
      const visibleText = (anchor.innerText || anchor.textContent || "")
        .replace(/\s+/g, " ")
        .trim()
        .slice(0, 200);

      results.push({
        title,
        description,
        source,
        pinUrl,
        pageUrl: "",  // external page URL requires pin detail — not fetched here
        imageUrl: imageUrl.startsWith("data:") ? "" : imageUrl,
        thumbnailUrl: thumbnailUrl.startsWith("data:") ? "" : thumbnailUrl,
        visibleText,
      });
    });

    return results;
  });
}
