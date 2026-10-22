#!/usr/bin/env python3
"""Reuse the claims-app fixture from the polish-council suite (see its docstring for planted problems)."""

import runpy
import sys
from pathlib import Path

fixture = runpy.run_path(str(Path(__file__).resolve().parents[1] / "krt-product-polish-council" / "setup.py"))
fixture["build"](Path(sys.argv[2]))
