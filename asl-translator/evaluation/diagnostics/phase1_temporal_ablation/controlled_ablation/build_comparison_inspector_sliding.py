#!/usr/bin/env python3
"""Extends the Phase-1 frame inspector with an independent-batches-vs-sliding-
windows comparison view for the 12 diagnostic clips (Phase 3B).

Reuses (imports, does not fork) extract_thumbnails()/render_timeline_svg()
from phase1_temporal_ablation/inspector/build_inspector.py. NO MODEL CALL.
Shows the SAME sampled frame sequence for both arms (this experiment does not
resample), with baseline's independent 24-frame batch boundaries drawn on one
timeline and Arm B's overlapping sliding-window boundaries (with the actual
overlap region shaded) drawn on a second timeline directly below it, so the
extra temporal context each window saw relative to an independent batch is
visible at a glance.
"""
from __future__ import annotations

import csv
import html
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path("/Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c")
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
PHASE1_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "diagnostics" / "phase1_temporal_ablation"
INSPECTOR_DIR = PHASE1_DIR / "inspector"
DIAGNOSTIC_12_JSON = PHASE1_DIR / "diagnostic_12_clips.json"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"

OUT_DIR = PHASE1_DIR / "controlled_ablation" / "independent_vs_sliding"
SLIDING_PRED_DIR = OUT_DIR / "predictions"
INSPECTORS_OUT_DIR = OUT_DIR / "inspectors"
PAIRED_CSV = OUT_DIR / "paired_results.csv"

THUMB_CACHE_ROOT = Path(tempfile.gettempdir()) / "asl-how2sign-phase3b-frames"

sys.path.insert(0, str(ASL_EVAL_DIR))
sys.path.insert(0, str(INSPECTOR_DIR))
import run_current_model as rcm  # noqa: E402
import build_inspector as bi  # noqa: E402  reused thumbnail/SVG helpers

WINDOW_SIZE = 24
STRIDE = 12

PAGE_CSS = bi.PAGE_CSS + """
.arm-block{border:1px solid var(--border);border-radius:8px;padding:12px 14px;margin:12px 0}
.arm-title{font-weight:700;margin-bottom:6px}
.arm-title.baseline{color:#a15b00}
.arm-title.sliding{color:#3454d1}
.thumbrow{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
.legend-line{font-size:12px;color:var(--muted);margin:4px 0}
"""


def load_paired() -> dict:
    if not PAIRED_CSV.exists():
        return {}
    with PAIRED_CSV.open(newline="", encoding="utf-8") as f:
        return {r["clip_id"]: r for r in csv.DictReader(f)}


def build_windows(n_frames: int) -> list[tuple[int, int]]:
    windows = []
    start = 0
    while True:
        end = min(start + WINDOW_SIZE, n_frames)
        windows.append((start, end))
        if end >= n_frames:
            break
        start += STRIDE
    return windows


def render_batches_svg(width: int, height: int, duration: float, runs, stamps, batch_size: int) -> str:
    """Independent-batch view: reuse bi.render_timeline_svg's batch-boundary
    rendering by constructing the same `batches` shape it expects."""
    n_batches = rcm.expected_batch_count(len(stamps))
    batches = [{"i": i, "t0": stamps[i * batch_size]} for i in range(n_batches) if i * batch_size < len(stamps)]
    return bi.render_timeline_svg(width, height, duration, runs, stamps, batches)


