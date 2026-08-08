"""Exactly one local role may read transcript content, and it has no network.

`AGENTS.md` forbids transcript content crossing the device boundary. That holds only
if no single process can both read content and reach the network — otherwise the
boundary is a promise about what a process chooses to send rather than a property of
how the processes are arranged.

`PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md` tabulated six of the eight local roles. The two
it omitted were the interactive shell, the only role that takes arbitrary operator
input, and the privileged supervisor, the only component that runs elevated.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "packages" / "schemas" / "local-trust-domains-v1.json"
MATRIX = ROOT / "docs" / "architecture" / "PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md"

CONTENT = "transcript-content"


def profile() -> dict:
    return json.loads(PROFILE.read_text(encoding="utf-8"))


def roles() -> dict[str, dict]:
    return {role["role_id"]: role for role in profile()["roles"]}


class SeparationTests(unittest.TestCase):
    def test_exactly_one_role_may_read_transcript_content(self) -> None:
        readers = sorted(
            r for r, role in roles().items() if CONTENT in role["may_read"]
        )

        self.assertEqual(readers, ["vibeproof-collector"])

    def test_the_content_reader_has_no_network(self) -> None:
        """The separation, stated as the property rather than as a promise."""
        self.assertEqual(roles()["vibeproof-collector"]["network"], "none")

    def test_no_role_both_reads_content_and_reaches_the_network(self) -> None:
        for role_id, role in sorted(roles().items()):
            if CONTENT in role["may_read"]:
                self.assertEqual(role["network"], "none", role_id)

    def test_the_networked_role_cannot_read_content_or_events(self) -> None:
        """vibeproof-sync is the only egress-allowlisted role."""
        sync = roles()["vibeproof-sync"]

        self.assertEqual(sync["network"], "egress-allowlist")
        self.assertNotIn(CONTENT, sync["may_read"])
        self.assertNotIn("normalized-events", sync["may_read"])

    def test_network_is_declared_and_not_inferred(self) -> None:
        """The first version of the check read this out of prose.

        `read allowlisted adapter sources` matched on the word allowlist — a source
        allowlist read as a network one — and the committed state failed. A capability
        the privacy boundary depends on is not something to substring-match.
        """
        for role_id, role in sorted(roles().items()):
            self.assertIn("network", role, role_id)


class PrivilegedRoleTests(unittest.TestCase):
    def test_both_privileged_roles_are_blind_to_every_product_data_class(self) -> None:
        for role_id in ("updater-helper", "privileged-supervisor"):
            role = roles()[role_id]
            self.assertEqual(role["privilege"], "privileged", role_id)
            for data_class in (
                CONTENT,
                "normalized-events",
                "safe-claim",
                "device-key",
            ):
                self.assertNotIn(data_class, role["may_read"], role_id)
                self.assertNotIn(data_class, role["may_write"], role_id)

    def test_the_supervisor_has_no_network(self) -> None:
        self.assertEqual(roles()["privileged-supervisor"]["network"], "none")

    def test_no_role_may_read_the_device_key(self) -> None:
        """Signing is requested through the daemon; the key is never handed out."""
        for role_id, role in sorted(roles().items()):
            self.assertNotIn("device-key", role["may_read"], role_id)


class CompletenessTests(unittest.TestCase):
    def test_all_eight_roles_are_declared(self) -> None:
        self.assertEqual(len(roles()), 8)

    def test_every_role_appears_in_the_privilege_matrix(self) -> None:
        """The matrix omitted the shell and the supervisor before PF-011."""
        matrix = MATRIX.read_text(encoding="utf-8")
        rows = "\n".join(
            line for line in matrix.splitlines() if line.lstrip().startswith("|")
        )
        for role_id, role in sorted(roles().items()):
            needle = role["executable"] if role_id != "updater-helper" else "updater"
            self.assertIn(
                needle.replace("vibemaxxing-supervisor", "supervisor"),
                rows.replace("`", ""),
                role_id,
            )

    def test_every_role_names_a_peer_identity_for_all_three_platforms(self) -> None:
        for role_id, role in sorted(roles().items()):
            for platform in ("macos", "windows", "linux"):
                self.assertIn(platform, role["os_peer_identity"], role_id)
                self.assertTrue(role["os_peer_identity"][platform].strip(), role_id)

    def test_every_data_class_used_is_declared(self) -> None:
        declared = set(profile()["data_classes"])
        for role_id, role in sorted(roles().items()):
            for data_class in role["may_read"] + role["may_write"]:
                self.assertIn(data_class, declared, role_id)

    def test_every_role_declares_at_least_one_prohibition(self) -> None:
        """A role with no `forbidden` list states no boundary at all."""
        for role_id, role in sorted(roles().items()):
            self.assertTrue(role["forbidden"], role_id)


if __name__ == "__main__":
    unittest.main()
