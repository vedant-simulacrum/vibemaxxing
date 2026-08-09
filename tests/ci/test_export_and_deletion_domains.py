"""The export package and the hosted deletion plan must answer for every domain.

PF-028 and PF-029, SR-013. "Covers every domain named in `docs/privacy/DATA_MAP.md`"
was the acceptance of two work units, and nothing in the repository could evaluate it:
an export manifest listed files whose logical names are whatever a producer types, and
`deletion_effects.subsystem` was `text not null` with no CHECK at all. Two owners of one
idea with no shared vocabulary cannot disagree, which is worse than disagreeing.

These cases mutate the artifacts and assert the validator notices. They prove the
comparison works. They do not prove that any export has been produced, that any domain
has been erased, or that any restore drill has run. None of those has happened.

The lifecycle-document case is the one worth reading twice. The original acceptance was
`grep -in 'forensic' docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md` returning no claim
of erasure, which the file satisfied by never mentioning the subject — an absence
satisfied by emptiness, passing on a document that made no statement about the claim
ceiling at all. `test_an_empty_lifecycle_document_fails` is the case the old form could
not have.
"""

from __future__ import annotations

import json
import unittest

from tests.ci.planning_fixtures import PlanningValidatorMixin

DATA_MAP = "docs/privacy/DATA_MAP.md"
LIFECYCLE = "docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md"
DISPOSITION = "packages/schemas/data-disposition-v1.json"
MANIFEST = "packages/schemas/export-manifest-v1.schema.json"
SQL = "packages/schemas/planning-schema.sql"
OPENAPI = "packages/schemas/openapi-v1.yaml"
REGISTRY = "packages/schemas/state-machine-registry-v1.json"


