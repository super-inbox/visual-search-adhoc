"""P0-18 DEV: index one directory of Uni-Sign's official How2Sign crop archive (metadata only, no video bytes).

Same method as P0-16 index_crop_val.py: range-fetch the last 8 MiB of how2sign_rgb_format.zip.ae (zip64 central
directory) and write name, compressed size, local-header offset, CRC-32 for every entry under PREFIX. Used to build
the dev (test) index for the H18 runner's dry run; the H18 index is P0-16's frozen holdout/crop_val_index.tsv.

Usage: python3 -I index_crop_archive.py PREFIX OUT.tsv      (e.g. crop_test/)
"""
import collections, struct, sys, urllib.request

URL = "https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_rgb_format.zip.ae"
PART_SIZE = 3010900187           # .aa-.ad are 4294967296 bytes each; .ae is the last part
TAIL = 8 << 20
PREFIX, OUT = sys.argv[1], sys.argv[2]
assert PREFIX != "crop_val/", "the val index is frozen by P0-16"

req = urllib.request.Request(URL, headers={"Range": f"bytes={PART_SIZE - TAIL}-{PART_SIZE - 1}"})
b = urllib.request.urlopen(req, timeout=120).read()
assert len(b) == TAIL, len(b)
z64 = b.rfind(b"PK\x06\x06")
_, _, _, _, _, _, _, n_entries, cd_size, cd_off = struct.unpack("<IQHHIIQQQQ", b[z64:z64 + 56])
cd = b[z64 - cd_size:z64]
rows, p = [], 0
while p < len(cd):
    (_, _, _, _, _, _, _, crc, csz, usz, nlen, elen, clen, _, _, _, lho) = struct.unpack("<IHHHHHHIIIHHHHHII", cd[p:p + 46])
    name = cd[p + 46:p + 46 + nlen].decode("utf-8")
    extra, q = cd[p + 46 + nlen:p + 46 + nlen + elen], 0
    while q < len(extra):
        hid, hsz = struct.unpack("<HH", extra[q:q + 4]); body, k = extra[q + 4:q + 4 + hsz], 0
        if hid == 1:
            vals = {"usz": usz, "csz": csz, "lho": lho}
            for fld in ("usz", "csz", "lho"):
                if vals[fld] == 0xFFFFFFFF:
                    vals[fld] = struct.unpack("<Q", body[k:k + 8])[0]; k += 8
            usz, csz, lho = vals["usz"], vals["csz"], vals["lho"]
        q += 4 + hsz
    rows.append((name, csz, lho, crc))
    p += 46 + nlen + elen + clen
assert len(rows) == n_entries
dirs = collections.Counter(n.split("/")[0] for n, *_ in rows if not n.endswith("/"))
val = sorted(r for r in rows if r[0].startswith(PREFIX) and not r[0].endswith("/"))
with open(OUT, "w") as f:
    f.write("name\tcompressed_size\tlocal_header_offset\tcrc32\n")
    f.write("".join(f"{n}\t{c}\t{o}\t{crc:08x}\n" for n, c, o, crc in val))
print({"entries": n_entries, "dirs": dict(dirs), PREFIX: len(val), "GB": round(sum(r[1] for r in val) / 1e9, 3)})
