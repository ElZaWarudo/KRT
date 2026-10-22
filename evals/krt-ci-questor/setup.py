#!/usr/bin/env python3
"""CI-questor fixture: a tiny billing repo whose PR broke CI, canned gh runs,
and a suite-local gh wrapper on PATH (via the fixture's project settings env)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED_GH = HERE.parent / "bin" / "gh"
SHA = None


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


WORKFLOW = """name: CI
on:
  pull_request:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('requirements.txt') }}
      - name: Run tests
        run: python -m unittest discover -s tests -t . -f
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: report
          path: reports/
"""

STATUS_OLD = '''PENDING = "pending"
PAID = "paid"
CANCELLED = "cancelled"

ALL = (PENDING, PAID, CANCELLED)
'''

STATUS_NEW = '''PENDING = "pending"
PAID = "paid"
CANCELED = "canceled"

ALL = (PENDING, PAID, CANCELED)
'''

INVOICES_OLD = '''from src.billing import status


class Invoice:
    def __init__(self, number, total):
        self.number = number
        self.total = total
        self.status = status.PENDING

    def pay(self):
        self.status = status.PAID

    def cancel(self):
        self.status = status.CANCELLED
'''

REPORTS = '''from collections import Counter


def status_counts(invoices):
    counts = Counter(i.status for i in invoices)
    return {"pending": counts["pending"], "paid": counts["paid"], "cancelled": counts["cancelled"]}
'''

REPORTS_NEW = REPORTS.replace('"cancelled": counts["cancelled"]', '"canceled": counts["canceled"]')

TEST_STATUS = '''import unittest

from src.billing import status


class StatusTest(unittest.TestCase):
    def test_all_statuses(self):
        self.assertEqual(len(status.ALL), 3)
'''

TEST_INVOICES = '''import unittest

from src.billing.invoices import Invoice


class InvoiceTest(unittest.TestCase):
    def test_new_invoice_is_pending(self):
        self.assertEqual(Invoice(1, 10).status, "pending")

    def test_cancel_invoice(self):
        inv = Invoice(1, 10)
        inv.cancel()
        self.assertEqual(inv.status, "cancelled")
'''

TEST_REPORTS = '''import unittest

from src.billing.invoices import Invoice
from src.billing.reports import status_counts


class ReportsTest(unittest.TestCase):
    def test_counts_cancelled(self):
        a, b = Invoice(1, 10), Invoice(2, 20)
        b.cancel()
        self.assertEqual(status_counts([a, b])["cancelled"], 1)
'''


def ts(n: int) -> str:
    return f"2026-10-21T09:{14 + n // 60:02d}:{n % 60:02d}.{n:07d}Z"


def failed_log(sha: str) -> str:
    lines = [
        ("Run tests", "##[group]Run python -m unittest discover -s tests -t . -f"),
        ("Run tests", "python -m unittest discover -s tests -t . -f"),
        ("Run tests", "shell: /usr/bin/bash -e {0}"),
        ("Run tests", "##[endgroup]"),
        ("Run tests", "F"),
        ("Run tests", "======================================================================"),
        ("Run tests", "FAIL: test_cancel_invoice (tests.test_invoices.InvoiceTest.test_cancel_invoice)"),
        ("Run tests", "----------------------------------------------------------------------"),
        ("Run tests", "Traceback (most recent call last):"),
        ("Run tests", '  File "/home/runner/work/billing/billing/tests/test_invoices.py", line 13, in test_cancel_invoice'),
        ("Run tests", '    self.assertEqual(inv.status, "cancelled")'),
        ("Run tests", "AssertionError: 'canceled' != 'cancelled'"),
        ("Run tests", "- canceled"),
        ("Run tests", "+ cancelled"),
        ("Run tests", "?       +"),
        ("Run tests", ""),
        ("Run tests", "----------------------------------------------------------------------"),
        ("Run tests", "Ran 1 test in 0.001s"),
        ("Run tests", ""),
        ("Run tests", "FAILED (failures=1)"),
        ("Run tests", "##[error]Process completed with exit code 1."),
        ("Upload test report", "##[group]Run actions/upload-artifact@v4"),
        ("Upload test report", "##[endgroup]"),
        ("Upload test report", "##[warning]No files were found with the provided path: reports/. No artifacts will be uploaded."),
        ("Post Run actions/cache@v4", "Post job cleanup."),
        ("Post Run actions/cache@v4", "##[warning]Failed to save: Unable to reserve cache with key pip-3f1c, another job may be creating this cache."),
        ("Post Run actions/cache@v4", "##[error]Error: read ECONNRESET at TLSWrap.onStreamRead (node:internal/stream_base_commons:217:20)"),
    ]
    return "\n".join(f"test\t{step}\t{ts(i)} {text}" for i, (step, text) in enumerate(lines))


def run_record(sha: str, attempt: int, run_id: int = 9001) -> dict:
    return {
        "databaseId": run_id, "attempt": attempt, "workflowName": "CI", "displayTitle": "Use US spelling for canceled status",
        "headBranch": "fix/canceled-status", "headSha": sha, "event": "pull_request", "status": "completed",
        "conclusion": "failure", "createdAt": "2026-10-21T09:14:00Z", "url": f"https://github.com/acme/billing/actions/runs/{run_id}",
        "jobs": [{"databaseId": 5501, "name": "test", "conclusion": "failure", "steps": [
            {"name": "Set up job", "conclusion": "success"}, {"name": "Run actions/checkout@v4", "conclusion": "success"},
            {"name": "Run actions/setup-python@v5", "conclusion": "success"}, {"name": "Run actions/cache@v4", "conclusion": "success"},
            {"name": "Run tests", "conclusion": "failure"}, {"name": "Upload test report", "conclusion": "success"},
            {"name": "Post Run actions/cache@v4", "conclusion": "failure"}]}],
        "log_failed": failed_log(sha), "log": failed_log(sha),
    }


def setup(case: str, root: Path) -> None:
    origin, repo = root / "origin.git", root / "repo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(repo)], check=True, capture_output=True)
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    write(repo, "README.md", "# billing\n\nInvoices and reports. Run tests with `python -m unittest discover -s tests -t .`.\n")
    write(repo, ".github/workflows/ci.yml", WORKFLOW)
    write(repo, "requirements.txt", "")
    write(repo, ".gitignore", "__pycache__/\n*.pyc\n")
    write(repo, "src/__init__.py", "")
    write(repo, "src/billing/__init__.py", "")
    write(repo, "src/billing/status.py", STATUS_OLD)
    write(repo, "src/billing/invoices.py", INVOICES_OLD)
    write(repo, "src/billing/reports.py", REPORTS)
    write(repo, "tests/__init__.py", "")
    write(repo, "tests/test_status.py", TEST_STATUS)
    write(repo, "tests/test_invoices.py", TEST_INVOICES)
    write(repo, "tests/test_reports.py", TEST_REPORTS)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "feat: invoices and status reports")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "switch", "-qc", "fix/canceled-status")
    write(repo, "src/billing/status.py", STATUS_NEW)
    write(repo, "src/billing/invoices.py", INVOICES_OLD.replace("status.CANCELLED", "status.CANCELED"))
    write(repo, "src/billing/reports.py", REPORTS_NEW)
    git(repo, "commit", "-qam", "Use US spelling for canceled status")
    git(repo, "push", "-qu", "origin", "fix/canceled-status")
    sha = git(repo, "rev-parse", "HEAD")

    run = run_record(sha, attempt=2)
    run["previous_attempts"] = [{"attempt": 1, "createdAt": "2026-10-21T09:02:00Z"}]
    state = {
        "repo": "acme/billing", "default_branch": "main",
        "prs": [{
            "number": 17, "title": "Use US spelling for canceled status", "url": "https://github.com/acme/billing/pull/17",
            "state": "OPEN", "isDraft": False, "headRefName": "fix/canceled-status", "baseRefName": "main", "headRefOid": sha,
            "author": {"login": "eval-dev"}, "mergeable": "MERGEABLE", "mergeStateStatus": "BLOCKED", "reviewDecision": "REVIEW_REQUIRED",
            "reviews": [], "statusCheckRollup": [{"name": "test", "status": "COMPLETED", "conclusion": "FAILURE",
                                                  "detailsUrl": "https://github.com/acme/billing/actions/runs/9001/job/5501"}],
        }],
        "runs": [run],
    }
    (root / "gh-state.json").write_text(json.dumps(state, indent=2))

    # Suite-local gh on PATH: the runner only prepends evals/bin, so expose the
    # wrapper through the fixture's project settings env (loaded by --setting-sources project).
    bin_dir = root / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text(f'#!/bin/sh\nGH_SHARED_FAKE="{SHARED_GH}" exec "{sys.executable}" "{HERE / "gh_runs.py"}" "$@"\n')
    (bin_dir / "gh").chmod(0o755)
    (repo / ".claude").mkdir()
    path = f"{bin_dir}:{SHARED_GH.parent}:{os.environ['PATH']}"
    (repo / ".claude" / "settings.json").write_text(json.dumps({"env": {"PATH": path}}, indent=2))


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
