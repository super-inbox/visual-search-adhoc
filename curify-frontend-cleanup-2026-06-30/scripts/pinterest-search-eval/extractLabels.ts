import type { Page } from "playwright";
import type { PinterestLabel } from "./types.js";

// Items to exclude from label results
const EXCLUDE_LOWER = new Set([
  "home", "explore", "create", "watch", "log in", "sign up", "sign in",
  "pinterest", "search", "ideas", "save", "share", "more options",
  "more", "all pins", "videos", "people", "boards", "try", "today",
  "following", "for you", "notifications", "inbox", "profile",
  "settings", "help", "about", "privacy", "terms",
]);

function shouldExclude(text: string): boolean {
  const lower = text.toLowerCase().trim();
  if (EXCLUDE_LOWER.has(lower)) return true;
  if (text.length > 100) return true;
  if (text.length < 2) return true;
  if (/^https?:/.test(text)) return true;
  return false;
}

export async function extractLabels(page: Page): Promise<PinterestLabel[]> {
  await tryScrollChipsBar(page);

  const labels: PinterestLabel[] = [];
  const seen = new Set<string>();

  function addLabel(text: string, href: string, type: PinterestLabel["type"]): void {
    const clean = text.trim();
    if (!clean || seen.has(clean.toLowerCase()) || shouldExclude(clean)) return;
    seen.add(clean.toLowerCase());
    labels.push({ text: clean, href: href || "", type });
  }

  // Strategy 1: Pinterest guided search chips
  // These appear as pill-buttons above the search results
  const chipSelectors: Array<{ sel: string; type: PinterestLabel["type"] }> = [
    { sel: '[data-test-id="search-filter-chip"] a', type: "chip" },
    { sel: '[data-test-id="search-filter-chip"]', type: "chip" },
    { sel: '[data-test-id="guided-search-chip"] a', type: "chip" },
    { sel: '[data-test-id="guided-search-chip"]', type: "chip" },
    { sel: '[data-test-id="searchScopeSelector"] a', type: "chip" },
    { sel: '.guidedSearch a', type: "chip" },
    { sel: '[data-test-id="search-refinements"] a', type: "related" },
    { sel: '[data-test-id="related-searches"] a', type: "related" },
    { sel: 'div[role="list"] a[href*="/search/pins"]', type: "chip" },
  ];

  for (const { sel, type } of chipSelectors) {
    try {
      const els = await page.$$(sel);
      for (const el of els) {
        const text = (await el.innerText().catch(() => el.textContent()))?.trim() ?? "";
        const href = (await el.getAttribute("href")) ?? "";
        addLabel(text, href, type);
      }
    } catch {
      // continue
    }
  }

  // Strategy 2: Evaluate-based scan for chip-like elements
  // No inner const-arrow-function assignments — avoids esbuild __name injection
  if (labels.length === 0) {
    const evalLabels = await page.evaluate(() => {
      const found: Array<{ text: string; href: string }> = [];
      const seenLower = new Set<string>();

      // Look for search-pin links that look like chip labels (short text, not in a pin card)
      const candidates = document.querySelectorAll('a[href*="/search/pins"]');
      candidates.forEach((el) => {
        if (found.length >= 50) return;
        const anchor = el as HTMLAnchorElement;
        const text = (anchor.innerText || anchor.textContent || "").trim();
        if (!text || text.length < 2 || text.length > 80) return;

        // Skip if inside a pin card or board result
        if (anchor.closest('[data-test-id="pin"]')) return;
        if (anchor.closest('[data-test-id="pinWrapper"]')) return;
        if (anchor.closest('[data-test-id="board-card"]')) return;
        if (anchor.closest('[data-test-id="boardCard"]')) return;

        // Skip pin detail links (long URLs with numeric pin IDs)
        const href = anchor.href || "";
        if (/\/pin\/\d+/.test(href)) return;

        const lower = text.toLowerCase();
        if (seenLower.has(lower)) return;
        seenLower.add(lower);
        found.push({ text, href });
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
  try {
    await page.evaluate(() => {
      // Pinterest guided search / filter chip containers
      const selectors = [
        '[data-test-id="search-filter-chip"]',
        '[data-test-id="guided-search-chip"]',
        ".guidedSearch",
        '[data-test-id="search-refinements"]',
      ];
      selectors.forEach((sel) => {
        const el = document.querySelector(sel);
        if (el) {
          const parent = el.parentElement;
          if (parent) (parent as HTMLElement).scrollLeft += 800;
        }
      });
    });
    await page.waitForTimeout(400);
  } catch {
    // ignore
  }
}
