"""An observation must say which execution it is about, who read it, and how.

PF-017. `validate_source_observation_identity` computes each of its claims from two
artifacts rather than restating one of them, and `validate_schema_example_coverage`
reads the example directory rather than a list of files. These tests inject the drift
each check exists to catch and assert the exact substring it fails with.

Three of them are the near-miss class this repository keeps hitting. A vocabulary
missing one value in one of five artifacts - `acp`, absent only from the observation -
is invisible to any check that reads one artifact. A field named `collector_instance`
where the forbidden list says `collector_instance_id` overlaps with nothing, so a
subset test finds no leak and reports success. And an example directory checked against
a list rather than against itself gets better when a failing file is deleted.

Nothing here is evidence that an adapter emits any of these fields. No adapter exists.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
VOCABULARIES = ROOT / "scripts" / "repository" / "validate_state_vocabularies.py"
EXAMPLES = ROOT / "packages" / "schemas" / "examples"

OBSERVATION = "source-observation.schema.json"
EVENT = "normalized-event.schema.json"
RECEIPT = "source-receipt-v1.schema.json"
BINDING = "producer-accounting-binding-v1.schema.json"
EQUIVALENCE = "observer-equivalence-v1.json"
MACHINES = "state-machine-registry-v1.json"


def load_module(path: Path, name: str) -> object:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class MutatedRecords:
    """Run a validator function with one record rewritten in memory.

    A mixin rather than a TestCase base: it owns the loader patch and nothing else, so
    a test class combines it with `unittest.TestCase` instead of inheriting from a
    class that is not itself a test.
    """

    validator: object

    def install(self) -> None:
        self.validator = load_module(VALIDATOR, "validate_planning_artifacts")
        self._load_json = self.validator.load_json
        self.addCleanup(setattr, self.validator, "load_json", self._load_json)

    def run_with(self, mutate, check=None) -> None:
        def loader(path):
            return mutate(Path(path), copy.deepcopy(self._load_json(path)))

        self.validator.load_json = loader
        (check or self.validator.validate_source_observation_identity)()

    def rewrite(self, filename: str, mutate):
        def loader(path: Path, record):
            if path.name == filename:
                mutate(record)
            return record

        return loader

    def expect(self, filename: str, mutate, message: str, check=None) -> None:
        with self.assertRaisesRegex(self.validator.ValidationFailure, message):
            self.run_with(self.rewrite(filename, mutate), check)


class ObservationIdentityTests(MutatedRecords, unittest.TestCase):
    def setUp(self) -> None:
        self.install()

    def test_repository_head_passes(self) -> None:
        self.validator.validate_source_observation_identity()

    def test_dropping_acp_from_one_mode_vocabulary_fails(self) -> None:
        """The defect PF-017 found: four artifacts had `acp` and the observation did not."""

        def mutate(record):
            record["properties"]["execution_mode"]["enum"] = [
                value
                for value in record["properties"]["execution_mode"]["enum"]
                if value != "acp"
            ]

        self.expect(OBSERVATION, mutate, r"is not the one observation-mode vocabulary")

    def test_an_unranked_capture_mode_on_the_event_fails(self) -> None:
        def mutate(record):
            record["properties"]["certification"]["properties"]["capture_mode"][
                "enum"
            ].append("carrier-pigeon")

        self.expect(EVENT, mutate, "is not the one observation-mode vocabulary")

    def test_a_certification_state_the_machine_cannot_reach_fails(self) -> None:
        """`revoked` was in two schemas and in no transition of the machine."""

        def mutate(record):
            record["properties"]["certification"]["properties"]["state"]["enum"].append(
                "revoked"
            )

        self.expect(RECEIPT, mutate, "source-certification machine's")

    def test_a_certification_state_the_machine_gained_fails(self) -> None:
        def mutate(record):
            machine = next(
                item
                for item in record["machines"]
                if item["machine_id"] == "source-certification"
            )
            machine["states"].append("quarantined")

        self.expect(MACHINES, mutate, r"missing=\['quarantined'\]")

    def test_an_event_that_does_not_require_the_operation_fails(self) -> None:
        def mutate(record):
            record["required"] = [
                name for name in record["required"] if name != "operation"
            ]

        self.expect(EVENT, mutate, "does not require operation")

    def test_an_observation_that_does_not_require_the_reading_fails(self) -> None:
        def mutate(record):
            record["required"] = [
                name for name in record["required"] if name != "reading"
            ]

        self.expect(OBSERVATION, mutate, "does not require reading")

    def test_an_observer_field_in_a_commitment_preimage_fails(self) -> None:
        def mutate(record):
            strong = next(
                item
                for item in record["equivalence_classes"]
                if item["class"] == "strong"
            )
            strong["preimage_inputs"].append("collector_instance_id")

        self.expect(EQUIVALENCE, mutate, "commitment preimage input")

    def test_an_observer_field_the_forbidden_list_does_not_name_fails(self) -> None:
        """The near-miss: a field the forbidden list almost names is not named at all."""

        def mutate(record):
            record["properties"]["observer"]["properties"]["observer_role"] = {
                "enum": ["primary-collector", "secondary-collector"]
            }
            record["properties"]["observer"]["required"].append("observer_role")

        with self.assertRaisesRegex(
            self.validator.ValidationFailure, "different fields"
        ):
            self.run_with(self.rewrite(EVENT, mutate))

        def mutate_both(path: Path, record):
            if path.name in {EVENT, OBSERVATION}:
                mutate(record)
            return record

        with self.assertRaisesRegex(
            self.validator.ValidationFailure, "forbidden preimage inputs"
        ):
            self.run_with(mutate_both)

    def test_a_reading_reset_vocabulary_that_drifts_from_the_binding_fails(
        self,
    ) -> None:
        def mutate(record):
            record["properties"]["reading"]["properties"]["reset_detection"][
                "enum"
            ].append("trust-the-producer")

        self.expect(OBSERVATION, mutate, "reset_detection differs from the producer")

    def test_an_accumulation_flag_that_is_not_the_binding_temporality_fails(
        self,
    ) -> None:
        def mutate(record):
            record["properties"]["reading"]["properties"]["accumulation"]["enum"] = [
                "cumulative",
                "incremental",
            ]

        self.expect(EVENT, mutate, "does not carry the cumulative/delta accumulation")


class SchemaExampleCoverageTests(unittest.TestCase):
    """`packages/schemas/examples/` is checked against itself, not against a list."""

    def setUp(self) -> None:
        self.validator = load_module(VALIDATOR, "validate_planning_artifacts")

    def test_repository_head_passes(self) -> None:
        self.validator.validate_schema_example_coverage()

    def test_an_example_with_no_owning_schema_fails(self) -> None:
        path = EXAMPLES / "unowned-record.valid.json"
        path.write_text("{}\n", encoding="utf-8")
        self.addCleanup(path.unlink, True)
        with self.assertRaisesRegex(
            self.validator.ValidationFailure, "carries a prefix no schema owns"
        ):
            self.validator.validate_schema_example_coverage()

    def test_an_example_with_no_expectation_in_its_name_fails(self) -> None:
        path = EXAMPLES / "normalized-event.probably-fine.json"
        path.write_text("{}\n", encoding="utf-8")
        self.addCleanup(path.unlink, True)
        with self.assertRaisesRegex(self.validator.ValidationFailure, "neither .* nor"):
            self.validator.validate_schema_example_coverage()

    def test_a_negative_that_stopped_being_negative_fails(self) -> None:
        source = EXAMPLES / "normalized-event.valid.json"
        path = EXAMPLES / "normalized-event.invalid-not-actually.json"
        path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        self.addCleanup(path.unlink, True)
        with self.assertRaisesRegex(
            self.validator.ValidationFailure, "negative fixture unexpectedly validated"
        ):
            self.validator.validate_schema_example_coverage()

    def test_a_computed_negative_its_schema_now_refuses_fails(self) -> None:
        name = "consolidation-plan.invalid-newer-identity-survives.json"
        path = EXAMPLES / name
        original = path.read_text(encoding="utf-8")
        self.addCleanup(path.write_text, original, "utf-8")
        record = json.loads(original)
        record["case"]["state"] = "not-a-declared-state"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(
            self.validator.ValidationFailure, "outlived the hole it excused"
        ):
            self.validator.validate_schema_example_coverage()

    def test_a_prefix_that_owns_only_refusals_fails(self) -> None:
        source = EXAMPLES / "source-observation.valid.json"
        moved = EXAMPLES / "source-observation.valid-acp.json"
        originals = {path: path.read_text(encoding="utf-8") for path in (source, moved)}
        for path in originals:
            self.addCleanup(path.write_text, originals[path], "utf-8")
            self.addCleanup(path.unlink, True)
        source.unlink()
        moved.unlink()
        with self.assertRaisesRegex(
            self.validator.ValidationFailure, "owns no valid example"
        ):
            self.validator.validate_schema_example_coverage()

    def test_a_declared_negative_gap_that_no_longer_exists_fails(self) -> None:
        source = EXAMPLES / "adapter-manifest.valid.json"
        path = EXAMPLES / "adapter-manifest.invalid-empty.json"
        path.write_text("{}\n", encoding="utf-8")
        self.addCleanup(path.unlink, True)
        self.assertTrue(source.is_file())
        with self.assertRaisesRegex(
            self.validator.ValidationFailure, "declares a negative-example gap"
        ):
            self.validator.validate_schema_example_coverage()


class CertificationStateColumnTests(unittest.TestCase):
    """The device column PF-067 recorded as a hole, and the guard that closes it."""

    def setUp(self) -> None:
        self.module = load_module(VOCABULARIES, "validate_state_vocabularies")

    def test_repository_head_passes(self) -> None:
        self.assertEqual(self.module.main(), 0)

    def test_the_column_now_declares_a_vocabulary(self) -> None:
        self.assertEqual(
            self.module.SQL_LOCAL_VOCABULARIES["source_receipts.certification_state"],
            (
                "uncertified",
                "candidate",
                "testing",
                "active",
                "degraded",
                "suspended",
                "expired",
                "superseded",
                "retired",
            ),
        )

    def test_an_excuse_for_a_column_that_now_has_one_fails(self) -> None:
        """The reverse check `check_absence_reasons` had and this table did not."""
        original = dict(self.module.SQL_COLUMNS_WITHOUT_VOCABULARY)
        self.addCleanup(
            setattr, self.module, "SQL_COLUMNS_WITHOUT_VOCABULARY", original
        )
        self.module.SQL_COLUMNS_WITHOUT_VOCABULARY = {
            "source_receipts.certification_state": "a reason that outlived its hole",
        }
        self.assertEqual(self.module.main(), 1)

    def test_an_excuse_naming_no_column_at_all_fails(self) -> None:
        original = dict(self.module.SQL_COLUMNS_WITHOUT_VOCABULARY)
        self.addCleanup(
            setattr, self.module, "SQL_COLUMNS_WITHOUT_VOCABULARY", original
        )
        self.module.SQL_COLUMNS_WITHOUT_VOCABULARY = {
            "receipts.imaginary_state": "names nothing",
        }
        self.assertEqual(self.module.main(), 1)


if __name__ == "__main__":
    unittest.main()
