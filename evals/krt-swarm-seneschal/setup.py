#!/usr/bin/env python3
"""Build one swarm-seneschal eval fixture: two independent bugs plus a unit list."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


TEST_HEADER = "import sys, unittest\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).resolve().parents[1] / \"src\"))\n"

FILES = {
    ".gitignore": "__pycache__/\n*.pyc\n",
    "README.md": "# toolkit\n\nUtilities you will recieve as a library. Run tests with `python3 -m unittest discover -s tests`.\n\nPRs target `develop`.\n",
    "src/toolkit/__init__.py": "",
    "src/toolkit/textutil.py": (
        "import re\n\n\n"
        "def slugify(text):\n"
        "    text = text.lower().strip()\n"
        "    text = re.sub(r\"[^a-z]+\", \"-\", text)\n"
        "    return text.strip(\"-\")\n"
    ),
    "src/toolkit/mathutil.py": (
        "def median(values):\n"
        "    ordered = sorted(values)\n"
        "    return ordered[len(ordered) // 2]\n"
    ),
    "tests/__init__.py": "",
    "tests/test_textutil.py": TEST_HEADER + (
        "from toolkit.textutil import slugify\n\n\n"
        "class SlugifyTest(unittest.TestCase):\n"
        "    def test_words(self):\n        self.assertEqual(slugify(\"Hello World\"), \"hello-world\")\n\n"
        "    def test_keeps_digits(self):\n        self.assertEqual(slugify(\"Top 10 Tips\"), \"top-10-tips\")\n"
    ),
    "tests/test_mathutil.py": TEST_HEADER + (
        "from toolkit.mathutil import median\n\n\n"
        "class MedianTest(unittest.TestCase):\n"
        "    def test_odd(self):\n        self.assertEqual(median([3, 1, 2]), 2)\n\n"
        "    def test_even(self):\n        self.assertEqual(median([4, 1, 3, 2]), 2.5)\n"
    ),
    "docs/units.md": (
        "# Ready units for this sprint\n\nAll scope and acceptance criteria are approved.\n\n"
        "- U1 Password reset by email. Owns `src/toolkit/auth/reset.py`, `src/toolkit/models/user.py` "
        "(adds `reset_token`), new migration `migrations/0003_reset_token.py`. Check: `tests/test_reset.py`.\n"
        "- U2 Login rate limiting. Owns `src/toolkit/auth/ratelimit.py`, new migration "
        "`migrations/0004_login_attempts.py`. Check: `tests/test_ratelimit.py`.\n"
        "- U3 Fix slugify dropping digits. Owns `src/toolkit/textutil.py`. Check: `tests/test_textutil.py`.\n"
        "- U4 Fix median for even-length lists. Owns `src/toolkit/mathutil.py`. Check: `tests/test_mathutil.py`.\n"
    ),
}


def setup(case: str, root: Path) -> None:
    origin, repo = root / "origin.git", root / "repo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(repo)], check=True, capture_output=True)
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    for rel, text in FILES.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "chore: initial toolkit")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "switch", "-qc", "develop")
    git(repo, "push", "-q", "origin", "develop")
    (root / "gh-state.json").write_text(json.dumps({"repo": "acme/toolkit", "default_branch": "main", "prs": []}))


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
