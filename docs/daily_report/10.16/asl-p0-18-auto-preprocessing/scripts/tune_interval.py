"""P0-18 DEV: tune the automatic signing-interval detector against TIMING AGREEMENT only (interval IoU with the How2Sign
realigned window, the oracle). No translation metric is read or computed here.

Two-stage search (both stages run the exact pipeline decision code; stage 1 is a vectorised copy of select_interval
with snap_s = 0, asserted equal to it on a sample):
  stage 1  activity-score params x warp option (family + margins + lag_min_r) x expected-window offsets
           (lag_start, lag_end), no activity snapping
  stage 2  around the stage-1 winner: activity-run params (thr_on, max_gap_s) x snap_s x (lag_start, lag_end)
Objective: mean interval IoU. Honest estimate: 5-fold CV grouped by source VIDEO_ID (deterministic sorted order), the
whole two-stage search refit inside each training fold. Families compared on the CV test folds: identity warp (the
fixed context-window detector), constant lag, linear warp, and "auto" (best family chosen on the training folds).

Usage: python -I tune_interval.py --vid-dir DIR --clips CLIPS.csv --oracle ORACLE.json --out OUT.json [--procs 4]
"""
import argparse, csv, itertools, json, os, re, sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "asl-p0-16-experimental-credibility", "scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402
import p018_lib as L  # noqa: E402
import pose_extract as PE  # noqa: E402

OFF = 9.0
SCORE_GRID = {"smooth_s": [0.2, 0.4], "up_scale": [1.0], "speed_scale": [1.0, 2.0], "valid_min": [0.3, 0.5]}
RUN_GRID = {"thr_on": [0.4, 0.55], "thr_off": [0.25], "max_gap_s": [0.3, 0.6], "min_seg_s": [0.3]}
WARP_OPTS = ([{"family": "identity", "margin_lag": OFF, "margin_warp": OFF, "lag_min_r": -1.0}]
             + [{"family": "lag", "margin_lag": ml, "margin_warp": OFF, "lag_min_r": r}
                for ml in (0.0, 0.03, 0.06) for r in (-1.0, 0.15)]
             + [{"family": "warp", "margin_lag": ml, "margin_warp": mw, "lag_min_r": r}
                for ml in (0.0, 0.03, 0.06) for mw in (0.0, 0.03, 0.06, 0.1) for r in (-1.0, 0.15)])
