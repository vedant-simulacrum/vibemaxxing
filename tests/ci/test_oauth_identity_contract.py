"""Drift-injection tests for the SR-006 cluster validator.

Each test breaks one input in a full copy of the tree and asserts the exact failure the
validator reports. A validator that has never been shown failing is a validator whose
green run means nothing, and the defects these inject are the ones PF-005 through PF-008
were written to remove: a capability claimed without an observation, an `iss` parameter
that follows the provider rather than the recorded capability, a bare authorization code
reaching an identity mutation, a snake_case vocabulary the persistence owner does not
hold, a total unique constraint that a retained history row collides with, a terminal
state reachable by the wrong actor, a consolidation domain nobody accounted for, and a
participant transition the API gives no route to.

Nothing here executes an authorization request, a callback, a recovery or a
consolidation. These tests prove the checks bite, not that any of it works.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_oauth_identity_contract.py"

IGNORED = shutil.ignore_patterns(
    ".git", ".venv", "node_modules", "target", "__pycache__", "assets", "artifacts"
)


class ContractTreeMixin:
    """A writable copy of the tree with the validator repointed at it.

    A mixin rather than a shared TestCase base: subclassing a TestCase to reuse a
    fixture makes the parent's own tests run again under every child's name, so the
    same assertion is counted several times and a failure names the wrong class.
    """

    def setUp(self) -> None:  # noqa: D102 - unittest hook
        super().setUp()
        specification = importlib.util.spec_from_file_location(
            "validate_oauth_identity_contract", VALIDATOR
        )
        assert specification is not None and specification.loader is not None
        module = importlib.util.module_from_spec(specification)
        sys.modules[specification.name] = module
        specification.loader.exec_module(module)
        self.validator = module

        parent = Path(tempfile.mkdtemp(prefix="oauth-identity-contract-"))
        self.addCleanup(shutil.rmtree, parent, True)
        self.root = parent / "repository"
        for relative in ("conformance", "packages", "docs", "scripts"):
            shutil.copytree(
                ROOT / relative, self.root / relative, ignore=IGNORED, symlinks=True
            )
        module.bind_root(self.root)
        self.addCleanup(module.bind_root, ROOT)

    # -- helpers ----------------------------------------------------------

    def run_stage(self, name: str) -> list[str]:
        report: list[str] = []
        self.validator.STAGES[name](report)
        return report

    def assert_reports(self, stage: str, fragment: str) -> None:
        report = self.run_stage(stage)
        joined = "\n".join(report)
        self.assertIn(fragment, joined)

    def assert_clean(self, stage: str) -> None:
        self.assertEqual([], self.run_stage(stage))

    def edit_json(self, relative: str, mutate) -> None:
        path = self.root / relative
        document = json.loads(path.read_text(encoding="utf-8"))
        mutate(document)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def edit_text(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        body = path.read_text(encoding="utf-8")
        self.assertIn(old, body, f"{relative} does not hold the text this test breaks")
        path.write_text(body.replace(old, new, 1), encoding="utf-8")

    def provider(self, document: dict, provider_id: str) -> dict:
        return next(
            row for row in document["providers"] if row["provider_id"] == provider_id
        )


REGISTRY = "packages/schemas/oauth-provider-registry-v1.json"
VECTORS = "conformance/auth/provider-mixup-vectors-v1.json"
MACHINES = "packages/schemas/state-machine-registry-v1.json"
OPENAPI = "packages/schemas/openapi-v1.yaml"
SQL = "packages/schemas/planning-schema.sql"
PLAN_SCHEMA = "packages/schemas/consolidation-plan-v1.schema.json"


class ProviderRegistryTests(ContractTreeMixin, unittest.TestCase):
    def test_committed_tree_passes(self) -> None:
        self.assert_clean("provider-registry")

    def test_capability_claimed_without_an_observation_fails(self) -> None:
        self.edit_json(
            REGISTRY,
            lambda document: self.provider(document, "github")["rfc9207_iss"].update(
                capability="supported",
                primary_source="https://example.invalid/doc",
                observed_at="2026-08-01T00:00:00Z",
            ),
        )
        self.assert_reports(
            "provider-registry",
            "github.rfc9207_iss claims 'supported' while the provider's verification "
            "state is unverified",
        )

    def test_provider_vocabulary_drift_fails(self) -> None:
        self.edit_text(
            SQL,
            "provider text not null check (provider in ('github','x')),\n"
            "  -- The stable linkage key while the binding is live",
            "provider text not null check (provider in ('github','X')),\n"
            "  -- The stable linkage key while the binding is live",
        )
        self.assert_reports(
            "provider-registry",
            "provider vocabulary differs: linked_identities.provider",
        )

    def test_asymmetric_iss_parameter_fails(self) -> None:
        self.edit_text(
            OPENAPI,
            "        - $ref: '#/components/parameters/OAuthState'\n"
            "        - $ref: '#/components/parameters/OAuthIssuer'\n"
            "  /auth/x/start:",
            "        - $ref: '#/components/parameters/OAuthState'\n  /auth/x/start:",
        )
        self.assert_reports(
            "provider-registry",
            "github records RFC 9207 as unverified and its callback declares no `iss` "
            "parameter",
        )

    def test_shared_callback_path_fails(self) -> None:
        self.edit_json(
            REGISTRY,
            lambda document: self.provider(document, "x").update(
                callback_path="/auth/github/callback",
                redirect_uri="https://vibemaxxing.dev/auth/github/callback",
            ),
        )
        self.assert_reports("provider-registry", "share the callback path")

    def test_review_window_beyond_the_ceiling_fails(self) -> None:
        self.edit_json(
            REGISTRY,
            lambda document: self.provider(document, "x").update(
                review_due_at="2031-08-09T00:00:00Z"
            ),
        )
        self.assert_reports("provider-registry", "beyond the 365-day ceiling")


class MixupVectorTests(ContractTreeMixin, unittest.TestCase):
    def test_vector_expectation_that_disagrees_with_the_registry_fails(self) -> None:
        def flip(document: dict) -> None:
            for vector in document["vectors"]:
                if vector["mutated_discriminator"] == "state-binding":
                    vector["expect"] = "accept"
                    vector["expect_reason_code"] = None
                    break

        self.edit_json(VECTORS, flip)
        self.assert_reports(
            "provider-registry", "records accept and the registry decides reject"
        )

    def test_a_corpus_with_no_accepted_baseline_fails(self) -> None:
        def drop(document: dict) -> None:
            document["vectors"] = [
                vector for vector in document["vectors"] if vector["role"] != "baseline"
            ]

        self.edit_json(VECTORS, drop)
        self.assert_reports(
            "provider-registry",
            "has no accepted baseline; a corpus that only ever rejects",
        )

    def test_a_discriminator_with_no_vector_fails(self) -> None:
        def drop(document: dict) -> None:
            document["vectors"] = [
                vector
                for vector in document["vectors"]
                if vector["mutated_discriminator"] != "pkce-method"
            ]

        self.edit_json(VECTORS, drop)
        self.assert_reports("provider-registry", "no vector exercises ['pkce-method']")

    def test_a_refusal_attributable_to_two_fields_fails(self) -> None:
        def widen(document: dict) -> None:
            for vector in document["vectors"]:
                if vector["mutated_discriminator"] == "pkce-method":
                    vector["callback"]["state_matches_transaction"] = False
                    break

        self.edit_json(VECTORS, widen)
        self.assert_reports(
            "provider-registry",
            "a refusal attributable to two fields is attributable to neither",
        )

    def test_the_evaluator_is_swept_even_when_every_vector_agrees(self) -> None:
        # The fixture is untouched and still correct. Removing a rule from the
        # evaluator must still fail, because a corpus cannot notice a check that
        # stopped being applied to it.
        self.validator.DISCRIMINATORS = tuple(
            entry
            for entry in self.validator.DISCRIMINATORS
            if entry[0] != "pkce-method"
        )
        self.assert_reports(
            "provider-registry",
            "declares a discriminator order the evaluator does not implement",
        )


class OAuthTransactionTests(ContractTreeMixin, unittest.TestCase):
    def test_committed_tree_passes(self) -> None:
        self.assert_clean("oauth-transaction")

    def test_a_bare_authorization_code_on_link_fails(self) -> None:
        self.edit_text(
            OPENAPI,
            "        - oauth_transaction_id\n      properties:\n        provider:",
            "        - authorization_code\n      properties:\n        provider:",
        )
        self.edit_text(
            OPENAPI,
            "        oauth_transaction_id:\n          type: string\n          format: uuid\n"
            "    ConsolidationPlanView:",
            "        authorization_code:\n          type: string\n          minLength: 8\n"
            "    ConsolidationPlanView:",
        )
        self.assert_reports(
            "oauth-transaction", "linkIdentity does not require an oauth_transaction_id"
        )

    def test_snake_case_intended_action_fails(self) -> None:
        self.edit_text(
            OPENAPI,
            "          enum:\n            - sign-in\n            - link-identity\n"
            "    OAuthStart:",
            "          enum:\n            - sign_in\n            - link_identity\n"
            "    OAuthStart:",
        )
        report = "\n".join(self.run_stage("oauth-transaction"))
        self.assertIn("intended_action differs: OAuthStartRequest", report)
        self.assertIn("is not lowercase kebab-case", report)

    def test_a_link_transaction_allowed_to_mint_a_session_fails(self) -> None:
        self.edit_text(
            SQL,
            "  check (intended_action <> 'link-identity' or resulting_session_id is null),\n",
            "",
        )
        self.assert_reports(
            "oauth-transaction",
            "a link transaction must not be able to mint browser access",
        )

    def test_an_unrecordable_transition_fails(self) -> None:
        self.edit_text(
            SQL,
            "'oauth-begin','oauth-callback','oauth-consume','oauth-expire','oauth-fail'",
            "'oauth-begin','oauth-callback','oauth-consume','oauth-expire'",
        )
        self.assert_reports(
            "oauth-transaction",
            "oauth_authorization_events.event_type differs from the machine's "
            "transitions: only-in-sql=[] only-in-machine=['oauth-fail']",
        )

    def test_a_missing_revision_column_fails(self) -> None:
        self.edit_text(
            SQL,
            "  failure_reason_code text,\n  state text not null check (state in "
            "('created','redirected','callback-received','consumed','expired','failed')),\n"
            "  revision integer not null default 1 check (revision > 0),\n",
            "  failure_reason_code text,\n  state text not null check (state in "
            "('created','redirected','callback-received','consumed','expired','failed')),\n",
        )
        self.assert_reports(
            "oauth-transaction",
            "oauth_transactions carries no revision column",
        )


class LinkedIdentityTests(ContractTreeMixin, unittest.TestCase):
    def test_committed_tree_passes(self) -> None:
        self.assert_clean("linked-identity")

    def test_a_total_subject_uniqueness_fails(self) -> None:
        self.edit_text(
            SQL,
            "  check (state_changed_at >= created_at)\n);",
            "  check (state_changed_at >= created_at),\n"
            "  unique (provider, provider_subject)\n);",
        )
        self.assert_reports(
            "linked-identity",
            "linked_identities carries a total unique (provider, provider_subject)",
        )

    def test_a_not_null_provider_subject_fails(self) -> None:
        # The pair that made unlinking silently permanent: a subject that cannot be
        # released, retained under a uniqueness rule that then blocks the provider
        # account from ever being linked again.
        self.edit_text(
            SQL,
            "  provider_subject text,\n",
            "  provider_subject text not null,\n",
        )
        self.assert_reports(
            "linked-identity",
            "linked_identities.provider_subject is not null, so an ended binding "
            "cannot release it",
        )

    def test_retention_stated_as_a_promise_rather_than_a_constraint_fails(self) -> None:
        self.edit_text(
            SQL,
            "  check ((provider_account_created_at is not null)\n"
            "         = (state not in ('candidate','unlinked','superseded'))),\n",
            "",
        )
        self.assert_reports(
            "linked-identity",
            "linked_identities does not tie provider_account_created_at to the live states",
        )

    def test_a_partial_index_over_the_wrong_states_fails(self) -> None:
        self.edit_text(
            SQL,
            "create unique index linked_identities_live_subject_idx\n"
            "  on linked_identities (provider, provider_subject)\n"
            "  where state in ('candidate','linked','unlink-pending','lost','compromised','recovery-pending');",
            "create unique index linked_identities_live_subject_idx\n"
            "  on linked_identities (provider, provider_subject)\n"
            "  where state in ('linked');",
        )
        self.assert_reports(
            "linked-identity",
            "linked_identities_live_subject_idx covers the wrong states",
        )

    def test_dropping_the_last_method_guard_fails(self) -> None:
        def rename(document: dict) -> None:
            machine = next(
                item
                for item in document["machines"]
                if item["machine_id"] == "linked-identity"
            )
            for transition in machine["transitions"]:
                if transition["to"] == "unlink-pending":
                    transition["action"] = "request-unlink"

        self.edit_json(MACHINES, rename)
        self.assert_reports(
            "linked-identity",
            "no transition into unlink-pending names the last-authentication-method guard",
        )

    def test_a_moderator_ending_an_identity_fails(self) -> None:
        def widen(document: dict) -> None:
            machine = next(
                item
                for item in document["machines"]
                if item["machine_id"] == "linked-identity"
            )
            for transition in machine["transitions"]:
                if transition["transition_id"] == "identity-supersede":
                    transition["actor"] = "moderator"

        self.edit_json(MACHINES, widen)
        report = "\n".join(self.run_stage("linked-identity"))
        self.assertIn("lets a moderator end a linked identity outright", report)
        self.assertIn("drives a live identity to the terminal state superseded", report)

    def test_a_one_way_recovery_fails(self) -> None:
        def strip(document: dict) -> None:
            machine = next(
                item
                for item in document["machines"]
                if item["machine_id"] == "linked-identity"
            )
            machine["transitions"] = [
                transition
                for transition in machine["transitions"]
                if transition["transition_id"] != "identity-recovery-restored"
            ]

        self.edit_json(MACHINES, strip)
        self.assert_reports(
            "linked-identity", "a recovery-pending identity has no way back to linked"
        )

    def test_requiring_a_credential_to_unlink_fails(self) -> None:
        self.edit_text(
            OPENAPI,
            "    IdentityUnlinkRequest:\n      description:",
            "    IdentityUnlinkRequest:\n"
            "      x-broken-by-test: true\n"
            "      description:",
        )
        self.edit_text(
            OPENAPI,
            "        identity_id:\n          type: string\n          format: uuid\n"
            "    Device:",
            "        identity_id:\n          type: string\n          format: uuid\n"
            "        authorization_code:\n          type: string\n"
            "    Device:",
        )
        self.assert_reports(
            "linked-identity", "unlinkIdentity requires a provider credential"
        )


class RankedIdentityTests(ContractTreeMixin, unittest.TestCase):
    def test_committed_tree_passes(self) -> None:
        self.assert_clean("ranked-identity")

    def test_an_uncovered_consolidation_domain_fails(self) -> None:
        def drop(document: dict) -> None:
            node = document["$defs"]["domain_dispositions"]
            node["required"] = [
                name for name in node["required"] if name != "deletions"
            ]

        self.edit_json(PLAN_SCHEMA, drop)
        self.assert_reports(
            "ranked-identity",
            "does not require every domain: missing=['deletions']",
        )

    def test_an_open_domain_object_fails(self) -> None:
        self.edit_json(
            PLAN_SCHEMA,
            lambda document: document["$defs"]["domain_dispositions"].update(
                additionalProperties=True
            ),
        )
        self.assert_reports(
            "ranked-identity", "domain_dispositions admits additional properties"
        )

    def test_the_newer_identity_surviving_fails(self) -> None:
        path = "packages/schemas/examples/consolidation-plan.valid.json"
        self.edit_json(
            path,
            lambda document: document["case"].update(
                surviving_ranked_identity_created_at="2026-06-01T08:00:00Z",
                absorbed_ranked_identity_created_at="2025-01-01T08:00:00Z",
            ),
        )
        self.assert_reports(
            "ranked-identity",
            "consolidation-plan.valid.json retires the older ranked identity and keeps "
            "the newer",
        )

    def test_a_negative_fixture_that_no_longer_violates_the_rule_fails(self) -> None:
        path = (
            "packages/schemas/examples/"
            "consolidation-plan.invalid-newer-identity-survives.json"
        )
        self.edit_json(
            path,
            lambda document: document["case"].update(
                surviving_ranked_identity_created_at="2025-01-01T08:00:00Z",
                absorbed_ranked_identity_created_at="2026-06-01T08:00:00Z",
            ),
        )
        self.assert_reports(
            "ranked-identity",
            "does not violate the D-564 ordering, so the check that the older identity "
            "survives is passing on data written to break it",
        )

    def test_a_combined_figure_on_the_plan_view_fails(self) -> None:
        self.edit_text(
            OPENAPI,
            "        affected_period_count:\n          type: integer\n          minimum: 0\n"
            "        domain_dispositions:",
            "        affected_period_count:\n          type: integer\n          minimum: 0\n"
            "        combined_token_burn_total:\n          type: integer\n          minimum: 0\n"
            "        domain_dispositions:",
        )
        self.assert_reports(
            "ranked-identity",
            "ConsolidationPlanView.combined_token_burn_total publishes a combined "
            "figure for two accounts",
        )

    def test_a_participant_transition_with_no_route_fails(self) -> None:
        self.validator.PARTICIPANT_OPERATIONS = {
            key: value
            for key, value in self.validator.PARTICIPANT_OPERATIONS.items()
            if key != ("account-consolidation", "consolidation-confirm")
        }
        self.assert_reports(
            "ranked-identity",
            "account-consolidation.consolidation-confirm is performed by the "
            "participant and no API operation reaches it",
        )

    def test_a_route_whose_recent_auth_disagrees_fails(self) -> None:
        def weaken(document: dict) -> None:
            machine = next(
                item
                for item in document["machines"]
                if item["machine_id"] == "account-consolidation"
            )
            for transition in machine["transitions"]:
                if transition["transition_id"] == "consolidation-confirm":
                    transition["recent_auth"] = False

        self.edit_json(MACHINES, weaken)
        self.assert_reports(
            "ranked-identity", "confirmConsolidation declares x-recent-auth 'required'"
        )

    def test_a_ranked_identity_column_on_accounts_fails(self) -> None:
        self.edit_text(
            SQL,
            "create table accounts (\n  account_id uuid primary key,\n",
            "create table accounts (\n  account_id uuid primary key,\n"
            "  ranked_identity_id uuid,\n",
        )
        self.assert_reports("ranked-identity", "accounts declares ranked_identity_id")


if __name__ == "__main__":
    unittest.main()
