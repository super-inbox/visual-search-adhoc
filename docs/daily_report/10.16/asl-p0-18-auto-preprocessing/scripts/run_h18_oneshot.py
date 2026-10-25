"""P0-18 H18 one-shot runner (EXPERIMENT_PLAN.md §6-§9). Also runs as a DRY RUN on development (How2Sign test) data.

    python -I run_h18_oneshot.py --mode dryrun --out DIR [--dry-videos 3]
    python -I run_h18_oneshot.py --mode h18 --confirm OPEN-H18          (only after explicit approval)
    add --resume to continue an interrupted run with the SAME lock and FREEZE (infrastructure failures only)

Order (nothing from the target split is read before step 2):
  1  verify FREEZE.json (every frozen file), the P0-16 holdout hashes, and every input file's sha256
  2  write RUN_LOCK.json (refuse if a lock or RESULT.json already exists, unless --resume with the same FREEZE)
  3  target clips: h18 = P0-16 H18_clips.txt (disjoint from H19 and EXCLUDED, asserted);
     dryrun = all clips of the first N How2Sign test VIDEO_IDs in sha1 order (P0-16 guard: must NOT be holdout)
  4  ORIGINAL timing of every clip of the target videos (VIDEO_ID, VIDEO_NAME, SENTENCE_NAME, START, END only)
  5  full-video poses in the canonical GPU pose environment (T4 VM: vm_remote -> vm_worker -> pose_extract; the VM
     range-fetches each member from the pinned mirror and must reproduce the sha256 computed here from the local,
     verified archive) -> conditions A_old, B_auto, B_time_only, B_crop_only, B_lag_only (pipeline, locally); the
     candidate evaluated by P1-P5 is config primary_arm (B_crop_only: original timing + automatic crop)
  6  oracle reference arm C_official: official crop videos posed as P0-12 condition C, same VM environment
     (vm_official)
  7  Uni-Sign decoding of every arm on the evaluable clips in the canonical T4 decoder environment (vm_remote
     .decode_remote -> decode_parallel.py, frozen settings); the decoder environment record must equal the frozen one
  8  sanity gates G1-G3
  9  references (realigned CSV, SENTENCE) -> scoring (score.py) -> criteria P1-P5 -> verdict (p018_verdict)
"""
import argparse, csv, hashlib, json, os, pickle, platform, re, socket, subprocess, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
P016 = os.path.join(os.path.dirname(EXP), "asl-p0-16-experimental-credibility")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(P016, "scripts"))
import holdout_guard as HG  # noqa: E402
import p018_verdict as V  # noqa: E402
import pipeline as PL  # noqa: E402
import pose_extract as PE  # noqa: E402
import vm_remote as VR  # noqa: E402

ARMS = ["A_old", "B_auto", "C_official", "B_time_only", "B_crop_only", "B_lag_only"]
PAIRS = ["A_old-B_auto", "A_old-C_official", "B_auto-C_official", "A_old-B_time_only", "A_old-B_crop_only",
         "A_old-B_lag_only"]
VIDEO_ID = lambda c: re.sub(r"_\d+(?:_\d+)*-\d+-rgb_front$", "", c)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def expand(p):
    return os.path.expanduser(p)


def log(msg):
    print(f"[{now()}] {msg}", flush=True)


def pose_arrays_sha(npz):
    import numpy as np
    z = np.load(npz)
    h = hashlib.sha256()
    for k in ("K", "S", "n_persons"):
        h.update(np.ascontiguousarray(z[k]).tobytes())
    return h.hexdigest()


def remote_poses(remote, inp, videos, local_dir, manifest_path):
    """Canonical GPU pose extraction of `videos` (members of the local verified archive inp) on the VM -> local_dir."""
    if not os.path.exists(manifest_path):
        json.dump(VR.fetch_manifest(inp["path"], videos, inp["url"], inp["sha256"]), open(manifest_path, "w"), indent=1)
    st = VR.ssh(f"test -f ~/{remote}/DONE && echo D || (pgrep -f 'vm_worke[r].py /home/[^ ]*/{remote} ' >/dev/null "
                f"&& echo R || echo N)").split()[-1]
    if st == "N":
        VR.start(remote, manifest_path)
    VR.wait(remote, "DONE", say=log)
    S = VR.download(remote, local_dir)
    if S["failed_videos"]:
        log(f"pose extraction failures: {S['failed_videos']}")
    return S


