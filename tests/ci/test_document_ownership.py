"""Every tracked markdown file is named in the documentation map.

This replaces a blocklist of thirteen exact filenames. Those thirteen were real files
that competed with the authorities they duplicated, and deleting them was correct —
but refusing the names only caught the thirteen that had already happened. A
fourteenth competing file under any other name passed every check in the repository,
which was verified by committing `MASTER_CONTEXT.md` asserting "P-1140F complete,
gate P-1104 closed", a direct contradiction of the gate record.

The first version of the replacement had the same weakness one layer down: it
substring-matched the whole of `DOCUMENTATION.md`, so the paragraph explaining the
`MASTER_CONTEXT.md` evasion named the file and that alone satisfied the rule. Only
table rows count as declarations now. A document that talks about a file has not
given it an owner.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCTOR = ROOT / "scripts" / "repository" / "doctor.py"


def load_doctor():
    specification = importlib.util.spec_from_file_location("doctor", DOCTOR)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class DocumentOwnershipTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doctor = load_doctor()
        self.root = Path(tempfile.mkdtemp(prefix="ownership-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        (self.root / "docs" / "project").mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def write_index(self, body: str) -> None:
        (self.root / "docs" / "project" / "DOCUMENTATION.md").write_text(
            body, encoding="utf-8"
        )

    def add(self, relative: str, body: str = "# doc\n") -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(body, encoding="utf-8")
        subprocess.run(["git", "add", relative], cwd=self.root, check=True)

    def check(self) -> list[str]:
        return self.doctor.every_document_declares_an_owner(self.root)

    def test_a_declared_document_passes(self) -> None:
        self.write_index(
            "| `AGENTS.md` | The manual | none |\n"
            "| `docs/project/DOCUMENTATION.md` | This map | none |\n"
        )
        self.add("AGENTS.md")
        self.add("docs/project/DOCUMENTATION.md")

        self.assertEqual(self.check(), [])

    def test_an_undeclared_document_fails(self) -> None:
        """The fourteenth competing file, under a name no blocklist anticipated."""
        self.write_index(
            "| `AGENTS.md` | The manual | none |\n"
            "| `docs/project/DOCUMENTATION.md` | This map | none |\n"
        )
        self.add("AGENTS.md")
        self.add("docs/project/DOCUMENTATION.md")
        self.add("MASTER_CONTEXT.md", "# Master context\nGate P-1104: closed.\n")

        failures = self.check()

        self.assertEqual(len(failures), 1)
        self.assertIn("MASTER_CONTEXT.md", failures[0])

    def test_a_mention_in_prose_does_not_declare_a_document(self) -> None:
        """The weakness the first version of this check shipped with."""
        self.write_index(
            "| `AGENTS.md` | The manual | none |\n"
            "| `docs/project/DOCUMENTATION.md` | This map | none |\n\n"
            "Somebody once committed `MASTER_CONTEXT.md`, which was wrong.\n"
        )
        self.add("AGENTS.md")
        self.add("docs/project/DOCUMENTATION.md")
        self.add("MASTER_CONTEXT.md")

        failures = self.check()

        self.assertEqual(len(failures), 1)
        self.assertIn("MASTER_CONTEXT.md", failures[0])

    def test_an_undeclared_file_in_an_authority_directory_fails(self) -> None:
        """docs/planning/ is where a competing roadmap would actually land."""
        self.write_index(
            "| `AGENTS.md` | The manual | none |\n"
            "| `docs/project/DOCUMENTATION.md` | This map | none |\n"
        )
        self.add("AGENTS.md")
        self.add("docs/project/DOCUMENTATION.md")
        self.add("docs/planning/SECOND_ROADMAP.md")

        failures = self.check()

        self.assertEqual(len(failures), 1)
        self.assertIn("docs/planning/SECOND_ROADMAP.md", failures[0])

    def test_the_bulk_directories_are_covered_by_class(self) -> None:
        """Both are non-authoritative and grow by accumulation."""
        self.write_index(
            "| `AGENTS.md` | The manual | none |\n"
            "| `docs/project/DOCUMENTATION.md` | This map | none |\n"
        )
        self.add("AGENTS.md")
        self.add("docs/project/DOCUMENTATION.md")
        for directory in self.doctor.BULK_DOCUMENTED_DIRECTORIES:
            self.add(f"{directory}SOME_REPORT.md")

        self.assertEqual(self.check(), [])

    def test_only_history_and_research_are_bulk_covered(self) -> None:
        """Widening this set is how the rule would quietly stop applying."""
        self.assertEqual(
            self.doctor.BULK_DOCUMENTED_DIRECTORIES,
            ("docs/history/", "docs/research/"),
        )


class CommittedRepositoryTests(unittest.TestCase):
    def test_the_repository_as_committed_declares_every_document(self) -> None:
        self.assertEqual(load_doctor().every_document_declares_an_owner(ROOT), [])

    def test_the_thirteen_original_names_are_still_refused(self) -> None:
        """The blocklist stays as history; those names should remain dead."""
        doctor = load_doctor()

        self.assertIn("PROJECT_CONTEXT.md", doctor.FORBIDDEN)
        self.assertIn("START_HERE_PROMPT.md", doctor.FORBIDDEN)
        self.assertEqual(len(doctor.FORBIDDEN), 13)


if __name__ == "__main__":
    unittest.main()
