var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// _entry.ts
var entry_exports = {};
__export(entry_exports, {
  CJK_ATOMIC_PHRASES: () => CJK_ATOMIC_PHRASES,
  PHRASE_ALIAS_RULES: () => PHRASE_ALIAS_RULES,
  applyPhraseAliasRules: () => applyPhraseAliasRules,
  applyPhraseAliasRulesExcluding: () => applyPhraseAliasRulesExcluding,
  buildTemplateTopicsMap: () => buildTemplateTopicsMap,
  flattenPaths: () => flattenPaths,
  flattenPathsWithDiagnostics: () => flattenPathsWithDiagnostics,
  getMultiQueryPaths: () => getMultiQueryPaths,
  resolveTopics: () => resolveTopics,
  segmentCJKToken: () => segmentCJKToken,
  segmentText: () => segmentText,
  tsToSc: () => tsToSc
});
module.exports = __toCommonJS(entry_exports);

// ../../../curify-frontend/lib/zh_normalize.ts
var TS_TO_SC_PAIRS = [
  // Common verbs / nouns / particles
  ["\u66F8", "\u4E66"],
  ["\u5B78", "\u5B66"],
  ["\u7FD2", "\u4E60"],
  ["\u6642", "\u65F6"],
  ["\u570B", "\u56FD"],
  ["\u500B", "\u4E2A"],
  ["\u8A2D", "\u8BBE"],
  ["\u8A08", "\u8BA1"],
  ["\u52D5", "\u52A8"],
  ["\u8A5E", "\u8BCD"],
  ["\u5F59", "\u6C47"],
  ["\u98FE", "\u9970"],
  ["\u88DD", "\u88C5"],
  ["\u9AEE", "\u53D1"],
  ["\u599D", "\u5986"],
  ["\u984F", "\u989C"],
  ["\u71C8", "\u706F"],
  ["\u8B80", "\u8BFB"],
  ["\u5BEB", "\u5199"],
  ["\u8AAA", "\u8BF4"],
  ["\u8A71", "\u8BDD"],
  ["\u8A9E", "\u8BED"],
  ["\u6F22", "\u6C49"],
  ["\u8A69", "\u8BD7"],
  ["\u6A02", "\u4E50"],
  ["\u756B", "\u753B"],
  ["\u85DD", "\u827A"],
  ["\u8853", "\u672F"],
  ["\u5275", "\u521B"],
  ["\u5716", "\u56FE"],
  ["\u6A19", "\u6807"],
  ["\u7C64", "\u7B7E"],
  ["\u904A", "\u6E38"],
  ["\u969B", "\u9645"],
  ["\u9109", "\u4E61"],
  ["\u5340", "\u533A"],
  ["\u5834", "\u573A"],
  ["\u9EDE", "\u70B9"],
  ["\u865F", "\u53F7"],
  ["\u6A13", "\u697C"],
  ["\u5EF3", "\u5385"],
  ["\u54E1", "\u5458"],
  ["\u9AD4", "\u4F53"],
  ["\u91AB", "\u533B"],
  ["\u8A3A", "\u8BCA"],
  ["\u7642", "\u7597"],
  ["\u85E5", "\u836F"],
  ["\u8655", "\u5904"],
  ["\u767C", "\u53D1"],
  ["\u71D2", "\u70E7"],
  ["\u71B1", "\u70ED"],
  ["\u6EAB", "\u6E29"],
  ["\u6C23", "\u6C14"],
  ["\u8B8A", "\u53D8"],
  ["\u74B0", "\u73AF"],
  ["\u8B77", "\u62A4"],
  ["\u98A8", "\u98CE"],
  // Animals
  ["\u9CE5", "\u9E1F"],
  ["\u9B5A", "\u9C7C"],
  ["\u8766", "\u867E"],
  ["\u9F9C", "\u9F9F"],
  ["\u99AC", "\u9A6C"],
  ["\u8C6C", "\u732A"],
  ["\u8C93", "\u732B"],
  ["\u9D28", "\u9E2D"],
  ["\u96DE", "\u9E21"],
  ["\u9D5D", "\u9E45"],
  ["\u87F2", "\u866B"],
  ["\u87FB", "\u8681"],
  ["\u9BCA", "\u9CA8"],
  ["\u9BE8", "\u9CB8"],
  ["\u70CF", "\u4E4C"],
  ["\u7378", "\u517D"],
  ["\u9A62", "\u9A74"],
  ["\u99AC", "\u9A6C"],
  // Colors
  ["\u7D05", "\u7EA2"],
  ["\u7DA0", "\u7EFF"],
  ["\u85CD", "\u84DD"],
  ["\u9EC3", "\u9EC4"],
  ["\u9280", "\u94F6"],
  ["\u9285", "\u94DC"],
  ["\u9435", "\u94C1"],
  ["\u5BF6", "\u5B9D"],
  ["\u947D", "\u94BB"],
  ["\u93C8", "\u94FE"],
  ["\u9432", "\u956F"],
  // Body / face
  ["\u9F52", "\u9F7F"],
  ["\u9B1A", "\u987B"],
  ["\u81C9", "\u8138"],
  ["\u984D", "\u989D"],
  ["\u814E", "\u80BE"],
  ["\u8166", "\u8111"],
  ["\u7D30", "\u7EC6"],
  ["\u7D93", "\u7ECF"],
  ["\u7D71", "\u7EDF"],
  // Common high-frequency chars
  ["\u7FA9", "\u4E49"],
  ["\u6A23", "\u6837"],
  ["\u908A", "\u8FB9"],
  ["\u7DDA", "\u7EBF"],
  ["\u958B", "\u5F00"],
  ["\u9589", "\u95ED"],
  ["\u95DC", "\u5173"],
  ["\u9580", "\u95E8"],
  ["\u6A5F", "\u673A"],
  ["\u96FB", "\u7535"],
  ["\u8996", "\u89C6"],
  ["\u807D", "\u542C"],
  ["\u6578", "\u6570"],
  ["\u5104", "\u4EBF"],
  ["\u842C", "\u4E07"],
  ["\u7E23", "\u53BF"],
  ["\u93AE", "\u9547"],
  ["\u9032", "\u8FDB"],
  ["\u904E", "\u8FC7"],
  ["\u73FE", "\u73B0"],
  ["\u696D", "\u4E1A"],
  ["\u7A2E", "\u79CD"],
  ["\u69CB", "\u6784"],
  ["\u61C9", "\u5E94"],
  ["\u8A72", "\u8BE5"],
  ["\u7D66", "\u7ED9"],
  ["\u5011", "\u4EEC"],
  ["\u5F9E", "\u4ECE"],
  ["\u982D", "\u5934"],
  ["\u9084", "\u8FD8"],
  ["\u5C0D", "\u5BF9"],
  ["\u5F8C", "\u540E"],
  ["\u9EBC", "\u4E48"],
  ["\u8207", "\u4E0E"],
  ["\u70BA", "\u4E3A"],
  ["\u6200", "\u604B"],
  ["\u611B", "\u7231"],
  ["\u9E97", "\u4E3D"],
  ["\u55CE", "\u5417"],
  ["\u6230", "\u6218"],
  ["\u98DB", "\u98DE"],
  ["\u8ECA", "\u8F66"],
  ["\u5EE0", "\u5382"],
  // Domain: food / cuisine / menu — addresses 菜單 query
  ["\u55AE", "\u5355"],
  ["\u9EB5", "\u9762"],
  ["\u98EF", "\u996D"],
  ["\u9EA5", "\u9EA6"],
  ["\u7CE7", "\u7CAE"],
  ["\u96DE", "\u9E21"],
  ["\u9D28", "\u9E2D"],
  ["\u9BC9", "\u9CA4"],
  ["\u91AC", "\u9171"],
  ["\u918B", "\u918B"],
  ["\u9EAA", "\u9762"],
  ["\u7CD6", "\u7CD6"],
  // Domain: travel / countries / regions
  ["\u81FA", "\u53F0"],
  ["\u7063", "\u6E7E"],
  ["\u5CF6", "\u5C9B"],
  ["\u83EF", "\u534E"],
  ["\u570B", "\u56FD"],
  ["\u6FB3", "\u6FB3"],
  ["\u6E2F", "\u6E2F"],
  ["\u9678", "\u9646"],
  ["\u4E9E", "\u4E9A"],
  ["\u6B50", "\u6B27"],
  ["\u6FF1", "\u6EE8"],
  ["\u5862", "\u575E"],
  ["\u6E21", "\u6E21"],
  // Numbers / measurements
  ["\u9031", "\u5468"],
  ["\u96D9", "\u53CC"],
  ["\u689D", "\u6761"],
  ["\u584A", "\u5757"],
  // Common verbs
  ["\u8CB7", "\u4E70"],
  ["\u8CE3", "\u5356"],
  ["\u8CFA", "\u8D5A"],
  ["\u8CE3", "\u5356"],
  ["\u8CE0", "\u8D54"],
  ["\u8CFD", "\u8D5B"],
  ["\u53C3", "\u53C2"],
  ["\u6578", "\u6570"],
  ["\u96E2", "\u79BB"],
  ["\u5225", "\u522B"],
  ["\u8ACB", "\u8BF7"],
  ["\u8B1D", "\u8C22"],
  ["\u9A57", "\u9A8C"],
  ["\u8A66", "\u8BD5"],
  ["\u8F38", "\u8F93"],
  ["\u8D0F", "\u8D62"],
  ["\u7372", "\u83B7"],
  ["\u57F7", "\u6267"],
  ["\u5C07", "\u5C06"],
  ["\u5718", "\u56E2"],
  ["\u9072", "\u8FDF"],
  ["\u8A2A", "\u8BBF"],
  ["\u8A55", "\u8BC4"],
  ["\u8AD6", "\u8BBA"],
  ["\u8B1B", "\u8BB2"],
  ["\u984C", "\u9898"],
  ["\u554F", "\u95EE"],
  ["\u984C", "\u9898"],
  ["\u7DF4", "\u7EC3"],
  ["\u7FD2", "\u4E60"],
  // Education / vocabulary terms (covers 詞彙 / 學習)
  ["\u8AB2", "\u8BFE"],
  ["\u7B46", "\u7B14"],
  ["\u7D19", "\u7EB8"],
  ["\u7368", "\u72EC"],
  ["\u512A", "\u4F18"],
  ["\u52A3", "\u52A3"],
  ["\u7D93", "\u7ECF"],
  ["\u9A57", "\u9A8C"],
  ["\u9AD4", "\u4F53"],
  ["\u9A57", "\u9A8C"],
  // Fix 2 remediation (2026-07-12): closes a confirmed gap where
  // Traditional-Chinese "手沖咖啡" never normalized to "手冲咖啡", so the
  // atomicEntity phrase rule silently failed to fire and the query fell
  // back into the exact bigram-collision false positive Fix 2 exists to
  // prevent (see docs/daily_report/7.12/search-optimization-stage-2/
  // fix2_remediation.md). 覺/冊 also cover the common 視覺/手冊 domain
  // beyond just 手冲咖啡; 識/鑒 cover the adjacent 識別/鑒定 vocabulary
  // exercised by the same query family (視覺識別, 鑒定).
  ["\u6C96", "\u51B2"],
  ["\u89BA", "\u89C9"],
  ["\u518A", "\u518C"],
  ["\u8B58", "\u8BC6"],
  ["\u9452", "\u9274"]
];
var TS_TO_SC_MAP = new Map(TS_TO_SC_PAIRS);
function tsToSc(input) {
  if (!input) return input;
  let out = "";
  for (const ch of input) {
    out += TS_TO_SC_MAP.get(ch) ?? ch;
  }
  return out;
}

