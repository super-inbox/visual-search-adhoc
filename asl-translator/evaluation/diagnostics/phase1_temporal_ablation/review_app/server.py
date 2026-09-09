#!/usr/bin/env python3
"""Minimal local human-review app for taxonomy_40_clips.csv.

Standard library only (http.server, json, csv, subprocess for ffmpeg
thumbnails) — no new dependency. Binds to 127.0.0.1 only.

NO GEMINI / google.genai CALL IS MADE ANYWHERE IN THIS FILE. It only:
  - reads the already-generated taxonomy_40_clips.csv / diagnostic_12_clips.json
  - reads already-saved baseline predictions and manifest.csv
  - streams local benchmark video files from disk
  - re-runs the local, unmodified motion sampler (probe_motion/segment_runs/
    allocate_timestamps from asl-eval/run_current_model.py) to extract small
    on-demand thumbnail images, cached to disk — the same no-model-call
    pattern used by inspector/build_inspector.py
  - persists your human annotations to taxonomy_40_human_review.json/.csv

Run (from the repo root):
    python3 asl-translator/evaluation/diagnostics/phase1_temporal_ablation/review_app/server.py

Then open http://127.0.0.1:8934/  (Ctrl+C in this terminal to stop).

Annotations are saved to, and resumed from:
    asl-translator/evaluation/diagnostics/phase1_temporal_ablation/taxonomy_40_human_review.json
    asl-translator/evaluation/diagnostics/phase1_temporal_ablation/taxonomy_40_human_review.csv

The original taxonomy_40_clips.csv is never written to by this app.
"""
from __future__ import annotations

import base64
import csv
import json
import mimetypes
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

HERE = Path(__file__).resolve().parent                          # .../review_app
PHASE1_DIR = HERE.parent                                        # .../phase1_temporal_ablation
DIAGNOSTICS_DIR = PHASE1_DIR.parent
REPO_ROOT = HERE.parents[4]
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
BASELINE_DIR = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2" / "curify_gemini_3_6_2026_09_04"
MANIFEST_PATH = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "manifest.csv"
INSPECTOR_DIR = PHASE1_DIR / "inspector"

TAXONOMY_CSV = PHASE1_DIR / "taxonomy_40_clips.csv"
DIAGNOSTIC_12_JSON = PHASE1_DIR / "diagnostic_12_clips.json"
REVIEW_JSON = PHASE1_DIR / "taxonomy_40_human_review.json"
REVIEW_CSV = PHASE1_DIR / "taxonomy_40_human_review.csv"
THUMB_CACHE_DIR = HERE / "thumb_cache"
APP_HTML_PATH = HERE / "templates" / "app.html"

PORT = 8934
HOST = "127.0.0.1"

CONTENT_TAG_COLUMNS = [
    "handshape_sensitive", "motion", "fingerspelling", "numbers",
    "facial_non_manual", "fast_signing", "other",
]
FAILURE_TAG_COLUMNS = [
    "handshape", "motion", "fingerspelling", "numbers", "facial_non_manual",
    "segmentation", "hallucinated_topic", "repetition",
    "correct_meaning_different_english", "other",
]

# Tags whose reliable judgment requires ASL fluency / visual sign-language
# expertise a text-only reviewer cannot be expected to have. These are still
# offered in the UI (so an ASL-fluent reviewer can use the same app) but are
# marked "Requires ASL/visual review unless directly obvious" and are never
# required or auto-filled. See HUMAN_REVIEW_GUIDE.md.
CONTENT_TAG_ASL_REVIEW = {
    "handshape_sensitive", "motion", "fingerspelling", "numbers", "facial_non_manual",
}
FAILURE_TAG_ASL_REVIEW = {
    "handshape", "motion", "fingerspelling", "numbers", "facial_non_manual",
    "segmentation", "hallucinated_topic",
}

SEMANTIC_FIELDS = ["semantic_adequacy", "reference_topic_mismatch", "hallucination",
                    "requires_asl_review", "fps_might_help",
                    "batch_boundary_might_help", "notes"]

N_THUMBS = 6
THUMB_WIDTH = 160

