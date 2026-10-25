"""P0-18 core: pose-only automatic signing-interval detection and signer crop, and Uni-Sign input writing.

Inputs are full-frame RTMPose (rtmlib Wholebody, COCO-WholeBody 133 keypoints) in PIXELS. Nothing here reads
English text, reference/realigned boundaries or any label. Oracle boundaries are used only by the tuning/eval
scripts, never by these functions.

Uni-Sign normalisation fact this relies on (datasets.py load_part_kp / crop_scale at eed438bc): body keypoints are
min-max boxed over the clip and divided by one isotropic scale; hands/face are made relative to wrist/nose and divided
by the same scale. So Uni-Sign input is exactly invariant to translation and to isotropic scaling of the stored
(normalised) keypoints. A crop therefore changes the input ONLY through its aspect ratio W/H (keypoints are stored
divided by (W, H)), plus through which frames are included.
"""
import numpy as np

NOSE, LSH, RSH, LEL, REL, LWR, RWR = 0, 5, 6, 7, 8, 9, 10
LHAND, RHAND = list(range(91, 112)), list(range(112, 133))
BODY_UNISIGN = [0] + list(range(3, 11))
THR = 0.3                                                     # Uni-Sign's own keypoint confidence threshold


# ---------------------------------------------------------------- signer selection (multi-person frames)
def select_signer(kps_list, scs_list):
    """kps_list[t]: (P, 133, 2) pixels, scs_list[t]: (P, 133). Returns (T,133,2), (T,133), n_multi.
    Per frame keep the person with the largest confident upper-body box; on ties of P>1 prefer continuity with the
    previous frame's choice (smallest shoulder-centre jump). Frames with no person get zeros (score 0)."""
    T = len(kps_list)
    K = np.zeros((T, 133, 2)); S = np.zeros((T, 133)); prev = None; n_multi = 0
    for t in range(T):
        k, s = np.asarray(kps_list[t], float), np.asarray(scs_list[t], float)
        if k.ndim == 2:
            k, s = k[None], s[None]
        if len(k) == 0:
            continue
        if len(k) > 1:
            n_multi += 1
        best, best_key = 0, None
        for p in range(len(k)):
            m = s[p, :13] > THR
            area = (np.ptp(k[p, :13][m, 0]) * np.ptp(k[p, :13][m, 1])) if m.sum() >= 3 else 0.0
            ctr = (k[p, LSH] + k[p, RSH]) / 2
            jump = np.linalg.norm(ctr - prev) if prev is not None else 0.0
            key = (area, -jump)
            if best_key is None or key > best_key:
                best, best_key = p, key
        K[t], S[t] = k[best], s[best]
        if S[t, LSH] > THR and S[t, RSH] > THR:
            prev = (K[t, LSH] + K[t, RSH]) / 2
    return K, S, n_multi


# ---------------------------------------------------------------- per-frame activity signals
def shoulder_width(K, S):
    m = (S[:, LSH] > THR) & (S[:, RSH] > THR)
    if m.sum() == 0:
        return float("nan")
    return float(np.median(np.linalg.norm(K[m, LSH] - K[m, RSH], axis=-1)))


