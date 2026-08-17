"""A pin that nothing reads is a comment, and five manifests held exactly that.

`apps/web/package.json` carried five caret ranges — `typescript: ^5.9.0` resolves to
whatever 5.x published most recently — while `apps/api/go.mod` required `go 1.26.5`
against an installed `go1.26.4`, so the module could not build with the toolchain the
repository shipped to. Nothing reported either, because nothing read either.

Every case here moves exactly one thing and asserts the exact substring the validator
answers with. That is the discipline the planning suites already use: a case that
asserts only a non-zero exit passes when the validator fails for a reason the case
never intended, and stays passing after the check it was written for is deleted.

`ToolchainPinsMixin` is a mixin rather than a base `TestCase` on purpose. Subclassing
one re-runs every test in this file inside each child class, inflating the count
without testing anything new and hiding which case actually covers what.

The mixin redirects the validator's whole path set or fails loudly. A suite that
redirected four of five constants would inject its drift into a copy the validator
never opens and read the real repository instead — the case would pass, for the wrong
reason, and would keep passing after the check under test regressed.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]

GO_PIN = re.search(
    r"^go (\S+)$",
    (ROOT / "apps" / "api" / "go.mod").read_text(encoding="utf-8"),
    flags=re.M,
).group(1)
"""The go pin, read from the manifest that owns it.

These tests hardcoded `1.26.4` and broke the moment the pin was corrected back to
`1.26.5` -- a test pinning a value in order to exercise a rule about that value's
shape. The rule is what is under test; the number belongs to `apps/api/go.mod`.
"""

CARGO_PIN = re.search(
    r'channel\s*=\s*"([^"]+)"',
    (ROOT / "rust-toolchain.toml").read_text(encoding="utf-8"),
).group(1)
NODE_PIN = (ROOT / ".node-version").read_text(encoding="utf-8").strip()
PINNED_PROBES = {
    "installed_cargo": lambda: CARGO_PIN,
    "installed_go": lambda: GO_PIN,
    "installed_node": lambda: NODE_PIN,
}
"""The three pins, and probes that report them as installed.

