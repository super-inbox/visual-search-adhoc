"""P0-16: freeze the How2Sign-val confirmatory holdout (HOLDOUT_PLAN.md §3).

Reads only: the three How2Sign re-aligned reference CSVs (for automated duplicate screening; no sentence is printed or
written), video names / ids, and holdout/crop_val_index.tsv. Never reads any model output. No val prediction exists.

Writes holdout/: EXCLUDED.csv, H18_{units,clips}.txt, H19_{units,clips}.txt, units.json, SPLIT_LOG.json,
HOLDOUT.sha256.

Usage: python3 -I build_holdout.py
"""
import collections, csv, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
OUT = os.path.join(EXP, "holdout")
P014 = os.path.join(os.path.dirname(os.path.dirname(EXP)), "10.15", "asl-unisign-representation-probe")
RAW = os.path.expanduser("~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/"
                         "landmark_t5_1pct/local_run_10pct/raw_download")
csvs = [os.path.join(RAW, f"how2sign_realigned_{s}.csv") for s in ("train", "val", "test")]

# the frozen P0-14 text helpers (top half of build_concepts.py, executed as-is; nothing is written by it)
src = open(os.path.join(P014, "scripts", "build_concepts.py")).read()
src = src.split("# ---------------------------------------------------------------- per-clip annotations")[0]
g = {"__name__": "bc"}; argv = sys.argv; sys.argv = ["bc", *csvs, "/nonexistent"]
exec(compile(src, "build_concepts.py", "exec"), g); sys.argv = argv
norm, sp = g["norm_sentence"], g["signer_proxy"]
train, val, test = g["splits"]["train"], g["splits"]["val"], g["splits"]["test"]
assert len(val) == 1741 and len(test) == 2357

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def grams(ws, n=4):                       # identical to build_concepts.py
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}

def dup_index(rows):
    exact = {norm(r["SENTENCE"]) for r in rows}
    gi, gl = collections.defaultdict(set), []
    for i, r in enumerate(rows):
        gg = grams(norm(r["SENTENCE"]).split()); gl.append(gg)
        for x in gg:
            gi[x].add(i)
    return exact, gi

def dup_kind(sent, idx):                  # P0-14 rule: exact normalised match, or >= 50 % of 4-grams in ONE sentence
    exact, gi = idx
    ns = norm(sent); ws = ns.split()
    if ns in exact:
        return "exact"
    if len(ws) >= 6:
        gg = grams(ws)
        hits = collections.Counter(j for x in gg for j in gi.get(x, ()))
        if hits and hits.most_common(1)[0][1] / len(gg) >= 0.5:
            return "near"
    return ""

crop = {os.path.splitext(os.path.basename(l.split("\t")[0]))[0]
        for l in open(os.path.join(OUT, "crop_val_index.tsv")).read().splitlines()[1:]}
I_train, I_test = dup_index(train), dup_index(test)
excl, keep = [], []
for r in val:
    c = r["SENTENCE_NAME"]
    reasons = []
    if c not in crop:
        reasons.append("no_official_crop_video")
    k = dup_kind(r["SENTENCE"], I_train)
    if k:
        reasons.append(f"{k}_dup_of_train")
    k = dup_kind(r["SENTENCE"], I_test)
    if k:
        reasons.append(f"{k}_dup_of_test")
    (excl if reasons else keep).append((r, ";".join(reasons)))

# units: val videos, merged when kept clips share an identical normalised sentence across videos
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
by_sent = collections.defaultdict(set)
for r, _ in keep:
    find(r["VIDEO_ID"]); by_sent[norm(r["SENTENCE"])].add(r["VIDEO_ID"])
merged = sorted(sorted(v) for v in by_sent.values() if len(v) > 1)
for v in merged:
    for x in v[1:]:
        parent[find(x)] = find(v[0])
members = collections.defaultdict(set)
for v in parent:
    members[find(v)].add(v)
unit_of = {v: "+".join(sorted(members[find(v)])) for v in parent}
clips_of = collections.defaultdict(list)
for r, _ in keep:
    clips_of[unit_of[r["VIDEO_ID"]]].append(r)
units = sorted(clips_of)
NC = {u: len(clips_of[u]) for u in units}
def stratum(u):
    cnt = collections.Counter(int(sp(r["VIDEO_NAME"])) for r in clips_of[u]); top = max(cnt.values())
    return min(s for s, n in cnt.items() if n == top)
