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

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
P1140E_VALIDATOR = ROOT / "scripts" / "repository" / "validate_p1140e_contracts.py"

# Every module-level path constant the validators resolve artifacts through. A new
# constant that is not redirected leaves a case injecting into a file nothing reads.
REDIRECTED = ("ROOT", "SCHEMAS", "CONFORMANCE")

# The same rule for `validate_p1140e_contracts.py`. `CONF` is the one that mattered:
# the first version of its suite redirected `SCHEMAS` alone, so a case that mutated
# the state-machine registry tripped `state fixture set mismatch` against the real
# `conformance/p1140e/` before it ever reached the check under test, and the case
# passed on the wrong error.
P1140E_REDIRECTED = ("ROOT", "SCHEMAS", "CONF", "TRACE")


def load_validator(name: str = "validate_planning_artifacts"):
    specification = importlib.util.spec_from_file_location(name, VALIDATOR)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


STATE_VOCABULARY_VALIDATOR = (
    ROOT / "scripts" / "repository" / "validate_state_vocabularies.py"
)


def load_state_vocabulary_validator(name: str = "validate_state_vocabularies"):
    specification = importlib.util.spec_from_file_location(
        name, STATE_VOCABULARY_VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def load_p1140e_validator(name: str = "validate_p1140e_contracts"):
    specification = importlib.util.spec_from_file_location(name, P1140E_VALIDATOR)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def mirror_repository(sandbox: Path, writable: tuple[str, ...]) -> None:
    """Build a sandbox where `writable` is copied and everything else is a symlink.

    `validate_p1140e_contracts.py` resolves the matrix's `normative_owner`,
    `work_unit`, `schema_or_state_owner`, `platform_scope` and `fixture_path` fields
    against `ROOT`, and those five point into four different top-level directories.
    Copying only the trees a case edits would make every one of those existence
    checks fail for a reason the case did not inject, and copying the whole tree
    would put `.git` and the virtualenv in a temporary directory on every test.
    """
    needed = {part for entry in writable for part in (entry, entry.split("/", 1)[0])}
    for entry in sorted(ROOT.iterdir()):
        # `.github/` holds paths the validation matrix cites, so dot-entries are
        # mirrored rather than skipped. Only the two that are neither repository
        # content nor cheap to symlink are left out.
        if entry.name in {".git", ".venv"}:
            continue
        target = sandbox / entry.name
        if entry.name in writable:
            shutil.copytree(entry, target, symlinks=True)
        elif entry.name in needed:
            target.mkdir(parents=True)
            for child in sorted(entry.iterdir()):
                relative = f"{entry.name}/{child.name}"
                if relative in writable:
                    shutil.copytree(child, target / child.name, symlinks=True)
                else:
                    (target / child.name).symlink_to(child)
        else:
            target.symlink_to(entry)


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


class P1140EValidatorMixin:
    """`validate_p1140e_contracts.py` reading a writable mirror of the repository.

    The validator's own `main()` runs end to end here rather than a single check
    function, because the acceptance for PF-035 is about the gate's exit status and
    a check called directly cannot show that the gate reaches it.
    """

    #: Trees a case may edit. Everything else in the repository is symlinked in, so
    #: the matrix's owner, work-unit and fixture citations still resolve.
    WRITABLE = ("docs", "conformance", "packages/schemas")

    def setUp(self) -> None:  # noqa: D102 - unittest hook
        super().setUp()
        self.sandbox = Path(tempfile.mkdtemp(prefix="p1140e-drift-"))
        self.addCleanup(shutil.rmtree, self.sandbox, True)
        mirror_repository(self.sandbox, self.WRITABLE)

        self.validator = load_p1140e_validator(f"validate_p1140e_contracts_{id(self)}")
        missing = [
            name for name in P1140E_REDIRECTED if not hasattr(self.validator, name)
        ]
        if missing:
            raise AssertionError(
                f"the validator no longer defines {missing}; a case would inject into "
                "a path nothing reads"
            )
        self.validator.ROOT = self.sandbox
        self.validator.SCHEMAS = self.sandbox / "packages" / "schemas"
        self.validator.CONF = self.sandbox / "conformance" / "p1140e"
        self.validator.TRACE = (
            self.sandbox / "docs" / "planning" / "decision-traceability"
        )

    # -- running ------------------------------------------------------------

    def run_validator(self) -> tuple[int, str]:
        """Run `main()` with the derived-coverage generator pointed at the sandbox too.

        `generate_p1140e_coverage` is imported by the validator and holds its own
        `ROOT`, `SCHEMAS` and `MATRIX`. Leaving those on the real repository would
        make the reproducibility check compare the committed matrix against the
        committed registries while every other check read the sandbox, so a case that
        edits a registry would fail on a disagreement it did not inject.
        """
        coverage = self.validator.generate_p1140e_coverage
        stdout = io.StringIO()
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(coverage, "ROOT", self.sandbox))
            stack.enter_context(
                patch.object(coverage, "SCHEMAS", self.sandbox / "packages" / "schemas")
            )
            stack.enter_context(
                patch.object(
                    coverage,
                    "MATRIX",
                    self.sandbox
                    / "conformance"
                    / "p1140e"
                    / "validation-matrix-v1.json",
                )
            )
            stack.enter_context(contextlib.redirect_stdout(stdout))
            code = self.validator.main()
        return code, stdout.getvalue()

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
        case = self
        assert isinstance(case, unittest.TestCase)
        case.assertEqual(text.count(old), 1, f"{relative}: {old!r}")
        target.write_text(text.replace(old, new, 1), encoding="utf-8")


