#!/usr/bin/env python3
"""Read `packages/schemas/vibeproof-claim-v1.cddl` structurally, and check instances.

`validate_cddl_file` in `validate_planning_artifacts.py` proves the grammar parses
and that named rules exist, and its own docstring says it validates no CBOR
instance against the CDDL. That left a hole the size of the protocol: the exact-byte
vectors could encode any label set at all, sign it correctly, reproduce from the
recorded seed, and every check in this repository stayed green while the bytes and
the normative grammar said different things.

This module closes it for the subset of CDDL the VibeProof messages actually use.
It is deliberately not a CDDL implementation. It handles literal integers and text,
inclusive ranges, `bytes .size N`, `nil` and `true`, homogeneous arrays with
occurrence bounds, named-rule references, and closed integer-labelled maps — which
is every construct in `vibeproof-claim-v1`, `checkpoint-receipt-v1`,
`token-categories` and the two protected-header rules. Anything else raises
`CddlUnsupported` rather than silently reporting a pass, because a checker that
skips what it does not understand reports the same green as one that checked.

Maps are closed: the CDDL preamble says integer labels not listed are invalid, so
an instance whose key set differs from the rule's label set in either direction is
a mismatch. A checker that only required the declared labels to be *present* would
accept an instance carrying extra ones.
"""

from __future__ import annotations

import re
from typing import Any


class CddlMismatch(ValueError):
    """An instance does not satisfy the rule it was checked against."""


class CddlUnsupported(NotImplementedError):
    """The grammar uses a construct this checker does not implement."""


_RULE_START = re.compile(r"^([a-zA-Z][a-zA-Z0-9_-]*)\s*=", re.M)
_INTEGER = re.compile(r"-?\d+")
_RANGE = re.compile(r"(-?\d+)\.\.(-?\d+)")
_BYTES_SIZE = re.compile(r"bytes\s*\.size\s*(\d+)")
_ARRAY_HEAD = re.compile(r"(?:(\d*)\*(\d*)|(\*))\s*(.+)")


def strip_comments(text: str) -> str:
    """Remove `;` comments.

    Every rule body in this grammar carries trailing field-name comments, and some
    of those words are also rule names. Scanning a body for references without
    stripping them first reports a dependency the grammar does not have.
    """
    return re.sub(r";[^\n]*", "", text)


def rule_bodies(text: str) -> dict[str, str]:
    """Split a CDDL document into `{rule name: body}`, comments removed."""
    stripped = strip_comments(text)
    starts = [
        (match.start(), match.group(1)) for match in _RULE_START.finditer(stripped)
    ]
    bodies: dict[str, str] = {}
    for index, (position, name) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else len(stripped)
        if name in bodies:
            raise CddlMismatch(f"CDDL declares rule {name} twice")
        bodies[name] = stripped[position:end].split("=", 1)[1].strip()
    return bodies


def rule_references(bodies: dict[str, str]) -> dict[str, set[str]]:
    """Map each rule to the rule names its body mentions."""
    names = set(bodies)
    return {
        name: {
            token
            for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*", body)
            if token in names
        }
        for name, body in bodies.items()
    }


def reference_closure(roots: set[str], references: dict[str, set[str]]) -> set[str]:
    """Every rule reachable from `roots`, including the roots."""
    seen: set[str] = set()
    pending = list(roots)
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        pending.extend(references.get(name, set()))
    return seen


def is_reference_closed(rules: set[str], references: dict[str, set[str]]) -> set[str]:
    """Return the rules `rules` depends on but does not contain."""
    required: set[str] = set()
    for name in rules:
        required |= references.get(name, set())
    return required - rules


def _split_top_level(body: str, separator: str) -> list[str]:
    """Split on `separator` outside `{}`, `[]`, `()` and text literals.

    Text literals matter: the protected-header rules pin the content type
    `"application/vibemaxxing-claim+cbor"`, and a splitter that treats `/` as a type
    alternative wherever it appears tears that constant in half and then reports the
    fragment as an unknown type.
    """
    parts: list[str] = []
    depth = 0
    quoted = False
    current: list[str] = []
    for character in body:
        if character == '"':
            quoted = not quoted
        elif not quoted and character in "{[(":
            depth += 1
        elif not quoted and character in "}])":
            depth -= 1
        if character == separator and depth == 0 and not quoted:
            parts.append("".join(current))
            current = []
            continue
        current.append(character)
    parts.append("".join(current))
    return [part.strip() for part in parts if part.strip()]


