#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import subprocess
import sys
from typing import TypeAlias

from eval_validation import (
    FixtureBinding,
    ReadySuite,
    VERSION,
    evidence_is_current,
    require_suite_id,
    result_path,
    timestamp,
    validate_fixture_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FIELDS = frozenset(
    {
        "id",
        "owner",
        "blocking_milestone",
        "status",
        "reason",
        "authority_class",
        "evidence_ceiling",
    }
)
BASELINE_FILENAME = "status-baseline-v1.json"
AUTHORITY_REGISTRY = "conformance/p1140f/artifact-authority-v1.json"
STATUSES = frozenset({"ready", "not_applicable"})
# The ceiling a suite may claim on the strength of its fixture manifest alone, when
# the manifest declares none of its own. A manifest binds fixture digests to a
# command; that supports consistency with those fixtures and nothing above it.
UNDECLARED_MANIFEST_CEILING = "fixture-consistent"
JsonValue: TypeAlias = (
    str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
)
Suite = dict[str, str | list[str]]


def parse_registry(path: Path) -> dict[str, Suite]:
    text = path.read_text()
    stripped = text.lstrip()
    records = (
        parse_json_registry(stripped)
        if stripped.startswith("{")
        else parse_yaml_registry(text)
    )
    suites: dict[str, Suite] = {}
    for record in records:
        add_suite(suites, record)
    return suites


def parse_json_registry(text: str) -> list[dict[str, JsonValue]]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON registry: {error.msg}") from error
    if not isinstance(document, dict) or document.get("version") != "1":
        raise ValueError("registry must declare version '1'")
    records = document.get("suites")
    if not isinstance(records, list) or not records:
        raise ValueError("registry must declare a nonempty suites list")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("each registry suite must be an object")
    return records


def parse_yaml_registry(text: str) -> list[dict[str, JsonValue]]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] != "version: 1" or lines[1] != "suites:":
        raise ValueError("registry must start with version: 1 and suites:")
    records: list[dict[str, JsonValue]] = []
    current: dict[str, JsonValue] | None = None
    for line_number, line in enumerate(lines[2:], start=3):
        if not line:
            continue
        is_entry = line.startswith("- ")
        if is_entry:
            if current is not None:
                records.append(current)
            current = {}
            line = line[2:]
        if current is None or (not is_entry and not line.startswith("  ")):
            raise ValueError(f"invalid registry syntax at line {line_number}")
        key, separator, value = line.strip().partition(": ")
        if not separator or not key:
            raise ValueError(f"invalid registry field at line {line_number}")
        if key in current:
            raise ValueError(f"duplicate registry field {key!r} at line {line_number}")
        current[key] = parse_yaml_value(key, value, line_number)
    if current is None:
        raise ValueError("registry has no suites")
    records.append(current)
    return records


def parse_yaml_value(key: str, value: str, line_number: int) -> JsonValue:
    if key in {
        "command",
        "cases",
        "fixture_ids",
        "not_applicable_until",
    } and value.startswith("["):
        try:
            return json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"invalid {key} list at line {line_number}: {error.msg}"
            ) from error
    if key == "command":
        try:
            return shlex.split(value)
        except ValueError as error:
            raise ValueError(
                f"invalid command at line {line_number}: {error}"
            ) from error
    if key == "case_id":
        return [value]
    if value in {'""', "''"}:
        return ""
    return value


