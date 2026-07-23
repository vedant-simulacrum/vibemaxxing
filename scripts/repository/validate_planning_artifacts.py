#!/usr/bin/env python3
"""Validate current planning schemas, registries, examples, and structural DDL.

These checks prove syntax and declared cross-file invariants only. They do not make
blocked planning placeholders implementation-ready or constitute security evidence.
"""
from __future__ import annotations

import argparse
import hashlib
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
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

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
    source_observation_schema = validate_schema_file(SCHEMAS / "source-observation.schema.json")
    detector_schema = validate_schema_file(SCHEMAS / "local-detector-result.schema.json")
    accounting_profile_schema = validate_schema_file(SCHEMAS / "accounting-profile.schema.json")
    device_lineage_schema = validate_schema_file(SCHEMAS / "device-lineage.schema.json")
    pricing_schema = validate_schema_file(SCHEMAS / "pricing-interpretation.schema.json")
    egress_schema = validate_schema_file(SCHEMAS / "egress-allowlist-v1.schema.json")
    agent_schema = validate_schema_file(CONFORMANCE / "adapters" / "agent-registry-v1.schema.json")
    anti_schema = validate_schema_file(CONFORMANCE / "adversarial" / "anti-cheat-registry-v1.schema.json")

    validate_instance(adapter_schema, load_json(SCHEMAS / "examples" / "adapter-manifest.valid.json"), "valid adapter manifest")
    validate_instance(event_schema, load_json(SCHEMAS / "examples" / "normalized-event.valid.json"), "valid normalized event")
    expect_invalid(
        event_schema,
        load_json(SCHEMAS / "examples" / "normalized-event.invalid-forbidden-field.json"),
        "forbidden normalized-event field",
    )

    accounting_registry = load_json(CONFORMANCE / "accounting" / "accounting-profiles-v1.json")
    accounting_cases = load_json(CONFORMANCE / "accounting" / "p1140b-accounting-cases-v1.json")
    privacy_cases = load_json(CONFORMANCE / "privacy" / "p1140b-boundary-canaries-v1.json")
    egress_registry = load_json(SCHEMAS / "egress-allowlist-v1.json")
    evidence_policy = load_json(SCHEMAS / "evidence-profile-policy-v1.json")

    validate_instance(egress_schema, egress_registry, "egress registry")
    for profile in accounting_registry["profiles"]:
        validate_instance(accounting_profile_schema, profile, f"accounting profile {profile['profile_id']}")
    assert_unique([profile["profile_id"] for profile in accounting_registry["profiles"]], "accounting profile IDs")
    assert_unique([case["case_id"] for case in accounting_cases["cases"]], "P-1140B accounting case IDs")
    required_accounting_cases = {
        "separate-cache-no-double-count", "inclusive-input-subtract-cache", "retry-distinct-execution",
        "cancelled-known-consumption", "local-token-ids", "contradictory-contained-counts",
    }
    missing_accounting = required_accounting_cases - {case["case_id"] for case in accounting_cases["cases"]}
    if missing_accounting:
        raise ValidationFailure(f"missing P-1140B accounting cases: {sorted(missing_accounting)}")

    required_privacy_boundaries = {
        "adapter", "ipc", "local-store", "detector", "claim", "http",
        "telemetry", "notification-delivery", "moderation", "export",
    }
    covered_boundaries = {case["boundary"] for case in privacy_cases["cases"]}
    if covered_boundaries != required_privacy_boundaries:
        raise ValidationFailure(
            f"privacy boundary coverage mismatch: missing={sorted(required_privacy_boundaries - covered_boundaries)}, "
            f"extra={sorted(covered_boundaries - required_privacy_boundaries)}"
        )
    for boundary in required_privacy_boundaries:
        outcomes = {case["expected"] for case in privacy_cases["cases"] if case["boundary"] == boundary}
        if not {"accept", "reject-before-egress"} <= outcomes:
            raise ValidationFailure(f"privacy boundary lacks positive/negative pair: {boundary}")

    if evidence_policy.get("authority") != "server-verifier":
        raise ValidationFailure("evidence profile policy must be server-owned")
    if evidence_policy.get("downgrade_order") != [
        "hardened-source-bound-v1", "standard-competitive-v1", "private-analytics"
    ]:
        raise ValidationFailure("evidence profile downgrade order is not deterministic")

    # Referencing these variables keeps schema structural validation explicit even before
    # P-1140C/D provide instances for their network/server records.
    if not all(isinstance(schema, dict) for schema in (
        source_observation_schema, detector_schema, device_lineage_schema, pricing_schema
    )):
        raise ValidationFailure("P-1140B schemas did not load as objects")

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
    schemas = spec["components"]["schemas"]
    for forbidden in ("Resource", "Collection"):
        if forbidden in schemas:
            raise ValidationFailure(f"generic OpenAPI schema remains: {forbidden}")
    if any(schema.get("additionalProperties") is True for schema in schemas.values() if isinstance(schema, dict)):
        raise ValidationFailure("OpenAPI permits arbitrary object properties")
    problem_details = schemas["Problem"]["properties"]["details"]
    if problem_details.get("type") != "array":
        raise ValidationFailure("Problem details must be a typed array")
    exceptions = {
        ("/auth/github/start", "post"), ("/auth/x/start", "post"),
        ("/auth/device/start", "post"), ("/auth/device/poll", "post"),
        ("/auth/device/exchange", "post"), ("/claim-challenges", "post"),
    }
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            method = method.lower()
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            if "responses" not in operation:
                raise ValidationFailure(f"OpenAPI operation lacks responses: {method.upper()} {path}")
            if "x-authorization" not in operation or "x-recent-auth" not in operation or "x-idempotency" not in operation:
                raise ValidationFailure(f"OpenAPI operation lacks authority metadata: {method.upper()} {path}")
            rate = operation["responses"].get("429")
            if rate != {"$ref": "#/components/responses/RateLimited"}:
                raise ValidationFailure(f"OpenAPI operation lacks typed rate-limit response: {method.upper()} {path}")
            if method in {"post", "put", "patch", "delete"} and (path, method) not in exceptions:
                refs = [p.get("$ref") for p in operation.get("parameters", []) if isinstance(p, dict)]
                if "#/components/parameters/IdempotencyKey" not in refs:
                    raise ValidationFailure(f"mutating operation lacks durable idempotency key: {method.upper()} {path}")
    batch_content = spec["paths"]["/claim-batches"]["post"]["requestBody"]["content"]
    if set(batch_content) != {"application/vibemaxxing-claim-batch+cbor"}:
        raise ValidationFailure("claim-batches must accept only the registered bounded CBOR media type")


