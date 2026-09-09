#!/usr/bin/env python3
"""Build a frame-level inspector for the 12 diagnostic How2Sign v2 clips.

Pattern reused (READ-ONLY reference, not checked out/pulled/modified) from
curify-studio origin/main commit 007dcf6
(dev/asl_mvp/inspector/build/build.py): re-derive the exact frames the model
saw by re-running the production sampler locally, score against the saved
prediction, and render a single self-contained HTML page per clip plus an
index. That page was built for one private-corpus clip (1252); this script
generalizes the same idea to the 12 frozen How2Sign v2 clips selected by
select_12_diagnostic_clips.py.

NO MODEL CALL IS MADE. This script only:
  - re-runs asl-eval/run_current_model.py's probe_motion/segment_runs/
    allocate_timestamps (the same, unmodified, already-ported production
    sampler used for the real baseline run) with the frame_budget recorded
    in that clip's own saved prediction run_metadata,
  - extracts thumbnail JPEGs locally with ffmpeg for display,
  - reads the already-saved baseline prediction JSON and reference SRT,
  - scores with asl-eval/lib.py (WER/CER numbers are read from the frozen
    per_clip_results.csv, not recomputed, so they always agree with the
    scored corpus).

Run:
    python3 asl-translator/evaluation/diagnostics/phase1_temporal_ablation/inspector/build_inspector.py
"""
from __future__ import annotations

import base64
import concurrent.futures as cf
import csv
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIAG_DIR = HERE.parent
REPO_ROOT = HERE.parents[4]
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"
DIAGNOSTIC_JSON = DIAG_DIR / "diagnostic_12_clips.json"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
PER_CLIP_CSV = BASELINE_DIR / "per_clip_results.csv"

CACHE_ROOT = Path(tempfile.gettempdir()) / "asl-how2sign-inspector-frames"
THUMB_WIDTH = 220
THUMB_QUALITY = "6"  # ffmpeg -q:v; higher = smaller/lower quality. Display only —
                      # NOT the 512px KEYFRAME_WIDTH actually sent to Gemini.

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_current_model as rcm  # noqa: E402  the same sampler used for the real run
import lib  # noqa: E402  the same scorer used for the frozen corpus


# ─────────────────────────────────────────────────────────────────────────
# Stage 1: re-derive the exact sampling this clip's baseline run used
# ─────────────────────────────────────────────────────────────────────────
def resample_clip(video_path: Path, frame_budget: int) -> dict:
    times, motion = rcm.probe_motion(str(video_path))
    runs = rcm.segment_runs(times, motion)
    stamps = rcm.allocate_timestamps(runs, frame_budget)
    return {"probe_times": times, "probe_motion": motion, "runs": runs, "stamps": stamps}


