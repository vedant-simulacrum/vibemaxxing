"""Drift-injection tests for scripts/repository/validate_finding_artifact_coverage.py.

The defect this guards is a finding recorded `repaired-pending-review` while one of the
conflicting artifacts it names was never opened by any commit its own closure evidence
cites. SR-007 was that, caught by hand twice; an audit then found the same shape in
three more findings, twelve artifacts in total. Nothing in `make validate` would have
said so.

The two directions matter equally and are tested separately. Forwards, an untouched and
unexplained artifact must fail. Backwards, a recorded reason for an artifact that *was*
touched must also fail — otherwise `unmodified_artifacts` becomes a place to park a
sentence, the excuse outlives the condition, and a later commit that did modify the
artifact leaves a record asserting it needed no modification.

The tests fabricate a findings record and patch `changed_paths`, so no test depends on
this repository's actual git history. A test that read real commits would start failing
for reasons that have nothing to do with the validator.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_finding_artifact_coverage.py"

SHA_A = "a" * 40
SHA_B = "b" * 40


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_finding_artifact_coverage", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


REASON = (
    "The contradiction this artifact was named for was resolved in the artifact it "
    "contradicted, which the repair edited instead."
)


def finding(**overrides):
    row = {
        "finding_id": "SR-005",
        "severity": "P1",
        "state": "repaired-pending-review",
        "title": "A fabricated finding",
        "repair_task": "P-1140F-1",
        "finding_class": "contradiction",
        "normative_owners": ["docs/owner.md"],
        "conflicting_artifacts": [
            "packages/schemas/one.json",
            "packages/schemas/two.json",
        ],
        "closure_evidence": [f"PF-001 at {SHA_A}: a repair happened."],
        "reviewed_commit": None,
        "review_verdict": "pending",
    }
    row.update(overrides)
    return row


class FindingArtifactCoverageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_validator()
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "semantic-findings-v1.json"

    def run_validator(self, rows, touched, unresolved=()):
        """Run main() against a fabricated record with a fabricated git history."""
        self.path.write_text(
            json.dumps({"schema_version": 1, "program": "P-1140F", "findings": rows}),
            encoding="utf-8",
        )

        def fake_changed_paths(sha):
            return None if sha in unresolved else set(touched.get(sha, ()))

        with (
            patch.object(self.module, "FINDINGS", self.path),
            patch.object(self.module, "changed_paths", fake_changed_paths),
        ):
            return self.module.main()

    def assert_fails(self, rows, touched, fragment, unresolved=()):
        with self.assertRaises(self.module.Failure) as caught:
            self.run_validator(rows, touched, unresolved)
        self.assertIn(fragment, str(caught.exception))

    # ---- forwards: an untouched, unexplained artifact fails --------------------

    def test_passes_when_every_artifact_is_touched(self):
        touched = {SHA_A: ["packages/schemas/one.json", "packages/schemas/two.json"]}
        self.assertEqual(self.run_validator([finding()], touched), 0)

    def test_untouched_artifact_fails(self):
        """The SR-007 case: evidence covering one of two named artifacts."""
        self.assert_fails(
            [finding()],
            {SHA_A: ["packages/schemas/one.json"]},
            "packages/schemas/two.json",
        )

    def test_untouched_artifact_passes_when_a_reason_is_recorded(self):
        rows = [finding(unmodified_artifacts={"packages/schemas/two.json": REASON})]
        self.assertEqual(
            self.run_validator(rows, {SHA_A: ["packages/schemas/one.json"]}), 0
        )

    def test_fragment_is_stripped_before_matching(self):
        """git reports files; an artifact may name a fragment inside one."""
        rows = [
            finding(
                conflicting_artifacts=["packages/schemas/one.json#certification"],
            )
        ]
        self.assertEqual(
            self.run_validator(rows, {SHA_A: ["packages/schemas/one.json"]}), 0
        )

    def test_directory_artifact_matches_a_path_beneath_it(self):
        rows = [finding(conflicting_artifacts=["crates/vibeproof-core/"])]
        self.assertEqual(
            self.run_validator(rows, {SHA_A: ["crates/vibeproof-core/src/lib.rs"]}), 0
        )

    def test_directory_artifact_is_not_matched_by_a_sibling_prefix(self):
        """`crates/vibeproof-core/` must not be satisfied by `crates/vibeproof-core-x`."""
        rows = [finding(conflicting_artifacts=["crates/vibeproof-core/"])]
        self.assert_fails(
            rows,
            {SHA_A: ["crates/vibeproof-core-extra/src/lib.rs"]},
            "crates/vibeproof-core/",
        )

    def test_settled_finding_with_no_cited_commit_fails(self):
        rows = [finding(closure_evidence=[])]
        self.assert_fails(rows, {}, "closure evidence cites no commit")

    # ---- state gating ---------------------------------------------------------

    def test_open_finding_is_not_required_to_cover_anything(self):
        """SR-016 is open with four untouched artifacts and is correct."""
        rows = [finding(state="open", closure_evidence=[])]
        self.assertEqual(self.run_validator(rows, {}), 0)

    def test_repair_in_progress_is_not_required_to_cover_anything(self):
        rows = [finding(state="repair-in-progress")]
        self.assertEqual(self.run_validator(rows, {SHA_A: []}), 0)

    def test_closed_finding_is_required_to_cover(self):
        self.assert_fails(
            [finding(state="closed")],
            {SHA_A: ["packages/schemas/one.json"]},
            "packages/schemas/two.json",
        )

    # ---- backwards: the reverse check -----------------------------------------

    def test_reason_for_a_touched_artifact_fails(self):
        """The guard that stops an excuse outliving the condition it described."""
        rows = [finding(unmodified_artifacts={"packages/schemas/two.json": REASON})]
        self.assert_fails(
            rows,
            {SHA_A: ["packages/schemas/one.json", "packages/schemas/two.json"]},
            "outlived the condition",
        )

    def test_reason_for_an_unnamed_artifact_fails(self):
        rows = [finding(unmodified_artifacts={"packages/schemas/absent.json": REASON})]
        self.assert_fails(
            rows,
            {SHA_A: ["packages/schemas/one.json", "packages/schemas/two.json"]},
            "does not name it in conflicting_artifacts",
        )

    def test_reverse_check_applies_to_an_open_finding_too(self):
        """A stale excuse is misleading whatever state the finding is in."""
        rows = [
            finding(
                state="repair-in-progress",
                unmodified_artifacts={"packages/schemas/two.json": REASON},
            )
        ]
        self.assert_fails(
            rows, {SHA_A: ["packages/schemas/two.json"]}, "outlived the condition"
        )

    def test_a_reason_too_short_to_be_a_reason_fails(self):
        rows = [finding(unmodified_artifacts={"packages/schemas/two.json": "n/a"})]
        self.assert_fails(
            rows, {SHA_A: ["packages/schemas/one.json"]}, "characters; at least"
        )

    # ---- unresolvable commits are unchecked, never passed ----------------------

    def test_unresolvable_commit_downgrades_to_unchecked_rather_than_failing(self):
        """A shallow clone cannot say, and must not fail an honest record."""
        rows = [finding()]
        self.assertEqual(self.run_validator(rows, {}, unresolved={SHA_A}), 0)

    def test_unresolvable_commit_does_not_fire_the_reverse_check(self):
        """Not knowing what a commit touched cannot prove a reason is stale."""
        rows = [finding(unmodified_artifacts={"packages/schemas/two.json": REASON})]
        self.assertEqual(self.run_validator(rows, {}, unresolved={SHA_A}), 0)

    def test_a_resolvable_commit_still_covers_when_another_is_unresolved(self):
        rows = [
            finding(
                closure_evidence=[
                    f"PF-001 at {SHA_A}: one.",
                    f"PF-002 at {SHA_B}: two.",
                ]
            )
        ]
        self.assertEqual(
            self.run_validator(
                rows,
                {SHA_B: ["packages/schemas/one.json", "packages/schemas/two.json"]},
                unresolved={SHA_A},
            ),
            0,
        )

    # ---- the record this repository actually ships -----------------------------

    def test_the_committed_record_satisfies_its_own_schema(self):
        import jsonschema

        base = ROOT / "conformance" / "p1140f"
        schema = json.loads((base / "semantic-findings-v1.schema.json").read_text())
        record = json.loads((base / "semantic-findings-v1.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(record)

    def test_every_recorded_reason_names_an_artifact_its_finding_claims(self):
        """Reads the shipped record rather than a fixture, in one direction only.

        The touched-ness half needs git and degrades in a shallow clone; this half is
        pure record consistency and holds everywhere.
        """
        base = ROOT / "conformance" / "p1140f"
        record = json.loads((base / "semantic-findings-v1.json").read_text())
        for row in record["findings"]:
            for artifact, reason in row.get("unmodified_artifacts", {}).items():
                self.assertIn(
                    artifact,
                    row["conflicting_artifacts"],
                    f"{row['finding_id']} excuses {artifact}, which it does not name",
                )
                self.assertGreaterEqual(len(reason.strip()), self.module.MINIMUM_REASON)


if __name__ == "__main__":
    unittest.main()
