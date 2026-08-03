# P-1140F Semantic Review and Standards Mapping

Status: `in-progress-planning`
Updated: 2026-08-04
Review target: current `main` at `41ecb77856991ee033afcfe52d24eb42cd6ecb47`
Evidence maturity: repository and standards audit; not runtime proof, third-party security certification, implementation authorization, or launch evidence

## Purpose

P-1140E proves structural repository consistency only. P-1140F owns semantic closure: whether the specifications, schemas, state machines, persistence model, fixtures, executable prototypes, and review records describe one implementable product without contradictory authorities.

The earlier four-finding review at `f06f630619427ec7f0576b57c4b3ac914d9a4c87` is stale. Current `main` contains later executable protocol/accounting prototypes and additional machine contracts, while `STATUS.md`, `AGENTS.md`, this record, and issue #41 still described the repository as having only SR-001 through SR-004 open and no VibeProof runtime codec. Those statements are superseded by this record.

## Current result

- Semantic P0 open: 0
- Semantic P1 clusters open: 12
- Product implementation: unauthorized
- P-1104: blocked
- Automated product, security, evaluation, release, signing, deployment, and operational workflows: remain disabled

No individual green schema check, fixture, cross-language agreement, or symbolic SQL race closes a finding unless it exercises the exact normative authority and its security or privacy invariant.

## Reality classification

### Implemented

- bounded fixture-backed hosted-web and Storybook prototype;
- planning validators and repository doctor;
- schemas, registries, fixtures, exact vectors, and symbolic race plans;
- bounded Rust and Go protocol/accounting prototypes added after the original P-1140F review target.

### Not implemented

- production collector, daemon, sync process, shell, installers, updater, and local storage;
- certified source adapters or universal competitive support;
- normative VibeProof v1 codecs and verifier interoperability;
- OAuth, identity, recovery, ranked-identity, ranking, social, presence, notification, moderation, export, deletion, and release services;
- production PostgreSQL migrations and executable transaction evidence;
- production infrastructure, release repository, deployment, and operations.

The later Rust and Go code is an exploratory executable prototype. It is not normative VibeProof v1 evidence and does not authorize additional product implementation.

## Consolidated semantic P1 register

### SR-005 — Protocol authority and executable drift

**Problem.** The normative VibeProof v1 authority is the 31-field deterministic CBOR payload and mandatory COSE_Sign1 profile in `packages/schemas/vibeproof-claim-v1.cddl` and `conformance/vibeproof/v1/`. The later Rust/Go prototype and `conformance/protocol/vibeproof-v1-vectors.json` implement an unsigned 11-field shadow protocol, including client-selected evidence and `billable` values. The `protocol-conformance` gate exercises the shadow protocol rather than the normative vectors.

**Required closure.** Remove or explicitly quarantine the shadow protocol from product import paths; rebuild Rust and Go reference codecs from the normative CDDL and COSE profile; point all protocol conformance to the sole exact-vector authority; classify suites as blocked until exact payload, signature, malformed, resource, continuity, rotation, and receipt cases pass.

**Primary owners.** `packages/schemas/vibeproof-claim-v1.cddl`, `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `crates/vibeproof-core/`, `apps/api/cmd/api/`, `conformance/vibeproof/v1/`, `evals/suites/suites.yaml`.

### SR-006 — OAuth, linked identity, recovery, and ranked identity

**Problem.** The API has competing identity-link paths, including a raw authorization-code mutation detached from the OAuth transaction. Persisted transactions do not bind the target account, session, recent-authentication grant, exact provider configuration, or result. Unlinking does not identify the exact linked identity or protect the final authentication method. Provider loss, compromise, recovery, duplicate-account consolidation, canonical ranked identity, retirement, and appeal effects lack executable authorities. Named ranked-identity persistence owners do not exist.

**Required closure.** Use one persisted OAuth transaction authority for sign-in, linking, reauthentication, and recovery; bind link transactions to account, session, recent-auth grant, provider revision, redirect, state, and PKCE; remove standalone authorization-code identity mutations; add exact linked-identity, account-recovery, consolidation, ranked-identity, investigation, and appeal-effect aggregates; prohibit silent provider-subject reassignment and automatic score-history summation.

**Primary owners.** `packages/schemas/openapi-v1.yaml`, `planning-schema.sql`, state-machine and reason registries, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`.

