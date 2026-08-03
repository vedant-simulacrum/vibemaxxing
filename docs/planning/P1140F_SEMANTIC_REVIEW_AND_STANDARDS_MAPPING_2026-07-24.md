# P-1140F Semantic Review and Standards Mapping

Status: `in-progress-planning`
Updated: 2026-08-04
Review base: `41ecb77856991ee033afcfe52d24eb42cd6ecb47`
Evidence maturity: repository and standards audit; not runtime proof, certification, implementation authorization, or launch evidence

## Purpose

P-1140E proves structural repository consistency only. P-1140F owns semantic closure: whether specifications, schemas, state machines, persistence, fixtures, prototypes, and review records describe one implementable product without contradictory authorities.

The original four-finding review against `f06f630619427ec7f0576b57c4b3ac914d9a4c87` is superseded. Current `main` contains later executable protocol/accounting prototypes and additional contracts that were outside that review.

## Current result

- Semantic P0 open: 0
- Semantic P1 clusters open: 13
- P-1104: blocked
- Product implementation: unauthorized
- Product/security/evaluation/release/signing/deployment workflows: remain disabled

A green schema check, fixture, symbolic SQL race, or cross-language agreement does not close a finding unless it exercises the exact normative authority and invariant.

## Reality classification

### Implemented

- bounded fixture-backed hosted-web and Storybook prototype;
- planning validators and repository doctor;
- planning-grade schemas, registries, fixtures, vectors, and symbolic race plans;
- bounded Rust and Go protocol/accounting prototypes added after the original review target.

### Not implemented

- production collector, daemon, sync, shell, installers, updater, and local storage;
- certified source adapters or universal competitive support;
- normative VibeProof v1 codecs and verifier interoperability;
- production identity, ranking, social, presence, notification, moderation, export, deletion, and release services;
- production PostgreSQL migrations and transaction evidence;
- production infrastructure, releases, deployment, and operations.

The Rust and Go protocol/accounting code is exploratory executable prototype material, not normative VibeProof evidence.

## Consolidated semantic P1 register

### SR-005 — Protocol authority and executable drift

The normative VibeProof v1 authority is the deterministic 31-field CBOR payload and mandatory COSE_Sign1 profile in `packages/schemas/vibeproof-claim-v1.cddl` and `conformance/vibeproof/v1/`. The later Rust/Go prototype and `conformance/protocol/vibeproof-v1-vectors.json` implement an unsigned 11-field shadow protocol, including client-selected evidence and `billable` values.

Closure requires quarantining or removing the shadow protocol from normative/product paths, rebuilding reference codecs from the CDDL/COSE authority, and pointing conformance to the sole exact-vector corpus.

### SR-006 — OAuth, linked identity, recovery, and ranked identity

The API has competing identity-link paths, including a raw authorization-code mutation detached from its OAuth transaction. Transactions do not bind the target account, session, recent-auth grant, exact provider configuration, or result. Provider loss, compromise, recovery, consolidation, canonical ranked identity, retirement, and appeal effects lack executable authorities.

Closure requires one persisted OAuth transaction authority; exact linked-identity, recovery, consolidation, ranked-identity, investigation, and appeal aggregates; no silent provider-subject reassignment; and D-070 claim-level historical consolidation.

### SR-007 — Device lineage, challenge, replay, checkpoint, and recovery

CDDL, OpenAPI, and PostgreSQL describe incompatible challenge objects and identifier types. Continuity is stored per device while the protocol claims lineage-wide authority. Checkpoint, rotation, recovery, clone, and fork semantics are incomplete.

Closure requires one lineage-scoped continuity authority, one canonical challenge, exact checkpoint and rotation contracts, and D-072 fork handling.

### SR-008 — Local daemon, shell, IPC, and platform supervision

The shell state machine combines independent daemon, collection, sync, authentication, update, permission, and connectivity dimensions and contains unreachable or contradictory states. The shared Protobuf omits process generation, trusts self-declared roles, lacks a complete handshake/capability grant, and structurally permits cross-role messages.

Closure requires a narrow shell lifecycle, separate subsystem projections, pre-auth startup, separate trust-domain protocols, OS peer and artifact identity, daemon-assigned role, generation, capability, replay protection, revocation, typed lifecycle operations, local persistence, and same-user impersonation cases.

