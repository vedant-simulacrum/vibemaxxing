# VibeMaxxing Implementation Handoff

Status: normative future implementation handoff; inactive until P-1140A–E pass and the user explicitly authorizes implementation.
Version: 4
Updated: 2026-07-23

## Purpose

This is the single build-order contract. It incorporates the July 23 repository audit, launch-policy decisions, privacy boundary, anti-cheat research and derived architecture.

It does not authorize implementation. Detailed reviewable units live in `PR_SIZED_WORK_BREAKDOWN.md`; current and future paths are distinguished in `REPOSITORY_LAYOUT.md`; execution-thread generation is governed by `ISSUE_GENERATION.md`.

## Entrance gate

Implementation may begin only when:

1. P-1140A through P-1140E are complete;
2. the repaired authoritative schemas, registries, references, policies and contracts are internally consistent;
3. the repository doctor and all planning-only validators pass from a clean checkout;
4. no open P0/P1 planning contradiction remains;
5. stale PR #17 is closed and no hidden branch competes with current authority;
6. the user explicitly opens implementation under P-1104.

Until then, current CDDL, JSON Schema, Protobuf, OpenAPI and SQL remain planning inputs and must not generate production code where marked blocked.

## Binding implementation constraints

### Privacy

- No prompt, output, transcript, code, diff, command, tool content, filename, path, project/repository name, credential, embedding, summary, classification, personal insight or content-derived hash reaches the server.
- Processes able to read raw source content have no network capability.
- Networked sync receives only fixed-schema aggregate claims.
- Review, moderation, observability and support tooling never expose local raw records.

### Competition

- Token Burn is the default raw metric.
- Estimated Cash Burn is a server-derived, versioned interpretation and always labelled estimated.
- Imported history is private analytics only.
- Accepted Standard and Hardened claims may both contribute globally.
- Local-model and delayed offline usage count when deterministically captured under a certified source profile.
- Evidence state is assigned by the server verifier, not the client.

### Identity

- OAuth proves provider-account control, not unique humanity.
- Launch supports GitHub and X; Google remains deferred until fully contracted.
- One active ranked identity per detected/resolved person is enforced through private account, device, recovery and enforcement lineage with review and appeal.
- Government ID and biometrics are not required by default.

### Launch scope

- Launch includes the complete core social product: global/friends/private/org/community/hacker-house leaderboards, all intended periods, profiles, friends, rivals, overtakes, movement, presence, boards, notifications, moderation and appeals.
- Country leaderboards are post-launch.
- SLM anti-cheat is post-launch research and not a launch dependency.

### Security architecture

- Default collector is unprivileged and per-user.
- No kernel anti-cheat.
- No mandatory VibeMaxxing model-call proxy.
- Deterministic accounting, canonicalization, signatures, sequences, replay, duplicates, continuity and hard eligibility are authoritative.
- Statistical/ML detectors start advisory and cannot alter totals or permanently ban.
- Official artifacts are digest-addressed, provenance-bound and delivered through rollback/freeze-resistant update metadata.

## Target system boundaries

### Rust-owned local and protocol components

1. `vibe-adapter-sdk`
   - capability manifest;
   - source probes;
   - typed source observations;
   - no network or device-key access.
2. `vibe-collector-core`
   - adapter lifecycle;
   - normalization;
   - accounting profiles;
   - deterministic rules;
   - deduplication;
   - local commitment state;
   - claim construction;
   - privacy egress filtering.
3. `vibe-device-identity`
   - protected per-installation signing keys;
   - enrollment, rotation, revocation, recovery and lineage;
   - platform assurance classification.
4. `vibeproof-protocol`
   - deterministic CBOR;
   - COSE signatures;
   - EvidenceClaim, CheckpointReceipt verification and local state;
   - exact test vectors.
5. `vibe-local-detector`
   - post-launch optional sandbox;
   - structured-feature mode first;
   - no network, shell, tools, keys or prose output.
6. native daemon/control/CLI/shell integration.

### Go-owned server components

