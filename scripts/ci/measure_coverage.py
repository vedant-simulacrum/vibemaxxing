#!/usr/bin/env python3
"""Measure real test coverage per executable surface and hold it against a record.

`docs/verification/TEST_STRATEGY.md` has stated coverage floors since it was written
and no number had ever been measured against them, so every floor was a threshold with
nothing on the other side of it. This measures the three surfaces that actually execute
something, and compares each against the ceiling recorded in
`scripts/ci/measured-coverage-baseline-v1.json`.

Three surfaces, three native tools, no third-party runner:

* `python-planning-tooling` — `scripts/ci` and `scripts/repository` under
  `coverage.py`, driven by the `tests/` unit suite. Line-and-branch, because a
  validator is mostly branches and a line-only number over one flatters it. In-process
  only: several tests exercise a validator by invoking it as a child process, and this
  measurement does not see any of that. Child-process capture was tried and rejected —
  it produced a number six points higher on one run and not on the next, and a ceiling
  that moves because a `.pth` file did or did not fire is not a ceiling. The number is
  therefore a lower bound on what the suite executes, and the modules it reads as 0%
  are listed in the output so the undercount is visible rather than assumed away.
* `rust-vibeproof-core` — `-C instrument-coverage` with the `llvm-profdata` and
  `llvm-cov` that ship in rustup's `llvm-tools-preview` component. Line. Nothing is
  installed from crates.io to measure this; `cargo-llvm-cov` produces the identical
  number and is one more pinned dependency for it.
* `go-apps-api` — `go test -coverprofile`. Statement, which is the only unit `go test`
  counts.

The rule is the one the repository already applies to lane outcomes and eval statuses:
a number may not get worse than the recorded one. Improving never fails. A missing or
malformed baseline fails closed, because an unreadable constraint is a broken one and
the only safe reading of a broken constraint is that it is violated. Editing the
baseline is the only sanctioned way to record a worse number, so a deliberate one
leaves a reviewable diff and a silent one turns this red.

**Regression from added code, versus regression from a file that moved.** A percentage
falls for two very different reasons and this reports which. Every scope records its
denominator — total measured units — alongside its percentage, and a regression is
classified by comparing denominators:

* denominator grew: new units arrived and the covered fraction fell. That is new
  uncovered code and it is the signal the check exists for.
* denominator shrank: the scope lost units. A file moved out, or covered code was
  deleted. Look at the scope it moved to before re-recording anything.
* denominator unchanged: units that used to execute no longer do. A test was removed,
  skipped or weakened.

A file moving *within* a scope is invisible here, because a scope is a directory rather
than a file list. A file moving *between* scopes shows as two opposite-signed
denominator deltas, which this names but does not resolve on its own: a human reads two
numbers. That residual is accepted rather than solved, and it is bounded by the fact
that the repository has three scopes.

Claim scope: this says what fraction of units executed. It does not say an assertion
was made about any of them. That is why `TEST_STRATEGY.md` states floors rather than
targets and why it also requires a mutation pass before each ring expansion.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BASELINE = Path(__file__).resolve().parent / "measured-coverage-baseline-v1.json"

# Everything the profiler should never count: vendored crates, the standard library,
# and the test files themselves. Measuring a test file measures whether the test ran.
RUST_IGNORE = (
    r"(/\.cargo/registry/|/rustc/|/crates/[^/]+/tests/|/crates/[^/]+/benches/)"
)

PYTHON_SOURCES = ("scripts/ci", "scripts/repository")


@dataclass
class Measurement:
    """One surface, measured or explicitly not."""

    scope: str
    language: str
    metric: str
    measured: bool
    percent: float | None = None
    covered_units: int | None = None
    total_units: int | None = None
    tool: str | None = None
    note: str | None = None
    detail: dict[str, object] = field(default_factory=dict)

    def as_json(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "scope": self.scope,
            "language": self.language,
            "metric": self.metric,
            "measured": self.measured,
        }
        if self.measured:
            payload["percent"] = self.percent
            payload["covered_units"] = self.covered_units
            payload["total_units"] = self.total_units
        if self.tool:
            payload["tool"] = self.tool
        if self.note:
            payload["note"] = self.note
        if self.detail:
            payload["detail"] = self.detail
        return payload


def percentage(covered: int, total: int) -> float:
    """Percent to two decimals, computed from integers so it does not drift."""
    if total <= 0:
        return 0.0
    return round(covered * 100.0 / total, 2)


# -- python ------------------------------------------------------------------------


def measure_python(root: Path, python: str | None = None) -> Measurement:
    """Run the unit suite under coverage.py over the two validator packages."""
    scope, language, metric = "python-planning-tooling", "python", "line-and-branch"
    interpreter = python or sys.executable
    if not module_available(interpreter, "coverage"):
        return Measurement(
            scope,
            language,
            metric,
            measured=False,
            note=(
                "coverage.py is not importable by this interpreter; it is pinned in "
                "requirements-planning.txt, so run `make venv` or install that file"
            ),
        )
    with tempfile.TemporaryDirectory(prefix="measured-coverage-") as directory:
        workspace = Path(directory)
        rcfile = workspace / "coveragerc"
        sources = "\n".join(f"    {name}" for name in PYTHON_SOURCES)
        rcfile.write_text(
            "[run]\n"
            "branch = True\n"
            # In-process only, deliberately. `patch = subprocess` would also count the
            # validators the suite drives as child processes, and on this repository it
            # added about six points on one run and nothing on the next depending on
            # whether the site-packages .pth fired. A ceiling that moves for that reason
            # measures the environment rather than the tests, so the undercount is
            # accepted and named instead: see modules_at_zero_percent below.
            f"data_file = {workspace / 'coverage'}\n"
            f"source =\n{sources}\n",
            encoding="utf-8",
        )
        base = [interpreter, "-m", "coverage"]
        run = subprocess.run(
            [
                *base,
                "run",
                f"--rcfile={rcfile}",
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if run.returncode != 0:
            return Measurement(
                scope,
                language,
                metric,
                measured=False,
                tool="coverage.py",
                note=(
                    f"the unit suite exited {run.returncode} under coverage; a coverage "
                    "number taken from a failing suite is not a measurement"
                ),
            )
        report = workspace / "coverage.json"
        exported = subprocess.run(
            [*base, "json", f"--rcfile={rcfile}", "-o", str(report), "-q"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if exported.returncode != 0 or not report.is_file():
            return Measurement(
                scope,
                language,
                metric,
                measured=False,
                tool="coverage.py",
                note=f"coverage json export exited {exported.returncode}",
            )
        totals = json.loads(report.read_text())["totals"]
        zero = sorted(
            name
            for name, entry in json.loads(report.read_text())["files"].items()
            if entry["summary"]["percent_covered"] == 0
        )
    covered = totals["covered_lines"] + totals["covered_branches"]
    total = totals["num_statements"] + totals["num_branches"]
    return Measurement(
        scope,
        language,
        metric,
        measured=True,
        percent=percentage(covered, total),
        covered_units=covered,
        total_units=total,
        tool="coverage.py",
        detail={
            "sources": list(PYTHON_SOURCES),
            "driver": "python -m unittest discover -s tests",
            "statements": totals["num_statements"],
            "branches": totals["num_branches"],
            "modules_at_zero_percent": zero,
        },
    )


def module_available(interpreter: str, module: str) -> bool:
    """Whether that interpreter can import that module. An absent interpreter is a no."""
    try:
        completed = subprocess.run(
            [interpreter, "-c", f"import {module}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return completed.returncode == 0


# -- rust --------------------------------------------------------------------------


def rust_llvm_tools() -> tuple[Path, Path] | None:
    """Locate llvm-profdata and llvm-cov inside the active rustup toolchain."""
    if shutil.which("rustc") is None:
        return None
    sysroot = subprocess.run(
        ["rustc", "--print", "sysroot"], capture_output=True, text=True, check=False
    )
    version = subprocess.run(
        ["rustc", "-vV"], capture_output=True, text=True, check=False
    )
    if sysroot.returncode != 0 or version.returncode != 0:
        return None
    host = next(
        (
            line.split(": ", 1)[1]
            for line in version.stdout.splitlines()
            if line.startswith("host: ")
        ),
        None,
    )
    if host is None:
        return None
    binaries = Path(sysroot.stdout.strip()) / "lib" / "rustlib" / host / "bin"
    profdata, cov = binaries / "llvm-profdata", binaries / "llvm-cov"
    return (profdata, cov) if profdata.is_file() and cov.is_file() else None


def measure_rust(root: Path) -> Measurement:
    """Build the workspace instrumented, run every test binary, export the summary."""
    scope, language, metric = "rust-vibeproof-core", "rust", "line"
    if not (root / "Cargo.toml").is_file():
        return Measurement(
            scope, language, metric, measured=False, note="no root Cargo.toml exists"
        )
    if shutil.which("cargo") is None:
        return Measurement(
            scope, language, metric, measured=False, note="cargo is not on PATH"
        )
    tools = rust_llvm_tools()
    if tools is None:
        return Measurement(
            scope,
            language,
            metric,
            measured=False,
            note=(
                "llvm-profdata and llvm-cov were not found in the active toolchain; run "
                "`rustup component add llvm-tools-preview`"
            ),
        )
    profdata, llvm_cov = tools
    with tempfile.TemporaryDirectory(prefix="measured-coverage-rust-") as directory:
        workspace = Path(directory)
        # Instrumented build scripts and proc macros run during the build and write a
        # profile wherever LLVM_PROFILE_FILE points, defaulting to the current
        # directory. Setting it on the build too keeps `default_*.profraw` out of the
        # working tree, which is the difference between a measurement and a mess.
        profile_pattern = str(workspace / "cov-%p-%m.profraw")
        build = subprocess.run(
            [
                "cargo",
                "test",
                "--workspace",
                "--all-features",
                "--no-run",
                "--message-format=json",
                "--target-dir",
                str(workspace / "target"),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            env={
                **os.environ,
                "RUSTFLAGS": "-C instrument-coverage",
                "LLVM_PROFILE_FILE": profile_pattern,
            },
        )
        if build.returncode != 0:
            return Measurement(
                scope,
                language,
                metric,
                measured=False,
                tool="llvm-cov",
                note=f"instrumented `cargo test --no-run` exited {build.returncode}",
            )
        binaries = test_binaries(build.stdout)
        if not binaries:
            return Measurement(
                scope,
                language,
                metric,
                measured=False,
                tool="llvm-cov",
                note="the instrumented build produced no test binary",
            )
        environment = {**os.environ, "LLVM_PROFILE_FILE": profile_pattern}
        for binary in binaries:
            executed = subprocess.run(
                [binary],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )
            if executed.returncode != 0:
                return Measurement(
                    scope,
                    language,
                    metric,
                    measured=False,
                    tool="llvm-cov",
                    note=f"instrumented test binary {Path(binary).name} exited {executed.returncode}",
                )
        raw = sorted(workspace.glob("*.profraw"))
        if not raw:
            return Measurement(
                scope,
                language,
                metric,
                measured=False,
                tool="llvm-cov",
                note="the instrumented test binaries wrote no profile",
            )
        merged = workspace / "merged.profdata"
        subprocess.run(
            [
                str(profdata),
                "merge",
                "-sparse",
                *[str(path) for path in raw],
                "-o",
                str(merged),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        objects: list[str] = []
        for binary in binaries:
            objects.extend(["-object", binary])
        exported = subprocess.run(
            [
                str(llvm_cov),
                "export",
                "--instr-profile",
                str(merged),
                *objects,
                "--summary-only",
                f"--ignore-filename-regex={RUST_IGNORE}",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if exported.returncode != 0:
            return Measurement(
                scope,
                language,
                metric,
                measured=False,
                tool="llvm-cov",
                note=f"llvm-cov export exited {exported.returncode}",
            )
        report = json.loads(exported.stdout)
    data = report["data"][0]
    lines = data["totals"]["lines"]
    files = sorted(
        str(Path(entry["filename"]).relative_to(root))
        if Path(entry["filename"]).is_relative_to(root)
        else entry["filename"]
        for entry in data.get("files", [])
    )
    return Measurement(
        scope,
        language,
        metric,
        measured=True,
        percent=percentage(lines["covered"], lines["count"]),
        covered_units=lines["covered"],
        total_units=lines["count"],
        tool="llvm-cov",
        detail={
            "driver": "RUSTFLAGS=-C instrument-coverage cargo test --workspace --all-features",
            "functions": data["totals"]["functions"],
            "files": files,
        },
    )


def test_binaries(message_stream: str) -> list[str]:
    """Every test executable cargo reported building, in build order."""
    found: list[str] = []
    for line in message_stream.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            not isinstance(message, dict)
            or message.get("reason") != "compiler-artifact"
        ):
            continue
        executable = message.get("executable")
        if executable and message.get("profile", {}).get("test"):
            found.append(executable)
    return found


# -- go ----------------------------------------------------------------------------


def measure_go(root: Path) -> Measurement:
    """Run `go test -coverprofile` over the module and total the profile itself.

    The percentage `go test` prints is per package; totalling the profile is the only
    way to get one number for the module that stays right when a second package lands.
    """
    scope, language, metric = "go-apps-api", "go", "statement"
    module = root / "apps" / "api"
    if not (module / "go.mod").is_file():
        return Measurement(
            scope, language, metric, measured=False, note="no apps/api/go.mod exists"
        )
    if shutil.which("go") is None:
        return Measurement(
            scope, language, metric, measured=False, note="go is not on PATH"
        )
    with tempfile.TemporaryDirectory(prefix="measured-coverage-go-") as directory:
        profile = Path(directory) / "cover.out"
        tested = subprocess.run(
            ["go", "test", f"-coverprofile={profile}", "./..."],
            cwd=module,
            capture_output=True,
            text=True,
            check=False,
        )
        if tested.returncode != 0:
            return Measurement(
                scope,
                language,
                metric,
                measured=False,
                tool="go test -coverprofile",
                note=f"`go test ./...` exited {tested.returncode}; a coverage number from a failing suite is not a measurement",
            )
        if not profile.is_file():
            return Measurement(
                scope,
                language,
                metric,
                measured=False,
                tool="go test -coverprofile",
                note="go test wrote no coverage profile",
            )
        covered, total, packages = read_go_profile(profile.read_text())
    listed = subprocess.run(
        ["go", "list", "-f", "{{.ImportPath}} {{.Name}}", "./..."],
        cwd=module,
        capture_output=True,
        text=True,
        check=False,
    )
    non_main = sorted(
        line.split(" ", 1)[0]
        for line in listed.stdout.splitlines()
        if line.strip() and line.rsplit(" ", 1)[-1] != "main"
    )
    return Measurement(
        scope,
        language,
        metric,
        measured=True,
        percent=percentage(covered, total),
        covered_units=covered,
        total_units=total,
        tool="go test -coverprofile",
        detail={
            "driver": "go test -coverprofile ./... in apps/api",
            "packages": packages,
            "non_main_packages": non_main,
        },
    )


def read_go_profile(text: str) -> tuple[int, int, list[str]]:
    """Total a Go coverage profile: covered statements, all statements, packages."""
    covered = total = 0
    packages: set[str] = set()
    for line in text.splitlines()[1:]:
        if not line.strip():
            continue
        position, statements, count = line.rsplit(" ", 2)
        packages.add(position.rsplit("/", 1)[0] if "/" in position else position)
        total += int(statements)
        if int(count) > 0:
            covered += int(statements)
    return covered, total, sorted(packages)


# -- baseline ----------------------------------------------------------------------

REQUIRED_SCOPE_FIELDS = (
    "language",
    "metric",
    "percent",
    "covered_units",
    "total_units",
)


def load_baseline(path: Path) -> dict[str, object]:
    """Read the recorded ceiling, failing closed on anything unreadable.

    Same rule as `scripts/ci/coverage-baseline-v1.json`: a baseline that cannot be
    parsed is not an absent constraint, it is a broken one. A scope recorded without a
    floor must say why it has none, so an absent floor is always attributable to a
    reason somebody can read rather than to an omission nobody noticed.
    """
    try:
        document = json.loads(path.read_text())
    except OSError as error:
        raise ValueError(f"unreadable coverage baseline {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid JSON coverage baseline {path}: {error.msg}"
        ) from error
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ValueError("coverage baseline must declare schema_version 1")
    tolerance = document.get("tolerance_percentage_points")
    if (
        not isinstance(tolerance, (int, float))
        or isinstance(tolerance, bool)
        or tolerance < 0
    ):
        raise ValueError(
            "coverage baseline must declare a non-negative tolerance_percentage_points"
        )
    scopes = document.get("scopes")
    if not isinstance(scopes, dict) or not scopes:
        raise ValueError("coverage baseline must declare a nonempty scopes object")
    for name, record in scopes.items():
        if not isinstance(record, dict):
            raise ValueError(f"coverage baseline scope {name} must be an object")
        for key in REQUIRED_SCOPE_FIELDS:
            if key not in record:
                raise ValueError(f"coverage baseline scope {name} is missing {key}")
        percent = record["percent"]
        if (
            not isinstance(percent, (int, float))
            or isinstance(percent, bool)
            or not 0 <= percent <= 100
        ):
            raise ValueError(
                f"coverage baseline scope {name} records a percent outside 0-100: {percent!r}"
            )
        for key in ("covered_units", "total_units"):
            units = record[key]
            if not isinstance(units, int) or isinstance(units, bool) or units < 0:
                raise ValueError(
                    f"coverage baseline scope {name} records a non-integer {key}: {units!r}"
                )
        if record["covered_units"] > record["total_units"]:
            raise ValueError(
                f"coverage baseline scope {name} records more covered units than total units"
            )
        floor = record.get("floor_percent")
        if floor is None:
            if not record.get("floor_absent_reason"):
                raise ValueError(
                    f"coverage baseline scope {name} records no floor and no floor_absent_reason; "
                    "an absent floor must say why it is absent"
                )
        elif (
            not isinstance(floor, (int, float))
            or isinstance(floor, bool)
            or not 0 <= floor <= 100
        ):
            raise ValueError(
                f"coverage baseline scope {name} records a floor outside 0-100: {floor!r}"
            )
        elif not record.get("floor_source"):
            raise ValueError(
                f"coverage baseline scope {name} records a floor with no floor_source to read it in"
            )
    return document


def classify(recorded_total: int, measured_total: int) -> str:
    """Say whether a fall is new uncovered code, a moved file, or a weakened test."""
    if measured_total > recorded_total:
        return (
            f"total units grew from {recorded_total} to {measured_total}: "
            f"{measured_total - recorded_total} unit(s) of new code arrived and the covered "
            "fraction fell, so this is uncovered code being added rather than a file moving"
        )
    if measured_total < recorded_total:
        return (
            f"total units shrank from {recorded_total} to {measured_total}: the scope lost "
            f"{recorded_total - measured_total} unit(s), so covered code was deleted or moved "
            "out. Check whether another scope gained the same units before re-recording"
        )
    return (
        f"total units unchanged at {measured_total}: units that used to execute no longer do, "
        "so a test was removed, skipped or weakened"
    )


def regressions(
    measurements: list[Measurement], document: dict[str, object], allow_unmeasured: bool
) -> list[str]:
    """Compare against the record. Improving never fails; getting worse always does."""
    failures: list[str] = []
    scopes: dict[str, dict] = document["scopes"]  # type: ignore[assignment]
    tolerance = float(document["tolerance_percentage_points"])  # type: ignore[arg-type]
    observed = {measurement.scope: measurement for measurement in measurements}

    for name in sorted(set(scopes) - set(observed)):
        failures.append(
            f"scope {name} is recorded in the coverage baseline but nothing measured it; "
            "removing a scope is a coverage regression"
        )
    for name in sorted(set(observed) - set(scopes)):
        failures.append(
            f"scope {name} is measured and not recorded in the coverage baseline; record its "
            "number there so a later regression has something to regress against"
        )
    for name in sorted(set(observed) & set(scopes)):
        measurement, record = observed[name], scopes[name]
        if not measurement.measured:
            if not allow_unmeasured:
                failures.append(
                    f"scope {name} was not measured: {measurement.note}. An unmeasured "
                    "surface is an absence of evidence, never a pass; pass "
                    "--allow-unmeasured only where the toolchain is genuinely absent"
                )
            continue
        if (
            measurement.language != record["language"]
            or measurement.metric != record["metric"]
        ):
            failures.append(
                f"scope {name} is recorded as {record['language']}/{record['metric']} and was "
                f"measured as {measurement.language}/{measurement.metric}; two different units "
                "cannot be compared"
            )
            continue
        percent = float(measurement.percent or 0.0)
        recorded = float(record["percent"])
        if percent < recorded - tolerance:
            failures.append(
                f"scope {name} regressed from {recorded:.2f}% to {percent:.2f}% "
                f"({percent - recorded:+.2f} points, tolerance {tolerance:.2f}); "
                f"{classify(int(record['total_units']), int(measurement.total_units or 0))}. "
                "A worse number requires an explicit edit to scripts/ci/measured-coverage-baseline-v1.json"
            )
        floor = record.get("floor_percent")
        if floor is not None and percent < float(floor):
            failures.append(
                f"scope {name} is at {percent:.2f}% and its floor is {float(floor):.2f}%, stated in "
                f"{record['floor_source']}; a floor is not lowered to fit a measurement"
            )
        if (
            floor is None
            and name == "go-apps-api"
            and measurement.detail.get("non_main_packages")
        ):
            failures.append(
                f"scope {name} records no floor because the module held only `main` packages, which "
                f"docs/verification/TEST_STRATEGY.md excludes. It now holds "
                f"{measurement.detail['non_main_packages']}, so the 85% and 75% Go floors have a "
                "subject and must be recorded"
            )
    return failures


def improvements(
    measurements: list[Measurement], document: dict[str, object]
) -> list[str]:
    """Scopes now ahead of the record, so the ceiling can be tightened."""
    scopes: dict[str, dict] = document["scopes"]  # type: ignore[assignment]
    tolerance = float(document["tolerance_percentage_points"])  # type: ignore[arg-type]
    ahead: list[str] = []
    for measurement in measurements:
        record = scopes.get(measurement.scope)
        if record is None or not measurement.measured:
            continue
        percent, recorded = float(measurement.percent or 0.0), float(record["percent"])
        if percent > recorded + tolerance:
            ahead.append(f"{measurement.scope} {recorded:.2f}% -> {percent:.2f}%")
    return sorted(ahead)


# -- entry point -------------------------------------------------------------------


def measure_all(root: Path, only: list[str] | None = None) -> list[Measurement]:
    measurers = {
        "python-planning-tooling": lambda: measure_python(root),
        "rust-vibeproof-core": lambda: measure_rust(root),
        "go-apps-api": lambda: measure_go(root),
    }
    selected = only or list(measurers)
    return [measurers[name]() for name in selected if name in measurers]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument(
        "--baseline", type=Path, default=BASELINE, help="recorded coverage ceiling"
    )
    parser.add_argument(
        "--scope",
        action="append",
        dest="scopes",
        help="measure only this scope; repeatable",
    )
    parser.add_argument(
        "--allow-unmeasured",
        action="store_true",
        help="do not fail when a toolchain is absent; never pass this in CI",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="record the measured numbers into the baseline",
    )
    arguments = parser.parse_args(argv)

    measurements = measure_all(ROOT, arguments.scopes)
    summary = {
        "measurements": [measurement.as_json() for measurement in measurements],
        "claim_scope": "executed-units-only",
        "claim_note": (
            "a covered unit executed; nothing here says an assertion was made about it, which "
            "is why docs/verification/TEST_STRATEGY.md states floors rather than targets"
        ),
    }

    try:
        document = load_baseline(arguments.baseline)
    except ValueError as error:
        print(json.dumps(summary, indent=2))
        print(f"invalid coverage baseline: {error}", file=sys.stderr)
        return 1

    if arguments.write:
        return write_baseline(arguments.baseline, document, measurements)

    print(json.dumps(summary, indent=2))
    failures = regressions(measurements, document, arguments.allow_unmeasured)
    for note in improvements(measurements, document):
        print(
            f"coverage improved beyond the recorded ceiling: {note}; re-record it to hold the gain"
        )
    if failures:
        for failure in failures:
            print(f"coverage regression: {failure}", file=sys.stderr)
        return 1
    print(
        "measured coverage: PASS (no scope below its recorded ceiling or its stated floor)"
    )
    return 0


def write_baseline(
    path: Path, document: dict[str, object], measurements: list[Measurement]
) -> int:
    """Re-record the measured numbers, keeping every floor and note already written.

    This is the auditable path to change the ceiling: it edits one committed file and
    leaves a diff. It refuses to record an unmeasured scope, because writing an absence
    into a ceiling is how a hole becomes invisible.
    """
    scopes: dict[str, dict] = document["scopes"]  # type: ignore[assignment]
    for measurement in measurements:
        if not measurement.measured:
            print(
                f"refusing to record unmeasured scope {measurement.scope}: {measurement.note}",
                file=sys.stderr,
            )
            return 1
        record = scopes.setdefault(measurement.scope, {})
        record["language"] = measurement.language
        record["metric"] = measurement.metric
        record["percent"] = measurement.percent
        record["covered_units"] = measurement.covered_units
        record["total_units"] = measurement.total_units
        record.setdefault("floor_percent", None)
        record.setdefault(
            "floor_absent_reason",
            "recorded by --write and not yet reconciled with a stated floor",
        )
    path.write_text(
        json.dumps(document, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(f"recorded {len(measurements)} scope(s) into {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
