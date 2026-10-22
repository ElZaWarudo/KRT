#!/usr/bin/env python3
"""Reuse the parent suite's fixtures for the legacy (main) critique comparison."""

import runpy
import sys
from pathlib import Path

sys.argv[0] = str(Path(__file__).resolve().parents[1] / "setup.py")
runpy.run_path(sys.argv[0], run_name="__main__")
