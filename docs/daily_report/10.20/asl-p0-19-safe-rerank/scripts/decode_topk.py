"""P0-19 Stage 0: Uni-Sign top-k beam candidates for every test_clean clip (official poses). No training.

Identical to P0-14 decode_baseline.py up to the decoder call: same frozen checkpoint, upstream S2T_Dataset.load_pose,
per-clip frame sampling seed random.seed(int(sha256(clip_id)[:8], 16)) (<= 256 frames), fp32, batch size 1,
U.set_seed(42), cuDNN deterministic. One Uni-Sign forward per clip, then for each k in --ks:

  mt5_model.generate(inputs_embeds, attention_mask, max_new_tokens=100, num_beams=k, num_return_sequences=k,
                     output_scores=True, return_dict_in_generate=True)

i.e. upstream Uni_Sign.generate with num_return_sequences=k (HF returns the k finished beams best-first). With
k = 4 the first returned beam must reproduce the stored P0-14 baseline (gate G1, checked in stage0_analyze.py).

Holdout protection: every clip id passes the P0-16 guard, an open() tripwire then refuses any val / holdout path,
and only official-archive members under test-pose-rtmpose-192/ may be read.

Output: <out>/candidates.jsonl, one line per clip:
  {clip_id, T, n_frames_raw, pose_sha256, sec_forward,
   k4: {sec, cands: [{rank, text, ids, n_tokens, seq_score}]}, k8: {...}}
<out>/run_meta.json (environment, hashes, timing). Resumable: clip_ids already in candidates.jsonl are skipped.

Usage (VM):  python -I decode_topk.py --unisign-repo REPO --mt5 MT5 --ckpt CKPT --zip z.00,z.01,z.02,z.03 \
                 --out stage0/main [--limit N] [--device cuda]
Usage (Mac smoke, CPU, local pilot poses):  ... --pose-dir ~/Desktop/curify/p014-work/poses_pilot --ids FILE
"""
import argparse, csv, hashlib, io, json, os, pickle, random, re, shutil, sys, tempfile, time, zipfile  # noqa: F401

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p019_common import ARCHIVE_TEST_DIR, CONFIG, EXP, P014, guard_and_trip, load_config, sha256, trim_ids  # noqa

ap = argparse.ArgumentParser()
ap.add_argument("--unisign-repo", required=True)
ap.add_argument("--mt5", required=True)
ap.add_argument("--ckpt", required=True)
ap.add_argument("--zip", default="")
ap.add_argument("--pose-dir", default="")
ap.add_argument("--ids", default="", help="optional file of clip ids (subset of test_clean, manifest order kept)")
ap.add_argument("--out", required=True)
ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
ap.add_argument("--limit", type=int, default=0)
a = ap.parse_args()
assert bool(a.zip) != bool(a.pose_dir), "give exactly one of --zip / --pose-dir"
cfg = load_config()["stage0"]
KS, MAX_NEW, ROLE = cfg["ks"], cfg["max_new_tokens"], cfg["role"]
torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False

manifest = os.path.join(P014, "splits", "manifest.csv")
rows = [r for r in csv.DictReader(open(manifest)) if r["role"] == ROLE]
if a.ids:
    keep = set(open(a.ids).read().split())
    rows = [r for r in rows if r["clip_id"] in keep]
if a.limit:
    rows = rows[: a.limit]
ids_all = [r["clip_id"] for r in rows]
guard_meta = guard_and_trip(ids_all)                       # G3: raises on any sealed id; tripwire from here on

# the same split-archive reader as P0-14 extract_representations.py (copied verbatim, no shared import under -I)
_src = open(os.path.join(P014, "scripts", "extract_representations.py")).read()
exec(re.search(r"class ConcatParts.*?return got\n", _src, re.S).group(0))

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
for p in model.parameters():
    p.requires_grad_(False)

ds = S2T_Dataset.__new__(S2T_Dataset)
ds.args, ds.rgb_support, ds.max_length, ds.phase = args, False, args.max_length, "test"
zf, zip_names = None, {}
if a.zip:
    parts = a.zip.split(",")
    zf = zipfile.ZipFile(ConcatParts(parts) if len(parts) > 1 else a.zip)  # noqa: F821 (exec'd above)
    zip_names = {os.path.basename(n)[:-4]: n for n in zf.namelist()
                 if n.endswith(".pkl") and n.startswith(ARCHIVE_TEST_DIR)}
tmp = tempfile.mkdtemp(prefix="p019_s0_")
ds.pose_dir = tmp


