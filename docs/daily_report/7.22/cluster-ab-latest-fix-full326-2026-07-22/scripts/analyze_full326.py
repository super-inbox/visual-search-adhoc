import csv
import json
import statistics
from collections import Counter

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22"
BANK = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv"
BASE_CSV = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/eval_raw/BASELINE_EASY326.csv"
PREV_CSV = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/eval_raw/CANDIDATE_EASY326.csv"
LATEST_CSV = f"{OUT}/eval_raw/CANDIDATE_LATEST_EASY326.csv"

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def by_idx(rows):
    return {int(r["row_index"]): r for r in rows}

bank = load(BANK)
base = by_idx(load(BASE_CSV))
prev = by_idx(load(PREV_CSV))
latest = by_idx(load(LATEST_CSV))
n = len(bank)
print(f"bank={n} base={len(base)} prev={len(prev)} latest={len(latest)}")

# alignment check across all three
mism = []
for i in range(n):
    for name, d in [("base", base), ("prev", prev), ("latest", latest)]:
        if d.get(i) and d[i]["query"] != bank[i]["query"]:
            mism.append((i, name, d[i]["query"], bank[i]["query"]))
print("alignment mismatches:", mism if mism else "NONE")

LABEL_RANK = {"FAIL": 0, "UNJUDGABLE": 1, "PARTIAL": 2, "PASS": 3}

def label(r): return r["relevance_label"]
def zero(r): return r["zero_result"] in ("True", "true")
def low(r): return r["low_result"] in ("True", "true")
def total(r):
    try: return int(r["total_results"])
    except Exception: return None
def score(r):
    try: return float(r["relevance_score"])
    except Exception: return None
def top5(r):
    try: return json.loads(r.get("top5_titles", "[]"))
    except Exception: return []

def dist(d):
    rows = [d[i] for i in range(n) if d.get(i)]
    c = Counter(label(r) for r in rows)
    z = sum(1 for r in rows if zero(r))
    lo = sum(1 for r in rows if low(r))
    totals = [total(r) for r in rows if total(r) is not None]
    scs = [score(r) for r in rows if score(r) is not None]
    mean_t = sum(totals) / len(totals) if totals else 0
    med_t = statistics.median(totals) if totals else 0
    mean_s = sum(scs) / len(scs) if scs else 0
    return {
        "PASS": c.get("PASS", 0), "PARTIAL": c.get("PARTIAL", 0),
        "FAIL": c.get("FAIL", 0), "UNJUDGABLE": c.get("UNJUDGABLE", 0),
        "zero": z, "low": lo, "mean_total": mean_t, "median_total": med_t,
        "min_total": min(totals) if totals else 0, "max_total": max(totals) if totals else 0,
        "mean_score": mean_s, "n": len(rows),
    }

base_d = dist(base)
prev_d = dist(prev)
latest_d = dist(latest)

print("\n=== base ===", base_d)
print("=== prev ===", prev_d)
print("=== latest ===", latest_d)

# ---------- 03_FULL326_LATEST_RESULTS.csv ----------
cols03 = ["row_index", "query", "language", "scenario", "category", "ok", "http_status", "elapsed_ms",
          "total_results", "inspiration_count", "matched_template_count", "gallery_prompt_count",
          "zero_result", "low_result", "rewrite_triggered", "used_rewrites", "paths_used",
          "relevance_label", "relevance_score", "primary_failure_reason", "semantic_drift",
          "original_intent_preserved", "judgeable_count", "relevant_count", "partial_count", "irrelevant_count",
          "top5_titles"]
