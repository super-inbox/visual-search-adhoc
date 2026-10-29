#!/usr/bin/env python3
"""P0-1 Stage A preparation: inventory, input-side candidate set, blind label template, span/crop pipeline, pre-reg.

No recognizer is run (no OpenFS, no FS-Detection, no RGB model), no external API is called and no prediction is
produced. Selection reads only input-side data:
  - the frozen How2Sign v2 manifest columns how2sign_id, source_video_id, video_sha256, duration_s (never the
    reference text, heuristic or words-per-second columns, which are derived from the reference);
  - How2Sign test sentence timing (SENTENCE_NAME, START, END only);
  - the existing per-frame RTMPose wholebody keypoints of our frozen v2 videos (P0-12 B_ours_5p39 inputs);
  - ffprobe frame timestamps of the frozen videos.
It never reads a reference sentence, a Uni-Sign/Gemini/OpenFS output, a score or a detector proposal.

Steps:
  inventory    existing fingerspelling artifacts -> results/p0_1_stage_a_inventory.json
  screen       letter-free hand-kinematics screen over the eligible clips (frozen formula below)
  select       deterministic tiers -> results/p0_1_stage_a_candidate_set.json + blank blind label template
  prereg       schema, pipeline, metrics, gates -> results/p0_1_stage_a_preregistration.json
  --self-test  synthetic checks of the span/frame/crop functions (no video decode, no model)

usage:
  python3 -I p0_1_stage_a_prepare.py --videos-dir DIR --pose-dir DIR --h2s-test-csv FILE [--openfs DIR --fsdet DIR]
  python3 -I p0_1_stage_a_prepare.py --self-test
"""
import argparse, csv, hashlib, json, pickle, re, subprocess, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / "results"
BENCH = REPO / "asl-translator/data/public_benchmarks/how2sign_v2"
CASES45 = REPO / "asl-translator/asl-eval/production_45/production_45_cases.csv"
FUSION = REPO / "docs/daily_report/10.16/asl-unisign-high-precision-fusion/split"
GUARD = REPO / "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"
P0_2_PREREG = REPO / "asl-translator/experiments/p0-2026-10-28/results/p0_2_openai_preregistration.json"
SALT = "P0-1-StageA-2026-10-29"
MANIFEST_COLUMNS = ("how2sign_id", "source_video_id", "video_sha256", "duration_s")     # nothing reference-derived
LEGACY = {"R02": "G3OMdQo1zjY_0-10-rgb_front", "R05": "G3VM7etNABI_0-10-rgb_front",
          "R35": "G2kVb4gINSI_1-10-rgb_front"}                     # existing Step-1 package; OpenFS already run on them

# ---- frozen screen (letter-free; input-side only) -------------------------------------------------------------------
SCREEN = {
    "keypoints": "P0-12 B_ours_5p39 RTMPose wholebody (rtmlib 0.0.13 lightweight), every frame of the frozen v2 video, "
                 "coordinates normalised by (W,H); first detected person per frame",
    "hand_valid": "mean score of the 21 hand keypoints >= 0.5",
    "raised": "hand wrist y above the same-side elbow y (image y grows downward); the OpenFS hand filter",
    "shape": "21 hand points minus the hand wrist point, divided by the max wrist-to-point distance",
    "articulation_rate": "L2 norm of the shape change between consecutive valid frames / dt (dt from frame PTS)",
    "wrist_speed": "hand-wrist displacement / shoulder width / dt",
    "window_s": 1.0,
    "window_score": "r * median(articulation_rate) / (1 + median(wrist_speed)); r = fraction of window frames where "
                    "the hand is valid and raised; computed per hand; windows with fewer than 6 valid raised frames "
                    "score 0",
    "clip_score": "max over windows and both hands",
    "probe_window": "2.0 s centred on the best window, clamped to the clip; used only as the recognizer input span "
                    "for confirmed-negative items (no human span exists there)",
    "clip_raised_fraction": "fraction of frames where either hand is valid and raised",
    "not_used": ["reference text", "names", "any model letter output", "detector proposals or scores",
                 "Uni-Sign / Gemini output or score", "whether a case previously succeeded"]}
TIERS = {"candidate_positive": 16, "candidate_easy_negative": 12, "random": 8}
SIGNER_CAP = 12                                        # at most 1/3 of the 36 items from one signer proxy


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def shs(s):
    return hashlib.sha256(s.encode()).hexdigest()


def lines(p):
    return [x.strip() for x in open(p) if x.strip()]


# ---- frame timing and crop pipeline (shared by both recognizers) ----------------------------------------------------
def frame_table(video, source_offset_s):
    """Every decoded frame: frame_index, clip_time_s (PTS), source_time_s (source offset + PTS). Never resampled."""
    fr = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames", "-show_entries",
         "frame=best_effort_timestamp_time", "-of", "json", str(video)]))["frames"]
    pts = [float(f["best_effort_timestamp_time"]) for f in fr]
    return [{"frame_index": i, "clip_time_s": round(t, 6), "source_time_s": round(source_offset_s + t, 6)}
            for i, t in enumerate(pts)]


def span_frames(table, start_s, end_s):
    """Frames whose clip PTS lies in [start_s, end_s). The span is clip time; nothing is resampled or shifted."""
    assert end_s > start_s
    return [r for r in table if start_s <= r["clip_time_s"] < end_s]


