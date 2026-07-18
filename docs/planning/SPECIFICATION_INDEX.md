# VibeMaxxing Technical Specification Index

Updated: 2026-07-19
Status: technical planning complete

| Component | Normative sources |
|---|---|
| Identity, thesis, privacy, stack | `PROJECT_CONTEXT.md`, `PROJECT_INSTRUCTIONS.md`, ADR-002, ADR-006 |
| Complete launch scope and stages | `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`, `IMPLEMENTATION_ROADMAP.md` |
| Decisions, dependencies and phase gates | `DECISION_REGISTER.md`, `DEPENDENCY_MAP.md`, `TASK_CATALOG.md`, `PLANNING_AUDIT.md` |
| Accounting, pricing and time | `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md` |
| Universal agent compatibility | `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`, `conformance/adapters/agent-registry-v1.json` |
| Adapter events and VibeProof | `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md` |
| Native product topology | `docs/architecture/NATIVE_PRODUCT_ARCHITECTURE.md` |
| Runtime, storage, IPC and devices | `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md` |
| Authentication and recovery | `docs/decisions/ADR-006-IDENTITY_AND_NATIVE_AUTH.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md` |
| Server API, data and ranking | `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` |
| Social, boards, integrity and UX | `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md` |
| Threats and anti-cheat | `docs/security/THREAT_MODEL.md`, `ANTI_CHEAT_RESEARCH_PROGRAM.md`, `ANTI_CHEAT_ATTACK_CATALOG.md`, `conformance/adversarial/anti-cheat-cases.json` |
| Privacy | `docs/privacy/PRIVACY_CONTRACT.md`, native/runtime and UX contracts |
| Packaging, operations and open source | `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md` |
| Implementation build order | `docs/implementation/IMPLEMENTATION_HANDOFF.md` |
| Historical research provenance | `docs/research/RESEARCH_PROVENANCE_INDEX.md` |
| Repository metadata | `scripts/repository/generate_repository_metadata.py` |

## Cross-cutting contract requirements

Every implementation must preserve owner/authority, interfaces and generated schemas, invariants and ordering, limits and idempotency, privacy/security classification, authorization/abuse behavior, failures/timeouts/retries, crash recovery and rollback, compatibility/versioning/migration/deprecation, observability allowlists, deletion/export, and positive/negative/adversarial/performance/accessibility evidence.

## No-invention rule

A future implementation model starts with `docs/implementation/IMPLEMENTATION_HANDOFF.md`. It may select libraries and write code within the frozen behavior, but it may not silently change metric semantics, privacy boundaries, evidence policy, identity model, compatibility tiers, state machines, authorization, ranking, data lifecycle, or launch gates. Material changes require the decision register and an ADR.

## Evidence rule

The contract set completes planning. It does not prove executable correctness. CI, conformance, attacks, benchmarks, accessibility, platform packaging, security review, recovery drills and launch acceptance must be produced during implementation.
