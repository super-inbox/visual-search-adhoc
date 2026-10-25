"""P0-A candidate decode (protocol P0_PROTOCOL_FREEZE.md §1.3). No training. Local CPU, fp32 only.

Adapted from P0-19 decode_topk.py (same frozen checkpoint, upstream S2T_Dataset.load_pose, per-clip frame sampling
seed random.seed(int(sha256(clip_id)[:8], 16)) for clips > 256 frames, U.set_seed(42), batch size 1). Differences:
the inputs are the P0-12 prepared PKLs of ONE domain (A_official = D-A, B_ours_5p39 = D-B), the case set is the
frozen 45-case case_list.csv, and the decoding is the P0-A one. One Uni-Sign forward per clip feeds both:

  T     : mt5_model.generate(..., max_new_tokens=100, num_beams=4)                          (control top-1)
  beam5 : mt5_model.generate(..., max_new_tokens=100, num_beams=5, num_return_sequences=5)  (candidates)

Pool = [T] + beam5 ranks 0..4, exact-text deduplication keeping the first occurrence, truncated to <= 5 unique.
Pre-/post-deduplication counts are recorded; a pool with fewer than 5 is kept as is (pool_lt5 = true).

Reference-free: this script reads only case_list.csv, provenance/case_provenance.csv (no reference column), the
P0-12 CHECKSUMS.sha256 and the domain's pose PKLs. An open() tripwire refuses How2Sign val / holdout paths (P0-19
p019_common, gate G2) and every reference-bearing file this repo stores (inputs_128.jsonl, inspection sheet,
How2Sign test CSVs, P0-14 manifest).

Output (<out>/):
  candidates.jsonl   one line per clip, in case_list.csv order (rewritten in that order at the end of every run)
  run_meta.json      environment, hashes, per-run timing ("runs" list, one entry per invocation)
Resumable: clip ids already in candidates.jsonl are skipped; a truncated last line from a killed run is dropped.

Usage (repo root):
  /opt/anaconda3/envs/unisign-cpu-arm64/bin/python -I \
      asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/scripts/decode_candidates.py \
      --domain A_official --unisign-repo ~/Desktop/curify/p014-work/Uni-Sign \
      --mt5 ~/.cache/huggingface/hub/models--google--mt5-base/snapshots/2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f \
      --ckpt ~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth --out <dir> [--limit 5]
"""
import argparse, builtins, csv, hashlib, io, json, os, pickle, random, re, subprocess, sys, time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(EXP, "..", "..", "..", ".."))
DR = os.path.join(REPO, "docs", "daily_report")
PREP = os.path.join(DR, "10.06", "asl-p0-12-unisign-pose-gap", "artifacts", "prepared_inputs")
P019_SCRIPTS = os.path.join(DR, "10.20", "asl-p0-19-safe-rerank", "scripts")
CASE_LIST = os.path.join(EXP, "case_list.csv")
PROVENANCE = os.path.join(EXP, "provenance", "case_provenance.csv")

DOMAINS = ("A_official", "B_ours_5p39")
POSE_SUBDIR = "test-pose-rtmpose-192"
GLOBAL_SEED, MAX_NEW, T_BEAMS, CAND_BEAMS, POOL_MAX = 42, 100, 4, 5, 5
CLIP_SEC_CAP = 600                                   # protocol §1.8: abort if any single clip takes > 10 min
CKPT_SHA = "1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d"
UNISIGN_COMMIT = "eed438bcb49e30405cd6ccdfcccca330c134e830"
MT5_SNAPSHOT = "2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f"
# reference-bearing files that must never be opened by the decoder
REF_DENY = re.compile(r"(inputs_128\.jsonl|inspection_sheet\.csv|how2sign_realigned_|how2sign_test|"
                      r"asl-unisign-representation-probe[/\\]splits[/\\]manifest\.csv)", re.I)

