"""P0-18 DEV: Old vs Automatic vs Oracle on How2Sign TEST, every arm decoded in the canonical T4 decoder environment
(dev_decode_t4.py). Two sets:
  full  evaluable TEST clips: A_old, B_auto, B_time_only, B_crop_only, O_time, O_time_crop
  128   oracle-arm clips (one per video): the six above + C_official (official crop) + B_lag_only
score.py (paired video-cluster bootstrap) per set, then gap recovery and the timing / crop decomposition, plus the
pre-registered criteria P1-P5 evaluated on development data with the frozen thresholds (p018_verdict.criteria).

Usage: python -I dev_compare.py --dev DEV_DIR --refs TEST_REFS.json --config CONFIG.json --out OUT_DIR
       env: UNISIGN_REPO (SLRT_metrics for score.py)
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "asl-p0-16-experimental-credibility", "scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402
import p018_verdict as V  # noqa: E402
import pipeline as PL  # noqa: E402

FULL = ["A_old", "B_auto", "B_time_only", "B_crop_only", "O_time", "O_time_crop"]
SET128 = FULL + ["C_official", "B_lag_only"]
PAIRS = ["A_old-B_auto", "A_old-B_time_only", "A_old-B_crop_only", "B_time_only-B_auto", "B_crop_only-B_auto",
         "A_old-O_time", "A_old-O_time_crop", "O_time-O_time_crop", "B_auto-O_time_crop"]
PAIRS128 = PAIRS + ["A_old-C_official", "B_auto-C_official", "O_time_crop-C_official", "A_old-B_lag_only"]


def run_score(refs, ids, arms, pairs, preds, out, B, seed):
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "score.py"), "--refs", refs, "--ids", ids, "--out", out,
                        "--B", str(B), "--seed", str(seed), "--pairs", ",".join(pairs)]
                       + [f"{a}={preds[a]}" for a in arms], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-2000:])
    return json.load(open(out))


def recovery(pt, lo, hi, mid, m="bleu4"):
    gap = pt[hi][m] - pt[lo][m]
    return {"gap": gap, "recovered": pt[mid][m] - pt[lo][m], "fraction": (pt[mid][m] - pt[lo][m]) / gap if gap else None}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", required=True); ap.add_argument("--refs", required=True)
    ap.add_argument("--config", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    D, CFG = a.dev, json.load(open(a.config))
    PRIMARY = CFG["primary_arm"]
    os.makedirs(a.out, exist_ok=True)
    R = json.load(open(a.refs)); res = {}
    for name, arms, pairs in (("full", FULL, PAIRS), ("128", SET128, PAIRS128)):
        ids = open(os.path.join(D, "cond_gpu", "eval_all.txt" if name == "full" else "eval128.txt")).read().split()
        assert_not_holdout(ids)
        refs = os.path.join(a.out, f"refs_{name}.json")
        json.dump({c: {"ref": R[c]["ref"], "video": R[c]["video"]} for c in ids}, open(refs, "w"))
        preds = {}
        for arm in arms:
            p = os.path.join(D, "dec_t4", "all", arm, "predictions.jsonl")
            if name == "128" and arm in ("C_official", "B_lag_only"):
                p = os.path.join(D, "dec_t4", "128", arm, "predictions.jsonl")
            preds[arm] = p
        ids_file = os.path.join(a.out, f"ids_{name}.txt"); open(ids_file, "w").write("\n".join(ids) + "\n")
        SC = run_score(refs, ids_file, arms, pairs, preds, os.path.join(a.out, f"score_{name}.json"),
                       CFG["scoring"]["B"], CFG["scoring"]["seed"])
        pt = SC["point"]
        rec = {arm: {m: {"oracle_timing_autocrop": recovery(pt, "A_old", "O_time_crop", arm, m)} for m in ("bleu4", "chrf")}
               for arm in ("B_crop_only", "B_auto")}
        if "C_official" in pt:
            for arm in rec:
                for m in ("bleu4", "chrf"):
                    rec[arm][m]["official"] = recovery(pt, "A_old", "C_official", arm, m)
        dlt = SC["paired_delta"]
        decomp = {"timing_only (B_time_only - A_old)": dlt["B_time_only - A_old"],
                  "crop_only (B_crop_only - A_old)": dlt["B_crop_only - A_old"],
                  "crop_given_auto_timing (B_auto - B_time_only)": dlt["B_auto - B_time_only"],
                  "timing_given_auto_crop (B_auto - B_crop_only)": dlt["B_auto - B_crop_only"],
                  "oracle_timing_only (O_time - A_old)": dlt["O_time - A_old"],
                  "crop_given_oracle_timing (O_time_crop - O_time)": dlt["O_time_crop - O_time"]}
        res[name] = {"n_clips": SC["n_clips"], "n_videos": SC["n_videos"], "point": pt, "paired_delta": dlt,
                     "gap_recovery": rec, "decomposition": decomp}
    # criteria P1, P2, P5 on development data (P3 failure rate / P4 runtime come from the build + pose logs)
    full, s128 = res["full"], res["128"]
    meta = json.load(open(os.path.join(D, "cond_gpu", "build_meta.json")))
    n_built = len(meta["clips"]); n_fail = sum(1 for v in meta["clips"].values() if PL.clip_failed(v, v, PRIMARY))
    pose_s = json.load(open(os.path.join(D, "gpu_run", "poses", "SUMMARY.json")))["pose_seconds"]
    build_s = sum(v["seconds_build"] for v in meta["videos"].values())
    dev_res = {"primary_arm": PRIMARY, "delta_B_minus_A": full["paired_delta"][f"{PRIMARY} - A_old"],
               "gap_recovery": {"gap_bleu4": s128["gap_recovery"][PRIMARY]["bleu4"]["official"]["gap"],
                                "recovery_bleu4": s128["gap_recovery"][PRIMARY]["bleu4"]["official"]["fraction"]},
               "failure_rate": n_fail / n_built, "runtime": {"preproc_s_per_clip": (pose_s + build_s) / n_built},
               "point": full["point"]}
    res["dev_criteria"] = {"inputs": {"delta_B_minus_A": "full set", "gap_recovery": "128 set, C_official oracle",
                                      "failure_rate": f"{n_fail}/{n_built}",
                                      "preproc_s_per_clip": f"(pose {pose_s:.0f} s + build {build_s:.0f} s) / {n_built}"},
                           "values": dev_res, "criteria": V.criteria(dev_res, CFG["thresholds"]),
                           "thresholds": CFG["thresholds"]}
    res["dev_criteria"]["verdict_if_all_gates_pass"] = V.decide({g: True for g in V.GATES}, res["dev_criteria"]["criteria"])
    json.dump(res, open(os.path.join(a.out, "DEV_COMPARISON.json"), "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("dev_criteria",)}, indent=1, default=str))
