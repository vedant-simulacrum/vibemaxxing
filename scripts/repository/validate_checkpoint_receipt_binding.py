#!/usr/bin/env python3
"""The checkpoint receipt says the same thing in the CDDL, the DDL and the API.

D-043's sixth and last recorded divergence, and the one PF-070 deliberately left open
because it is a receipt-shape defect rather than a challenge or batch one:

* `checkpoint-receipt-v1` bound twelve labels and `checkpoint_receipts` stored nine
  columns, and the two sets were near-disjoint. The account pseudonym, the accepted
  local commitment head, the last accepted claim digest, the verifier policy, the issue
  and expiry times and the server signing key id were all signed on the wire and stored
  by no column. The one concept the two shared was stored under the name
  `last_sequence`, which neither the wire nor the protocol document uses;
* `server_receipt_sequence` — CDDL label 7, and one of the five items
  `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` lists as server state — was defined in
  exactly one artifact in this repository and stored nowhere.
  `grep -rn server_receipt_sequence packages/ docs/ conformance/` returned one line, the
  CDDL declaration itself. A monotonic counter that the protocol attributes to the
  server, with no column in the only place server state is kept, is not a counter;
* `openapi-v1.yaml` had no `CheckpointReceipt` component at all.
  `ClaimBatchResult.checkpoint_receipt` was `string, base64, maxLength 4096` — an opaque
  blob projecting zero of the twelve labels — so a client could read none of the fields
  the server signed without a CBOR decoder and a copy of the CDDL.

ADR-007 is silent on receipts. `grep -in 'checkpoint\\|receipt'` over
`docs/decisions/ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md` matches nothing, so
unlike PF-070 there is no ADR consequence clause to derive a bound from and none is
invented here. `VIBEPROOF_V1_PROTOCOL.md` is the sole prose authority for what the
receipt acknowledges and what server state is, and its sentences are parsed rather than
restated: `check_protocol_still_names_server_state` reads the server-state bullet and
requires a column for every item in it, so the check cannot outlive its premise and
cannot be satisfied by a sentence this file happens to quote.

`docs/security/INTEGRITY_MODEL.md` owns the newest-wins rule and names the constraint
that carries it. The constraint name is read from that document, so renaming the column
in the DDL without repairing the document fails here rather than leaving the owner of
the rule pointing at a constraint that no longer exists — which is what the previous
`last_sequence` name did across five files.

Every check below compares two or more authorities and fails when either side moves. A
green run says the CDDL, the DDL, the API and the two documents state one shape. It does
not say the shape is correct, and nothing in this repository implements it: no verifier
issues a receipt, no handler writes one of these rows, and no client reads the component.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cddl_instance  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
CDDL = SCHEMAS / "vibeproof-claim-v1.cddl"
SQL = SCHEMAS / "planning-schema.sql"
OPENAPI = SCHEMAS / "openapi-v1.yaml"
PROTOCOL = ROOT / "docs" / "architecture" / "VIBEPROOF_V1_PROTOCOL.md"
INTEGRITY = ROOT / "docs" / "security" / "INTEGRITY_MODEL.md"

TABLE = "checkpoint_receipts"
COMPONENT = "CheckpointReceipt"
CARRIER = "ClaimBatchResult"


class Failure(Exception):
    """Two authorities describe the same receipt differently."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


# ---------------------------------------------------------------------------
# The receipt, field for field
# ---------------------------------------------------------------------------

# `checkpoint-receipt-v1` label -> (`checkpoint_receipts` column, `CheckpointReceipt`
# property). Eleven of the twelve labels; label 0 is declared wire-only below.
#
# Two labels are stored under a different name and both renames are deliberate. Label 1
# is `receipt_id` on the wire and `checkpoint_receipt_id` in SQL, because
# `claim_challenges.expected_checkpoint_receipt_id` already references it under that
# name. Label 3 is `device_lineage_id` on the wire and `lineage_id` everywhere else,
# which is the same pairing `challenge-v1` label 3 already uses.
RECEIPT_BINDING: dict[int, tuple[str, str]] = {
    1: ("checkpoint_receipt_id", "checkpoint_receipt_id"),
    2: ("account_pseudonym", "account_pseudonym"),
    3: ("lineage_id", "lineage_id"),
    4: ("accepted_through_claim_sequence", "accepted_through_claim_sequence"),
    5: ("accepted_local_commitment_head", "accepted_local_commitment_head"),
    6: ("last_accepted_claim_sha256", "last_accepted_claim_sha256"),
    7: ("server_receipt_sequence", "server_receipt_sequence"),
    8: ("verifier_policy_id", "verifier_policy_id"),
    9: ("issued_at", "issued_at"),
    10: ("expires_at", "expires_at"),
    11: ("server_signing_key_id", "server_signing_key_id"),
}

