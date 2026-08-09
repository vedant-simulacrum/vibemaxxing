#!/usr/bin/env python3
"""Generate a deterministic offline issue plan from stable work-unit headings.

Every record carries the unit's own `Files:`, `Acceptance:`, `Depends:`, `Est:` and
`Status:` lines. Without them the plan was a list of headings: 260 titles and a
component label, from which nobody could tell what a unit touches, what would make it
done, what it waits on, or whether it had already been done.

Two things this generator refuses to assert.

**A gate state it was not told.** `phase_gate` and the `blocked` label used to be
literals. Every implementation record said `P-1104-explicit-implementation-approval`
and `blocked`, which was true when it was written and false from the moment the owner
opened P-1104 on 2026-08-05 — and no input existed that could have noticed. Which gate
a unit sits behind is now derived from its epic prefix, and that gate's *state* is read
from `conformance/p1140f/gate-authorization-v1.json`, which is the sole authority for
it. A state this file does not recognise blocks the unit rather than releasing it,
because a generator that guesses `open` on a state it has never seen mislabels the
whole plan in the one direction that matters.

**A status it read alone.** `validate_work_unit_status.py` reads the same document with
a different heading pattern and different block boundaries. When the two readers
disagree about which units exist, or about any unit's status, one of them is wrong and
this generator exits non-zero rather than writing a plan built on the difference. That
is what catches a heading whose title was dropped, or one whose prefix is longer than
the validator's pattern admits: one tool counts it and the other does not, and neither
alone can see that.

Field *enforcement* is not duplicated here. `validate_work_unit_status.py` owns it under
D-201. This generator refuses to emit a record it cannot fill, which is a different
thing: an issue carrying an empty acceptance criterion is a lie about the unit, not a
document-quality finding.

Exit codes: 0 when a plan is written, 1 on any defect.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md"
GATE_RECORD = ROOT / "conformance/p1140f/gate-authorization-v1.json"
STATUS_VALIDATOR = Path(__file__).resolve().parent / "validate_work_unit_status.py"
DEFAULT_OUTPUT = ROOT / "artifacts/repository/issue-plan.json"

EPIC = re.compile(r"^##\s+Epic\s+([A-Z][A-Z0-9]*)\s+[—-]\s+(.+?)\s*$")
UNIT = re.compile(r"^###\s+([A-Z][A-Z0-9]*-\d{3})\s+[—-]?\s*(.+?)\s*$")
HEADING = re.compile(r"^#{2,3}\s")
FIELD = re.compile(r"^(Files|Acceptance|Depends|Est|Status):\s*(.*)$")
INLINE_CODE = re.compile(r"`([^`\n]+)`")
PLANNING_HEADING = "## Current planning program"

PLANNING_PREFIX = "PF"
PLANNING_GATE = "P-1140F"
IMPLEMENTATION_GATE = "P-1104"
PLANNING_EPIC_TITLE = "P-1140F planning repairs"

# Gate states under which the work behind the gate is not blocked. Membership is
# stated rather than inferred, and an unrecognised state is blocked: this set decides
# a label, and the failure that matters is releasing a unit the owner has not.
UNBLOCKING_GATE_STATES = frozenset(
    {"authorized-open", "in-progress-planning", "complete-planning"}
)

REQUIRED_FIELDS = ("Files", "Acceptance", "Depends", "Est", "Status")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_status_validator():
    """Import `validate_work_unit_status.py` as the second reader of the breakdown."""
    specification = importlib.util.spec_from_file_location(
        "validate_work_unit_status", STATUS_VALIDATOR
    )
    if specification is None or specification.loader is None:
        raise SystemExit(f"could not load {STATUS_VALIDATOR}")
    module = importlib.util.module_from_spec(specification)
    # Registering before exec is required: Python resolves the module's own
    # dataclass annotations against sys.modules while executing it.
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def load_gate_states(path: Path) -> dict[str, str]:
    """Read every gate's recorded state from the authorization record."""
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise SystemExit(f"unreadable gate record {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise SystemExit(f"invalid JSON gate record {path}: {error.msg}") from error

    gates = record.get("gates")
    if not isinstance(gates, list) or not gates:
        raise SystemExit(f"gate record {path} declares no gates")
    states: dict[str, str] = {}
    for entry in gates:
        gate_id, state = entry.get("gate"), entry.get("state")
        if not gate_id or not state:
            raise SystemExit(f"gate record {path} holds a gate with no id or no state")
        states[gate_id] = state
    for required in (PLANNING_GATE, IMPLEMENTATION_GATE):
        if required not in states:
            raise SystemExit(
                f"gate record {path} names no {required} gate, so nothing can say "
                "whether the units behind it are blocked"
            )
    return states


def gate_for_prefix(prefix: str) -> str:
    """The gate a unit sits behind, derived from its epic prefix, not listed."""
    return PLANNING_GATE if prefix == PLANNING_PREFIX else IMPLEMENTATION_GATE


def split_depends(value: str) -> list[str]:
    raw = value.strip()
    if raw in ("", "none"):
        return []
    return [token.strip().strip("`") for token in raw.split(",") if token.strip()]


def parse_units(text: str) -> list[dict[str, object]]:
    """Read every stable work-unit heading and the field block beneath it."""
    epic_id: str | None = None
    epic_title: str | None = None
    units: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        epic_match = EPIC.match(line)
        if epic_match:
            epic_id = epic_match.group(1)
            epic_title = epic_match.group(2).strip()
            current = None
            continue
        if line.strip() == PLANNING_HEADING:
            epic_id = PLANNING_PREFIX
            epic_title = PLANNING_EPIC_TITLE
            current = None
            continue

        unit_match = UNIT.match(line)
        if unit_match:
            if epic_id is None or epic_title is None:
                raise SystemExit(
                    f"work unit appears before an epic at line {line_number}"
                )
            key, title = unit_match.groups()
            current = {
                "key": key,
                "title": title.rstrip("."),
                "epic_id": epic_id,
                "epic_title": epic_title,
                "source_line": line_number,
                "fields": {},
            }
            units.append(current)
            continue

        # Any other heading of either level ends the block. A field line under
        # `### Required unit fields` belongs to no unit.
        if HEADING.match(line):
            current = None
            continue
        if current is None:
            continue

        field_match = FIELD.match(line)
        if field_match:
            name, value = field_match.group(1), field_match.group(2).strip()
            fields = current["fields"]
            assert isinstance(fields, dict)
            # First wins, exactly as the status validator reads it, so a duplicated
            # field cannot make the two readers disagree about anything but itself.
            fields.setdefault(name, value)

    return units


def check_keys(units: list[dict[str, object]]) -> None:
    seen: set[str] = set()
    for unit in units:
        key = str(unit["key"])
        if key in seen:
            raise SystemExit(f"duplicate work-unit key: {key}")
        seen.add(key)
        prefix = key.rsplit("-", 1)[0]
        if prefix != unit["epic_id"]:
            raise SystemExit(
                f"work-unit prefix {prefix} does not match current epic "
                f"{unit['epic_id']} at line {unit['source_line']}"
            )


def check_status_agreement(
    units: list[dict[str, object]], recorded: dict[str, str]
) -> None:
    """Fail when the second reader of the breakdown disagrees about any unit."""
    generated = {
        str(unit["key"]): str(dict(unit["fields"]).get("Status", "")).split(" ")[0]
        for unit in units
    }
    differences: list[str] = []
    for key in sorted(set(generated) | set(recorded)):
        mine, theirs = generated.get(key), recorded.get(key)
        if mine is None:
            differences.append(
                f"{key}: validate_work_unit_status.py reads status {theirs!r}; "
                "the issue plan has no record for it"
            )
        elif theirs is None:
            differences.append(
                f"{key}: the issue plan reads status {mine!r}; "
                "validate_work_unit_status.py has no unit for it"
            )
        elif mine != theirs:
            differences.append(
                f"{key}: the issue plan reads status {mine!r}; "
                f"validate_work_unit_status.py reads {theirs!r}"
            )
    if differences:
        detail = "\n".join(f"- {line}" for line in differences)
        raise SystemExit(
            "issue plan and work-unit status validator disagree about "
            f"{len(differences)} unit(s):\n{detail}"
        )


def check_required_fields(units: list[dict[str, object]]) -> None:
    for unit in units:
        fields = dict(unit["fields"])
        for name in REQUIRED_FIELDS:
            if not fields.get(name):
                raise SystemExit(
                    f"{unit['key']} (line {unit['source_line']}) is missing `{name}:`, "
                    "so no issue record can carry it"
                )


def check_contiguity(units: list[dict[str, object]]) -> None:
    numbers_by_prefix: dict[str, list[int]] = defaultdict(list)
    for unit in units:
        prefix, number = str(unit["key"]).rsplit("-", 1)
        numbers_by_prefix[prefix].append(int(number))
    for prefix, numbers in numbers_by_prefix.items():
        expected = list(range(1, max(numbers) + 1))
        if numbers != expected:
            raise SystemExit(
                f"work units for {prefix} must be contiguous and source ordered; found {numbers}"
            )


def build_records(
    units: list[dict[str, object]],
    gate_states: dict[str, str],
    planned_paths,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for unit in units:
        fields = dict(unit["fields"])
        key = str(unit["key"])
        prefix = key.rsplit("-", 1)[0]
        gate = gate_for_prefix(prefix)
        state = gate_states[gate]
        blocked = state not in UNBLOCKING_GATE_STATES
        component = slug(str(unit["epic_title"]))
        track = "planning-repair" if gate == PLANNING_GATE else "implementation"
        labels = [track, component] + (["blocked"] if blocked else [])
        status = fields["Status"].split(" ")[0]

        record: dict[str, object] = {
            "key": key,
            "title": unit["title"],
            "epic_id": unit["epic_id"],
            "component": component,
            "source_line": unit["source_line"],
            "phase_gate": gate,
            "phase_gate_state": state,
            "blocked": blocked,
            "labels": labels,
            "files": [token.strip() for token in INLINE_CODE.findall(fields["Files"])],
            "new_files": planned_paths(fields["Files"]),
            "acceptance": fields["Acceptance"],
            "depends": split_depends(fields["Depends"]),
            "est": fields["Est"],
            "status": status,
            "authority": "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
            "artifact_maturity": "planning",
        }
        if status == "superseded-by":
            record["superseded_by"] = fields["Status"][len(status) :].strip("() `")
        records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    source_text = source_bytes.decode("utf-8")

    validator = load_status_validator()
    recorded = {
        unit.unit_id: unit.status_word for unit in validator.parse_units(source_text)
    }
    gate_states = load_gate_states(GATE_RECORD)

    units = parse_units(source_text)
    if not units:
        raise SystemExit("no stable work-unit headings found")

    check_keys(units)
    check_status_agreement(units, recorded)
    check_required_fields(units)
    check_contiguity(units)

    records = build_records(units, gate_states, validator.planned_paths)

    output = args.output
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_version": 3,
        "source": "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "gate_record": "conformance/p1140f/gate-authorization-v1.json",
        "gate_states": {
            PLANNING_GATE: gate_states[PLANNING_GATE],
            IMPLEMENTATION_GATE: gate_states[IMPLEMENTATION_GATE],
        },
        "issue_count": len(records),
        "issues": records,
    }
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    try:
        display_path = output.relative_to(ROOT)
    except ValueError:
        display_path = output
    blocked = sum(1 for record in records if record["blocked"])
    print(f"generated {len(records)} stable work-unit records at {display_path}")
    print(
        f"phase gates read from the authorization record: "
        f"{PLANNING_GATE}={gate_states[PLANNING_GATE]}, "
        f"{IMPLEMENTATION_GATE}={gate_states[IMPLEMENTATION_GATE]}; "
        f"{blocked} record(s) labelled blocked"
    )
    print(
        "claim_scope=plan-metadata-only; a record restates the unit block it was read "
        "from and is not evidence that the unit is authorized, started or done"
    )


if __name__ == "__main__":
    main()
