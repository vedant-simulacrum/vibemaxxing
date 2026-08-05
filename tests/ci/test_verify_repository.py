"""Drift-injection tests for scripts/ci/verify_repository.py.

The matrix used to report a lane that executed nothing exactly like one that ran and
passed. Two things now stop that: the outcomes are distinct, and the outcome every
lane produced is recorded in scripts/ci/coverage-baseline-v1.json. These tests prove
the recorded ceiling fires on a regression, stays quiet at the ceiling and on an
improvement, and fails closed when it cannot be read — because a gate that cannot be
shown to fire is not evidence.
"""

from __future__ import annotations

import importlib.util
import io
import json
import shutil
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "scripts" / "ci" / "verify_repository.py"
BASELINE = ROOT / "scripts" / "ci" / "coverage-baseline-v1.json"


def load_verifier() -> object:
    specification = importlib.util.spec_from_file_location(
        "verify_repository", VERIFIER
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class VerifyRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.verifier = load_verifier()

    # -- lane selection ----------------------------------------------------------------

    def test_selects_go_and_rust_and_reports_the_node_lane_as_uncovered(self) -> None:
        checks = self.verifier.planned_checks(ROOT)
        statuses = {check.name: check.status for check in checks}

        self.assertEqual(statuses["go-test"], "pending")
        self.assertEqual(statuses["go-vet"], "pending")
        self.assertEqual(statuses["go-build"], "pending")
        self.assertEqual(statuses["rust-fmt"], "pending")
        self.assertEqual(statuses["rust-clippy"], "pending")
        self.assertEqual(statuses["rust-test"], "pending")
        # Not `not_applicable`: apps/web, packages/ui and scripts/brand are real npm
        # workspaces that no lane builds. Reporting that as a benign absence is the
        # defect issue 52 records.
        self.assertEqual(statuses["node"], "uncovered")

    def test_uncovered_node_lane_names_every_workspace_nothing_builds(self) -> None:
        node = next(
            check
            for check in self.verifier.planned_checks(ROOT)
            if check.name == "node"
        )

        self.assertIn("apps/web", node.note)
        self.assertIn("issue 52", node.note)
        self.assertEqual(
            self.verifier.node_workspaces(ROOT),
            ["apps/web", "packages/ui", "scripts/brand"],
        )

    def test_node_lane_runs_when_a_root_manifest_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "package.json").write_text("{}")
            (root / "package-lock.json").write_text("{}")

            self.assertEqual(self.verifier.planned_node_check(root).status, "pending")

    def test_node_lane_is_not_applicable_only_when_no_workspace_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            check = self.verifier.planned_node_check(Path(temp_dir))

        self.assertEqual(check.status, "not_applicable")
        self.assertIn("no npm workspace", check.note)

    def test_a_workspace_without_a_lockfile_is_not_counted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "apps" / "ghost").mkdir(parents=True)
            (root / "apps" / "ghost" / "package.json").write_text("{}")

            self.assertEqual(self.verifier.node_workspaces(root), [])

    # -- outcome reporting -------------------------------------------------------------

    def test_uncovered_ranks_below_every_other_recordable_outcome(self) -> None:
        self.assertEqual(
            self.verifier.OUTCOME_ORDER,
            ("uncovered", "not_applicable", "partial", "pass"),
        )
        # `fail` is not recordable, so a failing lane can never be baselined into
        # silence however the record is edited.
        self.assertNotIn("fail", self.verifier.RECORDABLE)

    def test_summary_separates_outcomes_and_disclaims_what_did_not_execute(
        self,
    ) -> None:
        summary = self.verifier.summarise(
            [
                self.verifier.Check("a", "pass", None, 0),
                self.verifier.Check("b", "not_applicable", None, note="nothing to run"),
                self.verifier.Check("c", "uncovered", None, note="nothing runs it"),
            ]
        )

        self.assertEqual(
            summary["outcomes"], {"not_applicable": 1, "pass": 1, "uncovered": 1}
        )
        self.assertEqual(summary["claim_scope"], "executed-lanes-only")
        self.assertIn("executed nothing", summary["claim_note"])
        self.assertEqual(summary["checks"][2]["note"], "nothing runs it")

    def test_eval_matrix_reports_partial_when_suites_execute_nothing(self) -> None:
        check = self.verifier.Check("evaluator-all-suites", "pending", ["list"])
        self.stub_suite_runs(check, ["alpha", "beta", "gamma"], {"alpha": "pass"})

        self.assertEqual(check.status, "partial")
        self.assertEqual(
            check.detail, {"executed": 1, "not_applicable": 2, "failed": 0}
        )
        self.assertIn("1 of 3 suites executed", check.note)

    def test_eval_matrix_passes_only_when_every_suite_executed(self) -> None:
        check = self.verifier.Check("evaluator-all-suites", "pending", ["list"])
        self.stub_suite_runs(check, ["alpha"], {"alpha": "pass"})

        self.assertEqual(check.status, "pass")
        self.assertEqual(
            check.detail, {"executed": 1, "not_applicable": 0, "failed": 0}
        )

    def test_eval_matrix_fails_when_a_suite_fails(self) -> None:
        check = self.verifier.Check("evaluator-all-suites", "pending", ["list"])
        self.stub_suite_runs(
            check, ["alpha", "beta"], {"alpha": "pass", "beta": "fail"}
        )

        self.assertEqual(check.status, "fail")
        self.assertEqual(check.detail["failed"], 1)

    # -- the coverage regression gate --------------------------------------------------
    #
    # A lane can be made to go dark for free: stop invoking it, or let a lane that once
    # ran start reporting it has nothing to do. The recorded ceiling turns that into a
    # failure, while keeping a hole the repository has knowingly accepted from holding a
    # required check permanently red.

    RECORDED = {"alpha": "pass", "beta": "partial", "node": "uncovered"}

    def test_a_matrix_at_its_recorded_ceiling_does_not_fail(self) -> None:
        failures = self.verifier.coverage_regressions(
            self.lanes(alpha="pass", beta="partial", node="uncovered"), self.RECORDED
        )

        self.assertEqual(failures, [])

    def test_a_lane_dropping_below_its_record_is_a_regression(self) -> None:
        for observed in ("uncovered", "not_applicable", "partial"):
            with self.subTest(observed=observed):
                failures = self.verifier.coverage_regressions(
                    self.lanes(alpha=observed, beta="partial", node="uncovered"),
                    self.RECORDED,
                )

                self.assertEqual(len(failures), 1)
                self.assertIn(
                    f"lane alpha regressed from pass to {observed}", failures[0]
                )

    def test_a_partial_lane_falling_to_not_applicable_is_a_regression(self) -> None:
        # The eval lane going from partial to not_applicable would mean every suite
        # stopped executing. That must not read as an absence of work.
        failures = self.verifier.coverage_regressions(
            self.lanes(alpha="pass", beta="not_applicable", node="uncovered"),
            self.RECORDED,
        )

        self.assertEqual(len(failures), 1)
        self.assertIn("lane beta regressed from partial to not_applicable", failures[0])

    def test_a_failing_lane_can_never_be_baselined_away(self) -> None:
        failures = self.verifier.coverage_regressions(
            self.lanes(alpha="fail", beta="partial", node="uncovered"), self.RECORDED
        )

        self.assertEqual(len(failures), 1)
        self.assertIn("lane alpha failed", failures[0])
        self.assertIn("never a recordable outcome", failures[0])

    def test_improving_a_lane_never_fails_and_is_reported(self) -> None:
        checks = self.lanes(alpha="pass", beta="pass", node="pass")

        self.assertEqual(self.verifier.coverage_regressions(checks, self.RECORDED), [])
        self.assertEqual(
            self.verifier.improved_lanes(checks, self.RECORDED), ["beta", "node"]
        )

    def test_deleting_a_recorded_lane_is_a_regression(self) -> None:
        # Otherwise the gate is evaded by removing the lane instead of letting it rot.
        failures = self.verifier.coverage_regressions(
            self.lanes(alpha="pass", beta="partial"), self.RECORDED
        )

        self.assertEqual(len(failures), 1)
        self.assertIn("lane node is recorded", failures[0])
        self.assertIn("no longer plans it", failures[0])

    def test_an_undeclared_new_lane_is_a_regression(self) -> None:
        # Otherwise the gate is evaded by renaming the lane.
        failures = self.verifier.coverage_regressions(
            self.lanes(
                alpha="pass", beta="partial", node="uncovered", ghost="uncovered"
            ),
            self.RECORDED,
        )

        self.assertEqual(len(failures), 1)
        self.assertIn("lane ghost is not recorded", failures[0])

    # -- fail-closed baseline loading --------------------------------------------------

    def test_a_malformed_baseline_fails_closed(self) -> None:
        malformed = {
            "not JSON": "{",
            "not an object": json.dumps([{"node": "uncovered"}]),
            "wrong schema version": json.dumps(
                {"schema_version": 2, "lanes": {"alpha": "pass"}}
            ),
            "no schema version": json.dumps({"lanes": {"alpha": "pass"}}),
            "empty lanes": json.dumps({"schema_version": 1, "lanes": {}}),
            "lanes not an object": json.dumps({"schema_version": 1, "lanes": []}),
            "unrecordable outcome": json.dumps(
                {"schema_version": 1, "lanes": {"alpha": "skipped"}}
            ),
            "a recorded failure": json.dumps(
                {"schema_version": 1, "lanes": {"alpha": "fail"}}
            ),
            "non-string outcome": json.dumps(
                {"schema_version": 1, "lanes": {"alpha": None}}
            ),
            "justifications not an object": json.dumps(
                {"schema_version": 1, "lanes": {"alpha": "pass"}, "justifications": []}
            ),
        }
        for name, text in malformed.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.verifier.load_coverage_baseline(self.write_baseline(text))

    def test_a_recorded_hole_without_a_justification_is_rejected(self) -> None:
        incomplete = (
            {"schema_version": 1, "lanes": {"node": "uncovered"}},
            {
                "schema_version": 1,
                "lanes": {"node": "uncovered"},
                "justifications": {"node": {"note": "no reference"}},
            },
            {
                "schema_version": 1,
                "lanes": {"node": "uncovered"},
                "justifications": {"node": {"reference": "issue 52"}},
            },
        )
        for index, document in enumerate(incomplete):
            with self.subTest(index=index):
                with self.assertRaisesRegex(ValueError, "without a justification"):
                    self.verifier.load_coverage_baseline(
                        self.write_baseline(json.dumps(document))
                    )

    def test_a_missing_baseline_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "unreadable coverage baseline"):
                self.verifier.load_coverage_baseline(Path(temp_dir) / "absent.json")

    # -- exit codes --------------------------------------------------------------------

    def test_a_matrix_at_its_ceiling_exits_zero(self) -> None:
        code, stdout, stderr = self.run_main(
            self.lanes(alpha="pass", node="uncovered"), self.committed_shape_baseline()
        )

        self.assertEqual(code, 0, stderr)
        self.assertIn("verification matrix: PASS", stdout)
        self.assertIn('"regressions": []', stdout)
        self.assertIn("claim_scope=recorded-coverage-only", stdout)

    def test_a_regressed_matrix_exits_one(self) -> None:
        code, stdout, stderr = self.run_main(
            self.lanes(alpha="fail", node="uncovered"), self.committed_shape_baseline()
        )

        self.assertEqual(code, 1)
        self.assertIn("verification matrix: FAIL", stderr)
        self.assertIn("lane alpha failed", stderr)
        self.assertNotIn("verification matrix: PASS", stdout)

    def test_an_improved_matrix_exits_zero_and_offers_to_tighten(self) -> None:
        code, stdout, _stderr = self.run_main(
            self.lanes(alpha="pass", node="pass"), self.committed_shape_baseline()
        )

        self.assertEqual(code, 0)
        self.assertIn("baseline may be tightened", stdout)
        self.assertIn("node", stdout)

    def test_an_unreadable_baseline_exits_two_without_claiming_success(self) -> None:
        code, stdout, stderr = self.run_main(
            self.lanes(alpha="pass"), self.write_baseline("{")
        )

        self.assertEqual(code, 2)
        self.assertIn("invalid coverage baseline", stderr)
        self.assertNotIn("verification matrix: PASS", stdout)

    # -- the repository as committed ---------------------------------------------------

    def test_the_committed_baseline_records_exactly_the_planned_lanes(self) -> None:
        recorded = self.verifier.load_coverage_baseline(BASELINE)
        planned = {check.name for check in self.verifier.planned_checks(ROOT)}

        self.assertEqual(set(recorded), planned)
        self.assertEqual(recorded["node"], "uncovered")
        self.assertEqual(recorded["evaluator-all-suites"], "partial")

    def test_the_committed_baseline_attributes_every_hole_to_a_reference(self) -> None:
        document = json.loads(BASELINE.read_text())

        for lane, outcome in document["lanes"].items():
            if outcome == "pass":
                continue
            justification = document["justifications"][lane]
            self.assertEqual(justification["outcome"], outcome)
            self.assertTrue(justification["reference"])
            self.assertGreater(len(justification["note"]), 80, lane)
        self.assertIn("52", document["justifications"]["node"]["reference"])

    # -- the rest of the matrix --------------------------------------------------------

    def test_root_python_tests_run_from_repository_root(self) -> None:
        verifier = load_verifier()
        evaluator_unit = next(
            check
            for check in verifier.planned_checks(ROOT)
            if check.name == "evaluator-unit"
        )
        with patch.object(verifier.subprocess, "run") as run:
            run.return_value.returncode = 0
            verifier.run_check(evaluator_unit, ROOT)

        self.assertEqual(run.call_args.kwargs["cwd"], ROOT)
        self.assertEqual(evaluator_unit.returncode, 0)

    def test_toolchains_are_pinned_while_ci_stays_manual(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()

        self.assertIn("workflow_dispatch", workflow)
        self.assertIn(
            "Automated build, eval, security, dependency, and release checks are intentionally disabled.",
            workflow,
        )
        self.assertEqual((ROOT / ".node-version").read_text().strip(), "22.23.1")
        self.assertIn('channel = "1.96.0"', (ROOT / "rust-toolchain.toml").read_text())
        self.assertIn("go 1.26.5", (ROOT / "apps" / "api" / "go.mod").read_text())

    def test_gitignore_excludes_generated_outputs_without_excluding_eval_fixtures(
        self,
    ) -> None:
        ignored = (ROOT / ".gitignore").read_text().splitlines()

        self.assertIn("apps/api/api", ignored)
        self.assertIn(".cache/go-build/", ignored)
        self.assertIn("artifacts/evals/", ignored)
        self.assertNotIn("evals/fixtures/", ignored)

    # -- harness -----------------------------------------------------------------------

    def lanes(self, **statuses: str) -> list[object]:
        return [
            self.verifier.Check(name, status, None) for name, status in statuses.items()
        ]

    def committed_shape_baseline(self) -> Path:
        return self.write_baseline(
            json.dumps(
                {
                    "schema_version": 1,
                    "lanes": {"alpha": "pass", "node": "uncovered"},
                    "justifications": {
                        "node": {"reference": "issue 52", "note": "nothing builds it"}
                    },
                }
            )
        )

    def write_baseline(self, text: str) -> Path:
        directory = Path(tempfile.mkdtemp(prefix="coverage-baseline-"))
        self.addCleanup(shutil.rmtree, directory, True)
        path = directory / "coverage-baseline-v1.json"
        path.write_text(text)
        return path

    def run_main(self, planned: list[object], baseline: Path) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(self.verifier, "planned_checks", return_value=planned):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = self.verifier.main(["--baseline", str(baseline)])
        return code, stdout.getvalue(), stderr.getvalue()

    def stub_suite_runs(
        self, check: object, suites: list[str], passing: dict[str, str]
    ) -> None:
        """Drive run_all_suites over a synthetic suite listing."""

        def fake_run(command, **_kwargs):
            class Completed:
                returncode = 0
                stdout = ""

            completed = Completed()
            if "--suite" not in command:
                completed.stdout = "\n".join(suites) + "\n"
                return completed
            suite = command[command.index("--suite") + 1]
            status = passing.get(suite, "not_applicable")
            completed.stdout = json.dumps({"suite": suite, "status": status})
            completed.returncode = 1 if status == "fail" else 0
            return completed

        with patch.object(self.verifier.subprocess, "run", side_effect=fake_run):
            self.verifier.run_all_suites(check, ROOT)


if __name__ == "__main__":
    unittest.main()
