#!/usr/bin/env python3
"""Tests for run_current_model.py.

No network calls. No Gemini/google.genai invocation. Where video-level
behavior is exercised, synthetic MotionRun lists are used instead of real
video files so these tests stay fast and hermetic.

Run:
    python3 -m unittest tools/asl-eval/test_run_current_model.py -v
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
