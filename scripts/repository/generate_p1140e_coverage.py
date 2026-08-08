#!/usr/bin/env python3
"""Regenerate the coverage arrays in the P-1140E validation matrix.

`conformance/p1140e/validation-matrix-v1.json` holds two different kinds of thing
under one filename. Its `decision_bindings` and `validation_domains` are a closed
program's evidence: D-001..D-069 as they stood when P-1140E completed, pinned to
exactly 69 entries by the schema, and they do not move again.

Its `api_operations`, `state_machines` and `platform_profiles` arrays are not that.
They are projections of three registries that are still being edited, and
`validate_p1140e_contracts.py` requires each to equal its registry exactly. So every
change that adds an OpenAPI operation, a state machine or a platform profile has to
edit this file too — which is why a file described everywhere as frozen has been
modified in nine commits since the gate closed.

The equality requirement is correct: a coverage array that does not cover everything
is not coverage. What was wrong was doing it by hand. A projection that can be
derived should never be typed, because typing it is how it drifts, and because the
resulting diff looks like someone amending a closed gate's evidence when they were
only keeping a derived list in step.

This regenerates the three arrays from their registries and leaves every other key
byte-identical. `--check` verifies the committed file already matches.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
MATRIX = ROOT / "conformance" / "p1140e" / "validation-matrix-v1.json"

# The three keys this owns. Everything else in the matrix is the frozen half and is
# copied through untouched.
DERIVED_KEYS = ("api_operations", "state_machines", "platform_profiles")

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def operation_ids() -> list[str]:
    """Every OpenAPI operationId, read the same way the validator reads them."""
    spec = yaml.safe_load((SCHEMAS / "openapi-v1.yaml").read_text(encoding="utf-8"))
    found: list[str] = []
    for item in spec["paths"].values():
        for method, operation in item.items():
            if method.lower() in HTTP_METHODS:
                found.append(operation["operationId"])
    return found


def machine_ids() -> list[str]:
    registry = json.loads(
        (SCHEMAS / "state-machine-registry-v1.json").read_text(encoding="utf-8")
    )
    return [machine["machine_id"] for machine in registry["machines"]]


def profile_ids() -> list[str]:
    registry = json.loads(
        (SCHEMAS / "platform-profile-registry-v1.json").read_text(encoding="utf-8")
    )
    return [profile["profile_id"] for profile in registry["profiles"]]


def derived() -> dict[str, list[str]]:
    """The three arrays as their registries currently define them.

    Sorted, because the array is a set the validator compares with `==` on sets and
    an arbitrary order would produce diff noise on every regeneration. Duplicates are
    a defect in the registry rather than something to silently collapse, so they are
    raised here instead of being deduplicated away.
    """
    result: dict[str, list[str]] = {}
    for key, values in (
        ("api_operations", operation_ids()),
        ("state_machines", machine_ids()),
        ("platform_profiles", profile_ids()),
    ):
        duplicates = sorted({v for v in values if values.count(v) > 1})
        if duplicates:
            raise SystemExit(
                f"{key}: the source registry declares duplicates {duplicates}; "
                "regenerating would hide a defect that belongs in the registry"
            )
        result[key] = sorted(values)
    return result


def regenerate() -> str:
    """The full matrix document with the three derived arrays refreshed."""
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    for key, values in derived().items():
        if key not in matrix:
            raise SystemExit(f"{MATRIX.name} has no {key} array to regenerate")
        matrix[key] = values
    return json.dumps(matrix, indent=2, ensure_ascii=False) + "\n"


def reproducible() -> bool:
    """Whether the committed matrix is exactly what a regeneration would write.

    Exists as a function rather than as a comparison inlined into
    `validate_p1140e_contracts.py` so that the wiring can be tested by patching
    `MATRIX`, instead of by asserting that the validator's source contains a
    particular string. A substring match is not a declaration.
    """
    return MATRIX.read_text(encoding="utf-8") == regenerate()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed matrix already matches, and change nothing",
    )
    arguments = parser.parse_args()

    generated = regenerate()
    current = MATRIX.read_text(encoding="utf-8")

    if arguments.check:
        if current != generated:
            print(
                "P-1140E coverage arrays are stale; run "
                "scripts/repository/generate_p1140e_coverage.py",
                file=sys.stderr,
            )
            return 1
        print(
            f"P-1140E coverage arrays: reproducible "
            f"({', '.join(f'{key}={len(json.loads(generated)[key])}' for key in DERIVED_KEYS)})"
        )
        return 0

    MATRIX.write_text(generated, encoding="utf-8")
    # `relative_to` raises when MATRIX has been pointed outside the repository, which
    # is exactly what a test that drives this path does. A progress message must not
    # be the reason a script cannot be tested.
    try:
        where: Path | str = MATRIX.relative_to(ROOT)
    except ValueError:
        where = MATRIX
    print(f"regenerated the coverage arrays in {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
