#!/usr/bin/env python3
"""Score Batch 2 of the manually-run SignCaption pilot (10 new How2Sign v2 clips) and
combine it with the already-scored original 5-clip pilot into a matched-15 comparison.

PREPARED BUT NOT EXECUTED TO COMPLETION. This script makes no network calls, no
Gemini/SignCaption API calls, and does not run any experiment — it only reads local
files: the frozen benchmark manifest/references, the already-scored Curify/Uni-Sign/
native-video result files, the original 5-clip pilot's own already-audited
per_clip_comparison.json (read-only, never re-derived or modified), and whatever the
human operator has manually placed under
clips/<clip_id>/signcaption_result.{srt,txt} for the 10 Batch-2 clips.

SignCaption's output is scored strictly as a PREDICTION being benchmarked against the
frozen reference — it is never treated as ground truth, and it never overwrites or
corrects any other system's, or the original 5-clip pilot's, existing recorded result.

Reports, without fabricating any missing prediction:
  - Batch-2-only aggregate (n up to 10, whatever is actually filled in)
  - Combined aggregate across all 15 pilot clips (5 original + 10 Batch-2), official
    corpus-level WER/CER/BLEU/chrF (edit counts summed then divided once; BLEU/chrF via
    one sacrebleu.corpus_score() call over all available hyp/ref pairs at once — the same
    convention independently audited for the original 5-clip pilot, see
    docs/daily_report/9.13/signcaption-calculation-audit/CALCULATION_AUDIT.md)
  - SignCaption vs. Uni-Sign vs. Curify frame-baseline on all 15 (all three are 100%
    available for all 15 by construction of the Batch-2 eligibility filter)
  - SignCaption vs. Uni-Sign vs. Curify vs. native-video on the matched 8/15 subset ONLY
    (the 5 original clips + the 3 Batch-2 diagnostic-12 clips that have a valid
    native-video prediction) — never extrapolated to the other 7 Batch-2 clips, which
    have no native-video prediction and none is invented here.
  - Semantic-adequacy / topic-mismatch / genuine-recovery fields: carried over from the
    already-published human/text review for the original 5 (RESULTS.md), left explicitly
    null (never inferred from WER) for Batch-2 clips until a human review is done.

Usage (do not run --write-results until some/all of the 10 Batch-2 clips.README.md-implied
result files are placed):
    python3 asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/score_batch2_and_combined.py \\
        --write-results

    # Inspect without writing anything:
    python3 asl-translator/evaluation/manual_signcaption/how2sign_v2_batch2_10clip/score_batch2_and_combined.py \\
        --dry-run
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
ASL_EVAL_DIR = REPO_ROOT / "asl-translator" / "asl-eval"
sys.path.insert(0, str(ASL_EVAL_DIR))
import lib  # noqa: E402  (repo's own parse_srt / build_transcript / text_metrics)

BENCH_DIR = REPO_ROOT / "asl-translator" / "data" / "public_benchmarks" / "how2sign_v2"
REFERENCES_DIR = BENCH_DIR / "references"
RESULTS_ROOT = REPO_ROOT / "asl-translator" / "evaluation" / "results" / "how2sign_v2"
CLIPS_DIR = HERE / "clips"
OUT_DIR = HERE / "results"

BASELINE_PER_CLIP = RESULTS_ROOT / "curify_gemini_3_6_2026_09_04" / "per_clip_results.json"
UNISIGN_PER_CLIP = RESULTS_ROOT / "unisign" / "per_clip_results.json"
NATIVE_VIDEO_PER_CLIP = RESULTS_ROOT / "curify_gemini_native_video_2026_09_10" / "per_clip_results.json"

# Original 5-clip pilot's own already-scored, already-audited results — read-only.
ORIGINAL5_RESULTS = (
    REPO_ROOT / "asl-translator" / "evaluation" / "manual_signcaption" / "how2sign_v2_5clip"
    / "results" / "per_clip_comparison.json"
)

BATCH2_CLIP_IDS = [
    "g2NA_eBUcH8_0-3-rgb_front",
    "G19uBylwQww_1-2-rgb_front",
    "fZM3IcM2Xs4_14_15_16-10-rgb_front",
    "g2nvBjp0loQ_4-3-rgb_front",
    "g05yGRoZE10_1-8-rgb_front",
    "FzQPg4aqNYc_13-1-rgb_front",
    "G3RvsnzQrXQ_3-10-rgb_front",
    "g0UUmEkoT1w_2-10-rgb_front",
    "FZCEymcpq7I_14-1-rgb_front",
    "G1jsDl1mVvk_1-1-rgb_front",
]

ORIGINAL5_CLIP_IDS = [
    "FzmL8SL6Bow_1-8-rgb_front",
    "92V3oH63zbQ_5-1-rgb_front",
    "G05uFub3YFc_9-2-rgb_front",
    "fzNnTgHa1lM_2-5-rgb_front",
    "-g0sqksgyc4_3-2-rgb_front",
]

# Already-published human/text semantic review for the original 5 (RESULTS.md §5) —
# carried over here as citation, not re-derived or inferred from any metric. Batch-2
# clips get null placeholders until the same manual review is done for them.
ORIGINAL5_SEMANTIC_REVIEW = {
    "FzmL8SL6Bow_1-8-rgb_front": {"semantic_adequacy": 0, "topic_mismatch": "yes", "genuine_recovery": "no"},
    "92V3oH63zbQ_5-1-rgb_front": {"semantic_adequacy": 0, "topic_mismatch": "yes", "genuine_recovery": "no"},
    "G05uFub3YFc_9-2-rgb_front": {"semantic_adequacy": 1, "topic_mismatch": "no (domain-level)", "genuine_recovery": "qualified"},
    "fzNnTgHa1lM_2-5-rgb_front": {"semantic_adequacy": 2, "topic_mismatch": "no", "genuine_recovery": "yes"},
    "-g0sqksgyc4_3-2-rgb_front": {"semantic_adequacy": 0, "topic_mismatch": "yes", "genuine_recovery": "no"},
}


def _load_per_clip(path: Path) -> dict:
    if not path.exists():
        return {}
    return {r["how2sign_id"]: r for r in json.loads(path.read_text(encoding="utf-8"))}


def _corpus_bleu_chrf_multi(refs: list[str], hyps: list[str]) -> dict:
    """One sacrebleu.corpus_score() call over ALL given hyp/ref pairs at once — the
    official corpus-level convention, not a per-clip average. Matches the independently
    audited convention used for the original 5-clip pilot's RESULTS.md §3b table."""
    if not refs:
        return {"bleu": None, "chrf": None}
    try:
        import sacrebleu
    except ImportError:
        return {"bleu": None, "chrf": None, "note": "sacrebleu not installed in this environment"}
    bleu = sacrebleu.BLEU().corpus_score(hyps, [refs])
    chrf = sacrebleu.CHRF().corpus_score(hyps, [refs])
    return {"bleu": round(bleu.score, 4), "chrf": round(chrf.score, 4)}


