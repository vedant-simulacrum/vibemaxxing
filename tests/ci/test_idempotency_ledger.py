"""The idempotency ledger keys on everything its contract says it keys on.

`openapi-v1.yaml#x-idempotency-contract` declared
`key_scope: [principal_id, operation_id, idempotency_key]`, and
`planning-schema.sql` keyed `idempotency_records` on
`(actor_account_id, idempotency_key)`. `operation_id` was a column sitting outside
the key.

The spurious 409 is the harmless half. A committed row stores the exact response for
byte-identical replay, so one key reused across two operations could be answered with
the *other* operation's recorded body — a client asking to delete something could be
handed the recorded success of an unrelated write.

`principal_type` was missing for the same reason: the contract's principal is the
account for a web session and the bound device enrollment for a native one, so a web
and a native session for one account were two principals in the contract and one row
in the table.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "packages" / "schemas" / "planning-schema.sql"
OPENAPI = ROOT / "packages" / "schemas" / "openapi-v1.yaml"
REGISTRY = ROOT / "packages" / "schemas" / "state-machine-registry-v1.json"

TABLE = re.compile(r"create table idempotency_records \((?P<body>.*?)\n\);", re.S)


def table_body() -> str:
    found = TABLE.search(SQL.read_text(encoding="utf-8"))
    assert found is not None, "idempotency_records not found"
    return found.group("body")


def ledger() -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return next(
        machine
        for machine in registry["machines"]
        if machine["machine_id"] == "idempotency-ledger"
    )


class KeyScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))[
            "x-idempotency-contract"
        ]

    def test_the_primary_key_is_exactly_the_declared_key_scope(self) -> None:
        """The defect: operation_id was declared in scope and outside the key."""
        found = re.search(r"primary key \(([^)]*)\)", table_body())
        assert found is not None
        columns = [column.strip() for column in found.group(1).split(",")]

        self.assertEqual(columns, self.contract["key_scope"])

    def test_operation_id_is_in_the_key(self) -> None:
        """Stated on its own because this is the replay-the-wrong-response bug."""
        found = re.search(r"primary key \(([^)]*)\)", table_body())
        assert found is not None

        self.assertIn("operation_id", found.group(1))

    def test_principal_type_distinguishes_the_two_principals(self) -> None:
        body = table_body()

        self.assertIn("principal_type", body)
        self.assertIn("'account'", body)
        self.assertIn("'device'", body)

    def test_principal_id_carries_no_foreign_key(self) -> None:
        """It addresses `accounts` or `devices`; a reference could name only one."""
        principal = next(
            line for line in table_body().splitlines() if "principal_id" in line
        )

        self.assertNotIn("references", principal)


class LedgerStateTests(unittest.TestCase):
    EXPECTED = (
        "executing",
        "committed",
        "replayable-failure",
        "conflict",
        "expired",
        "abandoned",
    )

    def test_the_sql_and_the_registry_declare_the_same_states(self) -> None:
        found = re.search(
            r"state text not null check \(state in \(([^)]*)\)", table_body()
        )
        assert found is not None
        sql_states = tuple(
            value.strip().strip("'") for value in found.group(1).split(",")
        )

        self.assertEqual(sql_states, self.EXPECTED)
        self.assertEqual(tuple(ledger()["states"]), self.EXPECTED)

    def test_a_run_that_failed_is_distinct_from_one_that_never_ran(self) -> None:
        """`replayable-failure` records that it ran; `abandoned` that it did not.

        Collapsing them, as the single `failed` state did, means a retry cannot know
        whether the first attempt had an effect.
        """
        states = set(ledger()["states"])

        self.assertIn("replayable-failure", states)
        self.assertIn("abandoned", states)
        self.assertNotIn("failed", states)

    def test_committed_is_not_terminal_because_it_expires(self) -> None:
        machine = ledger()

        self.assertNotIn("committed", machine["terminal_states"])
        self.assertTrue(
            any(
                "committed" in transition["from"] and transition["to"] == "expired"
                for transition in machine["transitions"]
            )
        )

    def test_every_state_is_reachable_from_the_initial_state(self) -> None:
        machine = ledger()
        reachable = {machine["initial_state"]}
        for _ in range(len(machine["states"])):
            for transition in machine["transitions"]:
                if reachable & set(transition["from"]):
                    reachable.add(transition["to"])

        self.assertEqual(reachable, set(machine["states"]))


if __name__ == "__main__":
    unittest.main()
