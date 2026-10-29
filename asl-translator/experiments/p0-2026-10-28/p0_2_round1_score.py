#!/usr/bin/env python3
"""P0-2 Round 1 scoring: frozen metrics, run-integrity checks and the frozen decision gates. No model or API call.

Written before any Round-1 output was read. Inputs: the harness case files (results/p0_2_same_input/{gemini,openai}),
the frozen pre-registration and manifest, and the 10.13 references (inputs_128.jsonl, the source used by production_45).
Metric functions are imported unchanged from asl-eval/production_45_tools.py (P0-A frozen definitions).

Interpretations fixed here, before outputs were read, where the pre-registered text leaves a detail open:
  - non-answer case = empty output text, or case status no_signing_detected / parse_failure / transport_failure;
  - win / loss / tie on sentence chrF: tie if |delta| < 1, win if delta >= 1, loss if delta <= -1;
  - B strata comparator = Gemini (the input-matched arm) for every stratum; the Uni-Sign stratum only selects cases;
    "one signer proxy" = each signer proxy with >= 5 pilot cases, tested separately;
  - generic/hallucinated automatic proxy = a non-empty output repeated verbatim on 2+ different clips within one arm;
  - cost = token counts x official list prices read on the run date (2026-10-29): OpenAI gpt-6.1-sol $2 / $0.10 cached /
    $10 output (reasoning billed as output); Gemini 2.5 Flash $0.30 / $0.03 cached / $2.50 output incl. thinking.

usage: python3 -I p0_2_round1_score.py
"""
import importlib.util, json, re, statistics, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RES = HERE / "results"
RUN = RES / "p0_2_same_input"
REFS = REPO / "docs/daily_report/10.13/asl-unisign-error-taxonomy/inputs_128.jsonl"
SEED, B = 20261028, 10_000
PRICE = {"openai": {"input": 2.0, "cached_input": 0.10, "output": 10.0},
         "gemini": {"input": 0.30, "cached_input": 0.03, "output": 2.50}}
PRICE_SOURCE = {"openai": "developers.openai.com/api/docs/models/gpt-6.1-sol, read 2026-10-29",
                "gemini": "ai.google.dev/gemini-api/docs/pricing (last updated 2026-10-28), read 2026-10-29"}
NON_ANSWER = ("no_signing_detected", "parse_failure", "transport_failure")

spec = importlib.util.spec_from_file_location("p45", REPO / "asl-translator/asl-eval/production_45_tools.py")
p45 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p45)
spec = importlib.util.spec_from_file_location("harness", HERE / "p0_2_same_input_comparison.py")
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)


def load():
    pre = json.loads((RES / "p0_2_openai_preregistration.json").read_text())
    man = {c["clip_id"]: c for c in json.loads((RES / "p0_2_subset_manifest.json").read_text())["pilot_frame_manifest"]}
    ids = sorted(pre["selection"]["pilot_ids"])
    assert ids == sorted(H.PILOT_IDS)
    rows = {json.loads(l)["clip_id"]: json.loads(l) for l in open(REFS)}
    cases = {p: {i: json.loads((RUN / p / f"{i}.json").read_text()) for i in ids
                 if (RUN / p / f"{i}.json").exists()} for p in ("gemini", "openai")}
    return pre, man, ids, rows, cases


