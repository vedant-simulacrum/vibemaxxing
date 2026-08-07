#!/usr/bin/env python3
"""Every P-1140F step knows which units and findings it is made of.

`AGENTS.md` says to follow `docs/planning/TASK_CATALOG.md` exactly, and the catalog
names five ordered repair tasks. Until this validator existed, the catalog named zero
work units and the work breakdown named zero repair tasks. The only binding anywhere
was `repair_task` on each finding, which tied findings to steps and left units tied to
nothing.

The consequence was that no one could answer "is P-1140F-2 done?" from the repository.
A step was a paragraph of prose with a hand-maintained `Status:` line beside it, and
that line could say `complete` while six of its units sat `not-started` — nothing
compared them. A gate whose completion is asserted rather than derived is the same
defect this repository has hit five times already, in a new place.

This derives step state instead:

- every unit in the repair series carries a `Repair:` naming a step the catalog defines;
- every step the catalog defines owns at least one unit, so a step cannot quietly empty;
- every finding's `repair_task` names a step that owns units, so a finding cannot be
  parked against a step with no work in it;
- a step's recorded `Status:` may not claim completion while it owns an unlanded unit
  or an unclosed finding.

The last rule is the point. The rest exist so it cannot be satisfied vacuously.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs" / "planning" / "TASK_CATALOG.md"
BREAKDOWN = ROOT / "docs" / "implementation" / "PR_SIZED_WORK_BREAKDOWN.md"
FINDINGS = ROOT / "conformance" / "p1140f" / "semantic-findings-v1.json"

# A step claiming any of these while it still owns open work is the failure this exists
# to catch. `in-progress-planning` and `blocked-planning` claim nothing and are fine.
COMPLETION_CLAIMS = ("complete", "closed", "done", "resolved")

UNIT = re.compile(r"###+\s+(PF-\d{3})\b[^\n]*\n(?P<body>.*?)(?=\n###|\Z)", re.S)
STEP = re.compile(
    r"####\s+(P-1140F-\d)\s*[—–-][^\n]*\n(?P<body>.*?)(?=\n####|\n## |\Z)", re.S
)


class Failure(Exception):
    """A step, unit or finding is bound to something that cannot be checked."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def field(body: str, name: str) -> str | None:
    found = re.search(rf"^{name}:\s*(.+)$", body, re.M)
    return found.group(1).strip() if found else None


def main() -> int:
    catalog = CATALOG.read_text(encoding="utf-8")
    breakdown = BREAKDOWN.read_text(encoding="utf-8")
    findings = json.loads(FINDINGS.read_text(encoding="utf-8"))["findings"]

    steps = {match.group(1): match.group("body") for match in STEP.finditer(catalog)}
    require(bool(steps), "TASK_CATALOG.md defines no P-1140F step")

    units = {match.group(1): match.group("body") for match in UNIT.finditer(breakdown)}
    series = {
        identifier: body
        for identifier, body in units.items()
        if int(identifier.split("-")[1]) <= 36
    }
    require(bool(series), "the work breakdown defines no P-1140F repair unit")

    owned: dict[str, list[str]] = defaultdict(list)
    for identifier, body in sorted(series.items()):
        repair = field(body, "Repair")
        require(
            repair is not None,
            f"{identifier} names no repair task, so no step accounts for it and its "
            "completion changes no step's state",
        )
        require(
            repair in steps,
            f"{identifier} names repair task {repair!r}, which TASK_CATALOG.md does "
            f"not define; the catalog defines {sorted(steps)}",
        )
        owned[repair].append(identifier)

    for step in sorted(steps):
        require(
            bool(owned.get(step)),
            f"{step} is defined in TASK_CATALOG.md and owns no unit, so it is prose "
            "that nothing can complete or fail",
        )

    for finding in findings:
        repair = finding["repair_task"]
        require(
            repair in steps,
            f"{finding['finding_id']} is assigned to {repair!r}, which the catalog "
            "does not define",
        )
        require(
            bool(owned.get(repair)),
            f"{finding['finding_id']} is assigned to {repair}, which owns no unit; the "
            "finding is tracked against a step with no work in it",
        )

    open_findings: dict[str, list[str]] = defaultdict(list)
    for finding in findings:
        if finding["state"] != "closed":
            open_findings[finding["repair_task"]].append(finding["finding_id"])

    for step, body in sorted(steps.items()):
        status = (field(body, "Status") or "").strip("`")
        if not any(claim in status.lower() for claim in COMPLETION_CLAIMS):
            continue
        unlanded = [
            identifier
            for identifier in owned[step]
            if (field(series[identifier], "Status") or "").strip("`") != "landed"
        ]
        require(
            not unlanded,
            f"{step} records Status: {status!r} and owns unlanded units {unlanded}",
        )
        require(
            not open_findings.get(step),
            f"{step} records Status: {status!r} and owns unclosed findings "
            f"{open_findings[step]}",
        )

    print("repair-task binding: pass")
    print(
        "steps="
        + " ".join(
            f"{step}:{len(owned[step])}u/{len(open_findings.get(step, []))}open"
            for step in sorted(steps)
        )
    )
    print(
        "claim_scope=binding-and-status-consistency-only; a bound step is not a "
        "correct one"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as failure:
        print(f"repair-task binding: FAIL — {failure}", file=sys.stderr)
        sys.exit(1)