def add_suite(suites: dict[str, Suite], record: dict[str, JsonValue]) -> None:
    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        raise ValueError(f"missing required metadata: {sorted(missing)}")
    # authority_class and evidence_ceiling are required by
    # scripts/repository/validate_p1140f_authority.py, which enforces the evidence
    # ceilings in docs/planning/ARTIFACT_POLICY.md. They are declarative only and
    # carry no execution semantics here. Rejecting them made the two validators
    # mutually unsatisfiable: one required exactly what the other forbade.
    allowed = REQUIRED_FIELDS | {
        "command",
        "cases",
        "case_id",
        "fixture_manifest",
        "fixture_ids",
        "authority_class",
        "evidence_ceiling",
        "scope_note",
        "not_applicable_until",
    }
    extra = record.keys() - allowed
    if extra:
        raise ValueError(f"unknown registry metadata: {sorted(extra)}")
    if not all(
        isinstance(record[field], str) and record[field].strip()
        for field in REQUIRED_FIELDS - {"reason"}
    ):
        raise ValueError("required suite metadata must be nonempty strings")
    suite_id = record["id"]
    status = record["status"]
    reason = record["reason"]
    if (
        not isinstance(suite_id, str)
        or not isinstance(status, str)
        or not isinstance(reason, str)
    ):
        raise ValueError("suite metadata must be strings")
    require_suite_id(suite_id)
    if status not in {"ready", "not_applicable"}:
        raise ValueError(f"invalid suite status for {suite_id}: {status}")
    if suite_id in suites:
        raise ValueError(f"duplicate suite id: {suite_id}")
    match status:
        case "ready":
            if reason:
                raise ValueError(f"ready suite {suite_id} requires a blank reason")
            if "not_applicable_until" in record:
                raise ValueError(
                    f"ready suite {suite_id} cannot declare not_applicable_until"
                )
            command = record.get("command")
            cases = record.get("cases", record.get("case_id"))
            fixture_manifest = record.get("fixture_manifest")
            fixture_ids = record.get("fixture_ids")
            if (
                not valid_string_list(command)
                or not valid_string_list(cases)
                or not isinstance(fixture_manifest, str)
                or not fixture_manifest
                or not valid_string_list(fixture_ids)
            ):
                raise ValueError(
                    f"ready suite {suite_id} requires command argv, case IDs, fixture_manifest, and fixture_ids"
                )
            if len(set(cases)) != len(cases) or len(set(fixture_ids)) != len(
                fixture_ids
            ):
                raise ValueError(
                    f"ready suite {suite_id} has duplicate case or fixture IDs"
                )
            suites[suite_id] = {
                "id": suite_id,
                "owner": record["owner"],
                "blocking_milestone": record["blocking_milestone"],
                "status": status,
                "reason": reason,
                "authority_class": record["authority_class"],
                "evidence_ceiling": record["evidence_ceiling"],
                "command": command,
                "cases": cases,
                "fixture_manifest": fixture_manifest,
                "fixture_ids": fixture_ids,
            }
        case "not_applicable":
            if not reason.strip():
                raise ValueError(f"not_applicable suite {suite_id} requires a reason")
            if any(
                field in record
                for field in {
                    "command",
                    "cases",
                    "case_id",
                    "fixture_manifest",
                    "fixture_ids",
                }
            ):
                raise ValueError(
                    f"not_applicable suite {suite_id} cannot declare execution metadata"
                )
            until = record.get("not_applicable_until")
            if not valid_string_list(until):
                raise ValueError(
                    f"not_applicable suite {suite_id} requires not_applicable_until: "
                    "the repository paths whose absence justifies the status"
                )
            assert isinstance(until, list)
            if len(set(until)) != len(until):
                raise ValueError(
                    f"not_applicable suite {suite_id} repeats a not_applicable_until path"
                )
            for candidate in until:
                require_repository_relative_path(suite_id, candidate)
            suites[suite_id] = {
                "id": suite_id,
                "owner": record["owner"],
                "blocking_milestone": record["blocking_milestone"],
                "status": status,
                "reason": reason,
                "authority_class": record["authority_class"],
                "evidence_ceiling": record["evidence_ceiling"],
                "not_applicable_until": until,
            }
        case unreachable:
            raise AssertionError(unreachable)


def valid_string_list(value: JsonValue | None) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item for item in value)
    )


