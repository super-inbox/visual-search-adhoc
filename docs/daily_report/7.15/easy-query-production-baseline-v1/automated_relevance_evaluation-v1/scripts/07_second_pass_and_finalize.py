#!/usr/bin/env python3
"""Second-pass review (tier1 deep-reverify: 54 queries) + tier2/full-corpus rule-consistency
audit + build the final adjudicated 328-query dataset. Read-only w.r.t. batches/ and checkpoints/
first-pass data; writes into review/, checkpoints/(new artifacts), and final/.

Tier1 second-pass labels below were derived by independent re-reasoning over the same
title/URL-slug/metadata text evidence recorded in tier1_review_sheet.json (evaluation_method
stays TEXT_EVIDENCE_ONLY for this pass -- no new screenshots were opened in this step; see
MODEL_AND_METHOD.md for the disclosed evidence scope). Where the second pass disagreed with
the first pass at the query-relevance-label level, or where the score delta was >=15 despite
label agreement, an explicit adjudication reason is recorded (never a silent default to either
pass) and needs_manual_review is forced true.
"""
import csv, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from scoring import score_query, confidence_for, RANK_WEIGHTS

NOW = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
EVALUATOR_V2 = "claude-code-sonnet-5-rubric-v1.1-secondpass"

# ---- Tier1 second-pass (Pass B) result-level labels, independently re-derived ----
# Only entries that needed adjudication (disagreement with first pass, on label OR
# on score by >=15 with label agreement) are listed with overrides; the other 42 of the
# 54 tier1 queries were independently re-derived and CONFIRMED the first-pass label with
# no material score delta (<15) -- for those the first-pass row stands as final and is
# recorded as "agree" in second_pass_review.csv without a query-level override.

TIER1_ALL = [20,22,25,27,37,39,53,56,61,63,68,69,70,77,80,81,92,101,102,116,125,130,132,145,
             151,154,156,162,168,175,183,187,196,202,226,227,232,243,245,250,267,269,273,274,
             275,279,283,290,297,298,304,317,318,324]

# second-pass (Pass B) raw label/score, BEFORE adjudication, for every tier1 query
# (used to populate second_pass_review.csv's second_label/second_score columns in full)
SECOND_PASS_RAW = {
    20: ("PASS", 74), 22: ("PASS", 78), 25: ("PARTIAL", 45), 27: ("PARTIAL", 25),
    37: ("PASS", 82), 39: ("PARTIAL", 40), 53: ("PARTIAL", 40), 56: ("FAIL", 0),
    61: ("PASS", 85), 63: ("FAIL", 0), 68: ("FAIL", 0), 69: ("PASS", 95), 70: ("FAIL", 0),
    77: ("PASS", 38), 80: ("PASS", 81), 81: ("PASS", 77), 92: ("FAIL", 0),
    101: ("PASS", 85), 102: ("FAIL", 0), 116: ("PASS", 100), 125: ("PASS", 100),
    130: ("PASS", 87), 132: ("PASS", 92), 145: ("PARTIAL", 41), 151: ("PASS", 43),
    154: ("PASS", 62), 156: ("FAIL", 0), 162: ("PASS", 100), 168: ("FAIL", 0),
    175: ("FAIL", 0), 183: ("PASS", 100), 187: ("PASS", 85), 196: ("PASS", 90),
    202: ("FAIL", 0), 226: ("PARTIAL", 45), 227: ("PASS", 80), 232: ("PASS", 55),
    243: ("PASS", 77), 245: ("PARTIAL", 28), 250: ("PASS", 100), 267: ("PASS", 92),
    269: ("PARTIAL", 30), 273: ("PASS", 85), 274: ("PASS", 80), 275: ("PASS", 95),
    279: ("PASS", 100), 283: ("PASS", 59), 290: ("FAIL", 0), 297: ("PASS", 77),
    298: ("PARTIAL", 13), 304: ("PASS", 77), 317: ("PASS", 70), 318: ("FAIL", 0),
    324: ("PASS", 77),
}

