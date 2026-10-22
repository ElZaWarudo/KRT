#!/usr/bin/env python3
"""Build one release-marshal eval fixture: repo/, origin.git/, gh-state.json."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def base_repo(root: Path) -> Path:
    origin, repo = root / "origin.git", root / "repo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(repo)], check=True, capture_output=True)
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    write(repo, "README.md", "# orders\n\nOrder management service.\n")
    write(repo, "src/orders/models.py", "class Order:\n    def __init__(self, id, total):\n        self.id = id\n        self.total = total\n")
    write(repo, "src/orders/service.py", "from .models import Order\n\n\ndef list_orders(repo):\n    return repo.all()\n")
    write(repo, "src/orders/api.py", "from .service import list_orders\n\n\ndef get_orders(request, repo):\n    return [o.__dict__ for o in list_orders(repo)]\n")
    write(repo, "tests/test_service.py", "def test_placeholder():\n    assert True\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "chore: initial service")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "switch", "-qc", "develop")
    git(repo, "push", "-q", "origin", "develop")
    return repo


def export_feature_changes(repo: Path) -> None:
    """Uncommitted multi-surface change: model, service, API, tests, docs."""
    write(repo, "src/orders/models.py", "class Order:\n    def __init__(self, id, total, currency=\"EUR\"):\n        self.id = id\n        self.total = total\n        self.currency = currency\n")
    write(repo, "src/orders/export.py", "import csv\nimport io\n\n\ndef orders_to_csv(orders):\n    buf = io.StringIO()\n    w = csv.writer(buf)\n    w.writerow([\"id\", \"total\", \"currency\"])\n    for o in orders:\n        w.writerow([o.id, o.total, o.currency])\n    return buf.getvalue()\n")
    write(repo, "src/orders/api.py", "from .export import orders_to_csv\nfrom .service import list_orders\n\n\ndef get_orders(request, repo):\n    return [o.__dict__ for o in list_orders(repo)]\n\n\ndef export_orders(request, repo):\n    return orders_to_csv(list_orders(repo))\n")
    write(repo, "tests/test_export.py", "from src.orders.export import orders_to_csv\nfrom src.orders.models import Order\n\n\ndef test_csv_header():\n    assert orders_to_csv([Order(1, 10)]).startswith(\"id,total,currency\")\n")
    write(repo, "docs/export.md", "# Order export\n\n`GET /orders/export` returns all orders as CSV.\n")


def pr(number: int, head: str, decision: str, reviews: list[dict], checks: str = "SUCCESS") -> dict:
    return {
        "number": number, "title": "feat: add order CSV export", "url": f"https://github.com/acme/orders/pull/{number}",
        "state": "OPEN", "isDraft": False, "headRefName": head, "baseRefName": "develop",
        "author": {"login": "eval-bot"}, "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN" if decision == "APPROVED" else "BLOCKED",
        "reviewDecision": decision, "reviews": reviews,
        "statusCheckRollup": [{"name": "test", "status": "COMPLETED", "conclusion": checks}],
    }


PROTECTION = {"branches/develop/protection": {"required_pull_request_reviews": {"required_approving_review_count": 1}}}


def setup(case: str, root: Path) -> None:
    repo = base_repo(root)
    state: dict = {"repo": "acme/orders", "default_branch": "main", "prs": [], "api": PROTECTION}

    if case == "es-dirty-feature":
        git(repo, "switch", "-qc", "feat/order-export")
        export_feature_changes(repo)
    elif case == "on-main":
        git(repo, "switch", "-q", "main")
        export_feature_changes(repo)
    elif case in ("merge-not-approved", "merge-approved-ask"):
        git(repo, "switch", "-qc", "feat/order-export")
        export_feature_changes(repo)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "feat(orders): add CSV export")
        git(repo, "push", "-qu", "origin", "feat/order-export")
        if case == "merge-not-approved":
            state["prs"] = [pr(42, "feat/order-export", "REVIEW_REQUIRED", [])]
        else:
            state["prs"] = [pr(42, "feat/order-export", "APPROVED", [{"author": {"login": "maria-dev"}, "state": "APPROVED"}])]
    elif case == "upstream-body":
        git(repo, "switch", "-qc", "feat/order-export")
        export_feature_changes(repo)
        git(repo, "add", "src/orders/models.py", "src/orders/export.py", "tests/test_export.py")
        git(repo, "commit", "-qm", "feat(orders): add CSV serializer with currency")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "feat(orders): expose CSV export endpoint")
    elif case == "force-with-lease":
        git(repo, "switch", "-qc", "feat/order-export")
        export_feature_changes(repo)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "feat(orders): add CSV export")
        git(repo, "push", "-qu", "origin", "feat/order-export")
        write(repo, "src/orders/export.py", (repo / "src/orders/export.py").read_text().replace("buf = io.StringIO()", "buf = io.StringIO(newline=\"\")"))
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "--amend", "--no-edit")
        state["prs"] = [pr(51, "feat/order-export", "REVIEW_REQUIRED", [])]
    else:
        raise SystemExit(f"unknown case {case}")

    (root / "gh-state.json").write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
