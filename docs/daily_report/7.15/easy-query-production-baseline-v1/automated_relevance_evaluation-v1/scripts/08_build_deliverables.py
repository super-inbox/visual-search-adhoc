#!/usr/bin/env python3
"""Build all final/ deliverables from checkpoints/master_query_level_final.csv and
master_result_level_final.jsonl. Read-only w.r.t. those inputs; writes only into final/
and summaries/."""
import csv, json, os, statistics, datetime, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
FINAL = os.path.join(OUT, "final")
SUMM = os.path.join(OUT, "summaries")
os.makedirs(FINAL, exist_ok=True)
os.makedirs(SUMM, exist_ok=True)
NOW = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def load():
    q = []
    with open(os.path.join(OUT, "checkpoints", "master_query_level_final.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            q.append(r)
    q.sort(key=lambda r: int(r["query_index"]))
    r_all = []
    with open(os.path.join(OUT, "checkpoints", "master_result_level_final.jsonl"), encoding="utf-8") as f:
        for line in f:
            r_all.append(json.loads(line))
    return q, r_all


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0


def main():
    q, r_all = load()
    assert len(q) == 328, len(q)
    qfields = list(q[0].keys())

    # ---------- 1/2: full query-level results ----------
    write_csv(os.path.join(FINAL, "automated_relevance_query_level_results.csv"), q, qfields)
    write_jsonl(os.path.join(FINAL, "automated_relevance_query_level_results.jsonl"), q)

    # ---------- 3/4: full result-level results ----------
    rfields = list(r_all[0].keys()) if r_all else []
    write_csv(os.path.join(FINAL, "automated_relevance_result_level_results.csv"), r_all, rfields)
    write_jsonl(os.path.join(FINAL, "automated_relevance_result_level_results.jsonl"), r_all)

    # ---------- label buckets ----------
    by_label = {"PASS": [], "PARTIAL": [], "FAIL": [], "UNJUDGABLE": []}
    for row in q:
        by_label.setdefault(row["query_relevance_label"], []).append(row)

    write_csv(os.path.join(FINAL, "automated_relevance_pass_queries.csv"), by_label["PASS"], qfields)
    write_csv(os.path.join(FINAL, "automated_relevance_partial_queries.csv"), by_label["PARTIAL"], qfields)
    write_csv(os.path.join(FINAL, "automated_relevance_fail_queries.csv"), by_label["FAIL"], qfields)
    write_csv(os.path.join(FINAL, "automated_relevance_unjudgable_queries.csv"), by_label["UNJUDGABLE"], qfields)

    low_conf = [r for r in q if r["relevance_confidence"] == "LOW"]
    write_csv(os.path.join(FINAL, "automated_relevance_low_confidence_queries.csv"), low_conf, qfields)

    drift_cases = [r for r in q if r["semantic_drift"] in ("MODERATE", "SEVERE")]
    write_csv(os.path.join(FINAL, "automated_relevance_semantic_drift_cases.csv"), drift_cases, qfields)

    rewrite_cases = [r for r in q if r["rewrite_observed"] == "True"]
    write_csv(os.path.join(FINAL, "automated_relevance_rewrite_cases.csv"), rewrite_cases, qfields)

    # ---------- manual review queue (priority P0/P1/P2) ----------
    def priority(row):
        label = row["query_relevance_label"]
        drift = row["semantic_drift"]
        conf = row["relevance_confidence"]
        jc = int(row["judgeable_result_count"] or 0)
        zero = row["zero_result"] == "True"
        reasons = []
        p0 = False
        if label == "UNJUDGABLE":
            p0 = True; reasons.append("UNJUDGABLE")
        if row.get("notes", "").find("SECOND-PASS ADJUDICATED") >= 0 and row["query_index"] in FLIPPED_SET:
            p0 = True; reasons.append("two-pass label disagreement (adjudicated)")
        if drift == "SEVERE":
            p0 = True; reasons.append("semantic_drift=SEVERE")
        if zero and label != "FAIL":
            p0 = True; reasons.append("zero_result data contradiction")
        if p0:
            return "P0", "; ".join(reasons) or "flagged for P0"
        p1 = False
        if label == "FAIL":
            p1 = True; reasons.append("FAIL")
        if label == "PARTIAL" and conf == "LOW":
            p1 = True; reasons.append("PARTIAL + LOW confidence")
        if row.get("ambiguity_level") == "HIGH":
            reasons.append("high ambiguity")
        if jc < 3 and not zero:
            p1 = True; reasons.append("judgeable_result_count<3")
        if p1:
            return "P1", "; ".join(reasons) or "flagged for P1"
        p2 = False
        if label == "PASS" and row["rewrite_observed"] == "True":
            p2 = True; reasons.append("PASS but rewrite/broaden triggered")
        if row["needs_manual_review"] == "True":
            p2 = True; reasons.append("needs_manual_review flag set")
        if p2:
            return "P2", "; ".join(reasons) or "flagged for P2"
        return None, None

    FLIPPED_SET = {"226", "233", "245", "269"}
    queue_rows = []
    for row in q:
        pri, reason = priority(row)
        if pri:
            queue_rows.append({
                "priority": pri, "query_index": row["query_index"], "original_query": row["original_query"],
                "first_label": "", "second_label": "", "final_label": row["query_relevance_label"],
                "relevance_score": row["relevance_score"], "confidence": row["relevance_confidence"],
                "semantic_drift": row["semantic_drift"], "rewrite_observed": row["rewrite_observed"],
                "reason_for_review": reason, "screenshot_path": row["screenshot_path"],
                "evidence_summary": row["evidence_summary"],
            })
    # backfill first/second label for the tier1/tier3-reviewed queries from second_pass_review.csv
    review_lookup = {}
    with open(os.path.join(OUT, "review", "second_pass_review.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            review_lookup[r["query_index"]] = (r["first_label"], r["second_label"])
    for row in queue_rows:
        if row["query_index"] in review_lookup:
            row["first_label"], row["second_label"] = review_lookup[row["query_index"]]

    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    queue_rows.sort(key=lambda r: (priority_order[r["priority"]], -float(r["relevance_score"] or 0)))
    queue_fields = ["priority", "query_index", "original_query", "first_label", "second_label", "final_label",
                     "relevance_score", "confidence", "semantic_drift", "rewrite_observed", "reason_for_review",
                     "screenshot_path", "evidence_summary"]
    write_csv(os.path.join(FINAL, "automated_relevance_manual_review_queue.csv"), queue_rows, queue_fields)
    write_csv(os.path.join(OUT, "review", "automated_relevance_manual_review_queue.csv"), queue_rows, queue_fields)

    # ---------- summary stats ----------
    scores = [float(r["relevance_score"]) for r in q if r["relevance_score"] not in ("", None, "None")]
    top5_rates = [float(r["top5_weighted_relevance"]) for r in q if r["top5_weighted_relevance"] not in ("", None, "None")]

    def label_dist(rows):
        d = {}
        for r in rows:
            d[r["query_relevance_label"]] = d.get(r["query_relevance_label"], 0) + 1
        return d

    conf_dist = {}
    for r in q:
        conf_dist[r["relevance_confidence"]] = conf_dist.get(r["relevance_confidence"], 0) + 1

    drift_dist = {}
    for r in q:
        drift_dist[r["semantic_drift"]] = drift_dist.get(r["semantic_drift"], 0) + 1

    intent_dist = {}
    for r in q:
        intent_dist[r["original_intent_preserved"]] = intent_dist.get(r["original_intent_preserved"], 0) + 1

    lang_dist = {}
    for r in q:
        lang_dist.setdefault(r["detected_language"], []).append(r["query_relevance_label"])
    lang_summary = {k: label_dist([{"query_relevance_label": x} for x in v]) for k, v in lang_dist.items()}

    cat_dist = {}
    for r in q:
        cat_dist.setdefault(r["category"], []).append(r["query_relevance_label"])
    cat_summary = {k: label_dist([{"query_relevance_label": x} for x in v]) for k, v in cat_dist.items()}

    qtype_dist = {}
    for r in q:
        qtype_dist.setdefault(r["query_type"], []).append(r["query_relevance_label"])
    qtype_summary = {k: label_dist([{"query_relevance_label": x} for x in v]) for k, v in qtype_dist.items()}

    def bucket_result_count(n):
        n = int(n)
        if n == 0: return "0"
        if n <= 2: return "1-2"
        if n <= 4: return "3-4"
        return "5+"
    bucket_dist = {}
    for r in q:
        b = bucket_result_count(r["visible_result_count"] or 0)
        bucket_dist.setdefault(b, []).append(r["query_relevance_label"])
    bucket_summary = {k: label_dist([{"query_relevance_label": x} for x in v]) for k, v in bucket_dist.items()}

    fail_reason_dist = {}
    for r in q:
        if r["query_relevance_label"] in ("FAIL", "PARTIAL"):
            fr = r["primary_failure_reason"] or "NONE"
            fail_reason_dist[fr] = fail_reason_dist.get(fr, 0) + 1

    rewrite_yes = [r for r in q if r["rewrite_observed"] == "True"]
    rewrite_no = [r for r in q if r["rewrite_observed"] != "True"]

    worst = sorted([r for r in q if r["relevance_score"] not in ("", None, "None")],
                    key=lambda r: float(r["relevance_score"]))[:20]
    best = sorted([r for r in q if r["relevance_score"] not in ("", None, "None")],
                   key=lambda r: -float(r["relevance_score"]))[:20]

    needs_review_count = sum(1 for r in q if r["needs_manual_review"] == "True")
    zero_count = sum(1 for r in q if r["zero_result"] == "True")
    low_count = sum(1 for r in q if r["low_result"] == "True")

    # calibration + second-pass agreement rates (pulled from existing artifacts)
    calib = json.load(open(os.path.join(OUT, "checkpoints", "calibration_comparison.json"), encoding="utf-8"))
    with open(os.path.join(OUT, "review", "second_pass_review.csv"), newline="", encoding="utf-8") as f:
        sp_rows = list(csv.DictReader(f))
    sp_agree = sum(1 for r in sp_rows if r["agreement"] == "True")
    sp_total = len(sp_rows)

    summary = {
        "run_id": "curify-easy-query-automated-relevance-eval-2026-07-15-16",
        "generated_at": NOW,
        "total_queries": len(q),
        "completed_queries": len(q),
        "label_distribution": label_dist(q),
        "label_pct": {k: pct(v, len(q)) for k, v in label_dist(q).items()},
        "relevance_score_mean": round(statistics.mean(scores), 2) if scores else None,
        "relevance_score_median": round(statistics.median(scores), 2) if scores else None,
        "relevance_score_p25": round(sorted(scores)[int(len(scores) * 0.25)], 2) if scores else None,
        "relevance_score_p75": round(sorted(scores)[int(len(scores) * 0.75)], 2) if scores else None,
        "top5_weighted_relevance_mean": round(statistics.mean(top5_rates), 4) if top5_rates else None,
        "confidence_distribution": conf_dist,
        "needs_manual_review_count": needs_review_count,
        "zero_result_count": zero_count,
        "low_result_count": low_count,
        "rewrite_observed_count": len(rewrite_yes),
        "rewrite_label_distribution": label_dist(rewrite_yes),
        "non_rewrite_label_distribution": label_dist(rewrite_no),
        "semantic_drift_distribution": drift_dist,
        "original_intent_preserved_distribution": intent_dist,
        "by_language": lang_summary,
        "by_category": cat_summary,
        "by_query_type": qtype_summary,
        "by_result_count_bucket_NOTE": "bucket computed from visible_result_count (saved Top Results count), not a site-wide total (not available/reliable to claim)",
        "by_result_count_bucket": bucket_summary,
        "primary_failure_reason_distribution": fail_reason_dist,
        "top20_worst_queries": [{"query_index": r["query_index"], "original_query": r["original_query"],
                                  "label": r["query_relevance_label"], "score": r["relevance_score"]} for r in worst],
        "top20_best_queries": [{"query_index": r["query_index"], "original_query": r["original_query"],
                                 "label": r["query_relevance_label"], "score": r["relevance_score"]} for r in best],
        "calibration_agreement_rate": calib["label_agreement_rate"],
        "calibration_avg_abs_score_diff": calib["avg_abs_score_diff"],
        "second_pass_tier1_tier3_reviewed": sp_total,
        "second_pass_agreement_count": sp_agree,
        "second_pass_agreement_rate_pct": pct(sp_agree, sp_total),
        "second_pass_label_flips": 4,
        "rubric_version": "rubric-v1.1",
        "evaluator_version_first_pass": "claude-code-sonnet-5-rubric-v1.1",
        "evaluator_version_second_pass": "claude-code-sonnet-5-rubric-v1.1-secondpass",
    }
    with open(os.path.join(FINAL, "automated_relevance_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # ---------- summary.md (short human-readable) ----------
    md = []
    md.append("# automated_relevance_summary.md\n")
    md.append(f"Generated: {NOW}\n")
    md.append(f"\nTotal queries: {len(q)} (328/328 evaluated)\n")
    md.append("\n## Label distribution\n")
    for k in ("PASS", "PARTIAL", "FAIL", "UNJUDGABLE"):
        n = label_dist(q).get(k, 0)
        md.append(f"- {k}: {n} ({pct(n, len(q))}%)\n")
    md.append(f"\nMean relevance_score: {summary['relevance_score_mean']} | Median: {summary['relevance_score_median']} "
               f"| P25: {summary['relevance_score_p25']} | P75: {summary['relevance_score_p75']}\n")
    md.append(f"\nConfidence: {conf_dist}\n")
    md.append(f"\nneeds_manual_review: {needs_review_count} | zero_result: {zero_count} | low_result: {low_count}\n")
    md.append(f"\nRewrite observed: {len(rewrite_yes)} -> {label_dist(rewrite_yes)}\n")
    md.append(f"Non-rewrite: {len(rewrite_no)} -> {label_dist(rewrite_no)}\n")
    md.append(f"\nCalibration label agreement: {calib['label_agreement_rate']*100:.1f}% (30/30 queries)\n")
    md.append(f"Second-pass (tier1 deep-reverify 54 + tier3 random-PASS-audit 10 = {sp_total}) label agreement: "
               f"{pct(sp_agree, sp_total)}% ({sp_agree}/{sp_total}); 4 label flips (all PASS->PARTIAL) after adjudication.\n")
    with open(os.path.join(FINAL, "automated_relevance_summary.md"), "w", encoding="utf-8") as f:
        f.write("".join(md))

    # ---------- rewrite analysis ----------
    rw_rows = []
    for r in rewrite_yes:
        rw_rows.append({
            "query_index": r["query_index"], "original_query": r["original_query"],
            "broadened_query": r["broadened_query"], "original_intent_preserved": r["original_intent_preserved"],
            "semantic_drift": r["semantic_drift"], "drift_reason": r["evidence_summary"][:200],
            "query_relevance_label": r["query_relevance_label"], "relevance_score": r["relevance_score"],
            "relevant_count": r["relevant_count"], "irrelevant_count": r["irrelevant_count"],
            "before_rewrite_evidence_available": "False",
            "needs_manual_review": r["needs_manual_review"],
        })
    write_csv(os.path.join(SUMM, "rewrite_relevance_analysis.csv"), rw_rows, list(rw_rows[0].keys()) if rw_rows else
              ["query_index","original_query","broadened_query","original_intent_preserved","semantic_drift",
               "drift_reason","query_relevance_label","relevance_score","relevant_count","irrelevant_count",
               "before_rewrite_evidence_available","needs_manual_review"])

    rw_label = label_dist(rewrite_yes)
    rw_drift = {}
    for r in rewrite_yes:
        rw_drift[r["semantic_drift"]] = rw_drift.get(r["semantic_drift"], 0) + 1
    rw_intent_yes = sum(1 for r in rewrite_yes if r["original_intent_preserved"] == "YES")
    rw_scores = [float(r["relevance_score"]) for r in rewrite_yes if r["relevance_score"] not in ("", None, "None")]
    nonrw_scores = [float(r["relevance_score"]) for r in rewrite_no if r["relevance_score"] not in ("", None, "None")]

    with open(os.path.join(SUMM, "rewrite_relevance_summary.md"), "w", encoding="utf-8") as f:
        f.write(f"""# rewrite_relevance_summary.md

Generated: {NOW}

## Scope

{len(rewrite_yes)} of 328 queries had `rewrite_observed=True` (production's own broaden/rewrite mechanism fired).
Per RUN_MANIFEST/INPUT_AUDIT this was recorded as 138 in the baseline collection; the automated-relevance
pass finds {len(rewrite_yes)} rows still flagged `rewrite_observed=True` in the final adjudicated dataset
(no discrepancy expected -- rewrite_observed is a collection-time production-behavior flag untouched by
relevance judging, so this equals the original collection's count unless noted otherwise below).

## 1-4. Label distribution among rewrite queries

- PASS: {rw_label.get('PASS',0)} ({pct(rw_label.get('PASS',0), len(rewrite_yes))}%)
- PARTIAL: {rw_label.get('PARTIAL',0)} ({pct(rw_label.get('PARTIAL',0), len(rewrite_yes))}%)
- FAIL: {rw_label.get('FAIL',0)} ({pct(rw_label.get('FAIL',0), len(rewrite_yes))}%)
- UNJUDGABLE: {rw_label.get('UNJUDGABLE',0)} ({pct(rw_label.get('UNJUDGABLE',0), len(rewrite_yes))}%)

## 5. Semantic drift among rewrite queries

{json.dumps(rw_drift, ensure_ascii=False)}
MODERATE+SEVERE: {rw_drift.get('MODERATE',0)+rw_drift.get('SEVERE',0)} of {len(rewrite_yes)} ({pct(rw_drift.get('MODERATE',0)+rw_drift.get('SEVERE',0), len(rewrite_yes))}%)

## 6. Intent preservation

original_intent_preserved=YES: {rw_intent_yes} of {len(rewrite_yes)} ({pct(rw_intent_yes, len(rewrite_yes))}%)

## 7. Rewrite queries introducing clear off-topic drift

See `automated_relevance_semantic_drift_cases.csv` intersected with rewrite_observed=True, and the FAIL-label
rewrite rows in this file. Representative confirmed-drift cases from this run's second-pass review: E017 地球仪
(desk-globe -> generic country maps), E019 镜子 (mirror -> unrelated heritage/solar-term posters, SEVERE drift,
confirmed via screenshot during calibration), E245 宝妈 (mom-life -> noise-template + unrelated gardening/park
content, MODERATE drift, label flipped PASS->PARTIAL on adjudication), E269 冬至 (winter solstice -> a different
holiday (Christmas) and a wrong-season solar term, MODERATE drift, label flipped PASS->PARTIAL).

## 8. Most common failure modes in rewrite queries

{json.dumps(fail_reason_dist, ensure_ascii=False)}
(counted across FAIL+PARTIAL queries corpus-wide; see automated_relevance_fail_queries.csv /
automated_relevance_partial_queries.csv filtered to rewrite_observed=True for the rewrite-only subset)

## 9. Queries best illustrating the case for a Rewrite Guard

E019 镜子 (SEVERE drift, 0 relevant results despite a mirror-specific rewrite), E245 宝妈 and E269 冬至
(MODERATE drift pulling in off-topic noise-template/wrong-holiday content that downgraded an
otherwise-workable query from PASS to PARTIAL), and the recurring 'dual-character-comparison-infographic'
noise-template pattern documented in CALIBRATION_REPORT.md finding #5, which surfaces via the
*non-rewrite* retrieval path across multiple unrelated object queries (cat/dog/book) as well as inside
rewritten queries like E245 -- indicating the noise is a retrieval-ranking issue, not purely a rewrite
issue, and a Rewrite Guard alone would not fully fix it.

## 10. Cases where rewrite improved results

Several object queries with literal near-zero direct catalog matches were meaningfully rescued by broadening,
e.g. E020 花瓶 (vase; rewrite surfaced a directly on-topic 'Ming vase' result, low_result=True but final PASS),
E297 香薰机 (diffuser; rewrite matched the exact product template, PASS), E304 婴儿用品 (baby products; rewrite
matched an exact-title template, PASS) -- all originally low_result queries where the broadened terms produced
a small but genuinely relevant result set rather than expanding into noise. This is disclosed evidence-based,
not an assumption that rewrite is uniformly helpful or harmful: mean relevance_score for rewrite queries is
{round(statistics.mean(rw_scores),1) if rw_scores else 'N/A'} vs {round(statistics.mean(nonrw_scores),1) if nonrw_scores else 'N/A'} for
non-rewrite queries in this run -- rewrite queries score somewhat lower on average, consistent with rewrite
generally firing on harder/sparser queries to begin with (selection effect), not proof that rewriting itself
causes harm on a per-query basis.
""")

    # ---------- zero/low result analysis ----------
    zero_rows = [r for r in q if r["zero_result"] == "True"]
    write_csv(os.path.join(SUMM, "zero_result_relevance_analysis.csv"),
              [{"query_index": r["query_index"], "original_query": r["original_query"], "category": r["category"],
                "query_relevance_label": r["query_relevance_label"], "relevance_score": r["relevance_score"],
                "primary_failure_reason": r["primary_failure_reason"], "needs_manual_review": r["needs_manual_review"]}
               for r in zero_rows],
              ["query_index", "original_query", "category", "query_relevance_label", "relevance_score",
               "primary_failure_reason", "needs_manual_review"])

    low_rows = [r for r in q if r["low_result"] == "True"]
    write_csv(os.path.join(SUMM, "low_result_relevance_analysis.csv"),
              [{"query_index": r["query_index"], "original_query": r["original_query"], "category": r["category"],
                "visible_result_count": r["visible_result_count"], "judgeable_result_count": r["judgeable_result_count"],
                "query_relevance_label": r["query_relevance_label"], "relevance_score": r["relevance_score"],
                "relevance_confidence": r["relevance_confidence"], "needs_manual_review": r["needs_manual_review"]}
               for r in low_rows],
              ["query_index", "original_query", "category", "visible_result_count", "judgeable_result_count",
               "query_relevance_label", "relevance_score", "relevance_confidence", "needs_manual_review"])

    print("zero_result:", len(zero_rows), "all FAIL:", all(r["query_relevance_label"] == "FAIL" for r in zero_rows))
    print("low_result:", len(low_rows), "label dist:", label_dist(low_rows))
    print("manual review queue:", len(queue_rows), "P0:", sum(1 for r in queue_rows if r["priority"]=="P0"),
          "P1:", sum(1 for r in queue_rows if r["priority"]=="P1"), "P2:", sum(1 for r in queue_rows if r["priority"]=="P2"))
    print("summary written. label_dist:", label_dist(q))


if __name__ == "__main__":
    main()
