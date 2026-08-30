"""Refuse to score, or to run a model on, a video that shows its own answer.

Sits between the corpus metadata and the two tools that can produce a number:
`evaluate.py` (scores a prediction) and `run_current_model.py` (generates one).

The failure this prevents is not hypothetical. Until 2026-08-30 the corpus's
primary accuracy anchor was the published demo *output* with English captions
burned into the frame, and it was scored twice, reported three times, and used to
justify a shipped change — because nothing in the path from "video file" to
"WER 0.0000" ever asked whether the answer was visible in the input.

Stdlib-only, no network, never opens a video.
"""
from __future__ import annotations

import json
from pathlib import Path

CORPUS_ROOT = Path(__file__).resolve().parents[1] / "data" / "asl_corpus"


class LeakageError(RuntimeError):
    """The requested input contains the reference answer."""


def _manifest() -> dict:
    return json.loads((CORPUS_ROOT / "manifest.json").read_text(encoding="utf-8"))


def entry_for(video_path: str | Path) -> dict | None:
    """Find the manifest entry for a video, matched on basename."""
    name = Path(video_path).name
    for video in _manifest()["videos"]:
        if Path(video["file"]).name == name:
            return video
    return None


def assert_input_usable(video_path: str | Path) -> None:
    """Raise if this file is a known-contaminated source, or is flagged but unmasked.

    Matching is on basename, so it also catches the reference renders parked in
    `ground_truth/` and `ground_truth_candidates/` — those are the files that
    caused the problem, and pointing a runner at one of them is exactly the
    mistake worth blocking.
    """
    path = Path(video_path)
    name = path.name
    if "_burned" in name:
        raise LeakageError(
            f"{name} is a reference render with the translation burned into the frame, "
            "not a corpus input. Use the file in data/asl_corpus/videos/ instead. "
            "See data/asl_corpus/CONTAMINATION.md."
        )
    entry = entry_for(path)
    if entry is None:
        return  # not a corpus video; nothing to assert
    if not entry.get("label_in_input"):
        return
    mask = entry.get("input_mask") or {}
    masked = mask.get("masked_input")
    if not masked:
        raise LeakageError(
            f"{name} is marked label_in_input=true in manifest.json and declares no input_mask. "
            "Scoring it would measure OCR of on-screen text, not sign recognition."
        )
    if Path(masked).name != name:
        raise LeakageError(
            f"{name} is marked label_in_input=true; the only usable input is {masked}."
        )


def assert_prediction_usable(prediction_path: str | Path) -> None:
    """Raise if a prediction was retracted, or was generated from a leaky input."""
    data = json.loads(Path(prediction_path).read_text(encoding="utf-8"))
    if "contamination" in data:
        block = data["contamination"]
        raise LeakageError(
            f"{Path(prediction_path).name} was RETRACTED on {block.get('RETRACTED')}: "
            f"{block.get('reason', '').strip()}"
        )
    video = data.get("video")
    if video:
        assert_input_usable(video)
