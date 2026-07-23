# VibeProof v1 Protocol Contract

Status: normative P-1140C planning contract; no production codec or interoperability claim
Version: 1
Updated: 2026-07-24

## Authority and artifacts

`packages/schemas/vibeproof-claim-v1.cddl` owns every protocol-v1 payload and integer label. This document owns canonical encoding, COSE, limits and state transitions. `conformance/vibeproof/v1/` owns exact planning vectors and malformed/resource cases.

P-1140B remains immutable input: a device signs facts and commitments only; the server owns appraisal, public evidence, ranking eligibility, pricing and corrections. No extension map or client-selected evidence/pricing field exists.

## Canonical CBOR

All signed payloads use RFC 8949 deterministic encoding with these stricter rules:

- definite lengths only;
- shortest integer and length encodings;
- map keys sorted by encoded-key length, then bytewise lexical order;
- no floats, simple values other than false/true/null, duplicate keys, undefined values, indefinite strings/arrays/maps or unregistered tags;
- only integer map labels listed in CDDL;
- UUIDv7 is exactly 16 raw bytes; SHA-256 is exactly 32 bytes; Ed25519 signatures are exactly 64 bytes;
- unsigned counts/sequences/durations are bounded to u64; timestamps are unsigned epoch milliseconds at most 253402300799999;
- registered semantic IDs are u32 registry numbers, never free text;
- a decoder rejects trailing bytes and verifies that re-encoding produces byte-identical input before signature/policy processing.

Limits are checked before allocation: one signed claim 16 KiB; atomic batch 256 claims and 1 MiB; depth 12; 64 map entries; text constant/identifier 128 UTF-8 bytes; byte string 64 KiB except the bounded outer batch; total parser allocation at most four times encoded bytes plus 64 KiB fixed overhead.

## COSE_Sign1 profile

Outer tag 18 is mandatory. The value is exactly `[protected, {}, payload, signature]`; the unprotected map is empty. Protected headers are:

- label 1 = -8 (EdDSA);
- label 3 = exact registered claim or receipt content-type string;
- label 4 = 16-byte key UUID (`kid`);
- label 1001 = protocol major 1.

Security-relevant unprotected headers, alternate algorithms, missing/extra protected headers and non-byte `kid` values reject. Ed25519 COSE_Key uses `{1:1, 2:kid, 3:-8, -1:6, -2:x}`, with 32-byte public `x`. Private keys never serialize.

External AAD is the exact ASCII bytes `VIBEMAXXING/VIBEPROOF/V1`. Sig_structure is deterministic CBOR `["Signature1", protected_bstr, external_aad, payload_bstr]`. Verification uses the received protected and payload bytes after canonical precheck; decoders never reconstruct a different semantic object for signature verification.

## Claim and checkpoint continuity

A lineage has separate local and server state:

- local state: next claim sequence, previous/current local commitment heads and queued claims;
- server state: expected sequence, accepted local head, last accepted claim digest, prior checkpoint receipt and monotonic receipt sequence.

A challenge binds account pseudonym, lineage, nonce, expected sequence/head/checkpoint, expiry and maximum batch. It proves upload freshness only. Offline events are committed into the local chain before reconnect; a later challenge does not prove they existed earlier. Their eligibility is bounded by the exact P-1140B delayed-sync and continuity policy.

A successful atomic batch advances server state from the challenge's expected tuple to the final claim tuple and returns server-signed checkpoint receipt(s). A receipt acknowledges only the bound accepted head. A sequence/head/checkpoint mismatch, fork, rollback or concurrently valid successor quarantines the lineage.

## Atomic submission and idempotency

The authenticated request body is binary `application/vibemaxxing-claim-batch+cbor`. One transaction:

1. enforces encoded/body/allocation limits;
2. canonical-decodes the batch and each COSE message;
3. authenticates account/lineage and locks its verifier state;
4. resolves the idempotency key plus exact request SHA-256;
5. verifies challenge ownership, expiry, expected tuple and single use;
6. verifies every signature, key status, artifact/profile digest, numeric/time/accounting/privacy invariant and duplicate commitment;
7. creates all claim facts and appraisals, consumes the challenge, advances checkpoint state, creates receipts/outbox rows and stores exact response bytes;
8. commits all or none.

Byte-identical retry under the same principal/route/key returns stored response bytes. Reuse with different bytes, or conflicting claim ID, sequence, challenge, commitment, checkpoint or duplicate domain, is a conflict and never partial success. Per-claim diagnostics explain an atomic result; they do not imply partial commit.

## Rotation, recovery and gaps

Routine rotation uses one canonical transition payload signed independently by both old and new keys; payload bytes must match. The server verifies recent authentication, old-key state, new-key uniqueness and checkpoint binding in one transaction.

Lost-key recovery cannot forge the old signature. It revokes the old lineage/key path, creates recovery authorization, resets continuity or starts a new lineage, and requires requalification. Restored or cloned successors quarantine until resolved.

A GapDeclaration represents missing locally committed sequence material; it never fabricates counts. It binds before/after sequences and heads, registered cause and local audit commitment. Policy may reject, quarantine or lower continuity. It cannot independently restore Hardened.

## Appraisals and corrections

`VerifierAppraisal` is immutable and server-owned. It binds claim digest, verifier policy/implementation, independent evidence dimensions, public profile, ranking eligibility, reasons, anomaly disposition, evaluated certification/policy digests and re-evaluation trigger.

Accepted claim bytes never mutate. A server-authorized `CorrectionRecord` binds the exact claim and appraisal, action, reasons and authorizing action digest. Reversal appends another correction referencing the prior correction and emits inverse ranking/projection events under P-1140D.

## Conformance

The fixed Ed25519 vectors include canonical payload, protected bytes, external AAD, Sig_structure, signature and COSE bytes for one claim and one receipt. The private seed is test-only.

Malformed/resource cases cover duplicate keys, non-minimal integers, indefinite containers, floats, unknown tags, unprotected security headers, wrong algorithm/content type/kid, trailing bytes, deep nesting, oversized strings/claims/batches, allocation ratio, mutation, replay, sequence fork, checkpoint mismatch, dual-rotation mismatch and conflicting idempotency reuse.

These planning vectors prove deterministic artifact agreement only. P-1140E requires independent Rust/Go implementations and clean cross-contract results; no current runtime implementation exists.
