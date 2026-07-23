#!/usr/bin/env python3
"""Validate current planning-placeholder coverage and repaired launch scope.

This is structural planning validation only. It deliberately does not claim that the
blocked OpenAPI or PostgreSQL placeholders are implementation-ready.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"

REQUIRED_PATHS = {
    "/auth/github/start", "/auth/github/callback", "/auth/x/start", "/auth/x/callback",
    "/auth/device/start", "/auth/device/poll", "/auth/device/exchange",
    "/sessions", "/sessions/{id}/revoke", "/identities", "/identities/link", "/identities/unlink",
    "/devices", "/devices/enroll", "/devices/{id}/rotate", "/devices/{id}/revoke",
    "/claim-challenges", "/claim-batches", "/claims/{id}",
    "/leaderboards/{scope}/{period}", "/rank/me", "/profiles/{handle}", "/me",
    "/friends", "/friend-requests", "/blocks", "/rivals",
    "/boards", "/boards/{id}/invitations", "/organizations", "/communities",
    "/presence", "/notifications", "/moderation/cases", "/appeals",
    "/exports", "/deletion-requests", "/pricing-datasets", "/compatibility",
}

REQUIRED_TABLES = {
    "accounts", "account_handles", "linked_identities", "web_sessions", "recovery_codes",
    "optional_authenticators", "oauth_transactions", "devices", "device_keys",
    "device_enrollment_grants", "adapter_installations", "claim_challenges", "device_sequences",
    "claims", "claim_payloads", "claim_rejections", "claim_corrections", "quarantines",
    "evidence_assessments", "moderation_cases", "moderation_actions", "appeals", "periods",
    "minute_scores", "period_scores", "score_snapshots", "ranking_corrections",
    "pricing_datasets", "pricing_entries", "cost_interpretations", "profiles", "friend_requests",
    "friend_edges", "blocks", "rival_edges", "organizations", "communities", "boards",
    "board_memberships", "board_invites", "presence_leases", "notifications",
    "notification_preferences", "outbox_events", "worker_checkpoints", "audit_events", "exports",
    "deletion_jobs", "feature_flags", "schema_migrations",
}

FORBIDDEN_LAUNCH_PATHS = {"/countries"}
FORBIDDEN_LAUNCH_TABLES = {"country_assertions"}

IDEMPOTENCY_EXCEPTIONS = {
    ("/auth/github/start", "post"), ("/auth/x/start", "post"),
    ("/auth/device/start", "post"), ("/auth/device/poll", "post"),
    ("/auth/device/exchange", "post"), ("/claim-challenges", "post"),
}

REPAIR_TARGETS = {
    "VerifierAppraisal": ("docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md", "VerifierAppraisal"),
    "CheckpointReceipt": ("docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md", "CheckpointReceipt"),
    "refresh-token families": ("docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md", "refresh-token family"),
    "durable idempotency ownership": ("docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md", "idempotency uniqueness"),
    "immutable ranking view identity": ("docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md", "ranking_view_id"),
    "exact platform support profiles": ("docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md", "support profile"),
    "mandatory automatic updates": ("docs/decisions/ADR-013-MANDATORY_AUTOMATIC_UPDATES.md", "mandatory automatic updates"),
}


def fail(messages: list[str]) -> None:
    if messages:
        print("planning coverage: FAIL", file=sys.stderr)
        for message in messages:
            print(f"- {message}", file=sys.stderr)
        raise SystemExit(1)


def main() -> None:
    errors: list[str] = []
    spec = yaml.safe_load((SCHEMAS / "openapi-v1.yaml").read_text(encoding="utf-8"))
    paths = spec.get("paths", {})

    missing_paths = sorted(REQUIRED_PATHS - set(paths))
    if missing_paths:
        errors.append(f"missing current planning API paths: {missing_paths}")
    forbidden_paths = sorted(FORBIDDEN_LAUNCH_PATHS & set(paths))
    if forbidden_paths:
        errors.append(f"post-launch country paths remain in the launch API placeholder: {forbidden_paths}")

    operation_ids: list[str] = []
    for path, item in paths.items():
        for method, operation in item.items():
            method = method.lower()
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            operation_id = operation.get("operationId")
            if not operation_id:
                errors.append(f"missing operationId: {method.upper()} {path}")
            else:
                operation_ids.append(operation_id)
            if not operation.get("responses"):
                errors.append(f"missing responses: {method.upper()} {path}")
            if method in {"post", "put", "patch", "delete"} and (path, method) not in IDEMPOTENCY_EXCEPTIONS:
                refs = [parameter.get("$ref") for parameter in operation.get("parameters", []) if isinstance(parameter, dict)]
                if "#/components/parameters/IdempotencyKey" not in refs:
                    errors.append(f"mutating operation lacks Idempotency-Key: {method.upper()} {path}")
    if len(operation_ids) != len(set(operation_ids)):
        errors.append("duplicate OpenAPI operationId")

    sql = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
    tables = set(re.findall(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(", sql))
    missing_tables = sorted(REQUIRED_TABLES - tables)
    if missing_tables:
        errors.append(f"missing current planning PostgreSQL tables: {missing_tables}")
    forbidden_tables = sorted(FORBIDDEN_LAUNCH_TABLES & tables)
    if forbidden_tables:
        errors.append(f"post-launch country tables remain in the launch SQL placeholder: {forbidden_tables}")
    if re.search(r"board_type\s+in\s*\([^)]*'country'", sql, flags=re.IGNORECASE | re.DOTALL):
        errors.append("country remains an allowed launch board_type")

    for label, (relative_path, marker) in REPAIR_TARGETS.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        if marker.lower() not in text.lower():
            errors.append(f"missing P-1140 repair target for {label}: {relative_path} lacks {marker!r}")

    fail(errors)
    print(
        "planning coverage: PASS "
        f"({len(REQUIRED_PATHS)} current API paths, {len(REQUIRED_TABLES)} current tables, "
        f"{len(REPAIR_TARGETS)} deferred repair targets)"
    )
    print("artifact maturity: blocked planning placeholders; not implementation evidence")


if __name__ == "__main__":
    main()
