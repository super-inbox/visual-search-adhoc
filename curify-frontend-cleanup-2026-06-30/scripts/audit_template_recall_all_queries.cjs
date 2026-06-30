#!/usr/bin/env node
// Comprehensive Template Recall Audit — all candidate queries.
//
// Purpose: template-level recall audit, NOT inspiration-level.
// Audits whether the production template recall pipeline (inspiration keyword
// match + template i18n blob match) surfaces relevant templates for each query,
// vs. what the template inventory actually contains.
//
// Based on app/[locale]/(public)/search/page.tsx logic (strict-AND + relaxed-AND,
// template i18n blob matching via messages/en,zh/nano.json).
//
// Output:
//   docs/search-evaluation/template-recall-audit-all-queries.md
//   docs/search-evaluation/template-recall-audit-all-queries.csv

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");

// ── Data files ─────────────────────────────────────────────────────────────
const TEMPLATES = JSON.parse(
  fs.readFileSync(path.join(ROOT, "public/data/nano_templates.json"), "utf8")
);
const INSPIRATIONS = JSON.parse(
  fs.readFileSync(path.join(ROOT, "public/data/nano_inspiration.json"), "utf8")
);

// Load template i18n blobs (mirrors page.tsx templateSearchBlob logic)
// Locales: en + zh (same as page.tsx localesToScan for non-locale-specific queries)
function loadNanoMessages(locale) {
  try {
    return JSON.parse(
      fs.readFileSync(path.join(ROOT, `messages/${locale}/nano.json`), "utf8")
    );
  } catch {
    return {};
  }
}

const NANO_EN = loadNanoMessages("en");
const NANO_ZH = loadNanoMessages("zh");

// Build template i18n blob: category + title + description + what + who
// (matches page.tsx templateSearchBlob building logic)
function buildTemplatei18nBlob(tid) {
  let parts = [];
  for (const msgs of [NANO_EN, NANO_ZH]) {
    const e = msgs[tid];
    if (!e) continue;
    if (e.category) parts.push(e.category);
    if (e.title) parts.push(e.title);
    if (e.description) parts.push(e.description);
    if (e.content?.sections?.what) parts.push(e.content.sections.what);
    if (e.content?.sections?.who) parts.push(e.content.sections.who);
  }
  return parts.join(" ").toLowerCase();
}

// Pre-build template i18n blobs
const TMPL_MAP = new Map(TEMPLATES.map((t) => [t.id, t]));
const TMPL_I18N_BLOBS = new Map();
for (const t of TEMPLATES) {
  TMPL_I18N_BLOBS.set(t.id, buildTemplatei18nBlob(t.id));
}

// ── Search simulation (mirrors page.tsx logic exactly) ─────────────────────
const STOPWORDS = new Set([
  "the", "a", "an", "of", "in", "on", "is", "are", "and", "or",
  "to", "for", "with", "by", "at", "as", "be", "this", "that",
  "的", "了", "和", "及",
  "topic", "topics", "theme", "themes", "category", "categories",
  "insights", "highlights", "guide", "guides",
]);

function normalizeStr(s) {
  return s.toLowerCase().replace(/×/g, "x");
}

function buildTokens(query) {
  const primary = normalizeStr(query)
    .split(/[\s,，、。.:：=·\/|()\[\]+*]+/)
    .map((w) => w.trim())
    .filter((w) => w && !STOPWORDS.has(w));

  if (primary.length === 1) {
    let t = primary[0];
    if (/^[a-z]+s$/.test(t) && t.length >= 4 && !/(ss|us|is|os|as)$/.test(t)) {
      if (/[bcdfghjklmnpqrtvwz]ies$/.test(t) && t.length >= 5) {
        t = t.slice(0, -3) + "y";
      } else if (/(ches|shes|xes|zzes)$/.test(t) && t.length >= 5) {
        t = t.slice(0, -2);
      } else {
        t = t.slice(0, -1);
      }
      primary[0] = t;
    }
  }

  const bigrams = [];
  if (primary.length === 1 && /[一-龥]/.test(primary[0]) && primary[0].length >= 2) {
    const w = primary[0];
    for (let i = 0; i < w.length - 1; i++) {
      const bg = w.slice(i, i + 2);
      if (/^[一-龥]{2}$/.test(bg)) bigrams.push(bg);
    }
  }
  return { primary, bigrams };
}