def _corpus_wer_cer_from_texts(pairs: list[tuple[str, str]]) -> dict:
    """pairs = [(ref_text, hyp_text), ...]. Sums word/char edit-op counts across all pairs
    first, then divides once — the same micro-averaged convention audited for the
    original 5-clip pilot (never a mean of per-clip WER/CER)."""
    tot_ref_words = tot_sub = tot_del = tot_ins = 0
    tot_ref_chars = tot_csub = tot_cdel = tot_cins = 0
    for ref, hyp in pairs:
        tm = lib.text_metrics(ref, hyp)
        tot_ref_words += tm["reference_words"]
        tot_sub += tm["substitutions"]; tot_del += tm["deletions"]; tot_ins += tm["insertions"]
        cl = tm["char_level"]
        tot_ref_chars += cl["reference_chars"]
        tot_csub += cl["substitutions"]; tot_cdel += cl["deletions"]; tot_cins += cl["insertions"]
    return {
        "corpus_wer": round((tot_sub + tot_del + tot_ins) / tot_ref_words, 4) if tot_ref_words else None,
        "corpus_cer": round((tot_csub + tot_cdel + tot_cins) / tot_ref_chars, 4) if tot_ref_chars else None,
    }


def load_signcaption_result(clip_id: str) -> dict:
    """Read the manually-placed SignCaption export for one Batch-2 clip. Same
    three-way status convention as the original pilot's score_pilot.py: missing /
    empty_prediction / parse_failure / success — never silently merged or fabricated."""
    clip_dir = CLIPS_DIR / clip_id
    srt_path = clip_dir / "signcaption_result.srt"
    txt_path = clip_dir / "signcaption_result.txt"

    if srt_path.exists():
        raw = srt_path.read_text(encoding="utf-8-sig", errors="replace")
        if raw.strip() == "":
            return {"status": "empty_prediction", "prediction_text": "", "source_file": str(srt_path.relative_to(REPO_ROOT))}
        try:
            segments = lib.parse_srt(srt_path)
        except Exception as e:
            return {"status": "parse_failure", "prediction_text": None,
                     "source_file": str(srt_path.relative_to(REPO_ROOT)), "error": str(e)}
        if not segments:
            return {"status": "parse_failure", "prediction_text": None,
                     "source_file": str(srt_path.relative_to(REPO_ROOT)),
                     "error": "file is non-empty but no valid SRT cue block was found"}
        text = lib.build_transcript(segments)
        return {"status": "success", "prediction_text": text,
                "source_file": str(srt_path.relative_to(REPO_ROOT)), "segments": segments}

    if txt_path.exists():
        raw = txt_path.read_text(encoding="utf-8", errors="replace").strip()
        if raw == "":
            return {"status": "empty_prediction", "prediction_text": "", "source_file": str(txt_path.relative_to(REPO_ROOT))}
        return {"status": "success", "prediction_text": raw,
                "source_file": str(txt_path.relative_to(REPO_ROOT))}

    return {"status": "missing", "prediction_text": None, "source_file": None}


