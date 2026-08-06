"""Drift-injection tests for scripts/repository/validate_load_scenarios.py.

The load scenarios are a specification for tests nobody has written yet, which is
exactly the kind of artifact that rots quietly: a rate stays at the number somebody
typed while the policy it was derived from moves underneath it, and the drift is
invisible until the day the scenario runs and asserts something untrue.

The validator ties every rate to a policy key and every scenario to the table in
`docs/verification/TEST_STRATEGY.md` that owns the set. These tests inject each drift
and assert it is caught: a renamed policy, a scenario in one place and not the other, a
population that no longer matches the invite quota, a pass condition that cannot be
read off a result, and a claim scope that quietly stops saying these are unrun.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_load_scenarios.py"
SCENARIOS = ROOT / "evals" / "load" / "load-scenarios-v1.json"
POLICIES = ROOT / "packages" / "schemas" / "policy-defaults-v1.json"
STRATEGY = ROOT / "docs" / "verification" / "TEST_STRATEGY.md"


def load_validator() -> object:
    specification = importlib.util.spec_from_file_location(
        "validate_load_scenarios", VALIDATOR
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class ScenarioValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_validator()

    def run_with(self, document: dict) -> list[str]:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        handle.write(json.dumps(document))
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return self.module.validate(Path(handle.name), POLICIES, STRATEGY)

    def document(self) -> dict:
        return json.loads(SCENARIOS.read_text())

    # -- the committed file ------------------------------------------------------------

    def test_the_committed_scenarios_resolve(self) -> None:
        self.assertEqual(self.module.validate(SCENARIOS, POLICIES, STRATEGY), [])

    def test_every_scenario_the_strategy_names_is_declared(self) -> None:
        named = self.module.scenarios_named_by_the_strategy(STRATEGY.read_text())
        self.assertEqual(
            named,
            {
                "beta-steady",
                "beta-peak",
                "offline-drain",
                "leaderboard-thunder",
                "ratelimit-breach",
                "soak",
            },
        )
        self.assertEqual(named, set(self.document()["scenarios"]))

    def test_every_scenario_is_sized_at_the_private_beta_and_says_so(self) -> None:
        document = self.document()
        policies = json.loads(POLICIES.read_text())["policies"]
        self.assertEqual(
            document["population"]["participants"],
            policies["invite_outstanding_max"]["value"],
        )
        # And the file still refuses to imply anything about the 100,000 target.
        self.assertIn("100,000", document["scale_target_note"])
        self.assertIn("D-360", document["scale_target_note"])

    # -- drift -------------------------------------------------------------------------

    def test_a_policy_reference_that_no_longer_resolves_fails(self) -> None:
        document = self.document()
        document["scenarios"]["beta-steady"]["operations"][0]["policy_ref"] = (
            "rate_limit_that_was_renamed"
        )
        defects = self.run_with(document)
        self.assertTrue(
            any("rate_limit_that_was_renamed" in defect for defect in defects)
        )

    def test_a_scenario_the_strategy_names_and_the_file_drops_fails(self) -> None:
        document = self.document()
        del document["scenarios"]["soak"]
        defects = self.run_with(document)
        self.assertTrue(any("names scenario soak" in defect for defect in defects))

    def test_a_scenario_the_file_invents_fails(self) -> None:
        document = self.document()
        document["scenarios"]["hundred-thousand-identities"] = document["scenarios"][
            "soak"
        ]
        defects = self.run_with(document)
        self.assertTrue(
            any(
                "hundred-thousand-identities" in defect and "does not name it" in defect
                for defect in defects
            )
        )

    def test_a_population_that_drifts_from_the_invite_quota_fails(self) -> None:
        document = self.document()
        document["population"]["participants"] = 1000
        defects = self.run_with(document)
        self.assertTrue(any("ring size is a row count" in defect for defect in defects))

    def test_an_unknown_operation_class_fails(self) -> None:
        document = self.document()
        document["scenarios"]["soak"]["operations"][0]["operation_class"] = (
            "bulk-export"
        )
        defects = self.run_with(document)
        self.assertTrue(any("bulk-export" in defect for defect in defects))

    def test_a_rate_with_no_derivation_fails(self) -> None:
        document = self.document()
        document["scenarios"]["soak"]["operations"][0]["derivation"] = "  "
        defects = self.run_with(document)
        self.assertTrue(
            any("a rate without one is a round number" in defect for defect in defects)
        )

    def test_a_scenario_with_no_failure_condition_fails(self) -> None:
        document = self.document()
        document["scenarios"]["soak"]["fails_when"] = ""
        defects = self.run_with(document)
        self.assertTrue(any("has to be judged" in defect for defect in defects))

    def test_a_pass_condition_that_cannot_be_read_off_a_result_fails(self) -> None:
        document = self.document()
        document["scenarios"]["soak"]["pass_conditions"][0] = {
            "metric": "memory",
            "comparison": "looks fine",
            "value": "not much",
        }
        defects = self.run_with(document)
        self.assertTrue(any("which is not one of" in defect for defect in defects))
        self.assertTrue(any("non-numeric value" in defect for defect in defects))

    def test_two_bounds_on_one_metric_fail(self) -> None:
        document = self.document()
        conditions = document["scenarios"]["beta-steady"]["pass_conditions"]
        conditions.append(dict(conditions[0]))
        defects = self.run_with(document)
        self.assertTrue(any("one bound too many" in defect for defect in defects))

    def test_a_scenario_that_drives_nothing_fails(self) -> None:
        document = self.document()
        document["scenarios"]["soak"]["operations"] = []
        defects = self.run_with(document)
        self.assertTrue(
            any(
                "a scenario that drives nothing is a sentence" in defect
                for defect in defects
            )
        )

    def test_a_zero_duration_fails(self) -> None:
        document = self.document()
        document["scenarios"]["soak"]["duration_seconds"] = 0
        defects = self.run_with(document)
        self.assertTrue(
            any("non-positive duration_seconds" in defect for defect in defects)
        )

    def test_dropping_the_specification_only_claim_scope_fails(self) -> None:
        # None of these has been written or run. A file that stops saying so starts
        # reading like evidence, which is the exact failure mode the eval registry had.
        document = self.document()
        document["claim_scope"] = "verified"
        defects = self.run_with(document)
        self.assertTrue(any("specification-only" in defect for defect in defects))

    def test_a_malformed_scenario_file_fails_closed(self) -> None:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        handle.write("{ not json")
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        defects = self.module.validate(Path(handle.name), POLICIES, STRATEGY)
        self.assertTrue(any("not valid JSON" in defect for defect in defects))

    def test_a_missing_scenario_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            defects = self.module.validate(
                Path(directory) / "absent.json", POLICIES, STRATEGY
            )
        self.assertTrue(any("unreadable" in defect for defect in defects))


class StrategyTableParsingTests(unittest.TestCase):
    """The scenario set is read out of the document rather than duplicated in code."""

    def setUp(self) -> None:
        self.module = load_validator()

    def test_only_backticked_identifiers_in_the_first_column_are_scenarios(
        self,
    ) -> None:
        text = "\n".join(
            [
                "| Scenario | Load | Duration | Passes when |",
                "|---|---|---|---|",
                "| `beta-steady` | 200 participants | 30 min | p95 fine |",
                "| `packages/ui` | 70% statement | | a coverage row, not a scenario |",
                "| Go unit and integration | `testing` | | a framework row |",
                "| `soak` | unchanged | 12 h | no leak |",
            ]
        )
        self.assertEqual(
            self.module.scenarios_named_by_the_strategy(text), {"beta-steady", "soak"}
        )

    def test_a_strategy_document_naming_no_scenario_fails(self) -> None:
        handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        handle.write("# Test Strategy\n\nNothing here.\n")
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        defects = self.module.validate(SCENARIOS, POLICIES, Path(handle.name))
        self.assertTrue(any("names no load scenario" in defect for defect in defects))


if __name__ == "__main__":
    unittest.main()