def choose_hand(raised_counts, labelled=None):
    """Human-labelled signing hand if given, else the hand with more valid raised frames in the span (tie: right)."""
    if labelled in ("left", "right"):
        return labelled, "human_label"
    return ("left" if raised_counts.get("left", 0) > raised_counts.get("right", 0) else "right"), "more_raised_frames"


def crop_boxes(landmarks, frame_wh, scale=1.6, min_side=64, smooth=5, max_gap=4):
    """Per-frame square hand crop boxes from one hand's landmarks.

    landmarks: list per span frame of None or an (21,2) pixel array. Returns one dict per frame with box
    [x0, y0, side] (integers) and status detected | interpolated | hand_missing. Deterministic: no randomness.
    """
    W, H = frame_wh
    n = len(landmarks)
    raw = np.full((n, 3), np.nan)
    for i, p in enumerate(landmarks):
        if p is not None:
            p = np.asarray(p, float)
            (x0, y0), (x1, y1) = p.min(0), p.max(0)
            raw[i] = [(x0 + x1) / 2, (y0 + y1) / 2, max(min_side, scale * max(x1 - x0, y1 - y0))]
    det = ~np.isnan(raw[:, 0])
    sm = raw.copy()
    half = smooth // 2
    for i in np.where(det)[0]:                          # centred median over detected frames only
        lo, hi = max(0, i - half), min(n, i + half + 1)
        sm[i] = np.median(raw[lo:hi][det[lo:hi]], axis=0)
    status = np.where(det, "detected", "hand_missing").astype(object)
    idx = np.where(det)[0]
    for a, b in zip(idx[:-1], idx[1:]):                 # interpolate short interior gaps only
        if 1 < b - a <= max_gap + 1:
            for i in range(a + 1, b):
                w = (i - a) / (b - a)
                sm[i] = (1 - w) * sm[a] + w * sm[b]; status[i] = "interpolated"
    out = []
    for i in range(n):
        if status[i] == "hand_missing":
            out.append({"box": None, "status": "hand_missing"}); continue
        cx, cy, s = sm[i]
        s = int(round(min(s, W, H)))
        x0 = int(round(min(max(cx - s / 2, 0), W - s))); y0 = int(round(min(max(cy - s / 2, 0), H - s)))
        out.append({"box": [x0, y0, s], "status": str(status[i])})
    return out


def self_test():
    t = [{"frame_index": i, "clip_time_s": round(i / 24, 6), "source_time_s": round(10 + i / 24, 6)} for i in range(48)]
    sf = span_frames(t, 0.5, 1.0)
    assert [r["frame_index"] for r in sf] == list(range(12, 24)) and sf[0]["source_time_s"] == 10.5
    hand = np.array([[0, 0], [20, 40]], float)
    lm = [hand + [100 + i, 200] for i in range(6)]
    lm[2] = None; lm[3] = None                           # 2-frame gap -> interpolated
    seq = lm + [None] * 6 + [hand + [300, 300]]          # 6-frame gap -> hand_missing
    b1, b2 = crop_boxes(seq, (1280, 720)), crop_boxes(seq, (1280, 720))
    assert b1 == b2, "crop boxes must be deterministic"
    st = [b["status"] for b in b1]
    assert st[2] == st[3] == "interpolated" and st[6:12] == ["hand_missing"] * 6 and st[12] == "detected"
    assert all(b["box"][2] >= 64 and b["box"][0] >= 0 and b["box"][1] >= 0 for b in b1 if b["box"])
    edge = crop_boxes([np.array([[0, 0], [10, 10]], float)], (1280, 720))[0]["box"]
    assert edge[0] == 0 and edge[1] == 0, "boxes are shifted inside the frame, never shrunk below min side"
    assert choose_hand({"left": 5, "right": 5}) == ("right", "more_raised_frames")
    assert choose_hand({"left": 9, "right": 1}, "right") == ("right", "human_label")
    print(json.dumps({"self_test": "pass", "checks": ["span_frames", "crop determinism", "short-gap interpolation",
                                                      "long-gap hand_missing", "edge clamp", "hand choice"]}))


# ---- screen --------------------------------------------------------------------------------------------------------
def load_pose(p):
    d = pickle.load(open(p, "rb")); K, S = [], []
    for k, s in zip(d["keypoints"], d["scores"]):
        k = np.asarray(k, float); s = np.asarray(s, float)
        if k.ndim == 3 and k.shape[0] >= 1:
            K.append(k[0]); S.append(s[0])
        else:
            K.append(np.full((133, 2), np.nan)); S.append(np.zeros(133))
    return np.array(K), np.array(S)


