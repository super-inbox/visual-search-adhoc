"""P0-18 canonical DECODER environment record (runs on the T4 VM inside ~/p018/decode_env.sh): versions, CUDA, Uni-Sign
commit + tracked-file content hash, checkpoint sha256, mT5 file sha256s, decoding settings. Frozen into the P0-18
config; the H18 runner requires the record taken at H18 time to equal the frozen one.

Usage: python -I decode_env_record.py OUT.json
"""
import glob, hashlib, json, os, subprocess, sys

import numpy as np
import torch
import transformers


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


REPO, MT5, CKPT = os.environ["UNISIGN_REPO"], os.environ["MT5"], os.environ["CKPT"]
files = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True, check=True).stdout.split()
content = hashlib.sha256("".join(f"{sha(os.path.join(REPO, f))}  {f}\n" for f in files if "__pycache__" not in f)
                         .encode()).hexdigest()
env = {"python": sys.version.split()[0], "torch": torch.__version__, "torch_cuda": torch.version.cuda,
       "cudnn": torch.backends.cudnn.version(), "transformers": transformers.__version__, "numpy": np.__version__,
       "cuda_available": torch.cuda.is_available(),
       "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
       "unisign_commit": subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "unisign_tracked_content_sha256": content, "checkpoint_sha256": sha(CKPT),
       "mt5_sha256": {os.path.basename(p): sha(p) for p in sorted(glob.glob(os.path.join(MT5, "*"))) if os.path.isfile(p)},
       "decoding": {"device": "cuda", "dtype": "fp32", "num_beams": 4, "max_new_tokens": 100, "batch_size": 1,
                    "set_seed": 42, "frame_sampling_seed": "int(sha256(clip_id)[:8], 16)", "max_frames": 256,
                    "cudnn_deterministic": True, "cudnn_benchmark": False}}
if not env["cuda_available"]:
    sys.exit("REFUSED: CUDA is not available for the canonical decoder")
json.dump(env, open(sys.argv[1], "w"), indent=1)
print(json.dumps(env, indent=1))
