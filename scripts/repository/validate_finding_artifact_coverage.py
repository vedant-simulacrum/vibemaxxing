#!/usr/bin/env python3
"""Every conflicting artifact a settled finding names was touched, or records why not.

`validate_repair_task_binding.py` proved that each `closure_evidence` entry names a
unit that serves the finding, that has landed, at a commit that resolves. It never
asked the next question: *did that commit go anywhere near the artifact the finding is
about?* So a finding could name four conflicting artifacts, carry four impeccably
formatted evidence entries, and leave one of those artifacts untouched by every commit
it cites — which is exactly what SR-007 did. `openapi-v1.yaml#ClaimChallenge` was named
by the finding, repaired by nothing, and the finding was recorded
`repaired-pending-review` on evidence covering three of four. It was caught by hand,
twice, after the record already said the repair was done.

An audit of all thirteen findings found the same shape in three more places: twelve
artifacts across four findings were untouched by every commit their own finding's
closure evidence cites. Hand-auditing found it; nothing in `make validate` would have.

**The rule is not "every artifact must be modified".** That rule is wrong, and stating
why is the whole design. A finding of class `contradiction` names the artifacts that
disagree. If A contradicts B and the repair decided B was the defect, then A is correct,
A is untouched, and A is nonetheless resolved. SR-015 is the honest case: it names
`planning-schema.sql#score_snapshots` and the invariant it asserts is that a display
boundary rechecks *current* authorization instead of replaying a sealed snapshot — the
snapshot table is supposed to be immutable and untouched. Demanding a diff there would
push someone to edit a table to satisfy a validator, which is worse than the defect.

So the rule is a disjunction: every conflicting artifact of a finding that claims to be
settled is either

- touched by a commit that finding's own `closure_evidence` cites, or
- named in that finding's `unmodified_artifacts` with a recorded reason it did not need
  to change.

An untouched artifact with no recorded reason fails. That is the SR-007 case.

And the reverse check, which is what stops the escape hatch becoming the exit: a reason
recorded for an artifact that *was* touched also fails. Without it, `unmodified_artifacts`
would be a place to park a sentence and forget it — the excuse would outlive the
condition that justified it, and a later commit that did modify the artifact would leave
a record claiming it needed no modification. This is the same guard
`check_absence_reasons` applies to `RECORDED_ABSENCES` in `validate_state_vocabularies.py`,
built for that table and never applied to this one, because until now this one did not
exist.

**Why a separate validator rather than a rule inside `validate_repair_task_binding.py`.**
That script ends by printing `claim_scope=binding-and-status-consistency-only`, and it
means it: every rule in it reads records against records. This one reads records against
the git object store, which is a different kind of claim with a different failure mode —
it degrades in a shallow clone, where the others do not. Folding it in would make that
`claim_scope` line untrue and would give one validator two reasons to be unavailable.
The two are ordered together in `make validate` and in CI instead.

**What a pass does not mean.** Coverage here is file-level. A finding names
`planning-schema.sql#verifier_appraisals` and git can only report that
`planning-schema.sql` changed; it cannot report that the `verifier_appraisals` table
changed, and a commit touching an unrelated table in the same file satisfies this check.
So a pass says the repair went to the right *file*, not that it repaired the right
*thing*. Fragment-level coverage is what the per-finding acceptance criteria and the
contract validators are for. This catches the case where the repair never opened the
file at all, which is the case that actually occurred, four times.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FINDINGS = ROOT / "conformance" / "p1140f" / "semantic-findings-v1.json"

# States in which a finding asserts the repair is finished. Coverage is required only
# here. A finding that is `open` or `repair-in-progress` is *supposed* to have artifacts
# nothing has touched yet — that is what those states mean, and failing them would
# punish an honest record. SR-016 is open with four untouched artifacts and is correct.
SETTLED_STATES = ("repaired-pending-review", "closed")

# Long enough that a reason has to be a sentence. `RECORDED_ABSENCES` reasons run to a
# clause explaining the mechanism; "n/a" and "not needed" are the failure this prevents.
MINIMUM_REASON = 40

SHA = re.compile(r"\b[0-9a-f]{40}\b")


def run_git(*args: str) -> str | None:
    """Stdout of a git command, or None when git cannot answer here."""
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout if completed.returncode == 0 else None


def repository_is_shallow() -> bool:
    result = run_git("rev-parse", "--is-shallow-repository")
    return result is not None and result.strip() == "true"


def changed_paths(sha: str) -> set[str] | None:
    """Paths a commit changed, or None when this checkout cannot say.

    Copied in shape from `commit_resolves()` in `validate_repair_task_binding.py`, and
    for the same reason: a commit that is genuinely absent from a shallow clone proves
    nothing about the artifact, so returning None keeps an honest record from failing
    on a checkout depth. The summary reports how many went unresolved, and a finding
    with any unresolved commit has its verdict downgraded to `unchecked` rather than to
    `pass`, so a skip is never read as coverage.
    """
    if run_git("rev-parse", "--git-dir") is None:
        return None
    if run_git("cat-file", "-e", f"{sha}^{{commit}}") is None:
        return None
    output = run_git("show", "--name-only", "--pretty=format:", sha)
    if output is None:
        return None
    return {line.strip() for line in output.splitlines() if line.strip()}


def artifact_path(artifact: str) -> str:
    """The repository path an artifact names, without its `#fragment`."""
    return artifact.split("#", 1)[0]


def is_touched(path: str, touched: set[str]) -> bool:
    """A file matches exactly; a directory artifact matches any path beneath it."""
    if path in touched:
        return True
    prefix = path if path.endswith("/") else path + "/"
    return any(candidate.startswith(prefix) for candidate in touched)


class Failure(Exception):
    """A finding claims a repair that never reached an artifact it named."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def main() -> int:
    findings = json.loads(FINDINGS.read_text(encoding="utf-8"))["findings"]

    total_artifacts = 0
    total_touched = 0
    total_explained = 0
    total_unchecked = 0
    unresolved_shas: set[str] = set()
    lines: list[str] = []

    for row in findings:
        finding_id = row["finding_id"]
        artifacts = row["conflicting_artifacts"]
        excused: dict[str, str] = row.get("unmodified_artifacts", {})

        shas = sorted(
            {sha for entry in row["closure_evidence"] for sha in SHA.findall(entry)}
        )
        touched: set[str] = set()
        unresolved: list[str] = []
        for sha in shas:
            paths = changed_paths(sha)
            if paths is None:
                unresolved.append(sha)
                unresolved_shas.add(sha)
                continue
            touched |= paths

        # Reverse check, applied in every state. An excuse is a claim about the repair,
        # and a claim that has stopped being true is worse than no claim: it reads as a
        # considered decision. This fires whether the finding is settled or not, because
        # a stale excuse on an open finding is just as misleading.
        for artifact, reason in sorted(excused.items()):
            require(
                artifact in artifacts,
                f"{finding_id} records {artifact!r} in unmodified_artifacts and does "
                "not name it in conflicting_artifacts. A reason to leave an artifact "
                "alone that the finding does not claim is a reason about nothing",
            )
            require(
                isinstance(reason, str) and len(reason.strip()) >= MINIMUM_REASON,
                f"{finding_id} records {artifact!r} as unmodified with a reason of "
                f"{len(str(reason).strip())} characters; at least {MINIMUM_REASON} are "
                "required. A reason has to state why the contradiction is resolved "
                "elsewhere, which cannot be done in a word",
            )
            if unresolved:
                continue
            require(
                not is_touched(artifact_path(artifact), touched),
                f"{finding_id} records {artifact!r} as needing no change, and a commit "
                "its own closure evidence cites modified that file. The reason has "
                "outlived the condition it described — either the repair did touch the "
                "artifact and the entry should be removed, or the evidence cites a "
                "commit that does not belong to this finding",
            )

        if row["state"] not in SETTLED_STATES:
            lines.append(
                f"{finding_id}:{row['state']}:not-required "
                f"({len(artifacts)} artifacts, coverage not required in this state)"
            )
            continue

        require(
            bool(shas) or not artifacts,
            f"{finding_id} is {row['state']!r} and its closure evidence cites no "
            f"commit, while it names {len(artifacts)} conflicting artifacts. A repair "
            "recorded as finished with no commit behind it covers nothing",
        )

        missing: list[str] = []
        covered = 0
        explained = 0
        for artifact in artifacts:
            total_artifacts += 1
            if is_touched(artifact_path(artifact), touched):
                covered += 1
                total_touched += 1
            elif artifact in excused:
                explained += 1
                total_explained += 1
            else:
                missing.append(artifact)

        if unresolved:
            # We cannot distinguish "no cited commit touched it" from "the commit that
            # touched it is not in this checkout". Reporting it as a pass would be the
            # exact self-satisfaction this validator exists to remove.
            total_unchecked += len(missing)
            lines.append(
                f"{finding_id}:{covered}touched/{explained}explained/"
                f"{len(missing)}UNCHECKED ({len(unresolved)} commits unresolved here)"
            )
            continue

        require(
            not missing,
            f"{finding_id} is {row['state']!r} and names conflicting artifacts that no "
            f"commit in its own closure evidence touched: {missing}. Either a unit "
            "repairs the artifact and records evidence at the commit it landed in, or "
            "the finding records the artifact in unmodified_artifacts with the reason "
            "the contradiction it was named for is resolved in the artifact it "
            "contradicted. Recording a finding as repaired on evidence that never "
            "reached one of its own named artifacts is the defect this program exists "
            f"to remove — it is what happened to SR-007. Commits cited: {shas}",
        )
        lines.append(f"{finding_id}:{covered}touched/{explained}explained")

    print("finding artifact coverage: pass")
    print("findings=" + " ".join(lines))
    print(
        f"artifacts={total_artifacts} in settled findings, {total_touched} touched by a "
        f"cited commit, {total_explained} recorded as needing no change"
    )
    if unresolved_shas:
        print(
            f"UNRESOLVED: {len(unresolved_shas)} cited commits do not exist in this "
            f"checkout and {total_unchecked} artifacts could not be checked against "
            "them (shallow clone; their coverage is unproven, not proven). CI checks "
            "out at fetch-depth: 0, where this number is 0"
        )
    print(
        "claim_scope=file-level-coverage-only; a cited commit touching the file is not "
        "a repair of the fragment, and a recorded reason is a claim a reviewer must "
        "read rather than one this validator can verify"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as failure:
        print(f"finding artifact coverage: FAIL — {failure}", file=sys.stderr)
        sys.exit(1)
