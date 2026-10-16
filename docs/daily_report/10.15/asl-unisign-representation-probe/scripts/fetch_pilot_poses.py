"""P0-14 Stage 2: pick a small pilot (whole source videos, train + clean test) and range-fetch only those PKLs
from the official archive (no full download). Every entry is CRC-32 verified against the zip central directory.

Selection is deterministic (seed) and reads only the frozen manifest: shuffle probe_train videos and take whole
videos until >= N_TRAIN clips; same for test_clean videos until >= N_TEST clips. Output manifest keeps manifest order.

Usage: python3 -I fetch_pilot_poses.py PROBE_DIR OUT_POSE_DIR OUT_PILOT_MANIFEST [N_TRAIN=300] [N_TEST=100]
"""
import binascii, csv, os, random, struct, subprocess, sys, zlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

D, out_dir, out_man = sys.argv[1:4]
N_TRAIN = int(sys.argv[4]) if len(sys.argv) > 4 else 300
N_TEST = int(sys.argv[5]) if len(sys.argv) > 5 else 100
SEED = 20261015 + 14

PART = 2147483648
SUF = [".zip.00", ".zip.01", ".zip.02", ".zip.03"]
SIZES = [PART] * 3 + [2023023631]
BASE = "https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_pose_format%s"

def fetch(off, n):
    buf = b""
    while n > 0:
        pi, po = off // PART, off % PART
        take = min(n, SIZES[pi] - po)
        r = subprocess.run(["curl", "-sSL", "--fail", "--retry", "8", "--retry-all-errors", "--retry-delay", "5",
                            "-r", f"{po}-{po + take - 1}", BASE % SUF[pi]], capture_output=True, check=True).stdout
        assert len(r) == take, (len(r), take)
        buf += r; off += take; n -= take
    return buf

man = list(csv.DictReader(open(os.path.join(D, "splits", "manifest.csv"))))
arch = {r["clip_id"]: r for r in csv.DictReader(open(os.path.join(D, "audit", "official_pose_archive_index.csv")))}

def pick(role, n):
    by = defaultdict(list)
    for r in man:
        if r["role"] == role:
            by[r["group"]].append(r["clip_id"])
    vids = sorted(by); random.Random(SEED).shuffle(vids)
    chosen, k = set(), 0
    for v in vids:
        if k >= n:
            break
        chosen |= set(by[v]); k += len(by[v])
    return chosen

sel = pick("probe_train", N_TRAIN) | pick("test_clean", N_TEST)
rows = [r for r in man if r["clip_id"] in sel]
with open(out_man, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

os.makedirs(out_dir, exist_ok=True)

def get(cid):
    e = arch[cid]
    dst = os.path.join(out_dir, cid + ".pkl")
    if os.path.exists(dst) and os.path.getsize(dst) == int(e["usz"]):
        data = open(dst, "rb").read()
    else:
        h = fetch(int(e["lho"]), 30)
        assert h[:4] == b"PK\x03\x04", cid
        nlen, elen = struct.unpack("<HH", h[26:30])
        comp = fetch(int(e["lho"]) + 30 + nlen + elen, int(e["csz"]))
        data = zlib.decompress(comp, -15) if int(e["method"]) == 8 else comp
        assert len(data) == int(e["usz"]), cid
    assert (binascii.crc32(data) & 0xFFFFFFFF) == int(e["crc"]), ("CRC MISMATCH", cid)
    if not os.path.exists(dst):
        open(dst, "wb").write(data)
    return cid, e["dir"], len(data)

with ThreadPoolExecutor(6) as ex:
    got = list(ex.map(get, [r["clip_id"] for r in rows]))
from collections import Counter
print("pilot clips", len(rows), Counter(r["role"] for r in rows), "videos", len({r["group"] for r in rows}))
print("fetched + CRC ok", len(got), Counter(d for _, d, _ in got), "MB", round(sum(n for *_, n in got) / 1e6, 1))
