from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "scripts" / "ci" / "verify_repository.py"


def load_verifier() -> object:
    specification = importlib.util.spec_from_file_location("verify_repository", VERIFIER)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class VerifyRepositoryTests(unittest.TestCase):
    def test_selects_go_and_rust_and_marks_node_not_applicable(self) -> None:
        verifier = load_verifier()

        checks = verifier.planned_checks(ROOT)
        statuses = {check.name: check.status for check in checks}

        self.assertEqual(statuses["go-test"], "pending")
        self.assertEqual(statuses["go-vet"], "pending")
        self.assertEqual(statuses["go-build"], "pending")
        self.assertEqual(statuses["rust-fmt"], "pending")
        self.assertEqual(statuses["rust-clippy"], "pending")
        self.assertEqual(statuses["rust-test"], "pending")
        self.assertEqual(statuses["node"], "not_applicable")

    def test_root_python_tests_run_from_repository_root(self) -> None:
        verifier = load_verifier()
        evaluator_unit = next(check for check in verifier.planned_checks(ROOT) if check.name == "evaluator-unit")
        with patch.object(verifier.subprocess, "run") as run:
            run.return_value.returncode = 0
            verifier.run_check(evaluator_unit, ROOT)

        self.assertEqual(run.call_args.kwargs["cwd"], ROOT)
        self.assertEqual(evaluator_unit.returncode, 0)

    def test_toolchains_are_pinned_while_ci_stays_manual(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()

        self.assertIn("workflow_dispatch", workflow)
        self.assertIn("Automated build, eval, security, dependency, and release checks are intentionally disabled.", workflow)
        self.assertEqual((ROOT / ".node-version").read_text().strip(), "22.23.1")
        self.assertIn('channel = "1.96.0"', (ROOT / "rust-toolchain.toml").read_text())
        self.assertIn("go 1.26.0", (ROOT / "apps" / "api" / "go.mod").read_text())

    def test_gitignore_excludes_generated_outputs_without_excluding_eval_fixtures(self) -> None:
        ignored = (ROOT / ".gitignore").read_text().splitlines()

        self.assertIn("apps/api/api", ignored)
        self.assertIn(".cache/go-build/", ignored)
        self.assertIn("artifacts/evals/", ignored)
        self.assertNotIn("evals/fixtures/", ignored)


if __name__ == "__main__":
    unittest.main()
