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
    """PF-055: the open-P1 ceiling is a recorded baseline, never a Python literal.

    Every case runs against a copy of `conformance/p1140f/`, so a test may change
    registry state without editing the committed records.
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

    def read(self, name: str) -> dict:
        return json.loads((self.conformance / name).read_text(encoding="utf-8"))

    def write(self, name: str, payload: object) -> None:
        (self.conformance / name).write_text(
            payload if isinstance(payload, str) else json.dumps(payload),
            encoding="utf-8",
        )

    def run_main(self) -> int:
        with redirect_stdout(io.StringIO()):
            return self.validator.main()

    def test_committed_state_passes(self) -> None:
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

        The recorded baseline covers P1 alone and fails only when the count
        *exceeds* it. Regrading a finding to P0 therefore lowers the P1 count
        and, without this check, leaves validation green while the regraded
        finding is tracked by nothing.
        """
        findings = self.read(FINDINGS)
        next(
            row for row in findings["findings"] if row["finding_id"] == "SR-010"
        )["severity"] = "P0"
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        message = str(raised.exception)
        self.assertIn("no recorded ceiling", message)
        self.assertIn("SR-010", message)

    def test_regrading_nine_findings_does_not_pass_by_emptying_the_ceiling(self) -> None:
        """The proposal's actual scenario, which would have gone green."""
        findings = self.read(FINDINGS)
        regraded = [
            "SR-005", "SR-006", "SR-007", "SR-009", "SR-010",
            "SR-013", "SR-014", "SR-015", "SR-017",
        ]
        for row in findings["findings"]:
            if row["finding_id"] in regraded:
                row["severity"] = "P0"
        self.write(FINDINGS, findings)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        message = str(raised.exception)
        for identifier in regraded:
            self.assertIn(identifier, message)

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

        The validator tells the owner to add the missing ceiling. That is not
        sufficient on its own: `gate-authorization-v1.schema.json` pins
        `open_p1_baseline.severity` to the constant `P1` and sets
        `additionalProperties: false`, so the record cannot express a second
        ceiling at all. A regrade therefore needs the schema amended in the same
        commit, and this test exists so that constraint is discovered here
        rather than halfway through the change.
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

    def test_review_cannot_pass_while_p1_findings_are_open(self) -> None:
        review = self.read("review-target-v1.json")
        review["state"] = "reviewed"
        review["review_verdict"] = "pass"
        review["reviewed_commit"] = "a" * 40
        review["validation_run"] = 1
        self.write("review-target-v1.json", review)

        with self.assertRaises(RuntimeError) as raised:
            self.run_main()

        self.assertIn("cannot pass with active P1 findings", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
