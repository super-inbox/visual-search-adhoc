"""P0-15 §2–§5: build the (clip, Tier L concept) cell table from frozen P0-14 artifacts.

Writes  WORK/cells_dev.csv.gz            (features, D, Y)       dev clips only
        WORK/cells_final_nolabel.csv.gz  (features, D, NO Y)    final clips only
        split/../dev/CELLS_META.json     (checks, theta, input hashes)

Usage: python -I build_cells.py
"""
import csv, gzip, io, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import P014, P014_WORK, EXP, WORK, REF_CSV_DIR, sha256, jdump  # noqa: E402

LR_DIR = os.path.join(P014_WORK, "results", "lr")
MT5_DRAWS = ["p100_d0"] + [f"p10_d{i}" for i in range(5)] + [f"p25_d{i}" for i in range(5)] + \
            [f"p50_d{i}" for i in range(3)]
assert len(MT5_DRAWS) == 14
PROBES = [("mt5", d) for d in MT5_DRAWS] + [("fsign", "p100_d0"), ("raw", "p100_d0")]

# ---- the frozen P0-14 matcher (top half of build_concepts.py, executed as-is, as in analyze_fusion_readiness.py)
csvs = [os.path.join(REF_CSV_DIR, f"how2sign_realigned_{s}.csv") for s in ("train", "val", "test")]
src = open(os.path.join(P014, "scripts", "build_concepts.py")).read()
src = src.split("# ---------------------------------------------------------------- per-clip annotations")[0]
g = {"__name__": "bc"}; argv = sys.argv; sys.argv = ["bc", *csvs, P014]
exec(compile(src, "build_concepts.py", "exec"), g); sys.argv = argv
concept_rows = list(csv.DictReader(open(os.path.join(P014, "concepts", "concept_list_v1.csv"))))
CON = [c["concept"] for c in concept_rows]
LIDX = [k for k, c in enumerate(concept_rows) if c["tier"] == "L"]
L = [CON[k] for k in LIDX]
assert len(L) == 24

def present(sent):
    lem, tok = g["lemmas"](sent), set(g["tokens"](sent))
    return [int((c["concept"].lower() in lem) if c["match"] == "lemma" else bool(tok & set(c["forms"].split())))
            for c in concept_rows]

man_all = list(csv.DictReader(open(os.path.join(P014, "splits", "manifest.csv"))))
man = [r for r in man_all if r["role"] == "test_clean"]
ids = [r["clip_id"] for r in man]
Y = np.array([[int(r[c]) for c in CON] for r in man])
ref = {r["SENTENCE_NAME"]: r["SENTENCE"] for r in g["splits"]["test"]}
assert (np.array([present(ref[c]) for c in ids]) == Y).all(), "matcher does not reproduce manifest labels"

pred_path = os.path.join(P014, "full_run", "vm_decode", "predictions.jsonl")
assert sha256(pred_path).startswith("0116a41a")
preds = [json.loads(l) for l in open(pred_path)]
assert [p["clip_id"] for p in preds] == ids
Dm = np.array([present(p["pred"]) for p in preds])
nD = int(Dm[:, LIDX].sum())
assert nD == 888, nD                                   # 534 hits + 354 false mentions (P0-14 recovery_counts)

prior = {c: np.mean([int(r[c]) for r in man_all if r["role"] == "probe_train"]) for c in L}

# ---- probe files: hash-checked, no testcv, theta recovered label-free
expected = dict(reversed(l.split()) for l in open(os.path.join(P014, "full_run", "results", "LR_FULL_OUTPUTS.sha256")))
S, P, TH, hashes = {}, {}, {}, {}
for rep, draw in PROBES:
    name = f"{rep}_ms_{draw}.json"
    assert "testcv" not in name
    path = os.path.join(LR_DIR, name)
    h = sha256(path); assert h == expected[name], name
    hashes[name] = h
    j = json.load(open(path))
    assert list(j["per_concept"]) == CON and j["n_test"] == 2209
    s = np.array(j["test_scores"], dtype=float)[:, LIDX]; p = np.array(j["test_pred"], dtype=int)[:, LIDX]
    th = np.array([s[p[:, k] == 1, k].min() if p[:, k].any() else s[:, k].max() + 1e-3 for k in range(24)])
    assert ((s >= th).astype(int) == p).all(), f"theta does not reproduce test_pred for {name}"
    S[(rep, draw)], P[(rep, draw)], TH[(rep, draw)] = s, p, th