### SR-007 — Device lineage, challenge, replay, checkpoint, and recovery

**Problem.** CDDL, OpenAPI, and PostgreSQL describe incompatible challenge objects and identifier types. SQL does not persist the challenge's expected lineage tuple. Continuity is keyed by device rows while the protocol claims lineage-wide authority, allowing restored installations to receive independent sequence state. Checkpoint receipts and key rotation omit normative fields and dual authorization. Clone suspicion has no real lifecycle authority and is non-appealable despite legitimate restore and rollback causes.

**Required closure.** Make continuity lineage-scoped; define one canonical challenge across CDDL, API, SQL, vectors, and verifier; freeze expected lineage revision, sequence, commitment head, checkpoint, batch commitment, policy, and expiry; persist typed continuity and duplicate-domain fields; define exact rotation, lost-key recovery, fork quarantine, survivor selection, requalification, appeal, and reversal.

**Primary owners.** VibeProof CDDL and protocol, OpenAPI, PostgreSQL planning schema, local IPC, state/reason registries, threat and integrity models.

### SR-008 — Local daemon, shell, IPC, and platform supervision

**Problem.** The interactive-shell machine combines independent daemon, collection, sync, authentication, update, permission, and connectivity dimensions, has unreachable states, contradicts terminal declarations, and cannot restart after crash. The shell requires a native session before login and a device signature for IPC. The shared Protobuf omits process generation, trusts a self-declared sender role, lacks a handshake and capability grant, and structurally permits every role to send every message. Same-user component impersonation is not covered. Windows Task Scheduler cannot independently meet the stated ten-second restart target.

**Required closure.** Restrict shell lifecycle to process and connection state; expose other subsystem states as projections; allow pre-auth shell startup; separate collector, sync, user-control, dashboard, privileged-supervisor, and updater trust domains; bind channels to OS peer identity, artifact/release identity, daemon-assigned role, generation, capability set, nonce, sequence window, and revocation; replace generic lifecycle actions with typed operations; classify weaker platform launchers honestly.

**Primary owners.** `local-control-v1.proto`, native runtime contracts, ADR-010/012/013, platform profiles, state machines, local persistence schema and platform conformance.

### SR-009 — Universal adapter certification and deterministic accounting

**Problem.** One manifest-wide certification can authorize a Cartesian product of untested products, platforms, modes, and accounting profiles. Certification does not bind the exact artifact, manifest, collector, source product, accounting profile, or expiry. Capture-mode vocabularies drift. Source observations omit facts required for deterministic normalization and nested/multi-observer deduplication. Accounting profile digests and examples contain placeholders. ACP and OpenTelemetry compatibility are transport facts, not stable competitive accounting authority.

**Required closure.** Separate broad capability declarations from one atomic compatibility tuple and one signed certification result; bind exact artifacts, source/version, platform, mode, protocol/telemetry profile, accounting profile, privacy policy, suite, validity interval, and evidence ceiling; add mutable per-tuple suspension and revocation; select the tuple before normalization; use canonical JSON hashing; keep generic ACP, OTel, proxy, and wrapper paths private analytics until one exact profile is exercised.

**Primary owners.** adapter/source/normalized/accounting schemas, compatibility registry, evidence policy, universal compatibility contract, validators and certification fixtures.

### SR-010 — Ranking authorization, immutable generations, periods, and corrections

