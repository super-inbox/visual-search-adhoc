"""Task 2 Step 3: score the same-domain sampling decode (Uni-Sign sampling diagnostic). CPU, no model.

Metrics are the P0-A frozen ones, copied verbatim from score_repetition.py (itself verbatim from P0-A
headroom_oracle.py): corpus chrF / BLEU-4 (sacrebleu defaults), WER (lowercase whitespace tokens, x100), mean
output/reference word-length ratio; sentence chrF / WER per case.

Definitions fixed in this file before any decode output existed (written before decode_sampling.py was run in full):
  scopes per domain (domains never pooled):
    primary      provenance VERIFIED rows (A 41, B 42)
    long         primary rows with > 256 pose frames (the only rows where arms differ)
    control      primary rows with <= 256 pose frames (arms identical by construction; outputs must be identical)
    all45        every row, model-input-relative only; R10/R14 B labelled timing-label MISMATCH, UNRESOLVED rows
                 labelled; never used for source-time claims
  per-case delta vs random: d_chrF = sentence chrF(arm) - chrF(random); d_WER likewise
  improve_candidate d_chrF >= +5 ; regress_candidate d_chrF <= -5 (same bin as Task 1) ; else small_change / unchanged
  geometry_improves  max_gap_frames(arm) <= max_gap_frames(random) - 2
  similar_geometry   |max_gap_frames(arm) - max_gap_frames(random)| <= 1 and overlap_with_random >= 0.90 x 256
  sign test          two-sided exact binomial on non-tied d_chrF signs (descriptive only; n is small)
Automatic metrics only; no semantic claim. human_status is "pending" for every case.

usage (repo root): /opt/anaconda3/bin/python3 -I asl-translator/experiments/p0-2026-10-27/score_sampling.py
"""
import csv, hashlib, json, math, os, statistics, sys

import sacrebleu

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.join(HERE, "results")
DECODE = os.path.join(RES, "sampling_quality_decode.json")
CALLS = os.path.join(RES, "sampling_quality_calls.json")
REFS = os.path.join(REPO, "docs/daily_report/10.13/asl-unisign-error-taxonomy/inputs_128.jsonl")
BUDGET, CHRF_BIN = 256, 5.0
DOMAINS = ("A_official", "B_ours_5p39")
ARMS = ("random", "uniform", "coverage_motion")
SENS = "coverage_motion_boss"

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def edits(h, r):
    h, r = h.lower().split(), r.lower().split()
    d = list(range(len(r) + 1))
    for i, hw in enumerate(h, 1):
        prev, d[0] = d[0], i
        for j, rw in enumerate(r, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (hw != rw))
    return d[len(r)], len(r)


def corpus(hyps, refs):
    e = [edits(h, r) for h, r in zip(hyps, refs)]
    return {"n": len(refs), "chrF": round(sacrebleu.corpus_chrf(hyps, [refs]).score, 4),
            "BLEU4": round(sacrebleu.corpus_bleu(hyps, [refs]).score, 4),
            "WER": round(100 * sum(x for x, _ in e) / sum(n for _, n in e), 4),
            "mean_len_ratio": round(sum(len(h.split()) / max(len(r.split()), 1) for h, r in zip(hyps, refs)) / len(refs), 4)}


def sent(h, r):
    e, n = edits(h, r)
    return {"chrF": round(sacrebleu.sentence_chrf(h, [r]).score, 4), "WER": round(100 * e / n, 4)}


def sign_test(d):
    pos, neg = sum(x > 0 for x in d), sum(x < 0 for x in d)
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    return round(min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n), 4)


