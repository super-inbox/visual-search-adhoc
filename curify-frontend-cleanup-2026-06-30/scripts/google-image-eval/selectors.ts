// Multiple selector fallbacks for Google Images DOM elements.
// Google frequently changes class names; always try in order.

export const LABEL_CHIP_SELECTORS = [
  // 2024–2025 chips bar
  'div[role="list"] g-scrolling-carousel a',
  'g-scrolling-carousel a[href*="tbm=isch"]',
  // chip links with data-hveid
  'a.HJ81nd',
  // older format
  'a.T7qlbe',
  // fallback: any chip-looking links in the chips container
  '[jscontroller] a[href*="tbm=isch"][data-query]',
  // very broad fallback
  '.qF20Ie a',
  'div[data-chip-id] a',
];

export const IMAGE_CONTAINER_SELECTORS = [
  // 2024–2025 main results grid
  "#islrg",
  // fallback containers
  "#rg_s",
  ".islrc",
  // broader fallback: div with image results
  'div[data-ri]',
  // outer wrapper
  "#search",
];

export const IMAGE_ITEM_SELECTORS = [
  // Each image tile in the grid
  'div[data-ri]',
  '.isv-r',
  '.rg_i_parent',
  // image links
  'a.wXeWr',
  // img inside grid
  '#islrg img[src]:not([src^="data:"])',
];

export const PREVIEW_PANEL_SELECTORS = [
  // Side panel (Knowledge Panel style)
  '#Sva75c',
  // Overlay panel
  '.tvh9oe',
  // Focused result panel
  '[jsname="figiqf"]',
  // fallback
  '.irc_c',
];

export const PREVIEW_TITLE_SELECTORS = [
  '.ReQCgd',
  '.Vkdmgd',
  'div[data-ved] h3',
  '.YQ4gaf',
  '[jsname="pIQkEc"]',
];

export const PREVIEW_SOURCE_SELECTORS = [
  '.aMiSBd span',
  '.irc_d',
  '.dTe1c a',
  '[jsname="hh3hBf"] span',
];

export const PREVIEW_PAGE_URL_SELECTORS = [
  'a.YsLeY',
  '.irc_lth a',
  'a[jsname="obdcZ"]',
  '.dTe1c a',
];

export const PREVIEW_IMAGE_URL_SELECTORS = [
  'img.sFlh5c',
  'img[jsname="kn3ccd"]',
  'img[src^="http"]:not([src^="data:"])',
];

export const CONSENT_SELECTORS = [
  'button[aria-label*="Accept all"]',
  'button[aria-label*="Reject all"]',
  'button#L2AGLb',  // Google's "Accept all" button ID
  'button.tHlp8d',
  'form[action*="consent"] button',
  '[jsname="b3VHJd"]',
];

export const CAPTCHA_INDICATORS = [
  'form#captcha-form',
  '#recaptcha',
  '.g-recaptcha',
  '[data-sitekey]',
  'iframe[src*="recaptcha"]',
];
