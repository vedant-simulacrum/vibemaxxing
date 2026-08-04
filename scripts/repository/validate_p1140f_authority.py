#!/usr/bin/env python3
"""Validate machine-readable P-1140F authority, maturity, bundles, and review state."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
P1140F = ROOT / "conformance" / "p1140f"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance_name: str) -> dict:
    schema = load_json(P1140F / schema_name)
    instance = load_json(P1140F / instance_name)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise RuntimeError(f"{instance_name}: " + "; ".join(error.message for error in errors[:8]))
    return instance


def path_exists(reference: str) -> bool:
    path = reference.split("#", 1)[0]
    return (ROOT / path).exists()


def main() -> int:
    findings = validate("semantic-findings-v1.schema.json", "semantic-findings-v1.json")
    artifacts = validate("artifact-authority-v1.schema.json", "artifact-authority-v1.json")
    bundles = validate("contract-bundles-v1.schema.json", "contract-bundles-v1.json")
    review = validate("review-target-v1.schema.json", "review-target-v1.json")

    finding_rows = findings["findings"]
    ids = [row["finding_id"] for row in finding_rows]
    expected = [f"SR-{number:03d}" for number in range(5, 18)]
    if ids != expected:
        raise RuntimeError(f"finding registry must be ordered exactly SR-005..SR-017; found {ids}")
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate semantic finding ID")

    open_states = {"open", "repair-in-progress", "repaired-pending-review"}
    open_p1 = sum(row["severity"] == "P1" and row["state"] in open_states for row in finding_rows)
    if open_p1 != 13:
        raise RuntimeError(f"expected 13 active P1 clusters during P-1140F-1; found {open_p1}")
    if finding_rows[0]["state"] != "repair-in-progress":
        raise RuntimeError("SR-005 must be repair-in-progress while P-1140F-1 is active")
    if any(row["state"] == "closed" and not row["closure_evidence"] for row in finding_rows):
        raise RuntimeError("closed finding lacks closure evidence")
    for row in finding_rows:
        for reference in row["normative_owners"] + row["conflicting_artifacts"]:
            if not path_exists(reference):
                raise RuntimeError(f"{row['finding_id']} references missing artifact: {reference}")

    artifact_rows = artifacts["artifacts"]
    paths = [row["path"] for row in artifact_rows]
    if len(paths) != len(set(paths)):
        raise RuntimeError("duplicate artifact-authority path")
    ceiling_order = {
        "schema-valid": 0,
        "structurally-consistent": 1,
        "fixture-consistent": 2,
        "cross-language-parity": 3,
        "normative-conformance": 4,
        "adversarial-tested": 5,
        "platform-exercised": 6,
        "production-evidence": 7,
    }
    for row in artifact_rows:
        if not path_exists(row["path"]):
            raise RuntimeError(f"artifact registry references missing path: {row['path']}")
        if row["authority_class"] == "exploratory-prototype":
            if ceiling_order[row["evidence_ceiling"]] > ceiling_order["cross-language-parity"]:
                raise RuntimeError(f"exploratory artifact overclaims evidence: {row['path']}")
            if not row.get("known_incompatibilities"):
                raise RuntimeError(f"exploratory artifact lacks known incompatibilities: {row['path']}")

    bundle_rows = bundles["bundles"]
    bundle_ids = [row["bundle_id"] for row in bundle_rows]
    if bundle_ids != [f"CB-{number:03d}" for number in range(1, 8)]:
        raise RuntimeError("contract bundles must be ordered exactly CB-001..CB-007")
    covered_findings: set[str] = set()
    for row in bundle_rows:
        if row["state"] == "complete-planning" and any(
            next(item for item in finding_rows if item["finding_id"] == finding_id)["state"] in open_states
            for finding_id in row["finding_ids"]
        ):
            raise RuntimeError(f"{row['bundle_id']} claims complete-planning while a linked finding is active")
        covered_findings.update(row["finding_ids"])
        for finding_id in row["finding_ids"]:
            if finding_id not in ids:
                raise RuntimeError(f"{row['bundle_id']} references unknown finding {finding_id}")
        references = [
            row["normative_owner"],
            row["lifecycle_owner"],
            row["persistence_owner"],
            row["privacy_owner"],
            *row["machine_owners"],
            *row["threat_mappings"],
            *row["fixtures"],
        ]
        for reference in references:
            if not path_exists(reference):
                raise RuntimeError(f"{row['bundle_id']} references missing owner or fixture: {reference}")
    if covered_findings != set(ids):
        raise RuntimeError(f"contract bundles do not cover every finding; missing={sorted(set(ids) - covered_findings)}")

    suites = yaml.safe_load((ROOT / "evals/suites/suites.yaml").read_text(encoding="utf-8"))["suites"]
    suite_ids = {row["id"] for row in suites}
    if "protocol-conformance" in suite_ids:
        raise RuntimeError("shadow codec suite must not be named protocol-conformance")
    if "shadow-codec-parity" not in suite_ids:
        raise RuntimeError("shadow-codec-parity suite is missing")
    shadow_suite = next(row for row in suites if row["id"] == "shadow-codec-parity")
    if shadow_suite.get("authority_class") != "exploratory-prototype" or shadow_suite.get("evidence_ceiling") != "cross-language-parity":
        raise RuntimeError("shadow-codec-parity suite lacks explicit exploratory authority ceiling")

    status = (ROOT / "docs/project/STATUS.md").read_text(encoding="utf-8")
    tasks = (ROOT / "docs/planning/TASK_CATALOG.md").read_text(encoding="utf-8")
    semantic = (ROOT / "docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md").read_text(encoding="utf-8")
    for label, text in (("STATUS", status), ("TASK_CATALOG", tasks), ("P1140F", semantic)):
        if "13" not in text or "SR-005" not in text or "SR-017" not in text:
            raise RuntimeError(f"{label} does not summarize the registry range/count")
    if re.search(r"SR-005 through SR-016", tasks):
        raise RuntimeError("TASK_CATALOG omits SR-017 from P-1140F acceptance")

    if review["state"] == "reviewed":
        if review["review_verdict"] != "pass" or not review["reviewed_commit"] or not review["validation_run"]:
            raise RuntimeError("reviewed P-1140F target lacks immutable passing evidence")
        if open_p1:
            raise RuntimeError("P-1140F review cannot pass with active P1 findings")
    elif review["review_verdict"] != "pending":
        raise RuntimeError("unpinned or pending review must have pending verdict")

    print("P-1140F authority validation: pass")
    print(
        f"findings={len(finding_rows)} active_p1={open_p1} artifacts={len(artifact_rows)} "
        f"bundles={len(bundle_rows)} review_state={review['state']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
