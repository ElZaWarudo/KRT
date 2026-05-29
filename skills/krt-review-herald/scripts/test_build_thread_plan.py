#!/usr/bin/env python3
"""Tests for review-thread plan generation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "build_thread_plan.py"
FIXTURES = ROOT / "fixtures"


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True, check=False)


class BuildThreadPlanTest(unittest.TestCase):
    def test_filters_resolved_threads_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_path = Path(tempdir)
            gh_path = temp_path / "fake-gh.py"
            log_path = temp_path / "gh-log.jsonl"
            self._write_fake_gh(gh_path, log_path)

            completed = run_command(
                "--repo",
                "acme/widgets",
                "--pr",
                "18",
                "--gh-bin",
                str(gh_path),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            plan = json.loads(completed.stdout)
            self.assertEqual(plan["repository"], "acme/widgets")
            self.assertEqual(plan["pull_request"], 18)
            self.assertEqual(plan["source"]["total_threads_seen"], 2)
            self.assertEqual(plan["source"]["threads_included"], 1)
            self.assertEqual(len(plan["threads"]), 1)
            self.assertEqual(plan["threads"][0]["thread_id"], "PRRT_open")
            self.assertEqual(plan["threads"][0]["reviewer"], "reviewer-a")
            self.assertEqual(plan["threads"][0]["classification"], "")
            self.assertEqual(len(log_path.read_text(encoding="utf-8").splitlines()), 2)

    def test_include_resolved_keeps_all_threads(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_path = Path(tempdir)
            gh_path = temp_path / "fake-gh.py"
            log_path = temp_path / "gh-log.jsonl"
            self._write_fake_gh(gh_path, log_path)

            completed = run_command(
                "--repo",
                "acme/widgets",
                "--pr",
                "18",
                "--include-resolved",
                "--gh-bin",
                str(gh_path),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            plan = json.loads(completed.stdout)
            self.assertEqual(len(plan["threads"]), 2)
            self.assertTrue(any(thread["is_resolved"] for thread in plan["threads"]))

    def test_invalid_repo_is_rejected(self) -> None:
        completed = run_command("--repo", "invalid", "--pr", "18")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("repo must be owner/repo", completed.stderr)

    @staticmethod
    def _write_fake_gh(gh_path: Path, log_path: Path) -> None:
        page_one = json.dumps(json.loads((FIXTURES / "threads_page_1.json").read_text(encoding="utf-8")))
        page_two = json.dumps(json.loads((FIXTURES / "threads_page_2.json").read_text(encoding="utf-8")))
        gh_path.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env python3
                import json
                import sys
                from pathlib import Path

                log_path = Path({str(log_path)!r})
                args = sys.argv[1:]
                previous = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
                log_path.write_text(previous + json.dumps(args) + "\\n", encoding="utf-8")
                joined = " ".join(args)
                if "after=cursor-1" in joined:
                    print({page_two!r})
                else:
                    print({page_one!r})
                """
            ),
            encoding="utf-8",
        )
        gh_path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
