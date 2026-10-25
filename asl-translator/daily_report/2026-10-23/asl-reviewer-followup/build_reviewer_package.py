"""Build the local ASL-fluent reviewer package for the open P0-B (R02/R05/R35) and P0-C (R26/R29) blockers.

Cuts short full-frame clips from the How2Sign TEST raw videos, writes the clip manifest and the blank label sheet, and
assembles a two-step local package:
  package_local/step1_blind/    clips + instructions + blank labels + manifest + SHA256SUMS (send first)
  package_local/step2_unblind/  reference / target sentences (send only after the step-1 labels are returned)
Videos stay local (CC BY-NC 4.0; package_local/ is git-excluded). Never opens val / H18 / H19 material.

usage:
  python -I build_reviewer_package.py build           # cut clips, write manifest, (re)write blank labels, build package
  python -I build_reviewer_package.py derive LABELS   # after review only: R26 containment check vs the official window
"""
import csv, hashlib, json, os, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REPORT = os.path.dirname(HERE)
PKG = os.path.join(HERE, "package_local")
WORK = os.path.join(PKG, "_src")  # extracted raw videos, deleted after the build
TEST_ZIP = os.path.expanduser("~/Desktop/curify/p018-work/downloads/test_raw_videos.zip")
TEST_CSV = os.path.expanduser("~/Desktop/curify/p018-work/downloads/how2sign_test.csv")
PROV = os.path.join(REPORT, "p0a-candidate-rerank", "provenance", "case_provenance.csv")
P012 = "docs/daily_report/10.06/asl-p0-12-unisign-pose-gap/artifacts/prepared_inputs"

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402

DOM_OLD = "B_ours_5p39: old preprocessing (original timing; full frame, as the model saw it)"
DOM_OFF = "A_official: official preprocessing (realigned timing; shown FULL FRAME; the official crop is not available as video)"
DOM_CTX = "source context: full-frame raw source span (no preprocessing window)"

# P0-B: both matched windows per case, read from case_provenance.csv. P0-C: fixed context spans (2026-10-24 request).
P0B = ["R02", "R05", "R35"]
P0C = {"R26": ("G3EfBFwsOpE_3-10-rgb_front", 11.75, 16.75), "R29": ("92V3oH63zbQ_5-1-rgb_front", 5.00, 25.80)}
P0C_NEIGHBOURS = {"R26": ("G3EfBFwsOpE_2", "G3EfBFwsOpE_4"), "R29": ("92V3oH63zbQ_4", "92V3oH63zbQ_6")}
# Team-side only (never written into the reviewer package): used by `derive` after the review.
R26_OFFICIAL_WINDOW = (15.15, 16.62)

LABEL_COLS = [
    # provenance (pre-filled)
    "row_id", "review_id", "task", "clip_id", "video_file", "preprocessing_domain", "source_video",
    "source_start_s", "source_end_s", "clip_duration_s", "source_video_sha256", "clip_sha256", "span_no",
    # STEP 1 - blind (P0-B rows)
    "fs_present", "fs_start_s", "fs_end_s", "letters_seen_blind", "fs_type", "hand_visibility",
    # STEP 1 - blind (P0-C rows)
    "utterance_boundaries_blind_s",
    "notes_blind",
    # STEP 2 - after opening step2_unblind (P0-B rows)
    "reference_name_after_unblind", "matches_reference_name",
    # STEP 2 - after opening step2_unblind (P0-C rows)
    "target_found", "target_start_s", "target_end_s", "target_confidence",
    "notes_after_unblind",
    # reviewer
    "reviewer_id", "asl_background", "step1_completed_at", "step2_completed_at",
]
PROV_COLS = LABEL_COLS[:LABEL_COLS.index("span_no")]
REVIEWER_COLS = LABEL_COLS[LABEL_COLS.index("span_no") + 1:]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def guard_path(p):
    low = os.path.basename(p).lower()
    if "val" in low or "h18" in low or "h19" in low:
        raise SystemExit(f"refusing to open holdout/val path: {p}")
    return p


def fix_text(s):  # the downloaded test CSV has cp1252/UTF-8 mojibake in apostrophes
    for enc in ("cp1252", "latin-1"):
        try:
            return s.encode(enc).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return s


