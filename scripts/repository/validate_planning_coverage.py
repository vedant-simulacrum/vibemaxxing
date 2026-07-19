#!/usr/bin/env python3
"""Validate planning coverage beyond parser-level correctness."""
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
    "/boards", "/boards/{id}/invitations", "/organizations", "/communities", "/countries",
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
    "board_memberships", "board_invites", "country_assertions", "presence_leases", "notifications",
    "notification_preferences", "outbox_events", "worker_checkpoints", "audit_events", "exports",
    "deletion_jobs", "feature_flags", "schema_migrations",
}

IDEMPOTENCY_EXCEPTIONS = {
    ("/auth/github/start", "post"), ("/auth/x/start", "post"),
    ("/auth/device/start", "post"), ("/auth/device/poll", "post"),
    ("/auth/device/exchange", "post"), ("/claim-challenges", "post"),
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
        errors.append(f"missing API paths: {missing_paths}")

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
        errors.append(f"missing PostgreSQL tables: {missing_tables}")

    fail(errors)
    print(f"planning coverage: PASS ({len(REQUIRED_PATHS)} API paths, {len(REQUIRED_TABLES)} tables)")


if __name__ == "__main__":
    main()
