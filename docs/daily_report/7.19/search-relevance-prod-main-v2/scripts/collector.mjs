// Real-pipeline search result collector for V0 vs V2 comparison.
//
// Fetches the actual rendered /search page from a running Next.js server
// (V0 or V2, same code either way) and extracts the SERVER-COMPUTED props
// passed to <SearchResultsClient> from the embedded RSC flight payload
// (self.__next_f.push(...) chunks). This captures exactly what the real
// production pipeline computed -- normalize, retrieval, rewrite, guard,
// multi-path, merge, final ranking -- with no re-implementation / mirror
// logic of our own. Same method used against both V0 and V2 servers, so
// the collection method is identical on both sides (required by the task
// spec section 13.2 / Stage 12).
//
// Two-phase decode:
//  Phase 1: each `self.__next_f.push([<id>,"<jsStringLiteral>"])` call's
//    string argument is matched with a standard JS-string-literal regex
//    and decoded ONCE via JSON.parse('"'+match+'"') -- this defers all
//    escape-sequence handling (\", \\, \uXXXX, ...) to the JS engine
//    itself instead of a hand-rolled scanner, which is what caused
//    silent corruption in an earlier version of this script.
//  Phase 2: concatenate all decoded row strings (document order) into
//    one plain-text "flight stream". Within that stream there is only
//    ONE remaining level of JSON escaping (the row payload's own string
//    values), so a simple single-char-skip bracket-depth scanner is
//    sufficient and correct to pull out "inspirations": [...] etc.
//
// Usage: import { collectQuery } from './collector.mjs'

function decodeFlightRows(html) {
  const re = /self\.__next_f\.push\(\[(\d+),"((?:[^"\\]|\\.)*)"\]\)/gs;
  let m;
  const rows = [];
  while ((m = re.exec(html)) !== null) {
    try {
      const decoded = JSON.parse('"' + m[2] + '"');
      rows.push(decoded);
    } catch {
      // skip malformed row rather than aborting the whole extraction
    }
  }
  return rows.join("");
}

/** Balanced bracket extraction over PLAIN text (single level of JSON
 * string escaping remaining, e.g. `"title":"Say \"hi\""`). */
function extractBalanced(text, openIdx) {
  const open = text[openIdx];
  const close = open === "[" ? "]" : "}";
  let depth = 0;
  let i = openIdx;
  let inString = false;
  while (i < text.length) {
    const c = text[i];
    if (inString) {
      if (c === "\\") { i += 2; continue; }
      if (c === '"') inString = false;
      i++;
      continue;
    }
    if (c === '"') { inString = true; i++; continue; }
    if (c === open) depth++;
    else if (c === close) {
      depth--;
      if (depth === 0) return { raw: text.slice(openIdx, i + 1), end: i + 1 };
    }
    i++;
  }
  throw new Error("unbalanced JSON value starting at " + openIdx);
}

function extractField(flightText, key) {
  const marker = `"${key}":`;
  const idx = flightText.indexOf(marker);
  if (idx === -1) return undefined;
  const valStart = idx + marker.length;
  const c = flightText[valStart];
  if (c === "[" || c === "{") {
    const { raw } = extractBalanced(flightText, valStart);
    return JSON.parse(raw);
  }
  if (c === '"') {
    let end = valStart + 1;
    while (end < flightText.length) {
      if (flightText[end] === "\\") { end += 2; continue; }
      if (flightText[end] === '"') { end++; break; }
      end++;
    }
    return JSON.parse(flightText.slice(valStart, end));
  }
  let end = valStart;
  while (end < flightText.length && !",}]".includes(flightText[end])) end++;
  const raw = flightText.slice(valStart, end);
  if (raw === "true") return true;
  if (raw === "false") return false;
  if (raw === "null" || raw.startsWith("$undefined")) return null;
  const n = Number(raw);
  return Number.isNaN(n) ? raw : n;
}

/**
 * Fetch /<locale>/search?q=<query> from `baseUrl` and extract the real
 * server-computed result. Returns ok:false (not throw) on parse failure
 * so a single bad page doesn't kill a batch run.
 */
export async function collectQuery(baseUrl, query, { locale = "en", timeoutMs = 30000 } = {}) {
  const url = `${baseUrl}/${locale}/search?q=${encodeURIComponent(query)}`;
  const t0 = Date.now();
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const res = await fetch(url, { redirect: "follow", signal: controller.signal });
    clearTimeout(timer);
    const html = await res.text();
    const elapsedMs = Date.now() - t0;
    if (!res.ok) {
      return { query, ok: false, error: `HTTP_${res.status}`, elapsedMs, httpStatus: res.status };
    }
    const flightText = decodeFlightRows(html);
    // "inspirations" appears as a prop key for SearchResultsClient AND
    // possibly nested inside other components; the FIRST occurrence in
    // document order corresponds to the component actually rendered
    // (React emits the tree in render order, SearchResultsClient is the
    // top-level page body), which matches what we want.
    const inspirations = extractField(flightText, "inspirations") ?? [];
    const usedRewrites = extractField(flightText, "usedRewrites") ?? [];
    const pathsUsed = extractField(flightText, "pathsUsed") ?? 1;
    const matchedTemplates = extractField(flightText, "matchedTemplates") ?? [];
    const galleryPrompts = extractField(flightText, "galleryPrompts") ?? [];
    return {
      query,
      ok: true,
      elapsedMs,
      httpStatus: res.status,
      finalUrl: res.url,
      inspirationCount: inspirations.length,
      matchedTemplateCount: matchedTemplates.length,
      galleryPromptCount: galleryPrompts.length,
      totalResults: inspirations.length + matchedTemplates.length + galleryPrompts.length,
      usedRewrites,
      pathsUsed,
      rewriteTriggered: usedRewrites.length > 0 || pathsUsed > 1,
      inspirations: inspirations.map((r) => ({
        id: r.id,
        template_id: r.template_id,
        tags: r.tags ?? [],
        topics: r.topics ?? [],
        title: r.locales?.en?.title || r.locales?.zh?.title || "",
      })),
      matchedTemplateIds: matchedTemplates.map((t) => t.template_id ?? t.id).filter(Boolean),
    };
  } catch (e) {
    return { query, ok: false, error: String((e && e.message) || e), elapsedMs: Date.now() - t0 };
  }
}

// Self-test when run directly: node collector.mjs <baseUrl> "<query>"
if (import.meta.url === `file://${process.argv[1]}`) {
  const baseUrl = process.argv[2] || "http://localhost:4501";
  const query = process.argv[3] || "coffee cup";
  const result = await collectQuery(baseUrl, query);
  console.log(JSON.stringify(result, null, 2));
}
