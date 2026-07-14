#!/usr/bin/env node
/**
 * Stage 7 2x2 ablation harness. Runs the 68 gold queries through the real
 * production catalog + real Stage 5 (lib/searchRewrite.ts) and Stage 6
 * (lib/query_phrase_aliases.ts / lib/cjk_tokenizer.ts) modules, imported
 * unmodified via _bundle_stage56.cjs (see build_bundle.cjs). Only the
 * page.tsx-local orchestration (buildSearchTokens/scoreBlob/scoreQueryTokens/
 * merge/hasStrict) is reproduced here, transcribed verbatim from:
 *   - NEW (Stage 6 / d=ON): app/[locale]/(public)/search/page.tsx (working
 *     tree, lines 151-326, 561-822 as read 2026-07-13)
 *   - OLD (pre-Stage-6 / d=OFF): `git show HEAD:app/[locale]/(public)/search/
 *     page.tsx` (lines 147-273, 508-622, 747-750) — the actual last-committed
 *     version, predating the Stage 2/5/6 uncommitted diff.
 * g (Stage 5 rewrite) is toggled by calling vs. skipping the real
 * getMultiQueryPaths()/flattenPaths() from the bundle.
 *
 * Each mode runs in its own process invocation (npm script loops over
 * A/B/C/D) so the in-memory MULTI_CACHE inside searchRewrite.ts starts fresh
 * per mode — no cross-mode cache bleed.
 *
 * Usage: node run_mode.cjs --mode=A|B|C|D
 */
"use strict";
const fs = require("fs");
const path = require("path");
require("dotenv").config({ path: "/Users/baobaoli/Desktop/curify-frontend/.env.local" });

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const OUT_DIR = __dirname;
const bundle = require(path.join(OUT_DIR, "_bundle_stage56.cjs"));

const argv = process.argv.slice(2);
const modeArg = (argv.find((a) => a.startsWith("--mode=")) || "").split("=")[1];
if (!["A", "B", "C", "D"].includes(modeArg)) {
  console.error("Usage: node run_mode.cjs --mode=A|B|C|D");
  process.exit(1);
}
const D_ON = modeArg === "B" || modeArg === "D";
const G_ON = modeArg === "C" || modeArg === "D";

const LOW_RESULT_THRESHOLD = 5; // page.tsx:52, confirmed both HEAD and working tree

// ---- Load 68-query manifest (authoritative source, see Stage 7 report) ----
const GOLD_CSV = path.join(
  "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.7",
  "gold_query_test_set_2026-07-07.csv"
);
// Minimal RFC4180 CSV parser (quoted fields, embedded commas/newlines,
// doubled-quote escaping) — avoids a cross-repo node_modules dependency.
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let i = 0;
  const n = text.length;
  while (i < n) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i += 2;
          continue;
        }
        inQuotes = false;
        i++;
        continue;
      }
      field += c;
      i++;
      continue;
    }
    if (c === '"') {
      inQuotes = true;
      i++;
      continue;
    }
    if (c === ",") {
      row.push(field);
      field = "";
      i++;
      continue;
    }
    if (c === "\r") {
      i++;
      continue;
    }
    if (c === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
      i++;
      continue;
    }
    field += c;
    i++;
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  const header = rows[0];
  return rows
    .slice(1)
    .filter((r) => r.length > 1 || (r.length === 1 && r[0] !== ""))
    .map((r) => Object.fromEntries(header.map((h, idx) => [h, r[idx] ?? ""])));
}
function parse(text) {
  return parseCsv(text);
}
const goldRows = parse(fs.readFileSync(GOLD_CSV, "utf-8"));
if (goldRows.length !== 68) throw new Error(`Expected 68 gold rows, got ${goldRows.length}`);

// ---- Load real catalog (read-only) ----
const nanoInspiration = JSON.parse(fs.readFileSync(path.join(CURIFY_ROOT, "public/data/nano_inspiration.json"), "utf-8"));
const nanoTemplates = JSON.parse(fs.readFileSync(path.join(CURIFY_ROOT, "public/data/nano_templates.json"), "utf-8"));
const TEMPLATE_TOPICS = bundle.buildTemplateTopicsMap(nanoTemplates);

