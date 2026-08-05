#!/usr/bin/env python3
"""Read-only repository authority and phase checks.

Deep contract, schema, protocol, API, SQL, fixture and P-1140F registry semantics
are owned by specialized validators. This doctor checks stable repository
boundaries and does not parse prose as the source of finding truth.

Phase and gate state are owned by `conformance/p1140f/gate-authorization-v1.json`
and are never encoded in this file. This doctor derives the expected state from
that record and then checks that prose agrees with it, so opening or closing a
gate is a data edit and never an edit to the validator that enforces the gate.

This module must keep running with no third-party dependencies: CI invokes it
before installing anything. Only the standard library may be imported.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PHASE_RECORD = "conformance/p1140f/gate-authorization-v1.json"

PHASES = {"planning-contract-repair", "implementation"}

GATE_STATES = {
    "complete-planning",
    "in-progress-planning",
    "blocked-planning",
    "blocked-implementation",
    "blocked-approval",
    "blocked-launch-evidence",
    "authorized-open",
}

FINDING_STATES = {
    "open",
    "repair-in-progress",
    "repaired-pending-review",
    "closed",
    "deferred",
    "superseded",
}

AUTHORIZATION_FIELDS = (
    "authorized_by",
    "authorized_at",
    "reference",
    "reference_kind",
    "open_p1_findings_at_authorization",
    "opened_with_open_findings",
    "findings_waived",
    "acknowledgement",
)

GATE_PATTERN = re.compile(r"^P-[0-9]{4}[A-Z]?$")
DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

REQUIRED = [
    "AGENTS.md",
    "docs/project/PROJECT.md",
    "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md",
    "docs/planning/DECISION_REGISTER.md",
    "docs/planning/TASK_CATALOG.md",
    "docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md",
    "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md",
    "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
    "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
    "conformance/p1140f/semantic-findings-v1.schema.json",
    "conformance/p1140f/semantic-findings-v1.json",
    "conformance/p1140f/artifact-authority-v1.schema.json",
    "conformance/p1140f/artifact-authority-v1.json",
    "conformance/p1140f/contract-bundles-v1.schema.json",
    "conformance/p1140f/contract-bundles-v1.json",
    "conformance/p1140f/review-target-v1.schema.json",
    "conformance/p1140f/review-target-v1.json",
    "conformance/p1140f/gate-authorization-v1.schema.json",
    "conformance/p1140f/gate-authorization-v1.json",
    "scripts/repository/validate_p1140f_authority.py",
    ".github/workflows/planning-checks.yml",
    ".github/workflows/storyboard-visuals.yml",
]

FORBIDDEN = [
    "PROJECT_CONTEXT.md",
    "PROJECT_INSTRUCTIONS.md",
    "CURRENT_STATUS.md",
    "MODEL_OPERATING_MANUAL.md",
    "IMPLEMENTATION_ROADMAP.md",
    "RESEARCH_AND_EVIDENCE_BACKLOG.md",
    "START_HERE_PROMPT.md",
    "CHATGPT_WORK_PROJECT_PROMPT.md",
    "docs/implementation/BUILD_PLAN.md",
    "docs/implementation/TECH_STACK.md",
    "docs/planning/SPECIFICATION_INDEX.md",
    "docs/planning/DEPENDENCY_MAP.md",
    "docs/planning/PLANNING_AUDIT.md",
]

OUT_OF_SCOPE_NATIVE_PATHS = [
    "apps/android",
    "apps/ios",
    "apps/ipados",
    "apps/chromeos",
    "packages/android",
    "packages/ios",
    "packages/ipados",
    "packages/chromeos",
]


class RecordError(Exception):
    """The phase record is absent, unreadable, or structurally invalid."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecordError(f"{label} must be a non-empty string")
    return value


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RecordError(f"{label} must be a non-negative integer")
    return value


