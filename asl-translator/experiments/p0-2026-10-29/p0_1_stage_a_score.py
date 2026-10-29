#!/usr/bin/env python3
"""P0-1 Stage A scoring: keypoint vs hand-RGB recognizer on the same human-confirmed spans. No model call.

Inputs (all supplied later; nothing real exists yet):
  --labels       blind Step-1 label CSV (schema: results/p0_1_stage_a_preregistration.json label_fields)
  --candidates   results/p0_1_stage_a_candidate_set.json (blind_id -> source video, probe window)
  --pred-kp      keypoint recognizer predictions JSONL
  --pred-rgb     RGB recognizer predictions JSONL
  --unisign      optional JSON {clip_id: Uni-Sign A_official output} for the already-correct control subgroup
Prediction rows: {"blind_id", "span_no", "letters" (raw string or null), "abstain" (bool), "abstain_reason",
                  "candidates" (optional list), "runtime_s", ...}. span_no 0 = the probe window of a negative item.

Model self-confidence is never read. Thresholds come from the frozen pre-registration and are not arguments.

usage:
  python3 -I p0_1_stage_a_score.py --labels L.csv --candidates C.json --pred-kp K.jsonl --pred-rgb R.jsonl --out O.json
  python3 -I p0_1_stage_a_score.py --self-test        (synthetic fixtures only)
"""
import argparse, csv, json, re, statistics
from collections import Counter
from pathlib import Path

import numpy as np

SEED, B = 20261029, 10_000
G = {"min_pos": 12, "min_neg": 8, "cer_margin": 0.10, "fpr_margin": 0.10, "drop_top": 2, "win_ratio": 1.5,
     "tie": 0.05, "fp_min_letters": 2, "readable_cer": 0.35, "readable_word": 0.30}


def norm(s):
    return re.sub(r"[^a-z?]", "", (s or "").lower())


def align(hyp, ref):
    """Levenshtein with '?' in ref matching any letter. Returns (edits, substitution pairs)."""
    n, m = len(ref), len(hyp)
    d = np.zeros((n + 1, m + 1), int); d[:, 0] = range(n + 1); d[0, :] = range(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = 0 if ref[i - 1] in ("?", hyp[j - 1]) else 1
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + c)
    subs, i, j = [], n, m
    while i > 0 and j > 0:
        c = 0 if ref[i - 1] in ("?", hyp[j - 1]) else 1
        if d[i, j] == d[i - 1, j - 1] + c:
            if c:
                subs.append((ref[i - 1], hyp[j - 1]))
            i, j = i - 1, j - 1
        elif d[i, j] == d[i - 1, j] + 1:
            i -= 1
        else:
            j -= 1
    return int(d[n, m]), subs


def word_equal(hyp, ref):
    return len(hyp) == len(ref) and all(r in ("?", h) for h, r in zip(hyp, ref))


def load_labels(rows):
    items = {}
    for r in rows:
        it = items.setdefault(r["blind_id"], {"present": r["fingerspelling_present"].strip().lower(), "spans": []})
        if it["present"] == "yes" and r.get("letters", "").strip():
            it["spans"].append({"span_no": int(r["span_no"]), "letters": norm(r["letters"]),
                                "confidence": r["letters_confidence"].strip().lower(),
                                "start": float(r["span_start_s"]), "end": float(r["span_end_s"])})
    return items


def build_units(labels, cands):
    pos, neg, unc = [], [], []
    for bid, it in labels.items():
        c = cands[bid]
        if it["present"] == "yes":
            for s in it["spans"]:
                (pos if s["confidence"] in ("high", "medium") and s["letters"] else unc).append(
                    {"blind_id": bid, "span_no": s["span_no"], "ref": s["letters"], "cluster": c["source_video_id"],
                     "clip_id": c["clip_id"], "tier": c["selection_tier"], "dev45": c["dev45_review_id"] is not None})
        elif it["present"] == "no":
            neg.append({"blind_id": bid, "span_no": 0, "cluster": c["source_video_id"], "tier": c["selection_tier"]})
        else:
            unc.append({"blind_id": bid})
    return pos, neg, unc


