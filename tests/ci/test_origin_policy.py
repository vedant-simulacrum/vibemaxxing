"""Tests for the D-230 and D-231 origin and loopback stage.

These prove the stage fails when the policy record and the OpenAPI document disagree,
when the development origin becomes a configuration flag rather than a compile-time
absence, and when a loopback listener drops a control or trusts its own input. They are
not evidence that any server validates a `Host` header, because none exists.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
SCHEMAS = ROOT / "packages" / "schemas"


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


COPIED = (
    "origin-policy-v1.json",
    "origin-policy-v1.schema.json",
    "openapi-v1.yaml",
    "reason-codes-v1.json",
)


class OriginPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.directory = Path(tempfile.mkdtemp(prefix="origin-policy-"))
        self.addCleanup(shutil.rmtree, self.directory, True)
        for name in COPIED:
            shutil.copyfile(SCHEMAS / name, self.directory / name)
        self.validator.SCHEMAS = self.directory

    def read_policy(self) -> dict:
        return json.loads(
            (self.directory / "origin-policy-v1.json").read_text(encoding="utf-8")
        )

    def write_policy(self, policy: dict) -> None:
        (self.directory / "origin-policy-v1.json").write_text(
            json.dumps(policy, indent=2), encoding="utf-8"
        )

    def read_openapi(self) -> dict:
        return yaml.safe_load(
            (self.directory / "openapi-v1.yaml").read_text(encoding="utf-8")
        )

    def write_openapi(self, spec: dict) -> None:
        (self.directory / "openapi-v1.yaml").write_text(
            yaml.dump(spec, sort_keys=False), encoding="utf-8"
        )

    def write_policy_and_block(self, policy: dict) -> None:
        """Mutate the record and re-project it into the OpenAPI block.

        The projection check fires first by design, so a test that wants to reach a
        later check has to keep the two in agreement. That is the point of the
        projection: a record cannot move without the document moving with it.
        """
        self.write_policy(policy)
        spec = self.read_openapi()
        for key in (
            "wildcard_origin",
            "origin_reflection",
            "subdomain_wildcard",
            "allowed_origins",
            "preflight",
            "state_changing_checks",
            "bearer_exemption",
        ):
            spec["x-origin-policy"][key] = policy["public_api"][key]
        self.write_openapi(spec)

    def assert_fails(self, fragment: str) -> None:
        with self.assertRaises(Exception) as caught:
            self.validator.validate_origin_policy()
        self.assertIn(fragment, str(caught.exception))

    def test_committed_contract_passes(self) -> None:
        self.validator.validate_origin_policy()

    def test_openapi_block_drift_fails(self) -> None:
        spec = self.read_openapi()
        spec["x-origin-policy"]["preflight"]["max_age_seconds"] = 86400
        self.write_openapi(spec)
        self.assert_fails("diverges from the policy record at preflight")

    def test_missing_origin_block_fails(self) -> None:
        spec = self.read_openapi()
        del spec["x-origin-policy"]
        self.write_openapi(spec)
        self.assert_fails("declares no x-origin-policy block")

    def test_configured_off_development_origin_fails(self) -> None:
        policy = self.read_policy()
        for origin in policy["public_api"]["allowed_origins"]:
            if origin["environments"] == ["local"]:
                origin["production_build"] = "included"
        self.write_policy_and_block(policy)
        self.assert_fails("compiled out of the production build")

    def test_wildcard_origin_fails_at_the_schema(self) -> None:
        policy = self.read_policy()
        policy["public_api"]["allowed_origins"][0]["origin"] = "https://*.example.dev"
        self.write_policy_and_block(policy)
        self.assert_fails("does not match")

    def test_subdomain_wildcard_origin_fails(self) -> None:
        policy = self.read_policy()
        policy["public_api"]["allowed_origins"][0]["origin"] = (
            "https://*.vibemaxxing.dev"
        )
        self.write_policy_and_block(policy)
        self.assert_fails("does not match")

    def test_origin_parameter_enum_drift_fails(self) -> None:
        spec = self.read_openapi()
        spec["components"]["parameters"]["Origin"]["schema"]["enum"].append(
            "https://partner.example"
        )
        self.write_openapi(spec)
        self.assert_fails("differs from the allowlist")

    def test_operation_without_origin_parameter_fails(self) -> None:
        spec = self.read_openapi()
        parameters = spec["paths"]["/sessions/revoke-all"]["post"]["parameters"]
        spec["paths"]["/sessions/revoke-all"]["post"]["parameters"] = [
            entry
            for entry in parameters
            if entry.get("$ref") != "#/components/parameters/Origin"
        ]
        self.write_openapi(spec)
        self.assert_fails("declares no Origin parameter: revokeAllSessions")

    def test_origin_parameter_without_csrf_scheme_fails(self) -> None:
        spec = self.read_openapi()
        operation = spec["paths"]["/leaderboards/{scope}/{period}"]["get"]
        operation.setdefault("parameters", []).append(
            {"$ref": "#/components/parameters/Origin"}
        )
        self.write_openapi(spec)
        self.assert_fails("without the csrfToken scheme that binds it")

    def test_required_preflight_header_fails(self) -> None:
        spec = self.read_openapi()
        spec["components"]["responses"]["Preflight"]["headers"][
            "Access-Control-Allow-Origin"
        ]["required"] = True
        self.write_openapi(spec)
        self.assert_fails("declared required")

    def test_listener_dropping_a_control_fails(self) -> None:
        policy = self.read_policy()
        policy["loopback_listeners"][0]["controls"] = policy["loopback_listeners"][0][
            "controls"
        ][:7]
        self.write_policy(policy)
        self.assert_fails("is too short")

    def test_listener_dropping_a_control_by_substitution_fails(self) -> None:
        policy = self.read_policy()
        controls = policy["loopback_listeners"][0]["controls"]
        controls[7] = dict(controls[7], control_id="host-allowlist")
        self.write_policy(policy)
        self.assert_fails("does not bind every loopback control")

    def test_listener_emitting_cors_headers_fails(self) -> None:
        policy = self.read_policy()
        policy["loopback_listeners"][0]["cors_headers"] = "permissive"
        self.write_policy(policy)
        self.assert_fails("origin policy")

    def test_listener_trusting_input_fails(self) -> None:
        policy = self.read_policy()
        policy["loopback_listeners"][1]["input_trust"] = "trusted"
        self.write_policy(policy)
        self.assert_fails("origin policy")

    def test_unauthenticated_listener_without_residual_exposure_fails(self) -> None:
        policy = self.read_policy()
        for listener in policy["loopback_listeners"]:
            listener.pop("residual_exposure", None)
        self.write_policy(policy)
        self.assert_fails("records no residual exposure")

    def test_loopback_code_in_the_api_registry_fails(self) -> None:
        registry = json.loads(
            (self.directory / "reason-codes-v1.json").read_text(encoding="utf-8")
        )
        template = dict(registry["codes"][-1])
        template["code"] = "LOOPBACK_HOST_NOT_ALLOWED"
        registry["codes"].append(template)
        (self.directory / "reason-codes-v1.json").write_text(
            json.dumps(registry, indent=2), encoding="utf-8"
        )
        self.assert_fails("added to the API reason registry")

    def test_unknown_state_changing_reason_code_fails(self) -> None:
        policy = self.read_policy()
        policy["public_api"]["state_changing_checks"][0]["on_failure"][
            "reason_code"
        ] = "NO_SUCH_CODE"
        self.write_policy_and_block(policy)
        self.assert_fails("names an unknown reason code")


if __name__ == "__main__":
    unittest.main()
