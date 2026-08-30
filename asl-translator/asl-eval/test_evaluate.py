#!/usr/bin/env python3
"""Deterministic tests for the ASL evaluation scaffold.

Run with:
    python3 -m unittest asl-translator/asl-eval/test_evaluate.py -v

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
import corpus_guard  # noqa: E402
import lib  # noqa: E402

# This file lives at asl-translator/asl-eval/test_evaluate.py — one level up
# is asl-translator/, which is the root all corpus paths are anchored to.
# Explicit, not derived from a fixed depth-from-repo-root assumption.
ASL_TRANSLATOR_ROOT = Path(__file__).resolve().parents[1]
CORPUS_ROOT = ASL_TRANSLATOR_ROOT / "data" / "asl_corpus"


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

    def test_155_is_excluded_for_label_leakage(self):
        """155 was the corpus's primary anchor until 2026-08-30.

        Its input was the caption-burned demo OUTPUT, so its scores measured OCR.
        This test is the tripwire against quietly promoting it back without a
        prediction generated from the clean input.
        """
        self.assertNotIn("155_demo_asl-demo-translation_26.7s", self.by_id)
        excluded = {e["video_id"]: e for e in self.manifest["excluded"]}
        self.assertIn("155_demo_asl-demo-translation_26.7s", excluded)
        self.assertEqual(excluded["155_demo_asl-demo-translation_26.7s"]["reason"],
                         "label_was_burned_into_input")

    def test_only_one_item_is_official(self):
        """As of 2026-08-30 exactly one item can produce a defensible accuracy number.

        If this starts failing because the count went up, good -- but check that the
        new item's input does not contain its own answer before relaxing it.
        """
        official = [i for i in self.manifest["items"] if i.get("usable_for_official_metrics")]
        self.assertEqual([i["video_id"] for i in official], ["1252_1000016397_76.8s"])

    def test_every_official_item_is_leak_free(self):
        for item in self.manifest["items"]:
            if not item.get("usable_for_official_metrics"):
                continue
            with self.subTest(video=item["video_id"]):
                self.assertFalse(item.get("label_in_input"),
                                 "an item whose input shows its own answer cannot be official")

    def test_flagged_items_declare_a_verified_mask(self):
        for item in self.manifest["items"]:
            if not item.get("label_in_input"):
                continue
            with self.subTest(video=item["video_id"]):
                mask = item.get("input_mask") or {}
                self.assertTrue(mask.get("masked_input"))
                self.assertTrue(mask.get("verified_clean"))
                self.assertEqual(Path(mask["masked_input"]).name, Path(item["video"]).name,
                                 "the item must point at its masked input, not the raw source")

    def test_1252_is_verified_gold(self):
        self.assertEqual(self.by_id["1252_1000016397_76.8s"]["reference_status"], "verified_gold")
        self.assertTrue(self.by_id["1252_1000016397_76.8s"]["usable_for_official_metrics"])

    def test_1320_is_candidate_reference(self):
        item = self.by_id["1320_1000022357_137.2s"]
        self.assertEqual(item["reference_status"], "candidate_reference")
        self.assertFalse(item["usable_for_official_metrics"])

    def test_1434_is_not_in_items(self):
        self.assertNotIn("1434_screenrec_youtube_16.6s", self.by_id)


class TestLeakageGuard(unittest.TestCase):
    """The guard that refuses to score a video showing its own answer."""

    def test_refuses_a_retracted_prediction(self):
        pred = CORPUS_ROOT / "predictions_eval" / "155_demo_asl-demo-translation_26.7s_temperature0.json"
        if not pred.exists():
            self.skipTest("retracted prediction not present")
        with self.assertRaises(corpus_guard.LeakageError):
            corpus_guard.assert_prediction_usable(pred)

    def test_allows_a_clean_prediction(self):
        pred = CORPUS_ROOT / "predictions_eval" / "1252_1000016397_76.8s_temperature0.json"
        if not pred.exists():
            self.skipTest("clean prediction not present")
        corpus_guard.assert_prediction_usable(pred)  # must not raise

    def test_refuses_a_burned_reference_render(self):
        for name in ("155_demo_asl-demo-translation_26.7s_burned_marketing.mp4",
                     "1320_1000022357_137.2s_burned.mp4"):
            with self.subTest(video=name):
                with self.assertRaises(corpus_guard.LeakageError):
                    corpus_guard.assert_input_usable(name)

    def test_allows_the_masked_and_clean_inputs(self):
        for name in ("1320_1000022357_137.2s.mp4", "155_demo_asl-demo-translation_26.7s.mp4",
                     "1252_1000016397_76.8s.mp4"):
            with self.subTest(video=name):
                corpus_guard.assert_input_usable(name)  # must not raise

    def test_every_video_in_videos_dir_is_declared_leak_free(self):
        """manifest.json must agree that nothing in videos/ carries its own answer,
        except where a verified mask is declared."""
        manifest = json.loads((CORPUS_ROOT / "manifest.json").read_text(encoding="utf-8"))
        for entry in manifest["videos"]:
            with self.subTest(video=entry["file"]):
                if entry.get("label_in_input"):
                    mask = entry.get("input_mask") or {}
                    self.assertTrue(mask.get("masked_input"), "flagged video needs a masked input")
                    self.assertTrue(mask.get("verified"), "flagged video needs a recorded verification")



if __name__ == "__main__":
    unittest.main()
