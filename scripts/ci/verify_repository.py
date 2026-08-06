#!/usr/bin/env python3
"""Report what this repository's verification lanes actually executed.

Five outcomes, deliberately distinguished, because collapsing them is how a matrix
comes to claim coverage it does not have:

* pass — the lane ran and every command exited 0.
* fail — the lane ran and a command exited non-zero.
* partial — the lane ran and part of it had nothing to execute. The eval lane is
  partial while most declared suites report not_applicable.
* not_applicable — there is nothing for the lane to run. No manifest, no sources,
  nothing that could be checked. This is the only benign non-execution.
* uncovered — there *is* something for the lane to run and no lane runs it. That is
  a hole in the matrix rather than an absence of work.

The node lane is the reason uncovered exists. It reported not_applicable because
the repository root has no package.json, which is true and irrelevant: apps/web,
packages/ui and scripts/brand are npm workspaces with lockfiles that no workflow has
ever built, and the web home page has never rendered. The green not_applicable is
why nobody noticed.

A hole is recorded rather than hidden. scripts/ci/coverage-baseline-v1.json pins the
outcome every lane produced, and this matrix fails only when coverage gets *worse*
than that record — a lane dropping below its recorded outcome, a recorded lane
disappearing, a lane appearing that the baseline does not record, or any lane
actually failing. A lane sitting at its recorded outcome does not fail the build, so
a known hole stays visible without holding a required check red on a defect that
needs a decision rather than a commit. Improving a lane never fails either, and the
matrix says so when the ceiling could be tightened.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
BASELINE = Path(__file__).resolve().parent / "coverage-baseline-v1.json"

LOCKFILES = ("package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock")
NODE_WORKSPACE_ROOTS = ("apps", "packages", "scripts")

# Worst to best. A lane may sit at its recorded outcome or beat it; producing an
# outcome further left than the record is a regression. `fail` is deliberately absent:
# a lane that ran and failed is never a recordable state, so it can never be baselined
# into silence.
OUTCOME_ORDER = ("uncovered", "not_applicable", "partial", "pass")
RECORDABLE = frozenset(OUTCOME_ORDER)


@dataclass
class Check:
    name: str
    status: str
    command: list[str] | None
    returncode: int | None = None
    note: str | None = None
    detail: dict[str, int] | None = None


def node_workspaces(root: Path) -> list[str]:
    """Return every npm workspace in the repository that has its own lockfile."""
    found: list[str] = []
    if (root / "package.json").is_file():
        found.append(".")
    for parent in NODE_WORKSPACE_ROOTS:
        directory = root / parent
        if not directory.is_dir():
            continue
        for manifest in sorted(directory.glob("*/package.json")):
            if any((manifest.parent / lockfile).is_file() for lockfile in LOCKFILES):
                found.append(str(manifest.parent.relative_to(root)))
    return found


def planned_checks(root: Path) -> list[Check]:
    runner = root / "scripts" / "ci" / "run_evals.py"
    checks = [
        Check("evaluator-unit", "pending", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]),
        Check("evaluator-registry", "pending", [sys.executable, str(runner), "--validate-registry"]),
        Check("evaluator-all-suites", "pending", [sys.executable, str(runner), "--list-suites"]),
    ]
    go_module = root / "apps" / "api" / "go.mod"
    if go_module.is_file():
        checks.extend([
            Check("go-test", "pending", ["go", "test", "./..."]),
            Check("go-vet", "pending", ["go", "vet", "./..."]),
            Check("go-build", "pending", ["go", "build", "./..."]),
        ])
    else:
        checks.append(Check("go", "not_applicable", None, note="no apps/api/go.mod exists"))
    if (root / "Cargo.toml").is_file():
        checks.extend([
            Check("rust-fmt", "pending", ["cargo", "fmt", "--all", "--check"]),
            Check("rust-clippy", "pending", ["cargo", "clippy", "--workspace", "--all-targets", "--all-features", "--", "-D", "warnings"]),
            Check("rust-test", "pending", ["cargo", "test", "--workspace", "--all-features"]),
        ])
    else:
        checks.append(Check("rust", "not_applicable", None, note="no root Cargo.toml exists"))
    checks.append(planned_node_check(root))
    return checks


# `apps/web` depends on `packages/ui` through a `file:` link, and npm will not
# install the link target's own dependencies transitively. Installing `apps/web`
# first leaves `lucide-react` unresolvable, so the order here is load-bearing
# rather than cosmetic.
NODE_WORKSPACE_ORDER = (
    "packages/ui",
    "apps/web",
    "scripts/brand",
    "scripts/ui/playwright-runtime",
)


def ordered_node_workspaces(root: Path) -> list[str]:
    """Every npm workspace, dependency order first, then any not yet ranked."""
    found = set(node_workspaces(root)) - {"."}
    ordered = [name for name in NODE_WORKSPACE_ORDER if name in found]
    return ordered + sorted(found - set(ordered))


def planned_node_check(root: Path) -> Check:
    """Decide whether the node lane runs or is genuinely absent.

    It used to report `uncovered` whenever the repository root had no
    package.json, which was true and useless: four npm workspaces existed and
    nothing built any of them, so `apps/web` failed to compile from the first
    commit that referenced a stylesheet nobody had written, and no check saw it.
    The absence of a root manifest was never the reason the lane could not run;
    it was only the reason nobody had made it.
    """
    if node_workspaces(root) == []:
        return Check("node", "not_applicable", None, note="no npm workspace exists")
    return Check("node", "pending", None)


def run_check(check: Check, root: Path) -> None:
    if check.name == "evaluator-all-suites":
        run_all_suites(check, root)
        return
    if check.name == "node":
        commands = [
            ["npm", "ci"],
            ["npm", "run", "lint", "--if-present"],
            ["npm", "run", "typecheck", "--if-present"],
            ["npm", "test", "--if-present"],
            ["npm", "run", "build", "--if-present"],
        ]
        check.returncode = 0
        covered: list[str] = []
        for workspace in ordered_node_workspaces(root):
            for command in commands:
                check.returncode = subprocess.run(
                    command,
                    cwd=root / workspace,
                    capture_output=True,
                    text=True,
                    check=False,
                ).returncode
                if check.returncode != 0:
                    check.note = f"{workspace}: {' '.join(command)} exited {check.returncode}"
                    break
            if check.returncode != 0:
                break
            covered.append(workspace)
        if check.returncode == 0:
            check.note = f"built {len(covered)} workspace(s) in dependency order: {', '.join(covered)}"
    else:
        assert check.command is not None
        working_directory = root / "apps" / "api" if check.name.startswith("go-") else root
        check.returncode = subprocess.run(check.command, cwd=working_directory, capture_output=True, text=True, check=False).returncode
    check.status = "pass" if check.returncode == 0 else "fail"


def run_all_suites(check: Check, root: Path) -> None:
    """Run every registered suite and record what each one actually did.

    The previous implementation kept only the first non-zero return code, which made
    not_applicable indistinguishable from pass: downgrading a real suite made this
    check greener, because a suite that executes nothing cannot fail.
    """
    assert check.command is not None
    listed = subprocess.run(check.command, cwd=root, capture_output=True, text=True, check=False)
    executed, skipped, failed = 0, 0, 0
    returncodes = [listed.returncode]
    for suite in listed.stdout.splitlines():
        command = [sys.executable, str(root / "scripts" / "ci" / "run_evals.py"), "--suite", suite]
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
        returncodes.append(completed.returncode)
        status = suite_result_status(completed.stdout)
        if status == "not_applicable":
            skipped += 1
        elif completed.returncode == 0 and status == "pass":
            executed += 1
        else:
            failed += 1
    check.returncode = next((returncode for returncode in returncodes if returncode != 0), 0)
    check.detail = {"executed": executed, "not_applicable": skipped, "failed": failed}
    if check.returncode != 0 or failed:
        check.status = "fail"
    elif skipped:
        check.status = "partial"
        check.note = f"{executed} of {executed + skipped} suites executed; {skipped} reported not_applicable and ran nothing. The recorded ceiling in evals/suites/status-baseline-v1.json is what stops that number growing."
    else:
        check.status = "pass"


def suite_result_status(stdout: str) -> str:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return "unreadable"
    status = payload.get("status") if isinstance(payload, dict) else None
    return status if isinstance(status, str) else "unreadable"


def load_coverage_baseline(path: Path) -> dict[str, str]:
    """Read the recorded coverage ceiling, failing closed on anything unreadable.

    A baseline that cannot be parsed is not an absent constraint. It is a broken one,
    and the only safe reading of a broken constraint is that it is violated.

    Every lane recorded as anything other than pass must carry a justification naming
    a reference and a note, so a recorded hole is always attributable to a decision
    somebody can go and read.
    """
    try:
        document = json.loads(path.read_text())
    except OSError as error:
        raise ValueError(f"unreadable coverage baseline {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON coverage baseline {path}: {error.msg}") from error
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ValueError("coverage baseline must declare schema_version 1")
    recorded = document.get("lanes")
    if not isinstance(recorded, dict) or not recorded:
        raise ValueError("coverage baseline must declare a nonempty lanes object")
    justifications = document.get("justifications", {})
    if not isinstance(justifications, dict):
        raise ValueError("coverage baseline justifications must be an object")
    for lane, outcome in recorded.items():
        if not isinstance(outcome, str) or outcome not in RECORDABLE:
            raise ValueError(f"coverage baseline records an unrecordable outcome for {lane}: {outcome!r}")
        if outcome == "pass":
            continue
        justification = justifications.get(lane)
        if not isinstance(justification, dict) or not justification.get("reference") or not justification.get("note"):
            raise ValueError(f"coverage baseline records {lane} as {outcome} without a justification naming a reference and a note")
    return recorded


def coverage_regressions(checks: list[Check], recorded: dict[str, str]) -> list[str]:
    """Compare the matrix against the recorded ceiling.

    Four things are regressions: a lane dropping below its recorded outcome, a
    recorded lane disappearing from the matrix, a lane appearing that the baseline
    does not record, and any lane that actually failed. The middle two matter because
    without them the gate is trivially evaded — delete the lane, or rename it, and the
    ceiling has nothing to compare against.

    Sitting at the recorded outcome is not a regression, so a known hole does not hold
    the build red. Beating it is not one either, so improving coverage cannot.
    """
    failures: list[str] = []
    observed = {check.name: check.status for check in checks}
    for lane in sorted(set(recorded) - set(observed)):
        failures.append(f"lane {lane} is recorded in the coverage baseline but the matrix no longer plans it; removing a lane is a coverage regression")
    for lane in sorted(set(observed) - set(recorded)):
        failures.append(f"lane {lane} is not recorded in the coverage baseline; record its outcome there so a later regression has something to regress against")
    for lane in sorted(set(observed) & set(recorded)):
        status = observed[lane]
        if status == "fail":
            failures.append(f"lane {lane} failed; a failing lane is never a recordable outcome and cannot be baselined away")
        elif status not in RECORDABLE:
            failures.append(f"lane {lane} produced an unrecognised outcome: {status!r}")
        elif OUTCOME_ORDER.index(status) < OUTCOME_ORDER.index(recorded[lane]):
            failures.append(f"lane {lane} regressed from {recorded[lane]} to {status}; a worse outcome requires an explicit edit to the recorded coverage baseline")
    return failures


def improved_lanes(checks: list[Check], recorded: dict[str, str]) -> list[str]:
    """Lanes now doing better than the record, so the ceiling can be tightened."""
    observed = {check.name: check.status for check in checks}
    return sorted(
        lane
        for lane, status in observed.items()
        if status in RECORDABLE
        and lane in recorded
        and OUTCOME_ORDER.index(status) > OUTCOME_ORDER.index(recorded[lane])
    )


def summarise(checks: list[Check]) -> dict[str, object]:
    outcomes: dict[str, int] = {}
    for check in checks:
        outcomes[check.status] = outcomes.get(check.status, 0) + 1
    return {
        "checks": [
            {
                key: value
                for key, value in (
                    ("name", check.name),
                    ("status", check.status),
                    ("command", check.command),
                    ("returncode", check.returncode),
                    ("detail", check.detail),
                    ("note", check.note),
                )
                if key in {"name", "status", "command", "returncode"} or value is not None
            }
            for check in checks
        ],
        "outcomes": dict(sorted(outcomes.items())),
        "claim_scope": "executed-lanes-only",
        "claim_note": "not_applicable and uncovered lanes executed nothing; only pass means every command in the lane ran and succeeded",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--baseline", type=Path, default=BASELINE, help="recorded coverage ceiling")
    arguments = parser.parse_args(argv)

    checks = planned_checks(ROOT)
    for check in checks:
        if check.status == "pending":
            run_check(check, ROOT)
    summary = summarise(checks)

    try:
        recorded = load_coverage_baseline(arguments.baseline)
    except ValueError as error:
        print(json.dumps(summary, indent=2))
        print(f"invalid coverage baseline: {error}", file=sys.stderr)
        return 2

    failures = coverage_regressions(checks, recorded)
    improved = improved_lanes(checks, recorded)
    summary["baseline"] = {"recorded": recorded, "regressions": failures, "improved": improved}
    print(json.dumps(summary, indent=2))

    if failures:
        print("verification matrix: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    executed = sum(1 for check in checks if check.status == "pass")
    print(f"verification matrix: PASS ({len(checks)} lanes, {executed} fully executed, {len(checks) - executed} at their recorded ceiling)")
    if improved:
        print("coverage baseline may be tightened; these lanes now beat their record: " + ", ".join(improved))
    print("claim_scope=recorded-coverage-only; a lane at its recorded ceiling executed no more than it did when the ceiling was written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