def _smooth(x, w):
    if w <= 1:
        return x
    k = np.ones(w) / w
    pad = np.pad(x, (w // 2, w - 1 - w // 2), mode="edge")
    return np.convolve(pad, k, mode="valid")


def activity_features(K, S, fps):
    """Per-frame features (all normalised by the clip's median shoulder width SW):
       hand_valid: max over hands of the fraction of hand keypoints with score > THR
       hand_up:    max over confident wrists of (rest_line - wrist_y) / SW, rest_line = shoulder_y + 1.5 SW
       speed:      max over confident wrists of |d wrist| * fps / SW  (shoulder widths per second)"""
    T = len(K)
    SW = shoulder_width(K, S)
    if not np.isfinite(SW) or SW <= 1:
        return None
    hv = np.maximum((S[:, LHAND] > THR).mean(1), (S[:, RHAND] > THR).mean(1))
    sh_y = np.where((S[:, LSH] > THR) & (S[:, RSH] > THR), (K[:, LSH, 1] + K[:, RSH, 1]) / 2, np.nan)
    sh_y = np.where(np.isnan(sh_y), np.nanmedian(sh_y) if np.isfinite(np.nanmedian(sh_y)) else 0, sh_y)
    rest = sh_y + 1.5 * SW
    up = np.full(T, -np.inf); sp = np.zeros(T)
    for w in (LWR, RWR):
        ok = S[:, w] > THR
        up = np.where(ok, np.maximum(up, (rest - K[:, w, 1]) / SW), up)
        d = np.zeros(T)
        d[1:] = np.linalg.norm(np.diff(K[:, w], axis=0), axis=-1) * fps / SW
        d[1:] = np.where(ok[1:] & ok[:-1], d[1:], 0.0)
        sp = np.maximum(sp, d)
    up = np.where(np.isfinite(up), up, -5.0)
    return {"hand_valid": hv, "hand_up": up, "speed": sp, "SW": SW}


def activity_score(F, fps, p):
    """Per-frame signing-activity score in [0, 1]: smoothed hand height and wrist speed, zeroed where too few hand
    landmarks are valid."""
    w = max(1, int(round(p["smooth_s"] * fps)))
    up, sp, hv = _smooth(F["hand_up"], w), _smooth(F["speed"], w), _smooth(F["hand_valid"], w)
    score = np.clip(up / p["up_scale"], 0, 1) * 0.5 + np.clip(sp / p["speed_scale"], 0, 1) * 0.5
    return np.where(hv >= p["valid_min"], score, 0.0)


def active_mask(F, fps, p):
    """Binary activity with smoothing + hysteresis + min-duration + gap filling (params dict p)."""
    score = activity_score(F, fps, p)
    act = _hysteresis(score, p["thr_on"], p["thr_off"])
    act = _fill_gaps(act, int(round(p["max_gap_s"] * fps)))
    act = _drop_short(act, int(round(p["min_seg_s"] * fps)))
    return act, score


def _hysteresis(score, on, off):
    """On when score >= on, off when score < off, otherwise keep the previous state (initially off); on >= off."""
    assert on >= off
    st = np.where(score >= on, 1.0, np.where(score < off, 0.0, np.nan))
    idx = np.where(~np.isnan(st), np.arange(len(st)), -1)
    np.maximum.accumulate(idx, out=idx)
    return np.where(idx >= 0, st[np.maximum(idx, 0)], 0.0).astype(bool)


def _runs(a):
    """[(start, end)) index pairs of the True runs of a boolean array."""
    d = np.diff(np.concatenate([[0], np.asarray(a, np.int8), [0]]))
    return list(zip(np.where(d == 1)[0].tolist(), np.where(d == -1)[0].tolist()))


def _fill_gaps(a, g):
    a = a.copy(); r = _runs(a)
    for (s0, e0), (s1, e1) in zip(r, r[1:]):
        if s1 - e0 <= g:
            a[e0:s1] = True
    return a


def _drop_short(a, d):
    a = a.copy()
    for s, e in _runs(a):
        if e - s < d:
            a[s:e] = False
    return a


# ---------------------------------------------------------------- interval selection around the anchor window
def activity_runs(K, S, fps, t0, p):
    """Active runs [(start_s, end_s), ...] from the activity mask, or None if shoulders are never found."""
    F = activity_features(K, S, fps)
    if F is None:
        return None, None
    act, _ = active_mask(F, fps, p)
    tt = t0 + np.arange(len(K)) / fps
    return [(float(tt[a]), float(tt[b - 1] + 1.0 / fps)) for a, b in _runs(act)], float(act.mean())


def select_interval(lo, hi, runs, anchor, p):
    """Expected window E = [anchor.start + lag_start, anchor.end + lag_end] (clamped to [lo, hi]); each bound is
    snapped to the nearest activity onset/offset within +-snap_s. runs=None means no pose evidence (E is returned)."""
    Es = min(max(anchor[0] + p["lag_start"], lo), hi); Ee = min(max(anchor[1] + p["lag_end"], lo), hi)
    if Ee - Es < p["min_dur_s"]:
        Ee = min(hi, Es + p["min_dur_s"])
    out = {"E": [Es, Ee], "snapped_start": False, "snapped_end": False, "fail": None}
    if runs is None:
        out.update(start=Es, end=Ee, fail="no_shoulders"); return out
    s, e, R = Es, Ee, p["snap_s"]
    if R > 0 and runs:
        inside = [r for r in runs if r[0] <= Es < r[1]]
        if inside:
            if inside[0][0] >= Es - R:
                s, out["snapped_start"] = inside[0][0], True
        else:
            nxt = [r for r in runs if Es <= r[0] <= Es + R]
            if nxt:
                s, out["snapped_start"] = nxt[0][0], True
        inside = [r for r in runs if r[0] < Ee <= r[1]]
        if inside:
            if inside[-1][1] <= Ee + R:
                e, out["snapped_end"] = inside[-1][1], True
        else:
            prv = [r for r in runs if Ee - R <= r[1] <= Ee]
            if prv:
                e, out["snapped_end"] = prv[-1][1], True
    if e - s < p["min_dur_s"]:                               # never return a degenerate interval
        s, e = Es, Ee
        out["fail"] = "degenerate_after_snap"
    if not any(r[0] < e and r[1] > s for r in runs):
        out["fail"] = out["fail"] or "no_activity_in_interval"
    out.update(start=float(s), end=float(e))
    return out


def detect_interval(K, S, fps, t0, anchor, p):
    """K,S cover a context window starting at t0 (s); anchor = (start, end) ORIGINAL timing (s). See select_interval."""
    lo, hi = t0, t0 + len(K) / fps
    runs, frac = activity_runs(K, S, fps, t0, p)
    out = select_interval(lo, hi, runs, anchor, p)
    out["active_frac"] = frac
    return out


# ---------------------------------------------------------------- video-level lag (signing vs original timing)
def warp_candidates(score, fps, sentences, p):
    """Best Pearson correlation, over the whole video binned at lag_hz, between the activity score and the indicator of
    the union of the warped ORIGINAL sentence windows [lag + slope*s, lag + slope*e], for three nested families:
    identity (lag 0, slope 1), constant lag (slope 1, lag in [lag_min, lag_max] step 1/lag_hz) and linear warp
    (slope in slope_grid as well). Returns {family: (r, lag, slope)}."""
    hz = p["lag_hz"]
    nb = int(np.ceil(len(score) / fps * hz))
    b = np.minimum((np.arange(len(score)) / fps * hz).astype(int), nb - 1)
    act = np.bincount(b, weights=score, minlength=nb) / np.maximum(np.bincount(b, minlength=nb), 1)
    act = act - act.mean(); sa = np.sqrt((act ** 2).sum())
    lags = np.arange(int(round(p["lag_min"] * hz)), int(round(p["lag_max"] * hz)) + 1)
    lo, hi = int(lags[0]), int(lags[-1])
    best = {"identity": (-2.0, 0.0, 1.0), "lag": (-2.0, 0.0, 1.0), "warp": (-2.0, 0.0, 1.0)}
    if sa == 0:
        return best
    for slope in sorted(set(p["slope_grid"]) | {1.0}):
        se = [(int(round(slope * s0 * hz)), int(round(slope * e0 * hz))) for s0, e0 in sentences]
        M = max([nb] + [e0 for _, e0 in se]) + 1
        pad = np.zeros(max(hi, 0) + M + nb + max(-lo, 0))              # pad[off + u] = indicator at bin u
        off = max(hi, 0)
        for s0, e0 in se:
            pad[off + max(s0, -off):off + max(e0, -off)] = 1.0
        for lb in sorted(set(lags.tolist()) | {0}):
            ind = pad[off - lb:off - lb + nb].copy()
            ind -= ind.mean(); si = np.sqrt((ind ** 2).sum())
            if si == 0:
                continue
            r = float(act @ ind / (sa * si)); cand = (r, lb / hz, float(slope))
            fams = ["warp"]
            if slope == 1.0 and lo <= lb <= hi:
                fams.append("lag")
            if slope == 1.0 and lb == 0:
                fams.append("identity")
            for f in fams:
                if r > best[f][0]:
                    best[f] = cand
    return best


def video_warp(score, fps, sentences, p):
    """Per-video linear time warp t_sign = lag + slope * t_orig (see warp_candidates). The constant lag replaces the
    identity only if its correlation is higher by at least margin_lag, and the linear warp replaces the result so far
    only if higher by at least margin_warp; a margin >= 9 disables that family. If the chosen correlation is below
    lag_min_r the identity is used (flag "lag_low_conf")."""
    return choose_warp(warp_candidates(score, fps, sentences, p), p)


def choose_warp(c, p):
    """The video_warp decision rule on precomputed warp_candidates."""
    pick = "identity"
    if c["lag"][0] >= c[pick][0] + p["margin_lag"]:
        pick = "lag"
    if c["warp"][0] >= c[pick][0] + p["margin_warp"]:
        pick = "warp"
    r, lag, slope = c[pick]
    fail = None
    if r < p["lag_min_r"]:
        lag, slope, fail = 0.0, 1.0, "lag_low_conf"
    return {"lag": float(lag), "slope": float(slope), "r": float(r), "family": pick, "fail": fail,
            "candidates": {k: list(v) for k, v in c.items()}}


def video_activity(K, S, fps, p):
    """Whole-video activity: per-frame score and active runs in seconds (None, None if shoulders are never found)."""
    F = activity_features(K, S, fps)
    if F is None:
        return None, None
    act, score = active_mask(F, fps, p)
    return score, [(a / fps, b / fps) for a, b in _runs(act)]


def detect_interval_video(runs, vid_end, anchor, warp, p):
    """Interval for one clip: the ORIGINAL anchor mapped through the video warp (lag + slope * t), then select_interval
    (expected window from lag_start / lag_end, bounds snapped to whole-video activity edges within +-snap_s), clamped
    to the video."""
    lag, slope = warp
    return select_interval(0.0, vid_end, runs, (lag + slope * anchor[0], lag + slope * anchor[1]), p)


# ---------------------------------------------------------------- automatic signer crop
def signer_box(K, S, frame_wh, p):
    """Static clip-level box from pooled keypoint percentiles over the selected frames, plus margins in shoulder
    widths. Uses body (0-12) and both hands; missing landmarks are ignored. Returns (x0, y0, W, H), fail flag."""
    Wf, Hf = frame_wh
    SW = shoulder_width(K, S)
    idx = list(range(0, 13)) + LHAND + RHAND
    m = S[:, idx] > THR
    pts = K[:, idx][m]
    if len(pts) < 20 or not np.isfinite(SW):
        return (0.0, 0.0, float(Wf), float(Hf)), "fallback_full_frame"
    q = p["pct"]
    xl, xh = np.percentile(pts[:, 0], [q, 100 - q]); yl, yh = np.percentile(pts[:, 1], [q, 100 - q])
    x0 = max(0.0, xl - p["margin_x"] * SW); x1 = min(float(Wf), xh + p["margin_x"] * SW)
    y0 = max(0.0, yl - p["margin_top"] * SW)
    y1 = float(Hf) if p["to_bottom"] else min(float(Hf), yh + p["margin_bottom"] * SW)
    if x1 - x0 < 16 or y1 - y0 < 16:
        return (0.0, 0.0, float(Wf), float(Hf)), "fallback_degenerate"
    return (float(x0), float(y0), float(x1 - x0), float(y1 - y0)), None


def box_iou(a, b):
    ax0, ay0, aw, ah = a; bx0, by0, bw, bh = b
    ix = max(0.0, min(ax0 + aw, bx0 + bw) - max(ax0, bx0)); iy = max(0.0, min(ay0 + ah, by0 + bh) - max(ay0, by0))
    inter = ix * iy
    return inter / (aw * ah + bw * bh - inter) if inter > 0 else 0.0


def interval_iou(a, b):
    inter = max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
    union = max(a[1], b[1]) - min(a[0], b[0])
    return inter / union if union > 0 else 0.0


# ---------------------------------------------------------------- Uni-Sign input
def to_unisign(K, S, box):
    """Uni-Sign pose dict: keypoints (pixels - box origin) / (W, H), one person per frame, as the official pkls."""
    x0, y0, W, H = box
    k = (K - np.array([x0, y0])) / np.array([W, H])
    # dtypes exactly as the official pkls: keypoints float64, scores float32
    return {"keypoints": [k[t][None].astype(np.float64) for t in range(len(K))],
            "scores": [S[t][None].astype(np.float32) for t in range(len(S))],
            "w_h": [int(round(W)), int(round(H))]}
