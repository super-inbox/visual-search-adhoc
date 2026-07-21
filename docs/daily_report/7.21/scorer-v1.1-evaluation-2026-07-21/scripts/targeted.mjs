// Collect full result detail for the targeted cases from BOTH servers.
// collector-only (no LLM). Dumps per-item id/title/tags/topics so we can
// do the disclosed inference of original-vs-non-original path membership
// for the 笔袋-class analysis (an item whose title+tags contain NO original
// query token can only have been surfaced by a rewrite/decomposition path).
import fs from "fs";
import { collectQuery } from "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.19/search-relevance-prod-main-v2/scripts/collector.mjs";

const BASE = "http://localhost:4520";
const CAND = "http://localhost:4521";
const OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/scorer-v1.1-evaluation-2026-07-21/eval_raw/targeted";
fs.mkdirSync(OUT, { recursive: true });

// query, locale
const CASES = [
  ["笔袋","zh"], ["促销海报","zh"], ["拼读卡","zh"],
  ["电影海报","zh"], ["sticker pack","en"], ["product photo","en"],
  ["日历","zh"], ["logo","en"], ["人体图解","zh"],
];

function tokenInBlob(blob, tok){ // whole-token / CJK substring check
  if(!tok) return false;
  return blob.includes(tok);
}

const summary = [];
for (const [q, locale] of CASES) {
  const [b, c] = await Promise.all([
    collectQuery(BASE, q, { locale }),
    collectQuery(CAND, q, { locale }),
  ]);
  const dump = (v) => v.ok ? {
    ok:true, totalResults:v.totalResults, inspirationCount:v.inspirationCount,
    matchedTemplateCount:v.matchedTemplateCount, pathsUsed:v.pathsUsed,
    usedRewrites:v.usedRewrites, rewriteTriggered:v.rewriteTriggered,
    inspirations: v.inspirations.map(x=>({id:x.id, template_id:x.template_id, title:x.title, tags:x.tags, topics:x.topics})),
  } : { ok:false, error:v.error };
  const rec = { query:q, locale, baseline:dump(b), candidate:dump(c) };
  fs.writeFileSync(`${OUT}/${q}.json`, JSON.stringify(rec, null, 2));

  // Inference: for each candidate/baseline inspiration in top 12, does its
  // title+tags contain the (single-token) query? If not -> off-subject / non-original-only.
  function offSubject(v){
    if(!v.ok) return {n:0, off:[]};
    const top = v.inspirations.slice(0,12);
    const off = top.filter(x=>{
      const blob = (x.title+" "+(x.tags||[]).join(" ")+" "+(x.topics||[]).join(" ")).toLowerCase();
      return !tokenInBlob(blob, q.toLowerCase());
    }).map(x=>({title:x.title, tags:(x.tags||[]).slice(0,6)}));
    return {n:top.length, off};
  }
  summary.push({
    query:q,
    base:{total:b.ok?b.totalResults:null, paths:b.pathsUsed, rewrites:b.usedRewrites, offSubjectTop12:offSubject(b)},
    cand:{total:c.ok?c.totalResults:null, paths:c.pathsUsed, rewrites:c.usedRewrites, offSubjectTop12:offSubject(c)},
  });
  console.log(`${q}: base total=${b.ok?b.totalResults:'ERR'} off=${offSubject(b).off.length}/${offSubject(b).n} | cand total=${c.ok?c.totalResults:'ERR'} off=${offSubject(c).off.length}/${offSubject(c).n}`);
}
fs.writeFileSync(`${OUT}/_SUMMARY.json`, JSON.stringify(summary, null, 2));
console.log("wrote targeted dumps to", OUT);
