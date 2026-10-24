"""P0-A headroom / automatic-metric oracle (protocol P0_PROTOCOL_FREEZE.md §1.6, §1.7 rule 1a). No rerank, no training.

Reads the canonical CPU decode (runs/full45/<domain>/run1/candidates.jsonl; run2 is determinism evidence only) and the
frozen-128 references (10.13 inputs_128.jsonl). References are used ONLY to score candidates that already exist; the
pool is never built, filtered or reordered from them. The oracle is an analysis upper bound, not a system result.

Frozen metrics (§1.6): corpus chrF (sacrebleu corpus_chrf defaults), corpus BLEU-4 (13a), WER (lowercase whitespace
tokens, x100), mean output/reference word-length ratio, loop_out count (§1.4) and the old 10.13 flag beside it, number
of cases changed vs T. Oracle = pool candidate with the highest sentence chrF against the reference; ties go to the
earliest pool position (T is position 0, so ties keep T; the P0-19 convention).

Also writes the blinded human comparison sheet for the 13 review cases (§1.6): reference + pool in a shuffled order
fixed by sha256(domain|clip_id), no rank / arm labels. The key that decodes letters back to pool position, rank and
"is CPU top-1" is written to review_key/ and must not be shown to the reviewer.

Usage (repo root):  /opt/anaconda3/bin/python3 -I asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/scripts/headroom_oracle.py
"""
import csv, hashlib, json, os, random, re, sys

import sacrebleu

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(EXP, "..", "..", "..", ".."))
DR = os.path.join(REPO, "docs", "daily_report")
REFS = os.path.join(DR, "10.13", "asl-unisign-error-taxonomy", "inputs_128.jsonl")
OUT = os.path.join(EXP, "headroom")
DOMAINS = ("A_official", "B_ours_5p39")
LETTERS = "ABCDE"
HEADROOM_MIN_DCHRF = 3.0                              # §1.7 rule 1(a)

sys.path.insert(0, os.path.join(DR, "10.16", "asl-p0-16-experimental-credibility", "scripts"))
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


cases = list(csv.DictReader(open(os.path.join(EXP, "case_list.csv"))))
assert_not_holdout([c["clip_id"] for c in cases])
refs = {}
for line in open(REFS):
    d = json.loads(line)
    refs[d["clip_id"]] = d["reference"]
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(EXP, "review_key"), exist_ok=True)

