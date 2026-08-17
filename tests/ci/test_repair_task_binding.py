"""Drift-injection tests for scripts/repository/validate_repair_task_binding.py.

The defect this guards is a step whose `Status:` claims completion while its units are
unlanded or its findings open. Before the binding existed that claim was uncheckable:
`TASK_CATALOG.md` named zero units and the work breakdown named zero repair tasks, so
"is P-1140F-2 done?" had no answer derivable from the repository.
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

# A commit that exists in this repository: the one PF-001 actually landed at. The
# fixture needs a resolvable sha because SR-005 is `closed` below, and a settled finding
# must now cite every landed unit that serves it. In a shallow clone `commit_resolves`
# answers None and the entry is reported unchecked rather than rejected, which is the
# behaviour that check already had.
PF_001_COMMIT = "0acaba7f25f228477908c2c4bc81a69609f4b682"

FINDINGS = {
    "schema_version": 1,
    "program": "P-1140F",
    "findings": [
        {
            "finding_id": "SR-005",
            "state": "closed",
            "repair_task": "P-1140F-1",
            "closure_evidence": [
                f"PF-001 at {PF_001_COMMIT}: the unit that repairs this finding, cited "
                "by it."
            ],
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


class SeriesMembershipTests(BindingFixture, unittest.TestCase):
    """The series was closed at PF-036, and all thirty-six were taken.

    That bound assumed the set of repairs was final. It was not: SR-007 was recorded as
    repaired while one of its four named conflicting artifacts had never been touched,
    and the unit that repairs it is PF-070. Under the old bound that unit could not
    carry `Repair:` or `Serves:` in any way this validator would read, so landing it
    would have changed no finding's evidence.

    Opening the top of the range is only safe if the two directions below both hold: a
    core unit still cannot drop `Repair:`, and an extended unit cannot claim a finding
    without one.
    """

    #: An extended unit that is ordinary work: neither field, outside the series.
    EXTENDED_PLAIN = """
### PF-070 — an extended unit that is not a repair
Files: `c.md`
Acceptance: it works.
Depends: none
Est: 4
Status: not-started
"""

    #: The same unit as a repair: both fields, inside the series.
    EXTENDED_REPAIR = """
### PF-070 — an extended unit that is a repair
Files: `c.md`
Acceptance: it works.
Depends: none
Repair: P-1140F-2
Serves: SR-006
Est: 4
Status: landed
Evidence: validator scripts/repository/validate_repair_task_binding.py
"""

    def test_an_extended_unit_with_neither_field_stays_outside_the_series(self) -> None:
        """PF-037..PF-069 are exactly this shape and must keep passing."""
        self.write(CATALOG, BREAKDOWN + self.EXTENDED_PLAIN, FINDINGS)

        self.assertEqual(self.run_validator(), 0)

    def test_an_extended_unit_declaring_a_repair_joins_the_series(self) -> None:
        self.write(CATALOG, BREAKDOWN + self.EXTENDED_REPAIR, FINDINGS)

        self.assertEqual(self.run_validator(), 0)

    def test_an_extended_unit_in_the_series_is_actually_checked(self) -> None:
        """Membership has to have consequences, or admitting the unit changes nothing.

        A step may not claim completion while it owns an unlanded unit. PF-070 here is
        `not-started` and owned by P-1140F-2, so a `complete-planning` claim on that step
        must name it. If joining the series were cosmetic, the claim would pass.
        """
        breakdown = BREAKDOWN + self.EXTENDED_REPAIR.replace(
            "Status: landed\nEvidence: validator scripts/repository/validate_repair_task_binding.py\n",
            "Status: not-started\n",
        )
        catalog = CATALOG.replace(
            "Status: `blocked-planning`", "Status: `complete-planning`"
        )

        self.write(catalog, breakdown, FINDINGS)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("PF-070", str(raised.exception))

    def test_an_extended_unit_serving_a_finding_without_a_repair_fails(self) -> None:
        """`Serves:` alone would look like a binding while binding nothing."""
        self.write(
            CATALOG,
            BREAKDOWN + self.EXTENDED_REPAIR.replace("Repair: P-1140F-2\n", ""),
            FINDINGS,
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("PF-070 serves", str(raised.exception))
        self.assertIn("names no repair task", str(raised.exception))

    def test_an_extended_unit_in_the_series_must_still_serve_a_finding(self) -> None:
        self.write(
            CATALOG,
            BREAKDOWN + self.EXTENDED_REPAIR.replace("Serves: SR-006\n", ""),
            FINDINGS,
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("PF-070 names no finding it serves", str(raised.exception))

    def test_a_core_unit_losing_its_repair_task_still_fails(self) -> None:
        """The guarantee the opening must not weaken, asserted with the range open.

        Core membership does not depend on the field, so dropping it fails. Had the
        series been defined as "any unit declaring a repair task", this would pass and
        the check would be satisfied by the units that happened to carry it.
        """
        self.write(
            CATALOG,
            (BREAKDOWN + self.EXTENDED_REPAIR).replace("Repair: P-1140F-1\n", ""),
            FINDINGS,
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("PF-001 names no repair task", str(raised.exception))


class CitationCompletenessTests(BindingFixture, unittest.TestCase):
    """The converse of `ClosureEvidenceTests`, and the direction nothing checked.

    Every rule in that class reads an evidence entry outwards: it must name a unit that
    serves the finding and has landed. None of them reads a landed unit inwards, so a
    unit could declare `Serves: SR-0NN`, record `Status: landed`, and be absent from
    that finding's `closure_evidence` entirely. The finding then read as fully evidenced
    on the entries it happened to carry, and the printed summary agreed with it.

    That is not hypothetical: SR-007 closed without citing PF-073, SR-009 closed without
    citing PF-074, and SR-009 closed without citing PF-016. Three separate reviews found
    the first two by hand; the third was found by this rule on the run that added it.
    """

    #: A second landed unit serving SR-006, used to prove the failure names exactly the
    #: units that are missing rather than every unit the finding has.
    SECOND_UNIT = """
