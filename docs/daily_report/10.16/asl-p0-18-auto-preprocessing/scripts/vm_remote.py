"""P0-18 local side of the canonical GPU pose environment (the T4 VM): fetch manifests, worker launch, result download.

The VM never receives videos from this machine: fetch_manifest() reads the local, SHA-256-verified archive and records
for every needed member its data offset / compressed size / CRC-32 / size / sha256; vm_worker.py range-fetches those
bytes from the pinned mirror copy of the same archive (same archive sha256) and must reproduce the member sha256.

    python -I vm_remote.py manifest --zip Z --url U --archive-sha256 H --videos LIST.txt --out MANIFEST.json
    python -I vm_remote.py start --root p018/test_run --manifest MANIFEST.json
    python -I vm_remote.py status --root p018/test_run
    python -I vm_remote.py download --root p018/test_run --out DIR       (after DONE; npz sha256 checked vs the log)
    python -I vm_remote.py official-start --root R --ids IDS.txt --index CROP_INDEX.tsv     (vm_official.py)
    python -I vm_remote.py official-download --root R --out DIR          (after OFFICIAL_DONE; pkl sha256 checked)
"""
import argparse, hashlib, json, os, struct, subprocess, sys, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pose_extract as PE  # noqa: E402

VM = ["baobao-training-t4", "--project", "superinbox-1719557621235", "--zone", "asia-east1-a"]
PY = "~/miniconda3/envs/p018-pose/bin/python"
REMOTE_SCRIPTS = "~/p018/repo/asl-p0-18-auto-preprocessing/scripts"
# canonical DECODER environment (T4, conda env "unisign"; the same file P0-14 used as ~/p014/env.sh) and sharding
DECODE_ENV = "~/p018/decode_env.sh"
DECODE_PROCS, DECODE_THREADS = 2, 2


def _retry(args):
    for k in range(5):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(15 * (k + 1))
    raise RuntimeError(f"{args[:3]} failed: {r.stderr[-500:]}")


def ssh(cmd):
    return _retry(["gcloud", "compute", "ssh", VM[0], *VM[1:], "--command", cmd])


def scp_to(srcs, dst):
    return _retry(["gcloud", "compute", "scp", *srcs, f"{VM[0]}:{dst}", *VM[1:]])


def scp_from(src, dst, recurse=False):
    return _retry(["gcloud", "compute", "scp", *(["--recurse"] if recurse else []), f"{VM[0]}:{src}", dst, *VM[1:]])


def fetch_manifest(zip_path, videos, url, archive_sha256):
    zf = zipfile.ZipFile(zip_path); idx = PE.zip_video_index(zf); out = {}
    with open(zip_path, "rb") as raw:
        for v in sorted(videos):
            zi = zf.getinfo(idx[v])
            raw.seek(zi.header_offset); h = raw.read(30)
            assert h[:4] == b"PK\x03\x04", v
            nlen, elen = struct.unpack("<HH", h[26:30])
            with zf.open(zi) as f:                         # zipfile verifies the CRC on a full read
                sha = hashlib.sha256()
                for b in iter(lambda: f.read(1 << 22), b""):
                    sha.update(b)
            out[v] = {"member": zi.filename, "data_offset": zi.header_offset + 30 + nlen + elen,
                      "csize": zi.compress_size, "method": zi.compress_type, "crc32": zi.CRC, "size": zi.file_size,
                      "sha256": sha.hexdigest()}
    return {"url": url, "archive_sha256": archive_sha256, "videos": out}


def start(root, manifest):
    ssh(f"mkdir -p ~/{root}")
    scp_to([manifest], f"{root}/manifest.json")
    # no '&&' before '&': a backgrounded list would keep ssh's stdout open until the worker exits
    return ssh(f"cd ~; setsid nohup {PY} -I {REMOTE_SCRIPTS}/vm_worker.py ~/{root} ~/{root}/manifest.json "
        f"> ~/{root}/worker.log 2>&1 < /dev/null & sleep 5; pgrep -f 'vm_worke[r].py /home/[^ ]*/{root} ' >/dev/null && echo started")


