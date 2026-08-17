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

- every unit in PF-001..PF-036 carries a `Repair:` naming a step the catalog defines,
  and a unit above that range joins the series by declaring one — but may not claim a
  finding with `Serves:` without it;
- every step the catalog defines owns at least one unit, so a step cannot quietly empty;
- every finding's `repair_task` names a step that owns units, so a finding cannot be
  parked against a step with no work in it;
- a step's recorded `Status:` may not claim completion while it owns an unlanded unit
  or an unclosed finding;
- every `closure_evidence` entry names a unit that serves that finding, that has
  landed, at a commit rather than a branch;
- and, once a finding says the repair is finished, every landed unit that declares it
  serves that finding is cited by it.

The last three rules are the point. The rest exist so they cannot be satisfied
vacuously.
"""

from __future__ import annotations

import json
import re
import subprocess
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

# The highest unit in the repair series as originally authored. Every unit at or below
# it must carry `Repair:`; units above it join the series by declaring one. See `main`.
CORE_SERIES_MAX = 36

UNIT = re.compile(r"###+\s+(PF-\d{3})\b[^\n]*\n(?P<body>.*?)(?=\n###|\Z)", re.S)
STEP = re.compile(
    r"####\s+(P-1140F-\d)\s*[—–-][^\n]*\n(?P<body>.*?)(?=\n####|\n## |\Z)", re.S
)
# A closure-evidence entry opens by naming the unit and the commit it landed at, with
# an optional parenthesised scope for a unit that repaired only part of the finding.
# That qualifier is kept because it carries what the entry does *not* cover, which is
# the half of a partial repair a reader most needs. The prose after the colon is the
# claim; this constrains only the provenance.
EVIDENCE = re.compile(
    r"^(?P<unit>PF-\d{3}) at (?P<sha>[0-9a-f]{40})"
    r"(?: \((?P<scope>[^)]+)\))?: \S"
)

# States in which a finding asserts it is no longer being worked on. Evidence held by
# a unit that has not landed is admissible while repair is in progress and is not
# admissible once the finding claims the repair is finished.
SETTLED_STATES = ("repaired-pending-review", "closed")


def repository_is_shallow() -> bool:
    result = run_git("rev-parse", "--is-shallow-repository")
    return result is not None and result.strip() == "true"


def run_git(*args: str) -> str | None:
    """Stdout of a git command, or None when git cannot answer here."""
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout if completed.returncode == 0 else None


def commit_resolves(sha: str) -> bool | None:
    """True if the commit exists, False if it does not, None if this checkout cannot say.

    CI checks out at `fetch-depth: 1`, so historical commits are genuinely absent
    there and their absence proves nothing. Returning None rather than False keeps a
    shallow clone from failing an honest record — and the summary line reports how
    many went unchecked, so a skip is never read as a pass.
    """
    if run_git("rev-parse", "--git-dir") is None:
        return None
    if run_git("cat-file", "-e", f"{sha}^{{commit}}") is not None:
        return True
    return None if repository_is_shallow() else False


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

    # PF-001..PF-036 are the repair series as it was first written, and every one of
    # them must carry `Repair:`. That requirement is the non-vacuous half: membership of
    # the core does not depend on the field, so a unit that drops it fails rather than
    # leaving the series quietly.
    #
    # Membership was *only* that range, which assumed the set of repairs was final. All
    # thirty-six were taken, so a repair discovered later for a finding that is still
    # open had nowhere to go: PF-037 and above are the general work breakdown, they
    # carry no `Repair:`, and a unit outside the series may not carry `Serves:` either,
    # so nothing landing could be recorded against the finding it repaired. SR-007 is
    # the case — one of its four conflicting artifacts was never touched, and the repair
    # is PF-070.
    #
    # So the series is opened at the top rather than moved: a unit above 36 joins it by
    # *declaring* a repair task. The declaration is the membership test, which keeps the
    # thirty-three units that are not repairs out without listing them.
    core = {
        identifier: body
        for identifier, body in units.items()
        if int(identifier.split("-")[1]) <= CORE_SERIES_MAX
    }
    require(bool(core), "the work breakdown defines no P-1140F repair unit")
    extended = {
        identifier: body
        for identifier, body in units.items()
        if int(identifier.split("-")[1]) > CORE_SERIES_MAX
        and field(body, "Repair") is not None
    }
    # The one way the opening above could be abused: a unit that claims a finding
    # without claiming a step. It would sit outside the series, so no rule below would
    # read it, and `Serves:` would look like a binding while binding nothing.
    for identifier, body in sorted(units.items()):
        if int(identifier.split("-")[1]) <= CORE_SERIES_MAX:
            continue
        require(
            field(body, "Serves") is None or field(body, "Repair") is not None,
            f"{identifier} serves {field(body, 'Serves')!r} and names no repair task. "
            "A unit outside PF-001..PF-036 joins the repair series by declaring "
            "`Repair:`; without it the unit is not in the series, nothing checks the "
            "finding it names, and landing it would record evidence against a step "
            "that does not own it",
        )
    series = {**core, **extended}

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

    # `closure_evidence` was the last binding nothing checked. The schema accepts any
    # non-empty string, so "PF-011 at HEAD of planning/pf-011-trust-domains" passed —
    # and so would a branch that never existed. D-206 records why a branch name is not
    # a record: under squash merge it stops existing the moment it lands, and until
    # then it moves. Four of SR-008's entries were written that way.
    #
    # This does not contradict D-206's refusal of commit ids as landing proof. What
    # proves a unit landed is its `Evidence:` lines, which execute. A sha here is
    # provenance on a narrative claim about a repair — it says where to look, not that
    # the repair is correct.
    unchecked_shas = 0
    evidence_entries = 0
    cited: dict[str, set[str]] = defaultdict(set)
    for row in findings:
        finding_id = row["finding_id"]
        for entry in row["closure_evidence"]:
            evidence_entries += 1
            match = EVIDENCE.match(entry)
            require(
                match is not None,
                f"{finding_id} records closure evidence that does not open "
                f"'PF-NNN at <40-hex commit>: ' — {entry[:72]!r}. A branch name moves "
                "and a bare claim resolves to nothing, so neither can be checked",
            )
            unit, sha = match.group("unit"), match.group("sha")
            cited[finding_id].add(unit)
            require(
                unit in served[finding_id],
                f"{finding_id} cites {unit} as closure evidence, but {unit} does not "
                f"serve it; its serving units are {sorted(served[finding_id])}",
            )
            status = (field(series[unit], "Status") or "").strip("`")
            require(
                status != "not-started",
                f"{finding_id} cites {unit} as closure evidence while {unit} records "
                "Status: 'not-started'; evidence cannot precede the work it describes",
            )
            require(
                status == "landed" or row["state"] not in SETTLED_STATES,
                f"{finding_id} is {row['state']!r} and rests on {unit}, which records "
                f"Status: {status!r}. A finding is not repaired while a unit its own "
                "evidence names is still open",
            )
            resolved = commit_resolves(sha)
            require(
                resolved is not False,
                f"{finding_id} cites {unit} at {sha}, which is not a commit in this "
                "repository",
            )
            if resolved is None:
                unchecked_shas += 1

    # The converse, and the direction that was missing. Everything above reads
    # `closure_evidence` outwards: each entry must name a unit that serves the finding
    # and has landed. Nothing read it inwards. A unit could declare `Serves: SR-0NN`,
    # record `Status: landed`, and appear nowhere in that finding's evidence, and the
    # finding still read as fully evidenced on the entries it happened to carry. SR-007
    # closed without citing PF-073 and SR-009 closed without citing PF-074 exactly that
    # way: both units landed, both declared the finding they served, neither was cited,
    # and each was found by hand after the record already said the repair was done.
    #
    # Why this is asked only of a settled finding. A unit lands in the commit that
    # repairs the artifact. Its evidence entry is a narrative claim about what that
    # repair achieved, and writing the claim in the same commit means writing it before
    # anyone has reviewed the unit it describes. So there is a legitimate interval —
    # unit landed, citation still to be written — and `open` and `repair-in-progress`
    # are the states that mean the finding is inside it. Requiring citation in every
    # state would fail the repository at the moment a repair merges and would push the
    # claim ahead of the review that justifies it, which is the wrong trade for a rule
    # whose whole purpose is to stop unearned claims.
    #
    # `repaired-pending-review` and `closed` assert the interval is over. A finding in
    # either has said nothing further is pending, so a landed unit missing from its own
    # finding's evidence is either evidence nobody wrote or work the finding is silently
    # not accounting for, and neither survives a state that claims the repair is done.
    for row in findings:
        if row["state"] not in SETTLED_STATES:
            continue
        finding_id = row["finding_id"]
        uncited = [
            identifier
            for identifier in sorted(served[finding_id])
            if (field(series[identifier], "Status") or "").strip("`") == "landed"
            and identifier not in cited[finding_id]
        ]
        require(
            not uncited,
            f"{finding_id} is {row['state']!r} and its closure evidence does not cite "
            f"{uncited}, each of which declares it serves {finding_id} and records "
            "Status: 'landed'. A finding that says the repair is finished while a "
            "landed repair of its own is absent from the record reads as fully "
            "evidenced on the evidence it did name",
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
    # Landed-over-served said how much of a finding's work is done and nothing about
    # whether the finding's own record names it. Those are different numbers, and the
    # gap between them is where SR-007 and SR-009 sat: 4/4 landed, three cited, and the
    # printed line looked complete. The third figure is the one a reader needs.
    print(
        "findings(landed/served,cited)="
        + " ".join(
            f"{row['finding_id']}:{sum(1 for u in served[row['finding_id']] if (field(series[u], 'Status') or '').strip('`') == 'landed')}"
            f"/{len(served[row['finding_id']])}"
            f",{len(cited[row['finding_id']])}"
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
    if unchecked_shas:
        print(
            f"closure_evidence={evidence_entries} entries, "
            f"{evidence_entries - unchecked_shas} at commits this checkout can resolve, "
            f"{unchecked_shas} UNRESOLVED HERE (shallow clone; their existence is "
            "unproven, not proven)"
        )
    else:
        print(
            f"closure_evidence={evidence_entries} entries, all at commits this "
            "checkout resolves"
        )
    print(
        "claim_scope=binding-and-status-consistency-only; a bound step is not a "
        "correct one, and a resolved commit is not a correct repair"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as failure:
        print(f"repair-task binding: FAIL — {failure}", file=sys.stderr)
        sys.exit(1)
