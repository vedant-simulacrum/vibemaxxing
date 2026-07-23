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
    "docs/project/PROJECT.md",
    "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md",
    "docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md",
    "docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md",
    "docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md",
    "docs/planning/DECISION_REGISTER.md",
    "docs/planning/TASK_CATALOG.md",
    "docs/planning/decision-traceability/README.md",
    "docs/planning/decision-traceability/D-001-D-020.md",
    "docs/planning/decision-traceability/D-021-D-040.md",
    "docs/planning/decision-traceability/D-041-D-061.md",
    "docs/planning/decision-traceability/D-062-D-069.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
    "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
    "docs/implementation/REPOSITORY_LAYOUT.md",
    "docs/implementation/ISSUE_GENERATION.md",
    "docs/decisions/ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md",
    "docs/decisions/ADR-008-HANDLE_NORMALIZATION_AND_POLICY_REGISTRY.md",
    "docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md",
    "docs/decisions/ADR-010-ALWAYS_ON_DAEMON_LIFECYCLE.md",
    "docs/decisions/ADR-011-UNIVERSAL_PLATFORM_SUPPORT_BASELINE.md",
    "docs/decisions/ADR-012-OPTIONAL_PRIVILEGED_SUPERVISION.md",
    "docs/decisions/ADR-013-MANDATORY_AUTOMATIC_UPDATES.md",
    "docs/decisions/ADR-014-PROTOTYPE_VISUAL_VALIDATION_AUTOMATION.md",
    "packages/schemas/adapter-manifest.schema.json",
    "packages/schemas/normalized-event.schema.json",
    "packages/schemas/source-observation.schema.json",
    "packages/schemas/local-detector-result.schema.json",
    "packages/schemas/accounting-profile.schema.json",
    "packages/schemas/device-lineage.schema.json",
    "packages/schemas/pricing-interpretation.schema.json",
    "packages/schemas/evidence-profile-policy-v1.json",
    "packages/schemas/egress-allowlist-v1.schema.json",
    "packages/schemas/egress-allowlist-v1.json",
    "packages/schemas/vibeproof-claim-v1.cddl",
    "docs/architecture/VIBEPROOF_V1_PROTOCOL.md",
    "conformance/vibeproof/v1/exact-byte-vectors.json",
    "conformance/vibeproof/v1/malformed-resource-corpus.json",
    "packages/schemas/local-control-v1.proto",
    "packages/schemas/social-integrity-events-v1.proto",
    "packages/schemas/openapi-v1.yaml",
    "packages/schemas/planning-schema.sql",
    "packages/schemas/reason-codes-v1.json",
    "packages/schemas/policy-defaults-v1.json",
    "packages/schemas/observability-allowlist-v1.yaml",
    "conformance/accounting/accounting-profiles-v1.json",
    "conformance/accounting/p1140b-accounting-cases-v1.json",
    "conformance/privacy/p1140b-boundary-canaries-v1.json",
    "conformance/adapters/agent-registry-v1.json",
    "conformance/adapters/agent-registry-v1.schema.json",
    "conformance/adversarial/anti-cheat-registry-v1.json",
    "conformance/adversarial/anti-cheat-registry-v1.schema.json",
    "conformance/models/t20-model-registry-v1.json",
    "conformance/models/t20-model-registry-v1.schema.json",
    "conformance/models/t20-optimization-evidence-v1.schema.json",
    "conformance/models/fixtures/t20-optimization-evidence.valid.json",
    "conformance/models/fixtures/t20-optimization-evidence.invalid-pass.json",
    "scripts/repository/validate_t20_contract.py",
    "scripts/ui/playwright-runtime/package.json",
    "scripts/ui/playwright-runtime/package-lock.json",
]

