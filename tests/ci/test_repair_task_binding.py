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
Serves: SR-005
Est: 4
Status: landed
Evidence: validator scripts/repository/validate_repair_task_binding.py

### PF-002 — another unit
Files: `b.md`
Acceptance: it works.
Depends: PF-001
Repair: P-1140F-2
Serves: SR-006
Est: 4
Status: not-started
"""

FINDINGS = {
    "schema_version": 1,
    "program": "P-1140F",
    "findings": [
        {
            "finding_id": "SR-005",
            "state": "closed",
            "repair_task": "P-1140F-1",
            "closure_evidence": [],
        },
        {
            "finding_id": "SR-006",
            "state": "open",
            "repair_task": "P-1140F-2",
            "closure_evidence": [],
        },
    ],
}


class BindingFixture:
    """Shared setup only. Carries no tests, so inheriting it does not re-run them."""

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


class RepairTaskBindingTests(BindingFixture, unittest.TestCase):
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
            "Serves: SR-006\nEst: 4\nStatus: not-started",
            "Serves: SR-006\nEst: 4\nStatus: landed",
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


class ServesBindingTests(BindingFixture, unittest.TestCase):
    """`Serves:` ties a unit to the finding it repairs, not just to the step.

    Steps are too coarse: P-1140F-4 owns twelve units and five findings, so landing
    one unit implied nothing about any particular finding, and closure evidence had to
    be assembled by reading. That is the bookkeeping that goes wrong quietly.
    """

    def test_a_unit_serving_no_finding_fails(self) -> None:
        self.write(CATALOG, BREAKDOWN.replace("Serves: SR-006\n", ""), FINDINGS)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("names no finding it serves", str(raised.exception))

    def test_a_unit_serving_a_finding_from_another_step_fails(self) -> None:
        """The binding has to agree with itself or it explains nothing."""
        self.write(
            CATALOG, BREAKDOWN.replace("Serves: SR-006", "Serves: SR-005"), FINDINGS
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn(
            "cannot repair a finding its own step does not own", str(raised.exception)
        )

    def test_a_finding_served_by_no_unit_fails(self) -> None:
        """Nothing landing could ever close it, so it would sit open forever."""
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"].append(
            {"finding_id": "SR-007", "state": "open", "repair_task": "P-1140F-2"}
        )

        self.write(CATALOG, BREAKDOWN, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("served by no unit", str(raised.exception))

    def test_a_finding_closed_while_a_unit_serving_it_is_unlanded_fails(self) -> None:
        """Carrying closure evidence is not the same as being closed."""
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][1]["state"] = "closed"

        self.write(CATALOG, BREAKDOWN, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("units serving it are not all landed", str(raised.exception))


class ClosureEvidenceTests(BindingFixture, unittest.TestCase):
    """`closure_evidence` is the last binding nothing checked before this.

    Before this check existed, four SR-008 entries and one SR-009 entry read
    "PF-0NN at HEAD of planning/some-branch: ..." — a branch that moves and, under
    squash merge, stops existing the moment the unit it names actually lands. These
    tests reproduce that prior state and the other ways the same field can lie.
    """

    def test_a_branch_pinned_entry_is_rejected(self) -> None:
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][0]["closure_evidence"] = [
            "PF-002 at HEAD of planning/some-branch: did a thing"
        ]

        self.write(CATALOG, BREAKDOWN, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("PF-NNN at <40-hex commit>", str(raised.exception))

    def test_a_sha_that_is_not_a_commit_is_rejected(self) -> None:
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][0]["closure_evidence"] = [
            "PF-001 at " + "0" * 40 + ": did a thing"
        ]

        self.write(CATALOG, BREAKDOWN, findings)

        with patch.object(self.validator, "commit_resolves", lambda sha: False):
            with self.assertRaises(self.validator.Failure) as raised:
                self.run_validator()

        self.assertIn("is not a commit in this repository", str(raised.exception))

    def test_commit_resolves_returns_none_when_git_cannot_answer(self) -> None:
        """A checkout that cannot answer must not be read as a rejection.

        `self.root` is a plain tempdir, not a git repository, so `git rev-parse
        --git-dir` run there fails and `run_git` reports it cannot answer.
        """
        with patch.object(self.validator, "ROOT", self.root):
            self.assertIsNone(self.validator.commit_resolves("0" * 40))

    def test_a_unit_that_does_not_serve_the_finding_is_rejected(self) -> None:
        """PF-002 serves SR-006, not SR-005; citing it for SR-005 must fail."""
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][0]["closure_evidence"] = [
            "PF-002 at " + "a" * 40 + ": did a thing"
        ]

        self.write(CATALOG, BREAKDOWN, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("does not serve it", str(raised.exception))

    def test_a_not_started_unit_cannot_be_cited_as_evidence(self) -> None:
        """PF-002 is `Status: not-started` in the base fixture."""
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][1]["closure_evidence"] = [
            "PF-002 at " + "a" * 40 + ": did a thing"
        ]

        self.write(CATALOG, BREAKDOWN, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn(
            "evidence cannot precede the work it describes", str(raised.exception)
        )

    def test_a_settled_finding_resting_on_an_unlanded_unit_is_rejected(self) -> None:
        """A finding may not claim it is done while its own cited unit is still open."""
        breakdown = BREAKDOWN.replace("Status: not-started", "Status: in-progress")
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][1]["state"] = "repaired-pending-review"
        findings["findings"][1]["closure_evidence"] = [
            "PF-002 at " + "a" * 40 + ": did a thing"
        ]

        self.write(CATALOG, breakdown, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn(
            "is not repaired while a unit its own evidence names is still open",
            str(raised.exception),
        )

    def test_a_finding_still_in_progress_may_rest_on_an_unlanded_unit(self) -> None:
        """The same fixture, unsettled, must pass: only settled states are checked.

        This is the companion the failure test above needs: on its own, that test
        cannot tell a genuine settled/unlanded check from one that rejects every
        unlanded citation unconditionally. This fixes the state at `repair-in-progress`
        — not in `SETTLED_STATES` — where the same unlanded citation is honest.
        """
        breakdown = BREAKDOWN.replace("Status: not-started", "Status: in-progress")
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][1]["state"] = "repair-in-progress"
        findings["findings"][1]["closure_evidence"] = [
            "PF-002 at " + "a" * 40 + ": did a thing"
        ]

        self.write(CATALOG, breakdown, findings)

        with patch.object(self.validator, "commit_resolves", lambda sha: True):
            self.assertEqual(self.run_validator(), 0)

    def test_the_optional_scope_qualifier_is_accepted(self) -> None:
        """Live in the real registry for SR-010/PF-021 and SR-011/PF-024."""
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][0]["closure_evidence"] = [
            "PF-001 at " + "a" * 40 + " (audience half only): did a thing"
        ]

        self.write(CATALOG, BREAKDOWN, findings)

        with patch.object(self.validator, "commit_resolves", lambda sha: True):
            self.assertEqual(self.run_validator(), 0)


if __name__ == "__main__":
    unittest.main()
