"""P0-14 step 3 (PROPOSED - NOT YET RUN ON REAL FEATURES): identical concept probes on every representation. CPU.

Probe A (primary): L2-regularised logistic regression, one independent binary probe per concept, fitted jointly as a
  K-output linear layer with full-batch L-BFGS (outputs share nothing but the input, so this equals K separate
  logistic regressions with the same L2 strength). Inputs standardised with probe-train statistics.
  Class imbalance: per-concept pos_weight = n_neg / n_pos. L2 strength chosen PER CONCEPT from LAMBDAS by
  5-fold group (video) CV on the probe-train draw, maximising out-of-fold AUROC. Decision threshold per concept
  = the one maximising out-of-fold F1 at the chosen L2 (no test labels are used for any choice).
Probe B (secondary): one-hidden-layer MLP (256, ReLU, dropout 0.2), multi-label BCE, AdamW, early stopping on CV
  fold 0 by macro AUROC, 3 seeds, thresholds from the fold-0 predictions.

Representations: raw | fsign | mt5 (from extract_representations.py), plus two sanity baselines run through the
  identical probe: `length` (log T, log n_frames_raw) and `shuffle` (mt5 features, train labels permuted).
Pooling: ms = [mean, std] (primary); msd = [mean, std, mad]; seg4 = 4 segment means (secondary).
Draws: p10_d0..d4, p25_d0..d4, p50_d0..d2, p100_d0 (splits/draws.json); evaluation on all test_clean clips.

Outputs: results/<probe>/<rep>_<pool>_<draw>.json with per-concept test scores (for bootstrap) and metrics.
Usage: python -I run_probe.py --probe-dir . --features features/ --reps raw,fsign,mt5,length,shuffle \
           --pools ms --draws all --probe lr [--synthetic]
"""
import argparse, csv, glob, json, os, time

import numpy as np
import torch

LAMBDAS = [1e-4, 1e-3, 1e-2, 1e-1, 1.0]

ap = argparse.ArgumentParser()
ap.add_argument("--probe-dir", required=True)
ap.add_argument("--features", default=None)
ap.add_argument("--reps", default="raw,fsign,mt5,length,shuffle")
ap.add_argument("--pools", default="ms")
ap.add_argument("--draws", default="all")
ap.add_argument("--probe", default="lr", choices=["lr", "mlp"])
ap.add_argument("--out", default=None)
ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--synthetic", action="store_true", help="self-test on random features with planted signal")
ap.add_argument("--subset", default=None, help="pipeline test: restrict to the clip_ids in this manifest-format CSV")
ap.add_argument("--synthetic-null", action="store_true", help="self-test: all three reps equally informative")
a = ap.parse_args()
torch.set_num_threads(a.threads)
D = a.probe_dir
OUT = a.out or os.path.join(D, "results", a.probe)
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ data
man = list(csv.DictReader(open(os.path.join(D, "splits", "manifest.csv"))))
concept_rows = list(csv.DictReader(open(os.path.join(D, "concepts", "concept_list_v1.csv"))))
CONCEPTS = [c["concept"] for c in concept_rows]
TIER = {c["concept"]: c["tier"] for c in concept_rows}
draws = json.load(open(os.path.join(D, "splits", "draws.json")))["draw_groups"]
keep = [r for r in man if r["role"] in ("probe_train", "test_clean")]
if a.subset:  # pipeline test only (Stage 2 pilot); never used for the real result
    _sub = {r["clip_id"] for r in csv.DictReader(open(a.subset))}
    keep = [r for r in keep if r["clip_id"] in _sub]
idx = {r["clip_id"]: i for i, r in enumerate(keep)}
Y = np.array([[int(r[c]) for c in CONCEPTS] for r in keep], dtype=np.float32)
role = np.array([r["role"] for r in keep])
group = np.array([r["group"] for r in keep])
cv_fold = np.array([int(r["cv_fold"]) if r["cv_fold"] != "" else -1 for r in keep])
test_mask = role == "test_clean"

