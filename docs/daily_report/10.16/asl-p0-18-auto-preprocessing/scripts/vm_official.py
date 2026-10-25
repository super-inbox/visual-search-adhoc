"""P0-18 oracle REFERENCE arm C_official on the canonical GPU host (same decoder + GPU extractor environment as
vm_worker.py): official signer-crop clip videos range-fetched from Uni-Sign's archive at a pinned revision
(official_crops.fetch, CRC-32 checked), posed per frame as P0-12 condition C (official_crops.pose_p012 with
pose_extract.make_wholebody("cuda")), the temporary video deleted after its pkl is written.

Outputs ROOT/C_official/<clip_id>.pkl, ROOT/official_log.jsonl (frames, pkl sha256 / error per clip),
ROOT/official_SUMMARY.json, then ROOT/OFFICIAL_DONE. Resumable.

Usage: python -I vm_official.py ROOT IDS.txt CROP_INDEX.tsv
"""
import json, os, pickle, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import official_crops as OC  # noqa: E402
import pose_extract as PE  # noqa: E402


def main(root, ids_path, index_path):
    ids = open(ids_path).read().split(); idx = OC.load_index(index_path)
    out, tmp = os.path.join(root, "C_official"), os.path.join(root, "crop_tmp")
    os.makedirs(out, exist_ok=True); os.makedirs(tmp, exist_ok=True)
    wb = PE.make_wholebody("cuda")                       # raises unless CUDAExecutionProvider is active
    env = dict(PE.environment(), device="cuda", started=time.strftime("%Y-%m-%dT%H:%M:%S"),
               crop_archive_revision=OC.REVISION, ids_sha256=PE.file_sha256(ids_path),
               index_sha256=PE.file_sha256(index_path))
    open(os.path.join(root, "official_env.jsonl"), "a").write(json.dumps(env) + "\n")
    t0 = time.time()
    with open(os.path.join(root, "official_log.jsonl"), "a") as log:
        for c in ids:
            dst = os.path.join(out, c + ".pkl")
            if os.path.exists(dst):
                continue
            if c not in idx:
                log.write(json.dumps({"clip_id": c, "error": "no_official_crop"}) + "\n"); continue
            vp = os.path.join(tmp, c + ".mp4"); t = time.time()
            try:
                OC.fetch(idx[c], vp)
            except Exception as ex:                                     # noqa: BLE001
                log.write(json.dumps({"clip_id": c, "error": f"fetch: {ex}"}) + "\n"); continue
            tf = time.time() - t
            d = OC.pose_p012(vp, wb, PE.WORKERS); os.remove(vp)
            if not d["keypoints"]:
                log.write(json.dumps({"clip_id": c, "error": "no_frames"}) + "\n"); continue
            pickle.dump(d, open(dst + ".tmp", "wb")); os.replace(dst + ".tmp", dst)
            log.write(json.dumps({"clip_id": c, "frames": len(d["keypoints"]), "seconds_fetch": round(tf, 2),
                                  "seconds_pose": round(time.time() - t - tf, 2),
                                  "pkl_sha256": PE.file_sha256(dst)}) + "\n")
            log.flush()
    last = {}
    for l in open(os.path.join(root, "official_log.jsonl")):
        r = json.loads(l); last[r["clip_id"]] = r
    ok = {c: r for c, r in last.items() if "error" not in r and os.path.exists(os.path.join(out, c + ".pkl"))}
    fr = sum(r["frames"] for r in ok.values()); sp = sum(r["seconds_pose"] for r in ok.values())
    S = {"completed_clips": len(ok), "failed_clips": {c: r["error"] for c, r in last.items() if c not in ok},
         "total_frames": fr, "pose_seconds": round(sp, 1), "avg_fps": round(fr / sp, 2) if sp else None,
         "wall_s": round(time.time() - t0, 1), "pkl_sha256": {c: r["pkl_sha256"] for c, r in sorted(ok.items())}}
    json.dump(S, open(os.path.join(root, "official_SUMMARY.json"), "w"), indent=1)
    os.rmdir(tmp)
    open(os.path.join(root, "OFFICIAL_DONE"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")
    print(json.dumps({k: v for k, v in S.items() if k != "pkl_sha256"}), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:4])