def screen_clip(K, S, pts):
    n = len(K)
    assert n == len(pts), "pose frames must match video frames"
    pts = np.asarray(pts)
    shoulder = np.linalg.norm(K[:, 5] - K[:, 6], axis=1)
    best = (0.0, None, None); raised_any = np.zeros(n, bool)
    for side, (h0, elbow, wrist) in {"left": (91, 7, 9), "right": (112, 8, 10)}.items():
        hand = K[:, h0:h0 + 21]
        valid = S[:, h0:h0 + 21].mean(1) >= 0.5
        raised = valid & (K[:, wrist, 1] < K[:, elbow, 1])
        raised_any |= raised
        rel = hand - hand[:, :1]
        scale = np.linalg.norm(rel, axis=2).max(1)
        shape = rel / np.where(scale > 0, scale, np.nan)[:, None, None]
        art = np.full(n, np.nan); spd = np.full(n, np.nan)
        for i in range(1, n):
            if valid[i] and valid[i - 1] and pts[i] > pts[i - 1]:
                dt = pts[i] - pts[i - 1]
                art[i] = np.linalg.norm(shape[i] - shape[i - 1]) / dt
                spd[i] = np.linalg.norm(hand[i, 0] - hand[i - 1, 0]) / max(shoulder[i], 1e-6) / dt
        for i in range(n):
            j = np.searchsorted(pts, pts[i] + SCREEN["window_s"])
            w = slice(i, j)
            ok = raised[w] & ~np.isnan(art[w])
            if ok.sum() < 6:
                continue
            sc = raised[w].mean() * np.median(art[w][ok]) / (1 + np.median(spd[w][ok]))
            if sc > best[0]:
                best = (float(sc), side, (float(pts[i]), float(pts[min(j, n) - 1])))
    return best, float(raised_any.mean())


def probe_window(win, dur):
    c = (win[0] + win[1]) / 2
    lo = min(max(0.0, c - 1.0), max(0.0, dur - 2.0))
    return [round(lo, 3), round(min(dur, lo + 2.0), 3)]


