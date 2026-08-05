#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
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
REQUIRED_FIELDS = frozenset({"id", "owner", "blocking_milestone", "status", "reason"})
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
    if key in {"command", "cases", "fixture_ids"} and value.startswith("["):
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
            suites[suite_id] = {
                "id": suite_id,
                "owner": record["owner"],
                "blocking_milestone": record["blocking_milestone"],
                "status": status,
                "reason": reason,
            }
        case unreachable:
            raise AssertionError(unreachable)


def valid_string_list(value: JsonValue | None) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item for item in value)
    )


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
        return 0
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
