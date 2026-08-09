"""Tests for CDDL rule ownership, the CBOR instance check, and the negative corpus.

Every test here exists because the property it covers was previously unenforced.
`validate_cddl_file` proved the grammar parsed and that named rules existed; nothing
compared a committed byte to a rule, nothing decoded the negative corpus, and nothing
stopped a third file from claiming the same wire format. So each test mutates the tree
into the defect and requires a failure — a check that has never been observed failing
is indistinguishable from one that cannot.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "repository" / "validate_planning_artifacts.py"
CDDL_INSTANCE = ROOT / "scripts" / "repository" / "cddl_instance.py"
GENERATOR = ROOT / "scripts" / "repository" / "generate_vibeproof_vectors.py"

IGNORED = shutil.ignore_patterns(
    ".git", ".venv", "node_modules", "target", "__pycache__", "assets", "artifacts"
)


def load(path: Path, name: str) -> object:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class CddlInstanceTests(unittest.TestCase):
    """The subset checker, on its own, without the repository around it."""

    def setUp(self) -> None:
        self.cddl = load(CDDL_INSTANCE, "cddl_instance")
        self.bodies = self.cddl.rule_bodies(
            (ROOT / "packages" / "schemas" / "vibeproof-claim-v1.cddl").read_text()
        )

    def test_comments_are_not_read_as_references(self) -> None:
        """`token-categories` comments its fields; none of them is a rule name, and a
        scanner that kept the comments would report dependencies the grammar lacks."""
        stripped = self.cddl.strip_comments("uuid7 = bytes .size 16 ; digest32 here\n")
        self.assertNotIn("digest32", stripped)

    def test_a_content_type_literal_is_not_split_on_its_slash(self) -> None:
        # "application/vibemaxxing-claim+cbor" holds a slash. Treating it as a type
        # alternative tore the constant in half and reported the fragment as unknown.
        self.cddl.check(
            '"application/vibemaxxing-claim+cbor"',
            "application/vibemaxxing-claim+cbor",
            self.bodies,
        )
        with self.assertRaises(self.cddl.CddlMismatch):
            self.cddl.check(
                '"application/vibemaxxing-claim+cbor"', "application", self.bodies
            )

    def test_maps_are_closed_in_both_directions(self) -> None:
        """The grammar's preamble says unlisted integer labels are invalid, so a
        checker that only required the declared labels to be present would accept an
        instance carrying extra ones."""
        entries = self.cddl.map_entries(self.bodies["token-categories"])
        valid = {label: 0 for label in entries}
        self.cddl.check("token-categories", valid, self.bodies)

        missing = dict(valid)
        missing.pop(6)
        with self.assertRaises(self.cddl.CddlMismatch) as caught:
            self.cddl.check("token-categories", missing, self.bodies)
        self.assertIn("missing=[6]", str(caught.exception))

        extra = dict(valid)
        extra[7] = 0
        with self.assertRaises(self.cddl.CddlMismatch) as caught:
            self.cddl.check("token-categories", extra, self.bodies)
        self.assertIn("undeclared=[7]", str(caught.exception))

    def test_byte_sizes_and_ranges_are_exact(self) -> None:
        self.cddl.check("digest32", b"\x00" * 32, self.bodies)
        with self.assertRaises(self.cddl.CddlMismatch):
            self.cddl.check("digest32", b"\x00" * 31, self.bodies)
        with self.assertRaises(self.cddl.CddlMismatch):
            self.cddl.check("uint32", -1, self.bodies)
        with self.assertRaises(self.cddl.CddlMismatch):
            self.cddl.check("uint32", True, self.bodies)

    def test_nil_alternatives_accept_both_arms_and_nothing_else(self) -> None:
        self.cddl.check("uuid7 / nil", None, self.bodies)
        self.cddl.check("uuid7 / nil", b"\x00" * 16, self.bodies)
        with self.assertRaises(self.cddl.CddlMismatch):
            self.cddl.check("uuid7 / nil", b"\x00" * 15, self.bodies)

    def test_array_occurrence_bounds_are_enforced(self) -> None:
        self.cddl.check("[* reason-code]", [1, 2], self.bodies)
        self.cddl.check("[1*256 reason-code]", [1], self.bodies)
        with self.assertRaises(self.cddl.CddlMismatch):
            self.cddl.check("[1*256 reason-code]", [], self.bodies)
        with self.assertRaises(self.cddl.CddlMismatch):
            self.cddl.check("[1*2 reason-code]", [1, 2, 3], self.bodies)

    def test_an_unimplemented_construct_raises_rather_than_passing(self) -> None:
        """A checker that skips what it does not understand reports the same green as
        one that checked."""
        with self.assertRaises(self.cddl.CddlUnsupported):
            self.cddl.check("#6.18([bstr])", [b""], self.bodies)


class ForeignDeclarationTests(unittest.TestCase):
    """The third-file rule, and the substring trap it must not fall into."""

    def setUp(self) -> None:
        self.validator = load(VALIDATOR, "validate_planning_artifacts")
        self.cddl = load(CDDL_INSTANCE, "cddl_instance")
        self.rules = set(
            self.cddl.rule_bodies(
                (ROOT / "packages" / "schemas" / "vibeproof-claim-v1.cddl").read_text()
            )
        )

    def test_a_third_file_declaring_a_rule_is_refused(self) -> None:
        offences = self.validator.vibeproof_foreign_declarations(
            self.rules,
            {
                "conformance/vibeproof/v1/negative-vectors.json": {
                    "cases": [{"rule": "gap-declaration"}]
                }
            },
        )
        self.assertEqual(len(offences), 1)
        self.assertIn("gap-declaration", offences[0])

    def test_a_third_file_claiming_ownership_is_refused(self) -> None:
        offences = self.validator.vibeproof_foreign_declarations(
            self.rules, {"conformance/protocol/shadow.json": {"cddl_rules_pinned": []}}
        )
        self.assertEqual(len(offences), 1)
        self.assertIn("cddl_rules_pinned", offences[0])

    def test_a_path_containing_a_rule_name_is_not_a_declaration(self) -> None:
        """`manifest.json` points at `packages/schemas/vibeproof-claim-v1.cddl` and at
        `packages/schemas/reason-codes-v1.json`. Both contain a rule name. A substring
        rule would fail on the file that names the authority, which teaches the next
        author to weaken the check rather than to fix a defect."""
        self.assertEqual(
            self.validator.vibeproof_foreign_declarations(
                self.rules,
                {
                    "conformance/vibeproof/v1/manifest.json": {
                        "authority_ref": "packages/schemas/vibeproof-claim-v1.cddl",
                        "reason_authority": "packages/schemas/reason-codes-v1.json",
                    }
                },
            ),
            [],
        )

    def test_the_committed_tree_declares_no_rule_outside_the_two_vector_files(
        self,
    ) -> None:
        self.assertEqual(
            self.validator.vibeproof_foreign_declarations(
                self.rules, self.validator._vibeproof_candidate_documents()
            ),
            [],
        )


class RuleOwnershipTests(unittest.TestCase):
    """Whole-stage tests over a mutated copy of the tree."""

    def setUp(self) -> None:
        self.validator = load(VALIDATOR, "validate_planning_artifacts")
        self.generator = load(GENERATOR, "generate_vibeproof_vectors")
        parent = Path(tempfile.mkdtemp(prefix="vibeproof-ownership-"))
        self.addCleanup(shutil.rmtree, parent, True)
        self.root = parent / "repository"
        for relative in ("conformance", "packages", "docs", "evals", "scripts"):
            shutil.copytree(
                ROOT / relative, self.root / relative, ignore=IGNORED, symlinks=True
            )
        self.validator.ROOT = self.root
        self.validator.SCHEMAS = self.root / "packages" / "schemas"
        self.validator.CONFORMANCE = self.root / "conformance"

    @property
    def vectors_path(self) -> Path:
        return self.validator.vibeproof_vector_path()

    @property
    def corpus_path(self) -> Path:
        return self.validator.vibeproof_corpus_path()

    def read(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, path: Path, document: dict) -> None:
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def assert_ownership_fails(self, fragment: str) -> None:
        with self.assertRaises(Exception) as caught:
            self.validator.validate_vibeproof_rule_ownership()
        self.assertIn(fragment, str(caught.exception))

    def assert_corpus_fails(self, fragment: str) -> None:
        with self.assertRaises(Exception) as caught:
            self.validator.validate_vibeproof_negative_corpus()
        self.assertIn(fragment, str(caught.exception))

    def test_the_committed_tree_passes_both_stages(self) -> None:
        self.validator.validate_vibeproof_rule_ownership()
        self.validator.validate_vibeproof_negative_corpus()

    def test_a_rule_owned_by_nobody_fails(self) -> None:
        cddl = self.root / "packages" / "schemas" / "vibeproof-claim-v1.cddl"
        cddl.write_text(
            cddl.read_text(encoding="utf-8") + "\nfuture-record-v1 = { 0: 1 }\n",
            encoding="utf-8",
        )
        self.assert_ownership_fails("owned by no vector file: ['future-record-v1']")

    def test_a_rule_owned_twice_fails(self) -> None:
        corpus = self.read(self.corpus_path)
        corpus["cddl_rules_pinned"].append("digest32")
        self.write(self.corpus_path, corpus)
        self.assert_ownership_fails("claimed by both")

    def test_pinning_a_rule_the_grammar_does_not_declare_fails(self) -> None:
        corpus = self.read(self.corpus_path)
        corpus["cddl_rules_pinned"].append("invented-rule-v1")
        self.write(self.corpus_path, corpus)
        self.assert_ownership_fails("rules the CDDL does not declare")

    def test_the_vectors_must_pin_exactly_their_reference_closure(self) -> None:
        vectors = self.read(self.vectors_path)
        vectors["cddl_rules_pinned"].remove("nonce32")
        corpus = self.read(self.corpus_path)
        corpus["cddl_rules_pinned"].append("nonce32")
        self.write(self.vectors_path, vectors)
        self.write(self.corpus_path, corpus)
        self.assert_ownership_fails("reference closure")

    def test_a_pinned_rule_no_case_exercises_fails(self) -> None:
        corpus = self.read(self.corpus_path)
        for case in corpus["cases"]:
            if case.get("cddl_rule") == "gap-declaration":
                del case["cddl_rule"]
        self.write(self.corpus_path, corpus)
        self.assert_ownership_fails("pins rules no case exercises")

    def test_an_unpinned_rule_that_gained_a_case_fails(self) -> None:
        """A justification that outlives the hole it explained is a stale excuse."""
        corpus = self.read(self.corpus_path)
        corpus["cases"][-1]["cddl_rule"] = "challenge-v1"
        self.write(self.corpus_path, corpus)
        self.assert_ownership_fails("name rules the corpus does not pin")

    def test_an_unpinned_rule_must_defer_to_a_real_work_unit(self) -> None:
        corpus = self.read(self.corpus_path)
        corpus["cddl_rules_unpinned"][0]["work_unit"] = "P-999"
        self.write(self.corpus_path, corpus)
        self.assert_ownership_fails("which has no work-unit block")

    def test_a_payload_label_the_grammar_does_not_declare_fails(self) -> None:
        """The check the repository did not have. The committed vectors could encode
        any label set, sign it correctly, reproduce from the recorded seed, and pass."""
        vectors = self.read(self.vectors_path)
        payload = self.generator.decode_exact(
            bytes.fromhex(vectors["claim"]["canonical_payload_hex"])
        )
        payload[31] = 0
        vectors["claim"]["canonical_payload_hex"] = self.generator.encode(payload).hex()
        self.write(self.vectors_path, vectors)
        self.assert_ownership_fails("undeclared=[31]")

    def test_a_payload_value_of_the_wrong_width_fails(self) -> None:
        vectors = self.read(self.vectors_path)
        payload = self.generator.decode_exact(
            bytes.fromhex(vectors["claim"]["canonical_payload_hex"])
        )
        payload[3] = b"\x00" * 31  # account_pseudonym is digest32
        vectors["claim"]["canonical_payload_hex"] = self.generator.encode(payload).hex()
        self.write(self.vectors_path, vectors)
        self.assert_ownership_fails("expected 32 bytes")

    def test_an_envelope_that_does_not_carry_the_fixture_bytes_fails(self) -> None:
        vectors = self.read(self.vectors_path)
        envelope = bytearray(bytes.fromhex(vectors["claim"]["cose_sign1_hex"]))
        envelope[-1] ^= 0x01
        vectors["claim"]["cose_sign1_hex"] = bytes(envelope).hex()
        self.write(self.vectors_path, vectors)
        self.assert_ownership_fails("envelope signature bytes differ")

    # -- negative corpus ---------------------------------------------------------

    def test_a_case_whose_bytes_decode_cleanly_fails(self) -> None:
        corpus = self.read(self.corpus_path)
        corpus["cases"][0]["input_hex"] = "a10001"
        self.write(self.corpus_path, corpus)
        self.assert_corpus_fails("decoder accepted this input")

    def test_a_case_declaring_the_wrong_malformation_fails(self) -> None:
        """`duplicate-map-key` says duplicate-key. Give it indefinite-length bytes and
        it still fails to decode, which is exactly why "it raised" is not enough."""
        corpus = self.read(self.corpus_path)
        corpus["cases"][0]["input_hex"] = "bf0001ff"
        self.write(self.corpus_path, corpus)
        self.assert_corpus_fails("refused it as indefinite-length")

    def test_a_reason_code_that_does_not_resolve_fails(self) -> None:
        corpus = self.read(self.corpus_path)
        corpus["cases"][0]["registry_reason_code"] = "CLAIM_INVENTED_CODE"
        self.write(self.corpus_path, corpus)
        self.assert_corpus_fails("does not resolve in")

    def test_a_case_stating_its_input_two_ways_fails(self) -> None:
        corpus = self.read(self.corpus_path)
        corpus["cases"][0]["mutation"] = "also a mutation"
        self.write(self.corpus_path, corpus)
        self.assert_corpus_fails("exactly one way")

    def test_a_prose_case_may_not_claim_a_decoder_signal(self) -> None:
        corpus = self.read(self.corpus_path)
        corpus["cases"][-1]["decoder_signal"] = "duplicate-key"
        self.write(self.corpus_path, corpus)
        self.assert_corpus_fails("no bytes to decode")

    def test_dropping_a_covered_refusal_fails(self) -> None:
        corpus = self.read(self.corpus_path)
        corpus["cases"] = [
            case
            for case in corpus["cases"]
            if case.get("decoder_signal") != "trailing-bytes"
        ]
        self.write(self.corpus_path, corpus)
        self.assert_corpus_fails("refuses inputs no corpus case exercises")

    def test_every_refusal_the_profile_can_produce_is_exercised(self) -> None:
        corpus = self.read(self.corpus_path)
        covered = {
            case["decoder_signal"]
            for case in corpus["cases"]
            if "decoder_signal" in case
        }
        self.assertEqual(covered, set(self.generator.PROFILE_VIOLATIONS))


if __name__ == "__main__":
    unittest.main()
