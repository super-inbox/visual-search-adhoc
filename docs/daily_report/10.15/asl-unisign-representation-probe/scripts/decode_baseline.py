"""P0-14 Stage 4: Uni-Sign's own translation of every test_clean clip (decoder baseline D). No training.

Same frozen checkpoint, same upstream S2T_Dataset.load_pose, same per-clip frame sampling seed
(random.seed(int(sha256(clip_id)[:8], 16)), <= 256 frames) and the same fp32 precision as extract_representations.py,
so the decoded text comes from exactly the frames the probes see.

Decoding = upstream fine_tuning.py evaluate(): model.generate(out, max_new_tokens=100, num_beams=4) (HF beam search,
no sampling, length_penalty / early_stopping from the mt5-base generation_config), batch size 1 (no padding effects).
Deterministic: U.set_seed(42), cuDNN deterministic, no sampling anywhere.

Output: <out>/predictions.jsonl (clip_id, pred, T, n_frames_raw, pose_sha256), <out>/decode_config.json.
Resumable (skips clip_ids already in predictions.jsonl).
Usage: python -I decode_baseline.py --unisign-repo REPO --mt5 MT5 --ckpt CKPT --manifest splits/manifest.csv \
           --roles test_clean --zip zip.00,zip.01,zip.02,zip.03 --out decode/ [--device cuda] [--limit N]
"""
import argparse, csv, hashlib, io, json, os, pickle, random, re, sys, tempfile, time, zipfile

import numpy as np
import torch

ap = argparse.ArgumentParser()
ap.add_argument("--unisign-repo", required=True)
ap.add_argument("--mt5", required=True)
ap.add_argument("--ckpt", required=True)
ap.add_argument("--manifest", required=True)
ap.add_argument("--roles", default="test_clean")
ap.add_argument("--zip", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
ap.add_argument("--max-new-tokens", type=int, default=100)
ap.add_argument("--num-beams", type=int, default=4)
ap.add_argument("--limit", type=int, default=0)
a = ap.parse_args()
torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False

# the same split-archive reader as extract_representations.py (copied verbatim, no shared import under -I)
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract_representations.py")).read()
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
parts = a.zip.split(",")
zf = zipfile.ZipFile(ConcatParts(parts) if len(parts) > 1 else a.zip)
zip_names = {os.path.basename(n)[:-4]: n for n in zf.namelist() if n.endswith(".pkl")}
tmp = tempfile.mkdtemp(prefix="p014_dec_")
ds.pose_dir = tmp

rows = [r for r in csv.DictReader(open(a.manifest)) if r["role"] in a.roles.split(",")]
if a.limit:
    rows = rows[: a.limit]
os.makedirs(a.out, exist_ok=True)
pf = os.path.join(a.out, "predictions.jsonl")
done = {json.loads(l)["clip_id"] for l in open(pf)} if os.path.exists(pf) else set()
fo = open(pf, "a")
t0, n_new = time.time(), 0
for n, r in enumerate(rows):
    cid = r["clip_id"]
    if cid in done:
        continue
    blob = zf.read(zip_names[cid])
    path = os.path.join(tmp, cid + ".pkl")
    open(path, "wb").write(blob)
    obj = pickle.loads(blob)
    n_raw = int(obj["end"] - obj["start"]) if "start" in obj else len(obj["scores"])
    random.seed(int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16))
    kps, _ = ds.load_pose(cid + ".mp4")
    kps = {k: v.float() if torch.is_tensor(v) and v.is_floating_point() else v for k, v in kps.items()}  # as extraction
    os.remove(path)
    src, _ = ds.collate_fn([(cid, kps, "", "", {})])
    src = {k: v.to(a.device) if torch.is_tensor(v) else v for k, v in src.items()}
    with torch.no_grad():
        out = model(src, {"gt_sentence": [""]})
        ids = model.generate(out, max_new_tokens=a.max_new_tokens, num_beams=a.num_beams)
    pred = model.mt5_tokenizer.batch_decode(ids, skip_special_tokens=True)[0]
    T = int(kps["body"].shape[0])
    fo.write(json.dumps({"clip_id": cid, "pred": pred, "T": T, "n_frames_raw": n_raw,
                         "n_tokens": int(ids.shape[1]), "pose_sha256": hashlib.sha256(blob).hexdigest()}) + "\n")
    fo.flush(); n_new += 1
    if n % 100 == 0:
        print(f"{n}/{len(rows)} {cid} T={T} {time.time() - t0:.0f}s :: {pred[:80]}", flush=True)
fo.close()
import platform, subprocess, transformers  # noqa: E402
gen_cfg = model.mt5_model.generation_config.to_dict()
json.dump({"decoding": {"call": "Uni_Sign.generate -> mt5_model.generate(inputs_embeds, attention_mask, "
                                "max_new_tokens, num_beams)", "max_new_tokens": a.max_new_tokens,
                        "num_beams": a.num_beams, "do_sample": False, "batch_size": 1,
                        "hf_generation_config": gen_cfg},
           "frames": "upstream load_pose, <=256 frames, random.seed(int(sha256(clip_id)[:8],16)) per clip",
           "precision": "fp32", "cudnn_deterministic": True, "global_seed": 42, "device": a.device,
           "gpu": torch.cuda.get_device_name(0) if a.device.startswith("cuda") else None,
           "python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__,
           "ckpt": a.ckpt, "mt5": a.mt5, "zip_parts": parts, "roles": a.roles, "n_rows": len(rows),
           "n_decoded_this_run": n_new, "seconds_this_run": time.time() - t0,
           "unisign_commit": subprocess.run(["git", "-C", a.unisign_repo, "rev-parse", "HEAD"],
                                            capture_output=True, text=True).stdout.strip()},
          open(os.path.join(a.out, "decode_config.json"), "w"), indent=1)
print("done", n_new, f"{time.time() - t0:.0f}s")
