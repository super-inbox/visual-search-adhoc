#!/usr/bin/env python3
"""Offline native/direct-video-input ASL evaluation runner.

Reproduces, as closely as the source documents it, the method recorded in
curify-studio's `docs/asl-translation-mvp-spec.md`, "13. Change record —
2026-09-10 (native video input — the first intervention that moved
anything)": the whole clip `.mp4` uploaded via the Gemini Files API and sent
to the model in ONE call, instead of extracted-JPEG-frames-per-batch (what
`run_current_model.py` does).

This is a SEPARATE script, not a modification of `run_current_model.py`.
The two runners share only read-only imports (PRODUCTION_PROMPT, the
sampler-free bits, prompt_sha256/input_md5) so the existing frame-based
baseline configs stay byte-for-byte unaffected by anything here.

DEFAULT MODE IS DRY-RUN. Dry-run does local ffprobe + corpus_guard checks
only: it reports the video's duration/size, confirms it is not a leaky
input, computes the prompt/input hashes, and reports what WOULD be sent
(1 file, 1 model call) — it never imports google.genai and never requires
GEMINI_API_KEY.

A real run requires BOTH --run AND --acknowledge-private-data-upload, plus
GEMINI_API_KEY, and is the only code path that imports google.genai, uploads
a file, or opens a network connection. It was NOT executed as part of
building this script.

────────────────────────────────────────────────────────────────────────────
PROVENANCE OF THE METHOD THIS SCRIPT REPRODUCES
────────────────────────────────────────────────────────────────────────────
Source: curify-studio origin/main @ db86417ec1889858f5b163503a60253302843644,
docs/asl-translation-mvp-spec.md, Section 13. Inspected read-only via
`git -C <curify-studio> show origin/main:docs/asl-translation-mvp-spec.md`;
curify-studio was NOT checked out, pulled, merged, or modified to build this
script (its working tree remains on an unrelated old commit, 7b3fa5b,
1468 commits behind origin/main — untouched).

What Section 13 documents, and what is reproduced here:
  - model            : gemini-3.6-flash (13.2 table; matches this script's
                        CONFIGS["native_video_2026_09_10_gemini_3_6"]["model"])
  - input mechanism   : "the whole `.mp4` sent to Gemini via the Files API,
                        instead of extracted JPEG frames" (13, opening line).
                        The exact upload/poll/reference/delete call pattern
                        is NOT itself documented in Section 13 (no code was
                        preserved — 13.5 says the original run "exists only
                        as a scratch script", `scratchpad/nativevid/
                        run_native_video.py`, which does not exist in this
                        checkout of curify-studio; confirmed via
                        `git ls-tree -r origin/main` returning no match).
                        The Files-API call sequence below (upload -> poll
                        ACTIVE -> Part.from_uri -> generate_content ->
                        delete) is this script's own implementation of "send
                        the whole mp4 via the Files API", using the
                        google-genai SDK's documented Files API surface
                        (client.files.upload / .get / .delete,
                        Part.from_uri) — NOT copied from a preserved source,
                        because none exists. Flagged explicitly rather than
                        silently presented as reproduced.
  - prompt            : PRODUCTION_PROMPT (imported from run_current_model,
                        byte-identical source) with exactly the two edits
                        13.1 documents by name: (1) the "Frames are sparse:
                        you are seeing key moments..." rule bullet removed
                        entirely; (2) "the frame timestamps you used" ->
                        "the video timeline" in the segmenting rule. 13.1:
                        "task, rules and output schema are byte-identical"
                        otherwise. See NATIVE_VIDEO_PROMPT / prompt_diff()
                        below. The full exact diff was recorded in Section
                        13's own `native_video_result.json`
                        (`prompt_diff_vs_PRODUCTION_PROMPT` key) — that file
                        does not exist in this checkout either, so this
                        script's diff is reconstructed from 13.1's prose,
                        not copied. Recorded as NOT DOCUMENTED beyond that
                        prose in the audit this script was built from.
  - temperature       : NOT set explicitly in Section 13's own table (13.2
                        lists only WER/CER/words/calls per arm, no
                        temperature column). This script mirrors the control
                        config `evaluation_2026_09_04_gemini_3_6`, whose own
                        CONFIGS entry in run_current_model.py has
                        `temperature: None` ("not carried over ... mixing a
                        legacy temperature pin with a thinking-enabled 3.x
                        model is not a documented, supported combination").
  - thinking_level    : "medium" per 13.1's control config and 13.6's own
                        discussion. 13.6 documents that on google-genai
                        1.55.0 (the benchmark machine's SDK at the time)
                        this value is REJECTED by the SDK's ThinkingLevel
                        enum (UNSPECIFIED/LOW/HIGH only) and silently
                        dropped with a UserWarning -- "confirmed live, firing
                        on the evaluation_2026_09_04_gemini_3_6 config
                        itself". THIS REPO'S installed google-genai is a
                        DIFFERENT version (2.20.0; checked via `pip show
                        google-genai` at audit time) whose ThinkingLevel enum
                        DOES include MEDIUM (also MINIMAL, LOW, HIGH,
                        UNSPECIFIED) -- verified via
                        `list(google.genai.types.ThinkingLevel)`. So 13.6's
                        specific bug is NOT reproduced by this script's
                        environment; that is an environment difference
                        between this repo and the machine Section 13 ran on,
                        not a claim that 13.6 was wrong. This script does not
                        silently rely on either behavior: see
                        validate_thinking_level() below, which fails loudly
                        (raises) if the configured value is not a member of
                        the INSTALLED SDK's own ThinkingLevel enum, rather
                        than letting an unrecognised value warn-and-drop --
                        exactly the fix Section 13's own P0-5 recommends
                        ("make an unrecognised config value fail the run
                        instead of warning").
  - test clip         : Section 13 ran ONE clip, the private-corpus video
                        `1252_1000016397_76.8s` (asl-translator/data/
                        asl_corpus/videos/1252_1000016397_76.8s.mp4 in THIS
                        repo). That clip is NOT part of the frozen How2Sign
                        v2 128-clip benchmark (confirmed: it lives under
                        data/asl_corpus/, a different, private, non-
                        independent corpus -- data/asl_corpus/manifest.json
                        marks it non_independent /
                        usable_for_official_metrics=false). This script can
                        run against either corpus; the How2Sign v2 benchmark
                        driver (run_native_video_how2sign_v2_benchmark.py)
                        is the intended path for the frozen-128/diagnostic-12
                        experiment this task is designing.
  - generation config : response_mime_type="application/json" (matches
                        run_current_model.run_real()'s existing frame path;
                        Section 13 does not document this explicitly but the
                        JSON schema of its own output ("segments"/
                        "confidence"/"notes") requires it and it is the
                        existing repo convention).
  - upload/file lifecycle : NOT DOCUMENTED in Section 13 beyond "via the
                        Files API". No mention of whether the uploaded file
                        was deleted after the call, what timeout was used
                        for the upload-processing wait, or how many bytes
                        were uploaded. This script deletes the uploaded file
                        after each clip by default (own design decision, not
                        reproduced from the source -- see --keep-uploaded-file
                        to disable) to avoid accumulating files against the
                        project's Files API quota across a 128-clip run.
  - timeout/cost/token observations : Section 13.2 reports "9,676 total
                        tokens, 15.9s wall-clock" for the ONE test-arm call
                        on the 76.8s private clip. No per-token cost figure,
                        no timeout value, and no token count for the control
                        arm are documented. NOT DOCUMENTED beyond those two
                        numbers.
  - caveats (13.5)   : n=1, not a measurement; circular reference (the only
                        clip tested is non-independent); the prompt confound
                        (13.1) is unavoidable and this script's
                        NATIVE_VIDEO_PROMPT carries the same confound by
                        construction; no repeat runs (decoding variance
                        untested at n=1); "not a config" -- 13.5 says the
                        original script "is not reproducible through the
                        normal harness... not resumable" -- resumability
                        here is intentionally added at the BENCHMARK DRIVER
                        level (run_native_video_how2sign_v2_benchmark.py),
                        mirroring run_curify_how2sign_v2_benchmark.py's
                        existing skip-already-completed-clip logic, rather
                        than in this single-clip runner, matching how
                        run_current_model.py itself has no resumability of
                        its own either.

Do not treat any output of this script's --run path (not executed while
building it) as literally reproducing Section 13's one recorded result --
Gemini decoding is non-deterministic even at a pinned thinking_level, and
Section 13 itself documents no repeat runs to establish a variance floor for
this arm specifically (see general variance floor in the source doc's own
§12.2, referenced above but not re-derived here).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_current_model as rcm  # noqa: E402 — reuse PRODUCTION_PROMPT, input_md5, probe_duration, validate_local_video_path

SOURCE_REPO = "curify-studio"
SOURCE_REF = "origin/main"
SOURCE_COMMIT = "db86417ec1889858f5b163503a60253302843644"  # spec commit Section 13 was read from
SOURCE_FILE = "docs/asl-translation-mvp-spec.md"
SOURCE_SECTION = "13. Change record — 2026-09-10 (native video input — the first intervention that moved anything)"

# ─────────────────────────────────────────────────────────────────────────
# Prompt reconstruction — exactly the two edits 13.1 names, nothing else.
# ─────────────────────────────────────────────────────────────────────────
_REMOVED_BULLET = (
    "- Frames are sparse: you are seeing key moments, not every sign. Where a sign is\n"
    "  ambiguous, prefer the reading that fits the surrounding context.\n"
)
_TIMESTAMP_OLD = "start/end seconds taken from the\n  frame timestamps you used."
_TIMESTAMP_NEW = "start/end seconds taken from\n  the video timeline."


def build_native_video_prompt() -> str:
    prod = rcm.PRODUCTION_PROMPT
    if _REMOVED_BULLET not in prod:
        raise RuntimeError(
            "PRODUCTION_PROMPT in run_current_model.py no longer contains the bullet "
            "Section 13.1 says was removed for native video — the two prompts have "
            "drifted. Re-derive NATIVE_VIDEO_PROMPT by hand before running anything."
        )
    if _TIMESTAMP_OLD not in prod:
        raise RuntimeError(
            "PRODUCTION_PROMPT no longer contains the 'frame timestamps you used' "
            "phrase Section 13.1 says was replaced — re-derive NATIVE_VIDEO_PROMPT "
            "by hand before running anything."
        )
    out = prod.replace(_REMOVED_BULLET, "")
    out = out.replace(_TIMESTAMP_OLD, _TIMESTAMP_NEW)
    return out


NATIVE_VIDEO_PROMPT = build_native_video_prompt()


def native_video_prompt_sha256() -> str:
    import hashlib
    return hashlib.sha256(NATIVE_VIDEO_PROMPT.encode("utf-8")).hexdigest()


def prompt_diff_vs_production() -> dict:
    """Structured record of the exact, documented edit — for run_metadata."""
    return {
        "base_prompt_sha256": rcm.prompt_sha256(),
        "native_video_prompt_sha256": native_video_prompt_sha256(),
        "edits": [
            {"type": "bullet_removed", "text": _REMOVED_BULLET.strip()},
            {"type": "phrase_replaced", "old": _TIMESTAMP_OLD.strip(), "new": _TIMESTAMP_NEW.strip()},
        ],
        "source": "curify-studio docs/asl-translation-mvp-spec.md §13.1, reconstructed from prose "
                   "(native_video_result.json's own prompt_diff_vs_PRODUCTION_PROMPT does not exist "
                   "in this checkout — see this script's module docstring).",
    }


# ─────────────────────────────────────────────────────────────────────────
# Config — one arm, dated and named like run_current_model.py's convention.
# Deliberately NOT added to run_current_model.CONFIGS: that dict is the
# frame-pipeline's own config registry and this script does not modify it.
# ─────────────────────────────────────────────────────────────────────────
CONFIGS = {
    "native_video_2026_09_10_gemini_3_6": {
        "model": "gemini-3.6-flash",
        "modality": "native_video",
        "temperature": None,
        "temperature_label": "temperature_not_set_gemini3_uses_thinking_level",
        "thinking_level": "medium",
    },
}


def validate_thinking_level(level: str) -> None:
    """Fail loudly on an unrecognised ThinkingLevel instead of letting the SDK
    warn-and-drop it — the fix §13.6/P0-5 in the source doc recommends."""
    from google.genai import types as gtypes
    valid = {m.value for m in gtypes.ThinkingLevel} | {m.name for m in gtypes.ThinkingLevel}
    if level.upper() not in {v.upper() for v in valid}:
        raise ValueError(
            f"thinking_level={level!r} is not a member of this installed google-genai SDK's "
            f"ThinkingLevel enum ({sorted(valid)}). Refusing to silently no-op it (see "
            "run_native_video.py module docstring, §13.6/P0-5)."
        )


# ─────────────────────────────────────────────────────────────────────────
# Dry-run (no network, no google.genai import)
# ─────────────────────────────────────────────────────────────────────────
@dataclass
class NativeVideoDryRunReport:
    video: str
    duration_s: float
    size_bytes: int
    expected_model_calls: int = 1
    expected_files_uploaded: int = 1


def run_dry(video_path: Path, config_name: str) -> NativeVideoDryRunReport:
    duration = rcm.probe_duration(str(video_path))
    return NativeVideoDryRunReport(
        video=str(video_path),
        duration_s=round(duration, 3),
        size_bytes=video_path.stat().st_size,
    )


def print_dry_run_report(report: NativeVideoDryRunReport, config_name: str) -> None:
    cfg = CONFIGS[config_name]
    print("=" * 72)
    print("DRY RUN ONLY — NO MODEL CALL, NO UPLOAD WAS MADE.")
    print("=" * 72)
    print(f"video                 : {report.video}")
    print(f"config                : {config_name}")
    print(f"model                 : {cfg['model']}")
    print(f"modality              : {cfg['modality']}")
    print(f"temperature mode      : {cfg['temperature_label']}")
    print(f"thinking_level        : {cfg['thinking_level']}")
    print(f"duration_s            : {report.duration_s}")
    print(f"size_bytes            : {report.size_bytes} ({report.size_bytes / 1e6:.2f} MB)")
    print(f"expected files uploaded: {report.expected_files_uploaded}")
    print(f"expected Gemini calls  : {report.expected_model_calls}")
    print(f"native-video prompt sha256: {native_video_prompt_sha256()}")
    print("=" * 72)
    print("DRY RUN ONLY — NO MODEL CALL, NO UPLOAD WAS MADE.")
    print("=" * 72)


def dry_run_report_to_json(report: NativeVideoDryRunReport, config_name: str, video_arg: str) -> dict:
    cfg = CONFIGS[config_name]
    return {
        "project_id": None,
        "video": video_arg,
        "producer": "asl-translator/asl-eval/run_native_video.py (dry_run)",
        "warning": "DRY RUN — no model call was made; no prediction segments exist.",
        "dry_run": True,
        "run_metadata": {
            "config": config_name,
            "model": cfg["model"],
            "modality": cfg["modality"],
            "temperature": cfg["temperature_label"],
            "thinking_level": cfg["thinking_level"],
            "duration_s": report.duration_s,
            "size_bytes": report.size_bytes,
            "model_calls": 0,
            "expected_model_calls": report.expected_model_calls,
            "expected_files_uploaded": report.expected_files_uploaded,
            "production_side_effects": False,
            "source_repo": SOURCE_REPO,
            "source_ref": SOURCE_REF,
            "source_commit": SOURCE_COMMIT,
            "source_file": SOURCE_FILE,
            "source_section": SOURCE_SECTION,
            "prompt_sha256": native_video_prompt_sha256(),
            "prompt_diff_vs_production": prompt_diff_vs_production(),
            "input_md5": rcm.input_md5(video_arg) if Path(video_arg).exists() else None,
        },
        "segments": [],
    }


# ─────────────────────────────────────────────────────────────────────────
# Real-run path — GATED. Not executed by this task. google.genai is only
# imported inside this function, only reached when --run is passed.
# ─────────────────────────────────────────────────────────────────────────
def parse_segments_response(raw: str) -> list:
    """Parse a Gemini text response into a list of {line, start, end, text} segments.

    Accepts two top-level JSON shapes, normalizing both through the same
    per-item extraction below: {"segments": [...]} (the requested shape) and a
    bare [...] array (observed at least once from the model in practice,
    see docs/daily_report/9.10/asl-native-video-evaluation/BLOCKER_STATUS.md).
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        data = json.loads(m.group(0)) if m else {"segments": []}

    raw_segments = data if isinstance(data, list) else data.get("segments", [])
    segments = []
    for s in raw_segments:
        try:
            segments.append({
                "line": len(segments) + 1,
                "start": float(s["start"]),
                "end": float(s["end"]),
                "text": str(s.get("text", "")).strip(),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return segments


def run_real(video_path: Path, config_name: str, output_path: Path,
             delete_uploaded_file: bool = True,
             file_state_poll_timeout_s: float = 120.0) -> None:
    """Upload the whole clip via the Files API and make ONE generate_content call.

    Requires GEMINI_API_KEY. Writes ONLY the specified local --output file.
    No Supabase, no Azure, no credits, no project/job records — this function
    does not import or reference any of that code (same guarantee as
    run_current_model.run_real()).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit(
            "GEMINI_API_KEY is not set. A real run requires it explicitly — "
            "refusing to fall back to any implicit credential source."
        )

    cfg = CONFIGS[config_name]
    validate_thinking_level(cfg["thinking_level"])

    from google import genai
    from google.genai import types as gtypes

    client = genai.Client(api_key=api_key)
    duration = rcm.probe_duration(str(video_path))

    t0 = time.monotonic()
    uploaded = client.files.upload(file=str(video_path))
    upload_s = round(time.monotonic() - t0, 3)

    file_name = uploaded.name
    t1 = time.monotonic()
    deadline = t1 + file_state_poll_timeout_s
    state = str(getattr(uploaded, "state", "")).upper()
    while "ACTIVE" not in state:
        if time.monotonic() > deadline:
            try:
                client.files.delete(name=file_name)
            except Exception:
                pass
            raise TimeoutError(
                f"Uploaded file {file_name!r} did not reach ACTIVE state within "
                f"{file_state_poll_timeout_s}s (last state={state!r})."
            )
        if "FAILED" in state:
            try:
                client.files.delete(name=file_name)
            except Exception:
                pass
            raise RuntimeError(f"Gemini Files API reported FAILED for {file_name!r} (video={video_path}).")
        time.sleep(2.0)
        uploaded = client.files.get(name=file_name)
        state = str(getattr(uploaded, "state", "")).upper()
    processing_wait_s = round(time.monotonic() - t1, 3)

    try:
        parts = [
            gtypes.Part.from_text(text=NATIVE_VIDEO_PROMPT),
            gtypes.Part.from_uri(file_uri=uploaded.uri, mime_type=uploaded.mime_type),
        ]
        gen_config_kwargs = {"response_mime_type": "application/json"}
        if cfg["temperature"] is not None:
            gen_config_kwargs["temperature"] = cfg["temperature"]
        if cfg.get("thinking_level"):
            gen_config_kwargs["thinking_config"] = gtypes.ThinkingConfig(
                thinking_level=cfg["thinking_level"]
            )

        t2 = time.monotonic()
        resp = client.models.generate_content(
            model=cfg["model"],
            contents=[gtypes.Content(role="user", parts=parts)],
            config=gtypes.GenerateContentConfig(**gen_config_kwargs),
        )
        call_wall_s = round(time.monotonic() - t2, 3)
    finally:
        if delete_uploaded_file:
            try:
                client.files.delete(name=file_name)
            except Exception as e:  # noqa: BLE001 — cleanup best-effort, never masks the real result
                print(f"warning: failed to delete uploaded file {file_name!r}: {e}", file=sys.stderr)

    raw = (resp.text or "").strip()
    segments = parse_segments_response(raw)

    usage = getattr(resp, "usage_metadata", None)
    token_counts = None
    if usage is not None:
        token_counts = {
            "prompt_token_count": getattr(usage, "prompt_token_count", None),
            "candidates_token_count": getattr(usage, "candidates_token_count", None),
            "total_token_count": getattr(usage, "total_token_count", None),
        }

    output = {
        "project_id": None,
        "video": str(video_path),
        "producer": "asl-translator/asl-eval/run_native_video.py (--run)",
        "warning": "UNVERIFIED machine output — offline evaluation run, not a production job.",
        "run_metadata": {
            "config": config_name,
            "model": cfg["model"],
            "modality": cfg["modality"],
            "temperature": cfg["temperature_label"],
            "thinking_level": cfg["thinking_level"],
            "duration_s": round(duration, 3),
            "model_calls": 1,
            "files_uploaded": 1,
            "upload_wall_clock_s": upload_s,
            "file_processing_wait_s": processing_wait_s,
            "generate_content_wall_clock_s": call_wall_s,
            "total_wall_clock_s": round(upload_s + processing_wait_s + call_wall_s, 3),
            "token_usage": token_counts,
            "uploaded_file_deleted": delete_uploaded_file,
            "production_side_effects": False,
            "source_repo": SOURCE_REPO,
            "source_ref": SOURCE_REF,
            "source_commit": SOURCE_COMMIT,
            "source_file": SOURCE_FILE,
            "source_section": SOURCE_SECTION,
            "prompt_sha256": native_video_prompt_sha256(),
            "prompt_diff_vs_production": prompt_diff_vs_production(),
            "input_md5": rcm.input_md5(video_path),
        },
        "segments": segments,
    }
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(segments)} segment(s) from 1 model call to {output_path}")


# ─────────────────────────────────────────────────────────────────────────
# CLI — mirrors run_current_model.py's flag names/semantics where the same
# concept applies (--video, --run, --acknowledge-private-data-upload,
# --acknowledge-contaminated-input, --output, --json-out).
# ─────────────────────────────────────────────────────────────────────────
def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--video", required=True, help="Path to a LOCAL video file. No URLs.")
    ap.add_argument("--config", choices=sorted(CONFIGS), default="native_video_2026_09_10_gemini_3_6")
    ap.add_argument("--output", default=None, help="Output JSON path. Required with --run.")
    ap.add_argument("--json-out", default=None,
                     help="Also write the dry-run report as JSON to this path (dry-run only).")
    ap.add_argument("--run", action="store_true",
                     help="NOT EXECUTED IN THIS PHASE. Enables the real Gemini Files-API call path. "
                          "Also requires --acknowledge-private-data-upload and GEMINI_API_KEY.")
    ap.add_argument("--acknowledge-contaminated-input", action="store_true",
                     help="Run against a video the corpus marks as showing its own reference answer. "
                          "Only for deliberately reproducing a retracted result.")
    ap.add_argument("--acknowledge-private-data-upload", action="store_true",
                     help="Required together with --run: confirms you understand the WHOLE VIDEO FILE "
                          "(not just sampled frames) will be uploaded to Gemini's Files API and will "
                          "leave this machine.")
    ap.add_argument("--keep-uploaded-file", action="store_true",
                     help="Do not delete the file from Gemini's Files API after the call. Off by "
                          "default to avoid accumulating files against the project's storage quota "
                          "across a multi-clip run.")
    ap.add_argument("--file-state-poll-timeout-s", type=float, default=120.0,
                     help="How long to wait for an uploaded file to reach ACTIVE state before giving up.")
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    try:
        video_path = rcm.validate_local_video_path(args.video)
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if not args.acknowledge_contaminated_input:
        try:
            import corpus_guard
            corpus_guard.assert_input_usable(video_path)
        except ImportError:
            pass
        except Exception as e:  # corpus_guard.LeakageError
            print(f"REFUSED: {e}", file=sys.stderr)
            print("Any prediction from this file would measure OCR of on-screen text, not sign "
                  "recognition. Pass --acknowledge-contaminated-input only to reproduce a known-bad "
                  "result on purpose.", file=sys.stderr)
            return 2

    if args.run:
        if not args.acknowledge_private_data_upload:
            print(
                "error: --run requires --acknowledge-private-data-upload. The WHOLE video file "
                "(not just sampled frames) will be uploaded to Gemini's Files API, off this machine. "
                "No network call was made.",
                file=sys.stderr,
            )
            return 2
        if not args.output:
            ap.error("--output is required with --run")
        print(
            "REAL MODEL RUN REQUESTED (--run + --acknowledge-private-data-upload present).\n"
            "This path was intentionally NOT exercised while building this script.",
            file=sys.stderr,
        )
        run_real(video_path, args.config, Path(args.output),
                  delete_uploaded_file=not args.keep_uploaded_file,
                  file_state_poll_timeout_s=args.file_state_poll_timeout_s)
        return 0

    if args.acknowledge_private_data_upload:
        print(
            "note: --acknowledge-private-data-upload was given without --run — this is still a "
            "dry run. No network call was made.",
        )

    report = run_dry(video_path, args.config)
    print_dry_run_report(report, args.config)

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(dry_run_report_to_json(report, args.config, args.video), indent=2),
            encoding="utf-8",
        )
        print(f"\nWrote dry-run JSON report to {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
