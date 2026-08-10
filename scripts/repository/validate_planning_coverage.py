#!/usr/bin/env python3
"""Validate repaired P-1140D planning coverage and launch scope.

This proves declared structural coverage only. It is not evidence that any
covered surface is implemented, correct, or launch-ready.
"""

from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
INVENTORY = ROOT / "docs" / "planning" / "SCHEMA_AND_INTERFACE_INVENTORY.md"

# The two trees the inventory answers for. Every file under them is a machine
# contract, a fixture or a registry, and the inventory is the file that says which
# specification family owns it.
INVENTORIED_TREES = ("packages/schemas", "conformance")

# Directories whose contents are enumerated bidirectionally by another check, so
# restating them row by row here would put a second owner on one vocabulary. Each
# entry names the file and the symbol that performs the enumeration; the delegation
# is refused when the delegate is gone, because an excuse that outlives its hole is
# how a coverage claim survives the loss of the thing that made it true.
DELEGATED_COVERAGE = (
    (
        "packages/schemas/examples/",
        "scripts/repository/validate_planning_artifacts.py",
        "def validate_schema_example_coverage(",
    ),
    (
        "conformance/<suite>/ where the suite declares manifest.json",
        "scripts/repository/validate_planning_artifacts.py",
        "def validate_conformance_manifests(",
    ),
)

# The inventory must say what it is. PF-029's shape — a `grep` for a word that had
# never appeared, passing because the corpus was empty — is refused by requiring the
# statement in exact literals as well as refusing the overclaims. A check that only
# forbids passes on an empty file.
INVENTORY_MATURITY_LITERALS = (
    "declared coverage only, not implementation evidence",
    "This inventory records declared ownership. It is not evidence that any listed "
    "contract is implemented, exercised, correct, or launch-ready.",
)

# Phrases that assert more than declared ownership. `complete` and `completeness` are
# deliberately absent: the inventory's completeness *rule* is what it exists to state,
# and a bare substring ban on the word would have forced the rule to be deleted to
# satisfy a check about overclaiming.
INVENTORY_FORBIDDEN_CLAIMS = (
    "closed-world",
    "closed world",
    "complete coverage",
    "coverage is complete",
    "fully covered",
    "covers every",
    "implementation-ready",
    "launch-ready",
    "production-ready",
    "conformance proven",
    "no gaps remain",
)

REQUIRED_PATHS = {
    "/auth/github/start",
    "/auth/github/callback",
    "/auth/x/start",
    "/auth/x/callback",
    "/auth/device/start",
    "/auth/device/poll",
    "/auth/device/exchange",
    "/sessions",
    "/sessions/{id}/revoke",
    "/identities",
    "/identities/link",
    "/identities/unlink",
    "/devices",
    "/devices/enroll",
    "/devices/{id}/rotate",
    "/devices/{id}/revoke",
    "/claim-challenges",
    "/claim-batches",
    "/claims/{id}",
    "/leaderboards/{scope}/{period}",
    "/rank/me",
    "/profiles/{handle}",
    "/me",
    "/friends",
    "/friend-requests",
    "/blocks",
    "/rivals",
    "/boards",
    "/boards/{id}/invitations",
    "/organizations",
    "/communities",
    "/presence",
    "/notifications",
    "/moderation/cases",
    "/appeals",
    "/exports",
    "/deletion-requests",
    "/pricing-datasets",
    "/compatibility",
}

REQUIRED_TABLES = {
    "accounts",
    "account_handles",
    "linked_identities",
    "web_sessions",
    "recovery_codes",
    "optional_authenticators",
    "oauth_transactions",
    "devices",
    "device_keys",
    "device_enrollment_grants",
    "adapter_installations",
    "claim_challenges",
    "device_sequences",
    "claims",
    "claim_payloads",
    "claim_rejections",
    "claim_corrections",
    "quarantines",
    "evidence_assessments",
    "moderation_cases",
    "moderation_actions",
    "appeals",
    "periods",
    "minute_scores",
    "period_scores",
    "score_snapshots",
    "ranking_corrections",
    "pricing_datasets",
    "pricing_entries",
    "cost_interpretations",
    "profiles",
    "friend_requests",
    "friend_edges",
    "blocks",
    "rival_edges",
    "organizations",
    "communities",
    "boards",
    "board_memberships",
    "board_invites",
    "presence_leases",
    "notifications",
    "notification_preferences",
    "outbox_events",
    "worker_checkpoints",
    "audit_events",
    "exports",
    "deletion_jobs",
    "feature_flags",
    "schema_migrations",
}

FORBIDDEN_LAUNCH_PATHS = {"/countries"}
FORBIDDEN_LAUNCH_TABLES = {"country_assertions"}

