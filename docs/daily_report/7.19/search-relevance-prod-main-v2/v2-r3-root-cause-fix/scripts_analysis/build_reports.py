import csv, json, math, random, statistics
from collections import Counter

random.seed(20260719)

ROOT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.19/search-relevance-prod-main-v2"
V2R3_DIR = f"{ROOT}/v2-r3-root-cause-fix"
BANK = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv"

V0_CSV = f"{ROOT}/eval_raw/EASY326_V0.csv"
V2R1_CSV = f"{ROOT}/eval_raw/EASY326_V2.csv"
V2R3_CSV = f"{V2R3_DIR}/eval_raw/full326/EASY326_V2R3.csv"

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

bank = load(BANK)
v0 = load(V0_CSV)
r1 = load(V2R1_CSV)
r3 = load(V2R3_CSV)

assert len(bank) == 326, len(bank)
assert len(v0) == 326, len(v0)
assert len(r1) == 326, len(r1)
assert len(r3) == 326, len(r3)

# index by row_index (== query_id)
def by_idx(rows):
    d = {}
    for r in rows:
        i = int(r["row_index"])
        assert i not in d, f"dup row_index {i}"
        d[i] = r
    return d

v0i, r1i, r3i = by_idx(v0), by_idx(r1), by_idx(r3)

# sanity: query text alignment across all four sources at every index
mismatches = []
for i in range(326):
    qb = bank[i]["query"]
    for name, d in (("V0", v0i), ("V2R1", r1i), ("V2R3", r3i)):
        if d[i]["query"] != qb:
            mismatches.append((i, name, d[i]["query"], qb))
if mismatches:
    print("QUERY ALIGNMENT MISMATCHES:", mismatches[:10])
    raise SystemExit(1)
print("Query alignment OK across bank/V0/V2R1/V2R3 for all 326 rows.")

LABEL_RANK = {"FAIL": 0, "UNJUDGABLE": 1, "PARTIAL": 2, "PASS": 3}

def is_tech_error(row):
    ok = row["ok"] == "True" or row["ok"] == "true"
    ce = row.get("collect_error", "")
    pfr = row.get("primary_failure_reason", "")
    return (not ok) or bool(ce) or pfr.startswith("TECHNICAL_ERROR") or pfr.startswith("JUDGE_CALL_FAILED")

def is_timeout(row):
    ce = row.get("collect_error", "")
    return "abort" in ce.lower() or "timeout" in ce.lower()

def flooding_flag(row):
    try:
        total = int(row["total_results"])
    except (ValueError, KeyError):
        return False
    return total >= 200

def broad_noise_flag(row):
    try:
        total = int(row["total_results"])
        rel = int(row["relevant_count"]) if row["relevant_count"] not in ("", None) else 0
        judgeable = int(row["judgeable_count"]) if row["judgeable_count"] not in ("", None) else 0
    except (ValueError, KeyError):
        return False
    if total < 50 or judgeable == 0:
        return False
    return (rel / judgeable) < 0.3

# ---------- File 13: V2-R3 results ----------
out13_path = f"{V2R3_DIR}/13_V2_R3_EASY326_RESULTS.csv"
cols13 = [
    "query_id", "query", "language", "scenario", "category",
    "ok", "technical_error", "timeout", "collect_error", "http_status", "elapsed_ms",
    "result_count", "zero_result", "low_result",
    "rewrite_triggered", "accepted_rewrites_used", "raw_rewrite_not_captured_by_methodology",
    "rejected_rewrites_not_captured_by_methodology", "paths_used", "decomposition",
    "top5_titles", "top5_score", "relevance_label", "failure_reason",
    "semantic_drift", "original_intent_preserved", "judgeable_count",
    "relevant_count", "partial_count", "irrelevant_count",
    "flooding_flag", "broad_noise_flag", "retry_count_not_individually_logged",
]
label_counts13 = Counter()
tech_err_count = 0
with open(out13_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cols13)
    for i in range(326):
        b = bank[i]
        row = r3i[i]
        label = row["relevance_label"]
        label_counts13[label] += 1
        te = is_tech_error(row)
        if te:
            tech_err_count += 1
        w.writerow([
            i, row["query"], row["language"], b["scenario"], b["category"],
            row["ok"], te, is_timeout(row), row.get("collect_error", ""), row.get("http_status", ""), row.get("elapsed_ms", ""),
            row.get("total_results", ""), row.get("zero_result", ""), row.get("low_result", ""),
            row.get("rewrite_triggered", ""), row.get("used_rewrites", ""), "NOT_CAPTURED_BY_METHODOLOGY",
            "NOT_CAPTURED_BY_METHODOLOGY", row.get("paths_used", ""),
            (row.get("paths_used", "") not in ("", "1")),
            row.get("top5_titles", ""), row.get("relevance_score", ""), label, row.get("primary_failure_reason", ""),
            row.get("semantic_drift", ""), row.get("original_intent_preserved", ""), row.get("judgeable_count", ""),
            row.get("relevant_count", ""), row.get("partial_count", ""), row.get("irrelevant_count", ""),
            flooding_flag(row), broad_noise_flag(row), "NOT_INDIVIDUALLY_LOGGED_BY_HARNESS",
        ])