### SR-009 — Universal adapter certification and deterministic accounting

One manifest-wide certificate can authorize untested products, platforms, modes, and accounting profiles. Certification does not bind the exact tuple or expiry. Source observations omit facts required for deterministic normalization and multi-observer deduplication. ACP and OpenTelemetry names alone do not provide competitive accounting authority.

Closure requires atomic compatibility tuples, signed result bundles, exact validity and revocation, tuple binding before normalization, canonical hashing, checked accounting, and private-only generic paths until one exact profile is exercised.

### SR-010 — Ranking authorization, immutable generations, periods, and corrections

One public route structurally serves global, friends, rivals, and board leaderboards without viewer or board identity. Stable definition and mutable generation facts are mixed. SQL cannot retain isolated score generations or durable snapshot pagination. Period, season, contribution, correction, movement, overtake, and streak authorities remain incomplete.

Closure requires separate ranking definition, audience instance, generation, snapshot, authorization, immutable entries, active pointer, exact periods/seasons, contribution ledger, correction/retraction, and PostgreSQL-backed ranking evidence. Historical consolidation follows D-070.

### SR-011 — Social relationships, boards, presence, and notifications

Board invitation, membership, ownership, friendship, directional block, rivalry, presence, and notification lifecycles are not coherently separated. Presence may be client-declared and its timing is contradictory. Notification inbox, transport, read, suppression, expiry, and retraction use incompatible authorities.

Closure requires D-071 non-privileged invitations with separate admin promotion/ownership transfer; separate friendship/block/rivalry authorities; D-073 presence timing and server derivation; and separate source event, inbox item, channel attempt, preference/subscription, read/dismiss, and retraction state.

### SR-012 — Idempotency and ambiguous commit recovery

The architecture promises exact replay but SQL stores only a nullable response digest. Key scope, principal types, lifecycle, crash recovery, expiry, failure caching, and business-effect/outbox linkage are incomplete.

Closure requires typed principal and operation scope, versioned request canonicalization, exact bounded response storage, atomic business/audit/outbox/result commit, explicit executing/conflict/failure/expiry/recovery states, and D-075 retention.

### SR-013 — Export, deletion, retention, and backup tombstones

Asynchronous export/deletion jobs lack durable status and completion interfaces. Export snapshot, manifest, artifact, encryption, checksum, grant, and purge authorities are absent. Server and per-device deletion are conflated. No complete data-disposition or backup-tombstone authority exists.

Closure requires durable job resources, immutable export/deletion plans, coherent snapshots, encrypted self-describing packages, per-effect and per-device results, account mutation restrictions during deletion, honest local execution receipts, complete disposition policy, tombstone reapplication, and D-076 completion wording.

### SR-014 — Release authorization, compatibility, migration, and rollback

The release set lacks a proper external trust envelope and component/path model. TUF client state, compatibility, migration, rollback, and verified installation plans are incomplete.

Closure requires TUF-backed authorization, typed components and paths, compatibility/migration graph, health and rollback classes, trusted client state, and D-074 migration-aware rollback.

### SR-015 — Privacy-safe projection and current authorization

Historical snapshots and events are not consistently separated from current authorization. Blocks, privacy changes, board removal, deletion, moderation reversal, and consolidation must immediately invalidate current display and delivery across ranking, presence, notifications, social/board views, exports, cursors, caches, and grants.

Closure requires current authorization checks at every display/delivery boundary and append-only correction/retraction rather than rewriting accepted evidence.

### SR-016 — Review, conformance, and launch-evidence integrity

Status and issue records reviewed a stale head. Some suites called conformance or ranking evidence only check schema presence, first transitions, symbolic races, or the shadow protocol. Named persistence owners are not always present.

Closure requires an exact repaired-head review, honest evidence classification, one reachable lifecycle and persistence owner per mutable aggregate, aligned vocabularies, suite names that match execution, and runtime evidence only after implementation authorization.

### SR-017 — Source-bound evidence and verifier appraisal authority

Device signatures authenticate a key and bytes; OAuth authenticates provider-account control; adapter certification authenticates an exercised artifact/configuration. None independently proves that an external source event occurred. Current claims can assert provider, model, source, adapter and evidence-related fields without a typed provider receipt or immutable verifier appraisal binding the exact claim, evidence, policy, references and result.

