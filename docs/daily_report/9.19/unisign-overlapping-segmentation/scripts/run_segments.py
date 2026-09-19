#!/usr/bin/env python3
"""Send each segment of segmentation_manifest.json to the local real-checkpoint Uni-Sign
service (POST /translate) EXACTLY ONCE, sequentially, and preserve the raw responses.

start/end in the output are OUR segmentation timestamps (source="wrapper_segmentation").
They are NOT Uni-Sign-native alignment. The service's own per-response segments[0].start/end
(0..clip length, "wrapper_derived") is kept verbatim under raw_response and is not used.

A failed segment is recorded with its error; nothing is retried silently. Segments already
recorded with HTTP 200 are skipped so a crash can resume without re-running (no double calls).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

FRAMES_RE = re.compile(r"(\d+)/(\d+)\s*\[")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def container_log_since(container: str, since: str) -> str:
    r = subprocess.run(["docker", "logs", "--since", since, container], capture_output=True, text=True)
    return r.stdout + r.stderr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--clips-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--log-out", required=True, help="filtered container log lines, per segment")
    ap.add_argument("--url", default="http://localhost:8010")
    ap.add_argument("--container", default="uni-sign-taskb")
    ap.add_argument("--timeout", type=int, default=3000)
    a = ap.parse_args()

    man = json.loads(Path(a.manifest).read_text())
    for ep in ("healthz", "readyz"):
        code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{a.url}/{ep}"],
                              capture_output=True, text=True).stdout
        print(f"/{ep}: {code}", flush=True)
        if code != "200":
            print("service not ready -- aborting")
            return 2

    out = Path(a.out)
    prev = json.loads(out.read_text())["segments"] if out.exists() else []
    results = [r for r in prev]
    done = {r["segment_id"] for r in results if r.get("http_status") == 200}
    log_path = Path(a.log_out)
    for seg in man["segments"]:
        sid = seg["segment_id"]
        if sid in done:
            continue
        clip = Path(a.clips_dir) / seg["file"]
        since = utc_now()
        t0 = time.time()
        p = subprocess.run(
            ["curl", "-s", "-m", str(a.timeout), "-w", "\n__HTTP__%{http_code}",
             "-F", f"video=@{clip};type=video/mp4", f"{a.url}/translate"],
            capture_output=True, text=True)
        runtime = time.time() - t0
        body, _, code = p.stdout.rpartition("\n__HTTP__")
        log = container_log_since(a.container, since)
        counters = [(int(m.group(1)), int(m.group(2))) for m in FRAMES_RE.finditer(log)]
        frames_seen = max((t for _, t in counters), default=None)   # tqdm total of "Processing frames: n/N"
        keep = [l for l in log.splitlines() if not ("onnxruntime" in l or "CleanUnused" in l)]
        with log_path.open("a") as f:
            f.write(f"===== segment {sid} since {since} http={code} runtime={runtime:.1f}s =====\n" + "\n".join(keep) + "\n")
        rec = {
            "segment_id": sid, "start_sec": seg["start_sec"], "end_sec": seg["end_sec"],
            "duration_sec": seg["duration_sec"], "source": "wrapper_segmentation",
            "http_status": int(code) if code.isdigit() else 0, "runtime_sec": round(runtime, 2),
            "expected_frames_manifest": seg["expected_frames_pts"],
            "frames_actual_clip_file": seg["clip_verification"]["frames_actual"],
            "frames_seen_by_service_tqdm_total": frames_seen,
            "random_256_sampling_occurred": (frames_seen or 0) > 256,
            "request_started_utc": since, "curl_exit": p.returncode, "text": None,
        }
        try:
            j = json.loads(body)
            rec["raw_response"] = j
            rec["text"] = j.get("translation")
        except Exception:
            rec["raw_response_text"] = body[:2000]
            rec["error"] = f"non-JSON/empty body (curl exit {p.returncode}, stderr={p.stderr[:300]!r})"
        results = [r for r in results if r["segment_id"] != sid] + [rec]
        results.sort(key=lambda r: r["segment_id"])
        out.write_text(json.dumps({
            "source": "wrapper_segmentation",
            "timestamp_note": "start_sec/end_sec are OUR segmentation timestamps, NOT Uni-Sign-native alignment.",
            "model_checkpoint": "how2sign_pose_only_slt.pth",
            "checkpoint_sha256": "1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d",
            "calls_per_segment": 1,
            "segments": results}, indent=2, ensure_ascii=False))
        print(f"[seg {sid}] {seg['start_sec']}-{seg['end_sec']}s http={rec['http_status']} {runtime:.1f}s "
              f"frames_seen={frames_seen} text={str(rec['text'])[:100]!r}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
