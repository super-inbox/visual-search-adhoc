#!/usr/bin/env python3
"""Phase D1 trajectory-tracking POC — raw pose extraction only.

Runs rtmlib's Wholebody() (RTMDet-tiny detector + RTMW pose model,
COCO-WholeBody 133 keypoints: body+feet+face+both hands) over every frame
of one local video and writes the RAW per-frame keypoints/scores to a
landmarks.json file. No derived signals (velocity, pauses, etc. — see
summarize_trajectory.py) and no ASL-specific interpretation of any kind
are computed here; this script only answers "what did the tracker see."

Must be run with the `unisign-cpu-arm64` conda env's interpreter (the only
env in this environment with rtmlib + onnxruntime + opencv installed):

    /opt/anaconda3/envs/unisign-cpu-arm64/bin/python3 extract_trajectory.py \\
        <video_path> <out_json_path>

Reuses the exact same extraction mechanism (rtmlib Wholebody, same cached
ONNX weights under ~/.cache/rtmlib/hub/checkpoints/) that this repo's own
prior Uni-Sign benchmark run used to process this same How2Sign v2
corpus — confirmed via the cached model filenames matching rtmlib's
'lightweight' mode exactly:
  det : yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx
  pose: rtmw-dw-l-m_simcc-cocktail14_270e-256x192_20231122.onnx
No network download occurs if those files are already cached (verified in
this session's smoke test — model load was 0.22s, no download log line).

Does NOT touch the frozen How2Sign v2 benchmark, any existing prediction
file, run_current_model.py, or run_native_video.py. Does NOT call Gemini.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keypoint_schema as ks  # noqa: E402

RTMLIB_VERSION = "0.0.13"
WHOLEBODY_MODE = "lightweight"
CACHE_DIR = Path.home() / ".cache" / "rtmlib" / "hub" / "checkpoints"
DET_MODEL_FILE = CACHE_DIR / "yolox_tiny_8xb8-300e_humanart-6f3252f9.onnx"
POSE_MODEL_FILE = CACHE_DIR / "rtmw-dw-l-m_simcc-cocktail14_270e-256x192_20231122.onnx"


def sha256_of(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract(video_path: Path, out_json: Path) -> dict:
    from rtmlib import Wholebody  # imported here: only needed for --run, not for --help

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open {video_path}")

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    n_frames_reported = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    t_load0 = time.monotonic()
    wb = Wholebody(mode=WHOLEBODY_MODE, backend="onnxruntime", device="cpu")
    model_load_s = round(time.monotonic() - t_load0, 3)

    frames_out = []
    frame_idx = 0
    t0 = time.monotonic()
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        keypoints, scores = wb(frame)  # keypoints: (n_people, 133, 2); scores: (n_people, 133)
        n_people = int(keypoints.shape[0])
        if n_people == 0:
            frames_out.append({
                "frame_idx": frame_idx,
                "t_s": round(frame_idx / src_fps, 4) if src_fps else None,
                "n_people_detected": 0,
                "keypoints_xy": None,
                "keypoints_score": None,
            })
        else:
            # Single-signer corpus: if >1 person is ever detected (background
            # person, detector false positive), take the highest-total-score
            # box as "the signer" and RECORD n_people_detected so this is
            # visible in QA, not silently discarded.
            totals = scores.sum(axis=1)
            best = int(totals.argmax())
            frames_out.append({
                "frame_idx": frame_idx,
                "t_s": round(frame_idx / src_fps, 4) if src_fps else None,
                "n_people_detected": n_people,
                "keypoints_xy": keypoints[best].round(3).tolist(),
                "keypoints_score": scores[best].round(4).tolist(),
            })
        frame_idx += 1
    extraction_s = round(time.monotonic() - t0, 3)
    cap.release()

    output = {
        "clip_id": video_path.stem,
        "source_video": str(video_path),
        "tracker": "rtmlib.Wholebody",
        "rtmlib_version": RTMLIB_VERSION,
        "wholebody_mode": WHOLEBODY_MODE,
        "backend": "onnxruntime",
        "device": "cpu",
        "det_model_file": DET_MODEL_FILE.name,
        "det_model_sha256": sha256_of(DET_MODEL_FILE),
        "pose_model_file": POSE_MODEL_FILE.name,
        "pose_model_sha256": sha256_of(POSE_MODEL_FILE),
        "keypoint_schema": "coco_wholebody_133",
        "keypoint_schema_module": "asl-translator/asl-eval/trajectory_probe/keypoint_schema.py",
        "kpt_detected_threshold": ks.KPT_DETECTED_THRESHOLD,
        "source_fps": src_fps,
        "frame_width": frame_w,
        "frame_height": frame_h,
        "n_frames_reported_by_opencv": n_frames_reported,
        "n_frames_processed": len(frames_out),
        "model_load_wall_clock_s": model_load_s,
        "extraction_wall_clock_s": extraction_s,
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Raw tracker output only — no derived signals, no ASL-specific "
                "interpretation. See summarize_trajectory.py for derived signals.",
        "frames": frames_out,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return output


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: extract_trajectory.py <video_path> <out_json_path>", file=sys.stderr)
        return 2
    video_path = Path(sys.argv[1]).resolve()
    out_json = Path(sys.argv[2]).resolve()
    if not video_path.exists():
        print(f"error: video not found: {video_path}", file=sys.stderr)
        return 2
    result = extract(video_path, out_json)
    n_detected = sum(1 for f in result["frames"] if f["n_people_detected"] > 0)
    print(f"{video_path.name}: {result['n_frames_processed']} frames processed, "
          f"{n_detected} with >=1 person detected, "
          f"extraction {result['extraction_wall_clock_s']}s -> {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
