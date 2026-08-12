from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_p1140f_authority.py"
CONFORMANCE = ROOT / "conformance" / "p1140f"
AUTHORIZATION = "gate-authorization-v1.json"
FINDINGS = "semantic-findings-v1.json"
REVIEW = "review-target-v1.json"

# The severities the finding registry's own schema admits. A ceiling is required for
# each of them, so this list is read from the schema rather than repeated here: a
# fourth severity added upstream must fail these tests until a ceiling exists for it.
SEVERITIES = json.loads(
    (CONFORMANCE / "semantic-findings-v1.schema.json").read_text(encoding="utf-8")
)["properties"]["findings"]["items"]["properties"]["severity"]["enum"]

# The D-300 regrade the recorded ceilings were sized for: nine findings to P0, three
# left at P1, one to P2. Tests apply it to a copy of the registry, so this file proves
# the ceilings admit the regrade whether or not the committed registry carries it yet.
REGRADE = {
    "P0": (
        "SR-005",
        "SR-006",
        "SR-007",
        "SR-009",
        "SR-010",
        "SR-013",
        "SR-014",
        "SR-015",
        "SR-017",
    ),
    "P1": ("SR-008", "SR-011", "SR-012"),
    "P2": ("SR-016",),
}


def load_validator() -> object:
    specification = importlib.util.spec_from_file_location(
        "validate_p1140f_authority", VALIDATOR
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class ValidateP1140fAuthorityTests(unittest.TestCase):
    """PF-055: the open-finding ceilings are recorded baselines, never Python literals.

    Every case runs against a copy of `conformance/p1140f/`, so a test may change
    registry state without editing the committed records.

    The gate record carries one ceiling per severity. These cases inject the drift a
    partitioned ceiling makes possible — a severity whose ceiling was never recorded,
    a ceiling exceeded by its own severity alone, ceilings that disagree about which
    states count as open — because each of them is a way for a finding to be open and
    governed by nothing while validation reports an improvement.
    """

    def setUp(self) -> None:
        self.validator = load_validator()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.conformance = Path(self.temporary.name) / "p1140f"
        shutil.copytree(CONFORMANCE, self.conformance)
        patcher = patch.object(self.validator, "P1140F", self.conformance)
        patcher.start()
        self.addCleanup(patcher.stop)
        # The copied registry is normalized to the D-300 severities the recorded
        # ceilings were sized for, so that a case about, say, an unknown finding id
        # fails on the unknown finding id rather than on whichever severity the
        # committed registry happens to carry on the day the suite runs.
        # `test_committed_state_passes` restores the committed registry, because
        # whether the tree itself validates is the one question this normalization
        # must not be allowed to answer.
        self.write(FINDINGS, self.regraded_findings())
        self.write(REVIEW, self.unpinned_review())

    def read(self, name: str) -> dict:
        return json.loads((self.conformance / name).read_text(encoding="utf-8"))

    def write(self, name: str, payload: object) -> None:
        (self.conformance / name).write_text(
            payload if isinstance(payload, str) else json.dumps(payload),
            encoding="utf-8",
        )

    def pristine(self, name: str) -> dict:
        """Read a committed record, ignoring anything an earlier subtest wrote.

        Subtests in one method share the copied tree, so a case that lowers a ceiling
        would otherwise leave it lowered for the next severity and fire on the wrong
        one.
        """
        return json.loads((CONFORMANCE / name).read_text(encoding="utf-8"))

    def regraded_findings(self) -> dict:
        """The committed registry with the D-300 severities applied and reopened.

        Reopened, because every ceiling here counts findings in a state the gate record
        calls open. Once the tree closed all thirteen, a case that lowers a ceiling had
        nothing left to exceed it and passed while naming a rule it no longer reached --
        the same shape as a check phrased as an absence and satisfied by emptiness. The
        cases that are *about* closure write the closed registry back themselves.
        """
        findings = self.pristine(FINDINGS)
        for severity, identifiers in REGRADE.items():
            for identifier in identifiers:
                self.finding(findings, identifier)["severity"] = severity
        for row in findings["findings"]:
            row["state"] = "repaired-pending-review"
            row["reviewed_commit"] = None
            row["review_verdict"] = "pending"
        return findings

    def unpinned_review(self) -> dict:
        """The review target as it stands before a head is pinned.

        A pinned, passing review and an open finding cannot coexist -- the validator
        refuses exactly that pair -- so a sandbox that reopens findings must unpin the
        review with them or every case fails on the review rather than on its subject.
        """
        review = self.pristine(REVIEW)
        review["state"] = "not-pinned"
        review["reviewed_commit"] = None
        review["validation_run"] = None
        review["finding_registry_sha256"] = None
        review["artifact_registry_sha256"] = None
        review["review_verdict"] = "pending"
        review["reviewed_at"] = None
        return review

    def run_main(self) -> int:
        with redirect_stdout(io.StringIO()):
            return self.validator.main()

    def run_main_output(self) -> str:
        stream = io.StringIO()
        with redirect_stdout(stream):
            self.validator.main()
        return stream.getvalue()

    def test_committed_state_passes(self) -> None:
        """The committed records as they stand, with no normalization applied."""
        self.write(FINDINGS, self.pristine(FINDINGS))
        self.write(REVIEW, self.pristine(REVIEW))

        self.assertEqual(self.run_main(), 0)

    def test_closing_a_finding_leaves_the_validator_green(self) -> None:
        findings = self.read(FINDINGS)
        closed = next(
            row for row in findings["findings"] if row["finding_id"] == "SR-006"
        )
        closed["state"] = "closed"
        closed["closure_evidence"] = ["docs/planning/TASK_CATALOG.md"]
        self.write(FINDINGS, findings)

        self.assertEqual(self.run_main(), 0)

    def test_open_count_above_the_baseline_fails(self) -> None:
        record = self.read(AUTHORIZATION)
        record["open_p1_baseline"]["count"] -= 1
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("active P1 findings regressed", str(raised.exception))

    def test_a_severity_with_no_recorded_ceiling_fails(self) -> None:
        """The hole the severity-regrading proposal exposed.

        A ceiling fails only when its own count is *exceeded*. Regrading a finding to
        a severity that has no ceiling therefore lowers the count that was watching it
        and, without this check, leaves validation green while the regraded finding is
        tracked by nothing. The gate record now declares a ceiling for every severity,
        so the drift is injected by deleting one rather than by regrading into a gap.
        """
        findings = self.read(FINDINGS)
        self.finding(findings, "SR-010")["severity"] = "P0"
        self.write(FINDINGS, findings)
        record = self.read(AUTHORIZATION)
        del record["open_p0_baseline"]
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        message = str(raised.exception)
        self.assertIn("no recorded ceiling", message)
        self.assertIn("SR-010", message)
        self.assertIn("A validator change would hide these findings instead", message)

    def test_regrading_nine_findings_does_not_pass_by_emptying_the_ceiling(
        self,
    ) -> None:
        """The proposal's actual scenario, which would have gone green.

        Nine findings move to P0 with no P0 ceiling recorded. All nine are named in
        the failure, because a message reporting only a count would leave the owner to
        work out which findings had walked out of scope.
        """
        self.write(FINDINGS, self.regraded_findings())
        record = self.read(AUTHORIZATION)
        del record["open_p0_baseline"]
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        message = str(raised.exception)
        self.assertIn("no recorded ceiling", message)
        for identifier in REGRADE["P0"]:
            self.assertIn(identifier, message)

    def test_the_recorded_regrade_keeps_every_severity_governed(self) -> None:
        """The ceilings are sized for the regrade they were recorded against.

        Nine P0, three P1 and one P2 is the D-300 partition, and the recorded ceilings
        admit exactly it. This is the case that makes the counts in the gate record
        falsifiable rather than plausible, and it holds whether or not the committed
        registry has been regraded yet.
        """
        self.write(FINDINGS, self.regraded_findings())

        self.assertEqual(self.run_main(), 0)

    def test_the_regrade_is_a_partition_and_not_a_relaxation(self) -> None:
        """The same thirteen findings, redistributed: the aggregate does not move."""
        record = self.pristine(AUTHORIZATION)
        ceilings = {
            severity: record[f"open_{severity.lower()}_baseline"]["count"]
            for severity in SEVERITIES
        }

        self.assertEqual(
            sum(ceilings.values()),
            record["gates"][-1]["authorization"]["open_p1_findings_at_authorization"],
            "the per-severity ceilings must sum to the count recorded when P-1104 was "
            "opened; a larger sum is a relaxation wearing a partition's clothes",
        )

    def test_every_severity_the_registry_can_carry_has_a_ceiling(self) -> None:
        """Coverage is what makes a regrade safe, not the individual counts."""
        record = self.pristine(AUTHORIZATION)
        declared = {
            ceiling["severity"]
            for key, ceiling in record.items()
            if key.startswith("open_p") and key.endswith("_baseline")
        }

        self.assertEqual(declared, set(SEVERITIES))

    def test_each_severity_ceiling_is_enforced_independently(self) -> None:
        """Lower one ceiling by one; that severity, and only that one, must fail.

        Every other ceiling keeps its recorded value and the registry keeps the D-300
        severities, so nothing except the ceiling under test can be what failed. A
        single shared check reading one severity would pass two of these three.
        """
        for severity in SEVERITIES:
            with self.subTest(severity=severity):
                self.write(FINDINGS, self.regraded_findings())
                active = len(REGRADE[severity])
                record = self.pristine(AUTHORIZATION)
                record[f"open_{severity.lower()}_baseline"]["count"] = active - 1
                self.write(AUTHORIZATION, record)

                with self.assertRaises(RuntimeError) as raised:
                    self.run_main()

                self.assertIn(
                    f"active {severity} findings regressed: {active} open exceeds "
                    f"the recorded baseline of {active - 1}",
                    str(raised.exception),
                )

    def test_a_count_exceeding_its_own_ceiling_fails_after_the_regrade(self) -> None:
        """P0 is nine; a tenth open P0 is a regression even though P1 has room."""
        findings = self.regraded_findings()
        self.finding(findings, "SR-008")["severity"] = "P0"
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn(
            "active P0 findings regressed: 10 open exceeds the recorded baseline of 9",
            str(raised.exception),
        )

    def test_ceilings_that_disagree_about_counted_states_fail(self) -> None:
        """A narrower counted_states is the same escape, reached by editing words."""
        record = self.read(AUTHORIZATION)
        record["open_p0_baseline"]["counted_states"] = ["open"]
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn(
            "recorded ceilings disagree about which states count as open",
            str(raised.exception),
        )

    def test_a_ceiling_recorded_under_the_wrong_property_fails(self) -> None:
        """The property name and the severity it pins may not drift apart."""
        record = self.read(AUTHORIZATION)
        record["open_p2_baseline"]["severity"] = "P0"
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("'P2' was expected", str(raised.exception))

    def test_the_summary_reports_every_severity(self) -> None:
        """A summary naming P1 alone would report an improvement after a regrade."""
        self.write(FINDINGS, self.regraded_findings())

        output = self.run_main_output()

        self.assertIn("active_p0=9 baseline_p0=9", output)
        self.assertIn("active_p1=3 baseline_p1=3", output)
        self.assertIn("active_p2=1 baseline_p2=1", output)

    def test_a_state_outside_counted_states_fails(self) -> None:
        """Neither open nor closed is governed by nothing."""
        findings = self.read(FINDINGS)
        findings["findings"][3]["state"] = "deferred"
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("the ceiling does not count", str(raised.exception))

    def test_the_recorded_escape_also_requires_a_schema_amendment(self) -> None:
        """Naming an owner action is only honest if the action is reachable.

        The validator tells the owner to add the missing ceiling. That was once not
        sufficient on its own: `gate-authorization-v1.schema.json` set
        `additionalProperties: false` and admitted `open_p1_baseline` alone, so the
        record could not express a second ceiling at all and a regrade needed the
        schema amended in the same commit. The schema now admits one property per
        severity, and this case holds the half of that amendment that still binds:
        each ceiling is pinned to its own severity constant, so a ceiling cannot be
        recorded under a property naming a different severity than it governs.
        """
        record = self.read(AUTHORIZATION)
        record["open_p1_baseline"]["severity"] = "P0"
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("'P1' was expected", str(raised.exception))

    def test_absent_authorization_record_fails_closed(self) -> None:
        (self.conformance / AUTHORIZATION).unlink()

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn(
            f"missing required P-1140F record: {AUTHORIZATION}", str(raised.exception)
        )

    def test_unparseable_authorization_record_fails_closed(self) -> None:
        self.write(AUTHORIZATION, "{ not json")

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn(
            f"unreadable P-1140F record {AUTHORIZATION}", str(raised.exception)
        )

    def test_schema_invalid_authorization_record_fails_closed(self) -> None:
        record = self.read(AUTHORIZATION)
        record["gates"][-1]["authorization"]["findings_waived"] = True
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn(AUTHORIZATION, str(raised.exception))

    def test_authorized_gate_without_an_authorization_record_fails_closed(self) -> None:
        record = self.read(AUTHORIZATION)
        record["gates"][-1]["authorization"] = None
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn(AUTHORIZATION, str(raised.exception))

    def test_authorization_naming_an_unknown_finding_fails(self) -> None:
        record = self.read(AUTHORIZATION)
        record["gates"][-1]["authorization"]["findings_open_at_authorization"].append(
            "SR-999"
        )
        self.write(AUTHORIZATION, record)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("names findings outside the registry", str(raised.exception))

    def finding(self, findings: dict, finding_id: str) -> dict:
        return next(
            row for row in findings["findings"] if row["finding_id"] == finding_id
        )

    def test_a_finding_naming_no_conflicting_artifact_fails(self) -> None:
        """The defect this rule exists for: an empty list used to pass silently."""
        findings = self.read(FINDINGS)
        self.finding(findings, "SR-011")["conflicting_artifacts"] = []
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("SR-011 lists no conflicting artifact", str(raised.exception))

    def test_a_conflicting_artifact_that_does_not_exist_fails(self) -> None:
        findings = self.read(FINDINGS)
        self.finding(findings, "SR-011")["conflicting_artifacts"] = [
            "packages/schemas/not-a-real-schema-v1.json"
        ]
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("references missing artifact", str(raised.exception))

    def test_a_well_formed_conflicting_artifact_does_not_fire(self) -> None:
        """A path that exists, with a fragment that file contains, stays green."""
        findings = self.read(FINDINGS)
        self.finding(findings, "SR-011")["conflicting_artifacts"] = [
            "packages/schemas/planning-schema.sql#blocks"
        ]
        self.write(FINDINGS, findings)

        self.assertEqual(self.run_main(), 0)

    def test_a_fragment_the_cited_file_does_not_contain_fails(self) -> None:
        findings = self.read(FINDINGS)
        self.finding(findings, "SR-011")["conflicting_artifacts"] = [
            "packages/schemas/planning-schema.sql#no_such_table_anywhere"
        ]
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("does not contain the cited fragment", str(raised.exception))

    def test_a_self_owned_finding_fails(self) -> None:
        """A finding may not cite its own authority as the thing it contradicts."""
        findings = self.read(FINDINGS)
        row = self.finding(findings, "SR-011")
        row["conflicting_artifacts"] = [row["normative_owners"][0]]
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("SR-011 is self-owned", str(raised.exception))

    def test_a_planned_artifact_that_already_exists_fails(self) -> None:
        findings = self.read(FINDINGS)
        self.finding(findings, "SR-017")["planned_artifacts"] = [
            "packages/schemas/openapi-v1.yaml"
        ]
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("but it exists", str(raised.exception))

    def test_a_planned_artifact_absent_from_the_inventory_fails(self) -> None:
        findings = self.read(FINDINGS)
        self.finding(findings, "SR-017")["planned_artifacts"] = [
            "packages/schemas/unplanned-v1.schema.json"
        ]
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("does not record as planned-missing", str(raised.exception))

    def test_a_reclassified_finding_without_a_restatement_fails(self) -> None:
        findings = self.read(FINDINGS)
        row = self.finding(findings, "SR-015")
        row.pop("restatement")
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("records no restatement", str(raised.exception))

    def pass_the_review(self) -> None:
        review = self.read("review-target-v1.json")
        review["state"] = "reviewed"
        review["review_verdict"] = "pass"
        review["reviewed_commit"] = "a" * 40
        review["validation_run"] = 1
        self.write("review-target-v1.json", review)

    def test_review_cannot_pass_while_findings_are_open(self) -> None:
        self.pass_the_review()

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("cannot pass with active findings", str(raised.exception))

    def test_review_cannot_pass_by_regrading_findings_off_p1(self) -> None:
        """The verdict is blocked by open findings, not by open P1 findings.

        Reading this check off the P1 count alone would have let the D-300 regrade
        empty it: nine findings move to P0, the P1 count drops to three and then to
        zero as those three close, and the review passes with nine open
        contradictions. Severity grades a finding; it does not un-open one.
        """
        findings = self.regraded_findings()
        for identifier in REGRADE["P1"] + REGRADE["P2"]:
            row = self.finding(findings, identifier)
            row["state"] = "closed"
            row["closure_evidence"] = ["docs/planning/TASK_CATALOG.md"]
        self.write(FINDINGS, findings)
        self.pass_the_review()

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn(
            "P-1140F review cannot pass with active findings (P0=9)",
            str(raised.exception),
        )


if __name__ == "__main__":
    unittest.main()