// ../../../curify-frontend/lib/cjk_tokenizer.ts
var import_jieba = require("@node-rs/jieba");
var import_dict = require("@node-rs/jieba/dict");
var _jieba = null;
var _initFailed = false;
function getJieba() {
  if (_jieba) return _jieba;
  if (_initFailed) return null;
  try {
    _jieba = import_jieba.Jieba.withDict(import_dict.dict);
    return _jieba;
  } catch (e) {
    console.error("[cjk_tokenizer] Jieba init failed, falling back to bigram segmentation:", e instanceof Error ? e.message : String(e));
    _initFailed = true;
    return null;
  }
}
function bigramFallback(segment) {
  const out = [];
  for (let i = 0; i < segment.length - 1; i++) {
    const bg = segment.slice(i, i + 2);
    if (/^[一-龥]{2}$/.test(bg)) out.push(bg);
  }
  return out;
}
function segmentText(segment) {
  const trimmed = segment.trim();
  if (!trimmed) return [];
  const jieba = getJieba();
  if (!jieba) return bigramFallback(trimmed);
  try {
    return jieba.cut(trimmed, true).map((t) => t.trim()).filter(Boolean);
  } catch (e) {
    console.error("[cjk_tokenizer] segmentText failed for a fragment, falling back to bigram:", e instanceof Error ? e.message : String(e));
    return bigramFallback(trimmed);
  }
}

