"""Task 3: assemble OpenFS reproduction / official-window outputs and the FS-Detection feasibility record.
No model run here; reads the raw specialist.py and fs_detection_smoke.py outputs and the boss's results/specialist.json
(read only). Raw outputs are embedded unchanged so the results are self-contained.

usage (repo root): python -I asl-translator/experiments/p0-2026-10-27/build_specialist_task3.py \
    --old RAW_OLD.json --repeat RAW_REPEAT.json --official RAW_OFFICIAL.json --fsdet FSDET.json --env ENV.json
"""
import argparse, csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REVIEW_PKG = "asl-translator/daily_report/2026-10-23/asl-reviewer-followup/reviewer_package_manifest.csv"
PROV = "asl-translator/daily_report/2026-10-27/p0-input-provenance/input_manifest_45.csv"

# Source spans per input, from committed provenance / reviewer package (seconds in the raw source video).
SPAN = {
    ("R02", "old_window_B_clip_how2sign_v2"): (3.3333, 7.5, "B_ours_5p39 VERIFIED measured slice (provenance)"),
    ("R05", "old_window_B_clip_how2sign_v2"): (1.25, 6.4583, "B_ours_5p39 VERIFIED measured slice (provenance)"),
    ("R35", "old_window_B_clip_how2sign_v2"): (6.5, 12.5, "B_ours_5p39 VERIFIED measured slice (provenance)"),
    ("R41", "old_window_B_clip_how2sign_v2"): (20.0833, 23.9167, "B_ours_5p39 VERIFIED measured slice (provenance)"),
    ("R02", "old_window_reviewer_package_raw_cut"): (3.31, 7.50, "reviewer package cut of raw at original annotation"),
    ("R05", "old_window_reviewer_package_raw_cut"): (1.22, 6.47, "reviewer package cut of raw at original annotation"),
    ("R35", "old_window_reviewer_package_raw_cut"): (6.50, 12.48, "reviewer package cut of raw at original annotation"),
    ("R02", "official_window_fullframe_reviewer_package"): (
        1.43, 11.69, "reviewer package full-frame cut at realigned annotation; A_official VERIFIED slice 1.4583-11.7083 "
                     "(246 frames, same count)"),
    ("R05", "official_window_fullframe_reviewer_package"): (
        0.76, 8.33, "reviewer package full-frame cut at realigned annotation; A_official VERIFIED slice 0.7917-8.375 "
                    "(182 frames vs 181 in the cut)"),
    ("R35", "official_crop_clip_model_input_span_UNRESOLVED"): (
        None, None, "official Uni-Sign crop clip crop_test/<clip>.mp4 = exact A model-input video (93 frames = A pose); "
                    "source span UNRESOLVED (Amendment 2 crop-box margin 0.034 < 0.05)"),
    ("R35", "official_window_fullframe_reviewer_package_annotation_span_not_provenance_verified"): (
        13.11, 16.90, "reviewer package full-frame cut at realigned annotation; NOT provenance-verified (A row UNRESOLVED)"),
}
CLIP = {"R02": "G3OMdQo1zjY_0-10-rgb_front", "R05": "G3VM7etNABI_0-10-rgb_front", "R35": "G2kVb4gINSI_1-10-rgb_front",
        "R41": "g2iFC1st7zQ_1-3-rgb_front"}


def wkey(o):
    return (round(o["start_s"], 3), o["proposal_method"])