**Problem.** One public route structurally serves global, friends, rivals, and board leaderboards without viewer or board identity. Ranking IDs are being used as selectors without authorization. Viewer-relative cohorts and block/privacy/membership revisions are absent. The allegedly content-addressed view mixes stable definition and mutable generation facts. SQL keys scores without generation, so isolated build, validation, promotion, rollback, and durable pagination cannot work. Snapshot rows do not retain ordered contents. Period, season, tie, contribution, correction, movement, overtake, and streak authorities are incomplete. The `ranking-accounting` suite does not execute ranking.

**Required closure.** Separate ranking definition, audience instance, immutable generation, snapshot, and authorization; make only global views public by default; bind viewer-relative cohorts and current authorization; store generation-keyed immutable entries and one active pointer; use score-only `rank()` peer semantics with deterministic display order; add exact period/season lifecycle, contribution ledger, correction and derived-event retraction; replace the mislabeled evaluation with PostgreSQL-backed ranking evidence.

**Primary owners.** OpenAPI, ranking-view schema, PostgreSQL schema, state/event/reason registries, product/ranking contracts and evaluation fixtures.

### SR-011 — Social relationships, boards, presence, and notifications

**Problem.** Board invitations can structurally request privileged roles without a closed board-role authorization model, while SQL cannot retain invitee or requested role. Board creation and ownership transfer cannot guarantee exactly one owner. Friendship embeds directional block state in an undirected aggregate and omits decline, cancel, expiry, unblock, and relationship generations. Presence can be client-declared through an account session, has contradictory idle/expiry timing, and lacks qualifying-activity and viewer authorization. Notification inbox, channel delivery, read, suppression, expiry, and retraction use incompatible authorities and vocabularies.

**Required closure.** Separate friendship, directional block, rivalry, board membership state, and board role; create initial owner atomically and transfer ownership through one paired transaction; add explicit role/action authorization; derive presence from device-bound qualifying activity with separate viewer visibility; separate immutable source event, recipient inbox item, per-channel attempt, preferences/subscriptions, read/dismiss, and retraction.

**Primary owners.** OpenAPI, PostgreSQL schema, state machines, social/integrity events, policy/reason registries, product, privacy, and threat contracts.

### SR-012 — Idempotency and ambiguous commit recovery

**Problem.** The architecture promises exact replay of the original mutation response, but SQL stores only a nullable digest. The unique key omits route/operation scope and supports only account principals. State vocabularies disagree. There is no defined in-progress, crash recovery, failure caching, expiry, or business-effect/outbox linkage. A claim batch committed before a dropped response cannot return the exact signed checkpoint receipt on retry.

**Required closure.** Key by typed principal, operation/API version, and idempotency key; define versioned request canonicalization; store exact bounded status, content type, safe headers, body bytes, schema version, and result references; commit ledger, business effect, audit, outbox, and response together; define executing, committed, replayable-failure, conflict, expiry, and abandoned reservation semantics; add crash-before/after-commit and exact-byte replay evidence.

**Primary owners.** authoritative state contract, OpenAPI, PostgreSQL schema, state/reason/policy registries and PostgreSQL race fixtures.

### SR-013 — Export, deletion, retention, and backup tombstones

**Problem.** Export and deletion return asynchronous job IDs without status resources. Exports cannot be downloaded, revoked, or purged through the API and lack snapshots, manifests, artifacts, encryption, checksums, grants, or audit. Server and local deletion lifecycles conflict, per-device execution cannot be represented, signed local receipts overclaim erasure, account mutation can race deletion, no domain-disposition matrix exists, and backup tombstones are promised without persistence.

**Required closure.** Add durable status resources and cancellation; freeze recent-auth grants and coherent export snapshots; produce versioned encrypted export packages and grants; create immutable deletion plans and per-effect results; freeze or restrict account mutation during execution; model hosted deletion separately from each device command; report device execution rather than forensic erasure; define every data domain's delete/anonymize/retract/retain/legal-hold/backup behavior; persist and reapply tombstones before restored data becomes visible.

**Primary owners.** OpenAPI, PostgreSQL schema, state machines, local IPC, privacy/product contracts, policy/reason registries and data-rights conformance.