def score_batch2_clip(clip_id: str, baseline_by_id: dict, unisign_by_id: dict, native_by_id: dict) -> dict:
    ref_path = REFERENCES_DIR / f"{clip_id}.srt"
    ref_segments = lib.parse_srt(ref_path)
    ref_text = lib.build_transcript(ref_segments)

    sc = load_signcaption_result(clip_id)
    row = {
        "clip_id": clip_id,
        "batch": 2,
        "reference_text": ref_text,
        "signcaption_status": sc["status"],
        "signcaption_source_file": sc.get("source_file"),
        "semantic_adequacy": None,
        "topic_mismatch": None,
        "genuine_recovery": None,
    }

    if sc["status"] == "success":
        tm = lib.text_metrics(ref_text, sc["prediction_text"])
        bc = _corpus_bleu_chrf_multi([ref_text], [sc["prediction_text"]])
        row.update({
            "signcaption_prediction_text": sc["prediction_text"],
            "signcaption_wer": tm["wer"], "signcaption_cer": tm["cer"],
            "signcaption_bleu": bc["bleu"], "signcaption_chrf": bc["chrf"],
        })
    elif sc["status"] == "empty_prediction":
        tm = lib.text_metrics(ref_text, "")
        row.update({
            "signcaption_prediction_text": "",
            "signcaption_wer": tm["wer"], "signcaption_cer": tm["cer"],
            "signcaption_bleu": 0.0, "signcaption_chrf": 0.0,
        })
    else:
        row.update({
            "signcaption_prediction_text": None,
            "signcaption_wer": None, "signcaption_cer": None,
            "signcaption_bleu": None, "signcaption_chrf": None,
        })
        if sc["status"] == "parse_failure":
            row["signcaption_parse_error"] = sc.get("error")

    b = baseline_by_id.get(clip_id); u = unisign_by_id.get(clip_id); n = native_by_id.get(clip_id)
    row["curify_frame_baseline_prediction_text"] = (b or {}).get("prediction_text")
    row["curify_frame_baseline_wer"] = (b or {}).get("wer") if b and b.get("status") == "success" else None
    row["unisign_prediction_text"] = (u or {}).get("prediction_text")
    row["unisign_wer"] = (u or {}).get("wer") if u and u.get("status") == "success" else None
    row["native_video_available"] = bool(n and n.get("status") == "success")
    row["native_video_prediction_text"] = (n or {}).get("prediction_text") if row["native_video_available"] else None
    row["native_video_wer"] = (n or {}).get("wer") if row["native_video_available"] else None
    return row