### PF-070 — a second landed unit serving the same finding
Files: `c.md`
Acceptance: it works.
Depends: none
Repair: P-1140F-2
Serves: SR-006
Est: 4
Status: landed
Evidence: validator scripts/repository/validate_repair_task_binding.py
"""

    def settled_sr006(self, state: str, evidence: list[str]) -> dict:
        """SR-006 settled in `state`, with PF-002 landed and `evidence` recorded."""
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][1]["state"] = state
        findings["findings"][1]["closure_evidence"] = evidence
        return findings

    def test_a_landed_serving_unit_absent_from_a_settled_finding_fails(self) -> None:
        """The exact defect. PF-001 is landed and serves SR-005, which is `closed`."""
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][0]["closure_evidence"] = []

        self.write(CATALOG, BREAKDOWN, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn(
            "SR-005 is 'closed' and its closure evidence does not cite ['PF-001']",
            str(raised.exception),
        )

    def test_the_same_unit_during_the_repair_interval_passes(self) -> None:
        """The companion the failure above needs, and the reason for the state gate.

        A unit lands in the commit that repairs the artifact; its evidence entry is a
        narrative claim about that repair and legitimately lands in a later PR. Without
        this case the failure above cannot be told apart from a rule that rejects every
        uncited landed unit, which would fail the repository at the moment a repair
        merges. Identical fixture, `repair-in-progress` instead of `closed`.
        """
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][0]["state"] = "repair-in-progress"
        findings["findings"][0]["closure_evidence"] = []

        self.write(CATALOG, BREAKDOWN, findings)

        self.assertEqual(self.run_validator(), 0)

    def test_the_other_settled_state_is_checked_too(self) -> None:
        """`repaired-pending-review` claims the repair is finished just as `closed` does."""
        findings = json.loads(json.dumps(FINDINGS))
        findings["findings"][0]["state"] = "repaired-pending-review"
        findings["findings"][0]["closure_evidence"] = []

        self.write(CATALOG, BREAKDOWN, findings)

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn(
            "SR-005 is 'repaired-pending-review' and its closure evidence does not "
            "cite ['PF-001']",
            str(raised.exception),
        )

    def test_only_the_uncited_units_are_named(self) -> None:
        """SR-007 carried three good entries and one missing unit; the message must say

        which. PF-002 and PF-070 both land and both serve SR-006; only PF-002 is cited.
        """
        breakdown = (
            BREAKDOWN.replace(
                "Serves: SR-006\nEst: 4\nStatus: not-started",
                "Serves: SR-006\nEst: 4\nStatus: landed\nEvidence: validator x",
            )
            + self.SECOND_UNIT
        )
        findings = self.settled_sr006(
            "closed", ["PF-002 at " + "a" * 40 + ": did a thing"]
        )

        self.write(CATALOG, breakdown, findings)

        with patch.object(self.validator, "commit_resolves", lambda sha: True):
            with self.assertRaises(self.validator.Failure) as raised:
                self.run_validator()

        message = str(raised.exception)
        self.assertIn("does not cite ['PF-070']", message)
        self.assertNotIn("PF-002'", message)

    def test_an_unlanded_serving_unit_need_not_be_cited(self) -> None:
        """The rule keys on `landed`, not on `serves`.

        A unit that has not landed has repaired nothing yet, and requiring a settled
        finding to cite it would demand evidence for work that does not exist — the
        inverse of the mistake this validator already refuses in the other direction,
        where a cited unit that has not landed is rejected.
        """
        breakdown = BREAKDOWN.replace("Status: not-started", "Status: in-progress")
        findings = self.settled_sr006("repaired-pending-review", [])

        self.write(CATALOG, breakdown, findings)

        self.assertEqual(self.run_validator(), 0)

    def test_the_summary_reports_citation_and_not_only_landing(self) -> None:
        """4/4 landed with three cited printed as `4/4` and looked complete."""
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(self.run_validator(), 0)

        output = stdout.getvalue()
        self.assertIn("findings(landed/served,cited)=", output)
        self.assertIn("SR-005:1/1,1", output)
        self.assertIn("SR-006:0/1,0", output)


if __name__ == "__main__":
    unittest.main()