POSE_ENV_KEYS = ["onnxruntime", "ort_device", "rtmlib", "opencv", "numpy", "models_sha256", "cuda_ep",
                 "deterministic_compute", "workers", "chunk", "ffmpeg", "gpu"]


def pose_env_matches(env_jsonl, frozen):
    """Every extractor start recorded on the VM must equal the frozen canonical pose environment."""
    diff = {}
    for line in open(env_jsonl):
        e = json.loads(line)
        diff.update({k: [frozen.get(k), e.get(k)] for k in POSE_ENV_KEYS if e.get(k) != frozen.get(k)})
    return not diff, diff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["h18", "dryrun"], required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--dry-videos", type=int, default=3)
    ap.add_argument("--confirm", default="")
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()

    # ---------------------------------------------------------------- 1. freeze + input verification
    FZ = json.load(open(os.path.join(EXP, "FREEZE.json")))
    bad = [f for f, h in FZ["files"].items() if sha256(os.path.join(EXP, f)) != h]
    if bad:
        sys.exit(f"REFUSED: frozen files changed: {bad}")
    freeze_sha = sha256(os.path.join(EXP, "FREEZE.json"))
    HG._verify()
    CFG = json.load(open(os.path.join(EXP, "config", "p018_config.json")))
    PRIMARY = CFG["primary_arm"]                            # the P0-18 candidate pipeline (EXPERIMENT_PLAN §4)
    assert PRIMARY in ARMS and PRIMARY not in ("A_old", "C_official"), PRIMARY
    if a.mode == "h18":
        if a.confirm != "OPEN-H18":
            sys.exit("REFUSED: the H18 run needs --confirm OPEN-H18 (explicit approval)")
        out = os.path.join(EXP, "h18_run")
        if a.out and os.path.abspath(a.out) != out:
            sys.exit(f"REFUSED: the H18 run always writes to {out}")
    else:
        if not a.out:
            sys.exit("--out is required for a dry run")
        out = os.path.abspath(a.out)
        if out.startswith(EXP + os.sep):
            sys.exit("REFUSED: dry-run output must live outside the experiment folder")
    INP = {k: dict(v, path=expand(v["path"])) for k, v in CFG["inputs"][a.mode].items()}
    INP.update({k: dict(v, path=expand(v["path"])) for k, v in CFG["inputs"]["common"].items()})
    lock_path, result_path = os.path.join(out, "RUN_LOCK.json"), os.path.join(out, "RESULT.json")
    if os.path.exists(result_path):
        sys.exit("REFUSED: this run is complete (RESULT.json exists); a one-shot run is never repeated")
    if os.path.exists(lock_path):
        lk = json.load(open(lock_path))
        if not (a.resume and lk["freeze_sha256"] == freeze_sha and lk["mode"] == a.mode):
            sys.exit("REFUSED: RUN_LOCK.json exists (use --resume only to continue an interrupted run with the same "
                     "FREEZE)")
        log(f"resuming run locked at {lk['locked_utc']}")
    input_hash_ok = {}
    for k, v in INP.items():
        if not os.path.exists(v["path"]):
            sys.exit(f"REFUSED: input missing: {k} {v['path']}")
        if not (a.resume and os.path.exists(lock_path)):
            input_hash_ok[k] = sha256(v["path"]) == v["sha256"]
            log(f"input {k}: sha256 {'OK' if input_hash_ok[k] else 'MISMATCH'}")
    if input_hash_ok and not all(input_hash_ok.values()):
        sys.exit(f"REFUSED: input hash mismatch: {[k for k, ok in input_hash_ok.items() if not ok]}")

    # ---------------------------------------------------------------- 2. lock
    os.makedirs(out, exist_ok=True)
    if not os.path.exists(lock_path):
        git = subprocess.run(["git", "-C", EXP, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        remote = f"p018/runs/{a.mode}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        if VR.ssh(f"test -e ~/{remote} && echo EXISTS || echo FRESH").split()[-1] != "FRESH":
            sys.exit(f"REFUSED: remote run folder {remote} already exists")
        json.dump({"mode": a.mode, "locked_utc": now(), "freeze_sha256": freeze_sha, "git_head": git,
                   "remote_root": remote, "pose_host": VR.VM[0],
                   "host": socket.gethostname(), "machine": platform.machine(), "python": sys.executable,
                   "input_sha256_verified": input_hash_ok}, open(lock_path, "w"), indent=1)
        log(f"RUN_LOCK written: {lock_path}")
    remote = json.load(open(lock_path))["remote_root"]
    status_path = os.path.join(out, "status.json")
    status = json.load(open(status_path)) if os.path.exists(status_path) else {}

    def done(step, **kw):
        status[step] = dict(kw, utc=now()); json.dump(status, open(status_path, "w"), indent=1)

    if input_hash_ok:                                       # fresh start: all hashes were verified above
        done("inputs", verified=all(input_hash_ok.values()), detail=input_hash_ok)

    # ---------------------------------------------------------------- 3. targets
    H = os.path.join(P016, "holdout")
    if a.mode == "h18":
        target = open(os.path.join(H, "H18_clips.txt")).read().split()
        units = open(os.path.join(H, "H18_units.txt")).read().split()
        tvideos = {v for u in units for v in u.split("+")}
        h19 = set(open(os.path.join(H, "H19_clips.txt")).read().split())
        h19v = {v for u in open(os.path.join(H, "H19_units.txt")).read().split() for v in u.split("+")}
        excl = {r["clip_id"] for r in csv.DictReader(open(os.path.join(H, "EXCLUDED.csv")))}
        assert not (set(target) & (h19 | excl)) and not (tvideos & h19v), "H18 target overlaps H19/EXCLUDED"
        assert len(target) == CFG["h18_expected"]["clips"] and len(tvideos) == CFG["h18_expected"]["videos"]
    else:
        ids = [r["SENTENCE_NAME"] for r in csv.DictReader(open(INP["original_csv"]["path"]), delimiter="\t")]
        vids = sorted({VIDEO_ID(c) for c in ids}, key=lambda v: hashlib.sha1(v.encode()).hexdigest())
        tvideos = set(vids[:a.dry_videos])
        target = sorted(c for c in ids if VIDEO_ID(c) in tvideos)
        HG.assert_not_holdout(target)
    target_set = set(target)

    # ---------------------------------------------------------------- 4. original timing (no text column is kept)
    timeline, timing = {}, {}
    for r in csv.DictReader(open(INP["original_csv"]["path"]), delimiter="\t"):
        if r["VIDEO_ID"] not in tvideos:
            continue
        s, e = float(r["START"]), float(r["END"])
        timeline.setdefault(r["VIDEO_NAME"], []).append((s, e))
        if r["SENTENCE_NAME"] in target_set:
            timing[r["SENTENCE_NAME"]] = (r["VIDEO_NAME"], s, e)
    missing = {c: "no_original_timing" for c in target if c not in timing}

    # ---------------------------------------------------------------- 5. poses + automatic conditions
    pose_dir, cond_dir = os.path.join(out, "poses"), os.path.join(out, "cond")
    os.makedirs(pose_dir, exist_ok=True)
    needed = sorted({timing[c][0] for c in timing})
    if "poses" not in status:
        log(f"pose extraction on {VR.VM[0]}: {len(needed)} videos -> {remote}")
        S = remote_poses(remote, INP["videos_zip"], needed, pose_dir, os.path.join(out, "pose_manifest.json"))
        done("poses", videos=len(needed), **{k: v for k, v in S.items() if not k.endswith("sha256")})
    env_ok, env_diff = pose_env_matches(os.path.join(pose_dir, "extractor_env.jsonl"), CFG["pose_env"])
    xlog = {}
    for line in open(os.path.join(pose_dir, "extract_log.jsonl")):
        j = json.loads(line); xlog[j["video"].replace(".mp4", "")] = j
    for c, (vn, _, _) in timing.items():
        if not os.path.exists(os.path.join(pose_dir, vn + ".npz")):
            missing[c] = "no_raw_video"
    PI, PC = CFG["interval"], CFG["crop"]
    meta_path = os.path.join(out, "build_meta.json")
    if "build" not in status:
        for c in PL.PROD:
            os.makedirs(os.path.join(cond_dir, c), exist_ok=True)
        meta, vmeta = {}, {}
        for vn in needed:
            npz = os.path.join(pose_dir, vn + ".npz")
            if not os.path.exists(npz):
                continue
            t = time.time()
            Vp = PE.VideoPose(npz)
            todo = [(c, s, e) for c, (v, s, e) in sorted(timing.items()) if v == vn]
            vrec, recs = PL.video_intervals(Vp, todo, timeline[vn], PI)
            for cid, rec in recs.items():
                pk, m = PL.build_clip(Vp, cid, rec, PL.PROD, PC)
                for cn, d in pk.items():
                    pickle.dump(d, open(os.path.join(cond_dir, cn, cid + ".pkl"), "wb"))
                meta[cid] = dict(rec, **m, video=vn, failed=PL.clip_failed(rec, m, PRIMARY))
            vrec["seconds_build"] = round(time.time() - t, 2); vmeta[vn] = vrec
        json.dump({"videos": vmeta, "clips": meta}, open(meta_path, "w"), indent=1)
        done("build", clips=len(meta))
    BM = json.load(open(meta_path))

    # ---------------------------------------------------------------- 6. oracle reference arm
    cdir = os.path.join(cond_dir, "C_official"); os.makedirs(cdir, exist_ok=True)
    if "official" not in status:
        oids = os.path.join(out, "official_ids.txt")
        open(oids, "w").write("\n".join(c for c in sorted(timing) if c not in missing) + "\n")
        if VR.ssh(f"test -f ~/{remote}/OFFICIAL_DONE && echo D || (pgrep -f 'vm_officia[l].py /home/[^ ]*/{remote} ' >/dev/null "
                  f"&& echo R || echo N)").split()[-1] == "N":
            log(f"oracle arm C_official on {VR.VM[0]}")
            VR.start_official(remote, oids, INP["crop_index"]["path"])
        VR.wait(remote, "OFFICIAL_DONE", say=log)
        S = VR.download_official(remote, cdir)
        done("official", **{k: v for k, v in S.items() if k != "pkl_sha256"})
    for c in timing:
        if c not in missing and not os.path.exists(os.path.join(cdir, c + ".pkl")):
            missing[c] = "no_official_crop"
    evaluable = sorted(c for c in target if c not in missing
                       and all(os.path.exists(os.path.join(cond_dir, arm, c + ".pkl")) for arm in ARMS))
    for c in target:
        if c not in missing and c not in evaluable:
            missing[c] = "condition_not_built"
    ids_path = os.path.join(out, "evaluable_ids.txt"); open(ids_path, "w").write("\n".join(evaluable) + "\n")
    assert set(evaluable) <= target_set

    # ---------------------------------------------------------------- 7. decoding (canonical T4 decoder environment)
    env = dict(os.environ, UNISIGN_REPO=expand(CFG["env"]["UNISIGN_REPO"]))      # local scorer (SLRT_metrics) only
    DC = CFG["decode"]
    assert (DC["host"], DC["device"], DC["procs"], DC["threads"]) == (VR.VM[0], "cuda", VR.DECODE_PROCS,
                                                                         VR.DECODE_THREADS), "decode config != vm_remote"
    denv_path = os.path.join(out, "decoder_env.json")
    if not os.path.exists(denv_path):
        json.dump(VR.decoder_env(remote), open(denv_path, "w"), indent=1)
    denv = json.load(open(denv_path))
    dec_env_diff = {k: [CFG["decode_env"].get(k), denv.get(k)] for k in set(CFG["decode_env"]) | set(denv)
                    if CFG["decode_env"].get(k) != denv.get(k)}

    def decode(jobs):
        """jobs: [(name, local_pose_dir, ids_file, local_out_dir)] decoded on the T4 (vm_remote.decode_remote)."""
        VR.decode_remote([(n, d, open(f).read().split(), o) for n, d, f, o in jobs], remote, say=log)

    def preds(out_dir):
        return {j["clip_id"]: j for j in map(json.loads, open(os.path.join(out_dir, "predictions.jsonl")))}

    if "decode" not in status:
        log(f"decoding {len(ARMS)} arms x {len(evaluable)} clips on {VR.VM[0]}")
        decode([(arm, os.path.join(cond_dir, arm), ids_path, os.path.join(out, "dec", arm)) for arm in ARMS])
        done("decode", decoder_env_matches_frozen=not dec_env_diff)

    # ---------------------------------------------------------------- 8. sanity gates
    gates, gate_detail = {}, {}
    # G1: the frozen environment reproduces frozen DEVELOPMENT outputs (decoder and pose extractor)
    g1 = CFG["gates"]["G1"]
    g1_dir = os.path.join(out, "g1")
    if "g1" not in status:
        decode([("g1", os.path.join(EXP, g1["pkl_dir"]), os.path.join(EXP, g1["ids"]), os.path.join(g1_dir, "dec"))])
        remote_poses(remote + "_g1", INP["g1_videos_zip"], [g1["pose_video"]], os.path.join(g1_dir, "pose"),
                     os.path.join(g1_dir, "pose_manifest.json"))
        done("g1")
    ref = {j["clip_id"]: j["pred"] for j in map(json.loads, open(os.path.join(EXP, g1["predictions"])))}
    got = {c: j["pred"] for c, j in preds(os.path.join(g1_dir, "dec")).items()}
    pose_sha = pose_arrays_sha(os.path.join(g1_dir, "pose", g1["pose_video"] + ".npz"))
    g1_env_ok, g1_env_diff = pose_env_matches(os.path.join(g1_dir, "pose", "extractor_env.jsonl"), CFG["pose_env"])
    env_ok, env_diff = env_ok and g1_env_ok, dict(env_diff, **{"g1:" + k: v for k, v in g1_env_diff.items()})
    gate_detail["G1_env_reproduction"] = {"decode_identical": got == ref, "n": len(ref),
                                          "pose_arrays_sha256": pose_sha, "pose_identical": pose_sha == g1["pose_sha256"],
                                          "pose_env_matches_frozen": env_ok, "pose_env_diff": env_diff,
                                          "decoder_env_matches_frozen": not dec_env_diff, "decoder_env_diff": dec_env_diff}
    gates["G1_env_reproduction"] = got == ref and pose_sha == g1["pose_sha256"] and env_ok and not dec_env_diff
    # G2: decoding the same inputs twice gives identical output
    g2n = CFG["gates"]["G2"]["n"]
    g2_ids = sorted(evaluable, key=lambda c: hashlib.sha256(c.encode()).hexdigest())[:g2n]
    g2_file = os.path.join(out, "g2_ids.txt"); open(g2_file, "w").write("\n".join(g2_ids) + "\n")
    if "g2" not in status:
        decode([("g2", os.path.join(cond_dir, PRIMARY), g2_file, os.path.join(out, "g2_dec"))])
        done("g2")
    first, second = preds(os.path.join(out, "dec", PRIMARY)), preds(os.path.join(out, "g2_dec"))
    g2_ok = len(g2_ids) == g2n and all(first[c]["pred"] == second[c]["pred"] for c in g2_ids)
    gates["G2_decode_determinism"] = g2_ok
    gate_detail["G2_decode_determinism"] = {"n": len(g2_ids), "identical": g2_ok}
    # G3: integrity
    miss_rate = len(missing) / len(target)
    arms_complete, sha_ok = True, True
    for arm in ARMS:
        P = preds(os.path.join(out, "dec", arm))
        arms_complete &= set(P) == set(evaluable)
        for c in evaluable[:: max(1, len(evaluable) // 50)]:
            sha_ok &= P[c]["pose_sha256"] == sha256(os.path.join(cond_dir, arm, c + ".pkl"))
    processed = {f[:-4] for arm in ARMS for f in os.listdir(os.path.join(cond_dir, arm)) if f.endswith(".pkl")}
    g3 = {"freeze_verified": True, "inputs_verified": status.get("inputs", {}).get("verified", False),
          "target_matches_frozen_list": True,
          "only_target_clips_processed": processed <= target_set,
          "input_missing_rate": miss_rate, "input_missing_ok": miss_rate <= CFG["gates"]["G3"]["max_input_missing_rate"],
          "all_arms_complete": arms_complete, "pose_sha_matches": sha_ok}
    gates["G3_integrity"] = all(v for k, v in g3.items() if k != "input_missing_rate")
    gate_detail["G3_integrity"] = g3

    # ---------------------------------------------------------------- 9. references, scoring, verdict
    refs = {}
    for r in csv.DictReader(open(INP["realigned_csv"]["path"]), delimiter="\t"):
        if r["SENTENCE_NAME"] in set(evaluable):
            refs[r["SENTENCE_NAME"]] = {"ref": r["SENTENCE"], "video": r["VIDEO_ID"]}
    assert set(refs) == set(evaluable), "references missing for evaluable clips"
    json.dump(refs, open(os.path.join(out, "refs.json"), "w"))
    score_out = os.path.join(out, "score.json")
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "score.py"), "--refs", os.path.join(out, "refs.json"),
                        "--ids", ids_path, "--out", score_out, "--B", str(CFG["scoring"]["B"]),
                        "--seed", str(CFG["scoring"]["seed"]), "--pairs", ",".join(PAIRS)]
                       + [f"{arm}={os.path.join(out, 'dec', arm, 'predictions.jsonl')}" for arm in ARMS],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-2000:])
    SC = json.load(open(score_out))
    pt = SC["point"]; gap = pt["C_official"]["bleu4"] - pt["A_old"]["bleu4"]
    fails = sum(1 for c in BM["clips"] if c in target_set and BM["clips"][c].get("failed"))
    n_built = sum(1 for c in BM["clips"] if c in target_set)
    pre_s = sum(xlog[v]["seconds_pose"] + xlog[v].get("seconds_unzip", 0) for v in needed if v in xlog) \
        + sum(v["seconds_build"] for v in BM["videos"].values())
    res = {"primary_arm": PRIMARY, "point": pt, "delta_B_minus_A": SC["paired_delta"][f"{PRIMARY} - A_old"],
           "delta_C_minus_A": SC["paired_delta"]["C_official - A_old"],
           "gap_recovery": {"gap_bleu4": gap,
                            "recovery_bleu4": (pt[PRIMARY]["bleu4"] - pt["A_old"]["bleu4"]) / gap if gap > 0 else None},
           "failure_rate": fails / max(1, n_built), "n_failed": fails, "n_built": n_built,
           "runtime": {"preproc_s_per_clip": pre_s / max(1, n_built), "preproc_s_total": pre_s},
           "n_target": len(target), "n_evaluable": len(evaluable), "n_videos": len({VIDEO_ID(c) for c in evaluable}),
           "missing": missing}
    crit = V.criteria(res, CFG["thresholds"])
    verdict = V.decide(gates, crit)
    out_json = {"mode": a.mode, "label": ("P0-18 H18 CONFIRMATORY RESULT" if a.mode == "h18" else
                                          "DRY RUN on development data (How2Sign test) - NOT a P0-18 result"),
                "verdict": verdict, "gates": gates, "gate_detail": gate_detail, "criteria": crit,
                "thresholds": CFG["thresholds"], "results": res, "score": SC, "freeze_sha256": freeze_sha,
                "finished_utc": now()}
    json.dump(out_json, open(result_path, "w"), indent=1)
    log(f"VERDICT ({out_json['label']}): {verdict}")
    print(json.dumps({"gates": gates, "criteria": crit, "verdict": verdict}, indent=1))


if __name__ == "__main__":
    main()
