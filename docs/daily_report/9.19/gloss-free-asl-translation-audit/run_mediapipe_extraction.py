"""Thin local driver: run the third-party repo's OWN MediaPipe extractor on one clip.

Run from the third-party repo root with its venv, e.g.:
    cd /Users/baobaoli/Desktop/gloss-free-asl-translation
    .venv/bin/python <this file> <clip.mp4> <out_dir> <summary.json>

Nothing here re-implements extraction:
  * extraction  -> src.data_pipeline.ASLLandmarkExtractor.extract_landmarks / save_landmarks
  * feature dim -> src.dataset.ASLLandmarkDataset (normalisation + flatten + max_len stride)
This script only measures / records what those functions return.
"""

from __future__ import annotations

import json
import os
import platform
import sys
import time

import cv2
import numpy as np


def stream_stats(arr: np.ndarray, name: str) -> dict:
    """Missing == an all-zero landmark set for that frame (the extractor's own
    representation of 'MediaPipe returned no landmarks')."""
    flat = arr.reshape(arr.shape[0], -1)
    frame_missing = ~np.any(flat != 0.0, axis=1)
    out = {
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "frames_missing": int(frame_missing.sum()),
        "frames_present": int((~frame_missing).sum()),
        "missing_rate": float(frame_missing.mean()),
        "nan_count": int(np.isnan(arr).sum()),
        "inf_count": int(np.isinf(arr).sum()),
    }
    present = arr[~frame_missing]
    if len(present):
        out["present_min"] = [float(v) for v in present.reshape(-1, arr.shape[-1]).min(0)]
        out["present_max"] = [float(v) for v in present.reshape(-1, arr.shape[-1]).max(0)]
    return out


def main(video: str, out_dir: str, summary_path: str) -> None:
    from src.data_pipeline import ASLLandmarkExtractor
    from src.dataset import ASLLandmarkDataset

    clip_id = os.path.splitext(os.path.basename(video))[0]

    cap = cv2.VideoCapture(video)
    src_frames_prop = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    extractor = ASLLandmarkExtractor()  # repo defaults: complexity=1, det/track conf=0.5
    t0 = time.perf_counter()
    lm = extractor.extract_landmarks(video)
    runtime = time.perf_counter() - t0

    out_path = os.path.join(out_dir, f"{clip_id}.npz")
    ASLLandmarkExtractor.save_landmarks(lm, out_path)

    n = lm["pose"].shape[0]
    streams = {k: stream_stats(v, k) for k, v in lm.items()}

    # Feature dim exactly as the model would see it (repo's own dataset path).
    feats = {}
    for include_face in (True, False):
        ds = ASLLandmarkDataset(
            data_dir="",
            file_list=[out_path],
            max_len=150,
            include_face=include_face,
            normalize=True,
            skip_empty_labels=False,
        )
        f = ds[0]["features"]
        feats["with_face" if include_face else "no_face"] = {
            "tensor_shape_after_normalise_and_max_len150": list(f.shape),
            "feature_dim": int(f.shape[1]),
            "frames_after_max_len": int(f.shape[0]),
            "nan_count": int(np.isnan(f.numpy()).sum()),
            "abs_max": float(f.abs().max()),
        }
    stride = int(np.ceil(n / 150)) if n > 150 else 1

    summary = {
        "clip_id": clip_id,
        "video_path": video,
        "video_resolution": [w, h],
        "video_fps": fps,
        "video_duration_s_from_frames": n / fps if fps else None,
        "source_frame_count_cv2_prop": src_frames_prop,
        "processed_frame_count": n,
        "extraction_runtime_s": round(runtime, 2),
        "extraction_fps": round(n / runtime, 2),
        "output_npz": out_path,
        "output_npz_bytes": os.path.getsize(out_path),
        "extractor_settings": {
            "api": "mediapipe.solutions.holistic.Holistic",
            "model_complexity": extractor.model_complexity,
            "min_detection_confidence": extractor.min_detection_confidence,
            "min_tracking_confidence": extractor.min_tracking_confidence,
            "refine_face_landmarks": False,
            "static_image_mode": False,
            "face_subset_size": len(extractor.face_indices),
        },
        "streams": streams,
        "landmark_counts": {
            "pose": lm["pose"].shape[1],
            "left_hand": lm["left_hand"].shape[1],
            "right_hand": lm["right_hand"].shape[1],
            "face_subset": lm["face"].shape[1],
            "face_full_mesh_before_subset": 468,
        },
        "max_len_150_stride": stride,
        "model_input_features": feats,
        "env": {
            "python": platform.python_version(),
            "cv2": cv2.__version__,
            "numpy": np.__version__,
            "machine": platform.machine(),
        },
    }
    with open(summary_path, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
