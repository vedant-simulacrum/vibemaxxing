from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[2]
VERSION: Final = "1"
MAX_EVIDENCE_AGE: Final = timedelta(hours=24)
MAX_FUTURE_SKEW: Final = timedelta(minutes=5)
SUITE_ID: Final = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
RFC3339: Final = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\Z")
SHA256: Final = re.compile(r"[0-9a-f]{64}\Z")
COMMIT: Final = re.compile(r"(?:[0-9a-f]{40,64}|local)\Z")


@dataclass(frozen=True, slots=True)
class ReadySuite:
    suite_id: str
    command: tuple[str, ...]
    case_ids: tuple[str, ...]
    fixture_manifest: Path
    fixture_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FixtureBinding:
    manifest_sha256: str
    command: tuple[str, ...]
    fixtures: tuple[tuple[str, str], ...]


def require_suite_id(value: str) -> None:
    if SUITE_ID.fullmatch(value) is None:
        raise ValueError(f"suite id must contain only lowercase alphanumeric characters and hyphens: {value!r}")


def validate_fixture_manifest(ready: ReadySuite) -> FixtureBinding:
    manifest_path = resolve_repository_file(ready.fixture_manifest, "fixture_manifest")
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid fixture manifest {ready.fixture_manifest}: {error.msg}") from error
    if not isinstance(manifest, dict):
        raise ValueError("fixture manifest must be an object")
    if manifest.get("version") != VERSION:
        raise ValueError("fixture manifest must declare version '1'")
    if manifest.get("suite") != ready.suite_id:
        raise ValueError("fixture manifest suite does not match ready suite")
    command = manifest.get("command")
    if not valid_string_argv(command):
        raise ValueError("fixture manifest must declare a nonempty command argv")
    validate_command_argv(command)
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list):
        raise ValueError("fixture manifest must declare fixtures")
    declared: list[tuple[str, str]] = []
    for fixture in fixtures:
        validate_fixture(fixture, declared)
    if tuple(fixture_id for fixture_id, _ in declared) != ready.fixture_ids:
        raise ValueError("fixture manifest IDs do not match the ready suite fixture IDs")
    return FixtureBinding(hashlib.sha256(manifest_bytes).hexdigest(), tuple(command), tuple(declared))


def validate_fixture(fixture: object, declared: list[tuple[str, str]]) -> None:
    if not isinstance(fixture, dict):
        raise ValueError("each fixture manifest entry must be an object")
    fixture_id = fixture.get("id")
    relative_path = fixture.get("path")
    digest = fixture.get("sha256")
    if not isinstance(fixture_id, str) or not fixture_id or any(item[0] == fixture_id for item in declared):
        raise ValueError("fixture manifest IDs must be unique nonempty strings")
    if not isinstance(relative_path, str) or not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
        raise ValueError("each fixture requires a repository-relative path and lowercase SHA-256 digest")
    fixture_path = resolve_repository_file(Path(relative_path), "fixture path")
    actual_digest = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    if actual_digest != digest:
        raise ValueError(f"fixture digest does not match for {fixture_id}")
    declared.append((fixture_id, digest))


def valid_string_argv(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def validate_command_argv(command: list[str]) -> None:
    executable = Path(command[0]).name.lower()
    if executable in {"bash", "sh", "zsh", "fish", "cmd", "powershell", "pwsh"} or executable.endswith((".bat", ".cmd", ".ps1")):
        raise ValueError("fixture manifest command must not use a shell")
    for argument in command:
        placeholders = re.findall(r"\{[^}]*\}", argument)
        if placeholders and (argument != "{commit}" or placeholders != ["{commit}"]):
            raise ValueError("fixture manifest command may use only the {commit} placeholder as a complete argv item")
        if not placeholders and ("{" in argument or "}" in argument):
            raise ValueError("fixture manifest command contains an invalid placeholder")


def resolve_repository_file(value: Path, field: str) -> Path:
    candidate = value if value.is_absolute() else ROOT / value
    resolved = candidate.resolve()
    if not resolved.is_relative_to(ROOT) or not resolved.is_file():
        raise ValueError(f"{field} must name a checked-in repository file")
    return resolved


def evidence_is_current(evidence: object, ready: ReadySuite, commit: str, binding: FixtureBinding, now: datetime | None = None) -> bool:
    if not isinstance(evidence, dict):
        return False
    if evidence.get("version") != VERSION or evidence.get("status") != "pass":
        return False
    if evidence.get("suite") != ready.suite_id or evidence.get("commit") != commit:
        return False
    timestamps = parse_evidence_timestamps(evidence, now or datetime.now(timezone.utc))
    if timestamps is None:
        return False
    evidence_cases = evidence.get("cases")
    if not isinstance(evidence_cases, list):
        return False
    return evidence_cases == [{"id": case_id, "status": "pass"} for case_id in ready.case_ids] and evidence.get("fixtures") == fixture_binding_json(binding)


def fixture_binding_json(binding: FixtureBinding) -> dict[str, str | list[dict[str, str]]]:
    return {
        "manifest_sha256": binding.manifest_sha256,
        "fixtures": [{"id": fixture_id, "sha256": digest} for fixture_id, digest in binding.fixtures],
    }


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def result_path(out: Path, suite: str, commit: str) -> Path:
    require_suite_id(suite)
    if COMMIT.fullmatch(commit) is None:
        raise ValueError("commit must be a SHA or local")
    directory = out if out.is_absolute() else ROOT / out
    return directory / suite / commit / "result.json"


def parse_evidence_timestamps(evidence: dict[str, object], now: datetime) -> tuple[datetime, datetime] | None:
    started = parse_rfc3339(evidence.get("started_at"))
    finished = parse_rfc3339(evidence.get("finished_at"))
    if started is None or finished is None or finished < started:
        return None
    if started > now + MAX_FUTURE_SKEW or finished > now + MAX_FUTURE_SKEW:
        return None
    if now - started > MAX_EVIDENCE_AGE or now - finished > MAX_EVIDENCE_AGE:
        return None
    return started, finished


def parse_rfc3339(value: object) -> datetime | None:
    if not isinstance(value, str) or RFC3339.fullmatch(value) is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
