/**
 * Google Images batch collector for search evaluation set.
 * Collects top-10 related chips and top-10 image results from Google Images
 * for each query in scripts/configs/search_eval_set.json.
 *
 * Usage:
 *   node scripts/collect_google_images_eval.mjs [options]
 *
 * Options:
 *   --headed / --headless       Browser visibility (default: headed)
 *   --limit N                   Only process first N queries
 *   --query "text"              Run a single specific query
 *   --force                     Re-run all queries (including already-successful)
 *   --screenshots=none|pilot|errors|all  (default: errors)
 *   --expected-count N          Expected query count (default: 57, warns if different)
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createWriteStream } from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

// ── Config ──────────────────────────────────────────────────────────────────

const EVAL_JSON   = path.join(ROOT, 'scripts/configs/search_eval_set.json');
const OUT_DIR     = path.join(ROOT, 'docs/search-evaluation/google-images-57');
const RESULTS_DIR     = path.join(OUT_DIR, 'results');
const SCREENSHOTS_DIR = path.join(OUT_DIR, 'screenshots');
const DEBUG_DIR       = path.join(OUT_DIR, 'debug');
const LOGS_DIR        = path.join(OUT_DIR, 'logs');
const PROFILE_DIR     = path.join(ROOT, '.cache/google-images-eval-profile');

const VIEWPORT = { width: 1536, height: 1024 };
const LOCALE   = 'en-US';
const TIMEZONE = 'America/Los_Angeles';
const SCRIPT_VERSION = '1.1.0';

// ── CLI args ─────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);

/**
 * Get a named argument value. Handles both --name=value and --name value forms.
 * Returns the string value, or true for boolean flags, or null if absent.
 */
function getArg(name) {
  for (let i = 0; i < args.length; i++) {
    if (args[i] === `--${name}`) {
      // Boolean flag or next arg is value
      const next = args[i + 1];
      if (next && !next.startsWith('--')) return next;
      return true;
    }
    if (args[i].startsWith(`--${name}=`)) {
      return args[i].slice(`--${name}=`.length);
    }
  }
  return null;
}

const HEADED         = !args.includes('--headless');
const FORCE          = args.includes('--force');
const _LIMIT         = getArg('limit');
const LIMIT          = (_LIMIT && _LIMIT !== true) ? parseInt(_LIMIT) : null;
const SINGLE_QUERY   = getArg('query') !== true ? getArg('query') : null;
const SCREENSHOTS    = (getArg('screenshots') !== true ? getArg('screenshots') : null) || 'errors';
const _EC            = getArg('expected-count');
const EXPECTED_COUNT = (_EC && _EC !== true) ? parseInt(_EC) : 57;

// ── Logging ──────────────────────────────────────────────────────────────────

fs.mkdirSync(LOGS_DIR, { recursive: true });
const logFile = createWriteStream(path.join(LOGS_DIR, 'run.log'), { flags: 'a' });

function log(...parts) {
  const msg = `[${new Date().toISOString()}] ${parts.join(' ')}`;
  console.log(msg);
  logFile.write(msg + '\n');
}
function logWarn(...parts) {
  const msg = `[${new Date().toISOString()}] WARN ${parts.join(' ')}`;
  console.warn(msg);
  logFile.write(msg + '\n');
}
function logError(...parts) {
  const msg = `[${new Date().toISOString()}] ERROR ${parts.join(' ')}`;
  console.error(msg);
  logFile.write(msg + '\n');
}

// ── Utilities ────────────────────────────────────────────────────────────────

/**
 * Generate URL-safe ASCII slug from a query string.
 * Falls back to empty string when the query is all non-ASCII (CJK, etc.).
 * Callers should suffix with query_id to ensure uniqueness.
 */
export function makeSlug(query) {
  return query
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .substring(0, 50);
}

/** Build the per-query result filename slug, always unique */
function makeFileSlug(query, queryId) {
  const s = makeSlug(query);
  return s || `cjk-${queryId}`;
}

function pad(n, width = 3) {
  return String(n).padStart(width, '0');
}

async function sleep(min, max = min) {
  const ms = Math.floor(min + Math.random() * (max - min));
  await new Promise(r => setTimeout(r, ms));
}

/** Extract a named URL parameter from a URL string */
export function extractUrlParam(urlStr, param) {
  try {
    const url = new URL(urlStr.startsWith('http') ? urlStr : `https://example.com${urlStr}`);
    return url.searchParams.get(param) || null;
  } catch {
    return null;
  }
}

/** Parse hostname from a URL, stripping www. prefix */
export function parseDomain(urlStr) {
  if (!urlStr) return null;
  try {
    return new URL(urlStr).hostname.replace(/^www\./, '');
  } catch {
    return null;
  }
}

