"""The Claude Code OTLP identity attributes must not survive either local stage.

These tests prove the validator catches drift in the D-099 strip list and in the
negative fixtures that back it. They do not prove any receiver implements the strip;
no receiver exists.
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
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
ADAPTER_ONE = ROOT / "conformance" / "adapters" / "claude-code-otel"
DISPOSITION = "otlp-attribute-disposition-v1.json"


def load_validator() -> object:
    specification = importlib.util.spec_from_file_location(
        "validate_planning_artifacts", VALIDATOR
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class AdapterOneBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()

    def _mutated(self, mutate) -> Path:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory, True)
        copy = directory / "claude-code-otel"
        shutil.copytree(ADAPTER_ONE, copy)
        mutate(copy)
        return copy

    def test_repository_head_passes(self) -> None:
        self.validator.validate_adapter_one_boundary()

    def test_strip_list_is_the_five_measured_identity_attributes(self) -> None:
        self.assertEqual(
            self.validator.ADAPTER_ONE_STRIP_LIST,
            (
                "organization.id",
                "user.account_id",
                "user.account_uuid",
                "user.email",
                "user.id",
            ),
        )

    def test_dropping_user_email_from_the_strip_list_fails(self) -> None:
        def mutate(copy: Path) -> None:
            record = json.loads((copy / DISPOSITION).read_text(encoding="utf-8"))
            for entry in record["attributes"]:
                if entry["attribute"] == "user.email":
                    entry["disposition"] = "allow"
            (copy / DISPOSITION).write_text(json.dumps(record), encoding="utf-8")

        with patch.object(self.validator, "ADAPTER_ONE", self._mutated(mutate)):
            with self.assertRaisesRegex(
                self.validator.ValidationFailure, "strip list drifted"
            ):
                self.validator.validate_adapter_one_boundary()

    def test_a_negative_fixture_that_stops_being_negative_fails(self) -> None:
        name = "source-observation.invalid-user-email.json"

        def mutate(copy: Path) -> None:
            record = json.loads((copy / name).read_text(encoding="utf-8"))
            record.pop("user.email")
            (copy / name).write_text(json.dumps(record), encoding="utf-8")

        with patch.object(self.validator, "ADAPTER_ONE", self._mutated(mutate)):
            with self.assertRaisesRegex(
                self.validator.ValidationFailure, "carries no stripped attribute"
            ):
                self.validator.validate_adapter_one_boundary()

    def test_permitting_a_partial_clean_path_fails(self) -> None:
        def mutate(copy: Path) -> None:
            record = json.loads((copy / DISPOSITION).read_text(encoding="utf-8"))
            record["partial_clean_permitted"] = True
            (copy / DISPOSITION).write_text(json.dumps(record), encoding="utf-8")

        with patch.object(self.validator, "ADAPTER_ONE", self._mutated(mutate)):
            with self.assertRaisesRegex(
                self.validator.ValidationFailure, "partial-clean path"
            ):
                self.validator.validate_adapter_one_boundary()

    def test_failing_open_on_an_unknown_attribute_fails(self) -> None:
        def mutate(copy: Path) -> None:
            record = json.loads((copy / DISPOSITION).read_text(encoding="utf-8"))
            record["unknown_attribute_disposition"] = "allow"
            (copy / DISPOSITION).write_text(json.dumps(record), encoding="utf-8")

        with patch.object(self.validator, "ADAPTER_ONE", self._mutated(mutate)):
            with self.assertRaisesRegex(self.validator.ValidationFailure, "fails open"):
                self.validator.validate_adapter_one_boundary()

    def test_every_strip_list_attribute_has_a_negative_fixture(self) -> None:
        record = json.loads((ADAPTER_ONE / DISPOSITION).read_text(encoding="utf-8"))
        covered: set[str] = set()
        for relative in record["negative_fixtures"]:
            instance = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            covered |= set(instance) & set(self.validator.ADAPTER_ONE_STRIP_LIST)
        self.assertEqual(covered, set(self.validator.ADAPTER_ONE_STRIP_LIST))


if __name__ == "__main__":
    unittest.main()
