"""PF-033. The current-authorization rule is total over the API it governs.

SR-015 asks for one enumerated boundary matrix plus a current-authorization check at
every boundary it names. Before this unit the profile named nine inputs and nine
surfaces and resolved neither against the document that declares the boundaries, so
three things were true at once and none was findable by anything: `board-member-list`
was a rule about a surface no operation renders, `listBlocks` rendered a third party's
account identifier with no surface at all, and one `leaderboard-page` claimed nine
read-time inputs on behalf of `getGlobalLeaderboard`, which carries `security: []`.

Each case injects one way the matrix, the corpus or the document it is derived from
can rot, and asserts the exact substring the validator answers with. The cases that
matter most are the ones where a field or an operation is *added*: a rule derived from
the document fails on a new operation with no boundary and on a new viewer-visible
field with no gate, and a hand-list would pass both.
"""

from __future__ import annotations

import unittest

from .planning_fixtures import PlanningValidatorMixin

PROFILE = "packages/schemas/projection-authorization-v1.json"
DISCLOSURE = "packages/schemas/disclosure-projection-v1.json"
VECTORS = "conformance/planning/authorization-invalidation-vectors-v1.json"
API = "packages/schemas/openapi-v1.yaml"


class AuthorizationBoundaryTests(PlanningValidatorMixin, unittest.TestCase):
    def check(self) -> None:
        self.validator.validate_authorization_boundaries()

    # -- helpers ------------------------------------------------------------

    def surface(self, profile: dict, surface_id: str) -> dict:
        return next(
            item for item in profile["surfaces"] if item["surface_id"] == surface_id
        )

    def boundary(self, profile: dict, operation_id: str) -> dict:
        return next(
            item
            for item in profile["boundaries"]
            if item["operation_id"] == operation_id
        )

    def resync_corpus(self, profile: dict) -> None:
        """Rewrite the corpus from the profile.

        Used only by the cases that change the profile's *structure* — the artifact
        set or what an artifact binds — where leaving the recorded expectations behind
        would fail on the mismatch rather than on the property under test.
        """
        triggers = {
            item["trigger_id"]: item for item in profile["invalidation_triggers"]
        }
        record = self.read(VECTORS)
        for case in record["cases"]:
            case["expected"] = self.validator.evaluate_invalidation(
                triggers[case["trigger"]], profile
            )
        self.write(VECTORS, record)

    # -- the committed tree -------------------------------------------------

    def test_the_committed_tree_passes(self) -> None:
        self.assert_passes(self.check)

    def test_every_api_operation_has_exactly_one_boundary(self) -> None:
        profile = self.read(PROFILE)
        identifiers = [item["operation_id"] for item in profile["boundaries"]]

        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertIn("getGlobalLeaderboard", identifiers)
        self.assertIn("listBlocks", identifiers)

    def test_the_global_board_is_a_surface_of_its_own(self) -> None:
        """The split PF-033 made. One operation has no viewer; two do."""
        profile = self.read(PROFILE)
        surface = self.surface(profile, "global-leaderboard-page")

        self.assertTrue(surface["universally_public"])
        self.assertNotIn("directional-block", surface["authorization_inputs"])
        self.assertEqual(
            self.boundary(profile, "getGlobalLeaderboard")["surface_id"],
            "global-leaderboard-page",
        )
        self.assertEqual(
            self.boundary(profile, "getLeaderboard")["surface_id"], "leaderboard-page"
        )

    def test_the_sealed_generation_survives_every_trigger(self) -> None:
        """The immutable-history half, evaluated rather than asserted in prose."""
        profile = self.read(PROFILE)
        for trigger in profile["invalidation_triggers"]:
            outcome = self.validator.evaluate_invalidation(trigger, profile)

            self.assertIn("sealed-generation-projection", outcome["retained_artifacts"])

    def test_only_deletion_reaches_the_export_download_grant(self) -> None:
        profile = self.read(PROFILE)
        reaching = [
            trigger["trigger_id"]
            for trigger in profile["invalidation_triggers"]
            if "export-download-grant"
            in self.validator.evaluate_invalidation(trigger, profile)[
                "invalidated_artifacts"
            ]
        ]

        self.assertEqual(reaching, ["account-deletion-requested"])

    # -- boundary coverage --------------------------------------------------

    def test_an_operation_with_no_boundary_fails(self) -> None:
        """The check a hand-list cannot make: an operation added later escapes it."""
        profile = self.read(PROFILE)
        profile["boundaries"] = [
            item
            for item in profile["boundaries"]
            if item["operation_id"] != "getPublicProfile"
        ]
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check, "does not cover the API operations ['getPublicProfile']"
        )

    def test_a_boundary_for_no_operation_fails(self) -> None:
        profile = self.read(PROFILE)
        profile["boundaries"].append(
            {
                "operation_id": "getSomethingElse",
                "response_schema": "PublicProfile",
                "subject": "first-party",
            }
        )
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "names operations the API does not declare: ['getSomethingElse']",
        )

    def test_two_boundaries_for_one_operation_fail(self) -> None:
        profile = self.read(PROFILE)
        profile["boundaries"].append(dict(self.boundary(profile, "getMe")))
        self.write(PROFILE, profile)

        self.assert_fails(self.check, "boundary operations")

    def test_a_boundary_naming_the_wrong_response_shape_fails(self) -> None:
        profile = self.read(PROFILE)
        self.boundary(profile, "getPublicProfile")["response_schema"] = "AccountProfile"
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "names the response schema AccountProfile and the API returns PublicProfile",
        )

    def test_an_operation_with_two_success_shapes_fails(self) -> None:
        """A boundary cannot name the shape it gates if there are two of them."""
        self.edit_text(
            API,
            "        '200':\n"
            "          description: PublicProfile\n"
            "          content:\n"
            "            application/json:\n"
            "              schema:\n"
            "                $ref: '#/components/schemas/PublicProfile'\n",
            "        '200':\n"
            "          description: PublicProfile\n"
            "          content:\n"
            "            application/json:\n"
            "              schema:\n"
            "                $ref: '#/components/schemas/PublicProfile'\n"
            "        '203':\n"
            "          description: AccountProfile\n"
            "          content:\n"
            "            application/json:\n"
            "              schema:\n"
            "                $ref: '#/components/schemas/AccountProfile'\n",
        )

        self.assert_fails(
            self.check,
            "getPublicProfile does not have exactly one success response schema",
        )

    def test_a_boundary_naming_a_surface_the_profile_dropped_fails(self) -> None:
        profile = self.read(PROFILE)
        profile["surfaces"] = [
            item for item in profile["surfaces"] if item["surface_id"] != "rival-list"
        ]
        for artifact in profile["derived_artifacts"]:
            artifact["binds_surfaces"] = [
                surface
                for surface in artifact["binds_surfaces"]
                if surface != "rival-list"
            ]
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check, "boundary listRivals names an undeclared surface: rival-list"
        )

    # -- computed subject ---------------------------------------------------

    def test_declaring_a_third_party_response_first_party_fails(self) -> None:
        """A boundary cannot declare itself out of the gate it needs."""
        profile = self.read(PROFILE)
        boundary = self.boundary(profile, "listNotifications")
        boundary["subject"] = "first-party"
        del boundary["surface_id"]
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "declares subject first-party and the document computes third-party",
        )

    def test_declaring_a_first_party_response_third_party_fails(self) -> None:
        """And cannot declare itself into one it does not need."""
        profile = self.read(PROFILE)
        boundary = self.boundary(profile, "getMe")
        boundary["subject"] = "third-party"
        boundary["surface_id"] = "public-profile"
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "declares subject third-party and the document computes first-party",
        )

    def test_a_write_receipt_naming_another_account_is_third_party(self) -> None:
        """markNotificationRead is a write returning one object and is still gated.

        The ordering of the two subject rules is what decides this. A foreign account
        reference wins over the write-receipt rule, because the object it returns names
        the actor whose block state has to be rechecked before it is handed over again.
        """
        profile = self.read(PROFILE)

        self.assertEqual(
            self.boundary(profile, "markNotificationRead")["subject"], "third-party"
        )
        self.assertEqual(
            self.boundary(profile, "renewPresence")["subject"], "first-party"
        )
        self.assertEqual(
            self.boundary(profile, "getCurrentRank")["subject"], "first-party"
        )

    # -- surface input partition -------------------------------------------

    def test_a_surface_that_neither_evaluates_nor_excuses_an_input_fails(self) -> None:
        profile = self.read(PROFILE)
        surface = self.surface(profile, "public-profile")
        surface["authorization_inputs"] = [
            name for name in surface["authorization_inputs"] if name != "rival-edge"
        ]
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "surface public-profile does not partition the authorization inputs: "
            "unanswered=['rival-edge']",
        )

    def test_a_surface_evaluating_and_excusing_one_input_fails(self) -> None:
        profile = self.read(PROFILE)
        surface = self.surface(profile, "public-profile")
        surface["omitted_inputs"].append(
            {
                "input_id": "rival-edge",
                "reason": "a reason long enough to satisfy the schema minimum length",
            }
        )
        self.write(PROFILE, profile)

        self.assert_fails(self.check, "public-profile input assignments")

    def test_a_surface_that_skips_account_lifecycle_fails(self) -> None:
        profile = self.read(PROFILE)
        surface = self.surface(profile, "friend-list")
        surface["authorization_inputs"] = [
            name
            for name in surface["authorization_inputs"]
            if name != "account-lifecycle"
        ]
        surface["omitted_inputs"].append(
            {
                "input_id": "account-lifecycle",
                "reason": "a reason long enough to satisfy the schema minimum length",
            }
        )
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check, "surface friend-list does not evaluate account-lifecycle"
        )

    # -- the universally-public exemption -----------------------------------

    def test_the_global_board_claiming_a_pair_shaped_input_fails(self) -> None:
        """An anonymous reader has no block row, so the claim could never be run."""
        profile = self.read(PROFILE)
        surface = self.surface(profile, "global-leaderboard-page")
        surface["authorization_inputs"].append("directional-block")
        surface["omitted_inputs"] = [
            item
            for item in surface["omitted_inputs"]
            if item["input_id"] != "directional-block"
        ]
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "universally-public surface global-leaderboard-page claims to evaluate "
            "['directional-block']",
        )

    def test_a_second_universally_public_surface_fails(self) -> None:
        profile = self.read(PROFILE)
        self.surface(profile, "public-profile")["universally_public"] = True
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "the universally-public surface set differs from the one AGENTS.md allows",
        )

    def test_a_new_surface_skipping_the_block_fails(self) -> None:
        """Omitting a deny-hard input is a decision, so the set is held in the code."""
        profile = self.read(PROFILE)
        surface = self.surface(profile, "presence-projection")
        surface["authorization_inputs"] = [
            name
            for name in surface["authorization_inputs"]
            if name != "directional-block"
        ]
        surface["omitted_inputs"].append(
            {
                "input_id": "directional-block",
                "reason": "a reason long enough to satisfy the schema minimum length",
            }
        )
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "the surfaces that do not evaluate directional-block differ from the "
            "declared set: only-in-file=['presence-projection']",
        )

    # -- reachability -------------------------------------------------------

    def test_a_surface_no_operation_renders_fails(self) -> None:
        """`board-member-list` was exactly this, and it hid that listBlocks had none."""
        profile = self.read(PROFILE)
        self.boundary(profile, "listBlocks")["surface_id"] = "friend-list"
        for artifact in profile["derived_artifacts"]:
            artifact["binds_surfaces"] = [
                surface
                for surface in artifact["binds_surfaces"]
                if surface != "block-list"
            ]
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "surfaces reached by no boundary and no derived artifact: ['block-list']",
        )

    def test_a_shape_naming_another_account_with_no_audience_fails(self) -> None:
        profile = self.read(DISCLOSURE)
        profile["projections"] = [
            item
            for item in profile["projections"]
            if item["api_schema"] != "Relationship"
        ]
        self.write(DISCLOSURE, profile)

        self.assert_fails(
            self.check,
            "Relationship names another account through ['peer_account_id'] and the "
            "disclosure projection does not classify it",
        )

    # -- the viewer-visible field matrix ------------------------------------

    def test_a_field_added_to_a_projected_shape_must_be_gated(self) -> None:
        """The case the acceptance turns on. A hand-listed matrix would pass this."""
        anchor = (
            "        top_model_alias:\n"
            "          type:\n"
            "            - string\n"
            "            - 'null'\n"
            "          minLength: 1\n"
            "          maxLength: 64\n"
            "        ranking_view_id:"
        )
        self.edit_text(
            API,
            anchor,
            "        side_channel:\n"
            "          type:\n"
            "            - string\n"
            "            - 'null'\n" + anchor,
        )
        disclosure = self.read(DISCLOSURE)
        entry = next(
            item
            for item in disclosure["projections"]
            if item["api_schema"] == "RankEntry"
        )
        entry["fields"].append(
            {
                "name": "side_channel",
                "audience": "public",
                "classification": "derived-personal",
            }
        )
        self.write(DISCLOSURE, disclosure)

        self.assert_fails(
            self.check,
            "the viewer-visible field matrix omits [('global-leaderboard-page', "
            "'RankEntry', 'side_channel')",
        )

    def test_a_removed_matrix_row_fails(self) -> None:
        profile = self.read(PROFILE)
        profile["viewer_visible_fields"] = [
            row
            for row in profile["viewer_visible_fields"]
            if not (row["surface_id"] == "public-profile" and row["field"] == "handle")
        ]
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "the viewer-visible field matrix omits [('public-profile', "
            "'PublicProfile', 'handle')]",
        )

    def test_a_matrix_row_the_document_does_not_publish_fails(self) -> None:
        profile = self.read(PROFILE)
        profile["viewer_visible_fields"].append(
            {
                "surface_id": "friend-list",
                "api_schema": "PublicProfile",
                "field": "handle",
                "gated_by": ["accounts.state"],
            }
        )
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "names rows the document does not publish: [('friend-list', "
            "'PublicProfile', 'handle')]",
        )

    def test_a_row_gated_on_the_wrong_revisions_fails(self) -> None:
        profile = self.read(PROFILE)
        row = next(
            item
            for item in profile["viewer_visible_fields"]
            if item["surface_id"] == "public-profile" and item["field"] == "handle"
        )
        row["gated_by"] = ["accounts.state"]
        self.write(PROFILE, profile)

        self.assert_fails(self.check, "and the surface rechecks")

    def test_narrowing_a_surface_regates_every_field_it_renders(self) -> None:
        """The gate is the surface's input set, so it cannot drift from it."""
        profile = self.read(PROFILE)
        surface = self.surface(profile, "public-profile")
        surface["authorization_inputs"] = [
            name for name in surface["authorization_inputs"] if name != "rival-edge"
        ]
        surface["omitted_inputs"].append(
            {
                "input_id": "rival-edge",
                "reason": "a reason long enough to satisfy the schema minimum length",
            }
        )
        self.write(PROFILE, profile)

        self.assert_fails(self.check, "and the surface rechecks")

    def test_a_matrix_out_of_the_computed_order_fails(self) -> None:
        profile = self.read(PROFILE)
        profile["viewer_visible_fields"].reverse()
        self.write(PROFILE, profile)

        self.assert_fails(self.check, "is not in the computed order")

    # -- the cache arm ------------------------------------------------------

    def test_a_document_with_no_cache_policy_fails(self) -> None:
        self.edit_text(
            API, "\nx-response-cache-policy:", "\nx-response-cache-policy-was:"
        )

        self.assert_fails(self.check, "the API declares no x-response-cache-policy")

    def test_making_a_viewer_relative_response_shared_cacheable_fails(self) -> None:
        self.edit_text(
            API, "  getPublicProfile: no-store", "  getPublicProfile: public-shared"
        )

        self.assert_fails(
            self.check,
            "x-response-cache-policy disagrees with the reason x-public-operations "
            "gives for ['getPublicProfile']",
        )

    def test_an_auth_bootstrap_response_may_not_be_shared_cached(self) -> None:
        """Public because it establishes a session, not because its body is."""
        self.edit_text(
            API, "  exchangeDeviceAuth: no-store", "  exchangeDeviceAuth: public-shared"
        )

        self.assert_fails(self.check, "gives for ['exchangeDeviceAuth']")

    def test_an_operation_with_no_cache_policy_fails(self) -> None:
        self.edit_text(API, "  listBlocks: no-store\n", "")

        self.assert_fails(
            self.check,
            "x-response-cache-policy does not cover exactly the declared operations: "
            "uncovered=['listBlocks']",
        )

    def test_a_policy_that_refuses_everything_fails(self) -> None:
        """A split satisfied by refusing both halves says nothing about the split."""
        self.edit_text(API, "  getGlobalLeaderboard: public-shared", "  getGlobalLeaderboard: no-store")
        self.edit_text(API, "  listPricingDatasets: public-shared", "  listPricingDatasets: no-store")
        self.edit_text(API, "  getCompatibility: public-shared", "  getCompatibility: no-store")
        self.edit_text(API, "  getGlobalLeaderboard: global-board", "  getGlobalLeaderboard: auth-bootstrap")
        self.edit_text(API, "  listPricingDatasets: reference-data", "  listPricingDatasets: auth-bootstrap")
        self.edit_text(API, "  getCompatibility: reference-data", "  getCompatibility: auth-bootstrap")

        self.assert_fails(self.check, "no operation is shared-cacheable")

    # -- the invalidation corpus -------------------------------------------

    def test_a_case_understating_what_it_destroys_fails(self) -> None:
        record = self.read(VECTORS)
        case = next(
            item for item in record["cases"] if item["trigger"] == "block-established"
        )
        case["expected"]["invalidated_artifacts"] = ["ranking-cursor"]
        self.write(VECTORS, record)

        self.assert_fails(
            self.check,
            "records invalidated_artifacts as ['ranking-cursor'] and the rule computes",
        )

    def test_a_case_overstating_what_it_destroys_fails(self) -> None:
        record = self.read(VECTORS)
        case = next(
            item
            for item in record["cases"]
            if item["trigger"] == "board-membership-removed"
        )
        case["expected"]["invalidated_artifacts"].append("export-download-grant")
        self.write(VECTORS, record)

        self.assert_fails(self.check, "records invalidated_artifacts as")

    def test_a_case_understating_which_surfaces_it_reaches_fails(self) -> None:
        record = self.read(VECTORS)
        case = next(
            item for item in record["cases"] if item["trigger"] == "block-established"
        )
        case["expected"]["affected_surfaces"] = ["public-profile"]
        self.write(VECTORS, record)

        self.assert_fails(self.check, "records affected_surfaces as ['public-profile']")

    def test_a_trigger_with_no_case_fails(self) -> None:
        """A signal that improves when the thing it counts is removed."""
        record = self.read(VECTORS)
        record["cases"] = [
            item
            for item in record["cases"]
            if item["trigger"] != "account-deletion-requested"
        ]
        self.write(VECTORS, record)

        self.assert_fails(
            self.check,
            "no case exercises the triggers ['account-deletion-requested']",
        )

    def test_an_input_no_trigger_moves_fails(self) -> None:
        profile = self.read(PROFILE)
        profile["invalidation_triggers"] = [
            item
            for item in profile["invalidation_triggers"]
            if "presence-visibility" not in item["changes_inputs"]
        ]
        self.write(PROFILE, profile)
        record = self.read(VECTORS)
        record["cases"] = [
            item
            for item in record["cases"]
            if item["trigger"] != "presence-visibility-narrowed"
        ]
        self.write(VECTORS, record)
        self.resync_corpus(profile)

        self.assert_fails(
            self.check,
            "no trigger moves the authorization inputs ['presence-visibility']",
        )

    def test_dropping_the_grant_kind_fails(self) -> None:
        """The acceptance names cursors, grants and caches; an absent kind is none."""
        profile = self.read(PROFILE)
        next(
            item
            for item in profile["derived_artifacts"]
            if item["artifact_id"] == "export-download-grant"
        )["kind"] = "cache"
        self.write(PROFILE, profile)

        self.assert_fails(self.check, "does not name a cursor, a grant and a cache")

    def test_dropping_the_authorization_independent_artifact_fails(self) -> None:
        profile = self.read(PROFILE)
        profile["derived_artifacts"] = [
            item
            for item in profile["derived_artifacts"]
            if item["artifact_id"] != "sealed-generation-projection"
        ]
        self.write(PROFILE, profile)
        self.resync_corpus(profile)

        self.assert_fails(
            self.check, "no derived artifact is authorization-independent"
        )

    def test_a_kind_no_trigger_reaches_fails(self) -> None:
        """An artifact excused from invalidation leaves its whole kind unexercised."""
        profile = self.read(PROFILE)
        next(
            item
            for item in profile["derived_artifacts"]
            if item["artifact_id"] == "export-download-grant"
        )["authorization_independent"] = True
        self.write(PROFILE, profile)
        self.resync_corpus(profile)

        self.assert_fails(
            self.check, "no case invalidates an artifact of kind grant"
        )

    def test_a_corpus_where_every_trigger_destroys_everything_fails(self) -> None:
        profile = self.read(PROFILE)
        for artifact in profile["derived_artifacts"]:
            if not artifact["authorization_independent"]:
                artifact["binds_surfaces"] = sorted(
                    {"leaderboard-page", *artifact["binds_surfaces"]}
                )
        self.write(PROFILE, profile)
        self.resync_corpus(profile)

        self.assert_fails(
            self.check, "cannot tell a trigger's blast radius from the whole set"
        )

    def test_an_artifact_binding_an_undeclared_surface_fails(self) -> None:
        """`export-package` is reachable only through the grant that delivers it."""
        profile = self.read(PROFILE)
        profile["surfaces"] = [
            item
            for item in profile["surfaces"]
            if item["surface_id"] != "export-package"
        ]
        self.write(PROFILE, profile)

        self.assert_fails(
            self.check,
            "derived artifact export-download-grant binds undeclared surfaces: "
            "['export-package']",
        )


if __name__ == "__main__":
    unittest.main()
