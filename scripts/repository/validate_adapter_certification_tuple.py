#!/usr/bin/env python3
"""The adapter manifest, the tuple authority and the certification row name one tuple.

SR-009 is the finding that a certification in this repository could not be said out loud.
PF-071 bound `packages/schemas/adapter-manifest.schema.json#certification` to the
certification *state* vocabulary and said in its own unit block what it had not done:

    "It does not add the collector-artifact, accounting-arithmetic or privacy-binding
    digests `UNIVERSAL_AGENT_COMPATIBILITY.md` names as tuple dimensions, nor the
    `version_min`/`version_max_exclusive` range `compatibility-tuple-v1.schema.json`
    requires against this file's single `source_version` string."

That residue is what this file checks. The manifest's `certification` block held one
`source_version`, one `platform_profile_id` and one `mode`, above four manifest-level
arrays - `source_products`, `platforms`, `modes`, `accounting_profile_ids` - so one
certification authorized every combination those arrays multiplied into. Certify adapter
one's loopback OTLP tuple and its session-log tuple was certified with it, at the 174x
input undercount D-098 measured. It carried no validity interval and no revocation, so an
expired certification and a current one were the same document. And a point version
cannot express a certified range at all.

Three authorities have to agree about what a tuple is, and none of them read each other:

* `packages/schemas/compatibility-tuple-v1.schema.json` defines the tuple. It is the
  authority `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md` names as normative;
* `packages/schemas/adapter-manifest.schema.json#certification` is what an adapter author
  writes, and is the artifact SR-009 names first;
* `source_certifications` in `packages/schemas/planning-schema.sql` is the persistence
  owner, and its `unique tuple_digest` is why it does not need a column per dimension.

Every check below is a comparison between two or more of those three, so it fails when
either side moves. A dimension is either bound in all three or absent from one with a
recorded reason, and a reason recorded for a dimension that *is* present fails too - so
neither half can be satisfied by emptiness and an excuse cannot outlive the hole it
excused.

A green run says these three artifacts state one tuple. It does not say any tuple is
certified: every state this repository can reach is `candidate` or `uncertified`,
`docs/integrations/ADAPTER_CERTIFICATION_POLICY.md` says so in terms, and one of the
checks below refuses a committed manifest example that claims otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "schemas"
MANIFEST = SCHEMAS / "adapter-manifest.schema.json"
TUPLE = SCHEMAS / "compatibility-tuple-v1.schema.json"
SQL = SCHEMAS / "planning-schema.sql"
PROFILES = SCHEMAS / "platform-profile-registry-v1.json"
EXAMPLE = SCHEMAS / "examples" / "adapter-manifest.valid.json"
POLICY = ROOT / "docs" / "integrations" / "ADAPTER_CERTIFICATION_POLICY.md"
COMPATIBILITY = ROOT / "docs" / "integrations" / "UNIVERSAL_AGENT_COMPATIBILITY.md"

TABLE = "source_certifications"
TUPLE_LIST = "certification.tuples[]"


class Failure(Exception):
    """Two authorities describe the same tuple differently."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


# ---------------------------------------------------------------------------
# The tuple, dimension by dimension
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Dimension:
    """One dimension of the atomic compatibility tuple, in all three authorities.

    `manifest` and `sql` are paths into the other two authorities, and each may be None
    exactly when the matching reason says why. An absence with a blank reason fails, and
    a reason recorded against a path that does resolve fails, so the table cannot be
    satisfied by emptiness in either direction.
    """

    manifest: str | None
    sql: str | None
    manifest_absence_reason: str = ""
    sql_absence_reason: str = ""


# `tuple_digest` is the reason most dimensions have no column. `source_certifications`
# stores it `unique`, and it is SHA-256 over the deterministic CBOR encoding of the whole
# tuple record, so a row naming a digest has already named every dimension that went into
# it. Adding columns for them would create a second place the same fact could be wrong.
BOUND_BY_DIGEST = (
    "No column. `source_certifications.tuple_digest` is `unique` and is SHA-256 over the "
    "deterministic CBOR encoding of the whole tuple, so the row names this dimension by "
    "naming the digest. A column would be a second place the same fact could disagree "
    "with itself."
)

