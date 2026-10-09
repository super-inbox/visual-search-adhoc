"""P0-11 copy of P0-13 scripts/compare_arms.py (unchanged logic): paired bootstrap of B - A on the same clips."""
"""P0-13: paired comparison baseline vs treatment on the same clips (corpus BLEU / chrF / WER).
Paired bootstrap over clips (10k resamples, seed 0) of treatment - baseline.
Usage: python compare_arms.py BASE_PRED_JSON TREAT_PRED_JSON [P012_PER_CLIP_CSV] -> JSON on stdout
Both prediction files are lists of {sample_id|id, reference, prediction}."""
import csv, json, sys
import numpy as np
import sacrebleu, jiwer


def load(p):
    rows = json.load(open(p))
    if isinstance(rows, dict):
        rows = rows["predictions"]
    return {r.get("sample_id", r.get("id")): r for r in rows}


def corpus(refs, hyps):
    hyps = [h if h.strip() else " " for h in hyps]
    return {"bleu": sacrebleu.corpus_bleu(hyps, [refs]).score, "chrf": sacrebleu.corpus_chrf(hyps, [refs]).score,
            "wer": jiwer.wer(refs, hyps)}


def compare(ids, A, B, n_boot=10000):
    refs = [A[i]["reference"] for i in ids]
    assert refs == [B[i]["reference"] for i in ids], "reference mismatch between arms"
    ha, hb = [A[i]["prediction"] for i in ids], [B[i]["prediction"] for i in ids]
    a, b = corpus(refs, ha), corpus(refs, hb)
    rng = np.random.default_rng(0)
    d = {"bleu": [], "chrf": []}
    n = len(ids)
    for _ in range(n_boot):
        s = rng.integers(0, n, n)
        r = [refs[j] for j in s]
        x, y = [ha[j] or " " for j in s], [hb[j] or " " for j in s]
        d["bleu"].append(sacrebleu.corpus_bleu(y, [r]).score - sacrebleu.corpus_bleu(x, [r]).score)
        d["chrf"].append(sacrebleu.corpus_chrf(y, [r]).score - sacrebleu.corpus_chrf(x, [r]).score)
    ci = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in d.items()}
    return {"n": n, "baseline": a, "treatment": b, "delta": {k: b[k] - a[k] for k in a}, "bootstrap95_delta": ci}


if __name__ == "__main__":
    A, B = load(sys.argv[1]), load(sys.argv[2])
    ids = [i for i in A if i in B]
    out = {"all": compare(ids, A, B, int(sys.argv[4]) if len(sys.argv) > 4 else 10000)}
    if len(sys.argv) > 3 and sys.argv[3] != "-":
        iou = {r["clip_id"]: float(r["segment_iou_ours_vs_realigned"]) for r in csv.DictReader(open(sys.argv[3]))}
        for name, f in (("iou_ge_0.5", lambda v: v >= 0.5), ("iou_lt_0.5", lambda v: v < 0.5)):
            sub = [i for i in ids if i in iou and f(iou[i])]
            out[name] = compare(sub, A, B, 2000)
    print(json.dumps(out, indent=1))
