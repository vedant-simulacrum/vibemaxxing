"""The retention registry must cover the schema and the erasure invariants must hold.

PF-050's defect was that retention lived in prose and `expires_at` columns were
enforced by nobody, and D-210 rests on check constraints rather than on worker
discipline. Both are only worth anything if drift is caught, so these tests mutate
the artifacts and assert the validator notices.

They prove the validator works. They do not prove any sweeper exists, that any key
has been destroyed, or that any restore has been drilled. None of those exist.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
SCHEMAS = ROOT / "packages" / "schemas"


def load_validator() -> object:
    specification = importlib.util.spec_from_file_location(
        "validate_planning_artifacts", VALIDATOR
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class DispositionAndErasureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()

    def _schemas_copy(self) -> Path:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory, True)
        copy = directory / "schemas"
        shutil.copytree(SCHEMAS, copy)
        return copy

    def _run_with(self, copy: Path, check) -> None:
        with patch.object(self.validator, "SCHEMAS", copy):
            check()

    # -- head state ---------------------------------------------------------

    def test_repository_head_passes(self) -> None:
        self.validator.validate_data_disposition()
        self.validator.validate_erasure_contract()

    def test_every_planning_table_has_a_disposition_row(self) -> None:
        tables = set(self.validator._planning_table_bodies())
        registry = json.loads(
            (SCHEMAS / "data-disposition-v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(tables, {entry["table"] for entry in registry["entries"]})

    # -- disposition coverage ----------------------------------------------

    def test_a_table_without_a_disposition_row_fails(self) -> None:
        copy = self._schemas_copy()
        path = copy / "data-disposition-v1.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["entries"] = [
            entry for entry in registry["entries"] if entry["table"] != "accounts"
        ]
        path.write_text(json.dumps(registry), encoding="utf-8")
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(copy, self.validator.validate_data_disposition)
        self.assertIn("accounts", str(raised.exception))

    def test_an_unresolvable_policy_key_fails(self) -> None:
        copy = self._schemas_copy()
        path = copy / "data-disposition-v1.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        for entry in registry["entries"]:
            if entry["table"] == "notifications":
                entry["retention"] = {"policy_key": "notification_retention_weeks"}
        path.write_text(json.dumps(registry), encoding="utf-8")
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(copy, self.validator.validate_data_disposition)
        self.assertIn("notification_retention_weeks", str(raised.exception))

    def test_an_expires_at_column_without_an_actor_fails(self) -> None:
        copy = self._schemas_copy()
        path = copy / "data-disposition-v1.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        for entry in registry["entries"]:
            if entry["table"] == "presence_leases":
                entry.pop("expiry_enforcement")
        path.write_text(json.dumps(registry), encoding="utf-8")
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(copy, self.validator.validate_data_disposition)
        self.assertIn("presence_leases", str(raised.exception))

    def test_journal_retention_must_be_one_day_beyond_the_backup_window(self) -> None:
        copy = self._schemas_copy()
        path = copy / "policy-defaults-v1.json"
        policies = json.loads(path.read_text(encoding="utf-8"))
        policies["policies"]["erasure_journal_retention_days"]["value"] = 60
        path.write_text(json.dumps(policies), encoding="utf-8")
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(copy, self.validator.validate_data_disposition)
        self.assertIn("exactly one day longer", str(raised.exception))

    def test_head_journal_window_is_one_day_beyond_the_backup_window(self) -> None:
        policies = json.loads(
            (SCHEMAS / "policy-defaults-v1.json").read_text(encoding="utf-8")
        )["policies"]
        self.assertEqual(
            policies["erasure_journal_retention_days"]["value"],
            policies["backup_retention_days"]["value"] + 1,
        )

    # -- inventory table integrity ------------------------------------------

    def test_a_duplicated_specification_family_fails(self) -> None:
        """The defect a rebase introduced twice, found by hand both times.

        The decision register grew a duplicate-id check after the same thing
        happened there. The inventory had none, so a replayed rebase duplicated
        a family four times and left a stale `planned-missing` row beside the
        current one that superseded it. The completeness count is read off this
        table, so a duplicate makes that count wrong.
        """
        inventory = ROOT / "docs" / "planning" / "SCHEMA_AND_INTERFACE_INVENTORY.md"
        original = inventory.read_text(encoding="utf-8")
        row = next(
            line
            for line in original.split("\n")
            if line.startswith("| Conformance harness |")
        )
        # The file has no trailing newline, so a bare append would concatenate
        # the row onto the last line and the check would never see it.
        inventory.write_text(original + "\n" + row + "\n", encoding="utf-8")
        try:
            with self.assertRaises(self.validator.ValidationFailure) as raised:
                self.validator.validate_inventory_register()
        finally:
            inventory.write_text(original, encoding="utf-8")
        self.assertIn("repeats the specification family", str(raised.exception))

    def test_an_undeclared_inventory_status_fails(self) -> None:
        """The vocabulary is read from the document's own definition list.

        Hard-coding it here would let the two drift apart, which is the defect
        rather than the check.
        """
        inventory = ROOT / "docs" / "planning" / "SCHEMA_AND_INTERFACE_INVENTORY.md"
        original = inventory.read_text(encoding="utf-8")
        inventory.write_text(
            original.replace("| present-provisional | D-441", "| done | D-441", 1),
            encoding="utf-8",
        )
        try:
            with self.assertRaises(self.validator.ValidationFailure) as raised:
                self.validator.validate_inventory_register()
        finally:
            inventory.write_text(original, encoding="utf-8")
        self.assertIn("not one of", str(raised.exception))

    # -- erasure invariants -------------------------------------------------

    def test_a_nullable_reference_into_an_erased_table_fails(self) -> None:
        """The gap that hid three of nine violations.

        The rule originally matched `not null references`, so a nullable
        reference with no ON DELETE action passed — even though PostgreSQL
        refuses the parent delete for those exactly as hard. Nullability
        decides whether a row may omit the reference, not whether the
        referenced row may be deleted.
        """
        copy = self._schemas_copy()
        path = copy / "planning-schema.sql"
        sql = path.read_text(encoding="utf-8")
        path.write_text(
            sql.replace(
                "  -- Deliberately not a foreign key: the case survives erasure "
                "unlinked; a nullable reference still blocks the delete.\n"
                "  account_id uuid,",
                "  account_id uuid references accounts(account_id),",
            ),
            encoding="utf-8",
        )
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(
                copy, self.validator.validate_notification_and_local_deletion_contracts
            )
        message = str(raised.exception)
        self.assertIn("moderation_cases.account_id", message)
        self.assertIn("cannot commit", message)

    def test_an_explicit_on_delete_action_is_accepted(self) -> None:
        """The rule is about whether the parent delete can proceed, nothing else.

        ON DELETE SET NULL and ON DELETE CASCADE both let it proceed, so a
        reference carrying one is not a violation and must not be reported as
        though dropping the reference were the only repair.
        """
        copy = self._schemas_copy()
        path = copy / "planning-schema.sql"
        sql = path.read_text(encoding="utf-8")
        path.write_text(
            sql.replace(
                "  -- Deliberately not a foreign key: the case survives erasure "
                "unlinked; a nullable reference still blocks the delete.\n"
                "  account_id uuid,",
                "  account_id uuid references accounts(account_id) on delete set null,",
            ),
            encoding="utf-8",
        )
        self._run_with(
            copy, self.validator.validate_notification_and_local_deletion_contracts
        )

    def test_the_exception_set_is_empty(self) -> None:
        """An exception list that outlives its exceptions is a stale excuse."""
        self.assertEqual(
            self.validator.ERASURE_FK_EXCEPTIONS,
            frozenset(),
            "every recorded exception has been repaired; a new entry needs a reason",
        )

    def test_a_key_row_that_can_be_destroyed_and_still_hold_material_fails(
        self,
    ) -> None:
        copy = self._schemas_copy()
        path = copy / "planning-schema.sql"
        sql = path.read_text(encoding="utf-8")
        path.write_text(
            sql.replace(
                "check ((key_material is null) = (destroyed_at is not null))",
                "check (key_material is null or destroyed_at is null)",
            ),
            encoding="utf-8",
        )
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(copy, self.validator.validate_erasure_contract)
        self.assertIn("erasure_keys", str(raised.exception))

    def test_a_receipt_that_may_admit_traffic_before_the_reapply_fails(self) -> None:
        copy = self._schemas_copy()
        path = copy / "planning-schema.sql"
        sql = path.read_text(encoding="utf-8")
        path.write_text(
            sql.replace(
                "check (traffic_admitted_at is null or traffic_admitted_at >= reapply_completed_at)",
                "check (traffic_admitted_at is null or traffic_admitted_at >= reapply_started_at)",
            ),
            encoding="utf-8",
        )
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(copy, self.validator.validate_erasure_contract)
        self.assertIn("erasure_restore_receipts", str(raised.exception))

    def test_a_sealed_entry_naming_an_account_fails(self) -> None:
        copy = self._schemas_copy()
        path = copy / "planning-schema.sql"
        sql = path.read_text(encoding="utf-8")
        path.write_text(
            sql.replace(
                "  erasure_domain_id uuid not null references erasure_domains(erasure_domain_id),\n"
                "  token_burn_total bigint not null check (token_burn_total >= 0),\n"
                "  evidence_profile_id text not null,",
                "  erasure_domain_id uuid not null references erasure_domains(erasure_domain_id),\n"
                "  account_id uuid not null,\n"
                "  token_burn_total bigint not null check (token_burn_total >= 0),\n"
                "  evidence_profile_id text not null,",
                1,
            ),
            encoding="utf-8",
        )
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(copy, self.validator.validate_erasure_contract)
        self.assertIn("erasure-domain pseudonym", str(raised.exception))

    def test_a_column_named_score_fails(self) -> None:
        copy = self._schemas_copy()
        path = copy / "planning-schema.sql"
        sql = path.read_text(encoding="utf-8")
        path.write_text(
            sql.replace(
                "  token_burn_total bigint not null check (token_burn_total >= 0),\n"
                "  primary key (period_id, account_id, minute_start)",
                "  score bigint not null,\n"
                "  primary key (period_id, account_id, minute_start)",
                1,
            ),
            encoding="utf-8",
        )
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self._run_with(copy, self.validator.validate_erasure_contract)
        self.assertIn("score", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