def require_repository_relative_path(suite_id: str, candidate: str) -> None:
    """A not_applicable_until entry must name a place inside this repository.

    It is allowed to name something that does not exist — that is the entire point
    — so this checks shape rather than existence: no absolute paths, no traversal,
    no Windows separators, and no trailing slash that would make two spellings of
    the same directory look like two different components.
    """
    path = PurePosixPath(candidate)
    if (
        path.is_absolute()
        or "\\" in candidate
        or candidate != candidate.strip()
        or candidate.endswith("/")
        or ".." in path.parts
    ):
        raise ValueError(
            f"not_applicable suite {suite_id} declares an unusable "
            f"not_applicable_until path: {candidate!r}"
        )


def introduced_components(suites: dict[str, Suite], root: Path) -> list[str]:
    """Report every not_applicable suite whose named component now exists.

    `docs/verification/EVAL_SYSTEM.md` says not_applicable "must not be used after
    the owning component is introduced". `not_applicable_until` is what makes that
    rule checkable: each suite names the paths whose absence is its justification,
    so the justification is falsified the moment one of them appears. Any one path
    is enough — a suite that names both an implementation and its fixtures is
    claiming neither exists.
    """
    failures: list[str] = []
    for suite_id, suite in suites.items():
        if suite["status"] != "not_applicable":
            continue
        until = suite["not_applicable_until"]
        assert isinstance(until, list)
        present = [name for name in until if (root / name).exists()]
        if present:
            failures.append(
                f"suite {suite_id} is not_applicable but its owning component exists: "
                f"{', '.join(present)}; give it a command or restate the justification"
            )
    return failures


def load_authority_vocabulary(root: Path) -> tuple[list[str], dict[str, str]]:
    """Read the declared authority classes and the ordered evidence-ceiling ladder.

    The vocabulary lives in `conformance/p1140f/artifact-authority-v1.json`, which
    `docs/planning/ARTIFACT_POLICY.md` owns in prose. It is read rather than
    duplicated here, because a validator carrying its own copy of a vocabulary is
    the mechanism by which a registry and its checker drift apart — which is the
    defect `PF-056` records between this file and `validate_p1140f_authority.py`.

    Fails closed: an unreadable or incoherent vocabulary is a broken constraint, and
    the only safe reading of a broken constraint is that it is violated.
    """
    document = json.loads((root / AUTHORITY_REGISTRY).read_text())
    ceilings = document.get("evidence_ceilings")
    classes = document.get("authority_classes")
    if not isinstance(ceilings, list) or not all(
        isinstance(item, str) for item in ceilings
    ):
        raise ValueError(f"{AUTHORITY_REGISTRY} declares no evidence_ceilings ladder")
    if len(set(ceilings)) != len(ceilings):
        raise ValueError(f"{AUTHORITY_REGISTRY} repeats an evidence ceiling")
    if not isinstance(classes, dict) or not classes:
        raise ValueError(f"{AUTHORITY_REGISTRY} declares no authority_classes")
    maxima: dict[str, str] = {}
    for name, record in classes.items():
        if not isinstance(record, dict):
            raise ValueError(f"authority class {name} is not an object")
        ceiling = record.get("maximum_evidence_ceiling")
        if ceiling not in ceilings:
            raise ValueError(
                f"authority class {name} caps at {ceiling!r}, which is not a declared "
                "evidence ceiling"
            )
        maxima[name] = ceiling
    return ceilings, maxima


def manifest_supported_ceiling(root: Path, suite: Suite) -> str:
    """The highest ceiling a ready suite's fixture manifest can support.

    This is the half of the check that an empty suite used to satisfy for free. A
    manifest declaring its own `evidence_ceiling` caps the suite at that value; a
    manifest that declares fixtures and no ceiling caps it at fixture consistency;
    and a manifest with no fixtures at all caps it at `none`, so a suite cannot
    reach a ceiling by having nothing for the ceiling to be about.
    """
    relative = suite["fixture_manifest"]
    assert isinstance(relative, str)
    document = json.loads((root / relative).read_text())
    declared = document.get("evidence_ceiling")
    if isinstance(declared, str) and declared:
        return declared
    fixtures = document.get("fixtures")
    if isinstance(fixtures, list) and fixtures:
        return UNDECLARED_MANIFEST_CEILING
    return "none"


