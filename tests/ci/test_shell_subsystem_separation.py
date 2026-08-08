"""One state variable cannot hold six independent facts.

`interactive-shell` carried fifteen states covering six subsystems: collection was
`paused`, connectivity was `offline` and `degraded`, authentication was
`auth-required`, updates were `update-required` and `update-blocked`, and permissions
were `permission-repair`.

A device whose collection is paused *and* whose network is offline had no
representable shell state. The transition table had to pretend one of the two had not
happened, which is not a modelling nicety: it is a state the product can reach and the
contract could not describe.
"""

from __future__ import annotations

import json
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "packages" / "schemas" / "state-machine-registry-v1.json"
LOCAL_STORE = ROOT / "packages" / "schemas" / "local-store-v1.sql"
SERVER = ROOT / "packages" / "schemas" / "planning-schema.sql"

PROCESS_STATES = {
    "absent",
    "headless",
    "starting",
    "connected",
    "daemon-unavailable",
    "stale",
    "exiting",
    "crashed",
}
MOVED = {
    "paused",
    "offline",
    "degraded",
    "auth-required",
    "update-required",
    "update-blocked",
    "permission-repair",
}
PROJECTIONS = (
    "local-collection",
    "local-sync",
    "local-auth",
    "local-permission",
    "local-connectivity",
)


def machines() -> dict[str, dict]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {m["machine_id"]: m for m in registry["machines"]}


class ShellOwnsProcessStateOnlyTests(unittest.TestCase):
    def test_the_shell_declares_only_process_and_connection_states(self) -> None:
        self.assertEqual(set(machines()["interactive-shell"]["states"]), PROCESS_STATES)

    def test_no_subsystem_state_remains_on_the_shell(self) -> None:
        shell = machines()["interactive-shell"]
        self.assertEqual(set(shell["states"]) & MOVED, set())
        for transition in shell["transitions"]:
            self.assertNotIn(transition["to"], MOVED)
            self.assertEqual(set(transition["from"]) & MOVED, set())

    def test_the_server_check_constraint_matches(self) -> None:
        body = re.search(
            r"create table shell_sessions \((?P<body>.*?)\n\);",
            SERVER.read_text(encoding="utf-8"),
            re.S,
        )
        assert body is not None
        constraint = re.search(
            r"state text not null check \(state in \(([^)]*)\)", body.group("body")
        )
        assert constraint is not None
        declared = {v.strip().strip("'") for v in constraint.group(1).split(",")}

        self.assertEqual(declared, PROCESS_STATES)


class ProjectionsAreIndependentTests(unittest.TestCase):
    def test_all_five_projections_exist(self) -> None:
        registry = machines()
        for name in PROJECTIONS:
            self.assertIn(name, registry)

    def test_each_projection_is_device_local_and_publishes_nothing(self) -> None:
        registry = machines()
        for name in PROJECTIONS:
            machine = registry[name]
            self.assertEqual(machine["privacy_boundary"], "local-only", name)
            self.assertEqual(machine["transaction_boundary"], "device-local", name)
            self.assertEqual(machine["outbox"], "none", name)

    def test_projections_persist_on_the_device_not_the_server(self) -> None:
        """None of them is aggregate accounting or an integrity claim."""
        local = set(re.findall(r"create table (\w+)", LOCAL_STORE.read_text("utf-8")))
        server = set(re.findall(r"create table (\w+)", SERVER.read_text("utf-8")))
        registry = machines()
        for name in PROJECTIONS:
            for owner in registry[name]["persistence_owner"]:
                table = owner.replace("-", "_")
                self.assertIn(table, local, name)
                self.assertNotIn(table, server, name)

    def test_every_projection_state_is_reachable(self) -> None:
        registry = machines()
        for name in PROJECTIONS:
            machine = registry[name]
            reachable = {machine["initial_state"]}
            for _ in range(len(machine["states"])):
                for transition in machine["transitions"]:
                    if reachable & set(transition["from"]):
                        reachable.add(transition["to"])
            self.assertEqual(reachable, set(machine["states"]), name)

    def test_the_combination_that_was_unrepresentable_now_is(self) -> None:
        """Paused collection and an offline network, at the same time."""
        connection = sqlite3.connect(":memory:")
        connection.executescript(LOCAL_STORE.read_text(encoding="utf-8"))
        connection.execute(
            "insert into local_collection_state values (1, 'paused', '2026-08-09')"
        )
        connection.execute(
            "insert into local_connectivity_state values (1, 'offline', '2026-08-09')"
        )

        self.assertEqual(
            connection.execute("select state from local_collection_state").fetchone()[0],
            "paused",
        )
        self.assertEqual(
            connection.execute(
                "select state from local_connectivity_state"
            ).fetchone()[0],
            "offline",
        )


if __name__ == "__main__":
    unittest.main()