# Labels the wire carries and neither the DDL nor the API stores, each with the reason.
# One entry, and it needs the same discipline as a server-only column: a second wire-only
# label appearing here with no reason is a field being quietly excused from the binding.
RECEIPT_WIRE_ONLY_LABELS: dict[int, str] = {
    0: (
        "The protocol major. The DDL expresses its own version by being the shape it is "
        "and is versioned by migration; the API is versioned by path. A constant "
        "repeated in every row and every response body is a third place the version can "
        "disagree with itself."
    ),
}

# Columns `checkpoint_receipts` carries that the signed receipt does not, each with the
# reason it is server-side only. This is the half that stops the binding being satisfied
# by addition: a column appearing with no recorded reason fails, so a field cannot be
# added to the persistence side alone.
RECEIPT_SERVER_ONLY_COLUMNS: dict[str, str] = {
    "device_id": (
        "Which device row presented the batch. The receipt is lineage-scoped on the wire "
        "because continuity is lineage-scoped under PF-009, and the device is "
        "operational attribution the participant is not asked to carry."
    ),
    "first_sequence": (
        "The batch's lower bound. The receipt acknowledges a head; the server records "
        "the span that produced it, which is what makes the difference between a batch "
        "that advanced one claim and one that advanced 256 a stored fact rather than an "
        "inference from the previous row."
    ),
    "batch_digest": (
        "The batch this receipt answered. The device already knows which batch it sent; "
        "the server needs the link to refuse a second receipt for one batch."
    ),
    "previous_receipt_digest": (
        "The chain link, kept server-side. The device carries the previous receipt id on "
        "its claims — `vibeproof-claim-v1` label 9 — and the server keeps the digest it "
        "chains over, so the two sides commit to the chain in different currencies and "
        "neither can rewrite it alone."
    ),
    "signed_receipt": (
        "The COSE bytes themselves. The wire *is* this, so the column stores the "
        "artifact rather than a field of it, and every bound column above is a "
        "projection of these bytes that SQL can index."
    ),
    "created_at": (
        "When the row was written, which is not `issued_at`. The receipt states when the "
        "server says it issued; this states when the transaction landed, and conflating "
        "them would make a signed timestamp the authority for a database fact."
    ),
}

# `VIBEPROOF_V1_PROTOCOL.md` lists five items as server state. Each is mapped to the
# table and column that holds it. The list itself is parsed out of the document rather
# than restated, so an item added to or removed from that sentence fails here; this table
# only says where each item was put.
PROTOCOL_SERVER_STATE: dict[str, tuple[str, str]] = {
    "expected sequence": ("claim_challenges", "expected_next_sequence"),
    "accepted local head": (TABLE, "accepted_local_commitment_head"),
    "last accepted claim digest": (TABLE, "last_accepted_claim_sha256"),
    "prior checkpoint receipt": (TABLE, "previous_receipt_digest"),
    "monotonic receipt sequence": (TABLE, "server_receipt_sequence"),
}


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------


def sql_table_bodies(text: str) -> dict[str, str]:
    bodies: dict[str, str] = {}
    for match in re.finditer(
        r"^create table ([a-z0-9_]+) \((.*?)^\);", text, re.S | re.M
    ):
        bodies[match.group(1)] = match.group(2)
    return bodies


def sql_columns(body: str) -> list[str]:
    columns: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^  ([a-z][a-z0-9_]*)\s+[a-z]", line)
        if match and match.group(1) not in ("constraint", "unique", "foreign", "check"):
            columns.append(match.group(1))
    return columns