// templateSearchBlob — mirror of page.tsx's construction (locale-scan en+zh)
const templateSearchBlob = new Map();
for (const loc of ["en", "zh"]) {
  let entries;
  try {
    entries = JSON.parse(fs.readFileSync(path.join(CURIFY_ROOT, `messages/${loc}/nano.json`), "utf-8"));
  } catch {
    continue;
  }
  for (const [tid, e] of Object.entries(entries)) {
    if (!e) continue;
    const parts = [e.category, e.title, e.description, e?.content?.sections?.what, e?.content?.sections?.who].filter(
      (v) => typeof v === "string" && v.length > 0
    );
    if (parts.length === 0) continue;
    const blob = parts.join(" ").toLowerCase();
    templateSearchBlob.set(tid, (templateSearchBlob.get(tid) ?? "") + " " + blob);
  }
}

// ---- STOPWORDS — verbatim from page.tsx (both OLD and NEW, unchanged) ----
const STOPWORDS = new Set([
  "the", "a", "an", "of", "in", "on", "is", "are", "and", "or", "to", "for", "with", "by", "at", "as", "be", "this", "that",
  "的", "了", "和", "及",
  "topic", "topics", "theme", "themes", "category", "categories", "insights", "highlights", "guide", "guides",
  "template",
]);

function normalizeForSearch(s) {
  return bundle.tsToSc(s.toLowerCase().replace(/×/g, "x"));
}

