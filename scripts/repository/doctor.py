#!/usr/bin/env python3
"""Read-only repository authority and phase checks.

Deep contract, schema, protocol, API, SQL and fixture semantics are owned by
specialized validators. This doctor intentionally checks only stable repository
boundaries and must not couple success to prose formatting.
"""
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
    "apps/android",
    "apps/ios",
    "apps/ipados",
    "apps/chromeos",
    "packages/android",
    "packages/ios",
    "packages/ipados",
    "packages/chromeos",
]


def require_tokens(path: str, tokens: list[str], errors: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8").lower()
    for token in tokens:
        if token.lower() not in text:
            errors.append(f"{path} is missing required authority token: {token}")


def main() -> None:
    errors: list[str] = []

    for path in REQUIRED:
        if not (ROOT / path).is_file():
            errors.append(f"missing required authority file: {path}")

    for path in FORBIDDEN + OUT_OF_SCOPE_NATIVE_PATHS:
        if (ROOT / path).exists():
            errors.append(f"forbidden or out-of-scope path exists: {path}")

    if not errors:
        require_tokens(
            "docs/project/STATUS.md",
            ["planning contract repair", "P-1140F", "P-1104", "blocked", "implementation remains unauthorized"],
            errors,
        )
        require_tokens(
            "docs/planning/TASK_CATALOG.md",
            ["P-1140E", "complete-planning", "P-1140F", "in-progress-planning", "P-1104", "blocked-approval"],
            errors,
        )
        require_tokens(
            "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md",
            ["structural P0 open: 0", "structural P1 open: 0", "semantic", "P-1140F"],
            errors,
        )
        require_tokens(
            "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md",
            ["semantic P1 open: 4", "SR-001", "SR-002", "SR-003", "SR-004", "P-1104: blocked"],
            errors,
        )
        require_tokens(
            "docs/implementation/IMPLEMENTATION_HANDOFF.md",
            ["inactive", "P-1140F", "P-1104", "blocked"],
            errors,
        )

        storyboard = (ROOT / ".github/workflows/storyboard-visuals.yml").read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*push:\s*$", storyboard):
            errors.append("storyboard workflow must not run on push under ADR-014")
        if "apps/web/**" in storyboard:
            errors.append("storyboard workflow must not include apps/web/** under ADR-014")
        if "${{ secrets." in storyboard:
            errors.append("storyboard workflow must not access secrets under ADR-014")
        for marker in [
            "contents: read",
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