### SR-014 — Release authorization, compatibility, migration, and rollback

**Problem.** The object called a signed release set contains no signature envelope and declares its own threshold. TUF metadata and client trusted state are mostly absent. The manifest cannot identify coordinated components or target paths, compatibility is an opaque digest, state vocabularies disagree, migration-aware rollback is undefined, and generic local IPC cannot carry a verified installation plan. Platform updater configuration is being conflated with competitive eligibility.

**Required closure.** Use TUF root/delegated roles as the trust authority and make the release manifest an authenticated target; define component IDs, target paths, provenance and native-signing policies, update class, compatibility graph, migration chain, health checks, and rollback class; persist canonical TUF metadata and trusted client state; allow binary rollback only when prior software remains compatible with committed storage changes, otherwise roll forward or restore a verified snapshot; keep server eligibility independent from OS installation mechanics.

**Primary owners.** release-set and platform-profile schemas, PostgreSQL schema, state machines, local IPC, ADR-013, operations contract and release conformance.

### SR-015 — Privacy-safe data projection and current authorization

**Problem.** Several planned systems retain historical snapshot or event identities without a closed rule that current blocks, privacy changes, board removal, account deletion, moderation reversal, or identity consolidation immediately invalidate display and delivery. This affects ranking cursors, presence, notifications, social/board views, exports, and cached public projections.

**Required closure.** Separate immutable historical facts from current viewer authorization; bind every private projection to the relevant policy and relationship revisions; recheck authorization on every display or delivery boundary; invalidate cursors and cached grants on current privacy changes; use append-only correction/retraction manifests rather than rewriting accepted evidence.

**Primary owners.** privacy contract, ranking/social/presence/notification/export APIs and schemas, block and visibility policies, cache/cursor/grant profiles.

### SR-016 — Review, conformance, and launch evidence integrity

**Problem.** Current status and issue #41 review a stale head and only four findings. Several fixtures and suites are named as conformance or ranking evidence while checking schema presence, first transitions, or a shadow protocol. Named persistence owners are not always present. Symbolic race plans are not executable transaction proof. The repository can therefore become green while validating the wrong authority.

**Required closure.** Repin review to the current exact head after repairs; classify structural, semantic, prototype, and executable evidence separately; require every mutable concept to have one persistence owner and reachable lifecycle; reject missing tables and vocabulary drift; make suite names match what they execute; add PostgreSQL-backed, cross-language, platform, privacy, recovery, and adversarial evidence only after implementation is authorized; keep workflows manual/disabled until then.

**Primary owners.** `AGENTS.md`, `STATUS.md`, task catalog, schema inventory, P-1140E/F fixtures and validators, evaluation registry, issue #41 and future review PRs.

## Decisions closed by the audit

The following decisions are sufficiently supported and should be treated as planning defaults unless a later accepted decision explicitly supersedes them:

1. Deterministic controls are authoritative; SLM/statistical detection remains local-only, advisory, and post-launch.
2. OAuth proves provider control, not unique humanity; account, provider identity, and ranked identity are separate aggregates.
3. One person may have only one active resolved ranked identity, with private evidence, appeal, and no automatic summation of duplicate account scores.
4. Raw Token Burn is not coupled to pricing; Estimated Cash Burn is explicitly server interpreted.
5. Continuity is lineage-scoped, not device-row-scoped.
6. Client code never selects public evidence status, competitive eligibility, or estimated cost authority.
7. The shell, CLI, and dashboard are low-trust control clients and never receive claim-signing keys or source-content authority.
8. Generic ACP, OpenTelemetry, proxy, wrapper, and unknown-version integrations remain private analytics until an exact tuple is certified.
9. Only global leaderboard views are universally public by default; friend, rival, private, and unlisted board views require current viewer authorization.
10. Blocks are directional and separate from symmetric friendship state.
11. Presence is server-derived from qualifying device activity; private is a visibility policy.
12. Server inbox is notification authority; push/email are best-effort delivery hints.
13. Accepted claims and historical facts remain immutable; corrections, retractions, consolidation, deletion, and moderation reversals are append-only effects.
14. A local signed deletion receipt is an authenticated execution report, not proof of forensic erasure.
15. TUF/project authorization, platform-native signing, compatibility, and server competitive eligibility are separate release controls.