def sql_statements(body: str) -> str:
    """The table body with comment lines removed and whitespace flattened.

    Constraints are matched against this rather than against the raw text, so a
    constraint written into a `--` comment does not satisfy a check, and one wrapped
    across two lines still does.
    """
    lines = [line for line in body.splitlines() if not line.strip().startswith("--")]
    return " ".join(" ".join(lines).split())


def markdown_bullet(text: str, lead: str) -> str:
    """The body of the `- <lead>: ...` bullet, or a failure naming what is missing."""
    match = re.search(rf"^- {re.escape(lead)}:(.+?)[.;]$", text, re.M)
    require(
        match is not None,
        f"{PROTOCOL.name} no longer carries a `- {lead}:` bullet. Every derivation below "
        "reads that sentence, so its absence would leave this file checking a rule the "
        "document has stopped making",
    )
    assert match is not None
    return match.group(1).strip()


def split_prose_list(text: str) -> list[str]:
    parts = re.split(r",\s*and\s+|\s+and\s+|,\s*", text)
    return [part.strip() for part in parts if part.strip()]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_receipt_is_one_definition(
    bodies: dict[str, str], tables: dict[str, str], api: dict
) -> None:
    """The three field sets are the same field set, in both directions."""
    labels = cddl_instance.map_entries(bodies["checkpoint-receipt-v1"])
    require(
        labels.get(0) == "1",
        "checkpoint-receipt-v1 label 0 is not the protocol major constant 1",
    )
    declared = set(RECEIPT_BINDING) | set(RECEIPT_WIRE_ONLY_LABELS)
    require(
        set(labels) == declared,
        "checkpoint-receipt-v1 binds labels this validator's three-way table does not: "
        f"only-in-cddl={sorted(set(labels) - declared)} "
        f"only-in-table={sorted(declared - set(labels))}",
    )
    for label, reason in RECEIPT_WIRE_ONLY_LABELS.items():
        require(
            bool(reason.strip()),
            f"checkpoint-receipt-v1 label {label} is excluded from the binding with no "
            "recorded reason",
        )
        require(
            label not in RECEIPT_BINDING,
            f"checkpoint-receipt-v1 label {label} is recorded as wire-only and is also "
            "bound to a column",
        )

    require(
        TABLE in tables,
        f"planning-schema.sql declares no `{TABLE}` table, so the receipt the server "
        "signs is persisted nowhere",
    )
    columns = set(sql_columns(tables[TABLE]))
    bound_columns = {column for column, _ in RECEIPT_BINDING.values()}
    expected = bound_columns | set(RECEIPT_SERVER_ONLY_COLUMNS)
    require(
        columns == expected,
        f"{TABLE} does not persist exactly the receipt tuple plus its recorded "
        f"server-only columns: only-in-sql={sorted(columns - expected)} "
        f"only-in-binding={sorted(expected - columns)}. A column with no entry in "
        "RECEIPT_BINDING or RECEIPT_SERVER_ONLY_COLUMNS is a field one authority carries "
        "and the others do not, which is the near-disjoint state D-043 records",
    )
    for column, reason in RECEIPT_SERVER_ONLY_COLUMNS.items():
        require(
            bool(reason.strip()),
            f"{TABLE}.{column} is excluded from the bound tuple with no reason",
        )
        require(
            column not in bound_columns,
            f"{TABLE}.{column} is recorded as server-only and is also bound",
        )

    schemas = api["components"]["schemas"]
    require(
        COMPONENT in schemas,
        f"openapi-v1.yaml declares no `{COMPONENT}` component, so the eleven fields the "
        "server signs reach the client as opaque bytes with no published meaning, which "
        "is the state PF-073 found",
    )
    schema = schemas[COMPONENT]
    properties = set(schema["properties"])
    bound_properties = {prop for _, prop in RECEIPT_BINDING.values()}
    require(
        properties == bound_properties,
        f"{COMPONENT} does not project exactly the receipt tuple: "
        f"only-in-api={sorted(properties - bound_properties)} "
        f"only-in-binding={sorted(bound_properties - properties)}",
    )
    require(
        set(schema["required"]) == bound_properties,
        f"{COMPONENT} publishes an optional member of the bound tuple: "
        f"{sorted(bound_properties - set(schema['required']))}. A receipt missing a "
        "field it signed is one a client cannot verify against the envelope",
    )
    require(
        schema.get("additionalProperties") is False,
        f"{COMPONENT} does not close its property set, so a fourth definition of the "
        "receipt can be introduced by a server that sends more",
    )


