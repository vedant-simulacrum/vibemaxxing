"""Continuity is scoped to the lineage, not to the device row.

`AGENTS.md` states it as a binding rule. `device_sequences` did the opposite: it was
keyed on `device_id` and held the continuity head per device row.

`docs/planning/SR_SEVERITY_REGRADING_PROPOSAL.md` had already written down what that
costs — "a copied device store produces two rows that are each internally continuous,
so the fork the D-072 quarantine exists to catch is invisible to the mechanism that is
supposed to catch it". Clone the store, enrol as a second device, and both rows count
up from their own zero forever.

`continuity_state` also sat on both `device_sequences` and `device_lineages` with
nothing stating which won, so a device reading `continuous` inside a lineage reading
`broken` was representable and unresolvable.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "packages" / "schemas" / "planning-schema.sql"


def table(name: str) -> str:
    found = re.search(
        rf"create table {name} \((?P<body>.*?)\n\);",
        SQL.read_text(encoding="utf-8"),
        re.S,
    )
    assert found is not None, name
    return found.group("body")


def primary_key(name: str) -> str:
    body = table(name)
    inline = re.search(r"^\s*(\w+)[^,\n]*\bprimary key\b", body, re.M)
    if inline:
        return inline.group(1)
    composite = re.search(r"primary key \(([^)]*)\)", body)
    assert composite is not None, name
    return composite.group(1)


class LineageScopedContinuityTests(unittest.TestCase):
    def test_the_sequence_is_keyed_on_the_lineage(self) -> None:
        """The defect: keyed on device_id, one clone got its own private counter."""
        self.assertEqual(primary_key("device_sequences"), "lineage_id")

    def test_the_sequence_no_longer_references_a_device_row(self) -> None:
        self.assertNotIn("device_id", table("device_sequences"))

    def test_the_sequence_references_the_lineage_table(self) -> None:
        self.assertIn(
            "references device_lineages(lineage_id)", table("device_sequences")
        )

    def test_continuity_state_has_exactly_one_owner(self) -> None:
        """Two tables carrying it, with no stated precedence, is unresolvable."""
        self.assertNotIn("continuity_state", table("device_sequences"))
        self.assertIn("continuity_state", table("device_lineages"))

    def test_a_challenge_is_scoped_to_the_lineage(self) -> None:
        body = table("claim_challenges")

        self.assertIn("lineage_id uuid not null references device_lineages", body)

    def test_the_lineage_table_precedes_everything_that_references_it(self) -> None:
        """PostgreSQL rejects a foreign key to a table declared later in the file.

        This was a real failure, not a hypothetical: applying the file to postgres:16
        after the rekey produced 'relation "device_lineages" does not exist', and
        `make validate` did not catch it because the DDL stage skips without a
        database URL.
        """
        text = SQL.read_text(encoding="utf-8")
        lineage = text.index("create table device_lineages (")
        for dependent in ("claim_challenges", "device_sequences"):
            self.assertLess(
                lineage, text.index(f"create table {dependent} ("), dependent
            )

    def test_one_spelling_for_a_challenge_and_one_for_a_lineage(self) -> None:
        """PF-009's other half: the identifiers must agree across boundaries."""
        cddl = (ROOT / "packages" / "schemas" / "vibeproof-claim-v1.cddl").read_text(
            encoding="utf-8"
        )
        api = (ROOT / "packages" / "schemas" / "openapi-v1.yaml").read_text(
            encoding="utf-8"
        )
        sql = SQL.read_text(encoding="utf-8")
        for identifier in ("challenge_id", "lineage_id"):
            for name, text in (("cddl", cddl), ("openapi", api), ("sql", sql)):
                self.assertIn(identifier, text, f"{identifier} missing from {name}")
        # No camelCase variant anywhere: one spelling means one spelling.
        for camel in ("challengeId", "lineageId"):
            for name, text in (("cddl", cddl), ("openapi", api), ("sql", sql)):
                self.assertNotIn(camel, text, f"{camel} present in {name}")


if __name__ == "__main__":
    unittest.main()
