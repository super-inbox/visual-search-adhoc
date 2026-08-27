#!/usr/bin/env python3
"""Deterministic tests for the ASL evaluation scaffold.

Run with:
    python3 -m unittest tools/asl-eval/test_evaluate.py -v

Uses synthetic in-memory/tempfile fixtures except where explicitly testing
SRT parsing against the real corpus reference files (read-only).
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = REPO_ROOT / "data" / "asl_corpus"


def _write(tmp_dir: Path, name: str, content: str) -> Path:
    p = tmp_dir / name
    p.write_text(content, encoding="utf-8")
    return p


def _prediction_json(segments: list[dict]) -> str:
    return json.dumps({"project_id": "x", "video": "v", "producer": "p", "warning": "w", "segments": segments})


class TestSrtParsing(unittest.TestCase):
    def test_155_has_six_segments(self):
        segs = lib.parse_srt(CORPUS_ROOT / "ground_truth" / "155_demo_asl-demo-translation_26.7s.srt")
        self.assertEqual(len(segs), 6)

    def test_1252_has_eleven_segments(self):
        segs = lib.parse_srt(CORPUS_ROOT / "ground_truth" / "1252_1000016397_76.8s.srt")
        self.assertEqual(len(segs), 11)


class TestWer(unittest.TestCase):
    def test_identity_is_zero(self):
        m = lib.text_metrics("I have three of them.", "I have three of them.")
        self.assertEqual(m["wer"], 0.0)
        self.assertEqual((m["substitutions"], m["deletions"], m["insertions"]), (0, 0, 0))

    def test_single_substitution(self):
        m = lib.text_metrics("I like coffee", "I love coffee")
        self.assertEqual(m["substitutions"], 1)
        self.assertEqual(m["deletions"], 0)
        self.assertEqual(m["insertions"], 0)
        self.assertAlmostEqual(m["wer"], 1 / 3, places=4)

    def test_insertion(self):
        # hyp has one extra word relative to ref
        m = lib.text_metrics("I like coffee", "I really like coffee")
        self.assertEqual(m["insertions"], 1)
        self.assertEqual(m["substitutions"], 0)
        self.assertEqual(m["deletions"], 0)
        self.assertAlmostEqual(m["wer"], 1 / 3, places=4)

    def test_deletion(self):
        # hyp is missing one word relative to ref
        m = lib.text_metrics("I really like coffee", "I like coffee")
        self.assertEqual(m["deletions"], 1)
        self.assertEqual(m["substitutions"], 0)
        self.assertEqual(m["insertions"], 0)
        self.assertAlmostEqual(m["wer"], 1 / 4)

    def test_empty_prediction_does_not_crash(self):
        m = lib.text_metrics("I like coffee", "")
        self.assertEqual(m["prediction_words"], 0)
        self.assertEqual(m["deletions"], 3)
        self.assertEqual(m["wer"], 1.0)

    def test_empty_reference_and_prediction(self):
        m = lib.text_metrics("", "")
        self.assertEqual(m["wer"], 0.0)
        self.assertEqual(m["cer"], 0.0)


class TestTimingMetrics(unittest.TestCase):
    def test_identical_intervals_are_perfect(self):
        ref = [{"start": 0.0, "end": 5.0, "text": "a"}, {"start": 6.0, "end": 8.0, "text": "b"}]
        pred = [{"start": 0.0, "end": 5.0, "text": "x"}, {"start": 6.0, "end": 8.0, "text": "y"}]
        t = lib.timing_metrics(ref, pred)
        self.assertEqual(t["temporal_precision"], 1.0)
        self.assertEqual(t["temporal_recall"], 1.0)
        self.assertEqual(t["temporal_iou"], 1.0)

    def test_partial_overlap(self):
        ref = [{"start": 0.0, "end": 10.0, "text": "a"}]
        pred = [{"start": 5.0, "end": 15.0, "text": "x"}]
        t = lib.timing_metrics(ref, pred)
        # overlap = 5s, ref_cov=10, pred_cov=10, union=15
        self.assertAlmostEqual(t["overlap_s"], 5.0)
        self.assertAlmostEqual(t["temporal_precision"], 0.5)
        self.assertAlmostEqual(t["temporal_recall"], 0.5)
        self.assertAlmostEqual(t["temporal_iou"], 5.0 / 15.0, places=4)

    def test_no_predictions(self):
        ref = [{"start": 0.0, "end": 10.0, "text": "a"}]
        pred = []
        t = lib.timing_metrics(ref, pred)
        self.assertEqual(t["prediction_coverage_s"], 0.0)
        self.assertEqual(t["temporal_precision"], 0.0)
        self.assertEqual(t["temporal_recall"], 0.0)
        self.assertEqual(t["temporal_iou"], 0.0)


class TestEvaluatorEndToEnd(unittest.TestCase):
    def test_synthetic_identical_prediction_gives_wer_zero(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            srt = _write(
                tmp,
                "ref.srt",
                "1\n00:00:00,000 --> 00:00:02,000\nHello there.\n\n"
                "2\n00:00:03,000 --> 00:00:05,000\nHow are you?\n",
            )
            pred = _write(
                tmp,
                "pred.json",
                _prediction_json(
                    [
                        {"line": 1, "start": 0.0, "end": 2.0, "text": "Hello there."},
                        {"line": 2, "start": 3.0, "end": 5.0, "text": "How are you?"},
                    ]
                ),
            )
            ref_segs = lib.parse_srt(srt)
            pred_segs = lib.parse_prediction_json(pred)
            self.assertEqual(len(ref_segs), 2)
            m = lib.text_metrics(lib.build_transcript(ref_segs), lib.build_transcript(pred_segs))
            self.assertEqual(m["wer"], 0.0)
            self.assertEqual(m["cer"], 0.0)
            t = lib.timing_metrics(ref_segs, pred_segs)
            self.assertEqual(t["temporal_iou"], 1.0)


class TestEvaluationSetManifest(unittest.TestCase):
    def setUp(self):
        manifest_path = CORPUS_ROOT / "evaluation_set.json"
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.by_id = {i["video_id"]: i for i in self.manifest["items"]}

    def test_155_is_verified_gold(self):
        self.assertEqual(self.by_id["155_demo_asl-demo-translation_26.7s"]["reference_status"], "verified_gold")
        self.assertTrue(self.by_id["155_demo_asl-demo-translation_26.7s"]["usable_for_official_metrics"])

    def test_1252_is_verified_gold(self):
        self.assertEqual(self.by_id["1252_1000016397_76.8s"]["reference_status"], "verified_gold")
        self.assertTrue(self.by_id["1252_1000016397_76.8s"]["usable_for_official_metrics"])

    def test_1320_is_candidate_reference(self):
        item = self.by_id["1320_1000022357_137.2s"]
        self.assertEqual(item["reference_status"], "candidate_reference")
        self.assertFalse(item["usable_for_official_metrics"])

    def test_1434_is_not_in_items(self):
        self.assertNotIn("1434_screenrec_youtube_16.6s", self.by_id)


if __name__ == "__main__":
    unittest.main()
