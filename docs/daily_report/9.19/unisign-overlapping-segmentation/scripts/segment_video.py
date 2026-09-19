#!/usr/bin/env python3
"""Manager task (b): deterministic, motion-aware OVERLAPPING video segmentation.

RESEARCH ONLY (research repo). Nothing here is imported by / copied into curify-studio.

Motion signal (REUSED, not re-implemented)
------------------------------------------
`probe_motion()` and `segment_runs()` from asl-translator/asl-eval/run_current_model.py,
which are line-for-line ports of curify-studio's production asl_utils._probe_motion /
_segment_runs (verified by diffing the executable code; only docstrings differ):
  * one ffmpeg pass, 4 Hz, 160 px wide, grayscale, mean |frame[i+1]-frame[i]|
  * times[i] = (i+1)/4  ->  temporal resolution 0.25 s
  * segment_runs() smooths with a 5-tap boxcar (np.convolve mode="same") before
    thresholding but DISCARDS the smoothed series, so the identical 3-line smoothing is
    re-applied here to get a per-time motion value.
NOT reused: allocate_timestamps() (picks a fixed budget of still frames for a VLM prompt).

Algorithm (greedy forward pass; depends ONLY on video motion + duration)
------------------------------------------------------------------------
Parameters: TARGET 6.0 s, MIN 4.0 s, MAX 8.0 s, OVERLAP 1.0 s (allowed 0.5-1.5 s).
For the segment starting at s:
  1. if video_end - s <= MAX: this is the final segment, ends at video_end. done.
  2. else END e: search the 0.25 s grid over the legal window [s+MIN, s+MAX], restricted
     so that a following segment of >= MIN seconds still fits (e <= video_end - MIN + 1.5).
     cost(e) = motion_percentile_rank(e) + LAMBDA * |e - (s+TARGET)| / 2.0
     (low motion = cheap; the distance term pulls toward the 6 s target). Take argmin;
     ties -> smaller |e-(s+TARGET)|, then earlier e.
  3. NEXT START s': search the grid over [e-1.5, e-0.5] (=overlap 0.5-1.5 s), restricted to
     video_end - s' >= MIN.
     cost(s') = motion_percentile_rank(s') + LAMBDA * |(e - s') - OVERLAP| / 0.5
  4. repeat from s'.
Chronology is preserved by construction (s' > s, e' > e). No gaps (overlap >= 0.5 s > 0).
The last segment is never shorter than MIN unless the whole video is shorter than MIN.
No reference text and no Uni-Sign output is read anywhere.

Cutting: video-only libx264 re-encode (crf 18, -fps_mode passthrough) so cuts are
frame-accurate and source frames are kept 1:1; audio dropped (Uni-Sign never reads it).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "asl-translator" / "asl-eval"))
from run_current_model import (  # noqa: E402  (existing detector, unmodified)
    ABS_MOTION_FLOOR, IDLE_QUANTILE, PROBE_FPS, PROBE_WIDTH, probe_motion, segment_runs,
)

GRID = 1.0 / PROBE_FPS  # 0.25 s
TARGET_DUR, MIN_DUR, MAX_DUR = 6.0, 4.0, 8.0
TARGET_OVL, MIN_OVL, MAX_OVL = 1.0, 0.5, 1.5
LAMBDA = 0.30
UNISIGN_MAX_LENGTH = 256


def q(x: float) -> int:
    return int(round(x / GRID))


def smoothed_motion(motion: list[float]) -> np.ndarray:
    """Identical kernel/mode to run_current_model.segment_runs()."""
    m = np.asarray(motion, dtype=np.float64)
    if len(m) >= 5:
        m = np.convolve(m, np.ones(5) / 5.0, mode="same")
    return m


def probe_video(video: str) -> dict:
    j = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,codec_name,r_frame_rate,avg_frame_rate,nb_frames,duration",
         "-show_entries", "format=duration", "-of", "json", video],
        capture_output=True, text=True, check=True).stdout)
    pts = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=pts_time",
         "-of", "csv=p=0", video], capture_output=True, text=True, check=True).stdout.split()
    pts = np.array(sorted(float(x.split(",")[0]) for x in pts if x.split(",")[0] not in ("", "N/A")))
    st = j["streams"][0]
    return {"stream": st, "container_duration": float(j["format"]["duration"]),
            "video_end": float(st["duration"]), "pts": pts}


def frames_in(pts: np.ndarray, s: float, e: float) -> int:
    """exact number of source frames with pts in [s, e)."""
    return int(np.searchsorted(pts, e - 1e-6, "left") - np.searchsorted(pts, s - 1e-6, "left"))


def build_segments(video_end: float, pts: np.ndarray, times: list[float], motion: list[float]) -> dict:
    m_s = smoothed_motion(motion)
    order = m_s.argsort().argsort()
    rank = {q(t): float(order[i]) / (len(m_s) - 1) for i, t in enumerate(times)}    # percentile rank in THIS video
    val = {q(t): float(m_s[i]) for i, t in enumerate(times)}
    raw = {q(t): float(motion[i]) for i, t in enumerate(times)}
    runs = segment_runs(times, motion)
    thresh = max(float(np.quantile(m_s, IDLE_QUANTILE)), ABS_MOTION_FLOOR)

    def cand(lo: float, hi: float):
        return [k for k in range(q(lo), q(hi) + 1) if k in rank]

    def in_idle(t: float) -> bool | None:
        for r in runs:
            if r.start_s <= t <= r.end_s:
                return not r.active
        return None

    def local_min(k: int) -> bool:
        nb = [val[j] for j in (k - 2, k - 1, k + 1, k + 2) if j in val]
        return bool(nb) and val[k] <= min(nb)

    rows: list[dict] = []
    s = 0.0
    seg_start_reason = "video_start"
    while True:
        rec: dict = {"segment_id": len(rows), "start_sec": s, "start_reason": seg_start_reason}
        if video_end - s <= MAX_DUR + 1e-9:
            rec.update(end_sec=video_end, end_reason="video_end (remaining <= MAX)", end_search=None)
            rows.append(rec)
            break
        # --- choose END e (also leaves room for a >= MIN follow-on segment)
        lo, hi = s + MIN_DUR, min(s + MAX_DUR, video_end - MIN_DUR + MAX_OVL)
        ends = cand(lo, hi)
        cost = lambda k: rank[k] + LAMBDA * abs(k * GRID - (s + TARGET_DUR)) / 2.0  # noqa: E731
        ek = min(ends, key=lambda k: (round(cost(k), 9), abs(k * GRID - (s + TARGET_DUR)), k))
        e = ek * GRID
        rec.update(end_sec=e, end_reason="argmin(motion_rank + %.2f*|dur-6|/2) over legal window" % LAMBDA,
                   end_search={"window_sec": [round(lo, 3), round(hi, 3)], "n_candidates": len(ends),
                               "cost": round(cost(ek), 4),
                               "window_mean_rank": round(float(np.mean([rank[k] for k in ends])), 3),
                               "window_min_rank": round(min(rank[k] for k in ends), 3)})
        rows.append(rec)
        # --- choose NEXT START s' (overlap 0.5-1.5 s)
        starts = [k for k in cand(e - MAX_OVL, e - MIN_OVL) if video_end - k * GRID >= MIN_DUR - 1e-9]
        sk = min(starts, key=lambda k: (round(rank[k] + LAMBDA * abs((e - k * GRID) - TARGET_OVL) / 0.5, 9),
                                        abs((e - k * GRID) - TARGET_OVL), k))
        s = sk * GRID
        seg_start_reason = "argmin(motion_rank + %.2f*|overlap-1|/0.5) over overlap window [0.5,1.5]" % LAMBDA
        rows[-1]["_next_start_choice"] = {"window_sec": [round(e - MAX_OVL, 3), round(e - MIN_OVL, 3)],
                                          "n_candidates": len(starts)}

    segs = []
    prev_end = None
    for r in rows:
        s_, e_ = r["start_sec"], r["end_sec"]
        sk_, ek_ = q(s_), q(e_)
        is_first, is_last = r["segment_id"] == 0, r["segment_id"] == len(rows) - 1
        nfr = frames_in(pts, s_, e_)

        def bmetrics(t, k, absent):
            if absent or k not in rank:
                return None
            return {"time_sec": round(t, 3), "smoothed_motion": round(val[k], 4), "raw_motion_0p25s": round(raw[k], 4),
                    "motion_percentile_rank": round(rank[k], 3), "above_idle_threshold": bool(val[k] > thresh),
                    "in_idle_run": in_idle(t), "is_local_min_pm0p5s": local_min(k)}

        segs.append({
            "segment_id": r["segment_id"],
            "start_sec": round(s_, 3), "end_sec": round(e_, 3), "duration_sec": round(e_ - s_, 3),
            "overlap_with_prev_sec": 0.0 if prev_end is None else round(prev_end - s_, 3),
            "expected_frames_pts": nfr,
            "subsampling_required_by_unisign": nfr > UNISIGN_MAX_LENGTH,
            "start_boundary": {"reason": r["start_reason"], "search": None if is_first else rows[r["segment_id"] - 1]["_next_start_choice"],
                               "motion": bmetrics(s_, sk_, is_first)},
            "end_boundary": {"reason": r["end_reason"], "search": r["end_search"], "motion": bmetrics(e_, ek_, is_last)},
            "source": "wrapper_segmentation",
        })
        prev_end = e_
    return {"segments": segs, "rank": rank, "val": val, "idle_threshold": thresh}


def validate(segs: list[dict], video_end: float) -> list[str]:
    p = []
    if segs[0]["start_sec"] != 0.0:
        p.append("first segment does not start at 0")
    if abs(segs[-1]["end_sec"] - video_end) > 0.002:
        p.append("last segment does not end at video end")
    for a, b in zip(segs, segs[1:]):
        ov = a["end_sec"] - b["start_sec"]
        if not (MIN_OVL - 1e-6 <= ov <= MAX_OVL + 1e-6):
            p.append(f"overlap {ov:.3f}s between {a['segment_id']},{b['segment_id']} outside [{MIN_OVL},{MAX_OVL}]")
        if not (b["start_sec"] > a["start_sec"] and b["end_sec"] > a["end_sec"]):
            p.append(f"chronology broken between {a['segment_id']},{b['segment_id']}")
    for s in segs:
        if not (MIN_DUR - 1e-6 <= s["duration_sec"] <= MAX_DUR + 1e-6):
            p.append(f"segment {s['segment_id']} duration {s['duration_sec']} outside [{MIN_DUR},{MAX_DUR}]")
    return p


def cut_segment(video: str, seg: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{seg['start_sec']:.3f}", "-i", video,
         "-t", f"{seg['duration_sec']:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", "-pix_fmt", "yuv420p", "-fps_mode", "passthrough", str(out)],
        check=True, capture_output=True)


def verify_clip(path: Path) -> dict:
    j = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
         "stream=nb_read_frames,duration,r_frame_rate,width,height,codec_name", "-show_entries", "format=duration",
         "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout)
    st = j["streams"][0]
    first = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-frames:v", "1", "-f", "null", "-"],
                           capture_output=True, text=True)
    return {"readable": first.returncode == 0 and first.stderr.strip() == "", "frames_actual": int(st["nb_read_frames"]),
            "duration_actual_sec": float(st["duration"]), "resolution": f'{st["width"]}x{st["height"]}',
            "codec": st["codec_name"], "size_bytes": path.stat().st_size}


def ascii_strip(val: dict, segs: list[dict], video_end: float) -> str:
    """One row per 0.25 s tick: smoothed motion bar + boundary marks (E=segment end, S=next start)."""
    ks = sorted(val)
    mx = max(val.values())
    marks: dict[int, str] = {}
    for s in segs:
        if s["segment_id"] > 0:
            marks[q(s["start_sec"])] = marks.get(q(s["start_sec"]), "") + f"S{s['segment_id']}"
        if s["segment_id"] < len(segs) - 1:
            marks[q(s["end_sec"])] = marks.get(q(s["end_sec"]), "") + f"E{s['segment_id']}"
    lines = []
    for k in ks:
        bar = "#" * int(round(40 * val[k] / mx))
        lines.append(f"{k*GRID:6.2f}s {val[k]:6.2f} |{bar:<40}| {marks.get(k, '')}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--clips-dir", required=True, help="derived mp4s; keep OUTSIDE git")
    ap.add_argument("--strip-out", help="write the ASCII motion strip here")
    a = ap.parse_args()

    info = probe_video(a.video)
    video_end, pts = info["video_end"], info["pts"]
    times, motion = probe_motion(a.video)
    print(f"video_end={video_end}s frames={len(pts)} motion samples={len(times)} t=[{times[0]},{times[-1]}]")

    res = build_segments(video_end, pts, times, motion)
    segs, rank, val = res["segments"], res["rank"], res["val"]
    problems = validate(segs, video_end)

    # diagnostic: chosen boundaries vs (a) fixed 6s/1s grid, (b) uniformly-random cut inside each legal window
    chosen = [s[b]["motion"]["motion_percentile_rank"] for s in segs for b in ("start_boundary", "end_boundary")
              if s[b]["motion"]]
    fixed = []
    st = TARGET_DUR - TARGET_OVL
    k = 0
    while (k + 1) * st + TARGET_OVL < video_end - MIN_DUR + 1e-9:
        for t in (k * st + TARGET_DUR, (k + 1) * st):
            fixed.append(rank[q(t)]) if q(t) in rank else None
        k += 1
    windows = [s["end_boundary"]["search"]["window_mean_rank"] for s in segs if s["end_boundary"]["search"]]

    clips = Path(a.clips_dir)
    for s in segs:
        out = clips / f"segment_{s['segment_id']:02d}.mp4"
        cut_segment(a.video, s, out)
        v = verify_clip(out)
        v["frames_match_expected"] = v["frames_actual"] == s["expected_frames_pts"]
        v["duration_match_expected"] = abs(v["duration_actual_sec"] - s["duration_sec"]) < 0.05
        s["file"] = out.name
        s["clip_verification"] = v
        print(f"seg {s['segment_id']} [{s['start_sec']:.2f},{s['end_sec']:.2f}] d={s['duration_sec']:.2f} "
              f"ovl={s['overlap_with_prev_sec']:.2f} frames={v['frames_actual']} (expected {s['expected_frames_pts']}) "
              f"readable={v['readable']}")
    for s, n in zip(segs, segs[1:]):
        if not (n["clip_verification"]["frames_actual"] and s["clip_verification"]["readable"]):
            problems.append("unreadable/empty clip")
    problems += [f"segment {s['segment_id']} frame/duration mismatch after cut" for s in segs
                 if not (s["clip_verification"]["frames_match_expected"] and s["clip_verification"]["duration_match_expected"]
                         and s["clip_verification"]["readable"])]

    manifest = {
        "task": "manager task (b) overlapping segmentation",
        "source_video": str(Path(a.video).resolve().relative_to(REPO)),
        "clip_id": Path(a.video).stem,
        "video": {"duration_sec": video_end, "container_duration_sec": info["container_duration"],
                  "frame_count_ffprobe_pts": int(len(pts)), "r_frame_rate": info["stream"]["r_frame_rate"],
                  "resolution": f'{info["stream"]["width"]}x{info["stream"]["height"]}', "codec": info["stream"]["codec_name"]},
        "motion_detector": {
            "reused_from": "asl-translator/asl-eval/run_current_model.py::probe_motion + segment_runs "
                           "(identical executable code to curify-studio origin/main curify_background/app/utils/asl_utils.py)",
            "probe_fps": PROBE_FPS, "probe_width_px": PROBE_WIDTH, "resolution_sec": GRID, "n_samples": len(times),
            "smoothing": "5-tap boxcar, np.convolve mode='same' (same as segment_runs)",
            "idle_quantile": IDLE_QUANTILE, "abs_motion_floor": ABS_MOTION_FLOOR,
            "idle_threshold_smoothed_motion": round(res["idle_threshold"], 4),
            "not_reused": "allocate_timestamps / allocate_timestamps_uniform / extract_frames (VLM still-frame budgeting)"},
        "parameters": {"target_duration_sec": TARGET_DUR, "min_duration_sec": MIN_DUR, "max_duration_sec": MAX_DUR,
                       "target_overlap_sec": TARGET_OVL, "overlap_range_sec": [MIN_OVL, MAX_OVL], "distance_weight_lambda": LAMBDA,
                       "grid_sec": GRID, "unisign_max_length_frames": UNISIGN_MAX_LENGTH},
        "timestamp_semantics": "start_sec/end_sec are wrapper/source-derived segmentation timestamps (source=wrapper_segmentation). "
                               "They are NOT Uni-Sign-native alignment; Uni-Sign has none.",
        "inputs_used_for_boundaries": "video pixels (motion) + video duration ONLY. No reference text, no model output.",
        "num_segments": len(segs),
        "validation_problems": problems,
        "boundary_motion_diagnostic": {
            "note": "percentile rank of smoothed motion within this video: 0 = calmest, 1 = busiest; random cut ~0.5",
            "mean_rank_chosen_interior_boundaries": round(float(np.mean(chosen)), 3),
            "mean_rank_naive_fixed_6s_1s_grid_boundaries": round(float(np.mean(fixed)), 3) if fixed else None,
            "mean_rank_of_uniform_random_cut_in_legal_windows": round(float(np.mean(windows)), 3) if windows else None,
        },
        "segments": segs,
    }
    Path(a.manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(a.manifest).write_text(json.dumps(manifest, indent=2))
    if a.strip_out:
        Path(a.strip_out).write_text(ascii_strip(val, segs, video_end) + "\n")
    print(f"wrote {a.manifest}; problems={problems or 'none'}")
    print("boundary diagnostic:", manifest["boundary_motion_diagnostic"])
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