def check_server_receipt_sequence_is_stored_and_is_not_the_claim_counter(
    tables: dict[str, str],
) -> None:
    """Label 7, the field that was defined once and stored nowhere."""
    body = sql_statements(tables[TABLE])
    require(
        "unique (lineage_id, server_receipt_sequence)" in body,
        f"{TABLE} offers no `unique (lineage_id, server_receipt_sequence)`. Storing the "
        "counter in a column without it makes the column a number rather than the "
        "monotonic receipt sequence VIBEPROOF_V1_PROTOCOL.md names as server state: two "
        "receipts at one position inside one lineage would insert",
    )
    require(
        "check (server_receipt_sequence >= 0)" in body,
        f"{TABLE} does not refuse a negative `server_receipt_sequence`; the wire type is "
        "`uint64` and SQL `bigint` is signed, so the floor exists in the CDDL and "
        "nowhere else unless it is written here",
    )
    require(
        "unique (lineage_id, accepted_through_claim_sequence)" in body,
        f"{TABLE} offers no `unique (lineage_id, accepted_through_claim_sequence)`, so "
        "two receipts acknowledging the same head inside one lineage insert. That is the "
        "`checkpoint-mismatch` detection basis, and it is a different constraint from "
        "the receipt-sequence one above: one accepted batch advances the claim sequence "
        "by up to 256 and the receipt sequence by exactly one, so a single unique index "
        "cannot carry both rules",
    )
    require(
        "check (accepted_through_claim_sequence >= first_sequence)" in body,
        f"{TABLE} does not refuse an acknowledged head below the span that produced it",
    )
    require(
        "check (expires_at > issued_at)" in body,
        f"{TABLE} admits a receipt that expired before it was issued",
    )


def check_the_api_carries_both_the_projection_and_the_envelope(api: dict) -> None:
    """A client verifies bytes and reads fields, and needs both to do either."""
    schemas = api["components"]["schemas"]
    result = schemas[CARRIER]
    properties = result["properties"]
    for name in ("checkpoint_receipt", "checkpoint_receipt_cose"):
        require(
            name in properties and name in result["required"],
            f"{CARRIER} does not carry a required `{name}`. The projection without the "
            "envelope is unverifiable and the envelope without the projection is "
            "unreadable; publishing one of the two is what this schema did before PF-073",
        )
    referenced = [
        arm.get("$ref")
        for arm in properties["checkpoint_receipt"].get("oneOf", [])
        if isinstance(arm, dict)
    ]
    require(
        f"#/components/schemas/{COMPONENT}" in referenced,
        f"{CARRIER}.checkpoint_receipt does not reference `{COMPONENT}`, so the "
        "component is published and nothing returns it",
    )
    require(
        {"type": "null"} in properties["checkpoint_receipt"]["oneOf"],
        f"{CARRIER}.checkpoint_receipt cannot be null, and a rejected batch has no "
        "receipt to project",
    )
    envelope = properties["checkpoint_receipt_cose"]
    require(
        envelope.get("contentEncoding") == "base64" and "null" in envelope["type"],
        f"{CARRIER}.checkpoint_receipt_cose is not a nullable base64 envelope",
    )

    arms = {
        arm["properties"]["state"]["const"]: arm["properties"]
        for arm in result["oneOf"]
    }
    rejected = arms["rejected"]
    for name in ("checkpoint_receipt", "checkpoint_receipt_cose"):
        require(
            rejected.get(name, {}).get("type") == "null",
            f"a rejected {CARRIER} may carry `{name}`. VIBEPROOF_V1_PROTOCOL.md: a "
            "receipt acknowledges an accepted head, and a rejected batch advanced none",
        )


