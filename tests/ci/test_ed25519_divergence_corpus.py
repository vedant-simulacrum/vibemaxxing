"""Tests for the Ed25519 divergence corpus and its generator.

The corpus exists because citing RFC 8032 does not pin Ed25519 verification.
These tests hold the four properties that make it worth committing:

* the two verification rules it implements are genuinely different functions,
  not the same one written out twice under two names;
* RFC 8032's own test vectors cannot separate them, which is the claim the
  corpus is built on and is asserted here executably rather than in prose;
* every recorded ZIP-215 verdict is either confirmed against an independent
  ZIP-215 implementation or marked `unconfirmed`, and the generator refuses to
  write a corpus whose oracle contradicts it;
* the file is reproducible from its recorded inputs, so a hand-edited verdict
  fails rather than persists.

Nothing here needs Go or a network: the oracle's answers are a committed
record, and these tests check that the corpus agrees with that record. Refreshing
the record is `scripts/repository/run_ed25519_oracles.py`, which does need Go.
"""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts" / "repository" / "generate_ed25519_divergence_corpus.py"
CORPUS = ROOT / "conformance" / "vibeproof" / "v1" / "ed25519-divergence-corpus.json"
ORACLE_RUN = ROOT / "conformance" / "vibeproof" / "v1" / "zip215-oracle-run.json"

REQUIRED_AXES = {
    "non-canonical-A",
    "non-canonical-R",
    "small-order-A",
    "S-not-less-than-l",
}

# RFC 8032 Section 7.1, TEST 1. Present to be shown insufficient.
RFC8032_PUBLIC = bytes.fromhex(
    "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
)
RFC8032_SIGNATURE = bytes.fromhex(
    "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555f"
    "b8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
)
RFC8032_MESSAGE = b""


