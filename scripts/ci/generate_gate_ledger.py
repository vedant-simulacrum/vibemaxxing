#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import TypeAlias

from eval_validation import VERSION
from run_evals import ROOT, current_commit, parse_registry


JsonValue: TypeAlias = str | None | list["JsonValue"] | dict[str, "JsonValue"]


def generated_timestamp(value: str | None) -> str:
    return value if value is not None else datetime.now(timezone.utc).isoformat()


def result_link(results: Path, suite_id: str, commit: str) -> str | None:
    result_file = results / suite_id / commit / "result.json"
    try:
        result = json.loads(result_file.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(result, dict) or result.get("suite") != suite_id or result.get("commit") != commit:
        return None
    return str(Path("artifacts/evals") / suite_id / commit / "result.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=ROOT / "evals/suites/suites.yaml")
    parser.add_argument("--out", type=Path, default=Path("artifacts/evals/gate-ledger.json"))
    parser.add_argument("--results", type=Path, default=ROOT / "artifacts/evals")
    parser.add_argument("--commit", default=current_commit())
    parser.add_argument("--generated-at")
    arguments = parser.parse_args()
    try:
        suites = parse_registry(arguments.registry)
        entries: list[dict[str, JsonValue]] = []
        for suite in suites.values():
            entries.append({
                "id": suite["id"],
                "owner": suite["owner"],
                "blocking_milestone": suite["blocking_milestone"],
                "status": suite["status"],
                "reason": suite["reason"],
                "result_path": result_link(arguments.results, str(suite["id"]), arguments.commit),
            })
    except (OSError, ValueError) as error:
        print(f"invalid eval registry: {error}", file=sys.stderr)
        return 2
    ledger: dict[str, JsonValue] = {
        "registry_version": VERSION,
        "commit": arguments.commit,
        "generated_at": generated_timestamp(arguments.generated_at),
        "suites": entries,
    }
    output = arguments.out if arguments.out.is_absolute() else ROOT / arguments.out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(ledger, indent=2) + "\n")
    print(json.dumps(ledger, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
