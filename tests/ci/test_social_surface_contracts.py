"""The board, presence and notification rules, and what happens when they drift.

`scripts/repository/validate_social_surface_contracts.py` passes on the repository
as it stands, which proves nothing on its own: a validator that checks a condition
already true and would also pass if it were false is decoration. Every test below
except the first breaks one artifact and requires the exact message the validator
owes for that break.

The drift each one injects is a defect that was real in this tree before PF-025,
PF-026 or PF-027, or the direct inverse of one. `blocked` was a terminal state on
`board-membership`; `BoardInvitationRequest.role` admitted `owner`;
`PresenceRenewalRequest` carried an `availability` the client chose; the idle
threshold was 300 seconds and the expiry 90; `notifications.retraction_reason_code`
admitted any string; and no artifact said which preference flag governed which
notification type.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_social_surface_contracts.py"


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_social_surface_contracts", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class SocialSurfaceFixtureMixin:
    """Owns a temporary copy of every artifact the validator reads.

    A mixin rather than a base `TestCase`: subclassing one would run every test in
    this file again per subclass, and a suite whose reported case count is a
    multiple of its real one has bitten this repository before.
    """

    def setUp(self) -> None:  # noqa: D102
        super().setUp()  # type: ignore[misc]
        self.validator = load_validator()
        directory = Path(tempfile.mkdtemp(prefix="social-surface-"))
        self.addCleanup(shutil.rmtree, directory, True)  # type: ignore[attr-defined]

        self.schemas = directory / "packages" / "schemas"
        self.schemas.mkdir(parents=True)
        self.conformance = directory / "conformance"
        (self.conformance / "p1140e").mkdir(parents=True)
        (self.conformance / "social").mkdir(parents=True)

        for name in (
            "planning-schema.sql",
            "openapi-v1.yaml",
            "state-machine-registry-v1.json",
            "policy-defaults-v1.json",
            "notification-delivery-v1.schema.json",
        ):
            shutil.copy(ROOT / "packages" / "schemas" / name, self.schemas / name)
        shutil.copy(
            ROOT / "conformance" / "p1140e" / "sql-race-plans-v1.json",
            self.conformance / "p1140e" / "sql-race-plans-v1.json",
        )
        shutil.copy(
            ROOT / "conformance" / "social" / "presence-merge-vectors.json",
            self.conformance / "social" / "presence-merge-vectors.json",
        )

        self.sql = self.schemas / "planning-schema.sql"
        self.openapi = self.schemas / "openapi-v1.yaml"
        self.registry = self.schemas / "state-machine-registry-v1.json"
        self.policies = self.schemas / "policy-defaults-v1.json"
        self.notification = self.schemas / "notification-delivery-v1.schema.json"
        self.merge = self.conformance / "social" / "presence-merge-vectors.json"
        self.races = self.conformance / "p1140e" / "sql-race-plans-v1.json"

    def run_validator(self) -> tuple[int, str]:
        module = self.validator
        with (
            patch.object(module, "SQL_PATH", self.sql),
            patch.object(module, "OPENAPI", self.openapi),
            patch.object(module, "REGISTRY", self.registry),
            patch.object(module, "POLICIES", self.policies),
            patch.object(module, "NOTIFICATION", self.notification),
            patch.object(module, "MERGE_VECTORS", self.merge),
            patch.object(module, "CONFORMANCE", self.conformance),
            patch("sys.stdout", new_callable=_Capture) as captured,
        ):
            code = module.main()
        return code, captured.text

    # -- mutation helpers ---------------------------------------------------

    def edit_text(self, path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1, old)  # type: ignore[attr-defined]
        path.write_text(text.replace(old, new), encoding="utf-8")

    def edit_json(self, path: Path, mutate) -> None:
        document = json.loads(path.read_text(encoding="utf-8"))
        mutate(document)
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")

    def machine(self, document: dict, machine_id: str) -> dict:
        return next(
            item for item in document["machines"] if item["machine_id"] == machine_id
        )

    def expect_failure(self, fragment: str) -> None:
        code, output = self.run_validator()
        self.assertEqual(code, 1, output)  # type: ignore[attr-defined]
        self.assertIn(fragment, output)  # type: ignore[attr-defined]


class _Capture:
    """A stdout stand-in, because the validator reports by printing."""

    def __init__(self) -> None:
        self.text = ""

    def write(self, chunk: str) -> int:
        self.text += chunk
        return len(chunk)

    def flush(self) -> None:
        return None


class HeadStateTests(SocialSurfaceFixtureMixin, unittest.TestCase):
    def test_repository_head_passes(self) -> None:
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)


class BoardBlockIndependenceTests(SocialSurfaceFixtureMixin, unittest.TestCase):
    def test_a_terminal_blocked_membership_state_fails(self) -> None:
        """The defect as found: `blocked`, terminal, reached by a block-cascade."""
        self.edit_json(
            self.registry,
            lambda document: self.machine(document, "board-membership")[
                "states"
            ].append("blocked"),
        )
        self.expect_failure("board-membership declares the block-caused state")

    def test_reintroducing_the_block_cascade_transition_fails(self) -> None:
        def mutate(document: dict) -> None:
            machine = self.machine(document, "board-membership")
            machine["states"].append("blocked")
            machine["terminal_states"].append("blocked")
            machine["transitions"].append(
                {
                    "transition_id": "board-membership-block",
                    "from": ["active-member"],
                    "action": "block-cascade",
                    "to": "blocked",
                    "actor": "user",
                    "authentication": "web-session",
                    "recent_auth": False,
                    "idempotency": "principal-route-key",
                    "audit_event": "board-membership-block.audit",
                    "reversal": "none",
                    "transaction_boundary": "board-membership",
                }
            )

        self.edit_json(self.registry, mutate)
        self.expect_failure("declares a block-cascade transition")

    def test_a_block_caused_invitation_state_fails(self) -> None:
        self.edit_json(
            self.registry,
            lambda document: self.machine(document, "board-invitation")[
                "states"
            ].append("invalidated-by-block"),
        )
        self.expect_failure("board-invitation declares the block-caused state")

    def test_removing_a_state_that_strands_another_fails(self) -> None:
        """The repair must not be a deletion that orphans the rest of the machine."""

        def mutate(document: dict) -> None:
            machine = self.machine(document, "board-membership")
            machine["transitions"] = [
                item
                for item in machine["transitions"]
                if item["transition_id"] != "board-join-viewer"
            ]

        self.edit_json(self.registry, mutate)
        self.expect_failure("board-membership has unreachable states")

    def test_a_block_race_plan_that_deletes_the_friendship_fails(self) -> None:
        """The pre-D-585 model as the plan still recorded it."""

        def mutate(document: dict) -> None:
            case = next(
                item for item in document["cases"] if item["case_id"] == "block-race"
            )
            for row in case["residual_rows"]:
                if row["table"] == "friend_edges":
                    row["presence"] = "absent"
                    row.pop("columns", None)

        self.edit_json(self.races, mutate)
        self.expect_failure("the block-race plan removes friend_edges on a block")


class BoardAuthorityTests(SocialSurfaceFixtureMixin, unittest.TestCase):
    def test_an_invitation_that_can_grant_owner_fails(self) -> None:
        """The wire enum as found: owner, admin, member, viewer."""
        self.edit_text(
            self.openapi,
            "        role:\n          enum:\n            - member\n            - viewer",
            "        role:\n          enum:\n            - owner\n            - member\n            - viewer",
        )
        self.expect_failure("an invitation can grant 'owner'")

    def test_an_invite_table_with_no_role_column_fails(self) -> None:
        """The record half of the same defect: nothing to refuse with."""
        self.edit_text(
            self.sql,
            "  role text not null check (role in ('member','viewer')),\n  state text not null check (state in ('pending','accepted','declined','expired','revoked')),",
            "  state text not null check (state in ('pending','accepted','declined','expired','revoked')),",
        )
        self.expect_failure("board_invites.role has no CHECK")

    def test_an_invite_table_with_no_invitee_fails(self) -> None:
        self.edit_text(
            self.sql,
            "  invited_account_id uuid not null references accounts(account_id),\n",
            "",
        )
        self.expect_failure("board_invites declares no invited_account_id column")

    def test_a_board_kind_enum_missing_hacker_house_fails(self) -> None:
        """The vocabulary mismatch as found: three on the wire, four in the SQL."""
        self.edit_text(
            self.openapi,
            "        kind:\n          enum:\n            - private\n            - organization\n            - hacker-house\n            - community\n        name:\n          type: string\n          minLength: 1\n          maxLength: 100\n        visibility:\n          enum:\n            - public\n            - unlisted\n            - invite-only\n            - private\n        membership_revision:",
            "        kind:\n          enum:\n            - private\n            - organization\n            - community\n        name:\n          type: string\n          minLength: 1\n          maxLength: 100\n        visibility:\n          enum:\n            - public\n            - unlisted\n            - invite-only\n            - private\n        membership_revision:",
        )
        self.expect_failure("Board.kind differs from boards.board_type")

    def test_a_boards_table_with_no_visibility_fails(self) -> None:
        self.edit_text(
            self.sql,
            "  visibility text not null check (visibility in ('public','unlisted','invite-only','private')),\n",
            "",
        )
        self.expect_failure("boards.visibility does not carry the four values")

    def test_removing_the_owner_demotion_transition_fails(self) -> None:
        """The transfer plan's residual row needs a transition to be reachable."""

        def mutate(document: dict) -> None:
            machine = self.machine(document, "board-membership")
            machine["transitions"] = [
                item
                for item in machine["transitions"]
                if item["transition_id"] != "board-demote-owner"
            ]

        self.edit_json(self.registry, mutate)
        self.expect_failure(
            "board-membership declares no transition out of active-owner"
        )

    def test_promoting_to_admin_without_recent_auth_fails(self) -> None:
        def mutate(document: dict) -> None:
            for item in self.machine(document, "board-membership")["transitions"]:
                if item["transition_id"] == "board-promote-admin":
                    item["recent_auth"] = False

        self.edit_json(self.registry, mutate)
        self.expect_failure(
            "board-membership grants a privileged role without recent authentication"
        )

    def test_removing_the_board_creation_plan_fails(self) -> None:
        def mutate(document: dict) -> None:
            document["cases"] = [
                item
                for item in document["cases"]
                if item["case_id"] != "board-create-owner"
            ]

        self.edit_json(self.races, mutate)
        self.expect_failure("no board-create-owner race plan")