A case about the manifests must not also assert which toolchain the runner ships.
This machine matched all three and CI did not -- its image carries a Go that is
installed, so not a skip, and unequal, so a defect -- which failed cases that were
about something else entirely.
"""

VALIDATOR = ROOT / "scripts" / "ci" / "check_toolchain_pins.py"

# The five manifests the unit names, relative to the repository root.
MANIFESTS = (
    "rust-toolchain.toml",
    ".node-version",
    "Cargo.toml",
    "apps/api/go.mod",
    "apps/web/package.json",
)


def load_validator():
    specification = importlib.util.spec_from_file_location(
        "check_toolchain_pins", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class ToolchainPinsMixin:
    """A temporary copy of the five manifests, and one place that redirects them."""

    def setUp(self) -> None:
        super().setUp()
        self.tree = Path(tempfile.mkdtemp(prefix="toolchain-pins-"))
        self.addCleanup(shutil.rmtree, self.tree, ignore_errors=True)
        for relative in MANIFESTS:
            source = ROOT / relative
            destination = self.tree / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    def redirections(self, module: Any) -> dict[str, Any]:
        mapping = {
            "ROOT": self.tree,
            "RUST_TOOLCHAIN": self.tree / "rust-toolchain.toml",
            "NODE_VERSION": self.tree / ".node-version",
            "CARGO_MANIFEST": self.tree / "Cargo.toml",
            "GO_MOD": self.tree / "apps" / "api" / "go.mod",
            "WEB_PACKAGE": self.tree / "apps" / "web" / "package.json",
        }
        # The validator declares which constants resolve artifacts. If it grows one
        # and this mapping does not, every case below silently starts reading the
        # real repository through it.
        self.assertEqual(
            set(module.REDIRECTED),
            set(mapping),
            "the validator's REDIRECTED set and this mixin's redirections have "
            "diverged, so some drift would be injected into a file nothing reads",
        )
        return mapping

    def run_check(
        self, argv: list[str] | None = None, **probes: Any
    ) -> tuple[int, str]:
        """Run the validator against the temporary tree and capture everything.

        Defaults to `--allow-uninstalled` so a drift case asserts the manifest
        defect it injected rather than whichever toolchain this machine lacks.
        """
        module = load_validator()
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.multiple(module, **self.redirections(module)):
            with contextlib.ExitStack() as stack:
                for name, value in probes.items():
                    stack.enter_context(patch.object(module, name, value))
                stack.enter_context(contextlib.redirect_stdout(stdout))
                stack.enter_context(contextlib.redirect_stderr(stderr))
                code = module.main(["--allow-uninstalled"] if argv is None else argv)
        return code, stdout.getvalue() + stderr.getvalue()

    def edit_json(self, relative: str, mutate: Callable[[dict], None]) -> None:
        path = self.tree / relative
        document = json.loads(path.read_text(encoding="utf-8"))
        mutate(document)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def edit_text(self, relative: str, old: str, new: str) -> None:
        path = self.tree / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, f"{relative} does not contain {old!r} to replace")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")


class CommittedTreeTest(ToolchainPinsMixin, unittest.TestCase):
    """The pinned tree passes, which is what makes every drift case meaningful."""

    def test_the_copied_committed_tree_passes(self) -> None:
        """The committed manifests pass, with the pins themselves reported as installed.

        Injecting the pins is what keeps this a test of the tree. Left to the real
        probes it asserted that whichever machine ran it happened to carry all three
        pinned releases, which is a fact about the machine.
        """
        code, output = self.run_check(**PINNED_PROBES)
        self.assertEqual(code, 0, output)
        self.assertIn("toolchain pins: pass", output)

    def test_the_summary_and_claim_scope_are_printed(self) -> None:
        _, output = self.run_check(**PINNED_PROBES)
        self.assertIn("pins read from 5 manifests", output)
        self.assertIn("claim_scope=declared-pins-and-installed-versions-only", output)

    def test_the_real_repository_is_well_pinned(self) -> None:
        """The tree's own manifests, checked without asserting anything about this machine.

        This ran `main([])` and required all three installed comparisons to pass, which
        made a repository test an assertion about whichever toolchain the runner shipped.
        It passed here and failed in CI, where the image carries a Go that is not the pin
        — installed, so not a skip, and unequal, so a defect. A unit test of the tree
        cannot depend on the machine under it. The installed comparison still runs in
        `make validate` and in the workflow, and its failure modes are covered by the
        injected cases above; `--declarations-only` reports all three as skips and counts
        them, so this can never be read as a run that compared.
        """
        module = load_validator()
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = module.main(["--declarations-only"])
        output = stdout.getvalue() + stderr.getvalue()
        self.assertEqual(code, 0, output)
        self.assertIn("0 of 3 installed comparisons ran, 3 skipped", output)
        self.assertIn("claim_scope=declared-pins-only", output)
        self.assertNotIn("equals the pin", output)

    def test_a_caret_in_a_dependency_fails(self) -> None:
        self.edit_json(
            "apps/web/package.json",
            lambda document: document["devDependencies"].__setitem__(
                "typescript", "^5.9.3"
            ),
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            "devDependencies `typescript` is a caret range, not an exact version",
            output,
        )

    def test_a_tilde_in_a_dependency_fails(self) -> None:
        self.edit_json(
            "apps/web/package.json",
            lambda document: document["dependencies"].__setitem__("next", "~16.3.0"),
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            "dependencies `next` is a tilde range, not an exact version", output
        )

    def test_a_partial_npm_version_fails_because_npm_widens_it(self) -> None:
        """`"24"` is not a pin; npm resolves it as `>=24.0.0 <25.0.0`."""
        self.edit_json(
            "apps/web/package.json",
            lambda document: document["devDependencies"].__setitem__(
                "@types/node", "24"
            ),
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn("which npm resolves as a range rather than one release", output)

    def test_a_bare_cargo_version_fails_because_cargo_reads_it_as_a_caret(
        self,
    ) -> None:
        """Cargo's trap, inverted from npm's: `"1.0.0"` and `"^1.0.0"` are one thing."""
        self.edit_text(
            "Cargo.toml",
            "[workspace.lints.rust]",
            '[workspace.dependencies]\nserde = "1.0.228"\n\n[workspace.lints.rust]',
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            "which Cargo reads as the caret range `^1.0.228`; an exact Cargo pin "
            "is written `=1.0.228`",
            output,
        )

    def test_an_exact_cargo_version_passes(self) -> None:
        """The counterpart, so the rule above is a rule and not a blanket refusal."""
        self.edit_text(
            "Cargo.toml",
            "[workspace.lints.rust]",
            '[workspace.dependencies]\nserde = "=1.0.228"\n\n[workspace.lints.rust]',
        )
        code, output = self.run_check(**PINNED_PROBES)
        self.assertEqual(code, 0, output)


class EngineDriftTest(ToolchainPinsMixin, unittest.TestCase):
    """`latest` is the specifier that makes a build unreproducible tomorrow."""

    def test_latest_in_an_engine_fails(self) -> None:
        self.edit_json(
            "apps/web/package.json",
            lambda document: document.__setitem__("engines", {"node": "latest"}),
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            "the `node` engine is the floating tag `latest`, not an exact version",
            output,
        )

    def test_an_engine_disagreeing_with_node_version_fails(self) -> None:
        """Both exact, both pins, and they name two different releases."""
        self.edit_json(
            "apps/web/package.json",
            lambda document: document.__setitem__("engines", {"node": "20.11.0"}),
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            ".node-version `22.23.1` and apps/web/package.json engines.node "
            "`20.11.0` disagree",
            output,
        )

    def test_latest_in_package_manager_fails(self) -> None:
        self.edit_json(
            "apps/web/package.json",
            lambda document: document.__setitem__("packageManager", "npm@latest"),
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            "packageManager `npm` is the floating tag `latest`, not an exact version",
            output,
        )


class GoModDriftTest(ToolchainPinsMixin, unittest.TestCase):
    """The `go` directive and the `require` versions are both pins."""

    def test_a_range_in_the_go_directive_fails(self) -> None:
        self.edit_text("apps/api/go.mod", f"go {GO_PIN}", f"go >={GO_PIN}")
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            "the go directive is a comparison range, not an exact version", output
        )

    def test_a_range_in_a_require_fails(self) -> None:
        self.edit_text(
            "apps/api/go.mod",
            f"go {GO_PIN}",
            f"go {GO_PIN}\n\nrequire (\n\tgithub.com/jackc/pgx/v5 >=v5.7.6\n)",
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            "require `github.com/jackc/pgx/v5` is a comparison range, not an exact "
            "version",
            output,
        )


class RustAgreementDriftTest(ToolchainPinsMixin, unittest.TestCase):
    """Two manifests, two Rust versions, and nothing compared them before."""

    def test_a_channel_disagreeing_with_rust_version_fails(self) -> None:
        self.edit_text(
            "rust-toolchain.toml", 'channel = "1.96.0"', 'channel = "1.97.0"'
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn(
            "rust-toolchain.toml channel `1.97.0` and Cargo.toml rust-version "
            "`1.96` disagree",
            output,
        )

    def test_a_floating_channel_fails(self) -> None:
        self.edit_text(
            "rust-toolchain.toml", 'channel = "1.96.0"', 'channel = "stable"'
        )
        code, output = self.run_check()
        self.assertNotEqual(code, 0)
        self.assertIn("the toolchain channel is", output)

    def test_a_patch_level_channel_still_satisfies_a_minor_msrv(self) -> None:
        """`rust-version = "1.96"` against `channel = "1.96.0"` is agreement.

        The conventional MSRV is written to minor precision, so a string equality
        here would fail on the correct, committed tree.
        """
        code, output = self.run_check(**PINNED_PROBES)
        self.assertEqual(code, 0, output)
        self.assertNotIn("disagree", output)


class UninstalledToolchainTest(ToolchainPinsMixin, unittest.TestCase):
    """An absent toolchain is an absence of evidence, never a pass."""

    def test_an_uninstalled_tool_is_a_defect_by_default(self) -> None:
        code, output = self.run_check(argv=[], installed_go=lambda: None)
        self.assertNotEqual(code, 0)
        self.assertIn(
            f"uncompared pin: go is not installed, so the pin `{GO_PIN}` from "
            "apps/api/go.mod was not compared",
            output,
        )

    def test_an_uninstalled_tool_is_reported_even_when_allowed(self) -> None:
        """The flag changes the exit code and never hides the skip."""
        code, output = self.run_check(
            argv=["--allow-uninstalled"], installed_go=lambda: None
        )
        self.assertEqual(code, 0, output)
        self.assertIn("SKIP go:", output)
        self.assertIn("2 of 3 installed comparisons ran, 1 skipped", output)

    def test_a_version_mismatch_is_reported_byte_for_byte(self) -> None:
        """The injected version is derived from the pin so it can never equal it.

        This asserted a mismatch against a hardcoded `1.26.5`, which stopped being a
        mismatch the moment the pin was corrected to that value: the test passed while
        proving the opposite of its name. The rule under test is that any difference is
        reported, so the case supplies a version that differs by construction.
        """
        other = GO_PIN + ".1"
        code, output = self.run_check(installed_go=lambda: other)
        self.assertNotEqual(code, 0)
        self.assertIn(
            f"installed go is `{other}`, byte-for-byte unequal to the `{GO_PIN}` "
            "pinned in apps/api/go.mod",
            output,
        )


if __name__ == "__main__":
    unittest.main()
