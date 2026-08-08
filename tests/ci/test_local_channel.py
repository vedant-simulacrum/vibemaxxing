"""A role cannot encode another role's message.

`docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md` states that role confusion is
rejected. `Envelope` carried a single universal `oneof body` holding all fifteen
bodies, and `sender_role` was a field the sender filled in — so any role could encode
any message and label itself anything. The document promised a property the wire
format made structurally impossible to have.

Each body is now reachable only through its own role's arm. What remains detectable
rather than unrepresentable has a reason code, which is the other half: before PF-012
the protocol had no vocabulary with which to refuse anything at all.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTO = ROOT / "packages" / "schemas" / "local-control-v1.proto"
REASONS = ROOT / "packages" / "schemas" / "reason-codes-v1.json"
VECTORS = ROOT / "conformance" / "local-channel" / "local-channel-vectors-v1.json"
TRUST = ROOT / "packages" / "schemas" / "local-trust-domains-v1.json"

ROLE_MESSAGES = (
    "CollectorToDaemon",
    "DaemonToCollector",
    "SyncToDaemon",
    "DaemonToSync",
    "ControlToDaemon",
    "DaemonToControl",
    "SupervisorToDaemon",
    "DaemonToSupervisor",
)


def proto() -> str:
    return PROTO.read_text(encoding="utf-8")


def arms(message: str) -> set[str]:
    body = re.search(rf"message {message} \{{(?P<body>.*?)\n\}}", proto(), re.S)
    assert body is not None, message
    return set(re.findall(r"(\w+) = \d+;", body.group("body")))


class NoUniversalUnionTests(unittest.TestCase):
    def test_the_envelope_selects_a_role_arm_not_a_body(self) -> None:
        envelope = re.search(r"message Envelope \{(?P<body>.*?)\n\}", proto(), re.S)
        assert envelope is not None

        self.assertIn("oneof role_body", envelope.group("body"))
        self.assertNotIn("oneof body", envelope.group("body"))

    def test_every_role_has_a_request_and_a_response_message(self) -> None:
        for message in ROLE_MESSAGES:
            self.assertIn(f"message {message} {{", proto(), message)

    def test_the_collector_cannot_encode_a_deletion_request(self) -> None:
        """Unrepresentable, not rejected — the point of the restructure."""
        self.assertNotIn("local_deletion_request", arms("CollectorToDaemon"))
        self.assertNotIn("local_export_request", arms("CollectorToDaemon"))

    def test_the_supervisor_holds_the_narrowest_arm(self) -> None:
        """It is the only elevated role, so it gets health and lifecycle only."""
        self.assertEqual(
            arms("SupervisorToDaemon"), {"health_request", "lifecycle_request"}
        )

    def test_sync_cannot_observe_sources_or_construct_claims(self) -> None:
        """It holds the only egress allowlist; those two must not travel with it."""
        body = arms("SyncToDaemon")

        self.assertNotIn("source_observation_submission", body)
        self.assertNotIn("claim_construction_request", body)

    def test_the_collector_cannot_read_a_queue_or_a_receipt(self) -> None:
        body = arms("CollectorToDaemon")

        self.assertNotIn("queue_summary_request", body)
        self.assertNotIn("receipt_summary_request", body)

    def test_no_two_role_arms_overlap_on_a_control_operation(self) -> None:
        """Export and deletion belong to control roles alone."""
        for message in ("CollectorToDaemon", "SyncToDaemon", "SupervisorToDaemon"):
            for operation in ("local_export_request", "local_deletion_request"):
                self.assertNotIn(operation, arms(message), message)

    def test_the_envelope_carries_a_role_grant_generation(self) -> None:
        """Without it, revocation is advisory: a survivor looks current."""
        envelope = re.search(r"message Envelope \{(?P<body>.*?)\n\}", proto(), re.S)
        assert envelope is not None

        self.assertIn("role_grant_generation", envelope.group("body"))


class ReasonCodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(REASONS.read_text(encoding="utf-8"))
        self.codes = {code["code"]: code for code in self.registry["codes"]}

    def test_the_three_channel_codes_exist(self) -> None:
        """The protocol had no vocabulary with which to refuse anything."""
        for code in (
            "IPC_ROLE_MISMATCH",
            "IPC_PEER_IDENTITY_REJECTED",
            "IPC_ROLE_GRANT_STALE",
        ):
            self.assertIn(code, self.codes)

    def test_the_local_channel_transport_is_declared(self) -> None:
        self.assertIn("local-channel", self.registry["transports"])

    def test_no_channel_code_reaches_the_wire(self) -> None:
        """A local refusal never crosses the API boundary, so it carries no status."""
        for code in self.codes.values():
            if code["transport"] == "local-channel":
                self.assertIsNone(code["http_status"], code["code"])
                self.assertFalse(code["user_safe"], code["code"])

    def test_the_channel_authority_is_declared_non_aggregate(self) -> None:
        """It is a wire format between processes, not a persisted aggregate."""
        self.assertIn("local-channel-v1", self.registry["non_aggregate_authorities"])


class VectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vectors = json.loads(VECTORS.read_text(encoding="utf-8"))
        self.cases = {case["case_id"]: case for case in self.vectors["cases"]}

    def test_a_same_user_impersonation_case_exists(self) -> None:
        case = self.cases["LC-201"]

        self.assertEqual(case["expect"], "reject")
        self.assertEqual(case["expect_reason_code"], "IPC_PEER_IDENTITY_REJECTED")
        self.assertIn("same as the daemon", case["given"]["peer_uid"])

    def test_a_stale_process_case_exists(self) -> None:
        case = self.cases["LC-202"]

        self.assertEqual(case["expect_reason_code"], "IPC_ROLE_GRANT_STALE")
        self.assertLess(
            case["given"]["role_grant_generation"],
            case["given"]["daemon_current_generation"],
        )

    def test_there_is_a_positive_case(self) -> None:
        """Four refusals are satisfied by a channel that refuses everything."""
        accepted = [c for c in self.cases.values() if c["expect"] == "accept"]

        self.assertEqual(len(accepted), 1)
        self.assertIsNone(accepted[0]["expect_reason_code"])

    def test_every_expected_code_resolves_in_the_registry(self) -> None:
        codes = {c["code"] for c in json.loads(REASONS.read_text("utf-8"))["codes"]}
        for case in self.cases.values():
            if case["expect_reason_code"]:
                self.assertIn(case["expect_reason_code"], codes, case["case_id"])


if __name__ == "__main__":
    unittest.main()
