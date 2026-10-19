"""P0-18 DEV: decode every development arm in the canonical T4 decoder environment (vm_remote.decode_remote, the same
path the H18 runner uses). Full TEST (evaluable clips): A_old, B_auto, B_time_only, B_crop_only, O_time_crop, O_time.
128-clip oracle set only: C_official, B_lag_only. Records the decoder environment first. Resumable.

Usage: python -I dev_decode_t4.py --dev DEV_DIR --root p018/dev_decode
       DEV_DIR holds cond_gpu/<arm>/*.pkl, gpu_run/C_official/*.pkl, cond_gpu/eval_all.txt, cond_gpu/eval128.txt;
       predictions go to DEV_DIR/dec_t4/<set>/<arm>/predictions.jsonl
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "asl-p0-16-experimental-credibility", "scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402
import vm_remote as VR  # noqa: E402

FULL = ["A_old", "B_auto", "B_time_only", "B_crop_only", "O_time_crop", "O_time"]
ONLY128 = ["C_official", "B_lag_only"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", required=True); ap.add_argument("--root", required=True)
    a = ap.parse_args()
    D = a.dev
    e_all = open(os.path.join(D, "cond_gpu", "eval_all.txt")).read().split()
    e128 = open(os.path.join(D, "cond_gpu", "eval128.txt")).read().split()
    assert set(e128) <= set(e_all)
    assert_not_holdout(e_all)
    os.makedirs(os.path.join(D, "dec_t4"), exist_ok=True)
    env = VR.decoder_env(a.root)
    json.dump(env, open(os.path.join(D, "dec_t4", "decoder_env.json"), "w"), indent=1)
    say = lambda m: print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)
    say(f"decoder env: torch {env['torch']} cuda {env['torch_cuda']} {env['gpu']} ckpt {env['checkpoint_sha256'][:8]}")
    jobs = [(f"all_{arm}", os.path.join(D, "cond_gpu", arm), e_all, os.path.join(D, "dec_t4", "all", arm)) for arm in FULL[:2]]
    jobs += [(f"128_{arm}", os.path.join(D, "gpu_run", "C_official") if arm == "C_official" else os.path.join(D, "cond_gpu", arm),
              e128, os.path.join(D, "dec_t4", "128", arm)) for arm in ONLY128]
    jobs += [(f"all_{arm}", os.path.join(D, "cond_gpu", arm), e_all, os.path.join(D, "dec_t4", "all", arm)) for arm in FULL[2:]]
    VR.decode_remote(jobs, a.root, say)
    say("ALL_DONE")