def evidence_ceiling_violations(
    suites: dict[str, Suite], root: Path, ceilings: list[str], maxima: dict[str, str]
) -> list[str]:
    """Every suite's declared ceiling must be one its own evidence can carry.

    Three caps apply and the lowest wins:

    * the ceiling must be a declared one and the class must be a declared class;
    * `authority_class` caps the ceiling, so an exploratory suite cannot claim
      normative conformance;
    * a `not_applicable` suite is capped at `none`, because it has no fixture
      manifest by construction and `docs/verification/EVAL_SYSTEM.md` says the
      status is an absence of evidence rather than a pass. A `ready` suite is
      capped by what its fixture manifest supports.

    The `not_applicable` cap is the one that matters most here. Twenty-four of the
    twenty-seven suites carry that status; before this, `authority_class` and
    `evidence_ceiling` were parsed, allowed through an allowlist, and read by
    nothing, so every one of them could have declared `production-evidence` and the
    registry would still have validated.
    """
    order = {name: index for index, name in enumerate(ceilings)}
    failures: list[str] = []
    for suite_id in sorted(suites):
        suite = suites[suite_id]
        authority_class = suite["authority_class"]
        ceiling = suite["evidence_ceiling"]
        assert isinstance(authority_class, str) and isinstance(ceiling, str)
        if authority_class not in maxima:
            failures.append(
                f"suite {suite_id} declares authority_class {authority_class!r}, which "
                f"{AUTHORITY_REGISTRY} does not declare"
            )
            continue
        if ceiling not in order:
            failures.append(
                f"suite {suite_id} declares evidence_ceiling {ceiling!r}, which "
                f"{AUTHORITY_REGISTRY} does not declare"
            )
            continue
        caps = [(maxima[authority_class], f"authority class {authority_class}")]
        if suite["status"] == "not_applicable":
            caps.append(
                (
                    "none",
                    "the not_applicable status, which is an absence of evidence and "
                    "never a pass",
                )
            )
        else:
            try:
                caps.append(
                    (
                        manifest_supported_ceiling(root, suite),
                        f"its fixture manifest {suite['fixture_manifest']}",
                    )
                )
            except (OSError, ValueError, json.JSONDecodeError) as error:
                failures.append(
                    f"suite {suite_id} is ready and its fixture manifest cannot be "
                    f"read to bound its evidence ceiling: {error}"
                )
                continue
        for cap, because in caps:
            if cap not in order:
                failures.append(
                    f"suite {suite_id} is capped at {cap!r} by {because}, which "
                    f"{AUTHORITY_REGISTRY} does not declare"
                )
            elif order[ceiling] > order[cap]:
                failures.append(
                    f"suite {suite_id} declares evidence_ceiling {ceiling} but is "
                    f"capped at {cap} by {because}"
                )
    return failures


def load_status_baseline(path: Path) -> dict[str, str]:
    """Read the recorded status ceiling, failing closed on anything unreadable.

    A baseline that cannot be parsed is not an absent constraint. It is a broken
    one, and the only safe reading of a broken constraint is that it is violated.
    """
    try:
        document = json.loads(path.read_text())
    except OSError as error:
        raise ValueError(f"unreadable status baseline {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON status baseline {path}: {error.msg}") from error
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ValueError("status baseline must declare schema_version 1")
    recorded = document.get("suites")
    if not isinstance(recorded, dict) or not recorded:
        raise ValueError("status baseline must declare a nonempty suites object")
    for suite_id, status in recorded.items():
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError(
                f"status baseline records an invalid status for {suite_id}: {status!r}"
            )
    return recorded


