import type { Page } from "playwright";
import type { ResultEntry } from "./types.js";

const MAX_RESULTS = 10;
const SCROLL_STEP = 900;
const SCROLL_WAIT_MS = 1500;
const MAX_SCROLLS = 5;

interface RawCard {
  title: string;
  subtitle: string;
  href: string;
  imageUrl: string;
  templateId: string;
  templateName: string;
  sourceType: "inspiration" | "template" | "unknown";
  visibleText: string;
}

/**
 * Extract top-10 search results from the Curify search page.
 * Collects from the Examples grid (inspirations) first, then
 * Templates rail, until 10 unique results are found.
 */
export async function extractTop10(
  page: Page,
  onNote?: (rank: number, note: string) => void,
): Promise<ResultEntry[]> {
  // Scroll to ensure results are loaded
  await scrollToLoadResults(page);

  // Collect from both sections
  const inspirations = await extractInspirationCards(page);
  const templates = await extractTemplateCards(page);

  // Merge, deduplicate by href, cap at 10
  const seen = new Set<string>();
  const merged: RawCard[] = [];

  for (const card of [...inspirations, ...templates]) {
    const key = card.href || card.title;
    if (!key) continue;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(card);
    if (merged.length >= MAX_RESULTS) break;
  }

  return merged.slice(0, MAX_RESULTS).map((card, i) => {
    const rank = i + 1;
    if (!card.href) onNote?.(rank, "href missing");
    return {
      rank,
      title: card.title,
      subtitle: card.subtitle,
      templateId: card.templateId,
      templateName: card.templateName,
      href: card.href,
      imageUrl: card.imageUrl,
      sourceType: card.sourceType,
      visibleText: card.visibleText,
    };
  });
}

async function scrollToLoadResults(page: Page): Promise<void> {
  for (let i = 0; i < MAX_SCROLLS; i++) {
    const prevHeight = await page.evaluate(() => document.body.scrollHeight);
    await page.evaluate((step) => window.scrollBy(0, step), SCROLL_STEP);
    await page.waitForTimeout(SCROLL_WAIT_MS);
    const newHeight = await page.evaluate(() => document.body.scrollHeight);
    if (newHeight === prevHeight) break;
  }
  // Scroll back to top
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(500);
}

