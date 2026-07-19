#!/usr/bin/env python3
"""Read-only repository consistency checks for the planning phase."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "AGENTS.md", "README.md", "LICENSES.md", "SECURITY.md", "CONTRIBUTING.md", ".github/CODEOWNERS",
    "docs/project/PROJECT.md", "docs/project/STATUS.md", "docs/project/DOCUMENTATION.md",
    "docs/planning/DECISION_REGISTER.md", "docs/planning/TASK_CATALOG.md",
    "docs/planning/PLANNING_HARDENING_VALIDATION_REPORT.md",
    "docs/planning/T20_PLANNING_COMPLETION_REPORT.md",
    "docs/integrations/T20_MODEL_HARDENING_CONTRACT.md",
    "docs/integrations/T20_CERTIFICATION_AND_SELECTION_SPEC.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md", "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
    "docs/implementation/REPOSITORY_LAYOUT.md", "docs/implementation/ISSUE_GENERATION.md",
    "docs/decisions/ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md",
    "docs/decisions/ADR-008-HANDLE_NORMALIZATION_AND_POLICY_REGISTRY.md",
    "docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md",
    "packages/schemas/adapter-manifest.schema.json", "packages/schemas/normalized-event.schema.json",
    "packages/schemas/vibeproof-claim-v1.cddl", "packages/schemas/local-control-v1.proto",
    "packages/schemas/social-integrity-events-v1.proto", "packages/schemas/openapi-v1.yaml",
    "packages/schemas/planning-schema.sql", "packages/schemas/reason-codes-v1.json",
    "packages/schemas/policy-defaults-v1.json", "packages/schemas/observability-allowlist-v1.yaml",
    "conformance/adapters/agent-registry-v1.json", "conformance/adapters/agent-registry-v1.schema.json",
    "conformance/adversarial/anti-cheat-registry-v1.json", "conformance/adversarial/anti-cheat-registry-v1.schema.json",
    "conformance/models/t20-model-registry-v1.json", "conformance/models/t20-model-registry-v1.schema.json",
    "conformance/models/t20-optimization-evidence-v1.schema.json",
    "conformance/models/fixtures/t20-optimization-evidence.valid.json",
    "conformance/models/fixtures/t20-optimization-evidence.invalid-pass.json",
    "scripts/repository/validate_t20_contract.py",
]

FORBIDDEN = [
    "PROJECT_CONTEXT.md", "PROJECT_INSTRUCTIONS.md", "CURRENT_STATUS.md", "MODEL_OPERATING_MANUAL.md",
    "IMPLEMENTATION_ROADMAP.md", "RESEARCH_AND_EVIDENCE_BACKLOG.md", "START_HERE_PROMPT.md",
    "CHATGPT_WORK_PROJECT_PROMPT.md", "docs/implementation/BUILD_PLAN.md", "docs/implementation/TECH_STACK.md",
    "docs/planning/SPECIFICATION_INDEX.md", "docs/planning/DEPENDENCY_MAP.md", "docs/planning/PLANNING_AUDIT.md",
    "conformance/adversarial/anti-cheat-cases.json",
]

CORE_DOCS = [
    "AGENTS.md", "README.md", "docs/project/PROJECT.md", "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md", "docs/implementation/IMPLEMENTATION_HANDOFF.md",
]
PATH_TOKEN = re.compile(r"`((?:\.?\.?/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)`")
DECISION = re.compile(r"\bD-\d{3}\b")
TASK = re.compile(r"\bP-\d{3,4}[A-Z]?\b")


def load_json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    errors: list[str] = []
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            errors.append(f"missing required file: {path}")
    for path in FORBIDDEN:
        if (ROOT / path).exists():
            errors.append(f"forbidden duplicate or obsolete file exists: {path}")

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
    registered_decisions = set(DECISION.findall(decisions_text))
    registered_tasks = set(TASK.findall(tasks_text))
    for doc in CORE_DOCS:
        text = (ROOT / doc).read_text(encoding="utf-8")
        for decision in DECISION.findall(text):
            if decision not in registered_decisions:
                errors.append(f"unregistered decision reference: {doc}: {decision}")
        for task in TASK.findall(text):
            if task not in registered_tasks:
                errors.append(f"unregistered task reference: {doc}: {task}")

    status = (ROOT / "docs/project/STATUS.md").read_text(encoding="utf-8")
    if "Technical planning, including the targeted T20 golden-path hardening, is complete" not in status:
        errors.append("status must state completed T20 planning hardening")
    if "P-1104" not in status:
        errors.append("status must identify P-1104 as the implementation entrance gate")
    for decision in ("D-045", "D-046"):
        if not re.search(rf"\| {decision} \|.*\| accepted \|", decisions_text):
            errors.append(f"decision register must accept {decision}")
    for task in ("P-1120", "P-1126", "P-1128", "P-1130A", "P-1130B", "P-1130C", "P-1130D", "P-1130E"):
        if not re.search(rf"\| {task} \|.*\| complete-planning \|", tasks_text):
            errors.append(f"task catalog must close {task} as complete-planning")
    if not re.search(r"\| P-1104 \|.*\| blocked-approval \|", tasks_text):
        errors.append("P-1104 must remain blocked-approval")
    if not re.search(r"\| P-1131 \|.*\| blocked-launch-evidence \|", tasks_text):
        errors.append("P-1131 must remain blocked-launch-evidence")

    t20_registry = load_json("conformance/models/t20-model-registry-v1.json")
    if t20_registry.get("selection_status") != "prelaunch-pending":
        errors.append("planning-phase T20 registry must remain prelaunch-pending")
    for key in ("slots", "selection_runs", "accounting_profiles"):
        if t20_registry.get(key):
            errors.append(f"planning-phase T20 registry must not claim {key}")

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
        "docs/integrations/T20_MODEL_HARDENING_CONTRACT.md": "T20 is the product's **golden path**",
        "docs/integrations/T20_CERTIFICATION_AND_SELECTION_SPEC.md": "Source precedence within one duplicate domain",
    }
    for path, marker in structural.items():
        if marker not in (ROOT / path).read_text(encoding="utf-8"):
            errors.append(f"missing structural marker in {path}: {marker}")

    if errors:
        print("repository doctor: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("repository doctor: PASS")
    print(f"required files: {len(REQUIRED)}")
    print("phase: planning complete; implementation not authorized")


if __name__ == "__main__":
    main()
