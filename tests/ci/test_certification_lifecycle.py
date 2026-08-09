"""A certification lifecycle can be specified without certifying anything.

Three defects, and the first is the one that made the accounting layer unusable.

`normalized-event.schema.json` required `certification.bundle_sha256` as sixty-four
hexadecimal characters with no null admitted, and every producer binding in this
repository carries null. So no `NormalizedAccountingEvent` could be constructed from
any OTLP capture this repository can actually take, and the only fixture that filled
the field used sixty-four `f` characters — a placeholder standing exactly where the
honest answer was. Four other artifacts had already made the same field nullable for
the same reason; `evidence-bundle-v1.cddl` even names the case, "nil while uncertified".

The result bundle's three case counts were self-reported and bound to nothing. A run
could declare twelve cases and list two, and the way to turn a failing suite into a
passing one was to delete the entry that failed — including `negative_case_count`,
which the `certification_results` check constraint reads to refuse an untested pass.

And `openapi-v1.yaml` published no certification state at all. `PF-016`'s own note
recorded the API third of its acceptance as unmet: a participant could read which
certification their claim was appraised under and nothing about whether it was still
active when it was read.

Nothing here certifies anything. Every tuple this repository can reach is `candidate`,
and these tests assert that too.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
SCHEMAS = ROOT / "packages" / "schemas"
EXAMPLES = SCHEMAS / "examples"


def load_module():
    specification = importlib.util.spec_from_file_location(
        "validate_planning_artifacts", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class CertificationFixtureMixin:
    """Shared schema and example access.

    A mixin, not a base `TestCase`: subclassing one runs every test in this file again
    inside each child class, which inflates the suite's count without testing anything
    more.
    """

    module: Any

    def setUp(self) -> None:  # noqa: D102 - unittest hook
        self.module = load_module()

    def schema(self, name: str) -> dict[str, Any]:
        return self.module.validate_schema_file(SCHEMAS / name)

    def example(self, name: str) -> dict[str, Any]:
        return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))

    def registry_states(self, machine_id: str) -> list[str]:
        registry = json.loads(
            (SCHEMAS / "state-machine-registry-v1.json").read_text(encoding="utf-8")
        )
        return next(
            machine["states"]
            for machine in registry["machines"]
            if machine["machine_id"] == machine_id
        )


class UncertifiedCaptureTests(CertificationFixtureMixin, unittest.TestCase):
    def test_an_uncertified_capture_is_representable(self) -> None:
        """The defect: no event could be built from any capture we can take."""
        event = self.example("normalized-event.valid.json")

        self.assertIsNone(event["certification"]["bundle_sha256"])
        self.module.validate_instance(
            self.schema("normalized-event.schema.json"), event, "uncertified event"
        )

    def test_the_placeholder_digest_is_gone(self) -> None:
        """Sixty-four `f` characters was the only value that ever filled the field."""
        raw = (EXAMPLES / "normalized-event.valid.json").read_text(encoding="utf-8")

        self.assertNotIn("f" * 64, raw)

    def test_an_uncertified_capture_cannot_be_admitted_beyond_private_analytics(
        self,
    ) -> None:
        """Admitting the null is a representation, never a permission."""
        event = self.example("normalized-event.valid.json")
        event["rule_result"]["disposition"] = "accept-local"

        self.module.expect_invalid(
            self.schema("normalized-event.schema.json"),
            event,
            "uncertified capture admitted beyond private analytics",
        )

    def test_a_certified_capture_is_still_representable(self) -> None:
        """Nullable must not mean the certified branch was deleted instead."""
        event = self.example("normalized-event.valid.json")
        event["certification"]["bundle_sha256"] = "ab" * 32
        event["rule_result"]["disposition"] = "accept-local"

        self.module.validate_instance(
            self.schema("normalized-event.schema.json"), event, "certified event"
        )

    def test_a_malformed_digest_is_still_refused(self) -> None:
        event = self.example("normalized-event.valid.json")
        event["certification"]["bundle_sha256"] = "not-a-digest"

        self.module.expect_invalid(
            self.schema("normalized-event.schema.json"), event, "malformed digest"
        )

    def test_the_field_is_required_rather_than_optional(self) -> None:
        """An omission would have to be interpreted; a null is a statement."""
        event = self.example("normalized-event.valid.json")
        del event["certification"]["bundle_sha256"]

        self.module.expect_invalid(
            self.schema("normalized-event.schema.json"), event, "omitted bundle digest"
        )

    def test_the_resolved_contradiction_is_not_still_declared(self) -> None:
        """A justification that outlives its hole is a stale excuse."""
        profile = json.loads(
            (SCHEMAS / "accounting-profile-otel-v1.json").read_text(encoding="utf-8")
        )
        declared = {
            item["contradiction_id"] for item in profile["known_contradictions"]
        }

        self.assertNotIn("otel-certification-bundle-absent", declared)
        blocked = [entry for entry in profile["derivations"] if "blocked_by" in entry]
        self.assertEqual(blocked, [])

    def drift_json(self, mutate) -> None:
        """Run the OTel profile validator against mutated JSON documents."""
        original = self.module.load_json

        def patched(path):
            document = original(path)
            document = copy.deepcopy(document)
            mutate(Path(path).name, document)
            return document

        self.module.load_json = patched
        try:
            self.module.validate_otel_accounting_profile()
        finally:
            self.module.load_json = original

    def test_the_committed_records_resolve(self) -> None:
        self.module.validate_otel_accounting_profile()

    def test_re_declaring_the_resolved_contradiction_is_refused(self) -> None:
        """A justification that outlives its hole is refused in both directions."""

        def mutate(name: str, document: Any) -> None:
            if name == "accounting-profile-otel-v1.json":
                document["known_contradictions"].append(
                    {
                        "contradiction_id": "otel-certification-bundle-absent",
                        "field": "certification",
                        "this_profile": "cannot be written",
                        "other_authority": "packages/schemas/normalized-event.schema.json",
                        "other_value": "requires a digest",
                        "effect": "stale",
                        "owner": "PF-016",
                    }
                )

        with self.assertRaises(Exception) as caught:
            self.drift_json(mutate)

        self.assertIn("has outlived its hole", str(caught.exception))

    def test_re_narrowing_the_schema_without_declaring_it_is_refused(self) -> None:
        """The gap is read out of the schema, so reopening it fails again."""

        def mutate(name: str, document: Any) -> None:
            if name == "normalized-event.schema.json":
                document["properties"]["certification"]["properties"][
                    "bundle_sha256"
                ] = {"type": "string", "pattern": "^[a-f0-9]{64}$"}

        with self.assertRaises(Exception) as caught:
            self.drift_json(mutate)

        self.assertIn(
            "no known_contradictions entry declares it", str(caught.exception)
        )

    def test_admitting_the_null_without_pinning_the_disposition_is_refused(
        self,
    ) -> None:
        """Otherwise a representation gap silently becomes a permission."""

        def mutate(name: str, document: Any) -> None:
            if name == "normalized-event.schema.json":
                document["allOf"] = []

        with self.assertRaises(Exception) as caught:
            self.drift_json(mutate)

        self.assertIn(
            "turns a representation gap into a permission", str(caught.exception)
        )


class ResultCountTests(CertificationFixtureMixin, unittest.TestCase):
    def test_the_committed_result_counts_agree_with_its_cases(self) -> None:
        result = self.example("certification-result.valid.json")["result"]

        self.assertIsNone(self.module.certification_count_mismatch(result))

    def test_deleting_the_failing_case_no_longer_improves_the_result(self) -> None:
        """The signal must not improve when you remove what it counts."""
        result = copy.deepcopy(self.example("certification-result.valid.json"))[
            "result"
        ]
        result["cases"] = [
            case for case in result["cases"] if case["outcome"] != "failed"
        ]
        result["failed_case_count"] = 0
        result["outcome"] = "passed"

        mismatch = self.module.certification_count_mismatch(result)

        self.assertIsNotNone(mismatch)
        self.assertIn("case_count declared 3, derived 2", mismatch)

    def test_a_negative_count_larger_than_the_negative_cases_is_refused(self) -> None:
        """`negative_case_count` is what refuses an untested pass, so it is derived."""
        result = copy.deepcopy(self.example("certification-result.valid.json"))[
            "result"
        ]
        result["negative_case_count"] = 9

        self.assertIn(
            "negative_case_count declared 9, derived 2",
            self.module.certification_count_mismatch(result) or "",
        )

    def test_one_case_counted_twice_is_refused(self) -> None:
        result = copy.deepcopy(self.example("certification-result.valid.json"))[
            "result"
        ]
        result["cases"].append(copy.deepcopy(result["cases"][0]))
        result["case_count"] += 1
        result["negative_case_count"] += 1

        self.assertIn(
            "counted twice", self.module.certification_count_mismatch(result) or ""
        )

    def test_a_result_listing_no_case_is_refused_by_the_schema(self) -> None:
        result = self.example("certification-result.valid.json")
        result["result"]["cases"] = []

        self.module.expect_invalid(
            self.schema("certification-result-v1.schema.json"),
            result,
            "result listing no case",
        )

    def test_every_case_is_bound_by_digest_and_not_only_by_name(self) -> None:
        result = self.example("certification-result.valid.json")

        for case in result["result"]["cases"]:
            self.assertRegex(case["case_sha256"], r"^[0-9a-f]{64}$")
        del result["result"]["cases"][0]["case_sha256"]
        self.module.expect_invalid(
            self.schema("certification-result-v1.schema.json"),
            result,
            "case bound by identifier alone",
        )

    def test_the_drift_example_is_schema_valid_on_purpose(self) -> None:
        """It exists to show the schema cannot see this class of defect."""
        drift = self.example("certification-result.invalid-counts-omit-a-case.json")

        self.module.validate_instance(
            self.schema("certification-result-v1.schema.json"), drift, "count drift"
        )
        self.assertIsNotNone(self.module.certification_count_mismatch(drift["result"]))


class PublishedLifecycleTests(CertificationFixtureMixin, unittest.TestCase):
    def api_evaluated(self) -> dict[str, Any]:
        spec = yaml.safe_load((SCHEMAS / "openapi-v1.yaml").read_text(encoding="utf-8"))
        return spec["components"]["schemas"]["AppraisalSummary"]["properties"][
            "evaluated"
        ]["properties"]

    def test_the_api_publishes_the_certification_state(self) -> None:
        """The API third of the acceptance, which the unit's own note recorded unmet."""
        self.assertIn("certification_state", self.api_evaluated())

    def test_one_vocabulary_crosses_registry_sql_and_api(self) -> None:
        machine = set(self.registry_states("source-certification"))
        published = set(self.api_evaluated()["certification_state"]["enum"])
        sql = self.module._sql_check_vocabulary(
            self.module._planning_table_bodies()["source_certifications"], "state"
        )

        self.assertEqual(sql, machine)
        self.assertEqual(published, machine | {"uncertified"})

    def test_uncertified_is_not_a_state_of_the_machine(self) -> None:
        """A capture bound to no certification has no aggregate to be in a state."""
        self.assertNotIn("uncertified", self.registry_states("source-certification"))

    def test_the_record_and_the_projection_admit_the_same_values(self) -> None:
        record = json.loads(
            (SCHEMAS / "appraisal-result-v1.schema.json").read_text(encoding="utf-8")
        )
        stored = set(
            record["properties"]["evaluated"]["properties"]["certification_state"][
                "enum"
            ]
        )

        self.assertEqual(
            stored, set(self.api_evaluated()["certification_state"]["enum"])
        )

    def test_the_state_is_required_rather_than_optional(self) -> None:
        """An absent field on a `self` shape is a redaction that fails open."""
        record = json.loads(
            (SCHEMAS / "appraisal-result-v1.schema.json").read_text(encoding="utf-8")
        )

        self.assertIn(
            "certification_state", record["properties"]["evaluated"]["required"]
        )

    def drift_api(self, mutate) -> None:
        """Run the certification validator against a mutated OpenAPI document."""
        original = self.module.load_yaml

        def patched(path):
            document = original(path)
            if Path(path).name == "openapi-v1.yaml":
                document = copy.deepcopy(document)
                mutate(document)
            return document

        self.module.load_yaml = patched
        try:
            self.module.validate_certification_contracts()
        finally:
            self.module.load_yaml = original

    def test_a_narrowed_api_vocabulary_is_refused(self) -> None:
        def mutate(document: dict[str, Any]) -> None:
            evaluated = document["components"]["schemas"]["AppraisalSummary"][
                "properties"
            ]["evaluated"]["properties"]
            evaluated["certification_state"]["enum"].remove("retired")

        with self.assertRaises(Exception) as caught:
            self.drift_api(mutate)

        self.assertIn("only-in-registry=['retired']", str(caught.exception))

    def test_removing_the_published_state_entirely_is_refused(self) -> None:
        """The check must not be satisfiable by deleting the field it reads."""

        def mutate(document: dict[str, Any]) -> None:
            evaluated = document["components"]["schemas"]["AppraisalSummary"][
                "properties"
            ]["evaluated"]["properties"]
            del evaluated["certification_state"]

        with self.assertRaises(Exception) as caught:
            self.drift_api(mutate)

        self.assertIn("the API publishes no certification state", str(caught.exception))

    def test_an_invented_published_state_is_refused(self) -> None:
        def mutate(document: dict[str, Any]) -> None:
            evaluated = document["components"]["schemas"]["AppraisalSummary"][
                "properties"
            ]["evaluated"]["properties"]
            evaluated["certification_state"]["enum"].append("provisional")

        with self.assertRaises(Exception) as caught:
            self.drift_api(mutate)

        self.assertIn("only-in-api=['provisional']", str(caught.exception))


class NothingIsCertifiedTests(CertificationFixtureMixin, unittest.TestCase):
    def test_no_producer_binding_carries_a_certification_bundle(self) -> None:
        """The lifecycle is specified. Nothing has moved through it."""
        bindings = json.loads(
            (
                ROOT / "conformance" / "accounting" / "producer-bindings-v1.json"
            ).read_text(encoding="utf-8")
        )

        digests = [
            binding["certification"]["tuple"]["bundle_sha256"]
            for binding in bindings["bindings"]
        ]
        self.assertTrue(digests)
        self.assertEqual(set(digests), {None})

    def test_no_binding_declares_itself_certified(self) -> None:
        bindings = json.loads(
            (
                ROOT / "conformance" / "accounting" / "producer-bindings-v1.json"
            ).read_text(encoding="utf-8")
        )

        states = {binding["certification"]["state"] for binding in bindings["bindings"]}
        self.assertTrue(states <= {"candidate", "uncertified"}, states)


if __name__ == "__main__":
    unittest.main()
