# PR-Sized Implementation Work Breakdown

Status: normative future implementation planning; inactive until P-1140A–E and P-1104 pass.
Updated: 2026-07-23

Each unit must be independently reviewable, tested, migration-aware and reversible where possible. Units may be combined only when their risk, ownership and rollback remain clear.

Country leaderboards and the SLM detector are not launch implementation units. Country is post-launch. SLM work is a later research/bakeoff track.

## Dependency rules

- Do not implement against schemas blocked by P-1140.
- Foundation precedes the synthetic secure spine.
- The synthetic spine precedes real adapters and broad UX.
- Device/continuity and server-verifier units precede competitive ranking.
- One local and one cloud source precede broad adapter expansion.
- Identity/session correctness precedes social write operations.
- Ranking-view identity precedes overtakes, movement and notifications.
- Moderation/reversal precedes public competitive beta.
- Packaging/release integrity precedes external distribution.

## Epic F — contract workspaces and generation

### F-01 Pin implementation toolchains

- Rust 2024 toolchain and components;
- Go version and module policy;
- Node and package manager;
- Buf/Protobuf, CDDL, OpenAPI, JSON Schema and migration tooling;
- clean-checkout version verification.

Acceptance: unsupported toolchain versions fail with actionable diagnostics.

### F-02 Create authoritative schema workspaces

- repaired local event schemas;
- repaired VibeProof CDDL and COSE profile;
- internal Protobuf;
- OpenAPI;
- SQL migrations;
- reason and policy registries.

Acceptance: blocked historical schemas are not imported by production packages.

### F-03 Generated binding pipeline

Generate Rust, Go and TypeScript bindings from authoritative sources.

Acceptance: clean regeneration is byte-identical; hand-edited generated files fail checks.

### F-04 Breaking-change classification

Classify source-compatible, wire-compatible, migration-required and protocol-major changes.

Acceptance: representative breaking fixtures are detected before merge.

### F-05 Privacy-canary framework

Seed forbidden values across prompts, outputs, paths, repos, credentials, tool fields, raw aliases and content hashes.

Acceptance: any canary reaching network, telemetry, logs, notifications or review data fails the suite.

### F-06 Checked numeric/time primitives

Provide cross-language safe token, sequence, timestamp, duration and money primitives.

Acceptance: overflow, JavaScript precision loss and PostgreSQL range mismatch fixtures fail closed.

## Epic P — VibeProof protocol core

### P-01 Rust EvidenceClaim domain model

Implement the repaired typed claim without public evidence state or pricing authority.

### P-02 Deterministic CBOR profile

Implement exact map ordering, shortest integers, definite lengths, tag policy, depth and size limits.

### P-03 COSE key and signature profile

Implement protected headers, key IDs, Ed25519/EdDSA, external AAD and exact signed-byte rules.

### P-04 Go independent decoder/verifier

No shared encoder logic with Rust beyond normative fixtures.

### P-05 TypeScript diagnostic decoder

Read-only inspection for developer/privacy tooling; never authoritative verification.

### P-06 Exact-byte golden vectors

Positive vectors for claims, receipts, appraisals, rotations, corrections and gaps.

### P-07 Malformed parser corpus

Duplicate keys, non-minimal integers, wrong tags, unprotected algorithm, truncation, nesting, allocation bombs and mutation.

### P-08 VerifierAppraisal model

Server-owned dimensions, profile ID, public state, outcome, reasons and policy version.

### P-09 CheckpointReceipt model

Bind device lineage, accepted local head, server state, receipt sequence and policy.

### P-10 KeyRotationTransition

Typed old/new authorization, boundary sequence, recovery variant and server transaction.

### P-11 CorrectionRecord

Server-authorized append-only correction and supersession semantics.

### P-12 Atomic batch envelope

One normative batch/challenge/replay model with no partial ambiguity.

Acceptance for P epic: independent Rust/Go verification agrees byte-for-byte and all malformed vectors fail without resource exhaustion.

## Epic A — accounting and deterministic integrity

