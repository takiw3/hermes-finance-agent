#!/usr/bin/env python3
"""Regression tests for README policy and evidence-backed history checks."""
from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("repository_validator", ROOT / "scripts/validate.py")
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        git_env = patch.dict("os.environ", {"GIT_CEILING_DIRECTORIES": str(self.root.parent)})
        git_env.start()
        self.addCleanup(git_env.stop)
        self.root_patch = patch.object(validator, "R", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        validator.F.clear()
        self.addCleanup(validator.F.clear)

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args], check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def commit(self, message):
        self.git("add", "-A")
        self.git("-c", "user.name=Synthetic Reviewer", "-c",
                 "user.email=reviewer@example.invalid", "commit", "-m", message)

    def init_repo(self):
        self.git("init", "-b", "main")

    def identity_fixture(self):
        (self.root / "SOUL.md").write_text((ROOT / "SOUL.md").read_text())
        body = (ROOT / "README.md").read_text().replace(
            "TakiGPT AI Agentic Workforce", "Agentic Workforce")
        (self.root / "README.md").write_text(body)

    def run_history_main(self):
        stream = io.StringIO()
        with contextlib.ExitStack() as stack:
            # Isolate the history CLI contract from unrelated layout requirements.
            for name in (
                "check_layout", "check_manifest", "check_config", "check_identity_and_safety",
                "check_skills", "check_artifacts", "check_evals", "check_residue_and_data",
                "check_links_ci",
            ):
                stack.enter_context(patch.object(validator, name))
            stack.enter_context(patch("sys.argv", ["validate.py", "--history"]))
            stack.enter_context(contextlib.redirect_stdout(stream))
            stack.enter_context(contextlib.redirect_stderr(stream))
            status = validator.main()
        return status, stream.getvalue()

    def test_history_main_redacts_secret_bearing_paths_in_all_findings(self):
        self.init_repo()
        synthetic = "gh" + "p_" + "a" * 36
        (self.root / (synthetic + ".key")).write_text(synthetic)
        (self.root / (synthetic + ".bin")).write_bytes(bytes([255]))
        (self.root / (synthetic + ".nul")).write_bytes(bytes([0]))
        (self.root / (synthetic + ".link")).symlink_to("safe.txt")
        self.commit("Synthetic secret-path fixtures")
        status, output = self.run_history_main()
        self.assertEqual(status, 1)
        for kind in ("history-secret", "history-sensitive-path", "history-artifact"):
            self.assertTrue(any(kind in finding for finding in validator.F))
            self.assertIn(kind, output)
        self.assertNotIn(synthetic, output)
        self.assertNotIn(synthetic, str(validator.F))

    def test_readme_accepts_generic_agentic_workforce_positioning(self):
        self.identity_fixture()
        validator.check_identity_and_safety()
        self.assertEqual(validator.F, [])

    def test_readme_still_requires_workforce_positioning(self):
        self.identity_fixture()
        p = self.root / "README.md"
        p.write_text(p.read_text().replace("Agentic Workforce", "Specialist team"))
        validator.check_identity_and_safety()
        self.assertTrue(any("Agentic Workforce" in finding for finding in validator.F))

    def test_history_detects_removed_secret_without_printing_value(self):
        self.init_repo()
        synthetic = "gh" + "p_" + "a" * 36
        p = self.root / "removed.txt"
        p.write_text(synthetic)
        self.commit("Synthetic old fixture")
        p.unlink()
        (self.root / "safe.txt").write_text("No credential data here.")
        self.commit("Remove fixture")
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            validator.history()
        self.assertTrue(any("history-secret" in finding for finding in validator.F))
        self.assertNotIn(synthetic, stream.getvalue() + str(validator.F))

    def test_history_detects_committed_credential_filename(self):
        self.init_repo()
        (self.root / ".env").write_text("SYNTHETIC_SENTINEL\n")
        self.commit("Synthetic credential-file fixture")
        validator.history()
        self.assertTrue(any("history-sensitive-path" in finding for finding in validator.F))

    def test_history_checks_commit_messages(self):
        self.init_repo()
        (self.root / "safe.txt").write_text("Synthetic fixture")
        synthetic = "github_" + "pat_" + "b" * 50
        self.commit(synthetic)
        validator.history()
        self.assertTrue(any("history-secret" in finding for finding in validator.F))
        self.assertNotIn(synthetic, str(validator.F))

    def test_clean_history_reports_scanned_objects(self):
        self.init_repo()
        (self.root / "safe.txt").write_text("Synthetic fixture")
        self.commit("Safe fixture")
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            not_run = validator.history()
        self.assertEqual(not_run, 0)
        self.assertEqual(validator.F, [])
        self.assertIn("1 commit", stream.getvalue())
        self.assertIn("1 unique blob", stream.getvalue())

    def test_empty_history_is_not_run(self):
        self.init_repo()
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            not_run = validator.history()
        self.assertEqual(not_run, 1)
        self.assertIn("not_run", stream.getvalue())

    def test_history_main_fails_when_requested_history_is_empty(self):
        self.init_repo()
        status, output = self.run_history_main()
        self.assertEqual(status, 1)
        self.assertIn("history scan: not_run (repository has no commits)", output)
        self.assertIn("not_run: 1", output)
        self.assertNotIn("PASS: distribution validation", output)

    def test_history_main_fails_when_requested_history_is_unavailable(self):
        # A directory without .git cannot provide the explicitly requested history.
        status, output = self.run_history_main()
        self.assertEqual(status, 1)
        self.assertIn("history-error", output)
        self.assertIn("not_run: 1", output)
        self.assertNotIn("PASS: distribution validation", output)

    def test_unreadable_history_is_not_a_pass(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            not_run = validator.history()
        self.assertEqual(not_run, 1)
        self.assertTrue(any("history-error" in finding for finding in validator.F))
        self.assertNotIn("history scan: pass", stream.getvalue())

    def test_shallow_history_requires_full_fetch(self):
        self.init_repo()
        (self.root / "safe.txt").write_text("Synthetic fixture")
        self.commit("Safe fixture")
        with tempfile.TemporaryDirectory() as clone:
            subprocess.run(["git", "clone", "--depth", "1", self.root.as_uri(), clone],
                           check=True, capture_output=True)
            with patch.object(validator, "R", Path(clone)):
                not_run = validator.history()
        self.assertEqual(not_run, 1)
        self.assertTrue(any("history-incomplete" in finding for finding in validator.F))

    def test_binary_history_requires_review(self):
        self.init_repo()
        (self.root / "fixture.bin").write_bytes(bytes([0, 255, 127]))
        self.commit("Synthetic binary fixture")
        validator.history()
        self.assertTrue(any("history-artifact" in finding for finding in validator.F))


if __name__ == "__main__":
    unittest.main(verbosity=2)
