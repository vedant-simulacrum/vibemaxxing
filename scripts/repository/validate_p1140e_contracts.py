#!/usr/bin/env python3
"""Validate P-1140E structural consistency without claiming semantic or runtime proof."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_p1140e_coverage  # noqa: E402  (path set immediately above)

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
CONF = ROOT / "conformance" / "p1140e"
TRACE = ROOT / "docs" / "planning" / "decision-traceability"


class Failure(RuntimeError):
    pass


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


_COLUMN_RE = re.compile(
    r"(?im)^\s{2}([a-z_][a-z0-9_]*)\s+"
    r"(?:uuid|text|bytea|bigint|integer|smallint|boolean|timestamptz|numeric|jsonb|inet)\b"
)


def planning_table_columns(sql: str) -> dict[str, set[str]]:
    """Map every planning table to the column names it declares.

    The race plans name column values, and a plan naming a column that no longer
    exists is the failure mode that made the previous version of that file worth
    nothing: it read as a specification and resolved against nothing.
    """
    columns: dict[str, set[str]] = {}
    starts = list(re.finditer(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(", sql))
    for position, match in enumerate(starts):
        end = starts[position + 1].start() if position + 1 < len(starts) else len(sql)
        body = sql[match.end() : end]
        body = "\n".join(
            line for line in body.splitlines() if not line.lstrip().startswith("--")
        )
        columns[match.group(1)] = {
            found.group(1) for found in _COLUMN_RE.finditer(body)
        }
    return columns


def main() -> int:
    schema = load_json(CONF / "validation-matrix-v1.schema.json")
    matrix = load_json(CONF / "validation-matrix-v1.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            matrix
        ),
        key=lambda item: list(item.absolute_path),
    )
    require(
        not errors,
        "validation matrix schema failure: " + "; ".join(e.message for e in errors[:8]),
    )
    require(
        matrix["maturity"] == "planning-validation-only",
        "matrix must remain planning-validation-only",
    )

    decision_text = (ROOT / "docs/planning/DECISION_REGISTER.md").read_text(
        encoding="utf-8"
    )
    decision_statuses: dict[str, str] = {}
    allowed = {
        "accepted",
        "provisional",
        "research-required",
        "deferred",
        "rejected",
        "superseded",
    }
    for line in decision_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if (
            len(cells) >= 3
            and re.fullmatch(r"D-\d{3}", cells[0])
            and cells[2] in allowed
        ):
            decision_statuses[cells[0]] = cells[2]

    # P-1140E froze structural traceability for D-001..D-069. Later P-1140F
    # decisions may extend the register, but they are owned by the P-1140F
    # authority validator and must not silently expand this historical matrix.
    expected_decisions = {f"D-{number:03d}" for number in range(1, 70)}
    require(
        expected_decisions <= set(decision_statuses),
        "decision register no longer contains every D-001..D-069 decision",
    )

    bindings = {item["decision_id"]: item for item in matrix["decision_bindings"]}
    require(
        set(bindings) == expected_decisions,
        "P-1140E matrix decision set is not exactly D-001..D-069",
    )
    for decision_id in sorted(expected_decisions):
        status = decision_statuses[decision_id]
        binding = bindings[decision_id]
        require(
            binding["decision_status"] == status, f"status mismatch for {decision_id}"
        )
        require(
            binding["active"] == (status in {"accepted", "provisional"}),
            f"active-path mismatch for {decision_id}",
        )
        for field in (
            "normative_owner",
            "work_unit",
            "schema_or_state_owner",
            "platform_scope",
            "fixture_path",
        ):
            require(bool(binding[field]), f"{decision_id} lacks {field}")
            require(
                (ROOT / binding[field].split("#", 1)[0]).exists(),
                f"{decision_id} references missing {field}",
            )

    trace_ids: list[str] = []
    for path in sorted(TRACE.glob("D-*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\|\s*(D-\d{3})\s*\|", line)
            if match:
                trace_ids.append(match.group(1))
    require(
        expected_decisions <= set(trace_ids),
        "traceability files no longer cover every D-001..D-069 decision",
    )
    require(
        len(trace_ids) == len(set(trace_ids)), "duplicate decision traceability row"
    )

    required_domains = {
        "decision-traceability",
        "protocol-exact-bytes",
        "protocol-malformed-resource",
        "accounting",
        "privacy-boundaries",
        "oauth-session-identity",
        "api-idempotency-rate",
        "sql-constraints-races",
        "ranking-pricing",
        "social-moderation",
        "export-deletion",
        "platform-profile-coverage",
        "platform-runtime-evidence",
        "release-update",
        "reason-policy-references",
        "registry-references",
        "current-future-paths",
        "clean-checkout",
    }
    require(
        {item["domain_id"] for item in matrix["validation_domains"]}
        == required_domains,
        "validation domain set mismatch",
    )
    for domain in matrix["validation_domains"]:
        for path in domain["authorities"] + domain["fixtures"]:
            require(
                (ROOT / path).exists(),
                f"{domain['domain_id']} references missing path {path}",
            )

    spec = yaml.safe_load((SCHEMAS / "openapi-v1.yaml").read_text(encoding="utf-8"))
    operation_ids: list[str] = []
    for item in spec["paths"].values():
        for method, operation in item.items():
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                operation_ids.append(operation["operationId"])
    require(
        len(operation_ids) == len(set(operation_ids)), "duplicate OpenAPI operationId"
    )
    require(
        set(matrix["api_operations"]) == set(operation_ids),
        "matrix does not cover every API operation",
    )
    github_callback = spec["paths"]["/auth/github/callback"]["get"]
    github_parameters = {item["$ref"] for item in github_callback["parameters"]}
    require(
        "#/components/parameters/OAuthIssuer" in github_parameters,
        "GitHub callback lacks RFC 9207 issuer parameter",
    )
    device_start = spec["components"]["schemas"]["DeviceAuthStartRequest"]
    require(
        "profile_id" in device_start["required"],
        "device authorization lacks registered profile binding",
    )
    semantic_fixtures = load_json(
        ROOT / "conformance" / "p1140f" / "semantic-fixtures-v1.json"
    )
    providers = semantic_fixtures["oauth_providers"]
    require(
        {provider["provider_id"] for provider in providers} == {"github", "x"},
        "launch OAuth provider fixtures mismatch",
    )
    for provider in providers:
        require(
            provider["pkce_required"],
            f"OAuth provider lacks PKCE requirement: {provider['provider_id']}",
        )
        require(
            provider["authorization_response_iss_supported"] is False,
            f"unsupported issuer-capability fixture: {provider['provider_id']}",
        )
        require(
            "redirect-confusion-rejected" in provider["negative_cases"],
            f"OAuth provider lacks redirect confusion negative: {provider['provider_id']}",
        )
    device_fixtures = semantic_fixtures["device_authorization"]
    require(
        device_fixtures["positive_case"] == "registered-headless-interactive-profile",
        "device authorization positive fixture is over-broad",
    )
    require(
        {"ordinary-desktop-profile-rejected", "ci-profile-rejected"}
        <= set(device_fixtures["negative_cases"]),
        "device authorization lacks desktop or CI negative fixture",
    )

    state_registry = load_json(SCHEMAS / "state-machine-registry-v1.json")
    machines = {item["machine_id"]: item for item in state_registry["machines"]}
    require(
        "interactive-shell" in machines,
        "interactive shell lacks authoritative state machine",
    )
    require(
        set(matrix["state_machines"]) == set(machines),
        "matrix does not cover every state machine",
    )
    state_fixtures = load_json(CONF / "state-machine-fixtures-v1.json")
    fixture_machines = {item["machine_id"]: item for item in state_fixtures["machines"]}
    require(set(fixture_machines) == set(machines), "state fixture set mismatch")
    for machine_id, fixture in fixture_machines.items():
        transitions = {
            item["transition_id"]: item for item in machines[machine_id]["transitions"]
        }
        positive = fixture["positive"]
        require(
            positive["transition_id"] in transitions,
            f"unknown positive transition for {machine_id}",
        )
        transition = transitions[positive["transition_id"]]
        require(
            positive["from"] in transition["from"]
            and positive["expected_to"] == transition["to"],
            f"invalid positive fixture for {machine_id}",
        )
        negative = fixture["negative"]
        require(
            negative["from"] not in transition["from"],
            f"negative fixture is legal for {machine_id}",
        )

    sql = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
    tables = set(re.findall(r"(?im)^create\s+table\s+([a-z_][a-z0-9_]*)\s*\(", sql))
    columns = planning_table_columns(sql)
    races = load_json(CONF / "sql-race-plans-v1.json")
    required_races = {
        "oauth-single-consume",
        "refresh-parent-reuse",
        "challenge-single-use",
        "idempotency-same-bytes",
        "idempotency-conflict",
        "device-sequence-fork",
        "friend-cross-request",
        "block-race",
        "board-owner-transfer",
        "ranking-generation-promote",
        "moderation-appeal-reversal",
        "deletion-export-race",
        "local-delete-ack",
        "release-promote-rollback",
        # PF-020. The ambiguous-commit family: the five moments at which a client
        # and a server can disagree about whether a mutation happened.
        "commit-crash-before-commit",
        "commit-crash-after-commit",
        "commit-dropped-response",
        "commit-executing-takeover",
        "commit-key-expiry",
    }
    require(
        {item["case_id"] for item in races["cases"]} == required_races,
        "SQL race plan set mismatch",
    )
    # PF-020. Every case names the rows a correct implementation leaves behind.
    #
    # All fourteen original cases carried the same four generic interleaving steps
    # -- lock, conflict, commit, recheck -- and one sentence of prose. That
    # described a scenario and asserted nothing: no row, no column, no value, so
    # nothing about it could be wrong. The checks below make the plan resolve
    # against the schema it plans against.
    seen_interleavings: dict[tuple[str, ...], str] = {}
    for case in races["cases"]:
        case_id = case["case_id"]
        require(
            set(case["tables"]) <= tables,
            f"SQL race references unknown table: {case_id}",
        )
        require(
            case["execution_state"] == "planned-runtime-evidence",
            "SQL race plan overclaims execution",
        )

        steps = tuple(case["interleaving"])
        require(
            len(steps) >= 4,
            f"SQL race plan states fewer than four steps: {case_id}",
        )
        require(
            len(set(steps)) == len(steps),
            f"SQL race plan repeats an interleaving step: {case_id}",
        )
        # The copy-paste that made the file vacuous is refused directly. Two cases
        # with the same interleaving are one case written twice.
        require(
            steps not in seen_interleavings,
            f"SQL race plans share one interleaving: {case_id} and "
            f"{seen_interleavings.get(steps)}",
        )
        seen_interleavings[steps] = case_id

        rows = case.get("residual_rows") or []
        require(
            bool(rows),
            f"SQL race plan names no residual rows: {case_id}",
        )
        require(
            sorted({row["table"] for row in rows}) == list(case["tables"]),
            f"SQL race plan tables disagree with its residual rows: {case_id}",
        )
        presences = {row["presence"] for row in rows}
        require(
            presences <= {"present", "absent"},
            f"SQL race plan states an unknown presence: {case_id}",
        )
        # A recovery plan that only says what survives, or only says what does not,
        # is half a plan: the defect this file exists to refuse is always a row that
        # is there and should not be, or the reverse.
        require(
            presences == {"present", "absent"},
            f"SQL race plan states no present and absent pair: {case_id}",
        )
        for row in rows:
            require(
                bool(row.get("key")) and bool(row.get("note")),
                f"SQL race residual row states no key or no note: {case_id}",
            )
            if row["presence"] == "absent":
                require(
                    "columns" not in row,
                    f"SQL race plan describes the columns of an absent row: {case_id}",
                )
                continue
            stated = row.get("columns") or {}
            require(
                bool(stated),
                f"SQL race present row names no column values: {case_id}",
            )
            unknown = sorted(set(stated) - columns[row["table"]])
            require(
                not unknown,
                f"SQL race residual row names columns {row['table']} does not "
                f"define: {case_id} {unknown}",
            )

    platform_registry = load_json(SCHEMAS / "platform-profile-registry-v1.json")
    source_ids: set[str] = set()
    for source in platform_registry["sources"]:
        required_source_fields = {
            "source_id",
            "canonical_uri",
            "authority",
            "source_version",
            "retrieved_at",
            "content_sha256",
            "supported_fields",
        }
        require(
            required_source_fields <= set(source),
            f"platform source lacks immutable evidence fields: {source.get('source_id')}",
        )
        require(
            source["source_id"] not in source_ids,
            f"duplicate platform source: {source['source_id']}",
        )
        source_ids.add(source["source_id"])
        require(
            len(source["content_sha256"]) == 64,
            f"platform source digest is not SHA-256: {source['source_id']}",
        )
        require(
            "/blob/main/" not in source["canonical_uri"],
            f"platform source uses moving branch URI: {source['source_id']}",
        )
    profiles = {item["profile_id"]: item for item in platform_registry["profiles"]}
    require(
        set(matrix["platform_profiles"]) == set(profiles),
        "matrix does not cover every platform profile",
    )
    plan = load_json(CONF / "platform-validation-plan-v1.json")
    planned_profiles = {item["profile_id"]: item for item in plan["profiles"]}
    require(
        set(planned_profiles) == set(profiles), "platform validation plan set mismatch"
    )
    for profile_id, planned in planned_profiles.items():
        source = profiles[profile_id]
        require(
            not source["advertised"] and not planned["advertised"],
            f"uncertified profile advertised: {profile_id}",
        )
        expected = {
            (item["case_id"], item["applicability"], item["expected"])
            for item in source["failure_matrix"]
        }
        actual = {
            (item["case_id"], item["applicability"], item["expected"])
            for item in planned["cases"]
        }
        require(actual == expected, f"platform case mismatch: {profile_id}")
        require(
            all(
                item["execution_state"] == "planned-runtime-evidence"
                for item in planned["cases"]
            ),
            f"platform plan overclaims execution: {profile_id}",
        )

    # The non-aggregate authorities are read from the registry rather than listed
    # here. They were hard-coded, which meant a reader of reason-codes-v1.json saw
    # `state_machine: "vibeproof-v1"` with no way to tell it was not a machine, and
    # the list had drifted: `device-lineage-v1` was permitted and used by no code.
    reason_registry = load_json(SCHEMAS / "reason-codes-v1.json")
    non_aggregate = set(reason_registry["non_aggregate_authorities"])
    require(
        not (non_aggregate & set(machines)),
        "a non-aggregate authority shadows a registered machine",
    )
    allowed_authorities = set(machines) | non_aggregate
    used = {item["state_machine"] for item in reason_registry["codes"]}
    for item in reason_registry["codes"]:
        require(
            item["state_machine"] in allowed_authorities,
            f"reason authority does not resolve: {item['code']}",
        )
    # A declared exemption that nothing uses is a stale excuse, which is how
    # `device-lineage-v1` survived being permitted long after it stopped applying.
    unused = sorted(non_aggregate - used)
    require(
        not unused, f"non-aggregate authority declared and used by no code: {unused}"
    )

    forbidden = [
        ROOT / "apps/android",
        ROOT / "apps/ios",
        ROOT / "apps/ipados",
        ROOT / "apps/chromeos",
        ROOT / "packages/android",
        ROOT / "packages/ios",
        ROOT / "packages/ipados",
        ROOT / "packages/chromeos",
    ]
    require(
        not any(path.exists() for path in forbidden),
        "out-of-scope native mobile implementation path exists",
    )

    # The three coverage arrays above are projections of live registries, so they are
    # derived rather than typed. The set-equality checks say they cover everything;
    # this says nobody hand-edited them into an order or a shape a regeneration would
    # not produce. PF-013's five machines had been appended rather than sorted in,
    # which set equality cannot see.
    require(
        generate_p1140e_coverage.reproducible(),
        "the P-1140E coverage arrays are not reproducible from their registries; run scripts/repository/generate_p1140e_coverage.py",
    )

    print("P-1140E structural cross-contract validation: pass")
    print(
        f"decisions={len(bindings)} operations={len(operation_ids)} machines={len(machines)} profiles={len(profiles)} races={len(races['cases'])}"
    )
    print(
        "claim_scope=structural-consistency-only semantic_gate=P-1140F-open runtime_evidence=absent"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            f"P-1140E structural cross-contract validation: FAIL: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1)
