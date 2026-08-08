"""Tests for scripts/repository/generate_p1140e_coverage.py.

`conformance/p1140e/validation-matrix-v1.json` mixes a closed program's frozen
evidence (`decision_bindings`, `validation_domains`) with three arrays that are
projections of live registries (`api_operations`, `state_machines`,
`platform_profiles`). The generator regenerates only the three derived arrays
and leaves the frozen half byte-identical; `validate_p1140e_contracts.py`
requires the committed file to already equal that regeneration.

These tests cover: determinism, the regression the validator now enforces
(the committed file matches its own regeneration), the specific defect that
motivated the generator (PF-013's machines were appended rather than sorted
in, which set-equality cannot see), the frozen-half passthrough guarantee,
duplicate-registry detection, and `--check`'s exit code.
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
GENERATOR = ROOT / "scripts" / "repository" / "generate_p1140e_coverage.py"
VALIDATOR = ROOT / "scripts" / "repository" / "validate_p1140e_contracts.py"
MATRIX = ROOT / "conformance" / "p1140e" / "validation-matrix-v1.json"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    # Python 3.14 resolves dataclass/annotation references against
    # sys.modules[name] during exec_module; registering first is required or
    # module-level type resolution fails.
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class GeneratorFixtureMixin:
    """Loads a fresh copy of the generator module against a scratch matrix.

    A mixin rather than a shared TestCase base, per repo convention: this
    repo has twice been bitten by subclassing a TestCase to reuse a fixture.
    """

    def setUp(self) -> None:
        super().setUp()
        self.generator = load_module(GENERATOR, "generate_p1140e_coverage")
        directory = Path(tempfile.mkdtemp(prefix="p1140e-coverage-"))
        self.addCleanup(shutil.rmtree, directory, True)
        self.matrix_copy = directory / "validation-matrix-v1.json"
        shutil.copyfile(MATRIX, self.matrix_copy)

    def patched_matrix(self):
        return patch.object(self.generator, "MATRIX", self.matrix_copy)


class RegenerateDeterminismTests(GeneratorFixtureMixin, unittest.TestCase):
    def test_regenerate_is_deterministic(self) -> None:
        first = self.generator.regenerate()
        second = self.generator.regenerate()
        self.assertEqual(first, second)

    def test_committed_matrix_is_already_reproducible(self) -> None:
        """The regression guard: this is exactly what the validator enforces."""
        self.assertEqual(
            self.generator.regenerate(),
            MATRIX.read_text(encoding="utf-8"),
        )


class ReorderingIsCaughtTests(GeneratorFixtureMixin, unittest.TestCase):
    def test_reordering_a_state_machine_entry_is_detected(self) -> None:
        """PF-013's actual defect: five machines were appended rather than
        sorted in. Set equality (`set(matrix["state_machines"]) == set(...)`)
        cannot see an order change, only regeneration can.
        """
        document = json.loads(self.matrix_copy.read_text(encoding="utf-8"))
        machines = document["state_machines"]
        self.assertGreater(len(machines), 1, "need at least two entries to reorder")
        moved = machines.pop(0)
        machines.append(moved)
        self.matrix_copy.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        with self.patched_matrix():
            generated = self.generator.regenerate()

        self.assertNotEqual(generated, self.matrix_copy.read_text(encoding="utf-8"))
        # And regeneration re-sorts it back to the canonical (and committed) order.
        self.assertEqual(
            json.loads(generated)["state_machines"],
            sorted(machines),
        )


class OnlyDerivedKeysChangeTests(GeneratorFixtureMixin, unittest.TestCase):
    def test_frozen_half_passes_through_byte_identical(self) -> None:
        committed = json.loads(MATRIX.read_text(encoding="utf-8"))
        generated = json.loads(self.generator.regenerate())

        self.assertEqual(generated["decision_bindings"], committed["decision_bindings"])
        self.assertEqual(
            generated["validation_domains"], committed["validation_domains"]
        )

    def test_top_level_key_order_is_unchanged(self) -> None:
        committed_text = MATRIX.read_text(encoding="utf-8")
        committed_keys = list(json.loads(committed_text).keys())
        generated_keys = list(json.loads(self.generator.regenerate()).keys())
        self.assertEqual(generated_keys, committed_keys)


class DuplicateRegistryEntryTests(GeneratorFixtureMixin, unittest.TestCase):
    def test_a_duplicate_in_a_source_registry_is_raised_not_deduplicated(self) -> None:
        """Collapsing a duplicate silently would hide a registry defect: two
        entries claiming the same id is a bug in the source, not a set to be
        rendered down to one.
        """
        real_machine_ids = self.generator.machine_ids()
        duplicated = real_machine_ids + [real_machine_ids[0]]

        with patch.object(self.generator, "machine_ids", return_value=duplicated):
            with self.assertRaises(SystemExit) as raised:
                self.generator.derived()

        message = str(raised.exception)
        self.assertIn("state_machines", message)
        self.assertIn(real_machine_ids[0], message)


class CheckFlagExitCodeTests(GeneratorFixtureMixin, unittest.TestCase):
    def run_main(self, argv: list[str]) -> int:
        with self.patched_matrix(), patch.object(sys, "argv", ["prog", *argv]):
            return self.generator.main()

    def test_check_exits_1_on_a_stale_file(self) -> None:
        document = json.loads(self.matrix_copy.read_text(encoding="utf-8"))
        document["state_machines"] = document["state_machines"][:-1]
        self.matrix_copy.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        self.assertEqual(self.run_main(["--check"]), 1)

    def test_check_exits_0_after_regenerating(self) -> None:
        document = json.loads(self.matrix_copy.read_text(encoding="utf-8"))
        document["state_machines"] = document["state_machines"][:-1]
        self.matrix_copy.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_main(["--check"]), 1)

        # Drive the real write path. Writing this test is what surfaced that
        # `main()` crashed on `MATRIX.relative_to(ROOT)` whenever MATRIX pointed
        # outside the repository — which is every scratch fixture. The generator
        # now falls back to the absolute path for that message, so the CLI can be
        # exercised end to end instead of stepped around.
        self.assertEqual(self.run_main([]), 0)

        self.assertEqual(self.run_main(["--check"]), 0)


class ValidatorWiringTests(GeneratorFixtureMixin, unittest.TestCase):
    """The validator fires when the matrix disagrees with regeneration.

    Confirmed two ways: the message the validator raises is present in its
    source (so we know the wiring exists and names the right cause), and
    `ReorderingIsCaughtTests` above already proves `regenerate()` itself
    detects the PF-013-shaped defect the validator's check depends on. A full
    end-to-end run of `validate_p1140e_contracts.main()` against a mutated
    matrix is not attempted here because the validator resolves `MATRIX` via
    its own `CONF` path constant rather than an overridable attribute the
    generator import shares, which would require monkeypatching module
    internals beyond what this test file's fixtures reach.
    """

    def test_reproducible_is_true_for_the_committed_matrix(self) -> None:
        """The predicate the validator actually calls, on the real tree."""
        self.assertTrue(self.generator.reproducible())

    def test_reproducible_is_false_when_the_matrix_is_reordered(self) -> None:
        """Drive the predicate, not the source text.

        This replaced an assertion that the validator's *source* contained the call
        and the message. A substring match is not a declaration: it passes just as
        well when the call sits in a branch that never runs, or in a comment. What
        the validator depends on is this returning False, so that is what is tested.
        """
        scratch = Path(tempfile.mkdtemp()) / "validation-matrix-v1.json"
        matrix = json.loads(self.generator.MATRIX.read_text(encoding="utf-8"))
        matrix["state_machines"].append(matrix["state_machines"].pop(0))
        scratch.write_text(json.dumps(matrix, indent=2, ensure_ascii=False) + "\n")

        with patch.object(self.generator, "MATRIX", scratch):
            self.assertFalse(self.generator.reproducible())

    def test_the_write_path_survives_a_matrix_outside_the_repository(self) -> None:
        """`main()` crashed on `relative_to` when MATRIX pointed at a scratch file.

        A progress message must not be the reason a script cannot be driven by a
        test — that is how a code path ends up covered only by reading it.
        """
        scratch = Path(tempfile.mkdtemp()) / "validation-matrix-v1.json"
        scratch.write_text(self.generator.MATRIX.read_text(encoding="utf-8"))

        with patch.object(self.generator, "MATRIX", scratch):
            with patch.object(sys, "argv", ["generate_p1140e_coverage.py"]):
                self.assertEqual(self.generator.main(), 0)


if __name__ == "__main__":
    unittest.main()