### A-01 Accounting profile registry

Typed provider/runtime/API-mode/model/tokenizer profiles with effective versions.

### A-02 Canonical token categories

Mutually exclusive competitive components and source-specific containment mappings.

### A-03 Source-total reconciliation

Prevent addition of totals that already include cache, reasoning, modalities or children.

### A-04 Retry/cancellation accounting

Distinguish distinct model execution, provider-internal retry, aborted stream and unknown remainder.

### A-05 Nested agent accounting

Parent/child attribution and duplicate prevention for orchestrators and subagents.

### A-06 Cache and reasoning profiles

Provider-specific semantics and golden fixtures.

### A-07 Local tokenizer profile

Exact model/tokenizer digest, algorithm/version and reconstruction ceiling.

### A-08 Runtime-native profile

Local inference counters, generated token IDs and runtime-generation semantics.

### A-09 Deterministic rules engine

Versioned rules, fatal contradictions, quarantine reasons and diagnostics.

### A-10 Clock and generation rules

Monotonic domain, suspend/resume, process/runtime reset and rollback handling.

### A-11 Duplicate-domain engine

Keyed non-content structural domains with collision/conflict behavior.

### A-12 Throughput envelope registry

Transparent source/model/runtime physical and protocol bounds, initially advisory unless impossible.

### A-13 Pricing rule engine

Server-side immutable pricing datasets, alias resolution, conditions, line items, rounding and provenance.

Acceptance for A epic: representative cloud/local fixtures reconcile deterministically without double counting or client-controlled cost interpretation.

## Epic N — native collector and local state

### N-01 SourceObservation typed IPC

Replace arbitrary JSON/bytes with bounded generated messages.

### N-02 Collector process

Adapter supervision, normalization, accounting and deterministic rules; no network.

### N-03 Sync process

Challenge, claim submission, receipts, retries and sessions; no source-content access.

### N-04 Daemon/control process

Lifecycle, configuration, health and capability routing without becoming a content monolith.

### N-05 Authenticated local IPC

Peer identity, ACLs, challenge-response, version negotiation, limits and replay controls.

### N-06 Encrypted local database

Separate tables/stores for source cursors, normalized facts, commitments, pending claims, receipts, audit and diagnostics.

### N-07 Append-only commitment store

Local sequence, previous/current head, monotonic generation and checkpoint receipt.

### N-08 Crash consistency

Transactional writes across normalized event, rule result, commitment and queue.

### N-09 Offline queue and backpressure

Bounded storage, batching, retry, expiry and user-visible backlog.

### N-10 Disk-full behavior

Stop safely without corrupting prior state or silently dropping ranked activity.

### N-11 Sleep/resume and clock-change recovery

Deterministic generation changes and diagnostics.

### N-12 Corrupt-state recovery

Quarantine, signed gap declaration where allowed and explicit new lineage when required.

### N-13 Local outbound audit ledger

Exact sent fields, claim/receipt status and local references without content.

### N-14 Privacy preview

Render the exact outbound claim before/after serialization.

### N-15 CLI core

Install, status, start/stop, pause collection/sync, adapters, privacy audit, export/delete, update/rollback and doctor.

## Epic D — device identity and platform keys

### D-01 Device-lineage schema

Separate installation, key and lineage identity.

### D-02 Enrollment protocol

Bind account, native session, key, collector build and challenge.

### D-03 macOS key backend

Keychain/Secure Enclave capability detection and migration behavior.

### D-04 Windows key backend

CNG/TPM non-exportable path with DPAPI fallback classification.

### D-05 Linux key backend

TPM/keyring/Secret Service capability matrix and disclosed fallback ceiling.

### D-06 Rotation flow

Old/new authorization and exact sequence boundary.

### D-07 Lost-key recovery

Revoke old key, create new lineage/state and prevent silent trust inheritance.

### D-08 Restore/clone detection inputs

Backup, home-directory restore, credential migration and VM snapshot signals without stable public hardware IDs.

### D-09 Requalification policy