sys.path.insert(0, str(ASL_EVAL_DIR))
import run_current_model as rcm  # noqa: E402  same unmodified sampler as the baseline run — no model call

_SAVE_LOCK = threading.Lock()


# ─────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────
def load_manifest() -> dict:
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as f:
        return {r["how2sign_id"]: r for r in csv.DictReader(f)}


def load_ordered_clips() -> list[dict]:
    with TAXONOMY_CSV.open(newline="", encoding="utf-8") as f:
        rows = {r["clip_id"]: r for r in csv.DictReader(f)}
    priority_ids = [c["clip_id"] for c in json.loads(DIAGNOSTIC_12_JSON.read_text(encoding="utf-8"))["clips"]]
    assert len(priority_ids) == 12, f"expected 12 priority clips, found {len(priority_ids)}"
    assert len(set(priority_ids)) == 12, "duplicate priority clip ids"
    assert len(rows) == 40, f"expected 40 taxonomy clips, found {len(rows)}"
    assert len(set(rows)) == 40, "duplicate clip ids in taxonomy_40_clips.csv"
    missing = [cid for cid in priority_ids if cid not in rows]
    assert not missing, f"priority clips missing from taxonomy_40_clips.csv: {missing}"

    ordered_ids = priority_ids + [cid for cid in rows if cid not in priority_ids]
    manifest = load_manifest()
    clips = []
    for i, cid in enumerate(ordered_ids):
        row = rows[cid]
        m = manifest.get(cid, {})
        clips.append({
            "index": i,
            "clip_id": cid,
            "priority": cid in priority_ids,
            "duration_s": row.get("duration_s"),
            "reference": row.get("reference"),
            "baseline_prediction": row.get("baseline_prediction"),
            "baseline_wer": row.get("baseline_wer"),
            "frames_sampled": row.get("frames_sampled"),
            "model_calls_baseline": row.get("model_calls_baseline"),
            "sampling_density_fps_baseline": row.get("sampling_density_fps_baseline"),
            "hint_number_token": row.get("hint_number_token"),
            "hint_fingerspelling_candidate": row.get("hint_fingerspelling_candidate"),
            "hint_fast_signing": row.get("hint_fast_signing"),
            "hint_question": row.get("hint_question"),
            "reason_selected": row.get("reason_selected"),
            "local_video_path": m.get("local_video_path"),
            "inspector_available": cid in priority_ids,
        })
    return clips


def blank_annotation() -> dict:
    rec = {
        "content": {c: False for c in CONTENT_TAG_COLUMNS},
        "failure": {c: False for c in FAILURE_TAG_COLUMNS},
    }
    for c in SEMANTIC_FIELDS:
        rec[c] = ""
    rec["last_saved_utc"] = None
    return rec


def _migrate_legacy_hallucination_yes(rec: dict) -> str | None:
    """One-time, non-destructive migration for records saved before the
    hallucination field was split into yes/no/uncertain/requires_asl_review
    plus a separate text-based reference_topic_mismatch field.

    A pre-existing hallucination == "yes" asserted "no basis at all in the
    video" — a visual-grounding claim a non-ASL-fluent reviewer cannot
    reliably make. Rather than silently keep asserting that, downgrade it to
    requires_asl_review and preserve the reviewer's actual (text-based)
    observation as reference_topic_mismatch=yes. Returns a note to append, or
    None if no migration was needed.
    """
    if rec.get("hallucination") != "yes":
        return None
    rec["reference_topic_mismatch"] = "yes"
    rec["hallucination"] = "requires_asl_review"
    rec["requires_asl_review"] = "yes"
    return ("[migrated 2026-09-07: prior hallucination=yes reflected a text-based "
            "topic-mismatch judgment, not confirmed visual grounding; downgraded to "
            "hallucination=requires_asl_review and flagged reference_topic_mismatch=yes]")