def check_protocol_still_names_server_state(
    protocol: str, tables: dict[str, str]
) -> list[str]:
    """The bound is read from the document, not restated here.

    `server_receipt_sequence` had no column because nothing compared this sentence to
    the schema. The sentence is parsed, every item in it must be mapped, and every
    mapped column must exist, so the sentence and the tables cannot drift apart in
    either direction.
    """
    items = split_prose_list(markdown_bullet(protocol, "server state"))
    require(
        set(items) == set(PROTOCOL_SERVER_STATE),
        f"{PROTOCOL.name} lists server state this validator has not placed in a column: "
        f"only-in-document={sorted(set(items) - set(PROTOCOL_SERVER_STATE))} "
        f"only-in-validator={sorted(set(PROTOCOL_SERVER_STATE) - set(items))}. Every "
        "item in that sentence is a thing the server is said to keep, and a thing it "
        "keeps in no table it does not keep",
    )
    for item in items:
        table, column = PROTOCOL_SERVER_STATE[item]
        require(
            table in tables and column in sql_columns(tables[table]),
            f"{PROTOCOL.name} lists {item!r} as server state and {table}.{column} does "
            "not exist. That is exactly the defect PF-073 repairs: label 7 named a "
            "monotonic receipt sequence the protocol attributes to the server, and no "
            "column held it",
        )

    for phrase in (
        "A receipt acknowledges only the bound accepted head.",
        "returns server-signed checkpoint receipt(s)",
    ):
        require(
            phrase in protocol,
            f"{PROTOCOL.name} no longer states {phrase!r}; the checks derived from it "
            "are stale and would keep passing against a rule the document has stopped "
            "making",
        )
    return items


def check_the_integrity_model_names_the_constraint_it_owns(
    integrity: str, tables: dict[str, str]
) -> str:
    """The owner of newest-wins names a constraint; that constraint must exist.

    `docs/project/DOCUMENTATION.md` makes INTEGRITY_MODEL.md the owner of the rule and
    the DDL comment defers to it. The constraint text is read out of the document, so a
    column rename in SQL that does not reach the document fails here — which is what
    `last_sequence` did in five files at once before PF-073.
    """
    match = re.search(rf"`(unique \(lineage_id, [a-z_]+\))` on `{TABLE}`", integrity)
    require(
        match is not None,
        f"{INTEGRITY.name} no longer names the `unique (...)` constraint on {TABLE} that "
        "carries the newest-wins rule it owns",
    )
    assert match is not None
    constraint = match.group(1)
    require(
        constraint in sql_statements(tables[TABLE]),
        f"{INTEGRITY.name} names {constraint!r} on {TABLE} and planning-schema.sql does "
        "not declare it. The document that owns the rule is pointing at a constraint "
        "that does not exist",
    )
    return constraint


def main() -> int:
    bodies = cddl_instance.rule_bodies(CDDL.read_text(encoding="utf-8"))
    tables = sql_table_bodies(SQL.read_text(encoding="utf-8"))
    api = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    protocol = PROTOCOL.read_text(encoding="utf-8")
    integrity = INTEGRITY.read_text(encoding="utf-8")

    check_receipt_is_one_definition(bodies, tables, api)
    check_server_receipt_sequence_is_stored_and_is_not_the_claim_counter(tables)
    check_the_api_carries_both_the_projection_and_the_envelope(api)
    state = check_protocol_still_names_server_state(protocol, tables)
    constraint = check_the_integrity_model_names_the_constraint_it_owns(
        integrity, tables
    )

    print("checkpoint receipt binding: pass")
    print(
        f"receipt={len(RECEIPT_BINDING)} fields three-way, "
        f"{len(RECEIPT_SERVER_ONLY_COLUMNS)} server-only columns and "
        f"{len(RECEIPT_WIRE_ONLY_LABELS)} wire-only label each with a reason"
    )
    print(
        f"server_state={len(state)} items read from {PROTOCOL.name}, each with a column; "
        f"newest-wins constraint {constraint} read from {INTEGRITY.name}"
    )
    print(
        "claim_scope=artifact-agreement-only; agreeing artifacts are not a correct "
        "protocol, and no implementation issues, stores or reads a receipt"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as failure:
        print(f"checkpoint receipt binding: FAIL — {failure}", file=sys.stderr)
        sys.exit(1)
