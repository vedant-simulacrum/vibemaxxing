from __future__ import annotations

import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from typing import TypeAlias
import unittest

from scripts.ci.eval_validation import ReadySuite, evidence_is_current, validate_fixture_manifest


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "ci" / "run_evals.py"
FIXTURE_MANIFEST = "evals/fixtures/runner-test-fixtures.json"
FIXTURE_COMMAND = "evals/fixtures/runner-test-command.py"
RegistryValue: TypeAlias = str | list[str] | list[dict[str, str | list[str]]]


class RunEvalsTests(unittest.TestCase):
    def run_runner(self, registry: dict[str, RegistryValue], *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            registry_path = temp_path / "suites.yaml"
            output_path = temp_path / "evals"
            registry_path.write_text(json.dumps(registry))
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
        for field in ("id", "owner", "blocking_milestone", "status", "reason"):
            with self.subTest(field=field):
                registry = self.not_applicable_registry()
                del registry["suites"][0][field]

                result = self.run_runner(registry, "--validate-registry")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field, result.stderr)

    def test_validate_registry_does_not_require_a_suite(self) -> None:
        registry = {
            "version": "1",
            "suites": [
                {
                    "id": "sample",
                    "owner": "security",
                    "blocking_milestone": "vertical-slice",
                    "status": "not_applicable",
                    "reason": "No implementation exists.",
                }
            ],
        }

        result = self.run_runner(registry, "--validate-registry")

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
                [sys.executable, str(RUNNER), "--registry", str(registry_path), "--suite", "sample", "--out", str(output)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue((output / "sample" / payload["commit"] / "result.json").is_file())

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
            result = self.run_runner(self.ready_registry(["not-an-evaluator-command"]), "--suite", "sample", "--out", str(output))

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(payload["cases"], [{"id": "rejects-invalid-input", "status": "fail"}])
            self.assertIn("command does not match", payload["reason"])
            self.assert_timestamped(payload)
            self.assertTrue((output / "sample" / payload["commit"] / "result.json").is_file())

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

    def test_rejects_malformed_future_stale_and_reversed_evidence_timestamps(self) -> None:
        now = datetime.now(timezone.utc)
        timestamp_cases = {
            "malformed": ("not-a-timestamp", now.isoformat()),
            "future": ((now + timedelta(hours=1)).isoformat(), (now + timedelta(hours=1, seconds=1)).isoformat()),
            "stale": ((now - timedelta(days=2)).isoformat(), (now - timedelta(days=2, seconds=-1)).isoformat()),
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
        ready = ReadySuite("sample", tuple(self.fixture_command()), ("rejects-invalid-input",), Path(FIXTURE_MANIFEST), ("rejects-invalid-input",))
        binding = validate_fixture_manifest(ready)

        self.assertFalse(evidence_is_current(evidence, ready, self.current_commit(), binding, now))

    def test_rejects_evidence_cases_that_are_not_exact_declared_ordered_passes(self) -> None:
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

    def test_rejects_valid_evidence_when_fixture_manifest_digest_mismatches(self) -> None:
        registry = self.ready_registry([sys.executable, "-c", f"print({json.dumps(self.valid_evidence())!r})"])
        registry["suites"][0]["fixture_manifest"] = "evals/fixtures/runner-test-fixtures-bad-digest.json"

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

    def test_rejects_fixture_bound_evidence_from_command_not_declared_by_manifest(self) -> None:
        registry = self.ready_registry([sys.executable, "-c", f"print({json.dumps(self.fixture_bound_evidence())!r})"])

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["cases"], [{"id": "rejects-invalid-input", "status": "fail"}])
        self.assertIn("command does not match", payload["reason"])
        self.assert_timestamped(payload)

    def test_accepts_current_complete_fixture_bound_behavioral_evidence(self) -> None:
        registry = self.ready_registry(self.fixture_command())

        result = self.run_runner(registry, "--suite", "sample")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_checked_in_manifest_without_commit_uses_current_evidence_commit(self) -> None:
        registry = self.ready_registry(self.fixture_command())

        result = self.run_runner(registry, "--suite", "sample")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["commit"], self.current_commit())

    def test_rejects_command_placeholder_other_than_commit(self) -> None:
        registry = self.ready_registry(["python3", "evals/fixtures/runner-test-command.py", "{suite}"])
        registry["suites"][0]["fixture_manifest"] = "evals/fixtures/runner-test-invalid-placeholder.json"

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("placeholder", json.loads(result.stdout)["reason"])

    def test_rejects_shell_command_before_execution(self) -> None:
        registry = self.ready_registry(["bash", "-lc", "echo forged"])
        registry["suites"][0]["fixture_manifest"] = "evals/fixtures/runner-test-shell-command.json"

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
        registry["suites"][0]["fixture_manifest"] = "evals/fixtures/runner-test-missing-fixture.json"

        result = self.run_runner(registry, "--suite", "sample")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checked-in repository file", json.loads(result.stdout)["reason"])

    def test_all_registered_suites_write_timestamped_results_matching_their_status(self) -> None:
        suites = subprocess.run([sys.executable, str(RUNNER), "--list-suites"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "evals"
            for suite in suites:
                result = subprocess.run([sys.executable, str(RUNNER), "--suite", suite, "--out", str(output)], cwd=ROOT, capture_output=True, text=True, check=False)
                payload = json.loads(result.stdout)
                self.assertIn(payload["status"], {"pass", "not_applicable"})
                self.assert_timestamped(payload)
            self.assertEqual(sorted(output.glob("*/" + self.current_commit() + "/result.json")), sorted(output / suite / self.current_commit() / "result.json" for suite in suites))

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
                }
            ],
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
        started_at = datetime.fromisoformat(str(payload["started_at"]).replace("Z", "+00:00"))
        finished_at = datetime.fromisoformat(str(payload["finished_at"]).replace("Z", "+00:00"))
        self.assertLessEqual(started_at, finished_at)

    def run_ready_evidence(self, evidence: dict[str, str | list[dict[str, str]]]) -> subprocess.CompletedProcess[str]:
        return self.run_runner(self.ready_registry([sys.executable, "-c", f"print({json.dumps(evidence)!r})"]), "--suite", "sample")


if __name__ == "__main__":
    unittest.main()