# Mutating operations that carry no `Idempotency-Key`, because the credential the request
# already presents is itself single-use and a durable request hash would be a second,
# weaker replay control layered over a stronger one. `/auth/session/refresh` joins the set
# under D-221: ADR-015 makes every refresh handle one-time-use with no grace window, so a
# repeated refresh is a replay incident rather than a retry.
IDEMPOTENCY_EXCEPTIONS = {
    ("/auth/github/start", "post"),
    ("/auth/x/start", "post"),
    ("/auth/device/start", "post"),
    ("/auth/device/poll", "post"),
    ("/auth/device/exchange", "post"),
    ("/auth/session/refresh", "post"),
    ("/claim-challenges", "post"),
}

REPAIR_TARGETS = {
    "VerifierAppraisal": (
        "packages/schemas/vibeproof-claim-v1.cddl",
        "verifier-appraisal-v1",
    ),
    "CheckpointReceipt": (
        "packages/schemas/vibeproof-claim-v1.cddl",
        "checkpoint-receipt-v1",
    ),
    "refresh-token families": (
        "packages/schemas/state-machine-registry-v1.json",
        "web-session-family",
    ),
    "durable idempotency ownership": (
        "packages/schemas/planning-schema.sql",
        "idempotency_records",
    ),
    "immutable ranking view identity": (
        "packages/schemas/ranking-view-v1.schema.json",
        "ranking_view_id",
    ),
    "exact platform support profiles": (
        "packages/schemas/platform-profile-registry-v1.json",
        "profile_id",
    ),
    "mandatory automatic updates": (
        "packages/schemas/release-set-v1.schema.json",
        "mandatory_after",
    ),
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


def inventoried_files() -> list[str]:
    """Every repository-owned file under the two inventoried trees.

    Read from Git rather than from the filesystem, because the question the check
    answers is which files this repository *ships*. A filesystem walk answers a
    different question and fails on a local scratch file, which is the fastest way
    to teach a reader that the check is noise.
    """
    try:
        listing = subprocess.run(
            ["git", "ls-files", "-z", "--", *INVENTORIED_TREES],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:  # pragma: no cover
        raise SystemExit(
            f"planning coverage: cannot list the inventoried trees from Git: {error}"
        ) from error
    return sorted(
        entry for entry in listing.stdout.decode("utf-8").split("\0") if entry
    )


def inventory_citations(text: str) -> list[str]:
    """Every backticked token in the inventory that names one of the two trees.

    A citation is a path, a directory ending in `/`, or a shell-style glob. Anything
    after a `#` is a fragment naming a table, a rule or a component inside the file
    and is not part of the path.
    """
    found: list[str] = []
    for token in re.findall(r"`([^`\n]+)`", text):
        candidate = token.strip().split("#", 1)[0].split(" ", 1)[0].strip()
        if not candidate:
            continue
        # `conformance/<suite>/` is a shape, not a path. A placeholder is the one
        # token that must not be resolved, because failing to resolve it would make
        # the sentence explaining the rule illegal under the rule.
        if "<" in candidate or ">" in candidate:
            continue
        if candidate.startswith(tuple(f"{tree}/" for tree in INVENTORIED_TREES)):
            found.append(candidate)
    return found


def check_inventory_coverage(errors: list[str]) -> None:
    """Resolve the inventory against the two trees it claims to inventory, both ways.

    Neither direction existed. `validate_planning_artifacts.py` checks that the
    inventory's rows are unique and carry a declared status, and `doctor.py` checks
    that the file is present; nothing read a single citation back against the tree.
    So the document could name a path that had been deleted, and — the direction that
    matters — a new schema, registry or fixture could be added and never appear in the
    file whose entire purpose is to say who owns it. Both were true when this ran
    first: three citations resolved to nothing, and sixty-three shipped files were
    owned by no row.
    """
    if not INVENTORY.is_file():
        errors.append("the schema and interface inventory is missing")
        return
    text = INVENTORY.read_text(encoding="utf-8")

    body = text
    for literal in INVENTORY_MATURITY_LITERALS:
        if literal not in text:
            errors.append(
                "the inventory does not carry its maturity statement, so a reader "
                f"cannot tell what the table claims: {literal!r}"
            )
        # The disclaimer is allowed to name the claims it disclaims. Nothing else
        # is, which is why the scan runs over the text with the disclaimer removed
        # rather than over the whole file.
        body = body.replace(literal, "")
    for phrase in INVENTORY_FORBIDDEN_CLAIMS:
        if phrase.lower() in body.lower():
            errors.append(
                f"the inventory claims {phrase!r}; it records declared ownership and "
                "nothing about coverage being total or any contract being ready"
            )

    for scope, delegate, symbol in DELEGATED_COVERAGE:
        path = ROOT / delegate
        if not path.is_file() or symbol not in path.read_text(encoding="utf-8"):
            errors.append(
                f"coverage of {scope} is delegated to {delegate}, which no longer "
                f"defines {symbol!r}; the delegation has outlived the check that "
                "made it true"
            )

    files = inventoried_files()
    known = set(files)
    directories = {
        parent
        for name in files
        for parent in (
            f"{part}/"
            for part in (
                str(Path(name).parent),
                *(str(ancestor) for ancestor in Path(name).parents),
            )
            if part not in {".", ""}
        )
    }

    # A directory citation is resolved but never grants coverage. It reads as an
    # owner and is not one: `conformance/planning/` appears in this file inside the
    # sentence explaining that the directory declares no manifest, and while a
    # directory citation counted, that sentence covered every file in the directory
    # it was describing as uncovered. Coverage comes from naming the file or from a
    # delegate that enumerates the directory and can refuse a new file in it.
    cited: set[str] = set()
    for citation in inventory_citations(text):
        if "*" in citation or "?" in citation:
            matched = [name for name in files if fnmatch.fnmatch(name, citation)]
            if not matched:
                errors.append(
                    f"the inventory cites the pattern {citation!r}, which matches no "
                    "file in the tree it names"
                )
            cited.update(matched)
            continue
        if citation.rstrip("/") in INVENTORIED_TREES:
            # The prose names the trees this file answers for. A tree naming itself
            # is not an owner: taking it as one made every file under it covered by
            # the sentence that said the files must be covered, which is the whole
            # check satisfied by its own description of itself.
            continue
        if citation.endswith("/"):
            if citation not in directories:
                errors.append(
                    f"the inventory cites the directory {citation!r}, which does not "
                    "exist"
                )
            continue
        if citation in known:
            cited.add(citation)
        elif f"{citation}/" not in directories:
            errors.append(
                f"the inventory cites {citation!r}, which resolves to no file and no "
                "directory"
            )

    delegated = {"packages/schemas/examples/"}
    delegated.update(
        f"{str(Path(name).parent)}/"
        for name in files
        if Path(name).name == "manifest.json"
    )

    uncovered = [
        name
        for name in files
        if name not in cited
        and not any(name.startswith(prefix) for prefix in delegated)
    ]
    if uncovered:
        errors.append(
            "the inventory names no owner for "
            f"{len(uncovered)} shipped files under {', '.join(INVENTORIED_TREES)}, so "
            "each is a contract this repository ships and no specification family "
            f"answers for: {uncovered}"
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
        errors.append(
            f"post-launch country paths remain in the launch API contract: {forbidden_paths}"
        )

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
            if (
                method in {"post", "put", "patch", "delete"}
                and (path, method) not in IDEMPOTENCY_EXCEPTIONS
            ):
                refs = [
                    parameter.get("$ref")
                    for parameter in operation.get("parameters", [])
                    if isinstance(parameter, dict)
                ]
                if "#/components/parameters/IdempotencyKey" not in refs:
                    errors.append(
                        f"mutating operation lacks Idempotency-Key: {method.upper()} {path}"
                    )
    if len(operation_ids) != len(set(operation_ids)):
        errors.append("duplicate OpenAPI operationId")

    sql = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
    tables = set(re.findall(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(", sql))
    missing_tables = sorted(REQUIRED_TABLES - tables)
    if missing_tables:
        errors.append(f"missing current planning PostgreSQL tables: {missing_tables}")
    forbidden_tables = sorted(FORBIDDEN_LAUNCH_TABLES & tables)
    if forbidden_tables:
        errors.append(
            f"post-launch country tables remain in the launch SQL contract: {forbidden_tables}"
        )
    if re.search(
        r"board_type\s+in\s*\([^)]*'country'", sql, flags=re.IGNORECASE | re.DOTALL
    ):
        errors.append("country remains an allowed launch board_type")
    if "P-1140D REPAIRED PLANNING MIGRATION CONTRACT" not in sql:
        errors.append("PostgreSQL contract lacks repaired P-1140D marker")
    if re.search(r"(?i)\bjsonb\b", sql):
        errors.append("untyped jsonb remains in the repaired SQL contract")
    if (
        "board_one_active_owner" not in sql
        or "check (account_id_a < account_id_b)" not in sql
    ):
        errors.append(
            "repaired social SQL lacks canonical pair or single-owner constraints"
        )

    check_local_trust_domains(errors)
    check_inventory_coverage(errors)

    for label, (relative_path, marker) in REPAIR_TARGETS.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        if marker.lower() not in text.lower():
            errors.append(
                f"missing P-1140 repair target for {label}: {relative_path} lacks {marker!r}"
            )

    fail(errors)
    print(
        "planning coverage: PASS "
        f"({len(REQUIRED_PATHS)} current API paths, {len(REQUIRED_TABLES)} current tables, "
        f"{len(REPAIR_TARGETS)} repaired authority targets, "
        f"{len(LOCAL_TRUST_ROLES)} local trust domains, "
        f"{len(inventoried_files())} inventoried files)"
    )
    print(
        "artifact maturity: repaired P-1140D planning contract; declared coverage only, not implementation evidence"
    )


if __name__ == "__main__":
    main()
