"""A fork quarantines every branch, and a rotation carries every authorization.

Two defects sat behind `PF-010`, both of the same shape: a rule stated in prose that
no artifact could represent.

`device_key_events` held one nullable `continuity_signature` and no account
authorization column at all, while `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` names
three separate things — a payload "signed independently by both old and new keys", and
a server that "verifies recent authentication". One blob can represent none of that, so
an ordinary rotation and a single-signature forgery were the same row.

And D-592 rekeyed `device_sequences` onto the lineage and stopped there. The counter
became lineage-scoped while the uniqueness that enforces it stayed device-scoped, so
the sequence a clone could no longer obtain from the counter it could still write into
`claims` — `unique (device_id, device_sequence)` let two device rows inside one lineage
each hold sequence 42. `checkpoint_receipts` was device-keyed for the same reason and
gave a restored store its own private receipt chain.

Every test here injects the defect and asserts the exact failure text, because a check
that has never been seen to fail is a check nobody has tested.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
SQL = ROOT / "packages" / "schemas" / "planning-schema.sql"
FIXTURE = ROOT / "conformance" / "vibeproof" / "v1" / "fork-and-rotation-vectors.json"


def load_module():
    specification = importlib.util.spec_from_file_location(
        "validate_planning_artifacts", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def table(name: str) -> str:
    found = re.search(
        rf"create table {name} \((?P<body>.*?)\n\);",
        SQL.read_text(encoding="utf-8"),
        re.S,
    )
    assert found is not None, name
    return found.group("body")


def statements(body: str) -> str:
    """The table body with comment lines removed, so prose cannot satisfy a check."""
    return " ".join(
        " ".join(line.split("--", 1)[0] for line in body.splitlines()).split()
    )


class ForkFixtureMixin:
    """Shared fixture access and drift injection.

    A mixin rather than a base `TestCase`: subclassing one would make every test in
    this file run again inside each child class, and a suite that reports a rising
    number for a falling amount of work is a metric that improves when you remove what
    it counts.
    """

    module: Any
    fixture: dict[str, Any]

    def setUp(self) -> None:  # noqa: D102 - unittest hook
        self.module = load_module()
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def drifted(self, mutate) -> dict[str, Any]:
        copied = copy.deepcopy(self.fixture)
        mutate(copied)
        return copied

    def assert_refuses(self, mutate, expected: str) -> None:
        copied = self.drifted(mutate)
        with self.assertRaises(Exception) as caught:  # type: ignore[attr-defined]
            self.module.validate_lineage_fork_and_rotation(copied)
        self.assertIn(expected, str(caught.exception))  # type: ignore[attr-defined]

    def lineage(self, case_id: str) -> dict[str, Any]:
        return next(
            item
            for item in self.fixture["lineages"]
            if item["lineage_case_id"] == case_id
        )


class ForkResolutionTests(ForkFixtureMixin, unittest.TestCase):
    def test_the_corpus_resolves_as_committed(self) -> None:
        self.module.validate_lineage_fork_and_rotation()

    def test_the_fixture_contains_a_lineage_that_branches(self) -> None:
        """The acceptance's first clause. A corpus of unforked lineages proves nothing."""
        forked = [
            lineage
            for lineage in self.fixture["lineages"]
            if self.module.resolve_lineage(lineage)["fork"]
        ]

        self.assertGreaterEqual(len(forked), 1)
        for lineage in forked:
            branches = self.module.resolve_lineage(lineage)["branches"]
            self.assertGreaterEqual(len(branches), 2, lineage["lineage_case_id"])

    def test_every_post_fork_branch_is_quarantined(self) -> None:
        for lineage in self.fixture["lineages"]:
            resolved = self.module.resolve_lineage(lineage)
            if not resolved["fork"]:
                continue
            for branch in resolved["branches"].values():
                self.assertEqual(
                    branch["disposition"], "quarantined", lineage["lineage_case_id"]
                )

    def test_the_branch_that_arrived_first_is_quarantined_too(self) -> None:
        """D-072 quarantines every post-fork branch, so arriving first does not win.

        `device-a` held the tip when `device-b` presented a copied store. Its own
        post-fork claims are retracted retroactively.
        """
        resolved = self.module.resolve_lineage(self.lineage("LN-DUPLICATE-SEQUENCE"))

        self.assertEqual(resolved["dispositions"]["dup-3"][0], "quarantined")
        self.assertEqual(resolved["branches"]["device-a"]["post_fork_claim_count"], 2)

    def test_every_pre_fork_claim_is_accepted(self) -> None:
        for lineage in self.fixture["lineages"]:
            resolved = self.module.resolve_lineage(lineage)
            if not resolved["fork"]:
                continue
            for submission in lineage["submissions"]:
                if submission["sequence"] > resolved["fork_generation"]:
                    continue
                self.assertEqual(
                    resolved["dispositions"][submission["submission_ref"]][0],
                    "accepted",
                    submission["submission_ref"],
                )

    def test_the_control_lineage_quarantines_nothing(self) -> None:
        """Without this, quarantining every input passes every other assertion."""
        resolved = self.module.resolve_lineage(self.lineage("LN-CONTROL"))

        self.assertFalse(resolved["fork"])
        self.assertEqual(
            {disposition for disposition, _ in resolved["dispositions"].values()},
            {"accepted"},
        )

    def test_a_malformed_submission_is_refused_rather_than_quarantined(self) -> None:
        """Neither identifies a branch, so neither may open a fork case."""
        resolved = self.module.resolve_lineage(self.lineage("LN-REFUSALS"))

        self.assertFalse(resolved["fork"])
        self.assertEqual(
            resolved["dispositions"]["ref-2"],
            ("refused", "CLAIM_GAP_DECLARATION_REQUIRED"),
        )
        self.assertEqual(
            resolved["dispositions"]["ref-3"],
            ("refused", "CLAIM_SEQUENCE_UNEXPECTED"),
        )

    def test_every_claim_level_detection_basis_is_exercised(self) -> None:
        bases = {
            self.module.resolve_lineage(lineage)["detection_basis"]
            for lineage in self.fixture["lineages"]
        }

        self.assertEqual(
            bases - {None},
            {
                "duplicate-sequence-continuation",
                "divergent-commitment-chain",
                "duplicate-installation-identity",
            },
        )


