# Review package for the inspection sheet: the 45 diagnostic How2Sign clips next to the page, so the reviewer can open
# inspection_sheet.html and play every clip directly (no file picker).
# Sources: the local, git-ignored How2Sign v2 clips (sheet column video_path), each checked against the video_sha256
# column of the committed How2Sign v2 manifest (asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv). Videos are NOT committed (How2Sign is a
# third-party dataset; the repo keeps benchmark videos local-only): git holds this script, videos_manifest.csv and the
# checksums, and the package is rebuilt from them.
# Outputs: ../videos/<clip_id>.mp4 (git-ignored; the page tries this path first), ../videos_manifest.csv (committed),
#          and with --zip a self-contained package: page, sheet CSV, README, repetition audit, manifest, SHA256SUMS,
#          videos/. The zip is deterministic (sorted entries, fixed timestamps, mp4 stored uncompressed).
# Usage: python3 -I build_review_package.py [--zip ~/Desktop/curify/asl-review-package/asl_inspection_review_package.zip]
import argparse, csv, hashlib, os, shutil, sys, zipfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(OUT, '..', '..', '..', '..'))
MANIFEST = os.path.join(ROOT, 'asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv')
PAGE_FILES = ['inspection_sheet.html', 'inspection_sheet.csv', 'README.md', 'repetition_audit.md', 'repetition_audit.csv',
              'videos_manifest.csv']


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zip', default='')
    a = ap.parse_args()
    rows = list(csv.DictReader(open(os.path.join(OUT, 'inspection_sheet.csv'), encoding='utf-8')))
    expected = {m['how2sign_id']: m['video_sha256'] for m in csv.DictReader(open(MANIFEST, encoding='utf-8'))}
    assert len(rows) == 45 and all(r['clip_id'] in expected for r in rows)
    vdir = os.path.join(OUT, 'videos'); os.makedirs(vdir, exist_ok=True)
    man = []
    for r in rows:
        src = os.path.join(ROOT, r['video_path'])
        if not os.path.exists(src):
            sys.exit(f"missing source video {r['video_path']} (local How2Sign v2 clip; see the 10.13 manual_review README)")
        h = sha256(src)
        if h != expected[r['clip_id']]:
            sys.exit(f"sha256 mismatch for {r['video_path']}")
        dst = os.path.join(vdir, r['clip_id'] + '.mp4')
        if not (os.path.exists(dst) and sha256(dst) == h):
            shutil.copyfile(src, dst)
        assert sha256(dst) == h
        man.append({'review_id': r['review_id'], 'clip_id': r['clip_id'], 'file': f"videos/{r['clip_id']}.mp4",
                    'sha256': h, 'bytes': os.path.getsize(dst), 'duration_s': r['duration_s'],
                    'source_path': r['video_path']})
    extra = sorted(set(os.listdir(vdir)) - {m['clip_id'] + '.mp4' for m in man})
    assert not extra, f'unexpected files in videos/: {extra}'
    with open(os.path.join(OUT, 'videos_manifest.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, list(man[0]), lineterminator='\n'); w.writeheader(); w.writerows(man)
    total = sum(m['bytes'] for m in man)
    print(f'{len(man)} videos verified and placed in videos/ ({total / 1e6:.1f} MB)')
    if a.zip:
        z = os.path.abspath(os.path.expanduser(a.zip)); os.makedirs(os.path.dirname(z), exist_ok=True)
        top = 'asl_inspection_review_package/'
        sums = ''.join(f"{m['sha256']}  {m['file']}\n" for m in man)
        with zipfile.ZipFile(z + '.tmp', 'w') as zf:
            def put(name, data, compress):
                zi = zipfile.ZipInfo(top + name, date_time=(2026, 10, 19, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
                zi.external_attr = 0o644 << 16
                zf.writestr(zi, data)
            for name in PAGE_FILES:
                put(name, open(os.path.join(OUT, name), 'rb').read(), True)
            put('SHA256SUMS', sums.encode(), True)
            for m in man:
                put(m['file'], open(os.path.join(OUT, m['file']), 'rb').read(), False)
        os.replace(z + '.tmp', z)
        print(f'package: {z} ({os.path.getsize(z) / 1e6:.1f} MB, sha256 {sha256(z)})')


if __name__ == '__main__':
    main()
