# Adapter and VibeProof Implementation Contract

Status: normative planning contract
Version: 1

## Adapter registry

Each adapter manifest is signed and contains: `adapter_id`, semantic version, maintainer, source agent IDs/versions, supported platforms/modes, capture mechanism, required permissions, token categories, model-identity quality, source authority, evidence ceiling, privacy risks, duplicate domains, capability probe, conformance suite version, emergency-disable status, and sunset date.

Lifecycle: `experimental -> community-certified -> competitive-certified -> hardened-certified`; any state may transition to `degraded`, `suspended`, `retired`, or `unsupported`.

Unknown source versions fail closed for Hardened evidence and downgrade to the highest exercised compatible tier for Standard evidence. Marketing support pages are generated from the exercised registry.

## Normalized agent event

Required fields:

- `schema_version`, `event_id` UUIDv7, `session_id`, optional `parent_event_id`;
- adapter/source IDs and versions;
- provider/model canonical IDs plus raw aliases;
- execution mode and platform;
- monotonic start/end counters plus wall-clock observations;
- token categories and count quality;
- source authority and capture mechanism;
- request outcome, retry ordinal, cache/modality metadata;
- privacy classification and forbidden-field scan result;
- stable local dedup fingerprint; never transcript content.

Event IDs are generated at first live observation. Adapters cannot accept caller-supplied competitive event IDs. Raw transcript text, paths, repos, prompts, outputs, tool bodies, and secrets are forbidden in normalized events.

## Source reconciliation

Authority order: provider-authenticated receipt > native source event > official structured hook/telemetry > protocol proxy > live source-bound observation > reconstruction > historical import.

When multiple sources describe the same model execution, only the highest-authority compatible record contributes tokens. Dedup uses provider request IDs where safe, otherwise keyed local fingerprints over non-content structural fields. Conflicts quarantine the event rather than averaging counts.

## VibeProof claim envelope

Canonical top-level fields:

- protocol version;
- claim ID UUIDv7;
- account pseudonym and revocable device-key ID;
- device sequence and previous accepted-claim hash;
- challenge ID/nonce and challenge expiry;
- source event-time range and server-independent monotonic duration;
- adapter/source/provider/model identifiers;
- normalized token categories, count quality, and estimated-pricing dataset ID;
- evidence capture/environment dimensions and consumer evidence state;
- privacy scan version/result;
- batch metadata when used;
- correction/supersession reference when applicable.

No free text is permitted.

## Encoding and signing

- Deterministic CBOR following RFC 8949 deterministic encoding requirements and a project-owned stricter profile.
- Definite lengths only; shortest integers; sorted map keys by encoded-byte order; no floats, duplicate keys, undefined values, or unapproved tags.
- CDDL is normative for structure; semantic invariants are normative in prose and conformance code.
- COSE_Sign1 signs exact protected-header and payload bytes.
- Initial algorithm: Ed25519/EdDSA. Algorithm ID is protected and pinned; `none`, ambiguity, and unprotected substitution are rejected.
- Protected headers include algorithm, protocol version, key ID, and content type.
- Maximum single claim: 64 KiB encoded. Maximum batch: 1 MiB, 500 claims. Decompressed limits are enforced before allocation.

## Key and sequence lifecycle

Device keys are generated in OS-backed credential storage when available. Server stores public keys, status, enrollment account, creation, rotation, revocation, and attestation metadata.

Sequence starts at 1 and increases exactly once per locally committed claim. A claim includes the previous claim hash. Server accepts only the expected sequence/hash or an exact idempotent replay. Gaps require a signed gap declaration with local audit evidence; forks quarantine the device. Rotation requires signatures from old and new keys when the old key exists. Lost-key recovery revokes the old device identity and starts a new chain; old claims remain attributable.

## Challenge and transport

Challenges are account/device bound, random 256-bit values, single-use, and expire after 15 minutes. Offline collection stores unsigned normalized events; claims are finalized when a fresh challenge is available. Event-time lateness rules remain applicable.

Batches are independently verifiable ordered claim arrays; each claim retains its own sequence and signature. Transport compression may use zstd only after encoded-size and decompressed-size limits; signed payloads are compressed after signing.

## Acceptance outcomes

`accepted`, `accepted_idempotent`, `rejected_invalid`, `rejected_replay`, `rejected_privacy`, `rejected_unsupported`, `downgraded`, `quarantined`, or `retryable`.

Stable reason codes cover parser, canonicalization, signature, key, challenge, sequence, clock, duplicate, accounting, adapter, privacy, eligibility, rate, and internal failures. Unknown errors default to rejection without exposing sensitive internals.

## Compatibility

Major protocol changes require a new major version. Readers support current and previous major during a published migration window. Unknown mandatory fields reject; unknown extension fields are allowed only inside a signed, size-bounded extension map with registered numeric keys. Server never reinterprets old accepted claims under new semantics; corrections are explicit records.

## Conformance

Required suites: exact-byte golden vectors, independent Rust/Go/TypeScript decoders, duplicate keys, non-minimal integers, malformed protected headers, algorithm confusion, deep nesting, allocation bombs, truncation, mutation, fuzzing, differential parsing, signature alteration, sequence forks, replay storms, batch partial failure, clock rollback, key rotation, lost state, and privacy canaries.
