"""PF-022. A leaderboard cursor is viewer-bound, generation-pinned and expiring.

The `Cursor` parameter asserted that the server "rejects a cursor it did not issue, a
cursor issued against a different snapshot_id, and a cursor issued to a different
principal". No record in the repository held an issuer, a snapshot or a principal, so
all three refusals compared fields that did not exist.

Each case injects one way the rule, the corpus or the storage it anchors in can rot.
"""

from __future__ import annotations

import copy
import unittest

from .planning_fixtures import PlanningValidatorMixin

VECTORS = "conformance/planning/ranking-cursor-vectors-v1.json"
SQL = "packages/schemas/planning-schema.sql"


class RankingCursorTests(PlanningValidatorMixin, unittest.TestCase):
    def check(self) -> None:
        self.validator.validate_ranking_cursor_vectors()

    def case(self, record, case_id: str) -> dict:
        return next(item for item in record["cases"] if item["case_id"] == case_id)

    def test_the_committed_tree_passes(self) -> None:
        self.assert_passes(self.check)

    def test_a_replay_by_another_viewer_is_refused(self) -> None:
        """The case the unit exists for, evaluated rather than read back."""
        record = self.read(VECTORS)
        case = self.case(record, "RC-002")
        refusal = self.validator.evaluate_cursor(case, record["refusal_order"])

        self.assertEqual(refusal, "viewer-mismatch")

    def test_an_anonymous_reader_is_not_a_wildcard_viewer(self) -> None:
        record = self.read(VECTORS)
        case = self.case(record, "RC-003")

        self.assertEqual(
            self.validator.evaluate_cursor(case, record["refusal_order"]),
            "viewer-mismatch",
        )

    def test_a_case_recording_the_wrong_outcome_fails(self) -> None:
        record = self.read(VECTORS)
        self.case(record, "RC-002")["expected"] = {
            "outcome": "accept",
            "refusal": None,
            "reason_code": None,
        }
        self.write(VECTORS, record)

        self.assert_fails(self.check, "records accept and the rules refuse it")

    def test_a_case_recording_the_wrong_refusal_fails(self) -> None:
        record = self.read(VECTORS)
        expected = self.case(record, "RC-006")["expected"]
        expected["refusal"] = "generation-mismatch"
        self.write(VECTORS, record)

        self.assert_fails(self.check, "and the rules refuse it with expired")

    def test_a_case_recording_the_wrong_reason_code_fails(self) -> None:
        record = self.read(VECTORS)
        self.case(record, "RC-002")["expected"]["reason_code"] = (
            "PAGINATION_CURSOR_INVALID"
        )
        self.write(VECTORS, record)

        self.assert_fails(self.check, "rather than VIEWER_NOT_AUTHORIZED")

    def test_removing_the_only_case_for_a_refusal_fails(self) -> None:
        """A signal that improves when the thing it counts is removed."""
        record = self.read(VECTORS)
        record["cases"] = [
            case
            for case in record["cases"]
            if case["expected"]["refusal"] != "authorization-revision-moved"
        ]
        self.write(VECTORS, record)

        self.assert_fails(self.check, "no case exercises the cursor refusals")

    def test_removing_every_accepted_case_fails(self) -> None:
        record = self.read(VECTORS)
        record["cases"] = [
            case for case in record["cases"] if case["expected"]["outcome"] != "accept"
        ]
        self.write(VECTORS, record)

        self.assert_fails(self.check, "no cursor case is accepted")

    def test_a_refusal_the_corpus_does_not_order_fails(self) -> None:
        """The direction that actually rots: the rule grows and the corpus does not.

        Dropping a refusal from the fixture is caught by the vectors schema, which
        requires all five. A refusal added to the rule and to nothing else is not,
        and it is the shape a new check takes when it is written.
        """
        self.validator.CURSOR_REFUSAL_REASONS["forged-signature"] = (
            "PAGINATION_CURSOR_INVALID"
        )

        self.assert_fails(self.check, "does not cover exactly the declared refusals")

    def test_the_declared_order_decides_a_doubly_broken_presentation(self) -> None:
        """Reordering changes the answer, which is why the order is a rule."""
        record = self.read(VECTORS)
        case = self.case(record, "RC-009")
        reordered = ["unknown-issuer", "expired", "generation-mismatch"]
        reordered += ["viewer-mismatch", "authorization-revision-moved"]

        self.assertEqual(
            self.validator.evaluate_cursor(case, record["refusal_order"]),
            "viewer-mismatch",
        )
        self.assertEqual(
            self.validator.evaluate_cursor(case, reordered), "generation-mismatch"
        )

    def test_a_cursor_whose_record_does_not_validate_fails(self) -> None:
        record = self.read(VECTORS)
        case = copy.deepcopy(self.case(record, "RC-001"))
        case["case_id"] = "RC-010"
        case["cursor"]["bound_viewer"] = {
            "principal_kind": "anonymous",
            "ranked_identity_id": "aa11bb22-cc33-4d44-8e55-ff6677889900",
        }
        record["cases"].append(case)
        self.write(VECTORS, record)

        self.assert_fails(self.check, "RC-010 cursor")

    def test_losing_the_one_active_generation_index_fails(self) -> None:
        self.edit_text(
            SQL,
            "create unique index ranking_projection_generations_active_idx",
            "create index ranking_projection_generations_active_idx",
        )

        self.assert_fails(self.check, "no partial unique index on the active")

    def test_an_entry_key_that_omits_the_generation_fails(self) -> None:
        self.edit_text(
            SQL,
            "unique (ranking_view_id, generation, erasure_domain_id)",
            "unique (ranking_view_id, erasure_domain_id)",
        )

        self.assert_fails(self.check, "does not key one participant per generation")

    def test_a_page_that_does_not_name_its_generation_fails(self) -> None:
        self.edit_text(
            "packages/schemas/openapi-v1.yaml",
            "        - cursor\n        - ranking_view_id\n        - generation\n",
            "        - cursor\n        - ranking_view_id\n",
        )

        self.assert_fails(self.check, "may omit the generation it renders")


if __name__ == "__main__":
    unittest.main()
