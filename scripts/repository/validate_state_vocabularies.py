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
        sql=("ranked_identities.state",),
    ),
    Binding(
        aggregate="idempotency-ledger",
        machine="idempotency-ledger",
        states=(
            "executing",
            "committed",
            "replayable-failure",
            "conflict",
            "expired",
            "abandoned",
        ),
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
            "ended",
        ),
        sql=("friend_requests.state",),
    ),
    Binding(
        aggregate="rivalry",
        machine="rivalry",
        states=("none", "active", "ended"),
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
        aggregate="invite-code",
        machine="invite-code",
        states=("issued", "redeemed", "expired", "revoked", "retired"),
        sql=("invite_codes.state",),
        note="Private-beta admission under D-180. No API enum: the invitee is told "
        "whether the redemption succeeded and never the code's lifecycle, because "
        "distinguishing unknown from expired from already-redeemed is what makes "
        "code enumeration productive.",
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
        sql=(
            "notification_events.state",
            "notifications.state",
        ),
        api=("Notification.state",),
        internal_states=("created", "grouped", "ready", "suppressed"),
        note=(
            "The API enum is exactly the states that reached the inbox. "
            "Everything before delivery is worker state; see D-420."
        ),
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
        sql=("service_instances.state",),
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
        sql=("privileged_supervisor_instances.state",),
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
            "exiting",
            "crashed",
        ),
        note="Local-only; never persisted server-side and never exposed by the API.",
        sql=("shell_sessions.state",),
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
        sql=(
            "update_policies.state",
            "update_installations.state",
        ),
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
        aggregate="linked-identity",
        machine="linked-identity",
        states=(
            "candidate",
            "linked",
            "unlink-pending",
            "lost",
            "compromised",
            "recovery-pending",
            "unlinked",
            "superseded",
        ),
        sql=("linked_identities.state",),
        api=("Identity.state",),
        internal_states=("candidate", "superseded"),
        note="PF-007. The aggregate was called `identity-link` and bound no machine, "
        "under a recorded absence saying the enrollment flow owned its transitions and "
        "they were unspecified. It is renamed to the spelling the table and the machine "
        "already use, because three names for one aggregate is the drift the one-spelling "
        "rule exists to stop. `candidate` is a link in flight and `superseded` is history "
        "the successor replaced; neither is a state a client is shown.",
    ),
    Binding(
        aggregate="recovery-case",
        machine="recovery-case",
        states=(
            "requested",
            "verifying",
            "cooling-off",
            "applied",
            "denied",
            "cancelled",
            "expired",
        ),
        sql=("recovery_cases.state",),
        note="Account recovery under D-380. No API enum: no operation exposes "
        "the case, so a client cannot read a state the contract has not "
        "published, and inventing one here would be a projection with no "
        "consumer.",
    ),
    Binding(
        aggregate="identity-investigation",
        machine="identity-investigation",
        states=(
            "opened",
            "gathering",
            "awaiting-participant",
            "concluded-no-action",
            "concluded-restricted",
            "concluded-consolidation",
            "withdrawn",
            "expired",
        ),
        sql=("identity_investigations.state",),
        note="Integrity-private under D-381. The participant reads the effect "
        "through `ranked-identity-eligibility`, which already marks its "
        "investigation states internal for the same reason.",
    ),
    Binding(
        aggregate="account-consolidation",
        machine="account-consolidation",
        states=(
            "requested",
            "planning",
            "awaiting-confirmation",
            "applying",
            "applied",
            "rejected",
            "reversed",
            "expired",
        ),
        sql=("consolidation_cases.state",),
        note="D-070 duplicate-account consolidation, D-382. `applied` is not "
        "terminal: a successful appeal moves it to `reversed`.",
    ),
    Binding(
        aggregate="lineage-fork-case",
        machine="lineage-fork-case",
        states=(
            "detected",
            "quarantined",
            "survivor-selected",
            "requalifying",
            "resumed",
            "unresolved",
            "appealed",
            "reversed",
        ),
        sql=("lineage_fork_cases.state",),
        note="D-072 fork and clone resolution, D-383. `unresolved` is not "
        "terminal, because D-072 makes the resolution appealable and a denied "
        "appeal returns the case to it.",
    ),
    Binding(
        aggregate="source-certification",
        machine="source-certification",
        states=(
            "candidate",
            "testing",
            "active",
            "degraded",
            "suspended",
            "expired",
            "superseded",
            "retired",
        ),
        sql=("source_certifications.state",),
        note="D-387. Distinct from `platform-certification`, which certifies an "
        "operating-system profile; this one certifies an exact source, mode, "
        "platform and accounting tuple. Only `active` may exceed "
        "private-analytics, which is a check constraint rather than a rule.",
    ),
    Binding(
        aggregate="claim-record",
        states=("accepted", "corrected", "retracted", "quarantined"),
        api=("ClaimRecord.state",),
        note="Claims are append-only facts; the state is derived, never a stored column.",
    ),
    # PF-013. Five subsystem projections split out of interactive-shell, which had
    # collapsed six independent facts into one state variable. They persist in
    # local-store-v1.sql and never leave the device.
    Binding(
        aggregate="local-collection",
        machine="local-collection",
        states=("collecting", "paused", "stopped"),
        sql=("local_collection_state.state",),
    ),
    Binding(
        aggregate="local-sync",
        machine="local-sync",
        states=("syncing", "paused", "backing-off", "stopped"),
        sql=("local_sync_state.state",),
    ),
    Binding(
        aggregate="local-auth",
        machine="local-auth",
        states=("authenticated", "auth-required", "locked-out"),
        sql=("local_auth_state.state",),
    ),
    Binding(
        aggregate="local-permission",
        machine="local-permission",
        states=("granted", "repair-required", "denied"),
        sql=("local_permission_state.state",),
    ),
    Binding(
        aggregate="local-connectivity",
        machine="local-connectivity",
        states=("online", "degraded", "offline"),
        sql=("local_connectivity_state.state",),
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
    # One transport attempt, not the notification. It is a sub-entity vocabulary
    # rather than an aggregate because the aggregate is the notification and a
    # transport attempt has no independent lifecycle: it is queued against an item
    # that already exists in the inbox, and its worst outcome loses a hint rather
    # than a notification. The table's own CHECK constraints hold the rest of the
    # rule — an inbox attempt has only `accepted`, and no attempt of any transport
    # carries a read.
    "notification_deliveries.state": (
        "queued",
        "deferred",
        "accepted",
        "acknowledged",
        "failed",
        "expired",
    ),
    # The participant-facing per-device answer under D-076. It is the
    # `local-deletion-command` machine coarsened by two facts the machine cannot
    # hold: whether the command was ever acknowledged, which separates a device
    # that never heard the request from one that heard it and stopped, and whether
    # the participant waived it. The DDL makes it equal that coarsening by
    # construction, so this declaration cannot drift from the state column beside
    # it.
    "local_deletion_commands.disposition": (
        "pending",
        "complete",
        "failed",
        "expired",
        "unreachable",
        "waived",
    ),
    # The device's own answer, and deliberately the same four values
    # `packages/schemas/local-store-v1.sql` declares on the device-side receipt.
    # The server row is the transported form of the device row; a second spelling
    # for the same fact is the duplication SR-009 exists to remove.
    "local_deletion_receipts.outcome": ("complete", "partial", "refused", "expired"),
    # Device-side outbox rows, not an aggregate: one claim's delivery attempt, whose
    # lifetime ends when the server acknowledges it. Surfaced once the persistence
    # check began reading the device half of the storage contract.
    "outbox_claims.state": (
        "pending",
        "in-flight",
        "acknowledged",
        "rejected",
        "superseded",
    ),
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
    "device_lineages.continuity_state": (
        "continuous",
        "gap-declared",
        "broken",
        "revoked",
    ),
    # A sealed ranking entry freezes the trust state that produced its ADR-020
    # weight, so the entry stays explainable after the ranked identity moves on.
    # The column name does not end in `_state`, so nothing would have governed
    # it; it is declared here deliberately, because it is a copy of the
    # `ranked-identity-eligibility` vocabulary minus `retired`, which produces no
    # entry at all, and a change to that machine has to be reconsidered here
    # rather than silently diverge.
    "ranking_entries.trust_state_at_projection": (
        "unverified",
        "eligible",
        "investigating",
        "restricted",
        "consolidating",
        "appealed",
        "reversed",
    ),
}

