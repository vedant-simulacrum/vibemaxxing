#!/usr/bin/env python3
"""Generate a deterministic, offline GitHub issue plan from the work breakdown."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md"
OUTPUT = ROOT / "artifacts/repository/issue-plan.json"
ITEM = re.compile(r"^(\d+)\.\s+(.+?)\s*$")
SECTION = re.compile(r"^##\s+(.+?)\s*$")


def main() -> None:
    component = "unspecified"
    records: list[dict[str, object]] = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        section_match = SECTION.match(line)
        if section_match:
            component = section_match.group(1).strip().lower().replace(" ", "-")
            continue
        item_match = ITEM.match(line)
        if not item_match:
            continue
        number = int(item_match.group(1))
        records.append(
            {
                "key": f"IMP-{number:03d}",
                "title": item_match.group(2).rstrip("."),
                "component": component,
                "phase_gate": "explicit-implementation-approval",
                "labels": ["implementation", component, "blocked"],
                "authority": "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
            }
        )

    expected = list(range(1, 53))
    actual = [int(record["key"].split("-")[1]) for record in records]
    if actual != expected:
        raise SystemExit(f"expected work units 1..52, found {actual}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"schema_version": 1, "issues": records}, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(records)} issue records at {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
