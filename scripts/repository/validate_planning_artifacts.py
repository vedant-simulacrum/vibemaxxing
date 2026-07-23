#!/usr/bin/env python3
"""Validate current planning schemas, registries, examples, and structural DDL.

These checks prove syntax and declared cross-file invariants only. They do not make
blocked planning placeholders implementation-ready or constitute security evidence.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import psycopg
import yaml
from cddlparser import parse as parse_cddl
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate as validate_openapi

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
CONFORMANCE = ROOT / "conformance"
FORMAT_CHECKER = FormatChecker()


class ValidationFailure(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationFailure(f"invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationFailure(f"invalid YAML: {path.relative_to(ROOT)}: {exc}") from exc


def validate_schema_file(path: Path) -> dict[str, Any]:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def validate_instance(schema: dict[str, Any], instance: Any, label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors[:8])
        raise ValidationFailure(f"{label} failed schema validation: {details}")


def expect_invalid(schema: dict[str, Any], instance: Any, label: str) -> None:
    if not list(Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(instance)):
        raise ValidationFailure(f"negative fixture unexpectedly validated: {label}")


def assert_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValidationFailure(f"duplicate values in {label}")


def validate_json_schemas_and_examples() -> None:
    adapter_schema = validate_schema_file(SCHEMAS / "adapter-manifest.schema.json")
    event_schema = validate_schema_file(SCHEMAS / "normalized-event.schema.json")
    agent_schema = validate_schema_file(CONFORMANCE / "adapters" / "agent-registry-v1.schema.json")
    anti_schema = validate_schema_file(CONFORMANCE / "adversarial" / "anti-cheat-registry-v1.schema.json")

    validate_instance(adapter_schema, load_json(SCHEMAS / "examples" / "adapter-manifest.valid.json"), "valid adapter manifest")
    validate_instance(event_schema, load_json(SCHEMAS / "examples" / "normalized-event.valid.json"), "valid normalized event")
    expect_invalid(
        event_schema,
        load_json(SCHEMAS / "examples" / "normalized-event.invalid-forbidden-field.json"),
        "forbidden normalized-event field",
    )

    agent_registry = load_json(CONFORMANCE / "adapters" / "agent-registry-v1.json")
    anti_registry = load_json(CONFORMANCE / "adversarial" / "anti-cheat-registry-v1.json")
    validate_instance(agent_schema, agent_registry, "agent registry")
    validate_instance(anti_schema, anti_registry, "adversarial registry")

    family_ids = [item["id"] for item in agent_registry["families"]]
    product_ids = [item["id"] for item in agent_registry["products"]]
    assert_unique(family_ids, "agent family IDs")
    assert_unique(product_ids, "agent product IDs")
    families = set(family_ids)
    tiers = set(agent_registry["support_tiers"])
    for product in agent_registry["products"]:
        if product["family"] not in families:
            raise ValidationFailure(f"unknown family for {product['id']}")
        if product["target_tier"] not in tiers:
            raise ValidationFailure(f"unknown target tier for {product['id']}")
        for certification in product["certifications"]:
            if certification["tier"] not in tiers:
                raise ValidationFailure(f"unknown certification tier for {product['id']}")

    reason_registry = load_json(SCHEMAS / "reason-codes-v1.json")
    reason_codes = [item["code"] for item in reason_registry["codes"]]
    assert_unique(reason_codes, "reason codes")
    reason_set = set(reason_codes)
    actions = set(anti_registry["actions"])
    case_ids = [item["id"] for item in anti_registry["cases"]]
    assert_unique(case_ids, "adversarial case IDs")
    for case in anti_registry["cases"]:
        if case["expected_action"] not in actions:
            raise ValidationFailure(f"unknown action in {case['id']}")
        if case["reason_code"] not in reason_set:
            raise ValidationFailure(f"unknown reason code in {case['id']}")
        fixture = ROOT / case["fixture"]
        if case["status"] != "planned" and not fixture.is_file():
            raise ValidationFailure(f"non-planned adversarial case lacks fixture: {case['id']}")


def validate_policy_and_observability() -> None:
    policies = load_json(SCHEMAS / "policy-defaults-v1.json")
    required = {
        "overtake_notification_hysteresis_hours", "overtake_material_lead_tokens",
        "friend_request_expiry_days", "handle_rename_cooldown_days", "old_handle_redirect_days",
        "presence_heartbeat_seconds", "presence_lease_expiry_seconds", "presence_idle_after_seconds",
        "standard_claim_lateness_seconds", "challenge_expiry_seconds", "batch_max_claims",
        "batch_max_encoded_bytes", "public_cache_stale_seconds",
        "moderation_ordinary_review_target_hours", "security_audit_retention_days",
        "operational_telemetry_retention_days",
    }
    keys = set(policies["policies"])
    missing = required - keys
    if missing:
        raise ValidationFailure(f"missing required policies: {sorted(missing)}")
    forbidden = {key for key in keys if key.startswith("country_")}
    if forbidden:
        raise ValidationFailure(f"post-launch country policies remain in launch defaults: {sorted(forbidden)}")
    for key, policy in policies["policies"].items():
        if not policy["min"] <= policy["value"] <= policy["max"]:
            raise ValidationFailure(f"policy default outside range: {key}")
        if not policy["owner"]:
            raise ValidationFailure(f"policy lacks owner: {key}")

    allowlist = load_yaml(SCHEMAS / "observability-allowlist-v1.yaml")
    if allowlist.get("policy") != "deny-by-default":
        raise ValidationFailure("observability policy must be deny-by-default")
    allowed = allowlist.get("allowed_attributes", [])
    forbidden_classes = allowlist.get("forbidden_classes", [])
    assert_unique(allowed, "observability allowed attributes")
    assert_unique(forbidden_classes, "observability forbidden classes")
    prohibited = {"prompt", "response", "transcript", "code", "path", "repository_name", "claim_payload"}
    overlap = prohibited & set(allowed)
    if overlap:
        raise ValidationFailure(f"forbidden attributes present in allowlist: {sorted(overlap)}")
    if allowlist["retention_days"]["operational_detail"] != policies["policies"]["operational_telemetry_retention_days"]["value"]:
        raise ValidationFailure("operational telemetry retention disagrees with policy registry")
    if allowlist["retention_days"]["security_audit"] != policies["policies"]["security_audit_retention_days"]["value"]:
        raise ValidationFailure("security audit retention disagrees with policy registry")


def validate_openapi_file() -> None:
    spec = load_yaml(SCHEMAS / "openapi-v1.yaml")
    validate_openapi(spec)
    paths = set(spec.get("paths", {}))
    required = {"/claim-challenges", "/claim-batches", "/leaderboards/{scope}/{period}", "/rank/me", "/deletion-requests"}
    missing = required - paths
    if missing:
        raise ValidationFailure(f"OpenAPI missing planning-critical paths: {sorted(missing)}")
    if "/countries" in paths:
        raise ValidationFailure("country route remains in launch OpenAPI despite D-052")
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            if method.lower() in {"get", "post", "put", "patch", "delete"} and "responses" not in operation:
                raise ValidationFailure(f"OpenAPI operation lacks responses: {method.upper()} {path}")


def validate_cddl_file() -> None:
    text = (SCHEMAS / "vibeproof-claim-v1.cddl").read_text(encoding="utf-8")
    parse_cddl(text)
    for required_rule in ("vibeproof-claim-v1", "token-categories", "batch-context", "gap-declaration"):
        if f"{required_rule} =" not in text:
            raise ValidationFailure(f"CDDL missing rule: {required_rule}")


def validate_protobuf_files() -> None:
    files = [SCHEMAS / "local-control-v1.proto", SCHEMAS / "social-integrity-events-v1.proto"]
    with tempfile.TemporaryDirectory() as temp_dir:
        result = subprocess.run(
            [sys.executable, "-m", "grpc_tools.protoc", f"-I{SCHEMAS}", f"--python_out={temp_dir}", *(str(path) for path in files)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise ValidationFailure(f"Protobuf compilation failed: {result.stderr.strip()}")


def validate_postgres_ddl(database_url: str) -> None:
    sql = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
    if "BLOCKED STRUCTURAL PLANNING PLACEHOLDER" not in sql:
        raise ValidationFailure("planning SQL must declare its blocked structural maturity")
    if re.search(r"(?im)^create\s+table\s+country_assertions\b", sql):
        raise ValidationFailure("country_assertions remains in launch SQL")
    if re.search(r"board_type\s+in\s*\([^)]*'country'", sql, flags=re.IGNORECASE | re.DOTALL):
        raise ValidationFailure("country remains an allowed launch board type")
    try:
        with psycopg.connect(database_url, autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute("drop schema if exists planning_validation cascade")
                cursor.execute("create schema planning_validation")
                cursor.execute("set search_path to planning_validation")
                cursor.execute(sql)
                cursor.execute("select count(*) from information_schema.tables where table_schema = 'planning_validation'")
                table_count = cursor.fetchone()[0]
                if table_count < 40:
                    raise ValidationFailure(f"planning DDL created too few structural tables: {table_count}")
                cursor.execute("drop schema planning_validation cascade")
    except ValidationFailure:
        raise
    except Exception as exc:
        raise ValidationFailure(f"PostgreSQL DDL validation failed: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("PLANNING_DATABASE_URL"))
    parser.add_argument("--allow-no-postgres", action="store_true")
    args = parser.parse_args()

    checks = [
        ("JSON schemas, examples, and registries", validate_json_schemas_and_examples),
        ("policy and observability artifacts", validate_policy_and_observability),
        ("OpenAPI", validate_openapi_file),
        ("CDDL", validate_cddl_file),
        ("Protobuf", validate_protobuf_files),
    ]
    failures: list[str] = []
    for label, function in checks:
        try:
            function()
            print(f"PASS: {label}")
        except Exception as exc:
            failures.append(f"FAIL: {label}: {exc}")

    if args.database_url:
        try:
            validate_postgres_ddl(args.database_url)
            print("PASS: PostgreSQL structural planning DDL")
        except Exception as exc:
            failures.append(f"FAIL: PostgreSQL structural planning DDL: {exc}")
    elif args.allow_no_postgres:
        print("SKIP: PostgreSQL structural planning DDL (no database URL)")
    else:
        failures.append("FAIL: PostgreSQL structural planning DDL: database URL required")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("planning artifact validation: pass")
    print("artifact maturity: structural planning only; implementation remains unauthorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