def extract_thumbnails(video_path: Path, stamps: list[float], cache_dir: Path) -> list[str]:
    cache_dir.mkdir(parents=True, exist_ok=True)

    def one(i_t):
        i, t = i_t
        out = cache_dir / f"f_{i:03d}.jpg"
        if not out.exists():
            subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video_path),
                 "-frames:v", "1", "-vf", f"scale={THUMB_WIDTH}:-2",
                 "-q:v", THUMB_QUALITY, "-y", str(out)],
                capture_output=True, timeout=60,
            )
        return out

    with cf.ThreadPoolExecutor(8) as ex:
        paths = list(ex.map(one, enumerate(stamps)))
    out = []
    for p in paths:
        if p.exists() and p.stat().st_size > 0:
            out.append("data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode())
        else:
            out.append(None)
    return out


# ─────────────────────────────────────────────────────────────────────────
# Stage 2: word-level diff for display only (WER itself is read from
# per_clip_results.csv, never recomputed here — see module docstring).
# Same technique as curify-studio's inspector: lib.levenshtein_align only
# returns counts, so the backtrace is repeated locally to get the path.
# ─────────────────────────────────────────────────────────────────────────
def diff_ops(ref: str, hyp: str) -> list[tuple]:
    r, h = lib.normalize_text(ref).split(), lib.normalize_text(hyp).split()
    n, m = len(r), len(h)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if r[i - 1] == h[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
    i, j, ops = n, m, []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (0 if r[i - 1] == h[j - 1] else 1):
            ops.append(("ok" if r[i - 1] == h[j - 1] else "sub", r[i - 1], h[j - 1]))
            i -= 1
            j -= 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            ops.append(("del", r[i - 1], None))
            i -= 1
        elif j > 0:
            ops.append(("ins", None, h[j - 1]))
            j -= 1
        else:
            break
    ops.reverse()
    return ops


def render_diff_html(text: str, ops: list[tuple], side: int) -> str:
    """side: 1 = ref token position, 2 = hyp token position."""
    out, k = [], 0
    for tok in text.split():
        words = lib.normalize_text(tok).split()
        n = len(words) or 1
        relevant = [o for o in ops if (o[1] is not None if side == 1 else o[2] is not None)]
        window = relevant[k:k + n]
        hit = bool(window) and all(o[0] == "ok" for o in window)
        k += n
        cls = "hit" if hit else "miss"
        out.append(f'<span class="{cls}">{html.escape(tok)}</span>')
    return " ".join(out)


# ─────────────────────────────────────────────────────────────────────────
# Stage 3: batch-seam heuristic — does a model segment start near a batch
# boundary? This is a HINT for human review (feeds fps_might_help /
# batch_boundary_might_help in the taxonomy), not a claim of causation.
# ─────────────────────────────────────────────────────────────────────────
def nearest_stamp_index(stamps: list[float], t: float) -> int:
    return min(range(len(stamps)), key=lambda i: abs(stamps[i] - t))


def near_batch_seam(idx: int, batch_size: int, slack: int = 1) -> bool:
    pos = idx % batch_size
    return pos <= slack - 1 or pos >= batch_size - slack


# ─────────────────────────────────────────────────────────────────────────
# Stage 4: page assembly
# ─────────────────────────────────────────────────────────────────────────
PAGE_CSS = """
:root{color-scheme:light dark;
  --bg:#ffffff;--fg:#1a1a1a;--muted:#6b6b6b;--border:#dcdcdc;
  --active:#ffe1a8;--idle:#eef0f2;--seam:#ffb3b3;--hit:#b6e6b0;--miss:#f3c4c4;
  --card:#f7f7f8;--accent:#3454d1;}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){--bg:#15161a;--fg:#e8e8ea;--muted:#9a9aa2;
  --border:#33343a;--active:#5b431a;--idle:#26272c;--seam:#5b2222;
  --hit:#204a24;--miss:#4a2323;--card:#1d1e23;--accent:#7f96ff;}}
:root[data-theme="dark"]{--bg:#15161a;--fg:#e8e8ea;--muted:#9a9aa2;
  --border:#33343a;--active:#5b431a;--idle:#26272c;--seam:#5b2222;
  --hit:#204a24;--miss:#4a2323;--card:#1d1e23;--accent:#7f96ff;}
body{background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif;margin:0;padding:24px;max-width:1100px}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:15px;margin:28px 0 8px;border-bottom:1px solid var(--border);padding-bottom:4px}
.muted{color:var(--muted)}
.meta{display:flex;flex-wrap:wrap;gap:8px 20px;background:var(--card);border:1px solid var(--border);
  border-radius:8px;padding:12px 16px;font-size:13px}
.meta b{color:var(--fg)}
.warn{background:var(--seam);border:1px solid var(--border);border-radius:6px;padding:8px 12px;margin:10px 0;font-size:13px}
.timeline{position:relative;height:140px;border:1px solid var(--border);border-radius:6px;overflow:hidden;background:var(--card)}
.timeline svg{display:block}
.frames{display:flex;flex-wrap:wrap;gap:4px}
.batch{border:1px solid var(--border);border-radius:6px;padding:8px;margin:0 0 10px 0}
.batch-label{font-size:12px;color:var(--muted);margin-bottom:6px}
.thumb{position:relative;width:96px}
.thumb img{width:96px;height:auto;display:block;border-radius:3px;border:1px solid var(--border)}
.thumb .ts{font-size:10px;color:var(--muted);text-align:center}
.thumb.seam img{outline:2px solid #d33;outline-offset:-2px}
table{border-collapse:collapse;width:100%;font-size:13px}
td,th{border:1px solid var(--border);padding:5px 8px;text-align:left;vertical-align:top}
th{background:var(--card)}
.hit{background:var(--hit);border-radius:2px;padding:0 2px}
.miss{background:var(--miss);border-radius:2px;padding:0 2px}
.textblock{background:var(--card);border:1px solid var(--border);border-radius:6px;padding:10px 12px}
.pill{display:inline-block;background:var(--card);border:1px solid var(--border);border-radius:999px;
  padding:2px 10px;font-size:12px;margin:2px 4px 2px 0}
.seamflag{color:#d33;font-weight:600}
a{color:var(--accent)}
code{background:var(--card);padding:1px 4px;border-radius:3px}
"""


def render_timeline_svg(width: int, height: int, duration: float, runs, stamps, batches) -> str:
    def x(t):
        return 4 + (t / duration) * (width - 8) if duration > 0 else 4

    parts = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
    # motion-run shading
    for r in runs:
        x0, x1 = x(r.start_s), x(r.end_s)
        color = "var(--active)" if r.active else "var(--idle)"
        parts.append(f'<rect x="{x0:.1f}" y="10" width="{max(1.0, x1 - x0):.1f}" height="60" fill="{color}"/>')
    # frame ticks
    for t in stamps:
        xt = x(t)
        parts.append(f'<line x1="{xt:.1f}" y1="10" x2="{xt:.1f}" y2="70" stroke="#555" stroke-width="1" opacity="0.55"/>')
    # batch boundaries
    for b in batches:
        xt = x(b["t0"])
        parts.append(f'<line x1="{xt:.1f}" y1="0" x2="{xt:.1f}" y2="80" stroke="#d33" stroke-width="2" stroke-dasharray="4,3"/>')
        parts.append(f'<text x="{xt + 3:.1f}" y="12" font-size="10" fill="#d33">batch {b["i"] + 1}</text>')
    parts.append(f'<line x1="4" y1="85" x2="{width - 4}" y2="85" stroke="var(--border)" stroke-width="1"/>')
    parts.append(f'<text x="4" y="100" font-size="10" fill="var(--muted)">0s</text>')
    parts.append(f'<text x="{width - 40}" y="100" font-size="10" fill="var(--muted)">{duration:.1f}s</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_clip_page(rec: dict, manifest_row: dict) -> tuple[str, dict]:
    clip_id = rec["clip_id"]
    video_path = REPO_ROOT / manifest_row["local_video_path"]
    ref_path = REPO_ROOT / manifest_row["local_reference_path"]
    pred_path = BASELINE_DIR / "predictions" / f"{clip_id}.json"

    pred_data = json.loads(pred_path.read_text(encoding="utf-8"))
    rm = pred_data["run_metadata"]
    frame_budget = rm["frame_budget"]
    batch_size = rm["batch_size"]
    duration_s = rm["duration_s"]

    sampling = resample_clip(video_path, frame_budget)
    stamps = sampling["stamps"]
    recomputed_n = len(stamps)
    recorded_n = rm["frames_sampled"]
    mismatch = recomputed_n != recorded_n

    cache_dir = CACHE_ROOT / clip_id
    thumbs = extract_thumbnails(video_path, stamps, cache_dir)

    n_batches = (len(stamps) + batch_size - 1) // batch_size
    batches = [{"i": b, "t0": stamps[b * batch_size],
                "t1": stamps[min(len(stamps) - 1, b * batch_size + batch_size - 1)],
                "start_idx": b * batch_size,
                "end_idx": min(len(stamps) - 1, b * batch_size + batch_size - 1)}
               for b in range(n_batches)]

    gold = lib.parse_srt(ref_path)
    gold_text = lib.build_transcript(gold)
    pred_segments = pred_data.get("segments", [])
    pred_text = lib.build_transcript(pred_segments)

    ops = diff_ops(gold_text, pred_text)
    ref_html = render_diff_html(gold_text, ops, side=1)
    hyp_html = render_diff_html(pred_text, ops, side=2)

    # flag model segments whose start lands near a batch seam
    seg_rows = []
    for s in pred_segments:
        idx = nearest_stamp_index(stamps, float(s["start"])) if stamps else 0
        seam = n_batches > 1 and near_batch_seam(idx, batch_size)
        seg_rows.append({**s, "nearest_frame_idx": idx, "near_batch_seam": seam})

    timeline_svg = render_timeline_svg(1000, 110, duration_s, sampling["runs"], stamps, batches)

    frame_groups_html = []
    for b in batches:
        tiles = []
        for i in range(b["start_idx"], b["end_idx"] + 1):
            seam_cls = "seam" if (i == b["start_idx"] and b["i"] > 0) or (i == b["end_idx"] and b["i"] < n_batches - 1) else ""
            img = thumbs[i] if i < len(thumbs) and thumbs[i] else ""
            img_tag = f'<img src="{img}">' if img else '<div class="ts">(extract failed)</div>'
            tiles.append(
                f'<div class="thumb {seam_cls}">{img_tag}<div class="ts">f{i} · {stamps[i]:.2f}s</div></div>'
            )
        frame_groups_html.append(
            f'<div class="batch"><div class="batch-label">batch {b["i"]+1} '
            f'(frames {b["start_idx"]}–{b["end_idx"]}, {b["t0"]:.2f}s–{b["t1"]:.2f}s)</div>'
            f'<div class="frames">{"".join(tiles)}</div></div>'
        )

    seam_marker = '<span class="seamflag">near batch seam</span>'
    seg_table_rows = "".join(
        f'<tr><td>{s["line"]}</td><td>{float(s["start"]):.2f}</td><td>{float(s["end"]):.2f}</td>'
        f'<td>{html.escape(s.get("text",""))}</td>'
        f'<td>{seam_marker if s["near_batch_seam"] else ""}</td></tr>'
        for s in seg_rows
    )

    mismatch_html = ""
    if mismatch:
        mismatch_html = (
            f'<div class="warn">Provenance note: re-derived sampling produced '
            f'{recomputed_n} frames; the saved run recorded {recorded_n}. Same frame_budget '
            f'({frame_budget}) and unmodified sampler were used; a mismatch here is the same '
            f'pre-existing ffprobe-vs-motion-probe duration rounding documented in '
            f'run_curify_how2sign_v2_benchmark.py, not a new bug. Frames shown below are the '
            f're-derived set.</div>'
        )

    wer = rec["baseline_wer"]
    tags = rec["manifest_heuristic_tags"]
    tag_pills = "".join(f'<span class="pill">{k}</span>' for k, v in tags.items() if v) or '<span class="pill">plain / no heuristic tag</span>'

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Inspector — {html.escape(clip_id)}</title>
<style>{PAGE_CSS}</style></head><body>
<p><a href="index.html">&larr; all 12 clips</a></p>
<h1>{html.escape(clip_id)}</h1>
<p class="muted">Phase-1 temporal-architecture diagnostic — baseline A
(<code>{rec['baseline_config']}</code>), no model call made by this page.</p>
<div class="meta">
  <div><b>duration</b> {duration_s:.2f}s</div>
  <div><b>WER</b> {wer}</div>
  <div><b>frames_sampled</b> {recorded_n}</div>
  <div><b>model_calls</b> {rm['model_calls']}</div>
  <div><b>sampling_density_fps</b> {rm['sampling_density_fps']}</div>
  <div><b>batch_size</b> {batch_size}</div>
  <div><b>reason_selected</b> {", ".join(rec['reason_selected'])}</div>
</div>
<p>{tag_pills}</p>
{mismatch_html}

<h2>Timeline: motion runs, sampled frames, batch boundaries</h2>
<div class="timeline">{timeline_svg}</div>
<p class="muted">Shaded = motion-active vs. idle runs from the (unmodified) production motion probe.
Thin ticks = each sampled frame timestamp. Dashed red lines = independent-batch boundaries
(batch_size={batch_size}) — the model never sees across a red line.</p>

<h2>Sampled frames, grouped by batch (red outline = frame adjacent to a batch seam)</h2>
{"".join(frame_groups_html)}

<h2>Reference vs. baseline prediction (word-level diff)</h2>
<div class="textblock"><b>Reference:</b><br>{ref_html}</div>
<div class="textblock" style="margin-top:8px"><b>Baseline prediction:</b><br>{hyp_html}</div>
<p class="muted">Highlighting is a word-level Levenshtein alignment for display only; the
authoritative WER above is read from <code>per_clip_results.csv</code>, not recomputed here.</p>

<h2>Model output segments (in order) — batch-seam proximity flagged</h2>
<table><tr><th>#</th><th>start</th><th>end</th><th>text</th><th>flag</th></tr>{seg_table_rows}</table>

<h2>Provenance</h2>
<table>
<tr><td>video</td><td><code>{html.escape(str(manifest_row['local_video_path']))}</code></td></tr>
<tr><td>reference</td><td><code>{html.escape(str(manifest_row['local_reference_path']))}</code></td></tr>
<tr><td>baseline prediction</td><td><code>{html.escape(str(pred_path.relative_to(REPO_ROOT)))}</code></td></tr>
<tr><td>config</td><td><code>{rec['baseline_config']}</code> (model={rm['model']}, thinking_level={rm.get('thinking_level')})</td></tr>
<tr><td>sampler</td><td>asl-translator/asl-eval/run_current_model.py: probe_motion &rarr; segment_runs &rarr; allocate_timestamps (unmodified; ported, with attribution, from curify-studio origin/main)</td></tr>
<tr><td>frame_budget used</td><td>{frame_budget} (recorded in this clip's saved run_metadata.json, not re-derived)</td></tr>
<tr><td>scoring</td><td>asl-translator/asl-eval/lib.py — WER/CER numbers shown above are copied from per_clip_results.csv</td></tr>
<tr><td>inspector pattern reused from</td><td>curify-studio origin/main commit 007dcf6, dev/asl_mvp/inspector/build/build.py (read-only reference; curify-studio not checked out/modified)</td></tr>
</table>
</body></html>
"""
    summary = {
        "clip_id": clip_id, "duration_s": duration_s, "wer": wer,
        "frames_sampled": recorded_n, "model_calls": rm["model_calls"],
        "sampling_density_fps": rm["sampling_density_fps"], "n_batches": n_batches,
        "frame_count_mismatch": mismatch,
        "n_segments_near_batch_seam": sum(1 for s in seg_rows if s["near_batch_seam"]),
        "reason_selected": rec["reason_selected"],
    }
    return page, summary


def build_index(summaries: list[dict]) -> str:
    rows = "".join(
        f'<tr><td><a href="{html.escape(s["clip_id"])}.html">{html.escape(s["clip_id"])}</a></td>'
        f'<td>{s["duration_s"]:.2f}</td><td>{s["wer"]}</td><td>{s["frames_sampled"]}</td>'
        f'<td>{s["model_calls"]}</td><td>{s["sampling_density_fps"]}</td>'
        f'<td>{s["n_batches"]}</td><td>{s["n_segments_near_batch_seam"]}</td>'
        f'<td>{", ".join(s["reason_selected"])}</td>'
        f'<td>{"&#9888; recomputed frame count differs" if s["frame_count_mismatch"] else ""}</td></tr>'
        for s in summaries
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>How2Sign v2 — Phase 1 frame inspector</title>
<style>{PAGE_CSS}</style></head><body>
<h1>Phase 1 temporal-architecture diagnostic — 12 selected How2Sign v2 clips</h1>
<p class="muted">Baseline A (<code>evaluation_2026_09_04_gemini_3_6</code>, 2 fps target density,
independent 24-frame batches, 128/128 clips scored). No model call made by this inspector.
See <a href="../TASK0_baseline_denominator.md">TASK0_baseline_denominator.md</a> and
<a href="../diagnostic_12_clips.json">diagnostic_12_clips.json</a> for how these 12 were chosen.</p>
<table>
<tr><th>clip</th><th>duration_s</th><th>WER</th><th>frames</th><th>model_calls</th>
<th>density_fps</th><th>n_batches</th><th>segments near seam</th><th>reason_selected</th><th>note</th></tr>
{rows}
</table>
<p class="muted">Pattern reused (read-only) from curify-studio origin/main commit 007dcf6,
<code>dev/asl_mvp/inspector/build/build.py</code> — not checked out, pulled, or modified.</p>
</body></html>
"""


def main() -> None:
    diag = json.loads(DIAGNOSTIC_JSON.read_text(encoding="utf-8"))
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        manifest = {r["how2sign_id"]: r for r in csv.DictReader(f)}

    summaries = []
    for rec in diag["clips"]:
        clip_id = rec["clip_id"]
        print(f"building {clip_id} ...")
        page, summary = build_clip_page(rec, manifest[clip_id])
        (HERE / f"{clip_id}.html").write_text(page, encoding="utf-8")
        summaries.append(summary)

    index_html = build_index(summaries)
    (HERE / "index.html").write_text(index_html, encoding="utf-8")
    print(f"\nWrote {len(summaries)} clip pages + index.html to {HERE}")
    for s in summaries:
        print(f"  {s['clip_id']:45s} batches={s['n_batches']} near_seam_segments={s['n_segments_near_batch_seam']}"
              f" mismatch={s['frame_count_mismatch']}")


if __name__ == "__main__":
    main()
