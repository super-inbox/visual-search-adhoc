#!/usr/bin/env node
/**
 * Stage 7 relevance judge. Applies the rubric in judge_prompt.js (verbatim
 * from the 7.9 manual-review guide) to each (query, mode) cell from the
 * mode_{A,B,C,D}_results.json harness output. Blind: the judge only ever
 * sees {query, top_results}; it is never told which mode/condition produced
 * the results, and each call is independent/stateless. Deterministic:
 * temperature=0. Same model/prompt used for all four modes.
 */
"use strict";
const fs = require("fs");
const path = require("path");
require("dotenv").config({ path: "/Users/baobaoli/Desktop/curify-frontend/.env.local" });
const { JUDGE_SYSTEM_PROMPT } = require("./judge_prompt.js");

const OUT_DIR = __dirname;
const MODEL = "gpt-4o-mini";
const PROMPT_HASH = require("crypto").createHash("sha256").update(JUDGE_SYSTEM_PROMPT).digest("hex");

const OpenAI = require(path.join("/Users/baobaoli/Desktop/curify-frontend/node_modules/openai"));
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY, timeout: 20_000 });

async function judgeOne(query, topResults) {
  const userPayload = {
    query,
    result_count: topResults.length,
    top_results: topResults.map((r) => ({
      rank: r.rank,
      title: r.title,
      tags: (r.tags || []).slice(0, 12),
      match_type: r.strict_or_relaxed,
    })),
  };
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await client.chat.completions.create({
        model: MODEL,
        temperature: 0,
        max_tokens: 500,
        response_format: { type: "json_object" },
        messages: [
          { role: "system", content: JUDGE_SYSTEM_PROMPT },
          { role: "user", content: JSON.stringify(userPayload) },
        ],
      });
      const raw = res.choices?.[0]?.message?.content?.trim() ?? "{}";
      const parsed = JSON.parse(raw);
      return { ok: true, verdict: parsed, raw };
    } catch (e) {
      if (attempt === 2) return { ok: false, error: String(e && e.message ? e.message : e) };
    }
  }
}

async function main() {
  const modes = ["A", "B", "C", "D"];
  const out = {};
  for (const mode of modes) {
    const file = path.join(OUT_DIR, `mode_${mode}_results.json`);
    const data = JSON.parse(fs.readFileSync(file, "utf-8"));
    out[mode] = [];
    let i = 0;
    for (const r of data.results) {
      i++;
      if (r.error) {
        out[mode].push({ query: r.query, judge_error: "no_results_due_to_harness_error" });
        continue;
      }
      const j = await judgeOne(r.query, r.top_results || []);
      out[mode].push({ query: r.query, ...j });
      process.stderr.write(`[judge ${mode}] ${i}/68 "${r.query.slice(0, 30)}" -> ${j.ok ? j.verdict.relevance_label : "ERROR:" + j.error}\n`);
    }
  }
  fs.writeFileSync(
    path.join(OUT_DIR, "judge_results.json"),
    JSON.stringify({ model: MODEL, temperature: 0, promptSha256: PROMPT_HASH, generatedAt: new Date().toISOString(), byMode: out }, null, 2)
  );
  console.log("Wrote judge_results.json, promptSha256=", PROMPT_HASH);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
