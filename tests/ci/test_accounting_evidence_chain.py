"""The accounting and evidence vectors must be executed, not merely declared.

A fixture that records its own answer proves nothing when the validator reads that
answer back. These tests corrupt each recorded expectation and require the validator
to notice, which is what makes a passing run mean the arithmetic, the OTLP capture
model and the observer-equivalence rule were actually reproduced.

They prove reference behaviour in this repository's validator only. No collector, no
receiver and no verifier exists, and nothing here is implementation evidence.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"


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


class ArithmeticVectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()

    def test_repository_head_passes(self) -> None:
        self.validator.validate_accounting_arithmetic()

    def test_checked_addition_rejects_past_the_domain(self) -> None:
        profile = {
            "source_fields": [{"field_id": "a"}, {"field_id": "b"}],
            "containment_edges": [],
            "component_map": [
                {"source_field": "a", "canonical_component": "input_uncached"},
                {"source_field": "b", "canonical_component": "output_visible"},
            ],
        }
        outcome, detail = self.validator.evaluate_token_burn(
            profile, {"a": str(self.validator.UINT64_MAX), "b": "1"}
        )
        self.assertEqual((outcome, detail), ("reject", "sum-overflow"))

    def test_containment_underflow_rejects_rather_than_clamping(self) -> None:
        profile = {
            "source_fields": [{"field_id": "total"}, {"field_id": "part"}],
            "containment_edges": [{"container": "total", "member": "part"}],
            "component_map": [
                {"source_field": "total", "canonical_component": "input_uncached"},
                {"source_field": "part", "canonical_component": "cache_read"},
            ],
        }
        outcome, detail = self.validator.evaluate_token_burn(
            profile, {"total": "20", "part": "30"}
        )
        self.assertEqual((outcome, detail), ("reject", "containment-underflow"))

    def test_half_even_resolves_both_ties_differently_from_half_up(self) -> None:
        down = self.validator.evaluate_cash_burn(
            [{"units": "5", "unit_price_nano": "500"}]
        )
        up = self.validator.evaluate_cash_burn(
            [{"units": "7", "unit_price_nano": "500"}]
        )
        self.assertEqual((down, up), (2, 4))

    def test_single_rounding_site_differs_from_per_component_rounding(self) -> None:
        components = [
            {"units": "1", "unit_price_nano": "1400"},
            {"units": "1", "unit_price_nano": "1400"},
            {"units": "1", "unit_price_nano": "1400"},
        ]
        self.assertEqual(self.validator.evaluate_cash_burn(components), 4)
        per_component = sum(
            self.validator.evaluate_cash_burn([entry]) for entry in components
        )
        self.assertEqual(per_component, 3)

    def test_retraction_past_zero_rejects(self) -> None:
        self.assertEqual(
            self.validator.evaluate_correction(
                [
                    {"direction": "add", "magnitude": "10"},
                    {"direction": "retract", "magnitude": "20"},
                ]
            ),
            ("reject", 0),
        )


class VectorCorruptionTests(unittest.TestCase):
    """Each recorded expectation must be load-bearing."""

    def setUp(self) -> None:
        self.validator = load_validator()
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory, True)

    def _sandbox(self) -> Path:
        conformance = self.directory / "conformance"
        if not conformance.exists():
            shutil.copytree(ROOT / "conformance", conformance)
        return conformance

    def _run_with(self, conformance: Path, check) -> None:
        original = self.validator.CONFORMANCE
        self.validator.CONFORMANCE = conformance
        try:
            with self.assertRaises(self.validator.ValidationFailure):
                check()
        finally:
            self.validator.CONFORMANCE = original

    def test_a_wrong_token_total_fails(self) -> None:
        conformance = self._sandbox()
        path = conformance / "accounting" / "arithmetic-vectors-v1.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["vectors"][0]["expected_token_burn"] = "211"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._run_with(conformance, self.validator.validate_accounting_arithmetic)

    def test_a_cumulative_counter_read_as_a_delta_fails(self) -> None:
        conformance = self._sandbox()
        path = conformance / "accounting" / "otel-capture-vectors-v1.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for vector in payload["vectors"]:
            if vector["vector_id"] == "cumulative-second-export-is-a-delta":
                vector["expected_components"]["input_uncached"] = "350"
                vector["expected_token_burn"] = "350"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._run_with(conformance, self.validator.validate_producer_bindings)

    def test_a_double_counted_deduplication_result_fails(self) -> None:
        conformance = self._sandbox()
        path = conformance / "accounting" / "dedup-vectors-v1.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for vector in payload["vectors"]:
            if (
                vector["vector_id"]
                == "two-collectors-source-cursor-collision-counts-once"
            ):
                vector["expected"]["dispositions"]["beta-otel"] = "counted"
                vector["expected"]["counted_token_burn"] = "420"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._run_with(conformance, self.validator.validate_observer_equivalence)


class ObserverEquivalenceRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.rule = json.loads(
            (ROOT / "packages" / "schemas" / "observer-equivalence-v1.json").read_text(
                encoding="utf-8"
            )
        )

    def test_repository_head_passes(self) -> None:
        self.validator.validate_observer_equivalence()

    def _observation(self, identifier: str, collector: str, ordinal: str) -> dict:
        return {
            "observation_id": identifier,
            "mode": "otel",
            "equivalence_class": "source-cursor",
            "collector_instance": collector,
            "preimage_inputs": [
                "device_lineage_id",
                "source_id",
                "provider_id",
                "model_id",
                "accounting_profile_id",
                "source_runtime_id",
                "runtime_generation",
                "source_cursor_domain",
                "source_cursor_ordinal",
            ],
            "facts": {
                "device_lineage_id": "lineage",
                "source_id": "source",
                "provider_id": "provider",
                "model_id": "model",
                "accounting_profile_id": "profile",
                "source_runtime_id": "runtime",
                "runtime_generation": "0",
                "source_cursor_domain": "domain",
                "source_cursor_ordinal": ordinal,
            },
            "token_burn": "210",
        }

    def test_two_collectors_that_agree_count_once(self) -> None:
        result = self.validator.resolve_observations(
            self.rule,
            [
                self._observation("alpha", "alpha", "7"),
                self._observation("beta", "beta", "7"),
            ],
        )
        self.assertEqual(sorted(result.values()), ["counted", "superseded"])

    def test_two_collectors_that_disagree_quarantine_rather_than_sum(self) -> None:
        result = self.validator.resolve_observations(
            self.rule,
            [
                self._observation("alpha", "alpha", "7"),
                self._observation("beta", "beta", "8"),
            ],
        )
        self.assertEqual(set(result.values()), {"quarantined"})

    def test_an_observer_derived_preimage_input_is_rejected(self) -> None:
        observation = self._observation("alpha", "alpha", "7")
        observation["preimage_inputs"].append("collector_instance_id")
        observation["facts"]["collector_instance_id"] = "alpha"
        result = self.validator.resolve_observations(self.rule, [observation])
        self.assertEqual(result, {"alpha": "rejected"})


if __name__ == "__main__":
    unittest.main()
