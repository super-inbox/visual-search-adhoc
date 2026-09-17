#!/usr/bin/env python3
"""Phase D2 — render RTMPose trajectory data as an observation-level TEXT
block, for injection into the Gemini prompt as the treatment condition's
one added Part.

STRICT CONSTRAINT (per manager instruction): this renders raw geometric/
kinematic observations ONLY — positions, confidence, velocity, band
percentages, distances. It NEVER writes an ASL gloss, a guess at meaning,
or any phrase like "this looks like the sign for X". If you are editing
this file, do not add any such phrase.

Operates on a time-sliced trajectory summary, built by
summarize_trajectory.summarize() run over only the frames that fall
inside one batch's [t_start, t_end] window — so a multi-batch clip's
later batches are not given trajectory information from time the model
in that call cannot see (kept observation-scope-matched to what the
image frames themselves cover).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import summarize_trajectory as st  # noqa: E402


def slice_landmarks_by_time(landmarks: dict, t_start: float, t_end: float) -> dict:
    frames = [f for f in landmarks["frames"] if f["t_s"] is not None and t_start <= f["t_s"] <= t_end]
    return {**landmarks, "frames": frames}


def _sample_path(series: list, n: int = 6) -> list:
    """Evenly-spaced sample of a (t, x, y) series, for a compact prompt
    representation — not the full per-frame series."""
    if not series:
        return []
    if len(series) <= n:
        return series
    idx = [round(i * (len(series) - 1) / (n - 1)) for i in range(n)]
    seen = sorted(set(idx))
    return [series[i] for i in seen]


def render_hand_block(label: str, summary: dict, side: str) -> str:
    n_total = summary["n_frames_total"]
    n_det = summary[f"n_frames_with_{side}_hand_detection"]
    pct_det = round(100 * n_det / n_total, 1) if n_total else 0.0
    conf = summary["confidence"][f"{side}_hand"]["mean"]
    center = summary[f"{side}_hand_center_trajectory"]["series_t_x_y"]
    path_sample = _sample_path(center, 6)
    path_str = "; ".join(f"t={t:.2f}s (x={x:.2f},y={y:.2f})" for t, x, y in path_sample) or "no confident position samples in this window"
    vel = summary["hand_center_velocity"][side]
    band = summary["hand_relative_to_body_band"][side]
    band_total = band["face_or_above"] + band["shoulder_to_chest"] + band["below_chest"] + band["unclassified"]
    def bpct(k):
        return round(100 * band[k] / band_total, 0) if band_total else None
    disc = summary["discontinuity_candidates"][f"{side}_hand_center"]

    return (
        f"{label}: detected in {pct_det}% of frames in this window (mean tracker "
        f"confidence {conf if conf is not None else 'n/a'}). Position samples "
        f"(x,y normalized 0..1, 0,0=top-left of frame): {path_str}. "
        f"Mean speed {vel['mean'] if vel['mean'] is not None else 'n/a'} "
        f"(normalized frame-diagonal/s, {vel['n_samples']} consecutive-frame samples). "
        f"Vertical position relative to body: {bpct('face_or_above')}% at-or-above face height, "
        f"{bpct('shoulder_to_chest')}% shoulder-to-chest height, {bpct('below_chest')}% below chest "
        f"(unclassified when shoulders/face were not confidently tracked in that frame). "
        f"{disc['n_candidates']} large frame-to-frame position jump(s) flagged in this window "
        f"(may reflect fast motion or brief tracking uncertainty; not independently confirmed)."
    )


def render_trajectory_text(landmarks: dict, t_start: float, t_end: float) -> str:
    """The exact text Part to inject for one batch's [t_start, t_end] window."""
    sliced = slice_landmarks_by_time(landmarks, t_start, t_end)
    summary = st.summarize(sliced)
    if summary["n_frames_total"] == 0:
        return ("HAND-TRACKING OBSERVATIONS: no tracked frames fall inside this batch's "
                "time window; no trajectory data available for this batch.")

    left = render_hand_block("Left hand", summary, "left")
    right = render_hand_block("Right hand", summary, "right")
    thd = summary["two_hand_distance"]
    thd_str = (f"mean {thd['mean']}, range {thd['min']}-{thd['max']} (normalized frame-diagonal)"
               if thd["mean"] is not None else "not available (hands rarely co-detected in this window)")

    return (
        "HAND-TRACKING OBSERVATIONS (from an independent computer-vision pose tracker, "
        "RTMPose/rtmlib, run separately from you on this same video. This is raw "
        "geometric tracking data ONLY — coordinates, confidence, speed, and body-relative "
        "position bands. It is NOT a translation, NOT an ASL gloss, and NOT an "
        "interpretation of what is being signed. Use it only as additional spatial/motion "
        f"context alongside the images above.)\n"
        f"Time window: {t_start:.2f}s to {t_end:.2f}s ({summary['n_frames_total']} tracked frames).\n"
        f"{left}\n"
        f"{right}\n"
        f"Two-hand distance in this window: {thd_str}."
    )