class ExportAndDeletionDomainTests(PlanningValidatorMixin, unittest.TestCase):
    COPIED = (
        "packages/schemas",
        "conformance/planning",
        "docs/architecture",
        "docs/privacy",
        "docs/operations",
    )

    def domains(self):
        return self.validator.validate_export_and_deletion_domains

    def lifecycles(self):
        return self.validator.validate_export_and_deletion_lifecycles

    # -- head state ---------------------------------------------------------

    def test_repository_head_passes(self) -> None:
        self.assert_passes(self.domains())
        self.assert_passes(self.lifecycles())

    def test_every_declared_domain_is_claimed_by_a_table(self) -> None:
        """A key with nothing behind it makes every coverage check below vacuous."""
        documented = self.validator._data_map_domain_table()
        registry = self.read(DISPOSITION)
        claimed = {
            entry["data_domain"]
            for entry in registry["entries"]
            if "data_domain" in entry
        }
        self.assertEqual(set(documented), claimed)
        self.assertEqual(len(documented), 7)

    # -- the Article 30 record owns the vocabulary --------------------------

    def test_a_domain_dropped_from_the_record_fails(self) -> None:
        self.edit_text(
            DATA_MAP,
            "| `requests-exports-deletion` | Requests, exports and deletion |",
            "| `requests-exports-deletion-renamed` | Requests, exports and deletion |",
        )
        self.assert_fails(self.domains(), "only-in-record")

    def test_a_domain_table_naming_a_section_that_does_not_exist_fails(self) -> None:
        self.edit_text(
            DATA_MAP,
            "| `authentication-session` | Authentication and session |",
            "| `authentication-session` | Authentication and sessions |",
        )
        self.assert_fails(self.domains(), "gives it no key")

    def test_a_domain_whose_section_names_no_covered_table_fails(self) -> None:
        """A key carried by a heading and nothing else."""
        text = self.path(DATA_MAP).read_text(encoding="utf-8")
        head, marker, tail = text.partition("### Authentication and session\n")
        body, gap, rest = tail.partition("\n### ")
        self.path(DATA_MAP).write_text(
            head + marker + "\nNo rows.\n" + gap + rest, encoding="utf-8"
        )
        self.assert_fails(self.domains(), "carried by a heading and nothing else")

    def test_a_table_filed_under_one_section_and_assigned_another_fails(self) -> None:
        """The assignment is derived from the record, not invented beside it."""
        registry = self.read(DISPOSITION)
        for entry in registry["entries"]:
            if entry["table"] == "presence_leases":
                entry["data_domain"] = "account-identity"
        self.write(DISPOSITION, registry)
        self.assert_fails(self.domains(), "contradicts the record")

    def test_an_emptied_domain_table_fails(self) -> None:
        text = self.path(DATA_MAP).read_text(encoding="utf-8")
        head, _, tail = text.partition("| Domain key | Section |")
        self.path(DATA_MAP).write_text(
            head + tail.split("\n\n", 1)[1], encoding="utf-8"
        )
        self.assert_fails(self.domains(), "has no rows")

    def test_a_personal_row_without_a_domain_fails(self) -> None:
        registry = self.read(DISPOSITION)
        for entry in registry["entries"]:
            if entry["table"] == "claims":
                entry.pop("data_domain")
        self.write(DISPOSITION, registry)
        self.assert_fails(self.validator.validate_data_disposition, "data_domain")

    def test_a_personal_row_an_erasure_never_reaches_fails(self) -> None:
        registry = self.read(DISPOSITION)
        for entry in registry["entries"]:
            if entry["table"] == "claims":
                entry["erasure_action"] = "not-applicable"
        self.write(DISPOSITION, registry)
        self.assert_fails(self.domains(), "an erasure never reaches them")

    # -- every owner carries the same seven keys ----------------------------

    def test_a_manifest_that_admits_fewer_domains_fails(self) -> None:
        manifest = self.read(MANIFEST)
        manifest["properties"]["domains"]["minItems"] = 6
        self.write(MANIFEST, manifest)
        self.assert_fails(self.domains(), "is silent about one")

    def test_a_narrowed_sql_domain_vocabulary_fails(self) -> None:
        self.edit_text(
            SQL,
            "data_domain text not null check (data_domain in ('account-identity',"
            "'authentication-session','device-collection','usage-claims-scores',"
            "'social-presence-notifications','integrity-moderation-appeals',"
            "'requests-exports-deletion')),\n  media_type",
            "data_domain text not null check (data_domain in ('account-identity',"
            "'authentication-session','device-collection','usage-claims-scores',"
            "'social-presence-notifications','integrity-moderation-appeals')),\n"
            "  media_type",
        )
        self.assert_fails(self.domains(), "export_artifacts.data_domain differs")

    def test_an_optional_domain_projection_fails(self) -> None:
        """A client that may omit the list renders one outcome for seven answers."""
        text = self.path(OPENAPI).read_text(encoding="utf-8")
        self.path(OPENAPI).write_text(
            text.replace(
                "        - blocked_by_legal_hold\n        - domain_effects\n", "", 1
            ),
            encoding="utf-8",
        )
        self.assert_fails(self.domains(), "renders one aggregate outcome")

    def test_a_deletion_effect_state_meaning_we_did_not_look_fails(self) -> None:
        self.edit_text(
            SQL,
            "state text not null check (state in ('pending','executing','complete',"
            "'failed')),\n  erasure_action",
            "state text not null check (state in ('pending','executing','complete',"
            "'failed','not-applicable')),\n  erasure_action",
        )
        self.assert_fails(self.domains(), "declining to answer")

    def test_an_effect_action_outside_the_registry_vocabulary_fails(self) -> None:
        self.edit_text(
            SQL,
            "erasure_action text not null check (erasure_action in ('delete',"
            "'key-destroy-retain','retain-pseudonymous','retain-unlinked')),",
            "erasure_action text not null check (erasure_action in ('delete',"
            "'key-destroy-retain','retain-pseudonymous','retain-unlinked','anonymised')),",
        )
        self.assert_fails(self.domains(), "deletion_effects.erasure_action differs")

    # -- the manifest fixtures ----------------------------------------------

    def test_a_manifest_answering_for_one_domain_twice_fails(self) -> None:
        """The schema cannot see this: two entries naming one domain are two objects."""
        path = self.path("packages/schemas/examples/export-manifest.valid.json")
        record = json.loads(path.read_text(encoding="utf-8"))
        record["domains"][1]["data_domain"] = record["domains"][0]["data_domain"]
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        self.assert_fails(self.domains(), "answers twice for")

    def test_removing_the_duplicate_domain_negative_fails(self) -> None:
        self.path(
            "packages/schemas/examples/export-manifest.invalid-domain-answered-twice.json"
        ).unlink()
        self.assert_fails(self.domains(), "no fixture exercises")

    def test_a_negative_that_stopped_being_one_fails(self) -> None:
        path = self.path(
            "packages/schemas/examples/export-manifest.invalid-domain-answered-twice.json"
        )
        record = json.loads(
            self.path("packages/schemas/examples/export-manifest.valid.json").read_text(
                encoding="utf-8"
            )
        )
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        self.assert_fails(self.domains(), "has stopped being one")

    def test_a_manifest_schema_carrying_a_key_fails(self) -> None:
        self.edit_text(
            MANIFEST,
            '"key_reference": {',
            '"key_material": { "type": "string" },\n        "key_reference": {',
        )
        self.assert_fails(self.domains(), "makes the encryption a label")

    # -- the operations document --------------------------------------------

    def test_an_empty_lifecycle_document_fails(self) -> None:
        """The case the original acceptance could not have.

        `grep -in 'forensic'` returning nothing was the criterion, and an empty file
        satisfies it perfectly while stating nothing about what the operation claims.
        """
        self.path(LIFECYCLE).write_text("", encoding="utf-8")
        self.assert_fails(self.domains(), "states no deletion claim ceiling")

    def test_removing_the_claim_ceiling_fails(self) -> None:
        self.edit_text(
            LIFECYCLE,
            "Deletion here is logical, not forensic.",
            "Deletion is thorough.",
        )
        self.assert_fails(self.domains(), "states no deletion claim ceiling")

    def test_a_claim_above_the_ceiling_fails(self) -> None:
        self.edit_text(
            LIFECYCLE,
            "A backup is not valid until restored and verified.",
            "A backup is not valid until restored and verified. Deleted rows are "
            "unrecoverable.",
        )
        self.assert_fails(self.domains(), "claims more than the product observes")

    def test_the_ceiling_section_may_deny_the_claim_by_name(self) -> None:
        """Banning the word rather than the claim would forbid the denial."""
        self.assertIn(
            "forensic", self.path(LIFECYCLE).read_text(encoding="utf-8").lower()
        )
        self.assert_passes(self.domains())


