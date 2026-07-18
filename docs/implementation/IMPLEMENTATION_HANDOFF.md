# VibeMaxxing Implementation Handoff

Status: normative future implementation handoff; inactive until planning-hardening passes and the user explicitly authorizes implementation.
Version: 3

## Purpose

This is the single build-order contract. It does not authorize implementation. Detailed units are in `PR_SIZED_WORK_BREAKDOWN.md`; current and future paths are distinguished in `REPOSITORY_LAYOUT.md`; execution-thread generation is governed by `ISSUE_GENERATION.md`.

## Entrance gate

Implementation may begin only when:

1. P-1120 through P-1128 are complete and the repository doctor passes from a clean checkout;
2. draft schemas, registries, references, governance, and protocol edge semantics are internally consistent;
3. the user explicitly opens implementation under P-1104.

## Initialization

Read `AGENTS.md`, project authority/status/documentation map, decision register, task catalog, relevant ADRs and contracts, and authoritative schemas. Do not treat historical research, future paths, placeholders, or generated artifacts as implemented state.

## Normative set

- Scope/product: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`
- Accounting: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- Compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, adapter registry and schema
- VibeProof: adapter/VibeProof contract, ADR-007, claim CDDL and reason registry
- Native: native runtime/storage contract, native topology contract and local-control Protobuf
- Identity: ADR-006, ADR-008 and authentication/recovery contract
- Server: server API/data/ranking contract, OpenAPI and planning SQL
- Social/integrity: social/integrity/UX contract, ADR-008, policy registry and adversarial registry
- Privacy/threats: privacy, threat and integrity contracts plus observability allowlist
- Licensing/governance: ADR-009, `LICENSES.md`, `CONTRIBUTING.md`, `SECURITY.md`, CODEOWNERS
- Operations/launch: operations/open-source/launch contract and evidence thresholds

## Build sequence after approval

### 1. Validate contract workspaces

Pin Rust, Go, Node, package manager, Protobuf/Buf, CDDL, OpenAPI, JSON Schema and migration toolchains. Convert planning DDL into an ordered migration history. Validate all authoritative schemas and examples. Generated output must be reproducible and drift-checked.

### 2. Synthetic secure spine

Implement synthetic normalized event → deterministic accounting → encrypted local state → signed claim → isolated sync → atomic batch challenge/ingestion → append-only ledger/outbox → deterministic aggregate → leaderboard API → accessible row. Prove canary privacy, invalid signature rejection, atomic replay/idempotency, bounded sequence recovery and rebuild equivalence.

### 3. Native boundary

Implement collector, sync, daemon, CLI, authenticated bounded IPC, encrypted storage, crash/offline/disk-full recovery, enrollment, diagnostics, audit, export/deletion and update hooks. Shells follow stable daemon API.

### 4. Identity and accounts

Implement GitHub App web/device authorization, X PKCE, linked identities, sessions, optional stronger factors, recovery, provider compromise/loss, merge, authorization and lifecycle.

### 5. Adapter platform

Implement manifest/event SDK, probes, source precedence, duplicate domains, lifecycle, emergency disable and conformance runner. Product-level support requires populated exact certification records.

### 6. Ranking and social

Implement periods, ties, corrections, filters, profiles, deterministic handle rules, friends, blocks, rivals, overtakes, boards, country cohorts, presence, notifications, moderation, appeals, export and deletion using the policy registry.

### 7. Web and native UX

Implement complete routes and exceptional states, privacy inspection, adapter/device/account controls, accessibility, browser/responsive behavior and performance budgets.

### 8. Integrity hardening

Execute the adversarial registry. Deterministic controls and transparent baselines precede optional model work. Complete independent privacy/security review.

### 9. Packaging and operations

Implement signing/notarization, TUF, rollback, SBOM/provenance, consumer verification, environments, secrets, backups/restores, SLOs, alerts, incidents, key rotation and DR. Restore product CI/security/release automation and branch protection.

### 10. Open-source release and launch

Complete dependency/license/trademark review, DCO and contributor/security governance, history/secret scan, public documentation, reproducible releases and every launch gate. Public release still requires explicit approval.

## Ownership

Rust owns canonical events, accounting, claims and local chain semantics. Go independently verifies claims and owns transactions, APIs, workers and ranking. TypeScript consumes generated contracts and owns presentation. PostgreSQL constraints/migrations are correctness. Transcript-capable processes cannot network; server processes cannot receive forbidden content.

## PR completion

Each PR identifies work key, tasks/decisions, contracts/schemas, privacy/security impact, compatibility/migrations, rollback, tests/benchmarks, generated files and unresolved risk. Placeholders, skipped tests and mock-only behavior do not close work.
