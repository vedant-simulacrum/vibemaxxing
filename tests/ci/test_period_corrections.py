"""PF-023. Periods have a lifecycle, and a period rebuilds from its ledger.

Three defects hid each other. `periods` had no state column, so nothing recorded
which side of the lateness window a period was on. `ranking_corrections` named no
participant and no period, so a rebuild from it was not possible in any form -- a key
that omits its discriminator does not become usable by being read more carefully. And
`score_contributions` was called an immutable ledger with nothing stopping an update
to it.

Each case injects one way the lifecycle, the ledger or the rebuild can rot.
"""

from __future__ import annotations

import unittest

from .planning_fixtures import PlanningValidatorMixin

VECTORS = "conformance/planning/ranking-correction-vectors-v1.json"
SQL = "packages/schemas/planning-schema.sql"
REGISTRY = "packages/schemas/state-machine-registry-v1.json"


class PeriodCorrectionTests(PlanningValidatorMixin, unittest.TestCase):
    def check(self) -> None:
        self.validator.validate_period_correction_rebuild()

    def case(self, record, case_id: str) -> dict:
        return next(item for item in record["cases"] if item["case_id"] == case_id)

    def machine(self, record) -> dict:
        return next(
            item for item in record["machines"] if item["machine_id"] == "period"
        )

    def test_the_committed_tree_passes(self) -> None:
        self.assert_passes(self.check)

    def test_a_correction_appends_and_the_claim_is_untouched(self) -> None:
        record = self.read(VECTORS)
        case = self.case(record, "PR-002")
        total, refusal = self.validator.rebuild_period_total(case)

        self.assertIsNone(refusal)
        self.assertEqual(total, 105000)
        self.assertEqual(case["contributions"][0]["token_burn_delta"], 120000)

    def test_retractions_exceeding_what_they_correct_reject(self) -> None:
        record = self.read(VECTORS)
        total, refusal = self.validator.rebuild_period_total(
            self.case(record, "PR-005")
        )

        self.assertIsNone(total)
        self.assertEqual(refusal, "retractions-exceed-what-they-correct")

    def test_a_case_recording_the_wrong_total_fails(self) -> None:
        record = self.read(VECTORS)
        self.case(record, "PR-001")["expected"]["token_burn_total"] = 205001
        self.write(VECTORS, record)

        self.assert_fails(self.check, "and the ledger rebuilds to 205000")

    def test_a_superseded_row_that_starts_counting_fails(self) -> None:
        record = self.read(VECTORS)
        self.case(record, "PR-003")["contributions"][0]["superseded"] = False
        self.write(VECTORS, record)

        self.assert_fails(self.check, "and the ledger rebuilds to 160000")

    def test_a_correction_row_drifting_from_the_ledger_fails(self) -> None:
        """The equivalence the rebuild exists to prove."""
        record = self.read(VECTORS)
        self.case(record, "PR-002")["corrections"][0]["magnitude"] = 19000
        self.write(VECTORS, record)

        self.assert_fails(self.check, "and the rebuild refuses it")

    def test_a_retraction_written_as_a_positive_delta_is_refused(self) -> None:
        record = self.read(VECTORS)
        case = self.case(record, "PR-002")
        case["contributions"][1]["token_burn_delta"] = 20000
        _, refusal = self.validator.rebuild_period_total(case)

        self.assertEqual(refusal, "direction-and-sign-disagree")

    def test_removing_every_rebuilding_case_fails(self) -> None:
        record = self.read(VECTORS)
        record["cases"] = [
            case for case in record["cases"] if case["expected"]["outcome"] != "rebuild"
        ]
        self.write(VECTORS, record)

        self.assert_fails(self.check, "no period case rebuilds")

    def test_removing_the_equivalence_refusal_case_fails(self) -> None:
        """A signal that improves when the thing it counts is removed."""
        record = self.read(VECTORS)
        record["cases"] = [
            case for case in record["cases"] if case["case_id"] != "PR-006"
        ]
        self.write(VECTORS, record)

        self.assert_fails(self.check, "no case exercises the rebuild refusals")

    def test_a_period_without_a_lifecycle_fails(self) -> None:
        self.edit_text(
            SQL,
            "  state text not null check (state in "
            "('open','frozen','closed','corrected','archived')),\n  rules_version",
            "  rules_version",
        )

        self.assert_fails(self.check, "lacks its required period-correction invariant")

    def test_a_lifetime_period_that_may_be_frozen_fails(self) -> None:
        self.edit_text(
            SQL,
            "  check (period_type <> 'lifetime' or state = 'open'),\n",
            "",
        )

        self.assert_fails(self.check, "may be frozen, closed or archived")

    def test_a_correction_key_that_omits_the_participant_fails(self) -> None:
        self.edit_text(
            SQL,
            "unique (correction_id, ranking_view_id, period_id, erasure_domain_id, "
            "direction)",
            "unique (correction_id, ranking_view_id, direction)",
        )

        self.assert_fails(self.check, "lacks its required period-correction invariant")

    def test_a_signed_delta_with_no_direction_rule_fails(self) -> None:
        self.edit_text(
            SQL,
            "  check ((origin = 'retraction') = (token_burn_delta < 0))\n",
            "  check (token_burn_delta <> 0)\n",
        )

        self.assert_fails(self.check, "lacks its required period-correction invariant")

    def test_dropping_the_append_only_delete_trigger_fails(self) -> None:
        self.edit_text(
            SQL,
            "create trigger score_contributions_no_delete\n  before delete on "
            "score_contributions",
            "create trigger score_contributions_no_delete\n  before truncate on "
            "score_contributions",
        )

        self.assert_fails(self.check, "declares no trigger enforcing it")

    def test_the_rewrite_trigger_losing_a_protected_column_fails(self) -> None:
        self.edit_text(
            SQL,
            "    or old.token_burn_delta is distinct from new.token_burn_delta\n",
            "",
        )

        self.assert_fails(self.check, "does not protect a column the ledger rests on")

    def test_the_trigger_refusing_the_erasure_path_fails(self) -> None:
        """`on delete set null` is performed as an UPDATE on this row."""
        self.edit_text(
            SQL,
            "    or old.origin is distinct from new.origin\n",
            "    or old.origin is distinct from new.origin\n"
            "    or old.claim_id is distinct from new.claim_id\n",
        )

        self.assert_fails(self.check, "which is the column an erasure clears")

    def test_a_worker_correcting_a_sealed_standing_fails(self) -> None:
        """A terminal-ish state reached by the wrong actor."""
        registry = self.read(REGISTRY)
        machine = self.machine(registry)
        for transition in machine["transitions"]:
            if transition["to"] == "corrected":
                transition["actor"] = "worker"
                transition["authentication"] = "workload-identity"
        self.write(REGISTRY, registry)

        self.assert_fails(self.check, "lets a worker supersede a sealed standing")

    def test_archiving_an_open_period_fails(self) -> None:
        registry = self.read(REGISTRY)
        machine = self.machine(registry)
        for transition in machine["transitions"]:
            if transition["to"] == "archived":
                transition["from"] = ["open", "closed", "corrected"]
        self.write(REGISTRY, registry)

        self.assert_fails(self.check, "archives an open period")

    def test_an_inline_foreign_key_to_a_later_table_fails(self) -> None:
        """The defect this rule was written from, injected back in.

        `ranking_corrections` is declared thirty-one tables before `ranking_views`.
        An inline reference resolves when the file is read as text and fails when
        PostgreSQL executes it, and CI is the only place it is ever executed.
        """
        self.edit_text(
            SQL,
            "  ranking_view_id text not null,\n  period_id uuid not null references "
            "periods(period_id),\n  erasure_domain_id uuid not null,",
            "  ranking_view_id text not null references "
            "ranking_views(ranking_view_id),\n  period_id uuid not null references "
            "periods(period_id),\n  erasure_domain_id uuid not null,",
        )

        self.assert_fails(
            self.validator.validate_ddl_declaration_order,
            "which is created later in the file",
        )

    def test_a_reference_to_a_table_the_ddl_never_creates_fails(self) -> None:
        self.edit_text(
            SQL,
            "  period_id uuid not null references periods(period_id),\n"
            "  erasure_domain_id uuid not null,",
            "  period_id uuid not null references calendar_periods(period_id),\n"
            "  erasure_domain_id uuid not null,",
        )

        self.assert_fails(
            self.validator.validate_ddl_declaration_order,
            "which the planning DDL never creates",
        )

    def test_the_committed_ddl_is_executable_top_to_bottom(self) -> None:
        self.assert_passes(self.validator.validate_ddl_declaration_order)

    def test_a_machine_missing_one_of_the_five_states_fails(self) -> None:
        registry = self.read(REGISTRY)
        machine = self.machine(registry)
        machine["states"] = [
            state for state in machine["states"] if state != "corrected"
        ]
        self.write(REGISTRY, registry)

        self.assert_fails(self.check, "the period machine declares")


if __name__ == "__main__":
    unittest.main()
