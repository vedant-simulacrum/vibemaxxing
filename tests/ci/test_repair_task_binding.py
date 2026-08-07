"""Drift-injection tests for scripts/repository/validate_repair_task_binding.py.

The defect this guards is a step whose `Status:` claims completion while its units are
unlanded or its findings open. Before the binding existed that claim was uncheckable:
`TASK_CATALOG.md` named zero units and the work breakdown named zero repair tasks, so
"is P-1140F-2 done?" had no answer derivable from the repository.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_repair_task_binding.py"


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_repair_task_binding", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


CATALOG = """# Task catalog

#### P-1140F-1 — first step

Status: `in-progress-planning`

Scope: things.

#### P-1140F-2 — second step

Status: `blocked-planning`

Dependencies: P-1140F-1.
"""

BREAKDOWN = """# Breakdown

### PF-001 — a unit
Files: `a.md`
Acceptance: it works.
Depends: none
Repair: P-1140F-1
Est: 4
Status: landed
Evidence: validator scripts/repository/validate_repair_task_binding.py

### PF-002 — another unit
Files: `b.md`
Acceptance: it works.
Depends: PF-001
Repair: P-1140F-2
Est: 4
Status: not-started
"""

FINDINGS = {
    "schema_version": 1,
    "program": "P-1140F",
    "findings": [
        {"finding_id": "SR-005", "state": "closed", "repair_task": "P-1140F-1"},
        {"finding_id": "SR-006", "state": "open", "repair_task": "P-1140F-2"},
    ],
}


class RepairTaskBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.root = Path(tempfile.mkdtemp(prefix="repair-binding-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.catalog = self.root / "catalog.md"
        self.breakdown = self.root / "breakdown.md"
        self.findings = self.root / "findings.json"
        self.write(CATALOG, BREAKDOWN, FINDINGS)

    def write(self, catalog: str, breakdown: str, findings: dict) -> None:
        self.catalog.write_text(catalog, encoding="utf-8")
        self.breakdown.write_text(breakdown, encoding="utf-8")
        self.findings.write_text(json.dumps(findings), encoding="utf-8")

    def run_validator(self):
        with (
            patch.object(self.validator, "CATALOG", self.catalog),
            patch.object(self.validator, "BREAKDOWN", self.breakdown),
            patch.object(self.validator, "FINDINGS", self.findings),
        ):
            return self.validator.main()

    def test_a_consistent_binding_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_a_unit_naming_no_repair_task_fails(self) -> None:
        """The exact prior state: every unit bound to nothing."""
        self.write(CATALOG, BREAKDOWN.replace("Repair: P-1140F-2\n", ""), FINDINGS)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("PF-002 names no repair task", str(raised.exception))

    def test_a_unit_naming_a_step_the_catalog_lacks_fails(self) -> None:
        self.write(
            CATALOG,
            BREAKDOWN.replace("Repair: P-1140F-2", "Repair: P-1140F-4"),
            FINDINGS,
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("does not define", str(raised.exception))

    def test_a_step_owning_no_unit_fails(self) -> None:
        """A step nothing is assigned to is prose that cannot complete or fail."""
        self.write(
            CATALOG + "\n#### P-1140F-3 — orphan step\n\nStatus: `blocked-planning`\n",
            BREAKDOWN,
            FINDINGS,
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("owns no unit", str(raised.exception))

    def test_a_step_claiming_completion_with_an_unlanded_unit_fails(self) -> None:
        """The rule the rest of this validator exists to make unfakeable."""
        self.write(
            CATALOG.replace(
                "Status: `blocked-planning`", "Status: `complete-planning`"
            ),
            BREAKDOWN,
            FINDINGS,
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("unlanded units ['PF-002']", str(raised.exception))

    def test_a_step_claiming_completion_with_an_open_finding_fails(self) -> None:
        """Landing every unit is not closure; the findings are the gate."""
        landed = BREAKDOWN.replace(
            "Depends: PF-001\nRepair: P-1140F-2\nEst: 4\nStatus: not-started",
            "Depends: PF-001\nRepair: P-1140F-2\nEst: 4\nStatus: landed",
        )
        self.write(
            CATALOG.replace(
                "Status: `blocked-planning`", "Status: `complete-planning`"
            ),
            landed,
            FINDINGS,
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("unclosed findings ['SR-006']", str(raised.exception))

    def test_a_finding_parked_against_a_step_with_no_work_fails(self) -> None:
        catalog = (
            CATALOG + "\n#### P-1140F-5 — empty step\n\nStatus: `blocked-planning`\n"
        )
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][1]["repair_task"] = "P-1140F-5"

        self.write(catalog, BREAKDOWN, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        # The step-owns-no-unit rule fires first and names the same defect.
        self.assertIn("owns no unit", str(raised.exception))

    def test_an_in_progress_step_with_unlanded_units_is_allowed(self) -> None:
        """Only completion claims are checked; honest in-progress states pass."""
        self.assertEqual(self.run_validator(), 0)


if __name__ == "__main__":
    unittest.main()
