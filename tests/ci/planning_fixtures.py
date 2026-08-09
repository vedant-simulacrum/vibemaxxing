"""Shared drift-injection scaffolding for the planning validators.

Every one of these suites does the same three things: load
`scripts/repository/validate_planning_artifacts.py` as a module, copy the
repository's real artifacts into a temporary tree, and point the module's path
constants at the copy so a case can corrupt one artifact and assert the exact
substring the validator answers with.

Doing it once matters beyond the line count. Each suite that rebuilt this by hand
chose its own idea of which paths to redirect, and a suite that redirects four of
five constants silently injects its drift into a file the validator never reads, so
the case passes for the wrong reason. `PlanningValidatorMixin` redirects the whole
set or fails.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"

# Every module-level path constant the validators resolve artifacts through. A new
# constant that is not redirected leaves a case injecting into a file nothing reads.
REDIRECTED = ("ROOT", "SCHEMAS", "CONFORMANCE")


def load_validator(name: str = "validate_planning_artifacts"):
    specification = importlib.util.spec_from_file_location(name, VALIDATOR)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class PlanningValidatorMixin:
    """A validator module reading a writable copy of the repository's artifacts."""

    #: Repository-relative directories copied into the sandbox. Kept small on
    #: purpose: copying the whole tree would make every case slow enough that the
    #: suite stops being run.
    COPIED = ("packages/schemas", "conformance/planning", "docs/architecture")

    def setUp(self) -> None:  # noqa: D102 - unittest hook
        super().setUp()
        self.sandbox = Path(tempfile.mkdtemp(prefix="planning-drift-"))
        self.addCleanup(shutil.rmtree, self.sandbox, True)
        for relative in self.COPIED:
            shutil.copytree(ROOT / relative, self.sandbox / relative)

        self.validator = load_validator(f"validate_planning_artifacts_{id(self)}")
        missing = [name for name in REDIRECTED if not hasattr(self.validator, name)]
        if missing:
            raise AssertionError(
                f"the validator no longer defines {missing}; a case would inject into "
                "a path nothing reads"
            )
        self.validator.ROOT = self.sandbox
        self.validator.SCHEMAS = self.sandbox / "packages" / "schemas"
        self.validator.CONFORMANCE = self.sandbox / "conformance"

    # -- artifact helpers ---------------------------------------------------

    def path(self, relative: str) -> Path:
        return self.sandbox / relative

    def read(self, relative: str) -> Any:
        return json.loads(self.path(relative).read_text(encoding="utf-8"))

    def write(self, relative: str, record: Any) -> None:
        self.path(relative).write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )

    def edit_text(self, relative: str, old: str, new: str) -> None:
        target = self.path(relative)
        text = target.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"{relative} does not contain the text to replace")
        target.write_text(text.replace(old, new, 1), encoding="utf-8")

    # -- assertions ---------------------------------------------------------

    def assert_passes(self, check) -> None:
        check()

    def assert_fails(self, check, substring: str) -> None:
        case = self
        assert isinstance(case, unittest.TestCase)
        with case.assertRaises(Exception) as raised:
            check()
        message = str(raised.exception)
        case.assertIn(substring, message)
