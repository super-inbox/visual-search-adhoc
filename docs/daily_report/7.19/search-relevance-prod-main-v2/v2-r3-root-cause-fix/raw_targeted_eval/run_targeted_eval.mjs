// V2-R3 targeted evaluation runner. Hits the three live servers (V0,
// V2-R1 frozen, V2-R3) with the SAME collector/judge methodology used by
// the prior V2-R2 stage, for exactly the fixed calibration/holdout/
// protection/invariant query sets from 03_V2_R3_CASE_SPLIT.csv. Does NOT
// touch functional_protection rows (those are structural invariants
// checked via the unit test suite, not live queries).
import fs from "fs";
import path from "path";
import { collectQuery } from "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/collector.mjs";
import { judgeResultSet, loadEnv } from "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/judge.mjs";

loadEnv("/Users/baobaoli/Desktop/curify-frontend-search-v2-r3-2026-07-19/.env.local");

const SERVERS = {
  v0: "http://localhost:4501",
  v2r1: "http://localhost:4502",
  v2r3: "http://localhost:4503",
};

function parseCsv(text) {
  const lines = text.split("\n").filter((l) => l.length > 0);
  const header = splitCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const cells = splitCsvLine(line);
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
}

function splitCsvLine(line) {
  const out = [];
  let cur = "";
  let inQ = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (inQ) {
      if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (c === '"') inQ = false;
      else cur += c;
    } else {
      if (c === '"') inQ = true;
      else if (c === ",") { out.push(cur); cur = ""; }
      else cur += c;
    }
  }
  out.push(cur);
  return out;
}

async function evalOneQueryOnServer(query) {
  const locale = /[一-鿿]/.test(query) ? "zh" : "en";
  const res = await collectQuery(SERVERS.__base, query, { locale });
  return res;
}

async function collectAndJudge(baseUrl, query) {
  const locale = /[一-鿿]/.test(query) ? "zh" : "en";
  const collected = await collectQuery(baseUrl, query, { locale });
  if (!collected.ok) {
    return { collected, judged: null };
  }
  const zeroResult = collected.totalResults === 0;
  const top5 = collected.inspirations.slice(0, 5);
  const judged = await judgeResultSet(query, top5, zeroResult);
  return { collected, judged };
}

async function main() {
  const caseSplitPath = process.argv[2];
  const outPath = process.argv[3];
  const csvText = fs.readFileSync(caseSplitPath, "utf8");
  const rows = parseCsv(csvText).filter((r) => r.set_name !== "functional_protection");

  const results = [];
  let i = 0;
  for (const row of rows) {
    i++;
    const query = row.query;
    console.error(`[${i}/${rows.length}] ${row.set_name} :: ${row.query_id} :: "${query}"`);
    const entry = { ...row, versions: {} };
    for (const [ver, baseUrl] of Object.entries(SERVERS)) {
      let attempt = 0;
      let done = false;
      while (!done && attempt < 2) {
        attempt++;
        try {
          const { collected, judged } = await collectAndJudge(baseUrl, query);
          entry.versions[ver] = { collected, judged };
          done = true;
        } catch (e) {
          console.error(`  ${ver} attempt ${attempt} failed: ${(e && e.message) || e}`);
          if (attempt >= 2) {
            entry.versions[ver] = { collected: { ok: false, error: String((e && e.message) || e) }, judged: null };
          }
        }
      }
    }
    results.push(entry);
    // Persist incrementally so a crash mid-run doesn't lose progress.
    fs.writeFileSync(outPath, JSON.stringify(results, null, 2));
  }
  console.error("DONE");
}

main().catch((e) => {
  console.error("FATAL", e);
  process.exit(1);
});
