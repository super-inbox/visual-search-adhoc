#!/usr/bin/env node
/**
 * Stage 7R Prompt 4A — page.tsx Merge/Ranking orchestration mirror.
 *
 * page.tsx is a Next.js Server Component and its scoreBlob/hasExecutable-
 * Constraint/scoreQueryTokens functions are module-private (not exported)
 * — there is no way to reach them from outside without either modifying
 * page.tsx (forbidden this stage, and Ranking/Merge changes are out of
 * scope entirely) or transcribing them, the same established pattern the
 * pre-existing curify-search-stage7-guard-smoke/scoring.cjs already uses.
 *
 * UNLIKE that pre-existing scoring.cjs, this file does NOT transcribe
 * buildSearchTokens/normalizeForSearch/STOPWORDS — those are now real,
 * exported, importable production code (lib/searchTokens.ts, Stage 7R
 * Prompt 4A) and are called directly from the bundle
 * (`bundle.buildSearchTokens(query, { dEnabled })`,
 * `bundle.normalizeForSearch`). Only scoreBlob/hasExecutableConstraint/
 * relaxedPrimaryThreshold/bigramHitThreshold/tokenInBlob (Merge/Ranking,
 * unmodified, out of scope this stage) remain transcribed.
 *
 * Drift protection: `verifyAgainstLiveSource()` reads the actual current
 * page.tsx file at call time and asserts specific critical substrings are
 * present. If page.tsx changes in a way that no longer contains these
 * exact substrings, this harness refuses to run rather than silently
 * testing stale/mismatched logic.
 */
"use strict";
const fs = require("fs");
const path = require("path");

const CURIFY_ROOT = "/Users/baobaoli/Desktop/curify-frontend";
const PAGE_TSX_PATH = path.join(CURIFY_ROOT, "app/[locale]/(public)/search/page.tsx");
const SEARCH_TOKENS_PATH = path.join(CURIFY_ROOT, "lib/searchTokens.ts");

function verifyAgainstLiveSource() {
  const src = fs.readFileSync(PAGE_TSX_PATH, "utf-8");
  const tokensSrc = fs.readFileSync(SEARCH_TOKENS_PATH, "utf-8");
  const checks = [
    {
      name: "Guard 1 fix present in scoreBlob (requiredSlots > 0 guard)",
      pattern: "allPrimary: requiredSlots > 0 && primaryHitsOnly + groupHits === requiredSlots,",
    },
    { name: "hasExecutableConstraint helper present", pattern: "function hasExecutableConstraint(tokens:" },
    { name: "page.tsx calls flattenPathsWithDiagnostics (Guard 2 wiring)", pattern: "flattenPathsWithDiagnostics(query, multi)" },
    { name: "Guard 3 diagnostic rejected-slot logging present", pattern: "errorType=${r.reason}" },
    { name: "Guard 3 diagnostic EMPTY_EXECUTABLE_TOKENS logging present", pattern: "errorType=EMPTY_EXECUTABLE_TOKENS" },
    { name: "Guard 3 diagnostic NO_VALID_REWRITE_PATH logging present", pattern: "errorType=NO_VALID_REWRITE_PATH" },
    { name: "relaxedPrimaryThreshold unchanged (n<=1 -> 1)", pattern: "if (n <= 1) return 1;" },
    { name: "page.tsx imports buildSearchTokens from lib/searchTokens (Prompt 4A wiring)", pattern: 'from "@/lib/searchTokens"' },
  ];
  const tokenChecks = [
    { name: "lib/searchTokens.ts exports SearchTokenizationOptions with dEnabled", pattern: "dEnabled?: boolean;" },
    { name: "lib/searchTokens.ts default dEnabled is true", pattern: "dEnabled: true," },
    { name: "lib/searchTokens.ts STOPWORDS still contains bare 'template'", pattern: '"template",' },
  ];
  const missing = checks.filter((c) => !src.includes(c.pattern));
  const missingTokens = tokenChecks.filter((c) => !tokensSrc.includes(c.pattern));
  const allMissing = [...missing, ...missingTokens];
  if (allMissing.length > 0) {
    const names = allMissing.map((m) => m.name).join("; ");
    throw new Error(
      `[scoring.cjs] DRIFT DETECTED: source no longer contains expected substring(s): ${names}. ` +
        `Refusing to run — this harness's transcription would no longer match the real production code.`
    );
  }
  const crypto = require("crypto");
  return {
    checked: checks.length + tokenChecks.length,
    missing: 0,
    pageTsxSha256: crypto.createHash("sha256").update(src).digest("hex"),
    searchTokensSha256: crypto.createHash("sha256").update(tokensSrc).digest("hex"),
  };
}

function makeScoringModule(bundle) {
  const normalizeForSearch = bundle.normalizeForSearch;

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

  // Stage 7R Prompt 4A — real production function, imported (not
  // transcribed). `options` ({ dEnabled }) is the ONLY new surface this
  // stage adds; omitting it is byte-identical to pre-Prompt-4A behavior.
  function buildSearchTokens(query, options) {
    return bundle.buildSearchTokens(query, options);
  }

  function hasExecutableConstraint(tokens) {
    return tokens.primary.length > 0 || (tokens.aliasGroups?.length ?? 0) > 0;
  }

  // Transcribed verbatim from app/[locale]/(public)/search/page.tsx
  // scoreBlob — Merge/Ranking, unmodified, out of scope this stage.
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
      allPrimary: requiredSlots > 0 && primaryHitsOnly + groupHits === requiredSlots,
      relaxedOk,
    };
  }

  return {
    normalizeForSearch,
    relaxedPrimaryThreshold,
    bigramHitThreshold,
    tokenInBlob,
    buildSearchTokens,
    scoreBlob,
    hasExecutableConstraint,
    STOPWORDS: bundle.STOPWORDS,
  };
}

module.exports = { makeScoringModule, verifyAgainstLiveSource, PAGE_TSX_PATH, SEARCH_TOKENS_PATH };
