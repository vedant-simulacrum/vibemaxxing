"""The OTel accounting profile may not claim support it has not exercised.

PF-041's acceptance asked for at least one real capture per supported metric. The
fixture covers one metric and the binding declares one, so the interesting failure is
the one that would happen next: a metric named in either record with nothing replaying
it. These tests drive that from both sides, and they drive the derivation table's own
rules — a field with no origin, an origin that reads an attribute the strip list
removes, and a declared disagreement that has outlived the disagreement.

Nothing here is evidence that a collector runs any of it. No collector exists.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
PROFILE = "accounting-profile-otel-v1.json"
BINDINGS = "producer-bindings-v1.json"


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


class OtelAccountingProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.load_json = self.validator.load_json
        self.addCleanup(setattr, self.validator, "load_json", self.load_json)

    def _run(self, mutate, check=None) -> None:
        def loader(path):
            return mutate(Path(path), copy.deepcopy(self.load_json(path)))

        self.validator.load_json = loader
        (check or self.validator.validate_otel_accounting_profile)()

    @staticmethod
    def _binding(record: dict) -> dict:
        return next(
            item
            for item in record["bindings"]
            if item["binding_id"] == "claude-code-otel-v1"
        )

    def test_repository_head_passes(self) -> None:
        self.validator.validate_otel_accounting_profile()

    def test_hazard_set_is_the_three_pf041_records(self) -> None:
        self.assertEqual(
            self.validator.OTEL_REQUIRED_HAZARDS,
            {
                "identity-attributes-on-every-datapoint",
                "default-on-prompt-logging",
                "default-third-party-metrics-exporter",
            },
        )

    def test_head_supports_exactly_one_metric(self) -> None:
        profile = self.load_json(
            ROOT / "packages" / "schemas" / "accounting-profile-otel-v1.json"
        )
        self.assertEqual(
            [item["name"] for item in profile["supported_metrics"]],
            ["claude_code.token.usage"],
        )

    def test_a_supported_metric_with_no_capture_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                record["supported_metrics"].append(
                    {
                        "name": "codex.turn.token_usage",
                        "producer_id": "codex-cli",
                        "capture_vectors": (
                            "conformance/accounting/otel-capture-vectors-v1.json"
                        ),
                        "capture_evidence_kind": "published-surface-read",
                        "assessed_on": "2026-08-06",
                    }
                )
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_a_capture_fixture_for_another_metric_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                record["supported_metrics"][0]["name"] = "gemini_cli.token.usage"
            if path.name == BINDINGS:
                metric = self._binding(record)["otel"]["metrics"][0]
                metric["name"] = "gemini_cli.token.usage"
                self._binding(record)["content_sha256"] = self.validator.record_digest(
                    self._binding(record)
                )
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_a_binding_metric_with_no_capture_fails(self) -> None:
        def mutate(path, record):
            if path.name == BINDINGS:
                binding = self._binding(record)
                extra = copy.deepcopy(binding["otel"]["metrics"][0])
                extra["name"] = "gemini_cli.token.usage"
                binding["otel"]["metrics"].append(extra)
                binding["content_sha256"] = self.validator.record_digest(binding)
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate, self.validator.validate_producer_bindings)

    def test_a_dropped_hazard_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                record["capture_surface_hazards"] = [
                    item
                    for item in record["capture_surface_hazards"]
                    if item["kind"] != "default-third-party-metrics-exporter"
                ]
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_calling_configuration_a_full_control_over_identity_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                for hazard in record["capture_surface_hazards"]:
                    if hazard["kind"] == "identity-attributes-on-every-datapoint":
                        hazard["configuration_is_a_control"] = "yes"
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_a_derivation_reading_a_stripped_attribute_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                for entry in record["derivations"]:
                    if entry["field"] == "model_id":
                        entry["otlp_attributes"] = ["user.email"]
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_a_missing_derivation_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                record["derivations"] = [
                    item for item in record["derivations"] if item["field"] != "outcome"
                ]
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_claiming_an_unobservable_field_is_deterministic_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                for entry in record["derivations"]:
                    if entry["field"] == "outcome":
                        entry["determinism"] = "deterministic"
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_an_undeclared_count_authority_disagreement_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                record["known_contradictions"] = [
                    item
                    for item in record["known_contradictions"]
                    if item["field"] != "count_authority"
                ]
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_a_declared_certification_gap_that_closed_fails(self) -> None:
        """A declaration may not outlive the hole it declares."""

        def mutate(path, record):
            if path.name == BINDINGS:
                binding = self._binding(record)
                binding["certification"]["tuple"]["bundle_sha256"] = "a" * 64
                binding["content_sha256"] = self.validator.record_digest(binding)
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)

    def test_an_unregistered_producer_fails(self) -> None:
        def mutate(path, record):
            if path.name == PROFILE:
                record["unsupported_metrics"][0]["producer_id"] = "not-a-product"
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate)


if __name__ == "__main__":
    unittest.main()