Recovered/migrated lineages cannot inherit Hardened automatically.

### D-10 Optional attestation adapters

Issuer-specific evidence input, nonce, freshness, expiry, revocation and policy—never a blanket truth flag.

## Epic S — server secure spine

### S-01 Go modular service skeleton

HTTP, auth callbacks, verifier module, workers and admin CLI around PostgreSQL.

### S-02 PostgreSQL migration baseline

Ordered migrations, roles, constraints and rollback/restore plan.

### S-03 Device/key persistence

Lineages, keys, status, attestation and recovery events.

### S-04 Challenge service

Random account/device-bound single-use challenges with expiry and outstanding limits.

### S-05 Idempotency ledger

Scoped key, authenticated principal, request fingerprint, stored outcome, expiry and conflict behavior.

### S-06 Atomic claim acceptance transaction

Decode, signature, key, challenge, sequence, checkpoint, certification, accounting, duplicate, privacy, eligibility, appraisal, ledger, receipt and outbox in one transaction.

### S-07 Exact replay response

Return stored success/rejection for byte-identical retry.

### S-08 Conflict/fork quarantine

Different bytes reusing claim/sequence/challenge/commitment/domain create registered conflict outcomes.

### S-09 Privacy-safe rejection records

Retain digest, bounded metadata and reasons; no invalid raw payload by default.

### S-10 Immutable claim/appraisal/checkpoint ledger

Facts never mutate; projections and case states are separate.

### S-11 Transactional outbox

Commit ranking/social events only after accepted transaction.

### S-12 Worker idempotency and checkpoints

Crash-safe `FOR UPDATE SKIP LOCKED` processing and deterministic versions.

### S-13 Synthetic ranking projection

Aggregate accepted facts into a canonical ranking view.

### S-14 Rebuild equivalence

Replay facts/corrections and hash-compare before projection promotion.

## Epic V — first two real sources

Source choices must be approved from current official interfaces before implementation.

### V-01 Local runtime selection spike

Compare Ollama, llama.cpp and vLLM on structured counters, token IDs, version identity and testability.

### V-02 Cloud source selection spike

Compare current OpenAI, Anthropic and Google structured usage interfaces without treating metadata as signed receipts.

### V-03 Local adapter implementation

Manifest, probe, observation, accounting profile, duplicate domain and fixtures.

### V-04 Cloud adapter implementation

Manifest, probe, local response metadata observation, accounting profile, duplicate domain and fixtures.

### V-05 Certification runner

Exact artifact/source/version/platform/mode test bundle and immutable result digest.

### V-06 Support registry publication

Generate honest support ceiling from exercised results.

### V-07 Emergency disable/sunset

Signed registry state, user diagnostics and downgrade behavior.

### V-08 Upgrade-break fixtures

Unknown or changed source versions fail closed for stronger profiles.

## Epic I — authentication, sessions and ranked identity

### I-01 GitHub App web authorization

State, issuer/client/redirect binding, minimal scopes and callback transaction.

### I-02 GitHub native device authorization

Polling limits, user-code lifecycle, local device binding and exchange.

### I-03 X Authorization Code + PKCE

Current-provider capability gate, S256 verifier storage and callback validation.

### I-04 OAuth transaction schema

Encrypted retrievable verifier where needed, hashes for lookup, intended action, browser/native instance and expiry.

### I-05 Web session families

Secure cookies, rotation, CSRF, replay and revoke-all.

### I-06 Native token families

Short access, bounded refresh, device binding, rotation and replay response.

### I-07 DPoP implementation decision

Operational bakeoff and ADR; implement only if benefits exceed compatibility cost.

### I-08 Linked identity state machine

Link, unlink, provider loss, compromise and conflict.

### I-09 Optional stronger factors

Passkeys/security keys for high-impact actions; no biometric storage.

### I-10 Recovery flow

Linked provider, stronger factor, recovery code, trusted session and human appeal ordering.

### I-11 Ranked eligibility

Provider uniqueness, accepted policy and abuse checks.

