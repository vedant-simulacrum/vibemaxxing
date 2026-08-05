from __future__ import annotations

import importlib.util
import io
import json
import contextlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_state_vocabularies.py"

REGISTRY = ROOT / "packages" / "schemas" / "state-machine-registry-v1.json"
SQL = ROOT / "packages" / "schemas" / "planning-schema.sql"
OPENAPI = ROOT / "packages" / "schemas" / "openapi-v1.yaml"
CONTRACT = (
    ROOT / "docs" / "architecture" / "AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md"
)


def load_validator() -> object:
    specification = importlib.util.spec_from_file_location(
        "validate_state_vocabularies", VALIDATOR
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class StateVocabularyValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.directory = Path(tempfile.mkdtemp(prefix="state-vocab-"))
        self.addCleanup(shutil.rmtree, self.directory, True)
        self.copies = {}
        for attribute, source in (
            ("REGISTRY_PATH", REGISTRY),
            ("SQL_PATH", SQL),
            ("OPENAPI_PATH", OPENAPI),
            ("CONTRACT_PATH", CONTRACT),
        ):
            target = self.directory / source.name
            shutil.copyfile(source, target)
            self.copies[attribute] = target

    def run_validator(self) -> tuple[int, str]:
        stderr = io.StringIO()
        stdout = io.StringIO()
        with contextlib.ExitStack() as stack:
            for attribute, target in self.copies.items():
                stack.enter_context(patch.object(self.validator, attribute, target))
            stack.enter_context(contextlib.redirect_stderr(stderr))
            stack.enter_context(contextlib.redirect_stdout(stdout))
            code = self.validator.main()
        return code, stderr.getvalue() + stdout.getvalue()

    def edit_registry(self, mutate) -> None:
        path = self.copies["REGISTRY_PATH"]
        registry = json.loads(path.read_text(encoding="utf-8"))
        mutate({machine["machine_id"]: machine for machine in registry["machines"]})
        path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    def edit_openapi(self, mutate) -> None:
        path = self.copies["OPENAPI_PATH"]
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        mutate(spec["components"]["schemas"])
        path.write_text(
            yaml.safe_dump(spec, sort_keys=False, width=4096), encoding="utf-8"
        )

    def edit_sql(self, old: str, new: str) -> None:
        path = self.copies["SQL_PATH"]
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1, old)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def edit_contract(self, old: str, new: str) -> None:
        path = self.copies["CONTRACT_PATH"]
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1, old)
        path.write_text(text.replace(old, new), encoding="utf-8")

    # -- the repository as committed -------------------------------------------------

    def test_repository_state_vocabularies_agree(self) -> None:
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)
        self.assertIn("state vocabulary validation: PASS", output)

    def test_every_registry_machine_is_bound(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        machine_ids = {machine["machine_id"] for machine in registry["machines"]}
        bound = {
            binding.machine for binding in self.validator.BINDINGS if binding.machine
        }
        self.assertEqual(bound, machine_ids)

    def test_notification_retraction_is_persistable_and_visible(self) -> None:
        binding = {b.aggregate: b for b in self.validator.BINDINGS}[
            "notification-delivery"
        ]
        self.assertIn("retracted", binding.states)
        self.assertNotIn("retracted", binding.internal_states)

    def test_replay_detection_is_persistable(self) -> None:
        bodies = self.validator.table_bodies(SQL.read_text(encoding="utf-8"))
        checks = self.validator.sql_check_sets(bodies)
        self.assertIn("replay-detected", checks["session_families.state"])

    def test_ranking_projection_worker_has_a_target_state(self) -> None:
        bodies = self.validator.table_bodies(SQL.read_text(encoding="utf-8"))
        checks = self.validator.sql_check_sets(bodies)
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        machine = {m["machine_id"]: m for m in registry["machines"]}[
            "ranking-projection"
        ]
        self.assertEqual(
            checks["ranking_projection_generations.state"], set(machine["states"])
        )

    def test_account_and_device_lifecycles_have_machines(self) -> None:
        bindings = {b.aggregate: b for b in self.validator.BINDINGS}
        self.assertEqual(bindings["account-lifecycle"].machine, "account-lifecycle")
        self.assertEqual(bindings["device-enrollment"].machine, "device-enrollment")

    def test_restriction_and_quarantine_are_restorable(self) -> None:
        # ANTI_CHEAT_ATTACK_CATALOG.md:87 requires restoration semantics for every
        # restriction, quarantine and revocation.
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        machines = {m["machine_id"]: m for m in registry["machines"]}
        for machine_id, source, target in (
            ("account-lifecycle", "restricted", "active"),
            ("device-enrollment", "quarantined", "active"),
        ):
            restorations = [
                t
                for t in machines[machine_id]["transitions"]
                if t["to"] == target and source in t["from"]
            ]
            self.assertEqual(len(restorations), 1, machine_id)
            self.assertTrue(restorations[0]["recent_auth"], machine_id)
            self.assertEqual(restorations[0]["actor"], "moderator", machine_id)

    def test_every_bound_machine_state_is_reachable(self) -> None:
        # A state no transition can reach is a vocabulary the three sources agree on
        # but no worker can ever produce. Scoped to machines this unit binds to SQL
        # or an API enum; the native runtime and shell machines are not yet complete.
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        machines = {m["machine_id"]: m for m in registry["machines"]}
        bound = {
            b.machine for b in self.validator.BINDINGS if b.machine and (b.sql or b.api)
        }
        for machine_id in sorted(bound):
            machine = machines[machine_id]
            reachable = {machine["initial_state"]}
            changed = True
            while changed:
                changed = False
                for transition in machine["transitions"]:
                    if (
                        set(transition["from"]) & reachable
                        and transition["to"] not in reachable
                    ):
                        reachable.add(transition["to"])
                        changed = True
            self.assertEqual(
                set(machine["states"]) - reachable, set(), f"{machine_id} unreachable"
            )

    def test_appeal_outcome_is_published_and_matches_persistence(self) -> None:
        spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
        appeal = spec["components"]["schemas"]["Appeal"]
        self.assertIn("decision", appeal["properties"])
        self.assertNotIn("decision", appeal["required"])
        bodies = self.validator.table_bodies(SQL.read_text(encoding="utf-8"))
        checks = self.validator.sql_check_sets(bodies)
        self.assertEqual(
            set(appeal["properties"]["decision"]["enum"]),
            checks["appeal_decisions.decision"],
        )
        # The outcome must not leak back into the lifecycle vocabulary.
        self.assertFalse(
            set(appeal["properties"]["decision"]["enum"])
            & set(appeal["properties"]["state"]["enum"])
        )

    # -- fail-closed behaviour -------------------------------------------------------

    def test_outcome_mirror_drift_fails(self) -> None:
        self.edit_openapi(
            lambda schemas: schemas["Appeal"]["properties"]["decision"]["enum"].remove(
                "partially-upheld"
            )
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("outcome enum Appeal.decision differs", output)

    def test_registry_state_drift_fails(self) -> None:
        self.edit_registry(
            lambda machines: machines["appeal"]["states"].append("mediating")
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("registry states differ", output)

    def test_sql_check_drift_fails(self) -> None:
        self.edit_sql(
            "'created','grouped','ready','delivered','read','suppressed','retracted','expired'",
            "'created','grouped','ready','delivered','read','suppressed','expired'",
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("SQL CHECK on notifications.state differs", output)

    def test_api_enum_drift_fails(self) -> None:
        self.edit_openapi(
            lambda schemas: schemas["ExportJob"]["properties"]["state"]["enum"].append(
                "queued"
            )
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("API enum ExportJob.state differs", output)

    def test_undeclared_internal_state_fails(self) -> None:
        self.edit_openapi(
            lambda schemas: schemas["ExportJob"]["properties"]["state"].__setitem__(
                "enum", ["requested", "ready", "downloaded", "purged", "failed"]
            )
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("only-in-binding=['encrypting', 'snapshotting']", output)

    def test_snake_case_state_value_fails(self) -> None:
        self.edit_sql("'invalidated-by-block'", "'invalidated_by_block'")
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("not lowercase kebab-case", output)

    def test_unbound_sql_state_column_fails(self) -> None:
        self.edit_sql(
            "create table schema_migrations (\n  version text primary key,",
            "create table schema_migrations (\n  version text primary key,\n"
            "  state text not null check (state in ('applied')),",
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("bound to no aggregate and declares no local vocabulary", output)

    def test_unbound_api_state_enum_fails(self) -> None:
        self.edit_openapi(
            lambda schemas: schemas["ExportRequest"]["properties"].__setitem__(
                "lifecycle_state", {"enum": ["fresh", "stale"]}
            )
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("API state enum is bound to no aggregate", output)

    def test_shared_session_family_column_must_be_the_union(self) -> None:
        self.edit_sql(
            "'active','rotating','replay-detected','revoked','device-revoked','expired'",
            "'active','rotating','replay-detected','revoked','device-revoked','expired','stale'",
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("is not the union of its machines", output)

    def test_contract_document_drift_fails(self) -> None:
        self.edit_contract(
            "| `appeal` | `appeal` | `appeals.state` | `Appeal.state` | `screening` |",
            "| `appeal` | `appeal` | `appeals.state` | `Appeal.state` | — |",
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("documented internal states", output)

    def test_missing_contract_table_fails(self) -> None:
        path = self.copies["CONTRACT_PATH"]
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace("| Aggregate | Registry machine |", "| Aggregate | Machine |"),
            encoding="utf-8",
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("no state vocabulary binding table", output)

    def test_projection_must_cover_every_machine_state(self) -> None:
        with patch.object(
            self.validator,
            "PROJECTIONS",
            (
                (
                    "presence-lease",
                    ("PresenceLease.availability",),
                    {"absent": "offline"},
                ),
            ),
        ):
            code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("does not cover every state", output)


if __name__ == "__main__":
    unittest.main()
