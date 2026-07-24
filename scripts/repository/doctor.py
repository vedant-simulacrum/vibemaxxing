#!/usr/bin/env python3
"""Read-only repository gate checks; deep schemas and fixtures have dedicated validators."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "AGENTS.md",
    "README.md",
    "LICENSES.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".github/CODEOWNERS",
    ".github/workflows/planning-checks.yml",
    ".github/workflows/storyboard-visuals.yml",
    "docs/project/PROJECT.md",
    "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md",
    "docs/planning/DECISION_REGISTER.md",
    "docs/planning/TASK_CATALOG.md",
    "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md",
    "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
    "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
    "packages/schemas/state-machine-registry-v1.json",
    "packages/schemas/platform-profile-registry-v1.json",
    "packages/schemas/openapi-v1.yaml",
    "packages/schemas/planning-schema.sql",
    "conformance/p1140e/validation-matrix-v1.json",
    "scripts/repository/validate_p1140e_contracts.py",
]

FORBIDDEN = [
    "PROJECT_CONTEXT.md",
    "PROJECT_INSTRUCTIONS.md",
    "CURRENT_STATUS.md",
    "MODEL_OPERATING_MANUAL.md",
    "IMPLEMENTATION_ROADMAP.md",
    "RESEARCH_AND_EVIDENCE_BACKLOG.md",
    "START_HERE_PROMPT.md",
    "CHATGPT_WORK_PROJECT_PROMPT.md",
    "docs/implementation/BUILD_PLAN.md",
    "docs/implementation/TECH_STACK.md",
    "docs/planning/SPECIFICATION_INDEX.md",
    "docs/planning/DEPENDENCY_MAP.md",
    "docs/planning/PLANNING_AUDIT.md",
]

OUT_OF_SCOPE_NATIVE_PATHS = [
    "apps/android", "apps/ios", "apps/ipados", "apps/chromeos",
    "packages/android", "packages/ios", "packages/ipados", "packages/chromeos",
]

ACTION_REF = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")
FULL_SHA_ACTION = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def parse_tasks(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    active: str | None = None
    for line in text.splitlines():
        heading = re.match(r"^###\s+(P-\d{3,4}[A-Z]?)\b", line)
        if heading:
            active = heading.group(1)
            continue
        if active and line.startswith("Status: `"):
            result[active] = line.removeprefix("Status: `").split("`", 1)[0]
            active = None
            continue
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and re.fullmatch(r"P-\d{3,4}[A-Z]?", cells[0]):
                result[cells[0]] = cells[2]
    return result


def main() -> None:
    errors: list[str] = []

    for path in REQUIRED:
        if not (ROOT / path).is_file():
            errors.append(f"missing required file: {path}")
    for path in FORBIDDEN + OUT_OF_SCOPE_NATIVE_PATHS:
        if (ROOT / path).exists():
            errors.append(f"forbidden or out-of-scope path exists: {path}")

    for path in ROOT.rglob("*.json"):
        if any(part in {".git", "node_modules", "target", "dist", "build"} for part in path.parts):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON: {path.relative_to(ROOT)}: {exc}")

    tasks = parse_tasks((ROOT / "docs/planning/TASK_CATALOG.md").read_text(encoding="utf-8"))
    expected = {
        "P-1140A": "complete-planning",
        "P-1140B": "complete-planning",
        "P-1140C": "complete-planning",
        "P-1140D": "complete-planning",
        "P-1140E": "complete-planning",
        "P-1140F": "in-progress-planning",
        "P-1104": "blocked-approval",
        "P-1131": "blocked-launch-evidence",
    }
    for task, status in expected.items():
        if tasks.get(task) != status:
            errors.append(f"task {task} must be {status}, found {tasks.get(task)!r}")

    status = (ROOT / "docs/project/STATUS.md").read_text(encoding="utf-8").lower()
    for marker in [
        "planning contract repair",
        "p-1140f semantic review is active",
        "p-1104 remains blocked",
        "product implementation remains unauthorized",
    ]:
        if marker not in status:
            errors.append(f"STATUS is missing required marker: {marker}")
    if "all planning prerequisites are complete" in status or "p-1104 awaits explicit user authorization" in status:
        errors.append("STATUS prematurely presents implementation as approval-ready")

    structural = (ROOT / "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md").read_text(encoding="utf-8").lower()
    for marker in ["structural p0 open: 0", "structural p1 open: 0", "does not establish", "p-1140f"]:
        if marker not in structural:
            errors.append(f"P-1140E structural audit is missing: {marker}")

    semantic = (ROOT / "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md").read_text(encoding="utf-8").lower()
    for marker in ["semantic p1 open: 4", "sr-001", "sr-002", "sr-003", "sr-004", "p-1104: blocked"]:
        if marker not in semantic:
            errors.append(f"P-1140F semantic review is missing: {marker}")

    for workflow in [".github/workflows/planning-checks.yml", ".github/workflows/storyboard-visuals.yml"]:
        for number, line in enumerate((ROOT / workflow).read_text(encoding="utf-8").splitlines(), start=1):
            match = ACTION_REF.match(line)
            if match and not match.group(1).startswith("./") and not FULL_SHA_ACTION.fullmatch(match.group(1)):
                errors.append(f"workflow action is not pinned to a full SHA: {workflow}:{number}")

    storyboard = (ROOT / ".github/workflows/storyboard-visuals.yml").read_text(encoding="utf-8")
    for marker in [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "VIBEMAXXING_FIXTURE_POLICY: synthetic-only",
        "--bind 127.0.0.1",
        "VIBEMAXXING_ARTIFACT_MATURITY: runnable-prototype",
    ]:
        if marker not in storyboard:
            errors.append(f"storyboard workflow is missing ADR-014 marker: {marker}")
    if re.search(r"(?m)^\s*push:\s*$", storyboard) or "apps/web/**" in storyboard or "${{ secrets." in storyboard:
        errors.append("storyboard workflow violates the ADR-014 event/path/secret boundary")
    retention = re.search(r"(?m)^\s*retention-days:\s*(\d+)\s*$", storyboard)
    if not retention or int(retention.group(1)) > 30:
        errors.append("storyboard artifact retention must be declared at no more than 30 days")

    if errors:
        print("Repository doctor: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    print("Repository doctor: PASS")
    print("phase=planning-contract-repair active=P-1140F implementation=P-1104-blocked")


if __name__ == "__main__":
    main()
