"""P0-A R1/R2 descriptive arms (frozen P0_PROTOCOL_FREEZE.md §1.4), reconstructed from existing artifacts. No model.

§1.7 rule 1: P0-A STOPPED at headroom (oracle − T corpus chrF +2.24 < +3.0), and "R1/R2 are reported descriptively".
They were never run (RESULTS.md §9). This script applies the frozen selection rules to the canonical candidate pools
that already exist and scores them with the frozen §1.6 automatic metrics. It changes no decision.

  R1 simple rerank : if loop_out(T) is false keep T; else the non-loop pool candidate with the highest HF
                     sequences_scores from the num_beams=5 run; if none, keep T.
  R2 = R1 + probe  : (D-A only) P = P0-14 mt5_ms_testcv_r0 test_pred for the clip (sha256 ab1f932d…7528146).
                     K(x) = Tier L concepts mentioned in x (frozen matcher, p019_common.load_matcher).
                     support(x) = |K(x)∩P| − |K(x)\\P|. Start from R1's x1; switch to the non-loop candidate with
                     maximal support (ties -> earlier pool position) only if support ≥ support(x1) + 1.
  Descriptive only (§1.4): beam-5 rank-0; R2 with probe fold seeds r1/r2 (sha256 606fe1e5…, c794dcb7…).

Inputs (all existing): p0a-candidate-rerank/runs/full45/<domain>/run1/candidates.jsonl (canonical decode),
10.13 inputs_128.jsonl (references; scoring only), P0-14 splits/manifest.csv (test_clean order = test_pred rows),
P0-14 results/lr/mt5_ms_testcv_r{0,1,2}.json (local p014-work), How2Sign realigned train/test CSVs (matcher only).
Metric functions copied verbatim from p0a-candidate-rerank/scripts/headroom_oracle.py (which runs on import).

usage (repo root): python3 -I asl-translator/experiments/p0-2026-10-27/p0a_r1_r2_descriptive.py --probe-dir DIR --ref-dir DIR
"""
import argparse, csv, hashlib, json, os, re, sys

import sacrebleu

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P0A = os.path.join(REPO, "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank")
REFS = os.path.join(REPO, "docs/daily_report/10.13/asl-unisign-error-taxonomy/inputs_128.jsonl")
P014 = os.path.join(REPO, "docs/daily_report/10.15/asl-unisign-representation-probe")
OUT = os.path.join(HERE, "results", "p0a_r1_r2_descriptive.json")
# Frozen P0-14 probe outputs (local, uncommitted p014-work/results/lr/). R2 cannot be reproduced without these exact files.
PROBE_SHA = {"r0": "ab1f932db2f1b33470544677d6d5004060901f1421de4d63e892c910b7528146",
             "r1": "606fe1e5d4d7710043b0c6272a21c7e5e83e7787b2dfe550ba3d20f86706b3ca",
             "r2": "c794dcb7049331875140af73d1ad48ce540ca52f0be7be53131c8914e013cacf"}
CANON_SHA = {"A_official": "aeb817641769dd79139020157964e5d39d5ba031518dd191b360bf805664f5b4"}
DOMAINS = ("A_official", "B_ours_5p39")
CONTROLS = ["R41", "R04", "R09", "R20", "R22", "R27", "R45"]
REVIEW_ROLES = ("focus", "named_control", "ordinary_control")   # the 13 human-review cases: arm texts withheld,
                                                                  # as in p0a RESULTS.md (blind candidate_review.csv)

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.20/asl-p0-19-safe-rerank/scripts"))
from p019_common import guard_and_trip, load_matcher  # noqa: E402


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---- verbatim from headroom_oracle.py (§1.4 / §1.6)
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


def sent_chrf(h, r):
    return round(sacrebleu.sentence_chrf(h, [r]).score, 4)
# ---- end verbatim


def r1_select(pool):
    """Index into pool. pool[0] is T."""
    if not loop_out(pool[0]["text"]):
        return 0, "T_not_loop"
    cands = [(i, c) for i, c in enumerate(pool) if not loop_out(c["text"]) and c.get("beam5_seq_score") is not None]
    if not cands:
        return 0, "T_loop_no_nonloop_candidate"
    best = max(cands, key=lambda ic: (ic[1]["beam5_seq_score"], -ic[0]))  # highest score; ties -> earlier position
    return best[0], "nonloop_highest_beam5_seq_score"


