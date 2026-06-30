import type { Page } from "playwright";
import * as readline from "readline";
import { CONSENT_SELECTORS, CAPTCHA_INDICATORS } from "./selectors.js";

const CAPTCHA_TEXT_SIGNALS = [
  "Before you continue",
  "Accept all",
  "I agree",
  "unusual traffic",
  "automated queries",
  "Our systems have detected",
  "CAPTCHA",
  "reCAPTCHA",
  "not a robot",
  "异常流量",
  "自动查询",
];

export async function handleConsent(page: Page): Promise<boolean> {
  for (const selector of CONSENT_SELECTORS) {
    try {
      const btn = await page.$(selector);
      if (btn) {
        const text = (await btn.textContent()) ?? "";
        // Only click "Accept" style buttons, not reject
        if (/accept|agree|确认|同意/i.test(text)) {
          await btn.click();
          await page.waitForTimeout(2000);
          return true;
        }
      }
    } catch {
      // continue trying
    }
  }
  return false;
}

export async function detectCaptchaOrBlock(page: Page): Promise<boolean> {
  // Check DOM indicators
  for (const selector of CAPTCHA_INDICATORS) {
    try {
      const el = await page.$(selector);
      if (el) return true;
    } catch {
      // continue
    }
  }

  // Check page text
  try {
    const bodyText = await page.evaluate(() => document.body?.innerText ?? "");
    for (const signal of CAPTCHA_TEXT_SIGNALS) {
      if (bodyText.includes(signal)) {
        // Distinguish consent page from actual CAPTCHA
        if (signal === "Before you continue" || signal === "Accept all" || signal === "I agree") {
          // Try auto-consent first
          const consented = await handleConsent(page);
          if (consented) return false;
        }
        return true;
      }
    }
  } catch {
    // page may not be ready
  }

  return false;
}

export async function waitForUserToClearCaptcha(page: Page, queryId: number): Promise<boolean> {
  console.log("\n" + "=".repeat(60));
  console.log("Google verification detected.");
  console.log("");
  console.log("Please complete the verification manually in the open browser.");
  console.log("");
  console.log("After the Google Images result page is visible again,");
  console.log("return to this terminal and press Enter.");
  console.log("=".repeat(60) + "\n");

  await waitForEnter();

  // Re-check after user confirms
  const stillBlocked = await detectCaptchaOrBlock(page);
  if (stillBlocked) {
    console.log("Still detecting verification page. Checking URL...");
    const url = page.url();
    console.log("Current URL:", url);
    // If user is on Google Images, treat as resolved
    if (url.includes("google.com/search") && url.includes("tbm=isch")) {
      return true;
    }
    return false;
  }
  return true;
}

function waitForEnter(): Promise<void> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    rl.question("", () => {
      rl.close();
      resolve();
    });
  });
}
