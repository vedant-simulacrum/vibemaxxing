# VibeMaxxing Documentation Map

This is the sole canonical documentation map. Do not create competing indexes, master-context files, duplicate roadmaps, parallel implementation plans, or numbered research waves.

## Initialization order

1. `AGENTS.md`
2. `docs/project/PROJECT.md`
3. `docs/project/STATUS.md`
4. this file
5. `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
6. `docs/planning/DECISION_REGISTER.md`
7. `docs/planning/TASK_CATALOG.md`
8. `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
9. `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`
10. `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`
11. relevant ADRs, normative contracts, schemas, registries and fixtures
12. `docs/implementation/IMPLEMENTATION_HANDOFF.md` and `PR_SIZED_WORK_BREAKDOWN.md` only for planning future work or after explicit P-1104 authorization

Run `python3 scripts/repository/doctor.py` from a clean checkout before relying on repository state.

## Current authority note

The repository is in planning contract repair. P-1140F owns all open semantic findings. Product implementation remains unauthorized and P-1104 remains blocked. The earlier SR-001 through SR-004-only review is superseded by the current consolidated semantic register.

The technical-specification completeness authority is `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`. A concept is not planning-complete merely because prose mentions it; the inventory must name its normative owner, machine owner or planned path, lifecycle/persistence owner, repair dependency, implementation dependency and evidence gate.

## Normative owners

- Project authority and phase: `docs/project/PROJECT.md`, `docs/project/STATUS.md`
- Documentation hierarchy: this file
- Decision authority: `docs/planning/DECISION_REGISTER.md`, `docs/decisions/`
- Task and gate state: `docs/planning/TASK_CATALOG.md`
- Technical-specification inventory: `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`
- Structural review: `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`
- Semantic review: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`
- Scope/product: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`
- Accounting/time/pricing: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- Adapter stages and VibeProof boundary: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- VibeProof wire/state protocol: `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `packages/schemas/vibeproof-claim-v1.cddl`
- Authoritative mutable state and platform behavior: `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
- Universal compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`
- Privacy: `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md`
- Security: `docs/security/THREAT_MODEL.md`, `docs/security/INTEGRITY_MODEL.md`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`
- Native runtime: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`, ADR-010 through ADR-013
- Operations/release/open source: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, ADR-013
- Future implementation order: `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- Future PR-sized units: `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`
- Future repository layout: `docs/implementation/REPOSITORY_LAYOUT.md`

## Machine-readable authorities

`packages/schemas/` and adjacent conformance registries own planning contracts for:

- VibeProof CDDL and exact vectors;
- adapter manifests, source observations and normalized accounting;
- accounting profiles, pricing interpretations and evidence policy;
- device lineage and privacy egress;
- local IPC and social/integrity events;
- OpenAPI and PostgreSQL planning schema;
- state machines, platform profiles, ranking views, release sets and export manifests;
- reason codes, policy defaults and observability allowlists.

Required but not-yet-present machine contracts are explicitly listed as `planned-missing` in `SCHEMA_AND_INTERFACE_INVENTORY.md`. These include source receipts, evidence bundles, verifier appraisal results, compatibility tuples, certification results/lifecycle, account consolidation, fork resolution, local persistence, ranking generations and contributions, notification delivery aggregates, deletion plans/tombstones, TUF client state, compatibility/migration graphs and other blocked owners.

No agent may invent those semantics directly in product code.

## Evidence classification

- **Specification** — intended behavior without runtime proof.
- **Mock** — static or illustrative artifact.
- **Runnable prototype** — executable exploratory work using fixtures or incomplete contracts.
- **Production implementation** — integrated code satisfying accepted contracts.
- **Executable evidence** — reproducible conformance, security, benchmark or operational evidence for a specific claim.

Structural validation is not semantic review. Semantic review is not runtime proof. A prototype is not product implementation. Empty or expired certification is not support evidence.

## Current important ADRs

- ADR-008 and ADR-009 remain accepted.
- ADR-010 owns always-on daemon lifecycle.
- ADR-011 owns candidate platform scope.
- ADR-012 owns optional privileged supervision.
- ADR-013 owns mandatory automatic updates.
- ADR-014 owns bounded prototype visual validation.

## Research

`docs/research/README.md` is the sole research entrypoint. Research may inform an open decision or repair but never overrides accepted decisions, normative contracts or the technical-specification inventory.

## Generated and historical artifacts

Repository metadata under `artifacts/repository/`, story captures, old completion reports, stale review packets and stale branches are non-authoritative. Storybook captures are prototype evidence only. Later executable Rust/Go protocol/accounting code remains prototype-only where it contradicts the normative VibeProof authority.

## Duplication and completeness rules

A concept has one normative owner. When duplicates exist, merge unique content into that owner, repair references, and mark or remove the duplicate.

Every technical specification must be represented in `SCHEMA_AND_INTERFACE_INVENTORY.md`. Every mutable concept must have one lifecycle and persistence owner. Every future implementation unit must trace back to an accepted decision and repaired specification. Every public support or launch claim must trace forward to executable evidence.