def sentences():
    with open(guard_path(TEST_CSV), encoding="utf-8") as f:
        return {r["SENTENCE_ID"] + "|" + r["VIDEO_NAME"]: fix_text(r["SENTENCE"]) for r in csv.DictReader(f, delimiter="\t")}


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_read_frames", "-of", "json", path],
                         capture_output=True, check=True, text=True).stdout
    s = json.loads(out)["streams"][0]; n, d = map(int, s["r_frame_rate"].split("/"))
    return s["width"], s["height"], n / d, int(s["nb_read_frames"])


def cut(src, a, b, dst):
    # Re-encode (frame-accurate start), native resolution and fps, no audio, no overlays.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", src, "-t", f"{b - a:.3f}", "-an",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-map_metadata", "-1", dst], check=True)


def rows_spec():
    prov = {r["review_id"]: r for r in csv.DictReader(open(PROV))}
    spec = []
    for rid in P0B:
        p = prov[rid]; vid = p["clip_id"].split("_")[0]; vn = p["clip_id"].split("-", 1)[1]
        src = f"{vid}-{vn}.mp4"
        spec.append(dict(row_id=f"{rid}-old", review_id=rid, task="P0-B", clip_id=p["clip_id"], src=src,
                         a=float(p["orig_start"]), b=float(p["orig_end"]), dom=DOM_OLD,
                         pkl=f"{P012}/B_ours_5p39/test-pose-rtmpose-192/{p['clip_id']}.pkl"))
        spec.append(dict(row_id=f"{rid}-official", review_id=rid, task="P0-B", clip_id=p["clip_id"], src=src,
                         a=float(p["realigned_start"]), b=float(p["realigned_end"]), dom=DOM_OFF,
                         pkl=f"{P012}/A_official/test-pose-rtmpose-192/{p['clip_id']}.pkl"))
    for rid, (cid, a, b) in P0C.items():
        vid = cid.split("_")[0]; vn = cid.split("-", 1)[1]
        spec.append(dict(row_id=f"{rid}-context", review_id=rid, task="P0-C", clip_id=cid, src=f"{vid}-{vn}.mp4",
                         a=a, b=b, dom=DOM_CTX, pkl=""))
    return spec


def labels_blank(path):
    if not os.path.exists(path):
        return True
    return all(not (r.get(c) or "").strip() for r in csv.DictReader(open(path)) for c in REVIEWER_COLS)