TUPLE_DIMENSIONS: dict[str, Dimension] = {
    "tuple_digest": Dimension(f"{TUPLE_LIST}.tuple_digest", "tuple_digest"),
    "artifact.adapter_id": Dimension("adapter_id", "adapter_id"),
    "artifact.artifact_sha256": Dimension(
        "artifact_sha256", None, sql_absence_reason=BOUND_BY_DIGEST
    ),
    "artifact.release_set_version": Dimension(
        None,
        None,
        manifest_absence_reason=(
            "The release set is assigned by the release authority and owned by "
            "`packages/schemas/release-set-v1.schema.json`; an adapter manifest is "
            "written before any release set exists and cannot declare which one will "
            "carry it. The dimension is optional in the tuple for the same reason."
        ),
        sql_absence_reason=BOUND_BY_DIGEST,
    ),
    "source.source_product_id": Dimension(
        f"{TUPLE_LIST}.source.source_product_id", "source_product_id"
    ),
    "source.version_min": Dimension(
        f"{TUPLE_LIST}.source.version_min", None, sql_absence_reason=BOUND_BY_DIGEST
    ),
    "source.version_max_exclusive": Dimension(
        f"{TUPLE_LIST}.source.version_max_exclusive",
        None,
        sql_absence_reason=BOUND_BY_DIGEST,
    ),
    "source.schema_url": Dimension(
        f"{TUPLE_LIST}.source.schema_url", None, sql_absence_reason=BOUND_BY_DIGEST
    ),
    "source.semantic_conventions_version": Dimension(
        f"{TUPLE_LIST}.source.semantic_conventions_version",
        None,
        sql_absence_reason=BOUND_BY_DIGEST,
    ),
    "observation_mode": Dimension(f"{TUPLE_LIST}.observation_mode", "observation_mode"),
    "platform_profile_id": Dimension(
        f"{TUPLE_LIST}.platform_profile_id", "platform_profile_id"
    ),
    "accounting.accounting_profile_id": Dimension(
        f"{TUPLE_LIST}.accounting.accounting_profile_id", "accounting_profile_id"
    ),
    "accounting.accounting_profile_sha256": Dimension(
        f"{TUPLE_LIST}.accounting.accounting_profile_sha256",
        None,
        sql_absence_reason=BOUND_BY_DIGEST,
    ),
    "accounting.arithmetic_sha256": Dimension(
        f"{TUPLE_LIST}.accounting.arithmetic_sha256",
        None,
        sql_absence_reason=BOUND_BY_DIGEST,
    ),
    "privacy_binding.attribute_allowlist_sha256": Dimension(
        f"{TUPLE_LIST}.privacy_binding.attribute_allowlist_sha256",
        None,
        sql_absence_reason=BOUND_BY_DIGEST,
    ),
    "privacy_binding.strip_list_sha256": Dimension(
        f"{TUPLE_LIST}.privacy_binding.strip_list_sha256",
        None,
        sql_absence_reason=BOUND_BY_DIGEST,
    ),
    "privacy_binding.rejects_undecodable_datapoint": Dimension(
        f"{TUPLE_LIST}.privacy_binding.rejects_undecodable_datapoint",
        None,
        sql_absence_reason=BOUND_BY_DIGEST,
    ),
    "duplicate_domain": Dimension(
        f"{TUPLE_LIST}.duplicate_domain", None, sql_absence_reason=BOUND_BY_DIGEST
    ),
}

# A dimension the tuple authority leaves optional and the manifest requires. Declared,
# because a strengthening that appears silently is indistinguishable from a divergence,
# and the next reader has no way to tell which one they are looking at.
MANIFEST_STRENGTHENED: dict[str, str] = {
    "duplicate_domain": (
        "The manifest already requires a non-empty `duplicate_domains` array, so an "
        "adapter that reaches no exclusivity unit cannot be declared at all. A certified "
        "tuple that named none would be one the survivor rule could not place against "
        "any other observer of the same execution."
    ),
}

# The certification record's own fields: not dimensions of the tuple, but facts about the
# certification of one. Each is bound to a manifest path, because these are precisely the
# fields SR-009 records as missing - "it carries no validity interval and no revocation".
RECORD_BINDING: dict[str, tuple[str, str]] = {
    "state": (
        "certification.state",
        "The lifecycle state, PF-071's repair. Nine values in the manifest: the eight of "
        "the `source-certification` machine plus `uncertified`, which is not a machine "
        "state because a manifest bound to no certification has no aggregate.",
    ),
    "effective_ceiling": (
        f"{TUPLE_LIST}.max_public_profile",
        "Per tuple rather than per manifest, because the ceiling is what differs between "
        "two tuples of one adapter: D-098 caps the session-log tuple at private "
        "analytics and not the OTLP one. The two columns spell the same three classes "
        "differently and CEILING_PROJECTION declares the mapping rather than leaving a "
        "security-critical translation to a reader.",
    ),
    "superseded_by_source_certification_id": (
        f"{TUPLE_LIST}.superseded_by_tuple_digest",
        "The tuple that replaced this one. The DDL names a row and the manifest names a "
        "digest, because a manifest cannot know a server-assigned row identifier and "
        "D-058 makes trust digest-addressed in any case.",
    ),
    "valid_from": (
        f"{TUPLE_LIST}.validity.valid_from",
        "Half of the validity interval SR-009 records as absent.",
    ),
    "valid_until": (
        f"{TUPLE_LIST}.validity.valid_until",
        "The other half. `check (valid_until is null or valid_from is not null)` is "
        "mirrored by an if/then in the manifest.",
    ),
    "revoked_at": (
        f"{TUPLE_LIST}.revocation.revoked_at",
        "The revocation SR-009 records as absent.",
    ),
    "revocation_reason_code": (
        f"{TUPLE_LIST}.revocation.revocation_reason_code",
        "`check ((revoked_at is null) = (revocation_reason_code is null))` is mirrored "
        "by an if/then/else, so a revocation nobody can appeal and a sanction with no "
        "event are both unrepresentable.",
    ),
}

