#!/usr/bin/env python3
"""Blind visual anchoring helper for the 5 UNRESOLVED source positions (2026-10-28). CPU only, no model.

The analyst judges contact sheets by eye. This helper only renders frames and keeps the time key away from the analyst:
  prepare  query sheet (the unresolved input clip) + coarse sheets covering the WHOLE raw source video
           (every 12th frame at 24 fps / 15th at 30 fps = 2 per second, one-row overlap between sheets).
           Sheets get random 3-letter codes and are listed in random order; cells are numbered 1-60 within a sheet.
           No sheet shows a time, a frame index, an annotation or any earlier candidate offset.
  fine     for a candidate chosen by eye ("sheet CODE cell K looks like query frame Qi"), render raw frames around
           the implied start, middle and end at full frame rate, labelled with opaque per-render letters, next to
           query frames Q-first / Q-mid / Q-last.
  unblind  only after the decisions file is written: maps the chosen labels to source frames and seconds, then (and
           only then) reads the manifest annotations for comparison.

Keys live in <work>/<case>/.key/ and are not opened during judging. Seeds are fixed so renders are reproducible.

usage: python3 -I blind_anchor.py prepare --case R26_A --input CLIP --raw RAW --work DIR
       python3 -I blind_anchor.py fine    --case R26_A --work DIR --sheet CODE --cell K --qframe I
       python3 -I blind_anchor.py unblind --work DIR --decisions FILE --out FILE
"""
import argparse, hashlib, json, random, string, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
BIG = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
COLS, ROWS, OVERLAP = 10, 6, 10
CELL = 150
RAW_BOX = (280, 0, 720, 720)        # x, y, w, h: fixed central signer region of the 1280x720 raw frame (not the crop box)


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def probe(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                        "stream=width,height,r_frame_rate,nb_read_frames", "-of", "json", str(p)],
                       capture_output=True, text=True, check=True)
    s = json.loads(o.stdout)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return {"w": s["width"], "h": s["height"], "fps": int(n) / int(d), "frames": int(s["nb_read_frames"])}


def frames(path, idx, box=None, size=None):
    """Decode the listed frame indices (decode order = presentation order for these CFR files)."""
    info = probe(path)
    w, h = (box[2], box[3]) if box else (info["w"], info["h"])
    want = sorted(set(idx))
    step = want[1] - want[0] if len(want) > 2 else 0
    regular = len(want) > 40 and want[0] == 0 and want == list(range(0, want[-1] + 1, step))
    vf = [f"select='not(mod(n\\,{step}))'" if regular else
          "select='" + "+".join(f"eq(n\\,{i})" for i in want) + "'"]
    if box:
        vf.append(f"crop={box[2]}:{box[3]}:{box[0]}:{box[1]}")
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", ",".join(vf), "-vsync", "0",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    arr = np.frombuffer(out, np.uint8).reshape(-1, h, w, 3)
    assert len(arr) == len(want), (len(arr), len(want))
    got = dict(zip(want, arr))
    ims = [Image.fromarray(got[i]) for i in idx]
    return [im.resize(size if isinstance(size, tuple) else (size, round(size * im.height / im.width))) if size else im
            for im in ims]


