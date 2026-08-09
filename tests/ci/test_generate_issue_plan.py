"""Drift-injection tests for the deterministic issue-plan generator.

The generator had no test at all and measured 0% in
`scripts/ci/measured-coverage-baseline-v1.json`, while running on every pull request.
What it asserted about the phase gate was therefore never checked against the gate
record: it printed `P-1104-explicit-implementation-approval` and `blocked` on every
implementation record, and the workflow step asserted the same two literals back, so
the pair agreed with each other and with nothing else for the three days after the
owner opened P-1104.

Every check here breaks one input and asserts the exact failure. A generator whose
failure modes are untested proves only that today's tree happens to pass.
"""

from __future__ import annotations

# Synthetic identifiers used by the fixtures below are composed rather than
# written out. `validate_cross_references.py` scans every tracked file, including
# this one, so a literal `docs/<missing>.md` or an invented unit id would dangle
# indistinguishably from a real broken citation.
# Fixture headings use the `ZZ` epic prefix, which no epic uses and which
# `validate_cross_references.py` does not recognise as a work-unit ID, and a real
# path. A synthetic fixture must not leave a dangling reference behind, and hiding
# one from the scanner by splitting the literal would be working around the check.
FIXTURE_PATH = "docs/implementation/ISSUE_GENERATION.md"

import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts" / "repository" / "generate_issue_plan.py"
BREAKDOWN = ROOT / "docs" / "implementation" / "PR_SIZED_WORK_BREAKDOWN.md"
GATE_RECORD = ROOT / "conformance" / "p1140f" / "gate-authorization-v1.json"
CONTRACT = ROOT / "docs" / "implementation" / "ISSUE_GENERATION.md"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    # Registering before exec is required on 3.14: module-level annotations are
    # resolved against sys.modules while the module executes.
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class IssuePlanFixtureMixin:
    """Fresh generator module over throwaway copies of both of its inputs.

    A mixin rather than a shared TestCase base: this repository has twice been bitten
    by subclassing a TestCase to reuse a fixture. Both inputs are copied because the
    generator reads the breakdown *and* the gate authorization record, and neither may
    be mutated in the tree — `tests/ci/test_work_unit_status.py` records what happened
    the one time a suite rewrote the real breakdown and restored it in cleanup.
    """

    def setUp(self) -> None:
        super().setUp()
        self.module = load_module(GENERATOR, "generate_issue_plan")
        directory = Path(tempfile.mkdtemp(prefix="issue-plan-"))
        self.addCleanup(shutil.rmtree, directory, True)
        self.directory = directory

        self.breakdown_text = BREAKDOWN.read_text(encoding="utf-8")
        self.gate_text = GATE_RECORD.read_text(encoding="utf-8")
        self.source = directory / "PR_SIZED_WORK_BREAKDOWN.md"
        self.gate = directory / "gate-authorization-v1.json"
        self.source.write_text(self.breakdown_text, encoding="utf-8")
        self.gate.write_text(self.gate_text, encoding="utf-8")
        self.output = directory / "issue-plan.json"
        self.module.SOURCE = self.source
        self.module.GATE_RECORD = self.gate

    # -- helpers ----------------------------------------------------------

    def generate(self) -> dict:
        with patch.object(
            sys, "argv", ["generate_issue_plan.py", "--output", str(self.output)]
        ):
            self.module.main()
        return json.loads(self.output.read_text(encoding="utf-8"))

    def expect_failure(self, fragment: str) -> str:
        with self.assertRaises(SystemExit) as raised:
            self.generate()
        message = str(raised.exception.code)
        self.assertIn(fragment, message)
        return message

    def write_source(self, text: str) -> None:
        self.source.write_text(text, encoding="utf-8")

    def set_gate_state(self, gate_id: str, state: str) -> None:
        record = json.loads(self.gate_text)
        for entry in record["gates"]:
            if entry["gate"] == gate_id:
                entry["state"] = state
                break
        else:  # pragma: no cover - the fixture record always names the gate
            raise AssertionError(f"no {gate_id} gate in the fixture record")
        self.gate.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def by_key(self) -> dict[str, dict]:
        return {issue["key"]: issue for issue in self.generate()["issues"]}


