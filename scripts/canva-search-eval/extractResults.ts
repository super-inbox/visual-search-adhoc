import type { Page } from "playwright";
import type { CanvaTemplateResult } from "./types.js";

const MAX_SCROLLS = 3;
const SCROLL_STEP = 900;
const SCROLL_WAIT_MS = 1500;

/**
 * Extract top-10 template results from Canva template search page.
 * Reads from DOM attributes — no clicking into editor or detail pages.
 */
export async function extractTop10(
  page: Page,
  onNote?: (rank: number, note: string) => void,
): Promise<CanvaTemplateResult[]> {
  const tiles = await scrollAndCollect(page, 10);
  const results: CanvaTemplateResult[] = [];

  for (const tile of tiles.slice(0, 10)) {
    const rank = results.length + 1;
    const result: CanvaTemplateResult = {
      rank,
      title: tile.title,
      description: tile.description,
      source: "Canva",
      templateUrl: tile.templateUrl,
      pageUrl: tile.pageUrl,
      imageUrl: tile.imageUrl,
      thumbnailUrl: tile.thumbnailUrl,
      visibleText: tile.visibleText,
      isPro: tile.isPro,
    };
    if (!result.templateUrl) onNote?.(rank, "templateUrl empty");
    if (!result.title) onNote?.(rank, "title empty");
    results.push(result);
  }

  return results;
}

interface TemplateTileData {
  title: string;
  description: string;
  templateUrl: string;
  pageUrl: string;
  imageUrl: string;
  thumbnailUrl: string;
  visibleText: string;
  isPro: boolean;
}

async function scrollAndCollect(page: Page, needed: number): Promise<TemplateTileData[]> {
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

async function extractTiles(page: Page): Promise<TemplateTileData[]> {
  return page.evaluate(() => {
    const results: Array<{
      title: string; description: string;
      templateUrl: string; pageUrl: string;
      imageUrl: string; thumbnailUrl: string;
      visibleText: string; isPro: boolean;
    }> = [];
    const seenUrls = new Set<string>();

    // Canva template links typically point to /templates/<slug> pages
    // We target anchors inside template card containers
    const templateAnchors = Array.from(document.querySelectorAll(
      'a[href*="/templates/"], a[href*="/design/"]',
    ));

    for (const el of templateAnchors) {
      if (results.length >= 20) break;
      const anchor = el as HTMLAnchorElement;
      const href = anchor.href || anchor.getAttribute("href") || "";
      if (!href) continue;

      let templateUrl = "";
      try {
        templateUrl = new URL(href, location.origin).href;
      } catch {
        templateUrl = href;
      }

      // Skip non-template pages (category pages, search pages, short slugs)
      // Template pages have a slug with ID suffix or are /design/ pages
      const isTemplateLink =
        /\/templates\/[^?#\/]{10,}/.test(templateUrl) ||
        /\/design\/[^?#]{5,}/.test(templateUrl);
      if (!isTemplateLink) continue;

      // Skip login/editor/account pages
      if (/\/login|\/signup|\/account|\/pricing|\/about/.test(templateUrl)) continue;

      // Deduplicate by URL
      const normalizedUrl = templateUrl.split("?")[0].replace(/\/$/, "");
      if (seenUrls.has(normalizedUrl)) continue;
      seenUrls.add(normalizedUrl);

      // Image extraction from within the card
      const img = anchor.querySelector("img") as HTMLImageElement | null;
      let imageUrl = "";
      let thumbnailUrl = "";
      if (img) {
        const src = img.src || img.getAttribute("data-src") || img.getAttribute("src") || "";
        if (src && !src.startsWith("data:") && !src.startsWith("blob:")) {
          imageUrl = src;
          thumbnailUrl = src;
        }
        const srcset = img.srcset || img.getAttribute("srcset") || "";
        if (srcset) {
          const parts = srcset.split(",").map((s) => s.trim().split(/\s+/));
          const best = parts.sort((a, b) => {
            const wa = parseFloat((a[1] || "0").replace(/[^\d.]/g, "")) || 0;
            const wb = parseFloat((b[1] || "0").replace(/[^\d.]/g, "")) || 0;
            return wb - wa;
          })[0];
          if (best?.[0] && !best[0].startsWith("data:") && !best[0].startsWith("blob:")) {
            imageUrl = imageUrl || best[0];
            thumbnailUrl = thumbnailUrl || best[0];
          }
        }
      }

      // Title: aria-label on anchor, img alt, heading inside card, or data attributes
      let title = (anchor.getAttribute("aria-label") || "").trim();
      if (!title && img) title = (img.alt || "").trim();
      if (!title) {
        const heading = anchor.querySelector("h2, h3, h4, h5, [class*='title'], [class*='Title'], [class*='name'], [class*='Name']") as HTMLElement | null;
        if (heading) title = (heading.innerText || heading.textContent || "").trim();
      }
      if (!title) {
        // Try data attributes
        title = (
          anchor.getAttribute("data-name") ||
          anchor.getAttribute("data-title") ||
          anchor.getAttribute("title") ||
          ""
        ).trim();
      }

      // Description: look for description/subtitle elements inside anchor
      let description = "";
      const descEl = anchor.querySelector(
        '[class*="description"], [class*="Description"], [class*="subtitle"], [class*="Subtitle"], [class*="caption"], [class*="Caption"]',
      ) as HTMLElement | null;
      if (descEl) {
        description = (descEl.innerText || descEl.textContent || "").trim();
      }

      // isPro: look for Pro badge, crown icon, or "Pro" text in card
      const cardEl = anchor.closest('[class*="card"], [class*="Card"], [class*="template"], [class*="Template"], li, [role="listitem"]') || anchor;
      const cardText = (cardEl as HTMLElement).innerText || (cardEl as HTMLElement).textContent || "";
      const isPro =
        cardText.includes("Pro") ||
        !!cardEl.querySelector('[class*="pro"], [class*="Pro"], [class*="premium"], [class*="Premium"], [aria-label*="Pro"], [title*="Pro"]');

      // Visible text of the card (trimmed)
      const visibleText = (anchor.innerText || anchor.textContent || "")
        .replace(/\s+/g, " ")
        .trim()
        .slice(0, 200);

      results.push({
        title,
        description,
        templateUrl: imageUrl.startsWith("data:") ? templateUrl : templateUrl,
        pageUrl: templateUrl, // same as templateUrl since we don't follow links
        imageUrl: (imageUrl && !imageUrl.startsWith("data:") && !imageUrl.startsWith("blob:")) ? imageUrl : "",
        thumbnailUrl: (thumbnailUrl && !thumbnailUrl.startsWith("data:") && !thumbnailUrl.startsWith("blob:")) ? thumbnailUrl : "",
        visibleText,
        isPro,
      });
    }

    return results;
  });
}