def validate_p1140d_contracts() -> None:
    state_schema = validate_schema_file(SCHEMAS / "state-machine-registry-v1.schema.json")
    state_registry = load_json(SCHEMAS / "state-machine-registry-v1.json")
    validate_instance(state_schema, state_registry, "state-machine registry")
    machines = state_registry["machines"]
    machine_ids = [machine["machine_id"] for machine in machines]
    assert_unique(machine_ids, "state-machine IDs")
    required_machines = {
        "oauth-transaction", "web-session-family", "native-session-family", "ranked-identity-eligibility",
        "idempotency-ledger", "ranking-projection", "model-alias-resolution", "friendship", "rivalry",
        "board-membership", "board-invitation", "presence-lease", "notification",
        "moderation-case", "appeal", "export-job", "server-deletion", "local-deletion-command",
        "daemon-lifecycle", "privileged-supervisor", "update-lifecycle", "release-trust",
        "platform-certification",
    }
    if set(machine_ids) != required_machines:
        raise ValidationFailure(f"state-machine set mismatch: missing={sorted(required_machines - set(machine_ids))}")
    for machine in machines:
        states = set(machine["states"])
        if machine["initial_state"] not in states or not set(machine["terminal_states"]) <= states:
            raise ValidationFailure(f"invalid state declaration: {machine['machine_id']}")
        transition_ids = [item["transition_id"] for item in machine["transitions"]]
        assert_unique(transition_ids, f"{machine['machine_id']} transition IDs")
        for transition in machine["transitions"]:
            if not set(transition["from"]) <= states or transition["to"] not in states:
                raise ValidationFailure(f"transition references unknown state: {transition['transition_id']}")
            for field in ("authentication", "idempotency", "audit_event", "reversal", "transaction_boundary"):
                if not transition.get(field):
                    raise ValidationFailure(f"transition lacks {field}: {transition['transition_id']}")

    platform_schema = validate_schema_file(SCHEMAS / "platform-profile-registry-v1.schema.json")
    platform_registry = load_json(SCHEMAS / "platform-profile-registry-v1.json")
    validate_instance(platform_schema, platform_registry, "platform-profile registry")
    profiles = platform_registry["profiles"]
    profile_ids = [profile["profile_id"] for profile in profiles]
    assert_unique(profile_ids, "platform-profile IDs")
    if len(profiles) < 30:
        raise ValidationFailure("launch platform matrix is not explicit enough")
    if any(profile["advertised"] for profile in profiles):
        raise ValidationFailure("uncertified platform profile is advertised")
    required_failures = {
        "install", "service-start", "service-crash-loop", "shell-close", "login-logout",
        "reboot", "sleep-resume", "key-denied-or-reset", "ipc-cross-user",
        "permission-revoked", "disk-full", "network-offline", "update-interrupted",
        "rollback", "uninstall", "privacy-canary",
    }
    for profile in profiles:
        cases = {case["case_id"] for case in profile["failure_matrix"]}
        if cases != required_failures:
            raise ValidationFailure(f"platform failure matrix mismatch: {profile['profile_id']}")
    if {"android", "ios", "ipados", "chromeos"} & {profile["os_family"] for profile in profiles}:
        raise ValidationFailure("out-of-scope native mobile profile is advertised")

    for name in ("release-set-v1.schema.json", "ranking-view-v1.schema.json", "export-manifest-v1.schema.json"):
        validate_schema_file(SCHEMAS / name)

    reasons = load_json(SCHEMAS / "reason-codes-v1.json")
    required_reason_fields = {
        "subsystem", "class", "default_outcome", "retryable", "public_message_key",
        "internal_visibility", "severity", "appealability", "state_machine",
        "introduced_in", "deprecated_in",
    }
    for item in reasons["codes"]:
        missing_fields = required_reason_fields - set(item)
        if missing_fields:
            raise ValidationFailure(f"reason code lacks authority fields: {item['code']}: {sorted(missing_fields)}")

    policies = load_json(SCHEMAS / "policy-defaults-v1.json")
    required_policy_fields = {
        "value_type", "unit", "effective_at", "change_scope", "rebuild_required",
        "notice_required", "emergency_override", "fixture_refs",
    }
    for key, item in policies["policies"].items():
        missing_fields = required_policy_fields - set(item)
        if missing_fields:
            raise ValidationFailure(f"policy lacks lifecycle fields: {key}: {sorted(missing_fields)}")

    proto = (SCHEMAS / "social-integrity-events-v1.proto").read_text(encoding="utf-8")
    for required in (
        "oneof event", "FriendshipEvent", "BlockEvent", "RivalEvent",
        "BoardMembershipEvent", "PresenceEvent", "NotificationEvent",
        "ModerationEffectEvent", "AppealDecisionEvent", "RetractionEvent",
    ):
        if required not in proto:
            raise ValidationFailure(f"social integrity proto lacks {required}")
    for forbidden in ("json", "payload", "map<"):
        if forbidden in proto.lower():
            raise ValidationFailure(f"social integrity proto retains opaque field: {forbidden}")


