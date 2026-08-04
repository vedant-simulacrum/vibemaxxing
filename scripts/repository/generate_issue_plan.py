#!/usr/bin/env python3
"""Generate a deterministic offline issue plan from stable work-unit headings."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md"
DEFAULT_OUTPUT = ROOT / "artifacts/repository/issue-plan.json"
EPIC = re.compile(r"^##\s+Epic\s+([A-Z][A-Z0-9]*)\s+[—-]\s+(.+?)\s*$")
UNIT = re.compile(r"^###\s+([A-Z][A-Z0-9]*-\d{3})\s+[—-]?\s*(.+?)\s*$")
PLANNING_HEADING = "## Current planning program"
POST_LAUNCH_HEADING = "## Post-launch tracks"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    source_text = source_bytes.decode("utf-8")
    current_epic_id: str | None = None
    current_epic_title: str | None = None
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    numbers_by_prefix: dict[str, list[int]] = defaultdict(list)

    for line_number, line in enumerate(source_text.splitlines(), start=1):
        epic_match = EPIC.match(line)
        if epic_match:
            current_epic_id = epic_match.group(1)
            current_epic_title = epic_match.group(2).strip()
            continue
        if line.strip() == PLANNING_HEADING:
            current_epic_id = "PF"
            current_epic_title = "P-1140F planning repairs"
            continue
        if line.strip() == POST_LAUNCH_HEADING:
            current_epic_id = "PL"
            current_epic_title = "post-launch tracks"
            continue

        unit_match = UNIT.match(line)
        if not unit_match:
            continue
        if current_epic_id is None or current_epic_title is None:
            raise SystemExit(f"work unit appears before an epic at line {line_number}")

        key, title = unit_match.groups()
        prefix, number_text = key.rsplit("-", 1)
        if prefix != current_epic_id:
            raise SystemExit(
                f"work-unit prefix {prefix} does not match current epic {current_epic_id} at line {line_number}"
            )
        if key in seen:
            raise SystemExit(f"duplicate work-unit key: {key}")
        seen.add(key)
        numbers_by_prefix[prefix].append(int(number_text))

        if prefix == "PF":
            phase_gate = "P-1140F-planning-repair"
            labels = ["planning-repair", "blocked-or-active"]
        elif prefix == "PL":
            phase_gate = "post-launch-explicit-approval"
            labels = ["implementation", "post-launch", "blocked"]
        else:
            phase_gate = "P-1104-explicit-implementation-approval"
            labels = ["implementation", "blocked"]
        component = slug(current_epic_title)
        records.append(
            {
                "key": key,
                "title": title.rstrip("."),
                "epic_id": current_epic_id,
                "component": component,
                "source_line": line_number,
                "phase_gate": phase_gate,
                "labels": [*labels, component],
                "authority": "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
                "artifact_maturity": "planning",
            }
        )

    if not records:
        raise SystemExit("no stable work-unit headings found")

    for prefix, numbers in numbers_by_prefix.items():
        expected = list(range(1, max(numbers) + 1))
        if numbers != expected:
            raise SystemExit(f"work units for {prefix} must be contiguous and source ordered; found {numbers}")

    output = args.output
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_version": 2,
        "source": "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "issue_count": len(records),
        "issues": records,
    }
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    try:
        display_path = output.relative_to(ROOT)
    except ValueError:
        display_path = output
    print(f"generated {len(records)} stable work-unit records at {display_path}")


if __name__ == "__main__":
    main()
