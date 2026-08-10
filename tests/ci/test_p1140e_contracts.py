"""Drift-injection tests for the P-1140E structural gate.

This validator had no tests. It enforces cross-contract structural agreement —
decision statuses against the P-1140E matrix, operations against the OpenAPI
document, reason authorities against the state-machine registry — and a check
that cannot be shown to fire is not evidence that anything agrees.

PF-035's acceptance names six injected defects and, as written, demanded all six
from `scripts/repository/validate_p1140e_contracts.py`. Four of them are owned by
other validators that already enforce them: lifecycle reachability and
SQL/state/API vocabulary agreement by `validate_state_vocabularies.py`, and the
generation-keyed constraints, the viewer-authorization revision sources and every
recomputed content digest by `validate_planning_artifacts.py`. Reimplementing them
here would have put a second owner on each of those vocabularies — the defect class
this repository has been repairing all along — so the acceptance was rewritten to
name the owning validator per leg, and each leg is injected against its owner here.
`make validate` runs all three, so the P-1140E structural gate fails on any of the
six.

Every case in this file runs its validator against a writable mirror of the
repository. The first version of this suite patched `SCHEMAS` alone and left `CONF`
on the real `conformance/p1140e/`, so any case that mutated a registry tripped
`state fixture set mismatch` or `platform validation plan set mismatch` before
reaching the check it meant to test, and passed on the wrong error.
"""

from __future__ import annotations

import json
import unittest

from tests.ci.planning_fixtures import (
    P1140EValidatorMixin,
    PlanningValidatorMixin,
    StateVocabularyMixin,
)

MATRIX = "conformance/p1140e/validation-matrix-v1.json"
REASONS = "packages/schemas/reason-codes-v1.json"
SQL = "packages/schemas/planning-schema.sql"
AUTHORIZATION = "packages/schemas/projection-authorization-v1.json"
SOCIAL_MANIFEST = "conformance/social/manifest.json"


class CleanTreeTests(P1140EValidatorMixin, unittest.TestCase):
    """The committed tree passes, and says what kind of check passed."""

    def test_the_committed_tree_passes(self) -> None:
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)

    def test_the_summary_names_the_check_as_structural(self) -> None:
        """A suite name must describe what it actually executes.

        Nothing in this validator observes a running system, so the line it prints
        on success has to say so. A reader who sees only `pass` will read it as
        evidence that the contracts work.
        """
        _, output = self.run_validator()
        self.assertIn("structural cross-contract validation: pass", output)
        self.assertIn("claim_scope=structural-consistency-only", output)
        self.assertIn("runtime_evidence=absent", output)