# Columns of `source_certifications` that are neither a tuple dimension nor a bound
# record field, each with the reason the manifest does not carry it. This is the half
# that stops the tables above being satisfied by addition: an eighteenth column appearing
# with no recorded reason fails.
RECORD_ONLY_COLUMNS: dict[str, str] = {
    "source_certification_id": (
        "The server's own aggregate key. A manifest is written before any certification "
        "row exists and never learns the identifier; the tuple is addressed by digest."
    ),
    "evidence_profile_id": (
        "Assigned by the release authority when the certification is created, not "
        "declared by the adapter. Public evidence status is assigned by the server "
        "verifier and never selected by the client, so a manifest field for it would be "
        "a client selecting one."
    ),
    "revision": (
        "The row's revision under the append-only model. A property of the persistence "
        "record rather than of the tuple, which is immutable by construction: change a "
        "dimension and the digest changes and it is a different tuple."
    ),
    "created_at": "When the row was written. Server clock, server fact.",
}

# Properties of the `certification` block that are not the tuple list and not a bound
# record field. Same rule: a fifth property with no entry fails.
CERTIFICATION_BLOCK_ONLY: dict[str, str] = {
    "bundle_sha256": (
        "PF-071. The signed result bundle, null exactly while uncertified. It is a "
        "property of the certification rather than of any one tuple: one bundle covers "
        "the run over the tuples listed, and `certification_results` is its owner."
    ),
    "suite_version": (
        "The conformance suite version that produced that bundle, null on the same "
        "condition and for the same reason - a suite that has never run has no version."
    ),
}

# `capability_ceiling.max_public_profile` and `source_certifications.effective_ceiling`
# spell the same three evidence classes differently. The mapping is declared because it
# is not the identity: a reader who assumed it was would publish `standard-competitive`
# into a column whose CHECK admits `standard`, and the constraint that keeps an
# uncertified tuple out of competition is written in terms of that column.
CEILING_PROJECTION: dict[str, str] = {
    "private-analytics": "private-analytics",
    "standard-competitive": "standard",
    "hardened-source-bound": "hardened",
}

# The manifest-level arrays that used to be the coverage statement. They stay, as a
# declaration of what the adapter can reach; what changed is that nothing multiplies
# them. Every enumerated tuple must draw its dimension from the matching array, which is
# containment rather than product.
COVERAGE_ARRAYS: dict[str, str] = {
    "source.source_product_id": "source_products",
    "observation_mode": "modes",
    "accounting.accounting_profile_id": "accounting_profile_ids",
    "duplicate_domain": "duplicate_domains",
}

# The three properties the old block carried, which is where the cross product came from:
# one value each, multiplied by four arrays nobody bound them to.
CROSS_PRODUCT_CARRIERS = ("source_version", "platform_profile_id", "mode")


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(schema: dict, node: dict) -> dict:
    """Follow a local `$ref` chain. Remote refs are refused rather than fetched."""
    seen = 0
    while "$ref" in node:
        reference = node["$ref"]
        require(
            reference.startswith("#/"),
            f"{reference!r} is not a local reference; a schema that resolves over the "
            "network is one whose meaning depends on something outside this repository",
        )
        target: object = schema
        for token in reference[2:].split("/"):
            require(
                isinstance(target, dict) and token in target,
                f"{reference!r} does not resolve",
            )
            target = target[token]  # type: ignore[index]
        require(isinstance(target, dict), f"{reference!r} does not resolve to a schema")
        node = target  # type: ignore[assignment]
        seen += 1
        require(seen < 16, f"{reference!r} is a reference cycle")
    return node


def walk(schema: dict, node: dict, prefix: str = "") -> dict[str, dict]:
    """Every leaf of an object schema, as dotted paths. Sub-objects recurse."""
    node = resolve(schema, node)
    leaves: dict[str, dict] = {}
    for name, child in (node.get("properties") or {}).items():
        child = resolve(schema, child)
        path = f"{prefix}{name}"
        if child.get("type") == "object" and child.get("properties"):
            leaves.update(walk(schema, child, f"{path}."))
        else:
            leaves[path] = child
    return leaves


def required_paths(schema: dict, node: dict, prefix: str = "") -> set[str]:
    node = resolve(schema, node)
    required: set[str] = set()
    for name in node.get("required") or []:
        child = (node.get("properties") or {}).get(name)
        if child is None:
            continue
        child = resolve(schema, child)
        path = f"{prefix}{name}"
        if child.get("type") == "object" and child.get("properties"):
            required |= required_paths(schema, child, f"{path}.")
        else:
            required.add(path)
    return required


def manifest_node(schema: dict, path: str) -> dict | None:
    """Resolve a dotted manifest path. `x[]` steps through an array's `items`."""
    node: dict = schema
    for token in path.split("."):
        array = token.endswith("[]")
        name = token[:-2] if array else token
        node = resolve(schema, node)
        properties = node.get("properties") or {}
        if name not in properties:
            return None
        node = resolve(schema, properties[name])
        if array:
            items = node.get("items")
            if items is None:
                return None
            node = resolve(schema, items)
    return node