class RecordFieldTests(IssuePlanFixtureMixin, unittest.TestCase):
    def test_the_suite_cannot_touch_the_real_inputs(self) -> None:
        self.write_source(self.breakdown_text.replace("Est: 4-6", "Est: 99", 1))
        self.set_gate_state("P-1104", "blocked-approval")
        self.generate()
        self.assertEqual(BREAKDOWN.read_text(encoding="utf-8"), self.breakdown_text)
        self.assertEqual(GATE_RECORD.read_text(encoding="utf-8"), self.gate_text)

    def test_every_record_carries_the_five_unit_fields(self) -> None:
        document = self.generate()
        self.assertGreater(document["issue_count"], 250)
        for issue in document["issues"]:
            for name in ("files", "acceptance", "depends", "est", "status"):
                self.assertIn(name, issue, f"{issue['key']} lacks {name}")
            self.assertTrue(issue["files"], issue["key"])
            self.assertTrue(issue["acceptance"], issue["key"])
            self.assertTrue(issue["est"], issue["key"])
            self.assertTrue(issue["status"], issue["key"])

    def test_fields_are_copied_from_the_unit_block_verbatim(self) -> None:
        issue = self.by_key()["PF-037"]
        self.assertEqual(issue["est"], "4-6")
        self.assertIn(
            "scripts/repository/generate_issue_plan.py",
            issue["files"],
        )
        self.assertEqual(issue["new_files"], ["tests/ci/test_generate_issue_plan.py"])
        self.assertIn("emits records carrying", issue["acceptance"])

    def test_depends_none_is_an_empty_list_not_the_word_none(self) -> None:
        self.assertEqual(self.by_key()["PF-037"]["depends"], [])
        self.assertEqual(self.by_key()["F-001"]["depends"], ["PF-036"])

    def test_a_unit_missing_a_required_field_is_not_emitted(self) -> None:
        mutated = self.breakdown_text.replace(
            "Acceptance: `python3 scripts/repository/generate_issue_plan.py` emits",
            "Acceptance:\nUnrelated: `python3 scripts/repository/generate_issue_plan.py` emits",
            1,
        )
        self.write_source(mutated)
        # The heading's line number is computed rather than written down. It was a
        # literal, and every edit anywhere above `PF-037` in the breakdown failed this
        # test for a reason with nothing to do with what it checks.
        line = next(
            number
            for number, text in enumerate(mutated.splitlines(), start=1)
            if text.startswith("### PF-037 ")
        )
        self.expect_failure(f"PF-037 (line {line}) is missing `Acceptance:`")

    def test_generation_is_byte_deterministic(self) -> None:
        first = self.output.read_bytes() if self.output.exists() else b""
        self.generate()
        first = self.output.read_bytes()
        self.generate()
        self.assertEqual(first, self.output.read_bytes())


