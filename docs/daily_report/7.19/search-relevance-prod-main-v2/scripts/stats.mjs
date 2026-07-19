// Statistical comparison: McNemar's test (paired categorical PASS-rate
// change) + paired bootstrap CI for mean score difference. No external
// stats package -- implemented directly (small, auditable, standard
// formulas) since neither worktree nor this scripts dir has a stats
// dependency installed and installing one for a one-off analysis isn't
// warranted.
import fs from "fs";

function parseCSV(text) {
  const rows = [];
  let row = [], field = "", inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else inQuotes = false; }
      else field += c;
    } else {
      if (c === '"') inQuotes = true;
      else if (c === ',') { row.push(field); field = ""; }
      else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ""; }
      else if (c === '\r') { }
      else field += c;
    }
  }
  if (field.length > 0 || row.length > 0) { row.push(field); rows.push(row); }
  return rows;
}

function readPaired(csvPath) {
  const text = fs.readFileSync(csvPath, "utf8");
  const rows = parseCSV(text);
  const header = rows[0];
  const idx = Object.fromEntries(header.map((h, i) => [h, i]));
  return rows.slice(1).filter((r) => r.length > 1 && r[idx.query]).map((r) => ({
    query: r[idx.query],
    v0_total: Number(r[idx.v0_total]) || 0,
    v2_total: Number(r[idx.v2_total]) || 0,
    v0_zero: r[idx.v0_zero] === "true",
    v2_zero: r[idx.v2_zero] === "true",
    v0_label: r[idx.v0_label],
    v2_label: r[idx.v2_label],
    v0_score: r[idx.v0_score] === "" ? null : Number(r[idx.v0_score]),
    v2_score: r[idx.v2_score] === "" ? null : Number(r[idx.v2_score]),
  }));
}

// McNemar's test (with continuity correction) for paired PASS/not-PASS.
function mcnemar(rows) {
  let b = 0, c = 0; // b: v0 PASS -> v2 not-PASS; c: v0 not-PASS -> v2 PASS
  for (const r of rows) {
    const v0pass = r.v0_label === "PASS";
    const v2pass = r.v2_label === "PASS";
    if (v0pass && !v2pass) b++;
    if (!v0pass && v2pass) c++;
  }
  if (b + c === 0) return { b, c, chi2: 0, p: 1 };
  const chi2 = Math.pow(Math.abs(b - c) - 1, 2) / (b + c);
  // Approximate chi-square(1) p-value via complementary error function.
  const p = 1 - chiSquareCDF(chi2, 1);
  return { b, c, chi2, p };
}

function chiSquareCDF(x, k) {
  // k=1 special case: CDF = erf(sqrt(x/2))
  if (k === 1) return erf(Math.sqrt(x / 2));
  return NaN;
}
function erf(x) {
  const a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741, a4 = -1.453152027, a5 = 1.061405429, p = 0.3275911;
  const sign = x < 0 ? -1 : 1;
  x = Math.abs(x);
  const t = 1 / (1 + p * x);
  const y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
  return sign * y;
}

// Paired bootstrap CI for mean(v2_score - v0_score), using judgeable
// (non-null) pairs only. 2000 resamples.
function pairedBootstrap(rows, iterations = 2000) {
  const diffs = rows
    .filter((r) => r.v0_score !== null && r.v2_score !== null)
    .map((r) => r.v2_score - r.v0_score);
  if (diffs.length === 0) return { n: 0, mean_diff: null, ci_low: null, ci_high: null };
  const mean = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;
  const meanDiff = mean(diffs);
  const boot = [];
  for (let i = 0; i < iterations; i++) {
    const sample = [];
    for (let j = 0; j < diffs.length; j++) sample.push(diffs[Math.floor(Math.random() * diffs.length)]);
    boot.push(mean(sample));
  }
  boot.sort((a, b) => a - b);
  const lo = boot[Math.floor(iterations * 0.025)];
  const hi = boot[Math.floor(iterations * 0.975)];
  return { n: diffs.length, mean_diff: meanDiff, ci_low: lo, ci_high: hi };
}

