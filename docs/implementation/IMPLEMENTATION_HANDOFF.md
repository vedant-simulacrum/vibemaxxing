# VibeMaxxing Implementation Handoff

Status: normative future implementation handoff; inactive until P-1140B–E pass and the user explicitly authorizes implementation.
Version: 8
Updated: 2026-07-24

## Purpose

This is the single build-order contract. It incorporates the repository alignment audit, machine-contract repair specification, D-001..D-069 traceability, frozen cross-platform audit, launch decisions, privacy boundary, anti-cheat architecture, optional privileged supervision and mandatory automatic updates.

It does not authorize implementation. Reviewable units live in `PR_SIZED_WORK_BREAKDOWN.md`; current/future paths are distinguished in `REPOSITORY_LAYOUT.md`; execution-thread generation is governed by `ISSUE_GENERATION.md`.

## Current handoff health

This document is structurally comprehensive but **not implementation-ready**. It describes the intended build order; it does not prove that the contracts consumed by that build order are coherent.

| Layer | Current state | Handoff consequence |
|---|---|---|
| Product authority and launch scope | Accepted and consolidated | Bind implementation to current decisions; do not revive country launch scope, mandatory proxying, kernel anti-cheat or a launch SLM |
| Evidence, privacy and accounting | P-1140B complete-planning | Typed local stages, accounting profiles, appraisal authority, lineage, pricing and egress boundaries are frozen planning inputs; no implementation evidence is claimed |
| VibeProof wire protocol | P-1140C complete-planning | Closed CDDL, deterministic CBOR/COSE, continuity/replay state and fixed vectors are frozen planning inputs; independent codecs remain P-1140E work |
| Identity, API, SQL, ranking, social, native and release state | P-1140D candidate; validation pending | The authoritative state/platform registry, endpoint-specific OpenAPI, repaired SQL, typed social events and release/ranking/export schemas are coherent candidate inputs; do not implement until exact-head validation and P-1140E |
| Cross-contract validation | P-1140E dependency-blocked | No current clean-checkout result can certify the future implementation handoff |
| Product code | Prototype/seeds only | Hosted fixture UI is a runnable prototype; API, Rust core, protocol, database, collectors, packaging and operations are not implemented |

Before P-1104 can be proposed, maintainers must reconcile this file and `PR_SIZED_WORK_BREAKDOWN.md` against the final repaired schemas and state machines, remove or reclassify stale completion claims, attach clean-checkout validation to the exact final head, and record any remaining P0/P1 contradiction as blocking.

### Concurrent branch handoff rule

Branch-local work is not canonical handoff state. The ADR-014 repair is merged through PR #31; the UI application-lockdown branch must now be updated onto that baseline, preserve the stricter workflow boundary and repository-doctor invariants, and rerun checks on the reconciled exact head. The authoritative status is updated only after merge.

## Mandatory pre-read

1. `AGENTS.md`;
2. project authority/status/documentation map;
3. `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`;
4. all files under `docs/planning/decision-traceability/`;
5. `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`;
6. `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` and the state/platform registries;
7. ADR-010 through ADR-014;
8. decision/task registers and relevant contracts/schemas;
9. this handoff and the PR-sized work breakdown.

## Entrance gate

Implementation may begin only when:

1. P-1140B through P-1140E are complete;
2. every accepted implementation-bearing decision has an owner, work unit, schema/state owner, platform scope and evidence gate;
3. superseded decisions have no active implementation path;
4. repaired schemas, registries, references, policies and contracts are internally consistent;
5. repository doctor and all planning-only validators pass from a clean checkout;
6. no open P0/P1 planning contradiction remains;
7. the user explicitly opens implementation under P-1104.

Platform scope is already frozen under D-062 through D-069. No implementation may reopen or narrow it silently.

## Binding product constraints

### Privacy

- No prompt, output, transcript, code, diff, command, tool content, filename, path, project/repository name, credential, embedding, summary, classification, personal insight or content-derived hash reaches the server.
- Processes able to read raw source content have no network capability.
- Networked sync receives only fixed-schema aggregate claims.
- Review, moderation, observability, support and privileged-supervisor tooling never expose local raw records.

### Competition

- Token Burn is the default raw metric.
- Estimated Cash Burn is server-derived, versioned and always labelled estimated.
- Imported history is private analytics only.
- Accepted Standard and Hardened claims may contribute globally.
- Local-model and delayed offline usage count when deterministically captured under a certified profile.
- WSL, containers and CI are globally eligible by default at the verifier-awarded evidence level.
- Evidence state is assigned by the server verifier, not the client.

