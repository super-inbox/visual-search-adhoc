#!/usr/bin/env python3
"""Production ASL model on the 45-case (R01-R45) inspection set — evaluation wrapper.

Calls the CURRENT production function itself, not a port: `transcribe_asl()` is loaded by path from a read-only
export of curify-studio `origin/main` (`curify_background/app/utils/asl_utils.py`). Nothing in that file is changed.

Only one production dependency is stubbed: `app.services.imagen_service`, which `transcribe_asl` imports for
`get_gemini_client()` and `is_quota_exhausted()`. Importing the real module would pull in `app.config.Settings`
and unrelated production environment. The stub mirrors production exactly:
  - `genai.Client(api_key=GEMINI_API_KEY, http_options=HttpOptions(timeout=60_000))` (production
    `_get_genai_client`, GEMINI_TIMEOUT_MS = 60_000, with the same fallback to a default client);
  - `is_quota_exhausted` with production's `_QUOTA_TOKENS`.

Pass-through instrumentation (no behaviour change):
  - `_extract_frames` is wrapped to record the exact timestamps production chose;
  - `client.models.generate_content` is wrapped to record requested model, returned `model_version`, usage metadata,
    latency, finish reason and the raw response text of every batch.

One primary inference per case, no retry by this wrapper. Production's own retry lives in the job queue (transport
errors only) and is not reproduced. No reference text is read by this script. Product side effects (DB, credits,
storage, translation/subtitle/mux) are not invoked: only `transcribe_asl`, which is what produces the English text.

--dry-run runs production's local preprocessing only (probe, runs, budget, timestamps, frame extraction); it never
imports google.genai and needs no key.

The API key is read only from the GEMINI_API_KEY environment variable and is never written or printed.

usage:
  python -I run_production_45.py --prod-src <export root> --prod-commit <sha> --out-dir <dir> [--only R01] [--dry-run]
"""
from __future__ import annotations

import argparse, csv, datetime as dt, hashlib, importlib.util, json, os, sys, time, types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SHEET = REPO / "docs/daily_report/10.18/asl-review-inspection-sheet"
GEMINI_TIMEOUT_MS = 60_000                                                  # production imagen_service
QUOTA_TOKENS = ("RESOURCE_EXHAUSTED", "429", "spend cap", "quota", "QUOTA")  # production imagen_service

sys.path.insert(0, str(REPO / "docs/daily_report/10.16/asl-p0-16-experimental-credibility/scripts"))
from holdout_guard import assert_not_holdout  # noqa: E402

CALLS: list = []


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def install_stub(dry_run: bool):
    """`app.services.imagen_service` stand-in, mirroring production's client accessor."""
    app = types.ModuleType("app"); app.__path__ = []
    services = types.ModuleType("app.services"); services.__path__ = []
    utils = types.ModuleType("app.utils"); utils.__path__ = []
    stub = types.ModuleType("app.services.imagen_service")
    state = {}

    def is_quota_exhausted(exc):
        return any(tok in str(exc) for tok in QUOTA_TOKENS)

    def get_gemini_client():
        if dry_run:
            raise RuntimeError("dry run: no client")
        if "c" in state:
            return state["c"]
        from google import genai
        from google.genai import types as gt
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        try:
            c = genai.Client(api_key=key, http_options=gt.HttpOptions(timeout=GEMINI_TIMEOUT_MS))
        except Exception:
            c = genai.Client(api_key=key)
        real = c.models.generate_content

        def recorded(*a, **kw):
            t0 = time.perf_counter(); rec = {"requested_model": kw.get("model"), "n_parts": None}
            try:
                parts = kw["contents"][0].parts
                rec["n_parts"] = len(parts)
                rec["n_images"] = sum(1 for p in parts if getattr(p, "inline_data", None) is not None)
                cfg = kw.get("config")
                rec["config"] = {"response_mime_type": getattr(cfg, "response_mime_type", None),
                                 "temperature": getattr(cfg, "temperature", None)}
                resp = real(*a, **kw)
            except Exception as e:
                rec.update(latency_s=round(time.perf_counter() - t0, 3), error=f"{type(e).__name__}: {str(e)[:300]}")
                CALLS.append(rec); raise
            um = getattr(resp, "usage_metadata", None)
            cand = (getattr(resp, "candidates", None) or [None])[0]
            rec.update(latency_s=round(time.perf_counter() - t0, 3), model_version=getattr(resp, "model_version", None),
                       response_id=getattr(resp, "response_id", None),
                       finish_reason=str(getattr(cand, "finish_reason", None)) if cand else None,
                       usage={k: getattr(um, k, None) for k in ("prompt_token_count", "candidates_token_count",
                                                                "thoughts_token_count", "total_token_count")} if um else None,
                       raw_text=resp.text)
            CALLS.append(rec)
            return resp
        c.models.generate_content = recorded
        state["c"] = c
        return c

    stub.get_gemini_client = get_gemini_client
    stub.is_quota_exhausted = is_quota_exhausted
    sys.modules.update({"app": app, "app.services": services, "app.utils": utils, "app.services.imagen_service": stub})


