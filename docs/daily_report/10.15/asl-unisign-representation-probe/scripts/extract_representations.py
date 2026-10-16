"""P0-14 step 2 (PROPOSED - NOT YET RUN): extract all three representations in ONE frozen Uni-Sign forward pass.

For each clip, from the same sampled frames (upstream rule: <=256 frames, random.sample seeded per clip with
int(sha256(clip_id)[:8], 16), identical to P0-13):

  R1 raw   [T, 207]   Uni-Sign's own normalised input: body 9 + left 21 + right 21 + face 18 keypoints x (x, y, conf)
                      after load_part_kp (crop/scale normalisation, conf threshold 0.3). This is exactly what the
                      pose branch consumes, so R1 -> R2 -> R3 is one processing chain.
  R2 Fsign [T, 1024]  pose-branch output after spatial GCN, temporal GCN (kernel 5), mean over keypoints, concat of
                      the 4 parts, + part_para. Captured as the INPUT of `pose_proj` (forward pre-hook).
                      (`pose_proj` output [T, 768] is also saved as a diagnostic only; it is a linear map of R2.)
  R3 mT5   [T, 768]   mT5-Base encoder last_hidden_state at the T pose positions (the 8 prefix-token rows
                      "Translate sign language video to English: " are dropped), as in P0-13.

Saved per clip (sharded .npz, float32): for each representation the pooled statistics
  mean[D], std[D], mad[D] (= mean |x_t - x_{t-1}|), seg4[4, D] (means of 4 equal temporal segments)
plus T, n_frames_raw, sampled flag. Full sequences (float16) are additionally saved for --save-seq-roles
(default: test_clean only) for later attentive-probe / fusion work.

Inputs: pose PKLs either from an extracted directory (--pose-dir) or streamed from the concatenated official zip
(--zip; `cat how2sign_pose_format.zip.0{0,1,2,3} > how2sign_pose_format.zip`), so the 15.9 GB of PKLs never has to be
unpacked. --zip also accepts the four parts comma-separated (zip.00,zip.01,zip.02,zip.03); they are then read as
one virtual concatenation, so the joined 8.5 GB copy is never written to disk (identical bytes, no extra space).

Usage:
  python -I extract_representations.py --unisign-repo REPO --mt5 MT5_DIR --ckpt how2sign_pose_only_slt.pth \
      --manifest splits/manifest.csv --roles probe_train,test_clean --zip how2sign_pose_format.zip \
      --out features/ [--device cuda|cpu] [--dtype fp32] [--limit N] [--decode-check N]
"""
import argparse, csv, hashlib, io, json, os, pickle, random, sys, tempfile, time, zipfile

import numpy as np
import torch

ap = argparse.ArgumentParser()
ap.add_argument("--unisign-repo", required=True)
ap.add_argument("--mt5", required=True)
ap.add_argument("--ckpt", required=True)
ap.add_argument("--manifest", required=True)
ap.add_argument("--roles", default="probe_train,test_clean")
ap.add_argument("--pose-dir", default=None)
ap.add_argument("--zip", default=None)
ap.add_argument("--out", required=True)
ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
ap.add_argument("--dtype", default="fp32", choices=["fp32", "fp16"])  # fp32 is the default for parity with P0-13
ap.add_argument("--shard-size", type=int, default=1000)
ap.add_argument("--save-seq-roles", default="test_clean")
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--decode-check", type=int, default=0, help="also beam-decode the first N clips (faithfulness check)")
ap.add_argument("--no-deterministic", action="store_true", help="leave cuDNN autotuning on (default: deterministic kernels)")
a = ap.parse_args()
if not a.no_deterministic:
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
assert bool(a.pose_dir) != bool(a.zip), "give exactly one of --pose-dir / --zip"

sys.path.insert(0, a.unisign_repo)
import config  # noqa: E402
config.mt5_path = a.mt5
import utils as U  # noqa: E402
from models import Uni_Sign  # noqa: E402
from datasets import S2T_Dataset  # noqa: E402

U.set_seed(42)
args = argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([])
args.dataset, args.rgb_support, args.seed = "How2Sign", False, 42
model = Uni_Sign(args=args)
for p in model.parameters():
    p.data = p.data.to(torch.float32)
ret = model.load_state_dict(torch.load(a.ckpt, map_location="cpu")["model"], strict=True)
assert not ret.missing_keys and not ret.unexpected_keys
model.eval().to(a.device)
if a.dtype == "fp16":
    model.half()
for p in model.parameters():
    p.requires_grad_(False)