def load_original5_rows() -> list[dict]:
    """Read-only: the original 5-clip pilot's own already-scored, already-audited
    per_clip_comparison.json. Never re-derived, never modified."""
    if not ORIGINAL5_RESULTS.exists():
        raise SystemExit(
            f"Original 5-clip pilot results not found at {ORIGINAL5_RESULTS} — "
            "run/inspect that pilot first; this script does not recompute it."
        )
    data = json.loads(ORIGINAL5_RESULTS.read_text(encoding="utf-8"))
    native_by_id = _load_per_clip(NATIVE_VIDEO_PER_CLIP)
    rows = []
    for r in data:
        cid = r["clip_id"]
        row = dict(r)
        row["batch"] = 1
        n = native_by_id.get(cid)
        row["native_video_available"] = bool(n and n.get("status") == "success")
        row["native_video_prediction_text"] = r.get("native_video_prediction_text")
        row["native_video_wer"] = r.get("native_video_wer")
        sem = ORIGINAL5_SEMANTIC_REVIEW.get(cid, {})
        row["semantic_adequacy"] = sem.get("semantic_adequacy")
        row["topic_mismatch"] = sem.get("topic_mismatch")
        row["genuine_recovery"] = sem.get("genuine_recovery")
        rows.append(row)
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write-results", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    baseline_by_id = _load_per_clip(BASELINE_PER_CLIP)
    unisign_by_id = _load_per_clip(UNISIGN_PER_CLIP)
    native_by_id = _load_per_clip(NATIVE_VIDEO_PER_CLIP)

    batch2_rows = [score_batch2_clip(c, baseline_by_id, unisign_by_id, native_by_id) for c in BATCH2_CLIP_IDS]
    original5_rows = load_original5_rows()
    combined_rows = original5_rows + batch2_rows

    n_success_b2 = sum(1 for r in batch2_rows if r["signcaption_status"] == "success")
    n_missing_b2 = sum(1 for r in batch2_rows if r["signcaption_status"] == "missing")
    print(f"Batch 2 — {len(batch2_rows)} clips: success={n_success_b2} missing={n_missing_b2} "
          f"other={len(batch2_rows) - n_success_b2 - n_missing_b2}")
    for r in batch2_rows:
        print(f"  {r['clip_id']:38s} signcaption_status={r['signcaption_status']:16s} wer={r['signcaption_wer']}")

    print(f"\nCombined pilot — {len(combined_rows)} clips total "
          f"({len(original5_rows)} original + {len(batch2_rows)} Batch 2)")

    def aggregate(rows: list[dict], system: str) -> dict:
        """system in {'signcaption', 'curify_frame_baseline', 'unisign', 'native_video'}."""
        text_field = {
            "signcaption": ("reference_text", "signcaption_prediction_text", "signcaption_status", "success"),
            "curify_frame_baseline": ("reference_text", "curify_frame_baseline_prediction_text", None, None),
            "unisign": ("reference_text", "unisign_prediction_text", None, None),
            "native_video": ("reference_text", "native_video_prediction_text", None, None),
        }[system]
        ref_f, hyp_f, status_f, want_status = text_field
        pairs, refs, hyps = [], [], []
        for r in rows:
            if system == "native_video" and not r.get("native_video_available"):
                continue
            if status_f and r.get(status_f) != want_status:
                continue
            ref, hyp = r.get(ref_f), r.get(hyp_f)
            if ref is None or hyp is None:
                continue
            pairs.append((ref, hyp)); refs.append(ref); hyps.append(hyp)
        if not pairs:
            return {"n": 0, "corpus_wer": None, "corpus_cer": None, "corpus_bleu": None, "corpus_chrf": None}
        wc = _corpus_wer_cer_from_texts(pairs)
        bc = _corpus_bleu_chrf_multi(refs, hyps)
        return {"n": len(pairs), **wc, "corpus_bleu": bc["bleu"], "corpus_chrf": bc["chrf"]}

    print("\n=== Matched-15 corpus aggregates (Curify / Uni-Sign always n=15; SignCaption n=however-many are filled) ===")
    for system in ["curify_frame_baseline", "unisign", "signcaption"]:
        agg = aggregate(combined_rows, system)
        print(f"  {system:24s} {agg}")

    print("\n=== Matched-8/15 native-video subset (Curify / Uni-Sign / native-video / SignCaption, only where native-video succeeded) ===")
    native_subset = [r for r in combined_rows if r.get("native_video_available")]
    print(f"  clips in native-video-matched subset: {len(native_subset)} -> {[r['clip_id'] for r in native_subset]}")
    for system in ["curify_frame_baseline", "unisign", "native_video", "signcaption"]:
        agg = aggregate(native_subset, system)
        print(f"  {system:24s} {agg}")

    if args.dry_run or not args.write_results:
        print("\n(dry run / no --write-results — nothing written)")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "batch2_per_clip.json").write_text(json.dumps(batch2_rows, indent=2), encoding="utf-8")
    (OUT_DIR / "combined15_per_clip.json").write_text(json.dumps(combined_rows, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_DIR / 'batch2_per_clip.json'} and {OUT_DIR / 'combined15_per_clip.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
