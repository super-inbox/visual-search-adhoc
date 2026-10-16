"""P0-15 shared code: operating-point rule, L2 logistic regression, AP, the D procedure, count-based metrics.

Everything here is deterministic. See EXPERIMENT_PLAN.md §5, §6, §9.
"""
import gzip, csv, hashlib, json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
P014 = os.path.join(os.path.dirname(os.path.dirname(EXP)), "10.15", "asl-unisign-representation-probe")
WORK = os.path.expanduser("~/Desktop/curify/p015-work")
P014_WORK = os.path.expanduser("~/Desktop/curify/p014-work")
REF_CSV_DIR = os.path.expanduser("~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/"
                                 "experiments/landmark_t5_1pct/local_run_10pct/raw_download")

D_FEATURES = ["mt5_logit", "mt5_margin", "mt5_agree", "mt5_margin_sd", "fsign_margin", "raw_margin",
              "log_frames", "n_tokens", "log_tok_per_frame", "log_prior", "n_other_trans"]          # §5 f1..f11
D_ABLATION_FEATURES = [f for f in D_FEATURES if f not in ("fsign_margin", "raw_margin")]           # §9.5
N2_FEATURES = ["log_frames", "log_T"]                                                              # §9.4 N2
LAMBDAS = [1e-4, 1e-3, 1e-2, 1e-1]
MIN_ADDS, LB_TARGET, Z90 = 10, 0.50, 1.6449


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ operating-point rule (§6)
def wilson_lb(tp, n, z=Z90):
    if n == 0:
        return 0.0
    p = tp / n
    return (p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def select_tau(score, y):
    """Smallest tau with n_add >= 10 and Wilson-90% LB of add precision >= 0.5; +inf (abstain) if none."""
    score = np.asarray(score, float); y = np.asarray(y, int)
    order = np.argsort(-score, kind="mergesort")
    s, t = score[order], y[order]
    tp, n = np.cumsum(t), np.arange(1, len(t) + 1)
    last = np.r_[s[1:] != s[:-1], True]          # end of each block of tied scores: {score >= s} ends here
    best = math.inf
    for j in np.where(last)[0]:
        if n[j] >= MIN_ADDS and wilson_lb(int(tp[j]), int(n[j])) >= LB_TARGET:
            best = float(s[j])                    # descending scan: the last qualifying value is the smallest
    return best


# ------------------------------------------------------------------ L2 logistic regression (§5)
def fit_scaler(X):
    mu = X.mean(0); sd = X.std(0)
    sd[sd == 0] = 1.0
    return mu, sd


def fit_lr(Z, y, lam, tol=1e-10, max_iter=100):
    """Minimise mean log-loss + lam/2 ||w||^2 (intercept unpenalised) by Newton/IRLS. Z must be standardised."""
    n, d = Z.shape
    A = np.hstack([np.ones((n, 1)), Z])
    beta = np.zeros(d + 1)
    pen = np.full(d + 1, lam); pen[0] = 0.0

    def obj(b):
        eta = A @ b
        return np.mean(np.logaddexp(0.0, eta) - y * eta) + 0.5 * np.sum(pen * b * b)
    f = obj(beta)
    for _ in range(max_iter):
        p = 1.0 / (1.0 + np.exp(-(A @ beta)))
        g = A.T @ (p - y) / n + pen * beta
        W = p * (1 - p)
        H = (A * W[:, None]).T @ A / n + np.diag(pen)
        step = np.linalg.solve(H + 1e-12 * np.eye(d + 1), g)
        t = 1.0
        while True:                                   # step halving: never increase the objective
            nb = beta - t * step; nf = obj(nb)
            if nf <= f + 1e-15 or t < 1e-8:
                break
            t *= 0.5
        beta, f = nb, nf
        if np.max(np.abs(t * step)) < tol:
            break
    return beta


def lr_logit(beta, Z):
    return beta[0] + Z @ beta[1:]


def average_precision(y, s):
    """AP with tied scores grouped: sum over distinct thresholds of (R_j - R_{j-1}) * P_j."""
    y = np.asarray(y, int); npos = y.sum()
    if npos == 0:
        return float("nan")
    order = np.argsort(-np.asarray(s, float), kind="mergesort")
    ss, yy = np.asarray(s, float)[order], y[order]
    tp, n = np.cumsum(yy), np.arange(1, len(yy) + 1)
    last = np.r_[ss[1:] != ss[:-1], True]
    tp, n = tp[last], n[last]
    R = tp / npos; P = tp / n
    return float(np.sum(np.diff(np.r_[0.0, R]) * P))


def fit_model(X, y, lam):
    mu, sd = fit_scaler(X)
    return {"lam": lam, "mu": mu, "sd": sd, "beta": fit_lr((X - mu) / sd, y, lam)}


def score_model(m, X):
    return lr_logit(m["beta"], (X - m["mu"]) / m["sd"])


def oof_scores(X, y, fold, lam):
    out = np.full(len(y), np.nan)
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        out[te] = score_model(fit_model(X[tr], y[tr], lam), X[te])
    return out


def d_procedure(X, y, fold):
    """λ by grouped-CV pooled OOF AP (ties -> larger λ); τ by the §6 rule on OOF logits at that λ; refit on all."""
    aps = {}
    oofs = {}
    for lam in LAMBDAS:
        oofs[lam] = oof_scores(X, y, fold, lam)
        aps[lam] = average_precision(y, oofs[lam])
    best = max(LAMBDAS, key=lambda l: (aps[l], l))
    tau = select_tau(oofs[best], y)
    m = fit_model(X, y, best)
    return {"model": m, "tau": tau, "cv_ap": {str(k): v for k, v in aps.items()}, "lam": best}


def model_to_json(m):
    return {"lam": m["lam"], "mu": m["mu"].tolist(), "sd": m["sd"].tolist(), "beta": m["beta"].tolist()}


def model_from_json(j):
    return {"lam": j["lam"], "mu": np.array(j["mu"]), "sd": np.array(j["sd"]), "beta": np.array(j["beta"])}


# ------------------------------------------------------------------ cells I/O
def read_cells(path):
    with gzip.open(path, "rt") as f:
        rows = list(csv.DictReader(f))
    cols = {k: [r[k] for r in rows] for k in rows[0]}
    out = {}
    for k, v in cols.items():
        if k in ("clip_id", "concept", "unit"):
            out[k] = np.array(v)
        else:
            out[k] = np.array(v, dtype=float)
    return out


def feat(cells, names, mask=None):
    X = np.column_stack([cells[n] for n in names])
    return X if mask is None else X[mask]


# ------------------------------------------------------------------ count-based metrics (§9.2) and bootstrap (§9.3)
def unit_counts(units, concepts, Y, D, A, unit_list, concept_list):
    """Per (unit, concept): fused TP, FP, FN; added TP, FP; candidate positives. A must be 0 where D == 1."""
    assert not np.any(A.astype(bool) & D.astype(bool)), "additions must be on candidate cells only"
    F = np.maximum(D, A)
    ui = {u: i for i, u in enumerate(unit_list)}; ci = {c: i for i, c in enumerate(concept_list)}
    U = np.array([ui[u] for u in units]); K = np.array([ci[c] for c in concepts])
    C = np.zeros((len(unit_list), len(concept_list), 6))
    for j, v in enumerate([F * Y, F * (1 - Y), (1 - F) * Y, A * Y, A * (1 - Y), (1 - D) * Y]):
        np.add.at(C[:, :, j], (U, K), v)
    return C


def summarize(C, Cbase, n_clips):
    """C, Cbase: [concept, 6] summed counts for an arm and for arm A."""
    def prf(tp, fp, fn):
        P = tp / (tp + fp) if tp + fp else 0.0; R = tp / (tp + fn) if tp + fn else 0.0
        return P, R, (2 * P * R / (P + R) if P + R else 0.0)
    tot, base = C.sum(0), Cbase.sum(0)
    P, R, F1 = prf(*tot[:3]); bP, bR, bF1 = prf(*base[:3])
    mac = np.array([prf(*C[k, :3]) for k in range(C.shape[0])]).mean(0)
    bmac = np.array([prf(*Cbase[k, :3]) for k in range(C.shape[0])]).mean(0)
    tpa, fpa, posc = tot[3], tot[4], tot[5]
    na = tpa + fpa
    ap = tpa / na if na else float("nan"); mr = tpa / posc if posc else float("nan")
    return {
        "n_add": na, "tp_add": tpa, "fp_add": fpa, "add_precision": ap, "missed_recall": mr,
        "add_f1": (2 * ap * mr / (ap + mr) if na and posc and ap + mr else 0.0),
        "net_correct": tpa - fpa, "net_correct_per100": 100 * (tpa - fpa) / n_clips,
        "false_adds_per_clip": fpa / n_clips, "missed_positives": posc,
        "micro_p": P, "micro_r": R, "micro_f1": F1,
        "d_micro_p": P - bP, "d_micro_r": R - bR, "d_micro_f1": F1 - bF1,
        "macro_p": mac[0], "macro_r": mac[1], "macro_f1": mac[2],
        "d_macro_p": mac[0] - bmac[0], "d_macro_r": mac[1] - bmac[1], "d_macro_f1": mac[2] - bmac[2],
    }


def bootstrap_weights(n_units, B, seed):
    rng = np.random.default_rng(seed)
    return np.stack([np.bincount(rng.integers(0, n_units, n_units), minlength=n_units) for _ in range(B)])


def ci95(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) else [float("nan")] * 2


def jdump(obj, path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, float) and math.isinf(o):
            return "inf"
        raise TypeError(type(o))
    def fix(o):
        if isinstance(o, float) and math.isinf(o):
            return "inf"
        if isinstance(o, dict):
            return {k: fix(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [fix(v) for v in o]
        return o
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(fix(obj), f, indent=1, default=conv)
        f.write("\n")


def tau_from_json(v):
    return math.inf if v == "inf" else float(v)
