"""P0-15 §7: source-video-level dev/final split of the 2,209 test_clean clips, plus the 5 dev folds.

Uses only: video ids, signer proxies, clip counts, normalised reference sentences (to merge videos that share a
sentence) and Tier L reference-positive COUNTS. Never reads translations or probe scores.

Usage: python -I build_split.py
"""
import collections, csv, json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import P014, EXP, REF_CSV_DIR, sha256, jdump  # noqa: E402

OUT = os.path.join(EXP, "split")
concepts = [c for c in csv.DictReader(open(os.path.join(P014, "concepts", "concept_list_v1.csv")))]
L = [c["concept"] for c in concepts if c["tier"] == "L"]
assert len(L) == 24
man = [r for r in csv.DictReader(open(os.path.join(P014, "splits", "manifest.csv"))) if r["role"] == "test_clean"]
assert len(man) == 2209

# ---- units: videos, merged when they share an identical normalised reference sentence (union-find)
ref = {r["SENTENCE_NAME"]: r["SENTENCE"]
       for r in csv.DictReader(open(os.path.join(REF_CSV_DIR, "how2sign_realigned_test.csv"), encoding="utf-8"),
                               delimiter="\t")}
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
by_sent = collections.defaultdict(set)
for r in man:
    find(r["video_id"]); by_sent[norm(ref[r["clip_id"]])].add(r["video_id"])
merged = [sorted(v) for v in by_sent.values() if len(v) > 1]
for v in merged:
    for x in v[1:]:
        parent[find(x)] = find(v[0])
unit_of_video = {v: "+".join(sorted(w for w in parent if find(w) == find(v))) for v in parent}
assert merged == [["G3di9jJTqDs", "f_zna_wG3zo"]], merged      # the one pair found in the design check
units = sorted(set(unit_of_video.values()))
assert len(units) == 148

clips_of = collections.defaultdict(list)
for r in man:
    clips_of[unit_of_video[r["video_id"]]].append(r)
def stratum(u):
    c = collections.Counter(int(r["signer_proxy"]) for r in clips_of[u])
    top = max(c.values())
    return min(s for s, n in c.items() if n == top)
S = {u: stratum(u) for u in units}
W = {u: sum(int(r[k]) for r in clips_of[u] for k in L) for u in units}
NC = {u: len(clips_of[u]) for u in units}
POS = {u: np.array([sum(int(r[k]) for r in clips_of[u]) for k in L]) for u in units}
tot_pos = sum(POS.values())

def assign(seed):
    rng = np.random.default_rng(seed)
    dev = set()
    for si, s in enumerate(sorted(set(S.values()))):
        us = [u for u in units if S[u] == s]
        us = [us[i] for i in rng.permutation(len(us))]
        us = sorted(us, key=lambda u: -W[u])                       # stable
        pat = ["dev", "final", "final", "dev"] if si % 2 == 0 else ["final", "dev", "dev", "final"]
        for j, u in enumerate(us):
            if pat[j % 4] == "dev":
                dev.add(u)
    return dev

log = []
chosen = None
for seed in range(15, 115):
    dev = assign(seed)
    clip_share = sum(NC[u] for u in dev) / len(man)
    pos_share = sum(POS[u] for u in dev) / tot_pos
    ok = bool(0.45 <= clip_share <= 0.55 and np.all((pos_share >= 0.25) & (pos_share <= 0.75)))
    log.append({"seed": seed, "dev_clip_share": round(clip_share, 4),
                "min_concept_dev_pos_share": round(float(pos_share.min()), 4),
                "max_concept_dev_pos_share": round(float(pos_share.max()), 4), "pass": ok})
    if ok:
        chosen = seed
        break
assert chosen is not None, "no seed in 15..114 passes the balance check"
dev = assign(chosen)
final = set(units) - dev

# ---- dev folds: units by clip count desc (ties by id), greedily to the fold with fewest clips (ties lowest index)
folds, load = {}, [0] * 5
for u in sorted(dev, key=lambda u: (-NC[u], u)):
    f = min(range(5), key=lambda i: (load[i], i))
    folds[u] = f; load[f] += NC[u]

os.makedirs(OUT, exist_ok=True)
def wl(name, items):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write("".join(x + "\n" for x in items))
wl("dev_units.txt", sorted(dev)); wl("final_units.txt", sorted(final))
wl("dev_clips.txt", [r["clip_id"] for r in man if unit_of_video[r["video_id"]] in dev])
wl("final_clips.txt", [r["clip_id"] for r in man if unit_of_video[r["video_id"]] in final])
jdump({"folds": {u: folds[u] for u in sorted(folds)}, "fold_clips": load}, os.path.join(OUT, "dev_folds.json"))
jdump({"unit_of_video": unit_of_video}, os.path.join(OUT, "units.json"))

pos_dev = sum(POS[u] for u in dev)
summary = {
    "seeds_tried": log, "chosen_seed": chosen, "n_units": len(units), "merged_units": merged,
    "dev": {"units": len(dev), "clips": sum(NC[u] for u in dev), "tierL_positives": int(pos_dev.sum())},
    "final": {"units": len(final), "clips": sum(NC[u] for u in final),
              "tierL_positives": int((tot_pos - pos_dev).sum())},
    "per_concept_dev_pos_share": {k: round(float(pos_dev[i] / tot_pos[i]), 4) for i, k in enumerate(L)},
    "strata_units": {str(s): {"dev": sum(1 for u in dev if S[u] == s), "final": sum(1 for u in final if S[u] == s)}
                     for s in sorted(set(S.values()))},
    "fold_clips": load,
}
jdump(summary, os.path.join(OUT, "SPLIT_LOG.json"))
names = ["dev_units.txt", "final_units.txt", "dev_clips.txt", "final_clips.txt", "dev_folds.json", "units.json",
         "SPLIT_LOG.json"]
with open(os.path.join(OUT, "SPLIT.sha256"), "w") as fh:
    fh.write("".join(f"{sha256(os.path.join(OUT, n))}  {n}\n" for n in names))
print(json.dumps({k: summary[k] for k in ("chosen_seed", "dev", "final", "strata_units", "fold_clips")}, indent=1))
print("seeds tried:", len(log))