def main():
    ap = argparse.ArgumentParser()
    for k in ("--old", "--repeat", "--official", "--fsdet", "--env"):
        ap.add_argument(k, required=True)
    a = ap.parse_args()
    old, rep, off = (json.load(open(p)) for p in (a.old, a.repeat, a.official))
    fsd, env = json.load(open(a.fsdet)), json.load(open(a.env))
    boss = json.load(open(os.path.join(RES, "specialist.json")))
    bossr = {r["case_id"]: r for r in boss["results"]}
    assert old["checkpoint_sha256"] == off["checkpoint_sha256"] == boss["checkpoint_sha256"]
    assert old["upstream_commit"] == off["upstream_commit"] == boss["upstream_commit"]

    meta = {"model": boss["model"], "upstream_repo": "https://github.com/AIRC-KETI/OpenFS",
            "upstream_commit": boss["upstream_commit"],
            "checkpoint": {"source": "OpenFS scripts/download/download_ckpts.sh: gdown 1Ox2sIOtDsafn1TcVg6LQlt7m-gq9xVuq "
                                     "(recognizer.zip -> recognizer/best_model.pth)",
                           "zip_sha256": env["openfs_zip_sha256"], "best_model_pth_sha256": old["checkpoint_sha256"],
                           "matches_boss": old["checkpoint_sha256"] == boss["checkpoint_sha256"],
                           "archived_config": "input_dim 42 (2D), d_model 256, nhead 8, num_layers 3, ff 2048, max_len 1024"},
            "runner": "experiments/p0-2026-10-27/specialist.py (boss, unchanged)",
            "preprocessing": old["preprocessing"], "input_representation": "MediaPipe Holistic hand landmarks, 2D (x, y in "
            "pixels) x 21 points per hand, raised-hand filter (wrist above elbow), per-hand upstream normalize(.5)",
            "decoding": "greedy generate, max_len 32, open vocabulary chars \"$abcdefghijklmnopqrstuvwxyz .&'@\"; no lexicon, "
                        "no reference names, no candidate list",
            "windows": "whole clip + fixed 2 s windows at 1 s stride (proposal_method fixed_window / whole_clip); not detection",
            "license": "OpenFS Non-Commercial Research License (code and checkpoints); research diagnostic only",
            "environment": env["openfs_env"], "device": "cpu", "is_fs_detector": False, "is_rgb_recognizer": False,
            "ground_truth_supplied": False, "accuracy_claim": None}

    # ---- A: reproduction vs boss
    comp = []
    for r in old["results"]:
        b = bossr[r["case_id"]]
        bo = {wkey(o): o["letters"] for o in b["outputs"]}
        for o in r["outputs"]:
            k = wkey(o)
            comp.append({"review_id": r["case_id"], "our_input": r["input_domain"], "start_s": o["start_s"], "end_s": o["end_s"],
                         "proposal_method": o["proposal_method"], "boss_letters": bo.get(k), "our_letters": o["letters"],
                         "exact_match": bo.get(k) == o["letters"]})
    repeat_identical = all(
        [o["letters"] for o in x["outputs"]] == [o["letters"] for o in y["outputs"]]
        for x, y in zip([r for r in old["results"] if r["input_domain"] == "old_window_B_clip_how2sign_v2"], rep["results"]))
    by_input = {}
    for c in comp:
        d = by_input.setdefault(c["our_input"], {"windows": 0, "exact": 0})
        d["windows"] += 1; d["exact"] += c["exact_match"]
    repro = {
        **meta, "question": "Do the boss's recorded old-window OpenFS strings reproduce?",
        "boss_inputs": {cid: {"domain": r["input_domain"], "video_sha256": r["video_sha256"], "n_frames": r["n_frames"],
                              "hand_observations": r["hand_observations"]} for cid, r in bossr.items()},
        "boss_inputs_available_locally": False,
        "boss_inputs_note": "boss ran on compressed OLD-window display re-encodes (sha256 above); none is stored on this "
                            "machine. Closest local inputs used: (1) the B clip the display video was re-encoded from "
                            "(how2sign_v2/videos, same frame count), (2) the reviewer-package raw cut at the original annotation",
        "boss_environment": "Intel macOS, Python 3.11, torch 2.2.2, mediapipe 0.10.9 (requirements-specialist.txt)",
        "shims_applied_here": env["openfs_shims_applied"],
        "summary": {"window_exact_match_by_input": by_input,
                    "determinism_repeat_identical": repeat_identical,
                    "R41_all_windows_match": all(c["exact_match"] for c in comp if c["review_id"] == "R41")},
        "window_comparison": comp,
        "hand_observations_ours": {f"{r['case_id']}|{r['input_domain']}": r["hand_observations"] for r in old["results"]},
        "raw_outputs": old, "raw_outputs_repeat": rep}
    json.dump(repro, open(os.path.join(RES, "specialist_openfs_reproduction.json"), "w"), indent=1)

    # ---- B: official windows
    runs = []
    for r in off["results"]:
        s0, s1, note = SPAN[(r["case_id"], r["input_domain"])]
        runs.append({"review_id": r["case_id"], "clip_id": CLIP[r["case_id"]], "domain": r["input_domain"],
                     "source_clip_sha256": r["video_sha256"], "source_span_s": [s0, s1], "span_basis": note,
                     "n_frames": r["n_frames"], "hand_observations": r["hand_observations"],
                     "runtime_s": round(r["seconds"], 2), "device": "cpu", "status": "ok",
                     "outputs": [{k: o.get(k) for k in ("start_s", "end_s", "time_base", "proposal_method", "letters",
                                                        "hand_frame_count", "mean_token_probability_uncalibrated",
                                                        "status", "fs_present", "character_timestamps")} for o in r["outputs"]]})

    # descriptive old-vs-official window overlap (R02/R05 only: both slices provenance VERIFIED)
    olds = {r["case_id"]: r for r in old["results"] if r["input_domain"] == "old_window_B_clip_how2sign_v2"}
    desc = []
    for rid, os0 in (("R02", 3.3333), ("R05", 1.25)):
        o0 = 1.4583 if rid == "R02" else 0.7917
        offr = next(r for r in off["results"] if r["case_id"] == rid)
        for o in olds[rid]["outputs"]:
            if o["proposal_method"] != "fixed_window":
                continue
            lo, hi = os0 + o["start_s"], os0 + o["end_s"]
            best = max((x for x in offr["outputs"] if x["proposal_method"] == "fixed_window"),
                       key=lambda x: min(hi, o0 + x["end_s"]) - max(lo, o0 + x["start_s"]))
            ov = max(0.0, min(hi, o0 + best["end_s"]) - max(lo, o0 + best["start_s"]))
            desc.append({"review_id": rid, "old_window_source_s": [round(lo, 3), round(hi, 3)], "old_letters": o["letters"],
                         "boss_old_letters": next((b["letters"] for b in bossr[rid]["outputs"] if wkey(b) == wkey(o)), None),
                         "best_overlapping_official_window_source_s": [round(o0 + best["start_s"], 3), round(o0 + best["end_s"], 3)],
                         "official_letters": best["letters"], "overlap_s": round(ov, 3),
                         "note": "windows overlap in source time but are not identical; descriptive only"})
    offj = {**meta, "question": "OpenFS on official-window inputs (R02/R05 primary; R35 separate)",
            "runs": runs, "old_vs_official_descriptive": desc,
            "R35_note": "old (6.50-12.48 s) and official (realigned 13.11-16.90 s) windows do not overlap and the official "
                        "source span is UNRESOLVED; no old-vs-official comparison is made for R35",
            "raw_outputs": off}
    json.dump(offj, open(os.path.join(RES, "specialist_openfs_official.json"), "w"), indent=1)

    # ---- C: FS-Detection
    fsd["checkpoint"]["zip_sha256"] = env["fsdet_zip_sha256"]
    fsd["dependency_matrix"] = env["fsdet_dependency_matrix"]
    fsd["pinned_install_attempts"] = env["fsdet_pinned_install_attempts"]
    fsd["porting_estimate"] = env["fsdet_porting_estimate"]
    fsd["license"] = "No LICENSE file in the repository at this commit (all rights reserved by default); checkpoint has no stated licence"
    json.dump(fsd, open(os.path.join(RES, "fs_detection_feasibility.json"), "w"), indent=1)

    # ---- case table
    rows = []
    for c in comp:
        s0, s1, _ = SPAN[(c["review_id"], c["our_input"])]
        rows.append({"review_id": c["review_id"], "part": "A_reproduction", "domain": c["our_input"], "model": "OpenFS recognizer Chicago",
                     "source_span_start_s": s0, "source_span_end_s": s1, "window_start_s": c["start_s"], "window_end_s": c["end_s"],
                     "interval_source": c["proposal_method"], "letters": c["our_letters"], "boss_letters": c["boss_letters"],
                     "exact_match_boss": c["exact_match"], "score_uncalibrated": "", "fs_present": "unknown",
                     "character_timestamps": "null", "status": "unverified_proposal"})
    for r in runs:
        for o in r["outputs"]:
            rows.append({"review_id": r["review_id"], "part": "B_official", "domain": r["domain"], "model": "OpenFS recognizer Chicago",
                         "source_span_start_s": r["source_span_s"][0], "source_span_end_s": r["source_span_s"][1],
                         "window_start_s": o["start_s"], "window_end_s": o["end_s"], "interval_source": o["proposal_method"],
                         "letters": o["letters"], "boss_letters": "", "exact_match_boss": "",
                         "score_uncalibrated": o["mean_token_probability_uncalibrated"], "fs_present": "unknown",
                         "character_timestamps": "null", "status": o["status"]})
    for r in fsd.get("runs", []):
        for p in r.get("D_forward", {}).get("top_proposals", [])[:5]:
            rows.append({"review_id": r["review_id"], "part": "C_fs_detection_smoke", "domain": "official_window_fullframe_reviewer_package",
                         "model": "FS-Detection ChicagoFSWild+ (CPU-shimmed smoke)", "source_span_start_s": p["source_start_s"],
                         "source_span_end_s": p["source_end_s"], "window_start_s": p["clip_start_s"], "window_end_s": p["clip_end_s"],
                         "interval_source": "detector", "letters": "", "boss_letters": "", "exact_match_boss": "",
                         "score_uncalibrated": p["score_uncalibrated"], "fs_present": "unknown", "character_timestamps": "null",
                         "status": p["status"]})
    with open(os.path.join(RES, "specialist_cases.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(json.dumps(repro["summary"], indent=1)); print(json.dumps(desc, indent=1))


if __name__ == "__main__":
    main()
