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
import generate_planning_docs as planning_docs  # noqa: E402

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
PLANNING_SCHEMAS = CONFORMANCE / "planning"
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
        # PF-014. The four surfaces that carry content by accident rather than by
        # design, and the four the acceptance for the local store names. A log line, a
        # backup, a support bundle and a corruption report are each assembled while
        # something is going wrong, which is when quoting the thing that went wrong is
        # most tempting and least examined.
        "log",
        "backup",
        "diagnostic",
        "corruption-report",
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

# PF-043, D-613. `AppraisalSummary` is `VerifierAppraisalResult` minus exactly these
# two fields. The pair lives here rather than only in the OpenAPI description so that a
# field added to the record forces a disclosure decision instead of arriving on the
# wire by default: the top-level comparison below is an equality, so a new record field
# fails until it is either projected or named as withheld.
APPRAISAL_WITHHELD_FROM_SUBJECT = {
    # D-381. `under-review` and `shadow-only` are the statement that an integrity case
    # is open, and the participant reads the effect on their standing rather than the
    # existence of a case.
    "evaluated": "anomaly_disposition",
    # The server verifier's own build digest. Not the participant's personal data and
    # not needed to understand or appeal an outcome.
    "policy": "implementation_sha256",
}
# A wire concern of the stored record. The document carries its own version.
APPRAISAL_RECORD_ONLY = frozenset({"schema_version"})
# D-143 admits one evidence vocabulary to the API, and it is not `public_state`.
APPRAISAL_RENAMED = {"public_state": "evidence_class"}
# Groups the projection reproduces whole. Listing them is what stops the nested
# comparison being satisfied by a group the projection simply dropped.
APPRAISAL_WHOLE_GROUPS = ("attestation", "dimensions", "validity", "supersession")


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


PUBLIC_OPERATION_REASONS = {
    # auth-bootstrap  — establishes the very session a viewer check would need.
    # global-board    — the one universally public view AGENTS.md names.
    # reference-data  — carries no participant, so no viewer is relevant to it.
    "auth-bootstrap",
    "global-board",
    "reference-data",
}


