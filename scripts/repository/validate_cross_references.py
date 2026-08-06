#!/usr/bin/env python3
"""Resolve every cross-reference in the repository and fail when one dangles.

A cross-reference is any token in a tracked file that names something owned
elsewhere in this repository. Eight classes are resolved, each against exactly one
owner:

| Class            | Token                           | Owner                                              |
| ---------------- | ------------------------------- | -------------------------------------------------- |
| `decision`       | `D-\\d{3}`                       | `docs/planning/DECISION_REGISTER.md` rows           |
| `finding`        | `SR-\\d{3}`                      | `conformance/p1140f/semantic-findings-v1.json`      |
| `adr`            | `ADR-\\d{3}`                     | a `docs/decisions/ADR-<n>-*.md` file                |
| `program`        | `P-\\d{4}[A-Z]?`                 | `docs/planning/TASK_CATALOG.md`                     |
| `work-unit`      | `<PREFIX>-\\d{2,3}`              | `### <ID>` headings in `PR_SIZED_WORK_BREAKDOWN.md` |
| `path`           | markdown link / inline-code path | the filesystem                                      |
| `json-ref`       | JSON Schema / OpenAPI `$ref`     | the pointer target                                  |
| `operation`      | an OpenAPI `operationId`         | `packages/schemas/openapi-v1.yaml`                  |

A ninth class, `non-authority`, has no owner by construction: `.context/` is
gitignored working space and `AF-\\d{3}` audit-finding IDs live only there, so a
tracked file that cites either is citing something outside repository authority.
Those are always reported as dangling.

Digit count distinguishes the classes and keeps them mutually exclusive, so no token
is resolved twice: three digits is a work unit (`P-001`), four is a program
(`P-1104`). Two digits is also accepted as a work-unit citation and can never
resolve, because the breakdown numbers every heading with three — that is the
superseded numbering this validator exists to surface rather than tolerate.

This proves reference resolution only. It does not claim that the thing a resolved
reference names is correct, current, or implemented.

Exit codes: 0 when every reference resolves (or under `--report`), 1 when any
reference dangles, 2 when the validator cannot read an owner it needs.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DECISION_REGISTER = ROOT / "docs" / "planning" / "DECISION_REGISTER.md"
SEMANTIC_FINDINGS = ROOT / "conformance" / "p1140f" / "semantic-findings-v1.json"
ADR_DIRECTORY = ROOT / "docs" / "decisions"
TASK_CATALOG = ROOT / "docs" / "planning" / "TASK_CATALOG.md"
WORK_BREAKDOWN = ROOT / "docs" / "implementation" / "PR_SIZED_WORK_BREAKDOWN.md"
OPENAPI_RELATIVE = "packages/schemas/openapi-v1.yaml"
OPENAPI = ROOT / OPENAPI_RELATIVE

# Tracked files under these prefixes are scanned, plus every root-level `*.md`.
SCAN_ROOTS = ("docs/", "packages/", "conformance/", "evals/", "scripts/", "tests/")

# Narrow, enumerated exclusions. Each one names a file whose *purpose* is to hold
# reference syntax rather than references, so its tokens are definitions and not
# citations. This is deliberately a file list and not a directory rule.
EXCLUDED_FILES = frozenset(
    {
        # Holds the reference regexes and the class table above.
        "scripts/repository/validate_cross_references.py",
        # Holds synthetic drift fixtures that must dangle for the tests to mean anything.
        "tests/ci/test_cross_references.py",
    }
)

# Extensions worth reading as text. Everything else under a scan root (fonts,
# raster fixtures, archives) is skipped because it cannot carry a prose reference.
TEXT_SUFFIXES = frozenset(
    {
        ".md",
        ".json",
        ".yaml",
        ".yml",
        ".py",
        ".sql",
        ".proto",
        ".cddl",
        ".toml",
        ".rs",
        ".go",
        ".ts",
        ".tsx",
        ".txt",
        ".sh",
        ".cfg",
        ".ini",
    }
)

# ---------------------------------------------------------------------------
# Reference tokens
# ---------------------------------------------------------------------------

# Every ID regex is anchored so a token embedded in a longer identifier, a path
# segment, or a date is not a citation: `ADR-003-PLATFORM…` yields `ADR-003` only,
# and `P-1140F-1` yields the program `P-1140F` and no work unit.
_LEFT = r"(?<![A-Za-z0-9-])"

DECISION_RE = re.compile(rf"{_LEFT}D-(\d{{3}})(?!\d)")
FINDING_RE = re.compile(rf"{_LEFT}(SR-\d{{3}})(?!\d)")
ADR_RE = re.compile(rf"{_LEFT}ADR-(\d{{3}})(?!\d)")
PROGRAM_RE = re.compile(rf"{_LEFT}(P-\d{{4}}[A-Z]?)(?!\d)")

# Epic prefixes used by `PR_SIZED_WORK_BREAKDOWN.md`, longest first so `PF-001` is
# never read as `F-001`. `I`, `U` and `PL` are recognised but were never defined:
# they appear only in the legacy two-digit citations below, so admitting them here is
# what makes those citations visible rather than silently unparsed.
WORK_UNIT_PREFIXES = (
    "PF",
    "OS",
    "PL",
    "F",
    "P",
    "A",
    "N",
    "S",
    "O",
    "V",
    "R",
    "G",
    "M",
    "L",
    "W",
    "X",
    "I",
    "U",
)
# Two digits as well as three. The breakdown numbers every unit with three digits, so
# a two-digit citation cannot resolve by construction — which is precisely the defect
# class: `ISSUE_GENERATION.md` and the decision-traceability matrices carry a legacy
# two-digit numbering that `generate_issue_plan.py`'s own `\d{3}` key pattern rejects.
WORK_UNIT_RE = re.compile(
    rf"{_LEFT}((?:{'|'.join(WORK_UNIT_PREFIXES)})-\d{{2,3}})(?!\d)"
)

AUDIT_FINDING_RE = re.compile(rf"{_LEFT}(AF-\d{{3}})(?!\d)")
CONTEXT_PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])\.context/[A-Za-z0-9_./-]*")
AUDIT_FINDING_DETAIL = (
    "audit finding IDs live in gitignored .context/, not in repository authority"
)
CONTEXT_PATH_DETAIL = ".context/ is gitignored working space, not repository authority"

# A `$ref` as it is written in either serialisation this repository uses: JSON
# (`"$ref": "…"`) and YAML (`$ref: '…'` or `$ref: "…"`). Used only to locate the
# citation's line and to count citations; resolution works on the parsed document.
REF_LINE_RE = re.compile(r'"?\$ref"?\s*:\s*["\']([^"\']+)["\']')

MARKDOWN_LINK_RE = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")

# A line that *defines* an identifier pattern rather than citing an identifier:
# a hyphen followed by a quantified digit class. `D-\d{3}`, `-[0-9]{3}`, `-\\d{3}`.
# It cannot match a literal citation, because a literal citation has digits there.
PATTERN_DEFINITION_RE = re.compile(r"-\\{1,2}d\{|-\[0-9\]\{|-\[0-9\]\+|\[A-Z0-9\]\*-")

# Paths cited in inline code. A token counts only when it has a directory
# separator and a file extension, which excludes media types (`application/json`),
# bare filenames (`Cargo.toml`), and versions (`1.0.0`).
_PATH_TOKEN_RE = re.compile(r"^[A-Za-z0-9_.@-]+(?:/[A-Za-z0-9_.@\[\]-]+)+$")
_HAS_EXTENSION_RE = re.compile(r"\.[A-Za-z0-9]{1,6}$")

# Path-shaped strings that name something outside this repository's filesystem.
NON_REPOSITORY_PATH_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "git@",
    "/",  # absolute host paths such as /etc/… and /usr/…
    "~",
    "$",
    "@",  # npm scopes: @scope/package
    ".context/",  # gitignored working space; the non-authority class owns it
)

# A path citation must resolve unless the citing line marks it as not-current. Two
# modalities are recognised, using the vocabulary the repository already writes:
#
# * planned — the artifact does not exist yet and a named work unit will create it:
#   `PR_SIZED_WORK_BREAKDOWN.md` writes `… .json` (new), and
#   `SCHEMA_AND_INTERFACE_INVENTORY.md` writes `proposed …` with a `planned-missing`
#   status cell;
# * retired — the artifact existed and a recorded restructuring removed it, so the
#   citation is a historical fact rather than a live pointer.
#
# A `planned` marker binds to the token it touches — `x.json` (new) marks `x.json`
# and nothing else on the line — so one planned deliverable in a `Files:` list cannot
# excuse a stale sibling beside it. A `retired` marker is a statement about the whole
# sentence and so binds to the line. An unmarked path that does not resolve is a
# defect, which is the whole point of the class.
PLANNED_TRAILING_RE = re.compile(r"^\s*`?\s*\(new\)", re.IGNORECASE)
PLANNED_LEADING_RE = re.compile(r"\bproposed\s+`?\s*$", re.IGNORECASE)
PLANNED_ROW_MARKER_RE = re.compile(r"\bplanned-missing\b", re.IGNORECASE)
RETIRED_PATH_MARKER_RE = re.compile(
    r"\brenamed\b|\bmerged into\b|\bfolded into\b|\barchived to\b|\babsorbed\b"
    r"|\bretired\b|\bsuperseded\b|\bdeprecated\b|\bthe former\b|\bformerly\b",
    re.IGNORECASE,
)

# `-999` is the reserved synthetic sentinel in every identifier class. Drift-injection
# tests need an ID that provably resolves nowhere; reserving one number keeps that
# possible without excluding whole test files from the scan.
SYNTHETIC_SENTINEL = "999"

# Identifiers cited as OpenAPI operations. A citation is only recognised when the
# artifact says so — an `api_operations` list, or a markdown line that names the
# word `operationId` — so ordinary camelCase prose is never misread as one.
OPERATION_LIST_KEYS = frozenset({"api_operations", "operation_ids", "operationIds"})
OPERATION_LABEL_RE = re.compile(r"operation\s*ids?\b|operationId", re.IGNORECASE)
_OPERATION_TOKEN_RE = re.compile(r"^[a-z][A-Za-z0-9]*$")


class Failure(RuntimeError):
    """An owner the validator needs could not be read."""


@dataclass(frozen=True)
class Dangle:
    kind: str
    token: str
    path: str
    line: int
    detail: str = ""

    def render(self) -> str:
        location = f"{self.path}:{self.line}"
        suffix = f" — {self.detail}" if self.detail else ""
        return f"{location}: {self.token}{suffix}"


@dataclass
class Report:
    dangles: list[Dangle]
    scanned_files: int
    counts: dict[str, int]


# ---------------------------------------------------------------------------
# Owners
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise Failure(f"unreadable required owner {path}: {error}") from error


def load_decisions() -> set[str]:
    """Accepted decision IDs are the leading cell of a DECISION_REGISTER row."""
    rows = re.findall(r"^\|\s*`?(D-\d{3})`?\s*\|", read_text(DECISION_REGISTER), re.M)
    if not rows:
        raise Failure(f"{DECISION_REGISTER.name} declares no decision rows")
    return set(rows)


def load_findings() -> set[str]:
    try:
        record = json.loads(read_text(SEMANTIC_FINDINGS))
    except json.JSONDecodeError as error:
        raise Failure(f"unreadable {SEMANTIC_FINDINGS.name}: {error}") from error
    ids = {row["finding_id"] for row in record.get("findings", [])}
    if not ids:
        raise Failure(f"{SEMANTIC_FINDINGS.name} declares no findings")
    return ids


def load_adrs() -> set[str]:
    if not ADR_DIRECTORY.is_dir():
        raise Failure(f"missing ADR directory {ADR_DIRECTORY}")
    ids = set()
    for path in ADR_DIRECTORY.glob("ADR-*.md"):
        match = re.match(r"(ADR-\d{3})-", path.name)
        if match:
            ids.add(match.group(1))
    if not ids:
        raise Failure(f"{ADR_DIRECTORY} contains no ADR files")
    return ids


def load_programs() -> set[str]:
    ids = set(PROGRAM_RE.findall(read_text(TASK_CATALOG)))
    if not ids:
        raise Failure(f"{TASK_CATALOG.name} declares no programs")
    return ids


def load_work_units() -> set[str]:
    ids = set(re.findall(r"^###\s+([A-Z]+-\d{3})\b", read_text(WORK_BREAKDOWN), re.M))
    if not ids:
        raise Failure(f"{WORK_BREAKDOWN.name} declares no work-unit headings")
    return ids


def parse_structured(text: str):
    """Parse a schema document that may be written as JSON or as YAML.

    JSON is attempted first because it is unambiguous and because every
    `*.schema.json` in the repository is JSON. YAML is the fallback, and it is what
    `packages/schemas/openapi-v1.yaml` has held since D-140. Returns `None` when the
    text is neither, which the callers report as an unreadable document.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        import yaml
    except ImportError:  # pragma: no cover - requirements pin PyYAML
        return None
    try:
        return yaml.safe_load(text)
    except Exception:
        return None


