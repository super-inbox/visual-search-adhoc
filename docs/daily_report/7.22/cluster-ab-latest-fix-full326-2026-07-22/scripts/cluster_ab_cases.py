import csv

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22"
BANK = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv"

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {int(r["row_index"]): r for r in csv.DictReader(f)}

with open(BANK, encoding="utf-8") as f:
    bank = list(csv.DictReader(f))
qidx = {b["query"]: i for i, b in enumerate(bank)}

base = load("/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/eval_raw/BASELINE_EASY326.csv")
prev = load("/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/eval_raw/CANDIDATE_EASY326.csv")
latest = load(f"{OUT}/eval_raw/CANDIDATE_LATEST_EASY326.csv")

# (query, cluster, expected_fix_outcome_per_docs)
cases = [
    ("wine label", "A", "fixed"),
    ("酒标", "A", "unresolved"),
    ("字母海报", "A", "unresolved"),
    ("巧克力礼盒", "A", "unresolved"),
    ("人体图解", "A", "partially_recovered"),
    ("coffee package", "A-adjacent", "fixed"),
    ("coffee bean package", "A-adjacent", "unresolved"),
    ("cosmetic package", "A-adjacent", "partially_recovered"),
    ("black friday banner", "A-known-gap", "unresolved (disclosed follow-up, not in this fix's scope)"),
    ("笔袋", "B", "unresolved (flagship, still worse than production)"),
    ("pencil case", "B", "unresolved (still worse than production)"),
    ("挂件", "B", "fixed (recovered to production PASS level)"),
    ("娃娃", "B", "unresolved"),
    ("泰迪熊", "B", "unresolved"),
    ("单词卡", "B", "unresolved"),
    ("积分卡", "B-related (new-zero from 7/21)", "fixed (recovered from zero)"),
    ("会员卡", "B-related (new-zero from 7/21)", "unresolved (still zero)"),
]

rows = []
for query, cluster, expected in cases:
    if query not in qidx:
        continue
    i = qidx[query]
    b, p, l = base.get(i), prev.get(i), latest.get(i)
    rows.append({
        "row_index": i, "query": query, "cluster": cluster,
        "production_status": b["relevance_label"] if b else "",
        "prevcandidate_status": p["relevance_label"] if p else "",
        "latest_status": l["relevance_label"] if l else "",
        "production_total": b["total_results"] if b else "",
        "prevcandidate_total": p["total_results"] if p else "",
        "latest_total": l["total_results"] if l else "",
        "production_top5": b["top5_titles"] if b else "",
        "prevcandidate_top5": p["top5_titles"] if p else "",
        "latest_top5": l["top5_titles"] if l else "",
        "fix_outcome": expected,
    })

with open(f"{OUT}/11_CLUSTER_AB_REPRESENTATIVE_CASES.csv", "w", newline="", encoding="utf-8") as f:
    cols = list(rows[0].keys())
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"wrote {len(rows)} representative case rows")
