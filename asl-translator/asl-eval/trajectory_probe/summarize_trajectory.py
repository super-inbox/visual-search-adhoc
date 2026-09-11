#!/usr/bin/env python3
"""Phase D1 trajectory-tracking POC — derived signals + tracking-quality
metrics, computed from a landmarks.json produced by extract_trajectory.py.

Pure arithmetic over the raw keypoints/scores already extracted — makes no
model call, does not re-run the tracker, and infers NO ASL gloss, handshape,
or semantic label of any kind. Every signal here is a generic kinematic
quantity (position, velocity, distance, threshold-based band) that would
apply to tracking any moving human, not an ASL-specific interpretation.

Usage (plain python3, no special env needed — only json/math/statistics):
    python3 summarize_trajectory.py <landmarks_json> <out_summary_json>
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keypoint_schema as ks  # noqa: E402

THR = ks.KPT_DETECTED_THRESHOLD


def _hand_slice(xy, sc, start, end):
    return xy[start:end], sc[start:end]


def _hand_detected(sc_slice: list[float]) -> bool:
    n_above = sum(1 for s in sc_slice if s >= THR)
    return n_above >= (len(sc_slice) / 2.0)  # majority of the 21 points visible


def _hand_center(xy_slice, sc_slice):
    pts = [(x, y, s) for (x, y), s in zip(xy_slice, sc_slice) if s >= THR]
    if len(pts) < 3:  # need at least 3 confident points to trust a centroid
        return None
    wsum = sum(s for _, _, s in pts)
    cx = sum(x * s for x, y, s in pts) / wsum
    cy = sum(y * s for x, y, s in pts) / wsum
    return (cx, cy)


def _body_detected(sc_body: list[float]) -> bool:
    n_above = sum(1 for s in sc_body if s >= THR)
    return n_above >= 12  # >=12 of 17 COCO body points visible


def summarize(landmarks: dict) -> dict:
    fw, fh = landmarks["frame_width"], landmarks["frame_height"]
    frames = landmarks["frames"]
    n_total = len(frames)

    n_body_detected = 0
    n_left_hand_detected = 0
    n_right_hand_detected = 0
    n_multi_person = 0

    body_scores, left_hand_scores, right_hand_scores = [], [], []
    left_wrist_series = []   # (t_s, x_norm, y_norm, score) sparse, only when body detected
    right_wrist_series = []
    left_hand_center_series = []   # (t_s, x_norm, y_norm) only when supported
    right_hand_center_series = []
    two_hand_distance_series = []
    band_counts = {"left": {"face_or_above": 0, "shoulder_to_chest": 0, "below_chest": 0, "unclassified": 0},
                   "right": {"face_or_above": 0, "shoulder_to_chest": 0, "below_chest": 0, "unclassified": 0}}

    for fr in frames:
        if fr["n_people_detected"] > 1:
            n_multi_person += 1
        if fr["n_people_detected"] == 0 or fr["keypoints_xy"] is None:
            continue
        xy = fr["keypoints_xy"]
        sc = fr["keypoints_score"]
        t_s = fr["t_s"]

        body_sc = sc[ks.BODY_START:ks.BODY_END]
        body_scores.extend(body_sc)
        if _body_detected(body_sc):
            n_body_detected += 1

        lh_xy, lh_sc = _hand_slice(xy, sc, ks.LEFT_HAND_START, ks.LEFT_HAND_END)
        rh_xy, rh_sc = _hand_slice(xy, sc, ks.RIGHT_HAND_START, ks.RIGHT_HAND_END)
        left_hand_scores.extend(lh_sc)
        right_hand_scores.extend(rh_sc)
        left_detected = _hand_detected(lh_sc)
        right_detected = _hand_detected(rh_sc)
        if left_detected:
            n_left_hand_detected += 1
        if right_detected:
            n_right_hand_detected += 1

        lw_x, lw_y = xy[ks.LEFT_WRIST_IDX]
        rw_x, rw_y = xy[ks.RIGHT_WRIST_IDX]
        lw_s, rw_s = sc[ks.LEFT_WRIST_IDX], sc[ks.RIGHT_WRIST_IDX]
        if lw_s >= THR:
            left_wrist_series.append((t_s, lw_x / fw, lw_y / fh, lw_s))
        if rw_s >= THR:
            right_wrist_series.append((t_s, rw_x / fw, rw_y / fh, rw_s))

        lc = _hand_center(lh_xy, lh_sc)
        rc = _hand_center(rh_xy, rh_sc)
        if lc:
            left_hand_center_series.append((t_s, lc[0] / fw, lc[1] / fh))
        if rc:
            right_hand_center_series.append((t_s, rc[0] / fw, rc[1] / fh))
        if lc and rc:
            d = ((lc[0] - rc[0]) ** 2 + (lc[1] - rc[1]) ** 2) ** 0.5 / max(fw, fh)
            two_hand_distance_series.append(d)

        nose_s = sc[ks.NOSE_IDX]
        lsh_s, rsh_s = sc[ks.LEFT_SHOULDER_IDX], sc[ks.RIGHT_SHOULDER_IDX]
        if nose_s >= THR and lsh_s >= THR and rsh_s >= THR:
            nose_y = xy[ks.NOSE_IDX][1]
            shoulder_y = (xy[ks.LEFT_SHOULDER_IDX][1] + xy[ks.RIGHT_SHOULDER_IDX][1]) / 2.0
            chest_y = shoulder_y + (shoulder_y - nose_y)
            for side, center in (("left", lc), ("right", rc)):
                if center is None:
                    band_counts[side]["unclassified"] += 1
                    continue
                hy = center[1]
                if hy <= nose_y:
                    band_counts[side]["face_or_above"] += 1
                elif hy <= chest_y:
                    band_counts[side]["shoulder_to_chest"] += 1
                else:
                    band_counts[side]["below_chest"] += 1
        else:
            band_counts["left"]["unclassified"] += 1
            band_counts["right"]["unclassified"] += 1

    def _velocity_stats(center_series):
        """Speed between IMMEDIATELY consecutive detected frames only (skips
        gaps across an occlusion so a missing-frame gap is never read as a
        fast movement)."""
        speeds = []
        for i in range(1, len(center_series)):
            t0, x0, y0 = center_series[i - 1][:3]
            t1, x1, y1 = center_series[i][:3]
            dt = t1 - t0
            if dt <= 0 or dt > 1.5 / max(landmarks["source_fps"], 1e-6):
                continue  # not consecutive frames — skip, don't infer speed across a gap
            dist = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            speeds.append(dist / dt)
        if not speeds:
            return {"mean": None, "median": None, "max": None, "n_samples": 0,
                     "unit": "normalized_frame_diagonal_per_s"}
        return {"mean": round(statistics.mean(speeds), 4),
                "median": round(statistics.median(speeds), 4),
                "max": round(max(speeds), 4),
                "n_samples": len(speeds),
                "unit": "normalized_frame_diagonal_per_s"}

    def _discontinuities(center_series, label):
        """Frame-to-frame displacement spikes: a step between two
        IMMEDIATELY consecutive detected frames whose distance exceeds
        4x that clip's own median consecutive-step distance. Self-calibrated
        per clip (no fixed pixel threshold) — flagged as a candidate
        discontinuity/possible detector jump, not a confirmed identity
        swap (rtmlib's per-frame detect+pose has no persistent track ID)."""
        steps = []
        for i in range(1, len(center_series)):
            t0, x0, y0 = center_series[i - 1][:3]
            t1, x1, y1 = center_series[i][:3]
            dt = t1 - t0
            if dt <= 0 or dt > 1.5 / max(landmarks["source_fps"], 1e-6):
                continue
            dist = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            steps.append((t1, dist))
        if len(steps) < 3:
            return {"n_candidates": 0, "candidate_times_s": [], "median_step": None}
        dists = [d for _, d in steps]
        med = statistics.median(dists)
        thr = max(med * 4.0, 0.02)  # floor so near-zero median doesn't flag noise
        candidates = [round(t, 3) for t, d in steps if d > thr]
        return {"n_candidates": len(candidates), "candidate_times_s": candidates,
                "median_step": round(med, 4), "flag_threshold": round(thr, 4)}

    def _mean_median(values):
        if not values:
            return {"mean": None, "median": None, "n": 0}
        return {"mean": round(statistics.mean(values), 4),
                "median": round(statistics.median(values), 4), "n": len(values)}

    summary = {
        "clip_id": landmarks["clip_id"],
        "duration_s": round(n_total / landmarks["source_fps"], 3) if landmarks["source_fps"] else None,
        "n_frames_total": n_total,
        "n_frames_with_body_detection": n_body_detected,
        "n_frames_with_left_hand_detection": n_left_hand_detected,
        "n_frames_with_right_hand_detection": n_right_hand_detected,
        "n_frames_multi_person_detected": n_multi_person,
        "missing_tracking_pct": {
            "body": round(100 * (1 - n_body_detected / n_total), 2) if n_total else None,
            "left_hand": round(100 * (1 - n_left_hand_detected / n_total), 2) if n_total else None,
            "right_hand": round(100 * (1 - n_right_hand_detected / n_total), 2) if n_total else None,
        },
        "confidence": {
            "body": _mean_median(body_scores),
            "left_hand": _mean_median(left_hand_scores),
            "right_hand": _mean_median(right_hand_scores),
        },
        "left_wrist_trajectory": {
            "n_points": len(left_wrist_series),
            "series_t_x_y": [[round(t, 3), round(x, 4), round(y, 4)] for t, x, y, s in left_wrist_series],
        },
        "right_wrist_trajectory": {
            "n_points": len(right_wrist_series),
            "series_t_x_y": [[round(t, 3), round(x, 4), round(y, 4)] for t, x, y, s in right_wrist_series],
        },
        "left_hand_center_trajectory": {
            "n_points": len(left_hand_center_series),
            "series_t_x_y": [[round(t, 3), round(x, 4), round(y, 4)] for t, x, y in left_hand_center_series],
        },
        "right_hand_center_trajectory": {
            "n_points": len(right_hand_center_series),
            "series_t_x_y": [[round(t, 3), round(x, 4), round(y, 4)] for t, x, y in right_hand_center_series],
        },
        "wrist_velocity": {
            "left": _velocity_stats(left_wrist_series),
            "right": _velocity_stats(right_wrist_series),
        },
        "hand_center_velocity": {
            "left": _velocity_stats(left_hand_center_series),
            "right": _velocity_stats(right_hand_center_series),
        },
        "two_hand_distance": {
            **_mean_median(two_hand_distance_series),
            "min": round(min(two_hand_distance_series), 4) if two_hand_distance_series else None,
            "max": round(max(two_hand_distance_series), 4) if two_hand_distance_series else None,
            "unit": "normalized_frame_diagonal",
        },
        "hand_relative_to_body_band": {
            side: {
                **{k: v for k, v in band_counts[side].items()},
                "band_definition": "face_or_above: hand_y <= nose_y; "
                                    "shoulder_to_chest: nose_y < hand_y <= shoulder_y+(shoulder_y-nose_y); "
                                    "below_chest: hand_y > that line. Only classified when nose+both "
                                    "shoulders are above the detection threshold in that frame.",
            }
            for side in ("left", "right")
        },
        "discontinuity_candidates": {
            "left_hand_center": _discontinuities(left_hand_center_series, "left"),
            "right_hand_center": _discontinuities(right_hand_center_series, "right"),
            "note": "A candidate is a frame-to-frame jump >4x that clip's own median "
                    "consecutive-frame step for that hand. This is a self-calibrated "
                    "discontinuity heuristic, not a confirmed identity swap — rtmlib's "
                    "per-frame detect+pose call carries no persistent track ID across frames.",
        },
        "note": "All signals here are generic kinematic quantities (position/velocity/"
                "distance/threshold bands) computed from raw tracker output. No ASL "
                "gloss, handshape, or semantic label is inferred anywhere in this file.",
    }
    return summary


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: summarize_trajectory.py <landmarks_json> <out_summary_json>", file=sys.stderr)
        return 2
    landmarks = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    summary = summarize(landmarks)
    out_path = Path(sys.argv[2])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"{summary['clip_id']}: body {summary['missing_tracking_pct']['body']}% missing, "
          f"L-hand {summary['missing_tracking_pct']['left_hand']}% missing, "
          f"R-hand {summary['missing_tracking_pct']['right_hand']}% missing -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
