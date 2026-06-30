import type { Page } from "playwright";
import * as readline from "readline";

// Pinterest cookie consent button selectors
const COOKIE_CONSENT_SELECTORS = [
  'button[data-test-id="acceptCookiesButton"]',
  'button[id="onetrust-accept-btn-handler"]',
  'button[aria-label*="Accept"]',
  'button[aria-label*="accept"]',
  "#accept-all-cookies",
  ".cookie-accept",
];

// Login/signup modal close selectors — only use if modal is dismissible
const MODAL_CLOSE_SELECTORS = [
  'button[aria-label="Close"]',
  'button[data-test-id="closeup-close-button"]',
  '[data-test-id="header-close-button"]',
  'button[class*="closeButton"]',
  'button[class*="CloseButton"]',
  'svg[aria-label="Close"]',
];

// Signals indicating a login wall
const LOGIN_WALL_SIGNALS = [
  "Sign up to see more",
  "Log in to see more",
  "Create an account",
  "Join Pinterest",
  "Continue with Google",
  "Continue with Facebook",
  "Log in",
  "Already a member?",
];

// Signals indicating a CAPTCHA / bot block
const CAPTCHA_SIGNALS = [
  "captcha",
  "CAPTCHA",
  "not a robot",
  "unusual traffic",
  "bot detection",
  "Access denied",
  "403 Forbidden",
];

export type PageState = "ok" | "cookie_consent" | "login_wall" | "captcha" | "blocked" | "error";

export async function detectPageState(page: Page): Promise<PageState> {
  const url = page.url();

  // Redirected to login page
  if (url.includes("pinterest.com/login") || url.includes("pinterest.com/register")) {
    return "login_wall";
  }

  try {
    const bodyText = await page.evaluate(() => document.body?.innerText ?? "");

    // CAPTCHA check first
    for (const signal of CAPTCHA_SIGNALS) {
      if (bodyText.includes(signal)) return "captcha";
    }

    // Cookie consent
    for (const sel of COOKIE_CONSENT_SELECTORS) {
      const el = await page.$(sel).catch(() => null);
      if (el) return "cookie_consent";
    }

    // Login wall in body text
    for (const signal of LOGIN_WALL_SIGNALS) {
      if (bodyText.includes(signal)) return "login_wall";
    }
  } catch {
    // page not ready
  }

  return "ok";
}

export async function handleCookieConsent(page: Page): Promise<boolean> {
  for (const sel of COOKIE_CONSENT_SELECTORS) {
    try {
      const btn = await page.$(sel);
      if (!btn) continue;
      const text = (await btn.textContent()) ?? "";
      if (/accept|allow|ok|agree/i.test(text) || text.trim() === "") {
        await btn.click();
        await page.waitForTimeout(1500);
        return true;
      }
    } catch {
      // continue
    }
  }
  return false;
}

export async function tryDismissLoginModal(page: Page): Promise<boolean> {
  for (const sel of MODAL_CLOSE_SELECTORS) {
    try {
      const btn = await page.$(sel);
      if (!btn) continue;
      await btn.click();
      await page.waitForTimeout(800);
      const stateAfter = await detectPageState(page);
      if (stateAfter !== "login_wall") return true;
    } catch {
      // continue
    }
  }

  // Try pressing Escape
  try {
    await page.keyboard.press("Escape");
    await page.waitForTimeout(800);
    const stateAfter = await detectPageState(page);
    if (stateAfter !== "login_wall") return true;
  } catch {
    // ignore
  }

  return false;
}

export async function waitForUserToHandleBlock(
  page: Page,
  queryId: number,
  reason: string,
): Promise<boolean> {
  // In non-interactive (background) mode there's no one to handle the block — skip it.
  if (!process.stdin.isTTY) {
    console.log(`[non-TTY] Query ${queryId}: ${reason} — marking login_required and continuing.`);
    return false;
  }

  console.log("\n" + "=".repeat(60));
  console.log(`Pinterest block detected on query ${queryId}: ${reason}`);
  console.log("");
  console.log("Please handle the block manually in the open browser window.");
  console.log("After Pinterest search results are visible, press Enter to continue.");
  console.log("Press Ctrl+C to abort this session.");
  console.log("=".repeat(60) + "\n");

  await waitForEnter();

  const state = await detectPageState(page);
  if (state === "ok") return true;
  const url = page.url();
  if (url.includes("pinterest.com/search/pins")) return true;
  return false;
}

function waitForEnter(): Promise<void> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question("", () => {
      rl.close();
      resolve();
    });
  });
}