// Wilcoxon signed-rank test (paired, non-parametric) on score differences.
function wilcoxonSignedRank(rows) {
  const diffs = rows
    .filter((r) => r.v0_score !== null && r.v2_score !== null && r.v2_score !== r.v0_score)
    .map((r) => r.v2_score - r.v0_score);
  const n = diffs.length;
  if (n === 0) return { n: 0, W: 0, z: 0, p: 1 };
  const abs = diffs.map((d) => Math.abs(d));
  const order = abs.map((v, i) => i).sort((a, b) => abs[a] - abs[b]);
  const ranks = new Array(n);
  let i = 0;
  while (i < n) {
    let j = i;
    while (j + 1 < n && abs[order[j + 1]] === abs[order[i]]) j++;
    const avgRank = (i + j) / 2 + 1;
    for (let k = i; k <= j; k++) ranks[order[k]] = avgRank;
    i = j + 1;
  }
  let Wpos = 0, Wneg = 0;
  for (let k = 0; k < n; k++) {
    if (diffs[k] > 0) Wpos += ranks[k];
    else Wneg += ranks[k];
  }
  const W = Math.min(Wpos, Wneg);
  const meanW = (n * (n + 1)) / 4;
  const sdW = Math.sqrt((n * (n + 1) * (2 * n + 1)) / 24);
  const z = sdW > 0 ? (W - meanW) / sdW : 0;
  const p = 2 * (1 - normalCDF(Math.abs(z)));
  return { n, W, z, p };
}
function normalCDF(x) { return 0.5 * (1 + erf(x / Math.sqrt(2))); }

export function analyze(pairedCSVPath) {
  const rows = readPaired(pairedCSVPath);
  const n = rows.length;
  const v0PassCount = rows.filter((r) => r.v0_label === "PASS").length;
  const v2PassCount = rows.filter((r) => r.v2_label === "PASS").length;
  const v0PartialCount = rows.filter((r) => r.v0_label === "PARTIAL").length;
  const v2PartialCount = rows.filter((r) => r.v2_label === "PARTIAL").length;
  const v0FailCount = rows.filter((r) => r.v0_label === "FAIL").length;
  const v2FailCount = rows.filter((r) => r.v2_label === "FAIL").length;
  const v0ZeroCount = rows.filter((r) => r.v0_zero).length;
  const v2ZeroCount = rows.filter((r) => r.v2_zero).length;
  const v0LowCount = rows.filter((r) => !r.v0_zero && r.v0_total > 0 && r.v0_total < 5).length;
  const v2LowCount = rows.filter((r) => !r.v2_zero && r.v2_total > 0 && r.v2_total < 5).length;
  const improved = rows.filter((r) => {
    const rank = { FAIL: 0, UNJUDGABLE: 1, PARTIAL: 2, PASS: 3 };
    return (rank[r.v2_label] ?? -1) > (rank[r.v0_label] ?? -1);
  }).length;
  const regressed = rows.filter((r) => {
    const rank = { FAIL: 0, UNJUDGABLE: 1, PARTIAL: 2, PASS: 3 };
    return (rank[r.v2_label] ?? -1) < (rank[r.v0_label] ?? -1);
  }).length;

  const mcnemarResult = mcnemar(rows);
  const bootstrap = pairedBootstrap(rows);
  const wilcoxon = wilcoxonSignedRank(rows);

  return {
    n,
    v0: { pass: v0PassCount, partial: v0PartialCount, fail: v0FailCount, zero: v0ZeroCount, low: v0LowCount, pass_rate: n ? v0PassCount / n : 0, fail_rate: n ? v0FailCount / n : 0, zero_rate: n ? v0ZeroCount / n : 0 },
    v2: { pass: v2PassCount, partial: v2PartialCount, fail: v2FailCount, zero: v2ZeroCount, low: v2LowCount, pass_rate: n ? v2PassCount / n : 0, fail_rate: n ? v2FailCount / n : 0, zero_rate: n ? v2ZeroCount / n : 0 },
    improved_queries: improved,
    regressed_queries: regressed,
    mcnemar: mcnemarResult,
    paired_bootstrap_score_diff: bootstrap,
    wilcoxon_signed_rank: wilcoxon,
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const result = analyze(process.argv[2]);
  console.log(JSON.stringify(result, null, 2));
}
