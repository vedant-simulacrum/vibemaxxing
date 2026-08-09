#!/usr/bin/env python3
"""Boards, presence and notifications: the rules no other validator holds.

PF-025, PF-026 and PF-027 complete SR-011. Each of them repaired a rule that was
stated in prose, or stated in one artifact and contradicted in another, and nothing
compared the two. This validator is where those comparisons live. It checks
agreement between records; it executes no handler, opens no board, admits no pulse
and delivers no notification, and it would pass identically if none ever existed.

**Boards.** A block between two accounts may not terminally end a membership or an
invitation a third party granted. `AGENTS.md` states that blocks are directional and
independent from symmetric friendship state, and D-585 applied that to friendship;
`board-membership` kept a terminal `blocked` reached by a user's `block-cascade`
from four states with no transition out, and `board-invitation` kept
`invalidated-by-block`. Both are refused here, in the same shape
`tests/ci/test_block_independence.py` refuses the friendship one, so the repair
cannot be undone in one machine while the other stays clean.

An invitation grants a role and, until PF-025, `board_invites` held no role column
and no invitee: the acceptance criterion said the operation cannot grant an admin or
owner role, and the refusal compared fields no record held. The wire enum and the
SQL vocabulary are compared to each other here, and both are required to exclude
`owner` and `admin`.

Board kind and visibility are compared across the API and the SQL because they were
two vocabularies for one concept: `Board.kind` admitted three values against a
`boards.board_type` that admitted four, so a stored hacker-house board had no
representation on the wire, and `visibility` was published by neither while
`AGENTS.md` makes it the input that decides whether a board view needs current
viewer authorization.

**Presence.** Presence is server-derived from qualifying device activity, so the
renewal request may not name a state. The check is that `PresenceRenewalRequest`
declares no `availability` and does declare the device and the lease generation the
discard rule is stated against, and that every security alternative on
`renewPresence` requires device proof — the social contract says a browser or
ordinary web session cannot fabricate indefinite activity, and a session-cookie
alternative is exactly that session.

The three D-073 thresholds are checked by value and by order. Idle must be strictly
less than offline: they were 300 and 90 under two misnamed keys, which is a lease
that expires before it can go idle and an `idle` state nothing can reach.

The multi-device merge is checked by evaluating the vector file's own rule under
both device orderings and requiring the same answer. A merge fixture that is only
read is a fixture that cannot disagree.

**Notifications.** Every declared event type names exactly one preference category,
every category has a property on the preferences record and a column on
`notification_preferences`, and `security` maps to the flag that is constrained
true. Four flags governed eight types with the mapping written down nowhere, so
`category-disabled` named a category no artifact defined and whether a security
notice could be muted depended on which mapping a worker assumed.

The retraction vocabulary is compared between the SQL check and the schema enum.
`notifications.retraction_reason_code` admitted any string, so the registered code
the contract promises was a convention.

Exit codes: 0 when every check passes, 1 on any defect, 2 when an input cannot be
read.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
CONFORMANCE = ROOT / "conformance"
SQL_PATH = SCHEMAS / "planning-schema.sql"
OPENAPI = SCHEMAS / "openapi-v1.yaml"
REGISTRY = SCHEMAS / "state-machine-registry-v1.json"
POLICIES = SCHEMAS / "policy-defaults-v1.json"
NOTIFICATION = SCHEMAS / "notification-delivery-v1.schema.json"
MERGE_VECTORS = CONFORMANCE / "social" / "presence-merge-vectors.json"

# The two machines a directional block was allowed to drive to a terminal state.
# `friendship` and `rivalry` are covered by tests/ci/test_block_independence.py.
BLOCK_FREE_MACHINES = ("board-membership", "board-invitation")
BLOCK_STATE_MARKERS = ("blocked", "invalidated-by-block")
BLOCK_ACTIONS = ("block-cascade",)

PRIVILEGED_ROLES = ("owner", "admin")
BOARD_KINDS = ("private", "organization", "hacker-house", "community")
BOARD_VISIBILITIES = ("public", "unlisted", "invite-only", "private")

# D-073. Named by key here so a rename cannot silently move a number, and checked
# by value so a name cannot silently mean a different one.
PRESENCE_THRESHOLDS = {
    "presence_heartbeat_seconds": 30,
    "presence_idle_after_seconds": 90,
    "presence_offline_after_seconds": 300,
}

RETRACTION_CODES = (
    "NOTIFICATION_RETRACTED_BY_CORRECTION",
    "NOTIFICATION_RETRACTED_BY_MODERATION_REVERSAL",
    "NOTIFICATION_RETRACTED_BY_RANKING_REBUILD",
)

CONSTRAINED_TRUE_CATEGORY = "security"


class Failure(RuntimeError):
    """An input the validator needs could not be read."""


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise Failure(f"unreadable {path}: {error}") from error


def load_yaml(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise Failure(f"unreadable {path}: {error}") from error


def table_bodies(sql: str) -> dict[str, str]:
    """The parenthesised body of every `create table`, matched by paren depth.

    Cutting at the first `\\n);` would be wrong on `notifications`, which closes
    with `) partition by range (created_at);` and would otherwise swallow the four
    tables after it.
    """
    bodies: dict[str, str] = {}
    for match in re.finditer(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(", sql):
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


def check_vocabulary(body: str, column: str) -> set[str]:
    """The values a column's CHECK admits, as a set. Empty when there is none."""
    match = re.search(
        rf"(?m)^\s*{re.escape(column)}\s+[a-z ]*?check\s*\({re.escape(column)}\s+in\s*\(([^)]*)\)",
        body,
    )
    if match is None:
        return set()
    return {value.strip().strip("'") for value in match.group(1).split(",")}


