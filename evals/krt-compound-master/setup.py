#!/usr/bin/env python3
"""Build one compound-master eval fixture: a tiny shop service with a bug."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


FILES = {
    ".gitignore": "__pycache__/\n*.pyc\n",
    "README.md": "# shop\n\nSmall checkout service. Run tests with `python3 -m unittest discover -s tests`.\n\nBranches: work on `feat/*` or `fix/*` from `develop`; PRs target `develop`.\n",
    "src/shop/__init__.py": "",
    "src/shop/pricing.py": (
        "from dataclasses import dataclass\n\n\n"
        "@dataclass\nclass Item:\n    price: float\n    qty: int = 1\n\n\n"
        "def apply_discount(amount, pct):\n    return amount * (1 - pct / 100)\n\n\n"
        "def checkout_total(items, discount_pct=0):\n"
        "    subtotal = sum(i.price * i.qty for i in items)\n"
        "    discounted = apply_discount(subtotal, discount_pct)\n"
        "    return round(apply_discount(discounted, discount_pct), 2)\n"
    ),
    "src/shop/accounts.py": (
        "USERS = {1: {\"name\": \"ana\", \"role\": \"admin\"}, 2: {\"name\": \"luis\", \"role\": \"customer\"}}\n"
        "ORDERS = {10: {\"user_id\": 2, \"total\": 30.0}}\n\n\n"
        "def get_user(user_id):\n    return USERS.get(user_id)\n"
    ),
    "src/shop/api.py": (
        "from .accounts import get_user\n\n\n"
        "def require_role(current_user, role):\n"
        "    if current_user is None or current_user.get(\"role\") != role:\n"
        "        raise PermissionError(\"forbidden\")\n\n\n"
        "def get_profile(current_user, user_id):\n"
        "    return get_user(user_id)\n"
    ),
    "tests/__init__.py": "",
    "tests/test_pricing.py": (
        "import sys, unittest\nfrom pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / \"src\"))\n"
        "from shop.pricing import Item, checkout_total\n\n\n"
        "class PricingTest(unittest.TestCase):\n"
        "    def test_no_discount(self):\n        self.assertEqual(checkout_total([Item(10, 2)]), 20)\n\n"
        "    def test_discount_applied_once(self):\n        self.assertEqual(checkout_total([Item(50, 2)], 10), 90)\n"
    ),
    "docs/loyalty-work-package.md": (
        "# Work package: loyalty points\n\nApproved scope. Jira parent: SHOP-200 (epic). Base branch: develop.\n\n"
        "Review units, each depends on the previous one:\n\n"
        "1. RU1 Points ledger model and migration (`src/shop/loyalty/models.py`, migration).\n"
        "2. RU2 Earning rules service: 1 point per euro, applied at checkout.\n"
        "3. RU3 Redemption service: redeem points as a discount, with balance checks.\n"
        "4. RU4 REST endpoints for balance and history.\n"
        "5. RU5 Checkout UI showing points earned and a redeem toggle.\n"
        "6. RU6 Monthly points-expiry job and notification email.\n\n"
        "Acceptance criteria are listed per unit in SHOP-200. All units are ready to implement.\n"
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
    git(repo, "commit", "-qm", "chore: initial shop service")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "switch", "-qc", "develop")
    git(repo, "push", "-q", "origin", "develop")
    state = {"repo": "acme/shop", "default_branch": "main", "prs": [],
             "api": {"branches/develop/protection": {"required_pull_request_reviews": {"required_approving_review_count": 1}}}}
    (root / "gh-state.json").write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