def validate_cddl_file() -> None:
    text = (SCHEMAS / "vibeproof-claim-v1.cddl").read_text(encoding="utf-8")
    parse_cddl(text)
    for required_rule in ("vibeproof-claim-v1", "verifier-appraisal-v1", "checkpoint-receipt-v1", "token-categories", "batch-context", "gap-declaration", "key-rotation-transition-v1", "correction-record-v1"):
        if f"{required_rule} =" not in text:
            raise ValidationFailure(f"CDDL missing rule: {required_rule}")
    for forbidden in ("extension-map", "estimated-pricing", "consumer-evidence-state", "raw-request-id"):
        if forbidden in text:
            raise ValidationFailure(f"VibeProof CDDL reintroduced forbidden client authority: {forbidden}")


def validate_vibeproof_vectors() -> None:
    vectors = load_json(CONFORMANCE / "vibeproof" / "v1" / "exact-byte-vectors.json")
    corpus = load_json(CONFORMANCE / "vibeproof" / "v1" / "malformed-resource-corpus.json")
    if vectors.get("external_aad_hex") != b"VIBEMAXXING/VIBEPROOF/V1".hex():
        raise ValidationFailure("VibeProof external AAD is not exact")

    seed = bytes.fromhex(vectors["private_seed_hex"])
    public = bytes.fromhex(vectors["public_key_hex"])
    derived_public = Ed25519PrivateKey.from_private_bytes(seed).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    if derived_public != public:
        raise ValidationFailure("VibeProof fixed seed does not derive declared public key")
    verifier = Ed25519PublicKey.from_public_bytes(public)

    for kind in ("claim", "receipt"):
        vector = vectors[kind]
        payload = bytes.fromhex(vector["canonical_payload_hex"])
        sig_structure = bytes.fromhex(vector["sig_structure_hex"])
        signature = bytes.fromhex(vector["signature_hex"])
        cose = bytes.fromhex(vector["cose_sign1_hex"])
        if hashlib.sha256(payload).hexdigest() != vector["canonical_payload_sha256"]:
            raise ValidationFailure(f"{kind} payload digest mismatch")
        if hashlib.sha256(cose).hexdigest() != vector["cose_sign1_sha256"]:
            raise ValidationFailure(f"{kind} COSE digest mismatch")
        if len(cose) != vector["encoded_bytes"]:
            raise ValidationFailure(f"{kind} encoded byte length mismatch")
        try:
            verifier.verify(signature, sig_structure)
        except Exception as exc:
            raise ValidationFailure(f"{kind} Ed25519 vector signature invalid: {exc}") from exc
        if not cose.startswith(bytes.fromhex("d284")):
            raise ValidationFailure(f"{kind} COSE_Sign1 must carry mandatory tag 18")

    case_ids = [case["id"] for case in corpus["cases"]]
    assert_unique(case_ids, "VibeProof malformed/resource case IDs")
    required = {
        "duplicate-map-key", "non-minimal-integer", "indefinite-map", "float-value", "unknown-tag",
        "trailing-bytes", "unprotected-algorithm", "wrong-algorithm", "wrong-content-type",
        "wrong-kid-size", "signature-mutation", "depth-13", "claim-16385-bytes",
        "batch-257-claims", "batch-1048577-bytes", "allocation-ratio", "idempotency-conflict",
        "sequence-fork", "checkpoint-mismatch", "rotation-payload-mismatch",
    }
    missing = required - set(case_ids)
    if missing:
        raise ValidationFailure(f"VibeProof malformed/resource corpus missing: {sorted(missing)}")


