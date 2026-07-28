#!/usr/bin/env python3
"""Check Word Illuminator runtime dependencies without installing anything."""

from __future__ import annotations

import argparse
import importlib
import json
import shutil
import subprocess


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-render",
        action="store_true",
        help="Fail unless a DOCX renderer and a PDF rasterizer are available.",
    )
    return parser.parse_args()


def can_import(module: str) -> bool:
    try:
        importlib.import_module(module)
    except Exception:
        return False
    return True


def runnable_command(*names: str) -> str | None:
    for name in names:
        command = shutil.which(name)
        if not command:
            continue
        try:
            completed = subprocess.run(
                [command, "--version"],
                check=False,
                capture_output=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if completed.returncode == 0:
            return command
    return None


def network_isolation_available() -> bool:
    unshare = shutil.which("unshare")
    if not unshare:
        return False
    candidates = (
        [unshare, "--net", "--", "true"],
        [
            unshare,
            "--user",
            "--map-root-user",
            "--net",
            "--",
            "true",
        ],
    )
    for command in candidates:
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if completed.returncode == 0:
            return True
    return False


def main() -> int:
    args = parse_args()
    python_modules = {
        "python-docx": can_import("docx"),
        "jsonschema": can_import("jsonschema"),
        "PyMuPDF": can_import("fitz"),
    }
    renderer = runnable_command("libreoffice", "soffice")
    pdftoppm = runnable_command("pdftoppm")
    network_isolation = network_isolation_available()
    core_ready = python_modules["python-docx"] and python_modules["jsonschema"]
    render_ready = bool(
        renderer
        and (pdftoppm or python_modules["PyMuPDF"])
        and network_isolation
    )
    ready = core_ready and (render_ready or not args.require_render)
    report = {
        "ready": ready,
        "core_ready": core_ready,
        "render_ready": render_ready,
        "python_modules": python_modules,
        "tools": {
            "libreoffice": renderer,
            "network_isolation": network_isolation,
            "pdftoppm": pdftoppm,
        },
        "installation_performed": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
