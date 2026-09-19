#!/usr/bin/env python3
"""Merge per-segment Uni-Sign outputs (two deterministic views) and score
DIRECT vs SEGMENTED with the SAME conventions as
docs/daily_report/9.19/unisign-real-e2e/score_e2e.py:

  WER / CER : asl-translator/asl-eval/lib.py::text_metrics (unmodified)
  BLEU/chrF : sacrebleu sentence_score (BLEU effective_order=True, CHRF default) on the
              lib.normalize_text()-normalized strings.
Because the direct baseline is re-scored here from its raw response JSON, the script asserts
it reproduces the numbers in the earlier scores.json exactly.

Merge views (no LLM, no ground truth, no paraphrase; text is only ever DELETED, never edited):
  A_naive : chronological join of the raw segment strings with one space.
  B_dedup : for each adjacent pair (running text R, next segment T): tokenise on whitespace;
            compare tokens case-/punctuation-insensitively; find the LONGEST k >= MIN_K with
            R[-k:] == T[:k]; drop those first k tokens of T; append the rest. k<MIN_K -> plain join.
            (Only exact repeated adjacent word runs caused by the overlap are removed.)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "asl-translator" / "asl-eval"))
import lib  # noqa: E402  (repo's existing scorer)
from sacrebleu.metrics import BLEU, CHRF  # noqa: E402

MIN_K = 2
E2E = REPO / "docs/daily_report/9.19/unisign-real-e2e"
MANIFEST_CSV = REPO / "asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv"
CLIP_ID = "FzmL8SL6Bow_1-8-rgb_front"
# fixed, tiny English function-word list for the content-word diagnostic (defined before seeing outputs)
STOP = set("a an the and or but if so of to in on at by for with from as is are was were be been am i you he she it we they "
           "me my your our their his her its this that these those there here what which who whom do does did doing have has had "
           "not no yes just very can will would could should about up out into over then than too also all any some".split())


def tok_norm(t: str) -> str:
    return re.sub(r"[^a-z0-9']", "", t.lower())


def suffix_prefix_k(a: list[str], b: list[str]) -> int:
    na, nb = [tok_norm(x) for x in a], [tok_norm(x) for x in b]
    for k in range(min(len(na), len(nb)), 0, -1):
        if na[-k:] == nb[:k] and all(na[-k:]):
            return k
    return 0


def merge_naive(texts: list[str]) -> str:
    return " ".join(t.strip() for t in texts if t and t.strip())


def merge_dedup(texts: list[str]) -> tuple[str, list[dict]]:
    out: list[str] = []
    log = []
    for i, t in enumerate(x for x in texts if x and x.strip()):
        toks = t.split()
        if not out:
            out = toks
            continue
        k = suffix_prefix_k(out, toks)
        removed = toks[:k] if k >= MIN_K else []
        log.append({"junction": [i - 1, i], "exact_suffix_prefix_words": k, "removed": " ".join(removed) or None})
        out = out + toks[len(removed):]
    return " ".join(out), log


def words(s: str) -> list[str]:
    return lib.normalize_text(s).split()


def rouge1(ref: str, hyp: str, content_only: bool = False) -> dict:
    r, h = words(ref), words(hyp)
    if content_only:
        r, h = [w for w in r if w not in STOP], [w for w in h if w not in STOP]
    cr, ch = Counter(r), Counter(h)
    ov = sum((cr & ch).values())
    rec, prec = ov / max(1, len(r)), ov / max(1, len(h))
    return {"recall": round(rec, 4), "precision": round(prec, 4),
            "f1": round(2 * rec * prec / (rec + prec), 4) if rec + prec else 0.0, "ref_n": len(r), "hyp_n": len(h), "overlap_n": ov}


def repeated_ngrams(s: str, n: int = 3) -> int:
    w = words(s)
    c = Counter(zip(*[w[i:] for i in range(n)]))
    return sum(v - 1 for v in c.values() if v > 1)


def longest_common_run(a: list[str], b: list[str]) -> list[str]:
    na, nb = [tok_norm(x) for x in a], [tok_norm(x) for x in b]
    best = (0, 0)
    for i in range(len(na)):
        for j in range(len(nb)):
            k = 0
            while i + k < len(na) and j + k < len(nb) and na[i + k] == nb[j + k] and na[i + k]:
                k += 1
            if k > best[0]:
                best = (k, i)
    return na[best[1]:best[1] + best[0]]


def score(ref: str, hyp: str) -> dict:
    bleu, chrf = BLEU(effective_order=True), CHRF()
    tm = lib.text_metrics(ref, hyp)
    ref_n, hyp_n = tm["reference_transcript_normalized"], tm["prediction_transcript_normalized"]
    return {"wer": tm["wer"], "cer": tm["cer"], "bleu": round(bleu.sentence_score(hyp_n, [ref_n]).score, 2),
            "chrf": round(chrf.sentence_score(hyp_n, [ref_n]).score, 2),
            "reference_words": tm["reference_words"], "prediction_words": tm["prediction_words"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    import csv
    row = next(r for r in csv.DictReader(MANIFEST_CSV.open(newline="", encoding="utf-8")) if r["how2sign_id"] == CLIP_ID)
    ref = row["reference_text"]
    pred = json.loads(Path(a.predictions).read_text())
    man = json.loads(Path(a.manifest).read_text())
    segs = sorted(pred["segments"], key=lambda r: r["segment_id"])
    assert [s["segment_id"] for s in segs] == [s["segment_id"] for s in man["segments"]], "segment set mismatch"
    ok = all(s["http_status"] == 200 and s["text"] is not None for s in segs)
    texts = [s["text"] or "" for s in segs]

    naive = merge_naive(texts)
    dedup, dedup_log = merge_dedup(texts)

    d1 = json.loads((E2E / "long_response.json").read_text())["translation"]
    d2 = json.loads((E2E / "long_response_repeat.json").read_text())["translation"]
    prev = json.loads((E2E / "scores.json").read_text())
    views = {"A_direct_run1": d1, "A_direct_run2_repeat": d2, "B_segmented_naive": naive, "C_segmented_dedup": dedup}
    metrics = {k: score(ref, v) for k, v in views.items()}
    for k, pk in (("A_direct_run1", "long"), ("A_direct_run2_repeat", "long_repeat")):
        for m in ("wer", "cer", "bleu", "chrf"):
            assert metrics[k][m] == prev[pk][m], f"direct baseline {k}.{m} does not reproduce scores.json"

    direct_rt = {"run1": 101.03806, "run2_repeat": 99.84442}      # long_curl_meta.txt / long_repeat_curl_meta.txt
    seg_rt = round(sum(s["runtime_sec"] for s in segs), 2)
    tot_frames_seg = sum(s["frames_seen_by_service_tqdm_total"] or 0 for s in segs)
    extras = {}
    for k, v in views.items():
        extras[k] = {"rouge1_all_words": rouge1(ref, v), "rouge1_content_words": rouge1(ref, v, True),
                     "repeated_word_trigram_count": repeated_ngrams(v, 3), "repeated_word_5gram_count": repeated_ngrams(v, 5),
                     "prediction_to_reference_word_ratio": round(len(words(v)) / len(words(ref)), 3)}

    # Segment 0 was the first request to a fresh container, so its runtime includes the one-time ~132 MB rtmlib
    # weight download (visible in segment_container_log_filtered.txt). Estimate the warm total from the per-frame
    # rate of segments 1..N (runtime is ~linear in frames: 0.307-0.320 s/frame there). ESTIMATE, labelled as such.
    rest = segs[1:]
    rate = sum(s["runtime_sec"] for s in rest) / sum(s["frames_seen_by_service_tqdm_total"] for s in rest)
    cold = segs[0]["runtime_sec"] - rate * segs[0]["frames_seen_by_service_tqdm_total"]
    probe_p = Path(a.predictions).parent / "determinism_probe_seg2.json"
    probe = None
    if probe_p.exists():
        pr = json.loads(probe_p.read_text())["segments"][0]
        probe = {"segment_id": pr["segment_id"], "identical_to_first_run": pr["text"] == segs[pr["segment_id"]]["text"],
                 "text": pr["text"], "runtime_sec": pr["runtime_sec"],
                 "note": "single extra call, NOT used in any score; segment has 102 frames (<256) so no random sampling"}

    junctions = []
    for s0, s1 in zip(segs, segs[1:]):
        wa, wb = (s0["text"] or "").split(), (s1["text"] or "").split()
        junctions.append({"pair": [s0["segment_id"], s1["segment_id"]],
                          "overlap_window_sec": [s1["start_sec"], s0["end_sec"]],
                          "overlap_sec": round(s0["end_sec"] - s1["start_sec"], 3),
                          "exact_suffix_prefix_words": suffix_prefix_k(wa, wb),
                          "longest_common_word_run_anywhere": " ".join(longest_common_run(wa, wb)),
                          "texts_identical": lib.normalize_text(" ".join(wa)) == lib.normalize_text(" ".join(wb))})

    out = {
        "clip_id": CLIP_ID, "reference": ref,
        "scoring_convention": "identical to docs/daily_report/9.19/unisign-real-e2e/score_e2e.py: WER/CER=asl-eval/lib.py::text_metrics; "
                              "BLEU=sacrebleu sentence_score(effective_order=True), chrF=sacrebleu CHRF sentence_score, both on lib.normalize_text() strings. "
                              "Sentence-level BLEU on one ~78-word item is very noisy.",
        "direct_baseline_reproduced_exactly_from_raw_json": True,
        "n": 1, "all_segments_http_200": ok,
        "merge_params": {"min_k_words_to_drop": MIN_K, "matching": "case/punctuation-insensitive exact word equality"},
        "texts": views,
        "metrics": metrics,
        "diagnostics_exploratory": extras,
        "dedup_log": dedup_log,
        "determinism_probe_segment2": probe,
        "adjacent_overlap_analysis": junctions,
        "cost": {
            "direct": {"model_calls": 1, "runtime_sec_run1": direct_rt["run1"], "runtime_sec_run2_repeat": direct_rt["run2_repeat"],
                       "frames_extracted": 618, "frames_reaching_model": 256, "segments_requiring_random_256_sampling": 1,
                       "frames_dropped_at_random": 362},
            "segmented": {"model_calls": len(segs), "runtime_sec_sum_of_calls": seg_rt,
                          "runtime_sec_per_segment": [s["runtime_sec"] for s in segs],
                          "frames_reaching_model_total": tot_frames_seg,
                          "frames_per_segment": [s["frames_seen_by_service_tqdm_total"] for s in segs],
                          "frames_extra_vs_video_due_to_overlap": tot_frames_seg - 618,
                          "segments_requiring_random_256_sampling": sum(1 for s in segs if s["random_256_sampling_occurred"]),
                          "seconds_per_frame_segments_1_to_N": round(rate, 4),
                          "cold_start_overhead_in_segment0_estimate_sec": round(cold, 1),
                          "runtime_sec_warm_estimate": round(seg_rt - cold, 1),
                          "warm_estimate_ratio_vs_direct_run1": round((seg_rt - cold) / direct_rt["run1"], 2),
                          "raw_sum_ratio_vs_direct_run1": round(seg_rt / direct_rt["run1"], 2),
                          "frames_dropped_at_random": 0 if not any(s["random_256_sampling_occurred"] for s in segs) else None},
        },
    }
    Path(a.out).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps({"metrics": metrics, "cost": out["cost"], "junctions": junctions, "dedup_log": dedup_log}, indent=2, ensure_ascii=False))
    print("\nNAIVE :", naive, "\nDEDUP :", dedup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
