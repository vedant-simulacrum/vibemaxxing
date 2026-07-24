#!/usr/bin/env python3
"""Read-only repository consistency checks for the planning-contract-repair phase."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
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
    "docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md",
    "docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md",
    "docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md",
    "docs/planning/DECISION_REGISTER.md",
    "docs/planning/TASK_CATALOG.md",
    "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md",
    "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md",
    "docs/planning/decision-traceability/README.md",
    "docs/planning/decision-traceability/D-001-D-020.md",
    "docs/planning/decision-traceability/D-021-D-040.md",
    "docs/planning/decision-traceability/D-041-D-061.md",
    "docs/planning/decision-traceability/D-062-D-069.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
    "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
    "docs/implementation/REPOSITORY_LAYOUT.md",
    "docs/implementation/ISSUE_GENERATION.md",
    "docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md",
    "docs/architecture/VIBEPROOF_V1_PROTOCOL.md",
    "packages/schemas/vibeproof-claim-v1.cddl",
    "packages/schemas/state-machine-registry-v1.schema.json",
    "packages/schemas/state-machine-registry-v1.json",
    "packages/schemas/platform-profile-registry-v1.schema.json",
    "packages/schemas/platform-profile-registry-v1.json",
    "packages/schemas/openapi-v1.yaml",
    "packages/schemas/planning-schema.sql",
    "packages/schemas/reason-codes-v1.json",
    "packages/schemas/policy-defaults-v1.json",
    "conformance/p1140e/validation-matrix-v1.schema.json",
    "conformance/p1140e/validation-matrix-v1.json",
    "conformance/p1140e/state-machine-fixtures-v1.json",
    "conformance/p1140e/sql-race-plans-v1.json",
    "conformance/p1140e/platform-validation-plan-v1.json",
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

TRACE_FILES = [
    "docs/planning/decision-traceability/D-001-D-020.md",
    "docs/planning/decision-traceability/D-021-D-040.md",
    "docs/planning/decision-traceability/D-041-D-061.md",
    "docs/planning/decision-traceability/D-062-D-069.md",
]

CORE_DOCS = [
    "AGENTS.md",
    "README.md",
    "docs/project/PROJECT.md",
    "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md",
    "docs/planning/TASK_CATALOG.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
]

PATH_TOKEN = re.compile(r"`((?:\.?\.?/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)`")
DECISION = re.compile(r"\bD-\d{3}\b")
TASK = re.compile(r"\bP-\d{3,4}[A-Z]?\b")
TRACE_ROW = re.compile(r"^\|\s*(D-\d{3})\s*\|")
ACTION_REF = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")
FULL_SHA_ACTION = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def parse_decisions(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    allowed = {"accepted", "provisional", "research-required", "deferred", "rejected", "superseded"}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"D-\d{3}", cells[0]) and cells[2] in allowed:
            result[cells[0]] = cells[2]
    return result


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


def validate_action_pins(path: str, errors: list[str]) -> None:
    for number, line in enumerate((ROOT / path).read_text(encoding="utf-8").splitlines(), start=1):
        match = ACTION_REF.match(line)
        if match and not match.group(1).startswith("./") and not FULL_SHA_ACTION.fullmatch(match.group(1)):
            errors.append(f"workflow action is not pinned to a full commit SHA: {path}:{number}: {match.group(1)}")


def validate_storyboard(errors: list[str]) -> None:
    path = ROOT / ".github/workflows/storyboard-visuals.yml"
    text = path.read_text(encoding="utf-8")
    required = [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "VIBEMAXXING_FIXTURE_POLICY: synthetic-only",
        "--bind 127.0.0.1",
        "scripts/ui/playwright-runtime/package-lock.json",
        "VIBEMAXXING_ARTIFACT_MATURITY: runnable-prototype",
        "workflow_dispatch:",
        "pull_request:",
    ]
    for marker in required:
        if marker not in text:
            errors.append(f"storyboard workflow is missing ADR-014 marker: {marker}")
    if re.search(r"(?m)^\s*push:\s*$", text):
        errors.append("storyboard workflow must not run on push under ADR-014")
    if "apps/web/**" in text:
        errors.append("storyboard workflow must not include apps/web/** under ADR-014")
    if "${{ secrets." in text:
        errors.append("storyboard workflow must not access secrets under ADR-014")
    match = re.search(r"(?m)^\s*retention-days:\s*(\d+)\s*$", text)
    if not match or int(match.group(1)) > 30:
        errors.append("storyboard workflow must declare artifact retention of at most 30 days")


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

    for doc in CORE_DOCS:
        file = ROOT / doc
        if not file.is_file():
            continue
        for token in PATH_TOKEN.findall(file.read_text(encoding="utf-8")):
            token = token.removeprefix("./")
            if token.startswith("../") or "{" in token or token.endswith("/"):
                continue
            if Path(token).suffix and not (ROOT / token).exists():
                errors.append(f"broken canonical reference: {doc} -> {token}")

    decisions = parse_decisions((ROOT / "docs/planning/DECISION_REGISTER.md").read_text(encoding="utf-8"))
    tasks = parse_tasks((ROOT / "docs/planning/TASK_CATALOG.md").read_text(encoding="utf-8"))
    expected_decisions = {f"D-{n:03d}" for n in range(1, 70)}
    if set(decisions) != expected_decisions:
        errors.append("decision register must contain exactly D-001..D-069")

    expected_decision_status = {
        "D-045": "superseded",
        "D-046": "provisional",
        "D-049": "accepted",
        "D-052": "accepted",
        **{f"D-{n:03d}": "accepted" for n in range(61, 70)},
    }
    for decision, expected in expected_decision_status.items():
        if decisions.get(decision) != expected:
            errors.append(f"decision {decision} must be {expected}, found {decisions.get(decision)!r}")

    trace_ids: list[str] = []
    for path in TRACE_FILES:
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            match = TRACE_ROW.match(line)
            if match:
                trace_ids.append(match.group(1))
    counts = Counter(trace_ids)
    if set(counts) != expected_decisions or any(count != 1 for count in counts.values()):
        errors.append("decision traceability must contain each D-001..D-069 exactly once")

    expected_tasks = {
        "P-1140A": "complete-planning",
        "P-1140B": "complete-planning",
        "P-1140C": "complete-planning",
        "P-1140D": "complete-planning",
        "P-1140E": "complete-planning",
        "P-1140F": "in-progress-planning",
        "P-1104": "blocked-approval",
        "P-1131": "blocked-launch-evidence",
    }
    for task, expected in expected_tasks.items():
        if tasks.get(task) != expected:
            errors.append(f"task {task} must be {expected}, found {tasks.get(task)!r}")

    status = (ROOT / "docs/project/STATUS.md").read_text(encoding="utf-8").lower()
    for marker in [
        "planning contract repair",
        "p-1140f semantic review is active",
        "p-1104 remains blocked",
        "product implementation remains unauthorized",
    ]:
        if marker not in status:
            errors.append(f"status is missing required gate marker: {marker}")
    if "p-1104 awaits explicit user authorization" in status or "all planning prerequisites are complete" in status:
        errors.append("status prematurely presents P-1104 as approval-ready")

    audit = (ROOT / "docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md").read_text(encoding="utf-8").lower()
    if "structural p0 open: 0" not in audit or "structural p1 open: 0" not in audit:
        errors.append("P-1140E audit must report structural findings explicitly")
    if "does not establish" not in audit or "semantic" not in audit:
        errors.append("P-1140E audit must disclaim semantic proof")

    semantic = (ROOT / "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md").read_text(encoding="utf-8").lower()
    for marker in ["semantic p1 open: 4", "sr-001", "sr-002", "sr-003", "sr-004", "p-1104: blocked"]:
        if marker not in semantic:
            errors.append(f"P-1140F record is missing: {marker}")

    for doc in CORE_DOCS:
        text = (ROOT / doc).read_text(encoding="utf-8")
        for decision in DECISION.findall(text):
            if decision not in decisions:
                errors.append(f"unregistered decision reference: {doc}: {decision}")
        for task in TASK.findall(text):
            if task not in tasks:
                errors.append(f"unregistered task reference: {doc}: {task}")

    for workflow in [".github/workflows/planning-checks.yml", ".github/workflows/storyboard-visuals.yml"]:
        validate_action_pins(workflow, errors)
    validate_storyboard(errors)

    t20 = load_json("conformance/models/t20-model-registry-v1.json")
    if t20.get("selection_status") != "prelaunch-pending":
        errors.append("T20 registry must remain prelaunch-pending")
    if any(t20.get(key) for key in ("slots", "selection_runs", "accounting_profiles")):
        errors.append("T20 registry must not claim exercised selection or accounting profiles")

    codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")
    if any(marker in codeowners for marker in ("@security-owner", "@protocol-owner", "@infra-owner", "Replace with real")):
        errors.append("CODEOWNERS contains placeholder ownership")

    if errors:
        print("Repository doctor: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    print("Repository doctor: PASS")
    print("phase=planning-contract-repair active=P-1140F implementation=P-1104-blocked")


if __name__ == "__main__":
    main()