def integrity(man, ids, cases):
    c = {}
    c["halted"] = (RUN / "HALTED.json").exists()
    c["cases_per_arm"] = {p: len(v) for p, v in cases.items()}
    calls = {p: [b for r in v.values() for b in r["batches"]] for p, v in cases.items()}
    c["requests_attempted"] = {p: sum(b["api_attempted"] for b in v) for p, v in calls.items()}
    c["requests_expected"] = sum(man[i]["n_batches"] for i in ids)
    c["no_retry"] = all(b["attempt"] == 1 and not b.get("replayed_from_primary") for v in calls.values() for b in v)
    c["frame_hashes_frozen"] = all(
        b.get("same_input_verified") and b["frame_sha256"] == [f["sha256"] for f in man[r["clip_id"]]["frames"]
                                                               [b["batch_index"] * 24:b["batch_index"] * 24 + 24]]
        and b["batch_input_sha256"] == man[r["clip_id"]]["batches"][b["batch_index"]]["input_sha256"]
        for v in cases.values() for r in v.values() for b in r["batches"])
    rm = json.loads((RUN / "manifest.json").read_text())
    c["prompt_hash_frozen"] = rm["prompt_sha256"] == H.PROMPT_SHA and c["frame_hashes_frozen"]   # checked per request
    oa = [b for b in calls["openai"] if b["api_ok"]]
    c["openai_model_exact_every_successful_call"] = all(b["model_returned"] == H.OPENAI_MODEL for b in oa)
    c["openai_successful_calls"] = len(oa)
    c["gemini_model_versions"] = sorted({str(b["model_returned"]) for b in calls["gemini"] if b["api_ok"]})
    first = {}
    for i in ids:
        t = {p: cases[p][i]["batches"][0].get("call_utc") for p in cases if i in cases[p]}
        first[i] = min(t, key=t.get) if len(t) == 2 and all(t.values()) else None
    c["call_order_followed"] = all(first[i] == H.arm_order(i)[0] for i in ids)
    c["call_order_counts"] = {"gemini_first": sum(first[i] == "gemini" for i in ids),
                              "openai_first": sum(first[i] == "openai" for i in ids)}
    c["all_cases_in_denominator"] = all(len(v) == len(ids) for v in cases.values())
    c["run_manifest"] = {k: rm[k] for k in ("started_utc", "openai_model", "gemini_model", "image_detail", "sdk",
                                            "retries")}
    return c, calls


