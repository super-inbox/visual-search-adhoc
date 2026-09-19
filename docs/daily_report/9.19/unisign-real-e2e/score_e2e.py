#!/usr/bin/env python3
"""Score the two real-checkpoint Uni-Sign /translate responses (n=2 smoke check).

WER / CER: reuses the repo's existing implementation, unmodified --
`asl-translator/asl-eval/lib.py::text_metrics` (same normalization as the
128-clip benchmark: lowercase, punctuation -> space, collapse whitespace).

BLEU / chrF: the repo has no implementation, so this uses the `sacrebleu`
library's sentence_bleu / sentence_chrf directly (no custom scorer), applied to
the SAME lib.normalize_text()-normalized strings so all four metrics share one
normalization. Sentence-level BLEU on a single ~10-60 word segment is very
noisy; treat it as a rough signal only.

Usage: python3 score_e2e.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT / "asl-translator" / "asl-eval"))
import lib  # noqa: E402  (repo's existing scorer, unmodified)
from sacrebleu.metrics import BLEU, CHRF  # noqa: E402

MANIFEST = (
    REPO_ROOT / "asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv"
)
PRIOR = REPO_ROOT / "docs/daily_report/9.2/asl-baselines/results/unisign_predictions.jsonl"

CLIPS = {
    "short": ("g0uGWjwdOIw_1-8-rgb_front", "short_response.json"),
    "long": ("FzmL8SL6Bow_1-8-rgb_front", "long_response.json"),
    # Identical request re-sent to the same live process (reproducibility probe).
    "long_repeat": ("FzmL8SL6Bow_1-8-rgb_front", "long_response_repeat.json"),
}


def main() -> int:
    manifest = {
        r["how2sign_id"]: r
        for r in csv.DictReader(MANIFEST.open(newline="", encoding="utf-8"))
    }
    prior = {}
    for line in PRIOR.open():
        d = json.loads(line)
        prior[d["clip_id"]] = d

    bleu = BLEU(effective_order=True)  # effective_order: sane sentence-level BLEU
    chrf = CHRF()
    out = {}
    for label, (clip_id, resp_file) in CLIPS.items():
        resp = json.loads((HERE / resp_file).read_text())
        row = manifest[clip_id]
        ref = row["reference_text"]
        hyp = resp["translation"]
        tm = lib.text_metrics(ref, hyp)
        ref_n = tm["reference_transcript_normalized"]
        hyp_n = tm["prediction_transcript_normalized"]
        out[label] = {
            "clip_id": clip_id,
            "manifest_duration_s": float(row["duration_s"]),
            "reference": ref,
            "unisign": hyp,
            "segments_source": [s["source"] for s in resp["segments"]],
            "wer": tm["wer"],
            "cer": tm["cer"],
            "bleu": round(bleu.sentence_score(hyp_n, [ref_n]).score, 2),
            "chrf": round(chrf.sentence_score(hyp_n, [ref_n]).score, 2),
            "reference_words": tm["reference_words"],
            "prediction_words": tm["prediction_words"],
            "prior_benchmark_prediction": prior.get(clip_id, {}).get("prediction"),
            "prior_benchmark_runtime_s": prior.get(clip_id, {}).get("runtime_s"),
        }
    (HERE / "scores.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    for label, d in out.items():
        print(f"== {label.upper()}  {d['clip_id']}  ({d['manifest_duration_s']}s)")
        print(f"REFERENCE: {d['reference']}")
        print(f"UNISIGN:   {d['unisign']}")
        print(
            f"WER={d['wer']}  CER={d['cer']}  BLEU={d['bleu']}  chrF={d['chrf']}  "
            f"(ref {d['reference_words']}w / pred {d['prediction_words']}w)"
        )
        print(f"segments source: {d['segments_source']}")
        print(f"[prior 128-clip benchmark run] {d['prior_benchmark_prediction']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
