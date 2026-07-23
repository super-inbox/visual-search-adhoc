import csv
import json
from collections import Counter

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22"
BANK = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv"
LATEST_CSV = f"{OUT}/eval_raw/CANDIDATE_LATEST_EASY326.csv"
BASE_CSV = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/eval_raw/BASELINE_EASY326.csv"
PREV_CSV = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.21/scorer-v1.1-evaluation-2026-07-21/eval_raw/CANDIDATE_EASY326.csv"

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {int(r["row_index"]): r for r in csv.DictReader(f)}

with open(BANK, encoding="utf-8") as f:
    bank = list(csv.DictReader(f))
latest = load(LATEST_CSV)
base = load(BASE_CSV)
prev = load(PREV_CSV)

FORMAT_TOKENS_CJK = ["海报", "横幅", "传单", "手册", "标签", "包装", "礼盒", "样机", "卡片", "模板", "封面", "壁纸", "图解", "图表", "图鉴", "名片", "单页", "排版", "缩略"]
FORMAT_TOKENS_EN = ["poster", "banner", "flyer", "brochure", "leaflet", "label", "package", "packaging",
                    "box", "mockup", "card", "flashcard", "sheet", "pack", "template", "cover", "wallpaper",
                    "infographic", "diagram", "photo", "thumbnail", "layout"]

def classify(i, l, b, p, bank_row):
    query = bank_row["query"]
    total = int(l["total_results"]) if l["total_results"] else 0
    zero = l["zero_result"] in ("True", "true")
    low = l["low_result"] in ("True", "true")
    rewrite = l["rewrite_triggered"] in ("True", "true")
    paths = l.get("paths_used", "")
    reason = l.get("primary_failure_reason", "")
    label = l["relevance_label"]

    if label == "UNJUDGABLE":
        return "evaluation_limitation", f"UNJUDGABLE ({reason}); no usable evidence for the judge to score, not a search-quality signal."

    if zero:
        b_zero = b and b["zero_result"] in ("True", "true")
        p_zero = p and p["zero_result"] in ("True", "true")
        if b_zero and p_zero:
            return "catalog_content_gap", "Zero results across production baseline, previous candidate, AND latest candidate -- persistent, not caused by this fix; likely no matching catalog content exists for this query concept."
        else:
            return "candidate_loss_regression", "Zero results in latest candidate where an earlier version returned results -- a NEW zero-result regression introduced somewhere in the retrieval/rewrite/filtering chain, not a pre-existing content gap."

    # multi-term head-noun+format shape (Cluster-A shape) still failing
    has_format_word = any(f in query.lower() for f in FORMAT_TOKENS_EN) or any(f in query for f in FORMAT_TOKENS_CJK)
    multi_term = len(query.split()) >= 2 or len(query) >= 4  # rough heuristic for CJK compounds too
    if label == "FAIL" and has_format_word and multi_term and total > 15:
        return "subject_binding_or_coverage_gap", "Query contains a format/output word (poster/label/package/海报/图解/礼盒 etc.) alongside a head-noun/theme; result pool is large but FAIL -- consistent with the Cluster-A mechanism (format word satisfies subject-presence and/or the coverage-ratio + isolated-hit-cap gates still demote the correct head-noun matches). Inference from result shape, not direct scorer instrumentation."

    if label == "FAIL" and low:
        return "candidate_loss", "Sparse result pool (1-4 results) that is still judged FAIL -- likely candidate loss upstream (retrieval/expansion not surfacing enough on-subject items), not merely a ranking problem."

    if label == "FAIL" and rewrite and total > 30:
        return "rewrite_or_decomposition_issue", "Rewrite/decomposition path was triggered and the pool is large but FAIL -- consistent with the rewrite path admitting off-subject non-original content (Cluster-B relaxed-expansion shape), or a genuine ambiguous/decomposed query."

    if label == "FAIL" and total > 30:
        return "retrieval_scoring_relevance_issue", "Large result pool but still judged FAIL -- off-subject/wrong-sense content is outranking on-subject content; a scoring/ranking issue rather than a candidate-availability issue."

    if label == "FAIL":
        return "insufficient_evidence", "FAIL with a small-to-moderate result pool and no single dominant signal (format word / low-result / rewrite) -- classification uncertain from row-level data alone; would need Top-5 manual read to confirm root cause."

    # PARTIAL cases only included if regressed vs production
    return "partial_regression_vs_production", "PARTIAL in latest candidate, was a better label in production baseline -- see 08_REGRESSIONS.csv for detail."


rows_out = []
for i in range(len(bank)):
    l = latest.get(i)
    if not l:
        continue
    label = l["relevance_label"]
    b = base.get(i)
    p = prev.get(i)
    include = False
    if label == "FAIL":
        include = True
    elif label == "PARTIAL":
        # "important PARTIAL" = regressed vs production (previously better)
        LABEL_RANK = {"FAIL": 0, "UNJUDGABLE": 1, "PARTIAL": 2, "PASS": 3}
        if b and LABEL_RANK.get(b["relevance_label"], -1) > LABEL_RANK.get(label, -1):
            include = True
    if not include:
        continue
    cat, explanation = classify(i, l, b, p, bank[i])
    rows_out.append({
        "row_index": i, "query": bank[i]["query"], "language": bank[i]["language"],
        "category": bank[i].get("category", ""), "latest_status": label,
        "production_status": b["relevance_label"] if b else "",
        "total_results": l["total_results"], "zero_result": l["zero_result"], "low_result": l["low_result"],
        "rewrite_triggered": l["rewrite_triggered"],
        "root_cause_category": cat, "explanation": explanation,
        "top5_titles": l.get("top5_titles", ""),
    })

with open(f"{OUT}/12_REMAINING_FAILURE_ROOT_CAUSES.csv", "w", newline="", encoding="utf-8") as f:
    cols = ["row_index", "query", "language", "category", "latest_status", "production_status",
            "total_results", "zero_result", "low_result", "rewrite_triggered",
            "root_cause_category", "explanation", "top5_titles"]
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows_out:
        w.writerow(r)

cause_counts = Counter(r["root_cause_category"] for r in rows_out)
print(f"total classified rows: {len(rows_out)}")
for k, v in cause_counts.most_common():
    print(f"  {k}: {v} ({100*v/len(rows_out):.1f}%)")

with open(f"{OUT}/scripts/root_cause_summary.json", "w", encoding="utf-8") as f:
    json.dump({"total": len(rows_out), "counts": dict(cause_counts)}, f, ensure_ascii=False, indent=2)
