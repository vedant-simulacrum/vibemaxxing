#!/usr/bin/env python3
"""The challenge, the batch and the gap declaration say the same thing in every artifact.

ADR-007's own consequence clause states the acceptance test for itself:

    "`vibeproof-claim-v1.cddl`, OpenAPI, SQL planning DDL, reason codes, and
    conformance cases must match this ADR."

Nothing checked it. `grep -n "ADR-007\\|ClaimChallenge\\|batch_commitment\\|atomic-batch-result"
scripts/repository/*.py` returned nothing before this file existed, which is how five
divergences of the following size survived a green `doctor.py` for the length of the
planning program:

* the challenge was defined three times over **disjoint** field sets. The CDDL bound the
  expected next sequence, the expected local head and the expected checkpoint; the DDL
  stored none of the three; the API published a `batch_commitment` neither of the others
  carried and no `lineage_id` at all. `VIBEPROOF_V1_PROTOCOL.md` says the server "verifies
  challenge ownership, expiry, expected tuple and single use", and the expected tuple was
  persisted nowhere, so that verification had nothing to read;
* nothing signed identified a claim's batch, index or position, so ADR-007's rejection of
  "missing indices, duplicate indices, changed order" could only be applied to the
  unsigned outer envelope the submitter writes;
* partial acceptance was prohibited in prose by three documents and constrained by nothing
  in any schema;
* the "bounded signed gap declaration" had a CBOR shape and no signed wrapper, no carrier,
  no table and no enforced bound;
* `policy-defaults-v1.json` set `batch_max_claims` to 500 while the grammar admitted 256
  and the negative corpus refused 257.

Each check below is a comparison between two or more authorities, so it fails when either
side moves. None of them proves the protocol is correct; they prove the artifacts agree,
which is the property that was absent. A green run here says the CDDL, the DDL, the API,
`policy-defaults-v1.json` and ADR-007 state one rule, not that the rule is a good one and
not that any code implements it.
"""

from __future__ import annotations

import json
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
POLICY = SCHEMAS / "policy-defaults-v1.json"
ADR = ROOT / "docs" / "decisions" / "ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md"
PROTOCOL = ROOT / "docs" / "architecture" / "VIBEPROOF_V1_PROTOCOL.md"