async function extractInspirationCards(page: Page): Promise<RawCard[]> {
  return page.evaluate(() => {
    const cards: Array<{
      title: string;
      subtitle: string;
      href: string;
      imageUrl: string;
      templateId: string;
      templateName: string;
      sourceType: "inspiration" | "template" | "unknown";
      visibleText: string;
    }> = [];

    // Find the "Examples" section by h2 heading
    const sections = document.querySelectorAll("section");
    let examplesSection: Element | null = null;
    for (const section of sections) {
      const h2 = section.querySelector("h2");
      if (h2 && h2.textContent?.trim().toLowerCase() === "examples") {
        examplesSection = section;
        break;
      }
    }

    if (!examplesSection) {
      // Fallback: try all cards with example-shaped hrefs on the page
      const exampleLinks = document.querySelectorAll('a[href*="/nano-template/"][href*="/example/"]');
      if (exampleLinks.length > 0) {
        // Build cards from example links
        const seen = new Set<string>();
        for (const link of exampleLinks) {
          const href = (link as HTMLAnchorElement).href;
          if (seen.has(href)) continue;
          seen.add(href);
          const cardEl = link.closest("div.group") ?? link.closest("div");
          const img = cardEl?.querySelector("img");
          const title = img?.alt?.trim() ?? link.textContent?.trim() ?? "";
          const templateId = extractTemplateIdFromHref(href);
          cards.push({
            title,
            subtitle: "",
            href,
            imageUrl: img?.src ?? "",
            templateId,
            templateName: "",
            sourceType: "inspiration",
            visibleText: title,
          });
        }
        return cards;
      }
      return cards;
    }

    // Find all card containers within the examples section
    // Cards are: div.group.rounded-3xl or div[class*="rounded-3xl"][class*="border"]
    const cardEls = examplesSection.querySelectorAll(
      "div.group, div[class*='rounded-3xl']"
    );

    for (const card of cardEls) {
      // Get the primary link (example page link or carousel link)
      const exLink = card.querySelector<HTMLAnchorElement>(
        'a[href*="/nano-template/"][href*="/example/"]'
      );
      const carouselLink = card.querySelector<HTMLAnchorElement>(
        'a[href*="/carousel/template-example/"]'
      );
      const primaryLink = exLink ?? carouselLink;
      if (!primaryLink) continue;

      const href = primaryLink.href;
      const img = card.querySelector("img");
      const title = img?.alt?.trim() ?? "";

      // Caption text (below image)
      const captionEl = card.querySelector(
        "div.px-3.pt-2, p.text-xs, div.text-xs"
      );
      const subtitle = captionEl?.textContent?.trim() ?? "";

      const templateId = extractTemplateIdFromHref(href);

      cards.push({
        title,
        subtitle,
        href,
        imageUrl: img?.src ?? "",
        templateId,
        templateName: "",
        sourceType: "inspiration",
        visibleText: [title, subtitle].filter(Boolean).join(" | "),
      });
    }

    return cards;

    function extractTemplateIdFromHref(href: string): string {
      // /en/nano-template/<template-slug>/example/<id>
      const m = href.match(/\/nano-template\/([^/]+)\/example\//);
      if (m) return m[1];
      // /en/carousel/template-example/<template-slug>/<id>
      const m2 = href.match(/\/carousel\/template-example\/([^/]+)\//);
      if (m2) return m2[1];
      return "";
    }
  });
}

async function extractTemplateCards(page: Page): Promise<RawCard[]> {
  return page.evaluate(() => {
    const cards: Array<{
      title: string;
      subtitle: string;
      href: string;
      imageUrl: string;
      templateId: string;
      templateName: string;
      sourceType: "inspiration" | "template" | "unknown";
      visibleText: string;
    }> = [];

    // Find the "Templates" section by h2 heading
    const sections = document.querySelectorAll("section");
    let templatesSection: Element | null = null;
    for (const section of sections) {
      const h2 = section.querySelector("h2");
      if (h2 && h2.textContent?.trim().toLowerCase() === "templates") {
        templatesSection = section;
        break;
      }
    }
    if (!templatesSection) return cards;

    // Template cards: links to /nano-template/<slug> (not /example/)
    const templateLinks = templatesSection.querySelectorAll<HTMLAnchorElement>(
      'a[href*="/nano-template/"]'
    );
    const seen = new Set<string>();

    for (const link of templateLinks) {
      const href = link.href;
      // Skip example links within template rail
      if (href.includes("/example/")) continue;
      // Skip carousel links
      if (href.includes("/carousel/")) continue;
      // Skip #reproduce anchor
      const cleanHref = href.split("#")[0];
      if (seen.has(cleanHref)) continue;
      seen.add(cleanHref);

      const cardEl = link.closest("div.group") ?? link.closest("article") ?? link.closest("div");
      const img = cardEl?.querySelector("img");
      const title = img?.alt?.trim() ?? link.textContent?.trim() ?? "";

      // Template name from text
      const nameEl = cardEl?.querySelector("h3, h4, p.font-semibold, div.font-semibold");
      const templateName = nameEl?.textContent?.trim() ?? "";

      // Extract template slug from href
      const m = href.match(/\/nano-template\/([^/?#]+)/);
      const templateId = m ? m[1] : "";

      cards.push({
        title: title || templateName,
        subtitle: "",
        href: cleanHref,
        imageUrl: img?.src ?? "",
        templateId,
        templateName,
        sourceType: "template",
        visibleText: [title, templateName].filter(Boolean).join(" | "),
      });
    }

    return cards;
  });
}