class ExportAndDeletionLifecycleTests(PlanningValidatorMixin, unittest.TestCase):
    COPIED = (
        "packages/schemas",
        "conformance/planning",
        "docs/architecture",
        "docs/privacy",
        "docs/operations",
    )

    def lifecycles(self):
        return self.validator.validate_export_and_deletion_lifecycles

    def test_an_export_without_a_coherent_snapshot_fails(self) -> None:
        self.edit_text(
            SQL,
            "  check (snapshot_cutoff_at is null or snapshot_cutoff_at >= requested_at),\n",
            "",
        )
        self.assert_fails(self.lifecycles(), "exports lacks its required constraint")

    def test_an_eternal_download_grant_fails(self) -> None:
        self.edit_text(
            SQL,
            "  expires_at timestamptz not null,\n  revoked_at timestamptz,",
            "  expires_at timestamptz,\n  revoked_at timestamptz,",
        )
        self.assert_fails(
            self.lifecycles(), "export_download_grants lacks its required constraint"
        )

    def test_a_cancellation_after_the_window_fails(self) -> None:
        self.edit_text(
            SQL,
            "  check (cancelled_at is null or cancelled_at < effective_after),\n",
            "",
        )
        self.assert_fails(
            self.lifecycles(), "deletion_jobs lacks its required constraint"
        )

    def test_a_legal_hold_that_stops_nothing_fails(self) -> None:
        self.edit_text(
            SQL,
            "or state in ('requested','recent-auth-verified','cooling-off','cancelled','failed')",
            "or state in ('requested','recent-auth-verified','cooling-off','processing','cancelled','failed')",
        )
        self.assert_fails(self.lifecycles(), "lets a held job reach")

    def test_a_hold_clause_naming_an_unknown_state_fails(self) -> None:
        self.edit_text(
            SQL,
            "or state in ('requested','recent-auth-verified','cooling-off','cancelled','failed')",
            "or state in ('requested','recent-auth-verified','cooling-off','cancelled','failed','held')",
        )
        self.assert_fails(self.lifecycles(), "does not admit")

    def test_a_worker_cancelling_an_erasure_fails(self) -> None:
        registry = self.read(REGISTRY)
        for machine in registry["machines"]:
            if machine["machine_id"] == "server-deletion":
                for transition in machine["transitions"]:
                    if transition["to"] == "cancelled":
                        transition["actor"] = "worker"
        self.write(REGISTRY, registry)
        self.assert_fails(self.lifecycles(), "the participant's own recently")

    def test_a_cancellation_from_outside_the_window_fails(self) -> None:
        registry = self.read(REGISTRY)
        for machine in registry["machines"]:
            if machine["machine_id"] == "server-deletion":
                for transition in machine["transitions"]:
                    if transition["to"] == "cancelled":
                        transition["from"] = ["cooling-off", "processing"]
        self.write(REGISTRY, registry)
        self.assert_fails(
            self.lifecycles(), "only the cooling-off window is reversible"
        )

    def test_a_machine_with_no_cancellation_fails(self) -> None:
        registry = self.read(REGISTRY)
        for machine in registry["machines"]:
            if machine["machine_id"] == "server-deletion":
                machine["transitions"] = [
                    transition
                    for transition in machine["transitions"]
                    if transition["to"] != "cancelled"
                ]
                machine["states"] = [
                    state for state in machine["states"] if state != "cancelled"
                ]
        self.write(REGISTRY, registry)
        self.assert_fails(self.lifecycles(), "reaches no cancelled state")

    def test_a_fourth_deletion_vocabulary_in_the_manifest_fails(self) -> None:
        manifest = self.read(MANIFEST)
        manifest["properties"]["deletion_state_at_generation"]["enum"] = [
            "none",
            "cooling_off",
            "executing",
            "completed",
        ]
        self.write(MANIFEST, manifest)
        self.assert_fails(self.lifecycles(), "only-in-manifest")

    def test_a_manifest_publishing_an_internal_state_fails(self) -> None:
        """The package may not say what the API declines to."""
        manifest = self.read(MANIFEST)
        manifest["properties"]["deletion_state_at_generation"]["enum"].append(
            "rebuilding-projections"
        )
        self.write(MANIFEST, manifest)
        self.assert_fails(self.lifecycles(), "only-in-manifest")

    def test_an_effect_completing_without_a_count_fails(self) -> None:
        self.edit_text(
            SQL,
            "  check (state <> 'complete' or affected_row_count is not null)\n",
            "\n",
        )
        self.assert_fails(
            self.lifecycles(), "deletion_effects lacks its required constraint"
        )


if __name__ == "__main__":
    unittest.main()
