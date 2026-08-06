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

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_vibeproof_vectors as vibeproof_vectors  # noqa: E402

import psycopg
import yaml
from cddlparser import parse as parse_cddl

from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate as validate_openapi
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
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
        raise ValidationFailure(
            f"invalid JSON: {path.relative_to(ROOT)}: {exc}"
        ) from exc


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationFailure(
            f"invalid YAML: {path.relative_to(ROOT)}: {exc}"
        ) from exc


def validate_schema_file(path: Path) -> dict[str, Any]:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def validate_instance(schema: dict[str, Any], instance: Any, label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(
            instance
        ),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(error.message for error in errors[:8])
        raise ValidationFailure(f"{label} failed schema validation: {details}")


def expect_invalid(schema: dict[str, Any], instance: Any, label: str) -> None:
    if not list(
        Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(
            instance
        )
    ):
        raise ValidationFailure(f"negative fixture unexpectedly validated: {label}")


def assert_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValidationFailure(f"duplicate values in {label}")


def validate_json_schemas_and_examples() -> None:
    adapter_schema = validate_schema_file(SCHEMAS / "adapter-manifest.schema.json")
    event_schema = validate_schema_file(SCHEMAS / "normalized-event.schema.json")
    source_observation_schema = validate_schema_file(
        SCHEMAS / "source-observation.schema.json"
    )
    detector_schema = validate_schema_file(
        SCHEMAS / "local-detector-result.schema.json"
    )
    accounting_profile_schema = validate_schema_file(
        SCHEMAS / "accounting-profile.schema.json"
    )
    device_lineage_schema = validate_schema_file(SCHEMAS / "device-lineage.schema.json")
    pricing_schema = validate_schema_file(
        SCHEMAS / "pricing-interpretation.schema.json"
    )
    egress_schema = validate_schema_file(SCHEMAS / "egress-allowlist-v1.schema.json")
    agent_schema = validate_schema_file(
        CONFORMANCE / "adapters" / "agent-registry-v1.schema.json"
    )
    anti_schema = validate_schema_file(
        CONFORMANCE / "adversarial" / "anti-cheat-registry-v1.schema.json"
    )

    validate_instance(
        adapter_schema,
        load_json(SCHEMAS / "examples" / "adapter-manifest.valid.json"),
        "valid adapter manifest",
    )
    validate_instance(
        event_schema,
        load_json(SCHEMAS / "examples" / "normalized-event.valid.json"),
        "valid normalized event",
    )
    expect_invalid(
        event_schema,
        load_json(
            SCHEMAS / "examples" / "normalized-event.invalid-forbidden-field.json"
        ),
        "forbidden normalized-event field",
    )

    accounting_registry = load_json(
        CONFORMANCE / "accounting" / "accounting-profiles-v1.json"
    )
    accounting_cases = load_json(
        CONFORMANCE / "accounting" / "p1140b-accounting-cases-v1.json"
    )
    privacy_cases = load_json(
        CONFORMANCE / "privacy" / "p1140b-boundary-canaries-v1.json"
    )
    egress_registry = load_json(SCHEMAS / "egress-allowlist-v1.json")
    evidence_policy = load_json(SCHEMAS / "evidence-profile-policy-v1.json")

    validate_instance(egress_schema, egress_registry, "egress registry")
    for profile in accounting_registry["profiles"]:
        validate_instance(
            accounting_profile_schema,
            profile,
            f"accounting profile {profile['profile_id']}",
        )
    assert_unique(
        [profile["profile_id"] for profile in accounting_registry["profiles"]],
        "accounting profile IDs",
    )
    assert_unique(
        [case["case_id"] for case in accounting_cases["cases"]],
        "P-1140B accounting case IDs",
    )
    required_accounting_cases = {
        "separate-cache-no-double-count",
        "inclusive-input-subtract-cache",
        "retry-distinct-execution",
        "cancelled-known-consumption",
        "local-token-ids",
        "contradictory-contained-counts",
    }
    missing_accounting = required_accounting_cases - {
        case["case_id"] for case in accounting_cases["cases"]
    }
    if missing_accounting:
        raise ValidationFailure(
            f"missing P-1140B accounting cases: {sorted(missing_accounting)}"
        )

    required_privacy_boundaries = {
        "adapter",
        "ipc",
        "local-store",
        "detector",
        "claim",
        "http",
        "telemetry",
        "notification",
        "moderation",
        "export",
    }
    covered_boundaries = {case["boundary"] for case in privacy_cases["cases"]}
    if covered_boundaries != required_privacy_boundaries:
        raise ValidationFailure(
            f"privacy boundary coverage mismatch: missing={sorted(required_privacy_boundaries - covered_boundaries)}, "
            f"extra={sorted(covered_boundaries - required_privacy_boundaries)}"
        )
    for boundary in required_privacy_boundaries:
        outcomes = {
            case["expected"]
            for case in privacy_cases["cases"]
            if case["boundary"] == boundary
        }
        if not {"accept", "reject-before-egress"} <= outcomes:
            raise ValidationFailure(
                f"privacy boundary lacks positive/negative pair: {boundary}"
            )

    if evidence_policy.get("authority") != "server-verifier":
        raise ValidationFailure("evidence profile policy must be server-owned")
    if evidence_policy.get("downgrade_order") != [
        "hardened-source-bound-v1",
        "standard-competitive-v1",
        "private-analytics",
    ]:
        raise ValidationFailure("evidence profile downgrade order is not deterministic")

    # Referencing these variables keeps schema structural validation explicit even before
    # P-1140C/D provide instances for their network/server records.
    if not all(
        isinstance(schema, dict)
        for schema in (
            source_observation_schema,
            detector_schema,
            device_lineage_schema,
            pricing_schema,
        )
    ):
        raise ValidationFailure("P-1140B schemas did not load as objects")

    agent_registry = load_json(CONFORMANCE / "adapters" / "agent-registry-v1.json")
    anti_registry = load_json(
        CONFORMANCE / "adversarial" / "anti-cheat-registry-v1.json"
    )
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
                raise ValidationFailure(
                    f"unknown certification tier for {product['id']}"
                )

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
            raise ValidationFailure(
                f"non-planned adversarial case lacks fixture: {case['id']}"
            )


ADAPTER_ONE_RELATIVE = Path("conformance") / "adapters" / "claude-code-otel"
ADAPTER_ONE = ROOT / ADAPTER_ONE_RELATIVE

# The five attributes Claude Code puts on every OTLP datapoint that name a person, an
# account, or an employer. D-099 makes their removal a collector obligation performed
# at the device boundary rather than a configuration option, because no documented
# vendor setting removes `user.email`. This tuple is the executable form of that list:
# the disposition record must strip exactly these, and a fixture carrying any of them
# must fail the stage schema.
ADAPTER_ONE_STRIP_LIST = (
    "organization.id",
    "user.account_id",
    "user.account_uuid",
    "user.email",
    "user.id",
)


def validate_adapter_one_boundary() -> None:
    """Prove the Claude Code OTLP identity attributes cannot survive either stage.

    This checks the schemas reject them and that the disposition record and the
    egress registry agree. It is not evidence that any receiver implements the strip;
    no receiver exists.
    """
    observation_schema = validate_schema_file(
        SCHEMAS / "source-observation.schema.json"
    )
    event_schema = validate_schema_file(SCHEMAS / "normalized-event.schema.json")

    disposition = load_json(ADAPTER_ONE / "otlp-attribute-disposition-v1.json")
    if disposition.get("metric") != "claude_code.token.usage":
        raise ValidationFailure("adapter-one disposition names the wrong metric")
    if disposition.get("partial_clean_permitted") is not False:
        raise ValidationFailure("adapter-one disposition permits a partial-clean path")
    if disposition.get("unknown_attribute_disposition") != "drop-and-flag":
        raise ValidationFailure(
            "adapter-one disposition fails open on an unknown attribute"
        )

    attributes = disposition["attributes"]
    assert_unique(
        [entry["attribute"] for entry in attributes], "adapter-one attribute names"
    )
    stripped = tuple(
        sorted(
            entry["attribute"]
            for entry in attributes
            if entry["disposition"] == "strip"
        )
    )
    if stripped != ADAPTER_ONE_STRIP_LIST:
        raise ValidationFailure(
            f"adapter-one strip list drifted: {list(stripped)} != {list(ADAPTER_ONE_STRIP_LIST)}"
        )

    allowed_dispositions = {"allow", "transform", "drop", "strip"}
    unknown = {entry["disposition"] for entry in attributes} - allowed_dispositions
    if unknown:
        raise ValidationFailure(
            f"adapter-one uses unknown dispositions: {sorted(unknown)}"
        )

    egress_field_ids = {
        field["field_id"]
        for field in load_json(SCHEMAS / "egress-allowlist-v1.json")["fields"]
    }
    leaked = {
        attribute
        for attribute in ADAPTER_ONE_STRIP_LIST
        if attribute in egress_field_ids
        or attribute.replace(".", "-") in egress_field_ids
    }
    if leaked:
        raise ValidationFailure(
            f"stripped identity attributes appear in the egress allowlist: {sorted(leaked)}"
        )

    validate_instance(
        observation_schema,
        load_json(ADAPTER_ONE / "source-observation.valid.json"),
        "adapter-one source observation",
    )

    negatives = disposition["negative_fixtures"]
    if len(negatives) < 4:
        raise ValidationFailure(
            "adapter-one declares fewer than four negative fixtures"
        )
    covered: set[str] = set()
    for relative in negatives:
        declared = Path(relative)
        # The record cites repository-relative paths so the cross-reference validator
        # can resolve them, and every one must live in this adapter's own directory.
        if declared.parent != ADAPTER_ONE_RELATIVE:
            raise ValidationFailure(
                f"adapter-one negative fixture is outside the adapter directory: {relative}"
            )
        path = ADAPTER_ONE / declared.name
        if not path.is_file():
            raise ValidationFailure(
                f"adapter-one negative fixture is missing: {relative}"
            )
        instance = load_json(path)
        schema = event_schema if "normalized-event" in path.name else observation_schema
        carried = sorted(set(instance) & set(ADAPTER_ONE_STRIP_LIST))
        if not carried:
            raise ValidationFailure(
                f"adapter-one negative fixture carries no stripped attribute: {relative}"
            )
        expect_invalid(schema, instance, f"adapter-one {path.name} carrying {carried}")
        covered |= set(carried)

    missing = set(ADAPTER_ONE_STRIP_LIST) - covered
    if missing:
        raise ValidationFailure(
            f"strip-list attributes without a negative fixture: {sorted(missing)}"
        )

    canaries = load_json(CONFORMANCE / "privacy" / "p1140b-boundary-canaries-v1.json")
    adapter_cases = {
        case["case_id"] for case in canaries["cases"] if case["boundary"] == "adapter"
    }
    if "adapter-negative-otel-identity-attributes" not in adapter_cases:
        raise ValidationFailure(
            "adapter boundary lacks the OTLP identity-attribute canary"
        )


def validate_policy_and_observability() -> None:
    policies = load_json(SCHEMAS / "policy-defaults-v1.json")
    required = {
        "overtake_notification_hysteresis_hours",
        "overtake_material_lead_tokens",
        "friend_request_expiry_days",
        "handle_rename_cooldown_days",
        "old_handle_redirect_days",
        "presence_heartbeat_seconds",
        "presence_lease_expiry_seconds",
        "presence_idle_after_seconds",
        "standard_claim_lateness_seconds",
        "challenge_expiry_seconds",
        "batch_max_claims",
        "batch_max_encoded_bytes",
        "public_cache_stale_seconds",
        "moderation_ordinary_review_target_hours",
        "security_audit_retention_days",
        "operational_telemetry_retention_days",
    }
    keys = set(policies["policies"])
    missing = required - keys
    if missing:
        raise ValidationFailure(f"missing required policies: {sorted(missing)}")
    forbidden = {key for key in keys if key.startswith("country_")}
    if forbidden:
        raise ValidationFailure(
            f"post-launch country policies remain in launch defaults: {sorted(forbidden)}"
        )
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
    prohibited = {
        "prompt",
        "response",
        "transcript",
        "code",
        "path",
        "repository_name",
        "claim_payload",
    }
    overlap = prohibited & set(allowed)
    if overlap:
        raise ValidationFailure(
            f"forbidden attributes present in allowlist: {sorted(overlap)}"
        )
    if (
        allowlist["retention_days"]["operational_detail"]
        != policies["policies"]["operational_telemetry_retention_days"]["value"]
    ):
        raise ValidationFailure(
            "operational telemetry retention disagrees with policy registry"
        )
    if (
        allowlist["retention_days"]["security_audit"]
        != policies["policies"]["security_audit_retention_days"]["value"]
    ):
        raise ValidationFailure(
            "security audit retention disagrees with policy registry"
        )


def validate_openapi_file() -> None:
    spec = load_yaml(SCHEMAS / "openapi-v1.yaml")
    validate_openapi(spec)
    paths = set(spec.get("paths", {}))
    required = {
        "/claim-challenges",
        "/claim-batches",
        "/leaderboards/{scope}/{period}",
        "/rank/me",
        "/deletion-requests",
    }
    missing = required - paths
    if missing:
        raise ValidationFailure(
            f"OpenAPI missing planning-critical paths: {sorted(missing)}"
        )
    if "/countries" in paths:
        raise ValidationFailure("country route remains in launch OpenAPI despite D-052")
    schemas = spec["components"]["schemas"]
    for forbidden in ("Resource", "Collection"):
        if forbidden in schemas:
            raise ValidationFailure(f"generic OpenAPI schema remains: {forbidden}")
    if any(
        schema.get("additionalProperties") is True
        for schema in schemas.values()
        if isinstance(schema, dict)
    ):
        raise ValidationFailure("OpenAPI permits arbitrary object properties")
    problem_details = schemas["Problem"]["properties"]["details"]
    if problem_details.get("type") != "array":
        raise ValidationFailure("Problem details must be a typed array")
    # Mutating operations that carry no `Idempotency-Key`, because the credential the
    # request already presents is itself single-use. `/auth/session/refresh` joins the
    # set under D-221: ADR-015 makes every refresh handle one-time-use with no grace
    # window, so a repeated refresh is a replay incident rather than a retry.
    exceptions = {
        ("/auth/github/start", "post"),
        ("/auth/x/start", "post"),
        ("/auth/device/start", "post"),
        ("/auth/device/poll", "post"),
        ("/auth/device/exchange", "post"),
        ("/auth/session/refresh", "post"),
        ("/claim-challenges", "post"),
    }
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            method = method.lower()
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            if "responses" not in operation:
                raise ValidationFailure(
                    f"OpenAPI operation lacks responses: {method.upper()} {path}"
                )
            if (
                "x-authorization" not in operation
                or "x-recent-auth" not in operation
                or "x-idempotency" not in operation
            ):
                raise ValidationFailure(
                    f"OpenAPI operation lacks authority metadata: {method.upper()} {path}"
                )
            rate = operation["responses"].get("429")
            if rate != {"$ref": "#/components/responses/RateLimited"}:
                raise ValidationFailure(
                    f"OpenAPI operation lacks typed rate-limit response: {method.upper()} {path}"
                )
            if (
                method in {"post", "put", "patch", "delete"}
                and (path, method) not in exceptions
            ):
                refs = [
                    p.get("$ref")
                    for p in operation.get("parameters", [])
                    if isinstance(p, dict)
                ]
                if "#/components/parameters/IdempotencyKey" not in refs:
                    raise ValidationFailure(
                        f"mutating operation lacks durable idempotency key: {method.upper()} {path}"
                    )
    # PF-044: one pagination style, applied to every operation that returns a page.
    page_refs = {
        f"#/components/schemas/{name}" for name in schemas if name.endswith("Page")
    }
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            returns_page = False
            for status, response in operation["responses"].items():
                if status == "default" or not str(status).startswith("2"):
                    continue
                for media in (response.get("content") or {}).values():
                    if (media.get("schema") or {}).get("$ref") in page_refs:
                        returns_page = True
            if not returns_page:
                continue
            refs = {
                item.get("$ref")
                for item in operation.get("parameters", [])
                if isinstance(item, dict)
            }
            missing = {
                "#/components/parameters/Cursor",
                "#/components/parameters/Limit",
            } - refs
            if missing:
                raise ValidationFailure(
                    f"collection operation lacks pagination: {operation['operationId']}: {sorted(missing)}"
                )

    batch_content = spec["paths"]["/claim-batches"]["post"]["requestBody"]["content"]
    if set(batch_content) != {"application/vibemaxxing-claim-batch+cbor"}:
        raise ValidationFailure(
            "claim-batches must accept only the registered bounded CBOR media type"
        )


OPERATION_CLASS_RULES = (
    "all",
    "public",
    "authenticated",
    "native-bound",
    "mutating",
    "mutating-authenticated",
    "recent-auth",
    "idempotent-durable",
    "collection",
    "path-addressed",
    "request-body",
)

# Status codes the reason registry may bind to an operation. 5xx is deliberately absent:
# every operation answers it through the `default` response, so requiring an explicit
# declaration would say the server enumerated its own failures, which it has not.
MATRIX_STATUS_RESPONSES = {
    400: "BadRequest",
    401: "Unauthenticated",
    403: "Forbidden",
    404: "NotFound",
    409: "Conflict",
    410: "Gone",
    415: "UnsupportedMediaType",
    422: "UnprocessableContent",
    429: "RateLimited",
}


def derive_operation_classes(spec: dict) -> dict[str, set[str]]:
    """Read the eleven operation classes out of the OpenAPI document itself.

    The registry records its own copy so a reader can see the matrix without an OpenAPI
    parser. Deriving them here is what stops the two from drifting: a hand-maintained
    class list would keep passing after the operation it describes changed shape.
    """
    parameters = spec["components"]["parameters"]

    def resolve(node: dict) -> dict:
        ref = node.get("$ref")
        return parameters[ref.rsplit("/", 1)[1]] if ref else node

    classes: dict[str, set[str]] = {name: set() for name in OPERATION_CLASS_RULES}
    for path, item in spec["paths"].items():
        for method, operation in item.items():
            method = method.lower()
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            operation_id = operation["operationId"]
            security = operation.get("security")
            if security is None:
                raise ValidationFailure(
                    f"operation inherits a document-level security requirement: {operation_id}"
                )
            classes["all"].add(operation_id)
            if security == []:
                classes["public"].add(operation_id)
            else:
                classes["authenticated"].add(operation_id)
                if all("deviceProof" in alternative for alternative in security):
                    classes["native-bound"].add(operation_id)
            if method in {"post", "put", "patch", "delete"}:
                classes["mutating"].add(operation_id)
                if security != []:
                    classes["mutating-authenticated"].add(operation_id)
            if operation.get("x-recent-auth") == "required":
                classes["recent-auth"].add(operation_id)
            if operation.get("x-idempotency") == "required-durable-request-hash":
                classes["idempotent-durable"].add(operation_id)
            declared = [resolve(item) for item in operation.get("parameters", [])]
            names = {item["name"] for item in declared}
            if {"cursor", "limit"} <= names:
                classes["collection"].add(operation_id)
            if any(item.get("in") == "path" for item in declared):
                classes["path-addressed"].add(operation_id)
            if operation.get("requestBody"):
                classes["request-body"].add(operation_id)
    return classes


def validate_api_error_matrix() -> None:
    """Prove the D-141 and D-223 matrix resolves in both directions.

    This proves that the registry and the OpenAPI document agree about which operation
    answers which status with which reason code. It is not evidence that any handler
    returns any of them.
    """
    spec = load_yaml(SCHEMAS / "openapi-v1.yaml")
    registry = load_json(SCHEMAS / "reason-codes-v1.json")

    for key in ("transports", "operation_class_definitions", "operation_classes"):
        if key not in registry:
            raise ValidationFailure(f"reason registry lacks {key}")
    if tuple(registry["operation_class_definitions"]) != OPERATION_CLASS_RULES:
        raise ValidationFailure(
            "reason registry class definitions differ from the rules"
        )

    derived = derive_operation_classes(spec)
    for name in OPERATION_CLASS_RULES:
        recorded = set(registry["operation_classes"].get(name, []))
        if recorded != derived[name]:
            raise ValidationFailure(
                f"operation class {name} differs from the OpenAPI document: "
                f"only-in-registry={sorted(recorded - derived[name])} "
                f"only-in-openapi={sorted(derived[name] - recorded)}"
            )

    transports = set(registry["transports"])
    expected: dict[str, set[int]] = {name: set() for name in derived["all"]}
    for code in registry["codes"]:
        if code["transport"] not in transports:
            raise ValidationFailure(
                f"reason code names an unknown transport: {code['code']}"
            )
        status = code["http_status"]
        if code["transport"] == "problem":
            if status is None:
                raise ValidationFailure(
                    f"problem-transport code lacks a status: {code['code']}"
                )
        elif status is not None:
            raise ValidationFailure(
                f"code carries a status but never reaches the wire: {code['code']}"
            )
        targets = set(code["operations"])
        for name in code["operation_classes"]:
            if name not in derived:
                raise ValidationFailure(
                    f"reason code names an unknown operation class: {code['code']}: {name}"
                )
            targets |= derived[name]
        unknown = sorted(targets - derived["all"])
        if unknown:
            raise ValidationFailure(
                f"reason code names operations the API does not declare: {code['code']}: {unknown}"
            )
        if status is None:
            continue
        if status >= 500:
            continue
        if status not in MATRIX_STATUS_RESPONSES:
            raise ValidationFailure(
                f"reason code binds an unmapped status: {code['code']}"
            )
        if not targets:
            raise ValidationFailure(
                f"wire-visible reason code binds to no operation: {code['code']}"
            )
        for operation_id in targets:
            expected[operation_id].add(status)

    responses = spec["components"]["responses"]
    for status, component in MATRIX_STATUS_RESPONSES.items():
        if component not in responses:
            raise ValidationFailure(
                f"OpenAPI lacks the {status} response component {component}"
            )

    for path, item in spec["paths"].items():
        for method, operation in item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            operation_id = operation["operationId"]
            declared = {
                int(status)
                for status in operation["responses"]
                if status != "default" and 400 <= int(status) < 500
            }
            if declared != expected[operation_id]:
                raise ValidationFailure(
                    f"4xx declaration differs from the reason matrix: {operation_id}: "
                    f"only-in-openapi={sorted(declared - expected[operation_id])} "
                    f"only-in-registry={sorted(expected[operation_id] - declared)}"
                )
            for status in declared:
                reference = operation["responses"][str(status)].get("$ref")
                component = f"#/components/responses/{MATRIX_STATUS_RESPONSES[status]}"
                if reference != component:
                    raise ValidationFailure(
                        f"{operation_id} answers {status} with an inline response instead of {component}"
                    )


def validate_p1140d_contracts() -> None:
    state_schema = validate_schema_file(
        SCHEMAS / "state-machine-registry-v1.schema.json"
    )
    state_registry = load_json(SCHEMAS / "state-machine-registry-v1.json")
    validate_instance(state_schema, state_registry, "state-machine registry")
    machines = state_registry["machines"]
    machine_ids = [machine["machine_id"] for machine in machines]
    assert_unique(machine_ids, "state-machine IDs")
    required_machines = {
        "oauth-transaction",
        "web-session-family",
        "native-session-family",
        "ranked-identity-eligibility",
        "idempotency-ledger",
        "ranking-projection",
        "model-alias-resolution",
        "friendship",
        "rivalry",
        "board-membership",
        "board-invitation",
        "invite-code",
        "presence-lease",
        "notification-delivery",
        "moderation-case",
        "appeal",
        "export-job",
        "server-deletion",
        "local-deletion-command",
        "daemon-lifecycle",
        "interactive-shell",
        "privileged-supervisor",
        "update-lifecycle",
        "release-trust",
        "platform-certification",
        "account-lifecycle",
        "device-enrollment",
        "recovery-case",
        "identity-investigation",
        "account-consolidation",
        "lineage-fork-case",
        "source-certification",
    }
    if set(machine_ids) != required_machines:
        raise ValidationFailure(
            f"state-machine set mismatch: missing={sorted(required_machines - set(machine_ids))}"
        )
    for machine in machines:
        states = set(machine["states"])
        if (
            machine["initial_state"] not in states
            or not set(machine["terminal_states"]) <= states
        ):
            raise ValidationFailure(
                f"invalid state declaration: {machine['machine_id']}"
            )
        transition_ids = [item["transition_id"] for item in machine["transitions"]]
        assert_unique(transition_ids, f"{machine['machine_id']} transition IDs")
        for transition in machine["transitions"]:
            if not set(transition["from"]) <= states or transition["to"] not in states:
                raise ValidationFailure(
                    f"transition references unknown state: {transition['transition_id']}"
                )
            for field in (
                "authentication",
                "idempotency",
                "audit_event",
                "reversal",
                "transaction_boundary",
            ):
                if not transition.get(field):
                    raise ValidationFailure(
                        f"transition lacks {field}: {transition['transition_id']}"
                    )

    platform_schema = validate_schema_file(
        SCHEMAS / "platform-profile-registry-v1.schema.json"
    )
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
        "install",
        "service-start",
        "service-crash-loop",
        "shell-close",
        "login-logout",
        "reboot",
        "sleep-resume",
        "key-denied-or-reset",
        "ipc-cross-user",
        "permission-revoked",
        "disk-full",
        "network-offline",
        "update-interrupted",
        "rollback",
        "uninstall",
        "privacy-canary",
    }
    for profile in profiles:
        cases = {case["case_id"] for case in profile["failure_matrix"]}
        if cases != required_failures:
            raise ValidationFailure(
                f"platform failure matrix mismatch: {profile['profile_id']}"
            )
    if {"android", "ios", "ipados", "chromeos"} & {
        profile["os_family"] for profile in profiles
    }:
        raise ValidationFailure("out-of-scope native mobile profile is advertised")

    for name in (
        "release-set-v1.schema.json",
        "ranking-view-v1.schema.json",
        "export-manifest-v1.schema.json",
    ):
        validate_schema_file(SCHEMAS / name)

    reasons = load_json(SCHEMAS / "reason-codes-v1.json")
    required_reason_fields = {
        "subsystem",
        "class",
        "default_outcome",
        "retryable",
        "public_message_key",
        "internal_visibility",
        "severity",
        "appealability",
        "state_machine",
        "introduced_in",
        "deprecated_in",
    }
    for item in reasons["codes"]:
        missing_fields = required_reason_fields - set(item)
        if missing_fields:
            raise ValidationFailure(
                f"reason code lacks authority fields: {item['code']}: {sorted(missing_fields)}"
            )

    policies = load_json(SCHEMAS / "policy-defaults-v1.json")
    required_policy_fields = {
        "value_type",
        "unit",
        "effective_at",
        "change_scope",
        "rebuild_required",
        "notice_required",
        "emergency_override",
        "fixture_refs",
    }
    for key, item in policies["policies"].items():
        missing_fields = required_policy_fields - set(item)
        if missing_fields:
            raise ValidationFailure(
                f"policy lacks lifecycle fields: {key}: {sorted(missing_fields)}"
            )

    proto = (SCHEMAS / "social-integrity-events-v1.proto").read_text(encoding="utf-8")
    for required in (
        "oneof event",
        "FriendshipEvent",
        "BlockEvent",
        "RivalEvent",
        "BoardMembershipEvent",
        "PresenceEvent",
        "NotificationEvent",
        "ModerationEffectEvent",
        "AppealDecisionEvent",
        "RetractionEvent",
    ):
        if required not in proto:
            raise ValidationFailure(f"social integrity proto lacks {required}")
    for forbidden in ("json", "payload", "map<"):
        if forbidden in proto.lower():
            raise ValidationFailure(
                f"social integrity proto retains opaque field: {forbidden}"
            )