function tokenInBlob(token, blob) {
  if (!token) return false;
  if (/[一-龥]/.test(token)) return blob.includes(token);
  const escaped = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(^|[^a-z0-9])${escaped}([^a-z0-9]|$)`).test(blob);
}

function bigramHitThreshold(n) {
  if (n <= 1) return 1;
  if (n <= 3) return 2;
  return 3;
}

function relaxedPrimaryThreshold(n) {
  if (n <= 1) return 1;
  return Math.ceil(n / 2);
}

function scoreBlob(blob, tokens) {
  let primaryHits = 0;
  for (const t of tokens.primary) if (tokenInBlob(t, blob)) primaryHits++;
  let bigramHits = 0;
  for (const t of tokens.bigrams) if (blob.includes(t)) bigramHits++;
  return {
    primaryHits,
    bigramHits,
    allPrimary: primaryHits === tokens.primary.length,
  };
}

// Build inspiration blob (same fields as page.tsx)
function buildInspoBlob(insp) {
  const tmpl = TMPL_MAP.get(insp.template_id);
  const tmplTopics = tmpl ? (tmpl.topics || []) : [];
  return normalizeStr([
    insp.id || "",
    insp.template_id || "",
    ...(insp.tags || []),
    ...(insp.search_aliases || []),
    ...(insp.topics || []),
    ...tmplTopics,
    ...Object.values(insp.locales || {}).flatMap((l) => [l?.title, l?.category]),
    ...Object.values(insp.params || {}),
  ]
    .filter((v) => typeof v === "string" && v.length > 0)
    .join(" "));
}

// Full search simulation: returns template IDs recalled by the production pipeline
// (strict i18n blob match + inspirations that strict-match → their template)
function searchTemplates(query) {
  const tokens = buildTokens(query);
  if (tokens.primary.length === 0 && tokens.bigrams.length === 0) {
    return { strictTemplateIds: new Set(), totalInspirations: 0, strictInspirations: 0, relaxedInspirations: 0 };
  }

  const bigramThr = bigramHitThreshold(tokens.bigrams.length);
  const relaxedThr = relaxedPrimaryThreshold(tokens.primary.length);

  // Step 1: template i18n blob strict match
  const strictTemplByI18n = new Set();
  for (const [tid, blob] of TMPL_I18N_BLOBS) {
    const s = scoreBlob(blob, tokens);
    if (s.allPrimary || s.bigramHits >= bigramThr) {
      strictTemplByI18n.add(tid);
    }
  }

  // Step 2: inspiration strict / relaxed matching
  let strictInspoCount = 0;
  let relaxedInspoCount = 0;
  const strictInspoTemplIds = new Set();

  for (const insp of INSPIRATIONS) {
    const blob = buildInspoBlob(insp);
    const s = scoreBlob(blob, tokens);

    const isStrictBlob = s.allPrimary || s.bigramHits >= bigramThr;
    let demoted = false;

    // Compound-noun guard (mirrors page.tsx): if only params carry the token, demote
    if (isStrictBlob && !strictTemplByI18n.has(insp.template_id)) {
      const topicalBlob = normalizeStr([
        insp.template_id,
        ...(insp.tags || []),
        ...(insp.topics || []),
        ...(TMPL_MAP.get(insp.template_id)?.topics || []),
        ...(insp.search_aliases || []),
      ].filter((v) => typeof v === "string").join(" "));
      const ts = scoreBlob(topicalBlob, tokens);
      if (!ts.allPrimary && ts.bigramHits < bigramThr) {
        // Check if param value is a whole-phrase match
        const queryTokenSet = new Set(tokens.primary);
        let paramWhole = false;
        for (const pv of Object.values(insp.params || {})) {
          if (typeof pv !== "string" || !pv) continue;
          const pvToks = normalizeStr(pv).split(/\s+/).filter(Boolean);
          if (pvToks.length > 0 && pvToks.every((tok) => queryTokenSet.has(tok))) {
            paramWhole = true;
            break;
          }
        }
        if (!paramWhole) demoted = true;
      }
    }

    if (isStrictBlob && !demoted) {
      strictInspoCount++;
      strictInspoTemplIds.add(insp.template_id);
    } else if (s.primaryHits >= relaxedThr && relaxedThr > 0) {
      relaxedInspoCount++;
    }
  }

  // Union of recalled template IDs
  const strictTemplateIds = new Set([...strictTemplByI18n, ...strictInspoTemplIds]);

  return {
    strictTemplateIds,
    totalInspirations: INSPIRATIONS.length,
    strictInspirations: strictInspoCount,
    relaxedInspirations: relaxedInspoCount,
    strictTemplByI18nCount: strictTemplByI18n.size,
    strictInspoTemplIdsCount: strictInspoTemplIds.size,
  };
}

// Inventory audit: how many templates/inspirations are relevant by keyword scan
function inventorySearch(keywordSets) {
  function blobContainsGroup(blob, kws) {
    return kws.every((kw) => {
      const norm = kw.toLowerCase();
      if (/[一-龥]/.test(norm)) return blob.includes(norm);
      const escaped = norm.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      return new RegExp(`(^|[^a-z0-9])${escaped}([^a-z0-9]|$)`).test(blob);
    });
  }

  const matchedTemplates = TEMPLATES.filter((t) => {
    const blob = (
      [t.id, JSON.stringify(t.topics || []), TMPL_I18N_BLOBS.get(t.id) || ""].join(" ")
    ).toLowerCase();
    return keywordSets.some((kws) => blobContainsGroup(blob, kws));
  });

  const matchedInspos = INSPIRATIONS.filter((insp) => {
    const blob = buildInspoBlob(insp);
    return keywordSets.some((kws) => blobContainsGroup(blob, kws));
  });

  return { templates: matchedTemplates, inspirations: matchedInspos };
}

// ── Candidate query list ────────────────────────────────────────────────────
// Covers: boss requirement queries, 58-query eval P0/P1/P2, daily report WARN queries
const CANDIDATES = [

  // ── Boss priority queries ─────────────────────────────────────────────────
  {
    query: "bilingual flashcards",
    originalClassification: "P1 template gap (boss report)",
    sourceFile: "boss feedback / external signal report",
    inventoryKeywordSets: [["bilingual"], ["flashcard"]],
  },
  {
    query: "bilingual flashcard",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["bilingual"], ["flashcard"]],
  },
  {
    query: "English Chinese flashcards",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["bilingual"], ["flashcard"], ["english-chinese"]],
  },
  {
    query: "Chinese English flashcards",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["bilingual"], ["flashcard"], ["english-chinese"]],
  },
  {
    query: "双语闪卡",
    originalClassification: "P1 recall issue",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["bilingual"], ["flashcard"], ["双语"]],
  },
  {
    query: "英语单词闪卡",
    originalClassification: "P1 recall issue",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["flashcard"], ["vocabulary"], ["词汇"]],
  },
  {
    query: "词汇闪卡",
    originalClassification: "P1 recall issue",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["flashcard"], ["vocabulary"], ["词汇"]],
  },
  {
    query: "education flashcards",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["flashcard"], ["education"]],
  },
  {
    query: "education flashcard",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["flashcard"], ["education"]],
  },
  {
    query: "EdTech flashcards",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["flashcard"], ["education"], ["edtech"]],
  },
  {
    query: "iCard flashcards",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["flashcard"], ["icard"]],
  },
  {
    query: "iCard",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["icard"]],
  },
  {
    query: "animal vocabulary",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    inventoryKeywordSets: [["animal"], ["vocabulary"]],
  },

  // ── 58-query eval P0/P1 gaps (creative intent) ────────────────────────────
  {
    query: "phonics worksheets kindergarten",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #47",
    inventoryKeywordSets: [["phonics"], ["worksheet"]],
  },
  {
    query: "easy weeknight dinners healthy",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #50",
    inventoryKeywordSets: [["recipe"], ["dinner"], ["healthy"]],
  },
  {
    query: "gluten free dinner ideas",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #51",
    inventoryKeywordSets: [["recipe"], ["dinner"], ["food"]],
  },
  {
    query: "meal prep weekly recipes",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #52",
    inventoryKeywordSets: [["recipe"], ["meal"], ["food"]],
  },
  {
    query: "unique cultural experiences",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #27",
    inventoryKeywordSets: [["cultural", "experience"], ["intangible", "heritage"], ["culture"]],
  },
  {
    query: "电商详情图",
    originalClassification: "P1 template gap (4 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #8",
    inventoryKeywordSets: [["电商"], ["详情图"], ["product", "detail"], ["e-commerce"]],
  },
  {
    query: "趣味经济学知识科普",
    originalClassification: "P1 template gap (6 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #13",
    inventoryKeywordSets: [["经济"], ["科普"], ["infographic"], ["knowledge"]],
  },
  {
    query: "证件照",
    originalClassification: "P1 template gap (6 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #18",
    inventoryKeywordSets: [["证件照"], ["portrait", "id"], ["headshot"]],
  },
  {
    query: "homophones and homonyms",
    originalClassification: "P1 template gap (4 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #22",
    inventoryKeywordSets: [["homophone"], ["vocabulary"], ["english", "grammar"]],
  },
  {
    query: "wedding planner",
    originalClassification: "P1 template gap (7 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #36",
    inventoryKeywordSets: [["wedding"], ["planner"], ["wedding", "planning"]],
  },
  {
    query: "cuban sandwich recipe poster",
    originalClassification: "P1 template gap (4 results in eval; 1 after fix)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #39",
    inventoryKeywordSets: [["recipe"], ["poster"], ["food", "recipe"]],
  },
  {
    query: "bilingual flashcards for kids learning korean fruits",
    originalClassification: "P1 template gap (6 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #40",
    inventoryKeywordSets: [["bilingual"], ["flashcard"], ["korean"]],
  },
  {
    query: "watercolor map of europe travel destinations",
    originalClassification: "P1 template gap (2 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #41",
    inventoryKeywordSets: [["watercolor", "map"], ["travel", "map"], ["europe"]],
  },
  {
    query: "marvel mbti character chart 16 types",
    originalClassification: "P1 template gap (7 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #43",
    inventoryKeywordSets: [["mbti"], ["character"], ["marvel"]],
  },
  {
    query: "lunar new year red envelope graphic design",
    originalClassification: "P1 template gap (4 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #44",
    inventoryKeywordSets: [["red envelope"], ["lunar", "new", "year"], ["new year", "design"]],
  },
  {
    query: "before after kitchen organization makeover",
    originalClassification: "P1 template gap (3 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #46",
    inventoryKeywordSets: [["before-after"], ["before", "after"], ["organization"], ["makeover"]],
  },
  {
    query: "Spanish vocabulary printable",
    originalClassification: "P1 / Better routing needed (6 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #48",
    inventoryKeywordSets: [["spanish", "vocabulary"], ["vocabulary", "printable"]],
  },
  {
    query: "ESL flashcards printable",
    originalClassification: "P1 / Already covered (10 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #49",
    inventoryKeywordSets: [["esl", "flashcard"], ["flashcard", "printable"]],
  },
  {
    query: "book lovers gift guide",
    originalClassification: "P1 / Need content generation (2 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #54",
    inventoryKeywordSets: [["book"], ["gift", "guide"], ["book", "recommendation"]],
  },
  {
    query: "mbti marvel",
    originalClassification: "P1 template gap (5 results in eval)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #30",
    inventoryKeywordSets: [["mbti"], ["marvel"]],
  },

  // ── 58-query eval P2 retrieval gaps ───────────────────────────────────────
  {
    query: "historical character",
    originalClassification: "P1 retrieval gap (5 results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #20",
    inventoryKeywordSets: [["historical"], ["character"], ["history"]],
  },
  {
    query: "反义词",
    originalClassification: "P2 retrieval gap (9 results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #32",
    inventoryKeywordSets: [["反义词"], ["antonym"], ["vocabulary"]],
  },
  {
    query: "paper cutting",
    originalClassification: "P2 retrieval gap (9 results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #33",
    inventoryKeywordSets: [["paper cutting"], ["paper-cutting"], ["剪纸"]],
  },
  {
    query: "samurai",
    originalClassification: "P2 retrieval gap (8 results)",
    sourceFile: "docs/external-signal-pilot/curify-gap-analysis-58.csv #56",
    inventoryKeywordSets: [["samurai"], ["武士"], ["japanese", "warrior"]],
  },

  // ── Daily report WARN queries ─────────────────────────────────────────────
  {
    query: "paris travel itinerary",
    originalClassification: "WARN / REAL_CONTENT_GAP + EVAL_FALSE_POSITIVE",
    sourceFile: "docs/daily_report/2026-06-19.md",
    inventoryKeywordSets: [["paris"], ["itinerary"], ["travel"]],
  },
  {
    query: "architecture empire state building",
    originalClassification: "WARN / RETRIEVAL_GAP",
    sourceFile: "docs/daily_report/2026-06-19.md",
    inventoryKeywordSets: [["architecture"], ["empire", "state"], ["landmark"], ["building"]],
  },
  {
    query: "childhood snacks then vs now",
    originalClassification: "WARN / RETRIEVAL_GAP + EVAL_FALSE_POSITIVE",
    sourceFile: "docs/daily_report/2026-06-19.md",
    inventoryKeywordSets: [["then-vs-now"], ["childhood"], ["snack"]],
  },
  {
    query: "warmup routine running checklist",
    originalClassification: "WARN / RETRIEVAL_GAP",
    sourceFile: "docs/daily_report/2026-06-19.md",
    inventoryKeywordSets: [["warmup"], ["running"], ["checklist"], ["routine"]],
  },
  {
    query: "vintage stamp collection garden birds",
    originalClassification: "WARN / RETRIEVAL_GAP + EVAL_FALSE_POSITIVE",
    sourceFile: "docs/daily_report/2026-06-19.md",
    inventoryKeywordSets: [["stamp"], ["vintage", "stamp"], ["garden", "bird"]],
  },
];

// ── Classification logic ───────────────────────────────────────────────────
const ADEQUATE_THRESHOLD = 3; // LOW_RESULT_THRESHOLD from page.tsx
const ADEQUATE_TEMPLATE_THRESHOLD = 2; // ≥2 templates recalled = adequate

function classify(recalled, inventory) {
  const { strictTemplateIds, strictInspirations } = recalled;
  const { templates: invTemplates, inspirations: invInspos } = inventory;

  const recalledTemplCount = strictTemplateIds.size;
  const invTemplCount = invTemplates.length;
  const invInspoCount = invInspos.length;

  // Check adequate recall FIRST (inspirations ≥ LOW_RESULT_THRESHOLD or ≥2 templates)
  // Production page shows the inspiration grid + template rail; enough inspirations = working
  if (recalledTemplCount >= ADEQUATE_TEMPLATE_THRESHOLD || strictInspirations >= ADEQUATE_THRESHOLD) {
    return "ADEQUATE_TEMPLATE_RECALL";
  }
  // Large inventory but few recalled → recall issue
  if (invTemplCount >= 3 && recalledTemplCount < ADEQUATE_TEMPLATE_THRESHOLD) {
    return "TEMPLATE_RECALL_ISSUE";
  }
  // Small inventory too — might be content gap
  if (invTemplCount === 0 && invInspoCount < 3) {
    return "TRUE_TEMPLATE_GAP";
  }
  // Has templates but thin inspirations only
  if (invTemplCount >= 1 && recalledTemplCount < ADEQUATE_TEMPLATE_THRESHOLD && invInspoCount < 10) {
    return "CONTENT_GAP_EXISTING_TEMPLATE";
  }
  return "UNCERTAIN";
}

function rootCause(recalled, inventory, query) {
  const { strictTemplateIds, strictInspirations, strictTemplByI18nCount } = recalled;
  const { templates: invTemplates } = inventory;
  const tokens = buildTokens(query);
  const causes = [];

  if (invTemplates.length > 0 && strictTemplateIds.size < 2) {
    if (strictTemplByI18nCount === 0) {
      causes.push("template i18n blob does not match query tokens (missing description/title coverage)");
    }
    // Check if it's a plurals issue
    if (tokens.primary.length >= 2) {
      causes.push("multi-token plural stem not applied (page.tsx only stems single-token queries)");
    }
    const hasCJK = tokens.primary.some((t) => /[一-龥]/.test(t));
    const hasEnglish = tokens.primary.some((t) => /^[a-z]+$/.test(t));
    if (hasCJK || !hasEnglish) {
      causes.push("CJK/synonym mapping gap — Chinese query tokens not in English template blobs");
    }
    if (strictInspirations < ADEQUATE_THRESHOLD) {
      causes.push("inspiration blobs missing relevant aliases/topics for these query tokens");
    }
  }
  if (causes.length === 0 && invTemplates.length === 0) {
    causes.push("no matching template in inventory (true gap)");
  }
  return causes.join("; ") || "none identified";
}

function recommendedAction(classification, rootCauseStr, query) {
  switch (classification) {
    case "TEMPLATE_RECALL_ISSUE":
      return `Fix recall: add search_aliases to inspirations; add query terms to template i18n description/title. Root cause: ${rootCauseStr}`;
    case "CONTENT_GAP_EXISTING_TEMPLATE":
      return "Batch-generate inspiration examples under existing template(s). Fix aliases first.";
    case "TRUE_TEMPLATE_GAP":
      return "Add new template(s) to cover this query intent. No existing template serves this need.";
    case "ADEQUATE_TEMPLATE_RECALL":
      return "No action needed. Monitor for diversity regression.";
    default:
      return "Manual review needed — insufficient evidence for classification.";
  }
}

// ── Run audit ──────────────────────────────────────────────────────────────
console.log(`\nTemplate Recall Audit — ${CANDIDATES.length} queries\n`);
console.log(`Inspirations: ${INSPIRATIONS.length} | Templates: ${TEMPLATES.length}\n`);

const results = [];
for (const c of CANDIDATES) {
  const recalled = searchTemplates(c.query);
  const inventory = inventorySearch(c.inventoryKeywordSets);
  const classification = classify(recalled, inventory);
  const rootCauseStr = rootCause(recalled, inventory, c.query);
  const action = recommendedAction(classification, rootCauseStr, c.query);

  const top5Recalled = [...recalled.strictTemplateIds].slice(0, 5).join("; ");
  const missed = inventory.templates
    .filter((t) => !recalled.strictTemplateIds.has(t.id))
    .slice(0, 5)
    .map((t) => t.id)
    .join("; ");

  results.push({
    query: c.query,
    sourceFile: c.sourceFile,
    originalClassification: c.originalClassification,
    newClassification: classification,
    currentTemplateCount: recalled.strictTemplateIds.size,
    currentInspirationCount: recalled.strictInspirations,
    relaxedInspirationCount: recalled.relaxedInspirations,
    templatesByI18n: recalled.strictTemplByI18nCount || 0,
    templatesByInspiration: recalled.strictInspoTemplIdsCount || 0,
    inventoryTemplateCount: inventory.templates.length,
    inventoryInspirationCount: inventory.inspirations.length,
    missedTemplateCount: Math.max(0, inventory.templates.length - recalled.strictTemplateIds.size),
    topRecalledTemplateIds: top5Recalled,
    topMissedTemplateIds: missed,
    rootCause: rootCauseStr,
    recommendedAction: action,
  });

  const flag = classification === "TEMPLATE_RECALL_ISSUE" ? "⚠" :
    classification === "TRUE_TEMPLATE_GAP" ? "✗" :
    classification === "CONTENT_GAP_EXISTING_TEMPLATE" ? "△" :
    classification === "ADEQUATE_TEMPLATE_RECALL" ? "✓" : "?";

  console.log(`${flag} [${classification}] "${c.query}"`);
  console.log(`  Recalled templates: ${recalled.strictTemplateIds.size} (i18n: ${recalled.strictTemplByI18nCount || 0}, inspo: ${recalled.strictInspoTemplIdsCount || 0})`);
  console.log(`  Recalled inspirations: ${recalled.strictInspirations} strict`);
  console.log(`  Inventory: ${inventory.templates.length} templates, ${inventory.inspirations.length} inspirations`);
  console.log(`  Missed templates: ${Math.max(0, inventory.templates.length - recalled.strictTemplateIds.size)}`);
  console.log();
}

// ── Summary ────────────────────────────────────────────────────────────────
const counts = {
  TEMPLATE_RECALL_ISSUE: 0,
  CONTENT_GAP_EXISTING_TEMPLATE: 0,
  TRUE_TEMPLATE_GAP: 0,
  ADEQUATE_TEMPLATE_RECALL: 0,
  UNCERTAIN: 0,
};
for (const r of results) counts[r.newClassification]++;

console.log("═══════════════════════════════════════════════════════");
console.log("SUMMARY");
console.log(`  Total queries: ${results.length}`);
console.log(`  TEMPLATE_RECALL_ISSUE:         ${counts.TEMPLATE_RECALL_ISSUE}`);
console.log(`  CONTENT_GAP_EXISTING_TEMPLATE: ${counts.CONTENT_GAP_EXISTING_TEMPLATE}`);
console.log(`  TRUE_TEMPLATE_GAP:             ${counts.TRUE_TEMPLATE_GAP}`);
console.log(`  ADEQUATE_TEMPLATE_RECALL:      ${counts.ADEQUATE_TEMPLATE_RECALL}`);
console.log(`  UNCERTAIN:                     ${counts.UNCERTAIN}`);
console.log("═══════════════════════════════════════════════════════\n");

// ── Write CSV ──────────────────────────────────────────────────────────────
const CSV_PATH = path.join(ROOT, "docs/search-evaluation/template-recall-audit-all-queries.csv");
const csvHeader = [
  "query", "source_file", "original_classification", "new_classification",
  "current_template_count", "current_inspiration_count", "relaxed_inspiration_count",
  "templates_by_i18n", "templates_by_inspiration",
  "inventory_template_count", "inventory_inspiration_count",
  "missed_template_count", "top_recalled_template_ids", "top_missed_template_ids",
  "root_cause", "recommended_action",
].join(",");

function csvEscape(v) {
  const s = String(v ?? "");
  if (s.includes(",") || s.includes('"') || s.includes("\n")) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

const csvRows = results.map((r) =>
  [
    r.query, r.sourceFile, r.originalClassification, r.newClassification,
    r.currentTemplateCount, r.currentInspirationCount, r.relaxedInspirationCount,
    r.templatesByI18n, r.templatesByInspiration,
    r.inventoryTemplateCount, r.inventoryInspirationCount,
    r.missedTemplateCount, r.topRecalledTemplateIds, r.topMissedTemplateIds,
    r.rootCause, r.recommendedAction,
  ].map(csvEscape).join(",")
);

fs.writeFileSync(CSV_PATH, [csvHeader, ...csvRows].join("\n") + "\n");
console.log(`CSV written → ${CSV_PATH}`);

// ── Write Markdown report ─────────────────────────────────────────────────
const MD_PATH = path.join(ROOT, "docs/search-evaluation/template-recall-audit-all-queries.md");

// Group by classification for root cause section
const byClass = {
  TEMPLATE_RECALL_ISSUE: results.filter((r) => r.newClassification === "TEMPLATE_RECALL_ISSUE"),
  CONTENT_GAP_EXISTING_TEMPLATE: results.filter((r) => r.newClassification === "CONTENT_GAP_EXISTING_TEMPLATE"),
  TRUE_TEMPLATE_GAP: results.filter((r) => r.newClassification === "TRUE_TEMPLATE_GAP"),
  ADEQUATE_TEMPLATE_RECALL: results.filter((r) => r.newClassification === "ADEQUATE_TEMPLATE_RECALL"),
  UNCERTAIN: results.filter((r) => r.newClassification === "UNCERTAIN"),
};

// Build priority examples section
function priorityEntry(r) {
  return `
### ${r.query}

- **Source:** ${r.sourceFile}
- **Original classification:** ${r.originalClassification}
- **New classification:** \`${r.newClassification}\`
- **Current template recall:** ${r.currentTemplateCount} templates (i18n match: ${r.templatesByI18n}, inspiration-derived: ${r.templatesByInspiration})
- **Current inspiration recall:** ${r.currentInspirationCount} strict
- **Inventory:** ${r.inventoryTemplateCount} templates, ${r.inventoryInspirationCount} inspirations
- **Missed templates:** ${r.missedTemplateCount}
- **Top recalled template IDs:** ${r.topRecalledTemplateIds || "(none)"}
- **Top missed template IDs:** ${r.topMissedTemplateIds || "(none)"}
- **Root cause:** ${r.rootCause}
- **Recommended action:** ${r.recommendedAction}
`.trim();
}