1. authentication and linked identities;
2. ranked-identity integrity and recovery;
3. device enrollment and public-key lifecycle;
4. challenge issuance and atomic claim verification;
5. verifier appraisal and checkpoint receipts;
6. append-only claim/moderation/correction ledgers;
7. transactional outbox, aggregation and deterministic rebuild;
8. pricing interpretation and immutable alias resolution;
9. leaderboard views, snapshots, pagination and filters;
10. social graph, boards, presence and notifications;
11. moderation, appeals, export and server deletion;
12. operations/admin tooling.

### TypeScript-owned web components

- generated API/schema consumption;
- public and authenticated routes;
- evidence and privacy disclosure;
- full social/board/moderation UX;
- no independent business-policy reimplementation;
- no assumptions derived only from fixtures.

### PostgreSQL ownership

PostgreSQL constraints and transactions are correctness boundaries for:

- account/provider uniqueness;
- token/session families;
- device/key lineage;
- challenge consumption;
- claim idempotency/replay/forks;
- immutable facts and mutable projections;
- ranking views/snapshots/corrections;
- relationships, ownership and invitations;
- moderation/appeal/reversal;
- outbox and rebuild checkpoints.

## Repaired normative set required before coding

- Product/scope: project authority, scope freeze and product spec with country removed from launch.
- Privacy: privacy contract plus exact local/outbound data-stage schemas.
- Accounting: provider/runtime accounting profiles, canonical categories, time and pricing interpretation.
- VibeProof: EvidenceClaim/appraisal/checkpoint/rotation/correction protocol and exact CBOR/COSE profile.
- Compatibility: capability registry, digest/provenance certification and source ceilings.
- Native: process/privilege, typed IPC, storage, failure, recovery, platform and updater contracts.
- Identity: OAuth transaction/session/token-family, ranked identity and recovery contracts.
- Server: OpenAPI, PostgreSQL schema, atomic verifier, idempotency, ranking view and rebuild contracts.
- Social/integrity: typed relationship, board, presence, notification, moderation and appeal state machines.
- Operations: release-set, TUF, provenance, transparency, compromise and launch-evidence contracts.

## Build sequence after approval

### Phase 1 — contract workspaces and generated boundaries

Implement only after repaired schemas are frozen.

Deliverables:

- pinned Rust, Go, Node, package-manager, Protobuf/Buf, CDDL, OpenAPI, JSON Schema and migration toolchains;
- schema workspaces and generated bindings;
- reproducible generation and breaking-change detection;
- ordered PostgreSQL migrations replacing planning DDL;
- privacy-canary fixture framework;
- exact reason/policy registries.

Exit evidence:

- clean checkout generates byte-identical outputs;
- blocked/stale schemas cannot enter builds;
- no hand-maintained parallel domain types.

### Phase 2 — synthetic secure spine

Implement a fully synthetic end-to-end path before real adapters or social scope:

`typed source observation -> normalized accounting event -> deterministic rules -> encrypted local state -> local commitment -> signed EvidenceClaim -> isolated sync -> challenge -> atomic verifier -> VerifierAppraisal -> CheckpointReceipt -> immutable ledger/outbox -> aggregate -> ranking view -> accessible leaderboard row`.

Required proofs:

- privacy canaries never reach sync/server;
- invalid canonical form/signature/key/challenge rejects;
- exact replay is idempotent;
- conflicting replay, duplicate and fork quarantine;
- checkpoint and delayed-sync state are deterministic;
- rebuild output matches live aggregation.

### Phase 3 — local runtime and device boundary

Deliverables:

- encrypted local storage and migration/recovery;
- collector/sync separation;
- typed authenticated bounded IPC;
- device enrollment, key protection classes, rotation, revocation and recovery;
- append-only commitments and checkpoint handling;
- sleep/resume, clock change, crash, disk-full, offline and corrupt-state behavior;
- CLI status/control/diagnostics/privacy audit.

Platform order:

1. macOS per-user service/LaunchAgent plus menu-bar shell;
2. Windows per-user background process plus tray shell;
3. Linux user service plus optional tray and headless fallback.

No privileged helper is added without a separate accepted decision.

### Phase 4 — two-source vertical slice

Implement one local runtime and one cloud structured-usage source before broad compatibility.

Selection criteria:

- current official structured interface;
- stable model/source version discovery;
- deterministic accounting profile;
- representative local and cloud threat surfaces;
- feasible privacy and duplicate fixtures.