def recognizer_metrics(pos, neg, pred):
    edits = refl = exact = abst_p = 0; per = {}; subs = Counter(); rt = []
    for u in pos:
        p = pred.get((u["blind_id"], u["span_no"]), {"letters": None, "abstain": True, "abstain_reason": "missing"})
        h = "" if p.get("abstain") else norm(p.get("letters"))
        abst_p += bool(p.get("abstain") or not h)
        e, sb = align(h, u["ref"]); edits += e; refl += len(u["ref"]); subs.update(sb)
        exact += word_equal(h, u["ref"])
        per[(u["blind_id"], u["span_no"])] = e / max(len(u["ref"]), 1)
        if p.get("runtime_s") is not None:
            rt.append(p["runtime_s"])
    fp = abst_n = 0
    for u in neg:
        p = pred.get((u["blind_id"], 0), {"letters": None, "abstain": True})
        h = "" if p.get("abstain") else norm(p.get("letters"))
        abst_n += bool(p.get("abstain") or not h); fp += len(h) >= G["fp_min_letters"]
    n = max(len(pos), 1)
    return {"CER": round(edits / max(refl, 1), 4), "word_exact": round(exact / n, 4),
            "abstain_rate_pos": round(abst_p / n, 4), "abstain_rate_neg": round(abst_n / max(len(neg), 1), 4),
            "coverage_pos": round(1 - abst_p / n, 4), "fpr_negatives": round(fp / max(len(neg), 1), 4),
            "n_pos": len(pos), "n_neg": len(neg), "ref_letters": refl,
            "top_confusions": [[f"{a}->{b}", c] for (a, b), c in subs.most_common(10)],
            "runtime_s": {"median": statistics.median(rt), "max": max(rt)} if rt else None,
            "_per_span_cer": per, "_edits": edits}


def boot_ci(diffs, clusters):
    rng = np.random.default_rng(SEED); d = np.asarray(diffs); keys = sorted(set(clusters))
    idx = {k: np.where(np.asarray(clusters) == k)[0] for k in keys}
    m = np.array([d[np.concatenate([idx[keys[k]] for k in rng.integers(0, len(keys), len(keys))])].mean()
                  for _ in range(B)])
    lo, hi = np.percentile(m, [2.5, 97.5])
    return {"lo": round(float(lo), 4), "hi": round(float(hi), 4), "resamples": B, "seed": SEED}


def gates(pos, neg, kp, rgb):
    keys = [(u["blind_id"], u["span_no"]) for u in pos]
    diff = [rgb["_per_span_cer"][k] - kp["_per_span_cer"][k] for k in keys]
    out = {"G0_validity": len(pos) >= G["min_pos"] and len(neg) >= G["min_neg"]}
    paired = {"mean_delta_cer": round(float(np.mean(diff)), 4) if diff else None,
              "wins_rgb": sum(x <= -G["tie"] for x in diff), "losses_rgb": sum(x >= G["tie"] for x in diff),
              "ties": sum(abs(x) < G["tie"] for x in diff)}
    paired["bootstrap95_cluster"] = boot_ci(diff, [u["cluster"] for u in pos]) if diff else None
    out["G1_cer"] = bool(diff) and rgb["CER"] <= kp["CER"] - G["cer_margin"] and paired["bootstrap95_cluster"]["hi"] < 0
    out["G2_word"] = rgb["word_exact"] >= kp["word_exact"]
    out["G3_false_positives"] = rgb["fpr_negatives"] <= kp["fpr_negatives"] + G["fpr_margin"]
    gain = sorted(range(len(keys)), key=lambda i: diff[i])[:G["drop_top"]]            # most negative = largest gain
    keep = [i for i in range(len(keys)) if i not in gain]
    reflen = {(u["blind_id"], u["span_no"]): max(len(u["ref"]), 1) for u in pos}
    cer_k = lambda r, ii: sum(r["_per_span_cer"][keys[i]] * reflen[keys[i]] for i in ii) / max(sum(reflen[keys[i]] for i in ii), 1)
    out["G4_breadth"] = bool(keep) and cer_k(rgb, keep) < cer_k(kp, keep) and \
        paired["wins_rgb"] >= G["win_ratio"] * paired["losses_rgb"]
    best = min((kp, rgb), key=lambda r: r["CER"])
    out["readable_at_known_spans"] = best["CER"] <= G["readable_cer"] and best["word_exact"] >= G["readable_word"]
    if not out["G0_validity"]:
        verdict = "INSUFFICIENT_LABELS"
    elif all(out[g] for g in ("G1_cer", "G2_word", "G3_false_positives", "G4_breadth")):
        verdict = "RGB_ADDS_VALUE"
    else:
        verdict = "NO_RGB_GAIN"
    return out, paired, verdict