class Failure(Exception):
    """Two authorities describe the same rule differently."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


# ---------------------------------------------------------------------------
# The challenge, field for field
# ---------------------------------------------------------------------------

# `challenge-v1` label -> (`claim_challenges` column, `ClaimChallenge` property).
# Label 0 is the protocol major and is checked separately: it is a wire constant, the
# DDL is versioned by migration and the API by path, so it is the one field that
# legitimately exists in one authority only.
CHALLENGE_BINDING: dict[int, tuple[str, str]] = {
    1: ("challenge_id", "challenge_id"),
    2: ("account_pseudonym", "account_pseudonym"),
    3: ("lineage_id", "lineage_id"),
    4: ("nonce", "nonce"),
    5: ("expected_next_sequence", "expected_next_sequence"),
    6: ("expected_local_commitment_head", "expected_local_commitment_head"),
    7: ("expected_checkpoint_receipt_id", "expected_checkpoint_receipt_id"),
    8: ("issued_at", "issued_at"),
    9: ("expires_at", "expires_at"),
    10: ("max_batch_claims", "max_batch_claims"),
    11: ("max_encoded_bytes", "max_encoded_bytes"),
}

# Columns `claim_challenges` carries that the bound tuple does not, each with the reason
# it is server-side only. This is the half that stops the check above being satisfied by
# addition: a twelfth column appearing here with no recorded reason fails, so a field
# cannot be added to the persistence side alone the way `batch_commitment` was added to
# the API side alone.
CHALLENGE_SERVER_ONLY_COLUMNS: dict[str, str] = {
    "account_id": (
        "The server's own account key. The wire carries `account_pseudonym`, which is "
        "what the device signs; the internal identifier never crosses the boundary."
    ),
    "device_id": (
        "Audit and attribution: which device row asked. A challenge is answered by the "
        "lineage, so this is deliberately not part of the bound tuple and the CDDL "
        "challenge carries no device at all."
    ),
    "consumed_by_batch_id": (
        "ADR-007: a challenge is consumed only when the full batch commits, and cannot "
        "authorize multiple batches. Consumption is server state after the fact, not "
        "part of what the challenge binds."
    ),
    "consumed_at": "The other half of consumption, constrained to move with it.",
}

# `claim_batches.outcome` -> (`atomic-batch-result-v1` label 2 ordinal, `ClaimBatchResult.state`).
# Six wire outcomes, two published states. The mapping is declared because it is not the
# identity: an API reader who assumed one state per ordinal would publish four values the
# schema does not admit, and a reader who assumed two ordinals would drop four.
BATCH_OUTCOMES: dict[str, tuple[int, str]] = {
    "committed": (0, "accepted"),
    "idempotent-replay": (1, "accepted"),
    "conflict": (2, "rejected"),
    "rejected": (3, "rejected"),
    "quarantined": (4, "rejected"),
    "retryable": (5, "rejected"),
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


def sql_check_values(body: str, column: str) -> list[str]:
    """The literal list of a `check (column in ('a','b'))` constraint, in order."""
    match = re.search(rf"{column} in \(([^)]*)\)", body)
    if not match:
        raise Failure(f"no `check ({column} in (...))` constraint to read")
    return re.findall(r"'([^']*)'", match.group(1))


def sql_between(body: str, column: str) -> tuple[int, int]:
    match = re.search(rf"{column} between (\d+) and (\d+)", body)
    if not match:
        raise Failure(f"no `check ({column} between N and M)` constraint to read")
    return int(match.group(1)), int(match.group(2))


def cddl_range(expression: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)\.\.(\d+)", expression.strip())
    if not match:
        raise Failure(f"{expression!r} is not an inclusive integer range")
    return int(match.group(1)), int(match.group(2))


def cddl_array(expression: str) -> tuple[int, int | None, str]:
    """`[1*256 rule]` -> (1, 256, "rule"); `[* rule]` -> (0, None, "rule")."""
    inner = expression.strip()[1:-1].strip()
    match = re.fullmatch(r"(?:(\d*)\*(\d*)|(\*))\s*(.+)", inner)
    if match is None:
        raise Failure(f"{expression!r} is not an occurrence-bounded array")
    low = int(match.group(1)) if match.group(1) else 0
    high = int(match.group(2)) if match.group(2) else None
    return low, high, match.group(4).strip()


def cddl_alternatives(body: str) -> list[str]:
    return cddl_instance._split_top_level(body, "/")


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_challenge_is_one_definition(
    bodies: dict[str, str], tables: dict[str, str], api: dict
) -> None:
    labels = cddl_instance.map_entries(bodies["challenge-v1"])
    require(
        labels.get("0" if "0" in labels else 0) == "1",
        "challenge-v1 label 0 is not the protocol major constant 1",
    )
    declared = set(CHALLENGE_BINDING)
    require(
        set(labels) - {0} == declared,
        "challenge-v1 binds labels this validator's three-way table does not: "
        f"only-in-cddl={sorted(set(labels) - {0} - declared)} "
        f"only-in-table={sorted(declared - set(labels))}",
    )

    columns = set(sql_columns(tables["claim_challenges"]))
    bound_columns = {column for column, _ in CHALLENGE_BINDING.values()}
    expected = bound_columns | set(CHALLENGE_SERVER_ONLY_COLUMNS)
    require(
        columns == expected,
        "claim_challenges does not persist exactly the challenge tuple plus its "
        f"recorded server-only columns: only-in-sql={sorted(columns - expected)} "
        f"only-in-binding={sorted(expected - columns)}. A column with no entry in "
        "CHALLENGE_BINDING or CHALLENGE_SERVER_ONLY_COLUMNS is a field one authority "
        "carries and the others do not, which is the defect SR-007 names",
    )
    for column, reason in CHALLENGE_SERVER_ONLY_COLUMNS.items():
        require(
            bool(reason.strip()),
            f"claim_challenges.{column} is excluded from the bound tuple with no reason",
        )
        require(
            column not in bound_columns,
            f"claim_challenges.{column} is recorded as server-only and is also bound",
        )

    schema = api["components"]["schemas"]["ClaimChallenge"]
    properties = set(schema["properties"])
    bound_properties = {prop for _, prop in CHALLENGE_BINDING.values()}
    require(
        properties == bound_properties,
        "ClaimChallenge does not project exactly the challenge tuple: "
        f"only-in-api={sorted(properties - bound_properties)} "
        f"only-in-binding={sorted(bound_properties - properties)}",
    )
    require(
        set(schema["required"]) == bound_properties,
        "ClaimChallenge publishes an optional member of the bound tuple: "
        f"{sorted(bound_properties - set(schema['required']))}",
    )
    require(
        schema.get("additionalProperties") is False,
        "ClaimChallenge does not close its property set, so a fourth definition of the "
        "challenge can be introduced by a server that sends more",
    )

    request = api["components"]["schemas"]["ClaimChallengeRequest"]
    client_chosen = set(request["properties"]) & bound_properties
    require(
        not client_chosen,
        "ClaimChallengeRequest lets the client propose part of the bound tuple: "
        f"{sorted(client_chosen)}. Public evidence status and the state a batch is "
        "verified against are server-assigned",
    )


def check_batch_commitment_is_gone(api: dict, tables: dict[str, str]) -> None:
    """D-626. The field existed in one artifact and could not be computed in any.

    Every claim in a batch signs the challenge nonce, so the batch bytes depend on the
    challenge; a commitment to those bytes required by the challenge *request* therefore
    depended on a value that did not yet exist. It is removed rather than propagated to
    the other two, and the removal is asserted here so it cannot come back into one
    artifact alone, which is exactly how it arrived.

    Property and column names are read rather than raw file text. A grep would be
    satisfied by this sentence, and a check a comment can fail is one the next author
    learns to weaken.
    """
    offenders = [
        f"{name}.{prop}"
        for name, schema in api["components"]["schemas"].items()
        for prop in (schema.get("properties") or {})
        if prop == "batch_commitment"
    ]
    offenders += [
        f"{table}.batch_commitment"
        for table, body in tables.items()
        if "batch_commitment" in sql_columns(body)
    ]
    require(
        not offenders,
        f"`batch_commitment` is declared by {offenders}. A challenge cannot bind a "
        "digest of the batch it authorizes, because every claim in that batch signs "
        "the challenge nonce; one-challenge-one-batch is enforced by single-use "
        "consumption in `claim_challenges`, not by a pre-commitment. The CDDL is not "
        "scanned because a CDDL field name is a comment, and the exact label set of "
        "`challenge-v1` is already required above"
    )


def check_batch_position_is_signed(
    bodies: dict[str, str], tables: dict[str, str], policies: dict
) -> int:
    claim = cddl_instance.map_entries(bodies["vibeproof-claim-v1"])
    for label, name in (
        (31, "batch_id"),
        (32, "batch_index"),
        (33, "batch_claim_count"),
    ):
        require(
            label in claim,
            f"vibeproof-claim-v1 declares no label {label} ({name}), so a claim's "
            "position in its batch is not signed and ADR-007's rejection of missing, "
            "duplicate and reordered indices can only be applied to the unsigned "
            "`batch-context` the submitter writes",
        )

    context = cddl_instance.map_entries(bodies["batch-context"])
    _, maximum, element = cddl_array(context[4])
    require(
        element == "cose-sign1-claim-v1" and maximum is not None,
        "batch-context label 4 is not a bounded array of signed claims",
    )
    ceiling = maximum

    require(
        cddl_range(claim[32]) == (0, ceiling - 1),
        f"vibeproof-claim-v1 label 32 is {claim[32]!r}; batch-context admits {ceiling} "
        f"claims, so the zero-based index runs 0..{ceiling - 1}",
    )
    require(
        cddl_range(claim[33]) == (1, ceiling),
        f"vibeproof-claim-v1 label 33 is {claim[33]!r}, which disagrees with the "
        f"{ceiling}-claim batch bound",
    )
    challenge = cddl_instance.map_entries(bodies["challenge-v1"])
    require(
        cddl_range(challenge[10]) == (1, ceiling),
        f"challenge-v1 label 10 is {challenge[10]!r}: a challenge that may authorize "
        f"more than {ceiling} claims authorizes a batch that cannot be encoded",
    )

    claims = tables["claims"]
    require(
        sql_between(claims, "batch_index") == (0, ceiling - 1),
        "claims.batch_index does not match the signed range",
    )
    require(
        sql_between(claims, "batch_claim_count") == (1, ceiling),
        "claims.batch_claim_count does not match the signed range",
    )
    require(
        sql_between(tables["claim_batches"], "claim_count") == (1, ceiling),
        "claim_batches.claim_count does not match the signed range",
    )
    require(
        sql_between(tables["claim_challenges"], "max_batch_claims") == (1, ceiling),
        "claim_challenges.max_batch_claims does not match the signed range",
    )
    require(
        "unique (batch_id, batch_index)" in claims,
        "claims does not refuse a duplicate batch index, so ADR-007's `duplicate "
        "indices` rejection has no constraint behind it",
    )

    default = policies["batch_max_claims"]
    require(
        default["value"] == ceiling and default["max"] == ceiling,
        f"policy-defaults-v1.json sets batch_max_claims to value={default['value']} "
        f"max={default['max']} while the grammar admits {ceiling} and the negative "
        f"corpus refuses {ceiling + 1}. A configurable ceiling above the encodable one "
        "is a limit that cannot be reached and a rejection reason that cannot be "
        "explained",
    )
    return ceiling


def check_partial_acceptance_is_unrepresentable(
    bodies: dict[str, str], tables: dict[str, str], api: dict, ceiling: int
) -> None:
    alternatives = cddl_alternatives(bodies["atomic-batch-result-v1"])
    require(
        len(alternatives) == 2,
        "atomic-batch-result-v1 is not a two-way choice, so one map carries both a "
        "batch outcome and independent per-claim outcomes and partial acceptance "
        f"encodes; it has {len(alternatives)} alternative(s)",
    )
    committed, refused = (cddl_instance.map_entries(arm) for arm in alternatives)

    committed_range = cddl_range(committed[2])
    refused_range = cddl_range(refused[2])
    require(
        committed_range[0] == 0 and refused_range[0] == committed_range[1] + 1,
        f"the batch outcome ordinals {committed_range} and {refused_range} are not "
        "contiguous, so an ordinal belongs to both arms or to neither",
    )
    ordinals = {ordinal for ordinal, _ in BATCH_OUTCOMES.values()}
    require(
        ordinals == set(range(committed_range[0], refused_range[1] + 1)),
        "BATCH_OUTCOMES does not enumerate exactly the ordinals the two arms admit",
    )

    for arm, expected_rule, label in (
        (committed, "claim-accepted-result-v1", "committed"),
        (refused, "claim-refused-result-v1", "refused"),
    ):
        low, high, element = cddl_array(arm[4])
        require(
            element == expected_rule,
            f"the {label} batch result admits {element!r} per-claim results rather than "
            f"{expected_rule!r}; a mixed list is what partial acceptance is",
        )
        require(
            (low, high) == (1, ceiling),
            f"the {label} batch result admits {low}..{high} per-claim results; a batch "
            f"holds 1..{ceiling} claims and each one is accounted for",
        )
    _, receipt_maximum, _ = cddl_array(refused[5])
    require(
        receipt_maximum == 0,
        "a refused batch may carry a checkpoint receipt; a receipt acknowledges an "
        "accepted head and a refused batch advanced no head",
    )

    accepted = cddl_instance.map_entries(bodies["claim-accepted-result-v1"])
    require(
        accepted[3] == "uuid7",
        f"an accepted claim result's appraisal reference is {accepted[3]!r}; an "
        "acceptance with no appraisal leaves the participant nothing to appeal",
    )
    refused_result = cddl_instance.map_entries(bodies["claim-refused-result-v1"])
    require(
        refused_result[3] == "nil",
        "a refused claim result may carry an appraisal reference",
    )
    reason_low, _, _ = cddl_array(refused_result[2])
    require(
        reason_low >= 1,
        "a refused claim result may carry an empty reason list, which is a refusal "
        "that explains nothing",
    )

    batches = tables["claim_batches"]
    require(
        sql_check_values(batches, "outcome") == list(BATCH_OUTCOMES),
        "claim_batches.outcome does not enumerate the six wire outcomes in ordinal "
        f"order: {sql_check_values(batches, 'outcome')}",
    )
    committed_names = {
        name for name, (_, state) in BATCH_OUTCOMES.items() if state == "accepted"
    }
    refused_names = set(BATCH_OUTCOMES) - committed_names
    require(
        set(sql_check_values(tables["claims"], "batch_outcome")) == committed_names,
        "claims may attach to a batch outcome that did not commit",
    )
    require(
        set(sql_check_values(tables["claim_rejections"], "batch_outcome"))
        == refused_names,
        "claim_rejections may attach to a batch outcome that committed, which is "
        "'batch accepted, claims 3 and 7 rejected' with a row to store it in",
    )
    for table in ("claims", "claim_rejections"):
        require(
            "foreign key (batch_id, batch_outcome) references claim_batches (batch_id, outcome)"
            in " ".join(tables[table].split()),
            f"{table} does not reference the batch at its outcome, so the outcome "
            "column is a comment rather than a constraint",
        )
    require(
        "unique (batch_id, outcome)" in batches,
        "claim_batches offers no (batch_id, outcome) key, so the composite foreign "
        "keys above cannot be declared",
    )

    result = api["components"]["schemas"]["ClaimBatchResult"]
    states = set(result["properties"]["state"]["enum"])
    require(
        states == {state for _, state in BATCH_OUTCOMES.values()},
        f"ClaimBatchResult.state publishes {sorted(states)}, which is not the image of "
        "the six wire outcomes",
    )
    arms = result.get("oneOf")
    require(
        isinstance(arms, list) and len(arms) == 2,
        "ClaimBatchResult states no mutual exclusion, so a response meaning 'batch "
        "accepted, claims 3 and 7 rejected' is a valid instance of the published "
        "schema, which it was until PF-070",
    )
    by_state = {arm["properties"]["state"]["const"]: arm["properties"] for arm in arms}
    require(
        set(by_state) == states,
        f"the ClaimBatchResult arms cover {sorted(by_state)} of {sorted(states)}",
    )
    require(
        by_state["accepted"]["rejections"]["maxItems"] == 0,
        "an accepted ClaimBatchResult may carry rejections",
    )
    require(
        by_state["rejected"]["accepted_claim_ids"]["maxItems"] == 0,
        "a rejected ClaimBatchResult may carry accepted claims",
    )
    require(
        by_state["rejected"]["checkpoint_receipt"]["type"] == "null",
        "a rejected ClaimBatchResult may carry a checkpoint receipt",
    )


def check_gap_declaration_is_signed_carried_stored_and_bounded(
    bodies: dict[str, str], tables: dict[str, str], policies: dict, adr: str
) -> None:
    require(
        "cose-sign1-gap-v1" in bodies,
        "there is no COSE wrapper for a gap declaration, so ADR-007's `signed "
        "gap-declaration` and D-043's `bounded signed gap declarations` name something "
        "nothing can sign",
    )
    headers = cddl_instance.map_entries(bodies["protected-headers-gap-v1"])
    require(
        headers[3] == '"application/vibemaxxing-gap+cbor"',
        f"the gap protected headers pin {headers[3]!r} as their content type; a COSE "
        "message with no content type is one an attacker can present as another kind",
    )

    claim = cddl_instance.map_entries(bodies["vibeproof-claim-v1"])
    require(
        claim.get(34) == "digest32 / nil",
        "vibeproof-claim-v1 carries no gap declaration commitment, so ADR-007's "
        "`included in the first claim after the gap` has no slot and a declaration "
        "reaches the server bound to nothing the device signed",
    )
    context = cddl_instance.map_entries(bodies["batch-context"])
    require(
        cddl_array(context[5])[2] == "cose-sign1-gap-v1",
        "batch-context carries no signed gap declarations, so the bytes the claim "
        "commits to have no transport",
    )

    causes = re.search(r"Allowed reasons are ([^.]+)\.", adr)
    require(causes is not None, "ADR-007 no longer states the allowed gap reasons")
    names = [
        part.strip().replace(" ", "-")
        for part in re.split(r",\s*and\s+|\s+and\s+|,\s*", causes.group(1))
        if part.strip()
    ]
    require(
        cddl_range(cddl_instance.map_entries(bodies["gap-declaration"])[7])
        == (0, len(names) - 1),
        f"gap-declaration label 7 does not admit exactly the {len(names)} causes "
        "ADR-007 registers; a representable ordinal with no registered meaning is a "
        "declaration the grammar accepts and no policy resolves",
    )
    declarations = tables["gap_declarations"]
    require(
        sql_check_values(declarations, "cause") == names,
        "gap_declarations.cause does not enumerate ADR-007's causes in ordinal order: "
        f"{sql_check_values(declarations, 'cause')} against {names}",
    )

    stated = re.search(r"maximum recoverable gap is ([\d,]+) sequences", adr)
    require(stated is not None, "ADR-007 no longer states a maximum recoverable gap")
    bound = int(stated.group(1).replace(",", ""))
    match = re.search(
        r"check \(sequence_after_gap - sequence_before_gap - 1 <= (\d+)\)", declarations
    )
    require(
        match is not None and int(match.group(1)) == bound,
        f"gap_declarations does not refuse a gap wider than the {bound} sequences "
        "ADR-007 allows. The bound is a relation between two labels and CDDL has no "
        "control for the difference of two, so if it is not here it is nowhere",
    )
    require(
        "max_recoverable_gap_sequences" in policies
        and policies["max_recoverable_gap_sequences"]["value"] == bound,
        "policy-defaults-v1.json does not carry the recoverable-gap bound, or carries "
        f"a different one from ADR-007's {bound}",
    )
    require(
        "first_post_gap_claim_id uuid not null unique" in declarations,
        "gap_declarations does not tie a declaration to exactly one first post-gap "
        "claim, so one gap could be declared twice or claimed by two claims",
    )


def check_adr_still_states_what_this_derives_from(adr: str, protocol: str) -> None:
    """Every derivation above reads ADR-007's words. If they change, this is stale."""
    for phrase in (
        "maximum claim count, and maximum encoded bytes",
        "missing indices, duplicate indices, changed order",
        "Partial batch acceptance is prohibited in protocol v1.",
    ):
        require(
            phrase in adr,
            f"ADR-007 no longer states {phrase!r}; the checks derived from it are stale "
            "and would keep passing against a rule the ADR has stopped making",
        )
    require(
        "never partial success" in protocol,
        "VIBEPROOF_V1_PROTOCOL.md no longer refuses partial success",
    )


