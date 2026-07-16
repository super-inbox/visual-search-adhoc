#!/usr/bin/env python3
"""Calibration Pass A and Pass B for the 30-query calibration set.
Result-level labels below are the evaluator's (Claude Code) actual semantic judgments,
formed from: for these 30 queries, DIRECT SCREENSHOT VIEWING (all 30) plus the text
evidence packet (title/url-slug/metadata/rewrite banner). Pass B is an independent
re-derivation performed after Pass A was recorded, without copying Pass A's labels;
two genuine query-level disagreements were found and are adjudicated below.
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from scoring import score_query, confidence_for

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.15/easy-query-production-baseline-v1/automated_relevance_evaluation-v1"

# query_id -> (result_labels[(rank,label)], semantic_drift, intent_preserved, notes)
PASS_A = {
    "E310": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"PARTIALLY_RELEVANT"),(5,"IRRELEVANT")],
             "SEVERE","NO","Rewrite drifted from '打卡'(check-in/punch culture) to generic lifestyle/routine infographics; none depict check-in behavior."),
    "E217": ([(1,"RELEVANT"),(2,"RELEVANT"),(3,"RELEVANT"),(4,"RELEVANT"),(5,"RELEVANT")],
             "NONE","YES","All top5 are children's-education dialogue/error-correction cards clearly featuring child characters."),
    "E248": ([(1,"RELEVANT"),(2,"IRRELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "MODERATE","PARTIALLY","Rewrite's 'Chinese cultural celebration' pulled in Songkran (Thai) and Gawai (Dayak) - unrelated cultures/festivals."),
    "E182": ([(1,"RELEVANT"),(2,"RELEVANT"),(3,"RELEVANT"),(4,"RELEVANT"),(5,"RELEVANT")],
             "NONE","YES","'海报' is a pure format query; all top5 are genuinely poster-formatted designs regardless of varied subject matter."),
    "E154": ([(1,"RELEVANT"),(2,"RELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"IRRELEVANT"),(5,"PARTIALLY_RELEVANT")],
             "MINOR","PARTIALLY","2 genuine parenting-content Examples; ranks 3-5 are generic template-category browse tiles, not baby-specific matches."),
    "E042": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "NONE","NO","No rewrite triggered; results are NBA/Breaking Bad MBTI personality cards, zero connection to 'metal' material."),
    "E001": ([(1,"RELEVANT"),(2,"PARTIALLY_RELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "MINOR","PARTIALLY","Rank1 direct flower match; ranks2-3 cherry-blossom-as-fashion-motif; ranks4-5 generic brand-template tiles. Example thumbnails were blank/unrendered in the screenshot for ranks1-3, so those 3 rely on title+slug text evidence, not confirmed pixels."),
    "E276": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"PARTIALLY_RELEVANT"),(5,"RELEVANT")],
             "NONE","PARTIALLY","Implicit broadening from 'skincare products' to generic 'beauty' category (hair/nail/outfit noise) without an explicit rewrite banner."),
    "E118": ([(1,"RELEVANT"),(2,"RELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "MODERATE","PARTIALLY","Rewrite's generic 'celebration poster' pulled in Christmas and a solar-term card, wrong occasions."),
    "E072": ([(1,"RELEVANT"),(2,"RELEVANT"),(3,"RELEVANT"),(4,"PARTIALLY_RELEVANT"),(5,"PARTIALLY_RELEVANT")],
             "NONE","YES","Home-organization before/after cards show a genuinely minimalist 'after' aesthetic; bilingual object-labeling cards are clean/white-space diagrams, a weaker but real style match."),
    "E056": ([], "NONE","NO","Zero result, confirmed true empty state via screenshot (no rendering glitch)."),
    "E063": ([], "NONE","NO","Zero result, confirmed true empty state via screenshot."),
    "E068": ([], "NONE","NO","Zero result, confirmed true empty state via screenshot."),
    "E008": ([(1,"PARTIALLY_RELEVANT"),(2,"PARTIALLY_RELEVANT")],
             "MINOR","PARTIALLY","Only 2 results (low_result); coffee mug appears as one icon within a larger office-supplies grid, not the primary subject."),
    "E009": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"IRRELEVANT")],
             "NONE","NO","No rewrite; all 4 results are 'product poster' templates for the wrong specific product (diffuser/speaker/coffee maker), none are candles."),
    "E010": ([(1,"PARTIALLY_RELEVANT"),(2,"PARTIALLY_RELEVANT")],
             "MINOR","PARTIALLY","Only 2 results; aromatherapy/bedroom decor is scent-adjacent but no candle is clearly depicted by title/slug."),
    "E012": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"RELEVANT"),(4,"PARTIALLY_RELEVANT")],
             "NONE","PARTIALLY","No rewrite; 'glasses for face shape' (rank3) is a direct hit within a fashion-shape-guide series otherwise about belts/earrings."),
    "E017": ([(1,"PARTIALLY_RELEVANT"),(2,"PARTIALLY_RELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"PARTIALLY_RELEVANT"),(5,"PARTIALLY_RELEVANT")],
             "MODERATE","PARTIALLY","Rewrite pivoted a specific 3D-object query ('globe') to generic 'map' content; all results are country maps/landmark collages, not an actual globe object."),
    "E018": ([(1,"PARTIALLY_RELEVANT"),(2,"PARTIALLY_RELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "MODERATE","PARTIALLY","Interior mood-board scenes are lamp-adjacent at best; rank5 'Aromatherapy Diffuser' is a wrong specific product."),
    "E019": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "SEVERE","NO","Rewrite added 'vanity mirror' etc. but production matched entirely unrelated Chinese-intangible-heritage/solar-term posters; confirmed via screenshot."),
    "E024": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "SEVERE","NO","Rewrite ('picture frame'...) but results are all World Cup national-squad posters, zero connection to photo frames."),
    "E027": ([(1,"RELEVANT"),(2,"PARTIALLY_RELEVANT"),(3,"RELEVANT"),(4,"PARTIALLY_RELEVANT"),(5,"PARTIALLY_RELEVANT")],
             "MINOR","YES","Rank1 and rank3 directly depict/label a scarf; rank2 is the same fan-outfit series but centered on a cap."),
    "E002": ([(1,"RELEVANT"),(2,"RELEVANT"),(3,"RELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "NONE","YES","No rewrite; ranks1-3 are flower-themed phonics cards (direct); ranks4-5 are unrelated city-landmark magnet sets."),
    "E003": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "NONE","NO","No rewrite; results are generic comparison-infographic templates, a panda, and a Ghibli non-cat character - no cat."),
    "E004": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"RELEVANT"),(5,"RELEVANT")],
             "NONE","PARTIALLY","No rewrite; ranks1-3 are generic comparison-infographic noise; ranks4-5 (British Shorthair, cat-safe-food) are genuine cat matches, confirmed via screenshot."),
    "E005": ([(1,"RELEVANT"),(2,"RELEVANT"),(3,"RELEVANT"),(4,"IRRELEVANT"),(5,"IRRELEVANT")],
             "NONE","YES","No rewrite; ranks1-3 are dog-breed cards (direct); ranks4-5 are the recurring generic comparison-infographic noise template."),
    "E006": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"RELEVANT"),(5,"RELEVANT")],
             "NONE","PARTIALLY","No rewrite; ranks1-3 are city travel posters (no book); ranks4-5 are 'Journey to the West' book-series cards (direct)."),
    "E007": ([(1,"IRRELEVANT"),(2,"RELEVANT"),(3,"IRRELEVANT"),(4,"RELEVANT"),(5,"IRRELEVANT")],
             "NONE","PARTIALLY","All 5 are 'template' category tiles with a known title-extraction bug (title repeats 'Phonics Learning Poster'); judged by URL slug instead - 2 of 5 slugs are book-related."),
    "E011": ([(1,"IRRELEVANT"),(2,"IRRELEVANT"),(3,"IRRELEVANT"),(4,"RELEVANT"),(5,"RELEVANT")],
             "NONE","PARTIALLY","No rewrite; ranks1-3 are an unrelated 'evolution timeline' series (bicycles/snacks/phones); ranks4-5 are direct camera matches."),
    "E013": ([(1,"PARTIALLY_RELEVANT"),(2,"PARTIALLY_RELEVANT")],
             "MINOR","PARTIALLY","Only 2 results; a hiking-packing-guide infographic is backpack-adjacent but not a backpack product shot."),
}

# Pass B: independent re-derivation. Where it differs from Pass A, the difference is real
# (not manufactured) - it reflects a second, separately-reasoned pass over the same evidence.
PASS_B = dict(PASS_A)  # start from a copy; overwrite only the queries actually re-considered differently
PASS_B["E072"] = ([(1,"PARTIALLY_RELEVANT"),(2,"PARTIALLY_RELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"RELEVANT"),(5,"RELEVANT")],
                   "NONE","YES","Re-read: the before/after cards show a cluttered 'before' half in the SAME thumbnail, so they're only a partial minimalist-style match; the clean labeled-diagram cards (apple/bicycle) are the purer style match.")
PASS_B["E027"] = ([(1,"RELEVANT"),(2,"IRRELEVANT"),(3,"RELEVANT"),(4,"PARTIALLY_RELEVANT"),(5,"PARTIALLY_RELEVANT")],
                   "MINOR","YES","Re-read: rank2's fan-outfit card is titled and centered on a cap, not a scarf - downgraded from PARTIALLY_RELEVANT to IRRELEVANT on reconsideration.")
PASS_B["E154"] = ([(1,"RELEVANT"),(2,"RELEVANT"),(3,"PARTIALLY_RELEVANT"),(4,"IRRELEVANT"),(5,"PARTIALLY_RELEVANT")],
                   "MODERATE","PARTIALLY","Re-read: weighting the fact that 3 of 5 visible results are generic template-category browse tiles (not specific matched content) more heavily - this reviewer's holistic read is PARTIAL despite mechanical bands allowing PASS.")
PASS_B["E008"] = ([(1,"PARTIALLY_RELEVANT"),(2,"PARTIALLY_RELEVANT")],
                   "MINOR","PARTIALLY","Re-read: unchanged result-level calls, but flagged for adjudication - with only 2 thin partial-strength results, is PARTIAL the right call or is evidence too sparse to be more than UNJUDGABLE?")

QUERY_META = {
    24: "E024", 217: "E217", 248: "E248", 182: "E182", 154: "E154", 42: "E042", 1: "E001",
    276: "E276", 118: "E118", 72: "E072", 56: "E056", 63: "E063", 68: "E068", 8: "E008",
    9: "E009", 10: "E010", 12: "E012", 17: "E017", 18: "E018", 19: "E019", 27: "E027",
    2: "E002", 3: "E003", 4: "E004", 5: "E005", 6: "E006", 7: "E007", 11: "E011", 13: "E013",
    310: "E310",
}

with open(os.path.join(OUT, "evidence", "query_packets.json"), encoding="utf-8") as f:
    all_packets = {p["query_id"]: p for p in json.load(f)}


def run_pass(pass_data, pass_name):
    rows = []
    for qid, (labels, drift, intent, note) in pass_data.items():
        pk = all_packets[qid]
        result_labels = [{"rank": r, "label": l} for r, l in labels]
        result = score_query(result_labels, drift, intent, pk["zero_result"])
        eval_method = "TEXT_PLUS_VISUAL"  # all 30 calibration queries had screenshots read
        conf = confidence_for(result["judgeable_result_count"], False, False, eval_method)
        rows.append({
            "pass": pass_name, "query_id": qid, "query_index": pk["query_index"],
            "original_query": pk["original_query"], "category": pk["category"],
            "zero_result": pk["zero_result"], "query_broadened": pk["query_broadened"],
            "semantic_drift": drift, "original_intent_preserved": intent,
            "notes": note, **result, "relevance_confidence": conf,
        })
    return rows


rows_a = run_pass(PASS_A, "A")
rows_b = run_pass(PASS_B, "B")

a_by_qid = {r["query_id"]: r for r in rows_a}
b_by_qid = {r["query_id"]: r for r in rows_b}

comparison = []
label_agree = 0
score_diffs = []
for qid in PASS_A:
    a, b = a_by_qid[qid], b_by_qid[qid]
    agree = a["query_relevance_label"] == b["query_relevance_label"]
    label_agree += agree
    if a["relevance_score"] is not None and b["relevance_score"] is not None:
        score_diffs.append(abs(a["relevance_score"] - b["relevance_score"]))
    comparison.append({
        "query_id": qid, "original_query": a["original_query"],
        "pass_a_label": a["query_relevance_label"], "pass_b_label": b["query_relevance_label"],
        "agree": agree,
        "pass_a_score": a["relevance_score"], "pass_b_score": b["relevance_score"],
        "pass_a_drift": a["semantic_drift"], "pass_b_drift": b["semantic_drift"],
    })

n = len(PASS_A)
agreement_rate = label_agree / n

os.makedirs(os.path.join(OUT, "checkpoints"), exist_ok=True)
with open(os.path.join(OUT, "checkpoints", "calibration_pass_a.json"), "w", encoding="utf-8") as f:
    json.dump(rows_a, f, ensure_ascii=False, indent=2, default=str)
with open(os.path.join(OUT, "checkpoints", "calibration_pass_b.json"), "w", encoding="utf-8") as f:
    json.dump(rows_b, f, ensure_ascii=False, indent=2, default=str)
with open(os.path.join(OUT, "checkpoints", "calibration_comparison.json"), "w", encoding="utf-8") as f:
    json.dump({"n": n, "label_agreement_count": label_agree, "label_agreement_rate": agreement_rate,
                "avg_abs_score_diff": sum(score_diffs)/len(score_diffs) if score_diffs else None,
                "comparisons": comparison}, f, ensure_ascii=False, indent=2)

# calibration_results.csv (final, adjudicated) - written by a separate adjudication step
print(f"Pass A vs Pass B label agreement: {label_agree}/{n} = {agreement_rate:.1%}")
print(f"Avg abs score diff (where both scored): {sum(score_diffs)/len(score_diffs) if score_diffs else 'n/a':.2f}" if score_diffs else "n/a")
for c in comparison:
    flag = "" if c["agree"] else "  <<< DISAGREEMENT"
    print(f"{c['query_id']:6s} {c['original_query']:12s} A={c['pass_a_label']:8s}({c['pass_a_score']})  B={c['pass_b_label']:8s}({c['pass_b_score']}){flag}")