class ReasonAuthorityTests(P1140EValidatorMixin, unittest.TestCase):
    """The reason-authority rule, which is where the validator had drifted.

    Its allowlist of non-aggregate authorities was hard-coded and had gone stale.
    """

    def edit(self, mutate) -> None:
        document = self.read(REASONS)
        mutate(document)
        self.write(REASONS, document)

    def test_an_authority_that_resolves_to_nothing_fails(self) -> None:
        self.edit(lambda d: d["codes"][0].update(state_machine="made-up-machine"))

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("authority", str(raised.exception))

    def test_a_declared_authority_no_code_uses_fails(self) -> None:
        """The `device-lineage-v1` case, which survived by being hard-coded.

        It was permitted by the validator and named by zero codes. A declared
        exemption that nothing uses is a stale excuse, and the only reason this
        one lasted is that nothing read the list back.
        """
        self.edit(
            lambda d: d["non_aggregate_authorities"].update(
                {"device-lineage-v1": "reintroduced dead exemption"}
            )
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("authority", str(raised.exception))

    def test_an_authority_shadowing_a_registered_machine_fails(self) -> None:
        """A name meaning two things is worse than a name meaning nothing."""
        self.edit(
            lambda d: d["non_aggregate_authorities"].update(
                {"friendship": "shadows a registered machine"}
            )
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("shadows", str(raised.exception))

    def test_every_declared_authority_is_absent_from_the_machine_registry(self) -> None:
        """The committed state holds the property the shadow check enforces."""
        registry = self.read(REASONS)
        machines = {
            machine["machine_id"]
            for machine in self.read("packages/schemas/state-machine-registry-v1.json")[
                "machines"
            ]
        }
        self.assertEqual(set(registry["non_aggregate_authorities"]) & machines, set())

    def test_every_declared_authority_carries_a_reason(self) -> None:
        """A bare list would say which names are allowed and never why."""
        registry = self.read(REASONS)
        for name, reason in registry["non_aggregate_authorities"].items():
            self.assertGreater(len(reason), 80, name)


class MissingOwnerTests(P1140EValidatorMixin, unittest.TestCase):
    """Injection 1 of 6: a decision whose normative owner is not there.

    Owned by `scripts/repository/validate_p1140e_contracts.py`. The matrix binds
    every D-001..D-069 decision to five owners and the binding is worth nothing if
    an owner is a string nobody resolves: a citation to a deleted document reads
    exactly like a citation to a live one.
    """

    def bind(self, field: str, value) -> None:
        matrix = self.read(MATRIX)
        matrix["decision_bindings"][0][field] = value
        self.write(MATRIX, matrix)

    def test_an_owner_that_resolves_to_no_file_fails(self) -> None:
        self.bind("normative_owner", "docs/architecture/DELETED_CONTRACT.md")

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("references missing normative_owner", str(raised.exception))

    def test_an_empty_owner_fails(self) -> None:
        self.bind("normative_owner", "")

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("non-empty", str(raised.exception))

    def test_a_missing_fixture_path_fails(self) -> None:
        """The same rule holds for all five owners, not only the normative one."""
        self.bind("fixture_path", "conformance/deleted/fixtures.json")

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("references missing fixture_path", str(raised.exception))


class LifecycleAndVocabularyTests(StateVocabularyMixin, unittest.TestCase):
    """Injections 2 and 3 of 6, owned by `validate_state_vocabularies.py`.

    That file is the single owner of the three-way agreement between the state
    registry, the planning DDL and the OpenAPI document, and of reachability within
    each machine. Both legs are injected against it rather than reimplemented in the
    P-1140E validator, because two files enforcing one vocabulary is how the two
    stop agreeing.
    """

    def test_an_unreachable_lifecycle_state_fails(self) -> None:
        """A state no transition arrives at is a state nothing can ever be in.

        It reads as a declared outcome, so a handler can be written to produce it
        and a reviewer can be satisfied that the case is covered.
        """

        def mutate(machines) -> None:
            machines["account-lifecycle"]["states"].append("orphaned-state")

        self.edit_registry(mutate)

        code, output = self.run_validator()

        self.assertEqual(code, 1, output)
        self.assertIn(
            "account-lifecycle.orphaned-state is unreachable from 'active'", output
        )

    def test_a_sql_state_api_vocabulary_mismatch_fails(self) -> None:
        """One aggregate, three owners, one spelling.

        A CHECK constraint admitting a value the registry does not declare is a
        state the database can hold and no lifecycle describes.
        """
        self.edit_sql(
            "state text not null check (state in "
            "('active','restricted','deletion-pending','deleted'))",
            "state text not null check (state in "
            "('active','restricted','deletion-pending','removed'))",
        )

        code, output = self.run_validator()

        self.assertEqual(code, 1, output)
        self.assertIn("SQL CHECK on accounts.state differs", output)

    def test_an_api_enum_that_drifts_from_the_registry_fails(self) -> None:
        """The third owner. A projection may narrow a vocabulary, not invent one."""

        def mutate(schemas) -> None:
            schemas["Session"]["properties"]["state"]["enum"] = [
                "active",
                "revoked",
                "expired",
                "vanished",
            ]

        self.edit_openapi(mutate)

        code, output = self.run_validator()

        self.assertEqual(code, 1, output)
        self.assertIn("vanished", output)


class PersistenceAndDigestTests(PlanningValidatorMixin, unittest.TestCase):
    """Injections 4, 5 and 6 of 6, owned by `validate_planning_artifacts.py`.

    Generation keys, viewer-authorization revision sources and every recomputed
    content digest already resolve there against the artifacts they describe.
    """

    COPIED = ("packages/schemas", "conformance", "docs", "evals", "scripts")

    def test_a_missing_generation_key_fails(self) -> None:
        """A generation column that is not part of a key is not a generation.

        `score_snapshots` exists to give a client a durable name for exactly one
        sealed generation. Drop the generation out of the uniqueness and one view
        can hold two snapshots for one generation, so the durable name stops naming
        anything and a cursor a client is holding resolves to whichever row the
        planner finds.
        """
        self.edit_text(
            SQL,
            "unique (ranking_view_id, generation)\n",
            "unique (ranking_view_id, snapshot_id)\n",
        )

        self.assert_fails(
            self.validator.validate_ranking_cursor_vectors,
            "score_snapshots lacks its generation-keyed constraint",
        )

    def test_a_missing_authority_revision_fails(self) -> None:
        """Each of the nine authorization inputs must name the revision it rechecks.

        The rule is deny-before-widen with a revision recheck before the answer is
        used. An input whose revision source is a table name with no column has
        nothing to recheck, so the recheck silently becomes a re-read of whatever
        the row says at the time.
        """
        profile = self.read(AUTHORIZATION)
        profile["inputs"][0]["revision_source"] = profile["inputs"][0][
            "persistence_owner"
        ]
        self.write(AUTHORIZATION, profile)

        self.assert_fails(
            self.validator.validate_identity_lifecycle_contracts,
            "names a revision source without a table",
        )

    def test_a_content_digest_that_does_not_match_fails(self) -> None:
        """A recorded digest is only worth the recomputation nobody skipped.

        Every conformance suite manifest records the SHA-256 of each fixture it
        names, and the manifest is what binds a case to the bytes it was written
        against. A digest that is never recomputed lets the fixture change under a
        case that still claims to exercise it.
        """
        manifest = self.read(SOCIAL_MANIFEST)
        for case in manifest["cases"]:
            if case.get("fixtures"):
                case["fixtures"][0]["sha256"] = "0" * 64
                break
        else:  # pragma: no cover - the suite would have no fixture to corrupt
            self.fail("the social suite manifest names no fixture to corrupt")
        self.write(SOCIAL_MANIFEST, manifest)

        self.assert_fails(
            self.validator.validate_conformance_manifests,
            "records a stale digest",
        )

    def test_every_named_fixture_digest_is_current(self) -> None:
        """The committed state holds the property the digest check enforces."""
        self.validator.validate_conformance_manifests()

    def test_the_recorded_digests_are_not_an_empty_set(self) -> None:
        """A digest check over zero digests passes and proves nothing."""
        recorded = 0
        for manifest in sorted(self.path("conformance").rglob("manifest.json")):
            document = json.loads(manifest.read_text(encoding="utf-8"))
            for case in document.get("cases", []):
                recorded += len(case.get("fixtures", []))
        self.assertGreater(recorded, 0)


if __name__ == "__main__":
    unittest.main()