### Identity

- OAuth proves provider-account control, not unique humanity.
- Launch supports GitHub and X; Google remains deferred.
- One active ranked identity per detected/resolved person is enforced through private account, device, recovery and enforcement lineage with review and appeal.
- Government ID and biometrics are not required by default.

### Platform scope

- macOS: Apple silicon `arm64` and Intel `x86_64`.
- Windows: native x64 and native ARM64 across maintained desktop and applicable Server profiles.
- Linux: maintained desktop, headless and remote profiles under exact distro/package/architecture certification.
- WSL, containers and CI/ephemeral runners: launch-supported environment profiles.
- Android, iOS, iPadOS and ChromeOS: no native implementation scope.
- Hosted web remains an ordinary browser surface.

### Security and lifecycle

- Default collector is unprivileged and per-user.
- Optional machine-wide privileged supervision is allowed only under ADR-012 and cannot inspect source content or merge users.
- No kernel anti-cheat or mandatory VibeMaxxing inference proxy.
- Deterministic accounting, canonicalization, signatures, sequences, replay, duplicates, continuity and eligibility are authoritative.
- Statistical/ML detectors are advisory and cannot alter totals or permanently ban.
- `vibemaxxing-daemon` is OS-supervised and always-on within the declared platform lifecycle context.
- Automatic updates are mandatory for competitive profiles under ADR-013.

### Automation

The Storybook workflow is prototype-only under ADR-014. It cannot satisfy product build, security, accessibility, platform or launch gates. Product CI remains disabled until P-1104 and P-1007.

## Component ownership

### Rust local/protocol

- `vibe-adapter-sdk`: manifests, probes and typed source observations; no network/device-key access.
- `vibe-collector-core`: normalization, accounting, deterministic rules, dedup, commitments, claims and privacy filtering.
- `vibe-device-identity`: keys, enrollment, rotation, revocation, recovery and platform assurance.
- `vibeproof-protocol`: deterministic CBOR, COSE, claims, appraisal/receipt verification and exact vectors.
- `vibemaxxing-daemon`: service lifecycle, supervision, local control and update coordination.
- `vibeproof-sync`: networked safe-claim sync with no source-content access.
- CLI and menu-bar/tray/local-dashboard integrations.
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
- operations/admin tooling;
- compatibility/update deadline enforcement.

### TypeScript web

- generated contract consumption;
- public/authenticated routes;
- evidence/privacy disclosure;
- social/board/moderation UX;
- device/update/platform status surfaces;
- no independent business-policy reimplementation;
- no fixture-only assumptions in production paths.

### PostgreSQL

Constraints and transactions own account/provider uniqueness, token families, device/key lineage, challenge use, idempotency/replay/forks, immutable facts/projections, ranking views/corrections, relationships/ownership, moderation/reversal, outbox/rebuild checkpoints and signed update-policy state.

## Repaired normative set required before coding

- product/scope and country removal;
- privacy and exact local/outbound stages;
- accounting profiles, canonical categories, time and pricing;
- VibeProof claim/appraisal/checkpoint/rotation/correction protocol;
- capability registry and digest/provenance certification;
- native process, always-on lifecycle, privilege, IPC, storage, recovery and update contracts;
- exact Mac/Windows/Linux/WSL/container/CI profile registry;
- OAuth/session/token-family/ranked-identity contracts;
- OpenAPI, PostgreSQL, atomic verifier, idempotency and ranking-view contracts;
- typed social, presence, notification, moderation and appeal state machines;
- TUF/release-set/provenance/transparency/compromise contracts;
- complete decision traceability and negative check for out-of-scope mobile/ChromeOS native work.

## Build sequence after approval

### Phase 1 — contract workspaces

Pin Rust, Go, Node, package manager, Buf/Protobuf, CDDL, OpenAPI, JSON Schema and migration tools. Create authoritative workspaces, generated bindings, drift checks, ordered migrations, reason/policy registries, platform-profile registry and privacy-canary fixtures.

Exit: clean generation is byte-identical; blocked schemas cannot enter builds; no parallel hand-maintained domain types.

### Phase 2 — synthetic secure spine

Implement:

`typed source observation -> normalized event -> accounting -> deterministic rules -> encrypted local state -> commitment -> signed claim -> isolated sync -> challenge -> atomic verifier -> appraisal -> checkpoint receipt -> immutable ledger/outbox -> aggregate -> ranking view -> accessible row`.