def score(label_rows, cands, pred_kp, pred_rgb, unisign=None):
    pos, neg, unc = build_units(load_labels(label_rows), cands)
    kp, rgb = recognizer_metrics(pos, neg, pred_kp), recognizer_metrics(pos, neg, pred_rgb)
    g, paired, verdict = gates(pos, neg, kp, rgb)
    per_case = [{"blind_id": u["blind_id"], "span_no": u["span_no"], "tier": u["tier"], "dev45": u["dev45"],
                 "cer_kp": round(kp["_per_span_cer"][(u["blind_id"], u["span_no"])], 4),
                 "cer_rgb": round(rgb["_per_span_cer"][(u["blind_id"], u["span_no"])], 4),
                 "unisign_already_correct": (None if unisign is None else
                                             u["ref"] in re.findall(r"[a-z]+", (unisign.get(u["clip_id"]) or "").lower()))}
                for u in pos]
    sub = {}
    if unisign is not None:
        ctrl = [u for u, c in zip(pos, per_case) if c["unisign_already_correct"]]
        sub["unisign_already_correct_controls"] = {"n": len(ctrl), "kp": recognizer_metrics(ctrl, [], pred_kp)["CER"],
                                                   "rgb": recognizer_metrics(ctrl, [], pred_rgb)["CER"]}
    clean = lambda r: {k: v for k, v in r.items() if not k.startswith("_")}
    return {"n_positive_spans": len(pos), "n_negative_items": len(neg), "n_uncertain": len(unc),
            "keypoint": clean(kp), "rgb": clean(rgb), "paired": paired, "gates": g, "verdict": verdict,
            "subgroups": sub, "per_case": per_case, "thresholds": G,
            "note": "Stage A is diagnostic on human spans; not an end-to-end or translation result"}


