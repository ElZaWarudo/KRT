#!/usr/bin/env python3
"""Build one Jira-scribe eval fixture: repo/ on a feature branch plus, for
configured cases, a fake Jira on 127.0.0.1 wired through .krt/env/.

Also used by evals/krt-jira-cloud-scribe/setup.py via build(case, root, cloud=True).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOKEN = "fake-token-7f3a9c51e2"
EMAIL = "eval.bot@example.com"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


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
    write(repo, "README.md", "# orders\n\nServicio de gestión de pedidos.\n")
    write(repo, "src/orders/models.py", "class Order:\n    def __init__(self, id, total):\n        self.id = id\n        self.total = total\n")
    write(repo, ".krt/env/.gitignore", "*\n!.gitignore\n!*.example\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "chore: initial service")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "switch", "-qc", "feat/order-csv-export")
    write(repo, "src/orders/export.py", "import csv\nimport io\n\n\ndef orders_to_csv(orders):\n    buf = io.StringIO()\n    w = csv.writer(buf)\n    w.writerow([\"id\", \"total\"])\n    for o in orders:\n        w.writerow([o.id, o.total])\n    return buf.getvalue()\n")
    write(repo, "tests/test_export.py", "from src.orders.export import orders_to_csv\nfrom src.orders.models import Order\n\n\ndef test_header():\n    assert orders_to_csv([Order(1, 10)]).startswith(\"id,total\")\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "feat(orders): add CSV export of orders")
    return repo


def jira_state(case: str, cloud: bool) -> dict:
    key = "KRT" if cloud else "PDP"
    issues = [
        {"key": f"{key}-10", "summary": "Exportación de datos de pedidos", "status": "Terminado", "type": "Tarea",
         "description": "Exportar pedidos a PDF para contabilidad."},
        {"key": f"{key}-11", "summary": "Exportación PDF de pedidos", "status": "Terminado", "type": "Subtarea", "parent": f"{key}-10"},
        {"key": f"{key}-20", "summary": "Mejoras del panel de administración", "status": "En Progreso", "type": "Tarea",
         "description": "Filtros y paginación en el panel de administración."},
    ]
    if case == "pr-review":
        issues.append({
            "key": f"{key}-42", "summary": "Exportar pedidos a CSV", "status": "En Progreso", "type": "Tarea",
            "description": "Permitir descargar el listado de pedidos en formato CSV.",
            "transitions": [{"id": "11", "name": "Por Hacer", "to": "Por Hacer"},
                            {"id": "31", "name": "En Revisión", "to": "En Revisión"},
                            {"id": "41", "name": "Terminado", "to": "Terminado"}],
            "remotelinks": [],
        })
    return {
        "auth": "basic" if cloud else "bearer", "token": TOKEN, "email": EMAIL,
        "myself_401": case == "myself-401",
        "project": {"key": key, "name": "Portal de Pedidos", "issue_types": ["Tarea", "Subtarea", "Historia", "Error", "Epic"]},
        "issues": issues,
        "boards": [{"id": 7, "name": f"Tablero {key}", "type": "scrum"}],
        "sprints": [{"id": 55, "name": "Sprint 14", "state": "active", "originBoardId": 7}],
    }


def start_fake_jira(root: Path, state: dict) -> int:
    (root / "jira-state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False))
    subprocess.Popen(
        [sys.executable, str(HERE / "fake_jira.py"), str(root / "jira-state.json"), str(root)],
        start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(100):
        if (root / "jira-port").exists() and (root / "jira-port").read_text():
            return int((root / "jira-port").read_text())
        time.sleep(0.05)
    raise SystemExit("fake jira did not start")


def build(case: str, root: Path, cloud: bool = False) -> None:
    repo = base_repo(root)
    if case.startswith("unconfigured"):
        if cloud:  # a Server/DC env file is present; the Cloud skill must not borrow it
            write(repo, ".krt/env/jira-scribe.env", f"JIRA_HOST=http://127.0.0.1:9\nJIRA_PROJECT_KEY=PDP\nJIRA_API_TOKEN={TOKEN}\n")
        return
    port = start_fake_jira(root, jira_state(case, cloud))
    host = f"http://127.0.0.1:{port}"
    if cloud:
        write(repo, ".krt/env/jira-cloud-scribe.env",
              f"JIRA_CLOUD_HOST={host}\nJIRA_CLOUD_EMAIL={EMAIL}\nJIRA_CLOUD_API_TOKEN={TOKEN}\nJIRA_CLOUD_PROJECT_KEY=KRT\n")
    else:
        write(repo, ".krt/env/jira-scribe.env", f"JIRA_HOST={host}\nJIRA_PROJECT_KEY=PDP\nJIRA_API_TOKEN={TOKEN}\n")


if __name__ == "__main__":
    build(sys.argv[1], Path(sys.argv[2]))
