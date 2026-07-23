# Machine Contract Repair Specification

Updated: 2026-07-23
Status: normative P-1140B–E planning input; does not authorize implementation

## Purpose

This specification converts the repository-wide audit into exact repair requirements for the planning-grade machine contracts in `packages/schemas/`, their dependent prose, and the eventual generated Rust, Go, TypeScript and PostgreSQL representations.

No existing planning schema is implementation-ready merely because it parses. A repaired contract is complete only when:

1. its semantic owner is identified;
2. every field has a single authority and privacy classification;
3. cross-language numeric and time ranges are compatible;
4. state transitions and transaction boundaries are explicit;
5. positive, negative, malformed, race and recovery fixtures are defined;
6. prose, schema, persistence and API behavior agree;
7. repository validation proves the agreement.

## Global contract rules

### Type and encoding rules

- All network and privileged-process messages are closed-world typed structures.
- No `additionalProperties: true`, untyped `object`, arbitrary JSON, arbitrary CBOR maps or opaque serialized domain objects may cross a trust boundary.
- Byte fields are allowed only for named cryptographic values, canonical protocol payloads or fixed-format attestations with explicit maximum sizes.
- Text fields crossing the device boundary must be enums, registered IDs or validated machine identifiers. Human prose is forbidden in claims, telemetry, moderation evidence and notification payloads.
- Identifiers use UUIDv7 encoded as 16 bytes in CBOR and canonical lowercase text in JSON.
- Cryptographic digests are 32-byte SHA-256 values unless a versioned algorithm identifier says otherwise.
- Public and API timestamps use RFC 3339 UTC with no leap-second dependence. Signed protocol timestamps use unsigned epoch milliseconds with a maximum of `253402300799999`.
- Token counts, sequences and durations are unsigned 64-bit in Rust/Go/PostgreSQL. JSON exposes them as canonical decimal strings, never JavaScript numbers.
- Money uses integer minor-scale units plus an explicit decimal scale and currency. Floating point is prohibited.
- Unknown values are represented explicitly by optional fields or enums; zero must never mean unknown.

### Authority rules

- Adapters observe source facts but do not select final competitive totals or evidence state.
- The collector applies a versioned accounting profile and deterministic rules.
- The device signs an `EvidenceClaim` containing facts and commitments only.
- The server creates `VerifierAppraisal`, `CheckpointReceipt`, pricing interpretations and ranking eligibility.
- Corrections, exclusions and moderation effects are server-authorized append-only records.
- Derived projections are rebuildable and never treated as immutable source facts.

## Data-stage model

### `SourceObservation`

Boundary: adapter process to collector only.

May contain locally sensitive source fields required for parsing, but must be ephemeral and absent from sync-accessible storage. Required envelope:

- `observation_schema_version`;
- adapter artifact digest and manifest digest;
- source product, source version, platform and execution mode;
- source cursor and runtime generation;
- source-local event reference;
- token observations and source total semantics;
- outcome, retry, cancellation, cache and modality facts;
- local wall-clock observation and monotonic clock domain;
- sensitivity labels for every optional source field.

The IPC schema must enumerate each source observation variant. A generic `bytes payload` or `json payload` field is prohibited.

### `NormalizedAccountingEvent`

Boundary: collector-local durable fact. It is not directly network serializable.

Required fields:

- schema version;
- collector-generated UUIDv7 event ID;
- local session ID and optional parent event ID;
- adapter, adapter artifact digest and certification tuple;
- source/provider/model canonical IDs;
- accounting profile ID and digest;
- monotonic clock domain, generation, start and end;
- bounded wall-time observation plus uncertainty;
- canonical mutually exclusive token components;
- source-observed categories retained separately for audit;
- count authority and reconstruction method;
- retry/cancellation/outcome semantics;
- duplicate-domain type and keyed local fingerprint;
- deterministic rule bundle ID and result;
- privacy scan policy ID and pass result.

Forbidden fields include raw model aliases, provider request IDs, prompts, outputs, paths, repository names and content-derived hashes.

### `LocalDetectorResult`

Boundary: optional local-only advisory record.

Required fields:

- detector bundle digest;
- runtime digest;
- feature schema version;
- input mode;
- anomaly-class enum set;
- confidence bucket;
- execution status;
- resource-use summary;
- deterministic precheck bundle ID.

No prose, embeddings, generated explanation or network address is permitted. The detector cannot change counts, claim eligibility or evidence profile.

