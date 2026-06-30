import type { QueryItem } from "./types.js";

export const BING_IMAGE_EVAL_QUERIES: readonly QueryItem[] = [
  { query_id: 1, group: "user-2026-05-20", query: "单词" },
  { query_id: 2, group: "user-2026-05-20", query: "卡通" },
  { query_id: 3, group: "user-2026-05-20", query: "吉伊卡哇" },
  { query_id: 4, group: "user-2026-05-20", query: "家居装饰" },
  { query_id: 5, group: "user-2026-05-20", query: "工程" },
  { query_id: 6, group: "user-2026-05-20", query: "植物" },
  { query_id: 7, group: "user-2026-05-20", query: "水果中文" },
  { query_id: 8, group: "user-2026-05-20", query: "电商详情图" },
  { query_id: 9, group: "user-2026-05-20", query: "自行车" },
  { query_id: 10, group: "user-2026-05-20", query: "葡萄酒" },
  { query_id: 11, group: "user-2026-05-20", query: "蔬菜" },
  { query_id: 12, group: "user-2026-05-20", query: "词汇" },
  { query_id: 13, group: "user-2026-05-20", query: "趣味经济学知识科普" },
  { query_id: 14, group: "user-2026-05-20", query: "音乐" },
  { query_id: 15, group: "user-2026-05-20", query: "食物" },
  { query_id: 16, group: "user-2026-05-20", query: "香薰" },
  { query_id: 17, group: "user-report-2026-05-18", query: "唯美春天" },
  { query_id: 18, group: "user-report-2026-05-18", query: "证件照" },
  { query_id: 19, group: "user-report-2026-05-18", query: "手作" },
  { query_id: 20, group: "reddit", query: "historical character" },
  { query_id: 21, group: "reddit", query: "future characters" },
  { query_id: 22, group: "reddit", query: "homophones and homonyms" },
  { query_id: 23, group: "reddit", query: "english-chinese" },
  { query_id: 24, group: "reddit", query: "language learning expressions" },
  { query_id: 25, group: "reddit", query: "global influence" },
  { query_id: 26, group: "reddit", query: "remote destination" },
  { query_id: 27, group: "reddit", query: "unique cultural experiences" },
  { query_id: 28, group: "reddit", query: "short city escapes" },
  { query_id: 29, group: "reddit", query: "creative comfort food" },
  { query_id: 30, group: "popular", query: "mbti marvel" },
  { query_id: 31, group: "popular", query: "spring flowers" },
  { query_id: 32, group: "popular", query: "反义词" },
  { query_id: 33, group: "popular", query: "paper cutting" },
  { query_id: 34, group: "gsc-zero", query: "met gala" },
  { query_id: 35, group: "synthetic", query: "动物 词汇" },
  { query_id: 36, group: "synthetic", query: "wedding planner" },
  {
    query_id: 37,
    group: "progseo-2026-05-26",
    query: "minimalist autumn outfit for japan travel",
  },
  {
    query_id: 38,
    group: "progseo-2026-05-26",
    query: "infj vs entp dating compatibility chart",
  },
  {
    query_id: 39,
    group: "progseo-2026-05-26",
    query: "cuban sandwich recipe poster",
  },
  {
    query_id: 40,
    group: "progseo-2026-05-26",
    query: "bilingual flashcards for kids learning korean fruits",
  },
  {
    query_id: 41,
    group: "progseo-2026-05-26",
    query: "watercolor map of europe travel destinations",
  },
  {
    query_id: 42,
    group: "progseo-2026-05-26",
    query: "monstera plant care guide infographic",
  },
  {
    query_id: 43,
    group: "progseo-2026-05-26",
    query: "marvel mbti character chart 16 types",
  },
  {
    query_id: 44,
    group: "progseo-2026-05-26",
    query: "lunar new year red envelope graphic design",
  },
  {
    query_id: 45,
    group: "progseo-2026-05-26",
    query: "1950s vintage diner illustration retro poster",
  },
  {
    query_id: 46,
    group: "progseo-2026-05-26",
    query: "before after kitchen organization makeover",
  },
  {
    query_id: 47,
    group: "pinterest-discovery-2026-05-29",
    query: "phonics worksheets kindergarten",
  },
  {
    query_id: 48,
    group: "pinterest-discovery-2026-05-29",
    query: "Spanish vocabulary printable",
  },
  {
    query_id: 49,
    group: "pinterest-discovery-2026-05-29",
    query: "ESL flashcards printable",
  },
  {
    query_id: 50,
    group: "pinterest-discovery-2026-05-29",
    query: "easy weeknight dinners healthy",
  },
  {
    query_id: 51,
    group: "pinterest-discovery-2026-05-29",
    query: "gluten free dinner ideas",
  },
  {
    query_id: 52,
    group: "pinterest-discovery-2026-05-29",
    query: "meal prep weekly recipes",
  },
  {
    query_id: 53,
    group: "pinterest-discovery-2026-05-29",
    query: "cozy reading aesthetic",
  },
  {
    query_id: 54,
    group: "pinterest-discovery-2026-05-29",
    query: "book lovers gift guide",
  },
  { query_id: 55, group: "user-weekly-2026-05-30", query: "chiikawa" },
  { query_id: 56, group: "user-weekly-2026-05-30", query: "samurai" },
  { query_id: 57, group: "user-weekly-2026-05-30", query: "genshin" },
  { query_id: 58, group: "user-report-2026-06-05", query: "maps" },
] as const;

export function assertQueries(): void {
  if (BING_IMAGE_EVAL_QUERIES.length !== 58) {
    throw new Error(`Expected exactly 58 queries, got ${BING_IMAGE_EVAL_QUERIES.length}`);
  }
  if (BING_IMAGE_EVAL_QUERIES[0].query !== "单词") {
    throw new Error(`Unexpected first query: ${BING_IMAGE_EVAL_QUERIES[0].query}`);
  }
  if (BING_IMAGE_EVAL_QUERIES[57].query !== "maps") {
    throw new Error(`Unexpected last query: ${BING_IMAGE_EVAL_QUERIES[57].query}`);
  }
  if (!BING_IMAGE_EVAL_QUERIES.some((item) => item.query === "maps")) {
    throw new Error("maps query must be included");
  }
  const hasCat = BING_IMAGE_EVAL_QUERIES.some((item) => item.query.toLowerCase() === "cat");
  if (hasCat) throw new Error("cat must not be in the eval query set");
  if (BING_IMAGE_EVAL_QUERIES[34].query !== "动物 词汇") {
    throw new Error(`Query 35 must be "动物 词汇", got "${BING_IMAGE_EVAL_QUERIES[34].query}"`);
  }
  if (BING_IMAGE_EVAL_QUERIES[47].query !== "Spanish vocabulary printable") {
    throw new Error(
      `Query 48 must be "Spanish vocabulary printable", got "${BING_IMAGE_EVAL_QUERIES[47].query}"`,
    );
  }
  if (BING_IMAGE_EVAL_QUERIES[48].query !== "ESL flashcards printable") {
    throw new Error(
      `Query 49 must be "ESL flashcards printable", got "${BING_IMAGE_EVAL_QUERIES[48].query}"`,
    );
  }
}