mt5_marg = np.stack([S[("mt5", d)] - TH[("mt5", d)] for d in MT5_DRAWS])      # [14, clips, 24]
mt5_pred = np.stack([P[("mt5", d)] for d in MT5_DRAWS])

units = json.load(open(os.path.join(EXP, "split", "units.json")))["unit_of_video"]
dev_clips = set(open(os.path.join(EXP, "split", "dev_clips.txt")).read().split())
final_clips = set(open(os.path.join(EXP, "split", "final_clips.txt")).read().split())
assert not dev_clips & final_clips and len(dev_clips | final_clips) == 2209

DL = Dm[:, LIDX]; YL = Y[:, LIDX]
cols = ["clip_id", "unit", "concept", "D", "mt5_p100_pred", "mt5_logit", "mt5_margin", "mt5_agree", "mt5_margin_sd",
        "fsign_margin", "raw_margin", "log_frames", "log_T", "n_tokens", "log_tok_per_frame", "log_prior",
        "n_other_trans"]
os.makedirs(WORK, exist_ok=True)
gzw = lambda n: io.TextIOWrapper(gzip.GzipFile(os.path.join(WORK, n), "wb", mtime=0), newline="")  # reproducible bytes
fd, ff = gzw("cells_dev.csv.gz"), gzw("cells_final_nolabel.csv.gz")
wd, wf = csv.writer(fd), csv.writer(ff)
wd.writerow(cols + ["Y"]); wf.writerow(cols)
n_dev = n_final = 0
for i, (r, p) in enumerate(zip(man, preds)):
    nf, T, nt = int(p["n_frames_raw"]), int(p["T"]), int(p["n_tokens"])
    for k, c in enumerate(L):
        row = [r["clip_id"], units[r["video_id"]], c, int(DL[i, k]), int(P[("mt5", "p100_d0")][i, k]),
               f"{S[('mt5', 'p100_d0')][i, k]:.6f}", f"{mt5_marg[0, i, k]:.6f}",
               f"{mt5_pred[:, i, k].mean():.6f}", f"{mt5_marg[:, i, k].std():.6f}",
               f"{S[('fsign', 'p100_d0')][i, k] - TH[('fsign', 'p100_d0')][k]:.6f}",
               f"{S[('raw', 'p100_d0')][i, k] - TH[('raw', 'p100_d0')][k]:.6f}",
               f"{math.log(nf):.6f}", f"{math.log(T):.6f}", nt, f"{math.log((nt + 1) / nf):.6f}",
               f"{math.log(prior[c]):.6f}", int(DL[i].sum() - DL[i, k])]
        if r["clip_id"] in dev_clips:
            wd.writerow(row + [int(YL[i, k])]); n_dev += 1
        else:
            wf.writerow(row); n_final += 1
fd.close(); ff.close()

meta = {
    "n_cells_dev": n_dev, "n_cells_final": n_final, "sum_D_all_tierL": nD,
    "matcher_reproduces_manifest_labels": True, "theta_reproduces_test_pred": True,
    "theta": {f"{rep}_{draw}": dict(zip(L, TH[(rep, draw)].round(6).tolist())) for rep, draw in PROBES},
    "train_prior": prior,
    "inputs": {"predictions.jsonl": sha256(pred_path), "manifest.csv": sha256(os.path.join(P014, "splits", "manifest.csv")),
               "concept_list_v1.csv": sha256(os.path.join(P014, "concepts", "concept_list_v1.csv")),
               "build_concepts.py": sha256(os.path.join(P014, "scripts", "build_concepts.py")), **hashes},
    "outputs": {"cells_dev.csv.gz": sha256(os.path.join(WORK, "cells_dev.csv.gz")),
                "cells_final_nolabel.csv.gz": sha256(os.path.join(WORK, "cells_final_nolabel.csv.gz"))},
}
jdump(meta, os.path.join(EXP, "dev", "CELLS_META.json"))
print(json.dumps({k: meta[k] for k in ("n_cells_dev", "n_cells_final", "sum_D_all_tierL")}))