def build():
    spec = rows_spec()
    assert_not_holdout(sorted({s["clip_id"] for s in spec}))
    labels_path = os.path.join(HERE, "reviewer_labels.csv")
    if not labels_blank(labels_path):
        raise SystemExit("reviewer_labels.csv already has reviewer answers - refusing to overwrite")
    step1, step2 = os.path.join(PKG, "step1_blind"), os.path.join(PKG, "step2_unblind")
    for d in (WORK, os.path.join(step1, "clips"), step2):
        os.makedirs(d, exist_ok=True)

    srcs = sorted({s["src"] for s in spec})
    subprocess.run(["unzip", "-o", "-j", "-q", guard_path(TEST_ZIP)] + [f"raw_videos/{s}" for s in srcs] + ["-d", WORK],
                   check=True)
    src_sha = {s: sha256(os.path.join(WORK, s)) for s in srcs}

    manifest = []
    for s in spec:
        clip = f"{s['row_id']}.mp4"; dst = os.path.join(step1, "clips", clip)
        cut(os.path.join(WORK, s["src"]), s["a"], s["b"], dst)
        w, h, fps, n = probe(dst)
        pkl_abs = os.path.join(REPO, s["pkl"]) if s["pkl"] else ""
        manifest.append(dict(
            row_id=s["row_id"], review_id=s["review_id"], task=s["task"], clip_id=s["clip_id"], video_file=f"clips/{clip}",
            preprocessing_domain=s["dom"], source_video=f"raw_videos/{s['src']}", source_zip=os.path.basename(TEST_ZIP),
            source_start_s=f"{s['a']:.2f}", source_end_s=f"{s['b']:.2f}", clip_duration_s=f"{n / fps:.3f}",
            clip_fps=f"{fps:g}", clip_w_h=f"{w}x{h}", clip_frames=n, source_video_sha256=src_sha[s["src"]],
            clip_sha256=sha256(dst), clip_bytes=os.path.getsize(dst), p012_model_input_pkl=s["pkl"],
            p012_model_input_pkl_sha256=sha256(pkl_abs) if pkl_abs and os.path.exists(pkl_abs) else ""))
    mcols = list(manifest[0])
    for path in (os.path.join(HERE, "reviewer_package_manifest.csv"), os.path.join(step1, "reviewer_package_manifest.csv")):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=mcols, lineterminator="\n"); w.writeheader(); w.writerows(manifest)

    with open(labels_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LABEL_COLS, lineterminator="\n"); w.writeheader()
        for m in manifest:
            w.writerow({**{c: m[c] for c in PROV_COLS}, "span_no": "1"})
    shutil.copy(labels_path, os.path.join(step1, "reviewer_labels.csv"))
    shutil.copy(os.path.join(HERE, "reviewer_instructions.md"), os.path.join(step1, "reviewer_instructions.md"))

    # Step 2: reference text only. No timings, no window boundaries, no hypotheses.
    S = sentences()
    def sent(sid, cid): return S[sid + "|" + cid.split("_")[0] + "-" + cid.split("-", 1)[1]]
    lines = ["# Step 2 - unblinded references", "",
             "Open this file **only after** every Step 1 field in `reviewer_labels.csv` is saved and "
             "`step1_completed_at` is filled. Do not change Step 1 answers; add any second thoughts in "
             "`notes_after_unblind`.", "", "## P0-B (rows R02-*, R05-*, R35-*)", "",
             "For each case: the English reference sentence for the clip. Fill `reference_name_after_unblind` with the "
             "person name in it and `matches_reference_name` (yes / partly / no / cant_tell) for each of your Step 1 "
             "spans.", ""]
    for rid in P0B:
        cid = next(s["clip_id"] for s in spec if s["review_id"] == rid)
        lines += [f"- **{rid}**: \"{sent(cid.split('-')[0], cid)}\""]
    lines += ["", "## P0-C (rows R26-context, R29-context)", "",
              "Target = the sentence we need located. For orientation only, the sentences said immediately before and "
              "after it are listed (their order in the original English; their signed order may differ). Fill "
              "`target_found` (yes / partly / no / unsure), `target_start_s`, `target_end_s` (seconds from the start of "
              "the context clip) and `target_confidence` (high / medium / low).", ""]
    for rid, (cid, _, _) in P0C.items():
        prev, nxt = P0C_NEIGHBOURS[rid]
        lines += [f"### {rid}", "", f"- Before: \"{sent(prev, cid)}\"",
                  f"- **Target: \"{sent(cid.split('-')[0], cid)}\"**", f"- After: \"{sent(nxt, cid)}\"", ""]
    open(os.path.join(step2, "UNBLIND_REFERENCES.md"), "w").write("\n".join(lines))

    for d in (step1, step2):
        files = sorted(os.path.relpath(os.path.join(r, f), d) for r, _, fs in os.walk(d) for f in fs if f != "SHA256SUMS")
        open(os.path.join(d, "SHA256SUMS"), "w").write("".join(f"{sha256(os.path.join(d, f))}  {f}\n" for f in files))
        zp = d + ".zip"
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
            for f in files + ["SHA256SUMS"]:  # fixed timestamp/permissions so a rebuild gives a byte-identical zip
                zi = zipfile.ZipInfo(os.path.join(os.path.basename(d), f), date_time=(2026, 10, 24, 0, 0, 0))
                zi.external_attr = 0o644 << 16
                with open(os.path.join(d, f), "rb") as fh:
                    z.writestr(zi, fh.read())
    shutil.rmtree(WORK)
    print(json.dumps({"clips": len(manifest), "step1_zip_bytes": os.path.getsize(os.path.join(PKG, "step1_blind.zip")),
                      "step2_zip_bytes": os.path.getsize(os.path.join(PKG, "step2_unblind.zip")),
                      "clip_bytes_total": sum(m["clip_bytes"] for m in manifest)}, indent=1))


def derive(labels):
    """After the review: is the reviewer-marked R26 target signing fully inside the official window (source seconds)?"""
    for r in csv.DictReader(open(labels)):
        if r["row_id"] != "R26-context":
            continue
        if not (r["target_start_s"].strip() and r["target_end_s"].strip()):
            print("R26: target span not marked"); continue
        off = float(r["source_start_s"]); a, b = off + float(r["target_start_s"]), off + float(r["target_end_s"])
        lo, hi = R26_OFFICIAL_WINDOW
        print(f"R26 target (source s) {a:.2f}-{b:.2f}; official {lo:.2f}-{hi:.2f}; "
              f"fully_contained={lo <= a and b <= hi}; overlap_s={max(0.0, min(b, hi) - max(a, lo)):.2f}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["build"]:
        build()
    elif sys.argv[1:2] == ["derive"] and len(sys.argv) == 3:
        derive(sys.argv[2])
    else:
        raise SystemExit(__doc__)