function relaxedPrimaryThreshold(n) {
  if (n <= 1) return 1;
  return Math.ceil(n / 2);
}
function bigramHitThreshold(n) {
  if (n <= 1) return 1;
  if (n <= 3) return 2;
  return 3;
}
function tokenInBlob(blob, t) {
  if (!t) return false;
  if (/[一-龥]/.test(t)) return blob.includes(t);
  const esc = t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(^|[^a-z0-9])${esc}([^a-z0-9]|$)`).test(blob);
}

// Split + plural-stem, shared by OLD and NEW (unchanged between the two).
function splitAndStem(query) {
  const normalizedQuery = normalizeForSearch(query);
  let primary = normalizedQuery
    .split(/[\s,，、。.:：=·\/|()\[\]+*]+/)
    .map((w) => w.trim())
    .filter((w) => w && !STOPWORDS.has(w));
  if (primary.length === 1) {
    let t = primary[0];
    if (/^[a-z]+s$/.test(t) && t.length >= 4 && !/(ss|us|is|os|as)$/.test(t)) {
      if (/[bcdfghjklmnpqrtvwz]ies$/.test(t) && t.length >= 5) t = t.slice(0, -3) + "y";
      else if (/(ches|shes|xes|zzes)$/.test(t) && t.length >= 5) t = t.slice(0, -2);
      else t = t.slice(0, -1);
      primary[0] = t;
    }
  }
  return { normalizedQuery, primary };
}

// ---- OLD (pre-Stage-6, d=OFF) buildSearchTokens — transcribed from
// `git show HEAD:app/[locale]/(public)/search/page.tsx` lines 147-212 ----
function buildSearchTokensOLD(query) {
  const { normalizedQuery, primary: split } = splitAndStem(query);
  let primary = split;
  const phraseResult = bundle.applyPhraseAliasRules(normalizedQuery, primary);
  primary = phraseResult.primary;
  const bigrams = [];
  if (!phraseResult.atomicEntityMatched && primary.length === 1 && /[一-龥]/.test(primary[0]) && primary[0].length >= 2) {
    const w = primary[0];
    for (let i = 0; i < w.length - 1; i++) {
      const bg = w.slice(i, i + 2);
      if (/^[一-龥]{2}$/.test(bg)) bigrams.push(bg);
    }
  }
  return { primary, bigrams, aliasGroups: phraseResult.aliasGroups };
}
function scoreBlobOLD(blob, tokens) {
  let primaryHits = 0;
  for (const t of tokens.primary) if (tokenInBlob(blob, t)) primaryHits++;
  const aliasGroups = tokens.aliasGroups ?? [];
  let groupHits = 0;
  for (const group of aliasGroups) if (group.some((alt) => tokenInBlob(blob, alt))) groupHits++;
  let bigramHits = 0;
  for (const t of tokens.bigrams) if (blob.includes(t)) bigramHits++;
  const requiredSlots = tokens.primary.length + aliasGroups.length;
  return { primaryHits: primaryHits + groupHits, bigramHits, allPrimary: primaryHits + groupHits === requiredSlots };
}

// ---- NEW (Stage 6, d=ON) buildSearchTokens — transcribed from the working
// tree's app/[locale]/(public)/search/page.tsx lines 151-241, 301-326 ----
function buildSearchTokensNEW(query) {
  const { normalizedQuery, primary: split } = splitAndStem(query);
  let primary = split;
  let expandedPrimary = [];
  let conceptGroups = [];
  for (const tok of primary) {
    if (/[一-龥]/.test(tok)) {
      const seg = bundle.segmentCJKToken(tok);
      expandedPrimary.push(...seg.tokens);
      conceptGroups.push(...seg.conceptGroups);
    } else {
      expandedPrimary.push(tok);
    }
  }
  expandedPrimary = [...new Set(expandedPrimary)];
  const phraseResult = bundle.applyPhraseAliasRulesExcluding(normalizedQuery, expandedPrimary, bundle.CJK_ATOMIC_PHRASES);
  primary = phraseResult.primary;
  const aliasGroups = [...conceptGroups, ...phraseResult.aliasGroups];
  return { primary, bigrams: [], aliasGroups };
}
function scoreBlobNEW(blob, tokens) {
  let primaryHitsOnly = 0;
  for (const t of tokens.primary) if (tokenInBlob(blob, t)) primaryHitsOnly++;
  const aliasGroups = tokens.aliasGroups ?? [];
  let groupHits = 0;
  for (const group of aliasGroups) if (group.some((alt) => tokenInBlob(blob, alt))) groupHits++;
  let bigramHits = 0;
  for (const t of tokens.bigrams) if (blob.includes(t)) bigramHits++;
  const requiredSlots = tokens.primary.length + aliasGroups.length;
  const relaxedThrPrimary = relaxedPrimaryThreshold(tokens.primary.length);
  const relaxedThrGroups = relaxedPrimaryThreshold(aliasGroups.length);
  const relaxedOk =
    (tokens.primary.length > 0 && primaryHitsOnly >= relaxedThrPrimary) ||
    (aliasGroups.length > 0 && groupHits >= relaxedThrGroups);
  return { primaryHits: primaryHitsOnly + groupHits, bigramHits, allPrimary: primaryHitsOnly + groupHits === requiredSlots, relaxedOk };
}

const buildSearchTokens = D_ON ? buildSearchTokensNEW : buildSearchTokensOLD;
const scoreBlobFn = D_ON ? scoreBlobNEW : scoreBlobOLD;

// ---- scoreQueryTokens — shared shape, relaxed-inclusion test parametrized ----
function scoreQueryTokens(tokens, promoteAllUnderStrictTpl = true) {
  const bigramThr = bigramHitThreshold(tokens.bigrams.length);
  const relaxedThrOLD = D_ON ? null : relaxedPrimaryThreshold(tokens.primary.length + tokens.aliasGroups.length);

  const strictTpl = new Set();
  for (const [tid, blob] of templateSearchBlob) {
    const s = scoreBlobFn(blob, tokens);
    const relaxedPass = D_ON ? s.relaxedOk : s.primaryHits >= relaxedThrOLD && relaxedThrOLD > 0;
    if (s.allPrimary || s.bigramHits >= bigramThr) strictTpl.add(tid);
    void relaxedPass; // template rail is strict-only in both OLD/NEW, kept for parity
  }
  const tplByI18n = strictTpl;

  const scored = [];
  const queryTokenSet = new Set(tokens.primary);
  for (const r of nanoInspiration) {
    if (promoteAllUnderStrictTpl && strictTpl.has(r.template_id)) {
      scored.push({ rec: r, score: 100, strict: true });
      continue;
    }
    const localeFields = Object.values(r.locales ?? {}).flatMap((l) => [l?.title, l?.category]);
    const { mergedTopics } = bundle.resolveTopics(r, TEMPLATE_TOPICS);
    const blob = normalizeForSearch(
      [r.id, r.template_id, ...(r.tags ?? []), ...mergedTopics, ...(r.search_aliases ?? []), ...Object.values(r.params ?? {}), ...localeFields]
        .filter((v) => typeof v === "string" && v.length > 0)
        .join(" ")
    );
    const s = scoreBlobFn(blob, tokens);
    const strictHit = s.allPrimary || s.bigramHits >= bigramThr;
    const relaxedHit = D_ON ? s.relaxedOk : s.primaryHits >= relaxedThrOLD && relaxedThrOLD > 0;

    let demoteToRelaxed = false;
    if (strictHit && !strictTpl.has(r.template_id)) {
      const topicalBlob = normalizeForSearch(
        [r.template_id, ...(r.tags ?? []), ...mergedTopics, ...(r.search_aliases ?? [])].filter((v) => typeof v === "string" && v.length > 0).join(" ")
      );
      const topicalScore = scoreBlobFn(topicalBlob, tokens);
      const topicalStrict = topicalScore.allPrimary || topicalScore.bigramHits >= bigramThr;
      if (!topicalStrict) {
        let paramWholePhrase = false;
        for (const pv of Object.values(r.params ?? {})) {
          if (typeof pv !== "string" || !pv) continue;
          const pvTokens = normalizeForSearch(pv).split(/\s+/).filter(Boolean);
          if (pvTokens.length === 0) continue;
          if (pvTokens.every((tok) => queryTokenSet.has(tok))) {
            paramWholePhrase = true;
            break;
          }
        }
        if (!paramWholePhrase) demoteToRelaxed = true;
      }
    }
    if (strictHit && !demoteToRelaxed) {
      scored.push({ rec: r, score: s.primaryHits + s.bigramHits, strict: true });
    } else if (D_ON ? relaxedHit : relaxedHit) {
      scored.push({ rec: r, score: s.primaryHits, strict: false });
    }
  }
  return { scored, strictTpl, tplByI18n };
}

function looksLikeGarbageQuery(q) {
  const t = q.trim();
  if (t.length < 2) return true;
  if (/\d+\.\d+\.\d+/.test(t)) return true;
  if (/\.[a-z]{2,4}(?:\s|$)/i.test(t)) return true;
  if (/_[a-z0-9]{4,}_|_[a-z0-9]{4,}\s|\s[a-z0-9]{4,}_/i.test(t)) return true;
  if (/^[a-z0-9]{20,}$/i.test(t)) return true;
  if (!/\s/.test(t) && t.length > 25 && /\d/.test(t) && /[A-Z]/.test(t) && /[a-z]/.test(t)) return true;
  return false;
}

function titleFor(rec) {
  const loc = rec.locales?.zh || rec.locales?.en || Object.values(rec.locales ?? {})[0];
  return loc?.title || rec.id;
}

async function runOne(query) {
  const tokens = buildSearchTokens(query);
  let baseResult;
  try {
    baseResult = scoreQueryTokens(tokens);
  } catch (e) {
    return { query, error: String(e && e.stack ? e.stack : e), timeout: false };
  }
  const inspirationById = new Map();
  for (const s of baseResult.scored) inspirationById.set(s.rec.id, s);
  const pathHitsById = new Map();
  for (const s of baseResult.scored) pathHitsById.set(s.rec.id, 1);
  let matchedTemplateIdsByI18nUnion = new Set(baseResult.tplByI18n);

  const initialThinCount = baseResult.scored.filter((s) => s.strict).length + matchedTemplateIdsByI18nUnion.size;
  const isGarbage = looksLikeGarbageQuery(query);

  let rewriteTriggered = false;
  let rewriteRaw = null;
  let rewriteParsed = null;
  let finalSearchQueries = [query];
  let usedPathsCount = 1;
  let rewriteError = null;
  let numberOfSearchPasses = 1;

  if (G_ON && initialThinCount < LOW_RESULT_THRESHOLD && query.length >= 2 && !isGarbage) {
    rewriteTriggered = true;
    let multi;
    try {
      multi = await bundle.getMultiQueryPaths(query);
    } catch (e) {
      rewriteError = String(e && e.message ? e.message : e);
      multi = { rewrites: [], decomposition: {} };
    }
    rewriteParsed = multi;
    const extraPaths = bundle.flattenPaths(query, multi);
    if (extraPaths.length > 0) {
      finalSearchQueries = [query, ...extraPaths];
      numberOfSearchPasses = finalSearchQueries.length;
      for (const p of extraPaths) {
        const pathTokens = buildSearchTokens(p);
        const pathResult = scoreQueryTokens(pathTokens, false);
        for (const id of pathResult.tplByI18n) matchedTemplateIdsByI18nUnion.add(id);
        for (const s of pathResult.scored) {
          const prev = inspirationById.get(s.rec.id);
          if (!prev || s.score > prev.score || (s.strict && !prev.strict)) inspirationById.set(s.rec.id, s);
          pathHitsById.set(s.rec.id, (pathHitsById.get(s.rec.id) ?? 0) + 1);
        }
      }
      usedPathsCount = 1 + extraPaths.length;
    }
  }

  if (usedPathsCount > 1) {
    for (const [id, sc] of inspirationById) {
      const hits = pathHitsById.get(id) ?? 1;
      if (hits <= 1) continue;
      const boost = 1 + Math.min(hits - 1, 5) * 0.08;
      inspirationById.set(id, { ...sc, score: sc.score * boost });
    }
  }

  const allScored = Array.from(inspirationById.values());
  const hasStrict = D_ON ? baseResult.scored.some((x) => x.strict) : allScored.some((x) => x.strict);
  const finalScored = allScored.filter((x) => (hasStrict ? x.strict : true)).sort((a, b) => b.score - a.score);
  const strictCount = finalScored.filter((x) => x.strict).length;
  const relaxedCount = finalScored.filter((x) => !x.strict).length;

  const top10 = finalScored.slice(0, 10).map((x, i) => ({
    rank: i + 1,
    result_id: x.rec.id,
    title: titleFor(x.rec),
    template_id: x.rec.template_id,
    tags: x.rec.tags ?? [],
    score: x.score,
    strict_or_relaxed: x.strict ? "strict" : "relaxed",
  }));

  return {
    query,
    mode: modeArg,
    d_enabled: D_ON,
    g_enabled: G_ON,
    primary_tokens: tokens.primary,
    alias_groups: tokens.aliasGroups,
    bigrams: tokens.bigrams,
    initial_result_count: initialThinCount,
    initial_zero_result: initialThinCount === 0,
    initial_low_result: initialThinCount < LOW_RESULT_THRESHOLD,
    low_result_threshold: LOW_RESULT_THRESHOLD,
    rewrite_triggered: rewriteTriggered,
    rewrite_error: rewriteError,
    rewrite_output: rewriteParsed,
    final_search_queries: finalSearchQueries,
    number_of_search_passes: numberOfSearchPasses,
    final_result_count: finalScored.length,
    final_zero_result: finalScored.length === 0,
    final_low_result: finalScored.length < LOW_RESULT_THRESHOLD,
    strict_result_count: strictCount,
    relaxed_result_count: relaxedCount,
    has_strict: hasStrict,
    top_results: top10,
  };
}

async function main() {
  const results = [];
  for (const row of goldRows) {
    const q = row.query;
    const r = await runOne(q);
    r.query_category = `${row.primary_scene || ""}/${row.secondary_scene || ""}`;
    r.priority = row.priority || "";
    r.confidence = row.confidence || "";
    results.push(r);
    process.stderr.write(`[mode ${modeArg}] ${results.length}/68  ${q.slice(0, 40)}  -> result=${r.final_result_count ?? "ERR"}\n`);
  }
  const outFile = path.join(OUT_DIR, `mode_${modeArg}_results.json`);
  fs.writeFileSync(outFile, JSON.stringify({ mode: modeArg, d_enabled: D_ON, g_enabled: G_ON, generatedAt: new Date().toISOString(), results }, null, 2));
  console.log(`Wrote ${outFile}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
