"""Tests for the D-223 operation-class and error-matrix stage.

These prove the stage fails when the OpenAPI document and the reason registry disagree.
They are not evidence that any handler returns any of the statuses described.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
SCHEMAS = ROOT / "packages" / "schemas"


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


class ApiErrorMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.directory = Path(tempfile.mkdtemp(prefix="api-error-matrix-"))
        self.addCleanup(shutil.rmtree, self.directory, True)
        for name in ("openapi-v1.yaml", "reason-codes-v1.json"):
            shutil.copyfile(SCHEMAS / name, self.directory / name)
        self.validator.SCHEMAS = self.directory

    @property
    def openapi_path(self) -> Path:
        return self.directory / "openapi-v1.yaml"

    @property
    def registry_path(self) -> Path:
        return self.directory / "reason-codes-v1.json"

    def read_openapi(self) -> dict:
        return yaml.safe_load(self.openapi_path.read_text(encoding="utf-8"))

    def write_openapi(self, spec: dict) -> None:
        self.openapi_path.write_text(yaml.dump(spec, sort_keys=False), encoding="utf-8")

    def read_registry(self) -> dict:
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def write_registry(self, registry: dict) -> None:
        self.registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    def assert_fails(self, fragment: str) -> None:
        with self.assertRaises(self.validator.ValidationFailure) as caught:
            self.validator.validate_api_error_matrix()
        self.assertIn(fragment, str(caught.exception))

    def test_committed_contract_passes(self) -> None:
        self.validator.validate_api_error_matrix()

    def test_missing_declared_status_fails(self) -> None:
        spec = self.read_openapi()
        del spec["paths"]["/sessions"]["get"]["responses"]["401"]
        self.write_openapi(spec)
        self.assert_fails(
            "4xx declaration differs from the reason matrix: listSessions"
        )

    def test_undeclared_extra_status_fails(self) -> None:
        spec = self.read_openapi()
        spec["paths"]["/sessions"]["get"]["responses"]["409"] = {
            "$ref": "#/components/responses/Conflict"
        }
        self.write_openapi(spec)
        self.assert_fails("only-in-openapi=[409]")

    def test_inline_problem_response_fails(self) -> None:
        spec = self.read_openapi()
        spec["paths"]["/sessions"]["get"]["responses"]["401"] = {
            "description": "inline",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/Problem"}}
            },
        }
        self.write_openapi(spec)
        self.assert_fails("answers 401 with an inline response")

    def test_document_level_security_fails(self) -> None:
        spec = self.read_openapi()
        spec["security"] = [{"bearerAuth": []}]
        for item in spec["paths"].values():
            for method, operation in item.items():
                if method in {"get", "post", "put", "patch", "delete"}:
                    operation.pop("security", None)
        self.write_openapi(spec)
        self.assert_fails("inherits a document-level security requirement")

    def test_stale_operation_class_membership_fails(self) -> None:
        registry = self.read_registry()
        registry["operation_classes"]["collection"].remove("listFriends")
        self.write_registry(registry)
        self.assert_fails(
            "operation class collection differs from the OpenAPI document"
        )

    def test_unknown_operation_in_a_code_fails(self) -> None:
        registry = self.read_registry()
        registry["codes"][-1]["operations"] = ["noSuchOperation"]
        self.write_registry(registry)
        self.assert_fails("names operations the API does not declare")

    def test_unknown_operation_class_in_a_code_fails(self) -> None:
        registry = self.read_registry()
        registry["codes"][-1]["operation_classes"] = ["no-such-class"]
        self.write_registry(registry)
        self.assert_fails("names an unknown operation class")

    def test_status_on_a_non_wire_transport_fails(self) -> None:
        registry = self.read_registry()
        for code in registry["codes"]:
            if code["transport"] == "claim-rejection":
                code["http_status"] = 422
                break
        self.write_registry(registry)
        self.assert_fails("carries a status but never reaches the wire")

    def test_problem_transport_without_a_status_fails(self) -> None:
        registry = self.read_registry()
        for code in registry["codes"]:
            if code["transport"] == "problem":
                code["http_status"] = None
                break
        self.write_registry(registry)
        self.assert_fails("problem-transport code lacks a status")


if __name__ == "__main__":
    unittest.main()
