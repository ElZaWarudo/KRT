#!/usr/bin/env python3
"""Build one review-herald eval fixture: repo/, origin.git/, gh-state.json.

PR #18 (feat/order-export -> develop) has five unresolved review threads,
served by the fake gh for any `gh api graphql` call and as REST comments.

The fake gh labels `gh api graphql` and `gh api ... -f body=` calls as reads,
so the suite detects thread replies/resolutions by matching the raw call log
(../gh-log.jsonl relative to the repo) instead of relying on no_gh_mutation.
A commit-msg hook appends commit messages to .git/commit-msgs.log, and
bytecode is git-excluded so judge_files never sees binary content.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = """#!/bin/sh
cat "$1" >> "$(git rev-parse --git-dir)/commit-msgs.log"
echo "----" >> "$(git rev-parse --git-dir)/commit-msgs.log"
"""

EXPORT = '''import csv
import io


def orders_to_csv(orders, include_cancelled=False):
    rows = [o for o in orders if include_cancelled or o.status != "cancelled"]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "total", "status"])
    for o in orders:
        w.writerow([o.id, o.total, o.status])
    return buf.getvalue()
'''

API = '''from .export import orders_to_csv
from .service import list_orders


def get_orders(request, repo):
    return [{"id": o.id, "total": o.total, "status": o.status} for o in list_orders(repo)]


def export_orders(request, repo):
    return orders_to_csv(list_orders(repo))
'''

# (thread id, reviewer, path, line, body)
THREADS = [
    ("PRRT_loop", "maria-dev", "src/orders/export.py", 10,
     "This loops over `orders` instead of the filtered `rows`, so cancelled orders still end up in the export."),
    ("PRRT_none", "li-wei", "src/orders/api.py", 10,
     "`list_orders(repo)` returns None when the repo is empty, so this will crash. Please add a None check here."),
    ("PRRT_rename", "maria-dev", "src/orders/api.py", 6,
     "Can we rename `total` to `amount`, both in the CSV header and in the GET /orders JSON? The new frontend calls it amount."),
    ("PRRT_nit", "li-wei", "src/orders/export.py", 8,
     "nit: `w` -> `writer`"),
    ("PRRT_stream", "maria-dev", "src/orders/export.py", 7,
     "Should this stream instead of building the whole CSV in memory?"),
]


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def build_repo(root: Path) -> Path:
    origin, repo = root / "origin.git", root / "repo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(repo)], check=True, capture_output=True)
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    write(repo, "README.md", "# orders\n\nOrder management service.\n")
    write(repo, "src/orders/models.py", "class Order:\n    def __init__(self, id, total, status=\"open\"):\n        self.id = id\n        self.total = total\n        self.status = status\n")
    write(repo, "src/orders/service.py", "def list_orders(repo):\n    return repo.all() or []\n")
    write(repo, "src/orders/api.py", "from .service import list_orders\n\n\ndef get_orders(request, repo):\n    return [{\"id\": o.id, \"total\": o.total, \"status\": o.status} for o in list_orders(repo)]\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "chore: initial service")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "switch", "-qc", "develop")
    git(repo, "push", "-q", "origin", "develop")
    git(repo, "switch", "-qc", "feat/order-export")
    write(repo, "src/orders/export.py", EXPORT)
    write(repo, "src/orders/api.py", API)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "feat(orders): add CSV export")
    git(repo, "push", "-qu", "origin", "feat/order-export")
    hook = repo / ".git" / "hooks" / "commit-msg"
    hook.write_text(HOOK)
    hook.chmod(0o755)
    (repo / ".git" / "commit-msgs.log").write_text("# commit messages\n")
    # Keep bytecode out of the judged work product (null bytes break the judge call).
    with open(repo / ".git" / "info" / "exclude", "a") as exclude:
        exclude.write("__pycache__/\n*.pyc\n")
    return repo


def graphql_threads() -> dict:
    nodes = []
    for i, (tid, who, path, line, body) in enumerate(THREADS, 1):
        nodes.append({
            "id": tid, "isResolved": False, "isOutdated": False, "path": path, "line": line,
            "originalLine": line, "startLine": None, "originalStartLine": None, "diffSide": "RIGHT",
            "comments": {"totalCount": 1, "nodes": [{
                "id": f"PRRC_{i}", "databaseId": 1000 + i, "body": body, "createdAt": "2026-10-20T10:00:00Z",
                "url": f"https://github.com/acme/orders/pull/18#discussion_r{1000 + i}", "author": {"login": who},
            }]},
        })
    return {"data": {"repository": {"pullRequest": {
        "id": "PR_kwDOorders18", "number": 18, "title": "feat: add order CSV export",
        "url": "https://github.com/acme/orders/pull/18",
        "reviewThreads": {"nodes": nodes, "pageInfo": {"hasNextPage": False, "endCursor": None}},
    }}}}


def rest_comments() -> list:
    return [{
        "id": 1000 + i, "node_id": f"PRRC_{i}", "path": path, "line": line, "body": body,
        "user": {"login": who}, "html_url": f"https://github.com/acme/orders/pull/18#discussion_r{1000 + i}",
        "in_reply_to_id": None,
    } for i, (tid, who, path, line, body) in enumerate(THREADS, 1)]


def state() -> dict:
    reviews = [
        {"author": {"login": "maria-dev"}, "state": "CHANGES_REQUESTED", "body": "A couple of things before this can go in."},
        {"author": {"login": "li-wei"}, "state": "COMMENTED", "body": ""},
    ]
    pr = {
        "number": 18, "title": "feat: add order CSV export", "url": "https://github.com/acme/orders/pull/18",
        "state": "OPEN", "isDraft": False, "headRefName": "feat/order-export", "baseRefName": "develop",
        "author": {"login": "eval-dev"}, "mergeable": "MERGEABLE", "mergeStateStatus": "BLOCKED",
        "reviewDecision": "CHANGES_REQUESTED", "reviews": reviews, "comments": [],
        "body": "- Add CSV export for orders, skipping cancelled orders by default\n",
        "files": [{"path": "src/orders/api.py"}, {"path": "src/orders/export.py"}],
        "statusCheckRollup": [{"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}],
    }
    rest_reviews = [{"id": 1, "user": {"login": r["author"]["login"]}, "state": r["state"], "body": r["body"]} for r in reviews]
    return {
        "repo": "acme/orders", "default_branch": "main", "prs": [pr],
        "api": {
            "graphql": graphql_threads(),
            "pulls/18/comments": rest_comments(),
            "pulls/18/reviews": rest_reviews,
            "issues/18/comments": [],
        },
    }


def setup(case: str, root: Path) -> None:
    if case not in {"address-comments", "resolve-all", "fix-and-commit"}:
        raise SystemExit(f"unknown case {case}")
    build_repo(root)
    (root / "gh-state.json").write_text(json.dumps(state(), indent=2))


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