def load_features():
    feats, T, nraw = {}, np.zeros(len(keep)), np.zeros(len(keep))
    if a.synthetic:  # planted signal: mt5 > fsign > raw, so the self-test must recover that ordering
        rng = np.random.default_rng(0)
        raw_base = None
        for rep, dim, snr in (("raw", 207, 0.15), ("fsign", 1024, 0.35), ("mt5", 768, 0.5)):
            Wp = rng.normal(size=(len(CONCEPTS), dim)).astype(np.float32)
            base = rng.normal(size=(len(keep), dim)).astype(np.float32) + snr * Y @ Wp
            if rep == "raw":
                raw_base = base
            elif a.synthetic_null:  # same information as raw: random rotation of raw + pure-noise padding dims
                Q, _ = np.linalg.qr(rng.normal(size=(207, 207)))
                base = np.concatenate([raw_base @ Q.astype(np.float32),
                                       rng.normal(size=(len(keep), dim - 207)).astype(np.float32)], 1)
            feats[rep] = {"mean": base, "std": np.abs(rng.normal(size=(len(keep), dim))).astype(np.float32),
                          "mad": np.abs(rng.normal(size=(len(keep), dim))).astype(np.float32),
                          "seg4": np.repeat(base[:, None], 4, 1)}
        T = rng.integers(20, 256, len(keep)).astype(float); nraw = T.copy()
        return feats, T, nraw
    feats = {rep: {} for rep in ("raw", "fsign", "mt5")}
    order = np.full(0, 0)
    parts = {}
    for f in sorted(glob.glob(os.path.join(a.features, "shard_*.npz"))):
        ids = json.load(open(f[:-4] + ".json"))["clip_ids"]
        z = np.load(f)
        rows = np.array([idx.get(c, -1) for c in ids])
        ok = rows >= 0
        for k in z.files:
            parts.setdefault(k, []).append((rows[ok], z[k][ok]))
    for k, lst in parts.items():
        dim = lst[0][1].shape[1:]
        arr = np.full((len(keep),) + dim, np.nan, dtype=np.float32)
        for rows, v in lst:
            arr[rows] = v
        if k in ("T", "n_frames_raw"):
            (T if k == "T" else nraw)[:] = arr
        else:
            rep, stat = k.split("_", 1)
            feats[rep][stat] = arr
    missing = np.isnan(feats["mt5"]["mean"]).any(1).sum()
    assert missing == 0, f"{missing} clips without features"
    return feats, T, nraw

FEATS, TLEN, NRAW = load_features()

def design(rep, pool):
    if rep == "length":
        return np.stack([np.log1p(TLEN), np.log1p(NRAW)], 1).astype(np.float32)
    src = FEATS["mt5" if rep == "shuffle" else rep]
    if pool == "ms":
        return np.concatenate([src["mean"], src["std"]], 1)
    if pool == "msd":
        return np.concatenate([src["mean"], src["std"], src["mad"]], 1)
    if pool == "seg4":
        return src["seg4"].reshape(len(keep), -1)
    raise ValueError(pool)

# ------------------------------------------------------------------ metrics (numpy, no sklearn)
def auroc(y, s):
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    ranks = np.empty(len(order)); ranks[order] = np.arange(1, len(order) + 1)
    allv = np.concatenate([pos, neg])  # average ranks for ties
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=ranks); ranks = (sums / cnt)[inv]
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))

def auprc(y, s):
    o = np.argsort(-s); y = y[o]; tp = np.cumsum(y); prec = tp / np.arange(1, len(y) + 1)
    return float((prec * y).sum() / max(y.sum(), 1))

def prf(y, pred):
    tp = float((pred * y).sum()); fp = float((pred * (1 - y)).sum()); fn = float(((1 - pred) * y).sum())
    p = tp / (tp + fp) if tp + fp else 0.0; r = tp / (tp + fn) if tp + fn else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)

def best_f1_threshold(y, s):
    o = np.argsort(-s); ys = y[o]; tp = np.cumsum(ys); k = np.arange(1, len(ys) + 1)
    f1 = 2 * tp / (k + ys.sum())
    i = int(np.argmax(f1))
    return float(s[o][i]) if i < len(s) else float("inf")

# ------------------------------------------------------------------ probes
def fit_lr(X, Yt, lam):
    n, d = X.shape; K = Yt.shape[1]
    Xt, Yt_ = torch.from_numpy(X), torch.from_numpy(Yt)
    pw = ((len(Yt) - Yt.sum(0)) / np.maximum(Yt.sum(0), 1)).astype(np.float32)
    W = torch.zeros(d, K, requires_grad=True); b = torch.zeros(K, requires_grad=True)
    opt = torch.optim.LBFGS([W, b], lr=1, max_iter=300, history_size=20, line_search_fn="strong_wolfe")
    lossf = torch.nn.BCEWithLogitsLoss(pos_weight=torch.from_numpy(pw), reduction="none")
    def closure():
        opt.zero_grad()
        l = lossf(Xt @ W + b, Yt_).mean(0).sum() + lam * (W ** 2).sum()
        l.backward(); return l
    opt.step(closure)
    return W.detach(), b.detach()

def predict_lr(model, X):
    W, b = model
    return (torch.from_numpy(X) @ W + b).numpy()

