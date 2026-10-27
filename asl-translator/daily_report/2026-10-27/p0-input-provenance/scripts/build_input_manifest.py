"""P0-1: assemble the 45-case x 2-domain input provenance manifest and apply the frozen status rules
(INPUT_PROVENANCE_PLAN.md + Amendment 1). Reads only already-produced evidence; no model, no video decoding.

Inputs: work/located_clips.json (locate_clips.py), work/sampling.jsonl (reproduce_sampling.py), How2Sign test CSVs,
how2sign_v2 subset TSVs, P0-12 official_crop_ffprobe.csv / segment_alignment_128.json /
crossframe_alignment_B_vs_C.json, P0-A case_provenance.csv.
Outputs: input_manifest_45.csv, selected_frames.jsonl, provenance_summary.json.
usage: python -I build_input_manifest.py
"""
import csv, hashlib, json, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
WORK = os.path.join(OUT, "work")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
P012 = os.path.join(REPO, "docs/daily_report/10.06/asl-p0-12-unisign-pose-gap")
P0A_PROV = os.path.join(REPO, "asl-translator/daily_report/2026-10-23/p0a-candidate-rerank/provenance/case_provenance.csv")
V2 = "asl-translator/data/public_benchmarks/how2sign_v2"
ORIG_CSV = os.path.expanduser("~/Desktop/curify/p018-work/downloads/how2sign_test.csv")
REAL_CSV = os.path.expanduser("~/Desktop/curify/visual-search-adhoc-asl-task-c/asl-translator/evaluation/experiments/"
                              "landmark_t5_1pct/local_run_10pct/raw_download/how2sign_realigned_test.csv")
