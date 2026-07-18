#!/usr/bin/env python3
"""Compatibility entrypoint for planning repository policy checks."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
runpy.run_path(str(ROOT / "scripts/repository/doctor.py"), run_name="__main__")