def validate_decision_register() -> None:
    """Every decision row must parse as four cells with a legal status.

    An unescaped pipe inside a decision's text silently splits the Markdown row
    into extra cells, which shifts every column right: the status column then
    reads whatever fragment landed there, or nothing at all. It has happened
    twice - once from a state vocabulary written `a | b | c`, once from a hash
    preimage written with `||`. Both were invisible until something tried to
    read the status as data.
    """
    register = ROOT / "docs" / "planning" / "DECISION_REGISTER.md"
    text = register.read_text(encoding="utf-8")

    allowed: set[str] = set()
    for line in text.split("\n"):
        if line.startswith("Allowed statuses:"):
            allowed = set(re.findall(r"`([a-z-]+)`", line))
            break
    if not allowed:
        raise ValidationFailure("DECISION_REGISTER.md declares no allowed statuses")

    seen: set[str] = set()
    for number, line in enumerate(text.split("\n"), start=1):
        if not line.startswith("| D-"):
            continue
        cells = line.split("|")
        if len(cells) != 6:
            raise ValidationFailure(
                f"DECISION_REGISTER.md:{number} splits into {len(cells) - 2} cells, "
                f"not 4; escape the pipe inside the text"
            )
        identifier, _, status, condition = (cell.strip() for cell in cells[1:5])
        if status not in allowed:
            raise ValidationFailure(
                f"DECISION_REGISTER.md:{number} {identifier} has status "
                f"{status!r}, which is not one of {sorted(allowed)}"
            )
        if not condition:
            raise ValidationFailure(
                f"DECISION_REGISTER.md:{number} {identifier} records no validation "
                f"or reopen condition"
            )
        if identifier in seen:
            raise ValidationFailure(
                f"DECISION_REGISTER.md:{number} repeats {identifier}; decision ids "
                f"are stable references and must be unique"
            )
        seen.add(identifier)