def wait(root, flag, poll=120, say=print):
    """Block until ROOT/<flag> exists on the VM; fail if the remote process died without writing it."""
    while True:
        r = ssh(f"cd ~/{root}; test -f {flag} && echo DONE || (pgrep -f 'vm_(worke[r]|officia[l]).py /home/[^ ]*/{root} ' >/dev/null "
                f"&& echo RUN || echo DEAD)").split()[-1]
        if r == "DONE":
            return
        if r == "DEAD":
            raise RuntimeError(f"remote job under {root} stopped without {flag}; see its log")
        say(status(root)); time.sleep(poll)


def start_official(root, ids, index):
    ssh(f"mkdir -p ~/{root}")
    scp_to([ids], f"{root}/official_ids.txt"); scp_to([index], f"{root}/crop_index.tsv")
    return ssh(f"cd ~; setsid nohup {PY} -I {REMOTE_SCRIPTS}/vm_official.py ~/{root} ~/{root}/official_ids.txt "
               f"~/{root}/crop_index.tsv > ~/{root}/official.log 2>&1 < /dev/null & sleep 5; "
               f"pgrep -f 'vm_officia[l].py /home/[^ ]*/{root} ' >/dev/null && echo started")


def download_official(root, out):
    os.makedirs(out, exist_ok=True)
    scp_from(f"{root}/C_official/*", out)
    for f in ("official_SUMMARY.json", "official_log.jsonl", "official_env.jsonl", "official.log"):
        scp_from(f"{root}/{f}", os.path.join(out, ".."))
    S = json.load(open(os.path.join(out, "..", "official_SUMMARY.json")))
    bad = [c for c, h in S["pkl_sha256"].items() if PE.file_sha256(os.path.join(out, c + ".pkl")) != h]
    if bad:
        raise SystemExit(f"downloaded pkl sha256 mismatch: {bad}")
    return S


def status(root):
    return ssh(f"cd ~/{root}; n=$(wc -l < poses/extract_log.jsonl 2>/dev/null); f=$(grep -c error poses/*_log.jsonl "
               f"2>/dev/null | awk -F: '{{s+=$2}} END {{print s}}'); echo extracted=$n errors=$f "
               f"done=$(test -f DONE && echo yes || echo no) "
               f"running=$(pgrep -f 'vm_worke[r].py /home/[^ ]*/{root} ' >/dev/null && echo yes || echo no) "
               f"free=$(df -h --output=avail ~ | tail -1)")


def download(root, out):
    os.makedirs(out, exist_ok=True)
    scp_from(f"{root}/poses/*", out)
    scp_from(f"{root}/worker.log", out)
    S = json.load(open(os.path.join(out, "SUMMARY.json")))
    bad = [v for v, h in S["npz_sha256"].items() if PE.file_sha256(os.path.join(out, v + ".npz")) != h]
    if bad:
        raise SystemExit(f"downloaded npz sha256 mismatch: {bad}")
    return S


# ---------------------------------------------------------------- canonical decoding on the T4 (decode_parallel.py)
def decoder_env(root):
    """Decoder environment record taken now on the VM (decode_env_record.py; refuses unless CUDA is available)."""
    ssh(f"mkdir -p ~/{root} && source {DECODE_ENV} && $PY -I {REMOTE_SCRIPTS}/decode_env_record.py "
        f"~/{root}/decoder_env.json > /dev/null")
    return json.loads(ssh(f"cat ~/{root}/decoder_env.json"))


def _upload_pkls(local_dir, ids, root, name):
    import tarfile, tempfile
    tmp = tempfile.mkdtemp(prefix="p018_up_"); tgz = os.path.join(tmp, name + ".tgz")
    with open(os.path.join(tmp, "ids.txt"), "w") as f:
        f.write("\n".join(ids) + "\n")
    with tarfile.open(tgz, "w:gz") as t:
        t.add(os.path.join(tmp, "ids.txt"), arcname="ids.txt")
        for c in ids:
            t.add(os.path.join(local_dir, c + ".pkl"), arcname=f"pkl/{c}.pkl")
    ssh(f"rm -rf ~/{root}/in/{name} && mkdir -p ~/{root}/in/{name}")
    scp_to([tgz], f"{root}/in/{name}.tgz")
    n = ssh(f"cd ~/{root}/in/{name} && tar xzf ../{name}.tgz && rm ../{name}.tgz && ls pkl | wc -l").split()[-1]
    os.remove(tgz); os.remove(os.path.join(tmp, "ids.txt")); os.rmdir(tmp)
    assert int(n) == len(ids), f"upload {name}: {n} of {len(ids)} pkls"