def manifest_required(schema: dict, path: str) -> bool:
    """Required at every step, not only the last one.

    A leaf declared `required` inside an object its own parent leaves optional is a leaf
    a manifest may omit by omitting the object above it, which is how the validity
    interval could be dropped whole while every field inside it still read as mandatory.
    """
    tokens = path.split(".")
    for index in range(len(tokens)):
        parent = ".".join(tokens[:index])
        leaf = tokens[index].removesuffix("[]")
        owner = manifest_node(schema, parent) if parent else resolve(schema, schema)
        if owner is None or leaf not in (owner.get("required") or []):
            return False
    return True


def sql_table_bodies(text: str) -> dict[str, str]:
    return {
        match.group(1): match.group(2)
        for match in re.finditer(
            r"^create table ([a-z0-9_]+) \((.*?)^\);", text, re.S | re.M
        )
    }


def sql_columns(body: str) -> list[str]:
    columns: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^  ([a-z][a-z0-9_]*)\s+[a-z]", line)
        if match and match.group(1) not in ("constraint", "unique", "foreign", "check"):
            columns.append(match.group(1))
    return columns


def sql_check_values(body: str, column: str) -> list[str]:
    match = re.search(rf"{column} in \(([^)]*)\)", body)
    if not match:
        raise Failure(f"no `check ({column} in (...))` constraint on {TABLE} to read")
    return re.findall(r"'([^']*)'", match.group(1))


def canonical_pattern(pattern: str) -> str:
    """`[a-f0-9]` and `[0-9a-f]` are one character class written two ways."""

    def normalise(match: re.Match[str]) -> str:
        tokens = re.findall(r"\\.|[^\\-]-[^\\-]|.", match.group(1))
        return "[" + "".join(sorted(tokens)) + "]"

    return re.sub(r"\[([^\]]*)\]", normalise, pattern)


def shape(node: dict) -> tuple[object, object, object]:
    types = node.get("type")
    if isinstance(types, list):
        types = tuple(sorted(types))
    enum = node.get("enum")
    if isinstance(enum, list):
        enum = tuple(enum)
    pattern = node.get("pattern")
    return types, enum, canonical_pattern(pattern) if pattern else None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_the_dimension_table_is_the_tuple_authority(tuple_schema: dict) -> None:
    """The table above is checked against the file it claims to transcribe.

    Every check that follows reads TUPLE_DIMENSIONS. If the table and
    `compatibility-tuple-v1.schema.json` may drift, all of them are comparisons against a
    copy, which is the failure mode SR-009 is made of.
    """
    tuple_node = tuple_schema["$defs"]["tuple"]
    leaves = set(walk(tuple_schema, tuple_node))
    declared = set(TUPLE_DIMENSIONS)
    require(
        leaves == declared,
        "compatibility-tuple-v1.schema.json and this validator's dimension table "
        "disagree about what a tuple is: "
        f"only-in-tuple-schema={sorted(leaves - declared)} "
        f"only-in-binding-table={sorted(declared - leaves)}. The tuple authority is "
        "`compatibility-tuple-v1.schema.json`; a dimension it gains or loses has to "
        "reach the adapter manifest and the certification row, and this table is where "
        "that is written down",
    )


def check_every_dimension_reaches_the_manifest(
    manifest: dict, tuple_schema: dict
) -> None:
    tuple_required = required_paths(tuple_schema, tuple_schema["$defs"]["tuple"])
    strengthened: set[str] = set()
    for name, dimension in TUPLE_DIMENSIONS.items():
        if dimension.manifest is None:
            require(
                bool(dimension.manifest_absence_reason.strip()),
                f"tuple dimension {name} is recorded as absent from "
                "adapter-manifest.schema.json with no reason. An absence with no reason "
                "is indistinguishable from a dimension nobody noticed was missing, "
                "which is how this block lost six of them",
            )
            require(
                name not in tuple_required,
                f"tuple dimension {name} is required by compatibility-tuple-v1.schema."
                "json and recorded as absent from the manifest. A required dimension "
                "cannot be excused",
            )
            continue
        node = manifest_node(manifest, dimension.manifest)
        require(
            node is not None,
            f"adapter-manifest.schema.json carries no {dimension.manifest} for tuple "
            f"dimension {name}. Every dimension compatibility-tuple-v1.schema.json "
            "declares is either bound in the manifest or recorded as absent with a "
            "reason; this one is neither",
        )
        assert node is not None
        required_here = manifest_required(manifest, dimension.manifest)
        if name in tuple_required:
            require(
                required_here,
                f"{dimension.manifest} is optional in adapter-manifest.schema.json and "
                f"required by compatibility-tuple-v1.schema.json. An optional dimension "
                "is one a manifest may omit and a certification may then be read as "
                "covering every value of",
            )
        elif required_here:
            strengthened.add(name)

        tuple_node = walk(tuple_schema, tuple_schema["$defs"]["tuple"])[name]
        require(
            shape(node) == shape(tuple_node),
            f"tuple dimension {name} has a different shape in the two schemas: "
            f"manifest={shape(node)} tuple={shape(tuple_node)}. A second spelling of one "
            "vocabulary is the duplication SR-009 exists to remove",
        )

    require(
        strengthened == set(MANIFEST_STRENGTHENED),
        "the manifest requires dimensions the tuple authority leaves optional, and the "
        f"declared list does not match: only-in-schema={sorted(strengthened - set(MANIFEST_STRENGTHENED))} "
        f"only-in-table={sorted(set(MANIFEST_STRENGTHENED) - strengthened)}",
    )
    for name, reason in MANIFEST_STRENGTHENED.items():
        require(
            bool(reason.strip()),
            f"tuple dimension {name} is strengthened in the manifest with no reason",
        )


