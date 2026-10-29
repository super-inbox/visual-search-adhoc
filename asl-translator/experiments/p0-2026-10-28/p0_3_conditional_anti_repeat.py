#!/usr/bin/env python3
"""P0-3 (NEXT_P0_PLAN 2026-10-28): conditional anti-repeat arm built from the SAVED Task 1 outputs. CPU, no model.

Pre-registered (fixed before any conditional output or metric was computed):
  trigger   loop_out(control) from P0_PROTOCOL_FREEZE §1.4, unchanged: lowercase, tokens = regex [a-z0-9']+,
            word 3-grams over consecutive tokens, repetition ratio = 1 - |distinct 3-grams| / |3-grams|, fire if >= 0.15
            (no 3-grams -> no fire). Output only; no reference, no model score.
  arm       triggered -> saved Task 1 treatment text (no_repeat_ngram_size=3, num_beams=4, max_new_tokens=100);
            not triggered -> saved control text, byte for byte. Nothing is regenerated.
  negatives every control output with >= 2 "I'm" (regex \\bI['\u2019]m\\b, case-sensitive) + R35.
  metrics   the P0-A §1.6 functions, copied verbatim from p0-2026-10-27/score_repetition.py (which runs on import).

Descriptive damage proxies (defined after the triggered texts had been read; not used for any decision threshold):
  first_repeat_word  index of the first word that starts a repeated word 3-gram in the control output
  common_prefix      length of the common word prefix of control and conditional output
  pre_loop_altered   common_prefix < first_repeat_word (text before the loop was changed)
  lost_word_types    word types (loop_out tokenizer) in control but absent from the conditional output

Inputs: committed Task 1 decode file (sha256-checked), P0-A canonical A_official T, 10.13 references (scoring only).
Usage (repo root): python3 -I asl-translator/experiments/p0-2026-10-28/p0_3_conditional_anti_repeat.py
"""
import hashlib, json, os, re, sys

import sacrebleu

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
T1 = os.path.join(REPO, "asl-translator/experiments/p0-2026-10-27/results")
DECODE = os.path.join(T1, "repetition_paired_decode_local_arm64.json")
SCORES = os.path.join(T1, "repetition_paired_scores.json")
CANON = os.path.join(REPO, "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/runs/full45/A_official/run1/candidates.jsonl")
REFS = os.path.join(REPO, "docs/daily_report/10.13/asl-unisign-error-taxonomy/inputs_128.jsonl")
OUT = os.path.join(HERE, "results", "p0_3_conditional_anti_repeat.json")
DECODE_SHA = "9de31696de1634390715ce6d5ac59b025ab466de02d5e2a48b2f21c6e362e6e6"
TRIGGER_THRESHOLD = 0.15
IM = re.compile(r"\bI['\u2019]m\b")
CHRF_BIN = 5.0                                       # Task 1's pre-fixed sentence-chrF triage bin, reused

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ── P0-A §1.4 / §1.6, verbatim from score_repetition.py ──────────────────────
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


# ── trigger details and descriptive damage proxies ───────────────────────────
def toks(x):
    return re.findall(r"[a-z0-9']+", x.lower())


def rep_ratio(x):
    t = toks(x)
    g = [tuple(t[i:i + 3]) for i in range(len(t) - 2)]
    return {"n_trigrams": len(g), "n_distinct": len(set(g)),
            "repeated_trigram_occurrences": len(g) - len(set(g)),
            "ratio": round(1 - len(set(g)) / len(g), 4) if g else 0.0}


def first_repeat_word(x):
    t, seen = toks(x), set()
    for i in range(len(t) - 2):
        g = tuple(t[i:i + 3])
        if g in seen:
            return i
        seen.add(g)
    return None


def common_prefix(a, b):
    a, b = toks(a), toks(b)
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