### I-12 Duplicate-identity case model

Private signals, corroboration, reviewer controls and no single-IP/device decisions.

### I-13 Restriction/consolidation

Canonical identity, duplicate account unranking, claim non-duplication and history continuity.

### I-14 Anti-reenrollment retention

Minimal, disclosed, access-controlled and legally reviewed.

## Epic R — ranking, periods, corrections and pricing

### R-01 Canonical ranking_view_id

Immutable metric, scope, period, evidence, model/agent and policy identity.

### R-02 Period registry

UTC day/week/month/year/lifetime and immutable seasons.

### R-03 Server-anchored event interval

Receipt/checkpoint/source uncertainty and delayed-sync assignment.

### R-04 Score fact/delta model

Accepted claim references, correction deltas and no in-place mutation.

### R-05 Snapshot generation

Consistent leaderboard pages and current-user rank.

### R-06 SQL rank semantics

`rank()` gaps and presentation tie-breakers.

### R-07 First-reached semantics

Define behavior under correction, rebuild and repeated crossings.

### R-08 Keyset pagination

Cursor binds ranking view, snapshot and row identity.

### R-09 Evidence filters

All accepted, Hardened-only and board minimum profiles without changing raw score.

### R-10 Pricing interpretation records

Dataset/rule/line-item/matched-condition/rounding provenance.

### R-11 Immutable alias resolution

Event-time provider/model identity persists through rebuild.

### R-12 Unpriced/local compute UX data

Never zero-dollar implication.

## Epic G — profiles and social graph

### G-01 Handle assignment ledger

Normalization, reservation, rename, redirect, non-reuse and deletion privacy.

### G-02 Profile privacy matrix

Independent controls for metrics, history, models, friends, memberships and presence.

### G-03 Block state machine

Immediate relationship/presence/notification effects and no automatic restore.

### G-04 Friend request state machine

Canonical unordered pair constraints, crossed requests, expiry and abuse limits.

### G-05 Friendship edge model

One undirected relationship, no reverse duplicates.

### G-06 Rival state machine

Private default, suggestions and comparable ranking views.

### G-07 Board aggregate root

One ownership authority and immutable board identity.

### G-08 Board membership/role state machine

Owner/admin/moderator/member/viewer, transfer and last-owner rules.

### G-09 Board invitation state machine

Expiry, cancellation, block interaction and idempotency.

### G-10 Board policy versions

Prospective metric, evidence, period, membership and eligible-source rules.

### G-11 Organization/community/hacker-house specialization

Reuse board primitives; no parallel governance model.

## Epic L — presence, movement and notifications

### L-01 Qualifying activity signal

Collector-derived, signed/accepted structural activity only.

### L-02 Presence lease transaction

Device/account binding, renewal, expiry and revocation.

### L-03 Audience/privacy projection

Viewer-specific visibility, board overrides and blocks.

### L-04 Multi-device merge

Strongest allowed state without source/project detail.

### L-05 Overtake event

Strict score crossing within identical finalized ranking view.

### L-06 Rank movement event

Snapshot-to-snapshot comparison with correction handling.

### L-07 Typed notification schema

No open JSON payloads or privacy-unsafe fields.

### L-08 Preferences and quiet hours

Per-type/channel controls and mandatory security notices.

### L-09 Deduplication/hysteresis/grouping

Stable event identity and anti-flap behavior.

### L-10 Retraction/correction

Withdraw or replace notifications after moderation/rebuild.

## Epic M — moderation, appeals and lifecycle

### M-01 Moderation case aggregate

Bind subject, claims, periods, ranking views, reasons and policy versions.

### M-02 Progressive actions

Downgrade, quarantine, exclusion, temporary restriction, device revocation and suspension.

### M-03 Automated authority limits

No model/statistical permanent ban or total mutation.

### M-04 Reviewer authorization/audit

Least privilege, recent auth, access logging and dual control where needed.

### M-05 Appeal state machine

Submission, information, review, outcome, expiry and service targets.

### M-06 Reversal record

