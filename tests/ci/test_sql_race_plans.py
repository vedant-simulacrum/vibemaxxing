"""A race plan that names no rows asserts nothing. PF-020.

`conformance/p1140e/sql-race-plans-v1.json` held fourteen cases. Every one carried
the same four interleaving steps — `transaction-a-locks-authority`,
`transaction-b-attempts-conflict`, `transaction-a-commits`,
`transaction-b-rechecks` — and one sentence of prose. No table column, no value, no
row. The file described scenarios and asserted nothing that could be wrong, and the
validator's only structural rule was that the case ids matched a hard-coded set and
the tables existed. That rule would pass on a file whose every case was a
placeholder, which is what it was passing on.

PF-020's acceptance says each case names the exact rows a correct implementation
leaves behind, which is only falsifiable if the rows are enumerated and resolve
against the schema they plan against. `residual_rows` is that enumeration and these
tests are what stop it rotting back into prose.

They prove the plans are well-formed and resolve. They prove nothing about
PostgreSQL's behaviour: `execution_state` is `planned-runtime-evidence` on every
case and none has been executed.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_p1140e_contracts.py"
CONFORMANCE = ROOT / "conformance" / "p1140e"
SCHEMAS = ROOT / "packages" / "schemas"
PLANS = CONFORMANCE / "sql-race-plans-v1.json"

AMBIGUOUS_COMMIT_CASES = (
    "commit-crash-before-commit",
    "commit-crash-after-commit",
    "commit-dropped-response",
    "commit-executing-takeover",
    "commit-key-expiry",
)


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_p1140e_contracts", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class RacePlanFixtureMixin:
    """Owns the temporary conformance copy and the patch that selects it.

    A mixin rather than a base `TestCase`: subclassing one runs every test in this
    file again per subclass, and this repository has been bitten by a suite whose
    reported case count was a multiple of its real one.
    """

    def setUp(self) -> None:  # noqa: D102
        super().setUp()  # type: ignore[misc]
        self.validator = load_validator()
        directory = Path(tempfile.mkdtemp(prefix="race-plans-"))
        self.addCleanup(shutil.rmtree, directory, True)  # type: ignore[attr-defined]
        self.conformance = directory / "p1140e"
        shutil.copytree(CONFORMANCE, self.conformance)
        self.plans = self.conformance / "sql-race-plans-v1.json"

    def run_validator(self) -> int:
        with patch.object(self.validator, "CONF", self.conformance):
            return self.validator.main()

    def edit(self, mutate) -> None:
        document = json.loads(self.plans.read_text(encoding="utf-8"))
        mutate(document)
        self.plans.write_text(json.dumps(document, indent=2), encoding="utf-8")

    def case(self, document: dict, case_id: str) -> dict:
        return next(item for item in document["cases"] if item["case_id"] == case_id)

    def expect_failure(self, fragment: str) -> None:
        with self.assertRaises(  # type: ignore[attr-defined]
            self.validator.Failure
        ) as raised:
            self.run_validator()
        self.assertIn(fragment, str(raised.exception))  # type: ignore[attr-defined]


class HeadStateTests(RacePlanFixtureMixin, unittest.TestCase):
    def test_repository_head_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_the_five_ambiguous_commit_cases_exist(self) -> None:
        document = json.loads(PLANS.read_text(encoding="utf-8"))
        declared = {case["case_id"] for case in document["cases"]}

        for case_id in AMBIGUOUS_COMMIT_CASES:
            self.assertIn(case_id, declared)

    def test_every_case_names_rows_rather_than_describing_a_scenario(self) -> None:
        """The defect as found: fourteen cases, zero rows named."""
        document = json.loads(PLANS.read_text(encoding="utf-8"))

        for case in document["cases"]:
            with self.subTest(case=case["case_id"]):
                rows = case["residual_rows"]
                self.assertTrue(rows)
                presences = {row["presence"] for row in rows}
                self.assertEqual(presences, {"present", "absent"})

    def test_no_two_cases_share_an_interleaving(self) -> None:
        """All fourteen shared one before this unit."""
        document = json.loads(PLANS.read_text(encoding="utf-8"))
        interleavings = [tuple(case["interleaving"]) for case in document["cases"]]

        self.assertEqual(len(set(interleavings)), len(interleavings))

    def test_every_named_column_resolves_against_the_schema(self) -> None:
        """The assertion the row enumeration exists to make, counted.

        A check over an empty set passes, so this states the size of the set as
        well as its correctness.
        """
        sql = (SCHEMAS / "planning-schema.sql").read_text(encoding="utf-8")
        columns = self.validator.planning_table_columns(sql)
        document = json.loads(PLANS.read_text(encoding="utf-8"))

        stated = 0
        for case in document["cases"]:
            for row in case["residual_rows"]:
                if row["presence"] != "present":
                    continue
                for column in row["columns"]:
                    stated += 1
                    self.assertIn(column, columns[row["table"]])

        self.assertGreater(stated, 60)

    def test_no_case_claims_to_have_been_executed(self) -> None:
        document = json.loads(PLANS.read_text(encoding="utf-8"))

        for case in document["cases"]:
            self.assertEqual(case["execution_state"], "planned-runtime-evidence")


class ResidualRowTests(RacePlanFixtureMixin, unittest.TestCase):
    def test_a_case_with_no_residual_rows_fails(self) -> None:
        self.edit(
            lambda document: self.case(document, "block-race").update(
                residual_rows=[], tables=[]
            )
        )

        self.expect_failure("SQL race plan names no residual rows")

    def test_a_case_that_only_says_what_survives_fails(self) -> None:
        """Half a recovery plan. The defect is always a row that is there and
        should not be, or the reverse, so a plan naming only one side cannot
        express the failure it is a plan for."""

        def mutate(document: dict) -> None:
            case = self.case(document, "commit-crash-before-commit")
            case["residual_rows"] = [
                row for row in case["residual_rows"] if row["presence"] == "present"
            ]
            case["tables"] = sorted({row["table"] for row in case["residual_rows"]})

        self.edit(mutate)

        self.expect_failure("SQL race plan states no present and absent pair")

    def test_a_row_naming_a_column_the_table_lost_fails(self) -> None:
        """`retain_until` is the column this unit added; renaming it must break
        the plan that depends on it rather than leaving a sentence behind."""

        def mutate(document: dict) -> None:
            case = self.case(document, "commit-key-expiry")
            row = next(
                item
                for item in case["residual_rows"]
                if item["table"] == "idempotency_records"
            )
            row["columns"]["retained_until"] = row["columns"].pop("retain_until")

        self.edit(mutate)

        self.expect_failure("names columns idempotency_records does not define")

    def test_a_present_row_naming_no_column_values_fails(self) -> None:
        def mutate(document: dict) -> None:
            row = next(
                item
                for item in self.case(document, "idempotency-same-bytes")[
                    "residual_rows"
                ]
                if item["presence"] == "present"
            )
            row["columns"] = {}

        self.edit(mutate)

        self.expect_failure("SQL race present row names no column values")

    def test_describing_the_columns_of_an_absent_row_fails(self) -> None:
        """A row that is not there has no column values, and stating some is the
        contradiction that makes an absence assertion read as a presence one."""

        def mutate(document: dict) -> None:
            row = next(
                item
                for item in self.case(document, "commit-crash-before-commit")[
                    "residual_rows"
                ]
                if item["presence"] == "absent"
            )
            row["columns"] = {"lineage_id": "L"}

        self.edit(mutate)

        self.expect_failure("describes the columns of an absent row")

    def test_a_row_with_no_key_fails(self) -> None:
        def mutate(document: dict) -> None:
            self.case(document, "board-owner-transfer")["residual_rows"][0].pop("key")

        self.edit(mutate)

        self.expect_failure("states no key or no note")

    def test_the_table_list_drifting_from_the_rows_fails(self) -> None:
        """`tables` is derived from the rows; a case that lists a table no row
        names is the old file's shape returning."""
        self.edit(
            lambda document: self.case(document, "local-delete-ack")["tables"].append(
                "accounts"
            )
        )

        self.expect_failure("tables disagree with its residual rows")

    def test_an_unknown_presence_value_fails(self) -> None:
        self.edit(
            lambda document: self.case(document, "block-race")["residual_rows"][
                0
            ].update(presence="maybe")
        )

        self.expect_failure("states an unknown presence")


