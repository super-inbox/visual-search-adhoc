import type { Page } from "playwright";

// Known Google search navigation items to exclude (case-insensitive)
const NAV_LOWER = new Set([
  "ai mode", "all", "images", "videos", "shopping", "forums",
  "short videos", "more", "tools", "news", "web", "flights",
  "finance", "books", "maps", "podcasts", "search labs", "gemini",
  "search", "sign in", "settings",
]);

export async function extractLabels(page: Page): Promise<string[]> {
  await tryScrollChipsBar(page);

  const labels: string[] = [];

  // 2026 Google Images: topic chips are [role="listitem"] a links
  // after the main navigation row
  try {
    const elements = await page.$$('[role="listitem"] a, [role="list"] a');
    for (const el of elements) {
      const text = (await el.textContent())?.trim();
      if (!text || text.length < 1) continue;
      if (NAV_LOWER.has(text.toLowerCase())) continue;
      if (text.length > 80) continue; // skip very long items (not chips)
      if (!labels.includes(text)) {
        labels.push(text);
      }
    }
  } catch {
    // ignore and fall through to older selectors
  }

  if (labels.length > 0) return labels;

  // Fallback: older chip selectors
  const FALLBACK_SELECTORS = [
    'div[role="list"] g-scrolling-carousel a',
    'g-scrolling-carousel a[href*="tbm=isch"]',
    'g-scrolling-carousel a[href*="udm=2"]',
    'a.HJ81nd',
    'a.T7qlbe',
    '.qF20Ie a',
    'div[data-chip-id] a',
  ];

  for (const selector of FALLBACK_SELECTORS) {
    try {
      const elements = await page.$$(selector);
      if (elements.length === 0) continue;
      for (const el of elements) {
        const text = (await el.textContent())?.trim();
        if (!text || text.length < 1) continue;
        if (NAV_LOWER.has(text.toLowerCase())) continue;
        if (!labels.includes(text)) labels.push(text);
      }
      if (labels.length > 0) break;
    } catch {
      // try next selector
    }
  }

  return labels;
}

async function tryScrollChipsBar(page: Page): Promise<void> {
  try {
    await page.evaluate(() => {
      const carousel = document.querySelector("g-scrolling-carousel");
      if (carousel) (carousel as HTMLElement).scrollLeft += 600;
      // Also try new chips container
      const listEl = document.querySelector('[role="list"]');
      if (listEl) (listEl as HTMLElement).scrollLeft += 600;
    });
    await page.waitForTimeout(400);
  } catch {
    // ignore
  }
}
