"""Index coverage is a coverage signal, not a count. PF-048.

The unit's original acceptance was `grep -c "CREATE INDEX" planning-schema.sql`
greater than three, which is wrong twice. The DDL is lower case, so a case-sensitive
grep answers zero against a file holding a hundred and thirty-odd indexes: a
criterion that was satisfied reported as failed, and the unit sat `not-started` for
that reason. And a count moves the wrong way in both directions — it rises when a
redundant index is added and falls when a wrong one is removed. Eighteen foreign
keys had no index at all while the count stood at 132, including all five on
`oauth_transactions` and `score_contributions.erasure_domain_id`, which is on the
erasure path the whole section exists to serve.

These tests mutate the DDL and the access-path contract and assert the validator
notices. They prove the rules are enforced. They prove nothing about latency: no
index in this repository has been built against data and no query plan has been
read.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
SCHEMAS = ROOT / "packages" / "schemas"
CONTRACT = ROOT / "docs" / "architecture" / "LEADERBOARD_STORAGE_AND_RANKING.md"


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_planning_artifacts", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class IndexFixtureMixin:
    """Owns the temporary schema and contract copies and the patches that select them.

    A mixin rather than a shared `TestCase` base: subclassing one would run every
    test in this file again for each subclass, which is how a suite quietly starts
    reporting four times the cases it has.
    """

    def setUp(self) -> None:  # noqa: D102
        super().setUp()  # type: ignore[misc]
        self.validator = load_validator()
        directory = Path(tempfile.mkdtemp(prefix="index-coverage-"))
        self.addCleanup(shutil.rmtree, directory, True)  # type: ignore[attr-defined]
        self.schemas = directory / "schemas"
        shutil.copytree(SCHEMAS, self.schemas)
        self.root = directory / "root"
        (self.root / "docs" / "architecture").mkdir(parents=True)
        self.contract = (
            self.root / "docs" / "architecture" / ("LEADERBOARD_STORAGE_AND_RANKING.md")
        )
        shutil.copy(CONTRACT, self.contract)
        self.sql = self.schemas / "planning-schema.sql"

    def run_validator(self) -> None:
        with patch.object(self.validator, "SCHEMAS", self.schemas):
            with patch.object(self.validator, "ROOT", self.root):
                self.validator.validate_index_coverage()

    def edit_sql(self, old: str, new: str) -> None:
        text = self.sql.read_text(encoding="utf-8")
        assert old in text, f"fixture text not found: {old!r}"
        self.sql.write_text(text.replace(old, new, 1), encoding="utf-8")

    def edit_contract(self, old: str, new: str) -> None:
        text = self.contract.read_text(encoding="utf-8")
        assert old in text, f"fixture text not found: {old!r}"
        self.contract.write_text(text.replace(old, new, 1), encoding="utf-8")

    def expect_failure(self, fragment: str) -> None:
        with self.assertRaises(  # type: ignore[attr-defined]
            self.validator.ValidationFailure
        ) as raised:
            self.run_validator()
        self.assertIn(fragment, str(raised.exception))  # type: ignore[attr-defined]


class HeadStateTests(IndexFixtureMixin, unittest.TestCase):
    def test_repository_head_passes(self) -> None:
        self.run_validator()

    def test_the_grep_the_acceptance_named_answers_zero(self) -> None:
        """Why the rewritten acceptance is not a count and not a grep.

        `grep -c "CREATE INDEX"` is case-sensitive and this file is lower case, so
        the original criterion evaluated to zero on a schema that satisfied it.
        """
        text = self.sql.read_text(encoding="utf-8")

        self.assertEqual(text.count("CREATE INDEX"), 0)
        self.assertGreater(len(re.findall(r"(?m)^create (unique )?index ", text)), 100)

    def test_every_index_is_reached_by_the_parser(self) -> None:
        """A check over an empty set passes. This asserts the set is not empty."""
        with patch.object(self.validator, "SCHEMAS", self.schemas):
            found = list(
                self.validator._CREATE_INDEX_RE.finditer(self.validator._planning_sql())
            )
            shapes = self.validator._planning_table_shapes()

        self.assertGreater(len(found), 100)
        self.assertGreater(len(shapes), 100)
        self.assertTrue(all(shape.columns for shape in shapes.values()))


class ForeignKeyCoverageTests(IndexFixtureMixin, unittest.TestCase):
    def test_dropping_an_indexed_foreign_key_index_fails(self) -> None:
        self.edit_sql(
            "create index claims_device_idx on claims (device_id);\n",
            "",
        )

        self.expect_failure("foreign keys with no supporting total index")

    def test_the_erasure_path_index_this_unit_added_is_load_bearing(self) -> None:
        """`score_contributions.erasure_domain_id` had no total index of its own.

        `score_contributions_period_domain_idx` leads with the period, so it cannot
        serve the enumeration an erasure performs across every period.
        """
        self.edit_sql(
            "create index score_contributions_domain_idx on score_contributions "
            "(erasure_domain_id);\n",
            "",
        )

        self.expect_failure("score_contributions.erasure_domain_id -> erasure_domains")

    def test_a_partial_index_does_not_cover_a_foreign_key(self) -> None:
        """The rule that found five of the eighteen, all on `oauth_transactions`.

        PostgreSQL's referential check on a parent delete looks for any matching
        child row, including the rows a predicate excludes, so a partial index over
        the referencing column proves nothing about the rest of the table.
        """
        self.edit_sql(
            "create index oauth_transactions_initiating_account_idx on "
            "oauth_transactions (initiating_account_id);",
            "create index oauth_transactions_initiating_account_idx on "
            "oauth_transactions (initiating_account_id) where state = 'created';",
        )

        self.expect_failure("oauth_transactions.initiating_account_id -> accounts")

    def test_a_composite_index_leading_with_the_wrong_column_does_not_cover(
        self,
    ) -> None:
        self.edit_sql(
            "create index certification_results_certification_idx\n"
            "  on certification_results (source_certification_id);",
            "create index certification_results_certification_idx\n"
            "  on certification_results (suite_id, source_certification_id);",
        )

        self.expect_failure(
            "certification_results.source_certification_id -> source_certifications"
        )


class JustificationTests(IndexFixtureMixin, unittest.TestCase):
    def test_an_index_serving_no_foreign_key_and_no_named_query_fails(self) -> None:
        self.edit_sql(
            "create index seasons_window_idx on seasons (starts_at, ends_at);",
            "create index seasons_window_idx on seasons (starts_at, ends_at);\n"
            "create index accounts_created_idx on accounts (created_at);",
        )

        self.expect_failure("indexes that support no foreign key and name no query")

    def test_removing_an_indexs_row_from_the_contract_fails(self) -> None:
        self.edit_contract("`web_sessions_family_idx`", "the family index")

        self.expect_failure("indexes that support no foreign key and name no query")

    def test_a_contract_naming_an_index_that_does_not_exist_fails(self) -> None:
        self.edit_contract(
            "| Season and period boundary lookup",
            "| Imagined path | Imagined access | `accounts_imaginary_idx` |\n"
            "| Season and period boundary lookup",
        )

        self.expect_failure(
            "index names the access-path contract states and the planning DDL "
            "does not define"
        )


class StructuralTests(IndexFixtureMixin, unittest.TestCase):
    def test_an_index_on_a_column_the_table_lost_fails(self) -> None:
        """A rename takes its index with it, or the index dangles silently."""
        self.edit_sql(
            "create index exports_account_idx on exports (account_id);",
            "create index exports_account_idx on exports (owner_account_id);",
        )

        self.expect_failure("index on a column the table does not define")

    def test_an_index_on_a_table_that_does_not_exist_fails(self) -> None:
        self.edit_sql(
            "create index exports_account_idx on exports (account_id);",
            "create index exports_account_idx on exports (account_id);\n"
            "create index ghosts_account_idx on ghosts (account_id);",
        )

        self.expect_failure("index on a table the planning DDL does not define")

    def test_reintroducing_the_redundant_index_fails(self) -> None:
        """The one this unit removed: it duplicated a unique constraint exactly.

        `social_integrity_events` declares `unique (aggregate_id, aggregate_revision)`,
        which PostgreSQL implements as a btree over those two columns in that order.
        The second index served no query the constraint did not and cost a write on
        every insert. It survived because nothing compared an index against the
        constraints beside it — and because it made the index count go up.
        """
        self.edit_sql(
            "create index notifications_account_created_idx on notifications "
            "(account_id, created_at desc);",
            "create index notifications_account_created_idx on notifications "
            "(account_id, created_at desc);\n"
            "create index social_integrity_events_aggregate_idx on "
            "social_integrity_events (aggregate_id, aggregate_revision);",
        )

        self.expect_failure("duplicate index")

    def test_a_descending_index_is_not_a_duplicate_of_its_ascending_constraint(
        self,
    ) -> None:
        """`score_snapshots_view_generation_idx` is the case that keeps this honest.

        `unique (ranking_view_id, generation)` indexes the same two columns, and a
        backward scan of it orders both descending. Neither direction produces
        `ranking_view_id` ascending with `generation` descending, so the second index
        is a different index and the duplicate rule must not flag it.
        """
        self.run_validator()

        text = self.sql.read_text(encoding="utf-8")
        self.assertIn(
            "create index score_snapshots_view_generation_idx on score_snapshots "
            "(ranking_view_id, generation desc);",
            text,
        )


class PartitioningTests(IndexFixtureMixin, unittest.TestCase):
    def test_the_three_partitioned_tables_are_found(self) -> None:
        """The agreement check is worthless if the parsed set is empty."""
        with patch.object(self.validator, "SCHEMAS", self.schemas):
            spans = self.validator._planning_table_spans()
        partitioned = {
            name
            for name, _, tail in spans
            if self.validator._PARTITION_BY_RE.match(tail)
        }

        self.assertEqual(
            partitioned, {"minute_scores", "notifications", "audit_events"}
        )

    def test_partitioning_the_ddl_does_not_declare_fails(self) -> None:
        self.edit_contract(
            "- `audit_events` on `created_at`.",
            "- `audit_events` on `created_at`;\n- `claims` on `received_at`.",
        )

        self.expect_failure("partitioning disagrees")

    def test_a_partitioned_table_the_contract_omits_fails(self) -> None:
        self.edit_contract("- `notifications` on `created_at`;\n", "")

        self.expect_failure("partitioning disagrees")

    def test_partitioning_on_a_different_column_fails(self) -> None:
        """The contract states the key, not only the fact of partitioning."""
        self.edit_contract(
            "- `minute_scores` on `minute_start`;",
            "- `minute_scores` on `created_at`;",
        )

        self.expect_failure("partitioning disagrees")

    def test_a_partitioned_table_with_no_default_partition_fails(self) -> None:
        self.edit_sql(
            "create table notifications_default partition of notifications default;\n",
            "",
        )

        self.expect_failure("range-partitioned tables with no default partition")


if __name__ == "__main__":
    unittest.main()
