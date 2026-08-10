"""Drift-injection tests for scripts/repository/validate_batch_challenge_binding.py.

The validator exists because ADR-007 stated an acceptance test for itself — "must match
this ADR" — and nothing executed it, so the challenge could be defined three times over
disjoint field sets, partial acceptance could be prohibited by three documents and
admitted by two schemas, and a "bounded signed gap declaration" could have no wrapper, no
carrier, no table and no bound, all under a green `doctor.py`.

A validator for that class of defect is only worth having if it fails when one authority
moves and the others do not. Every test below moves exactly one and requires the failure.
"""

from __future__ import annotations

import contextlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_batch_challenge_binding.py"

ARTIFACTS = ("CDDL", "SQL", "OPENAPI", "POLICY", "ADR", "PROTOCOL")


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_batch_challenge_binding", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class BindingFixture:
    """A working copy of the six artifacts, so a test mutates a file nothing else reads."""

    def setUp(self) -> None:
        self.validator = load_validator()
        self.root = Path(tempfile.mkdtemp(prefix="batch-challenge-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.paths: dict[str, Path] = {}
        for name in ARTIFACTS:
            source = getattr(self.validator, name)
            target = self.root / source.name
            shutil.copyfile(source, target)
            self.paths[name] = target

    def run_validator(self) -> int:
        with contextlib.ExitStack() as stack:
            for name, path in self.paths.items():
                stack.enter_context(patch.object(self.validator, name, path))
            return self.validator.main()
        raise AssertionError("unreachable")

    def rewrite(self, name: str, old: str, new: str) -> None:
        path = self.paths[name]
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"{name}: {old!r} is not present to rewrite")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def edit_policy(self, key: str, field: str, value: object) -> None:
        path = self.paths["POLICY"]
        document = json.loads(path.read_text(encoding="utf-8"))
        document["policies"][key][field] = value
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def assert_fails(self, fragment: str) -> None:
        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()
        self.assertIn(fragment, str(raised.exception))


class ChallengeIsOneDefinitionTests(BindingFixture, unittest.TestCase):
    """SR-007's untouched artifact, and the three-way disagreement behind it."""

    def test_the_repository_as_committed_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_dropping_the_expected_tuple_from_the_ddl_fails(self) -> None:
        """The exact prior state: the CDDL bound it and no column stored it."""
        self.rewrite(
            "SQL",
            "  expected_next_sequence bigint not null check (expected_next_sequence >= 0),\n",
            "",
        )

        self.assert_fails(
            "claim_challenges does not persist exactly the challenge tuple"
        )

    def test_a_column_with_no_recorded_reason_fails(self) -> None:
        """The check is not satisfiable by addition either."""
        self.rewrite(
            "SQL",
            "  issued_at timestamptz not null,",
            "  issued_at timestamptz not null,\n  batch_hint bytea,",
        )

        self.assert_fails(
            "claim_challenges does not persist exactly the challenge tuple"
        )

    def test_the_api_dropping_a_bound_field_fails(self) -> None:
        self.rewrite("OPENAPI", "        - expected_local_commitment_head\n", "")

        self.assert_fails("ClaimChallenge publishes an optional member")

    def test_reintroducing_batch_commitment_fails(self) -> None:
        """D-626. It arrived in one artifact alone and could come back the same way."""
        self.rewrite(
            "OPENAPI",
            "        challenge_id:\n          type: string\n          format: uuid\n"
            "        account_pseudonym:",
            "        challenge_id:\n          type: string\n          format: uuid\n"
            "        batch_commitment:\n          type: string\n"
            "        account_pseudonym:",
        )

        self.assert_fails("`batch_commitment` is declared by")

    def test_letting_the_client_choose_a_bound_field_fails(self) -> None:
        self.rewrite(
            "OPENAPI",
            "      properties:\n        device_id:\n          type: string\n"
            "          format: uuid\n    ClaimChallenge:",
            "      properties:\n        device_id:\n          type: string\n"
            "          format: uuid\n        expected_next_sequence:\n"
            "          type: integer\n    ClaimChallenge:",
        )

        self.assert_fails("lets the client propose part of the bound tuple")


class SignedBatchPositionTests(BindingFixture, unittest.TestCase):
    """ADR-007's ordering rules were unenforceable because nothing signed a position."""

    def test_dropping_the_signed_batch_index_fails(self) -> None:
        self.rewrite(
            "CDDL",
            "  32: 0..255,              ; batch_index, zero-based position in batch-context label 4\n",
            "",
        )

        self.assert_fails("declares no label 32")

    def test_a_signed_range_disagreeing_with_the_batch_bound_fails(self) -> None:
        self.rewrite("CDDL", "  33: 1..256,", "  33: 1..512,")

        self.assert_fails("disagrees with the 256-claim batch bound")

    def test_a_configurable_ceiling_above_the_encodable_one_fails(self) -> None:
        """Found while repairing: the default was 500 against a grammar bounded at 256."""
        self.edit_policy("batch_max_claims", "value", 500)

        self.assert_fails("policy-defaults-v1.json sets batch_max_claims")

    def test_dropping_the_duplicate_index_constraint_fails(self) -> None:
        self.rewrite("SQL", "  unique (batch_id, batch_index),\n", "")

        self.assert_fails("does not refuse a duplicate batch index")


class PartialAcceptanceTests(BindingFixture, unittest.TestCase):
    """Prohibited in three documents and constrained by nothing, for the whole program."""

    def test_a_single_batch_result_map_fails(self) -> None:
        """Reverting to one map is reverting to the shape partial acceptance encodes in."""
        text = self.paths["CDDL"].read_text(encoding="utf-8")
        start = text.index("atomic-batch-result-v1 = {")
        end = text.index("; Ordinals are", start)
        self.paths["CDDL"].write_text(
            text[:start]
            + "atomic-batch-result-v1 = {\n  0: 1,\n  1: uuid7,\n  2: 0..5,\n"
            "  3: digest32,\n  4: [1*256 claim-result-v1],\n"
            "  5: [* cose-sign1-receipt-v1],\n  6: bytes .size (0..1048576)\n}\n\n"
            + text[end:],
            encoding="utf-8",
        )

        self.assert_fails("atomic-batch-result-v1 is not a two-way choice")

    def test_a_committed_arm_admitting_refused_claim_results_fails(self) -> None:
        self.rewrite(
            "CDDL",
            "  4: [1*256 claim-accepted-result-v1],",
            "  4: [1*256 claim-result-v1],",
        )

        self.assert_fails("per-claim results rather than")

    def test_a_refusal_with_no_reason_code_fails(self) -> None:
        self.rewrite(
            "CDDL",
            "claim-refused-result-v1 = { 0: uuid7, 1: 4..7, 2: [1* reason-code], 3: nil }",
            "claim-refused-result-v1 = { 0: uuid7, 1: 4..7, 2: [* reason-code], 3: nil }",
        )

        self.assert_fails("empty reason list")

    def test_removing_the_api_mutual_exclusion_fails(self) -> None:
        self.rewrite(
            "OPENAPI",
            "            rejections:\n              maxItems: 0\n",
            "            rejections:\n              maxItems: 256\n",
        )

        self.assert_fails("may carry rejections")

    def test_letting_claims_attach_to_a_refused_batch_fails(self) -> None:
        self.rewrite(
            "SQL",
            "batch_outcome text not null check (batch_outcome in ('committed','idempotent-replay')),",
            "batch_outcome text not null check (batch_outcome in ('committed','idempotent-replay','rejected')),",
        )

        self.assert_fails("claims may attach to a batch outcome that did not commit")

    def test_dropping_the_composite_foreign_key_fails(self) -> None:
        self.rewrite(
            "SQL",
            "  foreign key (batch_id, batch_outcome) references claim_batches (batch_id, outcome),\n"
            "  unique (batch_id, batch_index),",
            "  unique (batch_id, batch_index),",
        )

        self.assert_fails("does not reference the batch at its outcome")


class GapDeclarationTests(BindingFixture, unittest.TestCase):
    """A shape with no signature, no carrier, no persistence owner and no bound."""

    def test_removing_the_cose_wrapper_fails(self) -> None:
        self.rewrite(
            "CDDL",
            "cose-sign1-gap-v1 = #6.18([\n  protected: bytes,\n  unprotected: {},\n"
            "  payload: bytes,\n  signature: signature64\n])\n",
            "",
        )

        self.assert_fails("no COSE wrapper for a gap declaration")

    def test_removing_the_claim_carrier_fails(self) -> None:
        self.rewrite("CDDL", "  34: digest32 / nil\n", "  34: uuid7 / nil\n")

        self.assert_fails("carries no gap declaration commitment")

    def test_a_cause_ordinal_with_no_registered_meaning_fails(self) -> None:
        self.rewrite(
            "CDDL", "  7: 0..3,                 ; registered gap cause", "  7: 0..5,"
        )

        self.assert_fails("does not admit exactly the 4 causes")

    def test_widening_the_recoverable_bound_past_the_adr_fails(self) -> None:
        self.rewrite(
            "SQL",
            "check (sequence_after_gap - sequence_before_gap - 1 <= 10000)",
            "check (sequence_after_gap - sequence_before_gap - 1 <= 100000)",
        )

        self.assert_fails("does not refuse a gap wider than the 10000 sequences")

    def test_moving_the_bound_in_the_adr_alone_fails(self) -> None:
        """The number is read from ADR-007, so the ADR cannot drift away from the CHECK."""
        self.rewrite(
            "ADR",
            "The maximum recoverable gap is 10,000 sequences.",
            "The maximum recoverable gap is 50,000 sequences.",
        )

        self.assert_fails("does not refuse a gap wider than the 50000 sequences")

    def test_a_policy_default_disagreeing_with_the_adr_fails(self) -> None:
        self.edit_policy("max_recoverable_gap_sequences", "value", 25)

        self.assert_fails("does not carry the recoverable-gap bound")


class AdrDerivationTests(BindingFixture, unittest.TestCase):
    """Every check above reads ADR-007's words; a check may not outlive its premise."""

    def test_deleting_the_prohibition_from_the_adr_fails(self) -> None:
        self.rewrite(
            "ADR", "Partial batch acceptance is prohibited in protocol v1.", ""
        )

        self.assert_fails("ADR-007 no longer states")

    def test_deleting_the_refusal_from_the_protocol_document_fails(self) -> None:
        self.rewrite("PROTOCOL", "never partial success", "sometimes partial success")

        self.assert_fails("no longer refuses partial success")


if __name__ == "__main__":
    unittest.main()
