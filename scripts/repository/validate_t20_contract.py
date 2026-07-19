#!/usr/bin/env python3
"""Validate the T20 golden-path planning contract without claiming implementation evidence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "conformance" / "models"
CONTRACT = ROOT / "docs" / "integrations" / "T20_MODEL_HARDENING_CONTRACT.md"
SPEC = ROOT / "docs" / "integrations" / "T20_CERTIFICATION_AND_SELECTION_SPEC.md"
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
        registry_schema_path,
        registry_path,
        optimization_schema_path,
        valid_fixture_path,
        invalid_fixture_path,
        CONTRACT,
        SPEC,
    )
    for path in required_paths:
        if not path.is_file():
            fail(f"missing T20 artifact: {path.relative_to(ROOT)}")

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
        fail("valid fixture is below the T20 family material-usage threshold")

    slots = registry["slots"]
    ranks = [slot["rank"] for slot in slots]
    families = [slot["family_id"] for slot in slots]
    if len(ranks) != len(set(ranks)):
        fail("T20 registry has duplicate ranks")
    if len(families) != len(set(families)):
        fail("T20 registry has duplicate model families")

    status = registry["selection_status"]
    if status == "prelaunch-pending":
        if slots or registry["selection_runs"] or registry["accounting_profiles"]:
            fail("prelaunch-pending registry must not contain invented selection or certification evidence")
    elif status == "active":
        if len(slots) != 20 or sorted(ranks) != list(range(1, 21)):
            fail("active T20 registry must contain exactly ranks 1 through 20")
        if not registry["selection_runs"]:
            fail("active T20 registry requires an approved selection run")
        for slot in slots:
            if slot["status"] != "hardened":
                fail(f"active T20 slot is not hardened: {slot['family_id']}")
            if not slot["certifications"]:
                fail(f"active T20 slot lacks certification: {slot['family_id']}")
            if not slot["coverage_matrix"]:
                fail(f"active T20 slot lacks coverage matrix: {slot['family_id']}")

    contract = CONTRACT.read_text(encoding="utf-8")
    contract_phrases = (
        "T20 is the product's **golden path**",
        "Models outside T20 may still be supported",
        "minimum practical collection and synchronization overhead",
        "automatic detection, zero manual mapping",
        "Optimization evidence gates",
        "A slot cannot pass the T20 launch gate using only qualitative claims",
        "every slot passes the optimization evidence gates",
    )
    missing = [phrase for phrase in contract_phrases if phrase not in contract]
    if missing:
        fail(f"T20 contract missing golden-path requirements: {missing}")

    spec = SPEC.read_text(encoding="utf-8")
    spec_phrases = (
        "model family × provider model ID × exact model version",
        "E1-provider-signed",
        "E6 can never enter active competition",
        "0.40 × usage + 0.30 × agent/coding relevance",
        "Missing usage is zero, never imputed from popularity",
        "Source precedence within one duplicate domain",
        "totals are not averaged",
        "Passing these checks proves planning consistency only",
    )
    missing = [phrase for phrase in spec_phrases if phrase not in spec]
    if missing:
        fail(f"T20 certification/selection specification is incomplete: {missing}")

    evidence_required = {
        "accounting",
        "performance",
        "reliability",
        "coverage_depth",
        "user_experience",
        "maintenance",
        "result",
    }
    declared = set(optimization_schema.get("required", []))
    if not evidence_required <= declared:
        fail(f"optimization evidence schema is incomplete: {sorted(evidence_required - declared)}")

    print("T20 golden-path planning validation: PASS")
    print(f"selection status: {status}")
    print(f"declared slots: {len(slots)}")
    print("P-1130A..E planning artifacts: complete")
    print("implementation evidence claimed: no")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"T20 golden-path planning validation: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
