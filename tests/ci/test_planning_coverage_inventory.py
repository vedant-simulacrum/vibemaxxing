"""Drift-injection tests for the inventory half of `validate_planning_coverage.py`.

`docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md` is declared by
`docs/project/DOCUMENTATION.md` as the authority that says which specification
family owns each machine contract, and until PF-034 nothing read it. `doctor.py`
asserted the file exists; `validate_planning_artifacts.py` asserted its rows are
unique and carry a declared status. Neither direction between the document and the
two trees it inventories was computed, so a citation could name a deleted path and —
the direction that matters — a new schema, registry or fixture could be shipped and
never appear in the file whose whole purpose is to name its owner.

These cases exist because a coverage check that cannot be shown to fail is
indistinguishable from a coverage check that reads nothing.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_coverage.py"
INVENTORY = ROOT / "docs" / "planning" / "SCHEMA_AND_INTERFACE_INVENTORY.md"


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_planning_coverage_under_test", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class InventoryCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.directory = Path(tempfile.mkdtemp(prefix="inventory-coverage-"))
        self.addCleanup(shutil.rmtree, self.directory, True)
        self.inventory = self.directory / INVENTORY.name
        shutil.copyfile(INVENTORY, self.inventory)
        self.files = self.validator.inventoried_files()

    # -- helpers ------------------------------------------------------------

    def run_check(self, *, text: str | None = None, files: list[str] | None = None):
        if text is not None:
            self.inventory.write_text(text, encoding="utf-8")
        errors: list[str] = []
        with (
            patch.object(self.validator, "INVENTORY", self.inventory),
            patch.object(
                self.validator,
                "inventoried_files",
                lambda: sorted(self.files if files is None else files),
            ),
        ):
            self.validator.check_inventory_coverage(errors)
        return errors

    def inventory_text(self) -> str:
        return self.inventory.read_text(encoding="utf-8")

    # -- the committed state ------------------------------------------------

    def test_the_committed_tree_is_covered_in_both_directions(self) -> None:
        self.assertEqual(self.run_check(), [])

    def test_the_tree_listing_is_not_empty(self) -> None:
        """A coverage check over nothing passes, which is the failure mode.

        Nine checks in this repository have been satisfied by emptiness. This one
        would be too: no files means no uncovered files.
        """
        self.assertGreater(len(self.files), 200)

    # -- direction: a shipped file with no owner ----------------------------

    def test_a_new_schema_no_row_names_fails(self) -> None:
        errors = self.run_check(
            files=[*self.files, "packages/schemas/unowned-contract-v1.json"]
        )
        self.assertTrue(
            any("unowned-contract-v1.json" in message for message in errors), errors
        )

    def test_a_new_file_in_an_unmanifested_conformance_directory_fails(self) -> None:
        """`p1140e`, `p1140f` and `planning` declare no suite manifest.

        Those three are the directories the manifest enumeration does not reach, so
        they are the ones this table has to own file by file.
        """
        errors = self.run_check(files=[*self.files, "conformance/p1140f/unowned.json"])
        self.assertTrue(
            any("conformance/p1140f/unowned.json" in message for message in errors),
            errors,
        )

    def test_a_new_file_in_a_manifested_suite_is_delegated_not_ignored(self) -> None:
        """The suite manifests enumerate their own directories bidirectionally.

        This asserts the delegation rather than the silence: the coverage check does
        not report the file, and `validate_conformance_manifests` — the delegate
        named in the validator — is what refuses it.
        """
        errors = self.run_check(files=[*self.files, "conformance/social/unowned.json"])
        self.assertEqual(errors, [])
        delegate = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
        self.assertTrue(
            "the suite holds files no case, authority or tooling entry "
            in delegate.read_text(encoding="utf-8"),
            "the delegate no longer refuses an unnamed file in a manifested suite",
        )

    def test_citing_the_tree_root_does_not_cover_the_tree(self) -> None:
        """The sentence naming the trees must not satisfy the rule it states."""
        text = self.inventory_text() + "\n\n`packages/schemas/` `conformance/`\n"
        errors = self.run_check(
            text=text, files=[*self.files, "packages/schemas/unowned-contract-v1.json"]
        )
        self.assertTrue(
            any("unowned-contract-v1.json" in message for message in errors), errors
        )

    def test_citing_a_directory_does_not_cover_its_contents(self) -> None:
        text = self.inventory_text() + "\n\n`conformance/p1140f/`\n"
        errors = self.run_check(
            text=text, files=[*self.files, "conformance/p1140f/unowned.json"]
        )
        self.assertTrue(
            any("conformance/p1140f/unowned.json" in message for message in errors),
            errors,
        )

    # -- direction: a row naming nothing ------------------------------------

    def test_a_citation_that_resolves_to_nothing_fails(self) -> None:
        # Assembled rather than written out, because a backticked path in this file
        # is a citation like any other and `validate_cross_references.py` reads it.
        deleted = "packages/schemas/" + "deleted-contract.json"
        text = self.inventory_text() + f"\n\n`{deleted}`\n"
        errors = self.run_check(text=text)
        self.assertTrue(
            any("deleted-contract.json" in message for message in errors), errors
        )

    def test_a_pattern_that_matches_nothing_fails(self) -> None:
        pattern = "conformance/evidence/" + "nothing.*.json"
        text = self.inventory_text() + f"\n\n`{pattern}`\n"
        errors = self.run_check(text=text)
        self.assertTrue(any("matches no file" in message for message in errors), errors)

    def test_a_directory_citation_that_does_not_exist_fails(self) -> None:
        text = self.inventory_text() + "\n\n`conformance/imaginary-suite/`\n"
        errors = self.run_check(text=text)
        self.assertTrue(any("imaginary-suite" in message for message in errors), errors)

    def test_a_placeholder_is_not_resolved(self) -> None:
        """`conformance/<suite>/` is a shape. Resolving it would ban the sentence."""
        text = self.inventory_text() + "\n\n`conformance/<suite>/manifest.json`\n"
        self.assertEqual(self.run_check(text=text), [])

    # -- delegation ---------------------------------------------------------

    def test_a_delegation_whose_delegate_is_gone_fails(self) -> None:
        delegated = (
            (
                "packages/schemas/examples/",
                "scripts/repository/validate_planning_artifacts.py",
                "def a_function_that_was_deleted(",
            ),
        )
        errors: list[str] = []
        with (
            patch.object(self.validator, "INVENTORY", self.inventory),
            patch.object(
                self.validator, "inventoried_files", lambda: sorted(self.files)
            ),
            patch.object(self.validator, "DELEGATED_COVERAGE", delegated),
        ):
            self.validator.check_inventory_coverage(errors)
        self.assertTrue(
            any("outlived the check" in message for message in errors), errors
        )

    def test_every_committed_delegate_exists(self) -> None:
        for scope, delegate, symbol in self.validator.DELEGATED_COVERAGE:
            path = ROOT / delegate
            self.assertTrue(path.is_file(), scope)
            self.assertIn(symbol, path.read_text(encoding="utf-8"), scope)

    # -- maturity -----------------------------------------------------------

    def test_a_missing_maturity_statement_fails(self) -> None:
        """The replacement for `grep -in 'closed-world|complete'`.

        That clause could not fail on a document where the words had never
        appeared, which is the shape PF-029 found: an absence satisfied by
        emptiness. The statement is required in exact literals as well.
        """
        for literal in self.validator.INVENTORY_MATURITY_LITERALS:
            with self.subTest(literal=literal[:40]):
                text = self.inventory_text().replace(literal, "")
                errors = self.run_check(text=text)
                self.assertTrue(
                    any("maturity statement" in message for message in errors), errors
                )
                shutil.copyfile(INVENTORY, self.inventory)

    def test_every_forbidden_claim_fires(self) -> None:
        """A ban list nothing has ever tripped is not a control."""
        for phrase in self.validator.INVENTORY_FORBIDDEN_CLAIMS:
            with self.subTest(phrase=phrase):
                text = self.inventory_text() + f"\n\nThis inventory is {phrase}.\n"
                errors = self.run_check(text=text)
                self.assertTrue(
                    any(phrase in message for message in errors), (phrase, errors)
                )
                shutil.copyfile(INVENTORY, self.inventory)

    def test_the_disclaimer_may_name_the_claims_it_disclaims(self) -> None:
        """The maturity statement says `launch-ready`, which is also banned.

        Scanning the whole file would make the required statement illegal, so the
        scan runs over the text with the statement removed. This asserts that the
        exemption is exactly that statement and does not leak.
        """
        self.assertEqual(self.run_check(), [])
        self.assertTrue(
            any(
                phrase in literal
                for phrase in self.validator.INVENTORY_FORBIDDEN_CLAIMS
                for literal in self.validator.INVENTORY_MATURITY_LITERALS
            ),
            "the exemption is untested: no forbidden phrase appears in the statement",
        )


if __name__ == "__main__":
    unittest.main()