def map_entries(body: str) -> dict[int, str]:
    """Parse a closed integer-labelled map rule body into `{label: type expression}`."""
    body = body.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise CddlUnsupported(f"not a map rule body: {body[:40]!r}")
    entries: dict[int, str] = {}
    for item in _split_top_level(body[1:-1], ","):
        label, separator, expression = item.partition(":")
        if not separator:
            raise CddlUnsupported(f"map entry without a label: {item!r}")
        label = label.strip()
        if not _INTEGER.fullmatch(label):
            raise CddlUnsupported(f"non-integer map label: {label!r}")
        key = int(label)
        if key in entries:
            raise CddlMismatch(f"CDDL map declares label {key} twice")
        entries[key] = expression.strip()
    return entries


def check(expression: str, value: Any, bodies: dict[str, str], path: str = "") -> None:
    """Raise `CddlMismatch` unless `value` satisfies `expression`."""
    expression = expression.strip()
    where = f" at {path}" if path else ""

    alternatives = _split_top_level(expression, "/")
    if len(alternatives) > 1:
        failures = []
        for alternative in alternatives:
            try:
                check(alternative, value, bodies, path)
                return
            except CddlMismatch as failure:
                failures.append(str(failure))
        raise CddlMismatch(
            f"{value!r}{where} matches no alternative of {expression!r}: {failures}"
        )

    if expression == "nil":
        if value is not None:
            raise CddlMismatch(f"expected nil{where}, got {value!r}")
        return
    if expression == "true":
        if value is not True:
            raise CddlMismatch(f"expected true{where}, got {value!r}")
        return
    if expression.startswith('"') and expression.endswith('"'):
        literal = expression[1:-1]
        if value != literal:
            raise CddlMismatch(f"expected {literal!r}{where}, got {value!r}")
        return
    if _INTEGER.fullmatch(expression):
        if value is not int(expression) and value != int(expression):
            raise CddlMismatch(f"expected {expression}{where}, got {value!r}")
        if isinstance(value, bool):
            raise CddlMismatch(f"expected {expression}{where}, got a boolean")
        return

    range_match = _RANGE.fullmatch(expression)
    if range_match:
        low, high = int(range_match.group(1)), int(range_match.group(2))
        if isinstance(value, bool) or not isinstance(value, int):
            raise CddlMismatch(
                f"expected an integer in {expression}{where}, got {value!r}"
            )
        if not low <= value <= high:
            raise CddlMismatch(f"{value} is outside {expression}{where}")
        return

    size_match = _BYTES_SIZE.fullmatch(expression)
    if size_match:
        width = int(size_match.group(1))
        if not isinstance(value, bytes):
            raise CddlMismatch(
                f"expected {width} bytes{where}, got {type(value).__name__}"
            )
        if len(value) != width:
            raise CddlMismatch(f"expected {width} bytes{where}, got {len(value)}")
        return

    if expression.startswith("[") and expression.endswith("]"):
        _check_array(expression, value, bodies, path)
        return

    if expression.startswith("{"):
        _check_map(map_entries(expression), value, bodies, path)
        return

    if expression in bodies:
        body = bodies[expression]
        if body.startswith("{"):
            _check_map(map_entries(body), value, bodies, path or expression)
            return
        check(body, value, bodies, path or expression)
        return

    raise CddlUnsupported(f"unsupported CDDL type expression: {expression!r}")


def _check_array(
    expression: str, value: Any, bodies: dict[str, str], path: str
) -> None:
    where = f" at {path}" if path else ""
    inner = expression[1:-1].strip()
    head = _ARRAY_HEAD.fullmatch(inner)
    if head is None:
        raise CddlUnsupported(f"unsupported array expression: {expression!r}")
    minimum = int(head.group(1)) if head.group(1) else 0
    maximum = int(head.group(2)) if head.group(2) else None
    element = head.group(4).strip()
    if not isinstance(value, list):
        raise CddlMismatch(f"expected an array{where}, got {type(value).__name__}")
    if len(value) < minimum or (maximum is not None and len(value) > maximum):
        raise CddlMismatch(
            f"array{where} holds {len(value)} elements, outside the declared "
            f"occurrence bounds of {expression!r}"
        )
    for index, item in enumerate(value):
        check(element, item, bodies, f"{path}[{index}]")


def _check_map(
    entries: dict[int, str], value: Any, bodies: dict[str, str], path: str
) -> None:
    where = f" at {path}" if path else ""
    if not isinstance(value, dict):
        raise CddlMismatch(f"expected a map{where}, got {type(value).__name__}")
    declared, present = set(entries), set(value)
    if declared != present:
        raise CddlMismatch(
            f"map{where} does not carry exactly the declared labels; "
            f"missing={sorted(declared - present)} undeclared={sorted(present - declared)}"
        )
    for label in sorted(declared):
        check(entries[label], value[label], bodies, f"{path}:{label}")