with open(f"{OUT}/03_FULL326_LATEST_RESULTS.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols03)
    w.writeheader()
    for i in range(n):
        b = bank[i]
        r = latest.get(i, {})
        row = {"row_index": i, "query": b["query"], "language": b["language"],
               "scenario": b.get("scenario", ""), "category": b.get("category", "")}
        for c in cols03[5:]:
            row[c] = r.get(c, "")
        w.writerow(row)
print("wrote 03_FULL326_LATEST_RESULTS.csv")

# ---------- 04_FULL326_TOP_RESULTS.csv ----------
cols04 = ["row_index", "query", "language", "rank", "title", "note"]
with open(f"{OUT}/04_FULL326_TOP_RESULTS.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols04)
    w.writeheader()
    for i in range(n):
        b = bank[i]
        r = latest.get(i, {})
        titles = top5(r)
        if not titles:
            w.writerow({"row_index": i, "query": b["query"], "language": b["language"],
                        "rank": "", "title": "", "note": "NO_RESULTS_OR_UNAVAILABLE"})
        for rank, t in enumerate(titles, start=1):
            w.writerow({"row_index": i, "query": b["query"], "language": b["language"],
                        "rank": rank, "title": t,
                        "note": "top5 only -- collector/judge schema does not capture top10 (established methodology limit, unavailable field)"})
print("wrote 04_FULL326_TOP_RESULTS.csv")

# ---------- transitions vs production baseline ----------
def build_transitions(other_d, other_name):
    rows_out = []
    improved, regressed, unchanged = [], [], 0
    trans = Counter()
    for i in range(n):
        o = other_d.get(i)
        l = latest.get(i)
        if not o or not l:
            continue
        ol, ll = label(o), label(l)
        trans[(ol, ll)] += 1
        orank, lrank = LABEL_RANK.get(ol, -1), LABEL_RANK.get(ll, -1)
        imp = lrank > orank
        reg = lrank < orank
        if imp: improved.append(i)
        elif reg: regressed.append(i)
        else: unchanged += 1
        rows_out.append({
            "row_index": i, "query": bank[i]["query"], "language": bank[i].get("language", ""),
            "category": bank[i].get("category", ""),
            f"{other_name}_status": ol, "latest_status": ll,
            f"{other_name}_total": total(o), "latest_total": total(l),
            f"{other_name}_zero": zero(o), "latest_zero": zero(l),
            f"{other_name}_low": low(o), "latest_low": low(l),
            "transition": f"{ol}->{ll}",
            "direction": "IMPROVED" if imp else ("REGRESSED" if reg else "UNCHANGED"),
            f"{other_name}_top5": o.get("top5_titles", ""), "latest_top5": l.get("top5_titles", ""),
        })
    return rows_out, improved, regressed, unchanged, trans

rows_prod, imp_prod, reg_prod, unch_prod, trans_prod = build_transitions(base, "production")
rows_prevcand, imp_prevcand, reg_prevcand, unch_prevcand, trans_prevcand = build_transitions(prev, "prevcandidate")

cols05 = ["row_index", "query", "language", "category", "production_status", "latest_status",
          "production_total", "latest_total", "production_zero", "latest_zero", "production_low", "latest_low",
          "transition", "direction", "production_top5", "latest_top5"]
with open(f"{OUT}/05_STATUS_TRANSITIONS_VS_PRODUCTION.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols05); w.writeheader()
    for r in rows_prod: w.writerow(r)
print(f"wrote 05, improved={len(imp_prod)} regressed={len(reg_prod)} unchanged={unch_prod}")

cols06 = ["row_index", "query", "language", "category", "prevcandidate_status", "latest_status",
          "prevcandidate_total", "latest_total", "prevcandidate_zero", "latest_zero",
          "prevcandidate_low", "latest_low", "transition", "direction", "prevcandidate_top5", "latest_top5"]
with open(f"{OUT}/06_STATUS_TRANSITIONS_VS_PREVIOUS_CANDIDATE.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols06); w.writeheader()
    for r in rows_prevcand: w.writerow(r)
print(f"wrote 06, improved={len(imp_prevcand)} regressed={len(reg_prevcand)} unchanged={unch_prevcand}")

# ---------- 07/08 improvements & regressions (vs production, the primary axis) ----------
def severity(o_total, l_total, o_zero, l_zero):
    if o_zero and l_zero: return "STILL_ZERO"
    if (not o_zero) and l_zero: return "NEW_ZERO_HIGH"
    if o_zero and (not l_zero): return "RECOVERED_ZERO"
    return "NORMAL"

with open(f"{OUT}/07_IMPROVEMENTS.csv", "w", newline="", encoding="utf-8") as f:
    cols = ["row_index", "query", "language", "category", "production_status", "latest_status",
            "prevcandidate_status", "production_total", "latest_total", "production_top5", "latest_top5",
            "zero_low_note"]
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for i in sorted(imp_prod):
        b = base[i]; l = latest[i]; p = prev.get(i)
        note = severity(total(b), total(l), zero(b), zero(l))
        w.writerow({"row_index": i, "query": bank[i]["query"], "language": bank[i]["language"],
                    "category": bank[i].get("category", ""),
                    "production_status": label(b), "latest_status": label(l),
                    "prevcandidate_status": label(p) if p else "",
                    "production_total": total(b), "latest_total": total(l),
                    "production_top5": b.get("top5_titles", ""), "latest_top5": l.get("top5_titles", ""),
                    "zero_low_note": note})
print(f"wrote 07_IMPROVEMENTS.csv ({len(imp_prod)} rows)")

with open(f"{OUT}/08_REGRESSIONS.csv", "w", newline="", encoding="utf-8") as f:
    cols = ["row_index", "query", "language", "category", "production_status", "latest_status",
            "prevcandidate_status", "production_total", "latest_total", "production_top5", "latest_top5",
            "severity", "new_zero_result"]
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for i in sorted(reg_prod):
        b = base[i]; l = latest[i]; p = prev.get(i)
        new_zero = (not zero(b)) and zero(l)
        sev = "HIGH" if new_zero or label(l) == "FAIL" else "MEDIUM"
        w.writerow({"row_index": i, "query": bank[i]["query"], "language": bank[i]["language"],
                    "category": bank[i].get("category", ""),
                    "production_status": label(b), "latest_status": label(l),
                    "prevcandidate_status": label(p) if p else "",
                    "production_total": total(b), "latest_total": total(l),
                    "production_top5": b.get("top5_titles", ""), "latest_top5": l.get("top5_titles", ""),
                    "severity": sev, "new_zero_result": new_zero})
print(f"wrote 08_REGRESSIONS.csv ({len(reg_prod)} rows)")

# ---------- 09 zero/low result analysis ----------
new_zero_vs_prod = [i for i in range(n) if base.get(i) and latest.get(i) and not zero(base[i]) and zero(latest[i])]
recovered_zero_vs_prod = [i for i in range(n) if base.get(i) and latest.get(i) and zero(base[i]) and not zero(latest[i])]
new_zero_vs_prev = [i for i in range(n) if prev.get(i) and latest.get(i) and not zero(prev[i]) and zero(latest[i])]
recovered_zero_vs_prev = [i for i in range(n) if prev.get(i) and latest.get(i) and zero(prev[i]) and not zero(latest[i])]
new_low_vs_prod = [i for i in range(n) if base.get(i) and latest.get(i) and not low(base[i]) and low(latest[i])]
resolved_low_vs_prod = [i for i in range(n) if base.get(i) and latest.get(i) and low(base[i]) and not low(latest[i])]

with open(f"{OUT}/09_ZERO_LOW_RESULT_ANALYSIS.csv", "w", newline="", encoding="utf-8") as f:
    cols = ["row_index", "query", "language", "category", "production_total", "prevcandidate_total", "latest_total",
            "production_zero", "prevcandidate_zero", "latest_zero", "production_low", "prevcandidate_low", "latest_low",
            "transition_zero_vs_production", "transition_zero_vs_prevcandidate"]
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for i in range(n):
        b = base.get(i); p = prev.get(i); l = latest.get(i)
        if not (b and p and l): continue
        tz_prod = "NEW_ZERO" if (not zero(b) and zero(l)) else ("RECOVERED" if (zero(b) and not zero(l)) else ("STILL_ZERO" if zero(b) and zero(l) else "NEVER_ZERO"))
        tz_prev = "NEW_ZERO" if (not zero(p) and zero(l)) else ("RECOVERED" if (zero(p) and not zero(l)) else ("STILL_ZERO" if zero(p) and zero(l) else "NEVER_ZERO"))
        w.writerow({"row_index": i, "query": bank[i]["query"], "language": bank[i]["language"],
                    "category": bank[i].get("category", ""),
                    "production_total": total(b), "prevcandidate_total": total(p), "latest_total": total(l),
                    "production_zero": zero(b), "prevcandidate_zero": zero(p), "latest_zero": zero(l),
                    "production_low": low(b), "prevcandidate_low": low(p), "latest_low": low(l),
                    "transition_zero_vs_production": tz_prod, "transition_zero_vs_prevcandidate": tz_prev})
print("wrote 09_ZERO_LOW_RESULT_ANALYSIS.csv")

# ---------- 10 vertical/category summary ----------
categories = sorted(set(b.get("category", "") for b in bank))
vert_rows = []
for cat in categories:
    idxs = [i for i in range(n) if bank[i].get("category", "") == cat]
    l_rows = [latest[i] for i in idxs if latest.get(i)]
    b_rows = [base[i] for i in idxs if base.get(i)]
    p_rows = [prev[i] for i in idxs if prev.get(i)]
    c = Counter(label(r) for r in l_rows)
    z = sum(1 for r in l_rows if zero(r))
    lo = sum(1 for r in l_rows if low(r))
    passn = c.get("PASS", 0)
    total_q = len(idxs)
    imp_prod_cat = sum(1 for i in idxs if i in imp_prod)
    reg_prod_cat = sum(1 for i in idxs if i in reg_prod)
    imp_prev_cat = sum(1 for i in idxs if i in imp_prevcand)
    reg_prev_cat = sum(1 for i in idxs if i in reg_prevcand)
    vert_rows.append({
        "category": cat, "query_count": total_q,
        "PASS": passn, "PARTIAL": c.get("PARTIAL", 0), "FAIL": c.get("FAIL", 0), "UNJUDGABLE": c.get("UNJUDGABLE", 0),
        "pass_rate": round(passn / total_q, 3) if total_q else 0,
        "zero_result": z, "low_result": lo,
        "improvements_vs_production": imp_prod_cat, "regressions_vs_production": reg_prod_cat,
        "improvements_vs_prevcandidate": imp_prev_cat, "regressions_vs_prevcandidate": reg_prev_cat,
    })
vert_rows.sort(key=lambda r: -r["query_count"])
with open(f"{OUT}/10_VERTICAL_SUMMARY.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(vert_rows[0].keys())); w.writeheader()
    for r in vert_rows: w.writerow(r)
print("wrote 10_VERTICAL_SUMMARY.csv")

# ---------- 13 aggregate comparison ----------
with open(f"{OUT}/13_AGGREGATE_COMPARISON.csv", "w", newline="", encoding="utf-8") as f:
    cols = ["role", "commit", "total_queries", "PASS", "PARTIAL", "FAIL", "UNJUDGABLE", "pass_rate",
            "zero_result", "low_result", "mean_result_count", "median_result_count",
            "improvements_vs_this_row", "regressions_vs_this_row"]
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    w.writerow({"role": "production_baseline", "commit": "c550856e", "total_queries": base_d["n"],
                "PASS": base_d["PASS"], "PARTIAL": base_d["PARTIAL"], "FAIL": base_d["FAIL"], "UNJUDGABLE": base_d["UNJUDGABLE"],
                "pass_rate": round(base_d["PASS"] / base_d["n"], 3), "zero_result": base_d["zero"], "low_result": base_d["low"],
                "mean_result_count": round(base_d["mean_total"], 2), "median_result_count": base_d["median_total"],
                "improvements_vs_this_row": len(imp_prod), "regressions_vs_this_row": len(reg_prod)})
    w.writerow({"role": "previous_candidate", "commit": "1e56e3f0", "total_queries": prev_d["n"],
                "PASS": prev_d["PASS"], "PARTIAL": prev_d["PARTIAL"], "FAIL": prev_d["FAIL"], "UNJUDGABLE": prev_d["UNJUDGABLE"],
                "pass_rate": round(prev_d["PASS"] / prev_d["n"], 3), "zero_result": prev_d["zero"], "low_result": prev_d["low"],
                "mean_result_count": round(prev_d["mean_total"], 2), "median_result_count": prev_d["median_total"],
                "improvements_vs_this_row": len(imp_prevcand), "regressions_vs_this_row": len(reg_prevcand)})
    w.writerow({"role": "latest_candidate", "commit": "0e794cd9", "total_queries": latest_d["n"],
                "PASS": latest_d["PASS"], "PARTIAL": latest_d["PARTIAL"], "FAIL": latest_d["FAIL"], "UNJUDGABLE": latest_d["UNJUDGABLE"],
                "pass_rate": round(latest_d["PASS"] / latest_d["n"], 3), "zero_result": latest_d["zero"], "low_result": latest_d["low"],
                "mean_result_count": round(latest_d["mean_total"], 2), "median_result_count": latest_d["median_total"],
                "improvements_vs_this_row": "N/A (this is the latest row)", "regressions_vs_this_row": "N/A"})
print("wrote 13_AGGREGATE_COMPARISON.csv")

# save summary blob for report-writing
summary = {
    "base": base_d, "prev": prev_d, "latest": latest_d,
    "improved_vs_prod": len(imp_prod), "regressed_vs_prod": len(reg_prod), "unchanged_vs_prod": unch_prod,
    "improved_vs_prevcand": len(imp_prevcand), "regressed_vs_prevcand": len(reg_prevcand), "unchanged_vs_prevcand": unch_prevcand,
    "trans_prod": {f"{k[0]}->{k[1]}": v for k, v in trans_prod.items()},
    "trans_prevcand": {f"{k[0]}->{k[1]}": v for k, v in trans_prevcand.items()},
    "new_zero_vs_prod": [bank[i]["query"] for i in new_zero_vs_prod],
    "recovered_zero_vs_prod": [bank[i]["query"] for i in recovered_zero_vs_prod],
    "new_zero_vs_prev": [bank[i]["query"] for i in new_zero_vs_prev],
    "recovered_zero_vs_prev": [bank[i]["query"] for i in recovered_zero_vs_prev],
    "new_low_vs_prod": [bank[i]["query"] for i in new_low_vs_prod],
    "resolved_low_vs_prod": [bank[i]["query"] for i in resolved_low_vs_prod],
}
with open(f"{OUT}/scripts/summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print("wrote scripts/summary.json")
print("\nDONE")