class ForkDriftTests(ForkFixtureMixin, unittest.TestCase):
    def test_a_pre_fork_claim_recorded_as_quarantined_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            lineage = fixture["lineages"][1]
            lineage["submissions"][0]["expected_disposition"] = "quarantined"

        self.assert_refuses(
            mutate, "resolved accepted, the fixture records quarantined"
        )

    def test_a_post_fork_claim_recorded_as_accepted_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            lineage = fixture["lineages"][1]
            lineage["submissions"][2]["expected_disposition"] = "accepted"

        self.assert_refuses(
            mutate, "resolved quarantined, the fixture records accepted"
        )

    def test_dropping_a_branch_from_the_expected_set_fails(self) -> None:
        """The signal must not improve when you remove what it counts."""

        def mutate(fixture: dict[str, Any]) -> None:
            fixture["lineages"][1]["expected_branches"].pop()

        self.assert_refuses(mutate, "branch set differs")

    def test_a_fork_declared_where_the_rules_produce_none_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            fixture["lineages"][0]["expected_fork"] = True

        self.assert_refuses(mutate, "does not fork this lineage")

    def test_a_wrong_fork_generation_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            fixture["lineages"][1]["expected_fork_generation"] = 1

        self.assert_refuses(mutate, "fork generation is 2, the fixture records 1")

    def test_a_wrong_detection_basis_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            fixture["lineages"][1]["expected_detection_basis"] = (
                "divergent-commitment-chain"
            )

        self.assert_refuses(
            mutate, "detection basis is duplicate-sequence-continuation"
        )

    def test_a_corpus_that_accepts_nothing_fails(self) -> None:
        """A resolver could otherwise be proved correct by refusing all input."""

        def mutate(fixture: dict[str, Any]) -> None:
            fixture["lineages"][0] = {
                "lineage_case_id": "LN-NOTHING-ACCEPTED",
                "title": "every submission refused",
                "expected_fork": False,
                "expected_fork_generation": None,
                "expected_detection_basis": None,
                "submissions": [
                    {
                        "submission_ref": "empty-1",
                        "device_ref": "device-z",
                        "installation_ref": "install-z",
                        "sequence": 1,
                        "previous_head": "head-nowhere",
                        "head": "head-z1",
                        "expected_disposition": "refused",
                        "expected_reason_code": "CLAIM_GAP_DECLARATION_REQUIRED",
                    }
                ],
                "expected_branches": [],
            }

        self.assert_refuses(mutate, "would let a resolver that refuses everything pass")

    def test_dropping_a_detection_basis_from_the_corpus_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            fixture["lineages"] = [
                lineage
                for lineage in fixture["lineages"]
                if lineage["lineage_case_id"] != "LN-DUPLICATE-INSTALLATION"
            ]

        self.assert_refuses(mutate, "do not exercise every claim-level detection basis")

    def test_a_precedence_list_that_is_not_the_registered_basis_set_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            fixture["detection_precedence"] = ["checkpoint-mismatch"]

        self.assert_refuses(mutate, "not the registered basis set")

    def test_an_unresolvable_reason_code_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            for lineage in fixture["lineages"]:
                for submission in lineage["submissions"]:
                    if submission["expected_reason_code"] == "CLAIM_CHAIN_FORK":
                        submission["expected_reason_code"] = "CLAIM_FORKED"

        self.assert_refuses(mutate, "resolved reason CLAIM_CHAIN_FORK")