def validate_protobuf_files() -> None:
    local_control = (SCHEMAS / "local-control-v1.proto").read_text(encoding="utf-8")
    for forbidden in ("normalized_event_json", "bytes payload", "string correlation_id"):
        if forbidden in local_control:
            raise ValidationFailure(f"opaque or unbounded local IPC remains: {forbidden}")
    for required in (
        "SourceObservationSubmission", "NormalizedEventAcknowledgement", "ClaimConstructionRequest",
        "QueueSummaryResponse", "ReceiptSummaryResponse", "LocalExportRequest", "LocalDeletionRequest",
        "ProcessRole sender_role", "monotonic_message_sequence", "deadline_monotonic_ns",
    ):
        if required not in local_control:
            raise ValidationFailure(f"typed local IPC is missing {required}")
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
    if "P-1140D REPAIRED PLANNING MIGRATION CONTRACT" not in sql:
        raise ValidationFailure("planning SQL lacks repaired P-1140D maturity marker")
    if re.search(r"(?i)\\bjsonb\\b", sql):
        raise ValidationFailure("planning SQL retains untyped jsonb")
    if re.search(r"create table boards \\([^;]*owner_account_id", sql, flags=re.IGNORECASE | re.DOTALL):
        raise ValidationFailure("board ownership is duplicated outside membership authority")
    if "board_one_active_owner" not in sql or "check (account_id_a < account_id_b)" not in sql:
        raise ValidationFailure("social SQL lacks canonical pair or single-owner constraints")
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
        ("P-1140D state and platform contracts", validate_p1140d_contracts),
        ("CDDL", validate_cddl_file),
        ("VibeProof exact-byte and malformed vectors", validate_vibeproof_vectors),
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
