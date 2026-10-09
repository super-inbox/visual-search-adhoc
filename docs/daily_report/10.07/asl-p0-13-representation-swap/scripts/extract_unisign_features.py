"""P0-13: frozen Uni-Sign feature extraction (no training, no gradient).

Uses the pinned upstream code path unchanged:
  pose pkl -> S2T_Dataset.load_pose (max_length 256, upstream random.sample, seeded per clip)
           -> Base_Dataset.collate_fn -> Uni_Sign pose branch (proj_linear, spatial/temporal
              ST-GCN per part, part_para, pose_proj) -> [prefix tokens ; pose tokens]
           -> mT5-Base encoder (frozen, eval, fp32; bf16->fp32 deviation measured: mean per-frame cos 0.9994)
Saved per clip (float16 .npz):
  enc      [T, 768] mT5 encoder last_hidden_state at the T pose positions (prefix positions dropped)
  pose_emb [T, 768] pose_proj output (input to the mT5 encoder) - diagnostics only
  frame_idx[T]      pose-frame indices that were sampled
Usage: python -I extract_unisign_features.py UNISIGN_REPO MT5_DIR CKPT POSE_DIR IDS_TXT OUT_DIR
"""
import argparse, hashlib, os, random, sys, time, json
import numpy as np
import torch

repo, mt5_dir, ckpt, pose_dir, ids_txt, out_dir = sys.argv[1:7]
sys.path.insert(0, repo)
import config  # noqa: E402
config.mt5_path = mt5_dir
import utils as U  # noqa: E402
from models import Uni_Sign  # noqa: E402
from datasets import S2T_Dataset  # noqa: E402

torch.set_num_threads(int(os.environ.get("P013_THREADS", "8")))
U.set_seed(42)
args = argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([])
args.dataset, args.rgb_support, args.seed = "How2Sign", False, 42

model = Uni_Sign(args=args)
model.train()
for p in model.parameters():
    p.data = p.data.to(torch.float32)
sd = torch.load(ckpt, map_location="cpu")["model"]
ret = model.load_state_dict(sd, strict=True)
assert not ret.missing_keys and not ret.unexpected_keys
model.eval()  # fp32 (checkpoint is bf16; exact upcast). Official eval casts to bf16: see REPRESENTATION_INTERFACE.md
for p in model.parameters():
    p.requires_grad_(False)

# loader object without reading a label file: only load_pose/collate_fn are used
ds = S2T_Dataset.__new__(S2T_Dataset)
ds.args, ds.rgb_support, ds.max_length, ds.phase = args, False, args.max_length, "test"
ds.pose_dir = pose_dir

ids = [l.strip() for l in open(ids_txt) if l.strip()]
os.makedirs(out_dir, exist_ok=True)
log = open(os.path.join(out_dir, "_extract_log.jsonl"), "a")
t0 = time.time()
for n, cid in enumerate(ids):
    dst = os.path.join(out_dir, cid + ".npz")
    if os.path.exists(dst):
        continue
    seed = int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16)
    random.seed(seed)  # makes upstream random.sample (only used when > 256 frames) reproducible
    pose = __import__("pickle").load(open(os.path.join(pose_dir, cid + ".pkl"), "rb"))
    n_frames_raw = int(pose["end"] - pose["start"]) if "start" in pose else len(pose["scores"])
    kps, _ = ds.load_pose(cid + ".mp4")
    src, _ = ds.collate_fn([(cid, kps, "", "", {})])
    with torch.no_grad():
        # exact upstream forward (pose branch + prefix concat); the dummy target only feeds its unused loss
        out = model(src, {"gt_sentence": [""]})
        emb, mask = out["inputs_embeds"], out["attention_mask"]
        P = emb.shape[1] - src["attention_mask"].shape[1]
        pose_emb = emb[:, P:]
        enc = model.mt5_model.encoder(inputs_embeds=emb, attention_mask=mask).last_hidden_state
        enc_t = enc[0, P:].float()
    T = int(src["attention_mask"].sum())
    assert tuple(enc_t.shape) == (T, 768) and pose_emb.shape[1] == T, (cid, enc_t.shape, T)
    assert bool(torch.isfinite(enc_t).all())
    # torch 2.1 + numpy 2.x in this env: Tensor.numpy() is broken, so convert via lists
    to_np = lambda t: np.asarray(t.tolist(), dtype=np.float32).astype(np.float16)
    np.savez(dst, enc=to_np(enc_t), pose_emb=to_np(pose_emb[0].float()),
             n_frames_raw=n_frames_raw, T=T, prefix_len=P)
    log.write(json.dumps({"id": cid, "n_frames_raw": n_frames_raw, "T": T, "prefix_len": P,
                          "sampled": n_frames_raw > args.max_length}) + "\n")
    if n % 100 == 0:
        print(f"{n}/{len(ids)} {cid} T={T} raw={n_frames_raw} {time.time()-t0:.0f}s", flush=True)
log.close()
print("done", len(ids), f"{time.time()-t0:.0f}s")
