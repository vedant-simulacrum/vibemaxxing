#!/usr/bin/env python3
"""Generate the decision register and task catalog from their JSON sources.

Every planning gate in this repository lived in a Markdown table that validators
reached by substring matching. `validate_p1140f_authority.py` greps prose for a
count; `doctor.py` asserts that literal strings appear somewhere in a document.
That is why the phase gate could once only be moved by editing its own validator,
and why nothing enforced that a decision's status, its reopen condition and the
artifact it governs stayed consistent.

`conformance/p1140f/*.json` is the pattern that works here: validators read
structure. So the structure moves to JSON and the Markdown becomes output.

The register is 290 rows running to D-607. It is a table with four columns and no
prose between rows, so the whole table is one generated block; the preamble stays
hand-written, including the `Allowed statuses:` line that
`validate_planning_artifacts.py` reads to derive the permitted set — that line is
the schema stated in prose, and generating it from the same JSON it constrains
would make it agree with itself by construction.

The catalog's program and step blocks are generated the same way. Their `Status:`
lines are what `validate_repair_task_binding.py` parses to decide whether a step
may claim completion, so the rendered shape is load-bearing and is asserted by
tests rather than left to look right.

`validate_work_unit_status.py` is the precedent: a marker-delimited block, rendered
on every run, with drift failing the build.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "conformance" / "planning"
DECISIONS_JSON = PLANNING / "decisions-v1.json"
TASKS_JSON = PLANNING / "tasks-v1.json"
REGISTER_MD = ROOT / "docs" / "planning" / "DECISION_REGISTER.md"
CATALOG_MD = ROOT / "docs" / "planning" / "TASK_CATALOG.md"

TRACEABILITY_JSON = PLANNING / "decision-traceability-v1.json"
TRACEABILITY_DIR = ROOT / "docs" / "planning" / "decision-traceability"

# The first four groups keep the boundaries the P-1140E-era files already used, so
# those filenames and their contents do not move.
LEGACY_GROUPS = (
    ("D-001", "D-020"),
    ("D-021", "D-040"),
    ("D-041", "D-061"),
    ("D-062", "D-069"),
)
# The tail is grouped on a fixed numeric grid, not by row count. Naming a file after
# the first and last id it happens to hold means adding one decision renames the last
# file and leaves the old name behind — which is exactly what adding D-609 did. A grid
# keeps every filename stable as the register grows, because the range is a property
# of the numbering rather than of the contents.
TAIL_GRID = 100

DECISIONS_BEGIN = "<!-- generated: decision-register -->"
DECISIONS_END = "<!-- end generated: decision-register -->"
TASKS_BEGIN = "<!-- generated: task-catalog -->"
TASKS_END = "<!-- end generated: task-catalog -->"


class Failure(Exception):
    """A document cannot be generated from its source."""


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_decisions(source: dict) -> str:
    """The register table, header row included."""
    lines = [
        DECISIONS_BEGIN,
        "",
        "| ID | Decision | Status | Validation or reopen condition |",
        "|---|---|---|---|",
    ]
    for row in source["decisions"]:
        # A literal pipe inside a cell would silently shift every column to its
        # right, which is the defect `validate_decision_register` exists to catch.
        # Refuse to emit one rather than emit a table that parses wrongly.
        for field in ("id", "decision", "status", "validation_or_reopen"):
            if "|" in row[field]:
                raise Failure(
                    f"{row['id']}: {field} contains a pipe, which would shift every "
                    "column to its right when the table is parsed back"
                )
        lines.append(
            f"| {row['id']} | {row['decision']} | {row['status']} | "
            f"{row['validation_or_reopen']} |"
        )
    lines += ["", DECISIONS_END]
    return "\n".join(lines)


def render_tasks(source: dict) -> str:
    """The program groups and the P-1140F step blocks.

    `Status:` is emitted on its own line in backticks because
    `validate_repair_task_binding.py` finds it with `^Status:\\s*(.+)$` and strips
    the backticks. Changing this shape silently unbinds every step from its units.
    """
    lines = [TASKS_BEGIN, ""]
    for program in source["programs"]:
        lines += [
            f"### {program['id']} — {program['title']}",
            "",
            f"Status: `{program['status']}`",
            "",
            program["body"],
            "",
        ]
    # The steps are nested under P-1140F, so its body runs up to the first `####`
    # and already carries the sentence introducing them. An earlier attempt lifted
    # that sentence into its own field and rendered it separately, which duplicated
    # every step block — the program-body pattern stopped at `###` and `##` but not
    # at `####`, so P-1140F had swallowed the steps too.
    for step in source["steps"]:
        lines += [
            f"#### {step['id']} — {step['title']}",
            "",
            f"Status: `{step['status']}`",
            "",
            step["body"],
            "",
        ]
    lines.append(TASKS_END)
    return "\n".join(lines)


def splice(text: str, begin: str, end: str, block: str, name: str) -> str:
    start = text.find(begin)
    stop = text.find(end)
    if start == -1 or stop == -1:
        raise Failure(f"{name} has no generated block; add {begin} and {end}")
    return text[:start] + block + text[stop + len(end) :]


def rendered(path: Path, begin: str, end: str, block: str) -> str:
    return splice(path.read_text(encoding="utf-8"), begin, end, block, path.name)


def traceability_groups(rows: list[dict]) -> list[list[dict]]:
    """Split the rows into the files they are written to."""
    by_id = {row["id"]: row for row in rows}
    groups: list[list[dict]] = []
    placed: set[str] = set()
    for first, last in LEGACY_GROUPS:
        group = [row for row in rows if first <= row["id"] <= last]
        if not group:
            raise Failure(f"no traceability rows in the legacy group {first}..{last}")
        groups.append(group)
        placed |= {row["id"] for row in group}
    tail = [row for row in rows if row["id"] not in placed]
    buckets: dict[int, list[dict]] = {}
    for row in tail:
        buckets.setdefault(int(row["id"].split("-")[1]) // TAIL_GRID, []).append(row)
    for bucket in sorted(buckets):
        groups.append(buckets[bucket])
    if sum(len(group) for group in groups) != len(by_id):
        raise Failure("traceability grouping lost or duplicated a row")
    return groups


def render_traceability_group(group: list[dict]) -> str:
    """One traceability file.

    A row that is not implementation-bearing still appears, carrying the reason it
    is not. Leaving it out would make the table's coverage unreadable: an absent row
    and an excluded one would look the same, and only one of them is a defect.
    """
    lines = [
        f"# Decisions {group[0]['id']} through {group[-1]['id']}",
        "",
        "<!-- generated: decision-traceability -->",
        "",
        "| ID | Normative owner | Implementation owner/work units | Machine/state ownership | Platform scope | Required executable evidence |",
        "|---|---|---|---|---|---|",
    ]
    for row in group:
        if row["implementation_bearing"]:
            cells = [
                row["normative_owner"],
                row["implementation_owner"],
                row["machine_or_state_ownership"],
                row["platform_scope"],
                row["required_executable_evidence"],
            ]
        else:
            cells = [
                f"Not implementation-bearing: {row['reason']}",
                "—",
                "—",
                "None",
                "—",
            ]
        for cell in cells:
            if "|" in cell:
                raise Failure(
                    f"{row['id']}: a cell contains a pipe, which would shift every "
                    "column to its right"
                )
        lines.append("| " + " | ".join([row["id"], *cells]) + " |")
    lines += ["", "<!-- end generated: decision-traceability -->", ""]
    return "\n".join(lines)


def traceability_documents() -> list[tuple[Path, str]]:
    rows = load(TRACEABILITY_JSON)["rows"]
    written = []
    for index, group in enumerate(traceability_groups(rows)):
        if index < len(LEGACY_GROUPS):
            name = f"{LEGACY_GROUPS[index][0]}-{LEGACY_GROUPS[index][1]}.md"
        else:
            bucket = int(group[0]["id"].split("-")[1]) // TAIL_GRID
            # The legacy files already hold D-001..D-069, so the first grid bucket
            # starts where they stop. Naming it from the bucket's own lower bound
            # would advertise rows the file does not contain.
            low = max(bucket * TAIL_GRID, 70)
            name = f"D-{low:03d}-D-{bucket * TAIL_GRID + TAIL_GRID - 1:03d}.md"
        written.append((TRACEABILITY_DIR / name, render_traceability_group(group)))
    return written


def orphaned_shards() -> list[Path]:
    """Traceability files on disk that no group would produce.

    Grouping by row count named each file after the ids it happened to hold, so
    adding D-609 renamed the final file and left the old one behind. The grid fixes
    the naming; this makes a leftover fail rather than sit there looking authoritative.
    """
    expected = {path.name for path, _ in traceability_documents()}
    return sorted(
        path for path in TRACEABILITY_DIR.glob("D-*.md") if path.name not in expected
    )


def check_step_block_is_bounded(catalog: str) -> None:
    """The last step's body must be terminated by a heading, not by the marker.

    `validate_repair_task_binding.STEP` bounds a step with `(?=\\n#### |\\n## |\\Z)`.
    The final step therefore ends only because `## P-1140F acceptance` follows the
    generated block in the hand-written half of the document. Nothing declared that,
    so moving or renaming that section would silently extend the last step's body to
    swallow the end marker — and a step's body is where its `Status:` is read from.

    This makes the coupling explicit instead of load-bearing and invisible.
    """
    tail = catalog.split(TASKS_END, 1)[-1].lstrip("\n")
    if not tail.startswith("## "):
        raise Failure(
            "the generated task block must be followed by a `## ` heading, because "
            "validate_repair_task_binding bounds the last step on one; found "
            f"{tail.splitlines()[0][:60]!r}"
        )


def documents() -> list[tuple[Path, str]]:
    """Each generated document paired with the text it should hold."""
    decisions = render_decisions(load(DECISIONS_JSON))
    tasks = render_tasks(load(TASKS_JSON))
    catalog = rendered(CATALOG_MD, TASKS_BEGIN, TASKS_END, tasks)
    check_step_block_is_bounded(catalog)
    return [
        (REGISTER_MD, rendered(REGISTER_MD, DECISIONS_BEGIN, DECISIONS_END, decisions)),
        (CATALOG_MD, catalog),
        *traceability_documents(),
    ]


def stale() -> list[Path]:
    return [
        path
        for path, text in documents()
        if not path.is_file() or path.read_text(encoding="utf-8") != text
    ]


def untraced() -> list[str]:
    """Decisions with no traceability row.

    P-1140E froze its matrix at `range(1, 70)` and delegated the rest to a validator
    that never references a `D-` identifier, so every decision from D-070 onward had
    no row at all. This is the check PF-063 exists to add: it runs over the register
    rather than over a fixed list, so a new decision cannot merge without a row.
    """
    decisions = [row["id"] for row in load(DECISIONS_JSON)["decisions"]]
    traced = {row["id"] for row in load(TRACEABILITY_JSON)["rows"]}
    return [identifier for identifier in decisions if identifier not in traced]


def orphaned() -> list[str]:
    """Traceability rows for decisions the register does not contain."""
    decisions = {row["id"] for row in load(DECISIONS_JSON)["decisions"]}
    return [
        row["id"]
        for row in load(TRACEABILITY_JSON)["rows"]
        if row["id"] not in decisions
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed documents already match, and change nothing",
    )
    arguments = parser.parse_args()

    if arguments.check:
        drifted = stale()
        if drifted:
            print(
                "planning documents are stale: "
                + ", ".join(path.name for path in drifted)
                + "; run scripts/repository/generate_planning_docs.py",
                file=sys.stderr,
            )
            return 1
        source = load(DECISIONS_JSON)
        tasks = load(TASKS_JSON)
        print(
            f"planning documents: generated "
            f"({len(source['decisions'])} decisions, {len(tasks['programs'])} programs, "
            f"{len(tasks['steps'])} steps)"
        )
        return 0

    for path, text in documents():
        path.write_text(text, encoding="utf-8")
    print(
        "regenerated DECISION_REGISTER.md and TASK_CATALOG.md from conformance/planning/"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Failure as failure:
        print(f"planning document generation: FAIL — {failure}", file=sys.stderr)
        raise SystemExit(1)