### `EvidenceClaim`

Boundary: device to server, signed.

Required fields:

- protocol major/minor;
- claim ID;
- account pseudonym;
- device lineage ID and active key ID;
- claim sequence;
- previous local commitment head;
- current local commitment head;
- previous server checkpoint receipt ID;
- challenge ID and nonce;
- event interval start/end plus uncertainty and monotonic duration;
- adapter artifact digest;
- collector artifact digest;
- certification bundle digest;
- source/provider/model registered IDs;
- accounting profile ID and digest;
- canonical token components;
- duplicate-domain commitment;
- deterministic rule-bundle ID and compact result summary;
- privacy policy ID and pass result;
- optional local-detector result commitment.

The claim must not contain:

- Standard/Hardened/Imported;
- pricing dataset or estimated cost;
- correction authority;
- arbitrary extension map;
- raw request identifiers;
- caller-controlled event IDs;
- unrestricted strings or metadata.

### `VerifierAppraisal`

Boundary: server-owned immutable fact.

Required fields:

- appraisal ID;
- claim ID and canonical claim digest;
- verifier policy ID and implementation digest;
- acceptance outcome;
- source, capture, accounting, device-key, continuity, environment and freshness classes;
- public evidence profile ID and public state;
- ranking eligibility state;
- reason-code set;
- anomaly disposition;
- evaluated certification and policy digests;
- creation time;
- optional expiry or re-evaluation trigger.

### `CheckpointReceipt`

Boundary: server to device, server-signed.

Required fields:

- receipt ID and protocol version;
- account pseudonym and device lineage ID;
- accepted through claim sequence;
- accepted local commitment head;
- last accepted claim digest;
- server ledger position or opaque monotonic receipt sequence;
- verifier policy ID;
- issued and expiry times;
- server signing key ID and signature.

A receipt acknowledges continuity only through the bound head. It does not prove the truth of future offline events.

## Accounting profile contract

Each profile is immutable and digest-addressed. Identity tuple:

- provider/runtime;
- API or protocol mode;
- source version range;
- model family or tokenizer identity;
- platform constraints;
- effective interval;
- profile semantic version;
- profile content digest.

A profile defines:

- source fields and units;
- category containment graph;
- canonical mutually exclusive output components;
- whether source total is authoritative;
- cache read/write semantics;
- reasoning-token containment;
- modality conversion;
- retry and cancellation treatment;
- nested-agent parent/child inclusion;
- tokenizer/runtime reconstruction method;
- maximum evidence ceiling;
- malformed and contradiction rules.

Canonical Token Burn is the checked sum of mutually exclusive profile outputs. There is no universal formula that blindly adds every provider field.

## VibeProof encoding and COSE profile

P-1140C must freeze:

- deterministic CBOR map labels;
- whether outer COSE tag 18 is required;
- protected headers for algorithm, key ID, protocol version and content type;
- prohibition of security-relevant unprotected headers;
- canonical `kid` byte encoding;
- COSE_Key representation for Ed25519;
- external AAD domain separator and version;
- exact Sig_structure bytes;
- claim and batch content types;
- decoder depth, item-count, string, byte-string and allocation limits;
- no indefinite lengths, floats, duplicate keys, non-minimal integers or unregistered tags;
- no generic extension map in protocol v1.

Suggested hard limits pending fixture validation:

- single signed claim: 16 KiB;
- atomic batch: 256 claims and 1 MiB encoded;
- nesting depth: 12;
- map entries per object: 64;
- text identifier: 128 UTF-8 bytes;
- byte string: 64 KiB except the outer bounded batch;
- parser total allocation: no more than 4x encoded bytes plus fixed overhead.

## Atomic claim transaction

One PostgreSQL transaction must:

1. obtain the authenticated account and device-lineage lock;
2. decode with preallocation limits;
3. verify deterministic canonical form;
4. verify signature, algorithm, key state and key-to-lineage binding;
5. resolve exact idempotency record and request fingerprint;
6. validate challenge ownership, expiry and single use;
7. validate expected sequence, local head and previous checkpoint;
8. validate certification, artifact digests and accounting profile;
9. validate token invariants, time uncertainty and delayed-sync policy;
10. check duplicate-domain conflicts across account/device scope;
11. apply privacy and ranked-identity eligibility policy;
12. create immutable claim fact;
13. create verifier appraisal;
14. consume challenge;
15. advance device checkpoint state;
16. create server-signed checkpoint receipt;
17. insert transactional outbox rows;
18. persist exact response bytes for idempotent replay;
19. commit before publishing any derived event.

