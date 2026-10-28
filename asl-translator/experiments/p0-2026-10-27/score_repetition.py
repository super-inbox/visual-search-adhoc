"""Score the paired control / no_repeat_token_trigram decode on the 45 canonical cases. CPU, no model.

Metrics are the P0-A frozen ones (P0_PROTOCOL_FREEZE.md §1.4/§1.6), copied verbatim from
daily_report/2026-10-23/p0a-candidate-rerank/scripts/headroom_oracle.py (that file runs on import):
corpus chrF / BLEU-4 (sacrebleu defaults), WER (lowercase whitespace tokens, x100), mean output/reference word-length
ratio, loop_out (§1.4, output only) and the old 10.13 flag beside it.

Descriptive bins below were fixed before any treatment output was read; they are triage for human review, not
semantic labels. human_status is always "pending".
  chrF candidate : delta sentence chrF >= +5 -> "improve_candidate", <= -5 -> "regress_candidate", else "small_change"
  shortened      : treatment words <= 0.75 x control words
  hits_max       : generated tokens (ids minus decoder start) >= 100 and no EOS

Usage (repo root): /opt/anaconda3/bin/python3 -I asl-translator/experiments/p0-2026-10-27/score_repetition.py
"""
import csv, hashlib, json, os, re, sys

import sacrebleu

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.join(HERE, "results")
DECODE = os.path.join(RES, "repetition_paired_decode_local_arm64.json")
CALLS = DECODE + ".calls.json"
CANON = os.path.join(REPO, "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/runs/full45/A_official/run1/candidates.jsonl")
REFS = os.path.join(REPO, "docs/daily_report/10.13/asl-unisign-error-taxonomy/inputs_128.jsonl")
MAX_NEW, CHRF_BIN, SHORT = 100, 5.0, 0.75

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def loop_out(x):                                      # §1.4, output only
    t = re.findall(r"[a-z0-9']+", x.lower())
    g = [tuple(t[i:i + 3]) for i in range(len(t) - 2)]
    return bool(g) and 1 - len(set(g)) / len(g) >= 0.15


def _rep3(s):                                         # 10.13 taxonomy.py has_rep3 / rep3_ratio, unchanged
    w = s.lower().split(); g = [tuple(w[k:k + 3]) for k in range(len(w) - 2)]
    return (len(g) > 0 and len(set(g)) < len(g)), (0.0 if not g else 1 - len(set(g)) / len(g))


def old_flag(pred, ref):                              # 10.13 primary == repetition_loop (reported beside loop_out)
    hp, rp = _rep3(pred)
    return hp and not _rep3(ref)[0] and rp >= 0.15


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
    return {"chrF": round(sacrebleu.corpus_chrf(hyps, [refs]).score, 4),
            "BLEU4": round(sacrebleu.corpus_bleu(hyps, [refs]).score, 4),
            "WER": round(100 * sum(x for x, _ in e) / sum(n for _, n in e), 4),
            "mean_len_ratio": round(sum(len(h.split()) / max(len(r.split()), 1) for h, r in zip(hyps, refs)) / len(refs), 4),
            "loop_out": sum(loop_out(h) for h in hyps),
            "old_1013_flag": sum(old_flag(h, r) for h, r in zip(hyps, refs))}


def sent(h, r):
    e, n = edits(h, r)
    return {"chrF": round(sacrebleu.sentence_chrf(h, [r]).score, 4), "WER": round(100 * e / n, 4),
            "len_ratio": round(len(h.split()) / max(n, 1), 4), "loop_out": loop_out(h), "old_1013_flag": old_flag(h, r)}


def gen_info(arm):
    n_gen = len(arm["token_ids"]) - 1                 # excludes decoder start token
    return {"n_gen_tokens": n_gen, "eos": arm["eos_present"], "hits_max": n_gen >= MAX_NEW and not arm["eos_present"],
            "n_words": len(arm["text"].split()), "empty": not arm["text"].strip()}


dec = json.load(open(DECODE))
assert dec["status"] == "COMPLETE" and dec["generation_executed"], dec["status"]
canon = {json.loads(l)["clip_id"]: json.loads(l) for l in open(CANON)}
refs = {}
for line in open(REFS):
    d = json.loads(line); refs[d["clip_id"]] = d["reference"]
res = dec["results"]
assert len(res) == 45 and sorted(r["review_id"] for r in res) == [f"R{i:02d}" for i in range(1, 46)]
assert_not_holdout([r["clip_id"] for r in res])