def check_every_dimension_reaches_the_certification_row(columns: set[str]) -> None:
    for name, dimension in TUPLE_DIMENSIONS.items():
        if dimension.sql is None:
            require(
                bool(dimension.sql_absence_reason.strip()),
                f"tuple dimension {name} is recorded as absent from {TABLE} with no "
                "reason",
            )
            continue
        require(
            dimension.sql in columns,
            f"{TABLE} has no column {dimension.sql} for tuple dimension {name}. The "
            "certification row is the persistence owner; a dimension it cannot store is "
            "one no accepted claim can be explained by",
        )


def check_the_reasons_have_not_outlived_their_holes(columns: set[str]) -> None:
    """A reason recorded against a column that now exists is a stale excuse."""
    for name, dimension in TUPLE_DIMENSIONS.items():
        if dimension.sql is not None:
            continue
        column = name.rpartition(".")[2]
        require(
            column not in columns,
            f"tuple dimension {name} is recorded as bound by tuple_digest alone, and "
            f"{TABLE} now carries a {column} column. Two places for one fact is two "
            "places it can be wrong; either the column goes or the reason does",
        )


def check_the_certification_row_holds_nothing_unaccounted(columns: set[str]) -> None:
    dimension_columns = {d.sql for d in TUPLE_DIMENSIONS.values() if d.sql}
    accounted = dimension_columns | set(RECORD_BINDING) | set(RECORD_ONLY_COLUMNS)
    require(
        columns == accounted,
        f"{TABLE} does not hold exactly the tuple dimensions, the bound record fields "
        f"and its recorded server-only columns: only-in-sql={sorted(columns - accounted)} "
        f"only-in-binding={sorted(accounted - columns)}. A column with no entry in any "
        "of the three tables is a fact one authority carries and the others do not",
    )
    for column, reason in RECORD_ONLY_COLUMNS.items():
        require(
            bool(reason.strip()),
            f"{TABLE}.{column} is excluded from the manifest with no reason",
        )
        require(
            column not in dimension_columns and column not in RECORD_BINDING,
            f"{TABLE}.{column} is recorded as server-only and is also bound",
        )


def check_the_record_fields_bind(manifest: dict, columns: set[str]) -> None:
    """The validity interval and the revocation SR-009 records as absent."""
    for column, (path, note) in RECORD_BINDING.items():
        require(bool(note.strip()), f"{TABLE}.{column} is bound with no recorded note")
        require(column in columns, f"{TABLE} has no column {column}")
        require(
            manifest_node(manifest, path) is not None,
            f"adapter-manifest.schema.json carries no {path} for {TABLE}.{column}. "
            "SR-009 records that this block 'carries no validity interval and no "
            "revocation'; that is this check",
        )
        require(
            manifest_required(manifest, path),
            f"{path} is optional, so a manifest may omit it and an expired or revoked "
            "certification is again indistinguishable from a current one",
        )


def check_the_version_range_replaced_the_point_version(manifest: dict) -> None:
    source = manifest_node(manifest, f"{TUPLE_LIST}.source")
    require(
        source is not None,
        f"adapter-manifest.schema.json carries no {TUPLE_LIST}.source",
    )
    assert source is not None
    properties = set(source.get("properties") or {})
    require(
        "source_version" not in properties,
        "the certified tuple still carries a single `source_version`. A point version "
        "cannot express a certified range: compatibility-tuple-v1.schema.json requires "
        "`version_min` and `version_max_exclusive`, and a certification of one point "
        "release either says nothing about the release beside it or is read as covering "
        "everything `source_version_range` declares",
    )
    for bound in ("version_min", "version_max_exclusive"):
        require(
            bound in properties and bound in (source.get("required") or []),
            f"the certified tuple does not require `{bound}`; an open-ended range "
            "certifies software that does not exist yet",
        )

    certification = manifest["properties"]["certification"]
    stale = sorted(set(certification.get("properties") or {}) & {"source_version"})
    require(
        not stale,
        f"the certification block still carries {stale} above the tuple list",
    )