class PhaseGateTests(IssuePlanFixtureMixin, unittest.TestCase):
    def test_the_gate_is_derived_from_the_epic_prefix_for_every_unit(self) -> None:
        for issue in self.generate()["issues"]:
            expected = "P-1140F" if issue["key"].startswith("PF-") else "P-1104"
            self.assertEqual(issue["phase_gate"], expected, issue["key"])

    def test_gate_state_is_read_from_the_authorization_record(self) -> None:
        record = json.loads(self.gate_text)
        states = {gate["gate"]: gate["state"] for gate in record["gates"]}
        document = self.generate()
        self.assertEqual(document["gate_states"]["P-1104"], states["P-1104"])
        by_key = {issue["key"]: issue for issue in document["issues"]}
        self.assertEqual(by_key["F-001"]["phase_gate_state"], states["P-1104"])
        self.assertEqual(by_key["PF-001"]["phase_gate_state"], states["P-1140F"])

    def test_an_open_gate_does_not_label_its_units_blocked(self) -> None:
        issue = self.by_key()["F-001"]
        self.assertEqual(issue["phase_gate_state"], "authorized-open")
        self.assertFalse(issue["blocked"])
        self.assertNotIn("blocked", issue["labels"])

    def test_moving_the_gate_back_to_blocked_relabels_every_unit(self) -> None:
        self.set_gate_state("P-1104", "blocked-approval")
        by_key = self.by_key()
        self.assertTrue(by_key["F-001"]["blocked"])
        self.assertIn("blocked", by_key["F-001"]["labels"])
        # The planning gate did not move, so the repair units did not either.
        self.assertFalse(by_key["PF-001"]["blocked"])

    def test_an_unrecognised_gate_state_fails_closed(self) -> None:
        self.set_gate_state("P-1104", "state-nobody-has-defined-yet")
        issue = self.by_key()["F-001"]
        self.assertTrue(issue["blocked"])
        self.assertEqual(issue["phase_gate_state"], "state-nobody-has-defined-yet")

    def test_a_record_naming_no_implementation_gate_is_refused(self) -> None:
        record = json.loads(self.gate_text)
        record["gates"] = [g for g in record["gates"] if g["gate"] != "P-1104"]
        self.gate.write_text(json.dumps(record, indent=2), encoding="utf-8")
        self.expect_failure("names no P-1104 gate")

    def test_a_gate_entry_without_a_state_is_refused(self) -> None:
        record = json.loads(self.gate_text)
        for entry in record["gates"]:
            entry.pop("state", None)
        self.gate.write_text(json.dumps(record, indent=2), encoding="utf-8")
        self.expect_failure("holds a gate with no id or no state")

    def test_an_unparseable_gate_record_is_refused(self) -> None:
        self.gate.write_text("{not json", encoding="utf-8")
        self.expect_failure("invalid JSON gate record")

    def test_no_gate_string_is_hardcoded_into_a_record(self) -> None:
        """Neither literal the generator used to print survives in its output."""
        self.generate()
        emitted = self.output.read_text(encoding="utf-8")
        self.assertNotIn("P-1104-explicit-implementation-approval", emitted)
        self.assertNotIn("P-1140F-planning-repair", emitted)
        # And no gate value in the plan is anything but a state the record holds.
        record = json.loads(self.gate_text)
        states = {gate["state"] for gate in record["gates"]}
        for issue in json.loads(emitted)["issues"]:
            self.assertIn(issue["phase_gate_state"], states, issue["key"])


class StatusAgreementTests(IssuePlanFixtureMixin, unittest.TestCase):
    def test_the_two_readers_agree_on_the_real_tree(self) -> None:
        validator = load_module(
            ROOT / "scripts" / "repository" / "validate_work_unit_status.py",
            "validate_work_unit_status",
        )
        recorded = {
            unit.unit_id: unit.status_word
            for unit in validator.parse_units(self.breakdown_text)
        }
        generated = {i["key"]: i["status"] for i in self.generate()["issues"]}
        self.assertEqual(generated, recorded)

    def test_a_heading_the_validator_sees_and_the_generator_does_not(self) -> None:
        """Dropping a title hides the unit from the generator's pattern alone."""
        self.write_source(
            self.breakdown_text.replace(
                "### PF-037 — Enforce required unit fields in the issue plan generator",
                "### PF-037",
                1,
            )
        )
        message = self.expect_failure(
            "issue plan and work-unit status validator disagree"
        )
        self.assertIn("PF-037: validate_work_unit_status.py reads status", message)
        self.assertIn("the issue plan has no record for it", message)

    def test_a_heading_the_generator_sees_and_the_validator_does_not(self) -> None:
        """A prefix wider than the validator's `[A-Z]{1,2}` pattern."""
        self.write_source(
            self.breakdown_text + "\n## Epic QQQ — Invented epic\n\n"
            "### QQQ-001 — Invented unit\n"
            "Files: `" + FIXTURE_PATH + "`\n"
            "Acceptance: nothing\n"
            "Depends: none\n"
            "Est: 1\n"
            "Status: not-started\n"
        )
        message = self.expect_failure(
            "issue plan and work-unit status validator disagree"
        )
        self.assertIn("QQQ-001: the issue plan reads status 'not-started'", message)
        self.assertIn("validate_work_unit_status.py has no unit for it", message)

    def test_the_disagreement_check_runs_before_contiguity(self) -> None:
        """Otherwise a dropped heading is reported as a numbering complaint."""
        message = self.expect_failure_after(
            self.breakdown_text.replace(
                "### F-002 Workspace initialization and package boundaries",
                "### F-002",
                1,
            ),
            "issue plan and work-unit status validator disagree",
        )
        self.assertNotIn("must be contiguous", message)

    def expect_failure_after(self, text: str, fragment: str) -> str:
        self.write_source(text)
        return self.expect_failure(fragment)