HISTORICAL_RECORDS = [
    "docs/planning/PLANNING_HARDENING_VALIDATION_REPORT.md",
    "docs/planning/T20_PLANNING_COMPLETION_REPORT.md",
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
    "conformance/adversarial/anti-cheat-cases.json",
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

CORE_DOCS = [
    "AGENTS.md",
    "README.md",
    "docs/project/PROJECT.md",
    "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
]

TRACEABILITY_FILES = [
    "docs/planning/decision-traceability/D-001-D-020.md",
    "docs/planning/decision-traceability/D-021-D-040.md",
    "docs/planning/decision-traceability/D-041-D-061.md",
    "docs/planning/decision-traceability/D-062-D-069.md",
]

WORKFLOWS_REQUIRING_IMMUTABLE_ACTIONS = [
    ".github/workflows/planning-checks.yml",
    ".github/workflows/storyboard-visuals.yml",
]

STORYBOARD_ALLOWED_EVENTS = {"workflow_dispatch", "pull_request"}
STORYBOARD_ALLOWED_PATHS = {
    "packages/ui/**",
    "assets/**",
    "scripts/ui/**",
    "docs/style-guide/**",
    ".github/workflows/storyboard-visuals.yml",
}

PATH_TOKEN = re.compile(r"`((?:\.?\.?/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)`")
DECISION = re.compile(r"\bD-\d{3}\b")
TASK = re.compile(r"\bP-\d{3,4}[A-Z]?\b")
TRACE_ROW = re.compile(r"^\|\s*(D-\d{3})\s*\|")
ACTION_REF = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")
FULL_SHA_ACTION = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def load_json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def parse_decision_statuses(text: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    allowed = {"accepted", "provisional", "research-required", "deferred", "rejected", "superseded"}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"D-\d{3}", cells[0]) and cells[2] in allowed:
            statuses[cells[0]] = cells[2]
    return statuses


def parse_task_statuses(text: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    active_heading: str | None = None
    for line in text.splitlines():
        heading = re.match(r"^###\s+(P-\d{3,4}[A-Z]?)\b", line)
        if heading:
            active_heading = heading.group(1)
            continue
        if active_heading and line.startswith("Status: `"):
            statuses[active_heading] = line.removeprefix("Status: `").split("`", 1)[0]
            active_heading = None
            continue
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and re.fullmatch(r"P-\d{3,4}[A-Z]?", cells[0]):
                statuses[cells[0]] = cells[2]
    return statuses


def validate_action_pins(path: str, errors: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = ACTION_REF.match(line)
        if not match:
            continue
        reference = match.group(1)
        if reference.startswith("./"):
            continue
        if not FULL_SHA_ACTION.fullmatch(reference):
            errors.append(f"workflow action is not pinned to a full commit SHA: {path}:{line_number}: {reference}")


def validate_storyboard_workflow(text: str, errors: list[str]) -> None:
    lines = text.splitlines()
    try:
        on_index = lines.index("on:")
    except ValueError:
        errors.append("storyboard workflow is missing its event block")
        return

    event_lines: list[str] = []
    for line in lines[on_index + 1 :]:
        if line and not line.startswith(" "):
            break
        event_lines.append(line)

    events = {
        match.group(1)
        for line in event_lines
        if (match := re.fullmatch(r"  ([A-Za-z0-9_-]+):\s*", line))
    }
    if events != STORYBOARD_ALLOWED_EVENTS:
        errors.append(
            "storyboard workflow events must be exactly pull_request and workflow_dispatch under ADR-014; "
            f"found {sorted(events)}"
        )

    paths: set[str] = set()
    in_pull_request = False
    in_paths = False
    for line in event_lines:
        event_match = re.fullmatch(r"  ([A-Za-z0-9_-]+):\s*", line)
        if event_match:
            in_pull_request = event_match.group(1) == "pull_request"
            in_paths = False
            continue
        if in_pull_request and line == "    paths:":
            in_paths = True
            continue
        if in_paths:
            path_match = re.fullmatch(r"      -\s+[\"']?(.+?)[\"']?\s*", line)
            if path_match:
                paths.add(path_match.group(1).strip('"\''))
            elif line.strip() and not line.startswith("      "):
                in_paths = False

    if paths != STORYBOARD_ALLOWED_PATHS:
        errors.append(
            "storyboard pull_request paths must exactly match ADR-014 allowed scope; "
            f"missing={sorted(STORYBOARD_ALLOWED_PATHS - paths)}, extra={sorted(paths - STORYBOARD_ALLOWED_PATHS)}"
        )

    required_markers = {
        "read-only repository permissions": "permissions:\n  contents: read",
        "non-persisted checkout credentials": "persist-credentials: false",
        "synthetic-only fixtures": "VIBEMAXXING_FIXTURE_POLICY: synthetic-only",
        "loopback-only Storybook serving": "--bind 127.0.0.1",
        "locked Playwright runtime": "scripts/ui/playwright-runtime/package-lock.json",
        "prototype artifact maturity": "VIBEMAXXING_ARTIFACT_MATURITY: runnable-prototype",
    }
    for label, marker in required_markers.items():
        if marker not in text:
            errors.append(f"storyboard workflow is missing ADR-014 invariant: {label}")

    if "${{ secrets." in text:
        errors.append("storyboard workflow must not access repository or environment secrets under ADR-014")
    if re.search(r"(?m)^\s*retention-days:\s*(\d+)\s*$", text):
        retention = int(re.search(r"(?m)^\s*retention-days:\s*(\d+)\s*$", text).group(1))
        if retention > 30:
            errors.append("storyboard workflow artifact retention must not exceed 30 days under ADR-014")
    else:
        errors.append("storyboard workflow must declare bounded artifact retention under ADR-014")


def main() -> None:
    errors: list[str] = []

    for path in REQUIRED + HISTORICAL_RECORDS:
        if not (ROOT / path).is_file():
            errors.append(f"missing required file: {path}")
    for path in FORBIDDEN:
        if (ROOT / path).exists():
            errors.append(f"forbidden duplicate or obsolete file exists: {path}")
    for path in OUT_OF_SCOPE_NATIVE_PATHS:
        if (ROOT / path).exists():
            errors.append(f"out-of-scope native platform path exists under D-066: {path}")

    for path in ROOT.rglob("*.json"):
        if any(part in {".git", "node_modules", "target", "dist", "build"} for part in path.parts):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON: {path.relative_to(ROOT)}: {exc}")

    for doc in CORE_DOCS:
        path = ROOT / doc
        if not path.is_file():
            continue
        for token in PATH_TOKEN.findall(path.read_text(encoding="utf-8")):
            token = token.removeprefix("./")
            if token.startswith("../") or "{" in token or token.endswith("/"):
                continue
            if Path(token).suffix and not (ROOT / token).exists():
                errors.append(f"broken canonical reference: {doc} -> {token}")

    decisions_text = (ROOT / "docs/planning/DECISION_REGISTER.md").read_text(encoding="utf-8")
    tasks_text = (ROOT / "docs/planning/TASK_CATALOG.md").read_text(encoding="utf-8")
    decision_statuses = parse_decision_statuses(decisions_text)
    task_statuses = parse_task_statuses(tasks_text)
    registered_decisions = set(decision_statuses)
    registered_tasks = set(TASK.findall(tasks_text))

    expected_decisions = {f"D-{number:03d}" for number in range(1, 70)}
    missing_decisions = sorted(expected_decisions - registered_decisions)
    extra_decisions = sorted(registered_decisions - expected_decisions)
    if missing_decisions:
        errors.append(f"decision register is missing D-001..D-069 entries: {missing_decisions}")
    if extra_decisions:
        errors.append(f"decision register contains unexpected post-D-069 entries without doctor update: {extra_decisions}")

    expected_statuses = {
        "D-045": "superseded",
        "D-046": "provisional",
        "D-049": "accepted",
        "D-052": "accepted",
        **{f"D-{number:03d}": "accepted" for number in range(61, 70)},
    }
    for decision, expected_status in expected_statuses.items():
        actual = decision_statuses.get(decision)
        if actual != expected_status:
            errors.append(f"decision {decision} must be {expected_status}, found {actual!r}")

    trace_rows: list[str] = []
    for path in TRACEABILITY_FILES:
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            match = TRACE_ROW.match(line)
            if match:
                trace_rows.append(match.group(1))
    trace_counts = Counter(trace_rows)
    missing_trace = sorted(expected_decisions - set(trace_counts))
    duplicate_trace = sorted(decision for decision, count in trace_counts.items() if count != 1)
    if missing_trace:
        errors.append(f"decision traceability is missing: {missing_trace}")
    if duplicate_trace:
        errors.append(f"decision traceability must contain each decision exactly once: {duplicate_trace}")

    for doc in CORE_DOCS:
        text = (ROOT / doc).read_text(encoding="utf-8")
        for decision in DECISION.findall(text):
            if decision not in registered_decisions:
                errors.append(f"unregistered decision reference: {doc}: {decision}")
        for task in TASK.findall(text):
            if task not in registered_tasks:
                errors.append(f"unregistered task reference: {doc}: {task}")

    status = (ROOT / "docs/project/STATUS.md").read_text(encoding="utf-8")
    status_lower = status.lower()
    if "planning contract repair" not in status_lower:
        errors.append("status must state the current planning contract repair phase")
    if "p-1140d is active" not in status_lower:
        errors.append("status must identify P-1140D as active")
    if "product implementation remains unauthorized" not in status_lower:
        errors.append("status must state that product implementation remains unauthorized")
    if "phase: planning complete" in status_lower or "technical planning, including the targeted t20" in status_lower:
        errors.append("status contains a superseded planning-complete assertion")

    expected_task_statuses = {
        "P-1140A": "complete-planning",
        "P-1140B": "complete-planning",
        "P-1140C": "complete-planning",
        "P-1140D": "in-progress-planning",
        "P-1140E": "blocked-planning",
        "P-1104": "blocked-approval",
        "P-1131": "blocked-launch-evidence",
    }
    for task, expected_status in expected_task_statuses.items():
        actual = task_statuses.get(task)
        if actual != expected_status:
            errors.append(f"task {task} must be {expected_status}, found {actual!r}")

    t20_registry = load_json("conformance/models/t20-model-registry-v1.json")
    if not isinstance(t20_registry, dict) or t20_registry.get("selection_status") != "prelaunch-pending":
        errors.append("provisional T20 registry must remain prelaunch-pending")
    elif any(t20_registry.get(key) for key in ("slots", "selection_runs", "accounting_profiles")):
        errors.append("provisional T20 registry must not claim slots, selection runs, or accounting profiles")

    codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")
    if any(marker in codeowners for marker in ("@security-owner", "@protocol-owner", "@infra-owner", "Replace with real")):
        errors.append("CODEOWNERS contains placeholder ownership")
    licenses = (ROOT / "LICENSES.md").read_text(encoding="utf-8")
    if "Apache License 2.0" not in licenses or "CC BY 4.0" not in licenses:
        errors.append("LICENSES.md disagrees with ADR-009")

    try:
        reasons = load_json("packages/schemas/reason-codes-v1.json")
        reason_codes = {item["code"] for item in reasons["codes"]}
        if len(reason_codes) != len(reasons["codes"]):
            errors.append("duplicate reason code")
        adversarial = load_json("conformance/adversarial/anti-cheat-registry-v1.json")
        actions = set(adversarial["actions"])
        case_ids: set[str] = set()
        for case in adversarial["cases"]:
            if case["id"] in case_ids:
                errors.append(f"duplicate adversarial case id: {case['id']}")
            case_ids.add(case["id"])
            if case["expected_action"] not in actions:
                errors.append(f"unknown adversarial action: {case['id']}")
            if case["reason_code"] not in reason_codes:
                errors.append(f"unknown adversarial reason code: {case['id']}")
    except Exception as exc:
        errors.append(f"registry validation failed: {exc}")

    try:
        agents = load_json("conformance/adapters/agent-registry-v1.json")
        families = {item["id"] for item in agents["families"]}
        product_ids: set[str] = set()
        for product in agents["products"]:
            if product["id"] in product_ids:
                errors.append(f"duplicate product id: {product['id']}")
            product_ids.add(product["id"])
            if product["family"] not in families:
                errors.append(f"unknown product family: {product['id']}")
    except Exception as exc:
        errors.append(f"agent registry validation failed: {exc}")

    structural = {
        "packages/schemas/vibeproof-claim-v1.cddl": "vibeproof-claim-v1",
        "packages/schemas/local-control-v1.proto": 'syntax = "proto3"',
        "packages/schemas/openapi-v1.yaml": "openapi: 3.1.0",
        "packages/schemas/planning-schema.sql": "create table claims",
        "packages/schemas/observability-allowlist-v1.yaml": "policy: deny-by-default",
        "docs/integrations/T20_MODEL_HARDENING_CONTRACT.md": "D-046 is provisional",
        "docs/integrations/T20_CERTIFICATION_AND_SELECTION_SPEC.md": "provisional candidate specification",
    }
    for path, marker in structural.items():
        if marker not in (ROOT / path).read_text(encoding="utf-8"):
            errors.append(f"missing structural marker in {path}: {marker}")

    for workflow in WORKFLOWS_REQUIRING_IMMUTABLE_ACTIONS:
        validate_action_pins(workflow, errors)

    storyboard = (ROOT / ".github/workflows/storyboard-visuals.yml").read_text(encoding="utf-8")
    validate_storyboard_workflow(storyboard, errors)
    if "npm install --no-save" in storyboard:
        errors.append("storyboard workflow must not install dependencies outside a committed lockfile")
    if "scripts/ui/playwright-runtime" not in storyboard:
        errors.append("storyboard workflow must install the dedicated locked Playwright runtime")

    issue_plan_source = (ROOT / "scripts/repository/generate_issue_plan.py").read_text(encoding="utf-8")
    if "IMP-" in issue_plan_source or "range(1, 53)" in issue_plan_source:
        errors.append("issue-plan generator still depends on obsolete IMP-001..IMP-052 numbering")

    if errors:
        print("repository doctor: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    print("repository doctor: PASS")
    print(f"required current files: {len(REQUIRED)}")
    print(f"registered decisions: {len(expected_decisions)}")
    print("phase: planning contract repair; implementation not authorized")


if __name__ == "__main__":
    main()
