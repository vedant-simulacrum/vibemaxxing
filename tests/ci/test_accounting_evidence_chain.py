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


class ThreeAuthoritySandboxMixin:
    """Sandboxes `packages/schemas/` and `conformance/` together.

    `validate_evidence_chain` cross-reads the CDDL grammar, the appraisal result
    schema and the SQL DDL, which all live under `packages/schemas/`, against
    fixtures under `conformance/`. A test that moves one of those authorities needs
    both trees copied and private, or a prior test's mutation could bleed into this
    one's run of the validator. This is a mixin rather than a shared `TestCase`
    subclass: the fixtures are reused by composing this class into each concrete
    `TestCase`, not by one test case inheriting another's setup.
    """

    def setUp(self) -> None:
        super().setUp()
        self.validator = load_validator()
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory, True)
        self.schemas = self.directory / "schemas"
        self.conformance = self.directory / "conformance"
        shutil.copytree(ROOT / "packages" / "schemas", self.schemas)
        shutil.copytree(ROOT / "conformance", self.conformance)

    def _expect_failure(self, *fragments: str) -> None:
        original_schemas = self.validator.SCHEMAS
        original_conformance = self.validator.CONFORMANCE
        self.validator.SCHEMAS = self.schemas
        self.validator.CONFORMANCE = self.conformance
        try:
            with self.assertRaises(self.validator.ValidationFailure) as context:
                self.validator.validate_evidence_chain()
        finally:
            self.validator.SCHEMAS = original_schemas
            self.validator.CONFORMANCE = original_conformance
        message = str(context.exception)
        for fragment in fragments:
            self.assertIn(fragment, message)

    def _mutate_bundle(self, mutate) -> None:
        """Edit `appraisal-policy-v1.json` and keep its self-digest honest.

        The bundle carries its own `content_sha256`. Leaving it stale would trip
        `assert_record_digest` before the check a test means to exercise ever runs,
        so every bundle mutation recomputes it the same way the validator does.
        """
        path = self.schemas / "appraisal-policy-v1.json"
        bundle = json.loads(path.read_text(encoding="utf-8"))
        mutate(bundle)
        bundle["content_sha256"] = self.validator.record_digest(bundle)
        path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    def _mutate_result_schema(self, mutate) -> None:
        path = self.schemas / "appraisal-result-v1.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        mutate(schema)
        path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    def _mutate_cddl_block(self, mutate) -> None:
        """Edit the body of `verifier-appraisal-v1 = { ... }` alone.

        Other CDDL rules in the same file reuse small label numbers, so a mutation
        has to stay inside this rule's braces rather than doing a whole-file
        string replace that could land on `checkpoint-receipt-v1` instead.
        """
        path = self.schemas / "vibeproof-claim-v1.cddl"
        text = path.read_text(encoding="utf-8")
        start = text.index("verifier-appraisal-v1 = {")
        end = text.index("\n}", start)
        path.write_text(
            text[:start] + mutate(text[start:end]) + text[end:], encoding="utf-8"
        )

    def _mutate_verifier_appraisals_table(self, mutate) -> None:
        """Edit the body of `create table verifier_appraisals ( ... )` alone.

        `claim_id` and `created_at` are column names several tables in this DDL
        share, so this scopes to the one table block the same way the validator's
        own DDL parser does, rather than a whole-file replace that could edit a
        different table entirely.
        """
        path = self.schemas / "planning-schema.sql"
        text = path.read_text(encoding="utf-8")
        marker = "create table verifier_appraisals ("
        start = text.index(marker)
        end = text.index("\n);", start)
        path.write_text(
            text[:start] + mutate(text[start:end]) + text[end:], encoding="utf-8"
        )


