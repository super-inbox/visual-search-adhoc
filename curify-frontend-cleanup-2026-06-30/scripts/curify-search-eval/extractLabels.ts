import type { Page } from "playwright";
import type { LabelEntry } from "./types.js";

// Text to skip — navigation items and action buttons
const SKIP_TEXT_LOWER = new Set([
  "sign in", "sign up", "log in", "login", "register",
  "english", "中文", "español", "français", "deutsch", "日本語",
  "home", "templates", "topics", "explore", "generate", "remix",
  "copy", "download", "share", "edit", "open", "create", "start",
  "browse all", "view all", "see all", "load more", "show more",
  "remove", "clear", "back", "next", "previous",
  "privacy policy", "terms", "contact", "about", "help", "feedback",
  "©", "all rights reserved",
]);

function shouldSkip(text: string): boolean {
  const lower = text.toLowerCase().trim();
  if (!lower || lower.length < 2) return true;
  if (lower.length > 120) return true;
  if (SKIP_TEXT_LOWER.has(lower)) return true;
  // Skip pure numbers
  if (/^\d+$/.test(lower)) return true;
  return false;
}

export async function extractLabels(page: Page): Promise<LabelEntry[]> {
  const labels: LabelEntry[] = [];

  // 1. Cluster chips: a[href*="intent="]
  try {
    const chipLinks = await page.$$('a[href*="intent="]');
    for (const el of chipLinks) {
      const text = (await el.textContent())?.trim();
      if (!text || shouldSkip(text)) continue;
      const href = (await el.getAttribute("href")) ?? "";
      const normalized = normalizeText(text);
      if (!labels.some((l) => l.href === href)) {
        labels.push({ text: normalized, type: "chip", href });
      }
    }
  } catch {
    // ignore
  }

  // 2. Topic chips: a[href*="within="]
  try {
    const withinLinks = await page.$$('a[href*="within="]');
    for (const el of withinLinks) {
      const text = (await el.textContent())?.trim();
      if (!text || shouldSkip(text)) continue;
      const href = (await el.getAttribute("href")) ?? "";
      const normalized = normalizeText(text);
      if (!labels.some((l) => l.href === href)) {
        labels.push({ text: normalized, type: "topic", href });
      }
    }
  } catch {
    // ignore
  }

  // 3. Related topics at the bottom: links to /topics/ that are NOT result cards
  try {
    const topicLinks = await page.$$('a[href*="/topics/"]');
    for (const el of topicLinks) {
      const text = (await el.textContent())?.trim();
      if (!text || shouldSkip(text)) continue;
      const href = (await el.getAttribute("href")) ?? "";
      // Skip result card links (they go to /nano-template/ not /topics/)
      if (href.includes("/nano-template/")) continue;
      // Skip active filter pill links (they point back to /search?q=)
      if (href.includes("/search?q=")) continue;
      const normalized = normalizeText(text);
      if (!labels.some((l) => l.href === href)) {
        labels.push({ text: normalized, type: "suggestion", href });
      }
    }
  } catch {
    // ignore
  }

  // 4. On /topics/<slug> pages (redirect target), grab topic navigation chips
  try {
    const currentUrl = page.url();
    if (currentUrl.includes("/topics/")) {
      // On topic pages, look for related topic pills / chip rows
      const navLinks = await page.$$('a[href*="/topics/"]');
      for (const el of navLinks) {
        const text = (await el.textContent())?.trim();
        if (!text || shouldSkip(text)) continue;
        const href = (await el.getAttribute("href")) ?? "";
        const normalized = normalizeText(text);
        if (!labels.some((l) => l.href === href)) {
          labels.push({ text: normalized, type: "topic", href });
        }
      }
    }
  } catch {
    // ignore
  }

  return labels;
}

function normalizeText(raw: string): string {
  // Collapse whitespace and strip chip count badges (e.g. "Vocabulary 12" → "Vocabulary 12")
  return raw.replace(/\s+/g, " ").trim();
}