TOL = 0.20
DECLARED = {"A_official": "realigned", "B_ours_5p39": "original"}
SELECTED_BY = {
    "B_ours_5p39": ("How2Sign 'Green Screen RGB clips (frontal view)' archive clip test_rgb_front_clips.zip:raw_videos/"
                    "<clip>.mp4, copied unchanged into how2sign_v2/videos (sha256 in how2sign_v2/manifest.csv); "
                    "P0-12 scripts/extract_rtmlib_lightweight.py on every frame (MANIFEST.csv row B_ours_5p39). The "
                    "interval is the dataset authors' cut; no repo code chose it"),
    "A_official": ("Official Uni-Sign How2Sign pose release (HF ZechengLi19/Uni-Sign how2sign_pose_format.zip, entry "
                   "test-pose-rtmpose-192/<clip>.pkl; P0-12 fetch_entries.py + make_condition_dirs.py), extracted by "
                   "the Uni-Sign authors from the official crop clip crop_test/<clip>.mp4. No repo code chose it"),
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tsv(path, s, e):
    assert "val" not in os.path.basename(path)
    return {r["SENTENCE_NAME"]: (float(r[s]), float(r[e])) for r in csv.DictReader(open(path), delimiter="\t")}


def rel(p):
    p = os.path.abspath(p)
    return os.path.relpath(p, REPO) if p.startswith(REPO) else p.replace(os.path.expanduser("~"), "~")


def main():
    loc = json.load(open(os.path.join(WORK, "located_clips.json")))
    samp = {(r["review_id"], r["domain"]): r for r in map(json.loads, open(os.path.join(WORK, "sampling.jsonl")))}
    prov = list(csv.DictReader(open(P0A_PROV)))
    orig, real = tsv(ORIG_CSV, "START", "END"), tsv(REAL_CSV, "START_REALIGNED", "END_REALIGNED")
    v2o = tsv(os.path.join(REPO, V2, "source_metadata/how2sign_test_original_subset_v2.tsv"), "START", "END")
    v2r = tsv(os.path.join(REPO, V2, "source_metadata/how2sign_test_realigned_subset_v2.tsv"), "START_REALIGNED", "END_REALIGNED")
    crop = {}
    for line in open(os.path.join(P012, "data/official_crop_ffprobe.csv")):
        c, w, h, fr, dur, nb = line.strip().split(",")
        n, d = fr.split("/"); crop[c] = {"w_h": f"{w}x{h}", "fps": float(n) / float(d), "frames": int(nb), "dur": float(dur)}
    seg = json.load(open(os.path.join(P012, "data/segment_alignment_128.json")))
    xf = json.load(open(os.path.join(P012, "data/crossframe_alignment_B_vs_C.json")))["per_clip"]
    v2man = {r["how2sign_id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "manifest.csv")))}
    files = {
        "orig_csv": (rel(ORIG_CSV), sha256(ORIG_CSV)), "real_csv": (rel(REAL_CSV), sha256(REAL_CSV)),
        "v2_orig_tsv": (f"{V2}/source_metadata/how2sign_test_original_subset_v2.tsv",
                        sha256(os.path.join(REPO, V2, "source_metadata/how2sign_test_original_subset_v2.tsv"))),
        "v2_real_tsv": (f"{V2}/source_metadata/how2sign_test_realigned_subset_v2.tsv",
                        sha256(os.path.join(REPO, V2, "source_metadata/how2sign_test_realigned_subset_v2.tsv"))),
    }
    rows, frames_out = [], []
    for p in prov:
        rid, cid = p["review_id"], p["clip_id"]
        L = loc[rid]
        fps = L["raw_probe"]["fps"]
        o, rl = orig.get(cid), real.get(cid)
        v2src = ("v2_real_tsv", v2r[cid]) if cid in v2r else ("v2_orig_tsv", v2o.get(cid))
        b_start = L["best_offset_frames"] / fps if L.get("unique_match") else None
        for dom in ("A_official", "B_ours_5p39"):
            s = samp[(rid, dom)]
            n = s["pose_frames"]
            reasons, notes = [], []
            # (b) frame counts
            if dom == "B_ours_5p39":
                vid_frames, eff_fps = L["clip_probe"]["frames"], L["clip_probe"]["fps"]
                input_video = f"{V2}/videos/{cid}.mp4"; input_video_sha = L["clip_sha256"]; input_w_h = L["clip_probe"]["w_h"]
            else:
                cr = crop.get(cid, {})
                vid_frames, eff_fps = cr.get("frames"), cr.get("fps")
                input_video = f"official crop clip crop_test/{cid}.mp4 (HF zip entry; not stored locally)"
                input_video_sha = ""; input_w_h = cr.get("w_h", "")
            frames_ok = vid_frames == n
            if not frames_ok:
                reasons.append(f"pose frames {n} != input video frames {vid_frames}")
            if eff_fps != fps:
                notes.append(f"input fps {eff_fps} != raw fps {fps}")
            # (c) slice
            start = method = None; evidence = ""
            if dom == "B_ours_5p39":
                method = "measured: pixel match of the input clip inside the raw source (Amendment 1)"
                evidence = (f"offset {L['best_offset_frames']} fr; motion r {L['motion_r_best']} (next outside ±5: "
                            f"{L['motion_r_next_outside_5']}); norm MAE {L['norm_mae_best']} (median {L['norm_mae_median']}); "
                            f"norm-MAE offset {L['best_offset_norm_mae']}; unique={L['unique_match']}")
                if b_start is None:
                    reasons.append("B clip location not unique")
                else:
                    start = b_start
            else:
                method = "derived: B measured start + P0-12 B-vs-C cross-frame offset (C = same official crop clip as A)"
                x = xf.get(cid)
                if x is None:
                    reasons.append("no B-vs-C cross-frame alignment (A and B windows do not overlap); A slice not measurable locally")
                elif b_start is None:
                    reasons.append("B slice unresolved, so A cannot be derived")
                elif x["resid_body"] > 0.02:
                    reasons.append(f"B-vs-C alignment residual {x['resid_body']:.4f} > 0.02")
                else:
                    sh = int(round((seg[cid]["ours_start"] - seg[cid]["realigned_start"]) * crop[cid]["fps"]))
                    k = sh + x["offset_frames"]
                    start = b_start - k / fps
                    evidence = (f"C index = B index + {sh} (shift) + {x['offset_frames']} (best offset) -> A frame 0 = B frame "
                                f"{-k}; resid_body {x['resid_body']:.4f}, resid_hands {x['resid_hands']:.4f} shoulder widths, "
                                f"{x['n_frames']} frames compared")
            end = start + n / fps if start is not None else None
            d = {}
            for lab, iv in (("original", o), ("realigned", rl)):
                if start is not None and iv:
                    d[lab] = (round(start - iv[0], 3), round(end - iv[1], 3))
            matches = [lab for lab, (ds, de) in d.items() if abs(ds) <= TOL and abs(de) <= TOL]
            # (a) / (d) hashes
            if not (s["pose_sha_eq_checksums"] and s["pose_sha_eq_p0a"]):
                reasons.append("pose sha256 differs from a stored hash")
            if not (s["frame_idx_reproduced"] and s["kps_reproduced"]):
                reasons.append("selected-index or model-input hash not reproduced")
            hash_bad = any("sha256" in x or "hash" in x for x in reasons)
            if start is None or not frames_ok:
                status = "UNRESOLVED"
            elif hash_bad:
                status = "MISMATCH"
            elif DECLARED[dom] in matches:
                status = "VERIFIED"
            else:
                status = "MISMATCH"
                reasons.append(f"actual slice does not match the declared {DECLARED[dom]} timing within {TOL} s; "
                               f"matches: {', '.join(matches) if matches else 'neither annotation'}")
            idx = s["selected_indices"]
            ts = [round(start + i / fps, 4) for i in idx] if start is not None else []
            if v2man[cid]["selection_reason"].startswith("replacement:realigned"):
                notes.append("how2sign_v2 'RESCUED via re-aligned-file timing': clip duration matched the realigned TSV, "
                             "so the v2 benchmark and P0-A case_provenance record realigned times in the 'original' column")
            rows.append({
                "review_id": rid, "clip_id": cid, "preprocessing_domain": dom, "declared_timing_source": DECLARED[dom],
                "source_video": L["source_video"], "source_video_sha256": L["source_video_sha256"], "source_fps": fps,
                "input_video": input_video, "input_video_sha256": input_video_sha, "input_w_h": input_w_h,
                "input_video_frames": vid_frames,
                "annotation_original_file": files["orig_csv"][0], "annotation_original_sha256": files["orig_csv"][1],
                "annotation_original_type": "How2Sign test 'English Translation (original)' (speech-aligned)",
                "original_start": o[0] if o else "", "original_end": o[1] if o else "",
                "annotation_realigned_file": files["real_csv"][0], "annotation_realigned_sha256": files["real_csv"][1],
                "annotation_realigned_type": "How2Sign test 'English Translation (manually re-aligned)'",
                "realigned_start": rl[0] if rl else "", "realigned_end": rl[1] if rl else "",
                "v2_timing_file": files[v2src[0]][0], "v2_timing_sha256": files[v2src[0]][1],
                "v2_start": v2src[1][0] if v2src[1] else "", "v2_end": v2src[1][1] if v2src[1] else "",
                "p0a_recorded_orig_start": p["orig_start"], "p0a_recorded_orig_end": p["orig_end"],
                "p0a_recorded_realigned_start": p["realigned_start"], "p0a_recorded_realigned_end": p["realigned_end"],
                "actual_slice_start_s": round(start, 4) if start is not None else "",
                "actual_slice_end_s": round(end, 4) if end is not None else "",
                "actual_duration_s": round(n / fps, 4), "slice_method": method, "slice_evidence": evidence,
                "slice_selected_by": SELECTED_BY[dom],
                "delta_vs_original_start_end_s": f"{d['original'][0]}/{d['original'][1]}" if "original" in d else "",
                "delta_vs_realigned_start_end_s": f"{d['realigned'][0]}/{d['realigned'][1]}" if "realigned" in d else "",
                "matches_annotation_within_0p20s": ";".join(matches) if start is not None else "",
                "pose_file": s["pose_path"], "pose_sha256": s["pose_sha256"], "pose_frame_count": n,
                "pose_frames_eq_input_video": frames_ok, "effective_fps": fps,
                "timestamp_mapping": "t_i = actual_slice_start_s + i / effective_fps (PKL has no start/end keys)",
                "first_pose_ts_s": round(start, 4) if start is not None else "",
                "last_pose_ts_s": round(start + (n - 1) / fps, 4) if start is not None else "",
                "max_frames": s["max_length"], "subsampled_gt256": s["subsampled"], "sampling_seed": s["clip_seed"],
                "selected_frame_count": s["selected_count"], "selected_first_last_index": f"{idx[0]}/{idx[-1]}",
                "selected_first_last_ts_s": f"{ts[0]}/{ts[-1]}" if ts else "",
                "selected_indices_sha256": s["frame_idx_sha256"],
                "selected_timestamps_sha256": hashlib.sha256(json.dumps(ts).encode()).hexdigest() if ts else "",
                "stored_frame_idx_sha256": s["stored_frame_idx_sha256"], "stored_model_input_kps_sha256": s["stored_kps_sha256"],
                "reproduced_model_input_kps_sha256": s["kps_sha256"],
                "model_input_hash_reproduced": s["frame_idx_reproduced"] and s["kps_reproduced"],
                "provenance_status": status, "status_reasons": " | ".join(reasons), "notes": " | ".join(notes)})
            frames_out.append({"review_id": rid, "clip_id": cid, "domain": dom, "selected_indices": idx,
                               "selected_timestamps_s": ts})
    cols = list(rows[0])
    with open(os.path.join(OUT, "input_manifest_45.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "selected_frames.jsonl"), "w") as f:
        for r in frames_out:
            f.write(json.dumps(r) + "\n")
    case = {}
    order = {"UNRESOLVED": 2, "MISMATCH": 1, "VERIFIED": 0}
    for r in rows:
        case[r["review_id"]] = max(case.get(r["review_id"], "VERIFIED"), r["provenance_status"], key=order.get)
    summ = {
        "generated": "2026-10-27", "rows": len(rows), "cases": len(case),
        "row_status": {d: dict(Counter(r["provenance_status"] for r in rows if r["preprocessing_domain"] == d))
                       for d in ("A_official", "B_ours_5p39")},
        "case_status_worst_of_domains": dict(Counter(case.values())),
        "cases_by_status": {s: sorted(k for k, v in case.items() if v == s) for s in order},
        "rows_by_status": {s: sorted(f"{r['review_id']}:{r['preprocessing_domain']}" for r in rows if r["provenance_status"] == s)
                           for s in order},
        "model_input_hash_reproduced_rows": sum(r["model_input_hash_reproduced"] for r in rows),
        "pose_frames_eq_input_video_rows": sum(r["pose_frames_eq_input_video"] for r in rows),
        "subsampled_rows": sum(r["subsampled_gt256"] for r in rows),
        "annotation_files": {k: {"path": v[0], "sha256": v[1]} for k, v in files.items()},
        "tolerance_s": TOL, "declared_timing": DECLARED,
        "R10": [{k: r[k] for k in ("preprocessing_domain", "actual_slice_start_s", "actual_slice_end_s", "original_start",
                                   "original_end", "realigned_start", "realigned_end", "delta_vs_realigned_start_end_s",
                                   "matches_annotation_within_0p20s", "pose_frame_count", "selected_frame_count",
                                   "selected_first_last_ts_s", "model_input_hash_reproduced", "provenance_status",
                                   "status_reasons")} for r in rows if r["review_id"] == "R10"],
    }
    json.dump(summ, open(os.path.join(OUT, "provenance_summary.json"), "w"), indent=1)
    print(json.dumps({k: summ[k] for k in ("row_status", "case_status_worst_of_domains", "cases_by_status")}, indent=1))


if __name__ == "__main__":
    main()