class CheckpointPrecedenceTests(ForkFixtureMixin, unittest.TestCase):
    def test_the_newest_acknowledged_head_wins(self) -> None:
        case = self.fixture["checkpoint_resolutions"][0]

        resolved = self.module.resolve_checkpoint_heads(case)

        self.assertEqual(resolved["authoritative_last_sequence"], 6)
        self.assertEqual(resolved["behind"], ["device-h"])
        self.assertFalse(resolved["fork"])

    def test_two_equal_heads_do_not_resolve(self) -> None:
        case = self.fixture["checkpoint_resolutions"][1]

        resolved = self.module.resolve_checkpoint_heads(case)

        self.assertTrue(resolved["fork"])
        self.assertIsNone(resolved["authoritative_last_sequence"])

    def test_ordering_is_over_the_sequence_and_not_the_arrival_order(self) -> None:
        """A clone controls its own clock; it does not control the server's counter."""
        case = copy.deepcopy(self.fixture["checkpoint_resolutions"][0])
        case["acknowledged_heads"].reverse()

        resolved = self.module.resolve_checkpoint_heads(case)

        self.assertEqual(resolved["authoritative_last_sequence"], 6)

    def test_a_corpus_with_no_mismatch_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            fixture["checkpoint_resolutions"] = fixture["checkpoint_resolutions"][:1]

        self.assert_refuses(mutate, "newest-wins is only ever asked a question")

    def test_a_wrong_authoritative_head_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            fixture["checkpoint_resolutions"][0][
                "expected_authoritative_last_sequence"
            ] = 3

        self.assert_refuses(mutate, "authoritative_last_sequence=6")


