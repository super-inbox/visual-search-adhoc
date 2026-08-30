#!/usr/bin/env python3
"""Fail if a corpus video shows its own reference answer on screen.

This exists because it already happened. Until 2026-08-30 the corpus's primary
accuracy anchor, `155_demo_asl-demo-translation_26.7s`, was the *published demo
output* with English captions burned into the frame. Every score on it measured
the model's ability to read those captions. The burn-in had even been recorded in
`VIDEO_TYPE_AUDIT.csv` — and read as corroboration that the signing matched,
rather than as contamination. See `data/asl_corpus/CONTAMINATION.md`.

What it does: samples frames from each video in `data/asl_corpus/videos/`, OCRs
them, and compares any on-screen text against that video's reference transcript.
A video whose frames contain its own answer cannot be used to measure recognition.

Local and read-only. Needs `ffmpeg` and `tesseract` on PATH; skips cleanly with a
non-fatal message if either is missing, in the same spirit as TestProductionParity
skipping when curify-studio is not checked out alongside.

Usage:
    python3 asl-translator/asl-eval/check_leakage.py
    python3 asl-translator/asl-eval/check_leakage.py --validate
    python3 asl-translator/asl-eval/check_leakage.py --video path/to/one.mp4

Exit codes: 0 clean (or skipped), 1 leakage detected, 2 validation failed.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

ASL_TRANSLATOR_ROOT = Path(__file__).resolve().parents[1]
CORPUS_ROOT = ASL_TRANSLATOR_ROOT / "data" / "asl_corpus"
VIDEOS_DIR = CORPUS_ROOT / "videos"

SAMPLE_FPS = 0.5          # frames per second of video to OCR
MIN_WORD_LEN = 2          # ignore single characters — OCR noise is full of them
MIN_CONFIDENCE = 65.0     # tesseract per-word confidence
OCR_MIN_WIDTH = 1600      # upscale before OCR; tesseract misses small burned-in captions
OVERLAP_FAIL = 0.30       # fraction of on-screen words also in the reference

# The two known positives, with the reference each one leaks. check_leakage must
# flag both, or it is not working. These files are kept precisely so the detector
# has something true to be tested against.
KNOWN_CONTAMINATED = [
    ("ground_truth/155_demo_asl-demo-translation_26.7s_burned_marketing.mp4",
     "ground_truth/155_demo_asl-demo-translation_26.7s.srt"),
    ("ground_truth_candidates/1320_1000022357_137.2s_burned.mp4",
     "ground_truth_candidates/1320_1000022357_137.2s.srt"),
]


def _have_tools() -> str | None:
    for tool in ("ffmpeg", "tesseract"):
        if shutil.which(tool) is None:
            return tool
    return None


def _ocr_words(image: Path) -> list[str]:
    proc = subprocess.run(["tesseract", str(image), "stdout", "tsv"],
                          capture_output=True, text=True)
    words = []
    for row in csv.DictReader(io.StringIO(proc.stdout), delimiter="\t"):
        try:
            conf = float(row["conf"])
        except (TypeError, ValueError):
            continue
        text = (row.get("text") or "").strip()
        if conf > MIN_CONFIDENCE and len(text) >= MIN_WORD_LEN:
            words.append(text)
    return words


def ocr_video(video: Path, sample_fps: float = SAMPLE_FPS) -> list[tuple[float, str]]:
    """Return [(timestamp_s, text)] for sampled frames that contain readable text.

    Two passes per frame, because one is not enough. Tesseract reads nothing at all
    from 155's burned captions on the full 640x360 frame, and reads them perfectly
    from an upscaled crop of the caption band -- so a full-frame-only checker would
    have declared the very file that caused this whole problem clean. Pass 1 is the
    whole frame upscaled (catches title cards and watermarks anywhere), pass 2 is the
    bottom third upscaled (catches subtitle-style burn-in, which is small and thin).
    """
    found: list[tuple[float, str]] = []
    passes = {
        "full": f"fps={sample_fps},scale={OCR_MIN_WIDTH}:-1",
        "band": f"fps={sample_fps},crop=iw:ih/3:0:ih*2/3,scale={OCR_MIN_WIDTH}:-1",
    }
    with tempfile.TemporaryDirectory() as td:
        per_frame: dict[int, list[str]] = {}
        for name, vf in passes.items():
            out = Path(td) / name
            out.mkdir()
            subprocess.run(
                ["ffmpeg", "-v", "error", "-i", str(video), "-vf", vf,
                 "-q:v", "2", str(out / "f%05d.png")],
                check=True,
            )
            for i, frame in enumerate(sorted(out.glob("f*.png"))):
                words = _ocr_words(frame)
                if words:
                    per_frame.setdefault(i, []).extend(words)
        for i in sorted(per_frame):
            # de-duplicate while preserving order; the two passes overlap
            seen, words = set(), []
            for w in per_frame[i]:
                if w not in seen:
                    seen.add(w)
                    words.append(w)
            found.append((i / sample_fps, " ".join(words)))
    return found


def reference_words(reference: Path) -> set[str]:
    segments = lib.parse_srt(str(reference))
    return set(lib.normalize_text(lib.build_transcript(segments)).split())


def overlap_fraction(onscreen: list[tuple[float, str]], ref_words: set[str]) -> float:
    """How much of what is on screen also appears in the reference."""
    words = lib.normalize_text(" ".join(t for _, t in onscreen)).split()
    words = [w for w in words if len(w) >= MIN_WORD_LEN]
    if not words:
        return 0.0
    return sum(1 for w in words if w in ref_words) / len(words)


def reference_for(video_id: str) -> Path | None:
    """The reference this video would be scored against, if one exists."""
    eval_set = json.loads((CORPUS_ROOT / "evaluation_set.json").read_text(encoding="utf-8"))
    for item in eval_set["items"]:
        if item["video_id"] == video_id:
            return CORPUS_ROOT / item["reference"]
    for pattern in ("ground_truth", "ground_truth_candidates"):
        candidate = CORPUS_ROOT / pattern / f"{video_id}.srt"
        if candidate.exists():
            return candidate
    return None


def check(video: Path, reference: Path | None = None) -> dict:
    video_id = video.stem
    onscreen = ocr_video(video)
    ref = reference or reference_for(video_id)
    frac = overlap_fraction(onscreen, reference_words(ref)) if (ref and onscreen) else 0.0
    return {
        "video": str(video.relative_to(CORPUS_ROOT)) if CORPUS_ROOT in video.parents else str(video),
        "video_id": video_id,
        "frames_with_text": len(onscreen),
        "reference": str(ref.relative_to(CORPUS_ROOT)) if ref else None,
        "reference_overlap": round(frac, 4),
        "leaks": bool(onscreen) and frac >= OVERLAP_FAIL,
        "sample": onscreen[0][1][:100] if onscreen else "",
    }


def manifest_flags() -> dict[str, bool]:
    manifest = json.loads((CORPUS_ROOT / "manifest.json").read_text(encoding="utf-8"))
    return {Path(v["file"]).stem: bool(v.get("label_in_input")) for v in manifest["videos"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", default=None, help="Check a single video instead of the whole corpus")
    ap.add_argument("--validate", action="store_true",
                    help="Also assert the two known-contaminated source files are still detected")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    missing = _have_tools()
    if missing:
        print(f"SKIP: {missing} not on PATH — cannot check for on-screen text.")
        return 0

    targets = [Path(args.video)] if args.video else sorted(VIDEOS_DIR.glob("*.mp4"))
    flags = manifest_flags()
    rows = [check(v) for v in targets]

    width = max(len(r["video_id"]) for r in rows)
    print(f"{'video':<{width}}  {'frames w/ text':>14}  {'ref overlap':>11}  verdict")
    print("-" * (width + 45))
    failures = []
    for r in rows:
        verdict = "LEAKS ITS REFERENCE" if r["leaks"] else ("text on screen" if r["frames_with_text"] else "clean")
        print(f"{r['video_id']:<{width}}  {r['frames_with_text']:>14}  {r['reference_overlap']:>11.2f}  {verdict}")
        if r["leaks"]:
            failures.append(r)
        declared = flags.get(r["video_id"])
        if declared and not r["leaks"]:
            # Expected: a flagged video is only allowed in videos/ as a masked render,
            # so "flagged but clean" is the mask doing its job, not a discrepancy.
            print("    ✓ flagged label_in_input, and the masked input reads clean")
        elif declared is False and r["leaks"]:
            print("    ⚠️  manifest says label_in_input=false but this video shows its own reference")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(rows, indent=2), encoding="utf-8")

    if args.validate:
        print("\nValidating the detector against known positives:")
        ok = True
        for rel, ref_rel in KNOWN_CONTAMINATED:
            path = CORPUS_ROOT / rel
            if not path.exists():
                print(f"  ✗ missing: {rel}")
                ok = False
                continue
            r = check(path, reference=CORPUS_ROOT / ref_rel)
            hit = r["leaks"]
            print(f"  {'✓' if hit else '✗'} {rel} -> overlap {r['reference_overlap']:.2f}, leaks={hit}")
            ok = ok and hit
        if not ok:
            print("\nVALIDATION FAILED — the detector does not flag a file known to be contaminated.")
            return 2
        print("  detector confirmed working on both known positives")

    if failures:
        print(f"\n{len(failures)} video(s) in videos/ show their own reference on screen. "
              f"They cannot measure recognition. See data/asl_corpus/CONTAMINATION.md.")
        return 1
    print("\nNo video in videos/ leaks its reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
