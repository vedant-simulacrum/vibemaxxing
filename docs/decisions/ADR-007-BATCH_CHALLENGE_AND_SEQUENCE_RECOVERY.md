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