# Sub-entity outcome vocabularies that are also published on the API. Key is the
# SQL_LOCAL_VOCABULARIES entry that owns the vocabulary; value is the API enum that mirrors it.
OUTCOME_MIRRORS: dict[str, str] = {
    "appeal_decisions.decision": "Appeal.decision",
    "local_deletion_commands.disposition": "LocalDeletionOutcome.disposition",
}

# API enums that report the outcome of a single request rather than a stored aggregate state.
TRANSIENT_API_ENUMS: dict[str, tuple[tuple[str, ...], str | None]] = {
    "ClaimBatchResult.state": (("accepted", "rejected"), None),
    # PF-006. A sign-in callback consumes the transaction; a link callback stops at
    # `callback-received`, because linking is performed by linkIdentity under recent
    # authentication rather than by a public callback. Both values are states of the
    # machine, which rule 10 checks.
    "OAuthCompletion.state": (("callback-received", "consumed"), "oauth-transaction"),
}

# Why an aggregate binds no machine, no SQL column or no API enum.
#
# Coverage was driven by whether a field happened to be filled in, so an aggregate
# whose `sql=` was never populated was indistinguishable from one that legitimately
# has no persistence — and all five `local-*` aggregates sat at `sql=()` while
# `local-store-v1.sql` defined the very tables they name. An omission must now be
# stated, and stating it is what makes the count of unchecked aggregates readable.
#
# Mirrored in the recorded-absence table of AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md;
# the two are compared entry for entry, so neither can drift.
RECORDED_ABSENCES: dict[tuple[str, str], str] = {
    (
        "session-member",
        "machine",
    ): "Member rows of a token family; the family machines own the transitions.",
    (
        "board-container",
        "machine",
    ): "A two-value archive flag; its mutable concepts have machines of their own.",
    (
        "claim-record",
        "machine",
    ): "Claims are immutable facts; the registry indexes mutable concepts.",
    (
        "claim-record",
        "sql",
    ): "Append-only; the state is derived from later records, never stored.",
    (
        "device-authorization-grant",
        "machine",
    ): "Open: mutable, but the OAuth flow owns its transitions and they are unspecified.",
    (
        "oauth-transaction",
        "api",
    ): "OAuthCompletion.state echoes the terminal value only; see TRANSIENT_API_ENUMS.",
    (
        "web-session-family",
        "api",
    ): "Families are server-internal; a client sees only its own session member.",
    (
        "native-session-family",
        "api",
    ): "Families are server-internal; a client sees only its own session member.",
    (
        "idempotency-ledger",
        "api",
    ): "Replay is observed through the replayed response, never as a state value.",
    (
        "ranking-projection",
        "api",
    ): "Generation build state is operational; a client sees a sealed generation or none.",
    (
        "friendship",
        "api",
    ): "The API exposes the edge, not the machine; the viewer's own side is derived.",
    (
        "rivalry",
        "api",
    ): "The API exposes the edge, not the machine; the viewer's own side is derived.",
    (
        "board-membership",
        "api",
    ): "Membership is exposed as presence in a board's member list, not as a state value.",
    (
        "board-invitation",
        "api",
    ): "An invitee sees the invitation or does not; intermediate states are server-side.",
    (
        "invite-code",
        "api",
    ): "Private-beta admission under D-180. The invitee is told whether it worked, not its state.",
    (
        "presence-lease",
        "api",
    ): "PresenceLease.availability is a declared coarser projection; see PROJECTIONS.",
    (
        "account-lifecycle",
        "api",
    ): "Exposed through the account's own surface as capability, not as a lifecycle enum.",
    (
        "recovery-case",
        "api",
    ): "Account recovery under D-380. No operation exposes the case.",
    (
        "identity-investigation",
        "api",
    ): "Integrity-private under D-381; a public state value would publish the sanction.",
    (
        "account-consolidation",
        "api",
    ): "D-070 consolidation under D-382. getConsolidationPlan publishes the plan and "
    "no lifecycle value; a state like `applying` is an operational fact.",
    (
        "lineage-fork-case",
        "api",
    ): "D-072 fork and clone resolution under D-383; quarantine is read through evidence class.",
    (
        "source-certification",
        "api",
    ): "D-387. Certification is server-assigned; exposing it would let a client select it.",
    (
        "update-lifecycle",
        "api",
    ): "Local-only; the server is never told what a device has installed.",
    (
        "release-trust",
        "api",
    ): "Local-only; trust in a release is evaluated on the device against TUF metadata.",
    (
        "local-deletion-command",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
    (
        "daemon-lifecycle",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
    (
        "privileged-supervisor",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
    (
        "interactive-shell",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
    (
        "local-collection",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
    (
        "local-sync",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
    (
        "local-auth",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
    (
        "local-permission",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
    (
        "local-connectivity",
        "api",
    ): "Local-only; never persisted server-side and never exposed by the API.",
}

# A state column that is neither bound to an aggregate nor a declared sub-entity
# vocabulary must still be accounted for, or extending the persistence check to the
# device half would simply not see it. Each entry names the unit that owns the hole.
SQL_COLUMNS_WITHOUT_VOCABULARY: dict[str, str] = {
    "source_receipts.certification_state": (
        "Device-side receipt column with no CHECK constraint, so it can hold any "
        "value. The source-certification vocabulary it should mirror is owned by "
        "PF-017 and PF-018; recorded here rather than guessed at."
    ),
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


def local_store_text() -> str:
    return (SCHEMAS / "local-store-v1.sql").read_text(encoding="utf-8")


def local_store_tables() -> set[str]:
    """Tables declared by the SQLite half of the storage contract."""
    return set(re.findall(r"create table (\w+)", local_store_text()))


def contract_absences(text: str) -> dict[tuple[str, str], str]:
    """Parse the recorded-absence table out of the authoritative contract document.

    The contract said "the reason is given under Open items" for every `—` cell, and
    nothing compared the two. Thirty-nine cells recorded `—`; Open items explained
    four. A promise no validator executes is the same defect as a check phrased as an
    absence, so the reasons now live in a table this parses and compares.
    """
    rows: dict[tuple[str, str], str] = {}
    inside = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Aggregate | Absent binding | Reason |"):
            inside = True
            continue
        if inside:
            if not stripped.startswith("|"):
                break
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) != 3 or set(cells[0]) <= {"-", ":"}:
                continue
            rows[(cells[0].strip("`"), cells[1].strip("`"))] = cells[2]
    if not inside:
        raise Failure("contract document contains no recorded-absence table")
    return rows


def coverage(binding: Binding) -> int:
    """How many of the three owners this aggregate is actually compared against."""
    return sum((bool(binding.machine), bool(binding.sql), bool(binding.api)))


def check_absence_reasons(report: Report, contract_text: str) -> None:
    """An unpopulated binding must be indistinguishable from nothing but itself.

    `validate_state_vocabularies.py` reported an aggregate count, and an aggregate
    counted whether it was compared against three owners or none. Five `local-*`
    aggregates carried `sql=()` while `local-store-v1.sql` defined the tables they
    name, so the number that was supposed to measure coverage went up when coverage
    was removed. Requiring a reason for every absence is what stops that: the reason
    is a claim, and a claim about an owner that exists is refutable.
    """
    absences = {
        (binding.aggregate, axis)
        for binding in BINDINGS
        for axis, bound in (
            ("machine", bool(binding.machine)),
            ("sql", bool(binding.sql)),
            ("api", bool(binding.api)),
        )
        if not bound
    }

    for aggregate, axis in sorted(absences):
        report.check(
            (aggregate, axis) in RECORDED_ABSENCES,
            f"{aggregate}: binds no {axis} and records no reason. An omission that is "
            "not stated cannot be told apart from one that was never noticed",
        )

    # A reason for an axis that is bound is a justification outliving its hole.
    for aggregate, axis in sorted(RECORDED_ABSENCES):
        report.check(
            (aggregate, axis) in absences,
            f"{aggregate}: records a reason for an absent {axis} binding, but the "
            f"{axis} binding is populated; the reason has outlived the gap it excused",
        )

    documented = contract_absences(contract_text)
    only_in_document = sorted(set(documented) - absences)
    only_in_validator = sorted(absences - set(documented))
    report.check(
        not only_in_document and not only_in_validator,
        "recorded-absence table mismatch: "
        f"only-in-document={only_in_document} only-in-validator={only_in_validator}",
    )
    for key in sorted(set(documented) & set(RECORDED_ABSENCES)):
        report.check(
            documented[key] == RECORDED_ABSENCES[key],
            f"{key[0]}: the contract's recorded reason for its absent {key[1]} binding "
            "differs from the validator's",
        )


def validate(report: Report) -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    machines = {machine["machine_id"]: machine for machine in registry["machines"]}
    sql_text = SQL_PATH.read_text(encoding="utf-8")
    bodies = table_bodies(sql_text)
    checks = sql_check_sets(bodies)
    declared_state_columns = sql_state_columns(bodies)

    # The device half of the storage contract was read for table names only, so a
    # column in it could not be bound and could not be found missing. Both halves are
    # now resolved the same way; a server aggregate still cannot bind a device column,
    # because rule 5 checks the column against the vocabulary either way and the
    # privacy boundary is enforced by what the tables hold, not by this validator.
    local_bodies_full = table_bodies(local_store_text())
    local_checks = sql_check_sets(local_bodies_full)
    local_state_columns_declared = sql_state_columns(local_bodies_full)
    checks = {**checks, **local_checks}
    declared_state_columns = declared_state_columns | local_state_columns_declared
    spec = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    enums = api_enums(spec)
    contract = contract_table(CONTRACT_PATH.read_text(encoding="utf-8"))

    aggregates = [binding.aggregate for binding in BINDINGS]
    report.check(
        len(aggregates) == len(set(aggregates)),
        "duplicate aggregate id in the binding table",
    )

    # 0a. Every declared persistence owner must exist.
    #
    # AGENTS.md requires every mutable aggregate to have one persistence owner.
    # A machine naming a table the DDL does not define has none. Nineteen of
    # twenty-six did. Nothing noticed because the registry stores owners in
    # kebab-case and the DDL declares them in snake_case, so a naive comparison
    # finds no overlap at all and a careless one finds no defect.
    # A `local-only` machine persists on the device, and PF-013 added five subsystem
    # projections that never leave it. Requiring them in planning-schema.sql would have
    # meant declaring server tables for state AGENTS.md does not permit across the
    # boundary: none of collection, sync, auth, permission or connectivity state is a
    # fixed-schema aggregate accounting figure or an integrity claim, and those are the
    # only things that may cross. `local-store-v1.sql` is the SQLite half of the storage
    # contract and is where they belong.
    local_bodies = local_store_tables()
    for machine_id, machine in sorted(machines.items()):
        device_local = machine["transaction_boundary"] == "device-local"
        for owner in machine["persistence_owner"]:
            table = owner.replace("-", "_")
            if device_local and table in local_bodies:
                continue
            report.check(
                table in bodies,
                f"{machine_id} names persistence owner {owner!r}, which "
                + (
                    "neither planning-schema.sql nor local-store-v1.sql defines"
                    if device_local
                    else "planning-schema.sql does not define"
                ),
            )

    # 0b. State-graph integrity, for every machine rather than every bound one.
    #
    # A state no transition can reach is dead vocabulary; a non-terminal state
    # with no outgoing transition is a sink the contract does not admit to; and
    # a terminal state that still has outgoing transitions is not terminal. All
    # three were present and none was caught, because a state named only as a
    # transition *source* still looks used.
    for machine_id, machine in sorted(machines.items()):
        reachable = {machine["initial_state"]}
        frontier = [machine["initial_state"]]
        while frontier:
            current = frontier.pop()
            for transition in machine["transitions"]:
                if current in transition["from"] and transition["to"] not in reachable:
                    reachable.add(transition["to"])
                    frontier.append(transition["to"])
        for state in sorted(set(machine["states"]) - reachable):
            report.check(
                False,
                f"{machine_id}.{state} is unreachable from {machine['initial_state']!r}",
            )
        terminal = set(machine["terminal_states"])
        for state in machine["states"]:
            outgoing = any(state in t["from"] for t in machine["transitions"])
            if state in terminal:
                report.check(
                    not outgoing,
                    f"{machine_id}.{state} is declared terminal but has outgoing transitions",
                )
            else:
                report.check(
                    outgoing,
                    f"{machine_id}.{state} is a sink but is not declared terminal",
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
        if column in SQL_COLUMNS_WITHOUT_VOCABULARY:
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


def check_concurrency_model(report: Report) -> None:
    """The outbox contract is a schema constraint, not a naming convention.

    `outbox_events` in `packages/schemas/planning-schema.sql` carries
    `unique (aggregate_id, aggregate_revision)`. That single constraint decides most of
    what follows: an aggregate can only publish if it has a revision to publish under,
    and it can only publish exactly once per revision. Until PF-004 the registry
    declared none of this, so thirty-two aggregates named a persistence owner and said
    nothing about how a concurrent write to it is ordered, what commits with it, or
    whether anything downstream can observe it. `AGENTS.md` requires every mutable
    aggregate to have a revision model, transaction boundaries and reversal behaviour;
    the registry is where that has to be checkable.

    The rules are consequences of the schema rather than preferences:

    - publishing requires a revision, so `outbox: required` cannot pair with
      `single-writer`, which has no server-side revision at all;
    - publishing is part of the write, so `outbox: required` demands the
      `aggregate-and-outbox` boundary — an outbox row written in a second transaction
      is exactly the lost-event bug the table exists to prevent;
    - `device-local` never reaches a server transaction, so it cannot publish;
    - `local-only` privacy means the rows never leave the device, so the boundary must
      be `device-local`. A local-only aggregate in a server transaction would be a
      privacy-boundary violation expressed as a persistence choice.
    """
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for machine in registry["machines"]:
        identifier = machine["machine_id"]
        revision = machine["revision_model"]
        boundary = machine["transaction_boundary"]
        outbox = machine["outbox"]

        if outbox == "required":
            if revision == "single-writer":
                report.errors.append(
                    f"{identifier} publishes to the outbox and has revision model "
                    "single-writer, which carries no revision; "
                    "outbox_events.unique(aggregate_id, aggregate_revision) has "
                    "nothing to key on"
                )
            if boundary != "aggregate-and-outbox":
                report.errors.append(
                    f"{identifier} publishes to the outbox with transaction boundary "
                    f"{boundary!r}; the outbox row must commit with the aggregate or "
                    "the event is lost exactly when the write succeeds"
                )
        if boundary == "device-local" and outbox != "none":
            report.errors.append(
                f"{identifier} is device-local and declares outbox {outbox!r}; a device "
                "has no server transaction to publish inside"
            )
        if machine["privacy_boundary"] == "local-only" and boundary != "device-local":
            report.errors.append(
                f"{identifier} is local-only and declares transaction boundary "
                f"{boundary!r}; local-only rows never reach a server transaction, so "
                "this states a privacy-boundary violation as a persistence choice"
            )
        if revision == "immutable-after-seal" and boundary == "aggregate-local":
            report.errors.append(
                f"{identifier} is immutable after sealing and publishes nothing; a "
                "sealed aggregate nothing can observe cannot drive a projection"
            )


def main() -> int:
    report = Report()
    try:
        validate(report)
        check_concurrency_model(report)
        check_absence_reasons(report, CONTRACT_PATH.read_text(encoding="utf-8"))
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
    three_way = sum(1 for binding in BINDINGS if coverage(binding) == 3)
    two_way = sum(1 for binding in BINDINGS if coverage(binding) == 2)
    one_way = sum(1 for binding in BINDINGS if coverage(binding) == 1)
    print(
        "state vocabulary validation: PASS "
        f"({len(BINDINGS)} aggregates, {machine_bound} bound registry machines, "
        f"{sql_bound} bound SQL columns, {len(SQL_LOCAL_VOCABULARIES)} declared sub-entity "
        f"vocabularies, {api_bound} bound API enums)"
    )
    # The aggregate count says how many aggregates are declared, not how many are
    # checked against three owners. Reporting the three depths separately is the point
    # of PF-067: a green run on 42 aggregates of which one is compared against a single
    # owner must not read as 42 three-way agreements.
    print(
        f"coverage={three_way} three-way, {two_way} two-way, {one_way} format-only; "
        f"{len(RECORDED_ABSENCES)} absent bindings each carry a recorded reason"
    )
    print(
        "claim_scope=vocabulary-agreement-only; transitions and workers remain "
        "unimplemented, and a recorded reason is an explanation rather than a check"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
