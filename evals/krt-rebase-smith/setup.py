#!/usr/bin/env python3
"""Build one rebase-smith eval fixture: repo/ with a local bare origin.

All cases end on a feature branch whose base (develop) has moved on.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def commit(repo: Path, rel: str, text: str, message: str) -> None:
    write(repo, rel, text)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", message)


def base_repo(root: Path) -> Path:
    origin, repo = root / "origin.git", root / "repo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(repo)], check=True, capture_output=True)
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    commit(repo, "README.md", "# orders\n", "chore: initial service")
    commit(repo, "src/orders/service.py", "def list_orders(repo):\n    return repo.all() or []\n", "feat(orders): list orders")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "switch", "-qc", "develop")
    git(repo, "push", "-q", "origin", "develop")
    return repo


def advance_develop(repo: Path) -> None:
    git(repo, "switch", "-q", "develop")
    commit(repo, "src/orders/health.py", "def health():\n    return 'ok'\n", "feat(health): add health endpoint")
    git(repo, "push", "-q", "origin", "develop")


def export_branch(repo: Path) -> None:
    git(repo, "switch", "-qc", "feat/order-export", "develop")
    commit(repo, "src/orders/export.py", "def orders_to_csv(orders):\n    return '\\n'.join(str(o.id) for o in orders)\n", "feat(orders): add CSV export")
    commit(repo, "docs/export.md", "# Export\n", "docs(orders): document CSV export")


def setup(case: str, root: Path) -> None:
    repo = base_repo(root)
    if case == "stacked-squash":
        git(repo, "switch", "-qc", "feat/order-model")
        commit(repo, "src/orders/models.py", "class Order:\n    pass\n", "feat(orders): add order model")
        commit(repo, "src/orders/models.py", "class Order:\n    def __init__(self, id):\n        self.id = id\n", "feat(orders): add order id")
        git(repo, "push", "-qu", "origin", "feat/order-model")
        git(repo, "switch", "-qc", "feat/order-export")
        commit(repo, "src/orders/export.py", "def orders_to_csv(orders):\n    return '\\n'.join(str(o.id) for o in orders)\n", "feat(orders): add CSV export")
        commit(repo, "docs/export.md", "# Export\n", "docs(orders): document CSV export")
        git(repo, "push", "-qu", "origin", "feat/order-export")
        # feat/order-model lands on develop as one squash commit.
        git(repo, "switch", "-q", "develop")
        git(repo, "merge", "-q", "--squash", "feat/order-model")
        git(repo, "commit", "-qm", "feat(orders): add order model (#12)")
        git(repo, "push", "-q", "origin", "develop")
        git(repo, "switch", "-q", "feat/order-export")
    elif case == "dirty-tree":
        export_branch(repo)
        git(repo, "push", "-qu", "origin", "feat/order-export")
        advance_develop(repo)
        git(repo, "switch", "-q", "feat/order-export")
        write(repo, "src/orders/export.py", "def orders_to_csv(orders):\n    return '\\n'.join(f'{o.id},{o.total}' for o in orders)\n")
    elif case == "plan-push-mode-changed":
        export_branch(repo)
        git(repo, "push", "-qu", "origin", "feat/order-export")
        advance_develop(repo)
        git(repo, "switch", "-q", "feat/order-export")
    elif case == "plan-push-matches":
        export_branch(repo)
        advance_develop(repo)
        git(repo, "switch", "-q", "feat/order-export")
    else:
        raise SystemExit(f"unknown case {case}")


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