def main():
    assert sha256(DECODE) == DECODE_SHA, "Task 1 decode file changed"
    dec = json.load(open(DECODE))
    assert dec["status"] == "COMPLETE" and dec["generation_executed"]
    t1 = json.load(open(SCORES))["summary"]
    canon = {json.loads(l)["clip_id"]: json.loads(l) for l in open(CANON)}
    refs = {json.loads(l)["clip_id"]: json.loads(l)["reference"] for l in open(REFS)}
    res = sorted(dec["results"], key=lambda r: r["review_id"])
    assert [r["review_id"] for r in res] == [f"R{i:02d}" for i in range(1, 46)]
    assert_not_holdout([r["clip_id"] for r in res])

    rows, C, G, K, R = [], [], [], [], []
    for r in res:
        c, g = r["arms"]["control"]["text"], r["arms"]["no_repeat_token_trigram"]["text"]
        assert r["control_matches_saved_cpu"] and r["arms"]["control"]["token_ids"] == canon[r["clip_id"]]["T"]["ids"]
        ref = refs[r["clip_id"]]
        trig = loop_out(c)
        k = g if trig else c
        sc, sk, sg = sent(c, ref), sent(k, ref), sent(g, ref)
        fr = first_repeat_word(c)
        cp = common_prefix(c, k)
        row = {"review_id": r["review_id"], "p0a_role": canon[r["clip_id"]]["p0a_role"],
               "trigger": {"fired": trig, **rep_ratio(c)},
               "conditional_source": "treatment" if trig else "control",
               "byte_identical_to_control": k == c, "changed": k != c,
               "global_treatment_changed": g != c,
               "im_count": {"control": len(IM.findall(c)), "conditional": len(IM.findall(k)), "global": len(IM.findall(g))},
               "loop_out": {"control": sc["loop_out"], "conditional": sk["loop_out"], "global": sg["loop_out"]},
               "old_1013_flag_control": sc["old_1013_flag"],
               "hits_max_control": (len(r["arms"]["control"]["token_ids"]) - 1) >= 100 and not r["arms"]["control"]["eos_present"],
               "words": {"control": len(c.split()), "conditional": len(k.split()), "global": len(g.split())},
               "sentence": {"control": {x: sc[x] for x in ("chrF", "WER", "len_ratio")},
                            "conditional": {x: sk[x] for x in ("chrF", "WER", "len_ratio")}},
               "delta_chrF": round(sk["chrF"] - sc["chrF"], 4), "delta_WER": round(sk["WER"] - sc["WER"], 4)}
        if trig:
            lost = sorted(set(toks(c)) - set(toks(k)))
            row["triggered_detail"] = {"first_repeat_word": fr, "common_prefix_words": cp,
                                       "pre_loop_altered": fr is not None and cp < fr,
                                       "lost_word_types_n": len(lost),
                                       "auto_bin": ("improve_candidate" if row["delta_chrF"] >= CHRF_BIN else
                                                    "regress_candidate" if row["delta_chrF"] <= -CHRF_BIN else "small_change")}
        rows.append(row); C.append(c); G.append(g); K.append(k); R.append(ref)

    trig = [x for x in rows if x["trigger"]["fired"]]
    untrig = [x for x in rows if not x["trigger"]["fired"]]
    assert all(x["byte_identical_to_control"] for x in untrig)
    neg = [x for x in rows if x["im_count"]["control"] >= 2 or x["review_id"] == "R35"]
    corp = {"control": corpus(C, R), "conditional": corpus(K, R), "global_no_repeat_3": corpus(G, R)}
    assert corp["control"] == {k: t1["corpus"]["control"][k] for k in corp["control"]}
    assert corp["global_no_repeat_3"] == {k: t1["corpus"]["no_repeat_token_trigram"][k] for k in corp["control"]}
    changed = [x for x in rows if x["changed"]]
    glob_changed = [x for x in rows if x["global_treatment_changed"]]
    out = {
        "inputs": {"task1_decode": os.path.relpath(DECODE, REPO), "task1_decode_sha256": DECODE_SHA,
                   "references": os.path.relpath(REFS, REPO), "references_sha256": sha256(REFS),
                   "canonical_T": os.path.relpath(CANON, REPO), "canonical_T_sha256": sha256(CANON),
                   "domain": "A_official (the Task 1 decode domain)", "n_cases": len(rows)},
        "preregistered_trigger": {"rule": "loop_out(control), P0_PROTOCOL_FREEZE §1.4", "normalization": "lowercase",
                                  "tokenizer": "regex [a-z0-9']+", "ngram": "word 3-grams over consecutive tokens",
                                  "statistic": "1 - distinct/total 3-grams", "threshold": TRIGGER_THRESHOLD,
                                  "uses_reference": False},
        "trigger": {"fired": len(trig), "rate": round(len(trig) / len(rows), 4),
                    "fired_ids": [x["review_id"] for x in trig],
                    "fired_with_old_1013_flag": [x["review_id"] for x in trig if x["old_1013_flag_control"]],
                    "fired_hits_max": [x["review_id"] for x in trig if x["hits_max_control"]],
                    "task1_loop_cases": t1["loop_change"]["removed"]},
        "loops": {"before": corp["control"]["loop_out"], "after_conditional": corp["conditional"]["loop_out"],
                  "after_global": corp["global_no_repeat_3"]["loop_out"],
                  "triggered_eliminated": sum(not x["loop_out"]["conditional"] for x in trig),
                  "triggered_remaining": sum(x["loop_out"]["conditional"] for x in trig)},
        "non_triggered_byte_identical": f"{sum(x['byte_identical_to_control'] for x in untrig)}/{len(untrig)}",
        "corpus": corp,
        "changed": {"conditional": [x["review_id"] for x in changed], "conditional_n": len(changed),
                    "global_n": len(glob_changed),
                    "global_non_loop_changed": [x["review_id"] for x in glob_changed if not x["loop_out"]["control"]],
                    "conditional_non_loop_changed": [x["review_id"] for x in changed if not x["loop_out"]["control"]]},
        "negative_controls": [{"review_id": x["review_id"], "im_count": x["im_count"], "trigger_fired": x["trigger"]["fired"],
                               "conditional_changed": x["changed"], "global_changed": x["global_treatment_changed"],
                               "repetition_ratio": x["trigger"]["ratio"]} for x in neg],
        "triggered_damage_proxies": {
            "pre_loop_altered": [x["review_id"] for x in trig if x["triggered_detail"]["pre_loop_altered"]],
            "regress_candidate": [x["review_id"] for x in trig if x["triggered_detail"]["auto_bin"] == "regress_candidate"],
            "chrF_down": [x["review_id"] for x in trig if x["delta_chrF"] < 0],
            "im_lost_inside_triggered": [x["review_id"] for x in trig if x["im_count"]["conditional"] < x["im_count"]["control"]]},
        "cost": {"incremental_model_calls": 0, "incremental_api_cost": 0,
                 "note": "built from saved outputs; a real triggered-only regeneration would add one decode per triggered case "
                         "(Task 1 recorded ~2.7 s CPU per no_repeat decode on this machine)",
                 "task1_no_repeat_decode_seconds_45": t1["generate_seconds"]["no_repeat_token_trigram"]},
        "review_case_texts": "withheld (P0-A convention); this file holds no output or reference text",
        "cases": rows,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    open(OUT, "a").write("\n")
    print(json.dumps({k: out[k] for k in ("trigger", "loops", "non_triggered_byte_identical", "changed",
                                          "triggered_damage_proxies")}, indent=1))
    print(json.dumps(out["corpus"], indent=1)); print(json.dumps(out["negative_controls"]))


if __name__ == "__main__":
    main()