def _start_decode(root, name):
    d = f"~/{root}/in/{name}"
    return ssh(f"mkdir -p ~/{root}/dec; setsid nohup bash -c 'source {DECODE_ENV}; $PY -I {REMOTE_SCRIPTS}/decode_parallel.py "
               f"--pose-dir {d}/pkl --ids {d}/ids.txt --out ~/{root}/dec/{name} --procs {DECODE_PROCS} "
               f"--threads {DECODE_THREADS} --device cuda > ~/{root}/dec/{name}.log 2>&1; echo $? > ~/{root}/dec/{name}.rc' "
               f"> /dev/null 2>&1 < /dev/null & echo started")


def _wait_decode(root, name, poll=60):
    while True:
        r = ssh(f"cat ~/{root}/dec/{name}.rc 2>/dev/null || echo RUN").split()[-1]
        if r != "RUN":
            if r != "0":
                raise RuntimeError(f"T4 decode {name} failed (rc {r}); see ~/{root}/dec/{name}.log")
            return
        time.sleep(poll)


def _fetch_decode(root, name, local_dir, ids, out):
    """Download predictions; every clip must be present and its pose_sha256 must equal the local pkl's sha256 (the T4
    decoded exactly the inputs built here). Then the remote input copy is deleted."""
    os.makedirs(out, exist_ok=True)
    for f in ("predictions.jsonl", "decode_config.json"):
        scp_from(f"{root}/dec/{name}/{f}", os.path.join(out, f))
    P = {j["clip_id"]: j for j in map(json.loads, open(os.path.join(out, "predictions.jsonl")))}
    assert set(P) == set(ids), f"{name}: predictions do not cover the ids"
    bad = [c for c in ids if P[c]["pose_sha256"] != PE.file_sha256(os.path.join(local_dir, c + ".pkl"))]
    if bad:
        raise RuntimeError(f"{name}: pose_sha256 mismatch for {len(bad)} clips")
    ssh(f"rm -rf ~/{root}/in/{name}")
    return P


def decode_remote(jobs, root, say=print):
    """jobs: [(name, local_pose_dir, ids, local_out)]. Each job's pkls are uploaded while the previous job decodes on the
    T4 (decode_parallel.py, DECODE_PROCS x DECODE_THREADS, cuda); predictions come back to local_out/predictions.jsonl.
    Resumable: a job whose local predictions already verify is skipped."""
    todo = []
    for name, d, ids, out in jobs:
        pf = os.path.join(out, "predictions.jsonl")
        if os.path.exists(pf):
            P = {j["clip_id"]: j for j in map(json.loads, open(pf))}
            if set(P) == set(ids):
                continue
        todo.append((name, d, ids, out))
    running = None
    for k, (name, d, ids, out) in enumerate(todo):
        say(f"upload {name} ({len(ids)} pkls)")
        _upload_pkls(d, ids, root, name)
        if running:
            _wait_decode(root, running[0]); _fetch_decode(root, *running); say(f"decoded {running[0]}")
        _start_decode(root, name); running = (name, d, ids, out)
    if running:
        _wait_decode(root, running[0]); _fetch_decode(root, *running); say(f"decoded {running[0]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["manifest", "start", "status", "download", "official-start", "official-download"])
    ap.add_argument("--zip"); ap.add_argument("--url"); ap.add_argument("--archive-sha256")
    ap.add_argument("--videos"); ap.add_argument("--out"); ap.add_argument("--root"); ap.add_argument("--manifest")
    ap.add_argument("--ids"); ap.add_argument("--index")
    a = ap.parse_args()
    if a.cmd == "manifest":
        m = fetch_manifest(a.zip, open(a.videos).read().split(), a.url, a.archive_sha256)
        json.dump(m, open(a.out, "w"), indent=1); print(len(m["videos"]), "videos")
    elif a.cmd == "start":
        print(start(a.root, a.manifest))
    elif a.cmd == "status":
        print(status(a.root))
    elif a.cmd == "official-start":
        print(start_official(a.root, a.ids, a.index))
    elif a.cmd == "official-download":
        S = download_official(a.root, a.out)
        print(json.dumps({k: v for k, v in S.items() if k != "pkl_sha256"}))
    else:
        S = download(a.root, a.out)
        print(json.dumps({k: v for k, v in S.items() if not k.endswith("sha256")}))
