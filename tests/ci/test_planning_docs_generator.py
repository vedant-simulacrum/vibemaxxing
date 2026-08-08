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


if __name__ == "__main__":
    unittest.main()