/** Return true if the URL is a real HTTP(S) URL (not data:, blob:, empty) */
export function isValidUrl(u) {
  if (!u || typeof u !== 'string' || u.trim() === '') return false;
  if (u.startsWith('data:') || u.startsWith('blob:')) return false;
  try {
    const parsed = new URL(u);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

/**
 * Sort items carrying a .box = {x, y} by visual reading order.
 * Items within rowTolerance px of each other vertically are treated as the same row.
 */
export function sortByVisualOrder(items, rowTolerance = 40) {
  return [...items].sort((a, b) => {
    const dy = a.box.y - b.box.y;
    if (Math.abs(dy) > rowTolerance) return dy;
    return a.box.x - b.box.x;
  });
}

/** Deduplicate an array by a key function, keeping first occurrence */
export function dedupeBy(items, keyFn) {
  const seen = new Set();
  return items.filter(item => {
    const k = keyFn(item);
    if (!k || seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

// ── Load queries ─────────────────────────────────────────────────────────────

function loadQueries() {
  if (!fs.existsSync(EVAL_JSON)) {
    throw new Error(`Eval JSON not found: ${EVAL_JSON}`);
  }

  let data;
  try {
    data = JSON.parse(fs.readFileSync(EVAL_JSON, 'utf-8'));
  } catch (e) {
    throw new Error(`Failed to parse eval JSON: ${e.message}`);
  }

  if (!data.queries || !Array.isArray(data.queries)) {
    throw new Error('JSON format error: expected top-level "queries" array');
  }

  const queries = data.queries;

  // Check duplicates
  const queryTexts = queries.map(q => q.query);
  const dupeSet = queryTexts.filter((q, i) => queryTexts.indexOf(q) !== i);
  if (dupeSet.length > 0) {
    logWarn(`Duplicate queries detected: ${JSON.stringify([...new Set(dupeSet)])}`);
  }

  if (queries.length !== EXPECTED_COUNT) {
    logWarn(
      `Query count mismatch: expected ${EXPECTED_COUNT}, found ${queries.length}. ` +
      `Proceeding with all ${queries.length} queries. ` +
      `(Pass --expected-count=${queries.length} to suppress this warning.)`
    );
  }

  return queries.map((q, i) => {
    const id = i + 1;
    return {
      query_id: id,
      query: q.query,
      slug: makeFileSlug(q.query, id),
      group: q.source || '',
      expected: q.expected || '',
      expected_templates: q.expected_templates || '',
      notes: q.notes || '',
    };
  });
}

// ── Result file helpers ───────────────────────────────────────────────────────

function resultFilePath(queryId, slug) {
  return path.join(RESULTS_DIR, `${pad(queryId)}-${slug}.json`);
}

function loadExistingResult(queryId, slug) {
  const fp = resultFilePath(queryId, slug);
  if (!fs.existsSync(fp)) return null;
  try {
    return JSON.parse(fs.readFileSync(fp, 'utf-8'));
  } catch {
    return null;
  }
}

function saveResult(result) {
  fs.mkdirSync(RESULTS_DIR, { recursive: true });
  const fp = resultFilePath(result.query_id, result.slug);
  fs.writeFileSync(fp, JSON.stringify(result, null, 2), 'utf-8');
  return fp;
}

// ── Manifest ─────────────────────────────────────────────────────────────────

function loadManifest() {
  const fp = path.join(OUT_DIR, 'manifest.json');
  if (!fs.existsSync(fp)) return null;
  try { return JSON.parse(fs.readFileSync(fp, 'utf-8')); } catch { return null; }
}

function saveManifest(manifest) {
  fs.writeFileSync(path.join(OUT_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf-8');
}

// ── Google Images scraper ────────────────────────────────────────────────────

const SEARCH_URL_UDM = (q) =>
  `https://www.google.com/search?udm=2&hl=en&gl=us&safe=active&pws=0&q=${encodeURIComponent(q)}`;
const SEARCH_URL_ISCH = (q) =>
  `https://www.google.com/search?tbm=isch&hl=en&gl=us&safe=active&pws=0&q=${encodeURIComponent(q)}`;

/**
 * Detect consent pages, CAPTCHAs, sign-in walls, etc.
 * Returns { type, message } or null if page looks normal.
 */
async function detectPageAnomaly(page) {
  const url = page.url();
  const title = await page.title().catch(() => '');
  const bodyText = await page.evaluate(
    () => document.body?.innerText?.substring(0, 3000) || ''
  ).catch(() => '');

  if (/accounts\.google\.com\/signin/i.test(url)) return { type: 'sign-in', message: 'Google sign-in wall' };
  if (/consent\.google\.com/i.test(url)) return { type: 'consent', message: 'Google consent page' };
  if (/captcha/i.test(url)) return { type: 'captcha', message: 'CAPTCHA URL detected' };
  if (/unusual traffic/i.test(bodyText)) return { type: 'captcha', message: 'Unusual traffic block' };
  if (/our systems have detected unusual/i.test(bodyText)) return { type: 'captcha', message: 'Traffic block' };
  if (/before you continue to google/i.test(bodyText)) return { type: 'consent', message: 'Cookie consent page' };
  if (/before you continue/i.test(title) && url.includes('google')) return { type: 'consent', message: 'Consent prompt' };
  if (/sign in/i.test(title) && url.includes('google.com')) return { type: 'sign-in', message: 'Sign-in required' };
  return null;
}

/**
 * Wait for Google Images results to appear.
 * Returns true if any results found before timeout.
 */
async function waitForImageResults(page) {
  const selectors = [
    // tbm=isch results
    'a[href*="/imgres"] img[src]',
    'a[href*="imgurl="] img[src]',
    '#islrg img[src]',
    // udm=2 results
    'c-wiz div[data-id] img[src]',
    '[role="listitem"] img[src]',
    // Generic fallback
    'div[jsname] img[src]:not([src^="data:"])',
  ];
  for (const sel of selectors) {
    try {
      await page.waitForSelector(sel, { timeout: 7000 });
      return true;
    } catch { /* try next */ }
  }
  return false;
}

/**
 * Collect related search chips from the page.
 * Works for both udm=2 and tbm=isch layouts.
 * Returns array sorted left-to-right, deduplicated, max 10.
 */
async function collectRelatedChips(page) {
  const rawChips = await page.evaluate(() => {
    const EXCLUDE_LABELS = new Set([
      'all', 'images', 'videos', 'shopping', 'tools', 'news', 'maps', 'more',
      'search tools', 'safe search', 'settings', 'web', 'forums',
      'short videos', 'books', 'flights', 'finance',
    ]);

    // Google UI control text patterns to exclude
    const EXCLUDE_PATTERNS = [
      /^turn (on|off)/i,
      /^safe search$/i,
      /^search tools$/i,
      /^more tools$/i,
    ];

    const results = [];
    const seen = new Set();

    const allLinks = Array.from(document.querySelectorAll('a[href]'));
    for (const link of allLinks) {
      const href = link.href || '';

      // Must be a Google image search link
      if (!href.includes('google.com/search')) continue;
      if (href.includes('/imgres') || href.includes('imgres?')) continue;
      if (!href.includes('tbm=isch') && !href.includes('udm=2')) continue;

      // Skip links that are just anchoring to same page with fragment only
      // (e.g. "Turn off continuous scrolling" appends #)
      try {
        const u = new URL(href);
        // If there's no meaningful query refinement (uds param or q is same), skip
        const hasRefinement = u.searchParams.has('uds') ||
                              u.searchParams.has('tbs') ||
                              u.searchParams.has('as_q');
        const hasOnlyFragment = [...u.searchParams.keys()].every(k =>
          ['udm', 'hl', 'gl', 'safe', 'pws', 'sei', 'q', 'sca_esv'].includes(k)
        ) && !hasRefinement;
        if (hasOnlyFragment) continue;
      } catch {}

      const text = (
        link.getAttribute('aria-label') ||
        link.textContent ||
        ''
      ).trim().replace(/\s+/g, ' ');

      if (!text || text.length > 100) continue;
      if (EXCLUDE_LABELS.has(text.toLowerCase())) continue;
      if (EXCLUDE_PATTERNS.some(re => re.test(text))) continue;
      if (seen.has(text.toLowerCase())) continue;

      // Must be visible and a reasonable chip height
      const rect = link.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) continue;
      if (rect.height > 80) continue; // too tall to be a chip

      let refinedQuery = '';
      try {
        refinedQuery = new URL(href).searchParams.get('q') || '';
      } catch {}

      seen.add(text.toLowerCase());
      results.push({
        label: text,
        refined_query: refinedQuery,
        target_url: href,
        x: rect.left + window.scrollX,
        y: rect.top + window.scrollY,
      });
    }

    return results;
  });

  // Sort left-to-right, grouping by row
  rawChips.sort((a, b) => {
    const dy = a.y - b.y;
    if (Math.abs(dy) > 60) return dy;
    return a.x - b.x;
  });

  return rawChips.slice(0, 10).map((chip, i) => ({
    rank: i + 1,
    label: chip.label,
    refined_query: chip.refined_query,
    target_url: chip.target_url,
  }));
}

/**
 * Collect image result cards from the page.
 * Works for both udm=2 (new layout) and tbm=isch (classic layout).
 *
 * Strategy:
 * 1. Find all large <img> elements that appear to be in the image grid
 * 2. Walk up DOM to find each image's parent link/container
 * 3. Filter out non-result images (logos, icons, chips, etc.)
 */
async function collectImageCards(page) {
  // Gentle scrolls to trigger lazy loading
  await page.evaluate(() => window.scrollBy(0, 500));
  await sleep(800);
  await page.evaluate(() => window.scrollBy(0, 500));
  await sleep(600);

  return page.evaluate(() => {
    const MIN_IMG_SIZE = 60;  // minimum px for image width/height
    const GRID_Y_MIN  = 100; // skip header area

    // URLs that indicate this is a Google-owned logo/icon, not a result
    const GOOGLE_ASSET_PATTERNS = [
      'googlelogo', 'google_logo', 'gstatic.com/images/branding',
      '/favicon', 'sprites', 'cleardot', 'blank.gif',
    ];

    const cards = [];
    const seenSrcs = new Set();

    // Walk every img on the page
    const imgs = Array.from(document.querySelectorAll('img[src]'));

    for (const img of imgs) {
      const src = img.src || '';
      if (!src || src.startsWith('data:') || src.startsWith('blob:')) continue;
      if (seenSrcs.has(src)) continue;

      // Skip Google assets
      if (GOOGLE_ASSET_PATTERNS.some(p => src.includes(p))) continue;

      // Size check: rendered size
      const w = img.width || img.clientWidth || img.offsetWidth || 0;
      const h = img.height || img.clientHeight || img.offsetHeight || 0;
      if (w < MIN_IMG_SIZE || h < MIN_IMG_SIZE) continue;

      // Position check: skip header/chip area
      const imgRect = img.getBoundingClientRect();
      const imgY = imgRect.top + window.scrollY;
      if (imgY < GRID_Y_MIN) continue;
      if (imgRect.width < MIN_IMG_SIZE || imgRect.height < MIN_IMG_SIZE) continue;

      // Walk up the DOM to find the nearest anchor element
      let anchor = null;
      let el = img.parentElement;
      let depth = 0;
      while (el && depth < 8) {
        if (el.tagName === 'A' && el.href) {
          anchor = el;
          break;
        }
        el = el.parentElement;
        depth++;
      }

      // Determine href: prefer anchor href, fall back to null
      const href = anchor?.href || '';

      // Filter out anchors that point to non-image URLs (navigation, etc.)
      if (anchor) {
        // Skip if this anchor is clearly a navigation link
        const skip =
          href.includes('accounts.google.com') ||
          href.includes('support.google.com') ||
          href.includes('policies.google.com') ||
          (href.includes('google.com/search') &&
           !href.includes('/imgres') &&
           !href.includes('imgurl=') &&
           !href.includes('#imgrc') &&
           !href.includes('udm=2') &&
           href.split('?')[1]?.split('#')[0].length < 20);

        if (skip) continue;
      }

      // Get the card's bounding box (use the anchor or image rect)
      const containerEl = anchor || img;
      const containerRect = containerEl.getBoundingClientRect();

      // Skip tiny containers
      if (containerRect.width < MIN_IMG_SIZE || containerRect.height < MIN_IMG_SIZE) continue;
      if (containerRect.top + window.scrollY < GRID_Y_MIN) continue;

      seenSrcs.add(src);

      // ── Title extraction ────────────────────────────────────────────────────
      const title = (
        img.getAttribute('alt') ||
        anchor?.getAttribute('aria-label') ||
        anchor?.getAttribute('title') ||
        img.getAttribute('title') ||
        anchor?.querySelector('[class*="title"], [class*="Title"]')?.textContent ||
        ''
      ).trim().replace(/\s+/g, ' ');

      // ── Source URL extraction (without clicking) ─────────────────────────────
      // Strategy 1: Direct external href on the anchor
      let sourceUrl = '';
      if (href && !href.includes('google.com') && !href.includes('gstatic.com')) {
        sourceUrl = href;
      }

      // Strategy 2: Check data attributes on img or container for source URL
      if (!sourceUrl) {
        const dataAttrs = ['data-src', 'data-imgurl', 'data-url', 'data-referer',
                           'data-page-url', 'data-source', 'data-lpage'];
        for (const attr of dataAttrs) {
          const val = img.getAttribute(attr) || anchor?.getAttribute(attr) ||
                      containerEl.getAttribute(attr);
          if (val && val.startsWith('http') && !val.includes('gstatic.com') &&
              !val.includes('google.com')) {
            sourceUrl = val;
            break;
          }
        }
      }

      // Strategy 3: Look for the source attribution text visible below the image
      // In Google Images cards, source name/domain often appears as text near the card
      let sourceName = '';
      if (!sourceUrl) {
        // Walk up to find a container, then look for text sibling elements
        let cardContainer = containerEl;
        for (let d = 0; d < 5; d++) {
          const parent = cardContainer.parentElement;
          if (!parent) break;
          // Look for a text element with domain-like content
          const textEls = Array.from(parent.querySelectorAll('span, div'))
            .filter(e => {
              const t = e.textContent?.trim() || '';
              // Short text that looks like a domain or site name
              return t.length > 2 && t.length < 60 && !e.querySelector('img') &&
                     e.children.length === 0;
            });
          for (const te of textEls) {
            const t = te.textContent.trim();
            // Skip obvious non-source text (numbers, single chars, etc.)
            if (/^\d+$/.test(t) || t.length < 3) continue;
            if (!sourceName && t) { sourceName = t; }
          }
          cardContainer = parent;
        }
      }

      cards.push({
        href: href || '',
        thumbnailUrl: src,
        title,
        sourceUrl,
        sourceName,
        rect: {
          x: containerRect.left + window.scrollX,
          y: containerRect.top + window.scrollY,
          width: containerRect.width,
          height: containerRect.height,
        },
      });
    }

    return cards;
  });
}

/**
 * Parse source and image URLs from a Google Images href.
 * Handles /imgres, imgurl= param, and direct external URLs.
 */
export function parseGoogleImageHref(href) {
  if (!href) return { sourceUrl: null, imageUrl: null };
  try {
    const url = new URL(href);
    // Classic tbm=isch format
    const imgurl    = url.searchParams.get('imgurl');
    const imgrefurl = url.searchParams.get('imgrefurl');
    if (imgurl) return { sourceUrl: imgrefurl || null, imageUrl: imgurl };
    // url= redirect
    const directUrl = url.searchParams.get('url');
    if (directUrl && directUrl.startsWith('http')) return { sourceUrl: directUrl, imageUrl: null };
    // If the href itself is an external URL (not google.com), it's the source
    if (!href.includes('google.com') && !href.includes('gstatic.com')) {
      return { sourceUrl: href, imageUrl: null };
    }
  } catch {}
  return { sourceUrl: null, imageUrl: null };
}

/**
 * Click the card at the given visual-order index (among all large images on page)
 * and extract detail panel info.
 * Returns { sourceUrl, imageUrl, width, height } or null.
 */
async function extractDetailPanel(page, cardVisualIndex) {
  const clicked = await page.evaluate((idx) => {
    const MIN_SIZE  = 60;
    const GRID_Y    = 100;
    const GOOGLE_SKIP = ['googlelogo', 'gstatic.com/images/branding', 'favicon', 'sprites', 'cleardot'];

    // Find all large result images
    const candidates = [];
    const seenSrc = new Set();

    for (const img of document.querySelectorAll('img[src]')) {
      const src = img.src;
      if (!src || src.startsWith('data:') || src.startsWith('blob:')) continue;
      if (GOOGLE_SKIP.some(p => src.includes(p))) continue;
      if (seenSrc.has(src)) continue;
      const rect = img.getBoundingClientRect();
      if (rect.width < MIN_SIZE || rect.height < MIN_SIZE) continue;
      if (rect.top + window.scrollY < GRID_Y) continue;
      seenSrc.add(src);

      // Find clickable ancestor
      let anchor = null;
      let el = img.parentElement;
      for (let d = 0; d < 8 && el; d++, el = el.parentElement) {
        if (el.tagName === 'A' || el.getAttribute('role') === 'link') { anchor = el; break; }
      }
      candidates.push({ el: anchor || img, x: rect.left + window.scrollX, y: rect.top + window.scrollY, src });
    }

    // Sort visually
    candidates.sort((a, b) => {
      const dy = a.y - b.y;
      if (Math.abs(dy) > 40) return dy;
      return a.x - b.x;
    });

    if (idx >= candidates.length) return false;
    candidates[idx].el.scrollIntoView({ block: 'center', behavior: 'instant' });
    candidates[idx].el.click();
    return true;
  }, cardVisualIndex);

  if (!clicked) return null;

  await sleep(1200, 2000);

  const detail = await page.evaluate(() => {
    // After clicking, look for detail panel or newly visible info
    // Try multiple panel selectors in order of specificity
    const panelSelectors = [
      // Classic tbm=isch side panel
      '#irc_bg', '.iGVLpd', '[jsname="Jt5YSd"]', '.tvh9oe',
      // UDM=2 panel
      '[data-is-active-result]',
      '[role="dialog"]',
      '.bicc',
      // Fallback: any large recently-displayed container
    ];

    let searchScope = null;
    for (const sel of panelSelectors) {
      const el = document.querySelector(sel);
      if (el) { searchScope = el; break; }
    }
    searchScope = searchScope || document.body;

    // Find first external link (non-Google) = source URL
    const externalLinks = Array.from(searchScope.querySelectorAll('a[href]'))
      .filter(a => {
        const h = a.href || '';
        return h.startsWith('http') &&
               !h.includes('google.com') &&
               !h.includes('gstatic.com') &&
               !h.includes('googleapis.com');
      });
    const sourceUrl = externalLinks[0]?.href || null;

    // Find largest image in the panel area
    const imgs = Array.from(searchScope.querySelectorAll('img[src]'))
      .filter(img => {
        const s = img.src;
        return s && !s.startsWith('data:') && !s.startsWith('blob:');
      })
      .map(img => ({
        src: img.src,
        w: img.naturalWidth || img.clientWidth || 0,
        h: img.naturalHeight || img.clientHeight || 0,
      }))
      .filter(img => img.w > 100 || img.h > 100)
      .sort((a, b) => (b.w * b.h) - (a.w * a.h));

    const best = imgs[0];
    return {
      sourceUrl,
      imageUrl: best?.src || null,
      width: best?.w || null,
      height: best?.h || null,
    };
  });

  // Dismiss the panel
  await page.keyboard.press('Escape').catch(() => {});
  await sleep(400);

  return detail;
}

/**
 * Collect all data for a single query.
 * Returns a full result object.
 */
async function collectQuery(browser, queryInfo, screenshotMode) {
  const { query_id, query, slug } = queryInfo;
  const warnings = [];
  const collectedAt = new Date().toISOString();

  // Fresh page for each query for cleaner state
  const page = await browser.newPage();
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

  let searchUrl = SEARCH_URL_UDM(query);
  let usedUrlMode = 'udm=2';

  try {
    log(`[${query_id}/${slug}] Starting: "${query}"`);

    // ── Navigate ────────────────────────────────────────────────────────────
    try {
      await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });
    } catch (e) {
      logError(`[${query_id}] Navigation error: ${e.message}`);
      return buildFailedResult(queryInfo, collectedAt, searchUrl, `Navigation failed: ${e.message}`, warnings);
    }

    await sleep(1500, 2500);

    // ── Detect anomalies ─────────────────────────────────────────────────────
    const anomaly = await detectPageAnomaly(page);
    if (anomaly) {
      logError(`[${query_id}] Anomaly: ${anomaly.type} — ${anomaly.message}`);

      if (anomaly.type === 'consent') {
        log('=== CONSENT PAGE DETECTED ===');
        log('Please complete the consent in the browser window, then the script will continue...');
        await sleep(20000); // Give user 20 seconds to click through consent
        const recheckAnomaly = await detectPageAnomaly(page);
        if (recheckAnomaly?.type === 'consent') {
          warnings.push('Consent page not resolved — result may be incomplete');
        }
      }

      if (anomaly.type === 'captcha') {
        const ssPath = path.join(DEBUG_DIR, `captcha-${slug}.jpg`);
        const htmlPath = path.join(DEBUG_DIR, `captcha-${slug}.html`);
        await page.screenshot({ path: ssPath, type: 'jpeg', quality: 80 }).catch(() => {});
        fs.writeFileSync(htmlPath, await page.content().catch(() => ''), 'utf-8');
        logError(`CAPTCHA at query [${query_id}] "${query}". Stopping all runs. Diagnostics saved.`);
        throw { type: 'captcha', query_id, query, message: anomaly.message };
      }
    }

    // ── Wait for results; try tbm=isch fallback ──────────────────────────────
    let hasResults = await waitForImageResults(page);

    if (!hasResults) {
      logWarn(`[${query_id}] No results with udm=2 — trying tbm=isch fallback`);
      searchUrl = SEARCH_URL_ISCH(query);
      usedUrlMode = 'tbm=isch';
      try {
        await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await sleep(1500);
        hasResults = await waitForImageResults(page);
      } catch (e) {
        logError(`[${query_id}] Fallback navigation error: ${e.message}`);
      }
    }

    // ── Screenshots ──────────────────────────────────────────────────────────
    if (screenshotMode === 'pilot' || screenshotMode === 'all') {
      const ssDir = screenshotMode === 'pilot'
        ? path.join(SCREENSHOTS_DIR, 'pilot')
        : path.join(SCREENSHOTS_DIR, 'all');
      fs.mkdirSync(ssDir, { recursive: true });
      await page.screenshot({ path: path.join(ssDir, `${pad(query_id)}-${slug}.jpg`), type: 'jpeg', quality: 75 }).catch(() => {});
    }

    if (!hasResults) {
      warnings.push('No image results detected on page');
      const errSsPath = path.join(SCREENSHOTS_DIR, 'errors', `${pad(query_id)}-${slug}.jpg`);
      const htmlPath  = path.join(DEBUG_DIR, `${pad(query_id)}-${slug}.html`);
      fs.mkdirSync(path.dirname(errSsPath), { recursive: true });
      await page.screenshot({ path: errSsPath, type: 'jpeg', quality: 70 }).catch(() => {});
      fs.writeFileSync(htmlPath, await page.content().catch(() => ''), 'utf-8');
      return buildResult(queryInfo, collectedAt, searchUrl, usedUrlMode, [], [], 'failed',
        'No image results found', warnings);
    }

    // ── Related chips ────────────────────────────────────────────────────────
    let relatedChips = [];
    try {
      relatedChips = await collectRelatedChips(page);
      log(`[${query_id}] Chips: ${relatedChips.length}`);
    } catch (e) {
      warnings.push(`Chip collection failed: ${e.message}`);
      logWarn(`[${query_id}] Chip error: ${e.message}`);
    }

    // ── Image cards ──────────────────────────────────────────────────────────
    let rawCards = [];
    try {
      rawCards = await collectImageCards(page);
      log(`[${query_id}] Raw cards: ${rawCards.length}`);
    } catch (e) {
      warnings.push(`Image card collection failed: ${e.message}`);
      logWarn(`[${query_id}] Card error: ${e.message}`);
    }

    // Sort by visual reading order and deduplicate
    const sortedCards = sortByVisualOrder(rawCards.map(c => ({ ...c, box: c.rect })), 40);
    const uniqueCards = dedupeBy(sortedCards, c => c.thumbnailUrl);
    const top10Cards  = uniqueCards.slice(0, 10);

    // ── Extract image details ────────────────────────────────────────────────
    const imageResults = [];

    for (let i = 0; i < top10Cards.length; i++) {
      const card = top10Cards[i];
      const rank = i + 1;

      // Start with URLs already extracted from DOM (without clicking)
      const { sourceUrl: hrefSource, imageUrl: hrefImage } = parseGoogleImageHref(card.href);
      let sourceUrl = hrefSource || (isValidUrl(card.sourceUrl) ? card.sourceUrl : null);
      let imageUrl  = hrefImage;
      let imgWidth  = null;
      let imgHeight = null;
      let sourceName = card.sourceName || '';

      // If still no source URL, try the detail panel click
      if (!isValidUrl(sourceUrl)) {
        try {
          const detail = await extractDetailPanel(page, i);
          if (detail) {
            if (isValidUrl(detail.sourceUrl) && !detail.sourceUrl.includes('google.com')) {
              sourceUrl = detail.sourceUrl;
            }
            if (isValidUrl(detail.imageUrl) && !detail.imageUrl.startsWith('data:')) {
              imageUrl  = detail.imageUrl;
              imgWidth  = detail.width;
              imgHeight = detail.height;
            }
          }
        } catch (e) {
          warnings.push(`Card ${rank}: detail panel error: ${e.message}`);
        }
      }

      // Fallback: use thumbnail URL as image URL
      if (!isValidUrl(imageUrl) && isValidUrl(card.thumbnailUrl)) {
        imageUrl = card.thumbnailUrl;
        warnings.push(`Card ${rank}: using thumbnail as image URL (no full URL found)`);
      }

      const sourceDomain = parseDomain(sourceUrl) || '';

      if (!isValidUrl(imageUrl)) {
        warnings.push(`Card ${rank}: no valid image URL`);
        imageUrl = null;
      }
      if (!isValidUrl(sourceUrl)) {
        warnings.push(`Card ${rank}: no valid source URL`);
        sourceUrl = null;
      }

      imageResults.push({
        rank,
        title: card.title || '',
        source_name: sourceName,
        source_domain: sourceDomain,
        source_url: sourceUrl || '',
        thumbnail_url: card.thumbnailUrl || '',
        image_url: imageUrl || '',
        width: imgWidth,
        height: imgHeight,
      });
    }

    // ── Error screenshot if issues ───────────────────────────────────────────
    const missingUrls = imageResults.filter(r => !r.image_url).length;
    if ((imageResults.length < 10 || missingUrls > 5) &&
        (screenshotMode === 'errors' || screenshotMode === 'all')) {
      const errPath = path.join(SCREENSHOTS_DIR, 'errors', `${pad(query_id)}-${slug}.jpg`);
      fs.mkdirSync(path.dirname(errPath), { recursive: true });
      await page.screenshot({ path: errPath, type: 'jpeg', quality: 70 }).catch(() => {});
    }

    // ── Status ───────────────────────────────────────────────────────────────
    let status;
    if (imageResults.length >= 10) {
      status = 'success';
    } else if (imageResults.length > 0) {
      status = 'partial';
      warnings.push(`Only ${imageResults.length}/10 image results collected`);
    } else {
      status = 'failed';
    }

    log(`[${query_id}] Done — status: ${status} | images: ${imageResults.length} | chips: ${relatedChips.length}`);

    return buildResult(queryInfo, collectedAt, searchUrl, usedUrlMode, relatedChips, imageResults, status, null, warnings);

  } finally {
    await page.close().catch(() => {});
  }
}

function buildResult(queryInfo, collectedAt, searchUrl, urlMode, relatedChips, imageResults, status, error, warnings) {
  return {
    query_id: queryInfo.query_id,
    query: queryInfo.query,
    slug: queryInfo.slug,
    group: queryInfo.group,
    expected: queryInfo.expected,
    expected_templates: queryInfo.expected_templates,
    collected_at: collectedAt,
    provider: 'google_images_web',
    browser: 'chromium',
    locale: LOCALE,
    region: 'US',
    viewport: VIEWPORT,
    search_url: searchUrl,
    url_mode: urlMode || null,
    status,
    related_chips: relatedChips || [],
    image_results: imageResults || [],
    counts: {
      related_chips: (relatedChips || []).length,
      image_results: (imageResults || []).length,
    },
    warnings: warnings || [],
    error: error || null,
  };
}

function buildFailedResult(queryInfo, collectedAt, searchUrl, error, warnings) {
  return buildResult(queryInfo, collectedAt, searchUrl, null, [], [], 'failed', error, warnings || []);
}

// ── Summary CSV ───────────────────────────────────────────────────────────────

function writeSummaryCsv(allResults) {
  const headers = [
    'query_id', 'query', 'group', 'expected', 'expected_templates',
    'status', 'chip_count', 'image_result_count',
    'missing_image_url_count', 'missing_source_url_count',
    'warning_count', 'error', 'result_file',
  ];

  const rows = allResults.map(r => {
    const imgs = r.image_results || [];
    const missingImg = imgs.filter(i => !isValidUrl(i.image_url)).length;
    const missingSrc = imgs.filter(i => !isValidUrl(i.source_url)).length;
    const fp = path.relative(OUT_DIR, resultFilePath(r.query_id, r.slug));
    return [
      r.query_id,
      `"${(r.query || '').replace(/"/g, '""')}"`,
      r.group || '',
      r.expected || '',
      r.expected_templates || '',
      r.status || '',
      r.counts?.related_chips ?? 0,
      r.counts?.image_results ?? 0,
      missingImg,
      missingSrc,
      (r.warnings || []).length,
      `"${(r.error || '').replace(/"/g, '""')}"`,
      fp,
    ].join(',');
  });

  fs.writeFileSync(
    path.join(OUT_DIR, 'summary.csv'),
    [headers.join(','), ...rows].join('\n') + '\n',
    'utf-8'
  );
}

// ── README ────────────────────────────────────────────────────────────────────

function writeReadme(queries, results, manifest) {
  const successCount = results.filter(r => r.status === 'success').length;
  const partialCount = results.filter(r => r.status === 'partial').length;
  const failedCount  = results.filter(r => r.status === 'failed').length;
  const notRunCount  = results.filter(r => r.status === 'not_run').length;

  fs.writeFileSync(path.join(OUT_DIR, 'README.md'), `# Google Images Search Evaluation — ${queries.length} Queries

## Overview

Playwright (Chromium) scrape of Google Images for the Curify search evaluation set.
Collects two metrics per query: related search chips and top-10 image results.

## Metrics

### 1. Related Search Chips (top 10)
Horizontal chip labels above image results, in left-to-right visual order.
Excludes navigation tabs (All, Images, Videos, Shopping, Tools).

### 2. Image Results (top 10)
First 10 image results in visual reading order (top→bottom, left→right within row).
Excludes ads, shopping modules, and navigation elements.
Sorted by bounding-box coordinates with 40px row tolerance.

## Data Source

\`scripts/configs/search_eval_set.json\` — ${queries.length} queries

## Environment

| Setting | Value |
|---------|-------|
| Browser | Chromium (Playwright ${SCRIPT_VERSION}) |
| Viewport | ${VIEWPORT.width}×${VIEWPORT.height} |
| Locale | ${LOCALE} |
| Region | US |
| Timezone | ${TIMEZONE} |
| Safe Search | active (safe=active) |
| Personalization | disabled (pws=0) |
| URL mode | udm=2 with tbm=isch fallback |

## Run Commands

\`\`\`bash
# Smoke test (first 3 queries, with screenshots)
node scripts/collect_google_images_eval.mjs --limit 3 --headed --screenshots=pilot

# Full run
node scripts/collect_google_images_eval.mjs --headed --screenshots=errors

# Resume (already-succeeded queries are skipped automatically)
node scripts/collect_google_images_eval.mjs --headed --screenshots=errors

# Force re-run everything
node scripts/collect_google_images_eval.mjs --headed --force

# Single query
node scripts/collect_google_images_eval.mjs --query "cats" --headed

# Headless mode
node scripts/collect_google_images_eval.mjs --headless --screenshots=errors
\`\`\`

## Checkpoint / Resume

Each query writes its result immediately to \`results/NNN-<slug>.json\`.
Re-running skips any query where \`status == "success"\`.
\`--force\` re-runs all queries regardless of prior status.

## Output Fields

| Field | Description |
|-------|-------------|
| query_id | 1-based index in eval set |
| query | Original query text |
| slug | URL-safe ASCII slug |
| group | Source tag from eval set |
| expected | Curify expected result richness |
| expected_templates | Expected template count |
| status | success / partial / failed |
| related_chips | Array of {rank, label, refined_query, target_url} |
| image_results | Array of {rank, title, source_name, source_domain, source_url, thumbnail_url, image_url, width, height} |

## Limitations

- Google's page structure changes frequently; selectors are heuristic
- Locale/timezone reduce but don't eliminate personalization
- Results vary by time of day and Google A/B experiments
- CJK queries may produce different chip patterns than English

## CAPTCHA Handling

If Google blocks the run:
1. A diagnostic screenshot and HTML are saved to \`debug/\`
2. The script stops immediately — no bypass is attempted
3. Completed queries are already saved; re-run to resume

## This Run

| Metric | Count |
|--------|-------|
| Total queries | ${queries.length} |
| Successful | ${successCount} |
| Partial | ${partialCount} |
| Failed | ${failedCount} |
| Not run | ${notRunCount} |
| Started | ${manifest?.started_at || 'N/A'} |
| Completed | ${manifest?.completed_at || 'N/A'} |
`, 'utf-8');
}

// ── Launch browser ────────────────────────────────────────────────────────────

async function launchBrowser() {
  const baseOptions = {
    headless: !HEADED,
    viewport: VIEWPORT,
    locale: LOCALE,
    timezoneId: TIMEZONE,
    args: ['--lang=en-US', '--disable-blink-features=AutomationControlled'],
  };

  // Try system Chrome first (avoids Playwright Chromium installation issues)
  try {
    const ctx = await chromium.launchPersistentContext(PROFILE_DIR, {
      ...baseOptions,
      channel: 'chrome',
    });
    log('Browser: system Chrome (channel: chrome)');
    return { browser: ctx, browserName: 'chrome' };
  } catch (e) {
    logWarn(`System Chrome unavailable (${e.message}), falling back to Playwright Chromium`);
  }

  // Fall back to Playwright-managed Chromium
  const ctx = await chromium.launchPersistentContext(PROFILE_DIR, baseOptions);
  log('Browser: Playwright Chromium');
  return { browser: ctx, browserName: 'chromium' };
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  // Ensure output directories exist
  for (const d of [OUT_DIR, RESULTS_DIR, path.join(SCREENSHOTS_DIR, 'pilot'),
                   path.join(SCREENSHOTS_DIR, 'errors'), DEBUG_DIR, LOGS_DIR, PROFILE_DIR]) {
    fs.mkdirSync(d, { recursive: true });
  }

  log('=== Google Images Eval Collector v' + SCRIPT_VERSION + ' ===');
  log(`Mode: ${HEADED ? 'headed' : 'headless'} | Screenshots: ${SCREENSHOTS} | Force: ${FORCE}`);

  // Load and validate queries
  let queries;
  try {
    queries = loadQueries();
  } catch (e) {
    logError(`FATAL: ${e.message}`);
    process.exit(1);
  }

  log(`Loaded ${queries.length} queries (expected: ${EXPECTED_COUNT})`);

  // Apply filters
  let filteredQueries = queries;
  if (SINGLE_QUERY) {
    filteredQueries = queries.filter(q => q.query === SINGLE_QUERY);
    if (filteredQueries.length === 0) {
      logError(`Query not found: "${SINGLE_QUERY}"`);
      process.exit(1);
    }
  } else if (LIMIT !== null) {
    filteredQueries = queries.slice(0, LIMIT);
    log(`Applying --limit ${LIMIT}: will run queries 1–${filteredQueries.length}`);
  }

  // Skip already-successful queries
  const toRun = FORCE
    ? filteredQueries
    : filteredQueries.filter(q => {
        const existing = loadExistingResult(q.query_id, q.slug);
        if (existing?.status === 'success') {
          log(`[${q.query_id}] Skip (already succeeded): "${q.query}"`);
          return false;
        }
        return true;
      });

  log(`Queries to run: ${toRun.length} (${filteredQueries.length - toRun.length} already done)`);

  // Initialize manifest
  const startedAt = new Date().toISOString();
  const manifest = loadManifest() || {
    query_set_source: path.relative(ROOT, EVAL_JSON),
    expected_query_count: EXPECTED_COUNT,
    actual_query_count: queries.length,
    started_at: startedAt,
    completed_at: null,
    successful_count: 0,
    partial_count: 0,
    failed_count: 0,
    browser_config: { browser: 'chromium', headed: HEADED, viewport: VIEWPORT, locale: LOCALE, timezone: TIMEZONE, region: 'US' },
    script_version: SCRIPT_VERSION,
    output_paths: { results: 'results/', screenshots: 'screenshots/', debug: 'debug/', logs: 'logs/' },
  };
  manifest.started_at = startedAt;
  saveManifest(manifest);

  // Launch browser
  log('Launching browser...');
  let browser, browserName;
  try {
    ({ browser, browserName } = await launchBrowser());
  } catch (e) {
    logError(`Failed to launch browser: ${e.message}`);
    process.exit(1);
  }

  let captchaStop = false;

  try {
    for (let i = 0; i < toRun.length; i++) {
      const queryInfo = toRun[i];
      let result = null;

      for (let attempt = 1; attempt <= 2; attempt++) {
        try {
          result = await collectQuery(browser, queryInfo, SCREENSHOTS);
          break;
        } catch (e) {
          if (e?.type === 'captcha') {
            captchaStop = true;
            throw e;
          }
          logWarn(`[${queryInfo.query_id}] Attempt ${attempt} error: ${e.message}`);
          if (attempt === 2) {
            logError(`[${queryInfo.query_id}] All retries failed`);
            result = buildFailedResult(queryInfo, new Date().toISOString(),
              SEARCH_URL_UDM(queryInfo.query), e.message, []);
          } else {
            await sleep(3000, 5000);
          }
        }
      }

      if (result) {
        const fp = saveResult(result);
        log(`[${queryInfo.query_id}] Saved → ${path.relative(ROOT, fp)}`);
      }

      // Pause between queries
      if (i < toRun.length - 1) {
        const waitSec = 4 + Math.random() * 4;
        log(`Waiting ${waitSec.toFixed(1)}s before next query...`);
        await sleep(waitSec * 1000);
      }
    }
  } catch (e) {
    if (e?.type === 'captcha') {
      logError(`Run halted: CAPTCHA/unusual traffic at query [${e.query_id}] "${e.query}"`);
    } else {
      logError(`Unexpected top-level error: ${e?.message || e}`);
    }
  } finally {
    await browser.close().catch(() => {});
    logFile.end();
  }

  // Build summary over all queries (not just this run's batch)
  const allResults = queries.map(q => {
    const r = loadExistingResult(q.query_id, q.slug);
    return r || {
      query_id: q.query_id, query: q.query, slug: q.slug,
      group: q.group, expected: q.expected, expected_templates: q.expected_templates,
      status: 'not_run', related_chips: [], image_results: [],
      counts: { related_chips: 0, image_results: 0 },
      warnings: [], error: 'Not run in this batch',
    };
  });

  const successCount = allResults.filter(r => r.status === 'success').length;
  const partialCount = allResults.filter(r => r.status === 'partial').length;
  const failedCount  = allResults.filter(r => r.status === 'failed').length;

  fs.writeFileSync(
    path.join(OUT_DIR, 'all_results.json'),
    JSON.stringify({ queries: allResults }, null, 2),
    'utf-8'
  );

  writeSummaryCsv(allResults);

  manifest.completed_at = new Date().toISOString();
  manifest.successful_count = successCount;
  manifest.partial_count    = partialCount;
  manifest.failed_count     = failedCount;
  manifest.browser_config.browser = browserName || 'chromium';
  saveManifest(manifest);

  writeReadme(queries, allResults, manifest);

  // ── Final report ──────────────────────────────────────────────────────────
  const q10chips = allResults.filter(r => (r.counts?.related_chips ?? 0) >= 10).length;
  const q0chips  = allResults.filter(r => (r.counts?.related_chips ?? 0) === 0).length;
  const q10imgs  = allResults.filter(r => (r.counts?.image_results ?? 0) >= 10).length;
  const failedList = allResults.filter(r => r.status === 'failed' || r.status === 'not_run');

  console.log('\n══════════════════════════════════════════');
  console.log('  FINAL SUMMARY');
  console.log('══════════════════════════════════════════');
  console.log(`Total queries:           ${queries.length}`);
  console.log(`  Successful:            ${successCount}`);
  console.log(`  Partial:               ${partialCount}`);
  console.log(`  Failed:                ${failedCount}`);
  console.log(`  Not run this batch:    ${allResults.filter(r => r.status === 'not_run').length}`);
  console.log(`Queries with 10 chips:   ${q10chips}`);
  console.log(`Queries with 0 chips:    ${q0chips}`);
  console.log(`Queries with 10 images:  ${q10imgs}`);
  if (failedList.length > 0) {
    console.log('\nFailed / Not-run queries:');
    failedList.forEach(r => console.log(`  [${r.query_id}] "${r.query}" — ${r.error || r.status}`));
  }
  if (captchaStop) {
    console.log('\n⚠ Run was stopped due to CAPTCHA/unusual traffic detection.');
    console.log('  Progress is saved. Wait before resuming.');
  }
  console.log('══════════════════════════════════════════\n');
}

main().catch(e => {
  console.error('Fatal error:', e?.message || e);
  process.exit(1);
});
