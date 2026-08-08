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


class ValidatorFixture:
    """Shared setup only. Carries no tests, so inheriting it does not re-run them."""

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


class ConcurrencyModelTests(ValidatorFixture, unittest.TestCase):
    """PF-004. Every rule here is a consequence of one SQL constraint.

    `outbox_events` carries `unique (aggregate_id, aggregate_revision)`. An aggregate
    can only publish if it has a revision to publish under, and only once per revision.
    Before PF-004 the registry declared none of this: thirty-two aggregates named a
    persistence owner and said nothing about how a concurrent write to it is ordered,
    what commits alongside it, or whether anything downstream could observe it.
    """

    def test_publishing_without_a_revision_fails(self) -> None:
        """`single-writer` has no server revision for the unique constraint to key on."""
        self.edit_registry(
            lambda machines: machines["friendship"].update(
                revision_model="single-writer"
            )
        )

        code, output = self.run_validator()

        self.assertEqual(code, 1, output)
        self.assertIn("carries no revision", output)

    def test_publishing_outside_the_aggregate_transaction_fails(self) -> None:
        """An outbox row written in a second transaction is the lost-event bug."""
        self.edit_registry(
            lambda machines: machines["friendship"].update(
                transaction_boundary="aggregate-local"
            )
        )

        code, output = self.run_validator()

        self.assertEqual(code, 1, output)
        self.assertIn("lost exactly when the write succeeds", output)

    def test_a_device_local_aggregate_cannot_publish(self) -> None:
        self.edit_registry(
            lambda machines: machines["daemon-lifecycle"].update(outbox="required")
        )

        code, output = self.run_validator()

        self.assertEqual(code, 1, output)
        self.assertIn("no server transaction to publish inside", output)

    def test_a_local_only_aggregate_in_a_server_transaction_fails(self) -> None:
        """A privacy-boundary violation stated as a persistence choice."""
        self.edit_registry(
            lambda machines: machines["interactive-shell"].update(
                transaction_boundary="aggregate-local"
            )
        )

        code, output = self.run_validator()

        self.assertEqual(code, 1, output)
        self.assertIn("privacy-boundary violation", output)

    def test_every_machine_declares_all_three_fields(self) -> None:
        """The committed registry holds the property, so absence is a regression."""
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for machine in registry["machines"]:
            for field in ("revision_model", "transaction_boundary", "outbox"):
                self.assertIn(field, machine, machine["machine_id"])

    def test_every_publisher_has_a_revision_and_the_right_boundary(self) -> None:
        """States the invariant over the committed data, not just the checker."""
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        publishers = [m for m in registry["machines"] if m["outbox"] == "required"]
        self.assertTrue(publishers)
        for machine in publishers:
            self.assertNotEqual(
                machine["revision_model"], "single-writer", machine["machine_id"]
            )
            self.assertEqual(
                machine["transaction_boundary"],
                "aggregate-and-outbox",
                machine["machine_id"],
            )


