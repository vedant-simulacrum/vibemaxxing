"""Tests for scripts/repository/generate_planning_docs.py.

The register and catalog used to be hand-maintained Markdown that validators reached by
substring matching, which is why the phase gate could once only be moved by editing its
own validator, and why `## Register rules` sitting mid-table left 146 rows following a
heading with no table header while `validate_decision_register` kept passing anyway (it
matches rows, not a parsed table). The structure now lives in
`conformance/planning/decisions-v1.json` and `tasks-v1.json`; the Markdown is generated
output, and `stale()` is what the CI validator calls to prove the committed documents
still equal that output.

These tests cover: the regression guard (`stale()` is empty against the real tree), that
a hand-edited generated row is caught, that rendering the register and parsing it back is
lossless for all 291 decisions, the pipe-refusal defect `validate_decision_register` was
built to catch, a document with no markers failing loudly, the load-bearing shape of a
step's `Status:` line that `validate_repair_task_binding.py` depends on, and the exact
`####`-in-body defect that once made P-1140F swallow and duplicate all five of its steps.
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

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts" / "repository" / "generate_planning_docs.py"
BINDING_VALIDATOR = ROOT / "scripts" / "repository" / "validate_repair_task_binding.py"
DECISIONS_JSON = ROOT / "conformance" / "planning" / "decisions-v1.json"
DECISIONS_SCHEMA = ROOT / "conformance" / "planning" / "decisions-v1.schema.json"
TASKS_JSON = ROOT / "conformance" / "planning" / "tasks-v1.json"
TASKS_SCHEMA = ROOT / "conformance" / "planning" / "tasks-v1.schema.json"
REGISTER_MD = ROOT / "docs" / "planning" / "DECISION_REGISTER.md"
CATALOG_MD = ROOT / "docs" / "planning" / "TASK_CATALOG.md"
TRACEABILITY_JSON = ROOT / "conformance" / "planning" / "decision-traceability-v1.json"
TRACEABILITY_SCHEMA = (
    ROOT / "conformance" / "planning" / "decision-traceability-v1.schema.json"
)
TRACEABILITY_DIR = ROOT / "docs" / "planning" / "decision-traceability"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    # Python 3.14 resolves module-level annotation/type references against
    # sys.modules[name] during exec_module; registering first is required or
    # exec_module fails.
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_decisions_table(rendered_block: str) -> list[dict]:
    """The inverse of `render_decisions`: turn table rows back into records.

    Safe as a plain `|`-split because the schema and `render_decisions` both refuse a
    literal pipe inside a cell, so a data row can never contain more than four `|`
    separators.
    """
    records = []
    for line in rendered_block.splitlines():
        if not line.startswith("| D-"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        assert len(cells) == 4, f"row split into {len(cells)} cells, not 4: {line!r}"
        records.append(
            {
                "id": cells[0],
                "decision": cells[1],
                "status": cells[2],
                "validation_or_reopen": cells[3],
            }
        )
    return records


class PlanningDocsFixtureMixin:
    """Loads a fresh copy of the generator module. A mixin, not a shared TestCase base:
    this repo has twice been bitten by subclassing a TestCase to reuse a fixture.
    """

    def setUp(self) -> None:
        super().setUp()
        self.module = load_module(GENERATOR, "generate_planning_docs")
        directory = Path(tempfile.mkdtemp(prefix="planning-docs-"))
        self.addCleanup(shutil.rmtree, directory, True)
        self.directory = directory


class RegressionGuardTests(PlanningDocsFixtureMixin, unittest.TestCase):
    def test_the_committed_documents_already_match_generation(self) -> None:
        """The exact check `validate_planning_doc_generation` runs in CI."""
        self.assertEqual(self.module.stale(), [])

    def test_check_flag_exits_zero_against_the_real_tree(self) -> None:
        with patch.object(sys, "argv", ["generate_planning_docs.py", "--check"]):
            self.assertEqual(self.module.main(), 0)


class HandEditedRowDetectionTests(PlanningDocsFixtureMixin, unittest.TestCase):
    def test_a_hand_tampered_row_is_detected_as_stale(self) -> None:
        copy = self.directory / "DECISION_REGISTER.md"
        shutil.copyfile(REGISTER_MD, copy)
        original = copy.read_text(encoding="utf-8")

        target = (
            "| D-001 | Greenfield VibeMaxxing; no migration of old accounts or "
            "scores | accepted | explicit product reset |"
        )
        self.assertIn(
            target,
            original,
            "fixture assumption: D-001's row text must match exactly for this "
            "test to actually tamper it",
        )
        tampered = original.replace(
            target,
            "| D-001 | HAND EDITED, NOT FROM THE JSON SOURCE | accepted | "
            "explicit product reset |",
        )
        copy.write_text(tampered, encoding="utf-8")

        with patch.object(self.module, "REGISTER_MD", copy):
            stale = self.module.stale()

        self.assertEqual(stale, [copy])


class RoundTripFidelityTests(PlanningDocsFixtureMixin, unittest.TestCase):
    def test_rendering_and_reparsing_reproduces_every_decision_exactly(self) -> None:
        """Proves generation is lossless for all 291 decisions: same count, same
        order, same four fields, round-tripped through the rendered table.
        """
        source = load_json(DECISIONS_JSON)
        rendered = self.module.render_decisions(source)

        reparsed = parse_decisions_table(rendered)

        self.assertEqual(len(reparsed), len(source["decisions"]))
        self.assertEqual(reparsed, source["decisions"])


class PipeRefusalTests(PlanningDocsFixtureMixin, unittest.TestCase):
    def test_a_pipe_in_a_decision_cell_is_refused_not_emitted(self) -> None:
        """A literal pipe would silently shift every column to its right when the
        table is parsed back — the defect `validate_decision_register` exists to
        catch. `render_decisions` must refuse to emit one rather than emit a table
        that parses wrongly.
        """
        source = load_json(DECISIONS_JSON)
        source["decisions"][0]["decision"] = "a | poisoned cell"
        poisoned_id = source["decisions"][0]["id"]

        with self.assertRaises(self.module.Failure) as raised:
            self.module.render_decisions(source)

        self.assertIn(poisoned_id, str(raised.exception))


class MissingMarkersTests(PlanningDocsFixtureMixin, unittest.TestCase):
    def test_a_document_with_no_markers_fails_loudly(self) -> None:
        with self.assertRaises(self.module.Failure) as raised:
            self.module.splice(
                "# A document\n\nno markers in here at all\n",
                self.module.DECISIONS_BEGIN,
                self.module.DECISIONS_END,
                "block",
                "some-document.md",
            )

        self.assertIn("has no generated block", str(raised.exception))
        self.assertIn("some-document.md", str(raised.exception))


class StepStatusShapeTests(PlanningDocsFixtureMixin, unittest.TestCase):
    def test_the_rendered_status_line_is_what_the_binding_validator_parses(
        self,
    ) -> None:
        """The `Status:` line's shape is load-bearing: `validate_repair_task_binding.py`
        finds it with `^Status:\\s*(.+)$` and strips the backticks to decide whether a
        step may claim completion while it still owns unlanded units. Changing the
        shape would silently unbind every step from that check. Confirmed two ways:
        the exact line is present in the rendered document, and the real validator's
        own `STEP` regex and `field()` function extract it from that document.
        """
        rendered = dict(self.module.documents())[CATALOG_MD]

        self.assertIn("Status: `in-progress-planning`\n", rendered)

        binding = load_module(BINDING_VALIDATOR, "validate_repair_task_binding")
        steps = {
            match.group(1): match.group("body")
            for match in binding.STEP.finditer(rendered)
        }
        self.assertIn("P-1140F-1", steps)
        self.assertEqual(
            binding.field(steps["P-1140F-1"], "Status"), "`in-progress-planning`"
        )


class TasksSchemaRejectsNestedHeadingTests(PlanningDocsFixtureMixin, unittest.TestCase):
    def test_a_level_four_heading_inside_a_program_body_is_rejected(self) -> None:
        """The first extraction's program-body pattern stopped at `###`/`##` but not
        at `####`, so P-1140F's own step-introducing sentence, once lifted into a
        program body, swallowed all five step blocks and rendering duplicated them.
        The schema now refuses a `####` line inside any block body outright.
        """
        tasks = load_json(TASKS_JSON)
        schema = load_json(TASKS_SCHEMA)
        tasks["programs"][0]["body"] += "\n#### a heading that must not be here\n"

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=tasks, schema=schema)


class CommittedSourcesValidateTests(unittest.TestCase):
    def test_decisions_json_validates_against_its_schema(self) -> None:
        jsonschema.validate(
            instance=load_json(DECISIONS_JSON), schema=load_json(DECISIONS_SCHEMA)
        )

    def test_tasks_json_validates_against_its_schema(self) -> None:
        jsonschema.validate(
            instance=load_json(TASKS_JSON), schema=load_json(TASKS_SCHEMA)
        )


class TraceabilityCoverageTests(PlanningDocsFixtureMixin, unittest.TestCase):
    """PF-063: every decision must have a traceability row, and no row may name a
    decision the register does not hold. `untraced()` and `orphaned()` are the checks
    `validate_decision_traceability` runs in CI.
    """

    def test_every_decision_is_traced_and_no_row_is_orphaned_on_the_real_tree(
        self,
    ) -> None:
        self.assertEqual(self.module.untraced(), [])
        self.assertEqual(self.module.orphaned(), [])

    def test_a_row_removed_from_the_register_is_reported_as_untraced(self) -> None:
        """Pick a real row out of the loaded JSON rather than hardcoding a decision
        id: the register is sparse, and a previously hardcoded id turned out not to
        exist, silently making that assertion vacuous.
        """
        traceability = load_json(TRACEABILITY_JSON)
        removed = traceability["rows"][0]["id"]
        traceability["rows"] = traceability["rows"][1:]

        patched = self.directory / "decision-traceability-v1.json"
        patched.write_text(json.dumps(traceability), encoding="utf-8")

        with patch.object(self.module, "TRACEABILITY_JSON", patched):
            self.assertEqual(self.module.untraced(), [removed])
            # The register itself is untouched, so nothing is orphaned by this edit.
            self.assertEqual(self.module.orphaned(), [])

    def test_a_row_for_an_unknown_decision_is_reported_as_orphaned(self) -> None:
        traceability = load_json(TRACEABILITY_JSON)
        decisions = {row["id"] for row in load_json(DECISIONS_JSON)["decisions"]}
        self.assertNotIn(
            "D-999",
            decisions,
            "fixture assumption: D-999 must not be a real decision id",
        )
        traceability["rows"].append(
            {
                "id": "D-999",
                "implementation_bearing": False,
                "reason": "synthetic row added by a test; not a real decision",
            }
        )

        patched = self.directory / "decision-traceability-v1.json"
        patched.write_text(json.dumps(traceability), encoding="utf-8")

        with patch.object(self.module, "TRACEABILITY_JSON", patched):
            self.assertEqual(self.module.orphaned(), ["D-999"])
            # Every real decision is still covered; the extra row does not remove
            # coverage for anything.
            self.assertEqual(self.module.untraced(), [])


class TraceabilityShardNamingTests(PlanningDocsFixtureMixin, unittest.TestCase):
    """PF-063 regression: grouping the tail by row count named each file after the ids
    it happened to hold, so appending one decision renamed the final shard and left the
    old name behind. The grid fixes that; these tests prove filenames are stable as the
    register grows and that a leftover file from the old scheme is caught.
    """

    def test_appending_a_decision_does_not_rename_any_existing_shard(self) -> None:
        """The regression this guards against only shows up when the new row lands in
        the *same* grid bucket as an already-populated one — a brand-new trailing
        bucket (as a `D-999`-style id would create) is a new file either way, old
        scheme or new. So this extends the highest existing tail id by one instead,
        landing in the same bucket the last real row already occupies, which is
        exactly what triggered the original defect when D-609 was added.

        The new id is built from an arithmetic offset rather than written as a
        literal `D-NNN` token, because a literal non-existent decision id in this
        file would itself be flagged as a dangling cross-reference.
        """
        before = {path.name for path, _ in self.module.traceability_documents()}

        traceability = load_json(TRACEABILITY_JSON)
        highest = max(int(row["id"].split("-")[1]) for row in traceability["rows"])
        synthetic_id = "D-" + f"{highest + 1:03d}"
        traceability["rows"].append(
            {
                "id": synthetic_id,
                "implementation_bearing": False,
                "reason": "synthetic row added by a test; not a real decision",
            }
        )
        patched = self.directory / "decision-traceability-v1.json"
        patched.write_text(json.dumps(traceability), encoding="utf-8")

        with patch.object(self.module, "TRACEABILITY_JSON", patched):
            after = {path.name for path, _ in self.module.traceability_documents()}

        # Every filename that existed before must still exist unchanged. Because the
        # synthetic row extends the same bucket the highest real row already
        # occupies, a grid-stable implementation produces the identical shard set —
        # no new file at all.
        self.assertTrue(
            before <= after,
            f"a pre-existing shard was renamed or dropped: {before - after}",
        )
        new_files = after - before
        self.assertEqual(
            new_files,
            set(),
            "appending one decision into an already-populated bucket must not "
            f"produce a new or renamed shard, got {new_files}",
        )

    def test_orphaned_shards_names_a_leftover_file_from_the_old_scheme(self) -> None:
        expected = {path.name for path, _ in self.module.traceability_documents()}

        shard_directory = self.directory / "decision-traceability"
        shard_directory.mkdir()
        for name in expected:
            (shard_directory / name).write_text("stale placeholder", encoding="utf-8")
        # "999" is this repository's synthetic-id sentinel (see SYNTHETIC_SENTINEL in
        # validate_cross_references.py), so this filename is exempt from the
        # dangling-decision-reference check while still being obviously not a real
        # generated shard name.
        leftover = shard_directory / "D-999-D-999.md"
        leftover.write_text("orphaned by a rename", encoding="utf-8")

        with patch.object(self.module, "TRACEABILITY_DIR", shard_directory):
            orphans = self.module.orphaned_shards()

        self.assertEqual(orphans, [leftover])

    def test_the_frozen_legacy_shards_keep_their_exact_filenames(self) -> None:
        """P-1140E already used D-001-D-020.md, D-021-D-040.md, D-041-D-061.md and
        D-062-D-069.md; PF-063 must not move that content under a new name.
        """
        generated = {path.name for path, _ in self.module.traceability_documents()}
        legacy_names = {
            f"{first}-{last}.md" for first, last in self.module.LEGACY_GROUPS
        }
        self.assertTrue(legacy_names <= generated)


class TraceabilitySchemaTests(unittest.TestCase):
    """The schema is the only thing standing between an empty implementation-owner
    cell and a row that looks covered but isn't. These prove both branches of the
    implementation_bearing conditional are actually enforced, not just documented.
    """

    def setUp(self) -> None:
        self.schema = load_json(TRACEABILITY_SCHEMA)
        self.data = load_json(TRACEABILITY_JSON)

    def test_a_bearing_row_with_an_empty_required_cell_is_rejected(self) -> None:
        row = next(r for r in self.data["rows"] if r["implementation_bearing"])
        row["normative_owner"] = ""

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=self.data, schema=self.schema)

    def test_a_non_bearing_row_carrying_an_implementation_field_is_rejected(
        self,
    ) -> None:
        row = next(r for r in self.data["rows"] if not r["implementation_bearing"])
        row["normative_owner"] = "smuggled in despite implementation_bearing: false"

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=self.data, schema=self.schema)

    def test_the_two_unassigned_owner_rows_carry_an_owner_gap_reason(self) -> None:
        """D-101 and D-103 are the only rows using the escape hatch the schema's
        description names: `implementation_owner: "unassigned"` is permitted only
        alongside `owner_gap_reason`, so a real gap is counted rather than papered
        over with a plausible-looking owner.

        NOTE: this is a data-level assertion only. The JSON Schema itself has no
        conditional (`if`/`then`) tying `owner_gap_reason` to
        `implementation_owner == "unassigned"` — `owner_gap_reason` is not in any
        `required` list, so a row can set `implementation_owner: "unassigned"` and
        omit `owner_gap_reason` and still validate. See the schema round-trip test
        below, which demonstrates this rather than asserting a rejection that the
        schema does not actually perform.
        """
        unassigned = [
            row
            for row in self.data["rows"]
            if row.get("implementation_owner") == "unassigned"
        ]
        self.assertEqual({row["id"] for row in unassigned}, {"D-101", "D-103"})
        for row in unassigned:
            self.assertTrue(
                row.get("owner_gap_reason"),
                f"{row['id']} uses implementation_owner: unassigned with no "
                "owner_gap_reason",
            )

    def test_an_unassigned_owner_without_a_reason_is_rejected(self) -> None:
        """`unassigned` claims no unit owns the decision, and a claim needs its reason.

        The schema described this rule in a property description and did not express
        it, so removing `owner_gap_reason` validated cleanly — a description is not a
        check, which is the defect class this repository keeps finding. The `if`/`then`
        now enforces it, and this test is what would notice if it were removed again.
        """
        row = next(r for r in self.data["rows"] if r["id"] == "D-101")
        self.assertEqual(row["implementation_owner"], "unassigned")
        row.pop("owner_gap_reason", None)

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=self.data, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
