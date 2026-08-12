// Reproducibility aid for the 8.12 Pinterest same-query pilot (see FINDINGS.md section "Pinterest").
//
// Method: navigate a browser tab to https://www.pinterest.com/search/pins/?q=<query>
// (URL-encoded, one of the 10 authoritative_queries.csv queries, unmodified), wait ~2s for the
// grid to render, then run this snippet in the page's JS console (or via a browser-automation
// tool's JS-exec action) to extract the publicly visible search-results grid: pin URL, thumbnail
// image URL, and the title/source text shown under each thumbnail. No login action, saved
// cookies, or account interaction is performed by this snippet — it only reads already-rendered
// public DOM content.
//
// Known limitations this script does NOT work around (see FINDINGS.md for detail):
//  - Outbound/original source URL is not present in this grid data or in the individual pin
//    page's static DOM / embedded JSON; Pinterest only resolves it via a click-triggered action.
//  - Per-pin tags/hashtags are not exposed in the search grid.
//  - Some queries render pins with no title/source text at all (a Pinterest-side gap, not a
//    script bug).

(function extractPinterestGrid(limit = 8) {
  const listItems = Array.from(document.querySelectorAll('div[role="listitem"]'));
  const results = listItems
    .map((li) => {
      const a = li.querySelector('a[href^="/pin/"]');
      if (!a) return null;
      const img = li.querySelector("img");
      return {
        pinHref: a.getAttribute("href"),
        imgSrc: img ? img.getAttribute("src") : null,
        text: (li.innerText || "").slice(0, 200),
      };
    })
    .filter(Boolean);
  return { count: results.length, top: results.slice(0, limit) };
})();
