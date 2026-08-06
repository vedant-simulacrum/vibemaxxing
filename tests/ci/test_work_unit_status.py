"""Drift-injection tests for the work-unit status validator.

Each test rewrites one field in a copy of the breakdown and asserts the validator
fails on it. A validator whose failure modes are untested proves that the current
tree happens to pass, which is a much weaker claim than the one it makes.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_work_unit_status.py"
BREAKDOWN = ROOT / "docs" / "implementation" / "PR_SIZED_WORK_BREAKDOWN.md"
PLANNING_SQL = ROOT / "packages" / "schemas" / "planning-schema.sql"


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_work_unit_status", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class WorkUnitStatusValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.directory = Path(tempfile.mkdtemp(prefix="work-unit-status-"))
        self.addCleanup(shutil.rmtree, self.directory, True)
        self.original = BREAKDOWN.read_text(encoding="utf-8")
        self.backup = self.directory / "breakdown.md"
        self.backup.write_text(self.original, encoding="utf-8")
        self.addCleanup(lambda: BREAKDOWN.write_text(self.original, encoding="utf-8"))

    def run_validator(self, argv=None) -> int:
        return self.validator.main(argv or [])

    def write(self, text: str) -> None:
        BREAKDOWN.write_text(text, encoding="utf-8")

    # -- baseline ---------------------------------------------------------

    def test_clean_tree_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_every_unit_carries_all_five_fields(self) -> None:
        units = self.validator.parse_units(self.original)
        self.assertGreater(len(units), 200)
        for unit in units:
            for name in ("Files", "Acceptance", "Depends", "Est", "Status"):
                self.assertIn(name, unit.fields, f"{unit.unit_id} lacks {name}")

    # -- field defects ----------------------------------------------------

    def test_missing_field_fails(self) -> None:
        self.write(self.original.replace("\nEst: 4-6\n", "\n", 1))
        self.assertEqual(self.run_validator(), 1)

    def test_estimate_above_the_ceiling_fails(self) -> None:
        self.write(self.original.replace("\nEst: 4-6\n", "\nEst: 40\n", 1))
        self.assertEqual(self.run_validator(), 1)

    def test_unresolvable_dependency_fails(self) -> None:
        self.write(
            self.original.replace("\nDepends: PF-036\n", "\nDepends: Z-001\n", 1)
        )
        self.assertEqual(self.run_validator(), 1)

    def test_prose_dependency_fails(self) -> None:
        self.write(
            self.original.replace(
                "\nDepends: PF-036\n", "\nDepends: implemented product paths\n", 1
            )
        )
        self.assertEqual(self.run_validator(), 1)

    def test_dependency_cycle_fails(self) -> None:
        text = self.original.replace(
            "### F-001 Toolchain and lockfile pins\n",
            "### F-001 Toolchain and lockfile pins\n",
            1,
        )
        text = re.sub(
            r"(### F-001 .*?\n)(Files:.*?\n)(Acceptance:.*?\n)Depends: PF-036\n",
            r"\1\2\3Depends: F-002\n",
            text,
            count=1,
            flags=re.S,
        )
        self.write(text)
        self.assertEqual(self.run_validator(), 1)

    # -- status defects ---------------------------------------------------

    def test_unknown_status_value_fails(self) -> None:
        self.write(
            self.original.replace("\nStatus: not-started\n", "\nStatus: done\n", 1)
        )
        self.assertEqual(self.run_validator(), 1)

    def test_landed_without_a_commit_fails(self) -> None:
        self.write(
            self.original.replace("\nStatus: not-started\n", "\nStatus: landed\n", 1)
        )
        self.assertEqual(self.run_validator(), 1)

    def test_landed_naming_an_unresolvable_commit_fails(self) -> None:
        self.write(
            self.original.replace(
                "\nStatus: not-started\n", "\nStatus: landed deadbee\n", 1
            )
        )
        self.assertEqual(self.run_validator(), 1)

    def test_not_started_contradicted_by_an_existing_artifact_fails(self) -> None:
        """The staleness this whole mechanism exists to catch."""
        text = re.sub(
            r"(### PF-054 .*?\nFiles: )`conformance/vibeproof/v1/negative-vectors\.json` \(new\)",
            r"\1`packages/schemas/planning-schema.sql` (new)",
            self.original,
            count=1,
            flags=re.S,
        )
        self.assertNotEqual(text, self.original)
        self.write(text)
        self.assertEqual(self.run_validator(), 1)

    def test_landed_with_a_missing_artifact_fails(self) -> None:
        text = re.sub(
            r"(### PF-054 .*?\n)Status: not-started\n",
            r"\1Status: landed 8baad9a\n",
            self.original,
            count=1,
            flags=re.S,
        )
        self.assertNotEqual(text, self.original)
        self.write(text)
        self.assertEqual(self.run_validator(), 1)

    def test_superseded_by_an_unknown_unit_fails(self) -> None:
        self.write(
            self.original.replace(
                "\nStatus: not-started\n", "\nStatus: superseded-by Z-001\n", 1
            )
        )
        self.assertEqual(self.run_validator(), 1)

    # -- derived block ----------------------------------------------------

    def test_stale_derived_block_fails(self) -> None:
        text = self.original.replace(
            "| `not-started` |", "| `not-started` | 1 |\n| unused |", 1
        )
        self.write(text)
        self.assertEqual(self.run_validator(), 1)

    def test_write_regenerates_the_block(self) -> None:
        text = self.original.replace(
            "| `not-started` |", "| `not-started` | 1 |\n| unused |", 1
        )
        self.write(text)
        self.assertEqual(self.run_validator(), 1)
        self.assertEqual(self.run_validator(["--write"]), 0)
        self.assertEqual(self.run_validator(), 0)

    # -- table ownership --------------------------------------------------

    def test_unowned_sql_table_fails(self) -> None:
        original_sql = PLANNING_SQL.read_text(encoding="utf-8")
        self.addCleanup(lambda: PLANNING_SQL.write_text(original_sql, encoding="utf-8"))
        PLANNING_SQL.write_text(
            original_sql
            + "\ncreate table orphaned_widgets (\n  id uuid primary key\n);\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_validator(), 1)

    # -- gate -------------------------------------------------------------

    def test_gate_fails_while_the_closure_is_unlanded(self) -> None:
        self.assertEqual(self.run_validator(["--gate", "X-011"]), 1)

    def test_gate_rejects_an_unknown_unit(self) -> None:
        self.assertEqual(self.run_validator(["--gate", "Z-001"]), 2)

    def test_x011_closure_covers_every_implementation_unit(self) -> None:
        units = self.validator.parse_units(self.original)
        by_id = {unit.unit_id: unit for unit in units}
        inside = self.validator.closure(by_id, "X-011")
        outside = [
            unit.unit_id
            for unit in units
            if unit.unit_id not in inside and unit.unit_id != "X-011"
        ]
        self.assertTrue(
            all(unit_id.startswith("PF-") for unit_id in outside),
            f"implementation units outside the launch gate: {outside}",
        )


if __name__ == "__main__":
    unittest.main()