assert sum(label_counts13.values()) == 326
print("File 13 written:", out13_path, dict(label_counts13), "technical_errors=", tech_err_count)

# ---------- File 14: 3-way paired ----------
out14_path = f"{V2R3_DIR}/14_V0_V2_R1_V2_R3_EASY326_PAIRED.csv"
cols14 = [
    "query_id", "query", "language", "scenario", "category",
    "v0_label", "v2r1_label", "v2r3_label",
    "v0_score", "v2r1_score", "v2r3_score",
    "v0_zero", "v2r1_zero", "v2r3_zero",
    "v0_total", "v2r1_total", "v2r3_total",
    "v0_to_r1_change", "v0_to_r3_change", "r1_to_r3_change",
    "v0_to_r1_label_upgrade", "v0_to_r1_label_downgrade",
    "v0_to_r3_label_upgrade", "v0_to_r3_label_downgrade",
    "r1_to_r3_label_upgrade", "r1_to_r3_label_downgrade",
    "in_original_50_regression_set", "in_targeted_5_new_regression_set",
]

REGRESSION_50_IDS = {2,3,6,7,18,19,22,23,26,33,51,52,65,70,91,96,97,107,112,114,115,116,117,122,125,137,139,148,153,155,171,191,195,199,202,206,211,219,240,241,242,248,254,268,270,278,284,285,294,308}
NEW_5_REGRESSION_IDS = {97,112,114,116,122}  # coffee package, 化妆品包装, 酒标, 零食包装, 产品标签

def change(a, b):
    ra, rb = LABEL_RANK.get(a, -1), LABEL_RANK.get(b, -1)
    if rb > ra: return "improved"
    if rb < ra: return "regressed"
    return "unchanged"