def load_openapi() -> dict:
    document = parse_structured(read_text(OPENAPI))
    if not isinstance(document, dict):
        raise Failure(f"{OPENAPI.name} is not a mapping")
    return document


def openapi_operation_ids(document: dict) -> set[str]:
    ids = set()
    for operations in document.get("paths", {}).values():
        if not isinstance(operations, dict):
            continue
        for operation in operations.values():
            if isinstance(operation, dict) and "operationId" in operation:
                ids.add(operation["operationId"])
    if not ids:
        raise Failure(f"{OPENAPI.name} declares no operationId")
    return ids


# ---------------------------------------------------------------------------
# File selection
# ---------------------------------------------------------------------------


def tracked_files() -> list[str]:
    try:
        listing = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise Failure(f"cannot list tracked files: {error}") from error
    return [entry for entry in listing.split("\0") if entry]


def in_scan_scope(relative: str) -> bool:
    if relative in EXCLUDED_FILES:
        return False
    if "/" not in relative:
        return relative.endswith(".md")
    if not relative.startswith(SCAN_ROOTS):
        return False
    return Path(relative).suffix in TEXT_SUFFIXES


# ---------------------------------------------------------------------------
# Line masking
# ---------------------------------------------------------------------------


def scannable_lines(text: str, is_markdown: bool) -> list[tuple[int, str]]:
    """Yield ``(line_number, line)`` for every line that may hold a citation.

    Two documented suppressions apply:

    * any line that defines an identifier pattern (``-\\d{3}`` and friends), because
      the token there is syntax rather than a citation;
    * any fenced markdown block that contains such a line, because the block as a
      whole is a pattern definition — its example IDs are illustrative.
    """
    lines = text.splitlines()
    suppressed: set[int] = set()

    if is_markdown:
        fence_start: int | None = None
        block: list[int] = []
        for index, line in enumerate(lines):
            if FENCE_RE.match(line):
                if fence_start is None:
                    fence_start, block = index, []
                else:
                    if any(PATTERN_DEFINITION_RE.search(lines[i]) for i in block):
                        suppressed.update(block)
                    fence_start = None
            elif fence_start is not None:
                block.append(index)

    return [
        (index + 1, line)
        for index, line in enumerate(lines)
        if index not in suppressed and not PATTERN_DEFINITION_RE.search(line)
    ]