def _mapping(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise RecordError(f"{label} must be an object")
    return value


def _sequence(value: object, label: str, minimum: int = 0) -> list:
    if not isinstance(value, list) or len(value) < minimum:
        raise RecordError(f"{label} must be an array with at least {minimum} entries")
    return value


def _strings(value: object, label: str, minimum: int = 0) -> list[str]:
    return [
        _text(item, f"{label}[{index}]")
        for index, item in enumerate(_sequence(value, label, minimum))
    ]


def load_record(root: Path, relative_path: str = PHASE_RECORD) -> dict:
    """Read and structurally validate the phase record, failing closed."""
    path = root / relative_path
    if not path.is_file():
        raise RecordError(f"missing phase record: {relative_path}")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RecordError(
            f"unreadable phase record {relative_path}: {error}"
        ) from error

    record = _mapping(record, relative_path)
    if record.get("schema_version") != 1:
        raise RecordError(f"{relative_path} must declare schema_version 1")
    if record.get("phase") not in PHASES:
        raise RecordError(
            f"{relative_path} declares unknown phase: {record.get('phase')!r}"
        )
    if not DATE_PATTERN.match(_text(record.get("recorded_at"), "recorded_at")):
        raise RecordError("recorded_at must be an ISO date")
    _text(record.get("finding_registry"), "finding_registry")
    _strings(record.get("registry_summary_documents"), "registry_summary_documents", 1)
    for index, pattern in enumerate(
        _strings(record.get("open_p1_claim_patterns"), "open_p1_claim_patterns", 1)
    ):
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
        except re.error as error:
            raise RecordError(
                f"open_p1_claim_patterns[{index}] is not a regular expression: {error}"
            ) from error
        if compiled.groups != 1:
            raise RecordError(
                f"open_p1_claim_patterns[{index}] must have exactly one capturing group"
            )

    baseline = _mapping(record.get("open_p1_baseline"), "open_p1_baseline")
    if baseline.get("severity") != "P1":
        raise RecordError("open_p1_baseline.severity must be P1")
    if baseline.get("rule") != "non-regression":
        raise RecordError("open_p1_baseline.rule must be non-regression")
    _integer(baseline.get("count"), "open_p1_baseline.count")
    counted = _strings(
        baseline.get("counted_states"), "open_p1_baseline.counted_states", 1
    )
    unknown = sorted(set(counted) - FINDING_STATES)
    if unknown:
        raise RecordError(
            f"open_p1_baseline.counted_states has unknown states: {unknown}"
        )

    gates = _sequence(record.get("gates"), "gates", 1)
    seen: set[str] = set()
    for index, gate in enumerate(gates):
        gate = _mapping(gate, f"gates[{index}]")
        identifier = _text(gate.get("gate"), f"gates[{index}].gate")
        if not GATE_PATTERN.match(identifier):
            raise RecordError(
                f"gates[{index}].gate is not a gate identifier: {identifier}"
            )
        if identifier in seen:
            raise RecordError(f"duplicate gate entry: {identifier}")
        seen.add(identifier)
        if gate.get("state") not in GATE_STATES:
            raise RecordError(
                f"{identifier} declares unknown state: {gate.get('state')!r}"
            )
        if "authorization" not in gate:
            raise RecordError(
                f"{identifier} must declare authorization, explicitly null when absent"
            )
        _validate_authorization(identifier, gate)
        for position, document in enumerate(
            _sequence(gate.get("documents"), f"{identifier}.documents")
        ):
            document = _mapping(document, f"{identifier}.documents[{position}]")
            _text(document.get("path"), f"{identifier}.documents[{position}].path")
            _strings(
                document.get("requires"), f"{identifier}.documents[{position}].requires"
            )
            _strings(
                document.get("forbids"), f"{identifier}.documents[{position}].forbids"
            )
    return record


def _validate_authorization(identifier: str, gate: dict) -> None:
    authorization = gate.get("authorization")
    if authorization is None:
        if gate.get("state") == "authorized-open":
            raise RecordError(
                f"{identifier} is authorized-open without an authorization record"
            )
        return
    authorization = _mapping(authorization, f"{identifier}.authorization")
    missing = [field for field in AUTHORIZATION_FIELDS if field not in authorization]
    if missing:
        raise RecordError(f"{identifier}.authorization is missing fields: {missing}")
    _text(authorization["authorized_by"], f"{identifier}.authorization.authorized_by")
    if not DATE_PATTERN.match(
        _text(
            authorization["authorized_at"], f"{identifier}.authorization.authorized_at"
        )
    ):
        raise RecordError(
            f"{identifier}.authorization.authorized_at must be an ISO date"
        )
    _text(authorization["reference"], f"{identifier}.authorization.reference")
    _text(authorization["reference_kind"], f"{identifier}.authorization.reference_kind")
    _text(
        authorization["acknowledgement"], f"{identifier}.authorization.acknowledgement"
    )
    open_at_authorization = _integer(
        authorization["open_p1_findings_at_authorization"],
        f"{identifier}.authorization.open_p1_findings_at_authorization",
    )
    if not isinstance(authorization["opened_with_open_findings"], bool):
        raise RecordError(
            f"{identifier}.authorization.opened_with_open_findings must be a boolean"
        )
    if authorization["findings_waived"] is not False:
        raise RecordError(
            f"{identifier}.authorization.findings_waived must be false; findings are never waived"
        )
    if authorization["opened_with_open_findings"] != (open_at_authorization > 0):
        raise RecordError(
            f"{identifier}.authorization contradicts itself: opened_with_open_findings does not match the recorded count"
        )


def open_p1_count(root: Path, record: dict) -> int:
    """Count active P1 findings in the registry named by the phase record."""
    relative_path = record["finding_registry"]
    path = root / relative_path
    if not path.is_file():
        raise RecordError(f"missing finding registry: {relative_path}")
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RecordError(
            f"unreadable finding registry {relative_path}: {error}"
        ) from error
    findings = _sequence(
        _mapping(registry, relative_path).get("findings"),
        f"{relative_path}.findings",
        1,
    )
    counted = set(record["open_p1_baseline"]["counted_states"])
    total = 0
    for index, finding in enumerate(findings):
        finding = _mapping(finding, f"{relative_path}.findings[{index}]")
        _text(
            finding.get("finding_id"), f"{relative_path}.findings[{index}].finding_id"
        )
        if (
            finding.get("severity") == "P1"
            and _text(finding.get("state"), "state") in counted
        ):
            total += 1
    return total


def finding_identifiers(root: Path, record: dict) -> list[str]:
    registry = json.loads(
        (root / record["finding_registry"]).read_text(encoding="utf-8")
    )
    return [finding["finding_id"] for finding in registry["findings"]]


def check_documents(root: Path, gate: dict, errors: list[str]) -> None:
    identifier = gate["gate"]
    for document in gate["documents"]:
        relative_path = document["path"]
        path = root / relative_path
        if not path.is_file():
            errors.append(f"{identifier} names a missing document: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8").lower()
        if identifier.lower() not in text:
            errors.append(f"{relative_path} does not mention {identifier}")
        for token in document["requires"]:
            if token.lower() not in text:
                errors.append(
                    f"{relative_path} is missing required {identifier} token: {token}"
                )
        for token in document["forbids"]:
            if token.lower() in text:
                errors.append(
                    f"{relative_path} still carries superseded {identifier} token: {token}"
                )


def check_open_p1_claims(
    relative_path: str,
    text: str,
    active: int,
    patterns: list[re.Pattern[str]],
    errors: list[str],
) -> None:
    """Require every open-P1 count a document states to equal the live registry count.

    A bare substring search for the count is both too weak and too strong: `"12" in
    text` is satisfied by an unrelated `2026-07-12`, so a document could keep claiming
    13 while the registry held 12. Matching the claim itself, and reporting the number
    the document actually states, makes a stale count a precise and self-evident prose
    defect rather than a puzzle about which digits are missing.
    """
    claims = sorted(
        {int(match) for pattern in patterns for match in pattern.findall(text)}
    )
    if not claims:
        errors.append(
            f"{relative_path} states no open P1 count matching any recorded claim pattern"
        )
        return
    for claim in claims:
        if claim != active:
            errors.append(
                f"{relative_path} claims {claim} open P1 findings; the registry has {active}. "
                f"Update the prose, not the validator."
            )


def evaluate_phase(root: Path) -> tuple[list[str], str]:
    """Derive phase state from the record and check that prose agrees with it.

    Returns collected errors and a summary line. Any absent, unreadable or
    structurally invalid record is a single fatal error: the phase is never
    inferred from prose, and an unusable record never reads as an open gate.
    """
    errors: list[str] = []
    try:
        record = load_record(root)
        active = open_p1_count(root, record)
        identifiers = finding_identifiers(root, record)
    except RecordError as error:
        return [f"phase record is not usable: {error}"], "phase=unknown"

    baseline = record["open_p1_baseline"]["count"]
    if active > baseline:
        errors.append(
            f"active P1 findings regressed: {active} open exceeds the recorded baseline of {baseline} "
            f"in {PHASE_RECORD}"
        )

    patterns = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in record["open_p1_claim_patterns"]
    ]

    for gate in record["gates"]:
        check_documents(root, gate, errors)

    for relative_path in record["registry_summary_documents"]:
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing registry summary document: {relative_path}")
            continue
        raw = path.read_text(encoding="utf-8")
        text = raw.lower()
        for token in (identifiers[0], identifiers[-1]):
            if token.lower() not in text:
                errors.append(
                    f"{relative_path} does not summarize the finding registry: missing {token}"
                )
        check_open_p1_claims(relative_path, raw, active, patterns, errors)

    summary = "phase={} gates={} open_p1={}/{}".format(
        record["phase"],
        ",".join(f"{gate['gate']}:{gate['state']}" for gate in record["gates"]),
        active,
        baseline,
    )
    return errors, summary


