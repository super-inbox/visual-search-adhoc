#!/usr/bin/env python3
"""Offline, production-configuration-equivalent ASL evaluation runner.

Reproduces the CURRENT production sampler / prompt / request-construction logic
for `transcribe_asl()` closely enough to evaluate it, with ALL product side
effects (Supabase, Azure, credits, project/job records) excluded by construction
— this script never imports or calls any of that code.

DEFAULT MODE IS DRY-RUN. Dry-run does local ffmpeg/numpy preprocessing only:
it probes motion, segments active/idle runs, allocates frame timestamps, and
(optionally) extracts frames to a temp dir to verify parity — then reports
what WOULD be sent to the model. It never imports google.genai and never
requires GEMINI_API_KEY.

A real model call requires BOTH --run AND --acknowledge-private-data-upload,
requires GEMINI_API_KEY, and is the only code path that imports google.genai
or opens a network connection. It was NOT executed as part of building this
script — see asl-translator/asl-eval/README.md.

────────────────────────────────────────────────────────────────────────────
SOURCE PROVENANCE
────────────────────────────────────────────────────────────────────────────
Copied (with attribution, not imported) from:

  repo    : curify-studio
  ref     : origin/main
  commit  : ac21f24fd25357f859741421f10775f6800c6c1c
            ("docs(design-agent): §7y — scoring the 30 runs: deterministic
            part perfect, rest still unmeasured")
  file    : curify_background/app/utils/asl_utils.py
  last commit that touched that file on origin/main at inspection time:
            08d12fb fix(asl): keep the provider error message; classify
            spend-cap failures

Inspected read-only via:
  git -C <curify-studio> show origin/main:curify_background/app/utils/asl_utils.py

curify-studio was NOT checked out, pulled, merged, or modified to build this
script. The functions below (`_probe_motion`, `_segment_runs`,
`_allocate_timestamps`, `_extract_frames`, `PRODUCTION_PROMPT`, the response
parser in `_call_vlm_dry`/`call_gemini`) are line-for-line ports of that
commit's logic, with the DB/credit/orchestration call sites removed. See
"PRODUCTION PARITY" in the README for the constant-by-constant diff (none, by
design) and the prompt SHA-256.

Note on the source module itself: as of the inspected commit, asl_utils.py's
own docstring records a negative evaluation result ("THE RECOGNISER DOES NOT
WORK. DO NOT SHIP.") — non-reproducible, order-independent output on repeat
runs. This script exists to let that claim be re-checked locally and on more
of the corpus, not to dispute or confirm it in advance.

Do not treat any output of this script's --run path (not executed here) as
literally reproducing a past production job — Gemini decoding is
non-deterministic even at temperature 0 in practice. Treat it as
"production-configuration-equivalent", not "the same output".
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# ─────────────────────────────────────────────────────────────────────────
# Copied production constants — verified against origin/main's
# asl-translator/data/asl_corpus/manifest.json → baseline0_config (see README
# "Production parity"). Do NOT import these from curify-studio: importing app.config.Settings
# requires unrelated production environment variables at import time.
# ─────────────────────────────────────────────────────────────────────────
ASL_MODEL = "gemini-2.5-flash"
PROBE_FPS = 4.0
PROBE_WIDTH = 160
FRAME_BUDGET = 96
KEYFRAME_WIDTH = 512
MIN_FRAMES_PER_RUN = 2
BATCH_SIZE = 24
IDLE_QUANTILE = 0.35
ABS_MOTION_FLOOR = 2.0

SOURCE_REPO = "curify-studio"
SOURCE_REF = "origin/main"
SOURCE_COMMIT = "ac21f24fd25357f859741421f10775f6800c6c1c"
SOURCE_FILE = "curify_background/app/utils/asl_utils.py"

CONFIGS = {
    "baseline0": {
        "model": ASL_MODEL,
        "temperature": None,  # omitted from GenerateContentConfig, matches production
        "temperature_label": "temperature_unset_provider_default",
    },
    "temperature0": {
        "model": ASL_MODEL,
        "temperature": 0.0,
        "temperature_label": "0.0",
    },
}

# Production prompt, copied verbatim from _PROMPT in the source file above.
PRODUCTION_PROMPT = """You are reading American Sign Language (ASL) from ordered video frames.

Each image is labelled with its timestamp in seconds. The frames are NOT evenly
spaced — they were sampled densely where the signer was actively signing and
sparsely where the signer was still.

Produce an English translation of what is being signed.

