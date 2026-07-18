# VibeMaxxing Implementation Handoff

Status: normative planning handoff
Version: 1

## Purpose

This document is the build-order contract for the implementation phase. An implementation agent must not invent behavior that conflicts with the referenced normative contracts. Where a platform or provider changes, update the relevant ADR/contract and conformance fixture before implementation.

## Authority

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `docs/planning/DECISION_REGISTER.md`
4. normative contracts listed below
5. accepted ADRs
6. historical research

## Normative contract set

- Product and launch: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`
- Accounting/time/pricing: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- Universal compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, `conformance/adapters/agent-registry-v1.json`
- Adapter/protocol: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- Native runtime/storage/IPC: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`
- Native product topology: `docs/architecture/NATIVE_PRODUCT_ARCHITECTURE.md`
- Identity: `docs/decisions/ADR-006-IDENTITY_AND_NATIVE_AUTH.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`
- Server/data/ranking: `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md`
- Social/integrity/UX: `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md`
- Threats/anti-cheat: `docs/security/THREAT_MODEL.md`, `docs/security/ANTI_CHEAT_RESEARCH_PROGRAM.md`, `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md`, `conformance/adversarial/anti-cheat-cases.json`
- Operations/open-source/launch: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`

## Repository layout

```text
/apps/web                 Next.js web product
/apps/api                 Go API and workers
/apps/docs                public protocol/product docs
/crates/vibeproof-core    canonical events, accounting, claims, crypto
/crates/vibeproof-adapters adapter SDK and built-in adapters
/crates/vibeproof-collector transcript-private capture process
/crates/vibeproof-sync    network-safe sync process
/crates/vibemaxxing-daemon supervisor and control API
/crates/vibemaxxing-cli   installer/control CLI
/apps/desktop             native shell packaging and platform UI
/packages/protocol        generated cross-language protocol bindings
/packages/schemas         OpenAPI/JSON Schema/Protobuf/CDDL sources
/packages/ui              design tokens and reusable accessible components
/migrations               PostgreSQL migrations
/conformance              protocol, accounting, adapter, privacy, attack fixtures
/benchmarks               native/server/database/frontend benchmarks
/infrastructure           cloud-portable reference deployment
```

## Build sequence

### 1. Contract workspaces

Create pinned Rust, Go, Node, Protobuf/Buf, CDDL, OpenAPI, JSON Schema, migration, and fixture workspaces. Generated output is reproducible and drift-checked. No business logic begins before accounting/event/claim schemas compile in all target languages.

### 2. Synthetic vertical slice

Implement synthetic event -> deterministic accounting -> local storage -> signed claim -> challenge/ingestion -> append-only ledger/outbox -> aggregate -> leaderboard API -> accessible leaderboard row. Prove privacy boundary, signature failure, replay rejection, duplicate idempotency, rebuild equivalence, and packet-capture canaries.

### 3. Native process boundary

Implement collector, sync, daemon, CLI and local control API with OS peer identity, application challenge-response, encrypted state, crash consistency, offline queue, device enrollment, health/doctor, export/deletion, update/rollback hooks. Add menu-bar/tray shell only after daemon API is stable.

### 4. Identity and accounts

Implement GitHub App web/device authorization, X PKCE, linked identities, sessions, optional passkeys, recovery, device binding, provider compromise flows, authorization matrix and deletion lifecycle.

### 5. Adapter platform

Implement manifest/event SDK, capability probes, source reconciliation, dedup domains, support lifecycle, emergency disable and conformance runner. Add one real adapter per capture family, then broaden product coverage from the machine registry. No adapter receives a support badge without exact version/mode/platform evidence.

### 6. Ranking and social product

Implement periods, ties, late events, corrections, filters, profiles, friendships, blocks, rivals, overtakes, boards, organizations, communities, country policy, presence, notifications, moderation and appeals. All state machines are property-tested and authorization-tested.

### 7. Full web/native UX

Implement route map and all loading/empty/error/offline/private/quarantined/deleted/unsupported states. Build privacy inspection, adapter/device management, OAuth/recovery, export/deletion and local shell flows. Pass WCAG, browser, responsive, visual and performance gates.

### 8. Integrity hardening

Run the complete attack catalog. Implement transparent rules/statistics before experimental SLM work. Conduct detector bakeoff; ship an SLM only if it provides measured lift under privacy, resource and false-quarantine budgets. Run independent security/privacy review.

### 9. Packaging and operations

Implement platform signing/notarization, TUF updater, atomic rollback, SBOM/provenance, clean-consumer verification, environments, backups/restores, SLOs, alerts, incident response, key rotation and disaster-recovery drills. Restore tuned automated checks and branch protection.

### 10. Open-source release and launch

Complete license/dependency/trademark review, DCO, contributor/security governance, secret/history scan, public documentation, protocol spec and adapter SDK. Public launch occurs only after the complete launch gate passes.

## Coding ownership rules

- Rust is authoritative for normalized events, accounting, canonical claims, local chain/sequence and cryptographic verification fixtures.
- Go independently verifies claims and owns acceptance transactions, APIs, workers and ranking.
- TypeScript consumes generated contracts and owns presentation/business interaction, never claim semantics.
- PostgreSQL constraints are part of correctness, not optional validation.
- No server process can receive forbidden content; no transcript-capable process can network.
- Every externally visible behavior has a stable error/reason code and migration story.

## Pull request completion template

Each PR states task/decision IDs, contract sections implemented, schema/migration changes, privacy/security impact, compatibility, rollback, tests, benchmark impact, generated files, and unresolved risks. A PR cannot claim completion with skipped tests, placeholders, mock-only behavior or undocumented feature flags.

## Definition of implementation-ready

Planning is implementation-ready when the normative contract set is present, internally consistent, linked from the task catalog and specification index, and no P0/P1 contradiction remains. Executable correctness, security, privacy, performance and launch readiness still require implementation evidence and cannot be declared by planning documents alone.
