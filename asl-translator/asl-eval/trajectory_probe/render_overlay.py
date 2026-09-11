#!/usr/bin/env python3
"""Phase D1 trajectory-tracking POC — visualization only.

1) render_svg_plot(): a static SVG of the left/right hand-center paths over
   time (reuses this repo's existing inline-SVG technique from
   build_inspector.py's render_timeline_svg — no new plotting library).
   Pure stdlib, runs in any environment.

2) render_overlay_video(): an actual skeleton-overlay .mp4, using rtmlib's
   own draw_skeleton() + OpenCV's VideoWriter. Needs the unisign-cpu-arm64
   env (cv2 + rtmlib). Only run for one clip in this POC (see module
   docstring of extract_trajectory.py — kept minimal, "if practical").

No ASL-specific interpretation anywhere — these are geometric plots of the
tracker's own raw/derived output.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path


def render_svg_plot(summary: dict, out_svg: Path) -> None:
    W, H = 640, 420
    pad = 30
    plot_w, plot_h = W - 2 * pad, H - 2 * pad - 20

    def to_xy(t, x, y, duration):
        px = pad + (t / duration) * plot_w if duration > 0 else pad
        py = pad + y * plot_h  # y already normalized 0..1 (top..bottom of frame)
        return px, py

    duration = summary["duration_s"] or 1.0
    parts = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'xmlns="http://www.w3.org/2000/svg" style="background:#fff">']
    parts.append(f'<text x="{pad}" y="16" font-size="12" fill="#333">'
                 f'{html.escape(summary["clip_id"])} — hand-center Y position over time '
                 f'(top=near face, bottom=below chest)</text>')

    for label, key, color in (("left hand", "left_hand_center_trajectory", "#3454d1"),
                               ("right hand", "right_hand_center_trajectory", "#d13434")):
        series = summary[key]["series_t_x_y"]
        if not series:
            continue
        pts = [to_xy(t, x, y, duration) for t, x, y in series]
        path = " ".join(f'{"M" if i == 0 else "L"}{px:.1f},{py:.1f}' for i, (px, py) in enumerate(pts))
        parts.append(f'<path d="{path}" stroke="{color}" stroke-width="1.6" fill="none" opacity="0.85"/>')
        lx, ly = pts[-1]
        parts.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3" fill="{color}"/>')
        parts.append(f'<text x="{lx+6:.1f}" y="{ly:.1f}" font-size="10" fill="{color}">{html.escape(label)}</text>')

    # axis
    parts.append(f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{pad+plot_h}" stroke="#999"/>')
    parts.append(f'<line x1="{pad}" y1="{pad+plot_h}" x2="{pad+plot_w}" y2="{pad+plot_h}" stroke="#999"/>')
    parts.append(f'<text x="{pad}" y="{pad+plot_h+15}" font-size="10" fill="#666">0s</text>')
    parts.append(f'<text x="{pad+plot_w-24}" y="{pad+plot_h+15}" font-size="10" fill="#666">{duration:.1f}s</text>')
    parts.append(f'<text x="{pad-22}" y="{pad+4}" font-size="10" fill="#666">face</text>')
    parts.append(f'<text x="{pad-30}" y="{pad+plot_h}" font-size="10" fill="#666">below</text>')
    parts.append("</svg>")
    out_svg.write_text("".join(parts), encoding="utf-8")


def render_overlay_video(video_path: Path, landmarks: dict, out_mp4: Path) -> None:
    import cv2
    from rtmlib import draw_skeleton

    cap = cv2.VideoCapture(str(video_path))
    fps = landmarks["source_fps"] or 24.0
    w, h = landmarks["frame_width"], landmarks["frame_height"]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_mp4), fourcc, fps, (w, h))

    frame_by_idx = {f["frame_idx"]: f for f in landmarks["frames"]}
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        fr = frame_by_idx.get(idx)
        if fr and fr["keypoints_xy"] is not None:
            import numpy as np
            kpts = np.array([fr["keypoints_xy"]])
            scores = np.array([fr["keypoints_score"]])
            frame = draw_skeleton(frame, kpts, scores, kpt_thr=0.3)
        writer.write(frame)
        idx += 1
    cap.release()
    writer.release()


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: render_overlay.py svg <summary_json> <out_svg>\n"
              "       render_overlay.py video <landmarks_json> <video_path> <out_mp4>  (needs unisign-cpu-arm64 env)",
              file=sys.stderr)
        return 2
    mode = sys.argv[1]
    if mode == "svg":
        summary = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        out_svg = Path(sys.argv[3])
        out_svg.parent.mkdir(parents=True, exist_ok=True)
        render_svg_plot(summary, out_svg)
        print(f"wrote {out_svg}")
    elif mode == "video":
        landmarks = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        video_path = Path(sys.argv[3])
        out_mp4 = Path(sys.argv[4])
        out_mp4.parent.mkdir(parents=True, exist_ok=True)
        render_overlay_video(video_path, landmarks, out_mp4)
        print(f"wrote {out_mp4}")
    else:
        print(f"unknown mode {mode!r}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