def self_test():
    """Synthetic fixtures only (letters are invented strings, not real labels or predictions)."""
    assert align("hello", "hello")[0] == 0 and align("helo", "hello")[0] == 1 and align("", "abc")[0] == 3
    assert align("hxllo", "h?llo")[0] == 0 and word_equal("hxllo", "h?llo") and not word_equal("hell", "hello")
    assert norm("Ab C-d!") == "abcd"
    rng = np.random.default_rng(0)
    words = ["".join(rng.choice(list("abcdefghijklmnopqrstuvwxyz"), rng.integers(3, 8))) for _ in range(16)]
    cands = {f"FSA-{i:03d}": {"source_video_id": f"V{i}", "clip_id": f"C{i}", "selection_tier": "random",
                              "dev45_review_id": None} for i in range(1, 27)}
    rows = [{"blind_id": f"FSA-{i:03d}", "span_no": "1", "fingerspelling_present": "yes", "letters": w,
             "letters_confidence": "high", "span_start_s": "0.5", "span_end_s": "1.5"} for i, w in enumerate(words, 1)]
    rows += [{"blind_id": f"FSA-{i:03d}", "span_no": "1", "fingerspelling_present": "no", "letters": "",
              "letters_confidence": "", "span_start_s": "", "span_end_s": ""} for i in range(17, 27)]

    def corrupt(w, k):
        w = list(w)
        for j in range(min(k, len(w))):
            w[j] = "z" if w[j] != "z" else "y"
        return "".join(w)
    # scenario 1: RGB clearly better on many spans, equal FP -> RGB_ADDS_VALUE
    kp = {(f"FSA-{i:03d}", 1): {"letters": corrupt(w, 2), "abstain": False, "runtime_s": 1.0} for i, w in enumerate(words, 1)}
    rgb = {(f"FSA-{i:03d}", 1): {"letters": w, "abstain": False, "runtime_s": 2.0} for i, w in enumerate(words, 1)}
    for i in range(17, 27):
        kp[(f"FSA-{i:03d}", 0)] = {"letters": "ab" if i < 19 else "", "abstain": i >= 19}
        rgb[(f"FSA-{i:03d}", 0)] = {"letters": "ab" if i < 19 else "", "abstain": i >= 19}
    r1 = score(rows, cands, kp, rgb)
    assert r1["verdict"] == "RGB_ADDS_VALUE", r1["gates"]
    # scenario 2: gain driven by two spans only -> breadth fails -> NO_RGB_GAIN
    rgb2 = {k: dict(v) for k, v in kp.items()}
    rgb2[("FSA-001", 1)] = {"letters": words[0], "abstain": False}; rgb2[("FSA-002", 1)] = {"letters": words[1], "abstain": False}
    r2 = score(rows, cands, kp, rgb2)
    assert r2["verdict"] == "NO_RGB_GAIN" and not r2["gates"]["G4_breadth"], r2["gates"]
    # scenario 3: RGB better letters but many false positives on negatives -> G3 fails
    rgb3 = {k: dict(v) for k, v in rgb.items()}
    for i in range(17, 27):
        rgb3[(f"FSA-{i:03d}", 0)] = {"letters": "abc", "abstain": False}
    r3 = score(rows, cands, kp, rgb3)
    assert not r3["gates"]["G3_false_positives"] and r3["verdict"] == "NO_RGB_GAIN"
    # scenario 4: too few labels -> INSUFFICIENT_LABELS; abstain counts as all-deletions
    r4 = score(rows[:5] + rows[16:20], cands, kp, rgb)
    assert r4["verdict"] == "INSUFFICIENT_LABELS"
    kp_ab = {k: {"letters": None, "abstain": True, "abstain_reason": "insufficient_hand_observations"} for k in kp}
    r5 = score(rows, cands, kp_ab, rgb)
    assert r5["keypoint"]["CER"] == 1.0 and r5["keypoint"]["abstain_rate_pos"] == 1.0
    # scenario 6: self-confidence is ignored
    rgb6 = {k: {**v, "confidence": 0.0} for k, v in rgb.items()}
    assert score(rows, cands, kp, rgb6)["rgb"]["CER"] == r1["rgb"]["CER"]
    print(json.dumps({"self_test": "pass", "scenarios": {"rgb_adds_value": r1["verdict"],
                                                         "gain_from_two_spans": r2["verdict"],
                                                         "rgb_false_positives": r3["verdict"],
                                                         "too_few_labels": r4["verdict"],
                                                         "abstain_scored_as_deletions": r5["keypoint"]["CER"],
                                                         "confidence_ignored": True}}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    for k in ("--labels", "--candidates", "--pred-kp", "--pred-rgb", "--unisign", "--out"):
        ap.add_argument(k, type=Path)
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    cands = {i["blind_id"]: i for i in json.loads(a.candidates.read_text())["items"]}
    rd = lambda p: {(r["blind_id"], int(r["span_no"])): r for r in map(json.loads, p.read_text().splitlines()) if r}
    res = score(list(csv.DictReader(open(a.labels))), cands, rd(a.pred_kp), rd(a.pred_rgb),
                json.loads(a.unisign.read_text()) if a.unisign else None)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("n_positive_spans", "n_negative_items", "gates", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