class EvidenceChainDriftTests(ThreeAuthoritySandboxMixin, unittest.TestCase):
    """`validate_evidence_chain` cross-checks four authorities against each other:
    the CDDL grammar, the appraisal result record schema, the appraisal policy
    bundle's wire and SQL bindings, and the `verifier_appraisals` DDL. Each test
    here moves exactly one of those authorities one step away from what the other
    three say and requires the validator to notice — which is what makes a passing
    run mean the four descriptions of one appraisal actually agree, rather than
    each merely being internally well-formed.
    """

    def test_repository_head_passes(self) -> None:
        self.validator.validate_evidence_chain()

    def test_a_label_the_cddl_drops_while_the_binding_still_maps_it_is_caught(
        self,
    ) -> None:
        def mutate(block: str) -> str:
            lines = block.splitlines(keepends=True)
            kept = [line for line in lines if not line.strip().startswith("5:")]
            self.assertLess(len(kept), len(lines))
            return "".join(kept)

        self._mutate_cddl_block(mutate)
        self._expect_failure("disagree about which labels exist", "only in the binding")

    def test_a_label_the_binding_never_mapped_is_caught_the_other_way(self) -> None:
        def mutate(block: str) -> str:
            return block + "\n  30: uint64,             ; unbound label"

        self._mutate_cddl_block(mutate)
        self._expect_failure("disagree about which labels exist", "only in the CDDL")

    def test_two_binding_labels_naming_the_same_field_are_unreachable(self) -> None:
        def mutate(bundle: dict) -> None:
            labels = bundle["appraisal_record"]["wire_binding"]["labels"]
            labels["5"] = labels["4"]

        self._mutate_bundle(mutate)
        self._expect_failure("unreachable")

    def test_a_record_field_the_binding_accounts_for_nowhere_is_caught(self) -> None:
        def mutate(schema: dict) -> None:
            schema["properties"]["operator_note"] = {"type": "string"}

        self._mutate_result_schema(mutate)
        self._expect_failure("describe different records", "operator_note")

    def test_a_record_only_field_the_record_never_declared_is_invented(self) -> None:
        def mutate(bundle: dict) -> None:
            bundle["appraisal_record"]["wire_binding"]["record_only_fields"][
                "phantom_field"
            ] = (
                "A field named here that appraisal-result-v1.schema.json never "
                "declared, which is the invented side of the same check."
            )

        self._mutate_bundle(mutate)
        self._expect_failure("describe different records", "phantom_field")

    def test_a_nullable_cddl_label_whose_record_field_forbids_null_is_caught(
        self,
    ) -> None:
        def mutate(block: str) -> str:
            old = "  4: registered-id,        ; verifier_policy_id"
            new = "  4: registered-id / nil,  ; verifier_policy_id"
            self.assertIn(old, block)
            return block.replace(old, new, 1)

        self._mutate_cddl_block(mutate)
        self._expect_failure("disagree about null", "appraisal label 4")

    def test_a_widened_range_leaves_an_unresolvable_ordinal(self) -> None:
        """The predecessor check used `>` rather than `!=`, so a range one wider
        than the vocabulary it encodes passed: the surplus ordinal was
        representable on the wire and resolved to nothing. Three ranges in the
        repository really were that slack until this check replaced it.
        """

        def mutate(block: str) -> str:
            old = "  8: 0..3,                 ; capture_class"
            new = "  8: 0..4,                 ; capture_class"
            self.assertIn(old, block)
            return block.replace(old, new, 1)

        self._mutate_cddl_block(mutate)
        self._expect_failure("representable and resolve to no value", "capture_class")

    def test_a_bound_column_the_table_no_longer_defines_is_caught(self) -> None:
        def mutate(block: str) -> str:
            old = "  claim_id uuid not null references claims(claim_id),\n"
            self.assertIn(old, block)
            return block.replace(old, "", 1)

        self._mutate_verifier_appraisals_table(mutate)
        self._expect_failure("does not define", "claim_id")

    def test_an_unexplained_new_column_is_a_private_vocabulary(self) -> None:
        def mutate(block: str) -> str:
            anchor = "  created_at timestamptz not null,\n"
            self.assertIn(anchor, block)
            return block.replace(anchor, anchor + "  spare_column text,\n", 1)

        self._mutate_verifier_appraisals_table(mutate)
        self._expect_failure("private vocabulary again", "spare_column")

    def test_evidence_profile_id_made_not_null_again_is_caught_against_the_sql(
        self,
    ) -> None:
        """The exact SR-017 defect: `evidence_profile_id text not null` sat in
        `column_bindings` while the record and the CDDL both said the field may be
        null, and nothing compared the column's nullability to either.
        """

        def mutate(block: str) -> str:
            old = (
                "  evidence_profile_id text check (evidence_profile_id in "
                "('hardened-source-bound-v1','standard-competitive-v1','imported-v1')),\n"
            )
            new = old.replace("text check", "text not null check", 1)
            self.assertIn(old, block)
            return block.replace(old, new, 1)

        self._mutate_verifier_appraisals_table(mutate)
        self._expect_failure("disagree about null", "evidence_profile_id")

    def test_an_unpersisted_field_that_also_has_a_column_has_outlived_its_excuse(
        self,
    ) -> None:
        def mutate(bundle: dict) -> None:
            sql_binding = bundle["appraisal_record"]["sql_binding"]
            self.assertIn("appraisal_id", sql_binding["column_bindings"])
            sql_binding["unpersisted_fields"]["appraisal_id"] = (
                "A field that is both stored under column_bindings and excused "
                "here, which is the reason that outlived its own gap."
            )

        self._mutate_bundle(mutate)
        self._expect_failure("outlived the gap it excused", "appraisal_id")

    def test_an_excuse_naming_a_field_the_record_never_declared_names_nothing(
        self,
    ) -> None:
        def mutate(bundle: dict) -> None:
            bundle["appraisal_record"]["sql_binding"]["unpersisted_fields"][
                "not_a_real_field"
            ] = (
                "A reason recorded for a field appraisal-result-v1.schema.json "
                "never declared, which names nothing at all."
            )

        self._mutate_bundle(mutate)
        self._expect_failure("the excuse names nothing", "not_a_real_field")

    def test_removing_created_at_from_column_only_makes_it_stray(self) -> None:
        def mutate(bundle: dict) -> None:
            column_only = bundle["appraisal_record"]["sql_binding"]["column_only"]
            self.assertIn("created_at", column_only)
            del column_only["created_at"]

        self._mutate_bundle(mutate)
        self._expect_failure("private vocabulary again", "created_at")


if __name__ == "__main__":
    unittest.main()