def api_enum(spec: dict, schema_name: str, prop: str) -> set[str]:
    node = spec["components"]["schemas"].get(schema_name)
    if node is None:
        return set()
    field = (node.get("properties") or {}).get(prop)
    if field is None:
        return set()
    return set(field.get("enum") or ())


def machines(registry: dict) -> dict[str, dict]:
    return {entry["machine_id"]: entry for entry in registry["machines"]}


# ---------------------------------------------------------------------------
# Boards
# ---------------------------------------------------------------------------


def check_boards(report: Report, spec: dict, registry: dict, bodies: dict) -> None:
    found = machines(registry)
    for machine_id in BLOCK_FREE_MACHINES:
        machine = found.get(machine_id)
        if machine is None:
            report.check(False, f"registry declares no {machine_id} machine")
            continue
        for marker in BLOCK_STATE_MARKERS:
            report.check(
                marker not in machine["states"],
                f"{machine_id} declares the block-caused state {marker!r}: a state "
                "one account causes on another account's membership, that neither "
                "can leave, is a directional block stored in a shared aggregate",
            )
        for transition in machine["transitions"]:
            report.check(
                transition["action"] not in BLOCK_ACTIONS,
                f"{machine_id} declares a {transition['action']} transition "
                f"{transition['transition_id']}: a block changes no relationship "
                "row, and its effect is evaluated at read time",
            )
        # Removing a state must not strand another or leave a terminal state with a
        # way out, which is the check that stops the repair being a deletion.
        reachable = {machine["initial_state"]}
        for _ in range(len(machine["states"])):
            for transition in machine["transitions"]:
                if reachable & set(transition["from"]):
                    reachable.add(transition["to"])
        report.check(
            reachable == set(machine["states"]),
            f"{machine_id} has unreachable states: "
            f"{sorted(set(machine['states']) - reachable)}",
        )
        for transition in machine["transitions"]:
            for state in transition["from"]:
                report.check(
                    state not in machine["terminal_states"],
                    f"{machine_id} leaves the terminal state {state!r} through "
                    f"{transition['transition_id']}",
                )

    membership = found.get("board-membership")
    if membership is not None:
        targets = {t["to"] for t in membership["transitions"]}
        report.check(
            "active-admin" in targets
            and any(
                t["to"] == "active-admin" and "active-owner" in t["from"]
                for t in membership["transitions"]
            ),
            "board-membership declares no transition out of active-owner into a "
            "non-owner active state, while the board-owner-transfer race plan "
            "requires the outgoing owner to stay a member: the plan's residual row "
            "is unreachable in the machine that owns it",
        )
        for transition in membership["transitions"]:
            if transition["to"] in {"active-owner", "active-admin"}:
                report.check(
                    transition["recent_auth"] is True,
                    "board-membership grants a privileged role without recent "
                    f"authentication: {transition['transition_id']}",
                )

    invites = bodies.get("board_invites", "")
    # A column *declaration*, not the identifier anywhere in the body: the table
    # also names `invited_account_id` inside a CHECK, and a substring test would
    # have read that mention as the column and passed on a table that lost it.
    report.check(
        re.search(r"(?m)^\s*invited_account_id\s+uuid\b", invites) is not None,
        "board_invites declares no invited_account_id column, so an invitation "
        "names no one and the role it grants cannot be bound to a person",
    )
    sql_roles = check_vocabulary(invites, "role")
    report.check(
        bool(sql_roles),
        "board_invites.role has no CHECK, so the refusal of a privileged invitation "
        "compares a field the record does not constrain",
    )
    wire_roles = api_enum(spec, "BoardInvitationRequest", "role")
    report.check(
        wire_roles == sql_roles,
        "BoardInvitationRequest.role differs from board_invites.role: "
        f"only-on-the-wire={sorted(wire_roles - sql_roles)} "
        f"only-in-sql={sorted(sql_roles - wire_roles)}",
    )
    for role in PRIVILEGED_ROLES:
        report.check(
            role not in sql_roles and role not in wire_roles,
            f"an invitation can grant {role!r}: privilege escalation by invitation "
            "must be unrepresentable, not refused in a handler",
        )

    boards = bodies.get("boards", "")
    sql_kinds = check_vocabulary(boards, "board_type")
    report.check(
        sql_kinds == set(BOARD_KINDS),
        f"boards.board_type is not the declared four kinds: {sorted(sql_kinds)}",
    )
    for schema_name in ("Board", "BoardCreateRequest"):
        wire_kinds = api_enum(spec, schema_name, "kind")
        report.check(
            wire_kinds == sql_kinds,
            f"{schema_name}.kind differs from boards.board_type: "
            f"only-on-the-wire={sorted(wire_kinds - sql_kinds)} "
            f"only-in-sql={sorted(sql_kinds - wire_kinds)}",
        )
        wire_visibility = api_enum(spec, schema_name, "visibility")
        report.check(
            wire_visibility == set(BOARD_VISIBILITIES),
            f"{schema_name}.visibility is not the declared four values: "
            f"{sorted(wire_visibility)}",
        )
    sql_visibility = check_vocabulary(boards, "visibility")
    report.check(
        sql_visibility == set(BOARD_VISIBILITIES),
        "boards.visibility does not carry the four values the board contract "
        f"states: {sorted(sql_visibility)}. Only the global leaderboard is "
        "universally public by default, so this is the value the current-viewer "
        "authorization rule reads",
    )
    report.check(
        re.search(r"(?m)^\s*name\s+text\s+not\s+null", boards) is not None,
        "boards declares no name, while Board requires one and BoardCreateRequest "
        "accepts one: the request carries a value the persistence owner cannot hold",
    )
    report.check(
        "membership_revision" in boards,
        "boards declares no membership_revision, while Board publishes one and the "
        "D-386 recheck needs a counter it can order",
    )
    report.check(
        "board_one_active_owner" in SQL_PATH.read_text(encoding="utf-8"),
        "the partial unique index enforcing at most one owner per board is absent",
    )


