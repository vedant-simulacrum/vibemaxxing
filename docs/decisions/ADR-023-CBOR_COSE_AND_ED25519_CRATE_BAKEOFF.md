# ADR-023 — CBOR, COSE and Ed25519 crate bakeoff

Status: accepted (candidate set and criteria); selection deferred
Date: 2026-08-09
Decision: D-012, constrained by D-011, D-090, D-183, D-192, D-342

## Context

D-012 records that the final Rust CBOR/COSE crates are selected during an implementation bakeoff behind an internal boundary, and it has sat `research-required` with the reopen condition "malformed, fuzz, differential and resource tests pass". Those tests need running code. No CBOR or COSE crate is a dependency of anything in this repository today, and the one workspace member, `crates/vibeproof-core`, is a quarantined non-protocol prototype.

So the decision has two halves and only one of them is closeable now. The candidate set, the disqualifications and the criteria are research, and research can be finished by reading. The selection is evidence, and evidence needs a `vibeproof-codec` crate that does not exist.

This ADR fixes the half that can be fixed, so the bakeoff starts from a narrowed field rather than from the whole registry.

## Requirements this must satisfy

From `VIBEPROOF_V1_CANONICAL_PROFILE.md` and `packages/schemas/vibeproof-claim-v1.cddl`:

1. RFC 8949 core deterministic encoding on the write path.
2. **Rejection of non-canonical input on the read path.** This is the requirement that eliminates most candidates. A decoder that accepts an indefinite-length item, a non-minimal integer, a duplicate map key or an out-of-order map key cannot support the negative corpus PF-054 exists to author, because there is nothing to assert against.
3. COSE_Sign1 with caller control over the exact `Sig_structure` bytes, and preservation of the received protected-header bytes rather than a re-encoding of them.
4. Cofactored Ed25519 verification per D-192.

## Disqualified, with reasons

- **`serde_cbor` 0.11.2.** Repository archived in 2022; RUSTSEC-2021-0127 marks it unmaintained with no patched version; still targets RFC 7049 rather than RFC 8949. Disqualified on maintenance alone.
- **`aws-nitro-enclaves-cose` 0.5.2.** Transitively disqualified: its manifest requires `serde_cbor = "0.11"`.
- **`ed25519-dalek`, for the verifier role only.** Its `verify` and `verify_strict` recompute `R'` and compare bytes, which is the cofactorless rule D-192 rejects. Its ZIP-215 support is confined to point decoding in `VerifyingKey::from_bytes`. It remains suitable for signing.

A disqualification is a research result. Three of them narrow the bakeoff before it starts.

## Candidate set

| Role | Candidates | Note |
|---|---|---|
| CBOR | `minicbor` 2.3.0, `dcbor` 0.25.2 | `ciborium` 0.2.2 as substrate only — its sole canonical helper implements RFC 8949 §4.2.3 length-first ordering, which the profile forbids, and its README states it is deliberately "liberal in what we accept". `cbor4ii` 1.2.2 as fallback. |
| COSE | `coset` 0.4.2, or a hand-written COSE_Sign1 over the chosen codec | `coset` exposes `sig_structure_data`, a 4-element Sign1 structure, and `ProtectedHeader::original_data` preserving received bytes. |
| Ed25519 verify | Rust `ed25519-zebra` 4.2.0; Go `ed25519consensus` v0.2.0 or `curve25519-voi` | The only Rust crate meeting all three D-192 criteria. |

Two candidates need a measurement rather than a reading: `minicbor` and `cbor4ii` both accept non-minimal integers today, so requirement 2 is not satisfied by either without a wrapper, and how much wrapper is the question the bakeoff answers.

## Constraint the bakeoff must not trip over

`ed25519-zebra` 4.2.0 pins `curve25519-dalek >=4.0, <4.2`; `ed25519-dalek` 3.0 requires `curve25519-dalek` 5.x. Using `ed25519-dalek` for signing and `ed25519-zebra` for verification therefore puts two major versions of the curve library in one binary. Either accept that, or sign with `ed25519-zebra` too.

## What remains missing

D-012 stays `research-required`. Its reopen condition names four test classes and none can run:

- **malformed and resource** — need a `vibeproof-codec` crate with a candidate wired in;
- **differential** — needs two candidates wired in simultaneously;
- **fuzz** — needs a fuzz target, and the phase rule forbids activating fuzz workflows in CI, so this criterion collides with the phase and the collision is the owner's to resolve rather than an agent's to route around.

The evidence is produced by the first unit that authors `vibeproof-codec` against this candidate set. Until then the honest state of D-012 is: field narrowed, three candidates eliminated, selection not made.

## Consequences

- The bakeoff starts from four CBOR candidates rather than the registry, with two already known to fail requirement 2 unwrapped.
- `VIBEPROOF_V1_PROTOCOL.md` is corrected: it claimed Rust satisfied the cofactored requirement via an `ed25519-dalek` ZIP-215 verification mode that does not exist, which made Rust look exempt from a constraint D-192 states in language-neutral terms.
- Nothing here is implementation evidence. An accepted candidate set is a narrowed field, not a working codec.
