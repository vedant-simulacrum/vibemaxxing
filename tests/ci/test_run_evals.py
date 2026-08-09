from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from typing import TypeAlias
import unittest

from scripts.ci.eval_validation import (
    ReadySuite,
    evidence_is_current,
    validate_fixture_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "ci" / "run_evals.py"
REGISTRY = ROOT / "evals" / "suites" / "suites.yaml"
BASELINE = ROOT / "evals" / "suites" / "status-baseline-v1.json"
FIXTURE_MANIFEST = "evals/fixtures/runner-test-fixtures.json"
FIXTURE_COMMAND = "evals/fixtures/runner-test-command.py"
# A path that must never exist, so a synthetic not_applicable suite's justification is
# always still standing. Real suites name real absent components.
ABSENT_COMPONENT = "evals/fixtures/runner-test-component-that-never-exists.rs"
RegistryValue: TypeAlias = str | list[str] | list[dict[str, str | list[str]]]


class RunEvalsTests(unittest.TestCase):
    def run_runner(
        self, registry: dict[str, RegistryValue], *args: str, baseline: object = None
    ) -> subprocess.CompletedProcess[str]:
        """Run the runner over a synthetic registry and its sibling status baseline.

        When no baseline is supplied the registry's own statuses are recorded, which is
        the no-drift case: whatever the registry declares is exactly what the ceiling
        remembers. Tests that care about drift pass one explicitly.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            registry_path = temp_path / "suites.yaml"
            output_path = temp_path / "evals"
            registry_path.write_text(json.dumps(registry))
            recorded = (
                baseline
                if isinstance(baseline, str)
                else json.dumps(
                    baseline if baseline is not None else self.baseline_for(registry)
                )
            )
            (temp_path / "status-baseline-v1.json").write_text(recorded)
            return subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--registry",
                    str(registry_path),
                    "--out",
                    str(output_path),
                    *args,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_rejects_registry_missing_blocking_milestone(self) -> None:
        registry = {
            "version": "1",
            "suites": [
                {
                    "id": "sample",
                    "owner": "security",
                    "status": "not_applicable",
                    "reason": "No implementation exists.",
                }
            ],
        }

        result = self.run_runner(registry, "--validate-registry")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blocking_milestone", result.stderr)

    def test_rejects_each_missing_required_metadata_field(self) -> None:
        for field in (
            "id",
            "owner",
            "blocking_milestone",
            "status",
            "reason",
            "authority_class",
            "evidence_ceiling",
        ):
            with self.subTest(field=field):
                registry = self.not_applicable_registry()
                del registry["suites"][0][field]

                result = self.run_runner(registry, "--validate-registry")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field, result.stderr)

    def test_validate_registry_does_not_require_a_suite(self) -> None:
        result = self.run_runner(self.not_applicable_registry(), "--validate-registry")

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_declared_not_applicable_emits_nonpassing_result(self) -> None:
        registry = self.not_applicable_registry()

        result = self.run_runner(registry, "--suite", "sample")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "not_applicable")
        self.assertEqual(payload["cases"], [])
        self.assertEqual(payload["reason"], "No implementation exists.")
        self.assert_timestamped(payload)

    def test_writes_commit_scoped_result_to_absolute_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "absolute-output"
            registry = self.not_applicable_registry()
            registry_path = Path(temp_dir) / "registry.json"
            registry_path.write_text(json.dumps(registry))
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--registry",
                    str(registry_path),
                    "--suite",
                    "sample",
                    "--out",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(
                (output / "sample" / payload["commit"] / "result.json").is_file()
            )

    def test_failed_behavioral_command_fails_the_suite(self) -> None:
        registry = {
            "version": "1",
            "suites": [
                {
                    "id": "sample",
                    "owner": "security",
                    "blocking_milestone": "vertical-slice",
                    "status": "ready",
                    "reason": "",
                    "authority_class": "exploratory-prototype",
                    "evidence_ceiling": "fixture-consistent",
                    "command": [sys.executable, "-c", "raise SystemExit(1)"],
                    "cases": ["rejects-invalid-input"],
                    "fixture_manifest": FIXTURE_MANIFEST,
                    "fixture_ids": ["rejects-invalid-input"],
                }
            ],
        }

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["cases"][0]["status"], "fail")
        self.assert_timestamped(payload)

    def test_command_mismatch_writes_timestamped_failure_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "evals"
            result = self.run_runner(
                self.ready_registry(["not-an-evaluator-command"]),
                "--suite",
                "sample",
                "--out",
                str(output),
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(
                payload["cases"], [{"id": "rejects-invalid-input", "status": "fail"}]
            )
            self.assertIn("command does not match", payload["reason"])
            self.assert_timestamped(payload)
            self.assertTrue(
                (output / "sample" / payload["commit"] / "result.json").is_file()
            )

    def test_rejects_malformed_behavioral_evidence(self) -> None:
        registry = self.ready_registry([sys.executable, "-c", "print('{}')"])

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_evidence_for_a_different_commit(self) -> None:
        evidence = json.dumps(
            {
                "status": "pass",
                "suite": "sample",
                "commit": "stale",
                "started_at": "2026-01-01T00:00:00+00:00",
                "finished_at": "2026-01-01T00:00:01+00:00",
                "cases": [{"id": "rejects-invalid-input", "status": "pass"}],
            }
        )
        registry = self.ready_registry([sys.executable, "-c", f"print({evidence!r})"])

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_evidence_without_version_one(self) -> None:
        evidence = self.valid_evidence()
        del evidence["version"]

        result = self.run_ready_evidence(evidence)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_evidence_with_wrong_version(self) -> None:
        evidence = self.valid_evidence()
        evidence["version"] = "2"

        result = self.run_ready_evidence(evidence)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_evidence_with_invalid_suite(self) -> None:
        evidence = self.valid_evidence()
        evidence["suite"] = "other"

        result = self.run_ready_evidence(evidence)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_malformed_future_stale_and_reversed_evidence_timestamps(
        self,
    ) -> None:
        now = datetime.now(timezone.utc)
        timestamp_cases = {
            "malformed": ("not-a-timestamp", now.isoformat()),
            "future": (
                (now + timedelta(hours=1)).isoformat(),
                (now + timedelta(hours=1, seconds=1)).isoformat(),
            ),
            "stale": (
                (now - timedelta(days=2)).isoformat(),
                (now - timedelta(days=2, seconds=-1)).isoformat(),
            ),
            "reversed": (now.isoformat(), (now - timedelta(seconds=1)).isoformat()),
        }
        for name, (started_at, finished_at) in timestamp_cases.items():
            with self.subTest(name=name):
                evidence = self.valid_evidence()
                evidence["started_at"] = started_at
                evidence["finished_at"] = finished_at

                result = self.run_ready_evidence(evidence)

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_evidence_with_stale_start_and_current_finish(self) -> None:
        evidence = self.fixture_bound_evidence()
        now = datetime.now(timezone.utc)
        evidence["started_at"] = (now - timedelta(hours=25)).isoformat()
        evidence["finished_at"] = now.isoformat()
        ready = ReadySuite(
            "sample",
            tuple(self.fixture_command()),
            ("rejects-invalid-input",),
            Path(FIXTURE_MANIFEST),
            ("rejects-invalid-input",),
        )
        binding = validate_fixture_manifest(ready)

        self.assertFalse(
            evidence_is_current(evidence, ready, self.current_commit(), binding, now)
        )

    def test_rejects_evidence_cases_that_are_not_exact_declared_ordered_passes(
        self,
    ) -> None:
        invalid_cases = (
            [{"id": "unexpected", "status": "pass"}],
            [{"id": "rejects-invalid-input", "status": "fail"}],
            [
                {"id": "rejects-invalid-input", "status": "pass"},
                {"id": "rejects-invalid-input", "status": "pass"},
            ],
        )
        for cases in invalid_cases:
            with self.subTest(cases=cases):
                evidence = self.valid_evidence()
                evidence["cases"] = cases

                result = self.run_ready_evidence(evidence)

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_ready_suite_without_fixture_manifest(self) -> None:
        registry = self.ready_registry([sys.executable, "-c", "print('{}')"])
        del registry["suites"][0]["fixture_manifest"]

        result = self.run_runner(registry, "--validate-registry")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fixture_manifest", result.stderr)

    def test_rejects_valid_evidence_when_fixture_manifest_digest_mismatches(
        self,
    ) -> None:
        registry = self.ready_registry(
            [sys.executable, "-c", f"print({json.dumps(self.valid_evidence())!r})"]
        )
        registry["suites"][0]["fixture_manifest"] = (
            "evals/fixtures/runner-test-fixtures-bad-digest.json"
        )

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_suite_ids_that_cannot_be_output_filenames(self) -> None:
        for suite_id in ("../escape", "/tmp/escape", "UPPER", "contains_space"):
            with self.subTest(suite_id=suite_id):
                registry = self.not_applicable_registry()
                registry["suites"][0]["id"] = suite_id

                result = self.run_runner(registry, "--validate-registry")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("suite id", result.stderr)

    def test_rejects_static_forged_evidence_without_fixture_binding(self) -> None:
        result = self.run_ready_evidence(self.valid_evidence())

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_rejects_fixture_bound_evidence_from_command_not_declared_by_manifest(
        self,
    ) -> None:
        registry = self.ready_registry(
            [
                sys.executable,
                "-c",
                f"print({json.dumps(self.fixture_bound_evidence())!r})",
            ]
        )

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(
            payload["cases"], [{"id": "rejects-invalid-input", "status": "fail"}]
        )
        self.assertIn("command does not match", payload["reason"])
        self.assert_timestamped(payload)

    def test_accepts_current_complete_fixture_bound_behavioral_evidence(self) -> None:
        registry = self.ready_registry(self.fixture_command())

        result = self.run_runner(registry, "--suite", "sample")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_checked_in_manifest_without_commit_uses_current_evidence_commit(
        self,
    ) -> None:
        registry = self.ready_registry(self.fixture_command())

        result = self.run_runner(registry, "--suite", "sample")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["commit"], self.current_commit())

    def test_rejects_command_placeholder_other_than_commit(self) -> None:
        registry = self.ready_registry(
            ["python3", "evals/fixtures/runner-test-command.py", "{suite}"]
        )
        registry["suites"][0]["fixture_manifest"] = (
            "evals/fixtures/runner-test-invalid-placeholder.json"
        )

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("placeholder", json.loads(result.stdout)["reason"])

    def test_rejects_shell_command_before_execution(self) -> None:
        registry = self.ready_registry(["bash", "-lc", "echo forged"])
        registry["suites"][0]["fixture_manifest"] = (
            "evals/fixtures/runner-test-shell-command.json"
        )

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("shell", json.loads(result.stdout)["reason"])

    def test_rejects_absolute_shell_command_during_manifest_validation(self) -> None:
        ready = ReadySuite(
            "sample",
            ("/bin/sh", "-lc", "echo forged"),
            ("rejects-invalid-input",),
            Path("evals/fixtures/runner-test-absolute-shell-command.json"),
            ("rejects-invalid-input",),
        )

        with self.assertRaisesRegex(ValueError, "shell"):
            validate_fixture_manifest(ready)

    def test_rejects_missing_fixture_before_execution(self) -> None:
        registry = self.ready_registry(self.fixture_command())
        registry["suites"][0]["fixture_manifest"] = (
            "evals/fixtures/runner-test-missing-fixture.json"
        )

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checked-in repository file", json.loads(result.stdout)["reason"])

    def test_all_registered_suites_write_timestamped_results_matching_their_status(
        self,
    ) -> None:
        suites = subprocess.run(
            [sys.executable, str(RUNNER), "--list-suites"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "evals"
            for suite in suites:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(RUNNER),
                        "--suite",
                        suite,
                        "--out",
                        str(output),
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                payload = json.loads(result.stdout)
                self.assertIn(payload["status"], {"pass", "not_applicable"})
                self.assert_timestamped(payload)
            self.assertEqual(
                sorted(output.glob("*/" + self.current_commit() + "/result.json")),
                sorted(
                    output / suite / self.current_commit() / "result.json"
                    for suite in suites
                ),
            )

    # -- status regression gate --------------------------------------------------------
    #
    # The registry is trivially made greener by downgrading a suite: delete the command,
    # write a sentence of prose, and the runner returns 0 for a suite that now executes
    # nothing. These tests prove the recorded ceiling in
    # evals/suites/status-baseline-v1.json turns that into a failure, and that the
    # opposite move never does.

    def test_downgrading_a_ready_suite_fails_registry_validation(self) -> None:
        result = self.run_runner(
            self.not_applicable_registry(),
            "--validate-registry",
            baseline={"schema_version": 1, "suites": {"sample": "ready"}},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("regressed from ready to not_applicable", result.stderr)

    def test_upgrading_a_suite_to_ready_never_fails_registry_validation(self) -> None:
        result = self.run_runner(
            self.ready_registry(self.fixture_command()),
            "--validate-registry",
            baseline={"schema_version": 1, "suites": {"sample": "not_applicable"}},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("baseline may be tightened", result.stdout)

    def test_an_unchanged_registry_passes_registry_validation(self) -> None:
        for name, registry in (
            ("ready", self.ready_registry(self.fixture_command())),
            ("not_applicable", self.not_applicable_registry()),
        ):
            with self.subTest(name=name):
                result = self.run_runner(registry, "--validate-registry")

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("eval registry validation: PASS", result.stdout)

    def test_deleting_a_recorded_suite_fails_registry_validation(self) -> None:
        # Otherwise the gate is evaded by removing the suite instead of downgrading it.
        result = self.run_runner(
            self.not_applicable_registry(),
            "--validate-registry",
            baseline={
                "schema_version": 1,
                "suites": {"sample": "not_applicable", "vanished": "ready"},
            },
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("no longer declares it", result.stderr)

    def test_an_unrecorded_suite_fails_registry_validation(self) -> None:
        # Otherwise the gate is evaded by renaming the suite.
        result = self.run_runner(
            self.not_applicable_registry(),
            "--validate-registry",
            baseline={"schema_version": 1, "suites": {"other": "not_applicable"}},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("is not recorded in the status baseline", result.stderr)

    def test_a_malformed_baseline_fails_closed(self) -> None:
        malformed = {
            "not JSON": "{",
            "not an object": json.dumps([{"sample": "ready"}]),
            "wrong schema version": json.dumps(
                {"schema_version": 2, "suites": {"sample": "not_applicable"}}
            ),
            "no schema version": json.dumps({"suites": {"sample": "not_applicable"}}),
            "empty suites": json.dumps({"schema_version": 1, "suites": {}}),
            "suites not an object": json.dumps({"schema_version": 1, "suites": []}),
            "invalid recorded status": json.dumps(
                {"schema_version": 1, "suites": {"sample": "skipped"}}
            ),
            "non-string recorded status": json.dumps(
                {"schema_version": 1, "suites": {"sample": None}}
            ),
        }
        for name, recorded in malformed.items():
            with self.subTest(name=name):
                result = self.run_runner(
                    self.not_applicable_registry(),
                    "--validate-registry",
                    baseline=recorded,
                )

                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn("invalid eval status baseline", result.stderr)

    def test_a_missing_baseline_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            registry_path = Path(temp_dir) / "suites.yaml"
            registry_path.write_text(json.dumps(self.not_applicable_registry()))
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--registry",
                    str(registry_path),
                    "--validate-registry",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unreadable status baseline", result.stderr)

    def test_the_committed_registry_matches_the_committed_baseline(self) -> None:
        recorded = json.loads(BASELINE.read_text())["suites"]

        result = subprocess.run(
            [sys.executable, str(RUNNER), "--validate-registry"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            sorted(recorded),
            sorted(re.findall(r"^- id: (\S+)$", REGISTRY.read_text(), re.M)),
        )
        self.assertEqual(
            sorted(name for name, status in recorded.items() if status == "ready"),
            [
                "ranking-accounting",
                "shadow-codec-parity",
                "token-accounting-conformance",
            ],
            "the recorded ready set changed; update the baseline deliberately",
        )

    # -- authority class and evidence ceiling ------------------------------------------
    #
    # Both keys arrived in commit 31a6539 to satisfy validate_p1140f_authority.py and
    # were then read by nothing here: the allowlist admitted them and no rule bounded
    # them, so any of the twenty-four not_applicable suites could have declared
    # production-evidence. These tests are each a way that is now refused.

    def test_a_not_applicable_suite_may_claim_no_evidence_at_all(self) -> None:
        """The rule AGENTS.md states as prose: an eval suite reported as
        not_applicable is an absence of evidence, never a pass."""
        registry = self.not_applicable_registry()
        registry["suites"][0]["evidence_ceiling"] = "fixture-consistent"

        result = self.run_runner(registry, "--validate-registry")

        self.assertEqual(result.returncode, 1)
        self.assertIn("capped at none by the not_applicable status", result.stderr)

    def test_an_authority_class_caps_the_ceiling(self) -> None:
        registry = self.ready_registry(self.fixture_command())
        registry["suites"][0]["evidence_ceiling"] = "normative-conformance"

        result = self.run_runner(registry, "--validate-registry")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "capped at cross-language-parity by authority class exploratory-prototype",
            result.stderr,
        )

    def test_a_ready_suite_is_capped_by_its_fixture_manifest(self) -> None:
        registry = self.ready_registry(self.fixture_command())
        registry["suites"][0]["evidence_ceiling"] = "cross-language-parity"

        result = self.run_runner(registry, "--validate-registry")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"capped at fixture-consistent by its fixture manifest {FIXTURE_MANIFEST}",
            result.stderr,
        )

    def test_a_manifest_that_binds_no_fixture_caps_the_suite_at_none(self) -> None:
        """Absence must lower the ceiling rather than leave it unexamined.

        A ceiling check phrased as "the fixtures must not contradict the claim" is
        satisfied for free by a suite with no fixtures, which is this repository's
        recurring defect. So the cap is derived from what the manifest binds.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "empty-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "version": "1",
                        "suite": "sample",
                        "command": self.fixture_command(),
                        "fixtures": [],
                    }
                )
            )
            registry = self.ready_registry(self.fixture_command())
            registry["suites"][0]["fixture_manifest"] = str(manifest)
            registry["suites"][0]["evidence_ceiling"] = "fixture-consistent"

            result = self.run_runner(registry, "--validate-registry")

            self.assertEqual(result.returncode, 1)
            self.assertIn("capped at none by its fixture manifest", result.stderr)

    def test_an_undeclared_authority_class_or_ceiling_fails(self) -> None:
        for field, value in (
            ("authority_class", "definitely-fine"),
            ("evidence_ceiling", "launch-ready"),
        ):
            with self.subTest(field=field):
                registry = self.not_applicable_registry()
                registry["suites"][0][field] = value

                result = self.run_runner(registry, "--validate-registry")

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    f"declares {field} {value!r}, which conformance/p1140f/artifact-authority-v1.json does not declare",
                    result.stderr,
                )

    def test_a_ready_suite_whose_manifest_cannot_be_read_fails(self) -> None:
        registry = self.ready_registry(self.fixture_command())
        registry["suites"][0]["fixture_manifest"] = (
            "evals/fixtures/no-such-manifest.json"
        )

        result = self.run_runner(registry, "--validate-registry")

        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot be read to bound its evidence ceiling", result.stderr)

    def test_every_committed_suite_carries_a_class_and_a_ceiling(self) -> None:
        text = REGISTRY.read_text()
        self.assertEqual(len(re.findall(r"^- id: ", text, re.M)), 27)
        self.assertEqual(len(re.findall(r"^  authority_class: ", text, re.M)), 27)
        self.assertEqual(len(re.findall(r"^  evidence_ceiling: ", text, re.M)), 27)

    def test_the_registry_ceilings_match_what_the_runner_reports_as_evidence(
        self,
    ) -> None:
        """`run_phase1_evidence.py` stamps a class and a ceiling onto the evidence it
        emits. A registry declaring one thing while the runner emits another is two
        answers to one question, which is how the two ceiling keys drifted in the
        first place."""
        runner = importlib.import_module("scripts.ci.run_phase1_evidence")
        declared = {
            suite: (record["authority_class"], record["evidence_ceiling"])
            for suite, record in self.committed_suites().items()
            if record["status"] == "ready"
        }
        emitted = {
            suite: (entry[3], entry[4]) for suite, entry in runner.SUITES.items()
        }
        self.assertEqual(declared, emitted)

    @staticmethod
    def committed_suites() -> dict[str, dict[str, str]]:
        suites: dict[str, dict[str, str]] = {}
        current: dict[str, str] | None = None
        for line in REGISTRY.read_text().splitlines()[2:]:
            if line.startswith("- id: "):
                current = {}
                suites[line.removeprefix("- id: ").strip()] = current
            elif current is not None and line.startswith("  ") and ": " in line:
                key, _, value = line.strip().partition(": ")
                current[key] = value.strip().strip('"')
        return suites

    # -- not_applicable justification --------------------------------------------------

    def test_not_applicable_requires_a_machine_checkable_justification(self) -> None:
        registry = self.not_applicable_registry()
        del registry["suites"][0]["not_applicable_until"]

        result = self.run_runner(registry, "--validate-registry")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not_applicable_until", result.stderr)

    def test_not_applicable_fails_once_the_named_component_exists(self) -> None:
        registry = self.not_applicable_registry()
        registry["suites"][0]["not_applicable_until"] = ["scripts/ci/run_evals.py"]

        result = self.run_runner(registry, "--validate-registry")

        self.assertEqual(result.returncode, 1)
        self.assertIn("its owning component exists", result.stderr)

    def test_running_a_stale_not_applicable_suite_fails_rather_than_skipping(
        self,
    ) -> None:
        registry = self.not_applicable_registry()
        registry["suites"][0]["not_applicable_until"] = ["scripts/ci/run_evals.py"]

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn("its owning component exists", payload["reason"])

    def test_rejects_unusable_not_applicable_until_paths(self) -> None:
        for candidate in (
            "/etc/passwd",
            "../outside/thing.rs",
            "crates\\core\\lib.rs",
            "crates/vibeproof-sync/",
            " crates/vibeproof-sync/src/lib.rs",
        ):
            with self.subTest(candidate=candidate):
                registry = self.not_applicable_registry()
                registry["suites"][0]["not_applicable_until"] = [candidate]

                result = self.run_runner(registry, "--validate-registry")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unusable", result.stderr)

    def test_rejects_repeated_and_empty_not_applicable_until_entries(self) -> None:
        for name, value in (
            ("repeated", [ABSENT_COMPONENT, ABSENT_COMPONENT]),
            ("empty list", []),
            ("empty string", [""]),
            ("not a list", ABSENT_COMPONENT),
        ):
            with self.subTest(name=name):
                registry = self.not_applicable_registry()
                registry["suites"][0]["not_applicable_until"] = value

                result = self.run_runner(registry, "--validate-registry")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("not_applicable_until", result.stderr)

    def test_a_ready_suite_cannot_declare_an_absence_justification(self) -> None:
        registry = self.ready_registry(self.fixture_command())
        registry["suites"][0]["not_applicable_until"] = [ABSENT_COMPONENT]

        result = self.run_runner(registry, "--validate-registry")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot declare not_applicable_until", result.stderr)

    def test_every_committed_not_applicable_suite_names_an_absent_component(
        self,
    ) -> None:
        declared = re.findall(
            r"^  not_applicable_until: (\[.*\])$", REGISTRY.read_text(), re.M
        )
        recorded = json.loads(BASELINE.read_text())["suites"]

        self.assertEqual(
            len(declared),
            sum(1 for status in recorded.values() if status == "not_applicable"),
            "every not_applicable suite must name what its status waits on",
        )
        for entry in declared:
            for candidate in json.loads(entry):
                self.assertFalse(
                    (ROOT / candidate).exists(),
                    f"{candidate} exists, so the suite waiting on it is no longer not_applicable",
                )

    @staticmethod
    def not_applicable_registry() -> dict[str, RegistryValue]:
        return {
            "version": "1",
            "suites": [
                {
                    "id": "sample",
                    "owner": "security",
                    "blocking_milestone": "vertical-slice",
                    "status": "not_applicable",
                    "reason": "No implementation exists.",
                    "authority_class": "absent",
                    "evidence_ceiling": "none",
                    "not_applicable_until": [ABSENT_COMPONENT],
                }
            ],
        }

    @staticmethod
    def baseline_for(registry: dict[str, RegistryValue]) -> dict[str, object]:
        """Record exactly what the registry declares, so nothing has drifted."""
        suites = registry["suites"]
        assert isinstance(suites, list)
        return {
            "schema_version": 1,
            "suites": {
                suite["id"]: suite["status"]
                for suite in suites
                if isinstance(suite.get("id"), str)
                and isinstance(suite.get("status"), str)
            },
        }

    @staticmethod
    def ready_registry(command: list[str]) -> dict[str, RegistryValue]:
        return {
            "version": "1",
            "suites": [
                {
                    "id": "sample",
                    "owner": "security",
                    "blocking_milestone": "vertical-slice",
                    "status": "ready",
                    "reason": "",
                    "authority_class": "exploratory-prototype",
                    "evidence_ceiling": "fixture-consistent",
                    "command": command,
                    "cases": ["rejects-invalid-input"],
                    "fixture_manifest": FIXTURE_MANIFEST,
                    "fixture_ids": ["rejects-invalid-input"],
                }
            ],
        }

    @staticmethod
    def valid_evidence() -> dict[str, str | list[dict[str, str]]]:
        commit = RunEvalsTests.current_commit()
        now = datetime.now(timezone.utc)
        return {
            "version": "1",
            "status": "pass",
            "suite": "sample",
            "commit": commit,
            "started_at": now.isoformat(),
            "finished_at": (now + timedelta(seconds=1)).isoformat(),
            "cases": [{"id": "rejects-invalid-input", "status": "pass"}],
        }

    @staticmethod
    def fixture_bound_evidence() -> dict[str, object]:
        manifest_text = (ROOT / FIXTURE_MANIFEST).read_text()
        fixture = json.loads(manifest_text)["fixtures"][0]
        evidence = RunEvalsTests.valid_evidence()
        evidence["fixtures"] = {
            "manifest_sha256": hashlib.sha256(manifest_text.encode()).hexdigest(),
            "fixtures": [{"id": fixture["id"], "sha256": fixture["sha256"]}],
        }
        return evidence

    @staticmethod
    def fixture_command() -> list[str]:
        return json.loads((ROOT / FIXTURE_MANIFEST).read_text())["command"]

    @staticmethod
    def current_commit() -> str:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()

    def assert_timestamped(self, payload: dict[str, object]) -> None:
        started_at = datetime.fromisoformat(
            str(payload["started_at"]).replace("Z", "+00:00")
        )
        finished_at = datetime.fromisoformat(
            str(payload["finished_at"]).replace("Z", "+00:00")
        )
        self.assertLessEqual(started_at, finished_at)

    def run_ready_evidence(
        self, evidence: dict[str, str | list[dict[str, str]]]
    ) -> subprocess.CompletedProcess[str]:
        return self.run_runner(
            self.ready_registry(
                [sys.executable, "-c", f"print({json.dumps(evidence)!r})"]
            ),
            "--suite",
            "sample",
        )


if __name__ == "__main__":
    unittest.main()