S = {u: stratum(u) for u in units}
n_keep = len(keep)

def assign(seed):                          # label-free: strata by signer proxy, sort by clip count, serpentine
    import random
    rng = random.Random(seed)
    A = set()
    for si, s in enumerate(sorted(set(S.values()))):
        us = sorted(u for u in units if S[u] == s)
        rng.shuffle(us)
        us = sorted(us, key=lambda u: -NC[u])                     # stable
        pat = ["H18", "H19", "H19", "H18"] if si % 2 == 0 else ["H19", "H18", "H18", "H19"]
        for j, u in enumerate(us):
            if pat[j % 4] == "H18":
                A.add(u)
    return A

log, chosen = [], None
for seed in range(16, 116):
    A = assign(seed)
    share = sum(NC[u] for u in A) / n_keep
    strata_ok = all(any(S[u] == s for u in A) and any(S[u] == s for u in units if u not in A)
                    for s in set(S.values()) if sum(1 for u in units if S[u] == s) >= 2)
    ok = bool(0.45 <= share <= 0.55 and strata_ok)
    log.append({"seed": seed, "H18_clip_share": round(share, 4), "strata_on_both_sides": strata_ok, "pass": ok})
    if ok:
        chosen = seed
        break
assert chosen is not None
A = assign(chosen); B = set(units) - A

def wl(name, items):
    with open(os.path.join(OUT, name), "w") as f:
        f.write("".join(x + "\n" for x in items))
wl("H18_units.txt", sorted(A)); wl("H19_units.txt", sorted(B))
wl("H18_clips.txt", sorted(r["SENTENCE_NAME"] for r, _ in keep if unit_of[r["VIDEO_ID"]] in A))
wl("H19_clips.txt", sorted(r["SENTENCE_NAME"] for r, _ in keep if unit_of[r["VIDEO_ID"]] in B))
with open(os.path.join(OUT, "EXCLUDED.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["clip_id", "video_id", "reason"])
    for r, why in sorted(excl, key=lambda x: x[0]["SENTENCE_NAME"]):
        w.writerow([r["SENTENCE_NAME"], r["VIDEO_ID"], why])
json.dump({"unit_of_video": unit_of}, open(os.path.join(OUT, "units.json"), "w"), indent=1)
reasons = collections.Counter(x for _, why in excl for x in why.split(";"))
excl_videos_entirely = sorted({r["VIDEO_ID"] for r, _ in excl} - {r["VIDEO_ID"] for r, _ in keep})
summary = {
    "val_clips": len(val), "val_videos": len({r["VIDEO_ID"] for r in val}),
    "excluded_clips": len(excl), "exclusion_reasons": dict(reasons),
    "videos_lost_entirely": len(excl_videos_entirely),
    "kept_clips": n_keep, "units": len(units), "merged_units": merged,
    "seeds_tried": log, "chosen_seed": chosen,
    "H18": {"units": len(A), "videos": sum(len(u.split("+")) for u in A), "clips": sum(NC[u] for u in A),
            "strata": dict(sorted(collections.Counter(S[u] for u in A).items()))},
    "H19": {"units": len(B), "videos": sum(len(u.split("+")) for u in B), "clips": sum(NC[u] for u in B),
            "strata": dict(sorted(collections.Counter(S[u] for u in B).items()))},
    "signer_proxies_in_val": sorted({int(sp(r["VIDEO_NAME"])) for r in val}),
    "inputs_sha256": {os.path.basename(p): sha(p) for p in csvs + [os.path.join(OUT, "crop_val_index.tsv")]},
}
json.dump(summary, open(os.path.join(OUT, "SPLIT_LOG.json"), "w"), indent=1)
names = ["crop_val_index.tsv", "EXCLUDED.csv", "H18_units.txt", "H18_clips.txt", "H19_units.txt", "H19_clips.txt",
         "units.json", "SPLIT_LOG.json"]
with open(os.path.join(OUT, "HOLDOUT.sha256"), "w") as f:
    f.write("".join(f"{sha(os.path.join(OUT, n))}  {n}\n" for n in names))
print(json.dumps({k: summary[k] for k in ("val_clips", "excluded_clips", "exclusion_reasons", "videos_lost_entirely",
                                          "kept_clips", "units", "chosen_seed", "H18", "H19",
                                          "signer_proxies_in_val")}, indent=1))
print("merged unit groups:", len(merged))
