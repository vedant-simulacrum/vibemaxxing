#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SUITES = {
    "protocol-conformance": (
        ((["cargo", "test", "-p", "vibeproof-core", "--test", "vectors"], ROOT), (["go", "test", "./cmd/api"], ROOT / "apps" / "api")),
        "evals/fixtures/protocol-conformance.json",
        ("canonical-vectors", "rust-go-acceptance-parity", "invalid-vectors"),
    ),
    "token-accounting-conformance": (
        ((["cargo", "test", "-p", "vibeproof-core", "--test", "accounting_pricing"], ROOT),),
        "evals/fixtures/token-accounting-conformance.json",
        ("deterministic-normalization",),
    ),
    "ranking-accounting": (
        ((["cargo", "test", "-p", "vibeproof-core", "--test", "accounting_pricing"], ROOT),),
        "evals/fixtures/ranking-accounting.json",
        ("imported-exclusion-and-dedupe",),
    ),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=sorted(SUITES))
    parser.add_argument("--commit", required=True)
    arguments = parser.parse_args()
    commands, manifest_path, cases = SUITES[arguments.suite]
    if arguments.commit != current_commit():
        return 2
    manifest_bytes = (ROOT / manifest_path).read_bytes()
    manifest = json.loads(manifest_bytes)
    started_at = now()
    returncode = 0
    for command, cwd in commands:
        completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            if completed.stdout:
                print(completed.stdout, end="", file=sys.stderr)
            if completed.stderr:
                print(completed.stderr, end="", file=sys.stderr)
            returncode = completed.returncode
            break
    fixtures = [{"id": fixture["id"], "sha256": fixture["sha256"]} for fixture in manifest["fixtures"]]
    evidence = {
        "version": "1",
        "suite": arguments.suite,
        "commit": arguments.commit,
        "status": "pass" if returncode == 0 else "fail",
        "cases": [{"id": case, "status": "pass" if returncode == 0 else "fail"} for case in cases],
        "fixtures": {"manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(), "fixtures": fixtures},
        "started_at": started_at,
        "finished_at": now(),
    }
    print(json.dumps(evidence))
    return returncode


def current_commit() -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else "local"


if __name__ == "__main__":
    raise SystemExit(main())