def render_windows_svg(width: int, height: int, duration: float, runs, stamps, windows: list[tuple[int, int]]) -> str:
    """Sliding-window view: draw each window's [start,end) as a translucent
    bar on its own vertical lane so overlap between consecutive windows is
    visibly shaded twice (darker), plus the same motion-run shading as the
    independent-batch view for direct visual comparison."""
    def x(t):
        return 4 + (t / duration) * (width - 8) if duration > 0 else 4

    parts = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
    for r in runs:
        x0, x1 = x(r.start_s), x(r.end_s)
        color = "var(--active)" if r.active else "var(--idle)"
        parts.append(f'<rect x="{x0:.1f}" y="10" width="{max(1.0, x1 - x0):.1f}" height="14" fill="{color}"/>')

    lane_h = 16
    for i, (w_start, w_end) in enumerate(windows):
        t0 = stamps[w_start]
        t1 = stamps[w_end - 1] if w_end - 1 < len(stamps) else stamps[-1]
        x0, x1 = x(t0), x(t1)
        y0 = 30 + i * lane_h
        parts.append(f'<rect x="{x0:.1f}" y="{y0}" width="{max(1.0, x1 - x0):.1f}" height="{lane_h - 3}" '
                     f'fill="var(--accent)" opacity="0.35" stroke="var(--accent)" stroke-width="1"/>')
        parts.append(f'<text x="{x0 + 3:.1f}" y="{y0 + 10}" font-size="9" fill="var(--fg)">w{i}</text>')
    for t in stamps:
        xt = x(t)
        parts.append(f'<line x1="{xt:.1f}" y1="10" x2="{xt:.1f}" y2="24" stroke="#555" stroke-width="1" opacity="0.5"/>')
    total_h = 30 + len(windows) * lane_h + 10
    parts.append(f'<line x1="4" y1="{total_h-6}" x2="{width-4}" y2="{total_h-6}" stroke="var(--border)" stroke-width="1"/>')
    parts.append(f'<text x="4" y="{total_h+8}" font-size="10" fill="var(--muted)">0s</text>')
    parts.append(f'<text x="{width-40}" y="{total_h+8}" font-size="10" fill="var(--muted)">{duration:.1f}s</text>')
    parts[0] = f'<svg width="{width}" height="{total_h+20}" viewBox="0 0 {width} {total_h+20}" xmlns="http://www.w3.org/2000/svg">'
    parts.append("</svg>")
    return "".join(parts)


def build_clip_page(clip_id: str, manifest_row: dict, paired: dict) -> str:
    video_path = REPO_ROOT / manifest_row["local_video_path"]
    times, motion = rcm.probe_motion(str(video_path))
    duration = times[-1]
    runs = rcm.segment_runs(times, motion)

    base_pred_path = BASELINE_DIR / "predictions" / f"{clip_id}.json"
    base_meta = json.loads(base_pred_path.read_text(encoding="utf-8"))["run_metadata"]
    frame_budget = base_meta["frame_budget"]
    stamps = rcm.allocate_timestamps(runs, frame_budget)
    n_frames = len(stamps)
    windows = build_windows(n_frames)

    batches_svg = render_batches_svg(1000, 90, duration, runs, stamps, rcm.BATCH_SIZE)
    windows_svg = render_windows_svg(1000, 90, duration, runs, stamps, windows)

    cache_dir = THUMB_CACHE_ROOT / clip_id
    thumbs = bi.extract_thumbnails(video_path, stamps, cache_dir)

    row = paired.get(clip_id, {})
    wer_line = ""
    if row:
        wer_line = (f'<div class="meta"><b>baseline WER:</b> {html.escape(row.get("baseline_wer",""))} '
                    f'&nbsp; <b>sliding WER:</b> {html.escape(row.get("sliding_wer",""))} '
                    f'&nbsp; <b>delta:</b> {html.escape(row.get("wer_delta",""))} '
                    f'&nbsp; <b>multi_batch:</b> {html.escape(row.get("is_multi_batch",""))}</div>')

    def thumb_row(thumbs, stamps):
        cells = []
        for t, data_uri in zip(stamps, thumbs):
            if data_uri is None:
                cells.append(f'<div class="thumb"><div class="ts">(extract failed)<br>{t:.2f}s</div></div>')
                continue
            cells.append(f'<div class="thumb"><img src="{data_uri}" loading="lazy"><div class="ts">{t:.2f}s</div></div>')
        return f'<div class="thumbrow">{"".join(cells)}</div>'

    page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>{html.escape(clip_id)} — independent batches vs sliding windows (Phase 3B)</title>