class InterleavingTests(RacePlanFixtureMixin, unittest.TestCase):
    def test_two_cases_sharing_one_interleaving_fails(self) -> None:
        """The exact defect: fourteen cases, one copy-pasted step list."""

        def mutate(document: dict) -> None:
            source = self.case(document, "block-race")["interleaving"]
            self.case(document, "board-owner-transfer")["interleaving"] = list(source)

        self.edit(mutate)

        self.expect_failure("share one interleaving")

    def test_an_interleaving_shorter_than_four_steps_fails(self) -> None:
        self.edit(
            lambda document: self.case(document, "block-race").update(
                interleaving=["a", "b", "c"]
            )
        )

        self.expect_failure("states fewer than four steps")

    def test_a_repeated_step_within_one_interleaving_fails(self) -> None:
        def mutate(document: dict) -> None:
            case = self.case(document, "block-race")
            case["interleaving"][1] = case["interleaving"][0]

        self.edit(mutate)

        self.expect_failure("repeats an interleaving step")


class CaseSetTests(RacePlanFixtureMixin, unittest.TestCase):
    def test_removing_an_ambiguous_commit_case_fails(self) -> None:
        for case_id in AMBIGUOUS_COMMIT_CASES:
            with self.subTest(case=case_id):
                self.setUp()
                self.edit(
                    lambda document, target=case_id: document.__setitem__(
                        "cases",
                        [
                            item
                            for item in document["cases"]
                            if item["case_id"] != target
                        ],
                    )
                )

                self.expect_failure("SQL race plan set mismatch")

    def test_a_case_claiming_execution_fails(self) -> None:
        self.edit(
            lambda document: self.case(document, "commit-dropped-response").update(
                execution_state="executed"
            )
        )

        self.expect_failure("overclaims execution")

    def test_a_case_naming_a_table_the_schema_lost_fails(self) -> None:
        def mutate(document: dict) -> None:
            case = self.case(document, "local-delete-ack")
            case["tables"] = ["local_deletion_ledger"]
            for row in case["residual_rows"]:
                row["table"] = "local_deletion_ledger"

        self.edit(mutate)

        self.expect_failure("SQL race references unknown table")


if __name__ == "__main__":
    unittest.main()