@functools.cache
def load_generator():
    """Loaded once: the generator memoises derivations and reloading discards them."""
    specification = importlib.util.spec_from_file_location(
        "generate_ed25519_divergence_corpus", GENERATOR
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class CurveDerivationTests(unittest.TestCase):
    """The constants are derived here, so the derivations are what get tested."""

    def setUp(self) -> None:
        self.generator = load_generator()

    def test_base_point_has_order_l(self) -> None:
        self.assertEqual(
            self.generator.point_mul(self.generator.BASE, self.generator.L),
            self.generator.IDENTITY,
        )

    def test_eight_torsion_is_a_group_of_the_expected_shape(self) -> None:
        points = self.generator.eight_torsion()
        self.assertEqual(len(points), 8)
        self.assertEqual(len({point for point in points}), 8, "points must be distinct")
        orders = sorted(self.generator.torsion_order(point) for point in points)
        # One identity, one point of order 2, two of order 4, four of order 8:
        # the subgroup structure of Z/8Z, which is what the cofactor is.
        self.assertEqual(orders, [1, 2, 4, 4, 8, 8, 8, 8])

    def test_torsion_points_are_annihilated_by_the_cofactor(self) -> None:
        """The single fact every accepting divergence case is built on."""
        for point in self.generator.eight_torsion():
            self.assertEqual(
                self.generator.point_mul(point, self.generator.COFACTOR),
                self.generator.IDENTITY,
            )

    def test_non_canonical_curve_points_are_exactly_the_enumerated_set(self) -> None:
        found = self.generator.non_canonical_curve_points()
        for entry in found:
            encoded = bytes.fromhex(entry["encoding_hex"])
            self.assertFalse(
                self.generator.is_canonical_encoding(encoded),
                "an enumerated non-canonical encoding must not be canonical",
            )
            self.assertIsNotNone(
                self.generator.decode_point(encoded),
                "an enumerated encoding must decode under the ZIP-215 rule",
            )
            self.assertIsNone(
                self.generator.decode_point_canonical(encoded),
                "and must not decode under the strict RFC 8032 rule",
            )
        # Only the 19 residues 0..18 have a second encoding, and both signs are
        # candidates, so the set can never exceed 38 whatever the curve does.
        self.assertLessEqual(len(found), 38)
        self.assertTrue(
            any(entry["point_class"] == "mixed-order" for entry in found),
            "the non-canonical set must contain a point outside the 8-torsion, "
            "or the corpus cannot separate non-canonical from small-order",
        )


class VerificationRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = load_generator()

    def test_rfc8032_test_vector_one_passes_under_both_criteria(self) -> None:
        """The reason this corpus exists, stated as a test rather than a claim.

        RFC 8032's own vectors are well-formed signatures. They pass under the
        cofactored rule and under the cofactorless one, so no number of them
        can tell the two apart, and a suite built from them proves nothing
        about the axis where conforming implementations disagree.
        """
        zip215, _ = self.generator.verify_zip215(
            RFC8032_PUBLIC,
            RFC8032_SIGNATURE[:32],
            RFC8032_SIGNATURE[32:],
            RFC8032_MESSAGE,
        )
        classic, _ = self.generator.verify_cofactorless(
            RFC8032_PUBLIC,
            RFC8032_SIGNATURE[:32],
            RFC8032_SIGNATURE[32:],
            RFC8032_MESSAGE,
        )
        self.assertTrue(zip215)
        self.assertTrue(classic)

    def test_a_tampered_signature_fails_under_both_criteria(self) -> None:
        """Neither verifier is a function that returns True."""
        tampered = bytearray(RFC8032_SIGNATURE)
        tampered[32] ^= 0x01
        for verify in (
            self.generator.verify_zip215,
            self.generator.verify_cofactorless,
        ):
            accepted, _ = verify(
                RFC8032_PUBLIC,
                bytes(tampered[:32]),
                bytes(tampered[32:]),
                RFC8032_MESSAGE,
            )
            self.assertFalse(accepted)

    def test_the_two_rules_are_different_functions(self) -> None:
        """At least one input where they disagree, or the corpus is decorative."""
        document = json.loads(CORPUS.read_text(encoding="utf-8"))
        disagreements = [
            case
            for case in document["cases"]
            if case["divergence"]["against_strict_rfc8032"]
        ]
        self.assertTrue(disagreements, "no case separates the two criteria")

    def test_s_at_least_l_is_refused_by_both(self) -> None:
        """ZIP-215 is not uniformly more permissive; the S range is where it is not."""
        document = json.loads(CORPUS.read_text(encoding="utf-8"))
        cases = [
            case for case in document["cases"] if case["axis"] == "S-not-less-than-l"
        ]
        self.assertTrue(cases)
        for case in cases:
            self.assertFalse(case["decoded"]["s_less_than_l"])
            self.assertEqual(case["zip215"]["verdict"], "reject")
            self.assertEqual(case["cofactorless"]["verdict"], "reject")


class CorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = load_generator()
        self.document = json.loads(CORPUS.read_text(encoding="utf-8"))

    def test_corpus_is_reproducible_from_its_recorded_inputs(self) -> None:
        self.assertEqual(
            self.generator.regenerate(),
            CORPUS.read_text(encoding="utf-8"),
            "the committed corpus differs from a regeneration; run the generator",
        )

    def test_generation_is_deterministic(self) -> None:
        self.assertEqual(self.generator.regenerate(), self.generator.regenerate())

    def test_every_required_axis_is_covered(self) -> None:
        axes = {case["axis"] for case in self.document["cases"]}
        self.assertTrue(
            REQUIRED_AXES.issubset(axes), f"missing: {REQUIRED_AXES - axes}"
        )

    def test_case_identifiers_are_unique(self) -> None:
        identifiers = [case["id"] for case in self.document["cases"]]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_case_digests_bind_the_bytes_they_claim_to(self) -> None:
        """Recomputed here, so a digest edited to match a stale confirmation fails."""
        message = bytes.fromhex(self.document["inputs"]["message_hex"])
        for case in self.document["cases"]:
            signature = bytes.fromhex(case["signature_hex"])
            material = b"|".join(
                (
                    case["id"].encode("ascii"),
                    bytes.fromhex(case["public_key_hex"]),
                    signature[:32],
                    signature[32:],
                    message,
                )
            )
            self.assertEqual(
                case["case_digest"], hashlib.sha256(material).hexdigest(), case["id"]
            )

    def test_recorded_verdicts_match_the_rules_this_generator_implements(self) -> None:
        message = bytes.fromhex(self.document["inputs"]["message_hex"])
        for case in self.document["cases"]:
            public_key = bytes.fromhex(case["public_key_hex"])
            signature = bytes.fromhex(case["signature_hex"])
            zip215, _ = self.generator.verify_zip215(
                public_key, signature[:32], signature[32:], message
            )
            classic, _ = self.generator.verify_cofactorless(
                public_key, signature[:32], signature[32:], message
            )
            self.assertEqual(
                case["zip215"]["verdict"], "accept" if zip215 else "reject"
            )
            self.assertEqual(
                case["cofactorless"]["verdict"], "accept" if classic else "reject"
            )

    def test_every_verdict_is_either_confirmed_or_says_how_to_confirm_it(self) -> None:
        """The honesty property. An unconfirmed verdict is allowed; a silent one is not."""
        for case in self.document["cases"]:
            confirmation = case["zip215"]["confirmation"]
            self.assertIn(confirmation["status"], {"confirmed", "unconfirmed"})
            if confirmation["status"] == "confirmed":
                self.assertTrue(confirmation["confirmed_by"])
                self.assertEqual(
                    confirmation["oracle_verdict"], case["zip215"]["verdict"]
                )
            else:
                self.assertTrue(
                    confirmation["confirmation_path"],
                    "an unconfirmed verdict must say what would confirm it",
                )

    def test_confirmations_resolve_against_the_committed_oracle_run(self) -> None:
        run = json.loads(ORACLE_RUN.read_text(encoding="utf-8"))
        results = {entry["case_id"]: entry for entry in run["results"]}
        for case in self.document["cases"]:
            confirmation = case["zip215"]["confirmation"]
            if confirmation["status"] != "confirmed":
                continue
            entry = results.get(case["id"])
            self.assertIsNotNone(
                entry, f"{case['id']} claims confirmation with no result"
            )
            self.assertEqual(entry["case_digest"], case["case_digest"])
            self.assertEqual(entry["zip215_verdict"], case["zip215"]["verdict"])
            self.assertEqual(entry["oracle_id"], confirmation["confirmed_by"])

    def test_the_oracle_is_not_this_generator(self) -> None:
        """A second opinion from the same code is not a second opinion."""
        run = json.loads(ORACLE_RUN.read_text(encoding="utf-8"))
        self.assertNotIn(
            "generate_ed25519_divergence_corpus", run["zip215_oracle"]["id"]
        )
        self.assertTrue(run["zip215_oracle"]["version"])
        self.assertTrue(run["zip215_oracle"]["go_sum_h1"].startswith("h1:"))

    def test_the_contrast_oracles_are_never_recorded_as_zip215(self) -> None:
        """python-cryptography is libsodium-like, not ZIP-215, and must not pass as one."""
        run = json.loads(ORACLE_RUN.read_text(encoding="utf-8"))
        contrast = {oracle["id"] for oracle in run["contrast_oracles"]}
        self.assertNotIn(run["zip215_oracle"]["id"], contrast)
        for entry in run["results"]:
            recorded = {
                observation["implementation"]
                for observation in entry["cofactorless_observations"]
            }
            self.assertNotIn(run["zip215_oracle"]["id"], recorded)

    def test_a_measured_verifier_disagrees_with_zip215_somewhere(self) -> None:
        """The corpus's whole purpose, measured rather than argued.

        A divergence only from the strict text would leave open that no shipping
        implementation is actually cofactorless. At least one case must be one
        where a real library that was run returns the other answer.
        """
        measured = [
            case
            for case in self.document["cases"]
            if case["divergence"]["against_observed_cofactorless"]
        ]
        self.assertTrue(
            measured,
            "no case is one a real cofactorless implementation actually disagreed with",
        )

    def test_the_generator_refuses_a_corpus_its_oracle_contradicts(self) -> None:
        """The property that makes `confirmed` mean something."""
        case = self.generator.build_cases()[0]
        digest = self.generator.case_digest(case)
        contradicting = {
            case["id"]: {
                "case_id": case["id"],
                "case_digest": digest,
                "oracle_id": "fabricated",
                # The control case verifies, so `reject` is a contradiction.
                "zip215_verdict": "reject",
                "cofactorless_observations": [],
            }
        }
        with self.assertRaises(SystemExit):
            self.generator.render_case(case, contradicting)

    def test_the_corpus_states_what_it_is_not_evidence_of(self) -> None:
        self.assertTrue(self.document["not_evidence_of"])
        self.assertEqual(self.document["evidence_ceiling"], "fixture-consistent")


if __name__ == "__main__":
    unittest.main()