def main():
    dec = json.load(open(DECODE))
    assert dec["status"] == "COMPLETE" and dec["generation_executed"], dec["status"]
    res = dec["results"]
    assert len(res) == 90
    assert_not_holdout(sorted({r["clip_id"] for r in res}))
    refs = {}
    for line in open(REFS):
        d = json.loads(line); refs[d["clip_id"]] = d["reference"]
    calls = json.load(open(CALLS))

    rows = []
    for r in res:
        ref = refs[r["clip_id"]]
        base = r["arms"]["random"]
        bs = sent(base["text"], ref)
        label = r["provenance_status"]
        if label == "MISMATCH":
            label = "MISMATCH (timing label; measured interval only, not original timing)"
        for arm, x in r["arms"].items():
            s = sent(x["text"], ref)
            row = {"domain": r["domain"], "review_id": r["review_id"], "clip_id": r["clip_id"], "arm": arm,
                   "provenance_status": label, "primary_scope": r["provenance_status"] == "VERIFIED",
                   "n_frames": r["n_frames"], "subsampled": r["subsampled"], "reference": ref, "text": x["text"],
                   "chrF": s["chrF"], "WER": s["WER"], "words_out": len(x["text"].split()), "words_ref": len(ref.split()),
                   "eos": x["eos_present"], "n_gen_tokens": len(x["token_ids"]) - 1,
                   "changed_vs_random": x["text"] != base["text"],
                   "d_chrF_vs_random": round(s["chrF"] - bs["chrF"], 4), "d_WER_vs_random": round(s["WER"] - bs["WER"], 4),
                   "overlap_with_random": x["overlap_with_random"], "n_selected": x["n_selected"],
                   "max_gap_frames": x["max_gap_frames"], "max_gap_s": x.get("max_gap_s", ""),
                   "selected_motion_mean": x.get("selected_motion_mean", ""),
                   "d_max_gap_frames_vs_random": x["max_gap_frames"] - base["max_gap_frames"],
                   "indices_sha256": x["indices_sha256"], "kps_sha256": x["kps_sha256"], "human_status": "pending"}
            d = row["d_chrF_vs_random"]
            row["auto_bin"] = ("baseline" if arm == "random" else "unchanged" if not row["changed_vs_random"] else
                               "improve_candidate" if d >= CHRF_BIN else "regress_candidate" if d <= -CHRF_BIN else "small_change")
            row["geometry_improves"] = arm != "random" and row["d_max_gap_frames_vs_random"] <= -2
            row["similar_geometry"] = (arm != "random" and abs(row["d_max_gap_frames_vs_random"]) <= 1
                                       and row["overlap_with_random"] >= 0.90 * BUDGET)
            rows.append(row)

    def pick(dom, scope, arm):
        out = [x for x in rows if x["domain"] == dom and x["arm"] == arm]
        if scope == "primary":
            out = [x for x in out if x["primary_scope"]]
        elif scope == "long":
            out = [x for x in out if x["primary_scope"] and x["subsampled"]]
        elif scope == "control":
            out = [x for x in out if x["primary_scope"] and not x["subsampled"]]
        elif scope == "all45_long":
            out = [x for x in out if x["subsampled"]]
        return sorted(out, key=lambda x: x["review_id"])

    def comp(dom, scope, arm):
        c = pick(dom, scope, arm)
        return corpus([x["text"] for x in c], [x["reference"] for x in c]) if c else None

    def paired(dom, scope, arm):
        c = pick(dom, scope, arm)
        if not c:
            return None
        dc, dw = [x["d_chrF_vs_random"] for x in c], [x["d_WER_vs_random"] for x in c]
        return {"n": len(c), "changed_vs_random": sum(x["changed_vs_random"] for x in c),
                "chrF_gt_random": sum(v > 0 for v in dc), "chrF_lt_random": sum(v < 0 for v in dc),
                "chrF_eq_random": sum(v == 0 for v in dc),
                "WER_lt_random(better)": sum(v < 0 for v in dw), "WER_gt_random(worse)": sum(v > 0 for v in dw),
                "mean_d_chrF": round(statistics.mean(dc), 4), "median_d_chrF": round(statistics.median(dc), 4),
                "mean_d_WER": round(statistics.mean(dw), 4), "median_d_WER": round(statistics.median(dw), 4),
                "sign_test_p_chrF": sign_test(dc),
                "improve_candidates": [x["review_id"] for x in c if x["auto_bin"] == "improve_candidate"],
                "regress_candidates": [x["review_id"] for x in c if x["auto_bin"] == "regress_candidate"],
                "mean_overlap_with_random": round(statistics.mean(x["overlap_with_random"] for x in c), 1),
                "mean_d_max_gap_frames": round(statistics.mean(x["d_max_gap_frames_vs_random"] for x in c), 2)}

    summary = {"decode_file": os.path.relpath(DECODE, REPO), "decode_sha256": sha256(DECODE),
               "references": os.path.relpath(REFS, REPO), "references_sha256": sha256(REFS),
               "interpretation": "Uni-Sign 256-frame sampling diagnostic only; not a production-model result "
                                 "(the production Gemini path does not use this sampling).",
               "random_control": {d: f"{sum(r['random_matches_saved_T'] for r in res if r['domain'] == d)}/45 text+token ids == saved P0-A T"
                                  for d in DOMAINS},
               "device_check": {"generate_calls": len(calls["calls"]),
                                "devices": sorted({v for c in calls["calls"] for v in c["devices"]}),
                                "kwargs_seen": sorted({json.dumps(c["kwargs"], sort_keys=True) for c in calls["calls"]}),
                                "torch": calls["torch"], "threads": calls["threads"],
                                "generate_seconds": round(sum(c["seconds"] for c in calls["calls"]), 1)},
               "frozen_definitions": {"chrF_bin": CHRF_BIN, "geometry_improves": "max_gap_frames <= random - 2",
                                      "similar_geometry": "|d max_gap_frames| <= 1 and overlap >= 0.90 x 256"},
               "domains": {}}
    for dom in DOMAINS:
        arms = ARMS + ((SENS,) if dom == "B_ours_5p39" else ())
        ctrl = pick(dom, "control", "random")
        ctrl_ok = all(len({x["text"] for x in rows if x["domain"] == dom and x["review_id"] == c["review_id"]}) == 1 for c in ctrl)
        D = {"n_primary": len(pick(dom, "primary", "random")), "n_long": len(pick(dom, "long", "random")),
             "n_control": len(ctrl), "long_cases": [x["review_id"] for x in pick(dom, "long", "random")],
             "controls_identical_across_arms": ctrl_ok,
             "corpus": {sc: {arm: comp(dom, sc, arm) for arm in (arms if sc in ("long", "all45_long") else ARMS)}
                        for sc in ("primary", "long", "control", "all45")},
             "paired_vs_random": {sc: {arm: paired(dom, sc, arm) for arm in arms if arm != "random"}
                                  for sc in ("long", "all45_long")}}
        long_rows = [x for x in rows if x["domain"] == dom and x["primary_scope"] and x["subsampled"] and x["arm"] != "random"]
        top = sorted(long_rows, key=lambda x: -x["d_chrF_vs_random"])
        brief = lambda x: {k: x[k] for k in ("review_id", "arm", "d_chrF_vs_random", "d_WER_vs_random", "overlap_with_random",
                                               "d_max_gap_frames_vs_random", "text")}
        D["strongest_improvements"] = [brief(x) for x in top if x["d_chrF_vs_random"] > 0][:5]
        D["strongest_regressions"] = [brief(x) for x in reversed(top) if x["d_chrF_vs_random"] < 0][:5]
        D["geometry_improves_translation_not"] = [brief(x) for x in long_rows
                                                  if x["geometry_improves"] and x["d_chrF_vs_random"] < CHRF_BIN]
        D["translation_improves_similar_geometry"] = [brief(x) for x in long_rows
                                                      if x["similar_geometry"] and x["d_chrF_vs_random"] >= CHRF_BIN]
        D["n_geometry_improves"] = sum(x["geometry_improves"] for x in long_rows)
        D["n_similar_geometry"] = sum(x["similar_geometry"] for x in long_rows)
        if dom == "B_ours_5p39":
            D["timing_mismatch_rows_model_input_relative"] = [
                {"review_id": x["review_id"], "arm": x["arm"], "d_chrF_vs_random": x["d_chrF_vs_random"],
                 "label": x["provenance_status"]} for x in rows
                if x["domain"] == dom and x["review_id"] in ("R10", "R14") and x["arm"] != "random"]
        summary["domains"][dom] = D

    json.dump({"summary": summary, "cases": rows}, open(os.path.join(RES, "sampling_quality_scores.json"), "w"), indent=1)
    with open(os.path.join(RES, "sampling_quality_cases.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