def load_or_init_reviews(clip_ids: list[str]) -> dict:
    if REVIEW_JSON.exists():
        try:
            data = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        data = {}
    changed = False
    for cid in clip_ids:
        if cid not in data:
            data[cid] = blank_annotation()
            changed = True
            continue
        rec = data[cid]
        # backfill any newly-added tag columns without discarding existing answers
        for c in CONTENT_TAG_COLUMNS:
            rec.setdefault("content", {}).setdefault(c, False)
        for c in FAILURE_TAG_COLUMNS:
            rec.setdefault("failure", {}).setdefault(c, False)
        pre_existing_fields = set(rec.keys())
        for c in SEMANTIC_FIELDS:
            rec.setdefault(c, "")
        if "reference_topic_mismatch" not in pre_existing_fields:
            note = _migrate_legacy_hallucination_yes(rec)
            if note:
                existing_notes = (rec.get("notes") or "").strip()
                rec["notes"] = (existing_notes + " " + note).strip() if existing_notes else note
                changed = True
    if changed or not REVIEW_JSON.exists():
        persist_reviews(data, clip_ids)
    return data


def persist_reviews(data: dict, clip_order: list[str]) -> None:
    with _SAVE_LOCK:
        REVIEW_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        fieldnames = (["clip_id"]
                      + [f"content__{c}" for c in CONTENT_TAG_COLUMNS]
                      + [f"failure__{c}" for c in FAILURE_TAG_COLUMNS]
                      + SEMANTIC_FIELDS)
        with REVIEW_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for cid in clip_order:
                rec = data.get(cid, blank_annotation())
                row = {"clip_id": cid}
                for c in CONTENT_TAG_COLUMNS:
                    row[f"content__{c}"] = rec["content"].get(c, False)
                for c in FAILURE_TAG_COLUMNS:
                    row[f"failure__{c}"] = rec["failure"].get(c, False)
                for c in SEMANTIC_FIELDS:
                    row[c] = rec.get(c, "")
                w.writerow(row)


# ─────────────────────────────────────────────────────────────────────────
# On-demand thumbnails (cached) — no model call, same sampler as baseline run
# ─────────────────────────────────────────────────────────────────────────
def get_thumbnails(clip_id: str, manifest_row: dict) -> dict:
    cache_file = THUMB_CACHE_DIR / f"{clip_id}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    pred_path = BASELINE_DIR / "predictions" / f"{clip_id}.json"
    if not pred_path.exists() or not manifest_row:
        return {"thumbs": [], "timestamps": [], "note": "prediction or manifest row not found"}

    rm = json.loads(pred_path.read_text(encoding="utf-8"))["run_metadata"]
    video_path = REPO_ROOT / manifest_row["local_video_path"]
    if not video_path.exists():
        return {"thumbs": [], "timestamps": [], "note": f"video not found: {video_path}"}

    times, motion = rcm.probe_motion(str(video_path))
    runs = rcm.segment_runs(times, motion)
    stamps = rcm.allocate_timestamps(runs, rm["frame_budget"])
    if not stamps:
        return {"thumbs": [], "timestamps": [], "note": "no frames sampled"}

    n = min(N_THUMBS, len(stamps))
    idxs = sorted(set(round(i * (len(stamps) - 1) / max(1, n - 1)) for i in range(n)))
    picked = [stamps[i] for i in idxs]

    thumbs = []
    THUMB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(picked):
        out = THUMB_CACHE_DIR / f"{clip_id}__{i}.jpg"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video_path),
             "-frames:v", "1", "-vf", f"scale={THUMB_WIDTH}:-2", "-q:v", "7", "-y", str(out)],
            capture_output=True, timeout=60,
        )
        if out.exists() and out.stat().st_size > 0:
            thumbs.append("data:image/jpeg;base64," + base64.b64encode(out.read_bytes()).decode())
            out.unlink()  # only the base64 cache json is kept, not the loose jpg
        else:
            thumbs.append(None)

    result = {"thumbs": thumbs, "timestamps": [round(t, 2) for t in picked]}
    cache_file.write_text(json.dumps(result), encoding="utf-8")
    return result


