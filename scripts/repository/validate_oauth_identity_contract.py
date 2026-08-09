#!/usr/bin/env python3
"""Decide the SR-006 cluster from the artifacts rather than from their prose.

SR-006 is the contradiction between what `docs/security/AUTHENTICATION_AND_RECOVERY.md`
and `docs/security/RANKED_IDENTITY_ELIGIBILITY.md` require of OAuth, linked identity,
recovery and ranked identity, and what `packages/schemas/openapi-v1.yaml`,
`packages/schemas/planning-schema.sql` and `packages/schemas/state-machine-registry-v1.json`
actually declare. Four stages, one per work unit, each runnable alone with `--stage`:

* `provider-registry` (PF-005) — the preconfigured provider-capability record both
  normative documents assume exists, and the mix-up vectors decided against it.
* `oauth-transaction` (PF-006) — the transaction is the only route by which a
  callback may change identity, and it binds everything the callback must not choose.
* `linked-identity` (PF-007) — the linked identity has a lifecycle, a durable subject
  and a last-method invariant, rather than three states and an open question.
* `ranked-identity` (PF-008) — the consolidation plan covers every domain a duplicate
  account owns, and no surface publishes a combined figure for two of them.

What this proves is agreement between records. Nothing here executes an authorization
request, a callback, a recovery, a consolidation or any server code, because none
exists. A green run means the contracts say one thing; it is not evidence that any of
it works.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
CONFORMANCE = ROOT / "conformance"

REGISTRY_PATH = SCHEMAS / "oauth-provider-registry-v1.json"
REGISTRY_SCHEMA_PATH = SCHEMAS / "oauth-provider-registry-v1.schema.json"
MIXUP_PATH = CONFORMANCE / "auth" / "provider-mixup-vectors-v1.json"
SQL_PATH = SCHEMAS / "planning-schema.sql"
OPENAPI_PATH = SCHEMAS / "openapi-v1.yaml"
MACHINES_PATH = SCHEMAS / "state-machine-registry-v1.json"
REASONS_PATH = SCHEMAS / "reason-codes-v1.json"
CONSOLIDATION_SCHEMA_PATH = SCHEMAS / "consolidation-plan-v1.schema.json"
AUTH_DOC = ROOT / "docs" / "security" / "AUTHENTICATION_AND_RECOVERY.md"
RANKED_DOC = ROOT / "docs" / "security" / "RANKED_IDENTITY_ELIGIBILITY.md"

FORMAT_CHECKER = FormatChecker()
MAX_REVIEW_WINDOW = timedelta(days=365)


def bind_root(root: Path) -> None:
    """Repoint every path constant at another checkout.

    The drift-injection tests mutate a full copy of the tree and run the stages
    against it. Without one function that rebinds every path, a test would set `ROOT`
    and silently keep reading the real repository through the constants derived from
    it, which is a test that passes by not looking at what it broke.
    """
    global ROOT, SCHEMAS, CONFORMANCE
    global REGISTRY_PATH, REGISTRY_SCHEMA_PATH, MIXUP_PATH, SQL_PATH, OPENAPI_PATH
    global MACHINES_PATH, REASONS_PATH, CONSOLIDATION_SCHEMA_PATH, AUTH_DOC, RANKED_DOC
    ROOT = root
    SCHEMAS = root / "packages" / "schemas"
    CONFORMANCE = root / "conformance"
    REGISTRY_PATH = SCHEMAS / "oauth-provider-registry-v1.json"
    REGISTRY_SCHEMA_PATH = SCHEMAS / "oauth-provider-registry-v1.schema.json"
    MIXUP_PATH = CONFORMANCE / "auth" / "provider-mixup-vectors-v1.json"
    SQL_PATH = SCHEMAS / "planning-schema.sql"
    OPENAPI_PATH = SCHEMAS / "openapi-v1.yaml"
    MACHINES_PATH = SCHEMAS / "state-machine-registry-v1.json"
    REASONS_PATH = SCHEMAS / "reason-codes-v1.json"
    CONSOLIDATION_SCHEMA_PATH = SCHEMAS / "consolidation-plan-v1.schema.json"
    AUTH_DOC = root / "docs" / "security" / "AUTHENTICATION_AND_RECOVERY.md"
    RANKED_DOC = root / "docs" / "security" / "RANKED_IDENTITY_ELIGIBILITY.md"


class Failure(RuntimeError):
    """A contract in the SR-006 cluster contradicts another one."""


# ---------------------------------------------------------------------------
# Shared readers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise Failure(f"unreadable JSON {path.name}: {error}") from error


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise Failure(f"unreadable YAML {path.name}: {error}") from error


_CREATE_TABLE = re.compile(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(")
_CHECK_IN = re.compile(
    r"check\s*\(\s*([a-z_][a-z0-9_]*)\s+in\s*\(([^)]*)\)\s*\)", re.IGNORECASE
)
_LITERAL = re.compile(r"'([^']*)'")


def table_bodies(path: Path) -> dict[str, str]:
    """The parenthesised body of every `create table` statement in one SQL file."""
    text = path.read_text(encoding="utf-8")
    bodies: dict[str, str] = {}
    for match in _CREATE_TABLE.finditer(text):
        depth, index = 1, match.end()
        while index < len(text) and depth:
            if text[index] == "(":
                depth += 1
            elif text[index] == ")":
                depth -= 1
            index += 1
        if depth:
            raise Failure(f"unterminated create table: {match.group(1)}")
        bodies[match.group(1)] = text[match.end() : index - 1]
    return bodies


def check_literals(body: str, column: str) -> set[str]:
    """The literal set of `check (<column> in (...))` inside one table body."""
    for match in _CHECK_IN.finditer(body):
        if match.group(1) == column:
            return set(_LITERAL.findall(match.group(2)))
    return set()


def has_column(body: str, column: str) -> bool:
    return bool(re.search(rf"(?m)^\s*{re.escape(column)}\s+\w", body))


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def resolve_parameter(spec: dict, node: dict) -> dict:
    reference = node.get("$ref")
    if not reference:
        return node
    return spec["components"]["parameters"][reference.rsplit("/", 1)[1]]


def operation_at(spec: dict, path: str, method: str) -> dict:
    item = spec["paths"].get(path)
    if not item or method not in item:
        raise Failure(f"OpenAPI declares no {method.upper()} {path}")
    return item[method]


# ---------------------------------------------------------------------------
# Stage 1 — PF-005: the provider configuration authority
# ---------------------------------------------------------------------------

# The ordered decision procedure a callback is put through. Each entry is the
# discriminator id, the predicate that refuses, and the reason code it refuses with.
# It is data rather than a chain of `if` statements because the mix-up fixture is
# checked against exactly this list in both directions: a discriminator with no vector
# is a hole, and a vector naming a discriminator this list does not hold is a vector
# nothing evaluates.
Callback = dict[str, Any]
Provider = dict[str, Any]


def _refuses_single_use(callback: Callback, provider: Provider) -> bool:
    return callback["transaction_state"] != "redirected"


def _refuses_lifetime(callback: Callback, provider: Provider) -> bool:
    return bool(callback["transaction_expired"])


def _refuses_callback_path(callback: Callback, provider: Provider) -> bool:
    return callback["delivered_to_callback_path"] != provider["callback_path"]


def _refuses_redirect(callback: Callback, provider: Provider) -> bool:
    return callback["presented_redirect_uri"] != provider["redirect_uri"]


def _refuses_issuer(callback: Callback, provider: Provider) -> bool:
    presented = callback["presented_iss"]
    supported = provider["rfc9207_iss"]["capability"] == "supported"
    if presented is None:
        # ADR-015: absent `iss` fails closed for a provider recorded as supporting
        # RFC 9207, and is not a fallback to unvalidated behaviour. For any other
        # capability there is nothing to require, which is precisely why claiming
        # the capability without an observation would manufacture the control.
        return supported
    return presented != provider["issuer"]


def _refuses_state(callback: Callback, provider: Provider) -> bool:
    return not callback["state_matches_transaction"]


def _refuses_pkce(callback: Callback, provider: Provider) -> bool:
    return callback["pkce_method"] != provider["pkce_method"]


DISCRIMINATORS: tuple[tuple[str, Callable[[Callback, Provider], bool], str], ...] = (
    ("transaction-single-use", _refuses_single_use, "OAUTH_CODE_ALREADY_CONSUMED"),
    ("transaction-lifetime", _refuses_lifetime, "OAUTH_TRANSACTION_EXPIRED"),
    ("callback-path-binding", _refuses_callback_path, "OAUTH_ISSUER_MISMATCH"),
    ("redirect-uri-exact-match", _refuses_redirect, "OAUTH_REDIRECT_URI_MISMATCH"),
    ("issuer-identification", _refuses_issuer, "OAUTH_ISSUER_MISMATCH"),
    ("state-binding", _refuses_state, "OAUTH_STATE_INVALID"),
    ("pkce-method", _refuses_pkce, "OAUTH_PKCE_VERIFICATION_FAILED"),
)

# Which single field of a callback observation each discriminator reads. The fixture
# is required to mutate exactly this field and nothing else, so a recorded rejection
# is attributable to one cause rather than to a generally malformed vector.
DISCRIMINATOR_FIELD: dict[str, str] = {
    "transaction-single-use": "transaction_state",
    "transaction-lifetime": "transaction_expired",
    "callback-path-binding": "delivered_to_callback_path",
    "redirect-uri-exact-match": "presented_redirect_uri",
    "issuer-identification": "presented_iss",
    "state-binding": "state_matches_transaction",
    "pkce-method": "pkce_method",
}

CALLBACK_FIELDS = (
    "transaction_provider_id",
    "transaction_state",
    "transaction_expired",
    "delivered_to_callback_path",
    "presented_redirect_uri",
    "presented_iss",
    "state_matches_transaction",
    "pkce_method",
)


def decide(
    callback: Callback, provider: Provider
) -> tuple[str, str | None, str | None]:
    """Accept or refuse one callback observation. Returns (outcome, code, rule)."""
    for name, refuses, code in DISCRIMINATORS:
        if refuses(callback, provider):
            return "reject", code, name
    return "accept", None, None


def _baseline_for(provider: Provider) -> Callback:
    return {
        "transaction_provider_id": provider["provider_id"],
        "transaction_state": "redirected",
        "transaction_expired": False,
        "delivered_to_callback_path": provider["callback_path"],
        "presented_redirect_uri": provider["redirect_uri"],
        "presented_iss": None,
        "state_matches_transaction": True,
        "pkce_method": provider["pkce_method"],
    }


def stage_provider_registry(report: list[str]) -> dict[str, int]:
    registry = load_json(REGISTRY_PATH)
    schema = load_json(REGISTRY_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(
            registry
        ),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise Failure(
            "oauth-provider-registry-v1.json failed its schema: "
            + "; ".join(error.message for error in errors[:6])
        )

    providers = {row["provider_id"]: row for row in registry["providers"]}
    if len(providers) != len(registry["providers"]):
        raise Failure("oauth-provider-registry-v1.json declares a provider twice")

    spec = load_yaml(OPENAPI_PATH)
    bodies = table_bodies(SQL_PATH)

    # 1. One spelling for a provider across every owner. The registry stores the
    #    same literals the DDL CHECKs and the API enums do; a second spelling here
    #    would be a provider the rest of the system cannot name, which is the
    #    kebab/snake class of defect this repository has already hit four times.
    expected = set(providers)
    sql_sets = {
        "linked_identities.provider": check_literals(
            bodies["linked_identities"], "provider"
        ),
        "oauth_transactions.provider": check_literals(
            bodies["oauth_transactions"], "provider"
        ),
    }
    for label, actual in sql_sets.items():
        if actual != expected:
            report.append(
                f"provider vocabulary differs: {label} holds {sorted(actual)}, the "
                f"registry declares {sorted(expected)}"
            )
    for name, definition in spec["components"]["schemas"].items():
        for prop, node in (definition.get("properties") or {}).items():
            if prop != "provider" or not isinstance(node, dict):
                continue
            if "enum" not in node:
                continue
            if set(node["enum"]) != expected:
                report.append(
                    f"provider vocabulary differs: {name}.{prop} holds "
                    f"{sorted(node['enum'])}, the registry declares {sorted(expected)}"
                )

    # 2. A capability is an observation or it is not claimed. A provider whose
    #    verification records that nothing was read cannot declare `supported` on
    #    anything: ADR-015 makes RFC 9207 the control that closes the mix-up attack,
    #    so a capability asserted without a reading manufactures the very control it
    #    is meant to prove.
    for name, row in sorted(providers.items()):
        verified = row["verification"]["state"] == "verified"
        for field in ("rfc9207_iss", "device_flow"):
            capability = row[field]["capability"]
            if capability != "unverified" and not verified:
                report.append(
                    f"{name}.{field} claims {capability!r} while the provider's "
                    "verification state is unverified; a capability nobody observed "
                    "cannot be relied on as a control"
                )

    # 3. The warranty is bounded and is not wall-clock. A row whose review is due
    #    before it was recorded, or more than a year after, is a record nobody will
    #    ever be asked to renew.
    for name, row in sorted(providers.items()):
        recorded, due = instant(row["recorded_at"]), instant(row["review_due_at"])
        if due <= recorded:
            report.append(f"{name}: review_due_at is not after recorded_at")
        elif due - recorded > MAX_REVIEW_WINDOW:
            report.append(
                f"{name}: review_due_at is {(due - recorded).days} days after "
                f"recorded_at, beyond the {MAX_REVIEW_WINDOW.days}-day ceiling"
            )

    # 4. Every declared path is a path the API actually declares, the callback paths
    #    are distinct, and the exact redirect ends at the callback it names. The
    #    unique provider-specific callback path is what binds a callback for a
    #    provider without RFC 9207, so two providers sharing one would delete the
    #    only mix-up control the launch configuration has.
    seen_callbacks: dict[str, str] = {}
    for name, row in sorted(providers.items()):
        for field in ("start_path", "callback_path"):
            if row[field] not in spec["paths"]:
                report.append(
                    f"{name}.{field} names {row[field]}, which openapi-v1.yaml does "
                    "not declare"
                )
        other = seen_callbacks.get(row["callback_path"])
        if other:
            report.append(
                f"{name} and {other} share the callback path {row['callback_path']}; "
                "the provider-specific path is the mix-up binding for a provider "
                "without RFC 9207 and cannot be shared"
            )
        seen_callbacks[row["callback_path"]] = name
        if not row["redirect_uri"].endswith(row["callback_path"]):
            report.append(
                f"{name}: redirect_uri {row['redirect_uri']} does not end at its "
                f"declared callback path {row['callback_path']}"
            )

    # 5. The `iss` parameter follows the recorded capability, not the provider.
    #    `/auth/github/callback` declared it and `/auth/x/callback` did not, and no
    #    record anywhere said why — an asymmetry that reads as a capability claim
    #    while resting on nothing. It is now a function of the capability value, so
    #    two providers recorded alike are declared alike.
    for name, row in sorted(providers.items()):
        operation = operation_at(spec, row["callback_path"], "get")
        declared = None
        for node in operation.get("parameters", []):
            resolved = resolve_parameter(spec, node)
            if resolved.get("name") == "iss":
                declared = resolved
        capability = row["rfc9207_iss"]["capability"]
        if capability == "supported":
            if declared is None:
                report.append(
                    f"{name} records RFC 9207 support and its callback declares no "
                    "`iss` parameter, so the control cannot be applied"
                )
            elif not declared.get("required"):
                report.append(
                    f"{name} records RFC 9207 support and its callback declares "
                    "`iss` optional; ADR-015 fails closed on an absent iss for such "
                    "a provider"
                )
        elif capability == "unsupported":
            if declared is not None:
                report.append(
                    f"{name} records RFC 9207 as unsupported and its callback still "
                    "declares `iss`; there is nothing for it to be compared against"
                )
        else:
            if declared is None:
                report.append(
                    f"{name} records RFC 9207 as unverified and its callback "
                    "declares no `iss` parameter, while another provider with the "
                    "same capability value does; the asymmetry states a capability "
                    "difference the registry does not record"
                )
            elif declared.get("required"):
                report.append(
                    f"{name} records RFC 9207 as unverified and its callback "
                    "requires `iss`; an unobserved capability may not be required"
                )

    # 6. The vectors, decided rather than believed.
    vectors_checked = stage_mixup_vectors(report, providers)
    return {"providers": len(providers), "vectors": vectors_checked}


def stage_mixup_vectors(report: list[str], providers: dict[str, Provider]) -> int:
    fixture = load_json(MIXUP_PATH)
    declared_order = tuple(fixture["discriminator_order"])
    implemented = tuple(name for name, _, _ in DISCRIMINATORS)
    if declared_order != implemented:
        report.append(
            "provider-mixup-vectors-v1.json declares a discriminator order the "
            f"evaluator does not implement: fixture={list(declared_order)} "
            f"evaluator={list(implemented)}"
        )

    codes = {row["code"] for row in load_json(REASONS_PATH)["codes"]}
    reason_of = {name: code for name, _, code in DISCRIMINATORS}
    for name, code in sorted(reason_of.items()):
        if code not in codes:
            report.append(
                f"discriminator {name} refuses with {code}, which reason-codes-v1.json "
                "does not declare"
            )

    baselines: dict[str, Callback] = {}
    covered: dict[str, set[str]] = {name: set() for name in providers}
    for vector in fixture["vectors"]:
        name = vector["provider_id"]
        if name not in providers:
            report.append(
                f"{vector['case_id']} names provider {name!r}, which the registry "
                "does not declare"
            )
            continue
        callback = vector["callback"]
        missing = sorted(set(CALLBACK_FIELDS) - set(callback))
        if missing:
            report.append(f"{vector['case_id']} omits callback fields {missing}")
            continue
        outcome, code, rule = decide(callback, providers[name])
        if outcome != vector["expect"]:
            report.append(
                f"{vector['case_id']} records {vector['expect']} and the registry "
                f"decides {outcome}" + (f" under {rule}" if rule else "")
            )
        elif code != vector["expect_reason_code"]:
            report.append(
                f"{vector['case_id']} records reason {vector['expect_reason_code']} "
                f"and the registry refuses with {code} under {rule}"
            )
        if vector["role"] == "baseline":
            if vector["mutated_discriminator"] is not None:
                report.append(f"{vector['case_id']} is a baseline and names a mutation")
            if name in baselines:
                report.append(f"{name} declares more than one accepted baseline")
            baselines[name] = callback
        else:
            covered.setdefault(name, set()).add(vector["mutated_discriminator"])

    for name in sorted(providers):
        if name not in baselines:
            report.append(
                f"{name} has no accepted baseline; a corpus that only ever rejects "
                "cannot show that the decision procedure accepts anything"
            )
            continue
        expected_baseline = _baseline_for(providers[name])
        if baselines[name] != expected_baseline:
            differing = sorted(
                field
                for field in CALLBACK_FIELDS
                if baselines[name].get(field) != expected_baseline.get(field)
            )
            report.append(
                f"{name}: the accepted baseline differs from the registry row it is "
                f"supposed to reproduce, at {differing}"
            )
        gaps = sorted(set(implemented) - covered.get(name, set()))
        if gaps:
            report.append(
                f"{name}: no vector exercises {gaps}; a discriminator with no vector "
                "is a rule nothing has ever seen refuse"
            )

    # Each mutation differs from its baseline in exactly the field its discriminator
    # names. Without this a vector could reject for a second reason and still record
    # the first, which is how a corpus starts confirming itself.
    for vector in fixture["vectors"]:
        if vector["role"] != "mutation":
            continue
        name = vector["provider_id"]
        if name not in baselines:
            continue
        differing = sorted(
            field
            for field in CALLBACK_FIELDS
            if vector["callback"].get(field) != baselines[name].get(field)
        )
        expected_field = DISCRIMINATOR_FIELD.get(vector["mutated_discriminator"])
        if expected_field is None:
            report.append(
                f"{vector['case_id']} names discriminator "
                f"{vector['mutated_discriminator']!r}, which no rule reads"
            )
        elif differing != [expected_field]:
            report.append(
                f"{vector['case_id']} claims to mutate {expected_field} and differs "
                f"from the baseline at {differing}; a refusal attributable to two "
                "fields is attributable to neither"
            )

    # The sweep. The fixture could be right about every vector it holds and still
    # miss a rule the evaluator silently stopped applying, so the evaluator is put
    # through its own discriminators here, against the committed registry.
    for name, provider in sorted(providers.items()):
        for discriminator, _, code in DISCRIMINATORS:
            probe = _baseline_for(provider)
            outcome, actual, rule = decide(probe, provider)
            if outcome != "accept":
                report.append(
                    f"{name}: the registry refuses its own baseline under {rule}"
                )
                break
            probe[DISCRIMINATOR_FIELD[discriminator]] = _mutate_value(
                discriminator, provider, providers
            )
            outcome, actual, rule = decide(probe, provider)
            if outcome != "reject":
                report.append(
                    f"{name}: mutating {DISCRIMINATOR_FIELD[discriminator]} does not "
                    f"trip {discriminator}; the rule reads a field nothing changes"
                )
            elif actual != code:
                report.append(
                    f"{name}: mutating {DISCRIMINATOR_FIELD[discriminator]} refuses "
                    f"with {actual} under {rule}, not the {code} {discriminator} declares"
                )

    # The capability has to change the decision, or recording it is decoration. A
    # callback with no `iss` is accepted for an unverified provider and refused for
    # one recorded as supporting RFC 9207 — which is the whole reason the capability
    # may not be claimed without an observation.
    probe_provider = dict(next(iter(providers.values())))
    probe = _baseline_for(probe_provider)
    probe["presented_iss"] = None
    probe_provider["rfc9207_iss"] = {"capability": "unverified", "basis": "probe"}
    if decide(probe, probe_provider)[0] != "accept":
        report.append(
            "an absent `iss` is refused for a provider whose RFC 9207 capability is "
            "unverified; the fallback binding is the provider-specific callback path"
        )
    probe_provider = dict(probe_provider)
    probe_provider["rfc9207_iss"] = {"capability": "supported", "basis": "probe"}
    outcome, code, _ = decide(probe, probe_provider)
    if outcome != "reject" or code != "OAUTH_ISSUER_MISMATCH":
        report.append(
            "an absent `iss` is accepted for a provider recorded as supporting "
            "RFC 9207; ADR-015 requires that to fail closed rather than fall back"
        )

    return len(fixture["vectors"])


def _mutate_value(
    discriminator: str, provider: Provider, providers: dict[str, Provider]
):
    others = [row for name, row in providers.items() if name != provider["provider_id"]]
    other = others[0] if others else provider
    return {
        "transaction-single-use": "consumed",
        "transaction-lifetime": True,
        "callback-path-binding": other["callback_path"] + "-elsewhere",
        "redirect-uri-exact-match": other["redirect_uri"] + "/elsewhere",
        "issuer-identification": other["issuer"] + ".invalid",
        "state-binding": False,
        "pkce-method": "plain",
    }[discriminator]


# ---------------------------------------------------------------------------
# Stage 2 — PF-006: the canonical OAuth transaction
# ---------------------------------------------------------------------------

# What a transaction must bind, and why each one is a column rather than a value the
# callback supplies. Every entry is a column of `oauth_transactions`; the point of the
# table is that a callback-controlled value never selects any of them.
TRANSACTION_BINDINGS: dict[str, str] = {
    "provider": "which authorization server the transaction was begun with",
    "provider_revision": "the provider-registry revision it agreed to",
    "issuer": "the immutable issuer the callback's iss is compared against",
    "redirect_uri": "the exact redirect, compared byte-for-byte",
    "pkce_method": "the pinned challenge method",
    "state_hash": "the state binding",
    "pkce_verifier_ciphertext": "the encrypted verifier",
    "intended_action": "sign-in or link-identity",
    "initiating_account_id": "the account that began a link",
    "initiating_web_session_id": "the session that began a link",
    "recent_auth_at": "the recent-authentication instant a link required",
    "resulting_account_id": "what it bound",
    "resulting_session_id": "the session a sign-in produced",
    "resulting_identity_id": "the linked identity a link produced",
    "failure_reason_code": "why it failed",
    "revision": "the monotonic revision its machine declares",
    "expires_at": "the lifetime",
    "consumed_at": "the one-time consumption instant",
}

# Constraint fragments that carry a rule no handler discipline can hold. Each is
# matched as a normalised substring of the table body, so reformatting is tolerated
# and deletion is not.
TRANSACTION_RULES: tuple[tuple[str, str], ...] = (
    (
        "intended_action <> 'link-identity' or resulting_session_id is null",
        "a link transaction must not be able to mint browser access",
    ),
    (
        "state <> 'consumed' or resulting_account_id is not null",
        "a consumed transaction must have bound an account",
    ),
    (
        "resulting_account_id = initiating_account_id",
        "a transaction must not finish on an account other than the one it started on",
    ),
)

# Operations that may change which provider subject an account holds. Each must reach
# the transaction; a bare authorization code reaching any of them is the standalone
# path SR-006 records.
IDENTITY_MUTATING_OPERATIONS = ("linkIdentity",)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def stage_oauth_transaction(report: list[str]) -> dict[str, int]:
    bodies = table_bodies(SQL_PATH)
    spec = load_yaml(OPENAPI_PATH)
    machines = {row["machine_id"]: row for row in load_json(MACHINES_PATH)["machines"]}
    schemas = spec["components"]["schemas"]

    body = bodies.get("oauth_transactions")
    if body is None:
        raise Failure("planning-schema.sql declares no oauth_transactions table")

    # 1. The transaction binds what the contract document says it binds.
    for column, purpose in sorted(TRANSACTION_BINDINGS.items()):
        if not has_column(body, column):
            report.append(
                f"oauth_transactions declares no {column}, so the transaction does not "
                f"bind {purpose}"
            )

    # 2. The rules that are constraints rather than conventions.
    flat = _normalise(body)
    for fragment, why in TRANSACTION_RULES:
        if _normalise(fragment) not in flat:
            report.append(
                f"oauth_transactions lost the constraint that {why}: {fragment!r}"
            )

    # 3. The intended-action vocabulary agrees across its two owners, in one spelling.
    #    It was `sign_in`/`link_identity` on the API and unconstrained in the DDL, so
    #    the API held a vocabulary the persistence owner did not, and neither spelling
    #    could be compared with the other.
    sql_actions = check_literals(body, "intended_action")
    if not sql_actions:
        report.append(
            "oauth_transactions.intended_action carries no CHECK vocabulary; the "
            "column can hold any string the API never declared"
        )
    api_actions: dict[str, set[str]] = {}
    for name in ("OAuthStartRequest", "OAuthCompletion"):
        node = (schemas.get(name) or {}).get("properties", {}).get("intended_action")
        if not node or "enum" not in node:
            report.append(f"{name} declares no intended_action enum")
            continue
        api_actions[name] = set(node["enum"])
    for name, values in sorted(api_actions.items()):
        if sql_actions and values != sql_actions:
            report.append(
                f"intended_action differs: {name} holds {sorted(values)}, "
                f"oauth_transactions.intended_action holds {sorted(sql_actions)}"
            )
    for value in sorted(sql_actions | set().union(*api_actions.values(), set())):
        if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", value):
            report.append(
                f"intended_action value {value!r} is not lowercase kebab-case; a "
                "second spelling of one vocabulary is a comparison that finds nothing"
            )

    # 4. No identity-mutating operation accepts a bare authorization code, and each one
    #    names a transaction. This is phrased over what the request body *requires*
    #    rather than over the absence of a word, so an operation that grows a new
    #    credential field without a transaction reference fails.
    for operation_id in IDENTITY_MUTATING_OPERATIONS:
        schema_name = _request_schema_name(spec, operation_id)
        if schema_name is None:
            report.append(f"{operation_id} declares no JSON request body")
            continue
        definition = schemas.get(schema_name, {})
        properties = set(definition.get("properties") or {})
        required = set(definition.get("required") or ())
        if "oauth_transaction_id" not in required:
            report.append(
                f"{operation_id} does not require an oauth_transaction_id; it mutates "
                "identity without reaching a transaction, so no redirect, state, PKCE "
                "or lifetime is verified on that path"
            )
        for forbidden in ("authorization_code", "access_token", "id_token", "code"):
            if forbidden in properties:
                report.append(
                    f"{operation_id} accepts {forbidden!r} directly; a credential "
                    "presented outside the transaction is the standalone "
                    "authorization-code path SR-006 records"
                )

    # 5. The audit ledger can record exactly the transitions the machine declares.
    machine = machines.get("oauth-transaction")
    if machine is None:
        raise Failure(
            "the state machine registry declares no oauth-transaction machine"
        )
    events = bodies.get("oauth_authorization_events")
    if events is None:
        report.append(
            "planning-schema.sql declares no oauth_authorization_events table"
        )
    else:
        recorded = check_literals(events, "event_type")
        declared = {t["transition_id"] for t in machine["transitions"]}
        if recorded != declared:
            report.append(
                "oauth_authorization_events.event_type differs from the machine's "
                f"transitions: only-in-sql={sorted(recorded - declared)} "
                f"only-in-machine={sorted(declared - recorded)}"
            )
        if not re.search(
            r"oauth_transaction_id\s+uuid\s+not\s+null\s+references\s+oauth_transactions",
            _normalise(events),
        ):
            report.append(
                "oauth_authorization_events does not reference oauth_transactions; an "
                "event about no particular transaction records nothing"
            )

    # 6. The machine declares a revision model and the table has somewhere to keep it.
    if machine["revision_model"] == "monotonic-revision" and not has_column(
        body, "revision"
    ):
        report.append(
            "the oauth-transaction machine declares monotonic-revision and "
            "oauth_transactions carries no revision column, so a conditional update "
            "has nothing to name"
        )

    # 7. The callback contract splits by action. A link callback must not be able to
    #    describe a session, which is the same rule the DDL carries as a constraint.
    completion = schemas.get("OAuthCompletion", {})
    conditionals = json.dumps(completion.get("allOf", []))
    if '"link-identity"' not in conditionals or "session_id" not in conditionals:
        report.append(
            "OAuthCompletion does not condition session_id on the intended action; the "
            "contract then says a link callback mints a session, which "
            "oauth_transactions refuses at the constraint level"
        )
    if set(completion.get("required") or ()) & {"account_id", "session_id"}:
        report.append(
            "OAuthCompletion requires account_id or session_id unconditionally, so a "
            "link callback cannot be answered without inventing one"
        )

    return {"transaction bindings": len(TRANSACTION_BINDINGS)}


def _request_schema_name(spec: dict, operation_id: str) -> str | None:
    for item in spec["paths"].values():
        for operation in item.values():
            if not isinstance(operation, dict):
                continue
            if operation.get("operationId") != operation_id:
                continue
            body = operation.get("requestBody") or {}
            media = (body.get("content") or {}).get("application/json") or {}
            reference = (media.get("schema") or {}).get("$ref")
            return reference.rsplit("/", 1)[1] if reference else None
    return None


# ---------------------------------------------------------------------------
# Stage registry
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Stage 3 — PF-007: linked identity and recovery lifecycle
# ---------------------------------------------------------------------------

LINKED_IDENTITY_STATES = (
    "candidate",
    "linked",
    "unlink-pending",
    "lost",
    "compromised",
    "recovery-pending",
    "unlinked",
    "superseded",
)

# The states a provider subject may be bound in. The partial unique index must cover
# exactly these: one more and a retained history row blocks its own successor, one
# fewer and two live rows can hold one subject.
LIVE_IDENTITY_STATES = frozenset(LINKED_IDENTITY_STATES) - {"unlinked", "superseded"}

# The guard the schema cannot carry, named in the machine and stated in the document.
# Both halves are required, because a rule recorded in only one of them is a rule the
# other owner can contradict without anything noticing.
LAST_METHOD_GUARD = "request-unlink-unless-last-authentication-method"
LAST_METHOD_PROSE = "last-authentication-method invariant"


def stage_linked_identity(report: list[str]) -> dict[str, int]:
    bodies = table_bodies(SQL_PATH)
    machines = {row["machine_id"]: row for row in load_json(MACHINES_PATH)["machines"]}
    sql_text = SQL_PATH.read_text(encoding="utf-8")

    machine = machines.get("linked-identity")
    if machine is None:
        raise Failure(
            "the state machine registry declares no linked-identity machine; the "
            "aggregate has a persistence owner and no lifecycle"
        )
    body = bodies.get("linked_identities")
    if body is None:
        raise Failure("planning-schema.sql declares no linked_identities table")

    # 1. Eight states, in one spelling, across the machine and the CHECK. Reachability
    #    and terminal-state integrity are proved for every machine by
    #    validate_state_vocabularies.py; what that cannot know is which eight.
    declared = set(machine["states"])
    if declared != set(LINKED_IDENTITY_STATES):
        report.append(
            "the linked-identity machine does not declare the eight states the "
            f"provider-loss contract requires: only-in-machine={sorted(declared - set(LINKED_IDENTITY_STATES))} "
            f"missing={sorted(set(LINKED_IDENTITY_STATES) - declared)}"
        )
    recorded = check_literals(body, "state")
    if recorded != set(LINKED_IDENTITY_STATES):
        report.append(
            "linked_identities.state cannot hold every linked-identity state: "
            f"only-in-sql={sorted(recorded - set(LINKED_IDENTITY_STATES))} "
            f"missing={sorted(set(LINKED_IDENTITY_STATES) - recorded)}"
        )

    # 2. The durable subject, and a uniqueness that survives retained history. A total
    #    unique constraint on (provider, provider_subject) reads correct and makes a
    #    re-link after a recovery collide with the row it replaced, so the constraint
    #    has to be partial and has to cover exactly the live states.
    for column in ("provider_subject", "provider_account_created_at", "revision"):
        if not has_column(body, column):
            report.append(f"linked_identities declares no {column}")
    # docs/privacy/DATA_MAP.md retains both fields "until unlink or account erasure" and
    # deletes the subject "immediately on unlink". A `not null` provider_subject makes
    # that unimplementable without deleting the row, and an ended row that keeps its
    # subject blocks that provider account from ever being linked again.
    if re.search(r"(?m)^\s*provider_subject\s+text\s+not\s+null", body):
        report.append(
            "linked_identities.provider_subject is not null, so an ended binding "
            "cannot release it; DATA_MAP.md deletes the subject immediately on unlink "
            "and a retained one blocks the provider account from ever being linked again"
        )
    flat_body = _normalise(body)
    for column in ("provider_subject", "provider_account_created_at"):
        if f"check (({column} is not null)" not in flat_body:
            report.append(
                f"linked_identities does not tie {column} to the live states; the "
                "retention rule DATA_MAP.md states is then a promise rather than a "
                "constraint"
            )
    if re.search(r"(?m)^\s*unique\s*\(\s*provider\s*,\s*provider_subject\s*\)", body):
        report.append(
            "linked_identities carries a total unique (provider, provider_subject); "
            "with superseded and unlinked rows retained, a re-link of one subject "
            "collides with the row it replaced"
        )
    index = _partial_index(sql_text, "linked_identities_live_subject_idx")
    if index is None:
        report.append(
            "linked_identities declares no partial unique index on the provider "
            "subject; nothing then stops two live rows binding one provider account"
        )
    else:
        columns, states = index
        if columns != ["provider", "provider_subject"]:
            report.append(
                f"linked_identities_live_subject_idx keys on {columns}, not the "
                "durable provider subject"
            )
        if states != LIVE_IDENTITY_STATES:
            report.append(
                "linked_identities_live_subject_idx covers the wrong states: "
                f"only-in-index={sorted(states - LIVE_IDENTITY_STATES)} "
                f"missing={sorted(LIVE_IDENTITY_STATES - states)}"
            )

    # 3. The invariant no constraint can hold is recorded in both places that could
    #    contradict each other. This is the check that keeps it from becoming a
    #    sentence in a document nothing reads.
    guards = [
        transition
        for transition in machine["transitions"]
        if transition["to"] == "unlink-pending"
    ]
    if not guards:
        report.append(
            "the linked-identity machine has no transition into unlink-pending"
        )
    elif not any(transition["action"] == LAST_METHOD_GUARD for transition in guards):
        report.append(
            "no transition into unlink-pending names the last-authentication-method "
            f"guard; expected the action {LAST_METHOD_GUARD!r}, found "
            f"{[transition['action'] for transition in guards]}"
        )
    if LAST_METHOD_PROSE not in AUTH_DOC.read_text(encoding="utf-8"):
        report.append(
            "AUTHENTICATION_AND_RECOVERY.md no longer states the "
            f"{LAST_METHOD_PROSE}; the machine names a guard the normative owner does "
            "not define"
        )

    # 4. A terminal state is reachable only by the actor entitled to drive it. `unlinked`
    #    and `superseded` have no way out, so an actor who can reach either can end an
    #    aggregate permanently. A directional block once drove a symmetric friendship to
    #    a terminal state for exactly this reason.
    for transition in machine["transitions"]:
        if transition["to"] not in ("unlinked", "superseded"):
            continue
        if transition["to"] == "superseded" and transition["actor"] != "worker":
            report.append(
                f"{transition['transition_id']} drives a live identity to the terminal "
                f"state superseded as {transition['actor']!r}; only a worker acting on "
                "a later binding of the same subject may"
            )
        if transition["actor"] == "moderator":
            report.append(
                f"{transition['transition_id']} lets a moderator end a linked identity "
                "outright; a sanction moves the ranked identity, not the account's "
                "authentication method"
            )

    # 5. Recovery is reachable from provider loss and returns. A `recovery-pending`
    #    identity that could only go forward would make a cancelled recovery destroy
    #    the binding it was opened to protect.
    reachable_from = {
        transition["to"]: set(transition["from"])
        for transition in machine["transitions"]
    }
    if "recovery-pending" not in reachable_from:
        report.append("no transition reaches recovery-pending from provider loss")
    elif not {"lost", "compromised"} <= reachable_from["recovery-pending"]:
        report.append(
            "recovery-pending is not reachable from both lost and compromised: "
            f"{sorted(reachable_from['recovery-pending'])}"
        )
    if not any(
        transition["from"] == ["recovery-pending"] and transition["to"] == "linked"
        for transition in machine["transitions"]
    ):
        report.append(
            "a recovery-pending identity has no way back to linked, so a cancelled or "
            "denied recovery destroys the binding it was opened to protect"
        )

    # 6. The unlink request no longer demands a provider credential. Sharing one request
    #    body with the link meant the contract required an authorization code to remove
    #    a link, including the case where the lost provider account is the reason.
    spec = load_yaml(OPENAPI_PATH)
    unlink_schema = _request_schema_name(spec, "unlinkIdentity")
    if unlink_schema is None:
        report.append("unlinkIdentity declares no JSON request body")
    else:
        definition = spec["components"]["schemas"].get(unlink_schema, {})
        properties = set(definition.get("properties") or {})
        if properties & {"authorization_code", "oauth_transaction_id"}:
            report.append(
                "unlinkIdentity requires a provider credential or transaction; "
                "removing a link is a change to this account's own rows, and a lost "
                "provider account is exactly when it is needed"
            )
        if "identity_id" not in set(definition.get("required") or ()):
            report.append("unlinkIdentity does not name the identity it removes")

    return {"linked-identity states": len(LINKED_IDENTITY_STATES)}


_INDEX_RE_TEMPLATE = (
    r"create\s+unique\s+index\s+{name}\s+on\s+\w+\s*\(([^)]*)\)\s*where\s+"
    r"state\s+in\s*\(([^)]*)\)"
)


def _partial_index(sql: str, name: str) -> tuple[list[str], frozenset[str]] | None:
    match = re.search(
        _INDEX_RE_TEMPLATE.format(name=re.escape(name)), _normalise(sql), re.IGNORECASE
    )
    if not match:
        return None
    columns = [column.strip() for column in match.group(1).split(",") if column.strip()]
    return columns, frozenset(_LITERAL.findall(match.group(2)))


# ---------------------------------------------------------------------------
# Stage registry
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Stage 4 — PF-008: ranked identity and consolidation authority
# ---------------------------------------------------------------------------

# Every domain a duplicate account owns. `docs/security/AUTHENTICATION_AND_RECOVERY.md`
# requires a merge to define ownership of each; the plan record covered three of them.
CONSOLIDATION_DOMAINS = (
    "identities",
    "devices",
    "claims",
    "social",
    "boards",
    "moderation",
    "exports",
    "deletions",
)

# Every plan record committed to the repository, and whether the schema accepts it.
# The ordering rule below is applied to each accepted one and to the fixture written to
# violate it, so the rule is exercised in both directions rather than only where it holds.
CONSOLIDATION_FIXTURES: tuple[tuple[str, bool], ...] = (
    ("consolidation-plan.valid.json", True),
    ("consolidation-plan.invalid-summed-total.json", False),
    ("consolidation-plan.invalid-domain-not-covered.json", False),
    ("consolidation-plan.invalid-newer-identity-survives.json", True),
)

# The participant-driven transitions of this cluster and the operation each is reached
# by. A `user` actor with no operation is a lifecycle that requires a person to do
# something the API gives them no way to do; the account-consolidation machine declared
# exactly that, and a case could leave awaiting-confirmation only by expiring.
PARTICIPANT_OPERATIONS: dict[tuple[str, str], str] = {
    ("account-consolidation", "consolidation-confirm"): "confirmConsolidation",
    ("linked-identity", "identity-link-confirm"): "linkIdentity",
    ("linked-identity", "identity-unlink-request"): "unlinkIdentity",
    ("linked-identity", "identity-unlink-cancel"): "cancelIdentityUnlink",
    ("linked-identity", "identity-report-lost"): "reportProviderAccess",
    ("linked-identity", "identity-report-compromised"): "reportProviderAccess",
}

# Property names that would hold one figure derived from two accounts' token burn.
# D-070 forbids adding two stored account totals, and the surviving standing is
# recomputed from claim-level contributions instead.
# `token_burn_total` on a single contribution is deliberately not matched: it is one
# claim's raw accepted quantity, carried unchanged, and it is the thing the surviving
# standing is recomputed *from*. What is forbidden is a figure that spans two accounts.
SUMMED_FIGURE_PATTERN = re.compile(
    r"(?:^|_)(?:combined|merged|summed)(?:_|$)"
    r"|^aggregate_.*(?:token_burn|score)"
    r"|(?:token_burn|score)_sum$"
)

# Schemas the consolidation surface publishes. Each is swept for a summed figure, and
# each numeric property must be a count rather than a quantity.
CONSOLIDATION_RESPONSE_SCHEMAS = (
    "ConsolidationPlanView",
    "ConsolidationDomainDisposition",
    "ConsolidationConfirmationRequest",
)


def stage_ranked_identity(report: list[str]) -> dict[str, int]:
    bodies = table_bodies(SQL_PATH)
    spec = load_yaml(OPENAPI_PATH)
    schemas = spec["components"]["schemas"]
    machines = {row["machine_id"]: row for row in load_json(MACHINES_PATH)["machines"]}

    # 1. Three aggregates, three tables. A survivor reference on `accounts` would put
    #    the ranked identity's resolution on the account row and collapse two of the
    #    three aggregates AGENTS.md keeps apart.
    ranked = bodies.get("ranked_identities")
    if ranked is None:
        raise Failure("planning-schema.sql declares no ranked_identities table")
    if "ranked_identities" not in _normalise(ranked).replace(
        "ranked_identities (", "", 1
    ) and not re.search(
        r"absorbed_into_ranked_identity_id\s+uuid\s+references\s+ranked_identities",
        _normalise(ranked),
    ):
        report.append(
            "ranked_identities carries no survivor reference; a consolidation survivor "
            "cannot name what it absorbed"
        )
    account_body = bodies.get("accounts", "")
    for stray in ("ranked_identity_id", "absorbed_into_ranked_identity_id", "score"):
        if has_column(account_body, stray):
            report.append(
                f"accounts declares {stray}; the account and the ranked identity are "
                "separate aggregates and a column here makes the account row a second "
                "authority for the identity's resolution"
            )

    # 2. The plan covers every domain a duplicate account owns, and the coverage cannot
    #    be satisfied by an empty object: the domains are required keys.
    schema = load_json(CONSOLIDATION_SCHEMA_PATH)
    dispositions = schema["$defs"].get("domain_dispositions")
    if dispositions is None:
        report.append(
            "consolidation-plan-v1.schema.json declares no domain_dispositions; a plan "
            "can apply while silent about the absorbed account's devices, social "
            "state, boards, moderation, exports and deletions"
        )
    else:
        required = set(dispositions.get("required") or ())
        if required != set(CONSOLIDATION_DOMAINS):
            report.append(
                "consolidation-plan-v1.schema.json does not require every domain: "
                f"missing={sorted(set(CONSOLIDATION_DOMAINS) - required)} "
                f"unexpected={sorted(required - set(CONSOLIDATION_DOMAINS))}"
            )
        if dispositions.get("additionalProperties") is not False:
            report.append(
                "domain_dispositions admits additional properties, so a ninth domain "
                "can be invented in a plan rather than in the schema that governs it"
            )
        if "domain_dispositions" not in set(schema.get("required") or ()):
            report.append(
                "the consolidation plan does not require domain_dispositions at all"
            )

    # 3. D-564: the older ranked identity survives and the newer is retired without
    #    summation. JSON Schema cannot compare two of its own fields, so the ordering is
    #    checked here — over every committed plan, and over the fixture written to
    #    break it, so the rule is exercised in both directions.
    violations: list[str] = []
    for name, schema_accepts in CONSOLIDATION_FIXTURES:
        path = SCHEMAS / "examples" / name
        if not path.is_file():
            report.append(f"consolidation fixture {name} does not exist")
            continue
        case = load_json(path).get("case", {})
        surviving = case.get("surviving_ranked_identity_created_at")
        absorbed = case.get("absorbed_ranked_identity_created_at")
        if surviving is None or absorbed is None:
            report.append(
                f"{name} records no creation instant for both identities, so D-564 "
                "cannot be evaluated against it"
            )
            continue
        if instant(surviving) > instant(absorbed):
            violations.append(name)
        _ = schema_accepts
    expected_violation = "consolidation-plan.invalid-newer-identity-survives.json"
    if expected_violation not in violations:
        report.append(
            f"{expected_violation} does not violate the D-564 ordering, so the check "
            "that the older identity survives is passing on data written to break it"
        )
    for name in violations:
        if name != expected_violation:
            report.append(
                f"{name} retires the older ranked identity and keeps the newer, which "
                "D-564 refuses"
            )

    # 4. No surface sums two accounts. This is phrased over the property names each
    #    consolidation schema declares rather than over the absence of an operation,
    #    because the previous form of this rule was satisfied by the API declaring no
    #    consolidation operation at all.
    swept = 0
    for name in CONSOLIDATION_RESPONSE_SCHEMAS:
        definition = schemas.get(name)
        if definition is None:
            report.append(
                f"openapi-v1.yaml declares no {name}; the consolidation surface it "
                "belongs to cannot be checked for a combined figure"
            )
            continue
        swept += 1
        for prop in definition.get("properties") or {}:
            if SUMMED_FIGURE_PATTERN.search(prop):
                report.append(
                    f"{name}.{prop} publishes a combined figure for two accounts, "
                    "which D-070 forbids"
                )
        for prop, node in (definition.get("properties") or {}).items():
            if not isinstance(node, dict) or node.get("type") != "integer":
                continue
            if not prop.endswith("_count") and prop not in ("revision",):
                report.append(
                    f"{name}.{prop} is a bare integer on the consolidation surface; "
                    "every quantity published here is a count of rows, and a figure "
                    "that is not is the summation D-070 forbids"
                )
    for pointer, definition in _walk_definitions(schema):
        for prop in definition.get("properties") or {}:
            if SUMMED_FIGURE_PATTERN.search(prop):
                report.append(
                    f"consolidation-plan-v1.schema.json{pointer}.{prop} holds a "
                    "combined figure for two accounts, which D-070 forbids"
                )

    # 5. Every participant-driven transition of this cluster has a route, and the route
    #    demands the authentication strength the transition declares.
    for machine_id in ("account-consolidation", "linked-identity"):
        machine = machines.get(machine_id)
        if machine is None:
            report.append(f"the registry declares no {machine_id} machine")
            continue
        for transition in machine["transitions"]:
            if transition["actor"] != "user":
                continue
            key = (machine_id, transition["transition_id"])
            operation_id = PARTICIPANT_OPERATIONS.get(key)
            if operation_id is None:
                report.append(
                    f"{machine_id}.{transition['transition_id']} is performed by the "
                    "participant and no API operation reaches it, so the lifecycle "
                    "requires a person to do something the contract gives them no way "
                    "to do"
                )
                continue
            operation = _operation_by_id(spec, operation_id)
            if operation is None:
                report.append(
                    f"{machine_id}.{transition['transition_id']} names operation "
                    f"{operation_id}, which openapi-v1.yaml does not declare"
                )
                continue
            required = operation.get("x-recent-auth") == "required"
            if required != bool(transition["recent_auth"]):
                report.append(
                    f"{operation_id} declares x-recent-auth "
                    f"{operation.get('x-recent-auth')!r} and "
                    f"{machine_id}.{transition['transition_id']} declares recent_auth "
                    f"{transition['recent_auth']}"
                )
    # A mapping entry for a transition that no longer has a user actor is an excuse
    # outliving its hole, and would keep the rule above looking covered.
    for (machine_id, transition_id), operation_id in sorted(
        PARTICIPANT_OPERATIONS.items()
    ):
        machine = machines.get(machine_id)
        if machine is None:
            continue
        found = [
            transition
            for transition in machine["transitions"]
            if transition["transition_id"] == transition_id
        ]
        if not found:
            report.append(
                f"{machine_id} declares no transition {transition_id}, but "
                f"{operation_id} is recorded as its route"
            )
        elif found[0]["actor"] != "user":
            report.append(
                f"{machine_id}.{transition_id} is no longer performed by the "
                f"participant, but {operation_id} is still recorded as its route"
            )

    return {"consolidation domains": len(CONSOLIDATION_DOMAINS), "swept schemas": swept}


def _walk_definitions(schema: dict, pointer: str = ""):
    """Every object node of a JSON Schema that declares properties."""
    if isinstance(schema, dict):
        if "properties" in schema:
            yield pointer, schema
        for key, value in schema.items():
            yield from _walk_definitions(value, f"{pointer}/{key}")
    elif isinstance(schema, list):
        for index, value in enumerate(schema):
            yield from _walk_definitions(value, f"{pointer}/{index}")


def _operation_by_id(spec: dict, operation_id: str) -> dict | None:
    for item in spec["paths"].values():
        for operation in item.values():
            if (
                isinstance(operation, dict)
                and operation.get("operationId") == operation_id
            ):
                return operation
    return None


# ---------------------------------------------------------------------------
# Stage registry
# ---------------------------------------------------------------------------

STAGES: dict[str, Callable[[list[str]], dict[str, int]]] = {
    "provider-registry": stage_provider_registry,
    "oauth-transaction": stage_oauth_transaction,
    "linked-identity": stage_linked_identity,
    "ranked-identity": stage_ranked_identity,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        action="append",
        choices=sorted(STAGES),
        help="run one stage; repeatable. Every stage runs when omitted.",
    )
    arguments = parser.parse_args()
    selected = arguments.stage or sorted(STAGES)

    report: list[str] = []
    counts: dict[str, int] = {}
    try:
        for name in selected:
            counts.update(STAGES[name](report))
    except Failure as failure:
        print(
            f"OAuth and identity contract validation: FAIL\n- {failure}",
            file=sys.stderr,
        )
        return 1
    if report:
        print("OAuth and identity contract validation: FAIL", file=sys.stderr)
        for line in report:
            print(f"- {line}", file=sys.stderr)
        return 1
    summary = ", ".join(f"{value} {key}" for key, value in sorted(counts.items()))
    print(f"OAuth and identity contract validation: PASS ({summary})")
    print(
        "claim_scope=record-agreement-only; no authorization request, callback, "
        "recovery or consolidation has been executed by anything in this repository"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