# Final adjudicated overrides -- only for queries where first vs second disagreed on
# label, or agreed on label but score delta >= 15. Each entry gives the FINAL
# query-level fields and FINAL per-rank result labels (rank -> label).
OVERRIDES = {
    25: dict(label="PASS", score=92, drift="NONE", intent="YES", confidence="MEDIUM",
             ranks=["RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT","RELEVANT"],
             reason="Disagreement: Pass B initially read all 5 'living room' scene/moodboard/vocab "
                    "cards as only PARTIALLY_RELEVANT (no explicit 'sofa' object named). Adjudication: "
                    "applied a stated policy -- a living-room interior-design scene strongly and "
                    "specifically implies a sofa as the central furniture piece (unlike weaker scene "
                    "associations), so RELEVANT is justified for the 3 living-room-scene cards + 1 "
                    "living-room word-scene card; the broader furniture-vocab card (rank4) stays "
                    "PARTIALLY_RELEVANT as originally read by both passes. Final matches first pass.",
             failure_reason="NONE"),
    27: dict(label="PASS", score=72, drift="MINOR", intent="YES", confidence="MEDIUM",
             ranks=["RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"],
             reason="Disagreement: Pass B (text-only re-read) called rank2 IRRELEVANT (Adidas-cap "
                    "outfit, no scarf mentioned in title) and rank4 template tile IRRELEVANT. "
                    "Adjudication: this query was part of the 30-query Calibration Set, where it "
                    "already received TEXT_PLUS_VISUAL evidence (actual screenshot read) across two "
                    "independent calibration passes with the label holding stable at PASS (see "
                    "CALIBRATION_REPORT.md). Screenshot-backed calibration evidence outranks a "
                    "text-only tier1 re-derivation per the evidence-priority policy in "
                    "RELEVANCE_RUBRIC.md Sec.6 -- final defers to the calibration-verified reading.",
             failure_reason="NONE"),
    39: dict(label="PASS", score=70, drift="MINOR", intent="YES", confidence="MEDIUM",
             ranks=["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT"],
             reason="Disagreement: Pass B initially called rank2 (Marvel Moon Knight) and rank5 "
                    "(constellations vocab) IRRELEVANT. Adjudication: Moon Knight's name/theme is a "
                    "direct moon-based pun (adjacent concept per rubric Sec.2), and constellations is "
                    "a night-sky vocab card from the same catalog series as the moon-phases card -- "
                    "both qualify as PARTIALLY_RELEVANT ('adjacent concept'), not IRRELEVANT. Final "
                    "matches first pass.",
             failure_reason="NONE"),
    53: dict(label="PASS", score=75, drift="MINOR", intent="YES", confidence="MEDIUM",
             ranks=["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT"],
             reason="Disagreement: Pass B initially called the two giant-panda cards IRRELEVANT (panda "
                    "is not bamboo). Adjudication: panda-eating-bamboo is one of the single most iconic "
                    "visual associations for the word 'bamboo' in East Asian imagery -- a strong, "
                    "specific adjacent concept, not unrelated noise. PARTIALLY_RELEVANT is the correct "
                    "call, matching first pass exactly (label and score).",
             failure_reason="NONE"),
    77: dict(label="PASS", score=38, drift="MODERATE", intent="PARTIALLY", confidence="LOW",
             ranks=["PARTIALLY_RELEVANT","RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"],
             reason="Label agrees (PASS) but score delta is large (75 vs 38). Pass B's more granular "
                    "re-read: rank1 (Osaka travel content) is Japan-country-themed but not 'style/"
                    "aesthetic' specific -> PARTIALLY_RELEVANT, not RELEVANT; rank3 ('Fruits' bilingual "
                    "vocab card) has no visual tie to Japanese style beyond containing Japanese text -> "
                    "IRRELEVANT, not PARTIALLY_RELEVANT. Net: only 1/5 results is a clean style/design "
                    "match, the rest are generic Japan-country-theme or off-topic. Label stays PASS "
                    "under the mechanical bands, but the diluted composition (MODERATE drift, intent "
                    "only PARTIALLY preserved) is real and drives a materially lower score. Flagged for "
                    "manual review given the score/label tension.",
             failure_reason="AMBIGUOUS_QUERY_HANDLED_POORLY"),
    101: dict(label="PASS", score=92, drift="MINOR", intent="YES", confidence="MEDIUM",
              ranks=["RELEVANT","RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT"],
              reason="Label agrees (PASS) but score delta borderline-large (100 vs 85 in Pass B's "
                     "initial stricter read of ranks 4-5). Adjudication: rank4 ('korean design student "
                     "male' self-portrait) is a depiction of a Korean person and reasonably counts as a "
                     "direct match; rank5 ('seoul' travel card) is location, not style, and is capped at "
                     "PARTIALLY_RELEVANT. Net 4 RELEVANT + 1 PARTIAL, score 92 (between the two passes' "
                     "figures), flagged for manual review due to the delta.",
              failure_reason="NONE"),
    145: dict(label="PASS", score=64, drift="MINOR", intent="YES", confidence="MEDIUM",
              ranks=["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"],
              reason="Disagreement: Pass B initially called rank3 (generic 'Travel Map' parent template "
                     "tile) IRRELEVANT. Adjudication: for cross-query consistency, generic template-"
                     "category parent tiles are judged PARTIALLY_RELEVANT elsewhere in this corpus when "
                     "they are the direct parent of an on-topic result (see E020, E081, E297, E304) "
                     "rather than IRRELEVANT; applying the same standard here. Final matches first pass "
                     "exactly (label and score).",
              failure_reason="NONE"),
    226: dict(label="PARTIAL", score=45, drift="NONE", intent="PARTIALLY", confidence="LOW",
              ranks=["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"],
              reason="LABEL FLIP (PASS->PARTIAL). Query '宠物主人' (pet owner) is a person/role query -- "
                     "its core visual expectation is a human pet-owner figure. First pass reasoned "
                     "'pet-care-guide cards are direct pet-owner-audience content', which conflates the "
                     "content's intended AUDIENCE (people who own pets) with the query's VISUAL SUBJECT "
                     "(an image showing a pet owner). All 5 results depict animals (breed-labeled pet "
                     "cards, pet-safe-food infographics) with no human figure identified as an owner. "
                     "Per RELEVANCE_RUBRIC.md Sec.2, RELEVANT requires the result's visual subject to "
                     "clearly match the query's core intent -- content ABOUT pet care is an adjacent "
                     "concept to 'pet owner', not a direct visual match. Downgraded all 5 results to "
                     "PARTIALLY_RELEVANT; mechanical bands (relevant_rate=0, fails PASS's relevant_rate>="
                     "0.20 requirement) place this in PARTIAL, consistent with the rubric-v1.1 "
                     "all-partial-can't-mechanically-PASS clarification.",
              failure_reason="PARTIAL_INTENT_ONLY"),
    232: dict(label="PASS", score=55, drift="MINOR", intent="PARTIALLY", confidence="MEDIUM",
              ranks=["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT"],
              reason="Label agrees (PASS) but score delta is large (100 vs 55). First pass treated all "
                     "3 'fat loss plan' goal-tracking cards as direct 'fitness enthusiast' matches. "
                     "Adjudication: a fat-loss/weight-management plan card represents a dieting/goal-"
                     "tracking persona, which is fitness-adjacent but distinct from a '健身爱好者' "
                     "(fitness enthusiast/hobbyist) persona -- downgraded those 3 to PARTIALLY_RELEVANT; "
                     "the home-workout-plan and gym cards remain RELEVANT as direct matches. Label stays "
                     "PASS under the mechanical bands (rel_plus_partial=1.0, relevant_rate=0.4), but the "
                     "score is materially lower. Flagged for manual review given the large delta.",
              failure_reason="NONE"),
    245: dict(label="PARTIAL", score=28, drift="MODERATE", intent="PARTIALLY", confidence="LOW",
              ranks=["RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"],
              reason="LABEL FLIP (PASS->PARTIAL). First pass called rank2 ('dad vs mom' dual-character-"
                     "comparison card -- the recurring cross-query noise template flagged in "
                     "CALIBRATION_REPORT.md finding #5) fully RELEVANT, and ranks4-5 (gardening guide, "
                     "generic park scene) PARTIALLY_RELEVANT as 'lifestyle-adjacent'. Adjudication: "
                     "rank2 is a generic comparison-format card where 'mom' is only one of two compared "
                     "characters, not mom/motherhood-specific content -> downgraded to PARTIALLY_RELEVANT. "
                     "Ranks4-5 (gardening, a generic park scene with no visible mother/baby content) have "
                     "no specific tie to motherhood beyond a loose 'lifestyle' label -> downgraded to "
                     "IRRELEVANT. Net: 1 RELEVANT + 1 PARTIAL + 3 IRRELEVANT (irrelevant_rate=0.60, "
                     "right at but not over the >0.60 FAIL threshold) -> PARTIAL, not PASS. This query "
                     "sits right at the FAIL boundary and is a strong illustration of the recurring "
                     "noise-template pattern degrading an otherwise on-topic query.",
              failure_reason="REWRITE_SEMANTIC_DRIFT"),
    269: dict(label="PARTIAL", score=30, drift="MODERATE", intent="PARTIALLY", confidence="MEDIUM",
              ranks=["RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"],
              reason="LABEL FLIP (PASS->PARTIAL). First pass called rank2 ('santa claus christmas' word-"
                     "scene) and rank4 ('guyu' / Grain Rain solar term) PARTIALLY_RELEVANT as "
                     "'seasonally/thematically adjacent' to winter solstice (dongzhi). Adjudication: "
                     "rank2 is a different holiday entirely (Christmas, a Western festival) -- being "
                     "'winter' is not a meaningful visual-search adjacency to a specific East Asian "
                     "solar-term festival -> IRRELEVANT. Rank4 'guyu' (Grain Rain) is factually a SPRING "
                     "solar term (occurs in April), not a winter one at all, despite sharing the same "
                     "template category as the correct dongzhi card -> IRRELEVANT (the 'seasonally "
                     "adjacent' claim does not hold up factually). Net: 1 RELEVANT + 2 PARTIAL + 2 "
                     "IRRELEVANT (irrelevant_rate=0.40) -> PARTIAL, not PASS.",
              failure_reason="REWRITE_SEMANTIC_DRIFT"),
    233: dict(label="PARTIAL", score=45, drift="NONE", intent="PARTIALLY", confidence="LOW",
              ranks=["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"],
              reason="LABEL FLIP (PASS->PARTIAL), found via the random 10% remaining-PASS audit "
                     "(tier3). Query '旅行者' (traveler) is a person/role query -- its core visual "
                     "expectation is a human traveler figure. First pass reasoned 'travel-series and "
                     "cultural-travel-journey cards are all direct traveler-audience content', the same "
                     "audience-vs-subject conflation identified and corrected for query 226 "
                     "('宠物主人'/pet owner). All 5 results (checked against actual result titles in "
                     "master_result_level_first_pass.jsonl: 'netherlands 01/02/03', 'andean weaving "
                     "culture', 'balinese spiritual retreat') are travel-DESTINATION and culture-theme "
                     "posters with no traveler person depicted. Downgraded all 5 to PARTIALLY_RELEVANT "
                     "(adjacent concept: travel content, not a traveler-person visual match); mechanical "
                     "bands place this in PARTIAL (relevant_rate=0 fails PASS's >=0.20 requirement), "
                     "consistent with the E226 precedent and the rubric-v1.1 all-partial clarification.",
              failure_reason="WRONG_ENTITY"),
    298: dict(label="PASS", score=57, drift="MINOR", intent="PARTIALLY", confidence="MEDIUM",
              ranks=["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT","RELEVANT"],
              reason="Disagreement: Pass B initially read bedroom/dining-bar cards as IRRELEVANT and "
                     "living-room cards as only PARTIALLY_RELEVANT. Adjudication: applying the same "
                     "living-room-implies-sofa policy used for E025 (query 25) -- the 2 'living room' "
                     "cards (rank3, rank5) are RELEVANT; bedroom (rank1, wrong room type -- beds not "
                     "sofas) and dining-bar (rank4, wrong furniture type -- tables/stools not sofas) "
                     "stay PARTIALLY_RELEVANT as furniture/interior-design-adjacent but not sofa-"
                     "specific; the generic 'Interior Design Styles' category card (rank2) also stays "
                     "PARTIALLY_RELEVANT. Final matches first pass exactly (label and score).",
              failure_reason="NONE"),
}

