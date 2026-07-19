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


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    registry_schema_path = MODELS / "t20-model-registry-v1.schema.json"
    registry_path = MODELS / "t20-model-registry-v1.json"
    optimization_schema_path = MODELS / "t20-optimization-evidence-v1.schema.json"

    for path in (registry_schema_path, registry_path, optimization_schema_path, CONTRACT):
        if not path.is_file():
            fail(f"missing T20 artifact: {path.relative_to(ROOT)}")

    registry_schema = load_json(registry_schema_path)
    optimization_schema = load_json(optimization_schema_path)
    registry = load_json(registry_path)

    Draft202012Validator.check_schema(registry_schema)
    Draft202012Validator.check_schema(optimization_schema)

    errors = sorted(
        Draft202012Validator(registry_schema, format_checker=FormatChecker()).iter_errors(registry),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        fail("T20 registry failed schema validation: " + "; ".join(error.message for error in errors[:8]))

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
    required_phrases = (
        "T20 is the product's **golden path**",
        "Models outside T20 may still be supported",
        "minimum practical collection and synchronization overhead",
        "automatic detection, zero manual mapping",
        "Optimization evidence gates",
        "A slot cannot pass the T20 launch gate using only qualitative claims",
        "every slot passes the optimization evidence gates",
    )
    missing = [phrase for phrase in required_phrases if phrase not in contract]
    if missing:
        fail(f"T20 contract missing golden-path requirements: {missing}")

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
    print("implementation evidence claimed: no")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"T20 golden-path planning validation: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
