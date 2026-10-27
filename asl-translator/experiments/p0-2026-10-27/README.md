# Three P0 experiments

Read [execution report](../../daily_report/2026-10-27/THREE_P0_EXECUTION_REPORT.md) and [protocol](PROTOCOL.md). Sampling proxy experiment and specialist smoke run are executed; paired Uni-Sign generation is blocked on missing assets. Nothing is deployed.

## Sampling

From this directory, with Python + NumPy + FFmpeg:

```bash
python -m unittest discover -p 'test_*.py' -v
python run_sampling.py --videos /path/to/display/videos --sheet /path/to/inspection_sheet.csv --out results/sampling_45.json
```

Only the reference-free `clip_id` and `review_id` fields are used from the sheet. The motion sampler consumes no text. `sampling_45.json` contains all decoded PTS and selected frame indices. Motion statistics are not translation metrics.

## Specialist

Install `requirements-specialist.txt` in an isolated Python 3.11 environment. Clone https://github.com/AIRC-KETI/OpenFS at `0d6fa3fa9b5aeaf99171e8c77e89531a22a6fd27`. Download only its Chicago recognizer via the official `scripts/download/download_ckpts.sh` link (Google Drive ID `1Ox2sIOtDsafn1TcVg6LQlt7m-gq9xVuq`) and unpack externally. Do not commit third-party assets. The upstream license is non-commercial research only.

Manifest format (no references):

```json
[{"case_id":"R02","video":"/path/to/clip.mp4","domain":"compressed_old_display_only"}]
```

```bash
python specialist.py --openfs /path/to/OpenFS --checkpoint /path/to/recognizer/best_model.pth --manifest /path/to/manifest.json --out results/specialist.json
```

On macOS MediaPipe may require graphics-service access even though inference uses the CPU. Every clip is scanned as a whole and with fixed 2-second windows at 1-second stride; this is **not temporal FS detection**. Returned time spans are input-window clip PTS; character boundaries are not available. The full-clip end is last PTS plus packet duration, falling back to median frame interval for these CFR display videos. Do not use that fallback as a claim of exact final-frame duration on arbitrary VFR media.

No names/lexicon/English references are passed to the model. Unknown FS presence and all raw letter hypotheses are preserved. Model token probabilities are not calibrated confidence in correctness. Source-video offsets require independently verified clip provenance.

## Repetition generation

Run in the original Uni-Sign CPU environment, with pinned Uni-Sign `eed438bcb49e30405cd6ccdfcccca330c134e830`, its How2Sign checkpoint and mT5 snapshot `2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f`:

```bash
python decode_repetition.py --unisign /path/to/Uni-Sign --checkpoint /path/to/how2sign_pose_only_slt.pth --mt5 /path/to/2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f --pose-dir /path/to/A_official/test-pose-rtmpose-192 --out paired_decode.json --preflight-only
# After successful preflight, remove --preflight-only to run both arms.
```

The runner loads only the 45 canonical exploratory IDs and verifies pose/tensor hashes. It does not consume text references. Stop on control mismatch; score saved paired outputs separately, and obtain human semantic labels before claiming a useful correction. This runner has not yet executed against the real model in this environment.
