"""Task 2 Step 3: same-domain sampling translation-quality decode (Uni-Sign sampling diagnostic, CPU only).

Only the selected frame indices differ between arms. Everything else is the P0-A / Task 1 control path: Uni-Sign
eed438bc, how2sign_pose_only_slt.pth, mT5 snapshot 2eb15465, S2T_Dataset.load_pose (max_length 256), U.set_seed(42),
batch 1, mt5_model.generate(num_beams=4, max_new_tokens=100, do_sample=False) = the P0-A "T" output.

Arms (frame budget 256; clips with <= 256 pose frames keep every frame, so all three arms are identical controls):
  random          sorted(random.Random(sha256(clip_id)[:8]).sample(range(n), 256)) -- Uni-Sign's own draw
  uniform         sampling.uniform(n, 256)                                   (boss's frozen implementation)
  coverage_motion sampling.coverage_motion(energy, 256), energy from run_sampling.probe on the video the pose was
                  extracted from (B: how2sign_v2/videos/<clip>.mp4; A: official crop clip crop_test/<clip>.mp4)
  coverage_motion_boss  (B subsampled rows only, sensitivity) the boss's sampling_45.json coverage_motion indices,
                  computed on the compressed display re-encode of the same B clip
The sampler code is imported unchanged; nothing is re-implemented. Injection: Uni-Sign's load_pose draws
sorted(random.sample(range(n), 256)); for non-random arms random.sample is replaced, for that one call, by a function
returning the arm's indices. For the random arm the real upstream draw runs and its model-input hash must equal P0-A.

Preflight (--preflight-only), fail closed:
  assets (checkpoint sha256, Uni-Sign commit, mT5 snapshot); R01-R45 x {A_official, B_ours_5p39}; P0-16 holdout guard;
  pose sha256 == P0-A; video frame count == pose frame count for every subsampled row; random arm indices ==
  P0-A frame_idx_sha256; random-arm kps hash via the real upstream draw AND via injection == P0-A kps_sha256;
  boss geometry (sampling_45.json, B display re-encodes) compared on B rows; CPU only (CUDA hidden, MPS disabled,
  every generate() call asserts all parameters and inputs on CPU).
Full run additionally stops if any random-arm output differs from the saved P0-A T text / token ids.

usage (repo root, unisign-cpu-arm64 env):
  python -I asl-translator/experiments/p0-2026-10-27/decode_sampling.py --unisign ... --checkpoint ... --mt5 ...
      --crop-dir DIR --out asl-translator/experiments/p0-2026-10-27/results/sampling_quality_decode.json [--preflight-only]
"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import argparse, hashlib, json, random, subprocess, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
from sampling import coverage_motion, uniform  # noqa: E402  boss's frozen sampler
from run_sampling import probe  # noqa: E402            boss's frozen energy / PTS extraction
sys.path.insert(0, str(REPO / "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402

CKPT = "1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d"
UPSTREAM = "eed438bcb49e30405cd6ccdfcccca330c134e830"
MT5 = "2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f"
BUDGET = 256
DOMAINS = ("A_official", "B_ours_5p39")
ARMS = ("random", "uniform", "coverage_motion")
P0A = REPO / "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/runs/full45"
V2 = REPO / "asl-translator/data/public_benchmarks/how2sign_v2/videos"
BOSS = HERE / "results/sampling_45.json"
MANIFEST = REPO / "asl-translator/daily_report/2026-10-27/p0-input-provenance/input_manifest_45.csv"


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jhash(x):
    return hashlib.sha256(json.dumps(x).encode()).hexdigest()


def geometry(idx, pts, energy):
    idx = list(idx)
    g = np.diff(idx) if len(idx) > 1 else np.array([0])
    out = {"max_gap_frames": int(g.max()), "n_selected": len(idx)}
    if pts is not None:
        out["max_gap_s"] = round(float(np.diff(pts[idx]).max()), 6) if len(idx) > 1 else 0.0
        out["selected_motion_mean"] = round(float(energy[idx].mean()), 6)
    return out


def main():
    ap = argparse.ArgumentParser()
    for k in ("--unisign", "--checkpoint", "--mt5", "--crop-dir", "--out"):
        ap.add_argument(k, type=Path, required=True)
    ap.add_argument("--preflight-only", action="store_true"); ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()

    import csv
    status = {(r["review_id"], r["preprocessing_domain"]): r["provenance_status"] for r in csv.DictReader(MANIFEST.open())}
    recs = {d: sorted((json.loads(l) for l in (P0A / d / "run1/candidates.jsonl").read_text().splitlines()),
                      key=lambda r: r["review_id"]) for d in DOMAINS}
    for d in DOMAINS:
        assert [r["review_id"] for r in recs[d]] == [f"R{i:02d}" for i in range(1, 46)], d
    assert [r["clip_id"] for r in recs["A_official"]] == [r["clip_id"] for r in recs["B_ours_5p39"]]
    assert_not_holdout([r["clip_id"] for r in recs["A_official"]])
    assert digest(a.checkpoint) == CKPT
    assert subprocess.check_output(["git", "-C", str(a.unisign), "rev-parse", "HEAD"], text=True).strip() == UPSTREAM
    assert a.mt5.name == MT5
    boss = {r["review_id"]: r for r in json.loads(BOSS.read_text())}

    import torch
    torch.backends.mps.is_available = lambda: False
    torch.backends.mps.is_built = lambda: False
    assert not torch.cuda.is_available()
    torch.set_num_threads(a.threads)
    sys.path.insert(0, str(a.unisign))
    import config
    config.mt5_path = str(a.mt5)
    import utils as U
    import datasets as UD
    from datasets import S2T_Dataset
    cfg = argparse.ArgumentParser(parents=[U.get_args_parser()]).parse_args([])
    cfg.dataset, cfg.rgb_support, cfg.seed = "How2Sign", False, 42

    def kps_for(ds, cid, seed, idx):
        """idx None -> real upstream draw under random.seed(seed); else inject idx into load_pose's one draw."""
        real = UD.random.sample
        if idx is not None:
            UD.random.sample = lambda pop, k: (assert_len(pop, k, idx), list(idx))[1]
        try:
            random.seed(seed)
            kps, _ = ds.load_pose(cid + ".mp4")
        finally:
            UD.random.sample = real
        kps = {k: v.float() if torch.is_tensor(v) and v.is_floating_point() else v for k, v in kps.items()}
        return kps, jhash({k: v.tolist() for k, v in sorted(kps.items()) if torch.is_tensor(v)})

    def assert_len(pop, k, idx):
        assert k == BUDGET == len(idx) and len(pop) > BUDGET and all(0 <= i < len(pop) for i in idx)

    rows, pre = [], {"checks": {}, "boss_geometry_B": [], "rows": []}
    for d in DOMAINS:
        ds = S2T_Dataset.__new__(S2T_Dataset)
        ds.args, ds.rgb_support, ds.max_length, ds.phase = cfg, False, BUDGET, "test"
        ds.pose_dir = str(REPO / f"docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs/{d}/test-pose-rtmpose-192")
        for r in recs[d]:
            cid, rid, seed = r["clip_id"], r["review_id"], r["clip_seed"]
            pkl = Path(ds.pose_dir) / (cid + ".pkl")
            assert digest(pkl) == r["pose_sha256"], (d, rid)
            n = r["n_frames_raw"]
            row = {"review_id": rid, "clip_id": cid, "domain": d, "provenance_status": status[(rid, d)],
                   "n_frames": n, "subsampled": n > BUDGET, "clip_seed": seed, "arms": {}}
            assert row["subsampled"] == r["subsampled"]
            if n > BUDGET:
                video = (V2 / (cid + ".mp4")) if d == "B_ours_5p39" else (a.crop_dir / (cid + ".mp4"))
                pts, energy = probe(video)
                assert len(pts) == n, (d, rid, len(pts), n)
                row["energy_video"] = (str(video.relative_to(REPO)) if d == "B_ours_5p39"
                                       else f"official crop clip crop_test/{cid}.mp4 (HF ZechengLi19/Uni-Sign; scratch)")
                row["energy_video_sha256"] = digest(video)
                idx = {"random": sorted(random.Random(seed).sample(range(n), BUDGET)),
                       "uniform": uniform(n, BUDGET), "coverage_motion": coverage_motion(energy, BUDGET)}
                if d == "B_ours_5p39":    # sensitivity only: boss's indices from the compressed display re-encode
                    idx["coverage_motion_boss"] = boss[rid]["arms"]["coverage_motion"]["indices"]
            else:
                pts = energy = None
                idx = {k: list(range(n)) for k in ARMS}
            assert jhash(idx["random"]) == r["frame_idx_sha256"], (d, rid, "random indices != P0-A")
            _, k_real = kps_for(ds, cid, seed, None)
            assert k_real == r["kps_sha256"], (d, rid, "upstream random draw kps != P0-A")
            for arm in idx:
                assert len(idx[arm]) == min(n, BUDGET) and idx[arm] == sorted(set(idx[arm]))
                kps, kh = kps_for(ds, cid, seed, idx[arm] if n > BUDGET else None)
                if arm == "random":
                    assert kh == r["kps_sha256"], (d, rid, "injected random kps != P0-A")
                row["arms"][arm] = {"indices": idx[arm], "indices_sha256": jhash(idx[arm]), "kps_sha256": kh,
                                    **geometry(idx[arm], pts, energy)}
                row["arms"][arm]["overlap_with_random"] = len(set(idx[arm]) & set(idx["random"]))
            if d == "B_ours_5p39" and n > BUDGET:
                b = boss[rid]
                pre["boss_geometry_B"].append({
                    "review_id": rid, "boss_n_frames": b["n_frames"], "n_frames": n,
                    "random_identical": b["arms"]["random"]["indices"] == idx["random"],
                    "uniform_identical": b["arms"]["uniform"]["indices"] == idx["uniform"],
                    "coverage_motion_identical": b["arms"]["coverage_motion"]["indices"] == idx["coverage_motion"],
                    "coverage_motion_overlap": len(set(b["arms"]["coverage_motion"]["indices"]) & set(idx["coverage_motion"])),
                    "max_gap_s_boss_vs_ours": {k: [round(b["arms"][k]["max_gap_s"], 6), row["arms"][k]["max_gap_s"]] for k in ARMS}})
            pre["rows"].append({"review_id": rid, "domain": d, "subsampled": row["subsampled"],
                                "random_indices_eq_p0a": True, "random_kps_eq_p0a_upstream": True,
                                "random_kps_eq_p0a_injected": True})
            rows.append(row)
            print("preflight", d, rid, n, row["subsampled"], flush=True)
    bg = pre["boss_geometry_B"]
    pre["checks"] = {
        "rows": len(rows), "holdout_guard": "pass", "cpu_only": {"cuda_available": False, "mps_disabled": True},
        "assets": {"checkpoint_sha256": CKPT, "upstream_commit": UPSTREAM, "mt5_snapshot": MT5},
        "random_indices_eq_p0a": f"{len(rows)}/{len(rows)}", "random_kps_eq_p0a": f"{len(rows)}/{len(rows)}",
        "subsampled_rows": {d: [r["review_id"] for r in rows if r["domain"] == d and r["subsampled"]] for d in DOMAINS},
        "boss_B_random_identical": f"{sum(x['random_identical'] for x in bg)}/{len(bg)}",
        "boss_B_uniform_identical": f"{sum(x['uniform_identical'] for x in bg)}/{len(bg)}",
        "boss_B_coverage_motion_identical": f"{sum(x['coverage_motion_identical'] for x in bg)}/{len(bg)}"}
    out = {"status": "PREFLIGHT_PASS", "generation_executed": False, "preflight": pre}
    a.out.write_text(json.dumps(out, indent=1))
    print(json.dumps(pre["checks"], indent=1))
    if a.preflight_only:
        return

    from transformers.generation.utils import GenerationMixin
    from models import Uni_Sign
    _generate = GenerationMixin.generate
    calls = []
    calls_path = a.out.parent / "sampling_quality_calls.json"

    def checked_generate(self, *args, **kw):
        devs = {p.device.type for p in self.parameters()} | {v.device.type for v in kw.values() if torch.is_tensor(v)}
        assert devs == {"cpu"}, devs
        t0 = time.perf_counter(); seq = _generate(self, *args, **kw)
        calls.append({"devices": sorted(devs), "seconds": round(time.perf_counter() - t0, 4),
                      "kwargs": {k: v for k, v in kw.items() if not torch.is_tensor(v)}})
        calls_path.write_text(json.dumps({"torch": torch.__version__, "threads": torch.get_num_threads(), "calls": calls}, indent=1))
        return seq

    GenerationMixin.generate = checked_generate
    U.set_seed(42)
    model = Uni_Sign(args=cfg).float().cpu()
    model.load_state_dict(torch.load(a.checkpoint, map_location="cpu", weights_only=True)["model"], strict=True)
    model.eval()
    saved = {(r["review_id"], d): r["T"] for d in DOMAINS for r in recs[d]}
    for row in rows:
        d = row["domain"]
        ds = S2T_Dataset.__new__(S2T_Dataset)
        ds.args, ds.rgb_support, ds.max_length, ds.phase = cfg, False, BUDGET, "test"
        ds.pose_dir = str(REPO / f"docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs/{d}/test-pose-rtmpose-192")
        for arm in row["arms"]:
            kps, kh = kps_for(ds, row["clip_id"], row["clip_seed"], row["arms"][arm]["indices"] if row["subsampled"] else None)
            assert kh == row["arms"][arm]["kps_sha256"]
            src, _ = ds.collate_fn([(row["clip_id"], kps, "", "", {})])
            with torch.inference_mode():
                enc = model(src, {"gt_sentence": [""]})
                seq = model.mt5_model.generate(inputs_embeds=enc["inputs_embeds"], attention_mask=enc["attention_mask"],
                                               num_beams=4, max_new_tokens=100, do_sample=False)
            ids = seq[0].tolist()
            row["arms"][arm].update({"text": model.mt5_tokenizer.decode(ids, skip_special_tokens=True), "token_ids": ids,
                                     "eos_present": model.mt5_tokenizer.eos_token_id in ids})
        T = saved[(row["review_id"], d)]
        row["random_matches_saved_T"] = row["arms"]["random"]["text"] == T["text"] and row["arms"]["random"]["token_ids"] == T["ids"]
        out.update(status="RUNNING", generation_executed=True, results=rows[:rows.index(row) + 1])
        a.out.write_text(json.dumps(out, indent=1))
        print(d, row["review_id"], row["subsampled"], row["random_matches_saved_T"],
              [row["arms"][k]["text"][:40] for k in ARMS], flush=True)
        if not row["random_matches_saved_T"]:
            out["status"] = "STOPPED_RANDOM_CONTROL_MISMATCH"; a.out.write_text(json.dumps(out, indent=1))
            raise RuntimeError(f"random control differs from saved P0-A T: {d} {row['review_id']}")
    out.update(status="COMPLETE", results=rows, checkpoint_sha256=CKPT, upstream_commit=UPSTREAM, mt5_snapshot=MT5,
               decode={"num_beams": 4, "max_new_tokens": 100, "do_sample": False, "global_seed": 42, "batch": 1,
                       "threads": torch.get_num_threads()})
    a.out.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