## User decisions still required before the affected contract can close

These do not block this consolidation change, but their answers must be recorded in the decision register before implementation of the affected domain:

1. **Duplicate-account score disposition.** Recommended: choose one surviving ranked identity; do not automatically add historical totals; reproject only independently valid, non-overlapping claims through an explicit correction manifest.
2. **Board privilege model.** Recommended: invitations grant member/viewer only; admin promotion and ownership transfer are separate recent-authenticated operations.
3. **Detected lineage fork.** Recommended: quarantine every post-fork branch, preserve accepted pre-fork claims, select/recover one installation where possible, resume through a new lineage generation, and keep the decision appealable.
4. **Presence timing.** Recommended: pulse every 30 seconds, idle after 90 seconds without a qualifying pulse, offline after 300 seconds; private remains separate visibility.
5. **High-impact idempotency retention.** Recommended: exact mutation results for at least 30 days; claim-batch results until safely superseded by a later acknowledged checkpoint; expired keys are rejected rather than silently reused.
6. **Delete-everything completion wording.** Recommended: hosted deletion and every local device are reported separately; never claim all local data erased while a device is offline, expired, unreachable, or unverified.
7. **Migration rollback boundary.** Recommended: automatic binary rollback only while the prior release remains read/write compatible; after an irreversible migration use roll-forward or a verified pre-migration snapshot.

## Dependency-ordered planning tasks

### 1. P-1140F-1 — Re-establish protocol and repository authority

- quarantine or remove the shadow protocol from normative paths;
- make the CDDL/exact vectors the sole VibeProof v1 authority;
- correct status, task, evaluation, documentation, and issue scope;
- register every mutable authority and persistence owner.

### 2. P-1140F-2 — Close identity, OAuth, lineage, replay, and recovery

- unify OAuth transaction and linked-identity lifecycle;
- add account/ranked-identity recovery and consolidation;
- make device continuity lineage-scoped;
- close challenge, checkpoint, rotation, fork, appeal, and reversal semantics.

### 3. P-1140F-3 — Close the local trust boundary and accounting inputs

- separate native process trust domains and authenticated IPC;
- define local persistence and generation ownership;
- introduce atomic compatibility tuples and certification lifecycle;
- close source observation, multi-observer deduplication, profile selection, and checked accounting.

### 4. P-1140F-4 — Close server product state and privacy projection

- repair idempotency and exact response replay;
- repair ranking generations, authorization, periods, and corrections;
- repair social/board ownership, presence, and notifications;
- repair export, deletion, retention, tombstones, and current-authorization invalidation.

### 5. P-1140F-5 — Close release trust and repin semantic review

- define TUF-backed release, component, compatibility, migration, rollback, and eligibility authorities;
- align API, SQL, state, events, reasons, policy, and fixtures;
- run only planning-safe validators until P-1104;
- pin a new exact review head and require zero open semantic P0/P1 findings before asking for implementation authorization.

## Closure criteria

P-1140F becomes `complete-planning` only when:

1. SR-005 through SR-016 are repaired in every affected normative owner and machine-readable contract.
2. No executable prototype contradicts or bypasses the sole normative protocol/accounting authority.
3. Every mutable aggregate has one reachable state machine, persistence owner, revision model, stable outcomes, and transaction boundary.
4. API, SQL, Protobuf/CDDL, fixtures, and state vocabularies cross-resolve without hidden security-critical mappings.
5. Privacy and authorization are current at every display and delivery boundary.
6. Structural validators pass without claiming semantic proof.
7. The exact repaired head receives an independent manual semantic review with zero open P0/P1 findings.
8. P-1104 remains a separate explicit user authorization after this gate closes.
