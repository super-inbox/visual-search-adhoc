#!/usr/bin/env node
/**
 * Stage 7R Prompt 3 — page.tsx orchestration mirror.
 *
 * page.tsx is a Next.js Server Component (imports next/navigation,
 * next/headers) and cannot be require()'d/imported directly outside a
 * Next.js runtime, and its buildSearchTokens/scoreBlob/hasExecutableConstraint/
 * scoreQueryTokens functions are module-private (not exported) — there is no
 * way to reach them from outside without either modifying page.tsx (forbidden
 * this stage) or transcribing them. This is the SAME situation the existing
 * Stage 7 harness (scripts/curify-search-collect-stage7/run_mode.cjs) already
 * solved, by verbatim-transcribing the same functions with explicit
 * line-number provenance. This file follows that same established project
 * convention for Mode D (d=ON, g=ON — the current production path).
 *
 * Genuinely-importable production logic (Guard 2's actual implementation,
 * the LLM rewrite/decomposition pipeline, the CJK tokenizer, the phrase-
 * alias engine) is NOT transcribed here — it is required from
 * ./_bundle_current.cjs (see build_bundle.cjs), which bundles the real,
 * unmodified, CURRENT lib/*.ts source files via esbuild. Only the
 * page.tsx-local orchestration is transcribed.
 *
 * Drift protection: `verifyAgainstLiveSource()` reads the actual current
 * page.tsx file at call time and asserts specific critical substrings are
 * present — most importantly the Guard 1 fix
 * (`requiredSlots > 0 && primaryHitsOnly + groupHits === requiredSlots`) and
 * the STOPWORDS "template" entry. If page.tsx changes in a way that no
 * longer contains these exact substrings, this harness refuses to run
 * rather than silently testing stale/mismatched logic.
 */
"use strict";
const fs = require("fs");
const path = require("path");

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const PAGE_TSX_PATH = path.join(CURIFY_ROOT, "app/[locale]/(public)/search/page.tsx");

// ---- Drift detector ------------------------------------------------------
function verifyAgainstLiveSource() {
  const src = fs.readFileSync(PAGE_TSX_PATH, "utf-8");
  const checks = [
    {
      name: "Guard 1 fix present in scoreBlob (requiredSlots > 0 guard)",
      pattern: "allPrimary: requiredSlots > 0 && primaryHitsOnly + groupHits === requiredSlots,",
    },
    {
      name: "hasExecutableConstraint helper present",
      pattern: "function hasExecutableConstraint(tokens:",
    },
    {
      name: "STOPWORDS still contains bare 'template'",
      pattern: '"template",',
    },
    {
      name: "page.tsx calls flattenPathsWithDiagnostics (Guard 2 wiring)",
      pattern: "flattenPathsWithDiagnostics(query, multi)",
    },
    {
      // Stage 7R Prompt 2B: page.tsx's rejected-slot log line was
      // generalized from a hardcoded `errorType=UNBOUND_NON_SUBJECT_SLOT`
      // to `errorType=${r.reason}` so it also surfaces Guard R's new
      // rewrite[] rejection reasons (EMPTY_EXECUTABLE_TOKENS /
      // UNANCHORED_REWRITE_CANDIDATE) truthfully instead of mislabeling
      // them. This is a disclosed, hand-verified update to the drift
      // detector's own expected substring — not a loosening of what it
      // checks; UNBOUND_NON_SUBJECT_SLOT itself is unchanged and still the
      // reason Guard 2 reports for rejected decomposition slots (see
      // lib/searchRewrite.ts's RejectedSlot.reason union).
      name: "Guard 3 diagnostic rejected-slot logging present (generalized errorType=${r.reason} in Prompt 2B)",
      pattern: "errorType=${r.reason}",
    },
    {
      name: "Guard 3 diagnostic EMPTY_EXECUTABLE_TOKENS logging present",
      pattern: "errorType=EMPTY_EXECUTABLE_TOKENS",
    },
    {
      name: "Guard 3 diagnostic NO_VALID_REWRITE_PATH logging present",
      pattern: "errorType=NO_VALID_REWRITE_PATH",
    },
    {
      name: "relaxedPrimaryThreshold unchanged (n<=1 -> 1)",
      pattern: "if (n <= 1) return 1;",
    },
  ];
  const missing = checks.filter((c) => !src.includes(c.pattern));
  if (missing.length > 0) {
    const names = missing.map((m) => m.name).join("; ");
    throw new Error(
      `[scoring.cjs] DRIFT DETECTED: page.tsx no longer contains expected substring(s): ${names}. ` +
        `Refusing to run — this harness's transcription would no longer match the real production code. ` +
        `Do not modify this harness to "fix" the mismatch without re-verifying the transcription by hand.`
    );
  }
  return { checked: checks.length, missing: 0, sourceSha256: require("crypto").createHash("sha256").update(src).digest("hex") };
}

// ---- STOPWORDS — verbatim from page.tsx (unchanged by Prompt 2) ---------
const STOPWORDS = new Set([
  "the", "a", "an", "of", "in", "on", "is", "are", "and", "or", "to", "for", "with", "by", "at", "as", "be", "this", "that",
  "的", "了", "和", "及",
  "topic", "topics", "theme", "themes", "category", "categories", "insights", "highlights", "guide", "guides",
  "template",
]);

function makeScoringModule(bundle) {
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

  // Transcribed verbatim from app/[locale]/(public)/search/page.tsx
  // buildSearchTokens (working tree, lines ~151-241 as of Prompt 2).
  function buildSearchTokens(query) {
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

  // Guard 1 (Stage 7R Prompt 2), transcribed verbatim from page.tsx scoreBlob.
  function hasExecutableConstraint(tokens) {
    return tokens.primary.length > 0 || (tokens.aliasGroups?.length ?? 0) > 0;
  }

  function scoreBlob(blob, tokens) {
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
    return {
      primaryHits: primaryHitsOnly + groupHits,
      bigramHits,
      // Guard 1: requiredSlots > 0 is the fix — see page.tsx scoreBlob comment.
      allPrimary: requiredSlots > 0 && primaryHitsOnly + groupHits === requiredSlots,
      relaxedOk,
    };
  }

  return { normalizeForSearch, relaxedPrimaryThreshold, bigramHitThreshold, tokenInBlob, buildSearchTokens, scoreBlob, hasExecutableConstraint, STOPWORDS };
}

module.exports = { makeScoringModule, verifyAgainstLiveSource, PAGE_TSX_PATH };