def usage(p, calls):
    tot = {k: 0 for k in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens", "total_tokens")}
    for b in calls:
        for k in tot:
            tot[k] += (b.get("usage") or {}).get(k) or 0
    pr = PRICE[p]
    billed_out = tot["output_tokens"] + (tot["reasoning_tokens"] if p == "gemini" else 0)   # OpenAI output incl.
    cost = ((tot["input_tokens"] - tot["cached_input_tokens"]) * pr["input"] + tot["cached_input_tokens"]
            * pr["cached_input"] + billed_out * pr["output"]) / 1e6
    lat = [b["latency_s"] for b in calls if b.get("latency_s") is not None]
    return {"calls": len(calls), "tokens": tot, "billed_output_tokens": billed_out, "cost_usd": round(cost, 4),
            "price_per_1M": pr, "price_source": PRICE_SOURCE[p],
            "latency_s": {"median": round(statistics.median(lat), 3), "mean": round(statistics.mean(lat), 3),
                          "max": round(max(lat), 3), "sum": round(sum(lat), 3)} if lat else None}


def boot(d, groups=None):
    rng = np.random.default_rng(SEED); d = np.asarray(d)
    if groups is None:
        m = d[rng.integers(0, len(d), size=(B, len(d)))].mean(axis=1)
    else:
        keys = sorted(set(groups)); idx = {k: np.where(np.asarray(groups) == k)[0] for k in keys}
        m = np.empty(B)
        for j in range(B):
            pick = rng.integers(0, len(keys), size=len(keys))
            m[j] = d[np.concatenate([idx[keys[k]] for k in pick])].mean()
    lo, hi = np.percentile(m, [2.5, 97.5])
    return {"lo": round(float(lo), 4), "hi": round(float(hi), 4), "resamples": B, "seed": SEED}


def wlt(ds):
    return {"wins": sum(x >= 1 for x in ds), "losses": sum(x <= -1 for x in ds), "ties": sum(abs(x) < 1 for x in ds)}


def main():
    pre, man, ids, rows, cases = load()
    chk, calls = integrity(man, ids, cases)
    refs = [rows[i]["reference"] for i in ids]
    signer = [man[i]["signer_proxy"] for i in ids]
    hyp = {p: [(cases[p][i].get("output_text") or "") if i in cases[p] else "" for i in ids] for p in cases}
    status = {p: [cases[p][i]["case_status"] if i in cases[p] else "missing" for i in ids] for p in cases}
    degen = {p: [bool(cases[p][i].get("degenerate_repetition")) if i in cases[p] else False for i in ids]
             for p in cases}
    uni = [rows[i]["predictions"]["A_official"] for i in ids]

    arm = {}
    for p in ("gemini", "openai"):
        cm = p45.corpus(hyp[p], refs)
        counts = {s: status[p].count(s) for s in ("success", "partial", "no_signing_detected", "parse_failure",
                                                    "transport_failure", "missing")}
        txt = [h.strip() for h in hyp[p] if h.strip()]
        rep = sum(txt.count(t) >= 2 for t in txt)
        non_answer = sum(not h.strip() or s in NON_ANSWER for h, s in zip(hyp[p], status[p]))
        arm[p] = {"corpus": cm, "degenerate_repetition": sum(degen[p]), "status_counts": counts,
                  "non_answer_cases": non_answer, "generic_proxy_repeated_verbatim_outputs": rep,
                  "usage_cost_latency": usage(p, calls[p])}
    unisign = {"label": "Uni-Sign A_official committed predictions: NOT input-matched, reference column only",
               "corpus": p45.corpus(uni, refs)}

    sent = {p: [p45.sent(h, r) for h, r in zip(hyp[p], refs)] for p in hyp}
    dchrf = [o["chrF"] - g["chrF"] for o, g in zip(sent["openai"], sent["gemini"])]
    dwer = [o["WER"] - g["WER"] for o, g in zip(sent["openai"], sent["gemini"])]
    paired = {"delta_sentence_chrF": {"mean": round(statistics.mean(dchrf), 4),
                                      "median": round(statistics.median(dchrf), 4), **wlt(dchrf),
                                      "bootstrap95_case": boot(dchrf), "bootstrap95_signer_cluster": boot(dchrf, signer)},
              "delta_sentence_WER": {"mean": round(statistics.mean(dwer), 4), "median": round(statistics.median(dwer), 4),
                                     "openai_lower": sum(x <= -1 for x in dwer), "openai_higher": sum(x >= 1 for x in dwer),
                                     "ties": sum(abs(x) < 1 for x in dwer)}}
    reg = sum(x <= -10 for x in dchrf); gain = sum(x >= 10 for x in dchrf)

    G, O = arm["gemini"], arm["openai"]
    R = {"non_answers": {"openai": O["non_answer_cases"], "gemini": G["non_answer_cases"]},
         "partial": {"openai": O["status_counts"]["partial"], "gemini": G["status_counts"]["partial"]}}
    R["pass"] = O["non_answer_cases"] <= G["non_answer_cases"] + 1 and \
        O["status_counts"]["partial"] <= G["status_counts"]["partial"] + 1
    d_corpus = O["corpus"]["chrF"] - G["corpus"]["chrF"]
    Q = {"corpus_chrF_delta": round(d_corpus, 4), "ci_lower": paired["delta_sentence_chrF"]["bootstrap95_case"]["lo"],
         "corpus_WER": {"openai": O["corpus"]["WER"], "gemini": G["corpus"]["WER"]}, "gemini_repeat": "not run"}
    Q["conditions"] = {"chrF_delta_ge_2": d_corpus >= 2.0, "ci_lower_gt_0": Q["ci_lower"] > 0,
                       "wer_o_le_g": O["corpus"]["WER"] <= G["corpus"]["WER"]}
    Q["pass"] = all(Q["conditions"].values())
    S = {"regressions": reg, "gains": gain,
         "generic_proxy": {"openai": O["generic_proxy_repeated_verbatim_outputs"],
                           "gemini": G["generic_proxy_repeated_verbatim_outputs"]},
         "blind_review": "not done"}
    S["conditions"] = {"regressions_le_gains": reg <= gain,
                       "generic_o_le_g_automatic_proxy": S["generic_proxy"]["openai"] <= S["generic_proxy"]["gemini"]}
    S["pass"] = all(S["conditions"].values())
    S["provisional"] = True                                   # automatic proxy only, no blind review
    lo, lg = O["usage_cost_latency"]["latency_s"], G["usage_cost_latency"]["latency_s"]
    co, cg = O["usage_cost_latency"]["cost_usd"], G["usage_cost_latency"]["cost_usd"]
    C = {"median_call_latency_s": {"openai": lo and lo["median"], "gemini": lg and lg["median"]},
         "total_cost_usd": {"openai": co, "gemini": cg}}
    C["conditions"] = {"latency_o_le_2g": bool(lo and lg and lo["median"] <= 2 * lg["median"]),
                       "cost_o_le_3g": co <= 3 * cg}
    C["pass"] = all(C["conditions"].values())

    strata = {"multi_batch": [k for k, i in enumerate(ids) if man[i]["n_batches"] > 1]}
    for s in sorted(set(signer), key=int):
        strata[f"signer_proxy_{s}"] = [k for k, x in enumerate(signer) if x == s]
    strata["gemini_nonanswer_loop_or_degenerate"] = [
        k for k in range(len(ids)) if not hyp["gemini"][k].strip() or status["gemini"][k] in NON_ANSWER
        or p45.loop_out(hyp["gemini"][k]) or degen["gemini"][k]]
    strata["unisign_loop_out_or_empty"] = [k for k in range(len(ids)) if p45.loop_out(uni[k]) or not uni[k].strip()]
    Bs = {}
    for name, ks in strata.items():
        d = [dchrf[k] for k in ks]
        e = {"n": len(ks), "eligible_n_ge_5": len(ks) >= 5, "comparator": "gemini"}
        if d:
            e.update(mean_delta_chrF=round(statistics.mean(d), 4), **wlt(d),
                     win_share=round(sum(x >= 1 for x in d) / len(d), 4))
            e["passes"] = len(ks) >= 5 and e["mean_delta_chrF"] >= 5 and e["win_share"] >= 2 / 3
        else:
            e["passes"] = False
        Bs[name] = e
    a_core = R["pass"] and Q["pass"] and S["pass"] and C["pass"]
    if a_core:
        verdict = "A provisional"          # human blind review (key-content errors) missing
    elif R["pass"] and any(e["passes"] for e in Bs.values()):
        verdict = "B"
    else:
        verdict = "C"

    per_case = []
    for k, i in enumerate(ids):
        per_case.append({"clip_id": i, "signer_proxy": signer[k], "n_batches": man[i]["n_batches"],
                         "status": {p: status[p][k] for p in status},
                         "batch_outcomes": {p: [b["outcome"] for b in cases[p][i]["batches"]] for p in cases},
                         "failure_categories": {p: [b["failure_category"] for b in cases[p][i]["batches"]
                                                    if b["failure_category"]] for p in cases},
                         "sentence": {p: sent[p][k] for p in sent}, "unisign_sentence": p45.sent(uni[k], refs[k]),
                         "delta_chrF": round(dchrf[k], 4), "delta_WER": round(dwer[k], 4),
                         "degenerate": {p: degen[p][k] for p in degen},
                         "regression": dchrf[k] <= -10, "gain": dchrf[k] >= 10})
    out = {"stage": "P0-2 Round 1 primary run: comparison (automatic metrics only)",
           "references": "10.13 inputs_128.jsonl (scoring only)", "interpretations_fixed_before_reading_outputs":
           __doc__.split("Interpretations fixed here")[1].split("usage:")[0].strip(),
           "integrity": chk, "arms": arm, "unisign_reference_column": unisign, "paired": paired,
           "regression_gain": {"regressions": reg, "gains": gain, "threshold": "sentence chrF |delta| >= 10"},
           "gates": {"R_reliability": R, "Q_quality": Q, "S_safety": S, "C_cost_latency": C},
           "B_strata": Bs, "verdict": verdict,
           "verdict_note": "A requires human blind review of key-content errors; without it the best possible verdict "
                           "is 'A provisional'. Automatic metrics do not establish semantic superiority.",
           "per_case": per_case}
    (RUN / "comparison.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("integrity", "regression_gain", "verdict")} |
                     {"arms": {p: {k: v for k, v in a.items()} for p, a in arm.items()}, "paired": paired,
                      "gates": {g: {"pass": v["pass"], **{k: v[k] for k in v if k not in ("pass",)}}
                                for g, v in out["gates"].items()}, "B_strata": Bs,
                      "unisign": unisign["corpus"]}, indent=1))


if __name__ == "__main__":
    main()
