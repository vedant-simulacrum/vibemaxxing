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


    # Units bind to steps and findings bind to steps, which was too coarse to say
    # which unit serves which finding: P-1140F-4 owns twelve units and five findings,
    # so "PF-019 landed" implied nothing about SR-012 specifically. Recording closure
    # evidence had to be done by hand and by reading, which is exactly the kind of
    # bookkeeping that goes wrong quietly. `Serves:` closes that, and the two bindings
    # must agree: a unit cannot serve a finding assigned to a different step.
    served: dict[str, list[str]] = defaultdict(list)
    finding_step = {row["finding_id"]: row["repair_task"] for row in findings}
    for identifier, body in sorted(series.items()):
        serves = field(body, "Serves")
        require(
            serves is not None,
            f"{identifier} names no finding it serves, so landing it changes no "
            "finding's evidence and closure has to be assembled by reading",
        )
        for finding in [entry.strip() for entry in serves.split(",")]:
            require(
                finding in finding_step,
                f"{identifier} serves {finding!r}, which is not a recorded finding",
            )
            require(
                finding_step[finding] == field(body, "Repair"),
                f"{identifier} is in {field(body, 'Repair')} and serves {finding}, "
                f"which is assigned to {finding_step[finding]}; a unit cannot repair a "
                "finding its own step does not own",
            )
            served[finding].append(identifier)

    for row in findings:
        require(
            bool(served.get(row["finding_id"])),
            f"{row['finding_id']} is served by no unit, so nothing landing can ever "
            "close it",
        )

    # A finding may only close once every unit serving it has landed. Closure evidence
    # is not the same as closure: a partially repaired finding may carry evidence and
    # must not carry `closed`.
    for row in findings:
        if row["state"] != "closed":
            continue
        outstanding = [
            identifier
            for identifier in served[row["finding_id"]]
            if (field(series[identifier], "Status") or "").strip("`") != "landed"
        ]
        require(
            not outstanding,
            f"{row['finding_id']} is closed and the units serving it are not all "
            f"landed: {outstanding}",
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
        "findings="
        + " ".join(
            f"{row['finding_id']}:{sum(1 for u in served[row['finding_id']] if (field(series[u], 'Status') or '').strip('`') == 'landed')}"
            f"/{len(served[row['finding_id']])}"
            for row in findings
        )
    )
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