def check_the_cross_product_is_unrepresentable(manifest: dict) -> None:
    """The half PF-071 explicitly did not touch.

    The defect was not that the block named a mode; it was that it named *one* of each
    dimension while the manifest named arrays of them, and nothing said which of the two
    was the coverage. Removing the single-valued carriers and enumerating tuples is what
    makes the product unrepresentable rather than merely discouraged: there is no field
    left from which a combination could be derived.
    """
    certification = manifest["properties"]["certification"]
    properties = certification.get("properties") or {}
    offenders = sorted(set(properties) & set(CROSS_PRODUCT_CARRIERS))
    require(
        not offenders,
        f"the certification block carries {offenders} as single values above the "
        "manifest-level arrays "
        f"{sorted(COVERAGE_ARRAYS.values()) + ['platforms']}. One certification then "
        "authorizes every combination those arrays multiply into, which is SR-009: "
        "certify adapter one's loopback OTLP tuple and its session-log tuple is "
        "certified with it, at the 174x input undercount D-098 measured",
    )
    tuples = properties.get("tuples")
    require(
        isinstance(tuples, dict) and tuples.get("type") == "array",
        "the certification block declares no `tuples` array, so coverage is not stated "
        "anywhere and falls back to whatever a reader multiplies",
    )
    assert isinstance(tuples, dict)
    require(
        tuples.get("uniqueItems") is True,
        "`certification.tuples` admits the same tuple twice",
    )
    require(
        isinstance(tuples.get("maxItems"), int),
        "`certification.tuples` is unbounded; a certification that may enumerate "
        "without limit is one that can restate the cross product entry by entry",
    )
    for name, array in COVERAGE_ARRAYS.items():
        require(
            array in (manifest.get("properties") or {}),
            f"the manifest no longer declares `{array}`, which is the array "
            f"{name} is contained by",
        )

    unaccounted = sorted(
        set(properties)
        - {"tuples"}
        - set(CERTIFICATION_BLOCK_ONLY)
        - {
            path.split(".")[1]
            for path, _ in RECORD_BINDING.values()
            if path.startswith("certification.") and "[]" not in path.split(".")[1]
        }
    )
    require(
        not unaccounted,
        f"the certification block carries {unaccounted} with no entry in "
        "CERTIFICATION_BLOCK_ONLY or RECORD_BINDING. A property added here with no "
        "recorded reason is how the single-valued carriers arrived",
    )
    for name, reason in CERTIFICATION_BLOCK_ONLY.items():
        require(
            bool(reason.strip()),
            f"certification.{name} is recorded as a block-level field with no reason",
        )

    certified = manifest_node(manifest, TUPLE_LIST)
    require(certified is not None, "`certification.tuples` has no item schema")
    assert certified is not None
    require(
        certified.get("additionalProperties") is False,
        "a certified tuple does not close its property set, so a dimension nothing "
        "checks can be added to one side alone",
    )
    dimension_heads = {
        d.manifest.split(".")[2].removesuffix("[]")
        for d in TUPLE_DIMENSIONS.values()
        if d.manifest and d.manifest.startswith(f"{TUPLE_LIST}.")
    }
    record_heads = {
        path.split(".")[2]
        for path, _ in RECORD_BINDING.values()
        if path.startswith(f"{TUPLE_LIST}.")
    }
    extra = sorted(
        set(certified.get("properties") or {}) - dimension_heads - record_heads
    )
    require(
        not extra,
        f"a certified tuple carries {extra}, which is neither a dimension of "
        "compatibility-tuple-v1.schema.json nor a bound field of the certification row",
    )


def check_the_ceiling_rule_is_in_both(manifest: dict, body: str) -> None:
    """`check (state = 'active' or effective_ceiling = 'private-analytics')`.

    The constraint lived in the DDL alone. The artifact every adapter author writes could
    not state it, which is what let SR-009 say a registry may imply exercised support.
    """
    require(
        "check (state = 'active' or effective_ceiling = 'private-analytics')" in body,
        f"{TABLE} no longer refuses a non-active certification above private analytics. "
        "That constraint is what stops a planned, expired or suspended tuple competing, "
        "and the manifest rule below is derived from it",
    )
    declared = sql_check_values(body, "effective_ceiling")
    require(
        set(declared) == set(CEILING_PROJECTION.values()),
        f"{TABLE}.effective_ceiling admits {declared}, which is not the image of the "
        "manifest's three evidence classes under CEILING_PROJECTION",
    )
    ceiling = manifest_node(manifest, f"{TUPLE_LIST}.max_public_profile")
    require(
        ceiling is not None,
        f"a certified tuple carries no `max_public_profile`, so the DDL's "
        "private-analytics rule has no field in the manifest to apply to",
    )
    assert ceiling is not None
    require(
        set(ceiling.get("enum") or []) == set(CEILING_PROJECTION),
        f"the certified tuple's ceiling admits {sorted(ceiling.get('enum') or [])}, "
        f"which is not the domain of CEILING_PROJECTION",
    )
    manifest_wide = manifest_node(manifest, "capability_ceiling.max_public_profile")
    require(
        manifest_wide is not None
        and set(manifest_wide.get("enum") or []) == set(CEILING_PROJECTION),
        "capability_ceiling.max_public_profile and the certified tuple's ceiling no "
        "longer share one vocabulary, which would make the manifest disagree with "
        "itself about what a ceiling is",
    )

    rules = manifest["properties"]["certification"].get("allOf") or []
    pinned = [
        rule
        for rule in rules
        if rule.get("if", {})
        .get("properties", {})
        .get("state", {})
        .get("not", {})
        .get("const")
        == "active"
        and rule.get("then", {})
        .get("properties", {})
        .get("tuples", {})
        .get("items", {})
        .get("properties", {})
        .get("max_public_profile", {})
        .get("const")
        == "private-analytics"
    ]
    require(
        len(pinned) == 1,
        "adapter-manifest.schema.json does not pin every tuple of a non-active "
        "certification to `private-analytics`. The DDL makes that pairing "
        "unrepresentable; a manifest that only describes it is a rule somebody has to "
        "remember to apply",
    )