<style>{PAGE_CSS}</style></head><body>
<h1>{html.escape(clip_id)} — independent 24-frame batches vs. overlapping sliding windows</h1>
<p class="muted">Phase 3B controlled batch/context ablation. SAME sampled frame sequence for both
arms (not resampled) — only how those frames are grouped for Gemini calls differs.</p>
<div class="meta"><b>duration_s:</b> {duration:.2f} &nbsp; <b>frame_budget:</b> {frame_budget}
&nbsp; <b>n_frames:</b> {n_frames} &nbsp; <b>baseline_batches:</b> {rcm.expected_batch_count(n_frames)}
&nbsp; <b>sliding_windows:</b> {len(windows)} (window_size=24, stride=12)</div>
{wer_line}

<div class="arm-block">
  <div class="arm-title baseline">Arm A — existing baseline, independent non-overlapping 24-frame batches</div>
  <div class="timeline">{batches_svg}</div>
  <div class="legend-line">Dashed red lines = independent batch boundaries (no cross-batch context).</div>
</div>

<div class="arm-block">
  <div class="arm-title sliding">Arm B — overlapping sliding windows (window_size=24, stride=12)</div>
  <div class="timeline">{windows_svg}</div>
  <div class="legend-line">Each blue bar (lane w0, w1, ...) is one window's frame span; where two bars
  overlap horizontally, both windows saw those frames — that overlap region is the extra temporal
  context this arm adds relative to Arm A's independent batches. Ownership of each output segment is
  resolved deterministically by frame-index position (see INDEPENDENT_VS_SLIDING.md), not shown here.</div>
</div>

<h2>Sampled frames (identical for both arms — not resampled)</h2>
{thumb_row(thumbs, stamps)}

<p class="muted">No model call was made by this inspector. Frame timestamps are re-derived locally
from the unmodified run_current_model.allocate_timestamps(); window boundaries from this
experiment's own (additive, standalone) build_windows(). Thumbnails are local ffmpeg extractions
for display only, not the exact 512px keyframes sent to Gemini.</p>
</body></html>"""
    return page


def build_index(clip_ids: list[str], paired: dict) -> str:
    rows = []
    for cid in clip_ids:
        r = paired.get(cid, {})
        rows.append(
            f'<tr><td><a href="{html.escape(cid)}.html">{html.escape(cid)}</a></td>'
            f'<td>{html.escape(r.get("baseline_wer",""))}</td>'
            f'<td>{html.escape(r.get("sliding_wer",""))}</td>'
            f'<td>{html.escape(r.get("wer_delta",""))}</td>'
            f'<td>{html.escape(r.get("is_multi_batch",""))}</td>'
            f'<td>{html.escape(r.get("manifest_hint_bucket",""))}</td></tr>'
        )
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Phase 3B — independent vs sliding inspector index</title>
<style>{PAGE_CSS}</style></head><body>
<h1>Phase 3B controlled batch/context ablation — 12 diagnostic clips</h1>
<p class="muted">Independent non-overlapping 24-frame batches (existing baseline) vs. overlapping
sliding windows (window_size=24, stride=12, new). Same sampled frames for both arms. No model call
made by this inspector.</p>
<table><tr><th>clip</th><th>baseline WER</th><th>sliding WER</th><th>delta</th><th>multi_batch</th><th>hint bucket</th></tr>
{''.join(rows)}
</table>
</body></html>"""


def main() -> None:
    diag = json.loads(DIAGNOSTIC_12_JSON.read_text(encoding="utf-8"))
    clip_ids = [c["clip_id"] for c in diag["clips"]]
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}
    paired = load_paired()

    INSPECTORS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    for clip_id in clip_ids:
        if not (SLIDING_PRED_DIR / f"{clip_id}.json").exists():
            print(f"SKIP {clip_id}: no sliding-arm prediction yet")
            continue
        print(f"building {clip_id} ...")
        page = build_clip_page(clip_id, manifest[clip_id], paired)
        (INSPECTORS_OUT_DIR / f"{clip_id}.html").write_text(page, encoding="utf-8")

    (INSPECTORS_OUT_DIR / "index.html").write_text(build_index(clip_ids, paired), encoding="utf-8")
    print(f"Wrote inspector pages + index.html to {INSPECTORS_OUT_DIR}")


if __name__ == "__main__":
    main()