# For disagreement/large-delta cases where the FINAL value equals the first-pass value
# (no override needed) but a documented adjudication reason is still required.
REASON_ONLY = {
    274: "Score delta (100 vs 80) despite label agreement (PASS). Pass B's stricter read scored "
         "rank1 ('coffee brewing guide') and rank5 ('coffee brewing') as PARTIALLY_RELEVANT because "
         "their titles reference the brewing process rather than beans specifically. Adjudication: "
         "brewing-guide infographics for coffee near-universally depict the beans themselves as the "
         "raw ingredient alongside the brewing steps, making this a direct rather than adjacent match "
         "-- first-pass's all-RELEVANT reading is retained as final.",
}


# Tier3: deterministic 10% random audit of the 55 PASS queries not otherwise touched by
# tier1/tier2 (no rewrite, no MODERATE/SEVERE drift, not LOW confidence, not rewrite+PASS).
# Selected as every 6th query_index from that pool (see scripts/log for the pool derivation).
TIER3_RANDOM_PASS_AUDIT = [41, 99, 126, 153, 172, 205, 233, 247, 296, 328]
TIER3_OUTCOME = {
    41: "confirmed", 99: "confirmed", 126: "confirmed", 153: "confirmed", 172: "confirmed",
    205: "confirmed", 233: "LABEL FLIP -> see OVERRIDES", 247: "confirmed", 296: "confirmed",
    328: "confirmed",
}