Byte-identical retry returns the stored response. Reuse of the same idempotency key, claim ID, sequence, challenge, commitment or duplicate domain with different request bytes is a conflict and never an idempotent success.

## PostgreSQL target entities

The repaired migration design must separate immutable facts from mutable workflow state.

Immutable facts:

- accounts and account creation facts;
- linked provider subject facts;
- device lineages, key events and attestations;
- OAuth authorization events;
- accepted evidence claims;
- verifier appraisals;
- checkpoint receipts;
- correction records;
- pricing interpretations and line items;
- moderation actions and reversals;
- ranking events;
- audit events.

Mutable state/projections:

- active sessions and token families;
- current device/key status;
- current ranked-identity eligibility;
- open investigations and appeals;
- current social relationships and board memberships;
- presence leases;
- notification delivery/read state;
- ranking projections, snapshots and caches;
- worker checkpoints.

Required database guarantees include:

- canonical ordered friendship pair constraints;
- one active owner membership per board and no competing owner column;
- partial unique indexes for active provider subjects, active handles and live token-family members;
- foreign-key binding from moderation effects to exact claims, ranking views and periods;
- immutable accepted-claim payload and appraisal rows;
- idempotency uniqueness scoped by principal, route and key;
- challenge and checkpoint single-use/monotonic constraints;
- append-only triggers or restricted roles for fact tables;
- checked integer arithmetic in aggregation procedures;
- projection generation and rebuild promotion records.

## API repair requirements

- Replace generic `Resource` and untyped `Collection.items` with endpoint-specific schemas.
- Every write endpoint declares authentication, authorization, recent-auth requirement, idempotency scope and conflict semantics.
- CBOR request bodies are binary `application/vibemaxxing-claim-batch+cbor`, not base64 JSON strings.
- Claim submission returns one atomic batch outcome. Per-claim diagnostics may be listed, but cannot imply partial commit.
- Remove country endpoints from launch API.
- Presence renewal is accepted only from an authorized native device and references recent qualifying collector activity or accepted claim continuity.
- Server deletion endpoints cannot claim to delete local data. Local deletion is a device command and receipt.
- Error `details` use a closed typed union; unrestricted objects are prohibited.
- All collection schemas define stable cursor identity, maximum page size and snapshot/revision binding.
- Rate-limit responses include `429`, `Retry-After` and safe limit metadata.
- Polling endpoints define minimum interval, expiration and outstanding-object limits.

## OAuth and session target model

OAuth transaction fields:

- transaction ID;
- provider and issuer;
- client configuration ID;
- exact redirect URI;
- state verifier hash;
- encrypted PKCE verifier where required;
- intended action;
- initiating web session or native instance;
- device enrollment public-key commitment where applicable;
- creation, expiry and consumption;
- one-time browser handoff secret hash.

Session model:

- separate web and native session families;
- access-token identifier and expiry;
- rotating refresh-token family with parent/child lineage;
- replay detection that revokes the family;
- device/native instance binding;
- authentication strength and recent-auth time;
- per-session and revoke-all controls;
- provider-loss and recovery restrictions;
- optional DPoP key binding after an evidence-backed ADR.

## Ranking and pricing target model

`ranking_view_id` is an immutable digest-addressed identity over:

- scope type and scope ID;
- metric ID and version;
- period ID;
- evidence eligibility filter;
- agent/provider/model filters;
- board policy version;
- ranking policy version;
- projection schema version.

Every snapshot, cursor, rank movement, overtake, moderation effect and rebuild references a `ranking_view_id`.

Estimated Cash Burn is a server-owned interpretation with:

- pricing dataset and rule digest;
- immutable event-time model alias resolution;
- category line items;
- unit, denominator and quantity;
- region, service tier, batch/flex/priority mode and modality conditions;
- threshold and cache-duration conditions;
- rounding rule and intermediate amount;
- canonical currency and scale;
- final estimated amount or typed unpriced reason.

## Social and moderation state-machine requirements

Friendship:

- canonical unordered pair identity;
- one pending request per pair;
- crossed requests resolve deterministically;
- blocking atomically removes active friendship/rival state and invalidates invitations/notifications;
- unblocking never restores old relationships.