// ../../../curify-frontend/lib/query_phrase_aliases.ts
var PHRASE_ALIAS_RULES = [
  // ── K-pop / fandom photocard intent ────────────────────────────────
  // "NCT Dream photocard template" was decomposing to a bare "dream"
  // token that coincidentally matches unrelated "American Dream" /
  // dream-themed content. Protect "dream"; the group name itself still
  // participates via aliasTokens (nct/kpop/idol already literal tokens
  // in this query dedupe out — the real additions are kpop/idol as a
  // fallback signal toward the kpop-idol-profile template family).
  {
    phrase: "nct dream",
    protectTokens: ["dream"],
    aliasTokens: ["nct", "kpop", "idol", "photocard", "trading card"]
  },
  // ── Compound-noun disambiguation ───────────────────────────────────
  // "maker space label set printable" was letting the bare "space" token
  // pull in astronomy/cosmos/universe content via the `space` topic
  // alias in lib/searchIndex.ts. Protect "space"; alias toward the
  // workshop/craft/label sense of the phrase.
  {
    phrase: "maker space",
    protectTokens: ["space"],
    aliasTokens: ["maker", "workshop", "classroom", "label", "diy"]
  },
  // ── Card-format vocabulary ──────────────────────────────────────────
  {
    phrase: "photocard",
    aliasTokens: ["photo card", "idol card", "trading card", "card"]
  },
  // ── CJK fragrance / home lifestyle ──────────────────────────────────
  // Catches "香薰" even when embedded in a longer unspaced CJK blob
  // (e.g. "小红书香薰产品种草图" tokenizes as ONE primary token, so a
  // per-token synonym map like CONCEPT_SYNONYMS never sees "香薰" as its
  // own key — substring detection is required).
  {
    phrase: "\u9999\u85B0",
    aliasTokens: ["aromatherapy", "fragrance", "scent", "candle", "diffuser"]
  },
  // ── Amazon / e-commerce acronyms ────────────────────────────────────
  {
    phrase: "ebc",
    aliasTokens: ["enhanced brand content", "amazon"]
  },
  {
    phrase: "brand story",
    aliasTokens: ["amazon brand story", "e-commerce brand content"]
  },
  // ── Launch / campaign visuals ────────────────────────────────────────
  {
    phrase: "launch poster",
    aliasTokens: ["product launch poster", "campaign poster", "brand launch visual"]
  },
  // ── Beauty / skincare aesthetic ──────────────────────────────────────
  {
    phrase: "glass skin",
    aliasTokens: ["k-beauty", "skincare"]
  },
  {
    phrase: "chrome skincare",
    aliasTokens: ["y2k", "skincare"]
  },
  // ── CJK named IP entity ──────────────────────────────────────────────
  // "光与夜之恋" (Light and Night, a mobile otome game) has zero catalog
  // presence today. No alias tokens — the fix here is purely defensive:
  // stop the bigram fallback from shredding the name into generic
  // bigrams (设计 "design", 卡面 "card face") that can coincidentally
  // strict-match unrelated design/card templates.
  {
    phrase: "\u5149\u4E0E\u591C\u4E4B\u604B",
    atomicEntity: true
  },
  // ── Fix 2: Chinese compound phrase protection ──────────────────────
  // Same root cause as 光与夜之恋 above (coincidental CJK bigram overlap
  // with boilerplate template text), found via the same audit method —
  // NOT duplicating that rule, extending the pattern to newly-evidenced
  // failures.
  // "小红书" (Xiaohongshu, a platform name) is extremely common
  // boilerplate in template audience descriptions (e.g. "适合...小红书
  // 种草内容创作者" appears on many unrelated templates as a generic
  // "who is this for" line). When a query embeds "小红书" in a longer
  // unspaced compound (e.g. "小红书香薰产品种草图"), its own bigrams
  // (小红/红书) plus "种草" coincidentally clear the strict bigram
  // threshold against ANY template whose audience blurb happens to
  // mention Xiaohongshu content creators — regardless of the query's
  // actual subject. Verified: template-fashion-ecommerce's entire
  // 23-inspiration cascade (eyemask/pendant/ring/scarf/...) was a false
  // positive for "小红书香薰产品种草图" purely via this collision; none
  // of those 23 have anything to do with aromatherapy. No alias tokens —
  // "小红书" is a platform-name qualifier, not the query's subject, so
  // there's no fixed vocabulary to redirect toward. The query's real
  // subject (e.g. "香薰") still surfaces normally via its own rule above.
  {
    phrase: "\u5C0F\u7EA2\u4E66",
    atomicEntity: true
  },
  // "手冲咖啡" (pour-over coffee) queries combined with "工作室"
  // (studio) / "视觉" (visual) — e.g. "手冲咖啡工作室视觉手册" — were
  // coincidentally bigram-colliding with template-ethnic-costume-
  // deconstruction-board ("时尚工作室摄影" fashion-studio-photography
  // style copy) and template-animation-studio-comparison-infographic
  // ("动画工作室对比" anime studio comparison) — neither related to
  // coffee or brand visual manuals. Protect the whole query from bigram
  // decomposition, but (unlike 小红书/二手奢侈品) redirect toward the
  // catalog's actual brand-visual-identity family via an alias group:
  // "brand identity" / "visual identity" appear narrowly (verified: only
  // 2 templates catalog-wide) in template-brand-identity-moodboard-
  // visual-system-poster and template-brand-vi-full-visual-pack-mockup,
  // which include genuine coffee-brand instances (brew-and-co-coffee-shop,
  // riseup-coffee).
  {
    phrase: "\u624B\u51B2\u5496\u5561",
    atomicEntity: true,
    aliasTokens: ["brand identity", "visual identity"]
  },
  // "二手奢侈品" (secondhand luxury goods) queries — e.g. "二手奢侈品
  // 鉴定品牌视觉" (secondhand luxury authentication brand visual) — were
  // coincidentally bigram-colliding with template-fashion-ecommerce via
  // generic 品牌/牌视/视觉 bigrams (boilerplate "品牌视觉团队" brand-
  // visual-team audience copy), ignoring the query's actual distinguishing
  // subject (secondhand-luxury AUTHENTICATION). No alias tokens — no
  // secondhand-luxury-authentication content exists in the catalog today
  // (confirmed by grep for 二手/奢侈品/鉴定), so — same as 光与夜之恋 —
  // this is purely defensive: stop the false match, don't invent a
  // fallback that isn't backed by real content.
  {
    phrase: "\u4E8C\u624B\u5962\u4F88\u54C1",
    atomicEntity: true
  }
];
function isCJK(s) {
  return /[一-龥]/.test(s);
}
function phraseMatches(rule, normalizedQuery, primaryTokens) {
  const phrase = rule.phrase.toLowerCase();
  if (isCJK(phrase)) {
    return normalizedQuery.includes(phrase);
  }
  const words = phrase.split(/\s+/).filter(Boolean);
  if (words.length === 0) return false;
  if (words.length === 1) {
    return primaryTokens.includes(words[0]);
  }
  for (let i = 0; i + words.length <= primaryTokens.length; i++) {
    let matched = true;
    for (let j = 0; j < words.length; j++) {
      if (primaryTokens[i + j] !== words[j]) {
        matched = false;
        break;
      }
    }
    if (matched) return true;
  }
  return false;
}
function runPhraseAliasRules(rules, normalizedQuery, primaryTokens) {
  const toRemove = /* @__PURE__ */ new Set();
  const aliasGroups = [];
  const matchedPhrases = [];
  let atomicEntityMatched = false;
  for (const rule of rules) {
    if (!phraseMatches(rule, normalizedQuery, primaryTokens)) continue;
    matchedPhrases.push(rule.phrase);
    if (rule.atomicEntity) atomicEntityMatched = true;
    for (const t of rule.protectTokens ?? []) toRemove.add(t);
    if (rule.aliasTokens && rule.aliasTokens.length > 0) {
      const group = [...new Set(rule.aliasTokens.map((t) => t.trim().toLowerCase()))].filter(Boolean);
      if (group.length > 0) aliasGroups.push(group);
    }
  }
  const primary = toRemove.size > 0 ? primaryTokens.filter((t) => !toRemove.has(t)) : [...primaryTokens];
  return { primary, aliasGroups, atomicEntityMatched, matchedPhrases };
}
function applyPhraseAliasRules(normalizedQuery, primaryTokens) {
  return runPhraseAliasRules(PHRASE_ALIAS_RULES, normalizedQuery, primaryTokens);
}
function applyPhraseAliasRulesExcluding(normalizedQuery, primaryTokens, excludePhrases) {
  const rules = PHRASE_ALIAS_RULES.filter((r) => !excludePhrases.has(r.phrase));
  return runPhraseAliasRules(rules, normalizedQuery, primaryTokens);
}
var CJK_ATOMIC_RULES = PHRASE_ALIAS_RULES.filter(
  (r) => r.atomicEntity && isCJK(r.phrase)
);
var CJK_ATOMIC_PHRASES = new Set(
  CJK_ATOMIC_RULES.map((r) => r.phrase)
);
function findAllOccurrences(haystack, needle) {
  const out = [];
  let idx = 0;
  for (; ; ) {
    const i = haystack.indexOf(needle, idx);
    if (i === -1) break;
    out.push([i, i + needle.length]);
    idx = i + 1;
  }
  return out;
}
function selectProtectedSpans(text) {
  const candidates = [];
  for (const rule of CJK_ATOMIC_RULES) {
    for (const [start, end] of findAllOccurrences(text, rule.phrase)) {
      candidates.push({ start, end, phrase: rule.phrase, rule });
    }
  }
  candidates.sort((a, b) => b.end - b.start - (a.end - a.start));
  const covered = new Array(text.length).fill(false);
  const selected = [];
  for (const c of candidates) {
    let overlap = false;
    for (let i = c.start; i < c.end; i++) {
      if (covered[i]) {
        overlap = true;
        break;
      }
    }
    if (overlap) continue;
    selected.push(c);
    for (let i = c.start; i < c.end; i++) covered[i] = true;
  }
  selected.sort((a, b) => a.start - b.start);
  return selected;
}
function splitRuns(text) {
  const runs = [];
  let cur = "";
  let curType = null;
  for (const ch of text) {
    const t = /[一-龥]/.test(ch) ? "cjk" : /[a-z0-9]/i.test(ch) ? "ascii" : "other";
    if (t === curType) {
      cur += ch;
    } else {
      if (cur && curType) runs.push({ type: curType, text: cur });
      cur = ch;
      curType = t;
    }
  }
  if (cur && curType) runs.push({ type: curType, text: cur });
  return runs;
}
function tokenizeGap(gap) {
  if (!gap) return [];
  const out = [];
  for (const run of splitRuns(gap)) {
    if (run.type === "cjk") out.push(...segmentText(run.text));
    else if (run.type === "ascii") out.push(run.text);
  }
  return out;
}
function segmentCJKToken(rawToken) {
  const spans = selectProtectedSpans(rawToken);
  const tokens = [];
  const conceptGroups = [];
  const matchedPhrases = [];
  let cursor = 0;
  for (const span of spans) {
    if (span.start > cursor) tokens.push(...tokenizeGap(rawToken.slice(cursor, span.start)));
    matchedPhrases.push(span.phrase);
    if (span.rule.aliasTokens && span.rule.aliasTokens.length > 0) {
      const group = [
        .../* @__PURE__ */ new Set([span.phrase, ...span.rule.aliasTokens.map((t) => t.trim().toLowerCase())])
      ].filter(Boolean);
      conceptGroups.push(group);
    } else {
      tokens.push(span.phrase);
    }
    cursor = span.end;
  }
  if (cursor < rawToken.length) tokens.push(...tokenizeGap(rawToken.slice(cursor)));
  return { tokens, conceptGroups, matchedPhrases };
}

