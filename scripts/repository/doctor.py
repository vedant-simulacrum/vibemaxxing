#!/usr/bin/env python3
"""Read-only authority and phase checks; deep contracts have dedicated validators."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "AGENTS.md",
    "docs/project/PROJECT.md",
    "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md",
    "docs/planning/DECISION_REGISTER.md",
    "docs/planning/TASK_CATALOG.md",
    "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md",
    "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
    "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
    ".github/workflows/planning-checks.yml",
    ".github/workflows/storyboard-visuals.yml",
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


def main() -> None:
    errors: list[str] = []

    for path in REQUIRED:
        if not (ROOT / path).is_file():
            errors.append(f"missing required authority file: {path}")
    for path in FORBIDDEN + OUT_OF_SCOPE_NATIVE_PATHS:
        if (ROOT / path).exists():
            errors.append(f"forbidden or out-of-scope path exists: {path}")

    status = (ROOT / "docs/project/STATUS.md").read_text(encoding="utf-8").lower()
    for marker in [
        "planning contract repair",
        "p-1140f semantic review is active",
        "p-1104 remains blocked",
        "product implementation remains unauthorized",
    ]:
        if marker not in status:
            errors.append(f"STATUS is missing required marker: {marker}")
    for forbidden in [
        "p-1104 awaits explicit user authorization",
        "all planning prerequisites are complete",
        "implementation may begin",
    ]:
        if forbidden in status:
            errors.append(f"STATUS contains premature implementation-readiness text: {forbidden}")

    tasks = (ROOT / "docs/planning/TASK_CATALOG.md").read_text(encoding="utf-8").lower()
    for marker in [
        "### p-1140e",
        "status: `complete-planning`",
        "### p-1140f",
        "status: `in-progress-planning`",
        "p-1104 | enter implementation phase | blocked-approval",
    ]:
        if marker not in tasks:
            errors.append(f"TASK_CATALOG is missing required gate marker: {marker}")

    structural = (ROOT / "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md").read_text(encoding="utf-8").lower()
    for marker in [
        "structural p0 open: 0",
        "structural p1 open: 0",
        "does not establish",
        "p-1140f",
    ]:
        if marker not in structural:
            errors.append(f"P-1140E audit is missing claim-boundary marker: {marker}")

    semantic = (ROOT / "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md").read_text(encoding="utf-8").lower()
    for marker in [
        "semantic p1 open: 4",
        "sr-001",
        "sr-002",
        "sr-003",
        "sr-004",
        "p-1104: blocked",
    ]:
        if marker not in semantic:
            errors.append(f"P-1140F review is missing required marker: {marker}")

    handoff = (ROOT / "docs/implementation/IMPLEMENTATION_HANDOFF.md").read_text(encoding="utf-8").lower()
    for marker in [
        "consolidated but inactive",
        "p-1140f semantic review is open",
        "p-1104 is blocked",
        "do not begin product implementation",
    ]:
        if marker not in handoff:
            errors.append(f"implementation handoff is missing required boundary: {marker}")

    storyboard = (ROOT / ".github/workflows/storyboard-visuals.yml").read_text(encoding="utf-8")
    if re.search(r"(?m)^\s*push:\s*$", storyboard):
        errors.append("storyboard workflow must not run on push under ADR-014")
    if "apps/web/**" in storyboard:
        errors.append("storyboard workflow must not include apps/web/** under ADR-014")
    if "${{ secrets." in storyboard:
        errors.append("storyboard workflow must not access secrets under ADR-014")
    for marker in [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "VIBEMAXXING_FIXTURE_POLICY: synthetic-only",
        "--bind 127.0.0.1",
        "VIBEMAXXING_ARTIFACT_MATURITY: runnable-prototype",
    ]:
        if marker not in storyboard:
            errors.append(f"storyboard workflow is missing ADR-014 marker: {marker}")

    if errors:
        print("Repository doctor: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    print("Repository doctor: PASS")
    print("phase=planning-contract-repair active=P-1140F implementation=P-1104-blocked")


if __name__ == "__main__":
    main()
