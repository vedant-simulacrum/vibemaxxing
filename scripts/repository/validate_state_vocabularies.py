#!/usr/bin/env python3
"""Assert that every aggregate state vocabulary is identical across its three owners.

The three owners are:

* `packages/schemas/state-machine-registry-v1.json` — the lifecycle authority;
* `packages/schemas/planning-schema.sql` — the persistence authority;
* `packages/schemas/openapi-v1.yaml` — the client-visible projection, read as YAML.

`docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` records the binding
table in prose; this script holds the same table as data and refuses to run if the two
disagree, so the document cannot drift away from the schemas it governs.

This proves structural vocabulary agreement only. It does not claim that any
transition, worker, or migration exists.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
REGISTRY_PATH = SCHEMAS / "state-machine-registry-v1.json"
SQL_PATH = SCHEMAS / "planning-schema.sql"
OPENAPI_PATH = SCHEMAS / "openapi-v1.yaml"
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md"
)

# P-1140F naming rule: every state value in every owner is lowercase kebab-case.
STATE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

NONE_MARKER = "—"


@dataclass(frozen=True)
class Binding:
    """One aggregate whose state vocabulary must agree across its declared owners."""

    aggregate: str
    states: tuple[str, ...]
    machine: str | None = None
    sql: tuple[str, ...] = ()
    api: tuple[str, ...] = ()
    internal_states: tuple[str, ...] = ()
    shared_sql: bool = False
    note: str = ""


# ---------------------------------------------------------------------------
# Binding table. Mirrored in AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md.
# ---------------------------------------------------------------------------

BINDINGS: tuple[Binding, ...] = (
    Binding(
        aggregate="oauth-transaction",
        machine="oauth-transaction",
        states=(
            "created",
            "redirected",
            "callback-received",
            "consumed",
            "expired",
            "failed",
        ),
        sql=("oauth_transactions.state",),
        note="OAuthCompletion.state echoes the terminal value only; see TRANSIENT_API_ENUMS.",
    ),
    Binding(
        aggregate="web-session-family",
        machine="web-session-family",
        states=("active", "rotating", "replay-detected", "revoked", "expired"),
        sql=("session_families.state",),
        shared_sql=True,
        note="session_families holds both family machines; the CHECK is their union.",
    ),
    Binding(
        aggregate="native-session-family",
        machine="native-session-family",
        states=(
            "active",
            "rotating",
            "replay-detected",
            "device-revoked",
            "revoked",
            "expired",
        ),
        sql=("session_families.state",),
        shared_sql=True,
    ),
    Binding(
        aggregate="session-member",
        states=("active", "rotated", "revoked", "expired"),
        sql=("web_sessions.state", "native_sessions.state"),
        api=("Session.state",),
        note="Member rows of a token family; no machine of their own.",
    ),
    Binding(
        aggregate="ranked-identity-eligibility",
        machine="ranked-identity-eligibility",
        states=(
            "unverified",
            "eligible",
            "investigating",
            "restricted",
            "consolidating",
            "appealed",
            "reversed",
            "retired",
        ),
        api=("PublicProfile.ranked_state", "AccountProfile.ranked_state"),
        internal_states=("investigating", "consolidating", "appealed", "reversed"),
        note="No ranked_identities table exists in the planning migration yet.",
    ),
    Binding(
        aggregate="idempotency-ledger",
        machine="idempotency-ledger",
        states=("reserved", "committed", "conflict", "expired", "failed"),
        sql=("idempotency_records.state",),
    ),
    Binding(
        aggregate="ranking-projection",
        machine="ranking-projection",
        states=("building", "validating", "active", "superseded", "failed"),
        sql=("ranking_projection_generations.state",),
    ),
    Binding(
        aggregate="model-alias-resolution",
        machine="model-alias-resolution",
        states=("active", "superseded", "revoked"),
        sql=("pricing_datasets.state", "cost_interpretations.state"),
        api=("PricingDataset.state",),
        note="model_alias_facts keeps a derived state from effective_at/superseded_at.",
    ),
    Binding(
        aggregate="friendship",
        machine="friendship",
        states=(
            "none",
            "pending-a-to-b",
            "pending-b-to-a",
            "active",
            "blocked",
            "ended",
        ),
        sql=("friend_requests.state",),
    ),
    Binding(
        aggregate="rivalry",
        machine="rivalry",
        states=("none", "active", "ended", "blocked"),
        sql=("rival_edges.state",),
    ),
    Binding(
        aggregate="board-membership",
        machine="board-membership",
        states=(
            "invited",
            "active-viewer",
            "active-member",
            "active-admin",
            "active-owner",
            "left",
            "removed",
            "blocked",
        ),
        sql=("board_memberships.state",),
    ),
    Binding(
        aggregate="board-invitation",
        machine="board-invitation",
        states=(
            "pending",
            "accepted",
            "declined",
            "expired",
            "revoked",
            "invalidated-by-block",
        ),
        sql=("board_invites.state",),
    ),
    Binding(
        aggregate="board-container",
        states=("active", "archived"),
        sql=("boards.state", "organizations.state", "communities.state"),
        api=("Board.state", "Organization.state", "Community.state"),
        note="Archive flag on a container; mutable board concepts have their own machines.",
    ),
    Binding(
        aggregate="presence-lease",
        machine="presence-lease",
        states=("absent", "active", "idle", "expired", "revoked"),
        sql=("presence_leases.state",),
        note="PresenceLease.availability is a declared projection; see PROJECTIONS.",
    ),
    Binding(
        aggregate="notification-delivery",
        machine="notification-delivery",
        states=(
            "created",
            "grouped",
            "suppressed",
            "ready",
            "delivered",
            "read",
            "retracted",
            "expired",
        ),
        sql=("notifications.state",),
        api=("Notification.state",),
        internal_states=("grouped", "ready"),
    ),
    Binding(
        aggregate="moderation-case",
        machine="moderation-case",
        states=(
            "open",
            "investigating",
            "actioned",
            "awaiting-appeal",
            "reversed",
            "closed",
        ),
        sql=("moderation_cases.state",),
        api=("ModerationCase.state",),
    ),
    Binding(
        aggregate="appeal",
        machine="appeal",
        states=(
            "submitted",
            "screening",
            "reviewing",
            "approved",
            "denied",
            "withdrawn",
            "needs-information",
            "expired",
        ),
        sql=("appeals.state",),
        api=("Appeal.state",),
        internal_states=("screening",),
    ),
    Binding(
        aggregate="export-job",
        machine="export-job",
        states=(
            "requested",
            "snapshotting",
            "encrypting",
            "ready",
            "downloaded",
            "purged",
            "failed",
        ),
        sql=("exports.state",),
        api=("ExportJob.state",),
    ),
    Binding(
        aggregate="server-deletion",
        machine="server-deletion",
        states=(
            "requested",
            "recent-auth-verified",
            "processing",
            "rebuilding-projections",
            "complete",
            "failed",
            "cooling-off",
            "awaiting-local-receipt",
        ),
        sql=("deletion_jobs.state",),
        api=("DeletionJob.state",),
        internal_states=("rebuilding-projections",),
    ),
    Binding(
        aggregate="local-deletion-command",
        machine="local-deletion-command",
        states=("issued", "acknowledged", "executing", "complete", "expired", "failed"),
        sql=("local_deletion_commands.state",),
    ),
    Binding(
        aggregate="daemon-lifecycle",
        machine="daemon-lifecycle",
        states=(
            "unregistered",
            "registered",
            "starting",
            "healthy",
            "paused",
            "offline",
            "degraded",
            "recovery",
            "stopping",
            "stopped",
            "uninstalled",
        ),
        note="Local-only; never persisted server-side and never exposed by the API.",
    ),
    Binding(
        aggregate="privileged-supervisor",
        machine="privileged-supervisor",
        states=(
            "absent",
            "consent-pending",
            "installing",
            "active",
            "degraded",
            "removing",
            "removed",
        ),
        note="Local-only; never persisted server-side and never exposed by the API.",
    ),
    Binding(
        aggregate="interactive-shell",
        machine="interactive-shell",
        states=(
            "absent",
            "headless",
            "starting",
            "connected",
            "daemon-unavailable",
            "stale",
            "paused",
            "offline",
            "degraded",
            "auth-required",
            "update-required",
            "update-blocked",
            "permission-repair",
            "exiting",
            "crashed",
        ),
        note="Local-only; never persisted server-side and never exposed by the API.",
    ),
    Binding(
        aggregate="update-lifecycle",
        machine="update-lifecycle",
        states=(
            "current",
            "available",
            "deferred",
            "deadline",
            "downloading",
            "staged",
            "installing",
            "health-check",
            "rolled-back",
            "complete",
            "blocked-version",
            "failed",
        ),
        sql=("update_installations.state",),
    ),
    Binding(
        aggregate="release-trust",
        machine="release-trust",
        states=(
            "draft",
            "threshold-signed",
            "published",
            "active",
            "superseded",
            "revoked",
            "expired",
        ),
        sql=("release_sets.state",),
    ),
    Binding(
        aggregate="platform-certification",
        machine="platform-certification",
        states=(
            "planned",
            "candidate",
            "exercised",
            "published",
            "degraded",
            "suspended",
            "retired",
            "certified",
            "blocked",
        ),
        sql=("platform_profiles.validation_state",),
        api=("CompatibilityProfile.validation_state",),
    ),
    Binding(
        aggregate="account-lifecycle",
        machine="account-lifecycle",
        states=("active", "restricted", "deletion-pending", "deleted"),
        sql=("accounts.state",),
        note="Cancelling a deletion requested while restricted returns the row to active; "
        "see the open items in the contract document.",
    ),
    Binding(
        aggregate="device-enrollment",
        machine="device-enrollment",
        states=("pending", "active", "quarantined", "revoked", "deleted"),
        sql=("devices.state",),
        api=("Device.state",),
        note="Revocation cascades to native-session-family via device-revoked.",
    ),
    Binding(
        aggregate="device-authorization-grant",
        states=("pending", "approved", "denied", "expired", "consumed"),
        sql=("device_enrollment_grants.state",),
        api=("DeviceAuthorizationStatus.state",),
    ),
    Binding(
        aggregate="identity-link",
        states=("linked", "unlink-pending", "unlinked"),
        sql=("linked_identities.state",),
        api=("Identity.state",),
    ),
    Binding(
        aggregate="claim-record",
        states=("accepted", "corrected", "retracted", "quarantined"),
        api=("ClaimRecord.state",),
        note="Claims are append-only facts; the state is derived, never a stored column.",
    ),
)

# SQL-only vocabularies that belong to a sub-entity rather than to an aggregate whose
# lifecycle a machine owns. Declared so the completeness scan below stays fail-closed.
SQL_LOCAL_VOCABULARIES: dict[str, tuple[str, ...]] = {
    "device_keys.state": ("active", "rotated", "revoked"),
    "quarantines.state": ("active", "released"),
    "deletion_effects.state": (
        "pending",
        "executing",
        "complete",
        "failed",
        "not-applicable",
    ),
    "platform_certifications.state": (
        "candidate",
        "exercised",
        "certified",
        "failed",
        "revoked",
    ),
    "appeal_decisions.decision": ("upheld", "partially-upheld", "reversed"),
    "evidence_assessments.public_state": (
        "hardened",
        "standard",
        "imported",
        "private-analytics",
    ),
    "evidence_assessments.provenance_state": (
        "verified",
        "partial",
        "unverified",
        "rejected",
    ),
    "evidence_assessments.continuity_state": ("continuous", "gap-declared", "broken"),
    "evidence_assessments.integrity_state": ("verified", "degraded", "failed"),
    "verifier_appraisals.provenance_state": (
        "verified",
        "partial",
        "unverified",
        "rejected",
    ),
    "verifier_appraisals.continuity_state": ("continuous", "gap-declared", "broken"),
    "verifier_appraisals.integrity_state": ("verified", "degraded", "failed"),
    "device_sequences.continuity_state": (
        "continuous",
        "gap-declared",
        "broken",
        "revoked",
    ),
    "device_lineages.continuity_state": (
        "continuous",
        "gap-declared",
        "broken",
        "revoked",
    ),
}

# Sub-entity outcome vocabularies that are also published on the API. Key is the
# SQL_LOCAL_VOCABULARIES entry that owns the vocabulary; value is the API enum that mirrors it.
OUTCOME_MIRRORS: dict[str, str] = {
    "appeal_decisions.decision": "Appeal.decision",
}

# API enums that report the outcome of a single request rather than a stored aggregate state.
TRANSIENT_API_ENUMS: dict[str, tuple[tuple[str, ...], str | None]] = {
    "ClaimBatchResult.state": (("accepted", "rejected"), None),
    "OAuthCompletion.state": (("consumed",), "oauth-transaction"),
}

# Client-facing fields that deliberately collapse a machine into a coarser vocabulary.
PROJECTIONS: tuple[tuple[str, tuple[str, ...], dict[str, str]], ...] = (
    (
        "presence-lease",
        ("PresenceLease.availability", "PresenceRenewalRequest.availability"),
        {
            "absent": "offline",
            "active": "online",
            "idle": "idle",
            "expired": "offline",
            "revoked": "offline",
        },
    ),
)


class Failure(RuntimeError):
    pass


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_CREATE_TABLE = re.compile(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(")
_CHECK_IN = re.compile(
    r"check\s*\(\s*([a-z_][a-z0-9_]*)\s+in\s*\(([^)]*)\)\s*\)", re.IGNORECASE
)
_LITERAL = re.compile(r"'([^']*)'")
_COLUMN = re.compile(
    r"^\s*([a-z_][a-z0-9_]*)\s+(text|uuid|bytea|boolean|smallint|bigint|numeric|timestamptz)\b"
)


def table_bodies(sql: str) -> dict[str, str]:
    """Return the parenthesised body of every `create table` statement."""
    bodies: dict[str, str] = {}
    for match in _CREATE_TABLE.finditer(sql):
        name = match.group(1)
        depth = 1
        index = match.end()
        while index < len(sql) and depth:
            character = sql[index]
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            index += 1
        if depth:
            raise Failure(f"unterminated create table statement: {name}")
        if name in bodies:
            raise Failure(f"duplicate create table statement: {name}")
        bodies[name] = sql[match.end() : index - 1]
    return bodies


def sql_check_sets(bodies: dict[str, str]) -> dict[str, set[str]]:
    """Map `table.column` to the literal set of its `check (column in (...))` constraint."""
    result: dict[str, set[str]] = {}
    for table, body in bodies.items():
        for match in _CHECK_IN.finditer(body):
            column = match.group(1)
            values = set(_LITERAL.findall(match.group(2)))
            key = f"{table}.{column}"
            if key in result:
                raise Failure(f"duplicate CHECK vocabulary for {key}")
            result[key] = values
    return result


def sql_state_columns(bodies: dict[str, str]) -> set[str]:
    """Every `table.column` whose name is `state` or ends in `_state`."""
    columns: set[str] = set()
    for table, body in bodies.items():
        for line in body.splitlines():
            match = _COLUMN.match(line)
            if not match:
                continue
            column = match.group(1)
            if column == "state" or column.endswith("_state"):
                columns.add(f"{table}.{column}")
    return columns


def api_enums(spec: dict) -> dict[str, list[str]]:
    """Every `Schema.property` with an enum, keyed for the binding table."""
    result: dict[str, list[str]] = {}
    for name, schema in spec["components"]["schemas"].items():
        for prop, node in (schema.get("properties") or {}).items():
            if isinstance(node, dict) and isinstance(node.get("enum"), list):
                result[f"{name}.{prop}"] = node["enum"]
    return result


def api_state_enums(enums: dict[str, list[str]]) -> set[str]:
    """API enums whose property name is `state` or ends in `_state`."""
    selected = set()
    for key in enums:
        prop = key.split(".", 1)[1]
        if prop == "state" or prop.endswith("_state"):
            selected.add(key)
    return selected


def contract_table(text: str) -> dict[str, dict[str, tuple[str, ...]]]:
    """Parse the binding table out of the authoritative contract document."""
    rows: dict[str, dict[str, tuple[str, ...]]] = {}
    inside = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Aggregate | Registry machine |"):
            inside = True
            continue
        if inside:
            if not stripped.startswith("|"):
                break
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) != 5 or set(cells[0]) <= {"-", ":"}:
                continue

            def parse(cell: str) -> tuple[str, ...]:
                if cell == NONE_MARKER:
                    return ()
                return tuple(
                    sorted(
                        item.strip().strip("`")
                        for item in cell.split(",")
                        if item.strip()
                    )
                )

            aggregate = cells[0].strip("`")
            rows[aggregate] = {
                "machine": parse(cells[1]),
                "sql": parse(cells[2]),
                "api": parse(cells[3]),
                "internal": parse(cells[4]),
            }
    if not inside:
        raise Failure("contract document contains no state vocabulary binding table")
    return rows


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def validate(report: Report) -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    machines = {machine["machine_id"]: machine for machine in registry["machines"]}
    sql_text = SQL_PATH.read_text(encoding="utf-8")
    bodies = table_bodies(sql_text)
    checks = sql_check_sets(bodies)
    declared_state_columns = sql_state_columns(bodies)
    spec = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    enums = api_enums(spec)
    contract = contract_table(CONTRACT_PATH.read_text(encoding="utf-8"))

    aggregates = [binding.aggregate for binding in BINDINGS]
    report.check(
        len(aggregates) == len(set(aggregates)),
        "duplicate aggregate id in the binding table",
    )

    # 1. Naming rule.
    for machine_id, machine in machines.items():
        for state in machine["states"]:
            report.check(
                bool(STATE_NAME_PATTERN.fullmatch(state)),
                f"registry state is not lowercase kebab-case: {machine_id}.{state}",
            )
    governed_columns = (
        declared_state_columns
        | set(SQL_LOCAL_VOCABULARIES)
        | {column for binding in BINDINGS for column in binding.sql}
    )
    for key in sorted(governed_columns & set(checks)):
        for value in sorted(checks[key]):
            report.check(
                bool(STATE_NAME_PATTERN.fullmatch(value)),
                f"SQL CHECK literal is not lowercase kebab-case: {key} = {value!r}",
            )
    for key in api_state_enums(enums) | set(TRANSIENT_API_ENUMS):
        for value in enums.get(key, []):
            report.check(
                bool(STATE_NAME_PATTERN.fullmatch(value)),
                f"API enum value is not lowercase kebab-case: {key} = {value!r}",
            )

    # 2. Every registry machine is bound exactly once.
    bound_machines = [binding.machine for binding in BINDINGS if binding.machine]
    report.check(
        len(bound_machines) == len(set(bound_machines)),
        "a registry machine is bound by more than one aggregate",
    )
    missing_machines = sorted(set(machines) - set(bound_machines))
    report.check(
        not missing_machines,
        f"registry machines absent from the binding table: {missing_machines}",
    )
    unknown_machines = sorted(set(bound_machines) - set(machines))
    report.check(
        not unknown_machines,
        f"binding table references unknown machines: {unknown_machines}",
    )

    shared_columns: dict[str, set[str]] = {}
    used_sql: set[str] = set()
    used_api: set[str] = set()

    for binding in BINDINGS:
        states = set(binding.states)
        report.check(
            len(states) == len(binding.states),
            f"{binding.aggregate}: duplicate declared state",
        )

        # 3. Registry agrees with the declared vocabulary.
        if binding.machine:
            machine = machines[binding.machine]
            registry_states = set(machine["states"])
            report.check(
                registry_states == states,
                f"{binding.aggregate}: registry states differ from the declared vocabulary: "
                f"only-in-registry={sorted(registry_states - states)} "
                f"only-in-binding={sorted(states - registry_states)}",
            )
            report.check(
                machine["initial_state"] in registry_states,
                f"{binding.aggregate}: initial state is not a declared state",
            )
            report.check(
                set(machine["terminal_states"]) <= registry_states,
                f"{binding.aggregate}: terminal states are not a subset of declared states",
            )

        # 4. Internal states are real states and are the only API omissions.
        internal = set(binding.internal_states)
        report.check(
            internal <= states,
            f"{binding.aggregate}: internal states are not a subset of declared states: "
            f"{sorted(internal - states)}",
        )
        visible = states - internal
        report.check(
            bool(visible) or not binding.api,
            f"{binding.aggregate}: every state is internal but an API enum is declared",
        )

        # 5. Persistence agrees exactly.
        for column in binding.sql:
            used_sql.add(column)
            report.check(
                column in declared_state_columns or column in checks,
                f"{binding.aggregate}: SQL column does not exist: {column}",
            )
            if column not in checks:
                report.check(
                    False,
                    f"{binding.aggregate}: SQL column has no CHECK vocabulary: {column}",
                )
                continue
            actual = checks[column]
            if binding.shared_sql:
                shared_columns.setdefault(column, set()).update(states)
                report.check(
                    states <= actual,
                    f"{binding.aggregate}: shared SQL column {column} cannot hold "
                    f"{sorted(states - actual)}",
                )
            else:
                report.check(
                    actual == states,
                    f"{binding.aggregate}: SQL CHECK on {column} differs: "
                    f"only-in-sql={sorted(actual - states)} only-in-binding={sorted(states - actual)}",
                )

        # 6. The API projection agrees exactly with the non-internal states.
        for reference in binding.api:
            used_api.add(reference)
            if reference not in enums:
                report.check(
                    False, f"{binding.aggregate}: API enum does not exist: {reference}"
                )
                continue
            actual = set(enums[reference])
            report.check(
                actual == visible,
                f"{binding.aggregate}: API enum {reference} differs: "
                f"only-in-api={sorted(actual - visible)} only-in-binding={sorted(visible - actual)}",
            )

    # 7. Shared SQL columns hold exactly the union of the machines that share them.
    for column, union in shared_columns.items():
        actual = checks.get(column, set())
        report.check(
            actual == union,
            f"shared SQL column {column} is not the union of its machines: "
            f"only-in-sql={sorted(actual - union)} only-in-machines={sorted(union - actual)}",
        )

    # 8. Every SQL state column is either bound or an explicitly declared sub-entity vocabulary.
    for column in sorted(declared_state_columns | set(SQL_LOCAL_VOCABULARIES)):
        if column in used_sql:
            continue
        if column not in SQL_LOCAL_VOCABULARIES:
            report.check(
                False,
                f"SQL state column is bound to no aggregate and declares no local vocabulary: {column}",
            )
            continue
        expected = set(SQL_LOCAL_VOCABULARIES[column])
        actual = checks.get(column)
        if actual is None:
            report.check(
                False,
                f"declared sub-entity vocabulary has no CHECK constraint: {column}",
            )
            continue
        report.check(
            actual == expected,
            f"sub-entity vocabulary {column} differs: only-in-sql={sorted(actual - expected)} "
            f"only-in-declaration={sorted(expected - actual)}",
        )

    # 9. Published outcome vocabularies agree with the SQL declaration that owns them.
    for column, reference in sorted(OUTCOME_MIRRORS.items()):
        expected = set(SQL_LOCAL_VOCABULARIES.get(column, ()))
        if not expected:
            report.check(
                False,
                f"outcome mirror names an undeclared sub-entity vocabulary: {column}",
            )
            continue
        if reference not in enums:
            report.check(False, f"outcome API enum does not exist: {reference}")
            continue
        actual = set(enums[reference])
        report.check(
            actual == expected,
            f"outcome enum {reference} differs from {column}: "
            f"only-in-api={sorted(actual - expected)} only-in-sql={sorted(expected - actual)}",
        )
        for value in sorted(actual):
            report.check(
                bool(STATE_NAME_PATTERN.fullmatch(value)),
                f"outcome enum value is not lowercase kebab-case: {reference} = {value!r}",
            )

    # 10. Every API state enum is bound, transient, or a declared projection.
    projection_refs = {
        reference for _, references, _ in PROJECTIONS for reference in references
    }
    for reference in sorted(api_state_enums(enums)):
        if reference in used_api or reference in projection_refs:
            continue
        if reference not in TRANSIENT_API_ENUMS:
            report.check(
                False,
                f"API state enum is bound to no aggregate: {reference}",
            )
            continue
        values, subset_of = TRANSIENT_API_ENUMS[reference]
        actual = set(enums[reference])
        report.check(
            actual == set(values),
            f"transient API enum {reference} differs from its declaration: "
            f"only-in-api={sorted(actual - set(values))} only-in-declaration={sorted(set(values) - actual)}",
        )
        if subset_of:
            machine_states = set(machines[subset_of]["states"])
            report.check(
                actual <= machine_states,
                f"transient API enum {reference} is not a subset of {subset_of}: "
                f"{sorted(actual - machine_states)}",
            )

    # 11. Declared projections cover their machine exactly.
    for machine_id, references, mapping in PROJECTIONS:
        if machine_id not in machines:
            report.check(False, f"projection references unknown machine: {machine_id}")
            continue
        machine_states = set(machines[machine_id]["states"])
        report.check(
            set(mapping) == machine_states,
            f"projection of {machine_id} does not cover every state: "
            f"missing={sorted(machine_states - set(mapping))} extra={sorted(set(mapping) - machine_states)}",
        )
        target = set(mapping.values())
        for value in target:
            report.check(
                bool(STATE_NAME_PATTERN.fullmatch(value)),
                f"projection value is not lowercase kebab-case: {machine_id} -> {value!r}",
            )
        for reference in references:
            if reference not in enums:
                report.check(False, f"projection API enum does not exist: {reference}")
                continue
            actual = set(enums[reference])
            report.check(
                actual == target,
                f"projection API enum {reference} differs: only-in-api={sorted(actual - target)} "
                f"only-in-projection={sorted(target - actual)}",
            )

    # 12. The contract document records the same table.
    report.check(
        set(contract) == set(aggregates),
        f"contract document binding table mismatch: "
        f"only-in-document={sorted(set(contract) - set(aggregates))} "
        f"only-in-validator={sorted(set(aggregates) - set(contract))}",
    )
    for binding in BINDINGS:
        row = contract.get(binding.aggregate)
        if row is None:
            continue
        expected_machine = (binding.machine,) if binding.machine else ()
        report.check(
            row["machine"] == expected_machine,
            f"{binding.aggregate}: documented machine {row['machine']} != {expected_machine}",
        )
        report.check(
            row["sql"] == tuple(sorted(binding.sql)),
            f"{binding.aggregate}: documented SQL columns {row['sql']} != {tuple(sorted(binding.sql))}",
        )
        report.check(
            row["api"] == tuple(sorted(binding.api)),
            f"{binding.aggregate}: documented API enums {row['api']} != {tuple(sorted(binding.api))}",
        )
        report.check(
            row["internal"] == tuple(sorted(binding.internal_states)),
            f"{binding.aggregate}: documented internal states {row['internal']} != "
            f"{tuple(sorted(binding.internal_states))}",
        )


def main() -> int:
    report = Report()
    try:
        validate(report)
    except Failure as failure:
        print(f"state vocabulary validation: FAIL\n- {failure}", file=sys.stderr)
        return 1
    if report.errors:
        print("state vocabulary validation: FAIL", file=sys.stderr)
        for error in report.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    machine_bound = sum(1 for binding in BINDINGS if binding.machine)
    sql_bound = sum(len(binding.sql) for binding in BINDINGS)
    api_bound = sum(len(binding.api) for binding in BINDINGS)
    print(
        "state vocabulary validation: PASS "
        f"({len(BINDINGS)} aggregates, {machine_bound} bound registry machines, "
        f"{sql_bound} bound SQL columns, {len(SQL_LOCAL_VOCABULARIES)} declared sub-entity "
        f"vocabularies, {api_bound} bound API enums)"
    )
    print(
        "claim_scope=vocabulary-agreement-only; transitions and workers remain unimplemented"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