def load_production(src_root: Path):
    path = src_root / "curify_background/app/utils/asl_utils.py"
    spec = importlib.util.spec_from_file_location("app.utils.asl_utils", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["app.utils.asl_utils"] = mod
    spec.loader.exec_module(mod)
    return mod, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prod-src", required=True, type=Path); ap.add_argument("--prod-commit", required=True)
    ap.add_argument("--out-dir", required=True, type=Path); ap.add_argument("--only", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--env-file", type=Path, help="dotenv file; ONLY GEMINI_API_KEY is loaded, into this process only")
    a = ap.parse_args()
    if a.env_file and not a.dry_run:
        for line in a.env_file.read_text().splitlines():
            k, sep, v = line.strip().removeprefix("export ").partition("=")
            if sep and k.strip() == "GEMINI_API_KEY":
                os.environ["GEMINI_API_KEY"] = v.strip().strip("'\"")
        if not os.environ.get("GEMINI_API_KEY"):
            sys.exit("GEMINI_API_KEY not found in --env-file")
        print("GEMINI_API_KEY loaded from --env-file (value not shown)", flush=True)
    install_stub(a.dry_run)
    prod, prod_path = load_production(a.prod_src)
    rows = list(csv.DictReader(open(SHEET / "videos_manifest.csv")))
    assert [r["review_id"] for r in rows] == [f"R{i:02d}" for i in range(1, 46)]
    assert_not_holdout([r["clip_id"] for r in rows])
    if a.only:
        keep = set(a.only.split(",")); rows = [r for r in rows if r["review_id"] in keep]
    a.out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"production_repo": "curify-studio", "production_ref": "origin/main", "production_commit": a.prod_commit,
            "production_file": "curify_background/app/utils/asl_utils.py", "production_file_sha256": sha256(prod_path),
            "entry_point": "transcribe_asl(video_path) with production defaults (provider='gemini', frame_budget=None)",
            "model": prod.ASL_MODEL, "temperature": prod.ASL_TEMPERATURE,
            "prompt_sha256": hashlib.sha256(prod._PROMPT.encode()).hexdigest(),
            "sampling": {k: getattr(prod, k) for k in ("PROBE_FPS", "PROBE_WIDTH", "TARGET_FRAMES_PER_SEC", "MIN_FRAME_BUDGET",
                                                       "MAX_FRAME_BUDGET", "DENSITY_FLOOR_FPS", "KEYFRAME_WIDTH",
                                                       "MIN_FRAMES_PER_RUN", "BATCH_SIZE", "IDLE_QUANTILE",
                                                       "ABS_MOTION_FLOOR", "DEDUP_MAX_GAP_S", "DEGENERATE_REPEAT_COUNT")},
            "stubbed": "app.services.imagen_service (get_gemini_client mirrored: GEMINI_API_KEY, HttpOptions timeout 60000 ms; "
                       "is_quota_exhausted mirrored)",
            "dry_run": a.dry_run}
    (a.out_dir / "run_meta.json").write_text(json.dumps(meta, indent=1))

    for r in rows:
        rid, cid = r["review_id"], r["clip_id"]
        out = a.out_dir / f"{rid}.json"
        if out.exists() and not a.dry_run:
            continue
        video = SHEET / r["file"]
        assert sha256(video) == r["sha256"], rid
        stamps_used = []
        real_extract = prod._extract_frames

        def extract(video_path, stamps, outdir, _real=real_extract):
            stamps_used.extend(stamps)
            return _real(video_path, stamps, outdir)
        prod._extract_frames = extract
        CALLS.clear()
        rec = {"review_id": rid, "clip_id": cid, "input_video": f"docs/daily_report/10.18/asl-review-inspection-sheet/{r['file']}",
               "input_video_sha256": r["sha256"], "input_domain": "inspection-sheet video = How2Sign v2 clip (B_ours_5p39 window)",
               "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        t0 = time.perf_counter()
        try:
            if a.dry_run:
                import tempfile
                times, motion = prod._probe_motion(str(video))
                runs = prod._segment_runs(times, motion)
                budget = prod._budget_for_duration(times[-1])
                st = prod._allocate_timestamps(runs, budget)
                with tempfile.TemporaryDirectory() as td:
                    frames = extract(str(video), st, td)
                rec.update(status="dry_run", frame_budget_used=budget, frames_sampled=len(frames),
                           probe_duration_s=times[-1], n_batches=-(-len(frames) // prod.BATCH_SIZE))
            else:
                res = prod.transcribe_asl(str(video))
                rec.update(status="ok" if res.segments else ("error" if res.error else "empty"),
                           output_text_raw=res.text, segments=[s.to_dict() for s in res.segments],
                           error=res.error, quota_exhausted=res.quota_exhausted,
                           had_transport_error=res.had_transport_error, frames_sampled=res.frames_sampled,
                           frame_budget_used=res.frame_budget_used, sampling_density_fps=res.sampling_density_fps,
                           low_density=res.low_density, degenerate_repetition=res.degenerate_repetition,
                           frames_uniform_equivalent=res.frames_uniform_equivalent,
                           n_runs=len(res.runs), n_active_runs=sum(x.active for x in res.runs))
        except Exception as e:
            rec.update(status="wrapper_exception", error=f"{type(e).__name__}: {str(e)[:300]}")
        finally:
            prod._extract_frames = real_extract
        rec.update(latency_s=round(time.perf_counter() - t0, 3), timestamps_sent_s=[round(x, 3) for x in stamps_used],
                   n_timestamps=len(stamps_used), api_calls=list(CALLS), retry_count=0)
        if not a.dry_run:
            out.write_text(json.dumps(rec, indent=1))
        print(rid, rec["status"], rec.get("frames_sampled"), rec.get("n_batches", len(CALLS)),
              (rec.get("output_text_raw") or "")[:80], flush=True)
        if a.dry_run:
            with open(a.out_dir / "dry_run.jsonl", "a") as f:
                f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