Prove privacy-canary blocking, canonical/signature/key/challenge rejection, exact replay idempotency, conflicting reuse/fork quarantine, deterministic delayed sync and rebuild equivalence.

### Phase 3 — always-on local runtime and device boundary

Implement:

- service registration before install success;
- always-on daemon desired state and two-level supervision;
- collector/sync separation and typed authenticated IPC;
- encrypted storage, migrations, crash consistency and bounded queues;
- protected keys, enrollment, rotation, revocation, recovery and requalification;
- local commitments and server checkpoints;
- shell-independent health/control and CLI parity;
- sleep/resume, logout/login, reboot, network loss, disk full, corruption, permission loss, update and rollback behavior;
- exact lifecycle/evidence status in diagnostics;
- optional privileged supervisor with separate identity and ACLs.

Platform implementation lanes:

1. macOS Apple silicon and Intel;
2. Windows native x64 and ARM64;
3. Linux distro/package/desktop/headless profiles;
4. WSL;
5. containers;
6. CI/ephemeral runners.

No Android, iOS, iPadOS or ChromeOS lane exists.

### Phase 4 — two-source vertical slice

Select one local runtime and one cloud structured-usage source. Each adapter ships manifest, digest/provenance, probes, accounting profile, duplicate contract, positive/adversarial/privacy/upgrade fixtures, support ceiling and emergency disable.

Exit: both sources work end-to-end without forbidden egress; imports cannot rank; appraisal, filters and privacy preview work.

### Phase 5 — authentication, sessions and ranked identity

Implement GitHub App web/device authorization, X Authorization Code plus PKCE, typed OAuth transactions, web/native token families, replay/revocation, linked identities, recovery, optional stronger factors, ranked eligibility, duplicate investigation, restriction, consolidation and appeal.

### Phase 6 — verifier, ranking and pricing

Implement atomic claim transaction, stored idempotent outcomes, appraisal policy, immutable receipts/corrections/moderation facts, outbox, canonical `ranking_view_id`, snapshots/cursors/current rank/rebuild, immutable alias resolution and line-item estimated pricing.

### Phase 7 — social state machines

Implement profiles/privacy/handles/blocks, friendships/rivals, boards/roles/invitations/ownership, organizations/communities/hacker houses, collector-derived presence, typed notifications, overtakes/movement, moderation/appeals/reversal and separate server/local export/deletion. Country remains absent.

### Phase 8 — complete UX

Implement onboarding/pairing, all launch leaderboards, profiles/activity/agent/model/estimated-cost views, social/boards/notifications, devices/adapters/privacy/audit/export/deletion, update/channel/deadline status, privileged-profile status, moderation/appeals and complete exceptional states. Meet WCAG 2.2 AA and declared performance/resource budgets on every advertised profile.

### Phase 9 — integration and adversarial beta

Execute protocol, replay, fork, clone, restore, accounting, identity, social, notification, moderation, privacy and release campaigns.

For every advertised profile execute install, registration, shell crash, daemon crash/hang, child crash loop, login/logout, reboot, sleep/hibernate where applicable, network loss, permission/key-store/storage failure, update/rollback, deadline expiry, background-service disable/repair and uninstall. Verify no queued-claim loss, duplicate score, continuity reset or privacy leakage.

Privileged profiles additionally require cross-user and substitution tests. WSL/container/CI profiles require clone/replica/retry/matrix dedup tests.

### Phase 10 — packaging, operations and launch

Produce signed/notarized native artifacts, Linux packages, container images, CI artifacts, TUF metadata, release-set graph, SBOM/provenance/transparency, consumer verification, environments/secrets/migrations, backups/restores, SLOs/alerts/incidents/DR, product CI/security/eval/release gates, legal/governance review, public docs and reproducible releases.

A platform enters public support only after every gate in `CROSS_PLATFORM_COMPLETENESS_AUDIT.md` passes for its exact tuple. Public release still requires explicit approval.

## Implementation evidence rules

Every PR identifies:

- work key and dependencies;
- every mapped decision ID;
- owning ADRs/contracts/schemas;
- exact platform profiles affected;
- privacy/security impact and threats;
- database/API/wire compatibility and migrations;
- rollback/disable path;
- tests, benchmarks, fixtures and generated artifacts;
- support/evidence ceilings;
- unresolved risk.

A PR cannot close an accepted decision unless its traceability row has implementation and executable evidence links. Placeholders, skipped tests, mocks, empty certifications and planning/prototype validators do not close implementation work.