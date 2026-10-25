"""P0-18 GPU pose worker (runs on the canonical GPU host: the VM decoder + GPU extractor environment is the P0-18 pose
environment for development AND for H18).

MANIFEST (built by vm_remote.fetch_manifest from the local SHA-256-verified archive) lists, per video, where its
compressed bytes sit inside the pinned mirror copy of that archive and the sha256 of the inflated member. A prefetch
thread range-fetches each member from the mirror (at most PREFETCH ahead of the GPU, so only a few videos are ever
on disk), inflates it and requires CRC-32, size AND the manifest sha256 to match; the main thread then extracts it
(pose_extract.extract_from_dir: per-frame, CUDA EP HEURISTIC, deterministic, 4 workers), validates and checksums the
npz, and deletes the temporary video copy. Outputs ROOT/poses/<video_name>.npz, ROOT/poses/extract_log.jsonl,
ROOT/poses/fetch_log.jsonl, ROOT/poses/SUMMARY.json, then ROOT/DONE. Resumable: rerun with the same ROOT.

Usage: python -I vm_worker.py ROOT MANIFEST.json
"""
import hashlib, json, os, queue, subprocess, sys, threading, time, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pose_extract as PE  # noqa: E402

PREFETCH = 2


def fetch(url, m, dst, tries=4):
    """Range-fetch one deflated member, inflate to dst, verify CRC-32 / size / sha256. Returns seconds."""
    lo, hi = m["data_offset"], m["data_offset"] + m["csize"] - 1
    for k in range(tries):
        t = time.time()
        p = subprocess.Popen(["curl", "-sSL", "--fail", "-r", f"{lo}-{hi}", url], stdout=subprocess.PIPE)
        d = zlib.decompressobj(-15) if m["method"] == 8 else None
        crc, h, n, got = 0, hashlib.sha256(), 0, 0
        with open(dst + ".part", "wb") as f:
            for b in iter(lambda: p.stdout.read(1 << 22), b""):
                got += len(b)
                b = d.decompress(b) if d else b
                crc = zlib.crc32(b, crc); h.update(b); n += len(b); f.write(b)
            if d:
                b = d.flush(); crc = zlib.crc32(b, crc); h.update(b); n += len(b); f.write(b)
        if p.wait() == 0 and got == m["csize"] and crc == m["crc32"] and n == m["size"] and h.hexdigest() == m["sha256"]:
            os.replace(dst + ".part", dst)
            return time.time() - t
        os.remove(dst + ".part"); time.sleep(5 * 2 ** k)
    raise IOError("fetch/verify failed")


def summarize(root, t_start):
    poses = os.path.join(root, "poses"); last = {}
    for l in open(os.path.join(poses, "extract_log.jsonl")):
        r = json.loads(l); last[r["video"].removesuffix(".mp4")] = r          # a retried video keeps its final record
    for l in open(os.path.join(poses, "fetch_log.jsonl")):
        r = json.loads(l)
        if "error" in r and r["video"] not in last:
            last[r["video"]] = r
    ok = {v: r for v, r in last.items() if "error" not in r and os.path.exists(os.path.join(poses, v + ".npz"))}
    frames = sum(r["frames"] for r in ok.values()); secs = sum(r["seconds_pose"] for r in ok.values())
    return {"completed_videos": len(ok), "failed_videos": {v: r["error"] for v, r in last.items() if v not in ok},
            "total_frames": frames, "pose_seconds": round(secs, 1), "avg_fps": round(frames / secs, 2) if secs else None,
            "worker_wall_s": round(time.time() - t_start, 1),
            "npz_sha256": {v: r["npz_sha256"] for v, r in sorted(ok.items())},
            "arrays_sha256": {v: r["arrays_sha256"] for v, r in sorted(ok.items())}}


def main(root, manifest):
    M = json.load(open(manifest))
    inbox, poses = os.path.join(root, "inbox"), os.path.join(root, "poses")
    os.makedirs(inbox, exist_ok=True); os.makedirs(poses, exist_ok=True)
    wb = PE.make_wholebody("cuda")                       # raises unless CUDAExecutionProvider is active
    env = dict(PE.environment(), device="cuda", started=time.strftime("%Y-%m-%dT%H:%M:%S"),
               manifest_sha256=PE.file_sha256(manifest))
    open(os.path.join(poses, "extractor_env.jsonl"), "a").write(json.dumps(env) + "\n")
    xlog, flog = os.path.join(poses, "extract_log.jsonl"), os.path.join(poses, "fetch_log.jsonl")
    open(xlog, "a").close()
    t_start = time.time()
    todo = [v for v in sorted(M["videos"], key=lambda v: hashlib.sha1(v.encode()).hexdigest())
            if not os.path.exists(os.path.join(poses, v + ".npz"))]
    q = queue.Queue(maxsize=PREFETCH)

    def fetcher():
        with open(flog, "a") as fl:
            for v in todo:
                dst = os.path.join(inbox, v + ".mp4")
                try:
                    dt = fetch(M["url"], M["videos"][v], dst)
                    fl.write(json.dumps({"video": v, "seconds": round(dt, 1),
                                         "MBps": round(M["videos"][v]["csize"] / 1e6 / dt, 1)}) + "\n")
                    q.put(v)
                except Exception as ex:                                     # noqa: BLE001
                    fl.write(json.dumps({"video": v, "error": f"fetch: {ex}"}) + "\n")
                fl.flush()
        q.put(None)

    threading.Thread(target=fetcher, daemon=True).start()
    while (v := q.get()) is not None:
        PE.extract_from_dir(inbox, {v: M["videos"][v]["sha256"]}, poses, wb, xlog, delete_after=True)
    s = summarize(root, t_start)
    json.dump(s, open(os.path.join(poses, "SUMMARY.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in s.items() if not k.endswith("sha256")}), flush=True)
    open(os.path.join(root, "DONE"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
