# VibeMaxxing Documentation Map

This is the sole canonical map. Do not create competing indexes, start prompts, master-context files, duplicate roadmaps or numbered research waves.

## Initialization

1. `AGENTS.md`
2. `docs/project/PROJECT.md`
3. `docs/project/STATUS.md`
4. this file
5. `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
6. `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`
7. `docs/planning/decision-traceability/README.md`
8. `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`
9. `docs/planning/DECISION_REGISTER.md`
10. `docs/planning/TASK_CATALOG.md`
11. `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`
12. `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`
13. relevant ADRs, contracts, schemas and fixtures
14. implementation handoff only for implementation planning or after explicit approval

Run `python3 scripts/repository/doctor.py` before relying on repository state.

## Current authority note

P-1140A through P-1140E are complete within their stated planning scopes. P-1140E proves structural repository consistency only. The P-1140F repair head is pending independent semantic review and PostgreSQL-backed clean-checkout validation. P-1104 remains blocked and product implementation remains unauthorized.

Historical reports that declare planning complete, implementation-ready or launch-ready do not override current STATUS, TASK_CATALOG, P-1140F, accepted decisions, ADRs or repaired contracts.

## Normative owners

- Project authority and phase: `docs/project/PROJECT.md`, `docs/project/STATUS.md`
- Documentation hierarchy: this file
- Task and gate state: `docs/planning/TASK_CATALOG.md`
- Decision authority: `docs/planning/DECISION_REGISTER.md`, `docs/decisions/`
- Repository reconciliation: `docs/planning/REPOSITORY_ALIGNMENT_2026-07-23.md`
- Machine-contract repair target: `docs/planning/MACHINE_CONTRACT_REPAIR_SPEC.md`
- Decision-to-owner/platform/evidence mapping: `docs/planning/decision-traceability/`
- Frozen candidate platform baseline: `docs/planning/CROSS_PLATFORM_COMPLETENESS_AUDIT.md`
- Structural cross-contract result: `docs/planning/P1140E_FINAL_CONTRADICTION_AUDIT_2026-07-24.md`
- Semantic review and standards mapping: `docs/planning/P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md`
- Scope/product: `docs/planning/PRODUCT_SCOPE_FREEZE.md`, `docs/product/PRODUCT_SPEC.md`, subject to D-052 and D-066
- Accounting/time/pricing: `docs/product/ACCOUNTING_AND_TIME_CONTRACT.md`
- Adapter data stages and VibeProof authority: `docs/architecture/ADAPTER_AND_VIBEPROOF_CONTRACT.md`
- VibeProof wire/state protocol: `docs/architecture/VIBEPROOF_V1_PROTOCOL.md`, `packages/schemas/vibeproof-claim-v1.cddl`
- Authoritative server/native state and platform contract: `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`, subject to P-1140F repairs
- Universal compatibility: `docs/integrations/UNIVERSAL_AGENT_COMPATIBILITY.md`
- Privacy: `docs/privacy/PRIVACY_CONTRACT.md`, `docs/privacy/PRIVACY_PRESERVING_USAGE_EVIDENCE.md`
- Security: `docs/security/THREAT_MODEL.md`, `docs/security/INTEGRITY_MODEL.md`, `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`, `docs/security/AUTHENTICATION_AND_RECOVERY.md`, `docs/security/RANKED_IDENTITY_ELIGIBILITY.md`
- Native runtime: `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md`, `docs/architecture/NATIVE_CLIENT_AND_DAEMON.md`, ADR-010 through ADR-013
- Operations and launch: `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`, ADR-013
- Prototype visual validation: ADR-014 and `.github/workflows/storyboard-visuals.yml`
- Future implementation handoff: `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- Future review-sized work units: `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`

## Important ADRs

- ADR-007 remains provisional where superseded by P-1140C.
- ADR-008 and ADR-009 remain accepted.
- ADR-010 owns always-on daemon lifecycle.
- ADR-011 owns universal platform baseline.
- ADR-012 owns optional privileged supervision.
- ADR-013 owns mandatory automatic updates.
- ADR-014 owns bounded prototype visual validation.

## Authoritative planning-grade schemas

`packages/schemas/` owns planning contracts for:

- adapter manifests and typed source observations;
- normalized accounting and local detector results;
- accounting profiles, pricing interpretations and evidence policy;
- device lineage and egress allowlists;
- VibeProof CDDL;
- local-control and social/integrity Protobuf;
- OpenAPI;
- PostgreSQL planning schema;
- state-machine, platform-profile, release-set, ranking-view and export-manifest schemas/registries;
- reason codes, policy defaults and observability allowlist.

These are not production-proven artifacts. P-1140F currently blocks the state/API/platform set on SR-001 through SR-004.

No generated production type may be based on a contract that P-1140F marks unresolved.

## Machine registries and conformance planning

- Adapter compatibility: `conformance/adapters/agent-registry-v1.json`
- Adversarial cases: `conformance/adversarial/anti-cheat-registry-v1.json`
- Mutable state: `packages/schemas/state-machine-registry-v1.json`
- Candidate platform profiles: `packages/schemas/platform-profile-registry-v1.json`
- T20 planning: `conformance/models/`
- Structural cross-contract matrix and plans: `conformance/p1140e/`
- Structural validator: `scripts/repository/validate_p1140e_contracts.py`

P-1140E validation demonstrates structural closure only. It cannot close P-1140F.

An empty certification list means no support claim. Certification must bind artifact digest, provenance, source version, exact platform tuple, mode and immutable result bundle.

## Implementation planning

Only these files are canonical for future execution:

- `docs/implementation/IMPLEMENTATION_HANDOFF.md`
- `docs/implementation/PR_SIZED_WORK_BREAKDOWN.md`
- `docs/implementation/REPOSITORY_LAYOUT.md`
- `docs/implementation/ISSUE_GENERATION.md`

They are inactive until P-1140F closes and the user explicitly authorizes P-1104.

## Research

`docs/research/README.md` is the sole research entrypoint. Research informs decisions but never overrides accepted decisions or repaired contracts. Current primary standards cited by P-1140F include RFC 7636, RFC 8252, RFC 8414, RFC 8628, RFC 9207, RFC 9700, deterministic CBOR/COSE/Ed25519 RFCs, TUF and SLSA provenance.

## Generated and historical artifacts

Repository metadata under `artifacts/repository/`, story captures, old completion reports and stale branch documents are non-authoritative. Storybook captures are short-lived prototype evidence only.

## Duplication rule

A concept has one normative owner. Merge unique content into that owner, repair references, delete or clearly mark duplicates and record material changes through the decision register and an ADR when required.