def r2_select(pool, x1, P, present, LIDX):
    def K(text):
        v = present(text)
        return {k for k in LIDX if v[k]}
    Pset = {k for k in LIDX if P[k]}
    sup = lambda i: len(K(pool[i]["text"]) & Pset) - len(K(pool[i]["text"]) - Pset)
    s1 = sup(x1)
    nonloop = [i for i in range(len(pool)) if not loop_out(pool[i]["text"])]
    if not nonloop:
        return x1, s1, None, "no_nonloop_candidate"
    best = max(nonloop, key=lambda i: (sup(i), -i))
    if sup(best) >= s1 + 1:
        return best, s1, sup(best), "switched_support_gain"
    return x1, s1, sup(best), "kept_x1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-dir", required=True); ap.add_argument("--ref-dir", required=True)
    a = ap.parse_args()
    refs = {}
    for line in open(REFS):
        d = json.loads(line); refs[d["clip_id"]] = d["reference"]
    recs = {d: [json.loads(l) for l in open(os.path.join(P0A, f"runs/full45/{d}/run1/candidates.jsonl"))] for d in DOMAINS}
    ids = [r["clip_id"] for r in recs["A_official"]]
    trip = guard_and_trip(ids)
    assert sha256(os.path.join(P0A, "runs/full45/A_official/run1/candidates.jsonl")) == CANON_SHA["A_official"]
    present, crow, LIDX, h2s_refs = load_matcher(os.path.join(a.ref_dir, "how2sign_realigned_train.csv"),
                                                 os.path.join(a.ref_dir, "how2sign_realigned_test.csv"))
    man = [r for r in csv.DictReader(open(os.path.join(P014, "splits", "manifest.csv"))) if r["role"] == "test_clean"]
    row = {r["clip_id"]: i for i, r in enumerate(man)}
    CON = [r["concept"] for r in crow]
    # matcher sanity on these 45 (as P0-19 G5): manifest labels == matcher(reference)
    label_ok = sum([int(man[row[c]][k]) for k in CON] == present(h2s_refs[c]) for c in ids)
    probes = {}
    for seed in ("r0", "r1", "r2"):
        p = os.path.join(a.probe_dir, f"mt5_ms_testcv_{seed}.json")
        if not os.path.isfile(p):
            raise SystemExit(f"missing frozen probe file mt5_ms_testcv_{seed}.json in --probe-dir (P0-14 results/lr/, "
                             f"sha256 {PROBE_SHA[seed]}); R2 cannot be reproduced without it")
        h = sha256(p)
        if h != PROBE_SHA[seed]:
            raise SystemExit(f"mt5_ms_testcv_{seed}.json sha256 {h} != frozen {PROBE_SHA[seed]}; refusing to run")
        d = json.load(open(p)); assert len(d["test_pred"]) == len(man) == 2209
        probes[seed] = {"sha256": h, "pred": d["test_pred"]}

    out = {"protocol": "asl-translator/daily_report/2026-10-23/P0_PROTOCOL_FREEZE.md §1.4/§1.6/§1.7 (commit c644bc3d)",
           "no_model_run": True, "human_labels": "none (candidate_review.csv status columns blank); §1.7 rules 2-4 "
           "human parts not evaluable", "holdout": trip,
           "inputs": {"candidates": {d: {"path": os.path.relpath(os.path.join(P0A, f"runs/full45/{d}/run1/candidates.jsonl"), REPO),
                                         "sha256": sha256(os.path.join(P0A, f"runs/full45/{d}/run1/candidates.jsonl"))} for d in DOMAINS},
                      "references": {"path": os.path.relpath(REFS, REPO), "sha256": sha256(REFS)},
                      "probe_files": {s: {"file": f"P0-14 results/lr/mt5_ms_testcv_{s}.json (local p014-work, not committed)",
                                          "sha256": probes[s]["sha256"]} for s in probes},
                      "manifest": {"path": os.path.relpath(os.path.join(P014, "splits", "manifest.csv"), REPO),
                                   "sha256": sha256(os.path.join(P014, "splits", "manifest.csv"))},
                      "matcher": "p019_common.load_matcher (P0-14 build_concepts.py, Tier L = 24 concepts)",
                      "matcher_label_reproduction_45": f"{label_ok}/45"},
           "domains": {}}
    for dom in DOMAINS:
        cases, arms = [], {"T": [], "R1": [], "beam5_rank0": []}
        if dom == "A_official":
            arms.update({"R2": [], "R2_seed_r1": [], "R2_seed_r2": []})
        for r in recs[dom]:
            pool, ref, rid = r["pool"], refs[r["clip_id"]], r["review_id"]
            assert pool[0]["source"] == "T_beam4" and pool[0]["text"] == r["T"]["text"]
            x1, why1 = r1_select(pool)
            c = {"review_id": rid, "role": r["p0a_role"], "T_loop": loop_out(pool[0]["text"]), "R1_index": x1, "R1_rule": why1}
            arms["T"].append(pool[0]["text"]); arms["R1"].append(pool[x1]["text"])
            arms["beam5_rank0"].append(r["beam5"][0]["text"])
            c.update(T_chrF=sent_chrf(pool[0]["text"], ref), R1_chrF=sent_chrf(pool[x1]["text"], ref),
                     R1_changed=x1 != 0, R1_text=pool[x1]["text"] if x1 else "")
            withheld = r["p0a_role"] in REVIEW_ROLES
            if dom == "A_official":
                P = probes["r0"]["pred"][row[r["clip_id"]]]
                x2, s1, sb, why2 = r2_select(pool, x1, P, present, LIDX)
                arms["R2"].append(pool[x2]["text"])
                c.update(R2_index=x2, R2_rule=why2, support_x1=s1, support_best_nonloop=sb,
                         R2_chrF=sent_chrf(pool[x2]["text"], ref), R2_changed_vs_T=x2 != 0, R2_changed_vs_R1=x2 != x1,
                         R2_text=pool[x2]["text"] if x2 != x1 else "",
                         probe_concepts_P=[CON[k] for k in LIDX if P[k]])
                for s in ("r1", "r2"):
                    xs = r2_select(pool, x1, probes[s]["pred"][row[r["clip_id"]]], present, LIDX)[0]
                    arms[f"R2_seed_{s}"].append(pool[xs]["text"])
                    c[f"R2_seed_{s}_index"] = xs
            if withheld:
                c.update({k: "[withheld: human-review case]" for k in ("R1_text", "R2_text") if c.get(k)})
            cases.append(c)
        rl = [refs[r["clip_id"]] for r in recs[dom]]
        met = {k: corpus(v, rl) for k, v in arms.items()}
        sec = lambda r, keys: sum(r[k] for k in keys)
        timing = {"T_only_s_mean": round(sum(sec(r, ("sec_forward", "sec_T")) for r in recs[dom]) / 45, 3),
                  "pool_arms_s_mean": round(sum(sec(r, ("sec_forward", "sec_T", "sec_beam5")) for r in recs[dom]) / 45, 3),
                  "note": "recorded canonical decode times; R1/R2 selection adds no decode (pool already exists)"}
        D = {"corpus": met, "cpu_seconds_per_clip": timing,
             "changed_vs_T": {k: sum(x != t for x, t in zip(v, arms["T"])) for k, v in arms.items() if k != "T"},
             "changed_ids_vs_T": {k: [c["review_id"] for c, x, t in zip(cases, v, arms["T"]) if x != t]
                                  for k, v in arms.items() if k != "T"},
             "delta_vs_T": {k: {m: round(met[k][m] - met["T"][m], 4) for m in ("chrF", "BLEU4", "WER", "mean_len_ratio",
                                                                               "loop_out", "old_1013_flag")}
                            for k in arms if k != "T"},
             "controls_changed": {k: [x for x in D_ids if x in CONTROLS] for k, D_ids in
                                  {k: [c["review_id"] for c, x, t in zip(cases, v, arms["T"]) if x != t]
                                   for k, v in arms.items() if k != "T"}.items()},
             "rule2_automatic_limits_descriptive_only": {
                 k: {"WER_delta_le_+1.0": round(met[k]["WER"] - met["T"]["WER"], 4) <= 1.0,
                     "chrF_delta_ge_-0.5": round(met[k]["chrF"] - met["T"]["chrF"], 4) >= -0.5,
                     "len_ratio_within_10pct": abs(met[k]["mean_len_ratio"] / met["T"]["mean_len_ratio"] - 1) <= 0.10,
                     "loop_out_le_T": met[k]["loop_out"] <= met["T"]["loop_out"]} for k in arms if k in ("R1", "R2")},
             "cases": cases}
        out["domains"][dom] = D
    json.dump(out, open(OUT, "w"), indent=1)
    for dom, D in out["domains"].items():
        print(dom, json.dumps({k: D["corpus"][k] for k in D["corpus"]}, indent=0))
        print("  changed", D["changed_vs_T"], D["changed_ids_vs_T"])
    print("matcher labels", out["inputs"]["matcher_label_reproduction_45"])


if __name__ == "__main__":
    main()