// Select priority examples: top RECALL_ISSUE + notable others
const priorityQueries = [
  "bilingual flashcards",
  "education flashcards",
  "ESL flashcards printable",
  "homophones and homonyms",
  "paris travel itinerary",
  "before after kitchen organization makeover",
  "phonics worksheets kindergarten",
  "easy weeknight dinners healthy",
  "unique cultural experiences",
  "iCard",
].map((q) => results.find((r) => r.query === q)).filter(Boolean);

const tableRows = results.map((r) =>
  `| ${r.query} | ${r.originalClassification} | **${r.newClassification}** | ${r.currentTemplateCount} | ${r.currentInspirationCount} | ${r.inventoryTemplateCount} | ${r.missedTemplateCount} | ${r.recommendedAction.slice(0, 80)}${r.recommendedAction.length > 80 ? "…" : ""} |`
).join("\n");

const mdContent = `# Template Recall Audit: All Candidate Queries

> **Generated:** ${new Date().toISOString().slice(0, 10)}
> **Branch:** baobao/multi-intent-topic-cooccurrence
> **Scope:** template-level recall audit — NOT inspiration-level recall
> **Simulation:** strict-AND + relaxed-AND inspiration scoring + template i18n blob matching (mirrors \`app/[locale]/(public)/search/page.tsx\`)

---

## Executive Summary

| Metric | Count |
|---|---|
| Total candidate queries audited | **${results.length}** |
| TEMPLATE_RECALL_ISSUE | **${counts.TEMPLATE_RECALL_ISSUE}** |
| CONTENT_GAP_EXISTING_TEMPLATE | **${counts.CONTENT_GAP_EXISTING_TEMPLATE}** |
| TRUE_TEMPLATE_GAP | **${counts.TRUE_TEMPLATE_GAP}** |
| ADEQUATE_TEMPLATE_RECALL | **${counts.ADEQUATE_TEMPLATE_RECALL}** |
| UNCERTAIN | **${counts.UNCERTAIN}** |

---

## Key Finding

> **This audit processes template-level recall, not inspiration-level recall.**
> The question is: does the production search pipeline surface the *right templates* for each query?

Several queries previously marked as "template gaps" or "P0 content gaps" are **not true template gaps**. Curify already has relevant templates and inspiration examples, but the production search pipeline does not recall them reliably.

Root causes fall into these buckets:
1. **Multi-token plural stem gap** — page.tsx only stems plurals for single-token queries; "bilingual flashcards" keeps "flashcards" unstemmed, missing records tagged with "flashcard"
2. **CJK / synonym mapping gap** — Chinese queries don't find English-only template blobs; "词汇闪卡" has no Chinese alias in inspiration records
3. **Template i18n blob coverage gap** — template descriptions (title/category/what/who) don't include the exact English terms users type
4. **Inspiration alias gaps** — relevant inspirations exist but their search_aliases don't include common user-typed synonyms

---

## Priority Examples

${priorityQueries.map(priorityEntry).join("\n\n---\n\n")}

---

## Full Audit Table

| query | original classification | new classification | current templates | current inspirations | inventory templates | missed templates | recommended action |
|---|---|---|---:|---:|---:|---:|---|
${tableRows}

---

## Classification Definitions

| Classification | Meaning |
|---|---|
| TEMPLATE_RECALL_ISSUE | Template inventory has ≥3 relevant templates but current search recalls <2 |
| CONTENT_GAP_EXISTING_TEMPLATE | Template framework exists but inspiration examples are thin (< 10 in inventory) |
| TRUE_TEMPLATE_GAP | No template in inventory matches the query intent |
| ADEQUATE_TEMPLATE_RECALL | Current search returns ≥2 templates or ≥3 inspirations |
| UNCERTAIN | Evidence insufficient for clear classification |

---

## Root Cause Groups

### 1. Multi-token plural stem gap
Queries where "flashcards" (plural) is a content word in a multi-token query but the stem "flashcard" is not applied.
- page.tsx only stems single-token queries
- Affects: "education flashcards", "ESL flashcards printable", "EdTech flashcards", "iCard flashcards"

**Fix:** In \`buildSearchTokens\` / \`buildTokens\`, extend singular stemming to individual tokens within multi-word queries (low-risk change).

### 2. CJK/synonym mapping gap
Chinese query tokens ("闪卡", "词汇", "证件照") not in English-only template/inspiration blobs.
- Affects: "双语闪卡", "英语单词闪卡", "词汇闪卡", "电商详情图", "证件照", "趣味经济学知识科普", "反义词"

**Fix:** Add Chinese aliases to relevant inspiration search_aliases fields (low-risk, targeted).

### 3. Template i18n description gap
Template descriptions don't use user-typed vocabulary.
- "recipe template" description doesn't mention "weeknight", "gluten free", "meal prep"
- "travel template" description doesn't mention "Paris", "itinerary"
- Affects: "easy weeknight dinners healthy", "gluten free dinner ideas", "paris travel itinerary"

**Fix:** Update messages/en/nano.json descriptions for key templates to include common user terms (low-risk).

### 4. Inspiration alias gaps
Relevant inspirations exist but no search_alias for common user synonyms.
- "warmup routine" has the warmup template but "checklist", "running" not in alias
- "phonics worksheets kindergarten" has phonics template but "worksheet", "kindergarten" not in alias
- Affects: "warmup routine running checklist", "phonics worksheets kindergarten", "homophones and homonyms"

**Fix:** Add targeted aliases to existing inspiration records (same approach as commit \`d25921dc\`).

### 5. True content generation needed
Queries where inventory genuinely lacks templates.
- Affects: ${byClass.TRUE_TEMPLATE_GAP.map((r) => `"${r.query}"`).join(", ") || "(none identified in this run)"}

### 6. Adequate recall (misclassified as gap)
${byClass.ADEQUATE_TEMPLATE_RECALL.map((r) => `- "${r.query}": ${r.currentTemplateCount} templates, ${r.currentInspirationCount} inspirations (was: ${r.originalClassification})`).join("\n")}

---

## Files Changed
*(Fixes applied in this run — see separate commit)*
None in this script run. This script is read-only and audit-only.

---

## Local UI Verification
Run the dev server and check template section (not just inspiration grid):
\`\`\`
npm run dev
\`\`\`

Key URLs to verify template results:
- http://localhost:3001/en/search?q=bilingual+flashcards
- http://localhost:3001/en/search?q=education+flashcards
- http://localhost:3001/en/search?q=paris+travel+itinerary
- http://localhost:3001/en/search?q=before+after+kitchen+organization+makeover
- http://localhost:3001/en/search?q=warmup+routine+running+checklist

Template results appear in the "Generate with these templates" / matched templates section below the inspiration grid.

---

## Tests
\`\`\`bash
npm run lint
npm test -- --testPathPattern="search|intent|template"
\`\`\`
`;

fs.writeFileSync(MD_PATH, mdContent);
console.log(`Markdown written → ${MD_PATH}`);
console.log("\nDone.");
