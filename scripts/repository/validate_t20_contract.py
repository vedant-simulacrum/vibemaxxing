#!/usr/bin/env python3
"""Validate the provisional D-046 T20 candidate artifacts without making launch claims."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "conformance" / "models"
CONTRACT = ROOT / "docs" / "integrations" / "T20_MODEL_HARDENING_CONTRACT.md"
SPEC = ROOT / "docs" / "integrations" / "T20_CERTIFICATION_AND_SELECTION_SPEC.md"
DECISIONS = ROOT / "docs" / "planning" / "DECISION_REGISTER.md"
FIXTURES = MODELS / "fixtures"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise RuntimeError(message)


def schema_errors(schema: dict, instance: object) -> list:
    return sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )


def main() -> int:
    registry_schema_path = MODELS / "t20-model-registry-v1.schema.json"
    registry_path = MODELS / "t20-model-registry-v1.json"
    optimization_schema_path = MODELS / "t20-optimization-evidence-v1.schema.json"
    valid_fixture_path = FIXTURES / "t20-optimization-evidence.valid.json"
    invalid_fixture_path = FIXTURES / "t20-optimization-evidence.invalid-pass.json"

    required_paths = (
        registry_schema_path, registry_path, optimization_schema_path,
        valid_fixture_path, invalid_fixture_path, CONTRACT, SPEC, DECISIONS,
    )
    for path in required_paths:
        if not path.is_file():
            fail(f"missing T20 candidate artifact: {path.relative_to(ROOT)}")

    registry_schema = load_json(registry_schema_path)
    optimization_schema = load_json(optimization_schema_path)
    registry = load_json(registry_path)
    valid_fixture = load_json(valid_fixture_path)
    invalid_fixture = load_json(invalid_fixture_path)

    Draft202012Validator.check_schema(registry_schema)
    Draft202012Validator.check_schema(optimization_schema)
    errors = schema_errors(registry_schema, registry)
    if errors:
        fail("T20 registry failed schema validation: " + "; ".join(error.message for error in errors[:8]))
    if schema_errors(optimization_schema, valid_fixture):
        fail("valid T20 optimization fixture failed schema validation")
    if not schema_errors(optimization_schema, invalid_fixture):
        fail("invalid T20 pass fixture unexpectedly validated")

    accounting = valid_fixture["accounting"]
    if accounting["passed_vectors"] != accounting["authoritative_vectors"]:
        fail("valid fixture does not pass every authoritative accounting vector")
    if accounting["fidelity_percent"] != 100:
        fail("valid fixture does not demonstrate exact accounting fidelity")
    if valid_fixture["coverage_depth"]["material_usage_coverage"] < 0.90:
        fail("valid fixture is below the candidate material-usage threshold")

    if registry["selection_status"] != "prelaunch-pending":
        fail("D-046 remains provisional, so the registry must remain prelaunch-pending")
    if registry["slots"] or registry["selection_runs"] or registry["accounting_profiles"]:
        fail("provisional registry must not contain invented selection or certification evidence")

    decision_line = next(
        (line for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.startswith("| D-046 |")),
        "",
    )
    if "| provisional |" not in decision_line:
        fail("decision register must keep D-046 provisional")

    contract = CONTRACT.read_text(encoding="utf-8")
    for phrase in (
        "D-046 is provisional", "not a public-launch dependency", "Exact certification tuple",
        "Source binding", "Device-key continuity", "Optimization evidence",
    ):
        if phrase.lower() not in contract.lower():
            fail(f"T20 candidate contract lacks {phrase!r}")

    spec = SPEC.read_text(encoding="utf-8")
    for phrase in (
        "provisional candidate specification",
        "model family × provider model ID × exact model version",
        "E1-provider-signed", "E6 can never enter active competition",
        "Missing usage is zero, never imputed from popularity",
        "Source precedence within one duplicate domain", "totals are not averaged",
        "Passing these checks proves planning consistency only",
    ):
        if phrase not in spec:
            fail(f"T20 candidate specification lacks {phrase!r}")

    required_evidence = {
        "accounting", "performance", "reliability", "coverage_depth",
        "user_experience", "maintenance", "result",
    }
    declared = set(optimization_schema.get("required", []))
    if not required_evidence <= declared:
        fail(f"optimization evidence schema is incomplete: {sorted(required_evidence - declared)}")

    print("T20 provisional planning validation: PASS")
    print("decision status: D-046 provisional")
    print("selection status: prelaunch-pending")
    print("implementation or launch evidence claimed: no")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"T20 provisional planning validation: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
