"""The appraisal an operation returns must be the projection, not the record.

PF-043's acceptance was that `ClaimRecord.appraisal_id` resolve to a defined schema and
a retrievable operation. Any response shape satisfies that, including one that publishes
an integrity-private record to whoever holds the identifier, so these tests exercise the
half the acceptance did not reach: that the shape is narrower than the record by exactly
the two fields D-613 withholds, that the withheld names appear nowhere in the document,
and that the operation has no audience but its own subject.

None of this proves a handler enforces ownership. No handler exists.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
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


class AppraisalDisclosureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.load_json = self.validator.load_json
        self.load_yaml = self.validator.load_yaml
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        self.validator.load_json = self.load_json
        self.validator.load_yaml = self.load_yaml

    def _run(self, mutate_json=None, mutate_yaml=None) -> None:
        def json_loader(path):
            record = copy.deepcopy(self.load_json(path))
            return record if mutate_json is None else mutate_json(Path(path), record)

        def yaml_loader(path):
            record = copy.deepcopy(self.load_yaml(path))
            return record if mutate_yaml is None else mutate_yaml(Path(path), record)

        self.validator.load_json = json_loader
        self.validator.load_yaml = yaml_loader
        self.validator.validate_appraisal_disclosure()

    def _operation(self, spec: dict) -> dict:
        return spec["paths"]["/appraisals/{id}"]["get"]

    def test_repository_head_passes(self) -> None:
        self.validator.validate_appraisal_disclosure()

    def test_withheld_pair_is_the_two_d613_names(self) -> None:
        self.assertEqual(
            self.validator.APPRAISAL_WITHHELD_FROM_SUBJECT,
            {"evaluated": "anomaly_disposition", "policy": "implementation_sha256"},
        )

    def test_returning_the_record_instead_of_the_projection_fails(self) -> None:
        def mutate(path, spec):
            if path.name != "openapi-v1.yaml":
                return spec
            content = self._operation(spec)["responses"]["200"]["content"]
            content["application/json"]["schema"]["$ref"] = (
                "#/components/schemas/ClaimRecord"
            )
            return spec

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_yaml=mutate)

    def test_reintroducing_the_anomaly_disposition_fails(self) -> None:
        def mutate(path, spec):
            if path.name != "openapi-v1.yaml":
                return spec
            summary = spec["components"]["schemas"]["AppraisalSummary"]
            summary["properties"]["evaluated"]["properties"]["anomaly_disposition"] = {
                "enum": ["no-signal"]
            }
            return spec

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_yaml=mutate)

    def test_withheld_name_on_any_other_shape_fails(self) -> None:
        def mutate(path, spec):
            if path.name != "openapi-v1.yaml":
                return spec
            spec["components"]["schemas"]["ClaimRecord"]["properties"][
                "implementation_sha256"
            ] = {"type": "string"}
            return spec

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_yaml=mutate)

    def test_a_field_added_to_the_record_must_be_decided(self) -> None:
        def mutate(path, record):
            if path.name == "appraisal-result-v1.schema.json":
                record["properties"]["operator_note"] = {"type": "string"}
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_json=mutate)

    def test_a_withheld_field_the_record_dropped_fails(self) -> None:
        """A justification may not outlive the hole it justifies."""

        def mutate(path, record):
            if path.name == "appraisal-result-v1.schema.json":
                del record["properties"]["evaluated"]["properties"][
                    "anomaly_disposition"
                ]
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_json=mutate)

    def test_a_public_operation_fails(self) -> None:
        def mutate(path, spec):
            if path.name != "openapi-v1.yaml":
                return spec
            self._operation(spec)["security"] = []
            return spec

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_yaml=mutate)

    def test_a_widened_disclosure_audience_fails(self) -> None:
        def mutate(path, record):
            if path.name == "disclosure-projection-v1.json":
                for projection in record["projections"]:
                    if projection["api_schema"] == "AppraisalSummary":
                        projection["audience"] = "public"
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_json=mutate)

    def test_an_unclassified_shape_fails(self) -> None:
        def mutate(path, record):
            if path.name == "disclosure-projection-v1.json":
                record["projections"] = [
                    item
                    for item in record["projections"]
                    if item["api_schema"] != "AppraisalSummary"
                ]
            return record

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_json=mutate)

    def test_a_narrowed_enum_fails(self) -> None:
        def mutate(path, spec):
            if path.name != "openapi-v1.yaml":
                return spec
            summary = spec["components"]["schemas"]["AppraisalSummary"]
            summary["properties"]["ranking_eligibility"]["enum"].remove("quarantined")
            return spec

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_yaml=mutate)

    def test_an_optional_projected_field_fails(self) -> None:
        def mutate(path, spec):
            if path.name != "openapi-v1.yaml":
                return spec
            summary = spec["components"]["schemas"]["AppraisalSummary"]
            summary["required"].remove("reason_codes")
            return spec

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_yaml=mutate)

    def test_removing_the_operation_fails(self) -> None:
        def mutate(path, spec):
            if path.name != "openapi-v1.yaml":
                return spec
            del spec["paths"]["/appraisals/{id}"]
            return spec

        with self.assertRaises(self.validator.ValidationFailure):
            self._run(mutate_yaml=mutate)


if __name__ == "__main__":
    unittest.main()
