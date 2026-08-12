"""Drift-injection tests for scripts/repository/validate_checkpoint_receipt_binding.py.

The validator exists because `checkpoint-receipt-v1`, `checkpoint_receipts` and the
OpenAPI document described one receipt three ways and agreed on almost nothing: the
twelve signed labels and the nine stored columns were near-disjoint, `openapi-v1.yaml`
published the whole receipt as an opaque base64 blob and had no component for it, and
`server_receipt_sequence` — which `VIBEPROOF_V1_PROTOCOL.md` lists as server state — was
declared in the CDDL and stored nowhere, under a green `doctor.py`, for the length of
the planning program.

A validator for that class of defect is only worth having if it fails when one authority
moves and the others do not. Every test below moves exactly one and requires the exact
failure, not merely that something raised: a check that fires with the wrong diagnosis is
a check that will be satisfied by the wrong repair.
"""

from __future__ import annotations

import contextlib
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_checkpoint_receipt_binding.py"

ARTIFACTS = ("CDDL", "SQL", "OPENAPI", "PROTOCOL", "INTEGRITY")


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_checkpoint_receipt_binding", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class ReceiptBindingFixture:
    """A working copy of the five artifacts, so a test mutates a file nothing else reads.

    A mixin rather than a base `TestCase`. Subclassing a `TestCase` to reuse a fixture
    makes the parent's own tests run again inside every child, which inflates the count
    with reruns and makes one broken assertion fail in several places at once.
    """

    def setUp(self) -> None:
        self.validator = load_validator()
        self.root = Path(tempfile.mkdtemp(prefix="checkpoint-receipt-"))
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

    def rewrite(self, name: str, old: str, new: str, count: int = 1) -> None:
        path = self.paths[name]
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"{name}: {old!r} is not present to rewrite")
        path.write_text(text.replace(old, new, count), encoding="utf-8")

    def assert_fails(self, fragment: str) -> None:
        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()
        self.assertIn(fragment, str(raised.exception))


class ReceiptIsOneDefinitionTests(ReceiptBindingFixture, unittest.TestCase):
    """The near-disjoint field sets D-043 records as its sixth divergence."""

    def test_the_repository_as_committed_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_dropping_the_receipt_sequence_from_the_ddl_fails(self) -> None:
        """The exact prior state: the CDDL bound label 7 and no column stored it."""
        self.rewrite(
            "SQL",
            "  server_receipt_sequence bigint not null check (server_receipt_sequence >= 0),\n",
            "",
        )

        self.assert_fails("only-in-binding=['server_receipt_sequence']")

    def test_dropping_the_receipt_sequence_from_the_cddl_fails(self) -> None:
        """The other direction. A column nothing signs is as disjoint as the reverse."""
        self.rewrite(
            "CDDL",
            "  7: uint64,               ; server_receipt_sequence\n",
            "",
        )

        self.assert_fails(
            "checkpoint-receipt-v1 binds labels this validator's three-way table does not"
        )

    def test_a_column_nothing_binds_fails(self) -> None:
        """The check is not satisfiable by addition either."""
        self.rewrite(
            "SQL",
            "  verifier_policy_id text not null,",
            "  verifier_policy_id text not null,\n  receipt_hint bytea,",
        )

        self.assert_fails("only-in-sql=['receipt_hint']")

    def test_renaming_a_column_away_from_its_label_fails(self) -> None:
        """`last_sequence` was the name the two sets shared and neither wire nor
        protocol document used. Reverting it makes the sets disjoint on that field."""
        self.rewrite(
            "SQL",
            "  accepted_through_claim_sequence bigint not null\n"
            "    check (accepted_through_claim_sequence >= 0),",
            "  last_sequence bigint not null check (last_sequence >= 0),",
        )

        self.assert_fails("only-in-sql=['last_sequence']")

    def test_a_server_only_column_with_no_recorded_reason_fails(self) -> None:
        """The reason is the whole content of `server-only`; without it the table is a
        list of exemptions granted to whatever was already there."""
        columns = dict(self.validator.RECEIPT_SERVER_ONLY_COLUMNS)
        columns["previous_receipt_digest"] = "   "
        with patch.object(self.validator, "RECEIPT_SERVER_ONLY_COLUMNS", columns):
            self.assert_fails(
                "checkpoint_receipts.previous_receipt_digest is excluded from the bound "
                "tuple with no reason"
            )

    def test_a_wire_only_label_with_no_recorded_reason_fails(self) -> None:
        labels = dict(self.validator.RECEIPT_WIRE_ONLY_LABELS)
        labels[0] = ""
        with patch.object(self.validator, "RECEIPT_WIRE_ONLY_LABELS", labels):
            self.assert_fails(
                "checkpoint-receipt-v1 label 0 is excluded from the binding with no "
                "recorded reason"
            )

    def test_the_api_dropping_a_bound_field_from_required_fails(self) -> None:
        self.rewrite("OPENAPI", "        - last_accepted_claim_sha256\n", "")

        self.assert_fails("CheckpointReceipt publishes an optional member")

    def test_the_api_dropping_a_bound_property_fails(self) -> None:
        self.rewrite(
            "OPENAPI",
            "        server_signing_key_id:\n          type: string\n"
            "          format: uuid\n    ClaimBatchResult:",
            "    ClaimBatchResult:",
        )

        self.assert_fails("only-in-binding=['server_signing_key_id']")

    def test_the_api_opening_its_property_set_fails(self) -> None:
        self.rewrite(
            "OPENAPI",
            "      type: object\n      additionalProperties: false\n      required:\n"
            "        - checkpoint_receipt_id",
            "      type: object\n      additionalProperties: true\n      required:\n"
            "        - checkpoint_receipt_id",
        )

        self.assert_fails("CheckpointReceipt does not close its property set")