def sheet(ims, labels, cols, cell, title):
    rows = -(-len(ims) // cols)
    H = max(im.height for im in ims)
    W = max(im.width for im in ims)
    canvas = Image.new("RGB", (cols * (W + 6) + 6, rows * (H + 26) + 40), "white")
    d = ImageDraw.Draw(canvas)
    d.text((8, 8), title, fill="black", font=BIG)
    for k, (im, lab) in enumerate(zip(ims, labels)):
        x, y = 6 + (k % cols) * (W + 6), 40 + (k // cols) * (H + 26)
        canvas.paste(im, (x, y + 20))
        d.text((x + 2, y + 1), lab, fill="black", font=FONT)
    return canvas


def cmd_prepare(a):
    case = Path(a.work) / a.case
    (case / ".key").mkdir(parents=True, exist_ok=True)
    rnd = random.Random(int(hashlib.sha256(a.case.encode()).hexdigest()[:8], 16))
    qi, ri = probe(a.input), probe(a.raw)
    step = round(ri["fps"] / 2)
    # query: every frame if <= 60, else 60 evenly spaced
    n = qi["frames"]
    qidx = list(range(n)) if n <= 60 else [round(k * (n - 1) / 59) for k in range(60)]
    qbox = RAW_BOX if (qi["w"], qi["h"]) == (ri["w"], ri["h"]) else None    # full-frame input: same signer region
    qims = frames(a.input, qidx, box=qbox, size=CELL) if qbox else \
        frames(a.input, qidx, size=(CELL, round(CELL * qi["h"] / qi["w"])))
    sheet(qims, [f"Q{k:02d}" for k in qidx], COLS, CELL, f"{a.case} QUERY ({n} frames; labels = query frame index)") \
        .save(case / "query.png")
    coarse = list(range(0, ri["frames"], step))
    ims = frames(a.raw, coarse, box=RAW_BOX, size=CELL)
    per, start, sheets = COLS * ROWS, 0, []
    while start < len(coarse):
        sheets.append(list(range(start, min(start + per, len(coarse)))))
        if start + per >= len(coarse):
            break
        start += per - OVERLAP
    codes = rnd.sample(sorted({"".join(rnd.choices(string.ascii_uppercase, k=3)) for _ in range(500)}), len(sheets))
    key = {}
    for code, cells in zip(codes, sheets):
        key[code] = [coarse[c] for c in cells]
        sheet([ims[c] for c in cells], [f"{k + 1}" for k in range(len(cells))], COLS, CELL,
              f"{a.case} sheet {code} (cells in time order within this sheet only)").save(case / f"coarse_{code}.png")
    order = codes[:]
    rnd.shuffle(order)
    (case / ".key/coarse.json").write_text(json.dumps({"raw_step": step, "sheets": key}))
    meta = {"case": a.case, "input": str(Path(a.input).name), "input_sha256": sha256(a.input), "input_probe": qi,
            "raw": str(Path(a.raw).name), "raw_sha256": sha256(a.raw), "raw_probe": ri, "raw_box": RAW_BOX,
            "coarse_step_frames": step, "n_sheets": len(sheets), "sheet_order_shown": order}
    (case / "meta.json").write_text(json.dumps(meta, indent=1))
    (case / ".key/paths.json").write_text(json.dumps({"input": str(a.input), "raw": str(a.raw)}))
    print(json.dumps({k: meta[k] for k in ("case", "input_probe", "n_sheets", "sheet_order_shown")}))


def cmd_fine(a):
    case = Path(a.work) / a.case
    key = json.loads((case / ".key/coarse.json").read_text())
    paths = json.loads((case / ".key/paths.json").read_text())
    qi, ri = probe(paths["input"]), probe(paths["raw"])
    cell_frame = key["sheets"][a.sheet][a.cell - 1]
    start0 = cell_frame - round(a.qframe * ri["fps"] / qi["fps"])        # implied raw frame of query frame 0
    n = qi["frames"]
    token = hashlib.sha256(f"{a.case}{a.sheet}{a.cell}{a.qframe}".encode()).hexdigest()[:6]
    rnd = random.Random(token)
    blocks, fkey = [], {}
    for name, q in (("FIRST", 0), ("MID", n // 2), ("LAST", n - 1)):
        center = start0 + round(q * ri["fps"] / qi["fps"])
        idx = [i for i in range(center - a.half, center + a.half + 1) if 0 <= i < ri["frames"]]
        letters = rnd.sample([x + y for x in string.ascii_uppercase for y in string.ascii_uppercase], len(idx))
        letters_sorted = sorted(letters)                      # labels increase with time but carry no offset
        labs = [f"{name[0]}-{l}" for l in letters_sorted]
        fkey[name] = dict(zip(labs, idx))
        qbox = RAW_BOX if (qi["w"], qi["h"]) == (ri["w"], ri["h"]) else None
        qim = frames(paths["input"], [q], box=qbox, size=2 * CELL)[0] if qbox else \
            frames(paths["input"], [q], size=(2 * CELL, round(2 * CELL * qi["h"] / qi["w"])))[0]
        rims = frames(paths["raw"], idx, box=RAW_BOX, size=CELL)
        blk = sheet(rims, labs, 9, CELL, f"{name}: query frame Q{q:02d} at left; raw frames below, time increases ->")
        canvas = Image.new("RGB", (qim.width + blk.width + 12, max(qim.height + 40, blk.height)), "white")
        canvas.paste(qim, (6, 40)); canvas.paste(blk, (qim.width + 12, 0))
        ImageDraw.Draw(canvas).text((6, 8), f"Q{q:02d}", fill="black", font=BIG)
        blocks.append(canvas)
    W = max(b.width for b in blocks)
    out = Image.new("RGB", (W, sum(b.height for b in blocks)), "white")
    y = 0
    for b in blocks:
        out.paste(b, (0, y)); y += b.height
    out.save(case / f"fine_{token}.png")
    fk = case / ".key/fine.json"
    allk = json.loads(fk.read_text()) if fk.exists() else {}
    allk[token] = {"sheet": a.sheet, "cell": a.cell, "qframe": a.qframe, "labels": fkey}
    fk.write_text(json.dumps(allk))
    print(f"fine_{token}.png")                                # no frame indices: the analyst stays blind


def cmd_unblind(a):
    dec = json.loads(Path(a.decisions).read_text())
    out = {"decisions_file_sha256": sha256(a.decisions), "cases": {}}
    for case, d in dec["cases"].items():
        cdir = Path(a.work) / case
        meta = json.loads((cdir / "meta.json").read_text())
        rec = {"decision": d, "meta": meta}
        if d.get("token"):
            fk = json.loads((cdir / ".key/fine.json").read_text())[d["token"]]["labels"]
            fps = meta["raw_probe"]["fps"]
            s, e = fk["FIRST"][d["first_label"]], fk["LAST"][d["last_label"]]
            rec.update(source_frame_start=s, source_frame_end=e, frames_spanned=e - s + 1,
                       input_frames=meta["input_probe"]["frames"],
                       source_time_start_s=round(s / fps, 3), source_time_end_excl_s=round((e + 1) / fps, 3))
            if d.get("mid_label"):
                m = fk["MID"][d["mid_label"]]
                rec["mid_check"] = {"source_frame": m, "expected": s + meta["input_probe"]["frames"] // 2}
        out["cases"][case] = rec
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1)[:4000])


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("prepare"); p.add_argument("--case", required=True); p.add_argument("--input", required=True)
    p.add_argument("--raw", required=True); p.add_argument("--work", required=True)
    f = sp.add_parser("fine"); f.add_argument("--case", required=True); f.add_argument("--work", required=True)
    f.add_argument("--sheet", required=True); f.add_argument("--cell", type=int, required=True)
    f.add_argument("--qframe", type=int, required=True); f.add_argument("--half", type=int, default=13)
    u = sp.add_parser("unblind"); u.add_argument("--work", required=True); u.add_argument("--decisions", required=True)
    u.add_argument("--out", required=True)
    a = ap.parse_args()
    {"prepare": cmd_prepare, "fine": cmd_fine, "unblind": cmd_unblind}[a.cmd](a)


if __name__ == "__main__":
    main()