Boards:

- ownership is represented by membership role, not a competing owner field;
- ownership transfer is one transaction with recent authentication;
- last owner cannot leave;
- policy versions apply prospectively unless an explicit rebuild record exists;
- organization/community/hacker-house specialization uses typed board metadata.

Presence:

- source is native device activity, not browser self-assertion;
- lease binds account, device, qualifying activity reference and privacy policy;
- audience projection is computed per viewer;
- revocation, blocking and privacy changes invalidate visibility immediately;
- multi-device merge is deterministic and never exposes project details.

Notifications:

- typed event union with fixed fields;
- typed preference matrix;
- stable dedup/grouping key;
- hysteresis and quiet-hour policy version;
- visibility recheck at render/delivery time;
- retraction event when underlying relationship, rank or moderation state changes.

Moderation:

- case subject, affected claims, periods and ranking views are explicit;
- actions produce append-only effects, never mutate accepted facts;
- reversal produces inverse ranking events and projection rebuild;
- permanent account-level outcomes require human authorization;
- user-safe reasons are separate from private reviewer evidence;
- appeal decision records exact restored/excluded effects.

## Local IPC repair

Replace `bytes normalized_event_json` with generated typed unions:

- source observation submission variants;
- normalized event acknowledgment;
- claim construction request/result;
- queue and receipt summaries;
- health, lifecycle and capability messages;
- local deletion/export operations.

Every envelope includes:

- protocol major/minor;
- message ID;
- request/response correlation ID;
- sender process role;
- connection nonce;
- monotonic message sequence;
- deadline;
- body type;
- authenticated challenge response.

Peer identity, ACL, body-size, connection-count, rate and deadline enforcement occur before body materialization.

## Updater and release-set contract

The updater contract must define:

- trusted root bootstrap and root rotation;
- threshold roles and offline/online key custody;
- delegated platform, architecture and channel targets;
- timestamp, snapshot and targets expiry;
- rollback, freeze, mix-and-match and endless-data defenses;
- release-set manifest binding compatible versions of daemon, collector, sync, shell, CLI, adapters, schemas and database migrations;
- minimum/maximum protocol and database versions;
- migration preconditions and rollback compatibility;
- compromised-version block policy preserving export/uninstall;
- SBOM, source commit, provenance and transparency references;
- atomic staging, health check and rollback transaction;
- interrupted download/install and disk-full recovery.

## Reason-code registry requirements

Every code must declare:

- stable code;
- subsystem and class;
- default protocol/API outcome;
- retryability;
- public-safe message key;
- internal diagnostic visibility;
- enforcement severity;
- appeal eligibility;
- owning policy/state machine;
- first protocol/API version;
- deprecation replacement.

Unknown internal failures fail closed without leaking sensitive context. Reason codes are not free-form logs.

## Policy registry requirements

Every policy entry must declare:

- typed value and unit;
- allowed range or enum;
- owner;
- effective time;
- prospective/retroactive behavior;
- affected state machines;
- change authorization;
- rebuild requirement;
- user-notice requirement;
- emergency override behavior;
- fixture references.

Country policies move to a post-launch registry and cannot affect launch validation.

## Required P-1140E validation matrix

At minimum:

- Rust/Go exact-byte claim and receipt vectors;
- malformed CBOR/COSE corpus;
- cross-language numeric-bound fixtures;
- every accounting profile category-containment case;
- retry, cancellation, cache, reasoning, modality and nested-agent cases;
- privacy canaries at adapter, IPC, storage, claim, HTTP, telemetry, notification and moderation boundaries;
- challenge races, idempotency conflicts, replay storms and sequence forks;
- offline checkpoint, long delay, clock rollback, suspend and restore;
- key rotation, lost key, clone and new-lineage requalification;
- OAuth state, PKCE, issuer, redirect, browser/native binding and token-family replay;
- friendship crossed-request, block and canonical-pair properties;
- board ownership transfer and last-owner constraints;
- presence privacy/revocation and multi-device aggregation;
- notification dedup, visibility recheck and retraction;
- moderation reversal and ranking rebuild equivalence;
- updater rollback, freeze, mix-and-match and compromised release;
- clean-checkout reference/schema/registry validation.

## Exit condition

This specification is satisfied only when the repaired prose and machine artifacts exist and validation demonstrates their agreement. It is not satisfied by documenting future work, adding empty schemas, or marking a parser-only check green.