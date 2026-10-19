"""P0-18: decode_dir.py over N parallel shards (batch size 1 and a per-clip seed make every prediction independent of
the sharding; the thread count per process is fixed and recorded). Merges OUT/shard_*/predictions.jsonl into
OUT/predictions.jsonl in ids order. Resumable.

Usage: python -I decode_parallel.py --pose-dir DIR --ids FILE --out OUT [--procs 3 --threads 4] [--device cpu]
       env: UNISIGN_REPO, MT5, CKPT
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def decode_parallel(pose_dir, ids_file, out, procs, threads, device="cpu", env=None):
    ids = open(ids_file).read().split()
    os.makedirs(out, exist_ok=True)
    jobs = []
    for k in range(procs):
        sd = os.path.join(out, f"shard_{k}"); os.makedirs(sd, exist_ok=True)
        sf = os.path.join(sd, "ids.txt"); open(sf, "w").write("\n".join(ids[k::procs]) + "\n")
        e = dict(env or os.environ, OMP_NUM_THREADS=str(threads), MKL_NUM_THREADS=str(threads))
        jobs.append(subprocess.Popen([sys.executable, "-I", os.path.join(HERE, "decode_dir.py"), "--pose-dir", pose_dir,
                                      "--ids", sf, "--out", sd, "--device", device, "--threads", str(threads)],
                                     env=e, stdout=open(os.path.join(sd, "decode.log"), "a"), stderr=subprocess.STDOUT))
    rc = [j.wait() for j in jobs]
    if any(rc):
        raise RuntimeError(f"decode shards failed {rc} for {pose_dir}; see {out}/shard_*/decode.log")
    P = {}
    for k in range(procs):
        for l in open(os.path.join(out, f"shard_{k}", "predictions.jsonl")):
            j = json.loads(l); P[j["clip_id"]] = j
    assert set(P) == set(ids), "shards incomplete"
    with open(os.path.join(out, "predictions.jsonl"), "w") as f:
        for c in ids:
            f.write(json.dumps(P[c]) + "\n")
    cfg = json.load(open(os.path.join(out, "shard_0", "decode_config.json")))
    json.dump(dict(cfg, n=len(ids), procs=procs, threads=threads, pose_dir=pose_dir),
              open(os.path.join(out, "decode_config.json"), "w"), indent=1)
    return P


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pose-dir", required=True); ap.add_argument("--ids", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=3); ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--device", default="cpu")
    a = ap.parse_args()
    print(len(decode_parallel(a.pose_dir, a.ids, a.out, a.procs, a.threads, a.device)), "decoded")