def check_board_creation_plan(report: Report) -> None:
    """The half the index cannot enforce: a board is never readable ownerless."""
    plans = load_json(CONFORMANCE / "p1140e" / "sql-race-plans-v1.json")
    case = next(
        (item for item in plans["cases"] if item["case_id"] == "board-create-owner"),
        None,
    )
    if case is None:
        report.check(
            False,
            "no board-create-owner race plan: the acceptance criterion says boards "
            "and board_memberships are written in one transaction in the recorded "
            "SQL plan, and no such plan exists",
        )
        return
    report.check(
        sorted(case["tables"]) == ["board_memberships", "boards"],
        "the board-create-owner plan does not name both tables it writes",
    )
    absent = [row for row in case["residual_rows"] if row["presence"] == "absent"]
    report.check(
        any("active-owner" in row["key"] for row in absent),
        "the board-create-owner plan states no absent row for a board without an "
        "active owner, which is the state the partial unique index is silent about",
    )

    block = next(item for item in plans["cases"] if item["case_id"] == "block-race")
    for row in block["residual_rows"]:
        if row["table"] in {"friend_edges", "rival_edges"}:
            report.check(
                row["presence"] == "present",
                f"the block-race plan removes {row['table']} on a block: D-585 "
                "makes a block change no relationship row, and a plan that deletes "
                "one is the pre-repair model outliving the repair",
            )