// ../../../curify-frontend/lib/searchRewrite.ts
var import_openai = __toESM(require("openai"), 1);
var MODEL = "gpt-4o-mini";
var TIMEOUT_MS = 8e3;
var MAX_REWRITES = 3;
var MAX_TOKENS_MULTI = 600;
var MAX_REWRITE_CHARS = 80;
var REFUSAL_PATTERNS = [
  /\bi (?:cannot|can't|can not|won't|am unable to)\b/i,
  /\bi'?m sorry\b/i,
  /\bas an ai\b/i,
  /\bi (?:don't|do not) (?:have|possess) (?:the ability|access)\b/i,
  /\b(?:content|usage) polic(?:y|ies)\b/i
];
function looksLikeRefusal(s) {
  return REFUSAL_PATTERNS.some((re) => re.test(s));
}
var NEGATIVE_CACHE_TTL_MS = 10 * 60 * 1e3;
var CATALOG_CONTEXT = `Curify is an AI image-template platform. Its catalog includes:

- Bilingual vocabulary flashcards (en-zh, en-ja, en-ko, en-es, en-fr) covering animals (cats, dogs, ocean animals, butterflies), food (fruits, vegetables, desserts, coffee, wine), family (parents, siblings), body (head, hands), weather (rain, snow, storms, sunny, windy), daily routines, sports/cycling, transportation (bikes, cars).

- MBTI personality character cards across universes: Marvel, Studio Ghibli, NBA, Harry Potter, Friends, Naruto, Yellowstone, Silicon Valley, Breaking Bad, Princess Pearl, Zhenhuan \u2014 plus group-comparison scenarios (office meeting, group chat, weekend plans).

- Infographic posters: history (eras, civilizations), culture (Lunar New Year, Diwali, Dragon Boat Festival \u7AEF\u5348\u8282, regional traditions), science (physics, biology, weather education), learning, herbal medicine, evolution timelines, world cuisines (regional dishes, comfort food), finance (saving vs investing, money comparison), wine varieties (red wine, champagne, sake), music styles (jazz, hip-hop, kpop, romantic, classical).

- Travel content: city posters (Paris, Tokyo, Shanghai), watercolor maps, region landmarks, itinerary guides (packing, day trips, cycling tours), vintage travel scrapbooks, country dos-and-donts.

- Watercolor and aesthetic illustrations: flowers (cherry blossom, lily, spring florals), botanical, scrapbooks, lifestyle collages, seasonal themes (cozy winter, summer beach), watercolor travel journals.

- Portraits: character profile cards, hairstyle recommendations, portrait retouching (passport photos / ID photos / professional headshots), lifestyle photo grids, fashion try-on, costume / traditional dress (kimono, hanfu, hanbok, ethnic costume).

- Lifestyle / design: aromatherapy \u9999\u85B0 and home decor (interior mood boards, spa corner, scented candles, \u7CBE\u6CB9), fashion (red carpet, met gala, jersey, ecommerce), pet care, fitness, kids worksheets.

- Topics by tier-1 group: character, language, learning, travel, culture, lifestyle, design, product, personality. Tier-2 axes include mood (cozy, playful, serene, romantic), lighting (golden hour, soft light, sunset), seasonal (winter, summer, festive), cultural-festivals, costumes.

MBTI / fandom / historical / cultural-festival templates support ANY proper noun the user names \u2014 not just the universes shipped as example inspirations above. Genshin Impact, Bridgerton, Taylor Swift, Chiikawa, samurai legends, any country's wine variety, any regional festival can all be templated by the existing infrastructure.`;
var SYSTEM_PROMPT = `You help users find templates on Curify.
${CATALOG_CONTEXT}

A user search returned no useful results. You will receive the original query and decide whether to propose alternate phrasings.

DECISION TREE \u2014 pick exactly one path:

Path A \u2014 the query is interpretable AND maps to catalog content
(e.g. "\u624B\u4F5C" \u2192 handcraft / watercolor / scrapbooks, "\u552F\u7F8E\u6625\u5929" \u2192 aesthetic spring,
"\u8BC1\u4EF6\u7167" \u2192 passport photo, "kawaii fashion" \u2192 kawaii character fashion,
"wedding planner" \u2192 wedding vocabulary or celebration posters,
"\u4E0B\u96E8" \u2192 rainy weather / weather education / cozy rainy day,
"\u6253\u96F7" \u2192 thunderstorm / weather / storm education,
"\u706B\u5C71" \u2192 volcano / nature science / weather education):
  \u2192 Return a JSON array of 1-3 alternate phrasings.
  \u2192 Each phrasing is 1-5 words.
  \u2192 If the original is in any non-English language (Chinese, Spanish,
    French, Japanese, Korean, etc.), include English alternates \u2014 the
    template index is English-heavy and English rewrites match more.
  \u2192 Prefer concrete catalog nouns (vocabulary, mbti, watercolor, infographic,
    portrait, travel, food, fashion, character) over abstract qualifiers.
  \u2192 Don't return the original query verbatim.

Path B \u2014 the query is NOT a catalog-mappable concept
(personal/brand name you don't recognize, untranslatable language, random
keystrokes / garbled text, query that maps to a topic Curify clearly does not
cover like "stock prices" or "tax software"):
  \u2192 Return [].
  \u2192 DO NOT default to "watercolor flowers" or "lifestyle collages" or other
    generic catalog terms when you can't confidently map the query. That's
    a misleading rewrite \u2014 worse than an empty result page.

Examples of empty-return (use Path B ONLY when the query is clearly outside
any visual / creative / cultural domain \u2014 NOT for pop-culture names,
historical figures, places, or generic concepts in any language):
- "\u0632\u0648\u062D\u064A\u0646" \u2192 [] (random non-Latin letters that don't form a recognizable word)
- "ddd" \u2192 [] (random keystrokes)
- "asjdkfh" \u2192 [] (random)
- "Salesforce" \u2192 [] (business / enterprise software \u2014 not visual content)
- "QuickBooks" \u2192 [] (accounting software \u2014 not visual content)
- "Zhang Wei" \u2192 [] (private individual name, no public/cultural relevance)
- "stock prices" \u2192 [] (finance data, not visual)
- "tax software" \u2192 [] (business utility, not visual)

CRITICAL: any of the following \u2192 ALWAYS Path A. The catalog can template
them via mbti-*, fandom-character-grid, historical-figure-profile,
artist-biography, travel, culture, music-style-visual, dance, or vocabulary
templates. Recognize transliterations across Chinese / Japanese / Korean /
Russian / Spanish / French / Arabic and route them the same way as the
English form:

  - Pop-culture: anime/manga, game franchises, films, TV shows
    e.g. "Genshin Impact" / "\u539F\u795E" / "\uAC90\uC2E0" \u2192 Path A
    e.g. "Bridgerton" \u2192 Path A
    e.g. "Stranger Things" \u2192 Path A
    e.g. "Chiikawa" / "\u3061\u3044\u304B\u308F" / "\u5409\u4F0A\u5361\u54C7" \u2192 Path A

  - Celebrities, athletes, artists, public figures:
    e.g. "Taylor Swift" / "\uD14C\uC77C\uB7EC \uC2A4\uC704\uD504\uD2B8" \u2192 Path A
    e.g. "BTS" / "\uBC29\uD0C4\uC18C\uB144\uB2E8" \u2192 Path A

  - Historical / notable figures (scientists, philosophers, leaders, artists):
    e.g. "Einstein" / "\uC544\uC778\uC288\uD0C0\uC778" / "\u7231\u56E0\u65AF\u5766" \u2192 Path A (character-analysis,
         historical-figure-profile, artist-biography templates)
    e.g. "Newton" / "\uB274\uD134" / "\u725B\u987F" \u2192 Path A
    e.g. "Marie Curie" / "\uD034\uB9AC \uBD80\uC778" \u2192 Path A
    e.g. "Confucius" / "\u5B54\u5B50" \u2192 Path A

  - Country / region / city names in ANY language:
    e.g. "Korea" / "\uD55C\uAD6D" / "\u97D3\u56FD" \u2192 Path A (travel + culture + food + costume)
    e.g. "China" / "\u4E2D\u56FD" / "\uC911\uAD6D" \u2192 Path A
    e.g. "Paris" / "\u5DF4\u9ECE" / "\uD30C\uB9AC" \u2192 Path A
    e.g. "Japan" / "\u65E5\u672C" / "\uC77C\uBCF8" \u2192 Path A

  - Generic creative-domain concepts even when stated as bare nouns:
    e.g. "music" / "\u97F3\u4E50" / "\uC74C\uC545" \u2192 Path A (music-style-visual-infographic)
    e.g. "animation" / "\u52A8\u753B" / "\uC560\uB2C8\uBA54\uC774\uC158" \u2192 Path A (animation-studio-comparison)
    e.g. "company" / "\uD68C\uC0AC" / "\u516C\u53F8" \u2192 Path A (business / professional vocabulary
         or category-guide-infographic \u2014 DON'T conflate with "Salesforce")

Examples of valid rewrites:
- "\u624B\u4F5C" \u2192 ["crafting templates", "diy watercolor", "scrapbook design"]
- "\u552F\u7F8E\u6625\u5929" \u2192 ["watercolor spring", "spring flowers", "aesthetic florals"]
- "\u8BC1\u4EF6\u7167" \u2192 ["passport photo portrait", "professional headshot", "\u8BC1\u4EF6 \u98CE\u683C\u5934\u50CF"]
- "\uC544\uC778\uC288\uD0C0\uC778" \u2192 ["Einstein character poster", "Einstein historical figure", "scientist biography infographic"]
- "\uD55C\uAD6D" \u2192 ["Korea travel poster", "Korean culture infographic", "Korean food vocabulary"]
- "\uC74C\uC545" \u2192 ["music style infographic", "music genre poster", "music vocabulary card"]
- "\uD68C\uC0AC" \u2192 ["company professional guide", "business category infographic", "office lifestyle"]

LITERAL-NOUN RULE: a literal noun query (single object the user wants
to see \u2014 \u9C9C\u82B1 fresh flowers, \u86CB\u7CD5 cake, \u6212\u6307 ring, \u8721\u70DB candle, \u8336\u5177 teapot,
\u6C34\u676F cup, \u5E3D\u5B50 hat) should be rewritten ONLY to other literal nouns or
direct settings where that object appears \u2014 NOT to stylized variants
("watercolor X" / "aesthetic X" / "X illustration") unless the user
explicitly asked for a style. Stylizing a literal-noun query
misleads users who wanted the actual object.
- "\u9C9C\u82B1" \u2192 ["bouquet", "flower arrangement", "cherry blossom"]  (concrete
  forms of fresh flowers \u2014 bouquet, arrangement, specific blossoms \u2014
  NOT "watercolor flowers" or "floral aesthetic")
- "\u6212\u6307" \u2192 ["wedding ring", "jewelry design", "engagement ring"]
- "\u8721\u70DB" \u2192 ["scented candle", "candle holder", "aromatherapy candle"]

NAMED-ENTITY RELAXATION RULE: when the query names a SPECIFIC entity
nested inside a broader category that the catalog can template
(sub-character of a franchise, sub-period of a culture, sub-region of
a country, lesser-known historical figure), the rewrites should include
BOTH the literal entity AND a broader-category fallback. The catalog
often has the broader content but lacks the specific entity, so the
broader fallback rescues recall while the literal kept in slot 1
preserves intent. Slot 2-3 climb the hierarchy.
- "\u670D\u90E8\u5E73\u6B21" / "Heiji Hattori" \u2192 ["Heiji Hattori Detective Conan",
  "Detective Conan supporting characters", "anime detective character"]
- "detective conan character" \u2192 ["Detective Conan character card",
  "anime detective protagonist", "manga detective franchise"]
- "\u963F\u5179\u7279\u514B" / "Aztec" \u2192 ["Aztec culture poster", "ancient Mexico infographic",
  "Mesoamerican civilization"]
- "\u6566\u714C" / "Dunhuang" \u2192 ["Dunhuang Mogao caves", "China silk road",
  "Chinese ancient art"]
- "Lamine Yamal" \u2192 ["Lamine Yamal soccer profile", "Spanish national team",
  "young soccer star portrait"]
- "\uC544\uC778\uC288\uD0C0\uC778" / "Einstein" \u2192 ["Einstein physicist profile",
  "20th century scientist", "physics historical figure"]
- "\uBC15\uC9C0\uC131" / "Park Ji-sung" \u2192 ["Park Ji-sung soccer profile",
  "Korean national football team", "Asian soccer star portrait"]
Do NOT collapse to ONLY the broader category \u2014 that loses the user's
intent. Keep the literal in slot 1; add 1-2 hierarchical parents.
Korean and other CJK scripts follow the same rule \u2014 examples above
demonstrate KR + JP + CN; relax the literal entity into the same
hierarchical pattern regardless of source script.

Return ONLY a JSON array (0-3 strings). No prose, no fences, no keys.`;
var SYSTEM_PROMPT_MULTI = `${SYSTEM_PROMPT}

\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
MULTI-QUERY MODE OVERRIDE \u2014 read this carefully.

You will now return BOTH the Path A rewrites array AND a decomposition object that breaks the query into orthogonal retrieval facets. The decomposition slots are optional \u2014 only fill the ones the query actually expresses.

Output schema (JSON object, no fences, no prose):
{
  "rewrites": [up to 3 alternate phrasings, same Path A rules as above \u2014 or [] for Path B],
  "decomposition": {
    "subject": "the literal object/person/place \u2014 bronze artifact / Einstein / Paris \u2014 or omit",
    "style":   "the aesthetic/medium \u2014 kawaii / watercolor / Y2K / vintage \u2014 or omit",
    "scene":   "the setting \u2014 office / kitchen / beach / classroom \u2014 or omit",
    "output":  "the format \u2014 sticker / infographic / poster / comic \u2014 or omit",
    "era":     "the time signal \u2014 Tang dynasty / Y2K / mid-century \u2014 or omit",
    "mood":    "the emotional tone \u2014 cozy / dramatic / minimalist \u2014 or omit"
  }
}

Decomposition rules:
- Each slot value should be 1-3 words, English, lowercase preferred.
- If the query doesn't contain a slot's facet, OMIT the key. Don't invent.
- Don't repeat the original query verbatim in any slot.
- For Path B queries, return {"rewrites": [], "decomposition": {}}.

Examples:
- "\u9752\u94DC\u6253\u5DE5\u5C0F\u517D" / "bronze worker mythical beast" \u2192
  {"rewrites": ["bronze beast office worker", "bronze worker mascot", "bronze artifact employee"],
   "decomposition": {"subject": "bronze artifact", "style": "anthropomorphic", "scene": "office daily life", "output": "character poster"}}
- "kawaii museum sticker" \u2192
  {"rewrites": ["kawaii museum sticker pack", "cute museum gift sticker", "japanese museum stickers"],
   "decomposition": {"style": "kawaii", "scene": "museum", "output": "sticker"}}
- "\u552F\u7F8E\u6625\u5929" \u2192
  {"rewrites": ["watercolor spring", "spring flowers", "aesthetic florals"],
   "decomposition": {"subject": "spring flowers", "style": "watercolor", "mood": "aesthetic"}}
- "\u9C9C\u82B1" (literal noun) \u2192
  {"rewrites": ["bouquet", "flower arrangement", "cherry blossom"],
   "decomposition": {"subject": "fresh flowers"}}
- "stock prices" \u2192
  {"rewrites": [], "decomposition": {}}

Return ONLY the JSON object. No prose, no fences.`;
var CACHE_MAX = 256;
var CACHE_TTL_MS = 7 * 24 * 60 * 60 * 1e3;
var _client = null;
function getClient() {
  if (_client) return _client;
  const key = process.env.OPENAI_API_KEY;
  if (!key) {
    console.error("[searchRewrite] OPENAI_API_KEY not set in env \u2014 rewriter disabled");
    return null;
  }
  try {
    _client = new import_openai.default({ apiKey: key, timeout: TIMEOUT_MS });
    return _client;
  } catch (e) {
    console.error("[searchRewrite] OpenAI client init failed:", e instanceof Error ? e.message : String(e));
    return null;
  }
}
var MULTI_CACHE = /* @__PURE__ */ new Map();
function multiCacheGet(key) {
  const hit = MULTI_CACHE.get(key);
  if (!hit) return null;
  if (Date.now() - hit.at > hit.ttlMs) {
    MULTI_CACHE.delete(key);
    return null;
  }
  MULTI_CACHE.delete(key);
  MULTI_CACHE.set(key, hit);
  return hit.paths;
}
function multiCacheSet(key, paths, ttlMs = CACHE_TTL_MS) {
  if (MULTI_CACHE.size >= CACHE_MAX) {
    const first = MULTI_CACHE.keys().next().value;
    if (first !== void 0) MULTI_CACHE.delete(first);
  }
  MULTI_CACHE.set(key, { paths, at: Date.now(), ttlMs });
}
var DECOMPOSITION_KEYS = [
  "subject",
  "style",
  "scene",
  "output",
  "era",
  "mood"
];
var PUNCTUATION_RE = /[!"#$%&'()*+,\-./:;<=>?@[\]^_`{|}~！？。，、；：""''（）【】《》～·]/g;
function compareKey(s) {
  return s.trim().toLowerCase().replace(PUNCTUATION_RE, "");
}
var REWRITE_STOPWORDS = /* @__PURE__ */ new Set([
  "the",
  "a",
  "an",
  "of",
  "in",
  "on",
  "is",
  "are",
  "and",
  "or",
  "to",
  "for",
  "with",
  "by",
  "at",
  "as",
  "be",
  "this",
  "that",
  "\u7684",
  "\u4E86",
  "\u548C",
  "\u53CA",
  "topic",
  "topics",
  "theme",
  "themes",
  "category",
  "categories",
  "insights",
  "highlights",
  "guide",
  "guides",
  "template"
]);
function normalizeRewriteText(s) {
  return tsToSc(s.toLowerCase().replace(/×/g, "x"));
}
function anchorTokens(text) {
  const normalized = normalizeRewriteText(text);
  let primary = normalized.split(/[\s,，、。.:：=·\/|()\[\]+*]+/).map((w) => w.trim()).filter((w) => w && !REWRITE_STOPWORDS.has(w));
  let expandedPrimary = [];
  let conceptGroups = [];
  for (const tok of primary) {
    if (/[一-龥]/.test(tok)) {
      const seg = segmentCJKToken(tok);
      expandedPrimary.push(...seg.tokens);
      conceptGroups.push(...seg.conceptGroups);
    } else {
      expandedPrimary.push(tok);
    }
  }
  expandedPrimary = [...new Set(expandedPrimary)];
  const phraseResult = applyPhraseAliasRulesExcluding(normalized, expandedPrimary, CJK_ATOMIC_PHRASES);
  primary = phraseResult.primary;
  const aliasGroups = [...conceptGroups, ...phraseResult.aliasGroups];
  return { primary, aliasGroups };
}
function anchorTokenSet(text) {
  const { primary, aliasGroups } = anchorTokens(text);
  const out = new Set(primary);
  for (const group of aliasGroups) for (const alt of group) out.add(alt);
  return out;
}
function hasCJK(s) {
  return /[一-龥]/.test(s);
}
function isWeakNumericAttribute(t) {
  if (/^\d+$/.test(t)) return true;
  if (/^\d+(k|p|fps|hz|px|cm|mm|kg|g|lb|min|sec|s)$/i.test(t)) return true;
  if (/^\d+x\d+$/i.test(t)) return true;
  if (/^\d+%$/.test(t)) return true;
  return false;
}
function isStrongIdentifierToken(t) {
  return /[a-z]/i.test(t) && /\d/.test(t) && !isWeakNumericAttribute(t);
}
function hasIndependentAnchor(primary) {
  return primary.some((t) => hasCJK(t) && t.length >= 2 || isStrongIdentifierToken(t));
}
function sharesRulePhrase(normalizedOriginal, normalizedCandidate) {
  return PHRASE_ALIAS_RULES.some((rule) => {
    const members = [rule.phrase, ...rule.aliasTokens ?? []].map((m) => m.toLowerCase());
    const originalHasMember = members.some((m) => normalizedOriginal.includes(m));
    const candidateHasMember = members.some((m) => normalizedCandidate.includes(m));
    return originalHasMember && candidateHasMember;
  });
}
function sharesCollapsedForm(normalizedOriginal, normalizedOther) {
  const collapsedOriginal = normalizedOriginal.replace(/\s+/g, "");
  const collapsedOther = normalizedOther.replace(/\s+/g, "");
  if (!collapsedOther || collapsedOther.length < 2) return false;
  return collapsedOriginal.includes(collapsedOther) || collapsedOther.includes(collapsedOriginal);
}
function extractOriginalAnchorPhrase(original) {
  const normalizedOriginal = normalizeRewriteText(original);
  for (const phrase of CJK_ATOMIC_PHRASES) {
    if (normalizedOriginal.includes(phrase.toLowerCase())) return phrase;
  }
  for (const rule of PHRASE_ALIAS_RULES) {
    if (normalizedOriginal.includes(rule.phrase.toLowerCase())) return rule.phrase;
  }
  const { primary } = anchorTokens(original);
  return primary.length > 0 ? primary[0] : null;
}
function evaluateRewriteCandidate(original, candidate, subject, bindTarget = subject) {
  const normalizedCandidate = normalizeRewriteText(candidate);
  const { primary, aliasGroups } = anchorTokens(candidate);
  const candidateAnchors = [.../* @__PURE__ */ new Set([...primary, ...aliasGroups.flat()])];
  const weakNumericAttributes = primary.filter(isWeakNumericAttribute);
  const strongIdentifiers = primary.filter(isStrongIdentifierToken);
  const base = {
    candidate,
    normalizedCandidate,
    executableTokens: primary,
    candidateAnchors,
    weakNumericAttributes,
    strongIdentifiers
  };
  if (primary.length === 0 && aliasGroups.length === 0) {
    return {
      ...base,
      originalAnchors: [],
      sharedAnchors: [],
      accepted: false,
      bindingApplied: false,
      executedQuery: candidate,
      reason: "EMPTY_EXECUTABLE_TOKENS"
    };
  }
  const subjectBasisText = subject ?? original;
  const subjectAnchors = anchorTokenSet(subjectBasisText);
  const originalAnchors = [...subjectAnchors];
  const sharedAnchors = candidateAnchors.filter((t) => subjectAnchors.has(t));
  if (sharedAnchors.length > 0 || sharesRulePhrase(normalizeRewriteText(original), normalizedCandidate) || sharesCollapsedForm(normalizeRewriteText(subjectBasisText), normalizedCandidate)) {
    return { ...base, originalAnchors, sharedAnchors, accepted: true, bindingApplied: false, executedQuery: candidate };
  }
  if (hasIndependentAnchor(primary)) {
    return { ...base, originalAnchors, sharedAnchors, accepted: true, bindingApplied: false, executedQuery: candidate };
  }
  if (subject && subject.trim()) {
    const prefix = bindTarget && bindTarget.trim() || subject.trim();
    return {
      ...base,
      originalAnchors,
      sharedAnchors,
      accepted: true,
      bindingApplied: true,
      executedQuery: `${prefix} ${candidate.trim()}`
    };
  }
  if (hasCJK(original) !== hasCJK(candidate)) {
    const fallbackAnchor = extractOriginalAnchorPhrase(original);
    if (fallbackAnchor && normalizeRewriteText(fallbackAnchor) !== normalizedCandidate) {
      return {
        ...base,
        originalAnchors,
        sharedAnchors,
        accepted: true,
        bindingApplied: true,
        executedQuery: `${fallbackAnchor.trim()} ${candidate.trim()}`
      };
    }
  }
  const reason = weakNumericAttributes.length > 0 && strongIdentifiers.length === 0 ? "WEAK_NUMERIC_ONLY_ANCHOR" : hasCJK(original) !== hasCJK(candidate) ? "CROSS_LANGUAGE_WITHOUT_ANCHOR" : "UNANCHORED_REWRITE_CANDIDATE";
  return {
    ...base,
    originalAnchors,
    sharedAnchors,
    accepted: false,
    bindingApplied: false,
    executedQuery: candidate,
    reason
  };
}
function evaluateSubjectCandidate(original, subject) {
  const normalizedSubject = normalizeRewriteText(subject);
  const { primary, aliasGroups } = anchorTokens(subject);
  const subjectAnchors = [.../* @__PURE__ */ new Set([...primary, ...aliasGroups.flat()])];
  const weakNumericAttributes = primary.filter(isWeakNumericAttribute);
  const strongIdentifiers = primary.filter(isStrongIdentifierToken);
  const base = {
    subject,
    normalizedSubject,
    executableTokens: primary,
    subjectAnchors,
    weakNumericAttributes,
    strongIdentifiers
  };
  if (primary.length === 0 && aliasGroups.length === 0) {
    return {
      ...base,
      originalAnchors: [],
      sharedAnchors: [],
      accepted: false,
      bindingApplied: false,
      executedSubject: subject,
      anchorBasisForDownstream: subject,
      reason: "EMPTY_EXECUTABLE_TOKENS"
    };
  }
  const originalAnchorSet = anchorTokenSet(original);
  const originalAnchors = [...originalAnchorSet];
  const sharedAnchors = subjectAnchors.filter((t) => originalAnchorSet.has(t));
  if (sharedAnchors.length > 0 || sharesRulePhrase(normalizeRewriteText(original), normalizedSubject) || sharesCollapsedForm(normalizeRewriteText(original), normalizedSubject)) {
    return { ...base, originalAnchors, sharedAnchors, accepted: true, bindingApplied: false, executedSubject: subject, anchorBasisForDownstream: subject };
  }
  if (hasIndependentAnchor(primary)) {
    return { ...base, originalAnchors, sharedAnchors, accepted: true, bindingApplied: false, executedSubject: subject, anchorBasisForDownstream: subject };
  }
  const fallbackAnchor = extractOriginalAnchorPhrase(original);
  if (fallbackAnchor && normalizeRewriteText(fallbackAnchor) !== normalizedSubject) {
    return {
      ...base,
      originalAnchors,
      sharedAnchors,
      accepted: true,
      bindingApplied: true,
      executedSubject: `${fallbackAnchor.trim()} ${subject.trim()}`,
      anchorBasisForDownstream: fallbackAnchor
    };
  }
  const reason = weakNumericAttributes.length > 0 && strongIdentifiers.length === 0 ? "WEAK_NUMERIC_ONLY_ANCHOR" : "UNANCHORED_DECOMPOSITION_SUBJECT";
  return {
    ...base,
    originalAnchors,
    sharedAnchors,
    accepted: false,
    bindingApplied: false,
    executedSubject: subject,
    anchorBasisForDownstream: subject,
    reason
  };
}
function flattenPathsWithDiagnostics(original, paths) {
  const executed = [];
  const rejected = [];
  const seen = /* @__PURE__ */ new Set([compareKey(original)]);
  const pushExecuted = (text, slotKey, slotValue, subjectBound) => {
    const t = text.trim();
    if (!t) return;
    const k = compareKey(t);
    if (!k || seen.has(k)) return;
    seen.add(k);
    executed.push({ text: t, slotKey, slotValue, subjectBound });
  };
  const subjectRaw = paths.decomposition.subject;
  const hasRawSubject = typeof subjectRaw === "string" && subjectRaw.trim().length > 0;
  let effectiveSubject;
  let anchorBasisForDownstream;
  if (hasRawSubject) {
    const subjEval = evaluateSubjectCandidate(original, subjectRaw);
    if (subjEval.accepted) {
      effectiveSubject = subjEval.executedSubject;
      anchorBasisForDownstream = subjEval.anchorBasisForDownstream;
    } else {
      rejected.push({ slotKey: "subject", slotValue: subjectRaw, reason: subjEval.reason });
    }
  }
  const hasSubject = effectiveSubject !== void 0;
  for (const r of paths.rewrites) {
    const evalResult = evaluateRewriteCandidate(original, r, anchorBasisForDownstream, effectiveSubject);
    if (!evalResult.accepted) {
      rejected.push({ slotKey: "rewrite", slotValue: r, reason: evalResult.reason });
      continue;
    }
    pushExecuted(evalResult.executedQuery, "rewrite", r, evalResult.bindingApplied);
  }
  if (hasSubject) pushExecuted(effectiveSubject, "subject", subjectRaw, true);
  for (const key of DECOMPOSITION_KEYS) {
    if (key === "subject") continue;
    const value = paths.decomposition[key];
    if (typeof value !== "string" || !value.trim()) continue;
    if (!hasSubject) {
      rejected.push({ slotKey: key, slotValue: value, reason: "UNBOUND_NON_SUBJECT_SLOT" });
      continue;
    }
    const { primary: modifierPrimary, aliasGroups: modifierAliasGroups } = anchorTokens(value);
    if (modifierPrimary.length === 0 && modifierAliasGroups.length === 0) {
      rejected.push({ slotKey: key, slotValue: value, reason: "EMPTY_EXECUTABLE_TOKENS" });
      continue;
    }
    if (modifierAliasGroups.length === 0 && modifierPrimary.every(isWeakNumericAttribute) && !modifierPrimary.some(isStrongIdentifierToken)) {
      rejected.push({ slotKey: key, slotValue: value, reason: "WEAK_NUMERIC_ONLY_ANCHOR" });
      continue;
    }
    const bound = `${effectiveSubject.trim()} ${value.trim()}`;
    pushExecuted(bound, key, value, true);
  }
  return { executed, rejected };
}
function flattenPaths(original, paths) {
  return flattenPathsWithDiagnostics(original, paths).executed.map((p) => p.text);
}
async function getMultiQueryPaths(query) {
  const empty = { rewrites: [], decomposition: {} };
  const trimmed = query.trim();
  if (trimmed.length < 2) return empty;
  const cacheKey = trimmed.toLowerCase();
  const cached = multiCacheGet(cacheKey);
  if (cached) return cached;
  const client = getClient();
  if (!client) return empty;
  try {
    const t0 = Date.now();
    const res = await client.chat.completions.create({
      model: MODEL,
      temperature: 0.4,
      max_tokens: MAX_TOKENS_MULTI,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: SYSTEM_PROMPT_MULTI },
        { role: "user", content: `Original query: ${trimmed}` }
      ]
    });
    const elapsedMs = Date.now() - t0;
    const raw = res.choices?.[0]?.message?.content?.trim() ?? "{}";
    const finishReason = res.choices?.[0]?.finish_reason;
    const cleaned = raw.replace(/^```(?:json)?\s*/i, "").replace(/```\s*$/i, "").trim();
    let parsed;
    try {
      parsed = JSON.parse(cleaned);
    } catch (e) {
      console.error(`[searchRewrite.multi] errorType=parse_failure query=${JSON.stringify(trimmed)} finish=${finishReason} elapsedMs=${elapsedMs} err=${e instanceof Error ? e.message : String(e)} raw="${raw.slice(0, 200)}"`);
      multiCacheSet(cacheKey, empty, NEGATIVE_CACHE_TTL_MS);
      return empty;
    }
    if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
      console.error(`[searchRewrite.multi] errorType=invalid_shape query=${JSON.stringify(trimmed)} finish=${finishReason} elapsedMs=${elapsedMs} parsedType=${parsed === null ? "null" : Array.isArray(parsed) ? "array" : typeof parsed}`);
      multiCacheSet(cacheKey, empty, NEGATIVE_CACHE_TTL_MS);
      return empty;
    }
    const parsedObj = parsed;
    const originalKey = compareKey(trimmed);
    let rawCandidateCount = 0;
    let refusalRejectedCount = 0;
    let sameQueryRejectedCount = 0;
    const rewrites = [];
    const seen = /* @__PURE__ */ new Set();
    const rawRewrites = Array.isArray(parsedObj.rewrites) ? parsedObj.rewrites : [];
    for (const r of rawRewrites) {
      if (typeof r !== "string") continue;
      const s = r.trim();
      if (!s) continue;
      rawCandidateCount++;
      if (s.length > MAX_REWRITE_CHARS) continue;
      if (looksLikeRefusal(s)) {
        refusalRejectedCount++;
        continue;
      }
      const k = compareKey(s);
      if (!k) continue;
      if (k === originalKey) {
        sameQueryRejectedCount++;
        continue;
      }
      if (seen.has(k)) continue;
      seen.add(k);
      rewrites.push(s);
      if (rewrites.length >= MAX_REWRITES) break;
    }
    const decomposition = {};
    const decRaw = parsedObj.decomposition && typeof parsedObj.decomposition === "object" && !Array.isArray(parsedObj.decomposition) ? parsedObj.decomposition : {};
    let rawDecompositionCount = 0;
    for (const key of DECOMPOSITION_KEYS) {
      const v = decRaw[key];
      if (typeof v !== "string") continue;
      const s = v.trim();
      if (!s) continue;
      rawCandidateCount++;
      rawDecompositionCount++;
      if (s.length > MAX_REWRITE_CHARS) continue;
      if (looksLikeRefusal(s)) {
        refusalRejectedCount++;
        continue;
      }
      const k = compareKey(s);
      if (!k) continue;
      if (k === originalKey) {
        sameQueryRejectedCount++;
        continue;
      }
      if (seen.has(k)) continue;
      seen.add(k);
      decomposition[key] = s;
    }
    const out = { rewrites, decomposition };
    const hasExecutablePath = flattenPathsWithDiagnostics(trimmed, out).executed.length > 0;
    if (hasExecutablePath) {
      if (refusalRejectedCount > 0) {
        console.error(`[searchRewrite.multi] errorType=model_refusal query=${JSON.stringify(trimmed)} finish=${finishReason} note=partial (other candidate(s) were usable)`);
      }
      multiCacheSet(cacheKey, out);
      return out;
    }
    let reason;
    if (rawCandidateCount === 0) {
      reason = "empty_output";
    } else if (refusalRejectedCount === rawCandidateCount) {
      reason = "model_refusal";
    } else if (sameQueryRejectedCount === rawCandidateCount) {
      reason = "same_query_only";
    } else if (rawRewrites.length === 0 && rawDecompositionCount > 0) {
      reason = "empty_decomposition";
    } else {
      reason = "all_candidates_filtered";
    }
    console.error(`[searchRewrite.multi] errorType=${reason} query=${JSON.stringify(trimmed)} finish=${finishReason} rawCandidateCount=${rawCandidateCount}`);
    multiCacheSet(cacheKey, out, NEGATIVE_CACHE_TTL_MS);
    return out;
  } catch (e) {
    const errorType = e instanceof Error && e.name === "APIConnectionTimeoutError" ? "timeout" : e instanceof Error && /network|ECONNRESET|ENOTFOUND|fetch failed/i.test(e.message) ? "network_error" : "api_error";
    console.error(`[searchRewrite.multi] errorType=${errorType} query=${JSON.stringify(trimmed)}: ${e instanceof Error ? `${e.name}: ${e.message}` : String(e)}`);
    return empty;
  }
}

