"""One tuple has one identity, whatever order it was serialised in.

`compatibility-tuple-v1.schema.json` states that a tuple's digest is SHA-256 over the
RFC 8949 core deterministic CBOR encoding of the record with `tuple_digest` omitted,
"so two implementations cannot disagree about the identity of a tuple". Nothing proved
it, and the unit's own note recorded that the digest half had not landed.

It matters because the tuple is what "exact certified tuple" means everywhere in the
product. A reader that preserved insertion order would produce two digests for one
tuple — and a certification is looked up by digest, so a re-serialised tuple would
miss its own certification and either be refused or, worse, be certified twice under
two identities.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
SCHEMA = ROOT / "packages" / "schemas" / "compatibility-tuple-v1.schema.json"
FIXTURE = ROOT / "conformance" / "adapters" / "compatibility-tuple-digest-v1.json"


def load_module():
    specification = importlib.util.spec_from_file_location(
        "validate_planning_artifacts", VALIDATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def digest(module, record: dict) -> str:
    body = {key: value for key, value in record.items() if key != "tuple_digest"}
    return hashlib.sha256(module.canonical_cbor(body)).hexdigest()


class TupleDigestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.orderings = self.fixture["orderings"]

    def test_the_fixture_records_two_genuinely_different_orderings(self) -> None:
        """A fixture whose two orderings are identical proves nothing."""
        first, second = (o["tuple"] for o in self.orderings)

        self.assertEqual(set(first), set(second))
        self.assertNotEqual(list(first), list(second))

    def test_both_orderings_produce_the_recorded_digest(self) -> None:
        for ordering in self.orderings:
            self.assertEqual(
                digest(self.module, ordering["tuple"]),
                self.fixture["expected_digest"],
                ordering["ordering_id"],
            )

    def test_nested_maps_are_reordered_too(self) -> None:
        """Top-level-only reordering would leave the harder case untested."""
        first, second = (o["tuple"] for o in self.orderings)
        nested = [
            key
            for key in first
            if isinstance(first[key], dict) and len(first[key]) > 1
        ]
        self.assertTrue(nested)
        reordered = [key for key in nested if list(first[key]) != list(second[key])]
        self.assertTrue(reordered, "no nested map was reordered")

    def test_changing_one_component_changes_the_identity(self) -> None:
        """Atomic means atomic: one dimension differs, it is a different tuple."""
        base = json.loads(json.dumps(self.orderings[0]["tuple"]))
        for path in (
            ("observation_mode",),
            ("platform_profile_id",),
            ("source", "version_min"),
            ("accounting", "arithmetic_sha256"),
            ("privacy_binding", "strip_list_sha256"),
        ):
            mutated = json.loads(json.dumps(base))
            target = mutated
            for key in path[:-1]:
                target = target[key]
            current = target[path[-1]]
            target[path[-1]] = "f" * 64 if len(current) == 64 else current + "-changed"

            self.assertNotEqual(
                digest(self.module, mutated),
                self.fixture["expected_digest"],
                ".".join(path),
            )

    def test_each_ordering_validates_against_the_tuple_schema(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        for ordering in self.orderings:
            record = json.loads(json.dumps(ordering["tuple"]))
            record["tuple_digest"] = self.fixture["expected_digest"]
            jsonschema.validate(
                {"schema_version": 1, "tuple": record}, schema
            )

    def test_the_encoder_refuses_a_float(self) -> None:
        """RFC 8949 4.2.2 leaves float determinism to the protocol; D-193 declines."""
        with self.assertRaises(self.module.ValidationFailure):
            self.module.canonical_cbor({"value": 1.5})


if __name__ == "__main__":
    unittest.main()