# ---------------------------------------------------------------------------
# Path references
# ---------------------------------------------------------------------------


def normalise_path(raw: str) -> str | None:
    """Strip decoration from a cited path, or return None when it is not one."""
    target = raw.strip().strip("<>").split("#", 1)[0]
    target = re.sub(r":\d+(?:-\d+)?$", "", target)  # `file.py:42` line citations
    target = target.rstrip(".,;:")
    if not target or "://" in target:
        return None
    if target.startswith(NON_REPOSITORY_PATH_PREFIXES):
        return None
    return target


def path_resolves(target: str, relative: str) -> bool:
    """Resolve a cited path against the repository root or any ancestor of the citer.

    `docs/project/DOCUMENTATION.md` is the index of `docs/`, so it writes
    `security/ANTI_CHEAT_ATTACK_CATALOG.md` for `docs/security/…`. Trying every
    directory between the citing file and the root reads those the way a human does
    and cannot make an unrelated path resolve, because the search stays inside the
    citing file's own ancestry.
    """
    bases = [ROOT]
    directory = (ROOT / relative).parent
    while True:
        bases.append(directory)
        if directory == ROOT:
            break
        directory = directory.parent
    return any((base / target).exists() for base in bases)


def path_candidates(line: str, is_markdown: bool) -> list[str]:
    """Return every repository-relative path this line requires to resolve.

    Two syntaxes count as a citation: a markdown link target, and an inline-code
    token that has both a directory separator and a file extension. A citation the
    line marks as `planned` or `retired` is dropped here, because it is a statement
    about an artifact that does not exist rather than a pointer to one that should.
    """
    line_is_retired = bool(RETIRED_PATH_MARKER_RE.search(line))
    line_is_planned_row = bool(PLANNED_ROW_MARKER_RE.search(line))
    if line_is_retired or line_is_planned_row:
        return []

    raw: list[str] = []
    for match in MARKDOWN_LINK_RE.finditer(line) if is_markdown else ():
        raw.append((match.group(1), match.start(1), match.end(1)))
    for match in INLINE_CODE_RE.finditer(line):
        token = match.group(1).strip()
        if (
            "/" in token
            and _PATH_TOKEN_RE.match(token)
            and _HAS_EXTENSION_RE.search(token.split("#", 1)[0])
        ):
            raw.append((token, match.start(1), match.end(1)))

    targets: list[str] = []
    for token, start, end in raw:
        if PLANNED_TRAILING_RE.match(line[end:]) or PLANNED_LEADING_RE.search(
            line[:start]
        ):
            continue
        target = normalise_path(token)
        if target:
            targets.append(target)
    return targets


