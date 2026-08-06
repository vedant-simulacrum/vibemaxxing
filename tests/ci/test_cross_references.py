"""Drift-injection tests for scripts/repository/validate_cross_references.py.

Every reference class gets two tests: one that injects a reference which resolves
nowhere and asserts the validator fails, and one that writes the legitimate prose
shape most likely to be misread and asserts it does not. A validator that cannot
be shown to fire is not evidence, and one that fires on ordinary prose is worse
than none.

The synthetic repository built in `setUp` is deliberately tiny: five owners and one
document under test. The real repository is exercised separately, against the
recorded set of known gaps.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_cross_references.py"

SAMPLE = "docs/sample/SAMPLE.md"

# The dangling references the repository knowingly carries at this head. Each is
# recorded rather than suppressed, so this test fails the moment one is repaired or
# a new one appears.
# Empty on purpose. Every cross-reference in the repository resolves; the last
# recorded gap, ADR-015, closed when ADR-015-SESSION_AUTHENTICATION.md was authored.
# A new entry here needs a written reason, not just a passing suite.
KNOWN_GAPS: set[tuple[str, str, str]] = set()


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_cross_references", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


OPENAPI = {
    "openapi": "3.1.0",
    "paths": {
        "/boards": {
            "get": {
                "operationId": "listBoards",
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Board"}
                            }
                        }
                    }
                },
            }
        }
    },
    "components": {"schemas": {"Board": {"type": "object"}}},
}


class CrossReferenceValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.root = Path(tempfile.mkdtemp(prefix="cross-reference-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.write(
            "docs/planning/DECISION_REGISTER.md",
            "| ID | Decision | Status | Reversal |\n"
            "|---|---|---|---|\n"
            "| D-001 | Greenfield reset | accepted | explicit product reset |\n"
            "| D-012 | Token Burn is the raw metric | accepted | none |\n",
        )
        self.write(
            "conformance/p1140f/semantic-findings-v1.json",
            json.dumps({"findings": [{"finding_id": "SR-005"}]}),
        )
        self.write("docs/decisions/ADR-001-LOCAL-FIRST.md", "# ADR-001\n")
        self.write(
            "docs/planning/TASK_CATALOG.md",
            "P-1104 enters the implementation phase; P-1140F is in progress.\n",
        )
        self.write(
            "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
            "### PF-001 — Quarantine the shadow protocol\n\n### P-008 — Rotate keys\n",
        )
        self.write("packages/schemas/openapi-v1.yaml", json.dumps(OPENAPI, indent=2))
        self.write("docs/security/REAL.md", "# A real document\n")

    # -- harness ---------------------------------------------------------------------

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def scan(self, sample: str, extra: dict[str, str] | None = None):
        """Scan a synthetic repository containing exactly `sample` and `extra`."""
        self.write(SAMPLE, sample)
        files = [SAMPLE, *(extra or {})]
        for relative, text in (extra or {}).items():
            self.write(relative, text)
        overrides = {
            "ROOT": self.root,
            "DECISION_REGISTER": self.root / "docs/planning/DECISION_REGISTER.md",
            "SEMANTIC_FINDINGS": self.root
            / "conformance/p1140f/semantic-findings-v1.json",
            "ADR_DIRECTORY": self.root / "docs/decisions",
            "TASK_CATALOG": self.root / "docs/planning/TASK_CATALOG.md",
            "WORK_BREAKDOWN": self.root
            / "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
            "OPENAPI": self.root / "packages/schemas/openapi-v1.yaml",
        }
        with contextlib.ExitStack() as stack:
            for name, value in overrides.items():
                stack.enter_context(patch.object(self.validator, name, value))
            return self.validator.scan(files)

    def dangles(self, sample: str, extra: dict[str, str] | None = None):
        return [(d.kind, d.token) for d in self.scan(sample, extra).dangles]

    def assertClean(self, sample: str, extra: dict[str, str] | None = None) -> None:
        found = self.dangles(sample, extra)
        self.assertEqual(found, [], f"false positive on: {sample!r}")

    # -- the repository as committed --------------------------------------------------

    def test_repository_carries_exactly_the_recorded_known_gaps(self) -> None:
        report = self.validator.scan()
        found = {(d.kind, d.token, d.path) for d in report.dangles}
        self.assertEqual(
            found,
            KNOWN_GAPS,
            "the repository's dangling-reference set changed; repair it or update "
            "KNOWN_GAPS with the reason",
        )

    def test_a_superseded_decision_cited_as_current_is_reported(self) -> None:
        """Stale authority resolves, which is what makes it worse than a dangle.

        Six live documents were reasoning from a spending ceiling that had been
        superseded, and one concluded a recovery objective was unaffordable
        when it had become merely unbuilt. Every one of those citations
        resolved to a real register row.
        """
        superseded = self.validator.superseded_decisions()
        self.assertTrue(superseded, "the register records no superseded decision")
        identifier = sorted(superseded)[0]

        document = ROOT / "docs" / "operations" / "SLOS_AND_ALERTS.md"
        original = document.read_text(encoding="utf-8")
        document.write_text(f"Spend is capped by {identifier}.\n" + original, "utf-8")
        try:
            found = self.validator.report_superseded_citations()
        finally:
            document.write_text(original, encoding="utf-8")

        self.assertTrue(any(d.token == identifier for d in found))

    def test_a_citation_marked_as_past_is_not_reported(self) -> None:
        """Recording history is how a document stays honest, not a defect."""
        identifier = sorted(self.validator.superseded_decisions())[0]
        document = ROOT / "docs" / "operations" / "SLOS_AND_ALERTS.md"
        original = document.read_text(encoding="utf-8")
        document.write_text(
            f"Spend was capped by {identifier}, now superseded.\n" + original, "utf-8"
        )
        try:
            found = self.validator.report_superseded_citations()
        finally:
            document.write_text(original, encoding="utf-8")

        self.assertEqual([d for d in found if d.token == identifier], [])

    def test_archival_trees_are_out_of_scope(self) -> None:
        """`docs/history/` cites superseded decisions because that is its job.

        Checking it would need an exemption list longer than the rule, which is
        the failure mode this check exists to prevent.
        """
        identifier = sorted(self.validator.superseded_decisions())[0]
        document = ROOT / "docs" / "history" / "FINAL_PLANNING_EXIT_AUDIT.md"
        original = document.read_text(encoding="utf-8")
        document.write_text(original + f"\n{identifier} caps spend.\n", "utf-8")
        try:
            found = self.validator.report_superseded_citations()
        finally:
            document.write_text(original, encoding="utf-8")

        self.assertEqual([d for d in found if d.token == identifier], [])

    def test_clean_repository_passes_in_both_modes(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            strict = self.validator.main([])
            report = self.validator.main(["--report"])
        self.assertEqual(strict, 0)
        self.assertEqual(report, 0)
        self.assertIn("cross-reference validation: PASS", stdout.getvalue())
        self.assertIn("cross-reference report:", stdout.getvalue())

    def test_strict_mode_exits_non_zero_when_a_dangle_exists(self) -> None:
        """The exit-code contract, independent of the repository's own state.

        Every other test here proves detection; this one proves that a detected
        dangle actually turns the process red, so a clean repository can never
        mask a broken strict mode.
        """
        planted = self.validator.Report(
            dangles=[
                self.validator.Dangle(
                    kind="decision",
                    token="D-900",
                    path="docs/planning/DECISION_REGISTER.md",
                    line=1,
                )
            ],
            scanned_files=1,
            counts={"decision": 1},
        )
        original = self.validator.scan
        self.validator.scan = lambda files=None: planted
        try:
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                strict = self.validator.main([])
                report = self.validator.main(["--report"])
        finally:
            self.validator.scan = original
        self.assertEqual(strict, 1)
        self.assertEqual(report, 0, "--report never fails the build")
        self.assertIn("cross-reference validation: FAIL", stderr.getvalue())
        self.assertIn("D-900", stderr.getvalue() + stdout.getvalue())

    def test_every_class_is_rendered_in_report_mode(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.validator.main(["--report"])
        output = stdout.getvalue()
        for kind in self.validator.CLASS_ORDER:
            self.assertIn(f"## {kind}:", output)

    # -- one failing test per reference class -----------------------------------------

    def test_unknown_decision_fails(self) -> None:
        self.assertEqual(
            self.dangles("Recorded under D-900 in the register.\n"),
            [("decision", "D-900")],
        )

    def test_unknown_finding_fails(self) -> None:
        self.assertEqual(
            self.dangles("SR-900 remains open.\n"), [("finding", "SR-900")]
        )

    def test_unknown_adr_fails(self) -> None:
        self.assertEqual(
            self.dangles("See ADR-900 for the rationale.\n"), [("adr", "ADR-900")]
        )

    def test_unknown_program_fails(self) -> None:
        self.assertEqual(
            self.dangles("P-9999 blocks the release.\n"), [("program", "P-9999")]
        )

    def test_unknown_work_unit_fails(self) -> None:
        self.assertEqual(
            self.dangles("Delivered by PF-900 and N-900.\n"),
            [("work-unit", "PF-900"), ("work-unit", "N-900")],
        )

    def test_a_two_digit_work_unit_citation_can_never_resolve(self) -> None:
        # The breakdown numbers every heading with three digits, so the superseded
        # two-digit numbering is a defect by construction rather than a lookup miss.
        self.assertEqual(
            self.dangles("Traced to F-01 and O-04.\n"),
            [("work-unit", "F-01"), ("work-unit", "O-04")],
        )

    def test_prefixes_that_were_never_defined_are_still_recognised(self) -> None:
        # `I-`, `U-` and `PL-` name nothing in the breakdown. They must be parsed as
        # work-unit citations, otherwise they dangle invisibly instead of failing.
        self.assertEqual(
            self.dangles("Covered by I-01, U-06 and PL-02.\n"),
            [("work-unit", "I-01"), ("work-unit", "U-06"), ("work-unit", "PL-02")],
        )

    def test_missing_path_fails_in_a_link_and_in_inline_code(self) -> None:
        self.assertEqual(
            self.dangles(
                "See [the model](../security/GONE.md) and `docs/security/GONE.md`.\n"
            ),
            [("path", "../security/GONE.md"), ("path", "docs/security/GONE.md")],
        )

    def test_unresolved_json_pointer_fails(self) -> None:
        broken = json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "properties": {"board": {"$ref": "#/$defs/Missing"}},
                "$defs": {"Present": {"type": "object"}},
            },
            indent=2,
        )
        self.assertEqual(
            self.dangles("", {"packages/schemas/x-v1.schema.json": broken}),
            [("json-ref", "#/$defs/Missing")],
        )

    def test_missing_external_ref_target_fails(self) -> None:
        broken = json.dumps({"properties": {"a": {"$ref": "absent-v1.schema.json"}}})
        self.assertEqual(
            self.dangles("", {"packages/schemas/y-v1.schema.json": broken}),
            [("json-ref", "absent-v1.schema.json")],
        )

    def test_unknown_operation_id_fails(self) -> None:
        matrix = json.dumps({"api_operations": ["listBoards", "listGhosts"]}, indent=2)
        self.assertEqual(
            self.dangles("", {"conformance/p1140e/validation-matrix-v1.json": matrix}),
            [("operation", "listGhosts")],
        )

    def test_operation_id_named_in_prose_must_exist(self) -> None:
        self.assertEqual(
            self.dangles("The operationId `listGhosts` returns the board.\n"),
            [("operation", "listGhosts")],
        )

    def test_non_authority_references_always_fail(self) -> None:
        self.assertEqual(
            self.dangles("Tracked as AF-014 in `.context/audit/notes.md`.\n"),
            [("non-authority", "AF-014"), ("non-authority", ".context/audit/notes.md")],
        )

    # -- legitimate prose must not fire ----------------------------------------------

    def test_ordinary_prose_citations_resolve(self) -> None:
        self.assertClean(
            "The D-012 decision makes Token Burn the raw metric, closing SR-005 for\n"
            "PF-001 and P-008 under P-1104, as ADR-001 records. See\n"
            "[the model](../security/REAL.md) and `docs/security/REAL.md`.\n"
        )

    def test_a_pattern_definition_block_is_not_a_citation(self) -> None:
        self.assertClean(
            "The identifier grammar is:\n\n"
            "```\n"
            "decision  := D-[0-9]{3}\n"
            "work unit := (PF|F|P)-[0-9]{3}   # for example PF-900\n"
            "```\n"
        )

    def test_a_regex_literal_on_a_prose_line_is_not_a_citation(self) -> None:
        self.assertClean(
            "The generator rejects two-digit keys because its own `[A-Z]+-\\d{3}` "
            "pattern, unlike D-900, requires three.\n"
        )

    def test_three_digits_and_four_digits_are_different_classes(self) -> None:
        # P-1104 is a program and must not be read as work unit P-110; P-008 is a
        # work unit and must not be read as a program.
        report = self.scan("P-1104 gates P-008, and P-1140F-1 is in progress.\n")
        self.assertEqual(report.dangles, [])
        self.assertEqual(report.counts["program"], 2)
        self.assertEqual(report.counts["work-unit"], 1)

    def test_an_embedded_identifier_is_not_a_separate_citation(self) -> None:
        # ADR-001-LOCAL-FIRST.md must not also yield decision D-001 or work unit
        # R-001 from inside the filename.
        report = self.scan("Recorded in `docs/decisions/ADR-001-LOCAL-FIRST.md`.\n")
        self.assertEqual(report.dangles, [])
        self.assertEqual(report.counts["adr"], 1)
        self.assertEqual(report.counts.get("decision", 0), 0)
        self.assertEqual(report.counts.get("work-unit", 0), 0)

    def test_the_synthetic_sentinel_is_never_resolved(self) -> None:
        report = self.scan("Drift fixture SR-999 and D-999 and PF-999.\n")
        self.assertEqual(report.dangles, [])
        self.assertEqual(report.counts["finding"], 1)

    def test_a_planned_marker_binds_only_to_the_token_it_follows(self) -> None:
        # One planned deliverable must not excuse a stale sibling beside it.
        self.assertEqual(
            self.dangles(
                "Files: `packages/schemas/new-v1.json` (new), `docs/security/GONE.md`\n"
            ),
            [("path", "docs/security/GONE.md")],
        )
        self.assertClean(
            "Files: `packages/schemas/new-v1.json` (new), `docs/security/REAL.md`\n"
        )

    def test_a_retired_marker_exempts_the_sentence_that_carries_it(self) -> None:
        self.assertClean(
            "`docs/design/design.md` was merged into `docs/security/REAL.md`.\n"
        )
        self.assertEqual(
            self.dangles("`docs/design/design.md` is the owner.\n"),
            [("path", "docs/design/design.md")],
        )

    def test_media_types_urls_and_versions_are_not_paths(self) -> None:
        self.assertClean(
            "Requests are `application/json` over `https://api.example.dev/v1`, "
            "pinned at `1.0.0`, built from `Cargo.toml`.\n"
        )

    def test_a_path_resolves_against_any_ancestor_of_the_citing_file(self) -> None:
        # docs/sample/SAMPLE.md may write `security/REAL.md` for docs/security/REAL.md.
        self.assertClean("Anti-cheat controls live in `security/REAL.md`.\n")

    def test_an_anchor_or_line_citation_does_not_break_resolution(self) -> None:
        self.assertClean(
            "See `docs/security/REAL.md` and [the section](../security/REAL.md#scope) "
            "and `docs/security/REAL.md:63-66`.\n"
        )

    # -- scope rules -----------------------------------------------------------------

    def test_scan_scope_is_the_declared_roots_plus_root_markdown(self) -> None:
        in_scope = self.validator.in_scan_scope
        self.assertTrue(in_scope("docs/project/PROJECT.md"))
        self.assertTrue(in_scope("packages/schemas/openapi-v1.yaml"))
        self.assertTrue(in_scope("conformance/p1140f/REPAIR_HEAD_REVIEW.md"))
        self.assertTrue(in_scope("README.md"))
        self.assertFalse(in_scope("apps/web/app/page.tsx"))
        self.assertFalse(in_scope("assets/brand/logo.svg"))
        self.assertFalse(in_scope("Cargo.toml"))

    def test_only_the_two_pattern_holding_files_are_excluded(self) -> None:
        self.assertEqual(
            self.validator.EXCLUDED_FILES,
            frozenset(
                {
                    "scripts/repository/validate_cross_references.py",
                    "tests/ci/test_cross_references.py",
                }
            ),
        )
        for name in self.validator.EXCLUDED_FILES:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_a_missing_owner_is_an_error_not_a_pass(self) -> None:
        (self.root / "docs/decisions/ADR-001-LOCAL-FIRST.md").unlink()
        with self.assertRaises(self.validator.Failure):
            self.scan("nothing to see\n")


if __name__ == "__main__":
    unittest.main()
