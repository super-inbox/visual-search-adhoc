"""P0-18: Uni-Sign translation of every pose pkl in a directory (one condition). No training.

Identical decoding to P0-14 decode_baseline.py: frozen how2sign_pose_only_slt.pth, upstream S2T_Dataset.load_pose,
<= 256 frames with random.seed(int(sha256(clip_id)[:8], 16)) per clip, fp32, model.generate(max_new_tokens=100,
num_beams=4), batch size 1, U.set_seed(42). Resumable.

Usage: python -I decode_dir.py --pose-dir DIR --out OUT_DIR [--ids FILE] [--device cpu] [--threads N]
       env: UNISIGN_REPO, MT5, CKPT
"""
import argparse, hashlib, io, json, os, pickle, random, shutil, sys, tempfile, time

import numpy as np
import torch

NUMPY1 = int(np.__version__.split(".")[0]) < 2


class _Np2Unpickler(pickle.Unpickler):
    """Load a numpy>=2 pickle under numpy 1.x: only the module path numpy._core -> numpy.core differs."""
    def find_class(self, module, name):
        if module.startswith("numpy._core"):
            module = "numpy.core" + module[len("numpy._core"):]
        return super().find_class(module, name)


ap = argparse.ArgumentParser()
ap.add_argument("--pose-dir", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--ids", default="")
ap.add_argument("--device", default="cpu")
ap.add_argument("--threads", type=int, default=0, help="torch intra-op threads (0 = torch default)")
a = ap.parse_args()
if a.threads:
    torch.set_num_threads(a.threads)
torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
REPO = os.environ.get("UNISIGN_REPO", os.path.expanduser("~/Desktop/curify/p014-work/Uni-Sign"))
MT5 = os.environ.get("MT5", os.path.expanduser(
    "~/.cache/huggingface/hub/models--google--mt5-base/snapshots/2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f"))
CKPT = os.environ.get("CKPT", os.path.expanduser("~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth"))

sys.path.insert(0, REPO)
import config  # noqa: E402
config.mt5_path = MT5
import utils as U  # noqa: E402
from models import Uni_Sign  # noqa: E402
from datasets import S2T_Dataset  # noqa: E402

U.set_seed(42)
args = argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([])
args.dataset, args.rgb_support, args.seed = "How2Sign", False, 42
model = Uni_Sign(args=args)
for p in model.parameters():
    p.data = p.data.to(torch.float32)
ret = model.load_state_dict(torch.load(CKPT, map_location="cpu")["model"], strict=True)
assert not ret.missing_keys and not ret.unexpected_keys
model.eval().to(a.device)
for p in model.parameters():
    p.requires_grad_(False)
ds = S2T_Dataset.__new__(S2T_Dataset)
ds.args, ds.rgb_support, ds.max_length, ds.phase = args, False, args.max_length, "test"
tmp = tempfile.mkdtemp(prefix="p018_dec_"); ds.pose_dir = tmp

ids = (open(a.ids).read().split() if a.ids else
       sorted(f[:-4] for f in os.listdir(a.pose_dir) if f.endswith(".pkl")))
os.makedirs(a.out, exist_ok=True)
pf = os.path.join(a.out, "predictions.jsonl")
done = {json.loads(l)["clip_id"] for l in open(pf)} if os.path.exists(pf) else set()
fo = open(pf, "a"); t0 = time.time(); n_new = 0
for n, cid in enumerate(ids):
    if cid in done:
        continue
    src_path = os.path.join(a.pose_dir, cid + ".pkl")
    blob = open(src_path, "rb").read()
    if NUMPY1 and b"numpy._core" in blob:                   # pkl written by numpy >= 2 (Mac build): same arrays
        pickle.dump(_Np2Unpickler(io.BytesIO(blob)).load(), open(os.path.join(tmp, cid + ".pkl"), "wb"))
    else:
        shutil.copyfile(src_path, os.path.join(tmp, cid + ".pkl"))
    random.seed(int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16))
    kps, _ = ds.load_pose(cid + ".mp4")                     # S2T_Dataset.load_pose(path): .mp4 -> .pkl
    kps = {k: v.float() if torch.is_tensor(v) and v.is_floating_point() else v for k, v in kps.items()}
    os.remove(os.path.join(tmp, cid + ".pkl"))
    src, _ = ds.collate_fn([(cid, kps, "", "", {})])
    src = {k: v.to(a.device) if torch.is_tensor(v) else v for k, v in src.items()}
    with torch.no_grad():
        out = model(src, {"gt_sentence": [""]})
        tok = model.generate(out, max_new_tokens=100, num_beams=4)
    pred = model.mt5_tokenizer.batch_decode(tok, skip_special_tokens=True)[0]
    n_raw = len(_Np2Unpickler(io.BytesIO(blob)).load()["scores"])
    fo.write(json.dumps({"clip_id": cid, "pred": pred, "T": int(kps["body"].shape[0]), "n_frames_raw": n_raw,
                         "n_tokens": int(tok.shape[1]), "pose_sha256": hashlib.sha256(blob).hexdigest()}) + "\n")
    fo.flush(); n_new += 1
    if n % 25 == 0:
        print(f"{n}/{len(ids)} {cid} {time.time() - t0:.0f}s", flush=True)
fo.close()
json.dump({"pose_dir": a.pose_dir, "n": len(ids), "n_decoded_this_run": n_new, "seconds_this_run": time.time() - t0,
           "device": a.device, "threads": torch.get_num_threads(), "torch": torch.__version__, "ckpt": CKPT, "decoding": "beam 4, max_new_tokens 100, fp32"},
          open(os.path.join(a.out, "decode_config.json"), "w"), indent=1)
print("DONE", n_new)
