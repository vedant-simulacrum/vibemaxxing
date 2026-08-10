# ADR-007: Batch Challenge and Sequence Recovery

Status: accepted
Date: 2026-07-19

## Decision

A claim challenge authorizes exactly one atomic batch for one account and device. It contains a random 256-bit nonce, expiry, maximum claim count, and maximum encoded bytes. Every claim in the batch signs the same batch challenge nonce plus its own batch ID, zero-based index, total count, sequence, and previous-claim hash.

The server accepts or rejects the batch atomically. It verifies all claims and locks the device sequence head before inserting any claim. An exact replay of an already accepted complete batch returns idempotent success. Mixed replay/new batches, missing indices, duplicate indices, changed order, sequence gaps, invalid signatures, or any invalid claim reject the complete batch. Retryable infrastructure failure consumes neither the challenge nor sequence state.

A challenge is consumed only when the full batch commits. A challenge cannot authorize multiple batches. Single-claim submission is a batch of one.

## Sequence gaps

Normal operation requires contiguous sequences. The only recoverable gap mechanism is a signed `gap-declaration` included in the first claim after the gap. It identifies the first and last missing sequence, a registered reason, a local audit commitment, and declaration time.

Allowed reasons are local corruption, acknowledged-state loss, interrupted migration, and key recovery. The maximum recoverable gap is 10,000 sequences. A gap declaration never restores Hardened continuity automatically. The device is downgraded to Standard and placed in review. A larger gap, conflicting chain, or unexplained gap requires device revocation and re-enrollment.

The server records the declaration, advances the sequence head only in the same atomic transaction as the first post-gap claim, and exposes the continuity break in the local audit and user-facing evidence history. Missing claims never contribute score.

## Recovery

Lost unacknowledged local claims may be resent only when their exact bytes and sequence chain remain available. If local state cannot reproduce the chain, the client must declare a bounded gap or revoke and re-enroll. It must never fabricate placeholder claims.

## Consequences

- `vibeproof-claim-v1.cddl`, OpenAPI, SQL planning DDL, reason codes, and conformance cases must match this ADR.
- Partial batch acceptance is prohibited in protocol v1.
- Future partial-acceptance support requires a protocol-major ADR and migration plan.

## Where this ADR is enforced

The consequence above states an acceptance test for this document and nothing checked it for the length of the planning program. `grep -n "ADR-007\|ClaimChallenge\|batch_commitment\|atomic-batch-result" scripts/repository/*.py` returned nothing, and five divergences of D-043's size survived a green `doctor.py` as a result. `scripts/repository/validate_batch_challenge_binding.py` now reads this file and compares it to the schemas, so the sentences below are load-bearing rather than descriptive; changing one of them without changing what it governs fails.

| This ADR says | Where it is now checkable |
| --- | --- |
| A challenge contains a nonce, expiry, maximum claim count and maximum encoded bytes | `challenge-v1`, `claim_challenges` and `ClaimChallenge` carry the same eleven fields, compared field for field |
| Every claim signs its own batch ID, zero-based index and total count | `vibeproof-claim-v1` labels 31, 32 and 33, whose ranges are derived from the `batch-context` occurrence bound rather than restated |
| Missing indices, duplicate indices, changed order reject the batch | `claims` mirrors the signed labels under `unique (batch_id, batch_index)`, so the three cases are answerable from stored signed material |
| A challenge cannot authorize multiple batches | `unique (consumed_by_batch_id)` on `claim_challenges` |
| Partial batch acceptance is prohibited | `atomic-batch-result-v1` is a two-way choice a mixed instance satisfies neither arm of, `ClaimBatchResult` carries a `oneOf`, and `claims` and `claim_rejections` reference `claim_batches (batch_id, outcome)` at disjoint outcome sets |
| A signed `gap-declaration` included in the first claim after the gap | `cose-sign1-gap-v1` with `protected-headers-gap-v1`; the digest is `vibeproof-claim-v1` label 34 and the envelope travels in `batch-context` label 5 |
| Allowed reasons are four | `gap-declaration` label 7 is `0..3` and `gap_declarations.cause` enumerates the four names this document uses, parsed from the sentence above |
| The maximum recoverable gap is 10,000 sequences | A CHECK constraint on `gap_declarations`, and `max_recoverable_gap_sequences` in `policy-defaults-v1.json`. The bound is a relation between two sequence numbers and CDDL constrains each label independently, so the grammar cannot hold it |

Two points of wording, recorded rather than left for a reader to resolve. This document identifies a gap by "the first and last missing sequence" and `gap-declaration` binds the sequences either side of it; they are the same statement one apart, and the pair either side also states which local heads the chain jumps between. And `vibeproof-claim-v1.cddl` carries no `batch_commitment`: the API required one on both the challenge request and the challenge response, and it is removed under D-626 rather than propagated, because every claim in a batch signs the challenge nonce and a digest of the batch therefore cannot be computed before the challenge that binds it exists.