def check_the_state_binding_is_intact(manifest: dict) -> None:
    """PF-071's null binding, extended to the two fields that joined it.

    A null bundle digest, a null suite version, an empty tuple list and `uncertified` are
    one fact. Admitting any of them on its own converts a representation gap into a
    permission - and an empty tuple list under a named state is the cross product coming
    back as an absence rather than as a product.
    """
    rules = manifest["properties"]["certification"].get("allOf") or []
    bound = [
        rule
        for rule in rules
        if rule.get("if", {}).get("properties", {}).get("state", {}).get("const")
        == "uncertified"
    ]
    require(
        len(bound) == 1,
        "the certification block no longer binds `uncertified` to anything in a single "
        "if/then/else",
    )
    rule = bound[0]
    for branch, expected in (
        (
            "then",
            {
                "bundle_sha256": {"type": "null"},
                "suite_version": {"type": "null"},
                "tuples": {"maxItems": 0},
            },
        ),
        (
            "else",
            {
                "bundle_sha256": {"type": "string"},
                "suite_version": {"type": "string"},
                "tuples": {"minItems": 1},
            },
        ),
    ):
        actual = (rule.get(branch) or {}).get("properties") or {}
        require(
            actual == expected,
            f"the `uncertified` binding's `{branch}` branch is {actual} rather than "
            f"{expected}. Both directions have to fail, or the pair is satisfiable by "
            "an implementer picking whichever half is convenient",
        )

    live = manifest.get("$defs", {}).get("live_tuple")
    require(
        isinstance(live, dict),
        "there is no `live_tuple` shape, so the DDL's `(state = 'active') = (valid_from "
        "is not null and revoked_at is null and superseded is null)` equivalence has no "
        "counterpart and an active certification may carry a revoked tuple",
    )
    equivalence = [
        r
        for r in rules
        if r.get("if", {}).get("properties", {}).get("state", {}).get("const")
        == "active"
        and "then" in r
        and "else" in r
    ]
    require(
        len(equivalence) == 1,
        "the active-state rule is not stated as an equivalence, so one direction of the "
        "DDL constraint is unenforced",
    )


def check_the_active_equivalence_is_in_the_ddl(body: str) -> None:
    require(
        "check ((state = 'active') = (valid_from is not null and revoked_at is null "
        "and superseded_by_source_certification_id is null))" in body,
        f"{TABLE} no longer states the active equivalence the manifest's `live_tuple` "
        "shape is derived from; the derivation is stale and would keep passing against "
        "a rule the DDL has stopped making",
    )
    require(
        "tuple_digest bytea not null unique" in body,
        f"{TABLE}.tuple_digest is no longer a unique non-null column. It is the reason "
        f"{sum(1 for d in TUPLE_DIMENSIONS.values() if d.sql is None and d.manifest)} "
        "dimensions have no column of their own: without it the row names a tuple it "
        "cannot identify, and two different tuples can occupy one certification",
    )


def check_nothing_here_is_certified(example: dict) -> None:
    """`ADAPTER_CERTIFICATION_POLICY.md`: every tuple this repository can reach is
    `candidate`. A committed example that says otherwise is a certification claim made
    by a fixture."""
    certification = example.get("certification") or {}
    state = certification.get("state")
    require(
        state in ("uncertified", "candidate"),
        f"the committed adapter manifest example declares certification state {state!r}. "
        "ADAPTER_CERTIFICATION_POLICY.md states that every tuple this repository can "
        "reach is `candidate`: no conformance suite has been run against any exact "
        "tuple, no result bundle has been signed, and no row in source_certifications "
        "has ever left the initial state. A fixture is not the place that changes",
    )
    if state == "uncertified":
        require(
            certification.get("bundle_sha256") is None
            and certification.get("suite_version") is None
            and certification.get("tuples") == [],
            "the committed example declares itself uncertified and carries a bundle "
            "digest, a suite version or a tuple. An uncertified manifest has none of "
            "the three, which is why none of them had to be invented here",
        )


