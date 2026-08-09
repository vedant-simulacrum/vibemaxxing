"""Reconciliation must be a function of the readings, and its bounds must refuse.

PF-018. `validate_accounting_reconciliation` recomputes every vector from the
arithmetic record rather than reading its expectation back, and it recomputes it under
every permutation of the vector's readings. These tests prove that machinery catches
drift rather than that it runs: each one injects a specific defect and asserts the
exact substring the validator fails with.

The interesting ones are the two that would otherwise be invisible. A reconciliation
that picks a survivor between two equally authoritative contradicting readings passes
every vector whose readings happen to be listed in one order, so the permutation sweep
is the only thing that catches it. And a coverage count that improves when a failing
case is deleted is the defect class this repository keeps rediscovering, so the failure
conditions are compared by set equality in both directions.

None of this is evidence that any implementation reconciles anything. No collector and
no server exists.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
VECTORS = "reconciliation-vectors-v1.json"
ARITHMETIC = "accounting-arithmetic-v1.json"
PROFILES = "accounting-profiles-v1.json"
EVENT = "normalized-event.schema.json"
PROFILE_SCHEMA = "accounting-profile.schema.json"


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


class MutatedRecords:
    """Run a validator function with one record rewritten in memory.

    A mixin rather than a TestCase base: it owns the loader patch and nothing else, so
    a test class can combine it with `unittest.TestCase` without inheriting assertions
    from a class that is not a test.
    """

    validator: object

    def install(self) -> None:
        self.validator = load_validator()
        self._load_json = self.validator.load_json
        self.addCleanup(setattr, self.validator, "load_json", self._load_json)

    def run_with(self, mutate, check=None) -> None:
        def loader(path):
            return mutate(Path(path), copy.deepcopy(self._load_json(path)))

        self.validator.load_json = loader
        (check or self.validator.validate_accounting_reconciliation)()

    def rewrite(self, filename: str, mutate):
        def loader(path: Path, record):
            if path.name == filename:
                mutate(record)
            return record

        return loader

    def expect(self, filename: str, mutate, message: str, check=None) -> None:
        with self.assertRaisesRegex(self.validator.ValidationFailure, message):
            self.run_with(self.rewrite(filename, mutate), check)


class ReconciliationVectorTests(MutatedRecords, unittest.TestCase):
    def setUp(self) -> None:
        self.install()

    def test_repository_head_passes(self) -> None:
        self.validator.validate_accounting_reconciliation()

    def test_a_wrong_recorded_total_fails(self) -> None:
        def mutate(record):
            record["vectors"][0]["expected"]["counted_token_burn"] = "211"

        self.expect(VECTORS, mutate, "counted 210 tokens, not 211")

    def test_summing_two_readings_of_one_operation_fails(self) -> None:
        """The double count the whole record exists to prevent."""

        def mutate(record):
            vector = next(
                item
                for item in record["vectors"]
                if item["vector_id"] == "higher-authority-supersedes-lower"
            )
            vector["expected"]["dispositions"]["r-source-live-log"] = "counted"

        self.expect(VECTORS, mutate, "dispositions disagree")

    def test_selecting_a_survivor_from_a_contradiction_fails(self) -> None:
        def mutate(record):
            vector = next(
                item
                for item in record["vectors"]
                if item["vector_id"] == "equal-authority-contradiction-quarantines"
            )
            vector["expected"]["dispositions"] = {
                "r-provider-otel": "counted",
                "r-provider-proxy": "superseded",
            }
            vector["expected"]["counted_token_burn"] = "140"
            vector["expected"]["period_total_after"] = "140"

        self.expect(VECTORS, mutate, "dispositions disagree")

    def test_a_deleted_failure_vector_fails(self) -> None:
        """A coverage signal that improves when the failing case is removed."""

        def mutate(record):
            record["vectors"] = [
                item
                for item in record["vectors"]
                if item["vector_id"] != "per-event-bound-exceeded-rejects"
            ]

        self.expect(VECTORS, mutate, r"unexercised=\['per-event-bound-exceeded'\]")

    def test_a_vector_wider_than_the_permutation_ceiling_fails(self) -> None:
        def mutate(record):
            vector = record["vectors"][0]
            base = vector["readings"][0]
            for index in range(6):
                extra = copy.deepcopy(base)
                extra["reading_id"] = f"r-extra-{index}"
                vector["readings"].append(extra)

        self.expect(VECTORS, mutate, "capped at six")

    def test_a_vector_naming_an_unregistered_profile_fails(self) -> None:
        def mutate(record):
            record["vectors"][0]["profile_id"] = "profile-that-does-not-exist"

        self.expect(VECTORS, mutate, "names an unregistered profile")


class ReconciliationRuleTests(MutatedRecords, unittest.TestCase):
    def setUp(self) -> None:
        self.install()

    def test_an_ordering_dependent_tie_break_is_caught(self) -> None:
        """The permutation sweep, driven from the evaluator rather than the fixture.

        A reconciler that keeps the reading it saw first is correct on any single
        ordering of an agreeing pair and wrong on the other, which is exactly the defect
        no per-vector expectation can see.
        """
        validator = self.validator
        arithmetic = validator.load_json(
            validator.SCHEMAS / "accounting-arithmetic-v1.json"
        )
        profiles = validator.load_json(
            validator.CONFORMANCE / "accounting" / "accounting-profiles-v1.json"
        )
        profile = next(
            item
            for item in profiles["profiles"]
            if item["profile_id"] == "cloud-separate-cache-v1"
        )
        rule = validator.load_json(validator.SCHEMAS / "observer-equivalence-v1.json")
        mode_rank = {
            mode["mode"]: mode["precedence_rank"] for mode in rule["observation_modes"]
        }
        vectors = validator.load_json(
            validator.CONFORMANCE / "accounting" / "reconciliation-vectors-v1.json"
        )
        agreeing = next(
            item
            for item in vectors["vectors"]
            if item["vector_id"] == "equal-authority-agreement-counts-once"
        )
        readings = agreeing["readings"]

        forward = validator.evaluate_reconciliation(
            arithmetic, profile, mode_rank, list(readings), "0"
        )
        backward = validator.evaluate_reconciliation(
            arithmetic, profile, mode_rank, list(reversed(readings)), "0"
        )
        self.assertEqual(forward, backward)

        # A first-wins reconciler, written out, disagrees with itself.
        def first_wins(items):
            return items[0]["reading_id"]

        self.assertNotEqual(first_wins(readings), first_wins(list(reversed(readings))))

    def test_an_authority_order_that_is_not_the_event_enum_fails(self) -> None:
        def mutate(record):
            record["reconciliation"]["authority_order"] = [
                "runtime-reported",
                "provider-reported",
                "source-reported",
                "exact-reconstruction",
            ]

        self.expect(ARITHMETIC, mutate, "is not the count_authority enum of")

    def test_a_profile_authority_spelled_differently_fails(self) -> None:
        """The `reconstructed` / `exact-reconstruction` split, as a check."""

        def mutate(record):
            record["properties"]["source_fields"]["items"]["properties"]["authority"][
                "enum"
            ] = [
                "provider-reported",
                "runtime-reported",
                "source-reported",
                "reconstructed",
            ]

        self.expect(PROFILE_SCHEMA, mutate, "different count authorities")

    def test_a_group_key_without_the_operation_fails(self) -> None:
        def mutate(record):
            record["reconciliation"]["group_key"] = [
                "device_lineage_id",
                "source_runtime_id",
                "runtime_generation",
            ]

        self.expect(ARITHMETIC, mutate, r"missing \['operation_ref'\]")

    def test_a_forbidden_input_used_as_a_tie_break_fails(self) -> None:
        def mutate(record):
            record["reconciliation"]["tie_break_order"].append("arrival-order")

        self.expect(ARITHMETIC, mutate, "forbidden tie-break input is also")

    def test_a_capture_mode_with_no_precedence_rank_fails(self) -> None:
        def mutate(record):
            record["properties"]["certification"]["properties"]["capture_mode"][
                "enum"
            ].append("carrier-pigeon")

        self.expect(EVENT, mutate, "capture modes the observer-equivalence rule")

    def test_a_per_event_bound_at_or_above_the_period_bound_fails(self) -> None:
        def mutate(record):
            record["bounds"]["per_event_token_burn_maximum"] = record["bounds"][
                "period_accumulator_maximum"
            ]

        self.expect(ARITHMETIC, mutate, "period bound would be unreachable")

    def test_a_period_bound_below_the_integer_domain_fails(self) -> None:
        def mutate(record):
            record["bounds"]["period_accumulator_maximum"] = "1000000000000"

        self.expect(ARITHMETIC, mutate, "not the integer domain maximum")

    def test_an_outcome_the_map_does_not_cover_fails(self) -> None:
        def mutate(record):
            record["outcome_normalization"]["map"] = [
                entry
                for entry in record["outcome_normalization"]["map"]
                if entry["observed"] != "unknown"
            ]

        self.expect(ARITHMETIC, mutate, "not total over source-observation")

    def test_an_outcome_reason_that_outlived_its_hole_fails(self) -> None:
        def mutate(record):
            # The inversion PF-017 removed, put back: the map now reaches
            # `aborted-known`, so the reason declaring it normalizer-assigned describes
            # nothing.
            for entry in record["outcome_normalization"]["map"]:
                if entry["observed"] == "aborted-unknown":
                    entry["normalized"] = "aborted-known"

        self.expect(ARITHMETIC, mutate, "not exactly the event outcomes")


if __name__ == "__main__":
    unittest.main()
