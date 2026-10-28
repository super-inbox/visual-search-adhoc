"""P0-1: reproduce, without any model, the exact keypoint tensor Uni-Sign received for each case x domain.

Calls upstream Uni-Sign S2T_Dataset.load_pose (commit eed438bc, max_length=256) with the frozen per-clip seed
random.seed(int(sha256(clip_id)[:8], 16)), exactly as P0-A decode_candidates.py, and recomputes frame_idx_sha256 and
kps_sha256 the same way. Compares them with the stored P0-A candidates.jsonl records. CPU only, no checkpoint loaded.

Run in the unisign-cpu-arm64 env:
  python -I reproduce_sampling.py --unisign-repo ~/Desktop/curify/p014-work/Uni-Sign --out sampling.jsonl
"""
import argparse, csv, hashlib, json, os, pickle, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
P0A = os.path.join(REPO, "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank")
PREP = os.path.join(REPO, "docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs")
POSE_SUBDIR = "test-pose-rtmpose-192"
DOMAINS = ("A_official", "B_ours_5p39")
UNISIGN_COMMIT = "eed438bcb49e30405cd6ccdfcccca330c134e830"

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--unisign-repo", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    commit = subprocess.run(["git", "-C", a.unisign_repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert commit == UNISIGN_COMMIT, commit
    sys.path.insert(0, a.unisign_repo)
    import torch  # noqa: E402
    import utils as U  # noqa: E402
    from datasets import S2T_Dataset  # noqa: E402

    cases = list(csv.DictReader(open(os.path.join(P0A, "case_list.csv"))))
    assert_not_holdout([c["clip_id"] for c in cases])
    checks = {}
    for line in open(os.path.join(PREP, "CHECKSUMS.sha256")):
        h, p = line.split(None, 1); checks[p.strip()] = h
    args = argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([])
    out = open(a.out, "w")
    for dom in DOMAINS:
        stored = {json.loads(l)["clip_id"]: json.loads(l) for l in open(os.path.join(P0A, "runs/full45", dom, "run1/candidates.jsonl"))}
        ds = S2T_Dataset.__new__(S2T_Dataset)
        ds.args, ds.rgb_support, ds.max_length, ds.phase = args, False, args.max_length, "test"
        ds.pose_dir = os.path.join(PREP, dom, POSE_SUBDIR)
        for c in cases:
            cid = c["clip_id"]; pkl = os.path.join(ds.pose_dir, cid + ".pkl")
            blob = open(pkl, "rb").read(); pose_sha = hashlib.sha256(blob).hexdigest()
            pose = pickle.loads(blob)
            clip_seed = int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16)
            # (1) the upstream draw, exactly as decode_candidates.py
            random.seed(clip_seed)
            kps, _ = ds.load_pose(cid + ".mp4")
            kps = {k: v.float() if torch.is_tensor(v) and v.is_floating_point() else v for k, v in kps.items()}
            kps_sha = hashlib.sha256(json.dumps({k: v.tolist() for k, v in sorted(kps.items()) if torch.is_tensor(v)})
                                     .encode()).hexdigest()
            # (2) the selected indices, recomputed independently with the same rule
            start, dur = (pose["start"], pose["end"] - pose["start"]) if "start" in pose else (0, len(pose["scores"]))
            fidx = [start + i for i in (sorted(random.Random(clip_seed).sample(range(dur), k=ds.max_length))
                                        if dur > ds.max_length else range(dur))]
            assert len(fidx) == int(kps["body"].shape[0]), (cid, dom)
            s = stored[cid]
            rec = {"review_id": c["review_id"], "clip_id": cid, "domain": dom,
                   "pose_path": os.path.relpath(pkl, REPO), "pose_sha256": pose_sha,
                   "pose_sha_eq_checksums": pose_sha == checks[f"{dom}/{POSE_SUBDIR}/{cid}.pkl"],
                   "pose_sha_eq_p0a": pose_sha == s["pose_sha256"],
                   "pose_frames": len(pose["scores"]), "pose_has_start_key": "start" in pose,
                   "pose_w_h": [int(x) for x in pose.get("w_h", [])], "max_length": ds.max_length,
                   "subsampled": dur > ds.max_length, "clip_seed": clip_seed, "selected_count": len(fidx),
                   "selected_indices": fidx,
                   "frame_idx_sha256": hashlib.sha256(json.dumps(fidx).encode()).hexdigest(),
                   "kps_sha256": kps_sha, "stored_frame_idx_sha256": s["frame_idx_sha256"], "stored_kps_sha256": s["kps_sha256"],
                   "stored_T_frames": s["T_frames"], "stored_n_frames_raw": s["n_frames_raw"]}
            rec["frame_idx_reproduced"] = rec["frame_idx_sha256"] == s["frame_idx_sha256"]
            rec["kps_reproduced"] = kps_sha == s["kps_sha256"]
            out.write(json.dumps(rec) + "\n"); out.flush()
            print(dom, c["review_id"], rec["pose_frames"], rec["subsampled"], rec["frame_idx_reproduced"], rec["kps_reproduced"], flush=True)


if __name__ == "__main__":
    main()