Closure requires D-077 semantics and explicit machine contracts for:

- `SourceReceipt` or server-observation records with issuer/provider subject, audience/resource, event/object identifier, event time, nonce or receipt ID, canonical digest, validity and signature or server-retrieval metadata;
- `EvidenceBundle` binding the claim to minimized source evidence without content leakage;
- immutable `AppraisalResult` binding claim digest, evidence digest, policy bundle/version/digest, reference values, verifier build, evaluation time, per-dimension outcomes, validity, dependencies, reasons and supersession/revocation;
- deterministic replay and uniqueness for provider receipts;
- append-only reappraisal after adapter revocation, account unlink, key compromise, source correction or policy change;
- ranking contributions pinned to an exact appraisal, never a mutable current tier.

Only provider-signed receipts or server-side retrieval under verified account binding may be called source-bound. Device-signed, adapter-certified or locally observed evidence is `attested-local` and cannot be promoted by client assertion or SLM output.

## Accepted semantic policy decisions

D-070 through D-077 are binding:

- historical score combines through independently valid, non-overlapping claim contributions, never stored-total summation;
- board invitations grant only non-privileged membership;
- detected forks quarantine all post-fork branches and remain appealable;
- presence uses 30-second pulses, 90-second idle and 300-second offline thresholds;
- irreversible migrations use roll-forward or verified pre-migration snapshot restore;
- high-impact idempotency retains exact replay for at least 30 days and claim-batch replay until safely superseded;
- hosted and per-device deletion completion are reported separately;
- source-bound evidence is reserved for provider-signed receipts or server-side verified retrieval.

No further user policy decision is required for this audit set. These decisions do not authorize implementation.

## Dependency-ordered planning tasks

### P-1140F-1 — Re-establish protocol and repository authority

- quarantine or remove the shadow protocol from normative paths;
- make CDDL and exact vectors the sole VibeProof authority;
- align status, tasks, inventories, evaluations, documentation, and issue scope;
- register every mutable authority and persistence owner.

### P-1140F-2 — Close identity, OAuth, lineage, replay, and recovery

- unify OAuth and linked-identity lifecycle;
- add account/ranked-identity recovery and D-070 consolidation;
- make continuity lineage-scoped;
- implement D-072 in challenge, checkpoint, fork, appeal, and recovery contracts.

### P-1140F-3 — Close local trust, source evidence and accounting inputs

- separate process trust domains and authenticated IPC;
- define local persistence and generation ownership;
- introduce atomic compatibility tuples and certification lifecycle;
- add source receipt, evidence bundle and immutable appraisal authorities under D-077;
- close source observation, multi-observer deduplication, profile selection, checked accounting and reappraisal.

### P-1140F-4 — Close server product state and privacy projection

- repair idempotency and exact response replay under D-075;
- repair ranking generations, authorization, periods, D-070 consolidation, appraisals and corrections;
- repair social/board ownership under D-071, presence under D-073, and notifications;
- repair export, deletion, retention, tombstones and D-076 current-authorization behavior.

### P-1140F-5 — Close release trust and repin semantic review

- define TUF-backed release, components, compatibility, migration, D-074 rollback, and eligibility;
- align API, SQL, state, events, reasons, policy, inventory and fixtures;
- run planning-safe validators only until P-1104;
- pin a new exact review head and require zero semantic P0/P1 findings before implementation authorization.

## Closure criteria

P-1140F becomes `complete-planning` only when:

1. SR-005 through SR-017 are repaired in every affected normative and machine-readable owner.
2. Every technical specification family is represented in `SCHEMA_AND_INTERFACE_INVENTORY.md` with one owner and explicit status.
3. No prototype contradicts or bypasses the sole normative protocol/accounting authority.
4. Every mutable aggregate has one reachable state machine, persistence owner, revision model, stable outcomes, and transaction boundary.
5. API, SQL, Protobuf/CDDL, fixtures, policy, reasons, inventory, and state vocabularies cross-resolve.
6. Privacy and authorization are current at every display and delivery boundary.
7. Structural validators pass without claiming semantic proof.
8. The exact repaired head receives independent manual review with zero open semantic P0/P1 findings.
9. P-1104 remains a separate explicit user authorization after this gate closes.