def read_pose(cid):
    if zf is not None:
        name = zip_names[cid]
        assert name.startswith(ARCHIVE_TEST_DIR), name
        return zf.read(name)
    return open(os.path.join(a.pose_dir, cid + ".pkl"), "rb").read()


os.makedirs(a.out, exist_ok=True)
pf = os.path.join(a.out, "candidates.jsonl")
done = {json.loads(l)["clip_id"] for l in open(pf)} if os.path.exists(pf) else set()
fo = open(pf, "a")
t0, n_new = time.time(), 0
for n, r in enumerate(rows):
    cid = r["clip_id"]
    if cid in done:
        continue
    blob = read_pose(cid)
    path = os.path.join(tmp, cid + ".pkl")
    open(path, "wb").write(blob)
    obj = pickle.loads(blob)
    n_raw = int(obj["end"] - obj["start"]) if "start" in obj else len(obj["scores"])
    random.seed(int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16))
    kps, _ = ds.load_pose(cid + ".mp4")
    kps = {k: v.float() if torch.is_tensor(v) and v.is_floating_point() else v for k, v in kps.items()}
    os.remove(path)
    src, _ = ds.collate_fn([(cid, kps, "", "", {})])
    src = {k: v.to(a.device) if torch.is_tensor(v) else v for k, v in src.items()}
    rec = {"clip_id": cid, "T": int(kps["body"].shape[0]), "n_frames_raw": n_raw,
           "pose_sha256": hashlib.sha256(blob).hexdigest()}
    ts = time.time()
    with torch.no_grad():
        out = model(src, {"gt_sentence": [""]})
    rec["sec_forward"] = round(time.time() - ts, 4)
    for k in KS:
        ts = time.time()
        with torch.no_grad():
            g = model.mt5_model.generate(inputs_embeds=out["inputs_embeds"], attention_mask=out["attention_mask"],
                                         max_new_tokens=MAX_NEW, num_beams=k, num_return_sequences=k,
                                         output_scores=True, return_dict_in_generate=True)
        seqs, scores = g.sequences.cpu().tolist(), g.sequences_scores.cpu().tolist()
        cands = []
        for j, (s, sc) in enumerate(zip(seqs, scores)):
            ids = trim_ids(s)
            cands.append({"rank": j, "text": model.mt5_tokenizer.decode(ids, skip_special_tokens=True),
                          "ids": ids, "n_tokens": len(ids), "seq_score": sc})
        rec[f"k{k}"] = {"sec": round(time.time() - ts, 4), "cands": cands}
    fo.write(json.dumps(rec) + "\n")
    fo.flush(); n_new += 1
    if n % 100 == 0:
        print(f"{n}/{len(rows)} {cid} T={rec['T']} {time.time() - t0:.0f}s :: {rec[f'k{KS[0]}']['cands'][0]['text'][:70]}",
              flush=True)
fo.close()
shutil.rmtree(tmp, ignore_errors=True)

import platform, subprocess, transformers  # noqa: E402
json.dump({"stage": "P0-19 Stage 0 decode_topk", "role": ROLE, "ks": KS, "max_new_tokens": MAX_NEW,
           "generate": "mt5_model.generate(inputs_embeds, attention_mask, max_new_tokens, num_beams=k, "
                       "num_return_sequences=k, output_scores=True, return_dict_in_generate=True)",
           "hf_generation_config": model.mt5_model.generation_config.to_dict(),
           "frames": "upstream load_pose, <=256 frames, random.seed(int(sha256(clip_id)[:8],16)) per clip",
           "precision": "fp32", "cudnn_deterministic": True, "global_seed": 42, "batch_size": 1,
           "device": a.device, "gpu": torch.cuda.get_device_name(0) if a.device.startswith("cuda") else None,
           "python": platform.python_version(), "torch": torch.__version__,
           "transformers": transformers.__version__, "numpy": np.__version__,
           "ckpt": a.ckpt, "ckpt_sha256": sha256(a.ckpt), "mt5": a.mt5,
           "pose_source": a.zip or a.pose_dir, "archive_dir_allowed": ARCHIVE_TEST_DIR,
           "config_sha256": sha256(CONFIG), "script_sha256": sha256(os.path.abspath(__file__)),
           "manifest_sha256": sha256(manifest), "n_rows": len(rows), "n_decoded_this_run": n_new,
           "seconds_this_run": time.time() - t0, **guard_meta,
           "unisign_commit": subprocess.run(["git", "-C", a.unisign_repo, "rev-parse", "HEAD"],
                                            capture_output=True, text=True).stdout.strip()},
          open(os.path.join(a.out, "run_meta.json"), "w"), indent=1)
print("done", n_new, f"{time.time() - t0:.0f}s")