Deliverables per adapter:

- capability and permission manifest;
- exact artifact digest and provenance;
- source/version/platform/mode probes;
- accounting profile;
- duplicate-domain contract;
- positive, malformed, retry, cancellation, cache, reset, privacy and upgrade-break fixtures;
- support ceiling and emergency disable.

Exit evidence:

- both sources contribute end-to-end without forbidden egress;
- Imported history cannot enter competition;
- server appraisal, filters and local privacy preview work.

### Phase 5 — authentication, sessions and ranked identity

Deliverables:

- GitHub App web/device authorization;
- X Authorization Code + PKCE subject to provider availability;
- typed OAuth transaction storage and exact issuer/redirect/client-instance binding;
- web/native sessions, refresh token families, rotation, replay and revocation;
- DPoP decision and implementation if accepted;
- linked identity, provider loss, recovery and optional stronger factor flows;
- ranked identity eligibility, duplicate investigation, restriction, merge and appeal;
- no duplicate claim transfer or score reset through identity operations.

### Phase 6 — verifier, ranking and pricing completion

Deliverables:

- atomic claim transaction and durable idempotent response replay;
- verifier appraisal policy engine;
- immutable checkpoint, correction and moderation facts;
- transactional outbox;
- canonical `ranking_view_id` and period/scope/filter identity;
- snapshots, stable cursors, current-user rank and deterministic rebuild;
- immutable event-time model alias resolution;
- typed pricing rules and line-item Estimated Cash Burn interpretations.

### Phase 7 — social product state machines

Implement in dependency order:

1. profiles, privacy controls, handles and blocks;
2. friendships and rivals;
3. boards, memberships, roles, invitations and ownership transfer;
4. organizations, communities and hacker houses on board primitives;
5. collector-derived presence and audience projection;
6. typed notifications, preferences, grouping, hysteresis and retraction;
7. overtakes and rank movement from finalized matching ranking views;
8. moderation, restrictions, appeals and ranking reversal;
9. export and deletion with server/local separation.

Country features remain absent.

### Phase 8 — complete web and native UX

Deliverables:

- onboarding, login and native pairing;
- global/friends/group/org/community leaderboards for all launch periods;
- profiles, activity, agent/model and estimated-cost views;
- social, board and notification surfaces;
- devices, adapters, privacy, outbound audit, export and deletion settings;
- moderation and appeal surfaces;
- loading, empty, stale, offline, restricted, quarantined, blocked, unsupported, incompatible and maintenance states;
- WCAG 2.2 AA and performance budgets.

### Phase 9 — integrity hardening and adversarial beta

Execute deterministic and operational campaigns:

- forged/mutated claims;
- parser/canonicalization/algorithm confusion;
- replay storms, forks and duplicate races;
- clone, snapshot, backup/restore and key migration;
- clock rollback, suspend and counter reset;
- modified adapter/collector and compromised release;
- retries, cancellation, cache/reasoning and nested agents;
- long offline legitimate use and high-volume local inference;
- Sybil/collusion and shared-network false positives;
- privacy canaries in every boundary;
- moderation reversal and ranking rebuild.

The SLM is not required. Its later bakeoff uses synthetic/consented data and separate approval.

### Phase 10 — packaging, operations and open-source launch

Deliverables:

- signed/notarized packages;
- TUF root/roles and rollback/freeze-resistant metadata;
- release-set compatibility manifest;
- SBOM, provenance, transparency and consumer verification;
- secrets, environments, migrations and promotion;
- backups/restores, SLOs, alerts, incidents, key rotation and DR;
- restored product CI/security/dependency/evaluation/release gates;
- dependency, license, trademark, history and secret review;
- public documentation and reproducible releases;
- independent security/privacy review and launch gate.

Public release still requires explicit approval.

## Implementation evidence rules

Every PR identifies:

- work key and dependencies;
- owning decisions, ADRs, contracts and schemas;
- privacy/security impact and threat cases;
- migrations, compatibility and rollback;
- tests, benchmarks and generated artifacts;
- unsupported platforms/sources and evidence ceilings;
- unresolved risks and follow-up gates.

Placeholders, skipped tests, mock-only behavior, empty certifications and planning validators do not close implementation work.