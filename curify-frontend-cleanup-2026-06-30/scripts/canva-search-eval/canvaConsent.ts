import type { Page } from "playwright";
import * as readline from "readline";

// Cookie consent button selectors for Canva
const COOKIE_CONSENT_SELECTORS = [
  'button[data-testid="cookie-consent-accept-all"]',
  'button[data-testid="accept-cookies"]',
  'button[id="onetrust-accept-btn-handler"]',
  '[id="accept-cookies"]',
  'button[aria-label*="Accept all"]',
  'button[aria-label*="accept"]',
  ".cookie-accept-all",
  "#accept-all-cookies",
  // Generic GDPR / consent buttons
  'button:has-text("Accept all")',
  'button:has-text("Accept All")',
  'button:has-text("Accept cookies")',
  'button:has-text("I accept")',
  'button:has-text("Got it")',
];

// Close/dismiss selectors for login/signup modals
const MODAL_CLOSE_SELECTORS = [
  'button[aria-label="Close"]',
  'button[aria-label="close"]',
  'button[data-testid="close-button"]',
  'button[data-testid="modal-close"]',
  '[aria-label="Dismiss"]',
  'button[class*="close"]',
  'button[class*="Close"]',
  'svg[aria-label="Close"]',
];

// Signals indicating a login wall / signup prompt
const LOGIN_WALL_SIGNALS = [
  "Sign up for free",
  "Sign up to Canva",
  "Log in to Canva",
  "Create your free account",
  "Continue with Google",
  "Continue with Facebook",
  "Continue with Apple",
  "Log in",
  "Already have an account",
  "Join Canva for free",
  "Get started for free",
  "Sign in",
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
  "Verify you are human",
  "security check",
  "Cloudflare",
];

// Signals for geo / region block
const BLOCK_SIGNALS = [
  "not available in your country",
  "not available in your region",
  "access restricted",
  "region not supported",
];

export type PageState =
  | "ok"
  | "cookie_consent"
  | "login_wall"
  | "captcha"
  | "blocked"
  | "error";

export async function detectPageState(page: Page): Promise<PageState> {
  const url = page.url();

  // Redirected to login page
  if (
    url.includes("canva.com/login") ||
    url.includes("canva.com/signup") ||
    url.includes("/auth/login") ||
    url.includes("/auth/signup")
  ) {
    return "login_wall";
  }

  try {
    const bodyText = await page.evaluate(() => document.body?.innerText ?? "");

    // CAPTCHA / bot check first
    for (const signal of CAPTCHA_SIGNALS) {
      if (bodyText.includes(signal)) return "captcha";
    }

    // Region / geo block
    for (const signal of BLOCK_SIGNALS) {
      if (bodyText.toLowerCase().includes(signal.toLowerCase())) return "blocked";
    }

    // Cookie consent — check for visible consent button
    for (const sel of COOKIE_CONSENT_SELECTORS) {
      const el = await page.$(sel).catch(() => null);
      if (el) {
        const visible = await el.isVisible().catch(() => false);
        if (visible) return "cookie_consent";
      }
    }

    // Login wall in body text — check only if we're on a Canva page
    if (url.includes("canva.com")) {
      for (const signal of LOGIN_WALL_SIGNALS) {
        if (bodyText.includes(signal)) return "login_wall";
      }
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
      const visible = await btn.isVisible().catch(() => false);
      if (!visible) continue;
      const text = (await btn.textContent()) ?? "";
      // Only click Accept/Allow/Got-it style buttons — not Reject
      if (/accept|allow|ok|agree|got it/i.test(text) || text.trim() === "") {
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
  // Try explicit close buttons
  for (const sel of MODAL_CLOSE_SELECTORS) {
    try {
      const btn = await page.$(sel);
      if (!btn) continue;
      const visible = await btn.isVisible().catch(() => false);
      if (!visible) continue;
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
  if (!process.stdin.isTTY) {
    console.log(`[non-TTY] Query ${queryId}: ${reason} — marking login_required and continuing.`);
    return false;
  }

  console.log("\n" + "=".repeat(60));
  console.log(`Canva block detected on query ${queryId}: ${reason}`);
  console.log("");
  console.log("Please handle the block manually in the open browser window.");
  console.log("After Canva template results are visible, press Enter to continue.");
  console.log("Press Ctrl+C to abort this session.");
  console.log("=".repeat(60) + "\n");

  await waitForEnter();

  const state = await detectPageState(page);
  if (state === "ok") return true;
  const url = page.url();
  if (url.includes("canva.com/templates")) return true;
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
