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
