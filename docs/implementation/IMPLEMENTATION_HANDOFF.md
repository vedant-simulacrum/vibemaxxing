# VibeMaxxing Implementation Handoff

Status: consolidated but inactive; P-1140F semantic review is open and P-1104 is blocked
Version: 10
Updated: 2026-07-24

## Purpose

This is the single future build-order contract. It consolidates current product authority, privacy and integrity boundaries, accounting, VibeProof, identity, API, ranking, social, native-platform and release planning.

It does not authorize implementation. `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md` is subordinate to this file and must be reconciled again when P-1140F closes.

## Current handoff health

| Layer | Current state | Consequence |
|---|---|---|
| Product authority and launch scope | consolidated | preserve no-country launch scope and no native mobile/ChromeOS work |
| Privacy, accounting and appraisal | P-1140B complete-planning | planning input only; no runtime privacy or security proof |
| VibeProof | P-1140C complete-planning | planning input only; independent codecs and interoperability absent |
| State/API/platform/release contracts | P-1140D complete-planning with four semantic P1 repairs open | not implementation-ready |
| Structural validation | P-1140E complete-planning | proves internal reference and coverage consistency only |
| Semantic review | P-1140F in progress | blocks implementation authorization |
| Product code | prototype/seeds only | collector, services, database, packaging and operations are absent |

P-1104 is not ready for approval. The exact semantic findings and closure criteria are owned by `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`.

## Mandatory pre-read

1. `AGENTS.md`
2. `docs/project/PROJECT.md`
3. `docs/project/STATUS.md`
4. `docs/project/DOCUMENTATION.md`
5. `docs/planning/DECISION_REGISTER.md`
6. `docs/planning/TASK_CATALOG.md`
7. `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`
8. `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`
9. relevant ADRs, contracts, schemas and conformance fixtures
10. this file and the PR-sized work breakdown only after the gate is understood

## Entrance gate

Implementation may begin only when:

1. P-1140F is `complete-planning`;
2. SR-001 through SR-004 are repaired in normative prose, schemas, registries, fixtures and validators;
3. P-1140E structural validation passes on the repaired exact head without claiming semantic proof;
4. the manual semantic review records zero open P0/P1 findings;
5. every implementation-bearing decision still has an owner, work unit, schema/state owner, platform scope and evidence gate;
6. superseded decisions have no active implementation path;
7. repository doctor and all planning-only validators pass from a clean checkout;
8. the user explicitly opens P-1104.

No agent may infer authorization from a green planning workflow, a complete planning task, this handoff, a prototype or a merged PR.

## Binding product constraints

### Privacy

- Servers never receive prompts, outputs, transcripts, code, diffs, commands, tool contents, filenames, paths, project/repository names, credentials, embeddings, summaries, classifications, personal insights or content-derived hashes.
- Processes able to read raw source content have no network capability.
- Networked sync receives only fixed-schema aggregate claims and receipts.
- Review, moderation, observability, support and privileged-supervisor tooling never expose local raw records.

### Competition and accounting

- Token Burn is the default raw ranking metric.
- Estimated Cash Burn is server-derived, versioned and always labelled estimated.
- Imported history is private analytics only and never ranks.
- Accepted Standard and Hardened claims may contribute globally.
- Local-model and delayed offline usage count only when deterministically captured under a certified profile.
- Evidence state is assigned by the server verifier, never by the client.

### Identity

- OAuth proves provider-account control, not unique humanity.
- One active ranked identity per detected/resolved person is enforced through private account, device, recovery and enforcement lineage with review and appeal.
- Government ID and biometrics are not required by default.
- Provider-specific OAuth behavior must follow the capability-aware SR-001 repair.
- Ordinary desktop clients use external-browser Authorization Code + PKCE; device authorization is limited by SR-002.

### Platforms

- Candidate native scope: macOS arm64/x86_64, Windows x64/ARM64, maintained Linux desktop/headless/remote, WSL, containers and CI/ephemeral runners.
- Android, iOS, iPadOS and ChromeOS have no native implementation lane.
- Every public support claim requires exact, non-expired certification.
- Platform evidence must use immutable version/commit/digest-bound source records under SR-004.

### Local runtime and anti-cheat

