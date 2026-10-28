"""P0-1: independent consistency checks on input_manifest_45.csv. Exits non-zero on any failure.

Re-hashes every pose PKL and both annotation CSVs, re-derives the selected-index / timestamp hashes from
selected_frames.jsonl, re-applies the frozen status rules from the CSV columns, and checks the row set
(45 cases x {A_official, B_ours_5p39}). No video decoding, no model.
usage: python -I verify_input_manifest.py
"""
import csv, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
TOL = 0.20
DECLARED = {"A_official": "realigned", "B_ours_5p39": "original"}


def sha256(p):
    h = hashlib.sha256()
    with open(os.path.expanduser(p) if p.startswith("~") else os.path.join(REPO, p), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    rows = list(csv.DictReader(open(os.path.join(OUT, "input_manifest_45.csv"))))
    frames = {(r["review_id"], r["domain"]): r for r in map(json.loads, open(os.path.join(OUT, "selected_frames.jsonl")))}
    fails = []
    def check(ok, msg):
        if not ok:
            fails.append(msg)
    keys = {(r["review_id"], r["preprocessing_domain"]) for r in rows}
    check(len(rows) == 90 and len(keys) == 90, f"expected 90 unique rows, got {len(rows)}/{len(keys)}")
    check({k[0] for k in keys} == {f"R{i:02d}" for i in range(1, 46)}, "review ids are not exactly R01-R45")
    ann = {}
    for r in rows:
        k = (r["review_id"], r["preprocessing_domain"]); tag = f"{k[0]}:{k[1]}"
        check(sha256(r["pose_file"]) == r["pose_sha256"], f"{tag} pose sha256")
        for col in ("annotation_original", "annotation_realigned"):
            f = r[f"{col}_file"]
            ann.setdefault(f, sha256(f)); check(ann[f] == r[f"{col}_sha256"], f"{tag} {col} sha256")
        fr = frames[k]
        check(hashlib.sha256(json.dumps(fr["selected_indices"]).encode()).hexdigest() == r["selected_indices_sha256"],
              f"{tag} selected index hash")
        check(r["selected_indices_sha256"] == r["stored_frame_idx_sha256"], f"{tag} index hash != stored")
        check(len(fr["selected_indices"]) == int(r["selected_frame_count"]) == min(256, int(r["pose_frame_count"])),
              f"{tag} selected count")
        if fr["selected_timestamps_s"]:
            check(hashlib.sha256(json.dumps(fr["selected_timestamps_s"]).encode()).hexdigest() == r["selected_timestamps_sha256"],
                  f"{tag} timestamp hash")
            fps, s0 = float(r["effective_fps"]), float(r["actual_slice_start_s"])
            check(all(abs(t - (s0 + i / fps)) < 1e-3 for i, t in zip(fr["selected_indices"], fr["selected_timestamps_s"])),
                  f"{tag} timestamps != start + i/fps")
        # re-apply the frozen rules
        resolved = r["actual_slice_start_s"] != "" and r["pose_frames_eq_input_video"] == "True"
        hashes_ok = r["model_input_hash_reproduced"] == "True" and r["reproduced_model_input_kps_sha256"] == r["stored_model_input_kps_sha256"]
        match = []
        if resolved:
            s0, e0 = float(r["actual_slice_start_s"]), float(r["actual_slice_end_s"])
            for lab in ("original", "realigned"):
                if r[f"{lab}_start"]:
                    if abs(s0 - float(r[f"{lab}_start"])) <= TOL and abs(e0 - float(r[f"{lab}_end"])) <= TOL:
                        match.append(lab)
        expect = ("UNRESOLVED" if not resolved else "MISMATCH" if not hashes_ok
                  else "VERIFIED" if DECLARED[k[1]] in match else "MISMATCH")
        check(expect == r["provenance_status"], f"{tag} status {r['provenance_status']} != re-derived {expect}")
    if fails:
        print(f"FAIL ({len(fails)}):"); [print(" -", f) for f in fails]; sys.exit(1)
    print(f"OK: {len(rows)} rows; pose, annotation, index and timestamp hashes and status rules all re-verified")


if __name__ == "__main__":
    main()