LS = [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
LE = [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
SNAP = [0.0, 0.5, 1.0, 2.0, 3.0]
FIXED = {"min_dur_s": 1.0, "lag_hz": 5.0, "lag_min": -10.0, "lag_max": 50.0,
         "slope_grid": [round(0.95 + 0.01 * i, 2) for i in range(51)]}
SCORES = [dict(zip(SCORE_GRID, v)) for v in itertools.product(*SCORE_GRID.values())]
RUNS = [dict(zip(RUN_GRID, v)) for v in itertools.product(*RUN_GRID.values())]
VIDEO_ID = lambda c: re.sub(r"_\d+(?:_\d+)*-\d+-rgb_front$", "", c)


def per_video(job):
    """Per score combo: warp for every WARP_OPT and activity runs for every RUN combo (whole video)."""
    npz, clips, sentences = job
    V = PE.VideoPose(npz)
    K, S, _, _ = V.signer_track()
    out = {"vid_end": V.n / V.fps, "clips": clips, "warps": [], "runs": [], "cands": []}
    for sc in SCORES:
        p = dict(sc, **FIXED, **RUNS[0])
        F = L.activity_features(K, S, V.fps)
        if F is None:
            out["warps"].append([(0.0, 1.0)] * len(WARP_OPTS)); out["runs"].append([None] * len(RUNS))
            out["cands"].append(None); continue
        score = L.activity_score(F, V.fps, p)
        c = L.warp_candidates(score, V.fps, sentences, p)
        w = []
        for wo in WARP_OPTS:
            d = L.choose_warp(c, dict(p, **wo))
            w.append((d["lag"], d["slope"]))
        out["warps"].append(w); out["cands"].append({k: list(v) for k, v in c.items()})
        rl = []
        for rc in RUNS:
            act, _ = L.active_mask(F, V.fps, dict(p, **rc))
            rl.append([(a / V.fps, b / V.fps) for a, b in L._runs(act)])
        out["runs"].append(rl)
    return out


def stage1_iou(V, orc, idx):
    """IoU [score, warp_opt, ls, le, clip] for snap_s = 0 (vectorised select_interval)."""
    s = np.array([V["anchor"][i][0] for i in idx]); e = np.array([V["anchor"][i][1] for i in idx])
    hi = np.array([V["vid_end"][i] for i in idx]); o = np.array([orc[V["ids"][i]] for i in idx])
    lag = V["lag"][:, :, idx]; slope = V["slope"][:, :, idx]                          # [score, wopt, clip]
    a0 = (lag + slope * s)[:, :, None, None, :]; a1 = (lag + slope * e)[:, :, None, None, :]
    ls = np.array(LS)[None, None, :, None, None]; le = np.array(LE)[None, None, None, :, None]
    Es = np.minimum(np.maximum(a0 + ls, 0.0), hi); Ee = np.minimum(np.maximum(a1 + le, 0.0), hi)
    Ee = np.where(Ee - Es < FIXED["min_dur_s"], np.minimum(hi, Es + FIXED["min_dur_s"]), Ee)
    inter = np.maximum(0.0, np.minimum(Ee, o[:, 1]) - np.maximum(Es, o[:, 0]))
    union = np.maximum(Ee, o[:, 1]) - np.minimum(Es, o[:, 0])
    return np.where(union > 0, inter / np.where(union > 0, union, 1), 0.0).astype(np.float32)


def interval(V, i, si, wi, ri, sel):
    p = dict(SCORES[si], **RUNS[ri], **sel, **FIXED)
    return L.detect_interval_video(V["runs"][si][V["vid"][i]][ri], V["vid_end"][i], V["anchor"][i],
                                   (V["lag"][si, wi, i], V["slope"][si, wi, i]), p)


def fit(V, orc, train, wsel):
    """Two-stage search on clip indices `train`, warp options restricted to wsel. Returns the chosen config."""
    m = stage1_iou(V, orc, train).mean(-1)                                              # [score, wopt, ls, le]
    m[:, [w for w in range(len(WARP_OPTS)) if w not in wsel]] = -1
    si, wi, li, ei = (int(x) for x in np.unravel_index(np.argmax(m), m.shape))
    best = (float(m[si, wi, li, ei]), 0, {"lag_start": LS[li], "lag_end": LE[ei], "snap_s": 0.0})
    for ri in range(len(RUNS)):
        for snap in SNAP[1:]:
            for ls in LS:
                for le in LE:
                    sel = {"lag_start": ls, "lag_end": le, "snap_s": snap}
                    v = float(np.mean([L.interval_iou(tuple((lambda o: (o["start"], o["end"]))(
                        interval(V, i, si, wi, ri, sel))), orc[V["ids"][i]]) for i in train]))
                    if v > best[0] + 1e-9:
                        best = (v, ri, sel)
    return {"si": si, "wi": wi, "ri": best[1], "sel": best[2], "train_mean_iou": best[0]}


def params_of(cfg):
    wo = {k: v for k, v in WARP_OPTS[cfg["wi"]].items() if k != "family"}
    return dict(SCORES[cfg["si"]], **RUNS[cfg["ri"]], **wo, **cfg["sel"], **FIXED)


def predict(V, cfg, idx):
    out = {}
    for i in idx:
        o = interval(V, i, cfg["si"], cfg["wi"], cfg["ri"], cfg["sel"])
        out[V["ids"][i]] = {"start": o["start"], "end": o["end"], "fail": o["fail"]}
    return out


def summarize(pred, orc, ids):
    iou = np.array([L.interval_iou(pred[c], orc[c]) for c in ids])
    ds = np.array([pred[c][0] - orc[c][0] for c in ids]); de = np.array([pred[c][1] - orc[c][1] for c in ids])
    inter = np.array([max(0.0, min(pred[c][1], orc[c][1]) - max(pred[c][0], orc[c][0])) for c in ids])
    olen = np.array([orc[c][1] - orc[c][0] for c in ids]); plen = np.array([pred[c][1] - pred[c][0] for c in ids])
    return {"n": len(ids), "mean_iou": float(iou.mean()), "median_iou": float(np.median(iou)),
            "frac_iou_ge_0.5": float((iou >= 0.5).mean()), "frac_iou_zero": float((iou == 0).mean()),
            "median_abs_start_err_s": float(np.median(np.abs(ds))), "median_abs_end_err_s": float(np.median(np.abs(de))),
            "median_start_err_s": float(np.median(ds)), "median_end_err_s": float(np.median(de)),
            "mean_oracle_coverage": float(np.mean(inter / np.maximum(olen, 1e-6))),
            "mean_precision": float(np.mean(inter / np.maximum(plen, 1e-6)))}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vid-dir", required=True)
    ap.add_argument("--clips", required=True)
    ap.add_argument("--oracle", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    orc = {k: tuple(v) for k, v in json.load(open(a.oracle)).items()}
    rows = list(csv.DictReader(open(a.clips)))
    assert_not_holdout([r["clip_id"] for r in rows])
    by_v = {}
    for r in rows:
        by_v.setdefault(r["video_name"], []).append((r["clip_id"], float(r["start"]), float(r["end"])))
    jobs = [(os.path.join(a.vid_dir, v + ".npz"), [c for c in cl if c[0] in orc], [(s, e) for _, s, e in cl])
            for v, cl in sorted(by_v.items()) if os.path.exists(os.path.join(a.vid_dir, v + ".npz"))]
    jobs = [j for j in jobs if j[1]]
    with Pool(a.procs) as pool:
        res = pool.map(per_video, jobs)
    # flatten to clip-indexed arrays
    V = {"ids": [], "anchor": [], "vid_end": [], "vid": [], "runs": [[] for _ in SCORES]}
    lag, slope = [], []
    for vi, r in enumerate(res):
        for si in range(len(SCORES)):
            V["runs"][si].append(r["runs"][si])
        for cid, s, e in r["clips"]:
            V["ids"].append(cid); V["anchor"].append((s, e)); V["vid_end"].append(r["vid_end"]); V["vid"].append(vi)
            lag.append([[w[0] for w in r["warps"][si]] for si in range(len(SCORES))])
            slope.append([[w[1] for w in r["warps"][si]] for si in range(len(SCORES))])
    V["lag"] = np.moveaxis(np.array(lag), 0, -1); V["slope"] = np.moveaxis(np.array(slope), 0, -1)
    n = len(V["ids"]); ids = V["ids"]
    # stage-1 vectorisation == select_interval (sample check)
    rng = np.random.default_rng(0)
    t1 = stage1_iou(V, orc, list(range(n)))
    for _ in range(300):
        si, wi, li, ei, i = (int(rng.integers(d)) for d in t1.shape)
        o = interval(V, i, si, wi, 0, {"lag_start": LS[li], "lag_end": LE[ei], "snap_s": 0.0})
        assert abs(L.interval_iou((o["start"], o["end"]), orc[ids[i]]) - t1[si, wi, li, ei, i]) < 1e-5
    del t1
    fam = {f: [w for w, wo in enumerate(WARP_OPTS) if wo["family"] == f] for f in ("identity", "lag", "warp")}
    fam["auto"] = list(range(len(WARP_OPTS)))
    vids = sorted({VIDEO_ID(c) for c in ids}); vfold = {v: i % 5 for i, v in enumerate(vids)}
    fold = np.array([vfold[VIDEO_ID(c)] for c in ids])
    orig = {c: V["anchor"][i] for i, c in enumerate(ids)}
    cv, cvp = [], {f: {} for f in fam}
    for f in range(5):
        tr = [i for i in range(n) if fold[i] != f]; te = [i for i in range(n) if fold[i] == f]
        rec = {"fold": f, "n_test": len(te), "original": summarize(orig, orc, [ids[i] for i in te])}
        for fname, ws in fam.items():
            cfg = fit(V, orc, tr, ws)
            pr = predict(V, cfg, te)
            cvp[fname].update({c: (v["start"], v["end"]) for c, v in pr.items()})
            rec[fname] = {"params": params_of(cfg), "family": WARP_OPTS[cfg["wi"]]["family"],
                          "train_mean_iou": cfg["train_mean_iou"], "test": summarize(cvp[fname], orc, [ids[i] for i in te])}
            print(f"fold {f} {fname}: test mean IoU {rec[fname]['test']['mean_iou']:.3f}", flush=True)
        cv.append(rec)
    pooled = {"original": summarize(orig, orc, ids)}
    pooled.update({fname: summarize(cvp[fname], orc, ids) for fname in fam})
    final = fit(V, orc, list(range(n)), fam["auto"])
    pf = predict(V, final, range(n))
    fails = sum(1 for v in pf.values() if v["fail"])
    warp_diag = {}
    for vi, r in enumerate(res):
        cl = r["clips"]; ii = [k for k in range(n) if V["vid"][k] == vi]
        warp_diag[os.path.basename(jobs[vi][0])[:-4]] = {
            "lag": float(V["lag"][final["si"], final["wi"], ii[0]]), "slope": float(V["slope"][final["si"], final["wi"], ii[0]]),
            "candidates": r["cands"][final["si"]],
            "oracle_median_start_lag": float(np.median([orc[c][0] - s for c, s, _ in cl])), "n_clips": len(cl)}
    out = {"n_clips": n, "n_videos": len(vids), "n_video_names": len(jobs),
           "grids": {"score": SCORE_GRID, "runs": RUN_GRID, "warp_options": WARP_OPTS, "lag_start": LS, "lag_end": LE,
                     "snap_s": SNAP, "fixed": FIXED},
           "objective": "mean interval IoU vs realigned window (timing agreement only)",
           "cv_folds": cv, "cv_pooled_test": pooled,
           "selected": {"params": params_of(final), "family": WARP_OPTS[final["wi"]]["family"],
                        "insample_mean_iou": final["train_mean_iou"], "insample_fail_rate": fails / n},
           "warp_per_video": warp_diag,
           "per_clip_selected": pf}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({"cv_pooled_test": {k: {m: round(v[m], 3) for m in ("mean_iou", "median_iou", "frac_iou_ge_0.5",
                                                                          "median_abs_start_err_s", "median_abs_end_err_s")}
                                         for k, v in pooled.items()},
                      "selected": out["selected"]}, indent=1))