def validate_cddl_file() -> None:
    """Parse the CDDL and assert the rules the contracts depend on are present.

    This proves the grammar parses and that named rules exist. It does **not**
    validate any CBOR instance against the CDDL: `cddlparser` is a
    specification-authoring parser whose own documentation disclaims CBOR
    validation, and it does not implement the RFC 9682 grammar updates. The
    repository therefore has no instance-level CDDL conformance checking, and
    this stage is named for what it executes rather than what a reader might
    assume from the word "CDDL".
    """
    text = (SCHEMAS / "vibeproof-claim-v1.cddl").read_text(encoding="utf-8")
    parse_cddl(text)
    for required_rule in (
        "vibeproof-claim-v1",
        "verifier-appraisal-v1",
        "checkpoint-receipt-v1",
        "token-categories",
        "batch-context",
        "gap-declaration",
        "key-rotation-transition-v1",
        "correction-record-v1",
    ):
        if f"{required_rule} =" not in text:
            raise ValidationFailure(f"CDDL missing rule: {required_rule}")
    for forbidden in (
        "extension-map",
        "estimated-pricing",
        "consumer-evidence-state",
        "raw-request-id",
    ):
        if forbidden in text:
            raise ValidationFailure(
                f"VibeProof CDDL reintroduced forbidden client authority: {forbidden}"
            )

    bundle = (SCHEMAS / "evidence-bundle-v1.cddl").read_text(encoding="utf-8")
    parse_cddl(bundle)
    for required_rule in (
        "evidence-bundle-v1",
        "provenance-record-v1",
        "privacy-record-v1",
        "equivalence-record-v1",
        "observation-record-v1",
    ):
        if f"{required_rule} =" not in bundle:
            raise ValidationFailure(
                f"evidence bundle CDDL missing rule: {required_rule}"
            )
    for forbidden in ("cose-sign1", "verifier-api", "attestation-class = 1"):
        if forbidden in bundle:
            raise ValidationFailure(
                "the evidence bundle is a device-local at-rest record and acquired a "
                f"wire or attestation affordance: {forbidden}"
            )


def validate_vector_reproducibility() -> None:
    """The signed vectors must regenerate byte-identically from the recorded seed.

    Hand-editing fixture hex is how a corpus drifts from the profile it claims
    to encode. If this fails, the committed vectors contain something the
    generator would not produce, which means they are no longer evidence of
    anything the profile says.
    """
    if vibeproof_vectors.regenerate() != (
        CONFORMANCE / "vibeproof" / "v1" / "exact-byte-vectors.json"
    ).read_text(encoding="utf-8"):
        raise ValidationFailure(
            "exact-byte vectors are not reproducible from the recorded seed; "
            "run scripts/repository/generate_vibeproof_vectors.py"
        )


def validate_vibeproof_vectors() -> None:
    vectors = load_json(CONFORMANCE / "vibeproof" / "v1" / "exact-byte-vectors.json")
    corpus = load_json(
        CONFORMANCE / "vibeproof" / "v1" / "malformed-resource-corpus.json"
    )
    if vectors.get("external_aad_hex") != b"VIBEMAXXING/VIBEPROOF/V1".hex():
        raise ValidationFailure("VibeProof external AAD is not exact")

    seed = bytes.fromhex(vectors["private_seed_hex"])
    public = bytes.fromhex(vectors["public_key_hex"])
    derived_public = (
        Ed25519PrivateKey.from_private_bytes(seed)
        .public_key()
        .public_bytes(Encoding.Raw, PublicFormat.Raw)
    )
    if derived_public != public:
        raise ValidationFailure(
            "VibeProof fixed seed does not derive declared public key"
        )
    verifier = Ed25519PublicKey.from_public_bytes(public)
    external_aad = bytes.fromhex(vectors["external_aad_hex"])

    def headers_of(protected: bytes) -> dict:
        decoded, consumed = vibeproof_vectors.decode_map_at(protected, 0)
        if consumed != len(protected):
            raise ValidationFailure("trailing bytes in protected headers")
        return decoded

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

        # Verifying the signature over `sig_structure_hex` only proves the
        # fixture is internally consistent. A Sig_structure built wrongly but
        # signed correctly passes that check, so rebuild it independently from
        # the protected headers, external AAD and payload and require the exact
        # bytes. RFC 9052 s4.4: four elements for COSE_Sign1, because the
        # signer-protected field is omitted rather than carried empty.
        protected = bytes.fromhex(vector["protected_headers_hex"])
        expected_structure = vibeproof_vectors.sig_structure(
            protected, external_aad, payload
        )
        if sig_structure != expected_structure:
            raise ValidationFailure(
                f"{kind} sig_structure is not the Signature1 construction for its "
                f"protected headers, external AAD and payload"
            )
        if vibeproof_vectors.encode(headers_of(protected))[:] != protected:
            raise ValidationFailure(
                f"{kind} protected headers are not core-deterministic CBOR "
                f"(RFC 8949 s4.2.1, which RFC 9052 s9 binds COSE to)"
            )
        if headers_of(protected).get(1) != vibeproof_vectors.ALG_ED25519:
            raise ValidationFailure(
                f"{kind} protected alg is not -19 Ed25519; RFC 9864 deprecates "
                f"the polymorphic EdDSA identifier -8"
            )
        try:
            verifier.verify(signature, sig_structure)
        except Exception as exc:
            raise ValidationFailure(
                f"{kind} Ed25519 vector signature invalid: {exc}"
            ) from exc
        if not cose.startswith(bytes.fromhex("d284")):
            raise ValidationFailure(f"{kind} COSE_Sign1 must carry mandatory tag 18")

    case_ids = [case["id"] for case in corpus["cases"]]
    assert_unique(case_ids, "VibeProof malformed/resource case IDs")
    required = {
        "duplicate-map-key",
        "non-minimal-integer",
        "indefinite-map",
        "float-value",
        "unknown-tag",
        "trailing-bytes",
        "unprotected-algorithm",
        "wrong-algorithm",
        "wrong-content-type",
        "wrong-kid-size",
        "signature-mutation",
        "depth-13",
        "claim-16385-bytes",
        "batch-257-claims",
        "batch-1048577-bytes",
        "allocation-ratio",
        "idempotency-conflict",
        "sequence-fork",
        "checkpoint-mismatch",
        "rotation-payload-mismatch",
    }
    missing = required - set(case_ids)
    if missing:
        raise ValidationFailure(
            f"VibeProof malformed/resource corpus missing: {sorted(missing)}"
        )