def main() -> None:
    errors: list[str] = []
    summary = "phase=unknown"

    for path in REQUIRED:
        if not (ROOT / path).is_file():
            errors.append(f"missing required authority file: {path}")

    for path in FORBIDDEN + OUT_OF_SCOPE_NATIVE_PATHS:
        if (ROOT / path).exists():
            errors.append(f"forbidden or out-of-scope path exists: {path}")

    if not errors:
        phase_errors, summary = evaluate_phase(ROOT)
        errors.extend(phase_errors)

        storyboard = (ROOT / ".github/workflows/storyboard-visuals.yml").read_text(
            encoding="utf-8"
        )
        if re.search(r"(?m)^\s*push:\s*$", storyboard):
            errors.append("storyboard workflow must not run on push under ADR-014")
        if "apps/web/**" in storyboard:
            errors.append(
                "storyboard workflow must not include apps/web/** under ADR-014"
            )
        if "${{ secrets." in storyboard:
            errors.append("storyboard workflow must not access secrets under ADR-014")
        for marker in [
            "contents: read",
            "persist-credentials: false",
            "VIBEMAXXING_FIXTURE_POLICY: synthetic-only",
            "--bind 127.0.0.1",
            "VIBEMAXXING_ARTIFACT_MATURITY: runnable-prototype",
        ]:
            if marker not in storyboard:
                errors.append(
                    f"storyboard workflow is missing ADR-014 marker: {marker}"
                )

    if errors:
        print("Repository doctor: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    print("Repository doctor: PASS")
    print(summary)


if __name__ == "__main__":
    main()