- Default collector is unprivileged and per-user.
- Optional privileged supervision is separately consented and cannot inspect source content or merge users.
- No kernel anti-cheat and no mandatory inference proxy.
- Deterministic accounting, canonicalization, signatures, sequences, replay, duplicate, continuity and eligibility controls are authoritative.
- Statistical/ML detectors are local-only, advisory and cannot alter totals, raise evidence tiers or permanently ban.
- The OS-supervised daemon is independent of collector, sync, CLI and interactive shell.
- The menu-bar/tray shell requires its own state machine and authenticated IPC under SR-003.

### Automation

The Storybook workflow remains prototype-only under ADR-014. Product build, dependency, security, fuzz, evaluation, signing, release, deployment and operational automation remain disabled until P-1104 and their separate implementation gate.

## Planned component ownership

### Rust local/protocol

- adapter SDK and probes;
- collector/normalization/accounting/deterministic rules;
- device identity and key lifecycle;
- VibeProof codec/signing/verification;
- OS-supervised daemon and local control;
- isolated safe-claim sync;
- CLI and menu-bar/tray shell;
- optional post-launch local detector sandbox.

### Go server

- provider-capability-aware OAuth and sessions;
- linked/ranked identity and recovery;
- device enrollment and lineage;
- challenge, verifier appraisal and checkpoint receipts;
- immutable ledgers, outbox and rebuild;
- pricing, ranking, social, presence and notifications;
- moderation, appeals, export and deletion;
- compatibility/update enforcement and operations tooling.

### TypeScript web

- generated contract consumption;
- public/authenticated routes and disclosure UX;
- social, board, moderation, device/update/platform status surfaces;
- no independent business-policy reimplementation.

### PostgreSQL

Transactions and constraints own provider/account uniqueness, token families, device/key lineage, challenges, idempotency/replay/forks, immutable facts, projections, ranking views/corrections, social ownership, moderation/reversal, outbox/rebuild checkpoints and signed update-policy state.

## Build sequence after explicit approval

### Phase 1 — contract workspaces

Pin Rust, Go, Node, Buf/Protobuf, CDDL, OpenAPI, JSON Schema and migration tools. Generate bindings and enforce byte-identical regeneration. Implement privacy-canary and checked numeric/time primitives first.

### Phase 2 — synthetic secure spine

Implement a synthetic end-to-end path:

`typed observation -> accounting -> deterministic rules -> encrypted local state -> commitment -> signed claim -> isolated sync -> challenge -> atomic verifier -> appraisal -> checkpoint -> immutable ledger/outbox -> ranking view`.

Prove forbidden-egress blocking, exact replay, conflicting reuse/fork quarantine, deterministic delayed sync and rebuild equivalence.

### Phase 3 — local runtime and device boundary

Implement OS supervision, collector/sync separation, authenticated local IPC, encrypted storage, crash consistency, bounded queues, protected keys, rotation/recovery, interactive shell, CLI parity, sleep/reboot/login/logout/offline/disk/permission/update behavior and optional privileged supervision.

### Phase 4 — two-source vertical slice

Select one local runtime and one cloud structured-usage source. Each adapter requires immutable manifest/provenance, accounting profile, duplicate domain, privacy/adversarial/upgrade fixtures, support ceiling and emergency disable.

### Phase 5 — authentication and ranked identity

Implement provider-capability-aware browser OAuth, restricted headless device flow where explicitly allowed, token-family rotation/replay, linked identities, recovery, ranked eligibility, investigation, restriction, consolidation and appeal.

### Phase 6 — ranking, pricing and social

Implement atomic claim acceptance, immutable corrections/moderation facts, ranking-view generations, snapshots/cursors/rebuilds, estimated pricing, social state machines, privacy-aware presence and revalidated notifications.

### Phase 7 — packaging and release trust

Implement exact-platform installers, daemon/shell registration, signed TUF metadata and release sets, immutable artifacts/provenance, mandatory update deadlines, rollback, compromise recovery and certification evidence.

## Handoff completeness checklist

Before implementation authorization, confirm:

- P-1140F has zero open semantic P0/P1 findings;
- STATUS, TASK_CATALOG, DOCUMENTATION and this handoff agree;
- the work breakdown no longer contains ordinary-desktop device authorization as a default path;
- interactive shell work is explicit and separate from the daemon;
- source evidence is immutable and digest-bound;
- all planning checks pass on the exact head;
- no open PR or stale branch is treated as authority;
- no implementation, support, security or launch claim is inferred from planning artifacts.

## Current next task

Repair SR-001 through SR-004 under P-1140F. Do not begin product implementation.
