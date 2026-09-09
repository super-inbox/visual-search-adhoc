#!/usr/bin/env python3
"""Extends the existing Phase-1 frame inspector with an adaptive-vs-uniform
comparison view for the 12 diagnostic clips (Phase 3A).

Reuses (imports, does not copy/fork) the existing inspector's own
extract_thumbnails() and render_timeline_svg() helpers from
phase1_temporal_ablation/inspector/build_inspector.py — no new thumbnail or
SVG-rendering logic is written here. NO MODEL CALL. Reads only:
  - the frozen manifest (video paths)
  - already-saved baseline (Arm A) and uniform-arm (Arm B) prediction JSON
  - paired_results.csv (already-computed WER, if score_and_report.py has run)

Writes one self-contained HTML page per clip (adaptive section + uniform
section, each with its own timeline + thumbnail strip) plus an index, under
controlled_ablation/adaptive_vs_uniform_2fps/inspectors/. Does not touch or
overwrite anything in phase1_temporal_ablation/inspector/.
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

OUT_DIR = PHASE1_DIR / "controlled_ablation" / "adaptive_vs_uniform_2fps"
UNIFORM_PRED_DIR = OUT_DIR / "predictions"
INSPECTORS_OUT_DIR = OUT_DIR / "inspectors"
PAIRED_CSV = OUT_DIR / "paired_results.csv"

THUMB_CACHE_ROOT = Path(tempfile.gettempdir()) / "asl-how2sign-controlled-ablation-frames"

sys.path.insert(0, str(ASL_EVAL_DIR))
sys.path.insert(0, str(INSPECTOR_DIR))
import run_current_model as rcm  # noqa: E402
import build_inspector as bi  # noqa: E402  reused extract_thumbnails()/render_timeline_svg(), not forked

UNIFORM_CONFIG = "evaluation_2026_09_07_gemini_3_6_uniform_2fps"

PAGE_CSS = bi.PAGE_CSS + """
.arm-block{border:1px solid var(--border);border-radius:8px;padding:12px 14px;margin:12px 0}
.arm-title{font-weight:700;margin-bottom:6px}
.arm-title.adaptive{color:#a15b00}
.arm-title.uniform{color:#3454d1}
.thumbrow{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
"""


def load_paired_wer() -> dict:
    if not PAIRED_CSV.exists():
        return {}
    with PAIRED_CSV.open(newline="", encoding="utf-8") as f:
        return {r["clip_id"]: r for r in csv.DictReader(f)}


def build_clip_page(clip_id: str, manifest_row: dict, paired: dict) -> str:
    video_path = REPO_ROOT / manifest_row["local_video_path"]
    times, motion = rcm.probe_motion(str(video_path))
    duration = times[-1]
    runs = rcm.segment_runs(times, motion)

    base_pred_path = BASELINE_DIR / "predictions" / f"{clip_id}.json"
    uni_pred_path = UNIFORM_PRED_DIR / f"{clip_id}.json"
    base_meta = json.loads(base_pred_path.read_text(encoding="utf-8"))["run_metadata"]
    uni_meta = json.loads(uni_pred_path.read_text(encoding="utf-8"))["run_metadata"] if uni_pred_path.exists() else None

    frame_budget = base_meta["frame_budget"]
    adaptive_stamps = rcm.allocate_timestamps(runs, frame_budget)
    uniform_stamps = rcm.allocate_timestamps_uniform(times, frame_budget)

    cache_dir = THUMB_CACHE_ROOT / clip_id
    adaptive_thumbs = bi.extract_thumbnails(video_path, adaptive_stamps, cache_dir / "adaptive")
    uniform_thumbs = bi.extract_thumbnails(video_path, uniform_stamps, cache_dir / "uniform")

    n_batches = rcm.expected_batch_count(len(adaptive_stamps))
    batches = [{"i": i, "t0": adaptive_stamps[i * rcm.BATCH_SIZE]}
               for i in range(n_batches) if i * rcm.BATCH_SIZE < len(adaptive_stamps)]

    adaptive_svg = bi.render_timeline_svg(1000, 110, duration, runs, adaptive_stamps, batches)
    uniform_svg = bi.render_timeline_svg(1000, 110, duration, runs, uniform_stamps, batches)

    row = paired.get(clip_id, {})
    wer_line = ""
    if row:
        wer_line = (f'<div class="meta"><b>adaptive WER:</b> {html.escape(row.get("adaptive_wer",""))} '
                    f'&nbsp; <b>uniform WER:</b> {html.escape(row.get("uniform_wer",""))} '
                    f'&nbsp; <b>delta (uniform - adaptive):</b> {html.escape(row.get("wer_delta",""))}</div>')

    def thumb_row(thumbs, stamps):
        cells = []
        for t, data_uri in zip(stamps, thumbs):
            if data_uri is None:
                cells.append(f'<div class="thumb"><div class="ts">(extract failed)<br>{t:.2f}s</div></div>')
                continue
            cells.append(f'<div class="thumb"><img src="{data_uri}" loading="lazy">'
                         f'<div class="ts">{t:.2f}s</div></div>')
        return f'<div class="thumbrow">{"".join(cells)}</div>'

    page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>{html.escape(clip_id)} — adaptive vs uniform (Phase 3A)</title>
<style>{PAGE_CSS}</style></head><body>
<h1>{html.escape(clip_id)} — adaptive (motion-weighted) vs. uniform sampling</h1>
<p class="muted">Phase 3A controlled sampling-strategy ablation. Same clip, same frame_budget
({frame_budget}), same model/prompt/batch settings for both arms — only the timestamp
allocation formula differs. Motion-run shading (orange=active, grey=idle) is IDENTICAL in both
timelines below; only the tick marks (sampled timestamps) differ.</p>
<div class="meta"><b>duration_s:</b> {duration:.2f} &nbsp; <b>frame_budget:</b> {frame_budget}
&nbsp; <b>batch_size:</b> {rcm.BATCH_SIZE} &nbsp; <b>n_batches:</b> {n_batches}</div>
{wer_line}

<div class="arm-block">
  <div class="arm-title adaptive">Arm A — existing baseline (adaptive / motion-weighted), config={html.escape(base_meta.get('config',''))}</div>
  <div class="timeline">{adaptive_svg}</div>
  <div class="muted" style="margin-top:4px">{len(adaptive_stamps)} sampled timestamps (dashed red lines = independent 24-frame batch boundaries)</div>
  {thumb_row(adaptive_thumbs, adaptive_stamps)}
</div>

<div class="arm-block">
  <div class="arm-title uniform">Arm B — new controlled arm (uniform), config={html.escape(UNIFORM_CONFIG)}</div>
  <div class="timeline">{uniform_svg}</div>
  <div class="muted" style="margin-top:4px">{len(uniform_stamps)} sampled timestamps, evenly spaced across the clip span,
  ignoring motion energy entirely</div>
  {thumb_row(uniform_thumbs, uniform_stamps)}
</div>

<p class="muted">No model call was made by this inspector. Adaptive timestamps are re-derived
locally from the unmodified run_current_model.allocate_timestamps(); uniform timestamps from
the new, additive run_current_model.allocate_timestamps_uniform(). Thumbnails are local ffmpeg
extractions for display only, not the exact 512px keyframes sent to Gemini.</p>
</body></html>"""
    return page


def build_index(clip_ids: list[str], paired: dict) -> str:
    rows = []
    for cid in clip_ids:
        r = paired.get(cid, {})
        rows.append(
            f'<tr><td><a href="{html.escape(cid)}.html">{html.escape(cid)}</a></td>'
            f'<td>{html.escape(r.get("adaptive_wer",""))}</td>'
            f'<td>{html.escape(r.get("uniform_wer",""))}</td>'
            f'<td>{html.escape(r.get("wer_delta",""))}</td>'
            f'<td>{html.escape(r.get("manifest_hint_bucket",""))}</td></tr>'
        )
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Phase 3A — adaptive vs uniform inspector index</title>
<style>{PAGE_CSS}</style></head><body>
<h1>Phase 3A controlled sampling-strategy ablation — 12 diagnostic clips</h1>
<p class="muted">Adaptive (motion-weighted, existing baseline) vs. uniform (evenly spaced, new
ablation arm). Same frame budget, model, prompt, batch size, dedup, thinking_level for both
arms per clip — only timestamp allocation differs. No model call made by this inspector.</p>
<table><tr><th>clip</th><th>adaptive WER</th><th>uniform WER</th><th>delta</th><th>manifest hint bucket</th></tr>
{''.join(rows)}
</table>
</body></html>"""


def main() -> None:
    diag = json.loads(DIAGNOSTIC_12_JSON.read_text(encoding="utf-8"))
    clip_ids = [c["clip_id"] for c in diag["clips"]]
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}
    paired = load_paired_wer()

    INSPECTORS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    for clip_id in clip_ids:
        uni_pred_path = UNIFORM_PRED_DIR / f"{clip_id}.json"
        if not uni_pred_path.exists():
            print(f"SKIP {clip_id}: no uniform-arm prediction yet")
            continue
        print(f"building {clip_id} ...")
        page = build_clip_page(clip_id, manifest[clip_id], paired)
        (INSPECTORS_OUT_DIR / f"{clip_id}.html").write_text(page, encoding="utf-8")

    (INSPECTORS_OUT_DIR / "index.html").write_text(build_index(clip_ids, paired), encoding="utf-8")
    print(f"Wrote inspector pages + index.html to {INSPECTORS_OUT_DIR}")


if __name__ == "__main__":
    main()