def validate_public_operations(spec: dict) -> None:
    """An operation is public only if it is declared public, with a stated reason.

    Writing `security: []` is not by itself authority to be public. `getPublicProfile`
    carried it while its own response schema described "what a viewer authorized to
    read this profile receives", and `projection-authorization-v1.json` makes
    `directional-block` deny-hard in both directions and `subject-visibility`
    deny-unless-authorized. An unauthenticated caller has no viewer identity, so
    neither input could be evaluated: a blocked person could read the profile, with
    presence and social counts on it, by logging out.

    Requiring a declaration puts the reason where a reviewer sees it, and closing the
    set of admissible reasons stops the next one being argued into existence.
    """
    declared = spec.get("x-public-operations", {})
    for identifier, reason in sorted(declared.items()):
        if reason not in PUBLIC_OPERATION_REASONS:
            raise ValidationFailure(
                f"x-public-operations lists {identifier} with reason {reason!r}, which "
                f"is not one of {sorted(PUBLIC_OPERATION_REASONS)}; a free-text reason "
                "lets any operation be justified into being public"
            )

    for path, item in spec["paths"].items():
        for method, operation in item.items():
            if not isinstance(operation, dict) or "operationId" not in operation:
                continue
            identifier = operation["operationId"]
            is_public = operation.get("security") == []
            if is_public and identifier not in declared:
                raise ValidationFailure(
                    f"OpenAPI operation {identifier} is public and undeclared: it "
                    "carries security: [] and x-public-operations does not name it, so "
                    "no viewer check applies to it and no reason was recorded"
                )
            if identifier in declared and not is_public:
                raise ValidationFailure(
                    f"OpenAPI operation {identifier} is declared in "
                    "x-public-operations and does not carry security: []; a stale "
                    "declaration is how the next public operation goes unnoticed"
                )
            if is_public and operation.get("x-authorization") != "public":
                raise ValidationFailure(
                    f"OpenAPI operation {identifier} carries security: [] and "
                    f"x-authorization: {operation.get('x-authorization')!r}; the two "
                    "must agree or one of them is decorative"
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
    validate_public_operations(spec)

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
        # PF-013 split five subsystem projections out of interactive-shell, which had
        # collapsed collection, sync, auth, permission and connectivity into one state
        # variable. They persist in local-store-v1.sql and never leave the device.
        "local-collection",
        "local-sync",
        "local-auth",
        "local-permission",
        "local-connectivity",
    }
    if set(machine_ids) != required_machines:
        raise ValidationFailure(
            "state-machine set mismatch: "
            f"missing={sorted(required_machines - set(machine_ids))} "
            f"unexpected={sorted(set(machine_ids) - required_machines)}"
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


def validate_inventory_register() -> None:
    """Every inventory row must be unique and carry a declared status.

    The decision register grew a duplicate-id check after a rebase replayed the
    same row once per commit. The inventory has the same shape and had no such
    check, so the same rebase duplicated a specification family four times and a
    stale `planned-missing` row survived beside the current one that superseded
    it — found by hand, twice, which is not a control.

    A duplicated family is worse than untidy: the completeness count is read off
    this table, and two rows for one family means the count is wrong in whichever
    direction the duplicate leans.
    """
    inventory = ROOT / "docs" / "planning" / "SCHEMA_AND_INTERFACE_INVENTORY.md"
    text = inventory.read_text(encoding="utf-8")

    allowed = set(re.findall(r"^- \*\*([a-z-]+)\*\* —", text, re.MULTILINE))
    if not allowed:
        raise ValidationFailure(
            "SCHEMA_AND_INTERFACE_INVENTORY.md declares no status vocabulary"
        )

    seen: dict[str, int] = {}
    for number, line in enumerate(text.split("\n"), start=1):
        if not line.startswith("| ") or line.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 5 or cells[0] in {"Specification family", ""}:
            continue
        family, status = cells[0], cells[3]
        if set(family) <= {"-", " "}:
            continue
        if status not in allowed:
            raise ValidationFailure(
                f"SCHEMA_AND_INTERFACE_INVENTORY.md:{number} {family!r} has status "
                f"{status!r}, which is not one of {sorted(allowed)}"
            )
        if family in seen:
            raise ValidationFailure(
                f"SCHEMA_AND_INTERFACE_INVENTORY.md:{number} repeats the "
                f"specification family {family!r}, first recorded at line "
                f"{seen[family]}; the completeness count is read off this table, so "
                f"a duplicated family makes it wrong"
            )
        seen[family] = number


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


def validate_decision_traceability() -> None:
    """Every decision has a traceability row, and no two decisions are the same one.

    P-1140E froze its traceability matrix at `range(1, 70)` and delegated the rest to
    a validator that never references a `D-` identifier, so every decision from D-070
    onward had no row at all — 222 of 291. This runs over the register rather than
    over a fixed list, so a new decision cannot merge without a row.

    The duplicate check is here because the register held fifteen byte-identical
    pairs, D-320 through D-334 repeating D-380 through D-394 with no `supersedes`
    marker on either copy. Nothing compared decision text to decision text, so two
    ids meant the same thing and a reader could cite whichever they found first.
    """
    schema = load_json(PLANNING_SCHEMAS / "decision-traceability-v1.schema.json")
    instance = load_json(PLANNING_SCHEMAS / "decision-traceability-v1.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        ),
        key=lambda error: list(error.path),
    )
    if errors:
        raise ValidationFailure(
            "decision-traceability-v1.json: "
            + "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:3])
        )

    orphan_shards = planning_docs.orphaned_shards()
    if orphan_shards:
        raise ValidationFailure(
            "traceability shards on disk that nothing generates: "
            + ", ".join(path.name for path in orphan_shards)
        )

    missing = planning_docs.untraced()
    if missing:
        raise ValidationFailure(
            f"{len(missing)} decision(s) have no traceability row: {missing[:8]}"
        )
    orphans = planning_docs.orphaned()
    if orphans:
        raise ValidationFailure(
            f"traceability rows name decisions the register does not hold: {orphans[:8]}"
        )

    # Keyed on the decision text alone, and only for decisions that are still live.
    # Keying on the reopen condition too would let a duplicate be resolved by editing
    # the column nobody reads, which is not the same as resolving it. A `superseded`
    # twin is the correct record of a merge and is allowed.
    decisions = load_json(PLANNING_SCHEMAS / "decisions-v1.json")["decisions"]
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for row in decisions:
        if row["status"] == "superseded":
            continue
        if row["decision"] in seen:
            duplicates.append(f"{row['id']} repeats {seen[row['decision']]}")
        else:
            seen[row["decision"]] = row["id"]
    if duplicates:
        raise ValidationFailure(
            "two live decisions carry the same text, so two ids mean the same thing "
            "and a reader may cite whichever they find first: "
            + "; ".join(duplicates[:6])
        )


def validate_planning_doc_generation() -> None:
    """The register and catalog must equal what their JSON sources render.

    Both documents were hand-maintained Markdown that validators reached by
    substring matching, which is why the phase gate could once only be moved by
    editing its own validator. The structure now lives in `conformance/planning/`
    and the Markdown is output. If this fails, someone edited a generated block,
    and the register no longer says what its source says.
    """
    stale = planning_docs.stale()
    if stale:
        raise ValidationFailure(
            "planning documents are stale: "
            + ", ".join(path.name for path in stale)
            + "; run scripts/repository/generate_planning_docs.py"
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


NOTIFICATION_DELETION_EXAMPLES: tuple[tuple[str, str, bool], ...] = (
    ("notification-delivery-v1.schema.json", "notification-delivery.valid.json", True),
    (
        "notification-delivery-v1.schema.json",
        "notification-delivery.invalid-inbox-attempt-deferred.json",
        False,
    ),
    (
        "notification-delivery-v1.schema.json",
        "notification-delivery.invalid-suppressed-security-event.json",
        False,
    ),
    ("local-deletion-v1.schema.json", "local-deletion.valid.json", True),
    (
        "local-deletion-v1.schema.json",
        "local-deletion.invalid-complete-without-receipt.json",
        False,
    ),
    (
        "local-deletion-v1.schema.json",
        "local-deletion.invalid-unreachable-after-acknowledgement.json",
        False,
    ),
    (
        "local-deletion-v1.schema.json",
        "local-deletion.invalid-partial-receipt-on-complete-command.json",
        False,
    ),
)

# A notification carries references and never a rendered sentence. Each name below
# would be that sentence, and the reason it is refused is that a stored sentence
# freezes a handle, a figure and an authorization decision at write time — so a
# rename becomes wrong, a block leaks, and a retraction arrives after the recipient
# has already read the claim it withdraws.
NOTIFICATION_BANNED_FIELDS: tuple[str, ...] = (
    "title",
    "body",
    "message",
    "summary",
    "preview",
    "rendered_text",
    "subject_line",
)

# Names a per-device deletion receipt may not carry, because a user-space daemon
# cannot observe any of them and D-076 forbids claiming an erasure the product
# cannot observe.
DELETION_BANNED_FIELDS: tuple[str, ...] = (
    "unrecoverable",
    "irrecoverable",
    "forensic",
    "sanitized",
    "shredded",
    "wiped",
    "destroyed_permanently",
    "guaranteed_erased",
)

# Retained rows whose subject row an erasure deletes. Each is a NOT NULL foreign
# key into a table `packages/schemas/data-disposition-v1.json` classifies
# `delete`, so the erasure transaction that deletes the parent cannot commit while
# the child survives — which is exactly what its own `retain-unlinked`
# classification says it must do. D-425 records the class. The two per-device rows
# are repaired by this change; the six below are the same defect in aggregates
# this change does not own, and they are enumerated so a new one cannot be added
# silently.
# Empty, and it stays that way or it stops being an exception list.
#
# Six entries were recorded here when the rule was written, because a rule with
# six live violations is a wish. All six are repaired: each column is retained
# and its reference dropped, which is what `retain-unlinked` means in
# `packages/schemas/data-disposition-v1.json` and what
# `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` describes as "an identifier
# whose subject row is gone".
#
# An entry added here is a promise to remove it. An exception list that outlives
# its exceptions is a stale excuse, which is the failure mode this repository
# has spent a lot of effort removing.
ERASURE_FK_EXCEPTIONS: frozenset[tuple[str, str]] = frozenset()

# Any reference blocks the delete, not only a NOT NULL one.
#
# The first version of this rule matched `not null` and therefore saw six of the
# nine violations. The other three were nullable references with no ON DELETE
# action, and PostgreSQL refuses the parent delete for those exactly as hard —
# nullability decides whether a *row* may omit the reference, not whether the
# referenced row may be deleted. Three tables sat inside a rule that could not
# see them, and the gap only surfaced when an erasure was actually executed
# against a real database rather than reasoned about.
#
# ON DELETE CASCADE and ON DELETE SET NULL are excluded: both let the parent
# delete proceed, which is the property this rule is about.
_ERASURE_FK_RE = re.compile(
    r"^\s*([a-z_][a-z0-9_]*)\s+uuid"
    r"(?:\s+not\s+null)?(?:\s+primary\s+key)?"
    r"\s+references\s+([a-z_][a-z0-9_]*)\s*\([^)]*\)([^,\n]*)",
    re.MULTILINE,
)


def _declared_property_names(node: Any) -> set[str]:
    """Every property name a JSON Schema declares, at any depth.

    Scanning names rather than the serialized document is what keeps `title` in the
    banned list usable: the schema's own annotation keyword is not a field the
    record carries.
    """
    names: set[str] = set()
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict):
            names |= set(properties)
        for value in node.values():
            names |= _declared_property_names(value)
    elif isinstance(node, list):
        for value in node:
            names |= _declared_property_names(value)
    return names


def _schema_enum(schema: dict[str, Any], definition: str, prop: str) -> set[str]:
    return set(schema["$defs"][definition]["properties"][prop]["enum"])


def _sql_check_vocabulary(body: str, column: str) -> set[str]:
    match = re.search(
        rf"check\s*\(\s*{re.escape(column)}\s+in\s*\(([^)]*)\)\s*\)",
        body,
        re.IGNORECASE,
    )
    if not match:
        raise ValidationFailure(f"planning DDL declares no vocabulary for {column}")
    return set(re.findall(r"'([^']*)'", match.group(1)))


def validate_notification_and_local_deletion_contracts() -> None:
    """Prove the notification and per-device deletion records resolve.

    Seven checks, none of which is behaviour. The notification source event's state
    vocabulary equals the registered machine's, and the inbox item's is exactly the
    subset the binding table publishes, so the internal states cannot leak back onto
    the API through a second surface. Every policy key the notification model names
    resolves in the policy registry. Every retraction reason code resolves in the
    reason registry and is carried on the notification transport rather than as a
    Problem body. The per-device disposition, receipt outcome and residual-risk
    vocabularies equal the SQL and the device-side store that already declare them.
    No notification schema declares a rendered-message field and no deletion schema
    declares a field that would assert an erasure the product cannot observe. And no
    retained-unlinked table gains a NOT NULL foreign key into a table an erasure
    deletes outright, beyond the six that already carry one.

    This proves reference agreement. No worker groups an event, no transport carries
    a hint, no device executes a command, and this validator would pass identically
    if none ever did.
    """
    notification = validate_schema_file(
        SCHEMAS / "notification-delivery-v1.schema.json"
    )
    deletion = validate_schema_file(SCHEMAS / "local-deletion-v1.schema.json")

    registry = load_json(SCHEMAS / "state-machine-registry-v1.json")
    machines = {item["machine_id"]: item for item in registry["machines"]}

    machine_states = set(machines["notification-delivery"]["states"])
    event_states = _schema_enum(notification, "source_event", "state")
    if event_states != machine_states:
        raise ValidationFailure(
            "notification-delivery-v1.schema.json source_event.state differs from "
            f"notification-delivery: only-in-schema={sorted(event_states - machine_states)} "
            f"only-in-registry={sorted(machine_states - event_states)}"
        )

    # The four states before the inbox are worker state. The rule is stated once,
    # here and in the binding table, rather than left to two enums agreeing by luck.
    inbox_states = _schema_enum(notification, "inbox_item", "state")
    expected_inbox = machine_states - {"created", "grouped", "ready", "suppressed"}
    if inbox_states != expected_inbox:
        raise ValidationFailure(
            "notification-delivery-v1.schema.json inbox_item.state is not the "
            f"post-delivery subset: only-in-schema={sorted(inbox_states - expected_inbox)} "
            f"only-in-expected={sorted(expected_inbox - inbox_states)}"
        )

    command_states = _schema_enum(deletion, "command", "state")
    local_states = set(machines["local-deletion-command"]["states"])
    if command_states != local_states:
        raise ValidationFailure(
            "local-deletion-v1.schema.json command.state differs from "
            f"local-deletion-command: only-in-schema={sorted(command_states - local_states)} "
            f"only-in-registry={sorted(local_states - command_states)}"
        )

    policies = load_json(SCHEMAS / "policy-defaults-v1.json")["policies"]
    keys = notification["$defs"]["policy_keys"]["properties"]
    for field, node in keys.items():
        key = node["const"]
        if key not in policies:
            raise ValidationFailure(
                f"notification {field} names an unknown policy key: {key}"
            )

    codes = {
        item["code"]: item
        for item in load_json(SCHEMAS / "reason-codes-v1.json")["codes"]
    }
    for code in _schema_enum(notification, "retraction", "reason_code"):
        if code not in codes:
            raise ValidationFailure(
                f"retraction names an unregistered reason code: {code}"
            )
        if codes[code]["transport"] != "notification":
            raise ValidationFailure(
                f"retraction reason {code} is not carried on the notification transport"
            )

    bodies = _planning_table_bodies()
    for table, column, definition, prop in (
        ("local_deletion_commands", "disposition", "device_disposition", "disposition"),
        ("local_deletion_receipts", "outcome", "receipt", "outcome"),
        ("local_deletion_receipts", "residual_risk", "receipt", "residual_risk"),
        ("notification_deliveries", "state", "delivery_attempt", "state"),
        ("notification_deliveries", "transport", "delivery_attempt", "transport"),
    ):
        sql_values = _sql_check_vocabulary(bodies[table], column)
        schema_values = _schema_enum(
            deletion if table.startswith("local") else notification, definition, prop
        )
        if sql_values != schema_values:
            raise ValidationFailure(
                f"{table}.{column} differs from the schema: "
                f"only-in-sql={sorted(sql_values - schema_values)} "
                f"only-in-schema={sorted(schema_values - sql_values)}"
            )

    # The server receipt is the transported form of the device receipt, so the two
    # carry one vocabulary rather than two spellings of the same fact.
    local_store = (SCHEMAS / "local-store-v1.sql").read_text(encoding="utf-8")
    store_receipt = local_store.split("create table local_deletion_receipts (", 1)[1]
    for column in ("outcome", "residual_risk"):
        if _sql_check_vocabulary(store_receipt, column) != _sql_check_vocabulary(
            bodies["local_deletion_receipts"], column
        ):
            raise ValidationFailure(
                f"local_deletion_receipts.{column} differs between the device store "
                "and the server contract"
            )

    declared = _declared_property_names(notification)
    for banned in NOTIFICATION_BANNED_FIELDS:
        if banned in declared:
            raise ValidationFailure(
                f"notification-delivery-v1.schema.json declares {banned}: a "
                "notification carries references, never a rendered sentence"
            )
    declared = _declared_property_names(deletion)
    for banned in DELETION_BANNED_FIELDS:
        if banned in declared:
            raise ValidationFailure(
                f"local-deletion-v1.schema.json declares {banned}: no field may "
                "assert an erasure the product cannot observe"
            )

    disposition = load_json(SCHEMAS / "data-disposition-v1.json")
    actions = {
        entry["table"]: entry["erasure_action"] for entry in disposition["entries"]
    }
    for table, body in bodies.items():
        if actions.get(table) not in {"retain-unlinked", "retain-pseudonymous"}:
            continue
        for match in _ERASURE_FK_RE.finditer(body):
            column, target, trailing = match.group(1), match.group(2), match.group(3)
            if actions.get(target) != "delete":
                continue
            if "on delete" in trailing.lower():
                continue
            if (table, column) in ERASURE_FK_EXCEPTIONS:
                continue
            raise ValidationFailure(
                f"{table}.{column} references {target}, which an erasure deletes, "
                f"while {table} is classified {actions[table]}. PostgreSQL refuses "
                "the parent delete, so the erasure transaction cannot commit and the "
                "retained row cannot survive. Drop the reference and keep the "
                "identifier, or give it an explicit ON DELETE action"
            )

    for filename, example, expect_valid in NOTIFICATION_DELETION_EXAMPLES:
        schema = notification if filename.startswith("notification") else deletion
        instance = load_json(SCHEMAS / "examples" / example)
        if expect_valid:
            validate_instance(schema, instance, example)
        else:
            expect_invalid(schema, instance, example)


AUDIENCE_WIDTH = {"self": 0, "authorized-viewer": 1, "public": 2}


def validate_presentation_contracts() -> None:
    """Prove the disclosure and exceptional-state projections resolve.

    Three checks. Every field the disclosure profile names exists on the OpenAPI
    schema it names, so the projection cannot drift from the shapes it governs.
    No field is disclosed more widely than the shape that carries it, and
    `token_burn_total` and the two ADR-020 weight factors are pinned to `self`,
    which is D-144 expressed as a check rather than as a convention. And every
    server-derived exceptional state resolves to a registered machine and to
    states that machine actually declares, or to an input the viewer
    authorization profile declares.

    This proves the records resolve against the contracts they cite. No surface
    renders any of it: `packages/ui` is a fixture-backed prototype and nothing in
    it reads these files.
    """
    profile_schema = validate_schema_file(
        SCHEMAS / "disclosure-projection-v1.schema.json"
    )
    profile = load_json(SCHEMAS / "disclosure-projection-v1.json")
    validate_instance(profile_schema, profile, "disclosure projection")

    spec = load_yaml(SCHEMAS / "openapi-v1.yaml")
    api_schemas = spec["components"]["schemas"]
    for projection in profile["projections"]:
        name = projection["api_schema"]
        if name not in api_schemas:
            raise ValidationFailure(
                f"disclosure projection names a schema the API does not declare: {name}"
            )
        declared = set((api_schemas[name].get("properties") or {}).keys())
        named = {field["name"] for field in projection["fields"]}
        missing = sorted(named - declared)
        if missing:
            raise ValidationFailure(
                f"disclosure projection for {name} names fields the API does not "
                f"declare: {missing}"
            )
        uncovered = sorted(declared - named)
        if uncovered:
            raise ValidationFailure(
                f"disclosure projection for {name} does not classify every field: "
                f"{uncovered}"
            )
        # No field may be narrower than the shape that carries it. A narrower
        # field on a wider shape is a per-response redaction, and a redaction
        # that fails open publishes the field.
        shape_width = AUDIENCE_WIDTH[projection["audience"]]
        for field in projection["fields"]:
            if AUDIENCE_WIDTH[field["audience"]] < shape_width:
                raise ValidationFailure(
                    f"{name}.{field['name']} is narrower than the {name} shape, which "
                    f"is served to {projection['audience']}; move it to its own shape"
                )

    # D-144. These four never leave the participant's own surface, because the
    # raw figure beside the credited one yields the weight by division and the
    # weight is the sanction D-084 keeps private.
    self_only = {
        "token_burn_total",
        "confidence_weight_hundredths",
        "evidence_factor_hundredths",
        "trust_factor_hundredths",
    }
    seen_self_only: set[str] = set()
    for projection in profile["projections"]:
        for field in projection["fields"]:
            if field["name"] in self_only:
                seen_self_only.add(field["name"])
                if field["audience"] != "self":
                    raise ValidationFailure(
                        f"D-144: {projection['api_schema']}.{field['name']} is "
                        f"disclosed to {field['audience']}"
                    )
    if seen_self_only != self_only:
        raise ValidationFailure(
            f"disclosure projection does not classify every D-144 field: "
            f"{sorted(self_only - seen_self_only)}"
        )

    state_schema = validate_schema_file(SCHEMAS / "ui-state-projection-v1.schema.json")
    states = load_json(SCHEMAS / "ui-state-projection-v1.json")
    validate_instance(state_schema, states, "exceptional surface states")

    machines = {
        item["machine_id"]: item
        for item in load_json(SCHEMAS / "state-machine-registry-v1.json")["machines"]
    }
    authorization_inputs = {
        item["input_id"]
        for item in load_json(SCHEMAS / "projection-authorization-v1.json")["inputs"]
    }
    required_states = {
        "loading",
        "empty",
        "blocked",
        "private",
        "stale",
        "retracted",
        "appeal",
        "recovery",
    }
    declared_states = {item["state_id"] for item in states["states"]}
    if declared_states != required_states:
        raise ValidationFailure(
            f"exceptional state set mismatch: missing="
            f"{sorted(required_states - declared_states)} "
            f"extra={sorted(declared_states - required_states)}"
        )
    for item in states["states"]:
        if item["origin"] != "server-derived":
            continue
        if "authorization_input" in item:
            if item["authorization_input"] not in authorization_inputs:
                raise ValidationFailure(
                    f"exceptional state {item['state_id']} names an unknown "
                    f"authorization input: {item['authorization_input']}"
                )
            continue
        machine_id = item["machine_id"]
        if machine_id not in machines:
            raise ValidationFailure(
                f"exceptional state {item['state_id']} names an unregistered "
                f"machine: {machine_id}"
            )
        unknown = sorted(
            set(item["source_states"]) - set(machines[machine_id]["states"])
        )
        if unknown:
            raise ValidationFailure(
                f"exceptional state {item['state_id']} names states "
                f"{machine_id} does not declare: {unknown}"
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


def validate_origin_policy() -> None:
    """Prove the origin contract has one machine owner and that the API document agrees.

    D-230 and D-231 were prose. `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md` named
    three exact origins, eight loopback controls and a `Host` allowlist, and no
    generator could read any of it: the inventory recorded that the OpenAPI document
    declared no `Origin` parameter and no preflight response, so the origin arm of the
    ADR-015 requirement had no implementable form.

    Four checks. The policy record validates against its schema. The `x-origin-policy`
    block in the OpenAPI document is compared field by field against the record, in the
    same way `derive_operation_classes` compares the reason registry's recorded classes
    against the ones the document actually declares — a hand-maintained copy keeps
    passing after the thing it describes changes shape, and a derived one cannot. The
    `Origin` parameter is declared by exactly the operations whose security includes
    `csrfToken`, which is the state-changing cookie-authenticated set PF-039 already
    marked, so the origin arm binds to it by construction rather than by a second list.
    And every loopback listener binds all eight controls, sends no CORS header, and
    treats its input as untrusted.

    This proves the contract resolves. No server validates a `Host` header, no dashboard
    exists, and no CORS configuration exists, so nothing here is security evidence.
    """
    schema = validate_schema_file(SCHEMAS / "origin-policy-v1.schema.json")
    policy = load_json(SCHEMAS / "origin-policy-v1.json")
    validate_instance(schema, policy, "origin policy")

    spec = load_yaml(SCHEMAS / "openapi-v1.yaml")
    block = spec.get("x-origin-policy")
    if not isinstance(block, dict):
        raise ValidationFailure("OpenAPI declares no x-origin-policy block")
    if block.get("contract") != "packages/schemas/origin-policy-v1.json":
        raise ValidationFailure("x-origin-policy does not name the policy record")
    if block.get("normative_owner") != policy["normative_owner"]:
        raise ValidationFailure("x-origin-policy names a different normative owner")

    api = policy["public_api"]
    for key in (
        "wildcard_origin",
        "origin_reflection",
        "subdomain_wildcard",
        "allowed_origins",
        "preflight",
        "state_changing_checks",
        "bearer_exemption",
    ):
        if block.get(key) != api[key]:
            raise ValidationFailure(
                f"x-origin-policy diverges from the policy record at {key}"
            )
    binding = api["openapi_binding"]
    projected = block.get("parameter_binding") or {}
    for key in (
        "origin_parameter",
        "preflight_response",
        "required_on_security_scheme",
        "preflight_routing",
    ):
        if projected.get(key) != binding[key]:
            raise ValidationFailure(
                f"x-origin-policy parameter binding diverges at {key}"
            )

    # A wildcard, a path, a userinfo section or an uppercase host is refused by the
    # `origin` pattern in origin-policy-v1.schema.json rather than here, so that the
    # refusal lives with the shape it constrains and no second, weaker copy of the rule
    # can drift away from it.
    local = [
        origin
        for origin in api["allowed_origins"]
        if origin["environments"] == ["local"]
    ]
    if not local:
        raise ValidationFailure("no origin is confined to the local environment")
    for origin in local:
        if origin["production_build"] != "compiled-out":
            raise ValidationFailure(
                "the development origin is disabled by configuration rather than "
                f"compiled out of the production build: {origin['origin']}"
            )
    for origin in api["allowed_origins"]:
        if (
            origin["environments"] != ["local"]
            and origin["production_build"] != "included"
        ):
            raise ValidationFailure(
                f"a production origin is compiled out: {origin['origin']}"
            )

    reason_codes = {
        item["code"] for item in load_json(SCHEMAS / "reason-codes-v1.json")["codes"]
    }
    orders = [check["order"] for check in api["state_changing_checks"]]
    if orders != sorted(orders) or len(set(orders)) != len(orders):
        raise ValidationFailure("state-changing checks are not a strict order")
    for check in api["state_changing_checks"]:
        code = check["on_failure"]["reason_code"]
        if check["enforced_by"] == "browser":
            if code is not None:
                raise ValidationFailure(
                    f"a browser-enforced check carries a server reason code: {check['check_id']}"
                )
            continue
        if code not in reason_codes:
            raise ValidationFailure(
                f"state-changing check names an unknown reason code: {code}"
            )
    known_checks = {check["check_id"] for check in api["state_changing_checks"]}
    unknown = sorted(set(api["bearer_exemption"]["exempt_checks"]) - known_checks)
    if unknown:
        raise ValidationFailure(f"bearer exemption names unknown checks: {unknown}")
    for check_id in api["bearer_exemption"]["exempt_checks"]:
        check = next(
            item
            for item in api["state_changing_checks"]
            if item["check_id"] == check_id
        )
        if check["enforced_by"] != "server":
            raise ValidationFailure(
                f"bearer exemption exempts a check no server performs: {check_id}"
            )

    parameters = spec["components"]["parameters"]
    if "Origin" not in parameters:
        raise ValidationFailure("OpenAPI declares no Origin parameter")
    declared_origins = set(parameters["Origin"]["schema"]["enum"])
    recorded_origins = {origin["origin"] for origin in api["allowed_origins"]}
    if declared_origins != recorded_origins:
        raise ValidationFailure(
            "the Origin parameter enum differs from the allowlist: "
            f"only-in-openapi={sorted(declared_origins - recorded_origins)} "
            f"only-in-policy={sorted(recorded_origins - declared_origins)}"
        )
    if "Preflight" not in spec["components"]["responses"]:
        raise ValidationFailure("OpenAPI declares no Preflight response component")
    preflight_headers = set(spec["components"]["responses"]["Preflight"]["headers"])
    required_headers = {
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers",
        "Access-Control-Expose-Headers",
        "Access-Control-Allow-Credentials",
        "Access-Control-Max-Age",
    }
    missing_headers = sorted(required_headers - preflight_headers)
    if missing_headers:
        raise ValidationFailure(
            f"the Preflight response omits declared headers: {missing_headers}"
        )
    for header in preflight_headers:
        if spec["components"]["responses"]["Preflight"]["headers"][header].get(
            "required"
        ):
            raise ValidationFailure(
                "a preflight header is declared required, which contradicts the rule "
                f"that a non-allowlisted origin receives none of them: {header}"
            )

    scheme = binding["required_on_security_scheme"]
    reference = binding["origin_parameter"]
    for path, item in spec["paths"].items():
        for method, operation in item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            security = operation.get("security") or []
            expected = any(scheme in alternative for alternative in security)
            refs = {
                entry.get("$ref")
                for entry in operation.get("parameters", [])
                if isinstance(entry, dict)
            }
            if expected and reference not in refs:
                raise ValidationFailure(
                    "a state-changing cookie-authenticated operation declares no "
                    f"Origin parameter: {operation['operationId']}"
                )
            if not expected and reference in refs:
                raise ValidationFailure(
                    "an operation declares an Origin parameter without the "
                    f"{scheme} scheme that binds it: {operation['operationId']}"
                )

    control_ids = {control["control_id"] for control in policy["loopback_controls"]}
    if len(control_ids) != 8:
        raise ValidationFailure(
            "the loopback control vocabulary is not the eight D-231 controls"
        )
    numbers = sorted(control["number"] for control in policy["loopback_controls"])
    if numbers != list(range(1, 9)):
        raise ValidationFailure("loopback control numbers are not 1 through 8")
    refusal_codes = {item["code"] for item in policy["loopback_refusal_codes"]}
    for item in policy["loopback_refusal_codes"]:
        if item["control_id"] not in control_ids:
            raise ValidationFailure(
                f"a loopback refusal code names an unknown control: {item['code']}"
            )
        if item["code"] in reason_codes:
            raise ValidationFailure(
                "a loopback refusal code was added to the API reason registry, where "
                f"every wire-visible code must bind to a declared operation: {item['code']}"
            )
    for listener in policy["loopback_listeners"]:
        bound = {binding["control_id"] for binding in listener["controls"]}
        if bound != control_ids:
            raise ValidationFailure(
                f"{listener['listener_id']} does not bind every loopback control: "
                f"missing={sorted(control_ids - bound)} unknown={sorted(bound - control_ids)}"
            )
        for entry in listener["controls"]:
            code = entry.get("refusal_code")
            if code is not None and code not in refusal_codes:
                raise ValidationFailure(
                    f"{listener['listener_id']} names an unknown refusal code: {code}"
                )
            if entry["state"] == "not-applicable" and code is not None:
                raise ValidationFailure(
                    f"{listener['listener_id']} refuses with a control it does not apply: {code}"
                )
        if listener["cors_headers"] != "none":
            raise ValidationFailure(
                f"{listener['listener_id']} sends CORS headers on a loopback surface"
            )
        if listener["input_trust"] != "untrusted":
            raise ValidationFailure(
                f"{listener['listener_id']} trusts its own input; an origin control is "
                "not a substitute for validating what a local process can post"
            )
        if listener["authentication"] == "none" and "residual_exposure" not in listener:
            raise ValidationFailure(
                "an unauthenticated loopback listener records no residual exposure: "
                f"{listener['listener_id']}"
            )


# Directories under `conformance/` that are records rather than suites.
#
# A manifest under D-441 declares a set of cases and what executing them proves.
# These three hold planning state that validators read — gate authorization,
# semantic findings, the decision register and task catalog — and there is nothing
# in them to execute, so a manifest could only describe an empty run. The criterion
# is stated here because the list was previously three bare names, and an exemption
# whose reason is not written down cannot be told apart from an oversight.
CONFORMANCE_EXEMPT_SUITES = ("p1140e", "p1140f", "planning")

# The two registries an `expect_reason_code` may resolve in, and where the codes live in
# each. `reason-codes-v1.json` is the API wire vocabulary and requires every code to bind
# to a declared OpenAPI operation, so a loopback refusal cannot live there; the origin
# policy owns that second vocabulary and this map is what keeps both checkable.
CONFORMANCE_REASON_AUTHORITIES = {
    "packages/schemas/reason-codes-v1.json": ("codes", "code"),
    "packages/schemas/origin-policy-v1.json": ("loopback_refusal_codes", "code"),
}


def _heading_slugs(text: str) -> set[str]:
    """GitHub-flavoured anchor slugs for every heading in a markdown document."""
    slugs = set()
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.*?)\s*$", line)
        if not match:
            continue
        title = match.group(1).replace("`", "")
        title = re.sub(r"[^\w\s-]", "", title).strip().lower()
        slugs.add(re.sub(r"\s+", "-", title))
    return slugs


def _pointer_resolves(document: Any, pointer: str) -> bool:
    node = document
    for token in pointer.lstrip("#").strip("/").split("/"):
        if token == "":
            continue
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if token not in node:
                return False
            node = node[token]
        elif isinstance(node, list):
            if not token.isdigit() or int(token) >= len(node):
                return False
            node = node[int(token)]
        else:
            return False
    return True


def _assert_reference_resolves(reference: str, label: str) -> None:
    path, _, fragment = reference.partition("#")
    target = ROOT / path
    if not target.is_file():
        raise ValidationFailure(f"{label} names a path that does not resolve: {path}")
    if not fragment:
        return
    if path.endswith(".md"):
        if fragment not in _heading_slugs(target.read_text(encoding="utf-8")):
            raise ValidationFailure(
                f"{label} names a heading that does not exist: {reference}"
            )
        return
    if path.endswith(".json"):
        document = load_json(target)
    elif path.endswith((".yaml", ".yml")):
        document = load_yaml(target)
    else:
        raise ValidationFailure(
            f"{label} carries a fragment on a file with no addressable members: {reference}"
        )
    if not _pointer_resolves(document, fragment):
        raise ValidationFailure(f"{label} names an unresolved pointer: {reference}")


def validate_conformance_manifests() -> None:
    """Prove every conformance suite declares a manifest and that it resolves.

    D-242 designed the manifest and nothing had one. Forty-five files of fixture data
    sat under `conformance/` with no machine record of what tests what, which is how
    `conformance/vibeproof/v1/` — the normative corpus — went unexecuted while
    `conformance/protocol/`, an exploratory shadow codec, ran in its place under a
    suite name that did not describe what it executed.

    Six invariants, all mechanical. Every suite directory holds exactly one manifest
    and a README. Every path in `authorities`, `tooling`, `generated_by`, `fixtures`
    and `authority_ref` resolves, and a fragment resolves to a real heading or a real
    pointer rather than to a plausible-looking one. Every recorded fixture digest
    matches the file, so a fixture cannot be edited without its expectation being
    revisited in the same diff. Every file in the suite directory is named by the
    manifest, so a fixture cannot hide from the record. Case identifiers are unique
    across the repository, correctly prefixed and three digits. And a populated suite
    declares at least one negative case, because a suite composed entirely of things
    that should work does not prove that the boundary rejects anything.

    Passing this is not conformance and changes no eval suite status. It proves a
    manifest is well formed. A suite whose manifest validates and whose runner does not
    exist stays `not_applicable`.
    """
    schema = validate_schema_file(SCHEMAS / "conformance-manifest-v1.schema.json")
    eval_suites = {
        suite["id"]
        for suite in load_yaml(ROOT / "evals" / "suites" / "suites.yaml")["suites"]
    }

    manifests = sorted(CONFORMANCE.glob("**/manifest.json"))
    if not manifests:
        raise ValidationFailure("no conformance suite declares a manifest")

    covered_roots: dict[str, Path] = {}
    for path in manifests:
        top = path.relative_to(CONFORMANCE).parts[0]
        if top in CONFORMANCE_EXEMPT_SUITES:
            raise ValidationFailure(
                f"a planning-review registry declares a conformance manifest: {top}"
            )
        if top in covered_roots:
            raise ValidationFailure(f"two manifests claim the same suite: {top}")
        covered_roots[top] = path.parent

    for child in sorted(CONFORMANCE.iterdir()):
        if not child.is_dir() or child.name in CONFORMANCE_EXEMPT_SUITES:
            continue
        if child.name not in covered_roots:
            raise ValidationFailure(
                f"conformance suite declares no manifest: {child.name}"
            )

    all_case_ids: list[str] = []
    for path in manifests:
        relative = path.relative_to(ROOT).as_posix()
        manifest = load_json(path)
        validate_instance(schema, manifest, relative)
        suite = manifest["suite_id"]
        top = path.relative_to(CONFORMANCE).parts[0]
        if suite != top:
            raise ValidationFailure(
                f"{relative}: suite_id {suite} is not the directory name {top}"
            )
        if not (path.parent / "README.md").is_file():
            raise ValidationFailure(f"{relative}: the suite declares no README")

        unknown_evals = sorted(set(manifest["eval_suite_ids"]) - eval_suites)
        if unknown_evals:
            raise ValidationFailure(
                f"{relative}: names eval suites the registry does not declare: {unknown_evals}"
            )
        for authority in manifest["authorities"]:
            _assert_reference_resolves(authority, f"{relative} authority")
        for tool in manifest.get("tooling", []):
            _assert_reference_resolves(tool, f"{relative} tooling")
        if manifest["generated_by"]:
            _assert_reference_resolves(
                manifest["generated_by"], f"{relative} generated_by"
            )

        authority_name, code_key = CONFORMANCE_REASON_AUTHORITIES[
            manifest["reason_authority"]
        ]
        authority_record = load_json(ROOT / manifest["reason_authority"])
        valid_codes = {item[code_key] for item in authority_record[authority_name]}

        cases = manifest["cases"]
        if manifest["fixture_state"] == "empty":
            if cases:
                raise ValidationFailure(
                    f"{relative}: declares cases while recording an empty fixture state"
                )
            if manifest["runner"]["state"] != "absent":
                raise ValidationFailure(
                    f"{relative}: declares a runner for a suite with no fixture"
                )
        else:
            if not cases:
                raise ValidationFailure(
                    f"{relative}: holds fixtures and declares no case"
                )
            has_negative = any(
                case["negative"] for case in cases if case["state"] == "active"
            )
            declares_gap = "negative_case_gap" in manifest
            if not has_negative and not declares_gap:
                raise ValidationFailure(
                    f"{relative}: declares no negative case and no negative_case_gap, "
                    "so it cannot show that the boundary rejects anything and does not "
                    "say so"
                )
            if has_negative and declares_gap:
                raise ValidationFailure(
                    f"{relative}: declares a negative_case_gap it no longer has; a "
                    "justification that outlives the hole it explained is a stale excuse"
                )

        named: set[str] = set(manifest.get("tooling", []))
        for case in cases:
            case_id = case["case_id"]
            all_case_ids.append(case_id)
            if not case_id.startswith(manifest["case_prefix"] + "-"):
                raise ValidationFailure(
                    f"{relative}: case {case_id} does not carry the suite prefix "
                    f"{manifest['case_prefix']}"
                )
            _assert_reference_resolves(case["authority_ref"], f"{relative} {case_id}")
            code = case["expect_reason_code"]
            if code is not None and code not in valid_codes:
                raise ValidationFailure(
                    f"{relative}: case {case_id} names a reason code that does not "
                    f"resolve in {manifest['reason_authority']}: {code}"
                )
            for fixture in case["fixtures"]:
                fixture_path = ROOT / fixture["path"]
                if not fixture_path.is_file():
                    raise ValidationFailure(
                        f"{relative}: case {case_id} names a missing fixture: {fixture['path']}"
                    )
                if not fixture_path.resolve().is_relative_to(path.parent.resolve()):
                    raise ValidationFailure(
                        f"{relative}: case {case_id} names a fixture outside its suite: "
                        f"{fixture['path']}"
                    )
                digest = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
                if digest != fixture["sha256"]:
                    raise ValidationFailure(
                        f"{relative}: case {case_id} records a stale digest for "
                        f"{fixture['path']}: recorded {fixture['sha256']}, computed {digest}"
                    )
                named.add(fixture["path"])

        for authority in manifest["authorities"]:
            if (ROOT / authority).resolve().is_relative_to(path.parent.resolve()):
                named.add(authority)

        present = {
            candidate.relative_to(ROOT).as_posix()
            for candidate in path.parent.rglob("*")
            if candidate.is_file()
            and candidate.name not in {"manifest.json", "README.md"}
        }
        unnamed = sorted(present - named)
        if unnamed:
            raise ValidationFailure(
                f"{relative}: the suite holds files no case, authority or tooling entry "
                f"names: {unnamed}"
            )

    assert_unique(all_case_ids, "conformance case IDs")


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
    binding: dict[str, Any], metric_name: str, series: list[dict[str, Any]]
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
    # Selected by name rather than by position. Reading metrics[0] meant a binding
    # could declare a second metric and have every vector silently replayed against
    # the first one's category map, which is a registry implying exercised support it
    # does not have.
    metrics = {item["name"]: item for item in binding["otel"]["metrics"]}
    if metric_name not in metrics:
        raise ValidationFailure(
            f"OTel capture vectors name metric {metric_name}, which binding "
            f"{binding['binding_id']} does not declare"
        )
    metric = metrics[metric_name]
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
    declared_metrics = {item["name"] for item in binding["otel"]["metrics"]}
    if capture["metric"] not in declared_metrics:
        raise ValidationFailure("OTel capture vectors name a metric the binding omits")
    # PF-041. Every metric a binding declares must be replayed by a capture, so a
    # binding cannot list a metric it has never exercised. The vectors file carries one
    # metric, so a binding declaring two would need a second vectors file before the
    # second metric could be declared at all.
    uncaptured = sorted(declared_metrics - {capture["metric"]})
    if uncaptured:
        raise ValidationFailure(
            f"producer binding {capture['binding_id']} declares metrics no capture "
            f"vector replays: {uncaptured}; a declared metric with no capture is "
            "support the registry has not exercised"
        )

    conditions: set[str] = set()
    for vector in capture["vectors"]:
        outcome, detail = evaluate_otel_series(
            binding, capture["metric"], vector["series"]
        )
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


# The three hazards PF-041 records. Pinned here so the profile cannot drop one and
# still pass: an omitted hazard is exactly the failure a receiver written against a
# producer's documented behaviour rather than its default behaviour would make.
OTEL_REQUIRED_HAZARDS = frozenset(
    {
        "identity-attributes-on-every-datapoint",
        "default-on-prompt-logging",
        "default-third-party-metrics-exporter",
    }
)


def validate_otel_accounting_profile() -> None:
    """Prove the OTLP-to-event profile is a map and that its support claims are exercised.

    PF-041's acceptance was that the profile maps a captured OTLP payload to a
    `NormalizedAccountingEvent` deterministically, with one real capture per supported
    metric. The second half is checkable and is checked here by equality: the supported
    metric set equals the metric set the binding declares, and each one names a capture
    fixture that exists and replays that exact metric. The first half is not
    satisfiable as written and the unit records why — an OTLP counter carries no
    outcome, no retry and no event identity, and `certification.bundle_sha256` cannot
    be written from any binding in this repository. So what is proven is narrower and
    true: every top-level field of the target schema has exactly one declared origin,
    the fields that cannot be read from the payload say so, and a disagreement with a
    bound authority is declared rather than left for a reader to find.

    The attribute check is the load-bearing one. A derivation may only read an
    attribute the binding admits, so no field can be derived from an identity attribute
    the strip list removes. That is D-099 expressed against the derivation table rather
    than only against the receiver.
    """
    profile_schema = validate_schema_file(
        SCHEMAS / "accounting-profile-otel-v1.schema.json"
    )
    profile = load_json(SCHEMAS / "accounting-profile-otel-v1.json")
    validate_instance(profile_schema, profile, "OTel accounting profile")

    for key in ("target_schema", "specification"):
        if not (ROOT / profile[key]).exists():
            raise ValidationFailure(
                f"the OTel accounting profile names {key} {profile[key]}, which does "
                "not exist"
            )

    bindings = {
        entry["binding_id"]: entry
        for entry in load_json(
            CONFORMANCE / "accounting" / "producer-bindings-v1.json"
        )["bindings"]
    }
    binding = bindings.get(profile["binding_id"])
    if binding is None:
        raise ValidationFailure(
            f"the OTel accounting profile binds {profile['binding_id']}, which the "
            "producer binding registry does not declare"
        )
    if binding["producer_kind"] != "otel":
        raise ValidationFailure(
            f"the OTel accounting profile binds {profile['binding_id']}, which is a "
            f"{binding['producer_kind']} producer"
        )

    # One real capture per supported metric, and no metric declared without one.
    supported = {item["name"]: item for item in profile["supported_metrics"]}
    assert_unique(list(supported), "supported OTel metric names")
    declared = {item["name"] for item in binding["otel"]["metrics"]}
    if set(supported) != declared:
        raise ValidationFailure(
            "the OTel accounting profile's supported metrics differ from the metrics "
            f"{profile['binding_id']} declares: "
            f"only-in-profile={sorted(set(supported) - declared)} "
            f"only-in-binding={sorted(declared - set(supported))}"
        )
    for name, entry in sorted(supported.items()):
        path = ROOT / entry["capture_vectors"]
        if not path.exists():
            raise ValidationFailure(
                f"supported metric {name} names capture vectors at "
                f"{entry['capture_vectors']}, which do not exist"
            )
        capture = load_json(path)
        if capture["metric"] != name:
            raise ValidationFailure(
                f"supported metric {name} names a capture fixture that replays "
                f"{capture['metric']}"
            )
        if capture["binding_id"] != profile["binding_id"]:
            raise ValidationFailure(
                f"supported metric {name} names a capture fixture bound to "
                f"{capture['binding_id']}"
            )
        if not any(
            vector["kind"] == "datapoint-series" for vector in capture["vectors"]
        ):
            raise ValidationFailure(
                f"supported metric {name} has only refusal vectors; a refusal proves "
                "the receiver rejects something and never proves it can count"
            )

    unsupported = {item["name"] for item in profile["unsupported_metrics"]}
    overlap = sorted(unsupported & set(supported))
    if overlap:
        raise ValidationFailure(
            f"the OTel accounting profile calls the same metric supported and "
            f"unsupported: {overlap}"
        )
    discarded = {item["name"] for item in binding["otel"]["discarded_metrics"]}
    missing_discards = sorted(discarded - unsupported - {"*"})
    if missing_discards:
        raise ValidationFailure(
            f"{profile['binding_id']} discards metrics the profile does not record as "
            f"unsupported: {missing_discards}"
        )

    products = {
        item["id"]
        for item in load_json(CONFORMANCE / "adapters" / "agent-registry-v1.json")[
            "products"
        ]
    }
    named = {item["producer_id"] for item in profile["supported_metrics"]}
    named |= {item["producer_id"] for item in profile["unsupported_metrics"]}
    named |= {item["producer_id"] for item in profile["capture_surface_hazards"]}
    unknown = sorted(named - products)
    if unknown:
        raise ValidationFailure(
            f"the OTel accounting profile names producers the agent registry does not "
            f"declare: {unknown}"
        )

    hazards = {item["kind"]: item for item in profile["capture_surface_hazards"]}
    if set(hazards) != OTEL_REQUIRED_HAZARDS:
        raise ValidationFailure(
            "the OTel accounting profile's hazard set differs from PF-041: "
            f"missing={sorted(OTEL_REQUIRED_HAZARDS - set(hazards))} "
            f"extra={sorted(set(hazards) - OTEL_REQUIRED_HAZARDS)}"
        )
    identity = hazards["identity-attributes-on-every-datapoint"]
    if tuple(sorted(identity.get("attributes", ()))) != ADAPTER_ONE_STRIP_LIST:
        raise ValidationFailure(
            "the OTel accounting profile's identity hazard does not name the D-099 "
            f"strip list: {sorted(identity.get('attributes', ()))}"
        )
    if identity["configuration_is_a_control"] == "yes":
        raise ValidationFailure(
            "the OTel accounting profile records producer configuration as a full "
            "control over the identity attributes; no documented setting removes "
            "user.email, so the strip is a receiver obligation"
        )

    # One origin per top-level field of the target schema, by equality in both
    # directions. A field added to the event fails here until someone says where it
    # comes from, and a derivation for a field the event dropped fails too.
    target = load_json(ROOT / profile["target_schema"])
    fields = {item["field"]: item for item in profile["derivations"]}
    assert_unique(
        [item["field"] for item in profile["derivations"]], "derivation fields"
    )
    expected_fields = set(target["properties"])
    if set(fields) != expected_fields:
        raise ValidationFailure(
            "the OTel accounting profile does not derive every field of "
            f"{profile['target_schema']}: "
            f"only-in-profile={sorted(set(fields) - expected_fields)} "
            f"only-in-target={sorted(expected_fields - set(fields))}"
        )

    admitted = {
        entry["attribute"]
        for entry in binding["attribute_policy"]["entries"]
        if entry["disposition"] in {"allow", "transform"}
    }
    refused = {
        entry["attribute"]
        for entry in binding["attribute_policy"]["entries"]
        if entry["disposition"] in {"strip", "drop"}
    }
    contradictions = {
        item["contradiction_id"] for item in profile["known_contradictions"]
    }
    for name, entry in sorted(fields.items()):
        attributes = set(entry.get("otlp_attributes", ()))
        if attributes and entry["origin"] not in {"otlp-attribute", "otlp-datapoint"}:
            raise ValidationFailure(
                f"derivation {name} reads OTLP attributes with origin "
                f"{entry['origin']}, which is not a reading of the payload"
            )
        forbidden = sorted(attributes & refused)
        if forbidden:
            raise ValidationFailure(
                f"derivation {name} reads attributes the binding strips or drops: "
                f"{forbidden}"
            )
        unknown_attributes = sorted(attributes - admitted)
        if unknown_attributes:
            raise ValidationFailure(
                f"derivation {name} reads attributes the binding does not admit: "
                f"{unknown_attributes}"
            )
        if entry["origin"] == "not-derivable-from-otlp":
            if entry["determinism"] != "not-observable":
                raise ValidationFailure(
                    f"derivation {name} is not derivable from OTLP and claims "
                    f"determinism {entry['determinism']}; a value the channel carries "
                    "no fact about is a declared stand-in, not an observation"
                )
            # A scalar field must name the literal that stands in for the missing
            # fact. An object field cannot, and saying so by type rather than by
            # exception is what keeps this from being a list of excused fields.
            is_object = "properties" in target["properties"][name]
            if not is_object and "constant" not in entry:
                raise ValidationFailure(
                    f"derivation {name} carries no fact and no constant, so nothing "
                    "says what is written"
                )
        blocked = entry.get("blocked_by")
        if blocked is not None and blocked not in contradictions:
            raise ValidationFailure(
                f"derivation {name} is blocked by {blocked}, which "
                "known_contradictions does not declare"
            )

    if fields["count_authority"].get("constant") != profile["count_authority"]:
        raise ValidationFailure(
            "the OTel accounting profile's count_authority and its own derivation of "
            "that field disagree"
        )

    # The count_authority disagreement is computed rather than trusted, so the
    # declaration cannot outlive the disagreement and the disagreement cannot outlive
    # the declaration.
    profiles = {
        item["profile_id"]: item
        for item in load_json(
            CONFORMANCE / "accounting" / "accounting-profiles-v1.json"
        )["profiles"]
    }
    bound = profiles[binding["accounting_profile"]["id"]]
    authorities = {field["authority"] for field in bound["source_fields"]}
    declared_contradictions = {
        item["field"] for item in profile["known_contradictions"]
    }
    disagrees = authorities != {profile["count_authority"]}
    if disagrees and "count_authority" not in declared_contradictions:
        raise ValidationFailure(
            f"{bound['profile_id']} declares its source fields {sorted(authorities)} "
            f"while this profile writes count_authority {profile['count_authority']}, "
            "and no known_contradictions entry declares it"
        )
    if not disagrees and "count_authority" in declared_contradictions:
        raise ValidationFailure(
            "a count_authority contradiction is declared and the bound accounting "
            "profile now agrees; remove the entry rather than leaving a record that "
            "describes nothing"
        )

    # The certification gap is computed the same way: a binding that acquires a
    # bundle digest must not keep a declaration saying it has none.
    bundle = binding["certification"]["tuple"]["bundle_sha256"]
    certification_declared = "certification" in declared_contradictions
    if bundle is None and not certification_declared:
        raise ValidationFailure(
            f"{profile['binding_id']} carries no certification bundle digest while "
            "normalized-event.schema.json requires one, and no known_contradictions "
            "entry declares it"
        )
    if bundle is not None and certification_declared:
        raise ValidationFailure(
            f"{profile['binding_id']} now carries a certification bundle digest; the "
            "declared certification contradiction has outlived its hole"
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


def enum_values(node: dict[str, Any]) -> frozenset:
    """Every literal a node admits, ignoring the null limb.

    `const`, `enum` and a `oneOf` over either are three spellings of the same
    statement, and the record and the API document do not use the same one.
    """
    if "const" in node:
        return frozenset({node["const"]})
    if "enum" in node:
        return frozenset(value for value in node["enum"] if value is not None)
    values: set = set()
    for branch in node.get("oneOf", []):
        values |= enum_values(branch)
    return frozenset(values)


def enum_map(schema: dict[str, Any], prefix: str = "") -> dict[str, frozenset]:
    """Flatten a schema to `path -> admitted literals` for every field that has any."""
    found: dict[str, frozenset] = {}
    for name, node in (schema.get("properties") or {}).items():
        path = f"{prefix}{name}"
        if "properties" in node:
            found.update(enum_map(node, f"{path}."))
            continue
        values = enum_values(node)
        if values:
            found[path] = values
    return found


def validate_appraisal_disclosure() -> None:
    """Prove `ClaimRecord.appraisal_id` resolves, and to a projection rather than a record.

    PF-043's acceptance is that the reference resolves to a defined schema and a
    retrievable operation. Resolving it is the easy half. The half that decides whether
    the operation may exist at all is that an appraisal is integrity-private: the
    identifier is classified `self` on a `self` shape, so there is no non-owner audience
    for any field, and two fields are withheld from the owner as well.

    So this proves four things a description alone cannot. The operation exists, is
    authenticated, and answers with `AppraisalSummary`. That shape is the record minus
    exactly `APPRAISAL_WITHHELD_FROM_SUBJECT`, by equality in both directions, so a
    field added to `appraisal-result-v1.schema.json` fails here until someone decides
    whether the subject sees it. The two withheld names appear nowhere in the OpenAPI
    document, so their absence is uniform and cannot itself be read as a signal. And the
    disclosure projection classifies the shape as `self`.

    None of it is evidence that any handler enforces ownership. It is evidence that no
    shape in this document offers a field that the privacy record refuses.
    """
    record = load_json(SCHEMAS / "appraisal-result-v1.schema.json")
    spec = load_yaml(SCHEMAS / "openapi-v1.yaml")
    api = spec["components"]["schemas"]

    if "appraisal_id" not in api["ClaimRecord"]["properties"]:
        raise ValidationFailure(
            "ClaimRecord no longer carries appraisal_id; this check exists because it "
            "did and nothing resolved it"
        )
    operations = {
        operation["operationId"]: operation
        for item in spec["paths"].values()
        for method, operation in item.items()
        if isinstance(operation, dict) and "operationId" in operation
    }
    if "getAppraisal" not in operations:
        raise ValidationFailure(
            "ClaimRecord.appraisal_id names an appraisal no operation retrieves"
        )
    operation = operations["getAppraisal"]
    returned = (
        operation["responses"]["200"]["content"]["application/json"]["schema"]
    ).get("$ref")
    if returned != "#/components/schemas/AppraisalSummary":
        raise ValidationFailure(
            f"getAppraisal answers with {returned}, not the AppraisalSummary "
            "projection; returning the stored record would publish the two fields "
            "D-381 and minimisation keep from the subject"
        )
    if operation.get("security") == [] or operation.get("x-authorization") != (
        "authenticated-account"
    ):
        raise ValidationFailure(
            "getAppraisal is not authenticated; an appraisal is integrity-private and "
            "has no public audience"
        )

    summary = api["AppraisalSummary"]
    record_properties = set(record["properties"])
    expected = (
        record_properties - APPRAISAL_RECORD_ONLY - set(APPRAISAL_RENAMED)
    ) | set(APPRAISAL_RENAMED.values())
    declared = set(summary["properties"])
    if declared != expected:
        raise ValidationFailure(
            "AppraisalSummary does not project the appraisal record: "
            f"only-in-api={sorted(declared - expected)} "
            f"only-in-record={sorted(expected - declared)}"
        )
    if set(summary["required"]) != expected:
        raise ValidationFailure(
            "AppraisalSummary declares an optional field; an appraisal field that may "
            "be absent is a per-response redaction, and a redaction that fails open "
            "publishes it"
        )

    for group, withheld in APPRAISAL_WITHHELD_FROM_SUBJECT.items():
        carried = set(record["properties"][group]["properties"])
        if withheld not in carried:
            raise ValidationFailure(
                f"the appraisal record no longer carries {group}.{withheld}, so the "
                "justification for withholding it has outlived the field; remove the "
                "entry rather than leaving a rule that guards nothing"
            )
        projected = set(summary["properties"][group]["properties"])
        if projected != carried - {withheld}:
            raise ValidationFailure(
                f"AppraisalSummary.{group} differs from the record minus {withheld}: "
                f"only-in-api={sorted(projected - (carried - {withheld}))} "
                f"only-in-record={sorted((carried - {withheld}) - projected)}"
            )

    for group in APPRAISAL_WHOLE_GROUPS:
        carried = set(record["properties"][group]["properties"])
        projected = set(summary["properties"][group]["properties"])
        if projected != carried:
            raise ValidationFailure(
                f"AppraisalSummary.{group} is not the whole record group: "
                f"only-in-api={sorted(projected - carried)} "
                f"only-in-record={sorted(carried - projected)}"
            )

    expected_enums: dict[str, frozenset] = {}
    for path, values in enum_map(record).items():
        head, _, tail = path.partition(".")
        if head in APPRAISAL_RECORD_ONLY:
            continue
        if tail and APPRAISAL_WITHHELD_FROM_SUBJECT.get(head) == tail:
            continue
        expected_enums[APPRAISAL_RENAMED.get(path, path)] = values
    projected_enums = enum_map(summary)
    if projected_enums != expected_enums:
        differing = sorted(
            path
            for path in set(projected_enums) | set(expected_enums)
            if projected_enums.get(path) != expected_enums.get(path)
        )
        raise ValidationFailure(
            "AppraisalSummary admits different values from the appraisal record at: "
            f"{differing}"
        )

    # The withheld names appear nowhere in the document, so no other shape reintroduces
    # them and their absence from this one carries no signal.
    def property_names(node: Any) -> set[str]:
        names: set[str] = set()
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "properties" and isinstance(value, dict):
                    names |= set(value)
                names |= property_names(value)
        elif isinstance(node, list):
            for item in node:
                names |= property_names(item)
        return names

    leaked = sorted(
        set(APPRAISAL_WITHHELD_FROM_SUBJECT.values()) & property_names(spec)
    )
    if leaked:
        raise ValidationFailure(
            f"the OpenAPI document declares withheld appraisal fields: {leaked}"
        )

    projections = {
        item["api_schema"]: item
        for item in load_json(SCHEMAS / "disclosure-projection-v1.json")["projections"]
    }
    if "AppraisalSummary" not in projections:
        raise ValidationFailure(
            "the disclosure projection does not classify AppraisalSummary, so the "
            "audience of an integrity-private shape is unrecorded"
        )
    if projections["AppraisalSummary"]["audience"] != "self":
        raise ValidationFailure(
            "AppraisalSummary is projected to "
            f"{projections['AppraisalSummary']['audience']}; an appraisal has no "
            "audience but its own subject"
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
            "OTel accounting profile and capture-surface hazards",
            validate_otel_accounting_profile,
        ),
        (
            "observer equivalence and deduplication vectors",
            validate_observer_equivalence,
        ),
        (
            "source receipt, appraisal policy and appraisal result",
            validate_evidence_chain,
        ),
        (
            "appraisal retrieval and subject disclosure",
            validate_appraisal_disclosure,
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
        (
            "notification model and per-device deletion contracts",
            validate_notification_and_local_deletion_contracts,
        ),
        (
            "disclosure projections and exceptional surface states",
            validate_presentation_contracts,
        ),
        ("origin validation and loopback controls", validate_origin_policy),
        ("conformance suite manifests", validate_conformance_manifests),
        ("decision register table integrity", validate_decision_register),
        ("inventory table integrity", validate_inventory_register),
        ("CDDL grammar parse and required rules", validate_cddl_file),
        ("VibeProof exact-byte and malformed vectors", validate_vibeproof_vectors),
        ("VibeProof vector reproducibility", validate_vector_reproducibility),
        ("planning document generation", validate_planning_doc_generation),
        ("decision traceability coverage", validate_decision_traceability),
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
