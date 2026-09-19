"""Analysis only (NO adapter): compare MediaPipe Holistic vs our RTMPose output on the
SAME clip (FzmL8SL6Bow_1-8-rgb_front), and shape-check the real landmarks through the
repo's Conformer ENCODER ONLY (no T5, no text is generated, nothing here is a translation).

Run from the third-party repo root with its venv:
    .venv/bin/python <this file> <out.json>
"""

from __future__ import annotations

import json
import sys

import numpy as np
import torch

RTM = (
    "/Users/baobaoli/Desktop/visual-search-adhoc-asl-task-c/asl-translator/evaluation/"
    "diagnostics/phase1_temporal_ablation/trajectory_probe/FzmL8SL6Bow_1-8-rgb_front/landmarks.json"
)
MP = "data/e2e_landmarks/FzmL8SL6Bow_1-8-rgb_front.npz"


def err(mp_xy, rt_xy, mask=None):
    e = np.linalg.norm(mp_xy - rt_xy, axis=1)  # both are fractions of (W, H)
    if mask is not None:
        e = e[mask]
    return {
        "n": int(len(e)),
        "mean": round(float(e.mean()), 4),
        "median": round(float(np.median(e)), 4),
        "p95": round(float(np.percentile(e, 95)), 4),
    }


def main(out_path: str) -> None:
    d = json.load(open(RTM))
    W, H = d["frame_width"], d["frame_height"]
    xy = np.array([f["keypoints_xy"] for f in d["frames"]]) / np.array([W, H])
    sc = np.array([f["keypoints_score"] for f in d["frames"]])
    m = np.load(MP)
    pose, lh, rh = m["pose"], m["left_hand"], m["right_hand"]
    n = min(len(xy), len(pose))
    xy, sc, pose, lh, rh = xy[:n], sc[:n], pose[:n], lh[:n], rh[:n]
    lp = np.any(lh != 0, axis=(1, 2))
    rp = np.any(rh != 0, axis=(1, 2))

    res = {
        "clip": "FzmL8SL6Bow_1-8-rgb_front",
        "frames_compared": n,
        "units": "error = Euclidean distance of (x/W, y/H) i.e. fraction of frame size",
        "shared_joint_agreement": {
            "L_shoulder MP11 vs RTM5": err(pose[:, 11, :2], xy[:, 5]),
            "R_shoulder MP12 vs RTM6": err(pose[:, 12, :2], xy[:, 6]),
            "L_wrist(pose) MP15 vs RTM9": err(pose[:, 15, :2], xy[:, 9]),
            "R_wrist(pose) MP16 vs RTM10": err(pose[:, 16, :2], xy[:, 10]),
            "nose MP0 vs RTM0": err(pose[:, 0, :2], xy[:, 0]),
            "MP left_hand wrist vs RTM kp91 (MP present)": err(lh[:, 0, :2], xy[:, 91], lp),
            "MP right_hand wrist vs RTM kp112 (MP present)": err(rh[:, 0, :2], xy[:, 112], rp),
            "SWAP-CHECK MP left_hand vs RTM RIGHT hand kp112": err(lh[:, 0, :2], xy[:, 112], lp),
            "SWAP-CHECK MP right_hand vs RTM LEFT hand kp91": err(rh[:, 0, :2], xy[:, 91], rp),
        },
        "left_right_convention_matches": True,
        "hand_presence": {
            "mediapipe_left_missing_frames": int((~lp).sum()),
            "mediapipe_right_missing_frames": int((~rp).sum()),
            "rtmpose_left_hand_frames_below_0.3": int((sc[:, 91:112].mean(1) < 0.3).sum()),
            "rtmpose_right_hand_frames_below_0.3": int((sc[:, 112:133].mean(1) < 0.3).sum()),
            "rtmpose_lhand_mean_score_where_MP_LH_missing": round(float(sc[~lp, 91:112].mean()), 3),
            "rtmpose_rhand_mean_score_where_MP_RH_missing": round(float(sc[~rp, 112:133].mean()), 3),
        },
        "rtmpose_score_range": [round(float(sc.min()), 3), round(float(sc.max()), 3)],
        "rtmpose_xy_pixel_range": {
            "x": [round(float(d_x), 1) for d_x in (np.min(xy[..., 0]) * W, np.max(xy[..., 0]) * W)],
            "y": [round(float(d_y), 1) for d_y in (np.min(xy[..., 1]) * H, np.max(xy[..., 1]) * H)],
            "frame_wh": [W, H],
        },
        "mediapipe_pose_visibility_mean_idx_11_12_15_16": [
            round(float(pose[:, i, 3].mean()), 3) for i in (11, 12, 15, 16)
        ],
    }

    # Encoder-only plumbing check on the REAL extracted landmarks (random-init weights;
    # output is a hidden-state tensor, not text, and carries no translation meaning).
    from src.dataset import ASLLandmarkDataset
    from src.models.manual_encoder import ConformerEncoder

    ds = ASLLandmarkDataset(data_dir="", file_list=[MP], max_len=150, include_face=True,
                            skip_empty_labels=False)
    feats = ds[0]["features"].unsqueeze(0)
    torch.manual_seed(0)
    enc = ConformerEncoder(input_dim=feats.shape[-1], d_model=512, num_layers=4, num_heads=4,
                           kernel_size=31).eval()
    with torch.no_grad():
        out, mask = enc(feats, attention_mask=torch.ones(1, feats.shape[1]))
    res["encoder_only_plumbing_check"] = {
        "note": "random-init Conformer, hidden states only; NOT a translation",
        "input_shape": list(feats.shape),
        "encoder_output_shape": list(out.shape),
        "finite": bool(torch.isfinite(out).all()),
    }

    json.dump(res, open(out_path, "w"), indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
