from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts" / "ci" / "generate_gate_ledger.py"
COMMIT = "a" * 40
# A component that must never exist, so these suites stay legitimately not_applicable.
ABSENT = "evals/fixtures/ledger-test-component-that-never-exists.rs"


class GateLedgerTests(unittest.TestCase):
    def test_writes_ordered_complete_entries_with_only_valid_result_links(self) -> None:
        registry = {
            "version": "1",
            "suites": [
                {"id": "first", "owner": "security", "blocking_milestone": "g0", "status": "not_applicable", "reason": "Not built.", "authority_class": "absent", "evidence_ceiling": "none", "not_applicable_until": [ABSENT]},
                {"id": "second", "owner": "backend", "blocking_milestone": "g1", "status": "not_applicable", "reason": "Not built.", "authority_class": "absent", "evidence_ceiling": "none", "not_applicable_until": [ABSENT]},
            ],
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            registry_path = temporary_path / "suites.json"
            output_path = temporary_path / "ledger.json"
            results_path = temporary_path / "results"
            registry_path.write_text(json.dumps(registry))
            valid_result = results_path / "second" / COMMIT / "result.json"
            valid_result.parent.mkdir(parents=True)
            valid_result.write_text(json.dumps({"suite": "second", "commit": COMMIT}))

            result = subprocess.run(
                [sys.executable, str(GENERATOR), "--registry", str(registry_path), "--out", str(output_path), "--results", str(results_path), "--commit", COMMIT, "--generated-at", "2026-01-01T00:00:00+00:00"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output_path.read_text())
            self.assertEqual(payload["registry_version"], "1")
            self.assertEqual(payload["commit"], COMMIT)
            self.assertEqual(payload["generated_at"], "2026-01-01T00:00:00+00:00")
            self.assertEqual([entry["id"] for entry in payload["suites"]], ["first", "second"])
            self.assertEqual(
                payload["suites"],
                [
                    {"id": "first", "owner": "security", "blocking_milestone": "g0", "status": "not_applicable", "reason": "Not built.", "result_path": None},
                    {"id": "second", "owner": "backend", "blocking_milestone": "g1", "status": "not_applicable", "reason": "Not built.", "result_path": f"artifacts/evals/second/{COMMIT}/result.json"},
                ],
            )

    def test_rejects_malformed_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            registry_path = temporary_path / "suites.json"
            registry_path.write_text(json.dumps({"version": "1", "suites": [{"id": "duplicate", "owner": "security", "status": "not_applicable", "reason": "Not built."}]}))

            result = subprocess.run(
                [sys.executable, str(GENERATOR), "--registry", str(registry_path), "--out", str(temporary_path / "ledger.json"), "--commit", COMMIT],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("blocking_milestone", result.stderr)


if __name__ == "__main__":
    unittest.main()
