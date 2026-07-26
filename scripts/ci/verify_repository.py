#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Check:
    name: str
    status: str
    command: list[str] | None
    returncode: int | None = None


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
        checks.append(Check("go", "not_applicable", None))
    if (root / "Cargo.toml").is_file():
        checks.extend([
            Check("rust-fmt", "pending", ["cargo", "fmt", "--all", "--check"]),
            Check("rust-clippy", "pending", ["cargo", "clippy", "--workspace", "--all-targets", "--all-features", "--", "-D", "warnings"]),
            Check("rust-test", "pending", ["cargo", "test", "--workspace", "--all-features"]),
        ])
    else:
        checks.append(Check("rust", "not_applicable", None))
    has_node_workspace = (root / "package.json").is_file() and any((root / lockfile).is_file() for lockfile in ("package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock"))
    checks.append(Check("node", "pending", None) if has_node_workspace else Check("node", "not_applicable", None))
    return checks


def run_check(check: Check, root: Path) -> None:
    if check.name == "evaluator-all-suites":
        assert check.command is not None
        listed = subprocess.run(check.command, cwd=root, capture_output=True, text=True, check=False)
        suite_commands = [[sys.executable, str(root / "scripts" / "ci" / "run_evals.py"), "--suite", suite] for suite in listed.stdout.splitlines()]
        returncodes = [listed.returncode, *(subprocess.run(command, cwd=root, capture_output=True, text=True, check=False).returncode for command in suite_commands)]
        check.returncode = next((returncode for returncode in returncodes if returncode != 0), 0)
    elif check.name == "node":
        commands = [["npm", "ci"], ["npm", "run", "lint", "--if-present"], ["npm", "run", "typecheck", "--if-present"], ["npm", "test", "--if-present"], ["npm", "run", "build", "--if-present"]]
        check.returncode = 0
        for command in commands:
            check.returncode = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False).returncode
            if check.returncode != 0:
                break
    else:
        assert check.command is not None
        working_directory = root / "apps" / "api" if check.name.startswith("go-") else root
        check.returncode = subprocess.run(check.command, cwd=working_directory, capture_output=True, text=True, check=False).returncode
    check.status = "pass" if check.returncode == 0 else "fail"


def main() -> int:
    checks = planned_checks(ROOT)
    for check in checks:
        if check.status == "pending":
            run_check(check, ROOT)
    summary = {"checks": [{"name": check.name, "status": check.status, "command": check.command, "returncode": check.returncode} for check in checks]}
    print(json.dumps(summary, indent=2))
    return 0 if all(check.status in {"pass", "not_applicable"} for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