Immutable reversal and exact affected facts/views.

### M-07 Ranking rebuild after reversal

Deterministic restoration and notification correction.

### M-08 Export workflow

Typed scope, coherent snapshot, manifest, recent auth, encrypted delivery and expiring grant.

### M-09 Server deletion workflow

Immediate hiding/revocation, cooling-off, deletion/anonymization and aggregate rebuild.

### M-10 Local deletion workflow

Per-device command and receipt; never falsely promised by server alone.

## Epic U — web and native UX

### U-01 Native onboarding and permissions
### U-02 Account login and device pairing
### U-03 Daemon/collector/sync health
### U-04 Adapter discovery and support ceilings
### U-05 Exact outbound privacy inspection
### U-06 Global leaderboard and period/filter views
### U-07 Friends leaderboard and social home
### U-08 Board/org/community/hacker-house leaderboards
### U-09 Public profile and evidence disclosure
### U-10 Personal activity/model/agent views
### U-11 Estimated Cash Burn explanation and pricing provenance
### U-12 Friends, rivals, overtakes and movement surfaces
### U-13 Presence controls and privacy
### U-14 Notifications center and preferences
### U-15 Board creation/administration
### U-16 Devices, identities and sessions
### U-17 Moderation/restriction/appeal surfaces
### U-18 Export and deletion surfaces
### U-19 Exceptional-state matrix
### U-20 Accessibility and performance completion

Acceptance for each UX PR: generated contracts, no fixture-only policy, loading/empty/error/offline/restricted states, accessibility and privacy review.

## Epic O — packaging, updater and operations

### O-01 macOS service/menu-bar packaging
### O-02 Windows background/tray packaging
### O-03 Linux user-service/headless packaging
### O-04 Signed installers and uninstall verification
### O-05 TUF trust root and role policy
### O-06 Release-set manifest and compatibility graph
### O-07 Atomic update and interrupted recovery
### O-08 Rollback/freeze/compromised-version handling
### O-09 SBOM and provenance generation
### O-10 Signature transparency and consumer verification
### O-11 Environment/secrets/migration promotion
### O-12 Observability allowlist and canary blocking
### O-13 Backup/restore and disaster recovery
### O-14 SLOs, alerts, incident and key-compromise playbooks
### O-15 Restore product CI/security/dependency/evaluation/release gates
### O-16 Independent security/privacy review
### O-17 Open-source history, secret, license and trademark review
### O-18 Reproducible public release and launch gate

## Adversarial beta campaigns

Separate PRs/campaign records are required for:

- canonicalization and parser attacks;
- signature/key/header confusion;
- exact/conflicting replay and race storms;
- device fork, snapshot, clone, restore and migration;
- modified adapter/collector and fake source events;
- clock rollback, suspend, runtime reset and disk failure;
- retry/cancellation/cache/reasoning/nested accounting;
- long offline legitimate usage;
- extreme legitimate local-model volume;
- identity duplicates, collusion and shared-network false positives;
- social/board authorization abuse;
- notification/privacy leakage;
- moderation reversal and rebuild;
- update/signing compromise;
- privacy canaries across all processes and server surfaces.

## Post-launch tracks

### PL-01 Country leaderboard research

Semantics, season-frozen affiliation, cohort privacy, switching, historical attribution and moderation. No launch dependency.

### PL-02 SLM detector bakeoff

Synthetic/consented corpus; deterministic and classical baselines; structured-feature model first; optional raw-local sandbox; prompt-injection and evasion testing; predeclared false-positive ceiling. No authority unless separately approved.

## PR acceptance contract

Every PR names:

- unit ID and dependencies;
- decisions, ADRs, contracts and schemas;
- privacy/security impact and threat cases;
- database/API/wire compatibility and migrations;
- rollback or disable path;
- tests, benchmarks, fixtures and generated artifacts;
- supported platforms/sources and evidence ceilings;
- unresolved risks.

Placeholder-only PRs, skipped tests, mocks, empty certifications and planning validators do not close implementation work.