def status_regressions(suites: dict[str, Suite], recorded: dict[str, str]) -> list[str]:
    """Compare the registry against the recorded ceiling.

    Three things are regressions: downgrading a recorded ready suite, deleting a
    recorded suite outright, and declaring a suite the baseline never recorded.
    The last two matter because without them the gate is trivially evaded — delete
    the suite, or rename it, and the ceiling has nothing to compare against.

    Raising a suite to ready is never a regression, so improving coverage cannot
    turn validation red. Lowering the recorded ceiling afterwards stays manual.
    """
    failures: list[str] = []
    for suite_id in sorted(set(recorded) - set(suites)):
        failures.append(
            f"suite {suite_id} is recorded in the status baseline but the registry "
            "no longer declares it; removing a suite is a coverage regression"
        )
    for suite_id in sorted(set(suites) - set(recorded)):
        failures.append(
            f"suite {suite_id} is not recorded in the status baseline; record its "
            "status there so a later downgrade has something to regress against"
        )
    for suite_id in sorted(set(suites) & set(recorded)):
        status = suites[suite_id]["status"]
        if recorded[suite_id] == "ready" and status != "ready":
            failures.append(
                f"suite {suite_id} regressed from ready to {status}; a downgrade "
                "requires an explicit edit to the recorded status baseline"
            )
    return failures


def validate_registry_against_baseline(
    suites: dict[str, Suite], baseline_path: Path, root: Path
) -> int:
    """Run both registry gates and return the process exit code.

    2 means the gate could not be evaluated, 1 means it was evaluated and failed.
    """
    try:
        recorded = load_status_baseline(baseline_path)
    except ValueError as error:
        print(f"invalid eval status baseline: {error}", file=sys.stderr)
        return 2
    try:
        ceilings, maxima = load_authority_vocabulary(root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"invalid artifact authority vocabulary: {error}", file=sys.stderr)
        return 2
    failures = (
        status_regressions(suites, recorded)
        + introduced_components(suites, root)
        + evidence_ceiling_violations(suites, root, ceilings, maxima)
    )
    if failures:
        print("eval registry validation: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    ready = sorted(
        suite_id for suite_id, suite in suites.items() if suite["status"] == "ready"
    )
    liftable = sorted(
        suite_id for suite_id in ready if recorded.get(suite_id) == "not_applicable"
    )
    print(
        f"eval registry validation: PASS ({len(suites)} suites, {len(ready)} ready, "
        f"{len(suites) - len(ready)} not_applicable)"
    )
    if liftable:
        print(
            "status baseline may be tightened; these suites are now ready: "
            + ", ".join(liftable)
        )
    print(
        "claim_scope=declared-status-and-bounded-ceiling-only; a ready suite declares "
        "an executable command, not a proven property, and a ceiling within its cap "
        "is a claim its fixtures could support rather than one they have"
    )
    return 0


def current_commit() -> str:
    value = os.getenv("GITHUB_SHA")
    if value:
        return value
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "local"


