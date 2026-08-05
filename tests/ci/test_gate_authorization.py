from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
DOCTOR = ROOT / "scripts" / "repository" / "doctor.py"

RECORD_PATH = "conformance/p1140f/gate-authorization-v1.json"
REGISTRY_PATH = "conformance/p1140f/semantic-findings-v1.json"
GATE_DOCUMENT = "docs/gate.md"
SUMMARY_DOCUMENT = "docs/summary.md"


def load_doctor() -> object:
    specification = importlib.util.spec_from_file_location("repository_doctor", DOCTOR)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def finding(identifier: str, state: str, severity: str = "P1") -> dict:
    return {"finding_id": identifier, "severity": severity, "state": state}


def build_record(baseline_count: int) -> dict:
    return {
        "schema_version": 1,
        "phase": "implementation",
        "recorded_at": "2026-08-05",
        "finding_registry": REGISTRY_PATH,
        "open_p1_baseline": {
            "severity": "P1",
            "count": baseline_count,
            "rule": "non-regression",
            "counted_states": ["open", "repair-in-progress", "repaired-pending-review"],
            "recorded_at": "2026-08-05",
            "reference": "https://example.invalid/issues/44",
        },
        "registry_summary_documents": [SUMMARY_DOCUMENT],
        "open_p1_claim_patterns": ["([0-9]+) active P1 findings"],
        "gates": [
            {
                "gate": "P-1104",
                "state": "authorized-open",
                "authorization": {
                    "authorized_by": "owner",
                    "authorized_at": "2026-08-05",
                    "reference": "https://example.invalid/issues/44",
                    "reference_kind": "github-issue",
                    "open_p1_findings_at_authorization": 2,
                    "opened_with_open_findings": True,
                    "findings_waived": False,
                    "acknowledgement": "Opened with findings open. They are tracked, not waived.",
                },
                "documents": [
                    {
                        "path": GATE_DOCUMENT,
                        "requires": ["authorized-open"],
                        "forbids": ["P-1104 remains blocked"],
                    }
                ],
            }
        ],
    }


