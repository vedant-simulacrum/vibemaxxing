#!/usr/bin/env python3
"""Read every toolchain pin from the manifest that owns it, then check it twice.

Five manifests each pin part of the toolchain, and before this nothing read any of
them. `rust-toolchain.toml` names the Rust channel, `Cargo.toml` names the minimum
Rust the workspace compiles under, `apps/api/go.mod` names the Go language version,
`.node-version` names the Node runtime, and `apps/web/package.json` names the Node
engine and every npm dependency.

**Nothing here is restated.** An earlier shape of this check would have carried a
constant — `EXPECTED_RUST = "1.96.0"` — and compared the manifest against it. That
check passes whenever the two copies agree, which is exactly when it is useless: it
proves an edit touched both places, never that either place is right. Every version
this script knows is read out of a manifest at run time. There is no second copy to
agree with.

Three independent questions get asked, and they fail for different reasons.

**Is each specifier exact?** A pin that names a range is not a pin. The test is a
whitelist rather than a blocklist of `^` and `~`: a specifier is exact when it is a
recognised literal version and inexact otherwise, so a range syntax nobody here
anticipated fails closed instead of passing unread. Two ecosystem rules matter and
are easy to get backwards:

* In Cargo, a bare `version = "1.2.3"` *is* a caret range — `1.2.3` and `^1.2.3`
  are the same requirement. An exact Cargo pin has to be written `=1.2.3`, so a
  bare version is reported here as the range it actually is.
* In npm, a partial `"24"` resolves as `>=24.0.0 <25.0.0`. Only a full
  major.minor.patch is a pin, so a two-component npm specifier is a range too.

`file:` and `link:` specifiers are accepted. They resolve to a path in this
repository rather than to a registry version, so there is no range for them to
widen into.

**Do the manifests agree with each other?** `rust-toolchain.toml`'s channel is the
toolchain that gets installed and `Cargo.toml`'s `rust-version` is the floor the
crates claim; a channel below that floor is a workspace that cannot build with its
own pinned toolchain. `rust-version` is conventionally written to minor precision,
so the comparison is component-wise over the components `rust-version` actually
states rather than a string equality that would reject the conventional form.
`.node-version` and `package.json`'s `engines.node` are compared byte-for-byte,
because both are full versions and there is no reason for them to differ.

**Does the installed toolchain equal the pin, byte-for-byte?** `cargo`, `go` and
`node` are each invoked and the version is extracted from their output. Only the
carrier prefix is stripped — `v` from node, `go` from go — and what remains is
compared as bytes. `1.26.4` and `1.26.5` are not the same pin and nothing here
treats them as one.

**An uninstalled tool is not a pass.** This mirrors `scripts/ci/measure_coverage.py`,
where an absent toolchain reports `unmeasured` and fails rather than quietly
shrinking the matrix. A tool that is not installed is a comparison that did not
happen, it is printed as `SKIP` on its own line, it is counted separately in the
summary, and by default it is a defect. `--allow-uninstalled` downgrades it to a
reported skip, and is for saying out loud that the comparison was not made. The
summary states the skipped count either way, so a run that checked one pin of three
cannot read like a run that checked three.

What this does not prove: that any pinned version exists upstream, that it is
supported, that it is free of advisories, that the lockfiles resolve under it, or
that anything in this repository builds. It compares declared pins against each
other and against what is installed on the machine running it.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Every manifest this reads. The test suite redirects this whole set into a
# temporary tree; a constant added here and not redirected there would let a case
# inject its drift into a file the validator never opens, and pass for that reason.
RUST_TOOLCHAIN = ROOT / "rust-toolchain.toml"
NODE_VERSION = ROOT / ".node-version"
CARGO_MANIFEST = ROOT / "Cargo.toml"
GO_MOD = ROOT / "apps" / "api" / "go.mod"
WEB_PACKAGE = ROOT / "apps" / "web" / "package.json"

REDIRECTED = (
    "ROOT",
    "RUST_TOOLCHAIN",
    "NODE_VERSION",
    "CARGO_MANIFEST",
    "GO_MOD",
    "WEB_PACKAGE",
)

# A literal version: numeric components, optional prerelease, optional build.
EXACT = re.compile(r"^\d+(\.\d+)*(-[0-9A-Za-z.]+)?(\+[0-9A-Za-z.]+)?$")

# Specifiers that name a path in this repository rather than a registry version.
LOCAL_PREFIXES = ("file:", "link:")

FLOATING_TAGS = {"latest", "next", "*", "x", "X", "canary", "beta", "alpha"}


class Failure(Exception):
    """A manifest could not be read at all, which stops the run rather than
    producing a defect list computed from files that were not there."""


def inexactness(spec: str) -> str | None:
    """Say why `spec` is not an exact version, or return None when it is one.

    The wording is the failure message, so it names the operator that made the
    specifier inexact rather than saying `invalid`. A reviewer reading the output
    should not have to open the manifest to learn what is wrong with it.
    """
    text = spec.strip()
    if not text:
        return "an empty specifier"
    if text in FLOATING_TAGS:
        return f"the floating tag `{text}`"
    if text.startswith("^"):
        return "a caret range"
    if text.startswith("~"):
        return "a tilde range"
    if text.startswith((">=", "<=", "=>", "=<", ">", "<")):
        return "a comparison range"
    if "||" in text:
        return "an alternation range"
    if " - " in text:
        return "a hyphen range"
    if "*" in text or re.search(r"(^|\.)[xX](\.|$)", text):
        return "a wildcard range"
    if not EXACT.match(text):
        return f"not a recognised exact version (`{text}`)"
    return None


def npm_inexactness(spec: str) -> str | None:
    """npm's rule, which is the general rule plus one trap.

    A bare `"24"` is not a pin; npm reads it as `>=24.0.0 <25.0.0`. Only a full
    major.minor.patch names one release, so a shorter literal is reported as the
    range it resolves to rather than accepted as a version.
    """
    text = spec.strip()
    if text.startswith(LOCAL_PREFIXES):
        return None
    reason = inexactness(text)
    if reason is not None:
        return reason
    core = text.split("-", 1)[0].split("+", 1)[0]
    if len(core.split(".")) != 3:
        return (
            f"a partial version (`{text}`), which npm resolves as a range rather "
            "than one release"
        )
    return None


def cargo_inexactness(spec: str) -> str | None:
    """Cargo's rule, which inverts the intuition.

    `version = "1.2.3"` is `^1.2.3`; the two are the same requirement to Cargo. An
    exact Cargo pin is spelled `=1.2.3`, so a bare version is reported as the caret
    range it silently is. Getting this backwards is the whole reason it is written
    out here.
    """
    text = spec.strip()
    if text.startswith("="):
        rest = text[1:].strip()
        reason = inexactness(rest)
        if reason is not None:
            return reason
        return None
    reason = inexactness(text)
    if reason is not None:
        return reason
    return (
        f"a bare version (`{text}`), which Cargo reads as the caret range "
        f"`^{text}`; an exact Cargo pin is written `={text}`"
    )


def read_text(path: Path, label: str) -> str:
    if not path.exists():
        raise Failure(f"{label} does not exist at {path}")
    return path.read_text(encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.name


def parse_rust_toolchain(defects: list[str]) -> str | None:
    """The channel `rustup` installs."""
    document = tomllib.loads(read_text(RUST_TOOLCHAIN, "rust-toolchain.toml"))
    channel = document.get("toolchain", {}).get("channel")
    where = rel(RUST_TOOLCHAIN)
    if not isinstance(channel, str) or not channel:
        defects.append(f"{where}: no `[toolchain].channel` is declared")
        return None
    reason = inexactness(channel)
    if reason is not None:
        defects.append(
            f"{where}: the toolchain channel is {reason}, not an exact version"
        )
        return None
    if len(channel.split(".")) != 3:
        defects.append(
            f"{where}: the toolchain channel `{channel}` is a partial version, "
            "which does not name one Rust release"
        )
        return None
    return channel


def parse_cargo(defects: list[str]) -> str | None:
    """The workspace MSRV, plus every dependency table in the workspace manifest."""
    document = tomllib.loads(read_text(CARGO_MANIFEST, "Cargo.toml"))
    where = rel(CARGO_MANIFEST)

    tables: list[tuple[str, dict]] = []
    workspace = document.get("workspace", {})
    for name in ("dependencies", "dev-dependencies", "build-dependencies"):
        for owner, table in ((f"workspace.{name}", workspace), (name, document)):
            value = table.get(name)
            if isinstance(value, dict):
                tables.append((owner, value))

    for owner, table in tables:
        for crate, value in sorted(table.items()):
            if isinstance(value, str):
                spec = value
            elif isinstance(value, dict):
                if "path" in value or "workspace" in value:
                    # A path dependency resolves inside this repository and a
                    # `workspace = true` inherits the pin checked above it.
                    continue
                spec = value.get("version")
                if not isinstance(spec, str):
                    defects.append(
                        f"{where}: {owner} `{crate}` declares no version, so nothing "
                        "is pinned"
                    )
                    continue
            else:
                defects.append(f"{where}: {owner} `{crate}` has an unreadable version")
                continue
            reason = cargo_inexactness(spec)
            if reason is not None:
                defects.append(
                    f"{where}: {owner} `{crate}` is {reason}, not an exact version"
                )

    rust_version = document.get("workspace", {}).get("package", {}).get("rust-version")
    if not isinstance(rust_version, str) or not rust_version:
        defects.append(f"{where}: no `[workspace.package].rust-version` is declared")
        return None
    reason = inexactness(rust_version)
    if reason is not None:
        defects.append(f"{where}: rust-version is {reason}, not an exact version")
        return None
    return rust_version


def parse_go_mod(defects: list[str]) -> str | None:
    """The `go` directive, and every version in a `require`."""
    where = rel(GO_MOD)
    text = read_text(GO_MOD, "apps/api/go.mod")
    directive: str | None = None
    in_require_block = False

    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        if line.startswith("go ") or line == "go":
            directive = line[2:].strip()
            continue
        if line.startswith("toolchain "):
            value = line[len("toolchain ") :].strip()
            candidate = value[2:] if value.startswith("go") else value
            reason = inexactness(candidate)
            if reason is not None:
                defects.append(
                    f"{where}: the toolchain directive is {reason}, not an exact "
                    "version"
                )
            continue
        if line.startswith("require (") or line == "require (":
            in_require_block = True
            continue
        if in_require_block and line == ")":
            in_require_block = False
            continue

        requirement: str | None = None
        if in_require_block:
            requirement = line
        elif line.startswith("require "):
            requirement = line[len("require ") :].strip()
        if requirement is None:
            continue
        parts = requirement.split()
        if len(parts) < 2:
            continue
        module, version = parts[0], parts[1]
        candidate = version[1:] if version.startswith("v") else version
        reason = inexactness(candidate)
        if reason is not None:
            defects.append(
                f"{where}: require `{module}` is {reason}, not an exact version"
            )

    if directive is None:
        defects.append(f"{where}: no `go` directive is declared")
        return None
    reason = inexactness(directive)
    if reason is not None:
        defects.append(f"{where}: the go directive is {reason}, not an exact version")
        return None
    return directive


def parse_node_version(defects: list[str]) -> str | None:
    """`.node-version` is one line and the whole file is the pin."""
    where = rel(NODE_VERSION)
    text = read_text(NODE_VERSION, ".node-version").strip()
    value = text[1:] if text.startswith("v") else text
    reason = inexactness(value)
    if reason is not None:
        defects.append(f"{where}: the node pin is {reason}, not an exact version")
        return None
    if len(value.split(".")) != 3:
        defects.append(
            f"{where}: the node pin `{value}` is a partial version, which does not "
            "name one Node release"
        )
        return None
    return value


def parse_web_package(defects: list[str]) -> tuple[str | None, int]:
    """Engines, `packageManager`, and both dependency tables.

    Returns the declared node engine when there is one. `engines` is optional here
    and its absence is not a defect; what is a defect is an `engines` block that
    names something other than one release.
    """
    where = rel(WEB_PACKAGE)
    document = json.loads(read_text(WEB_PACKAGE, "apps/web/package.json"))
    checked = 0

    for table_name in ("dependencies", "devDependencies", "optionalDependencies"):
        table = document.get(table_name)
        if not isinstance(table, dict):
            continue
        for package, spec in sorted(table.items()):
            checked += 1
            if not isinstance(spec, str):
                defects.append(f"{where}: {table_name} `{package}` has no specifier")
                continue
            reason = npm_inexactness(spec)
            if reason is not None:
                defects.append(
                    f"{where}: {table_name} `{package}` is {reason}, not an exact "
                    "version"
                )

    node_engine: str | None = None
    engines = document.get("engines")
    if isinstance(engines, dict):
        for tool, spec in sorted(engines.items()):
            checked += 1
            if not isinstance(spec, str):
                defects.append(f"{where}: the `{tool}` engine has no specifier")
                continue
            reason = npm_inexactness(spec)
            if reason is not None:
                defects.append(
                    f"{where}: the `{tool}` engine is {reason}, not an exact version"
                )
                continue
            if tool == "node":
                node_engine = spec.strip()

    package_manager = document.get("packageManager")
    if isinstance(package_manager, str):
        checked += 1
        name, separator, version = package_manager.partition("@")
        if not separator:
            defects.append(
                f"{where}: packageManager `{package_manager}` names no version"
            )
        else:
            reason = npm_inexactness(version.split("+", 1)[0])
            if reason is not None:
                defects.append(
                    f"{where}: packageManager `{name}` is {reason}, not an exact "
                    "version"
                )

    return node_engine, checked


def check_agreement(
    defects: list[str],
    channel: str | None,
    rust_version: str | None,
    node_pin: str | None,
    node_engine: str | None,
) -> None:
    """Two manifests may not name two different versions of one tool."""
    if channel is not None and rust_version is not None:
        stated = rust_version.split(".")
        actual = channel.split(".")
        if actual[: len(stated)] != stated:
            defects.append(
                f"toolchain agreement: rust-toolchain.toml channel `{channel}` and "
                f"Cargo.toml rust-version `{rust_version}` disagree"
            )

    if node_pin is not None and node_engine is not None:
        if node_pin != node_engine:
            defects.append(
                f"toolchain agreement: .node-version `{node_pin}` and "
                f"apps/web/package.json engines.node `{node_engine}` disagree"
            )


def probe(command: list[str]) -> str | None:
    """Run a version command, or return None when the tool is not installed."""
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=60, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def installed_cargo() -> str | None:
    # `cargo 1.96.0 (30a34c682 2026-05-25)`
    output = probe(["cargo", "--version"])
    if output is None:
        return None
    parts = output.split()
    return parts[1] if len(parts) >= 2 else None


def installed_go() -> str | None:
    # `go version go1.26.4 darwin/arm64`
    output = probe(["go", "version"])
    if output is None:
        return None
    for token in output.split():
        if token.startswith("go") and token[2:3].isdigit():
            return token[2:]
    return None


def installed_node() -> str | None:
    # `v22.23.1`
    output = probe(["node", "--version"])
    if output is None:
        return None
    return output[1:] if output.startswith("v") else output


def compare_installed(
    defects: list[str],
    skips: list[str],
    pins: list[tuple[str, str | None, str | None, str]],
    allow_uninstalled: bool,
    declarations_only: bool = False,
) -> int:
    """Compare each installed version with its pin, byte-for-byte.

    A tool that is not installed produces a `SKIP` line and, unless the caller said
    `--allow-uninstalled`, a defect. The comparison that did not happen is never
    folded into the passing count.
    """
    ran = 0
    for tool, pinned, found, source in pins:
        if declarations_only:
            # The caller is checking the repository, not this machine. Every
            # comparison is skipped and every skip is still printed and counted, so
            # a declarations-only run can never be mistaken for one that compared.
            skips.append(
                f"SKIP {tool}: --declarations-only, so the pin `{pinned}` from "
                f"{source} was not compared against this machine"
            )
            continue
        if pinned is None:
            # The pin itself failed to parse and is already a defect above. There
            # is nothing to compare against, and reporting a second failure for the
            # same cause would overstate the damage.
            skips.append(
                f"SKIP {tool}: {source} did not yield a readable pin, so no "
                "comparison was made"
            )
            continue
        if found is None:
            message = (
                f"{tool} is not installed, so the pin `{pinned}` from {source} was "
                "not compared"
            )
            skips.append(f"SKIP {tool}: {message}")
            if not allow_uninstalled:
                defects.append(f"uncompared pin: {message}")
            continue
        ran += 1
        if found != pinned:
            defects.append(
                f"installed {tool} is `{found}`, byte-for-byte unequal to the "
                f"`{pinned}` pinned in {source}"
            )
        else:
            print(f"installed {tool} `{found}` equals the pin in {source}")
    return ran


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that every toolchain pin is exact, that the manifests agree, and "
            "that the installed cargo, go and node match byte-for-byte."
        )
    )
    parser.add_argument(

        "--declarations-only",

        action="store_true",

        help=(

            "Check the manifests against each other and skip every installed-version "

            "comparison. For callers that are testing the repository rather than the "

            "machine: a unit test asserting the tree is well pinned must not also "

            "assert which toolchain the runner happens to ship. Every skipped "

            "comparison is still printed and counted."

        ),

    )
    parser.add_argument(
        "--allow-uninstalled",
        action="store_true",
        help=(
            "Report an absent tool as a skip instead of a defect. The skip is "
            "printed and counted either way; this flag only decides the exit code."
        ),
    )
    arguments = parser.parse_args(argv)

    defects: list[str] = []
    skips: list[str] = []

    channel = parse_rust_toolchain(defects)
    rust_version = parse_cargo(defects)
    go_directive = parse_go_mod(defects)
    node_pin = parse_node_version(defects)
    node_engine, npm_checked = parse_web_package(defects)

    check_agreement(defects, channel, rust_version, node_pin, node_engine)

    ran = compare_installed(
        defects,
        skips,
        [
            ("cargo", channel, installed_cargo(), "rust-toolchain.toml"),
            ("go", go_directive, installed_go(), "apps/api/go.mod"),
            ("node", node_pin, installed_node(), ".node-version"),
        ],
        arguments.allow_uninstalled,
        arguments.declarations_only,
    )

    for skip in skips:
        print(skip)

    read = sum(
        1
        for value in (channel, rust_version, go_directive, node_pin, node_engine)
        if value is not None
    )
    summary = (
        f"{read} pins read from 5 manifests, {npm_checked} npm specifiers checked, "
        f"{ran} of 3 installed comparisons ran, {len(skips)} skipped"
    )

    if defects:
        print("toolchain pins: FAIL", file=sys.stderr)
        for defect in defects:
            print(f"- {defect}", file=sys.stderr)
        print(
            f"toolchain pins: FAIL ({len(defects)} defect(s); {summary})",
            file=sys.stderr,
        )
        return 1

    print(f"toolchain pins: pass ({summary})")
    if arguments.declarations_only:
        # The unqualified sentence claims this machine has the pinned releases,
        # which is exactly what this mode did not check.
        print(
            "claim_scope=declared-pins-only; the manifests name one release each and "
            "agree with one another, and nothing here was compared against an "
            "installed toolchain"
        )
    else:
        print(
            "claim_scope=declared-pins-and-installed-versions-only; "
            "an exact pin means the manifests name one release and this machine has it, "
            "not that the release exists upstream, is supported, is free of advisories, "
            "or that anything here builds"
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as failure:
        print(f"toolchain pins: FAIL — {failure}", file=sys.stderr)
        sys.exit(1)