# ---- main ----------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--videos-dir", type=Path); ap.add_argument("--pose-dir", type=Path)
    ap.add_argument("--h2s-test-csv", type=Path, help="How2Sign test sentence timing; only SENTENCE_NAME/START/END read")
    ap.add_argument("--openfs", type=Path); ap.add_argument("--fsdet", type=Path)
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    sys.path.insert(0, str(GUARD))
    from holdout_guard import assert_not_holdout

    man = [{k: r[k] for k in MANIFEST_COLUMNS} for r in csv.DictReader(open(BENCH / "manifest.csv"))]
    freeze = {l.split()[1]: l.split()[0] for l in lines(BENCH / "FREEZE_CHECKSUMS.sha256")}
    timing = {r["SENTENCE_NAME"]: (float(r["START"]), float(r["END"]))
              for r in ({k: x[k] for k in ("SENTENCE_NAME", "START", "END")}
                        for x in csv.DictReader(open(a.h2s_test_csv), delimiter="\t"))}
    dev45 = {r["clip_id"]: r["review_id"] for r in csv.DictReader(open(CASES45))}
    fin_v = {v for u in lines(FUSION / "final_units.txt") for v in u.split("+")}
    p02 = json.loads(P0_2_PREREG.read_text())["selection"]
    p02_role = {**{i: "P0-2 pilot" for i in p02["pilot_ids"]}, **{i: "P0-2 reserve" for i in p02["reserve_ids"]}}

    rows = []
    for r in man:
        cid = r["how2sign_id"]
        v = a.videos_dir / f"{cid}.mp4"
        ok = v.exists() and sha256(v) == freeze[f"videos/{cid}.mp4"] == r["video_sha256"]
        excl = ("p0_15_sealed_final" if r["source_video_id"] in fin_v else
                "legacy_step1_package" if cid in LEGACY.values() else None if ok else "video_not_verified")
        rows.append({"clip_id": cid, "source_video_id": r["source_video_id"], "video_sha256": r["video_sha256"],
                     "signer_proxy": re.search(r"-(\d+)-rgb_front$", cid).group(1),
                     "duration_s": float(r["duration_s"]), "dev45_review_id": dev45.get(cid),
                     "p0_2_role": p02_role.get(cid), "excluded": excl})
    elig = [x for x in rows if x["excluded"] is None]
    assert_not_holdout([x["clip_id"] for x in elig])

    for x in elig:
        v = a.videos_dir / f"{x['clip_id']}.mp4"
        tab = frame_table(v, timing[x["clip_id"]][0])
        K, S = load_pose(a.pose_dir / f"{x['clip_id']}.pkl")
        (sc, side, win), rfrac = screen_clip(K, S, [t["clip_time_s"] for t in tab])
        dur = tab[-1]["clip_time_s"]
        x.update(n_frames=len(tab), source_offset_s=timing[x["clip_id"]][0], screen_score=round(sc, 6),
                 screen_hand=side, screen_window_clip_s=[round(w, 3) for w in win] if win else None,
                 probe_window_clip_s=probe_window(win, dur) if win else [0.0, round(min(2.0, dur), 3)],
                 clip_raised_fraction=round(rfrac, 4), order_key=shs(f"{SALT}|{x['clip_id']}"))

    # ---- deterministic tiers --------------------------------------------------------------------------------------
    taken, per_signer = [], {}

    def take(x, tier):
        if per_signer.get(x["signer_proxy"], 0) >= SIGNER_CAP:
            return False
        x["tier"] = tier; taken.append(x); per_signer[x["signer_proxy"]] = per_signer.get(x["signer_proxy"], 0) + 1
        return True

    by_score = sorted(elig, key=lambda x: (-x["screen_score"], x["order_key"]))
    for x in by_score:
        if sum(t["tier"] == "candidate_positive" for t in taken) == TIERS["candidate_positive"]:
            break
        take(x, "candidate_positive")
    rest = [x for x in elig if x not in taken]
    med_r = float(np.median([x["clip_raised_fraction"] for x in elig]))
    low_half = {x["clip_id"] for x in sorted(elig, key=lambda x: x["screen_score"])[:len(elig) // 2]}
    for x in sorted((x for x in rest if x["clip_raised_fraction"] >= med_r and x["clip_id"] in low_half),
                    key=lambda x: x["order_key"]):
        if sum(t["tier"] == "candidate_easy_negative" for t in taken) == TIERS["candidate_easy_negative"]:
            break
        take(x, "candidate_easy_negative")
    for x in sorted((x for x in elig if x not in taken), key=lambda x: x["order_key"]):
        if sum(t["tier"] == "random" for t in taken) == TIERS["random"]:
            break
        take(x, "random")
    assert len(taken) == sum(TIERS.values())
    for k, x in enumerate(sorted(taken, key=lambda x: shs(f"{SALT}|blind|{x['clip_id']}")), 1):
        x["blind_id"] = f"FSA-{k:03d}"                 # blind ID order is independent of tier

    items = []
    for x in sorted(taken, key=lambda x: x["blind_id"]):
        items.append({
            "blind_id": x["blind_id"], "clip_id": x["clip_id"], "source_video_id": x["source_video_id"],
            "video_sha256": x["video_sha256"], "signer_proxy": x["signer_proxy"],
            "clip_window": {"time_base": "clip PTS seconds of the frozen v2 video", "start_s": 0.0,
                            "end_s": x["duration_s"], "n_frames": x["n_frames"]},
            "source_offset_s": x["source_offset_s"],
            "selection_tier": x["tier"],
            "category_rule": {"candidate_positive": "top-16 screen score (signer cap 12)",
                              "candidate_easy_negative": "clip raised-hand fraction >= eligible median and screen "
                                                         "score in the eligible bottom half; first 12 by salted hash",
                              "random": "first 8 of the remainder by salted hash"}[x["tier"]],
            "final_category": "assigned only from blind Step-1 labels (positive / negative / uncertain); "
                              "Uni-Sign already-correct control status is derived after labelling",
            "screen": {"score": x["screen_score"], "hand": x["screen_hand"], "window_clip_s": x["screen_window_clip_s"],
                       "clip_raised_fraction": x["clip_raised_fraction"]},
            "probe_window_clip_s": x["probe_window_clip_s"],
            "dev45_review_id": x["dev45_review_id"], "p0_2_role": x["p0_2_role"],
            "reviewer_sees_reference_text": False, "reviewer_sees_screen_or_tier": False})
    cand = {"stage": "P0-1 Stage A expanded blind label set (selection only; no label, no prediction)",
            "salt": SALT, "pool": {"benchmark": "How2Sign v2 frozen 128 (test split; FREEZE.sha256 "
                                                f"{lines(BENCH / 'FREEZE.sha256')[0][:16]}...)",
                                   "clips": len(rows), "eligible": len(elig),
                                   "excluded": {k: sum(x["excluded"] == k for x in rows)
                                                for k in ("p0_15_sealed_final", "legacy_step1_package",
                                                          "video_not_verified")},
                                   "eligible_dev45": sum(x["dev45_review_id"] is not None for x in elig),
                                   "eligible_raised_fraction_median": med_r,
                                   "clean_untouched": False,
                                   "exposure_note": "every clip has prior Uni-Sign and Gemini exposure; no clip in "
                                                    "the selected set has been run through OpenFS, FS-Detection or "
                                                    "an RGB fingerspelling recognizer"},
            "screen": SCREEN, "tiers": TIERS, "signer_cap": SIGNER_CAP,
            "tier_counts": {t: sum(x["tier"] == t for x in taken) for t in TIERS},
            "signer_counts": dict(sorted(per_signer.items(), key=lambda kv: int(kv[0]))),
            "dev45_in_set": sum(x["dev45_review_id"] is not None for x in taken),
            "legacy_package_separate": {k: v for k, v in LEGACY.items()},
            "items": items,
            "eligible_screen_table": [{k: x[k] for k in ("clip_id", "signer_proxy", "screen_score",
                                                         "clip_raised_fraction")} for x in elig]}
    OUT.mkdir(exist_ok=True)
    (OUT / "p0_1_stage_a_candidate_set.json").write_text(json.dumps(cand, indent=1) + "\n")
    with open(OUT / "p0_1_stage_a_blind_labels_TEMPLATE.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(LABEL_FIELDS)
        for it in items:
            w.writerow([it["blind_id"], f"{it['blind_id']}.mp4", 1] + [""] * (len(LABEL_FIELDS) - 3))

    inv = inventory(a)
    (OUT / "p0_1_stage_a_inventory.json").write_text(json.dumps(inv, indent=1) + "\n")
    (OUT / "p0_1_stage_a_preregistration.json").write_text(json.dumps(prereg(cand), indent=1) + "\n")
    print(json.dumps({"eligible": len(elig), "tier_counts": cand["tier_counts"], "signer_counts": cand["signer_counts"],
                      "dev45_in_set": cand["dev45_in_set"], "excluded": cand["pool"]["excluded"]}, indent=1))


# ---- blind label schema ---------------------------------------------------------------------------------------------
LABEL_FIELDS = ["blind_id", "video_file", "span_no", "fingerspelling_present", "span_start_s", "span_end_s",
                "letters", "letters_confidence", "signing_hand", "visibility_issue", "occlusion_issue",
                "multiple_spans_in_clip", "notes", "reviewer_id", "asl_background", "labelled_at"]
LABEL_SCHEMA = {
    "blind_id": "FSA-### only; no clip ID, case ID or source name is shown",
    "video_file": "blind-named copy of the frozen clip; clip time = file time",
    "span_no": "1, 2, ... one row per fingerspelling span; one row with span_no 1 if none",
    "fingerspelling_present": "yes | no | uncertain (whole clip)",
    "span_start_s / span_end_s": "clip seconds (file time), span level only; per-letter times are NOT collected",
    "letters": "letters seen, a-z, as signed (no correction to an English word); '?' for an unreadable letter; "
               "blank if not readable",
    "letters_confidence": "high | medium | low",
    "signing_hand": "left | right | both | unclear",
    "visibility_issue": "none | motion_blur | out_of_frame | low_resolution | lighting | other",
    "occlusion_issue": "none | other_hand | body | object | other",
    "multiple_spans_in_clip": "yes | no",
    "notes": "free text",
    "not_shown_in_step1": ["reference sentence", "expected name or word", "OpenFS output", "RGB output",
                           "Uni-Sign / Gemini output", "selection tier or screen window", "clip/source ID"]}


def inventory(a):
    def committed(p):
        q = REPO / p
        return {"path": p, "exists": q.exists(), "sha256": sha256(q) if q.is_file() else None}

    local = lambda p: bool(p and Path(p).exists())
    return {
        "stage": "P0-1 Stage A inventory of existing fingerspelling artifacts (no model run)",
        "artifacts": [
            {**committed("asl-translator/experiments/p0-2026-10-27/specialist.py"),
             "role": "OpenFS CPU runner (boss's adapter): MediaPipe Holistic -> raised-hand filter -> OpenFS greedy "
                     "letters on whole clip + fixed 2 s windows", "modality": "keypoint",
             "reproducibility": "same commit/checkpoint as boss; deterministic run-to-run here; boss strings "
                                "reproduce 10/18 windows (input encode + platform sensitivity)",
             "reuse_for_stage_a": "yes as the keypoint baseline runner, with the span taken from human labels "
                                  "instead of fixed windows (same model call)",
             "limitations": "no abstain except < 8 hand frames; greedy decoding amplifies landmark jitter; x86 "
                            "Rosetta platform; non-commercial licence"},
            {**committed("asl-translator/experiments/p0-2026-10-27/results/specialist_openfs_official.json"),
             "role": "OpenFS outputs on R02/R05 official windows (+ R35 separate)", "modality": "keypoint",
             "reproducibility": "re-runnable from specialist.py", "reuse_for_stage_a": "no for scoring the expanded "
             "set (different items, fixed windows); legacy package only", "limitations": "unverified_proposal; "
             "fs_present unknown; R35 official span UNRESOLVED"},
            {**committed("asl-translator/experiments/p0-2026-10-27/results/specialist_openfs_reproduction.json"),
             "role": "boss-vs-ours OpenFS reproduction, determinism repeat", "modality": "keypoint",
             "reproducibility": "documented", "reuse_for_stage_a": "evidence of platform sensitivity only",
             "limitations": "old windows; boss inputs not local"},
            {**committed("asl-translator/experiments/p0-2026-10-27/results/specialist.json"),
             "role": "boss's original OpenFS run (old windows)", "modality": "keypoint",
             "reproducibility": "partial (10/18)", "reuse_for_stage_a": "no", "limitations": "not modified"},
            {**committed("asl-translator/experiments/p0-2026-10-27/results/specialist_cases.csv"),
             "role": "one row per OpenFS window / FS-Detection proposal", "modality": "keypoint + detector",
             "reproducibility": "derived", "reuse_for_stage_a": "no", "limitations": "unvalidated"},
            {**committed("asl-translator/experiments/p0-2026-10-27/fs_detection_smoke.py"),
             "role": "FS-Detection stage-1 CPU smoke (3 shims)", "modality": "detector-only (RGB + flow input)",
             "reproducibility": "CPU/torch-2.2 equivalence to published GPU outputs NOT verified",
             "reuse_for_stage_a": "no: Stage A uses human spans; reserved for Stage B (automatic localization)",
             "limitations": "no LICENSE file; trained on ChicagoFSWild+; stage-2, NMS not ported"},
            {**committed("asl-translator/experiments/p0-2026-10-27/results/fs_detection_feasibility.json"),
             "role": "FS-Detection top-50 proposals R02/R05 + setup log", "modality": "detector-only",
             "reproducibility": "documented", "reuse_for_stage_a": "no (Stage B only)",
             "limitations": "uncalibrated scores; unvalidated proposals"},
            {**committed("asl-translator/daily_report/2026-10-27/TASK3_FINGERSPELLING_RESULT.md"),
             "role": "Task 3 report (OpenFS + FS-Detection)", "modality": "report", "reproducibility": "n/a",
             "reuse_for_stage_a": "source of facts", "limitations": "no accuracy claim"},
            {**committed("asl-translator/daily_report/2026-10-23/asl-reviewer-followup/blind_review.csv"),
             "role": "existing Step-1 blind package rows (R02/R05/R35 FS check, R26/R29 context)",
             "modality": "human-label template", "reproducibility": "build_reviewer_package.py",
             "reuse_for_stage_a": "schema basis; its 3 FS cases stay a separate legacy stratum",
             "limitations": "3 FS cases only; reviewer labels still empty"},
            {**committed("asl-translator/daily_report/2026-10-23/p0b-fingerspelling-feasibility/interval_labels.csv"),
             "role": "earlier interval-label sheet for R02/R05/R35 (old + realigned windows)",
             "modality": "human-label template", "reproducibility": "n/a", "reuse_for_stage_a": "superseded by the "
             "Stage A schema", "limitations": "unfilled"},
            {**committed("asl-translator/data/public_benchmarks/how2sign_v2/validation/"
                         "review_proper_noun_fingerspelling.csv"),
             "role": "proper-noun / fingerspelling candidate review", "modality": "reference-text derived",
             "reproducibility": "n/a", "reuse_for_stage_a": "NO for selection: derived from reference text",
             "limitations": "reference-derived"},
            {"path": "docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs/B_ours_5p39/",
             "exists": local(a.pose_dir), "role": "per-frame RTMPose wholebody keypoints of the frozen v2 videos "
             "(local, git-ignored)", "modality": "keypoint (input-side)", "reproducibility": "P0-12 scripts",
             "reuse_for_stage_a": "yes: letter-free selection screen only", "limitations": "rtmlib lightweight; "
             "not the OpenFS keypoint path"},
            {"path": "<local scratch> OpenFS @ 0d6fa3fa + recognizer/best_model.pth (c8e4c227...2925)",
             "exists": local(a.openfs), "role": "keypoint recognizer code + checkpoint (not committed; licence)",
             "modality": "keypoint", "reproducibility": "re-downloadable (download_ckpts.sh)",
             "reuse_for_stage_a": "yes", "limitations": "non-commercial research licence"},
            {"path": "<local scratch> FS-Detection @ b386f04d + fswild-plus best-dev.pth (004d4abc...)",
             "exists": local(a.fsdet), "role": "detector code + checkpoint (not committed)",
             "modality": "detector-only", "reproducibility": "re-downloadable", "reuse_for_stage_a": "no (Stage B)",
             "limitations": "no licence"}],
        "rgb_recognizer_present_locally": False,
        "summary": "Only a keypoint recognizer (OpenFS) and a detector (FS-Detection) exist locally. No hand-RGB "
                   "recognizer exists in the repo or the local environment."}


def prereg(cand):
    return {
        "stage": "P0-1 Stage A pre-registration (frozen before any Stage A label or prediction exists)",
        "date": "2026-10-29",
        "source_of_truth": ["2026-10-28 NEXT_P0_PLAN.md (origin/codex/asl-next-p0-20261028) P0-1",
                            "2026-10-28 PROGRESS_REVIEW.md"],
        "question": "On independently human-confirmed fingerspelling spans, can the letters be read, and does a hand-"
                    "RGB recognizer add information over the existing keypoint recognizer? Diagnostic only; reported "
                    "separately from automatic localization (Stage B) and fusion (Stage C).",
        "recognizers": {
            "keypoint_baseline": {
                "name": "OpenFS recognizer (CVPR 2026, AIRC-KETI)", "repo_commit": "0d6fa3fa9b5aeaf99171e8c77e89531a22a6fd27",
                "checkpoint": "recognizer/best_model.pth sha256 c8e4c227ea9cf02a0574518cd01bd6f56fd9d390cc0aa05404eedfafbf642925 "
                              "(recognizer.zip b7a562e1...; Google Drive 1Ox2sIOtDsafn1TcVg6LQlt7m-gq9xVuq)",
                "architecture": "EncoderDecoderTransformer, input_dim 42 (21 hand points x 2D), d_model 256, 8 heads, "
                                "3 layers, ff 2048",
                "preprocessing": "MediaPipe Holistic 0.10.9 (model_complexity 1, full frame, single signer, no YOLO "
                                 "crop); a hand is kept on a frame only if its wrist is above its elbow; per-hand "
                                 "upstream normalize(.5); compact per-hand frame indices",
                "decoding": "greedy, max 32 tokens, open vocabulary over '$abcdefghijklmnopqrstuvwxyz .&\\'@'; no "
                            "lexicon, no language model",
                "abstain": "fewer than 8 hand observations in the span -> abstain (insufficient_hand_observations); "
                           "an empty decoded string also counts as abstain",
                "runner": "asl-translator/experiments/p0-2026-10-27/specialist.py model path, unchanged, with the span "
                          "taken from the human label instead of fixed windows",
                "platform": "Apple M3 Pro, Python 3.11.7 x86_64 (Rosetta), torch 2.2.2 CPU, mediapipe 0.10.9, numpy "
                            "1.26.4, 2 threads; known platform/encode sensitivity (boss strings reproduce 10/18)",
                "is_rgb": False, "note": "never to be described as hand-RGB fusion"},
            "rgb_primary": {
                "name": "HandReader_RGB (ai-forever/HandReader, arXiv 2505.10267)",
                "repo": "https://github.com/ai-forever/HandReader @ 77d390d0650a63b917087b78ab36e1eeb4e0ae3b",
                "licence": "code: Apache-2.0 (LICENSE sha256 c71d239d...). checkpoint: trained on ChicagoFSWild+; "
                           "checkpoint and data use remain subject to the relevant dataset/checkpoint terms, not "
                           "necessarily covered by the code licence",
                "variant": "RGB: TSM ResNet-34 (unidirectional shift) + 2-layer BiGRU head (1024), CTC, configs/"
                           "rgb_chicago.yaml (sha256 3ccc1c1b...)",
                "checkpoint": "HandReader_ChicagoFSWild+.zip (sha256 f66a5c77...) -> chicago+/rgb/best.pt sha256 "
                              "fa92e90db23a467c59d47e718f07233b94d73c1bff8dfdf3a2248ed4f3c9ad0a (strict load: 241 "
                              "tensors, 0 missing, 0 unexpected)",
                "alphabet": "chars_ctc '_ &'.@abcdefghijklmnopqrstuvwxyz', blank index 0 ('_'), 32 classes",
                "input": "per-frame RGB hand crops; eval transform Normalize(ImageNet mean/std) then Resize(224,224), "
                         "ToTensorV2; frames concatenated with per-clip lengths; no temporal resampling. Upstream "
                         "ships no crop code (training crops came from the Shi et al. 2019 localizer); Stage A uses "
                         "the shared MediaPipe crop pipeline below",
                "decoding": {
                    "primary": "CTC beam search, beam size 5, no language model, no lexicon (upstream beam_decode, "
                               "scorer None, so lm_beta/ins_gamma are inactive)",
                    "secondary": "upstream greedy_decode, diagnostic only; never used for a metric or gate",
                    "why": "the upstream greedy decoder can collapse a legitimate repeated letter: after 2+ emitted "
                           "characters it skips a letter equal to the previous emitted letter, even across a blank",
                    "not_claimed": "beam decoding is not claimed to be more accurate on our data",
                    "freeze_statement": "This decoder choice was frozen before any Stage A evaluation output was "
                                        "produced and therefore was not selected based on benchmark accuracy."},
                "runtime": "CPU, Python 3.11.7 x86_64 (Rosetta), torch 2.0.1, torchvision 0.15.2; runtime patches "
                           "P1 (no ImageNet download at construction) and P2 (Tensor.cuda no-op on CPU), no model "
                           "logic change; see results/p0_1_handreader_rgb_feasibility.json",
                "status": "feasibility PASSED 2026-10-29 on a synthetic input; NOT run on any Stage A item",
                "risks": ["crop-source shift (MediaPipe crops vs the training localizer)", "only 2 public commits",
                          "ChicagoFSWild+ domain vs How2Sign studio video", "x86_64 Rosetta CPU platform"]},
            "rgb_fallback": {
                "name": "MiCT-RANet (fmahoudeau/MiCT-RANet-ASL-FingerSpelling), ChicagoFSWild+ weights",
                "input": "full RGB frames (224/256p) plus Farneback optical flow; attention finds the hand, no crop",
                "checkpoint": "released (Proton Drive): MiCT-RANet34.pth (V1) and MiCT-RANet18 ChicagoFS large (V2)",
                "licence": "NOT stated on the repo page: research use must be confirmed before use",
                "decoding": "CTC beam search, beam 5, no language model",
                "status": "NOT installed, NOT run", "use_if": "HandReader cannot be installed or run on CPU, or its "
                                                              "checkpoint cannot be verified"}},
        "spans": {
            "positives": "human-confirmed span(s) from blind Step 1 (fingerspelling_present = yes, letters given, "
                         "letters_confidence high or medium); both recognizers get exactly the same span",
            "negatives": "items labelled fingerspelling_present = no; both recognizers get the frozen probe window "
                         "from the input-side screen (no human span exists)",
            "uncertain": "excluded from primary metrics; counted and reported",
            "per_letter_timing": "not collected; stays blank",
            "localization": "none: Stage A never uses a detector for the temporal span"},
        "pipeline": {
            "timing": "ffprobe best_effort_timestamp_time per decoded frame of the frozen clip; frame_index, "
                      "clip_time_s (PTS) and source_time_s (How2Sign START + PTS) logged separately; no resampling",
            "span_frames": "frames with start <= clip PTS < end",
            "landmarks": "one MediaPipe Holistic 0.10.9 pass (complexity 1) over the span frames, shared by both "
                         "recognizers",
            "hand_side": "human-labelled signing hand when left/right; otherwise the hand with more valid raised "
                         "frames in the span (tie: right); same hand for both recognizers",
            "keypoint_input": "OpenFS path unchanged (both raised hands, as upstream), frames with detected landmarks",
            "rgb_crop": "selected hand; square box centred on the landmark bbox, side 1.6 x max(w,h), min 64 px; "
                        "centred median over 5 detected frames; gaps <= 4 frames linearly interpolated "
                        "(status interpolated); longer gaps -> hand_missing, frame dropped from RGB input; box "
                        "shifted (not shrunk) inside the frame; resized to the recognizer's input size",
            "missing_hand": "logged per frame; if fewer than 8 usable frames remain, the recognizer abstains",
            "logged_per_item": ["blind_id", "source_video_id", "video_sha256", "span clip/source times", "frame_index "
                                "list", "clip_time_s list", "source_time_s list", "hand side and rule", "crop box per "
                                "frame + status", "landmark detection flags", "raw letter string", "candidates (if "
                                "the recognizer returns n-best)", "abstain reason", "runtime_s", "model/commit/"
                                "checkpoint sha"],
            "naming": "files and metadata carry blind_id only; no reference text, name or clip title",
            "implemented_in": "p0_1_stage_a_prepare.py frame_table / span_frames / choose_hand / crop_boxes"},
        "label_schema": LABEL_SCHEMA, "label_fields": LABEL_FIELDS,
        "label_procedure": "Step 1 blind: the reviewer sees only the blind-named clip. Step 2 (reference-conditioned) "
                           "is not part of Stage A scoring.",
        "candidate_set": {"file": "results/p0_1_stage_a_candidate_set.json", "items": len(cand["items"]),
                          "tier_counts": cand["tier_counts"]},
        "metrics": {
            "normalisation": "lowercase; keep a-z only (spaces, punctuation, digits removed) for both label and "
                             "output; a human '?' letter is kept as a wildcard that matches any single letter",
            "primary": {"CER": "sum of Levenshtein edits / sum of human letters over positive spans; an abstain "
                               "is scored as the empty string (all deletions)",
                        "word_exact": "fraction of positive spans whose normalised output equals the normalised "
                                      "human letters"},
            "secondary": {"abstain_rate": "abstains / spans (positives and negatives reported separately)",
                          "fpr_negatives": "fraction of negative items where the recognizer emits >= 2 letters on "
                                           "the probe window",
                          "coverage": "spans with a non-abstain output / spans",
                          "per_letter_confusion": "substitution pairs from the Levenshtein alignment",
                          "runtime_per_span_s": "median and max wall time per span"},
            "paired": "per-span CER difference (RGB - keypoint); wins / losses / ties (tie if |delta| < 0.05); "
                      "95 % bootstrap CI of the mean per-span difference, clustered by source video, 10,000 "
                      "resamples, seed 20261029",
            "subgroups": ["Uni-Sign already-correct controls (human letters appear as a token in the Uni-Sign "
                          "A_official output, derived after labelling)", "dev45 vs non-dev", "selection tier"],
            "control_subgroup_rule": "The 36-item selection does NOT use Uni-Sign output. After blind human labels "
                                     "return, an 'already-correct Uni-Sign control' subgroup may be defined by "
                                     "comparing the blinded human-confirmed letters against the previously saved "
                                     "Uni-Sign A_official output. The subgroup is analysis-only after labelling and "
                                     "cannot affect which 36 items were selected.",
            "not_used": "model self-confidence is never used as correctness or for abstain decisions"},
        "gates": {
            "G0_validity": "at least 12 positive spans with letters (confidence high/medium) and at least 8 "
                           "negatives; otherwise no verdict (insufficient labels)",
            "rgb_adds_value_all_of": {
                "G1_cer": "RGB corpus CER <= keypoint CER - 0.10 (absolute) AND the upper bound of the 95 % "
                          "cluster-bootstrap CI of the mean per-span CER difference (RGB - keypoint) < 0",
                "G2_word": "RGB whole-word exact accuracy >= keypoint whole-word exact accuracy",
                "G3_false_positives": "RGB FPR on negatives <= keypoint FPR + 0.10",
                "G4_breadth": "after removing the 2 spans with the largest RGB gain, RGB corpus CER is still < "
                              "keypoint CER, AND per-span wins >= 1.5 x losses"},
            "readable_at_known_spans": "the better recognizer reaches CER <= 0.35 AND whole-word exact >= 0.30 on "
                                       "positives; otherwise Stage A says: improve the recognizer first, postpone "
                                       "Stage B and fusion",
            "outcomes": {"RGB_ADDS_VALUE": "G0 and G1-G4 pass",
                         "NO_RGB_GAIN": "G0 passes and any of G1-G4 fails",
                         "INSUFFICIENT_LABELS": "G0 fails"},
            "fixed_before_results": "thresholds are fixed here, before any Stage A label or prediction exists, and "
                                    "must not change after results are seen"},
        "expansion_rule": "if Step-1 labels leave G0 unmet, label further items in this fixed order, in batches of 8: "
                          "remaining eligible clips by descending screen score (eligible_screen_table), each batch "
                          "taking up to 6 by score and 2 by salted hash; stop as soon as G0 is met or the 61-clip pool "
                          "is exhausted. Beyond that, a How2Sign test raw-video pool (outside the 128) needs new "
                          "keypoints and a separate approval. Items added this way are flagged expansion = true.",
        "blocked_on": ["blind Step-1 labels for the candidate set", "approval to install HandReader (and MiCT-RANet "
                       "if needed) in an isolated research venv", "approval to run both recognizers on the "
                       "confirmed spans"]}


if __name__ == "__main__":
    main()
