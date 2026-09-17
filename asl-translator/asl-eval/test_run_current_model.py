#!/usr/bin/env python3
"""Tests for run_current_model.py.

No network calls. No Gemini/google.genai invocation. Where video-level
behavior is exercised, synthetic MotionRun lists are used instead of real
video files so these tests stay fast and hermetic.

Run:
    python3 -m unittest asl-translator/asl-eval/test_run_current_model.py -v
"""
from __future__ import annotations

import importlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_current_model as m  # noqa: E402


class TestDefaultIsDryRun(unittest.TestCase):
    def test_run_flag_defaults_false(self):
        ap = m.build_arg_parser()
        args = ap.parse_args(["--video", "x.mp4"])
        self.assertFalse(args.run)

    def test_main_without_run_never_touches_env_key(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            with mock.patch.object(m, "run_dry") as fake_dry, \
                 mock.patch.object(m, "run_real") as fake_real, \
                 mock.patch.dict("os.environ", {}, clear=True):
                fake_dry.return_value = m.DryRunReport(
                    video=f.name, duration_s=1.0, probe_frame_count=4,
                    active_run_count=1, idle_run_count=1, sampled_frame_count=2,
                    frame_budget=96, used_full_budget=False, expected_model_calls=1,
                    selected_timestamps=[0.1, 0.5],
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = m.main(["--video", f.name])
                self.assertEqual(rc, 0)
                fake_real.assert_not_called()
                self.assertIn("DRY RUN ONLY", buf.getvalue())


class TestDryRunNoApiKeyRequired(unittest.TestCase):
    def test_dry_run_works_with_no_gemini_api_key_env(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            with mock.patch.object(m, "run_dry") as fake_dry, \
                 mock.patch.dict("os.environ", {}, clear=True):
                fake_dry.return_value = m.DryRunReport(
                    video=f.name, duration_s=1.0, probe_frame_count=4,
                    active_run_count=1, idle_run_count=1, sampled_frame_count=2,
                    frame_budget=96, used_full_budget=False, expected_model_calls=1,
                    selected_timestamps=[0.1, 0.5],
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = m.main(["--video", f.name])
                self.assertEqual(rc, 0)

    def test_google_genai_not_imported_for_dry_run(self):
        # google.genai must not already be a loaded module as a side effect
        # of importing run_current_model or running dry-run.
        self.assertNotIn("google.genai", sys.modules)


class TestConfigTemperature(unittest.TestCase):
    def test_baseline0_temperature_unset(self):
        cfg = m.CONFIGS["baseline0"]
        self.assertIsNone(cfg["temperature"])
        self.assertEqual(cfg["temperature_label"], "temperature_unset_provider_default")

    def test_temperature0_sets_zero(self):
        cfg = m.CONFIGS["temperature0"]
        self.assertEqual(cfg["temperature"], 0.0)
        self.assertEqual(cfg["temperature_label"], "0.0")

    def test_baseline0_omits_temperature_kwarg_shape(self):
        # Mirrors the kwarg-building logic in run_real without calling it.
        cfg = m.CONFIGS["baseline0"]
        kwargs = {"response_mime_type": "application/json"}
        if cfg["temperature"] is not None:
            kwargs["temperature"] = cfg["temperature"]
        self.assertNotIn("temperature", kwargs)

    def test_temperature0_includes_temperature_kwarg_shape(self):
        cfg = m.CONFIGS["temperature0"]
        kwargs = {"response_mime_type": "application/json"}
        if cfg["temperature"] is not None:
            kwargs["temperature"] = cfg["temperature"]
        self.assertEqual(kwargs.get("temperature"), 0.0)


class TestBatchCount(unittest.TestCase):
    def test_batch_counts(self):
        cases = {0: 0, 1: 1, 24: 1, 25: 2, 96: 4, 97: 5, 48: 2}
        for n, expected in cases.items():
            with self.subTest(n=n):
                self.assertEqual(m.expected_batch_count(n), expected)


class TestOutputSchema(unittest.TestCase):
    def test_dry_run_json_shape(self):
        report = m.DryRunReport(
            video="videos/155_demo_asl-demo-translation_26.7s.mp4",
            duration_s=26.7, probe_frame_count=100, active_run_count=3,
            idle_run_count=2, sampled_frame_count=40, frame_budget=96,
            used_full_budget=False, expected_model_calls=2,
            selected_timestamps=[0.1, 1.2],
        )
        out = m.dry_run_report_to_json(report, "baseline0", "videos/155.mp4")
        self.assertIsNone(out["project_id"])
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["segments"], [])
        rm = out["run_metadata"]
        self.assertEqual(rm["model"], "gemini-2.5-flash")
        self.assertEqual(rm["temperature"], "temperature_unset_provider_default")
        self.assertEqual(rm["frame_budget"], 96)
        self.assertEqual(rm["keyframe_width"], 512)
        self.assertEqual(rm["batch_size"], 24)
        self.assertEqual(rm["model_calls"], 0)
        self.assertFalse(rm["production_side_effects"])
        self.assertIn("prompt_sha256", rm)
        # Must round-trip through json.dumps without error.
        json.dumps(out)


class TestRunGates(unittest.TestCase):
    def test_run_without_ack_refuses(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            with mock.patch.object(m, "run_real") as fake_real:
                buf_out, buf_err = io.StringIO(), io.StringIO()
                with redirect_stdout(buf_out), redirect_stderr(buf_err):
                    rc = m.main(["--video", f.name, "--run", "--output", "/tmp/out.json"])
                self.assertEqual(rc, 2)
                fake_real.assert_not_called()
                self.assertIn("--acknowledge-private-data-upload", buf_err.getvalue())

    def test_ack_without_run_makes_no_call(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            with mock.patch.object(m, "run_dry") as fake_dry, \
                 mock.patch.object(m, "run_real") as fake_real:
                fake_dry.return_value = m.DryRunReport(
                    video=f.name, duration_s=1.0, probe_frame_count=4,
                    active_run_count=1, idle_run_count=1, sampled_frame_count=2,
                    frame_budget=96, used_full_budget=False, expected_model_calls=1,
                    selected_timestamps=[0.1, 0.5],
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = m.main(["--video", f.name, "--acknowledge-private-data-upload"])
                self.assertEqual(rc, 0)
                fake_real.assert_not_called()
                self.assertIn("DRY RUN ONLY", buf.getvalue())

    def test_run_with_both_flags_but_no_api_key_fails_clearly(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            with mock.patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(SystemExit) as ctx:
                    m.run_real(Path(f.name), "baseline0", 96, Path("/tmp/should_not_be_written.json"))
                self.assertIn("GEMINI_API_KEY", str(ctx.exception))

    def test_run_requires_output(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            with self.assertRaises(SystemExit):
                m.main(["--video", f.name, "--run", "--acknowledge-private-data-upload"])


class TestUrlBlocking(unittest.TestCase):
    def test_rejects_http_url(self):
        with self.assertRaises(ValueError):
            m.validate_local_video_path("https://example.com/video.mp4")

    def test_rejects_azure_and_s3_like_urls(self):
        for url in ["https://foo.blob.core.windows.net/x.mp4", "s3://bucket/key.mp4",
                    "gs://bucket/key.mp4", "ftp://host/x.mp4"]:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    m.validate_local_video_path(url)

    def test_accepts_existing_local_file(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            path = m.validate_local_video_path(f.name)
            self.assertEqual(str(path), f.name)

    def test_rejects_missing_local_file(self):
        with self.assertRaises(FileNotFoundError):
            m.validate_local_video_path("/nonexistent/path/video.mp4")


class TestNoProductionSideEffectImports(unittest.TestCase):
    """Checks actual `import`/`from ... import` statements only — the source
    file's docstrings and comments legitimately *mention* Supabase/Azure/etc.
    to document what it deliberately does NOT touch, so a raw substring scan
    over the whole file would false-positive on that prose."""

    FORBIDDEN_MODULE_PREFIXES = (
        "app.crud", "app.pipelines", "app.orchestrators", "app.config",
        "app.services", "sqlalchemy", "supabase", "azure",
    )
    IMPORT_RE = __import__("re").compile(
        r"^\s*(?:from\s+(\S+)\s+import\s+\S+|import\s+(\S+))", __import__("re").MULTILINE
    )

    def test_source_has_no_forbidden_imports(self):
        src = Path(m.__file__).read_text(encoding="utf-8")
        imported_modules = []
        for from_mod, import_mod in self.IMPORT_RE.findall(src):
            imported_modules.append(from_mod or import_mod)
        for mod in imported_modules:
            for bad in self.FORBIDDEN_MODULE_PREFIXES:
                with self.subTest(mod=mod, forbidden=bad):
                    self.assertFalse(
                        mod == bad or mod.startswith(bad + "."),
                        f"forbidden import found: {mod}",
                    )

    def test_no_credit_or_db_write_function_names_defined(self):
        src = Path(m.__file__).read_text(encoding="utf-8")
        for name in ("charge_user_if_needed", "write_projectsegment",
                     "create_project", "update_project"):
            with self.subTest(name=name):
                self.assertNotIn(f"def {name}", src)

    def test_module_import_did_not_pull_in_sqlalchemy_or_supabase(self):
        for bad in ("sqlalchemy", "supabase"):
            self.assertNotIn(bad, sys.modules)


class TestSegmentationLogicMatchesProduction(unittest.TestCase):
    """Sanity-check the ported pure functions against known small inputs."""

    def test_allocate_timestamps_no_active_runs_falls_back_uniform(self):
        runs = [m.MotionRun(0.0, 10.0, 1.0, False)]
        stamps = m.allocate_timestamps(runs, budget=96)
        self.assertEqual(len(stamps), 12)
        self.assertAlmostEqual(stamps[0], 0.0)
        self.assertAlmostEqual(stamps[-1], 10.0)

    def test_allocate_timestamps_single_active_run_uses_full_budget_share(self):
        runs = [m.MotionRun(0.0, 10.0, 100.0, True)]
        stamps = m.allocate_timestamps(runs, budget=24)
        self.assertEqual(len(stamps), 24)
        self.assertTrue(all(0.0 <= s <= 10.0 for s in stamps))

    def test_allocate_timestamps_respects_budget_ceiling(self):
        runs = [m.MotionRun(0.0, 5.0, 50.0, True), m.MotionRun(5.0, 10.0, 50.0, True)]
        stamps = m.allocate_timestamps(runs, budget=10)
        self.assertLessEqual(len(stamps), 10)


class TestPromptProvenance(unittest.TestCase):
    def test_prompt_hash_is_stable(self):
        h1 = m.prompt_sha256()
        h2 = m.prompt_sha256()
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)


if __name__ == "__main__":
    unittest.main()


# ─────────────────────────────────────────────────────────────────────────
# 2026-08-29 mirror: duration-scaled budget, dedup, degeneracy signal.
# Fixtures are real values from data/asl_corpus/, not invented ones.
# ─────────────────────────────────────────────────────────────────────────
class TestBudgetForDuration(unittest.TestCase):
    def test_short_clips_get_the_floor(self):
        self.assertEqual(m.budget_for_duration(6.7), m.MIN_FRAME_BUDGET)

    def test_mid_length_hits_the_target_density(self):
        for duration in (26.7, 76.8):
            self.assertAlmostEqual(
                m.budget_for_duration(duration) / duration,
                m.TARGET_FRAMES_PER_SEC, delta=0.05)

    def test_long_clips_are_capped(self):
        self.assertEqual(m.budget_for_duration(300.0), m.MAX_FRAME_BUDGET)

    def test_190s_job_clears_the_density_floor(self):
        # 0.51 f/s under the old absolute budget; the read collapsed into "Many".
        self.assertGreater(m.budget_for_duration(189.5) / 189.5, m.DENSITY_FLOOR_FPS)

    def test_300s_job_still_does_not_clear_the_floor(self):
        # The cap binds, so this stays flagged rather than silently shipped.
        self.assertLess(m.budget_for_duration(300.0) / 300.0, m.DENSITY_FLOOR_FPS)

    def test_1320_crosses_the_floor(self):
        # The corpus's best unlabelled video: 0.70 f/s before, above the floor now.
        self.assertLess(m.FRAME_BUDGET / 137.2, m.DENSITY_FLOOR_FPS)
        self.assertGreater(m.budget_for_duration(137.2) / 137.2, m.DENSITY_FLOOR_FPS)


class TestResolveFrameBudget(unittest.TestCase):
    def test_historical_configs_keep_the_absolute_budget(self):
        for name in ("baseline0", "temperature0"):
            self.assertEqual(m.resolve_frame_budget(name, 300.0), m.FRAME_BUDGET)

    def test_current_config_scales_with_duration(self):
        self.assertEqual(m.resolve_frame_budget("production_2026_08_29", 26.7),
                         m.budget_for_duration(26.7))

    def test_explicit_override_wins_everywhere(self):
        for name in sorted(m.CONFIGS):
            self.assertEqual(m.resolve_frame_budget(name, 300.0, override=7), 7)


class TestExperimentB8fpsAblation(unittest.TestCase):
    """2026-09-06 temporal-sampling ablation: Experiment B must scale the frame
    budget at 8.0 f/s while leaving baseline A / production at 2.0 f/s."""

    def test_module_default_target_fps_is_unchanged(self):
        self.assertEqual(m.TARGET_FRAMES_PER_SEC, 2.0)

    def test_8fps_config_declares_its_own_target(self):
        cfg = m.CONFIGS["evaluation_2026_09_06_gemini_3_6_8fps"]
        self.assertEqual(cfg["target_frames_per_sec"], 8.0)
        self.assertEqual(cfg["budget_mode"], "duration_scaled")

    def test_baseline_and_production_configs_have_no_override(self):
        for name in ("production_2026_08_29", "evaluation_2026_09_04_gemini_3_6"):
            self.assertNotIn("target_frames_per_sec", m.CONFIGS[name])

    def test_resolve_target_fps(self):
        self.assertEqual(m.resolve_target_fps("evaluation_2026_09_04_gemini_3_6"), 2.0)
        self.assertEqual(m.resolve_target_fps("production_2026_08_29"), 2.0)
        self.assertEqual(m.resolve_target_fps("evaluation_2026_09_06_gemini_3_6_8fps"), 8.0)

    def test_8fps_config_quadruples_the_duration_scaled_budget_before_clamping(self):
        # Mid-length clip, both densities land strictly inside [MIN_FRAME_BUDGET, MAX_FRAME_BUDGET]
        # so the 4x relationship isn't hidden by clamping.
        duration = 20.0
        baseline_budget = m.resolve_frame_budget("evaluation_2026_09_04_gemini_3_6", duration)
        ablation_budget = m.resolve_frame_budget("evaluation_2026_09_06_gemini_3_6_8fps", duration)
        self.assertEqual(baseline_budget, 40)
        self.assertEqual(ablation_budget, 160)
        self.assertEqual(ablation_budget, baseline_budget * 4)

    def test_8fps_config_still_respects_the_absolute_clamps(self):
        self.assertEqual(
            m.resolve_frame_budget("evaluation_2026_09_06_gemini_3_6_8fps", 1.0),
            m.MIN_FRAME_BUDGET,
        )
        self.assertEqual(
            m.resolve_frame_budget("evaluation_2026_09_06_gemini_3_6_8fps", 300.0),
            m.MAX_FRAME_BUDGET,
        )

    def test_explicit_override_still_wins_over_the_ablation_target(self):
        self.assertEqual(
            m.resolve_frame_budget("evaluation_2026_09_06_gemini_3_6_8fps", 300.0, override=5),
            5,
        )


class TestConfigs(unittest.TestCase):
    def test_historical_configs_are_unchanged(self):
        """These reproduce every saved prediction; changing them invalidates them."""
        self.assertIsNone(m.CONFIGS["baseline0"]["temperature"])
        self.assertEqual(m.CONFIGS["baseline0"]["budget_mode"], "absolute")
        self.assertFalse(m.CONFIGS["baseline0"]["dedup"])
        self.assertEqual(m.CONFIGS["temperature0"]["temperature"], 0.0)
        self.assertEqual(m.CONFIGS["temperature0"]["budget_mode"], "absolute")
        self.assertFalse(m.CONFIGS["temperature0"]["dedup"])

    def test_current_config_matches_what_production_ships(self):
        cfg = m.CONFIGS["production_2026_08_29"]
        self.assertEqual(cfg["temperature"], 0.0)
        self.assertEqual(cfg["budget_mode"], "duration_scaled")
        self.assertTrue(cfg["dedup"])

    def test_every_config_declares_the_full_knob_set(self):
        for name, cfg in m.CONFIGS.items():
            for key in ("model", "temperature", "temperature_label", "budget_mode", "dedup"):
                self.assertIn(key, cfg, f"{name} is missing {key}")


class TestMergeAdjacentDuplicates(unittest.TestCase):
    def _seg(self, i, start, end, text):
        return {"line": i, "start": start, "end": end, "text": text}

    def test_merges_the_155_batch_boundary_repeats(self):
        segs = [
            self._seg(1, 8.88, 9.94, "My mother is twenty-nine."),
            self._seg(2, 10.31, 12.65, "My mother is twenty-nine."),
            self._seg(3, 18.48, 18.80, "My brother is seven."),
            self._seg(4, 19.12, 20.42, "My brother is seven."),
        ]
        out = m.merge_adjacent_duplicates(segs)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["start"], 8.88)
        self.assertEqual(out[0]["end"], 12.65)  # union span
        self.assertEqual([s["line"] for s in out], [1, 2])  # renumbered

    def test_does_not_merge_the_degenerate_long_video_repeats(self):
        segs = [
            self._seg(1, 1.10, 14.30, "Many"),
            self._seg(2, 25.49, 30.10, "Many"),   # gap 11.19s
            self._seg(3, 35.10, 40.00, "Many"),   # gap  5.00s
        ]
        self.assertEqual(len(m.merge_adjacent_duplicates(segs)), 3)

    def test_matching_ignores_case_and_punctuation(self):
        segs = [self._seg(1, 0.0, 1.0, "My mother is twenty-nine."),
                self._seg(2, 1.2, 2.0, "my mother is twenty nine")]
        self.assertEqual(len(m.merge_adjacent_duplicates(segs)), 1)

    def test_identical_text_split_by_another_caption_is_untouched(self):
        segs = [self._seg(1, 0.0, 1.0, "Yes."), self._seg(2, 1.1, 2.0, "No."),
                self._seg(3, 2.1, 3.0, "Yes.")]
        self.assertEqual(len(m.merge_adjacent_duplicates(segs)), 3)

    def test_blank_captions_never_merge(self):
        segs = [self._seg(1, 0.0, 1.0, "   "), self._seg(2, 1.1, 2.0, "  ")]
        self.assertEqual(len(m.merge_adjacent_duplicates(segs)), 2)

    def test_does_not_mutate_the_input(self):
        segs = [self._seg(1, 0.0, 1.0, "Hi"), self._seg(2, 1.2, 2.0, "Hi")]
        m.merge_adjacent_duplicates(segs)
        self.assertEqual(segs[0]["end"], 1.0)

    def test_empty(self):
        self.assertEqual(m.merge_adjacent_duplicates([]), [])


class TestDegenerateRepetition(unittest.TestCase):
    def _segs(self, texts):
        return [{"line": i + 1, "start": i * 10.0, "end": i * 10.0 + 1.0, "text": t}
                for i, t in enumerate(texts)]

    def test_fires_on_a_collapsed_read(self):
        self.assertTrue(m.has_degenerate_repetition(self._segs(["Many"] * 4)))

    def test_threshold_is_the_documented_count(self):
        n = m.DEGENERATE_REPEAT_COUNT
        self.assertFalse(m.has_degenerate_repetition(self._segs(["Not"] * (n - 1))))
        self.assertTrue(m.has_degenerate_repetition(self._segs(["Not"] * n)))

    def test_does_not_fire_on_fluent_fabrication(self):
        """Documents the blind spot: job 1442 is 15 distinct fluent sentences."""
        self.assertFalse(m.has_degenerate_repetition(
            self._segs([f"Distinct sentence number {i}." for i in range(15)])))

    def test_empty(self):
        self.assertFalse(m.has_degenerate_repetition([]))


class TestAllocateTimestampsGuard(unittest.TestCase):
    def test_budget_of_one_does_not_divide_by_zero(self):
        runs = [m.MotionRun(0.0, 5.0, 100.0, True), m.MotionRun(6.0, 12.0, 120.0, True)]
        self.assertEqual(len(m.allocate_timestamps(runs, 1)), 1)


class TestProductionParity(unittest.TestCase):
    """Load curify-studio's asl_utils.py directly and diff it against this mirror.

    This is the drift detector. Everything in this file is a hand-copied port, so
    the only thing that actually keeps it honest is comparing it to the source.
    Skipped when curify-studio is not checked out next door — CI without it still
    runs every other test.

    asl_utils keeps every heavy import (numpy, google.genai, imagen_service)
    function-local, so it loads with no environment and no provider config. That
    is what makes this possible; app.config would not.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util
        candidates = [
            Path.home() / "curify-studio" / "curify_background" / "app" / "utils" / "asl_utils.py",
            Path(__file__).resolve().parents[3] / "curify-studio" / "curify_background"
            / "app" / "utils" / "asl_utils.py",
        ]
        src = next((p for p in candidates if p.exists()), None)
        if src is None:
            raise unittest.SkipTest("curify-studio not available; parity check skipped")
        spec = importlib.util.spec_from_file_location("_prod_asl_utils", src)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_prod_asl_utils"] = mod  # dataclasses needs it registered
        spec.loader.exec_module(mod)
        cls.prod = mod

    def test_constants_match_production(self):
        for name in ("PROBE_FPS", "PROBE_WIDTH", "KEYFRAME_WIDTH", "MIN_FRAMES_PER_RUN",
                     "BATCH_SIZE", "IDLE_QUANTILE", "ABS_MOTION_FLOOR",
                     "TARGET_FRAMES_PER_SEC", "MIN_FRAME_BUDGET", "MAX_FRAME_BUDGET",
                     "DENSITY_FLOOR_FPS", "ASL_TEMPERATURE", "DEDUP_MAX_GAP_S",
                     "DEGENERATE_REPEAT_COUNT"):
            self.assertEqual(getattr(m, name), getattr(self.prod, name),
                             f"{name} has drifted from production")

    def test_model_matches_production(self):
        self.assertEqual(m.ASL_MODEL, self.prod.ASL_MODEL)

    def test_prompt_matches_production(self):
        self.assertEqual(m.PRODUCTION_PROMPT, self.prod._PROMPT)

    def test_budget_curve_matches_production(self):
        for duration in (3.0, 6.7, 11.5, 26.7, 76.8, 137.2, 189.5, 300.0, 3600.0):
            self.assertEqual(m.budget_for_duration(duration),
                             self.prod._budget_for_duration(duration),
                             f"budget diverges at {duration}s")

    def test_normalization_matches_production(self):
        for text in ("My mother is twenty-nine.", "I don't know", "  Many  ",
                     "H.G.Q.", "", "   "):
            self.assertEqual(m.normalize_for_dedup(text),
                             self.prod._normalize_for_dedup(text))

    def test_dedup_matches_production(self):
        fixtures = [
            [(8.88, 9.94, "My mother is twenty-nine."), (10.31, 12.65, "My mother is twenty-nine.")],
            [(1.10, 14.30, "Many"), (25.49, 30.10, "Many"), (35.10, 40.00, "Many")],
            [(0.0, 1.0, "Yes."), (1.1, 2.0, "No."), (2.1, 3.0, "Yes.")],
        ]
        for fixture in fixtures:
            mine = m.merge_adjacent_duplicates(
                [{"line": i + 1, "start": s, "end": e, "text": t}
                 for i, (s, e, t) in enumerate(fixture)])
            theirs = self.prod._merge_adjacent_duplicates(
                [self.prod.AslSegment(s, e, t) for s, e, t in fixture])
            self.assertEqual([(x["start"], x["end"], x["text"]) for x in mine],
                             [(x.start, x.end, x.text) for x in theirs])