class RecordedAbsenceCoverageTests(ValidatorFixture, unittest.TestCase):
    """PF-067. `check_absence_reasons` is what stops a `sql=()` aggregate from being

    silently counted as covered again: every axis an aggregate does not bind must
    carry a reason in `RECORDED_ABSENCES`, that reason must vanish the moment the
    axis is populated, and the reason table mirrored into
    `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` must agree with it in both
    directions and on the text. These drive `check_absence_reasons` directly with a
    synthetic contract string rather than editing the real document, because the
    check under test is the comparison logic itself, not file parsing.
    """

    def test_absence_with_no_recorded_reason_fails(self) -> None:
        report = self.validator.Report()
        contract_text = CONTRACT.read_text(encoding="utf-8")
        absences = dict(self.validator.RECORDED_ABSENCES)
        del absences[("local-collection", "api")]

        with patch.object(self.validator, "RECORDED_ABSENCES", absences):
            self.validator.check_absence_reasons(report, contract_text)

        self.assertTrue(
            any(
                "local-collection: binds no api and records no reason" in error
                for error in report.errors
            ),
            report.errors,
        )

    def test_reason_for_populated_binding_fails(self) -> None:
        """The check that would have caught the real defect: PF-013 left the five

        `local-*` bindings at `sql=()` while `local-store-v1.sql` defined the
        tables they name, so a reason recorded against a binding that is actually
        populated must fail loudly rather than sit there looking like coverage.
        `oauth-transaction` binds `sql`, so recording an absence reason for its
        `sql` axis is the bogus case.
        """
        report = self.validator.Report()
        contract_text = CONTRACT.read_text(encoding="utf-8")
        absences = dict(self.validator.RECORDED_ABSENCES)
        absences[("oauth-transaction", "sql")] = (
            "bogus reason for a binding that is actually populated"
        )

        with patch.object(self.validator, "RECORDED_ABSENCES", absences):
            self.validator.check_absence_reasons(report, contract_text)

        self.assertTrue(
            any(
                "oauth-transaction: records a reason for an absent sql binding" in error
                and "the reason has outlived the gap it excused" in error
                for error in report.errors
            ),
            report.errors,
        )

    def test_absence_table_document_only_row_fails_mismatch(self) -> None:
        contract_text = CONTRACT.read_text(encoding="utf-8")
        marker = "| Aggregate | Absent binding | Reason |\n|---|---|---|\n"
        self.assertEqual(contract_text.count(marker), 1)
        extra_row = (
            "| `fake-aggregate` | `sql` | Manufactured absence for a drift test. |\n"
        )
        mutated = contract_text.replace(marker, marker + extra_row)

        report = self.validator.Report()
        self.validator.check_absence_reasons(report, mutated)

        self.assertTrue(
            any(
                "recorded-absence table mismatch" in error
                and "only-in-document" in error
                and "fake-aggregate" in error
                for error in report.errors
            ),
            report.errors,
        )

    def test_absence_table_validator_only_entry_fails_mismatch(self) -> None:
        contract_text = CONTRACT.read_text(encoding="utf-8")
        row = (
            "| `oauth-transaction` | `api` | OAuthCompletion.state echoes the "
            "terminal value only; see TRANSIENT_API_ENUMS. |\n"
        )
        self.assertEqual(contract_text.count(row), 1)
        mutated = contract_text.replace(row, "")

        report = self.validator.Report()
        self.validator.check_absence_reasons(report, mutated)

        self.assertTrue(
            any(
                "recorded-absence table mismatch" in error
                and "only-in-validator" in error
                and "oauth-transaction" in error
                for error in report.errors
            ),
            report.errors,
        )

    def test_absence_reason_text_drift_fails(self) -> None:
        contract_text = CONTRACT.read_text(encoding="utf-8")
        row = (
            "| `oauth-transaction` | `api` | OAuthCompletion.state echoes the "
            "terminal value only; see TRANSIENT_API_ENUMS. |\n"
        )
        self.assertEqual(contract_text.count(row), 1)
        drifted_row = (
            "| `oauth-transaction` | `api` | A drifted reason that does not "
            "match the validator's text. |\n"
        )
        mutated = contract_text.replace(row, drifted_row)

        report = self.validator.Report()
        self.validator.check_absence_reasons(report, mutated)

        self.assertTrue(
            any(
                "oauth-transaction" in error
                and "absent api binding" in error
                and "differs from the validator's" in error
                for error in report.errors
            ),
            report.errors,
        )

    def test_missing_absence_table_raises_failure(self) -> None:
        report = self.validator.Report()
        contract_text = "# Doc\n\nNo such table anywhere in this document.\n"

        with self.assertRaises(self.validator.Failure) as context:
            self.validator.check_absence_reasons(report, contract_text)

        self.assertIn("contains no recorded-absence table", str(context.exception))

    def test_local_aggregates_are_wired_to_sql(self) -> None:
        """PF-013 created `local_collection_state` etc. in `local-store-v1.sql`, but

        the five `local-*` bindings sat at `sql=()`. `coverage()` counted an
        aggregate as covered whether it was compared against three owners or
        none, so those five were reported as covered while compared against
        nothing. This asserts directly against the committed `BINDINGS`, not
        through the validator's report, so it fails on the exact regression
        rather than on any incidental message text.
        """
        bindings = {binding.aggregate: binding for binding in self.validator.BINDINGS}
        expected_columns = {
            "local-collection": "local_collection_state.state",
            "local-sync": "local_sync_state.state",
            "local-auth": "local_auth_state.state",
            "local-permission": "local_permission_state.state",
            "local-connectivity": "local_connectivity_state.state",
        }
        for aggregate, column in expected_columns.items():
            binding = bindings[aggregate]
            self.assertEqual(
                binding.sql,
                (column,),
                f"{aggregate}: PF-013 created {column.split('.')[0]} but the "
                f"binding's sql tuple is {binding.sql!r}; an aggregate counted as "
                "covered while compared against nothing is exactly the PF-013 "
                "defect PF-067 exists to catch",
            )

    def test_unbound_local_store_column_fails_rule_8(self) -> None:
        """Rule 8 must fail closed on the device half of the storage contract too.

        Before PF-067, `local_store_tables()` read `local-store-v1.sql` for table
        names only, so a state column declared there and bound to nothing could
        not be detected. This injects one into `local_meta`, a table no binding
        or sub-entity vocabulary names, and points the validator's `SCHEMAS`
        constant at a temporary copy so the real schema tree is never touched.
        """
        local_store_path = ROOT / "packages" / "schemas" / "local-store-v1.sql"
        text = local_store_path.read_text(encoding="utf-8")
        old = (
            "create table local_meta (\n"
            "  singleton integer primary key check (singleton = 1),"
        )
        new = old + "\n  state text not null check (state in ('applied')),"
        self.assertEqual(text.count(old), 1)
        mutated = text.replace(old, new)

        schema_dir = self.directory / "local_schema"
        schema_dir.mkdir()
        (schema_dir / "local-store-v1.sql").write_text(mutated, encoding="utf-8")

        with patch.object(self.validator, "SCHEMAS", schema_dir):
            code, output = self.run_validator()

        self.assertEqual(code, 1, output)
        self.assertIn(
            "bound to no aggregate and declares no local vocabulary: local_meta.state",
            output,
        )
