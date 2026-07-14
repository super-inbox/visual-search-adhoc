#!/usr/bin/env node
/**
 * Stage 7R Prompt 4A — Mode Contract engine. Runs ONE (query, mode) combo
 * through the real production pipeline, with `dEnabled` (lib/searchTokens.ts,
 * genuinely imported) and `gEnabled` (whether to invoke the Rewrite/Guard
 * pipeline at all) as EXPLICIT options — never git-history reconstruction,
 * never manual token/rewrite stripping.
 *
 * g=OFF: only the first-pass (original-query) score is computed. The
 * Rewrite Provider (bundle.getMultiQueryPaths, a real OpenAI call) and
 * Guard (bundle.flattenPathsWithDiagnostics) are never invoked.
 *
 * g=ON: this Mode Contract Smoke Test NEVER calls the real LLM
 * (bundle.getMultiQueryPaths). Instead, a fixed `rewriteFixture` (a
 * {rewrites, decomposition} object, the same shape getMultiQueryPaths
 * returns) is passed straight into the REAL
 * bundle.flattenPathsWithDiagnostics — proving the g/Guard wiring works,
 * without any model non-determinism or real API cost. (The later
 * full-68-rerun-v2 harness is the one that will call the real LLM.)
 */
"use strict";
const fs = require("fs");
const path = require("path");

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const bundle = require(path.join(__dirname, "_bundle_current.cjs"));
const { makeScoringModule, verifyAgainstLiveSource } = require("./scoring.cjs");

const scoring = makeScoringModule(bundle);
const { buildSearchTokens, scoreBlob, hasExecutableConstraint, bigramHitThreshold, normalizeForSearch } = scoring;

const LOW_RESULT_THRESHOLD = 5; // page.tsx:52, unchanged this stage

const nanoInspiration = JSON.parse(fs.readFileSync(path.join(CURIFY_ROOT, "public/data/nano_inspiration.json"), "utf-8"));
const nanoTemplates = JSON.parse(fs.readFileSync(path.join(CURIFY_ROOT, "public/data/nano_templates.json"), "utf-8"));
const TEMPLATE_TOPICS = bundle.buildTemplateTopicsMap(nanoTemplates);

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
    templateSearchBlob.set(tid, (templateSearchBlob.get(tid) ?? "") + " " + normalizeForSearch(parts.join(" ")));
  }
}
for (const [tid, topics] of TEMPLATE_TOPICS) {
  if (!topics || topics.length === 0) continue;
  templateSearchBlob.set(tid, (templateSearchBlob.get(tid) ?? "") + " " + topics.join(" "));
}

function catalogInfo() {
  return { catalogSize: nanoInspiration.length, templateCount: templateSearchBlob.size };
}

