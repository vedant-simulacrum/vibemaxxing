"""The local store holds no key material, and four accidental surfaces are bounded.

`packages/schemas/local-store-v1.sql` is the device half of the storage contract. Two
properties matter and neither was checked.

It holds no key material of its own — keys live in the platform keystore, so a copied
database file is not a copied identity. And the surfaces that carry content *by
accident* rather than by design were absent from the canary fixture: a log line, a
backup, a diagnostic bundle and a corruption report. Each is assembled while something
is going wrong, which is exactly when quoting the thing that went wrong is most
tempting and least reviewed.
"""

from __future__ import annotations

import json
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "packages" / "schemas" / "local-store-v1.sql"
CANARIES = ROOT / "conformance" / "privacy" / "p1140b-boundary-canaries-v1.json"
ALLOWLIST = ROOT / "packages" / "schemas" / "egress-allowlist-v1.json"

ACCIDENTAL = ("log", "backup", "diagnostic", "corruption-report")


def sql() -> str:
    return STORE.read_text(encoding="utf-8")


def statements() -> str:
    """The DDL with comment lines removed, so prose cannot satisfy a check."""
    return "\n".join(
        line for line in sql().splitlines() if not line.lstrip().startswith("--")
    )


class LocalStoreTests(unittest.TestCase):
    def test_the_file_parses_under_sqlite(self) -> None:
        connection = sqlite3.connect(":memory:")
        connection.executescript(sql())

        tables = connection.execute(
            "select count(*) from sqlite_master where type='table'"
        ).fetchone()[0]
        self.assertGreater(tables, 0)

    def test_the_store_holds_no_key_material(self) -> None:
        """A copied database file must not be a copied identity."""
        body = statements()
        for forbidden in (
            "private_key",
            "secret_key",
            "signing_key",
            "key_material",
            "keypair",
            "passphrase",
            "password",
        ):
            self.assertNotIn(forbidden, body, forbidden)

    def test_the_only_failure_explanation_is_a_registered_code(self) -> None:
        """`last_reason_code`, not `last_error_message`.

        A failure explained by quoting what failed is how a transcript reaches a
        column nobody classified.
        """
        body = statements()

        self.assertIn("last_reason_code", body)
        for freeform in ("error_message", "error_detail", "stack_trace", "log_text"):
            self.assertNotIn(freeform, body, freeform)

    def test_the_deletion_receipt_admits_what_it_cannot_prove(self) -> None:
        body = statements()

        self.assertIn("filesystem-snapshot-possible", body)
        self.assertIn("backup-copy-possible", body)


class AccidentalSurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = json.loads(CANARIES.read_text(encoding="utf-8"))["cases"]
        self.boundaries = {case["boundary"] for case in self.cases}

    def test_all_four_accidental_surfaces_are_covered(self) -> None:
        for boundary in ACCIDENTAL:
            self.assertIn(boundary, self.boundaries, boundary)

    def test_each_carries_a_positive_and_a_negative_case(self) -> None:
        """A boundary with only a rejection is satisfied by rejecting everything."""
        for boundary in ACCIDENTAL:
            outcomes = {
                case["expected"]
                for case in self.cases
                if case["boundary"] == boundary
            }
            self.assertEqual(outcomes, {"accept", "reject-before-egress"}, boundary)

    def test_every_negative_names_a_declared_forbidden_class(self) -> None:
        forbidden = set(
            json.loads(ALLOWLIST.read_text(encoding="utf-8"))["forbidden_classes"]
        )
        for case in self.cases:
            if case["expected"] != "reject-before-egress":
                continue
            field = case["input"].get("forbidden_field")
            if field is not None:
                self.assertIn(field, forbidden, case["case_id"])

    def test_every_negative_carries_a_distinct_canary(self) -> None:
        """A shared canary cannot tell you which boundary leaked."""
        canaries = [
            case["input"]["canary"]
            for case in self.cases
            if case["expected"] == "reject-before-egress" and "canary" in case["input"]
        ]

        self.assertEqual(len(canaries), len(set(canaries)))


if __name__ == "__main__":
    unittest.main()