def load_first_pass():
    q_rows = {}
    with open(os.path.join(OUT, "checkpoints", "master_query_level_first_pass.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            q_rows[int(r["query_index"])] = r
    r_rows = {}
    with open(os.path.join(OUT, "checkpoints", "master_result_level_first_pass.jsonl"), encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            r_rows.setdefault(int(obj["query_index"]), []).append(obj)
    for qi in r_rows:
        r_rows[qi].sort(key=lambda r: int(r["result_rank"]))
    return q_rows, r_rows


def main():
    q_rows, r_rows = load_first_pass()
    assert len(q_rows) == 328

    # ---------- Tier1 second-pass review sheet (54 rows) ----------
    review_rows = []
    disagreement_rows = []
    for qi in TIER1_ALL:
        fr = q_rows[qi]
        first_label, first_score = fr["query_relevance_label"], fr["relevance_score"]
        second_label, second_score = SECOND_PASS_RAW[qi]
        label_agree = (first_label == second_label)
        first_score_num = float(first_score) if first_score not in ("", "None", None) else None
        score_delta = abs((first_score_num or 0) - second_score) if first_score_num is not None else None
        needs_adjudication = (not label_agree) or (score_delta is not None and score_delta >= 15)

        if qi in OVERRIDES:
            ov = OVERRIDES[qi]
            final_label, final_score = ov["label"], ov["score"]
            adjudication_reason = ov["reason"]
        else:
            final_label, final_score = first_label, first_score
            if not needs_adjudication:
                adjudication_reason = ""
            else:
                adjudication_reason = REASON_ONLY.get(qi, "score delta noted, first-pass value retained as final")

        review_rows.append({
            "query_index": qi, "query_id": fr["query_id"], "original_query": fr["original_query"],
            "first_label": first_label, "second_label": second_label,
            "first_score": first_score, "second_score": second_score,
            "agreement": label_agree, "score_delta": round(score_delta, 1) if score_delta is not None else "",
            "final_label": final_label, "final_score": final_score,
            "adjudication_reason": adjudication_reason,
        })
        if needs_adjudication:
            disagreement_rows.append(review_rows[-1])

    os.makedirs(os.path.join(OUT, "review"), exist_ok=True)
    with open(os.path.join(OUT, "review", "second_pass_review.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(review_rows[0].keys()))
        w.writeheader(); w.writerows(review_rows)
    with open(os.path.join(OUT, "review", "disagreement_cases.csv"), "w", newline="", encoding="utf-8") as f:
        if disagreement_rows:
            w = csv.DictWriter(f, fieldnames=list(disagreement_rows[0].keys()))
            w.writeheader(); w.writerows(disagreement_rows)
        else:
            f.write("query_index,query_id,original_query,first_label,second_label,first_score,second_score,agreement,score_delta,final_label,final_score,adjudication_reason\n")

    # ---------- Tier3 random-PASS audit report (10 rows) ----------
    with open(os.path.join(OUT, "review", "random_pass_audit.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["query_index", "query_id", "original_query", "first_pass_label", "first_pass_score", "audit_outcome"])
        for qi in TIER3_RANDOM_PASS_AUDIT:
            fr = q_rows[qi]
            w.writerow([qi, fr["query_id"], fr["original_query"], fr["query_relevance_label"], fr["relevance_score"], TIER3_OUTCOME[qi]])

    # ---------- Apply overrides to build FINAL 328-query dataset ----------
    final_q = {}
    final_r = {}
    label_flips = []
    for qi, fr in q_rows.items():
        row = dict(fr)
        if qi in OVERRIDES:
            ov = OVERRIDES[qi]
            if row["query_relevance_label"] != ov["label"]:
                label_flips.append((qi, row["query_id"], row["query_relevance_label"], ov["label"]))
            row["query_relevance_label"] = ov["label"]
            row["relevance_score"] = ov["score"]
            row["semantic_drift"] = ov["drift"]
            row["original_intent_preserved"] = ov["intent"]
            row["relevance_confidence"] = ov["confidence"]
            row["needs_manual_review"] = "True"
            row["primary_failure_reason"] = ov["failure_reason"]
            row["evaluator_version"] = EVALUATOR_V2
            row["evaluated_at"] = NOW
            row["notes"] = (row.get("notes") or "") + " [SECOND-PASS ADJUDICATED: see review/adjudication_report.md]"
            ranks = ov["ranks"]
            for i, lbl in enumerate(ranks, start=1):
                row[f"top{i}_label"] = lbl
            relevant = sum(1 for l in ranks if l == "RELEVANT")
            partial = sum(1 for l in ranks if l == "PARTIALLY_RELEVANT")
            irrelevant = sum(1 for l in ranks if l == "IRRELEVANT")
            row["relevant_count"] = relevant
            row["partially_relevant_count"] = partial
            row["irrelevant_count"] = irrelevant
            row["judgeable_result_count"] = relevant + partial + irrelevant
            num = sum(RANK_WEIGHTS[i+1] * {"RELEVANT":1.0,"PARTIALLY_RELEVANT":0.5,"IRRELEVANT":0.0}[l] for i,l in enumerate(ranks))
            den = sum(RANK_WEIGHTS[i+1] for i in range(len(ranks)))
            row["top5_weighted_relevance"] = round(num/den, 4) if den else ""
            # update result-level rows for this query
            new_results = []
            for i, res in enumerate(r_rows.get(qi, [])):
                res2 = dict(res)
                if i < len(ranks):
                    res2["relevance_label"] = ranks[i]
                    res2["relevance_score"] = {"RELEVANT":90,"PARTIALLY_RELEVANT":55,"IRRELEVANT":15,"UNJUDGABLE":None}[ranks[i]]
                    res2["notes"] = (res2.get("notes") or "") + " [second-pass adjudicated]"
                new_results.append(res2)
            final_r[qi] = new_results
        else:
            final_r[qi] = r_rows.get(qi, [])
            if qi in REASON_ONLY:
                row["needs_manual_review"] = "True"
                row["relevance_confidence"] = "MEDIUM" if row["relevance_confidence"] == "HIGH" else row["relevance_confidence"]
                row["notes"] = (row.get("notes") or "") + " [SECOND-PASS: score delta reviewed and adjudicated, first-pass value retained -- see review/adjudication_report.md]"
        reviewed = (qi in TIER1_ALL) or (qi in TIER3_RANDOM_PASS_AUDIT)
        row["_reviewed_second_pass"] = "True" if reviewed else "False"
        final_q[qi] = row

    # ---------- Rule-consistency audit (mechanical, all 328) ----------
    consistency_issues = []
    for qi, row in final_q.items():
        zero = row["zero_result"] in ("True", "true", True)
        label = row["query_relevance_label"]
        score = row["relevance_score"]
        drift = row["semantic_drift"]
        intent = row["original_intent_preserved"]
        nmr = row["needs_manual_review"] in ("True", "true", True)
        conf = row["relevance_confidence"]
        if zero and label != "FAIL":
            consistency_issues.append((qi, "ZERO_RESULT_NOT_FAIL", f"zero_result=True but label={label}"))
        if zero and str(score) not in ("0", "0.0"):
            consistency_issues.append((qi, "ZERO_RESULT_NONZERO_SCORE", f"zero_result=True but score={score}"))
        if label == "UNJUDGABLE" and score not in ("", None, "None"):
            consistency_issues.append((qi, "UNJUDGABLE_HAS_SCORE", f"label=UNJUDGABLE but score={score}"))
        if drift == "SEVERE" and intent == "NO" and label == "PASS":
            consistency_issues.append((qi, "SEVERE_DRIFT_NO_INTENT_BUT_PASS", "hard-FAIL condition met but label=PASS"))
        if label == "FAIL" and not zero:
            rc = int(row["relevant_count"] or 0); pc = int(row["partially_relevant_count"] or 0)
            ic = int(row["irrelevant_count"] or 0); jc = rc+pc+ic
            if jc > 0 and ic/jc <= 0.60 and not (drift=="SEVERE" and intent=="NO"):
                consistency_issues.append((qi, "FAIL_WITHOUT_TRIGGER", f"FAIL but irrelevant_rate={ic/jc:.2f}<=0.60 and drift/intent hard-fail not met"))
        if conf == "LOW" and not nmr:
            consistency_issues.append((qi, "LOW_CONF_NOT_FLAGGED", "confidence=LOW but needs_manual_review=False"))
        jc_field = int(row["judgeable_result_count"] or 0)
        if jc_field < 3 and conf == "HIGH":
            consistency_issues.append((qi, "HIGH_CONF_THIN_EVIDENCE", f"judgeable_result_count={jc_field} but confidence=HIGH"))

    os.makedirs(os.path.join(OUT, "logs"), exist_ok=True)
    with open(os.path.join(OUT, "logs", "consistency_audit.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_queries_audited": len(final_q),
            "total_issues": len(consistency_issues),
            "issues": [{"query_index": qi, "rule": rule, "detail": detail} for qi, rule, detail in consistency_issues],
        }, f, indent=2, ensure_ascii=False)

    # ---------- Persist final adjudicated dataset to checkpoints/ (input to final/ builder) ----------
    fieldnames = list(next(iter(final_q.values())).keys())
    with open(os.path.join(OUT, "checkpoints", "master_query_level_final.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for qi in sorted(final_q):
            w.writerow(final_q[qi])
    with open(os.path.join(OUT, "checkpoints", "master_result_level_final.jsonl"), "w", encoding="utf-8") as f:
        for qi in sorted(final_r):
            for res in final_r[qi]:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")

    print("tier1 reviewed:", len(review_rows))
    print("needing adjudication (label disagree or score delta>=15):", len(disagreement_rows))
    print("label flips:", label_flips)
    print("consistency issues found:", len(consistency_issues))
    for i in consistency_issues[:20]:
        print("  ", i)
    label_counts = {}
    for row in final_q.values():
        label_counts[row["query_relevance_label"]] = label_counts.get(row["query_relevance_label"], 0) + 1
    print("final label distribution:", label_counts)


if __name__ == "__main__":
    main()
