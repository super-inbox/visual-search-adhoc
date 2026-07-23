import csv

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22"

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

rows_out = []

def add(query, section, note, extra=""):
    rows_out.append({"section": section, "query": query, "note": note, "detail": extra})

# Major improvements (vs production)
imp = load(f"{OUT}/07_IMPROVEMENTS.csv")
imp_sorted = sorted(imp, key=lambda r: (r["production_status"], r["latest_status"]))
strong_imp = [r for r in imp if r["production_status"] == "FAIL" and r["latest_status"] == "PASS"]
for r in strong_imp[:8]:
    add(r["query"], "MAJOR_IMPROVEMENT", f"{r['production_status']}->{r['latest_status']} vs production", r["category"])

# Major regressions
reg = load(f"{OUT}/08_REGRESSIONS.csv")
strong_reg = [r for r in reg if r["severity"] == "HIGH"]
for r in strong_reg[:10]:
    add(r["query"], "MAJOR_REGRESSION", f"{r['production_status']}->{r['latest_status']} vs production, severity={r['severity']}", r["category"])

# Cluster A/B representative cases
cab = load(f"{OUT}/11_CLUSTER_AB_REPRESENTATIVE_CASES.csv")
for r in cab:
    add(r["query"], f"CLUSTER_{r['cluster']}", r["fix_outcome"], f"{r['production_status']}->{r['prevcandidate_status']}->{r['latest_status']}")

# Unresolved content gaps (catalog_content_gap root cause)
rc = load(f"{OUT}/12_REMAINING_FAILURE_ROOT_CAUSES.csv")
gaps = [r for r in rc if r["root_cause_category"] == "catalog_content_gap"]
for r in gaps[:10]:
    add(r["query"], "CONTENT_GAP", "zero-result across production/previous-candidate/latest -- likely missing catalog content", r["category"])

# Newly introduced risks
newrisk = [r for r in rc if r["root_cause_category"] == "candidate_loss_regression"]
for r in newrisk:
    add(r["query"], "NEW_RISK", "NEW zero-result regression introduced somewhere in the retrieval/filter chain (not pre-existing)", r["category"])

with open(f"{OUT}/14_KEY_CASES_FOR_MANAGER_REVIEW.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["section", "query", "note", "detail"])
    w.writeheader()
    for r in rows_out:
        w.writerow(r)
print(f"wrote {len(rows_out)} key-case rows")
