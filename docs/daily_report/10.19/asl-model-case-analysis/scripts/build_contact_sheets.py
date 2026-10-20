"""Timestamped contact sheets per clip for model review: 4 fps, centre 720x720 signer crop, 6x4 tiles (6 s) per sheet.

    python3 -I scripts/build_contact_sheets.py ../../10.18/asl-review-inspection-sheet contact_sheets
"""
import csv, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

pkg, out = Path(sys.argv[1]), Path(sys.argv[2])
FPS, COLS, ROWS, T = 4, 6, 4, 300
out.mkdir(parents=True, exist_ok=True)
for row in csv.DictReader(open(pkg / "videos_manifest.csv")):
    rid, vid = row["review_id"], pkg / row["file"]
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(vid), "-vf",
                        f"fps={FPS},crop=720:720:280:0,scale={T}:{T}", f"{td}/f%04d.jpg"], check=True)
        frames = sorted(Path(td).glob("f*.jpg"))
        per = COLS * ROWS
        for s in range(0, len(frames), per):
            chunk = frames[s:s + per]
            rows = (len(chunk) + COLS - 1) // COLS
            sheet = Image.new("RGB", (COLS * T, rows * T), "black")
            d = ImageDraw.Draw(sheet)
            for i, f in enumerate(chunk):
                x, y = (i % COLS) * T, (i // COLS) * T
                sheet.paste(Image.open(f), (x, y))
                d.rectangle([x, y, x + 62, y + 14], fill="black")
                d.text((x + 3, y + 2), f"{(s + i) / FPS:5.2f}s", fill="yellow")
            sheet.save(out / f"{rid}_{s // per + 1:02d}.jpg", quality=85)
    print(rid, len(frames))
