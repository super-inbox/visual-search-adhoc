import type { Page } from "playwright";
import type { CanvaLabel } from "./types.js";

// Items to exclude — navigation, auth, generic UI chrome
const EXCLUDE_LOWER = new Set([
  "home", "explore", "create", "watch", "log in", "sign up", "sign in",
  "canva", "canva pro", "try canva pro", "get canva pro", "upgrade",
  "search", "ideas", "save", "share", "more", "more options",
  "templates", "photos", "elements", "text", "brand", "apps",
  "settings", "help", "about", "privacy", "terms", "pricing",
  "features", "education", "business", "enterprise", "nonprofit",
  "what's new", "whats new", "see all", "view all", "show all",
  "back", "next", "previous", "load more", "see more",
  "create a design", "start designing", "use template", "edit this template",
  "customize this template", "copy template",
  "all", "filters", "sort", "sort by",
  "notifications", "inbox", "profile", "account",
  "free", "pro", "start for free",
]);

function shouldExclude(text: string): boolean {
  const lower = text.toLowerCase().trim();
  if (EXCLUDE_LOWER.has(lower)) return true;
  if (text.length > 100) return true;
  if (text.length < 2) return true;
  if (/^https?:/.test(text)) return true;
  // Skip numeric-only
  if (/^\d+$/.test(text)) return true;
  return false;
}

export async function extractLabels(page: Page): Promise<CanvaLabel[]> {
  const labels: CanvaLabel[] = [];
  const seen = new Set<string>();

  function addLabel(text: string, href: string, type: CanvaLabel["type"]): void {
    const clean = text.trim().replace(/\s+/g, " ");
    if (!clean || seen.has(clean.toLowerCase()) || shouldExclude(clean)) return;
    seen.add(clean.toLowerCase());
    labels.push({ text: clean, href: href || "", type });
  }

  // Strategy 1: Design-type filter chips / category tabs
  // Canva template search often has a row of design-type pills or tabs
  const chipSelectors: Array<{ sel: string; type: CanvaLabel["type"] }> = [
    // Filter chips / design type pills
    { sel: '[data-testid="filter-chip"] a', type: "filter" },
    { sel: '[data-testid="filter-chip"]', type: "filter" },
    { sel: '[data-testid="search-filter"] a', type: "filter" },
    { sel: '[data-testid="search-filter"]', type: "filter" },
    { sel: '[data-testid="category-chip"] a', type: "category" },
    { sel: '[data-testid="category-chip"]', type: "category" },
    // Tab bar (Templates / Photos / Elements / etc.)
    { sel: '[role="tab"] a', type: "chip" },
    { sel: '[role="tab"]', type: "chip" },
    // Related searches / suggestions
    { sel: '[data-testid="related-searches"] a', type: "related" },
    { sel: '[data-testid="search-suggestions"] a', type: "related" },
    // Generic pill/chip elements that look like filter chips
    { sel: 'a[href*="/templates/"][class*="chip"]', type: "chip" },
    { sel: 'a[href*="/templates/"][class*="pill"]', type: "chip" },
    { sel: 'a[href*="/templates/"][class*="filter"]', type: "filter" },
    { sel: 'a[href*="/templates/"][class*="category"]', type: "category" },
    { sel: 'a[href*="/templates/"][class*="tag"]', type: "chip" },
    // Canva nav refinement links inside search context
    { sel: '[class*="SearchFilter"] a', type: "filter" },
    { sel: '[class*="searchFilter"] a', type: "filter" },
    { sel: '[class*="FilterChip"] a', type: "filter" },
    { sel: '[class*="filterChip"] a', type: "filter" },
    { sel: '[class*="CategoryChip"] a', type: "category" },
    { sel: '[class*="categoryChip"] a', type: "category" },
    { sel: '[class*="RelatedSearch"] a', type: "related" },
    { sel: '[class*="relatedSearch"] a', type: "related" },
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

  // Strategy 2: Evaluate-based scan — find template-category links that look like chips
  // (short text, not inside a template card, pointing to /templates/)
  if (labels.length < 3) {
    const evalLabels = await page.evaluate(() => {
      const found: Array<{ text: string; href: string }> = [];
      const seenLower = new Set<string>();

      const candidates = document.querySelectorAll('a[href*="/templates/"]');
      candidates.forEach((el) => {
        if (found.length >= 60) return;
        const anchor = el as HTMLAnchorElement;
        const text = (anchor.innerText || anchor.textContent || "").trim().replace(/\s+/g, " ");
        if (!text || text.length < 2 || text.length > 80) return;

        // Skip if inside a template card (these are result items, not chips)
        // Canva template cards tend to be in grid containers
        const card = anchor.closest('[data-testid*="template"], [class*="TemplateCard"], [class*="templateCard"]');
        if (card) return;

        // Skip very long hrefs that look like individual template pages
        const href = anchor.href || "";
        // Template-specific pages have slugs like /templates/some-long-slug-1234/
        // Category/filter pages typically have shorter or query-style URLs
        if (/\/templates\/[^?#]+\/[a-zA-Z0-9_-]{20,}/.test(href)) return;

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