# ---------------------------------------------------------------------------
# Presence
# ---------------------------------------------------------------------------


def check_presence(report: Report, spec: dict, bodies: dict) -> None:
    request = spec["components"]["schemas"].get("PresenceRenewalRequest") or {}
    properties = request.get("properties") or {}
    report.check(
        "availability" not in properties,
        "PresenceRenewalRequest declares availability: presence is server-derived "
        "from qualifying device activity, so a request that names a state is the "
        "client selecting a server-assigned value",
    )
    for field in ("device_id", "lease_generation", "qualifying"):
        report.check(
            field in properties and field in (request.get("required") or []),
            f"PresenceRenewalRequest does not require {field}: the discard rule is "
            "stated against the device and the generation, and a rule enforced "
            "where a value is read but not where it is written is enforced nowhere",
        )

    operation = None
    for item in spec["paths"].values():
        for method, candidate in item.items():
            if (
                method.lower() in {"get", "post", "put", "patch", "delete"}
                and candidate.get("operationId") == "renewPresence"
            ):
                operation = candidate
    if operation is None:
        report.check(False, "the API declares no renewPresence operation")
    else:
        alternatives = operation.get("security") or []
        report.check(
            bool(alternatives)
            and all("deviceProof" in alternative for alternative in alternatives),
            "renewPresence admits a credential without device proof: a browser or "
            "ordinary web session cannot fabricate indefinite activity, and a "
            "session-cookie alternative on this route is that session",
        )

    leases = bodies.get("presence_leases", "")
    report.check(
        "visibility" not in leases,
        "presence_leases carries a visibility column: the presence projection "
        "answers once per account, so a policy stored once per device lets two "
        "devices disagree with no rule saying which the merge takes",
    )
    report.check(
        "lease_generation" in leases,
        "presence_leases records no lease generation",
    )
    report.check(
        "presence_visibility" in bodies.get("profiles", ""),
        "profiles carries no presence_visibility: the account-scoped presence "
        "policy has no persistence owner",
    )

    policies = load_json(POLICIES)["policies"]
    for key, expected in PRESENCE_THRESHOLDS.items():
        entry = policies.get(key)
        if entry is None:
            report.check(False, f"policy-defaults declares no {key}")
            continue
        report.check(
            entry["value"] == expected,
            f"{key} is {entry['value']} and D-073 fixes it at {expected}",
        )
    idle = (policies.get("presence_idle_after_seconds") or {}).get("value")
    offline = (policies.get("presence_offline_after_seconds") or {}).get("value")
    if idle is not None and offline is not None:
        report.check(
            idle < offline,
            f"the idle threshold {idle} is not strictly before the offline "
            f"threshold {offline}: a lease that expires before it can go idle "
            "leaves the idle state unreachable, which is what the two misnamed "
            "keys were hiding",
        )


def merge_availability(rule: dict, states: list[str]) -> str:
    """Fold per-device lease states into one account answer, by the stated rule."""
    order = rule["precedence"]
    ranked = [state for state in order if state in states]
    return rule["projection"][ranked[0]] if ranked else rule["empty"]


def check_presence_merge(report: Report) -> None:
    vectors = load_json(MERGE_VECTORS)
    rule = vectors["merge_rule"]
    report.check(
        len(set(rule["precedence"])) == len(rule["precedence"]),
        "the merge precedence repeats a state, so the fold is not a total order",
    )
    for case in vectors["cases"]:
        states = [device["state"] for device in case["devices"]]
        forward = merge_availability(rule, states)
        backward = merge_availability(rule, list(reversed(states)))
        report.check(
            forward == backward,
            f"{case['case_id']}: the merge depends on device order "
            f"({forward} forward, {backward} reversed)",
        )
        report.check(
            forward == case["expected_availability"],
            f"{case['case_id']}: the merge yields {forward} and the case expects "
            f"{case['expected_availability']}",
        )


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


