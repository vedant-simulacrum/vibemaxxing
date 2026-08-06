"""Tests for the D-242 conformance manifest stage.

These prove the stage fails when a manifest names a fixture that is absent, when a
fixture is present and no manifest names it, when a recorded digest goes stale, when an
authority or an authority clause does not resolve, when a case identifier is duplicated
or wrongly prefixed, when a suite declares no manifest at all, and when a populated
suite neither declares a negative case nor records why it has none.

Validating a manifest is not conformance. Nothing here executes a fixture against an
implementation, because no runner exists in any language.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"

IGNORED = shutil.ignore_patterns(
    ".git", ".venv", "node_modules", "target", "__pycache__", "assets", "artifacts"
)


def load_validator() -> object:
    specification = importlib.util.spec_from_file_location(
        "validate_planning_artifacts", VALIDATOR
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class ConformanceManifestTests(unittest.TestCase):
    """Each test mutates a full copy of the tree, because the stage resolves paths
    against the repository root and a partial copy would prove the wrong thing."""

    def setUp(self) -> None:
        self.validator = load_validator()
        parent = Path(tempfile.mkdtemp(prefix="conformance-manifests-"))
        self.addCleanup(shutil.rmtree, parent, True)
        self.root = parent / "repository"
        for relative in ("conformance", "packages", "docs", "evals", "scripts"):
            shutil.copytree(
                ROOT / relative, self.root / relative, ignore=IGNORED, symlinks=True
            )
        self.validator.ROOT = self.root
        self.validator.SCHEMAS = self.root / "packages" / "schemas"
        self.validator.CONFORMANCE = self.root / "conformance"

    def manifest_path(self, suite: str) -> Path:
        if suite == "vibeproof":
            return self.root / "conformance" / "vibeproof" / "v1" / "manifest.json"
        return self.root / "conformance" / suite / "manifest.json"

    def read(self, suite: str) -> dict:
        return json.loads(self.manifest_path(suite).read_text(encoding="utf-8"))

    def write(self, suite: str, manifest: dict) -> None:
        self.manifest_path(suite).write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )

    def assert_fails(self, fragment: str) -> None:
        with self.assertRaises(Exception) as caught:
            self.validator.validate_conformance_manifests()
        self.assertIn(fragment, str(caught.exception))

    def test_committed_manifests_pass(self) -> None:
        self.validator.validate_conformance_manifests()

    def test_every_suite_declares_a_manifest(self) -> None:
        count = len(list((self.root / "conformance").glob("**/manifest.json")))
        directories = [
            child
            for child in (self.root / "conformance").iterdir()
            if child.is_dir() and child.name not in {"p1140e", "p1140f"}
        ]
        self.assertEqual(count, len(directories))

    def test_missing_manifest_fails(self) -> None:
        self.manifest_path("telemetry").unlink()
        self.assert_fails("conformance suite declares no manifest: telemetry")

    def test_missing_fixture_fails(self) -> None:
        (self.root / "conformance" / "telemetry" / "canaries.json").unlink()
        self.assert_fails("names a missing fixture")

    def test_unnamed_fixture_fails(self) -> None:
        (self.root / "conformance" / "telemetry" / "stray-vectors.json").write_text(
            "{}\n", encoding="utf-8"
        )
        self.assert_fails("holds files no case, authority or tooling entry names")

    def test_stale_digest_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["cases"][0]["fixtures"][0]["sha256"] = "0" * 64
        self.write("telemetry", manifest)
        self.assert_fails("records a stale digest")

    def test_edited_fixture_without_manifest_change_fails(self) -> None:
        target = self.root / "conformance" / "telemetry" / "canaries.json"
        body = json.loads(target.read_text(encoding="utf-8"))
        body["canaries"].append("VM-CANARY-ADDED-WITHOUT-AN-EXPECTATION")
        target.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        self.assert_fails("records a stale digest")

    def test_unresolved_authority_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["authorities"].append("docs/operations/NO_SUCH_DOCUMENT.md")
        self.write("telemetry", manifest)
        self.assert_fails("names a path that does not resolve")

    def test_unresolved_authority_clause_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["cases"][0]["authority_ref"] = (
            "docs/operations/OBSERVABILITY_PRIVACY.md#no-such-section"
        )
        self.write("telemetry", manifest)
        self.assert_fails("names a heading that does not exist")

    def test_unresolved_schema_pointer_fails(self) -> None:
        manifest = self.read("models")
        manifest["cases"][0]["authority_ref"] = (
            "conformance/models/t20-model-registry-v1.schema.json#/properties/no_such_member"
        )
        self.write("models", manifest)
        self.assert_fails("names an unresolved pointer")

    def test_wrong_case_prefix_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["cases"][0]["case_id"] = "XX-001"
        self.write("telemetry", manifest)
        self.assert_fails("does not carry the suite prefix")

    def test_reused_case_id_fails(self) -> None:
        """An identifier is permanent, so reuse has to fail even when the case that
        reuses it looks nothing like the original."""
        manifest = self.read("telemetry")
        clone = dict(manifest["cases"][0])
        clone["title"] = "A different case wearing an identifier that is already spent"
        manifest["cases"].append(clone)
        self.write("telemetry", manifest)
        self.assert_fails("conformance case IDs")

    def test_unknown_reason_code_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["cases"][0]["expect_reason_code"] = "NO_SUCH_REASON_CODE"
        self.write("telemetry", manifest)
        self.assert_fails("names a reason code that does not resolve")

    def test_loopback_reason_code_in_an_api_suite_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["cases"][0]["expect_reason_code"] = "LOOPBACK_HOST_NOT_ALLOWED"
        self.write("telemetry", manifest)
        self.assert_fails("names a reason code that does not resolve")

    def test_sandbox_resolves_its_loopback_reason_authority(self) -> None:
        manifest = self.read("sandbox")
        self.assertEqual(
            manifest["reason_authority"], "packages/schemas/origin-policy-v1.json"
        )
        policy = json.loads(
            (self.root / "packages" / "schemas" / "origin-policy-v1.json").read_text(
                encoding="utf-8"
            )
        )
        codes = {item["code"] for item in policy["loopback_refusal_codes"]}
        self.assertIn("LOOPBACK_HOST_NOT_ALLOWED", codes)

    def test_missing_negative_case_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["cases"][0]["negative"] = False
        self.write("telemetry", manifest)
        self.assert_fails("declares no negative case and no negative_case_gap")

    def test_stale_negative_case_gap_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["negative_case_gap"] = {
            "work_unit": "OS-009",
            "reason": "an excuse that outlived its hole",
        }
        self.write("telemetry", manifest)
        self.assert_fails("declares a negative_case_gap it no longer has")

    def test_unknown_eval_suite_fails(self) -> None:
        manifest = self.read("telemetry")
        manifest["eval_suite_ids"].append("no-such-eval-suite")
        self.write("telemetry", manifest)
        self.assert_fails("names eval suites the registry does not declare")

    def test_suite_id_must_match_the_directory(self) -> None:
        manifest = self.read("telemetry")
        manifest["suite_id"] = "telemetry-enforcement"
        self.write("telemetry", manifest)
        self.assert_fails("is not the directory name telemetry")

    def test_empty_suite_declaring_a_case_fails(self) -> None:
        manifest = self.read("sandbox")
        donor = self.read("telemetry")["cases"][0]
        donor["case_id"] = "SB-001"
        manifest["cases"] = [donor]
        self.write("sandbox", manifest)
        self.assert_fails("declares cases while recording an empty fixture state")

    def test_empty_suite_declaring_a_runner_fails(self) -> None:
        manifest = self.read("release")
        manifest["runner"]["state"] = "present"
        manifest["runner"]["command"] = ["true"]
        self.write("release", manifest)
        self.assert_fails("declares a runner for a suite with no fixture")

    def test_fixture_outside_the_suite_fails(self) -> None:
        manifest = self.read("telemetry")
        foreign = "conformance/privacy/p1140b-boundary-canaries-v1.json"
        digest = self.validator.hashlib.sha256(
            (self.root / foreign).read_bytes()
        ).hexdigest()
        manifest["cases"][0]["fixtures"].append({"path": foreign, "sha256": digest})
        self.write("telemetry", manifest)
        self.assert_fails("names a fixture outside its suite")


if __name__ == "__main__":
    unittest.main()
