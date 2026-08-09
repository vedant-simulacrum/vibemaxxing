"""PF-021. The ranking definition and the audience are two things.

`ranking-view-v1.schema.json` was one flat object with `scope` and `board_id` beside
`period_id` and `rules_digest`, and `ranking_view_id` was a digest over the lot with
no name for either half. Two audiences of one ranking could not be said to be that,
and a view identifier that omitted the audience could not be refused — which is the
shape in which a global and a friends board collapse onto one sealed generation.

Each case injects one way the split can rot.
"""

from __future__ import annotations

import copy
import unittest

from .planning_fixtures import PlanningValidatorMixin

SCHEMA = "packages/schemas/ranking-view-v1.schema.json"
EXAMPLES = "packages/schemas/examples"
GLOBAL = f"{EXAMPLES}/ranking-view.valid.json"
FRIENDS = (
    f"{EXAMPLES}/ranking-view.valid-friends-audience-over-the-same-definition.json"
)
OMITS = f"{EXAMPLES}/ranking-view.invalid-view-id-omits-the-audience.json"


class RankingViewSeparationTests(PlanningValidatorMixin, unittest.TestCase):
    def check(self) -> None:
        self.validator.validate_ranking_view_separation()

    def test_the_committed_tree_passes(self) -> None:
        self.assert_passes(self.check)

    def test_the_two_audiences_share_one_definition(self) -> None:
        """The property the split exists for, asserted directly."""
        first = self.read(GLOBAL)
        second = self.read(FRIENDS)
        self.assertEqual(
            first["definition"]["ranking_definition_id"],
            second["definition"]["ranking_definition_id"],
        )
        self.assertNotEqual(first["ranking_view_id"], second["ranking_view_id"])

    def test_an_audience_field_moved_into_the_definition_fails(self) -> None:
        schema = self.read(SCHEMA)
        definition = schema["$defs"]["ranking_definition"]
        definition["properties"]["scope"] = {"enum": ["global", "friends"]}
        self.write(SCHEMA, schema)

        self.assert_fails(self.check, "differ from the declared partition")

    def test_a_definition_field_moved_into_the_audience_fails(self) -> None:
        schema = self.read(SCHEMA)
        schema["$defs"]["audience"]["properties"]["rules_digest"] = {"type": "string"}
        self.write(SCHEMA, schema)

        self.assert_fails(self.check, "differ from the declared partition")

    def test_a_view_id_that_omits_the_audience_fails(self) -> None:
        record = self.read(FRIENDS)
        record["ranking_view_id"] = record["definition"]["ranking_definition_id"]
        self.write(FRIENDS, record)

        self.assert_fails(self.check, "does not bind both halves")

    def test_two_audiences_collapsing_to_one_view_id_fails(self) -> None:
        """The consequence: one sealed generation serving two audiences."""
        record = self.read(GLOBAL)
        friends = self.read(FRIENDS)
        friends["audience"] = copy.deepcopy(record["audience"])
        friends["ranking_view_id"] = record["ranking_view_id"]
        self.write(FRIENDS, friends)

        self.assert_fails(self.check, "carries scope")

    def test_a_declared_audience_example_that_is_deleted_fails(self) -> None:
        """The signal must not improve when the thing it counts is removed."""
        self.path(FRIENDS).unlink()

        self.assert_fails(self.check, "differ from the declared set")

    def test_the_negative_that_stops_being_negative_fails(self) -> None:
        record = self.read(OMITS)
        record["ranking_view_id"] = self.read(FRIENDS)["ranking_view_id"]
        self.write(OMITS, record)

        self.assert_fails(self.check, "has stopped being the negative")

    def test_an_authorization_input_the_profile_does_not_declare_fails(self) -> None:
        schema = self.read(SCHEMA)
        inputs = schema["$defs"]["audience"]["properties"]["authorization_inputs"]
        inputs["items"]["enum"].append("vibes-based-allow")
        self.write(SCHEMA, schema)

        self.assert_fails(self.check, "differ from")

    def test_the_write_site_losing_the_public_only_global_rule_fails(self) -> None:
        self.edit_text(
            "packages/schemas/planning-schema.sql",
            "check ((scope = 'global') = (default_visibility = 'universally-public'))",
            "check (default_visibility in ('universally-public','viewer-authorized'))",
        )

        self.assert_fails(self.check, "lacks its required ranking-view invariant")

    def test_the_definition_table_growing_an_audience_column_fails(self) -> None:
        self.edit_text(
            "packages/schemas/planning-schema.sql",
            "  metric text not null check (metric = 'credited-token-burn'),",
            "  metric text not null check (metric = 'credited-token-burn'),\n"
            "  scope text not null,",
        )

        self.assert_fails(self.check, "carries the audience column")

    def test_the_public_scope_readmitting_global_fails(self) -> None:
        self.edit_text(
            "packages/schemas/openapi-v1.yaml",
            "      schema:\n        enum:\n          - friends\n          - rivals",
            "      schema:\n        enum:\n          - global\n          - friends\n"
            "          - rivals",
        )

        self.assert_fails(self.check, "still admits 'global'")

    def test_the_global_board_reason_held_by_two_operations_fails(self) -> None:
        self.edit_text(
            "packages/schemas/openapi-v1.yaml",
            "  getGlobalLeaderboard: global-board",
            "  getGlobalLeaderboard: global-board\n  getLeaderboard: global-board",
        )

        self.assert_fails(self.check, "the global-board reason is held by")

    def test_rank_entry_readmitting_an_imported_record_fails(self) -> None:
        self.edit_text(
            "packages/schemas/openapi-v1.yaml",
            "        evidence_class:\n          enum:\n            - hardened\n"
            "            - standard\n          description: 'The awarded public "
            "evidence state from packages/schemas/evidence-profile-policy-v1.json. "
            "The server verifier assigns it; a client field requesting one is ignored "
            "under the policy''s client-requested-public-state rule. Under ADR-020 the "
            "class is a weight on Credited Token Burn rather than a badge, and under "
            "D-100 no provider offers an individual-account attestation path, so the "
            "class assesses the quality of a self-report and is not a confirmation "
            "from any provider. `imported` is absent on a ranking entry",
            "        evidence_class:\n          enum:\n            - hardened\n"
            "            - standard\n            - imported\n          description: "
            "'`imported` is absent on a ranking entry",
        )

        self.assert_fails(self.check, "admits the imported evidence class")


if __name__ == "__main__":
    unittest.main()
