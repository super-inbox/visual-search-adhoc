// Retry pass for the V2-R3 targeted eval: re-runs only (query, version)
// pairs that failed collection or judging in the first pass, with longer
// delays and more retry attempts to ride out the transient
// api.openai.com / local-server flakiness documented in judge.mjs's own
// header comment. Merges results back into the same output file.
import fs from "fs";
import { collectQuery } from "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/collector.mjs";
import { judgeResultSet, loadEnv } from "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/judge.mjs";

loadEnv("/Users/baobaoli/Desktop/curify-frontend-search-v2-r3-2026-07-19/.env.local");

const SERVERS = {
  v0: "http://localhost:4501",
  v2r1: "http://localhost:4502",
  v2r3: "http://localhost:4503",
};

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function isBad(v) {
  const c = v && v.collected;
  const j = v && v.judged;
  if (!c || c.ok === false) return true;
  if (!j) return true;
  if (j.query_relevance_label === "UNJUDGABLE" && j.primary_failure_reason && j.primary_failure_reason.startsWith("JUDGE_CALL_FAILED")) return true;
  return false;
}

async function collectAndJudge(baseUrl, query) {
  const locale = /[一-鿿]/.test(query) ? "zh" : "en";
  const collected = await collectQuery(baseUrl, query, { locale, timeoutMs: 45000 });
  if (!collected.ok) {
    return { collected, judged: null };
  }
  const zeroResult = collected.totalResults === 0;
  const top5 = collected.inspirations.slice(0, 5);
  const judged = await judgeResultSet(query, top5, zeroResult);
  return { collected, judged };
}

async function retryOne(baseUrl, query, maxAttempts = 5) {
  let last;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const result = await collectAndJudge(baseUrl, query);
      if (!isBad(result)) return result;
      last = result;
      console.error(`  attempt ${attempt} still bad (${result.collected?.error || result.judged?.primary_failure_reason})`);
    } catch (e) {
      console.error(`  attempt ${attempt} threw: ${(e && e.message) || e}`);
      last = { collected: { ok: false, error: String((e && e.message) || e) }, judged: null };
    }
    if (attempt < maxAttempts) await sleep(3000 * attempt);
  }
  return last;
}

async function main() {
  const inOutPath = process.argv[2];
  const rows = JSON.parse(fs.readFileSync(inOutPath, "utf8"));

  // Also fix the 4 CJK protection queries that accidentally included an
  // English gloss suffix in the query text (documentation artifact from
  // 03_V2_R3_CASE_SPLIT.csv, not how these queries are actually typed by
  // users / were actually tested historically).
  const QUERY_FIX = {
    "吉祥物 (mascot)": "吉祥物",
    "贴纸 (sticker)": "贴纸",
    "咖啡馆菜单 (cafe menu)": "咖啡馆菜单",
    "横幅 (banner, generic)": "横幅",
  };

  let retried = 0;
  for (const row of rows) {
    const fixedQuery = QUERY_FIX[row.query];
    const needsQueryFix = !!fixedQuery;
    if (needsQueryFix) row.query = fixedQuery;
    for (const [ver, baseUrl] of Object.entries(SERVERS)) {
      const v = row.versions[ver];
      if (needsQueryFix || isBad(v)) {
        retried++;
        console.error(`retry [${row.query_id}] ${ver} :: "${row.query}"`);
        const result = await retryOne(baseUrl, row.query);
        row.versions[ver] = result;
        fs.writeFileSync(inOutPath, JSON.stringify(rows, null, 2));
        await sleep(1000);
      }
    }
  }
  console.error(`DONE, retried ${retried} (query, version) pairs`);
}

main().catch((e) => {
  console.error("FATAL", e);
  process.exit(1);
});