Rules:
- Translate meaning into natural English. Do NOT output ASL gloss.
- Group into short caption-length segments with start/end seconds taken from the
  frame timestamps you used.
- Frames are sparse: you are seeing key moments, not every sign. Where a sign is
  ambiguous, prefer the reading that fits the surrounding context.
- If a stretch shows no actual signing (signer resting, adjusting, or absent),
  omit it rather than inventing content.
- If you cannot read the signing with reasonable confidence, say so honestly in
  the `notes` field instead of guessing.

Return STRICT JSON only:
{"segments":[{"start":<sec>,"end":<sec>,"text":"..."}],
 "confidence":"high|medium|low",
 "notes":"what limited the reading, if anything"}
"""


def prompt_sha256() -> str:
    import hashlib
    return hashlib.sha256(PRODUCTION_PROMPT.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────
# Dataclasses (mirrors production's MotionRun shape)
# ─────────────────────────────────────────────────────────────────────────
@dataclass
class MotionRun:
    start_s: float
    end_s: float
    energy: float
    active: bool

    @property
    def duration(self) -> float:
        return max(0.0, self.end_s - self.start_s)


# ─────────────────────────────────────────────────────────────────────────
# Stage 1: motion probe — ported from asl_utils._probe_motion
# ─────────────────────────────────────────────────────────────────────────
def probe_motion(video_path: str, probe_fps: float = PROBE_FPS) -> tuple:
    import numpy as np

    w = PROBE_WIDTH
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", video_path],
        capture_output=True, text=True, timeout=60,
    ).stdout.strip().split(",")
    src_w, src_h = int(probe[0]), int(probe[1])
    h = max(2, int(round(w * src_h / src_w)) // 2 * 2)

    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", video_path,
         "-vf", f"fps={probe_fps},scale={w}:{h},format=gray",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True, timeout=1800,
    )
    buf = proc.stdout
    frame_bytes = w * h
    n = len(buf) // frame_bytes
    if n < 2:
        return [], []

    arr = np.frombuffer(buf[: n * frame_bytes], dtype=np.uint8).reshape(n, h, w).astype(np.int16)
    diffs = np.abs(arr[1:] - arr[:-1]).mean(axis=(1, 2))
    times = [(i + 1) / probe_fps for i in range(len(diffs))]
    return times, diffs.tolist()


# ─────────────────────────────────────────────────────────────────────────
# Stage 2: segmentation — ported from asl_utils._segment_runs
# ─────────────────────────────────────────────────────────────────────────
def segment_runs(times: List[float], motion: List[float]) -> List[MotionRun]:
    import numpy as np

    if not motion:
        return []
    m = np.asarray(motion)
    if len(m) >= 5:
        k = np.ones(5) / 5.0
        m = np.convolve(m, k, mode="same")
    thresh = max(float(np.quantile(m, IDLE_QUANTILE)), ABS_MOTION_FLOOR)
    if float(m.max()) < ABS_MOTION_FLOOR:
        return [MotionRun(times[0], times[-1], float(m.sum()), False)]

    runs: List[MotionRun] = []
    cur_active = bool(m[0] > thresh)
    start = times[0]
    energy = 0.0
    for t, v in zip(times, m):
        is_active = bool(v > thresh)
        if is_active != cur_active:
            runs.append(MotionRun(start, t, energy, cur_active))
            start, energy, cur_active = t, 0.0, is_active
        energy += float(v)
    runs.append(MotionRun(start, times[-1], energy, cur_active))
    return runs


# ─────────────────────────────────────────────────────────────────────────
# Stage 3: timestamp allocation — ported from asl_utils._allocate_timestamps
# ─────────────────────────────────────────────────────────────────────────
def allocate_timestamps(runs: List[MotionRun], budget: int = FRAME_BUDGET) -> List[float]:
    active = [r for r in runs if r.active and r.duration > 0]
    if not active:
        if not runs:
            return []
        lo, hi = runs[0].start_s, runs[-1].end_s
        n = min(budget, 12)
        return [lo + (hi - lo) * i / max(1, n - 1) for i in range(n)]

    total_energy = sum(r.energy for r in active) or 1.0
    stamps: List[float] = []
    for r in active:
        share = r.energy / total_energy
        n = max(MIN_FRAMES_PER_RUN, int(round(budget * share)))
        for i in range(n):
            frac = (i + 0.5) / n
            stamps.append(r.start_s + r.duration * frac)
    stamps.sort()
    if len(stamps) > budget:
        idx = [int(round(i * (len(stamps) - 1) / (budget - 1))) for i in range(budget)]
        stamps = [stamps[i] for i in sorted(set(idx))]
    return stamps


# ─────────────────────────────────────────────────────────────────────────
# Stage 4: frame extraction — ported from asl_utils._extract_frames
# ─────────────────────────────────────────────────────────────────────────
def extract_frames(video_path: str, stamps: List[float], outdir: str) -> List[str]:
    paths = []
    for i, t in enumerate(stamps):
        out = os.path.join(outdir, f"f_{i:04d}_{t:07.2f}.jpg")
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", video_path,
             "-frames:v", "1", "-vf", f"scale={KEYFRAME_WIDTH}:-2", "-q:v", "3", out],
            capture_output=True, timeout=120,
        )
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0:
            paths.append(out)
    return paths


def expected_batch_count(n_frames: int, batch_size: int = BATCH_SIZE) -> int:
    if n_frames <= 0:
        return 0
    return (n_frames + batch_size - 1) // batch_size


# ─────────────────────────────────────────────────────────────────────────
# Local, network-free video probing (duration only — for reporting)
# ─────────────────────────────────────────────────────────────────────────
def probe_duration(video_path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", video_path],
        capture_output=True, text=True, timeout=60,
    ).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


# ─────────────────────────────────────────────────────────────────────────
# Input validation — local files only, no URLs, no remote resolution
# ─────────────────────────────────────────────────────────────────────────
_URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")


def validate_local_video_path(raw: str) -> Path:
    if _URL_RE.match(raw):
        raise ValueError(
            f"refusing to accept a URL as --video ({raw!r}); this runner only "
            "reads local files — no downloads, no Azure blobs, no YouTube, no "
            "Supabase IDs."
        )
    path = Path(raw)
    if not path.exists():
        raise FileNotFoundError(f"video not found: {path}")
    if not path.is_file():
        raise ValueError(f"not a file: {path}")
    return path


# ─────────────────────────────────────────────────────────────────────────
# Dry-run pipeline (no network, no google.genai import)
# ─────────────────────────────────────────────────────────────────────────
@dataclass
class DryRunReport:
    video: str
    duration_s: float
    probe_frame_count: int
    active_run_count: int
    idle_run_count: int
    sampled_frame_count: int
    frame_budget: int
    used_full_budget: bool
    expected_model_calls: int
    selected_timestamps: List[float] = field(default_factory=list)
    frames_extracted: int = 0
    frames_verified_on_disk: bool = False


def run_dry(video_path: Path, frame_budget: int, extract: bool, keep_frames_dir: Optional[str]) -> DryRunReport:
    duration = probe_duration(str(video_path))
    times, motion = probe_motion(str(video_path))
    if not times:
        raise RuntimeError("could not read video frames for motion probe")

    runs = segment_runs(times, motion)
    stamps = allocate_timestamps(runs, frame_budget)

    frames_extracted = 0
    if extract:
        if keep_frames_dir:
            os.makedirs(keep_frames_dir, exist_ok=True)
            paths = extract_frames(str(video_path), stamps, keep_frames_dir)
            frames_extracted = len(paths)
        else:
            with tempfile.TemporaryDirectory(prefix="asl_eval_dryrun_") as td:
                paths = extract_frames(str(video_path), stamps, td)
                frames_extracted = len(paths)
            # td is removed automatically on context exit

    active = [r for r in runs if r.active]
    idle = [r for r in runs if not r.active]

    return DryRunReport(
        video=str(video_path),
        duration_s=round(duration or (times[-1] if times else 0.0), 3),
        probe_frame_count=len(times),
        active_run_count=len(active),
        idle_run_count=len(idle),
        sampled_frame_count=len(stamps),
        frame_budget=frame_budget,
        used_full_budget=len(stamps) >= frame_budget,
        expected_model_calls=expected_batch_count(len(stamps)),
        selected_timestamps=[round(t, 3) for t in stamps],
        frames_extracted=frames_extracted,
        frames_verified_on_disk=extract,
    )


def print_dry_run_report(report: DryRunReport, config_name: str) -> None:
    cfg = CONFIGS[config_name]
    print("=" * 72)
    print("DRY RUN ONLY — NO MODEL CALL WAS MADE.")
    print("=" * 72)
    print(f"video                 : {report.video}")
    print(f"config                : {config_name}")
    print(f"model                 : {cfg['model']}")
    print(f"temperature mode      : {cfg['temperature_label']}")
    print(f"duration_s            : {report.duration_s}")
    print(f"motion probe count    : {report.probe_frame_count} (probe_fps={PROBE_FPS})")
    print(f"active runs           : {report.active_run_count}")
    print(f"idle runs             : {report.idle_run_count}")
    print(f"frame_budget          : {report.frame_budget}")
    print(f"sampled frame count   : {report.sampled_frame_count}")
    print(f"used full budget      : {report.used_full_budget}")
    print(f"expected Gemini calls : {report.expected_model_calls} (batch_size={BATCH_SIZE})")
    if report.frames_verified_on_disk:
        print(f"frames extracted (tmp, deleted after run unless --keep-frames-dir): {report.frames_extracted}")
    print(f"selected timestamps (s): {report.selected_timestamps}")
    print("=" * 72)
    print("DRY RUN ONLY — NO MODEL CALL WAS MADE.")
    print("=" * 72)


def dry_run_report_to_json(report: DryRunReport, config_name: str, video_arg: str) -> dict:
    cfg = CONFIGS[config_name]
    return {
        "project_id": None,
        "video": video_arg,
        "producer": "asl-translator/asl-eval/run_current_model.py (dry_run)",
        "warning": "DRY RUN — no model call was made; no prediction segments exist.",
        "dry_run": True,
        "run_metadata": {
            "config": config_name,
            "model": cfg["model"],
            "temperature": cfg["temperature_label"],
            "frame_budget": FRAME_BUDGET,
            "keyframe_width": KEYFRAME_WIDTH,
            "batch_size": BATCH_SIZE,
            "duration_s": report.duration_s,
            "motion_probe_count": report.probe_frame_count,
            "active_run_count": report.active_run_count,
            "idle_run_count": report.idle_run_count,
            "frames_sampled": report.sampled_frame_count,
            "used_full_budget": report.used_full_budget,
            "model_calls": 0,
            "expected_model_calls": report.expected_model_calls,
            "production_side_effects": False,
            "source_repo": SOURCE_REPO,
            "source_ref": SOURCE_REF,
            "source_commit": SOURCE_COMMIT,
            "source_file": SOURCE_FILE,
            "prompt_sha256": prompt_sha256(),
        },
        "selected_timestamps_s": report.selected_timestamps,
        "segments": [],
    }


# ─────────────────────────────────────────────────────────────────────────
# Real-run path — GATED. Not executed by this task. google.genai is only
# imported inside this function, only reached when --run is passed.
# ─────────────────────────────────────────────────────────────────────────
def run_real(video_path: Path, config_name: str, frame_budget: int, output_path: Path) -> None:
    """Call Gemini directly with production-equivalent frames/prompt/config.

    Requires GEMINI_API_KEY. Writes ONLY the specified local --output file.
    No Supabase, no Azure, no credits, no project/job records — this function
    does not import or reference any of that code.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit(
            "GEMINI_API_KEY is not set. A real run requires it explicitly — "
            "refusing to fall back to any implicit credential source."
        )

    from google import genai
    from google.genai import types as gtypes

    cfg = CONFIGS[config_name]
    client = genai.Client(api_key=api_key)

    times, motion = probe_motion(str(video_path))
    if not times:
        raise RuntimeError("could not read video frames for motion probe")
    runs = segment_runs(times, motion)
    stamps = allocate_timestamps(runs, frame_budget)

    segments = []
    model_calls = 0
    with tempfile.TemporaryDirectory(prefix="asl_eval_run_") as td:
        frames = extract_frames(str(video_path), stamps, td)
        for i in range(0, len(frames), BATCH_SIZE):
            batch = frames[i:i + BATCH_SIZE]
            parts = [gtypes.Part.from_text(text=PRODUCTION_PROMPT)]
            for p in batch:
                ts = float(re.search(r"_(\d+\.\d+)\.jpg$", p).group(1))
                parts.append(gtypes.Part.from_text(text=f"[t={ts:.2f}s]"))
                with open(p, "rb") as fh:
                    parts.append(gtypes.Part.from_bytes(data=fh.read(), mime_type="image/jpeg"))

            gen_config_kwargs = {"response_mime_type": "application/json"}
            if cfg["temperature"] is not None:
                gen_config_kwargs["temperature"] = cfg["temperature"]

            resp = client.models.generate_content(
                model=cfg["model"],
                contents=[gtypes.Content(role="user", parts=parts)],
                config=gtypes.GenerateContentConfig(**gen_config_kwargs),
            )
            model_calls += 1
            raw = (resp.text or "").strip()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                m = re.search(r"\{.*\}", raw, re.S)
                data = json.loads(m.group(0)) if m else {"segments": []}
            for s in data.get("segments", []):
                try:
                    segments.append({
                        "line": len(segments) + 1,
                        "start": float(s["start"]),
                        "end": float(s["end"]),
                        "text": str(s.get("text", "")).strip(),
                    })
                except (KeyError, TypeError, ValueError):
                    continue

        duration = times[-1]
        output = {
            "project_id": None,
            "video": str(video_path),
            "producer": "asl-translator/asl-eval/run_current_model.py (--run)",
            "warning": "UNVERIFIED machine output — offline evaluation run, not a production job.",
            "run_metadata": {
                "config": config_name,
                "model": cfg["model"],
                "temperature": cfg["temperature_label"],
                "frame_budget": FRAME_BUDGET,
                "keyframe_width": KEYFRAME_WIDTH,
                "batch_size": BATCH_SIZE,
                "duration_s": round(duration, 3),
                "frames_sampled": len(frames),
                "model_calls": model_calls,
                "production_side_effects": False,
                "source_repo": SOURCE_REPO,
                "source_ref": SOURCE_REF,
                "source_commit": SOURCE_COMMIT,
                "source_file": SOURCE_FILE,
                "prompt_sha256": prompt_sha256(),
            },
            "segments": segments,
        }
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(segments)} segment(s) from {model_calls} model call(s) to {output_path}")


