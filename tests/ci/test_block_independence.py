"""A block changes no relationship row.

`AGENTS.md` states blocks are directional and independent from symmetric friendship
state. `SOCIAL_INTEGRITY_AND_UX_CONTRACT.md` said the opposite — blocking "removes or
disables friendship/rival relationships" and "does not automatically restore
relationships after unblock" — and both machines carried a terminal `blocked` state
with no transition out.

Friendship is keyed on an unordered pair, so it is symmetric. A directional action
reaching a terminal state on it meant one person could permanently destroy a shared
relationship, and the other party lost it through an action they could not see, take
or reverse. Unblocking could not undo it, because terminal means terminal.

These tests pin the repaired shape structurally, so the prose and the machines cannot
drift apart again.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "packages" / "schemas" / "state-machine-registry-v1.json"
SQL = ROOT / "packages" / "schemas" / "planning-schema.sql"
CONTRACT = ROOT / "docs" / "product" / "SOCIAL_INTEGRITY_AND_UX_CONTRACT.md"
AUTHORIZATION = ROOT / "packages" / "schemas" / "projection-authorization-v1.json"
VECTORS = ROOT / "conformance" / "social" / "block-independence-vectors.json"

SHARED_AGGREGATES = ("friendship", "rivalry")


def machine(identifier: str) -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return next(
        entry for entry in registry["machines"] if entry["machine_id"] == identifier
    )


class SharedAggregateTests(unittest.TestCase):
    def test_no_shared_relationship_has_a_blocked_state(self) -> None:
        """A state one party causes and neither can leave is not a lifecycle state."""
        for identifier in SHARED_AGGREGATES:
            self.assertNotIn("blocked", machine(identifier)["states"], identifier)

    def test_no_transition_blocks_a_shared_relationship(self) -> None:
        for identifier in SHARED_AGGREGATES:
            targets = {t["to"] for t in machine(identifier)["transitions"]}
            self.assertNotIn("blocked", targets, identifier)

    def test_every_state_remains_reachable_and_every_terminal_is_a_sink(self) -> None:
        """Removing a state must not strand another or leave a dangling transition."""
        for identifier in SHARED_AGGREGATES:
            entry = machine(identifier)
            reachable = {entry["initial_state"]}
            for _ in range(len(entry["states"])):
                for transition in entry["transitions"]:
                    if reachable & set(transition["from"]):
                        reachable.add(transition["to"])
            self.assertEqual(reachable, set(entry["states"]), identifier)
            for transition in entry["transitions"]:
                for state in transition["from"]:
                    self.assertNotIn(state, entry["terminal_states"], identifier)

    def test_the_sql_constraints_admit_no_blocked_state(self) -> None:
        sql = SQL.read_text(encoding="utf-8")
        for table in ("friend_requests", "rival_edges"):
            body = re.search(rf"create table {table} \((?P<body>.*?)\n\);", sql, re.S)
            assert body is not None, table
            constraint = re.search(
                r"state text not null check \(state in \(([^)]*)\)", body.group("body")
            )
            assert constraint is not None, table
            self.assertNotIn("blocked", constraint.group(1), table)


class BlockRemainsDirectionalTests(unittest.TestCase):
    def test_blocks_carry_no_symmetry_constraint(self) -> None:
        """The friendship table has `check (a < b)`; the block table must not."""
        sql = SQL.read_text(encoding="utf-8")
        blocks = re.search(r"create table blocks \((?P<body>.*?)\n\);", sql, re.S)
        friends = re.search(
            r"create table friend_edges \((?P<body>.*?)\n\);", sql, re.S
        )
        assert blocks is not None and friends is not None

        self.assertIn("<", friends.group("body"))
        self.assertNotIn(
            "account_id_a", blocks.group("body"), "blocks must not be a canonical pair"
        )

    def test_the_authorization_profile_owns_the_block_effect(self) -> None:
        """Where the effect lives now: read time, both directions, deny-hard."""
        profile = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
        block = next(
            entry
            for entry in profile["inputs"]
            if entry["input_id"] == "directional-block"
        )

        self.assertEqual(block["effect"], "deny-hard")
        self.assertEqual(block["persistence_owner"], "blocks")


class ContractProseTests(unittest.TestCase):
    def test_the_contract_no_longer_says_blocking_removes_relationships(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")

        self.assertNotIn("removes or disables friendship/rival relationships", text)
        self.assertIn("Blocking changes no relationship row", text)


class VectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vectors = json.loads(VECTORS.read_text(encoding="utf-8"))

    def test_no_case_deletes_a_relationship_row_on_a_block(self) -> None:
        """The property the whole unit exists to state, read off the vectors."""
        for case in self.vectors["cases"]:
            if case["action"]["operation"] != "createBlock":
                continue
            given = case["given"]
            expected = case["expected_rows"]
            for table in ("friend_edges", "rival_edges"):
                if table in given:
                    self.assertEqual(given[table], expected.get(table), case["case_id"])

    def test_a_surviving_block_still_denies_both_directions(self) -> None:
        """SO-105: the case a symmetric boolean gets wrong."""
        case = next(c for c in self.vectors["cases"] if c["case_id"] == "SO-105")

        self.assertEqual(len(case["expected_rows"]["blocks"]), 1)
        self.assertEqual(case["expected_visibility"]["a_sees_b"], "denied")
        self.assertEqual(case["expected_visibility"]["b_sees_a"], "denied")

    def test_unblocking_restores_visibility(self) -> None:
        case = next(c for c in self.vectors["cases"] if c["case_id"] == "SO-102")

        self.assertEqual(case["expected_rows"]["blocks"], [])
        self.assertEqual(case["expected_visibility"]["a_sees_b"], "allowed")
        self.assertEqual(case["expected_visibility"]["b_sees_a"], "allowed")


if __name__ == "__main__":
    unittest.main()
