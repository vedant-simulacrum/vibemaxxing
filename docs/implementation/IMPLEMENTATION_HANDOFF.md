# VibeMaxxing Implementation Handoff

Status: normative future implementation handoff; inactive until P-1140B–E pass and the user explicitly authorizes implementation.
Version: 5
Updated: 2026-07-23

## Purpose

This is the single build-order contract. It incorporates the repository alignment audit, machine-contract repair specification, D-001..D-061 implementation traceability, cross-platform completeness audit, launch-policy decisions, privacy boundary and anti-cheat architecture.

It does not authorize implementation. Reviewable units live in `PR_SIZED_WORK_BREAKDOWN.md`; current/future paths are distinguished in `REPOSITORY_LAYOUT.md`; execution-thread generation is governed by `ISSUE_GENERATION.md`.

## Mandatory pre-read

Before implementation work, read:

1. `AGENTS.md`;
2. project authority/status/documentation map;
3. `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`;
4. all files under `docs/planning/decision-traceability/`;
5. `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`;
6. decision/task registers and relevant ADRs/contracts/schemas;
7. this handoff and the PR-sized work breakdown.

## Entrance gate

Implementation may begin only when:

1. P-1140B through P-1140E are complete;
2. every accepted implementation-bearing decision has an owner, work unit, schema/state owner, platform scope and evidence gate;
3. superseded decisions have no active implementation path;
4. exact launch OS/version/architecture/distribution/environment profiles are frozen;
5. repaired schemas, registries, references, policies and contracts are internally consistent;
6. repository doctor and all planning-only validators pass from a clean checkout;
7. no open P0/P1 planning contradiction remains;
8. the user explicitly opens implementation under P-1104.

Until then, current CDDL, JSON Schema, Protobuf, OpenAPI and SQL remain planning inputs and must not generate production code where marked blocked.

## Binding implementation constraints

### Privacy

- No prompt, output, transcript, code, diff, command, tool content, filename, path, project/repository name, credential, embedding, summary, classification, personal insight or content-derived hash reaches the server.
- Processes able to read raw source content have no network capability.
- Networked sync receives only fixed-schema aggregate claims.
- Review, moderation, observability and support tooling never expose local raw records.

### Competition

- Token Burn is the default raw metric.
- Estimated Cash Burn is server-derived, versioned and always labelled estimated.
- Imported history is private analytics only.
- Accepted Standard and Hardened claims may both contribute globally.
- Local-model and delayed offline usage count when deterministically captured under a certified profile.
- Evidence state is assigned by the server verifier, not the client.

### Identity

- OAuth proves provider-account control, not unique humanity.
- Launch supports GitHub and X; Google remains deferred.
- One active ranked identity per detected/resolved person is enforced through private account, device, recovery and enforcement lineage with review and appeal.
- Government ID and biometrics are not required by default.

### Launch scope

- Launch includes the complete core social product except country leaderboards.
- Country leaderboards and SLM anti-cheat are post-launch.
- A platform/source is advertised only at the exact exercised support profile.

### Security and lifecycle

- Default collector is unprivileged and per-user.
- No kernel anti-cheat or mandatory VibeMaxxing inference proxy.
- Deterministic accounting, canonicalization, signatures, sequences, replay, duplicates, continuity and eligibility are authoritative.
- Statistical/ML detectors are advisory and cannot alter totals or permanently ban.
- Official artifacts are digest-addressed, provenance-bound and delivered through rollback/freeze-resistant metadata.
- `vibemaxxing-daemon` is OS-supervised and always-on within the declared platform service context; shell state, collection pause, sync pause, network loss and degraded child state do not stop it.

## Component ownership

### Rust local/protocol

- `vibe-adapter-sdk`: manifests, probes and typed source observations; no network/device-key access.
- `vibe-collector-core`: normalization, accounting, deterministic rules, dedup, commitments, claims and privacy filtering.
- `vibe-device-identity`: keys, enrollment, rotation, revocation, recovery and platform assurance.
- `vibeproof-protocol`: deterministic CBOR, COSE, claims, appraisals/receipts verification and vectors.
- `vibemaxxing-daemon`: service lifecycle, supervision, local control and update coordination without raw-content monolith behavior.
- `vibeproof-sync`: networked safe-claim sync with no source-content access.
- CLI and shell integrations.
- optional post-launch local detector sandbox.

### Go server

- OAuth, sessions, linked and ranked identities;
- device/key enrollment and lineage;
- challenge issuance and atomic verification;
- verifier appraisal and checkpoint receipts;
- immutable claim/moderation/correction ledgers;
- transactional outbox, aggregation and rebuild;
- pricing interpretation and alias resolution;
- ranking views, snapshots, cursors and filters;
- social graph, boards, presence and notifications;
- moderation, appeals, export and server deletion;
- operations/admin tooling.

### TypeScript web

- generated contract consumption;
- public/authenticated routes;
- evidence/privacy disclosure;
- social/board/moderation UX;
- no independent business-policy reimplementation;
- no fixture-only assumptions in production paths.

### PostgreSQL

Constraints and transactions own account/provider uniqueness, token families, device/key lineage, challenge use, idempotency/replay/forks, immutable facts/projections, ranking views/corrections, relationships/ownership, moderation/reversal and outbox/rebuild checkpoints.

## Repaired normative set required before coding

