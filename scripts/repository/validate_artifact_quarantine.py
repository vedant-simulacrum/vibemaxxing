#!/usr/bin/env python3
"""Every quarantined artifact carries its quarantine notice in its own source.

PF-001 asked that the shadow VibeProof protocol be quarantined, and its acceptance
criterion was:

    grep -rn 'VibeProof v1' crates/vibeproof-core apps/api/cmd/api
    returns no line that omits the word `prototype`

That criterion passed before any quarantine work was done, because
`crates/vibeproof-core/README.md` was a two-line stub that said nothing at all. A
criterion phrased as the absence of a bad mention is satisfied by the absence of any
mention, so it measured silence and reported it as compliance.

This validator inverts it. `conformance/p1140f/artifact-authority-v1.json` records
which artifacts are prototypes, what they are incompatible with, and what they may not
be used for. Anything it classes as a prototype must say so in its own source, and must
list the same incompatibilities and prohibitions the record does — so a reader who
opens the file learns its status without knowing the record exists, and a maintainer
who edits one has to edit the other.

The record is the authority. When the two disagree this fails, and the repair is to
edit the source notice to match the record.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "conformance" / "p1140f" / "artifact-authority-v1.json"

# A prototype directory is quarantined by a notice in one of these, in order.
DIRECTORY_NOTICE_FILES = ("README.md", "src/lib.rs")

# Comment syntax varies; the notice is prose, so compare on words rather than markup.
MARKUP = re.compile(r"^\s*(?://[/!]?|#|\*|-|\s)+", re.MULTILINE)


class Failure(Exception):
    """A quarantined artifact does not carry the notice its record requires."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def structured_notice(document: object, path: Path) -> tuple[Path, str]:
    """Flatten a structured quarantine block into text the prose checks can read.

    JSON has no comments and a YAML suite entry is a record rather than a file, so
    those carry the notice as data. The rule enforced is identical either way; only
    the place the words live differs.
    """
    require(
        isinstance(document, dict) and bool(document),
        f"{path}: quarantined and carries no quarantine block",
    )
    assert isinstance(document, dict)
    return path, json.dumps(document)


def notice_text(root: Path, recorded: str) -> tuple[Path, str]:
    """Return the file whose notice governs `recorded`, and its searchable text."""
    file_part, _, fragment = recorded.partition("#")
    path = root / file_part

    if fragment:
        # A record inside a file: the notice belongs to the entry, not the document.
        require(path.exists(), f"{recorded}: names a file that does not exist")
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        # The fragment names an `id` in whichever list the document holds; every list
        # is searched so this does not hard-code that suites.yaml calls its list
        # `suites`, which is exactly the kind of coupling that goes stale unnoticed.
        entries = [
            entry
            for value in (
                document.values() if isinstance(document, dict) else [document]
            )
            if isinstance(value, list)
            for entry in value
            if isinstance(entry, dict)
        ]
        require(
            bool(entries),
            f"{recorded}: fragment addressing needs a list of records to search",
        )
        matched = [entry for entry in entries if entry.get("id") == fragment]
        require(
            len(matched) == 1, f"{recorded}: fragment matches {len(matched)} entries"
        )
        # The whole record is the notice. `evals/suites/suites.yaml` is read by a
        # deliberately minimal hand-rolled parser in scripts/ci/run_evals.py that
        # accepts flat `key: value` lines only, so a nested quarantine block is not
        # expressible there; the words live in the fields that already exist —
        # `authority_class` and `scope_note` — and searching the serialised record
        # finds them without this validator caring which field they landed in.
        return structured_notice(matched[0], path)

    if path.is_dir():
        for candidate in DIRECTORY_NOTICE_FILES:
            resolved = path / candidate
            if resolved.exists():
                return resolved, MARKUP.sub("", resolved.read_text(encoding="utf-8"))
        raise Failure(
            f"{recorded} is a quarantined directory with none of "
            f"{DIRECTORY_NOTICE_FILES} to carry its notice"
        )

    require(path.exists(), f"{recorded} is recorded as quarantined and does not exist")
    if path.suffix == ".json":
        document = json.loads(path.read_text(encoding="utf-8"))
        return structured_notice(document.get("_quarantine"), path)
    return path, MARKUP.sub("", path.read_text(encoding="utf-8"))


def main() -> int:
    record = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    quarantined = [
        artifact
        for artifact in record["artifacts"]
        if "prototype" in artifact["authority_class"]
    ]
    require(
        bool(quarantined),
        "no artifact is classed as a prototype; either the shadow protocol was retired "
        "and this validator should go with it, or the record has been emptied",
    )

    for artifact in quarantined:
        where = artifact["path"]
        source, text = notice_text(ROOT, where)

        require(
            "P-1140F-1" in text,
            f"{where}: quarantined by the record, and {source.name} does not name "
            "P-1140F-1 as the gate that quarantines it",
        )
        require(
            "prototype" in text.lower(),
            f"{where}: quarantined by the record, and {source.name} never calls it a "
            "prototype — the word a reader greps for",
        )
        require(
            artifact["normative_owner"] in text,
            f"{where}: {source.name} does not name its normative owner "
            f"{artifact['normative_owner']}, so a reader cannot find what it is wrong "
            "against",
        )

        # The two lists are the whole content of the quarantine. A notice that omits one
        # understates the fence; there is no reason to state it loosely.
        for incompatibility in artifact["known_incompatibilities"]:
            require(
                incompatibility in text,
                f"{where}: the record lists the incompatibility "
                f"{incompatibility!r} and {source.name} does not",
            )
        for prohibition in artifact["prohibited_uses"]:
            require(
                prohibition in text,
                f"{where}: the record prohibits {prohibition!r} and {source.name} "
                "does not say so",
            )

        print(f"quarantine notice: {where} -> {source.relative_to(ROOT)}")

    print(f"artifact quarantine: pass ({len(quarantined)} quarantined artifacts)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as failure:
        print(f"artifact quarantine: FAIL — {failure}", file=sys.stderr)
        sys.exit(1)
