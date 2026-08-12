#!/usr/bin/env python3
"""Validate machine-readable P-1140F authority, maturity, bundles, and review state.

Findings carry evidence rules this validator owns, because a JSON Schema can express
their shape but not why the shape matters:

* `conflicting_artifacts` may not be empty — a finding that names nothing it
  contradicts cannot be falsified by anyone but its author;
* no artifact may be both a finding's normative owner and its conflicting artifact,
  which is what a self-owned finding looks like in machine-readable form;
* a `path#fragment` citation must resolve to a fragment the file contains;
* `planned_artifacts` names artifacts that deliberately do not exist yet, so each one
  must be absent from the filesystem and recorded `planned-missing` in the schema
  inventory;
* a finding classified as anything other than a contradiction must record the
  restatement that reclassified it.

None of this proves a finding is correct. It proves only that the finding says what
would contradict it.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
P1140F = ROOT / "conformance" / "p1140f"
INVENTORY = ROOT / "docs" / "planning" / "SCHEMA_AND_INTERFACE_INVENTORY.md"

# A path in inline code on an inventory row. Rows are matched by their
# `planned-missing` status cell, so this only ever reads paths off a planned row.
PLANNED_MISSING_RE = re.compile(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`")

# A per-severity non-regression ceiling in the gate record. Ceilings are discovered
# by this shape rather than listed here, so recording one for a new severity is an
# edit to the record and its schema and never to this file.
BASELINE_KEY_RE = re.compile(r"^open_p[0-9]+_baseline$")


def load_json(path: Path):
    if not path.is_file():
        raise RuntimeError(f"missing required P-1140F record: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"unreadable P-1140F record {path.name}: {error}") from error


def validate(schema_name: str, instance_name: str) -> dict:
    schema = load_json(P1140F / schema_name)
    instance = load_json(P1140F / instance_name)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        ),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise RuntimeError(
            f"{instance_name}: " + "; ".join(error.message for error in errors[:8])
        )
    return instance


def path_exists(reference: str) -> bool:
    path = reference.split("#", 1)[0]
    return (ROOT / path).exists()


def fragment_resolves(reference: str) -> bool:
    """A `path#fragment` citation must name something the file actually contains.

    The fragment is a literal token — a SQL table, an OpenAPI `operationId` or schema
    name, a CDDL rule, a Protobuf field, a state-machine ID, a commit. Requiring it to
    occur in the cited file is what makes a citation rot visibly instead of silently
    pointing at a file that no longer says what the finding claims.
    """
    path, _, fragment = reference.partition("#")
    if not fragment:
        return True
    target = ROOT / path
    if not target.is_file():
        return False
    return fragment in target.read_text(encoding="utf-8", errors="replace")


def planned_missing_artifacts() -> set[str]:
    """Paths the schema inventory records as `planned-missing`."""
    if not INVENTORY.is_file():
        raise RuntimeError(f"missing schema inventory: {INVENTORY.name}")
    planned: set[str] = set()
    for line in INVENTORY.read_text(encoding="utf-8").splitlines():
        if "planned-missing" in line:
            planned.update(PLANNED_MISSING_RE.findall(line))
    return planned


def check_finding_evidence(finding_rows: list[dict]) -> None:
    """Every finding must name what it contradicts, and every citation must resolve.

    These rules live here rather than in the JSON Schema so each failure can say why
    the shape matters. An empty `conflicting_artifacts` is indistinguishable from an
    unexamined one, which is how twelve findings sat unfalsifiable while every
    validator stayed green.
    """
    planned_inventory = planned_missing_artifacts()
    for row in finding_rows:
        identifier = row["finding_id"]
        if not row["conflicting_artifacts"]:
            raise RuntimeError(
                f"{identifier} lists no conflicting artifact: a finding that names nothing "
                "it contradicts is unfalsifiable, so no evidence can close it"
            )
        owners = {reference.split("#", 1)[0] for reference in row["normative_owners"]}
        conflicts = {
            reference.split("#", 1)[0] for reference in row["conflicting_artifacts"]
        }
        self_owned = sorted(owners & conflicts)
        if self_owned:
            raise RuntimeError(
                f"{identifier} is self-owned: {self_owned} is both its normative authority "
                "and the artifact it contradicts, so its closure evidence would be its own "
                "definition"
            )
        for reference in row["normative_owners"] + row["conflicting_artifacts"]:
            if not path_exists(reference):
                raise RuntimeError(
                    f"{identifier} references missing artifact: {reference}"
                )
            if not fragment_resolves(reference):
                raise RuntimeError(
                    f"{identifier} cites {reference} but that file does not contain the "
                    "cited fragment"
                )
        for reference in row.get("planned_artifacts", []):
            if "#" in reference:
                raise RuntimeError(
                    f"{identifier} plans {reference} with a fragment; an artifact that does "
                    "not exist cannot have one"
                )
            if path_exists(reference):
                raise RuntimeError(
                    f"{identifier} lists {reference} as planned, but it exists; a live "
                    "artifact belongs in conflicting_artifacts"
                )
            if reference not in planned_inventory:
                raise RuntimeError(
                    f"{identifier} plans {reference}, which {INVENTORY.name} does not record "
                    "as planned-missing"
                )
        if row["finding_class"] != "contradiction" and "restatement" not in row:
            raise RuntimeError(
                f"{identifier} is classified {row['finding_class']} rather than a "
                "contradiction and records no restatement explaining what it is instead"
            )


def main() -> int:
    findings = validate("semantic-findings-v1.schema.json", "semantic-findings-v1.json")
    artifacts = validate(
        "artifact-authority-v1.schema.json", "artifact-authority-v1.json"
    )
    bundles = validate("contract-bundles-v1.schema.json", "contract-bundles-v1.json")
    review = validate("review-target-v1.schema.json", "review-target-v1.json")
    authorization = validate(
        "gate-authorization-v1.schema.json", "gate-authorization-v1.json"
    )

    finding_rows = findings["findings"]
    ids = [row["finding_id"] for row in finding_rows]
    expected = [f"SR-{number:03d}" for number in range(5, 18)]
    if ids != expected:
        raise RuntimeError(
            f"finding registry must be ordered exactly SR-005..SR-017; found {ids}"
        )
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate semantic finding ID")

    # The gate record declares one ceiling per severity, under a property named for
    # that severity. They are read as a set rather than by name so that adding a
    # severity to the finding registry needs a ceiling in the record and nothing
    # here. Each ceiling's own `severity` field is what the ceiling is keyed by; the
    # property name is a label, and the schema pins the two to agree.
    ceilings = {
        ceiling["severity"]: ceiling
        for key, ceiling in authorization.items()
        if BASELINE_KEY_RE.match(key)
    }
    if len(ceilings) != sum(1 for key in authorization if BASELINE_KEY_RE.match(key)):
        raise RuntimeError(
            "conformance/p1140f/gate-authorization-v1.json declares two ceilings for "
            "one severity; a severity with two ceilings is governed by whichever the "
            "reader picks"
        )

    # Every ceiling must agree about which states count as open. A ceiling that
    # counted fewer states than its neighbours would let a finding be open under one
    # severity and invisible under another, which is the same escape as having no
    # ceiling at all, reached by editing three words instead of deleting an object.
    baseline = authorization["open_p1_baseline"]
    open_states = set(baseline["counted_states"])
    disagreeing = sorted(
        severity
        for severity, ceiling in ceilings.items()
        if set(ceiling["counted_states"]) != open_states
    )
    if disagreeing:
        raise RuntimeError(
            f"recorded ceilings disagree about which states count as open: {disagreeing} "
            f"differ from open_p1_baseline.counted_states {sorted(open_states)} in "
            f"conformance/p1140f/gate-authorization-v1.json. One severity would then be "
            f"open in a state another severity is not counted in"
        )

    active = Counter(
        row["severity"] for row in finding_rows if row["state"] in open_states
    )
    for severity in sorted(ceilings):
        if active[severity] > ceilings[severity]["count"]:
            raise RuntimeError(
                f"active {severity} findings regressed: {active[severity]} open exceeds "
                f"the recorded baseline of {ceilings[severity]['count']} in "
                f"conformance/p1140f/gate-authorization-v1.json"
            )

    # Every severity that actually appears must have a ceiling tracking it.
    #
    # Each ceiling's rule fails only when its count *exceeds* it, so a regrade that
    # moves findings to a severity with no ceiling lowers the count that was watching
    # them, keeps validation green, and leaves the regraded findings tracked by
    # nothing at all — a ceiling reporting an improvement while the findings walked
    # out of scope. This is the same shape as an eval suite downgraded to
    # not_applicable: a number improved by removing what it counts.
    #
    # The record now declares a ceiling for every severity the finding registry's
    # schema admits, so a legal regrade cannot reach this branch. It stays because
    # what makes the regrade safe is the coverage, not the count: adding a severity
    # to the registry, or deleting a ceiling from the gate record, reopens exactly
    # the hole this guard was written for. A severity without a ceiling is therefore
    # an error rather than an absence, and it is not softened by the ceilings that do
    # exist. Adding the missing one is an owner action, because ceilings live in the
    # gate record.
    ceilinged = set(ceilings)
    ungoverned: dict[str, list[str]] = {}
    for row in finding_rows:
        if row["state"] in open_states and row["severity"] not in ceilinged:
            ungoverned.setdefault(row["severity"], []).append(row["finding_id"])
    if ungoverned:
        detail = "; ".join(
            f"{severity}: {', '.join(sorted(identifiers))}"
            for severity, identifiers in sorted(ungoverned.items())
        )
        raise RuntimeError(
            f"open findings carry a severity with no recorded ceiling ({detail}). "
            f"conformance/p1140f/gate-authorization-v1.json records ceilings for "
            f"{', '.join(sorted(ceilinged))} only, so these findings are tracked by "
            f"nothing. The owner adds the missing ceiling as open_<severity>_baseline, "
            f"which also needs gate-authorization-v1.schema.json amended because it "
            f"admits one named property per severity and pins each to its own severity "
            f"constant. A validator change would hide these findings instead."
        )

    # A state outside counted_states escapes the ceiling entirely.
    declared_states = {row["state"] for row in finding_rows}
    uncounted = sorted(declared_states - open_states - {"closed"})
    if uncounted:
        raise RuntimeError(
            f"findings sit in states the ceiling does not count: {uncounted}. "
            f"conformance/p1140f/gate-authorization-v1.json counts "
            f"{sorted(open_states)}; a state outside that set is neither open nor "
            f"closed and is governed by nothing"
        )
    if finding_rows[0]["state"] == "open":
        raise RuntimeError(
            "SR-005 must be under repair or resolved while P-1140F-1 is active"
        )
    if any(
        row["state"] == "closed" and not row["closure_evidence"] for row in finding_rows
    ):
        raise RuntimeError("closed finding lacks closure evidence")
    check_finding_evidence(finding_rows)

    artifact_rows = artifacts["artifacts"]
    paths = [row["path"] for row in artifact_rows]
    if len(paths) != len(set(paths)):
        raise RuntimeError("duplicate artifact-authority path")
    # The ladder and the per-class caps are read from the registry rather than
    # copied here. This validator used to carry its own copy of the ladder and its
    # own hard-coded rule for one class, so a ceiling added to the policy was
    # unknown to the checker and a class other than exploratory-prototype was
    # capped by nothing at all.
    declared_ceilings = artifacts["evidence_ceilings"]
    if len(set(declared_ceilings)) != len(declared_ceilings):
        raise RuntimeError("artifact registry repeats an evidence ceiling")
    if declared_ceilings[0] != "none":
        raise RuntimeError(
            "the weakest evidence ceiling must be 'none'; an eval suite with no "
            "fixtures is capped there, and a ladder whose floor is a positive claim "
            "gives an absence of evidence somewhere to sit"
        )
    ceiling_order = {name: index for index, name in enumerate(declared_ceilings)}
    class_maxima = {
        name: record["maximum_evidence_ceiling"]
        for name, record in artifacts["authority_classes"].items()
    }
    unknown_caps = sorted(set(class_maxima.values()) - set(ceiling_order))
    if unknown_caps:
        raise RuntimeError(
            f"authority classes cap at undeclared ceilings: {unknown_caps}"
        )
    for row in artifact_rows:
        if not path_exists(row["path"]):
            raise RuntimeError(
                f"artifact registry references missing path: {row['path']}"
            )
        if row["authority_class"] not in class_maxima:
            raise RuntimeError(
                f"artifact declares an undeclared authority class: {row['path']} "
                f"({row['authority_class']})"
            )
        if row["evidence_ceiling"] not in ceiling_order:
            raise RuntimeError(
                f"artifact declares an undeclared evidence ceiling: {row['path']} "
                f"({row['evidence_ceiling']})"
            )
        cap = class_maxima[row["authority_class"]]
        if ceiling_order[row["evidence_ceiling"]] > ceiling_order[cap]:
            raise RuntimeError(
                f"artifact overclaims evidence: {row['path']} declares "
                f"{row['evidence_ceiling']} and {row['authority_class']} caps at {cap}"
            )
        if row["authority_class"] == "exploratory-prototype" and not row.get(
            "known_incompatibilities"
        ):
            raise RuntimeError(
                f"exploratory artifact lacks known incompatibilities: {row['path']}"
            )

    bundle_rows = bundles["bundles"]
    bundle_ids = [row["bundle_id"] for row in bundle_rows]
    if bundle_ids != [f"CB-{number:03d}" for number in range(1, 8)]:
        raise RuntimeError("contract bundles must be ordered exactly CB-001..CB-007")
    covered_findings: set[str] = set()
    for row in bundle_rows:
        if row["state"] == "complete-planning" and any(
            next(item for item in finding_rows if item["finding_id"] == finding_id)[
                "state"
            ]
            in open_states
            for finding_id in row["finding_ids"]
        ):
            raise RuntimeError(
                f"{row['bundle_id']} claims complete-planning while a linked finding is active"
            )
        covered_findings.update(row["finding_ids"])
        for finding_id in row["finding_ids"]:
            if finding_id not in ids:
                raise RuntimeError(
                    f"{row['bundle_id']} references unknown finding {finding_id}"
                )
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
                raise RuntimeError(
                    f"{row['bundle_id']} references missing owner or fixture: {reference}"
                )
    if covered_findings != set(ids):
        raise RuntimeError(
            f"contract bundles do not cover every finding; missing={sorted(set(ids) - covered_findings)}"
        )

    suites = yaml.safe_load(
        (ROOT / "evals/suites/suites.yaml").read_text(encoding="utf-8")
    )["suites"]
    suite_ids = {row["id"] for row in suites}
    if "protocol-conformance" in suite_ids:
        raise RuntimeError("shadow codec suite must not be named protocol-conformance")
    if "shadow-codec-parity" not in suite_ids:
        raise RuntimeError("shadow-codec-parity suite is missing")
    shadow_suite = next(row for row in suites if row["id"] == "shadow-codec-parity")
    if (
        shadow_suite.get("authority_class") != "exploratory-prototype"
        or shadow_suite.get("evidence_ceiling") != "cross-language-parity"
    ):
        raise RuntimeError(
            "shadow-codec-parity suite lacks explicit exploratory authority ceiling"
        )

    for gate in authorization["gates"]:
        for document in gate["documents"]:
            if not path_exists(document["path"]):
                raise RuntimeError(
                    f"{gate['gate']} names a missing document: {document['path']}"
                )
        grant = gate["authorization"]
        if grant is None:
            continue
        unknown = sorted(
            set(grant.get("findings_open_at_authorization", [])) - set(ids)
        )
        if unknown:
            raise RuntimeError(
                f"{gate['gate']} authorization names findings outside the registry: {unknown}"
            )
        if len(grant.get("findings_open_at_authorization", [])) not in (
            0,
            grant["open_p1_findings_at_authorization"],
        ):
            raise RuntimeError(
                f"{gate['gate']} authorization lists a finding set that contradicts its recorded count"
            )

    # Prose-versus-record count agreement is owned by scripts/repository/doctor.py so
    # that exactly one validator holds it. This one owns registry range and ordering.
    for relative_path in authorization["registry_summary_documents"]:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for token in (ids[0], ids[-1]):
            if token not in text:
                raise RuntimeError(
                    f"{relative_path} does not summarize the registry range/count: missing {token}"
                )
        stale = sorted(
            {
                match
                for match in re.findall(rf"{ids[0]} through (SR-[0-9]{{3}})", text)
                if match != ids[-1]
            }
        )
        if stale:
            raise RuntimeError(
                f"{relative_path} states a finding range ending at {stale} rather than {ids[-1]}"
            )

    if review["state"] == "reviewed":
        if (
            review["review_verdict"] != "pass"
            or not review["reviewed_commit"]
            or not review["validation_run"]
        ):
            raise RuntimeError(
                "reviewed P-1140F target lacks immutable passing evidence"
            )
        # Every open finding blocks the verdict, not only the P1 ones. Reading this
        # off the P1 count alone would have let the same regrade that partitioned the
        # ceiling also empty this check: nine findings moved to P0 and the review
        # passes with nine open contradictions.
        if sum(active.values()):
            detail = ", ".join(
                f"{severity}={count}" for severity, count in sorted(active.items())
            )
            raise RuntimeError(
                f"P-1140F review cannot pass with active findings ({detail})"
            )
    elif review["review_verdict"] != "pending":
        raise RuntimeError("unpinned or pending review must have pending verdict")

    print("P-1140F authority validation: pass")
    print(
        f"findings={len(finding_rows)} "
        + " ".join(
            f"active_{severity.lower()}={active[severity]} "
            f"baseline_{severity.lower()}={ceilings[severity]['count']}"
            for severity in sorted(ceilings)
        )
        + f" artifacts={len(artifact_rows)} bundles={len(bundle_rows)} "
        f"review_state={review['state']} "
        + " ".join(f"{gate['gate']}={gate['state']}" for gate in authorization["gates"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