class GateAuthorizationTests(unittest.TestCase):
    """The phase gate is data, not prose, and it fails closed when the data is unusable."""

    def setUp(self) -> None:
        self.doctor = load_doctor()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "conformance" / "p1140f").mkdir(parents=True)
        (self.root / "docs").mkdir()
        (self.root / GATE_DOCUMENT).write_text(
            "P-1104 is authorized-open.\n", encoding="utf-8"
        )

    def write_record(self, record: object) -> None:
        path = self.root / RECORD_PATH
        path.write_text(
            record if isinstance(record, str) else json.dumps(record), encoding="utf-8"
        )

    def write_registry(self, findings: list[dict]) -> None:
        (self.root / REGISTRY_PATH).write_text(
            json.dumps({"findings": findings}), encoding="utf-8"
        )

    def write_summary(self, active: int, first: str, last: str) -> None:
        (self.root / SUMMARY_DOCUMENT).write_text(
            f"{first} through {last}: {active} active P1 findings remain open and tracked.\n",
            encoding="utf-8",
        )

    def test_open_count_below_baseline_passes(self) -> None:
        self.write_record(build_record(baseline_count=2))
        self.write_registry([finding("SR-005", "closed"), finding("SR-006", "open")])
        self.write_summary(1, "SR-005", "SR-006")

        errors, summary = self.doctor.evaluate_phase(self.root)

        self.assertEqual(errors, [])
        self.assertEqual(
            summary, "phase=implementation gates=P-1104:authorized-open open_p1=1/2"
        )

    def test_open_count_above_baseline_fails(self) -> None:
        self.write_record(build_record(baseline_count=1))
        self.write_registry(
            [finding("SR-005", "open"), finding("SR-006", "repair-in-progress")]
        )
        self.write_summary(2, "SR-005", "SR-006")

        errors, _ = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("regressed: 2 open exceeds the recorded baseline of 1", errors[0])

    def test_absent_record_fails_closed(self) -> None:
        self.write_registry([finding("SR-005", "open")])
        self.write_summary(1, "SR-005", "SR-005")

        errors, summary = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(f"missing phase record: {RECORD_PATH}", errors[0])
        self.assertEqual(summary, "phase=unknown")

    def test_malformed_record_fails_closed(self) -> None:
        self.write_registry([finding("SR-005", "open")])
        self.write_summary(1, "SR-005", "SR-005")
        self.write_record("{ not json")

        errors, summary = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("unreadable phase record", errors[0])
        self.assertEqual(summary, "phase=unknown")

    def test_record_missing_baseline_fails_closed(self) -> None:
        record = build_record(baseline_count=2)
        del record["open_p1_baseline"]["count"]
        self.write_record(record)
        self.write_registry([finding("SR-005", "open")])
        self.write_summary(1, "SR-005", "SR-005")

        errors, _ = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "open_p1_baseline.count must be a non-negative integer", errors[0]
        )

    def test_authorized_gate_without_authorization_fails_closed(self) -> None:
        record = build_record(baseline_count=2)
        record["gates"][0]["authorization"] = None
        self.write_record(record)
        self.write_registry([finding("SR-005", "open")])
        self.write_summary(1, "SR-005", "SR-005")

        errors, _ = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("authorized-open without an authorization record", errors[0])

    def test_waived_findings_are_rejected(self) -> None:
        record = build_record(baseline_count=2)
        record["gates"][0]["authorization"]["findings_waived"] = True
        self.write_record(record)
        self.write_registry([finding("SR-005", "open")])
        self.write_summary(1, "SR-005", "SR-005")

        errors, _ = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("findings are never waived", errors[0])

    def test_prose_contradicting_the_record_is_reported(self) -> None:
        self.write_record(build_record(baseline_count=2))
        self.write_registry([finding("SR-005", "open"), finding("SR-006", "open")])
        self.write_summary(2, "SR-005", "SR-006")
        (self.root / GATE_DOCUMENT).write_text(
            "P-1104 remains blocked.\n", encoding="utf-8"
        )

        errors, _ = self.doctor.evaluate_phase(self.root)

        self.assertEqual(
            errors,
            [
                f"{GATE_DOCUMENT} is missing required P-1104 token: authorized-open",
                f"{GATE_DOCUMENT} still carries superseded P-1104 token: P-1104 remains blocked",
            ],
        )

    def test_gate_state_is_read_from_the_record_not_from_the_validator(self) -> None:
        record = build_record(baseline_count=2)
        record["phase"] = "planning-contract-repair"
        record["gates"][0]["state"] = "blocked-approval"
        record["gates"][0]["authorization"] = None
        record["gates"][0]["documents"][0]["requires"] = []
        record["gates"][0]["documents"][0]["forbids"] = []
        self.write_record(record)
        self.write_registry([finding("SR-005", "open"), finding("SR-006", "open")])
        self.write_summary(2, "SR-005", "SR-006")

        errors, summary = self.doctor.evaluate_phase(self.root)

        self.assertEqual(errors, [])
        self.assertEqual(
            summary,
            "phase=planning-contract-repair gates=P-1104:blocked-approval open_p1=2/2",
        )

    def test_closing_a_finding_passes_once_the_prose_states_the_new_count(self) -> None:
        self.write_record(build_record(baseline_count=2))
        self.write_registry([finding("SR-005", "closed"), finding("SR-006", "open")])
        self.write_summary(1, "SR-005", "SR-006")

        errors, summary = self.doctor.evaluate_phase(self.root)

        self.assertEqual(errors, [])
        self.assertIn("open_p1=1/2", summary)

    def test_a_stale_count_claim_names_the_number_the_document_states(self) -> None:
        self.write_record(build_record(baseline_count=2))
        self.write_registry([finding("SR-005", "closed"), finding("SR-006", "open")])
        self.write_summary(2, "SR-005", "SR-006")

        errors, _ = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            f"{SUMMARY_DOCUMENT} claims 2 open P1 findings; the registry has 1",
            errors[0],
        )

    def test_incidental_digits_do_not_satisfy_the_count_check(self) -> None:
        """A bare substring search would pass here; matching the claim must not.

        The document states 2 while the registry holds 1, and separately contains a
        `2026-07-01` date whose digits include the correct count.
        """
        self.write_record(build_record(baseline_count=2))
        self.write_registry([finding("SR-005", "closed"), finding("SR-006", "open")])
        (self.root / SUMMARY_DOCUMENT).write_text(
            "Updated: 2026-07-01\nSR-005 through SR-006: 2 active P1 findings remain open.\n",
            encoding="utf-8",
        )

        errors, _ = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("claims 2 open P1 findings; the registry has 1", errors[0])

    def test_a_document_stating_no_count_is_reported(self) -> None:
        self.write_record(build_record(baseline_count=2))
        self.write_registry([finding("SR-005", "open"), finding("SR-006", "open")])
        (self.root / SUMMARY_DOCUMENT).write_text(
            "SR-005 through SR-006 are tracked in the registry.\n", encoding="utf-8"
        )

        errors, _ = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("states no open P1 count", errors[0])

    def test_an_uncompilable_claim_pattern_fails_closed(self) -> None:
        record = build_record(baseline_count=2)
        record["open_p1_claim_patterns"] = ["([0-9]+ unbalanced"]
        self.write_record(record)
        self.write_registry([finding("SR-005", "open")])
        self.write_summary(1, "SR-005", "SR-005")

        errors, summary = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("is not a regular expression", errors[0])
        self.assertEqual(summary, "phase=unknown")

    def test_a_claim_pattern_without_one_capturing_group_fails_closed(self) -> None:
        record = build_record(baseline_count=2)
        record["open_p1_claim_patterns"] = ["[0-9]+ active P1 findings"]
        self.write_record(record)
        self.write_registry([finding("SR-005", "open")])
        self.write_summary(1, "SR-005", "SR-005")

        errors, summary = self.doctor.evaluate_phase(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("exactly one capturing group", errors[0])
        self.assertEqual(summary, "phase=unknown")

    def test_committed_claim_patterns_match_the_committed_documents(self) -> None:
        record = self.doctor.load_record(ROOT)
        active = self.doctor.open_p1_count(ROOT, record)
        patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in record["open_p1_claim_patterns"]
        ]

        for relative_path in record["registry_summary_documents"]:
            errors: list[str] = []
            self.doctor.check_open_p1_claims(
                relative_path,
                (ROOT / relative_path).read_text(encoding="utf-8"),
                active,
                patterns,
                errors,
            )
            self.assertEqual(errors, [], relative_path)

    def test_committed_record_matches_the_committed_registry(self) -> None:
        record = self.doctor.load_record(ROOT)
        active = self.doctor.open_p1_count(ROOT, record)

        self.assertLessEqual(active, record["open_p1_baseline"]["count"])
        gates = {gate["gate"]: gate for gate in record["gates"]}
        authorization = gates["P-1104"]["authorization"]
        self.assertEqual(gates["P-1104"]["state"], "authorized-open")
        self.assertIs(authorization["findings_waived"], False)
        self.assertTrue(authorization["opened_with_open_findings"])
        self.assertEqual(authorization["open_p1_findings_at_authorization"], 13)


if __name__ == "__main__":
    unittest.main()
