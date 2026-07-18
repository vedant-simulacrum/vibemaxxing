# VibeMaxxing Implementation Handoff

Status: normative planning handoff; implementation requires explicit user approval.
Version: 2

## Purpose

This is the single build-order contract for the implementation phase. Do not create another implementation roadmap or build plan. The detailed dependency-ordered units are in `PR_SIZED_WORK_BREAKDOWN.md`.

An implementation agent must not invent behavior that conflicts with the normative contracts. When a platform, provider, dependency, or external fact changes, update the relevant ADR or contract and conformance fixture before changing behavior.

## Initialization and authority

Start with:

1. `/AGENTS.md`
2. `docs/project/PROJECT.md`
3. `docs/project/STATUS.md`
4. `docs/project/DOCUMENTATION.md`
5. `docs/planning/DECISION_REGISTER.md`
6. the normative contracts below
7. accepted ADRs
8. historical research only when the provenance index identifies relevant evidence

## Normative contract set

- Product and launch: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`
- Accounting, time, and pricing: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- Universal compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, `conformance/adapters/agent-registry-v1.json`
- Adapter and VibeProof protocol: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- Native runtime, storage, and IPC: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`
- Native product topology: `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`
- Identity: `docs/decisions/ADR-006-IDENTITY_AND_NATIVE_AUTH.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
- Server, data, and ranking: `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`
- Social, integrity, and UX: `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
- Privacy and threats: `docs/privacy/PRIVACY_CONTRACT.md`, `docs/security/THREAT_MODEL.md`, `docs/security/INTEGRITY_MODEL.md`
- Anti-cheat and adversarial evidence: `docs/security/ANTI_CHEAT_RESEARCH_PROGRAM.md`, `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md`, `docs/security/ADVERSARIAL_TABLETOPS.md`, `conformance/adversarial/anti-cheat-registry-v1.json`
- Operations, open source, and launch: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`
- Evidence thresholds: `docs/evals/BENCHMARK_AND_EVIDENCE_PROTOCOLS.md`, `docs/qa/ACCEPTANCE_GATES.md`

## Intended implementation layout

```text
/apps/web                         Next.js web product
/apps/api                         Go APIs and workers
/apps/docs                        public protocol/product documentation
/apps/desktop                     native shell packaging and platform UI
/crates/vibeproof-core            canonical events, accounting, claims, crypto
/crates/vibeproof-adapters        adapter SDK and built-in adapters
/crates/vibeproof-collector       transcript-private capture process
/crates/vibeproof-sync            network-safe sync process
/crates/vibemaxxing-daemon        supervisor and local control API
/crates/vibemaxxing-cli           installer and control CLI
/packages/protocol                generated cross-language protocol bindings
/packages/schemas                 OpenAPI, JSON Schema, Protobuf, and CDDL sources
/packages/ui                      design tokens and accessible components
/migrations                       PostgreSQL migrations
/conformance                      accounting, protocol, adapter, privacy, and attack fixtures
/benchmarks                       native, server, database, and frontend benchmarks
/infrastructure                   cloud-portable reference deployment
```

Do not create a second product repository or split VibeProof into another repository without an accepted ADR.

## Build sequence

### 1. Contract workspaces

Create pinned Rust, Go, Node, Protobuf/Buf, CDDL, OpenAPI, JSON Schema, migration, and fixture workspaces. Generated output must be reproducible and drift-checked. Business logic begins only after accounting, event, claim, IPC, API, and database schema sources validate in their target toolchains.

### 2. Synthetic secure spine

Implement synthetic event → deterministic accounting → encrypted local storage → signed claim → isolated sync → challenge and ingestion → append-only ledger and outbox → deterministic aggregate → leaderboard API → accessible leaderboard row.

Prove forbidden-content canaries do not leave the device, invalid signatures fail, replay fails, duplicate submission is idempotent, and aggregate rebuild is equivalent.

### 3. Native process boundary

Implement collector, sync, daemon, CLI, local control API, peer authentication, encrypted state, crash consistency, offline queue, device enrollment, diagnostics, export/deletion, and update/rollback hooks. Add menu-bar and tray shells only after the daemon API stabilizes.

### 4. Identity and accounts

Implement GitHub App web/device authorization, X OAuth 2.0 PKCE, linked identities, sessions, optional stronger credentials, recovery, device binding, provider compromise handling, authorization, merge, export, and deletion.

### 5. Adapter platform

Implement manifest/event SDKs, capability probes, source reconciliation, deduplication domains, support lifecycle, emergency disable, and conformance runner. Add representative adapters across capture families, then expand using the machine registry. No support badge exists without exact version, mode, platform, and test evidence.

### 6. Ranking and social product

Implement periods, ties, late events, corrections, filters, profiles, friendships, blocks, rivals, overtakes, boards, organizations, communities, country policy, presence, notifications, moderation, appeals, retention, export, and deletion. Property-test state machines and authorization.

### 7. Full web and native UX

Implement the route map and all loading, empty, error, offline, private, restricted, quarantined, deleted, and unsupported states. Complete privacy inspection, adapter/device management, account/recovery, export/deletion, accessibility, browser, responsive, visual, and performance evidence.

### 8. Integrity hardening

Execute the attack catalog. Implement deterministic rules and transparent statistical baselines before experimental model work. Ship an SLM only if the measured bakeoff passes privacy, resource, calibration, and false-quarantine gates. Complete independent privacy and security review.

### 9. Packaging and operations

Implement platform signing and notarization, TUF updates, atomic rollback, SBOM and provenance, consumer verification, environments, secrets, backups and restores, SLOs, alerts, incident response, key rotation, and disaster-recovery drills. Restore tuned automated checks and branch protection.

### 10. Open-source release and launch

Complete dependency/license/trademark review, DCO, contributor and security governance, secret/history scan, protocol documentation, adapter SDK, reproducible releases, and the complete launch gate. The repository becomes public only after private-material review and before public launch.

## Ownership rules

- Rust is authoritative for normalized events, accounting, canonical claims, local sequence/chaining, and cryptographic reference fixtures.
- Go independently verifies claims and owns acceptance transactions, APIs, workers, and ranking.
- TypeScript consumes generated contracts and owns presentation and interaction, never claim semantics.
- PostgreSQL constraints and migrations are part of correctness.
- No server process can receive forbidden content; no transcript-capable process can network.
- Every externally visible behavior has stable errors or reason codes and a migration story.

## Pull request completion contract

Each PR identifies task and decision IDs, contract sections implemented, schemas and migrations changed, privacy/security impact, compatibility, rollback, tests, benchmark impact, generated files, and unresolved risks. A PR cannot claim completion using skipped tests, placeholders, mock-only behavior, undocumented feature flags, or unexecuted fixtures.

## Evidence boundary

The repository is implementation-ready at planning level. Executable correctness, security, privacy, performance, compatibility, packaging, operations, and launch readiness require real implementation evidence and cannot be declared by documentation.