def validate_protobuf_files() -> None:
    local_control = (SCHEMAS / "local-control-v1.proto").read_text(encoding="utf-8")
    for forbidden in (
        "normalized_event_json",
        "bytes payload",
        "string correlation_id",
    ):
        if forbidden in local_control:
            raise ValidationFailure(
                f"opaque or unbounded local IPC remains: {forbidden}"
            )
    for required in (
        "SourceObservationSubmission",
        "NormalizedEventAcknowledgement",
        "ClaimConstructionRequest",
        "QueueSummaryResponse",
        "ReceiptSummaryResponse",
        "LocalExportRequest",
        "LocalDeletionRequest",
        "ProcessRole sender_role",
        "monotonic_message_sequence",
        "deadline_monotonic_ns",
    ):
        if required not in local_control:
            raise ValidationFailure(f"typed local IPC is missing {required}")
    files = [
        SCHEMAS / "local-control-v1.proto",
        SCHEMAS / "social-integrity-events-v1.proto",
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "grpc_tools.protoc",
                f"-I{SCHEMAS}",
                f"--python_out={temp_dir}",
                *(str(path) for path in files),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise ValidationFailure(
                f"Protobuf compilation failed: {result.stderr.strip()}"
            )


_CREATE_TABLE_RE = re.compile(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(")


def _planning_table_bodies() -> dict[str, str]:
    """Return the parenthesised body of every `create table` in the planning DDL."""
    sql = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
    bodies: dict[str, str] = {}
    for match in _CREATE_TABLE_RE.finditer(sql):
        depth = 1
        index = match.end()
        while index < len(sql) and depth:
            character = sql[index]
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            index += 1
        bodies[match.group(1)] = sql[match.end() : index - 1]
    return bodies


def validate_data_disposition() -> None:
    """Prove the retention registry covers the schema and resolves to real windows.

    PF-050's problem was that retention lived in prose and `expires_at` columns were
    enforced by nobody. Three things make that checkable rather than aspirational:
    every persistence owner has a disposition row, every numeric window names a policy
    key that exists, and every table carrying an `expires_at` column names the actor
    that acts when the timestamp passes. An expiry with no actor is a comment.

    This proves coverage and resolution. It does not prove that any sweeper exists;
    none does.
    """
    schema = validate_schema_file(SCHEMAS / "data-disposition-v1.schema.json")
    registry = load_json(SCHEMAS / "data-disposition-v1.json")
    validate_instance(schema, registry, "data disposition registry")

    entries = registry["entries"]
    tables = [entry["table"] for entry in entries]
    assert_unique(tables, "data disposition tables")

    bodies = _planning_table_bodies()
    declared = set(bodies)
    covered = set(tables)
    missing = sorted(declared - covered)
    if missing:
        raise ValidationFailure(f"planning tables without a disposition row: {missing}")
    unknown = sorted(covered - declared)
    if unknown:
        raise ValidationFailure(
            f"disposition rows naming tables the planning DDL does not define: {unknown}"
        )

    policies = load_json(SCHEMAS / "policy-defaults-v1.json")["policies"]
    for entry in entries:
        for field in ("retention", "attribution_retention"):
            window = entry.get(field)
            if not window:
                continue
            key = window.get("policy_key")
            if key and key not in policies:
                raise ValidationFailure(
                    f"{entry['table']}.{field} names unknown policy key: {key}"
                )
    for field in ("backup_retention_policy_key", "journal_retention_policy_key"):
        if registry[field] not in policies:
            raise ValidationFailure(
                f"{field} names unknown policy key: {registry[field]}"
            )

    expiring = {
        table
        for table, body in bodies.items()
        if re.search(r"(?m)^\s*expires_at\b", body)
    }
    by_table = {entry["table"]: entry for entry in entries}
    unenforced = sorted(
        table for table in expiring if "expiry_enforcement" not in by_table[table]
    )
    if unenforced:
        raise ValidationFailure(
            f"tables with an expires_at column and no enforcement owner: {unenforced}"
        )
    spurious = sorted(
        entry["table"]
        for entry in entries
        if "expiry_enforcement" in entry and entry["table"] not in expiring
    )
    if spurious:
        raise ValidationFailure(
            f"disposition rows declaring expiry enforcement for a table with no "
            f"expires_at column: {spurious}"
        )

    # D-214: the erasure journal has to outlive the backups it exists to correct,
    # by exactly one day. Longer keeps identifiers of erased participants past the
    # point any restore could need them; shorter leaves a restore with nothing to
    # replay. The two windows are separately editable, so the relation is checked
    # rather than assumed.
    backup_days = policies[registry["backup_retention_policy_key"]]["value"]
    journal_days = policies[registry["journal_retention_policy_key"]]["value"]
    if journal_days != backup_days + 1:
        raise ValidationFailure(
            f"erasure journal retention is {journal_days} days against a "
            f"{backup_days}-day backup window; it must be exactly one day longer"
        )


IDENTITY_LIFECYCLE_SCHEMAS: dict[str, str] = {
    "recovery-case-v1.schema.json": "recovery-case",
    "ranked-identity-v1.schema.json": "identity-investigation",
    "consolidation-plan-v1.schema.json": "account-consolidation",
    "fork-resolution-v1.schema.json": "lineage-fork-case",
}

# Where each schema keeps the state vocabulary that must equal its machine's.
IDENTITY_LIFECYCLE_STATE_POINTERS: dict[str, tuple[str, ...]] = {
    "recovery-case-v1.schema.json": ("recovery_case",),
    "ranked-identity-v1.schema.json": ("investigation",),
    "consolidation-plan-v1.schema.json": ("consolidation_case",),
    "fork-resolution-v1.schema.json": ("fork_case",),
}

IDENTITY_LIFECYCLE_EXAMPLES: tuple[tuple[str, str, bool], ...] = (
    ("recovery-case-v1.schema.json", "recovery-case.valid.json", True),
    (
        "recovery-case-v1.schema.json",
        "recovery-case.invalid-skipped-cooling-off.json",
        False,
    ),
    ("ranked-identity-v1.schema.json", "ranked-identity.valid.json", True),
    (
        "ranked-identity-v1.schema.json",
        "ranked-identity.invalid-two-case-causes.json",
        False,
    ),
    ("consolidation-plan-v1.schema.json", "consolidation-plan.valid.json", True),
    (
        "consolidation-plan-v1.schema.json",
        "consolidation-plan.invalid-summed-total.json",
        False,
    ),
    ("fork-resolution-v1.schema.json", "fork-resolution.valid.json", True),
    (
        "fork-resolution-v1.schema.json",
        "fork-resolution.invalid-resumed-without-generation.json",
        False,
    ),
    ("presence-pulse-v1.schema.json", "presence-pulse.valid.json", True),
    (
        "presence-pulse-v1.schema.json",
        "presence-pulse.invalid-blocked-viewer-sees-online.json",
        False,
    ),
)

# Names no schema in this cluster may carry, each with the rule it would break.
IDENTITY_LIFECYCLE_BANNED_FIELDS: dict[str, str] = {
    "combined_token_burn_total": "D-070 forbids adding two stored account totals",
    "provider_verified": "D-100: no provider attests an individual account",
    "provider_attestation": "D-100: no provider attests an individual account",
    "file_path": "the privacy boundary forbids paths crossing it",
    "project_name": "the privacy boundary forbids project names crossing it",
    "repository_name": "the privacy boundary forbids repository names crossing it",
    "content_hash": "the privacy boundary forbids content-derived hashes",
}


def _schema_state_enum(schema: dict[str, Any], definition: str) -> set[str]:
    node = schema["$defs"][definition]["properties"]["state"]
    return set(node["enum"])


def validate_identity_lifecycle_contracts() -> None:
    """Prove the identity-lifecycle artifacts agree with the authorities they cite.

    Four things are checked, none of which is behaviour. The state vocabulary in
    each schema equals the vocabulary its registered machine declares, so D-079's
    one-spelling rule holds across a fourth surface as well as the three
    `validate_state_vocabularies.py` already covers. Every persistence owner and
    revision source named by the current-viewer-authorization profile resolves to
    a real table and a real column in the planning DDL. The presence thresholds
    bind policy keys that exist. And no schema in the cluster carries a field name
    that a binding product rule forbids.

    This proves reference agreement. No recovery, consolidation, investigation,
    fork resolution or authorization check is implemented, and this validator
    would pass identically if none ever were.
    """
    registry = load_json(SCHEMAS / "state-machine-registry-v1.json")
    machines = {item["machine_id"]: item for item in registry["machines"]}

    loaded: dict[str, dict[str, Any]] = {}
    for filename in (
        *IDENTITY_LIFECYCLE_SCHEMAS,
        "presence-pulse-v1.schema.json",
        "projection-authorization-v1.schema.json",
    ):
        loaded[filename] = validate_schema_file(SCHEMAS / filename)

    for filename, machine_id in IDENTITY_LIFECYCLE_SCHEMAS.items():
        if machine_id not in machines:
            raise ValidationFailure(
                f"{filename} names an unregistered machine: {machine_id}"
            )
        expected = set(machines[machine_id]["states"])
        for definition in IDENTITY_LIFECYCLE_STATE_POINTERS[filename]:
            actual = _schema_state_enum(loaded[filename], definition)
            if actual != expected:
                raise ValidationFailure(
                    f"{filename}#{definition}.state differs from {machine_id}: "
                    f"only-in-schema={sorted(actual - expected)} "
                    f"only-in-registry={sorted(expected - actual)}"
                )

    # The ranked identity itself is governed by a machine the binding table
    # already owns, so it is checked against that one rather than against a new
    # vocabulary invented here.
    identity_states = _schema_state_enum(
        loaded["ranked-identity-v1.schema.json"], "ranked_identity"
    )
    if identity_states != set(machines["ranked-identity-eligibility"]["states"]):
        raise ValidationFailure(
            "ranked-identity-v1.schema.json ranked_identity.state differs from "
            "ranked-identity-eligibility"
        )

    lease_states = _schema_state_enum(loaded["presence-pulse-v1.schema.json"], "lease")
    if lease_states != set(machines["presence-lease"]["states"]):
        raise ValidationFailure(
            "presence-pulse-v1.schema.json lease.state differs from presence-lease"
        )

    for filename, example, expect_valid in IDENTITY_LIFECYCLE_EXAMPLES:
        instance = load_json(SCHEMAS / "examples" / example)
        if expect_valid:
            validate_instance(loaded[filename], instance, example)
        else:
            expect_invalid(loaded[filename], instance, example)

    # The cross-field rule the schema cannot express: a resumed fork continues on
    # a strictly later generation. Merging two commitment chains is what D-072
    # forbids, and a resolution that resumed on the generation it forked at would
    # be that merge under another name.
    fork = load_json(SCHEMAS / "examples" / "fork-resolution.valid.json")["case"]
    if fork["resumed_generation"] <= fork["fork_generation"]:
        raise ValidationFailure(
            "fork-resolution.valid.json resumes on a generation that is not later "
            "than the fork generation"
        )

    profile_schema = loaded["projection-authorization-v1.schema.json"]
    profile = load_json(SCHEMAS / "projection-authorization-v1.json")
    validate_instance(profile_schema, profile, "viewer authorization profile")

    bodies = _planning_table_bodies()
    for entry in profile["inputs"]:
        table = entry["persistence_owner"]
        if table not in bodies:
            raise ValidationFailure(
                f"viewer authorization input {entry['input_id']} names a table the "
                f"planning DDL does not define: {table}"
            )
        source = entry["revision_source"]
        if "." not in source:
            raise ValidationFailure(
                f"viewer authorization input {entry['input_id']} names a revision "
                f"source without a table: {source}"
            )
        source_table, column = source.split(".", 1)
        if source_table != table:
            raise ValidationFailure(
                f"viewer authorization input {entry['input_id']} reads {source} but "
                f"declares {table} as its persistence owner"
            )
        if not re.search(rf"(?m)^\s*{re.escape(column)}\s", bodies[table]):
            raise ValidationFailure(
                f"viewer authorization input {entry['input_id']} names a column "
                f"{table} does not declare: {column}"
            )

    policies = load_json(SCHEMAS / "policy-defaults-v1.json")["policies"]
    thresholds = load_json(SCHEMAS / "examples" / "presence-pulse.valid.json")[
        "thresholds"
    ]
    for field, key in thresholds.items():
        if key not in policies:
            raise ValidationFailure(
                f"presence threshold {field} names an unknown policy key: {key}"
            )
    # D-073 fixes the three numbers; the two misnamed keys make it worth checking
    # the values rather than trusting the names.
    expected_values = {
        "pulse_interval_policy_key": 30,
        "idle_after_policy_key": 90,
        "offline_after_policy_key": 300,
    }
    for field, value in expected_values.items():
        actual = policies[thresholds[field]]["value"]
        if actual != value:
            raise ValidationFailure(
                f"presence threshold {field} resolves to {actual}, not the D-073 "
                f"value {value}"
            )

    for filename, schema in loaded.items():
        text = json.dumps(schema)
        for banned, why in IDENTITY_LIFECYCLE_BANNED_FIELDS.items():
            if f'"{banned}"' in text:
                raise ValidationFailure(f"{filename} declares {banned}: {why}")

    local_store = (SCHEMAS / "local-store-v1.sql").read_text(encoding="utf-8")
    for required in (
        "pragma journal_mode = wal;",
        "pragma synchronous = full;",
        "create table outbox_claims (",
        "create table claim_commitments (",
        "create table source_receipts (",
        "create table local_deletion_receipts (",
    ):
        if required not in local_store:
            raise ValidationFailure(f"local-store-v1.sql lacks {required!r}")
    # A key column in the local store would put the key beside the ciphertext it
    # protects, which is the arrangement D-213 rejects on the server side.
    if re.search(r"(?im)^\s*\w*key_material\b", local_store):
        raise ValidationFailure("local-store-v1.sql declares key material")


CERTIFICATION_EXAMPLES: tuple[tuple[str, str, bool], ...] = (
    ("compatibility-tuple-v1.schema.json", "compatibility-tuple.valid.json", True),
    (
        "compatibility-tuple-v1.schema.json",
        "compatibility-tuple.invalid-open-version-range.json",
        False,
    ),
    ("certification-result-v1.schema.json", "certification-result.valid.json", True),
    (
        "certification-result-v1.schema.json",
        "certification-result.invalid-pass-without-negative-case.json",
        False,
    ),
    ("install-plan-v1.schema.json", "install-plan.valid.json", True),
    (
        "install-plan-v1.schema.json",
        "install-plan.invalid-write-before-verify.json",
        False,
    ),
)


def validate_certification_contracts() -> None:
    """Prove the certification cluster cannot advertise support it has not exercised.

    Four checks. The lifecycle vocabulary equals the registered machine's. Every
    state other than `active` is pinned to a `private-analytics` ceiling in the
    schema as well as in the DDL, so a registry cannot imply exercised support for
    a planned, expired, suspended or superseded tuple. The tuple's platform
    profile resolves to a registered profile. And a passing result with no
    negative case is refused, because a suite that has never failed carries no
    information.

    This proves the records agree with each other. No suite has been run and no
    tuple is certified: every certification state reachable from this repository
    today is `candidate`.
    """
    registry = load_json(SCHEMAS / "state-machine-registry-v1.json")
    machines = {item["machine_id"]: item for item in registry["machines"]}

    tuple_schema = validate_schema_file(SCHEMAS / "compatibility-tuple-v1.schema.json")
    result_schema = validate_schema_file(
        SCHEMAS / "certification-result-v1.schema.json"
    )
    plan_schema = validate_schema_file(SCHEMAS / "install-plan-v1.schema.json")
    schemas = {
        "compatibility-tuple-v1.schema.json": tuple_schema,
        "certification-result-v1.schema.json": result_schema,
        "install-plan-v1.schema.json": plan_schema,
    }

    lifecycle = set(
        result_schema["$defs"]["certification"]["properties"]["state"]["enum"]
    )
    expected = set(machines["source-certification"]["states"])
    if lifecycle != expected:
        raise ValidationFailure(
            "certification-result-v1.schema.json state differs from "
            f"source-certification: only-in-schema={sorted(lifecycle - expected)} "
            f"only-in-registry={sorted(expected - lifecycle)}"
        )

    # Every non-active state must be pinned to private-analytics by the schema and
    # not only by the DDL, so a record that never reaches PostgreSQL is still
    # refused.
    pinned: set[str] = set()
    for clause in result_schema["$defs"]["certification"]["allOf"]:
        condition = clause.get("if", {}).get("properties", {}).get("state", {})
        ceiling = (
            clause.get("then", {})
            .get("properties", {})
            .get("effective_ceiling", {})
            .get("const")
        )
        if ceiling == "private-analytics" and "enum" in condition:
            pinned |= set(condition["enum"])
    if pinned != expected - {"active"}:
        raise ValidationFailure(
            "certification-result-v1.schema.json does not pin every non-active "
            f"state to private-analytics: missing={sorted(expected - {'active'} - pinned)}"
        )

    for filename, example, expect_valid in CERTIFICATION_EXAMPLES:
        instance = load_json(SCHEMAS / "examples" / example)
        if expect_valid:
            validate_instance(schemas[filename], instance, example)
        else:
            expect_invalid(schemas[filename], instance, example)

    profiles = {
        profile["profile_id"]
        for profile in load_json(SCHEMAS / "platform-profile-registry-v1.json")[
            "profiles"
        ]
    }
    for example, pointer in (
        ("compatibility-tuple.valid.json", ("tuple", "platform_profile_id")),
        ("install-plan.valid.json", ("plan", "platform_profile_id")),
    ):
        instance = load_json(SCHEMAS / "examples" / example)
        value = instance[pointer[0]][pointer[1]]
        if value not in profiles:
            raise ValidationFailure(
                f"{example} names an unregistered platform profile: {value}"
            )

    modes = {
        item["mode"]
        for item in load_json(SCHEMAS / "observer-equivalence-v1.json")[
            "observation_modes"
        ]
    }
    declared = set(
        tuple_schema["$defs"]["tuple"]["properties"]["observation_mode"]["enum"]
    )
    if modes and declared != modes:
        raise ValidationFailure(
            "compatibility tuple observation modes differ from the equivalence rule: "
            f"only-in-tuple={sorted(declared - modes)} only-in-rule={sorted(modes - declared)}"
        )

    bodies = _planning_table_bodies()
    for table, constraint in {
        # Only an active certification may exceed private analytics.
        "source_certifications": "check (state = 'active' or effective_ceiling = 'private-analytics')",
        # A pass with no negative case is an untested suite reporting success.
        "certification_results": "check (outcome <> 'passed' or negative_case_count > 0)",
        # An operation names its reversal or declares it has none.
        "platform_install_operations": "check (irreversible = (reversal_operation is null))",
    }.items():
        body = bodies.get(table)
        if body is None:
            raise ValidationFailure(f"planning DDL lacks the {table} table")
        if constraint not in " ".join(body.split()):
            raise ValidationFailure(
                f"{table} lacks its required invariant: {constraint}"
            )


RELEASE_COMPATIBILITY_EXAMPLES: tuple[tuple[str, str, bool], ...] = (
    ("tuf-trust-v1.schema.json", "tuf-trust.valid.json", True),
    ("tuf-trust-v1.schema.json", "tuf-trust.invalid-online-root-key.json", False),
    ("compatibility-graph-v1.schema.json", "compatibility-graph.valid.json", True),
    (
        "compatibility-graph-v1.schema.json",
        "compatibility-graph.invalid-sunset-without-notice.json",
        False,
    ),
    ("migration-chain-v1.schema.json", "migration-chain.valid.json", True),
    (
        "migration-chain-v1.schema.json",
        "migration-chain.invalid-reversible-with-drop.json",
        False,
    ),
)

# D-239 fixes each TUF role's cadence. The policy registry is where the numbers
# live and this is the mapping that stops the schema and the registry drifting.
TUF_EXPIRY_EXPECTATIONS: dict[str, tuple[str, int]] = {
    "root": ("tuf_root_expiry_days", 365),
    "timestamp": ("tuf_timestamp_expiry_days", 1),
    "snapshot": ("tuf_snapshot_expiry_days", 7),
    "targets": ("tuf_targets_expiry_days", 90),
}


def validate_release_compatibility_contracts() -> None:
    """Prove the release, compatibility and migration records resolve.

    Four checks. Every TUF role policy names a policy key that exists and
    resolves to the D-239 cadence. Root and targets keys are offline, which the
    schema refuses to express otherwise. Every compatibility interface in the
    graph schema is also a value the DDL admits. And every migration step's
    rollback class agrees with what it says it did: a binary-reversible step
    naming an irreversible operation is refused.

    This proves the records agree. No TUF repository exists, no client holds
    trusted state, and no migration has been applied.
    """
    tuf_schema = validate_schema_file(SCHEMAS / "tuf-trust-v1.schema.json")
    graph_schema = validate_schema_file(SCHEMAS / "compatibility-graph-v1.schema.json")
    chain_schema = validate_schema_file(SCHEMAS / "migration-chain-v1.schema.json")
    schemas = {
        "tuf-trust-v1.schema.json": tuf_schema,
        "compatibility-graph-v1.schema.json": graph_schema,
        "migration-chain-v1.schema.json": chain_schema,
    }

    for filename, example, expect_valid in RELEASE_COMPATIBILITY_EXAMPLES:
        instance = load_json(SCHEMAS / "examples" / example)
        if expect_valid:
            validate_instance(schemas[filename], instance, example)
        else:
            expect_invalid(schemas[filename], instance, example)

    policies = load_json(SCHEMAS / "policy-defaults-v1.json")["policies"]
    roles = load_json(SCHEMAS / "examples" / "tuf-trust.valid.json")["roles"]
    seen = {role["role"]: role for role in roles}
    for role, (key, value) in TUF_EXPIRY_EXPECTATIONS.items():
        if role not in seen:
            raise ValidationFailure(f"tuf-trust.valid.json declares no {role} role")
        if seen[role]["expiry_policy_key"] != key:
            raise ValidationFailure(
                f"{role} names {seen[role]['expiry_policy_key']}, not {key}"
            )
        if key not in policies:
            raise ValidationFailure(f"{role} names an unknown policy key: {key}")
        if policies[key]["value"] != value:
            raise ValidationFailure(
                f"{key} resolves to {policies[key]['value']}, not the D-239 cadence {value}"
            )

    bodies = _planning_table_bodies()
    graph_interfaces = set(
        graph_schema["$defs"]["edge"]["properties"]["interface"]["enum"]
    )
    edge_body = " ".join(bodies["compatibility_edges"].split())
    for interface in sorted(graph_interfaces):
        if f"'{interface}'" not in edge_body:
            raise ValidationFailure(
                f"compatibility_edges admits no interface {interface!r}"
            )

    chain_classes = set(
        chain_schema["$defs"]["step"]["properties"]["rollback_class"]["enum"]
    )
    migration_body = " ".join(bodies["storage_migrations"].split())
    for rollback_class in sorted(chain_classes):
        if f"'{rollback_class}'" not in migration_body:
            raise ValidationFailure(
                f"storage_migrations admits no rollback class {rollback_class!r}"
            )

    for table, constraint in {
        # An empty compatibility range is unrepresentable.
        "compatibility_edges": "check (maximum_exclusive > minimum_supported)",
        # A snapshot-required migration records the snapshot it required.
        "storage_migrations": (
            "check ((rollback_class = 'snapshot-required') = "
            "(pre_migration_snapshot_digest is not null))"
        ),
        # A client never records trusted metadata signed below threshold.
        "tuf_metadata": "check (signature_count >= threshold)",
    }.items():
        body = " ".join(bodies[table].split())
        if constraint not in body:
            raise ValidationFailure(
                f"{table} lacks its required invariant: {constraint}"
            )


def validate_erasure_contract() -> None:
    """Prove the erasure invariants that a check constraint can carry are carried.

    D-210 rests on constraints rather than on worker discipline, so the constraints
    are the thing to verify. This is structural agreement between the schema, the DDL
    and the decision. It is not evidence that any erasure has been executed.
    """
    validate_schema_file(SCHEMAS / "erasure-record-v1.schema.json")
    validate_schema_file(SCHEMAS / "ranking-generation-v1.schema.json")
    validate_schema_file(SCHEMAS / "score-contribution-v1.schema.json")
    validate_schema_file(SCHEMAS / "ranking-event-v1.schema.json")
    validate_schema_file(SCHEMAS / "period-calendar-v1.schema.json")

    bodies = _planning_table_bodies()
    required = {
        # A key is present or destroyed, never both and never neither.
        "erasure_keys": "check ((key_material is null) = (destroyed_at is not null))",
        # A restore cannot record traffic admitted before the erasure replay finished.
        "erasure_restore_receipts": (
            "check (traffic_admitted_at is null or traffic_admitted_at >= reapply_completed_at)"
        ),
        # The weight only ever discounts, so ADR-020's ceiling is enforced per entry.
        "ranking_entries": "check (credited_token_burn <= token_burn_total)",
        # The chain has exactly one root.
        "erasure_records": "check ((chain_sequence = 1) = (previous_record_digest is null))",
    }
    for table, constraint in required.items():
        body = bodies.get(table)
        if body is None:
            raise ValidationFailure(f"planning DDL lacks the {table} table")
        if constraint not in " ".join(body.split()):
            raise ValidationFailure(
                f"{table} lacks its required erasure invariant: {constraint}"
            )

    entry_body = " ".join(bodies["ranking_entries"].split())
    if "account_id" in entry_body:
        raise ValidationFailure(
            "ranking_entries names an account identifier; a sealed entry is keyed on "
            "the erasure-domain pseudonym so that key destruction is sufficient"
        )
    for banned_table in ("minute_scores", "period_scores"):
        if re.search(r"(?m)^\s*score\s+bigint", bodies[banned_table]):
            raise ValidationFailure(
                f"{banned_table} retains a column named score, which ADR-020 bans"
            )


def validate_postgres_ddl(database_url: str) -> None:
    sql = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
    if "P-1140D REPAIRED PLANNING MIGRATION CONTRACT" not in sql:
        raise ValidationFailure("planning SQL lacks repaired P-1140D maturity marker")
    if re.search(r"(?i)\bjsonb\b", sql):
        raise ValidationFailure("planning SQL retains untyped jsonb")
    if re.search(
        r"create table boards \([^;]*owner_account_id",
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        raise ValidationFailure(
            "board ownership is duplicated outside membership authority"
        )
    if (
        "board_one_active_owner" not in sql
        or "check (account_id_a < account_id_b)" not in sql
    ):
        raise ValidationFailure(
            "social SQL lacks canonical pair or single-owner constraints"
        )
    if re.search(r"(?im)^create\s+table\s+country_assertions\b", sql):
        raise ValidationFailure("country_assertions remains in launch SQL")
    if re.search(
        r"board_type\s+in\s*\([^)]*'country'", sql, flags=re.IGNORECASE | re.DOTALL
    ):
        raise ValidationFailure("country remains an allowed launch board type")
    try:
        with psycopg.connect(database_url, autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute("drop schema if exists planning_validation cascade")
                cursor.execute("create schema planning_validation")
                cursor.execute("set search_path to planning_validation")
                cursor.execute(sql)
                cursor.execute(
                    "select count(*) from information_schema.tables where table_schema = 'planning_validation'"
                )
                table_count = cursor.fetchone()[0]
                if table_count < 40:
                    raise ValidationFailure(
                        f"planning DDL created too few structural tables: {table_count}"
                    )
                cursor.execute("drop schema planning_validation cascade")
    except ValidationFailure:
        raise
    except Exception as exc:
        raise ValidationFailure(f"PostgreSQL DDL validation failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Accounting arithmetic, producer bindings, observer equivalence, evidence chain
# ---------------------------------------------------------------------------

UINT64_MAX = 18446744073709551615

CANONICAL_COMPONENTS = (
    "input_uncached",
    "output_visible",
    "cache_read",
    "cache_write",
    "reasoning",
    "multimodal_input",
    "multimodal_output",
)


def canonical_cbor(value: Any) -> bytes:
    """Encode a planning record under the digest profile the arithmetic record states.

    RFC 8949 core deterministic encoding, restricted to what a signed planning record
    may contain: unsigned and negative integers, text strings, arrays, maps and the
    simple value `null`. Floats are refused because RFC 8949 Section 4.2.2 leaves their
    determinism to the protocol and D-193 declines to define one. Booleans are refused
    because a two-valued field written as a named enum stays legible inside the digest
    preimage, and refusing them keeps this encoder and the claim encoder agreeing on
    what a record may hold.
    """
    if isinstance(value, bool):  # before int; bool is an int subclass
        raise ValidationFailure(
            "digested planning records encode no boolean; use a named enum"
        )
    if value is None:
        return b"\xf6"
    if isinstance(value, int):
        if value >= 0:
            return vibeproof_vectors.encode_head(0, value)
        return vibeproof_vectors.encode_head(1, -value - 1)
    if isinstance(value, float):
        raise ValidationFailure("digested planning records encode no float (D-193)")
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return vibeproof_vectors.encode_head(3, len(encoded)) + encoded
    if isinstance(value, list):
        return vibeproof_vectors.encode_head(4, len(value)) + b"".join(
            canonical_cbor(item) for item in value
        )
    if isinstance(value, dict):
        items = sorted(
            (
                (canonical_cbor(key), canonical_cbor(item))
                for key, item in value.items()
            ),
            key=lambda pair: pair[0],
        )
        return vibeproof_vectors.encode_head(5, len(items)) + b"".join(
            key + item for key, item in items
        )
    raise ValidationFailure(f"unencodable planning type: {type(value).__name__}")


def record_digest(record: dict[str, Any]) -> str:
    body = {key: item for key, item in record.items() if key != "content_sha256"}
    return hashlib.sha256(canonical_cbor(body)).hexdigest()


def assert_record_digest(record: dict[str, Any], label: str) -> None:
    expected = record_digest(record)
    if record["content_sha256"] != expected:
        raise ValidationFailure(
            f"{label} content_sha256 does not match its canonical encoding: "
            f"recorded {record['content_sha256']}, computed {expected}"
        )


def evaluate_token_burn(
    profile: dict[str, Any], source_fields: dict[str, str]
) -> tuple[str, Any]:
    """Reproduce Token Burn from a profile and a source reading.

    This is a second implementation of the arithmetic, independent of the fixture that
    records the answer. A vector whose recorded expectation disagrees with this fails.
    """
    declared = {field["field_id"] for field in profile["source_fields"]}
    component_of = {
        entry["source_field"]: entry["canonical_component"]
        for entry in profile["component_map"]
    }

    values: dict[str, int] = {}
    for field_id, raw in source_fields.items():
        if field_id not in declared:
            return ("reject", "unmapped-source-field")
        values[field_id] = int(raw)

    containers: dict[str, list[str]] = {}
    for edge in profile["containment_edges"]:
        if edge["container"] not in declared or edge["member"] not in declared:
            return ("reject", "unmapped-source-field")
        containers.setdefault(edge["member"], []).append(edge["container"])
    for members in containers.values():
        if len(members) > 1:
            return ("reject", "multiple-containers")
    for member in containers:
        seen = {member}
        cursor = member
        while cursor in containers:
            cursor = containers[cursor][0]
            if cursor in seen:
                return ("reject", "containment-cycle")
            seen.add(cursor)

    for member, parents in containers.items():
        container = parents[0]
        if member in values and container in values:
            if values[container] < values[member]:
                return ("reject", "containment-underflow")
            values[container] -= values[member]

    components = {name: 0 for name in CANONICAL_COMPONENTS}
    for field_id, value in values.items():
        components[component_of[field_id]] += value
        if components[component_of[field_id]] > UINT64_MAX:
            return ("reject", "sum-overflow")

    total = 0
    for name in CANONICAL_COMPONENTS:
        total += components[name]
        if total > UINT64_MAX:
            return ("reject", "sum-overflow")
    return ("ok", (components, total))


def evaluate_cash_burn(priced: list[dict[str, str]]) -> int:
    """Exact integer products, one summation, one round-half-even division."""
    nano = 0
    for entry in priced:
        nano += int(entry["units"]) * int(entry["unit_price_nano"])
    quotient, remainder = divmod(nano, 1000)
    if remainder * 2 > 1000:
        quotient += 1
    elif remainder * 2 == 1000:
        quotient += quotient % 2
    return quotient


def evaluate_correction(contributions: list[dict[str, str]]) -> tuple[str, int]:
    total = 0
    for contribution in contributions:
        magnitude = int(contribution["magnitude"])
        if contribution["direction"] == "add":
            total += magnitude
            if total > UINT64_MAX:
                return ("reject", 0)
        else:
            if magnitude > total:
                return ("reject", 0)
            total -= magnitude
    return ("composed", total)


def validate_accounting_arithmetic() -> None:
    arithmetic_schema = validate_schema_file(
        SCHEMAS / "accounting-arithmetic-v1.schema.json"
    )
    vectors_schema = validate_schema_file(
        SCHEMAS / "accounting-arithmetic-vectors-v1.schema.json"
    )
    profile_schema = validate_schema_file(SCHEMAS / "accounting-profile.schema.json")

    arithmetic = load_json(SCHEMAS / "accounting-arithmetic-v1.json")
    validate_instance(arithmetic_schema, arithmetic, "accounting arithmetic record")
    assert_record_digest(arithmetic, "accounting-arithmetic-v1")
    if tuple(arithmetic["canonical_component_order"]) != CANONICAL_COMPONENTS:
        raise ValidationFailure(
            "the arithmetic record's component order no longer matches the canonical "
            "component set the claim encodes"
        )

    registry = load_json(CONFORMANCE / "accounting" / "accounting-profiles-v1.json")
    profiles = {profile["profile_id"]: profile for profile in registry["profiles"]}
    for profile_id, profile in profiles.items():
        validate_instance(profile_schema, profile, f"accounting profile {profile_id}")
        assert_record_digest(profile, f"accounting profile {profile_id}")
        declared = [field["field_id"] for field in profile["source_fields"]]
        mapped = [entry["source_field"] for entry in profile["component_map"]]
        if sorted(declared) != sorted(mapped):
            raise ValidationFailure(
                f"accounting profile {profile_id} maps {sorted(mapped)} but declares "
                f"{sorted(declared)}; every source field resolves to exactly one component"
            )
        outputs = set(profile["canonical_outputs"])
        for entry in profile["component_map"]:
            if entry["canonical_component"] not in outputs:
                raise ValidationFailure(
                    f"accounting profile {profile_id} maps a source field to "
                    f"{entry['canonical_component']}, which it does not enable"
                )

    vectors = load_json(CONFORMANCE / "accounting" / "arithmetic-vectors-v1.json")
    validate_instance(vectors_schema, vectors, "accounting arithmetic vectors")
    assert_unique(
        [vector["vector_id"] for vector in vectors["vectors"]], "arithmetic vector IDs"
    )
    expect_invalid(
        vectors_schema,
        load_json(
            CONFORMANCE
            / "accounting"
            / "arithmetic-vectors-v1.invalid-float-quantity.json"
        ),
        "arithmetic vectors carrying a fractional quantity",
    )

    kinds: set[str] = set()
    for vector in vectors["vectors"]:
        vector_id = vector["vector_id"]
        kinds.add(vector["kind"])
        if vector["kind"] in {"token-burn", "arithmetic-failure"}:
            profile = profiles.get(vector["profile_id"])
            if profile is None:
                raise ValidationFailure(
                    f"arithmetic vector {vector_id} names an unregistered profile"
                )
            outcome, detail = evaluate_token_burn(profile, vector["source_fields"])
            if vector["kind"] == "arithmetic-failure":
                if outcome != "reject":
                    raise ValidationFailure(
                        f"arithmetic vector {vector_id} was expected to reject and did not"
                    )
                if detail != vector["expected_failure"]["condition"]:
                    raise ValidationFailure(
                        f"arithmetic vector {vector_id} rejected for {detail}, "
                        f"not {vector['expected_failure']['condition']}"
                    )
                continue
            if outcome != "ok":
                raise ValidationFailure(
                    f"arithmetic vector {vector_id} rejected unexpectedly: {detail}"
                )
            components, total = detail
            recorded = {
                name: int(vector["expected_components"][name])
                for name in CANONICAL_COMPONENTS
            }
            if components != recorded:
                raise ValidationFailure(
                    f"arithmetic vector {vector_id} components disagree: "
                    f"computed {components}, recorded {recorded}"
                )
            if total != int(vector["expected_token_burn"]):
                raise ValidationFailure(
                    f"arithmetic vector {vector_id} total disagrees: computed {total}, "
                    f"recorded {vector['expected_token_burn']}"
                )
        elif vector["kind"] == "estimated-cash-burn":
            computed = evaluate_cash_burn(vector["priced_components"])
            if computed != int(vector["expected_estimated_cash_burn_micros"]):
                raise ValidationFailure(
                    f"cash-burn vector {vector_id} disagrees: computed {computed}, "
                    f"recorded {vector['expected_estimated_cash_burn_micros']}"
                )
        else:
            disposition, total = evaluate_correction(vector["contributions"])
            expected = vector["expected_result"]
            if disposition != expected["disposition"]:
                raise ValidationFailure(
                    f"correction vector {vector_id} reached {disposition}, "
                    f"not {expected['disposition']}"
                )
            if disposition == "composed" and total != int(expected["composed_total"]):
                raise ValidationFailure(
                    f"correction vector {vector_id} composed {total}, "
                    f"not {expected['composed_total']}"
                )

    required_kinds = {
        "token-burn",
        "arithmetic-failure",
        "estimated-cash-burn",
        "correction",
    }
    if kinds != required_kinds:
        raise ValidationFailure(
            f"arithmetic vector coverage mismatch: missing {sorted(required_kinds - kinds)}"
        )


def evaluate_otel_series(
    binding: dict[str, Any], series: list[dict[str, Any]]
) -> tuple[str, Any]:
    policy = binding["attribute_policy"]
    allowed = {
        entry["attribute"]
        for entry in policy["entries"]
        if entry["disposition"] in {"allow", "transform"}
    }
    stripped = {
        entry["attribute"]
        for entry in policy["entries"]
        if entry["disposition"] == "strip"
    }
    dropped = {
        entry["attribute"]
        for entry in policy["entries"]
        if entry["disposition"] == "drop"
    }
    metric = binding["otel"]["metrics"][0]
    category_attribute = metric["category_attribute"]
    category_map = {
        entry["attribute_value"]: entry["canonical_component"]
        for entry in metric["category_map"]
    }

    state: dict[tuple, tuple[str, int]] = {}
    generation = 0
    components = {name: 0 for name in CANONICAL_COMPONENTS}
    for datapoint in series:
        attributes = datapoint["attributes"]
        if any(name in stripped for name in attributes):
            return ("rejected", ("identity-attribute-present", "reject-whole"))
        unknown = [
            name
            for name in attributes
            if name not in allowed and name not in stripped and name not in dropped
        ]
        if unknown:
            return ("rejected", ("unknown-attribute", "drop-and-flag"))
        category = attributes.get(category_attribute)
        if category not in category_map:
            return ("rejected", ("unmapped-category-value", "reject-whole"))

        key = tuple(sorted(item for item in attributes.items() if item[0] in allowed))
        value = int(datapoint["cumulative_value"])
        start = datapoint["start_time_unix_nano"]
        previous = state.get(key)
        if previous is None:
            delta = value
        elif previous[0] != start or value < previous[1]:
            generation += 1
            delta = value
        else:
            delta = value - previous[1]
        state[key] = (start, value)
        components[category_map[category]] += delta

    total = 0
    for name in CANONICAL_COMPONENTS:
        total += components[name]
    return ("ok", (components, total, generation))


def validate_producer_bindings() -> None:
    binding_schema = validate_schema_file(
        SCHEMAS / "producer-accounting-binding-v1.schema.json"
    )
    capture_schema = validate_schema_file(
        SCHEMAS / "otel-capture-vectors-v1.schema.json"
    )

    registry = load_json(CONFORMANCE / "accounting" / "producer-bindings-v1.json")
    bindings = {entry["binding_id"]: entry for entry in registry["bindings"]}
    assert_unique(list(bindings), "producer binding IDs")

    arithmetic = load_json(SCHEMAS / "accounting-arithmetic-v1.json")
    profiles = {
        profile["profile_id"]: profile
        for profile in load_json(
            CONFORMANCE / "accounting" / "accounting-profiles-v1.json"
        )["profiles"]
    }

    for binding_id, binding in bindings.items():
        validate_instance(binding_schema, binding, f"producer binding {binding_id}")
        assert_record_digest(binding, f"producer binding {binding_id}")
        if binding["arithmetic"]["content_sha256"] != arithmetic["content_sha256"]:
            raise ValidationFailure(
                f"producer binding {binding_id} pins a stale arithmetic digest"
            )
        profile = profiles.get(binding["accounting_profile"]["id"])
        if profile is None:
            raise ValidationFailure(
                f"producer binding {binding_id} names an unregistered accounting profile"
            )
        if binding["accounting_profile"]["content_sha256"] != profile["content_sha256"]:
            raise ValidationFailure(
                f"producer binding {binding_id} pins a stale accounting profile digest"
            )
        if binding["certification"]["state"] == "active":
            raise ValidationFailure(
                f"producer binding {binding_id} advertises an active certification; "
                "no exercised certification result exists in this repository"
            )
        if binding["effective_ceiling"] != "private-analytics":
            raise ValidationFailure(
                f"producer binding {binding_id} claims a competitive ceiling without an "
                "active certification"
            )
        component_of = {
            entry["source_field"]: entry["canonical_component"]
            for entry in profile["component_map"]
        }
        mapped_entries = []
        if binding["producer_kind"] == "otel":
            for metric in binding["otel"]["metrics"]:
                mapped_entries.extend(metric["category_map"])
        else:
            mapped_entries.extend(binding["acp"]["usage_fields"])
        for entry in mapped_entries:
            field = entry["profile_source_field"]
            if field not in component_of:
                raise ValidationFailure(
                    f"producer binding {binding_id} maps to source field {field}, "
                    "which its accounting profile does not declare"
                )
            if component_of[field] != entry["canonical_component"]:
                raise ValidationFailure(
                    f"producer binding {binding_id} places {field} in "
                    f"{entry['canonical_component']} while its profile places it in "
                    f"{component_of[field]}"
                )

    adapter_one = bindings["claude-code-otel-v1"]
    stripped = tuple(
        sorted(
            entry["attribute"]
            for entry in adapter_one["attribute_policy"]["entries"]
            if entry["disposition"] == "strip"
        )
    )
    if stripped != ADAPTER_ONE_STRIP_LIST:
        raise ValidationFailure(
            f"the OTel producer binding's strip list drifted from D-099: {list(stripped)}"
        )

    expect_invalid(
        binding_schema,
        load_json(
            CONFORMANCE
            / "accounting"
            / "producer-bindings-v1.invalid-uncertified-competitive.json"
        ),
        "uncertified producer binding claiming a competitive ceiling",
    )

    capture = load_json(CONFORMANCE / "accounting" / "otel-capture-vectors-v1.json")
    validate_instance(capture_schema, capture, "OTel capture vectors")
    assert_unique(
        [vector["vector_id"] for vector in capture["vectors"]],
        "OTel capture vector IDs",
    )
    binding = bindings[capture["binding_id"]]
    if capture["metric"] != binding["otel"]["metrics"][0]["name"]:
        raise ValidationFailure("OTel capture vectors name a metric the binding omits")

    conditions: set[str] = set()
    for vector in capture["vectors"]:
        outcome, detail = evaluate_otel_series(binding, vector["series"])
        vector_id = vector["vector_id"]
        if vector["kind"] == "rejection":
            if outcome != "rejected":
                raise ValidationFailure(
                    f"OTel capture vector {vector_id} was expected to be refused and was not"
                )
            expected = (
                vector["expected_rejection"]["condition"],
                vector["expected_rejection"]["disposition"],
            )
            if detail != expected:
                raise ValidationFailure(
                    f"OTel capture vector {vector_id} produced {detail}, not {expected}"
                )
            conditions.add(expected[0])
            continue
        if outcome != "rejected":
            components, total, generation = detail
        else:
            raise ValidationFailure(
                f"OTel capture vector {vector_id} was refused for {detail}"
            )
        recorded = {
            name: int(vector["expected_components"][name])
            for name in CANONICAL_COMPONENTS
        }
        if components != recorded:
            raise ValidationFailure(
                f"OTel capture vector {vector_id} components disagree: "
                f"computed {components}, recorded {recorded}"
            )
        if total != int(vector["expected_token_burn"]):
            raise ValidationFailure(
                f"OTel capture vector {vector_id} total disagrees: computed {total}"
            )
        if generation != int(vector["expected_final_runtime_generation"]):
            raise ValidationFailure(
                f"OTel capture vector {vector_id} runtime generation disagrees: "
                f"computed {generation}"
            )

    required_conditions = {
        "identity-attribute-present",
        "unknown-attribute",
        "unmapped-category-value",
    }
    if conditions != required_conditions:
        raise ValidationFailure(
            "OTel capture vectors do not cover every refusal condition: "
            f"missing {sorted(required_conditions - conditions)}"
        )


def resolve_observations(
    rule: dict[str, Any], observations: list[dict[str, Any]]
) -> dict[str, str]:
    """Apply the observer-equivalence rule and return one disposition per observation."""
    rank = {mode["mode"]: mode["precedence_rank"] for mode in rule["observation_modes"]}
    forbidden = set(rule["forbidden"]["preimage_inputs"])
    class_inputs = {
        item["class"]: set(item["preimage_inputs"])
        for item in rule["equivalence_classes"]
    }

    result: dict[str, str] = {}
    active: list[dict[str, Any]] = []
    for observation in observations:
        identifier = observation["observation_id"]
        inputs = set(observation["preimage_inputs"])
        if inputs & forbidden:
            result[identifier] = "rejected"
            continue
        if inputs != class_inputs[observation["equivalence_class"]]:
            result[identifier] = "rejected"
            continue
        missing = inputs - set(observation["facts"])
        if missing:
            result[identifier] = "rejected"
            continue
        if observation["equivalence_class"] == "weak":
            result[identifier] = "private-analytics"
            continue
        active.append(observation)

    def commitment(observation: dict[str, Any]) -> tuple:
        return tuple(
            observation["facts"][name]
            for name in sorted(observation["preimage_inputs"])
        )

    def unit_of(observation: dict[str, Any]) -> tuple:
        facts = observation["facts"]
        return tuple(facts[name] for name in rule["exclusivity"]["unit"])

    units: dict[tuple, list[dict[str, Any]]] = {}
    for observation in active:
        units.setdefault(unit_of(observation), []).append(observation)

    for members in units.values():
        if all(item["equivalence_class"] == "strong" for item in members):
            survivors = members
        else:
            channels: dict[tuple, list[dict[str, Any]]] = {}
            for item in members:
                channels.setdefault(
                    (item["mode"], item["collector_instance"]), []
                ).append(item)
            if len(channels) == 1:
                survivors = members
            else:
                best = min(rank[mode] for mode, _ in channels)
                tied = [channel for channel in channels if rank[channel[0]] == best]
                if len(tied) == 1:
                    survivors = channels[tied[0]]
                else:
                    sets = [
                        sorted(commitment(item) for item in channels[channel])
                        for channel in tied
                    ]
                    if any(entry != sets[0] for entry in sets[1:]):
                        for item in members:
                            result[item["observation_id"]] = "quarantined"
                        continue
                    survivors = [item for channel in tied for item in channels[channel]]
                for item in members:
                    if item not in survivors:
                        result[item["observation_id"]] = "superseded"

        groups: dict[tuple, list[dict[str, Any]]] = {}
        for item in survivors:
            groups.setdefault(commitment(item), []).append(item)
        for group in groups.values():
            group.sort(
                key=lambda item: (
                    rank[item["mode"]],
                    item["collector_instance"],
                    item["observation_id"],
                )
            )
            result[group[0]["observation_id"]] = "counted"
            for item in group[1:]:
                result[item["observation_id"]] = "superseded"
    return result


def validate_observer_equivalence() -> None:
    rule_schema = validate_schema_file(SCHEMAS / "observer-equivalence-v1.schema.json")
    vectors_schema = validate_schema_file(SCHEMAS / "dedup-vectors-v1.schema.json")

    rule = load_json(SCHEMAS / "observer-equivalence-v1.json")
    validate_instance(rule_schema, rule, "observer equivalence rule")
    assert_record_digest(rule, "observer-equivalence-v1")

    ranks = [mode["precedence_rank"] for mode in rule["observation_modes"]]
    assert_unique([str(value) for value in ranks], "observation mode precedence ranks")

    overlap = set(rule["forbidden"]["preimage_inputs"]) & {
        name for item in rule["equivalence_classes"] for name in item["preimage_inputs"]
    }
    if overlap:
        raise ValidationFailure(
            f"observer-derived inputs appear in an equivalence preimage: {sorted(overlap)}"
        )
    if rule["wire_binding"]["new_egress_fields"]:
        raise ValidationFailure(
            "the observer-equivalence rule proposes a new egress field; the preimage is "
            "constrained, the wire is not extended"
        )
    egress_fields = {
        field["field_id"]
        for field in load_json(SCHEMAS / "egress-allowlist-v1.json")["fields"]
    }
    if rule["wire_binding"]["egress_field_id"] not in egress_fields:
        raise ValidationFailure(
            "the observer-equivalence commitment is not admissible in the egress allowlist"
        )

    vectors = load_json(CONFORMANCE / "accounting" / "dedup-vectors-v1.json")
    validate_instance(vectors_schema, vectors, "deduplication vectors")
    assert_unique(
        [vector["vector_id"] for vector in vectors["vectors"]],
        "deduplication vector IDs",
    )
    expect_invalid(
        vectors_schema,
        load_json(
            CONFORMANCE / "accounting" / "dedup-vectors-v1.invalid-empty-preimage.json"
        ),
        "deduplication vector with an empty commitment preimage",
    )

    dispositions: set[str] = set()
    for vector in vectors["vectors"]:
        computed = resolve_observations(rule, vector["observations"])
        recorded = vector["expected"]["dispositions"]
        if computed != recorded:
            raise ValidationFailure(
                f"deduplication vector {vector['vector_id']} disagrees: "
                f"computed {computed}, recorded {recorded}"
            )
        dispositions |= set(recorded.values())
        counted = sum(
            int(observation["token_burn"])
            for observation in vector["observations"]
            if computed[observation["observation_id"]] == "counted"
        )
        if counted != int(vector["expected"]["counted_token_burn"]):
            raise ValidationFailure(
                f"deduplication vector {vector['vector_id']} counted {counted} tokens, "
                f"not {vector['expected']['counted_token_burn']}"
            )

    required_dispositions = {
        "counted",
        "superseded",
        "quarantined",
        "private-analytics",
        "rejected",
    }
    if dispositions != required_dispositions:
        raise ValidationFailure(
            "deduplication vectors do not exercise every disposition: "
            f"missing {sorted(required_dispositions - dispositions)}"
        )


APPRAISAL_RANGE_RE = re.compile(r"^\s*\d+:\s*0\.\.(\d+),?\s*;\s*([a-z_ ]+?)\s*$")


def appraisal_wire_ranges() -> dict[str, int]:
    """Read the integer ceiling the CDDL declares for each appraisal dimension."""
    text = (SCHEMAS / "vibeproof-claim-v1.cddl").read_text(encoding="utf-8")
    start = text.index("verifier-appraisal-v1 = {")
    body = text[start : text.index("\n}", start)]
    ranges: dict[str, int] = {}
    for line in body.splitlines():
        match = APPRAISAL_RANGE_RE.match(line)
        if match:
            ranges[match.group(2).replace(" ", "_")] = int(match.group(1))
    return ranges


def validate_evidence_chain() -> None:
    receipt_schema = validate_schema_file(SCHEMAS / "source-receipt-v1.schema.json")
    result_schema = validate_schema_file(SCHEMAS / "appraisal-result-v1.schema.json")
    policy_schema = validate_schema_file(SCHEMAS / "appraisal-policy-v1.schema.json")

    evidence_policy = load_json(SCHEMAS / "evidence-profile-policy-v1.json")
    bundle = load_json(SCHEMAS / "appraisal-policy-v1.json")
    validate_instance(policy_schema, bundle, "appraisal policy bundle")
    assert_record_digest(bundle, "appraisal-policy-v1")

    source_digest = hashlib.sha256(canonical_cbor(evidence_policy)).hexdigest()
    if bundle["dimension_source"]["content_sha256"] != source_digest:
        raise ValidationFailure(
            "the appraisal policy bundle pins a stale digest of "
            "packages/schemas/evidence-profile-policy-v1.json; the dimension enums it "
            "binds are not the ones that file now carries"
        )

    # The refined source vocabulary: the owning file's enum with E1 replaced by its limbs.
    refinements = {
        entry["base_value"]: [limb["limb"] for limb in entry["limbs"]]
        for entry in bundle["dimension_refinements"]["source"]
    }
    refined_source: list[str] = []
    for value in evidence_policy["dimensions"]["source"]:
        refined_source.extend(refinements.get(value, [value]))

    expected_vocabularies = {
        "source_class": refined_source,
        "capture_class": evidence_policy["dimensions"]["capture"],
        "accounting_class": evidence_policy["dimensions"]["accounting"],
        "device_key_class": evidence_policy["dimensions"]["device_key"],
        "continuity_class": evidence_policy["dimensions"]["continuity"],
        "environment_class": evidence_policy["dimensions"]["environment"],
        "freshness_class": evidence_policy["dimensions"]["freshness"],
    }

    ordinals = bundle["wire_ordinals"]
    ranges = appraisal_wire_ranges()
    missing_ranges = set(ordinals) - set(ranges)
    if missing_ranges:
        raise ValidationFailure(
            f"the appraisal CDDL declares no range for: {sorted(missing_ranges)}"
        )
    for name, table in ordinals.items():
        values = sorted(table.values())
        if values != list(range(len(values))):
            raise ValidationFailure(
                f"appraisal wire ordinals for {name} are not dense from zero: {values}"
            )
        if values[-1] > ranges[name]:
            raise ValidationFailure(
                f"appraisal wire ordinal for {name} reaches {values[-1]}, outside the "
                f"CDDL range 0..{ranges[name]}"
            )
    for name, vocabulary in expected_vocabularies.items():
        if sorted(ordinals[name]) != sorted(vocabulary):
            raise ValidationFailure(
                f"the appraisal {name} vocabulary disagrees with "
                "packages/schemas/evidence-profile-policy-v1.json: "
                f"bundle {sorted(ordinals[name])}, policy {sorted(vocabulary)}"
            )
        schema_enum = result_schema["properties"]["dimensions"]["properties"][name][
            "enum"
        ]
        if sorted(schema_enum) != sorted(vocabulary):
            raise ValidationFailure(
                f"packages/schemas/appraisal-result-v1.schema.json enumerates {name} as "
                f"{sorted(schema_enum)}, which is not the policy vocabulary"
            )
    for name in ("acceptance_outcome", "ranking_eligibility"):
        schema_enum = result_schema["properties"][name]["enum"]
        if sorted(schema_enum) != sorted(ordinals[name]):
            raise ValidationFailure(
                f"the appraisal result and the policy bundle disagree on {name}"
            )
    anomaly_enum = result_schema["properties"]["evaluated"]["properties"][
        "anomaly_disposition"
    ]["enum"]
    if sorted(anomaly_enum) != sorted(ordinals["anomaly_disposition"]):
        raise ValidationFailure(
            "the appraisal result and the policy bundle disagree on anomaly_disposition"
        )

    awarded = result_schema["properties"]["awarded_profile_id"]["oneOf"][0]["enum"]
    registered_profiles = [
        profile["profile_id"] for profile in evidence_policy["profiles"]
    ]
    if sorted(awarded) != sorted(registered_profiles):
        raise ValidationFailure(
            "the appraisal result awards profiles the evidence policy does not define"
        )

    binding = bundle["appraisal_record"]["sql_binding"]
    ddl = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
    marker = f"create table {binding['table']} ("
    if marker not in ddl:
        raise ValidationFailure(
            f"the appraisal persistence owner {binding['table']} is not defined in the DDL"
        )
    block_start = ddl.index(marker)
    block = ddl[block_start : ddl.index("\n);", block_start)]
    columns = set(re.findall(r"^\s{2}([a-z0-9_]+)\s", block, flags=re.MULTILINE))
    for column in binding["bound_columns"] + binding["dropped_columns"]:
        if column not in columns:
            raise ValidationFailure(
                f"the appraisal SQL binding names column {column}, which "
                f"{binding['table']} does not define"
            )
    landed = [field for field in binding["unbound_fields"] if field in columns]
    if landed:
        raise ValidationFailure(
            f"{sorted(landed)} now exist as columns on {binding['table']}. The SQL half "
            f"of {binding['defect_reference']} has moved; move these entries from "
            "unbound_fields to bound_columns in packages/schemas/appraisal-policy-v1.json"
        )

    validate_instance(
        receipt_schema,
        load_json(CONFORMANCE / "evidence" / "source-receipt.valid.json"),
        "source receipt",
    )
    for name, label in (
        (
            "source-receipt.invalid-two-counted-observations.json",
            "two counted observations",
        ),
        ("source-receipt.invalid-provider-attested.json", "a provider-attested figure"),
        ("source-receipt.invalid-network-eligible.json", "a network-eligible receipt"),
        ("source-receipt.invalid-content-field.json", "a content field"),
    ):
        expect_invalid(
            receipt_schema,
            load_json(CONFORMANCE / "evidence" / name),
            f"source receipt carrying {label}",
        )

    for name in (
        "appraisal-result.valid-standard.json",
        "appraisal-result.valid-superseded.json",
    ):
        instance = load_json(CONFORMANCE / "evidence" / name)
        validate_instance(result_schema, instance, name)
        if instance["policy"]["content_sha256"] != bundle["content_sha256"]:
            raise ValidationFailure(f"{name} pins a stale appraisal policy digest")
    for name, label in (
        ("appraisal-result.invalid-e1r-hardened.json", "E1-R reaching Hardened"),
        (
            "appraisal-result.invalid-imported-competitive.json",
            "an imported source ranked competitively",
        ),
        (
            "appraisal-result.invalid-client-selected-state.json",
            "a client-selected public state",
        ),
    ):
        expect_invalid(
            result_schema,
            load_json(CONFORMANCE / "evidence" / name),
            f"appraisal result with {label}",
        )
    expect_invalid(
        policy_schema,
        load_json(
            CONFORMANCE
            / "evidence"
            / "appraisal-policy.invalid-second-dimension-authority.json"
        ),
        "appraisal policy bundle with a second dimension authority",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database-url", default=os.environ.get("PLANNING_DATABASE_URL")
    )
    parser.add_argument("--allow-no-postgres", action="store_true")
    args = parser.parse_args()

    checks = [
        ("JSON schemas, examples, and registries", validate_json_schemas_and_examples),
        ("adapter-one OTLP identity boundary", validate_adapter_one_boundary),
        ("policy and observability artifacts", validate_policy_and_observability),
        ("data disposition and retention coverage", validate_data_disposition),
        ("erasure and sealed-generation invariants", validate_erasure_contract),
        ("OpenAPI", validate_openapi_file),
        ("API error matrix and operation classes", validate_api_error_matrix),
        ("P-1140D state and platform contracts", validate_p1140d_contracts),
        ("accounting arithmetic vectors", validate_accounting_arithmetic),
        ("producer bindings and OTel capture vectors", validate_producer_bindings),
        (
            "observer equivalence and deduplication vectors",
            validate_observer_equivalence,
        ),
        (
            "source receipt, appraisal policy and appraisal result",
            validate_evidence_chain,
        ),
        (
            "identity lifecycle, presence and viewer authorization contracts",
            validate_identity_lifecycle_contracts,
        ),
        (
            "compatibility tuple, certification and install-plan contracts",
            validate_certification_contracts,
        ),
        (
            "TUF trust, compatibility graph and migration chain",
            validate_release_compatibility_contracts,
        ),
        ("decision register table integrity", validate_decision_register),
        ("CDDL grammar parse and required rules", validate_cddl_file),
        ("VibeProof exact-byte and malformed vectors", validate_vibeproof_vectors),
        ("VibeProof vector reproducibility", validate_vector_reproducibility),
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
        failures.append(
            "FAIL: PostgreSQL structural planning DDL: database URL required"
        )

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("planning artifact validation: pass")
    print("artifact maturity: structural planning only; not implementation evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
