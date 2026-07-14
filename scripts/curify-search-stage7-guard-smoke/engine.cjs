#!/usr/bin/env node
/**
 * Stage 7R Prompt 3 — shared search engine for Replay (Phase A) and Live
 * (Phase B). Mode D only (d=ON, g=ON — the current production path); this
 * smoke test is about validating Prompt 2's Guards on the real production
 * path, not re-running the A/B/C/D ablation from Stage 7.
 *
 * Genuinely-imported real production code (via ./_bundle_current.cjs):
 *   tsToSc, segmentCJKToken, applyPhraseAliasRulesExcluding,
 *   CJK_ATOMIC_PHRASES, getMultiQueryPaths, flattenPathsWithDiagnostics,
 *   buildTemplateTopicsMap, resolveTopics
 *
 * Transcribed page.tsx-local orchestration (see scoring.cjs for the
 * transcription + drift detector): buildSearchTokens, scoreBlob,
 * hasExecutableConstraint. scoreQueryTokens and the decomposition-path
 * merge loop below mirror page.tsx lines ~561-822 (as of Prompt 2),
 * including the Guard 1/2/3 wiring added in that stage.
 */
"use strict";
const fs = require("fs");
const path = require("path");

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const bundle = require(path.join(__dirname, "_bundle_current.cjs"));
const { makeScoringModule, verifyAgainstLiveSource } = require("./scoring.cjs");

const scoring = makeScoringModule(bundle);
const { buildSearchTokens, scoreBlob, hasExecutableConstraint, bigramHitThreshold, normalizeForSearch } = scoring;

const LOW_RESULT_THRESHOLD = 5; // page.tsx:52, unchanged by Prompt 2

// ---- Catalog (read-only) --------------------------------------------------
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

// scoreQueryTokens — mirrors page.tsx lines ~561-671 (unchanged by Prompt 2
// except for scoreBlob's own Guard 1 fix, which this calls into).
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
 * Runs the Mode-D (d=ON, g=ON) search path end to end, mirroring page.tsx's
 * SearchPage decomposition-path loop INCLUDING the Guard 1/2/3 wiring added
 * in Prompt 2 (lines ~719-800 as of that stage). `multiPathsOverride`, when
 * provided, is a real MultiQueryPaths object ({rewrites, decomposition})
 * used INSTEAD of calling the (real) getMultiQueryPaths — this is how Phase
 * A (Deterministic Replay) reuses the exact 7.13-recorded rewrite/
 * decomposition without any LLM call. When omitted, this function calls the
 * REAL getMultiQueryPaths (Phase B, Live Smoke) — a genuine OpenAI API call.
 */
async function runOne(query, { multiPathsOverride = null, forceRewrite = false } = {}) {
  const diagnostics = { rejectedSlots: [], emptyTokenPaths: [], noValidRewritePath: false };
  const tokens = buildSearchTokens(query);
  const baseResult = scoreQueryTokens(tokens, true);
  const inspirationById = new Map();
  for (const s of baseResult.scored) inspirationById.set(s.rec.id, s);
  const pathHitsById = new Map();
  for (const s of baseResult.scored) pathHitsById.set(s.rec.id, 1);
  let matchedTemplateIdsByI18nUnion = new Set(baseResult.tplByI18n);

  const initialThinCount = baseResult.scored.filter((s) => s.strict).length + matchedTemplateIdsByI18nUnion.size;
  const isGarbage = looksLikeGarbageQuery(query);

  let rewriteTriggered = false;
  let multi = { rewrites: [], decomposition: {} };
  let rewriteError = null;
  let candidatePaths = [];
  let executedPathCount = 0;
  let usedPathsCount = 1;
  let cacheHit = "NOT_APPLICABLE"; // real cache state is process-local inside the bundle; see live.cjs notes

  const lowResultGatePassed = initialThinCount < LOW_RESULT_THRESHOLD && query.length >= 2 && !isGarbage;

  if ((lowResultGatePassed || forceRewrite) && (multiPathsOverride || !multiPathsOverride)) {
    rewriteTriggered = true;
    if (multiPathsOverride) {
      // Phase A: Deterministic Replay — reuse 7.13-recorded rewrite/decomposition, no LLM call.
      multi = multiPathsOverride;
    } else {
      // Phase B: Live Smoke — real OpenAI call via the real bundled getMultiQueryPaths.
      try {
        multi = await bundle.getMultiQueryPaths(query);
      } catch (e) {
        rewriteError = String(e && e.message ? e.message : e);
        multi = { rewrites: [], decomposition: {} };
      }
    }

    const { executed, rejected } = bundle.flattenPathsWithDiagnostics(query, multi);
    candidatePaths = executed;
    diagnostics.rejectedSlots = rejected;

    for (const candidate of candidatePaths) {
      const pathTokens = buildSearchTokens(candidate.text);
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

  const preMergeCount = baseResult.scored.length; // baseline-only, before any rewrite path merged in
  if (usedPathsCount > 1) {
    for (const [id, sc] of inspirationById) {
      const hits = pathHitsById.get(id) ?? 1;
      if (hits <= 1) continue;
      const boost = 1 + Math.min(hits - 1, 5) * 0.08;
      inspirationById.set(id, { ...sc, score: sc.score * boost });
    }
  }
  const postMergeCount = inspirationById.size; // after union, before strict-filter/sort/slice
  const allScored = Array.from(inspirationById.values());
  const hasStrict = baseResult.scored.some((x) => x.strict);
  const finalScored = allScored.filter((x) => (hasStrict ? x.strict : true)).sort((a, b) => b.score - a.score);

  const top10 = finalScored.slice(0, 10).map((x, i) => ({
    rank: i + 1,
    result_id: x.rec.id,
    title: titleFor(x.rec),
    template_id: x.rec.template_id,
    tags: x.rec.tags ?? [],
    category: (x.rec.locales?.zh || x.rec.locales?.en || {}).category ?? null,
    score: x.score,
    strict_or_relaxed: x.strict ? "strict" : "relaxed",
  }));

  return {
    query,
    tokens,
    initialThinCount,
    rewriteTriggered,
    rewriteError,
    multi,
    candidatePaths,
    diagnostics,
    executedPathCount,
    usedPathsCount,
    preMergeCount,
    postMergeCount,
    dedupCount: postMergeCount, // inspirationById is itself the by-id dedup map
    finalResultCount: finalScored.length,
    strictCount: finalScored.filter((x) => x.strict).length,
    relaxedCount: finalScored.filter((x) => !x.strict).length,
    hasStrict,
    top10,
    cacheHit,
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