rows, ctrl_hyp, trt_hyp, ref_list = [], [], [], []
for r in sorted(res, key=lambda x: x["review_id"]):
    c, ref = canon[r["clip_id"]], refs[r["clip_id"]]
    ca, ta = r["arms"]["control"], r["arms"]["no_repeat_token_trigram"]
    assert r["kps_sha256"] == c["kps_sha256"]
    cs, ts, cg, tg = sent(ca["text"], ref), sent(ta["text"], ref), gen_info(ca), gen_info(ta)
    changed = ca["text"] != ta["text"]
    d_chrf = round(ts["chrF"] - cs["chrF"], 4)
    loop = ("none" if not cs["loop_out"] and not ts["loop_out"] else "kept" if cs["loop_out"] and ts["loop_out"]
            else "removed" if cs["loop_out"] else "new")
    chrf_bin = "unchanged" if not changed else ("improve_candidate" if d_chrf >= CHRF_BIN else
                                                "regress_candidate" if d_chrf <= -CHRF_BIN else "small_change")
    rows.append({
        "review_id": r["review_id"], "clip_id": r["clip_id"], "p0a_role": c["p0a_role"], "subsampled": c["subsampled"],
        "reference": ref, "control_text": ca["text"], "treatment_text": ta["text"],
        "control_text_matches_saved_T": r["control_matches_saved_cpu"],
        "control_ids_match_saved_T": ca["token_ids"] == c["T"]["ids"],
        "changed": changed,
        "chrF_control": cs["chrF"], "chrF_treatment": ts["chrF"], "chrF_delta": d_chrf,
        "WER_control": cs["WER"], "WER_treatment": ts["WER"], "WER_delta": round(ts["WER"] - cs["WER"], 4),
        "loop_out_control": cs["loop_out"], "loop_out_treatment": ts["loop_out"], "loop_change": loop,
        "old_1013_flag_control": cs["old_1013_flag"], "old_1013_flag_treatment": ts["old_1013_flag"],
        "words_ref": len(ref.split()), "words_control": cg["n_words"], "words_treatment": tg["n_words"],
        "gen_tokens_control": cg["n_gen_tokens"], "gen_tokens_treatment": tg["n_gen_tokens"],
        "eos_control": cg["eos"], "eos_treatment": tg["eos"],
        "hits_max_control": cg["hits_max"], "hits_max_treatment": tg["hits_max"],
        "shortened": changed and tg["n_words"] <= SHORT * cg["n_words"],
        "empty_control": cg["empty"], "empty_treatment": tg["empty"],
        "auto_bin": chrf_bin,
        "loop_removed_but_chrF_down": loop == "removed" and d_chrf < 0,
        "human_status": "pending"})
    ctrl_hyp.append(ca["text"]); trt_hyp.append(ta["text"]); ref_list.append(ref)

calls = json.load(open(CALLS))
kw = {json.dumps(x["kwargs"], sort_keys=True) for x in calls["calls"]}
arm_secs = {"control": round(sum(x["seconds"] for x in calls["calls"][0::2]), 1),
            "no_repeat_token_trigram": round(sum(x["seconds"] for x in calls["calls"][1::2]), 1)}


def count(key, val=True):
    return sum(x[key] == val for x in rows)


summary = {
    "decode_file": os.path.relpath(DECODE, REPO), "decode_sha256": sha256(DECODE),
    "references": os.path.relpath(REFS, REPO), "references_sha256": sha256(REFS),
    "canonical": os.path.relpath(CANON, REPO), "canonical_sha256": sha256(CANON),
    "n_cases": len(rows),
    "control_reproduction": {"text_match": count("control_text_matches_saved_T"), "token_ids_match": count("control_ids_match_saved_T")},
    "device_check": {"generate_calls": len(calls["calls"]), "devices": sorted({d for x in calls["calls"] for d in x["devices"]}),
                     "torch": calls["torch"], "threads": calls["threads"], "generate_kwargs_seen": sorted(kw)},
    "generate_seconds": arm_secs,
    "corpus": {"control": corpus(ctrl_hyp, ref_list), "no_repeat_token_trigram": corpus(trt_hyp, ref_list)},
    "saved_P0A_T_corpus_for_reference": {"chrF": 23.7634, "BLEU4": 5.7246, "WER": 95.4369, "mean_len_ratio": 0.9997, "loop_out": 9, "old_1013_flag": 7},
    "mean_words": {"reference": round(sum(x["words_ref"] for x in rows) / 45, 2),
                   "control": round(sum(x["words_control"] for x in rows) / 45, 2),
                   "no_repeat_token_trigram": round(sum(x["words_treatment"] for x in rows) / 45, 2)},
    "changed": count("changed"), "unchanged": 45 - count("changed"),
    "loop_change": {k: [x["review_id"] for x in rows if x["loop_change"] == k] for k in ("removed", "new", "kept")},
    "loop_none_count": sum(x["loop_change"] == "none" for x in rows),
    "hits_max": {"control": [x["review_id"] for x in rows if x["hits_max_control"]],
                 "no_repeat_token_trigram": [x["review_id"] for x in rows if x["hits_max_treatment"]]},
    "shortened": [x["review_id"] for x in rows if x["shortened"]],
    "empty": {"control": count("empty_control"), "no_repeat_token_trigram": count("empty_treatment")},
    "auto_bin": {k: [x["review_id"] for x in rows if x["auto_bin"] == k]
                 for k in ("improve_candidate", "regress_candidate", "small_change", "unchanged")},
    "loop_removed_but_chrF_down": [x["review_id"] for x in rows if x["loop_removed_but_chrF_down"]],
    "human_status": "pending for all 45",
    "bins_fixed_before_results": {"chrF_bin": CHRF_BIN, "shortened_ratio": SHORT, "max_new_tokens": MAX_NEW},
}
json.dump({"summary": summary, "cases": rows}, open(os.path.join(RES, "repetition_paired_scores.json"), "w"), indent=1)
with open(os.path.join(RES, "repetition_paired_cases.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(json.dumps(summary, indent=1))