def check_the_example_enumerates_only_declared_tuples(
    example: dict, profile_ids: set[str]
) -> int:
    """Containment, which is what replaced the product.

    Vacuous on the committed example, because an uncertified manifest enumerates no
    tuple. It is not vacuous on any manifest that ever certifies anything, and the drift
    tests exercise it against one.
    """
    tuples = (example.get("certification") or {}).get("tuples") or []
    digests: set[str] = set()
    for index, entry in enumerate(tuples):
        digest = entry.get("tuple_digest")
        require(
            digest not in digests,
            f"certification.tuples[{index}] repeats tuple digest {digest}; two entries "
            "with one identity are one tuple counted twice",
        )
        digests.add(digest)
        for name, array in COVERAGE_ARRAYS.items():
            node: object = entry
            for token in name.split("."):
                node = (node or {}).get(token) if isinstance(node, dict) else None
            declared = example.get(array) or []
            require(
                node in declared,
                f"certification.tuples[{index}] names {name}={node!r}, which "
                f"`{array}` does not declare. A certification may only name a "
                "combination the adapter declares it reaches",
            )
        profile = entry.get("platform_profile_id")
        require(
            profile in profile_ids,
            f"certification.tuples[{index}] names platform profile {profile!r}, which "
            "platform-profile-registry-v1.json does not declare. A profile fixes the "
            "key-protection class and the supervision mechanism the evidence ceiling "
            "depends on; an unregistered one fixes nothing",
        )
    return len(tuples)


def check_the_documents_still_say_this(policy: str, compatibility: str) -> None:
    """Every derivation above reads these sentences. If they change, this is stale."""
    for phrase in (
        "Every tuple this repository can reach is `candidate`.",
        "Only `active` may exceed `private-analytics`.",
    ):
        require(
            phrase in policy,
            f"ADAPTER_CERTIFICATION_POLICY.md no longer states {phrase!r}",
        )
    for phrase in (
        "`packages/schemas/compatibility-tuple-v1.schema.json` is its machine-readable form",
        "A certification of one tuple says nothing about any other.",
    ):
        require(
            phrase in compatibility,
            f"UNIVERSAL_AGENT_COMPATIBILITY.md no longer states {phrase!r}",
        )


def main() -> int:
    manifest = load_json(MANIFEST)
    tuple_schema = load_json(TUPLE)
    example = load_json(EXAMPLE)
    tables = sql_table_bodies(SQL.read_text(encoding="utf-8"))
    require(TABLE in tables, f"planning-schema.sql declares no {TABLE} table")
    body = tables[TABLE]
    columns = set(sql_columns(body))
    profile_ids = {p["profile_id"] for p in load_json(PROFILES)["profiles"]}

    # Ordered so the specific diagnosis wins. The cross product and the point version are
    # what this unit exists to remove, so they are named before the generic field-set
    # comparisons that would otherwise report them as a shape mismatch.
    check_the_dimension_table_is_the_tuple_authority(tuple_schema)
    check_the_cross_product_is_unrepresentable(manifest)
    check_the_version_range_replaced_the_point_version(manifest)
    check_every_dimension_reaches_the_manifest(manifest, tuple_schema)
    check_every_dimension_reaches_the_certification_row(columns)
    check_the_reasons_have_not_outlived_their_holes(columns)
    check_the_certification_row_holds_nothing_unaccounted(columns)
    check_the_record_fields_bind(manifest, columns)
    check_the_ceiling_rule_is_in_both(manifest, body)
    check_the_active_equivalence_is_in_the_ddl(body)
    check_the_state_binding_is_intact(manifest)
    check_nothing_here_is_certified(example)
    enumerated = check_the_example_enumerates_only_declared_tuples(example, profile_ids)
    check_the_documents_still_say_this(
        POLICY.read_text(encoding="utf-8"), COMPATIBILITY.read_text(encoding="utf-8")
    )

    columned = sum(1 for d in TUPLE_DIMENSIONS.values() if d.sql)
    by_digest = sum(1 for d in TUPLE_DIMENSIONS.values() if d.sql is None)
    absent = sum(1 for d in TUPLE_DIMENSIONS.values() if d.manifest is None)
    product = 1
    for array in ("source_products", "platforms", "modes", "accounting_profile_ids"):
        product *= len(example.get(array) or [])
    print("adapter certification tuple binding: pass")
    print(
        f"tuple={len(TUPLE_DIMENSIONS)} dimensions three-way, {columned} columned in "
        f"{TABLE}, {by_digest} bound by tuple_digest with a recorded reason, {absent} "
        "absent from the manifest with a recorded reason"
    )
    print(
        f"record={len(RECORD_BINDING)} certification fields bound, "
        f"{len(RECORD_ONLY_COLUMNS)} server-only columns each with a reason, "
        f"{len(CEILING_PROJECTION)} evidence classes projected"
    )
    print(
        f"coverage={enumerated} enumerated tuple(s) against a {product}-combination "
        "declared cross product; the arrays declare reach and the list is the whole of "
        "the certification"
    )
    print(
        f"certified=none; the committed example is "
        f"{example['certification']['state']} and no state above `candidate` is "
        "reachable in this repository, which is what ADAPTER_CERTIFICATION_POLICY.md "
        "says is true"
    )
    print(
        "claim_scope=artifact-agreement-only; three agreeing artifacts are not a "
        "certified adapter, no conformance suite has been run against any tuple, and no "
        "implementation reads any of them"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failure as failure:
        print(
            f"adapter certification tuple binding: FAIL — {failure}",
            file=sys.stderr,
        )
        sys.exit(1)
