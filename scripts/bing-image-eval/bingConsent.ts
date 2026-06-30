import type { Page } from "playwright";
import * as readline from "readline";

// Text signals indicating Bing is blocked or showing consent
const BLOCK_SIGNALS = [
  "unusual activity",
  "automated queries",
  "not a robot",
  "CAPTCHA",
  "security check",
  "To continue, complete",
  "异常流量",
];

const CONSENT_TEXT_SIGNALS = [
  "consent.microsoft.com",
  "We care about your privacy",
  "Microsoft and partners",
  "Manage preferences",
  "Accept all",
  "Reject all",
];

// Cookie consent accept button selectors
const CONSENT_BTN_SELECTORS = [
  "#bnp_btn_accept",
  "button#bnp_btn_accept",
  '[id="bnp_btn_accept"]',
  'button[aria-label*="Accept"]',
  'button[title*="Accept"]',
  "#accept-button",
];

export async function handleCookieConsent(page: Page): Promise<boolean> {
  for (const sel of CONSENT_BTN_SELECTORS) {
    try {
      const btn = await page.$(sel);
      if (!btn) continue;
      const text = (await btn.textContent()) ?? "";
      if (/accept|agree|allow|ok/i.test(text)) {
        await btn.click();
        await page.waitForTimeout(2000);
        return true;
      }
    } catch {
      // try next
    }
  }
  return false;
}

export async function detectBlockOrConsent(page: Page): Promise<"blocked" | "consent" | "ok"> {
  const url = page.url();

  // Consent redirect
  if (url.includes("consent.microsoft.com") || url.includes("login.microsoftonline.com")) {
    return "consent";
  }

  try {
    const bodyText = await page.evaluate(() => document.body?.innerText ?? "");

    for (const signal of CONSENT_TEXT_SIGNALS) {
      if (bodyText.includes(signal)) {
        // Try to auto-click consent
        const clicked = await handleCookieConsent(page);
        if (clicked) {
          await page.waitForTimeout(2000);
          return "ok";
        }
        return "consent";
      }
    }

    for (const signal of BLOCK_SIGNALS) {
      if (bodyText.includes(signal)) return "blocked";
    }
  } catch {
    // page may not be ready
  }

  return "ok";
}

export async function waitForUserToUnblock(page: Page, queryId: number): Promise<boolean> {
  console.log("\n" + "=".repeat(60));
  console.log(`Bing block/CAPTCHA detected on query ${queryId}.`);
  console.log("");
  console.log("Please resolve the block manually in the open browser window.");
  console.log("After Bing Images results are visible, press Enter to continue.");
  console.log("Press Ctrl+C to abort this session.");
  console.log("=".repeat(60) + "\n");

  await waitForEnter();

  const state = await detectBlockOrConsent(page);
  if (state !== "ok") {
    const url = page.url();
    // If we're on bing images search, treat as resolved
    if (url.includes("bing.com/images/search")) return true;
    return false;
  }
  return true;
}

function waitForEnter(): Promise<void> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question("", () => { rl.close(); resolve(); });
  });
}
