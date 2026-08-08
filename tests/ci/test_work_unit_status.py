"""Drift-injection tests for the work-unit status validator.

Each test rewrites one field in the breakdown and asserts the validator fails on
it. A validator whose failure modes are untested proves that the current tree
happens to pass, which is a much weaker claim than the one it makes.

Subprocess-running evidence is exercised directly through `evaluate_evidence`;
the document-level tests pass `--no-run` so the suite does not re-run every
validator in the repository once per case.
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
        # Every document mutation happens on a copy. An earlier revision of this
        # suite rewrote the real file and restored it in cleanup, and a single
        # interrupted run left a fabricated dependency in the committed tree.
        self.copy = self.directory / "PR_SIZED_WORK_BREAKDOWN.md"
        self.copy.write_text(self.original, encoding="utf-8")
        self.validator.BREAKDOWN = self.copy

    def run_validator(self, argv=None) -> int:
        return self.validator.main(list(argv or []) + ["--no-run"])

    def write(self, text: str) -> None:
        self.copy.write_text(text, encoding="utf-8")

    def test_the_suite_cannot_touch_the_real_breakdown(self) -> None:
        self.write(self.original.replace("\nEst: 4-6\n", "\nEst: 99\n", 1))
        self.run_validator()
        self.assertEqual(BREAKDOWN.read_text(encoding="utf-8"), self.original)

    # -- baseline ---------------------------------------------------------

    def test_clean_tree_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_every_unit_carries_all_five_fields(self) -> None:
        units = self.validator.parse_units(self.original)
        self.assertGreater(len(units), 250)
        for unit in units:
            for name in ("Files", "Acceptance", "Depends", "Est", "Status"):
                self.assertIn(name, unit.fields, f"{unit.unit_id} lacks {name}")

    def test_every_landed_unit_carries_evidence(self) -> None:
        units = self.validator.parse_units(self.original)
        landed = [u for u in units if u.status_word == "landed"]
        self.assertTrue(landed)
        for unit in landed:
            self.assertTrue(unit.evidence, f"{unit.unit_id} is landed with no evidence")

    def test_no_status_carries_a_commit_id(self) -> None:
        """D-206: a squash-merged sha is not evidence and must not reappear."""
        for line in self.original.splitlines():
            if line.startswith("Status:"):
                self.assertIsNone(
                    re.search(r"\b[0-9a-f]{7,40}\b", line),
                    f"commit id back in a status line: {line!r}",
                )

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
        text = re.sub(
            r"(### F-001 .*?\n)(Files:.*?\n)(Acceptance:.*?\n)Depends: PF-036\n",
            r"\1\2\3Depends: F-002\n",
            self.original,
            count=1,
            flags=re.S,
        )
        self.assertNotEqual(text, self.original)
        self.write(text)
        self.assertEqual(self.run_validator(), 1)

    def test_dependency_on_a_superseded_unit_fails(self) -> None:
        text = re.sub(
            r"(### F-002 .*?\n)(Files:.*?\n)(Acceptance:.*?\n)Depends: F-001\n",
            r"\1\2\3Depends: F-009\n",
            self.original,
            count=1,
            flags=re.S,
        )
        self.assertNotEqual(text, self.original)
        self.write(text)
        self.assertEqual(self.run_validator(), 1)

    # -- status defects ---------------------------------------------------

    def test_unknown_status_value_fails(self) -> None:
        self.write(
            self.original.replace("\nStatus: not-started\n", "\nStatus: done\n", 1)
        )
        self.assertEqual(self.run_validator(), 1)

    def test_landed_without_evidence_fails(self) -> None:
        self.write(
            self.original.replace("\nStatus: not-started\n", "\nStatus: landed\n", 1)
        )
        self.assertEqual(self.run_validator(), 1)

    def test_unverifiable_without_a_reason_fails(self) -> None:
        self.write(
            self.original.replace(
                "\nStatus: not-started\n", "\nStatus: unverifiable\n", 1
            )
        )
        self.assertEqual(self.run_validator(), 1)

    def test_unverifiable_with_a_reason_passes(self) -> None:
        self.write(
            self.original.replace(
                "\nStatus: not-started\n",
                "\nStatus: unverifiable\nReason: nothing in the tree can show this.\n",
                1,
            )
        )
        # The derived block now disagrees, which is itself a defect; regenerate first.
        self.assertEqual(self.validator.main(["--write"]), 0)
        self.assertEqual(self.run_validator(), 0)

    def test_evidence_on_a_non_landed_unit_fails(self) -> None:
        self.write(
            self.original.replace(
                "\nStatus: not-started\n",
                "\nStatus: not-started\nEvidence: exists README.md\n",
                1,
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

    def test_superseded_by_an_unknown_unit_fails(self) -> None:
        self.write(
            self.original.replace(
                "\nStatus: not-started\n", "\nStatus: superseded-by Z-001\n", 1
            )
        )
        self.assertEqual(self.run_validator(), 1)

    # -- the evidence engine ----------------------------------------------

    def evidence(self, assertion: str, run: bool = True):
        return self.validator.evaluate_evidence(assertion, run)

    def test_exists_and_missing(self) -> None:
        self.assertTrue(self.evidence("exists README.md")[0])
        self.assertFalse(self.evidence("exists docs/no-such-file.md")[0])
        self.assertTrue(self.evidence("missing docs/no-such-file.md")[0])
        self.assertFalse(self.evidence("missing README.md")[0])

    def test_contains_counts_lines(self) -> None:
        self.assertTrue(self.evidence("contains 1 README.md :: VibeMaxxing")[0])
        self.assertFalse(self.evidence("contains 9999 README.md :: VibeMaxxing")[0])
        self.assertFalse(
            self.evidence("contains 1 README.md :: no-such-string-anywhere")[0]
        )

    def test_absent_requires_zero(self) -> None:
        self.assertTrue(self.evidence("absent README.md :: no-such-string-anywhere")[0])
        self.assertFalse(self.evidence("absent README.md :: VibeMaxxing")[0])

    def test_contains_matches_a_literal_not_a_pattern(self) -> None:
        """A regex must not be honoured, or every assertion becomes vacuous."""
        probe = ROOT / "artifacts" / "work-unit-status-probe.txt"
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("alpha\nbeta\n", encoding="utf-8")
        self.addCleanup(probe.unlink, True)
        relative = probe.relative_to(ROOT)
        self.assertFalse(self.evidence(f"contains 1 {relative} :: .*")[0])
        self.assertFalse(self.evidence(f"contains 1 {relative} :: al.ha")[0])
        self.assertTrue(self.evidence(f"contains 1 {relative} :: alpha")[0])

    def test_validator_verb_runs_and_reports_exit_status(self) -> None:
        passed, _ = self.evidence("validator scripts/repository/doctor.py")
        self.assertTrue(passed)

    def test_validator_verb_refuses_paths_outside_scripts(self) -> None:
        self.assertFalse(self.evidence("validator /bin/echo")[0])
        self.assertFalse(self.evidence("validator ../escape.py")[0])

    def test_validator_verb_refuses_self_reference(self) -> None:
        self.assertFalse(
            self.evidence("validator scripts/repository/validate_work_unit_status.py")[
                0
            ]
        )

    def test_validator_verb_refuses_unsafe_arguments(self) -> None:
        self.assertFalse(
            self.evidence("validator scripts/repository/doctor.py ;rm -rf /")[0]
        )

    def test_unknown_verb_fails(self) -> None:
        self.assertFalse(self.evidence("shell echo hello")[0])

    def test_malformed_contains_fails(self) -> None:
        self.assertFalse(self.evidence("contains README.md :: x")[0])
        self.assertFalse(self.evidence("contains 1 README.md")[0])

    def test_a_landed_unit_with_a_failing_assertion_fails(self) -> None:
        text = self.original.replace(
            "Evidence: exists docs/decisions/ADR-015-SESSION_AUTHENTICATION.md",
            "Evidence: exists docs/decisions/ADR-999-NOT-A-FILE.md",
            1,
        )
        self.assertNotEqual(text, self.original)
        self.write(text)
        self.assertEqual(self.run_validator(), 1)

    # -- derived block ----------------------------------------------------

    def test_stale_derived_block_fails(self) -> None:
        self.write(
            self.original.replace(
                "| `not-started` |", "| `not-started` | 1 |\n| x |", 1
            )
        )
        self.assertEqual(self.run_validator(), 1)

    def test_write_regenerates_the_block(self) -> None:
        self.write(
            self.original.replace(
                "| `not-started` |", "| `not-started` | 1 |\n| x |", 1
            )
        )
        self.assertEqual(self.run_validator(), 1)
        self.assertEqual(self.validator.main(["--write"]), 0)
        self.assertEqual(self.run_validator(), 0)

    # -- table ownership --------------------------------------------------

    def test_unowned_sql_table_fails(self) -> None:
        copy = self.directory / "planning-schema.sql"
        copy.write_text(
            PLANNING_SQL.read_text(encoding="utf-8")
            + "\ncreate table orphaned_widgets (\n  id uuid primary key\n);\n",
            encoding="utf-8",
        )
        self.validator.PLANNING_SQL = copy
        self.assertEqual(self.run_validator(), 1)

    # -- gate -------------------------------------------------------------

    def test_gate_fails_while_the_closure_is_unlanded(self) -> None:
        self.assertEqual(self.run_validator(["--gate", "X-011"]), 1)

    def test_gate_rejects_an_unknown_unit(self) -> None:
        self.assertEqual(self.run_validator(["--gate", "Z-001"]), 2)

    def test_x011_closure_covers_every_live_implementation_unit(self) -> None:
        units = self.validator.parse_units(self.original)
        by_id = {unit.unit_id: unit for unit in units}
        inside = self.validator.closure(by_id, "X-011")
        outside = [
            unit.unit_id
            for unit in units
            if unit.unit_id not in inside
            and unit.unit_id != "X-011"
            and unit.status_word != "superseded-by"
        ]
        self.assertTrue(
            all(unit_id.startswith("PF-") for unit_id in outside),
            f"live implementation units outside the launch gate: {outside}",
        )


if __name__ == "__main__":
    unittest.main()


class RepairScheduleTests(unittest.TestCase):
    """The schedule is derived, so it cannot disagree with the units it schedules.

    A hand-maintained plan is stale the moment a unit lands, and a stale plan is worse
    than no plan because it still reads like one.
    """

    def setUp(self) -> None:
        self.validator = load_validator()
        self.units = self.validator.parse_units(
            self.validator.read_text(self.validator.BREAKDOWN)
        )
        self.series = {
            unit.unit_id: unit
            for unit in self.units
            if unit.unit_id.startswith("PF-")
            and int(unit.unit_id.split("-")[1]) <= 36
        }

    def test_every_unlanded_repair_unit_appears_exactly_once(self) -> None:
        waves = self.validator.repair_waves(self.units)
        scheduled = [unit_id for wave in waves for unit_id in wave]
        unlanded = {
            unit_id
            for unit_id, unit in self.series.items()
            if unit.status_word != "landed"
        }

        self.assertEqual(sorted(scheduled), sorted(unlanded))
        self.assertEqual(len(scheduled), len(set(scheduled)))

    def test_no_landed_unit_is_scheduled(self) -> None:
        waves = self.validator.repair_waves(self.units)
        scheduled = {unit_id for wave in waves for unit_id in wave}
        for unit_id, unit in self.series.items():
            if unit.status_word == "landed":
                self.assertNotIn(unit_id, scheduled)

    def test_every_dependency_lands_in_an_earlier_wave(self) -> None:
        """The property that makes the schedule a schedule."""
        waves = self.validator.repair_waves(self.units)
        position = {
            unit_id: index for index, wave in enumerate(waves) for unit_id in wave
        }
        for unit_id, unit in self.series.items():
            for dependency in unit.depends:
                if dependency in position and unit_id in position:
                    self.assertLess(
                        position[dependency], position[unit_id], f"{unit_id}"
                    )

    def test_wave_one_units_have_no_unlanded_dependency(self) -> None:
        waves = self.validator.repair_waves(self.units)
        if not waves:
            self.skipTest("every repair unit has landed")
        for unit_id in waves[0]:
            for dependency in self.series[unit_id].depends:
                if dependency in self.series:
                    self.assertEqual(
                        self.series[dependency].status_word, "landed", unit_id
                    )
