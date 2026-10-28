"""Task 2 Step 2 (Amendment 2, A2.1): range-fetch only the official Uni-Sign crop clips crop_test/<clip>.mp4 for the
A_official rows still UNRESOLVED, from the same HF release P0-12 used (ZechengLi19/Uni-Sign how2sign_rgb_format.zip.*),
addressed by P0-12 data/official_rgb_index_128.json. CRC32 is checked against the zip central directory; sha256, size,
byte range and the HF repo commit are recorded; frame count / fps / w_h are checked against P0-12
official_crop_ffprobe.csv. Clips go to a scratch folder and are never committed.

usage: python -I fetch_official_crops.py --scratch DIR --out work/official_crops.json
"""
import argparse, binascii, csv, hashlib, json, os, struct, subprocess, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
P012 = os.path.join(REPO, "docs/daily_report/10.06/asl-p0-12-unisign-pose-gap")
# split-zip layout, identical to P0-12 scripts/fetch_entries.py (KIND == 'rgb')
PART = 4294967296
SUF = [".zip.aa", ".zip.ab", ".zip.ac", ".zip.ad", ".zip.ae"]
SIZES = [PART] * 4 + [3010900187]
BASE = "https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_rgb_format%s"

sys.path.insert(0, os.path.join(REPO, "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402


def fetch(off, n, log):
    buf = b""
    while n > 0:
        pi, po = off // PART, off % PART
        take = min(n, SIZES[pi] - po)
        r = subprocess.run(["curl", "-sSL", "--fail", "-r", f"{po}-{po + take - 1}", BASE % SUF[pi]],
                           capture_output=True, check=True).stdout
        assert len(r) == take, (len(r), take)
        log.append({"url": BASE % SUF[pi], "range": f"{po}-{po + take - 1}"})
        buf += r; off += take; n -= take
    return buf


def repo_commit():
    h = subprocess.run(["curl", "-sSIL", BASE % SUF[0]], capture_output=True, text=True, check=True).stdout
    c = [l.split(":", 1)[1].strip() for l in h.splitlines() if l.lower().startswith("x-repo-commit:")]
    return c[0] if c else ""


def probe(path):
    s = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
         "stream=r_frame_rate,nb_read_frames,width,height", "-of", "json", path],
        capture_output=True, check=True, text=True).stdout)["streams"][0]
    return {"w_h": f"{s['width']}x{s['height']}", "r_frame_rate": s["r_frame_rate"], "frames": int(s["nb_read_frames"])}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--scratch", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    man = list(csv.DictReader(open(os.path.join(OUT, "input_manifest_45.csv"))))
    todo = [(r["review_id"], r["clip_id"], int(r["pose_frame_count"])) for r in man
            if r["preprocessing_domain"] == "A_official" and r["provenance_status"] == "UNRESOLVED"]
    assert_not_holdout([c for _, c, _ in todo])
    idx = json.load(open(os.path.join(P012, "data/official_rgb_index_128.json")))
    ref = {}
    for line in open(os.path.join(P012, "data/official_crop_ffprobe.csv")):
        c, w, h, fr, _, nb = line.strip().split(",")
        ref[c] = {"w_h": f"{w}x{h}", "r_frame_rate": fr, "frames": int(nb)}
    os.makedirs(a.scratch, exist_ok=True)
    commit = repo_commit()
    out = {}
    for rid, cid, n_pose in todo:
        e = idx[cid]
        assert e["name"] == f"crop_test/{cid}.mp4", e["name"]
        log = []
        h = fetch(e["lho"], 30, log)
        assert h[:4] == b"PK\x03\x04"
        nlen, elen = struct.unpack("<HH", h[26:30])
        comp = fetch(e["lho"] + 30 + nlen + elen, e["csz"], log)
        data = zlib.decompress(comp, -15) if e["method"] == 8 else comp
        assert len(data) == e["usz"], cid
        crc = binascii.crc32(data) & 0xffffffff
        assert crc == e["crc"], ("CRC MISMATCH", cid)
        dst = os.path.join(a.scratch, cid + ".mp4")
        open(dst, "wb").write(data)
        p = probe(dst)
        ok = p == ref[cid] and p["frames"] == n_pose
        out[rid] = {"review_id": rid, "clip_id": cid, "hf_repo": "ZechengLi19/Uni-Sign", "hf_repo_commit": commit,
                    "zip_entry": e["name"], "zip_local_header_offset": e["lho"], "compressed_size": e["csz"],
                    "size_bytes": len(data), "crc32": f"{crc:08x}", "crc32_matches_central_directory": True,
                    "sha256": hashlib.sha256(data).hexdigest(), "byte_ranges": log, "probe": p,
                    "p012_ffprobe": ref[cid], "a_pose_frames": n_pose, "probe_matches_p012_and_pose": ok}
        print(rid, cid, len(data), out[rid]["sha256"][:12], p, "OK" if ok else "PROBE MISMATCH", flush=True)
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