def main() -> int:
    cddl_text = CDDL.read_text(encoding="utf-8")
    sql_text = SQL.read_text(encoding="utf-8")
    openapi_text = OPENAPI.read_text(encoding="utf-8")
    adr_text = ADR.read_text(encoding="utf-8")
    protocol_text = PROTOCOL.read_text(encoding="utf-8")

    bodies = cddl_instance.rule_bodies(cddl_text)
    tables = sql_table_bodies(sql_text)
    api = yaml.safe_load(openapi_text)
    policies = json.loads(POLICY.read_text(encoding="utf-8"))["policies"]

    # Ordered so the specific diagnosis wins: `batch_commitment` reappearing anywhere
    # would otherwise be reported as a generic field-set mismatch, which names the
    # symptom rather than the field and the reason it cannot exist.
    check_batch_commitment_is_gone(api, tables)
    check_challenge_is_one_definition(bodies, tables, api)
    ceiling = check_batch_position_is_signed(bodies, tables, policies)
    check_partial_acceptance_is_unrepresentable(bodies, tables, api, ceiling)
    check_gap_declaration_is_signed_carried_stored_and_bounded(
        bodies, tables, policies, adr_text
    )
    check_adr_still_states_what_this_derives_from(adr_text, protocol_text)

    print("batch and challenge binding: pass")
    print(
        f"challenge={len(CHALLENGE_BINDING)} fields three-way, "
        f"{len(CHALLENGE_SERVER_ONLY_COLUMNS)} server-only columns each with a reason"
    )
    print(
        f"batch={ceiling} claims, outcomes={len(BATCH_OUTCOMES)} wire onto 2 published"
    )
    print(
        "claim_scope=artifact-agreement-only; agreeing artifacts are not a correct "
        "protocol, and no implementation reads any of them"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as failure:
        print(f"batch and challenge binding: FAIL — {failure}", file=sys.stderr)
        sys.exit(1)
