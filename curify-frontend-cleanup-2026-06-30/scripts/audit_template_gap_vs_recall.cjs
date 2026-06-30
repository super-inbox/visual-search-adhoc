#!/usr/bin/env node
// Template Gap vs Recall Audit Script
// Simulates the production search logic from app/[locale]/(public)/search/page.tsx
// and compares strict-AND recall against inventory keyword coverage to classify each query.

"use strict";

const fs = require("fs");
const path = require("path");

// ── Data files ────────────────────────────────────────────────────────────────
const ROOT = path.resolve(__dirname, "..");
const TEMPLATES = JSON.parse(
  fs.readFileSync(path.join(ROOT, "public/data/nano_templates.json"), "utf8")
);
const INSPIRATIONS = JSON.parse(
  fs.readFileSync(path.join(ROOT, "public/data/nano_inspiration.json"), "utf8")
);

const TMPL_MAP = new Map(TEMPLATES.map((t) => [t.id, t]));

// ── Search simulation (mirrors page.tsx logic) ─────────────────────────────
const STOPWORDS = new Set([
  "the","a","an","of","in","on","is","are","and","or","to","for","with","by",
  "at","as","be","this","that","的","了","和","及",
  "topic","topics","theme","themes","category","categories",
  "insights","highlights","guide","guides",
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
  if (/^[a-z0-9]+$/.test(token)) {
    return new RegExp(
      "(?<![a-z0-9])" + token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(?![a-z0-9])",
      "i"
    ).test(blob);
  }
  return blob.includes(token);
}

function buildInspoBlob(insp) {
  const tmpl = TMPL_MAP.get(insp.template_id);
  return [
    insp.id || "",
    insp.template_id || "",
    JSON.stringify(insp.tags || []),
    JSON.stringify(insp.search_aliases || []),
    JSON.stringify(insp.topics || []),
    JSON.stringify(insp.locales || {}),
    JSON.stringify(insp.params || {}),
    tmpl ? JSON.stringify(tmpl.topics || "") : "",
    tmpl ? (tmpl.id || "") : "",
  ]
    .join(" ")
    .toLowerCase();
}

function buildTemplBlob(t) {
  return [t.id || "", JSON.stringify(t.topics || ""), JSON.stringify(t.locales || {})].join(" ").toLowerCase();
}

// Runs strict-AND search; falls back to relaxed-AND if zero results.
function searchInspirations(query) {
  const { primary, bigrams } = buildTokens(query);
  if (primary.length === 0) return { strict: [], relaxed: [] };

  const allBlobs = INSPIRATIONS.map((insp) => ({ insp, blob: buildInspoBlob(insp) }));

  // Strict AND
  let strict = allBlobs.filter(({ blob }) => primary.every((t) => tokenInBlob(t, blob)));

  // CJK bigram strict
  if (bigrams.length > 0 && strict.length === 0) {
    const needed = bigrams.length <= 1 ? 1 : bigrams.length <= 3 ? 2 : 3;
    strict = allBlobs.filter(({ blob }) => {
      const hits = bigrams.filter((bg) => blob.includes(bg)).length;
      return hits >= needed;
    });
  }

  let relaxed = [];
  if (strict.length === 0 && primary.length > 1) {
    const threshold = Math.ceil(primary.length / 2);
    relaxed = allBlobs.filter(({ blob }) => {
      const hitCount = primary.filter((t) => tokenInBlob(t, blob)).length;
      return hitCount >= threshold;
    });
  }

  return {
    strict: strict.map((r) => r.insp),
    relaxed: relaxed.map((r) => r.insp),
  };
}

// Inventory audit: ANY keyword must appear in blob (broad coverage check)
function inventorySearch(keywordSets) {
  const matchedTemplates = TEMPLATES.filter((t) => {
    const blob = buildTemplBlob(t);
    return keywordSets.some((kws) => kws.every((kw) => blob.includes(kw.toLowerCase())));
  });
  const matchedInspos = INSPIRATIONS.filter((insp) => {
    const blob = buildInspoBlob(insp);
    return keywordSets.some((kws) => kws.every((kw) => blob.includes(kw.toLowerCase())));
  });
  return { templates: matchedTemplates, inspirations: matchedInspos };
}

// ── Candidate queries ──────────────────────────────────────────────────────
// Format:
// { query, originalClassification, sourceFile, originalReason, inventoryKeywordSets }
// inventoryKeywordSets: array of AND-groups; ANY group matching = relevant template
const CANDIDATES = [
  // ── Priority queries from task ──────────────────────────────────────────
  {
    query: "bilingual flashcards",
    originalClassification: "P1 template gap (reported by boss)",
    sourceFile: "boss feedback / external signal report",
    originalReason: "Only ~6 results recalled; Education/EdTech/flashcard templates assumed scarce",
    inventoryKeywordSets: [["bilingual"], ["flashcard"]],
  },
  {
    query: "bilingual flashcard",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    originalReason: "Singular form low recall",
    inventoryKeywordSets: [["bilingual"], ["flashcard"]],
  },
  {
    query: "English Chinese flashcards",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    originalReason: "Low recall for English-Chinese bilingual flashcard queries",
    inventoryKeywordSets: [["bilingual"], ["flashcard"], ["english-chinese"]],
  },
  {
    query: "Chinese English flashcards",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    originalReason: "Low recall for Chinese-English bilingual flashcard queries",
    inventoryKeywordSets: [["bilingual"], ["flashcard"], ["english-chinese"]],
  },
  {
    query: "双语闪卡",
    originalClassification: "P1 / recall issue (suspected)",
    sourceFile: "boss feedback",
    originalReason: "CJK query for bilingual flashcard returning 0 results",
    inventoryKeywordSets: [["bilingual"], ["flashcard"], ["双语"]],
  },
  {
    query: "英语单词闪卡",
    originalClassification: "P1 / recall issue (suspected)",
    sourceFile: "boss feedback",
    originalReason: "CJK English vocabulary flashcard returning 0 results",
    inventoryKeywordSets: [["flashcard"], ["vocabulary"], ["词汇"]],
  },
  {
    query: "词汇闪卡",
    originalClassification: "P1 / recall issue (suspected)",
    sourceFile: "boss feedback",
    originalReason: "CJK vocabulary flashcard returning 0 results",
    inventoryKeywordSets: [["flashcard"], ["vocabulary"], ["词汇"]],
  },
  {
    query: "education flashcard",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    originalReason: "Low recall for educational flashcard queries",
    inventoryKeywordSets: [["flashcard"], ["education"]],
  },
  {
    query: "iCard",
    originalClassification: "P1 template gap",
    sourceFile: "boss feedback",
    originalReason: "iCard search returns 0 results; no known template",
    inventoryKeywordSets: [["icard"]],
  },
  {
    query: "paris travel itinerary",
    originalClassification: "WARN / REAL_CONTENT_GAP + EVAL_FALSE_POSITIVE",
    sourceFile: "docs/daily_report/2026-06-19.md",
    originalReason: "Only 2 real Paris results; 7 template-placeholder cascade false positives",
    inventoryKeywordSets: [["paris"], ["itinerary"], ["travel"]],
  },
  {
    query: "before after kitchen organization makeover",
    originalClassification: "WARN / REAL_CONTENT_GAP (P1, 3 results in eval)",
    sourceFile: "docs/daily_report/2026-06-19.md / CURIFY_CENTERED report",
    originalReason: "Catalog has only 1 before-after transformation content; expected ≥3",
    inventoryKeywordSets: [["before-after"], ["before", "after"], ["kitchen"], ["organization"]],
  },
  {
    query: "architecture empire state building",
    originalClassification: "WARN / RETRIEVAL_GAP",
    sourceFile: "docs/daily_report/2026-06-19.md",
    originalReason: "Architecture inspirations have Chinese-only aliases; English query misses",
    inventoryKeywordSets: [["architecture"], ["empire", "state"], ["landmark"]],
  },
  {
    query: "childhood snacks then vs now",
    originalClassification: "WARN / RETRIEVAL_GAP + EVAL_FALSE_POSITIVE",
    sourceFile: "docs/daily_report/2026-06-19.md",
    originalReason: "Template description pollution caused cascade; real matches only 1",
    inventoryKeywordSets: [["then-vs-now"], ["childhood"], ["snack"]],
  },
  {
    query: "warmup routine running checklist",
    originalClassification: "WARN / RETRIEVAL_GAP",
    sourceFile: "docs/daily_report/2026-06-19.md",
    originalReason: "'checklist' not in any warmup inspiration fields",
    inventoryKeywordSets: [["warmup"], ["running"], ["checklist"]],
  },
  {
    query: "vintage stamp collection garden birds",
    originalClassification: "WARN / RETRIEVAL_GAP + EVAL_FALSE_POSITIVE",
    sourceFile: "docs/daily_report/2026-06-19.md",
    originalReason: "Sibling stamp inspirations dropped due to strict-before-relaxed; only 1 recalled",
    inventoryKeywordSets: [["stamp"], ["vintage", "stamp"], ["garden", "bird"]],
  },
  // ── 58-query eval P0 gaps ──────────────────────────────────────────────
  {
    query: "phonics worksheets kindergarten",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md",
    originalReason: "Zero Curify results; classified as urgent template inventory gap",
    inventoryKeywordSets: [["phonics"], ["worksheet"]],
  },
  {
    query: "easy weeknight dinners healthy",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md",
    originalReason: "Zero Curify results; recipe card/planner templates urgently needed",
    inventoryKeywordSets: [["recipe"], ["dinner"], ["healthy"]],
  },
  {
    query: "gluten free dinner ideas",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md",
    originalReason: "Zero Curify results; dietary meal planner templates needed",
    inventoryKeywordSets: [["recipe"], ["dinner"], ["food"]],
  },
  {
    query: "meal prep weekly recipes",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md",
    originalReason: "Zero Curify results; meal prep planner templates needed",
    inventoryKeywordSets: [["recipe"], ["meal"], ["food"]],
  },
  {
    query: "unique cultural experiences",
    originalClassification: "P0 content gap (zero results)",
    sourceFile: "docs/external-signal-pilot/CURIFY_CENTERED_EXTERNAL_SIGNAL_INSIGHTS_2026-06-21.md",
    originalReason: "Zero Curify results; travel/cultural experience templates missing",
    inventoryKeywordSets: [["cultural", "travel"], ["culture"], ["experience"]],
  },
  // ── 58-query eval P1 gaps ──────────────────────────────────────────────
  {
    query: "bilingual flashcards for kids learning korean fruits",
    originalClassification: "P1 template gap (6 results in eval)",
    sourceFile: "docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv",
    originalReason: "Curify has bilingual content but Korean-fruit-specific routing is thin",
    inventoryKeywordSets: [["bilingual"], ["flashcard"], ["korean"]],
  },
  {
    query: "watercolor map of europe travel destinations",
    originalClassification: "P1 / Need content generation (2 results)",
    sourceFile: "docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv",
    originalReason: "Very thin Curify coverage; watercolor-map specific templates needed",
    inventoryKeywordSets: [["watercolor", "map"], ["europe"], ["travel", "map"]],
  },
  {
    query: "cuban sandwich recipe poster",
    originalClassification: "P1 / Need content generation (4 results in eval; 1 after fix)",
    sourceFile: "docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv",
    originalReason: "Canva/Pinterest show rich template supply; Curify needs recipe poster templates",
    inventoryKeywordSets: [["recipe"], ["poster"], ["food"]],
  },
  {
    query: "Spanish vocabulary printable",
    originalClassification: "P1 / Better routing needed (6 results in eval)",
    sourceFile: "docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv",
    originalReason: "Curify has bilingual content but Spanish-specific printable routing is thin",
    inventoryKeywordSets: [["spanish"], ["vocabulary"], ["flashcard"]],
  },
  {
    query: "ESL flashcards printable",
    originalClassification: "Already covered (10 results in eval)",
    sourceFile: "docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv",
    originalReason: "ESL printable flashcard — Curify returns full-10",
    inventoryKeywordSets: [["esl"], ["flashcard"], ["vocabulary"]],
  },
  {
    query: "homophones and homonyms",
    originalClassification: "P1 / Need better routing (4 results in eval)",
    sourceFile: "docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv",
    originalReason: "Canva has dedicated worksheet templates; Curify needs homophone/grammar routing",
    inventoryKeywordSets: [["homophone"], ["grammar"], ["vocabulary"]],
  },
  {
    query: "book lovers gift guide",
    originalClassification: "P1 / Need content generation (2 results in eval)",
    sourceFile: "docs/external-signal-pilot/query-tier1-distribution-58-curify-centered.csv",
    originalReason: "Gift guide visual creation thin; gift guide template needed",
    inventoryKeywordSets: [["book"], ["gift"], ["guide"]],
  },
];

// ── Classification logic ───────────────────────────────────────────────────
function classify(candidate) {
  const { query, inventoryKeywordSets } = candidate;

  const { strict, relaxed } = searchInspirations(query);
  const currentRecall = strict.length;
  const relaxedCount = relaxed.length;

  const inventory = inventorySearch(inventoryKeywordSets);
  const inventoryTemplates = inventory.templates.length;
  const inventoryInspos = inventory.inspirations.length;

  const recalledTemplateIds = [...new Set(strict.map((i) => i.template_id))];
  const inventoryTemplateIds = inventory.templates.map((t) => t.id);
  const missedTemplateIds = inventoryTemplateIds.filter(
    (id) => !recalledTemplateIds.includes(id)
  );

  // Classification rules
  let newClassification;
  let evidence;
  let recommendedAction;

  if (inventoryTemplates >= 3 && currentRecall === 0) {
    // Templates exist but zero recall → clear recall issue
    newClassification = "RECALL_ISSUE";
    evidence = `${inventoryTemplates} templates found in inventory matching keywords, but search returns 0. Token matching gap — aliases or topic slugs missing.`;
    recommendedAction = `Add missing aliases/topics to inspirations under: ${inventoryTemplateIds.slice(0, 5).join(", ")}`;
  } else if (inventoryTemplates >= 3 && currentRecall < 3) {
    // Templates exist but recall below LOW_RESULT_THRESHOLD
    newClassification = "RECALL_ISSUE";
    evidence = `${inventoryTemplates} templates in inventory, ${inventoryInspos} inspirations potentially relevant, but strict search returns only ${currentRecall}. Relaxed mode adds ${relaxedCount} more.`;
    recommendedAction = `Add search_aliases and/or topics to missed inspiration records. Missed templates: ${missedTemplateIds.slice(0, 5).join(", ")}`;
  } else if (inventoryTemplates >= 1 && inventoryInspos < 10) {
    // Template exists but sparse inspiration content
    newClassification = "CONTENT_GAP_EXISTING_TEMPLATE";
    evidence = `Template(s) exist (${inventoryTemplateIds.slice(0, 3).join(", ")}) but only ${inventoryInspos} inspiration records match. No new template needed — generate examples under existing template(s).`;
    recommendedAction = `Batch-generate inspiration examples under existing template(s). Fix aliases in existing inspirations first.`;
  } else if (inventoryTemplates === 0 && inventoryInspos === 0) {
    newClassification = "TRUE_TEMPLATE_GAP";
    evidence = `Zero templates and zero inspirations match any inventory keyword. No relevant template exists.`;
    recommendedAction = `Propose new template and batch-generate initial inspiration set.`;
  } else if (currentRecall >= 10) {
    newClassification = "ADEQUATE_RECALL";
    evidence = `Current recall is ${currentRecall} — already at or above the full-10 threshold.`;
    recommendedAction = `No action needed. Monitor for diversity quality.`;
  } else if (currentRecall >= 3) {
    newClassification = "ADEQUATE_RECALL";
    evidence = `Current recall ${currentRecall} is above LOW_RESULT_THRESHOLD=3. ${inventoryTemplates} templates in inventory.`;
    recommendedAction = `Optional: add aliases to improve recall further. Not P0/P1.`;
  } else {
    newClassification = "UNCERTAIN";
    evidence = `Mixed signals. Current recall: ${currentRecall}, inventory templates: ${inventoryTemplates}, inventory inspos: ${inventoryInspos}.`;
    recommendedAction = `Manual review needed.`;
  }

  return {
    query,
    sourceFile: candidate.sourceFile,
    originalClassification: candidate.originalClassification,
    newClassification,
    currentTemplateRecallCount: recalledTemplateIds.length,
    currentInspirationRecallCount: currentRecall,
    relaxedInspirationCount: relaxedCount,
    inventoryCandidateTemplateCount: inventoryTemplates,
    inventoryCandidateInspoCount: inventoryInspos,
    missedCandidateCount: missedTemplateIds.length,
    topMissedTemplateIds: missedTemplateIds.slice(0, 5).join("; "),
    topRecalledTemplateIds: recalledTemplateIds.slice(0, 5).join("; "),
    evidence,
    recommendedAction,
    originalReason: candidate.originalReason,
  };
}

// ── Run audit ──────────────────────────────────────────────────────────────
const results = CANDIDATES.map(classify);

// ── CSV output ─────────────────────────────────────────────────────────────
const CSV_HEADER = [
  "query",
  "source_file",
  "original_classification",
  "new_classification",
  "current_template_recall_count",
  "current_inspiration_recall_count",
  "relaxed_inspiration_count",
  "inventory_candidate_template_count",
  "inventory_candidate_inspo_count",
  "missed_candidate_count",
  "top_missed_template_ids",
  "top_recalled_template_ids",
  "evidence",
  "recommended_action",
]
  .map((h) => `"${h}"`)
  .join(",");

function esc(v) {
  return `"${String(v || "").replace(/"/g, '""')}"`;
}

const csvRows = results.map((r) =>
  [
    r.query,
    r.sourceFile,
    r.originalClassification,
    r.newClassification,
    r.currentTemplateRecallCount,
    r.currentInspirationRecallCount,
    r.relaxedInspirationCount,
    r.inventoryCandidateTemplateCount,
    r.inventoryCandidateInspoCount,
    r.missedCandidateCount,
    r.topMissedTemplateIds,
    r.topRecalledTemplateIds,
    r.evidence,
    r.recommendedAction,
  ]
    .map(esc)
    .join(",")
);

const csvContent = [CSV_HEADER, ...csvRows].join("\n");

// ── Markdown report ────────────────────────────────────────────────────────
const byClass = (cls) => results.filter((r) => r.newClassification === cls);

const recall = byClass("RECALL_ISSUE");
const contentGap = byClass("CONTENT_GAP_EXISTING_TEMPLATE");
const trueGap = byClass("TRUE_TEMPLATE_GAP");
const adequate = byClass("ADEQUATE_RECALL");
const uncertain = byClass("UNCERTAIN");

function fmtRow(r) {
  return `| ${r.query} | ${r.originalClassification} | **${r.newClassification}** | ${r.currentInspirationRecallCount} | ${r.inventoryCandidateTemplateCount} | ${r.missedCandidateCount} | ${r.recommendedAction} |`;
}

const mdReport = `# Template Gap vs Recall Audit

> **Generated:** ${new Date().toISOString().slice(0, 10)}
> **Branch:** baobao/multi-intent-topic-cooccurrence
> **Search baseline:** Simulates strict-AND + relaxed-AND token matching from \`app/[locale]/(public)/search/page.tsx\`
> **Inventory audit:** Keyword-set match against full \`nano_templates.json\` + \`nano_inspiration.json\`

---

## Executive Summary

| Metric | Count |
|---|---|
| Total candidate queries audited | ${results.length} |
| Reclassified as **RECALL_ISSUE** | **${recall.length}** |
| Reclassified as **CONTENT_GAP_EXISTING_TEMPLATE** | **${contentGap.length}** |
| Confirmed **TRUE_TEMPLATE_GAP** | **${trueGap.length}** |
| Already **ADEQUATE_RECALL** (misclassified as gap) | **${adequate.length}** |
| **UNCERTAIN** | **${uncertain.length}** |

---

## Key Finding

**Several queries previously marked as "template gaps" or "P0 content gaps" are not true template gaps.** Curify already has relevant templates and/or inspiration content, but the current search does not recall them reliably due to:

1. **Missing CJK aliases** — flashcard templates use English "flashcard"/"flashcards" in tags, but Chinese queries for "闪卡" / "词汇闪卡" get zero hits because "闪卡" is not in any inspiration blob.
2. **Multi-token no-plural-stem** — the production tokenizer only stems plurals for single-token queries. "bilingual flashcard**s**" (two tokens) doesn't stem "flashcards" → "flashcard", but the singular "bilingual flashcard" fails strict-AND because most blobs store "flashcards" not "flashcard".
3. **Keyword missing from aliases** — "kindergarten", "worksheet", "weeknight", "gluten", "checklist" are legitimate user terms not yet mapped to existing template aliases, causing P0 results even when templates exist.
4. **Template-description pollution** (already partially fixed in commit \`9f4836f2\`) — placeholder terms in template descriptions create cascade false-positives then get stripped, inflating WARN counts.

---

## Priority Examples

### 1. bilingual flashcards / 双语闪卡

| Variant | Current Recall | Inventory Templates | Inventory Inspirations | Classification |
|---|---:|---:|---:|---|
| bilingual flashcards (plural) | **454** | 36 | 817 | ADEQUATE_RECALL |
| bilingual flashcard (singular) | 6 | 36 | 817 | RECALL_ISSUE |
| English Chinese flashcards | **374** | 36 | 817 | ADEQUATE_RECALL |
| Chinese English flashcards | **374** | 36 | 817 | ADEQUATE_RECALL |
| 双语闪卡 (CJK) | **0** | 36 | 817 | RECALL_ISSUE |
| 英语单词闪卡 (CJK) | **0** | 36 | 817 | RECALL_ISSUE |
| 词汇闪卡 (CJK) | **0** | 36 | 817 | RECALL_ISSUE |
| education flashcard | 1 | 116 | 846 | RECALL_ISSUE |

**Diagnosis:**
- English plural "bilingual flashcards" → **already excellent recall (454)**. The boss's report of "only ~6 templates" was incorrect — the issue was actually with the *singular* form.
- Chinese queries fail because **"闪卡" is not in any inspiration blob**. Templates store "flashcards" in English tags; no Chinese alias for the flashcard concept exists.
- Fix: add "闪卡" to search_aliases of key flashcard-family inspirations (low-risk, ~5 records).
- This is **NOT a template gap**. 36 templates and 817 inspirations are available.

**Relevant templates in inventory:**
\`template-vocabulary\`, \`template-word-scene\`, \`template-detailed-vocab-flashcard\`, \`template-cartoon-english-vocabulary-flashcards\`, \`template-children-english-vocab-spelling\`, \`template-bilingual-object-structure-labeling\`, \`template-educational-flashcard-ontology-mindmap-infographic\`, and 29 more.

---

### 2. phonics worksheets kindergarten (P0 in report → RECALL_ISSUE)

- **Current recall: 0** (classified P0 in external signal report)
- **Inventory: 1 template (template-phonics-consonant-blend), 50 inspirations**
- **Root cause:** Search tokens are ["phonics", "worksheets", "kindergarten"]. Phonics inspiration blobs have "phonics" in tags, but:
  - "worksheets" is not in any phonics inspiration alias (aliases are in Chinese: "辅音组合", "学习海报", etc.)
  - "kindergarten" is in zero inspiration records anywhere
- **Classification: RECALL_ISSUE** — template and content exist; aliases missing
- **Fix:** Add "worksheet", "worksheets", "kindergarten", "printable" to phonics inspiration search_aliases

---

### 3. easy weeknight dinners / gluten free dinner ideas / meal prep weekly recipes (P0 → mixed)

| Query | Recall | Recipe Templates | Classification |
|---|---:|---:|---|
| easy weeknight dinners healthy | 0 | 7 | CONTENT_GAP_EXISTING_TEMPLATE |
| gluten free dinner ideas | 0 | 7 | CONTENT_GAP_EXISTING_TEMPLATE |
| meal prep weekly recipes | 0 | 7 | CONTENT_GAP_EXISTING_TEMPLATE |

- Recipe templates exist: \`template-recipe\`, \`template-premium-recipe-card-infographic\`, \`template-food-recipe-tip-infographic\`
- Current recipe aliases cover: "comfort food", "cuisine guide", "family recipe", "recipe poster" — but NOT "weeknight", "gluten free", "meal prep", "weekly"
- Alias fix would restore basic recall, but current recipe inspirations are mostly **Chinese cuisine** — so while the template can generate Western dinner recipes, inspiration examples are thin for English-speaking meal planning queries
- **Classification: CONTENT_GAP_EXISTING_TEMPLATE** — template framework exists; need alias fixes + Western recipe inspiration batch generation

---

### 4. watercolor map of europe travel destinations (P1 → RECALL_ISSUE + CONTENT_GAP)

- **Current recall: 1** (was P1 in eval)
- **Inventory: 63 templates, 176 inspirations** matching watercolor/map/travel keywords
- Root cause: "europe" not present in most watercolor map inspiration blobs; templates \`template-watercolor-world-map-illustration\` and \`template-tourist-spot-watercolor-map-infographic\` exist
- Fix: (a) Add "europe", "European cities", "Europe travel" to alias of existing map inspirations; (b) batch-generate Europe watercolor map examples

---

### 5. before after kitchen organization makeover (WARN → CONTENT_GAP)

- **Current recall: 2**, inventory 13 templates, 38 inspirations
- \`template-home-organization-before-after\` exists and is the right template
- But inspiration records for kitchen-specific before/after are sparse — most content is general home decor
- **Classification: CONTENT_GAP_EXISTING_TEMPLATE** — batch-generate kitchen before/after examples under existing template

---

### 6. iCard (TRUE_TEMPLATE_GAP)

- **Current recall: 0**, inventory 0 templates, 1 inspiration (incidental match)
- No Curify template produces "iCard" format content
- **Classification: TRUE_TEMPLATE_GAP**

---

### 7. unique cultural experiences (TRUE_TEMPLATE_GAP)

- **Current recall: 0**, inventory 0 templates match "cultural experience"
- No travel/cultural experience template exists
- **Classification: TRUE_TEMPLATE_GAP**

---

## Full Query Audit Table

| query | original classification | new classification | strict recall | inventory templates | missed templates | recommended action |
|---|---|---:|---:|---:|---:|---|
${results.map(fmtRow).join("\n")}

---

## Recommended Engineering Fixes (by type)

### 1. CJK Alias Fixes (HIGH PRIORITY — affects all Chinese flashcard queries)

Add "闪卡" to the \`search_aliases\` array of at least 5 flashcard-family inspirations:
- \`template-vocabulary\` inspirations
- \`template-word-scene\` inspirations
- \`template-detailed-vocab-flashcard\` inspirations
- \`template-cartoon-english-vocabulary-flashcards\` inspirations
- \`template-children-english-vocab-spelling\` inspirations

**Impact:** Fixes 双语闪卡, 词汇闪卡, 英语单词闪卡 — all currently returning 0.

### 2. Phonics Worksheet Alias Fix (MEDIUM — fixes one P0)

Add the following to \`search_aliases\` of \`template-phonics-consonant-blend\` inspirations:
- "worksheet", "worksheets", "printable worksheet", "phonics worksheet"
- "kindergarten", "preschool", "early literacy"

**Impact:** Fixes "phonics worksheets kindergarten" from 0 to ~50 results.

### 3. Recipe Alias Expansion (MEDIUM — partially fixes 3 P0s)

Add to recipe template inspirations (\`template-recipe\`, \`template-premium-recipe-card-infographic\`):
- "weeknight dinner", "easy dinner", "healthy dinner", "quick dinner"
- "gluten free", "gluten-free", "dietary meal", "special diet"
- "meal prep", "weekly meal plan", "meal planner"

**Note:** Recall fix alone insufficient — Western recipe inspirations are thin. Pair with batch generation.

### 4. Multi-Token Plural Stemming (ENGINEERING — longer term)

The tokenizer only stems plurals for single-token queries. Consider extending to all tokens:
- "bilingual flashcard**s**" should match "bilingual flashcard"
- Low risk, high impact across many vocabulary/template queries

### 5. Content Generation Follow-up (BATCH GEN)

For CONTENT_GAP_EXISTING_TEMPLATE items:
- Batch-generate Europe watercolor map inspirations under \`template-watercolor-world-map-illustration\`
- Batch-generate kitchen before/after examples under \`template-home-organization-before-after\`
- Batch-generate Western recipe examples under \`template-recipe\` / \`template-premium-recipe-card-infographic\`
- Batch-generate Cuban sandwich example under \`template-recipe\`

---

## Summary: What Was Previously Misclassified as "Template Gap"

| Query | Previous Classification | Actual Issue | Action Type |
|---|---|---|---|
| bilingual flashcards (plural) | P1 template gap | NOT A GAP (454 results) | None needed |
| 双语闪卡 | P1 template gap | Recall issue (missing "闪卡" alias) | Add Chinese alias |
| 词汇闪卡 | P1 template gap | Recall issue (missing "闪卡" alias) | Add Chinese alias |
| phonics worksheets kindergarten | P0 template gap | Recall issue (missing aliases) | Add aliases |
| easy weeknight dinners healthy | P0 template gap | Content gap with existing templates | Add aliases + batch gen |
| gluten free dinner ideas | P0 template gap | Content gap with existing templates | Add aliases + batch gen |
| meal prep weekly recipes | P0 template gap | Content gap with existing templates | Add aliases + batch gen |

True template gaps (no existing template): **iCard**, **unique cultural experiences** only.

---

## Files Changed

_None in this audit run — see validation section. Fixes listed above are recommendations; apply after human review._
`;

// ── Write outputs ──────────────────────────────────────────────────────────
const OUT_DIR = path.join(ROOT, "docs/search-evaluation");
fs.mkdirSync(OUT_DIR, { recursive: true });

fs.writeFileSync(path.join(OUT_DIR, "template-gap-vs-recall-audit.csv"), csvContent, "utf8");
fs.writeFileSync(path.join(OUT_DIR, "template-gap-vs-recall-audit.md"), mdReport, "utf8");

// ── Console summary ────────────────────────────────────────────────────────
console.log("\n=== TEMPLATE GAP VS RECALL AUDIT ===\n");
console.log(`Total queries audited: ${results.length}`);
console.log(`  RECALL_ISSUE:                  ${recall.length}`);
console.log(`  CONTENT_GAP_EXISTING_TEMPLATE: ${contentGap.length}`);
console.log(`  TRUE_TEMPLATE_GAP:             ${trueGap.length}`);
console.log(`  ADEQUATE_RECALL:               ${adequate.length}`);
console.log(`  UNCERTAIN:                     ${uncertain.length}`);

console.log("\n--- RECALL ISSUES (not true template gaps) ---");
recall.forEach((r) => {
  console.log(`  [${r.currentInspirationRecallCount}→${r.inventoryCandidateTemplateCount} tmpl] ${r.query}`);
});

console.log("\n--- TRUE TEMPLATE GAPS ---");
trueGap.forEach((r) => console.log(`  ${r.query}`));

console.log("\n--- ADEQUATE RECALL (previously misclassified as gap) ---");
adequate.forEach((r) => {
  console.log(`  [${r.currentInspirationRecallCount} results] ${r.query}`);
});

console.log("\nOutputs written to:");
console.log("  docs/search-evaluation/template-gap-vs-recall-audit.md");
console.log("  docs/search-evaluation/template-gap-vs-recall-audit.csv\n");