captured = {}
model.pose_proj.register_forward_pre_hook(lambda m, inp: captured.__setitem__("fsign", inp[0].detach()))

ds = S2T_Dataset.__new__(S2T_Dataset)
ds.args, ds.rgb_support, ds.max_length, ds.phase = args, False, args.max_length, "test"

class ConcatParts(io.RawIOBase):
    """Read-only seekable view of several files as one byte stream (the split official archive, without `cat`)."""
    def __init__(self, paths):
        self.fs = [open(p, "rb") for p in paths]
        self.sizes = [os.path.getsize(p) for p in paths]
        self.starts = np.cumsum([0] + self.sizes[:-1]).tolist()
        self.total, self.pos = sum(self.sizes), 0
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.total + off
        return self.pos
    def readinto(self, b):
        n, got = len(b), 0
        while got < n and self.pos < self.total:
            i = max(j for j, st in enumerate(self.starts) if st <= self.pos)
            f = self.fs[i]; f.seek(self.pos - self.starts[i])
            chunk = f.read(min(n - got, self.sizes[i] - (self.pos - self.starts[i])))
            b[got:got + len(chunk)] = chunk; got += len(chunk); self.pos += len(chunk)
        return got

zip_parts = a.zip.split(",") if a.zip else []
zf = zipfile.ZipFile(ConcatParts(zip_parts) if len(zip_parts) > 1 else a.zip) if a.zip else None
zip_names = {}
if zf:
    for n in zf.namelist():
        if n.endswith(".pkl"):
            zip_names[os.path.basename(n)[:-4]] = n

tmp_pose_dir = tempfile.mkdtemp(prefix="p014_pose_")

def upstream_kps(cid):
    """Run the unchanged upstream S2T_Dataset.load_pose on one clip (from the zip via a temp file, or a directory)."""
    if zf:
        path = os.path.join(tmp_pose_dir, cid + ".pkl")
        with open(path, "wb") as f:
            f.write(zf.read(zip_names[cid]))
        ds.pose_dir = tmp_pose_dir
    else:
        path = os.path.join(a.pose_dir, cid + ".pkl")
        ds.pose_dir = a.pose_dir
    blob = open(path, "rb").read()
    obj = pickle.loads(blob)
    n_raw = int(obj["end"] - obj["start"]) if "start" in obj else len(obj["scores"])
    kps, _ = ds.load_pose(cid + ".mp4")
    # upstream returns float64 here under numpy 1.x (float32 under the Mac numpy 2.x env); upstream eval casts inputs to
    # the model dtype, so cast explicitly -> identical fp32 inputs on every machine
    kps = {k: v.float() if torch.is_tensor(v) and v.is_floating_point() else v for k, v in kps.items()}
    if zf:
        os.remove(path)
    return kps, n_raw, hashlib.sha256(blob).hexdigest()

def to_np(t):
    # torch 2.1 + numpy 2.x in the unisign-cpu-arm64 env: Tensor.numpy() is broken (same workaround as P0-13)
    return np.asarray(t.detach().float().cpu().tolist(), dtype=np.float32)

def pool(x):  # x: [T, D] float32 numpy
    T = x.shape[0]
    mad = np.abs(np.diff(x, axis=0)).mean(0) if T > 1 else np.zeros(x.shape[1], np.float32)
    segs = np.array_split(np.arange(T), 4)
    seg4 = np.stack([x[s].mean(0) if len(s) else x.mean(0) for s in segs])
    return {"mean": x.mean(0), "std": x.std(0), "mad": mad, "seg4": seg4}

rows = [r for r in csv.DictReader(open(a.manifest)) if r["role"] in a.roles.split(",")]
if a.limit:
    rows = rows[: a.limit]
seq_roles = set(a.save_seq_roles.split(",")) if a.save_seq_roles else set()
os.makedirs(a.out, exist_ok=True)
os.makedirs(os.path.join(a.out, "seq"), exist_ok=True)
log = open(os.path.join(a.out, "_extract_log.jsonl"), "a")
done = set()
for fn in os.listdir(a.out):
    if fn.startswith("shard_") and fn.endswith(".json"):
        done |= set(json.load(open(os.path.join(a.out, fn)))["clip_ids"])

buf, shard_i, t0 = [], len([f for f in os.listdir(a.out) if f.startswith("shard_") and f.endswith(".npz")]), time.time()