def collect_paths(
    relative: str, lines: list[tuple[int, str]], is_markdown: bool
) -> list[Dangle]:
    dangles: list[Dangle] = []
    for number, line in lines:
        for target in path_candidates(line, is_markdown):
            if not path_resolves(target, relative):
                dangles.append(Dangle("path", target, relative, number))
    return dangles


# ---------------------------------------------------------------------------
# JSON `$ref` references
# ---------------------------------------------------------------------------


def walk_refs(node, pointer: str = ""):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                yield pointer, value
            else:
                yield from walk_refs(value, f"{pointer}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk_refs(value, f"{pointer}/{index}")


def resolve_pointer(document, pointer: str) -> bool:
    node = document
    for token in pointer.lstrip("#").strip("/").split("/"):
        if token == "":
            continue
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if token not in node:
                return False
            node = node[token]
        elif isinstance(node, list):
            if not token.isdigit() or int(token) >= len(node):
                return False
            node = node[int(token)]
        else:
            return False
    return True


def collect_json_refs(relative: str, source: Path, text: str) -> list[Dangle]:
    """Resolve every `$ref` in a schema document, internal pointer or external file.

    The document may be JSON or YAML. `packages/schemas/openapi-v1.yaml` is YAML under
    D-140 while every `*.schema.json` beside it is JSON, and a `$ref` means the same
    thing in both, so the parser is chosen by content rather than by extension.
    """
    document = parse_structured(text)
    if not isinstance(document, dict):
        return [
            Dangle(
                "json-ref",
                relative,
                relative,
                1,
                "document is not readable JSON or YAML",
            )
        ]
    dangles: list[Dangle] = []
    line_of = {
        reference: index + 1
        for index, line in enumerate(text.splitlines())
        for reference in REF_LINE_RE.findall(line)
    }
    for _pointer, reference in walk_refs(document):
        line = line_of.get(reference, 1)
        if reference.startswith("#"):
            if not resolve_pointer(document, reference):
                dangles.append(
                    Dangle("json-ref", reference, relative, line, "unresolved pointer")
                )
            continue
        file_part, _, fragment = reference.partition("#")
        target = source.parent / file_part
        if not target.exists():
            target = ROOT / file_part
        if not target.exists():
            dangles.append(
                Dangle("json-ref", reference, relative, line, "missing target file")
            )
            continue
        if fragment:
            try:
                external = parse_structured(target.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                external = None
            if external is None:
                dangles.append(
                    Dangle("json-ref", reference, relative, line, "unreadable target")
                )
                continue
            if not resolve_pointer(external, f"#{fragment}"):
                dangles.append(
                    Dangle(
                        "json-ref",
                        reference,
                        relative,
                        line,
                        "unresolved external pointer",
                    )
                )
    return dangles


# ---------------------------------------------------------------------------
# OpenAPI operation references
# ---------------------------------------------------------------------------


def collect_operation_citations(
    relative: str, text: str, lines: list[tuple[int, str]], is_markdown: bool
) -> list[tuple[str, int]]:
    """Return `(operationId, line)` for every explicit citation in one file."""
    citations: list[tuple[str, int]] = []

    if relative.endswith(".json"):
        try:
            document = json.loads(text)
        except json.JSONDecodeError:
            document = None
        if document is not None:
            named: list[str] = []

            def walk(node):
                if isinstance(node, dict):
                    for key, value in node.items():
                        if key in OPERATION_LIST_KEYS and isinstance(value, list):
                            named.extend(
                                item for item in value if isinstance(item, str)
                            )
                        else:
                            walk(value)
                elif isinstance(node, list):
                    for item in node:
                        walk(item)

            walk(document)
            index = {
                value: number
                for number, line in enumerate(text.splitlines(), 1)
                for value in re.findall(r'"([A-Za-z0-9_]+)"', line)
            }
            citations.extend((name, index.get(name, 1)) for name in named)

    if is_markdown:
        for number, line in lines:
            if not OPERATION_LABEL_RE.search(line):
                continue
            for code in INLINE_CODE_RE.findall(line):
                token = code.strip()
                if token in {"operationId", "operation_id"}:
                    continue
                if _OPERATION_TOKEN_RE.match(token):
                    citations.append((token, number))

    return citations


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------


def scan(files: list[str] | None = None) -> Report:
    decisions = load_decisions()
    findings = load_findings()
    adrs = load_adrs()
    programs = load_programs()
    work_units = load_work_units()
    operations = openapi_operation_ids(load_openapi())

    # One row per identifier class: the token regex, how a match becomes an ID, the
    # owner's set of declared IDs, and why a miss is a defect.
    id_classes = (
        ("decision", DECISION_RE, "D-{}".format, decisions, "no DECISION_REGISTER row"),
        (
            "finding",
            FINDING_RE,
            str,
            findings,
            "not in conformance/p1140f/semantic-findings-v1.json",
        ),
        (
            "adr",
            ADR_RE,
            "ADR-{}".format,
            adrs,
            "no docs/decisions/ADR-<n>-*.md file",
        ),
        ("program", PROGRAM_RE, str, programs, "not in docs/planning/TASK_CATALOG.md"),
        (
            "work-unit",
            WORK_UNIT_RE,
            str,
            work_units,
            "no ### heading in docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
        ),
    )

    if files is None:
        files = [name for name in tracked_files() if in_scan_scope(name)]

    dangles: list[Dangle] = []
    counts: dict[str, int] = defaultdict(int)
    scanned = 0

    for relative in sorted(files):
        source = ROOT / relative
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        is_markdown = relative.endswith(".md")
        lines = scannable_lines(text, is_markdown)

        for number, line in lines:
            for kind, pattern, render, known, detail in id_classes:
                for match in pattern.findall(line):
                    token = render(match)
                    counts[kind] += 1
                    if token.endswith(f"-{SYNTHETIC_SENTINEL}"):
                        continue
                    if token not in known:
                        dangles.append(Dangle(kind, token, relative, number, detail))
            for pattern, detail in (
                (AUDIT_FINDING_RE, AUDIT_FINDING_DETAIL),
                (CONTEXT_PATH_RE, CONTEXT_PATH_DETAIL),
            ):
                for token in pattern.findall(line):
                    counts["non-authority"] += 1
                    dangles.append(
                        Dangle("non-authority", token, relative, number, detail)
                    )

        counts["path"] += count_path_candidates(lines, is_markdown)
        dangles.extend(collect_paths(relative, lines, is_markdown))

        if relative.endswith(".schema.json") or relative == OPENAPI_RELATIVE:
            refs = collect_json_refs(relative, source, text)
            counts["json-ref"] += count_json_refs(text)
            dangles.extend(refs)

        if relative != OPENAPI_RELATIVE:
            for token, number in collect_operation_citations(
                relative, text, lines, is_markdown
            ):
                counts["operation"] += 1
                if token not in operations:
                    dangles.append(
                        Dangle(
                            "operation",
                            token,
                            relative,
                            number,
                            "no operationId in openapi-v1.yaml",
                        )
                    )

    superseded = report_superseded_citations()
    dangles.extend(superseded)
    counts["superseded"] = counts.get("superseded", 0) + len(superseded)

    return Report(dangles=dangles, scanned_files=scanned, counts=dict(counts))


def count_path_candidates(lines: list[tuple[int, str]], is_markdown: bool) -> int:
    return sum(len(path_candidates(line, is_markdown)) for _number, line in lines)


def count_json_refs(text: str) -> int:
    return len(REF_LINE_RE.findall(text))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

CLASS_ORDER = (
    "decision",
    "finding",
    "adr",
    "program",
    "work-unit",
    "path",
    "json-ref",
    "operation",
    "non-authority",
    "superseded",
)


def render_report(report: Report, stream) -> None:
    grouped: dict[str, list[Dangle]] = defaultdict(list)
    for dangle in report.dangles:
        grouped[dangle.kind].append(dangle)
    for kind in CLASS_ORDER:
        rows = grouped.get(kind, [])
        scanned = report.counts.get(kind, 0)
        unique = len({row.token for row in rows})
        print(
            f"\n## {kind}: {len(rows)} dangling reference(s) "
            f"across {unique} unique token(s); {scanned} scanned",
            file=stream,
        )
        for row in sorted(rows, key=lambda row: (row.path, row.line, row.token)):
            print(f"  {row.render()}", file=stream)


# Scoped to documents that state what is true now, rather than to everything.
#
# A record of the past cites superseded decisions because that is its job: the
# register explains what changed, `docs/history/` is archival by definition,
# `decision-traceability/` maps decisions to the units that implemented them,
# and `conformance/p1140e/` is a completed gate's evidence, frozen at the head
# it was taken against. Flagging those would produce an exemption list longer
# than the rule, which is the failure mode this check exists to prevent.
#
# What is checked is the live normative surface: the documents an engineer
# reads to learn what the product does today.
SUPERSEDED_CITATION_ROOTS = (
    "docs/decisions/",
    "docs/architecture/",
    "docs/product/",
    "docs/privacy/",
    "docs/security/",
    "docs/operations/",
    "docs/integrations/",
    "docs/engineering/",
    "docs/verification/",
    "packages/",
)

SUPERSEDED_CITATION_EXEMPT = frozenset(
    {
        # Amended in place, so it explains the position it replaced. Removing the
        # superseded ids would remove the explanation.
        "docs/decisions/ADR-017-HOSTING_REGION_AND_RESIDENCY.md",
    }
)


def superseded_decisions() -> dict[str, str]:
    """Decision ids the register marks superseded, with their replacement note."""
    superseded: dict[str, str] = {}
    for line in DECISION_REGISTER.read_text(encoding="utf-8").split("\n"):
        if not line.startswith("| D-"):
            continue
        cells = line.split("|")
        if len(cells) != 6:
            continue
        identifier, _, status, condition = (cell.strip() for cell in cells[1:5])
        if status == "superseded":
            superseded[identifier] = condition
    return superseded


def report_superseded_citations() -> list[Dangle]:
    """A superseded decision cited as though it still holds is stale authority.

    It is not a dangling reference: the row exists and resolves. It is worse,
    because it resolves to something that was true and is not. Six documents
    were reasoning from a spending ceiling that had been replaced, and one of
    them concluded a recovery objective was unaffordable when it had become
    merely unbuilt.

    A citation that explicitly says the decision is superseded is fine, and is
    how a document records history. The rule is about citations that read as
    current.
    """
    superseded = superseded_decisions()
    if not superseded:
        return []
    found: list[Dangle] = []
    for relative in tracked_files():
        if not relative.startswith(SUPERSEDED_CITATION_ROOTS):
            continue
        if relative in SUPERSEDED_CITATION_EXEMPT:
            continue
        text = (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.split("\n"), start=1):
            lowered = line.lower()
            # A citation that marks the decision as past is how a document
            # records history rather than asserting a stale fact. The rule is
            # about citations that read as current.
            if any(
                marker in lowered
                for marker in (
                    "supersed",
                    "no longer",
                    "used to",
                    "is resolved",
                    "resolved by",
                    "replaced by",
                    "previously",
                    "was fixed by",
                )
            ):
                continue
            for identifier in superseded:
                if identifier in line:
                    found.append(
                        Dangle(
                            kind="superseded",
                            token=identifier,
                            path=relative,
                            line=number,
                            detail=f"cited as current; {superseded[identifier]}",
                        )
                    )
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--report",
        action="store_true",
        help="list every dangling reference grouped by class and exit 0",
    )
    arguments = parser.parse_args(argv)

    try:
        report = scan()
    except Failure as failure:
        print(f"cross-reference validation: ERROR\n- {failure}", file=sys.stderr)
        return 2

    total_scanned = sum(report.counts.values())
    summary = f"{report.scanned_files} files, {total_scanned} references, " + ", ".join(
        f"{kind}={report.counts.get(kind, 0)}" for kind in CLASS_ORDER
    )

    if arguments.report:
        print(f"cross-reference report: {len(report.dangles)} dangling ({summary})")
        render_report(report, sys.stdout)
        return 0

    if report.dangles:
        print("cross-reference validation: FAIL", file=sys.stderr)
        for dangle in sorted(
            report.dangles, key=lambda row: (row.kind, row.path, row.line, row.token)
        ):
            print(f"- [{dangle.kind}] {dangle.render()}", file=sys.stderr)
        print(
            f"cross-reference validation: FAIL ({len(report.dangles)} dangling; {summary})",
            file=sys.stderr,
        )
        return 1

    print(f"cross-reference validation: PASS ({summary})")
    print(
        "claim_scope=reference-resolution-only; a resolved reference is not a correct one"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
