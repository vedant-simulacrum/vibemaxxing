#!/usr/bin/env python3
"""Regenerate conformance/vibeproof/v1/exact-byte-vectors.json deterministically.

The vectors are signed fixtures. Hand-editing their hex is how a corpus drifts
from the profile it claims to encode, so they are generated here instead, from
the recorded private seed, and the result is byte-reproducible: running this
twice produces identical output, and running it without changing an input
produces a file identical to the committed one.

Canonical encoding follows RFC 8949 Section 4.2.1 Core Deterministic Encoding,
which is what RFC 9052 Section 9 binds COSE to. That is *not* the length-first
ordering of Section 4.2.3 (the older RFC 7049 "Canonical CBOR"), which several
libraries still default to and which produces different bytes for the same map.
The encoder below implements Core, and `encode_map` documents the difference.

Usage:
    generate_vibeproof_vectors.py            # rewrite the vectors in place
    generate_vibeproof_vectors.py --check    # exit 1 if the committed file differs
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

ROOT = Path(__file__).resolve().parents[2]
VECTORS = ROOT / "conformance" / "vibeproof" / "v1" / "exact-byte-vectors.json"

# RFC 9864 replaces the polymorphic EdDSA identifier (-8) with fully-specified
# Ed25519 (-19). -8 required information beyond the algorithm identifier to
# determine the operation, which is exactly what a cross-language conformance
# corpus cannot tolerate.
ALG_ED25519 = -19

COSE_SIGN1_TAG = 18
CONTEXT_SIGNATURE1 = "Signature1"

# Every way the decoder below refuses an input, as stable symbols. The negative
# corpus names one of these per byte-level case and
# `validate_vibeproof_negative_corpus` requires the decoder to raise exactly that
# one, so a case cannot claim to test a malformation its bytes do not contain.
# The set is enumerated here rather than inferred, so a refusal the corpus never
# exercises is visible as a gap instead of being invisible.
PROFILE_VIOLATIONS = frozenset(
    {
        "duplicate-key",
        "float",
        "indefinite-length",
        "non-minimal-integer",
        "reserved",
        "simple-value",
        "tag",
        "trailing-bytes",
        "truncated",
    }
)


class ProfileViolation(ValueError):
    """An input the VibeProof canonical profile refuses, tagged with which rule."""

    def __init__(self, symbol: str, detail: str) -> None:
        if symbol not in PROFILE_VIOLATIONS:
            raise AssertionError(f"undeclared profile violation symbol: {symbol}")
        super().__init__(f"{symbol}: {detail}")
        self.symbol = symbol


# --- minimal deterministic CBOR ------------------------------------------------


def encode_head(major: int, argument: int) -> bytes:
    """Encode an initial byte plus its argument in the shortest legal form.

    RFC 8949 Section 4.2.1 requires preferred serialization: the argument is
    encoded in the fewest bytes that hold it, so 1 is 0x01 and never 0x1801.
    """
    prefix = major << 5
    if argument < 24:
        return bytes([prefix | argument])
    for additional, width in ((24, 1), (25, 2), (26, 4), (27, 8)):
        if argument < 1 << (8 * width):
            return bytes([prefix | additional]) + argument.to_bytes(width, "big")
    raise ValueError(f"argument out of range: {argument}")


def encode(value: object) -> bytes:
    if value is None:
        # `nil` is a declared value in the grammar: three claim labels are
        # `X / nil`. It was unencodable here only because the committed payload hex
        # was never re-encoded from a decoded instance.
        return bytes([0xF6])
    if isinstance(value, bool):  # before int; bool is an int subclass
        if value is not True:
            # `29: true` is the whole privacy_pass field. A claim that did not pass
            # the privacy boundary is never serialized, so `false` has no encoding
            # rather than a discouraged one.
            raise TypeError("the VibeProof profile never serializes false")
        return bytes([0xF5])
    if isinstance(value, int):
        if value >= 0:
            return encode_head(0, value)
        return encode_head(1, -value - 1)
    if isinstance(value, bytes):
        return encode_head(2, len(value)) + value
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return encode_head(3, len(encoded)) + encoded
    if isinstance(value, list):
        return encode_head(4, len(value)) + b"".join(encode(item) for item in value)
    if isinstance(value, dict):
        return encode_map(value)
    if isinstance(value, float):
        # Section 4.2.2 hands float determinism to the protocol - signed zero,
        # integral values, NaN payloads and subnormals are all left open. The
        # profile bans floats rather than choosing, so aggregates are integers
        # with a fixed scale and no encoder disagreement is possible.
        raise TypeError("the VibeProof profile bans floats; use scaled integers")
    raise TypeError(f"unencodable type: {type(value).__name__}")


def encode_map(value: dict) -> bytes:
    """Encode a map with Core Deterministic key ordering.

    RFC 8949 Section 4.2.1: keys sort by the bytewise lexicographic order of
    their *encoded* form, with no length preference. Section 4.2.3's length-first
    ordering sorts shorter encodings first instead, and the two disagree whenever
    keys differ in encoded length - the spec's own example orders 10, 100, -1
    under Core and 10, -1, false, 100 under length-first. RFC 9052 Section 9
    binds COSE to Core, so a length-first encoder silently produces a different
    signature over the same claim.
    """
    items = [(encode(key), encode(item)) for key, item in value.items()]
    if len({key for key, _ in items}) != len(items):
        raise ValueError("duplicate map key; RFC 9052 Section 9 forbids it")
    items.sort(key=lambda pair: pair[0])
    return encode_head(5, len(items)) + b"".join(key + item for key, item in items)


def decode_map_at(data: bytes, offset: int) -> tuple[Any, int]:
    """Decode the profile's CBOR subset, starting at `offset`.

    The name says "map" because reading a protected-header map back is what it was
    written for. It now decodes claim and receipt payloads too, which carry an array
    of reason codes and the simple values `true` and `nil`, so the committed bytes
    can be checked against the CDDL rather than only against their own signature.

    Everything outside the profile is refused rather than accommodated: indefinite
    lengths, floats, `undefined`, and any tag. A decoder that quietly accepts what
    the profile forbids cannot be used to prove a fixture obeys it.
    """
    if offset >= len(data):
        raise ProfileViolation("truncated", f"no initial byte at offset {offset}")
    initial = data[offset]
    major, additional = initial >> 5, initial & 0x1F
    offset += 1
    if additional == 31:
        raise ProfileViolation(
            "indefinite-length", f"indefinite-length item at offset {offset - 1}"
        )
    if 28 <= additional <= 30:
        raise ProfileViolation(
            "reserved", f"reserved additional information {additional}"
        )
    if major == 7:
        if additional in {25, 26, 27}:
            raise ProfileViolation("float", "the VibeProof profile bans floats")
        simple = {20: False, 21: True, 22: None}
        if additional not in simple:
            raise ProfileViolation("simple-value", f"simple value {additional}")
        return simple[additional], offset
    if additional < 24:
        argument = additional
    else:
        width = {24: 1, 25: 2, 26: 4, 27: 8}[additional]
        if offset + width > len(data):
            raise ProfileViolation(
                "truncated", f"argument runs past the end at offset {offset}"
            )
        argument = int.from_bytes(data[offset : offset + width], "big")
        offset += width
        # RFC 8949 s4.2.1 preferred serialization. Accepting 0x1817 as 23 is how a
        # decoder admits two encodings of one value, which is two different signed
        # byte strings for one claim.
        if argument < (24 if width == 1 else 1 << (8 * (width // 2))):
            raise ProfileViolation(
                "non-minimal-integer",
                f"argument {argument} is not in its shortest form",
            )
    if major == 6:
        # The profile permits exactly one tag, 18, and only as the outermost
        # COSE_Sign1 wrapper. Payloads and header maps carry none, so any tag
        # reached here is forbidden regardless of its number.
        raise ProfileViolation("tag", f"tag {argument} at offset {offset - 1}")
    if major == 4:
        items = []
        for _ in range(argument):
            item, offset = decode_map_at(data, offset)
            items.append(item)
        return items, offset
    if major == 0:
        return argument, offset
    if major == 1:
        return -argument - 1, offset
    if major in {2, 3}:
        if offset + argument > len(data):
            raise ProfileViolation(
                "truncated", f"string of {argument} bytes runs past the end"
            )
        chunk = data[offset : offset + argument]
        return (chunk if major == 2 else chunk.decode("utf-8")), offset + argument
    if major == 5:
        result = {}
        for _ in range(argument):
            key, offset = decode_map_at(data, offset)
            item, offset = decode_map_at(data, offset)
            if key in result:
                # RFC 9052 s9: applications MUST NOT parse and process a message
                # with the same label twice. Most CBOR libraries silently
                # last-write-wins here, which is why this has to be explicit.
                raise ProfileViolation(
                    "duplicate-key", f"duplicate map label on decode: {key!r}"
                )
            result[key] = item
        return result, offset
    raise AssertionError(f"unreachable major type {major}")


def decode_exact(data: bytes) -> Any:
    """Decode one profile item and require it to consume every byte.

    Trailing bytes after a complete item are the classic smuggling primitive: a
    verifier that hashes the whole buffer and a verifier that decodes the first
    item disagree about what was signed.
    """
    value, consumed = decode_map_at(data, 0)
    if consumed != len(data):
        raise ProfileViolation(
            "trailing-bytes", f"{len(data) - consumed} bytes after a complete item"
        )
    return value


# --- vector construction -------------------------------------------------------


def sig_structure(protected: bytes, external_aad: bytes, payload: bytes) -> bytes:
    """Build the COSE_Sign1 Sig_structure of RFC 9052 Section 4.4.

    Four elements, not five: COSE_Sign1 omits the signer-protected field
    entirely rather than carrying an empty slot for it. `external_aad` is
    always present even when zero-length, and `payload` is the actual bytes
    even when the message carries a detached (nil) payload.
    """
    return encode([CONTEXT_SIGNATURE1, protected, external_aad, payload])


def build(kind: str, source: dict, seed: bytes, external_aad: bytes) -> dict:
    previous = bytes.fromhex(source["protected_headers_hex"])
    headers, consumed = decode_map_at(previous, 0)
    if consumed != len(previous):
        raise ValueError(f"{kind}: trailing bytes in protected headers")
    headers[1] = ALG_ED25519

    protected = encode(headers)
    payload = bytes.fromhex(source["canonical_payload_hex"])
    to_be_signed = sig_structure(protected, external_aad, payload)
    signature = Ed25519PrivateKey.from_private_bytes(seed).sign(to_be_signed)

    # COSE_Sign1 is tag 18 over [protected, unprotected, payload, signature].
    # The unprotected bucket stays an empty map; note that an *absent* protected
    # bucket would be a zero-length bstr (0x40), never a bstr wrapping an empty
    # map (0x41a0) - a distinction that changes the bytes being signed.
    body = encode([protected, {}, payload, signature])
    cose = encode_head(6, COSE_SIGN1_TAG) + body

    return {
        "canonical_payload_hex": payload.hex(),
        "canonical_payload_sha256": hashlib.sha256(payload).hexdigest(),
        "protected_headers_hex": protected.hex(),
        "sig_structure_hex": to_be_signed.hex(),
        "signature_hex": signature.hex(),
        "cose_sign1_hex": cose.hex(),
        "cose_sign1_sha256": hashlib.sha256(cose).hexdigest(),
        "encoded_bytes": len(cose),
    }


def regenerate() -> str:
    document = json.loads(VECTORS.read_text(encoding="utf-8"))
    seed = bytes.fromhex(document["private_seed_hex"])
    external_aad = bytes.fromhex(document["external_aad_hex"])

    derived = (
        Ed25519PrivateKey.from_private_bytes(seed)
        .public_key()
        .public_bytes(Encoding.Raw, PublicFormat.Raw)
    )
    if derived.hex() != document["public_key_hex"]:
        raise SystemExit("recorded public key does not derive from the recorded seed")

    for kind in ("claim", "receipt"):
        document[kind] = build(kind, document[kind], seed, external_aad)

    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the committed vectors differ from a regeneration",
    )
    arguments = parser.parse_args(argv)

    generated = regenerate()
    if arguments.check:
        if VECTORS.read_text(encoding="utf-8") != generated:
            print(
                "exact-byte vectors are not reproducible from the recorded seed; "
                "run generate_vibeproof_vectors.py",
                file=sys.stderr,
            )
            return 1
        print("exact-byte vectors: reproducible")
        return 0

    VECTORS.write_text(generated, encoding="utf-8")
    print(f"wrote {VECTORS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