rows, summary, review, key = [], {}, [], []
for dom in DOMAINS:
    src = os.path.join(EXP, "runs", "full45", dom, "run1", "candidates.jsonl")
    recs = [json.loads(l) for l in open(src)]
    assert [r["clip_id"] for r in recs] == [c["clip_id"] for c in cases] and all(r["domain"] == dom for r in recs)
    top1, orc, R = [], [], []
    for r, c in zip(recs, cases):
        ref = refs[r["clip_id"]]
        pool = r["pool"]
        assert pool[0]["source"] == "T_beam4" and pool[0]["text"] == r["T"]["text"]
        m = [sent(p["text"], ref) for p in pool]
        best = max(range(len(pool)), key=lambda i: (m[i]["chrF"], -i))
        nonloop = [i for i in range(1, len(pool)) if not m[i]["loop_out"]]
        bnl = max(nonloop, key=lambda i: (m[i]["chrF"], -i)) if nonloop else None
        row = {"review_id": r["review_id"], "clip_id": r["clip_id"], "domain": dom, "p0a_role": c["p0a_role"],
               "human_review": c["human_review"], "cpu_top1": r["T"]["text"], "n_pool": r["n_pool"],
               "n_unique_pre_trunc": r["n_unique"], "pool_lt5": int(r["pool_lt5"])}
        for i in range(5):
            p = pool[i] if i < len(pool) else None
            row[f"cand{i}_text"] = p["text"] if p else ""
            row[f"cand{i}_source"] = f"{p['source']}:{p['source_rank']}" if p else ""
            row[f"cand{i}_source_seq_score"] = round(p["source_seq_score"], 6) if p else ""
            row[f"cand{i}_beam5_seq_score"] = "" if not p or p["beam5_seq_score"] is None else round(p["beam5_seq_score"], 6)
            row[f"cand{i}_sum_logprob"] = round(p["source_sum_logprob"], 6) if p else ""
            row[f"cand{i}_chrF"] = m[i]["chrF"] if p else ""
        row.update({"oracle_pos": best, "oracle_text": pool[best]["text"], "oracle_differs": int(best != 0),
                    "top1_chrF": m[0]["chrF"], "oracle_chrF": m[best]["chrF"],
                    "delta_chrF": round(m[best]["chrF"] - m[0]["chrF"], 4),
                    "top1_WER": m[0]["WER"], "oracle_WER": m[best]["WER"],
                    "delta_WER": round(m[best]["WER"] - m[0]["WER"], 4),
                    "top1_len_ratio": m[0]["len_ratio"], "oracle_len_ratio": m[best]["len_ratio"],
                    "top1_loop_out": int(m[0]["loop_out"]), "oracle_loop_out": int(m[best]["loop_out"]),
                    "top1_old_1013_flag": int(m[0]["old_1013_flag"]), "oracle_old_1013_flag": int(m[best]["old_1013_flag"]),
                    "n_nonloop_alternatives": len(nonloop),
                    "best_nonloop_alt_pos": "" if bnl is None else bnl,
                    "best_nonloop_alt_chrF": "" if bnl is None else m[bnl]["chrF"],
                    "best_nonloop_alt_delta_chrF": "" if bnl is None else round(m[bnl]["chrF"] - m[0]["chrF"], 4)})
        rows.append(row)
        top1.append(pool[0]["text"]); orc.append(pool[best]["text"]); R.append(ref)
        if c["human_review"] == "1":
            order = list(range(len(pool)))
            random.Random(int(hashlib.sha256(f"P0-A review|{dom}|{r['clip_id']}".encode()).hexdigest()[:8], 16)).shuffle(order)
            rv = {"review_id": r["review_id"], "domain": dom, "ground_truth": ref}
            for k in range(5):
                rv[f"candidate_{LETTERS[k]}"] = pool[order[k]]["text"] if k < len(order) else ""
            for k in range(5):
                rv[f"status_{LETTERS[k]}"] = ""
                rv[f"error_tags_{LETTERS[k]}"] = ""
            rv.update({f: "" for f in ("best_candidate", "top1_status", "best_candidate_status", "wrong_to_right",
                                       "right_to_wrong", "unchanged", "changed_same_status", "cant_tell", "notes")})
            review.append(rv)
            for k, pos in enumerate(order):
                p = pool[pos]
                key.append({"review_id": r["review_id"], "domain": dom, "letter": LETTERS[k],
                            "candidate_id": f"{dom}:{r['review_id']}:p{pos}", "pool_pos": pos, "source": p["source"],
                            "source_rank": p["source_rank"], "beam5_rank": "" if p["beam5_rank"] is None else p["beam5_rank"],
                            "is_cpu_top1": int(pos == 0), "is_auto_oracle": int(pos == best), "text": p["text"]})
    ct, co = corpus(top1, R), corpus(orc, R)
    dom_rows = [x for x in rows if x["domain"] == dom]
    loops = [x for x in dom_rows if x["top1_loop_out"]]
    lwa = [x for x in loops if x["n_nonloop_alternatives"] > 0]
    summary[dom] = {
        "canonical_decode": os.path.relpath(src, REPO), "canonical_decode_sha256": sha256(src), "n_cases": len(recs),
        "top1": ct, "oracle": co, "delta": {k: round(co[k] - ct[k], 4) for k in ct},
        "n_oracle_differs_from_top1": sum(x["oracle_differs"] for x in dom_rows),
        "n_top1_is_oracle": sum(1 - x["oracle_differs"] for x in dom_rows),
        "oracle_differs_ids": [x["review_id"] for x in dom_rows if x["oracle_differs"]],
        "pool_size_distribution": {str(k): sum(x["n_pool"] == k for x in dom_rows) for k in range(1, 6) if any(x["n_pool"] == k for x in dom_rows)},
        "pools_lt5": {x["review_id"]: x["n_pool"] for x in dom_rows if x["pool_lt5"]},
        "rule_1a_oracle_minus_top1_chrF": round(co["chrF"] - ct["chrF"], 4),
        "rule_1a_threshold": HEADROOM_MIN_DCHRF,
        "rule_1a_pass": co["chrF"] - ct["chrF"] >= HEADROOM_MIN_DCHRF,
        "rule_1b": "PENDING human candidate review (>= 3 of 13 reviewed cases with a pool candidate rated strictly better than T)",
        "loops": {"top1_loop_out": len(loops), "with_nonloop_alternative": len(lwa),
                  "ids_with_alternative": {x["review_id"]: {"best_nonloop_alt_delta_chrF": x["best_nonloop_alt_delta_chrF"]} for x in lwa},
                  "ids_without_alternative": [x["review_id"] for x in loops if not x["n_nonloop_alternatives"]]},
    }

with open(os.path.join(OUT, "headroom_by_case.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(EXP, "candidate_review.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(review[0].keys())); w.writeheader(); w.writerows(review)
with open(os.path.join(EXP, "review_key", "candidate_review_key.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(key[0].keys())); w.writeheader(); w.writerows(key)
summary["meta"] = {"protocol": "P0_PROTOCOL_FREEZE.md §1.6 / §1.7 rule 1", "sacrebleu": sacrebleu.__version__,
                   "references": os.path.relpath(REFS, REPO), "references_sha256": sha256(REFS),
                   "oracle": "argmax sentence chrF over the pool; ties -> earliest pool position (T)",
                   "oracle_is_system_result": False, "rerank_run": False, "probe_run": False,
                   "script_sha256": sha256(os.path.abspath(__file__)), "holdout_guard": "PASS (45 ids)",
                   "n_review_rows": len(review)}
json.dump(summary, open(os.path.join(OUT, "headroom_summary.json"), "w"), indent=1)
print(json.dumps({d: {k: summary[d][k] for k in ("top1", "oracle", "delta", "n_oracle_differs_from_top1", "pools_lt5",
                                                    "rule_1a_pass", "loops")} for d in DOMAINS}, indent=1))
