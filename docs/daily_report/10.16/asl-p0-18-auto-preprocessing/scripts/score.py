"""P0-18: translation metrics for several conditions on the same clips, plus paired video-cluster bootstrap deltas.

BLEU-4: Uni-Sign SLRT_metrics.sableu (the P0-12 / E0 path, 13a). chrF: sacrebleu corpus_chrf. Bootstrap resamples
use per-sentence sufficient statistics (sacrebleu BLEU / CHRF), asserted equal to sableu / corpus_chrf on the full
set. WER: the P0-12 word-level edit distance (sum of edits / sum of reference words). Length ratio: hypothesis words /
reference words. BLEURT is not computed (not installed locally).

Usage: python -I score.py --refs REFS_JSON --ids IDS.txt --out OUT.json [--B 2000] [--pairs X-Y,...] NAME=preds.jsonl ...
       REFS_JSON: {clip_id: {"ref": str, "video": str}}
"""
import argparse, json, os, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--refs", required=True)
ap.add_argument("--ids", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--B", type=int, default=2000)
ap.add_argument("--seed", type=int, default=20261016)
ap.add_argument("--pairs", default="")
ap.add_argument("systems", nargs="+")
a = ap.parse_args()
sys.path.insert(0, os.environ.get("UNISIGN_REPO", os.path.expanduser("~/Desktop/curify/p014-work/Uni-Sign")))
from SLRT_metrics import sableu  # noqa: E402
import sacrebleu  # noqa: E402
from sacrebleu.metrics import BLEU, CHRF  # noqa: E402

REF = json.load(open(a.refs)); ids = open(a.ids).read().split()
refs = [REF[i]["ref"] for i in ids]; vids = [REF[i]["video"] for i in ids]
_bleu, _chrf = BLEU(tokenize="13a"), CHRF()


def wer_counts(h, r):
    h = h.lower().split(); r = r.lower().split(); d = np.arange(len(h) + 1)
    for i in range(1, len(r) + 1):
        prev = d.copy(); d[0] = i
        for j in range(1, len(h) + 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (r[i - 1] != h[j - 1]))
    return int(d[len(h)]), len(r)


def stats(H):
    return {"bleu": np.array(_bleu._extract_corpus_statistics(H, [refs]), dtype=np.int64),
            "chrf": np.array(_chrf._extract_corpus_statistics(H, [refs]), dtype=np.int64),
            "wer": np.array([wer_counts(h, r) for h, r in zip(H, refs)], dtype=np.int64),
            "len": np.array([[len(h.split()), len(r.split())] for h, r in zip(H, refs)], dtype=np.int64)}


def from_stats(st, w):
    """w: per-clip multiplicity (bootstrap weights) -> metrics."""
    b = (st["bleu"] * w[:, None]).sum(0); c = (st["chrf"] * w[:, None]).sum(0)
    e = (st["wer"] * w[:, None]).sum(0); ln = (st["len"] * w[:, None]).sum(0)
    return {"bleu4": float(_bleu._compute_score_from_stats(list(b)).score),
            "chrf": float(_chrf._compute_score_from_stats(list(c)).score),
            "wer": 100.0 * e[0] / max(1, e[1]), "len_ratio": ln[0] / max(1, ln[1])}


sysd, S = {}, {}
for s in a.systems:
    name, path = s.split("=", 1)
    P = {}
    for l in open(path):
        j = json.loads(l); P[j["clip_id"]] = j["pred"]
    missing = [i for i in ids if i not in P]
    assert not missing, f"{name}: {len(missing)} missing"
    sysd[name] = [P[i] for i in ids]; S[name] = stats(sysd[name])

ones = np.ones(len(ids), dtype=np.int64)
point = {}
for n, H in sysd.items():
    m = from_stats(S[n], ones)
    off = float(sableu(references=refs, hypotheses=H, tokenizer="13a")["bleu4"])
    assert abs(off - m["bleu4"]) < 1e-9, (n, off, m["bleu4"])
    assert abs(float(sacrebleu.corpus_chrf(H, [refs]).score) - m["chrf"]) < 1e-9
    point[n] = m
res = {"n_clips": len(ids), "n_videos": len(set(vids)), "sacrebleu_version": sacrebleu.__version__, "point": point,
       "bootstrap": {"B": a.B, "seed": a.seed, "unit": "source video"}, "paired_delta": {}}
uv = sorted(set(vids)); vidx = np.array([uv.index(v) for v in vids])
rng = np.random.default_rng(a.seed)
W = []
for _ in range(a.B):
    cnt = np.bincount(rng.integers(0, len(uv), len(uv)), minlength=len(uv))
    W.append(cnt[vidx])
for pr in [p for p in a.pairs.split(",") if p]:
    x, y = pr.split("-", 1)
    dpt = {m: point[y][m] - point[x][m] for m in ("bleu4", "chrf", "wer", "len_ratio")}
    bs = {m: [] for m in dpt}
    for w in W:
        mx, my = from_stats(S[x], w), from_stats(S[y], w)
        for m in dpt:
            bs[m].append(my[m] - mx[m])
    res["paired_delta"][f"{y} - {x}"] = {m: {"delta": dpt[m], "ci95": [float(np.percentile(bs[m], 2.5)),
                                                                       float(np.percentile(bs[m], 97.5))]}
                                         for m in dpt}
json.dump(res, open(a.out, "w"), indent=1)
print(json.dumps(point, indent=1))
for k, v in res["paired_delta"].items():
    print(k, {m: (round(x["delta"], 2), [round(c, 2) for c in x["ci95"]]) for m, x in v.items()})
