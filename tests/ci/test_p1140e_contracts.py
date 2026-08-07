"""Drift-injection tests for scripts/repository/validate_p1140e_contracts.py.

This validator had no tests. It enforces cross-contract structural agreement —
decision statuses against the P-1140E matrix, operations against the OpenAPI
document, reason authorities against the state-machine registry — and a check
that cannot be shown to fire is not evidence that anything agrees.

These cover the reason-authority rule, which is where the validator had drifted:
its allowlist of non-aggregate authorities was hard-coded and had gone stale.
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
SCHEMAS = ROOT / "packages" / "schemas"


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_p1140e_contracts", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class ReasonAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        directory = Path(tempfile.mkdtemp(prefix="p1140e-"))
        self.addCleanup(shutil.rmtree, directory, True)
        self.schemas = directory / "schemas"
        shutil.copytree(SCHEMAS, self.schemas)
        self.registry = self.schemas / "reason-codes-v1.json"

    def run_validator(self):
        with patch.object(self.validator, "SCHEMAS", self.schemas):
            return self.validator.main()

    def edit(self, mutate) -> None:
        document = json.loads(self.registry.read_text(encoding="utf-8"))
        mutate(document)
        self.registry.write_text(json.dumps(document, indent=2), encoding="utf-8")

    def test_committed_state_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_an_authority_that_resolves_to_nothing_fails(self) -> None:
        self.edit(lambda d: d["codes"][0].update(state_machine="made-up-machine"))

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("authority", str(raised.exception))

    def test_a_declared_authority_no_code_uses_fails(self) -> None:
        """The `device-lineage-v1` case, which survived by being hard-coded.

        It was permitted by the validator and named by zero codes. A declared
        exemption that nothing uses is a stale excuse, and the only reason this
        one lasted is that nothing read the list back.
        """
        self.edit(
            lambda d: d["non_aggregate_authorities"].update(
                {"device-lineage-v1": "reintroduced dead exemption"}
            )
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("authority", str(raised.exception))

    def test_an_authority_shadowing_a_registered_machine_fails(self) -> None:
        """A name meaning two things is worse than a name meaning nothing."""
        self.edit(
            lambda d: d["non_aggregate_authorities"].update(
                {"friendship": "shadows a registered machine"}
            )
        )

        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()

        self.assertIn("shadows", str(raised.exception))

    def test_every_declared_authority_is_absent_from_the_machine_registry(self) -> None:
        """The committed state holds the property the shadow check enforces."""
        registry = json.loads(self.registry.read_text(encoding="utf-8"))
        machines = {
            machine["machine_id"]
            for machine in json.loads(
                (self.schemas / "state-machine-registry-v1.json").read_text("utf-8")
            )["machines"]
        }
        self.assertEqual(set(registry["non_aggregate_authorities"]) & machines, set())

    def test_every_declared_authority_carries_a_reason(self) -> None:
        """A bare list would say which names are allowed and never why."""
        registry = json.loads(self.registry.read_text(encoding="utf-8"))
        for name, reason in registry["non_aggregate_authorities"].items():
            self.assertGreater(len(reason), 80, name)


if __name__ == "__main__":
    unittest.main()