class ServerReceiptSequenceTests(ReceiptBindingFixture, unittest.TestCase):
    """A counter is a column plus the constraint that makes it monotonic."""

    def test_dropping_the_monotonic_constraint_fails(self) -> None:
        self.rewrite("SQL", "  unique (lineage_id, server_receipt_sequence)\n", "")

        self.assert_fails("offers no `unique (lineage_id, server_receipt_sequence)`")

    def test_writing_the_constraint_into_a_comment_only_fails(self) -> None:
        """SQL is read with comment lines stripped, so a constraint stated in prose
        beside the table does not satisfy a check the way a grep would let it."""
        self.rewrite(
            "SQL",
            "  unique (lineage_id, server_receipt_sequence)\n",
            "  -- unique (lineage_id, server_receipt_sequence)\n",
        )

        self.assert_fails("offers no `unique (lineage_id, server_receipt_sequence)`")

    def test_collapsing_the_two_counters_into_one_constraint_fails(self) -> None:
        """One batch advances the claim sequence by up to 256 and the receipt sequence
        by one, so one unique index cannot carry both rules."""
        self.rewrite(
            "SQL", "  unique (lineage_id, accepted_through_claim_sequence),\n", ""
        )

        self.assert_fails(
            "offers no `unique (lineage_id, accepted_through_claim_sequence)`"
        )

    def test_dropping_the_non_negative_floor_fails(self) -> None:
        self.rewrite(
            "SQL",
            "  server_receipt_sequence bigint not null check (server_receipt_sequence >= 0),",
            "  server_receipt_sequence bigint not null,",
        )

        self.assert_fails("does not refuse a negative `server_receipt_sequence`")

    def test_dropping_the_span_constraint_fails(self) -> None:
        self.rewrite(
            "SQL",
            "  constraint checkpoint_receipts_head_within_span\n"
            "    check (accepted_through_claim_sequence >= first_sequence),\n",
            "",
        )

        self.assert_fails("acknowledged head below the span that produced it")

    def test_dropping_the_expiry_constraint_fails(self) -> None:
        self.rewrite(
            "SQL",
            "  constraint checkpoint_receipts_expiry_follows_issue check (expires_at > issued_at),\n",
            "",
        )

        self.assert_fails("a receipt that expired before it was issued")


