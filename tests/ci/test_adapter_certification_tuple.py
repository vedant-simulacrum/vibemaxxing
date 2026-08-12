"""Drift-injection tests for scripts/repository/validate_adapter_certification_tuple.py.

The validator exists because three artifacts had to agree about what a certified tuple is
and none of them read each other. `adapter-manifest.schema.json#certification` held one
`source_version`, one `platform_profile_id` and one `mode` above four manifest-level
arrays, so one certification authorized every combination those arrays multiplied into;
`compatibility-tuple-v1.schema.json` required a version range the manifest could not
express and six digests the manifest did not carry; and `source_certifications` stored a
validity interval and a revocation the manifest had no field for.

A validator for that class of defect is only worth having if it fails when one authority
moves and the others do not. Every test below moves exactly one and requires the exact
failure, because a test that merely requires *something* to raise passes for the wrong
reason as soon as an earlier check starts firing first.
"""

from __future__ import annotations

import contextlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_adapter_certification_tuple.py"

ARTIFACTS = (
    "MANIFEST",
    "TUPLE",
    "SQL",
    "PROFILES",
    "EXAMPLE",
    "POLICY",
    "COMPATIBILITY",
)


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "validate_adapter_certification_tuple", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class TupleBindingFixture:
    """A working copy of the seven artifacts, so a test mutates a file nothing else reads.

    A mixin rather than a base TestCase: the drift classes below group by which authority
    moves, and subclassing one of them to reuse its fixtures would re-run its assertions
    under a second name and report one check as two.
    """

    def setUp(self) -> None:
        self.validator = load_validator()
        self.root = Path(tempfile.mkdtemp(prefix="certification-tuple-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.paths: dict[str, Path] = {}
        for name in ARTIFACTS:
            source = getattr(self.validator, name)
            target = self.root / source.name
            shutil.copyfile(source, target)
            self.paths[name] = target

    def run_validator(self) -> int:
        with contextlib.ExitStack() as stack:
            for name, path in self.paths.items():
                stack.enter_context(patch.object(self.validator, name, path))
            return self.validator.main()
        raise AssertionError("unreachable")

    def rewrite(self, name: str, old: str, new: str) -> None:
        path = self.paths[name]
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"{name}: {old!r} is not present to rewrite")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def rewrite_table(self, table: str, old: str, new: str) -> None:
        """A rewrite scoped to one `create table` body.

        `planning-schema.sql` declares `accounting_profile_id text not null,` in several
        tables, so an unscoped first-occurrence replace silently edits whichever one
        comes first and the test then proves nothing about the table it named.
        """
        path = self.paths["SQL"]
        text = path.read_text(encoding="utf-8")
        opening = f"create table {table} (\n"
        start = text.index(opening) + len(opening)
        end = text.index("\n);", start)
        body = text[start:end]
        if old not in body:
            raise AssertionError(f"{table}: {old!r} is not present to rewrite")
        path.write_text(
            text[:start] + body.replace(old, new, 1) + text[end:], encoding="utf-8"
        )

    def edit_json(self, name: str, mutate: Callable[[Any], None]) -> None:
        path = self.paths[name]
        document = json.loads(path.read_text(encoding="utf-8"))
        mutate(document)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def certified_tuple(self, document: dict) -> dict:
        return document["$defs"]["certified_tuple"]["properties"]

    def assert_fails(self, fragment: str) -> None:
        with self.assertRaises(self.validator.Failure) as raised:
            self.run_validator()
        self.assertIn(fragment, str(raised.exception))

    def candidate_tuple(self, **overrides: Any) -> dict:
        """One enumerated tuple, drawn from what the committed example declares.

        `candidate` rather than `active`: ADAPTER_CERTIFICATION_POLICY.md states that no
        tuple in this repository has ever left the initial state, and a fixture is not
        the place that changes. No digest here is a certification of anything - the
        validator reads identity and containment from these fields and never a bundle.
        """
        entry = {
            "tuple_digest": "0" * 64,
            "source": {
                "source_product_id": "synthetic-agent",
                "version_min": "1.0.0",
                "version_max_exclusive": "2.0.0",
            },
            "observation_mode": "native-event",
            "platform_profile_id": "ubuntu-26.04-x86-64-headless",
            "accounting": {"accounting_profile_id": "cloud-separate-cache-v1"},
            "duplicate_domain": "synthetic-request",
            "max_public_profile": "private-analytics",
        }
        entry.update(overrides)
        return entry

    def enumerate_tuples(self, *entries: dict) -> None:
        def mutate(document: dict) -> None:
            document["certification"]["state"] = "candidate"
            document["certification"]["tuples"] = list(entries)

        self.edit_json("EXAMPLE", mutate)


class RepositoryHeadTests(TupleBindingFixture, unittest.TestCase):
    def test_the_repository_as_committed_passes(self) -> None:
        self.assertEqual(self.run_validator(), 0)


class ManifestDriftTests(TupleBindingFixture, unittest.TestCase):
    """The artifact SR-009 names first, and the one PF-071 opened without finishing."""

    def test_removing_a_tuple_dimension_from_the_manifest_fails(self) -> None:
        """The exact prior state: the tuple required six digests the manifest lacked."""

        def mutate(document: dict) -> None:
            privacy = self.certified_tuple(document)["privacy_binding"]
            del privacy["properties"]["strip_list_sha256"]
            privacy["required"] = [
                name for name in privacy["required"] if name != "strip_list_sha256"
            ]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails(
            "adapter-manifest.schema.json carries no "
            "certification.tuples[].privacy_binding.strip_list_sha256 for tuple "
            "dimension privacy_binding.strip_list_sha256"
        )

    def test_reverting_the_version_range_to_a_point_version_fails(self) -> None:
        """A point version cannot express a certified range. This is the prior state."""

        def mutate(document: dict) -> None:
            source = self.certified_tuple(document)["source"]
            source["properties"] = {
                "source_version": {"type": "string", "maxLength": 80}
            }
            source["required"] = ["source_version"]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails("the certified tuple still carries a single `source_version`")

    def test_dropping_only_the_exclusive_upper_bound_fails(self) -> None:
        """An open-ended range certifies software that does not exist yet."""

        def mutate(document: dict) -> None:
            source = self.certified_tuple(document)["source"]
            source["required"] = [
                name for name in source["required"] if name != "version_max_exclusive"
            ]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails("does not require `version_max_exclusive`")

    def test_reintroducing_a_single_valued_dimension_above_the_arrays_fails(
        self,
    ) -> None:
        """The cross product, exactly as it stood: one value against four arrays."""

        def mutate(document: dict) -> None:
            block = document["properties"]["certification"]
            block["properties"]["platform_profile_id"] = {
                "type": "string",
                "pattern": "^[a-z0-9]+(?:[.-][a-z0-9]+)*$",
            }

        self.edit_json("MANIFEST", mutate)

        self.assert_fails(
            "the certification block carries ['platform_profile_id'] as single values "
            "above the manifest-level arrays"
        )

    def test_removing_the_tuple_list_fails(self) -> None:
        def mutate(document: dict) -> None:
            del document["properties"]["certification"]["properties"]["tuples"]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails("the certification block declares no `tuples` array")

    def test_admitting_the_same_tuple_twice_fails(self) -> None:
        def mutate(document: dict) -> None:
            del document["properties"]["certification"]["properties"]["tuples"][
                "uniqueItems"
            ]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails("`certification.tuples` admits the same tuple twice")

    def test_dropping_the_validity_interval_fails(self) -> None:
        """SR-009: 'it carries no validity interval and no revocation'."""

        def mutate(document: dict) -> None:
            del self.certified_tuple(document)["validity"]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails(
            "adapter-manifest.schema.json carries no "
            "certification.tuples[].validity.valid_from for "
            "source_certifications.valid_from"
        )

    def test_making_the_revocation_optional_fails(self) -> None:
        def mutate(document: dict) -> None:
            entry = document["$defs"]["certified_tuple"]
            entry["required"] = [
                name for name in entry["required"] if name != "revocation"
            ]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails(
            "certification.tuples[].revocation.revoked_at is optional, so a manifest "
            "may omit it"
        )

    def test_a_second_spelling_of_the_mode_vocabulary_fails(self) -> None:
        def mutate(document: dict) -> None:
            mode = self.certified_tuple(document)["observation_mode"]
            mode["enum"] = [value for value in mode["enum"] if value != "acp"]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails(
            "tuple dimension observation_mode has a different shape in the two schemas"
        )

    def test_unpinning_the_private_analytics_ceiling_fails(self) -> None:
        """The DDL's load-bearing check, mirrored. Removing the mirror fails."""

        def mutate(document: dict) -> None:
            block = document["properties"]["certification"]
            block["allOf"] = [
                rule
                for rule in block["allOf"]
                if rule.get("if", {})
                .get("properties", {})
                .get("state", {})
                .get("not", {})
                .get("const")
                != "active"
            ]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails(
            "adapter-manifest.schema.json does not pin every tuple of a non-active "
            "certification to `private-analytics`"
        )

    def test_letting_an_uncertified_manifest_enumerate_tuples_fails(self) -> None:
        """An empty list under a named state is the cross product returning as absence."""

        def mutate(document: dict) -> None:
            block = document["properties"]["certification"]
            for rule in block["allOf"]:
                if (
                    rule.get("if", {})
                    .get("properties", {})
                    .get("state", {})
                    .get("const")
                    == "uncertified"
                ):
                    rule["then"]["properties"]["tuples"]["maxItems"] = 8

        self.edit_json("MANIFEST", mutate)

        self.assert_fails("the `uncertified` binding's `then` branch is")

    def test_dropping_the_active_equivalence_fails(self) -> None:
        def mutate(document: dict) -> None:
            block = document["properties"]["certification"]
            block["allOf"] = [
                rule
                for rule in block["allOf"]
                if rule.get("if", {})
                .get("properties", {})
                .get("state", {})
                .get("const")
                != "active"
            ]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails("the active-state rule is not stated as an equivalence")


class TupleAuthorityDriftTests(TupleBindingFixture, unittest.TestCase):
    """`compatibility-tuple-v1.schema.json` is the authority. It may not move alone."""

    def test_removing_a_dimension_from_the_tuple_authority_fails(self) -> None:
        def mutate(document: dict) -> None:
            accounting = document["$defs"]["accounting"]
            del accounting["properties"]["arithmetic_sha256"]
            accounting["required"] = [
                name for name in accounting["required"] if name != "arithmetic_sha256"
            ]

        self.edit_json("TUPLE", mutate)

        self.assert_fails("only-in-binding-table=['accounting.arithmetic_sha256']")

    def test_adding_a_dimension_to_the_tuple_authority_alone_fails(self) -> None:
        """The check is not satisfiable by addition either."""

        def mutate(document: dict) -> None:
            document["$defs"]["tuple"]["properties"]["transport_profile_id"] = {
                "type": "string"
            }

        self.edit_json("TUPLE", mutate)

        self.assert_fails("only-in-tuple-schema=['transport_profile_id']")

    def test_making_a_required_dimension_optional_in_the_manifest_fails(self) -> None:
        def mutate(document: dict) -> None:
            entry = document["$defs"]["certified_tuple"]
            entry["required"] = [
                name for name in entry["required"] if name != "observation_mode"
            ]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails(
            "certification.tuples[].observation_mode is optional in "
            "adapter-manifest.schema.json and required by "
            "compatibility-tuple-v1.schema.json"
        )

    def test_an_undeclared_strengthening_fails(self) -> None:
        """A silent strengthening reads exactly like a divergence."""

        def mutate(document: dict) -> None:
            source = self.certified_tuple(document)["source"]
            source["required"] = source["required"] + ["schema_url"]

        self.edit_json("MANIFEST", mutate)

        self.assert_fails(
            "the manifest requires dimensions the tuple authority leaves optional, and "
            "the declared list does not match: only-in-schema=['source.schema_url']"
        )


class CertificationRowDriftTests(TupleBindingFixture, unittest.TestCase):
    """`source_certifications` is the persistence owner, and its digest is load-bearing."""

    def test_the_ddl_losing_tuple_digest_fails(self) -> None:
        self.rewrite(
            "SQL",
            "  tuple_digest bytea not null unique check (octet_length(tuple_digest) = 32),\n",
            "",
        )

        self.assert_fails(
            "source_certifications has no column tuple_digest for tuple dimension "
            "tuple_digest"
        )

    def test_the_ddl_dropping_the_digest_uniqueness_fails(self) -> None:
        """Without it the row names a tuple it cannot identify."""
        self.rewrite(
            "SQL",
            "  tuple_digest bytea not null unique check",
            "  tuple_digest bytea not null check",
        )

        self.assert_fails(
            "source_certifications.tuple_digest is no longer a unique non-null column"
        )

    def test_the_ddl_losing_a_columned_dimension_fails(self) -> None:
        self.rewrite_table(
            "source_certifications", "  accounting_profile_id text not null,\n", ""
        )

        self.assert_fails(
            "source_certifications has no column accounting_profile_id for tuple "
            "dimension accounting.accounting_profile_id"
        )

    def test_a_column_with_no_recorded_reason_fails(self) -> None:
        self.rewrite_table(
            "source_certifications",
            "  evidence_profile_id text not null,",
            "  evidence_profile_id text not null,\n  attestation_hint text,",
        )

        self.assert_fails(
            "source_certifications does not hold exactly the tuple dimensions"
        )

    def test_a_reason_that_outlived_its_hole_fails(self) -> None:
        """A dimension recorded as bound by the digest, given a column of its own."""
        self.rewrite_table(
            "source_certifications",
            "  evidence_profile_id text not null,",
            "  evidence_profile_id text not null,\n  duplicate_domain text not null,",
        )

        self.assert_fails(
            "tuple dimension duplicate_domain is recorded as bound by tuple_digest "
            "alone, and source_certifications now carries a duplicate_domain column"
        )

    def test_the_ddl_dropping_the_private_analytics_check_fails(self) -> None:
        self.rewrite(
            "SQL",
            "  check (state = 'active' or effective_ceiling = 'private-analytics')\n",
            "  check (revision > 0)\n",
        )

        self.assert_fails(
            "source_certifications no longer refuses a non-active certification above "
            "private analytics"
        )

    def test_the_ddl_dropping_the_active_equivalence_fails(self) -> None:
        self.rewrite(
            "SQL",
            "  check ((state = 'active') = (valid_from is not null and revoked_at is "
            "null and superseded_by_source_certification_id is null)),\n",
            "",
        )

        self.assert_fails(
            "source_certifications no longer states the active equivalence the "
            "manifest's `live_tuple` shape is derived from"
        )

    def test_the_ceiling_vocabularies_falling_out_of_projection_fails(self) -> None:
        self.rewrite(
            "SQL",
            "effective_ceiling in ('hardened','standard','private-analytics')",
            "effective_ceiling in ('hardened','standard','imported','private-analytics')",
        )

        self.assert_fails(
            "source_certifications.effective_ceiling admits ['hardened', 'standard', "
            "'imported', 'private-analytics']"
        )


class RecordedReasonTests(TupleBindingFixture, unittest.TestCase):
    """An absence is satisfied by a reason, so a blank reason has to fail."""

    def test_blanking_a_dimension_absence_reason_fails(self) -> None:
        table = dict(self.validator.TUPLE_DIMENSIONS)
        table["duplicate_domain"] = self.validator.Dimension(
            manifest=table["duplicate_domain"].manifest,
            sql=None,
            sql_absence_reason="   ",
        )
        with patch.object(self.validator, "TUPLE_DIMENSIONS", table):
            self.assert_fails(
                "tuple dimension duplicate_domain is recorded as absent from "
                "source_certifications with no reason"
            )

    def test_blanking_a_manifest_absence_reason_fails(self) -> None:
        table = dict(self.validator.TUPLE_DIMENSIONS)
        table["artifact.release_set_version"] = self.validator.Dimension(
            manifest=None,
            sql=None,
            manifest_absence_reason="",
            sql_absence_reason=table["artifact.release_set_version"].sql_absence_reason,
        )
        with patch.object(self.validator, "TUPLE_DIMENSIONS", table):
            self.assert_fails(
                "tuple dimension artifact.release_set_version is recorded as absent "
                "from adapter-manifest.schema.json with no reason"
            )

    def test_blanking_a_server_only_column_reason_fails(self) -> None:
        columns = dict(self.validator.RECORD_ONLY_COLUMNS)
        columns["evidence_profile_id"] = ""
        with patch.object(self.validator, "RECORD_ONLY_COLUMNS", columns):
            self.assert_fails(
                "source_certifications.evidence_profile_id is excluded from the "
                "manifest with no reason"
            )

    def test_blanking_a_strengthening_reason_fails(self) -> None:
        with patch.object(
            self.validator, "MANIFEST_STRENGTHENED", {"duplicate_domain": " "}
        ):
            self.assert_fails(
                "tuple dimension duplicate_domain is strengthened in the manifest with "
                "no reason"
            )

    def test_excusing_a_required_dimension_fails(self) -> None:
        """A dimension the tuple authority requires may not be excused at all."""
        table = dict(self.validator.TUPLE_DIMENSIONS)
        table["source.version_min"] = self.validator.Dimension(
            manifest=None,
            sql=None,
            manifest_absence_reason="an adapter cannot know its own lower bound",
            sql_absence_reason=table["source.version_min"].sql_absence_reason,
        )
        with patch.object(self.validator, "TUPLE_DIMENSIONS", table):
            self.assert_fails(
                "tuple dimension source.version_min is required by "
                "compatibility-tuple-v1.schema.json and recorded as absent from the "
                "manifest"
            )


class CommittedExampleTests(TupleBindingFixture, unittest.TestCase):
    """Nothing in this repository is certified, and containment replaced the product."""

    def test_a_manifest_that_marks_itself_certified_fails(self) -> None:
        self.edit_json(
            "EXAMPLE",
            lambda document: document["certification"].__setitem__("state", "active"),
        )

        self.assert_fails(
            "the committed adapter manifest example declares certification state "
            "'active'"
        )

    def test_an_uncertified_manifest_carrying_a_suite_version_fails(self) -> None:
        """The prior example did exactly this: a suite version for a suite never run."""
        self.edit_json(
            "EXAMPLE",
            lambda document: document["certification"].__setitem__(
                "suite_version", "1.0.0"
            ),
        )

        self.assert_fails(
            "the committed example declares itself uncertified and carries a bundle "
            "digest, a suite version or a tuple"
        )

    def test_a_tuple_naming_a_mode_the_manifest_does_not_declare_fails(self) -> None:
        self.enumerate_tuples(self.candidate_tuple(observation_mode="otel"))

        self.assert_fails(
            "names observation_mode='otel', which `modes` does not declare"
        )

    def test_a_tuple_naming_an_unregistered_platform_profile_fails(self) -> None:
        """The prior example named `linux-x64-native`, which the registry has never had."""
        self.enumerate_tuples(
            self.candidate_tuple(platform_profile_id="linux-x64-native")
        )

        self.assert_fails(
            "names platform profile 'linux-x64-native', which "
            "platform-profile-registry-v1.json does not declare"
        )

    def test_a_tuple_naming_an_undeclared_accounting_profile_fails(self) -> None:
        self.enumerate_tuples(
            self.candidate_tuple(
                accounting={"accounting_profile_id": "cloud-inclusive-total-v1"}
            )
        )

        self.assert_fails(
            "names accounting.accounting_profile_id='cloud-inclusive-total-v1', which "
            "`accounting_profile_ids` does not declare"
        )

    def test_two_tuples_sharing_one_digest_fails(self) -> None:
        self.enumerate_tuples(
            self.candidate_tuple(),
            self.candidate_tuple(platform_profile_id="debian-13-x86-64-headless"),
        )

        self.assert_fails("repeats tuple digest")

    def test_a_declared_tuple_the_manifest_reaches_passes(self) -> None:
        """The containment rule admits what the arrays declare, and only that."""
        self.enumerate_tuples(self.candidate_tuple())

        self.assertEqual(self.run_validator(), 0)


class DerivationSourceTests(TupleBindingFixture, unittest.TestCase):
    """Every rule above is derived from a sentence. If the sentence goes, this is stale."""

    def test_the_policy_dropping_its_uncertified_statement_fails(self) -> None:
        self.rewrite(
            "POLICY",
            "Every tuple this repository can reach is `candidate`.",
            "Certification is under way.",
        )

        self.assert_fails("ADAPTER_CERTIFICATION_POLICY.md no longer states")

    def test_the_compatibility_document_dropping_the_atomicity_rule_fails(self) -> None:
        self.rewrite(
            "COMPATIBILITY",
            "A certification of one tuple says nothing about any other.",
            "Certifications generalise across tuples.",
        )

        self.assert_fails("UNIVERSAL_AGENT_COMPATIBILITY.md no longer states")


if __name__ == "__main__":
    unittest.main()