def write_result(path: Path, result: dict[str, JsonValue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite")
    parser.add_argument("--validate-registry", action="store_true")
    parser.add_argument("--list-suites", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("artifacts/evals"))
    parser.add_argument(
        "--registry", type=Path, default=ROOT / "evals/suites/suites.yaml"
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help=f"recorded status ceiling; defaults to {BASELINE_FILENAME} beside the registry",
    )
    arguments = parser.parse_args()
    if (
        not arguments.validate_registry
        and not arguments.list_suites
        and arguments.suite is None
    ):
        parser.error(
            "--suite is required unless --validate-registry or --list-suites is provided"
        )
    try:
        suites = parse_registry(arguments.registry)
    except (OSError, ValueError) as error:
        print(f"invalid eval registry: {error}", file=sys.stderr)
        return 2
    if arguments.validate_registry:
        baseline_path = (
            arguments.baseline
            if arguments.baseline is not None
            else arguments.registry.parent / BASELINE_FILENAME
        )
        return validate_registry_against_baseline(suites, baseline_path, ROOT)
    if arguments.list_suites:
        print("\n".join(suites))
        return 0
    assert arguments.suite is not None
    suite = suites.get(arguments.suite)
    if suite is None:
        print(f"unknown suite: {arguments.suite}", file=sys.stderr)
        return 2
    commit = current_commit()
    output = result_path(arguments.out, arguments.suite, commit)
    started_at = timestamp()
    result: dict[str, JsonValue] = {
        "version": VERSION,
        "suite": arguments.suite,
        "commit": commit,
        "status": "fail",
        "reason": suite["reason"],
        "cases": [],
        "evidence_paths": [],
        "started_at": started_at,
        "finished_at": started_at,
    }
    match suite["status"]:
        case "not_applicable":
            # A suite may only report not_applicable while the component it names is
            # still absent. Once that component exists the status is a false claim of
            # inapplicability, so the run fails rather than reporting a benign skip.
            stale = introduced_components({arguments.suite: suite}, ROOT)
            if stale:
                result["reason"] = stale[0]
            else:
                result["status"] = "not_applicable"
        case "ready":
            command = suite["command"]
            cases = suite["cases"]
            fixture_manifest = suite["fixture_manifest"]
            fixture_ids = suite["fixture_ids"]
            assert isinstance(command, list) and all(
                isinstance(item, str) for item in command
            )
            assert isinstance(cases, list) and all(
                isinstance(item, str) for item in cases
            )
            assert isinstance(fixture_manifest, str)
            assert isinstance(fixture_ids, list) and all(
                isinstance(item, str) for item in fixture_ids
            )
            result["cases"] = [{"id": case, "status": "fail"} for case in cases]
            ready = ReadySuite(
                arguments.suite,
                tuple(command),
                tuple(cases),
                Path(fixture_manifest),
                tuple(fixture_ids),
            )
            try:
                binding = validate_fixture_manifest(ready)
            except (OSError, ValueError) as error:
                result["reason"] = f"Ready suite fixture manifest is invalid: {error}"
            else:
                if tuple(command) != binding.command:
                    result["reason"] = (
                        "Declared behavioral command does not match fixture manifest command."
                    )
                else:
                    try:
                        completed = subprocess.run(
                            substitute_commit(command, commit),
                            cwd=ROOT,
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                    except OSError as error:
                        result["reason"] = (
                            f"Declared behavioral command could not start: {error}"
                        )
                    else:
                        if completed.returncode == 0:
                            try:
                                evidence: JsonValue = json.loads(completed.stdout)
                            except json.JSONDecodeError:
                                evidence = None
                            validate_evidence_result(
                                evidence, ready, commit, binding, output, result
                            )
                        else:
                            result["reason"] = (
                                "Declared behavioral command failed validation."
                            )
                            if completed.stderr:
                                print(completed.stderr, end="", file=sys.stderr)
        case unreachable:
            raise AssertionError(unreachable)
    result["finished_at"] = timestamp()
    write_result(output, result)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in {"pass", "not_applicable"} else 1


def validate_evidence_result(
    evidence: JsonValue,
    ready: ReadySuite,
    commit: str,
    binding: FixtureBinding,
    output: Path,
    result: dict[str, JsonValue],
) -> None:
    if not evidence_is_current(evidence, ready, commit, binding):
        result["reason"] = (
            "Declared behavioral command returned invalid current evidence."
        )
        return
    evidence_name = "evidence.json"
    write_result(output.with_name(evidence_name), evidence)
    result["status"] = "pass"
    result["reason"] = (
        "Declared behavioral command produced validated current evidence."
    )
    result["cases"] = [
        {"id": case, "status": "pass", "evidence": evidence_name}
        for case in ready.case_ids
    ]
    result["evidence_paths"] = [evidence_name]


def substitute_commit(command: list[str], commit: str) -> list[str]:
    return [commit if argument == "{commit}" else argument for argument in command]


if __name__ == "__main__":
    raise SystemExit(main())