ap = argparse.ArgumentParser()
ap.add_argument("--domain", required=True, choices=DOMAINS)
ap.add_argument("--unisign-repo", required=True)
ap.add_argument("--mt5", required=True)
ap.add_argument("--ckpt", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--limit", type=int, default=0, help="first N clips of case_list.csv (smoke / G3 subset)")
ap.add_argument("--threads", type=int, default=4, help="torch CPU threads, fixed and recorded")
a = ap.parse_args()
torch.set_num_threads(a.threads)

# ------------------------------------------------------------------ cases, inputs, holdout guard (gates G1, G2)
cases = list(csv.DictReader(open(CASE_LIST)))
if a.limit:
    cases = cases[: a.limit]
prov = {r["clip_id"]: r for r in csv.DictReader(open(PROVENANCE))}
assert not any("ref" in k.lower() or "sentence" in k.lower() for k in next(iter(prov.values()))), "reference column"
ids_all = [r["clip_id"] for r in cases]
assert len(set(ids_all)) == len(ids_all)
checks = {}
for line in open(os.path.join(PREP, "CHECKSUMS.sha256")):
    h, p = line.split(None, 1)
    checks[p.strip()] = h

sys.path.insert(0, P019_SCRIPTS)
from p019_common import guard_and_trip, sha256, trim_ids  # noqa: E402
guard_meta = guard_and_trip(ids_all)                  # raises on any sealed id; val / holdout open() tripwire from here
_trip_open = builtins.open


def _ref_tripped_open(file, *args, **kw):
    if isinstance(file, (str, bytes, os.PathLike)) and REF_DENY.search(os.fsdecode(file)):
        raise PermissionError(f"P0-A tripwire: reference-bearing file refused: {os.fsdecode(file)}")
    return _trip_open(file, *args, **kw)


builtins.open = io.open = _ref_tripped_open

pose_dir = os.path.join(PREP, a.domain, POSE_SUBDIR)
for cid in ids_all:
    rel = f"{a.domain}/{POSE_SUBDIR}/{cid}.pkl"
    assert prov[cid][f"{a.domain}_pkl"].endswith(rel), (cid, prov[cid][f"{a.domain}_pkl"])
    assert rel in checks, rel

# ------------------------------------------------------------------ model (CPU, fp32)
assert sha256(a.ckpt) == CKPT_SHA, "checkpoint sha256 mismatch"
unisign_commit = subprocess.run(["git", "-C", a.unisign_repo, "rev-parse", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
assert unisign_commit == UNISIGN_COMMIT, unisign_commit
assert os.path.basename(os.path.normpath(a.mt5)) == MT5_SNAPSHOT, a.mt5

sys.path.insert(0, a.unisign_repo)
import config  # noqa: E402
config.mt5_path = a.mt5
import utils as U  # noqa: E402
from models import Uni_Sign  # noqa: E402
from datasets import S2T_Dataset  # noqa: E402

DEVICE = "cpu"
U.set_seed(GLOBAL_SEED)
args = argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([])
args.dataset, args.rgb_support, args.seed = "How2Sign", False, GLOBAL_SEED
model = Uni_Sign(args=args)
for p in model.parameters():
    p.data = p.data.to(torch.float32)
ret = model.load_state_dict(torch.load(a.ckpt, map_location="cpu")["model"], strict=True)
assert not ret.missing_keys and not ret.unexpected_keys
model.eval().to(DEVICE)
for p in model.parameters():
    p.requires_grad_(False)
assert all(p.dtype == torch.float32 for p in model.parameters())
mt5 = model.mt5_model
LENGTH_PENALTY = mt5.generation_config.length_penalty

ds = S2T_Dataset.__new__(S2T_Dataset)
ds.args, ds.rgb_support, ds.max_length, ds.phase = args, False, args.max_length, "test"
ds.pose_dir = pose_dir


def run_generate(out, k):
    g = mt5.generate(inputs_embeds=out["inputs_embeds"], attention_mask=out["attention_mask"],
                     max_new_tokens=MAX_NEW, num_beams=k, num_return_sequences=k if k == CAND_BEAMS else 1,
                     output_scores=True, return_dict_in_generate=True)
    tr = mt5.compute_transition_scores(g.sequences, g.scores, g.beam_indices, normalize_logits=False)
    seqs, scores = g.sequences.cpu().tolist(), g.sequences_scores.cpu().tolist()
    cands = []
    for j, (s, sc) in enumerate(zip(seqs, scores)):
        ids = trim_ids(s)
        n_gen = len(ids) - 1                          # generated tokens (excludes decoder start), incl. eos
        cands.append({"rank": j, "text": model.mt5_tokenizer.decode(ids, skip_special_tokens=True), "ids": ids, "n_tokens": len(ids), "seq_score": sc,
                      "sum_logprob": float(tr[j, :n_gen].sum()), "n_gen_tokens": n_gen})
    return cands


def build_pool(t, beam5):
    pre = [dict(c, source="T_beam4") for c in t] + [dict(c, source="beam5") for c in beam5]
    b5 = {}
    for c in beam5:
        b5.setdefault(c["text"], c)
    seen, pool = set(), []
    for c in pre:
        if c["text"] in seen:
            continue
        seen.add(c["text"])
        m = b5.get(c["text"])
        pool.append({"pos": len(pool), "text": c["text"], "ids": c["ids"], "n_tokens": c["n_tokens"],
                     "source": c["source"], "source_rank": c["rank"], "source_seq_score": c["seq_score"],
                     "source_sum_logprob": c["sum_logprob"],
                     "beam5_rank": m["rank"] if m else None, "beam5_seq_score": m["seq_score"] if m else None})
    n_unique = len(pool)
    return pool[:POOL_MAX], len(pre), n_unique


# ------------------------------------------------------------------ decode (resumable)
os.makedirs(a.out, exist_ok=True)
pf = os.path.join(a.out, "candidates.jsonl")
recs = {}
if os.path.exists(pf):
    for line in open(pf):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:                  # truncated last line from a killed run
            continue
        assert r["domain"] == a.domain, f"{pf} holds domain {r['domain']}"
        recs[r["clip_id"]] = r
fo = open(pf, "a")
t0, n_new = time.time(), 0
for n, c in enumerate(cases):
    cid = c["clip_id"]
    if cid in recs:
        continue
    pkl = os.path.join(pose_dir, cid + ".pkl")
    blob = open(pkl, "rb").read()
    pose_sha = hashlib.sha256(blob).hexdigest()
    assert pose_sha == checks[f"{a.domain}/{POSE_SUBDIR}/{cid}.pkl"], f"G1 input integrity: {cid}"
    ts_clip = time.time()
    clip_seed = int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16)
    random.seed(clip_seed)
    assert random.getstate() == random.Random(clip_seed).getstate()   # so fidx below = upstream's actual draw
    kps, _ = ds.load_pose(cid + ".mp4")
    kps = {k: v.float() if torch.is_tensor(v) and v.is_floating_point() else v for k, v in kps.items()}
    # frame-dropping fingerprint: the indices the frozen seed implies (independent RNG, same rule as upstream
    # load_pose) and a hash of the keypoint tensors the model actually received
    pose = pickle.loads(blob)
    start, dur = (pose["start"], pose["end"] - pose["start"]) if "start" in pose else (0, len(pose["scores"]))
    fidx = [start + i for i in (sorted(random.Random(clip_seed).sample(range(dur), k=ds.max_length))
                                if dur > ds.max_length else range(dur))]
    kps_sha = hashlib.sha256(json.dumps({k: v.tolist() for k, v in sorted(kps.items()) if torch.is_tensor(v)})
                             .encode()).hexdigest()
    src, _ = ds.collate_fn([(cid, kps, "", "", {})])
    src = {k: v.to(DEVICE) if torch.is_tensor(v) else v for k, v in src.items()}
    rec = {"clip_id": cid, "review_id": c["review_id"], "p0a_role": c["p0a_role"], "domain": a.domain,
           "pose_path": os.path.relpath(pkl, REPO), "pose_sha256": pose_sha, "pose_sha_ok": True,
           "n_frames_raw": int(prov[cid][f"{a.domain}_frames"]), "T_frames": int(kps["body"].shape[0]),
           "clip_seed": clip_seed, "global_seed": GLOBAL_SEED, "subsampled": dur > ds.max_length,
           "frame_idx_sha256": hashlib.sha256(json.dumps(fidx).encode()).hexdigest(), "kps_sha256": kps_sha}
    assert len(fidx) == rec["T_frames"], (cid, len(fidx), rec["T_frames"])
    with torch.no_grad():
        ts = time.time()
        out = model(src, {"gt_sentence": [""]})
        rec["sec_forward"] = round(time.time() - ts, 4)
        ts = time.time()
        t = run_generate(out, T_BEAMS)
        rec["sec_T"] = round(time.time() - ts, 4)
        ts = time.time()
        beam5 = run_generate(out, CAND_BEAMS)
        rec["sec_beam5"] = round(time.time() - ts, 4)
    rec["T"] = t[0]
    rec["beam5"] = beam5
    rec["pool"], rec["n_pre_dedup"], rec["n_unique"] = build_pool(t, beam5)
    rec["n_pool"] = len(rec["pool"])
    rec["pool_lt5"] = rec["n_pool"] < POOL_MAX
    rec["sec_clip"] = round(time.time() - ts_clip, 4)
    fo.write(json.dumps(rec) + "\n")
    fo.flush()
    recs[cid] = rec
    n_new += 1
    print(f"{n + 1}/{len(cases)} {c['review_id']} {cid} T={rec['T_frames']} pool={rec['n_pool']} "
          f"{rec['sec_clip']:.1f}s :: {rec['T']['text'][:70]}", flush=True)
    if rec["sec_clip"] > CLIP_SEC_CAP:
        fo.close()
        sys.exit(f"ABORT: {cid} took {rec['sec_clip']:.0f}s > {CLIP_SEC_CAP}s (protocol §1.8)")
fo.close()

# deterministic output order: case_list.csv order, atomic rewrite
tmp = pf + ".tmp"
with open(tmp, "w") as f:
    for c in cases:
        if c["clip_id"] in recs:
            f.write(json.dumps(recs[c["clip_id"]]) + "\n")
os.replace(tmp, pf)

import platform, transformers  # noqa: E402
mf = os.path.join(a.out, "run_meta.json")
meta = json.load(open(mf)) if os.path.exists(mf) else {"runs": []}
meta.update({
    "stage": "P0-A decode_candidates", "protocol": "asl-translator/daily_report/2026-10-23/P0_PROTOCOL_FREEZE.md §1.3",
    "domain": a.domain, "pose_dir": os.path.relpath(pose_dir, REPO),
    "decoding": {"T": f"num_beams={T_BEAMS}, num_return_sequences=1", "candidates": f"num_beams={CAND_BEAMS}, "
                 f"num_return_sequences={CAND_BEAMS}", "max_new_tokens": MAX_NEW, "do_sample": False,
                 "pool": "[T] + beam5 ranks; exact-text dedup, first kept; truncate to <= 5",
                 "seq_score": "HF sequences_scores (sum logprob / n_gen_tokens ** length_penalty)",
                 "length_penalty": LENGTH_PENALTY},
    "hf_generation_config": mt5.generation_config.to_dict(),
    "frames": "upstream load_pose, <=256 frames, random.seed(int(sha256(clip_id)[:8],16)) per clip",
    "device": DEVICE, "precision": "fp32", "torch_threads": torch.get_num_threads(), "global_seed": GLOBAL_SEED,
    "batch_size": 1, "machine": platform.machine(), "processor": platform.processor(),
    "python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__,
    "numpy": np.__version__, "ckpt_sha256": CKPT_SHA, "mt5_snapshot": MT5_SNAPSHOT, "unisign_commit": unisign_commit,
    "case_list_sha256": sha256(CASE_LIST), "provenance_sha256": sha256(PROVENANCE),
    "script_sha256": sha256(os.path.abspath(__file__)), "n_cases": len(cases), "n_records": len(recs), **guard_meta,
    "reference_tripwire_installed": True,
})
meta["runs"].append({"started_unix": t0, "n_decoded": n_new, "seconds": round(time.time() - t0, 2)})
json.dump(meta, open(mf, "w"), indent=1)
print("done", a.domain, "new", n_new, "total", len(recs), f"{time.time() - t0:.0f}s")
