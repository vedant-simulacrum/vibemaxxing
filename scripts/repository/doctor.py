#!/usr/bin/env python3
"""Read-only repository consistency checks for the planning phase."""

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
    "docs/project/PROJECT.md",
    "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md",
    "docs/planning/DECISION_REGISTER.md",
    "docs/planning/TASK_CATALOG.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
    "docs/implementation/PR_SIZED_WORK_BREAKDOWN.md",
    "docs/implementation/REPOSITORY_LAYOUT.md",
    "docs/implementation/ISSUE_GENERATION.md",
    "docs/decisions/ADR-007-BATCH_CHALLENGE_AND_SEQUENCE_RECOVERY.md",
    "docs/decisions/ADR-008-HANDLE_NORMALIZATION_AND_POLICY_REGISTRY.md",
    "docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md",
    "packages/schemas/adapter-manifest.schema.json",
    "packages/schemas/normalized-event.schema.json",
    "packages/schemas/vibeproof-claim-v1.cddl",
    "packages/schemas/local-control-v1.proto",
    "packages/schemas/openapi-v1.yaml",
    "packages/schemas/planning-schema.sql",
    "packages/schemas/reason-codes-v1.json",
    "packages/schemas/policy-defaults-v1.json",
    "packages/schemas/observability-allowlist-v1.yaml",
    "conformance/adapters/agent-registry-v1.json",
    "conformance/adapters/agent-registry-v1.schema.json",
    "conformance/adversarial/anti-cheat-registry-v1.json",
    "conformance/adversarial/anti-cheat-registry-v1.schema.json",
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

CORE_DOCS = [
    "AGENTS.md",
    "README.md",
    "docs/project/PROJECT.md",
    "docs/project/STATUS.md",
    "docs/project/DOCUMENTATION.md",
    "docs/implementation/IMPLEMENTATION_HANDOFF.md",
]

PATH_TOKEN = re.compile(r"`((?:\.?\.?/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)`")
DECISION = re.compile(r"\bD-\d{3}\b")
TASK = re.compile(r"\bP-\d{3,4}\b")


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
            candidate = ROOT / token
            if Path(token).suffix and not candidate.exists():
                errors.append(f"broken canonical reference: {doc} -> {token}")

    decisions_text = (ROOT / "docs/planning/DECISION_REGISTER.md").read_text(encoding="utf-8") if (ROOT / "docs/planning/DECISION_REGISTER.md").exists() else ""
    tasks_text = (ROOT / "docs/planning/TASK_CATALOG.md").read_text(encoding="utf-8") if (ROOT / "docs/planning/TASK_CATALOG.md").exists() else ""
    registered_decisions = set(DECISION.findall(decisions_text))
    registered_tasks = set(TASK.findall(tasks_text))
    for doc in CORE_DOCS:
        path = ROOT / doc
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for decision in DECISION.findall(text):
            if decision not in registered_decisions:
                errors.append(f"unregistered decision reference: {doc}: {decision}")
        for task in TASK.findall(text):
            if task not in registered_tasks:
                errors.append(f"unregistered task reference: {doc}: {task}")

    status = (ROOT / "docs/project/STATUS.md").read_text(encoding="utf-8") if (ROOT / "docs/project/STATUS.md").exists() else ""
    if "planning-hardening" not in status:
        errors.append("status must identify planning-hardening until P-1120..P-1128 pass")
    if "P-1120" not in tasks_text or "P-1128" not in tasks_text:
        errors.append("task catalog must contain planning-hardening range P-1120..P-1128")

    codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8") if (ROOT / ".github/CODEOWNERS").exists() else ""
    if "@security-owner" in codeowners or "@protocol-owner" in codeowners or "@infra-owner" in codeowners or "Replace with real" in codeowners:
        errors.append("CODEOWNERS contains placeholder ownership")

    licenses = (ROOT / "LICENSES.md").read_text(encoding="utf-8") if (ROOT / "LICENSES.md").exists() else ""
    if "AGPL" in licenses or "Apache License 2.0" not in licenses or "CC BY 4.0" not in licenses:
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
                errors.append(f"unknown adversarial action: {case['id']}: {case['expected_action']}")
            if case["reason_code"] not in reason_codes:
                errors.append(f"unknown adversarial reason code: {case['id']}: {case['reason_code']}")
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
                errors.append(f"unknown product family: {product['id']}: {product['family']}")
            for certification in product["certifications"]:
                for field in ("version", "mode", "platform", "tier", "suite_version", "result", "tested_at", "fixture_ref", "maintainer"):
                    if not certification.get(field):
                        errors.append(f"incomplete certification: {product['id']}: {field}")
    except Exception as exc:
        errors.append(f"agent registry validation failed: {exc}")

    structural = {
        "packages/schemas/vibeproof-claim-v1.cddl": "vibeproof-claim-v1",
        "packages/schemas/local-control-v1.proto": "syntax = \"proto3\"",
        "packages/schemas/openapi-v1.yaml": "openapi: 3.1.0",
        "packages/schemas/planning-schema.sql": "create table claims",
        "packages/schemas/observability-allowlist-v1.yaml": "policy: deny-by-default",
    }
    for path, marker in structural.items():
        if (ROOT / path).is_file() and marker not in (ROOT / path).read_text(encoding="utf-8"):
            errors.append(f"missing structural marker in {path}: {marker}")

    if errors:
        print("repository doctor: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    print("repository doctor: PASS")
    print(f"required files: {len(REQUIRED)}")
    print("phase: planning-hardening")


if __name__ == "__main__":
    main()
