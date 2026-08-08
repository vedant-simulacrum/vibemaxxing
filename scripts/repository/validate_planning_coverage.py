#!/usr/bin/env python3
"""Validate repaired P-1140D planning coverage and launch scope.

This proves declared structural coverage only. It is not evidence that any
covered surface is implemented, correct, or launch-ready.
"""
from __future__ import annotations

import json
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

# Mutating operations that carry no `Idempotency-Key`, because the credential the request
# already presents is itself single-use and a durable request hash would be a second,
# weaker replay control layered over a stronger one. `/auth/session/refresh` joins the set
# under D-221: ADR-015 makes every refresh handle one-time-use with no grace window, so a
# repeated refresh is a replay incident rather than a retry.
IDEMPOTENCY_EXCEPTIONS = {
    ("/auth/github/start", "post"), ("/auth/x/start", "post"),
    ("/auth/device/start", "post"), ("/auth/device/poll", "post"),
    ("/auth/device/exchange", "post"), ("/auth/session/refresh", "post"),
    ("/claim-challenges", "post"),
}

REPAIR_TARGETS = {
    "VerifierAppraisal": ("packages/schemas/vibeproof-claim-v1.cddl", "verifier-appraisal-v1"),
    "CheckpointReceipt": ("packages/schemas/vibeproof-claim-v1.cddl", "checkpoint-receipt-v1"),
    "refresh-token families": ("packages/schemas/state-machine-registry-v1.json", "web-session-family"),
    "durable idempotency ownership": ("packages/schemas/planning-schema.sql", "idempotency_records"),
    "immutable ranking view identity": ("packages/schemas/ranking-view-v1.schema.json", "ranking_view_id"),
    "exact platform support profiles": ("packages/schemas/platform-profile-registry-v1.json", "profile_id"),
    "mandatory automatic updates": ("packages/schemas/release-set-v1.schema.json", "mandatory_after"),
}


# The eight local roles. `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md` names the
# product's processes in prose and PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md tabulated six
# of them, omitting the interactive shell and the privileged supervisor — the only
# role that takes arbitrary operator input and the only one that runs elevated. A role
# with no declared capability is one nothing can refuse.
LOCAL_TRUST_ROLES = (
    "vibemaxxing-daemon",
    "vibeproof-collector",
    "vibeproof-sync",
    "vibemaxxing-cli",
    "vibemaxxing-desktop-shell",
    "vibemaxxing-shell",
    "updater-helper",
    "privileged-supervisor",
)

# The separation the product's privacy claim rests on. AGENTS.md forbids transcript
# content crossing the device boundary; that holds only if no single process can both
# read content and reach the network. Each role declares `network` explicitly, because
# the first version of this check inferred it from the prose capability list and
# "read allowlisted adapter sources" matched on the word allowlist — a source allowlist
# read as a network one, failing the committed state. A capability the privacy boundary
# depends on is not something to substring-match.
CONTENT_CLASS = "transcript-content"
NO_NETWORK = "none"


def check_local_trust_domains(errors: list[str]) -> None:
    profile = json.loads(
        (SCHEMAS / "local-trust-domains-v1.json").read_text(encoding="utf-8")
    )
    roles = {role["role_id"]: role for role in profile["roles"]}

    for role_id in LOCAL_TRUST_ROLES:
        if role_id not in roles:
            errors.append(
                f"local trust domain missing for {role_id}: it holds capabilities no "
                "file declares, so nothing can refuse them"
            )
    for role_id in sorted(set(roles) - set(LOCAL_TRUST_ROLES)):
        errors.append(
            f"local trust domain declares {role_id}, which is not a named local role"
        )
    if len(roles) != len(profile["roles"]):
        errors.append("a local role is declared more than once")

    declared = set(profile["data_classes"])
    for role_id, role in sorted(roles.items()):
        for data_class in role["may_read"] + role["may_write"]:
            if data_class not in declared:
                errors.append(
                    f"{role_id} names data class {data_class!r}, which "
                    "local-trust-domains-v1.json does not define"
                )
        reads_content = CONTENT_CLASS in role["may_read"]
        if reads_content and role["network"] != NO_NETWORK:
            errors.append(
                f"{role_id} may read {CONTENT_CLASS} and holds a network capability. "
                "The privacy boundary is the separation of those two, not a promise "
                "about what the process chooses to send"
            )

    readers = [r for r, role in roles.items() if CONTENT_CLASS in role["may_read"]]
    if readers != ["vibeproof-collector"]:
        errors.append(
            f"{CONTENT_CLASS} is readable by {readers}; exactly one role may read it "
            "and it is the collector, which has no network capability at all"
        )


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
        errors.append(f"post-launch country paths remain in the launch API contract: {forbidden_paths}")

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
        errors.append(f"post-launch country tables remain in the launch SQL contract: {forbidden_tables}")
    if re.search(r"board_type\s+in\s*\([^)]*'country'", sql, flags=re.IGNORECASE | re.DOTALL):
        errors.append("country remains an allowed launch board_type")
    if "P-1140D REPAIRED PLANNING MIGRATION CONTRACT" not in sql:
        errors.append("PostgreSQL contract lacks repaired P-1140D marker")
    if re.search(r"(?i)\bjsonb\b", sql):
        errors.append("untyped jsonb remains in the repaired SQL contract")
    if "board_one_active_owner" not in sql or "check (account_id_a < account_id_b)" not in sql:
        errors.append("repaired social SQL lacks canonical pair or single-owner constraints")

    check_local_trust_domains(errors)

    for label, (relative_path, marker) in REPAIR_TARGETS.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        if marker.lower() not in text.lower():
            errors.append(f"missing P-1140 repair target for {label}: {relative_path} lacks {marker!r}")

    fail(errors)
    print(
        "planning coverage: PASS "
        f"({len(REQUIRED_PATHS)} current API paths, {len(REQUIRED_TABLES)} current tables, "
        f"{len(REPAIR_TARGETS)} repaired authority targets, "
        f"{len(LOCAL_TRUST_ROLES)} local trust domains)"
    )
    print("artifact maturity: repaired P-1140D planning contract; declared coverage only, not implementation evidence")


if __name__ == "__main__":
    main()
