"""Core parsing and metrics for the ASL ground-truth evaluator.

Pure standard library, no network calls, no third-party dependencies.
Operates only on local SRT/JSON text files — never touches the corpus
videos.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

TIME_RE = re.compile(
    r"(\d\d):(\d\d):(\d\d)[.,](\d\d\d)\s*-->\s*(\d\d):(\d\d):(\d\d)[.,](\d\d\d)"
)


def _to_seconds(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(path: str | Path) -> list[dict]:
    """Parse a .srt file into [{start, end, text}] (seconds, float)."""
    raw = Path(path).read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", raw.strip())
    segments = []
    for block in blocks:
        lines = [l for l in block.strip().splitlines() if l.strip() != ""]
        if not lines:
            continue
        # Optional leading cue-number line.
        if lines[0].strip().isdigit():
            lines = lines[1:]
        if not lines:
            continue
        m = TIME_RE.search(lines[0])
        if not m:
            continue
        start = _to_seconds(*m.groups()[0:4])
        end = _to_seconds(*m.groups()[4:8])
        text = " ".join(l.strip() for l in lines[1:]).strip()
        segments.append({"start": start, "end": end, "text": text})
    return segments


def parse_prediction_json(path: str | Path) -> list[dict]:
    """Parse a baseline0-shaped prediction JSON into [{start, end, text}]."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    segments = []
    for s in data.get("segments", []):
        segments.append(
            {
                "start": float(s.get("start", 0.0)),
                "end": float(s.get("end", 0.0)),
                "text": (s.get("text") or "").strip(),
            }
        )
    return segments


def build_transcript(segments: list[dict]) -> str:
    return " ".join(s["text"] for s in segments if s.get("text"))


# ---------------------------------------------------------------------------
# Text normalization (documented, conservative)
# ---------------------------------------------------------------------------
_PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Lowercase, strip ordinary punctuation, collapse whitespace.

    Punctuation characters are replaced with a space (not deleted), so
    "don't" -> "don t" rather than "dont" — this avoids silently merging
    two distinct words. No paraphrase matching, no number-word rewriting.
    """
    text = text.lower()
    text = _PUNCT_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    return text


# ---------------------------------------------------------------------------
# Levenshtein alignment (word- or character-level; any hashable sequence)
# ---------------------------------------------------------------------------
def levenshtein_align(ref: list, hyp: list) -> tuple[int, int, int, int]:
    """Return (substitutions, deletions, insertions, total_distance)."""
    n, m = len(ref), len(hyp)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,  # deletion
                d[i][j - 1] + 1,  # insertion
                d[i - 1][j - 1] + cost,  # match / substitution
            )

    i, j = n, m
    sub = deletions = insertions = 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (
            0 if ref[i - 1] == hyp[j - 1] else 1
        ):
            if ref[i - 1] != hyp[j - 1]:
                sub += 1
            i -= 1
            j -= 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            deletions += 1
            i -= 1
        elif j > 0 and d[i][j] == d[i][j - 1] + 1:
            insertions += 1
            j -= 1
        else:  # pragma: no cover - unreachable given DP invariants
            break

    return sub, deletions, insertions, d[n][m]


def _rate(sub: int, deletions: int, insertions: int, ref_len: int, hyp_len: int) -> float:
    if ref_len == 0:
        return 0.0 if hyp_len == 0 else 1.0
    return (sub + deletions + insertions) / ref_len


def text_metrics(ref_text: str, pred_text: str) -> dict:
    ref_norm = normalize_text(ref_text)
    pred_norm = normalize_text(pred_text)

    ref_words = ref_norm.split()
    pred_words = pred_norm.split()
    ws, wd, wi, _ = levenshtein_align(ref_words, pred_words)
    wer = _rate(ws, wd, wi, len(ref_words), len(pred_words))

    ref_chars = list(ref_norm)
    pred_chars = list(pred_norm)
    cs, cd, ci, _ = levenshtein_align(ref_chars, pred_chars)
    cer = _rate(cs, cd, ci, len(ref_chars), len(pred_chars))

    return {
        "reference_words": len(ref_words),
        "prediction_words": len(pred_words),
        "substitutions": ws,
        "deletions": wd,
        "insertions": wi,
        "wer": round(wer, 4),
        "cer": round(cer, 4),
        "char_level": {
            "reference_chars": len(ref_chars),
            "prediction_chars": len(pred_chars),
            "substitutions": cs,
            "deletions": cd,
            "insertions": ci,
        },
        "reference_transcript_normalized": ref_norm,
        "prediction_transcript_normalized": pred_norm,
    }


# ---------------------------------------------------------------------------
# Timing / coverage metrics
# ---------------------------------------------------------------------------
def merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    ivs = sorted((s, e) for s, e in intervals if e > s)
    merged: list[tuple[float, float]] = []
    for s, e in ivs:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def total_duration(intervals: list[tuple[float, float]]) -> float:
    return sum(e - s for s, e in intervals)


def intersect_duration(
    a: list[tuple[float, float]], b: list[tuple[float, float]]
) -> float:
    i = j = 0
    total = 0.0
    while i < len(a) and j < len(b):
        s = max(a[i][0], b[j][0])
        e = min(a[i][1], b[j][1])
        if e > s:
            total += e - s
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return total


def timing_metrics(ref_segments: list[dict], pred_segments: list[dict]) -> dict:
    ref_iv = merge_intervals([(s["start"], s["end"]) for s in ref_segments])
    pred_iv = merge_intervals([(s["start"], s["end"]) for s in pred_segments])

    ref_cov = total_duration(ref_iv)
    pred_cov = total_duration(pred_iv)
    overlap = intersect_duration(ref_iv, pred_iv)
    union = ref_cov + pred_cov - overlap

    precision = (overlap / pred_cov) if pred_cov > 0 else 0.0
    recall = (overlap / ref_cov) if ref_cov > 0 else 0.0
    # Both empty -> trivially identical (nothing to disagree about).
    iou = (overlap / union) if union > 0 else 1.0

    return {
        "reference_coverage_s": round(ref_cov, 3),
        "prediction_coverage_s": round(pred_cov, 3),
        "overlap_s": round(overlap, 3),
        "temporal_precision": round(precision, 4),
        "temporal_recall": round(recall, 4),
        "temporal_iou": round(iou, 4),
    }


# ---------------------------------------------------------------------------
# Optional diagnostic: per-reference-segment best-overlap alignment
# ---------------------------------------------------------------------------
def align_segments(ref_segments: list[dict], pred_segments: list[dict]) -> list[dict]:
    results = []
    for idx, r in enumerate(ref_segments):
        best = None
        best_overlap = 0.0
        for p in pred_segments:
            s = max(r["start"], p["start"])
            e = min(r["end"], p["end"])
            ov = max(0.0, e - s)
            if ov > best_overlap:
                best_overlap = ov
                best = p

        iou = 0.0
        if best is not None:
            r_dur = r["end"] - r["start"]
            p_dur = best["end"] - best["start"]
            union_dur = r_dur + p_dur - best_overlap
            iou = best_overlap / union_dur if union_dur > 0 else 0.0

        results.append(
            {
                "ref_index": idx,
                "ref_start": r["start"],
                "ref_end": r["end"],
                "ref_text": r["text"],
                "matched_prediction_text": best["text"] if best else None,
                "matched_prediction_start": best["start"] if best else None,
                "matched_prediction_end": best["end"] if best else None,
                "overlap_s": round(best_overlap, 3),
                "iou": round(iou, 4),
            }
        )
    return results