class StructuralRefusalTests(IssuePlanFixtureMixin, unittest.TestCase):
    def test_a_prefix_that_does_not_match_its_epic_is_refused(self) -> None:
        self.write_source(
            self.breakdown_text.replace(
                "### F-002 Workspace initialization and package boundaries",
                "### Q-002 Workspace initialization and package boundaries",
                1,
            )
        )
        self.expect_failure("work-unit prefix Q does not match current epic F")

    def test_non_contiguous_numbering_is_refused(self) -> None:
        """Both readers see `ZZ-002`, so they agree and contiguity is what fails."""
        self.write_source(
            self.breakdown_text + "\n## Epic ZZ — Invented epic\n\n"
            "### ZZ-002 — Invented second unit of a one-unit epic\n"
            "Files: `" + FIXTURE_PATH + "`\n"
            "Acceptance: nothing\n"
            "Depends: none\n"
            "Est: 1\n"
            "Status: not-started\n"
        )
        self.expect_failure("work units for ZZ must be contiguous and source ordered")

    def test_a_field_line_under_a_prose_heading_belongs_to_no_unit(self) -> None:
        """`### Required unit fields` documents the field names in prose."""
        units = self.module.parse_units(self.breakdown_text)
        keys = {unit["key"] for unit in units}
        self.assertNotIn("Required", keys)
        for unit in units:
            self.assertTrue(unit["fields"], unit["key"])


class DeadPostLaunchBranchTests(IssuePlanFixtureMixin, unittest.TestCase):
    def test_the_post_launch_heading_constant_is_gone(self) -> None:
        self.assertFalse(hasattr(self.module, "POST_LAUNCH_HEADING"))

    def test_no_post_launch_gate_survives_in_generator_or_contract(self) -> None:
        self.assertNotIn(
            "post-launch-explicit-approval", GENERATOR.read_text(encoding="utf-8")
        )
        self.assertNotIn(
            "post-launch-explicit-approval", CONTRACT.read_text(encoding="utf-8")
        )

    def test_a_post_launch_section_no_longer_invents_an_epic(self) -> None:
        """The heading is an ordinary section now, so it sets no epic of its own."""
        self.write_source(
            self.breakdown_text + "\n## Post-launch tracks\n\n"
            "### ZZ-001 — Invented post-launch unit\n"
            "Files: `" + FIXTURE_PATH + "`\n"
            "Acceptance: nothing\n"
            "Depends: none\n"
            "Est: 1\n"
            "Status: not-started\n"
        )
        message = self.expect_failure("work-unit prefix ZZ does not match current epic")
        # The epic named is whichever one preceded the section. Had the dead branch
        # survived, this would read `current epic PL`.
        self.assertNotIn("current epic PL", message)


class ContractDocumentTests(IssuePlanFixtureMixin, unittest.TestCase):
    """`ISSUE_GENERATION.md` documents keys the generator's own pattern must accept."""

    def test_every_documented_key_matches_the_generator_pattern(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")
        keys = set(self.by_key())
        cited = re.findall(r"`([A-Z][A-Z0-9]*-\d{2,3})`", text)
        self.assertTrue(cited, "the contract cites no stable key at all")
        for citation in cited:
            self.assertRegex(citation, r"^[A-Z][A-Z0-9]*-\d{3}$")
            self.assertIn(citation, keys, f"{citation} names no work unit")

    def test_the_documented_heading_form_is_three_digit(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("<EPIC>-<NNN> <title>", text)
        self.assertNotIn("<NN> <title>", text)

    def test_the_contract_does_not_contradict_the_open_p1104_gate(self) -> None:
        """The sentence the gate record forbids in five sibling documents."""
        text = CONTRACT.read_text(encoding="utf-8")
        for forbidden in (
            "remain blocked by `P-1104",
            "implementation remains unauthorized",
            "until the user explicitly authorizes implementation after P-1140F closes",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