def flush():
    global buf, shard_i
    if not buf:
        return
    out = {}
    for rep in ("raw", "fsign", "mt5"):
        for stat in ("mean", "std", "mad", "seg4"):
            out[f"{rep}_{stat}"] = np.stack([b[rep][stat] for b in buf]).astype(np.float32)
    out["T"] = np.array([b["T"] for b in buf]); out["n_frames_raw"] = np.array([b["n_raw"] for b in buf])
    np.savez(os.path.join(a.out, f"shard_{shard_i:04d}.npz"), **out)
    json.dump({"clip_ids": [b["cid"] for b in buf], "records": [b["rec"] for b in buf],
               "arrays": {k: list(v.shape) for k, v in out.items()}},
              open(os.path.join(a.out, f"shard_{shard_i:04d}.json"), "w"))
    shard_i += 1
    buf = []

decoded = []
for n, r in enumerate(rows):
    cid = r["clip_id"]
    if cid in done:
        continue
    seed = int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    kps, n_raw, pose_sha = upstream_kps(cid)
    src, _ = ds.collate_fn([(cid, kps, "", "", {})])
    src = {k: (v.to(a.device).half() if a.dtype == "fp16" and v.is_floating_point() else v.to(a.device))
           if torch.is_tensor(v) else v for k, v in src.items()}
    raw = torch.cat([kps[p] for p in ("body", "left", "right", "face_all")], dim=1)  # [T, 69, 3]
    raw = to_np(raw.reshape(raw.shape[0], -1))                                        # [T, 207]
    with torch.no_grad():
        out = model(src, {"gt_sentence": [""]})
        emb, mask = out["inputs_embeds"], out["attention_mask"]
        P = emb.shape[1] - src["attention_mask"].shape[1]
        enc = model.mt5_model.encoder(inputs_embeds=emb, attention_mask=mask).last_hidden_state
        if n < a.decode_check:
            ids = model.generate(out, max_new_tokens=100, num_beams=4)
            decoded.append({"clip_id": cid, "pred": model.mt5_tokenizer.batch_decode(ids, skip_special_tokens=True)[0]})
    fs = to_np(captured["fsign"][0])
    m5 = to_np(enc[0, P:])
    T = raw.shape[0]
    assert fs.shape == (T, 1024) and m5.shape == (T, 768), (cid, fs.shape, m5.shape, T)
    assert np.isfinite(fs).all() and np.isfinite(m5).all() and np.isfinite(raw).all(), cid
    buf.append({"cid": cid, "T": T, "n_raw": n_raw, "raw": pool(raw), "fsign": pool(fs), "mt5": pool(m5),
                "rec": {"clip_id": cid, "split": r["h2s_split"], "role": r["role"], "source_video_id": r["video_id"],
                        "T": T, "n_frames_raw": n_raw, "sampled": bool(n_raw > args.max_length), "pose_sha256": pose_sha,
                        "pose_source": ("zip:" + zip_names[cid]) if zf else ("dir:" + a.pose_dir),
                        "dims": {"raw": int(raw.shape[1]), "fsign": int(fs.shape[1]), "mt5": int(m5.shape[1])}}})
    if r["role"] in seq_roles:
        np.savez(os.path.join(a.out, "seq", cid + ".npz"), raw=raw.astype(np.float16), fsign=fs.astype(np.float16),
                 mt5=m5.astype(np.float16))
    log.write(json.dumps({"id": cid, "role": r["role"], "T": T, "n_frames_raw": n_raw, "sampled": n_raw > args.max_length}) + "\n")
    if len(buf) >= a.shard_size:
        flush()
    if n % 500 == 0:
        print(f"{n}/{len(rows)} {cid} T={T} {time.time() - t0:.0f}s", flush=True)
flush()
if decoded:
    json.dump(decoded, open(os.path.join(a.out, "decode_check.json"), "w"), indent=1)
import platform, subprocess, transformers  # noqa: E402
json.dump({"device": a.device, "dtype": a.dtype, "cudnn_deterministic": not a.no_deterministic, "zip_parts": zip_parts,
           "gpu": torch.cuda.get_device_name(0) if a.device.startswith("cuda") else None, "python": platform.python_version(), "torch": torch.__version__,
           "transformers": transformers.__version__, "numpy": np.__version__, "ckpt": a.ckpt, "mt5": a.mt5,
           "unisign_commit": subprocess.run(["git", "-C", a.unisign_repo, "rev-parse", "HEAD"],
                                            capture_output=True, text=True).stdout.strip(),
           "n_rows": len(rows), "seconds": time.time() - t0}, open(os.path.join(a.out, "_run_meta.json"), "w"), indent=1)
print("done", len(rows), f"{time.time() - t0:.0f}s")
