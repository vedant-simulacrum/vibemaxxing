"""Drift-injection tests for scripts/repository/validate_artifact_quarantine.py.

The validator exists because PF-001's original acceptance criterion — a grep that had
to return no unmarked mention — passed while `crates/vibeproof-core/README.md` was a
two-line stub. Absence satisfied it. So every test here injects a *removal* and asserts
the validator notices, which is the failure mode the grep could not see.
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
VALIDATOR = ROOT / "scripts" / "repository" / "validate_artifact_quarantine.py"


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_artifact_quarantine", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class QuarantineNoticeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        directory = Path(tempfile.mkdtemp(prefix="quarantine-"))
        self.addCleanup(shutil.rmtree, directory, True)
        self.root = directory / "repository"
        # Only the paths the record names are needed, but copying the tree keeps the
        # fixture honest: the test runs against the committed notices, not a mock.
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git", "node_modules", "target", ".venv", "artifacts"
            ),
        )
        self.authority = (
            self.root / "conformance" / "p1140f" / "artifact-authority-v1.json"
        )

    def run_validator(self):
        with (
            patch.object(self.validator, "ROOT", self.root),
            patch.object(self.validator, "AUTHORITY", self.authority),
        ):
            return self.validator.main()

    def edit_record(self, mutate) -> None:
        document = json.loads(self.authority.read_text(encoding="utf-8"))
        mutate(document)
        self.authority.write_text(json.dumps(document, indent=2), encoding="utf-8")

    def test_committed_state_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_the_stub_readme_that_started_this_fails(self) -> None:
        """The exact prior state: a README saying nothing, which the old grep allowed."""
        readme = self.root / "crates" / "vibeproof-core" / "README.md"
        readme.write_text(
            "# VibeProof core\n\nImplementation location. Follow `AGENTS.md`.\n",
            encoding="utf-8",
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("P-1140F-1", str(raised.exception))

    def test_a_notice_missing_one_prohibition_fails(self) -> None:
        """Understating the fence is the quiet failure, not deleting it outright."""
        readme = self.root / "crates" / "vibeproof-core" / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace("- verifier-appraisal\n", ""),
            encoding="utf-8",
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("verifier-appraisal", str(raised.exception))

    def test_a_notice_missing_one_incompatibility_fails(self) -> None:
        source = self.root / "apps" / "api" / "cmd" / "api" / "protocol_fixtures.go"
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "//   - does not verify COSE Sign1\n", ""
            ),
            encoding="utf-8",
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("COSE Sign1", str(raised.exception))

    def test_a_notice_that_does_not_name_its_normative_owner_fails(self) -> None:
        """Without the owner a reader knows it is wrong but not what it is wrong against."""
        readme = self.root / "crates" / "vibeproof-core" / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "packages/schemas/vibeproof-claim-v1.cddl", "the normative schema"
            ),
            encoding="utf-8",
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("normative owner", str(raised.exception))

    def test_a_json_artifact_stripped_of_its_block_fails(self) -> None:
        """JSON has no comments, so its notice is data and can be dropped silently."""
        vectors = self.root / "conformance" / "protocol" / "vibeproof-v1-vectors.json"
        document = json.loads(vectors.read_text(encoding="utf-8"))
        document.pop("_quarantine")
        vectors.write_text(json.dumps(document, indent=2), encoding="utf-8")

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("no quarantine block", str(raised.exception))

    def test_a_newly_quarantined_artifact_needs_a_notice(self) -> None:
        """Adding to the record without writing the notice is the likeliest drift."""
        self.edit_record(
            lambda d: d["artifacts"].append(
                {
                    "path": "crates/vibeproof-core/Cargo.toml",
                    "authority_class": "exploratory-prototype",
                    "evidence_ceiling": "fixture-consistent",
                    "normative_owner": "packages/schemas/vibeproof-claim-v1.cddl",
                    "known_incompatibilities": ["an incompatibility stated nowhere"],
                    "prohibited_uses": ["support-claim"],
                }
            )
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("an incompatibility stated nowhere", str(raised.exception))

    def test_emptying_the_record_fails_rather_than_passing_vacuously(self) -> None:
        """Zero quarantined artifacts would otherwise be a green run over nothing.

        This is the defect class the whole validator was written against: a number
        that improves when you delete what it counts.
        """
        self.edit_record(
            lambda d: d.update(
                artifacts=[
                    a for a in d["artifacts"] if "prototype" not in a["authority_class"]
                ]
            )
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("no artifact is classed as a prototype", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