def check_notifications(report: Report, spec: dict, bodies: dict) -> None:
    schema = load_json(NOTIFICATION)
    defs = schema["$defs"]
    categories = defs["event_categories"]["properties"]
    declared_types = set(defs["source_event"]["properties"]["event_type"]["enum"])
    report.check(
        set(categories) == declared_types,
        "event_categories does not name every event type exactly once: "
        f"only-in-map={sorted(set(categories) - declared_types)} "
        f"only-in-enum={sorted(declared_types - set(categories))}",
    )
    preferences = defs["preferences"]["properties"]
    prefs_sql = bodies.get("notification_preferences", "")
    for event_type, node in categories.items():
        category = node["const"]
        column = f"{category}_enabled"
        report.check(
            column in preferences,
            f"{event_type} names the category {category!r} and the preferences "
            f"record declares no {column}: a suppression cause of "
            "'category-disabled' would name a category no artifact defines",
        )
        report.check(
            re.search(rf"(?m)^\s*{column}\s+boolean", prefs_sql) is not None,
            f"notification_preferences declares no {column} column for the "
            f"category {category!r}",
        )
    report.check(
        categories.get(CONSTRAINED_TRUE_CATEGORY, {}).get("const")
        == CONSTRAINED_TRUE_CATEGORY,
        "the security event type does not map to the security category, so "
        "whether a security notice can be muted depends on the mapping rather "
        "than on the constrained-true flag",
    )
    report.check(
        preferences.get(f"{CONSTRAINED_TRUE_CATEGORY}_enabled", {}).get("const")
        is True,
        "the security preference flag is not constrained true",
    )

    sql_codes = check_vocabulary(
        bodies.get("notifications", ""), "retraction_reason_code"
    )
    schema_codes = set(defs["retraction"]["properties"]["reason_code"]["enum"])
    report.check(
        sql_codes == schema_codes == set(RETRACTION_CODES),
        "notifications.retraction_reason_code and the retraction enum do not carry "
        f"the same registered codes: only-in-sql={sorted(sql_codes - schema_codes)} "
        f"only-in-schema={sorted(schema_codes - sql_codes)}",
    )

    operations = {
        candidate["operationId"]
        for item in spec["paths"].values()
        for method, candidate in item.items()
        if method.lower() in {"get", "post", "put", "patch", "delete"}
    }
    for operation_id in ("getNotificationPreferences", "updateNotificationPreferences"):
        report.check(
            operation_id in operations,
            f"the API declares no {operation_id}: notification_preferences is a "
            "table a participant can neither read nor set",
        )
    update = spec["components"]["schemas"].get("NotificationPreferencesUpdate") or {}
    report.check(
        "security_enabled" not in (update.get("properties") or {}),
        "NotificationPreferencesUpdate accepts security_enabled: a field a client "
        "may send and the server must refuse is a control that appears to work",
    )


def main() -> int:
    report = Report()
    try:
        spec = load_yaml(OPENAPI)
        registry = load_json(REGISTRY)
        bodies = table_bodies(SQL_PATH.read_text(encoding="utf-8"))
        check_boards(report, spec, registry, bodies)
        check_board_creation_plan(report)
        check_presence(report, spec, bodies)
        check_presence_merge(report)
        check_notifications(report, spec, bodies)
    except Failure as error:
        print(f"social surface contract validation: ERROR: {error}")
        return 2

    if report.errors:
        print("social surface contract validation: FAIL")
        for message in report.errors:
            print(f"- {message}")
        print(
            f"social surface contract validation: FAIL ({len(report.errors)} defect(s))"
        )
        return 1
    print("social surface contract validation: pass")
    print(
        "claim_scope=record-agreement-only; no board is created, no pulse is "
        "admitted and no notification is delivered by anything checked here"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