class RotationAuthorizationTests(ForkFixtureMixin, unittest.TestCase):
    def ordinary(self) -> dict[str, Any]:
        return copy.deepcopy(
            next(
                case
                for case in self.fixture["rotations"]
                if case["rotation_case_id"] == "RT-ORDINARY"
            )
        )

    def test_an_ordinary_rotation_is_admitted(self) -> None:
        self.assertEqual(self.module.admit_key_event(self.ordinary()), (True, None))

    def test_each_authorization_is_independently_required(self) -> None:
        """Neither key signature nor the account gate may stand in for another."""
        for field in (
            "old_key_signature_present",
            "new_key_signature_present",
            "account_recent_auth",
        ):
            with self.subTest(field=field):
                case = self.ordinary()
                case[field] = False

                self.assertEqual(
                    self.module.admit_key_event(case),
                    (False, "DEVICE_KEY_CONTINUITY_BROKEN"),
                )

    def test_a_recovery_may_not_carry_the_outgoing_signature(self) -> None:
        """If the old key can sign, the key is not lost and the ordinary path applies."""
        case = next(
            item
            for item in self.fixture["rotations"]
            if item["rotation_case_id"] == "RT-RECOVERY-WITH-OLD-SIGNATURE"
        )

        self.assertEqual(
            self.module.admit_key_event(case),
            (False, "DEVICE_KEY_CONTINUITY_BROKEN"),
        )

    def test_a_rotation_may_not_borrow_the_recovery_authority(self) -> None:
        case = self.ordinary()
        case["recovery_approval"] = "approved"

        self.assertEqual(
            self.module.admit_key_event(case),
            (False, "DEVICE_KEY_CONTINUITY_BROKEN"),
        )

    def test_a_revocation_needs_no_key_signature_but_needs_the_account(self) -> None:
        case = next(
            item
            for item in self.fixture["rotations"]
            if item["rotation_case_id"] == "RT-REVOCATION"
        )

        self.assertEqual(self.module.admit_key_event(case), (True, None))
        without_account = dict(case, account_recent_auth=False)
        self.assertEqual(
            self.module.admit_key_event(without_account),
            (False, "DEVICE_KEY_CONTINUITY_BROKEN"),
        )

    def test_dropping_a_refusal_vector_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            fixture["rotations"] = [
                case
                for case in fixture["rotations"]
                if case["rotation_case_id"] != "RT-MISSING-OLD-KEY-SIGNATURE"
            ]

        self.assert_refuses(mutate, "old_key_signature_present")

    def test_a_corpus_that_admits_nothing_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            for case in fixture["rotations"]:
                case["expected_admitted"] = False
                case["expected_reason_code"] = "DEVICE_KEY_CONTINUITY_BROKEN"

        self.assert_refuses(mutate, "the rule admits this transition")

    def test_a_vector_recording_the_wrong_outcome_fails(self) -> None:
        def mutate(fixture: dict[str, Any]) -> None:
            for case in fixture["rotations"]:
                if case["rotation_case_id"] == "RT-MISSING-ACCOUNT-AUTH":
                    case["expected_admitted"] = True
                    case["expected_reason_code"] = None

        self.assert_refuses(mutate, "the rule refuses this transition")


class DeviceKeyEventTableTests(unittest.TestCase):
    """`device_key_events` records both authorizations, which is the acceptance."""

    def setUp(self) -> None:
        self.body = statements(table("device_key_events"))

    def test_both_key_signatures_are_separate_columns(self) -> None:
        """The defect: one nullable blob could not tell the two signatures apart."""
        self.assertIn("old_key_signature bytea", self.body)
        self.assertIn("new_key_signature bytea", self.body)
        self.assertNotIn("continuity_signature", self.body)

    def test_the_account_authorization_is_recorded(self) -> None:
        self.assertIn("account_recent_auth boolean not null", self.body)

    def test_an_ordinary_rotation_needs_all_three(self) -> None:
        self.assertIn(
            "constraint device_key_events_rotation_is_dual_authorized check ( "
            "action <> 'rotated' or (old_key_signature is not null and "
            "new_key_signature is not null and account_recent_auth and "
            "previous_key_id is not null) )",
            self.body,
        )

    def test_a_recovery_cannot_carry_an_outgoing_signature(self) -> None:
        self.assertIn(
            "constraint device_key_events_recovery_has_no_old_signature check ( "
            "action <> 'recovered' or (old_key_signature is null and "
            "new_key_signature is not null and recovery_approval = 'approved') )",
            self.body,
        )

    def test_only_a_recovery_carries_a_recovery_approval(self) -> None:
        self.assertIn(
            "constraint device_key_events_recovery_approval_is_scoped check ( "
            "action = 'recovered' or recovery_approval = 'not-required' )",
            self.body,
        )

    def test_the_event_is_scoped_to_the_lineage(self) -> None:
        self.assertIn(
            "lineage_id uuid not null references device_lineages(lineage_id)",
            self.body,
        )


