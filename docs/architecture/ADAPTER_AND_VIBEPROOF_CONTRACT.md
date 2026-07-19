# Adapter and VibeProof Implementation Contract

Status: normative planning contract
Version: 1
Updated: 2026-07-19

## Adapter registry

Each adapter manifest is signed and contains: `adapter_id`, semantic version, maintainer, source agent IDs/versions, supported platforms/modes, capture mechanism, required permissions, token categories, model-identity quality, source evidence class, accounting authority, public evidence ceiling, privacy risks, duplicate domains, capability probe, conformance suite version, emergency-disable status and sunset date.

Lifecycle: `experimental -> community-certified -> competitive-certified -> hardened-certified`; any state may transition to `degraded`, `suspended`, `retired` or `unsupported`.

Unknown source versions fail closed for Hardened evidence and downgrade only to the highest exact exercised compatible Standard tier. Marketing support pages are generated from the exercised registry.

### Minimum generic adapter admission contract

A generic or community adapter may enter `generic-live` only when it declares and passes:

- exact observation mechanism: official hook, local API, file, process observation, proxy, gateway or reconstruction;
- source/runtime version probe plus negative and unknown-version probes;
- source evidence class and accounting authority from `EVIDENCE_AND_ATTESTATION_PROFILES.md`;
- duplicate domains and interactions with host/guest, IDE/CLI, proxy/provider and orchestrator/subagent paths;
- retry, streaming finalization, cancellation, partial failure and missing-usage behavior;
- model identity quality and unknown-alias behavior;
- privacy canaries and a fixed outbound field allowlist;
- bounded CPU, memory, disk, file, process and parser limits;
- hostile or malformed source-output handling;
- emergency disable, revocation, downgrade and sunset behavior.

Generic support never implies Hardened support. An adapter with no exercised source binding, duplicate-domain contract or privacy-negative fixtures is `unsupported`, not `generic-live`.

## Normalized agent event

Required fields:

- `schema_version`, `event_id` UUIDv7, `session_id`, optional `parent_event_id`;
- adapter/source IDs and versions;
- provider/model canonical IDs plus raw aliases;
- execution mode and platform;
- monotonic start/end counters plus wall-clock observations;
- token categories and count quality;
- source evidence class, accounting profile and capture mechanism;
- request outcome, retry ordinal, cache/modality metadata;
- privacy classification and forbidden-field scan result;
- duplicate-domain ID and stable local keyed dedup fingerprint;
- optional source request/execution identifier when safe;
- local commitment reference and continuity class when applicable;
- never transcript content.

Event IDs are generated at first live observation. Adapters cannot accept caller-supplied competitive event IDs. Raw transcript text, paths, repos, prompts, outputs, tool bodies and secrets are forbidden in normalized events.

## Source reconciliation

Evidence classes and their ceilings are normative in `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`.

Accounting-source precedence is profile-specific rather than one universal prose order. In general, independently provider-verifiable evidence outranks VibeMaxxing-server-observed provider responses, which outrank exercised official structured events, exercised gateways/proxies and deterministic derivation. E6 imports never enter competition.

Ordinary provider JSON usage metadata observed on a user-controlled machine is not a provider-signed receipt. TLS authentication during transport does not create a portable signed artifact after termination.

When multiple sources describe one execution, only one compatible canonical accounting record contributes tokens. Dedup uses a provider request ID only when its issuer, namespace and reuse behavior are known. Otherwise it uses a versioned keyed fingerprint over approved non-content structural fields within a declared duplicate domain. Conflicts quarantine rather than average counts.

A later higher-authority observation creates an explicit reconciliation/correction record. It never silently adds a second execution or mutates the immutable original event.

## VibeProof claim envelope

Canonical top-level fields:

- protocol version;
- claim ID UUIDv7;
- account pseudonym and revocable device-key ID;
- device sequence and previous accepted-claim hash;
- challenge ID/nonce and challenge expiry;
- source event-time range and server-independent monotonic duration;
- adapter/source/provider/model identifiers;
- exact certification tuple and profile ID;
- normalized token categories, count quality, accounting profile and estimated-pricing dataset ID;
- evidence class, key class, continuity class and environment class;
- duplicate domain, event ID and safe source execution identifier when available;
- pre-challenge local commitment reference/time when C3/C4 applies;
- privacy scan version/result;
- batch metadata when used;
- correction/supersession reference when applicable.

No free text is permitted.

## Encoding and signing

- Deterministic CBOR following RFC 8949 deterministic encoding requirements and a project-owned stricter profile.
- Definite lengths only; shortest integers; sorted map keys by encoded-byte order; no floats, duplicate keys, undefined values or unapproved tags.
- CDDL is normative for structure; semantic invariants are normative in prose and conformance code.
- COSE_Sign1 signs exact protected-header and payload bytes.
- Initial algorithm: Ed25519/EdDSA. Algorithm ID is protected and pinned; `none`, ambiguity and unprotected substitution are rejected.
- Protected headers include algorithm, protocol version, key ID and content type.
- Maximum single claim: 64 KiB encoded. Maximum atomic batch: 1 MiB and 500 claims. Decompressed limits are enforced before allocation.

## Key and sequence lifecycle

Device key classes are defined in `EVIDENCE_AND_ATTESTATION_PROFILES.md`; platform behavior is defined in `PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`. “Stored in an OS credential store” does not itself imply non-exportability or hardware protection.

Sequence starts at 1 and increases exactly once per locally committed claim. A claim includes the previous accepted-claim hash. Server accepts only the expected sequence/hash or an exact idempotent replay. Gaps require a signed gap declaration with local audit evidence; forks quarantine the device. Rotation requires signatures from old and new keys when the old key exists. Lost-key recovery revokes the old device identity and starts a new chain; old claims remain attributable.

A restored local state behind the last server checkpoint cannot silently continue. It enters recovery, and migration or clone uncertainty lowers the evidence profile or creates a new device chain.

## Offline commitments, challenge and transport

Challenges are account/device bound, random 256-bit values, single-use and expire after 15 minutes. A challenge proves submission freshness only; it does not prove the event existed before challenge issuance.

Standard offline collection may store unsigned normalized events within bounded encrypted storage. C3/C4 continuity requires each observed event or bounded event batch to be committed before any future submission challenge is known into an append-only local commitment chain. The claim later binds the commitment ID, commitment hash, monotonic commitment time and chain predecessor.

The server compares submitted commitments against device checkpoints and rejects conflicting reuse. This narrows retrospective fabrication but does not claim to defeat a fully compromised user-controlled machine.

Batches are atomic and independently verifiable ordered claim arrays. Each claim retains its own sequence and signature under ADR-007 semantics. Transport compression may use zstd only after encoded-size and decompressed-size limits; signed payloads are compressed after signing.

## Acceptance outcomes

`accepted`, `accepted_idempotent`, `rejected_invalid`, `rejected_replay`, `rejected_privacy`, `rejected_unsupported`, `downgraded`, `quarantined` or `retryable`.

Stable reason codes cover parser, canonicalization, signature, key, challenge, sequence, commitment, rollback, clock, duplicate, accounting, adapter, privacy, eligibility, rate and internal failures. Unknown errors default to rejection without exposing sensitive internals.

## Compatibility

Major protocol changes require a new major version. Readers support current and previous major during a published migration window. Unknown mandatory fields reject; unknown extension fields are allowed only inside a signed, size-bounded extension map with registered numeric keys. Server never reinterprets old accepted claims under new semantics; corrections are explicit records.

## Conformance

Required suites include exact-byte golden vectors, independent Rust/Go/TypeScript decoders, duplicate keys, non-minimal integers, malformed protected headers, algorithm confusion, deep nesting, allocation bombs, truncation, mutation, fuzzing, differential parsing, signature alteration, sequence forks, challenge replay, event replay, commitment reuse, clone concurrency, snapshot rollback, batch partial failure, clock rollback, key rotation, lost state, source-version downgrade, duplicate-domain conflicts, higher-authority corrections and privacy canaries.
