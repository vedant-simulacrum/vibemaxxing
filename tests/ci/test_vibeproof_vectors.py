"""Tests for the deterministic VibeProof vector generator.

The generator exists so the signed corpus is reproducible rather than
hand-maintained. These tests prove the two properties that makes worth having:
the canonical encoder implements RFC 8949 Core Deterministic Encoding rather
than the length-first ordering it is easily confused with, and the Sig_structure
builder produces the four-element COSE_Sign1 construction of RFC 9052 s4.4.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts" / "repository" / "generate_vibeproof_vectors.py"
VECTORS = ROOT / "conformance" / "vibeproof" / "v1" / "exact-byte-vectors.json"


def load_generator():
    specification = importlib.util.spec_from_file_location(
        "generate_vibeproof_vectors", GENERATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class CanonicalEncoderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = load_generator()

    def test_arguments_use_the_shortest_legal_form(self) -> None:
        """RFC 8949 s4.2.1 preferred serialization: 1 is 0x01, never 0x1801."""
        self.assertEqual(self.generator.encode(1), bytes.fromhex("01"))
        self.assertEqual(self.generator.encode(23), bytes.fromhex("17"))
        self.assertEqual(self.generator.encode(24), bytes.fromhex("1818"))
        self.assertEqual(self.generator.encode(256), bytes.fromhex("190100"))

    def test_negative_integers_encode_as_major_type_one(self) -> None:
        # -19 is the Ed25519 algorithm identifier: -(18 + 1), so argument 18.
        self.assertEqual(self.generator.encode(-19), bytes.fromhex("32"))
        self.assertEqual(self.generator.encode(-8), bytes.fromhex("27"))

    def test_map_ordering_is_core_deterministic_not_length_first(self) -> None:
        """The distinction that silently breaks COSE interoperability.

        RFC 8949 s4.2.1 sorts by the bytewise order of the encoded key with no
        length preference; s4.2.3 sorts shorter encodings first. The spec's own
        example separates them: Core gives 10, 100, -1; length-first gives
        10, -1, 100. RFC 9052 s9 binds COSE to Core.
        """
        encoded = self.generator.encode({10: 0, 100: 0, -1: 0})
        core_order = [
            self.generator.encode(10),
            self.generator.encode(100),
            self.generator.encode(-1),
        ]
        length_first_order = [
            self.generator.encode(10),
            self.generator.encode(-1),
            self.generator.encode(100),
        ]
        self.assertNotEqual(
            core_order, length_first_order, "the fixture must separate the two rules"
        )
        body = encoded[1:]
        self.assertEqual(
            body,
            b"".join(key + self.generator.encode(0) for key in core_order),
            "map keys must sort by bytewise order of the encoded key",
        )

    def test_duplicate_map_labels_are_rejected_on_decode(self) -> None:
        """RFC 9052 s9 forbids parsing a message with the same label twice.

        This is the direction that matters: most CBOR libraries silently
        last-write-wins on decode, so a message carrying a label twice is
        accepted and one of the two values disappears without a trace.
        """
        # map(2) with label 1 repeated: {1: 0, 1: 0}
        duplicated = bytes.fromhex("a2" + "0100" + "0100")
        with self.assertRaises(ValueError):
            self.generator.decode_map_at(duplicated, 0)

    def test_distinct_labels_decode_normally(self) -> None:
        decoded, _ = self.generator.decode_map_at(
            bytes.fromhex("a2" + "0100" + "0200"), 0
        )
        self.assertEqual(decoded, {1: 0, 2: 0})

    def test_floats_are_refused(self) -> None:
        """RFC 8949 s4.2.2 leaves float determinism to the protocol; ours bans it."""
        with self.assertRaises(TypeError):
            self.generator.encode(1.5)

    def test_false_is_refused_and_true_and_nil_are_not(self) -> None:
        """`29: true` and three `X / nil` labels are declared by the grammar.

        The encoder refused all three until the vectors were checked against the CDDL,
        which never surfaced because the committed payload hex was copied rather than
        re-encoded from a decoded instance. `false` stays unencodable: a claim that did
        not pass the privacy boundary is never serialized, so it has no encoding rather
        than a discouraged one.
        """
        self.assertEqual(self.generator.encode(True), bytes.fromhex("f5"))
        self.assertEqual(self.generator.encode(None), bytes.fromhex("f6"))
        with self.assertRaises(TypeError):
            self.generator.encode(False)

    def test_round_trip_through_the_decoder(self) -> None:
        original = {1: -19, 3: "application/x+cbor", 4: b"\x00" * 16, 1001: 1}
        decoded, consumed = self.generator.decode_map_at(
            self.generator.encode(original), 0
        )
        self.assertEqual(decoded, original)
        self.assertEqual(consumed, len(self.generator.encode(original)))


class SigStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = load_generator()

    def test_signature1_has_four_elements(self) -> None:
        """RFC 9052 s4.4: COSE_Sign1 omits the signer-protected field entirely.

        Emitting a five-element array with an empty slot for it is a common
        error that produces a valid signature over the wrong bytes.
        """
        structure = self.generator.sig_structure(b"\xa0", b"aad", b"payload")
        self.assertEqual(structure[0], 0x84, "must be a definite-length array of 4")
        wrong = self.generator.encode(["Signature1", b"\xa0", b"", b"aad", b"payload"])
        self.assertNotEqual(structure, wrong)

    def test_external_aad_is_present_even_when_empty(self) -> None:
        structure = self.generator.sig_structure(b"\xa0", b"", b"payload")
        self.assertEqual(structure[0], 0x84)
        self.assertIn(b"Signature1", structure)


class CommittedVectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = load_generator()

    def test_committed_vectors_are_reproducible(self) -> None:
        self.assertEqual(
            self.generator.regenerate(),
            VECTORS.read_text(encoding="utf-8"),
            "the committed vectors differ from a regeneration; run the generator",
        )

    def test_generation_is_deterministic(self) -> None:
        self.assertEqual(self.generator.regenerate(), self.generator.regenerate())

    def test_committed_vectors_carry_the_fully_specified_algorithm(self) -> None:
        """RFC 9864 deprecates the polymorphic EdDSA identifier -8."""
        document = json.loads(VECTORS.read_text(encoding="utf-8"))
        for kind in ("claim", "receipt"):
            protected = bytes.fromhex(document[kind]["protected_headers_hex"])
            headers, _ = self.generator.decode_map_at(protected, 0)
            self.assertEqual(headers[1], -19, f"{kind} must declare alg Ed25519")

    def test_committed_sig_structures_are_correctly_constructed(self) -> None:
        """Not merely signed over — actually built from their own inputs."""
        document = json.loads(VECTORS.read_text(encoding="utf-8"))
        external_aad = bytes.fromhex(document["external_aad_hex"])
        for kind in ("claim", "receipt"):
            vector = document[kind]
            expected = self.generator.sig_structure(
                bytes.fromhex(vector["protected_headers_hex"]),
                external_aad,
                bytes.fromhex(vector["canonical_payload_hex"]),
            )
            self.assertEqual(bytes.fromhex(vector["sig_structure_hex"]), expected)


if __name__ == "__main__":
    unittest.main()