class BatchResultCarriesBothFormsTests(ReceiptBindingFixture, unittest.TestCase):
    """A client verifies bytes and reads fields; publishing one of the two is the defect."""

    def test_the_projection_not_being_referenced_fails(self) -> None:
        """A component nothing returns is a definition, not a projection."""
        self.rewrite(
            "OPENAPI",
            "          oneOf:\n"
            "            - $ref: '#/components/schemas/CheckpointReceipt'\n"
            "            - type: 'null'\n",
            "          type:\n            - string\n            - 'null'\n",
        )

        self.assert_fails(
            "ClaimBatchResult.checkpoint_receipt does not reference `CheckpointReceipt`"
        )

    def test_dropping_the_signed_envelope_fails(self) -> None:
        """The bytes are what a client verifies against `server_signing_key_id`."""
        self.rewrite("OPENAPI", "        - checkpoint_receipt_cose\n", "")

        self.assert_fails(
            "ClaimBatchResult does not carry a required `checkpoint_receipt_cose`"
        )

    def test_a_rejected_batch_carrying_an_envelope_fails(self) -> None:
        self.rewrite(
            "OPENAPI",
            "            checkpoint_receipt_cose:\n              type: 'null'\n",
            "",
        )

        self.assert_fails(
            "a rejected ClaimBatchResult may carry `checkpoint_receipt_cose`"
        )


class ProtocolDerivationTests(ReceiptBindingFixture, unittest.TestCase):
    """The bound is read from VIBEPROOF_V1_PROTOCOL.md; a check may not outlive it."""

    def test_deleting_the_server_state_sentence_fails(self) -> None:
        self.rewrite(
            "PROTOCOL",
            "- server state: expected sequence, accepted local head, last accepted "
            "claim digest, prior checkpoint receipt and monotonic receipt sequence.\n",
            "",
        )

        self.assert_fails("no longer carries a `- server state:` bullet")

    def test_removing_one_item_from_the_server_state_sentence_fails(self) -> None:
        """The sentence is parsed, so it cannot shed the item this unit exists for."""
        self.rewrite(
            "PROTOCOL",
            ", prior checkpoint receipt and monotonic receipt sequence.",
            " and prior checkpoint receipt.",
        )

        self.assert_fails("only-in-validator=['monotonic receipt sequence']")

    def test_adding_an_item_with_no_column_fails(self) -> None:
        self.rewrite(
            "PROTOCOL",
            "prior checkpoint receipt and monotonic receipt sequence.",
            "prior checkpoint receipt, monotonic receipt sequence and last known "
            "device posture.",
        )

        self.assert_fails("only-in-document=['last known device posture']")

    def test_deleting_the_acknowledgement_sentence_fails(self) -> None:
        self.rewrite(
            "PROTOCOL", "A receipt acknowledges only the bound accepted head.", ""
        )

        self.assert_fails("no longer states 'A receipt acknowledges only the bound")


class IntegrityModelDerivationTests(ReceiptBindingFixture, unittest.TestCase):
    """The owner of newest-wins names the constraint; the constraint must exist."""

    def test_the_document_naming_a_constraint_the_ddl_dropped_fails(self) -> None:
        """The `last_sequence` rename reached five files. This is the check that would
        have caught it missing any one of them."""
        self.rewrite(
            "INTEGRITY",
            "`unique (lineage_id, accepted_through_claim_sequence)` on `checkpoint_receipts`",
            "`unique (lineage_id, last_sequence)` on `checkpoint_receipts`",
        )

        self.assert_fails(
            "names 'unique (lineage_id, last_sequence)' on checkpoint_receipts and "
            "planning-schema.sql does not declare it"
        )

    def test_the_document_dropping_the_constraint_entirely_fails(self) -> None:
        self.rewrite(
            "INTEGRITY",
            "`unique (lineage_id, accepted_through_claim_sequence)` on `checkpoint_receipts`",
            "a uniqueness constraint",
        )

        self.assert_fails("no longer names the `unique (...)` constraint")


if __name__ == "__main__":
    unittest.main()