class PresenceEvidenceTests(SocialSurfaceFixtureMixin, unittest.TestCase):
    def test_a_client_selected_availability_fails(self) -> None:
        """The defect as found: the renewal body's only field was a state."""
        self.edit_text(
            self.openapi,
            "      required:\n        - device_id\n        - lease_generation\n        - qualifying\n      properties:\n        device_id:",
            "      required:\n        - device_id\n        - lease_generation\n        - qualifying\n      properties:\n        availability:\n          enum:\n            - online\n            - idle\n            - offline\n        device_id:",
        )
        self.expect_failure("PresenceRenewalRequest declares availability")

    def test_a_renewal_that_does_not_require_the_generation_fails(self) -> None:
        self.edit_text(
            self.openapi,
            "        - device_id\n        - lease_generation\n        - qualifying\n",
            "        - device_id\n        - qualifying\n",
        )
        self.expect_failure("PresenceRenewalRequest does not require lease_generation")

    def test_a_session_cookie_on_the_pulse_route_fails(self) -> None:
        """A browser or ordinary web session cannot fabricate indefinite activity."""
        self.edit_text(
            self.openapi,
            "      operationId: renewPresence\n      description:",
            "      operationId: renewPresence\n      x-drift: injected\n      description:",
        )
        self.edit_text(
            self.openapi,
            "      x-idempotency: required-durable-request-hash\n      security:\n        - bearerAuth: []\n          deviceProof: []\n      responses:\n        '200':\n          description: PresenceLease",
            "      x-idempotency: required-durable-request-hash\n      security:\n        - sessionCookie: []\n          csrfToken: []\n        - bearerAuth: []\n          deviceProof: []\n      responses:\n        '200':\n          description: PresenceLease",
        )
        self.expect_failure("renewPresence admits a credential without device proof")

    def test_the_swapped_presence_thresholds_fail(self) -> None:
        """The values as found under two misnamed keys: idle 300, expiry 90."""

        def mutate(document: dict) -> None:
            policies = document["policies"]
            policies["presence_idle_after_seconds"]["value"] = 300
            policies["presence_offline_after_seconds"]["value"] = 90

        self.edit_json(self.policies, mutate)
        self.expect_failure("is not strictly before the offline threshold")

    def test_per_device_presence_visibility_fails(self) -> None:
        self.edit_text(
            self.sql,
            "  lease_generation bigint not null default 0 check (lease_generation >= 0),\n  revision integer not null default 1 check (revision > 0),\n  last_qualifying_pulse_at timestamptz,",
            "  lease_generation bigint not null default 0 check (lease_generation >= 0),\n  visibility text not null default 'authorized-viewers',\n  revision integer not null default 1 check (revision > 0),\n  last_qualifying_pulse_at timestamptz,",
        )
        self.expect_failure("presence_leases carries a visibility column")

    def test_an_order_dependent_merge_fails(self) -> None:
        """A merge that answers differently by device order is not a merge."""

        def mutate(document: dict) -> None:
            document["merge_rule"]["precedence"] = ["active", "active", "idle"]

        self.edit_json(self.merge, mutate)
        self.expect_failure("the merge precedence repeats a state")

    def test_a_merge_rule_that_disagrees_with_its_cases_fails(self) -> None:
        def mutate(document: dict) -> None:
            document["merge_rule"]["precedence"] = [
                "expired",
                "revoked",
                "absent",
                "active",
                "idle",
            ]

        self.edit_json(self.merge, mutate)
        self.expect_failure("SO-201: the merge yields offline and the case expects")