def score_f(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None

paired_rows = []
with open(out14_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cols14)
    for i in range(326):
        b = bank[i]
        rv0, rv1, rv3 = v0i[i], r1i[i], r3i[i]
        l0, l1, l3 = rv0["relevance_label"], rv1["relevance_label"], rv3["relevance_label"]
        s0, s1, s3 = score_f(rv0["relevance_score"]), score_f(rv1["relevance_score"]), score_f(rv3["relevance_score"])
        c01, c03, c13 = change(l0, l1), change(l0, l3), change(l1, l3)
        row = [
            i, b["query"], rv0["language"], b["scenario"], b["category"],
            l0, l1, l3, s0, s1, s3,
            rv0.get("zero_result", ""), rv1.get("zero_result", ""), rv3.get("zero_result", ""),
            rv0.get("total_results", ""), rv1.get("total_results", ""), rv3.get("total_results", ""),
            c01, c03, c13,
            c01 == "improved", c01 == "regressed",
            c03 == "improved", c03 == "regressed",
            c13 == "improved", c13 == "regressed",
            i in REGRESSION_50_IDS, i in NEW_5_REGRESSION_IDS,
        ]
        w.writerow(row)
        paired_rows.append({
            "query_id": i, "query": b["query"], "l0": l0, "l1": l1, "l3": l3,
            "s0": s0, "s1": s1, "s3": s3,
            "z0": rv0.get("zero_result") in ("True", "true"),
            "z1": rv1.get("zero_result") in ("True", "true"),
            "z3": rv3.get("zero_result") in ("True", "true"),
            "c01": c01, "c03": c03, "c13": c13,
        })

print("File 14 written:", out14_path)

# ---------- Stats helpers ----------
def erf(x):
    a1,a2,a3,a4,a5,p = 0.254829592,-0.284496736,1.421413741,-1.453152027,1.061405429,0.3275911
    sign = -1 if x < 0 else 1
    x = abs(x)
    t = 1/(1+p*x)
    y = 1 - (((((a5*t+a4)*t)+a3)*t+a2)*t+a1)*t*math.exp(-x*x)
    return sign*y

def normal_cdf(x):
    return 0.5*(1+erf(x/math.sqrt(2)))

def chi2_cdf_k1(x):
    return erf(math.sqrt(x/2))

def mcnemar(pairs, key_a, key_b):
    b = c = 0
    for p in pairs:
        pa = p[key_a] == "PASS"
        pb = p[key_b] == "PASS"
        if pa and not pb: b += 1
        if not pa and pb: c += 1
    if b + c == 0:
        return {"b": b, "c": c, "chi2": 0.0, "p": 1.0}
    chi2 = (abs(b-c)-1)**2 / (b+c)
    p = 1 - chi2_cdf_k1(chi2)
    return {"b": b, "c": c, "chi2": chi2, "p": p}

def paired_bootstrap(pairs, key_a, key_b, iters=2000):
    diffs = [p[key_b]-p[key_a] for p in pairs if p[key_a] is not None and p[key_b] is not None]
    if not diffs:
        return {"n": 0, "mean_diff": None, "ci_low": None, "ci_high": None}
    mean = lambda arr: sum(arr)/len(arr)
    md = mean(diffs)
    boot = []
    for _ in range(iters):
        sample = [diffs[random.randrange(len(diffs))] for _ in diffs]
        boot.append(mean(sample))
    boot.sort()
    lo = boot[int(iters*0.025)]
    hi = boot[int(iters*0.975)]
    return {"n": len(diffs), "mean_diff": md, "ci_low": lo, "ci_high": hi}

def wilcoxon(pairs, key_a, key_b):
    diffs = [p[key_b]-p[key_a] for p in pairs if p[key_a] is not None and p[key_b] is not None and p[key_a] != p[key_b]]
    n = len(diffs)
    if n == 0:
        return {"n": 0, "W": 0, "z": 0.0, "p": 1.0}
    absd = [abs(d) for d in diffs]
    order = sorted(range(n), key=lambda i: absd[i])
    ranks = [0.0]*n
    i = 0
    while i < n:
        j = i
        while j+1 < n and absd[order[j+1]] == absd[order[i]]:
            j += 1
        avg_rank = (i+j)/2 + 1
        for k in range(i, j+1):
            ranks[order[k]] = avg_rank
        i = j+1
    Wpos = sum(ranks[k] for k in range(n) if diffs[k] > 0)
    Wneg = sum(ranks[k] for k in range(n) if diffs[k] < 0)
    W = min(Wpos, Wneg)
    meanW = n*(n+1)/4
    sdW = math.sqrt(n*(n+1)*(2*n+1)/24)
    z = (W-meanW)/sdW if sdW > 0 else 0.0
    p = 2*(1-normal_cdf(abs(z)))
    return {"n": n, "W": W, "z": z, "p": p}

def label_dist(pairs, key):
    c = Counter(p[key] for p in pairs)
    return {k: c.get(k, 0) for k in ("PASS", "PARTIAL", "FAIL", "UNJUDGABLE")}

def score_stats(pairs, key):
    vals = [p[key] for p in pairs if p[key] is not None]
    if not vals:
        return {"mean": None, "median": None, "n": 0}
    return {"mean": statistics.mean(vals), "median": statistics.median(vals), "n": len(vals)}

def zero_low_counts(rows_dict):
    zero = sum(1 for r in rows_dict.values() if r.get("zero_result") in ("True", "true"))
    low = sum(1 for r in rows_dict.values() if r.get("low_result") in ("True", "true"))
    return zero, low

def improved_regressed(pairs, key):
    imp = sum(1 for p in pairs if p[key] == "improved")
    reg = sum(1 for p in pairs if p[key] == "regressed")
    unc = sum(1 for p in pairs if p[key] == "unchanged")
    return imp, reg, unc

results = {}
for pairname, ka_l, kb_l, ka_s, kb_s, ckey in (
    ("V0_to_V2R1", "l0", "l1", "s0", "s1", "c01"),
    ("V0_to_V2R3", "l0", "l3", "s0", "s3", "c03"),
    ("V2R1_to_V2R3", "l1", "l3", "s1", "s3", "c13"),
):
    mc = mcnemar(paired_rows, ka_l, kb_l)
    bs = paired_bootstrap(paired_rows, ka_s, kb_s)
    wc = wilcoxon(paired_rows, ka_s, kb_s)
    imp, reg, unc = improved_regressed(paired_rows, ckey)
    results[pairname] = {
        "mcnemar": mc, "bootstrap": bs, "wilcoxon": wc,
        "improved": imp, "regressed": reg, "unchanged": unc,
        "label_dist_a": label_dist(paired_rows, ka_l), "label_dist_b": label_dist(paired_rows, kb_l),
        "score_stats_a": score_stats(paired_rows, ka_s), "score_stats_b": score_stats(paired_rows, kb_s),
    }

zero0, low0 = zero_low_counts(v0i)
zero1, low1 = zero_low_counts(r1i)
zero3, low3 = zero_low_counts(r3i)

summary = {
    "n": 326,
    "v0": {"labels": label_dist(paired_rows, "l0"), "score": score_stats(paired_rows, "s0"), "zero": zero0, "low": low0},
    "v2r1": {"labels": label_dist(paired_rows, "l1"), "score": score_stats(paired_rows, "s1"), "zero": zero1, "low": low1},
    "v2r3": {"labels": label_dist(paired_rows, "l3"), "score": score_stats(paired_rows, "s3"), "zero": zero3, "low": low3},
    "pairwise": results,
}

with open(f"{V2R3_DIR}/_summary_stats.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print(json.dumps(summary, indent=2, default=str))

# ---------- Original-50-regression fix rate in R3 ----------
reg50 = [p for p in paired_rows if p["query_id"] in REGRESSION_50_IDS]
fixed = sum(1 for p in reg50 if p["c13"] == "improved" or (LABEL_RANK[p["l3"]] > LABEL_RANK[p["l1"]]))
newreg_in50 = sum(1 for p in reg50 if p["c13"] == "regressed")
unchanged50 = sum(1 for p in reg50 if p["c13"] == "unchanged")
print(f"\nOriginal 50-regression set at FULL326 scale: n={len(reg50)} fixed(R1->R3 improved)={fixed} newly_regressed(R1->R3)={newreg_in50} unchanged={unchanged50}")

new5 = [p for p in paired_rows if p["query_id"] in NEW_5_REGRESSION_IDS]
print("\n5 targeted-stage new-regression queries at FULL326 scale:")
for p in new5:
    print(f"  qid={p['query_id']:>4} {p['query']:<20} V0={p['l0']}/{p['s0']} V2R1={p['l1']}/{p['s1']} V2R3={p['l3']}/{p['s3']}  R1->R3={p['c13']}")

# ---------- specific flagged cases ----------
print("\nFlagged softening cases (coffee cup / 贴纸 / 咖啡馆菜单) at FULL326 scale:")
for qtext in ("coffee cup", "贴纸", "咖啡馆菜单", "吉祥物"):
    for p in paired_rows:
        if p["query"] == qtext:
            print(f"  {qtext:<12} qid={p['query_id']:>4} V0={p['l0']}/{p['s0']} V2R1={p['l1']}/{p['s1']} V2R3={p['l3']}/{p['s3']}  R1->R3={p['c13']}")

with open(f"{V2R3_DIR}/_reg50_and_new5_and_flagged.json", "w") as f:
    json.dump({
        "reg50_n": len(reg50), "reg50_fixed_r1_to_r3": fixed, "reg50_new_regression_r1_to_r3": newreg_in50,
        "reg50_unchanged": unchanged50,
        "new5_detail": new5,
        "flagged_cases": {qtext: [p for p in paired_rows if p["query"] == qtext] for qtext in ("coffee cup", "贴纸", "咖啡馆菜单", "吉祥物", "statue", "periodic table", "globe")},
    }, f, indent=2, default=str)

print("\nDONE analysis script.")