// ../../../curify-frontend/lib/topic_resolver.ts
function normalizeTopicList(input) {
  if (!Array.isArray(input)) return [];
  const seen = /* @__PURE__ */ new Set();
  const result = [];
  for (const item of input) {
    if (typeof item !== "string") continue;
    const slug = item.trim().toLowerCase();
    if (!slug) continue;
    if (seen.has(slug)) continue;
    seen.add(slug);
    result.push(slug);
  }
  return result;
}
function buildTemplateTopicsMap(templates) {
  const map = /* @__PURE__ */ new Map();
  for (const t of templates) {
    if (typeof t?.id !== "string" || !t.id) continue;
    map.set(t.id, normalizeTopicList(t.topics));
  }
  return map;
}
function resolveTopics(inspiration, templateMap) {
  const inspirationTopics = normalizeTopicList(inspiration.topics);
  const templateId = typeof inspiration.template_id === "string" ? inspiration.template_id : "";
  const templateTopics = templateId ? templateMap.get(templateId) ?? [] : [];
  const mergedSet = new Set(inspirationTopics);
  for (const slug of templateTopics) mergedSet.add(slug);
  const mergedTopics = Array.from(mergedSet);
  return { inspirationTopics, templateTopics, mergedTopics };
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  CJK_ATOMIC_PHRASES,
  PHRASE_ALIAS_RULES,
  applyPhraseAliasRules,
  applyPhraseAliasRulesExcluding,
  buildTemplateTopicsMap,
  flattenPaths,
  flattenPathsWithDiagnostics,
  getMultiQueryPaths,
  resolveTopics,
  segmentCJKToken,
  segmentText,
  tsToSc
});
