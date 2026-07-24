#!/usr/bin/env python3
"""Validate P-1140E structural consistency without claiming semantic or runtime proof."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
CONF = ROOT / "conformance" / "p1140e"
TRACE = ROOT / "docs" / "planning" / "decision-traceability"


class Failure(RuntimeError):
    pass


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def main() -> int:
    schema = load_json(CONF / "validation-matrix-v1.schema.json")
    matrix = load_json(CONF / "validation-matrix-v1.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(matrix),
        key=lambda item: list(item.absolute_path),
    )
    require(not errors, "validation matrix schema failure: " + "; ".join(e.message for e in errors[:8]))
    require(matrix["maturity"] == "planning-validation-only", "matrix must remain planning-validation-only")

    decision_text = (ROOT / "docs/planning/DECISION_REGISTER.md").read_text(encoding="utf-8")
    decision_statuses: dict[str, str] = {}
    allowed = {"accepted", "provisional", "research-required", "deferred", "rejected", "superseded"}
    for line in decision_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"D-\d{3}", cells[0]) and cells[2] in allowed:
            decision_statuses[cells[0]] = cells[2]

    expected_decisions = {f"D-{number:03d}" for number in range(1, 70)}
    require(set(decision_statuses) == expected_decisions, "decision register is not exactly D-001..D-069")

    bindings = {item["decision_id"]: item for item in matrix["decision_bindings"]}
    require(set(bindings) == expected_decisions, "matrix decision set is not exactly D-001..D-069")
    for decision_id, status in decision_statuses.items():
        binding = bindings[decision_id]
        require(binding["decision_status"] == status, f"status mismatch for {decision_id}")
        require(binding["active"] == (status in {"accepted", "provisional"}), f"active-path mismatch for {decision_id}")
        for field in ("normative_owner", "work_unit", "schema_or_state_owner", "platform_scope", "fixture_path"):
            require(bool(binding[field]), f"{decision_id} lacks {field}")
            require((ROOT / binding[field].split("#", 1)[0]).exists(), f"{decision_id} references missing {field}")

    trace_ids: list[str] = []
    for path in sorted(TRACE.glob("D-*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\|\s*(D-\d{3})\s*\|", line)
            if match:
                trace_ids.append(match.group(1))
    require(set(trace_ids) == expected_decisions, "traceability files do not cover D-001..D-069")
    require(len(trace_ids) == len(set(trace_ids)), "duplicate decision traceability row")

    required_domains = {
        "decision-traceability", "protocol-exact-bytes", "protocol-malformed-resource",
        "accounting", "privacy-boundaries", "oauth-session-identity", "api-idempotency-rate",
        "sql-constraints-races", "ranking-pricing", "social-moderation", "export-deletion",
        "platform-profile-coverage", "platform-runtime-evidence", "release-update",
        "reason-policy-references", "registry-references", "current-future-paths", "clean-checkout",
    }
    require({item["domain_id"] for item in matrix["validation_domains"]} == required_domains, "validation domain set mismatch")
    for domain in matrix["validation_domains"]:
        for path in domain["authorities"] + domain["fixtures"]:
            require((ROOT / path).exists(), f"{domain['domain_id']} references missing path {path}")

    spec = yaml.safe_load((SCHEMAS / "openapi-v1.yaml").read_text(encoding="utf-8"))
    operation_ids: list[str] = []
    for item in spec["paths"].values():
        for method, operation in item.items():
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                operation_ids.append(operation["operationId"])
    require(len(operation_ids) == len(set(operation_ids)), "duplicate OpenAPI operationId")
    require(set(matrix["api_operations"]) == set(operation_ids), "matrix does not cover every API operation")

    state_registry = load_json(SCHEMAS / "state-machine-registry-v1.json")
    machines = {item["machine_id"]: item for item in state_registry["machines"]}
    require(set(matrix["state_machines"]) == set(machines), "matrix does not cover every state machine")
    state_fixtures = load_json(CONF / "state-machine-fixtures-v1.json")
    fixture_machines = {item["machine_id"]: item for item in state_fixtures["machines"]}
    require(set(fixture_machines) == set(machines), "state fixture set mismatch")
    for machine_id, fixture in fixture_machines.items():
        transitions = {item["transition_id"]: item for item in machines[machine_id]["transitions"]}
        positive = fixture["positive"]
        require(positive["transition_id"] in transitions, f"unknown positive transition for {machine_id}")
        transition = transitions[positive["transition_id"]]
        require(positive["from"] in transition["from"] and positive["expected_to"] == transition["to"], f"invalid positive fixture for {machine_id}")
        negative = fixture["negative"]
        require(negative["from"] not in transition["from"], f"negative fixture is legal for {machine_id}")

    sql = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
    tables = set(re.findall(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(", sql))
    races = load_json(CONF / "sql-race-plans-v1.json")
    required_races = {
        "oauth-single-consume", "refresh-parent-reuse", "challenge-single-use",
        "idempotency-same-bytes", "idempotency-conflict", "device-sequence-fork",
        "friend-cross-request", "block-race", "board-owner-transfer",
        "ranking-generation-promote", "moderation-appeal-reversal",
        "deletion-export-race", "local-delete-ack", "release-promote-rollback",
    }
    require({item["case_id"] for item in races["cases"]} == required_races, "SQL race plan set mismatch")
    for case in races["cases"]:
        require(set(case["tables"]) <= tables, f"SQL race references unknown table: {case['case_id']}")
        require(case["execution_state"] == "planned-runtime-evidence", "SQL race plan overclaims execution")

    platform_registry = load_json(SCHEMAS / "platform-profile-registry-v1.json")
    profiles = {item["profile_id"]: item for item in platform_registry["profiles"]}
    require(set(matrix["platform_profiles"]) == set(profiles), "matrix does not cover every platform profile")
    plan = load_json(CONF / "platform-validation-plan-v1.json")
    planned_profiles = {item["profile_id"]: item for item in plan["profiles"]}
    require(set(planned_profiles) == set(profiles), "platform validation plan set mismatch")
    for profile_id, planned in planned_profiles.items():
        source = profiles[profile_id]
        require(not source["advertised"] and not planned["advertised"], f"uncertified profile advertised: {profile_id}")
        expected = {(item["case_id"], item["applicability"], item["expected"]) for item in source["failure_matrix"]}
        actual = {(item["case_id"], item["applicability"], item["expected"]) for item in planned["cases"]}
        require(actual == expected, f"platform case mismatch: {profile_id}")
        require(all(item["execution_state"] == "planned-runtime-evidence" for item in planned["cases"]), f"platform plan overclaims execution: {profile_id}")

    reason_registry = load_json(SCHEMAS / "reason-codes-v1.json")
    allowed_authorities = set(machines) | {"vibeproof-v1", "device-lineage-v1", "server-runtime"}
    for item in reason_registry["codes"]:
        require(item["state_machine"] in allowed_authorities, f"reason authority does not resolve: {item['code']}")

    structural_audit = (ROOT / "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md").read_text(encoding="utf-8").lower()
    require("structural p0 open: 0" in structural_audit and "structural p1 open: 0" in structural_audit, "structural audit is not closed")
    require("semantic correctness" in structural_audit and "p-1140f" in structural_audit, "structural audit overstates its claim scope")

    semantic_review = (ROOT / "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md").read_text(encoding="utf-8").lower()
    require("semantic p1 open: 4" in semantic_review, "semantic review must retain the four open P1 findings")
    require("p-1104: blocked" in semantic_review, "semantic review must keep P-1104 blocked")
    for finding in ("sr-001", "sr-002", "sr-003", "sr-004"):
        require(finding in semantic_review, f"semantic review is missing {finding}")

    forbidden = [
        ROOT / "apps/android", ROOT / "apps/ios", ROOT / "apps/ipados", ROOT / "apps/chromeos",
        ROOT / "packages/android", ROOT / "packages/ios", ROOT / "packages/ipados", ROOT / "packages/chromeos",
    ]
    require(not any(path.exists() for path in forbidden), "out-of-scope native mobile implementation path exists")

    print("P-1140E structural cross-contract validation: pass")
    print(f"decisions={len(bindings)} operations={len(operation_ids)} machines={len(machines)} profiles={len(profiles)} races={len(races['cases'])}")
    print("claim_scope=structural-consistency-only semantic_gate=P-1140F-open runtime_evidence=absent")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P-1140E structural cross-contract validation: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
