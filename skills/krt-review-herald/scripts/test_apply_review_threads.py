#!/usr/bin/env python3
"""Fixture tests for review thread automation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
SCRIPT = ROOT / "apply_review_threads.py"


def run_json(*args: str) -> tuple[int, dict]:
    completed = subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True, check=False)
    return completed.returncode, json.loads(completed.stdout)


class ReviewThreadScriptTest(unittest.TestCase):
    def test_valid_plan_dry_run(self) -> None:
        code, result = run_json("--plan-file", str(FIXTURES / "valid_plan.json"))
        self.assertEqual(code, 0, result)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["summary"]["reply_count"], 2)
        self.assertEqual(result["summary"]["resolve_count"], 1)
        self.assertEqual(result["operations"][0]["status"], "planned")

    def test_resolve_requires_verification_or_reason(self) -> None:
        code, result = run_json("--plan-file", str(FIXTURES / "invalid_missing_reason.json"))
        self.assertNotEqual(code, 0)
        self.assertIn("thread[1]:resolve-requires-verification-or-reason", result["errors"])

    def test_clarify_cannot_resolve(self) -> None:
        code, result = run_json("--plan-file", str(FIXTURES / "invalid_clarify_resolve.json"))
        self.assertNotEqual(code, 0)
        self.assertIn("thread[1]:resolve-forbidden-for-decision:clarify", result["errors"])

    def test_execute_uses_gh_for_reply_and_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_path = Path(tempdir)
            log_path = temp_path / "gh-log.jsonl"
            gh_path = temp_path / "fake-gh.py"
            gh_path.write_text(
                textwrap.dedent(
                    f"""\
                    #!/usr/bin/env python3
                    import json
                    import sys
                    from pathlib import Path

                    args = sys.argv[1:]
                    Path({str(log_path)!r}).write_text(
                        Path({str(log_path)!r}).read_text(encoding="utf-8") + json.dumps(args) + "\\n",
                        encoding="utf-8",
                    ) if Path({str(log_path)!r}).exists() else Path({str(log_path)!r}).write_text(json.dumps(args) + "\\n", encoding="utf-8")
                    print(json.dumps({{"data": {{"ok": True}}}}))
                    """
                ),
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            code, result = run_json(
                "--plan-file",
                str(FIXTURES / "execute_plan.json"),
                "--execute",
                "--gh-bin",
                str(gh_path),
            )

            self.assertEqual(code, 0, result)
            self.assertTrue(result["allowed"])
            log_lines = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(log_lines), 2)
            self.assertEqual(log_lines[0][:2], ["api", "graphql"])
            self.assertIn("threadId=PRRT_kwDOAAABc123", log_lines[0])
            self.assertIn("threadId=PRRT_kwDOAAABc123", log_lines[1])


if __name__ == "__main__":
    unittest.main()