function scoreQueryTokens(tokens, promoteAllUnderStrictTpl) {
  const bigramThr = bigramHitThreshold(tokens.bigrams.length);
  const strictTpl = new Set();
  for (const [tid, blob] of templateSearchBlob) {
    const s = scoreBlob(blob, tokens);
    if (s.allPrimary || s.bigramHits >= bigramThr) strictTpl.add(tid);
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
    const s = scoreBlob(blob, tokens);
    let demoteToRelaxed = false;
    const strictHit = s.allPrimary || s.bigramHits >= bigramThr;
    if (strictHit && !strictTpl.has(r.template_id)) {
      const topicalBlob = normalizeForSearch(
        [r.template_id, ...(r.tags ?? []), ...mergedTopics, ...(r.search_aliases ?? [])].filter((v) => typeof v === "string" && v.length > 0).join(" ")
      );
      const topicalScore = scoreBlob(topicalBlob, tokens);
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
    } else if (s.relaxedOk) {
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

/**
 * Runs ONE (query, mode) combo. `dEnabled`/`gEnabled` are explicit,
 * required booleans (Section 8's Mode Contract). `rewriteFixture` (only
 * used when gEnabled=true) is a fixed {rewrites, decomposition} object —
 * NEVER a real LLM call in this Mode Contract Smoke Test.
 */
async function runOne(query, { dEnabled, gEnabled, rewriteFixture = null } = {}) {
  if (typeof dEnabled !== "boolean" || typeof gEnabled !== "boolean") {
    throw new Error("runOne requires explicit boolean dEnabled and gEnabled");
  }
  const diagnostics = { rejectedSlots: [], emptyTokenPaths: [], noValidRewritePath: false };
  const tokens = buildSearchTokens(query, { dEnabled });
  const baseResult = scoreQueryTokens(tokens, true);
  const inspirationById = new Map();
  for (const s of baseResult.scored) inspirationById.set(s.rec.id, s);
  const pathHitsById = new Map();
  for (const s of baseResult.scored) pathHitsById.set(s.rec.id, 1);
  let matchedTemplateIdsByI18nUnion = new Set(baseResult.tplByI18n);

  const initialThinCount = baseResult.scored.filter((s) => s.strict).length + matchedTemplateIdsByI18nUnion.size;
  const isGarbage = looksLikeGarbageQuery(query);

  let rewriteTriggered = false;
  let rewriteProviderCalled = false;
  let multi = { rewrites: [], decomposition: {} };
  let candidatePaths = [];
  let executedPathCount = 0;
  let usedPathsCount = 1;

  const lowResultGatePassed = initialThinCount < LOW_RESULT_THRESHOLD && query.length >= 2 && !isGarbage;

  if (gEnabled && lowResultGatePassed) {
    rewriteTriggered = true;
    // Mode Contract Smoke Test: NEVER call bundle.getMultiQueryPaths (the
    // real LLM). Use the fixed fixture instead — proves the g/Guard wiring
    // works without any model call.
    multi = rewriteFixture ?? { rewrites: [], decomposition: {} };
    rewriteProviderCalled = false;

    const { executed, rejected } = bundle.flattenPathsWithDiagnostics(query, multi);
    candidatePaths = executed;
    diagnostics.rejectedSlots = rejected;

    for (const candidate of candidatePaths) {
      const pathTokens = buildSearchTokens(candidate.text, { dEnabled });
      if (!hasExecutableConstraint(pathTokens)) {
        diagnostics.emptyTokenPaths.push({ slotKey: candidate.slotKey, path: candidate.text });
        continue;
      }
      executedPathCount++;
      const pathResult = scoreQueryTokens(pathTokens, false);
      for (const id of pathResult.tplByI18n) matchedTemplateIdsByI18nUnion.add(id);
      for (const s of pathResult.scored) {
        const prev = inspirationById.get(s.rec.id);
        if (!prev || s.score > prev.score || (s.strict && !prev.strict)) inspirationById.set(s.rec.id, s);
        pathHitsById.set(s.rec.id, (pathHitsById.get(s.rec.id) ?? 0) + 1);
      }
    }
    if (candidatePaths.length > 0) usedPathsCount = 1 + executedPathCount;
    if (executedPathCount === 0) diagnostics.noValidRewritePath = true;
  }

  const preMergeCount = baseResult.scored.length;
  if (usedPathsCount > 1) {
    for (const [id, sc] of inspirationById) {
      const hits = pathHitsById.get(id) ?? 1;
      if (hits <= 1) continue;
      const boost = 1 + Math.min(hits - 1, 5) * 0.08;
      inspirationById.set(id, { ...sc, score: sc.score * boost });
    }
  }
  const postMergeCount = inspirationById.size;
  const allScored = Array.from(inspirationById.values());
  const hasStrict = baseResult.scored.some((x) => x.strict);
  const finalScored = allScored.filter((x) => (hasStrict ? x.strict : true)).sort((a, b) => b.score - a.score);

  const top10 = finalScored.slice(0, 10).map((x, i) => ({
    rank: i + 1,
    result_id: x.rec.id,
    title: titleFor(x.rec),
    template_id: x.rec.template_id,
    score: x.score,
    strict_or_relaxed: x.strict ? "strict" : "relaxed",
  }));

  return {
    query,
    dEnabled,
    gEnabled,
    tokens,
    initialThinCount,
    rewriteTriggered,
    rewriteProviderCalled,
    multi,
    candidatePaths,
    diagnostics,
    executedPathCount,
    usedPathsCount,
    preMergeCount,
    postMergeCount,
    dedupCount: postMergeCount,
    finalResultCount: finalScored.length,
    top10,
  };
}

module.exports = {
  bundle,
  scoring,
  verifyAgainstLiveSource,
  catalogInfo,
  buildSearchTokens,
  scoreBlob,
  hasExecutableConstraint,
  scoreQueryTokens,
  runOne,
  CURIFY_ROOT,
};