# ─────────────────────────────────────────────────────────────────────────
# HTTP handler
# ─────────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    server_version = "ASLReviewApp/1.0"

    def log_message(self, fmt, *args):  # quieter default logging
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, text: str, status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self):
        self._json({"error": "not found"}, status=404)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/":
            self._html(APP_HTML_PATH.read_text(encoding="utf-8"))
            return

        if path == "/api/state":
            clips = load_ordered_clips()
            clip_ids = [c["clip_id"] for c in clips]
            reviews = load_or_init_reviews(clip_ids)
            self._json({"clips": clips, "reviews": reviews,
                        "content_tags": CONTENT_TAG_COLUMNS, "failure_tags": FAILURE_TAG_COLUMNS,
                        "content_tags_asl_review": sorted(CONTENT_TAG_ASL_REVIEW),
                        "failure_tags_asl_review": sorted(FAILURE_TAG_ASL_REVIEW)})
            return

        m = re.match(r"^/api/thumbs/([^/]+)$", path)
        if m:
            clip_id = m.group(1)
            manifest = load_manifest()
            self._json(get_thumbnails(clip_id, manifest.get(clip_id)))
            return

        m = re.match(r"^/inspector/([^/]+)$", path)
        if m:
            clip_id = m.group(1)
            fp = INSPECTOR_DIR / f"{clip_id}.html"
            if fp.exists():
                self._html(fp.read_text(encoding="utf-8"))
            else:
                self._not_found()
            return

        m = re.match(r"^/video/([^/]+)$", path)
        if m:
            self._serve_video(m.group(1))
            return

        self._not_found()

    def _serve_video(self, clip_id: str):
        manifest = load_manifest()
        row = manifest.get(clip_id)
        if not row:
            self._not_found()
            return
        video_path = (REPO_ROOT / row["local_video_path"]).resolve()
        # safety: must resolve inside the frozen benchmark's video directory
        allowed_root = (REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2" / "videos").resolve()
        if allowed_root not in video_path.parents or not video_path.exists():
            self._not_found()
            return

        file_size = video_path.stat().st_size
        content_type = mimetypes.guess_type(str(video_path))[0] or "video/mp4"
        range_header = self.headers.get("Range")

        if range_header:
            m = re.match(r"bytes=(\d+)-(\d*)", range_header)
            start = int(m.group(1)) if m else 0
            end = int(m.group(2)) if m and m.group(2) else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(length))
            self.end_headers()
            with video_path.open("rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(65536, remaining))
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        return
                    remaining -= len(chunk)
        else:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with video_path.open("rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        return

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/save":
            self._not_found()
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, ValueError):
            self._json({"error": "bad json"}, status=400)
            return

        clip_id = payload.get("clip_id")
        annotation = payload.get("annotation")
        if not clip_id or not isinstance(annotation, dict):
            self._json({"error": "missing clip_id or annotation"}, status=400)
            return

        clips = load_ordered_clips()
        clip_ids = [c["clip_id"] for c in clips]
        if clip_id not in clip_ids:
            self._json({"error": f"unknown clip_id {clip_id!r}"}, status=400)
            return

        reviews = load_or_init_reviews(clip_ids)
        rec = blank_annotation()
        rec["content"] = {c: bool(annotation.get("content", {}).get(c, False)) for c in CONTENT_TAG_COLUMNS}
        rec["failure"] = {c: bool(annotation.get("failure", {}).get(c, False)) for c in FAILURE_TAG_COLUMNS}
        for c in SEMANTIC_FIELDS:
            rec[c] = str(annotation.get(c, "") or "")
        rec["last_saved_utc"] = datetime.now(timezone.utc).isoformat()
        reviews[clip_id] = rec
        persist_reviews(reviews, clip_ids)
        self._json({"ok": True, "clip_id": clip_id, "last_saved_utc": rec["last_saved_utc"]})


def main() -> None:
    clips = load_ordered_clips()  # validates 40/12/no-dup up front, fails fast on config errors
    clip_ids = [c["clip_id"] for c in clips]
    load_or_init_reviews(clip_ids)  # ensures review files exist / are backfilled before serving
    THUMB_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"ASL Phase-1 review app running at http://{HOST}:{PORT}/  (Ctrl+C to stop)")
    print(f"Annotations persist to: {REVIEW_JSON.relative_to(REPO_ROOT)}")
    print(f"                        {REVIEW_CSV.relative_to(REPO_ROOT)}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