def fit_mlp(X, Yt, Xv, Yv, seed):
    torch.manual_seed(seed)
    d, K = X.shape[1], Yt.shape[1]
    net = torch.nn.Sequential(torch.nn.Linear(d, 256), torch.nn.ReLU(), torch.nn.Dropout(0.2), torch.nn.Linear(256, K))
    pw = torch.from_numpy(((len(Yt) - Yt.sum(0)) / np.maximum(Yt.sum(0), 1)).astype(np.float32))
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=1e-2)
    lossf = torch.nn.BCEWithLogitsLoss(pos_weight=pw)
    Xt, Yt_ = torch.from_numpy(X), torch.from_numpy(Yt)
    best, best_state, bad = -1, None, 0
    for ep in range(100):
        net.train()
        perm = torch.randperm(len(Xt))
        for i in range(0, len(perm), 256):
            j = perm[i:i + 256]; opt.zero_grad(); lossf(net(Xt[j]), Yt_[j]).backward(); opt.step()
        net.eval()
        with torch.no_grad():
            sv = net(torch.from_numpy(Xv)).numpy()
        m = np.nanmean([auroc(Yv[:, k], sv[:, k]) for k in range(K)])
        if m > best:
            best, best_state, bad = m, {k: v.clone() for k, v in net.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= 10:
                break
    net.load_state_dict(best_state); net.eval()
    return net

def lr_select_and_fit(Xtr, Ytr, folds, Xapply):
    """Per-concept L2 by grouped CV (OOF AUROC), OOF-F1 threshold, refit on all of Xtr, score Xapply."""
    K, nf = Ytr.shape[1], int(folds.max()) + 1
    oof = np.zeros((len(LAMBDAS), len(Ytr), K), np.float32)
    for li, lam in enumerate(LAMBDAS):
        for f in range(nf):
            m = folds == f
            oof[li, m] = predict_lr(fit_lr(Xtr[~m], Ytr[~m], lam), Xtr[m])
    cv_auc = np.array([[auroc(Ytr[:, k], oof[li, :, k]) for k in range(K)] for li in range(len(LAMBDAS))])
    best_li = np.nanargmax(np.nan_to_num(cv_auc, nan=-1), 0)
    thr = np.array([best_f1_threshold(Ytr[:, k], oof[best_li[k], :, k]) for k in range(K)])
    full = [predict_lr(fit_lr(Xtr, Ytr, lam), Xapply) for lam in LAMBDAS]
    st = np.stack([full[best_li[k]][:, k] for k in range(K)], 1)
    return st, thr, [LAMBDAS[i] for i in best_li]

def run_testcv(rep, pool, draw):
    """Design B (leakage control): probe trained AND evaluated inside test_clean, which no representation saw.
    5 outer folds by video; inside each, 4 inner folds by video choose L2 / threshold. Pooled OOF predictions."""
    rep_seed = int(draw.split("_r")[1])
    X = design(rep, pool)[test_mask]
    Yt = Y[test_mask].copy()
    if rep == "shuffle":
        Yt = Yt[np.random.default_rng(0).permutation(len(Yt))]
    g = group[test_mask]
    vids = np.array(sorted(set(g))); np.random.default_rng(100 + rep_seed).shuffle(vids)
    vfold = {v: i % 5 for i, v in enumerate(vids)}
    outer = np.array([vfold[x] for x in g])
    st = np.zeros_like(Yt); pred = np.zeros_like(Yt)
    for f in range(5):
        tr, te = outer != f, outer == f
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        Xs = ((X - mu) / sd).astype(np.float32)
        inner = np.array([(vfold[x] - f - 1) % 5 for x in g[tr]])  # remaining 4 outer folds -> inner folds 0..3
        s, thr, _ = lr_select_and_fit(Xs[tr], Yt[tr], inner, Xs[te])
        st[te] = s; pred[te] = (s >= thr).astype(np.float32)
    Yeval = Yt  # for `shuffle`, labels are permuted for both fitting and scoring -> expected chance level
    per = {}
    for k, c in enumerate(CONCEPTS):
        p, r, f1 = prf(Yeval[:, k], pred[:, k])
        per[c] = {"tier": TIER[c], "n_pos_test": int(Yeval[:, k].sum()), "precision": p, "recall": r, "f1": f1,
                  "f1_prev_matched": float("nan"), "auroc": auroc(Yeval[:, k], st[:, k]), "auprc": auprc(Yeval[:, k], st[:, k]),
                  "prevalence_test": float(Yeval[:, k].mean()), "lambda": None}
    return per, st, pred, X.shape[1], int(test_mask.sum())

def run_one(rep, pool, draw):
    if draw.startswith("testcv"):
        per, st, pred, dim, n = run_testcv(rep, pool, draw)
        macro = lambda t, key: float(np.nanmean([v[key] for v in per.values() if v["tier"] == t]))
        res = {"rep": rep, "pool": pool, "draw": draw, "probe": "lr", "design": "B", "n_train": n, "n_test": n,
               "dim": dim, "per_concept": per,
               "macro": {t: {k: macro(t, k) for k in ("precision", "recall", "f1", "f1_prev_matched", "auroc", "auprc")}
                         for t in ("L", "S")},
               "test_scores": st.astype(np.float32).round(5).tolist(), "test_pred": pred.astype(np.uint8).tolist()}
        json.dump(res, open(os.path.join(OUT, f"{rep}_{pool}_{draw}.json"), "w"))
        return res
    tr = np.isin(group, draws[draw]) & (role == "probe_train")
    X = design(rep, pool)
    Ytr = Y[tr].copy()
    if rep == "shuffle":
        Ytr = Ytr[np.random.default_rng(0).permutation(len(Ytr))]
    mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
    Xs = ((X - mu) / sd).astype(np.float32)
    Xtr, folds = Xs[tr], cv_fold[tr]
    K = len(CONCEPTS)
    if a.probe == "lr":
        st, thr, chosen = lr_select_and_fit(Xtr, Ytr, folds, Xs[test_mask])
    else:
        m0 = folds == 0
        res_seeds = []  # (test scores, fold-0 thresholds) per seed
        for seed in range(3):
            net = fit_mlp(Xtr[~m0], Ytr[~m0], Xtr[m0], Ytr[m0], seed)
            with torch.no_grad():
                sv = net(torch.from_numpy(Xtr[m0])).numpy()
                s_test = net(torch.from_numpy(Xs[test_mask])).numpy()
            res_seeds.append((s_test, np.array([best_f1_threshold(Ytr[m0][:, k], sv[:, k]) for k in range(K)])))
        st = np.mean([s_ for s_, _ in res_seeds], 0)  # seed-averaged scores for AUROC / AUPRC
        thr, chosen = None, None
    Yte = Y[test_mask]
    prev_tr = Ytr.mean(0)
    per = {}
    for k, c in enumerate(CONCEPTS):
        y, s = Yte[:, k], st[:, k]
        if a.probe == "lr":
            p, r, f = prf(y, (s >= thr[k]).astype(float))
        else:  # MLP: F1 averaged over seeds, each with its own fold-0 threshold
            prfs = [prf(y, (s_[:, k] >= t_[k]).astype(float)) for s_, t_ in res_seeds]
            p, r, f = (float(np.mean([x[i] for x in prfs])) for i in range(3))
        kq = max(1, int(round(prev_tr[k] * len(s))))  # prevalence-matched threshold (label-free sensitivity rule)
        pm = np.zeros_like(y); pm[np.argsort(-s)[:kq]] = 1
        _, _, f_pm = prf(y, pm)
        per[c] = {"tier": TIER[c], "n_pos_test": int(y.sum()), "precision": p, "recall": r, "f1": f,
                  "f1_prev_matched": f_pm, "auroc": auroc(y, s), "auprc": auprc(y, s), "prevalence_test": float(y.mean()),
                  "lambda": chosen[k] if chosen else None}
    def macro(tier, key):
        return float(np.nanmean([v[key] for v in per.values() if v["tier"] == tier]))
    res = {"rep": rep, "pool": pool, "draw": draw, "probe": a.probe, "n_train": int(tr.sum()), "n_test": int(test_mask.sum()),
           "dim": int(X.shape[1]), "per_concept": per,
           "macro": {t: {k: macro(t, k) for k in ("precision", "recall", "f1", "f1_prev_matched", "auroc", "auprc")}
                     for t in ("L", "S")},
           "test_scores": st.astype(np.float32).round(5).tolist(),
           "test_pred": ((st >= thr).astype(np.uint8).tolist() if thr is not None else None)}
    json.dump(res, open(os.path.join(OUT, f"{rep}_{pool}_{draw}.json"), "w"))
    return res

TESTCV = ["testcv_r0", "testcv_r1", "testcv_r2"]
draw_names = (sorted(draws) + TESTCV) if a.draws == "all" else a.draws.split(",")
if a.probe == "mlp":  # Design B is defined for the primary (LR) probe only
    draw_names = [d for d in draw_names if not d.startswith("testcv")]
for pool in a.pools.split(","):
    for draw in draw_names:
        for rep in a.reps.split(","):
            if rep == "length" and pool != a.pools.split(",")[0]:
                continue
            t0 = time.time()
            r = run_one(rep, pool, draw)
            print(f"{a.probe} {rep:8s} {pool:4s} {draw:7s} n={r['n_train']:5d} d={r['dim']:5d} "
                  f"L: F1={r['macro']['L']['f1']:.3f} AUROC={r['macro']['L']['auroc']:.3f} AUPRC={r['macro']['L']['auprc']:.3f} "
                  f"| S: F1={r['macro']['S']['f1']:.3f} AUROC={r['macro']['S']['auroc']:.3f}  ({time.time() - t0:.0f}s)", flush=True)
