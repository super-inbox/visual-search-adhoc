import type { Page } from "playwright";
import type { BingLabel } from "./types.js";

// Navigation tabs and UI chrome to exclude (case-insensitive)
const EXCLUDE_LOWER = new Set([
  "images", "videos", "maps", "news", "shopping", "more", "search",
  "web", "all", "sign in", "sign out", "settings", "safesearch",
  "filter", "tools", "feedback", "privacy", "terms",
  "microsoft", "bing", "help", "report", "close", "clear",
]);

function shouldExclude(text: string): boolean {
  const lower = text.toLowerCase().trim();
  if (EXCLUDE_LOWER.has(lower)) return true;
  if (text.length > 100) return true;
  if (text.length < 2) return true;
  return false;
}

export async function extractLabels(page: Page): Promise<BingLabel[]> {
  await tryScrollChipsBar(page);

  const labels: BingLabel[] = [];
  const seen = new Set<string>();

  function addLabel(text: string, href: string, type: BingLabel["type"]): void {
    const clean = text.trim();
    if (!clean || seen.has(clean.toLowerCase()) || shouldExclude(clean)) return;
    seen.add(clean.toLowerCase());
    labels.push({ text: clean, href: href || "", type });
  }

  // Strategy 1: Bing Images pivot / chip bar (topic chips above results)
  const chipSelectors: Array<{ sel: string; type: BingLabel["type"] }> = [
    { sel: ".pivotA a", type: "chip" },
    { sel: ".b_pivotA a", type: "chip" },
    { sel: ".qpvt a", type: "chip" },
    { sel: "a.piv_btn", type: "chip" },
    { sel: "#b_imagingFilters a", type: "filter" },
    { sel: ".qfilt a", type: "filter" },
    { sel: ".b_filters a", type: "filter" },
    { sel: ".chips a", type: "chip" },
    { sel: ".b_imgflt a", type: "filter" },
  ];

  for (const { sel, type } of chipSelectors) {
    try {
      const els = await page.$$(sel);
      for (const el of els) {
        const text = (await el.textContent())?.trim() ?? "";
        const href = (await el.getAttribute("href")) ?? "";
        addLabel(text, href, type);
      }
    } catch {
      // continue
    }
  }

  // Strategy 2: Related searches section (below image grid)
  const relatedSelectors: Array<{ sel: string; type: BingLabel["type"] }> = [
    { sel: "#b_context .b_rs a", type: "related" },
    { sel: "#b_results .b_rs a", type: "related" },
    { sel: ".b_rs a", type: "related" },
    { sel: ".b_relSearches a", type: "related" },
  ];

  for (const { sel, type } of relatedSelectors) {
    try {
      const els = await page.$$(sel);
      for (const el of els) {
        const text = (await el.textContent())?.trim() ?? "";
        const href = (await el.getAttribute("href")) ?? "";
        addLabel(text, href, type);
      }
    } catch {
      // continue
    }
  }

  // Strategy 3: Fallback evaluate-based scan.
  // NOTE: No inner const-arrow-function assignments — avoids esbuild __name injection.
  if (labels.length === 0) {
    const evalLabels = await page.evaluate(() => {
      const found: Array<{ text: string; href: string }> = [];
      const seenLower = new Set<string>();

      const allAnchors = document.querySelectorAll('a[href*="images/search"]');
      allAnchors.forEach((el) => {
        if (found.length >= 40) return;
        const anchor = el as HTMLAnchorElement;
        const text = (anchor.innerText || anchor.textContent || "").trim();
        if (!text || text.length < 2 || text.length > 80) return;

        // Skip if inside an image result tile or pagination
        if (anchor.closest(".iusc") || anchor.closest(".inflnk") || anchor.closest(".b_pag")) return;
        if (anchor.closest("#b_results li.b_algo")) return;

        // Skip if text looks like a URL
        if (/^https?:/.test(text)) return;

        const lower = text.toLowerCase();
        if (seenLower.has(lower)) return;
        seenLower.add(lower);
        found.push({ text, href: anchor.href });
      });
      return found;
    });

    for (const { text, href } of evalLabels) {
      addLabel(text, href, "unknown");
    }
  }

  return labels;
}

async function tryScrollChipsBar(page: Page): Promise<void> {
  // Inline — no inner helper functions — avoids esbuild __name injection
  try {
    await page.evaluate(() => {
      const selectors = [".pivotA", ".b_pivotA", "#b_imagingFilters", ".qpvt", ".chips"];
      selectors.forEach((sel) => {
        const el = document.querySelector(sel);
        if (el) (el as HTMLElement).scrollLeft += 800;
      });
    });
    await page.waitForTimeout(400);
    await page.evaluate(() => {
      const selectors = [".pivotA", ".b_pivotA", "#b_imagingFilters", ".qpvt", ".chips"];
      selectors.forEach((sel) => {
        const el = document.querySelector(sel);
        if (el) (el as HTMLElement).scrollLeft += 800;
      });
    });
    await page.waitForTimeout(300);
  } catch {
    // ignore
  }
}