class StateVocabularyMixin:
    """`validate_state_vocabularies.py` reading writable copies of its four owners.

    Setup and helpers only, and this one means it: `ValidatorFixture` in
    `tests/ci/test_state_vocabularies.py` says the same in its docstring and carries
    twenty-one cases, so every class inheriting it re-runs all of them. Splitting the
    scaffolding out is what lets a suite reuse the sandbox without adopting another
    suite's assertions.
    """

    OWNERS = (
        ("REGISTRY_PATH", "packages/schemas/state-machine-registry-v1.json"),
        ("SQL_PATH", "packages/schemas/planning-schema.sql"),
        ("OPENAPI_PATH", "packages/schemas/openapi-v1.yaml"),
        (
            "CONTRACT_PATH",
            "docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md",
        ),
    )

    def setUp(self) -> None:  # noqa: D102 - unittest hook
        super().setUp()
        self.validator = load_state_vocabulary_validator()
        self.directory = Path(tempfile.mkdtemp(prefix="state-vocab-"))
        self.addCleanup(shutil.rmtree, self.directory, True)
        self.copies: dict[str, Path] = {}
        for attribute, relative in self.OWNERS:
            source = ROOT / relative
            target = self.directory / source.name
            shutil.copyfile(source, target)
            self.copies[attribute] = target

    def run_validator(self) -> tuple[int, str]:
        stderr = io.StringIO()
        stdout = io.StringIO()
        with contextlib.ExitStack() as stack:
            for attribute, target in self.copies.items():
                stack.enter_context(patch.object(self.validator, attribute, target))
            stack.enter_context(contextlib.redirect_stderr(stderr))
            stack.enter_context(contextlib.redirect_stdout(stdout))
            code = self.validator.main()
        return code, stderr.getvalue() + stdout.getvalue()

    def edit_registry(self, mutate) -> None:
        path = self.copies["REGISTRY_PATH"]
        registry = json.loads(path.read_text(encoding="utf-8"))
        mutate({machine["machine_id"]: machine for machine in registry["machines"]})
        path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    def edit_openapi(self, mutate) -> None:
        import yaml

        path = self.copies["OPENAPI_PATH"]
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        mutate(spec["components"]["schemas"])
        path.write_text(
            yaml.safe_dump(spec, sort_keys=False, width=4096), encoding="utf-8"
        )

    def edit_sql(self, old: str, new: str) -> None:
        path = self.copies["SQL_PATH"]
        text = path.read_text(encoding="utf-8")
        case = self
        assert isinstance(case, unittest.TestCase)
        case.assertEqual(text.count(old), 1, old)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def edit_contract(self, old: str, new: str) -> None:
        path = self.copies["CONTRACT_PATH"]
        text = path.read_text(encoding="utf-8")
        case = self
        assert isinstance(case, unittest.TestCase)
        case.assertEqual(text.count(old), 1, old)
        path.write_text(text.replace(old, new), encoding="utf-8")
