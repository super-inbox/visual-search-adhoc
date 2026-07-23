// LLM-judge + rubric-v1.1 deterministic scoring, applied identically to
// V0 and V2 result sets. Evidence basis: textual (title/tags/topics),
// NOT screenshots -- same disclosed limitation as the historical
// full-328 evaluation runs in this project (see RELEVANCE_RUBRIC.md
// section 6: "full-328 screenshot reading was not performed for scale
// reasons and this is disclosed, not hidden"). This run makes the same
// disclosed tradeoff for the same reason (scale).
import fs from "fs";

const RANK_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10];
const LABEL_VALUES = { RELEVANT: 1.0, PARTIALLY_RELEVANT: 0.5, IRRELEVANT: 0.0 };

function loadEnv(worktreeEnvPath) {
  const envText = fs.readFileSync(worktreeEnvPath, "utf8");
  for (const line of envText.split("\n")) {
    const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^"|"$/g, "");
  }
}

const SYSTEM_PROMPT = `You are a strict relevance judge for an AI image-template search engine called Curify. You will be given a user's search query and up to 5 top results (each with a title, tags, and topics). For EACH result, judge whether its visual subject/object/scene/design-type/core semantic matches the query's core intent.

Labels:
- RELEVANT: the result's core visual subject clearly matches the query's core intent.
- PARTIALLY_RELEVANT: matches a secondary attribute, superordinate category, adjacent concept, or only part of a multi-component query.
- IRRELEVANT: does not match the query's core intent at all.
- UNJUDGABLE: the title/tags/topics give no usable signal to judge (essentially blank).

Also assess, across the whole result set:
- semantic_drift: NONE / MINOR / MODERATE / SEVERE -- did the underlying search/rewrite process appear to substitute or drift away from the query's original intent (visible from result content, not from any rewrite banner)?
- original_intent_preserved: YES / PARTIALLY / NO

Any common, plausible visual reading of an ambiguous word is acceptable -- do not penalize a query merely for having multiple senses unless the RESULTS clearly locked into a wrong sense.

Return ONLY a JSON object: {"results": [{"label": "RELEVANT|PARTIALLY_RELEVANT|IRRELEVANT|UNJUDGABLE"}, ...], "semantic_drift": "NONE|MINOR|MODERATE|SEVERE", "original_intent_preserved": "YES|PARTIALLY|NO"}
The results array must have exactly as many entries as the results given to you, in the same order. No prose, no markdown fences.`;

// ENVIRONMENT FINDING (2026-07-19, diagnosed live during this evaluation
// run): connectivity to api.openai.com in this environment is
// intermittently flaky (some individual attempts hit a connect timeout)
// but NOT permanently broken -- isolated re-testing with 3 sequential
// in-process fetch calls all succeeded quickly once no other heavy
// background load (concurrent eval batches) was competing for the
// network at the same moment. A curl-subprocess workaround was tried
// and found to hang unpredictably (worse, not better) so it was
// reverted. The fix that matters is: (a) real retry with backoff below,
// and (b) NOT running multiple eval batches concurrently against the
// same servers (see scripts/run_eval.mjs comment / RUN_LOG.md) -- this
// was the actual root cause of the failure clusters observed earlier in
// this session, not a Node/fetch defect.
async function chatCompletionJSON({ system, user, temperature = 0, maxTokens = 500 }) {
  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error("OPENAI_API_KEY not set");
  let lastErr;
  for (let attempt = 0; attempt < 4; attempt++) {
    if (attempt > 0) await new Promise((res) => setTimeout(res, 800 * Math.pow(2, attempt)));
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 20000);
    try {
      const res = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          model: "gpt-4o-mini",
          temperature,
          max_tokens: maxTokens,
          response_format: { type: "json_object" },
          messages: [
            { role: "system", content: system },
            { role: "user", content: user },
          ],
        }),
      });
      if (!res.ok) {
        const bodyText = await res.text();
        throw new Error(`OpenAI HTTP ${res.status}: ${bodyText.slice(0, 300)}`);
      }
      const data = await res.json();
      return data.choices?.[0]?.message?.content?.trim() ?? "{}";
    } catch (e) {
      lastErr = e;
      continue;
    } finally {
      clearTimeout(timer);
    }
  }
  throw lastErr;
}
/**
 * Judge one query's result set (top 5 items: {title, tags, topics}).
 * Returns the full rubric-v1.1 computation: label (PASS/PARTIAL/FAIL/
 * UNJUDGABLE), score (0-100 or null), and the raw per-result judgments.
 */