- product/scope and country removal;
- privacy and exact local/outbound stages;
- accounting profiles, canonical categories, time and pricing;
- VibeProof claim/appraisal/checkpoint/rotation/correction protocol;
- capability registry and digest/provenance certification;
- native process, always-on lifecycle, privilege, IPC, storage, recovery and updater contracts;
- OAuth/session/token-family/ranked-identity contracts;
- OpenAPI, PostgreSQL, atomic verifier, idempotency and ranking-view contracts;
- typed social, presence, notification, moderation and appeal state machines;
- TUF/release-set/provenance/transparency/compromise contracts;
- complete decision traceability and platform baseline registry.

## Build sequence after approval

### Phase 1 — contract workspaces

Pin Rust, Go, Node, package manager, Buf/Protobuf, CDDL, OpenAPI, JSON Schema and migration tools. Create authoritative workspaces, generated bindings, drift checks, ordered migrations, reason/policy registries and privacy-canary fixtures.

Exit: clean generation is byte-identical; blocked schemas cannot enter builds; no parallel hand-maintained domain types.

### Phase 2 — synthetic secure spine

Implement:

`typed source observation -> normalized event -> accounting -> deterministic rules -> encrypted local state -> commitment -> signed claim -> isolated sync -> challenge -> atomic verifier -> appraisal -> checkpoint receipt -> immutable ledger/outbox -> aggregate -> ranking view -> accessible row`.

Prove privacy-canary blocking, canonical/signature/key/challenge rejection, exact replay idempotency, conflicting reuse/fork quarantine, deterministic delayed sync and rebuild equivalence.

### Phase 3 — always-on local runtime and device boundary

Implement:

- OS service registration before install success;
- always-on daemon desired-state and two-level supervision;
- collector/sync process separation and typed authenticated IPC;
- encrypted storage, migrations, crash consistency and bounded queues;
- protected keys, enrollment, rotation, revocation, recovery and requalification;
- local commitments and server checkpoints;
- shell-independent health/control and CLI parity;
- sleep/resume, logout/login, reboot, network loss, disk full, corruption, permission loss, update and rollback behavior;
- exact platform lifecycle/evidence status in diagnostics.

Platform implementation order:

1. macOS declared architecture/version profiles;
2. Windows declared architecture/version profiles;
3. Linux declared distribution/desktop/headless profiles;
4. WSL profile;
5. container profile;
6. CI/ephemeral profile.

No privileged helper or machine-wide service is added without an accepted decision.

### Phase 4 — two-source vertical slice

Select one local runtime and one cloud structured-usage source using current official interfaces. Each adapter ships manifest, digest/provenance, probes, accounting profile, duplicate contract, positive/adversarial/privacy/upgrade fixtures, support ceiling and emergency disable.

Exit: both sources work end-to-end without forbidden egress; imports cannot rank; appraisal, filters and privacy preview work.

### Phase 5 — authentication, sessions and ranked identity

Implement GitHub App web/device authorization, X Authorization Code plus PKCE, typed OAuth transactions, web/native token families, replay/revocation, linked identities, recovery, optional stronger factors, ranked eligibility, duplicate investigation, restriction, consolidation and appeal. Identity operations never duplicate claims or reset score history.

### Phase 6 — verifier, ranking and pricing

Implement atomic claim transaction, stored idempotent outcomes, appraisal policy, immutable receipts/corrections/moderation facts, outbox, canonical `ranking_view_id`, snapshots/cursors/current rank/rebuild, immutable alias resolution and line-item estimated pricing.

### Phase 7 — social state machines

Implement profiles/privacy/handles/blocks, friendships/rivals, boards/roles/invitations/ownership, organizations/communities/hacker houses, collector-derived presence, typed notifications, overtakes/movement, moderation/appeals/reversal and separate server/local export/deletion. Country remains absent.

### Phase 8 — complete UX

Implement onboarding/pairing, all launch leaderboards, profiles/activity/agent/model/estimated-cost views, social/boards/notifications, devices/adapters/privacy/audit/export/deletion, moderation/appeals and complete exceptional states. Meet WCAG 2.2 AA and declared performance/resource budgets on every advertised platform profile.

### Phase 9 — integration and adversarial beta

Execute protocol, replay, fork, clone, restore, accounting, identity, social, notification, moderation, privacy and release campaigns.

For every advertised platform execute install, service registration, shell crash, daemon crash/hang, child crash loop, login/logout, reboot, sleep/hibernate, network loss, permission/key-store/storage failure, update/rollback, background-service disable/repair and uninstall. Verify no queued-claim loss, duplicate score, continuity reset or privacy leakage.

The SLM is not required.

### Phase 10 — packaging, operations and launch

Produce signed/notarized packages, TUF metadata, release-set graph, SBOM/provenance/transparency, consumer verification, environments/secrets/migrations, backups/restores, SLOs/alerts/incidents/DR, product CI/security/eval/release gates, legal/governance review, public docs and reproducible releases.

A platform enters public support only after every gate in `CROSS_PLATFORM_COMPLETENESS_AUDIT.md` passes for its exact profile. Public release still requires explicit approval.

## Implementation evidence rules

Every PR identifies:

- work key and dependencies;
- every mapped decision ID;
- owning ADRs/contracts/schemas;
- platform profiles affected;
- privacy/security impact and threats;
- database/API/wire compatibility and migrations;
- rollback/disable path;
- tests, benchmarks, fixtures and generated artifacts;
- support/evidence ceilings;
- unresolved risk.

A PR cannot close an accepted decision unless its matrix row has implementation and executable evidence links. Placeholders, skipped tests, mocks, empty certifications and planning validators do not close implementation work.