# ─────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────
def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--video", required=True, help="Path to a LOCAL video file. No URLs.")
    ap.add_argument("--config", choices=sorted(CONFIGS), default="baseline0",
                     help="baseline0 (temperature unset, matches production) or temperature0.")
    ap.add_argument("--frame-budget", type=int, default=FRAME_BUDGET,
                     help=f"Override frame budget for local experimentation (default: production {FRAME_BUDGET}).")
    ap.add_argument("--extract-frames", action="store_true",
                     help="Locally extract sampled frames to a temp dir (auto-deleted) to verify parity. No network.")
    ap.add_argument("--keep-frames-dir", default=None, metavar="DIR",
                     help="If set with --extract-frames, save frames to this LOCAL directory instead of a temp dir "
                          "(NOT auto-deleted). Frames may show identifiable people — you are responsible for "
                          "deleting them. Requires --extract-frames.")
    ap.add_argument("--output", default=None, help="Output JSON path. Required with --run.")
    ap.add_argument("--json-out", default=None,
                     help="Also write the dry-run report as JSON to this path (dry-run only).")
    ap.add_argument("--run", action="store_true",
                     help="NOT EXECUTED IN THIS PHASE. Enables the real Gemini call path. Also requires "
                          "--acknowledge-private-data-upload and GEMINI_API_KEY.")
    ap.add_argument("--acknowledge-private-data-upload", action="store_true",
                     help="Required together with --run: confirms you understand sampled frames contain "
                          "identifiable people and will leave this machine.")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    if args.keep_frames_dir and not args.extract_frames:
        ap.error("--keep-frames-dir requires --extract-frames")

    try:
        video_path = validate_local_video_path(args.video)
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.run:
        if not args.acknowledge_private_data_upload:
            print(
                "error: --run requires --acknowledge-private-data-upload. Sampled video frames "
                "contain identifiable people and a real run sends them to Gemini, off this machine. "
                "No network call was made.",
                file=sys.stderr,
            )
            return 2
        if not args.output:
            ap.error("--output is required with --run")
        print(
            "REAL MODEL RUN REQUESTED (--run + --acknowledge-private-data-upload present).\n"
            "This path was intentionally NOT exercised while building this script.",
            file=sys.stderr,
        )
        run_real(video_path, args.config, args.frame_budget, Path(args.output))
        return 0

    if args.acknowledge_private_data_upload:
        print(
            "note: --acknowledge-private-data-upload was given without --run — this is still a "
            "dry run. No network call was made.",
        )

    if args.keep_frames_dir:
        print(
            f"privacy warning: extracted frames will be written to {args.keep_frames_dir!r} and "
            "NOT auto-deleted. They may show identifiable people. Delete them yourself when done."
        )

    report = run_dry(video_path, args.frame_budget, args.extract_frames, args.keep_frames_dir)
    print_dry_run_report(report, args.config)

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(dry_run_report_to_json(report, args.config, args.video), indent=2),
            encoding="utf-8",
        )
        print(f"\nWrote dry-run JSON report to {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