export async function judgeResultSet(query, top5Items, zeroResult) {
  if (zeroResult) {
    return {
      query_relevance_label: "FAIL",
      score: 0,
      primary_failure_reason: "ZERO_RESULT",
      per_result_labels: [],
      semantic_drift: "NONE",
      original_intent_preserved: "NO",
      judgeable_count: 0,
    };
  }
  if (top5Items.length === 0) {
    return {
      query_relevance_label: "UNJUDGABLE",
      score: null,
      primary_failure_reason: "NO_EVIDENCE",
      per_result_labels: [],
      semantic_drift: "NONE",
      original_intent_preserved: "YES",
      judgeable_count: 0,
    };
  }
  const itemsText = top5Items
    .map((it, i) => `${i + 1}. title="${it.title || "(no title)"}" tags=[${(it.tags || []).slice(0, 8).join(", ")}] topics=[${(it.topics || []).slice(0, 5).join(", ")}]`)
    .join("\n");
  let parsed;
  try {
    let raw;
    try {
      raw = await chatCompletionJSON({
        system: SYSTEM_PROMPT,
        user: `Query: "${query}"\n\nResults:\n${itemsText}`,
      });
    } catch (firstErr) {
      // Retry once -- transient network/connection-pool contention under
      // concurrent batch evaluation should not permanently mark a query
      // UNJUDGABLE if a retry succeeds.
      await new Promise((res) => setTimeout(res, 800));
      raw = await chatCompletionJSON({
        system: SYSTEM_PROMPT,
        user: `Query: "${query}"\n\nResults:\n${itemsText}`,
      });
    }
    parsed = JSON.parse(raw);
  } catch (e) {
    return {
      query_relevance_label: "UNJUDGABLE",
      score: null,
      primary_failure_reason: "JUDGE_CALL_FAILED:" + String((e && e.message) || e),
      per_result_labels: [],
      semantic_drift: "NONE",
      original_intent_preserved: "YES",
      judgeable_count: 0,
    };
  }
  const labels = Array.isArray(parsed.results)
    ? parsed.results.map((r) => r?.label).filter((l) => l in LABEL_VALUES || l === "UNJUDGABLE")
    : [];
  while (labels.length < top5Items.length) labels.push("UNJUDGABLE");
  const semantic_drift = ["NONE", "MINOR", "MODERATE", "SEVERE"].includes(parsed.semantic_drift) ? parsed.semantic_drift : "NONE";
  const original_intent_preserved = ["YES", "PARTIALLY", "NO"].includes(parsed.original_intent_preserved) ? parsed.original_intent_preserved : "YES";

  // Rubric-v1.1 deterministic scoring (computed here, not by the LLM).
  let numerator = 0, denominator = 0;
  let relevant = 0, partial = 0, irrelevant = 0, judgeable = 0;
  labels.forEach((label, i) => {
    if (label === "UNJUDGABLE") return;
    const w = RANK_WEIGHTS[i] ?? 0;
    const v = LABEL_VALUES[label] ?? 0;
    numerator += w * v;
    denominator += w;
    judgeable++;
    if (label === "RELEVANT") relevant++;
    else if (label === "PARTIALLY_RELEVANT") partial++;
    else if (label === "IRRELEVANT") irrelevant++;
  });
  const top5_weighted_relevance = denominator > 0 ? numerator / denominator : null;
  let base = top5_weighted_relevance !== null ? Math.round(top5_weighted_relevance * 100) : null;
  let label, score, primary_failure_reason = null;

  if (judgeable === 0) {
    label = "UNJUDGABLE";
    score = null;
    primary_failure_reason = "NO_JUDGEABLE_RESULTS";
  } else {
    const irrelevant_rate = irrelevant / judgeable;
    const relevant_rate = relevant / judgeable;
    const rel_plus_partial_rate = (relevant + partial) / judgeable;
    const hardFail = irrelevant_rate > 0.60 || (semantic_drift === "SEVERE" && original_intent_preserved === "NO");
    if (hardFail) {
      label = "FAIL";
      primary_failure_reason = irrelevant_rate > 0.60 ? "HIGH_IRRELEVANT_RATE" : "SEVERE_DRIFT_INTENT_LOST";
    } else if (
      irrelevant_rate <= 0.20 &&
      original_intent_preserved !== "NO" &&
      semantic_drift !== "SEVERE" &&
      (relevant_rate >= 0.60 || (rel_plus_partial_rate >= 0.80 && relevant_rate >= 0.20))
    ) {
      label = "PASS";
    } else {
      label = "PARTIAL";
    }
    // Deductions (Step 3), applied to base, floor 0.
    let deducted = base ?? 0;
    if (semantic_drift === "SEVERE") deducted -= 20;
    else if (semantic_drift === "MODERATE") deducted -= 10;
    else if (semantic_drift === "MINOR") deducted -= 3;
    if (original_intent_preserved === "NO") deducted -= 15;
    else if (original_intent_preserved === "PARTIALLY") deducted -= 5;
    score = Math.max(0, Math.min(100, deducted));
  }

  return {
    query_relevance_label: label,
    score,
    primary_failure_reason,
    per_result_labels: labels,
    semantic_drift,
    original_intent_preserved,
    judgeable_count: judgeable,
    relevant_count: relevant,
    partial_count: partial,
    irrelevant_count: irrelevant,
  };
}

export { loadEnv };