class ForkCaseConstraintTests(ForkFixtureMixin, unittest.TestCase):
    """The two D-383 constraints, over the vectors the traceability row now names."""

    def test_a_resumed_generation_is_strictly_later_than_the_fork(self) -> None:
        """A resolution that replayed the fork it resolved would be a merge."""
        self.assertIn(
            "check (resumed_generation is null or resumed_generation > fork_generation)",
            statements(table("lineage_fork_cases")),
        )

    def test_two_survivors_in_one_case_are_unwritable(self) -> None:
        text = SQL.read_text(encoding="utf-8")

        self.assertIn(
            "create unique index lineage_fork_branches_survivor_idx\n"
            "  on lineage_fork_branches (lineage_fork_case_id)\n"
            "  where disposition = 'survivor';",
            text,
        )

    def test_every_resolved_fork_is_expressible_as_the_normative_record(self) -> None:
        """The fixture cannot describe a resolution the record schema has no shape for."""
        forked = [
            lineage
            for lineage in self.fixture["lineages"]
            if self.module.resolve_lineage(lineage)["fork"]
        ]

        self.assertGreaterEqual(len(forked), 3)
        self.module.validate_lineage_fork_and_rotation()

    def test_a_resolution_naming_one_branch_is_refused_by_the_record(self) -> None:
        """`fork-resolution-v1.schema.json` requires at least two, and here is why."""
        schema = self.module.validate_schema_file(
            ROOT / "packages" / "schemas" / "fork-resolution-v1.schema.json"
        )
        record = {
            "schema_version": 1,
            "case": {
                "lineage_fork_case_id": "00000000-0000-7000-8000-000000000001",
                "lineage_id": "00000000-0000-7000-8000-000000000002",
                "ranked_identity_id": "00000000-0000-7000-8000-000000000003",
                "state": "quarantined",
                "fork_generation": 2,
                "detected_at": "2026-08-09T00:00:00Z",
                "revision": 1,
            },
            "branches": [
                {
                    "lineage_fork_branch_id": "00000000-0000-7000-8000-000000000004",
                    "device_id": "00000000-0000-7000-8000-000000000005",
                    "branch_head_sequence": 3,
                    "disposition": "survivor",
                    "post_fork_claim_count": 1,
                    "created_at": "2026-08-09T00:00:00Z",
                }
            ],
        }

        self.module.expect_invalid(schema, record, "single-branch fork resolution")


class LineageScopedUniquenessTests(unittest.TestCase):
    """D-592 rekeyed the counter and left the uniqueness that enforces it behind."""

    def test_a_claim_is_unique_within_its_lineage_not_its_device_row(self) -> None:
        body = statements(table("claims"))

        self.assertIn("unique (lineage_id, device_sequence)", body)
        self.assertIn("unique (lineage_id, payload_hash)", body)
        self.assertNotIn("unique (device_id, device_sequence)", body)
        self.assertNotIn("unique (device_id, payload_hash)", body)

    def test_a_claim_resolves_to_its_lineage(self) -> None:
        self.assertIn(
            "lineage_id uuid not null references device_lineages(lineage_id)",
            statements(table("claims")),
        )

    def test_two_receipts_at_one_head_in_one_lineage_are_unwritable(self) -> None:
        """The checkpoint-mismatch detection basis as a write refusal."""
        body = statements(table("checkpoint_receipts"))

        self.assertIn(
            "lineage_id uuid not null references device_lineages(lineage_id)", body
        )
        self.assertIn("unique (lineage_id, last_sequence)", body)

    def test_the_lineage_table_precedes_every_new_dependant(self) -> None:
        """PostgreSQL rejects a foreign key to a table declared later in the file.

        The DDL stage skips locally without a database URL, so a forward reference
        fails only in CI. It has happened here before, under `PF-009`.
        """
        text = SQL.read_text(encoding="utf-8")
        lineage = text.index("create table device_lineages (")
        for dependent in ("claims", "device_key_events", "checkpoint_receipts"):
            with self.subTest(table=dependent):
                self.assertLess(lineage, text.index(f"create table {dependent} ("))


if __name__ == "__main__":
    unittest.main()
