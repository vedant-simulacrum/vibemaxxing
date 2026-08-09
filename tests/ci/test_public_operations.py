"""An operation is public only if it is declared public, with an admissible reason.

`getPublicProfile` carried `security: []` while its own response schema described
"what a viewer authorized to read this profile receives", and
`packages/schemas/projection-authorization-v1.json` makes `directional-block` a
deny-hard input evaluated in both directions and `subject-visibility`
deny-unless-authorized.

An unauthenticated caller has no viewer identity, so neither input can be evaluated.
A blocked person could read the profile — including presence, friend count, board
count and top model alias — by logging out. That is block evasion, and nothing in the
repository objected, because writing `security: []` required no declaration and gave
no reason.

These tests inject each way the declaration can rot.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
OPENAPI = ROOT / "packages" / "schemas" / "openapi-v1.yaml"
AUTHORIZATION = ROOT / "packages" / "schemas" / "projection-authorization-v1.json"

ADMISSIBLE = {"auth-bootstrap", "global-board", "reference-data"}


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_planning_artifacts", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def operations(spec: dict) -> dict:
    found = {}
    for path, item in spec["paths"].items():
        for method, operation in item.items():
            if isinstance(operation, dict) and "operationId" in operation:
                found[operation["operationId"]] = operation
    return found


class PublicOperationDeclarationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
        cls.declared = cls.spec["x-public-operations"]
        cls.operations = operations(cls.spec)

    def test_every_public_operation_is_declared(self) -> None:
        public = {
            identifier
            for identifier, operation in self.operations.items()
            if operation.get("security") == []
        }
        self.assertEqual(public, set(self.declared))

    def test_every_declaration_carries_an_admissible_reason(self) -> None:
        for identifier, reason in self.declared.items():
            self.assertIn(reason, ADMISSIBLE, identifier)

    def test_exactly_one_declaration_is_a_board(self) -> None:
        """AGENTS.md: only global leaderboard views are universally public."""
        boards = [i for i, r in self.declared.items() if r == "global-board"]
        self.assertEqual(boards, ["getGlobalLeaderboard"])

    def test_the_global_board_operation_takes_no_scope(self) -> None:
        """PF-021's live defect: one reason covering four scopes.

        `getLeaderboard` held `global-board` while its path was
        `/leaderboards/{scope}/{period}` and `Scope` admitted `global`, `friends`,
        `rivals` and `board`. The declaration named one of the four values and
        covered all of them, so an unauthenticated caller reached a friends or a
        private-board standing by naming it in the path.
        """
        parameters = self.spec["components"]["parameters"]
        for identifier, reason in self.declared.items():
            if reason != "global-board":
                continue
            names = {
                parameters[item["$ref"].rsplit("/", 1)[1]]["name"]
                for item in self.operations[identifier].get("parameters", [])
                if isinstance(item, dict) and "$ref" in item
            }
            self.assertNotIn("scope", names, identifier)
        self.assertNotIn("global", parameters["Scope"]["schema"]["enum"])

    def test_the_cohort_and_board_boards_require_a_session(self) -> None:
        for identifier in ("getLeaderboard", "getBoardLeaderboard"):
            operation = self.operations[identifier]
            self.assertNotEqual(operation.get("security"), [])
            self.assertEqual(operation["x-authorization"], "authenticated-account")
            self.assertIn("401", operation["responses"])
            self.assertNotIn(identifier, self.declared)

    def test_the_board_leaderboard_names_the_board(self) -> None:
        """scope=board named no board. A key that omits its discriminator."""
        parameters = self.spec["components"]["parameters"]
        names = {
            parameters[item["$ref"].rsplit("/", 1)[1]]["name"]
            for item in self.operations["getBoardLeaderboard"].get("parameters", [])
            if isinstance(item, dict) and "$ref" in item
        }
        self.assertIn("id", names)
        self.assertNotIn("board", parameters["Scope"]["schema"]["enum"])

    def test_the_public_profile_requires_a_viewer(self) -> None:
        """The defect this unit exists to close: block evasion by logging out."""
        profile = self.operations["getPublicProfile"]

        self.assertNotEqual(profile.get("security"), [])
        self.assertEqual(profile["x-authorization"], "authenticated-account")
        self.assertIn("401", profile["responses"])
        self.assertNotIn("getPublicProfile", self.declared)

    def test_no_declared_public_operation_returns_a_viewer_relative_field(self) -> None:
        """A public operation may not carry a field the authorization profile gates.

        `availability` is server-derived presence and `friend_count` is a social
        projection; both are viewer-relative, and both sat on the unauthenticated
        profile response.
        """
        gated = {"availability", "friend_count", "board_count", "top_model_alias"}
        schemas = self.spec["components"]["schemas"]
        for identifier in self.declared:
            operation = self.operations[identifier]
            body = (
                operation["responses"]
                .get("200", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            reference = body.get("$ref", "")
            if not reference:
                continue
            properties = schemas.get(reference.rsplit("/", 1)[1], {}).get(
                "properties", {}
            )
            self.assertEqual(
                gated & set(properties), set(), f"{identifier} exposes a gated field"
            )


class InjectionTests(unittest.TestCase):
    """Each case removes or corrupts one half of the declaration."""

    def setUp(self) -> None:
        self.validator = load_validator()
        self.spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))

    def check(self, spec: dict) -> str:
        with self.assertRaises(self.validator.ValidationFailure) as raised:
            self.validator.validate_public_operations(spec)
        return str(raised.exception)

    def test_an_undeclared_public_operation_fails(self) -> None:
        spec = copy.deepcopy(self.spec)
        operations(spec)["getPublicProfile"]["security"] = []
        operations(spec)["getPublicProfile"]["x-authorization"] = "public"

        self.assertIn("public and undeclared", self.check(spec))

    def test_a_stale_declaration_fails(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["x-public-operations"]["listBoards"] = "reference-data"

        self.assertIn("does not carry security: []", self.check(spec))

    def test_a_free_text_reason_fails(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["x-public-operations"]["getGlobalLeaderboard"] = "it-is-fine-really"

        self.assertIn("is not one of", self.check(spec))

    def test_security_and_x_authorization_disagreeing_fails(self) -> None:
        spec = copy.deepcopy(self.spec)
        operations(spec)["getGlobalLeaderboard"]["x-authorization"] = (
            "authenticated-account"
        )

        self.assertIn("must agree", self.check(spec))


if __name__ == "__main__":
    unittest.main()
