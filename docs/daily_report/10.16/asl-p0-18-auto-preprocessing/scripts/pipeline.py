"""P0-18 automatic preprocessing for one video (shared by dev build_conditions.py and the H18 one-shot runner).

Per video: whole-video signer track -> activity score + runs -> video warp (p018_lib.video_warp) from the ORIGINAL
sentence timeline of ALL the video's clips. Per clip: interval (p018_lib.detect_interval_video), then the signer crop
over the interval's frames (p018_lib.signer_box), then the Uni-Sign pose dict.

Conditions (production-legal: video frames + ORIGINAL timing only):
  A_old          original window, full frame                                  (old pipeline)
  B_auto         automatic interval + automatic crop                          (the P0-18 pipeline)
  B_time_only    automatic interval, full frame                               (ablation)
  B_crop_only    original window, automatic crop                              (ablation)
  B_lag_only     video warp + expected window, no activity snapping, auto crop (ablation)
DEV-ONLY oracle conditions (need realigned boundaries; never built for the holdout):
  O_time         realigned window, full frame
  O_time_crop    realigned window, automatic crop
"""
import p018_lib as L

PROD = ["A_old", "B_auto", "B_time_only", "B_crop_only", "B_lag_only"]
ORACLE = ["O_time", "O_time_crop"]
_WINDOW = {"A_old": "orig", "B_auto": "auto", "B_time_only": "auto", "B_crop_only": "orig", "B_lag_only": "lag",
           "O_time": "oracle", "O_time_crop": "oracle"}
_FULL_FRAME = {"A_old", "B_time_only", "O_time"}


def video_intervals(V, clips, sentences, PI):
    """V: pose_extract.VideoPose; clips: [(clip_id, start, end)] to process; sentences: [(start, end)] ORIGINAL timing
    of ALL clips of the video. Returns (video record, {clip_id: interval record})."""
    tr = V.signer_track()
    vid_end = V.n / V.fps
    score, runs = (None, None) if tr is None else L.video_activity(tr[0], tr[1], V.fps, PI)
    if score is None:
        wp = {"lag": 0.0, "slope": 1.0, "r": None, "fail": "no_shoulders"}
    else:
        wp = L.video_warp(score, V.fps, sentences, PI)
    vrec = {"lag": wp["lag"], "slope": wp["slope"], "warp_r": wp["r"], "warp_fail": wp["fail"], "frames": V.n,
            "fps": V.fps, "n_runs": None if runs is None else len(runs)}
    warp = (wp["lag"], wp["slope"])
    out = {}
    for cid, s, e in clips:
        det = L.detect_interval_video(runs, vid_end, (s, e), warp, PI)
        det0 = L.detect_interval_video(runs, vid_end, (s, e), warp, dict(PI, snap_s=0.0))
        out[cid] = {"anchor": [s, e], "auto": [det["start"], det["end"]], "auto_fail": det["fail"],
                    "lag_window": [det0["start"], det0["end"]], "E": det["E"]}
    return vrec, out


def build_clip(V, cid, rec, conds, PC, oracle=None):
    """Uni-Sign pose dicts {condition: dict} for one clip plus its build record (boxes, failures, frame counts)."""
    win = {"orig": rec["anchor"], "auto": rec["auto"], "lag": rec["lag_window"]}
    if oracle is not None:
        win["oracle"] = oracle
    full = (0.0, 0.0, float(V.frame_wh[0]), float(V.frame_wh[1]))
    pk, m = {}, {"box": {}, "frames": {}, "crop_fail": {}, "cond_fail": {}, "n_multi": {}}
    for c in conds:
        w = win.get(_WINDOW[c])
        cp = None if w is None else V.clip_pose(*w)
        if cp is None or len(cp[0]) < 2:
            m["cond_fail"][c] = "too_few_frames"; continue
        K, S, t0, n_multi = cp
        box, bfail = (full, None) if c in _FULL_FRAME else L.signer_box(K, S, V.frame_wh, PC)
        if bfail:
            m["crop_fail"][c] = bfail
        m["box"][c], m["frames"][c], m["n_multi"][c] = box, len(K), int(n_multi)
        pk[c] = L.to_unisign(K, S, box)
    return pk, m


def clip_failed(rec, m, arm="B_auto"):
    """Pre-registered failure of the primary arm on a clip (EXPERIMENT_PLAN.md §3, P3): its condition cannot be built,
    its crop falls back to the full frame, or (only for an arm with automatic timing) the interval detector flags a
    failure."""
    timed = _WINDOW[arm] in ("auto", "lag")
    return bool((timed and rec.get("auto_fail")) or m["cond_fail"].get(arm) or m["crop_fail"].get(arm))