class NotificationCategoryTests(SocialSurfaceFixtureMixin, unittest.TestCase):
    def test_an_event_type_with_no_category_fails(self) -> None:
        """`compatibility` and `release` were in exactly this position."""

        def mutate(document: dict) -> None:
            categories = document["$defs"]["event_categories"]
            categories["properties"].pop("release")
            categories["required"].remove("release")

        self.edit_json(self.notification, mutate)
        self.expect_failure("event_categories does not name every event type")

    def test_a_category_with_no_preference_column_fails(self) -> None:
        def mutate(document: dict) -> None:
            document["$defs"]["event_categories"]["properties"]["release"]["const"] = (
                "announcements"
            )

        self.edit_json(self.notification, mutate)
        self.expect_failure("the preferences record declares no announcements_enabled")

    def test_remapping_security_to_a_mutable_category_fails(self) -> None:
        """Whether a security notice can be muted must not be an assumption."""

        def mutate(document: dict) -> None:
            categories = document["$defs"]["event_categories"]["properties"]
            categories["security"]["const"] = "social"

        self.edit_json(self.notification, mutate)
        self.expect_failure("the security event type does not map to the security")

    def test_dropping_the_preference_column_fails(self) -> None:
        self.edit_text(self.sql, "  product_enabled boolean not null,\n", "")
        self.expect_failure(
            "notification_preferences declares no product_enabled column"
        )

    def test_an_unconstrained_retraction_reason_fails(self) -> None:
        """The column as found: `retraction_reason_code text`, any string."""
        body = self.sql.read_text(encoding="utf-8")
        match = re.search(
            r"  retraction_reason_code text check \(retraction_reason_code in \([^)]*\)\),",
            body,
        )
        assert match is not None
        self.sql.write_text(
            body.replace(match.group(0), "  retraction_reason_code text,"),
            encoding="utf-8",
        )
        self.expect_failure("do not carry the same registered codes")

    def test_removing_the_preferences_operation_fails(self) -> None:
        self.edit_text(
            self.openapi,
            "      operationId: updateNotificationPreferences",
            "      operationId: replaceNotificationPreferences",
        )
        self.expect_failure("the API declares no updateNotificationPreferences")

    def test_a_settable_security_flag_fails(self) -> None:
        self.edit_text(
            self.openapi,
            "    NotificationPreferencesUpdate:\n      description:",
            "    NotificationPreferencesUpdate:\n      x-drift: injected\n      description:",
        )
        self.edit_text(
            self.openapi,
            "      required:\n        - social_enabled\n        - ranking_enabled\n        - moderation_enabled\n        - product_enabled\n        - timezone_name\n      properties:\n        social_enabled:\n          type: boolean",
            "      required:\n        - social_enabled\n        - ranking_enabled\n        - moderation_enabled\n        - product_enabled\n        - timezone_name\n      properties:\n        security_enabled:\n          type: boolean\n        social_enabled:\n          type: boolean",
        )
        self.expect_failure("NotificationPreferencesUpdate accepts security_enabled")


if __name__ == "__main__":
    unittest.main()
